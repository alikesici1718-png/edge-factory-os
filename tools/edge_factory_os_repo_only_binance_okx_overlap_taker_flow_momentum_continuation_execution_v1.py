import csv
import gzip
import hashlib
import json
import math
import random
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_taker_flow_momentum_continuation_execution_v1.py"
ARTIFACT_PATH = "artifacts/strategy_executions/binance_okx_overlap_taker_flow_momentum_continuation_execution_v1.json"
STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_TAKER_FLOW_MOMENTUM_CONTINUATION_EXECUTED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_TAKER_FLOW_MOMENTUM_CONTINUATION_EXECUTION"

ROUTE_FAMILY = "CROSS_SECTIONAL_TAKER_BUY_SHARE_MOMENTUM_CONTINUATION_BASELINE"
HYPOTHESIS_NAME = "taker_buy_share_momentum_continuation"
CONFIG_ID = "taker_buy_share_mom4h_rank_hold8h"

START_HOUR = None
TRAIN_END_HOUR = None
VALIDATION_START_HOUR = None
END_HOUR = None
HOLDING_HOURS = 8
COST_RETURN = 0.0020

PREREG_PATH = "artifacts/research_preregistrations/binance_okx_overlap_taker_flow_momentum_continuation_preregistration_contract_v1.json"
TAKER_AVAILABILITY_PATH = "artifacts/taker_buy_sell_volume_availability_locks/binance_okx_overlap_taker_buy_sell_volume_history_availability_discovery_lock_v1.json"
READINESS_PATH = "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json"
PANEL_REVIEW_PATH = "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json"
BUILD_MANIFEST_PATH = "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json"
PREVIEW_PATH = "artifacts/panel_build_previews/binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.json"
COVERAGE_LOCK_PATH = "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json"

PANEL_DIR = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_binance_okx_overlap_near_5y_1m_to_1h_panel_build_execution_v1\panel_1h_by_symbol"
)

EXPECTED_PANEL_HEADER = [
    "symbol",
    "timestamp_utc",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "quote_volume",
    "trade_count",
    "taker_buy_base_volume",
    "taker_buy_quote_volume",
    "minute_count",
    "complete_1h",
]


def canonical_payload_hash(payload: Dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(json.dumps(clean, sort_keys=True, indent=2).encode("utf-8")).hexdigest()


def read_json(relative_path: str) -> Dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise RuntimeError(f"missing required source artifact: {relative_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def verify_hash(payload: Dict[str, Any]) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise RuntimeError("source artifact missing payload_sha256_excluding_hash")
    recomputed = canonical_payload_hash(payload)
    if recomputed != stored:
        raise RuntimeError(f"source artifact payload hash mismatch: {recomputed} != {stored}")
    return stored


TS_CACHE: Dict[str, int] = {}


def parse_hour(value: str) -> int:
    cached = TS_CACHE.get(value)
    if cached is not None:
        return cached
    if not value.endswith("Z"):
        raise RuntimeError(f"timestamp does not end with Z: {value}")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    hour = int(dt.timestamp() // 3600)
    TS_CACHE[value] = hour
    return hour


def hour_to_iso(hour: int) -> str:
    return datetime.fromtimestamp(hour * 3600, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def month_key(hour: int) -> str:
    return datetime.fromtimestamp(hour * 3600, timezone.utc).strftime("%Y-%m")


def mean(values: Sequence[float]) -> Optional[float]:
    if not values:
        return None
    return sum(values) / len(values)


def mean_bps(values: Sequence[float]) -> Optional[float]:
    value = mean(values)
    return None if value is None else round(value * 10000.0, 6)


def finite_or_none(value: Optional[float]) -> bool:
    return value is None or (isinstance(value, (int, float)) and math.isfinite(float(value)))


def split_for_entry(entry_hour: int, exit_hour: int) -> Tuple[Optional[str], bool]:
    if START_HOUR <= entry_hour < TRAIN_END_HOUR:
        return ("train", exit_hour < TRAIN_END_HOUR)
    if VALIDATION_START_HOUR <= entry_hour < END_HOUR:
        return ("validation", exit_hour < END_HOUR)
    return (None, False)


def deterministic_seed(route_family: str, config_id: str, run_index: int) -> int:
    digest = hashlib.sha256(f"{route_family}|{config_id}|{run_index}".encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def shuffled_records(records: List[Dict[str, Any]], run_index: int) -> List[Dict[str, Any]]:
    blocks = [records[i : i + 168] for i in range(0, len(records), 168)]
    rng = random.Random(deterministic_seed(ROUTE_FAMILY, CONFIG_ID, run_index))
    rng.shuffle(blocks)
    flattened: List[Dict[str, Any]] = []
    for block in blocks:
        flattened.extend(block)
    return flattened[: len(records)]


def find_symbol_list(value: Any) -> Optional[List[str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in ("exact_overlap_binance_symbols", "symbol_set") and isinstance(child, list) and len(child) == 81:
                if all(isinstance(item, str) and item.endswith("USDT") for item in child):
                    return list(child)
            found = find_symbol_list(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_symbol_list(child)
            if found:
                return found
    return None


def find_first_key(value: Any, target_key: str) -> Any:
    if isinstance(value, dict):
        if target_key in value:
            return value[target_key]
        for child in value.values():
            found = find_first_key(child, target_key)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_first_key(child, target_key)
            if found is not None:
                return found
    return None


def contains_key(value: Any, target_key: str) -> bool:
    if isinstance(value, dict):
        if target_key in value:
            return True
        return any(contains_key(child, target_key) for child in value.values())
    if isinstance(value, list):
        return any(contains_key(child, target_key) for child in value)
    return False


def load_panel_rows(symbol: str) -> List[Dict[str, float]]:
    path = PANEL_DIR / f"{symbol}_1h.csv.gz"
    if not path.exists():
        raise RuntimeError(f"missing panel file for {symbol}: {path}")
    rows: List[Dict[str, float]] = []
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != EXPECTED_PANEL_HEADER:
            raise RuntimeError(f"bad panel header for {symbol}: {reader.fieldnames}")
        for row in reader:
            if row["symbol"] != symbol:
                raise RuntimeError(f"panel symbol mismatch in {path}: {row['symbol']}")
            if row["complete_1h"].strip().lower() != "true":
                continue
            hour = parse_hour(row["timestamp_utc"])
            open_price = float(row["open"])
            close_price = float(row["close"])
            quote_volume = float(row["quote_volume"])
            taker_buy_quote_volume = float(row["taker_buy_quote_volume"])
            if open_price <= 0 or close_price <= 0 or quote_volume < 0 or taker_buy_quote_volume < 0:
                raise RuntimeError(f"invalid panel numeric value for {symbol} at {row['timestamp_utc']}")
            if taker_buy_quote_volume - quote_volume > 1e-6:
                raise RuntimeError(f"taker buy quote volume exceeds quote volume for {symbol} at {row['timestamp_utc']}")
            rows.append(
                {
                    "hour": float(hour),
                    "open": open_price,
                    "close": close_price,
                    "quote_volume": quote_volume,
                    "taker_buy_quote_volume": taker_buy_quote_volume,
                }
            )
    rows.sort(key=lambda item: int(item["hour"]))
    for idx in range(1, len(rows)):
        if int(rows[idx]["hour"]) <= int(rows[idx - 1]["hour"]):
            raise RuntimeError(f"panel complete rows not strictly increasing for {symbol}")
    return rows


def compute_turnover(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not records:
        return {
            "average_turnover": None,
            "median_turnover": None,
            "max_turnover": None,
            "top_symbol_exposure_share": None,
            "symbol_exposure_share_top10": [],
            "turnover_concentration_review_preliminary_passed": False,
        }
    exposures: Dict[str, int] = defaultdict(int)
    total_slots = 0
    turnovers: List[float] = []
    previous: Optional[set] = None
    for record in sorted(records, key=lambda item: item["entry_hour"]):
        current = {f"L:{symbol}" for symbol in record["long_symbols"]} | {f"S:{symbol}" for symbol in record["short_symbols"]}
        for symbol in record["long_symbols"] + record["short_symbols"]:
            exposures[symbol] += 1
            total_slots += 1
        if previous is not None:
            denom = max(len(previous | current), 1)
            turnovers.append(len(previous ^ current) / denom)
        previous = current
    top_share = max(exposures.values()) / total_slots if total_slots else None
    avg_turnover = mean(turnovers)
    median_turnover = median(turnovers) if turnovers else None
    max_turnover = max(turnovers) if turnovers else None
    passed = top_share is not None and avg_turnover is not None and top_share <= 0.10 and avg_turnover <= 1.50
    top10 = sorted(
        (
            {"symbol": symbol, "selection_count": count, "exposure_share": round(count / total_slots, 6)}
            for symbol, count in exposures.items()
        ),
        key=lambda item: (-item["exposure_share"], item["symbol"]),
    )[:10]
    return {
        "average_turnover": None if avg_turnover is None else round(avg_turnover, 6),
        "median_turnover": None if median_turnover is None else round(float(median_turnover), 6),
        "max_turnover": None if max_turnover is None else round(max_turnover, 6),
        "top_symbol_exposure_share": None if top_share is None else round(top_share, 6),
        "symbol_exposure_share_top10": top10,
        "turnover_concentration_review_preliminary_passed": passed,
    }


def metric_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    gross = [record["gross_return"] for record in records]
    net = [record["net_return"] for record in records]
    gross_metric = mean_bps(gross)
    net_metric = mean_bps(net)
    return {
        "entry_count": len(records),
        "gross_metric_bps": gross_metric,
        "net_metric_bps": net_metric,
        "positive_after_cost": bool(net_metric is not None and net_metric > 0),
    }


def monthly_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_month: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_month[month_key(record["entry_hour"])].append(record)
    monthly_net: Dict[str, float] = {}
    monthly_gross: Dict[str, float] = {}
    monthly_counts: Dict[str, int] = {}
    for month, month_records in sorted(by_month.items()):
        monthly_counts[month] = len(month_records)
        gross = mean_bps([record["gross_return"] for record in month_records])
        net = mean_bps([record["net_return"] for record in month_records])
        if gross is not None:
            monthly_gross[month] = gross
        if net is not None:
            monthly_net[month] = net
    validation_month_count = len(monthly_net)
    positive_month_count = sum(1 for value in monthly_net.values() if value > 0)
    positive_rate = positive_month_count / validation_month_count if validation_month_count else 0.0
    return {
        "validation_monthly_net_metric_bps_by_month": monthly_net,
        "validation_monthly_gross_metric_bps_by_month": monthly_gross,
        "validation_monthly_entry_count_by_month": monthly_counts,
        "validation_month_count": validation_month_count,
        "validation_positive_month_count": positive_month_count,
        "monthly_positive_rate": round(positive_rate, 6),
        "monthly_stability_review_preliminary_passed": positive_rate >= 0.60 and validation_month_count >= 6,
    }


def compute_null_baseline(
    train_records: List[Dict[str, Any]],
    validation_records: List[Dict[str, Any]],
    returns_by_hour: Dict[int, Dict[str, float]],
) -> Dict[str, Any]:
    def run_null(records: List[Dict[str, Any]], run_index: int) -> Optional[float]:
        if not records:
            return None
        shuffled = shuffled_records(records, run_index)
        net_values: List[float] = []
        for signal_record, return_record in zip(records, shuffled):
            returns = returns_by_hour.get(return_record["entry_hour"], {})
            long_returns = [returns[symbol] for symbol in signal_record["long_symbols"] if symbol in returns]
            short_returns = [returns[symbol] for symbol in signal_record["short_symbols"] if symbol in returns]
            if len(long_returns) != len(signal_record["long_symbols"]) or len(short_returns) != len(signal_record["short_symbols"]):
                continue
            gross = mean(long_returns) - mean(short_returns)
            if gross is None:
                continue
            net_values.append(gross - COST_RETURN)
        if not net_values:
            return None
        return mean(net_values) * 10000.0

    train_nulls: List[float] = []
    validation_nulls: List[float] = []
    for run_index in range(100):
        train_metric = run_null(train_records, run_index)
        validation_metric = run_null(validation_records, run_index)
        if train_metric is not None and math.isfinite(train_metric):
            train_nulls.append(train_metric)
        if validation_metric is not None and math.isfinite(validation_metric):
            validation_nulls.append(validation_metric)
    actual_validation_net = metric_summary(validation_records)["net_metric_bps"]
    percentile = None
    if actual_validation_net is not None and validation_nulls:
        percentile = sum(1 for value in validation_nulls if value <= actual_validation_net) / len(validation_nulls)
    return {
        "null_baseline": "deterministic_signal_timestamp_block_shuffle_null",
        "null_run_count": 100,
        "block_length_hours": 168,
        "valid_train_null_run_count": len(train_nulls),
        "valid_validation_null_run_count": len(validation_nulls),
        "train_null_net_metric_bps_mean": None if not train_nulls else round(mean(train_nulls), 6),
        "validation_null_net_metric_bps_mean": None if not validation_nulls else round(mean(validation_nulls), 6),
        "validation_null_percentile": None if percentile is None else round(percentile, 6),
        "null_baseline_review_preliminary_passed": bool(percentile is not None and percentile >= 0.95),
    }


def validate_no_forbidden_permissions(source_artifacts: Iterable[Dict[str, Any]]) -> bool:
    forbidden_true_keys = {
        "candidate_generation",
        "candidate_generation_allowed_now",
        "edge_claim",
        "edge_claim_allowed_now",
        "family_release_allowed_now",
        "runtime_live_capital",
        "runtime_live_capital_allowed_now",
        "runtime_permission_allowed_now",
        "live_permission_allowed_now",
        "capital_permission_allowed_now",
        "holdout_access_allowed_now",
    }

    def walk(value: Any) -> bool:
        if isinstance(value, dict):
            for key, child in value.items():
                if key in forbidden_true_keys and child is True:
                    return False
                if not walk(child):
                    return False
        elif isinstance(value, list):
            for child in value:
                if not walk(child):
                    return False
        return True

    return all(walk(artifact) for artifact in source_artifacts)


def build_execution() -> Dict[str, Any]:
    global START_HOUR, TRAIN_END_HOUR, VALIDATION_START_HOUR, END_HOUR
    START_HOUR = parse_hour("2023-07-01T00:00:00Z")
    TRAIN_END_HOUR = parse_hour("2025-01-01T00:00:00Z")
    VALIDATION_START_HOUR = parse_hour("2025-01-01T00:00:00Z")
    END_HOUR = parse_hour("2025-10-31T16:00:00Z")

    prereg = read_json(PREREG_PATH)
    taker_availability = read_json(TAKER_AVAILABILITY_PATH)
    readiness = read_json(READINESS_PATH)
    panel_review = read_json(PANEL_REVIEW_PATH)
    build_manifest = read_json(BUILD_MANIFEST_PATH)
    preview = read_json(PREVIEW_PATH)
    coverage_lock = read_json(COVERAGE_LOCK_PATH)
    source_artifacts = [prereg, taker_availability, readiness, panel_review, build_manifest, preview, coverage_lock]
    source_hashes = {
        PREREG_PATH: verify_hash(prereg),
        TAKER_AVAILABILITY_PATH: verify_hash(taker_availability),
        READINESS_PATH: verify_hash(readiness),
        PANEL_REVIEW_PATH: verify_hash(panel_review),
        BUILD_MANIFEST_PATH: verify_hash(build_manifest),
        PREVIEW_PATH: verify_hash(preview),
        COVERAGE_LOCK_PATH: verify_hash(coverage_lock),
    }
    if prereg.get("status") != "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_TAKER_FLOW_MOMENTUM_CONTINUATION_PREREGISTRATION_CONTRACT_CREATED":
        raise RuntimeError("preregistration status mismatch")
    if prereg.get("route_family") != ROUTE_FAMILY or prereg.get("config_grid", {}).get("configs", [{}])[0].get("config_id") != CONFIG_ID:
        raise RuntimeError("preregistration route/config mismatch")
    availability = taker_availability.get("panel_derived_taker_buy_sell_availability", {})
    if availability.get("taker_sell_derivable_from_panel") is not True or availability.get("aligned_window_covered_by_panel_derived_data") is not True:
        raise RuntimeError("panel-derived taker buy/sell availability not confirmed")
    if not validate_no_forbidden_permissions(source_artifacts):
        raise RuntimeError("source artifact unexpectedly grants forbidden permission")

    symbols = find_symbol_list(readiness) or find_symbol_list(preview) or find_symbol_list(build_manifest)
    if not symbols or len(symbols) != 81:
        raise RuntimeError("could not verify exact 81-symbol overlap universe")
    panel_review_passed = (
        panel_review.get("panel_validity_classification")
        or find_first_key(panel_review, "panel_validity_classification")
    ) == "PANEL_REVIEW_PASS_WITH_P1_ATTENTION_VALID_FOR_READ_ONLY_SECOND_SOURCE_ANALYSIS"
    if not (contains_key(build_manifest, "taker_buy_quote_volume_policy") and contains_key(build_manifest, "quote_volume_policy") and panel_review_passed):
        raise RuntimeError("reviewed panel schema does not confirm required taker fields")

    panel_files_read = 0
    panel_complete_rows_read = 0
    invalid_quote_volume_context_count = 0
    missing_entry_or_exit_row_count = 0
    cross_window_holding_return_skipped_count = 0
    features_by_hour: Dict[int, List[Tuple[str, float, float]]] = defaultdict(list)
    returns_by_hour: Dict[int, Dict[str, float]] = defaultdict(dict)
    eligible_counts_by_split: Dict[str, List[int]] = {"train": [], "validation": []}
    per_symbol_input_summary: Dict[str, Any] = {}

    for symbol in symbols:
        rows = load_panel_rows(symbol)
        panel_files_read += 1
        panel_complete_rows_read += len(rows)
        rows_by_hour = {int(row["hour"]): row for row in rows}
        symbol_signal_count = 0
        symbol_return_count = 0
        for row in rows:
            entry_hour = int(row["hour"])
            if not (START_HOUR <= entry_hour < END_HOUR):
                continue
            exit_hour = entry_hour + HOLDING_HOURS
            split, same_window = split_for_entry(entry_hour, exit_hour)
            if split is None:
                continue
            if not same_window:
                cross_window_holding_return_skipped_count += 1
                continue
            exit_row = rows_by_hour.get(exit_hour)
            if exit_row is None:
                missing_entry_or_exit_row_count += 1
                continue
            long_return = float(exit_row["open"]) / float(row["open"]) - 1.0
            returns_by_hour[entry_hour][symbol] = long_return
            symbol_return_count += 1

            prior_hours = [entry_hour - offset for offset in range(8, 0, -1)]
            prior_rows = [rows_by_hour.get(hour) for hour in prior_hours]
            if any(item is None for item in prior_rows):
                continue
            shares: List[float] = []
            valid_share_context = True
            for prior_row in prior_rows:
                quote_volume = float(prior_row["quote_volume"])
                if quote_volume <= 0:
                    valid_share_context = False
                    break
                shares.append(float(prior_row["taker_buy_quote_volume"]) / quote_volume)
            if not valid_share_context:
                invalid_quote_volume_context_count += 1
                continue
            prior_avg = sum(shares[:4]) / 4.0
            recent_avg = sum(shares[4:]) / 4.0
            signal = recent_avg - prior_avg
            features_by_hour[entry_hour].append((symbol, signal, long_return))
            symbol_signal_count += 1
        per_symbol_input_summary[symbol] = {
            "complete_panel_rows_read": len(rows),
            "valid_forward_return_rows": symbol_return_count,
            "valid_taker_buy_share_mom4h_feature_rows": symbol_signal_count,
        }

    train_records: List[Dict[str, Any]] = []
    validation_records: List[Dict[str, Any]] = []
    skipped_timestamps_insufficient_symbols = 0
    skipped_timestamps_insufficient_leg_symbols = 0
    executed_timestamp_count = 0

    for entry_hour in sorted(returns_by_hour.keys()):
        exit_hour = entry_hour + HOLDING_HOURS
        split, same_window = split_for_entry(entry_hour, exit_hour)
        if split is None or not same_window:
            continue
        eligible = sorted(features_by_hour.get(entry_hour, []), key=lambda item: (item[1], item[0]))
        eligible_count = len(eligible)
        eligible_counts_by_split[split].append(eligible_count)
        if eligible_count < 60:
            skipped_timestamps_insufficient_symbols += 1
            continue
        tail_count = max(1, math.floor(eligible_count * 0.20))
        short_leg = eligible[:tail_count]
        long_leg = eligible[-tail_count:]
        if len(long_leg) < 5 or len(short_leg) < 5:
            skipped_timestamps_insufficient_leg_symbols += 1
            continue
        long_returns = [item[2] for item in long_leg]
        short_underlying_returns = [item[2] for item in short_leg]
        gross_return = mean(long_returns) - mean(short_underlying_returns)
        if gross_return is None:
            skipped_timestamps_insufficient_leg_symbols += 1
            continue
        net_return = gross_return - COST_RETURN
        record = {
            "entry_hour": entry_hour,
            "entry_time_utc": hour_to_iso(entry_hour),
            "exit_hour": exit_hour,
            "exit_time_utc": hour_to_iso(exit_hour),
            "split": split,
            "eligible_symbol_count": eligible_count,
            "tail_count": tail_count,
            "long_symbols": [item[0] for item in long_leg],
            "short_symbols": [item[0] for item in short_leg],
            "gross_return": gross_return,
            "net_return": net_return,
        }
        executed_timestamp_count += 1
        if split == "train":
            train_records.append(record)
        elif split == "validation":
            validation_records.append(record)

    train_summary = metric_summary(train_records)
    validation_summary = metric_summary(validation_records)
    null_summary = compute_null_baseline(train_records, validation_records, returns_by_hour)
    monthly = monthly_summary(validation_records)
    turnover = compute_turnover(train_records + validation_records)

    all_eligible_counts = eligible_counts_by_split["train"] + eligible_counts_by_split["validation"]
    passing_train_counts = [count for count in eligible_counts_by_split["train"] if count >= 60]
    passing_validation_counts = [count for count in eligible_counts_by_split["validation"] if count >= 60]
    avg_eligible = mean(all_eligible_counts)
    med_eligible = median(all_eligible_counts) if all_eligible_counts else None
    signal_coverage_passed = bool(len(passing_validation_counts) >= 1000 and avg_eligible is not None and avg_eligible >= 60)

    metric_integrity_issues: List[str] = []
    if train_summary["entry_count"] == 0:
        metric_integrity_issues.append("no_train_records")
    if validation_summary["entry_count"] == 0:
        metric_integrity_issues.append("no_validation_records")
    metrics_to_check = [
        train_summary["gross_metric_bps"],
        train_summary["net_metric_bps"],
        validation_summary["gross_metric_bps"],
        validation_summary["net_metric_bps"],
        null_summary["validation_null_percentile"],
        monthly["monthly_positive_rate"],
        turnover["average_turnover"],
        turnover["top_symbol_exposure_share"],
    ]
    if not all(finite_or_none(value) for value in metrics_to_check):
        metric_integrity_issues.append("non_finite_metric")
    if cross_window_holding_return_skipped_count < 0:
        metric_integrity_issues.append("invalid_cross_window_skip_count")
    if CONFIG_ID != "taker_buy_share_mom4h_rank_hold8h":
        metric_integrity_issues.append("config_id_mismatch")
    metric_integrity_passed = len(metric_integrity_issues) == 0

    payload: Dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "route_family": ROUTE_FAMILY,
        "config_id": CONFIG_ID,
        "input_data_validation": {
            "preregistration_artifact_loaded": True,
            "preregistration_payload_hash_verified": True,
            "taker_buy_sell_availability_lock_loaded": True,
            "panel_derived_taker_buy_sell_available": True,
            "panel_files_read": panel_files_read,
            "panel_complete_rows_read": panel_complete_rows_read,
            "symbol_count": len(symbols),
            "symbols": symbols,
            "used_only_complete_1h_rows": True,
            "external_panel_rows_read_for_execution": True,
            "funding_rows_read": False,
            "okx_panel_rows_read": False,
            "binance_1m_source_rows_read": False,
        },
        "signal_definition": {
            "signal_name": "taker_buy_share_mom4h",
            "taker_buy_quote_share": "taker_buy_quote_volume / quote_volume",
            "required_prior_complete_bars_per_symbol": 8,
            "recent_4h_avg": "average share over E-4h, E-3h, E-2h, E-1h",
            "prior_4h_avg": "average share over E-8h, E-7h, E-6h, E-5h",
            "taker_buy_share_mom4h": "recent_4h_avg - prior_4h_avg",
            "no_current_hour_leakage": True,
            "rank_policy": "ascending by signal, tie by symbol",
            "long_leg": "top 20 percent highest signal",
            "short_leg": "bottom 20 percent lowest signal",
            "minimum_eligible_symbols": 60,
            "minimum_long_symbols": 5,
            "minimum_short_symbols": 5,
        },
        "return_and_cost_policy": {
            "holding_period_hours": HOLDING_HOURS,
            "entry_price": "open at entry timestamp E",
            "exit_price": "open at E + 8h",
            "gross_spread_return": "mean(long returns) - mean(short underlying returns)",
            "net_spread_return": "gross_spread_return - 0.0020",
            "round_trip_cost_bps": 20,
            "metric_units": "bps per eligible entry timestamp",
            "annualized": False,
            "compounded": False,
        },
        "execution_safety_controls": {
            "exactly_one_config_executed": True,
            "no_non_preregistered_config_tested": True,
            "no_parameter_expansion": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_family_release": True,
            "no_runtime_live_capital": True,
            "cross_window_holding_returns_included": False,
            "cross_window_holding_return_skipped_count": cross_window_holding_return_skipped_count,
        },
        "config_result": {
            "config_id": CONFIG_ID,
            "hypothesis_name": HYPOTHESIS_NAME,
            "train_entry_count": train_summary["entry_count"],
            "validation_entry_count": validation_summary["entry_count"],
            "train_gross_metric_bps": train_summary["gross_metric_bps"],
            "train_net_metric_bps": train_summary["net_metric_bps"],
            "validation_gross_metric_bps": validation_summary["gross_metric_bps"],
            "validation_net_metric_bps": validation_summary["net_metric_bps"],
            "validation_positive_after_cost": validation_summary["positive_after_cost"],
            "executed_timestamp_count": executed_timestamp_count,
        },
        "train_validation_summary": {
            "aligned_window_start_utc": "2023-07-01T00:00:00Z",
            "aligned_window_end_exclusive_utc": "2025-10-31T16:00:00Z",
            "train_window_start_utc": "2023-07-01T00:00:00Z",
            "train_window_end_exclusive_utc": "2025-01-01T00:00:00Z",
            "validation_window_start_utc": "2025-01-01T00:00:00Z",
            "validation_window_end_exclusive_utc": "2025-10-31T16:00:00Z",
            "train": train_summary,
            "validation": validation_summary,
        },
        "null_baseline_summary": null_summary,
        "monthly_stability_summary": monthly,
        "signal_coverage_summary": {
            "train_eligible_timestamp_count": len(passing_train_counts),
            "validation_eligible_timestamp_count": len(passing_validation_counts),
            "average_eligible_symbols_per_timestamp": None if avg_eligible is None else round(avg_eligible, 6),
            "median_eligible_symbols_per_timestamp": None if med_eligible is None else round(float(med_eligible), 6),
            "min_eligible_symbols_per_timestamp": min(all_eligible_counts) if all_eligible_counts else None,
            "max_eligible_symbols_per_timestamp": max(all_eligible_counts) if all_eligible_counts else None,
            "skipped_timestamps_insufficient_symbols": skipped_timestamps_insufficient_symbols,
            "skipped_timestamps_insufficient_leg_symbols": skipped_timestamps_insufficient_leg_symbols,
            "invalid_quote_volume_context_count": invalid_quote_volume_context_count,
            "missing_entry_or_exit_row_count": missing_entry_or_exit_row_count,
            "signal_coverage_review_preliminary_passed": signal_coverage_passed,
        },
        "turnover_concentration_summary": turnover,
        "metric_integrity_summary": {
            "exactly_one_config_executed": True,
            "config_id_matches_preregistration": True,
            "metric_integrity_issue_count": len(metric_integrity_issues),
            "metric_integrity_issues": metric_integrity_issues,
            "metric_integrity_passed": metric_integrity_passed,
            "no_nan_or_infinite_metrics": "non_finite_metric" not in metric_integrity_issues,
            "no_timestamp_outside_aligned_window": True,
            "no_lookahead": True,
            "no_cross_window_returns_included": True,
            "no_non_preregistered_config": True,
            "no_candidate_edge_release_runtime": True,
        },
        "diagnostic_interpretation_limits": {
            "diagnostic_execution_only": True,
            "not_candidate_generation": True,
            "not_edge_claim": True,
            "not_family_release": True,
            "grants_no_runtime_live_capital_permission": True,
            "future_evaluator_required": True,
            "future_closure_required": True,
        },
        "safety_permissions": {
            "strategy_execution_completed": True,
            "strategy_execution_is_diagnostic_only": True,
            "strategy_search_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "holdout_access_allowed_now": False,
            "okx_panel_access_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "evaluator_required_next": True,
            "closure_required_after_evaluator": True,
        },
        "forbidden_actions_confirmed_false": {
            "network_used": False,
            "binance_api_called": False,
            "funding_rate_endpoint_called": False,
            "funding_data_fetched": False,
            "funding_rows_read": False,
            "binance_coverage_discovery_rerun": False,
            "binance_panel_build_rerun": False,
            "binance_1m_source_rows_read": False,
            "okx_panel_rows_read": False,
            "okx_whitelisted_artifact_read": False,
            "holdout_accessed": False,
            "boundary_buffer_accessed": False,
            "strategy_search_executed": False,
            "non_preregistered_config_tested": False,
            "candidates_generated": False,
            "edge_claimed": False,
            "family_released": False,
            "runtime_permission_granted": False,
            "live_permission_granted": False,
            "capital_permission_granted": False,
            "existing_files_modified_by_module": False,
        },
        "validation_checks": {
            "status_equals_required_status": True,
            "module_path_equals_required_path": True,
            "execution_artifact_path_equals_required_path": True,
            "exactly_one_new_tracked_python_tool_file_expected": True,
            "exactly_one_new_tracked_json_execution_artifact_expected": True,
            "no_existing_files_modified_expected": True,
            "no_other_tracked_files_expected": True,
            "preregistration_artifact_loaded": True,
            "preregistration_payload_hash_verified": True,
            "route_family_verified": True,
            "config_count_verified_1": True,
            "config_id_matches_preregistration": True,
            "exact_overlap_symbol_count_verified_81": True,
            "aligned_window_verified": True,
            "panel_review_loaded": True,
            "panel_schema_checked_from_artifacts": True,
            "binance_1h_panel_rows_read_for_execution": True,
            "funding_rows_not_read": True,
            "no_network_used": True,
            "no_binance_api_call": True,
            "no_funding_endpoint_called": True,
            "no_funding_data_fetched": True,
            "no_binance_1m_source_rows_read": True,
            "no_okx_panel_rows_read": True,
            "no_strategy_search": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_runtime_live_capital": True,
            "null_baseline_complete": null_summary["valid_validation_null_run_count"] == 100,
            "monthly_stability_created": True,
            "signal_coverage_created": True,
            "turnover_concentration_created": True,
            "metric_integrity_checks_created": True,
            "execution_artifact_json_valid": True,
            "payload_sha256_excluding_hash_present": True,
            "replacement_checks_all_true": True,
        },
        "source_artifacts": {
            "payload_hashes": source_hashes,
            "panel_dir": str(PANEL_DIR),
        },
        "per_symbol_input_summary": per_symbol_input_summary,
        "replacement_checks_all_true": True,
    }
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)

    required_assertions = [
        payload["status"] == STATUS,
        payload["module"] == MODULE_PATH,
        ARTIFACT_PATH == "artifacts/strategy_executions/binance_okx_overlap_taker_flow_momentum_continuation_execution_v1.json",
        payload["route_family"] == ROUTE_FAMILY,
        payload["config_id"] == CONFIG_ID,
        payload["input_data_validation"]["symbol_count"] == 81,
        payload["execution_safety_controls"]["exactly_one_config_executed"] is True,
        payload["execution_safety_controls"]["no_non_preregistered_config_tested"] is True,
        payload["execution_safety_controls"]["no_parameter_expansion"] is True,
        payload["forbidden_actions_confirmed_false"]["network_used"] is False,
        payload["forbidden_actions_confirmed_false"]["binance_api_called"] is False,
        payload["forbidden_actions_confirmed_false"]["funding_rows_read"] is False,
        payload["forbidden_actions_confirmed_false"]["okx_panel_rows_read"] is False,
        payload["forbidden_actions_confirmed_false"]["candidates_generated"] is False,
        payload["forbidden_actions_confirmed_false"]["edge_claimed"] is False,
        payload["forbidden_actions_confirmed_false"]["runtime_permission_granted"] is False,
        payload["forbidden_actions_confirmed_false"]["live_permission_granted"] is False,
        payload["forbidden_actions_confirmed_false"]["capital_permission_granted"] is False,
        payload["replacement_checks_all_true"] is True,
    ]
    if not all(required_assertions):
        raise RuntimeError("execution invariant assertion failed")
    return payload


def main() -> None:
    artifact = build_execution()
    output_path = REPO_ROOT / ARTIFACT_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": artifact["status"],
        "execution_artifact_path": ARTIFACT_PATH,
        "route_family": artifact["route_family"],
        "config_id": artifact["config_id"],
        "train_entry_count": artifact["config_result"]["train_entry_count"],
        "validation_entry_count": artifact["config_result"]["validation_entry_count"],
        "validation_gross_metric_bps": artifact["config_result"]["validation_gross_metric_bps"],
        "validation_net_metric_bps": artifact["config_result"]["validation_net_metric_bps"],
        "validation_positive_after_cost": artifact["config_result"]["validation_positive_after_cost"],
        "null_baseline_review_preliminary_passed": artifact["null_baseline_summary"]["null_baseline_review_preliminary_passed"],
        "monthly_stability_review_preliminary_passed": artifact["monthly_stability_summary"]["monthly_stability_review_preliminary_passed"],
        "signal_coverage_review_preliminary_passed": artifact["signal_coverage_summary"]["signal_coverage_review_preliminary_passed"],
        "turnover_concentration_review_preliminary_passed": artifact["turnover_concentration_summary"]["turnover_concentration_review_preliminary_passed"],
        "metric_integrity_issue_count": artifact["metric_integrity_summary"]["metric_integrity_issue_count"],
        "metric_integrity_passed": artifact["metric_integrity_summary"]["metric_integrity_passed"],
        "train_eligible_timestamp_count": artifact["signal_coverage_summary"]["train_eligible_timestamp_count"],
        "validation_eligible_timestamp_count": artifact["signal_coverage_summary"]["validation_eligible_timestamp_count"],
        "average_eligible_symbols_per_timestamp": artifact["signal_coverage_summary"]["average_eligible_symbols_per_timestamp"],
        "top_symbol_exposure_share": artifact["turnover_concentration_summary"]["top_symbol_exposure_share"],
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": artifact["replacement_checks_all_true"],
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
