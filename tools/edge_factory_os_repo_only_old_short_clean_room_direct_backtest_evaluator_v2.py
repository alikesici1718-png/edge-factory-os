from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXECUTION_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "old_short_clean_room_direct_backtest_execution_v2.json"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_evaluations" / "old_short_clean_room_direct_backtest_evaluator_v2.json"

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_V2_EVALUATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_V2_EVALUATION"
ROUTE_KEY = "old_short_clean_room_v1"
EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_V2_EXECUTED"

PROMISING = "OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_V2_DIAGNOSTIC_PROMISING_NO_EDGE_NO_LIVE"
REJECTED = "OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_V2_REJECTED_NO_FOLLOWUP"
INCONCLUSIVE = "OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_V2_INCONCLUSIVE_NEEDS_MORE_DATA"
INVALIDATED = "OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_V2_INVALIDATED_BY_DATA_OR_INTEGRITY_FAILURE"


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def payload_hash(data: dict[str, Any]) -> str:
    clone = dict(data)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def git(args: list[str]) -> str:
    completed = subprocess.run(["git", "-C", str(REPO_ROOT), *args], check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def tracked_python_count() -> int:
    return len([line for line in git(["ls-files", "*.py"]).splitlines() if line.strip()])


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def gt(value: Any, threshold: float) -> bool:
    return is_number(value) and value > threshold


def gte(value: Any, threshold: float) -> bool:
    return is_number(value) and value >= threshold


def main() -> int:
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status = {
        "?? tools/edge_factory_os_repo_only_old_short_clean_room_direct_backtest_evaluator_v2.py",
        "?? artifacts/strategy_evaluations/old_short_clean_room_direct_backtest_evaluator_v2.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]
    execution = load_json(EXECUTION_PATH)
    mode_results = execution.get("mode_results", {})
    mode_a = mode_results.get("MODE_A_PROXY_GATE_CONSERVATIVE", {})
    mode_b = mode_results.get("MODE_B_NO_GATE_UPPER_BOUND_DIAGNOSTIC", {})
    mode_a_validation = mode_a.get("split_metrics", {}).get("validation", {})
    mode_a_holdout = mode_a.get("split_metrics", {}).get("holdout", {})
    accounting_integrity = execution.get("accounting_integrity_result", {})
    gate_limit = execution.get("gate_limitation_result", {})
    safety_permissions = execution.get("safety_permissions", {})

    validation_closed = mode_a_validation.get("closed_trades", 0)
    criteria = {
        "mode_a_validation_portfolio_net_bps_positive": gt(mode_a_validation.get("portfolio_net_bps"), 0),
        "mode_a_holdout_portfolio_net_bps_positive": gt(mode_a_holdout.get("portfolio_net_bps"), 0),
        "validation_monthly_positive_rate_gte_0_60": gte(mode_a_validation.get("monthly_positive_rate"), 0.60),
        "holdout_monthly_positive_rate_gte_0_50": gte(mode_a_holdout.get("monthly_positive_rate"), 0.50),
        "validation_closed_trades_gte_30": isinstance(validation_closed, int) and validation_closed >= 30,
        "null_baseline_passes": mode_a.get("null_baseline", {}).get("null_pass") is True,
        "top_symbol_share_lte_0_25": gte(0.25, mode_a.get("symbol_concentration", {}).get("top_symbol_share", 1.0)),
        "worst_month_gt_minus_1000_bps": gt(mode_a.get("worst_month_bps"), -1000.0),
        "metric_integrity_passes": accounting_integrity.get("passed") is True,
        "no_exact_gate_replay_false_claim": gate_limit.get("exact_gate_replay_recovered") is False
        and gate_limit.get("mode_a_proxy_gate_not_exact_replay") is True,
        "no_edge_live_capital_permission": all(value is False for value in safety_permissions.values()),
    }
    diagnostic_promising = all(criteria.values())
    invalidated_reasons = []
    if execution.get("status") != EXECUTION_STATUS:
        invalidated_reasons.append("execution_status_mismatch")
    if execution.get("route_key") != ROUTE_KEY:
        invalidated_reasons.append("route_key_mismatch")
    if execution.get("replacement_checks_all_true") is not True:
        invalidated_reasons.append("execution_replacement_checks_not_true")
    if accounting_integrity.get("passed") is not True:
        invalidated_reasons.append("accounting_integrity_failed")
    if mode_a.get("max_concurrent_positions", 999) > 3:
        invalidated_reasons.append("mode_a_max_concurrent_positions_exceeded")
    if not criteria["no_exact_gate_replay_false_claim"]:
        invalidated_reasons.append("exact_gate_replay_false_claim")
    if invalidated_reasons:
        result_class = INVALIDATED
    elif validation_closed < 30:
        result_class = INCONCLUSIVE
    elif diagnostic_promising:
        result_class = PROMISING
    else:
        result_class = REJECTED

    metric_integrity_result = {
        "passed": not invalidated_reasons,
        "invalidated_reasons": invalidated_reasons,
        "accounting_integrity": accounting_integrity,
        "mode_a_max_concurrent_positions": mode_a.get("max_concurrent_positions"),
        "mode_a_same_symbol_overlap_block_count": mode_a.get("same_symbol_overlap_block_count"),
        "mode_a_proxy_gate_capacity_block_count": mode_a.get("proxy_gate_capacity_block_count"),
    }
    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": "edge_factory_os_repo_only_old_short_clean_room_direct_backtest_evaluator_v2",
        "route_key": ROUTE_KEY,
        "source_checkpoint": {
            "actual_head": git(["rev-parse", "HEAD"]),
            "tracked_python_count": tracked_python_count(),
            "repo_clean_before_run": not unexpected_status,
            "git_status_at_evaluation": status_lines,
            "allowed_new_paths_at_evaluation": sorted(allowed_status),
            "unexpected_dirty_paths_at_evaluation": unexpected_status,
        },
        "source_artifacts": {
            "execution_v2": str(EXECUTION_PATH),
        },
        "primary_mode": "MODE_A_PROXY_GATE_CONSERVATIVE",
        "mode_b_informational_only": True,
        "mode_a_summary": {
            "validation_portfolio_net_bps": mode_a_validation.get("portfolio_net_bps"),
            "holdout_portfolio_net_bps": mode_a_holdout.get("portfolio_net_bps"),
            "validation_monthly_positive_rate": mode_a_validation.get("monthly_positive_rate"),
            "holdout_monthly_positive_rate": mode_a_holdout.get("monthly_positive_rate"),
            "validation_closed_trades": validation_closed,
            "closed_trades": mode_a.get("closed_trades"),
            "worst_month_bps": mode_a.get("worst_month_bps"),
            "top_symbol_concentration": mode_a.get("symbol_concentration"),
            "null_baseline": mode_a.get("null_baseline"),
        },
        "mode_b_informational_summary": {
            "portfolio_net_bps": mode_b.get("portfolio_net_bps"),
            "closed_trades": mode_b.get("closed_trades"),
            "eligible_for_diagnostic_promising": mode_b.get("eligible_for_diagnostic_promising"),
        },
        "diagnostic_promising": diagnostic_promising,
        "diagnostic_promising_criteria": criteria,
        "result_classification": result_class,
        "metric_integrity_result": metric_integrity_result,
        "null_baseline_result": mode_a.get("null_baseline"),
        "gate_limitation_result": gate_limit,
        "limitations": execution.get("limitations", []),
        "safety_permissions": {
            "live_trading_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "monitor_allowed_now": False,
            "capital_allocation_allowed_now": False,
            "real_orders_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
        },
        "validation_checks": {
            "repo_clean_before_run": not unexpected_status,
            "execution_v2_loaded": True,
            "execution_status_verified": execution.get("status") == EXECUTION_STATUS,
            "route_key_verified": execution.get("route_key") == ROUTE_KEY,
            "mode_a_primary": True,
            "mode_b_informational_only": True,
            "no_backtest_rerun": True,
            "no_threshold_optimization": True,
            "no_network_used": True,
            "no_api_used": True,
            "no_runtime_live_capital": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
        },
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }
    artifact["replacement_checks_all_true"] = all(artifact["validation_checks"].values()) and all(
        value is False for value in artifact["safety_permissions"].values()
    )
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")
    print(f"status: {STATUS}")
    print(f"route_key: {ROUTE_KEY}")
    print(f"result_classification: {result_class}")
    print(f"diagnostic_promising: {str(diagnostic_promising).lower()}")
    print(f"mode_a_validation_portfolio_net_bps: {mode_a_validation.get('portfolio_net_bps')}")
    print(f"mode_a_holdout_portfolio_net_bps: {mode_a_holdout.get('portfolio_net_bps')}")
    print(f"mode_a_validation_closed_trades: {validation_closed}")
    print(f"accounting_integrity_result: {str(accounting_integrity.get('passed') is True).lower()}")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
