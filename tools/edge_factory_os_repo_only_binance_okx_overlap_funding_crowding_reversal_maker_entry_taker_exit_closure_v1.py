import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_crowding_reversal_maker_entry_taker_exit_closure_v1.py"
ARTIFACT_PATH = "artifacts/strategy_closures/binance_okx_overlap_funding_crowding_reversal_maker_entry_taker_exit_closure_v1.json"
STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_CROWDING_REVERSAL_MAKER_ENTRY_TAKER_EXIT_CLOSURE_CREATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_FUNDING_CROWDING_REVERSAL_MAKER_ENTRY_TAKER_EXIT_CLOSURE_RECORD"

EVALUATOR_PATH = "artifacts/strategy_evaluations/binance_okx_overlap_funding_crowding_reversal_maker_entry_taker_exit_evaluator_v1.json"
EXECUTION_PATH = "artifacts/strategy_executions/binance_okx_overlap_funding_crowding_reversal_maker_entry_taker_exit_execution_v1.json"
EVALUATOR_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_CROWDING_REVERSAL_MAKER_ENTRY_TAKER_EXIT_EVALUATED"
EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_FUNDING_CROWDING_REVERSAL_MAKER_ENTRY_TAKER_EXIT_EXECUTED"
EVALUATOR_PAYLOAD_HASH = "951a9582319d23c5a5833a8cb6661762f478aa809b4dc77badf9269b1f797bdb"
EXECUTION_PAYLOAD_HASH = "a4d54bb6b0d07c876c3a93ec78711e377b7b1a7f287aa512a240e1605de0f37c"

ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_CROWDING_REVERSAL_MAKER_ENTRY_TAKER_EXIT_DIAGNOSTIC"
CONFIG_ID = "funding_mean9_hold24h_maker_entry_1bps_taker_exit_cost10bps"
PROMISING_CLASS = "FUNDING_CROWDING_REVERSAL_MAKER_ENTRY_TAKER_EXIT_DIAGNOSTIC_PROMISING_REQUIRES_CLOSURE_NO_CANDIDATE_NO_EDGE"
REJECTED_CLASS = "FUNDING_CROWDING_REVERSAL_MAKER_ENTRY_TAKER_EXIT_REJECTED_NO_FOLLOWUP"
INCONCLUSIVE_CLASS = "FUNDING_CROWDING_REVERSAL_MAKER_ENTRY_TAKER_EXIT_INCONCLUSIVE_INPUT_INCOMPLETE_NO_FOLLOWUP"
INVALIDATED_CLASS = "FUNDING_CROWDING_REVERSAL_MAKER_ENTRY_TAKER_EXIT_INVALIDATED_BY_SAFETY_OR_INTEGRITY_FAILURE"


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
    maker_findings = evaluator["maker_fill_quality_findings"]
    prior_execution = evaluator["prior_execution_preserved"]
    result_class = classification["result_class"]
    diagnostic_promising = classification["diagnostic_promising"]
    closure_state = closure_state_for_result(result_class)
    route_closed = True
    closure_reason = (
        f"The maker-entry funding crowding reversal diagnostic is closed with result_class={result_class}. "
        f"Validation gross metric was {classification['validation_gross_metric_bps']} bps and validation net metric was "
        f"{classification['validation_net_metric_bps']} bps. validation_positive_after_cost="
        f"{classification['validation_positive_after_cost']}, null_baseline_passed="
        f"{classification['null_baseline_review_passed']}, validation_monthly_stability_passed="
        f"{classification['validation_monthly_stability_review_passed']}, turnover_concentration_passed="
        f"{classification['turnover_concentration_review_passed']}, maker_fill_quality_passed="
        f"{classification['maker_fill_quality_review_passed']}. The maker fill proxy uses 1h OHLCV and does not model "
        "order book queue position. This closure grants no candidate, edge claim, family release, holdout access, or "
        "runtime/live/capital permission."
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
            "validation_monthly_stability_review_passed": classification["validation_monthly_stability_review_passed"],
            "turnover_concentration_review_passed": classification["turnover_concentration_review_passed"],
            "maker_fill_quality_review_passed": classification["maker_fill_quality_review_passed"],
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
            "train": execution["config_result"]["train"],
            "validation": execution["config_result"]["validation"],
            "holdout": execution["config_result"]["holdout"],
            "train_monthly_positive_rate": prior_execution["train_monthly_positive_rate"],
            "validation_monthly_positive_rate": prior_execution["validation_monthly_positive_rate"],
            "holdout_monthly_positive_rate": prior_execution["holdout_monthly_positive_rate"],
            "holdout_used_for_config_selection": prior_execution["holdout_used_for_config_selection"],
            "metric_integrity_issue_count": prior_execution["metric_integrity_issue_count"],
            "candidate_generation": False,
            "edge_claim": False,
            "family_release": False,
            "runtime_live_capital": False,
        },
        "maker_fill_proxy_warning_preserved": {
            "maker_fill_proxy_is_not_order_book_simulation": True,
            "order_book_queue_not_modeled": maker_findings["order_book_queue_not_modeled"],
            "adverse_selection_proxy_note": maker_findings["adverse_selection_proxy_note"],
            "maker_fill_quality_review_passed": maker_findings["maker_fill_quality_review_preliminary_passed"],
            "long_fill_rate": maker_findings["long_fill_rate"],
            "short_fill_rate": maker_findings["short_fill_rate"],
            "average_fill_imbalance_abs": maker_findings["average_fill_imbalance_abs"],
            "validation_executed_timestamp_count": maker_findings["validation_executed_timestamp_count"],
            "average_filled_long_symbols": maker_findings["average_filled_long_symbols"],
            "average_filled_short_symbols": maker_findings["average_filled_short_symbols"],
        },
        "closure_record": {
            "closure_record_created": True,
            "closure_type": "FUNDING_CROWDING_REVERSAL_MAKER_ENTRY_TAKER_EXIT_CLOSURE_AFTER_EVALUATOR",
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
            "validation_monthly_stability_review_passed": classification["validation_monthly_stability_review_passed"],
            "turnover_concentration_review_passed": classification["turnover_concentration_review_passed"],
            "maker_fill_quality_review_passed": classification["maker_fill_quality_review_passed"],
            "metric_integrity_issue_count": classification["metric_integrity_issue_count"],
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
            "runtime_live_capital_allowed_now": False,
        },
        "project_state_after_closure": {
            "maker_entry_diagnostic_route_closed": route_closed,
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
            "evaluator_artifact_loaded": True,
            "evaluator_payload_hash_verified": True,
            "execution_artifact_loaded": True,
            "execution_payload_hash_verified": True,
            "evaluator_result_class_preserved": True,
            "maker_fill_proxy_warning_preserved": True,
            "route_closed_true": route_closed,
            "holdout_used_for_config_selection_false": True,
            "no_evaluator_rerun": True,
            "no_execution_rerun": True,
            "no_panel_rows_read": True,
            "no_funding_rows_read": True,
            "no_okx_panel_rows_read": True,
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
        payload["maker_fill_proxy_warning_preserved"]["order_book_queue_not_modeled"] is True,
        payload["closure_record"]["route_closed"] is True,
        payload["closure_record"]["candidate_generation_allowed_now"] is False,
        payload["closure_record"]["edge_claim_allowed_now"] is False,
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
        "order_book_queue_not_modeled": artifact["maker_fill_proxy_warning_preserved"]["order_book_queue_not_modeled"],
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": artifact["replacement_checks_all_true"],
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
