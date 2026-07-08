from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_STATUS = (
    "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVERSAL_EXECUTION_GOVERNANCE_APPROVAL_AFTER_PREREGISTRATION_CONTRACT_CREATED"
)
MODULE_PATH = Path(
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_reversal_execution_governance_approval_after_preregistration_contract_v1.py"
).as_posix()
PRIOR_PREREGISTRATION_CONTRACT_MODULE = (
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_new_route_family_preregistration_contract_proposal_after_governance_summary_v1.py"
)
PRIOR_PREREGISTRATION_CONTRACT_STATUS = (
    "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_NEW_ROUTE_FAMILY_PREREGISTRATION_CONTRACT_PROPOSAL_AFTER_GOVERNANCE_SUMMARY_CREATED"
)
PRIOR_HEAD = "015a80695783e2ff0d6140bf517371218fd363d6"
ROUTE_FAMILY = "CROSS_SECTIONAL_REVERSAL_BASELINE"
MOMENTUM_RESULT_CLASS = "MOMENTUM_BASELINE_REJECTED_NO_FOLLOWUP"
BEST_VALIDATION_NET_METRIC = -4.680782776161402

REPO_SCOPE: dict[str, str] = {
    "project": "Edge Factory OS / OKX historical data + research governance pipeline",
    "panel_scope": "OKX 88-symbol 1h panel",
}

SOURCE_CHECKPOINT: dict[str, Any] = {
    "prior_preregistration_contract_module": PRIOR_PREREGISTRATION_CONTRACT_MODULE,
    "prior_preregistration_contract_status": PRIOR_PREREGISTRATION_CONTRACT_STATUS,
    "prior_head": PRIOR_HEAD,
    "prior_tracked_python_count": 799,
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
    "relationship_to_prior_closure": "independent_new_route_family_preregistration_proposal_not_a_momentum_followup_grant",
    "reversal_was_not_tested_by_prior_momentum_route": True,
    "route_family_is_candidate_for_future_approval_only": True,
    "required_separate_governance_approval_before_execution_was_true": True,
}

PRIOR_NEGATIVE_MOMENTUM_CLOSURE_PRESERVED: dict[str, Any] = {
    "momentum_route_closed": True,
    "momentum_result_class": MOMENTUM_RESULT_CLASS,
    "momentum_diagnostic_promising": False,
    "best_validation_config_id": "momentum_lb48h_hold1h",
    "best_validation_lookback": "48h",
    "best_validation_holding_period": "1h",
    "best_validation_net_metric": BEST_VALIDATION_NET_METRIC,
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

REUSABLE_PANEL_STATUS_PRESERVED: dict[str, bool] = {
    "panel_reusable_for_future_read_only_research": True,
    "panel_valid_for_edge_claim": False,
    "panel_requires_new_preregistered_route_for_future_search": True,
    "panel_valid_for_runtime_or_live": False,
    "panel_valid_for_capital_deployment": False,
    "panel_reuse_requires_governance": True,
    "future_final_edge_claim_requires_external_or_future_holdout": True,
}

EXECUTION_APPROVAL_DECISION: dict[str, Any] = {
    "approval_record_created": True,
    "approval_type": "ONE_FUTURE_RESTRICTED_REVERSAL_SEARCH_EXECUTION_MODULE_NON_HOLDOUT_ONLY",
    "approval_granted_for_future_separate_module": True,
    "approval_executes_search_in_this_module": False,
    "approval_reads_panel_rows_in_this_module": False,
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
    "approval_does_not_override_final_edge_claim_requirements": True,
    "final_edge_claim_still_requires_external_or_future_holdout": True,
}

APPROVED_FUTURE_RESTRICTED_REVERSAL_SEARCH_SCOPE: dict[str, Any] = {
    "scope_is_only_for_future_separate_execution_module_do_not_run_here": True,
    "route_family": ROUTE_FAMILY,
    "route_description": (
        "Cross-sectional reversal baseline using prior relative underperformance as the proposed long leg "
        "and prior relative outperformance as the proposed short leg, subject to this approval and future "
        "execution controls."
    ),
    "allowed_data_for_future_execution": "finalized_revised_non_holdout_panel_only",
    "forbidden_data_for_future_execution": (
        "sealed_holdout",
        "boundary_buffer",
        "all_in_one_panel",
        "original_1m_source_files",
        "external_data",
        "alternative_data",
    ),
    "train_development_window_start": "2023-07-01T00:00:00Z",
    "train_development_window_end_exclusive": "2025-01-01T00:00:00Z",
    "validation_window_start": "2025-01-01T00:00:00Z",
    "validation_window_revised_safe_non_holdout_end_exclusive": "2025-10-31T16:00:00Z",
    "sealed_holdout_start": "2025-11-01T00:00:00Z",
    "sealed_holdout_end_exclusive": "2026-05-19T00:00:00Z",
    "boundary_buffer_start": "2025-10-31T16:00:00Z",
    "boundary_buffer_end": "2025-11-01T00:00:00Z",
    "lookback_options_hours": (6, 12, 24, 48),
    "excluded_lookback_hours_from_this_contract": (72,),
    "holding_periods_hours": (1, 3, 6),
    "approved_config_grid_count": 12,
    "signal_definition": (
        "rank symbols cross-sectionally by trailing close-to-close return over the lookback window; "
        "reversal signal goes long lower trailing-return ranks and short higher trailing-return ranks "
        "after required lag"
    ),
    "no_symbol_specific_tuning": True,
    "no_ml": True,
    "no_ensemble": True,
    "no_alternative_data": True,
    "no_funding_data": True,
    "no_order_book_data": True,
    "no_social_data": True,
    "no_news_data": True,
    "cost_policy": {
        "fee_bps_per_side": 5,
        "slippage_bps_per_side": 5,
        "round_trip_cost_bps": 20,
    },
    "null_baseline": "deterministic_block_shuffled_timestamp_spread_return_null",
    "null_run_count": 100,
    "required_outputs_for_future_execution": (
        "gross_metrics",
        "net_cost_adjusted_metrics",
        "deterministic_null_baseline",
        "monthly_stability",
        "turnover_concentration",
        "metric_integrity_checks",
        "execution_closure_recommendation",
    ),
    "candidate_generation_allowed": False,
    "edge_claim_allowed": False,
    "family_release_allowed": False,
    "runtime_live_capital_allowed": False,
}

REQUIRED_FUTURE_EXECUTION_CONTROLS: dict[str, bool] = {
    "future_execution_must_start_from_clean_repo": True,
    "future_execution_must_create_exactly_one_new_tracked_python_tool_file": True,
    "future_execution_must_not_modify_existing_files_without_new_governance": True,
    "future_execution_must_not_create_data_artifacts_without_new_governance": True,
    "future_execution_must_use_finalized_revised_non_holdout_panel_only": True,
    "future_execution_must_not_use_all_in_one_panel": True,
    "future_execution_must_not_use_original_1m_source_files": True,
    "future_execution_must_not_access_sealed_holdout": True,
    "future_execution_must_not_access_boundary_buffer": True,
    "future_execution_must_apply_no_lookahead_policy": True,
    "future_execution_must_apply_signal_entry_delay": True,
    "future_execution_must_apply_incomplete_hour_policy": True,
    "future_execution_must_prevent_cross_window_holding_returns": True,
    "future_execution_must_include_gross_and_net_metrics": True,
    "future_execution_must_include_cost_model": True,
    "future_execution_must_include_null_baseline": True,
    "future_execution_must_include_monthly_stability": True,
    "future_execution_must_include_turnover_concentration": True,
    "future_execution_must_include_metric_integrity_checks": True,
    "future_execution_must_not_generate_candidates": True,
    "future_execution_must_not_claim_edge": True,
    "future_execution_must_not_release_family": True,
    "future_execution_must_not_grant_runtime_live_capital": True,
    "future_execution_results_even_if_positive_are_diagnostic_only": True,
    "future_positive_result_would_require_separate_evaluator_and_governance": True,
    "future_final_edge_claim_requires_external_or_future_holdout": True,
    "future_holdout_access_requires_separate_governance": True,
}

PERMISSIONS_AFTER_APPROVAL: dict[str, Any] = {
    "approval_record_created": True,
    "one_future_restricted_reversal_search_execution_module_approved": True,
    "approved_future_module_route_family": ROUTE_FAMILY,
    "approved_future_module_may_run_restricted_reversal_search": True,
    "approved_future_module_may_read_finalized_revised_non_holdout_panel_rows": True,
    "approved_future_module_may_access_holdout": False,
    "approved_future_module_may_access_boundary_buffer": False,
    "approved_future_module_may_access_all_in_one_panel": False,
    "approved_future_module_may_access_original_1m_source_files": False,
    "approved_future_module_may_generate_candidates": False,
    "approved_future_module_may_claim_edge": False,
    "approved_future_module_may_release_family": False,
    "approved_future_module_may_grant_runtime_permission": False,
    "approved_future_module_may_grant_live_permission": False,
    "approved_future_module_may_grant_capital_permission": False,
    "strategy_search_executed_by_this_module": False,
    "reversal_tested_by_this_module": False,
    "panel_rows_read_by_this_module": False,
    "holdout_accessed_by_this_module": False,
    "candidate_generation_by_this_module": False,
    "edge_claim_by_this_module": False,
    "family_release_by_this_module": False,
    "runtime_permission_granted_by_this_module": False,
    "live_permission_granted_by_this_module": False,
    "capital_permission_granted_by_this_module": False,
    "momentum_retest_allowed_now": False,
    "momentum_parameter_expansion_allowed_now": False,
    "candidate_generation_allowed_now": False,
    "edge_claim_allowed_now": False,
    "family_release_allowed_now": False,
    "holdout_access_allowed_now": False,
    "runtime_permission_allowed_now": False,
    "live_permission_allowed_now": False,
    "capital_permission_allowed_now": False,
}

FORBIDDEN_ACTIONS_CONFIRMED_FALSE: dict[str, bool] = {
    "new_strategy_search_executed": False,
    "reversal_tested": False,
    "momentum_retest_executed": False,
    "momentum_parameter_expansion_executed": False,
    "candidates_generated": False,
    "edge_claimed": False,
    "family_released": False,
    "holdout_accessed": False,
    "boundary_buffer_accessed": False,
    "all_in_one_panel_accessed": False,
    "finalized_panel_rows_read": False,
    "original_1m_source_files_read": False,
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
    "no_panel_rows_read_by_this_module": True,
    "no_holdout_access_by_this_module": True,
    "no_boundary_buffer_access_by_this_module": True,
    "no_strategy_search_by_this_module": True,
    "no_reversal_test_by_this_module": True,
    "no_momentum_retest": True,
    "no_momentum_parameter_expansion": True,
    "no_candidate_generation": True,
    "no_edge_claim": True,
    "no_family_release": True,
    "no_runtime_live_capital": True,
    "prior_preregistration_contract_preserved": True,
    "proposed_route_family_is_cross_sectional_reversal_baseline": True,
    "approved_future_route_family_count_is_one": True,
    "one_future_restricted_reversal_search_execution_module_approved": True,
    "approval_executes_no_search_in_this_module": True,
    "approved_future_execution_non_holdout_only": True,
    "approved_future_execution_forbids_holdout": True,
    "approved_future_execution_forbids_boundary_buffer": True,
    "approved_future_execution_forbids_candidates_edge_release_runtime_live_capital": True,
    "momentum_result_is_negative_and_closed": True,
    "reusable_panel_status_preserved": True,
    "future_final_edge_claim_requires_external_or_future_holdout": True,
    "active_p0_blocker_count": 0,
    "active_p1_attention_count": 0,
    "replacement_checks_all_true": True,
}


def build_summary() -> dict[str, Any]:
    return {
        "status": REQUIRED_STATUS,
        "module": MODULE_PATH,
        "repo_scope": REPO_SCOPE,
        "source_checkpoint": SOURCE_CHECKPOINT,
        "prior_preregistration_contract_preserved": PRIOR_PREREGISTRATION_CONTRACT_PRESERVED,
        "prior_negative_momentum_closure_preserved": PRIOR_NEGATIVE_MOMENTUM_CLOSURE_PRESERVED,
        "reusable_panel_status_preserved": REUSABLE_PANEL_STATUS_PRESERVED,
        "execution_approval_decision": EXECUTION_APPROVAL_DECISION,
        "approved_future_restricted_reversal_search_scope": APPROVED_FUTURE_RESTRICTED_REVERSAL_SEARCH_SCOPE,
        "required_future_execution_controls": REQUIRED_FUTURE_EXECUTION_CONTROLS,
        "permissions_after_approval": PERMISSIONS_AFTER_APPROVAL,
        "forbidden_actions_confirmed_false": FORBIDDEN_ACTIONS_CONFIRMED_FALSE,
        "validation_checks": VALIDATION_CHECKS,
        "replacement_checks_all_true": True,
    }


def validate_summary(summary: dict[str, Any]) -> None:
    assert summary["status"] == REQUIRED_STATUS
    assert summary["module"] == MODULE_PATH
    assert summary["source_checkpoint"]["prior_head"] == PRIOR_HEAD
    assert summary["source_checkpoint"]["prior_tracked_python_count"] == 799
    assert (
        summary["source_checkpoint"]["prior_preregistration_contract_status"]
        == PRIOR_PREREGISTRATION_CONTRACT_STATUS
    )

    prior_contract = summary["prior_preregistration_contract_preserved"]
    assert prior_contract["proposal_created"] is True
    assert prior_contract["proposal_is_execution_approval"] is False
    assert prior_contract["proposed_route_family"] == ROUTE_FAMILY
    assert prior_contract["proposed_route_family_count"] == 1
    assert prior_contract["required_separate_governance_approval_before_execution_was_true"] is True

    momentum = summary["prior_negative_momentum_closure_preserved"]
    assert momentum["momentum_route_closed"] is True
    assert momentum["momentum_result_class"] == MOMENTUM_RESULT_CLASS
    assert momentum["momentum_diagnostic_promising"] is False
    assert momentum["best_validation_net_metric"] < 0
    assert momentum["momentum_route_retest_allowed_now"] is False
    assert momentum["momentum_parameter_expansion_allowed_now"] is False

    panel = summary["reusable_panel_status_preserved"]
    assert panel["panel_reusable_for_future_read_only_research"] is True
    assert panel["future_final_edge_claim_requires_external_or_future_holdout"] is True
    assert panel["panel_valid_for_edge_claim"] is False
    assert panel["panel_valid_for_runtime_or_live"] is False
    assert panel["panel_valid_for_capital_deployment"] is False

    decision = summary["execution_approval_decision"]
    assert decision["approval_record_created"] is True
    assert decision["approval_granted_for_future_separate_module"] is True
    assert decision["approval_executes_search_in_this_module"] is False
    assert decision["approval_reads_panel_rows_in_this_module"] is False
    assert decision["approved_future_route_family"] == ROUTE_FAMILY
    assert decision["approved_future_route_family_count"] == 1
    assert decision["approved_future_execution_may_run_restricted_reversal_search"] is True
    assert decision["approved_future_execution_may_read_finalized_revised_non_holdout_panel_rows"] is True
    assert decision["approved_future_execution_may_not_read_holdout"] is True
    assert decision["approved_future_execution_may_not_read_boundary_buffer"] is True
    assert decision["approved_future_execution_may_not_read_all_in_one_panel"] is True
    assert decision["approved_future_execution_may_not_read_original_1m_source_files"] is True
    assert decision["approved_future_execution_may_not_generate_candidates"] is True
    assert decision["approved_future_execution_may_not_claim_edge"] is True
    assert decision["approved_future_execution_may_not_release_family"] is True
    assert decision["approved_future_execution_may_not_grant_runtime_live_capital"] is True

    scope = summary["approved_future_restricted_reversal_search_scope"]
    assert scope["route_family"] == ROUTE_FAMILY
    assert scope["allowed_data_for_future_execution"] == "finalized_revised_non_holdout_panel_only"
    assert scope["approved_config_grid_count"] == 12
    assert scope["candidate_generation_allowed"] is False
    assert scope["edge_claim_allowed"] is False
    assert scope["family_release_allowed"] is False
    assert scope["runtime_live_capital_allowed"] is False

    controls = summary["required_future_execution_controls"]
    for key, value in controls.items():
        assert value is True, key

    permissions = summary["permissions_after_approval"]
    assert permissions["approval_record_created"] is True
    assert permissions["one_future_restricted_reversal_search_execution_module_approved"] is True
    assert permissions["approved_future_module_route_family"] == ROUTE_FAMILY
    assert permissions["approved_future_module_may_run_restricted_reversal_search"] is True
    assert permissions["approved_future_module_may_read_finalized_revised_non_holdout_panel_rows"] is True
    for key, value in permissions.items():
        if key in {
            "approval_record_created",
            "one_future_restricted_reversal_search_execution_module_approved",
            "approved_future_module_route_family",
            "approved_future_module_may_run_restricted_reversal_search",
            "approved_future_module_may_read_finalized_revised_non_holdout_panel_rows",
        }:
            continue
        assert value is False, key

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
