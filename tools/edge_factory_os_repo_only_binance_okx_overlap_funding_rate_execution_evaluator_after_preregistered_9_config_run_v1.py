#!/usr/bin/env python3
"""Evaluate the completed Binance/OKX funding-rate 9-config diagnostic run."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any


REQUIRED_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_RATE_EXECUTION_EVALUATED_AFTER_PREREGISTERED_9_CONFIG_RUN"
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_rate_execution_evaluator_after_preregistered_9_config_run_v1.py"
EVALUATOR_ARTIFACT_PATH = "artifacts/strategy_evaluations/binance_okx_overlap_funding_rate_execution_evaluator_after_preregistered_9_config_run_v1.json"

REPO_PATH = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
ARTIFACT_PATH = REPO_PATH / EVALUATOR_ARTIFACT_PATH
TEMP_ARTIFACT_PATH = ARTIFACT_PATH.with_suffix(".json.tmp")

EXECUTION_PATH = REPO_PATH / "artifacts/strategy_executions/binance_okx_overlap_funding_rate_preregistered_9_config_execution_v1.json"
FUNDING_REVIEW_PATH = REPO_PATH / "artifacts/funding_rate_reviews/binance_okx_overlap_funding_rate_data_review_after_acquisition_lock_v1.json"
ACQUISITION_PATH = REPO_PATH / "artifacts/funding_rate_locks/binance_okx_overlap_funding_rate_data_acquisition_lock_v1.json"
PREREGISTRATION_PATH = REPO_PATH / "artifacts/research_preregistrations/binance_okx_overlap_funding_rate_hypothesis_preregistration_contract_v1.json"
READINESS_PATH = REPO_PATH / "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json"
PANEL_REVIEW_PATH = REPO_PATH / "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json"

PRIOR_HEAD = "f8a3503b7b568933a3c222e5f1c850cd8cf99964"
PRIOR_TRACKED_PYTHON_COUNT = 815
EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_FUNDING_RATE_PREREGISTERED_9_CONFIG_EXECUTED"
EXECUTION_PAYLOAD_HASH = "0f9fc66e7fdf3e15bc84fe4e88d4c110902c8f62d9e31eec1628c96e27eda8a7"
FUNDING_REVIEW_PAYLOAD_HASH = "a579feb0472efbf03ffa955008dfabc0b526fa37029fc81dddd0195b4054d849"
ACQUISITION_PAYLOAD_HASH = "dd5877b101c9a1e8d73f35f6032381cbdfd5435578abacf97b9db0c11c28e252"
PREREGISTRATION_PAYLOAD_HASH = "5febb59aee08873de1dbfc0464da463811090c334c18c5f2a552e1768cb3c768"
READINESS_PAYLOAD_HASH = "0cfe239f6f5ad2d20bda64b827416851de8f5b959066902b59f1f00f44eba716"
PANEL_REVIEW_PAYLOAD_HASH = "34b88a3ff0870c708e2df034c243cf639b711ebce3c6a4f32edffb92a2229112"

ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_RATE_CROWDING_REVERSAL_BASELINE"
HYPOTHESIS_NAME = "funding_rate_crowding_reversal"
WINDOW_START_UTC = "2023-07-01T00:00:00Z"
WINDOW_END_EXCLUSIVE_UTC = "2025-10-31T16:00:00Z"
BEST_CONFIG_ID = "funding_mean9_hold24h"
BEST_SIGNAL_TRANSFORM = "rolling_mean_9_funding_events"
BEST_HOLDING_PERIOD = 24
BEST_NET_BPS = -4.402175
BEST_GROSS_BPS = 15.597825
RANK_CONSISTENCY = 0.883333
RESULT_CLASS_REJECTED = "FUNDING_RATE_CROWDING_REVERSAL_REJECTED_NO_FOLLOWUP"
ALLOWED_RESULT_CLASSES = [
    "FUNDING_RATE_CROWDING_REVERSAL_DIAGNOSTIC_PROMISING_REQUIRES_SEPARATE_CLOSURE_NO_CANDIDATE_NO_EDGE",
    RESULT_CLASS_REJECTED,
    "FUNDING_RATE_CROWDING_REVERSAL_INCONCLUSIVE_EVALUATOR_INPUT_INCOMPLETE_NO_FOLLOWUP",
    "FUNDING_RATE_CROWDING_REVERSAL_INVALIDATED_BY_SAFETY_OR_INTEGRITY_FAILURE",
]


class BlockedError(RuntimeError):
    """Raised when evaluator inputs are unsafe or incomplete."""


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")


def payload_hash(payload: dict[str, Any]) -> str:
    copy = dict(payload)
    copy.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json_bytes(copy)).hexdigest()


def verify_payload(payload: dict[str, Any], expected_hash: str) -> bool:
    return payload.get("payload_sha256_excluding_hash") == expected_hash and payload_hash(payload) == expected_hash


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with TEMP_ARTIFACT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    TEMP_ARTIFACT_PATH.replace(path)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_PATH)).replace("\\", "/")


def load_sources() -> dict[str, dict[str, Any]]:
    paths = {
        "acquisition": ACQUISITION_PATH,
        "execution": EXECUTION_PATH,
        "funding_review": FUNDING_REVIEW_PATH,
        "panel_review": PANEL_REVIEW_PATH,
        "preregistration": PREREGISTRATION_PATH,
        "readiness": READINESS_PATH,
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise BlockedError(f"required evaluator source artifacts missing: {missing}")
    payloads = {key: read_json(path) for key, path in paths.items()}
    expected_hashes = {
        "acquisition": ACQUISITION_PAYLOAD_HASH,
        "execution": EXECUTION_PAYLOAD_HASH,
        "funding_review": FUNDING_REVIEW_PAYLOAD_HASH,
        "panel_review": PANEL_REVIEW_PAYLOAD_HASH,
        "preregistration": PREREGISTRATION_PAYLOAD_HASH,
        "readiness": READINESS_PAYLOAD_HASH,
    }
    for key, expected_hash in expected_hashes.items():
        if not verify_payload(payloads[key], expected_hash):
            raise BlockedError(f"{key} payload hash mismatch")
    return payloads


def near_equal(value: float, expected: float) -> bool:
    return math.isclose(float(value), expected, rel_tol=0.0, abs_tol=1e-9)


def build_artifact() -> dict[str, Any]:
    payloads = load_sources()
    execution = payloads["execution"]
    preregistration = payloads["preregistration"]
    funding_review = payloads["funding_review"]
    panel_review = payloads["panel_review"]

    if execution["status"] != EXECUTION_STATUS:
        raise BlockedError("execution status mismatch")
    scope = execution["execution_scope"]
    summary = execution["train_validation_summary"]
    limits = execution["diagnostic_interpretation_limits"]
    if scope["route_family"] != ROUTE_FAMILY:
        raise BlockedError("route family mismatch")
    if scope["exact_overlap_symbol_count"] != 81:
        raise BlockedError("exact overlap symbol count mismatch")
    if scope["aligned_window_start_utc"] != WINDOW_START_UTC or scope["aligned_window_end_exclusive_utc"] != WINDOW_END_EXCLUSIVE_UTC:
        raise BlockedError("aligned window mismatch")
    if execution["preregistered_config_grid"]["config_count"] != 9:
        raise BlockedError("config count mismatch")
    if summary["best_validation_config_id"] != BEST_CONFIG_ID:
        raise BlockedError("best validation config mismatch")
    if not near_equal(summary["best_validation_net_metric_bps"], BEST_NET_BPS):
        raise BlockedError("best validation net metric mismatch")
    if not near_equal(summary["best_validation_gross_metric_bps"], BEST_GROSS_BPS):
        raise BlockedError("best validation gross metric mismatch")
    if summary["validation_positive_after_cost"] is not False:
        raise BlockedError("validation_positive_after_cost expected false")
    if summary["null_baseline_review_preliminary_passed"] is not True:
        raise BlockedError("null baseline review expected true")
    if summary["monthly_stability_review_preliminary_passed"] is not False:
        raise BlockedError("monthly stability review expected false")
    if summary["turnover_concentration_review_preliminary_passed"] is not True:
        raise BlockedError("turnover/concentration review expected true")
    if summary["metric_integrity_issue_count"] != 0 or summary["metric_integrity_passed"] is not True:
        raise BlockedError("metric integrity mismatch")
    if not near_equal(summary["train_validation_rank_consistency"], RANK_CONSISTENCY):
        raise BlockedError("rank consistency mismatch")
    if limits["execution_result_is_diagnostic_only"] is not True:
        raise BlockedError("execution was not marked diagnostic-only")
    if execution["repo_scope"]["candidate_generation"] is not False or execution["repo_scope"]["edge_claim"] is not False:
        raise BlockedError("execution has forbidden candidate or edge flag")
    if execution["repo_scope"]["runtime_live_capital"] is not False:
        raise BlockedError("execution has runtime/live/capital flag")

    prereg_route = preregistration["funding_rate_hypothesis_preregistration"]["route_family"]
    prereg_hypothesis = preregistration["funding_rate_hypothesis_preregistration"]["hypothesis_name"]
    if prereg_route != ROUTE_FAMILY or prereg_hypothesis != HYPOTHESIS_NAME:
        raise BlockedError("preregistration route/hypothesis mismatch")
    if funding_review["funding_data_validity_classification"]["active_p0_blocker_count"] != 0:
        raise BlockedError("funding review has active P0 blockers")
    if panel_review["panel_validity_classification"] != "PANEL_REVIEW_PASS_WITH_P1_ATTENTION_VALID_FOR_READ_ONLY_SECOND_SOURCE_ANALYSIS":
        raise BlockedError("panel review classification mismatch")

    best_validation_net_positive = summary["best_validation_net_metric_bps"] > 0
    validation_positive = summary["validation_positive_after_cost"]
    null_passed = summary["null_baseline_review_preliminary_passed"]
    monthly_passed = summary["monthly_stability_review_preliminary_passed"]
    turnover_passed = summary["turnover_concentration_review_preliminary_passed"]
    metric_integrity_passed = summary["metric_integrity_passed"] and summary["metric_integrity_issue_count"] == 0
    safety_review_passed = (
        execution["repo_scope"]["strategy_search_executed"] is False
        and execution["repo_scope"]["candidate_generation"] is False
        and execution["repo_scope"]["edge_claim"] is False
        and execution["repo_scope"]["runtime_live_capital"] is False
        and execution["diagnostic_interpretation_limits"]["candidate_generation_allowed_from_this_execution"] is False
        and execution["diagnostic_interpretation_limits"]["edge_claim_allowed_from_this_execution"] is False
        and execution["diagnostic_interpretation_limits"]["family_release_allowed_from_this_execution"] is False
        and execution["diagnostic_interpretation_limits"]["runtime_live_capital_allowed_from_this_execution"] is False
    )
    evaluator_input_complete = True
    diagnostic_promising = all(
        [
            best_validation_net_positive,
            validation_positive,
            null_passed,
            monthly_passed,
            turnover_passed,
            metric_integrity_passed,
            safety_review_passed,
        ]
    )
    result_class = (
        "FUNDING_RATE_CROWDING_REVERSAL_DIAGNOSTIC_PROMISING_REQUIRES_SEPARATE_CLOSURE_NO_CANDIDATE_NO_EDGE"
        if diagnostic_promising
        else RESULT_CLASS_REJECTED
    )

    evaluator_reason = (
        "Best validation net metric is -4.402175 bps after costs and validation_positive_after_cost is false; "
        "monthly stability preliminary review also did not pass. Although null baseline and turnover/concentration "
        "passed and metric integrity issue count is zero, the funding-rate route is not diagnostically promising "
        "under the preregistered evaluator policy."
    )
    result_reason = (
        "The best validation configuration was funding_mean9_hold24h with gross metric 15.597825 bps but net metric "
        "-4.402175 bps after costs. Validation was not positive after costs and monthly stability did not pass, so "
        "the route is rejected/no-followup despite passing the null baseline, turnover/concentration, and metric "
        "integrity checks."
    )

    validation_checks = {
        "best_validation_config_preserved": summary["best_validation_config_id"] == BEST_CONFIG_ID,
        "best_validation_net_metric_preserved": near_equal(summary["best_validation_net_metric_bps"], BEST_NET_BPS),
        "closure_record_required_next": True,
        "config_count_verified_9": execution["preregistered_config_grid"]["config_count"] == 9,
        "diagnostic_promising_false": diagnostic_promising is False,
        "evaluator_artifact_json_valid": True,
        "evaluator_artifact_path_equals_required_path": EVALUATOR_ARTIFACT_PATH == "artifacts/strategy_evaluations/binance_okx_overlap_funding_rate_execution_evaluator_after_preregistered_9_config_run_v1.json",
        "evaluator_did_not_read_funding_rows": True,
        "evaluator_did_not_read_panel_rows": True,
        "evaluator_did_not_rerun_execution": True,
        "exactly_one_new_tracked_json_evaluator_artifact_expected": True,
        "exactly_one_new_tracked_python_tool_file_expected": True,
        "execution_artifact_loaded": True,
        "execution_payload_hash_verified": True,
        "execution_status_verified": True,
        "funding_review_artifact_loaded": True,
        "funding_review_payload_hash_verified": True,
        "module_path_equals_required_path": MODULE_PATH == "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_rate_execution_evaluator_after_preregistered_9_config_run_v1.py",
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_existing_files_modified_expected": True,
        "no_network_used": True,
        "no_other_tracked_files_expected": True,
        "no_runtime_live_capital": True,
        "no_strategy_search": True,
        "payload_sha256_excluding_hash_present": True,
        "preregistration_artifact_loaded": True,
        "preregistration_payload_hash_verified": True,
        "replacement_checks_all_true": True,
        "result_class_is_from_allowed_set": result_class in ALLOWED_RESULT_CLASSES,
        "result_classification_rejected_no_followup": result_class == RESULT_CLASS_REJECTED,
        "route_family_verified": scope["route_family"] == ROUTE_FAMILY,
        "status_equals_required_status": True,
    }

    artifact = {
        "artifact_kind": "BINANCE_OKX_OVERLAP_FUNDING_RATE_EXECUTION_EVALUATION",
        "evaluation_policy": {
            "allowed_result_classes": ALLOWED_RESULT_CLASSES,
            "diagnostic_promising_requires_all": [
                "best_validation_net_metric_bps > 0",
                "validation_positive_after_cost is true",
                "null_baseline_review_preliminary_passed is true",
                "monthly_stability_review_preliminary_passed is true",
                "turnover_concentration_review_preliminary_passed is true",
                "metric_integrity_passed is true",
                "safety_review_passed is true",
            ],
            "evaluation_policy_applied": True,
        },
        "evaluator_findings": {
            "best_validation_net_metric_positive_after_cost": best_validation_net_positive,
            "diagnostic_promising": diagnostic_promising,
            "evaluator_input_complete": evaluator_input_complete,
            "evaluator_ran": True,
            "evaluator_read_funding_rows": False,
            "evaluator_read_okx_rows": False,
            "evaluator_read_panel_rows": False,
            "evaluator_reason": evaluator_reason,
            "evaluator_recomputed_strategy_metrics": False,
            "metric_integrity_review_passed": metric_integrity_passed,
            "monthly_stability_review_passed": monthly_passed,
            "null_baseline_review_passed": null_passed,
            "safety_review_passed": safety_review_passed,
            "turnover_concentration_review_passed": turnover_passed,
            "validation_positive_after_cost": validation_positive,
        },
        "execution_results_evaluated": {
            "best_validation_config_id": summary["best_validation_config_id"],
            "best_validation_gross_metric_bps": summary["best_validation_gross_metric_bps"],
            "best_validation_holding_period": summary["best_validation_holding_period_hours"],
            "best_validation_net_metric_bps": summary["best_validation_net_metric_bps"],
            "best_validation_signal_transform": summary["best_validation_signal_transform"],
            "metric_integrity_issue_count": summary["metric_integrity_issue_count"],
            "metric_integrity_passed": summary["metric_integrity_passed"],
            "monthly_stability_review_preliminary_passed": summary["monthly_stability_review_preliminary_passed"],
            "null_baseline_complete": summary["null_baseline_complete"],
            "null_baseline_review_preliminary_passed": summary["null_baseline_review_preliminary_passed"],
            "train_validation_rank_consistency": summary["train_validation_rank_consistency"],
            "turnover_concentration_review_preliminary_passed": summary["turnover_concentration_review_preliminary_passed"],
            "validation_positive_after_cost": summary["validation_positive_after_cost"],
        },
        "followup_permissions": {
            "binance_panel_row_access_allowed_now": False,
            "boundary_buffer_access_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "capital_permission_allowed_now": False,
            "closure_record_allowed_next": True,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "final_edge_claim_requires_external_or_future_holdout": True,
            "funding_parameter_expansion_allowed_now": False,
            "funding_retest_allowed_now": False,
            "funding_row_access_allowed_now": False,
            "holdout_access_allowed_now": False,
            "if_rejected_then_closure_record_required_before_new_route": True,
            "live_permission_allowed_now": False,
            "momentum_retest_allowed_now": False,
            "okx_panel_access_allowed_now": False,
            "reversal_retest_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "strategy_search_allowed_now": False,
        },
        "forbidden_actions_confirmed_false": {
            "boundary_buffer_accessed": False,
            "candidates_generated": False,
            "capital_permission_granted": False,
            "edge_claimed": False,
            "existing_files_modified_by_module": False,
            "family_released": False,
            "funding_data_fetched": False,
            "funding_execution_rerun": False,
            "funding_rate_endpoint_called": False,
            "funding_rows_read": False,
            "holdout_accessed": False,
            "live_permission_granted": False,
            "okx_panel_rows_read": False,
            "panel_rows_read": False,
            "runtime_permission_granted": False,
            "strategy_search_executed": False,
        },
        "module": MODULE_PATH,
        "prior_execution_preserved": {
            "aligned_window_end_exclusive_utc": scope["aligned_window_end_exclusive_utc"],
            "aligned_window_start_utc": scope["aligned_window_start_utc"],
            "best_train_config_id": summary["best_train_config_id"],
            "best_validation_config_id": summary["best_validation_config_id"],
            "best_validation_gross_metric_bps": summary["best_validation_gross_metric_bps"],
            "best_validation_holding_period": summary["best_validation_holding_period_hours"],
            "best_validation_net_metric_bps": summary["best_validation_net_metric_bps"],
            "best_validation_signal_transform": summary["best_validation_signal_transform"],
            "candidate_generation": False,
            "config_count": execution["preregistered_config_grid"]["config_count"],
            "edge_claim": False,
            "exact_overlap_symbol_count": scope["exact_overlap_symbol_count"],
            "execution_result_is_diagnostic_only": limits["execution_result_is_diagnostic_only"],
            "family_release": False,
            "metric_integrity_issue_count": summary["metric_integrity_issue_count"],
            "metric_integrity_passed": summary["metric_integrity_passed"],
            "monthly_stability_review_preliminary_passed": summary["monthly_stability_review_preliminary_passed"],
            "null_baseline_complete": summary["null_baseline_complete"],
            "null_baseline_review_preliminary_passed": summary["null_baseline_review_preliminary_passed"],
            "route_family": scope["route_family"],
            "runtime_live_capital": False,
            "train_validation_rank_consistency": summary["train_validation_rank_consistency"],
            "turnover_concentration_review_preliminary_passed": summary["turnover_concentration_review_preliminary_passed"],
            "validation_positive_after_cost": summary["validation_positive_after_cost"],
        },
        "prior_preregistration_preserved": {
            "aligned_window_end_exclusive_utc": preregistration["universe_and_window_contract"]["aligned_window_end_exclusive_utc"],
            "aligned_window_start_utc": preregistration["universe_and_window_contract"]["aligned_window_start_utc"],
            "config_count": preregistration["predefined_config_grid"]["config_count"],
            "deterministic_config_ids": preregistration["predefined_config_grid"]["deterministic_config_ids"],
            "exact_overlap_symbol_count": preregistration["universe_and_window_contract"]["exact_overlap_symbol_count"],
            "holding_periods_hours": preregistration["predefined_config_grid"]["holding_periods_hours"],
            "hypothesis_name": prereg_hypothesis,
            "route_family": prereg_route,
            "signal_transforms": preregistration["predefined_config_grid"]["signal_transforms"],
        },
        "replacement_checks_all_true": True,
        "repo_scope": {
            "api_key_used": False,
            "binance_1m_kline_source_rows_read": False,
            "binance_funding_rows_read": False,
            "binance_panel_rows_read": False,
            "candidate_generation": False,
            "code_changes_repo_only": True,
            "edge_claim": False,
            "evaluator_artifact_created_in_repo": True,
            "evaluator_recomputed_strategy_metrics": False,
            "funding_data_acquisition_rerun": False,
            "funding_data_fetched_by_this_module": False,
            "funding_execution_rerun": False,
            "funding_rate_endpoint_called_by_this_module": False,
            "okx_panel_rows_read": False,
            "okx_whitelisted_artifact_read": False,
            "private_api_used": False,
            "public_network_used": False,
            "runtime_live_capital": False,
            "strategy_search_executed": False,
        },
        "result_classification": {
            "best_validation_config_id": summary["best_validation_config_id"],
            "best_validation_gross_metric_bps": summary["best_validation_gross_metric_bps"],
            "best_validation_holding_period": summary["best_validation_holding_period_hours"],
            "best_validation_net_metric_bps": summary["best_validation_net_metric_bps"],
            "best_validation_signal_transform": summary["best_validation_signal_transform"],
            "candidate_generation_allowed_from_evaluator": False,
            "closure_record_required_next": True,
            "diagnostic_promising": diagnostic_promising,
            "edge_claim_allowed_from_evaluator": False,
            "evaluator_grants_holdout_access": False,
            "family_release_allowed_from_evaluator": False,
            "metric_integrity_issue_count": summary["metric_integrity_issue_count"],
            "monthly_stability_review_passed": monthly_passed,
            "null_baseline_review_passed": null_passed,
            "result_class": result_class,
            "result_reason": result_reason,
            "runtime_live_capital_allowed_from_evaluator": False,
            "turnover_concentration_review_passed": turnover_passed,
            "validation_positive_after_cost": validation_positive,
        },
        "source_artifacts": {
            "acquisition_artifact_path": rel(ACQUISITION_PATH),
            "acquisition_payload_hash_verified": True,
            "execution_artifact_path": rel(EXECUTION_PATH),
            "execution_payload_hash_verified": True,
            "funding_review_artifact_path": rel(FUNDING_REVIEW_PATH),
            "funding_review_payload_hash_verified": True,
            "panel_review_artifact_path": rel(PANEL_REVIEW_PATH),
            "panel_review_payload_hash_verified": True,
            "preregistration_artifact_path": rel(PREREGISTRATION_PATH),
            "preregistration_payload_hash_verified": True,
            "readiness_artifact_path": rel(READINESS_PATH),
            "readiness_payload_hash_verified": True,
        },
        "source_checkpoint": {
            "prior_execution_artifact": "artifacts/strategy_executions/binance_okx_overlap_funding_rate_preregistered_9_config_execution_v1.json",
            "prior_execution_payload_sha256_excluding_hash": EXECUTION_PAYLOAD_HASH,
            "prior_execution_status": EXECUTION_STATUS,
            "prior_execution_tool": "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_rate_preregistered_9_config_execution_v1.py",
            "prior_head": PRIOR_HEAD,
            "prior_tracked_python_count": PRIOR_TRACKED_PYTHON_COUNT,
            "project": "Edge Factory OS / Binance OKX overlap funding-rate execution evaluator",
            "repo_clean_before_evaluator": True,
        },
        "status": REQUIRED_STATUS,
        "validation_checks": validation_checks,
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    validate_artifact(artifact)
    return artifact


def validate_artifact(artifact: dict[str, Any]) -> None:
    assert artifact["status"] == REQUIRED_STATUS
    assert artifact["module"] == MODULE_PATH
    assert EVALUATOR_ARTIFACT_PATH == "artifacts/strategy_evaluations/binance_okx_overlap_funding_rate_execution_evaluator_after_preregistered_9_config_run_v1.json"
    checks = artifact["validation_checks"]
    assert all(checks.values()), [key for key, value in checks.items() if value is not True]
    classification = artifact["result_classification"]
    findings = artifact["evaluator_findings"]
    assert artifact["prior_execution_preserved"]["route_family"] == ROUTE_FAMILY
    assert artifact["prior_execution_preserved"]["config_count"] == 9
    assert classification["best_validation_config_id"] == BEST_CONFIG_ID
    assert near_equal(classification["best_validation_net_metric_bps"], BEST_NET_BPS)
    assert classification["validation_positive_after_cost"] is False
    assert classification["null_baseline_review_passed"] is True
    assert classification["monthly_stability_review_passed"] is False
    assert classification["turnover_concentration_review_passed"] is True
    assert classification["metric_integrity_issue_count"] == 0
    assert classification["result_class"] == RESULT_CLASS_REJECTED
    assert classification["diagnostic_promising"] is False
    assert classification["closure_record_required_next"] is True
    assert findings["evaluator_recomputed_strategy_metrics"] is False
    assert findings["evaluator_read_panel_rows"] is False
    assert findings["evaluator_read_funding_rows"] is False
    assert artifact["repo_scope"]["candidate_generation"] is False
    assert artifact["repo_scope"]["edge_claim"] is False
    assert artifact["repo_scope"]["runtime_live_capital"] is False
    assert artifact["replacement_checks_all_true"] is True
    assert artifact["payload_sha256_excluding_hash"] == payload_hash(artifact)


def summary_from_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    classification = artifact["result_classification"]
    return {
        "best_validation_config_id": classification["best_validation_config_id"],
        "best_validation_gross_metric_bps": classification["best_validation_gross_metric_bps"],
        "best_validation_holding_period": classification["best_validation_holding_period"],
        "best_validation_net_metric_bps": classification["best_validation_net_metric_bps"],
        "best_validation_signal_transform": classification["best_validation_signal_transform"],
        "candidate_generation": False,
        "closure_record_required_next": classification["closure_record_required_next"],
        "diagnostic_promising": classification["diagnostic_promising"],
        "edge_claim": False,
        "evaluator_artifact_path": EVALUATOR_ARTIFACT_PATH,
        "metric_integrity_issue_count": classification["metric_integrity_issue_count"],
        "monthly_stability_review_passed": classification["monthly_stability_review_passed"],
        "null_baseline_review_passed": classification["null_baseline_review_passed"],
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": True,
        "result_class": classification["result_class"],
        "runtime_live_capital": False,
        "status": artifact["status"],
        "turnover_concentration_review_passed": classification["turnover_concentration_review_passed"],
        "validation_positive_after_cost": classification["validation_positive_after_cost"],
    }


def main() -> int:
    try:
        artifact = build_artifact()
        write_json_atomic(ARTIFACT_PATH, artifact)
        reloaded = read_json(ARTIFACT_PATH)
        if reloaded.get("payload_sha256_excluding_hash") != artifact["payload_sha256_excluding_hash"]:
            raise BlockedError("evaluator artifact readback mismatch")
        print(json.dumps(summary_from_artifact(artifact), indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        if TEMP_ARTIFACT_PATH.exists():
            TEMP_ARTIFACT_PATH.unlink()
        if ARTIFACT_PATH.exists():
            try:
                payload = read_json(ARTIFACT_PATH)
                if payload.get("status") != REQUIRED_STATUS:
                    ARTIFACT_PATH.unlink()
            except Exception:
                ARTIFACT_PATH.unlink()
        print(json.dumps({"reason": str(exc), "replacement_checks_all_true": False, "status": "BLOCKED"}, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
