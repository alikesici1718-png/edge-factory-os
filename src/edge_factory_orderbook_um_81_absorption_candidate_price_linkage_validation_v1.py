#!/usr/bin/env python
"""Validate fixed absorption candidates against aggTrades forward price returns."""

from __future__ import annotations

import bisect
import csv
import json
import math
import statistics
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import edge_factory_orderbook_um_81_streaming_absorption_discovery_90d_v1 as base


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"

LATEST_DEPTH_CANDIDATES_CSV = OUTPUTS_DIR / "orderbook_um_81_streaming_absorption_discovery_90d_candidates.csv"
HOLDOUT_DEPTH_COMPARISON_CSV = (
    OUTPUTS_DIR / "orderbook_um_81_streaming_absorption_discovery_holdout_90d_candidate_comparison.csv"
)

SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_81_absorption_candidate_price_linkage_summary.json"
SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_81_absorption_candidate_price_linkage_summary.md"
CANDIDATE_COMPARISON_CSV = OUTPUTS_DIR / "orderbook_um_81_absorption_candidate_price_linkage_candidate_comparison.csv"
SYMBOL_STABILITY_CSV = OUTPUTS_DIR / "orderbook_um_81_absorption_candidate_price_linkage_symbol_stability.csv"
NULL_COMPARISON_CSV = OUTPUTS_DIR / "orderbook_um_81_absorption_candidate_price_linkage_null_comparison.csv"

EXPECTED_SYMBOL_COUNT = 81
WINDOW_DAYS = 90
PROGRESS_INTERVAL_SECONDS = 30
MIN_PRICE_LINKAGE_EVENT_COUNT = 500
RESERVOIR_LIMIT = 50_000

WINDOWS = [
    {"window": "LATEST_90D", "days_to_skip": 0},
    {"window": "HOLDOUT_90D", "days_to_skip": 90},
]
PRICE_LINKAGE_CANDIDATES = [
    ("FLOW_AND_DEPTH_ALIGNED_DOWN", 300),
    ("SELL_PRESSURE_ABSORBED", 300),
    ("FLOW_AND_DEPTH_ALIGNED_DOWN", 60),
    ("FLOW_AND_DEPTH_ALIGNED_DOWN", 30),
    ("FLOW_AND_DEPTH_ALIGNED_DOWN", 10),
]
PRICE_HORIZONS = [10, 30, 60, 300]


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def int_value(value: Any, default: int = 0) -> int:
    return base.int_value(value, default)


def float_value(value: Any, default: float = 0.0) -> float:
    return base.float_value(value, default)


def float_or_none(value: Any) -> float | None:
    try:
        if value in {None, ""}:
            return None
        result = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(result):
        return None
    return result


def rounded(value: float | None, places: int = 10) -> float | str:
    if value is None or math.isnan(value):
        return ""
    return round(value, places)


def safe_div(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def sign_of(value: float | None, tolerance: float = 1e-12) -> int:
    return base.sign_of(value, tolerance)


def sign_text(value: float | None) -> str:
    sign = sign_of(value)
    if sign > 0:
        return "POSITIVE"
    if sign < 0:
        return "NEGATIVE"
    return "ZERO_OR_UNAVAILABLE"


def direction_agreement(price_effect: float | None, depth_effect: float | None) -> str:
    price_sign = sign_of(price_effect)
    depth_sign = sign_of(depth_effect)
    if not price_sign or not depth_sign:
        return "UNAVAILABLE"
    return "AGREES_WITH_DEPTH_PROXY_DIRECTION" if price_sign == depth_sign else "DIVERGES_FROM_DEPTH_PROXY_DIRECTION"


def candidate_label(category: str, horizon: int) -> str:
    return f"{category}@{horizon}s"


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def load_previous_depth_effects() -> dict[tuple[str, int, str], dict[str, str]]:
    latest_rows = read_csv_rows(LATEST_DEPTH_CANDIDATES_CSV)
    holdout_rows = read_csv_rows(HOLDOUT_DEPTH_COMPARISON_CSV)
    effects: dict[tuple[str, int, str], dict[str, str]] = {}
    for row in latest_rows:
        category = str(row.get("category", ""))
        horizon = int_value(row.get("horizon_seconds"))
        if (category, horizon) in PRICE_LINKAGE_CANDIDATES:
            effects[(category, horizon, "LATEST_90D")] = row
    for row in holdout_rows:
        category = str(row.get("category", ""))
        horizon = int_value(row.get("horizon_seconds"))
        if (category, horizon) in PRICE_LINKAGE_CANDIDATES:
            effects[(category, horizon, "HOLDOUT_90D")] = row

    missing: list[str] = []
    for category, horizon in PRICE_LINKAGE_CANDIDATES:
        for window in ["LATEST_90D", "HOLDOUT_90D"]:
            if (category, horizon, window) not in effects:
                missing.append(f"{window}:{candidate_label(category, horizon)}")
    if missing:
        raise ValueError(f"missing previous depth-proxy candidate rows: {', '.join(missing)}")
    return effects


def build_window_pairs(days_to_skip: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    book_rows = base.load_verified_paths(base.BOOKDEPTH_FILE_STATUS_CSV, base.DEFAULT_BOOKDEPTH_RAW_ROOT)
    agg_rows = base.load_verified_paths(base.AGGTRADES_FILE_STATUS_CSV, base.DEFAULT_AGGTRADES_RAW_ROOT)
    by_symbol: dict[str, list[str]] = defaultdict(list)
    for symbol, file_date in sorted(set(book_rows) & set(agg_rows)):
        by_symbol[symbol].append(file_date)

    pairs: list[dict[str, Any]] = []
    incomplete_symbols: list[dict[str, Any]] = []
    window_details: dict[str, Any] = {}
    for symbol in sorted(by_symbol):
        descending_dates = sorted(by_symbol[symbol], reverse=True)
        selected_desc = descending_dates[days_to_skip : days_to_skip + WINDOW_DAYS]
        if len(selected_desc) < WINDOW_DAYS:
            incomplete_symbols.append({"symbol": symbol, "days_available": len(selected_desc)})
        selected_dates = sorted(selected_desc)
        window_details[symbol] = {
            "days_available": len(selected_dates),
            "newest": selected_desc[0] if selected_desc else "",
            "oldest": selected_desc[-1] if selected_desc else "",
        }
        for file_date in selected_dates:
            key = (symbol, file_date)
            pairs.append(
                {
                    "symbol": symbol,
                    "file_date": file_date,
                    "year_month": file_date[:7],
                    "week": base.iso_week_text(file_date),
                    "bookdepth_zip_path": book_rows[key]["local_zip_path"],
                    "aggtrades_zip_path": agg_rows[key]["local_zip_path"],
                }
            )
    return pairs, {"incomplete_symbols": incomplete_symbols, "window_details": window_details}


def read_features_and_trade_prices(pair: dict[str, Any]) -> tuple[list[int], list[dict[str, Any]], list[int], list[float]]:
    timestamps, rows = base.read_bookdepth_features(pair)
    if not timestamps:
        return timestamps, rows, [], []

    trade_times: list[int] = []
    trade_prices: list[float] = []
    out_of_order = False
    previous_trade_ms = -1
    reader = iter(base.single_csv_reader(Path(str(pair["aggtrades_zip_path"]))))
    header = next(reader, None)
    if not header:
        base.add_rolling_features(rows)
        return timestamps, rows, [], []
    positions = {name: index for index, name in enumerate(header)}
    required = {"price", "quantity", "transact_time", "is_buyer_maker"}
    if not required.issubset(positions):
        raise ValueError(f"aggTrades CSV missing columns: {required - set(positions)}")

    for columns in reader:
        transact_ms = int_value(columns[positions["transact_time"]], -1)
        price = float_value(columns[positions["price"]])
        quantity = float_value(columns[positions["quantity"]])
        if transact_ms < previous_trade_ms:
            out_of_order = True
        previous_trade_ms = transact_ms
        trade_times.append(transact_ms)
        trade_prices.append(price)

        row_index = bisect.bisect_right(timestamps, transact_ms) - 1
        if row_index < 0:
            continue
        row = rows[row_index]
        notional = price * quantity
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
        combined = sorted(zip(trade_times, trade_prices), key=lambda item: item[0])
        trade_times = [item[0] for item in combined]
        trade_prices = [item[1] for item in combined]
    base.add_rolling_features(rows)
    return timestamps, rows, trade_times, trade_prices


def forward_price_return(
    event_ms: int,
    horizon_seconds: int,
    trade_times: list[int],
    trade_prices: list[float],
) -> float | None:
    if not trade_times:
        return None
    reference_index = bisect.bisect_right(trade_times, event_ms) - 1
    future_index = bisect.bisect_left(trade_times, event_ms + horizon_seconds * 1000)
    if reference_index < 0 or future_index >= len(trade_prices):
        return None
    reference_price = trade_prices[reference_index]
    future_price = trade_prices[future_index]
    if reference_price <= 0:
        return None
    return (future_price / reference_price) - 1.0


def distribution_metrics(stats: base.DistributionStats) -> dict[str, Any]:
    return {
        "event_count": stats.valid_forward_count,
        "mean_forward_price_return": rounded(stats.mean(), 12),
        "median_forward_price_return": rounded(stats.sampled_median(), 12),
        "std_forward_price_return": rounded(stats.std(), 12),
        "q05_forward_price_return": rounded(stats.quantile(0.05), 12),
        "q25_forward_price_return": rounded(stats.quantile(0.25), 12),
        "q50_forward_price_return": rounded(stats.quantile(0.50), 12),
        "q75_forward_price_return": rounded(stats.quantile(0.75), 12),
        "q95_forward_price_return": rounded(stats.quantile(0.95), 12),
        "directional_diagnostic_rate": rounded(stats.directional_rate(), 6),
        "directional_diagnostic_count": stats.directional_match,
        "directional_diagnostic_total": stats.directional_total,
    }


def stability_summary(
    window: str,
    category: str,
    horizon: int,
    price_effect: float | None,
    stability: dict[tuple[str, str, int, str, str], base.MomentStats],
) -> dict[str, Any]:
    effect_sign = sign_of(price_effect)
    result: dict[str, Any] = {}
    for period_type in ["SYMBOL", "MONTH", "WEEK"]:
        support = 0
        consistent = 0
        min_count = 100 if period_type == "SYMBOL" else 50
        for (candidate_window, candidate_category, candidate_horizon, candidate_period_type, _period_value), stats in stability.items():
            if (
                candidate_window != window
                or candidate_category != category
                or candidate_horizon != horizon
                or candidate_period_type != period_type
            ):
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
    window: str,
    category: str,
    horizon: int,
    price_effect: float | None,
    stability: dict[tuple[str, str, int, str, str], base.MomentStats],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    effect_sign = sign_of(price_effect)
    for key in sorted(stability):
        candidate_window, candidate_category, candidate_horizon, period_type, period_value = key
        if candidate_window != window or candidate_category != category or candidate_horizon != horizon:
            continue
        stats = stability[key]
        mean_value = stats.mean()
        rows.append(
            {
                "window": window,
                "category": category,
                "horizon_seconds": horizon,
                "period_type": period_type,
                "period_value": period_value,
                "event_count": stats.valid_forward_count,
                "mean_forward_price_return": rounded(mean_value, 12),
                "std_forward_price_return": rounded(stats.std(), 12),
                "directional_diagnostic_rate": rounded(stats.directional_rate(), 6),
                "consistent_with_window_price_effect": (
                    "true" if effect_sign and sign_of(mean_value) == effect_sign else "false"
                ),
            }
        )
    return rows


def price_linkage_status(
    latest_row: dict[str, Any],
    holdout_row: dict[str, Any],
) -> str:
    latest_effect = float_or_none(latest_row.get("price_effect_vs_null"))
    holdout_effect = float_or_none(holdout_row.get("price_effect_vs_null"))
    if int_value(latest_row.get("event_count")) < MIN_PRICE_LINKAGE_EVENT_COUNT:
        return "FAILED_PRICE_LINKAGE_LATEST_COUNT"
    if int_value(holdout_row.get("event_count")) < MIN_PRICE_LINKAGE_EVENT_COUNT:
        return "FAILED_PRICE_LINKAGE_HOLDOUT_COUNT"
    if not sign_of(latest_effect) or not sign_of(holdout_effect):
        return "FAILED_PRICE_LINKAGE_ZERO_OR_UNAVAILABLE_EFFECT"
    if sign_of(latest_effect) != sign_of(holdout_effect):
        return "FAILED_PRICE_LINKAGE_LATEST_HOLDOUT_SIGN_FLIP"
    stability_values = [
        float_or_none(latest_row.get("symbol_stability_rate")),
        float_or_none(latest_row.get("month_stability_rate")),
        float_or_none(latest_row.get("week_stability_rate")),
        float_or_none(holdout_row.get("symbol_stability_rate")),
        float_or_none(holdout_row.get("month_stability_rate")),
        float_or_none(holdout_row.get("week_stability_rate")),
    ]
    if all(value is not None and value >= 0.5 for value in stability_values):
        return "SURVIVED_PRICE_LINKAGE"
    return "PARTIAL_PRICE_LINKAGE_SIGN_MATCH_STABILITY_WEAK"


def process_window(
    window: str,
    pairs: list[dict[str, Any]],
    candidate_stats: dict[tuple[str, str, int], base.DistributionStats],
    null_stats: dict[tuple[str, int], base.MomentStats],
    stability: dict[tuple[str, str, int, str, str], base.MomentStats],
) -> dict[str, Any]:
    started = time.monotonic()
    processed_symbol_days = 0
    failed_symbol_days = 0
    total_feature_rows = 0
    valid_price_observations = 0
    candidate_event_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    failure_examples: list[dict[str, str]] = []
    next_progress = time.monotonic() + PROGRESS_INTERVAL_SECONDS
    candidate_set = set(PRICE_LINKAGE_CANDIDATES)

    for pair in pairs:
        try:
            timestamps, rows, trade_times, trade_prices = read_features_and_trade_prices(pair)
            processed_symbol_days += 1
            total_feature_rows += len(rows)
            symbol = str(pair["symbol"])
            month = str(pair["year_month"])
            week = str(pair.get("week", ""))
            for index, row in enumerate(rows):
                category = str(row.get("absorption_category") or "INSUFFICIENT_DATA")
                if category not in base.CATEGORIES:
                    category = "INSUFFICIENT_DATA"
                category_counts[category] += 1
                expected_direction = base.DIRECTION_BY_CATEGORY.get(category, 0)
                event_ms = timestamps[index]
                for horizon in PRICE_HORIZONS:
                    price_return = forward_price_return(event_ms, horizon, trade_times, trade_prices)
                    null_stats[(window, horizon)].add(price_return, expected_direction)
                    if price_return is not None:
                        valid_price_observations += 1
                    if (category, horizon) not in candidate_set:
                        continue
                    key = (window, category, horizon)
                    if key not in candidate_stats:
                        candidate_stats[key] = base.DistributionStats(
                            sample_limit=RESERVOIR_LIMIT,
                            seed_text=f"price-linkage:{window}:{category}:{horizon}",
                        )
                    candidate_stats[key].add_diagnostic(
                        price_return,
                        expected_direction,
                        "UNUSED",
                        None,
                        None,
                        None,
                    )
                    stability[(window, category, horizon, "SYMBOL", symbol)].add(price_return, expected_direction)
                    stability[(window, category, horizon, "MONTH", month)].add(price_return, expected_direction)
                    stability[(window, category, horizon, "WEEK", week)].add(price_return, expected_direction)
                    if price_return is not None:
                        candidate_event_counts[candidate_label(category, horizon)] += 1
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
                "progress phase=price_linkage "
                f"window={window} processed_symbol_days={processed_symbol_days}/{len(pairs)} "
                f"failed_symbol_days={failed_symbol_days} feature_rows={total_feature_rows} "
                f"valid_price_observations={valid_price_observations} "
                f"elapsed_window_seconds={round(time.monotonic() - started, 1)}",
                flush=True,
            )
            next_progress = time.monotonic() + PROGRESS_INTERVAL_SECONDS
    return {
        "window": window,
        "processed_symbol_days": processed_symbol_days,
        "failed_symbol_days": failed_symbol_days,
        "total_feature_rows": total_feature_rows,
        "valid_price_observations": valid_price_observations,
        "candidate_event_counts": dict(candidate_event_counts),
        "category_counts": dict(category_counts),
        "failure_examples": failure_examples,
    }


def comparison_fieldnames() -> list[str]:
    base_fields = [
        "candidate_rank",
        "category",
        "horizon_seconds",
        "price_linkage_status",
        "latest_vs_holdout_price_effect_consistency",
        "latest_price_vs_latest_depth_direction",
        "holdout_price_vs_holdout_depth_direction",
    ]
    metric_names = [
        "event_count",
        "mean_forward_price_return",
        "median_forward_price_return",
        "std_forward_price_return",
        "q05_forward_price_return",
        "q25_forward_price_return",
        "q50_forward_price_return",
        "q75_forward_price_return",
        "q95_forward_price_return",
        "directional_diagnostic_rate",
        "directional_diagnostic_count",
        "directional_diagnostic_total",
        "null_event_count",
        "null_mean_forward_price_return",
        "null_std_forward_price_return",
        "price_effect_vs_null",
        "price_effect_size_vs_null",
        "previous_depth_proxy_effect_vs_null",
        "previous_depth_proxy_effect_size_vs_null",
        "symbol_stability_rate",
        "month_stability_rate",
        "week_stability_rate",
    ]
    fields = base_fields[:]
    for window_prefix in ["latest", "holdout"]:
        fields.extend([f"{window_prefix}_{name}" for name in metric_names])
    return fields


def null_fieldnames() -> list[str]:
    return [
        "window",
        "category",
        "horizon_seconds",
        "candidate_event_count",
        "candidate_mean_forward_price_return",
        "null_event_count",
        "null_mean_forward_price_return",
        "null_std_forward_price_return",
        "price_effect_vs_null",
        "price_effect_size_vs_null",
    ]


def stability_fieldnames() -> list[str]:
    return [
        "window",
        "category",
        "horizon_seconds",
        "period_type",
        "period_value",
        "event_count",
        "mean_forward_price_return",
        "std_forward_price_return",
        "directional_diagnostic_rate",
        "consistent_with_window_price_effect",
    ]


def build_metric_rows(
    previous_depth: dict[tuple[str, int, str], dict[str, str]],
    candidate_stats: dict[tuple[str, str, int], base.DistributionStats],
    null_stats: dict[tuple[str, int], base.MomentStats],
    stability: dict[tuple[str, str, int, str, str], base.MomentStats],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    per_window_metrics: dict[tuple[str, str, int], dict[str, Any]] = {}
    null_rows: list[dict[str, Any]] = []
    stability_rows: list[dict[str, Any]] = []
    for window_config in WINDOWS:
        window = str(window_config["window"])
        for category, horizon in PRICE_LINKAGE_CANDIDATES:
            stats = candidate_stats.get(
                (window, category, horizon),
                base.DistributionStats(sample_limit=RESERVOIR_LIMIT, seed_text=f"empty:{window}:{category}:{horizon}"),
            )
            null = null_stats[(window, horizon)]
            candidate_mean = stats.mean()
            null_mean = null.mean()
            null_std = null.std()
            effect = candidate_mean - null_mean if candidate_mean is not None and null_mean is not None else None
            effect_size = safe_div(effect, null_std)
            depth_row = previous_depth[(category, horizon, window)]
            stability_metrics = stability_summary(window, category, horizon, effect, stability)
            metric = {
                **distribution_metrics(stats),
                "null_event_count": null.valid_forward_count,
                "null_mean_forward_price_return": rounded(null_mean, 12),
                "null_std_forward_price_return": rounded(null_std, 12),
                "price_effect_vs_null": rounded(effect, 12),
                "price_effect_size_vs_null": rounded(effect_size, 8),
                "previous_depth_proxy_effect_vs_null": depth_row.get(
                    "effect_vs_null",
                    depth_row.get("holdout_effect_vs_null", ""),
                ),
                "previous_depth_proxy_effect_size_vs_null": depth_row.get(
                    "effect_size_vs_null",
                    depth_row.get("holdout_effect_size_vs_null", ""),
                ),
                **{
                    key: rounded(value, 6) if key.endswith("_rate") else value
                    for key, value in stability_metrics.items()
                },
            }
            per_window_metrics[(window, category, horizon)] = metric
            null_rows.append(
                {
                    "window": window,
                    "category": category,
                    "horizon_seconds": horizon,
                    "candidate_event_count": stats.valid_forward_count,
                    "candidate_mean_forward_price_return": rounded(candidate_mean, 12),
                    "null_event_count": null.valid_forward_count,
                    "null_mean_forward_price_return": rounded(null_mean, 12),
                    "null_std_forward_price_return": rounded(null_std, 12),
                    "price_effect_vs_null": rounded(effect, 12),
                    "price_effect_size_vs_null": rounded(effect_size, 8),
                }
            )
            stability_rows.extend(stability_detail_rows(window, category, horizon, effect, stability))

    comparison_rows: list[dict[str, Any]] = []
    for rank, (category, horizon) in enumerate(PRICE_LINKAGE_CANDIDATES, start=1):
        latest = per_window_metrics[("LATEST_90D", category, horizon)]
        holdout = per_window_metrics[("HOLDOUT_90D", category, horizon)]
        status = price_linkage_status(latest, holdout)
        latest_effect = float_or_none(latest.get("price_effect_vs_null"))
        holdout_effect = float_or_none(holdout.get("price_effect_vs_null"))
        latest_depth_effect = float_or_none(latest.get("previous_depth_proxy_effect_vs_null"))
        holdout_depth_effect = float_or_none(holdout.get("previous_depth_proxy_effect_vs_null"))
        row: dict[str, Any] = {
            "candidate_rank": rank,
            "category": category,
            "horizon_seconds": horizon,
            "price_linkage_status": status,
            "latest_vs_holdout_price_effect_consistency": (
                "CONSISTENT" if sign_of(latest_effect) and sign_of(latest_effect) == sign_of(holdout_effect) else "INCONSISTENT"
            ),
            "latest_price_vs_latest_depth_direction": direction_agreement(latest_effect, latest_depth_effect),
            "holdout_price_vs_holdout_depth_direction": direction_agreement(holdout_effect, holdout_depth_effect),
        }
        for prefix, metrics in [("latest", latest), ("holdout", holdout)]:
            for key, value in metrics.items():
                if key.endswith("_support_count") or key.endswith("_consistent_count"):
                    continue
                row[f"{prefix}_{key}"] = value
        comparison_rows.append(row)
    return comparison_rows, null_rows, stability_rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary_md(summary: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM 81 absorption candidate price linkage validation v1",
        "",
        f"status: {summary['status']}",
        f"runtime_seconds: {summary['runtime_seconds']}",
        f"symbol_days_processed_total: {summary['symbol_days_processed_total']}",
        f"valid_price_observations_total: {summary['valid_price_observations_total']}",
        f"survived_price_linkage_candidates: {', '.join(summary['survived_price_linkage_candidates'])}",
        f"failed_price_linkage_candidates: {', '.join(summary['failed_price_linkage_candidates'])}",
        f"row_level_dataset_created: {str(summary['row_level_dataset_created']).lower()}",
        f"parquet_dataset_created: {str(summary['parquet_dataset_created']).lower()}",
        "",
        "## Candidate Results",
        "| rank | category | horizon_seconds | latest_price_effect_size | holdout_price_effect_size | status |",
        "| ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for row in summary.get("candidate_comparison", []):
        lines.append(
            "| "
            f"{row['candidate_rank']} | {row['category']} | {row['horizon_seconds']} | "
            f"{row.get('latest_price_effect_size_vs_null', '')} | "
            f"{row.get('holdout_price_effect_size_vs_null', '')} | "
            f"{row['price_linkage_status']} |"
        )
    lines.extend(
        [
            "",
            "Forward price return uses aggTrades prices: last trade price at or before the event time, then first trade price at or after the horizon time.",
            "This is fixed-candidate research validation only.",
        ]
    )
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def output_sizes() -> dict[str, int]:
    paths = [SUMMARY_JSON, SUMMARY_MD, CANDIDATE_COMPARISON_CSV, SYMBOL_STABILITY_CSV, NULL_COMPARISON_CSV]
    return {path.name: path.stat().st_size for path in paths if path.exists()}


def run_validation() -> dict[str, Any]:
    started = time.monotonic()
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    if base.path_is_inside(base.DEFAULT_BOOKDEPTH_RAW_ROOT, REPO_ROOT) or base.path_is_inside(base.DEFAULT_AGGTRADES_RAW_ROOT, REPO_ROOT):
        raise RuntimeError("raw ZIP roots must stay outside repo")

    previous_depth = load_previous_depth_effects()
    candidate_stats: dict[tuple[str, str, int], base.DistributionStats] = {}
    null_stats: dict[tuple[str, int], base.MomentStats] = defaultdict(base.MomentStats)
    stability: dict[tuple[str, str, int, str, str], base.MomentStats] = defaultdict(base.MomentStats)
    window_summaries: list[dict[str, Any]] = []
    window_selection: dict[str, Any] = {}

    for window_config in WINDOWS:
        window = str(window_config["window"])
        pairs, metadata = build_window_pairs(int(window_config["days_to_skip"]))
        window_selection[window] = metadata
        window_summaries.append(process_window(window, pairs, candidate_stats, null_stats, stability))

    comparison_rows, null_rows, stability_rows = build_metric_rows(previous_depth, candidate_stats, null_stats, stability)
    write_csv(CANDIDATE_COMPARISON_CSV, comparison_fieldnames(), comparison_rows)
    write_csv(NULL_COMPARISON_CSV, null_fieldnames(), null_rows)
    write_csv(SYMBOL_STABILITY_CSV, stability_fieldnames(), stability_rows)

    survived = [
        candidate_label(str(row["category"]), int_value(row["horizon_seconds"]))
        for row in comparison_rows
        if row.get("price_linkage_status") == "SURVIVED_PRICE_LINKAGE"
    ]
    failed = [
        candidate_label(str(row["category"]), int_value(row["horizon_seconds"]))
        for row in comparison_rows
        if row.get("price_linkage_status") != "SURVIVED_PRICE_LINKAGE"
    ]
    total_processed = sum(int(item["processed_symbol_days"]) for item in window_summaries)
    total_failed = sum(int(item["failed_symbol_days"]) for item in window_summaries)
    total_price_observations = sum(int(item["valid_price_observations"]) for item in window_summaries)
    total_feature_rows = sum(int(item["total_feature_rows"]) for item in window_summaries)
    selected_symbol_counts = {
        window: len(metadata.get("window_details", {}))
        for window, metadata in window_selection.items()
    }
    status = (
        "PASS_ORDERBOOK_UM_81_ABSORPTION_CANDIDATE_PRICE_LINKAGE_VALIDATED"
        if total_processed == EXPECTED_SYMBOL_COUNT * WINDOW_DAYS * len(WINDOWS)
        and total_failed == 0
        and all(count == EXPECTED_SYMBOL_COUNT for count in selected_symbol_counts.values())
        and all(not metadata.get("incomplete_symbols") for metadata in window_selection.values())
        else "PARTIAL_ORDERBOOK_UM_81_ABSORPTION_CANDIDATE_PRICE_LINKAGE_VALIDATION"
    )
    summary: dict[str, Any] = {
        "status": status,
        "created_at_utc": utc_now_text(),
        "task": "ORDERBOOK_UM_81_ABSORPTION_CANDIDATE_PRICE_LINKAGE_VALIDATION_V1",
        "mode": "FIXED_CANDIDATE_PRICE_LINKAGE_LATEST_AND_HOLDOUT_90D",
        "raw_bookdepth_root": str(base.DEFAULT_BOOKDEPTH_RAW_ROOT),
        "raw_aggtrades_root": str(base.DEFAULT_AGGTRADES_RAW_ROOT),
        "raw_roots_outside_repo": True,
        "windows": WINDOWS,
        "price_linkage_candidates": [candidate_label(category, horizon) for category, horizon in PRICE_LINKAGE_CANDIDATES],
        "runtime_seconds": round(time.monotonic() - started, 3),
        "symbol_days_processed_total": total_processed,
        "failed_symbol_days_total": total_failed,
        "feature_rows_seen_total": total_feature_rows,
        "valid_price_observations_total": total_price_observations,
        "window_summaries": window_summaries,
        "window_selection": window_selection,
        "candidate_comparison": comparison_rows,
        "survived_price_linkage_candidates": survived,
        "failed_price_linkage_candidates": failed,
        "price_return_definition": "simple forward return from aggTrades price: future_price / reference_price - 1",
        "reference_price_definition": "last aggTrade price at or before the absorption event timestamp",
        "future_price_definition": "first aggTrade price at or after event timestamp plus the candidate horizon",
        "row_level_dataset_created": False,
        "parquet_dataset_created": False,
        "downloads_run": False,
        "outputs": {
            "summary_json": str(SUMMARY_JSON),
            "summary_md": str(SUMMARY_MD),
            "candidate_comparison_csv": str(CANDIDATE_COMPARISON_CSV),
            "symbol_stability_csv": str(SYMBOL_STABILITY_CSV),
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
            "status": "FAILED_ORDERBOOK_UM_81_ABSORPTION_CANDIDATE_PRICE_LINKAGE_VALIDATION",
            "created_at_utc": utc_now_text(),
            "error": f"{type(exc).__name__}: {exc}",
            "row_level_dataset_created": False,
            "parquet_dataset_created": False,
            "downloads_run": False,
        }
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        SUMMARY_JSON.write_text(json.dumps(error_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        SUMMARY_MD.write_text(
            "# Orderbook UM 81 absorption candidate price linkage validation v1\n\n"
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
