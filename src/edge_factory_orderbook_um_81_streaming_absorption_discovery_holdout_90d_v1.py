#!/usr/bin/env python
"""Run disjoint 90-day holdout validation for prior absorption discovery candidates."""

from __future__ import annotations

import csv
import json
import math
import os
import statistics
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import edge_factory_orderbook_um_81_streaming_absorption_discovery_90d_v1 as base


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"

LATEST_CANDIDATES_CSV = OUTPUTS_DIR / "orderbook_um_81_streaming_absorption_discovery_90d_candidates.csv"

SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_81_streaming_absorption_discovery_holdout_90d_summary.json"
SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_81_streaming_absorption_discovery_holdout_90d_summary.md"
CANDIDATE_COMPARISON_CSV = OUTPUTS_DIR / "orderbook_um_81_streaming_absorption_discovery_holdout_90d_candidate_comparison.csv"
SIGN_AUDIT_CSV = OUTPUTS_DIR / "orderbook_um_81_streaming_absorption_discovery_holdout_90d_sign_audit.csv"
STABILITY_CSV = OUTPUTS_DIR / "orderbook_um_81_streaming_absorption_discovery_holdout_90d_stability.csv"

EXPECTED_SYMBOL_COUNT = 81
HOLDOUT_DAYS_PER_SYMBOL = 90
LATEST_WINDOW_DAYS_PER_SYMBOL = 90
PROGRESS_INTERVAL_SECONDS = 30
MIN_HOLDOUT_SAMPLE_COUNT = 500

PREVIOUS_CANDIDATES = [
    ("FLOW_AND_DEPTH_ALIGNED_DOWN", 300),
    ("SELL_PRESSURE_ABSORBED", 300),
    ("FLOW_AND_DEPTH_ALIGNED_DOWN", 60),
    ("FLOW_AND_DEPTH_ALIGNED_DOWN", 30),
    ("FLOW_AND_DEPTH_ALIGNED_DOWN", 10),
]


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def int_value(value: Any, default: int = 0) -> int:
    return base.int_value(value, default)


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


def load_latest_candidates() -> dict[tuple[str, int], dict[str, str]]:
    if not LATEST_CANDIDATES_CSV.exists():
        raise FileNotFoundError(f"missing latest candidate CSV: {LATEST_CANDIDATES_CSV}")
    with LATEST_CANDIDATES_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    by_key: dict[tuple[str, int], dict[str, str]] = {}
    for row in rows:
        key = (str(row.get("category", "")), int_value(row.get("horizon_seconds")))
        by_key[key] = row
    missing = [f"{category}@{horizon}s" for category, horizon in PREVIOUS_CANDIDATES if (category, horizon) not in by_key]
    if missing:
        raise ValueError(f"latest candidate CSV missing required candidates: {', '.join(missing)}")
    return by_key


def iso_week_text(file_date: str) -> str:
    return base.iso_week_text(file_date)


def build_holdout_pairs() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    book_rows = base.load_verified_paths(base.BOOKDEPTH_FILE_STATUS_CSV, base.DEFAULT_BOOKDEPTH_RAW_ROOT)
    agg_rows = base.load_verified_paths(base.AGGTRADES_FILE_STATUS_CSV, base.DEFAULT_AGGTRADES_RAW_ROOT)
    by_symbol: dict[str, list[str]] = defaultdict(list)
    for symbol, file_date in sorted(set(book_rows) & set(agg_rows)):
        by_symbol[symbol].append(file_date)

    pairs: list[dict[str, Any]] = []
    window_details: dict[str, Any] = {}
    incomplete_symbols: list[dict[str, Any]] = []
    for symbol in sorted(by_symbol):
        descending_dates = sorted(by_symbol[symbol], reverse=True)
        latest_window = descending_dates[:LATEST_WINDOW_DAYS_PER_SYMBOL]
        holdout_window_desc = descending_dates[
            LATEST_WINDOW_DAYS_PER_SYMBOL : LATEST_WINDOW_DAYS_PER_SYMBOL + HOLDOUT_DAYS_PER_SYMBOL
        ]
        if len(holdout_window_desc) < HOLDOUT_DAYS_PER_SYMBOL:
            incomplete_symbols.append({"symbol": symbol, "holdout_days_available": len(holdout_window_desc)})
        holdout_window = sorted(holdout_window_desc)
        window_details[symbol] = {
            "latest_window_newest": latest_window[0] if latest_window else "",
            "latest_window_oldest": latest_window[-1] if latest_window else "",
            "holdout_window_newest": holdout_window_desc[0] if holdout_window_desc else "",
            "holdout_window_oldest": holdout_window_desc[-1] if holdout_window_desc else "",
            "holdout_days_available": len(holdout_window),
        }
        for file_date in holdout_window:
            key = (symbol, file_date)
            pairs.append(
                {
                    "symbol": symbol,
                    "file_date": file_date,
                    "year_month": file_date[:7],
                    "week": iso_week_text(file_date),
                    "bookdepth_zip_path": book_rows[key]["local_zip_path"],
                    "aggtrades_zip_path": agg_rows[key]["local_zip_path"],
                    "bookdepth_size_bytes": int_value(book_rows[key].get("observed_size_bytes")),
                    "aggtrades_size_bytes": int_value(agg_rows[key].get("observed_size_bytes")),
                }
            )
    return pairs, {"window_details": window_details, "incomplete_symbols": incomplete_symbols}


def compute_metric_row(
    category: str,
    horizon: int,
    category_horizon: dict[tuple[str, int], base.DistributionStats],
    horizon_null: dict[int, base.MomentStats],
    stability: dict[tuple[str, str, str, str, int], base.MomentStats],
) -> dict[str, Any]:
    stats = category_horizon.get((category, horizon))
    null_stats = horizon_null[horizon]
    mean_value = stats.mean() if stats else None
    null_mean = null_stats.mean()
    null_std = null_stats.std()
    effect = mean_value - null_mean if mean_value is not None and null_mean is not None else None
    effect_size = safe_div(effect, null_std)
    stability_result = base.stability_rates(category, horizon, effect, stability)
    return {
        "category": category,
        "horizon_seconds": horizon,
        "valid_forward_count": stats.valid_forward_count if stats else 0,
        "mean_forward_proxy_return": mean_value,
        "null_mean_forward_proxy_return": null_mean,
        "null_std_forward_proxy_return": null_std,
        "effect_vs_null": effect,
        "effect_size_vs_null": effect_size,
        "directional_diagnostic_rate": stats.directional_rate() if stats else None,
        "symbol_support_count": stability_result.get("symbol_support_count", 0),
        "symbol_consistent_count": stability_result.get("symbol_consistent_count", 0),
        "symbol_stability_rate": stability_result.get("symbol_stability_rate"),
        "month_support_count": stability_result.get("month_support_count", 0),
        "month_consistent_count": stability_result.get("month_consistent_count", 0),
        "month_stability_rate": stability_result.get("month_stability_rate"),
        "week_support_count": stability_result.get("week_support_count", 0),
        "week_consistent_count": stability_result.get("week_consistent_count", 0),
        "week_stability_rate": stability_result.get("week_stability_rate"),
    }


def survival_status(latest_effect: float | None, holdout: dict[str, Any]) -> str:
    holdout_effect = float_or_none(holdout.get("effect_vs_null"))
    if int_value(holdout.get("valid_forward_count")) < MIN_HOLDOUT_SAMPLE_COUNT:
        return "FAILED_HOLDOUT_INSUFFICIENT_COUNT"
    latest_sign = sign_of(latest_effect)
    holdout_sign = sign_of(holdout_effect)
    if latest_sign == 0 or holdout_sign == 0:
        return "FAILED_HOLDOUT_ZERO_OR_UNAVAILABLE_EFFECT"
    if latest_sign != holdout_sign:
        return "FAILED_HOLDOUT_SIGN_FLIP"
    stability_values = [
        float_or_none(holdout.get("symbol_stability_rate")),
        float_or_none(holdout.get("month_stability_rate")),
        float_or_none(holdout.get("week_stability_rate")),
    ]
    if all(value is not None and value >= 0.5 for value in stability_values):
        return "SURVIVED_HOLDOUT"
    return "PARTIAL_HOLDOUT_SIGN_MATCH_STABILITY_WEAK"


def comparison_fieldnames() -> list[str]:
    return [
        "candidate_rank",
        "category",
        "horizon_seconds",
        "latest_valid_forward_count",
        "holdout_valid_forward_count",
        "latest_mean_forward_proxy_return",
        "holdout_mean_forward_proxy_return",
        "latest_null_mean_forward_proxy_return",
        "holdout_null_mean_forward_proxy_return",
        "latest_effect_vs_null",
        "holdout_effect_vs_null",
        "latest_effect_size_vs_null",
        "holdout_effect_size_vs_null",
        "effect_size_retention_ratio",
        "latest_directional_diagnostic_rate",
        "holdout_directional_diagnostic_rate",
        "latest_symbol_stability_rate",
        "holdout_symbol_stability_rate",
        "latest_month_stability_rate",
        "holdout_month_stability_rate",
        "latest_week_stability_rate",
        "holdout_week_stability_rate",
        "holdout_status",
    ]


def stability_fieldnames() -> list[str]:
    return [
        "candidate_rank",
        "category",
        "horizon_seconds",
        "period_type",
        "support_count",
        "consistent_count",
        "stability_rate",
    ]


def sign_audit_fieldnames() -> list[str]:
    return [
        "candidate_rank",
        "category",
        "horizon_seconds",
        "forward_proxy_return_definition",
        "positive_proxy_means",
        "category_definition",
        "category_label_proxy_direction",
        "latest_effect_sign",
        "holdout_effect_sign",
        "holdout_vs_latest_sign",
        "effect_sign_vs_category_label",
        "sign_sanity_result",
    ]


def category_definition(category: str) -> str:
    definitions = {
        "BUY_PRESSURE_ABSORBED": "rolling_flow_pressure >= 0.15 and rolling_depth_imbalance_proxy <= -0.15",
        "SELL_PRESSURE_ABSORBED": "rolling_flow_pressure <= -0.15 and rolling_depth_imbalance_proxy >= 0.15",
        "FLOW_AND_DEPTH_ALIGNED_UP": "rolling_flow_pressure >= 0.15 and rolling_depth_imbalance_proxy >= 0.15",
        "FLOW_AND_DEPTH_ALIGNED_DOWN": "rolling_flow_pressure <= -0.15 and rolling_depth_imbalance_proxy <= -0.15",
        "MIXED_OR_NOISY": "small or mixed flow/depth proxy state",
        "INSUFFICIENT_DATA": "missing flow or depth proxy state",
    }
    return definitions.get(category, "")


def sign_audit_result(category: str, latest_effect: float | None, holdout_effect: float | None) -> dict[str, str]:
    latest_sign = sign_of(latest_effect)
    holdout_sign = sign_of(holdout_effect)
    label_sign = base.DIRECTION_BY_CATEGORY.get(category, 0)
    if latest_sign and holdout_sign and latest_sign == holdout_sign:
        holdout_vs_latest = "CONSISTENT"
    elif latest_sign and holdout_sign:
        holdout_vs_latest = "INVERTED"
    else:
        holdout_vs_latest = "ZERO_OR_UNAVAILABLE"

    if label_sign and holdout_sign and label_sign == holdout_sign:
        vs_label = "MATCHES_CATEGORY_LABEL_PROXY_DIRECTION"
    elif label_sign and holdout_sign:
        vs_label = "INVERTED_VS_CATEGORY_LABEL_PROXY_DIRECTION"
    else:
        vs_label = "CATEGORY_NAME_AMBIGUOUS_OR_ZERO_PROXY_DIRECTION"

    if category == "FLOW_AND_DEPTH_ALIGNED_DOWN":
        sanity = (
            "CATEGORY_NAME_AMBIGUOUS: the DOWN label describes contemporaneous negative flow and depth "
            "alignment, while positive forward proxy means depth imbalance moved upward toward bid-side dominance."
        )
    elif vs_label.startswith("INVERTED"):
        sanity = "INVERTED_VS_CATEGORY_LABEL_PROXY_DIRECTION"
    elif holdout_vs_latest == "CONSISTENT":
        sanity = "CONSISTENT_WINDOW_SIGN_PROXY_ONLY"
    else:
        sanity = "INCONSISTENT_WINDOW_SIGN_PROXY_ONLY"
    return {
        "category_label_proxy_direction": "POSITIVE" if label_sign > 0 else "NEGATIVE" if label_sign < 0 else "NEUTRAL",
        "latest_effect_sign": sign_text(latest_effect),
        "holdout_effect_sign": sign_text(holdout_effect),
        "holdout_vs_latest_sign": holdout_vs_latest,
        "effect_sign_vs_category_label": vs_label,
        "sign_sanity_result": sanity,
    }


def write_outputs(
    summary: dict[str, Any],
    comparison_rows: list[dict[str, Any]],
    sign_rows: list[dict[str, Any]],
    stability_rows: list[dict[str, Any]],
) -> None:
    with CANDIDATE_COMPARISON_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=comparison_fieldnames())
        writer.writeheader()
        writer.writerows(comparison_rows)
    with SIGN_AUDIT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=sign_audit_fieldnames())
        writer.writeheader()
        writer.writerows(sign_rows)
    with STABILITY_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=stability_fieldnames())
        writer.writeheader()
        writer.writerows(stability_rows)

    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_summary_md(summary, comparison_rows, sign_rows)
    summary["output_sizes_bytes"] = {
        path.name: path.stat().st_size
        for path in [SUMMARY_JSON, SUMMARY_MD, CANDIDATE_COMPARISON_CSV, SIGN_AUDIT_CSV, STABILITY_CSV]
        if path.exists()
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_summary_md(summary: dict[str, Any], comparison_rows: list[dict[str, Any]], sign_rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Orderbook UM 81 streaming absorption discovery holdout 90d v1",
        "",
        f"status: {summary['status']}",
        f"runtime_seconds: {summary['runtime_seconds']}",
        f"processed_symbol_days: {summary['processed_symbol_days']}",
        f"failed_symbol_days: {summary['failed_symbol_days']}",
        f"survived_candidates: {', '.join(summary['survived_candidates'])}",
        f"failed_candidates: {', '.join(summary['failed_candidates'])}",
        f"row_level_dataset_created: {str(summary['row_level_dataset_created']).lower()}",
        f"parquet_dataset_created: {str(summary['parquet_dataset_created']).lower()}",
        "",
        "## Candidate Comparison",
        "| rank | category | horizon_seconds | latest_effect_size | holdout_effect_size | status |",
        "| ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for row in comparison_rows:
        lines.append(
            "| "
            f"{row['candidate_rank']} | {row['category']} | {row['horizon_seconds']} | "
            f"{row['latest_effect_size_vs_null']} | {row['holdout_effect_size_vs_null']} | "
            f"{row['holdout_status']} |"
        )
    lines.extend(["", "## Sign Audit"])
    for row in sign_rows:
        lines.append(
            "- "
            f"{row['category']} @ {row['horizon_seconds']}s: {row['holdout_vs_latest_sign']}; "
            f"{row['sign_sanity_result']}"
        )
    lines.append("")
    lines.append("Positive proxy means the rolling bid-vs-ask depth imbalance proxy increased; it is not a price-return statement.")
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_holdout() -> dict[str, Any]:
    started = time.monotonic()
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    if base.path_is_inside(base.DEFAULT_BOOKDEPTH_RAW_ROOT, REPO_ROOT) or base.path_is_inside(base.DEFAULT_AGGTRADES_RAW_ROOT, REPO_ROOT):
        raise RuntimeError("raw ZIP roots must stay outside repo")

    latest_candidates = load_latest_candidates()
    pairs, window_metadata = build_holdout_pairs()
    selected_symbols = sorted({str(pair["symbol"]) for pair in pairs})

    vol_by_pair, volatility_threshold, volatility_metadata = base.compute_day_volatility_threshold(pairs)
    category_horizon: dict[tuple[str, int], base.DistributionStats] = {}
    horizon_null: dict[int, base.MomentStats] = defaultdict(base.MomentStats)
    stability: dict[tuple[str, str, str, str, int], base.MomentStats] = defaultdict(base.MomentStats)

    processed_symbol_days = 0
    failed_symbol_days = 0
    total_feature_rows_seen = 0
    total_horizon_observations = 0
    valid_forward_observations = 0
    category_counts_total: Counter[str] = Counter()
    failure_examples: list[dict[str, str]] = []
    next_progress = time.monotonic() + PROGRESS_INTERVAL_SECONDS

    for pair in pairs:
        try:
            result = base.aggregate_pair(pair, vol_by_pair, volatility_threshold, category_horizon, horizon_null, stability)
            processed_symbol_days += 1
            total_feature_rows_seen += int(result["row_count"])
            total_horizon_observations += int(result["observation_count"])
            valid_forward_observations += int(result["valid_forward_count"])
            category_counts_total.update(result["category_counts"])
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
                "progress phase=holdout_discovery "
                f"processed_symbol_days={processed_symbol_days}/{len(pairs)} "
                f"failed_symbol_days={failed_symbol_days} "
                f"feature_rows={total_feature_rows_seen} "
                f"valid_forward_observations={valid_forward_observations} "
                f"elapsed_seconds={round(time.monotonic() - started, 1)}",
                flush=True,
            )
            next_progress = time.monotonic() + PROGRESS_INTERVAL_SECONDS

    comparison_rows: list[dict[str, Any]] = []
    sign_rows: list[dict[str, Any]] = []
    stability_rows: list[dict[str, Any]] = []
    survived_candidates: list[str] = []
    failed_candidates: list[str] = []

    for rank, (category, horizon) in enumerate(PREVIOUS_CANDIDATES, start=1):
        latest = latest_candidates[(category, horizon)]
        holdout = compute_metric_row(category, horizon, category_horizon, horizon_null, stability)
        latest_effect = float_or_none(latest.get("effect_vs_null"))
        latest_effect_size = float_or_none(latest.get("effect_size_vs_null"))
        holdout_effect_size = float_or_none(holdout.get("effect_size_vs_null"))
        status = survival_status(latest_effect, holdout)
        label = f"{category}@{horizon}s"
        if status == "SURVIVED_HOLDOUT":
            survived_candidates.append(label)
        else:
            failed_candidates.append(label)
        comparison_rows.append(
            {
                "candidate_rank": rank,
                "category": category,
                "horizon_seconds": horizon,
                "latest_valid_forward_count": latest.get("valid_forward_count", ""),
                "holdout_valid_forward_count": holdout["valid_forward_count"],
                "latest_mean_forward_proxy_return": latest.get("mean_forward_proxy_return", ""),
                "holdout_mean_forward_proxy_return": rounded(holdout["mean_forward_proxy_return"]),
                "latest_null_mean_forward_proxy_return": latest.get("null_mean_forward_proxy_return", ""),
                "holdout_null_mean_forward_proxy_return": rounded(holdout["null_mean_forward_proxy_return"]),
                "latest_effect_vs_null": latest.get("effect_vs_null", ""),
                "holdout_effect_vs_null": rounded(holdout["effect_vs_null"]),
                "latest_effect_size_vs_null": latest.get("effect_size_vs_null", ""),
                "holdout_effect_size_vs_null": rounded(holdout_effect_size, 8),
                "effect_size_retention_ratio": rounded(safe_div(abs(holdout_effect_size) if holdout_effect_size is not None else None, abs(latest_effect_size) if latest_effect_size is not None else None), 8),
                "latest_directional_diagnostic_rate": latest.get("directional_diagnostic_rate", ""),
                "holdout_directional_diagnostic_rate": rounded(holdout["directional_diagnostic_rate"], 6),
                "latest_symbol_stability_rate": latest.get("symbol_stability_rate", ""),
                "holdout_symbol_stability_rate": rounded(holdout["symbol_stability_rate"], 6),
                "latest_month_stability_rate": latest.get("month_stability_rate", ""),
                "holdout_month_stability_rate": rounded(holdout["month_stability_rate"], 6),
                "latest_week_stability_rate": latest.get("week_stability_rate", ""),
                "holdout_week_stability_rate": rounded(holdout["week_stability_rate"], 6),
                "holdout_status": status,
            }
        )
        for period_type, prefix in [("SYMBOL", "symbol"), ("MONTH", "month"), ("WEEK", "week")]:
            stability_rows.append(
                {
                    "candidate_rank": rank,
                    "category": category,
                    "horizon_seconds": horizon,
                    "period_type": period_type,
                    "support_count": holdout.get(f"{prefix}_support_count", 0),
                    "consistent_count": holdout.get(f"{prefix}_consistent_count", 0),
                    "stability_rate": rounded(holdout.get(f"{prefix}_stability_rate"), 6),
                }
            )
        audit = sign_audit_result(category, latest_effect, holdout.get("effect_vs_null"))
        sign_rows.append(
            {
                "candidate_rank": rank,
                "category": category,
                "horizon_seconds": horizon,
                "forward_proxy_return_definition": "future rolling depth-imbalance proxy minus current rolling depth-imbalance proxy",
                "positive_proxy_means": "rolling bid-vs-ask depth imbalance proxy increased; not a verified price-up movement",
                "category_definition": category_definition(category),
                **audit,
            }
        )

    categories_found = [category for category in base.CATEGORIES if category_counts_total.get(category, 0) > 0]
    status = (
        "PASS_ORDERBOOK_UM_81_STREAMING_ABSORPTION_DISCOVERY_HOLDOUT_90D_COMPLETED"
        if processed_symbol_days > 0
        and failed_symbol_days == 0
        and len(selected_symbols) == EXPECTED_SYMBOL_COUNT
        and not window_metadata["incomplete_symbols"]
        else "PARTIAL_ORDERBOOK_UM_81_STREAMING_ABSORPTION_DISCOVERY_HOLDOUT_90D_COMPLETED"
    )
    runtime_seconds = round(time.monotonic() - started, 3)
    summary: dict[str, Any] = {
        "status": status,
        "created_at_utc": utc_now_text(),
        "task": "ORDERBOOK_UM_81_STREAMING_ABSORPTION_DISCOVERY_HOLDOUT_90D_V1",
        "mode": "DISJOINT_PREVIOUS_90D_HOLDOUT",
        "raw_bookdepth_root": str(base.DEFAULT_BOOKDEPTH_RAW_ROOT),
        "raw_aggtrades_root": str(base.DEFAULT_AGGTRADES_RAW_ROOT),
        "raw_roots_outside_repo": True,
        "selected_symbol_count": len(selected_symbols),
        "selected_symbols": selected_symbols,
        "latest_window_days_skipped_per_symbol": LATEST_WINDOW_DAYS_PER_SYMBOL,
        "holdout_days_per_symbol": HOLDOUT_DAYS_PER_SYMBOL,
        "selected_symbol_days": len(pairs),
        "processed_symbol_days": processed_symbol_days,
        "failed_symbol_days": failed_symbol_days,
        "failure_examples": failure_examples,
        "runtime_seconds": runtime_seconds,
        "horizon_seconds": base.HORIZON_SECONDS,
        "categories_expected": base.CATEGORIES,
        "categories_found": categories_found,
        "category_counts_total": dict(category_counts_total),
        "total_feature_rows_seen": total_feature_rows_seen,
        "total_horizon_observations": total_horizon_observations,
        "valid_forward_observations": valid_forward_observations,
        "previous_candidates": [f"{category}@{horizon}s" for category, horizon in PREVIOUS_CANDIDATES],
        "survived_candidates": survived_candidates,
        "failed_candidates": failed_candidates,
        "candidate_comparison": comparison_rows,
        "sign_audit": sign_rows,
        "forward_proxy_return_definition": "future rolling depth-imbalance proxy minus current rolling depth-imbalance proxy",
        "sign_convention": "positive proxy means rolling bid-vs-ask depth imbalance proxy increased; it is not a verified price-up movement",
        "row_level_dataset_created": False,
        "parquet_dataset_created": False,
        "downloads_run": False,
        "outputs": {
            "summary_json": str(SUMMARY_JSON),
            "summary_md": str(SUMMARY_MD),
            "candidate_comparison_csv": str(CANDIDATE_COMPARISON_CSV),
            "sign_audit_csv": str(SIGN_AUDIT_CSV),
            "stability_csv": str(STABILITY_CSV),
        },
        **window_metadata,
        **volatility_metadata,
    }
    write_outputs(summary, comparison_rows, sign_rows, stability_rows)
    return json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))


def main() -> int:
    try:
        summary = run_holdout()
    except Exception as exc:  # noqa: BLE001
        error_summary = {
            "status": "FAILED_ORDERBOOK_UM_81_STREAMING_ABSORPTION_DISCOVERY_HOLDOUT_90D",
            "created_at_utc": utc_now_text(),
            "error": f"{type(exc).__name__}: {exc}",
            "row_level_dataset_created": False,
            "parquet_dataset_created": False,
            "downloads_run": False,
        }
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        SUMMARY_JSON.write_text(json.dumps(error_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        SUMMARY_MD.write_text(
            "# Orderbook UM 81 streaming absorption discovery holdout 90d v1\n\n"
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
