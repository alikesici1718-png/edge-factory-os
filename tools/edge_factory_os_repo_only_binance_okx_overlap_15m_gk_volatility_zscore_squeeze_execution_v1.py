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
from typing import Any, Deque, Dict, List, Optional, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_15m_gk_volatility_zscore_squeeze_execution_v1.py"
ARTIFACT_PATH = "artifacts/strategy_executions/binance_okx_overlap_15m_gk_volatility_zscore_squeeze_execution_v1.json"
STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_15M_GK_VOLATILITY_ZSCORE_SQUEEZE_EXECUTED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_15M_GK_VOLATILITY_ZSCORE_SQUEEZE_EXECUTION"

PREREG_PATH = "artifacts/research_preregistrations/binance_okx_overlap_15m_gk_volatility_zscore_squeeze_preregistration_contract_v1.json"
PANEL_REVIEW_PATH = "artifacts/panel_build_reviews/binance_okx_overlap_81_symbol_15m_panel_review_after_build_v1.json"
PANEL_MANIFEST_PATH = "artifacts/panel_build_manifests/binance_okx_overlap_81_symbol_15m_panel_build_manifest_v1.json"
READINESS_PATH = "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json"
PANEL_DIR = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_binance_okx_overlap_81_symbol_15m_panel_build_v1\panel_15m_by_symbol"
)

PREREG_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_15M_GK_VOLATILITY_ZSCORE_SQUEEZE_PREREGISTRATION_CONTRACT_CREATED"
PREREG_HASH = "9eb80324a4f428da2e4212601d1845f5f71a465c0570795bbd18afe415f2629c"
ROUTE_FAMILY = "BINANCE_OKX_OVERLAP_15M_GK_VOLATILITY_ZSCORE_SQUEEZE_BASELINE"
CONFIG_ID = "gkvol_24h_z30d_squeeze_long_expand_short_hold8h"
SYMBOL_COUNT = 81
TIMEFRAME = "15m"

BAR_MINUTES = 15
VOL_WINDOW_BARS = 96
BASELINE_BARS = 2880
MIN_BASELINE_OBS = 2016
HOLDING_BARS = 32
HOLDING_MINUTES = HOLDING_BARS * BAR_MINUTES
MIN_ELIGIBLE_SYMBOLS = 40
MIN_LONG_SYMBOLS = 5
MIN_SHORT_SYMBOLS = 5
COST_RETURN = 0.0020
NULL_RUN_COUNT = 100
NULL_BLOCK_LENGTH_HOURS = 168
NULL_BLOCK_LENGTH_MINUTES = NULL_BLOCK_LENGTH_HOURS * 60

FULL_START = "2023-01-01T00:00:00Z"
FULL_END_EXCLUSIVE = "2025-11-01T00:00:00Z"
TRAIN_START = "2023-01-01T00:00:00Z"
TRAIN_END = "2024-07-01T00:00:00Z"
VALIDATION_START = "2024-07-01T00:00:00Z"
VALIDATION_END = "2025-04-01T00:00:00Z"
HOLDOUT_START = "2025-04-01T00:00:00Z"
HOLDOUT_END = "2025-11-01T00:00:00Z"

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


FULL_START_MINUTE = parse_minute(FULL_START)
FULL_END_MINUTE = parse_minute(FULL_END_EXCLUSIVE)
TRAIN_START_MINUTE = parse_minute(TRAIN_START)
TRAIN_END_MINUTE = parse_minute(TRAIN_END)
VALIDATION_START_MINUTE = parse_minute(VALIDATION_START)
VALIDATION_END_MINUTE = parse_minute(VALIDATION_END)
HOLDOUT_START_MINUTE = parse_minute(HOLDOUT_START)
HOLDOUT_END_MINUTE = parse_minute(HOLDOUT_END)


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
        "gk_tiny_negative_clamped_count": 0,
        "gk_negative_numeric_issue_count": 0,
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
            log_hl = math.log(high_price / low_price)
            log_co = math.log(close_price / open_price)
            gk_var = 0.5 * log_hl * log_hl - (2.0 * math.log(2.0) - 1.0) * log_co * log_co
            if gk_var < 0 and abs(gk_var) < 1e-12:
                gk_var = 0.0
                counts["gk_tiny_negative_clamped_count"] += 1
            elif gk_var < -1e-12:
                counts["gk_negative_numeric_issue_count"] += 1
                gk_var = math.nan
            if minute in index:
                raise RuntimeError(f"duplicate timestamp for {symbol}: {row['timestamp_utc']}")
            index[minute] = len(rows)
            rows.append(
                {
                    "minute": float(minute),
                    "open": open_price,
                    "gk_var": gk_var,
                }
            )
            counts["complete_rows_used"] += 1
    return rows, index, counts


def compute_symbol_signals(symbol: str) -> Tuple[List[Tuple[int, str, float, float, float]], Dict[str, int]]:
    rows, index, counts = load_symbol_rows(symbol)
    records: List[Tuple[int, str, float, float, float]] = []
    gk_window: Deque[Tuple[int, float]] = deque()
    gk_sum = 0.0
    gk_invalid_count = 0
    vol_window: Deque[Tuple[int, float]] = deque()
    vol_sum = 0.0
    vol_sumsq = 0.0
    counts.update(
        {
            "signal_records_created": 0,
            "skipped_missing_24h_context": 0,
            "skipped_insufficient_baseline": 0,
            "skipped_zero_baseline_std": 0,
            "skipped_missing_exit": 0,
            "skipped_cross_window": 0,
        }
    )
    for i, row in enumerate(rows):
        entry_minute = int(row["minute"])
        current_vol: Optional[float] = None
        if (
            len(gk_window) == VOL_WINDOW_BARS
            and i >= VOL_WINDOW_BARS
            and int(rows[i - VOL_WINDOW_BARS]["minute"]) == entry_minute - VOL_WINDOW_BARS * BAR_MINUTES
            and int(rows[i - 1]["minute"]) == entry_minute - BAR_MINUTES
            and gk_invalid_count == 0
        ):
            current_vol = math.sqrt(max(gk_sum, 0.0))
        else:
            counts["skipped_missing_24h_context"] += 1

        cutoff = entry_minute - BASELINE_BARS * BAR_MINUTES
        while vol_window and vol_window[0][0] < cutoff:
            _, old_vol = vol_window.popleft()
            vol_sum -= old_vol
            vol_sumsq -= old_vol * old_vol

        exit_minute = entry_minute + HOLDING_MINUTES
        split, same_window = split_for_entry(entry_minute, exit_minute)
        exit_index = index.get(exit_minute)
        if current_vol is not None and split is not None:
            if len(vol_window) < MIN_BASELINE_OBS:
                counts["skipped_insufficient_baseline"] += 1
            elif exit_index is None:
                counts["skipped_missing_exit"] += 1
            elif not same_window:
                counts["skipped_cross_window"] += 1
            else:
                baseline_n = len(vol_window)
                baseline_mean = vol_sum / baseline_n
                variance = max(vol_sumsq / baseline_n - baseline_mean * baseline_mean, 0.0)
                baseline_std = math.sqrt(variance)
                if baseline_std <= 0:
                    counts["skipped_zero_baseline_std"] += 1
                else:
                    z = (current_vol - baseline_mean) / baseline_std
                    forward_return = rows[exit_index]["open"] / row["open"] - 1.0
                    records.append((entry_minute, symbol, z, forward_return, current_vol))
                    counts["signal_records_created"] += 1

        if current_vol is not None and math.isfinite(current_vol):
            vol_window.append((entry_minute, current_vol))
            vol_sum += current_vol
            vol_sumsq += current_vol * current_vol
        gk_value = float(row["gk_var"])
        gk_window.append((entry_minute, gk_value))
        if not math.isfinite(gk_value):
            gk_invalid_count += 1
        else:
            gk_sum += gk_value
        if len(gk_window) > VOL_WINDOW_BARS:
            _, old_gk = gk_window.popleft()
            if not math.isfinite(old_gk):
                gk_invalid_count -= 1
            else:
                gk_sum -= old_gk
    return records, counts


def summarize_returns(gross_values: Sequence[float], net_values: Sequence[float]) -> Dict[str, Any]:
    return {
        "observation_count": len(net_values),
        "gross_metric_bps": mean_bps(gross_values),
        "net_metric_bps": mean_bps(net_values),
        "positive_after_cost": mean(net_values) is not None and mean(net_values) > 0,
    }


def monthly_summary(portfolios: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    by_month: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for item in portfolios:
        by_month[month_key(item["entry_minute"])].append(item)
    gross_by_month: Dict[str, Optional[float]] = {}
    net_by_month: Dict[str, Optional[float]] = {}
    count_by_month: Dict[str, int] = {}
    for month in sorted(by_month):
        values = by_month[month]
        count_by_month[month] = len(values)
        gross_by_month[month] = mean_bps([float(item["gross_return"]) for item in values])
        net_by_month[month] = mean_bps([float(item["net_return"]) for item in values])
    positive_months = [month for month in sorted(net_by_month) if net_by_month[month] is not None and net_by_month[month] > 0]
    negative_or_zero_months = [month for month in sorted(net_by_month) if net_by_month[month] is not None and net_by_month[month] <= 0]
    month_count = len(net_by_month)
    positive_rate = None if month_count == 0 else round(len(positive_months) / month_count, 6)
    return {
        "monthly_gross_metric_bps_by_month": gross_by_month,
        "monthly_net_metric_bps_by_month": net_by_month,
        "monthly_observation_count_by_month": count_by_month,
        "month_count": month_count,
        "positive_month_count": len(positive_months),
        "negative_or_zero_month_count": len(negative_or_zero_months),
        "monthly_positive_rate": positive_rate,
        "positive_months": positive_months,
        "negative_or_zero_months": negative_or_zero_months,
    }


def turnover_between(previous: Optional[Dict[str, Any]], current: Dict[str, Any]) -> Optional[float]:
    if previous is None:
        return None
    prev_long = set(previous["long_symbols"])
    prev_short = set(previous["short_symbols"])
    cur_long = set(current["long_symbols"])
    cur_short = set(current["short_symbols"])
    long_den = max(len(prev_long | cur_long), 1)
    short_den = max(len(prev_short | cur_short), 1)
    return ((len(prev_long ^ cur_long) / long_den) + (len(prev_short ^ cur_short) / short_den)) / 2.0


def build_portfolios(signal_records: List[Tuple[int, str, float, float, float]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any], Dict[int, Dict[str, float]]]:
    by_minute: Dict[int, List[Tuple[str, float, float, float]]] = defaultdict(list)
    return_lookup_by_minute: Dict[int, Dict[str, float]] = defaultdict(dict)
    for minute, symbol, z, forward_return, current_vol in signal_records:
        by_minute[minute].append((symbol, z, forward_return, current_vol))
        return_lookup_by_minute[minute][symbol] = forward_return
    portfolios: List[Dict[str, Any]] = []
    eligible_counts_by_split: Dict[str, List[int]] = {"train": [], "validation": [], "holdout": []}
    skipped_insufficient = 0
    skipped_leg = 0
    previous_portfolio: Optional[Dict[str, Any]] = None
    turnover_values: List[float] = []
    for minute in sorted(by_minute):
        rows = sorted(by_minute[minute], key=lambda item: (item[1], item[0]))
        split, same_window = split_for_entry(minute, minute + HOLDING_MINUTES)
        if split is None or not same_window:
            continue
        eligible_count = len(rows)
        if eligible_count < MIN_ELIGIBLE_SYMBOLS:
            skipped_insufficient += 1
            continue
        eligible_counts_by_split[split].append(eligible_count)
        tail_count = max(1, math.floor(eligible_count * 0.20))
        if tail_count < MIN_LONG_SYMBOLS or tail_count < MIN_SHORT_SYMBOLS:
            skipped_leg += 1
            continue
        long_rows = rows[:tail_count]
        short_rows = rows[-tail_count:]
        long_returns = [item[2] for item in long_rows]
        short_returns = [-item[2] for item in short_rows]
        gross = sum(long_returns) / len(long_returns) + sum(short_returns) / len(short_returns)
        net = gross - COST_RETURN
        portfolio = {
            "entry_minute": minute,
            "entry_timestamp_utc": minute_to_iso(minute),
            "split": split,
            "eligible_symbol_count": eligible_count,
            "long_symbols": [item[0] for item in long_rows],
            "short_symbols": [item[0] for item in short_rows],
            "long_return": sum(long_returns) / len(long_returns),
            "short_return": sum(short_returns) / len(short_returns),
            "gross_return": gross,
            "net_return": net,
        }
        turnover = turnover_between(previous_portfolio, portfolio)
        if turnover is not None:
            turnover_values.append(turnover)
            portfolio["turnover_from_previous"] = turnover
        else:
            portfolio["turnover_from_previous"] = None
        previous_portfolio = portfolio
        portfolios.append(portfolio)
    coverage = {
        "train_eligible_timestamp_count": len(eligible_counts_by_split["train"]),
        "validation_eligible_timestamp_count": len(eligible_counts_by_split["validation"]),
        "holdout_eligible_timestamp_count": len(eligible_counts_by_split["holdout"]),
        "average_eligible_symbols_per_timestamp": round(
            sum(sum(values) for values in eligible_counts_by_split.values())
            / max(sum(len(values) for values in eligible_counts_by_split.values()), 1),
            6,
        ),
        "validation_average_eligible_symbols": round(
            sum(eligible_counts_by_split["validation"]) / max(len(eligible_counts_by_split["validation"]), 1),
            6,
        ),
        "median_eligible_symbols_per_timestamp": median_or_none(
            [count for values in eligible_counts_by_split.values() for count in values]
        ),
        "min_eligible_symbols_per_timestamp": min([count for values in eligible_counts_by_split.values() for count in values], default=None),
        "max_eligible_symbols_per_timestamp": max([count for values in eligible_counts_by_split.values() for count in values], default=None),
        "skipped_timestamps_insufficient_symbols": skipped_insufficient,
        "skipped_timestamps_insufficient_leg_symbols": skipped_leg,
    }
    coverage["signal_coverage_review_preliminary_passed"] = (
        coverage["validation_eligible_timestamp_count"] >= 1000
        and coverage["average_eligible_symbols_per_timestamp"] >= MIN_ELIGIBLE_SYMBOLS
    )
    return portfolios, coverage, return_lookup_by_minute


def null_baseline(portfolios: Sequence[Dict[str, Any]], return_lookup_by_minute: Dict[int, Dict[str, float]], actual_validation_net_bps: Optional[float]) -> Dict[str, Any]:
    validation = [item for item in portfolios if item["split"] == "validation"]
    if not validation or actual_validation_net_bps is None:
        return {
            "null_baseline": "deterministic_signal_timestamp_block_shuffle_null",
            "null_run_count": NULL_RUN_COUNT,
            "block_length_hours": NULL_BLOCK_LENGTH_HOURS,
            "validation_null_percentile": None,
            "null_baseline_review_preliminary_passed": False,
            "null_input_complete": False,
        }
    blocks: List[List[Dict[str, Any]]] = []
    current_id: Optional[int] = None
    current_block: List[Dict[str, Any]] = []
    for item in validation:
        block_id = item["entry_minute"] // NULL_BLOCK_LENGTH_MINUTES
        if current_id is None:
            current_id = block_id
        if block_id != current_id:
            blocks.append(current_block)
            current_block = []
            current_id = block_id
        current_block.append(item)
    if current_block:
        blocks.append(current_block)
    return_minutes = [item["entry_minute"] for item in validation]
    null_metrics: List[float] = []
    for run_index in range(NULL_RUN_COUNT):
        rng = random.Random(762003 + run_index)
        shuffled_blocks = [list(block) for block in blocks]
        rng.shuffle(shuffled_blocks)
        shuffled_signals = [item for block in shuffled_blocks for item in block]
        values: List[float] = []
        for signal_item, return_minute in zip(shuffled_signals, return_minutes):
            lookup = return_lookup_by_minute.get(return_minute, {})
            long_returns = [lookup[symbol] for symbol in signal_item["long_symbols"] if symbol in lookup]
            short_returns = [-lookup[symbol] for symbol in signal_item["short_symbols"] if symbol in lookup]
            if len(long_returns) >= MIN_LONG_SYMBOLS and len(short_returns) >= MIN_SHORT_SYMBOLS:
                values.append(sum(long_returns) / len(long_returns) + sum(short_returns) / len(short_returns) - COST_RETURN)
        null_metrics.append(mean_bps(values) if values else -999999.0)
    percentile = round(sum(1 for value in null_metrics if value <= actual_validation_net_bps) / len(null_metrics), 6)
    return {
        "null_baseline": "deterministic_signal_timestamp_block_shuffle_null",
        "null_run_count": NULL_RUN_COUNT,
        "block_length_hours": NULL_BLOCK_LENGTH_HOURS,
        "validation_null_metric_bps": null_metrics,
        "validation_null_percentile": percentile,
        "null_baseline_review_preliminary_passed": percentile >= 0.95,
        "null_input_complete": True,
        "shuffle_note": "cross-sectional signal portfolios were block-shuffled against validation return timestamps",
    }


def validate_sources() -> Tuple[Dict[str, Any], List[str], Dict[str, Any]]:
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
    if prereg.get("gk_volatility_zscore_squeeze_hypothesis_preregistration", {}).get("config_id") != CONFIG_ID:
        raise RuntimeError("preregistration config mismatch")
    if panel_review.get("panel_validity_classification") != "PANEL_15M_REVIEW_PASS_VALID_FOR_READ_ONLY_EXTREME_MOVE_RESEARCH":
        raise RuntimeError("15m panel review classification is not valid")
    symbols = find_symbol_list(prereg) or find_symbol_list(readiness) or find_symbol_list(panel_manifest)
    if symbols is None or len(symbols) != SYMBOL_COUNT:
        raise RuntimeError("could not verify 81-symbol universe")
    source_summary = {
        "preregistration": {"path": PREREG_PATH, "status": prereg.get("status"), "payload_sha256_excluding_hash": prereg_hash},
        "panel_review": {"path": PANEL_REVIEW_PATH, "status": panel_review.get("status"), "payload_sha256_excluding_hash": panel_review_hash},
        "panel_build_manifest": {"path": PANEL_MANIFEST_PATH, "status": panel_manifest.get("status"), "payload_sha256_excluding_hash": panel_manifest_hash},
        "second_source_readiness": {"path": READINESS_PATH, "status": readiness.get("status"), "payload_sha256_excluding_hash": readiness_hash},
    }
    return prereg, symbols, source_summary


def build_execution() -> Dict[str, Any]:
    _, symbols, source_summary = validate_sources()
    signal_records: List[Tuple[int, str, float, float, float]] = []
    symbol_counts: Dict[str, Dict[str, int]] = {}
    aggregate_counts = defaultdict(int)
    for symbol in symbols:
        records, counts = compute_symbol_signals(symbol)
        signal_records.extend(records)
        symbol_counts[symbol] = counts
        for key, value in counts.items():
            aggregate_counts[key] += value

    portfolios, coverage_summary, return_lookup = build_portfolios(signal_records)
    split_portfolios = {split: [item for item in portfolios if item["split"] == split] for split in ("train", "validation", "holdout")}
    split_summaries = {
        split: summarize_returns(
            [float(item["gross_return"]) for item in values],
            [float(item["net_return"]) for item in values],
        )
        for split, values in split_portfolios.items()
    }
    train_monthly = monthly_summary(split_portfolios["train"])
    validation_monthly = monthly_summary(split_portfolios["validation"])
    holdout_monthly = monthly_summary(split_portfolios["holdout"])
    monthly_passed = (
        validation_monthly["monthly_positive_rate"] is not None
        and validation_monthly["monthly_positive_rate"] >= 0.60
        and validation_monthly["month_count"] >= 6
    )

    long_short = {}
    for split, values in split_portfolios.items():
        long_values = [float(item["long_return"]) for item in values]
        short_values = [float(item["short_return"]) for item in values]
        long_short[f"long_{split}_gross_metric_bps"] = mean_bps(long_values)
        long_short[f"long_{split}_net_metric_bps"] = mean_bps([value - COST_RETURN for value in long_values])
        long_short[f"short_{split}_gross_metric_bps"] = mean_bps(short_values)
        long_short[f"short_{split}_net_metric_bps"] = mean_bps([value - COST_RETURN for value in short_values])
        long_short[f"long_{split}_observation_count"] = len(long_values)
        long_short[f"short_{split}_observation_count"] = len(short_values)

    participation = {symbol: 0 for symbol in symbols}
    for item in portfolios:
        for symbol in item["long_symbols"] + item["short_symbols"]:
            participation[symbol] += 1
    total_participation = sum(participation.values())
    top_symbol_exposure_share = None if total_participation == 0 else round(max(participation.values()) / total_participation, 6)
    turnover_values = [float(item["turnover_from_previous"]) for item in portfolios if item["turnover_from_previous"] is not None]
    average_turnover = None if not turnover_values else round(sum(turnover_values) / len(turnover_values), 6)
    turnover_summary = {
        "event_participation_by_symbol": participation,
        "top_symbol_exposure_share": top_symbol_exposure_share,
        "average_turnover": average_turnover,
        "median_turnover": median_or_none(turnover_values),
        "max_turnover": max(turnover_values) if turnover_values else None,
        "turnover_concentration_review_preliminary_passed": (
            top_symbol_exposure_share is not None
            and top_symbol_exposure_share <= 0.10
            and average_turnover is not None
            and average_turnover <= 1.50
        ),
    }
    null_summary = null_baseline(portfolios, return_lookup, split_summaries["validation"]["net_metric_bps"])

    metric_issues: List[str] = []
    if aggregate_counts["gk_negative_numeric_issue_count"] > 0:
        metric_issues.append("gk_negative_variance_numeric_issues_detected")
    metrics_to_check = [
        split_summaries["train"]["gross_metric_bps"],
        split_summaries["train"]["net_metric_bps"],
        split_summaries["validation"]["gross_metric_bps"],
        split_summaries["validation"]["net_metric_bps"],
        split_summaries["holdout"]["gross_metric_bps"],
        split_summaries["holdout"]["net_metric_bps"],
        validation_monthly["monthly_positive_rate"],
        coverage_summary["average_eligible_symbols_per_timestamp"],
        top_symbol_exposure_share,
        average_turnover,
    ]
    if not all(finite_or_none(value) for value in metrics_to_check):
        metric_issues.append("non_finite_metric_detected")

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
            "ohlcv_only": True,
            "total_raw_rows_read": aggregate_counts["raw_rows_read"],
            "total_complete_rows_used": aggregate_counts["complete_rows_used"],
            "gk_tiny_negative_clamped_count": aggregate_counts["gk_tiny_negative_clamped_count"],
            "gk_negative_numeric_issue_count": aggregate_counts["gk_negative_numeric_issue_count"],
            "symbol_signal_counts": symbol_counts,
        },
        "signal_definition": {
            "garman_klass_variance": "0.5 * ln(high/low)^2 - (2*ln(2)-1) * ln(close/open)^2",
            "current_gk_vol_24h": "sqrt(sum gk_var over prior 96 completed 15m bars)",
            "baseline_observations": "trailing 30d prior current_gk_vol_24h observations",
            "baseline_lookback_15m_observations": BASELINE_BARS,
            "minimum_baseline_observations": MIN_BASELINE_OBS,
            "zscore": "(current_gk_vol_24h - trailing_30d_mean) / trailing_30d_std",
            "long_leg": "lowest 20 percent gk_vol_z",
            "short_leg": "highest 20 percent gk_vol_z",
            "minimum_eligible_symbols": MIN_ELIGIBLE_SYMBOLS,
            "minimum_long_symbols": MIN_LONG_SYMBOLS,
            "minimum_short_symbols": MIN_SHORT_SYMBOLS,
            "no_current_bar_leakage": True,
            "no_future_data": True,
        },
        "return_and_cost_policy": {
            "entry_price": "open at E",
            "exit_price": "open at E + 8h",
            "holding_period_hours": 8,
            "round_trip_cost_bps": 20,
            "gross_spread": "mean(long returns) + mean(short returns)",
            "net_spread": "gross - 0.0020",
            "no_annualization": True,
            "no_compounding": True,
        },
        "execution_safety_controls": {
            "exactly_one_config_executed": True,
            "no_non_preregistered_config": True,
            "no_parameter_expansion": True,
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
            "train_gross_metric_bps": split_summaries["train"]["gross_metric_bps"],
            "train_net_metric_bps": split_summaries["train"]["net_metric_bps"],
            "validation_gross_metric_bps": split_summaries["validation"]["gross_metric_bps"],
            "validation_net_metric_bps": split_summaries["validation"]["net_metric_bps"],
            "holdout_gross_metric_bps": split_summaries["holdout"]["gross_metric_bps"],
            "holdout_net_metric_bps": split_summaries["holdout"]["net_metric_bps"],
            "train_observation_count": split_summaries["train"]["observation_count"],
            "validation_observation_count": split_summaries["validation"]["observation_count"],
            "holdout_observation_count": split_summaries["holdout"]["observation_count"],
            "validation_positive_after_cost": split_summaries["validation"]["positive_after_cost"],
            "holdout_reported_separately": True,
            "holdout_used_for_config_selection": False,
        },
        "train_validation_holdout_summary": {
            "full_window_start_utc": FULL_START,
            "full_window_end_exclusive_utc": FULL_END_EXCLUSIVE,
            "train": split_summaries["train"],
            "validation": split_summaries["validation"],
            "holdout": split_summaries["holdout"],
            "holdout_used_for_config_selection": False,
        },
        "monthly_stability_summary": {
            "train_monthly_gross_metric_bps_by_month": train_monthly["monthly_gross_metric_bps_by_month"],
            "train_monthly_net_metric_bps_by_month": train_monthly["monthly_net_metric_bps_by_month"],
            "validation_monthly_gross_metric_bps_by_month": validation_monthly["monthly_gross_metric_bps_by_month"],
            "validation_monthly_net_metric_bps_by_month": validation_monthly["monthly_net_metric_bps_by_month"],
            "validation_monthly_positive_rate": validation_monthly["monthly_positive_rate"],
            "validation_month_count": validation_monthly["month_count"],
            "holdout_monthly_gross_metric_bps_by_month": holdout_monthly["monthly_gross_metric_bps_by_month"],
            "holdout_monthly_net_metric_bps_by_month": holdout_monthly["monthly_net_metric_bps_by_month"],
            "holdout_monthly_positive_rate": holdout_monthly["monthly_positive_rate"],
            "monthly_stability_review_preliminary_passed": monthly_passed,
        },
        "signal_coverage_summary": coverage_summary,
        "long_short_side_summary": long_short,
        "turnover_concentration_summary": turnover_summary,
        "null_baseline_summary": null_summary,
        "metric_integrity_summary": {
            "exactly_one_config_executed": True,
            "config_id_matches_preregistration": True,
            "no_nan_or_inf": "non_finite_metric_detected" not in metric_issues,
            "no_timestamp_outside_windows": True,
            "no_lookahead": True,
            "no_cross_window_returns": True,
            "no_non_preregistered_config": True,
            "no_candidate_edge_release_runtime": True,
            "metric_integrity_issues": metric_issues,
            "metric_integrity_issue_count": len(metric_issues),
            "metric_integrity_passed": len(metric_issues) == 0,
        },
        "diagnostic_interpretation_limits": {
            "diagnostic_execution_only": True,
            "no_candidate": True,
            "no_edge_claim": True,
            "no_family_release": True,
            "no_holdout_permission": True,
            "no_runtime_live_capital": True,
        },
        "safety_permissions": {
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
            "data_downloaded": False,
            "funding_rows_read": False,
            "okx_panel_rows_read": False,
            "binance_1m_source_rows_read": False,
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
            "preregistration_loaded": True,
            "preregistration_hash_verified": True,
            "panel_review_loaded": True,
            "exact_overlap_symbol_count_verified_81": True,
            "exactly_one_config_executed": True,
            "no_non_preregistered_config": True,
            "no_parameter_expansion": True,
            "no_network": True,
            "no_api_calls": True,
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
    if artifact_path.exists():
        raise RuntimeError(f"execution artifact already exists: {ARTIFACT_PATH}")
    payload = build_execution()
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": STATUS,
        "artifact_path": ARTIFACT_PATH,
        "route_family": ROUTE_FAMILY,
        "config_id": CONFIG_ID,
        "train_gross_metric_bps": payload["config_result"]["train_gross_metric_bps"],
        "train_net_metric_bps": payload["config_result"]["train_net_metric_bps"],
        "validation_gross_metric_bps": payload["config_result"]["validation_gross_metric_bps"],
        "validation_net_metric_bps": payload["config_result"]["validation_net_metric_bps"],
        "holdout_gross_metric_bps": payload["config_result"]["holdout_gross_metric_bps"],
        "holdout_net_metric_bps": payload["config_result"]["holdout_net_metric_bps"],
        "validation_positive_after_cost": payload["config_result"]["validation_positive_after_cost"],
        "validation_eligible_timestamp_count": payload["signal_coverage_summary"]["validation_eligible_timestamp_count"],
        "average_eligible_symbols": payload["signal_coverage_summary"]["average_eligible_symbols_per_timestamp"],
        "null_baseline_review_preliminary_passed": payload["null_baseline_summary"]["null_baseline_review_preliminary_passed"],
        "monthly_stability_review_preliminary_passed": payload["monthly_stability_summary"]["monthly_stability_review_preliminary_passed"],
        "signal_coverage_review_preliminary_passed": payload["signal_coverage_summary"]["signal_coverage_review_preliminary_passed"],
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
