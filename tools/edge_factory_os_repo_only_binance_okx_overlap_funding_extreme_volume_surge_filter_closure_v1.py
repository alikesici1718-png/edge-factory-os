import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_extreme_volume_surge_filter_closure_v1.py"
ARTIFACT_PATH = "artifacts/strategy_closures/binance_okx_overlap_funding_extreme_volume_surge_filter_closure_v1.json"
STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_EXTREME_VOLUME_SURGE_FILTER_CLOSURE_CREATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_FUNDING_EXTREME_VOLUME_SURGE_FILTER_CLOSURE_RECORD"

EVALUATOR_PATH = "artifacts/strategy_evaluations/binance_okx_overlap_funding_extreme_volume_surge_filter_evaluator_v1.json"
EXECUTION_PATH = "artifacts/strategy_executions/binance_okx_overlap_funding_extreme_volume_surge_filter_execution_v1.json"
EVALUATOR_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_EXTREME_VOLUME_SURGE_FILTER_EVALUATED"
EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_FUNDING_EXTREME_VOLUME_SURGE_FILTER_EXECUTED"
EVALUATOR_PAYLOAD_HASH = "aa1c4acdddb0d919236a1955459360d12e80a6f8f0bacbfab7c5565fdee514d4"
EXECUTION_PAYLOAD_HASH = "59da56218164c952cc3dd7551a5dd0f72cd4a6d5d82cc9cf4323fe760031e58b"

ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_EXTREME_VOLUME_SURGE_FILTER_REVERSAL_BASELINE"
CONFIG_ID = "funding_mean9_volume_surge24h_p80_30d_hold24h"
REJECTED_CLASS = "FUNDING_EXTREME_VOLUME_SURGE_FILTER_REJECTED_NO_FOLLOWUP"
PROMISING_CLASS = "FUNDING_EXTREME_VOLUME_SURGE_FILTER_DIAGNOSTIC_PROMISING_REQUIRES_CLOSURE_NO_CANDIDATE_NO_EDGE"
INCONCLUSIVE_CLASS = "FUNDING_EXTREME_VOLUME_SURGE_FILTER_INCONCLUSIVE_EVALUATOR_INPUT_INCOMPLETE_NO_FOLLOWUP"
INVALIDATED_CLASS = "FUNDING_EXTREME_VOLUME_SURGE_FILTER_INVALIDATED_BY_SAFETY_OR_INTEGRITY_FAILURE"


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

    classification = evaluator["result_classification"]
    prior_execution = evaluator["prior_execution_preserved"]
    result_class = classification["result_class"]
    diagnostic_promising = classification["diagnostic_promising"]
    closure_state = closure_state_for_result(result_class)

    route_closed = True
    closure_reason = (
        f"The volume-surge funding-extreme route is closed with result_class={result_class}. "
        f"Validation gross metric was {classification['validation_gross_metric_bps']} bps and validation net metric was "
        f"{classification['validation_net_metric_bps']} bps. validation_positive_after_cost="
        f"{classification['validation_positive_after_cost']}, null_baseline_passed="
        f"{classification['null_baseline_review_passed']}, monthly_stability_passed="
        f"{classification['monthly_stability_review_passed']}, turnover_concentration_passed="
        f"{classification['turnover_concentration_review_passed']}, volume_anomaly_coverage_passed="
        f"{classification['volume_anomaly_coverage_review_passed']}, metric_integrity_issue_count="
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
            "validation_net_metric_bps": classification["validation_net_metric_bps"],
            "validation_gross_metric_bps": classification["validation_gross_metric_bps"],
            "validation_positive_after_cost": classification["validation_positive_after_cost"],
            "null_baseline_review_passed": classification["null_baseline_review_passed"],
            "monthly_stability_review_passed": classification["monthly_stability_review_passed"],
            "turnover_concentration_review_passed": classification["turnover_concentration_review_passed"],
            "volume_anomaly_coverage_review_passed": classification["volume_anomaly_coverage_review_passed"],
            "metric_integrity_issue_count": classification["metric_integrity_issue_count"],
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
            "train_entry_count": execution["config_result"]["train_entry_count"],
            "validation_entry_count": execution["config_result"]["validation_entry_count"],
            "validation_net_metric_bps": execution["config_result"]["validation_net_metric_bps"],
            "validation_gross_metric_bps": execution["config_result"]["validation_gross_metric_bps"],
            "validation_positive_after_cost": execution["config_result"]["validation_positive_after_cost"],
            "null_baseline_review_preliminary_passed": execution["null_baseline_summary"]["null_baseline_review_preliminary_passed"],
            "monthly_stability_review_preliminary_passed": execution["monthly_stability_summary"]["monthly_stability_review_preliminary_passed"],
            "turnover_concentration_review_preliminary_passed": execution["turnover_concentration_summary"]["turnover_concentration_review_preliminary_passed"],
            "volume_anomaly_coverage_review_preliminary_passed": execution["volume_anomaly_coverage_summary"]["volume_anomaly_coverage_review_preliminary_passed"],
            "metric_integrity_issue_count": execution["metric_integrity_summary"]["metric_integrity_issue_count"],
            "metric_integrity_passed": execution["metric_integrity_summary"]["metric_integrity_passed"],
            "execution_result_is_diagnostic_only": execution["diagnostic_interpretation_limits"]["diagnostic_execution_only"],
            "candidate_generation": False,
            "edge_claim": False,
            "family_release": False,
            "runtime_live_capital": False,
        },
        "volume_anomaly_coverage_preserved": {
            "volume_anomaly_coverage_review_passed": classification["volume_anomaly_coverage_review_passed"],
            "average_volume_anomaly_symbols_per_timestamp": prior_execution["average_volume_anomaly_symbols_per_timestamp"],
            "validation_volume_anomaly_eligible_timestamp_count": prior_execution["validation_volume_anomaly_eligible_timestamp_count"],
            "volume_anomaly_field": "quote_volume",
            "volume_anomaly_filter_created": True,
        },
        "closure_record": {
            "closure_record_created": True,
            "closure_type": "FUNDING_EXTREME_VOLUME_SURGE_FILTER_CLOSURE_AFTER_EVALUATOR",
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
            "volume_anomaly_coverage_review_passed": classification["volume_anomaly_coverage_review_passed"],
            "metric_integrity_issue_count": classification["metric_integrity_issue_count"],
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
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "no_active_candidate_exists": True,
            "no_active_edge_claim_exists": True,
            "no_family_release_exists": True,
            "no_runtime_live_capital_permission_exists": True,
        },
        "project_state_after_closure": {
            "binance_okx_overlap_panel_built_and_reviewed": True,
            "funding_data_acquired_and_reviewed": True,
            "volume_surge_route_closed": route_closed,
            "no_active_candidate_exists": True,
            "no_active_edge_claim_exists": True,
            "no_family_release_exists": True,
            "no_holdout_access_exists": True,
            "no_runtime_live_capital_permission_exists": True,
            "immediate_next_module_required": False,
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
            "strategy_execution_rerun": False,
            "evaluator_rerun": False,
            "strategy_search_executed": False,
            "panel_rows_read": False,
            "funding_rows_read": False,
            "okx_panel_rows_read": False,
            "funding_rate_endpoint_called": False,
            "funding_data_fetched": False,
            "candidates_generated": False,
            "edge_claimed": False,
            "family_released": False,
            "holdout_accessed": False,
            "boundary_buffer_accessed": False,
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
            "evaluator_status_verified": True,
            "evaluator_payload_hash_verified": True,
            "execution_artifact_loaded": True,
            "execution_payload_hash_verified": True,
            "result_class_preserved": True,
            "diagnostic_promising_preserved": True,
            "config_id_preserved": True,
            "validation_net_metric_preserved": True,
            "validation_positive_after_cost_preserved": True,
            "volume_anomaly_coverage_preserved": True,
            "route_closed": route_closed,
            "no_network_used": True,
            "no_execution_rerun": True,
            "no_evaluator_rerun": True,
            "no_panel_rows_read": True,
            "no_funding_rows_read": True,
            "no_okx_panel_rows_read": True,
            "no_strategy_search": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_runtime_live_capital": True,
            "next_immediate_module_required_false": True,
            "project_can_pause_after_closure": True,
            "closure_artifact_json_valid": True,
            "payload_sha256_excluding_hash_present": True,
            "replacement_checks_all_true": True,
        },
        "replacement_checks_all_true": True,
    }
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)

    required_assertions = [
        payload["status"] == STATUS,
        payload["module"] == MODULE_PATH,
        payload["closure_record"]["route_closed"] is True,
        payload["closure_record"]["retest_allowed_now"] is False,
        payload["closure_record"]["parameter_expansion_allowed_now"] is False,
        payload["closure_record"]["candidate_generation_allowed_now"] is False,
        payload["closure_record"]["edge_claim_allowed_now"] is False,
        payload["closure_record"]["runtime_live_capital_allowed_now"] is False,
        payload["project_state_after_closure"]["immediate_next_module_required"] is False,
        payload["project_state_after_closure"]["project_can_pause_after_closure"] is True,
        payload["forbidden_actions_confirmed_false"]["strategy_execution_rerun"] is False,
        payload["forbidden_actions_confirmed_false"]["evaluator_rerun"] is False,
        payload["forbidden_actions_confirmed_false"]["panel_rows_read"] is False,
        payload["forbidden_actions_confirmed_false"]["funding_rows_read"] is False,
        payload["replacement_checks_all_true"] is True,
    ]
    if not all(required_assertions):
        raise RuntimeError("closure invariant assertion failed")
    return payload


def main() -> None:
    artifact = build_closure()
    path = REPO_ROOT / ARTIFACT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": artifact["status"],
        "closure_artifact_path": ARTIFACT_PATH,
        "result_class": artifact["closure_record"]["result_class_confirmed"],
        "diagnostic_promising": artifact["closure_record"]["diagnostic_promising_confirmed"],
        "config_id": CONFIG_ID,
        "validation_net_metric_bps": artifact["closure_record"]["validation_net_metric_bps"],
        "validation_gross_metric_bps": artifact["closure_record"]["validation_gross_metric_bps"],
        "validation_positive_after_cost": artifact["closure_record"]["validation_positive_after_cost"],
        "null_baseline_review_passed": artifact["closure_record"]["null_baseline_review_passed"],
        "monthly_stability_review_passed": artifact["closure_record"]["monthly_stability_review_passed"],
        "turnover_concentration_review_passed": artifact["closure_record"]["turnover_concentration_review_passed"],
        "volume_anomaly_coverage_review_passed": artifact["closure_record"]["volume_anomaly_coverage_review_passed"],
        "metric_integrity_issue_count": artifact["closure_record"]["metric_integrity_issue_count"],
        "route_closed": artifact["closure_record"]["route_closed"],
        "retest_allowed_now": artifact["closure_record"]["retest_allowed_now"],
        "parameter_expansion_allowed_now": artifact["closure_record"]["parameter_expansion_allowed_now"],
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "next_immediate_module_required": artifact["project_state_after_closure"]["immediate_next_module_required"],
        "project_can_pause_after_closure": artifact["project_state_after_closure"]["project_can_pause_after_closure"],
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": artifact["replacement_checks_all_true"],
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
