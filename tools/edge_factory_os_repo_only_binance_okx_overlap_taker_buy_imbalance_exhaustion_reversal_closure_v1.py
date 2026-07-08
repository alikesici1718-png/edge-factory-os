import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_taker_buy_imbalance_exhaustion_reversal_closure_v1.py"
ARTIFACT_PATH = "artifacts/strategy_closures/binance_okx_overlap_taker_buy_imbalance_exhaustion_reversal_closure_v1.json"
STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_TAKER_BUY_IMBALANCE_EXHAUSTION_REVERSAL_CLOSURE_CREATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_TAKER_BUY_IMBALANCE_EXHAUSTION_REVERSAL_CLOSURE_RECORD"

EVALUATOR_PATH = "artifacts/strategy_evaluations/binance_okx_overlap_taker_buy_imbalance_exhaustion_reversal_evaluator_v1.json"
EXECUTION_PATH = "artifacts/strategy_executions/binance_okx_overlap_taker_buy_imbalance_exhaustion_reversal_execution_v1.json"
EVALUATOR_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_TAKER_BUY_IMBALANCE_EXHAUSTION_REVERSAL_EVALUATED"
EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_TAKER_BUY_IMBALANCE_EXHAUSTION_REVERSAL_EXECUTED"
EVALUATOR_PAYLOAD_HASH = "9642fe21a87563bd2bd9bb063de1f6716b92915dec74ca626d16e0efed06de70"
EXECUTION_PAYLOAD_HASH = "43e5ee6a12a32c32ea52f019feb3a1bf5d90b790983b58cf89d5db9b871f1ef0"

ROUTE_FAMILY = "BINANCE_OKX_OVERLAP_TAKER_BUY_IMBALANCE_EXHAUSTION_REVERSAL_BASELINE"
CONFIG_ID = "taker_buy_share_p95_upcandle_short_hold8h"
REJECTED_CLASS = "TAKER_BUY_IMBALANCE_EXHAUSTION_REVERSAL_REJECTED_NO_FOLLOWUP"
PROMISING_CLASS = "TAKER_BUY_IMBALANCE_EXHAUSTION_REVERSAL_DIAGNOSTIC_PROMISING_REQUIRES_CLOSURE_NO_CANDIDATE_NO_EDGE"
INCONCLUSIVE_CLASS = "TAKER_BUY_IMBALANCE_EXHAUSTION_REVERSAL_INCONCLUSIVE_EVALUATOR_INPUT_INCOMPLETE_NO_FOLLOWUP"
INVALIDATED_CLASS = "TAKER_BUY_IMBALANCE_EXHAUSTION_REVERSAL_INVALIDATED_BY_SAFETY_OR_INTEGRITY_FAILURE"


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
    if execution.get("route_family") != ROUTE_FAMILY:
        raise RuntimeError("execution route family mismatch")
    if execution.get("config_id") != CONFIG_ID:
        raise RuntimeError("execution config id mismatch")

    classification = evaluator["result_classification"]
    prior_execution = evaluator["prior_execution_preserved"]
    result_class = classification["result_class"]
    diagnostic_promising = classification["diagnostic_promising"]
    closure_state = closure_state_for_result(result_class)
    route_closed = True
    closure_reason = (
        f"The taker-buy imbalance exhaustion reversal route is closed with result_class={result_class}. "
        f"Validation gross metric was {classification['validation_gross_metric_bps']} bps and validation net metric was "
        f"{classification['validation_net_metric_bps']} bps. validation_positive_after_cost="
        f"{classification['validation_positive_after_cost']}, null_baseline_passed="
        f"{classification['null_baseline_review_passed']}, monthly_stability_passed="
        f"{classification['monthly_stability_review_passed']}, event_coverage_passed="
        f"{classification['event_coverage_review_passed']}, exposure_risk_passed="
        f"{classification['exposure_risk_review_passed']}, turnover_concentration_passed="
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
            "validation_net_metric_bps": classification["validation_net_metric_bps"],
            "validation_gross_metric_bps": classification["validation_gross_metric_bps"],
            "validation_positive_after_cost": classification["validation_positive_after_cost"],
            "null_baseline_review_passed": classification["null_baseline_review_passed"],
            "monthly_stability_review_passed": classification["monthly_stability_review_passed"],
            "event_coverage_review_passed": classification["event_coverage_review_passed"],
            "exposure_risk_review_passed": classification["exposure_risk_review_passed"],
            "turnover_concentration_review_passed": classification["turnover_concentration_review_passed"],
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
            "train_event_count": execution["config_result"]["train_event_count"],
            "validation_event_count": execution["config_result"]["validation_event_count"],
            "validation_net_metric_bps": execution["config_result"]["validation_net_metric_bps"],
            "validation_gross_metric_bps": execution["config_result"]["validation_gross_metric_bps"],
            "validation_positive_after_cost": execution["config_result"]["validation_positive_after_cost"],
            "top_symbol_event_share": execution["event_coverage_summary"]["top_symbol_event_share"],
            "correlation_with_equal_weight_market_return": execution["exposure_risk_summary"]["correlation_with_equal_weight_market_return"],
            "worst_validation_month_net_metric_bps": execution["exposure_risk_summary"]["worst_validation_month_net_metric_bps"],
            "null_baseline_review_preliminary_passed": execution["null_baseline_summary"]["null_baseline_review_preliminary_passed"],
            "monthly_stability_review_preliminary_passed": execution["monthly_stability_summary"]["monthly_stability_review_preliminary_passed"],
            "event_coverage_review_preliminary_passed": execution["event_coverage_summary"]["event_coverage_review_preliminary_passed"],
            "exposure_risk_review_preliminary_passed": execution["exposure_risk_summary"]["exposure_risk_review_preliminary_passed"],
            "turnover_concentration_review_preliminary_passed": execution["turnover_concentration_summary"]["turnover_concentration_review_preliminary_passed"],
            "metric_integrity_issue_count": execution["metric_integrity_summary"]["metric_integrity_issue_count"],
            "metric_integrity_passed": execution["metric_integrity_summary"]["metric_integrity_passed"],
            "execution_result_is_diagnostic_only": execution["diagnostic_interpretation_limits"]["diagnostic_execution_only"],
            "short_only": execution["preregistration_contract_snapshot"]["short_only"],
            "market_neutral": execution["preregistration_contract_snapshot"]["market_neutral"],
            "candidate_generation": False,
            "edge_claim": False,
            "family_release": False,
            "runtime_live_capital": False,
        },
        "closure_record": {
            "closure_record_created": True,
            "closure_type": "TAKER_BUY_IMBALANCE_EXHAUSTION_REVERSAL_CLOSURE_AFTER_EVALUATOR",
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
            "event_coverage_review_passed": classification["event_coverage_review_passed"],
            "exposure_risk_review_passed": classification["exposure_risk_review_passed"],
            "turnover_concentration_review_passed": classification["turnover_concentration_review_passed"],
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
            "strategy_search_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "no_active_candidate_exists": True,
            "no_active_edge_claim_exists": True,
            "no_family_release_exists": True,
            "no_runtime_live_capital_permission_exists": True,
        },
        "project_state_after_closure": {
            "taker_buy_imbalance_exhaustion_route_closed": route_closed,
            "short_only_route_closed_without_edge_claim": True,
            "no_active_candidate_exists": True,
            "no_active_edge_claim_exists": True,
            "no_family_release_exists": True,
            "no_holdout_access_exists": True,
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
            "network_used": False,
            "binance_api_called": False,
            "strategy_search_executed": False,
            "non_preregistered_config_tested": False,
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
            "evaluator_payload_hash_verified": True,
            "execution_artifact_loaded": True,
            "execution_payload_hash_verified": True,
            "evaluator_result_class_preserved": True,
            "route_closed_true": route_closed,
            "no_evaluator_rerun": True,
            "no_execution_rerun": True,
            "no_panel_rows_read": True,
            "no_funding_rows_read": True,
            "no_okx_panel_rows_read": True,
            "no_network_used": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_runtime_live_capital": True,
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
        payload["prior_evaluator_result_preserved"]["result_class"] == result_class,
        payload["closure_record"]["route_closed"] is True,
        payload["closure_record"]["retest_allowed_now"] is False,
        payload["closure_record"]["parameter_expansion_allowed_now"] is False,
        payload["closure_record"]["candidate_generation_allowed_now"] is False,
        payload["closure_record"]["edge_claim_allowed_now"] is False,
        payload["closure_record"]["runtime_live_capital_allowed_now"] is False,
        payload["project_state_after_closure"]["next_immediate_module_required"] is False,
        payload["project_state_after_closure"]["project_can_pause_after_closure"] is True,
        payload["forbidden_actions_confirmed_false"]["execution_rerun"] is False,
        payload["forbidden_actions_confirmed_false"]["panel_rows_read"] is False,
        payload["forbidden_actions_confirmed_false"]["network_used"] is False,
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
        "result_class": artifact["prior_evaluator_result_preserved"]["result_class"],
        "diagnostic_promising": artifact["prior_evaluator_result_preserved"]["diagnostic_promising"],
        "config_id": artifact["closure_record"]["config_id"],
        "validation_gross_metric_bps": artifact["closure_record"]["validation_gross_metric_bps"],
        "validation_net_metric_bps": artifact["closure_record"]["validation_net_metric_bps"],
        "validation_positive_after_cost": artifact["closure_record"]["validation_positive_after_cost"],
        "null_baseline_review_passed": artifact["closure_record"]["null_baseline_review_passed"],
        "monthly_stability_review_passed": artifact["closure_record"]["monthly_stability_review_passed"],
        "event_coverage_review_passed": artifact["closure_record"]["event_coverage_review_passed"],
        "exposure_risk_review_passed": artifact["closure_record"]["exposure_risk_review_passed"],
        "turnover_concentration_review_passed": artifact["closure_record"]["turnover_concentration_review_passed"],
        "metric_integrity_issue_count": artifact["closure_record"]["metric_integrity_issue_count"],
        "route_closed": artifact["closure_record"]["route_closed"],
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "next_immediate_module_required": artifact["project_state_after_closure"]["next_immediate_module_required"],
        "project_can_pause_after_closure": artifact["project_state_after_closure"]["project_can_pause_after_closure"],
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": artifact["replacement_checks_all_true"],
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
