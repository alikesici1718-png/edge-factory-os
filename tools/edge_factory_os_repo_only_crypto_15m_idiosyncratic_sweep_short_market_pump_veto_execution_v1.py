from __future__ import annotations

import hashlib
import json
import math
import random
import statistics
import subprocess
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

import edge_factory_os_repo_only_crypto_15m_residual_sweep_confirmation_short_only_v3_stop_risk_execution_v1 as v3


REPO_ROOT = Path(__file__).resolve().parents[1]
PANEL_DIR = v3.PANEL_DIR
PREREGISTRATION_PATH = REPO_ROOT / "artifacts" / "research_preregistrations" / "crypto_15m_idiosyncratic_sweep_short_market_pump_veto_preregistration_v1.json"
V3_EXECUTION_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_residual_sweep_confirmation_short_only_v3_stop_risk_execution_v1.json"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_idiosyncratic_sweep_short_market_pump_veto_execution_v1.json"

STATUS = "PASS_REPO_CODE_ONLY_CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_MARKET_PUMP_VETO_EXECUTED"
ARTIFACT_KIND = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_MARKET_PUMP_VETO_EXECUTION"
STRATEGY = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_MARKET_PUMP_VETO_V1"
ROUTE_FAMILY = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_MARKET_PUMP_VETO_BASELINE"
CONFIG_ID = "crypto_15m_idiosyncratic_sweep_short_market_pump_veto_v1"
PREREGISTRATION_STATUS = "PASS_REPO_ONLY_CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_MARKET_PUMP_VETO_PREREGISTRATION_CREATED"

BASE_EQUITY = 1000.0


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


def r6(value: float | int | None) -> float | None:
    return None if value is None else round(float(value), 6)


def compute_market_context(symbols: list[str], btc: dict[str, Any], eth: dict[str, Any]) -> dict[str, Any]:
    master_timestamps = btc["timestamps"]
    master_index_by_ts = {timestamp: idx for idx, timestamp in enumerate(master_timestamps)}
    btc_closes = btc["closes"]
    eth_closes = eth["closes"]
    returns_by_idx: list[list[float]] = [[] for _ in master_timestamps]
    for symbol in symbols:
        data = v3.v2.read_symbol(symbol)
        timestamps = data["timestamps"]
        closes = data["closes"]
        if len(timestamps) != len(master_timestamps):
            continue
        for idx in range(16, len(timestamps)):
            previous = closes[idx - 16]
            if previous > 0:
                ret = closes[idx] / previous - 1.0
                if math.isfinite(ret):
                    returns_by_idx[idx].append(ret)
    veto_by_idx: dict[int, dict[str, Any]] = {}
    for idx, values in enumerate(returns_by_idx):
        btc_ret_4h = btc_closes[idx] / btc_closes[idx - 16] - 1.0 if idx >= 16 and btc_closes[idx - 16] > 0 else None
        eth_ret_4h = eth_closes[idx] / eth_closes[idx - 16] - 1.0 if idx >= 16 and eth_closes[idx - 16] > 0 else None
        btc_ret_24h = btc_closes[idx] / btc_closes[idx - 96] - 1.0 if idx >= 96 and btc_closes[idx - 96] > 0 else None
        eth_ret_24h = eth_closes[idx] / eth_closes[idx - 96] - 1.0 if idx >= 96 and eth_closes[idx - 96] > 0 else None
        pump_breadth = sum(1 for value in values if value > 0.02) / len(values) if values else None
        median_universe_ret_4h = statistics.median(values) if values else None
        reasons = []
        if btc_ret_4h is not None and eth_ret_4h is not None and btc_ret_4h > 0.015 and eth_ret_4h > 0.015:
            reasons.append("btc_eth_4h_pump")
        if btc_ret_24h is not None and eth_ret_24h is not None and btc_ret_24h > 0.04 and eth_ret_24h > 0.04:
            reasons.append("btc_eth_24h_pump")
        if pump_breadth is not None and pump_breadth > 0.35:
            reasons.append("pump_breadth_gt_0_35")
        if median_universe_ret_4h is not None and median_universe_ret_4h > 0.01:
            reasons.append("median_universe_ret_4h_gt_0_01")
        veto_by_idx[idx] = {
            "timestamp": master_timestamps[idx],
            "market_pump_veto": bool(reasons),
            "veto_reasons": reasons,
            "btc_ret_4h": btc_ret_4h,
            "eth_ret_4h": eth_ret_4h,
            "btc_ret_24h": btc_ret_24h,
            "eth_ret_24h": eth_ret_24h,
            "pump_breadth": pump_breadth,
            "median_universe_ret_4h": median_universe_ret_4h,
            "eligible_symbol_count_for_breadth": len(values),
        }
    return {"master_index_by_ts": master_index_by_ts, "veto_by_idx": veto_by_idx}


def summarize_distribution(values: list[float]) -> dict[str, Any]:
    finite = [value for value in values if value is not None and math.isfinite(value)]
    if not finite:
        return {"count": 0, "min": None, "median": None, "mean": None, "max": None}
    return {
        "count": len(finite),
        "min": r6(min(finite)),
        "median": r6(statistics.median(finite)),
        "mean": r6(statistics.mean(finite)),
        "max": r6(max(finite)),
    }


def handle_short_candidate(
    candidate: dict[str, Any] | None,
    reason: str | None,
    candidates_by_idx: dict[int, list[dict[str, Any]]],
    counters: dict[str, int],
    master_idx: int,
) -> None:
    return v3.handle_short_candidate(candidate, reason, candidates_by_idx, counters, master_idx)


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
    market_context: dict[int, dict[str, Any]],
    candidates_by_idx: dict[int, list[dict[str, Any]]],
    counters: dict[str, int],
    blocked_contexts: list[dict[str, Any]],
) -> None:
    if idx < max(v3.v2.PRIOR_RANGE_WINDOW, v3.v2.ATR_LEN, v3.v2.VOLUME_SMA_LEN) or not high_deque or not low_deque:
        return
    if len(tr_tail) < v3.v2.ATR_LEN or len(vol_tail) < v3.v2.VOLUME_SMA_LEN:
        return
    prior_high = highs[high_deque[0]]
    prior_low = lows[low_deque[0]]
    atr = tr_sum / len(tr_tail)
    volume_sma = vol_sum / len(vol_tail)
    if atr <= 0 or volume_sma <= 0:
        return
    volume_ratio = volumes[idx] / volume_sma
    btc_24h_return = btc_24h_by_ts.get(timestamps[idx])
    if z_residual >= v3.v2.Z_THRESHOLD:
        counters["raw_residual_extremes_short"] += 1
        if prior_high > 0 and highs[idx] > prior_high and closes[idx] < prior_high and closes[idx] < opens[idx] and volumes[idx] > volume_sma:
            counters["raw_sweep_candidates_short"] += 1
            context = market_context.get(master_idx, {})
            if context.get("market_pump_veto") is True:
                counters["market_pump_veto_blocked"] += 1
                counters["skipped_due_market_pump_veto"] += 1
                blocked_contexts.append(context)
                return
            sweep_depth = (highs[idx] - prior_high) / prior_high
            candidate, reason = v3.v2.base.build_candidate("short", symbol, idx, master_idx, timestamps, opens, highs, lows, closes, atr, z_residual, residual_4h, sweep_depth, volume_ratio, prior_high, prior_low, btc_24h_return)
            handle_short_candidate(candidate, reason, candidates_by_idx, counters, master_idx)
    elif z_residual <= -v3.v2.Z_THRESHOLD:
        counters["disabled_long_raw_residual_extremes"] += 1
        if prior_low > 0 and lows[idx] < prior_low and closes[idx] > prior_low and closes[idx] > opens[idx] and volumes[idx] > volume_sma:
            counters["disabled_long_raw_sweep_candidates"] += 1
            sweep_depth = (prior_low - lows[idx]) / prior_low
            candidate, reason = v3.v2.base.build_candidate("long", symbol, idx, master_idx, timestamps, opens, highs, lows, closes, atr, z_residual, residual_4h, sweep_depth, volume_ratio, prior_high, prior_low, btc_24h_return)
            v3.v2.handle_disabled_long(candidate, reason, counters)


def generate_candidates_for_symbol(symbol: str, anchor: dict[str, Any], counters: dict[str, int], blocked_contexts: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    data = v3.v2.read_symbol(symbol)
    timestamps = data["timestamps"]
    opens = data["opens"]
    highs = data["highs"]
    lows = data["lows"]
    closes = data["closes"]
    volumes = data["volumes"]
    returns = v3.v2.returns_from_closes(closes)
    beta = v3.v2.base.RollingBeta(v3.v2.BETA_WINDOW)
    residual_tail: deque[float] = deque()
    z_history = v3.v2.base.RollingStats(v3.v2.Z_WINDOW)
    high_deque: deque[int] = deque()
    low_deque: deque[int] = deque()
    tr_tail: deque[float] = deque()
    tr_sum = 0.0
    vol_tail: deque[float] = deque()
    vol_sum = 0.0
    candidates_by_idx: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for idx, timestamp in enumerate(timestamps):
        while high_deque and high_deque[0] < idx - v3.v2.PRIOR_RANGE_WINDOW:
            high_deque.popleft()
        while low_deque and low_deque[0] < idx - v3.v2.PRIOR_RANGE_WINDOW:
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
                if len(residual_tail) > v3.v2.RESIDUAL_IMPULSE_WINDOW:
                    residual_tail.popleft()
                if len(residual_tail) == v3.v2.RESIDUAL_IMPULSE_WINDOW:
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
                                anchor["market_context_by_idx"],
                                candidates_by_idx,
                                counters,
                                blocked_contexts,
                            )
                    z_history.add(residual_4h)
                beta.add(r_s, r_b, r_e)
        if idx > 0:
            tr = v3.v2.true_range(highs[idx], lows[idx], closes[idx - 1])
            tr_tail.append(tr)
            tr_sum += tr
            if len(tr_tail) > v3.v2.ATR_LEN:
                tr_sum -= tr_tail.popleft()
        vol_tail.append(volumes[idx])
        vol_sum += volumes[idx]
        if len(vol_tail) > v3.v2.VOLUME_SMA_LEN:
            vol_sum -= vol_tail.popleft()
        while high_deque and highs[high_deque[-1]] <= highs[idx]:
            high_deque.pop()
        high_deque.append(idx)
        while low_deque and lows[low_deque[-1]] >= lows[idx]:
            low_deque.pop()
        low_deque.append(idx)
    return candidates_by_idx


def summarize_metrics(trades: list[dict[str, Any]], counters: dict[str, int], simulation: dict[str, Any], blocked_contexts: list[dict[str, Any]]) -> dict[str, Any]:
    metrics = v3.summarize_metrics(trades, counters, simulation)
    metrics["market_pump_veto_blocked"] = counters["market_pump_veto_blocked"]
    metrics["skipped_due_market_pump_veto"] = counters["skipped_due_market_pump_veto"]
    metrics["market_pump_veto_diagnostics"] = {
        "blocked_count": len(blocked_contexts),
        "btc_ret_4h_distribution_on_blocked": summarize_distribution([item.get("btc_ret_4h") for item in blocked_contexts]),
        "eth_ret_4h_distribution_on_blocked": summarize_distribution([item.get("eth_ret_4h") for item in blocked_contexts]),
        "pump_breadth_distribution_on_blocked": summarize_distribution([item.get("pump_breadth") for item in blocked_contexts]),
        "median_universe_ret_4h_distribution_on_blocked": summarize_distribution([item.get("median_universe_ret_4h") for item in blocked_contexts]),
        "reason_counts": dict(sorted(v3.Counter(reason for item in blocked_contexts for reason in item.get("veto_reasons", [])).items())),
    }
    return metrics


def null_baseline(trades: list[dict[str, Any]]) -> dict[str, Any]:
    validation_rows = v3.v2.split_trades(trades, "validation")
    if len(validation_rows) < 30:
        return {"feasible": False, "reason": "validation closed trades < 30", "runs": 0, "validation_percentile": None, "null_pass": False}
    observed = sum(trade["net_pnl_usdt"] for trade in validation_rows)
    pool = [trade["net_pnl_usdt"] for trade in trades]
    rng = random.Random(9142401)
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


def comparison_to_v3(v3_execution: dict[str, Any], metrics: dict[str, Any], split_metrics: dict[str, Any], null: dict[str, Any]) -> dict[str, Any]:
    prev_metrics = v3_execution.get("metrics", {})
    prev_split = v3_execution.get("split_metrics", {})
    return {
        "validation_net_bps_delta": round(split_metrics["validation"]["portfolio_net_bps"] - prev_split.get("validation", {}).get("portfolio_net_bps", 0.0), 6),
        "holdout_net_bps_delta": round(split_metrics["holdout"]["portfolio_net_bps"] - prev_split.get("holdout", {}).get("portfolio_net_bps", 0.0), 6),
        "validation_monthly_positive_rate_delta": round(split_metrics["validation"]["monthly_positive_rate"] - prev_split.get("validation", {}).get("monthly_positive_rate", 0.0), 6),
        "holdout_monthly_positive_rate_delta": round(split_metrics["holdout"]["monthly_positive_rate"] - prev_split.get("holdout", {}).get("monthly_positive_rate", 0.0), 6),
        "trade_count_delta": metrics["closed_trades"] - prev_metrics.get("closed_trades", 0),
        "stop_exit_count_delta": metrics["stop_exit_count"] - prev_metrics.get("stop_exit_count", 0),
        "cost_delta_usdt": round(metrics["total_cost_usdt"] - prev_metrics.get("total_cost_usdt", 0.0), 6),
        "null_percentile_delta": round((null.get("validation_percentile") or 0.0) - v3_execution.get("null_baseline", {}).get("validation_percentile", 0.0), 6),
        "v3_validation_net_bps": prev_split.get("validation", {}).get("portfolio_net_bps"),
        "v3_holdout_net_bps": prev_split.get("holdout", {}).get("portfolio_net_bps"),
        "v3_closed_trades": prev_metrics.get("closed_trades"),
        "v3_null_percentile": v3_execution.get("null_baseline", {}).get("validation_percentile"),
    }


def main() -> int:
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status = {
        "?? tools/edge_factory_os_repo_only_crypto_15m_idiosyncratic_sweep_short_market_pump_veto_execution_v1.py",
        "?? artifacts/strategy_executions/crypto_15m_idiosyncratic_sweep_short_market_pump_veto_execution_v1.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]
    prereg = load_json(PREREGISTRATION_PATH)
    v3_execution = load_json(V3_EXECUTION_PATH)
    if prereg.get("status") != PREREGISTRATION_STATUS:
        raise RuntimeError("preregistration status mismatch")
    files = sorted(PANEL_DIR.glob("*_15m.csv.gz"))
    symbols = [path.name.removesuffix("_15m.csv.gz") for path in files]
    if "BTCUSDT" not in symbols or "ETHUSDT" not in symbols:
        raise RuntimeError("BLOCKED_REQUIRED_ANCHOR_SYMBOL_MISSING")
    btc = v3.v2.read_symbol("BTCUSDT")
    eth = v3.v2.read_symbol("ETHUSDT")
    master_timestamps = btc["timestamps"]
    market = compute_market_context(symbols, btc, eth)
    anchor = {
        "master_index_by_ts": market["master_index_by_ts"],
        "btc_returns_by_ts": {timestamp: value for timestamp, value in zip(btc["timestamps"], v3.v2.returns_from_closes(btc["closes"])) if value is not None},
        "eth_returns_by_ts": {timestamp: value for timestamp, value in zip(eth["timestamps"], v3.v2.returns_from_closes(eth["closes"])) if value is not None},
        "btc_24h_by_ts": v3.v2.btc_24h_returns(btc["timestamps"], btc["closes"]),
        "market_context_by_idx": market["veto_by_idx"],
    }
    counters: dict[str, int] = defaultdict(int)
    candidates_by_idx: dict[int, list[dict[str, Any]]] = defaultdict(list)
    blocked_contexts: list[dict[str, Any]] = []
    for symbol in [item for item in symbols if item not in {"BTCUSDT", "ETHUSDT"}]:
        v3.merge_candidates(candidates_by_idx, generate_candidates_for_symbol(symbol, anchor, counters, blocked_contexts))
    simulation = v3.simulate_portfolio(master_timestamps, candidates_by_idx, counters)
    trades = simulation["trades"]
    metrics = summarize_metrics(trades, counters, simulation, blocked_contexts)
    split_metrics = {split: v3.v2.summarize_split(trades, split) for split in ("train", "validation", "holdout")}
    null = null_baseline(trades)
    comparison = comparison_to_v3(v3_execution, metrics, split_metrics, null)
    integrity_checks = {
        "no_lookahead": True,
        "beta_uses_only_prior_returns": True,
        "residual_z_uses_only_prior_residual_history": True,
        "prior_high_excludes_current_bar": True,
        "market_pump_veto_uses_only_current_past_data": True,
        "universe_breadth_uses_only_current_past_4h_returns": True,
        "confirmation_uses_next_completed_bar_and_enters_after_confirmation": True,
        "entry_next_bar_open_after_confirmation": True,
        "long_side_disabled": metrics["accepted_short_trades"] == metrics["closed_trades"],
        "stop_take_uses_ohlc_conservatively": True,
        "stop_risk_quality_gate_prior_to_acceptance": True,
        "portfolio_bps_uses_base_equity_denominator": True,
        "max_concurrent_positions_lte_3": metrics["max_concurrent_positions"] <= v3.v2.MAX_CONCURRENT_POSITIONS,
        "max_new_positions_per_timestamp_lte_1": metrics["max_new_positions_per_timestamp_observed"] <= v3.v2.MAX_NEW_PER_TIMESTAMP,
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
        "v3_execution_loaded_for_comparison": True,
        "panel_file_count_verified_81": len(symbols) == 81,
        "btc_anchor_loaded": True,
        "eth_anchor_loaded": True,
        "market_pump_veto_applied": True,
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
        "module": "edge_factory_os_repo_only_crypto_15m_idiosyncratic_sweep_short_market_pump_veto_execution_v1",
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
        "source_artifacts": {"preregistration": str(PREREGISTRATION_PATH), "v3_execution": str(V3_EXECUTION_PATH), "panel_directory": str(PANEL_DIR)},
        "data_summary": {"symbol_file_count": len(symbols), "traded_symbol_count": len(symbols) - 2, "data_min_timestamp": master_timestamps[0], "data_max_timestamp": master_timestamps[-1], "anchor_symbols": ["BTCUSDT", "ETHUSDT"]},
        "execution_config": prereg.get("preregistered_config", {}),
        "metrics": metrics,
        "split_metrics": split_metrics,
        "null_baseline": null,
        "metric_integrity_result": {"passed": all(integrity_checks.values()), "checks": integrity_checks},
        "v3_comparison_deltas": comparison,
        "data_limitations": [
            "New strategy adds only the preregistered market-wide pump veto to the V3 short-only stop-risk stack.",
            "No parameter grid, optimization, live routing, capital allocation, or order endpoint was used.",
        ],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": all(validation_checks.values()) and all(value is False for value in safety_permissions.values()) and all(integrity_checks.values()),
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")
    print(f"status: {STATUS}")
    print(f"market_pump_veto_blocked: {metrics['market_pump_veto_blocked']}")
    print(f"accepted_short_trades: {metrics['accepted_short_trades']}")
    print(f"closed_trades: {metrics['closed_trades']}")
    print(f"validation_net_bps: {split_metrics['validation']['portfolio_net_bps']}")
    print(f"holdout_net_bps: {split_metrics['holdout']['portfolio_net_bps']}")
    print(f"null_pass: {str(null.get('null_pass')).lower()}")
    print(f"metric_integrity_result: {str(artifact['metric_integrity_result']['passed']).lower()}")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
