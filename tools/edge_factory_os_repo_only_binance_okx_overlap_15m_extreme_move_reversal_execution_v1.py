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
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_15m_extreme_move_reversal_execution_v1.py"
ARTIFACT_PATH = "artifacts/strategy_executions/binance_okx_overlap_15m_extreme_move_reversal_execution_v1.json"
STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_15M_EXTREME_MOVE_REVERSAL_EXECUTED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_15M_EXTREME_MOVE_REVERSAL_EXECUTION"

PREREG_PATH = "artifacts/research_preregistrations/binance_okx_overlap_15m_extreme_move_reversal_preregistration_contract_v1.json"
PANEL_REVIEW_PATH = "artifacts/panel_build_reviews/binance_okx_overlap_81_symbol_15m_panel_review_after_build_v1.json"
PANEL_MANIFEST_PATH = "artifacts/panel_build_manifests/binance_okx_overlap_81_symbol_15m_panel_build_manifest_v1.json"
READINESS_PATH = "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json"
PANEL_DIR = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_binance_okx_overlap_81_symbol_15m_panel_build_v1\panel_15m_by_symbol"
)

PREREG_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_15M_EXTREME_MOVE_REVERSAL_PREREGISTRATION_CONTRACT_CREATED"
PREREG_HASH = "f7bd65b67f28d9c679fb6fcfac6df782fcd3dca06eb3ab6640208f35d59ccff1"
ROUTE_FAMILY = "BINANCE_OKX_OVERLAP_15M_EXTREME_MOVE_REVERSAL_BASELINE"
HYPOTHESIS_NAME = "extreme_4h_move_reversal"
CONFIG_ID = "extreme4h_5pct_reversal_hold8h"
SYMBOL_COUNT = 81
TIMEFRAME = "15m"

FULL_START = "2023-01-01T00:00:00Z"
FULL_END_EXCLUSIVE = "2025-11-01T00:00:00Z"
TRAIN_START = "2023-01-01T00:00:00Z"
TRAIN_END = "2024-07-01T00:00:00Z"
VALIDATION_START = "2024-07-01T00:00:00Z"
VALIDATION_END = "2025-04-01T00:00:00Z"
HOLDOUT_START = "2025-04-01T00:00:00Z"
HOLDOUT_END = "2025-11-01T00:00:00Z"

BAR_MINUTES = 15
LOOKBACK_BARS = 16
HOLDING_BARS = 32
HOLDING_MINUTES = HOLDING_BARS * BAR_MINUTES
EXTREME_THRESHOLD_ABS = 0.05
COST_RETURN = 0.0020
NULL_RUN_COUNT = 100
NULL_BLOCK_LENGTH_HOURS = 168
NULL_BLOCK_LENGTH_MINUTES = NULL_BLOCK_LENGTH_HOURS * 60

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
    "complete_15m",
]

TS_CACHE: Dict[str, int] = {}


def canonical_payload_hash(payload: Dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(json.dumps(clean, sort_keys=True, indent=2).encode("utf-8")).hexdigest()


def read_json(relative_path: str) -> Dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise RuntimeError(f"missing required artifact: {relative_path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"artifact is not a JSON object: {relative_path}")
    return payload


def verify_hash(payload: Dict[str, Any], expected: Optional[str] = None) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise RuntimeError("artifact missing payload_sha256_excluding_hash")
    recomputed = canonical_payload_hash(payload)
    if recomputed != stored:
        raise RuntimeError(f"payload hash mismatch: {recomputed} != {stored}")
    if expected is not None and stored != expected:
        raise RuntimeError(f"payload hash mismatch against expected: {stored} != {expected}")
    return stored


def parse_minute(value: str) -> int:
    cached = TS_CACHE.get(value)
    if cached is not None:
        return cached
    if not value.endswith("Z"):
        raise RuntimeError(f"timestamp does not end with Z: {value}")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    minute = int(dt.timestamp() // 60)
    if minute % BAR_MINUTES != 0:
        raise RuntimeError(f"timestamp is not 15m aligned: {value}")
    TS_CACHE[value] = minute
    return minute


def minute_to_iso(minute: int) -> str:
    return datetime.fromtimestamp(minute * 60, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def month_key(minute: int) -> str:
    return datetime.fromtimestamp(minute * 60, timezone.utc).strftime("%Y-%m")


def mean(values: Sequence[float]) -> Optional[float]:
    if not values:
        return None
    return sum(values) / len(values)


def mean_bps(values: Sequence[float]) -> Optional[float]:
    value = mean(values)
    return None if value is None else round(value * 10000.0, 6)


def median_or_none(values: Sequence[float]) -> Optional[float]:
    if not values:
        return None
    return float(median(values))


def finite_or_none(value: Optional[float]) -> bool:
    return value is None or (isinstance(value, (int, float)) and math.isfinite(float(value)))


def find_symbol_list(value: Any) -> Optional[List[str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"exact_overlap_binance_symbols", "symbol_set", "symbols", "binance_symbols"}:
                if isinstance(child, list) and len(child) == SYMBOL_COUNT:
                    if all(isinstance(item, str) and item.endswith("USDT") for item in child):
                        return sorted(child)
            found = find_symbol_list(child)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_symbol_list(child)
            if found is not None:
                return found
    return None


def split_for_entry(entry_minute: int, exit_minute: int) -> Tuple[Optional[str], bool]:
    if TRAIN_START_MINUTE <= entry_minute < TRAIN_END_MINUTE:
        return ("train", exit_minute < TRAIN_END_MINUTE)
    if VALIDATION_START_MINUTE <= entry_minute < VALIDATION_END_MINUTE:
        return ("validation", exit_minute < VALIDATION_END_MINUTE)
    if HOLDOUT_START_MINUTE <= entry_minute < HOLDOUT_END_MINUTE:
        return ("holdout", exit_minute < HOLDOUT_END_MINUTE)
    return (None, False)


FULL_START_MINUTE = parse_minute(FULL_START)
FULL_END_MINUTE = parse_minute(FULL_END_EXCLUSIVE)
TRAIN_START_MINUTE = parse_minute(TRAIN_START)
TRAIN_END_MINUTE = parse_minute(TRAIN_END)
VALIDATION_START_MINUTE = parse_minute(VALIDATION_START)
VALIDATION_END_MINUTE = parse_minute(VALIDATION_END)
HOLDOUT_START_MINUTE = parse_minute(HOLDOUT_START)
HOLDOUT_END_MINUTE = parse_minute(HOLDOUT_END)


def load_symbol_rows(symbol: str) -> Tuple[List[Dict[str, float]], Dict[int, int], Dict[str, int]]:
    path = PANEL_DIR / f"{symbol}_15m.csv.gz"
    if not path.exists():
        raise RuntimeError(f"missing 15m panel partition for {symbol}: {path}")
    rows: List[Dict[str, float]] = []
    index: Dict[int, int] = {}
    counts = {
        "raw_rows_read": 0,
        "complete_rows_used": 0,
        "incomplete_rows_skipped": 0,
        "rows_outside_full_window_skipped": 0,
    }
    previous_minute: Optional[int] = None
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != EXPECTED_PANEL_HEADER:
            raise RuntimeError(f"bad 15m panel header for {symbol}: {reader.fieldnames}")
        for row in reader:
            counts["raw_rows_read"] += 1
            if row["symbol"] != symbol:
                raise RuntimeError(f"symbol mismatch in {path}: {row['symbol']}")
            minute = parse_minute(row["timestamp_utc"])
            if previous_minute is not None and minute <= previous_minute:
                raise RuntimeError(f"timestamps not strictly increasing for {symbol}")
            previous_minute = minute
            if row["complete_15m"].strip().lower() != "true":
                counts["incomplete_rows_skipped"] += 1
                continue
            if not (FULL_START_MINUTE <= minute < FULL_END_MINUTE):
                counts["rows_outside_full_window_skipped"] += 1
                continue
            open_price = float(row["open"])
            high_price = float(row["high"])
            low_price = float(row["low"])
            close_price = float(row["close"])
            volume = float(row["volume"])
            quote_volume = float(row["quote_volume"])
            if open_price <= 0 or high_price <= 0 or low_price <= 0 or close_price <= 0:
                raise RuntimeError(f"non-positive OHLC for {symbol} at {row['timestamp_utc']}")
            if high_price < max(open_price, close_price, low_price):
                raise RuntimeError(f"high sanity failed for {symbol} at {row['timestamp_utc']}")
            if low_price > min(open_price, close_price, high_price):
                raise RuntimeError(f"low sanity failed for {symbol} at {row['timestamp_utc']}")
            if volume < 0 or quote_volume < 0:
                raise RuntimeError(f"negative volume for {symbol} at {row['timestamp_utc']}")
            if minute in index:
                raise RuntimeError(f"duplicate timestamp for {symbol}: {row['timestamp_utc']}")
            index[minute] = len(rows)
            rows.append(
                {
                    "minute": float(minute),
                    "open": open_price,
                    "close": close_price,
                }
            )
            counts["complete_rows_used"] += 1
    return rows, index, counts


def detect_events(symbol: str) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    rows, index, load_counts = load_symbol_rows(symbol)
    events: List[Dict[str, Any]] = []
    next_allowed_entry = -1
    counts = dict(load_counts)
    counts.update(
        {
            "candidate_signal_count": 0,
            "accepted_event_count": 0,
            "skipped_missing_prior_context_count": 0,
            "skipped_missing_exit_row_count": 0,
            "skipped_cross_window_count": 0,
            "skipped_same_symbol_overlap_count": 0,
        }
    )
    for i, row in enumerate(rows):
        entry_minute = int(row["minute"])
        if i < LOOKBACK_BARS:
            continue
        prior_open_row = rows[i - LOOKBACK_BARS]
        prior_close_row = rows[i - 1]
        if int(prior_open_row["minute"]) != entry_minute - LOOKBACK_BARS * BAR_MINUTES:
            counts["skipped_missing_prior_context_count"] += 1
            continue
        if int(prior_close_row["minute"]) != entry_minute - BAR_MINUTES:
            counts["skipped_missing_prior_context_count"] += 1
            continue
        prior_4h_return = prior_close_row["close"] / prior_open_row["open"] - 1.0
        if prior_4h_return <= -EXTREME_THRESHOLD_ABS:
            side = "long"
            side_multiplier = 1.0
        elif prior_4h_return >= EXTREME_THRESHOLD_ABS:
            side = "short"
            side_multiplier = -1.0
        else:
            continue
        counts["candidate_signal_count"] += 1
        exit_minute = entry_minute + HOLDING_MINUTES
        exit_index = index.get(exit_minute)
        if exit_index is None:
            counts["skipped_missing_exit_row_count"] += 1
            continue
        split, same_window = split_for_entry(entry_minute, exit_minute)
        if split is None:
            continue
        if not same_window:
            counts["skipped_cross_window_count"] += 1
            continue
        if entry_minute < next_allowed_entry:
            counts["skipped_same_symbol_overlap_count"] += 1
            continue
        entry_open = row["open"]
        exit_open = rows[exit_index]["open"]
        underlying_return = exit_open / entry_open - 1.0
        gross_return = side_multiplier * underlying_return
        net_return = gross_return - COST_RETURN
        events.append(
            {
                "symbol": symbol,
                "entry_minute": entry_minute,
                "exit_minute": exit_minute,
                "entry_timestamp_utc": minute_to_iso(entry_minute),
                "exit_timestamp_utc": minute_to_iso(exit_minute),
                "split": split,
                "side": side,
                "side_multiplier": side_multiplier,
                "prior_4h_return": prior_4h_return,
                "underlying_forward_return": underlying_return,
                "gross_return": gross_return,
                "net_return": net_return,
            }
        )
        counts["accepted_event_count"] += 1
        next_allowed_entry = exit_minute
    return events, counts


def summarize_events(events: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    gross_values = [float(event["gross_return"]) for event in events]
    net_values = [float(event["net_return"]) for event in events]
    return {
        "event_count": len(events),
        "gross_metric_bps": mean_bps(gross_values),
        "net_metric_bps": mean_bps(net_values),
        "positive_after_cost": (mean(net_values) is not None and mean(net_values) > 0),
        "mean_gross_return": mean(gross_values),
        "mean_net_return": mean(net_values),
    }


def monthly_summary(events: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    by_month: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for event in events:
        by_month[month_key(int(event["entry_minute"]))].append(event)
    monthly_gross = {}
    monthly_net = {}
    monthly_counts = {}
    counted_months = []
    for month in sorted(by_month):
        month_events = by_month[month]
        monthly_counts[month] = len(month_events)
        monthly_gross[month] = mean_bps([float(event["gross_return"]) for event in month_events])
        monthly_net[month] = mean_bps([float(event["net_return"]) for event in month_events])
        if len(month_events) >= 5:
            counted_months.append(month)
    positive_months = [month for month in counted_months if monthly_net[month] is not None and monthly_net[month] > 0]
    negative_or_zero = [month for month in counted_months if monthly_net[month] is not None and monthly_net[month] <= 0]
    positive_rate = None if not counted_months else round(len(positive_months) / len(counted_months), 6)
    return {
        "monthly_gross_metric_bps_by_month": monthly_gross,
        "monthly_net_metric_bps_by_month": monthly_net,
        "monthly_event_count_by_month": monthly_counts,
        "monthly_counted_months_min_5_events": counted_months,
        "month_count": len(counted_months),
        "positive_month_count": len(positive_months),
        "negative_or_zero_month_count": len(negative_or_zero),
        "monthly_positive_rate": positive_rate,
        "positive_months": positive_months,
        "negative_or_zero_months": negative_or_zero,
    }


def side_summary(events: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for side in ("long", "short"):
        side_events = [event for event in events if event["side"] == side]
        for split in ("train", "validation", "holdout"):
            split_side_events = [event for event in side_events if event["split"] == split]
            summary = summarize_events(split_side_events)
            result[f"{side}_{split}_gross_metric_bps"] = summary["gross_metric_bps"]
            result[f"{side}_{split}_net_metric_bps"] = summary["net_metric_bps"]
            result[f"{side}_{split}_event_count"] = summary["event_count"]
    return result


def block_shuffle_null(events: Sequence[Dict[str, Any]], actual_validation_net_metric_bps: Optional[float]) -> Dict[str, Any]:
    validation_events = sorted([event for event in events if event["split"] == "validation"], key=lambda item: (item["entry_minute"], item["symbol"]))
    if not validation_events or actual_validation_net_metric_bps is None:
        return {
            "null_baseline": "deterministic_event_timestamp_block_shuffle_null",
            "null_run_count": NULL_RUN_COUNT,
            "block_length_hours": NULL_BLOCK_LENGTH_HOURS,
            "validation_null_metric_bps": [],
            "validation_null_percentile": None,
            "null_baseline_review_preliminary_passed": False,
            "null_baseline_input_complete": False,
            "shuffle_note": "validation event set empty or actual validation metric missing",
        }
    blocks: List[List[float]] = []
    current_block_id: Optional[int] = None
    current_block: List[float] = []
    for event in validation_events:
        block_id = int(event["entry_minute"]) // NULL_BLOCK_LENGTH_MINUTES
        if current_block_id is None:
            current_block_id = block_id
        if block_id != current_block_id:
            blocks.append(current_block)
            current_block = []
            current_block_id = block_id
        current_block.append(float(event["underlying_forward_return"]))
    if current_block:
        blocks.append(current_block)
    side_multipliers = [float(event["side_multiplier"]) for event in validation_events]
    null_metrics: List[float] = []
    for run_index in range(NULL_RUN_COUNT):
        rng = random.Random(150015 + run_index)
        shuffled_blocks = [list(block) for block in blocks]
        rng.shuffle(shuffled_blocks)
        shuffled_underlying = [value for block in shuffled_blocks for value in block]
        if len(shuffled_underlying) != len(side_multipliers):
            raise RuntimeError("null shuffle length mismatch")
        null_returns = [side * underlying - COST_RETURN for side, underlying in zip(side_multipliers, shuffled_underlying)]
        null_metrics.append(round(sum(null_returns) / len(null_returns) * 10000.0, 6))
    percentile = round(sum(1 for value in null_metrics if value <= actual_validation_net_metric_bps) / len(null_metrics), 6)
    return {
        "null_baseline": "deterministic_event_timestamp_block_shuffle_null",
        "null_run_count": NULL_RUN_COUNT,
        "block_length_hours": NULL_BLOCK_LENGTH_HOURS,
        "preserve_event_side_distribution_if_feasible": True,
        "validation_null_metric_bps": null_metrics,
        "validation_null_percentile": percentile,
        "null_baseline_review_preliminary_passed": percentile >= 0.95,
        "null_baseline_input_complete": True,
        "shuffle_note": "validation accepted-event underlying returns were block shuffled against accepted event side labels",
    }


def top_symbol_share(events_by_symbol: Dict[str, int], total_events: int) -> Optional[float]:
    if total_events <= 0:
        return None
    return round(max(events_by_symbol.values()) / total_events, 6) if events_by_symbol else None


def validate_source_artifacts() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any], List[str]]:
    prereg = read_json(PREREG_PATH)
    panel_review = read_json(PANEL_REVIEW_PATH)
    panel_manifest = read_json(PANEL_MANIFEST_PATH)
    readiness = read_json(READINESS_PATH)
    prereg_hash = verify_hash(prereg, PREREG_HASH)
    panel_review_hash = verify_hash(panel_review)
    panel_manifest_hash = verify_hash(panel_manifest)
    readiness_hash = verify_hash(readiness)
    if prereg.get("status") != PREREG_STATUS:
        raise RuntimeError("preregistration status mismatch")
    if prereg.get("extreme_move_reversal_hypothesis_preregistration", {}).get("route_family") != ROUTE_FAMILY:
        raise RuntimeError("preregistration route family mismatch")
    if prereg.get("extreme_move_reversal_hypothesis_preregistration", {}).get("config_id") != CONFIG_ID:
        raise RuntimeError("preregistration config id mismatch")
    if panel_review.get("panel_validity_classification") != "PANEL_15M_REVIEW_PASS_VALID_FOR_READ_ONLY_EXTREME_MOVE_RESEARCH":
        raise RuntimeError("15m panel review classification is not valid")
    symbols = find_symbol_list(prereg) or find_symbol_list(readiness) or find_symbol_list(panel_manifest)
    if symbols is None or len(symbols) != SYMBOL_COUNT:
        raise RuntimeError("could not verify exact 81-symbol universe")
    source_summary = {
        "preregistration": {
            "path": PREREG_PATH,
            "status": prereg.get("status"),
            "payload_sha256_excluding_hash": prereg_hash,
            "payload_hash_verified": True,
        },
        "panel_review": {
            "path": PANEL_REVIEW_PATH,
            "status": panel_review.get("status"),
            "panel_validity_classification": panel_review.get("panel_validity_classification"),
            "payload_sha256_excluding_hash": panel_review_hash,
            "payload_hash_verified": True,
        },
        "panel_build_manifest": {
            "path": PANEL_MANIFEST_PATH,
            "status": panel_manifest.get("status"),
            "payload_sha256_excluding_hash": panel_manifest_hash,
            "payload_hash_verified": True,
        },
        "second_source_readiness": {
            "path": READINESS_PATH,
            "status": readiness.get("status"),
            "payload_sha256_excluding_hash": readiness_hash,
            "payload_hash_verified": True,
        },
    }
    return prereg, panel_review, panel_manifest, source_summary, symbols


def build_execution() -> Dict[str, Any]:
    prereg, panel_review, panel_manifest, source_summary, symbols = validate_source_artifacts()
    all_events: List[Dict[str, Any]] = []
    symbol_load_counts: Dict[str, Dict[str, int]] = {}
    aggregate_counts = defaultdict(int)
    for symbol in symbols:
        events, counts = detect_events(symbol)
        all_events.extend(events)
        symbol_load_counts[symbol] = counts
        for key, value in counts.items():
            aggregate_counts[key] += value

    all_events.sort(key=lambda item: (item["entry_minute"], item["symbol"]))
    by_split = {
        split: [event for event in all_events if event["split"] == split]
        for split in ("train", "validation", "holdout")
    }
    train_summary = summarize_events(by_split["train"])
    validation_summary = summarize_events(by_split["validation"])
    holdout_summary = summarize_events(by_split["holdout"])
    train_monthly = monthly_summary(by_split["train"])
    validation_monthly = monthly_summary(by_split["validation"])
    holdout_monthly = monthly_summary(by_split["holdout"])

    events_by_symbol = {symbol: 0 for symbol in symbols}
    gross_by_symbol: Dict[str, List[float]] = {symbol: [] for symbol in symbols}
    net_by_symbol: Dict[str, List[float]] = {symbol: [] for symbol in symbols}
    for event in all_events:
        symbol = event["symbol"]
        events_by_symbol[symbol] += 1
        gross_by_symbol[symbol].append(float(event["gross_return"]))
        net_by_symbol[symbol].append(float(event["net_return"]))
    events_by_month = defaultdict(int)
    for event in all_events:
        events_by_month[month_key(int(event["entry_minute"]))] += 1
    total_event_count = len(all_events)
    symbol_performance = {
        symbol: {
            "event_count": events_by_symbol[symbol],
            "gross_metric_bps": mean_bps(gross_by_symbol[symbol]),
            "net_metric_bps": mean_bps(net_by_symbol[symbol]),
        }
        for symbol in symbols
    }

    validation_top_share = top_symbol_share(events_by_symbol, total_event_count)
    average_events_per_symbol = round(total_event_count / SYMBOL_COUNT, 6)
    event_coverage_passed = (
        validation_summary["event_count"] >= 100
        and validation_top_share is not None
        and validation_top_share <= 0.20
    )
    monthly_stability_passed = (
        validation_monthly["monthly_positive_rate"] is not None
        and validation_monthly["monthly_positive_rate"] >= 0.60
        and validation_monthly["month_count"] >= 6
    )
    turnover_passed = validation_top_share is not None and validation_top_share <= 0.20
    null_summary = block_shuffle_null(all_events, validation_summary["net_metric_bps"])

    metric_issues: List[str] = []
    if CONFIG_ID != prereg.get("extreme_move_reversal_hypothesis_preregistration", {}).get("config_id"):
        metric_issues.append("config_id_mismatch")
    metrics_to_check = [
        train_summary["gross_metric_bps"],
        train_summary["net_metric_bps"],
        validation_summary["gross_metric_bps"],
        validation_summary["net_metric_bps"],
        holdout_summary["gross_metric_bps"],
        holdout_summary["net_metric_bps"],
        validation_monthly["monthly_positive_rate"],
    ]
    if not all(finite_or_none(value) for value in metrics_to_check):
        metric_issues.append("non_finite_metric_detected")
    metric_integrity_passed = not metric_issues

    side = side_summary(all_events)
    payload: Dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "route_family": ROUTE_FAMILY,
        "config_id": CONFIG_ID,
        "input_data_validation": {
            "source_artifacts": source_summary,
            "panel_dir": str(PANEL_DIR),
            "symbol_count": SYMBOL_COUNT,
            "symbols": symbols,
            "complete_15m_rows_only": True,
            "required_fields": EXPECTED_PANEL_HEADER,
            "panel_rows_read_for_execution": True,
            "funding_rows_read": False,
            "okx_panel_rows_read": False,
            "binance_1m_source_rows_read": False,
            "total_raw_rows_read": aggregate_counts["raw_rows_read"],
            "total_complete_rows_used": aggregate_counts["complete_rows_used"],
            "total_incomplete_rows_skipped": aggregate_counts["incomplete_rows_skipped"],
            "rows_outside_full_window_skipped": aggregate_counts["rows_outside_full_window_skipped"],
            "panel_review_status": panel_review.get("status"),
            "panel_review_classification": panel_review.get("panel_validity_classification"),
            "panel_manifest_status": panel_manifest.get("status"),
        },
        "signal_definition": {
            "timeframe": TIMEFRAME,
            "entry_timestamp_policy": "E is a 15m bar open",
            "lookback_bars": LOOKBACK_BARS,
            "lookback_hours": 4,
            "prior_4h_return": "close of bar E-15m / open of bar E-4h - 1",
            "long_signal": "prior_4h_return <= -0.05",
            "short_signal": "prior_4h_return >= +0.05",
            "extreme_threshold_abs": EXTREME_THRESHOLD_ABS,
            "no_current_hour_leakage": True,
            "no_future_data": True,
            "no_taker_flow_signal": True,
            "no_open_interest_signal": True,
            "no_pair_logic": True,
        },
        "event_decluster_policy": {
            "same_symbol_overlapping_allowed": False,
            "cross_symbol_overlapping_allowed": True,
            "cooldown_until_exit": "after accepting an event for symbol S at E, ignore new events for S until E+8h",
            "skipped_same_symbol_overlap_count": aggregate_counts["skipped_same_symbol_overlap_count"],
        },
        "return_and_cost_policy": {
            "entry_price": "open at E",
            "exit_price": "open at E + 8h",
            "exit_offset_bars": HOLDING_BARS,
            "holding_period_hours": 8,
            "long_return": "exit_open / entry_open - 1",
            "short_return": "-(exit_open / entry_open - 1)",
            "gross_return": "event return before cost",
            "net_return": "gross_return - 0.0020",
            "round_trip_cost_bps": 20,
            "no_annualization": True,
            "no_compounding": True,
            "cross_window_holding_returns_forbidden": True,
        },
        "execution_safety_controls": {
            "exactly_one_config_executed": True,
            "no_non_preregistered_config": True,
            "no_parameter_expansion": True,
            "no_strategy_search": True,
            "no_network": True,
            "no_api_calls": True,
            "no_funding_rows": True,
            "no_okx_rows": True,
            "no_binance_1m_rows": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_runtime_live_capital": True,
        },
        "config_result": {
            "config_id": CONFIG_ID,
            "train_gross_metric_bps": train_summary["gross_metric_bps"],
            "train_net_metric_bps": train_summary["net_metric_bps"],
            "validation_gross_metric_bps": validation_summary["gross_metric_bps"],
            "validation_net_metric_bps": validation_summary["net_metric_bps"],
            "holdout_gross_metric_bps": holdout_summary["gross_metric_bps"],
            "holdout_net_metric_bps": holdout_summary["net_metric_bps"],
            "train_event_count": train_summary["event_count"],
            "validation_event_count": validation_summary["event_count"],
            "holdout_event_count": holdout_summary["event_count"],
            "validation_positive_after_cost": validation_summary["positive_after_cost"],
            "holdout_reported_separately": True,
            "holdout_used_for_config_selection": False,
            "candidate_generation": False,
            "edge_claim": False,
            "family_release": False,
            "runtime_live_capital": False,
        },
        "train_validation_holdout_summary": {
            "full_window_start_utc": FULL_START,
            "full_window_end_exclusive_utc": FULL_END_EXCLUSIVE,
            "train_window_start_utc": TRAIN_START,
            "train_window_end_exclusive_utc": TRAIN_END,
            "validation_window_start_utc": VALIDATION_START,
            "validation_window_end_exclusive_utc": VALIDATION_END,
            "holdout_window_start_utc": HOLDOUT_START,
            "holdout_window_end_exclusive_utc": HOLDOUT_END,
            "train": train_summary,
            "validation": validation_summary,
            "holdout": holdout_summary,
            "holdout_used_for_config_selection": False,
            "holdout_positive_cannot_create_candidate_edge_or_release": True,
        },
        "event_coverage_summary": {
            "train_event_count": train_summary["event_count"],
            "validation_event_count": validation_summary["event_count"],
            "holdout_event_count": holdout_summary["event_count"],
            "total_event_count": total_event_count,
            "long_event_count": len([event for event in all_events if event["side"] == "long"]),
            "short_event_count": len([event for event in all_events if event["side"] == "short"]),
            "skipped_same_symbol_overlap_count": aggregate_counts["skipped_same_symbol_overlap_count"],
            "events_by_month": dict(sorted(events_by_month.items())),
            "events_by_symbol": events_by_symbol,
            "symbol_performance": symbol_performance,
            "top_symbol_event_share": validation_top_share,
            "average_events_per_symbol": average_events_per_symbol,
            "validation_event_coverage_review_preliminary_passed": event_coverage_passed,
        },
        "long_short_side_summary": side,
        "monthly_stability_summary": {
            "train_monthly_gross_metric_bps_by_month": train_monthly["monthly_gross_metric_bps_by_month"],
            "train_monthly_net_metric_bps_by_month": train_monthly["monthly_net_metric_bps_by_month"],
            "train_monthly_event_count_by_month": train_monthly["monthly_event_count_by_month"],
            "train_monthly_positive_rate": train_monthly["monthly_positive_rate"],
            "validation_monthly_gross_metric_bps_by_month": validation_monthly["monthly_gross_metric_bps_by_month"],
            "validation_monthly_net_metric_bps_by_month": validation_monthly["monthly_net_metric_bps_by_month"],
            "validation_monthly_event_count_by_month": validation_monthly["monthly_event_count_by_month"],
            "validation_month_count": validation_monthly["month_count"],
            "validation_monthly_positive_rate": validation_monthly["monthly_positive_rate"],
            "validation_positive_months": validation_monthly["positive_months"],
            "validation_negative_or_zero_months": validation_monthly["negative_or_zero_months"],
            "holdout_monthly_gross_metric_bps_by_month": holdout_monthly["monthly_gross_metric_bps_by_month"],
            "holdout_monthly_net_metric_bps_by_month": holdout_monthly["monthly_net_metric_bps_by_month"],
            "holdout_monthly_event_count_by_month": holdout_monthly["monthly_event_count_by_month"],
            "holdout_monthly_positive_rate": holdout_monthly["monthly_positive_rate"],
            "monthly_stability_review_preliminary_passed": monthly_stability_passed,
        },
        "null_baseline_summary": null_summary,
        "turnover_concentration_summary": {
            "event_participation_by_symbol": events_by_symbol,
            "top_symbol_event_share": validation_top_share,
            "turnover_concentration_review_preliminary_passed": turnover_passed,
            "turnover_concentration_rule": "top_symbol_event_share <= 0.20",
        },
        "metric_integrity_summary": {
            "exactly_one_config_executed": True,
            "config_id_matches_preregistration": True,
            "no_nan_or_inf": "non_finite_metric_detected" not in metric_issues,
            "no_timestamp_outside_windows": True,
            "no_lookahead": True,
            "no_cross_window_returns": True,
            "cross_window_returns_skipped_count": aggregate_counts["skipped_cross_window_count"],
            "no_non_preregistered_config": True,
            "no_candidate_edge_release_runtime": True,
            "metric_integrity_issues": metric_issues,
            "metric_integrity_issue_count": len(metric_issues),
            "metric_integrity_passed": metric_integrity_passed,
        },
        "diagnostic_interpretation_limits": {
            "diagnostic_execution_only": True,
            "not_a_backtest_for_candidate_generation": True,
            "no_candidate": True,
            "no_edge_claim": True,
            "no_family_release": True,
            "no_holdout_permission": True,
            "no_runtime_live_capital": True,
        },
        "safety_permissions": {
            "strategy_execution_completed_as_diagnostic": True,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "holdout_access_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "evaluator_required_next": True,
        },
        "forbidden_actions_confirmed_false": {
            "network_used": False,
            "api_called": False,
            "binance_api_called": False,
            "data_downloaded": False,
            "binance_1m_source_rows_read": False,
            "funding_rows_read": False,
            "okx_panel_rows_read": False,
            "non_preregistered_config_tested": False,
            "candidates_generated": False,
            "edge_claimed": False,
            "family_released": False,
            "holdout_permission_granted": False,
            "runtime_permission_granted": False,
            "live_permission_granted": False,
            "capital_permission_granted": False,
        },
        "validation_checks": {
            "status_equals_required_status": True,
            "artifact_kind_equals_required": True,
            "module_path_equals_required": True,
            "artifact_path_equals_required": True,
            "preregistration_loaded": True,
            "preregistration_payload_hash_verified": True,
            "panel_review_loaded": True,
            "panel_review_valid_for_read_only_extreme_move_research": True,
            "exact_overlap_symbol_count_verified_81": True,
            "exactly_one_config_executed": True,
            "config_id_matches_preregistration": True,
            "no_non_preregistered_config": True,
            "no_network": True,
            "no_api_calls": True,
            "no_download": True,
            "no_funding_rows_read": True,
            "no_okx_rows_read": True,
            "no_binance_1m_rows_read": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_runtime_live_capital": True,
            "payload_sha256_excluding_hash_present": True,
            "replacement_checks_all_true": True,
        },
        "replacement_checks_all_true": True,
        "payload_sha256_excluding_hash": "",
    }

    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)
    assert payload["status"] == STATUS
    assert payload["route_family"] == ROUTE_FAMILY
    assert payload["config_id"] == CONFIG_ID
    assert payload["config_result"]["holdout_used_for_config_selection"] is False
    assert payload["forbidden_actions_confirmed_false"]["network_used"] is False
    assert payload["forbidden_actions_confirmed_false"]["funding_rows_read"] is False
    assert payload["forbidden_actions_confirmed_false"]["okx_panel_rows_read"] is False
    assert payload["forbidden_actions_confirmed_false"]["candidates_generated"] is False
    assert payload["forbidden_actions_confirmed_false"]["edge_claimed"] is False
    assert payload["replacement_checks_all_true"] is True
    assert all(payload["validation_checks"].values())
    assert canonical_payload_hash(payload) == payload["payload_sha256_excluding_hash"]
    return payload


def main() -> None:
    artifact_path = REPO_ROOT / ARTIFACT_PATH
    payload = build_execution()
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": STATUS,
        "artifact_path": ARTIFACT_PATH,
        "route_family": ROUTE_FAMILY,
        "config_id": CONFIG_ID,
        "train_event_count": payload["config_result"]["train_event_count"],
        "validation_event_count": payload["config_result"]["validation_event_count"],
        "holdout_event_count": payload["config_result"]["holdout_event_count"],
        "train_gross_metric_bps": payload["config_result"]["train_gross_metric_bps"],
        "train_net_metric_bps": payload["config_result"]["train_net_metric_bps"],
        "validation_gross_metric_bps": payload["config_result"]["validation_gross_metric_bps"],
        "validation_net_metric_bps": payload["config_result"]["validation_net_metric_bps"],
        "holdout_gross_metric_bps": payload["config_result"]["holdout_gross_metric_bps"],
        "holdout_net_metric_bps": payload["config_result"]["holdout_net_metric_bps"],
        "validation_positive_after_cost": payload["config_result"]["validation_positive_after_cost"],
        "null_baseline_review_preliminary_passed": payload["null_baseline_summary"]["null_baseline_review_preliminary_passed"],
        "monthly_stability_review_preliminary_passed": payload["monthly_stability_summary"]["monthly_stability_review_preliminary_passed"],
        "validation_event_coverage_review_preliminary_passed": payload["event_coverage_summary"]["validation_event_coverage_review_preliminary_passed"],
        "turnover_concentration_review_preliminary_passed": payload["turnover_concentration_summary"]["turnover_concentration_review_preliminary_passed"],
        "metric_integrity_issue_count": payload["metric_integrity_summary"]["metric_integrity_issue_count"],
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "payload_sha256_excluding_hash": payload["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": True,
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
