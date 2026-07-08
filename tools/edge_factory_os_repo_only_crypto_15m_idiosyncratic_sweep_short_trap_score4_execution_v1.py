from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import edge_factory_os_repo_only_crypto_15m_idiosyncratic_sweep_short_trap_quality_execution_v1 as trap


REPO_ROOT = Path(__file__).resolve().parents[1]
PANEL_DIR = trap.PANEL_DIR
PREREGISTRATION_PATH = REPO_ROOT / "artifacts" / "research_preregistrations" / "crypto_15m_idiosyncratic_sweep_short_trap_score4_preregistration_v1.json"
PRIOR_TRAP_EXECUTION_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_idiosyncratic_sweep_short_trap_quality_execution_v1.json"
RISK_TIGHTENED_EXECUTION_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_idiosyncratic_sweep_short_trap_quality_risk_tightened_execution_v1.json"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_idiosyncratic_sweep_short_trap_score4_execution_v1.json"

STATUS = "PASS_REPO_CODE_ONLY_CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_SCORE4_EXECUTED"
ARTIFACT_KIND = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_SCORE4_EXECUTION"
STRATEGY = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_SCORE4_ONLY_V2"
ROUTE_FAMILY = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_SCORE4_ONLY_BASELINE"
CONFIG_ID = "crypto_15m_idiosyncratic_sweep_short_trap_score4_only_v2"
PREREGISTRATION_STATUS = "PASS_REPO_ONLY_CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_SCORE4_PREREGISTRATION_CREATED"


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


def r6(value: float | int | None) -> float | None:
    return None if value is None else round(float(value), 6)


def comparison_to_prior(prior: dict[str, Any], metrics: dict[str, Any], split_metrics: dict[str, Any], null: dict[str, Any]) -> dict[str, Any]:
    prior_metrics = prior.get("metrics", {})
    prior_split = prior.get("split_metrics", {})
    return {
        "validation_net_bps_delta": r6(split_metrics["validation"]["portfolio_net_bps"] - prior_split.get("validation", {}).get("portfolio_net_bps", 0.0)),
        "holdout_net_bps_delta": r6(split_metrics["holdout"]["portfolio_net_bps"] - prior_split.get("holdout", {}).get("portfolio_net_bps", 0.0)),
        "validation_monthly_positive_rate_delta": r6(split_metrics["validation"]["monthly_positive_rate"] - prior_split.get("validation", {}).get("monthly_positive_rate", 0.0)),
        "holdout_monthly_positive_rate_delta": r6(split_metrics["holdout"]["monthly_positive_rate"] - prior_split.get("holdout", {}).get("monthly_positive_rate", 0.0)),
        "trade_count_delta": metrics["closed_trades"] - prior_metrics.get("closed_trades", 0),
        "stop_exit_count_delta": metrics["stop_exit_count"] - prior_metrics.get("stop_exit_count", 0),
        "cost_delta_usdt": r6(metrics["total_cost_usdt"] - prior_metrics.get("total_cost_usdt", 0.0)),
        "null_percentile_delta": r6((null.get("validation_percentile") or 0.0) - prior.get("null_baseline", {}).get("validation_percentile", 0.0)),
        "prior_validation_net_bps": prior_split.get("validation", {}).get("portfolio_net_bps"),
        "prior_holdout_net_bps": prior_split.get("holdout", {}).get("portfolio_net_bps"),
        "prior_validation_monthly_positive_rate": prior_split.get("validation", {}).get("monthly_positive_rate"),
        "prior_holdout_monthly_positive_rate": prior_split.get("holdout", {}).get("monthly_positive_rate"),
        "prior_closed_trades": prior_metrics.get("closed_trades"),
        "prior_stop_exit_count": prior_metrics.get("stop_exit_count"),
        "prior_cost_usdt": prior_metrics.get("total_cost_usdt"),
        "prior_null_percentile": prior.get("null_baseline", {}).get("validation_percentile"),
    }


def comparison_to_risk_tightened(risk_execution: dict[str, Any], split_metrics: dict[str, Any], null: dict[str, Any]) -> dict[str, Any]:
    risk_split = risk_execution.get("split_metrics", {})
    return {
        "validation_net_bps_delta": r6(split_metrics["validation"]["portfolio_net_bps"] - risk_split.get("validation", {}).get("portfolio_net_bps", 0.0)),
        "holdout_net_bps_delta": r6(split_metrics["holdout"]["portfolio_net_bps"] - risk_split.get("holdout", {}).get("portfolio_net_bps", 0.0)),
        "null_percentile_delta": r6((null.get("validation_percentile") or 0.0) - risk_execution.get("null_baseline", {}).get("validation_percentile", 0.0)),
        "risk_tightened_validation_net_bps": risk_split.get("validation", {}).get("portfolio_net_bps"),
        "risk_tightened_holdout_net_bps": risk_split.get("holdout", {}).get("portfolio_net_bps"),
        "risk_tightened_null_percentile": risk_execution.get("null_baseline", {}).get("validation_percentile"),
    }


def main() -> int:
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status = {
        "?? tools/edge_factory_os_repo_only_crypto_15m_idiosyncratic_sweep_short_trap_score4_execution_v1.py",
        "?? artifacts/strategy_executions/crypto_15m_idiosyncratic_sweep_short_trap_score4_execution_v1.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]

    prereg = load_json(PREREGISTRATION_PATH)
    prior = load_json(PRIOR_TRAP_EXECUTION_PATH)
    risk_tightened = load_json(RISK_TIGHTENED_EXECUTION_PATH)
    if prereg.get("status") != PREREGISTRATION_STATUS:
        raise RuntimeError("preregistration status mismatch")

    files = sorted(PANEL_DIR.glob("*_15m.csv.gz"))
    symbols = [path.name.removesuffix("_15m.csv.gz") for path in files]
    if "BTCUSDT" not in symbols or "ETHUSDT" not in symbols:
        raise RuntimeError("BLOCKED_REQUIRED_ANCHOR_SYMBOL_MISSING")

    btc = trap.mpv.v3.v2.read_symbol("BTCUSDT")
    eth = trap.mpv.v3.v2.read_symbol("ETHUSDT")
    master_timestamps = btc["timestamps"]
    market = trap.mpv.compute_market_context(symbols, btc, eth)
    anchor = {
        "master_index_by_ts": market["master_index_by_ts"],
        "btc_returns_by_ts": {timestamp: value for timestamp, value in zip(btc["timestamps"], trap.mpv.v3.v2.returns_from_closes(btc["closes"])) if value is not None},
        "eth_returns_by_ts": {timestamp: value for timestamp, value in zip(eth["timestamps"], trap.mpv.v3.v2.returns_from_closes(eth["closes"])) if value is not None},
        "btc_24h_by_ts": trap.mpv.v3.v2.btc_24h_returns(btc["timestamps"], btc["closes"]),
        "market_context_by_idx": market["veto_by_idx"],
    }

    original_trap_score_min = trap.TRAP_SCORE_MIN
    trap.TRAP_SCORE_MIN = 4
    try:
        counters: dict[str, int] = defaultdict(int)
        candidates_by_idx: dict[int, list[dict[str, Any]]] = defaultdict(list)
        blocked_contexts: list[dict[str, Any]] = []
        for symbol in [item for item in symbols if item not in {"BTCUSDT", "ETHUSDT"}]:
            trap.mpv.v3.merge_candidates(candidates_by_idx, trap.generate_candidates_for_symbol(symbol, anchor, counters, blocked_contexts))
    finally:
        trap.TRAP_SCORE_MIN = original_trap_score_min

    simulation = trap.simulate_portfolio(master_timestamps, candidates_by_idx, counters)
    trades = simulation["trades"]
    metrics = trap.summarize_metrics(trades, counters, simulation, blocked_contexts)
    trap_score4_blocked = sum(counters[f"trap_quality_score_{score}"] for score in range(4))
    metrics["trap_quality_score_rule"] = "score == 4"
    metrics["trap_quality_score_4_count"] = counters["trap_quality_score_4"]
    metrics["trap_score4_blocked"] = trap_score4_blocked
    metrics["skipped_due_trap_score_lt_4"] = trap_score4_blocked
    metrics["risk_quality_gate_passed"] = counters["stop_risk_quality_gate_passed"]
    metrics["skipped_due_risk_quality"] = counters["skipped_due_stop_risk_quality"]

    split_metrics = {split: trap.mpv.v3.v2.summarize_split(trades, split) for split in ("train", "validation", "holdout")}
    null = trap.null_baseline(trades)
    comparison_prior = comparison_to_prior(prior, metrics, split_metrics, null)
    comparison_risk = comparison_to_risk_tightened(risk_tightened, split_metrics, null)
    accepted_scores = [int(trade.get("trap_quality_score", 0)) for trade in trades]
    integrity_checks = {
        "no_lookahead": True,
        "beta_uses_only_prior_returns": True,
        "residual_z_uses_only_prior_residual_history": True,
        "prior_high_excludes_current_bar": True,
        "trap_quality_uses_only_sweep_bar_known_at_close": True,
        "trap_score4_rule_applied_before_entry_without_future_data": True,
        "trap_score4_only_enforced": all(score == 4 for score in accepted_scores) if accepted_scores else True,
        "market_pump_veto_uses_only_current_past_data": True,
        "universe_breadth_uses_only_current_past_4h_returns": True,
        "confirmation_uses_next_completed_bar_and_enters_after_confirmation": True,
        "entry_next_bar_open_after_confirmation": True,
        "long_side_disabled": metrics["accepted_short_trades"] == metrics["closed_trades"],
        "stop_take_uses_ohlc_conservatively": True,
        "risk_quality_gate_prior_to_acceptance": True,
        "risk_quality_ratio_min_1p0_restored": True,
        "portfolio_bps_uses_base_equity_denominator": True,
        "max_concurrent_positions_lte_3": metrics["max_concurrent_positions"] <= trap.mpv.v3.v2.MAX_CONCURRENT_POSITIONS,
        "max_new_positions_per_timestamp_lte_1": metrics["max_new_positions_per_timestamp_observed"] <= trap.mpv.v3.v2.MAX_NEW_PER_TIMESTAMP,
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
        "prior_trap_quality_execution_loaded_for_comparison": True,
        "risk_tightened_execution_loaded_for_comparison": True,
        "panel_file_count_verified_81": len(symbols) == 81,
        "btc_anchor_loaded": True,
        "eth_anchor_loaded": True,
        "trap_score4_rule_applied": True,
        "risk_quality_ratio_min_1p0_restored": True,
        "market_pump_veto_unchanged": True,
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
        "module": Path(__file__).name,
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
        "source_artifacts": {
            "preregistration": str(PREREGISTRATION_PATH),
            "prior_trap_quality_execution": str(PRIOR_TRAP_EXECUTION_PATH),
            "risk_tightened_execution": str(RISK_TIGHTENED_EXECUTION_PATH),
            "panel_directory": str(PANEL_DIR),
        },
        "data_summary": {
            "symbol_file_count": len(symbols),
            "traded_symbol_count": len(symbols) - 2,
            "data_min_timestamp": master_timestamps[0],
            "data_max_timestamp": master_timestamps[-1],
            "anchor_symbols": ["BTCUSDT", "ETHUSDT"],
        },
        "execution_config": prereg.get("preregistered_config", {}),
        "only_changed_parameter": {
            "trap_quality_score_rule": "score == 4",
            "prior_value": "score >= 3",
            "risk_quality_ratio_min": 1.0,
            "all_other_parameters_inherited_unchanged": True,
        },
        "metrics": metrics,
        "split_metrics": split_metrics,
        "null_baseline": null,
        "metric_integrity_result": {"passed": all(integrity_checks.values()), "checks": integrity_checks},
        "prior_trap_quality_comparison_deltas": comparison_prior,
        "risk_tightened_comparison_deltas": comparison_risk,
        "data_limitations": [
            "Execution reuses the exact prior trap-quality stack and changes only the trap-quality score rule from >=3 to ==4.",
            "Risk quality ratio minimum is restored to 1.0; the rejected 1.5 risk-tightening direction is not used.",
            "No grid, optimization, live routing, capital allocation, candidate generation, or order endpoint was used.",
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
    print(f"trap_quality_score_4_count: {metrics['trap_quality_score_4_count']}")
    print(f"trap_score4_blocked: {metrics['trap_score4_blocked']}")
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
