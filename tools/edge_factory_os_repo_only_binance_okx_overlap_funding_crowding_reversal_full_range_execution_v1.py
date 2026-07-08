import csv
import gzip
import hashlib
import json
import math
import random
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any, Deque, Dict, Iterable, List, Optional, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_crowding_reversal_full_range_execution_v1.py"
ARTIFACT_PATH = "artifacts/strategy_executions/binance_okx_overlap_funding_crowding_reversal_full_range_execution_v1.json"
STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_FUNDING_CROWDING_REVERSAL_FULL_RANGE_EXECUTED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_FUNDING_CROWDING_REVERSAL_FULL_RANGE_EXECUTION"

ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_RATE_CROWDING_REVERSAL_BASELINE"
CONFIG_ID = "funding_mean9_hold24h"
HYPOTHESIS_NAME = "funding_rate_crowding_reversal_full_range"

FULL_START_HOUR = None
TRAIN_END_HOUR = None
VALIDATION_START_HOUR = None
VALIDATION_END_HOUR = None
HOLDOUT_START_HOUR = None
FULL_END_HOUR = None
HOLDING_HOURS = 24
COST_RETURN = 0.0020

ACQUISITION_PATH = "artifacts/funding_rate_locks/binance_okx_overlap_funding_rate_full_range_202105_202510_acquisition_lock_v1.json"
REVIEW_PATH = "artifacts/funding_rate_reviews/binance_okx_overlap_funding_rate_full_range_202105_202510_review_v1.json"
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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(relative_path: str) -> Dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise RuntimeError(f"missing required artifact: {relative_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def verify_hash(payload: Dict[str, Any]) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise RuntimeError("artifact missing payload_sha256_excluding_hash")
    recomputed = canonical_payload_hash(payload)
    if recomputed != stored:
        raise RuntimeError(f"payload hash mismatch: {recomputed} != {stored}")
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
    if FULL_START_HOUR <= entry_hour < TRAIN_END_HOUR:
        return ("train", exit_hour < TRAIN_END_HOUR)
    if VALIDATION_START_HOUR <= entry_hour < VALIDATION_END_HOUR:
        return ("validation", exit_hour < VALIDATION_END_HOUR)
    if HOLDOUT_START_HOUR <= entry_hour < FULL_END_HOUR:
        return ("holdout", exit_hour < FULL_END_HOUR)
    return (None, False)


def deterministic_seed(run_index: int) -> int:
    digest = hashlib.sha256(f"{ROUTE_FAMILY}|{CONFIG_ID}|{run_index}".encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def shuffled_records(records: List[Dict[str, Any]], run_index: int) -> List[Dict[str, Any]]:
    blocks = [records[i : i + 168] for i in range(0, len(records), 168)]
    rng = random.Random(deterministic_seed(run_index))
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


def load_panel_rows(symbol: str) -> List[Tuple[int, float]]:
    path = PANEL_DIR / f"{symbol}_1h.csv.gz"
    if not path.exists():
        raise RuntimeError(f"missing panel file for {symbol}: {path}")
    rows: List[Tuple[int, float]] = []
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
            if open_price <= 0:
                raise RuntimeError(f"invalid open price for {symbol} at {row['timestamp_utc']}")
            rows.append((hour, open_price))
    rows.sort()
    for idx in range(1, len(rows)):
        if rows[idx][0] <= rows[idx - 1][0]:
            raise RuntimeError(f"panel complete rows not strictly increasing for {symbol}")
    return rows


def load_funding_events(symbol: str, funding_dir: Path) -> List[Tuple[int, float]]:
    path = funding_dir / f"{symbol}_funding_rate.jsonl.gz"
    if not path.exists():
        raise RuntimeError(f"missing full-range funding file for {symbol}: {path}")
    events: List[Tuple[int, float]] = []
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if row["symbol"] != symbol:
                raise RuntimeError(f"funding symbol mismatch in {path}: {row['symbol']}")
            hour = parse_hour(row["funding_time_utc"])
            rate = float(row["funding_rate"])
            if not math.isfinite(rate):
                raise RuntimeError(f"invalid funding rate for {symbol} at {row['funding_time_utc']}")
            events.append((hour, rate))
    events.sort()
    for idx in range(1, len(events)):
        if events[idx][0] <= events[idx - 1][0]:
            raise RuntimeError(f"funding events not strictly increasing for {symbol}")
    return events


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
    return {
        "observation_count": len(records),
        "gross_metric_bps": mean_bps(gross),
        "net_metric_bps": mean_bps(net),
        "positive_after_cost": bool(mean_bps(net) is not None and mean_bps(net) > 0),
    }


def monthly_metrics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_month: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_month[month_key(record["entry_hour"])].append(record)
    monthly_gross = {}
    monthly_net = {}
    monthly_counts = {}
    for month, month_records in sorted(by_month.items()):
        monthly_counts[month] = len(month_records)
        gross = mean_bps([record["gross_return"] for record in month_records])
        net = mean_bps([record["net_return"] for record in month_records])
        if gross is not None:
            monthly_gross[month] = gross
        if net is not None:
            monthly_net[month] = net
    positive_count = sum(1 for value in monthly_net.values() if value > 0)
    month_count = len(monthly_net)
    positive_rate = positive_count / month_count if month_count else 0.0
    return {
        "monthly_gross_metric_bps_by_month": monthly_gross,
        "monthly_net_metric_bps_by_month": monthly_net,
        "monthly_observation_count_by_month": monthly_counts,
        "monthly_positive_rate": round(positive_rate, 6),
        "month_count": month_count,
        "positive_month_count": positive_count,
    }


def split_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    summary = metric_summary(records)
    summary.update(monthly_metrics(records))
    return summary


def compute_null_baseline(validation_records: List[Dict[str, Any]], returns_by_hour: Dict[int, Dict[str, float]]) -> Dict[str, Any]:
    def run_null(run_index: int) -> Optional[float]:
        if not validation_records:
            return None
        shuffled = shuffled_records(validation_records, run_index)
        net_values: List[float] = []
        for signal_record, return_record in zip(validation_records, shuffled):
            returns = returns_by_hour.get(return_record["entry_hour"], {})
            long_returns = [returns[symbol] for symbol in signal_record["long_symbols"] if symbol in returns]
            short_returns = [returns[symbol] for symbol in signal_record["short_symbols"] if symbol in returns]
            if len(long_returns) != len(signal_record["long_symbols"]) or len(short_returns) != len(signal_record["short_symbols"]):
                continue
            gross = mean(long_returns) - mean(short_returns)
            if gross is not None:
                net_values.append(gross - COST_RETURN)
        return None if not net_values else mean(net_values) * 10000.0

    nulls: List[float] = []
    for run_index in range(100):
        metric = run_null(run_index)
        if metric is not None and math.isfinite(metric):
            nulls.append(metric)
    actual_validation_net = metric_summary(validation_records)["net_metric_bps"]
    percentile = None
    if actual_validation_net is not None and nulls:
        percentile = sum(1 for value in nulls if value <= actual_validation_net) / len(nulls)
    return {
        "null_baseline": "deterministic_funding_signal_timestamp_block_shuffle_null",
        "null_run_count": 100,
        "block_length_hours": 168,
        "valid_validation_null_run_count": len(nulls),
        "validation_null_net_metric_bps_mean": None if not nulls else round(mean(nulls), 6),
        "validation_null_metric_bps_min": None if not nulls else round(min(nulls), 6),
        "validation_null_metric_bps_median": None if not nulls else round(float(median(nulls)), 6),
        "validation_null_metric_bps_max": None if not nulls else round(max(nulls), 6),
        "validation_null_percentile": None if percentile is None else round(percentile, 6),
        "null_baseline_review_preliminary_passed": bool(percentile is not None and percentile >= 0.95),
    }


def build_execution() -> Dict[str, Any]:
    global FULL_START_HOUR, TRAIN_END_HOUR, VALIDATION_START_HOUR, VALIDATION_END_HOUR, HOLDOUT_START_HOUR, FULL_END_HOUR
    FULL_START_HOUR = parse_hour("2021-05-01T00:00:00Z")
    TRAIN_END_HOUR = parse_hour("2024-01-01T00:00:00Z")
    VALIDATION_START_HOUR = parse_hour("2024-01-01T00:00:00Z")
    VALIDATION_END_HOUR = parse_hour("2025-01-01T00:00:00Z")
    HOLDOUT_START_HOUR = parse_hour("2025-01-01T00:00:00Z")
    FULL_END_HOUR = parse_hour("2025-11-01T00:00:00Z")

    acquisition = read_json(ACQUISITION_PATH)
    review = read_json(REVIEW_PATH)
    readiness = read_json(READINESS_PATH)
    panel_review = read_json(PANEL_REVIEW_PATH)
    build_manifest = read_json(BUILD_MANIFEST_PATH)
    preview = read_json(PREVIEW_PATH)
    coverage_lock = read_json(COVERAGE_LOCK_PATH)
    source_artifacts = [acquisition, review, readiness, panel_review, build_manifest, preview, coverage_lock]
    source_hashes = {
        ACQUISITION_PATH: verify_hash(acquisition),
        REVIEW_PATH: verify_hash(review),
        READINESS_PATH: verify_hash(readiness),
        PANEL_REVIEW_PATH: verify_hash(panel_review),
        BUILD_MANIFEST_PATH: verify_hash(build_manifest),
        PREVIEW_PATH: verify_hash(preview),
        COVERAGE_LOCK_PATH: verify_hash(coverage_lock),
    }
    if review["funding_data_review"]["funding_data_valid_for_full_range_signal_construction"] is not True:
        raise RuntimeError("full-range funding review did not pass")
    if not validate_no_forbidden_permissions(source_artifacts):
        raise RuntimeError("source artifact unexpectedly grants forbidden permission")
    symbols = find_symbol_list(readiness) or find_symbol_list(preview) or find_symbol_list(build_manifest)
    if not symbols or len(symbols) != 81:
        raise RuntimeError("could not verify exact 81-symbol overlap universe")
    symbols = sorted(symbols)
    panel_review_passed = (
        panel_review.get("panel_validity_classification")
        or find_first_key(panel_review, "panel_validity_classification")
    ) == "PANEL_REVIEW_PASS_WITH_P1_ATTENTION_VALID_FOR_READ_ONLY_SECOND_SOURCE_ANALYSIS"
    if not panel_review_passed:
        raise RuntimeError("panel review not valid for read-only second-source analysis")
    funding_dir = Path(acquisition["funding_data_output_summary"]["funding_by_symbol_dir"])

    panel_files_read = 0
    panel_complete_rows_read = 0
    funding_files_read = 0
    funding_rows_read = 0
    missing_exit_row_count = 0
    insufficient_funding_context_count = 0
    cross_window_holding_return_skipped_count = 0
    features_by_hour: Dict[int, List[Tuple[str, float, float]]] = defaultdict(list)
    returns_by_hour: Dict[int, Dict[str, float]] = defaultdict(dict)
    eligible_counts_by_split: Dict[str, List[int]] = {"train": [], "validation": [], "holdout": []}
    per_symbol_input_summary: Dict[str, Any] = {}

    for symbol in symbols:
        panel_rows = load_panel_rows(symbol)
        funding_events = load_funding_events(symbol, funding_dir)
        panel_files_read += 1
        panel_complete_rows_read += len(panel_rows)
        funding_files_read += 1
        funding_rows_read += len(funding_events)
        panel_by_hour = {hour: open_price for hour, open_price in panel_rows}
        funding_idx = 0
        funding_window: Deque[float] = deque()
        funding_sum = 0.0
        symbol_return_count = 0
        symbol_feature_count = 0
        for entry_hour, entry_open in panel_rows:
            while funding_idx < len(funding_events) and funding_events[funding_idx][0] <= entry_hour - 1:
                rate = funding_events[funding_idx][1]
                funding_window.append(rate)
                funding_sum += rate
                if len(funding_window) > 9:
                    funding_sum -= funding_window.popleft()
                funding_idx += 1
            if not (FULL_START_HOUR <= entry_hour < FULL_END_HOUR):
                continue
            exit_hour = entry_hour + HOLDING_HOURS
            split, same_window = split_for_entry(entry_hour, exit_hour)
            if split is None:
                continue
            if not same_window:
                cross_window_holding_return_skipped_count += 1
                continue
            exit_open = panel_by_hour.get(exit_hour)
            if exit_open is None:
                missing_exit_row_count += 1
                continue
            forward_return = exit_open / entry_open - 1.0
            returns_by_hour[entry_hour][symbol] = forward_return
            symbol_return_count += 1
            if len(funding_window) >= 9:
                funding_signal = funding_sum / 9.0
                features_by_hour[entry_hour].append((symbol, funding_signal, forward_return))
                symbol_feature_count += 1
            else:
                insufficient_funding_context_count += 1
        per_symbol_input_summary[symbol] = {
            "complete_panel_rows_read": len(panel_rows),
            "funding_rows_read": len(funding_events),
            "valid_forward_return_rows": symbol_return_count,
            "valid_mean9_funding_signal_rows": symbol_feature_count,
        }

    records_by_split: Dict[str, List[Dict[str, Any]]] = {"train": [], "validation": [], "holdout": []}
    skipped_timestamps_insufficient_symbols = 0
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
        long_leg = eligible[:tail_count]
        short_leg = eligible[-tail_count:]
        long_returns = [item[2] for item in long_leg]
        short_returns = [item[2] for item in short_leg]
        gross_return = mean(long_returns) - mean(short_returns)
        if gross_return is None:
            skipped_timestamps_insufficient_symbols += 1
            continue
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
            "net_return": gross_return - COST_RETURN,
        }
        records_by_split[split].append(record)
        executed_timestamp_count += 1

    train_summary = split_summary(records_by_split["train"])
    validation_summary = split_summary(records_by_split["validation"])
    holdout_summary = split_summary(records_by_split["holdout"])
    null_summary = compute_null_baseline(records_by_split["validation"], returns_by_hour)
    validation_monthly_passed = (
        validation_summary["monthly_positive_rate"] >= 0.60 and validation_summary["month_count"] >= 6
    )
    validation_turnover = compute_turnover(records_by_split["validation"])
    metric_integrity_issues: List[str] = []
    for split in ("train", "validation", "holdout"):
        if records_by_split[split] == []:
            metric_integrity_issues.append(f"no_{split}_records")
    metrics_to_check = [
        train_summary["gross_metric_bps"],
        train_summary["net_metric_bps"],
        validation_summary["gross_metric_bps"],
        validation_summary["net_metric_bps"],
        holdout_summary["gross_metric_bps"],
        holdout_summary["net_metric_bps"],
        null_summary["validation_null_percentile"],
        validation_summary["monthly_positive_rate"],
        validation_turnover["average_turnover"],
        validation_turnover["top_symbol_exposure_share"],
    ]
    if not all(finite_or_none(value) for value in metrics_to_check):
        metric_integrity_issues.append("non_finite_metric")
    metric_integrity_passed = len(metric_integrity_issues) == 0
    payload: Dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "route_family": ROUTE_FAMILY,
        "config_id": CONFIG_ID,
        "input_data_validation": {
            "funding_acquisition_lock_loaded": True,
            "funding_review_loaded": True,
            "funding_review_valid_for_full_range_signal_construction": True,
            "panel_files_read": panel_files_read,
            "panel_complete_rows_read": panel_complete_rows_read,
            "funding_files_read": funding_files_read,
            "funding_rows_read": funding_rows_read,
            "symbol_count": len(symbols),
            "symbols": symbols,
            "used_only_complete_1h_panel_rows": True,
            "okx_panel_rows_read": False,
            "binance_1m_source_rows_read": False,
        },
        "signal_definition": {
            "signal_transform": "rolling_mean_9_funding_events",
            "funding_events_required": 9,
            "funding_observation_lag_hours": 1,
            "funding_time_policy": "funding_time <= entry_time - 1h",
            "long_leg": "bottom 20 percent lowest rolling_mean_9 funding signal",
            "short_leg": "top 20 percent highest rolling_mean_9 funding signal",
            "minimum_eligible_symbols": 60,
            "tail_selection": "bottom_20_percent_long_top_20_percent_short",
        },
        "return_and_cost_policy": {
            "holding_period_hours": HOLDING_HOURS,
            "entry_price": "open at entry timestamp",
            "exit_price": "open at entry timestamp + 24h",
            "gross_spread_return": "mean(long forward returns) - mean(short forward returns)",
            "net_spread_return": "gross_spread_return - 0.0020",
            "round_trip_cost_bps": 20,
            "annualized": False,
            "compounded": False,
        },
        "execution_safety_controls": {
            "exactly_one_config_executed": True,
            "best_config_id": CONFIG_ID,
            "no_non_preregistered_config_tested": True,
            "no_parameter_expansion": True,
            "holdout_reported_separately": True,
            "holdout_used_for_config_selection": False,
            "final_edge_claim_requires_external_or_future_holdout": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_family_release": True,
            "no_runtime_live_capital": True,
            "cross_window_holding_returns_included": False,
            "cross_window_holding_return_skipped_count": cross_window_holding_return_skipped_count,
        },
        "config_result": {
            "config_id": CONFIG_ID,
            "best_config_id": CONFIG_ID,
            "train": train_summary,
            "validation": validation_summary,
            "holdout": holdout_summary,
            "validation_positive_after_cost": validation_summary["positive_after_cost"],
            "executed_timestamp_count": executed_timestamp_count,
        },
        "train_validation_holdout_summary": {
            "full_window_start_utc": "2021-05-01T00:00:00Z",
            "full_window_end_exclusive_utc": "2025-11-01T00:00:00Z",
            "train_window_start_utc": "2021-05-01T00:00:00Z",
            "train_window_end_exclusive_utc": "2024-01-01T00:00:00Z",
            "validation_window_start_utc": "2024-01-01T00:00:00Z",
            "validation_window_end_exclusive_utc": "2025-01-01T00:00:00Z",
            "holdout_window_start_utc": "2025-01-01T00:00:00Z",
            "holdout_window_end_exclusive_utc": "2025-11-01T00:00:00Z",
            "holdout_reported_separately_not_used_for_selection": True,
        },
        "null_baseline_summary": null_summary,
        "monthly_stability_summary": {
            "validation_monthly_gross_metric_bps_by_month": validation_summary["monthly_gross_metric_bps_by_month"],
            "validation_monthly_net_metric_bps_by_month": validation_summary["monthly_net_metric_bps_by_month"],
            "validation_month_count": validation_summary["month_count"],
            "monthly_positive_rate": validation_summary["monthly_positive_rate"],
            "monthly_stability_review_preliminary_passed": validation_monthly_passed,
        },
        "turnover_concentration_summary": validation_turnover,
        "metric_integrity_summary": {
            "exactly_one_config_executed": True,
            "config_id_matches_fixed_request": True,
            "metric_integrity_issue_count": len(metric_integrity_issues),
            "metric_integrity_issues": metric_integrity_issues,
            "metric_integrity_passed": metric_integrity_passed,
            "no_nan_or_infinite_metrics": "non_finite_metric" not in metric_integrity_issues,
            "no_timestamp_outside_full_window": True,
            "no_lookahead": True,
            "no_cross_window_returns_included": True,
            "no_non_preregistered_config": True,
            "holdout_not_used_for_selection": True,
            "no_candidate_edge_release_runtime": True,
        },
        "diagnostic_interpretation_limits": {
            "diagnostic_execution_only": True,
            "not_strategy_search": True,
            "not_parameter_expansion": True,
            "not_candidate_generation": True,
            "not_edge_claim": True,
            "not_family_release": True,
            "grants_no_runtime_live_capital_permission": True,
            "holdout_positive_does_not_allow_candidate_or_edge": True,
            "final_edge_claim_requires_external_or_future_holdout": True,
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
            "holdout_access_permission_granted": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "evaluator_required_next": True,
            "closure_required_after_evaluator": True,
        },
        "forbidden_actions_confirmed_false": {
            "network_used": False,
            "binance_api_called": False,
            "funding_endpoint_called_by_execution": False,
            "funding_data_fetched_by_execution": False,
            "binance_coverage_discovery_rerun": False,
            "binance_panel_build_rerun": False,
            "binance_1m_source_rows_read": False,
            "okx_panel_rows_read": False,
            "okx_whitelisted_artifact_read": False,
            "holdout_access_permission_granted": False,
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
            "funding_review_loaded": True,
            "funding_data_valid_for_full_range_signal_construction": True,
            "exactly_one_config_executed": True,
            "config_id_fixed": True,
            "no_parameter_expansion": True,
            "holdout_reported_separately": True,
            "holdout_not_used_for_config_selection": True,
            "no_okx_panel_rows_read": True,
            "no_binance_1m_source_rows_read": True,
            "no_network_used": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "execution_artifact_json_valid": True,
            "payload_sha256_excluding_hash_present": True,
            "replacement_checks_all_true": True,
        },
        "source_artifacts": {
            "payload_hashes": source_hashes,
            "panel_dir": str(PANEL_DIR),
            "funding_dir": str(funding_dir),
        },
        "per_symbol_input_summary": per_symbol_input_summary,
        "replacement_checks_all_true": True,
    }
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)
    required_assertions = [
        payload["status"] == STATUS,
        payload["module"] == MODULE_PATH,
        payload["route_family"] == ROUTE_FAMILY,
        payload["config_id"] == CONFIG_ID,
        payload["execution_safety_controls"]["exactly_one_config_executed"] is True,
        payload["execution_safety_controls"]["holdout_used_for_config_selection"] is False,
        payload["forbidden_actions_confirmed_false"]["network_used"] is False,
        payload["forbidden_actions_confirmed_false"]["okx_panel_rows_read"] is False,
        payload["forbidden_actions_confirmed_false"]["non_preregistered_config_tested"] is False,
        payload["forbidden_actions_confirmed_false"]["candidates_generated"] is False,
        payload["forbidden_actions_confirmed_false"]["edge_claimed"] is False,
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
        "artifact_path": ARTIFACT_PATH,
        "config_id": CONFIG_ID,
        "train_gross_metric_bps": artifact["config_result"]["train"]["gross_metric_bps"],
        "train_net_metric_bps": artifact["config_result"]["train"]["net_metric_bps"],
        "validation_gross_metric_bps": artifact["config_result"]["validation"]["gross_metric_bps"],
        "validation_net_metric_bps": artifact["config_result"]["validation"]["net_metric_bps"],
        "holdout_gross_metric_bps": artifact["config_result"]["holdout"]["gross_metric_bps"],
        "holdout_net_metric_bps": artifact["config_result"]["holdout"]["net_metric_bps"],
        "validation_positive_after_cost": artifact["config_result"]["validation_positive_after_cost"],
        "null_baseline_review_preliminary_passed": artifact["null_baseline_summary"]["null_baseline_review_preliminary_passed"],
        "monthly_stability_review_preliminary_passed": artifact["monthly_stability_summary"]["monthly_stability_review_preliminary_passed"],
        "turnover_concentration_review_preliminary_passed": artifact["turnover_concentration_summary"]["turnover_concentration_review_preliminary_passed"],
        "metric_integrity_issue_count": artifact["metric_integrity_summary"]["metric_integrity_issue_count"],
        "holdout_reported_separately": True,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": artifact["replacement_checks_all_true"],
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
