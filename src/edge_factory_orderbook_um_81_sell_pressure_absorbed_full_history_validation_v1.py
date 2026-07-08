#!/usr/bin/env python
"""Full-history validation for locked SELL_PRESSURE_ABSORBED@300s with 600s cooldown."""

from __future__ import annotations

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

SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_81_sell_pressure_absorbed_full_history_validation_summary.json"
SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_81_sell_pressure_absorbed_full_history_validation_summary.md"
PERIOD_STABILITY_CSV = OUTPUTS_DIR / "orderbook_um_81_sell_pressure_absorbed_full_history_validation_period_stability.csv"
SYMBOL_STABILITY_CSV = OUTPUTS_DIR / "orderbook_um_81_sell_pressure_absorbed_full_history_validation_symbol_stability.csv"
COST_GRID_CSV = OUTPUTS_DIR / "orderbook_um_81_sell_pressure_absorbed_full_history_validation_cost_grid.csv"
NULL_COMPARISON_CSV = OUTPUTS_DIR / "orderbook_um_81_sell_pressure_absorbed_full_history_validation_null_comparison.csv"

LOCKED_CATEGORY = "SELL_PRESSURE_ABSORBED"
LOCKED_HORIZON_SECONDS = 300
LOCKED_COOLDOWN_SECONDS = 600
OBSERVED_PRICE_DIRECTION = -1
COST_GRID_BPS = [0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0]
EXPECTED_SYMBOL_COUNT = 81
EXPECTED_SYMBOL_DAYS = 99_404
LATEST_WINDOW_DAYS = 90
HOLDOUT_WINDOW_DAYS = 90
MIN_EVENT_COUNT = 100
MIN_PERIOD_EVENT_COUNT = 50
MIN_SYMBOL_EVENT_COUNT = 100
MIN_STABILITY_RATE = 0.5
PROGRESS_INTERVAL_SECONDS = 30
RESERVOIR_LIMIT = 50_000
START_DATE = "2023-01-01"
END_DATE = "2026-06-15"


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def int_value(value: Any, default: int = 0) -> int:
    return base.int_value(value, default)


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


def quarter_text(file_date: str) -> str:
    year = file_date[:4]
    month = int_value(file_date[5:7], 1)
    quarter = ((month - 1) // 3) + 1
    return f"{year}-Q{quarter}"


def observed_direction_text() -> str:
    return "NEGATIVE_PRICE_EFFECT" if OBSERVED_PRICE_DIRECTION < 0 else "POSITIVE_PRICE_EFFECT"


def fresh_distribution(seed_text: str) -> base.DistributionStats:
    return base.DistributionStats(sample_limit=RESERVOIR_LIMIT, seed_text=seed_text)


def may_keep_event(last_kept_ms: int | None, event_ms: int) -> bool:
    if last_kept_ms is None:
        return True
    return event_ms - last_kept_ms >= LOCKED_COOLDOWN_SECONDS * 1000


def load_full_history_pairs() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    book_rows = base.load_verified_paths(base.BOOKDEPTH_FILE_STATUS_CSV, base.DEFAULT_BOOKDEPTH_RAW_ROOT)
    agg_rows = base.load_verified_paths(base.AGGTRADES_FILE_STATUS_CSV, base.DEFAULT_AGGTRADES_RAW_ROOT)
    by_symbol: dict[str, list[str]] = defaultdict(list)
    for symbol, file_date in sorted(set(book_rows) & set(agg_rows)):
        if START_DATE <= file_date <= END_DATE:
            by_symbol[symbol].append(file_date)

    pairs: list[dict[str, Any]] = []
    symbol_details: dict[str, Any] = {}
    for symbol in sorted(by_symbol):
        ascending_dates = sorted(by_symbol[symbol])
        descending_dates = list(reversed(ascending_dates))
        latest_set = set(descending_dates[:LATEST_WINDOW_DAYS])
        holdout_set = set(descending_dates[LATEST_WINDOW_DAYS : LATEST_WINDOW_DAYS + HOLDOUT_WINDOW_DAYS])
        symbol_details[symbol] = {
            "days_available": len(ascending_dates),
            "oldest": ascending_dates[0] if ascending_dates else "",
            "newest": ascending_dates[-1] if ascending_dates else "",
        }
        for file_date in ascending_dates:
            if file_date in latest_set:
                validation_window = "LATEST_90D"
            elif file_date in holdout_set:
                validation_window = "HOLDOUT_90D"
            else:
                validation_window = "OLDER_HISTORY"
            key = (symbol, file_date)
            pairs.append(
                {
                    "symbol": symbol,
                    "file_date": file_date,
                    "year": file_date[:4],
                    "year_month": file_date[:7],
                    "quarter": quarter_text(file_date),
                    "week": base.iso_week_text(file_date),
                    "validation_window": validation_window,
                    "bookdepth_zip_path": book_rows[key]["local_zip_path"],
                    "aggtrades_zip_path": agg_rows[key]["local_zip_path"],
                }
            )
    return pairs, {"symbol_details": symbol_details}


def add_candidate_value(
    price_return: float,
    pair: dict[str, Any],
    full_stats: base.DistributionStats,
    window_stats: dict[str, base.DistributionStats],
    period_stats: dict[tuple[str, str], base.MomentStats],
    symbol_stats: dict[str, base.MomentStats],
) -> None:
    full_stats.add_diagnostic(price_return, OBSERVED_PRICE_DIRECTION, "UNUSED", None, None, None)
    window = str(pair["validation_window"])
    if window not in window_stats:
        window_stats[window] = fresh_distribution(f"candidate-window:{window}")
    window_stats[window].add_diagnostic(price_return, OBSERVED_PRICE_DIRECTION, "UNUSED", None, None, None)
    symbol_stats[str(pair["symbol"])].add(price_return, OBSERVED_PRICE_DIRECTION)
    for period_type, period_value in [
        ("YEAR", str(pair["year"])),
        ("QUARTER", str(pair["quarter"])),
        ("MONTH", str(pair["year_month"])),
        ("WEEK", str(pair["week"])),
        ("WINDOW", window),
    ]:
        period_stats[(period_type, period_value)].add(price_return, OBSERVED_PRICE_DIRECTION)


def add_null_value(
    price_return: float,
    pair: dict[str, Any],
    full_stats: base.MomentStats,
    window_stats: dict[str, base.MomentStats],
    period_stats: dict[tuple[str, str], base.MomentStats],
    symbol_stats: dict[str, base.MomentStats],
) -> None:
    full_stats.add(price_return, OBSERVED_PRICE_DIRECTION)
    window = str(pair["validation_window"])
    window_stats[window].add(price_return, OBSERVED_PRICE_DIRECTION)
    symbol_stats[str(pair["symbol"])].add(price_return, OBSERVED_PRICE_DIRECTION)
    for period_type, period_value in [
        ("YEAR", str(pair["year"])),
        ("QUARTER", str(pair["quarter"])),
        ("MONTH", str(pair["year_month"])),
        ("WEEK", str(pair["week"])),
        ("WINDOW", window),
    ]:
        period_stats[(period_type, period_value)].add(price_return, OBSERVED_PRICE_DIRECTION)


def process_full_history(pairs: list[dict[str, Any]]) -> dict[str, Any]:
    started = time.monotonic()
    processed_symbol_days = 0
    failed_symbol_days = 0
    total_feature_rows = 0
    original_candidate_row_count = 0
    original_event_count = 0
    null_original_event_count = 0
    category_counts: Counter[str] = Counter()
    failure_examples: list[dict[str, str]] = []
    last_candidate_kept_ms: dict[str, int] = {}
    last_null_kept_ms: dict[str, int] = {}
    candidate_full_stats = fresh_distribution("sell-pressure-full-history")
    candidate_window_stats: dict[str, base.DistributionStats] = {}
    candidate_period_stats: dict[tuple[str, str], base.MomentStats] = defaultdict(base.MomentStats)
    candidate_symbol_stats: dict[str, base.MomentStats] = defaultdict(base.MomentStats)
    null_full_stats = base.MomentStats()
    null_window_stats: dict[str, base.MomentStats] = defaultdict(base.MomentStats)
    null_period_stats: dict[tuple[str, str], base.MomentStats] = defaultdict(base.MomentStats)
    null_symbol_stats: dict[str, base.MomentStats] = defaultdict(base.MomentStats)
    next_progress = time.monotonic() + PROGRESS_INTERVAL_SECONDS

    for pair in pairs:
        try:
            timestamps, rows, trade_times, trade_prices = price_linkage.read_features_and_trade_prices(pair)
            processed_symbol_days += 1
            total_feature_rows += len(rows)
            symbol = str(pair["symbol"])
            for index, row in enumerate(rows):
                category = str(row.get("absorption_category") or "INSUFFICIENT_DATA")
                if category not in base.CATEGORIES:
                    category = "INSUFFICIENT_DATA"
                category_counts[category] += 1
                event_ms = timestamps[index]
                price_return = price_linkage.forward_price_return(
                    event_ms,
                    LOCKED_HORIZON_SECONDS,
                    trade_times,
                    trade_prices,
                )
                if price_return is not None:
                    null_original_event_count += 1
                    if may_keep_event(last_null_kept_ms.get(symbol), event_ms):
                        last_null_kept_ms[symbol] = event_ms
                        add_null_value(
                            price_return,
                            pair,
                            null_full_stats,
                            null_window_stats,
                            null_period_stats,
                            null_symbol_stats,
                        )
                if category != LOCKED_CATEGORY:
                    continue
                original_candidate_row_count += 1
                if price_return is None:
                    continue
                original_event_count += 1
                if not may_keep_event(last_candidate_kept_ms.get(symbol), event_ms):
                    continue
                last_candidate_kept_ms[symbol] = event_ms
                add_candidate_value(
                    price_return,
                    pair,
                    candidate_full_stats,
                    candidate_window_stats,
                    candidate_period_stats,
                    candidate_symbol_stats,
                )
        except Exception as exc:  # noqa: BLE001
            failed_symbol_days += 1
            if len(failure_examples) < 30:
                failure_examples.append(
                    {
                        "symbol": str(pair.get("symbol", "")),
                        "file_date": str(pair.get("file_date", "")),
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
        if time.monotonic() >= next_progress:
            print(
                "progress phase=sell_pressure_full_history "
                f"processed_symbol_days={processed_symbol_days}/{len(pairs)} "
                f"failed_symbol_days={failed_symbol_days} feature_rows={total_feature_rows} "
                f"kept_events={candidate_full_stats.valid_forward_count} "
                f"elapsed_seconds={round(time.monotonic() - started, 1)}",
                flush=True,
            )
            next_progress = time.monotonic() + PROGRESS_INTERVAL_SECONDS

    return {
        "processed_symbol_days": processed_symbol_days,
        "failed_symbol_days": failed_symbol_days,
        "total_feature_rows": total_feature_rows,
        "original_candidate_row_count": original_candidate_row_count,
        "original_event_count": original_event_count,
        "null_original_event_count": null_original_event_count,
        "category_counts": dict(category_counts),
        "failure_examples": failure_examples,
        "candidate_full_stats": candidate_full_stats,
        "candidate_window_stats": candidate_window_stats,
        "candidate_period_stats": candidate_period_stats,
        "candidate_symbol_stats": candidate_symbol_stats,
        "null_full_stats": null_full_stats,
        "null_window_stats": null_window_stats,
        "null_period_stats": null_period_stats,
        "null_symbol_stats": null_symbol_stats,
    }


def metric_row(
    scope_type: str,
    scope_value: str,
    candidate_stats: base.MomentStats,
    null_stats: base.MomentStats,
    original_event_count: int | None = None,
    original_row_count: int | None = None,
) -> dict[str, Any]:
    candidate_mean = candidate_stats.mean()
    null_mean = null_stats.mean()
    effect = candidate_mean - null_mean if candidate_mean is not None and null_mean is not None else None
    gross_edge = effect * OBSERVED_PRICE_DIRECTION if effect is not None else None
    break_even = max(0.0, gross_edge * 10_000) if gross_edge is not None else None
    median_value = (
        candidate_stats.sampled_median()
        if isinstance(candidate_stats, base.DistributionStats)
        else None
    )
    return {
        "scope_type": scope_type,
        "scope_value": scope_value,
        "candidate": candidate_label(),
        "category": LOCKED_CATEGORY,
        "horizon_seconds": LOCKED_HORIZON_SECONDS,
        "cooldown_seconds": LOCKED_COOLDOWN_SECONDS,
        "observed_direction": observed_direction_text(),
        "original_candidate_row_count": "" if original_row_count is None else original_row_count,
        "original_event_count": "" if original_event_count is None else original_event_count,
        "kept_event_count": candidate_stats.valid_forward_count,
        "retention_rate": rounded(safe_div(candidate_stats.valid_forward_count, original_event_count), 6)
        if original_event_count is not None
        else "",
        "gross_mean_forward_price_return": rounded(candidate_mean),
        "gross_median_forward_price_return": rounded(median_value),
        "gross_std_forward_price_return": rounded(candidate_stats.std()),
        "null_event_count": null_stats.valid_forward_count,
        "null_mean_forward_price_return": rounded(null_mean),
        "null_std_forward_price_return": rounded(null_stats.std()),
        "gross_effect_vs_null_signed": rounded(effect),
        "gross_edge_observed_direction": rounded(gross_edge),
        "break_even_cost_bps": rounded(break_even, 6),
        "directional_diagnostic_rate": rounded(candidate_stats.directional_rate(), 6),
        "consistent_with_observed_direction": str(sign_of(effect) == OBSERVED_PRICE_DIRECTION).lower(),
    }


def build_window_rows(processed: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        metric_row(
            "FULL_HISTORY",
            "2023-01-01_TO_2026-06-15",
            processed["candidate_full_stats"],
            processed["null_full_stats"],
            processed["original_event_count"],
            processed["original_candidate_row_count"],
        )
    ]
    for window in ["LATEST_90D", "HOLDOUT_90D", "OLDER_HISTORY"]:
        rows.append(
            metric_row(
                "WINDOW",
                window,
                processed["candidate_window_stats"].get(window, fresh_distribution(f"empty:{window}")),
                processed["null_window_stats"][window],
            )
        )
    return rows


def build_period_rows(processed: dict[str, Any], full_effect_sign: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    candidate_period_stats: dict[tuple[str, str], base.MomentStats] = processed["candidate_period_stats"]
    null_period_stats: dict[tuple[str, str], base.MomentStats] = processed["null_period_stats"]
    for period_key in sorted(candidate_period_stats):
        period_type, period_value = period_key
        row = metric_row(period_type, period_value, candidate_period_stats[period_key], null_period_stats[period_key])
        effect = price_linkage.float_or_none(row["gross_effect_vs_null_signed"])
        gross_edge = price_linkage.float_or_none(row["gross_edge_observed_direction"])
        row["consistent_with_full_history_effect"] = str(sign_of(effect) == full_effect_sign).lower()
        row["regime_edge_bps"] = rounded(gross_edge * 10_000 if gross_edge is not None else None, 6)
        rows.append(row)
    return rows


def build_symbol_rows(processed: dict[str, Any], full_effect_sign: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    candidate_symbol_stats: dict[str, base.MomentStats] = processed["candidate_symbol_stats"]
    null_symbol_stats: dict[str, base.MomentStats] = processed["null_symbol_stats"]
    for symbol in sorted(candidate_symbol_stats):
        row = metric_row("SYMBOL", symbol, candidate_symbol_stats[symbol], null_symbol_stats[symbol])
        effect = price_linkage.float_or_none(row["gross_effect_vs_null_signed"])
        gross_edge = price_linkage.float_or_none(row["gross_edge_observed_direction"])
        row["symbol"] = symbol
        row["consistent_with_full_history_effect"] = str(sign_of(effect) == full_effect_sign).lower()
        row["symbol_edge_bps"] = rounded(gross_edge * 10_000 if gross_edge is not None else None, 6)
        rows.append(row)
    return rows


def stability_summary(rows: list[dict[str, Any]], period_type: str, min_count: int) -> dict[str, Any]:
    support = 0
    consistent = 0
    for row in rows:
        if str(row.get("scope_type")) != period_type:
            continue
        if int_value(row.get("kept_event_count")) < min_count:
            continue
        support += 1
        if str(row.get("consistent_with_full_history_effect", "")).lower() == "true":
            consistent += 1
    return {
        "period_type": period_type,
        "support_count": support,
        "consistent_count": consistent,
        "stability_rate": rounded(safe_div(consistent, support), 6),
    }


def worst_period(rows: list[dict[str, Any]], period_type: str) -> dict[str, Any]:
    candidates = [
        row for row in rows
        if str(row.get("scope_type")) == period_type
        and int_value(row.get("kept_event_count")) >= MIN_PERIOD_EVENT_COUNT
        and price_linkage.float_or_none(row.get("gross_edge_observed_direction")) is not None
    ]
    if not candidates:
        return {}
    return min(candidates, key=lambda row: price_linkage.float_or_none(row.get("gross_edge_observed_direction")) or 0.0)


def build_cost_rows(scope_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scope_row in scope_rows:
        gross_edge = price_linkage.float_or_none(scope_row.get("gross_edge_observed_direction"))
        for cost_bps in COST_GRID_BPS:
            cost_return = cost_bps / 10_000
            net_effect = gross_edge - cost_return if gross_edge is not None else None
            rows.append(
                {
                    "scope_type": scope_row["scope_type"],
                    "scope_value": scope_row["scope_value"],
                    "candidate": candidate_label(),
                    "horizon_seconds": LOCKED_HORIZON_SECONDS,
                    "cooldown_seconds": LOCKED_COOLDOWN_SECONDS,
                    "cost_bps": cost_bps,
                    "kept_event_count": scope_row["kept_event_count"],
                    "gross_mean_forward_price_return": scope_row["gross_mean_forward_price_return"],
                    "gross_median_forward_price_return": scope_row["gross_median_forward_price_return"],
                    "gross_effect_vs_null_signed": scope_row["gross_effect_vs_null_signed"],
                    "gross_edge_observed_direction": scope_row["gross_edge_observed_direction"],
                    "net_effect_after_cost": rounded(net_effect),
                    "net_effect_after_cost_bps": rounded(net_effect * 10_000 if net_effect is not None else None, 6),
                    "break_even_cost_bps": scope_row["break_even_cost_bps"],
                    "classification": "SURVIVES_COST" if net_effect is not None and net_effect > 0 else "FILTER_ONLY",
                }
            )
    return rows


def max_cost_survived(cost_rows: list[dict[str, Any]], required_scope_values: set[str]) -> float | None:
    survived: list[float] = []
    for cost in COST_GRID_BPS:
        rows_for_cost = [
            row for row in cost_rows
            if float(row.get("cost_bps", -1)) == cost and str(row.get("scope_value")) in required_scope_values
        ]
        if len(rows_for_cost) != len(required_scope_values):
            continue
        if all(str(row.get("classification")) == "SURVIVES_COST" for row in rows_for_cost):
            survived.append(cost)
    return max(survived) if survived else None


def classify(
    scope_rows: list[dict[str, Any]],
    stability: dict[str, Any],
    max_all_window_cost: float | None,
) -> str:
    by_scope = {str(row["scope_value"]): row for row in scope_rows}
    full = by_scope["2023-01-01_TO_2026-06-15"]
    latest = by_scope["LATEST_90D"]
    holdout = by_scope["HOLDOUT_90D"]
    older = by_scope["OLDER_HISTORY"]
    full_edge = price_linkage.float_or_none(full.get("gross_edge_observed_direction"))
    latest_edge = price_linkage.float_or_none(latest.get("gross_edge_observed_direction"))
    holdout_edge = price_linkage.float_or_none(holdout.get("gross_edge_observed_direction"))
    older_edge = price_linkage.float_or_none(older.get("gross_edge_observed_direction"))
    if full_edge is None or full_edge <= 0 or int_value(full.get("kept_event_count")) < MIN_EVENT_COUNT:
        return "REJECTED"
    stable = all(
        (price_linkage.float_or_none(stability[key]["stability_rate"]) or 0.0) >= MIN_STABILITY_RATE
        for key in ["symbol", "monthly", "quarterly", "yearly", "weekly"]
    )
    all_windows_positive = all(
        value is not None and value > 0
        for value in [latest_edge, holdout_edge, older_edge]
    )
    if all_windows_positive and stable and max_all_window_cost is not None:
        return "FULL_HISTORY_SURVIVED"
    if latest_edge is not None and latest_edge > 0 and holdout_edge is not None and holdout_edge > 0:
        if older_edge is None or older_edge <= 0:
            return "RECENT_ONLY"
    if full_edge > 0:
        return "UNSTABLE"
    return "REJECTED"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def period_fieldnames() -> list[str]:
    return [
        "scope_type",
        "scope_value",
        "candidate",
        "horizon_seconds",
        "cooldown_seconds",
        "observed_direction",
        "kept_event_count",
        "gross_mean_forward_price_return",
        "null_event_count",
        "null_mean_forward_price_return",
        "gross_effect_vs_null_signed",
        "gross_edge_observed_direction",
        "regime_edge_bps",
        "break_even_cost_bps",
        "directional_diagnostic_rate",
        "consistent_with_observed_direction",
        "consistent_with_full_history_effect",
    ]


def symbol_fieldnames() -> list[str]:
    return [
        "symbol",
        "scope_type",
        "scope_value",
        "candidate",
        "horizon_seconds",
        "cooldown_seconds",
        "observed_direction",
        "kept_event_count",
        "gross_mean_forward_price_return",
        "null_event_count",
        "null_mean_forward_price_return",
        "gross_effect_vs_null_signed",
        "gross_edge_observed_direction",
        "symbol_edge_bps",
        "break_even_cost_bps",
        "directional_diagnostic_rate",
        "consistent_with_observed_direction",
        "consistent_with_full_history_effect",
    ]


def cost_fieldnames() -> list[str]:
    return [
        "scope_type",
        "scope_value",
        "candidate",
        "horizon_seconds",
        "cooldown_seconds",
        "cost_bps",
        "kept_event_count",
        "gross_mean_forward_price_return",
        "gross_median_forward_price_return",
        "gross_effect_vs_null_signed",
        "gross_edge_observed_direction",
        "net_effect_after_cost",
        "net_effect_after_cost_bps",
        "break_even_cost_bps",
        "classification",
    ]


def null_fieldnames() -> list[str]:
    return [
        "scope_type",
        "scope_value",
        "candidate",
        "horizon_seconds",
        "cooldown_seconds",
        "kept_event_count",
        "gross_mean_forward_price_return",
        "gross_median_forward_price_return",
        "null_event_count",
        "null_mean_forward_price_return",
        "null_std_forward_price_return",
        "gross_effect_vs_null_signed",
        "gross_edge_observed_direction",
        "break_even_cost_bps",
    ]


def output_sizes() -> dict[str, int]:
    paths = [SUMMARY_JSON, SUMMARY_MD, PERIOD_STABILITY_CSV, SYMBOL_STABILITY_CSV, COST_GRID_CSV, NULL_COMPARISON_CSV]
    return {path.name: path.stat().st_size for path in paths if path.exists()}


def write_summary_md(summary: dict[str, Any]) -> None:
    lines = [
        "# Sell pressure absorbed full-history validation v1",
        "",
        f"status: {summary['status']}",
        f"classification: {summary['classification']}",
        f"runtime_seconds: {summary['runtime_seconds']}",
        f"symbol_days_processed: {summary['symbol_days_processed']}",
        f"kept_non_overlap_event_count: {summary['kept_non_overlap_event_count']}",
        f"break_even_cost_bps: {summary['full_history_metrics'].get('break_even_cost_bps', '')}",
        f"max_cost_bps_survived_full_history: {summary.get('max_cost_bps_survived_full_history', '')}",
        f"max_cost_bps_survived_latest_holdout_older: {summary.get('max_cost_bps_survived_latest_holdout_older', '')}",
        "",
        "## Stability",
        f"symbol_stability_rate: {summary['stability']['symbol']['stability_rate']}",
        f"monthly_stability_rate: {summary['stability']['monthly']['stability_rate']}",
        f"quarterly_stability_rate: {summary['stability']['quarterly']['stability_rate']}",
        f"yearly_stability_rate: {summary['stability']['yearly']['stability_rate']}",
        f"weekly_stability_rate: {summary['stability']['weekly']['stability_rate']}",
        "",
        "This is locked-candidate research validation only. No downloads, row-level dataset, parquet dataset, strategy, backtest, signal, PnL curve, orders, private endpoints, or recommendations are created.",
    ]
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_validation() -> dict[str, Any]:
    started = time.monotonic()
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    if base.path_is_inside(base.DEFAULT_BOOKDEPTH_RAW_ROOT, REPO_ROOT) or base.path_is_inside(
        base.DEFAULT_AGGTRADES_RAW_ROOT,
        REPO_ROOT,
    ):
        raise RuntimeError("raw ZIP roots must stay outside repo")
    pairs, pair_metadata = load_full_history_pairs()
    processed = process_full_history(pairs)
    scope_rows = build_window_rows(processed)
    full_row = scope_rows[0]
    full_effect_sign = sign_of(price_linkage.float_or_none(full_row.get("gross_effect_vs_null_signed")))
    period_rows = build_period_rows(processed, full_effect_sign)
    symbol_rows = build_symbol_rows(processed, full_effect_sign)
    stability = {
        "symbol": stability_summary(symbol_rows, "SYMBOL", MIN_SYMBOL_EVENT_COUNT),
        "monthly": stability_summary(period_rows, "MONTH", MIN_PERIOD_EVENT_COUNT),
        "quarterly": stability_summary(period_rows, "QUARTER", MIN_PERIOD_EVENT_COUNT),
        "yearly": stability_summary(period_rows, "YEAR", MIN_PERIOD_EVENT_COUNT),
        "weekly": stability_summary(period_rows, "WEEK", MIN_PERIOD_EVENT_COUNT),
    }
    cost_rows = build_cost_rows(scope_rows)
    null_rows = scope_rows + [
        row for row in period_rows
        if str(row.get("scope_type")) in {"YEAR", "QUARTER", "MONTH", "WEEK"}
    ]
    max_full_cost = max_cost_survived(cost_rows, {"2023-01-01_TO_2026-06-15"})
    max_all_window_cost = max_cost_survived(cost_rows, {"LATEST_90D", "HOLDOUT_90D", "OLDER_HISTORY"})
    classification = classify(scope_rows, stability, max_all_window_cost)
    worst_quarter = worst_period(period_rows, "QUARTER")
    worst_month = worst_period(period_rows, "MONTH")
    write_csv(PERIOD_STABILITY_CSV, period_fieldnames(), period_rows)
    write_csv(SYMBOL_STABILITY_CSV, symbol_fieldnames(), symbol_rows)
    write_csv(COST_GRID_CSV, cost_fieldnames(), cost_rows)
    write_csv(NULL_COMPARISON_CSV, null_fieldnames(), null_rows)

    status = (
        "PASS_ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_FULL_HISTORY_VALIDATED"
        if processed["processed_symbol_days"] == EXPECTED_SYMBOL_DAYS
        and processed["failed_symbol_days"] == 0
        and len(pair_metadata["symbol_details"]) == EXPECTED_SYMBOL_COUNT
        else "PARTIAL_ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_FULL_HISTORY_VALIDATION"
    )
    summary: dict[str, Any] = {
        "status": status,
        "classification": classification,
        "created_at_utc": utc_now_text(),
        "task": "ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_FULL_HISTORY_VALIDATION_V1",
        "candidate": candidate_label(),
        "locked_category": LOCKED_CATEGORY,
        "locked_horizon_seconds": LOCKED_HORIZON_SECONDS,
        "locked_cooldown_seconds": LOCKED_COOLDOWN_SECONDS,
        "observed_direction": observed_direction_text(),
        "coverage_start": START_DATE,
        "coverage_end": END_DATE,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "symbol_days_expected": EXPECTED_SYMBOL_DAYS,
        "symbol_days_processed": processed["processed_symbol_days"],
        "failed_symbol_days": processed["failed_symbol_days"],
        "feature_rows_seen": processed["total_feature_rows"],
        "original_candidate_row_count": processed["original_candidate_row_count"],
        "original_event_count": processed["original_event_count"],
        "kept_non_overlap_event_count": processed["candidate_full_stats"].valid_forward_count,
        "retention_rate": rounded(
            safe_div(processed["candidate_full_stats"].valid_forward_count, processed["original_event_count"]),
            6,
        ),
        "null_original_event_count": processed["null_original_event_count"],
        "null_kept_event_count": processed["null_full_stats"].valid_forward_count,
        "full_history_metrics": full_row,
        "window_consistency": [row for row in scope_rows if row["scope_type"] == "WINDOW"],
        "latest_90d_vs_holdout_90d_vs_older_history_consistency": {
            row["scope_value"]: {
                "kept_event_count": row["kept_event_count"],
                "gross_effect_vs_null_signed": row["gross_effect_vs_null_signed"],
                "gross_edge_observed_direction": row["gross_edge_observed_direction"],
                "break_even_cost_bps": row["break_even_cost_bps"],
                "consistent_with_observed_direction": row["consistent_with_observed_direction"],
            }
            for row in scope_rows if row["scope_type"] == "WINDOW"
        },
        "stability": stability,
        "regime_drift": {
            "yearly": stability["yearly"],
            "quarterly": stability["quarterly"],
            "monthly": stability["monthly"],
        },
        "worst_quarter": worst_quarter,
        "worst_month": worst_month,
        "max_cost_bps_survived_full_history": "" if max_full_cost is None else max_full_cost,
        "max_cost_bps_survived_latest_holdout_older": "" if max_all_window_cost is None else max_all_window_cost,
        "cost_grid_bps": COST_GRID_BPS,
        "category_counts": processed["category_counts"],
        "failure_examples": processed["failure_examples"],
        "pair_metadata": {
            "symbol_count": len(pair_metadata["symbol_details"]),
            "oldest_date": min((item["oldest"] for item in pair_metadata["symbol_details"].values()), default=""),
            "newest_date": max((item["newest"] for item in pair_metadata["symbol_details"].values()), default=""),
        },
        "row_level_dataset_created": False,
        "parquet_dataset_created": False,
        "downloads_run": False,
        "new_filters_added": False,
        "thresholds_optimized": False,
        "outputs": {
            "summary_json": str(SUMMARY_JSON),
            "summary_md": str(SUMMARY_MD),
            "period_stability_csv": str(PERIOD_STABILITY_CSV),
            "symbol_stability_csv": str(SYMBOL_STABILITY_CSV),
            "cost_grid_csv": str(COST_GRID_CSV),
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
        summary = run_validation()
    except Exception as exc:  # noqa: BLE001
        error_summary = {
            "status": "FAILED_ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_FULL_HISTORY_VALIDATION",
            "created_at_utc": utc_now_text(),
            "error": f"{type(exc).__name__}: {exc}",
            "row_level_dataset_created": False,
            "parquet_dataset_created": False,
            "downloads_run": False,
        }
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        SUMMARY_JSON.write_text(json.dumps(error_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        SUMMARY_MD.write_text(
            "# Sell pressure absorbed full-history validation v1\n\n"
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
