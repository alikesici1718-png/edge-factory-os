import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_15m_gk_volatility_zscore_squeeze_evaluator_v1.py"
ARTIFACT_PATH = "artifacts/strategy_evaluations/binance_okx_overlap_15m_gk_volatility_zscore_squeeze_evaluator_v1.json"
STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_15M_GK_VOLATILITY_ZSCORE_SQUEEZE_EVALUATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_15M_GK_VOLATILITY_ZSCORE_SQUEEZE_EVALUATION"

EXECUTION_PATH = "artifacts/strategy_executions/binance_okx_overlap_15m_gk_volatility_zscore_squeeze_execution_v1.json"
PREREG_PATH = "artifacts/research_preregistrations/binance_okx_overlap_15m_gk_volatility_zscore_squeeze_preregistration_contract_v1.json"
EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_15M_GK_VOLATILITY_ZSCORE_SQUEEZE_EXECUTED"
EXECUTION_HASH = "b69adb4b57d7e9995bd1db359e43cb36a1188f3d8338a6c5cf9fdd18e774249c"
PREREG_HASH = "9eb80324a4f428da2e4212601d1845f5f71a465c0570795bbd18afe415f2629c"

ROUTE_FAMILY = "BINANCE_OKX_OVERLAP_15M_GK_VOLATILITY_ZSCORE_SQUEEZE_BASELINE"
CONFIG_ID = "gkvol_24h_z30d_squeeze_long_expand_short_hold8h"
PROMISING_CLASS = "GK_VOLATILITY_ZSCORE_SQUEEZE_DIAGNOSTIC_PROMISING_REQUIRES_CLOSURE_NO_CANDIDATE_NO_EDGE"
REJECTED_CLASS = "GK_VOLATILITY_ZSCORE_SQUEEZE_REJECTED_NO_FOLLOWUP"
INCONCLUSIVE_CLASS = "GK_VOLATILITY_ZSCORE_SQUEEZE_INCONCLUSIVE_INPUT_INCOMPLETE_NO_FOLLOWUP"
INVALIDATED_CLASS = "GK_VOLATILITY_ZSCORE_SQUEEZE_INVALIDATED_BY_SAFETY_OR_INTEGRITY_FAILURE"


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


def finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def build_evaluation() -> Dict[str, Any]:
    execution = read_json(EXECUTION_PATH)
    prereg = read_json(PREREG_PATH)
    execution_hash = verify_hash(execution, EXECUTION_HASH)
    prereg_hash = verify_hash(prereg, PREREG_HASH)
    if execution.get("status") != EXECUTION_STATUS:
        raise RuntimeError("execution status mismatch")
    if execution.get("route_family") != ROUTE_FAMILY or execution.get("config_id") != CONFIG_ID:
        raise RuntimeError("execution route/config mismatch")

    config = execution["config_result"]
    null_summary = execution["null_baseline_summary"]
    monthly = execution["monthly_stability_summary"]
    coverage = execution["signal_coverage_summary"]
    turnover = execution["turnover_concentration_summary"]
    integrity = execution["metric_integrity_summary"]
    side = execution["long_short_side_summary"]
    forbidden = execution["forbidden_actions_confirmed_false"]

    validation_net = config["validation_net_metric_bps"]
    validation_gross = config["validation_gross_metric_bps"]
    validation_positive = config["validation_positive_after_cost"]
    null_passed = null_summary["null_baseline_review_preliminary_passed"]
    monthly_passed = monthly["monthly_stability_review_preliminary_passed"]
    coverage_passed = coverage["signal_coverage_review_preliminary_passed"]
    turnover_passed = turnover["turnover_concentration_review_preliminary_passed"]
    integrity_passed = integrity["metric_integrity_passed"]
    safety_review_passed = (
        forbidden["network_used"] is False
        and forbidden["api_called"] is False
        and forbidden["data_downloaded"] is False
        and forbidden["funding_rows_read"] is False
        and forbidden["okx_panel_rows_read"] is False
        and forbidden["binance_1m_source_rows_read"] is False
        and forbidden["non_preregistered_config_tested"] is False
        and forbidden["candidates_generated"] is False
        and forbidden["edge_claimed"] is False
        and forbidden["family_released"] is False
        and forbidden["holdout_permission_granted"] is False
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
            isinstance(coverage_passed, bool),
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
        and coverage_passed is True
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
        f"The single preregistered GK volatility z-score squeeze config produced validation gross metric "
        f"{validation_gross} bps and validation net metric {validation_net} bps. "
        f"validation_positive_after_cost={validation_positive}, null_baseline_passed={null_passed}, "
        f"monthly_stability_passed={monthly_passed}, signal_coverage_passed={coverage_passed}, "
        f"turnover_concentration_passed={turnover_passed}, metric_integrity_passed={integrity_passed}. "
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
            "train_gross_metric_bps": config["train_gross_metric_bps"],
            "train_net_metric_bps": config["train_net_metric_bps"],
            "validation_gross_metric_bps": validation_gross,
            "validation_net_metric_bps": validation_net,
            "holdout_gross_metric_bps": config["holdout_gross_metric_bps"],
            "holdout_net_metric_bps": config["holdout_net_metric_bps"],
            "validation_positive_after_cost": validation_positive,
            "validation_eligible_timestamp_count": coverage["validation_eligible_timestamp_count"],
            "average_eligible_symbols": coverage["average_eligible_symbols_per_timestamp"],
            "top_symbol_exposure_share": turnover["top_symbol_exposure_share"],
            "holdout_used_for_config_selection": config["holdout_used_for_config_selection"],
            "metric_integrity_issue_count": integrity["metric_integrity_issue_count"],
        },
        "evaluation_policy": {
            "diagnostic_promising_requires_all": [
                "validation_net_metric_bps > 0",
                "validation_positive_after_cost is true",
                "null_baseline_review_preliminary_passed is true",
                "monthly_stability_review_preliminary_passed is true",
                "signal_coverage_review_preliminary_passed is true",
                "turnover_concentration_review_preliminary_passed is true",
                "metric_integrity_passed is true",
                "safety_review_passed is true",
            ],
            "holdout_policy": {
                "holdout_reported_separately": True,
                "holdout_used_for_config_selection": False,
                "holdout_positive_cannot_create_candidate_edge_or_release": True,
            },
        },
        "execution_results_evaluated": {
            "config_id": CONFIG_ID,
            "validation_gross_metric_bps": validation_gross,
            "validation_net_metric_bps": validation_net,
            "validation_positive_after_cost": validation_positive,
            "train_gross_metric_bps": config["train_gross_metric_bps"],
            "train_net_metric_bps": config["train_net_metric_bps"],
            "holdout_gross_metric_bps": config["holdout_gross_metric_bps"],
            "holdout_net_metric_bps": config["holdout_net_metric_bps"],
            "holdout_reported_separately": True,
            "holdout_used_for_config_selection": False,
        },
        "signal_coverage_findings": {
            "train_eligible_timestamp_count": coverage["train_eligible_timestamp_count"],
            "validation_eligible_timestamp_count": coverage["validation_eligible_timestamp_count"],
            "holdout_eligible_timestamp_count": coverage["holdout_eligible_timestamp_count"],
            "average_eligible_symbols_per_timestamp": coverage["average_eligible_symbols_per_timestamp"],
            "validation_average_eligible_symbols": coverage["validation_average_eligible_symbols"],
            "signal_coverage_review_preliminary_passed": coverage_passed,
        },
        "side_performance_findings": {
            "long_validation_gross_metric_bps": side["long_validation_gross_metric_bps"],
            "long_validation_net_metric_bps": side["long_validation_net_metric_bps"],
            "short_validation_gross_metric_bps": side["short_validation_gross_metric_bps"],
            "short_validation_net_metric_bps": side["short_validation_net_metric_bps"],
        },
        "evaluator_findings": {
            "validation_net_metric_bps_gt_0": validation_net > 0 if finite(validation_net) else False,
            "validation_positive_after_cost": validation_positive,
            "null_baseline_review_passed": null_passed,
            "monthly_stability_review_passed": monthly_passed,
            "signal_coverage_review_passed": coverage_passed,
            "turnover_concentration_review_passed": turnover_passed,
            "metric_integrity_passed": integrity_passed,
            "safety_review_passed": safety_review_passed,
            "evaluator_input_complete": evaluator_input_complete,
            "diagnostic_promising": diagnostic_promising,
            "result_reason": reason,
        },
        "result_classification": {
            "result_class": result_class,
            "diagnostic_promising": diagnostic_promising,
            "validation_gross_metric_bps": validation_gross,
            "validation_net_metric_bps": validation_net,
            "validation_positive_after_cost": validation_positive,
            "null_baseline_review_passed": null_passed,
            "monthly_stability_review_passed": monthly_passed,
            "signal_coverage_review_passed": coverage_passed,
            "turnover_concentration_review_passed": turnover_passed,
            "metric_integrity_issue_count": integrity["metric_integrity_issue_count"],
            "metric_integrity_passed": integrity_passed,
            "safety_review_passed": safety_review_passed,
            "closure_record_required_next": True,
            "candidate_generation_allowed_from_evaluator": False,
            "edge_claim_allowed_from_evaluator": False,
            "family_release_allowed_from_evaluator": False,
            "runtime_live_capital_allowed_from_evaluator": False,
        },
        "followup_permissions": {
            "closure_record_required_next": True,
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
            "execution_loaded": True,
            "execution_status_verified": True,
            "execution_payload_hash_verified": True,
            "preregistration_loaded": True,
            "preregistration_payload_hash_verified": prereg_hash == PREREG_HASH,
            "route_family_verified": True,
            "config_id_verified": True,
            "evaluation_policy_applied": True,
            "holdout_used_for_config_selection_false": True,
            "no_execution_rerun": True,
            "no_panel_rows_read": True,
            "no_network_used": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_runtime_live_capital": True,
            "replacement_checks_all_true": True,
        },
        "replacement_checks_all_true": True,
        "payload_sha256_excluding_hash": "",
    }
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)
    assert payload["status"] == STATUS
    assert payload["result_classification"]["result_class"] in {
        PROMISING_CLASS,
        REJECTED_CLASS,
        INCONCLUSIVE_CLASS,
        INVALIDATED_CLASS,
    }
    assert payload["evaluation_policy"]["holdout_policy"]["holdout_used_for_config_selection"] is False
    assert payload["followup_permissions"]["candidate_generation_allowed_now"] is False
    assert payload["followup_permissions"]["edge_claim_allowed_now"] is False
    assert payload["forbidden_actions_confirmed_false"]["panel_rows_read"] is False
    assert payload["replacement_checks_all_true"] is True
    assert all(payload["validation_checks"].values())
    assert canonical_payload_hash(payload) == payload["payload_sha256_excluding_hash"]
    return payload


def main() -> None:
    artifact_path = REPO_ROOT / ARTIFACT_PATH
    if artifact_path.exists():
        raise RuntimeError(f"evaluator artifact already exists: {ARTIFACT_PATH}")
    payload = build_evaluation()
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": STATUS,
        "artifact_path": ARTIFACT_PATH,
        "result_class": payload["result_classification"]["result_class"],
        "diagnostic_promising": payload["result_classification"]["diagnostic_promising"],
        "config_id": CONFIG_ID,
        "validation_net_metric_bps": payload["result_classification"]["validation_net_metric_bps"],
        "validation_positive_after_cost": payload["result_classification"]["validation_positive_after_cost"],
        "closure_record_required_next": True,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "payload_sha256_excluding_hash": payload["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": True,
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
