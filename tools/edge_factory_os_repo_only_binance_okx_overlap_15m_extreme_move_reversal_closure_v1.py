import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_15m_extreme_move_reversal_closure_v1.py"
ARTIFACT_PATH = "artifacts/strategy_closures/binance_okx_overlap_15m_extreme_move_reversal_closure_v1.json"
STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_15M_EXTREME_MOVE_REVERSAL_CLOSURE_CREATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_15M_EXTREME_MOVE_REVERSAL_CLOSURE_RECORD"

EVALUATOR_PATH = "artifacts/strategy_evaluations/binance_okx_overlap_15m_extreme_move_reversal_evaluator_v1.json"
EXECUTION_PATH = "artifacts/strategy_executions/binance_okx_overlap_15m_extreme_move_reversal_execution_v1.json"
EVALUATOR_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_15M_EXTREME_MOVE_REVERSAL_EVALUATED"
EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_15M_EXTREME_MOVE_REVERSAL_EXECUTED"
EVALUATOR_PAYLOAD_HASH = "df5e4b604847efbf7aae4aef6149eda4b9ddec1087e5401bc9f65935a85f0b48"
EXECUTION_PAYLOAD_HASH = "337b50700395531f4065953b423a6bea3d17bfa5b735d642c598690f3d942db4"

ROUTE_FAMILY = "BINANCE_OKX_OVERLAP_15M_EXTREME_MOVE_REVERSAL_BASELINE"
CONFIG_ID = "extreme4h_5pct_reversal_hold8h"
PROMISING_CLASS = "EXTREME_MOVE_REVERSAL_15M_DIAGNOSTIC_PROMISING_REQUIRES_CLOSURE_NO_CANDIDATE_NO_EDGE"
REJECTED_CLASS = "EXTREME_MOVE_REVERSAL_15M_REJECTED_NO_FOLLOWUP"
INCONCLUSIVE_CLASS = "EXTREME_MOVE_REVERSAL_15M_INCONCLUSIVE_INPUT_INCOMPLETE_NO_FOLLOWUP"
INVALIDATED_CLASS = "EXTREME_MOVE_REVERSAL_15M_INVALIDATED_BY_SAFETY_OR_INTEGRITY_FAILURE"


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


def closure_state_for_result(result_class: str) -> str:
    if result_class == PROMISING_CLASS:
        return "CLOSED_DIAGNOSTIC_PROMISING_NO_CANDIDATE_NO_EDGE_NO_RELEASE"
    if result_class == REJECTED_CLASS:
        return "CLOSED_REJECTED_NO_FOLLOWUP"
    if result_class == INCONCLUSIVE_CLASS:
        return "CLOSED_INCONCLUSIVE_NO_FOLLOWUP"
    if result_class == INVALIDATED_CLASS:
        return "CLOSED_INVALIDATED_BY_SAFETY_OR_INTEGRITY_FAILURE"
    raise RuntimeError(f"unexpected evaluator result class: {result_class}")


def build_closure() -> Dict[str, Any]:
    evaluator = read_json(EVALUATOR_PATH)
    execution = read_json(EXECUTION_PATH)
    evaluator_hash = verify_hash(evaluator, EVALUATOR_PAYLOAD_HASH)
    execution_hash = verify_hash(execution, EXECUTION_PAYLOAD_HASH)
    if evaluator.get("status") != EVALUATOR_STATUS:
        raise RuntimeError("evaluator status mismatch")
    if execution.get("status") != EXECUTION_STATUS:
        raise RuntimeError("execution status mismatch")
    if execution.get("route_family") != ROUTE_FAMILY or execution.get("config_id") != CONFIG_ID:
        raise RuntimeError("execution route/config mismatch")

    classification = evaluator["result_classification"]
    prior_execution = evaluator["prior_execution_preserved"]
    result_class = classification["result_class"]
    diagnostic_promising = classification["diagnostic_promising"]
    closure_state = closure_state_for_result(result_class)
    closure_reason = (
        f"The 15m extreme-move reversal route is closed with result_class={result_class}. "
        f"Validation gross metric was {classification['validation_gross_metric_bps']} bps and validation net metric was "
        f"{classification['validation_net_metric_bps']} bps. validation_positive_after_cost="
        f"{classification['validation_positive_after_cost']}, null_baseline_passed="
        f"{classification['null_baseline_review_passed']}, monthly_stability_passed="
        f"{classification['monthly_stability_review_passed']}, event_coverage_passed="
        f"{classification['event_coverage_review_passed']}, turnover_concentration_passed="
        f"{classification['turnover_concentration_review_passed']}, metric_integrity_issue_count="
        f"{classification['metric_integrity_issue_count']}. This closure grants no candidate, edge claim, family release, "
        "holdout access, or runtime/live/capital permission."
    )

    payload: Dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "prior_evaluator_result_preserved": {
            "path": EVALUATOR_PATH,
            "status": evaluator["status"],
            "payload_sha256_excluding_hash": evaluator_hash,
            "result_class": result_class,
            "diagnostic_promising": diagnostic_promising,
            "config_id": CONFIG_ID,
            "validation_gross_metric_bps": classification["validation_gross_metric_bps"],
            "validation_net_metric_bps": classification["validation_net_metric_bps"],
            "validation_positive_after_cost": classification["validation_positive_after_cost"],
            "null_baseline_review_passed": classification["null_baseline_review_passed"],
            "monthly_stability_review_passed": classification["monthly_stability_review_passed"],
            "event_coverage_review_passed": classification["event_coverage_review_passed"],
            "turnover_concentration_review_passed": classification["turnover_concentration_review_passed"],
            "metric_integrity_issue_count": classification["metric_integrity_issue_count"],
            "metric_integrity_passed": classification["metric_integrity_passed"],
            "safety_review_passed": classification["safety_review_passed"],
            "closure_record_required_next": classification["closure_record_required_next"],
        },
        "prior_execution_result_preserved": {
            "path": EXECUTION_PATH,
            "status": execution["status"],
            "payload_sha256_excluding_hash": execution_hash,
            "route_family": execution["route_family"],
            "config_id": execution["config_id"],
            "train_gross_metric_bps": prior_execution["train_gross_metric_bps"],
            "train_net_metric_bps": prior_execution["train_net_metric_bps"],
            "validation_gross_metric_bps": prior_execution["validation_gross_metric_bps"],
            "validation_net_metric_bps": prior_execution["validation_net_metric_bps"],
            "holdout_gross_metric_bps": prior_execution["holdout_gross_metric_bps"],
            "holdout_net_metric_bps": prior_execution["holdout_net_metric_bps"],
            "train_event_count": prior_execution["train_event_count"],
            "validation_event_count": prior_execution["validation_event_count"],
            "holdout_event_count": prior_execution["holdout_event_count"],
            "holdout_used_for_config_selection": prior_execution["holdout_used_for_config_selection"],
            "long_validation_event_count": execution["long_short_side_summary"]["long_validation_event_count"],
            "short_validation_event_count": execution["long_short_side_summary"]["short_validation_event_count"],
            "long_validation_net_metric_bps": execution["long_short_side_summary"]["long_validation_net_metric_bps"],
            "short_validation_net_metric_bps": execution["long_short_side_summary"]["short_validation_net_metric_bps"],
            "top_symbol_event_share": execution["event_coverage_summary"]["top_symbol_event_share"],
            "execution_result_is_diagnostic_only": execution["diagnostic_interpretation_limits"]["diagnostic_execution_only"],
        },
        "closure_record": {
            "closure_record_created": True,
            "closure_type": "EXTREME_MOVE_REVERSAL_15M_CLOSURE_AFTER_EVALUATOR",
            "closure_state": closure_state,
            "route_closed": True,
            "route_family_closed": ROUTE_FAMILY,
            "config_id": CONFIG_ID,
            "result_class_preserved_exactly": result_class,
            "diagnostic_promising": diagnostic_promising,
            "closure_reason": closure_reason,
            "retest_allowed_now": False,
            "parameter_expansion_allowed_now": False,
            "strategy_search_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "holdout_access_allowed_now": False,
            "runtime_live_capital_allowed_now": False,
            "next_immediate_module_required": False,
            "project_can_pause_after_closure": True,
            "closure_grants_no_candidate": True,
            "closure_grants_no_edge_claim": True,
            "closure_grants_no_release": True,
            "closure_grants_no_holdout_permission": True,
            "closure_grants_no_runtime_live_capital": True,
        },
        "route_family_state_after_closure": {
            "route_family": ROUTE_FAMILY,
            "route_closed": True,
            "route_state": closure_state,
            "final_result_class": result_class,
            "diagnostic_promising": diagnostic_promising,
            "no_automatic_retest": True,
            "no_parameter_expansion": True,
        },
        "project_state_after_closure": {
            "active_candidate": False,
            "edge_claim": False,
            "family_release": False,
            "holdout_permission": False,
            "runtime_live_capital": False,
            "next_immediate_module_required": False,
            "project_can_pause_after_closure": True,
        },
        "followup_permissions_after_closure": {
            "retest_allowed_now": False,
            "parameter_expansion_allowed_now": False,
            "strategy_search_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "holdout_access_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "runtime_live_capital_allowed_now": False,
        },
        "forbidden_actions_confirmed_false": {
            "evaluator_rerun": False,
            "execution_rerun": False,
            "panel_rows_read": False,
            "network_used": False,
            "api_called": False,
            "candidate_generation": False,
            "edge_claim": False,
            "family_release": False,
            "holdout_access": False,
            "runtime_live_capital": False,
        },
        "validation_checks": {
            "status_equals_required_status": True,
            "artifact_kind_equals_required": True,
            "module_path_equals_required": True,
            "artifact_path_equals_required": True,
            "evaluator_loaded": True,
            "evaluator_status_verified": True,
            "evaluator_payload_hash_verified": True,
            "execution_loaded": True,
            "execution_status_verified": True,
            "execution_payload_hash_verified": True,
            "result_class_preserved_exactly": True,
            "holdout_used_for_config_selection_false": True,
            "route_closed_true": True,
            "no_evaluator_rerun": True,
            "no_execution_rerun": True,
            "no_panel_rows_read": True,
            "no_network_used": True,
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
    assert payload["prior_evaluator_result_preserved"]["result_class"] == result_class
    assert payload["closure_record"]["route_closed"] is True
    assert payload["closure_record"]["candidate_generation_allowed_now"] is False
    assert payload["closure_record"]["edge_claim_allowed_now"] is False
    assert payload["closure_record"]["runtime_live_capital_allowed_now"] is False
    assert payload["prior_execution_result_preserved"]["holdout_used_for_config_selection"] is False
    assert payload["replacement_checks_all_true"] is True
    assert all(payload["validation_checks"].values())
    assert canonical_payload_hash(payload) == payload["payload_sha256_excluding_hash"]
    return payload


def main() -> None:
    artifact_path = REPO_ROOT / ARTIFACT_PATH
    if artifact_path.exists():
        raise RuntimeError(f"closure artifact already exists: {ARTIFACT_PATH}")
    payload = build_closure()
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": STATUS,
        "artifact_path": ARTIFACT_PATH,
        "result_class": payload["prior_evaluator_result_preserved"]["result_class"],
        "diagnostic_promising": payload["prior_evaluator_result_preserved"]["diagnostic_promising"],
        "route_closed": payload["closure_record"]["route_closed"],
        "config_id": CONFIG_ID,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "payload_sha256_excluding_hash": payload["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": True,
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
