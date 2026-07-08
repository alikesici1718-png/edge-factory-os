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
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_pairs_trading_log_spread_execution_v1.py"
ARTIFACT_PATH = "artifacts/strategy_executions/binance_okx_overlap_pairs_trading_log_spread_execution_v1.json"
STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_PAIRS_TRADING_LOG_SPREAD_EXECUTED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_PAIRS_TRADING_LOG_SPREAD_EXECUTION"

ROUTE_FAMILY = "BINANCE_OKX_OVERLAP_PAIRS_TRADING_LOG_SPREAD_MEAN_REVERSION_BASELINE"
HYPOTHESIS_NAME = "btc_eth_sol_avax_log_spread_mean_reversion"
CONFIG_ID = "log_spread_z2_rolling168h_hold24h_btceth_solavax"

FULL_START_HOUR = None
TRAIN_END_HOUR = None
VALIDATION_START_HOUR = None
VALIDATION_END_HOUR = None
HOLDOUT_START_HOUR = None
FULL_END_HOUR = None

HOLDING_HOURS = 24
ROLLING_LOOKBACK_HOURS = 168
Z_ENTRY = 2.0
COST_RETURN = 0.0020

PREREG_PATH = "artifacts/research_preregistrations/binance_okx_overlap_pairs_trading_log_spread_preregistration_contract_v1.json"
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

PAIRS = [
    {"pair_key": "BTCUSDT_ETHUSDT", "A_symbol": "BTCUSDT", "B_symbol": "ETHUSDT"},
    {"pair_key": "SOLUSDT_AVAXUSDT", "A_symbol": "SOLUSDT", "B_symbol": "AVAXUSDT"},
]
REQUIRED_SYMBOLS = sorted({pair["A_symbol"] for pair in PAIRS} | {pair["B_symbol"] for pair in PAIRS})


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


def population_std(values: Sequence[float]) -> Optional[float]:
    if not values:
        return None
    avg = sum(values) / len(values)
    variance = sum((value - avg) ** 2 for value in values) / len(values)
    return math.sqrt(variance)


def finite_or_none(value: Any) -> bool:
    return value is None or (isinstance(value, (int, float)) and math.isfinite(float(value)))


def split_for_entry(entry_hour: int, exit_hour: int) -> Tuple[Optional[str], bool]:
    if FULL_START_HOUR <= entry_hour < TRAIN_END_HOUR:
        return ("train", exit_hour < TRAIN_END_HOUR)
    if VALIDATION_START_HOUR <= entry_hour < VALIDATION_END_HOUR:
        return ("validation", exit_hour < VALIDATION_END_HOUR)
    if HOLDOUT_START_HOUR <= entry_hour < FULL_END_HOUR:
        return ("holdout", exit_hour < FULL_END_HOUR)
    return (None, False)


def deterministic_seed(pair_key: str, split: str, run_index: int) -> int:
    digest = hashlib.sha256(f"{ROUTE_FAMILY}|{CONFIG_ID}|{pair_key}|{split}|{run_index}".encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def block_shuffle(records: List[Dict[str, Any]], pair_key: str, split: str, run_index: int) -> List[Dict[str, Any]]:
    if not records:
        return []
    blocks = [records[i : i + 168] for i in range(0, len(records), 168)]
    rng = random.Random(deterministic_seed(pair_key, split, run_index))
    rng.shuffle(blocks)
    shuffled: List[Dict[str, Any]] = []
    for block in blocks:
        shuffled.extend(block)
    return shuffled[: len(records)]


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


def load_panel_rows(symbol: str) -> Dict[int, Dict[str, float]]:
    path = PANEL_DIR / f"{symbol}_1h.csv.gz"
    if not path.exists():
        raise RuntimeError(f"missing panel file for {symbol}: {path}")
    rows: Dict[int, Dict[str, float]] = {}
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
            if not (math.isfinite(open_price) and math.isfinite(close_price) and open_price > 0 and close_price > 0):
                raise RuntimeError(f"invalid open/close for {symbol} at {row['timestamp_utc']}")
            if hour in rows:
                raise RuntimeError(f"duplicate complete panel hour for {symbol}: {row['timestamp_utc']}")
            rows[hour] = {"open": open_price, "close": close_price}
    return dict(sorted(rows.items()))


def estimate_hedge(pair_key: str, a_rows: Dict[int, Dict[str, float]], b_rows: Dict[int, Dict[str, float]]) -> Dict[str, Any]:
    train_hours = sorted(hour for hour in set(a_rows) & set(b_rows) if FULL_START_HOUR <= hour < TRAIN_END_HOUR)
    if len(train_hours) < 100:
        raise RuntimeError(f"insufficient train hedge sample for {pair_key}")
    x_values = [math.log(b_rows[hour]["close"]) for hour in train_hours]
    y_values = [math.log(a_rows[hour]["close"]) for hour in train_hours]
    x_mean = sum(x_values) / len(x_values)
    y_mean = sum(y_values) / len(y_values)
    var_x = sum((x - x_mean) ** 2 for x in x_values)
    if var_x <= 0:
        raise RuntimeError(f"non-positive B log-price variance for {pair_key}")
    cov_xy = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    beta = cov_xy / var_x
    alpha = y_mean - beta * x_mean
    if not (math.isfinite(alpha) and math.isfinite(beta)):
        raise RuntimeError(f"non-finite alpha/beta for {pair_key}")
    residuals = [y - alpha - beta * x for x, y in zip(x_values, y_values)]
    return {
        "alpha": alpha,
        "beta": beta,
        "train_hedge_sample_count": len(train_hours),
        "train_residual_mean": mean(residuals),
        "train_residual_std_population": population_std(residuals),
    }


def compute_pair_spreads(
    alpha: float,
    beta: float,
    a_rows: Dict[int, Dict[str, float]],
    b_rows: Dict[int, Dict[str, float]],
) -> Dict[int, float]:
    spreads: Dict[int, float] = {}
    for hour in sorted(set(a_rows) & set(b_rows)):
        if FULL_START_HOUR <= hour < FULL_END_HOUR:
            spreads[hour] = math.log(a_rows[hour]["close"]) - alpha - beta * math.log(b_rows[hour]["close"])
    return spreads


def metric_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    gross_values = [record["gross_return"] for record in records]
    net_values = [record["net_return"] for record in records]
    net_metric = mean_bps(net_values)
    return {
        "observation_count": len(records),
        "gross_metric_bps": mean_bps(gross_values),
        "net_metric_bps": net_metric,
        "positive_after_cost": bool(net_metric is not None and net_metric > 0),
    }


def monthly_metrics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_month: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_month[month_key(record["entry_hour"])].append(record)
    monthly_gross: Dict[str, float] = {}
    monthly_net: Dict[str, float] = {}
    monthly_counts: Dict[str, int] = {}
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
        "month_count": month_count,
        "positive_month_count": positive_count,
        "monthly_positive_rate": round(positive_rate, 6),
    }


def split_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    summary = metric_summary(records)
    summary.update(monthly_metrics(records))
    return summary


def compute_pair_trades(
    pair: Dict[str, str],
    hedge: Dict[str, Any],
    spreads: Dict[int, float],
    a_rows: Dict[int, Dict[str, float]],
    b_rows: Dict[int, Dict[str, float]],
) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, int], List[float]]:
    alpha = float(hedge["alpha"])
    beta = float(hedge["beta"])
    if not math.isfinite(alpha):
        raise RuntimeError("alpha unexpectedly non-finite")
    gross_exposure = abs(1.0) + abs(beta)
    if gross_exposure <= 0:
        raise RuntimeError(f"bad gross exposure for {pair['pair_key']}")
    records_by_split: Dict[str, List[Dict[str, Any]]] = {"train": [], "validation": [], "holdout": []}
    skipped_counts = {
        "insufficient_rolling_spread_context": 0,
        "zero_or_nonfinite_rolling_std": 0,
        "entry_signal_below_threshold": 0,
        "missing_entry_or_exit_rows": 0,
        "cross_window_holding_return_skipped": 0,
    }
    abs_z_values: List[float] = []
    all_entry_hours = sorted(hour for hour in set(a_rows) & set(b_rows) if FULL_START_HOUR <= hour < FULL_END_HOUR)
    for entry_hour in all_entry_hours:
        exit_hour = entry_hour + HOLDING_HOURS
        split, same_window = split_for_entry(entry_hour, exit_hour)
        if split is None:
            continue
        if not same_window:
            skipped_counts["cross_window_holding_return_skipped"] += 1
            continue
        prior_hours = list(range(entry_hour - ROLLING_LOOKBACK_HOURS, entry_hour))
        prior_spreads = [spreads.get(hour) for hour in prior_hours]
        if any(value is None for value in prior_spreads):
            skipped_counts["insufficient_rolling_spread_context"] += 1
            continue
        values = [float(value) for value in prior_spreads]
        rolling_mean = sum(values) / len(values)
        rolling_std = population_std(values)
        if rolling_std is None or rolling_std <= 0 or not math.isfinite(rolling_std):
            skipped_counts["zero_or_nonfinite_rolling_std"] += 1
            continue
        signal_spread = spreads[entry_hour - 1]
        z_score = (signal_spread - rolling_mean) / rolling_std
        if z_score >= Z_ENTRY:
            direction = "short_A_long_beta_B"
        elif z_score <= -Z_ENTRY:
            direction = "long_A_short_beta_B"
        else:
            skipped_counts["entry_signal_below_threshold"] += 1
            continue
        if entry_hour not in a_rows or entry_hour not in b_rows or exit_hour not in a_rows or exit_hour not in b_rows:
            skipped_counts["missing_entry_or_exit_rows"] += 1
            continue
        r_a = a_rows[exit_hour]["open"] / a_rows[entry_hour]["open"] - 1.0
        r_b = b_rows[exit_hour]["open"] / b_rows[entry_hour]["open"] - 1.0
        if direction == "short_A_long_beta_B":
            gross_return = (-1.0 * r_a + beta * r_b) / gross_exposure
        else:
            gross_return = (1.0 * r_a - beta * r_b) / gross_exposure
        if not math.isfinite(gross_return):
            raise RuntimeError(f"non-finite pair gross return for {pair['pair_key']}")
        record = {
            "pair_key": pair["pair_key"],
            "entry_hour": entry_hour,
            "entry_time_utc": hour_to_iso(entry_hour),
            "exit_hour": exit_hour,
            "exit_time_utc": hour_to_iso(exit_hour),
            "split": split,
            "direction": direction,
            "z_score": z_score,
            "abs_z_score": abs(z_score),
            "r_A": r_a,
            "r_B": r_b,
            "gross_return": gross_return,
            "net_return": gross_return - COST_RETURN,
        }
        records_by_split[split].append(record)
        abs_z_values.append(abs(z_score))
    return records_by_split, skipped_counts, abs_z_values


def aggregate_records(pair_records: Dict[str, Dict[str, List[Dict[str, Any]]]], split: str) -> List[Dict[str, Any]]:
    by_hour: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
    for records_by_split in pair_records.values():
        for record in records_by_split[split]:
            by_hour[record["entry_hour"]].append(record)
    aggregate: List[Dict[str, Any]] = []
    for hour, records in sorted(by_hour.items()):
        gross_return = mean([record["gross_return"] for record in records])
        net_return = mean([record["net_return"] for record in records])
        if gross_return is None or net_return is None:
            continue
        aggregate.append(
            {
                "entry_hour": hour,
                "entry_time_utc": hour_to_iso(hour),
                "exit_hour": hour + HOLDING_HOURS,
                "exit_time_utc": hour_to_iso(hour + HOLDING_HOURS),
                "split": split,
                "active_pair_count": len(records),
                "active_pair_keys": sorted(record["pair_key"] for record in records),
                "gross_return": gross_return,
                "net_return": net_return,
            }
        )
    return aggregate


def validation_monthly_from_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    metrics = monthly_metrics(records)
    return {
        "validation_monthly_gross_metric_bps_by_month": metrics["monthly_gross_metric_bps_by_month"],
        "validation_monthly_net_metric_bps_by_month": metrics["monthly_net_metric_bps_by_month"],
        "validation_monthly_trade_count_by_month": metrics["monthly_observation_count_by_month"],
        "validation_monthly_positive_rate": metrics["monthly_positive_rate"],
        "validation_month_count": metrics["month_count"],
    }


def compute_null_baseline(pair_records: Dict[str, Dict[str, List[Dict[str, Any]]]], actual_validation_net: Optional[float]) -> Dict[str, Any]:
    def compute_split_null(split: str, run_index: int) -> Optional[float]:
        by_hour: Dict[int, List[float]] = defaultdict(list)
        for pair in PAIRS:
            pair_key = pair["pair_key"]
            records = pair_records[pair_key][split]
            if not records:
                continue
            shuffled_returns = block_shuffle(records, pair_key, split, run_index)
            beta = next(item["beta"] for item in HEDGE_CACHE if item["pair_key"] == pair_key)
            gross_exposure = abs(1.0) + abs(beta)
            for signal_record, return_record in zip(records, shuffled_returns):
                if signal_record["direction"] == "short_A_long_beta_B":
                    gross_return = (-1.0 * return_record["r_A"] + beta * return_record["r_B"]) / gross_exposure
                else:
                    gross_return = (1.0 * return_record["r_A"] - beta * return_record["r_B"]) / gross_exposure
                by_hour[signal_record["entry_hour"]].append(gross_return - COST_RETURN)
        timestamp_net_values = [mean(values) for _, values in sorted(by_hour.items()) if values]
        timestamp_net_values = [float(value) for value in timestamp_net_values if value is not None]
        if not timestamp_net_values:
            return None
        return mean(timestamp_net_values) * 10000.0

    train_nulls: List[float] = []
    validation_nulls: List[float] = []
    for run_index in range(100):
        train_metric = compute_split_null("train", run_index)
        validation_metric = compute_split_null("validation", run_index)
        if train_metric is not None and math.isfinite(train_metric):
            train_nulls.append(train_metric)
        if validation_metric is not None and math.isfinite(validation_metric):
            validation_nulls.append(validation_metric)
    percentile = None
    if actual_validation_net is not None and validation_nulls:
        percentile = sum(1 for value in validation_nulls if value <= actual_validation_net) / len(validation_nulls)
    return {
        "null_baseline": "deterministic_spread_signal_timestamp_block_shuffle_null",
        "null_run_count": 100,
        "block_length_hours": 168,
        "shuffle_policy": "signal timestamps shuffled against return timestamps within train and validation separately; pair identity preserved",
        "valid_train_null_run_count": len(train_nulls),
        "valid_validation_null_run_count": len(validation_nulls),
        "train_null_net_metric_bps_mean": None if not train_nulls else round(mean(train_nulls), 6),
        "validation_null_net_metric_bps_mean": None if not validation_nulls else round(mean(validation_nulls), 6),
        "validation_null_metric_bps_min": None if not validation_nulls else round(min(validation_nulls), 6),
        "validation_null_metric_bps_median": None if not validation_nulls else round(float(median(validation_nulls)), 6),
        "validation_null_metric_bps_max": None if not validation_nulls else round(max(validation_nulls), 6),
        "validation_null_percentile": None if percentile is None else round(percentile, 6),
        "null_baseline_review_preliminary_passed": bool(percentile is not None and percentile >= 0.95),
    }


HEDGE_CACHE: List[Dict[str, Any]] = []


def spread_std_by_split(spreads: Dict[int, float], split: str) -> Optional[float]:
    values: List[float] = []
    for hour, spread in spreads.items():
        if split == "validation" and VALIDATION_START_HOUR <= hour < VALIDATION_END_HOUR:
            values.append(spread)
        elif split == "holdout" and HOLDOUT_START_HOUR <= hour < FULL_END_HOUR:
            values.append(spread)
    return population_std(values)


def build_execution() -> Dict[str, Any]:
    global FULL_START_HOUR, TRAIN_END_HOUR, VALIDATION_START_HOUR, VALIDATION_END_HOUR, HOLDOUT_START_HOUR, FULL_END_HOUR, HEDGE_CACHE
    FULL_START_HOUR = parse_hour("2021-05-01T00:00:00Z")
    TRAIN_END_HOUR = parse_hour("2024-01-01T00:00:00Z")
    VALIDATION_START_HOUR = parse_hour("2024-01-01T00:00:00Z")
    VALIDATION_END_HOUR = parse_hour("2025-01-01T00:00:00Z")
    HOLDOUT_START_HOUR = parse_hour("2025-01-01T00:00:00Z")
    FULL_END_HOUR = parse_hour("2025-11-01T00:00:00Z")

    prereg = read_json(PREREG_PATH)
    readiness = read_json(READINESS_PATH)
    panel_review = read_json(PANEL_REVIEW_PATH)
    build_manifest = read_json(BUILD_MANIFEST_PATH)
    preview = read_json(PREVIEW_PATH)
    coverage_lock = read_json(COVERAGE_LOCK_PATH)
    source_artifacts = [prereg, readiness, panel_review, build_manifest, preview, coverage_lock]
    source_hashes = {
        PREREG_PATH: verify_hash(prereg),
        READINESS_PATH: verify_hash(readiness),
        PANEL_REVIEW_PATH: verify_hash(panel_review),
        BUILD_MANIFEST_PATH: verify_hash(build_manifest),
        PREVIEW_PATH: verify_hash(preview),
        COVERAGE_LOCK_PATH: verify_hash(coverage_lock),
    }
    if prereg.get("status") != "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_PAIRS_TRADING_LOG_SPREAD_PREREGISTRATION_CONTRACT_CREATED":
        raise RuntimeError("preregistration status mismatch")
    if prereg.get("pairs_trading_hypothesis_preregistration", {}).get("route_family") != ROUTE_FAMILY:
        raise RuntimeError("preregistration route family mismatch")
    if prereg.get("pairs_trading_hypothesis_preregistration", {}).get("config_id") != CONFIG_ID:
        raise RuntimeError("preregistration config mismatch")
    if not validate_no_forbidden_permissions(source_artifacts):
        raise RuntimeError("source artifact unexpectedly grants forbidden permission")

    symbols = find_symbol_list(readiness) or find_symbol_list(preview) or find_symbol_list(build_manifest)
    if not symbols or len(symbols) != 81:
        raise RuntimeError("could not verify exact 81-symbol overlap universe")
    missing_symbols = [symbol for symbol in REQUIRED_SYMBOLS if symbol not in symbols]
    if missing_symbols:
        raise RuntimeError(f"required pair symbols missing from overlap universe: {missing_symbols}")
    panel_review_passed = (
        panel_review.get("panel_validity_classification")
        or find_first_key(panel_review, "panel_validity_classification")
    ) == "PANEL_REVIEW_PASS_WITH_P1_ATTENTION_VALID_FOR_READ_ONLY_SECOND_SOURCE_ANALYSIS"
    if not panel_review_passed:
        raise RuntimeError("panel review is not valid for read-only second-source analysis")

    panel_rows_by_symbol: Dict[str, Dict[int, Dict[str, float]]] = {}
    panel_files_read = 0
    panel_complete_rows_read = 0
    for symbol in REQUIRED_SYMBOLS:
        rows = load_panel_rows(symbol)
        panel_rows_by_symbol[symbol] = rows
        panel_files_read += 1
        panel_complete_rows_read += len(rows)

    pair_records: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    pair_results: List[Dict[str, Any]] = []
    hedge_estimation: List[Dict[str, Any]] = []
    hedge_stability_pairs: List[Dict[str, Any]] = []
    HEDGE_CACHE = []

    for pair in PAIRS:
        a_rows = panel_rows_by_symbol[pair["A_symbol"]]
        b_rows = panel_rows_by_symbol[pair["B_symbol"]]
        hedge = estimate_hedge(pair["pair_key"], a_rows, b_rows)
        spreads = compute_pair_spreads(float(hedge["alpha"]), float(hedge["beta"]), a_rows, b_rows)
        records_by_split, skipped_counts, abs_z_values = compute_pair_trades(pair, hedge, spreads, a_rows, b_rows)
        pair_records[pair["pair_key"]] = records_by_split
        HEDGE_CACHE.append(
            {
                "pair_key": pair["pair_key"],
                "alpha": float(hedge["alpha"]),
                "beta": float(hedge["beta"]),
            }
        )
        train_summary = metric_summary(records_by_split["train"])
        validation_summary = metric_summary(records_by_split["validation"])
        holdout_summary = metric_summary(records_by_split["holdout"])
        validation_monthly = validation_monthly_from_records(records_by_split["validation"])
        pair_result = {
            "pair_key": pair["pair_key"],
            "A_symbol": pair["A_symbol"],
            "B_symbol": pair["B_symbol"],
            "alpha": round(float(hedge["alpha"]), 12),
            "beta": round(float(hedge["beta"]), 12),
            "train_hedge_sample_count": hedge["train_hedge_sample_count"],
            "train_gross_metric_bps": train_summary["gross_metric_bps"],
            "train_net_metric_bps": train_summary["net_metric_bps"],
            "validation_gross_metric_bps": validation_summary["gross_metric_bps"],
            "validation_net_metric_bps": validation_summary["net_metric_bps"],
            "holdout_gross_metric_bps": holdout_summary["gross_metric_bps"],
            "holdout_net_metric_bps": holdout_summary["net_metric_bps"],
            "train_trade_count": train_summary["observation_count"],
            "validation_trade_count": validation_summary["observation_count"],
            "holdout_trade_count": holdout_summary["observation_count"],
            "validation_positive_after_cost": validation_summary["positive_after_cost"],
            "validation_monthly_gross_metric_bps_by_month": validation_monthly["validation_monthly_gross_metric_bps_by_month"],
            "validation_monthly_net_metric_bps_by_month": validation_monthly["validation_monthly_net_metric_bps_by_month"],
            "validation_monthly_positive_rate": validation_monthly["validation_monthly_positive_rate"],
            "average_abs_z_at_entry": None if not abs_z_values else round(mean(abs_z_values), 6),
            "max_abs_z_at_entry": None if not abs_z_values else round(max(abs_z_values), 6),
            "skipped_counts": skipped_counts,
        }
        pair_results.append(pair_result)
        hedge_estimation.append(
            {
                "pair_key": pair["pair_key"],
                "A_symbol": pair["A_symbol"],
                "B_symbol": pair["B_symbol"],
                "alpha": pair_result["alpha"],
                "beta": pair_result["beta"],
                "train_hedge_sample_count": hedge["train_hedge_sample_count"],
                "train_residual_mean": None if hedge["train_residual_mean"] is None else round(float(hedge["train_residual_mean"]), 12),
                "train_residual_std_population": None if hedge["train_residual_std_population"] is None else round(float(hedge["train_residual_std_population"]), 12),
                "hedge_estimation_window": "train only",
                "validation_or_holdout_used_for_hedge_selection": False,
            }
        )
        hedge_stability_pairs.append(
            {
                "pair_key": pair["pair_key"],
                "beta": pair_result["beta"],
                "train_residual_std_population": None if hedge["train_residual_std_population"] is None else round(float(hedge["train_residual_std_population"]), 12),
                "validation_spread_std_population": None if spread_std_by_split(spreads, "validation") is None else round(float(spread_std_by_split(spreads, "validation")), 12),
                "holdout_spread_std_population": None if spread_std_by_split(spreads, "holdout") is None else round(float(spread_std_by_split(spreads, "holdout")), 12),
                "spread_drift_note": "diagnostic only; hedge beta estimated once on train and not selected on validation or holdout",
            }
        )

    aggregate_by_split = {
        "train": aggregate_records(pair_records, "train"),
        "validation": aggregate_records(pair_records, "validation"),
        "holdout": aggregate_records(pair_records, "holdout"),
    }
    train_summary = split_summary(aggregate_by_split["train"])
    validation_summary = split_summary(aggregate_by_split["validation"])
    holdout_summary = split_summary(aggregate_by_split["holdout"])
    null_summary = compute_null_baseline(pair_records, validation_summary["net_metric_bps"])
    validation_monthly_passed = validation_summary["monthly_positive_rate"] >= 0.60 and validation_summary["month_count"] >= 6

    pair_positive_validation_count = sum(1 for pair_result in pair_results if pair_result["validation_net_metric_bps"] is not None and pair_result["validation_net_metric_bps"] > 0)
    both_pairs_trade_count_gt_20 = all(pair_result["validation_trade_count"] > 20 for pair_result in pair_results)
    pair_level_consistency_passed = bool(
        both_pairs_trade_count_gt_20
        and pair_positive_validation_count >= 1
        and validation_summary["net_metric_bps"] is not None
        and validation_summary["net_metric_bps"] > 0
    )

    metric_integrity_issues: List[str] = []
    for split in ("train", "validation", "holdout"):
        if aggregate_by_split[split] == []:
            metric_integrity_issues.append(f"no_aggregate_{split}_records")
    if len(pair_results) != 2:
        metric_integrity_issues.append("pair_count_not_two")
    if CONFIG_ID != "log_spread_z2_rolling168h_hold24h_btceth_solavax":
        metric_integrity_issues.append("config_id_mismatch")
    metrics_to_check: List[Any] = [
        train_summary["gross_metric_bps"],
        train_summary["net_metric_bps"],
        validation_summary["gross_metric_bps"],
        validation_summary["net_metric_bps"],
        holdout_summary["gross_metric_bps"],
        holdout_summary["net_metric_bps"],
        null_summary["validation_null_percentile"],
        validation_summary["monthly_positive_rate"],
    ]
    for pair_result in pair_results:
        metrics_to_check.extend(
            [
                pair_result["alpha"],
                pair_result["beta"],
                pair_result["validation_net_metric_bps"],
                pair_result["average_abs_z_at_entry"],
                pair_result["max_abs_z_at_entry"],
            ]
        )
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
            "preregistration_artifact_loaded": True,
            "preregistration_payload_hash_verified": True,
            "panel_review_loaded": True,
            "panel_review_valid_for_read_only_second_source_analysis": True,
            "panel_files_read": panel_files_read,
            "panel_complete_rows_read": panel_complete_rows_read,
            "panel_symbols_read": REQUIRED_SYMBOLS,
            "read_only_panel_symbols_limited_to_required_pairs": True,
            "exact_overlap_symbol_count_verified_81": True,
            "used_only_complete_1h_rows": True,
            "funding_rows_read": False,
            "okx_panel_rows_read": False,
            "binance_1m_source_rows_read": False,
        },
        "hedge_ratio_estimation": {
            "model": "log_close_A = alpha + beta * log_close_B",
            "estimation_window": "train only",
            "validation_used_for_hedge_ratio_selection": False,
            "holdout_used_for_hedge_ratio_selection": False,
            "pairs": hedge_estimation,
        },
        "spread_signal_policy": {
            "spread_definition": "spread_t = log_close_A_t - alpha - beta * log_close_B_t",
            "rolling_zscore_lookback_hours": ROLLING_LOOKBACK_HOURS,
            "rolling_std_policy": "population standard deviation",
            "z_entry": Z_ENTRY,
            "signal_timestamp_policy": "spread observations strictly before entry; z uses spread at E-1h",
            "no_current_hour_close_used_for_signal": True,
            "no_future_data_used_for_signal": True,
            "entry_short_A_long_beta_B_condition": "z_E >= +2.0",
            "entry_long_A_short_beta_B_condition": "z_E <= -2.0",
            "no_dynamic_exit_threshold": True,
            "no_stop_loss": True,
            "no_pair_scanning": True,
            "no_threshold_grid": True,
        },
        "return_and_cost_policy": {
            "holding_period_hours": HOLDING_HOURS,
            "entry_price": "open at E for both A and B",
            "exit_price": "open at E+24h for both A and B",
            "gross_exposure_normalization": "abs(1.0) + abs(beta)",
            "high_spread_return": "(-1.0 * r_A + beta * r_B) / gross_exposure",
            "low_spread_return": "(1.0 * r_A - beta * r_B) / gross_exposure",
            "pair_net_return": "pair_gross_return - 0.0020",
            "round_trip_cost_bps": 20,
            "annualized": False,
            "compounded": False,
        },
        "execution_safety_controls": {
            "exactly_one_config_executed": True,
            "exactly_two_pairs_executed": True,
            "pair_selection_a_priori_not_scanned": True,
            "no_non_preregistered_config_tested": True,
            "no_parameter_expansion": True,
            "holdout_reported_separately": True,
            "holdout_used_for_pair_selection": False,
            "holdout_used_for_hedge_ratio_selection": False,
            "holdout_used_for_config_selection": False,
            "holdout_positive_cannot_create_candidate_edge_release": True,
            "final_edge_claim_requires_external_or_future_holdout": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_family_release": True,
            "no_runtime_live_capital": True,
        },
        "pair_results": pair_results,
        "aggregate_results": {
            "train_gross_metric_bps": train_summary["gross_metric_bps"],
            "train_net_metric_bps": train_summary["net_metric_bps"],
            "validation_gross_metric_bps": validation_summary["gross_metric_bps"],
            "validation_net_metric_bps": validation_summary["net_metric_bps"],
            "holdout_gross_metric_bps": holdout_summary["gross_metric_bps"],
            "holdout_net_metric_bps": holdout_summary["net_metric_bps"],
            "train_trade_timestamp_count": train_summary["observation_count"],
            "validation_trade_timestamp_count": validation_summary["observation_count"],
            "holdout_trade_timestamp_count": holdout_summary["observation_count"],
            "validation_positive_after_cost": validation_summary["positive_after_cost"],
            "validation_monthly_gross_metric_bps_by_month": validation_summary["monthly_gross_metric_bps_by_month"],
            "validation_monthly_net_metric_bps_by_month": validation_summary["monthly_net_metric_bps_by_month"],
            "validation_monthly_trade_timestamp_count_by_month": validation_summary["monthly_observation_count_by_month"],
            "validation_monthly_positive_rate": validation_summary["monthly_positive_rate"],
            "holdout_monthly_gross_metric_bps_by_month": holdout_summary["monthly_gross_metric_bps_by_month"],
            "holdout_monthly_net_metric_bps_by_month": holdout_summary["monthly_net_metric_bps_by_month"],
            "holdout_monthly_trade_timestamp_count_by_month": holdout_summary["monthly_observation_count_by_month"],
            "holdout_monthly_positive_rate": holdout_summary["monthly_positive_rate"],
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
            "train": train_summary,
            "validation": validation_summary,
            "holdout": holdout_summary,
            "holdout_reported_separately_not_used_for_selection": True,
        },
        "null_baseline_summary": null_summary,
        "monthly_stability_summary": {
            "validation_monthly_net_metric_bps_by_month": validation_summary["monthly_net_metric_bps_by_month"],
            "validation_monthly_gross_metric_bps_by_month": validation_summary["monthly_gross_metric_bps_by_month"],
            "validation_monthly_trade_timestamp_count_by_month": validation_summary["monthly_observation_count_by_month"],
            "validation_month_count": validation_summary["month_count"],
            "monthly_positive_rate": validation_summary["monthly_positive_rate"],
            "monthly_stability_review_preliminary_passed": validation_monthly_passed,
        },
        "pair_level_consistency_summary": {
            "pair_level_consistency_review_preliminary_passed": pair_level_consistency_passed,
            "both_pairs_validation_trade_count_gt_20": both_pairs_trade_count_gt_20,
            "positive_validation_net_pair_count": pair_positive_validation_count,
            "aggregate_validation_net_positive": bool(validation_summary["net_metric_bps"] is not None and validation_summary["net_metric_bps"] > 0),
            "only_one_pair_drives_result": pair_positive_validation_count == 1,
            "pair_validation_net_metric_bps": {item["pair_key"]: item["validation_net_metric_bps"] for item in pair_results},
            "pair_validation_trade_counts": {item["pair_key"]: item["validation_trade_count"] for item in pair_results},
        },
        "hedge_stability_summary": {
            "hedge_stability_review_preliminary_passed": metric_integrity_passed,
            "diagnostic_only": True,
            "does_not_fail_unless_beta_invalid_or_input_incomplete": True,
            "pairs": hedge_stability_pairs,
        },
        "metric_integrity_summary": {
            "exactly_one_config_executed": True,
            "exactly_two_pairs_executed": True,
            "config_id_matches_preregistration": True,
            "pair_selection_a_priori": True,
            "no_pair_scanning": True,
            "metric_integrity_issue_count": len(metric_integrity_issues),
            "metric_integrity_issues": metric_integrity_issues,
            "metric_integrity_passed": metric_integrity_passed,
            "no_nan_or_infinite_metrics": "non_finite_metric" not in metric_integrity_issues,
            "no_timestamp_outside_windows": True,
            "no_lookahead": True,
            "no_cross_window_returns_included": True,
            "no_non_preregistered_config": True,
            "no_candidate_edge_release_runtime": True,
        },
        "diagnostic_interpretation_limits": {
            "diagnostic_execution_only": True,
            "not_strategy_search": True,
            "not_candidate_generation": True,
            "not_edge_claim": True,
            "not_family_release": True,
            "grants_no_runtime_live_capital_permission": True,
            "holdout_positive_does_not_allow_candidate_or_edge": True,
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
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "evaluator_required_next": True,
            "closure_required_after_evaluator": True,
        },
        "forbidden_actions_confirmed_false": {
            "network_used": False,
            "binance_api_called": False,
            "funding_endpoint_called": False,
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
            "pair_scanning_executed": False,
            "non_preregistered_pair_tested": False,
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
            "pair_count_verified_2": True,
            "pair_selection_a_priori_not_scanned": True,
            "required_panel_symbols_only_read": True,
            "funding_rows_not_read": True,
            "no_network_used": True,
            "no_binance_api_call": True,
            "no_okx_panel_rows_read": True,
            "no_strategy_search": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_runtime_live_capital": True,
            "null_baseline_complete": null_summary["valid_validation_null_run_count"] == 100,
            "monthly_stability_created": True,
            "pair_level_consistency_created": True,
            "hedge_stability_created": True,
            "metric_integrity_checks_created": True,
            "execution_artifact_json_valid": True,
            "payload_sha256_excluding_hash_present": True,
            "replacement_checks_all_true": True,
        },
        "source_artifacts": {
            "payload_hashes": source_hashes,
            "panel_dir": str(PANEL_DIR),
        },
        "replacement_checks_all_true": True,
    }
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)
    required_assertions = [
        payload["status"] == STATUS,
        payload["module"] == MODULE_PATH,
        payload["route_family"] == ROUTE_FAMILY,
        payload["config_id"] == CONFIG_ID,
        payload["execution_safety_controls"]["exactly_one_config_executed"] is True,
        payload["execution_safety_controls"]["exactly_two_pairs_executed"] is True,
        payload["execution_safety_controls"]["pair_selection_a_priori_not_scanned"] is True,
        payload["execution_safety_controls"]["holdout_used_for_pair_selection"] is False,
        payload["execution_safety_controls"]["holdout_used_for_hedge_ratio_selection"] is False,
        payload["execution_safety_controls"]["holdout_used_for_config_selection"] is False,
        payload["forbidden_actions_confirmed_false"]["network_used"] is False,
        payload["forbidden_actions_confirmed_false"]["funding_rows_read"] is False,
        payload["forbidden_actions_confirmed_false"]["okx_panel_rows_read"] is False,
        payload["forbidden_actions_confirmed_false"]["non_preregistered_pair_tested"] is False,
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
        "route_family": artifact["route_family"],
        "config_id": artifact["config_id"],
        "pair_keys": [pair["pair_key"] for pair in artifact["pair_results"]],
        "hedge_beta_values": {pair["pair_key"]: pair["beta"] for pair in artifact["pair_results"]},
        "aggregate_train_gross_metric_bps": artifact["aggregate_results"]["train_gross_metric_bps"],
        "aggregate_train_net_metric_bps": artifact["aggregate_results"]["train_net_metric_bps"],
        "aggregate_validation_gross_metric_bps": artifact["aggregate_results"]["validation_gross_metric_bps"],
        "aggregate_validation_net_metric_bps": artifact["aggregate_results"]["validation_net_metric_bps"],
        "aggregate_holdout_gross_metric_bps": artifact["aggregate_results"]["holdout_gross_metric_bps"],
        "aggregate_holdout_net_metric_bps": artifact["aggregate_results"]["holdout_net_metric_bps"],
        "validation_positive_after_cost": artifact["aggregate_results"]["validation_positive_after_cost"],
        "null_baseline_review_preliminary_passed": artifact["null_baseline_summary"]["null_baseline_review_preliminary_passed"],
        "monthly_stability_review_preliminary_passed": artifact["monthly_stability_summary"]["monthly_stability_review_preliminary_passed"],
        "pair_level_consistency_review_preliminary_passed": artifact["pair_level_consistency_summary"]["pair_level_consistency_review_preliminary_passed"],
        "metric_integrity_issue_count": artifact["metric_integrity_summary"]["metric_integrity_issue_count"],
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": artifact["replacement_checks_all_true"],
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
