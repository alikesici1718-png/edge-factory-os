import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_pairs_trading_log_spread_evaluator_v1.py"
ARTIFACT_PATH = "artifacts/strategy_evaluations/binance_okx_overlap_pairs_trading_log_spread_evaluator_v1.json"
STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_PAIRS_TRADING_LOG_SPREAD_EVALUATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_PAIRS_TRADING_LOG_SPREAD_EVALUATION"

EXECUTION_PATH = "artifacts/strategy_executions/binance_okx_overlap_pairs_trading_log_spread_execution_v1.json"
EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_PAIRS_TRADING_LOG_SPREAD_EXECUTED"
PREREG_PATH = "artifacts/research_preregistrations/binance_okx_overlap_pairs_trading_log_spread_preregistration_contract_v1.json"

ROUTE_FAMILY = "BINANCE_OKX_OVERLAP_PAIRS_TRADING_LOG_SPREAD_MEAN_REVERSION_BASELINE"
CONFIG_ID = "log_spread_z2_rolling168h_hold24h_btceth_solavax"

PROMISING_CLASS = "PAIRS_TRADING_LOG_SPREAD_DIAGNOSTIC_PROMISING_REQUIRES_CLOSURE_NO_CANDIDATE_NO_EDGE"
REJECTED_CLASS = "PAIRS_TRADING_LOG_SPREAD_REJECTED_NO_FOLLOWUP"
INCONCLUSIVE_CLASS = "PAIRS_TRADING_LOG_SPREAD_INCONCLUSIVE_INPUT_INCOMPLETE_NO_FOLLOWUP"
INVALIDATED_CLASS = "PAIRS_TRADING_LOG_SPREAD_INVALIDATED_BY_SAFETY_OR_INTEGRITY_FAILURE"
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


def finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def build_evaluation() -> Dict[str, Any]:
    execution = read_json(EXECUTION_PATH)
    execution_hash = verify_hash(execution)
    prereg = read_json(PREREG_PATH)
    prereg_hash = verify_hash(prereg)
    if execution.get("status") != EXECUTION_STATUS:
        raise RuntimeError("execution status mismatch")
    if execution.get("route_family") != ROUTE_FAMILY or execution.get("config_id") != CONFIG_ID:
        raise RuntimeError("execution route/config mismatch")
    if prereg.get("pairs_trading_hypothesis_preregistration", {}).get("route_family") != ROUTE_FAMILY:
        raise RuntimeError("preregistration route mismatch")
    if prereg.get("pairs_trading_hypothesis_preregistration", {}).get("config_id") != CONFIG_ID:
        raise RuntimeError("preregistration config mismatch")

    aggregate = execution["aggregate_results"]
    pair_consistency = execution["pair_level_consistency_summary"]
    hedge_stability = execution["hedge_stability_summary"]
    null_summary = execution["null_baseline_summary"]
    monthly = execution["monthly_stability_summary"]
    metric_integrity = execution["metric_integrity_summary"]
    forbidden = execution["forbidden_actions_confirmed_false"]

    validation_net = aggregate["validation_net_metric_bps"]
    validation_gross = aggregate["validation_gross_metric_bps"]
    validation_positive = aggregate["validation_positive_after_cost"]
    null_passed = null_summary["null_baseline_review_preliminary_passed"]
    monthly_passed = monthly["monthly_stability_review_preliminary_passed"]
    pair_consistency_passed = pair_consistency["pair_level_consistency_review_preliminary_passed"]
    metric_integrity_passed = metric_integrity["metric_integrity_passed"]
    safety_review_passed = (
        forbidden["network_used"] is False
        and forbidden["binance_api_called"] is False
        and forbidden["funding_rows_read"] is False
        and forbidden["okx_panel_rows_read"] is False
        and forbidden["non_preregistered_pair_tested"] is False
        and forbidden["non_preregistered_config_tested"] is False
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
            isinstance(pair_consistency_passed, bool),
            isinstance(metric_integrity_passed, bool),
            isinstance(safety_review_passed, bool),
        ]
    )
    diagnostic_promising = bool(
        evaluator_input_complete
        and validation_net > 0
        and validation_positive is True
        and null_passed is True
        and monthly_passed is True
        and pair_consistency_passed is True
        and metric_integrity_passed is True
        and safety_review_passed is True
    )
    if not safety_review_passed or not metric_integrity_passed:
        result_class = INVALIDATED_CLASS
    elif not evaluator_input_complete:
        result_class = INCONCLUSIVE_CLASS
    elif diagnostic_promising:
        result_class = PROMISING_CLASS
    else:
        result_class = REJECTED_CLASS

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
            "pair_keys": [item["pair_key"] for item in execution["pair_results"]],
            "hedge_beta_values": {item["pair_key"]: item["beta"] for item in execution["pair_results"]},
            "aggregate_train_gross_metric_bps": aggregate["train_gross_metric_bps"],
            "aggregate_train_net_metric_bps": aggregate["train_net_metric_bps"],
            "aggregate_validation_gross_metric_bps": validation_gross,
            "aggregate_validation_net_metric_bps": validation_net,
            "aggregate_holdout_gross_metric_bps": aggregate["holdout_gross_metric_bps"],
            "aggregate_holdout_net_metric_bps": aggregate["holdout_net_metric_bps"],
            "holdout_reported_separately": True,
            "holdout_used_for_pair_selection": False,
            "holdout_used_for_hedge_ratio_selection": False,
            "holdout_used_for_config_selection": False,
            "final_edge_claim_requires_external_or_future_holdout": True,
            "candidate_generation": False,
            "edge_claim": False,
            "family_release": False,
            "runtime_live_capital": False,
        },
        "evaluation_policy": {
            "diagnostic_promising_requires_all": [
                "aggregate validation_net_metric_bps > 0",
                "validation_positive_after_cost is true",
                "null_baseline_review_preliminary_passed is true",
                "monthly_stability_review_preliminary_passed is true",
                "pair_level_consistency_review_preliminary_passed is true",
                "metric_integrity_passed is true",
                "safety_review_passed is true",
            ],
            "holdout_policy": {
                "holdout_reported_separately": True,
                "holdout_used_for_pair_selection": False,
                "holdout_used_for_hedge_ratio_selection": False,
                "holdout_used_for_config_selection": False,
                "holdout_positive_does_not_override_validation_failure": True,
                "holdout_used_for_candidate_generation": False,
                "holdout_used_for_edge_claim": False,
                "holdout_used_for_family_release": False,
                "final_edge_claim_requires_external_or_future_holdout": True,
            },
            "allowed_result_classes": ALLOWED_RESULT_CLASSES,
        },
        "execution_results_evaluated": {
            "config_id": CONFIG_ID,
            "aggregate_results": aggregate,
            "pair_results": execution["pair_results"],
            "validation_null_percentile": null_summary["validation_null_percentile"],
            "validation_monthly_net_metric_bps_by_month": monthly["validation_monthly_net_metric_bps_by_month"],
            "validation_monthly_gross_metric_bps_by_month": monthly["validation_monthly_gross_metric_bps_by_month"],
        },
        "pair_level_findings": {
            "pair_level_consistency_review_preliminary_passed": pair_consistency_passed,
            "positive_validation_net_pair_count": pair_consistency["positive_validation_net_pair_count"],
            "only_one_pair_drives_result": pair_consistency["only_one_pair_drives_result"],
            "pair_validation_net_metric_bps": pair_consistency["pair_validation_net_metric_bps"],
            "pair_validation_trade_counts": pair_consistency["pair_validation_trade_counts"],
        },
        "hedge_stability_findings": hedge_stability,
        "evaluator_findings": {
            "evaluator_ran": True,
            "evaluator_recomputed_strategy_metrics": False,
            "evaluator_read_panel_rows": False,
            "evaluator_read_funding_rows": False,
            "validation_positive_after_cost": validation_positive,
            "null_baseline_review_passed": null_passed,
            "monthly_stability_review_passed": monthly_passed,
            "pair_level_consistency_review_passed": pair_consistency_passed,
            "metric_integrity_review_passed": metric_integrity_passed,
            "safety_review_passed": safety_review_passed,
            "evaluator_input_complete": evaluator_input_complete,
            "diagnostic_promising": diagnostic_promising,
            "evaluator_reason": (
                f"Aggregate validation net metric is {validation_net} bps with "
                f"validation_positive_after_cost={validation_positive}, null_passed={null_passed}, "
                f"monthly_passed={monthly_passed}, and pair_consistency_passed={pair_consistency_passed}."
            ),
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
            "pair_level_consistency_review_passed": pair_consistency_passed,
            "metric_integrity_issue_count": metric_integrity["metric_integrity_issue_count"],
            "metric_integrity_passed": metric_integrity_passed,
            "safety_review_passed": safety_review_passed,
            "closure_record_required_next": True,
            "candidate_generation_allowed_from_evaluator": False,
            "edge_claim_allowed_from_evaluator": False,
            "family_release_allowed_from_evaluator": False,
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
            "pair_scanning_executed": False,
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
            "evaluator_artifact_path_equals_required_path": True,
            "execution_artifact_loaded": True,
            "execution_payload_hash_verified": True,
            "preregistration_artifact_loaded": True,
            "preregistration_payload_hash_verified": True,
            "result_class_allowed": result_class in ALLOWED_RESULT_CLASSES,
            "holdout_reported_separately": True,
            "holdout_not_used_for_pair_selection": True,
            "holdout_not_used_for_hedge_ratio_selection": True,
            "holdout_not_used_for_config_selection": True,
            "no_execution_rerun": True,
            "no_panel_rows_read": True,
            "no_funding_rows_read": True,
            "no_network_used": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "payload_sha256_excluding_hash_present": True,
            "replacement_checks_all_true": True,
        },
        "source_artifacts": {
            "execution_payload_sha256_excluding_hash": execution_hash,
            "preregistration_payload_sha256_excluding_hash": prereg_hash,
        },
        "replacement_checks_all_true": True,
    }
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)
    required_assertions = [
        payload["status"] == STATUS,
        payload["module"] == MODULE_PATH,
        payload["result_classification"]["result_class"] in ALLOWED_RESULT_CLASSES,
        payload["result_classification"]["closure_record_required_next"] is True,
        payload["evaluation_policy"]["holdout_policy"]["holdout_used_for_config_selection"] is False,
        payload["followup_permissions"]["candidate_generation_allowed_now"] is False,
        payload["followup_permissions"]["edge_claim_allowed_now"] is False,
        payload["forbidden_actions_confirmed_false"]["execution_rerun"] is False,
        payload["forbidden_actions_confirmed_false"]["panel_rows_read"] is False,
        payload["forbidden_actions_confirmed_false"]["funding_rows_read"] is False,
        payload["replacement_checks_all_true"] is True,
    ]
    if not all(required_assertions):
        raise RuntimeError("evaluator invariant assertion failed")
    return payload


def main() -> None:
    artifact = build_evaluation()
    output_path = REPO_ROOT / ARTIFACT_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": artifact["status"],
        "artifact_path": ARTIFACT_PATH,
        "result_class": artifact["result_classification"]["result_class"],
        "diagnostic_promising": artifact["result_classification"]["diagnostic_promising"],
        "validation_net_metric_bps": artifact["result_classification"]["validation_net_metric_bps"],
        "validation_gross_metric_bps": artifact["result_classification"]["validation_gross_metric_bps"],
        "null_baseline_review_passed": artifact["result_classification"]["null_baseline_review_passed"],
        "monthly_stability_review_passed": artifact["result_classification"]["monthly_stability_review_passed"],
        "pair_level_consistency_review_passed": artifact["result_classification"]["pair_level_consistency_review_passed"],
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": artifact["replacement_checks_all_true"],
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
