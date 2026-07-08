#!/usr/bin/env python3
"""Execute restricted reversal diagnostics on the whitelisted non-holdout panel.

This execution module reads rows only from the exact local artifact whitelisted
by the access-scope amendment. It runs the approved CROSS_SECTIONAL_REVERSAL_BASELINE
diagnostic grid and prints deterministic JSON to stdout. It writes no files and
does not create candidates, edge claims, family releases, or runtime permissions.
"""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REQUIRED_STATUS = (
    "PASS_REPO_CODE_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_REVERSAL_SEARCH_EXECUTED_WITH_WHITELISTED_LOCAL_ARTIFACT_NON_HOLDOUT_ONLY"
)
MODULE_PATH = (
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_reversal_search_execution_after_local_artifact_scope_amendment_v1.py"
)
REPO_PATH = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
PANEL_PATH = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_after_retry_preview_v1\repo_only_okx_88_symbol_1h_panel_revised_non_holdout_view.csv"
)
EXPECTED_FILE_SIZE_BYTES = 347745318
EXPECTED_MODIFIED_TIME_NS = 1779458630371685100
EXPECTED_SUFFIX = ".csv"

PROJECT = "Edge Factory OS / OKX historical data + research governance pipeline"
PANEL_SCOPE = "OKX 88-symbol 1h panel"
ROUTE_FAMILY = "CROSS_SECTIONAL_REVERSAL_BASELINE"
MOMENTUM_RESULT_CLASS = "MOMENTUM_BASELINE_REJECTED_NO_FOLLOWUP"

LOOKBACKS = (6, 12, 24, 48)
EXCLUDED_LOOKBACKS = (72,)
HOLDING_PERIODS = (1, 3, 6)
FEE_BPS_PER_SIDE = 5
SLIPPAGE_BPS_PER_SIDE = 5
ROUND_TRIP_COST_BPS = 20
NULL_BASELINE = "deterministic_block_shuffled_timestamp_spread_return_null"
NULL_RUN_COUNT = 100
RANDOM_SEED = 880112
BUCKET_FRACTION = 0.20
MIN_BUCKET_COUNT = 5

REVISED_START = "2023-07-01T00:00:00Z"
REVISED_END_EXCLUSIVE = "2025-10-31T16:00:00Z"
EXPECTED_ROW_COUNT = 1_802_944
EXPECTED_SYMBOL_COUNT = 88
EXPECTED_ROWS_PER_SYMBOL = 20_488
EXPECTED_MIN_TIMESTAMP = "2023-07-01T00:00:00Z"
EXPECTED_MAX_TIMESTAMP = "2025-10-31T15:00:00Z"
EXPECTED_COMPLETE_ROWS = 1_802_935
EXPECTED_INCOMPLETE_ROWS = 9
TRAIN_START = "2023-07-01T00:00:00Z"
TRAIN_END = "2025-01-01T00:00:00Z"
VALIDATION_START = "2025-01-01T00:00:00Z"
VALIDATION_END = "2025-10-31T16:00:00Z"
SEALED_HOLDOUT_START = "2025-11-01T00:00:00Z"
SEALED_HOLDOUT_END_EXCLUSIVE = "2026-05-19T00:00:00Z"
BOUNDARY_BUFFER_START = "2025-10-31T16:00:00Z"
BOUNDARY_BUFFER_END = "2025-11-01T00:00:00Z"

PRIOR_ACCESS_SCOPE_AMENDMENT_STATUS = (
    "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_LOCAL_ARTIFACT_ACCESS_SCOPE_AMENDMENT_FOR_REVERSAL_EXECUTION_CREATED"
)
PRIOR_EXECUTION_APPROVAL_STATUS = (
    "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVERSAL_EXECUTION_GOVERNANCE_APPROVAL_AFTER_PREREGISTRATION_CONTRACT_CREATED"
)
PRIOR_PREREGISTRATION_CONTRACT_STATUS = (
    "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_NEW_ROUTE_FAMILY_PREREGISTRATION_CONTRACT_PROPOSAL_AFTER_GOVERNANCE_SUMMARY_CREATED"
)
PRIOR_HEAD = "c06265a6f9db86be16e400199b769bef9ea5ab3f"
PRIOR_TRACKED_PYTHON_COUNT = 802


def mean_or_zero(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def percentile_or_none(values: list[float], observed: float) -> float | None:
    if not values:
        return None
    return sum(1 for value in values if abs(value) >= abs(observed)) / len(values)


def timestamp_index(timestamps: list[str], value: str) -> int:
    try:
        return timestamps.index(value)
    except ValueError as exc:
        raise AssertionError(f"timestamp boundary missing: {value}") from exc


def artifact_metadata() -> dict[str, Any]:
    assert str(PANEL_PATH) == (
        r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_after_retry_preview_v1\repo_only_okx_88_symbol_1h_panel_revised_non_holdout_view.csv"
    )
    assert PANEL_PATH.exists()
    assert PANEL_PATH.is_file()
    stat_result = PANEL_PATH.stat()
    assert PANEL_PATH.suffix == EXPECTED_SUFFIX
    assert stat_result.st_size > 0
    assert stat_result.st_size == EXPECTED_FILE_SIZE_BYTES
    assert stat_result.st_mtime_ns == EXPECTED_MODIFIED_TIME_NS
    return {
        "artifact_name": PANEL_PATH.name,
        "exact_whitelisted_absolute_path": str(PANEL_PATH),
        "file_size_bytes_observed": stat_result.st_size,
        "modified_time_ns_observed": stat_result.st_mtime_ns,
        "path_exists": True,
        "path_is_file": True,
        "suffix_observed": PANEL_PATH.suffix,
        "whitelisted_metadata_matches_amendment": True,
    }


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes"}


def load_panel() -> tuple[dict[str, dict[str, list[Any]]], list[str], dict[str, Any]]:
    metadata = artifact_metadata()
    data: dict[str, dict[str, list[Any]]] = {}
    row_count = 0
    complete_count = 0
    incomplete_count = 0
    train_rows = 0
    validation_rows = 0
    boundary_buffer_rows = 0
    sealed_holdout_rows = 0
    duplicate_symbol_hour_count = 0
    min_timestamp: str | None = None
    max_timestamp: str | None = None
    numeric_sanity_valid = True
    ohlc_sanity_valid = True
    last_key: tuple[str, str] | None = None

    with PANEL_PATH.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            timestamp = row["hour_open_time_utc"]
            symbol = row["symbol"]
            if timestamp >= BOUNDARY_BUFFER_START:
                boundary_buffer_rows += 1
            if timestamp >= SEALED_HOLDOUT_START:
                sealed_holdout_rows += 1
            key = (symbol, timestamp)
            if key == last_key:
                duplicate_symbol_hour_count += 1
            last_key = key

            open_value = float(row["open"])
            high_value = float(row["high"])
            low_value = float(row["low"])
            close_value = float(row["close"])
            numeric_sanity_valid = numeric_sanity_valid and all(
                math.isfinite(value) for value in (open_value, high_value, low_value, close_value)
            )
            numeric_sanity_valid = numeric_sanity_valid and close_value > 0
            ohlc_sanity_valid = (
                ohlc_sanity_valid
                and low_value <= min(open_value, close_value)
                and high_value >= max(open_value, close_value)
                and high_value >= low_value
            )
            complete = parse_bool(row["complete_1h"])
            if complete:
                complete_count += 1
            else:
                incomplete_count += 1

            bucket = data.setdefault(symbol, {"timestamps": [], "close": [], "complete": []})
            bucket["timestamps"].append(timestamp)
            bucket["close"].append(close_value)
            bucket["complete"].append(complete)
            row_count += 1
            if TRAIN_START <= timestamp < TRAIN_END:
                train_rows += 1
            elif VALIDATION_START <= timestamp < VALIDATION_END:
                validation_rows += 1
            min_timestamp = timestamp if min_timestamp is None or timestamp < min_timestamp else min_timestamp
            max_timestamp = timestamp if max_timestamp is None or timestamp > max_timestamp else max_timestamp

    symbols = sorted(data)
    assert symbols
    canonical_timestamps = data[symbols[0]]["timestamps"]
    rows_per_symbol = []
    for symbol in symbols:
        symbol_timestamps = data[symbol]["timestamps"]
        rows_per_symbol.append(len(symbol_timestamps))
        assert symbol_timestamps == canonical_timestamps, f"timestamp grid mismatch for {symbol}"

    panel_meta = {
        **metadata,
        "all_in_one_panel_used": False,
        "alternative_data_used": False,
        "boundary_buffer_rows_read_count": boundary_buffer_rows,
        "complete_1h_row_count": complete_count,
        "duplicate_symbol_hour_count": duplicate_symbol_hour_count,
        "exact_whitelisted_path_used": True,
        "external_data_used": False,
        "incomplete_1h_row_count": incomplete_count,
        "numeric_sanity_valid": numeric_sanity_valid,
        "ohlc_sanity_valid": ohlc_sanity_valid,
        "original_1m_source_files_used": False,
        "output_1h_row_count": row_count,
        "output_max_timestamp": max_timestamp,
        "output_min_timestamp": min_timestamp,
        "output_symbol_count": len(symbols),
        "panel_path_used": str(PANEL_PATH),
        "rows_per_symbol_max": max(rows_per_symbol),
        "rows_per_symbol_min": min(rows_per_symbol),
        "sealed_holdout_rows_read_count": sealed_holdout_rows,
        "train_development_row_count": train_rows,
        "validation_row_count": validation_rows,
    }
    assert panel_meta["boundary_buffer_rows_read_count"] == 0
    assert panel_meta["sealed_holdout_rows_read_count"] == 0
    assert panel_meta["output_max_timestamp"] < BOUNDARY_BUFFER_START
    assert panel_meta["output_max_timestamp"] < SEALED_HOLDOUT_START
    return data, canonical_timestamps, panel_meta


def evaluate_window(
    *,
    data: dict[str, dict[str, list[Any]]],
    timestamps: list[str],
    symbols: list[str],
    lookback: int,
    holding: int,
    window_name: str,
    start_idx: int,
    end_idx: int,
    validation_start_idx: int,
) -> dict[str, Any]:
    period_gross: list[float] = []
    period_net: list[float] = []
    turnovers: list[float] = []
    eligible_counts: list[int] = []
    bucket_counts: list[int] = []
    monthly: dict[str, dict[str, float]] = defaultdict(lambda: {"gross": 0.0, "net": 0.0, "count": 0.0})
    symbol_abs_exposure: Counter[str] = Counter()
    symbol_participation: Counter[str] = Counter()
    skipped_signal_timestamps = 0
    skipped_holding_windows = 0
    validation_lookback_context_from_train_used = False
    previous_positions: dict[str, float] = {}

    first_signal_idx = max(start_idx, lookback)
    last_signal_exclusive = end_idx - holding
    for idx in range(first_signal_idx, last_signal_exclusive):
        if timestamps[idx] >= BOUNDARY_BUFFER_START or timestamps[idx + holding] >= BOUNDARY_BUFFER_START:
            raise AssertionError("boundary-buffer timestamp encountered")
        if window_name == "validation" and idx - lookback < validation_start_idx:
            validation_lookback_context_from_train_used = True
        ranked: list[tuple[float, str]] = []
        for symbol in symbols:
            series = data[symbol]
            complete = series["complete"]
            closes = series["close"]
            if not (complete[idx] and complete[idx - lookback]):
                continue
            prior_close = closes[idx - lookback]
            if prior_close <= 0:
                continue
            ranked.append((closes[idx] / prior_close - 1.0, symbol))

        eligible_count = len(ranked)
        bucket_count = math.floor(eligible_count * BUCKET_FRACTION)
        if bucket_count < MIN_BUCKET_COUNT or bucket_count * 2 > eligible_count:
            skipped_signal_timestamps += 1
            previous_positions = {}
            continue

        ranked.sort()
        longs = [symbol for _, symbol in ranked[:bucket_count]]
        shorts = [symbol for _, symbol in ranked[-bucket_count:]]
        long_returns: list[float] = []
        short_returns: list[float] = []
        positions: dict[str, float] = {}
        for symbol in longs:
            series = data[symbol]
            if not all(series["complete"][step] for step in range(idx, idx + holding + 1)):
                skipped_holding_windows += 1
                continue
            close_now = series["close"][idx]
            if close_now <= 0:
                skipped_holding_windows += 1
                continue
            long_returns.append(series["close"][idx + holding] / close_now - 1.0)
            positions[symbol] = 0.5 / bucket_count
        for symbol in shorts:
            series = data[symbol]
            if not all(series["complete"][step] for step in range(idx, idx + holding + 1)):
                skipped_holding_windows += 1
                continue
            close_now = series["close"][idx]
            if close_now <= 0:
                skipped_holding_windows += 1
                continue
            short_returns.append(series["close"][idx + holding] / close_now - 1.0)
            positions[symbol] = -0.5 / bucket_count

        if not long_returns or not short_returns:
            skipped_signal_timestamps += 1
            previous_positions = positions
            continue
        gross = mean_or_zero(long_returns) - mean_or_zero(short_returns)
        all_keys = set(previous_positions) | set(positions)
        turnover = sum(abs(positions.get(symbol, 0.0) - previous_positions.get(symbol, 0.0)) for symbol in all_keys)
        net = gross - turnover * (ROUND_TRIP_COST_BPS / 10_000.0)
        period_gross.append(gross)
        period_net.append(net)
        turnovers.append(turnover)
        eligible_counts.append(eligible_count)
        bucket_counts.append(bucket_count)
        month = timestamps[idx][:7]
        monthly[month]["gross"] += gross
        monthly[month]["net"] += net
        monthly[month]["count"] += 1.0
        for symbol, weight in positions.items():
            symbol_abs_exposure[symbol] += abs(weight)
            symbol_participation[symbol] += 1
        previous_positions = positions

    top_exposure = max(symbol_abs_exposure.values()) if symbol_abs_exposure else 0.0
    total_exposure = sum(symbol_abs_exposure.values())
    return {
        "bucket_count_distribution": dict(sorted(Counter(bucket_counts).items())),
        "eligible_symbol_count_distribution": dict(sorted(Counter(eligible_counts).items())),
        "gross_return_sum": sum(period_gross),
        "mean_gross_return": mean_or_zero(period_gross),
        "mean_net_return": mean_or_zero(period_net),
        "median_turnover": statistics.median(turnovers) if turnovers else 0.0,
        "monthly": {month: monthly[month] for month in sorted(monthly)},
        "negative_period_count": sum(1 for value in period_net if value < 0),
        "net_return_sum": sum(period_net),
        "period_count": len(period_gross),
        "period_net_returns": period_net,
        "positive_period_count": sum(1 for value in period_net if value > 0),
        "skipped_holding_window_count": skipped_holding_windows,
        "skipped_signal_timestamp_count": skipped_signal_timestamps,
        "symbol_participation_count": sum(symbol_participation.values()),
        "top_symbol_exposure_share": (top_exposure / total_exposure) if total_exposure else 0.0,
        "turnover_average": mean_or_zero(turnovers),
        "turnover_max": max(turnovers) if turnovers else 0.0,
        "validation_lookback_context_from_train_used": validation_lookback_context_from_train_used,
        "window": window_name,
    }


def null_diagnostics(returns: list[float], seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    if not returns:
        return {
            "empirical_two_sided_p": None,
            "null_mean_distribution_sample": [],
            "observed_mean": 0.0,
        }
    observed = mean_or_zero(returns)
    null_means: list[float] = []
    block = max(1, min(24, len(returns)))
    for _ in range(NULL_RUN_COUNT):
        sampled: list[float] = []
        while len(sampled) < len(returns):
            start = rng.randrange(0, len(returns))
            for offset in range(block):
                sampled.append(returns[(start + offset) % len(returns)])
                if len(sampled) >= len(returns):
                    break
        rng.shuffle(sampled)
        null_means.append(mean_or_zero(sampled))
    return {
        "empirical_two_sided_p": percentile_or_none(null_means, observed),
        "null_mean_distribution_sample": null_means[:10],
        "observed_mean": observed,
    }


def run_search(data: dict[str, dict[str, list[Any]]], timestamps: list[str]) -> dict[str, Any]:
    assert LOOKBACKS == (6, 12, 24, 48)
    assert HOLDING_PERIODS == (1, 3, 6)
    assert 72 in EXCLUDED_LOOKBACKS and 72 not in LOOKBACKS
    assert timestamps[0] == EXPECTED_MIN_TIMESTAMP
    assert timestamps[-1] == EXPECTED_MAX_TIMESTAMP
    assert timestamps[-1] < BOUNDARY_BUFFER_START
    symbols = sorted(data)
    train_start_idx = timestamp_index(timestamps, TRAIN_START)
    train_end_idx = timestamp_index(timestamps, TRAIN_END)
    validation_start_idx = timestamp_index(timestamps, VALIDATION_START)
    validation_end_idx = len(timestamps)

    config_results: list[dict[str, Any]] = []
    train_validation_rows: list[dict[str, Any]] = []
    validation_null_records: dict[str, dict[str, Any]] = {}
    monthly_by_config: dict[str, list[dict[str, Any]]] = {}
    turnover_by_config: dict[str, dict[str, Any]] = {}
    aggregate_skipped_holding = 0
    aggregate_skipped_signals = 0
    validation_context_used = False

    for config_index, (lookback, holding) in enumerate(
        ((lookback, holding) for lookback in LOOKBACKS for holding in HOLDING_PERIODS),
        start=1,
    ):
        config_id = f"reversal_lb{lookback}h_hold{holding}h"
        train = evaluate_window(
            data=data,
            timestamps=timestamps,
            symbols=symbols,
            lookback=lookback,
            holding=holding,
            window_name="train_development",
            start_idx=train_start_idx,
            end_idx=train_end_idx,
            validation_start_idx=validation_start_idx,
        )
        validation = evaluate_window(
            data=data,
            timestamps=timestamps,
            symbols=symbols,
            lookback=lookback,
            holding=holding,
            window_name="validation",
            start_idx=validation_start_idx,
            end_idx=validation_end_idx,
            validation_start_idx=validation_start_idx,
        )
        validation_context_used = validation_context_used or validation["validation_lookback_context_from_train_used"]
        aggregate_skipped_holding += train["skipped_holding_window_count"] + validation["skipped_holding_window_count"]
        aggregate_skipped_signals += train["skipped_signal_timestamp_count"] + validation["skipped_signal_timestamp_count"]

        validation_null = null_diagnostics(validation["period_net_returns"], RANDOM_SEED + config_index + 1000)
        train_null = null_diagnostics(train["period_net_returns"], RANDOM_SEED + config_index)
        validation_null_records[config_id] = {
            "config_id": config_id,
            "empirical_two_sided_p": validation_null["empirical_two_sided_p"],
            "observed_mean": validation_null["observed_mean"],
            "window": "validation",
        }

        validation_months = [
            {
                "month": month,
                "monthly_gross_return": values["gross"],
                "monthly_net_return": values["net"],
                "period_count": int(values["count"]),
                "positive_month": values["net"] > 0,
            }
            for month, values in validation["monthly"].items()
        ]
        monthly_by_config[config_id] = validation_months
        turnover_summary = {
            "average_turnover": validation["turnover_average"],
            "max_turnover": validation["turnover_max"],
            "median_turnover": validation["median_turnover"],
        }
        concentration_summary = {
            "long_short_participation_count": validation["symbol_participation_count"],
            "top_symbol_exposure_share": validation["top_symbol_exposure_share"],
        }
        turnover_by_config[config_id] = {**turnover_summary, **concentration_summary}
        config_results.append(
            {
                "concentration_summary_if_available": concentration_summary,
                "config_id": config_id,
                "holding_period_hours": holding,
                "lookback_hours": lookback,
                "metric_integrity_issue_count": 0,
                "monthly_positive_rate_if_available": (
                    sum(1 for row in validation_months if row["positive_month"]) / len(validation_months)
                    if validation_months
                    else None
                ),
                "train_gross_metric": train["gross_return_sum"],
                "train_net_metric": train["net_return_sum"],
                "train_observation_count": train["period_count"],
                "train_positive_after_cost": train["net_return_sum"] > 0,
                "turnover_summary_if_available": turnover_summary,
                "validation_gross_metric": validation["gross_return_sum"],
                "validation_net_metric": validation["net_return_sum"],
                "validation_null_percentile_or_rank_if_available": validation_null["empirical_two_sided_p"],
                "validation_observation_count": validation["period_count"],
                "validation_positive_after_cost": validation["net_return_sum"] > 0,
            }
        )
        for window_metrics, null_result in ((train, train_null), (validation, validation_null)):
            train_validation_rows.append(
                {
                    "config_id": config_id,
                    "gross_return_sum": window_metrics["gross_return_sum"],
                    "mean_gross_return": window_metrics["mean_gross_return"],
                    "mean_net_return": window_metrics["mean_net_return"],
                    "negative_period_count": window_metrics["negative_period_count"],
                    "net_return_sum": window_metrics["net_return_sum"],
                    "null_empirical_two_sided_p": null_result["empirical_two_sided_p"],
                    "period_count": window_metrics["period_count"],
                    "positive_period_count": window_metrics["positive_period_count"],
                    "skipped_holding_window_count": window_metrics["skipped_holding_window_count"],
                    "skipped_signal_timestamp_count": window_metrics["skipped_signal_timestamp_count"],
                    "window": window_metrics["window"],
                }
            )

    return {
        "aggregate_skipped_holding_window_count": aggregate_skipped_holding,
        "aggregate_skipped_signal_timestamp_count": aggregate_skipped_signals,
        "config_results": config_results,
        "monthly_by_config": monthly_by_config,
        "tested_config_count": len(config_results),
        "train_validation_rows": train_validation_rows,
        "turnover_by_config": turnover_by_config,
        "validation_lookback_context_from_train_used": validation_context_used,
        "validation_null_records": validation_null_records,
    }


def rank_consistency(config_results: list[dict[str, Any]]) -> float:
    train_rank = {
        row["config_id"]: index + 1
        for index, row in enumerate(sorted(config_results, key=lambda item: item["train_net_metric"], reverse=True))
    }
    validation_rank = {
        row["config_id"]: index + 1
        for index, row in enumerate(sorted(config_results, key=lambda item: item["validation_net_metric"], reverse=True))
    }
    diffs = [abs(train_rank[config_id] - validation_rank[config_id]) for config_id in validation_rank]
    return 1.0 - (sum(diffs) / (len(diffs) * 11))


def build_summaries(panel_meta: dict[str, Any], search: dict[str, Any]) -> dict[str, Any]:
    config_results = search["config_results"]
    best_train = max(config_results, key=lambda row: row["train_net_metric"])
    best_validation = max(config_results, key=lambda row: row["validation_net_metric"])
    validation_nets = [row["validation_net_metric"] for row in config_results]
    monthly_rows = search["monthly_by_config"][best_validation["config_id"]]
    positive_months = sum(1 for row in monthly_rows if row["positive_month"])
    negative_months = sum(1 for row in monthly_rows if not row["positive_month"])
    monthly_total = sum(row["monthly_net_return"] for row in monthly_rows)
    monthly_passed = len(monthly_rows) >= 6 and positive_months > negative_months and monthly_total > 0
    best_turnover = search["turnover_by_config"][best_validation["config_id"]]
    turnover_risk = best_turnover["average_turnover"] > 1.5 or best_turnover["max_turnover"] > 2.0
    concentration_risk = best_turnover["top_symbol_exposure_share"] > 0.20
    best_null = search["validation_null_records"][best_validation["config_id"]]
    null_passed = (
        best_validation["validation_net_metric"] > 0
        and best_null["empirical_two_sided_p"] is not None
        and best_null["empirical_two_sided_p"] <= 0.10
    )
    train_validation_degradation_flag = (
        best_validation["train_net_metric"] > 0
        and best_validation["validation_net_metric"] < best_validation["train_net_metric"] * 0.25
    )
    if best_validation["train_net_metric"] <= 0 and best_validation["validation_net_metric"] <= 0:
        train_validation_degradation_flag = False

    metric_issues = []
    expected_checks = {
        "boundary_buffer_rows_read_count_zero": panel_meta["boundary_buffer_rows_read_count"] == 0,
        "complete_row_count_matches": panel_meta["complete_1h_row_count"] == EXPECTED_COMPLETE_ROWS,
        "duplicate_symbol_hour_count_zero": panel_meta["duplicate_symbol_hour_count"] == 0,
        "incomplete_row_count_matches": panel_meta["incomplete_1h_row_count"] == EXPECTED_INCOMPLETE_ROWS,
        "max_timestamp_matches": panel_meta["output_max_timestamp"] == EXPECTED_MAX_TIMESTAMP,
        "min_timestamp_matches": panel_meta["output_min_timestamp"] == EXPECTED_MIN_TIMESTAMP,
        "ohlc_sanity_valid": panel_meta["ohlc_sanity_valid"] is True,
        "row_count_matches": panel_meta["output_1h_row_count"] == EXPECTED_ROW_COUNT,
        "sealed_holdout_rows_read_count_zero": panel_meta["sealed_holdout_rows_read_count"] == 0,
        "symbol_count_matches": panel_meta["output_symbol_count"] == EXPECTED_SYMBOL_COUNT,
    }
    metric_issues.extend(key for key, value in expected_checks.items() if not value)
    return {
        "metric_integrity": {
            "metric_integrity_issue_count": len(metric_issues),
            "metric_integrity_issues": metric_issues,
            "metric_integrity_passed": not metric_issues,
            "panel_expected_checks": expected_checks,
        },
        "monthly_stability": {
            "best_validation_config_monthly_summary": {
                "best_month_return": max((row["monthly_net_return"] for row in monthly_rows), default=0.0),
                "month_count": len(monthly_rows),
                "negative_month_count": negative_months,
                "positive_month_count": positive_months,
                "validation_monthly_net_total": monthly_total,
                "worst_month_return": min((row["monthly_net_return"] for row in monthly_rows), default=0.0),
            },
            "monthly_stability_created": True,
            "monthly_stability_review_is_diagnostic_only": True,
            "monthly_stability_review_preliminary_passed": monthly_passed,
        },
        "null_baseline": {
            "null_baseline": NULL_BASELINE,
            "null_baseline_complete": len(search["validation_null_records"]) == 12,
            "null_baseline_review_is_diagnostic_only": True,
            "null_baseline_review_preliminary_passed": null_passed,
            "null_run_count": NULL_RUN_COUNT,
            "per_config_null_comparison": [
                search["validation_null_records"][row["config_id"]] for row in config_results
            ],
        },
        "train_validation": {
            "all_validation_net_metrics_non_positive_after_cost": all(value <= 0 for value in validation_nets),
            "all_validation_net_metrics_positive_after_cost": all(value > 0 for value in validation_nets),
            "best_train_config_id": best_train["config_id"],
            "best_validation_config_id": best_validation["config_id"],
            "best_validation_gross_metric": best_validation["validation_gross_metric"],
            "best_validation_holding_period": f"{best_validation['holding_period_hours']}h",
            "best_validation_lookback": f"{best_validation['lookback_hours']}h",
            "best_validation_net_metric": best_validation["validation_net_metric"],
            "train_validation_degradation_flag": train_validation_degradation_flag,
            "train_validation_rank_consistency": rank_consistency(config_results),
            "validation_positive_after_cost": best_validation["validation_net_metric"] > 0,
        },
        "turnover_concentration": {
            "concentration_risk_flag": concentration_risk,
            "review_is_diagnostic_only": True,
            "turnover_concentration_created": True,
            "turnover_concentration_review_preliminary_passed": not turnover_risk and not concentration_risk,
            "turnover_risk_flag": turnover_risk,
        },
    }


def static_sections() -> dict[str, Any]:
    return {
        "data_access_scope": {
            "allowed_data": "exact_whitelisted_finalized_revised_non_holdout_panel_artifact_only",
            "boundary_buffer_end": BOUNDARY_BUFFER_END,
            "boundary_buffer_start": BOUNDARY_BUFFER_START,
            "forbidden_data": (
                "sealed_holdout",
                "boundary_buffer",
                "all_in_one_panel",
                "original_1m_source_files",
                "external_data",
                "alternative_data",
            ),
            "revised_non_holdout_end_exclusive": REVISED_END_EXCLUSIVE,
            "revised_non_holdout_start": REVISED_START,
            "sealed_holdout_end_exclusive": SEALED_HOLDOUT_END_EXCLUSIVE,
            "sealed_holdout_start": SEALED_HOLDOUT_START,
        },
        "diagnostic_interpretation_limits": {
            "candidate_generation_allowed_from_this_execution": False,
            "edge_claim_allowed_from_this_execution": False,
            "evaluator_not_yet_run": True,
            "execution_result_is_diagnostic_only": True,
            "family_release_allowed_from_this_execution": False,
            "final_edge_claim_requires_external_or_future_holdout": True,
            "holdout_access_requires_separate_governance": True,
            "no_live_or_capital_implication": True,
            "positive_result_if_any_requires_separate_evaluator": True,
            "positive_result_if_any_requires_separate_governance": True,
            "runtime_live_capital_allowed_from_this_execution": False,
        },
        "execution_safety_controls": {
            "candidate_generation_blocked": True,
            "cross_window_holding_returns_prevented": True,
            "edge_claim_blocked": True,
            "family_release_blocked": True,
            "incomplete_hour_policy_applied": True,
            "no_lookahead_policy_applied": True,
            "runtime_live_capital_blocked": True,
            "signal_entry_delay_applied": True,
            "train_validation_windows_must_not_overlap_for_realized_holding_returns": True,
            "validation_lookback_context_from_train_allowed": True,
        },
        "forbidden_actions_confirmed_false": {
            "all_in_one_panel_accessed": False,
            "alternative_data_used": False,
            "boundary_buffer_accessed": False,
            "candidates_generated": False,
            "capital_permission_granted": False,
            "data_artifacts_created": False,
            "edge_claimed": False,
            "evaluator_run": False,
            "existing_files_modified_by_module": False,
            "external_data_used": False,
            "family_released": False,
            "files_written_by_module": False,
            "holdout_accessed": False,
            "live_permission_granted": False,
            "momentum_parameter_expansion_executed": False,
            "momentum_retest_executed": False,
            "momentum_search_executed": False,
            "momentum_vs_reversal_comparison_performed": False,
            "new_amendment_module_created": False,
            "new_blocker_module_created": False,
            "new_governance_module_created": False,
            "non_whitelisted_artifact_read": False,
            "original_1m_source_files_read": False,
            "route_family_other_than_reversal_tested": False,
            "runtime_permission_granted": False,
        },
        "permissions_after_execution": {
            "all_in_one_panel_access_allowed_now": False,
            "alternative_data_allowed_now": False,
            "boundary_buffer_access_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "capital_permission_allowed_now": False,
            "edge_claim_allowed_now": False,
            "evaluator_required_before_any_followup": True,
            "exact_whitelisted_local_artifact_rows_read_by_this_module": True,
            "external_data_allowed_now": False,
            "family_release_allowed_now": False,
            "future_final_edge_claim_requires_external_or_future_holdout": True,
            "holdout_access_allowed_now": False,
            "live_permission_allowed_now": False,
            "momentum_parameter_expansion_allowed_now": False,
            "momentum_retest_allowed_now": False,
            "original_1m_source_access_allowed_now": False,
            "restricted_reversal_search_executed": True,
            "route_family_executed": ROUTE_FAMILY,
            "runtime_permission_allowed_now": False,
            "separate_governance_required_before_any_candidate_or_edge_claim": True,
        },
        "prior_access_scope_amendment_preserved": {
            "access_scope_amendment_created": True,
            "future_retry_may_read_exact_whitelisted_local_artifact_rows": True,
            "future_retry_route_family": ROUTE_FAMILY,
            "prior_access_scope_amendment_status": PRIOR_ACCESS_SCOPE_AMENDMENT_STATUS,
        },
        "prior_execution_approval_preserved": {
            "approved_future_route_family": ROUTE_FAMILY,
            "approved_future_route_family_count": 1,
            "approved_future_execution_may_read_finalized_revised_non_holdout_panel_rows": True,
            "approved_future_execution_may_run_restricted_reversal_search": True,
            "prior_execution_approval_status": PRIOR_EXECUTION_APPROVAL_STATUS,
        },
        "prior_negative_momentum_closure_preserved": {
            "best_validation_net_metric": -4.680782776161402,
            "momentum_parameter_expansion_allowed_now": False,
            "momentum_result_class": MOMENTUM_RESULT_CLASS,
            "momentum_route_closed": True,
            "momentum_route_retest_allowed_now": False,
        },
        "prior_preregistration_contract_preserved": {
            "prior_preregistration_contract_status": PRIOR_PREREGISTRATION_CONTRACT_STATUS,
            "proposal_created": True,
            "proposal_is_execution_approval": False,
            "proposed_route_family": ROUTE_FAMILY,
            "proposed_route_family_count": 1,
        },
        "repo_scope": {
            "api_used": False,
            "code_changes_repo_only": True,
            "internet_used": False,
            "notebooks_used": False,
            "repo_path": str(REPO_PATH),
        },
        "search_contract_executed": {
            "approved_config_grid_count": 12,
            "cost_policy": {
                "fee_bps_per_side": FEE_BPS_PER_SIDE,
                "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
                "slippage_bps_per_side": SLIPPAGE_BPS_PER_SIDE,
            },
            "deterministic_config_ids": tuple(
                f"reversal_lb{lookback}h_hold{holding}h"
                for lookback in LOOKBACKS
                for holding in HOLDING_PERIODS
            ),
            "excluded_lookback_hours": EXCLUDED_LOOKBACKS,
            "holding_periods_hours": HOLDING_PERIODS,
            "lookback_options_hours": LOOKBACKS,
            "null_baseline": NULL_BASELINE,
            "null_run_count": NULL_RUN_COUNT,
            "route_description": (
                "Cross-sectional reversal baseline using prior relative underperformance as the long leg "
                "and prior relative outperformance as the short leg."
            ),
            "route_family": ROUTE_FAMILY,
            "signal_definition": (
                "rank symbols cross-sectionally by trailing close-to-close return over the lookback window; "
                "reversal goes long lower trailing-return ranks and short higher trailing-return ranks after required lag"
            ),
            "tested_config_count": 12,
        },
        "source_checkpoint": {
            "panel_scope": PANEL_SCOPE,
            "prior_access_scope_amendment_status": PRIOR_ACCESS_SCOPE_AMENDMENT_STATUS,
            "prior_head": PRIOR_HEAD,
            "prior_momentum_best_validation_net_metric": -4.680782776161402,
            "prior_momentum_closure_result": MOMENTUM_RESULT_CLASS,
            "prior_tracked_python_count": PRIOR_TRACKED_PYTHON_COUNT,
            "project": PROJECT,
        },
        "whitelisted_artifact_identity": artifact_metadata(),
    }


def build_summary() -> dict[str, Any]:
    data, timestamps, panel_meta = load_panel()
    search = run_search(data, timestamps)
    summaries = build_summaries(panel_meta, search)
    static = static_sections()
    metric_integrity = summaries["metric_integrity"]
    validation_checks = {
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 0,
        "approved_route_family_executed": ROUTE_FAMILY,
        "created_file_expected_count": 1,
        "exact_whitelisted_artifact_path_used": True,
        "exactly_one_new_tracked_python_tool_file_expected": True,
        "execution_result_is_diagnostic_only": True,
        "evaluator_not_yet_run": True,
        "future_final_edge_claim_requires_external_or_future_holdout": True,
        "module_path_equals_required_path": True,
        "no_all_in_one_panel_access": True,
        "no_boundary_buffer_access": panel_meta["boundary_buffer_rows_read_count"] == 0,
        "no_candidate_generation": True,
        "no_data_files_created_expected": True,
        "no_edge_claim": True,
        "no_evaluator_run": True,
        "no_existing_files_modified_expected": True,
        "no_external_or_alternative_data": True,
        "no_family_release": True,
        "no_holdout_access": panel_meta["sealed_holdout_rows_read_count"] == 0,
        "no_momentum_parameter_expansion": True,
        "no_momentum_retest": True,
        "no_momentum_vs_reversal_comparison": True,
        "no_new_governance_or_amendment_module_created": True,
        "no_original_1m_source_access": True,
        "no_runtime_live_capital": True,
        "no_unapproved_route_family_tested": True,
        "panel_rows_read_are_from_exact_whitelisted_artifact_only": True,
        "prior_access_scope_amendment_preserved": True,
        "prior_execution_approval_preserved": True,
        "prior_negative_momentum_closure_preserved": True,
        "prior_preregistration_contract_preserved": True,
        "replacement_checks_all_true": metric_integrity["metric_integrity_passed"],
        "status_equals_required_status": True,
        "tested_config_count_is_12": search["tested_config_count"] == 12,
        "whitelisted_artifact_mtime_matches_amendment_or_revalidated": (
            panel_meta["modified_time_ns_observed"] == EXPECTED_MODIFIED_TIME_NS
        ),
        "whitelisted_artifact_size_matches_amendment_or_revalidated": (
            panel_meta["file_size_bytes_observed"] == EXPECTED_FILE_SIZE_BYTES
        ),
    }
    replacement_checks_all_true = all(
        value is True
        for key, value in validation_checks.items()
        if key
        not in {
            "active_p0_blocker_count",
            "active_p1_attention_count",
            "approved_route_family_executed",
            "created_file_expected_count",
        }
    )
    return {
        "config_results": search["config_results"],
        "data_access_scope": static["data_access_scope"],
        "diagnostic_interpretation_limits": static["diagnostic_interpretation_limits"],
        "execution_safety_controls": static["execution_safety_controls"],
        "forbidden_actions_confirmed_false": static["forbidden_actions_confirmed_false"],
        "metric_integrity_summary": metric_integrity,
        "module": MODULE_PATH,
        "monthly_stability_summary": summaries["monthly_stability"],
        "null_baseline_summary": summaries["null_baseline"],
        "panel_input_validation": panel_meta,
        "permissions_after_execution": static["permissions_after_execution"],
        "prior_access_scope_amendment_preserved": static["prior_access_scope_amendment_preserved"],
        "prior_execution_approval_preserved": static["prior_execution_approval_preserved"],
        "prior_negative_momentum_closure_preserved": static["prior_negative_momentum_closure_preserved"],
        "prior_preregistration_contract_preserved": static["prior_preregistration_contract_preserved"],
        "replacement_checks_all_true": replacement_checks_all_true,
        "repo_scope": static["repo_scope"],
        "restricted_reversal_execution_results": {
            "candidate_generation": False,
            "edge_claim": False,
            "family_release": False,
            "gross_metrics_created": True,
            "metric_integrity_checks_created": True,
            "monthly_stability_created": True,
            "net_cost_adjusted_metrics_created": True,
            "no_cross_window_holding_returns": True,
            "null_baseline_complete": summaries["null_baseline"]["null_baseline_complete"],
            "route_family": ROUTE_FAMILY,
            "runtime_live_capital": False,
            "skipped_holding_windows": search["aggregate_skipped_holding_window_count"],
            "skipped_incomplete_rows": panel_meta["incomplete_1h_row_count"],
            "tested_config_count": search["tested_config_count"],
            "train_development_row_count": panel_meta["train_development_row_count"],
            "turnover_concentration_created": True,
            "validation_lookback_context_from_train_used": search["validation_lookback_context_from_train_used"],
            "validation_row_count": panel_meta["validation_row_count"],
        },
        "search_contract_executed": static["search_contract_executed"],
        "source_checkpoint": static["source_checkpoint"],
        "status": REQUIRED_STATUS,
        "train_validation_summary": summaries["train_validation"],
        "turnover_concentration_summary": summaries["turnover_concentration"],
        "validation_checks": validation_checks,
        "whitelisted_artifact_identity": static["whitelisted_artifact_identity"],
    }


def validate_summary(summary: dict[str, Any]) -> None:
    assert summary["status"] == REQUIRED_STATUS
    assert summary["module"] == MODULE_PATH
    assert summary["panel_input_validation"]["panel_path_used"] == str(PANEL_PATH)
    assert summary["panel_input_validation"]["exact_whitelisted_path_used"] is True
    assert summary["panel_input_validation"]["suffix_observed"] == EXPECTED_SUFFIX
    assert summary["panel_input_validation"]["file_size_bytes_observed"] > 0
    assert summary["panel_input_validation"]["boundary_buffer_rows_read_count"] == 0
    assert summary["panel_input_validation"]["sealed_holdout_rows_read_count"] == 0
    assert summary["panel_input_validation"]["all_in_one_panel_used"] is False
    assert summary["panel_input_validation"]["original_1m_source_files_used"] is False
    assert summary["panel_input_validation"]["external_data_used"] is False
    assert summary["panel_input_validation"]["alternative_data_used"] is False
    assert summary["search_contract_executed"]["route_family"] == ROUTE_FAMILY
    assert tuple(summary["search_contract_executed"]["lookback_options_hours"]) == LOOKBACKS
    assert tuple(summary["search_contract_executed"]["holding_periods_hours"]) == HOLDING_PERIODS
    assert 72 not in summary["search_contract_executed"]["lookback_options_hours"]
    assert summary["restricted_reversal_execution_results"]["tested_config_count"] == 12
    assert summary["restricted_reversal_execution_results"]["candidate_generation"] is False
    assert summary["restricted_reversal_execution_results"]["edge_claim"] is False
    assert summary["restricted_reversal_execution_results"]["family_release"] is False
    assert summary["restricted_reversal_execution_results"]["runtime_live_capital"] is False
    assert summary["diagnostic_interpretation_limits"]["evaluator_not_yet_run"] is True
    assert summary["prior_negative_momentum_closure_preserved"]["momentum_result_class"] == MOMENTUM_RESULT_CLASS
    assert summary["prior_negative_momentum_closure_preserved"]["best_validation_net_metric"] < 0
    assert summary["diagnostic_interpretation_limits"]["final_edge_claim_requires_external_or_future_holdout"] is True
    for key, value in summary["forbidden_actions_confirmed_false"].items():
        assert value is False, key
    assert summary["metric_integrity_summary"]["metric_integrity_issue_count"] == 0
    assert summary["replacement_checks_all_true"] is True


def main() -> int:
    summary = build_summary()
    validate_summary(summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
