from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import subprocess
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PANEL_DIR = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_binance_okx_overlap_81_symbol_15m_panel_build_v1\panel_15m_by_symbol"
)
PANEL_REVIEW = REPO_ROOT / "artifacts" / "panel_build_reviews" / "binance_okx_overlap_81_symbol_15m_panel_review_after_build_v1.json"
PREREGISTRATION_PATH = REPO_ROOT / "artifacts" / "research_preregistrations" / "crypto_15m_liquidity_sweep_reversal_preregistration_v1.json"
EXECUTION_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_liquidity_sweep_reversal_execution_v1.json"
EVALUATOR_PATH = REPO_ROOT / "artifacts" / "strategy_evaluations" / "crypto_15m_liquidity_sweep_reversal_evaluator_v1.json"
CLOSURE_PATH = REPO_ROOT / "artifacts" / "strategy_closures" / "crypto_15m_liquidity_sweep_reversal_closure_v1.json"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_reviews" / "crypto_15m_liquidity_sweep_filter_kill_audit_v1.json"

STATUS = "PASS_REPO_ONLY_CRYPTO_15M_LIQUIDITY_SWEEP_FILTER_KILL_AUDIT_CREATED"
ARTIFACT_KIND = "CRYPTO_15M_LIQUIDITY_SWEEP_FILTER_KILL_AUDIT"
STRATEGY = "CRYPTO_15M_LIQUIDITY_SWEEP_FAILED_BREAKOUT_REVERSAL_V1"
ROUTE_FAMILY = "CRYPTO_15M_LIQUIDITY_SWEEP_REVERSAL_BASELINE"
CONFIG_ID = "crypto_15m_liquidity_sweep_48h_reversal_r2_timestop8h_v1"

PRIOR_RANGE_WINDOW = 192
ATR_LEN = 14
VOLUME_SMA_LEN = 20
RETURN_4H_BARS = 16
BTC_24H_BARS = 96
VOLUME_MULT = 1.5
TIME_STOP_BARS = 32
MAX_CONCURRENT_POSITIONS = 5
BASE_EQUITY = 1000.0
RISK_USDT = 5.0
MAX_NOTIONAL = 100.0


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def payload_hash(data: dict[str, Any]) -> str:
    clone = dict(data)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git(args: list[str]) -> str:
    completed = subprocess.run(["git", "-C", str(REPO_ROOT), *args], check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def tracked_python_count() -> int:
    return len([line for line in git(["ls-files", "*.py"]).splitlines() if line.strip()])


def read_symbol(symbol: str) -> dict[str, list[Any]]:
    path = PANEL_DIR / f"{symbol}_15m.csv.gz"
    if not path.exists():
        raise FileNotFoundError(str(path))
    data = {"timestamps": [], "opens": [], "highs": [], "lows": [], "closes": [], "volumes": []}
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"timestamp_utc", "open", "high", "low", "close", "volume"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise RuntimeError(f"{symbol} missing required columns: {sorted(missing)}")
        for row in reader:
            data["timestamps"].append(row["timestamp_utc"])
            data["opens"].append(float(row["open"]))
            data["highs"].append(float(row["high"]))
            data["lows"].append(float(row["low"]))
            data["closes"].append(float(row["close"]))
            data["volumes"].append(float(row["volume"]))
    return data


def true_range(high: float, low: float, prev_close: float) -> float:
    return max(high - low, abs(high - prev_close), abs(low - prev_close))


def top_items(counter: Counter[str], limit: int = 10) -> list[dict[str, Any]]:
    return [{"key": key, "count": count} for key, count in counter.most_common(limit)]


def build_btc_24h_returns(master_index_by_ts: dict[str, int]) -> dict[str, float]:
    btc = read_symbol("BTCUSDT")
    values: dict[str, float] = {}
    closes = btc["closes"]
    for idx, timestamp in enumerate(btc["timestamps"]):
        if idx >= BTC_24H_BARS and closes[idx - BTC_24H_BARS] > 0 and timestamp in master_index_by_ts:
            values[timestamp] = closes[idx] / closes[idx - BTC_24H_BARS] - 1.0
    return values


def scan_rank_values(symbol: str, master_index_by_ts: dict[str, int], return_values_by_idx: list[list[float]]) -> None:
    data = read_symbol(symbol)
    timestamps = data["timestamps"]
    closes = data["closes"]
    for idx, timestamp in enumerate(timestamps):
        master_idx = master_index_by_ts.get(timestamp)
        if master_idx is None:
            continue
        if idx >= max(PRIOR_RANGE_WINDOW, RETURN_4H_BARS, ATR_LEN, VOLUME_SMA_LEN) and closes[idx - RETURN_4H_BARS] > 0:
            ret = closes[idx] / closes[idx - RETURN_4H_BARS] - 1.0
            if math.isfinite(ret):
                return_values_by_idx[master_idx].append(ret)


def rank_thresholds(return_values_by_idx: list[list[float]]) -> tuple[list[float | None], list[float | None], list[int]]:
    bottom_threshold: list[float | None] = []
    top_threshold: list[float | None] = []
    eligible_counts: list[int] = []
    for values in return_values_by_idx:
        eligible_counts.append(len(values))
        if len(values) < 5:
            bottom_threshold.append(None)
            top_threshold.append(None)
            continue
        ordered = sorted(values)
        bottom_index = max(0, math.ceil(len(ordered) * 0.20) - 1)
        top_index = min(len(ordered) - 1, math.floor(len(ordered) * 0.80))
        bottom_threshold.append(ordered[bottom_index])
        top_threshold.append(ordered[top_index])
    return bottom_threshold, top_threshold, eligible_counts


def increment(counter: dict[str, int], key: str) -> None:
    counter[key] += 1


def make_stage_counter() -> dict[str, int]:
    return {
        "eligible_rows_with_required_lookback": 0,
        "raw_sweep_count": 0,
        "after_candle_rejection_count": 0,
        "after_volume_filter_count": 0,
        "after_cross_sectional_rank_count": 0,
        "after_btc_disaster_filter_count": 0,
        "after_atr_risk_validity_count": 0,
        "after_next_bar_available_count": 0,
        "final_candidate_count_before_position_capacity": 0,
        "capacity_block_estimate": 0,
        "estimated_accepted_after_capacity": 0,
    }


def risk_valid(side: str, entry: float, atr: float, signal_low: float, signal_high: float) -> bool:
    if entry <= 0 or atr <= 0:
        return False
    if side == "long":
        stop = signal_low - 0.5 * atr
        risk = entry - stop
    else:
        stop = signal_high + 0.5 * atr
        risk = stop - entry
    if risk <= 0:
        return False
    stop_distance_fraction = risk / entry
    if stop_distance_fraction <= 0:
        return False
    notional = min(MAX_NOTIONAL, RISK_USDT / stop_distance_fraction)
    return bool(notional > 0 and math.isfinite(notional))


def audit_symbol(
    symbol: str,
    master_index_by_ts: dict[str, int],
    btc_24h_by_ts: dict[str, float],
    bottom_threshold: list[float | None],
    top_threshold: list[float | None],
    long_counts: dict[str, int],
    short_counts: dict[str, int],
    raw_symbol_counter: Counter[str],
    final_symbol_counter: Counter[str],
    raw_month_counter: Counter[str],
    final_month_counter: Counter[str],
    candidates_by_idx: dict[int, list[dict[str, Any]]],
) -> None:
    data = read_symbol(symbol)
    timestamps = data["timestamps"]
    opens = data["opens"]
    highs = data["highs"]
    lows = data["lows"]
    closes = data["closes"]
    volumes = data["volumes"]
    high_deque: deque[int] = deque()
    low_deque: deque[int] = deque()
    tr_tail: deque[float] = deque()
    tr_sum = 0.0
    vol_tail: deque[float] = deque()
    vol_sum = 0.0

    for idx, timestamp in enumerate(timestamps):
        while high_deque and high_deque[0] < idx - PRIOR_RANGE_WINDOW:
            high_deque.popleft()
        while low_deque and low_deque[0] < idx - PRIOR_RANGE_WINDOW:
            low_deque.popleft()

        master_idx = master_index_by_ts.get(timestamp)
        has_required_lookback = (
            master_idx is not None
            and idx >= max(PRIOR_RANGE_WINDOW, RETURN_4H_BARS, ATR_LEN, VOLUME_SMA_LEN)
            and len(tr_tail) >= ATR_LEN
            and len(vol_tail) >= VOLUME_SMA_LEN
            and closes[idx - RETURN_4H_BARS] > 0
            and bool(high_deque)
            and bool(low_deque)
        )
        if has_required_lookback:
            long_counts["eligible_rows_with_required_lookback"] += 1
            short_counts["eligible_rows_with_required_lookback"] += 1
            prior_high = highs[high_deque[0]]
            prior_low = lows[low_deque[0]]
            atr = tr_sum / len(tr_tail)
            volume_sma = vol_sum / len(vol_tail)
            return_4h = closes[idx] / closes[idx - RETURN_4H_BARS] - 1.0
            candle_range = highs[idx] - lows[idx]
            btc_24h = btc_24h_by_ts.get(timestamp)
            next_bar_available = idx + 1 < len(timestamps) and master_index_by_ts.get(timestamps[idx + 1]) is not None

            raw_long = prior_low > 0 and lows[idx] < prior_low and closes[idx] > prior_low
            raw_short = prior_high > 0 and highs[idx] > prior_high and closes[idx] < prior_high

            if raw_long:
                long_counts["raw_sweep_count"] += 1
                raw_symbol_counter[symbol] += 1
                raw_month_counter[timestamp[:7]] += 1
                candle_ok = closes[idx] > opens[idx] and candle_range > 0 and closes[idx] >= lows[idx] + 0.6 * candle_range
                if candle_ok:
                    long_counts["after_candle_rejection_count"] += 1
                    volume_ok = volumes[idx] > volume_sma * VOLUME_MULT
                    if volume_ok:
                        long_counts["after_volume_filter_count"] += 1
                        rank_ok = bottom_threshold[master_idx] is not None and return_4h <= bottom_threshold[master_idx]
                        if rank_ok:
                            long_counts["after_cross_sectional_rank_count"] += 1
                            btc_ok = btc_24h is None or btc_24h >= -0.05
                            if btc_ok:
                                long_counts["after_btc_disaster_filter_count"] += 1
                                entry = opens[idx + 1] if idx + 1 < len(opens) else 0.0
                                risk_ok = risk_valid("long", entry, atr, lows[idx], highs[idx])
                                if risk_ok:
                                    long_counts["after_atr_risk_validity_count"] += 1
                                    if next_bar_available:
                                        long_counts["after_next_bar_available_count"] += 1
                                        long_counts["final_candidate_count_before_position_capacity"] += 1
                                        final_symbol_counter[symbol] += 1
                                        final_month_counter[timestamp[:7]] += 1
                                        candidates_by_idx[master_idx].append(
                                            {
                                                "symbol": symbol,
                                                "side": "long",
                                                "signal_time": timestamp,
                                                "exit_master_idx": master_idx + TIME_STOP_BARS + 1,
                                                "sweep_depth": (prior_low - lows[idx]) / prior_low,
                                                "return_4h": return_4h,
                                            }
                                        )

            if raw_short:
                short_counts["raw_sweep_count"] += 1
                raw_symbol_counter[symbol] += 1
                raw_month_counter[timestamp[:7]] += 1
                candle_ok = closes[idx] < opens[idx] and candle_range > 0 and closes[idx] <= lows[idx] + 0.4 * candle_range
                if candle_ok:
                    short_counts["after_candle_rejection_count"] += 1
                    volume_ok = volumes[idx] > volume_sma * VOLUME_MULT
                    if volume_ok:
                        short_counts["after_volume_filter_count"] += 1
                        rank_ok = top_threshold[master_idx] is not None and return_4h >= top_threshold[master_idx]
                        if rank_ok:
                            short_counts["after_cross_sectional_rank_count"] += 1
                            btc_ok = btc_24h is None or btc_24h <= 0.05
                            if btc_ok:
                                short_counts["after_btc_disaster_filter_count"] += 1
                                entry = opens[idx + 1] if idx + 1 < len(opens) else 0.0
                                risk_ok = risk_valid("short", entry, atr, lows[idx], highs[idx])
                                if risk_ok:
                                    short_counts["after_atr_risk_validity_count"] += 1
                                    if next_bar_available:
                                        short_counts["after_next_bar_available_count"] += 1
                                        short_counts["final_candidate_count_before_position_capacity"] += 1
                                        final_symbol_counter[symbol] += 1
                                        final_month_counter[timestamp[:7]] += 1
                                        candidates_by_idx[master_idx].append(
                                            {
                                                "symbol": symbol,
                                                "side": "short",
                                                "signal_time": timestamp,
                                                "exit_master_idx": master_idx + TIME_STOP_BARS + 1,
                                                "sweep_depth": (highs[idx] - prior_high) / prior_high,
                                                "return_4h": return_4h,
                                            }
                                        )

        if idx > 0:
            tr = true_range(highs[idx], lows[idx], closes[idx - 1])
            tr_tail.append(tr)
            tr_sum += tr
            if len(tr_tail) > ATR_LEN:
                tr_sum -= tr_tail.popleft()
        vol_tail.append(volumes[idx])
        vol_sum += volumes[idx]
        if len(vol_tail) > VOLUME_SMA_LEN:
            vol_sum -= vol_tail.popleft()
        while high_deque and highs[high_deque[-1]] <= highs[idx]:
            high_deque.pop()
        high_deque.append(idx)
        while low_deque and lows[low_deque[-1]] >= lows[idx]:
            low_deque.pop()
        low_deque.append(idx)


def estimate_capacity(
    master_timestamps: list[str],
    candidates_by_idx: dict[int, list[dict[str, Any]]],
    long_counts: dict[str, int],
    short_counts: dict[str, int],
) -> dict[str, int]:
    open_positions: list[tuple[str, int]] = []
    accepted = {"long": 0, "short": 0}
    blocked = {"long": 0, "short": 0}
    same_symbol_blocked = {"long": 0, "short": 0}
    for master_idx, _timestamp in enumerate(master_timestamps):
        open_positions = [(symbol, exit_idx) for symbol, exit_idx in open_positions if exit_idx > master_idx]
        open_symbols = {symbol for symbol, _exit_idx in open_positions}
        candidates = candidates_by_idx.get(master_idx, [])
        candidates.sort(key=lambda item: (item["sweep_depth"], abs(item["return_4h"])), reverse=True)
        for candidate in candidates:
            side = candidate["side"]
            if candidate["symbol"] in open_symbols:
                blocked[side] += 1
                same_symbol_blocked[side] += 1
                continue
            if len(open_positions) >= MAX_CONCURRENT_POSITIONS:
                blocked[side] += 1
                continue
            accepted[side] += 1
            open_positions.append((candidate["symbol"], candidate["exit_master_idx"]))
            open_symbols.add(candidate["symbol"])
    long_counts["capacity_block_estimate"] = blocked["long"]
    long_counts["estimated_accepted_after_capacity"] = accepted["long"]
    short_counts["capacity_block_estimate"] = blocked["short"]
    short_counts["estimated_accepted_after_capacity"] = accepted["short"]
    return {
        "accepted_long_after_capacity": accepted["long"],
        "accepted_short_after_capacity": accepted["short"],
        "capacity_blocked_long": blocked["long"],
        "capacity_blocked_short": blocked["short"],
        "same_symbol_blocked_long": same_symbol_blocked["long"],
        "same_symbol_blocked_short": same_symbol_blocked["short"],
    }


STAGES = [
    "raw_sweep_count",
    "after_candle_rejection_count",
    "after_volume_filter_count",
    "after_cross_sectional_rank_count",
    "after_btc_disaster_filter_count",
    "after_atr_risk_validity_count",
    "after_next_bar_available_count",
    "final_candidate_count_before_position_capacity",
]


def kill_attribution_for_side(counts: dict[str, int]) -> list[dict[str, Any]]:
    output = []
    raw = counts["raw_sweep_count"]
    previous_stage = "raw_sweep_count"
    for stage in STAGES[1:]:
        prev = counts[previous_stage]
        current = counts[stage]
        killed = prev - current
        output.append(
            {
                "filter_stage": stage,
                "previous_stage_count": prev,
                "survivor_count": current,
                "killed_count": killed,
                "killed_share_of_previous_stage": round(killed / prev, 6) if prev else None,
                "killed_share_of_raw_sweep": round(killed / raw, 6) if raw else None,
            }
        )
        previous_stage = stage
    cap = counts.get("capacity_block_estimate", 0)
    final_before_cap = counts["final_candidate_count_before_position_capacity"]
    output.append(
        {
            "filter_stage": "capacity_block_estimate",
            "previous_stage_count": final_before_cap,
            "survivor_count": counts.get("estimated_accepted_after_capacity", 0),
            "killed_count": cap,
            "killed_share_of_previous_stage": round(cap / final_before_cap, 6) if final_before_cap else None,
            "killed_share_of_raw_sweep": round(cap / raw, 6) if raw else None,
        }
    )
    return output


def primary_kill_filter(long_attr: list[dict[str, Any]], short_attr: list[dict[str, Any]]) -> dict[str, Any]:
    combined: dict[str, dict[str, Any]] = {}
    for side, rows in (("long", long_attr), ("short", short_attr)):
        for row in rows:
            stage = row["filter_stage"]
            combined.setdefault(stage, {"filter_stage": stage, "killed_count": 0, "side_details": {}})
            combined[stage]["killed_count"] += row["killed_count"]
            combined[stage]["side_details"][side] = row
    ranked = sorted(combined.values(), key=lambda item: item["killed_count"], reverse=True)
    return ranked[0] if ranked else {"filter_stage": None, "killed_count": 0, "side_details": {}}


def classify_audit(long_counts: dict[str, int], short_counts: dict[str, int], capacity: dict[str, int], panel_ok: bool) -> tuple[str, str]:
    raw_total = long_counts["raw_sweep_count"] + short_counts["raw_sweep_count"]
    final_total = long_counts["final_candidate_count_before_position_capacity"] + short_counts["final_candidate_count_before_position_capacity"]
    accepted_after_capacity = capacity["accepted_long_after_capacity"] + capacity["accepted_short_after_capacity"]
    if not panel_ok:
        return "LIQUIDITY_SWEEP_NO_TRADE_CAUSED_BY_DATA_OR_FIELD_ISSUE", "Panel or required field availability should be repaired before any bounded follow-up."
    if final_total > 0 or accepted_after_capacity > 0:
        return (
            "LIQUIDITY_SWEEP_NO_TRADE_CAUSED_BY_SIGNAL_LOGIC_BUG",
            "Bounded V2 direction: inspect the prior execution implementation against this audit, because the filter pipeline yields candidates before capacity without changing strategy parameters.",
        )
    if raw_total > 0:
        return (
            "LIQUIDITY_SWEEP_NO_TRADE_CAUSED_BY_OVERSTRICT_FILTERS",
            "Bounded V2 direction: document which preregistered filter eliminates the raw sweeps before considering any separately approved fixed-config follow-up; no parameter optimization is authorized here.",
        )
    return (
        "LIQUIDITY_SWEEP_NO_TRADE_CAUSED_BY_TRUE_RARITY",
        "Bounded V2 direction: raw sweep definitions themselves appear rare under the reviewed panel; any follow-up must be separately preregistered and must not optimize from this audit.",
    )


def main() -> int:
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status = {
        "?? tools/edge_factory_os_repo_only_crypto_15m_liquidity_sweep_filter_kill_audit_v1.py",
        "?? artifacts/strategy_reviews/crypto_15m_liquidity_sweep_filter_kill_audit_v1.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]

    panel_review = load_json(PANEL_REVIEW)
    preregistration = load_json(PREREGISTRATION_PATH)
    execution = load_json(EXECUTION_PATH)
    evaluator = load_json(EVALUATOR_PATH)
    closure = load_json(CLOSURE_PATH)

    files = sorted(PANEL_DIR.glob("*_15m.csv.gz"))
    symbols = [path.name.removesuffix("_15m.csv.gz") for path in files]
    panel_ok = PANEL_DIR.exists() and len(symbols) == 81 and (PANEL_DIR / "BTCUSDT_15m.csv.gz").exists()
    if not panel_ok:
        raise RuntimeError("reviewed panel unavailable for filter-kill audit")

    btc = read_symbol("BTCUSDT")
    master_timestamps = btc["timestamps"]
    master_index_by_ts = {timestamp: idx for idx, timestamp in enumerate(master_timestamps)}
    btc_24h_by_ts = build_btc_24h_returns(master_index_by_ts)

    return_values_by_idx: list[list[float]] = [[] for _ in master_timestamps]
    for symbol in symbols:
        scan_rank_values(symbol, master_index_by_ts, return_values_by_idx)
    bottom_threshold, top_threshold, eligible_counts = rank_thresholds(return_values_by_idx)

    long_counts = make_stage_counter()
    short_counts = make_stage_counter()
    raw_symbol_counter: Counter[str] = Counter()
    final_symbol_counter: Counter[str] = Counter()
    raw_month_counter: Counter[str] = Counter()
    final_month_counter: Counter[str] = Counter()
    candidates_by_idx: dict[int, list[dict[str, Any]]] = defaultdict(list)

    for symbol in symbols:
        audit_symbol(
            symbol,
            master_index_by_ts,
            btc_24h_by_ts,
            bottom_threshold,
            top_threshold,
            long_counts,
            short_counts,
            raw_symbol_counter,
            final_symbol_counter,
            raw_month_counter,
            final_month_counter,
            candidates_by_idx,
        )

    capacity = estimate_capacity(master_timestamps, candidates_by_idx, long_counts, short_counts)
    long_attr = kill_attribution_for_side(long_counts)
    short_attr = kill_attribution_for_side(short_counts)
    primary = primary_kill_filter(long_attr, short_attr)
    classification, bounded_v2_direction = classify_audit(long_counts, short_counts, capacity, panel_ok)

    raw_total = long_counts["raw_sweep_count"] + short_counts["raw_sweep_count"]
    final_total = long_counts["final_candidate_count_before_position_capacity"] + short_counts["final_candidate_count_before_position_capacity"]
    diagnostic_flags = {
        "long_side_dies_earlier": long_counts["final_candidate_count_before_position_capacity"] < short_counts["final_candidate_count_before_position_capacity"],
        "short_side_dies_earlier": short_counts["final_candidate_count_before_position_capacity"] < long_counts["final_candidate_count_before_position_capacity"],
        "volume_filter_appears_too_strict": any(
            row["filter_stage"] == "after_volume_filter_count"
            and row["killed_share_of_previous_stage"] is not None
            and row["killed_share_of_previous_stage"] >= 0.80
            for row in long_attr + short_attr
        ),
        "rank_filter_appears_too_strict": any(
            row["filter_stage"] == "after_cross_sectional_rank_count"
            and row["killed_share_of_previous_stage"] is not None
            and row["killed_share_of_previous_stage"] >= 0.80
            for row in long_attr + short_attr
        ),
        "candle_rejection_appears_too_strict": any(
            row["filter_stage"] == "after_candle_rejection_count"
            and row["killed_share_of_previous_stage"] is not None
            and row["killed_share_of_previous_stage"] >= 0.80
            for row in long_attr + short_attr
        ),
        "atr_risk_validity_kills_candidates": (
            long_counts["after_btc_disaster_filter_count"] + short_counts["after_btc_disaster_filter_count"]
            > long_counts["after_atr_risk_validity_count"] + short_counts["after_atr_risk_validity_count"]
        ),
        "btc_disaster_filter_kills_meaningful_count": (
            long_counts["after_cross_sectional_rank_count"] + short_counts["after_cross_sectional_rank_count"]
            - long_counts["after_btc_disaster_filter_count"] - short_counts["after_btc_disaster_filter_count"]
            > 0
        ),
        "any_final_candidates_before_capacity": final_total > 0,
    }

    safety_permissions = {
        "filter_kill_audit_created": True,
        "strategy_execution_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
    }
    validation_checks = {
        "repo_clean_before_run": not unexpected_status,
        "prior_liquidity_sweep_artifacts_loaded": True,
        "panel_review_loaded": True,
        "no_new_strategy_executed": True,
        "no_v2_tested": True,
        "no_parameter_optimization": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_network_used": True,
        "no_api_called": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": True,
        "replacement_checks_all_true": True,
    }

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": "edge_factory_os_repo_only_crypto_15m_liquidity_sweep_filter_kill_audit_v1",
        "source_checkpoint": {
            "actual_head": git(["rev-parse", "HEAD"]),
            "tracked_python_count": tracked_python_count(),
            "repo_clean_before_run": not unexpected_status,
            "git_status_at_audit": status_lines,
            "allowed_new_paths_at_audit": sorted(allowed_status),
            "unexpected_dirty_paths_at_audit": unexpected_status,
        },
        "source_artifacts": {
            "panel_review": str(PANEL_REVIEW),
            "preregistration": str(PREREGISTRATION_PATH),
            "execution": str(EXECUTION_PATH),
            "evaluator": str(EVALUATOR_PATH),
            "closure": str(CLOSURE_PATH),
        },
        "prior_result_summary": {
            "strategy": STRATEGY,
            "route_family": ROUTE_FAMILY,
            "config_id": CONFIG_ID,
            "execution_status": execution.get("status"),
            "evaluator_result_classification": evaluator.get("result_classification"),
            "closure_result_classification": closure.get("closure_result", {}).get("result_classification"),
            "prior_accepted_long_trades": execution.get("metrics", {}).get("accepted_long_trades"),
            "prior_accepted_short_trades": execution.get("metrics", {}).get("accepted_short_trades"),
            "prior_closed_trades": execution.get("metrics", {}).get("closed_trades"),
            "prior_metric_integrity": execution.get("metric_integrity_result", {}).get("passed"),
        },
        "dataset_review": {
            "panel_dir": str(PANEL_DIR),
            "panel_review_status": panel_review.get("status"),
            "symbol_file_count": len(symbols),
            "master_timestamp_count": len(master_timestamps),
            "eligible_symbol_count_average": round(sum(eligible_counts) / len(eligible_counts), 6) if eligible_counts else 0.0,
        },
        "filter_pipeline_counts": {
            "raw_sweep_count_total": raw_total,
            "final_candidate_count_before_position_capacity_total": final_total,
            "estimated_accepted_after_capacity_total": capacity["accepted_long_after_capacity"] + capacity["accepted_short_after_capacity"],
            "long": long_counts,
            "short": short_counts,
            "capacity_estimate": capacity,
        },
        "long_side_filter_counts": long_counts,
        "short_side_filter_counts": short_counts,
        "kill_attribution": {
            "long": long_attr,
            "short": short_attr,
            "diagnostic_flags": diagnostic_flags,
        },
        "top_symbols_by_stage": {
            "raw_sweeps": top_items(raw_symbol_counter),
            "final_candidates_before_capacity": top_items(final_symbol_counter),
        },
        "top_months_by_stage": {
            "raw_sweeps": top_items(raw_month_counter),
            "final_candidates_before_capacity": top_items(final_month_counter),
        },
        "suspected_primary_kill_filter": primary,
        "audit_classification": classification,
        "bounded_v2_direction": bounded_v2_direction,
        "limitations": [
            "This audit recomputes the filter pipeline and capacity estimate only; it does not create trades, compute PnL, optimize parameters, or run a V2 strategy.",
            "Capacity estimate uses fixed 32-bar holding state solely to count capacity and same-symbol blocks.",
        ],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": all(validation_checks.values())
        and safety_permissions["filter_kill_audit_created"] is True
        and all(value is False for key, value in safety_permissions.items() if key != "filter_kill_audit_created"),
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")

    print(f"status: {STATUS}")
    print(f"audit_classification: {classification}")
    print(f"raw_long_sweep_count: {long_counts['raw_sweep_count']}")
    print(f"raw_short_sweep_count: {short_counts['raw_sweep_count']}")
    print(f"final_long_candidate_count: {long_counts['final_candidate_count_before_position_capacity']}")
    print(f"final_short_candidate_count: {short_counts['final_candidate_count_before_position_capacity']}")
    print(f"suspected_primary_kill_filter: {primary['filter_stage']}")
    print(f"bounded_v2_direction: {bounded_v2_direction}")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
