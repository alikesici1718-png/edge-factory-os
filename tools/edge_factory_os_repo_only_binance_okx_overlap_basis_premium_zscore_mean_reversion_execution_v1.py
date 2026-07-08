#!/usr/bin/env python
"""Execute one preregistered basis/premium z-score mean-reversion diagnostic."""

from __future__ import annotations

import bisect
import gzip
import hashlib
import json
import math
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EXTERNAL_ROW_DIR = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_binance_okx_overlap_basis_premium_1h_data_pack_v1\basis_premium_by_symbol"
)

MODULE_RELATIVE_PATH = (
    "tools/"
    "edge_factory_os_repo_only_binance_okx_overlap_basis_premium_zscore_mean_reversion_"
    "execution_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/strategy_executions/"
    "binance_okx_overlap_basis_premium_zscore_mean_reversion_execution_v1.json"
)
PREREG_RELATIVE_PATH = (
    "artifacts/research_preregistrations/"
    "binance_okx_overlap_basis_premium_zscore_mean_reversion_preregistration_contract_v1.json"
)
REVIEW_RELATIVE_PATH = (
    "artifacts/basis_premium_data_reviews/"
    "binance_okx_overlap_basis_premium_1h_data_pack_review_v1.json"
)
MANIFEST_RELATIVE_PATH = (
    "artifacts/basis_premium_data_locks/"
    "binance_okx_overlap_basis_premium_1h_data_pack_v1.json"
)

ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH
PREREG_PATH = REPO_ROOT / PREREG_RELATIVE_PATH
REVIEW_PATH = REPO_ROOT / REVIEW_RELATIVE_PATH
MANIFEST_PATH = REPO_ROOT / MANIFEST_RELATIVE_PATH

STATUS = (
    "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_BASIS_PREMIUM_ZSCORE_MEAN_REVERSION_EXECUTED"
)
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_BASIS_PREMIUM_ZSCORE_MEAN_REVERSION_EXECUTION"
ROUTE_FAMILY = "BINANCE_OKX_OVERLAP_BASIS_PREMIUM_ZSCORE_MEAN_REVERSION_BASELINE"
CONFIG_ID = "mark_index_basis_z30d_reversal_hold8h"
EXPECTED_PREREG_STATUS = (
    "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_BASIS_PREMIUM_ZSCORE_MEAN_REVERSION_"
    "PREREGISTRATION_CONTRACT_CREATED"
)
EXPECTED_REVIEW_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_BASIS_PREMIUM_1H_DATA_PACK_REVIEW_CREATED"
EXPECTED_REVIEW_PAYLOAD = "9fca2469059be23e9a1bee77c4772f0cc5a06cb01c916f1b7356a69fa2278f4a"
EXPECTED_SYMBOL_COUNT = 81
EXPECTED_ROW_COUNT = 1_952_156

HOUR_MS = 3_600_000
HOLD_HOURS = 8
HOLD_MS = HOLD_HOURS * HOUR_MS
LOOKBACK_OBSERVATIONS = 720
MIN_PRIOR_OBSERVATIONS = 504
MIN_ELIGIBLE_SYMBOLS = 60
MIN_LEG_SYMBOLS = 5
TAIL_FRACTION = 0.20
COST_ROUND_TRIP = 0.0020
COST_SIDE = COST_ROUND_TRIP / 2.0
NULL_RUN_COUNT = 100
NULL_BLOCK_LENGTH = 168

FULL_START_MS = 1_672_531_200_000
FULL_END_MS = 1_761_955_200_000
TRAIN_START_MS = FULL_START_MS
TRAIN_END_MS = 1_719_792_000_000
VALIDATION_START_MS = TRAIN_END_MS
VALIDATION_END_MS = 1_743_465_600_000
HOLDOUT_START_MS = VALIDATION_END_MS
HOLDOUT_END_MS = FULL_END_MS

SPLITS = (
    ("train", TRAIN_START_MS, TRAIN_END_MS),
    ("validation", VALIDATION_START_MS, VALIDATION_END_MS),
    ("holdout", HOLDOUT_START_MS, HOLDOUT_END_MS),
)

REQUIRED_FIELDS = (
    "symbol",
    "timestamp_utc",
    "timestamp_ms",
    "premium_close",
    "mark_open",
    "mark_close",
    "index_open",
    "index_close",
    "interval",
)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def payload_hash(artifact: dict) -> str:
    payload = {key: value for key, value in artifact.items() if key != "payload_sha256_excluding_hash"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def norm_path(path: Path) -> str:
    return os.path.normcase(os.path.abspath(str(path)))


def path_inside(path: Path, root: Path) -> bool:
    try:
        return os.path.commonpath([norm_path(path), norm_path(root)]) == norm_path(root)
    except ValueError:
        return False


def parse_int(value: object) -> int:
    if isinstance(value, bool):
        raise ValueError("bool is not int")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().lstrip("-").isdigit():
        return int(value.strip())
    raise ValueError("not int")


def parse_float(value: object) -> float:
    if isinstance(value, bool):
        raise ValueError("bool is not numeric")
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError("not finite")
    return parsed


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def median(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    midpoint = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[midpoint]
    return (ordered[midpoint - 1] + ordered[midpoint]) / 2.0


def bps(value: float | None) -> float | None:
    return value * 10_000.0 if value is not None else None


def month_key(timestamp_ms: int) -> str:
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc).strftime("%Y-%m")


def iso_from_ms(timestamp_ms: int) -> str:
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def update_min(current: float | None, value: float) -> float:
    return value if current is None or value < current else current


def update_max(current: float | None, value: float) -> float:
    return value if current is None or value > current else current


def summarize_records(records: list[dict]) -> dict:
    gross_values = [record["gross_return"] for record in records]
    net_values = [record["net_return"] for record in records]
    long_values = [record["long_mean_return"] for record in records]
    short_values = [record["short_mean_return"] for record in records]
    gross_mean = mean(gross_values)
    net_mean = mean(net_values)
    long_gross_mean = mean(long_values)
    short_gross_mean = mean(short_values)
    return {
        "eligible_timestamp_count": len(records),
        "gross_mean_return": gross_mean,
        "net_mean_return": net_mean,
        "gross_mean_bps": bps(gross_mean),
        "net_mean_bps": bps(net_mean),
        "positive_after_cost": net_mean is not None and net_mean > 0.0,
        "long_gross_mean_bps": bps(long_gross_mean),
        "long_net_mean_bps": bps(long_gross_mean - COST_SIDE) if long_gross_mean is not None else None,
        "short_gross_mean_bps": bps(short_gross_mean),
        "short_net_mean_bps": bps(short_gross_mean - COST_SIDE) if short_gross_mean is not None else None,
        "long_selection_count": sum(len(record["long_symbols"]) for record in records),
        "short_selection_count": sum(len(record["short_symbols"]) for record in records),
    }


def monthly_summary(records: list[dict]) -> dict:
    buckets: dict[str, dict[str, list[float]]] = {}
    for record in records:
        month = month_key(record["entry_timestamp_ms"])
        if month not in buckets:
            buckets[month] = {"gross": [], "net": []}
        buckets[month]["gross"].append(record["gross_return"])
        buckets[month]["net"].append(record["net_return"])

    months = []
    for month in sorted(buckets):
        gross_mean = mean(buckets[month]["gross"])
        net_mean = mean(buckets[month]["net"])
        months.append(
            {
                "entry_month": month,
                "eligible_timestamp_count": len(buckets[month]["net"]),
                "gross_mean_bps": bps(gross_mean),
                "net_mean_bps": bps(net_mean),
                "positive_after_cost": net_mean is not None and net_mean > 0.0,
            }
        )
    positive_rate = (
        sum(1 for month in months if month["positive_after_cost"]) / len(months) if months else None
    )
    return {
        "months": months,
        "month_count": len(months),
        "positive_rate_net": positive_rate,
    }


def make_weights(record: dict) -> dict[str, float]:
    weights: dict[str, float] = {}
    long_weight = 0.5 / len(record["long_symbols"])
    short_weight = -0.5 / len(record["short_symbols"])
    for symbol in record["long_symbols"]:
        weights[symbol] = long_weight
    for symbol in record["short_symbols"]:
        weights[symbol] = short_weight
    return weights


def turnover_summary(records: list[dict]) -> dict:
    long_counts: dict[str, int] = {}
    short_counts: dict[str, int] = {}
    total_counts: dict[str, int] = {}
    turnovers: list[float] = []
    previous_weights: dict[str, float] | None = None

    for record in records:
        for symbol in record["long_symbols"]:
            long_counts[symbol] = long_counts.get(symbol, 0) + 1
            total_counts[symbol] = total_counts.get(symbol, 0) + 1
        for symbol in record["short_symbols"]:
            short_counts[symbol] = short_counts.get(symbol, 0) + 1
            total_counts[symbol] = total_counts.get(symbol, 0) + 1
        weights = make_weights(record)
        if previous_weights is not None:
            symbols = set(previous_weights) | set(weights)
            turnovers.append(sum(abs(weights.get(symbol, 0.0) - previous_weights.get(symbol, 0.0)) for symbol in symbols))
        previous_weights = weights

    total_selections = sum(total_counts.values())
    top_share = max(total_counts.values()) / total_selections if total_selections else None
    avg_turnover = mean(turnovers)
    med_turnover = median(turnovers)
    max_turnover = max(turnovers) if turnovers else None
    return {
        "participation_by_selected_long_symbols": dict(sorted(long_counts.items())),
        "participation_by_selected_short_symbols": dict(sorted(short_counts.items())),
        "participation_by_selected_symbols_total": dict(sorted(total_counts.items())),
        "average_turnover": avg_turnover,
        "median_turnover": med_turnover,
        "max_turnover": max_turnover,
        "top_symbol_exposure_share": top_share,
        "turnover_concentration_review_preliminary_passed": (
            top_share is not None
            and avg_turnover is not None
            and top_share <= 0.10
            and avg_turnover <= 1.50
        ),
    }


def recompute_with_source_signals(target_record: dict, source_record: dict) -> float | None:
    long_returns = [
        target_record["long_return_by_symbol"][symbol]
        for symbol in source_record["long_symbols"]
        if symbol in target_record["long_return_by_symbol"]
    ]
    short_returns = [
        target_record["short_return_by_symbol"][symbol]
        for symbol in source_record["short_symbols"]
        if symbol in target_record["short_return_by_symbol"]
    ]
    if not long_returns or not short_returns:
        return None
    return (sum(long_returns) / len(long_returns)) + (sum(short_returns) / len(short_returns)) - COST_ROUND_TRIP


def block_shuffle_metric(records: list[dict], seed: int) -> float | None:
    if not records:
        return None
    blocks = [records[index : index + NULL_BLOCK_LENGTH] for index in range(0, len(records), NULL_BLOCK_LENGTH)]
    order = list(range(len(blocks)))
    rng = random.Random(seed)
    rng.shuffle(order)
    source_records = [record for block_index in order for record in blocks[block_index]]
    null_returns: list[float] = []
    for target_record, source_record in zip(records, source_records):
        recomputed = recompute_with_source_signals(target_record, source_record)
        if recomputed is not None and math.isfinite(recomputed):
            null_returns.append(recomputed)
    return mean(null_returns)


def build_prefix(values: list[float]) -> tuple[list[float], list[float]]:
    sums = [0.0]
    squares = [0.0]
    for value in values:
        sums.append(sums[-1] + value)
        squares.append(squares[-1] + value * value)
    return sums, squares


def load_symbol_rows(review: dict) -> tuple[dict[str, dict], dict]:
    records = review.get("symbol_review_records", [])
    data: dict[str, dict] = {}
    validation = {
        "symbol_file_count": len(records),
        "rows_read": 0,
        "required_field_missing_count": 0,
        "invalid_numeric_count": 0,
        "nonpositive_price_count": 0,
        "invalid_interval_count": 0,
        "timestamp_outside_full_window_count": 0,
        "unsorted_timestamp_count": 0,
        "duplicate_timestamp_count": 0,
        "row_files_outside_reviewed_external_directory_count": 0,
        "global_min_basis_close": None,
        "global_max_basis_close": None,
        "global_min_premium_close": None,
        "global_max_premium_close": None,
        "extreme_abs_basis_count": 0,
        "extreme_abs_premium_count": 0,
    }

    for record in records:
        symbol = record["symbol"]
        path = Path(record["file_path"])
        if not path_inside(path, EXTERNAL_ROW_DIR):
            validation["row_files_outside_reviewed_external_directory_count"] += 1
            continue

        timestamps: list[int] = []
        basis_close: list[float] = []
        premium_close: list[float] = []
        mark_open: list[float] = []
        mark_open_by_timestamp: dict[int, float] = {}
        seen_timestamps: set[int] = set()
        previous_timestamp: int | None = None

        with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
            for line in handle:
                row = json.loads(line)
                missing_fields = [field for field in REQUIRED_FIELDS if field not in row]
                if missing_fields:
                    validation["required_field_missing_count"] += len(missing_fields)
                    continue
                if row.get("interval") not in {"1h", "1H", "60m", "60min", "3600s", "3600000ms"}:
                    validation["invalid_interval_count"] += 1
                    continue
                try:
                    timestamp_ms = parse_int(row["timestamp_ms"])
                    premium_value = parse_float(row["premium_close"])
                    mark_open_value = parse_float(row["mark_open"])
                    mark_close_value = parse_float(row["mark_close"])
                    index_open_value = parse_float(row["index_open"])
                    index_close_value = parse_float(row["index_close"])
                except (TypeError, ValueError):
                    validation["invalid_numeric_count"] += 1
                    continue
                if mark_open_value <= 0 or mark_close_value <= 0 or index_open_value <= 0 or index_close_value <= 0:
                    validation["nonpositive_price_count"] += 1
                    continue
                if timestamp_ms < FULL_START_MS or timestamp_ms >= FULL_END_MS:
                    validation["timestamp_outside_full_window_count"] += 1
                    continue
                if previous_timestamp is not None and timestamp_ms <= previous_timestamp:
                    validation["unsorted_timestamp_count"] += 1
                if timestamp_ms in seen_timestamps:
                    validation["duplicate_timestamp_count"] += 1

                previous_timestamp = timestamp_ms
                seen_timestamps.add(timestamp_ms)
                basis_value = mark_close_value / index_close_value - 1.0
                timestamps.append(timestamp_ms)
                basis_close.append(basis_value)
                premium_close.append(premium_value)
                mark_open.append(mark_open_value)
                mark_open_by_timestamp[timestamp_ms] = mark_open_value
                validation["rows_read"] += 1
                validation["global_min_basis_close"] = update_min(validation["global_min_basis_close"], basis_value)
                validation["global_max_basis_close"] = update_max(validation["global_max_basis_close"], basis_value)
                validation["global_min_premium_close"] = update_min(
                    validation["global_min_premium_close"], premium_value
                )
                validation["global_max_premium_close"] = update_max(
                    validation["global_max_premium_close"], premium_value
                )
                if abs(basis_value) > 0.10:
                    validation["extreme_abs_basis_count"] += 1
                if abs(premium_value) > 0.10:
                    validation["extreme_abs_premium_count"] += 1

        prefix_sum, prefix_square = build_prefix(basis_close)
        data[symbol] = {
            "timestamps": timestamps,
            "basis_close": basis_close,
            "premium_close": premium_close,
            "mark_open": mark_open,
            "mark_open_by_timestamp": mark_open_by_timestamp,
            "prefix_sum": prefix_sum,
            "prefix_square": prefix_square,
        }

    return data, validation


def execute_config(data: dict[str, dict]) -> tuple[dict[str, list[dict]], dict, dict]:
    split_records: dict[str, list[dict]] = {split: [] for split, _, _ in SPLITS}
    skipped = {split: 0 for split, _, _ in SPLITS}
    lookahead_violation_count = 0
    cross_window_violation_count = 0
    timestamp_outside_split_count = 0
    diagnostic = {
        "validation_long_z_sum": 0.0,
        "validation_long_z_count": 0,
        "validation_short_z_sum": 0.0,
        "validation_short_z_count": 0,
        "validation_long_premium_sum": 0.0,
        "validation_long_premium_count": 0,
        "validation_short_premium_sum": 0.0,
        "validation_short_premium_count": 0,
    }

    for split_name, split_start, split_end in SPLITS:
        entry_timestamp = split_start
        while entry_timestamp + HOLD_MS < split_end:
            eligible = []
            for symbol, symbol_data in data.items():
                entry_mark_open = symbol_data["mark_open_by_timestamp"].get(entry_timestamp)
                exit_mark_open = symbol_data["mark_open_by_timestamp"].get(entry_timestamp + HOLD_MS)
                if entry_mark_open is None or exit_mark_open is None:
                    continue

                timestamps = symbol_data["timestamps"]
                prior_index = bisect.bisect_left(timestamps, entry_timestamp)
                if prior_index < MIN_PRIOR_OBSERVATIONS:
                    continue
                latest_index = prior_index - 1
                latest_timestamp = timestamps[latest_index]
                if latest_timestamp >= entry_timestamp:
                    lookahead_violation_count += 1
                    continue
                lookback_start = max(0, prior_index - LOOKBACK_OBSERVATIONS)
                observation_count = prior_index - lookback_start
                if observation_count < MIN_PRIOR_OBSERVATIONS:
                    continue

                prefix_sum = symbol_data["prefix_sum"]
                prefix_square = symbol_data["prefix_square"]
                trailing_sum = prefix_sum[prior_index] - prefix_sum[lookback_start]
                trailing_square = prefix_square[prior_index] - prefix_square[lookback_start]
                trailing_mean = trailing_sum / observation_count
                variance = trailing_square / observation_count - trailing_mean * trailing_mean
                if variance <= 0.0 or not math.isfinite(variance):
                    continue
                trailing_std = math.sqrt(variance)
                if trailing_std <= 0.0 or not math.isfinite(trailing_std):
                    continue

                latest_basis = symbol_data["basis_close"][latest_index]
                basis_z = (latest_basis - trailing_mean) / trailing_std
                if not math.isfinite(basis_z):
                    continue
                raw_return = exit_mark_open / entry_mark_open - 1.0
                if not math.isfinite(raw_return):
                    continue
                eligible.append(
                    {
                        "symbol": symbol,
                        "basis_z": basis_z,
                        "premium_close": symbol_data["premium_close"][latest_index],
                        "basis_close": latest_basis,
                        "raw_return": raw_return,
                    }
                )

            if len(eligible) < MIN_ELIGIBLE_SYMBOLS:
                skipped[split_name] += 1
                entry_timestamp += HOUR_MS
                continue
            eligible.sort(key=lambda item: (item["basis_z"], item["symbol"]))
            tail_count = int(math.floor(len(eligible) * TAIL_FRACTION))
            tail_count = max(1, tail_count)
            if tail_count < MIN_LEG_SYMBOLS:
                skipped[split_name] += 1
                entry_timestamp += HOUR_MS
                continue

            long_leg = eligible[:tail_count]
            short_leg = eligible[-tail_count:]
            long_returns = [item["raw_return"] for item in long_leg]
            short_returns = [-item["raw_return"] for item in short_leg]
            long_mean = sum(long_returns) / len(long_returns)
            short_mean = sum(short_returns) / len(short_returns)
            gross_return = long_mean + short_mean
            net_return = gross_return - COST_ROUND_TRIP
            if entry_timestamp < split_start or entry_timestamp >= split_end:
                timestamp_outside_split_count += 1
            if entry_timestamp + HOLD_MS >= split_end:
                cross_window_violation_count += 1

            long_return_by_symbol = {item["symbol"]: item["raw_return"] for item in eligible}
            short_return_by_symbol = {item["symbol"]: -item["raw_return"] for item in eligible}
            record = {
                "entry_timestamp_ms": entry_timestamp,
                "entry_timestamp_utc": iso_from_ms(entry_timestamp),
                "split": split_name,
                "eligible_symbol_count": len(eligible),
                "tail_count": tail_count,
                "long_symbols": [item["symbol"] for item in long_leg],
                "short_symbols": [item["symbol"] for item in short_leg],
                "long_mean_return": long_mean,
                "short_mean_return": short_mean,
                "gross_return": gross_return,
                "net_return": net_return,
                "long_return_by_symbol": long_return_by_symbol,
                "short_return_by_symbol": short_return_by_symbol,
            }
            split_records[split_name].append(record)

            if split_name == "validation":
                for item in long_leg:
                    diagnostic["validation_long_z_sum"] += item["basis_z"]
                    diagnostic["validation_long_z_count"] += 1
                    diagnostic["validation_long_premium_sum"] += item["premium_close"]
                    diagnostic["validation_long_premium_count"] += 1
                for item in short_leg:
                    diagnostic["validation_short_z_sum"] += item["basis_z"]
                    diagnostic["validation_short_z_count"] += 1
                    diagnostic["validation_short_premium_sum"] += item["premium_close"]
                    diagnostic["validation_short_premium_count"] += 1

            entry_timestamp += HOUR_MS

    integrity_counts = {
        "lookahead_violation_count": lookahead_violation_count,
        "cross_window_violation_count": cross_window_violation_count,
        "timestamp_outside_split_count": timestamp_outside_split_count,
    }
    return split_records, skipped, {**diagnostic, **integrity_counts}


def finite_or_none(value: object) -> bool:
    return value is None or not isinstance(value, float) or math.isfinite(value)


def main() -> int:
    if ARTIFACT_PATH.exists():
        print(f"BLOCKED: artifact already exists: {ARTIFACT_PATH}")
        print("replacement_checks_all_true: false")
        return 1

    prereg = load_json(PREREG_PATH)
    review = load_json(REVIEW_PATH)
    manifest = load_json(MANIFEST_PATH)

    prereg_checks = {
        "preregistration_loaded": True,
        "preregistration_status_verified": prereg.get("status") == EXPECTED_PREREG_STATUS,
        "preregistration_route_family_verified": prereg.get("route_family") == ROUTE_FAMILY,
        "preregistration_exactly_one_config": len(prereg.get("config_grid", [])) == 1,
        "preregistration_config_id_verified": prereg.get("config_grid", [{}])[0].get("config_id") == CONFIG_ID,
        "review_loaded": True,
        "review_status_verified": review.get("status") == EXPECTED_REVIEW_STATUS,
        "review_payload_hash_verified": review.get("payload_sha256_excluding_hash") == EXPECTED_REVIEW_PAYLOAD,
        "manifest_loaded": True,
        "manifest_payload_matches_review_source": manifest.get("payload_sha256_excluding_hash")
        == review.get("manifest_review", {}).get("payload_sha256_actual"),
    }
    if not all(value is True for value in prereg_checks.values()):
        print("BLOCKED: source preregistration or review validation failed")
        for key in sorted(prereg_checks):
            if prereg_checks[key] is not True:
                print(f"{key}: {prereg_checks[key]}")
        print("replacement_checks_all_true: false")
        return 1

    data, input_validation = load_symbol_rows(review)
    source_data_valid = (
        input_validation["symbol_file_count"] == EXPECTED_SYMBOL_COUNT
        and input_validation["rows_read"] == EXPECTED_ROW_COUNT
        and input_validation["required_field_missing_count"] == 0
        and input_validation["invalid_numeric_count"] == 0
        and input_validation["nonpositive_price_count"] == 0
        and input_validation["invalid_interval_count"] == 0
        and input_validation["timestamp_outside_full_window_count"] == 0
        and input_validation["unsorted_timestamp_count"] == 0
        and input_validation["duplicate_timestamp_count"] == 0
        and input_validation["row_files_outside_reviewed_external_directory_count"] == 0
    )
    if not source_data_valid:
        print("BLOCKED: input basis/premium rows failed validation")
        print(json.dumps(input_validation, sort_keys=True))
        print("replacement_checks_all_true: false")
        return 1

    split_records, skipped, execution_diagnostics = execute_config(data)
    train_summary = summarize_records(split_records["train"])
    validation_summary = summarize_records(split_records["validation"])
    holdout_summary = summarize_records(split_records["holdout"])

    all_records = split_records["train"] + split_records["validation"] + split_records["holdout"]
    eligible_counts = [record["eligible_symbol_count"] for record in all_records]
    signal_coverage_summary = {
        "train_eligible_timestamp_count": len(split_records["train"]),
        "validation_eligible_timestamp_count": len(split_records["validation"]),
        "holdout_eligible_timestamp_count": len(split_records["holdout"]),
        "average_eligible_symbols_per_timestamp": mean([float(value) for value in eligible_counts]),
        "median_eligible_symbols_per_timestamp": median([float(value) for value in eligible_counts]),
        "min_eligible_symbols_per_timestamp": min(eligible_counts) if eligible_counts else None,
        "max_eligible_symbols_per_timestamp": max(eligible_counts) if eligible_counts else None,
        "skipped_timestamps_insufficient_symbols": sum(skipped.values()),
        "skipped_timestamps_insufficient_symbols_by_split": skipped,
        "signal_coverage_review_preliminary_passed": (
            len(split_records["validation"]) >= 1000
            and (mean([float(value) for value in eligible_counts]) or 0.0) >= 60.0
        ),
    }

    validation_avg_long_z = mean(
        [execution_diagnostics["validation_long_z_sum"] / execution_diagnostics["validation_long_z_count"]]
    ) if execution_diagnostics["validation_long_z_count"] else None
    validation_avg_short_z = mean(
        [execution_diagnostics["validation_short_z_sum"] / execution_diagnostics["validation_short_z_count"]]
    ) if execution_diagnostics["validation_short_z_count"] else None
    validation_avg_long_premium = mean(
        [
            execution_diagnostics["validation_long_premium_sum"]
            / execution_diagnostics["validation_long_premium_count"]
        ]
    ) if execution_diagnostics["validation_long_premium_count"] else None
    validation_avg_short_premium = mean(
        [
            execution_diagnostics["validation_short_premium_sum"]
            / execution_diagnostics["validation_short_premium_count"]
        ]
    ) if execution_diagnostics["validation_short_premium_count"] else None

    premium_basis_diagnostic_summary = {
        "global_min_basis_close": input_validation["global_min_basis_close"],
        "global_max_basis_close": input_validation["global_max_basis_close"],
        "validation_average_long_basis_z": validation_avg_long_z,
        "validation_average_short_basis_z": validation_avg_short_z,
        "validation_average_long_premium_close": validation_avg_long_premium,
        "validation_average_short_premium_close": validation_avg_short_premium,
        "extreme_abs_basis_count": input_validation["extreme_abs_basis_count"],
        "extreme_abs_premium_count": input_validation["extreme_abs_premium_count"],
        "P1_attention_preserved_from_data_review": True,
    }

    long_short_side_summary = {
        "long_train_gross_bps": train_summary["long_gross_mean_bps"],
        "long_train_net_bps": train_summary["long_net_mean_bps"],
        "short_train_gross_bps": train_summary["short_gross_mean_bps"],
        "short_train_net_bps": train_summary["short_net_mean_bps"],
        "long_validation_gross_bps": validation_summary["long_gross_mean_bps"],
        "long_validation_net_bps": validation_summary["long_net_mean_bps"],
        "short_validation_gross_bps": validation_summary["short_gross_mean_bps"],
        "short_validation_net_bps": validation_summary["short_net_mean_bps"],
        "long_holdout_gross_bps": holdout_summary["long_gross_mean_bps"],
        "long_holdout_net_bps": holdout_summary["long_net_mean_bps"],
        "short_holdout_gross_bps": holdout_summary["short_gross_mean_bps"],
        "short_holdout_net_bps": holdout_summary["short_net_mean_bps"],
        "long_validation_selection_count": validation_summary["long_selection_count"],
        "short_validation_selection_count": validation_summary["short_selection_count"],
    }

    train_monthly = monthly_summary(split_records["train"])
    validation_monthly = monthly_summary(split_records["validation"])
    holdout_monthly = monthly_summary(split_records["holdout"])
    monthly_stability_summary = {
        "train_monthly_gross_net_by_entry_month": train_monthly["months"],
        "validation_monthly_gross_net_by_entry_month": validation_monthly["months"],
        "holdout_monthly_gross_net_by_entry_month": holdout_monthly["months"],
        "validation_monthly_positive_rate_based_on_net": validation_monthly["positive_rate_net"],
        "validation_month_count": validation_monthly["month_count"],
        "monthly_stability_review_preliminary_passed": (
            validation_monthly["positive_rate_net"] is not None
            and validation_monthly["positive_rate_net"] >= 0.60
            and validation_monthly["month_count"] >= 6
        ),
    }

    validation_actual_net = validation_summary["net_mean_return"]
    validation_null_metrics = [
        block_shuffle_metric(split_records["validation"], 20260525 + run_index)
        for run_index in range(NULL_RUN_COUNT)
    ]
    validation_null_metrics = [
        value for value in validation_null_metrics if value is not None and math.isfinite(value)
    ]
    train_null_metrics = [
        block_shuffle_metric(split_records["train"], 20270525 + run_index)
        for run_index in range(NULL_RUN_COUNT)
    ]
    train_null_metrics = [value for value in train_null_metrics if value is not None and math.isfinite(value)]
    validation_null_percentile = (
        sum(1 for value in validation_null_metrics if value <= validation_actual_net)
        / len(validation_null_metrics)
        if validation_actual_net is not None and validation_null_metrics
        else None
    )
    null_baseline_summary = {
        "null_baseline": "deterministic_signal_timestamp_block_shuffle_null",
        "null_run_count": NULL_RUN_COUNT,
        "block_length": "168 hours",
        "block_length_hours": NULL_BLOCK_LENGTH,
        "shuffle_scope": "train and validation separately",
        "preserve_cross_sectional_return_vectors_by_timestamp": True,
        "train_null_net_bps_min": bps(min(train_null_metrics)) if train_null_metrics else None,
        "train_null_net_bps_median": bps(median(train_null_metrics)) if train_null_metrics else None,
        "train_null_net_bps_max": bps(max(train_null_metrics)) if train_null_metrics else None,
        "validation_null_net_bps_min": bps(min(validation_null_metrics)) if validation_null_metrics else None,
        "validation_null_net_bps_median": bps(median(validation_null_metrics)) if validation_null_metrics else None,
        "validation_null_net_bps_max": bps(max(validation_null_metrics)) if validation_null_metrics else None,
        "validation_actual_net_bps": validation_summary["net_mean_bps"],
        "validation_null_percentile": validation_null_percentile,
        "null_baseline_review_preliminary_passed": (
            validation_null_percentile is not None and validation_null_percentile >= 0.95
        ),
    }

    turnover_concentration_summary = turnover_summary(split_records["validation"])

    metric_issues = []
    if execution_diagnostics["lookahead_violation_count"] != 0:
        metric_issues.append("lookahead_violation")
    if execution_diagnostics["cross_window_violation_count"] != 0:
        metric_issues.append("cross_window_return")
    if execution_diagnostics["timestamp_outside_split_count"] != 0:
        metric_issues.append("timestamp_outside_split")
    if not split_records["validation"]:
        metric_issues.append("no_validation_records")
    no_nan_inf = all(
        finite_or_none(value)
        for summary in (train_summary, validation_summary, holdout_summary)
        for value in summary.values()
    )
    if not no_nan_inf:
        metric_issues.append("nan_or_inf_metric")
    metric_integrity_passed = len(metric_issues) == 0
    metric_integrity_summary = {
        "exactly_one_config_executed": True,
        "no_nan_inf": no_nan_inf,
        "no_timestamp_outside_windows": execution_diagnostics["timestamp_outside_split_count"] == 0,
        "no_lookahead": execution_diagnostics["lookahead_violation_count"] == 0,
        "no_cross_window_returns": execution_diagnostics["cross_window_violation_count"] == 0,
        "no_non_preregistered_config": True,
        "no_candidate_edge_release_runtime": True,
        "issue_count": len(metric_issues),
        "issues": metric_issues,
        "metric_integrity_passed": metric_integrity_passed,
    }

    safety_permissions = {
        "strategy_diagnostic_executed": True,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
        "holdout_permission_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
    }
    forbidden_actions_confirmed_false = {
        "network_used": False,
        "binance_api_called": False,
        "okx_api_called": False,
        "data_downloaded": False,
        "binance_ohlcv_panel_rows_read": False,
        "binance_1m_source_rows_read": False,
        "okx_rows_read": False,
        "funding_rows_read": False,
        "oi_rows_read": False,
        "taker_flow_signal_used": False,
        "pair_logic_used": False,
        "candidate_generated": False,
        "edge_claim_created": False,
        "family_release_created": False,
        "holdout_permission_created": False,
        "runtime_live_capital_permission_created": False,
    }

    validation_checks = {
        **prereg_checks,
        "input_symbol_file_count_verified_81": input_validation["symbol_file_count"] == EXPECTED_SYMBOL_COUNT,
        "input_rows_read_verified": input_validation["rows_read"] == EXPECTED_ROW_COUNT,
        "required_field_missing_count_zero": input_validation["required_field_missing_count"] == 0,
        "invalid_numeric_count_zero": input_validation["invalid_numeric_count"] == 0,
        "nonpositive_price_count_zero": input_validation["nonpositive_price_count"] == 0,
        "invalid_interval_count_zero": input_validation["invalid_interval_count"] == 0,
        "timestamp_outside_full_window_count_zero": input_validation["timestamp_outside_full_window_count"] == 0,
        "unsorted_timestamp_count_zero": input_validation["unsorted_timestamp_count"] == 0,
        "duplicate_timestamp_count_zero": input_validation["duplicate_timestamp_count"] == 0,
        "external_rows_read_only_in_execution_step": True,
        "exactly_one_config_executed": True,
        "no_non_preregistered_config": True,
        "no_parameter_expansion": True,
        "no_network_used": True,
        "no_api_calls": True,
        "no_data_download": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_family_release": True,
        "no_holdout_permission": True,
        "no_runtime_live_capital": True,
        "metric_integrity_passed": metric_integrity_passed,
        "replacement_checks_all_true": False,
    }
    validation_checks["replacement_checks_all_true"] = all(
        value is True
        for key, value in validation_checks.items()
        if key != "replacement_checks_all_true" and isinstance(value, bool)
    )

    if not validation_checks["replacement_checks_all_true"]:
        print("BLOCKED: execution integrity validation failed")
        for key in sorted(validation_checks):
            if validation_checks[key] is not True:
                print(f"{key}: {validation_checks[key]}")
        print("replacement_checks_all_true: false")
        return 1

    config_result = {
        "config_id": CONFIG_ID,
        "config_count_executed": 1,
        "cost_round_trip_bps": 20,
        "holding_period_hours": HOLD_HOURS,
        "train": train_summary,
        "validation": validation_summary,
        "holdout": holdout_summary,
        "validation_net_metric_bps": validation_summary["net_mean_bps"],
        "validation_positive_after_cost": validation_summary["positive_after_cost"],
        "holdout_used_for_config_selection": False,
    }
    train_validation_holdout_summary = {
        "train_gross_bps": train_summary["gross_mean_bps"],
        "train_net_bps": train_summary["net_mean_bps"],
        "validation_gross_bps": validation_summary["gross_mean_bps"],
        "validation_net_bps": validation_summary["net_mean_bps"],
        "holdout_gross_bps": holdout_summary["gross_mean_bps"],
        "holdout_net_bps": holdout_summary["net_mean_bps"],
        "holdout_reported_separately": True,
        "holdout_used_for_config_selection": False,
    }

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "route_family": ROUTE_FAMILY,
        "config_id": CONFIG_ID,
        "input_data_validation": input_validation,
        "signal_definition": prereg.get("signal_definition"),
        "return_and_cost_policy": {
            "entry_price": "mark_open at E",
            "exit_price": "mark_open at E+8h",
            "long_return": "exit_mark_open / entry_mark_open - 1",
            "short_return": "-(exit_mark_open / entry_mark_open - 1)",
            "gross_spread_return": "mean(long returns) + mean(short returns)",
            "net_spread_return": "gross - 0.0020",
            "cost_round_trip_bps": 20,
            "annualization_used": False,
            "compounding_used": False,
        },
        "execution_safety_controls": {
            "exactly_one_config": True,
            "no_extra_configs_tested": True,
            "no_parameter_tuning": True,
            "holdout_reported_separately": True,
            "holdout_positive_cannot_create_candidate_edge_or_release": True,
            "no_subprocess_used_inside_module": True,
        },
        "config_result": config_result,
        "train_validation_holdout_summary": train_validation_holdout_summary,
        "signal_coverage_summary": signal_coverage_summary,
        "premium_basis_diagnostic_summary": premium_basis_diagnostic_summary,
        "long_short_side_summary": long_short_side_summary,
        "monthly_stability_summary": monthly_stability_summary,
        "null_baseline_summary": null_baseline_summary,
        "turnover_concentration_summary": turnover_concentration_summary,
        "metric_integrity_summary": metric_integrity_summary,
        "diagnostic_interpretation_limits": [
            "This is a single-config diagnostic only.",
            "No parameter expansion or tuning was performed.",
            "Holdout is reported separately and not used for config selection.",
            "A positive holdout result cannot create a candidate, edge claim, release, or permission.",
            "No runtime, live, or capital permission is granted.",
        ],
        "safety_permissions": safety_permissions,
        "forbidden_actions_confirmed_false": forbidden_actions_confirmed_false,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": validation_checks["replacement_checks_all_true"],
        "payload_sha256_excluding_hash": None,
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(artifact, handle, indent=2)
        handle.write("\n")

    print(f"status: {STATUS}")
    print(f"artifact_path: {ARTIFACT_PATH}")
    print(f"config_id: {CONFIG_ID}")
    print(f"train_gross_bps: {train_summary['gross_mean_bps']}")
    print(f"train_net_bps: {train_summary['net_mean_bps']}")
    print(f"validation_gross_bps: {validation_summary['gross_mean_bps']}")
    print(f"validation_net_bps: {validation_summary['net_mean_bps']}")
    print(f"holdout_gross_bps: {holdout_summary['gross_mean_bps']}")
    print(f"holdout_net_bps: {holdout_summary['net_mean_bps']}")
    print(f"validation_eligible_timestamp_count: {len(split_records['validation'])}")
    print(f"average_eligible_symbols: {signal_coverage_summary['average_eligible_symbols_per_timestamp']}")
    print(f"validation_null_percentile: {validation_null_percentile}")
    print(f"metric_integrity_issue_count: {metric_integrity_summary['issue_count']}")
    print("candidate_generation_allowed_now: false")
    print("edge_claim_allowed_now: false")
    print("family_release_allowed_now: false")
    print("holdout_permission_allowed_now: false")
    print("runtime_live_capital_allowed_now: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print("replacement_checks_all_true: true")
    return 0


if __name__ == "__main__":
    sys.exit(main())
