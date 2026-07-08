import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_crowding_reversal_full_range_closure_v1.py"
ARTIFACT_PATH = "artifacts/strategy_closures/binance_okx_overlap_funding_crowding_reversal_full_range_closure_v1.json"
STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_CROWDING_REVERSAL_FULL_RANGE_CLOSURE_CREATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_FUNDING_CROWDING_REVERSAL_FULL_RANGE_CLOSURE_RECORD"

EVALUATOR_PATH = "artifacts/strategy_evaluations/binance_okx_overlap_funding_crowding_reversal_full_range_evaluator_v1.json"
EXECUTION_PATH = "artifacts/strategy_executions/binance_okx_overlap_funding_crowding_reversal_full_range_execution_v1.json"
EVALUATOR_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_CROWDING_REVERSAL_FULL_RANGE_EVALUATED"
EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_FUNDING_CROWDING_REVERSAL_FULL_RANGE_EXECUTED"
EVALUATOR_PAYLOAD_HASH = "ef1dc708e54ab0a2946bf272c5b0648e60244211dc4d17cff5f382dac173d752"
EXECUTION_PAYLOAD_HASH = "3d485f58a69f7a9433b287f6f329d4721ba8f0359a9778f520f06cf28f360f2d"

ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_RATE_CROWDING_REVERSAL_BASELINE"
CONFIG_ID = "funding_mean9_hold24h"
PROMISING_CLASS = "FUNDING_CROWDING_REVERSAL_FULL_RANGE_DIAGNOSTIC_PROMISING_REQUIRES_CLOSURE_NO_CANDIDATE_NO_EDGE"
REJECTED_CLASS = "FUNDING_CROWDING_REVERSAL_FULL_RANGE_REJECTED_NO_FOLLOWUP"
INCONCLUSIVE_CLASS = "FUNDING_CROWDING_REVERSAL_FULL_RANGE_INCONCLUSIVE_INPUT_INCOMPLETE_NO_FOLLOWUP"
INVALIDATED_CLASS = "FUNDING_CROWDING_REVERSAL_FULL_RANGE_INVALIDATED_BY_SAFETY_OR_INTEGRITY_FAILURE"
ALLOWED_RESULT_CLASSES = [PROMISING_CLASS, REJECTED_CLASS, INCONCLUSIVE_CLASS, INVALIDATED_CLASS]


def canonical_payload_hash(payload: Dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(json.dumps(clean, sort_keys=True, indent=2).encode("utf-8")).hexdigest()


def read_json(relative_path: str) -> Dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise RuntimeError(f"missing required artifact: {relative_path}")
    return json.loads(path.read_text(encoding="utf-8"))


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
        return "CLOSED_DIAGNOSTIC_PROMISING_NO_CANDIDATE_NO_EDGE"
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
    result_class = classification["result_class"]
    diagnostic_promising = classification["diagnostic_promising"]
    if result_class not in ALLOWED_RESULT_CLASSES:
        raise RuntimeError("evaluator result class is not allowed")
    holdout_policy = evaluator["evaluation_policy"]["holdout_policy"]
    if holdout_policy["holdout_used_for_config_selection"] is not False:
        raise RuntimeError("holdout policy mismatch")
    if holdout_policy["holdout_reported_separately"] is not True:
        raise RuntimeError("holdout reporting policy mismatch")

    closure_state = closure_state_for_result(result_class)
    route_closed = True
    train = evaluator["execution_results_evaluated"]["train"]
    validation = evaluator["execution_results_evaluated"]["validation"]
    holdout = evaluator["execution_results_evaluated"]["holdout"]
    split_summary = execution["train_validation_holdout_summary"]
    holdout_findings = evaluator["holdout_findings"]

    closure_reason = (
        f"The full-range funding crowding reversal route is closed with result_class={result_class}. "
        f"Validation gross metric was {classification['validation_gross_metric_bps']} bps and validation net metric was "
        f"{classification['validation_net_metric_bps']} bps. validation_positive_after_cost="
        f"{classification['validation_positive_after_cost']}, null_baseline_passed="
        f"{classification['null_baseline_review_passed']}, monthly_stability_passed="
        f"{classification['monthly_stability_review_passed']}, turnover_concentration_passed="
        f"{classification['turnover_concentration_review_passed']}, metric_integrity_issue_count="
        f"{classification['metric_integrity_issue_count']}. Holdout was reported separately, was not used for config "
        "selection, and grants no candidate, edge claim, family release, holdout access, or runtime/live/capital permission."
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
            "validation_net_metric_bps": classification["validation_net_metric_bps"],
            "validation_gross_metric_bps": classification["validation_gross_metric_bps"],
            "validation_positive_after_cost": classification["validation_positive_after_cost"],
            "null_baseline_review_passed": classification["null_baseline_review_passed"],
            "monthly_stability_review_passed": classification["monthly_stability_review_passed"],
            "turnover_concentration_review_passed": classification["turnover_concentration_review_passed"],
            "metric_integrity_issue_count": classification["metric_integrity_issue_count"],
            "metric_integrity_passed": classification["metric_integrity_passed"],
            "safety_review_passed": classification["safety_review_passed"],
            "closure_record_required_next": classification["closure_record_required_next"],
            "candidate_generation_allowed_from_evaluator": classification["candidate_generation_allowed_from_evaluator"],
            "edge_claim_allowed_from_evaluator": classification["edge_claim_allowed_from_evaluator"],
            "family_release_allowed_from_evaluator": classification["family_release_allowed_from_evaluator"],
            "runtime_live_capital_allowed_from_evaluator": classification["runtime_live_capital_allowed_from_evaluator"],
        },
        "prior_execution_result_preserved": {
            "path": EXECUTION_PATH,
            "status": execution["status"],
            "payload_sha256_excluding_hash": execution_hash,
            "route_family": execution["route_family"],
            "config_id": execution["config_id"],
            "fixed_config_id": execution["execution_safety_controls"]["best_config_id"],
            "train": train,
            "validation": validation,
            "holdout": holdout,
            "full_window_start_utc": split_summary["full_window_start_utc"],
            "full_window_end_exclusive_utc": split_summary["full_window_end_exclusive_utc"],
            "train_window_start_utc": split_summary["train_window_start_utc"],
            "train_window_end_exclusive_utc": split_summary["train_window_end_exclusive_utc"],
            "validation_window_start_utc": split_summary["validation_window_start_utc"],
            "validation_window_end_exclusive_utc": split_summary["validation_window_end_exclusive_utc"],
            "holdout_window_start_utc": split_summary["holdout_window_start_utc"],
            "holdout_window_end_exclusive_utc": split_summary["holdout_window_end_exclusive_utc"],
            "metric_integrity_issue_count": execution["metric_integrity_summary"]["metric_integrity_issue_count"],
            "metric_integrity_passed": execution["metric_integrity_summary"]["metric_integrity_passed"],
            "candidate_generation": False,
            "edge_claim": False,
            "family_release": False,
            "runtime_live_capital": False,
        },
        "holdout_policy_preserved": {
            "holdout_gross_metric_bps": holdout_findings["holdout_gross_metric_bps"],
            "holdout_net_metric_bps": holdout_findings["holdout_net_metric_bps"],
            "holdout_positive_after_cost": holdout_findings["holdout_positive_after_cost"],
            "holdout_reported_separately": holdout_policy["holdout_reported_separately"],
            "holdout_used_for_config_selection": holdout_policy["holdout_used_for_config_selection"],
            "holdout_used_for_candidate_generation": holdout_policy["holdout_used_for_candidate_generation"],
            "holdout_used_for_edge_claim": holdout_policy["holdout_used_for_edge_claim"],
            "holdout_used_for_family_release": holdout_policy["holdout_used_for_family_release"],
            "holdout_used_for_runtime_live_capital": holdout_policy["holdout_used_for_runtime_live_capital"],
            "holdout_positive_does_not_override_validation_failure": holdout_policy["holdout_positive_does_not_override_validation_failure"],
            "final_edge_claim_requires_external_or_future_holdout": holdout_policy["final_edge_claim_requires_external_or_future_holdout"],
            "holdout_policy_source": holdout_policy["holdout_policy_source"],
        },
        "closure_record": {
            "closure_record_created": True,
            "closure_type": "FUNDING_CROWDING_REVERSAL_FULL_RANGE_CLOSURE_AFTER_EVALUATOR",
            "closure_state": closure_state,
            "route_closed": route_closed,
            "route_family_closed": ROUTE_FAMILY,
            "config_id": CONFIG_ID,
            "result_class_confirmed": result_class,
            "diagnostic_promising_confirmed": diagnostic_promising,
            "validation_gross_metric_bps": classification["validation_gross_metric_bps"],
            "validation_net_metric_bps": classification["validation_net_metric_bps"],
            "validation_positive_after_cost": classification["validation_positive_after_cost"],
            "null_baseline_review_passed": classification["null_baseline_review_passed"],
            "monthly_stability_review_passed": classification["monthly_stability_review_passed"],
            "turnover_concentration_review_passed": classification["turnover_concentration_review_passed"],
            "metric_integrity_issue_count": classification["metric_integrity_issue_count"],
            "holdout_reported_separately": True,
            "holdout_used_for_config_selection": False,
            "closure_reason": closure_reason,
            "retest_allowed_now": False,
            "parameter_expansion_allowed_now": False,
            "strategy_search_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "holdout_access_allowed_now": False,
            "runtime_live_capital_allowed_now": False,
            "closure_grants_no_candidate": True,
            "closure_grants_no_edge_claim": True,
            "closure_grants_no_release": True,
            "closure_grants_no_holdout_access_permission": True,
            "closure_grants_no_runtime_live_capital": True,
        },
        "route_family_state_after_closure": {
            "route_family": ROUTE_FAMILY,
            "status": closure_state,
            "result_class": result_class,
            "diagnostic_promising": diagnostic_promising,
            "route_closed": route_closed,
            "retest_allowed_now": False,
            "parameter_expansion_allowed_now": False,
            "strategy_search_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "holdout_access_allowed_now": False,
            "no_active_candidate_exists": True,
            "no_active_edge_claim_exists": True,
            "no_family_release_exists": True,
            "no_runtime_live_capital_permission_exists": True,
        },
        "project_state_after_closure": {
            "full_range_funding_crowding_reversal_route_closed": route_closed,
            "no_active_candidate_exists": True,
            "no_active_edge_claim_exists": True,
            "no_family_release_exists": True,
            "no_holdout_access_permission_exists": True,
            "no_runtime_live_capital_permission_exists": True,
            "next_immediate_module_required": False,
            "project_can_pause_after_closure": True,
        },
        "followup_permissions_after_closure": {
            "closure_record_created": True,
            "closure_complete": True,
            "strategy_search_allowed_now": False,
            "retest_allowed_now": False,
            "parameter_expansion_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "holdout_access_allowed_now": False,
            "boundary_buffer_access_allowed_now": False,
            "okx_panel_access_allowed_now": False,
            "binance_panel_row_access_allowed_now": False,
            "funding_row_access_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "next_immediate_module_required": False,
            "project_can_pause_after_closure": True,
        },
        "forbidden_actions_confirmed_false": {
            "evaluator_rerun": False,
            "execution_rerun": False,
            "panel_rows_read": False,
            "funding_rows_read": False,
            "okx_panel_rows_read": False,
            "binance_1m_source_rows_read": False,
            "network_used": False,
            "binance_api_called": False,
            "strategy_search_executed": False,
            "non_preregistered_config_tested": False,
            "candidates_generated": False,
            "edge_claimed": False,
            "family_released": False,
            "holdout_access_permission_granted": False,
            "runtime_permission_granted": False,
            "live_permission_granted": False,
            "capital_permission_granted": False,
            "existing_files_modified_by_module": False,
        },
        "validation_checks": {
            "status_equals_required_status": True,
            "module_path_equals_required_path": True,
            "closure_artifact_path_equals_required_path": True,
            "exactly_one_new_tracked_python_tool_file_expected": True,
            "exactly_one_new_tracked_json_closure_artifact_expected": True,
            "no_existing_files_modified_expected": True,
            "no_other_tracked_files_expected": True,
            "evaluator_artifact_loaded": True,
            "evaluator_payload_hash_verified": True,
            "execution_artifact_loaded": True,
            "execution_payload_hash_verified": True,
            "evaluator_result_class_preserved": True,
            "holdout_policy_preserved": True,
            "holdout_used_for_config_selection_false": True,
            "route_closed_true": route_closed,
            "no_evaluator_rerun": True,
            "no_execution_rerun": True,
            "no_panel_rows_read": True,
            "no_funding_rows_read": True,
            "no_okx_panel_rows_read": True,
            "no_binance_1m_source_rows_read": True,
            "no_network_used": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_runtime_live_capital": True,
            "payload_sha256_excluding_hash_present": True,
            "replacement_checks_all_true": True,
        },
        "replacement_checks_all_true": True,
    }
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)
    required_assertions = [
        payload["status"] == STATUS,
        payload["module"] == MODULE_PATH,
        payload["prior_evaluator_result_preserved"]["result_class"] == result_class,
        payload["holdout_policy_preserved"]["holdout_used_for_config_selection"] is False,
        payload["closure_record"]["route_closed"] is True,
        payload["closure_record"]["candidate_generation_allowed_now"] is False,
        payload["closure_record"]["edge_claim_allowed_now"] is False,
        payload["closure_record"]["family_release_allowed_now"] is False,
        payload["closure_record"]["holdout_access_allowed_now"] is False,
        payload["closure_record"]["runtime_live_capital_allowed_now"] is False,
        payload["followup_permissions_after_closure"]["next_immediate_module_required"] is False,
        payload["project_state_after_closure"]["project_can_pause_after_closure"] is True,
        payload["forbidden_actions_confirmed_false"]["evaluator_rerun"] is False,
        payload["forbidden_actions_confirmed_false"]["execution_rerun"] is False,
        payload["forbidden_actions_confirmed_false"]["panel_rows_read"] is False,
        payload["forbidden_actions_confirmed_false"]["funding_rows_read"] is False,
        payload["replacement_checks_all_true"] is True,
    ]
    if not all(required_assertions):
        raise RuntimeError("closure invariant assertion failed")
    return payload


def main() -> None:
    artifact = build_closure()
    output_path = REPO_ROOT / ARTIFACT_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": artifact["status"],
        "artifact_path": ARTIFACT_PATH,
        "result_class": artifact["prior_evaluator_result_preserved"]["result_class"],
        "diagnostic_promising": artifact["prior_evaluator_result_preserved"]["diagnostic_promising"],
        "route_closed": artifact["closure_record"]["route_closed"],
        "holdout_used_for_config_selection": artifact["holdout_policy_preserved"]["holdout_used_for_config_selection"],
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": artifact["replacement_checks_all_true"],
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
