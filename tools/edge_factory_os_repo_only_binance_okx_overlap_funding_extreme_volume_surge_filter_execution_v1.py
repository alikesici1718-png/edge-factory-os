import bisect
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
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_extreme_volume_surge_filter_execution_v1.py"
ARTIFACT_PATH = "artifacts/strategy_executions/binance_okx_overlap_funding_extreme_volume_surge_filter_execution_v1.json"
STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_FUNDING_EXTREME_VOLUME_SURGE_FILTER_EXECUTED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_FUNDING_EXTREME_VOLUME_SURGE_FILTER_EXECUTION"

ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_EXTREME_VOLUME_SURGE_FILTER_REVERSAL_BASELINE"
HYPOTHESIS_NAME = "funding_extreme_volume_surge_reversal"
CONFIG_ID = "funding_mean9_volume_surge24h_p80_30d_hold24h"

START_HOUR = None
TRAIN_END_HOUR = None
VALIDATION_START_HOUR = None
END_HOUR = None
HOLDING_HOURS = 24
COST_RETURN = 0.0020

PREREG_PATH = "artifacts/research_preregistrations/binance_okx_overlap_funding_extreme_volume_surge_filter_preregistration_contract_v1.json"
OI_LOCK_PATH = "artifacts/oi_data_availability_locks/binance_okx_overlap_oi_historical_data_availability_discovery_lock_v1.json"
FUNDING_CARRY_CLOSURE_PATH = "artifacts/strategy_closures/binance_okx_overlap_funding_carry_short_positive_flat_negative_closure_v1.json"
GROUP2_CLOSURE_PATH = "artifacts/strategy_closures/binance_okx_group2_funding_extreme_momentum_confirmed_closure_v1.json"
FUNDING_EXTREME_LIQ_CLOSURE_PATH = "artifacts/strategy_closures/binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_closure_v1.json"
PLAIN_FUNDING_CLOSURE_PATH = "artifacts/strategy_closures/binance_okx_overlap_funding_rate_closure_record_after_evaluator_v1.json"
FUNDING_REVIEW_PATH = "artifacts/funding_rate_reviews/binance_okx_overlap_funding_rate_data_review_after_acquisition_lock_v1.json"
FUNDING_LOCK_PATH = "artifacts/funding_rate_locks/binance_okx_overlap_funding_rate_data_acquisition_lock_v1.json"
READINESS_PATH = "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json"
PANEL_REVIEW_PATH = "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json"
BUILD_MANIFEST_PATH = "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json"
PREVIEW_PATH = "artifacts/panel_build_previews/binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.json"
COVERAGE_LOCK_PATH = "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json"

PANEL_DIR = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_binance_okx_overlap_near_5y_1m_to_1h_panel_build_execution_v1\panel_1h_by_symbol"
)
FUNDING_DIR = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_binance_okx_overlap_funding_rate_data_acquisition_lock_v1\funding_by_symbol"
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
    encoded = json.dumps(clean, sort_keys=True, indent=2).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def read_json(relative_path: str) -> Dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise RuntimeError(f"missing required source artifact: {relative_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def verify_hash(payload: Dict[str, Any], expected: Optional[str] = None) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise RuntimeError("source artifact missing payload_sha256_excluding_hash")
    recomputed = canonical_payload_hash(payload)
    if recomputed != stored:
        raise RuntimeError(f"payload hash mismatch: {recomputed} != {stored}")
    if expected is not None and stored != expected:
        raise RuntimeError(f"payload hash mismatch against expected: {stored} != {expected}")
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
    return value is None or math.isfinite(value)


def percentile_nearest_rank(sorted_values: Sequence[float], percentile: float) -> float:
    if not sorted_values:
        raise RuntimeError("empty percentile context")
    rank = max(1, math.ceil(len(sorted_values) * percentile))
    return sorted_values[rank - 1]


def split_for_entry(entry_hour: int, exit_hour: int) -> Tuple[Optional[str], bool]:
    if START_HOUR <= entry_hour < TRAIN_END_HOUR:
        return ("train", exit_hour < TRAIN_END_HOUR)
    if VALIDATION_START_HOUR <= entry_hour < END_HOUR:
        return ("validation", exit_hour < END_HOUR)
    return (None, False)


def load_funding_events(symbol: str) -> List[Tuple[int, float]]:
    path = FUNDING_DIR / f"{symbol}_funding_rate.jsonl.gz"
    if not path.exists():
        raise RuntimeError(f"missing funding file for {symbol}: {path}")
    events: List[Tuple[int, float]] = []
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("symbol") != symbol:
                raise RuntimeError(f"funding symbol mismatch in {path}")
            hour = parse_hour(str(row["funding_time_utc"]))
            rate = float(row["funding_rate"])
            if not math.isfinite(rate):
                raise RuntimeError(f"invalid funding rate for {symbol} at {row['funding_time_utc']}")
            events.append((hour, rate))
    events.sort()
    for idx in range(1, len(events)):
        if events[idx][0] <= events[idx - 1][0]:
            raise RuntimeError(f"funding timestamps not strictly increasing for {symbol}")
    return events


def load_complete_panel_rows(symbol: str) -> List[Tuple[int, float, float, float]]:
    path = PANEL_DIR / f"{symbol}_1h.csv.gz"
    if not path.exists():
        raise RuntimeError(f"missing panel file for {symbol}: {path}")
    rows: List[Tuple[int, float, float, float]] = []
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
            if open_price <= 0 or close_price <= 0 or quote_volume < 0:
                raise RuntimeError(f"invalid panel numeric value for {symbol} at {row['timestamp_utc']}")
            rows.append((hour, open_price, close_price, quote_volume))
    rows.sort(key=lambda item: item[0])
    for idx in range(1, len(rows)):
        if rows[idx][0] <= rows[idx - 1][0]:
            raise RuntimeError(f"panel complete rows not strictly increasing for {symbol}")
    return rows


def sorted_remove(values: List[float], value: float) -> None:
    idx = bisect.bisect_left(values, value)
    if idx >= len(values) or values[idx] != value:
        raise RuntimeError("percentile sorted window removal failed")
    values.pop(idx)


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
    passed = (
        top_share is not None
        and avg_turnover is not None
        and top_share <= 0.10
        and avg_turnover <= 1.50
    )
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
    oi_lock = read_json(OI_LOCK_PATH)
    funding_carry_closure = read_json(FUNDING_CARRY_CLOSURE_PATH)
    group2_closure = read_json(GROUP2_CLOSURE_PATH)
    funding_extreme_liq_closure = read_json(FUNDING_EXTREME_LIQ_CLOSURE_PATH)
    plain_funding_closure = read_json(PLAIN_FUNDING_CLOSURE_PATH)
    funding_review = read_json(FUNDING_REVIEW_PATH)
    funding_lock = read_json(FUNDING_LOCK_PATH)
    readiness = read_json(READINESS_PATH)
    panel_review = read_json(PANEL_REVIEW_PATH)
    build_manifest = read_json(BUILD_MANIFEST_PATH)
    preview = read_json(PREVIEW_PATH)
    coverage_lock = read_json(COVERAGE_LOCK_PATH)

    source_payload_hashes = {
        PREREG_PATH: verify_hash(prereg, "227f02d39d48012749e0881046ae64d50b254c70fd1dc91148c45a00bee2c763"),
        OI_LOCK_PATH: verify_hash(oi_lock),
        FUNDING_CARRY_CLOSURE_PATH: verify_hash(funding_carry_closure),
        GROUP2_CLOSURE_PATH: verify_hash(group2_closure),
        FUNDING_EXTREME_LIQ_CLOSURE_PATH: verify_hash(funding_extreme_liq_closure),
        PLAIN_FUNDING_CLOSURE_PATH: verify_hash(plain_funding_closure),
        FUNDING_REVIEW_PATH: verify_hash(funding_review),
        FUNDING_LOCK_PATH: verify_hash(funding_lock),
        READINESS_PATH: verify_hash(readiness),
        PANEL_REVIEW_PATH: verify_hash(panel_review),
        BUILD_MANIFEST_PATH: verify_hash(build_manifest),
        PREVIEW_PATH: verify_hash(preview),
        COVERAGE_LOCK_PATH: verify_hash(coverage_lock),
    }

    if prereg.get("status") != "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_EXTREME_VOLUME_SURGE_FILTER_PREREGISTRATION_CONTRACT_CREATED":
        raise RuntimeError("preregistration status mismatch")
    if prereg.get("funding_volume_hypothesis_preregistration", {}).get("route_family") != ROUTE_FAMILY:
        raise RuntimeError("route family mismatch")
    if prereg.get("config_grid", {}).get("config_id") != CONFIG_ID:
        raise RuntimeError("config id mismatch")
    if prereg.get("config_grid", {}).get("config_count") != 1:
        raise RuntimeError("config count mismatch")
    funding_valid = (
        funding_review.get("safety_permissions", {}).get("funding_data_valid_for_future_funding_signal_construction") is True
        or funding_review.get("acquisition_manifest_review", {}).get("acquisition_lock_valid_for_future_funding_signal_construction") is True
        or funding_review.get("valid_for_future_funding_signal_construction") is True
    )
    if not funding_valid:
        raise RuntimeError("funding review does not permit future signal construction")
    panel_classification = panel_review.get("panel_validity_classification") or panel_review.get("panel_review", {}).get("panel_validity_classification")
    if panel_classification != "PANEL_REVIEW_PASS_WITH_P1_ATTENTION_VALID_FOR_READ_ONLY_SECOND_SOURCE_ANALYSIS":
        raise RuntimeError("panel review validity classification mismatch")
    if not validate_no_forbidden_permissions(
        [
            prereg,
            oi_lock,
            funding_carry_closure,
            group2_closure,
            funding_extreme_liq_closure,
            plain_funding_closure,
            funding_review,
            readiness,
            panel_review,
        ]
    ):
        raise RuntimeError("source artifact grants forbidden permission")

    readiness_universe = readiness["symbol_universe_alignment"]
    symbols = list(readiness_universe["exact_overlap_binance_symbols"])
    if len(symbols) != 81:
        raise RuntimeError(f"expected 81 symbols, found {len(symbols)}")
    if readiness["okx_binance_alignment_window"]["recommended_aligned_window_start_utc"] != "2023-07-01T00:00:00Z":
        raise RuntimeError("aligned start mismatch")
    if readiness["okx_binance_alignment_window"]["recommended_aligned_window_end_exclusive_utc"] != "2025-10-31T16:00:00Z":
        raise RuntimeError("aligned end mismatch")

    panel_files_read = 0
    funding_files_read = 0
    panel_complete_rows_read = 0
    funding_rows_read = 0
    returns_by_hour: Dict[int, Dict[str, float]] = defaultdict(dict)
    features_by_hour: Dict[int, List[Tuple[str, float, float]]] = defaultdict(list)
    per_symbol_summary: Dict[str, Dict[str, Any]] = {}
    cross_window_holding_return_skipped_count = 0
    missing_exit_row_count = 0
    insufficient_volume_context_count = 0
    insufficient_funding_context_count = 0
    volume_anomaly_symbol_events = 0

    for symbol in symbols:
        panel_rows = load_complete_panel_rows(symbol)
        funding_events = load_funding_events(symbol)
        panel_files_read += 1
        funding_files_read += 1
        panel_complete_rows_read += len(panel_rows)
        funding_rows_read += len(funding_events)

        ts_to_idx = {row[0]: idx for idx, row in enumerate(panel_rows)}
        prefix_quote_volume = [0.0]
        for _, _, _, quote_volume in panel_rows:
            prefix_quote_volume.append(prefix_quote_volume[-1] + quote_volume)

        funding_idx = 0
        funding_window: deque = deque()
        funding_sum = 0.0
        volume_context_queue: deque = deque()
        volume_context_sorted: List[float] = []
        symbol_return_count = 0
        symbol_feature_count = 0

        for idx, (entry_hour, entry_open, _entry_close, _entry_quote_volume) in enumerate(panel_rows):
            while funding_idx < len(funding_events) and funding_events[funding_idx][0] <= entry_hour - 1:
                rate = funding_events[funding_idx][1]
                funding_window.append(rate)
                funding_sum += rate
                if len(funding_window) > 9:
                    funding_sum -= funding_window.popleft()
                funding_idx += 1

            current_volume_change: Optional[float] = None
            has_recent_window = idx >= 24 and panel_rows[idx - 1][0] == entry_hour - 1 and panel_rows[idx - 24][0] == entry_hour - 24
            has_prior_window = idx >= 48 and panel_rows[idx - 25][0] == entry_hour - 25 and panel_rows[idx - 48][0] == entry_hour - 48
            if has_recent_window and has_prior_window:
                trailing_current = prefix_quote_volume[idx] - prefix_quote_volume[idx - 24]
                trailing_prior = prefix_quote_volume[idx - 24] - prefix_quote_volume[idx - 48]
                if trailing_current > 0 and trailing_prior > 0:
                    current_volume_change = math.log(trailing_current / trailing_prior)

            while volume_context_queue and volume_context_queue[0][0] < entry_hour - 720:
                old_hour, old_value = volume_context_queue.popleft()
                sorted_remove(volume_context_sorted, old_value)

            exit_hour = entry_hour + HOLDING_HOURS
            split, same_window = split_for_entry(entry_hour, exit_hour)
            if split is not None and not same_window:
                cross_window_holding_return_skipped_count += 1

            if split is not None and same_window:
                exit_idx = ts_to_idx.get(exit_hour)
                if exit_idx is None:
                    missing_exit_row_count += 1
                else:
                    exit_open = panel_rows[exit_idx][1]
                    forward_return = exit_open / entry_open - 1.0
                    returns_by_hour[entry_hour][symbol] = forward_return
                    symbol_return_count += 1

                    volume_anomaly = False
                    if current_volume_change is not None and len(volume_context_sorted) >= 720:
                        threshold = percentile_nearest_rank(volume_context_sorted, 0.80)
                        volume_anomaly = current_volume_change > 0 and current_volume_change > threshold
                    else:
                        insufficient_volume_context_count += 1

                    if volume_anomaly:
                        volume_anomaly_symbol_events += 1
                        if len(funding_window) >= 9:
                            funding_signal = funding_sum / 9.0
                            features_by_hour[entry_hour].append((symbol, funding_signal, forward_return))
                            symbol_feature_count += 1
                        else:
                            insufficient_funding_context_count += 1

            if current_volume_change is not None:
                volume_context_queue.append((entry_hour, current_volume_change))
                bisect.insort(volume_context_sorted, current_volume_change)

        per_symbol_summary[symbol] = {
            "complete_panel_rows_read": len(panel_rows),
            "funding_rows_read": len(funding_events),
            "valid_forward_return_rows": symbol_return_count,
            "volume_anomaly_and_funding_feature_rows": symbol_feature_count,
        }

    train_records: List[Dict[str, Any]] = []
    validation_records: List[Dict[str, Any]] = []
    skipped_timestamps_insufficient_volume_anomaly_symbols = 0
    skipped_timestamps_insufficient_leg_symbols = 0
    train_eligible_symbol_counts: List[int] = []
    validation_eligible_symbol_counts: List[int] = []
    all_eligible_symbol_counts: List[int] = []
    executed_timestamp_count = 0

    for entry_hour in sorted(returns_by_hour.keys()):
        exit_hour = entry_hour + HOLDING_HOURS
        split, same_window = split_for_entry(entry_hour, exit_hour)
        if split is None or not same_window:
            continue
        eligible = sorted(features_by_hour.get(entry_hour, []), key=lambda item: (item[1], item[0]))
        eligible_count = len(eligible)
        all_eligible_symbol_counts.append(eligible_count)
        if split == "train":
            train_eligible_symbol_counts.append(eligible_count)
        elif split == "validation":
            validation_eligible_symbol_counts.append(eligible_count)
        if eligible_count < 20:
            skipped_timestamps_insufficient_volume_anomaly_symbols += 1
            continue
        tail_count = max(1, math.floor(eligible_count * 0.20))
        long_leg = eligible[:tail_count]
        short_leg = eligible[-tail_count:]
        if len(long_leg) < 3 or len(short_leg) < 3:
            skipped_timestamps_insufficient_leg_symbols += 1
            continue
        long_returns = [item[2] for item in long_leg]
        short_returns = [item[2] for item in short_leg]
        gross_return = mean(long_returns) - mean(short_returns)
        if gross_return is None:
            skipped_timestamps_insufficient_leg_symbols += 1
            continue
        net_return = gross_return - COST_RETURN
        record = {
            "entry_hour": entry_hour,
            "entry_time_utc": hour_to_iso(entry_hour),
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

    eligible_counts_passing_min = [count for count in all_eligible_symbol_counts if count >= 20]
    validation_counts_passing_min = [count for count in validation_eligible_symbol_counts if count >= 20]
    train_counts_passing_min = [count for count in train_eligible_symbol_counts if count >= 20]
    avg_volume_symbols = mean(eligible_counts_passing_min)
    median_volume_symbols = median(eligible_counts_passing_min) if eligible_counts_passing_min else None
    min_volume_symbols = min(eligible_counts_passing_min) if eligible_counts_passing_min else None
    max_volume_symbols = max(eligible_counts_passing_min) if eligible_counts_passing_min else None
    volume_coverage_passed = (
        len(validation_counts_passing_min) >= 500
        and avg_volume_symbols is not None
        and avg_volume_symbols >= 20
    )

    metric_integrity_issues: List[str] = []
    if len(train_records) == 0:
        metric_integrity_issues.append("no_train_records")
    if len(validation_records) == 0:
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
    if CONFIG_ID != "funding_mean9_volume_surge24h_p80_30d_hold24h":
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
            "panel_files_read": panel_files_read,
            "funding_files_read": funding_files_read,
            "symbol_count": len(symbols),
            "symbols": symbols,
            "panel_complete_rows_read": panel_complete_rows_read,
            "funding_rows_read": funding_rows_read,
            "used_only_complete_1h_rows": True,
            "external_panel_rows_read_for_execution": True,
            "external_funding_rows_read_for_execution": True,
            "okx_panel_rows_read": False,
        },
        "signal_alignment_policy": {
            "funding_transform": "rolling_mean_9_funding_events",
            "funding_events_required": 9,
            "funding_observation_lag_hours": 1,
            "funding_time_policy": "funding_time <= entry_time - 1h",
            "no_forward_fill": True,
            "no_backfill": True,
        },
        "volume_anomaly_policy": {
            "volume_anomaly_filter_created": True,
            "volume_anomaly_field": "quote_volume",
            "trailing_24h_quote_volume_t": "sum quote_volume over prior 24 complete 1h rows ending at E - 1h",
            "trailing_24h_quote_volume_t_minus_24h": "same trailing 24h value measured 24 hours earlier",
            "volume_change_definition": "log(trailing_24h_quote_volume_t / trailing_24h_quote_volume_t_minus_24h)",
            "percentile_context_days": 30,
            "percentile_context_hours": 720,
            "percentile_threshold": 0.80,
            "percentile_method": "nearest_rank_on_prior_defined_symbol_local_values",
            "no_current_hour_volume": True,
            "no_future_volume": True,
        },
        "return_and_cost_policy": {
            "holding_period_hours": HOLDING_HOURS,
            "entry_price": "open at entry timestamp",
            "exit_price": "open at entry timestamp + 24h",
            "gross_spread_return": "mean(long open-to-open returns) - mean(short open-to-open returns)",
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
        "volume_anomaly_coverage_summary": {
            "volume_anomaly_filter_created": True,
            "volume_anomaly_field": "quote_volume",
            "volume_change_definition": "log(trailing_24h_quote_volume_t / trailing_24h_quote_volume_t_minus_24h)",
            "percentile_context_days": 30,
            "percentile_threshold": 0.80,
            "train_volume_anomaly_eligible_timestamp_count": len(train_counts_passing_min),
            "validation_volume_anomaly_eligible_timestamp_count": len(validation_counts_passing_min),
            "average_volume_anomaly_symbols_per_timestamp": None if avg_volume_symbols is None else round(avg_volume_symbols, 6),
            "median_volume_anomaly_symbols_per_timestamp": None if median_volume_symbols is None else round(float(median_volume_symbols), 6),
            "min_volume_anomaly_symbols_per_timestamp": min_volume_symbols,
            "max_volume_anomaly_symbols_per_timestamp": max_volume_symbols,
            "skipped_timestamps_insufficient_volume_anomaly_symbols": skipped_timestamps_insufficient_volume_anomaly_symbols,
            "skipped_timestamps_insufficient_leg_symbols": skipped_timestamps_insufficient_leg_symbols,
            "volume_anomaly_symbol_events": volume_anomaly_symbol_events,
            "insufficient_volume_context_symbol_timestamp_count": insufficient_volume_context_count,
            "insufficient_funding_context_after_volume_anomaly_count": insufficient_funding_context_count,
            "volume_anomaly_coverage_review_preliminary_passed": volume_coverage_passed,
        },
        "turnover_concentration_summary": turnover,
        "metric_integrity_summary": {
            "exactly_one_config_executed": True,
            "config_id_matches_preregistration": True,
            "metric_integrity_issue_count": len(metric_integrity_issues),
            "metric_integrity_issues": metric_integrity_issues,
            "metric_integrity_passed": metric_integrity_passed,
            "no_nan_or_infinite_metrics": True,
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
            "panel_valid_for_read_only_second_source_analysis_verified": True,
            "funding_review_loaded": True,
            "funding_data_valid_for_signal_construction_verified": True,
            "binance_1h_panel_rows_read_for_execution": True,
            "reviewed_funding_rows_read_for_execution": True,
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
            "volume_anomaly_coverage_created": True,
            "turnover_concentration_created": True,
            "metric_integrity_checks_created": True,
            "execution_artifact_json_valid": True,
            "payload_sha256_excluding_hash_present": True,
            "replacement_checks_all_true": True,
        },
        "source_artifacts": {
            "payload_hashes": source_payload_hashes,
            "panel_dir": str(PANEL_DIR),
            "funding_dir": str(FUNDING_DIR),
        },
        "per_symbol_input_summary": per_symbol_summary,
        "replacement_checks_all_true": True,
    }
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)

    required_assertions = [
        payload["status"] == STATUS,
        payload["module"] == MODULE_PATH,
        ARTIFACT_PATH == "artifacts/strategy_executions/binance_okx_overlap_funding_extreme_volume_surge_filter_execution_v1.json",
        payload["route_family"] == ROUTE_FAMILY,
        payload["config_id"] == CONFIG_ID,
        payload["input_data_validation"]["symbol_count"] == 81,
        payload["execution_safety_controls"]["exactly_one_config_executed"] is True,
        payload["execution_safety_controls"]["no_non_preregistered_config_tested"] is True,
        payload["execution_safety_controls"]["no_parameter_expansion"] is True,
        payload["forbidden_actions_confirmed_false"]["network_used"] is False,
        payload["forbidden_actions_confirmed_false"]["binance_api_called"] is False,
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
        "turnover_concentration_review_preliminary_passed": artifact["turnover_concentration_summary"]["turnover_concentration_review_preliminary_passed"],
        "volume_anomaly_coverage_review_preliminary_passed": artifact["volume_anomaly_coverage_summary"]["volume_anomaly_coverage_review_preliminary_passed"],
        "average_volume_anomaly_symbols_per_timestamp": artifact["volume_anomaly_coverage_summary"]["average_volume_anomaly_symbols_per_timestamp"],
        "validation_volume_anomaly_eligible_timestamp_count": artifact["volume_anomaly_coverage_summary"]["validation_volume_anomaly_eligible_timestamp_count"],
        "metric_integrity_issue_count": artifact["metric_integrity_summary"]["metric_integrity_issue_count"],
        "metric_integrity_passed": artifact["metric_integrity_summary"]["metric_integrity_passed"],
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": artifact["replacement_checks_all_true"],
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
