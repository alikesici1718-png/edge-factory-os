#!/usr/bin/env python
"""Capacity-aware refinement for locked SELL_PRESSURE_ABSORBED@300s."""

from __future__ import annotations

import csv
import json
import math
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import edge_factory_orderbook_um_81_sell_pressure_absorbed_execution_delay_capacity_diagnostic_v1 as prior


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"
PREFIX = "orderbook_um_81_sell_pressure_absorbed_capacity_aware_refinement"

SUMMARY_JSON = OUTPUTS_DIR / f"{PREFIX}_summary.json"
SUMMARY_MD = OUTPUTS_DIR / f"{PREFIX}_summary.md"
SUBSET_SUMMARY_CSV = OUTPUTS_DIR / f"{PREFIX}_subset_summary.csv"
DELAY_COST_GRID_CSV = OUTPUTS_DIR / f"{PREFIX}_delay_cost_grid.csv"
SYMBOL_SELECTION_CSV = OUTPUTS_DIR / f"{PREFIX}_symbol_selection.csv"
CAPACITY_BY_SYMBOL_CSV = OUTPUTS_DIR / f"{PREFIX}_capacity_by_symbol_window.csv"

LOCKED_CATEGORY = prior.LOCKED_CATEGORY
LOCKED_HORIZON_SECONDS = prior.LOCKED_HORIZON_SECONDS
LOCKED_COOLDOWN_SECONDS = prior.LOCKED_COOLDOWN_SECONDS
OBSERVED_PRICE_DIRECTION = prior.OBSERVED_PRICE_DIRECTION
EXPECTED_SYMBOL_COUNT = prior.EXPECTED_SYMBOL_COUNT
EXPECTED_SYMBOL_DAYS_TOTAL = prior.EXPECTED_SYMBOL_DAYS_TOTAL
DELAY_SECONDS = [0, 1, 3, 5, 10]
COST_GRID_BPS = [0.0, 1.0, 2.0, 3.0, 5.0]
WINDOWS = prior.WINDOWS
NOTIONAL_THRESHOLDS = [5_000.0, 10_000.0, 25_000.0, 50_000.0, 100_000.0]
TOP_SYMBOL_COUNTS = [10, 20, 40]
PROGRESS_INTERVAL_SECONDS = 30
MIN_EVENT_COUNT = 100
MIN_STABILITY_RATE = 0.5
MIN_SYMBOL_STABILITY_COUNT = 50
MIN_TIME_STABILITY_COUNT = 50


@dataclass
class RunningStats:
    count: int = 0
    sum_value: float = 0.0
    sum_square: float = 0.0
    directional_total: int = 0
    directional_match: int = 0

    def add(self, value: float | None, expected_direction: int) -> None:
        if value is None:
            return
        self.count += 1
        self.sum_value += value
        self.sum_square += value * value
        observed_direction = prior.sign_of(value)
        if expected_direction and observed_direction:
            self.directional_total += 1
            if observed_direction == expected_direction:
                self.directional_match += 1

    def merge(self, other: "RunningStats") -> None:
        self.count += other.count
        self.sum_value += other.sum_value
        self.sum_square += other.sum_square
        self.directional_total += other.directional_total
        self.directional_match += other.directional_match

    def mean(self) -> float | None:
        if not self.count:
            return None
        return self.sum_value / self.count

    def std(self) -> float | None:
        if self.count <= 1:
            return None
        mean_value = self.sum_value / self.count
        variance = max(0.0, (self.sum_square / self.count) - (mean_value * mean_value))
        return math.sqrt(variance)

    def directional_rate(self) -> float | None:
        if not self.directional_total:
            return None
        return self.directional_match / self.directional_total


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def candidate_label() -> str:
    return prior.candidate_label()


def rounded(value: float | None, places: int = 12) -> float | str:
    if value is None or math.isnan(value):
        return ""
    return round(value, places)


def rounded_bps(value: float | None) -> float | str:
    return rounded(value, 6)


def safe_div(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def split_threshold_name(threshold: float) -> str:
    return f"MIN_AROUND_EVENT_NOTIONAL_{int(threshold)}"


def add_stats(
    stats: dict[tuple[Any, ...], RunningStats],
    key: tuple[Any, ...],
    value: float | None,
) -> None:
    stats[key].add(value, OBSERVED_PRICE_DIRECTION)


def add_threshold_stats(
    split_name: str,
    window: str,
    delay: int,
    symbol: str,
    week: str,
    month: str,
    price_return: float,
    threshold_candidate_stats: dict[tuple[str, str, int], RunningStats],
    threshold_stability_stats: dict[tuple[str, str, int, str, str], RunningStats],
) -> None:
    add_stats(threshold_candidate_stats, (split_name, window, delay), price_return)
    add_stats(threshold_stability_stats, (split_name, window, delay, "SYMBOL", symbol), price_return)
    add_stats(threshold_stability_stats, (split_name, window, delay, "WEEK", week), price_return)
    add_stats(threshold_stability_stats, (split_name, window, delay, "MONTH", month), price_return)


def process_window(
    window: str,
    pairs: list[dict[str, Any]],
    candidate_symbol_stats: dict[tuple[str, int, str], RunningStats],
    candidate_symbol_week_stats: dict[tuple[str, int, str, str], RunningStats],
    candidate_symbol_month_stats: dict[tuple[str, int, str, str], RunningStats],
    null_symbol_stats: dict[tuple[str, int, str], RunningStats],
    threshold_candidate_stats: dict[tuple[str, str, int], RunningStats],
    threshold_null_stats: dict[tuple[str, str, int], RunningStats],
    threshold_stability_stats: dict[tuple[str, str, int, str, str], RunningStats],
    capacity_stats: dict[tuple[str, str], prior.base.DistributionStats],
    capacity_daily_counts: Counter[tuple[str, str, str]],
) -> dict[str, Any]:
    started = time.monotonic()
    processed_symbol_days = 0
    failed_symbol_days = 0
    total_feature_rows = 0
    original_candidate_row_count = 0
    original_event_count = 0
    kept_event_count = 0
    category_counts: Counter[str] = Counter()
    failure_examples: list[dict[str, str]] = []
    last_candidate_kept_ms: dict[str, int] = {}
    last_null_kept_ms: dict[tuple[str, int], int] = {}
    next_progress = time.monotonic() + PROGRESS_INTERVAL_SECONDS

    for pair in pairs:
        try:
            timestamps, rows, trade_times, trade_prices, _trade_notionals, prefix_notionals = prior.read_features_trade_details(pair)
            processed_symbol_days += 1
            total_feature_rows += len(rows)
            symbol = str(pair["symbol"])
            month = str(pair["year_month"])
            week = str(pair["week"])
            file_date = str(pair["file_date"])

            for index, row in enumerate(rows):
                event_ms = timestamps[index]
                category = str(row.get("absorption_category") or "INSUFFICIENT_DATA")
                if category not in prior.base.CATEGORIES:
                    category = "INSUFFICIENT_DATA"
                category_counts[category] += 1

                null_around_notional: float | None = None
                for delay in DELAY_SECONDS:
                    null_key = (symbol, delay)
                    if not prior.may_keep_event(last_null_kept_ms.get(null_key), event_ms):
                        continue
                    price_return = prior.delayed_forward_price_return(event_ms, delay, trade_times, trade_prices)
                    if price_return is None:
                        continue
                    last_null_kept_ms[null_key] = event_ms
                    add_stats(null_symbol_stats, (window, delay, symbol), price_return)
                    if null_around_notional is None:
                        null_around_notional = prior.notional_around_event(event_ms, trade_times, prefix_notionals)
                    if null_around_notional is None:
                        continue
                    for threshold in NOTIONAL_THRESHOLDS:
                        if null_around_notional >= threshold:
                            add_stats(
                                threshold_null_stats,
                                (split_threshold_name(threshold), window, delay),
                                price_return,
                            )

                if category != LOCKED_CATEGORY:
                    continue
                original_candidate_row_count += 1
                base_return = prior.delayed_forward_price_return(event_ms, 0, trade_times, trade_prices)
                if base_return is None:
                    continue
                original_event_count += 1
                if not prior.may_keep_event(last_candidate_kept_ms.get(symbol), event_ms):
                    continue
                last_candidate_kept_ms[symbol] = event_ms
                kept_event_count += 1

                around_notional = prior.notional_around_event(event_ms, trade_times, prefix_notionals)
                if around_notional is not None:
                    capacity_key = (window, symbol)
                    if capacity_key not in capacity_stats:
                        capacity_stats[capacity_key] = prior.capacity_distribution(f"capacity_refinement:{window}:{symbol}")
                    capacity_stats[capacity_key].add_diagnostic(around_notional, 0, "UNUSED", None, None, None)
                    capacity_daily_counts[(window, symbol, file_date)] += 1

                for delay in DELAY_SECONDS:
                    price_return = prior.delayed_forward_price_return(event_ms, delay, trade_times, trade_prices)
                    if price_return is None:
                        continue
                    add_stats(candidate_symbol_stats, (window, delay, symbol), price_return)
                    add_stats(candidate_symbol_week_stats, (window, delay, symbol, week), price_return)
                    add_stats(candidate_symbol_month_stats, (window, delay, symbol, month), price_return)
                    if around_notional is None:
                        continue
                    for threshold in NOTIONAL_THRESHOLDS:
                        if around_notional >= threshold:
                            add_threshold_stats(
                                split_threshold_name(threshold),
                                window,
                                delay,
                                symbol,
                                week,
                                month,
                                price_return,
                                threshold_candidate_stats,
                                threshold_stability_stats,
                            )
        except Exception as exc:  # noqa: BLE001
            failed_symbol_days += 1
            if len(failure_examples) < 20:
                failure_examples.append(
                    {
                        "symbol": str(pair.get("symbol", "")),
                        "file_date": str(pair.get("file_date", "")),
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
        if time.monotonic() >= next_progress:
            print(
                "progress phase=sell_pressure_capacity_refinement "
                f"window={window} processed_symbol_days={processed_symbol_days}/{len(pairs)} "
                f"failed_symbol_days={failed_symbol_days} feature_rows={total_feature_rows} "
                f"kept_events={kept_event_count} elapsed_seconds={round(time.monotonic() - started, 1)}",
                flush=True,
            )
            next_progress = time.monotonic() + PROGRESS_INTERVAL_SECONDS

    return {
        "window": window,
        "processed_symbol_days": processed_symbol_days,
        "failed_symbol_days": failed_symbol_days,
        "total_feature_rows": total_feature_rows,
        "original_candidate_row_count": original_candidate_row_count,
        "original_event_count": original_event_count,
        "kept_event_count": kept_event_count,
        "category_counts": dict(category_counts),
        "failure_examples": failure_examples,
    }


def capacity_row(
    window: str,
    symbol: str,
    stats: prior.base.DistributionStats,
    capacity_daily_counts: Counter[tuple[str, str, str]],
) -> dict[str, Any]:
    p25 = stats.quantile(0.25)
    p50 = stats.quantile(0.50)
    p75 = stats.quantile(0.75)
    p90 = stats.quantile(0.90)
    daily_counts = [
        count
        for (count_window, count_symbol, _date), count in capacity_daily_counts.items()
        if count_window == window and count_symbol == symbol
    ]
    return {
        "window": window,
        "symbol": symbol,
        "kept_event_count": stats.valid_forward_count,
        "p25_aggtrades_notional_around_event": rounded(p25, 4),
        "p50_aggtrades_notional_around_event": rounded(p50, 4),
        "p75_aggtrades_notional_around_event": rounded(p75, 4),
        "p90_aggtrades_notional_around_event": rounded(p90, 4),
        "symbol_liquidity_tier": prior.liquidity_tier(p50),
        "max_events_per_day": max(daily_counts) if daily_counts else 0,
    }


def build_capacity_rows(
    capacity_stats: dict[tuple[str, str], prior.base.DistributionStats],
    capacity_daily_counts: Counter[tuple[str, str, str]],
) -> list[dict[str, Any]]:
    return [
        capacity_row(window, symbol, stats, capacity_daily_counts)
        for (window, symbol), stats in sorted(capacity_stats.items())
    ]


def merge_symbol_stats(
    source: dict[tuple[str, int, str], RunningStats],
    window: str,
    delay: int,
    symbols: set[str],
) -> RunningStats:
    merged = RunningStats()
    for symbol in symbols:
        merged.merge(source.get((window, delay, symbol), RunningStats()))
    return merged


def stability_for_symbols(
    window: str,
    delay: int,
    symbols: set[str],
    effect_sign: int,
    candidate_symbol_stats: dict[tuple[str, int, str], RunningStats],
    candidate_symbol_week_stats: dict[tuple[str, int, str, str], RunningStats],
    candidate_symbol_month_stats: dict[tuple[str, int, str, str], RunningStats],
) -> dict[str, Any]:
    symbol_support = 0
    symbol_consistent = 0
    for symbol in symbols:
        stats = candidate_symbol_stats.get((window, delay, symbol), RunningStats())
        mean_value = stats.mean()
        if mean_value is None or stats.count < MIN_SYMBOL_STABILITY_COUNT:
            continue
        symbol_support += 1
        if effect_sign and prior.sign_of(mean_value) == effect_sign:
            symbol_consistent += 1

    week_stats: dict[str, RunningStats] = defaultdict(RunningStats)
    for (stat_window, stat_delay, symbol, week), stats in candidate_symbol_week_stats.items():
        if stat_window == window and stat_delay == delay and symbol in symbols:
            week_stats[week].merge(stats)
    month_stats: dict[str, RunningStats] = defaultdict(RunningStats)
    for (stat_window, stat_delay, symbol, month), stats in candidate_symbol_month_stats.items():
        if stat_window == window and stat_delay == delay and symbol in symbols:
            month_stats[month].merge(stats)

    def period_rate(period_stats: dict[str, RunningStats]) -> tuple[int, int, float | None]:
        support = 0
        consistent = 0
        for stats in period_stats.values():
            mean_value = stats.mean()
            if mean_value is None or stats.count < MIN_TIME_STABILITY_COUNT:
                continue
            support += 1
            if effect_sign and prior.sign_of(mean_value) == effect_sign:
                consistent += 1
        return support, consistent, safe_div(consistent, support)

    week_support, week_consistent, week_rate = period_rate(week_stats)
    month_support, month_consistent, month_rate = period_rate(month_stats)
    return {
        "symbol_support_count": symbol_support,
        "symbol_consistent_count": symbol_consistent,
        "symbol_stability_rate": safe_div(symbol_consistent, symbol_support),
        "week_support_count": week_support,
        "week_consistent_count": week_consistent,
        "week_stability_rate": week_rate,
        "month_support_count": month_support,
        "month_consistent_count": month_consistent,
        "month_stability_rate": month_rate,
    }


def stability_for_threshold(
    split_name: str,
    window: str,
    delay: int,
    effect_sign: int,
    threshold_stability_stats: dict[tuple[str, str, int, str, str], RunningStats],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for period_type, min_count in [
        ("SYMBOL", MIN_SYMBOL_STABILITY_COUNT),
        ("WEEK", MIN_TIME_STABILITY_COUNT),
        ("MONTH", MIN_TIME_STABILITY_COUNT),
    ]:
        support = 0
        consistent = 0
        for (stat_split, stat_window, stat_delay, stat_period_type, _value), stats in threshold_stability_stats.items():
            if (
                stat_split != split_name
                or stat_window != window
                or stat_delay != delay
                or stat_period_type != period_type
            ):
                continue
            mean_value = stats.mean()
            if mean_value is None or stats.count < min_count:
                continue
            support += 1
            if effect_sign and prior.sign_of(mean_value) == effect_sign:
                consistent += 1
        prefix = period_type.lower()
        result[f"{prefix}_support_count"] = support
        result[f"{prefix}_consistent_count"] = consistent
        result[f"{prefix}_stability_rate"] = safe_div(consistent, support)
    return result


def metric_bundle(candidate: RunningStats, null: RunningStats) -> dict[str, Any]:
    candidate_mean = candidate.mean()
    null_mean = null.mean()
    effect = candidate_mean - null_mean if candidate_mean is not None and null_mean is not None else None
    edge = effect * OBSERVED_PRICE_DIRECTION if effect is not None else None
    break_even = max(0.0, edge * 10_000) if edge is not None else None
    return {
        "event_count": candidate.count,
        "candidate_mean_forward_price_return": candidate_mean,
        "null_event_count": null.count,
        "null_mean_forward_price_return": null_mean,
        "gross_effect_vs_null_signed": effect,
        "gross_edge_observed_direction": edge,
        "break_even_cost_bps": break_even,
        "effect_sign": prior.sign_of(effect),
        "directional_diagnostic_rate": candidate.directional_rate(),
    }


def stability_passes(stability: dict[str, Any]) -> bool:
    rates = [
        stability.get("symbol_stability_rate"),
        stability.get("week_stability_rate"),
        stability.get("month_stability_rate"),
    ]
    present = [value for value in rates if value is not None]
    return bool(present) and all(float(value) >= MIN_STABILITY_RATE for value in present)


def max_cost_survived(latest: dict[str, Any], holdout: dict[str, Any], latest_stability: dict[str, Any], holdout_stability: dict[str, Any]) -> float | None:
    latest_edge = latest.get("gross_edge_observed_direction")
    holdout_edge = holdout.get("gross_edge_observed_direction")
    if latest_edge is None or holdout_edge is None:
        return None
    if latest.get("event_count", 0) < MIN_EVENT_COUNT or holdout.get("event_count", 0) < MIN_EVENT_COUNT:
        return None
    if not stability_passes(latest_stability) or not stability_passes(holdout_stability):
        return None
    survived = [
        cost
        for cost in COST_GRID_BPS
        if latest_edge - (cost / 10_000) > 0 and holdout_edge - (cost / 10_000) > 0
    ]
    return max(survived) if survived else None


def capacity_classification(split_name: str, capacity_profile: dict[str, Any]) -> str:
    if split_name.startswith("MIN_AROUND_EVENT_NOTIONAL_"):
        threshold = float(split_name.rsplit("_", 1)[-1])
        if threshold >= 100_000:
            return "FUND_CAPABLE_CAPACITY"
        if threshold >= 50_000:
            return "CAPACITY_SAFE"
        if threshold >= 25_000:
            return "CAPACITY_MODERATE"
        return "SMALL_CAP_OR_MIXED"
    tiers = Counter()
    for window_profile in capacity_profile.get("by_window", {}).values():
        tiers.update(window_profile.get("tier_counts", {}))
    if tiers.get("THIN", 0):
        return "THIN_INCLUDED"
    if tiers.get("HIGH", 0) + tiers.get("MEDIUM", 0) == sum(tiers.values()) and sum(tiers.values()) > 0:
        return "FUND_CAPABLE_CAPACITY"
    return "CAPACITY_SAFE"


def diagnostic_classification(max_cost: float | None, delay: int, capacity_class: str, latest: dict[str, Any], holdout: dict[str, Any]) -> str:
    latest_edge = latest.get("gross_edge_observed_direction")
    holdout_edge = holdout.get("gross_edge_observed_direction")
    if latest_edge is None or holdout_edge is None or latest_edge <= 0 or holdout_edge <= 0:
        return "REJECTED"
    if max_cost is None:
        return "FILTER_ONLY"
    if capacity_class == "FUND_CAPABLE_CAPACITY" and max_cost >= 2.0 and delay <= 5:
        return "FUND_CAPABLE"
    if capacity_class in {"CAPACITY_SAFE", "CAPACITY_MODERATE"} and max_cost >= 1.0:
        return "FUND_CAPABLE" if max_cost >= 3.0 and delay <= 3 else "FILTER_ONLY"
    if capacity_class in {"THIN_INCLUDED", "SMALL_CAP_OR_MIXED"}:
        return "SMALL_CAP_ONLY"
    return "FILTER_ONLY"


def build_capacity_profile(split_name: str, selected_by_window: dict[str, set[str]], capacity_rows: list[dict[str, Any]]) -> dict[str, Any]:
    rows_by_window = {
        window: [row for row in capacity_rows if row["window"] == window and row["symbol"] in selected_by_window.get(window, set())]
        for window in ["LATEST_90D", "HOLDOUT_90D"]
    }
    profile: dict[str, Any] = {"by_window": {}}
    for window, rows in rows_by_window.items():
        p50_values = [
            float(row["p50_aggtrades_notional_around_event"])
            for row in rows
            if str(row.get("p50_aggtrades_notional_around_event", "")) != ""
        ]
        tier_counts = Counter(str(row.get("symbol_liquidity_tier", "")) for row in rows)
        profile["by_window"][window] = {
            "selected_symbol_count": len(rows),
            "tier_counts": dict(tier_counts),
            "median_selected_symbol_p50_notional": rounded(sorted(p50_values)[len(p50_values) // 2] if p50_values else None, 4),
            "min_selected_symbol_p50_notional": rounded(min(p50_values) if p50_values else None, 4),
        }
    return profile


def build_symbol_selection_rows(
    split_symbols: dict[str, dict[str, set[str]]],
    capacity_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    capacity_lookup = {(str(row["window"]), str(row["symbol"])): row for row in capacity_rows}
    rows: list[dict[str, Any]] = []
    for split_name, by_window in sorted(split_symbols.items()):
        for window, symbols in sorted(by_window.items()):
            for symbol in sorted(symbols):
                capacity = capacity_lookup.get((window, symbol), {})
                rows.append(
                    {
                        "subset": split_name,
                        "window": window,
                        "symbol": symbol,
                        "p50_aggtrades_notional_around_event": capacity.get("p50_aggtrades_notional_around_event", ""),
                        "symbol_liquidity_tier": capacity.get("symbol_liquidity_tier", ""),
                        "kept_event_count": capacity.get("kept_event_count", ""),
                    }
                )
    return rows


def build_symbol_subsets(capacity_rows: list[dict[str, Any]]) -> dict[str, dict[str, set[str]]]:
    tiers = {(str(row["window"]), str(row["symbol"])): str(row["symbol_liquidity_tier"]) for row in capacity_rows}
    p50 = {
        (str(row["window"]), str(row["symbol"])): float(row["p50_aggtrades_notional_around_event"] or 0.0)
        for row in capacity_rows
    }
    all_symbols = sorted({str(row["symbol"]) for row in capacity_rows})
    combined_scores = {
        symbol: min(p50.get(("LATEST_90D", symbol), 0.0), p50.get(("HOLDOUT_90D", symbol), 0.0))
        for symbol in all_symbols
    }
    ranked_symbols = [
        symbol
        for symbol, _score in sorted(combined_scores.items(), key=lambda item: (item[1], item[0]), reverse=True)
    ]
    subsets: dict[str, dict[str, set[str]]] = {
        "HIGH_ONLY": {
            window: {symbol for symbol in all_symbols if tiers.get((window, symbol)) == "HIGH"}
            for window in ["LATEST_90D", "HOLDOUT_90D"]
        },
        "HIGH_MEDIUM": {
            window: {symbol for symbol in all_symbols if tiers.get((window, symbol)) in {"HIGH", "MEDIUM"}}
            for window in ["LATEST_90D", "HOLDOUT_90D"]
        },
        "EXCLUDE_THIN": {
            window: {symbol for symbol in all_symbols if tiers.get((window, symbol)) in {"HIGH", "MEDIUM", "LOW"}}
            for window in ["LATEST_90D", "HOLDOUT_90D"]
        },
    }
    for count in TOP_SYMBOL_COUNTS:
        selected = set(ranked_symbols[:count])
        subsets[f"TOP_{count}_BY_AROUND_EVENT_NOTIONAL"] = {
            "LATEST_90D": selected,
            "HOLDOUT_90D": selected,
        }
    return subsets


def build_subset_rows(
    capacity_rows: list[dict[str, Any]],
    candidate_symbol_stats: dict[tuple[str, int, str], RunningStats],
    candidate_symbol_week_stats: dict[tuple[str, int, str, str], RunningStats],
    candidate_symbol_month_stats: dict[tuple[str, int, str, str], RunningStats],
    null_symbol_stats: dict[tuple[str, int, str], RunningStats],
    threshold_candidate_stats: dict[tuple[str, str, int], RunningStats],
    threshold_null_stats: dict[tuple[str, str, int], RunningStats],
    threshold_stability_stats: dict[tuple[str, str, int, str, str], RunningStats],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, set[str]]]]:
    subset_rows: list[dict[str, Any]] = []
    cost_rows: list[dict[str, Any]] = []
    split_symbols = build_symbol_subsets(capacity_rows)
    split_profiles = {
        split_name: build_capacity_profile(split_name, selected_by_window, capacity_rows)
        for split_name, selected_by_window in split_symbols.items()
    }
    for split_name, selected_by_window in split_symbols.items():
        cap_class = capacity_classification(split_name, split_profiles[split_name])
        for delay in DELAY_SECONDS:
            latest_symbols = selected_by_window["LATEST_90D"]
            holdout_symbols = selected_by_window["HOLDOUT_90D"]
            latest = metric_bundle(
                merge_symbol_stats(candidate_symbol_stats, "LATEST_90D", delay, latest_symbols),
                merge_symbol_stats(null_symbol_stats, "LATEST_90D", delay, latest_symbols),
            )
            holdout = metric_bundle(
                merge_symbol_stats(candidate_symbol_stats, "HOLDOUT_90D", delay, holdout_symbols),
                merge_symbol_stats(null_symbol_stats, "HOLDOUT_90D", delay, holdout_symbols),
            )
            latest_stability = stability_for_symbols(
                "LATEST_90D",
                delay,
                latest_symbols,
                latest["effect_sign"],
                candidate_symbol_stats,
                candidate_symbol_week_stats,
                candidate_symbol_month_stats,
            )
            holdout_stability = stability_for_symbols(
                "HOLDOUT_90D",
                delay,
                holdout_symbols,
                holdout["effect_sign"],
                candidate_symbol_stats,
                candidate_symbol_week_stats,
                candidate_symbol_month_stats,
            )
            max_cost = max_cost_survived(latest, holdout, latest_stability, holdout_stability)
            classification = diagnostic_classification(max_cost, delay, cap_class, latest, holdout)
            subset_rows.append(
                subset_row(split_name, delay, cap_class, split_profiles[split_name], latest, holdout, latest_stability, holdout_stability, max_cost, classification)
            )
            cost_rows.extend(cost_grid_rows(split_name, delay, latest, holdout, latest_stability, holdout_stability, cap_class, classification))

    for threshold in NOTIONAL_THRESHOLDS:
        split_name = split_threshold_name(threshold)
        profile = {
            "by_window": {
                "LATEST_90D": {"selected_symbol_count": "", "tier_counts": {}, "minimum_event_notional": threshold},
                "HOLDOUT_90D": {"selected_symbol_count": "", "tier_counts": {}, "minimum_event_notional": threshold},
            }
        }
        cap_class = capacity_classification(split_name, profile)
        for delay in DELAY_SECONDS:
            latest = metric_bundle(
                threshold_candidate_stats[(split_name, "LATEST_90D", delay)],
                threshold_null_stats[(split_name, "LATEST_90D", delay)],
            )
            holdout = metric_bundle(
                threshold_candidate_stats[(split_name, "HOLDOUT_90D", delay)],
                threshold_null_stats[(split_name, "HOLDOUT_90D", delay)],
            )
            latest_stability = stability_for_threshold(split_name, "LATEST_90D", delay, latest["effect_sign"], threshold_stability_stats)
            holdout_stability = stability_for_threshold(split_name, "HOLDOUT_90D", delay, holdout["effect_sign"], threshold_stability_stats)
            max_cost = max_cost_survived(latest, holdout, latest_stability, holdout_stability)
            classification = diagnostic_classification(max_cost, delay, cap_class, latest, holdout)
            subset_rows.append(
                subset_row(split_name, delay, cap_class, profile, latest, holdout, latest_stability, holdout_stability, max_cost, classification)
            )
            cost_rows.extend(cost_grid_rows(split_name, delay, latest, holdout, latest_stability, holdout_stability, cap_class, classification))
    return subset_rows, cost_rows, split_symbols


def subset_row(
    split_name: str,
    delay: int,
    capacity_class: str,
    profile: dict[str, Any],
    latest: dict[str, Any],
    holdout: dict[str, Any],
    latest_stability: dict[str, Any],
    holdout_stability: dict[str, Any],
    max_cost: float | None,
    classification: str,
) -> dict[str, Any]:
    return {
        "subset": split_name,
        "delay_seconds": delay,
        "candidate": candidate_label(),
        "horizon_seconds": LOCKED_HORIZON_SECONDS,
        "cooldown_seconds": LOCKED_COOLDOWN_SECONDS,
        "latest_event_count": latest["event_count"],
        "holdout_event_count": holdout["event_count"],
        "latest_break_even_cost_bps": rounded_bps(latest["break_even_cost_bps"]),
        "holdout_break_even_cost_bps": rounded_bps(holdout["break_even_cost_bps"]),
        "min_latest_holdout_break_even_cost_bps": rounded_bps(
            min(latest["break_even_cost_bps"] or 0.0, holdout["break_even_cost_bps"] or 0.0)
        ),
        "max_cost_bps_survived": "" if max_cost is None else max_cost,
        "latest_symbol_stability_rate": rounded(latest_stability.get("symbol_stability_rate"), 6),
        "holdout_symbol_stability_rate": rounded(holdout_stability.get("symbol_stability_rate"), 6),
        "latest_week_stability_rate": rounded(latest_stability.get("week_stability_rate"), 6),
        "holdout_week_stability_rate": rounded(holdout_stability.get("week_stability_rate"), 6),
        "latest_month_stability_rate": rounded(latest_stability.get("month_stability_rate"), 6),
        "holdout_month_stability_rate": rounded(holdout_stability.get("month_stability_rate"), 6),
        "latest_directional_diagnostic_rate": rounded(latest.get("directional_diagnostic_rate"), 6),
        "holdout_directional_diagnostic_rate": rounded(holdout.get("directional_diagnostic_rate"), 6),
        "latest_selected_symbol_count": profile["by_window"].get("LATEST_90D", {}).get("selected_symbol_count", ""),
        "holdout_selected_symbol_count": profile["by_window"].get("HOLDOUT_90D", {}).get("selected_symbol_count", ""),
        "latest_capacity_tier_counts": json.dumps(profile["by_window"].get("LATEST_90D", {}).get("tier_counts", {}), sort_keys=True),
        "holdout_capacity_tier_counts": json.dumps(profile["by_window"].get("HOLDOUT_90D", {}).get("tier_counts", {}), sort_keys=True),
        "capacity_classification": capacity_class,
        "diagnostic_classification": classification,
        "survives_without_thin_symbols": str(split_name == "EXCLUDE_THIN" and max_cost is not None).lower(),
    }


def cost_grid_rows(
    split_name: str,
    delay: int,
    latest: dict[str, Any],
    holdout: dict[str, Any],
    latest_stability: dict[str, Any],
    holdout_stability: dict[str, Any],
    capacity_class: str,
    subset_classification: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    latest_edge = latest.get("gross_edge_observed_direction")
    holdout_edge = holdout.get("gross_edge_observed_direction")
    for cost in COST_GRID_BPS:
        latest_net = latest_edge - cost / 10_000 if latest_edge is not None else None
        holdout_net = holdout_edge - cost / 10_000 if holdout_edge is not None else None
        survives = (
            latest_net is not None
            and holdout_net is not None
            and latest_net > 0
            and holdout_net > 0
            and latest.get("event_count", 0) >= MIN_EVENT_COUNT
            and holdout.get("event_count", 0) >= MIN_EVENT_COUNT
            and stability_passes(latest_stability)
            and stability_passes(holdout_stability)
        )
        rows.append(
            {
                "subset": split_name,
                "delay_seconds": delay,
                "cost_bps": cost,
                "latest_net_effect_after_cost_bps": rounded_bps(latest_net * 10_000 if latest_net is not None else None),
                "holdout_net_effect_after_cost_bps": rounded_bps(holdout_net * 10_000 if holdout_net is not None else None),
                "survives_cost": str(survives).lower(),
                "capacity_classification": capacity_class,
                "diagnostic_classification": subset_classification if survives else ("FILTER_ONLY" if latest_edge and holdout_edge and latest_edge > 0 and holdout_edge > 0 else "REJECTED"),
            }
        )
    return rows


def best_capacity_safe_subset(subset_rows: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = [
        row for row in subset_rows
        if row.get("diagnostic_classification") == "FUND_CAPABLE"
        and row.get("capacity_classification") in {"FUND_CAPABLE_CAPACITY", "CAPACITY_SAFE", "CAPACITY_MODERATE"}
        and row.get("max_cost_bps_survived") != ""
    ]
    if not candidates:
        candidates = [
            row for row in subset_rows
            if row.get("max_cost_bps_survived") != ""
            and row.get("capacity_classification") in {"FUND_CAPABLE_CAPACITY", "CAPACITY_SAFE", "CAPACITY_MODERATE"}
        ]
    if not candidates:
        return {}
    return max(
        candidates,
        key=lambda row: (
            float(row.get("max_cost_bps_survived") or 0.0),
            float(row.get("min_latest_holdout_break_even_cost_bps") or 0.0),
            int(row.get("latest_event_count") or 0) + int(row.get("holdout_event_count") or 0),
            -int(row.get("delay_seconds") or 0),
        ),
    )


def final_assessment(best: dict[str, Any]) -> str:
    if not best:
        return "REJECTED"
    return str(best.get("diagnostic_classification") or "REJECTED")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_summary_md(summary: dict[str, Any]) -> None:
    best = summary.get("best_capacity_safe_subset", {})
    lines = [
        "# Sell pressure absorbed capacity-aware refinement v1",
        "",
        f"status: {summary['status']}",
        f"assessment: {summary['assessment']}",
        f"runtime_seconds: {summary['runtime_seconds']}",
        f"symbol_days_processed_total: {summary['symbol_days_processed_total']}",
        f"best_capacity_safe_subset: {best.get('subset', '')}",
        f"best_delay_seconds: {best.get('delay_seconds', '')}",
        f"best_max_cost_bps_survived: {best.get('max_cost_bps_survived', '')}",
        f"best_latest_break_even_bps: {best.get('latest_break_even_cost_bps', '')}",
        f"best_holdout_break_even_bps: {best.get('holdout_break_even_cost_bps', '')}",
        "",
        "This is research diagnostics only. No downloads, full parquet dataset, row-level dataset, live trading, paper trading, orders, private endpoint use, recommendations, PnL curve, entries, exits, stops, or targets are created.",
    ]
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_diagnostic() -> dict[str, Any]:
    started = time.monotonic()
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    if prior.base.path_is_inside(prior.base.DEFAULT_BOOKDEPTH_RAW_ROOT, REPO_ROOT) or prior.base.path_is_inside(
        prior.base.DEFAULT_AGGTRADES_RAW_ROOT,
        REPO_ROOT,
    ):
        raise RuntimeError("raw ZIP roots must stay outside repo")

    candidate_symbol_stats: dict[tuple[str, int, str], RunningStats] = defaultdict(RunningStats)
    candidate_symbol_week_stats: dict[tuple[str, int, str, str], RunningStats] = defaultdict(RunningStats)
    candidate_symbol_month_stats: dict[tuple[str, int, str, str], RunningStats] = defaultdict(RunningStats)
    null_symbol_stats: dict[tuple[str, int, str], RunningStats] = defaultdict(RunningStats)
    threshold_candidate_stats: dict[tuple[str, str, int], RunningStats] = defaultdict(RunningStats)
    threshold_null_stats: dict[tuple[str, str, int], RunningStats] = defaultdict(RunningStats)
    threshold_stability_stats: dict[tuple[str, str, int, str, str], RunningStats] = defaultdict(RunningStats)
    capacity_stats: dict[tuple[str, str], prior.base.DistributionStats] = {}
    capacity_daily_counts: Counter[tuple[str, str, str]] = Counter()
    window_summaries: list[dict[str, Any]] = []

    for window_config in WINDOWS:
        window = str(window_config["window"])
        pairs, _metadata = prior.build_window_pairs(int(window_config["days_to_skip"]), window)
        window_summaries.append(
            process_window(
                window,
                pairs,
                candidate_symbol_stats,
                candidate_symbol_week_stats,
                candidate_symbol_month_stats,
                null_symbol_stats,
                threshold_candidate_stats,
                threshold_null_stats,
                threshold_stability_stats,
                capacity_stats,
                capacity_daily_counts,
            )
        )

    capacity_rows = build_capacity_rows(capacity_stats, capacity_daily_counts)
    subset_rows, cost_rows, split_symbols = build_subset_rows(
        capacity_rows,
        candidate_symbol_stats,
        candidate_symbol_week_stats,
        candidate_symbol_month_stats,
        null_symbol_stats,
        threshold_candidate_stats,
        threshold_null_stats,
        threshold_stability_stats,
    )
    symbol_selection_rows = build_symbol_selection_rows(split_symbols, capacity_rows)
    best = best_capacity_safe_subset(subset_rows)
    assessment = final_assessment(best)

    write_csv(CAPACITY_BY_SYMBOL_CSV, capacity_rows, list(capacity_rows[0].keys()) if capacity_rows else [])
    write_csv(SUBSET_SUMMARY_CSV, subset_rows, list(subset_rows[0].keys()) if subset_rows else [])
    write_csv(DELAY_COST_GRID_CSV, cost_rows, list(cost_rows[0].keys()) if cost_rows else [])
    write_csv(SYMBOL_SELECTION_CSV, symbol_selection_rows, list(symbol_selection_rows[0].keys()) if symbol_selection_rows else [])

    total_processed = sum(prior.int_value(item["processed_symbol_days"]) for item in window_summaries)
    total_failed = sum(prior.int_value(item["failed_symbol_days"]) for item in window_summaries)
    status = (
        "PASS_ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_CAPACITY_AWARE_REFINEMENT"
        if total_processed == EXPECTED_SYMBOL_DAYS_TOTAL and total_failed == 0
        else "PARTIAL_ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_CAPACITY_AWARE_REFINEMENT"
    )
    summary = {
        "status": status,
        "assessment": assessment,
        "created_at_utc": utc_now_text(),
        "task": "ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_CAPACITY_AWARE_REFINEMENT_V1",
        "mode": "LATEST_90D_AND_HOLDOUT_90D_ONLY",
        "candidate": candidate_label(),
        "locked_category": LOCKED_CATEGORY,
        "locked_horizon_seconds": LOCKED_HORIZON_SECONDS,
        "locked_cooldown_seconds": LOCKED_COOLDOWN_SECONDS,
        "delay_seconds": DELAY_SECONDS,
        "cost_grid_bps": COST_GRID_BPS,
        "notional_thresholds": NOTIONAL_THRESHOLDS,
        "top_symbol_counts": TOP_SYMBOL_COUNTS,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "symbol_days_processed_total": total_processed,
        "failed_symbol_days_total": total_failed,
        "window_summaries": window_summaries,
        "best_capacity_safe_subset": best,
        "classification_counts": dict(Counter(str(row["diagnostic_classification"]) for row in subset_rows)),
        "survives_without_thin_symbols": any(
            row.get("subset") == "EXCLUDE_THIN" and row.get("max_cost_bps_survived") != ""
            for row in subset_rows
        ),
        "raw_roots_outside_repo": True,
        "downloads_run": False,
        "full_history_run": False,
        "full_parquet_dataset_created": False,
        "row_level_dataset_created": False,
        "new_feature_discovery_run": False,
        "orders_created": False,
        "private_endpoints_used": False,
        "outputs": {
            "summary_json": str(SUMMARY_JSON),
            "summary_md": str(SUMMARY_MD),
            "subset_summary_csv": str(SUBSET_SUMMARY_CSV),
            "delay_cost_grid_csv": str(DELAY_COST_GRID_CSV),
            "symbol_selection_csv": str(SYMBOL_SELECTION_CSV),
            "capacity_by_symbol_csv": str(CAPACITY_BY_SYMBOL_CSV),
        },
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_summary_md(summary)
    summary["output_sizes_bytes"] = {
        path.name: path.stat().st_size
        for path in [SUMMARY_JSON, SUMMARY_MD, SUBSET_SUMMARY_CSV, DELAY_COST_GRID_CSV, SYMBOL_SELECTION_CSV, CAPACITY_BY_SYMBOL_CSV]
        if path.exists()
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    try:
        summary = run_diagnostic()
    except Exception as exc:  # noqa: BLE001
        error_summary = {
            "status": "FAILED_ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_CAPACITY_AWARE_REFINEMENT",
            "created_at_utc": utc_now_text(),
            "error": f"{type(exc).__name__}: {exc}",
            "downloads_run": False,
            "row_level_dataset_created": False,
        }
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        SUMMARY_JSON.write_text(json.dumps(error_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        SUMMARY_MD.write_text(
            "# Sell pressure absorbed capacity-aware refinement v1\n\n"
            f"status: {error_summary['status']}\n"
            f"error: {error_summary['error']}\n",
            encoding="utf-8",
        )
        print(json.dumps(error_summary, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if str(summary.get("status", "")).startswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
