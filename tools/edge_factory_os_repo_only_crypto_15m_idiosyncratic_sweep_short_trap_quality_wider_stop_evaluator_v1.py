from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXECUTION_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_idiosyncratic_sweep_short_trap_quality_wider_stop_execution_v1.json"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_evaluations" / "crypto_15m_idiosyncratic_sweep_short_trap_quality_wider_stop_evaluator_v1.json"

STATUS = "PASS_REPO_ONLY_CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_WIDER_STOP_EVALUATED"
ARTIFACT_KIND = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_WIDER_STOP_EVALUATION"
STRATEGY = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_WIDER_STOP_V2"
ROUTE_FAMILY = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_WIDER_STOP_BASELINE"
CONFIG_ID = "crypto_15m_idiosyncratic_sweep_short_trap_quality_wider_stop_1atr_v2"
EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_WIDER_STOP_EXECUTED"

PROMISING = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_WIDER_STOP_DIAGNOSTIC_PROMISING_NO_EDGE_NO_LIVE"
REJECTED = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_WIDER_STOP_REJECTED_NO_FOLLOWUP"
INCONCLUSIVE = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_WIDER_STOP_INCONCLUSIVE_NEEDS_MORE_DATA"
INVALIDATED = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_WIDER_STOP_INVALIDATED_BY_DATA_OR_INTEGRITY_FAILURE"


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


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def main() -> int:
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status = {
        "?? tools/edge_factory_os_repo_only_crypto_15m_idiosyncratic_sweep_short_trap_quality_wider_stop_evaluator_v1.py",
        "?? artifacts/strategy_evaluations/crypto_15m_idiosyncratic_sweep_short_trap_quality_wider_stop_evaluator_v1.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]

    execution = load_json(EXECUTION_PATH)
    metrics = execution.get("metrics", {})
    split = execution.get("split_metrics", {})
    validation = split.get("validation", {})
    holdout = split.get("holdout", {})
    null = execution.get("null_baseline", {})
    integrity = execution.get("metric_integrity_result", {})
    safety = execution.get("safety_permissions", {})
    top_share = metrics.get("top_symbol_concentration", {}).get("top_symbol_trade_share")
    worst_month = metrics.get("worst_month_bps")

    criteria = {
        "validation_portfolio_net_bps_positive": is_number(validation.get("portfolio_net_bps")) and validation["portfolio_net_bps"] > 0,
        "holdout_portfolio_net_bps_positive": is_number(holdout.get("portfolio_net_bps")) and holdout["portfolio_net_bps"] > 0,
        "validation_monthly_positive_rate_gte_0_60": is_number(validation.get("monthly_positive_rate")) and validation["monthly_positive_rate"] >= 0.60,
        "holdout_monthly_positive_rate_gte_0_50": is_number(holdout.get("monthly_positive_rate")) and holdout["monthly_positive_rate"] >= 0.50,
        "validation_closed_trades_gte_30": isinstance(validation.get("closed_trades"), int) and validation["closed_trades"] >= 30,
        "null_baseline_passes": null.get("null_pass") is True,
        "top_symbol_trade_share_lte_0_25": is_number(top_share) and top_share <= 0.25,
        "worst_month_gt_minus_1000_bps": is_number(worst_month) and worst_month > -1000.0,
        "metric_integrity_passes": integrity.get("passed") is True,
        "no_candidate_edge_live_capital": all(value is False for value in safety.values()),
    }

    invalidated_reasons = []
    if execution.get("status") != EXECUTION_STATUS:
        invalidated_reasons.append("execution_status_mismatch")
    if execution.get("strategy") != STRATEGY or execution.get("route_family") != ROUTE_FAMILY:
        invalidated_reasons.append("strategy_or_route_family_mismatch")
    if execution.get("config_id") != CONFIG_ID:
        invalidated_reasons.append("config_id_mismatch")
    if execution.get("replacement_checks_all_true") is not True:
        invalidated_reasons.append("execution_replacement_checks_not_true")
    if integrity.get("passed") is not True:
        invalidated_reasons.append("metric_integrity_failed")
    if metrics.get("trap_quality_score_rule") != "score >= 3":
        invalidated_reasons.append("trap_quality_score_rule_not_score_gte_3")
    if metrics.get("stop_buffer_atr") != 1.0:
        invalidated_reasons.append("stop_buffer_atr_not_1p0")

    if invalidated_reasons:
        result = INVALIDATED
    elif validation.get("closed_trades", 0) < 30:
        result = INCONCLUSIVE
    elif all(criteria.values()):
        result = PROMISING
    else:
        result = REJECTED
    diagnostic_promising = result == PROMISING

    evaluator_safety = {
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "live_permission_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "monitor_allowed_now": False,
        "capital_permission_allowed_now": False,
        "real_orders_allowed_now": False,
        "family_release_allowed_now": False,
    }
    checks = {
        "repo_clean_before_run": not unexpected_status,
        "execution_artifact_loaded": True,
        "execution_status_verified": execution.get("status") == EXECUTION_STATUS,
        "strategy_verified": execution.get("strategy") == STRATEGY,
        "route_family_verified": execution.get("route_family") == ROUTE_FAMILY,
        "config_id_verified": execution.get("config_id") == CONFIG_ID,
        "trap_quality_score_rule_verified": metrics.get("trap_quality_score_rule") == "score >= 3",
        "stop_buffer_atr_1p0_verified": metrics.get("stop_buffer_atr") == 1.0,
        "wider_stop_valid_count_metric_present": metrics.get("wider_stop_valid_count") is not None,
        "no_backtest_rerun": True,
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
            "git_status_at_evaluation": status_lines,
            "allowed_new_paths_at_evaluation": sorted(allowed_status),
            "unexpected_dirty_paths_at_evaluation": unexpected_status,
        },
        "source_artifacts": {"execution": str(EXECUTION_PATH)},
        "execution_status_preserved": execution.get("status"),
        "execution_metric_summary": {
            "wider_stop_valid_count": metrics.get("wider_stop_valid_count"),
            "stop_buffer_atr": metrics.get("stop_buffer_atr"),
            "confirmation_quality_passed_count": metrics.get("confirmation_quality_passed_count"),
            "market_pump_veto_blocked": metrics.get("market_pump_veto_blocked"),
            "accepted_short_trades": metrics.get("accepted_short_trades"),
            "closed_trades": metrics.get("closed_trades"),
            "validation_closed_trades": validation.get("closed_trades"),
            "holdout_closed_trades": holdout.get("closed_trades"),
            "validation_net_bps": validation.get("portfolio_net_bps"),
            "holdout_net_bps": holdout.get("portfolio_net_bps"),
            "validation_monthly_positive_rate": validation.get("monthly_positive_rate"),
            "holdout_monthly_positive_rate": holdout.get("monthly_positive_rate"),
            "worst_month_bps": metrics.get("worst_month_bps"),
            "max_drawdown_bps": metrics.get("max_drawdown_bps"),
            "stop_exit_count": metrics.get("stop_exit_count"),
            "take_profit_exit_count": metrics.get("take_profit_exit_count"),
            "time_stop_exit_count": metrics.get("time_stop_exit_count"),
            "top_symbol_concentration": metrics.get("top_symbol_concentration"),
            "null_baseline": null,
            "comparison_deltas_versus_prior_trap_quality": execution.get("prior_trap_quality_comparison_deltas"),
            "comparison_deltas_versus_risk_tightened": execution.get("risk_tightened_comparison_deltas"),
            "comparison_deltas_versus_trap_score4": execution.get("trap_score4_comparison_deltas"),
        },
        "diagnostic_promising": diagnostic_promising,
        "diagnostic_promising_criteria": criteria,
        "result_classification": result,
        "metric_integrity_result": {
            "passed": not invalidated_reasons and integrity.get("passed") is True,
            "invalidated_reasons": invalidated_reasons,
            "execution_integrity": integrity,
        },
        "safety_permissions": evaluator_safety,
        "validation_checks": checks,
        "replacement_checks_all_true": all(checks.values()) and all(value is False for value in evaluator_safety.values()),
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")

    print(f"status: {STATUS}")
    print(f"strategy: {STRATEGY}")
    print(f"result_classification: {result}")
    print(f"diagnostic_promising: {str(diagnostic_promising).lower()}")
    print(f"validation_net_bps: {validation.get('portfolio_net_bps')}")
    print(f"holdout_net_bps: {holdout.get('portfolio_net_bps')}")
    print(f"null_pass: {str(null.get('null_pass')).lower()}")
    print(f"metric_integrity_result: {str(artifact['metric_integrity_result']['passed']).lower()}")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
