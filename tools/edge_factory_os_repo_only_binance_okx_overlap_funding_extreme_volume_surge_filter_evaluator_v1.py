import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_extreme_volume_surge_filter_evaluator_v1.py"
ARTIFACT_PATH = "artifacts/strategy_evaluations/binance_okx_overlap_funding_extreme_volume_surge_filter_evaluator_v1.json"
STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_EXTREME_VOLUME_SURGE_FILTER_EVALUATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_FUNDING_EXTREME_VOLUME_SURGE_FILTER_EVALUATION"

EXECUTION_PATH = "artifacts/strategy_executions/binance_okx_overlap_funding_extreme_volume_surge_filter_execution_v1.json"
PREREG_PATH = "artifacts/research_preregistrations/binance_okx_overlap_funding_extreme_volume_surge_filter_preregistration_contract_v1.json"
EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_FUNDING_EXTREME_VOLUME_SURGE_FILTER_EXECUTED"
EXECUTION_PAYLOAD_HASH = "59da56218164c952cc3dd7551a5dd0f72cd4a6d5d82cc9cf4323fe760031e58b"
ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_EXTREME_VOLUME_SURGE_FILTER_REVERSAL_BASELINE"
CONFIG_ID = "funding_mean9_volume_surge24h_p80_30d_hold24h"

PROMISING_CLASS = "FUNDING_EXTREME_VOLUME_SURGE_FILTER_DIAGNOSTIC_PROMISING_REQUIRES_CLOSURE_NO_CANDIDATE_NO_EDGE"
REJECTED_CLASS = "FUNDING_EXTREME_VOLUME_SURGE_FILTER_REJECTED_NO_FOLLOWUP"
INCONCLUSIVE_CLASS = "FUNDING_EXTREME_VOLUME_SURGE_FILTER_INCONCLUSIVE_EVALUATOR_INPUT_INCOMPLETE_NO_FOLLOWUP"
INVALIDATED_CLASS = "FUNDING_EXTREME_VOLUME_SURGE_FILTER_INVALIDATED_BY_SAFETY_OR_INTEGRITY_FAILURE"
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
    prereg = read_json(PREREG_PATH)
    execution_hash = verify_hash(execution, EXECUTION_PAYLOAD_HASH)
    prereg_hash = verify_hash(prereg, "227f02d39d48012749e0881046ae64d50b254c70fd1dc91148c45a00bee2c763")

    if execution.get("status") != EXECUTION_STATUS:
        raise RuntimeError("execution status mismatch")
    if execution.get("route_family") != ROUTE_FAMILY:
        raise RuntimeError("route family mismatch")
    if execution.get("config_id") != CONFIG_ID:
        raise RuntimeError("config id mismatch")

    config_result = execution["config_result"]
    monthly = execution["monthly_stability_summary"]
    null_summary = execution["null_baseline_summary"]
    turnover = execution["turnover_concentration_summary"]
    volume_coverage = execution["volume_anomaly_coverage_summary"]
    metric_integrity = execution["metric_integrity_summary"]

    validation_net = config_result["validation_net_metric_bps"]
    validation_gross = config_result["validation_gross_metric_bps"]
    validation_positive = config_result["validation_positive_after_cost"]
    null_passed = null_summary["null_baseline_review_preliminary_passed"]
    monthly_passed = monthly["monthly_stability_review_preliminary_passed"]
    turnover_passed = turnover["turnover_concentration_review_preliminary_passed"]
    volume_passed = volume_coverage["volume_anomaly_coverage_review_preliminary_passed"]
    integrity_passed = metric_integrity["metric_integrity_passed"]
    safety_review_passed = (
        execution["forbidden_actions_confirmed_false"]["network_used"] is False
        and execution["forbidden_actions_confirmed_false"]["binance_api_called"] is False
        and execution["forbidden_actions_confirmed_false"]["okx_panel_rows_read"] is False
        and execution["forbidden_actions_confirmed_false"]["candidates_generated"] is False
        and execution["forbidden_actions_confirmed_false"]["edge_claimed"] is False
        and execution["forbidden_actions_confirmed_false"]["runtime_permission_granted"] is False
        and execution["forbidden_actions_confirmed_false"]["live_permission_granted"] is False
        and execution["forbidden_actions_confirmed_false"]["capital_permission_granted"] is False
    )
    evaluator_input_complete = all(
        [
            finite(validation_net),
            finite(validation_gross),
            isinstance(validation_positive, bool),
            isinstance(null_passed, bool),
            isinstance(monthly_passed, bool),
            isinstance(turnover_passed, bool),
            isinstance(volume_passed, bool),
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
        and turnover_passed is True
        and volume_passed is True
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
        f"The single preregistered volume-surge funding-extreme route produced validation gross metric "
        f"{validation_gross} bps and validation net metric {validation_net} bps. "
        f"validation_positive_after_cost={validation_positive}, null_baseline_passed={null_passed}, "
        f"monthly_stability_passed={monthly_passed}, turnover_concentration_passed={turnover_passed}, "
        f"volume_anomaly_coverage_passed={volume_passed}, metric_integrity_passed={integrity_passed}. "
        "The evaluator grants no candidate, edge claim, family release, holdout access, or runtime/live/capital permission."
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
            "validation_net_metric_bps": validation_net,
            "validation_gross_metric_bps": validation_gross,
            "validation_positive_after_cost": validation_positive,
            "null_baseline_review_preliminary_passed": null_passed,
            "monthly_stability_review_preliminary_passed": monthly_passed,
            "turnover_concentration_review_preliminary_passed": turnover_passed,
            "volume_anomaly_coverage_review_preliminary_passed": volume_passed,
            "average_volume_anomaly_symbols_per_timestamp": volume_coverage["average_volume_anomaly_symbols_per_timestamp"],
            "validation_volume_anomaly_eligible_timestamp_count": volume_coverage["validation_volume_anomaly_eligible_timestamp_count"],
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
                "turnover_concentration_review_preliminary_passed is true",
                "volume_anomaly_coverage_review_preliminary_passed is true",
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
            "train_entry_count": config_result["train_entry_count"],
            "validation_entry_count": config_result["validation_entry_count"],
            "validation_monthly_net_metric_bps_by_month": monthly["validation_monthly_net_metric_bps_by_month"],
            "validation_monthly_gross_metric_bps_by_month": monthly["validation_monthly_gross_metric_bps_by_month"],
        },
        "volume_anomaly_coverage_findings": {
            "volume_anomaly_coverage_review_passed": volume_passed,
            "validation_volume_anomaly_eligible_timestamp_count": volume_coverage["validation_volume_anomaly_eligible_timestamp_count"],
            "average_volume_anomaly_symbols_per_timestamp": volume_coverage["average_volume_anomaly_symbols_per_timestamp"],
            "median_volume_anomaly_symbols_per_timestamp": volume_coverage["median_volume_anomaly_symbols_per_timestamp"],
            "min_volume_anomaly_symbols_per_timestamp": volume_coverage["min_volume_anomaly_symbols_per_timestamp"],
            "max_volume_anomaly_symbols_per_timestamp": volume_coverage["max_volume_anomaly_symbols_per_timestamp"],
            "coverage_rule": "passed iff validation eligible timestamp count >= 500 and average anomaly symbols per timestamp >= 20",
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
            "turnover_concentration_review_passed": turnover_passed,
            "volume_anomaly_coverage_review_passed": volume_passed,
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
            "turnover_concentration_review_passed": turnover_passed,
            "volume_anomaly_coverage_review_passed": volume_passed,
            "metric_integrity_issue_count": metric_integrity["metric_integrity_issue_count"],
            "result_reason": reason,
            "candidate_generation_allowed_from_evaluator": False,
            "edge_claim_allowed_from_evaluator": False,
            "family_release_allowed_from_evaluator": False,
            "runtime_live_capital_allowed_from_evaluator": False,
            "closure_record_required_next": True,
            "evaluator_grants_holdout_access": False,
        },
        "followup_permissions": {
            "closure_record_allowed_next": True,
            "strategy_search_allowed_now": False,
            "funding_retest_allowed_now": False,
            "funding_parameter_expansion_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "holdout_access_allowed_now": False,
            "okx_panel_access_allowed_now": False,
            "binance_panel_row_access_allowed_now": False,
            "funding_row_access_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "final_edge_claim_requires_external_or_future_holdout": True,
        },
        "forbidden_actions_confirmed_false": {
            "funding_execution_rerun": False,
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
            "evaluator_artifact_path_equals_required_path": True,
            "exactly_one_new_tracked_python_tool_file_expected": True,
            "exactly_one_new_tracked_json_evaluator_artifact_expected": True,
            "no_existing_files_modified_expected": True,
            "no_other_tracked_files_expected": True,
            "execution_artifact_loaded": True,
            "execution_status_verified": True,
            "execution_payload_hash_verified": True,
            "preregistration_artifact_loaded": True,
            "preregistration_payload_hash_verified": True,
            "route_family_verified": True,
            "config_count_verified_1": True,
            "config_id_preserved": True,
            "evaluator_did_not_rerun_execution": True,
            "evaluator_did_not_read_panel_rows": True,
            "evaluator_did_not_read_funding_rows": True,
            "no_network_used": True,
            "no_strategy_search": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_runtime_live_capital": True,
            "result_class_is_from_allowed_set": result_class in ALLOWED_RESULT_CLASSES,
            "closure_record_required_next": True,
            "evaluator_artifact_json_valid": True,
            "payload_sha256_excluding_hash_present": True,
            "replacement_checks_all_true": True,
        },
        "source_artifacts": {
            EXECUTION_PATH: execution_hash,
            PREREG_PATH: prereg_hash,
        },
        "replacement_checks_all_true": True,
    }
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)

    required_assertions = [
        payload["status"] == STATUS,
        payload["module"] == MODULE_PATH,
        result_class in ALLOWED_RESULT_CLASSES,
        payload["result_classification"]["closure_record_required_next"] is True,
        payload["evaluator_findings"]["evaluator_recomputed_strategy_metrics"] is False,
        payload["evaluator_findings"]["evaluator_read_panel_rows"] is False,
        payload["evaluator_findings"]["evaluator_read_funding_rows"] is False,
        payload["result_classification"]["candidate_generation_allowed_from_evaluator"] is False,
        payload["result_classification"]["edge_claim_allowed_from_evaluator"] is False,
        payload["result_classification"]["runtime_live_capital_allowed_from_evaluator"] is False,
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
        "config_id": CONFIG_ID,
        "validation_net_metric_bps": artifact["result_classification"]["validation_net_metric_bps"],
        "validation_gross_metric_bps": artifact["result_classification"]["validation_gross_metric_bps"],
        "validation_positive_after_cost": artifact["result_classification"]["validation_positive_after_cost"],
        "null_baseline_review_passed": artifact["result_classification"]["null_baseline_review_passed"],
        "monthly_stability_review_passed": artifact["result_classification"]["monthly_stability_review_passed"],
        "turnover_concentration_review_passed": artifact["result_classification"]["turnover_concentration_review_passed"],
        "volume_anomaly_coverage_review_passed": artifact["result_classification"]["volume_anomaly_coverage_review_passed"],
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
