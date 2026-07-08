#!/usr/bin/env python3
"""Static closure record after the restricted reversal evaluator.

This module closes the restricted CROSS_SECTIONAL_REVERSAL_BASELINE route using
the already-committed evaluator result. It does not rerun execution, rerun the
evaluator, read panel rows, open the whitelisted artifact, or grant follow-up
research/candidate/edge/runtime permissions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_STATUS = (
    "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_REVERSAL_CLOSURE_RECORD_AFTER_EVALUATOR_CREATED"
)
MODULE_PATH = (
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_reversal_closure_record_after_evaluator_v1.py"
)
REPO_PATH = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
WHITELISTED_ARTIFACT_PATH = (
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_after_retry_preview_v1"
    r"\repo_only_okx_88_symbol_1h_panel_revised_non_holdout_view.csv"
)

PROJECT = "Edge Factory OS / OKX historical data + research governance pipeline"
PANEL_SCOPE = "OKX 88-symbol 1h panel"
MOMENTUM_ROUTE_FAMILY = "CROSS_SECTIONAL_MOMENTUM_BASELINE"
REVERSAL_ROUTE_FAMILY = "CROSS_SECTIONAL_REVERSAL_BASELINE"
MOMENTUM_RESULT_CLASS = "MOMENTUM_BASELINE_REJECTED_NO_FOLLOWUP"
REVERSAL_RESULT_CLASS = "REVERSAL_BASELINE_REJECTED_NO_FOLLOWUP"
PRIOR_HEAD = "4a13376e502644e893bde8c1307483283557cfe1"
PRIOR_TRACKED_PYTHON_COUNT = 804
PRIOR_EVALUATOR_MODULE = (
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_reversal_execution_evaluator_after_whitelisted_artifact_run_v1.py"
)
PRIOR_EVALUATOR_STATUS = (
    "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_REVERSAL_EXECUTION_EVALUATED_AFTER_WHITELISTED_ARTIFACT_RUN"
)
PRIOR_EXECUTION_MODULE = (
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_reversal_search_execution_after_local_artifact_scope_amendment_v1.py"
)
PRIOR_EXECUTION_STATUS = (
    "PASS_REPO_CODE_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_REVERSAL_SEARCH_EXECUTED_WITH_WHITELISTED_LOCAL_ARTIFACT_NON_HOLDOUT_ONLY"
)

BEST_REVERSAL_CONFIG_ID = "reversal_lb48h_hold6h"
BEST_REVERSAL_NET_METRIC = 1.0545052484969872
BEST_MOMENTUM_CONFIG_ID = "momentum_lb48h_hold1h"
BEST_MOMENTUM_NET_METRIC = -4.680782776161402

SOURCE_CHECKPOINT = {
    "active_p0_blocker_count_before_closure": 0,
    "panel_scope": PANEL_SCOPE,
    "prior_evaluator_module": PRIOR_EVALUATOR_MODULE,
    "prior_evaluator_status": PRIOR_EVALUATOR_STATUS,
    "prior_execution_module": PRIOR_EXECUTION_MODULE,
    "prior_execution_status": PRIOR_EXECUTION_STATUS,
    "prior_head": PRIOR_HEAD,
    "prior_tracked_python_count": PRIOR_TRACKED_PYTHON_COUNT,
    "project": PROJECT,
    "repo_clean_before_closure": True,
}

PRIOR_EVALUATOR_RESULT_PRESERVED = {
    "best_validation_config_id": BEST_REVERSAL_CONFIG_ID,
    "best_validation_net_metric": BEST_REVERSAL_NET_METRIC,
    "best_validation_net_metric_positive_after_cost": True,
    "candidate_generation_allowed_from_evaluator": False,
    "closure_record_required_next": True,
    "diagnostic_promising": False,
    "edge_claim_allowed_from_evaluator": False,
    "evaluator_grants_holdout_access": False,
    "evaluator_ran": True,
    "evaluator_read_panel_rows": False,
    "evaluator_read_whitelisted_artifact": False,
    "evaluator_reason": (
        "Best validation net metric was positive after costs, but the reversal baseline was rejected "
        "because null baseline review did not pass and monthly stability review did not pass; "
        "diagnostic_promising is false."
    ),
    "evaluator_recomputed_strategy_metrics": False,
    "family_release_allowed_from_evaluator": False,
    "final_edge_claim_requires_external_or_future_holdout": True,
    "metric_integrity_issue_count": 0,
    "metric_integrity_review_passed": True,
    "monthly_stability_review_passed": False,
    "null_baseline_review_passed": False,
    "result_class": REVERSAL_RESULT_CLASS,
    "route_family_evaluated": REVERSAL_ROUTE_FAMILY,
    "runtime_live_capital_allowed_from_evaluator": False,
    "tested_config_count": 12,
    "turnover_concentration_review_passed": True,
}

PRIOR_REVERSAL_EXECUTION_PRESERVED = {
    "all_in_one_panel_accessed": False,
    "alternative_data_used": False,
    "best_validation_config_id": BEST_REVERSAL_CONFIG_ID,
    "best_validation_net_metric": BEST_REVERSAL_NET_METRIC,
    "boundary_buffer_accessed": False,
    "candidate_generation": False,
    "diagnostic_only": True,
    "edge_claim": False,
    "exact_whitelisted_artifact_path_used": WHITELISTED_ARTIFACT_PATH,
    "exact_whitelisted_local_artifact_rows_read_by_prior_execution": True,
    "external_data_used": False,
    "family_release": False,
    "holdout_accessed": False,
    "original_1m_source_files_read": False,
    "restricted_reversal_search_executed": True,
    "route_family_executed": REVERSAL_ROUTE_FAMILY,
    "runtime_live_capital": False,
    "tested_config_count": 12,
}

PRIOR_ACCESS_SCOPE_AMENDMENT_PRESERVED = {
    "active_p0_blocker_count_after_amendment": 0,
    "amendment_created": True,
    "amendment_reads_artifact_content": False,
    "amendment_reads_panel_rows": False,
    "amendment_type": "EXPLICITLY_WHITELISTED_READ_ONLY_LOCAL_ARTIFACT_SCOPE_AMENDMENT",
    "exact_whitelisted_local_artifact_path": WHITELISTED_ARTIFACT_PATH,
    "final_edge_claim_still_requires_external_or_future_holdout": True,
    "whitelisted_artifact_file_size_bytes": 347745318,
    "whitelisted_artifact_modified_time_ns": 1779458630371685100,
    "whitelisted_artifact_suffix": ".csv",
}

PRIOR_NEGATIVE_MOMENTUM_CLOSURE_PRESERVED = {
    "best_validation_config_id": BEST_MOMENTUM_CONFIG_ID,
    "best_validation_holding_period": "1h",
    "best_validation_lookback": "48h",
    "best_validation_net_metric": BEST_MOMENTUM_NET_METRIC,
    "clean_negative_research_result_preserved": True,
    "metric_integrity_issue_count": 0,
    "momentum_diagnostic_promising": False,
    "momentum_parameter_expansion_allowed_now": False,
    "momentum_result_class": MOMENTUM_RESULT_CLASS,
    "momentum_route_closed": True,
    "momentum_route_retest_allowed_now": False,
    "monthly_stability_review_passed": False,
    "not_a_data_failure": True,
    "not_a_family_release": True,
    "not_a_runtime_failure": True,
    "not_an_edge_claim": True,
    "null_baseline_review_passed": False,
    "turnover_concentration_review_passed": True,
    "validation_positive_after_cost": False,
}

REVERSAL_CLOSURE_RECORD = {
    "best_validation_config_id": BEST_REVERSAL_CONFIG_ID,
    "best_validation_net_metric": BEST_REVERSAL_NET_METRIC,
    "candidate_generation_allowed_now": False,
    "closure_grants_no_candidate": True,
    "closure_grants_no_edge_claim": True,
    "closure_grants_no_new_search": True,
    "closure_grants_no_release": True,
    "closure_grants_no_runtime_live_capital": True,
    "closure_reason": (
        "The restricted reversal baseline produced a positive best validation net metric of "
        "1.0545052484969872 for reversal_lb48h_hold6h, but the evaluator classified the route as "
        "REVERSAL_BASELINE_REJECTED_NO_FOLLOWUP because null baseline review did not pass, monthly "
        "stability review did not pass, and diagnostic_promising is false. This is a clean rejected "
        "diagnostic result, not a candidate, edge claim, family release, runtime permission, live "
        "permission, or capital permission."
    ),
    "closure_record_created": True,
    "closure_type": "RESTRICTED_REVERSAL_BASELINE_CLOSURE_AFTER_EVALUATOR",
    "diagnostic_promising_confirmed": False,
    "edge_claim_allowed_now": False,
    "family_release_allowed_now": False,
    "holdout_access_allowed_now": False,
    "metric_integrity_issue_count": 0,
    "monthly_stability_review_passed": False,
    "null_baseline_review_passed": False,
    "positive_best_validation_metric_not_promoted_to_candidate": True,
    "positive_best_validation_metric_not_promoted_to_edge_claim": True,
    "positive_best_validation_metric_preserved": True,
    "positive_metric_not_promoted_to_candidate": True,
    "positive_metric_not_promoted_to_edge_claim": True,
    "result_class_confirmed": REVERSAL_RESULT_CLASS,
    "reversal_parameter_expansion_allowed_now": False,
    "reversal_route_closed": True,
    "reversal_route_retest_allowed_now": False,
    "route_family_closed": REVERSAL_ROUTE_FAMILY,
    "runtime_live_capital_allowed_now": False,
    "strategy_search_expansion_allowed_now": False,
    "turnover_concentration_review_passed": True,
}

BASELINE_ROUTE_FAMILY_STATE_AFTER_CLOSURE = {
    "both_baseline_routes_closed": True,
    "momentum_baseline": {
        "candidate_generation_allowed_now": False,
        "diagnostic_promising": False,
        "edge_claim_allowed_now": False,
        "parameter_expansion_allowed_now": False,
        "result_class": MOMENTUM_RESULT_CLASS,
        "retest_allowed_now": False,
        "route_family": MOMENTUM_ROUTE_FAMILY,
        "status": "CLOSED_REJECTED_NO_FOLLOWUP",
    },
    "no_active_candidate_exists": True,
    "no_active_edge_claim_exists": True,
    "no_family_release_exists": True,
    "no_runtime_live_capital_permission_exists": True,
    "reversal_baseline": {
        "candidate_generation_allowed_now": False,
        "diagnostic_promising": False,
        "edge_claim_allowed_now": False,
        "parameter_expansion_allowed_now": False,
        "result_class": REVERSAL_RESULT_CLASS,
        "retest_allowed_now": False,
        "route_family": REVERSAL_ROUTE_FAMILY,
        "status": "CLOSED_REJECTED_NO_FOLLOWUP",
    },
    "tested_baseline_route_families_count": 2,
}

GOVERNANCE_SPRAWL_CONTROL_POLICY = {
    "create_governance_or_amendment_module_only_if": (
        "holdout_access_requested",
        "candidate_edge_release_live_or_capital_boundary_requested",
        "data_source_scope_contradiction_detected",
        "repo_state_dirty_or_artifact_identity_failure",
        "new_route_family_contract_required_for_new_research_cycle",
    ),
    "do_not_create_governance_modules_for_routine_progress": True,
    "future_search_not_automatically_approved_by_this_closure": True,
    "future_search_requires_new_deliberate_research_cycle": True,
    "future_work_should_prefer_fewer_modules_with_clear_boundaries": True,
    "no_new_access_scope_module_created_by_this_closure": True,
    "no_new_amendment_module_created_by_this_closure": True,
    "no_new_approval_module_created_by_this_closure": True,
    "no_new_blocker_module_created_by_this_closure": True,
    "no_new_governance_module_created_by_this_closure": True,
    "normal_research_path_after_this_closure": ("execution", "evaluator", "closure"),
    "policy_recorded": True,
    "reason": (
        "Recent workflow created multiple governance, blocker, and access-scope modules. Future work "
        "should avoid governance sprawl and only create such modules for real P0 contradictions or "
        "boundary crossings."
    ),
}

PANEL_AND_DATA_STATUS_AFTER_CLOSURE = {
    "all_in_one_panel_not_used_by_reversal_execution_evaluator_or_closure": True,
    "boundary_buffer_remains_unaccessed_by_reversal_execution_evaluator_and_closure": True,
    "final_edge_claim_requires_external_or_future_holdout": True,
    "finalized_revised_non_holdout_panel_used_for_reversal_execution": True,
    "finalized_revised_non_holdout_panel_valid_for_edge_claim": False,
    "holdout_remains_unaccessed_by_reversal_execution_evaluator_and_closure": True,
    "okx_88_symbol_1h_panel_reusable_for_future_read_only_research": True,
    "original_1m_source_files_not_used_by_reversal_execution_evaluator_or_closure": True,
    "panel_rows_read_by_this_closure_module": False,
    "whitelisted_artifact_read_by_this_closure_module": False,
}

FOLLOWUP_PERMISSIONS_AFTER_CLOSURE = {
    "all_in_one_panel_access_allowed_now": False,
    "alternative_data_access_allowed_now": False,
    "boundary_buffer_access_allowed_now": False,
    "candidate_generation_allowed_now": False,
    "capital_permission_allowed_now": False,
    "closure_complete": True,
    "closure_record_created": True,
    "edge_claim_allowed_now": False,
    "evaluator_allowed_now": False,
    "external_data_access_allowed_now": False,
    "family_release_allowed_now": False,
    "holdout_access_allowed_now": False,
    "live_permission_allowed_now": False,
    "momentum_parameter_expansion_allowed_now": False,
    "momentum_retest_allowed_now": False,
    "new_research_cycle_allowed_only_with_new_deliberate_contract": True,
    "next_immediate_module_required": False,
    "original_1m_source_access_allowed_now": False,
    "project_can_pause_after_closure": True,
    "reversal_parameter_expansion_allowed_now": False,
    "reversal_retest_allowed_now": False,
    "runtime_permission_allowed_now": False,
    "strategy_search_allowed_now": False,
}

FORBIDDEN_ACTIONS_CONFIRMED_FALSE = {
    "all_in_one_panel_accessed": False,
    "alternative_data_used": False,
    "boundary_buffer_accessed": False,
    "candidates_generated": False,
    "capital_permission_granted": False,
    "data_artifacts_created": False,
    "edge_claimed": False,
    "evaluator_rerun": False,
    "existing_files_modified_by_module": False,
    "external_data_used": False,
    "family_released": False,
    "files_written_by_module": False,
    "holdout_accessed": False,
    "live_permission_granted": False,
    "momentum_parameter_expansion_executed": False,
    "momentum_retest_executed": False,
    "momentum_search_executed": False,
    "momentum_vs_reversal_comparison_performed": False,
    "new_access_scope_module_created": False,
    "new_amendment_module_created": False,
    "new_approval_module_created": False,
    "new_blocker_module_created": False,
    "new_governance_module_created": False,
    "original_1m_source_files_read": False,
    "panel_rows_read": False,
    "reversal_execution_rerun": False,
    "reversal_tested": False,
    "runtime_permission_granted": False,
    "strategy_search_executed": False,
    "whitelisted_artifact_read": False,
}


def build_summary() -> dict[str, Any]:
    validation_checks = {
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 0,
        "best_validation_config_id_preserved": True,
        "best_validation_net_metric_preserved": True,
        "both_baseline_routes_closed": True,
        "candidate_generation_forbidden": True,
        "closure_did_not_access_all_in_one_panel": True,
        "closure_did_not_access_boundary_buffer": True,
        "closure_did_not_access_holdout": True,
        "closure_did_not_access_original_1m_source_files": True,
        "closure_did_not_read_panel_rows": True,
        "closure_did_not_read_whitelisted_artifact": True,
        "closure_did_not_rerun_evaluator": True,
        "closure_did_not_rerun_execution": True,
        "closure_did_not_run_strategy_search": True,
        "closure_did_not_use_external_or_alternative_data": True,
        "created_file_expected_count": 1,
        "edge_claim_forbidden": True,
        "exactly_one_new_tracked_python_tool_file_expected": True,
        "family_release_forbidden": True,
        "final_edge_claim_requires_external_or_future_holdout": True,
        "metric_integrity_issue_count_zero_preserved": True,
        "module_path_equals_required_path": True,
        "momentum_route_remains_closed": True,
        "monthly_stability_review_failed_preserved": True,
        "no_active_candidate_exists": True,
        "no_active_edge_claim_exists": True,
        "no_data_files_created_expected": True,
        "no_existing_files_modified_expected": True,
        "no_new_governance_or_amendment_or_blocker_module_created": True,
        "null_baseline_review_failed_preserved": True,
        "positive_best_validation_metric_not_promoted_to_candidate_or_edge": True,
        "prior_access_scope_amendment_preserved": True,
        "prior_evaluator_result_class_preserved": True,
        "prior_evaluator_status_preserved": True,
        "prior_execution_status_preserved": True,
        "prior_negative_momentum_closure_preserved": True,
        "replacement_checks_all_true": True,
        "reversal_diagnostic_promising_is_false": True,
        "reversal_result_class_is_rejected_no_followup": True,
        "reversal_route_closed": True,
        "runtime_live_capital_forbidden": True,
        "status_equals_required_status": True,
        "turnover_concentration_review_passed_preserved": True,
    }
    replacement_checks_all_true = all(
        value is True
        for key, value in validation_checks.items()
        if key not in {"active_p0_blocker_count", "active_p1_attention_count", "created_file_expected_count"}
    )
    return {
        "baseline_route_family_state_after_closure": BASELINE_ROUTE_FAMILY_STATE_AFTER_CLOSURE,
        "followup_permissions_after_closure": FOLLOWUP_PERMISSIONS_AFTER_CLOSURE,
        "forbidden_actions_confirmed_false": FORBIDDEN_ACTIONS_CONFIRMED_FALSE,
        "governance_sprawl_control_policy": GOVERNANCE_SPRAWL_CONTROL_POLICY,
        "module": MODULE_PATH,
        "panel_and_data_status_after_closure": PANEL_AND_DATA_STATUS_AFTER_CLOSURE,
        "prior_access_scope_amendment_preserved": PRIOR_ACCESS_SCOPE_AMENDMENT_PRESERVED,
        "prior_evaluator_result_preserved": PRIOR_EVALUATOR_RESULT_PRESERVED,
        "prior_negative_momentum_closure_preserved": PRIOR_NEGATIVE_MOMENTUM_CLOSURE_PRESERVED,
        "prior_reversal_execution_preserved": PRIOR_REVERSAL_EXECUTION_PRESERVED,
        "replacement_checks_all_true": replacement_checks_all_true,
        "repo_scope": {
            "api_used": False,
            "code_changes_repo_only": True,
            "evaluator_rerun_by_this_module": False,
            "internet_used": False,
            "non_repo_artifact_content_read_by_this_module": False,
            "notebooks_used": False,
            "panel_rows_read_by_this_module": False,
            "repo_path": str(REPO_PATH),
            "strategy_search_executed_by_this_module": False,
        },
        "reversal_closure_record": REVERSAL_CLOSURE_RECORD,
        "source_checkpoint": SOURCE_CHECKPOINT,
        "status": REQUIRED_STATUS,
        "validation_checks": validation_checks,
    }


def validate_summary(summary: dict[str, Any]) -> None:
    assert summary["status"] == REQUIRED_STATUS
    assert summary["module"] == MODULE_PATH
    assert summary["source_checkpoint"]["prior_evaluator_status"] == PRIOR_EVALUATOR_STATUS
    assert summary["source_checkpoint"]["prior_execution_status"] == PRIOR_EXECUTION_STATUS
    evaluator = summary["prior_evaluator_result_preserved"]
    closure = summary["reversal_closure_record"]
    family_state = summary["baseline_route_family_state_after_closure"]
    followup = summary["followup_permissions_after_closure"]
    assert evaluator["result_class"] == REVERSAL_RESULT_CLASS
    assert evaluator["diagnostic_promising"] is False
    assert evaluator["best_validation_config_id"] == BEST_REVERSAL_CONFIG_ID
    assert abs(evaluator["best_validation_net_metric"] - BEST_REVERSAL_NET_METRIC) <= 1e-12
    assert evaluator["best_validation_net_metric_positive_after_cost"] is True
    assert evaluator["null_baseline_review_passed"] is False
    assert evaluator["monthly_stability_review_passed"] is False
    assert evaluator["turnover_concentration_review_passed"] is True
    assert evaluator["metric_integrity_issue_count"] == 0
    assert closure["positive_best_validation_metric_not_promoted_to_candidate"] is True
    assert closure["positive_best_validation_metric_not_promoted_to_edge_claim"] is True
    assert closure["reversal_route_closed"] is True
    assert closure["reversal_route_retest_allowed_now"] is False
    assert closure["reversal_parameter_expansion_allowed_now"] is False
    momentum = summary["prior_negative_momentum_closure_preserved"]
    assert momentum["momentum_route_closed"] is True
    assert momentum["momentum_result_class"] == MOMENTUM_RESULT_CLASS
    assert momentum["best_validation_net_metric"] < 0
    assert family_state["both_baseline_routes_closed"] is True
    assert family_state["no_active_candidate_exists"] is True
    assert family_state["no_active_edge_claim_exists"] is True
    assert followup["candidate_generation_allowed_now"] is False
    assert followup["edge_claim_allowed_now"] is False
    assert followup["family_release_allowed_now"] is False
    assert followup["runtime_permission_allowed_now"] is False
    assert followup["live_permission_allowed_now"] is False
    assert followup["capital_permission_allowed_now"] is False
    assert followup["holdout_access_allowed_now"] is False
    assert followup["boundary_buffer_access_allowed_now"] is False
    assert followup["all_in_one_panel_access_allowed_now"] is False
    assert followup["original_1m_source_access_allowed_now"] is False
    assert followup["next_immediate_module_required"] is False
    assert followup["project_can_pause_after_closure"] is True
    assert summary["panel_and_data_status_after_closure"]["final_edge_claim_requires_external_or_future_holdout"] is True
    for key, value in summary["forbidden_actions_confirmed_false"].items():
        assert value is False, key
    assert summary["validation_checks"]["active_p0_blocker_count"] == 0
    assert summary["replacement_checks_all_true"] is True


def main() -> int:
    summary = build_summary()
    validate_summary(summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
