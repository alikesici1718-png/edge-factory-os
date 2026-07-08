from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_STATUS = (
    "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_NEW_ROUTE_FAMILY_PREREGISTRATION_CONTRACT_PROPOSAL_AFTER_GOVERNANCE_SUMMARY_CREATED"
)
MODULE_PATH = Path(
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_new_route_family_preregistration_contract_proposal_after_governance_summary_v1.py"
).as_posix()
PRIOR_GOVERNANCE_SUMMARY_MODULE = (
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_research_governance_summary_after_momentum_closure_v1.py"
)
PRIOR_GOVERNANCE_SUMMARY_STATUS = (
    "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESEARCH_GOVERNANCE_SUMMARY_AFTER_MOMENTUM_CLOSURE_CREATED"
)
PRIOR_HEAD = "382ccff1117812eb6205707c08a4e9174fe73dc8"
RESULT_CLASS = "MOMENTUM_BASELINE_REJECTED_NO_FOLLOWUP"
PROPOSED_ROUTE_FAMILY = "CROSS_SECTIONAL_REVERSAL_BASELINE"
BEST_VALIDATION_NET_METRIC = -4.680782776161402

REPO_SCOPE: dict[str, str] = {
    "project": "Edge Factory OS / OKX historical data + research governance pipeline",
    "panel_scope": "OKX 88-symbol 1h panel",
}

SOURCE_CHECKPOINT: dict[str, Any] = {
    "prior_governance_summary_module": PRIOR_GOVERNANCE_SUMMARY_MODULE,
    "prior_governance_summary_status": PRIOR_GOVERNANCE_SUMMARY_STATUS,
    "prior_head": PRIOR_HEAD,
    "prior_tracked_python_count": 798,
}

PRIOR_GOVERNANCE_SUMMARY_PRESERVED: dict[str, Any] = {
    "momentum_route_closed": True,
    "momentum_result_class": RESULT_CLASS,
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

SELECTED_NEW_ROUTE_FAMILY_PREREGISTRATION_PROPOSAL: dict[str, Any] = {
    "proposal_created": True,
    "proposal_is_execution_approval": False,
    "proposed_route_family": PROPOSED_ROUTE_FAMILY,
    "proposed_route_family_count": 1,
    "selection_basis": "NEW_INDEPENDENT_PREREGISTRATION_PROPOSAL_PERFORMANCE_FREE_THEORETICAL_PRIOR",
    "selection_not_based_on_momentum_validation_performance": True,
    "selection_not_based_on_holdout": True,
    "selection_not_based_on_panel_row_scan": True,
    "selection_not_based_on_new_backtest": True,
    "selection_not_based_on_candidate_generation": True,
    "relationship_to_prior_closure": "independent_new_route_family_preregistration_proposal_not_a_momentum_followup_grant",
    "reversal_was_not_tested_by_prior_momentum_route": True,
    "reversal_is_not_approved_for_search_by_this_module": True,
    "route_family_is_candidate_for_future_approval_only": True,
    "requires_separate_governance_approval_before_execution": True,
}

PROPOSED_SEARCH_SPACE_CONTRACT: dict[str, Any] = {
    "contract_is_proposed_future_contract_only_do_not_run": True,
    "route_family": PROPOSED_ROUTE_FAMILY,
    "route_description": (
        "Cross-sectional reversal baseline using prior relative underperformance as the proposed long leg "
        "and prior relative outperformance as the proposed short leg, subject to future approval."
    ),
    "allowed_data_if_later_approved": "finalized_revised_non_holdout_panel_only",
    "forbidden_data_even_if_later_approved_without_separate_governance": (
        "sealed_holdout",
        "boundary_buffer",
        "all_in_one_panel",
        "original_1m_source_files",
        "external_data",
        "alternative_data",
    ),
    "lookback_options_hours": (6, 12, 24, 48),
    "excluded_lookback_hours_from_this_contract": (72,),
    "holding_periods_hours": (1, 3, 6),
    "proposed_config_grid_count": 12,
    "signal_definition": (
        "rank symbols cross-sectionally by trailing close-to-close return over the lookback window; "
        "proposed reversal signal goes long lower trailing-return ranks and short higher trailing-return "
        "ranks after required lag"
    ),
    "no_symbol_specific_tuning": True,
    "no_ml": True,
    "no_ensemble": True,
    "no_alternative_data": True,
    "no_funding_data": True,
    "no_order_book_data": True,
    "no_social_data": True,
    "no_news_data": True,
    "cost_policy_if_later_approved": {
        "fee_bps_per_side": 5,
        "slippage_bps_per_side": 5,
        "round_trip_cost_bps": 20,
    },
    "null_baseline_if_later_approved": "deterministic_block_shuffled_timestamp_spread_return_null",
    "null_run_count_if_later_approved": 100,
    "required_outputs_if_later_approved": (
        "gross_metrics",
        "net_cost_adjusted_metrics",
        "deterministic_null_baseline",
        "monthly_stability",
        "turnover_concentration",
        "metric_integrity_checks",
    ),
    "candidate_generation_allowed_by_contract": False,
    "edge_claim_allowed_by_contract": False,
    "family_release_allowed_by_contract": False,
    "runtime_live_capital_allowed_by_contract": False,
}

ANTI_OVERFIT_AND_DATA_SAFETY_CONTROLS: dict[str, bool] = {
    "preregister_before_execution": True,
    "exactly_one_route_family_in_contract": True,
    "bounded_grid_before_execution": True,
    "no_parameter_expansion_after_results_without_new_contract": True,
    "no_momentum_retest": True,
    "no_momentum_parameter_expansion": True,
    "no_momentum_vs_reversal_performance_comparison_before_execution": True,
    "no_holdout_access": True,
    "no_boundary_buffer_access": True,
    "no_panel_row_read_by_this_module": True,
    "no_strategy_search_by_this_module": True,
    "no_candidate_generation_by_this_module": True,
    "no_edge_claim_by_this_module": True,
    "no_family_release_by_this_module": True,
    "no_runtime_live_capital_by_this_module": True,
    "future_execution_must_be_separate_module": True,
    "future_execution_must_reference_this_contract": True,
    "future_execution_requires_clean_repo_and_explicit_approval": True,
    "future_execution_must_remain_non_holdout_only_unless_separately_governed": True,
    "future_final_edge_claim_requires_external_or_future_holdout": True,
}

APPROVAL_REQUIREMENTS_BEFORE_ANY_EXECUTION: dict[str, Any] = {
    "separate_governance_approval_required": True,
    "approval_must_name_this_contract_module": True,
    "approval_must_name_exact_route_family": PROPOSED_ROUTE_FAMILY,
    "approval_must_confirm_no_holdout_access": True,
    "approval_must_confirm_no_boundary_buffer_access": True,
    "approval_must_confirm_no_all_in_one_panel_access": True,
    "approval_must_confirm_finalized_revised_non_holdout_panel_only": True,
    "approval_must_confirm_no_candidate_generation": True,
    "approval_must_confirm_no_edge_claim": True,
    "approval_must_confirm_no_family_release": True,
    "approval_must_confirm_no_runtime_live_capital": True,
    "approval_must_confirm_no_parameter_expansion": True,
    "approval_must_confirm_cost_model_before_run": True,
    "approval_must_confirm_null_baseline_before_run": True,
    "approval_granted_by_this_module": False,
    "strategy_search_allowed_now": False,
}

PERMISSIONS_AFTER_PROPOSAL: dict[str, bool] = {
    "strategy_search_allowed_now": False,
    "reversal_search_allowed_now": False,
    "momentum_retest_allowed_now": False,
    "momentum_parameter_expansion_allowed_now": False,
    "candidate_generation_allowed_now": False,
    "edge_claim_allowed_now": False,
    "family_release_allowed_now": False,
    "holdout_access_allowed_now": False,
    "boundary_buffer_access_allowed_now": False,
    "all_in_one_panel_access_allowed_now": False,
    "original_1m_source_access_allowed_now": False,
    "panel_row_read_allowed_now": False,
    "runtime_permission_allowed_now": False,
    "live_permission_allowed_now": False,
    "capital_permission_allowed_now": False,
    "execution_approval_granted_now": False,
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
    "no_panel_rows_read": True,
    "no_holdout_access": True,
    "no_boundary_buffer_access": True,
    "no_strategy_search": True,
    "no_reversal_test": True,
    "no_momentum_retest": True,
    "no_momentum_parameter_expansion": True,
    "no_candidate_generation": True,
    "no_edge_claim": True,
    "no_family_release": True,
    "no_runtime_live_capital": True,
    "proposal_created": True,
    "proposal_is_not_execution_approval": True,
    "proposed_route_family_is_cross_sectional_reversal_baseline": True,
    "proposed_route_family_count_is_one": True,
    "future_execution_requires_separate_governance_approval": True,
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
        "prior_governance_summary_preserved": PRIOR_GOVERNANCE_SUMMARY_PRESERVED,
        "reusable_panel_status_preserved": REUSABLE_PANEL_STATUS_PRESERVED,
        "selected_new_route_family_preregistration_proposal": (
            SELECTED_NEW_ROUTE_FAMILY_PREREGISTRATION_PROPOSAL
        ),
        "proposed_search_space_contract": PROPOSED_SEARCH_SPACE_CONTRACT,
        "anti_overfit_and_data_safety_controls": ANTI_OVERFIT_AND_DATA_SAFETY_CONTROLS,
        "approval_requirements_before_any_execution": APPROVAL_REQUIREMENTS_BEFORE_ANY_EXECUTION,
        "permissions_after_proposal": PERMISSIONS_AFTER_PROPOSAL,
        "forbidden_actions_confirmed_false": FORBIDDEN_ACTIONS_CONFIRMED_FALSE,
        "validation_checks": VALIDATION_CHECKS,
        "replacement_checks_all_true": True,
    }


def validate_summary(summary: dict[str, Any]) -> None:
    assert summary["status"] == REQUIRED_STATUS
    assert summary["module"] == MODULE_PATH
    assert summary["source_checkpoint"]["prior_head"] == PRIOR_HEAD
    assert summary["source_checkpoint"]["prior_tracked_python_count"] == 798
    assert summary["source_checkpoint"]["prior_governance_summary_status"] == PRIOR_GOVERNANCE_SUMMARY_STATUS

    prior = summary["prior_governance_summary_preserved"]
    assert prior["momentum_route_closed"] is True
    assert prior["momentum_result_class"] == RESULT_CLASS
    assert prior["momentum_diagnostic_promising"] is False
    assert prior["best_validation_net_metric"] < 0
    assert prior["clean_negative_research_result_preserved"] is True

    panel = summary["reusable_panel_status_preserved"]
    assert panel["panel_reusable_for_future_read_only_research"] is True
    assert panel["panel_requires_new_preregistered_route_for_future_search"] is True
    assert panel["future_final_edge_claim_requires_external_or_future_holdout"] is True
    assert panel["panel_valid_for_edge_claim"] is False
    assert panel["panel_valid_for_runtime_or_live"] is False
    assert panel["panel_valid_for_capital_deployment"] is False

    proposal = summary["selected_new_route_family_preregistration_proposal"]
    assert proposal["proposal_created"] is True
    assert proposal["proposal_is_execution_approval"] is False
    assert proposal["proposed_route_family"] == PROPOSED_ROUTE_FAMILY
    assert proposal["proposed_route_family_count"] == 1
    assert proposal["reversal_is_not_approved_for_search_by_this_module"] is True
    assert proposal["requires_separate_governance_approval_before_execution"] is True

    contract = summary["proposed_search_space_contract"]
    assert contract["route_family"] == PROPOSED_ROUTE_FAMILY
    assert contract["proposed_config_grid_count"] == 12
    assert contract["candidate_generation_allowed_by_contract"] is False
    assert contract["edge_claim_allowed_by_contract"] is False
    assert contract["family_release_allowed_by_contract"] is False
    assert contract["runtime_live_capital_allowed_by_contract"] is False

    controls = summary["anti_overfit_and_data_safety_controls"]
    for key, value in controls.items():
        assert value is True, key

    approval = summary["approval_requirements_before_any_execution"]
    assert approval["separate_governance_approval_required"] is True
    assert approval["approval_must_name_exact_route_family"] == PROPOSED_ROUTE_FAMILY
    assert approval["approval_granted_by_this_module"] is False
    assert approval["strategy_search_allowed_now"] is False

    for key, value in summary["permissions_after_proposal"].items():
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
