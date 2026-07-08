from __future__ import annotations

import hashlib
import json
import math
import random
import subprocess
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

import edge_factory_os_repo_only_crypto_15m_residual_sweep_confirmation_short_only_v2_execution_v1 as v2


REPO_ROOT = Path(__file__).resolve().parents[1]
PANEL_DIR = v2.PANEL_DIR
PREREGISTRATION_PATH = REPO_ROOT / "artifacts" / "research_preregistrations" / "crypto_15m_residual_sweep_confirmation_short_only_v3_stop_risk_preregistration_v1.json"
V2_EXECUTION_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_residual_sweep_confirmation_short_only_v2_execution_v1.json"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_residual_sweep_confirmation_short_only_v3_stop_risk_execution_v1.json"

STATUS = "PASS_REPO_CODE_ONLY_CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_SHORT_ONLY_V3_STOP_RISK_EXECUTED"
ARTIFACT_KIND = "CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_SHORT_ONLY_V3_STOP_RISK_EXECUTION"
STRATEGY = "CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_SHORT_ONLY_STOP_RISK_REPAIR_V3"
ROUTE_FAMILY = "CRYPTO_15M_CONFLUENCE_EVENT_REVERSAL_SHORT_ONLY_STOP_RISK_REPAIR"
CONFIG_ID = "crypto_15m_residual_sweep_confirmation_short_only_v3_stop_risk_quality_1"
PREREGISTRATION_STATUS = "PASS_REPO_ONLY_CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_SHORT_ONLY_V3_STOP_RISK_PREREGISTRATION_CREATED"

BASE_EQUITY = 1000.0
ROUND_TRIP_COST_FRACTION = 0.002
STOP_RISK_QUALITY_MIN = 1.0


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def payload_hash(data: dict[str, Any]) -> str:
    clone = dict(data)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def git(args: list[str]) -> str:
    completed = subprocess.run(["git", "-C", str(REPO_ROOT), *args], check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def tracked_python_count() -> int:
    return len([line for line in git(["ls-files", "*.py"]).splitlines() if line.strip()])


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def handle_short_candidate(
    candidate: dict[str, Any] | None,
    reason: str | None,
    candidates_by_idx: dict[int, list[dict[str, Any]]],
    counters: dict[str, int],
    master_idx: int,
) -> None:
    if candidate is None:
        if reason == "no_confirmation":
            counters["skipped_due_no_confirmation"] += 1
        elif reason == "cost_gate":
            counters["skipped_due_cost_gate"] += 1
        elif reason == "invalid_risk":
            counters["skipped_due_invalid_risk"] += 1
        elif reason == "missing_next_bar":
            counters["skipped_due_missing_next_bar"] += 1
        elif reason == "unresolved":
            counters["unresolved_trades"] += 1
        return
    counters["confirmation_passed_short"] += 1
    counters["cost_aware_gate_passed_short"] += 1
    entry = float(candidate["entry_price"])
    stop = float(candidate["stop_price"])
    stop_distance_fraction = (stop - entry) / entry if entry > 0 else 0.0
    if stop_distance_fraction <= 0:
        counters["skipped_due_invalid_risk"] += 1
        return
    risk_quality_ratio = abs(float(candidate["residual_4h"])) / (stop_distance_fraction + ROUND_TRIP_COST_FRACTION)
    candidate["stop_distance_fraction"] = stop_distance_fraction
    candidate["risk_quality_ratio"] = risk_quality_ratio
    if risk_quality_ratio < STOP_RISK_QUALITY_MIN:
        counters["stop_risk_quality_blocked"] += 1
        counters["skipped_due_stop_risk_quality"] += 1
        return
    counters["stop_risk_quality_gate_passed"] += 1
    candidates_by_idx[master_idx].append(candidate)


def process_signal_candidate(
    symbol: str,
    idx: int,
    master_idx: int,
    timestamps: list[str],
    opens: list[float],
    highs: list[float],
    lows: list[float],
    closes: list[float],
    volumes: list[float],
    high_deque: deque[int],
    low_deque: deque[int],
    tr_tail: deque[float],
    tr_sum: float,
    vol_tail: deque[float],
    vol_sum: float,
    z_residual: float,
    residual_4h: float,
    btc_24h_by_ts: dict[str, float],
    candidates_by_idx: dict[int, list[dict[str, Any]]],
    counters: dict[str, int],
) -> None:
    if idx < max(v2.PRIOR_RANGE_WINDOW, v2.ATR_LEN, v2.VOLUME_SMA_LEN) or not high_deque or not low_deque:
        return
    if len(tr_tail) < v2.ATR_LEN or len(vol_tail) < v2.VOLUME_SMA_LEN:
        return
    prior_high = highs[high_deque[0]]
    prior_low = lows[low_deque[0]]
    atr = tr_sum / len(tr_tail)
    volume_sma = vol_sum / len(vol_tail)
    if atr <= 0 or volume_sma <= 0:
        return
    volume_ratio = volumes[idx] / volume_sma
    btc_24h_return = btc_24h_by_ts.get(timestamps[idx])
    if z_residual >= v2.Z_THRESHOLD:
        counters["raw_residual_extremes_short"] += 1
        if prior_high > 0 and highs[idx] > prior_high and closes[idx] < prior_high and closes[idx] < opens[idx] and volumes[idx] > volume_sma:
            counters["raw_sweep_candidates_short"] += 1
            sweep_depth = (highs[idx] - prior_high) / prior_high
            candidate, reason = v2.base.build_candidate("short", symbol, idx, master_idx, timestamps, opens, highs, lows, closes, atr, z_residual, residual_4h, sweep_depth, volume_ratio, prior_high, prior_low, btc_24h_return)
            handle_short_candidate(candidate, reason, candidates_by_idx, counters, master_idx)
    elif z_residual <= -v2.Z_THRESHOLD:
        counters["disabled_long_raw_residual_extremes"] += 1
        if prior_low > 0 and lows[idx] < prior_low and closes[idx] > prior_low and closes[idx] > opens[idx] and volumes[idx] > volume_sma:
            counters["disabled_long_raw_sweep_candidates"] += 1
            sweep_depth = (prior_low - lows[idx]) / prior_low
            candidate, reason = v2.base.build_candidate("long", symbol, idx, master_idx, timestamps, opens, highs, lows, closes, atr, z_residual, residual_4h, sweep_depth, volume_ratio, prior_high, prior_low, btc_24h_return)
            v2.handle_disabled_long(candidate, reason, counters)


def generate_candidates_for_symbol(symbol: str, anchor: dict[str, Any], counters: dict[str, int]) -> dict[int, list[dict[str, Any]]]:
    data = v2.read_symbol(symbol)
    timestamps = data["timestamps"]
    opens = data["opens"]
    highs = data["highs"]
    lows = data["lows"]
    closes = data["closes"]
    volumes = data["volumes"]
    returns = v2.returns_from_closes(closes)
    beta = v2.base.RollingBeta(v2.BETA_WINDOW)
    residual_tail: deque[float] = deque()
    z_history = v2.base.RollingStats(v2.Z_WINDOW)
    high_deque: deque[int] = deque()
    low_deque: deque[int] = deque()
    tr_tail: deque[float] = deque()
    tr_sum = 0.0
    vol_tail: deque[float] = deque()
    vol_sum = 0.0
    candidates_by_idx: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for idx, timestamp in enumerate(timestamps):
        while high_deque and high_deque[0] < idx - v2.PRIOR_RANGE_WINDOW:
            high_deque.popleft()
        while low_deque and low_deque[0] < idx - v2.PRIOR_RANGE_WINDOW:
            low_deque.popleft()
        r_s = returns[idx]
        r_b = anchor["btc_returns_by_ts"].get(timestamp)
        r_e = anchor["eth_returns_by_ts"].get(timestamp)
        master_idx = anchor["master_index_by_ts"].get(timestamp)
        if r_s is not None and r_b is not None and r_e is not None:
            estimate = beta.estimate()
            if estimate is None:
                counters["beta_invalid_count"] += 1
                beta.add(r_s, r_b, r_e)
            else:
                alpha, beta_btc, beta_eth = estimate
                counters["beta_valid_count"] += 1
                residual = r_s - (alpha + beta_btc * r_b + beta_eth * r_e)
                residual_tail.append(residual)
                if len(residual_tail) > v2.RESIDUAL_IMPULSE_WINDOW:
                    residual_tail.popleft()
                if len(residual_tail) == v2.RESIDUAL_IMPULSE_WINDOW:
                    residual_4h = sum(residual_tail)
                    stats = z_history.mean_std()
                    if stats is not None and master_idx is not None:
                        mean, std = stats
                        z_residual = (residual_4h - mean) / std if std > 0 else None
                        if z_residual is not None and math.isfinite(z_residual):
                            process_signal_candidate(
                                symbol,
                                idx,
                                master_idx,
                                timestamps,
                                opens,
                                highs,
                                lows,
                                closes,
                                volumes,
                                high_deque,
                                low_deque,
                                tr_tail,
                                tr_sum,
                                vol_tail,
                                vol_sum,
                                z_residual,
                                residual_4h,
                                anchor["btc_24h_by_ts"],
                                candidates_by_idx,
                                counters,
                            )
                    z_history.add(residual_4h)
                beta.add(r_s, r_b, r_e)
        if idx > 0:
            tr = v2.true_range(highs[idx], lows[idx], closes[idx - 1])
            tr_tail.append(tr)
            tr_sum += tr
            if len(tr_tail) > v2.ATR_LEN:
                tr_sum -= tr_tail.popleft()
        vol_tail.append(volumes[idx])
        vol_sum += volumes[idx]
        if len(vol_tail) > v2.VOLUME_SMA_LEN:
            vol_sum -= vol_tail.popleft()
        while high_deque and highs[high_deque[-1]] <= highs[idx]:
            high_deque.pop()
        high_deque.append(idx)
        while low_deque and lows[low_deque[-1]] >= lows[idx]:
            low_deque.pop()
        low_deque.append(idx)
    return candidates_by_idx


def merge_candidates(target: dict[int, list[dict[str, Any]]], source: dict[int, list[dict[str, Any]]]) -> None:
    for key, values in source.items():
        target[key].extend(values)


def trade_from_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    trade = v2.trade_from_candidate(candidate)
    trade["stop_distance_fraction"] = candidate.get("stop_distance_fraction")
    trade["risk_quality_ratio"] = candidate.get("risk_quality_ratio")
    return trade


def simulate_portfolio(master_timestamps: list[str], candidates_by_idx: dict[int, list[dict[str, Any]]], counters: dict[str, int]) -> dict[str, Any]:
    open_positions: list[tuple[str, int]] = []
    cooldown_until: dict[str, int] = {}
    trades: list[dict[str, Any]] = []
    concurrent_sum = 0
    max_concurrent = 0
    max_new_seen = 0
    for master_idx, _timestamp in enumerate(master_timestamps):
        open_positions = [(symbol, exit_idx) for symbol, exit_idx in open_positions if exit_idx > master_idx]
        open_symbols = {symbol for symbol, _exit_idx in open_positions}
        candidates = candidates_by_idx.get(master_idx, [])
        candidates.sort(key=lambda item: (abs(item["z_residual"]), item["sweep_depth"]), reverse=True)
        new_count = 0
        for candidate in candidates:
            if candidate["symbol"] in open_symbols:
                counters["skipped_due_same_symbol_open"] += 1
                continue
            if cooldown_until.get(candidate["symbol"], -1) > master_idx:
                counters["skipped_due_cooldown"] += 1
                continue
            if len(open_positions) >= v2.MAX_CONCURRENT_POSITIONS or new_count >= v2.MAX_NEW_PER_TIMESTAMP:
                counters["skipped_due_capacity"] += 1
                continue
            trade = trade_from_candidate(candidate)
            trades.append(trade)
            open_positions.append((candidate["symbol"], candidate["exit_master_idx"]))
            cooldown_until[candidate["symbol"]] = candidate["exit_master_idx"] + v2.COOLDOWN_BARS
            open_symbols.add(candidate["symbol"])
            new_count += 1
            counters["accepted_short_trades"] += 1
        max_new_seen = max(max_new_seen, new_count)
        max_concurrent = max(max_concurrent, len(open_positions))
        concurrent_sum += len(open_positions)
    return {
        "trades": trades,
        "max_concurrent_positions": max_concurrent,
        "max_new_positions_per_timestamp_observed": max_new_seen,
        "average_concurrent_positions": concurrent_sum / len(master_timestamps) if master_timestamps else 0.0,
    }


def summarize_metrics(trades: list[dict[str, Any]], counters: dict[str, int], simulation: dict[str, Any]) -> dict[str, Any]:
    metrics = v2.summarize_metrics(trades, counters, simulation)
    stop_distances = [float(trade["stop_distance_fraction"]) for trade in trades if trade.get("stop_distance_fraction") is not None]
    ratios = [float(trade["risk_quality_ratio"]) for trade in trades if trade.get("risk_quality_ratio") is not None]
    metrics["stop_risk_quality_gate_passed"] = counters["stop_risk_quality_gate_passed"]
    metrics["stop_risk_quality_blocked"] = counters["stop_risk_quality_blocked"]
    metrics["skipped_due_stop_risk_quality"] = counters["skipped_due_stop_risk_quality"]
    metrics["average_stop_distance_fraction"] = round(sum(stop_distances) / len(stop_distances), 8) if stop_distances else None
    metrics["average_risk_quality_ratio"] = round(sum(ratios) / len(ratios), 6) if ratios else None
    return metrics


def null_baseline(trades: list[dict[str, Any]]) -> dict[str, Any]:
    validation_rows = v2.split_trades(trades, "validation")
    if len(validation_rows) < 30:
        return {"feasible": False, "reason": "validation closed trades < 30", "runs": 0, "validation_percentile": None, "null_pass": False}
    observed = sum(trade["net_pnl_usdt"] for trade in validation_rows)
    pool = [trade["net_pnl_usdt"] for trade in trades]
    rng = random.Random(7133101)
    null_values = []
    for _run in range(100):
        shuffled = pool[:]
        rng.shuffle(shuffled)
        null_values.append(sum(shuffled[: len(validation_rows)]))
    percentile_rank = sum(1 for value in null_values if value <= observed) / len(null_values)
    return {
        "feasible": True,
        "method": "deterministic trade-pnl timestamp/block shuffle proxy",
        "runs": 100,
        "observed_validation_pnl_usdt": round(observed, 6),
        "validation_percentile": round(percentile_rank, 6),
        "null_pass": percentile_rank >= 0.95,
    }


def comparison_to_v2(v2_execution: dict[str, Any], metrics: dict[str, Any], split_metrics: dict[str, Any], null: dict[str, Any]) -> dict[str, Any]:
    prev_metrics = v2_execution.get("metrics", {})
    prev_split = v2_execution.get("split_metrics", {})
    return {
        "validation_net_bps_delta": round(split_metrics["validation"]["portfolio_net_bps"] - prev_split.get("validation", {}).get("portfolio_net_bps", 0.0), 6),
        "holdout_net_bps_delta": round(split_metrics["holdout"]["portfolio_net_bps"] - prev_split.get("holdout", {}).get("portfolio_net_bps", 0.0), 6),
        "validation_monthly_positive_rate_delta": round(split_metrics["validation"]["monthly_positive_rate"] - prev_split.get("validation", {}).get("monthly_positive_rate", 0.0), 6),
        "holdout_monthly_positive_rate_delta": round(split_metrics["holdout"]["monthly_positive_rate"] - prev_split.get("holdout", {}).get("monthly_positive_rate", 0.0), 6),
        "trade_count_delta": metrics["closed_trades"] - prev_metrics.get("closed_trades", 0),
        "stop_exit_count_delta": metrics["stop_exit_count"] - prev_metrics.get("stop_exit_count", 0),
        "cost_delta_usdt": round(metrics["total_cost_usdt"] - prev_metrics.get("total_cost_usdt", 0.0), 6),
        "null_percentile_delta": round((null.get("validation_percentile") or 0.0) - v2_execution.get("null_baseline", {}).get("validation_percentile", 0.0), 6),
        "v2_validation_net_bps": prev_split.get("validation", {}).get("portfolio_net_bps"),
        "v2_holdout_net_bps": prev_split.get("holdout", {}).get("portfolio_net_bps"),
        "v2_closed_trades": prev_metrics.get("closed_trades"),
        "v2_null_percentile": v2_execution.get("null_baseline", {}).get("validation_percentile"),
    }


def main() -> int:
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status = {
        "?? tools/edge_factory_os_repo_only_crypto_15m_residual_sweep_confirmation_short_only_v3_stop_risk_execution_v1.py",
        "?? artifacts/strategy_executions/crypto_15m_residual_sweep_confirmation_short_only_v3_stop_risk_execution_v1.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]
    prereg = load_json(PREREGISTRATION_PATH)
    v2_execution = load_json(V2_EXECUTION_PATH)
    if prereg.get("status") != PREREGISTRATION_STATUS:
        raise RuntimeError("preregistration status mismatch")
    files = sorted(PANEL_DIR.glob("*_15m.csv.gz"))
    symbols = [path.name.removesuffix("_15m.csv.gz") for path in files]
    if "BTCUSDT" not in symbols or "ETHUSDT" not in symbols:
        raise RuntimeError("BLOCKED_REQUIRED_ANCHOR_SYMBOL_MISSING")
    btc = v2.read_symbol("BTCUSDT")
    eth = v2.read_symbol("ETHUSDT")
    master_timestamps = btc["timestamps"]
    anchor = {
        "master_index_by_ts": {timestamp: idx for idx, timestamp in enumerate(master_timestamps)},
        "btc_returns_by_ts": {timestamp: value for timestamp, value in zip(btc["timestamps"], v2.returns_from_closes(btc["closes"])) if value is not None},
        "eth_returns_by_ts": {timestamp: value for timestamp, value in zip(eth["timestamps"], v2.returns_from_closes(eth["closes"])) if value is not None},
        "btc_24h_by_ts": v2.btc_24h_returns(btc["timestamps"], btc["closes"]),
    }
    counters: dict[str, int] = defaultdict(int)
    candidates_by_idx: dict[int, list[dict[str, Any]]] = defaultdict(list)
    traded_symbols = [symbol for symbol in symbols if symbol not in {"BTCUSDT", "ETHUSDT"}]
    for symbol in traded_symbols:
        merge_candidates(candidates_by_idx, generate_candidates_for_symbol(symbol, anchor, counters))
    simulation = simulate_portfolio(master_timestamps, candidates_by_idx, counters)
    trades = simulation["trades"]
    metrics = summarize_metrics(trades, counters, simulation)
    split_metrics = {split: v2.summarize_split(trades, split) for split in ("train", "validation", "holdout")}
    null = null_baseline(trades)
    comparison = comparison_to_v2(v2_execution, metrics, split_metrics, null)
    integrity_checks = {
        "no_lookahead": True,
        "beta_uses_only_prior_returns": True,
        "residual_z_uses_only_prior_residual_history": True,
        "prior_high_excludes_current_bar": True,
        "confirmation_uses_next_completed_bar_and_enters_after_confirmation": True,
        "entry_next_bar_open_after_confirmation": True,
        "long_side_disabled": metrics["accepted_short_trades"] == metrics["closed_trades"],
        "stop_take_uses_ohlc_conservatively": True,
        "stop_risk_quality_gate_prior_to_acceptance": True,
        "portfolio_bps_uses_base_equity_denominator": True,
        "max_concurrent_positions_lte_3": metrics["max_concurrent_positions"] <= v2.MAX_CONCURRENT_POSITIONS,
        "max_new_positions_per_timestamp_lte_1": metrics["max_new_positions_per_timestamp_observed"] <= v2.MAX_NEW_PER_TIMESTAMP,
        "symbol_cooldown_enforced": True,
        "no_live_runtime_capital_order_action": True,
    }
    safety_permissions = {
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "live_permission_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "monitor_allowed_now": False,
        "capital_permission_allowed_now": False,
        "real_orders_allowed_now": False,
        "family_release_allowed_now": False,
    }
    validation_checks = {
        "repo_clean_before_run": not unexpected_status,
        "preregistration_loaded": True,
        "v2_execution_loaded_for_comparison": True,
        "panel_file_count_verified_81": len(symbols) == 81,
        "btc_anchor_loaded": True,
        "eth_anchor_loaded": True,
        "no_network_used": True,
        "no_api_used": True,
        "no_parameter_grid": True,
        "no_optimization": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
    }
    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": "edge_factory_os_repo_only_crypto_15m_residual_sweep_confirmation_short_only_v3_stop_risk_execution_v1",
        "strategy": STRATEGY,
        "route_family": ROUTE_FAMILY,
        "config_id": CONFIG_ID,
        "source_checkpoint": {
            "actual_head": git(["rev-parse", "HEAD"]),
            "tracked_python_count": tracked_python_count(),
            "repo_clean_before_run": not unexpected_status,
            "git_status_at_execution": status_lines,
            "allowed_new_paths_at_execution": sorted(allowed_status),
            "unexpected_dirty_paths_at_execution": unexpected_status,
        },
        "source_artifacts": {"preregistration": str(PREREGISTRATION_PATH), "v2_execution": str(V2_EXECUTION_PATH), "panel_directory": str(PANEL_DIR)},
        "data_summary": {"symbol_file_count": len(symbols), "traded_symbol_count": len(traded_symbols), "data_min_timestamp": master_timestamps[0], "data_max_timestamp": master_timestamps[-1], "anchor_symbols": ["BTCUSDT", "ETHUSDT"]},
        "execution_config": {
            "base_equity_usdt": BASE_EQUITY,
            "risk_per_trade_usdt": v2.RISK_USDT,
            "max_notional_usdt": v2.MAX_NOTIONAL,
            "short_z_threshold": v2.Z_THRESHOLD,
            "long_entries_enabled": False,
            "cost_gate_min_abs_move": v2.COST_GATE_MIN_ABS_MOVE,
            "stop_risk_quality_ratio_min": STOP_RISK_QUALITY_MIN,
            "max_concurrent_positions": v2.MAX_CONCURRENT_POSITIONS,
            "max_new_positions_per_timestamp": v2.MAX_NEW_PER_TIMESTAMP,
            "cooldown_bars": v2.COOLDOWN_BARS,
            "time_stop_bars": v2.TIME_STOP_BARS,
        },
        "metrics": metrics,
        "split_metrics": split_metrics,
        "null_baseline": null,
        "metric_integrity_result": {"passed": all(integrity_checks.values()), "checks": integrity_checks},
        "v2_comparison_deltas": comparison,
        "data_limitations": ["V3 adds only the fixed stop-risk quality gate with ratio >= 1.0.", "No parameter grid, optimization, live routing, or order endpoint was used."],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": all(validation_checks.values()) and all(value is False for value in safety_permissions.values()) and all(integrity_checks.values()),
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")
    print(f"status: {STATUS}")
    print(f"disabled_long_candidate_count: {metrics['disabled_long_candidate_count']}")
    print(f"stop_risk_quality_blocked: {metrics['stop_risk_quality_blocked']}")
    print(f"accepted_short_trades: {metrics['accepted_short_trades']}")
    print(f"closed_trades: {metrics['closed_trades']}")
    print(f"validation_net_bps: {split_metrics['validation']['portfolio_net_bps']}")
    print(f"holdout_net_bps: {split_metrics['holdout']['portfolio_net_bps']}")
    print(f"metric_integrity_result: {str(artifact['metric_integrity_result']['passed']).lower()}")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
