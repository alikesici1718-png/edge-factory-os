from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_STATUS = (
    "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVERSAL_EXECUTION_PANEL_ACCESS_SCOPE_BLOCKER_REVIEW_CREATED"
)
MODULE_PATH = Path(
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_reversal_execution_panel_access_scope_blocker_review_v1.py"
).as_posix()
PRIOR_EXECUTION_APPROVAL_MODULE = (
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_reversal_execution_governance_approval_after_preregistration_contract_v1.py"
)
PRIOR_EXECUTION_APPROVAL_STATUS = (
    "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVERSAL_EXECUTION_GOVERNANCE_APPROVAL_AFTER_PREREGISTRATION_CONTRACT_CREATED"
)
PRIOR_PREREGISTRATION_CONTRACT_MODULE = (
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_new_route_family_preregistration_contract_proposal_after_governance_summary_v1.py"
)
PRIOR_PREREGISTRATION_CONTRACT_STATUS = (
    "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_NEW_ROUTE_FAMILY_PREREGISTRATION_CONTRACT_PROPOSAL_AFTER_GOVERNANCE_SUMMARY_CREATED"
)
ATTEMPTED_EXECUTION_MODULE = (
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_reversal_search_execution_after_governance_approval_v1.py"
)
PRIOR_HEAD = "6b742a30bc0c1320388b4ab421a178ada8e530d9"
ROUTE_FAMILY = "CROSS_SECTIONAL_REVERSAL_BASELINE"
MOMENTUM_RESULT_CLASS = "MOMENTUM_BASELINE_REJECTED_NO_FOLLOWUP"
BLOCKER_CLASS = "REPO_ONLY_VS_REQUIRED_PANEL_ROW_ACCESS_SCOPE_CONFLICT"
EXACT_BLOCKER = (
    "finalized revised non-holdout panel rows required, but no repo-local panel exists and non-repo paths are forbidden"
)

REPO_SCOPE: dict[str, str] = {
    "project": "Edge Factory OS / OKX historical data + research governance pipeline",
    "panel_scope": "OKX 88-symbol 1h panel",
}

SOURCE_CHECKPOINT: dict[str, Any] = {
    "prior_head": PRIOR_HEAD,
    "prior_tracked_python_count": 800,
    "prior_execution_approval_module": PRIOR_EXECUTION_APPROVAL_MODULE,
    "prior_execution_approval_status": PRIOR_EXECUTION_APPROVAL_STATUS,
    "attempted_execution_module": ATTEMPTED_EXECUTION_MODULE,
    "attempted_execution_created": False,
    "attempted_execution_committed": False,
    "repo_clean_after_block": True,
    "tracked_python_count_after_block": 800,
    "changed_paths_after_block": (),
    "code_changed_after_block": False,
}

BLOCKED_ATTEMPT_RECORD: dict[str, Any] = {
    "blocked": True,
    "blocked_before_code_change": True,
    "blocked_before_execution": True,
    "attempted_execution_module": ATTEMPTED_EXECUTION_MODULE,
    "attempted_route_family": ROUTE_FAMILY,
    "attempted_status_created": False,
    "attempted_commit_created": False,
    "attempted_replacement_checks_all_true": False,
    "exact_blocker": EXACT_BLOCKER,
    "blocker_class": BLOCKER_CLASS,
    "no_substitution_performed": True,
    "no_partial_execution_performed": True,
    "repo_remained_clean": True,
    "tracked_python_count_remained": 800,
}

SCOPE_CONFLICT_ANALYSIS: dict[str, Any] = {
    "required_for_reversal_execution": "finalized_revised_non_holdout_panel_rows",
    "prior_prompt_forbidden_access": (
        "non_repo_paths",
        "external_paths",
        "sealed_holdout",
        "boundary_buffer",
        "all_in_one_panel",
        "original_1m_source_files",
        "external_data",
        "alternative_data",
    ),
    "repo_local_panel_available_for_execution": False,
    "prior_momentum_execution_referenced_sibling_artifact_path": True,
    "sibling_artifact_path_outside_repo_scope": True,
    "cannot_execute_without_resolving_scope": True,
    "safe_block_was_correct": True,
    "continuing_under_conflicted_constraints_allowed": False,
    "substituting_data_source_allowed": False,
    "lowering_governance_standards_allowed": False,
    "blocker_is_not_strategy_result": True,
    "blocker_is_not_reversal_failure": True,
    "blocker_is_not_data_quality_failure": True,
    "blocker_is_access_scope_governance_failure": True,
}

PRIOR_EXECUTION_APPROVAL_PRESERVED: dict[str, Any] = {
    "approval_record_created": True,
    "approval_type": "ONE_FUTURE_RESTRICTED_REVERSAL_SEARCH_EXECUTION_MODULE_NON_HOLDOUT_ONLY",
    "approval_granted_for_future_separate_module": True,
    "approved_future_route_family": ROUTE_FAMILY,
    "approved_future_route_family_count": 1,
    "approved_future_execution_must_reference_preregistration_contract": True,
    "approved_future_execution_must_reference_this_approval_module": True,
    "approved_future_execution_must_be_separate_new_module": True,
    "approved_future_execution_is_single_route_family_only": True,
    "approved_future_execution_is_single_use_governance_step": True,
    "approved_future_execution_may_run_restricted_reversal_search": True,
    "approved_future_execution_may_read_finalized_revised_non_holdout_panel_rows": True,
    "approved_future_execution_may_not_read_holdout": True,
    "approved_future_execution_may_not_read_boundary_buffer": True,
    "approved_future_execution_may_not_read_all_in_one_panel": True,
    "approved_future_execution_may_not_read_original_1m_source_files": True,
    "approved_future_execution_may_not_generate_candidates": True,
    "approved_future_execution_may_not_claim_edge": True,
    "approved_future_execution_may_not_release_family": True,
    "approved_future_execution_may_not_grant_runtime_live_capital": True,
    "approval_did_not_authorize_non_repo_path_under_repo_only_prompt": True,
    "approval_does_not_override_panel_access_scope_conflict": True,
    "final_edge_claim_still_requires_external_or_future_holdout": True,
}

PRIOR_PREREGISTRATION_CONTRACT_PRESERVED: dict[str, Any] = {
    "proposal_created": True,
    "proposal_is_execution_approval": False,
    "proposed_route_family": ROUTE_FAMILY,
    "proposed_route_family_count": 1,
    "selection_basis": "NEW_INDEPENDENT_PREREGISTRATION_PROPOSAL_PERFORMANCE_FREE_THEORETICAL_PRIOR",
    "selection_not_based_on_momentum_validation_performance": True,
    "selection_not_based_on_holdout": True,
    "selection_not_based_on_panel_row_scan": True,
    "selection_not_based_on_new_backtest": True,
    "selection_not_based_on_candidate_generation": True,
    "reversal_was_not_tested_by_prior_momentum_route": True,
    "required_separate_governance_approval_before_execution_was_true": True,
}

PRIOR_NEGATIVE_MOMENTUM_CLOSURE_PRESERVED: dict[str, Any] = {
    "momentum_route_closed": True,
    "momentum_result_class": MOMENTUM_RESULT_CLASS,
    "momentum_diagnostic_promising": False,
    "best_validation_config_id": "momentum_lb48h_hold1h",
    "best_validation_lookback": "48h",
    "best_validation_holding_period": "1h",
    "best_validation_net_metric": -4.680782776161402,
    "validation_positive_after_cost": False,
    "null_baseline_review_passed": False,
    "monthly_stability_review_passed": False,
    "turnover_concentration_review_passed": True,
    "metric_integrity_issue_count": 0,
    "clean_negative_research_result_preserved": True,
    "not_a_data_failure": True,
    "not_a_runtime_failure": True,
    "not_an_edge_claim": True,
    "not_a_family_release": True,
    "momentum_route_retest_allowed_now": False,
    "momentum_parameter_expansion_allowed_now": False,
}

REUSABLE_PANEL_STATUS_PRESERVED: dict[str, Any] = {
    "panel_reusable_for_future_read_only_research": True,
    "panel_valid_for_edge_claim": False,
    "panel_requires_new_preregistered_route_for_future_search": True,
    "panel_valid_for_runtime_or_live": False,
    "panel_valid_for_capital_deployment": False,
    "panel_reuse_requires_governance": True,
    "future_final_edge_claim_requires_external_or_future_holdout": True,
    "finalized_revised_non_holdout_panel_expected_rows": 1802944,
    "finalized_revised_non_holdout_panel_expected_symbols": 88,
    "finalized_revised_non_holdout_panel_expected_rows_per_symbol": 20488,
    "finalized_revised_non_holdout_panel_expected_min_timestamp": "2023-07-01T00:00:00Z",
    "finalized_revised_non_holdout_panel_expected_max_timestamp": "2025-10-31T15:00:00Z",
    "finalized_revised_non_holdout_end_exclusive": "2025-10-31T16:00:00Z",
    "boundary_buffer_start": "2025-10-31T16:00:00Z",
    "boundary_buffer_end": "2025-11-01T00:00:00Z",
    "sealed_holdout_start": "2025-11-01T00:00:00Z",
    "sealed_holdout_end_exclusive": "2026-05-19T00:00:00Z",
}

SAFE_RESOLUTION_OPTIONS: tuple[dict[str, Any], ...] = (
    {
        "option_id": "REPO_LOCAL_PANEL_REGISTRATION_OR_IMPORT_GOVERNANCE",
        "allowed_as_future_governance_step": True,
        "description": (
            "Create a separate governance step that makes the finalized revised non-holdout panel available "
            "under repo-local controlled scope or registers a repo-local immutable manifest without reading rows "
            "in the blocker module."
        ),
        "may_create_or_register_repo_local_panel_artifact_now": False,
        "requires_separate_governance_module": True,
        "requires_hash_or_size_or_schema_validation_before_execution": True,
        "requires_no_holdout_no_boundary_buffer_assertions": True,
        "requires_no_all_in_one_panel_assertion": True,
        "requires_no_original_1m_source_assertion": True,
        "grants_reversal_execution_now": False,
        "grants_candidate_generation_now": False,
        "grants_edge_claim_now": False,
        "grants_runtime_live_capital_now": False,
    },
    {
        "option_id": "EXPLICITLY_WHITELISTED_READ_ONLY_LOCAL_ARTIFACT_SCOPE_AMENDMENT",
        "allowed_as_future_governance_step": True,
        "description": (
            "Create a separate access-scope amendment that explicitly names the sibling finalized revised "
            "non-holdout panel artifact path as a read-only local artifact for one future restricted reversal "
            "execution module."
        ),
        "may_approve_non_repo_read_only_artifact_path_now": False,
        "requires_separate_governance_module": True,
        "requires_exact_absolute_path": True,
        "requires_file_existence_check": True,
        "requires_hash_or_size_or_schema_validation_before_execution": True,
        "requires_timestamp_boundary_assertions": True,
        "requires_boundary_buffer_rows_read_count_zero": True,
        "requires_sealed_holdout_rows_read_count_zero": True,
        "grants_reversal_execution_now": False,
        "grants_candidate_generation_now": False,
        "grants_edge_claim_now": False,
        "grants_runtime_live_capital_now": False,
    },
    {
        "option_id": "DO_NOTHING_KEEP_EXECUTION_BLOCKED",
        "allowed_as_future_governance_step": True,
        "description": "Keep restricted reversal execution blocked until a safe panel access scope is approved.",
        "safest_default_if_scope_not_resolved": True,
        "grants_reversal_execution_now": False,
        "grants_candidate_generation_now": False,
        "grants_edge_claim_now": False,
        "grants_runtime_live_capital_now": False,
    },
)

RECOMMENDED_NEXT_GOVERNANCE_STEP: dict[str, Any] = {
    "recommended_next_module": (
        "edge_factory_os_repo_only_okx_88_symbol_1h_panel_local_artifact_access_scope_amendment_for_reversal_execution_v1.py"
    ),
    "recommendation_type": "SEPARATE_ACCESS_SCOPE_AMENDMENT_REQUIRED_BEFORE_REVERSAL_EXECUTION_RETRY",
    "recommended_resolution_option": "EXPLICITLY_WHITELISTED_READ_ONLY_LOCAL_ARTIFACT_SCOPE_AMENDMENT",
    "rationale": (
        "The approved reversal execution requires finalized revised non-holdout panel rows, but the panel is not "
        "repo-local and the previous prompt forbade non-repo paths. A separate access-scope amendment should "
        "explicitly whitelist the exact local artifact path read-only, with file identity and timestamp-boundary "
        "assertions, before retrying execution."
    ),
    "this_blocker_review_grants_access_scope_amendment": False,
    "this_blocker_review_grants_reversal_execution_retry": False,
    "this_blocker_review_grants_panel_row_read": False,
    "this_blocker_review_grants_candidate_generation": False,
    "this_blocker_review_grants_edge_claim": False,
    "this_blocker_review_grants_runtime_live_capital": False,
}

PERMISSIONS_AFTER_BLOCKER_REVIEW: dict[str, Any] = {
    "blocker_review_created": True,
    "restricted_reversal_execution_remains_blocked": True,
    "access_scope_conflict_recorded": True,
    "future_access_scope_amendment_required_before_execution_retry": True,
    "reversal_execution_retry_allowed_now": False,
    "strategy_search_allowed_now": False,
    "reversal_search_allowed_now": False,
    "panel_row_read_allowed_now": False,
    "non_repo_artifact_access_allowed_now": False,
    "holdout_access_allowed_now": False,
    "boundary_buffer_access_allowed_now": False,
    "all_in_one_panel_access_allowed_now": False,
    "original_1m_source_access_allowed_now": False,
    "momentum_retest_allowed_now": False,
    "momentum_parameter_expansion_allowed_now": False,
    "candidate_generation_allowed_now": False,
    "edge_claim_allowed_now": False,
    "family_release_allowed_now": False,
    "evaluator_allowed_now": False,
    "runtime_permission_allowed_now": False,
    "live_permission_allowed_now": False,
    "capital_permission_allowed_now": False,
}

FORBIDDEN_ACTIONS_CONFIRMED_FALSE: dict[str, bool] = {
    "restricted_reversal_execution_created": False,
    "restricted_reversal_execution_executed": False,
    "strategy_search_executed": False,
    "reversal_tested": False,
    "momentum_search_executed": False,
    "momentum_retest_executed": False,
    "momentum_parameter_expansion_executed": False,
    "route_family_other_than_reversal_tested": False,
    "momentum_vs_reversal_comparison_performed": False,
    "panel_rows_read": False,
    "non_repo_artifact_read": False,
    "candidates_generated": False,
    "edge_claimed": False,
    "family_released": False,
    "holdout_accessed": False,
    "boundary_buffer_accessed": False,
    "all_in_one_panel_accessed": False,
    "original_1m_source_files_read": False,
    "external_data_used": False,
    "alternative_data_used": False,
    "evaluator_run": False,
    "runtime_permission_granted": False,
    "live_permission_granted": False,
    "capital_permission_granted": False,
    "files_written_by_module": False,
    "data_artifacts_created": False,
    "existing_files_modified_by_module": False,
}

VALIDATION_CHECKS: dict[str, Any] = {
    "status_equals_required_status": True,
    "module_path_equals_required_path": True,
    "exactly_one_new_tracked_python_tool_file_expected": True,
    "created_file_expected_count": 1,
    "no_existing_files_modified_expected": True,
    "no_data_files_created_expected": True,
    "blocked_attempt_recorded": True,
    "blocker_class_is_repo_only_vs_required_panel_row_access_scope_conflict": True,
    "restricted_reversal_execution_remains_blocked": True,
    "no_reversal_execution_retry_allowed_now": True,
    "no_strategy_search": True,
    "no_reversal_test": True,
    "no_panel_rows_read": True,
    "no_non_repo_artifact_access": True,
    "no_holdout_access": True,
    "no_boundary_buffer_access": True,
    "no_all_in_one_panel_access": True,
    "no_original_1m_source_access": True,
    "no_external_or_alternative_data": True,
    "no_candidate_generation": True,
    "no_edge_claim": True,
    "no_family_release": True,
    "no_evaluator_run": True,
    "no_runtime_live_capital": True,
    "prior_execution_approval_preserved": True,
    "prior_preregistration_contract_preserved": True,
    "prior_negative_momentum_closure_preserved": True,
    "reusable_panel_status_preserved": True,
    "future_access_scope_amendment_required_before_execution_retry": True,
    "active_p0_blocker_count": 1,
    "active_p1_attention_count": 0,
    "replacement_checks_all_true": True,
}


def build_summary() -> dict[str, Any]:
    return {
        "status": REQUIRED_STATUS,
        "module": MODULE_PATH,
        "repo_scope": REPO_SCOPE,
        "source_checkpoint": SOURCE_CHECKPOINT,
        "blocked_attempt_record": BLOCKED_ATTEMPT_RECORD,
        "scope_conflict_analysis": SCOPE_CONFLICT_ANALYSIS,
        "prior_execution_approval_preserved": PRIOR_EXECUTION_APPROVAL_PRESERVED,
        "prior_preregistration_contract_preserved": PRIOR_PREREGISTRATION_CONTRACT_PRESERVED,
        "prior_negative_momentum_closure_preserved": PRIOR_NEGATIVE_MOMENTUM_CLOSURE_PRESERVED,
        "reusable_panel_status_preserved": REUSABLE_PANEL_STATUS_PRESERVED,
        "safe_resolution_options": SAFE_RESOLUTION_OPTIONS,
        "recommended_next_governance_step": RECOMMENDED_NEXT_GOVERNANCE_STEP,
        "permissions_after_blocker_review": PERMISSIONS_AFTER_BLOCKER_REVIEW,
        "forbidden_actions_confirmed_false": FORBIDDEN_ACTIONS_CONFIRMED_FALSE,
        "validation_checks": VALIDATION_CHECKS,
        "replacement_checks_all_true": True,
    }


def validate_summary(summary: dict[str, Any]) -> None:
    assert summary["status"] == REQUIRED_STATUS
    assert summary["module"] == MODULE_PATH
    checkpoint = summary["source_checkpoint"]
    assert checkpoint["prior_head"] == PRIOR_HEAD
    assert checkpoint["prior_tracked_python_count"] == 800
    assert checkpoint["prior_execution_approval_status"] == PRIOR_EXECUTION_APPROVAL_STATUS
    assert checkpoint["attempted_execution_created"] is False
    assert checkpoint["attempted_execution_committed"] is False

    blocked = summary["blocked_attempt_record"]
    assert blocked["blocked"] is True
    assert blocked["blocked_before_code_change"] is True
    assert blocked["blocked_before_execution"] is True
    assert blocked["attempted_replacement_checks_all_true"] is False
    assert blocked["blocker_class"] == BLOCKER_CLASS
    assert blocked["repo_remained_clean"] is True

    conflict = summary["scope_conflict_analysis"]
    assert conflict["repo_local_panel_available_for_execution"] is False
    assert conflict["cannot_execute_without_resolving_scope"] is True
    assert conflict["continuing_under_conflicted_constraints_allowed"] is False
    assert conflict["substituting_data_source_allowed"] is False
    assert conflict["safe_block_was_correct"] is True

    approval = summary["prior_execution_approval_preserved"]
    assert approval["approved_future_route_family"] == ROUTE_FAMILY
    assert approval["approved_future_route_family_count"] == 1
    assert approval["approval_did_not_authorize_non_repo_path_under_repo_only_prompt"] is True
    assert approval["approval_does_not_override_panel_access_scope_conflict"] is True

    prereg = summary["prior_preregistration_contract_preserved"]
    assert prereg["proposal_created"] is True
    assert prereg["proposal_is_execution_approval"] is False
    assert prereg["proposed_route_family"] == ROUTE_FAMILY
    assert prereg["proposed_route_family_count"] == 1
    assert prereg["required_separate_governance_approval_before_execution_was_true"] is True

    momentum = summary["prior_negative_momentum_closure_preserved"]
    assert momentum["momentum_result_class"] == MOMENTUM_RESULT_CLASS
    assert momentum["best_validation_net_metric"] < 0
    assert momentum["momentum_route_closed"] is True
    assert momentum["momentum_route_retest_allowed_now"] is False
    assert momentum["momentum_parameter_expansion_allowed_now"] is False

    panel = summary["reusable_panel_status_preserved"]
    assert panel["panel_reusable_for_future_read_only_research"] is True
    assert panel["future_final_edge_claim_requires_external_or_future_holdout"] is True
    assert panel["panel_valid_for_edge_claim"] is False
    assert panel["panel_valid_for_runtime_or_live"] is False
    assert panel["panel_valid_for_capital_deployment"] is False

    options = summary["safe_resolution_options"]
    assert len(options) == 3
    assert [option["option_id"] for option in options] == [
        "REPO_LOCAL_PANEL_REGISTRATION_OR_IMPORT_GOVERNANCE",
        "EXPLICITLY_WHITELISTED_READ_ONLY_LOCAL_ARTIFACT_SCOPE_AMENDMENT",
        "DO_NOTHING_KEEP_EXECUTION_BLOCKED",
    ]
    for option in options:
        assert option["allowed_as_future_governance_step"] is True
        for key, value in option.items():
            if key.startswith("grants_"):
                assert value is False, key

    recommended = summary["recommended_next_governance_step"]
    assert recommended["recommended_resolution_option"] == "EXPLICITLY_WHITELISTED_READ_ONLY_LOCAL_ARTIFACT_SCOPE_AMENDMENT"
    for key, value in recommended.items():
        if key.startswith("this_blocker_review_grants_"):
            assert value is False, key

    permissions = summary["permissions_after_blocker_review"]
    assert permissions["blocker_review_created"] is True
    assert permissions["restricted_reversal_execution_remains_blocked"] is True
    assert permissions["future_access_scope_amendment_required_before_execution_retry"] is True
    for key, value in permissions.items():
        if key.endswith("_allowed_now"):
            assert value is False, key

    for key, value in summary["forbidden_actions_confirmed_false"].items():
        assert value is False, key

    checks = summary["validation_checks"]
    assert checks["created_file_expected_count"] == 1
    assert checks["active_p0_blocker_count"] == 1
    assert checks["active_p1_attention_count"] == 0
    for key, value in checks.items():
        if key not in {"created_file_expected_count", "active_p0_blocker_count", "active_p1_attention_count"}:
            assert value is True, key
    assert summary["replacement_checks_all_true"] is True


def main() -> int:
    summary = build_summary()
    validate_summary(summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
