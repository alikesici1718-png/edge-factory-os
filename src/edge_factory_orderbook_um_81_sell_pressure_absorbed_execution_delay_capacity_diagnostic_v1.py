#!/usr/bin/env python
"""Execution delay and capacity diagnostic for locked SELL_PRESSURE_ABSORBED@300s."""

from __future__ import annotations

import bisect
import csv
import json
import math
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import edge_factory_orderbook_um_81_absorption_candidate_price_linkage_validation_v1 as price_linkage
import edge_factory_orderbook_um_81_streaming_absorption_discovery_90d_v1 as base


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"
PREFIX = "orderbook_um_81_sell_pressure_absorbed_execution_delay_capacity"

SUMMARY_JSON = OUTPUTS_DIR / f"{PREFIX}_summary.json"
SUMMARY_MD = OUTPUTS_DIR / f"{PREFIX}_summary.md"
DELAY_COST_GRID_CSV = OUTPUTS_DIR / f"{PREFIX}_delay_cost_grid.csv"
CAPACITY_CSV = OUTPUTS_DIR / f"{PREFIX}_capacity_by_symbol_window.csv"
STABILITY_CSV = OUTPUTS_DIR / f"{PREFIX}_stability.csv"
NULL_COMPARISON_CSV = OUTPUTS_DIR / f"{PREFIX}_null_comparison.csv"

LOCKED_CATEGORY = "SELL_PRESSURE_ABSORBED"
LOCKED_HORIZON_SECONDS = 300
LOCKED_COOLDOWN_SECONDS = 600
OBSERVED_PRICE_DIRECTION = -1
WINDOW_DAYS = 90
EXPECTED_SYMBOL_COUNT = 81
EXPECTED_SYMBOL_DAYS_TOTAL = 14_580
DELAY_SECONDS = [0, 1, 3, 5, 10, 30]
COST_GRID_BPS = [0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0]
WINDOWS = [
    {"window": "LATEST_90D", "days_to_skip": 0},
    {"window": "HOLDOUT_90D", "days_to_skip": 90},
]
MIN_EVENT_COUNT = 100
MIN_STABILITY_RATE = 0.5
MIN_CAPACITY_SYMBOLS = 60
PROGRESS_INTERVAL_SECONDS = 30
RESERVOIR_LIMIT = 50_000
CAPACITY_RESERVOIR_LIMIT = 20_000
CAPACITY_WINDOW_RADIUS_MS = 30_000


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def int_value(value: Any, default: int = 0) -> int:
    return base.int_value(value, default)


def float_value(value: Any, default: float = 0.0) -> float:
    return base.float_value(value, default)


def float_or_none(value: Any) -> float | None:
    return price_linkage.float_or_none(value)


def rounded(value: float | None, places: int = 12) -> float | str:
    if value is None or math.isnan(value):
        return ""
    return round(value, places)


def safe_div(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def sign_of(value: float | None, tolerance: float = 1e-12) -> int:
    if value is None or abs(value) <= tolerance:
        return 0
    return 1 if value > 0 else -1


def candidate_label() -> str:
    return f"{LOCKED_CATEGORY}@{LOCKED_HORIZON_SECONDS}s"


def observed_direction_text() -> str:
    return "NEGATIVE_PRICE_EFFECT" if OBSERVED_PRICE_DIRECTION < 0 else "POSITIVE_PRICE_EFFECT"


def fresh_distribution(seed_text: str, sample_limit: int = RESERVOIR_LIMIT) -> base.DistributionStats:
    return base.DistributionStats(sample_limit=sample_limit, seed_text=seed_text)


def may_keep_event(last_kept_ms: int | None, event_ms: int) -> bool:
    if last_kept_ms is None:
        return True
    return event_ms - last_kept_ms >= LOCKED_COOLDOWN_SECONDS * 1000


def build_window_pairs(days_to_skip: int, window: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    pairs, metadata = price_linkage.build_window_pairs(days_to_skip)
    for pair in pairs:
        pair["validation_window"] = window
        pair["year_month"] = str(pair.get("year_month") or str(pair["file_date"])[:7])
        pair["week"] = str(pair.get("week") or base.iso_week_text(str(pair["file_date"])))
    return pairs, metadata


def read_features_trade_details(
    pair: dict[str, Any],
) -> tuple[list[int], list[dict[str, Any]], list[int], list[float], list[float], list[float]]:
    timestamps, rows = base.read_bookdepth_features(pair)
    if not timestamps:
        return timestamps, rows, [], [], [], [0.0]

    trade_times: list[int] = []
    trade_prices: list[float] = []
    trade_notionals: list[float] = []
    out_of_order = False
    previous_trade_ms = -1
    reader = iter(base.single_csv_reader(Path(str(pair["aggtrades_zip_path"]))))
    header = next(reader, None)
    if not header:
        base.add_rolling_features(rows)
        return timestamps, rows, [], [], [], [0.0]
    positions = {name: index for index, name in enumerate(header)}
    required = {"price", "quantity", "transact_time", "is_buyer_maker"}
    if not required.issubset(positions):
        raise ValueError(f"aggTrades CSV missing columns: {required - set(positions)}")

    for columns in reader:
        transact_ms = int_value(columns[positions["transact_time"]], -1)
        price = float_value(columns[positions["price"]])
        quantity = float_value(columns[positions["quantity"]])
        notional = price * quantity
        if transact_ms < previous_trade_ms:
            out_of_order = True
        previous_trade_ms = transact_ms
        trade_times.append(transact_ms)
        trade_prices.append(price)
        trade_notionals.append(notional)

        row_index = bisect.bisect_right(timestamps, transact_ms) - 1
        if row_index < 0:
            continue
        row = rows[row_index]
        row["trade_count"] += 1
        row["total_qty"] += quantity
        row["total_notional"] += notional
        if base.bool_value(columns[positions["is_buyer_maker"]]):
            row["aggressive_sell_qty"] += quantity
            row["aggressive_sell_notional"] += notional
        else:
            row["aggressive_buy_qty"] += quantity
            row["aggressive_buy_notional"] += notional

    if out_of_order:
        combined = sorted(zip(trade_times, trade_prices, trade_notionals), key=lambda item: item[0])
        trade_times = [item[0] for item in combined]
        trade_prices = [item[1] for item in combined]
        trade_notionals = [item[2] for item in combined]
    prefix_notionals = [0.0]
    running = 0.0
    for notional in trade_notionals:
        running += notional
        prefix_notionals.append(running)
    base.add_rolling_features(rows)
    return timestamps, rows, trade_times, trade_prices, trade_notionals, prefix_notionals


def delayed_forward_price_return(
    event_ms: int,
    delay_seconds: int,
    trade_times: list[int],
    trade_prices: list[float],
) -> float | None:
    if not trade_times:
        return None
    reference_ms = event_ms + delay_seconds * 1000
    future_ms = event_ms + LOCKED_HORIZON_SECONDS * 1000
    if reference_ms >= future_ms:
        return None
    reference_index = bisect.bisect_right(trade_times, reference_ms) - 1
    future_index = bisect.bisect_left(trade_times, future_ms)
    if reference_index < 0 or future_index >= len(trade_prices):
        return None
    reference_price = trade_prices[reference_index]
    future_price = trade_prices[future_index]
    if reference_price <= 0:
        return None
    return (future_price / reference_price) - 1.0


def notional_around_event(event_ms: int, trade_times: list[int], prefix_notionals: list[float]) -> float | None:
    if not trade_times:
        return None
    left = bisect.bisect_left(trade_times, event_ms - CAPACITY_WINDOW_RADIUS_MS)
    right = bisect.bisect_right(trade_times, event_ms + CAPACITY_WINDOW_RADIUS_MS)
    if right <= left:
        return 0.0
    return prefix_notionals[right] - prefix_notionals[left]


def add_candidate_return(
    price_return: float,
    window: str,
    delay: int,
    symbol: str,
    month: str,
    week: str,
    candidate_stats: dict[tuple[str, int], base.DistributionStats],
    stability_stats: dict[tuple[str, int, str, str], base.MomentStats],
) -> None:
    key = (window, delay)
    if key not in candidate_stats:
        candidate_stats[key] = fresh_distribution(f"candidate:{window}:{delay}")
    candidate_stats[key].add_diagnostic(price_return, OBSERVED_PRICE_DIRECTION, "UNUSED", None, None, None)
    stability_stats[(window, delay, "SYMBOL", symbol)].add(price_return, OBSERVED_PRICE_DIRECTION)
    stability_stats[(window, delay, "MONTH", month)].add(price_return, OBSERVED_PRICE_DIRECTION)
    stability_stats[(window, delay, "WEEK", week)].add(price_return, OBSERVED_PRICE_DIRECTION)


def add_null_return(
    price_return: float,
    window: str,
    delay: int,
    null_stats: dict[tuple[str, int], base.MomentStats],
) -> None:
    null_stats[(window, delay)].add(price_return, OBSERVED_PRICE_DIRECTION)


def capacity_distribution(seed_text: str) -> base.DistributionStats:
    return fresh_distribution(seed_text, sample_limit=CAPACITY_RESERVOIR_LIMIT)


def process_window(
    window: str,
    pairs: list[dict[str, Any]],
    candidate_stats: dict[tuple[str, int], base.DistributionStats],
    null_stats: dict[tuple[str, int], base.MomentStats],
    stability_stats: dict[tuple[str, int, str, str], base.MomentStats],
    capacity_stats: dict[tuple[str, str], base.DistributionStats],
    capacity_daily_counts: Counter[tuple[str, str, str]],
    capacity_hour_counts: Counter[tuple[str, str, int]],
    total_trade_notional: Counter[tuple[str, str]],
) -> dict[str, Any]:
    started = time.monotonic()
    processed_symbol_days = 0
    failed_symbol_days = 0
    total_feature_rows = 0
    original_candidate_row_count = 0
    original_event_count = 0
    kept_event_count = 0
    null_original_counts: Counter[int] = Counter()
    category_counts: Counter[str] = Counter()
    failure_examples: list[dict[str, str]] = []
    last_candidate_kept_ms: dict[str, int] = {}
    last_null_kept_ms: dict[tuple[str, int], int] = {}
    next_progress = time.monotonic() + PROGRESS_INTERVAL_SECONDS

    for pair in pairs:
        try:
            timestamps, rows, trade_times, trade_prices, _trade_notionals, prefix_notionals = read_features_trade_details(pair)
            processed_symbol_days += 1
            total_feature_rows += len(rows)
            symbol = str(pair["symbol"])
            month = str(pair["year_month"])
            week = str(pair["week"])
            file_date = str(pair["file_date"])
            total_trade_notional[(window, symbol)] += prefix_notionals[-1] if prefix_notionals else 0.0
            for index, row in enumerate(rows):
                category = str(row.get("absorption_category") or "INSUFFICIENT_DATA")
                if category not in base.CATEGORIES:
                    category = "INSUFFICIENT_DATA"
                category_counts[category] += 1
                event_ms = timestamps[index]
                for delay in DELAY_SECONDS:
                    null_key = (symbol, delay)
                    if not may_keep_event(last_null_kept_ms.get(null_key), event_ms):
                        continue
                    price_return = delayed_forward_price_return(event_ms, delay, trade_times, trade_prices)
                    if price_return is None:
                        continue
                    null_original_counts[delay] += 1
                    last_null_kept_ms[null_key] = event_ms
                    add_null_return(price_return, window, delay, null_stats)

                if category != LOCKED_CATEGORY:
                    continue
                original_candidate_row_count += 1
                base_return = delayed_forward_price_return(event_ms, 0, trade_times, trade_prices)
                if base_return is None:
                    continue
                original_event_count += 1
                if not may_keep_event(last_candidate_kept_ms.get(symbol), event_ms):
                    continue
                last_candidate_kept_ms[symbol] = event_ms
                kept_event_count += 1
                capacity_key = (window, symbol)
                if capacity_key not in capacity_stats:
                    capacity_stats[capacity_key] = capacity_distribution(f"capacity:{window}:{symbol}")
                around_notional = notional_around_event(event_ms, trade_times, prefix_notionals)
                capacity_stats[capacity_key].add_diagnostic(around_notional, 0, "UNUSED", None, None, None)
                capacity_daily_counts[(window, symbol, file_date)] += 1
                hour = datetime.fromtimestamp(event_ms / 1000, tz=timezone.utc).hour
                capacity_hour_counts[(window, symbol, hour)] += 1
                for delay in DELAY_SECONDS:
                    price_return = delayed_forward_price_return(event_ms, delay, trade_times, trade_prices)
                    if price_return is None:
                        continue
                    add_candidate_return(
                        price_return,
                        window,
                        delay,
                        symbol,
                        month,
                        week,
                        candidate_stats,
                        stability_stats,
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
                "progress phase=sell_pressure_delay_capacity "
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
        "null_original_counts_by_delay": dict(null_original_counts),
        "category_counts": dict(category_counts),
        "failure_examples": failure_examples,
    }


def stats_metrics(stats: base.DistributionStats | base.MomentStats) -> dict[str, Any]:
    median_value = stats.sampled_median() if isinstance(stats, base.DistributionStats) else None
    return {
        "event_count": stats.valid_forward_count,
        "gross_mean_forward_price_return": rounded(stats.mean()),
        "gross_median_forward_price_return": rounded(median_value),
        "gross_std_forward_price_return": rounded(stats.std()),
        "directional_diagnostic_rate": rounded(stats.directional_rate(), 6),
    }


def stability_summary(
    window: str,
    delay: int,
    effect_sign: int,
    stability_stats: dict[tuple[str, int, str, str], base.MomentStats],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for period_type in ["SYMBOL", "MONTH", "WEEK"]:
        support = 0
        consistent = 0
        min_count = 100 if period_type == "SYMBOL" else 50
        for key, stats in stability_stats.items():
            candidate_window, candidate_delay, candidate_period_type, _period_value = key
            if candidate_window != window or candidate_delay != delay or candidate_period_type != period_type:
                continue
            mean_value = stats.mean()
            if mean_value is None or stats.valid_forward_count < min_count:
                continue
            support += 1
            if effect_sign and sign_of(mean_value) == effect_sign:
                consistent += 1
        prefix = period_type.lower()
        result[f"{prefix}_support_count"] = support
        result[f"{prefix}_consistent_count"] = consistent
        result[f"{prefix}_stability_rate"] = safe_div(consistent, support)
    return result


def stability_detail_rows(
    candidate_stats: dict[tuple[str, int], base.DistributionStats],
    stability_stats: dict[tuple[str, int, str, str], base.MomentStats],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    effect_signs = {
        key: sign_of(stats.mean())
        for key, stats in candidate_stats.items()
    }
    for key in sorted(stability_stats):
        window, delay, period_type, period_value = key
        stats = stability_stats[key]
        mean_value = stats.mean()
        effect_sign = effect_signs.get((window, delay), 0)
        rows.append(
            {
                "window": window,
                "delay_seconds": delay,
                "period_type": period_type,
                "period_value": period_value,
                "event_count": stats.valid_forward_count,
                "mean_forward_price_return": rounded(mean_value),
                "std_forward_price_return": rounded(stats.std()),
                "directional_diagnostic_rate": rounded(stats.directional_rate(), 6),
                "consistent_with_window_effect": str(effect_sign and sign_of(mean_value) == effect_sign).lower(),
            }
        )
    return rows


def liquidity_tier(p50_notional: float | None) -> str:
    if p50_notional is None:
        return "UNKNOWN"
    if p50_notional >= 1_000_000:
        return "HIGH"
    if p50_notional >= 250_000:
        return "MEDIUM"
    if p50_notional >= 50_000:
        return "LOW"
    return "THIN"


def capacity_rows(
    capacity_stats: dict[tuple[str, str], base.DistributionStats],
    capacity_daily_counts: Counter[tuple[str, str, str]],
    capacity_hour_counts: Counter[tuple[str, str, int]],
    total_trade_notional: Counter[tuple[str, str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for window, symbol in sorted(capacity_stats):
        stats = capacity_stats[(window, symbol)]
        p25 = stats.quantile(0.25)
        p50 = stats.quantile(0.50)
        p75 = stats.quantile(0.75)
        p90 = stats.quantile(0.90)
        daily_counts = [
            count for (count_window, count_symbol, _date), count in capacity_daily_counts.items()
            if count_window == window and count_symbol == symbol
        ]
        hour_counts = {
            hour: count
            for (count_window, count_symbol, hour), count in capacity_hour_counts.items()
            if count_window == window and count_symbol == symbol
        }
        busiest_hour = max(hour_counts, key=hour_counts.get) if hour_counts else ""
        busiest_hour_count = hour_counts.get(busiest_hour, 0) if busiest_hour != "" else 0
        total_window_notional = float(total_trade_notional[(window, symbol)])
        pressure = safe_div(stats.valid_forward_count * (p50 or 0.0), total_window_notional)
        rows.append(
            {
                "window": window,
                "symbol": symbol,
                "kept_event_count": stats.valid_forward_count,
                "median_aggtrades_notional_around_event": rounded(p50, 4),
                "p25_aggtrades_notional_around_event": rounded(p25, 4),
                "p50_aggtrades_notional_around_event": rounded(p50, 4),
                "p75_aggtrades_notional_around_event": rounded(p75, 4),
                "p90_aggtrades_notional_around_event": rounded(p90, 4),
                "estimated_safe_notional_conservative": rounded((p25 or 0.0) * 0.01, 4),
                "estimated_safe_notional_moderate": rounded((p25 or 0.0) * 0.025, 4),
                "estimated_safe_notional_upper_diagnostic": rounded((p25 or 0.0) * 0.05, 4),
                "symbol_liquidity_tier": liquidity_tier(p50),
                "max_events_per_day": max(daily_counts) if daily_counts else 0,
                "mean_events_per_active_day": rounded(sum(daily_counts) / len(daily_counts), 6) if daily_counts else "",
                "busiest_event_hour_utc": busiest_hour,
                "busiest_event_hour_count": busiest_hour_count,
                "busiest_hour_event_share": rounded(safe_div(busiest_hour_count, stats.valid_forward_count), 6),
                "window_trade_notional_total": rounded(total_window_notional, 4),
                "turnover_pressure_proxy": rounded(pressure, 10),
            }
        )
    return rows


def capacity_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    tiers = Counter(str(row.get("symbol_liquidity_tier", "")) for row in rows)
    by_window: dict[str, dict[str, Any]] = {}
    for window in ["LATEST_90D", "HOLDOUT_90D"]:
        window_rows = [row for row in rows if row.get("window") == window]
        p50_values = [float_or_none(row.get("p50_aggtrades_notional_around_event")) for row in window_rows]
        p50_values = [value for value in p50_values if value is not None]
        pressure_values = [float_or_none(row.get("turnover_pressure_proxy")) for row in window_rows]
        pressure_values = [value for value in pressure_values if value is not None]
        by_window[window] = {
            "symbol_count": len(window_rows),
            "liquidity_tier_counts": dict(Counter(str(row.get("symbol_liquidity_tier", "")) for row in window_rows)),
            "median_symbol_event_notional_p50": rounded(sorted(p50_values)[len(p50_values) // 2] if p50_values else None, 4),
            "max_symbol_turnover_pressure_proxy": rounded(max(pressure_values) if pressure_values else None, 10),
            "max_events_per_day": max((int_value(row.get("max_events_per_day")) for row in window_rows), default=0),
        }
    return {"tier_counts": dict(tiers), "by_window": by_window}


def build_delay_window_metrics(
    candidate_stats: dict[tuple[str, int], base.DistributionStats],
    null_stats: dict[tuple[str, int], base.MomentStats],
    stability_stats: dict[tuple[str, int, str, str], base.MomentStats],
) -> dict[tuple[str, int], dict[str, Any]]:
    metrics: dict[tuple[str, int], dict[str, Any]] = {}
    for window in ["LATEST_90D", "HOLDOUT_90D"]:
        for delay in DELAY_SECONDS:
            candidate = candidate_stats.get((window, delay), fresh_distribution(f"empty:{window}:{delay}"))
            null = null_stats[(window, delay)]
            candidate_mean = candidate.mean()
            null_mean = null.mean()
            effect = candidate_mean - null_mean if candidate_mean is not None and null_mean is not None else None
            gross_edge = effect * OBSERVED_PRICE_DIRECTION if effect is not None else None
            break_even = max(0.0, gross_edge * 10_000) if gross_edge is not None else None
            effect_sign = sign_of(effect)
            stability = stability_summary(window, delay, effect_sign, stability_stats)
            metrics[(window, delay)] = {
                **stats_metrics(candidate),
                "null_event_count": null.valid_forward_count,
                "null_mean_forward_price_return": rounded(null_mean),
                "null_std_forward_price_return": rounded(null.std()),
                "gross_effect_vs_null_signed": rounded(effect),
                "gross_edge_observed_direction": rounded(gross_edge),
                "break_even_cost_bps": rounded(break_even, 6),
                **{
                    key: rounded(value, 6) if key.endswith("_rate") else value
                    for key, value in stability.items()
                },
            }
    return metrics


def classify_delay_cost(
    delay: int,
    cost_bps: float,
    latest: dict[str, Any],
    holdout: dict[str, Any],
    delay_zero_cost_row: dict[float, bool],
    capacity_ok: bool,
) -> str:
    latest_edge = float_or_none(latest.get("gross_edge_observed_direction"))
    holdout_edge = float_or_none(holdout.get("gross_edge_observed_direction"))
    if latest_edge is None or holdout_edge is None:
        return "REJECTED"
    if int_value(latest.get("event_count")) < MIN_EVENT_COUNT or int_value(holdout.get("event_count")) < MIN_EVENT_COUNT:
        return "REJECTED"
    stable_values = [
        float_or_none(latest.get("symbol_stability_rate")),
        float_or_none(latest.get("month_stability_rate")),
        float_or_none(latest.get("week_stability_rate")),
        float_or_none(holdout.get("symbol_stability_rate")),
        float_or_none(holdout.get("month_stability_rate")),
        float_or_none(holdout.get("week_stability_rate")),
    ]
    if not all(value is not None and value >= MIN_STABILITY_RATE for value in stable_values):
        return "REJECTED"
    latest_net = latest_edge - (cost_bps / 10_000)
    holdout_net = holdout_edge - (cost_bps / 10_000)
    if latest_net > 0 and holdout_net > 0:
        return "EXECUTION_SURVIVED" if capacity_ok else "CAPACITY_LIMITED"
    if delay > 0 and delay_zero_cost_row.get(cost_bps, False):
        return "LATENCY_SENSITIVE"
    if latest_edge > 0 and holdout_edge > 0:
        return "FILTER_ONLY"
    return "REJECTED"


def build_delay_cost_rows(
    metrics: dict[tuple[str, int], dict[str, Any]],
    capacity_ok: bool,
) -> list[dict[str, Any]]:
    delay_zero_pass: dict[float, bool] = {}
    latest_zero = metrics[("LATEST_90D", 0)]
    holdout_zero = metrics[("HOLDOUT_90D", 0)]
    latest_zero_edge = float_or_none(latest_zero.get("gross_edge_observed_direction")) or 0.0
    holdout_zero_edge = float_or_none(holdout_zero.get("gross_edge_observed_direction")) or 0.0
    for cost_bps in COST_GRID_BPS:
        delay_zero_pass[cost_bps] = latest_zero_edge - cost_bps / 10_000 > 0 and holdout_zero_edge - cost_bps / 10_000 > 0

    rows: list[dict[str, Any]] = []
    for delay in DELAY_SECONDS:
        latest = metrics[("LATEST_90D", delay)]
        holdout = metrics[("HOLDOUT_90D", delay)]
        latest_edge = float_or_none(latest.get("gross_edge_observed_direction"))
        holdout_edge = float_or_none(holdout.get("gross_edge_observed_direction"))
        consistency = (
            "CONSISTENT_POSITIVE"
            if latest_edge is not None and latest_edge > 0 and holdout_edge is not None and holdout_edge > 0
            else "NOT_POSITIVE_IN_BOTH_WINDOWS"
        )
        for cost_bps in COST_GRID_BPS:
            latest_net = latest_edge - cost_bps / 10_000 if latest_edge is not None else None
            holdout_net = holdout_edge - cost_bps / 10_000 if holdout_edge is not None else None
            rows.append(
                {
                    "candidate": candidate_label(),
                    "horizon_seconds": LOCKED_HORIZON_SECONDS,
                    "cooldown_seconds": LOCKED_COOLDOWN_SECONDS,
                    "delay_seconds": delay,
                    "cost_bps": cost_bps,
                    "latest_event_count": latest.get("event_count", 0),
                    "holdout_event_count": holdout.get("event_count", 0),
                    "latest_gross_mean_forward_price_return": latest.get("gross_mean_forward_price_return", ""),
                    "holdout_gross_mean_forward_price_return": holdout.get("gross_mean_forward_price_return", ""),
                    "latest_gross_median_forward_price_return": latest.get("gross_median_forward_price_return", ""),
                    "holdout_gross_median_forward_price_return": holdout.get("gross_median_forward_price_return", ""),
                    "latest_gross_effect_vs_null_signed": latest.get("gross_effect_vs_null_signed", ""),
                    "holdout_gross_effect_vs_null_signed": holdout.get("gross_effect_vs_null_signed", ""),
                    "latest_gross_edge_observed_direction": latest.get("gross_edge_observed_direction", ""),
                    "holdout_gross_edge_observed_direction": holdout.get("gross_edge_observed_direction", ""),
                    "latest_net_effect_after_cost": rounded(latest_net),
                    "holdout_net_effect_after_cost": rounded(holdout_net),
                    "latest_net_effect_after_cost_bps": rounded(latest_net * 10_000 if latest_net is not None else None, 6),
                    "holdout_net_effect_after_cost_bps": rounded(holdout_net * 10_000 if holdout_net is not None else None, 6),
                    "latest_break_even_cost_bps": latest.get("break_even_cost_bps", ""),
                    "holdout_break_even_cost_bps": holdout.get("break_even_cost_bps", ""),
                    "min_latest_holdout_break_even_cost_bps": rounded(
                        min(
                            float_or_none(latest.get("break_even_cost_bps")) or 0.0,
                            float_or_none(holdout.get("break_even_cost_bps")) or 0.0,
                        ),
                        6,
                    ),
                    "latest_symbol_stability_rate": latest.get("symbol_stability_rate", ""),
                    "holdout_symbol_stability_rate": holdout.get("symbol_stability_rate", ""),
                    "latest_week_stability_rate": latest.get("week_stability_rate", ""),
                    "holdout_week_stability_rate": holdout.get("week_stability_rate", ""),
                    "latest_month_stability_rate": latest.get("month_stability_rate", ""),
                    "holdout_month_stability_rate": holdout.get("month_stability_rate", ""),
                    "latest_vs_holdout_consistency": consistency,
                    "classification": classify_delay_cost(delay, cost_bps, latest, holdout, delay_zero_pass, capacity_ok),
                }
            )
    return rows


def max_survived_cost_by_delay(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for delay in DELAY_SECONDS:
        survived = [
            float(row["cost_bps"])
            for row in rows
            if int_value(row.get("delay_seconds")) == delay and row.get("classification") == "EXECUTION_SURVIVED"
        ]
        result[str(delay)] = max(survived) if survived else ""
    return result


def strongest_viable(rows: list[dict[str, Any]]) -> dict[str, Any]:
    survived = [row for row in rows if row.get("classification") == "EXECUTION_SURVIVED"]
    if not survived:
        return {}
    return max(
        survived,
        key=lambda row: (
            float(row.get("cost_bps", 0.0)),
            int_value(row.get("delay_seconds")),
            float_or_none(row.get("min_latest_holdout_break_even_cost_bps")) or 0.0,
        ),
    )


def final_assessment(rows: list[dict[str, Any]], capacity_ok: bool) -> str:
    if not rows:
        return "REJECTED"
    if not capacity_ok:
        return "CAPACITY_LIMITED"
    survived = [row for row in rows if row.get("classification") == "EXECUTION_SURVIVED"]
    if not survived:
        latency_rows = [row for row in rows if row.get("classification") == "LATENCY_SENSITIVE"]
        return "LATENCY_SENSITIVE" if latency_rows else "REJECTED"
    max_delay_at_3bps = max(
        (int_value(row.get("delay_seconds")) for row in survived if float(row.get("cost_bps", 0.0)) >= 3.0),
        default=-1,
    )
    if max_delay_at_3bps >= 10:
        return "STANDALONE_VIABLE"
    return "LATENCY_SENSITIVE"


def cost_grid_fieldnames() -> list[str]:
    return [
        "candidate",
        "horizon_seconds",
        "cooldown_seconds",
        "delay_seconds",
        "cost_bps",
        "latest_event_count",
        "holdout_event_count",
        "latest_gross_mean_forward_price_return",
        "holdout_gross_mean_forward_price_return",
        "latest_gross_median_forward_price_return",
        "holdout_gross_median_forward_price_return",
        "latest_gross_effect_vs_null_signed",
        "holdout_gross_effect_vs_null_signed",
        "latest_gross_edge_observed_direction",
        "holdout_gross_edge_observed_direction",
        "latest_net_effect_after_cost",
        "holdout_net_effect_after_cost",
        "latest_net_effect_after_cost_bps",
        "holdout_net_effect_after_cost_bps",
        "latest_break_even_cost_bps",
        "holdout_break_even_cost_bps",
        "min_latest_holdout_break_even_cost_bps",
        "latest_symbol_stability_rate",
        "holdout_symbol_stability_rate",
        "latest_week_stability_rate",
        "holdout_week_stability_rate",
        "latest_month_stability_rate",
        "holdout_month_stability_rate",
        "latest_vs_holdout_consistency",
        "classification",
    ]


def capacity_fieldnames() -> list[str]:
    return [
        "window",
        "symbol",
        "kept_event_count",
        "median_aggtrades_notional_around_event",
        "p25_aggtrades_notional_around_event",
        "p50_aggtrades_notional_around_event",
        "p75_aggtrades_notional_around_event",
        "p90_aggtrades_notional_around_event",
        "estimated_safe_notional_conservative",
        "estimated_safe_notional_moderate",
        "estimated_safe_notional_upper_diagnostic",
        "symbol_liquidity_tier",
        "max_events_per_day",
        "mean_events_per_active_day",
        "busiest_event_hour_utc",
        "busiest_event_hour_count",
        "busiest_hour_event_share",
        "window_trade_notional_total",
        "turnover_pressure_proxy",
    ]


def stability_fieldnames() -> list[str]:
    return [
        "window",
        "delay_seconds",
        "period_type",
        "period_value",
        "event_count",
        "mean_forward_price_return",
        "std_forward_price_return",
        "directional_diagnostic_rate",
        "consistent_with_window_effect",
    ]


def null_fieldnames() -> list[str]:
    return [
        "window",
        "delay_seconds",
        "candidate_event_count",
        "candidate_mean_forward_price_return",
        "null_event_count",
        "null_mean_forward_price_return",
        "null_std_forward_price_return",
        "gross_effect_vs_null_signed",
        "gross_edge_observed_direction",
        "break_even_cost_bps",
    ]


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def null_rows(metrics: dict[tuple[str, int], dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for window in ["LATEST_90D", "HOLDOUT_90D"]:
        for delay in DELAY_SECONDS:
            metric = metrics[(window, delay)]
            rows.append(
                {
                    "window": window,
                    "delay_seconds": delay,
                    "candidate_event_count": metric.get("event_count", 0),
                    "candidate_mean_forward_price_return": metric.get("gross_mean_forward_price_return", ""),
                    "null_event_count": metric.get("null_event_count", 0),
                    "null_mean_forward_price_return": metric.get("null_mean_forward_price_return", ""),
                    "null_std_forward_price_return": metric.get("null_std_forward_price_return", ""),
                    "gross_effect_vs_null_signed": metric.get("gross_effect_vs_null_signed", ""),
                    "gross_edge_observed_direction": metric.get("gross_edge_observed_direction", ""),
                    "break_even_cost_bps": metric.get("break_even_cost_bps", ""),
                }
            )
    return rows


def output_sizes() -> dict[str, int]:
    paths = [SUMMARY_JSON, SUMMARY_MD, DELAY_COST_GRID_CSV, CAPACITY_CSV, STABILITY_CSV, NULL_COMPARISON_CSV]
    return {path.name: path.stat().st_size for path in paths if path.exists()}


def write_summary_md(summary: dict[str, Any]) -> None:
    strongest = summary.get("strongest_viable_delay_cost", {})
    lines = [
        "# Sell pressure absorbed execution delay capacity diagnostic v1",
        "",
        f"status: {summary['status']}",
        f"assessment: {summary['assessment']}",
        f"runtime_seconds: {summary['runtime_seconds']}",
        f"symbol_days_processed_total: {summary['symbol_days_processed_total']}",
        f"kept_event_count_total: {summary['kept_event_count_total']}",
        f"strongest_viable_delay_cost: delay={strongest.get('delay_seconds', '')}s cost={strongest.get('cost_bps', '')}bps",
        f"capacity_ok: {str(summary['capacity_ok']).lower()}",
        "",
        "## Break-Even By Delay",
        "| delay_seconds | max_cost_bps_survived | latest_break_even_bps | holdout_break_even_bps |",
        "| ---: | ---: | ---: | ---: |",
    ]
    for delay in DELAY_SECONDS:
        detail = summary["break_even_by_delay"][str(delay)]
        lines.append(
            f"| {delay} | {detail.get('max_cost_bps_survived', '')} | "
            f"{detail.get('latest_break_even_cost_bps', '')} | {detail.get('holdout_break_even_cost_bps', '')} |"
        )
    lines.extend(
        [
            "",
            "This is research diagnostics only. No downloads, full parquet dataset, row-level dataset, live trading, paper trading, orders, private endpoint use, recommendations, PnL curve, entries, exits, stops, or targets are created.",
        ]
    )
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_diagnostic() -> dict[str, Any]:
    started = time.monotonic()
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    if base.path_is_inside(base.DEFAULT_BOOKDEPTH_RAW_ROOT, REPO_ROOT) or base.path_is_inside(
        base.DEFAULT_AGGTRADES_RAW_ROOT,
        REPO_ROOT,
    ):
        raise RuntimeError("raw ZIP roots must stay outside repo")

    candidate_stats: dict[tuple[str, int], base.DistributionStats] = {}
    null_stats: dict[tuple[str, int], base.MomentStats] = defaultdict(base.MomentStats)
    stability_stats: dict[tuple[str, int, str, str], base.MomentStats] = defaultdict(base.MomentStats)
    capacity_stats: dict[tuple[str, str], base.DistributionStats] = {}
    capacity_daily_counts: Counter[tuple[str, str, str]] = Counter()
    capacity_hour_counts: Counter[tuple[str, str, int]] = Counter()
    total_trade_notional: Counter[tuple[str, str]] = Counter()
    window_summaries: list[dict[str, Any]] = []
    window_selection: dict[str, Any] = {}

    for window_config in WINDOWS:
        window = str(window_config["window"])
        pairs, metadata = build_window_pairs(int(window_config["days_to_skip"]), window)
        window_selection[window] = metadata
        window_summaries.append(
            process_window(
                window,
                pairs,
                candidate_stats,
                null_stats,
                stability_stats,
                capacity_stats,
                capacity_daily_counts,
                capacity_hour_counts,
                total_trade_notional,
            )
        )

    metrics = build_delay_window_metrics(candidate_stats, null_stats, stability_stats)
    cap_rows = capacity_rows(capacity_stats, capacity_daily_counts, capacity_hour_counts, total_trade_notional)
    cap_summary = capacity_summary(cap_rows)
    capacity_ok = (
        cap_summary["by_window"].get("LATEST_90D", {}).get("symbol_count") == EXPECTED_SYMBOL_COUNT
        and cap_summary["by_window"].get("HOLDOUT_90D", {}).get("symbol_count") == EXPECTED_SYMBOL_COUNT
        and cap_summary["tier_counts"].get("THIN", 0) <= (EXPECTED_SYMBOL_COUNT * 2 - MIN_CAPACITY_SYMBOLS)
    )
    delay_cost_rows = build_delay_cost_rows(metrics, capacity_ok)
    stability_rows = stability_detail_rows(candidate_stats, stability_stats)
    null_detail_rows = null_rows(metrics)
    write_csv(DELAY_COST_GRID_CSV, cost_grid_fieldnames(), delay_cost_rows)
    write_csv(CAPACITY_CSV, capacity_fieldnames(), cap_rows)
    write_csv(STABILITY_CSV, stability_fieldnames(), stability_rows)
    write_csv(NULL_COMPARISON_CSV, null_fieldnames(), null_detail_rows)

    max_costs = max_survived_cost_by_delay(delay_cost_rows)
    strongest = strongest_viable(delay_cost_rows)
    assessment = final_assessment(delay_cost_rows, capacity_ok)
    total_processed = sum(int_value(item["processed_symbol_days"]) for item in window_summaries)
    total_failed = sum(int_value(item["failed_symbol_days"]) for item in window_summaries)
    total_feature_rows = sum(int_value(item["total_feature_rows"]) for item in window_summaries)
    total_kept = sum(int_value(item["kept_event_count"]) for item in window_summaries)
    selected_symbol_counts = {
        window: len(metadata.get("window_details", {}))
        for window, metadata in window_selection.items()
    }
    break_even_by_delay = {
        str(delay): {
            "max_cost_bps_survived": max_costs.get(str(delay), ""),
            "latest_break_even_cost_bps": metrics[("LATEST_90D", delay)].get("break_even_cost_bps", ""),
            "holdout_break_even_cost_bps": metrics[("HOLDOUT_90D", delay)].get("break_even_cost_bps", ""),
            "latest_event_count": metrics[("LATEST_90D", delay)].get("event_count", 0),
            "holdout_event_count": metrics[("HOLDOUT_90D", delay)].get("event_count", 0),
        }
        for delay in DELAY_SECONDS
    }
    status = (
        "PASS_ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_EXECUTION_DELAY_CAPACITY_DIAGNOSTIC"
        if total_processed == EXPECTED_SYMBOL_DAYS_TOTAL
        and total_failed == 0
        and all(count == EXPECTED_SYMBOL_COUNT for count in selected_symbol_counts.values())
        else "PARTIAL_ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_EXECUTION_DELAY_CAPACITY_DIAGNOSTIC"
    )
    summary: dict[str, Any] = {
        "status": status,
        "assessment": assessment,
        "created_at_utc": utc_now_text(),
        "task": "ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_EXECUTION_DELAY_CAPACITY_DIAGNOSTIC_V1",
        "mode": "LATEST_90D_AND_HOLDOUT_90D_ONLY",
        "candidate": candidate_label(),
        "locked_category": LOCKED_CATEGORY,
        "locked_horizon_seconds": LOCKED_HORIZON_SECONDS,
        "locked_cooldown_seconds": LOCKED_COOLDOWN_SECONDS,
        "observed_direction": observed_direction_text(),
        "delay_seconds": DELAY_SECONDS,
        "cost_grid_bps": COST_GRID_BPS,
        "capacity_window_seconds": CAPACITY_WINDOW_RADIUS_MS * 2 / 1000,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "symbol_days_processed_total": total_processed,
        "failed_symbol_days_total": total_failed,
        "feature_rows_seen_total": total_feature_rows,
        "kept_event_count_total": total_kept,
        "window_summaries": window_summaries,
        "break_even_by_delay": break_even_by_delay,
        "delay_cost_grid_row_count": len(delay_cost_rows),
        "classification_counts": dict(Counter(str(row["classification"]) for row in delay_cost_rows)),
        "strongest_viable_delay_cost": strongest,
        "capacity_ok": capacity_ok,
        "capacity_summary": cap_summary,
        "raw_roots_outside_repo": True,
        "downloads_run": False,
        "full_history_run": False,
        "full_parquet_dataset_created": False,
        "row_level_dataset_created": False,
        "new_filters_added": False,
        "thresholds_optimized": False,
        "orders_created": False,
        "private_endpoints_used": False,
        "outputs": {
            "summary_json": str(SUMMARY_JSON),
            "summary_md": str(SUMMARY_MD),
            "delay_cost_grid_csv": str(DELAY_COST_GRID_CSV),
            "capacity_csv": str(CAPACITY_CSV),
            "stability_csv": str(STABILITY_CSV),
            "null_comparison_csv": str(NULL_COMPARISON_CSV),
        },
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_summary_md(summary)
    summary["output_sizes_bytes"] = output_sizes()
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    try:
        summary = run_diagnostic()
    except Exception as exc:  # noqa: BLE001
        error_summary = {
            "status": "FAILED_ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_EXECUTION_DELAY_CAPACITY_DIAGNOSTIC",
            "created_at_utc": utc_now_text(),
            "error": f"{type(exc).__name__}: {exc}",
            "downloads_run": False,
            "full_history_run": False,
            "row_level_dataset_created": False,
        }
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        SUMMARY_JSON.write_text(json.dumps(error_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        SUMMARY_MD.write_text(
            "# Sell pressure absorbed execution delay capacity diagnostic v1\n\n"
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
