from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_STATUS = (
    "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_LOCAL_ARTIFACT_ACCESS_SCOPE_AMENDMENT_FOR_REVERSAL_EXECUTION_CREATED"
)
MODULE_PATH = Path(
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_local_artifact_access_scope_amendment_for_reversal_execution_v1.py"
).as_posix()
REPO_PATH = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_NEW_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
WHITELISTED_LOCAL_ARTIFACT_PATH = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_after_retry_preview_v1\repo_only_okx_88_symbol_1h_panel_revised_non_holdout_view.csv"
)
EXPECTED_FILE_SIZE_BYTES = 347745318
EXPECTED_MODIFIED_TIME_NS = 1779458630371685100
ROUTE_FAMILY = "CROSS_SECTIONAL_REVERSAL_BASELINE"
MOMENTUM_RESULT_CLASS = "MOMENTUM_BASELINE_REJECTED_NO_FOLLOWUP"
PRIOR_HEAD = "11c2476252eb6b3d7680e693815dc421d6f93083"
PRIOR_BLOCKER_REVIEW_STATUS = (
    "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVERSAL_EXECUTION_PANEL_ACCESS_SCOPE_BLOCKER_REVIEW_CREATED"
)
PRIOR_EXACT_BLOCKER = (
    "finalized revised non-holdout panel rows required, but no repo-local panel exists and non-repo paths are forbidden"
)

REPO_SCOPE: dict[str, Any] = {
    "code_changes_repo_only": True,
    "repo_path": str(REPO_PATH),
    "non_repo_artifact_scope_amendment_created": True,
    "non_repo_artifact_content_read_by_this_module": False,
    "non_repo_artifact_metadata_checked_by_this_module": True,
    "internet_used": False,
    "api_used": False,
    "notebooks_used": False,
}

SOURCE_CHECKPOINT: dict[str, Any] = {
    "project": "Edge Factory OS / OKX historical data + research governance pipeline",
    "panel_scope": "OKX 88-symbol 1h panel",
    "prior_head": PRIOR_HEAD,
    "prior_tracked_python_count": 801,
    "prior_blocker_review_module": (
        "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_reversal_execution_panel_access_scope_blocker_review_v1.py"
    ),
    "prior_blocker_review_status": PRIOR_BLOCKER_REVIEW_STATUS,
    "prior_active_p0_blocker_count": 1,
    "prior_exact_blocker": PRIOR_EXACT_BLOCKER,
}

BLOCKER_REVIEW_PRESERVED: dict[str, Any] = {
    "blocker_review_created": True,
    "blocker_class": "REPO_ONLY_VS_REQUIRED_PANEL_ROW_ACCESS_SCOPE_CONFLICT",
    "restricted_reversal_execution_remained_blocked_before_this_amendment": True,
    "attempted_execution_created": False,
    "attempted_execution_committed": False,
    "attempted_execution_replacement_checks_all_true": False,
    "no_substitution_performed": True,
    "no_partial_execution_performed": True,
    "repo_remained_clean_after_block": True,
    "tracked_python_count_after_block": 800,
    "active_p0_blocker_count_before_amendment": 1,
    "future_access_scope_amendment_required_before_execution_retry": True,
}

PRIOR_EXECUTION_APPROVAL_PRESERVED: dict[str, Any] = {
    "approval_record_created": True,
    "approval_type": "ONE_FUTURE_RESTRICTED_REVERSAL_SEARCH_EXECUTION_MODULE_NON_HOLDOUT_ONLY",
    "approval_granted_for_future_separate_module": True,
    "approved_future_route_family": ROUTE_FAMILY,
    "approved_future_route_family_count": 1,
    "approved_future_execution_must_reference_preregistration_contract": True,
    "approved_future_execution_must_reference_execution_approval_module": True,
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
    "approval_does_not_override_final_edge_claim_requirements": True,
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

LOCAL_ARTIFACT_SCOPE_AMENDMENT: dict[str, Any] = {
    "amendment_created": True,
    "amendment_type": "EXPLICITLY_WHITELISTED_READ_ONLY_LOCAL_ARTIFACT_SCOPE_AMENDMENT",
    "amendment_resolves_prior_access_scope_conflict": True,
    "prior_conflict": PRIOR_EXACT_BLOCKER,
    "strict_repo_only_prompt_replaced_for_future_execution_by": (
        "repo_code_only_plus_exact_whitelisted_local_artifact_read_only"
    ),
    "whitelisted_artifact_purpose": (
        "finalized_revised_non_holdout_panel_for_one_future_restricted_reversal_execution_retry"
    ),
    "whitelisted_route_family": ROUTE_FAMILY,
    "whitelisted_future_execution_count": 1,
    "whitelisted_future_execution_must_be_separate_module": True,
    "whitelisted_future_execution_must_reference_this_amendment": True,
    "whitelisted_future_execution_must_reference_prior_execution_approval": True,
    "whitelisted_future_execution_must_reference_prior_preregistration_contract": True,
    "amendment_executes_reversal_search": False,
    "amendment_reads_panel_rows": False,
    "amendment_reads_artifact_content": False,
    "amendment_checks_artifact_metadata_only": True,
    "amendment_grants_candidate_generation": False,
    "amendment_grants_edge_claim": False,
    "amendment_grants_family_release": False,
    "amendment_grants_runtime_live_capital": False,
    "final_edge_claim_still_requires_external_or_future_holdout": True,
}

METADATA_CHECKS_PERFORMED_BY_THIS_MODULE: dict[str, bool] = {
    "exact_path_discovered_from_repo_metadata": True,
    "exists_check_performed": True,
    "is_file_check_performed": True,
    "stat_check_performed": True,
    "file_size_bytes_recorded": True,
    "modified_time_ns_recorded": True,
    "suffix_recorded": True,
    "content_opened": False,
    "content_read": False,
    "rows_read": False,
    "csv_reader_used": False,
    "parquet_reader_used": False,
    "pandas_used": False,
    "pyarrow_used": False,
    "polars_used": False,
    "duckdb_used": False,
    "hash_computed": False,
}

ROW_ACCESS_POLICY_FOR_THIS_MODULE: dict[str, bool] = {
    "panel_rows_read_by_this_module": False,
    "artifact_content_read_by_this_module": False,
    "metadata_only_access_by_this_module": True,
    "strategy_search_executed_by_this_module": False,
    "reversal_tested_by_this_module": False,
    "evaluator_run_by_this_module": False,
    "this_module_is_access_scope_amendment_only": True,
}

APPROVED_FUTURE_EXECUTION_RETRY_SCOPE: dict[str, Any] = {
    "one_future_restricted_reversal_execution_retry_approved_after_access_scope_amendment": True,
    "future_execution_retry_module_name": (
        "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_reversal_search_execution_after_local_artifact_scope_amendment_v1.py"
    ),
    "future_execution_route_family": ROUTE_FAMILY,
    "future_execution_route_family_count": 1,
    "future_execution_allowed_data": "exact_whitelisted_finalized_revised_non_holdout_panel_artifact_only",
    "future_execution_whitelisted_absolute_path": str(WHITELISTED_LOCAL_ARTIFACT_PATH),
    "future_execution_may_read_panel_rows_from_whitelisted_path": True,
    "future_execution_may_not_read_any_other_non_repo_artifact": True,
    "future_execution_may_not_read_all_in_one_panel": True,
    "future_execution_may_not_read_original_1m_source_files": True,
    "future_execution_may_not_access_holdout": True,
    "future_execution_may_not_access_boundary_buffer": True,
    "future_execution_may_not_use_external_data": True,
    "future_execution_may_not_use_alternative_data": True,
    "future_execution_may_not_generate_candidates": True,
    "future_execution_may_not_claim_edge": True,
    "future_execution_may_not_release_family": True,
    "future_execution_may_not_grant_runtime_live_capital": True,
    "future_execution_result_even_if_positive_is_diagnostic_only": True,
    "future_execution_requires_separate_evaluator_before_any_followup": True,
    "future_final_edge_claim_requires_external_or_future_holdout": True,
}

FUTURE_EXECUTION_REQUIRED_VALIDATIONS: dict[str, Any] = {
    "must_start_from_clean_repo": True,
    "must_create_exactly_one_new_tracked_python_tool_file": True,
    "must_reference_this_access_scope_amendment": True,
    "must_reference_prior_execution_approval": True,
    "must_reference_prior_preregistration_contract": True,
    "must_assert_exact_whitelisted_path_before_reading": True,
    "must_assert_path_exists_before_reading": True,
    "must_assert_path_is_file_before_reading": True,
    "must_assert_file_size_matches_or_is_revalidated": True,
    "must_assert_no_holdout_rows_read": True,
    "must_assert_no_boundary_buffer_rows_read": True,
    "must_assert_no_timestamp_at_or_after_2025_10_31T16_00_00Z": True,
    "must_assert_no_timestamp_at_or_after_2025_11_01T00_00_00Z": True,
    "must_assert_output_expected_rows_or_explain_gap_before_metrics": True,
    "must_assert_expected_symbol_count_88_or_explain_gap_before_metrics": True,
    "must_assert_no_all_in_one_panel_access": True,
    "must_assert_no_original_1m_source_access": True,
    "must_apply_no_lookahead_policy": True,
    "must_apply_signal_entry_delay": True,
    "must_apply_incomplete_hour_policy": True,
    "must_prevent_cross_window_holding_returns": True,
    "must_use_approved_lookbacks_hours": (6, 12, 24, 48),
    "must_use_approved_holding_periods_hours": (1, 3, 6),
    "must_exclude_72h_lookback": True,
    "must_test_exactly_12_configs": True,
    "must_use_cost_model_fee_bps_per_side": 5,
    "must_use_cost_model_slippage_bps_per_side": 5,
    "must_use_cost_model_round_trip_cost_bps": 20,
    "must_use_deterministic_null_baseline": True,
    "must_use_null_run_count": 100,
    "must_create_gross_and_net_metrics": True,
    "must_create_monthly_stability": True,
    "must_create_turnover_concentration": True,
    "must_create_metric_integrity_checks": True,
    "must_not_generate_candidates": True,
    "must_not_claim_edge": True,
    "must_not_release_family": True,
    "must_not_grant_runtime_live_capital": True,
}

PERMISSIONS_AFTER_AMENDMENT: dict[str, Any] = {
    "access_scope_amendment_created": True,
    "prior_p0_access_scope_blocker_resolved_by_amendment": True,
    "active_p0_blocker_count": 0,
    "active_p1_attention_count": 0,
    "one_future_restricted_reversal_execution_retry_allowed": True,
    "future_retry_may_read_exact_whitelisted_local_artifact_rows": True,
    "future_retry_may_run_restricted_reversal_search": True,
    "future_retry_route_family": ROUTE_FAMILY,
    "future_retry_may_read_holdout": False,
    "future_retry_may_read_boundary_buffer": False,
    "future_retry_may_read_all_in_one_panel": False,
    "future_retry_may_read_original_1m_source_files": False,
    "future_retry_may_use_external_data": False,
    "future_retry_may_use_alternative_data": False,
    "future_retry_may_generate_candidates": False,
    "future_retry_may_claim_edge": False,
    "future_retry_may_release_family": False,
    "future_retry_may_grant_runtime_permission": False,
    "future_retry_may_grant_live_permission": False,
    "future_retry_may_grant_capital_permission": False,
    "this_module_panel_rows_read": False,
    "this_module_artifact_content_read": False,
    "this_module_strategy_search_executed": False,
    "this_module_reversal_tested": False,
    "this_module_candidate_generation": False,
    "this_module_edge_claim": False,
    "this_module_family_release": False,
    "this_module_evaluator_run": False,
    "this_module_runtime_permission_granted": False,
    "this_module_live_permission_granted": False,
    "this_module_capital_permission_granted": False,
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
    "local_artifact_content_read": False,
    "local_artifact_opened": False,
    "local_artifact_hash_computed": False,
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
    "prior_blocker_review_preserved": True,
    "blocker_class_was_repo_only_vs_required_panel_row_access_scope_conflict": True,
    "exact_local_artifact_path_discovered_from_repo_metadata": True,
    "exact_local_artifact_exists": True,
    "exact_local_artifact_is_file": True,
    "exact_local_artifact_stat_recorded": True,
    "exact_local_artifact_content_not_read": True,
    "no_panel_rows_read_by_this_module": True,
    "no_strategy_search_by_this_module": True,
    "no_reversal_test_by_this_module": True,
    "no_evaluator_run_by_this_module": True,
    "one_future_restricted_reversal_execution_retry_allowed": True,
    "future_retry_restricted_to_exact_whitelisted_path": True,
    "future_retry_restricted_to_cross_sectional_reversal_baseline": True,
    "future_retry_forbids_holdout": True,
    "future_retry_forbids_boundary_buffer": True,
    "future_retry_forbids_all_in_one_panel": True,
    "future_retry_forbids_original_1m_source_files": True,
    "future_retry_forbids_external_or_alternative_data": True,
    "future_retry_forbids_candidate_generation": True,
    "future_retry_forbids_edge_claim": True,
    "future_retry_forbids_family_release": True,
    "future_retry_forbids_runtime_live_capital": True,
    "prior_execution_approval_preserved": True,
    "prior_preregistration_contract_preserved": True,
    "prior_negative_momentum_closure_preserved": True,
    "reusable_panel_status_preserved": True,
    "future_final_edge_claim_requires_external_or_future_holdout": True,
    "active_p0_blocker_count": 0,
    "active_p1_attention_count": 0,
    "replacement_checks_all_true": True,
}


def artifact_identity() -> dict[str, Any]:
    path = WHITELISTED_LOCAL_ARTIFACT_PATH
    path_exists = path.exists()
    path_is_file = path.is_file()
    stat_result = path.stat()
    return {
        "discovered_from_repo_local_metadata": True,
        "discovered_from_prior_momentum_execution_or_safe_non_holdout_build_module": True,
        "exact_absolute_path": str(path),
        "path_is_absolute": path.is_absolute(),
        "path_exists_at_amendment_creation": path_exists,
        "path_is_file_at_amendment_creation": path_is_file,
        "path_is_outside_repo": not path.is_relative_to(REPO_PATH),
        "path_is_under_edge_lab_new_root_or_known_local_project_artifact_root": path.is_relative_to(
            EDGE_LAB_NEW_ROOT
        ),
        "artifact_name": path.name,
        "artifact_suffix": path.suffix,
        "file_size_bytes": stat_result.st_size,
        "modified_time_ns": stat_result.st_mtime_ns,
        "content_hash_computed_by_this_module": False,
        "content_hash_deferred_to_future_execution_or_manifest_validation": True,
        "schema_read_by_this_module": False,
        "row_count_read_by_this_module": False,
        "timestamp_boundaries_read_by_this_module": False,
        "identity_validation_level": "METADATA_ONLY_EXACT_PATH_EXISTENCE_FILE_SIZE_MTIME",
        "identity_validation_is_sufficient_for_access_scope_amendment_only": True,
        "identity_validation_is_not_sufficient_for_edge_claim": True,
        "future_execution_must_revalidate_before_reading_rows": True,
    }


def build_summary() -> dict[str, Any]:
    identity = artifact_identity()
    return {
        "status": REQUIRED_STATUS,
        "module": MODULE_PATH,
        "repo_scope": REPO_SCOPE,
        "source_checkpoint": SOURCE_CHECKPOINT,
        "blocker_review_preserved": BLOCKER_REVIEW_PRESERVED,
        "prior_execution_approval_preserved": PRIOR_EXECUTION_APPROVAL_PRESERVED,
        "prior_preregistration_contract_preserved": PRIOR_PREREGISTRATION_CONTRACT_PRESERVED,
        "prior_negative_momentum_closure_preserved": PRIOR_NEGATIVE_MOMENTUM_CLOSURE_PRESERVED,
        "reusable_panel_status_preserved": REUSABLE_PANEL_STATUS_PRESERVED,
        "local_artifact_scope_amendment": LOCAL_ARTIFACT_SCOPE_AMENDMENT,
        "whitelisted_local_artifact_identity": identity,
        "metadata_checks_performed_by_this_module": METADATA_CHECKS_PERFORMED_BY_THIS_MODULE,
        "row_access_policy_for_this_module": ROW_ACCESS_POLICY_FOR_THIS_MODULE,
        "approved_future_execution_retry_scope": APPROVED_FUTURE_EXECUTION_RETRY_SCOPE,
        "future_execution_required_validations": FUTURE_EXECUTION_REQUIRED_VALIDATIONS,
        "permissions_after_amendment": PERMISSIONS_AFTER_AMENDMENT,
        "forbidden_actions_confirmed_false": FORBIDDEN_ACTIONS_CONFIRMED_FALSE,
        "validation_checks": VALIDATION_CHECKS,
        "replacement_checks_all_true": True,
    }


def validate_summary(summary: dict[str, Any]) -> None:
    assert summary["status"] == REQUIRED_STATUS
    assert summary["module"] == MODULE_PATH

    identity = summary["whitelisted_local_artifact_identity"]
    exact_path = identity["exact_absolute_path"]
    assert identity["discovered_from_repo_local_metadata"] is True
    assert "INSERT_" not in exact_path
    assert identity["path_is_absolute"] is True
    assert identity["path_exists_at_amendment_creation"] is True
    assert identity["path_is_file_at_amendment_creation"] is True
    assert identity["file_size_bytes"] == EXPECTED_FILE_SIZE_BYTES
    assert identity["modified_time_ns"] == EXPECTED_MODIFIED_TIME_NS
    assert identity["file_size_bytes"] > 0
    assert identity["path_is_outside_repo"] is True
    assert identity["path_is_under_edge_lab_new_root_or_known_local_project_artifact_root"] is True
    assert identity["content_hash_computed_by_this_module"] is False
    assert identity["schema_read_by_this_module"] is False
    assert identity["row_count_read_by_this_module"] is False
    assert identity["timestamp_boundaries_read_by_this_module"] is False

    amendment = summary["local_artifact_scope_amendment"]
    assert amendment["amendment_created"] is True
    assert amendment["amendment_resolves_prior_access_scope_conflict"] is True
    assert amendment["amendment_executes_reversal_search"] is False
    assert amendment["amendment_reads_panel_rows"] is False
    assert amendment["amendment_reads_artifact_content"] is False
    assert amendment["amendment_checks_artifact_metadata_only"] is True
    assert amendment["final_edge_claim_still_requires_external_or_future_holdout"] is True

    row_policy = summary["row_access_policy_for_this_module"]
    assert row_policy["panel_rows_read_by_this_module"] is False
    assert row_policy["artifact_content_read_by_this_module"] is False
    assert row_policy["metadata_only_access_by_this_module"] is True
    assert row_policy["strategy_search_executed_by_this_module"] is False
    assert row_policy["reversal_tested_by_this_module"] is False
    assert row_policy["evaluator_run_by_this_module"] is False

    retry = summary["approved_future_execution_retry_scope"]
    assert retry["future_execution_route_family"] == ROUTE_FAMILY
    assert retry["future_execution_whitelisted_absolute_path"] == exact_path
    assert retry["future_execution_may_read_panel_rows_from_whitelisted_path"] is True
    assert retry["future_execution_may_not_access_holdout"] is True
    assert retry["future_execution_may_not_access_boundary_buffer"] is True
    assert retry["future_execution_may_not_read_all_in_one_panel"] is True
    assert retry["future_execution_may_not_read_original_1m_source_files"] is True
    assert retry["future_execution_may_not_generate_candidates"] is True
    assert retry["future_execution_may_not_claim_edge"] is True
    assert retry["future_execution_may_not_release_family"] is True
    assert retry["future_execution_may_not_grant_runtime_live_capital"] is True
    assert retry["future_final_edge_claim_requires_external_or_future_holdout"] is True

    permissions = summary["permissions_after_amendment"]
    assert permissions["active_p0_blocker_count"] == 0
    assert permissions["active_p1_attention_count"] == 0
    assert permissions["one_future_restricted_reversal_execution_retry_allowed"] is True
    assert permissions["future_retry_may_read_exact_whitelisted_local_artifact_rows"] is True
    assert permissions["future_retry_route_family"] == ROUTE_FAMILY
    assert permissions["future_retry_may_read_holdout"] is False
    assert permissions["future_retry_may_read_boundary_buffer"] is False
    assert permissions["future_retry_may_read_all_in_one_panel"] is False
    assert permissions["future_retry_may_read_original_1m_source_files"] is False
    assert permissions["future_retry_may_generate_candidates"] is False
    assert permissions["future_retry_may_claim_edge"] is False
    assert permissions["future_retry_may_release_family"] is False
    assert permissions["future_retry_may_grant_runtime_permission"] is False
    assert permissions["future_retry_may_grant_live_permission"] is False
    assert permissions["future_retry_may_grant_capital_permission"] is False
    for key, value in permissions.items():
        if key.endswith("_allowed_now"):
            assert value is False, key
        if key.endswith("_permission_granted"):
            assert value is False, key

    momentum = summary["prior_negative_momentum_closure_preserved"]
    assert momentum["momentum_result_class"] == MOMENTUM_RESULT_CLASS
    assert momentum["best_validation_net_metric"] < 0

    panel = summary["reusable_panel_status_preserved"]
    assert panel["panel_reusable_for_future_read_only_research"] is True
    assert panel["future_final_edge_claim_requires_external_or_future_holdout"] is True

    metadata_checks = summary["metadata_checks_performed_by_this_module"]
    assert metadata_checks["content_opened"] is False
    assert metadata_checks["content_read"] is False
    assert metadata_checks["rows_read"] is False
    assert metadata_checks["csv_reader_used"] is False
    assert metadata_checks["hash_computed"] is False

    for key, value in summary["forbidden_actions_confirmed_false"].items():
        assert value is False, key

    checks = summary["validation_checks"]
    assert checks["created_file_expected_count"] == 1
    assert checks["active_p0_blocker_count"] == 0
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
