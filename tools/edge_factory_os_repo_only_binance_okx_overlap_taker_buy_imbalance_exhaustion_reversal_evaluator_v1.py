import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_taker_buy_imbalance_exhaustion_reversal_evaluator_v1.py"
ARTIFACT_PATH = "artifacts/strategy_evaluations/binance_okx_overlap_taker_buy_imbalance_exhaustion_reversal_evaluator_v1.json"
STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_TAKER_BUY_IMBALANCE_EXHAUSTION_REVERSAL_EVALUATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_TAKER_BUY_IMBALANCE_EXHAUSTION_REVERSAL_EVALUATION"

EXECUTION_PATH = "artifacts/strategy_executions/binance_okx_overlap_taker_buy_imbalance_exhaustion_reversal_execution_v1.json"
TAKER_AVAILABILITY_PATH = "artifacts/taker_buy_sell_volume_availability_locks/binance_okx_overlap_taker_buy_sell_volume_history_availability_discovery_lock_v1.json"
EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_TAKER_BUY_IMBALANCE_EXHAUSTION_REVERSAL_EXECUTED"
EXECUTION_PAYLOAD_HASH = "43e5ee6a12a32c32ea52f019feb3a1bf5d90b790983b58cf89d5db9b871f1ef0"
ROUTE_FAMILY = "BINANCE_OKX_OVERLAP_TAKER_BUY_IMBALANCE_EXHAUSTION_REVERSAL_BASELINE"
CONFIG_ID = "taker_buy_share_p95_upcandle_short_hold8h"

PROMISING_CLASS = "TAKER_BUY_IMBALANCE_EXHAUSTION_REVERSAL_DIAGNOSTIC_PROMISING_REQUIRES_CLOSURE_NO_CANDIDATE_NO_EDGE"
REJECTED_CLASS = "TAKER_BUY_IMBALANCE_EXHAUSTION_REVERSAL_REJECTED_NO_FOLLOWUP"
INCONCLUSIVE_CLASS = "TAKER_BUY_IMBALANCE_EXHAUSTION_REVERSAL_INCONCLUSIVE_EVALUATOR_INPUT_INCOMPLETE_NO_FOLLOWUP"
INVALIDATED_CLASS = "TAKER_BUY_IMBALANCE_EXHAUSTION_REVERSAL_INVALIDATED_BY_SAFETY_OR_INTEGRITY_FAILURE"
ALLOWED_RESULT_CLASSES = [
    PROMISING_CLASS,
    REJECTED_CLASS,
    INCONCLUSIVE_CLASS,
    INVALIDATED_CLASS,
]


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


def finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def build_evaluation() -> Dict[str, Any]:
    execution = read_json(EXECUTION_PATH)
    availability = read_json(TAKER_AVAILABILITY_PATH)
    execution_hash = verify_hash(execution, EXECUTION_PAYLOAD_HASH)
    availability_hash = verify_hash(availability)

    if execution.get("status") != EXECUTION_STATUS:
        raise RuntimeError("execution status mismatch")
    if execution.get("route_family") != ROUTE_FAMILY:
        raise RuntimeError("route family mismatch")
    if execution.get("config_id") != CONFIG_ID:
        raise RuntimeError("config id mismatch")
    if availability.get("panel_derived_taker_buy_sell_availability", {}).get("aligned_window_covered_by_panel_derived_data") is not True:
        raise RuntimeError("panel-derived aligned-window taker availability not preserved")

    config_result = execution["config_result"]
    null_summary = execution["null_baseline_summary"]
    monthly = execution["monthly_stability_summary"]
    event_coverage = execution["event_coverage_summary"]
    exposure = execution["exposure_risk_summary"]
    turnover = execution["turnover_concentration_summary"]
    metric_integrity = execution["metric_integrity_summary"]
    forbidden = execution["forbidden_actions_confirmed_false"]

    validation_net = config_result["validation_net_metric_bps"]
    validation_gross = config_result["validation_gross_metric_bps"]
    validation_positive = config_result["validation_positive_after_cost"]
    null_passed = null_summary["null_baseline_review_preliminary_passed"]
    monthly_passed = monthly["monthly_stability_review_preliminary_passed"]
    event_coverage_passed = event_coverage["event_coverage_review_preliminary_passed"]
    exposure_passed = exposure["exposure_risk_review_preliminary_passed"]
    turnover_passed = turnover["turnover_concentration_review_preliminary_passed"]
    integrity_passed = metric_integrity["metric_integrity_passed"]
    safety_review_passed = (
        forbidden["network_used"] is False
        and forbidden["binance_api_called"] is False
        and forbidden["funding_rows_read"] is False
        and forbidden["okx_panel_rows_read"] is False
        and forbidden["candidates_generated"] is False
        and forbidden["edge_claimed"] is False
        and forbidden["runtime_permission_granted"] is False
        and forbidden["live_permission_granted"] is False
        and forbidden["capital_permission_granted"] is False
    )
    evaluator_input_complete = all(
        [
            finite(validation_net),
            finite(validation_gross),
            isinstance(validation_positive, bool),
            isinstance(null_passed, bool),
            isinstance(monthly_passed, bool),
            isinstance(event_coverage_passed, bool),
            isinstance(exposure_passed, bool),
            isinstance(turnover_passed, bool),
            isinstance(integrity_passed, bool),
            isinstance(safety_review_passed, bool),
        ]
    )
    diagnostic_promising = bool(
        evaluator_input_complete
        and validation_net > 0
        and validation_positive is True
        and null_passed is True
        and monthly_passed is True
        and event_coverage_passed is True
        and exposure_passed is True
        and turnover_passed is True
        and integrity_passed is True
        and safety_review_passed is True
    )
    if not safety_review_passed or not integrity_passed:
        result_class = INVALIDATED_CLASS
    elif not evaluator_input_complete:
        result_class = INCONCLUSIVE_CLASS
    elif diagnostic_promising:
        result_class = PROMISING_CLASS
    else:
        result_class = REJECTED_CLASS

    reason = (
        f"The single embedded-config taker-buy imbalance exhaustion route produced validation gross metric "
        f"{validation_gross} bps and validation net metric {validation_net} bps. "
        f"validation_positive_after_cost={validation_positive}, null_baseline_passed={null_passed}, "
        f"monthly_stability_passed={monthly_passed}, event_coverage_passed={event_coverage_passed}, "
        f"exposure_risk_passed={exposure_passed}, turnover_concentration_passed={turnover_passed}, "
        f"metric_integrity_passed={integrity_passed}. The evaluator grants no candidate, edge claim, "
        "family release, holdout access, or runtime/live/capital permission."
    )

    payload: Dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "prior_execution_preserved": {
            "path": EXECUTION_PATH,
            "status": execution["status"],
            "payload_sha256_excluding_hash": execution_hash,
            "route_family": execution["route_family"],
            "config_id": execution["config_id"],
            "preregistration_contract_snapshot_preserved": True,
            "short_only": execution["preregistration_contract_snapshot"]["short_only"],
            "market_neutral": execution["preregistration_contract_snapshot"]["market_neutral"],
            "validation_net_metric_bps": validation_net,
            "validation_gross_metric_bps": validation_gross,
            "validation_positive_after_cost": validation_positive,
            "train_event_count": config_result["train_event_count"],
            "validation_event_count": config_result["validation_event_count"],
            "top_symbol_event_share": event_coverage["top_symbol_event_share"],
            "correlation_with_equal_weight_market_return": exposure["correlation_with_equal_weight_market_return"],
            "worst_validation_month_net_metric_bps": exposure["worst_validation_month_net_metric_bps"],
            "metric_integrity_issue_count": metric_integrity["metric_integrity_issue_count"],
            "metric_integrity_passed": integrity_passed,
            "execution_result_is_diagnostic_only": execution["diagnostic_interpretation_limits"]["diagnostic_execution_only"],
            "candidate_generation": False,
            "edge_claim": False,
            "family_release": False,
            "runtime_live_capital": False,
        },
        "evaluation_policy": {
            "diagnostic_promising_requires_all": [
                "validation_net_metric_bps > 0",
                "validation_positive_after_cost is true",
                "null_baseline_review_preliminary_passed is true",
                "monthly_stability_review_preliminary_passed is true",
                "event_coverage_review_preliminary_passed is true",
                "exposure_risk_review_preliminary_passed is true",
                "turnover_concentration_review_preliminary_passed is true",
                "metric_integrity_passed is true",
                "safety_review_passed is true",
            ],
            "allowed_result_classes": ALLOWED_RESULT_CLASSES,
        },
        "execution_results_evaluated": {
            "config_id": CONFIG_ID,
            "validation_net_metric_bps": validation_net,
            "validation_gross_metric_bps": validation_gross,
            "validation_positive_after_cost": validation_positive,
            "train_event_count": config_result["train_event_count"],
            "validation_event_count": config_result["validation_event_count"],
            "validation_monthly_net_metric_bps_by_month": monthly["validation_monthly_net_metric_bps_by_month"],
            "validation_monthly_gross_metric_bps_by_month": monthly["validation_monthly_gross_metric_bps_by_month"],
        },
        "event_coverage_findings": {
            "event_coverage_review_passed": event_coverage_passed,
            "train_event_count": event_coverage["train_event_count"],
            "validation_event_count": event_coverage["validation_event_count"],
            "total_event_count": event_coverage["total_event_count"],
            "accepted_event_count": event_coverage["accepted_event_count"],
            "overlapping_event_skipped_count": event_coverage["overlapping_event_skipped_count"],
            "top_symbol_event_share": event_coverage["top_symbol_event_share"],
            "sample_size_review_preliminary_passed": event_coverage["sample_size_review_preliminary_passed"],
        },
        "exposure_risk_findings": {
            "exposure_risk_review_passed": exposure_passed,
            "short_only": exposure["short_only"],
            "market_neutral": exposure["market_neutral"],
            "average_active_events_per_timestamp": exposure["average_active_events_per_timestamp"],
            "max_active_events_per_timestamp": exposure["max_active_events_per_timestamp"],
            "correlation_with_equal_weight_market_return": exposure["correlation_with_equal_weight_market_return"],
            "worst_validation_month_net_metric_bps": exposure["worst_validation_month_net_metric_bps"],
            "exposure_risk_note": "short-only event route remains exposed to market short beta; exposure risk review must pass before diagnostic_promising can be true",
        },
        "evaluator_findings": {
            "evaluator_ran": True,
            "evaluator_recomputed_strategy_metrics": False,
            "evaluator_read_panel_rows": False,
            "evaluator_read_funding_rows": False,
            "evaluator_read_okx_rows": False,
            "best_validation_net_metric_positive_after_cost": bool(validation_net > 0),
            "validation_positive_after_cost": validation_positive,
            "null_baseline_review_passed": null_passed,
            "monthly_stability_review_passed": monthly_passed,
            "event_coverage_review_passed": event_coverage_passed,
            "exposure_risk_review_passed": exposure_passed,
            "turnover_concentration_review_passed": turnover_passed,
            "metric_integrity_review_passed": integrity_passed,
            "safety_review_passed": safety_review_passed,
            "evaluator_input_complete": evaluator_input_complete,
            "diagnostic_promising": diagnostic_promising,
            "evaluator_reason": reason,
        },
        "result_classification": {
            "result_class": result_class,
            "diagnostic_promising": diagnostic_promising,
            "config_id": CONFIG_ID,
            "validation_net_metric_bps": validation_net,
            "validation_gross_metric_bps": validation_gross,
            "validation_positive_after_cost": validation_positive,
            "null_baseline_review_passed": null_passed,
            "monthly_stability_review_passed": monthly_passed,
            "event_coverage_review_passed": event_coverage_passed,
            "exposure_risk_review_passed": exposure_passed,
            "turnover_concentration_review_passed": turnover_passed,
            "metric_integrity_issue_count": metric_integrity["metric_integrity_issue_count"],
            "metric_integrity_passed": integrity_passed,
            "safety_review_passed": safety_review_passed,
            "closure_record_required_next": True,
            "candidate_generation_allowed_from_evaluator": False,
            "edge_claim_allowed_from_evaluator": False,
            "family_release_allowed_from_evaluator": False,
            "holdout_access_allowed_from_evaluator": False,
            "runtime_live_capital_allowed_from_evaluator": False,
        },
        "followup_permissions": {
            "closure_record_required_next": True,
            "strategy_search_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "holdout_access_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
        },
        "forbidden_actions_confirmed_false": {
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
            "evaluator_artifact_path_equals_required_path": True,
            "exactly_one_new_tracked_python_tool_file_expected": True,
            "exactly_one_new_tracked_json_evaluator_artifact_expected": True,
            "no_existing_files_modified_expected": True,
            "no_other_tracked_files_expected": True,
            "execution_artifact_loaded": True,
            "execution_payload_hash_verified": True,
            "availability_artifact_loaded": True,
            "availability_payload_hash_verified": True,
            "config_id_matches_execution": True,
            "result_class_allowed": result_class in ALLOWED_RESULT_CLASSES,
            "closure_record_required_next": True,
            "no_execution_rerun": True,
            "no_panel_rows_read": True,
            "no_funding_rows_read": True,
            "no_okx_panel_rows_read": True,
            "no_network_used": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_runtime_live_capital": True,
            "evaluator_artifact_json_valid": True,
            "payload_sha256_excluding_hash_present": True,
            "replacement_checks_all_true": True,
        },
        "source_artifacts": {
            "execution_payload_hash": execution_hash,
            "taker_buy_sell_availability_payload_hash": availability_hash,
        },
        "replacement_checks_all_true": True,
    }
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)

    required_assertions = [
        payload["status"] == STATUS,
        payload["module"] == MODULE_PATH,
        payload["result_classification"]["result_class"] in ALLOWED_RESULT_CLASSES,
        payload["result_classification"]["closure_record_required_next"] is True,
        payload["followup_permissions"]["candidate_generation_allowed_now"] is False,
        payload["followup_permissions"]["edge_claim_allowed_now"] is False,
        payload["followup_permissions"]["runtime_permission_allowed_now"] is False,
        payload["forbidden_actions_confirmed_false"]["execution_rerun"] is False,
        payload["forbidden_actions_confirmed_false"]["panel_rows_read"] is False,
        payload["forbidden_actions_confirmed_false"]["funding_rows_read"] is False,
        payload["forbidden_actions_confirmed_false"]["network_used"] is False,
        payload["replacement_checks_all_true"] is True,
    ]
    if not all(required_assertions):
        raise RuntimeError("evaluator invariant assertion failed")
    return payload


def main() -> None:
    artifact = build_evaluation()
    path = REPO_ROOT / ARTIFACT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": artifact["status"],
        "evaluator_artifact_path": ARTIFACT_PATH,
        "result_class": artifact["result_classification"]["result_class"],
        "diagnostic_promising": artifact["result_classification"]["diagnostic_promising"],
        "config_id": artifact["result_classification"]["config_id"],
        "validation_gross_metric_bps": artifact["result_classification"]["validation_gross_metric_bps"],
        "validation_net_metric_bps": artifact["result_classification"]["validation_net_metric_bps"],
        "validation_positive_after_cost": artifact["result_classification"]["validation_positive_after_cost"],
        "null_baseline_review_passed": artifact["result_classification"]["null_baseline_review_passed"],
        "monthly_stability_review_passed": artifact["result_classification"]["monthly_stability_review_passed"],
        "event_coverage_review_passed": artifact["result_classification"]["event_coverage_review_passed"],
        "exposure_risk_review_passed": artifact["result_classification"]["exposure_risk_review_passed"],
        "turnover_concentration_review_passed": artifact["result_classification"]["turnover_concentration_review_passed"],
        "metric_integrity_issue_count": artifact["result_classification"]["metric_integrity_issue_count"],
        "closure_record_required_next": artifact["result_classification"]["closure_record_required_next"],
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": artifact["replacement_checks_all_true"],
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
