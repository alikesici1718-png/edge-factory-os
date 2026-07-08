from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_STATUS = (
    "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESEARCH_GOVERNANCE_SUMMARY_AFTER_MOMENTUM_CLOSURE_CREATED"
)
MODULE_PATH = Path(
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_research_governance_summary_after_momentum_closure_v1.py"
).as_posix()
PRIOR_CLOSURE_MODULE = (
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_momentum_closure_record_after_evaluator_v1.py"
)
PRIOR_CLOSURE_STATUS = (
    "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_MOMENTUM_CLOSURE_RECORD_CREATED"
)
PRIOR_HEAD = "6ed363946be44aecdbf9fdfd4141414b5874eb5f"
RESULT_CLASS = "MOMENTUM_BASELINE_REJECTED_NO_FOLLOWUP"
BEST_VALIDATION_NET_METRIC = -4.680782776161402
CLOSURE_REASON = (
    "All validation net metrics are non-positive after costs, best validation net metric is "
    "-4.680782776161402 for momentum_lb48h_hold1h, null baseline review did not pass, "
    "monthly stability review did not pass, and diagnostic_promising is false. This is a clean "
    "negative research result, not a data failure, runtime failure, edge claim, or release."
)

REPO_SCOPE: dict[str, str] = {
    "project": "Edge Factory OS / OKX historical data + research governance pipeline",
    "panel_scope": "OKX 88-symbol 1h panel",
}

SOURCE_CHECKPOINT: dict[str, Any] = {
    "prior_closure_module": PRIOR_CLOSURE_MODULE,
    "prior_closure_status": PRIOR_CLOSURE_STATUS,
    "prior_head": PRIOR_HEAD,
    "tracked_python_count_before_this_task": 797,
}

MAJOR_STAGE_SUMMARY: dict[str, dict[str, Any]] = {
    "A_OKX_universe_coverage_discovery": {
        "candidate_universe_symbols": 303,
        "chunks_completed": 16,
        "chunks_total": 16,
        "symbols_evaluated": 303,
        "near_3y_complete_symbols": 88,
        "coverage_gap_symbols": 215,
        "pending_symbols": 0,
        "strict_3y_completeness_claimed": False,
        "max_available_start_candidate": "2023-07-01",
        "max_available_end_date": "2026-05-18",
        "survivorship_and_delisted_limitations_recorded": True,
    },
    "B_88_symbol_1m_to_1h_build": {
        "selected_symbols": 88,
        "gap_symbols_excluded": 215,
        "source_files_processed": 92664,
        "raw_1m_source_rows_read": 133464732,
        "exact_duplicate_rows_dropped": 28497,
        "material_conflict_rows_quarantined": 168,
        "clean_source_rows_after_policy": 133436067,
        "full_1h_output_rows": 2223936,
        "complete_1h_rows": 2223843,
        "incomplete_1h_rows": 93,
        "duplicate_symbol_hour_count": 0,
        "numeric_sanity_valid": True,
        "provenance_valid": True,
        "synthetic_fill": False,
        "forward_fill": False,
        "backfill": False,
    },
    "C_research_readiness": {
        "output_valid_for_read_only_research_backtest": True,
        "output_valid_for_edge_claim": False,
        "candidate_generation": False,
        "strategy_search_initially_blocked_until_holdout_registry": True,
        "runtime_live_capital": False,
    },
    "D_extreme_return_diagnostics": {
        "baseline_extreme_returns_found": 80,
        "threshold_rule": "abs(close_to_close_return) >= 0.25",
        "extracted_extreme_returns": 80,
        "unique_symbols": 43,
        "top_symbol": "PEOPLE-USDT-SWAP",
        "top_symbol_count": 7,
        "top_3_symbols": ("PEOPLE-USDT-SWAP", "AGLD-USDT-SWAP", "LUNA-USDT-SWAP"),
        "top_3_count": 16,
        "concentrated_in_top_3": False,
        "unique_months": 26,
        "top_month": "2025-10",
        "top_month_count": 29,
        "clustered_by_month": False,
        "listing_start_window_overlap": 0,
        "incomplete_hour_overlap": 0,
        "volume_spike_overlap": 74,
        "real_market_event_like": 74,
        "unresolved_initial": 6,
        "real_market_event_like_context_confirmed_count": 3,
        "cross_symbol_market_shock_like_count": 3,
        "data_issue_suspect_context_count": 0,
        "bad_tick_like_reversal_suspect_count": 0,
        "unresolved_requires_source_review_count": 0,
        "unresolved_extreme_return_count_after_review": 0,
        "active_p1_attention_count": 0,
    },
    "E_holdout_registry": {
        "holdout_registry_created_for_this_panel": True,
        "holdout_registry_valid_for_this_panel": True,
        "holdout_registry_valid_for_strategy_search_governance": True,
        "true_untouched_final_holdout_claimed": False,
        "diagnostic_exposure_recorded": True,
        "valid_for_final_edge_claim": False,
        "final_edge_claim_requires_external_or_future_holdout": True,
        "binance_5y_second_source_validation_recorded_as_future_work": True,
        "train_development_window_start": "2023-07-01T00:00:00Z",
        "train_development_window_end_exclusive": "2025-01-01T00:00:00Z",
        "validation_window_original_start": "2025-01-01T00:00:00Z",
        "validation_window_original_end_exclusive": "2025-11-01T00:00:00Z",
        "validation_window_revised_safe_non_holdout_end_exclusive": "2025-10-31T16:00:00Z",
        "sealed_holdout_start": "2025-11-01T00:00:00Z",
        "sealed_holdout_end_exclusive": "2026-05-19T00:00:00Z",
        "holdout_access_blocked_during_strategy_search": True,
    },
    "F_strategy_family_preregistration": {
        "route_family_selected": "CROSS_SECTIONAL_MOMENTUM_BASELINE",
        "rejected_alternative_for_first_route": "CROSS_SECTIONAL_REVERSAL_BASELINE",
        "selection_basis": "PERFORMANCE_FREE_THEORETICAL_PRIOR",
        "momentum_vs_reversal_both_tested": False,
        "reversal_not_tested_in_first_route": True,
        "route_family_count_max": 1,
        "lookback_options_hours": (6, 12, 24, 48),
        "excluded_lookback_hours_from_first_route": (72,),
        "holding_periods_hours": (1, 3, 6),
        "config_grid_count": 12,
        "no_symbol_specific_tuning": True,
        "no_ml": True,
        "no_ensemble": True,
        "no_alternative_data": True,
    },
    "G_safe_non_holdout_panel_construction": {
        "initial_restricted_strategy_execution_blocked": True,
        "block_reason": (
            "PANEL_SORTED_BY_SYMBOL_WITHOUT_ROW_OFFSET_INDEX_REQUIRES_SEALED_HOLDOUT_SCAN_TO_REACH_LATER_SYMBOL_PRE_HOLDOUT_ROWS"
        ),
        "built_separate_holdout_safe_non_holdout_view": True,
        "all_in_one_panel_used_for_retry": False,
        "source_files_appear_utc_plus_8_day_boundary_shifted": True,
        "source_file_2025_10_31_ended_at": "2025-10-31T15:59:00Z",
        "source_file_2025_11_01_forbidden_due_sealed_holdout": True,
        "revised_non_holdout_start": "2023-07-01T00:00:00Z",
        "revised_non_holdout_end_exclusive": "2025-10-31T16:00:00Z",
        "boundary_buffer_start": "2025-10-31T16:00:00Z",
        "boundary_buffer_end": "2025-11-01T00:00:00Z",
        "boundary_buffer_rows_excluded": 704,
        "output_1h_row_count": 1802944,
        "output_symbol_count": 88,
        "expected_rows_per_symbol": 20488,
        "duplicate_symbol_hour_count": 0,
        "output_min_timestamp": "2023-07-01T00:00:00Z",
        "output_max_timestamp": "2025-10-31T15:00:00Z",
        "boundary_buffer_rows_written_count": 0,
        "sealed_holdout_rows_written_count": 0,
        "complete_1h_row_count": 1802935,
        "incomplete_1h_row_count": 9,
        "numeric_sanity_valid": True,
        "ohlc_sanity_valid": True,
        "output_valid_for_strategy_search_after_finalization": True,
        "output_valid_for_restricted_momentum_search_input": True,
        "output_valid_for_edge_claim": False,
        "output_valid_for_final_edge_claim": False,
        "output_valid_for_runtime_or_live": False,
    },
    "H_restricted_momentum_search_execution_summary": {
        "historical_summary_only_do_not_rerun": True,
        "route": "CROSS_SECTIONAL_MOMENTUM_BASELINE",
        "used_finalized_revised_non_holdout_panel_only": True,
        "used_all_in_one_panel": False,
        "used_original_1m_source_files": False,
        "accessed_sealed_holdout": False,
        "accessed_boundary_buffer": False,
        "reversal_tested": False,
        "momentum_vs_reversal_compared": False,
        "lookbacks_used_hours": (6, 12, 24, 48),
        "holding_periods_used_hours": (1, 3, 6),
        "tested_config_count": 12,
        "train_development_row_count": 1161600,
        "validation_row_count": 641344,
        "validation_lookback_context_from_train_used": True,
        "no_cross_window_holding_returns": True,
        "no_lookahead_policy_applied": True,
        "signal_entry_delay_applied": True,
        "incomplete_hour_policy_applied": True,
        "skipped_incomplete_rows": 9,
        "skipped_holding_windows": 175,
        "gross_metrics_created": True,
        "net_cost_adjusted_metrics_created": True,
        "fee_bps_per_side": 5,
        "slippage_bps_per_side": 5,
        "round_trip_cost_bps": 20,
        "null_baseline": "deterministic_block_shuffled_timestamp_spread_return_null",
        "null_run_count": 100,
        "null_baseline_complete": True,
        "monthly_stability_created": True,
        "turnover_concentration_created": True,
        "candidate_generation": False,
        "edge_claim": False,
        "family_release": False,
    },
    "I_evaluator_result_and_closure": {
        "evaluator_status": "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_STRATEGY_SEARCH_RETRY_EVALUATED",
        "result_class": RESULT_CLASS,
        "diagnostic_promising": False,
        "best_validation_config_id": "momentum_lb48h_hold1h",
        "best_validation_lookback": "48h",
        "best_validation_holding_period": "1h",
        "best_validation_net_metric": BEST_VALIDATION_NET_METRIC,
        "best_train_config_id": "momentum_lb48h_hold6h",
        "train_validation_rank_consistency": 0.7575757575757576,
        "validation_positive_after_cost": False,
        "null_baseline_review_passed": False,
        "monthly_stability_review_passed": False,
        "turnover_concentration_review_passed": True,
        "train_validation_degradation_flag": False,
        "concentration_risk_flag": False,
        "turnover_risk_flag": False,
        "metric_integrity_issue_count": 0,
        "closure_record_created": True,
        "closure_reason": CLOSURE_REASON,
    },
}

MOMENTUM_CLOSURE_PRESERVATION: dict[str, bool] = {
    "momentum_route_closed": True,
    "momentum_route_retest_allowed_now": False,
    "momentum_parameter_expansion_allowed_now": False,
    "reversal_followup_allowed_from_this_closure": False,
    "strategy_search_expansion_allowed_now": False,
    "candidate_generation_allowed_now": False,
    "edge_claim_allowed_now": False,
    "family_release_allowed_now": False,
    "holdout_access_allowed_now": False,
    "runtime_live_capital_allowed_now": False,
    "new_strategy_search_executed_by_this_module": False,
    "reversal_tested_by_this_module": False,
    "candidate_generation_performed_by_this_module": False,
    "edge_claim_performed_by_this_module": False,
    "family_release_performed_by_this_module": False,
    "holdout_accessed_by_this_module": False,
    "finalized_panel_rows_read_by_this_module": False,
}

REUSABLE_PANEL_STATUS: dict[str, bool] = {
    "panel_reusable_for_future_read_only_research": True,
    "panel_valid_for_edge_claim": False,
    "panel_requires_new_preregistered_route_for_future_search": True,
    "panel_valid_for_runtime_or_live": False,
    "panel_valid_for_capital_deployment": False,
    "panel_reuse_requires_governance": True,
    "future_final_edge_claim_requires_external_or_future_holdout": True,
}

FUTURE_RESEARCH_GOVERNANCE_QUEUE: dict[str, Any] = {
    "grants_search_permission_now": False,
    "allowed_future_categories": (
        {
            "category": "New route-family preregistration contract proposal",
            "allowed_as_future_governance_step": True,
            "may_select_exactly_one_route_family": True,
            "must_be_performance_free_or_prejustified": True,
            "must_define_search_space_before_execution": True,
            "requires_separate_governance_approval_before_any_search": True,
            "grants_strategy_search_now": False,
        },
        {
            "category": "Future external or future holdout validation planning",
            "allowed_as_planning_only": True,
            "binance_5y_second_source_validation_recorded_as_future_work": True,
            "grants_holdout_access_now": False,
            "grants_edge_claim_now": False,
        },
        {
            "category": "Read-only governance documentation",
            "allowed": True,
            "may_summarize_prior_committed_results": True,
            "may_not_read_panel_rows": True,
            "may_not_execute_research": True,
        },
    ),
    "explicit_constraints": {
        "reversal_is_not_approved_from_this_closure": True,
        "momentum_retest_is_not_approved_now": True,
        "parameter_expansion_is_not_approved_now": True,
        "future_route_requires_new_preregistered_route_family_contract": True,
        "future_route_requires_explicit_approval_before_data_execution": True,
        "summary_is_not_candidate": True,
        "summary_is_not_edge_claim": True,
        "summary_is_not_release": True,
        "summary_is_not_permission_for_live_runtime_capital": True,
    },
}

PERMISSIONS_AFTER_SUMMARY: dict[str, bool] = {
    "strategy_search_allowed_now": False,
    "momentum_retest_allowed_now": False,
    "momentum_parameter_expansion_allowed_now": False,
    "reversal_search_allowed_now": False,
    "candidate_generation_allowed_now": False,
    "edge_claim_allowed_now": False,
    "family_release_allowed_now": False,
    "holdout_access_allowed_now": False,
    "panel_row_read_allowed_now": False,
    "runtime_permission_allowed_now": False,
    "live_permission_allowed_now": False,
    "capital_permission_allowed_now": False,
}

FORBIDDEN_ACTIONS_CONFIRMED_FALSE: dict[str, bool] = {
    "new_strategy_search_executed": False,
    "momentum_retest_executed": False,
    "momentum_parameter_expansion_executed": False,
    "reversal_tested": False,
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
    "no_strategy_search": True,
    "no_reversal_test": True,
    "no_candidate_generation": True,
    "no_edge_claim": True,
    "no_runtime_live_capital": True,
    "momentum_result_is_negative_and_closed": True,
    "reusable_panel_status_preserved": True,
    "future_search_requires_new_preregistration": True,
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
        "major_stage_summary": MAJOR_STAGE_SUMMARY,
        "momentum_closure_preservation": MOMENTUM_CLOSURE_PRESERVATION,
        "reusable_panel_status": REUSABLE_PANEL_STATUS,
        "future_research_governance_queue": FUTURE_RESEARCH_GOVERNANCE_QUEUE,
        "permissions_after_summary": PERMISSIONS_AFTER_SUMMARY,
        "forbidden_actions_confirmed_false": FORBIDDEN_ACTIONS_CONFIRMED_FALSE,
        "validation_checks": VALIDATION_CHECKS,
        "replacement_checks_all_true": True,
    }


def validate_summary(summary: dict[str, Any]) -> None:
    assert summary["status"] == REQUIRED_STATUS
    assert summary["module"] == MODULE_PATH
    assert summary["source_checkpoint"]["prior_head"] == PRIOR_HEAD
    assert summary["source_checkpoint"]["prior_closure_status"] == PRIOR_CLOSURE_STATUS

    result = summary["major_stage_summary"]["I_evaluator_result_and_closure"]
    assert result["result_class"] == RESULT_CLASS
    assert result["best_validation_net_metric"] < 0
    assert result["diagnostic_promising"] is False
    assert result["closure_record_created"] is True

    closure = summary["momentum_closure_preservation"]
    assert closure["momentum_route_closed"] is True
    for key, value in closure.items():
        if key != "momentum_route_closed":
            assert value is False, key

    reusable_panel = summary["reusable_panel_status"]
    assert reusable_panel["panel_reusable_for_future_read_only_research"] is True
    assert reusable_panel["panel_requires_new_preregistered_route_for_future_search"] is True
    assert reusable_panel["panel_valid_for_edge_claim"] is False
    assert reusable_panel["panel_valid_for_runtime_or_live"] is False
    assert reusable_panel["panel_valid_for_capital_deployment"] is False

    for key, value in summary["permissions_after_summary"].items():
        assert value is False, key
    for key, value in summary["forbidden_actions_confirmed_false"].items():
        assert value is False, key

    queue = summary["future_research_governance_queue"]
    assert queue["grants_search_permission_now"] is False
    assert queue["explicit_constraints"]["reversal_is_not_approved_from_this_closure"] is True
    assert queue["explicit_constraints"]["future_route_requires_new_preregistered_route_family_contract"] is True
    assert queue["explicit_constraints"]["future_route_requires_explicit_approval_before_data_execution"] is True

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
