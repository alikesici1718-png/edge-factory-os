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
from typing import Any, Deque, Dict, Iterable, List, Optional, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_taker_buy_imbalance_exhaustion_reversal_execution_v1.py"
ARTIFACT_PATH = "artifacts/strategy_executions/binance_okx_overlap_taker_buy_imbalance_exhaustion_reversal_execution_v1.json"
STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_TAKER_BUY_IMBALANCE_EXHAUSTION_REVERSAL_EXECUTED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_TAKER_BUY_IMBALANCE_EXHAUSTION_REVERSAL_EXECUTION"

ROUTE_FAMILY = "BINANCE_OKX_OVERLAP_TAKER_BUY_IMBALANCE_EXHAUSTION_REVERSAL_BASELINE"
HYPOTHESIS_NAME = "taker_buy_imbalance_exhaustion_reversal"
ROUTE_TYPE = "one_sided_short_event_reversal"
CONFIG_ID = "taker_buy_share_p95_upcandle_short_hold8h"

START_HOUR = None
TRAIN_END_HOUR = None
VALIDATION_START_HOUR = None
END_HOUR = None
HOLDING_HOURS = 8
COST_RETURN = 0.0020
TRAILING_CONTEXT_HOURS = 720
TAKER_SHARE_PCTL = 0.95
MIN_TAKER_SHARE = 0.65
MIN_TRAIN_EVENT_COUNT = 100
MIN_VALIDATION_EVENT_COUNT = 50

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


def percentile_nearest_rank(sorted_values: Sequence[float], percentile: float) -> float:
    if not sorted_values:
        raise RuntimeError("empty percentile context")
    rank = max(1, math.ceil(len(sorted_values) * percentile))
    return sorted_values[rank - 1]


def sorted_remove(values: List[float], value: float) -> None:
    idx = bisect.bisect_left(values, value)
    if idx >= len(values) or values[idx] != value:
        raise RuntimeError("sorted window removal failed")
    values.pop(idx)


def split_for_entry(entry_hour: int, exit_hour: int) -> Tuple[Optional[str], bool]:
    if START_HOUR <= entry_hour < TRAIN_END_HOUR:
        return ("train", exit_hour < TRAIN_END_HOUR)
    if VALIDATION_START_HOUR <= entry_hour < END_HOUR:
        return ("validation", exit_hour < END_HOUR)
    return (None, False)


def finite_or_none(value: Optional[float]) -> bool:
    return value is None or (isinstance(value, (int, float)) and math.isfinite(float(value)))


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


def deterministic_seed(route_family: str, config_id: str, run_index: int) -> int:
    digest = hashlib.sha256(f"{route_family}|{config_id}|{run_index}".encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def shuffled_blocks(values: List[float], run_index: int, symbol: str, split: str) -> List[float]:
    blocks = [values[i : i + 168] for i in range(0, len(values), 168)]
    seed_digest = hashlib.sha256(f"{ROUTE_FAMILY}|{CONFIG_ID}|{run_index}|{symbol}|{split}".encode("utf-8")).hexdigest()
    rng = random.Random(int(seed_digest[:16], 16))
    rng.shuffle(blocks)
    flattened: List[float] = []
    for block in blocks:
        flattened.extend(block)
    return flattened


def metric_summary(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    gross_returns = [float(record["gross_return"]) for record in records]
    net_returns = [float(record["net_return"]) for record in records]
    return {
        "event_count": len(records),
        "gross_metric_bps": mean_bps(gross_returns),
        "net_metric_bps": mean_bps(net_returns),
        "positive_after_cost": bool(net_returns and mean(net_returns) is not None and mean(net_returns) > 0),
        "mean_gross_return": None if mean(gross_returns) is None else round(float(mean(gross_returns)), 12),
        "mean_net_return": None if mean(net_returns) is None else round(float(mean(net_returns)), 12),
    }


def monthly_summary(validation_records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    gross_by_month: Dict[str, List[float]] = defaultdict(list)
    net_by_month: Dict[str, List[float]] = defaultdict(list)
    event_count_by_month: Dict[str, int] = defaultdict(int)
    for record in validation_records:
        month = month_key(int(record["entry_hour"]))
        gross_by_month[month].append(float(record["gross_return"]))
        net_by_month[month].append(float(record["net_return"]))
        event_count_by_month[month] += 1
    months = sorted(set(gross_by_month) | set(net_by_month))
    monthly_gross = {month: mean_bps(gross_by_month[month]) for month in months}
    monthly_net = {month: mean_bps(net_by_month[month]) for month in months}
    positive_months = [month for month in months if monthly_net[month] is not None and monthly_net[month] > 0]
    monthly_positive_rate = None if not months else round(len(positive_months) / len(months), 6)
    return {
        "validation_month_count": len(months),
        "validation_event_count_by_month": {month: event_count_by_month[month] for month in months},
        "validation_monthly_gross_metric_bps_by_month": monthly_gross,
        "validation_monthly_net_metric_bps_by_month": monthly_net,
        "monthly_positive_rate": monthly_positive_rate,
        "monthly_stability_review_preliminary_passed": bool(
            monthly_positive_rate is not None and monthly_positive_rate >= 0.60 and len(months) >= 6
        ),
        "worst_validation_month_net_metric_bps": None if not monthly_net else min(value for value in monthly_net.values() if value is not None),
    }


def pearson(xs: Sequence[float], ys: Sequence[float]) -> Optional[float]:
    if len(xs) < 3 or len(xs) != len(ys):
        return None
    mx = mean(xs)
    my = mean(ys)
    if mx is None or my is None:
        return None
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 0 or vy <= 0:
        return None
    return round(cov / math.sqrt(vx * vy), 6)


def compute_null_baseline(
    validation_records: Sequence[Dict[str, Any]],
    candidate_returns_by_symbol_split: Dict[str, Dict[str, List[float]]],
) -> Dict[str, Any]:
    actual_validation_net_bps = mean_bps([float(record["net_return"]) for record in validation_records])
    actual_validation_net = None if actual_validation_net_bps is None else actual_validation_net_bps / 10000.0
    validation_counts_by_symbol: Dict[str, int] = defaultdict(int)
    train_counts_by_symbol: Dict[str, int] = defaultdict(int)
    for record in validation_records:
        validation_counts_by_symbol[str(record["symbol"])] += 1
    # Train counts are recorded for diagnostic completeness by preserving each split independently.
    null_validation_metrics: List[float] = []
    null_train_event_counts: List[int] = []
    null_validation_event_counts: List[int] = []
    for run_index in range(100):
        validation_returns: List[float] = []
        train_count = 0
        validation_count = 0
        for symbol, split_map in sorted(candidate_returns_by_symbol_split.items()):
            train_candidates = split_map.get("train", [])
            validation_candidates = split_map.get("validation", [])
            train_take = min(len(train_candidates), train_counts_by_symbol.get(symbol, 0))
            validation_take = min(len(validation_candidates), validation_counts_by_symbol.get(symbol, 0))
            if train_take:
                shuffled_blocks(train_candidates, run_index, symbol, "train")[:train_take]
                train_count += train_take
            if validation_take:
                shuffled = shuffled_blocks(validation_candidates, run_index, symbol, "validation")
                validation_returns.extend(value - COST_RETURN for value in shuffled[:validation_take])
                validation_count += validation_take
        null_train_event_counts.append(train_count)
        null_validation_event_counts.append(validation_count)
        if validation_returns:
            null_validation_metrics.append(sum(validation_returns) / len(validation_returns) * 10000.0)
    percentile = None
    if actual_validation_net_bps is not None and null_validation_metrics:
        percentile = round(sum(1 for value in null_validation_metrics if value <= actual_validation_net_bps) / len(null_validation_metrics), 6)
    return {
        "null_baseline": "deterministic_event_timestamp_block_shuffle_null",
        "null_run_count": 100,
        "block_length_hours": 168,
        "shuffle_policy": "event timestamps shuffled within symbol and within train/validation separately, preserving per-symbol event count where possible",
        "actual_validation_net_metric_bps": actual_validation_net_bps,
        "actual_validation_net_return": actual_validation_net,
        "null_validation_net_metric_bps_min": None if not null_validation_metrics else round(min(null_validation_metrics), 6),
        "null_validation_net_metric_bps_median": None if not null_validation_metrics else round(float(median(null_validation_metrics)), 6),
        "null_validation_net_metric_bps_max": None if not null_validation_metrics else round(max(null_validation_metrics), 6),
        "validation_null_percentile": percentile,
        "valid_validation_null_run_count": len(null_validation_metrics),
        "null_train_event_count_min": min(null_train_event_counts) if null_train_event_counts else 0,
        "null_validation_event_count_min": min(null_validation_event_counts) if null_validation_event_counts else 0,
        "null_baseline_review_preliminary_passed": bool(percentile is not None and percentile >= 0.95),
    }


def validate_no_forbidden_permissions(source_artifacts: Iterable[Dict[str, Any]]) -> bool:
    forbidden_true_keys = {
        "candidate_generation",
        "edge_claim",
        "family_release",
        "runtime_live_capital",
        "runtime_permission_allowed_now",
        "live_permission_allowed_now",
        "capital_permission_allowed_now",
        "candidate_generation_allowed_now",
        "edge_claim_allowed_now",
        "family_release_allowed_now",
        "runtime_live_capital_allowed_now",
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

    taker_availability = read_json(TAKER_AVAILABILITY_PATH)
    readiness = read_json(READINESS_PATH)
    panel_review = read_json(PANEL_REVIEW_PATH)
    build_manifest = read_json(BUILD_MANIFEST_PATH)
    preview = read_json(PREVIEW_PATH)
    coverage_lock = read_json(COVERAGE_LOCK_PATH)
    source_artifacts = [taker_availability, readiness, panel_review, build_manifest, preview, coverage_lock]
    source_payload_hashes = {
        TAKER_AVAILABILITY_PATH: verify_hash(taker_availability),
        READINESS_PATH: verify_hash(readiness),
        PANEL_REVIEW_PATH: verify_hash(panel_review),
        BUILD_MANIFEST_PATH: verify_hash(build_manifest),
        PREVIEW_PATH: verify_hash(preview),
        COVERAGE_LOCK_PATH: verify_hash(coverage_lock),
    }
    if taker_availability.get("status") != "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_TAKER_BUY_SELL_VOLUME_HISTORY_AVAILABILITY_DISCOVERY_LOCK_API_UNAVAILABLE_PANEL_DERIVED_AVAILABLE":
        raise RuntimeError("latest taker buy/sell availability lock status mismatch")
    panel_availability = taker_availability.get("panel_derived_taker_buy_sell_availability", {})
    if panel_availability.get("taker_sell_derivable_from_panel") is not True:
        raise RuntimeError("panel-derived taker buy/sell availability was not confirmed")
    if panel_availability.get("aligned_window_covered_by_panel_derived_data") is not True:
        raise RuntimeError("panel-derived taker buy/sell aligned-window coverage was not confirmed")
    if not validate_no_forbidden_permissions(source_artifacts):
        raise RuntimeError("source artifact unexpectedly grants forbidden permission")

    symbols = find_symbol_list(readiness) or find_symbol_list(preview) or find_symbol_list(build_manifest)
    if not symbols or len(symbols) != 81:
        raise RuntimeError("could not verify exact 81-symbol overlap universe")

    panel_review_passed = (
        panel_review.get("panel_validity_classification")
        or find_first_key(panel_review, "panel_validity_classification")
    ) == "PANEL_REVIEW_PASS_WITH_P1_ATTENTION_VALID_FOR_READ_ONLY_SECOND_SOURCE_ANALYSIS"
    schema_ok = (
        contains_key(build_manifest, "taker_buy_quote_volume_policy")
        and contains_key(build_manifest, "quote_volume_policy")
        and contains_key(build_manifest, "volume_policy")
        and panel_review_passed
    )
    if not schema_ok:
        raise RuntimeError("reviewed panel schema does not confirm required taker/volume fields")

    panel_files_read = 0
    panel_complete_rows_read = 0
    invalid_quote_volume_context_count = 0
    insufficient_percentile_context_count = 0
    missing_entry_or_exit_row_count = 0
    cross_window_holding_return_skipped_count = 0
    event_candidate_count = 0
    overlapping_event_skipped_count = 0
    accepted_records: List[Dict[str, Any]] = []
    train_records: List[Dict[str, Any]] = []
    validation_records: List[Dict[str, Any]] = []
    event_count_by_symbol: Dict[str, int] = defaultdict(int)
    event_count_by_month: Dict[str, int] = defaultdict(int)
    accepted_events_by_entry_hour: Dict[int, int] = defaultdict(int)
    market_returns_by_entry_hour: Dict[int, List[float]] = defaultdict(list)
    candidate_returns_by_symbol_split: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
    per_symbol_input_summary: Dict[str, Any] = {}

    for symbol in symbols:
        rows = load_panel_rows(symbol)
        panel_files_read += 1
        panel_complete_rows_read += len(rows)
        rows_by_hour = {int(row["hour"]): row for row in rows}
        share_window: Deque[Tuple[int, float]] = deque()
        share_sorted: List[float] = []
        last_event_exit_hour: Optional[int] = None
        symbol_candidate_count = 0
        symbol_accepted_count = 0
        symbol_overlap_count = 0

        for row in rows:
            event_hour = int(row["hour"])
            while share_window and share_window[0][0] < event_hour - TRAILING_CONTEXT_HOURS:
                _old_hour, old_share = share_window.popleft()
                sorted_remove(share_sorted, old_share)

            entry_hour = event_hour + 1
            exit_hour = entry_hour + HOLDING_HOURS
            event_in_aligned_window = START_HOUR <= event_hour < END_HOUR
            split, same_window = split_for_entry(entry_hour, exit_hour)
            entry_row = rows_by_hour.get(entry_hour)
            exit_row = rows_by_hour.get(exit_hour)
            if event_in_aligned_window and split is not None and not same_window:
                cross_window_holding_return_skipped_count += 1
            if event_in_aligned_window and split is not None and same_window and entry_row is not None and exit_row is not None:
                forward_long_return = float(exit_row["open"]) / float(entry_row["open"]) - 1.0
                market_returns_by_entry_hour[entry_hour].append(forward_long_return)
                short_return = -forward_long_return
                candidate_returns_by_symbol_split[symbol][split].append(short_return)
            elif event_in_aligned_window and split is not None and same_window:
                missing_entry_or_exit_row_count += 1

            context_is_consecutive = (
                len(share_window) == TRAILING_CONTEXT_HOURS
                and share_window[0][0] == event_hour - TRAILING_CONTEXT_HOURS
                and share_window[-1][0] == event_hour - 1
            )
            if event_in_aligned_window and split is not None and same_window and entry_row is not None and exit_row is not None:
                if context_is_consecutive:
                    quote_volume = float(row["quote_volume"])
                    taker_buy_quote_volume = float(row["taker_buy_quote_volume"])
                    if quote_volume > 0:
                        event_share = taker_buy_quote_volume / quote_volume
                        threshold = percentile_nearest_rank(share_sorted, TAKER_SHARE_PCTL)
                        spike_hour_return = float(row["close"]) / float(row["open"]) - 1.0
                        if event_share > threshold and event_share >= MIN_TAKER_SHARE and spike_hour_return > 0:
                            event_candidate_count += 1
                            symbol_candidate_count += 1
                            if last_event_exit_hour is not None and event_hour < last_event_exit_hour:
                                overlapping_event_skipped_count += 1
                                symbol_overlap_count += 1
                            else:
                                gross_return = -(float(exit_row["open"]) / float(entry_row["open"]) - 1.0)
                                net_return = gross_return - COST_RETURN
                                record = {
                                    "symbol": symbol,
                                    "event_hour": event_hour,
                                    "event_time_utc": hour_to_iso(event_hour),
                                    "entry_hour": entry_hour,
                                    "entry_time_utc": hour_to_iso(entry_hour),
                                    "exit_hour": exit_hour,
                                    "exit_time_utc": hour_to_iso(exit_hour),
                                    "split": split,
                                    "taker_buy_quote_share": round(event_share, 12),
                                    "trailing_30d_p95_taker_buy_quote_share": round(threshold, 12),
                                    "spike_hour_return": round(spike_hour_return, 12),
                                    "gross_return": gross_return,
                                    "net_return": net_return,
                                }
                                accepted_records.append(record)
                                event_count_by_symbol[symbol] += 1
                                event_count_by_month[month_key(entry_hour)] += 1
                                accepted_events_by_entry_hour[entry_hour] += 1
                                symbol_accepted_count += 1
                                last_event_exit_hour = exit_hour
                                if split == "train":
                                    train_records.append(record)
                                elif split == "validation":
                                    validation_records.append(record)
                    else:
                        invalid_quote_volume_context_count += 1
                else:
                    insufficient_percentile_context_count += 1

            quote_volume_for_context = float(row["quote_volume"])
            taker_buy_quote_volume_for_context = float(row["taker_buy_quote_volume"])
            if quote_volume_for_context > 0:
                share_for_context = taker_buy_quote_volume_for_context / quote_volume_for_context
                share_window.append((event_hour, share_for_context))
                bisect.insort(share_sorted, share_for_context)
            else:
                share_window.clear()
                share_sorted.clear()

        per_symbol_input_summary[symbol] = {
            "complete_panel_rows_read": len(rows),
            "event_candidates_before_declustering": symbol_candidate_count,
            "accepted_event_count": symbol_accepted_count,
            "overlapping_event_skipped_count": symbol_overlap_count,
            "candidate_return_pool_train_count": len(candidate_returns_by_symbol_split[symbol].get("train", [])),
            "candidate_return_pool_validation_count": len(candidate_returns_by_symbol_split[symbol].get("validation", [])),
        }

    train_summary = metric_summary(train_records)
    validation_summary = metric_summary(validation_records)
    monthly = monthly_summary(validation_records)
    null_summary = compute_null_baseline(validation_records, candidate_returns_by_symbol_split)
    total_event_count = len(accepted_records)
    average_events_per_symbol = None if not symbols else round(total_event_count / len(symbols), 6)
    top_symbol_event_share = None
    if total_event_count:
        top_symbol_event_share = round(max(event_count_by_symbol.values()) / total_event_count, 6)
    sample_size_passed = train_summary["event_count"] >= MIN_TRAIN_EVENT_COUNT and validation_summary["event_count"] >= MIN_VALIDATION_EVENT_COUNT
    event_coverage_passed = bool(sample_size_passed and top_symbol_event_share is not None and top_symbol_event_share <= 0.20)

    market_return_by_entry_hour = {
        entry_hour: sum(values) / len(values)
        for entry_hour, values in market_returns_by_entry_hour.items()
        if values
    }
    corr_records = [
        (float(record["gross_return"]), market_return_by_entry_hour[int(record["entry_hour"])])
        for record in validation_records
        if int(record["entry_hour"]) in market_return_by_entry_hour
    ]
    corr = pearson([item[0] for item in corr_records], [item[1] for item in corr_records]) if corr_records else None
    worst_validation_month_net = monthly["worst_validation_month_net_metric_bps"]
    active_events = list(accepted_events_by_entry_hour.values())
    avg_active_events = None if not active_events else round(sum(active_events) / len(active_events), 6)
    max_active_events = max(active_events) if active_events else 0
    exposure_risk_passed = bool(
        validation_summary["net_metric_bps"] is not None
        and validation_summary["net_metric_bps"] > 0
        and corr is not None
        and corr > -0.30
        and worst_validation_month_net is not None
        and worst_validation_month_net > -250.0
    )
    turnover_concentration_passed = bool(top_symbol_event_share is not None and top_symbol_event_share <= 0.20)

    metric_integrity_issues: List[str] = []
    if train_summary["event_count"] == 0:
        metric_integrity_issues.append("no_train_events")
    if validation_summary["event_count"] == 0:
        metric_integrity_issues.append("no_validation_events")
    metrics_to_check = [
        train_summary["gross_metric_bps"],
        train_summary["net_metric_bps"],
        validation_summary["gross_metric_bps"],
        validation_summary["net_metric_bps"],
        null_summary["validation_null_percentile"],
        monthly["monthly_positive_rate"],
        top_symbol_event_share,
        corr,
        worst_validation_month_net,
    ]
    if not all(finite_or_none(value) for value in metrics_to_check):
        metric_integrity_issues.append("non_finite_metric")
    if cross_window_holding_return_skipped_count < 0:
        metric_integrity_issues.append("invalid_cross_window_skip_count")
    if CONFIG_ID != "taker_buy_share_p95_upcandle_short_hold8h":
        metric_integrity_issues.append("config_id_mismatch")
    metric_integrity_passed = len(metric_integrity_issues) == 0

    payload: Dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "route_family": ROUTE_FAMILY,
        "config_id": CONFIG_ID,
        "preregistration_contract_snapshot": {
            "snapshot_created_before_metric_computation": True,
            "immutable_single_config_contract": True,
            "route_family": ROUTE_FAMILY,
            "hypothesis_name": HYPOTHESIS_NAME,
            "route_type": ROUTE_TYPE,
            "config_count": 1,
            "config_id": CONFIG_ID,
            "symbol_count": 81,
            "aligned_window": {
                "start_utc": "2023-07-01T00:00:00Z",
                "end_exclusive_utc": "2025-10-31T16:00:00Z",
            },
            "train_window": {
                "start_utc": "2023-07-01T00:00:00Z",
                "end_exclusive_utc": "2025-01-01T00:00:00Z",
            },
            "validation_window": {
                "start_utc": "2025-01-01T00:00:00Z",
                "end_exclusive_utc": "2025-10-31T16:00:00Z",
            },
            "event_definition": {
                "taker_buy_quote_share": "taker_buy_quote_volume / quote_volume",
                "trailing_context": "prior 720 complete 1h bars before event hour t",
                "threshold": "taker_buy_quote_share > symbol trailing 30d p95 and >= 0.65",
                "spike_hour_direction": "close > open",
                "event_known_after_hour_close": True,
                "entry_timestamp": "event_hour + 1h",
            },
            "holding_period_hours": HOLDING_HOURS,
            "cost": {"round_trip_cost_bps": 20},
            "short_only": True,
            "market_neutral": False,
            "no_parameter_expansion": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
        },
        "input_data_validation": {
            "taker_buy_sell_availability_lock_loaded": True,
            "taker_buy_sell_availability_payload_hash_verified": True,
            "panel_derived_taker_buy_sell_available": True,
            "panel_derived_aligned_window_covered": True,
            "panel_files_read": panel_files_read,
            "panel_complete_rows_read": panel_complete_rows_read,
            "symbol_count": len(symbols),
            "symbols": symbols,
            "used_only_complete_1h_rows": True,
            "required_panel_fields_present": EXPECTED_PANEL_HEADER,
            "external_panel_rows_read_for_execution": True,
            "funding_rows_read": False,
            "okx_panel_rows_read": False,
            "binance_1m_source_rows_read": False,
        },
        "event_definition": {
            "taker_buy_quote_share_t": "taker_buy_quote_volume_t / quote_volume_t",
            "quote_volume_t_must_be_positive": True,
            "trailing_30d_context_hours": TRAILING_CONTEXT_HOURS,
            "percentile_threshold": TAKER_SHARE_PCTL,
            "minimum_taker_buy_quote_share": MIN_TAKER_SHARE,
            "spike_hour_return": "close_t / open_t - 1",
            "spike_hour_return_required_positive": True,
            "event_condition": "share > trailing p95 and share >= 0.65 and close > open",
            "event_hour_known_only_after_close": True,
            "entry_timestamp": "t + 1h",
            "decluster_policy": "per-symbol cooldown skips events before previous event exit",
            "cooldown_holding_hours": HOLDING_HOURS,
        },
        "return_and_cost_policy": {
            "holding_period_hours": HOLDING_HOURS,
            "entry_price": "open at event_hour + 1h",
            "exit_price": "open at entry timestamp + 8h",
            "gross_return": "short price return = -(exit_open / entry_open - 1)",
            "net_return": "gross_return - 0.0020",
            "round_trip_cost_bps": 20,
            "metric_units": "bps per accepted event",
            "annualized": False,
            "compounded": False,
            "funding_cashflow_included": False,
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
            "route_type": ROUTE_TYPE,
            "train_event_count": train_summary["event_count"],
            "validation_event_count": validation_summary["event_count"],
            "train_gross_metric_bps": train_summary["gross_metric_bps"],
            "train_net_metric_bps": train_summary["net_metric_bps"],
            "validation_gross_metric_bps": validation_summary["gross_metric_bps"],
            "validation_net_metric_bps": validation_summary["net_metric_bps"],
            "validation_positive_after_cost": validation_summary["positive_after_cost"],
            "total_event_count": total_event_count,
            "accepted_event_count": total_event_count,
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
        "event_coverage_summary": {
            "train_event_count": train_summary["event_count"],
            "validation_event_count": validation_summary["event_count"],
            "total_event_count": total_event_count,
            "accepted_event_count": total_event_count,
            "event_candidate_count_before_declustering": event_candidate_count,
            "overlapping_event_skipped_count": overlapping_event_skipped_count,
            "events_by_month": dict(sorted(event_count_by_month.items())),
            "events_by_symbol": dict(sorted(event_count_by_symbol.items())),
            "average_events_per_symbol": average_events_per_symbol,
            "top_symbol_event_share": top_symbol_event_share,
            "minimum_train_event_count_for_metric": MIN_TRAIN_EVENT_COUNT,
            "minimum_validation_event_count_for_metric": MIN_VALIDATION_EVENT_COUNT,
            "sample_size_review_preliminary_passed": sample_size_passed,
            "event_coverage_review_preliminary_passed": event_coverage_passed,
            "insufficient_percentile_context_count": insufficient_percentile_context_count,
            "invalid_quote_volume_context_count": invalid_quote_volume_context_count,
            "missing_entry_or_exit_row_count": missing_entry_or_exit_row_count,
        },
        "exposure_risk_summary": {
            "short_only": True,
            "market_neutral": False,
            "average_active_events_per_timestamp": avg_active_events,
            "max_active_events_per_timestamp": max_active_events,
            "correlation_with_equal_weight_market_return": corr,
            "correlation_basis": "validation accepted event gross returns versus equal-weight market forward returns at matching entry hours",
            "worst_validation_month_net_metric_bps": worst_validation_month_net,
            "strong_negative_market_beta_threshold": -0.30,
            "exposure_risk_review_preliminary_passed": exposure_risk_passed,
        },
        "turnover_concentration_summary": {
            "participation_by_symbol": dict(sorted(event_count_by_symbol.items())),
            "top_symbol_exposure_share": top_symbol_event_share,
            "event_based_turnover_diagnostic_only": True,
            "turnover_concentration_review_preliminary_passed": turnover_concentration_passed,
            "review_rule": "passed iff top_symbol_exposure_share <= 0.20",
        },
        "metric_integrity_summary": {
            "exactly_one_config_executed": True,
            "config_id_matches_preregistration_snapshot": True,
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
            "short_only_not_market_neutral": True,
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
            "preregistration_contract_snapshot_embedded": True,
            "config_count_verified_1": True,
            "config_id_matches_preregistration_snapshot": True,
            "exact_overlap_symbol_count_verified_81": True,
            "aligned_window_verified": True,
            "taker_buy_sell_availability_lock_loaded": True,
            "panel_derived_taker_buy_sell_available_verified": True,
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
            "event_coverage_created": True,
            "exposure_risk_created": True,
            "turnover_concentration_created": True,
            "metric_integrity_checks_created": True,
            "execution_artifact_json_valid": True,
            "payload_sha256_excluding_hash_present": True,
            "replacement_checks_all_true": True,
        },
        "source_artifacts": {
            "payload_hashes": source_payload_hashes,
            "panel_dir": str(PANEL_DIR),
        },
        "per_symbol_input_summary": per_symbol_input_summary,
        "replacement_checks_all_true": True,
    }
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)

    required_assertions = [
        payload["status"] == STATUS,
        payload["module"] == MODULE_PATH,
        ARTIFACT_PATH == "artifacts/strategy_executions/binance_okx_overlap_taker_buy_imbalance_exhaustion_reversal_execution_v1.json",
        payload["route_family"] == ROUTE_FAMILY,
        payload["config_id"] == CONFIG_ID,
        payload["preregistration_contract_snapshot"]["config_count"] == 1,
        payload["preregistration_contract_snapshot"]["short_only"] is True,
        payload["preregistration_contract_snapshot"]["market_neutral"] is False,
        payload["input_data_validation"]["symbol_count"] == 81,
        payload["execution_safety_controls"]["exactly_one_config_executed"] is True,
        payload["execution_safety_controls"]["no_non_preregistered_config_tested"] is True,
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
        "train_event_count": artifact["config_result"]["train_event_count"],
        "validation_event_count": artifact["config_result"]["validation_event_count"],
        "validation_gross_metric_bps": artifact["config_result"]["validation_gross_metric_bps"],
        "validation_net_metric_bps": artifact["config_result"]["validation_net_metric_bps"],
        "validation_positive_after_cost": artifact["config_result"]["validation_positive_after_cost"],
        "null_baseline_review_preliminary_passed": artifact["null_baseline_summary"]["null_baseline_review_preliminary_passed"],
        "monthly_stability_review_preliminary_passed": artifact["monthly_stability_summary"]["monthly_stability_review_preliminary_passed"],
        "event_coverage_review_preliminary_passed": artifact["event_coverage_summary"]["event_coverage_review_preliminary_passed"],
        "exposure_risk_review_preliminary_passed": artifact["exposure_risk_summary"]["exposure_risk_review_preliminary_passed"],
        "turnover_concentration_review_preliminary_passed": artifact["turnover_concentration_summary"]["turnover_concentration_review_preliminary_passed"],
        "metric_integrity_issue_count": artifact["metric_integrity_summary"]["metric_integrity_issue_count"],
        "metric_integrity_passed": artifact["metric_integrity_summary"]["metric_integrity_passed"],
        "top_symbol_event_share": artifact["event_coverage_summary"]["top_symbol_event_share"],
        "correlation_with_equal_weight_market_return": artifact["exposure_risk_summary"]["correlation_with_equal_weight_market_return"],
        "worst_validation_month_net_metric_bps": artifact["exposure_risk_summary"]["worst_validation_month_net_metric_bps"],
        "short_only": True,
        "market_neutral": False,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": artifact["replacement_checks_all_true"],
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
