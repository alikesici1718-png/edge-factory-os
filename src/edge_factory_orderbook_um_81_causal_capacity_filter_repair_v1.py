#!/usr/bin/env python
"""Causal capacity filter repair for locked SELL_PRESSURE_ABSORBED@300s."""

from __future__ import annotations

import bisect
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
PREFIX = "orderbook_um_81_causal_capacity_filter_repair"

SUMMARY_JSON = OUTPUTS_DIR / f"{PREFIX}_summary.json"
SUMMARY_MD = OUTPUTS_DIR / f"{PREFIX}_summary.md"
SUBSET_SUMMARY_CSV = OUTPUTS_DIR / f"{PREFIX}_subset_summary.csv"
DELAY_COST_GRID_CSV = OUTPUTS_DIR / f"{PREFIX}_delay_cost_grid.csv"
INVALIDATED_FILTERS_JSON = OUTPUTS_DIR / f"{PREFIX}_invalidated_non_causal_filters.json"
PRIOR_LIQUIDITY_CSV = OUTPUTS_DIR / f"{PREFIX}_prior_liquidity_symbol_rank.csv"

LOCKED_CATEGORY = prior.LOCKED_CATEGORY
LOCKED_HORIZON_SECONDS = prior.LOCKED_HORIZON_SECONDS
LOCKED_COOLDOWN_SECONDS = prior.LOCKED_COOLDOWN_SECONDS
OBSERVED_PRICE_DIRECTION = prior.OBSERVED_PRICE_DIRECTION
EXPECTED_SYMBOL_DAYS_TOTAL = 14_580
EXPECTED_SYMBOL_COUNT = 81
WINDOWS = prior.WINDOWS

DELAY_SECONDS = [0, 1, 3, 5, 10]
COST_GRID_BPS = [0.0, 1.0, 2.0, 3.0, 5.0, 7.5, 10.0]
TRAILING_WINDOWS_SECONDS = [60, 300, 600]
NOTIONAL_THRESHOLDS = [5_000.0, 10_000.0, 25_000.0, 50_000.0, 100_000.0]
TRADE_COUNT_THRESHOLDS = [5, 10, 25, 50, 100]
TOP_SYMBOL_COUNTS = [10, 20, 40]

BASELINE_FILTER = "BASELINE_ALL_SYMBOLS"
EXCLUDE_THIN_FILTER = "EXCLUDE_CAUSAL_THIN_PRIOR_7D"
PROGRESS_INTERVAL_SECONDS = 30
MIN_EVENT_COUNT = 100
MIN_STABILITY_RATE = 0.5
MIN_SYMBOL_STABILITY_COUNT = 50
MIN_TIME_STABILITY_COUNT = 50

INVALIDATED_NON_CAUSAL_FILTERS = [
    {
        "filter_family": "MIN_AROUND_EVENT_NOTIONAL",
        "reason": "uses notional_around_event with post-event trade notional",
        "replacement_family": "TRAILING_NOTIONAL_*S_GE_*",
        "classification": "NON_CAUSAL_DIAGNOSTIC",
        "selection_allowed": False,
    },
    {
        "filter_family": "TOP_BY_AROUND_EVENT_NOTIONAL",
        "reason": "derived from around-event notional statistics that include post-event data",
        "replacement_family": "TOP_*_BY_CAUSAL_PRIOR_7D_LIQUIDITY",
        "classification": "NON_CAUSAL_DIAGNOSTIC",
        "selection_allowed": False,
    },
    {
        "filter_family": "HIGH_MEDIUM_LOW_THIN_FROM_AROUND_EVENT",
        "reason": "liquidity tier was inferred from around-event notional statistics",
        "replacement_family": "CAUSAL_PRIOR_7D_LIQUIDITY_TIER",
        "classification": "NON_CAUSAL_DIAGNOSTIC",
        "selection_allowed": False,
    },
]


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
        observed = prior.sign_of(value)
        if expected_direction and observed:
            self.directional_total += 1
            if observed == expected_direction:
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


def add_stats(stats: dict[tuple[Any, ...], RunningStats], key: tuple[Any, ...], value: float | None) -> None:
    stats[key].add(value, OBSERVED_PRICE_DIRECTION)


def trailing_trade_slice(event_ms: int, lookback_seconds: int, trade_times: list[int]) -> tuple[int, int]:
    left = bisect.bisect_left(trade_times, event_ms - lookback_seconds * 1000)
    right = bisect.bisect_left(trade_times, event_ms)
    return left, right


def trailing_notional_before_event(
    event_ms: int,
    lookback_seconds: int,
    trade_times: list[int],
    prefix_notionals: list[float],
) -> float:
    left, right = trailing_trade_slice(event_ms, lookback_seconds, trade_times)
    if right <= left:
        return 0.0
    return prefix_notionals[right] - prefix_notionals[left]


def trailing_trade_count_before_event(event_ms: int, lookback_seconds: int, trade_times: list[int]) -> int:
    left, right = trailing_trade_slice(event_ms, lookback_seconds, trade_times)
    return max(0, right - left)


def event_time_bookdepth_notional(row: dict[str, Any]) -> float:
    total = 0.0
    for bucket in prior.base.BUCKETS:
        total += float(row.get(f"bid_notional_pct_{bucket}", 0.0) or 0.0)
        total += float(row.get(f"ask_notional_pct_{bucket}", 0.0) or 0.0)
    return total


def trailing_notional_filter_name(window_seconds: int, threshold: float) -> str:
    return f"TRAILING_NOTIONAL_{window_seconds}S_GE_{int(threshold)}"


def trailing_trade_count_filter_name(window_seconds: int, threshold: int) -> str:
    return f"TRAILING_TRADE_COUNT_{window_seconds}S_GE_{threshold}"


def event_bookdepth_filter_name(threshold: float) -> str:
    return f"EVENT_BOOKDEPTH_NOTIONAL_GE_{int(threshold)}"


def top_prior_liquidity_filter_name(count: int) -> str:
    return f"TOP_{count}_BY_CAUSAL_PRIOR_7D_LIQUIDITY"


def all_filter_names() -> list[str]:
    names = [BASELINE_FILTER]
    names.extend(top_prior_liquidity_filter_name(count) for count in TOP_SYMBOL_COUNTS)
    names.append(EXCLUDE_THIN_FILTER)
    for window_seconds in TRAILING_WINDOWS_SECONDS:
        for threshold in NOTIONAL_THRESHOLDS:
            names.append(trailing_notional_filter_name(window_seconds, threshold))
        for threshold in TRADE_COUNT_THRESHOLDS:
            names.append(trailing_trade_count_filter_name(window_seconds, threshold))
    for threshold in NOTIONAL_THRESHOLDS:
        names.append(event_bookdepth_filter_name(threshold))
    return names


def load_all_verified_dates() -> tuple[dict[tuple[str, str], dict[str, str]], dict[str, list[str]]]:
    agg_rows = prior.base.load_verified_paths(prior.base.AGGTRADES_FILE_STATUS_CSV, prior.base.DEFAULT_AGGTRADES_RAW_ROOT)
    by_symbol: dict[str, list[str]] = defaultdict(list)
    for symbol, file_date in sorted(agg_rows):
        by_symbol[symbol].append(file_date)
    return agg_rows, by_symbol


def row_size_bytes(row: dict[str, str]) -> int:
    value = prior.int_value(row.get("observed_size_bytes"), 0)
    if value > 0:
        return value
    path = Path(str(row.get("local_zip_path", "")))
    return path.stat().st_size if path.exists() else 0


def build_prior_liquidity_profiles(
    window_pairs: dict[str, list[dict[str, Any]]],
    window_metadata: dict[str, dict[str, Any]],
) -> tuple[dict[str, dict[str, set[str]]], list[dict[str, Any]]]:
    agg_rows, by_symbol = load_all_verified_dates()
    profiles: dict[str, dict[str, set[str]]] = {}
    rows: list[dict[str, Any]] = []
    for window in ["LATEST_90D", "HOLDOUT_90D"]:
        scores: dict[str, int] = {}
        details = window_metadata[window].get("window_details", {})
        for symbol in sorted({str(pair["symbol"]) for pair in window_pairs[window]}):
            oldest = str(details.get(symbol, {}).get("oldest", ""))
            dates = [date for date in by_symbol.get(symbol, []) if date < oldest]
            prior_dates = dates[-7:]
            score = sum(row_size_bytes(agg_rows[(symbol, date)]) for date in prior_dates if (symbol, date) in agg_rows)
            scores[symbol] = score
        ranked = [symbol for symbol, _score in sorted(scores.items(), key=lambda item: (item[1], item[0]), reverse=True)]
        profiles[window] = {
            top_prior_liquidity_filter_name(10): set(ranked[:10]),
            top_prior_liquidity_filter_name(20): set(ranked[:20]),
            top_prior_liquidity_filter_name(40): set(ranked[:40]),
            EXCLUDE_THIN_FILTER: set(ranked[:40]),
        }
        for rank, symbol in enumerate(ranked, start=1):
            if rank <= 10:
                tier = "HIGH"
            elif rank <= 20:
                tier = "MEDIUM"
            elif rank <= 40:
                tier = "LOW"
            else:
                tier = "THIN"
            rows.append(
                {
                    "window": window,
                    "symbol": symbol,
                    "prior_7d_aggtrades_zip_size_bytes": scores[symbol],
                    "causal_prior_liquidity_rank": rank,
                    "causal_prior_liquidity_tier": tier,
                    "in_top10": str(symbol in profiles[window][top_prior_liquidity_filter_name(10)]).lower(),
                    "in_top20": str(symbol in profiles[window][top_prior_liquidity_filter_name(20)]).lower(),
                    "in_top40": str(symbol in profiles[window][top_prior_liquidity_filter_name(40)]).lower(),
                    "in_exclude_thin": str(symbol in profiles[window][EXCLUDE_THIN_FILTER]).lower(),
                }
            )
    return profiles, rows


def selected_filters_for_event(
    window: str,
    symbol: str,
    row: dict[str, Any],
    event_ms: int,
    trade_times: list[int],
    prefix_notionals: list[float],
    prior_liquidity_profiles: dict[str, dict[str, set[str]]],
) -> list[str]:
    selected = [BASELINE_FILTER]
    for split_name, symbols in prior_liquidity_profiles.get(window, {}).items():
        if symbol in symbols:
            selected.append(split_name)

    bookdepth_notional = event_time_bookdepth_notional(row)
    for threshold in NOTIONAL_THRESHOLDS:
        if bookdepth_notional >= threshold:
            selected.append(event_bookdepth_filter_name(threshold))

    for window_seconds in TRAILING_WINDOWS_SECONDS:
        trailing_notional = trailing_notional_before_event(event_ms, window_seconds, trade_times, prefix_notionals)
        for threshold in NOTIONAL_THRESHOLDS:
            if trailing_notional >= threshold:
                selected.append(trailing_notional_filter_name(window_seconds, threshold))

        trailing_count = trailing_trade_count_before_event(event_ms, window_seconds, trade_times)
        for threshold in TRADE_COUNT_THRESHOLDS:
            if trailing_count >= threshold:
                selected.append(trailing_trade_count_filter_name(window_seconds, threshold))
    return selected


def process_window(
    window: str,
    pairs: list[dict[str, Any]],
    prior_liquidity_profiles: dict[str, dict[str, set[str]]],
    candidate_stats: dict[tuple[str, str, int], RunningStats],
    null_stats: dict[tuple[str, str, int], RunningStats],
    stability_stats: dict[tuple[str, str, int, str, str], RunningStats],
) -> dict[str, Any]:
    started = time.monotonic()
    processed_symbol_days = 0
    failed_symbol_days = 0
    total_feature_rows = 0
    original_candidate_row_count = 0
    original_event_count = 0
    kept_event_count = 0
    category_counts: Counter[str] = Counter()
    selected_event_counts: Counter[str] = Counter()
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
            week = str(pair["week"])
            month = str(pair["year_month"])
            quarter = month[:4] + "-Q" + str((int(month[5:7]) - 1) // 3 + 1)
            year = month[:4]

            for index, row in enumerate(rows):
                event_ms = timestamps[index]
                category = str(row.get("absorption_category") or "INSUFFICIENT_DATA")
                if category not in prior.base.CATEGORIES:
                    category = "INSUFFICIENT_DATA"
                category_counts[category] += 1
                selected_filters: list[str] | None = None

                for delay in DELAY_SECONDS:
                    null_key = (symbol, delay)
                    if not prior.may_keep_event(last_null_kept_ms.get(null_key), event_ms):
                        continue
                    price_return = prior.delayed_forward_price_return(event_ms, delay, trade_times, trade_prices)
                    if price_return is None:
                        continue
                    last_null_kept_ms[null_key] = event_ms
                    if selected_filters is None:
                        selected_filters = selected_filters_for_event(
                            window,
                            symbol,
                            row,
                            event_ms,
                            trade_times,
                            prefix_notionals,
                            prior_liquidity_profiles,
                        )
                    for filter_name in selected_filters:
                        add_stats(null_stats, (filter_name, window, delay), price_return)

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
                if selected_filters is None:
                    selected_filters = selected_filters_for_event(
                        window,
                        symbol,
                        row,
                        event_ms,
                        trade_times,
                        prefix_notionals,
                        prior_liquidity_profiles,
                    )
                for filter_name in selected_filters:
                    selected_event_counts[filter_name] += 1
                for delay in DELAY_SECONDS:
                    price_return = prior.delayed_forward_price_return(event_ms, delay, trade_times, trade_prices)
                    if price_return is None:
                        continue
                    for filter_name in selected_filters:
                        add_stats(candidate_stats, (filter_name, window, delay), price_return)
                        add_stats(stability_stats, (filter_name, window, delay, "SYMBOL", symbol), price_return)
                        add_stats(stability_stats, (filter_name, window, delay, "WEEK", week), price_return)
                        add_stats(stability_stats, (filter_name, window, delay, "MONTH", month), price_return)
                        add_stats(stability_stats, (filter_name, window, delay, "QUARTER", quarter), price_return)
                        add_stats(stability_stats, (filter_name, window, delay, "YEAR", year), price_return)
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
                "progress phase=causal_capacity_filter_repair "
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
        "selected_event_counts": dict(selected_event_counts),
        "failure_examples": failure_examples,
    }


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


def stability_summary(
    filter_name: str,
    window: str,
    delay: int,
    effect_sign: int,
    stability_stats: dict[tuple[str, str, int, str, str], RunningStats],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    minimums = {
        "SYMBOL": MIN_SYMBOL_STABILITY_COUNT,
        "WEEK": MIN_TIME_STABILITY_COUNT,
        "MONTH": MIN_TIME_STABILITY_COUNT,
        "QUARTER": MIN_TIME_STABILITY_COUNT,
        "YEAR": MIN_TIME_STABILITY_COUNT,
    }
    for period_type, min_count in minimums.items():
        support = 0
        consistent = 0
        for (stat_filter, stat_window, stat_delay, stat_period, _value), stats in stability_stats.items():
            if stat_filter != filter_name or stat_window != window or stat_delay != delay or stat_period != period_type:
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


def stability_passes(stability: dict[str, Any]) -> bool:
    required = [
        stability.get("symbol_stability_rate"),
        stability.get("week_stability_rate"),
        stability.get("month_stability_rate"),
    ]
    present = [value for value in required if value is not None]
    return bool(present) and all(float(value) >= MIN_STABILITY_RATE for value in present)


def filter_capacity_classification(filter_name: str) -> str:
    if filter_name == BASELINE_FILTER:
        return "BASELINE"
    if filter_name == EXCLUDE_THIN_FILTER or filter_name.startswith("TOP_"):
        return "CAUSAL_PRIOR_LIQUIDITY"
    if filter_name.startswith("TRAILING_NOTIONAL_"):
        threshold = float(filter_name.rsplit("_", 1)[-1])
        if threshold >= 100_000:
            return "FUND_CAPABLE_CAUSAL_TRAILING_NOTIONAL"
        if threshold >= 50_000:
            return "CAPACITY_SAFE_CAUSAL_TRAILING_NOTIONAL"
        if threshold >= 25_000:
            return "CAPACITY_MODERATE_CAUSAL_TRAILING_NOTIONAL"
        return "SMALL_CAP_OR_MIXED_CAUSAL_TRAILING_NOTIONAL"
    if filter_name.startswith("TRAILING_TRADE_COUNT_"):
        return "CAUSAL_TRAILING_TRADE_COUNT_PROXY"
    if filter_name.startswith("EVENT_BOOKDEPTH_NOTIONAL_"):
        threshold = float(filter_name.rsplit("_", 1)[-1])
        if threshold >= 100_000:
            return "FUND_CAPABLE_EVENT_TIME_BOOKDEPTH"
        if threshold >= 50_000:
            return "CAPACITY_SAFE_EVENT_TIME_BOOKDEPTH"
        return "EVENT_TIME_BOOKDEPTH_PROXY"
    return "UNKNOWN"


def max_cost_survived(
    latest: dict[str, Any],
    holdout: dict[str, Any],
    latest_stability: dict[str, Any],
    holdout_stability: dict[str, Any],
) -> float | None:
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


def diagnostic_classification(filter_name: str, max_cost: float | None, latest: dict[str, Any], holdout: dict[str, Any]) -> str:
    latest_edge = latest.get("gross_edge_observed_direction")
    holdout_edge = holdout.get("gross_edge_observed_direction")
    if latest_edge is None or holdout_edge is None or latest_edge <= 0 or holdout_edge <= 0:
        return "REJECTED"
    if max_cost is None:
        return "FILTER_ONLY"
    capacity_class = filter_capacity_classification(filter_name)
    if "FUND_CAPABLE" in capacity_class and max_cost >= 5.0:
        return "FUND_CAPABLE"
    if "CAPACITY_SAFE" in capacity_class and max_cost >= 3.0:
        return "CAPACITY_SAFE"
    if max_cost >= 1.0:
        return "FILTER_ONLY"
    return "FILTER_ONLY"


def subset_row(
    filter_name: str,
    delay: int,
    latest: dict[str, Any],
    holdout: dict[str, Any],
    latest_stability: dict[str, Any],
    holdout_stability: dict[str, Any],
    max_cost: float | None,
    classification: str,
) -> dict[str, Any]:
    return {
        "filter_name": filter_name,
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
        "capacity_classification": filter_capacity_classification(filter_name),
        "diagnostic_classification": classification,
    }


def cost_grid_rows(
    filter_name: str,
    delay: int,
    latest: dict[str, Any],
    holdout: dict[str, Any],
    latest_stability: dict[str, Any],
    holdout_stability: dict[str, Any],
    classification: str,
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
                "filter_name": filter_name,
                "delay_seconds": delay,
                "cost_bps": cost,
                "latest_net_effect_after_cost_bps": rounded_bps(latest_net * 10_000 if latest_net is not None else None),
                "holdout_net_effect_after_cost_bps": rounded_bps(holdout_net * 10_000 if holdout_net is not None else None),
                "survives_cost": str(survives).lower(),
                "capacity_classification": filter_capacity_classification(filter_name),
                "diagnostic_classification": classification if survives else ("FILTER_ONLY" if latest_edge and holdout_edge and latest_edge > 0 and holdout_edge > 0 else "REJECTED"),
            }
        )
    return rows


def build_output_rows(
    candidate_stats: dict[tuple[str, str, int], RunningStats],
    null_stats: dict[tuple[str, str, int], RunningStats],
    stability_stats: dict[tuple[str, str, int, str, str], RunningStats],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    subset_rows: list[dict[str, Any]] = []
    cost_rows: list[dict[str, Any]] = []
    for filter_name in all_filter_names():
        for delay in DELAY_SECONDS:
            latest = metric_bundle(
                candidate_stats[(filter_name, "LATEST_90D", delay)],
                null_stats[(filter_name, "LATEST_90D", delay)],
            )
            holdout = metric_bundle(
                candidate_stats[(filter_name, "HOLDOUT_90D", delay)],
                null_stats[(filter_name, "HOLDOUT_90D", delay)],
            )
            latest_stability = stability_summary(filter_name, "LATEST_90D", delay, latest["effect_sign"], stability_stats)
            holdout_stability = stability_summary(filter_name, "HOLDOUT_90D", delay, holdout["effect_sign"], stability_stats)
            max_cost = max_cost_survived(latest, holdout, latest_stability, holdout_stability)
            classification = diagnostic_classification(filter_name, max_cost, latest, holdout)
            subset_rows.append(subset_row(filter_name, delay, latest, holdout, latest_stability, holdout_stability, max_cost, classification))
            cost_rows.extend(cost_grid_rows(filter_name, delay, latest, holdout, latest_stability, holdout_stability, classification))
    return subset_rows, cost_rows


def best_causal_subset(subset_rows: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = [
        row for row in subset_rows
        if row["filter_name"] != BASELINE_FILTER
        and row.get("diagnostic_classification") in {"FUND_CAPABLE", "CAPACITY_SAFE", "FILTER_ONLY"}
        and row.get("max_cost_bps_survived") != ""
        and row.get("capacity_classification") not in {"BASELINE", "SMALL_CAP_OR_MIXED_CAUSAL_TRAILING_NOTIONAL"}
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


def baseline_delay_zero(subset_rows: list[dict[str, Any]]) -> dict[str, Any]:
    for row in subset_rows:
        if row["filter_name"] == BASELINE_FILTER and int(row["delay_seconds"]) == 0:
            return row
    return {}


def repair_succeeded(best: dict[str, Any], baseline: dict[str, Any]) -> bool:
    if not best or not baseline:
        return False
    best_be = float(best.get("min_latest_holdout_break_even_cost_bps") or 0.0)
    baseline_be = float(baseline.get("min_latest_holdout_break_even_cost_bps") or 0.0)
    best_cost = float(best.get("max_cost_bps_survived") or 0.0)
    baseline_cost = float(baseline.get("max_cost_bps_survived") or 0.0)
    return best_be > baseline_be and best_cost >= baseline_cost


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_summary_md(summary: dict[str, Any]) -> None:
    best = summary.get("best_causal_capacity_subset", {})
    baseline = summary.get("baseline_delay_zero", {})
    lines = [
        "# Causal capacity filter repair v1",
        "",
        f"status: {summary['status']}",
        f"causal_capacity_repair_succeeded: {str(summary['causal_capacity_repair_succeeded']).lower()}",
        f"best_filter_name: {best.get('filter_name', '')}",
        f"best_delay_seconds: {best.get('delay_seconds', '')}",
        f"best_latest_break_even_bps: {best.get('latest_break_even_cost_bps', '')}",
        f"best_holdout_break_even_bps: {best.get('holdout_break_even_cost_bps', '')}",
        f"best_max_cost_bps_survived: {best.get('max_cost_bps_survived', '')}",
        f"baseline_min_break_even_bps: {baseline.get('min_latest_holdout_break_even_cost_bps', '')}",
        "",
        "Invalidated non-causal around-event filters are reported but not used. No downloads, parquet dataset, row-level dataset, strategy, backtest, PnL, orders, private endpoints, or recommendations were created.",
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

    window_pairs: dict[str, list[dict[str, Any]]] = {}
    window_metadata: dict[str, dict[str, Any]] = {}
    for window_config in WINDOWS:
        window = str(window_config["window"])
        pairs, metadata = prior.build_window_pairs(int(window_config["days_to_skip"]), window)
        window_pairs[window] = pairs
        window_metadata[window] = metadata

    prior_liquidity_profiles, prior_liquidity_rows = build_prior_liquidity_profiles(window_pairs, window_metadata)
    write_csv(PRIOR_LIQUIDITY_CSV, prior_liquidity_rows, list(prior_liquidity_rows[0].keys()) if prior_liquidity_rows else [])
    INVALIDATED_FILTERS_JSON.write_text(json.dumps(INVALIDATED_NON_CAUSAL_FILTERS, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    candidate_stats: dict[tuple[str, str, int], RunningStats] = defaultdict(RunningStats)
    null_stats: dict[tuple[str, str, int], RunningStats] = defaultdict(RunningStats)
    stability_stats: dict[tuple[str, str, int, str, str], RunningStats] = defaultdict(RunningStats)
    window_summaries: list[dict[str, Any]] = []

    for window in ["LATEST_90D", "HOLDOUT_90D"]:
        window_summaries.append(
            process_window(
                window,
                window_pairs[window],
                prior_liquidity_profiles,
                candidate_stats,
                null_stats,
                stability_stats,
            )
        )

    subset_rows, cost_rows = build_output_rows(candidate_stats, null_stats, stability_stats)
    write_csv(SUBSET_SUMMARY_CSV, subset_rows, list(subset_rows[0].keys()) if subset_rows else [])
    write_csv(DELAY_COST_GRID_CSV, cost_rows, list(cost_rows[0].keys()) if cost_rows else [])

    best = best_causal_subset(subset_rows)
    baseline = baseline_delay_zero(subset_rows)
    succeeded = repair_succeeded(best, baseline)
    total_processed = sum(prior.int_value(item["processed_symbol_days"]) for item in window_summaries)
    total_failed = sum(prior.int_value(item["failed_symbol_days"]) for item in window_summaries)
    status = (
        "PASS_ORDERBOOK_UM_81_CAUSAL_CAPACITY_FILTER_REPAIR"
        if total_processed == EXPECTED_SYMBOL_DAYS_TOTAL and total_failed == 0
        else "PARTIAL_ORDERBOOK_UM_81_CAUSAL_CAPACITY_FILTER_REPAIR"
    )
    summary = {
        "status": status,
        "created_at_utc": utc_now_text(),
        "task": "ORDERBOOK_UM_81_CAUSAL_CAPACITY_FILTER_REPAIR_V1",
        "candidate": candidate_label(),
        "locked_category": LOCKED_CATEGORY,
        "locked_horizon_seconds": LOCKED_HORIZON_SECONDS,
        "locked_cooldown_seconds": LOCKED_COOLDOWN_SECONDS,
        "mode": "LATEST_90D_AND_HOLDOUT_90D_ONLY",
        "delay_seconds": DELAY_SECONDS,
        "cost_grid_bps": COST_GRID_BPS,
        "causal_filter_families_tested": [
            "trailing aggTrades notional before event",
            "trailing aggTrades trade count before event",
            "event-time bookDepth notional",
            "causal prior-7-day symbol liquidity rank",
        ],
        "invalidated_non_causal_filters": INVALIDATED_NON_CAUSAL_FILTERS,
        "old_non_causal_result_must_not_be_used": True,
        "causal_selection_uses_future_window": False,
        "causal_selection_uses_post_event_notional": False,
        "causal_selection_uses_post_event_trade_count": False,
        "causal_selection_uses_post_event_volatility": False,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "symbol_days_processed_total": total_processed,
        "failed_symbol_days_total": total_failed,
        "window_summaries": window_summaries,
        "baseline_delay_zero": baseline,
        "best_causal_capacity_subset": best,
        "classification_counts": dict(Counter(str(row["diagnostic_classification"]) for row in subset_rows)),
        "causal_capacity_repair_succeeded": succeeded,
        "beats_baseline_definition": "best causal non-baseline subset has higher min latest/holdout break-even bps and at least baseline max survived cost",
        "downloads_run": False,
        "raw_data_modified": False,
        "full_history_run": False,
        "full_parquet_dataset_created": False,
        "row_level_dataset_created": False,
        "strategy_created": False,
        "backtest_created": False,
        "pnl_created": False,
        "orders_created": False,
        "private_endpoints_used": False,
        "recommendations_created": False,
        "outputs": {
            "summary_json": str(SUMMARY_JSON),
            "summary_md": str(SUMMARY_MD),
            "subset_summary_csv": str(SUBSET_SUMMARY_CSV),
            "delay_cost_grid_csv": str(DELAY_COST_GRID_CSV),
            "invalidated_filters_json": str(INVALIDATED_FILTERS_JSON),
            "prior_liquidity_csv": str(PRIOR_LIQUIDITY_CSV),
        },
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_summary_md(summary)
    summary["output_sizes_bytes"] = {
        path.name: path.stat().st_size
        for path in [SUMMARY_JSON, SUMMARY_MD, SUBSET_SUMMARY_CSV, DELAY_COST_GRID_CSV, INVALIDATED_FILTERS_JSON, PRIOR_LIQUIDITY_CSV]
        if path.exists()
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    try:
        summary = run_diagnostic()
    except Exception as exc:  # noqa: BLE001
        summary = {
            "status": "FAILED_ORDERBOOK_UM_81_CAUSAL_CAPACITY_FILTER_REPAIR",
            "created_at_utc": utc_now_text(),
            "error": f"{type(exc).__name__}: {exc}",
            "downloads_run": False,
            "row_level_dataset_created": False,
        }
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        SUMMARY_MD.write_text(
            "# Causal capacity filter repair v1\n\n"
            f"status: {summary['status']}\n"
            f"error: {summary['error']}\n",
            encoding="utf-8",
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if str(summary.get("status", "")).startswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
