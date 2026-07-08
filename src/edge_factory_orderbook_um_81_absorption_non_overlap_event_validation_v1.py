#!/usr/bin/env python
"""Validate fixed absorption candidates after removing overlapping events."""

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

SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_81_absorption_non_overlap_event_validation_summary.json"
SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_81_absorption_non_overlap_event_validation_summary.md"
CANDIDATE_COOLDOWN_CSV = OUTPUTS_DIR / "orderbook_um_81_absorption_non_overlap_event_validation_candidate_cooldown.csv"
SYMBOL_STABILITY_CSV = OUTPUTS_DIR / "orderbook_um_81_absorption_non_overlap_event_validation_symbol_stability.csv"
NULL_COMPARISON_CSV = OUTPUTS_DIR / "orderbook_um_81_absorption_non_overlap_event_validation_null_comparison.csv"

EXPECTED_SYMBOL_COUNT = 81
WINDOW_DAYS = 90
PROGRESS_INTERVAL_SECONDS = 30
MIN_NON_OVERLAP_EVENT_COUNT = 100
RESERVOIR_LIMIT = 50_000

WINDOWS = [
    {"window": "LATEST_90D", "days_to_skip": 0},
    {"window": "HOLDOUT_90D", "days_to_skip": 90},
]

NON_OVERLAP_CANDIDATES = [
    ("SELL_PRESSURE_ABSORBED", 300),
    ("FLOW_AND_DEPTH_ALIGNED_DOWN", 300),
    ("FLOW_AND_DEPTH_ALIGNED_DOWN", 60),
    ("FLOW_AND_DEPTH_ALIGNED_DOWN", 30),
]

COOLDOWN_SECONDS = [300, 600, 900]
PRICE_HORIZONS = sorted({horizon for _category, horizon in NON_OVERLAP_CANDIDATES})


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def int_value(value: Any, default: int = 0) -> int:
    return base.int_value(value, default)


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


def candidate_label(category: str, horizon: int) -> str:
    return f"{category}@{horizon}s"


def cooldown_label(category: str, horizon: int, cooldown: int) -> str:
    return f"{candidate_label(category, horizon)} cooldown={cooldown}s"


def float_or_none(value: Any) -> float | None:
    return price_linkage.float_or_none(value)


def fresh_distribution(seed_text: str) -> base.DistributionStats:
    return base.DistributionStats(sample_limit=RESERVOIR_LIMIT, seed_text=seed_text)


def may_keep_event(last_kept_ms: int | None, event_ms: int, cooldown_seconds: int) -> bool:
    if last_kept_ms is None:
        return True
    return event_ms - last_kept_ms >= cooldown_seconds * 1000


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
    cooldown: int,
    price_effect: float | None,
    stability: dict[tuple[str, str, int, int, str, str], base.MomentStats],
) -> dict[str, Any]:
    effect_sign = sign_of(price_effect)
    result: dict[str, Any] = {}
    for period_type in ["SYMBOL", "MONTH", "WEEK"]:
        support = 0
        consistent = 0
        min_count = 100 if period_type == "SYMBOL" else 50
        for key, stats in stability.items():
            candidate_window, candidate_category, candidate_horizon, candidate_cooldown, candidate_period_type, _period_value = key
            if (
                candidate_window != window
                or candidate_category != category
                or candidate_horizon != horizon
                or candidate_cooldown != cooldown
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
    cooldown: int,
    price_effect: float | None,
    stability: dict[tuple[str, str, int, int, str, str], base.MomentStats],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    effect_sign = sign_of(price_effect)
    for key in sorted(stability):
        candidate_window, candidate_category, candidate_horizon, candidate_cooldown, period_type, period_value = key
        if (
            candidate_window != window
            or candidate_category != category
            or candidate_horizon != horizon
            or candidate_cooldown != cooldown
        ):
            continue
        stats = stability[key]
        mean_value = stats.mean()
        rows.append(
            {
                "window": window,
                "category": category,
                "horizon_seconds": horizon,
                "cooldown_seconds": cooldown,
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


def non_overlap_status(latest_row: dict[str, Any], holdout_row: dict[str, Any]) -> str:
    latest_effect = float_or_none(latest_row.get("price_effect_vs_null"))
    holdout_effect = float_or_none(holdout_row.get("price_effect_vs_null"))
    if int_value(latest_row.get("event_count")) < MIN_NON_OVERLAP_EVENT_COUNT:
        return "FAILED_NON_OVERLAP_LATEST_COUNT"
    if int_value(holdout_row.get("event_count")) < MIN_NON_OVERLAP_EVENT_COUNT:
        return "FAILED_NON_OVERLAP_HOLDOUT_COUNT"
    if not sign_of(latest_effect) or not sign_of(holdout_effect):
        return "FAILED_NON_OVERLAP_ZERO_OR_UNAVAILABLE_EFFECT"
    if sign_of(latest_effect) != sign_of(holdout_effect):
        return "FAILED_NON_OVERLAP_LATEST_HOLDOUT_SIGN_FLIP"
    stability_values = [
        float_or_none(latest_row.get("symbol_stability_rate")),
        float_or_none(latest_row.get("month_stability_rate")),
        float_or_none(latest_row.get("week_stability_rate")),
        float_or_none(holdout_row.get("symbol_stability_rate")),
        float_or_none(holdout_row.get("month_stability_rate")),
        float_or_none(holdout_row.get("week_stability_rate")),
    ]
    if all(value is not None and value >= 0.5 for value in stability_values):
        return "SURVIVED_NON_OVERLAP"
    return "PARTIAL_NON_OVERLAP_SIGN_MATCH_STABILITY_WEAK"


def process_window(
    window: str,
    pairs: list[dict[str, Any]],
    candidate_stats: dict[tuple[str, str, int, int], base.DistributionStats],
    null_stats: dict[tuple[str, int, int], base.MomentStats],
    stability: dict[tuple[str, str, int, int, str, str], base.MomentStats],
    original_event_counts: Counter[tuple[str, str, int]],
    original_row_counts: Counter[tuple[str, str, int]],
    null_original_counts: Counter[tuple[str, int]],
) -> dict[str, Any]:
    started = time.monotonic()
    processed_symbol_days = 0
    failed_symbol_days = 0
    total_feature_rows = 0
    valid_price_observations = 0
    category_counts: Counter[str] = Counter()
    failure_examples: list[dict[str, str]] = []
    next_progress = time.monotonic() + PROGRESS_INTERVAL_SECONDS
    candidate_by_category: dict[str, set[int]] = defaultdict(set)
    for category, horizon in NON_OVERLAP_CANDIDATES:
        candidate_by_category[category].add(horizon)
    last_kept_ms: dict[tuple[str, str, int, int], int] = {}
    last_null_kept_ms: dict[tuple[str, int, int], int] = {}

    for pair in pairs:
        try:
            timestamps, rows, trade_times, trade_prices = price_linkage.read_features_and_trade_prices(pair)
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
                returns_by_horizon: dict[int, float | None] = {}
                for horizon in PRICE_HORIZONS:
                    price_return = price_linkage.forward_price_return(event_ms, horizon, trade_times, trade_prices)
                    returns_by_horizon[horizon] = price_return
                    if price_return is not None:
                        valid_price_observations += 1
                        null_original_counts[(window, horizon)] += 1
                    for cooldown in COOLDOWN_SECONDS:
                        null_key = (symbol, horizon, cooldown)
                        if price_return is None:
                            continue
                        if not may_keep_event(last_null_kept_ms.get(null_key), event_ms, cooldown):
                            continue
                        last_null_kept_ms[null_key] = event_ms
                        null_stats[(window, horizon, cooldown)].add(price_return, expected_direction)

                if category not in candidate_by_category:
                    continue
                for horizon in candidate_by_category[category]:
                    original_row_counts[(window, category, horizon)] += 1
                    price_return = returns_by_horizon.get(horizon)
                    if price_return is None:
                        continue
                    original_event_counts[(window, category, horizon)] += 1
                    for cooldown in COOLDOWN_SECONDS:
                        symbol_key = (symbol, category, horizon, cooldown)
                        if not may_keep_event(last_kept_ms.get(symbol_key), event_ms, cooldown):
                            continue
                        last_kept_ms[symbol_key] = event_ms
                        stats_key = (window, category, horizon, cooldown)
                        if stats_key not in candidate_stats:
                            candidate_stats[stats_key] = fresh_distribution(
                                f"non-overlap:{window}:{category}:{horizon}:{cooldown}"
                            )
                        candidate_stats[stats_key].add_diagnostic(
                            price_return,
                            expected_direction,
                            "UNUSED",
                            None,
                            None,
                            None,
                        )
                        stability[(window, category, horizon, cooldown, "SYMBOL", symbol)].add(
                            price_return,
                            expected_direction,
                        )
                        stability[(window, category, horizon, cooldown, "MONTH", month)].add(
                            price_return,
                            expected_direction,
                        )
                        stability[(window, category, horizon, cooldown, "WEEK", week)].add(
                            price_return,
                            expected_direction,
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
            kept_events = sum(
                stats.valid_forward_count
                for key, stats in candidate_stats.items()
                if key[0] == window
            )
            print(
                "progress phase=non_overlap_price_linkage "
                f"window={window} processed_symbol_days={processed_symbol_days}/{len(pairs)} "
                f"failed_symbol_days={failed_symbol_days} feature_rows={total_feature_rows} "
                f"valid_price_observations={valid_price_observations} kept_candidate_events={kept_events} "
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
        "category_counts": dict(category_counts),
        "original_candidate_event_counts": {
            candidate_label(category, horizon): original_event_counts[(window, category, horizon)]
            for category, horizon in NON_OVERLAP_CANDIDATES
        },
        "failure_examples": failure_examples,
    }


def metric_names() -> list[str]:
    return [
        "original_candidate_row_count",
        "original_event_count",
        "event_count",
        "retention_rate",
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
        "null_original_event_count",
        "null_event_count",
        "null_retention_rate",
        "null_mean_forward_price_return",
        "null_std_forward_price_return",
        "price_effect_vs_null",
        "price_effect_size_vs_null",
        "symbol_stability_rate",
        "month_stability_rate",
        "week_stability_rate",
    ]


def candidate_cooldown_fieldnames() -> list[str]:
    fields = [
        "candidate_rank",
        "category",
        "horizon_seconds",
        "cooldown_seconds",
        "non_overlap_status",
        "latest_vs_holdout_price_effect_consistency",
    ]
    for prefix in ["latest", "holdout"]:
        fields.extend([f"{prefix}_{name}" for name in metric_names()])
    return fields


def null_fieldnames() -> list[str]:
    return [
        "window",
        "category",
        "horizon_seconds",
        "cooldown_seconds",
        "original_event_count",
        "non_overlap_event_count",
        "retention_rate",
        "candidate_mean_forward_price_return",
        "null_original_event_count",
        "null_non_overlap_event_count",
        "null_retention_rate",
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
        "cooldown_seconds",
        "period_type",
        "period_value",
        "event_count",
        "mean_forward_price_return",
        "std_forward_price_return",
        "directional_diagnostic_rate",
        "consistent_with_window_price_effect",
    ]


def build_metric_rows(
    candidate_stats: dict[tuple[str, str, int, int], base.DistributionStats],
    null_stats: dict[tuple[str, int, int], base.MomentStats],
    stability: dict[tuple[str, str, int, int, str, str], base.MomentStats],
    original_event_counts: Counter[tuple[str, str, int]],
    original_row_counts: Counter[tuple[str, str, int]],
    null_original_counts: Counter[tuple[str, int]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    per_window_metrics: dict[tuple[str, str, int, int], dict[str, Any]] = {}
    null_rows: list[dict[str, Any]] = []
    stability_rows: list[dict[str, Any]] = []
    for window_config in WINDOWS:
        window = str(window_config["window"])
        for category, horizon in NON_OVERLAP_CANDIDATES:
            for cooldown in COOLDOWN_SECONDS:
                stats_key = (window, category, horizon, cooldown)
                stats = candidate_stats.get(
                    stats_key,
                    fresh_distribution(f"empty:{window}:{category}:{horizon}:{cooldown}"),
                )
                null = null_stats[(window, horizon, cooldown)]
                candidate_mean = stats.mean()
                null_mean = null.mean()
                null_std = null.std()
                effect = candidate_mean - null_mean if candidate_mean is not None and null_mean is not None else None
                effect_size = safe_div(effect, null_std)
                original_count = original_event_counts[(window, category, horizon)]
                null_original_count = null_original_counts[(window, horizon)]
                stability_metrics = stability_summary(window, category, horizon, cooldown, effect, stability)
                metric = {
                    "original_candidate_row_count": original_row_counts[(window, category, horizon)],
                    "original_event_count": original_count,
                    **distribution_metrics(stats),
                    "retention_rate": rounded(safe_div(stats.valid_forward_count, original_count), 6),
                    "null_original_event_count": null_original_count,
                    "null_event_count": null.valid_forward_count,
                    "null_retention_rate": rounded(safe_div(null.valid_forward_count, null_original_count), 6),
                    "null_mean_forward_price_return": rounded(null_mean, 12),
                    "null_std_forward_price_return": rounded(null_std, 12),
                    "price_effect_vs_null": rounded(effect, 12),
                    "price_effect_size_vs_null": rounded(effect_size, 8),
                    **{
                        key: rounded(value, 6) if key.endswith("_rate") else value
                        for key, value in stability_metrics.items()
                    },
                }
                per_window_metrics[stats_key] = metric
                null_rows.append(
                    {
                        "window": window,
                        "category": category,
                        "horizon_seconds": horizon,
                        "cooldown_seconds": cooldown,
                        "original_event_count": original_count,
                        "non_overlap_event_count": stats.valid_forward_count,
                        "retention_rate": rounded(safe_div(stats.valid_forward_count, original_count), 6),
                        "candidate_mean_forward_price_return": rounded(candidate_mean, 12),
                        "null_original_event_count": null_original_count,
                        "null_non_overlap_event_count": null.valid_forward_count,
                        "null_retention_rate": rounded(safe_div(null.valid_forward_count, null_original_count), 6),
                        "null_mean_forward_price_return": rounded(null_mean, 12),
                        "null_std_forward_price_return": rounded(null_std, 12),
                        "price_effect_vs_null": rounded(effect, 12),
                        "price_effect_size_vs_null": rounded(effect_size, 8),
                    }
                )
                stability_rows.extend(stability_detail_rows(window, category, horizon, cooldown, effect, stability))

    candidate_rows: list[dict[str, Any]] = []
    rank = 1
    for category, horizon in NON_OVERLAP_CANDIDATES:
        for cooldown in COOLDOWN_SECONDS:
            latest = per_window_metrics[("LATEST_90D", category, horizon, cooldown)]
            holdout = per_window_metrics[("HOLDOUT_90D", category, horizon, cooldown)]
            status = non_overlap_status(latest, holdout)
            latest_effect = float_or_none(latest.get("price_effect_vs_null"))
            holdout_effect = float_or_none(holdout.get("price_effect_vs_null"))
            row: dict[str, Any] = {
                "candidate_rank": rank,
                "category": category,
                "horizon_seconds": horizon,
                "cooldown_seconds": cooldown,
                "non_overlap_status": status,
                "latest_vs_holdout_price_effect_consistency": (
                    "CONSISTENT"
                    if sign_of(latest_effect) and sign_of(latest_effect) == sign_of(holdout_effect)
                    else "INCONSISTENT"
                ),
            }
            for prefix, metrics in [("latest", latest), ("holdout", holdout)]:
                for key, value in metrics.items():
                    if key.endswith("_support_count") or key.endswith("_consistent_count"):
                        continue
                    row[f"{prefix}_{key}"] = value
            candidate_rows.append(row)
            rank += 1
    return candidate_rows, null_rows, stability_rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def candidate_level_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["category"]), int_value(row["horizon_seconds"]))].append(row)
    result: list[dict[str, Any]] = []
    for category, horizon in NON_OVERLAP_CANDIDATES:
        candidate_rows = grouped[(category, horizon)]
        survived_cooldowns = [
            int_value(row.get("cooldown_seconds"))
            for row in candidate_rows
            if row.get("non_overlap_status") == "SURVIVED_NON_OVERLAP"
        ]
        failed_cooldowns = [
            int_value(row.get("cooldown_seconds"))
            for row in candidate_rows
            if row.get("non_overlap_status") != "SURVIVED_NON_OVERLAP"
        ]
        result.append(
            {
                "candidate": candidate_label(category, horizon),
                "survived_any_cooldown": bool(survived_cooldowns),
                "survived_all_cooldowns": len(survived_cooldowns) == len(COOLDOWN_SECONDS),
                "survived_cooldowns_seconds": survived_cooldowns,
                "failed_cooldowns_seconds": failed_cooldowns,
            }
        )
    return result


def write_summary_md(summary: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM 81 absorption non-overlap event validation v1",
        "",
        f"status: {summary['status']}",
        f"runtime_seconds: {summary['runtime_seconds']}",
        f"symbol_days_processed_total: {summary['symbol_days_processed_total']}",
        f"valid_price_observations_total: {summary['valid_price_observations_total']}",
        f"survived_non_overlap_candidate_cooldowns: {', '.join(summary['survived_non_overlap_candidate_cooldowns'])}",
        f"failed_non_overlap_candidate_cooldowns: {', '.join(summary['failed_non_overlap_candidate_cooldowns'])}",
        f"row_level_dataset_created: {str(summary['row_level_dataset_created']).lower()}",
        f"parquet_dataset_created: {str(summary['parquet_dataset_created']).lower()}",
        "",
        "## Candidate Cooldown Results",
        "| category | horizon_seconds | cooldown_seconds | latest_events | holdout_events | latest_effect_size | holdout_effect_size | status |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in summary.get("candidate_cooldown_comparison", []):
        lines.append(
            "| "
            f"{row['category']} | {row['horizon_seconds']} | {row['cooldown_seconds']} | "
            f"{row.get('latest_event_count', '')} | {row.get('holdout_event_count', '')} | "
            f"{row.get('latest_price_effect_size_vs_null', '')} | "
            f"{row.get('holdout_price_effect_size_vs_null', '')} | "
            f"{row['non_overlap_status']} |"
        )
    lines.extend(
        [
            "",
            "Forward price return uses aggTrades prices: last trade price at or before the event time, then first trade price at or after the horizon time.",
            "Cooldown filtering keeps the first event per symbol and candidate, then suppresses later events inside the selected cooldown window.",
            "This is fixed-candidate research validation only.",
        ]
    )
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def output_sizes() -> dict[str, int]:
    paths = [SUMMARY_JSON, SUMMARY_MD, CANDIDATE_COOLDOWN_CSV, SYMBOL_STABILITY_CSV, NULL_COMPARISON_CSV]
    return {path.name: path.stat().st_size for path in paths if path.exists()}


def run_validation() -> dict[str, Any]:
    started = time.monotonic()
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    if base.path_is_inside(base.DEFAULT_BOOKDEPTH_RAW_ROOT, REPO_ROOT) or base.path_is_inside(
        base.DEFAULT_AGGTRADES_RAW_ROOT,
        REPO_ROOT,
    ):
        raise RuntimeError("raw ZIP roots must stay outside repo")

    candidate_stats: dict[tuple[str, str, int, int], base.DistributionStats] = {}
    null_stats: dict[tuple[str, int, int], base.MomentStats] = defaultdict(base.MomentStats)
    stability: dict[tuple[str, str, int, int, str, str], base.MomentStats] = defaultdict(base.MomentStats)
    original_event_counts: Counter[tuple[str, str, int]] = Counter()
    original_row_counts: Counter[tuple[str, str, int]] = Counter()
    null_original_counts: Counter[tuple[str, int]] = Counter()
    window_summaries: list[dict[str, Any]] = []
    window_selection: dict[str, Any] = {}

    for window_config in WINDOWS:
        window = str(window_config["window"])
        pairs, metadata = price_linkage.build_window_pairs(int(window_config["days_to_skip"]))
        window_selection[window] = metadata
        window_summaries.append(
            process_window(
                window,
                pairs,
                candidate_stats,
                null_stats,
                stability,
                original_event_counts,
                original_row_counts,
                null_original_counts,
            )
        )

    candidate_rows, null_rows, stability_rows = build_metric_rows(
        candidate_stats,
        null_stats,
        stability,
        original_event_counts,
        original_row_counts,
        null_original_counts,
    )
    write_csv(CANDIDATE_COOLDOWN_CSV, candidate_cooldown_fieldnames(), candidate_rows)
    write_csv(NULL_COMPARISON_CSV, null_fieldnames(), null_rows)
    write_csv(SYMBOL_STABILITY_CSV, stability_fieldnames(), stability_rows)

    survived = [
        cooldown_label(str(row["category"]), int_value(row["horizon_seconds"]), int_value(row["cooldown_seconds"]))
        for row in candidate_rows
        if row.get("non_overlap_status") == "SURVIVED_NON_OVERLAP"
    ]
    failed = [
        cooldown_label(str(row["category"]), int_value(row["horizon_seconds"]), int_value(row["cooldown_seconds"]))
        for row in candidate_rows
        if row.get("non_overlap_status") != "SURVIVED_NON_OVERLAP"
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
        "PASS_ORDERBOOK_UM_81_ABSORPTION_NON_OVERLAP_EVENT_VALIDATED"
        if total_processed == EXPECTED_SYMBOL_COUNT * WINDOW_DAYS * len(WINDOWS)
        and total_failed == 0
        and all(count == EXPECTED_SYMBOL_COUNT for count in selected_symbol_counts.values())
        and all(not metadata.get("incomplete_symbols") for metadata in window_selection.values())
        else "PARTIAL_ORDERBOOK_UM_81_ABSORPTION_NON_OVERLAP_EVENT_VALIDATION"
    )
    summary: dict[str, Any] = {
        "status": status,
        "created_at_utc": utc_now_text(),
        "task": "ORDERBOOK_UM_81_ABSORPTION_NON_OVERLAP_EVENT_VALIDATION_V1",
        "mode": "FIXED_CANDIDATE_PRICE_LINKAGE_NON_OVERLAP_LATEST_AND_HOLDOUT_90D",
        "raw_bookdepth_root": str(base.DEFAULT_BOOKDEPTH_RAW_ROOT),
        "raw_aggtrades_root": str(base.DEFAULT_AGGTRADES_RAW_ROOT),
        "raw_roots_outside_repo": True,
        "windows": WINDOWS,
        "cooldown_seconds": COOLDOWN_SECONDS,
        "non_overlap_candidates": [candidate_label(category, horizon) for category, horizon in NON_OVERLAP_CANDIDATES],
        "runtime_seconds": round(time.monotonic() - started, 3),
        "symbol_days_processed_total": total_processed,
        "failed_symbol_days_total": total_failed,
        "feature_rows_seen_total": total_feature_rows,
        "valid_price_observations_total": total_price_observations,
        "window_summaries": window_summaries,
        "window_selection_summary": {
            window: {
                "selected_symbol_count": len(metadata.get("window_details", {})),
                "incomplete_symbol_count": len(metadata.get("incomplete_symbols", [])),
                "oldest_by_symbol_min": min(
                    (details.get("oldest", "") for details in metadata.get("window_details", {}).values()),
                    default="",
                ),
                "newest_by_symbol_max": max(
                    (details.get("newest", "") for details in metadata.get("window_details", {}).values()),
                    default="",
                ),
            }
            for window, metadata in window_selection.items()
        },
        "candidate_cooldown_comparison": candidate_rows,
        "candidate_level_summary": candidate_level_summary(candidate_rows),
        "survived_non_overlap_candidate_cooldowns": survived,
        "failed_non_overlap_candidate_cooldowns": failed,
        "price_return_definition": "simple forward return from aggTrades price: future_price / reference_price - 1",
        "reference_price_definition": "last aggTrade price at or before the absorption event timestamp",
        "future_price_definition": "first aggTrade price at or after event timestamp plus the candidate horizon",
        "null_comparison_method": "all valid bookDepth timestamps for the same horizon, with the same per-symbol cooldown filtering applied",
        "row_level_dataset_created": False,
        "parquet_dataset_created": False,
        "downloads_run": False,
        "outputs": {
            "summary_json": str(SUMMARY_JSON),
            "summary_md": str(SUMMARY_MD),
            "candidate_cooldown_csv": str(CANDIDATE_COOLDOWN_CSV),
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
            "status": "FAILED_ORDERBOOK_UM_81_ABSORPTION_NON_OVERLAP_EVENT_VALIDATION",
            "created_at_utc": utc_now_text(),
            "error": f"{type(exc).__name__}: {exc}",
            "row_level_dataset_created": False,
            "parquet_dataset_created": False,
            "downloads_run": False,
        }
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        SUMMARY_JSON.write_text(json.dumps(error_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        SUMMARY_MD.write_text(
            "# Orderbook UM 81 absorption non-overlap event validation v1\n\n"
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
