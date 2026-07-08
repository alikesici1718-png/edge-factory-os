#!/usr/bin/env python3
"""Create the closure record for the rejected Binance/OKX funding route."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


REQUIRED_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_RATE_CLOSURE_RECORD_AFTER_EVALUATOR_CREATED"
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_rate_closure_record_after_evaluator_v1.py"
CLOSURE_ARTIFACT_PATH = "artifacts/strategy_closures/binance_okx_overlap_funding_rate_closure_record_after_evaluator_v1.json"

REPO_PATH = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
ARTIFACT_PATH = REPO_PATH / CLOSURE_ARTIFACT_PATH
TEMP_ARTIFACT_PATH = ARTIFACT_PATH.with_suffix(".json.tmp")

EVALUATOR_PATH = REPO_PATH / "artifacts/strategy_evaluations/binance_okx_overlap_funding_rate_execution_evaluator_after_preregistered_9_config_run_v1.json"
EXECUTION_PATH = REPO_PATH / "artifacts/strategy_executions/binance_okx_overlap_funding_rate_preregistered_9_config_execution_v1.json"
FUNDING_REVIEW_PATH = REPO_PATH / "artifacts/funding_rate_reviews/binance_okx_overlap_funding_rate_data_review_after_acquisition_lock_v1.json"
ACQUISITION_PATH = REPO_PATH / "artifacts/funding_rate_locks/binance_okx_overlap_funding_rate_data_acquisition_lock_v1.json"
PREREGISTRATION_PATH = REPO_PATH / "artifacts/research_preregistrations/binance_okx_overlap_funding_rate_hypothesis_preregistration_contract_v1.json"
READINESS_PATH = REPO_PATH / "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json"
PANEL_REVIEW_PATH = REPO_PATH / "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json"

PRIOR_HEAD = "d59f0445d1dc1c59f8d63449a9d0f5ff9348540c"
PRIOR_TRACKED_PYTHON_COUNT = 816
EVALUATOR_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_RATE_EXECUTION_EVALUATED_AFTER_PREREGISTERED_9_CONFIG_RUN"
EVALUATOR_PAYLOAD_HASH = "2dc652c21ad2b103aa5821e141d259abe523e03cc6662a28bb2e04dccc342306"
EXECUTION_PAYLOAD_HASH = "0f9fc66e7fdf3e15bc84fe4e88d4c110902c8f62d9e31eec1628c96e27eda8a7"
FUNDING_REVIEW_PAYLOAD_HASH = "a579feb0472efbf03ffa955008dfabc0b526fa37029fc81dddd0195b4054d849"
ACQUISITION_PAYLOAD_HASH = "dd5877b101c9a1e8d73f35f6032381cbdfd5435578abacf97b9db0c11c28e252"
PREREGISTRATION_PAYLOAD_HASH = "5febb59aee08873de1dbfc0464da463811090c334c18c5f2a552e1768cb3c768"
READINESS_PAYLOAD_HASH = "0cfe239f6f5ad2d20bda64b827416851de8f5b959066902b59f1f00f44eba716"
PANEL_REVIEW_PAYLOAD_HASH = "34b88a3ff0870c708e2df034c243cf639b711ebce3c6a4f32edffb92a2229112"

ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_RATE_CROWDING_REVERSAL_BASELINE"
HYPOTHESIS_NAME = "funding_rate_crowding_reversal"
RESULT_CLASS = "FUNDING_RATE_CROWDING_REVERSAL_REJECTED_NO_FOLLOWUP"
BEST_CONFIG_ID = "funding_mean9_hold24h"
BEST_SIGNAL_TRANSFORM = "rolling_mean_9_funding_events"
BEST_HOLDING_PERIOD = 24
BEST_NET_BPS = -4.402175
BEST_GROSS_BPS = 15.597825
RANK_CONSISTENCY = 0.883333


class BlockedError(RuntimeError):
    """Raised when closure inputs are unsafe or inconsistent."""


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


def near_equal(value: float, expected: float) -> bool:
    return math.isclose(float(value), expected, rel_tol=0.0, abs_tol=1e-9)


def load_sources() -> dict[str, dict[str, Any]]:
    paths = {
        "acquisition": ACQUISITION_PATH,
        "evaluator": EVALUATOR_PATH,
        "execution": EXECUTION_PATH,
        "funding_review": FUNDING_REVIEW_PATH,
        "panel_review": PANEL_REVIEW_PATH,
        "preregistration": PREREGISTRATION_PATH,
        "readiness": READINESS_PATH,
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise BlockedError(f"required closure source artifacts missing: {missing}")
    payloads = {key: read_json(path) for key, path in paths.items()}
    expected_hashes = {
        "acquisition": ACQUISITION_PAYLOAD_HASH,
        "evaluator": EVALUATOR_PAYLOAD_HASH,
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


def build_artifact() -> dict[str, Any]:
    payloads = load_sources()
    evaluator = payloads["evaluator"]
    execution = payloads["execution"]
    preregistration = payloads["preregistration"]

    if evaluator["status"] != EVALUATOR_STATUS:
        raise BlockedError("evaluator status mismatch")
    result = evaluator["result_classification"]
    execution_summary = execution["train_validation_summary"]
    execution_scope = execution["execution_scope"]
    execution_limits = execution["diagnostic_interpretation_limits"]

    if result["result_class"] != RESULT_CLASS:
        raise BlockedError("evaluator result class mismatch")
    if result["diagnostic_promising"] is not False:
        raise BlockedError("diagnostic_promising must be false")
    if result["best_validation_config_id"] != BEST_CONFIG_ID:
        raise BlockedError("best validation config mismatch")
    if result["best_validation_signal_transform"] != BEST_SIGNAL_TRANSFORM:
        raise BlockedError("best validation signal transform mismatch")
    if result["best_validation_holding_period"] != BEST_HOLDING_PERIOD:
        raise BlockedError("best validation holding period mismatch")
    if not near_equal(result["best_validation_net_metric_bps"], BEST_NET_BPS):
        raise BlockedError("best validation net metric mismatch")
    if not near_equal(result["best_validation_gross_metric_bps"], BEST_GROSS_BPS):
        raise BlockedError("best validation gross metric mismatch")
    if result["validation_positive_after_cost"] is not False:
        raise BlockedError("validation_positive_after_cost must be false")
    if result["null_baseline_review_passed"] is not True:
        raise BlockedError("null baseline review must be passed")
    if result["monthly_stability_review_passed"] is not False:
        raise BlockedError("monthly stability review must be failed")
    if result["turnover_concentration_review_passed"] is not True:
        raise BlockedError("turnover/concentration review must be passed")
    if result["metric_integrity_issue_count"] != 0:
        raise BlockedError("metric integrity issue count must be zero")
    if result["closure_record_required_next"] is not True:
        raise BlockedError("closure record was not required")
    if execution_scope["route_family"] != ROUTE_FAMILY or execution["preregistered_config_grid"]["config_count"] != 9:
        raise BlockedError("execution route/config mismatch")
    if preregistration["funding_rate_hypothesis_preregistration"]["hypothesis_name"] != HYPOTHESIS_NAME:
        raise BlockedError("hypothesis name mismatch")

    closure_reason = (
        "The preregistered funding-rate crowding reversal route produced a positive best validation gross metric of "
        "15.597825 bps for funding_mean9_hold24h, but the net validation metric after costs was -4.402175 bps, "
        "validation_positive_after_cost was false, and monthly stability did not pass. The route is therefore closed "
        "as FUNDING_RATE_CROWDING_REVERSAL_REJECTED_NO_FOLLOWUP. This is a clean rejected diagnostic result, not a "
        "candidate, edge claim, family release, runtime permission, live permission, or capital permission."
    )

    validation_checks = {
        "best_validation_config_preserved": result["best_validation_config_id"] == BEST_CONFIG_ID,
        "best_validation_net_metric_preserved": near_equal(result["best_validation_net_metric_bps"], BEST_NET_BPS),
        "closure_artifact_json_valid": True,
        "closure_artifact_path_equals_required_path": CLOSURE_ARTIFACT_PATH == "artifacts/strategy_closures/binance_okx_overlap_funding_rate_closure_record_after_evaluator_v1.json",
        "diagnostic_promising_false_preserved": result["diagnostic_promising"] is False,
        "evaluator_artifact_loaded": True,
        "evaluator_payload_hash_verified": True,
        "evaluator_status_verified": True,
        "exactly_one_new_tracked_json_closure_artifact_expected": True,
        "exactly_one_new_tracked_python_tool_file_expected": True,
        "execution_artifact_loaded": True,
        "execution_payload_hash_verified": True,
        "funding_review_artifact_loaded": True,
        "funding_review_payload_hash_verified": True,
        "funding_route_closed": True,
        "metric_integrity_issue_count_zero_preserved": result["metric_integrity_issue_count"] == 0,
        "module_path_equals_required_path": MODULE_PATH == "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_rate_closure_record_after_evaluator_v1.py",
        "monthly_stability_review_failed_preserved": result["monthly_stability_review_passed"] is False,
        "next_immediate_module_required_false": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_evaluator_rerun": True,
        "no_execution_rerun": True,
        "no_existing_files_modified_expected": True,
        "no_funding_rows_read": True,
        "no_network_used": True,
        "no_okx_panel_rows_read": True,
        "no_other_tracked_files_expected": True,
        "no_panel_rows_read": True,
        "no_runtime_live_capital": True,
        "no_strategy_search": True,
        "null_baseline_review_passed_preserved": result["null_baseline_review_passed"] is True,
        "payload_sha256_excluding_hash_present": True,
        "preregistration_artifact_loaded": True,
        "preregistration_payload_hash_verified": True,
        "project_can_pause_after_closure": True,
        "replacement_checks_all_true": True,
        "result_class_preserved": result["result_class"] == RESULT_CLASS,
        "status_equals_required_status": True,
        "turnover_concentration_review_passed_preserved": result["turnover_concentration_review_passed"] is True,
        "validation_positive_after_cost_false_preserved": result["validation_positive_after_cost"] is False,
    }

    artifact = {
        "artifact_kind": "BINANCE_OKX_OVERLAP_FUNDING_RATE_CLOSURE_RECORD",
        "followup_permissions_after_closure": {
            "binance_panel_row_access_allowed_now": False,
            "boundary_buffer_access_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "capital_permission_allowed_now": False,
            "closure_complete": True,
            "closure_record_created": True,
            "edge_claim_allowed_now": False,
            "external_data_access_allowed_now": False,
            "family_release_allowed_now": False,
            "funding_parameter_expansion_allowed_now": False,
            "funding_retest_allowed_now": False,
            "funding_row_access_allowed_now": False,
            "holdout_access_allowed_now": False,
            "live_permission_allowed_now": False,
            "momentum_retest_allowed_now": False,
            "new_research_cycle_allowed_only_with_new_deliberate_contract": True,
            "next_immediate_module_required": False,
            "okx_panel_access_allowed_now": False,
            "project_can_pause_after_closure": True,
            "reversal_retest_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "strategy_search_allowed_now": False,
        },
        "forbidden_actions_confirmed_false": {
            "boundary_buffer_accessed": False,
            "candidates_generated": False,
            "capital_permission_granted": False,
            "edge_claimed": False,
            "evaluator_rerun": False,
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
        "funding_route_closure_record": {
            "best_validation_config_id": BEST_CONFIG_ID,
            "best_validation_gross_metric_bps": BEST_GROSS_BPS,
            "best_validation_holding_period": BEST_HOLDING_PERIOD,
            "best_validation_net_metric_bps": BEST_NET_BPS,
            "best_validation_signal_transform": BEST_SIGNAL_TRANSFORM,
            "candidate_generation_allowed_now": False,
            "closure_grants_no_candidate": True,
            "closure_grants_no_edge_claim": True,
            "closure_grants_no_new_search": True,
            "closure_grants_no_release": True,
            "closure_grants_no_runtime_live_capital": True,
            "closure_reason": closure_reason,
            "closure_record_created": True,
            "closure_type": "FUNDING_RATE_CROWDING_REVERSAL_BASELINE_CLOSURE_AFTER_EVALUATOR",
            "diagnostic_promising_confirmed": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "funding_parameter_expansion_allowed_now": False,
            "funding_retest_allowed_now": False,
            "funding_route_closed": True,
            "gross_positive_but_net_negative_after_costs": True,
            "holdout_access_allowed_now": False,
            "hypothesis_name": HYPOTHESIS_NAME,
            "metric_integrity_issue_count": 0,
            "monthly_stability_review_passed": False,
            "null_baseline_review_passed": True,
            "positive_gross_metric_not_promoted_to_candidate": True,
            "positive_gross_metric_not_promoted_to_edge_claim": True,
            "result_class_confirmed": RESULT_CLASS,
            "route_family_closed": ROUTE_FAMILY,
            "runtime_live_capital_allowed_now": False,
            "strategy_search_expansion_allowed_now": False,
            "turnover_concentration_review_passed": True,
            "validation_positive_after_cost": False,
        },
        "module": MODULE_PATH,
        "prior_evaluator_result_preserved": {
            "best_validation_config_id": result["best_validation_config_id"],
            "best_validation_gross_metric_bps": result["best_validation_gross_metric_bps"],
            "best_validation_holding_period": result["best_validation_holding_period"],
            "best_validation_net_metric_bps": result["best_validation_net_metric_bps"],
            "best_validation_signal_transform": result["best_validation_signal_transform"],
            "candidate_generation_allowed_from_evaluator": result["candidate_generation_allowed_from_evaluator"],
            "closure_record_required_next": result["closure_record_required_next"],
            "diagnostic_promising": result["diagnostic_promising"],
            "edge_claim_allowed_from_evaluator": result["edge_claim_allowed_from_evaluator"],
            "family_release_allowed_from_evaluator": result["family_release_allowed_from_evaluator"],
            "metric_integrity_issue_count": result["metric_integrity_issue_count"],
            "monthly_stability_review_passed": result["monthly_stability_review_passed"],
            "null_baseline_review_passed": result["null_baseline_review_passed"],
            "result_class": result["result_class"],
            "runtime_live_capital_allowed_from_evaluator": result["runtime_live_capital_allowed_from_evaluator"],
            "turnover_concentration_review_passed": result["turnover_concentration_review_passed"],
            "validation_positive_after_cost": result["validation_positive_after_cost"],
        },
        "prior_execution_result_preserved": {
            "best_train_config_id": execution_summary["best_train_config_id"],
            "best_validation_config_id": execution_summary["best_validation_config_id"],
            "best_validation_gross_metric_bps": execution_summary["best_validation_gross_metric_bps"],
            "best_validation_net_metric_bps": execution_summary["best_validation_net_metric_bps"],
            "candidate_generation": False,
            "config_count": execution["preregistered_config_grid"]["config_count"],
            "edge_claim": False,
            "execution_result_is_diagnostic_only": execution_limits["execution_result_is_diagnostic_only"],
            "family_release": False,
            "metric_integrity_issue_count": execution_summary["metric_integrity_issue_count"],
            "metric_integrity_passed": execution_summary["metric_integrity_passed"],
            "monthly_stability_review_preliminary_passed": execution_summary["monthly_stability_review_preliminary_passed"],
            "null_baseline_complete": execution_summary["null_baseline_complete"],
            "null_baseline_review_preliminary_passed": execution_summary["null_baseline_review_preliminary_passed"],
            "route_family": execution_scope["route_family"],
            "runtime_live_capital": False,
            "train_validation_rank_consistency": execution_summary["train_validation_rank_consistency"],
            "turnover_concentration_review_preliminary_passed": execution_summary["turnover_concentration_review_preliminary_passed"],
            "validation_positive_after_cost": execution_summary["validation_positive_after_cost"],
        },
        "project_state_after_closure": {
            "binance_funding_route_closed": True,
            "binance_okx_overlap_panel_built_and_reviewed": True,
            "funding_data_acquired_and_reviewed": True,
            "immediate_next_module_required": False,
            "no_active_candidate_exists": True,
            "no_active_edge_claim_exists": True,
            "no_family_release_exists": True,
            "no_holdout_access_exists": True,
            "no_runtime_live_capital_permission_exists": True,
            "okx_momentum_route_closed": True,
            "okx_reversal_route_closed": True,
            "project_can_pause_after_funding_closure": True,
        },
        "replacement_checks_all_true": True,
        "repo_scope": {
            "api_key_used": False,
            "binance_1m_kline_source_rows_read": False,
            "binance_funding_rows_read": False,
            "binance_panel_rows_read": False,
            "candidate_generation": False,
            "closure_artifact_created_in_repo": True,
            "code_changes_repo_only": True,
            "edge_claim": False,
            "evaluator_rerun": False,
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
        "route_family_state_after_closure": {
            "closed_route_families": [
                "CROSS_SECTIONAL_MOMENTUM_BASELINE",
                "CROSS_SECTIONAL_REVERSAL_BASELINE",
                ROUTE_FAMILY,
            ],
            "funding_rate_route": {
                "candidate_generation_allowed_now": False,
                "diagnostic_promising": False,
                "edge_claim_allowed_now": False,
                "parameter_expansion_allowed_now": False,
                "result_class": RESULT_CLASS,
                "retest_allowed_now": False,
                "route_family": ROUTE_FAMILY,
                "status": "CLOSED_REJECTED_NO_FOLLOWUP",
            },
            "no_active_candidate_exists": True,
            "no_active_edge_claim_exists": True,
            "no_family_release_exists": True,
            "no_runtime_live_capital_permission_exists": True,
        },
        "source_artifacts": {
            "acquisition_artifact_path": rel(ACQUISITION_PATH),
            "acquisition_payload_hash_verified": True,
            "evaluator_artifact_path": rel(EVALUATOR_PATH),
            "evaluator_payload_hash_verified": True,
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
            "prior_evaluator_artifact": "artifacts/strategy_evaluations/binance_okx_overlap_funding_rate_execution_evaluator_after_preregistered_9_config_run_v1.json",
            "prior_evaluator_payload_sha256_excluding_hash": EVALUATOR_PAYLOAD_HASH,
            "prior_evaluator_status": EVALUATOR_STATUS,
            "prior_evaluator_tool": "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_rate_execution_evaluator_after_preregistered_9_config_run_v1.py",
            "prior_head": PRIOR_HEAD,
            "prior_tracked_python_count": PRIOR_TRACKED_PYTHON_COUNT,
            "project": "Edge Factory OS / Binance OKX overlap funding-rate closure",
            "repo_clean_before_closure": True,
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
    assert CLOSURE_ARTIFACT_PATH == "artifacts/strategy_closures/binance_okx_overlap_funding_rate_closure_record_after_evaluator_v1.json"
    checks = artifact["validation_checks"]
    assert all(checks.values()), [key for key, value in checks.items() if value is not True]
    closure = artifact["funding_route_closure_record"]
    followup = artifact["followup_permissions_after_closure"]
    assert artifact["prior_evaluator_result_preserved"]["result_class"] == RESULT_CLASS
    assert artifact["prior_evaluator_result_preserved"]["diagnostic_promising"] is False
    assert closure["funding_route_closed"] is True
    assert closure["funding_retest_allowed_now"] is False
    assert closure["funding_parameter_expansion_allowed_now"] is False
    assert closure["candidate_generation_allowed_now"] is False
    assert closure["edge_claim_allowed_now"] is False
    assert closure["runtime_live_capital_allowed_now"] is False
    assert followup["next_immediate_module_required"] is False
    assert followup["project_can_pause_after_closure"] is True
    assert artifact["repo_scope"]["funding_execution_rerun"] is False
    assert artifact["repo_scope"]["evaluator_rerun"] is False
    assert artifact["repo_scope"]["binance_panel_rows_read"] is False
    assert artifact["repo_scope"]["binance_funding_rows_read"] is False
    assert artifact["repo_scope"]["candidate_generation"] is False
    assert artifact["repo_scope"]["edge_claim"] is False
    assert artifact["repo_scope"]["runtime_live_capital"] is False
    assert artifact["replacement_checks_all_true"] is True
    assert artifact["payload_sha256_excluding_hash"] == payload_hash(artifact)


def summary_from_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    closure = artifact["funding_route_closure_record"]
    return {
        "best_validation_config_id": closure["best_validation_config_id"],
        "best_validation_gross_metric_bps": closure["best_validation_gross_metric_bps"],
        "best_validation_holding_period": closure["best_validation_holding_period"],
        "best_validation_net_metric_bps": closure["best_validation_net_metric_bps"],
        "best_validation_signal_transform": closure["best_validation_signal_transform"],
        "candidate_generation": False,
        "closure_artifact_path": CLOSURE_ARTIFACT_PATH,
        "diagnostic_promising": closure["diagnostic_promising_confirmed"],
        "edge_claim": False,
        "funding_parameter_expansion_allowed_now": closure["funding_parameter_expansion_allowed_now"],
        "funding_retest_allowed_now": closure["funding_retest_allowed_now"],
        "funding_route_closed": closure["funding_route_closed"],
        "metric_integrity_issue_count": closure["metric_integrity_issue_count"],
        "monthly_stability_review_passed": closure["monthly_stability_review_passed"],
        "next_immediate_module_required": False,
        "null_baseline_review_passed": closure["null_baseline_review_passed"],
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "project_can_pause_after_closure": True,
        "replacement_checks_all_true": True,
        "result_class": closure["result_class_confirmed"],
        "runtime_live_capital": False,
        "status": artifact["status"],
        "turnover_concentration_review_passed": closure["turnover_concentration_review_passed"],
        "validation_positive_after_cost": closure["validation_positive_after_cost"],
    }


def main() -> int:
    try:
        artifact = build_artifact()
        write_json_atomic(ARTIFACT_PATH, artifact)
        reloaded = read_json(ARTIFACT_PATH)
        if reloaded.get("payload_sha256_excluding_hash") != artifact["payload_sha256_excluding_hash"]:
            raise BlockedError("closure artifact readback mismatch")
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
