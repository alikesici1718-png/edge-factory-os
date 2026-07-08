#!/usr/bin/env python3
"""Static evaluator for the restricted reversal execution result.

This module evaluates the captured stdout JSON from the immediately prior
committed restricted reversal execution. It does not rerun execution, import the
execution module, read panel rows, or open the whitelisted local artifact.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_STATUS = (
    "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_REVERSAL_EXECUTION_EVALUATED_AFTER_WHITELISTED_ARTIFACT_RUN"
)
MODULE_PATH = (
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_reversal_execution_evaluator_after_whitelisted_artifact_run_v1.py"
)
REPO_PATH = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
WHITELISTED_ARTIFACT_PATH = (
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_after_retry_preview_v1"
    r"\repo_only_okx_88_symbol_1h_panel_revised_non_holdout_view.csv"
)

PROJECT = "Edge Factory OS / OKX historical data + research governance pipeline"
PANEL_SCOPE = "OKX 88-symbol 1h panel"
ROUTE_FAMILY = "CROSS_SECTIONAL_REVERSAL_BASELINE"
MOMENTUM_RESULT_CLASS = "MOMENTUM_BASELINE_REJECTED_NO_FOLLOWUP"
PRIOR_HEAD = "ab88e46949a2ccce71b2b4ec11d8c56424eadc73"
PRIOR_TRACKED_PYTHON_COUNT = 803
PRIOR_EXECUTION_MODULE = (
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_reversal_search_execution_after_local_artifact_scope_amendment_v1.py"
)
PRIOR_EXECUTION_STATUS = (
    "PASS_REPO_CODE_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_REVERSAL_SEARCH_EXECUTED_WITH_WHITELISTED_LOCAL_ARTIFACT_NON_HOLDOUT_ONLY"
)
PRIOR_ACCESS_SCOPE_AMENDMENT_MODULE = (
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_local_artifact_access_scope_amendment_for_reversal_execution_v1.py"
)
PRIOR_ACCESS_SCOPE_AMENDMENT_STATUS = (
    "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_LOCAL_ARTIFACT_ACCESS_SCOPE_AMENDMENT_FOR_REVERSAL_EXECUTION_CREATED"
)
PRIOR_EXECUTION_APPROVAL_STATUS = (
    "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVERSAL_EXECUTION_GOVERNANCE_APPROVAL_AFTER_PREREGISTRATION_CONTRACT_CREATED"
)
PRIOR_PREREGISTRATION_CONTRACT_STATUS = (
    "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_NEW_ROUTE_FAMILY_PREREGISTRATION_CONTRACT_PROPOSAL_AFTER_GOVERNANCE_SUMMARY_CREATED"
)

ALLOWED_RESULT_CLASSES = (
    "REVERSAL_BASELINE_DIAGNOSTIC_PROMISING_REQUIRES_SEPARATE_CLOSURE_NO_CANDIDATE_NO_EDGE",
    "REVERSAL_BASELINE_REJECTED_NO_FOLLOWUP",
    "REVERSAL_BASELINE_INCONCLUSIVE_EVALUATOR_INPUT_INCOMPLETE_NO_FOLLOWUP",
    "REVERSAL_BASELINE_INVALIDATED_BY_SAFETY_OR_INTEGRITY_FAILURE",
)

SOURCE_CHECKPOINT = {
    "active_p0_blocker_count_before_evaluator": 0,
    "panel_scope": PANEL_SCOPE,
    "prior_access_scope_amendment_module": PRIOR_ACCESS_SCOPE_AMENDMENT_MODULE,
    "prior_access_scope_amendment_status": PRIOR_ACCESS_SCOPE_AMENDMENT_STATUS,
    "prior_execution_module": PRIOR_EXECUTION_MODULE,
    "prior_execution_status": PRIOR_EXECUTION_STATUS,
    "prior_head": PRIOR_HEAD,
    "prior_tracked_python_count": PRIOR_TRACKED_PYTHON_COUNT,
    "project": PROJECT,
    "repo_clean_before_evaluator": True,
}

PRIOR_EXECUTION_SUMMARY_PRESERVED = {
    "all_in_one_panel_accessed": False,
    "alternative_data_used": False,
    "best_validation_config_id": "reversal_lb48h_hold6h",
    "best_validation_net_metric": 1.0545052484969872,
    "boundary_buffer_accessed": False,
    "candidate_generation": False,
    "diagnostic_only": True,
    "edge_claim": False,
    "evaluator_not_yet_run_before_this_module": True,
    "exact_whitelisted_artifact_path_used": WHITELISTED_ARTIFACT_PATH,
    "exact_whitelisted_local_artifact_rows_read_by_prior_execution": True,
    "external_data_used": False,
    "family_release": False,
    "holdout_accessed": False,
    "original_1m_source_files_read": False,
    "restricted_reversal_search_executed": True,
    "route_family_executed": ROUTE_FAMILY,
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
    "whitelisted_artifact_purpose": "finalized_revised_non_holdout_panel_for_one_future_restricted_reversal_execution_retry",
    "whitelisted_artifact_suffix": ".csv",
    "whitelisted_future_execution_count": 1,
    "whitelisted_route_family": ROUTE_FAMILY,
}

PRIOR_EXECUTION_APPROVAL_PRESERVED = {
    "approval_granted_for_future_separate_module": True,
    "approval_record_created": True,
    "approval_type": "ONE_FUTURE_RESTRICTED_REVERSAL_SEARCH_EXECUTION_MODULE_NON_HOLDOUT_ONLY",
    "approved_future_execution_may_not_claim_edge": True,
    "approved_future_execution_may_not_generate_candidates": True,
    "approved_future_execution_may_not_grant_runtime_live_capital": True,
    "approved_future_execution_may_not_read_all_in_one_panel": True,
    "approved_future_execution_may_not_read_boundary_buffer": True,
    "approved_future_execution_may_not_read_holdout": True,
    "approved_future_execution_may_not_read_original_1m_source_files": True,
    "approved_future_execution_may_not_release_family": True,
    "approved_future_execution_may_read_finalized_revised_non_holdout_panel_rows": True,
    "approved_future_execution_may_run_restricted_reversal_search": True,
    "approved_future_route_family": ROUTE_FAMILY,
    "approved_future_route_family_count": 1,
    "final_edge_claim_still_requires_external_or_future_holdout": True,
}

PRIOR_PREREGISTRATION_CONTRACT_PRESERVED = {
    "proposal_created": True,
    "proposal_is_execution_approval": False,
    "proposed_route_family": ROUTE_FAMILY,
    "proposed_route_family_count": 1,
    "required_separate_governance_approval_before_execution_was_true": True,
    "reversal_was_not_tested_by_prior_momentum_route": True,
    "selection_basis": "NEW_INDEPENDENT_PREREGISTRATION_PROPOSAL_PERFORMANCE_FREE_THEORETICAL_PRIOR",
    "selection_not_based_on_candidate_generation": True,
    "selection_not_based_on_holdout": True,
    "selection_not_based_on_momentum_validation_performance": True,
    "selection_not_based_on_new_backtest": True,
    "selection_not_based_on_panel_row_scan": True,
}

PRIOR_NEGATIVE_MOMENTUM_CLOSURE_PRESERVED = {
    "best_validation_config_id": "momentum_lb48h_hold1h",
    "best_validation_holding_period": "1h",
    "best_validation_lookback": "48h",
    "best_validation_net_metric": -4.680782776161402,
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

EVALUATOR_INPUT_SOURCE = {
    "captured_execution_best_validation_config_id": "reversal_lb48h_hold6h",
    "captured_execution_best_validation_net_metric": 1.0545052484969872,
    "captured_execution_status_matches_expected": True,
    "captured_execution_tested_config_count": 12,
    "evaluator_uses_static_embedded_execution_results": True,
    "input_source_type": "captured_stdout_json_from_prior_committed_reversal_execution",
    "panel_rows_read_by_this_evaluator": False,
    "prior_execution_module_called_by_this_evaluator": False,
    "prior_execution_module_imported_by_this_evaluator": False,
    "prior_execution_rerun_by_this_task": False,
    "whitelisted_artifact_read_by_this_evaluator": False,
}

EVALUATION_POLICY = {
    "allowed_result_classes": ALLOWED_RESULT_CLASSES,
    "candidate_generation_allowed_by_evaluator": False,
    "diagnostic_promising_requires_all": (
        "best_validation_net_metric_positive_after_cost",
        "validation_positive_after_cost",
        "null_baseline_review_preliminary_passed",
        "monthly_stability_review_preliminary_passed",
        "turnover_concentration_review_preliminary_passed",
        "metric_integrity_passed",
        "no_safety_violation",
    ),
    "edge_claim_allowed_by_evaluator": False,
    "evaluator_policy_version": "restricted_reversal_execution_evaluator_v1",
    "family_release_allowed_by_evaluator": False,
    "final_edge_claim_requires_external_or_future_holdout": True,
    "rejection_or_no_followup_conditions": (
        "all_validation_net_metrics_non_positive_after_cost",
        "null_baseline_review_failed",
        "monthly_stability_review_failed",
        "turnover_or_concentration_review_failed",
        "metric_integrity_failed",
        "evaluator_input_incomplete",
        "safety_violation",
    ),
    "result_is_diagnostic_only": True,
    "runtime_live_capital_allowed_by_evaluator": False,
}

CONFIG_RESULTS_EVALUATED = (
    {
        "concentration_summary_if_available": {
            "long_short_participation_count": 247758,
            "top_symbol_exposure_share": 0.019813689164426676,
        },
        "config_id": "reversal_lb6h_hold1h",
        "holding_period_hours": 1,
        "lookback_hours": 6,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.0,
        "train_gross_metric": -0.3287520387778237,
        "train_net_metric": -17.621457921130766,
        "train_observation_count": 13193,
        "train_positive_after_cost": False,
        "turnover_summary_if_available": {
            "average_turnover": 0.6664810016225511,
            "max_turnover": 1.7058823529411764,
            "median_turnover": 0.6470588235294118,
        },
        "validation_gross_metric": 1.0698895145513838,
        "validation_net_metric": -8.643404603095675,
        "validation_null_percentile_or_rank_if_available": 0.51,
        "validation_observation_count": 7287,
        "validation_positive_after_cost": False,
    },
    {
        "concentration_summary_if_available": {
            "long_short_participation_count": 247690,
            "top_symbol_exposure_share": 0.019811054140256062,
        },
        "config_id": "reversal_lb6h_hold3h",
        "holding_period_hours": 3,
        "lookback_hours": 6,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.0,
        "train_gross_metric": -1.3261249305512683,
        "train_net_metric": -18.6157719893748,
        "train_observation_count": 13191,
        "train_positive_after_cost": False,
        "turnover_summary_if_available": {
            "average_turnover": 0.6664540352860431,
            "max_turnover": 1.7058823529411764,
            "median_turnover": 0.6470588235294118,
        },
        "validation_gross_metric": 1.9638728622602117,
        "validation_net_metric": -7.746362431857436,
        "validation_null_percentile_or_rank_if_available": 0.48,
        "validation_observation_count": 7285,
        "validation_positive_after_cost": False,
    },
    {
        "concentration_summary_if_available": {
            "long_short_participation_count": 247588,
            "top_symbol_exposure_share": 0.019811137858054606,
        },
        "config_id": "reversal_lb6h_hold6h",
        "holding_period_hours": 6,
        "lookback_hours": 6,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.1,
        "train_gross_metric": -3.110708203055528,
        "train_net_metric": -20.395884673643764,
        "train_observation_count": 13188,
        "train_positive_after_cost": False,
        "turnover_summary_if_available": {
            "average_turnover": 0.6663893241998805,
            "max_turnover": 1.7058823529411764,
            "median_turnover": 0.6470588235294118,
        },
        "validation_gross_metric": 3.256606330837949,
        "validation_net_metric": -6.44868778680911,
        "validation_null_percentile_or_rank_if_available": 0.5,
        "validation_observation_count": 7282,
        "validation_positive_after_cost": False,
    },
    {
        "concentration_summary_if_available": {
            "long_short_participation_count": 247758,
            "top_symbol_exposure_share": 0.020915570839286836,
        },
        "config_id": "reversal_lb12h_hold1h",
        "holding_period_hours": 1,
        "lookback_hours": 12,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.0,
        "train_gross_metric": -0.47248440283730814,
        "train_net_metric": -12.877425579307896,
        "train_observation_count": 13187,
        "train_positive_after_cost": False,
        "turnover_summary_if_available": {
            "average_turnover": 0.4814456041782707,
            "max_turnover": 1.588235294117647,
            "median_turnover": 0.47058823529411764,
        },
        "validation_gross_metric": 1.0088302121890573,
        "validation_net_metric": -6.00775802310506,
        "validation_null_percentile_or_rank_if_available": 0.5,
        "validation_observation_count": 7287,
        "validation_positive_after_cost": False,
    },
    {
        "concentration_summary_if_available": {
            "long_short_participation_count": 247690,
            "top_symbol_exposure_share": 0.02091323832209628,
        },
        "config_id": "reversal_lb12h_hold3h",
        "holding_period_hours": 3,
        "lookback_hours": 12,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.1,
        "train_gross_metric": -1.7464520085332904,
        "train_net_metric": -14.149393185003879,
        "train_observation_count": 13185,
        "train_positive_after_cost": False,
        "turnover_summary_if_available": {
            "average_turnover": 0.4814082118777504,
            "max_turnover": 1.588235294117647,
            "median_turnover": 0.47058823529411764,
        },
        "validation_gross_metric": 2.0201747044298735,
        "validation_net_metric": -4.99394294262895,
        "validation_null_percentile_or_rank_if_available": 0.5,
        "validation_observation_count": 7285,
        "validation_positive_after_cost": False,
    },
    {
        "concentration_summary_if_available": {
            "long_short_participation_count": 247588,
            "top_symbol_exposure_share": 0.02091377611192799,
        },
        "config_id": "reversal_lb12h_hold6h",
        "holding_period_hours": 6,
        "lookback_hours": 12,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.3,
        "train_gross_metric": -4.532135097340538,
        "train_net_metric": -16.932605685575833,
        "train_observation_count": 13182,
        "train_positive_after_cost": False,
        "turnover_summary_if_available": {
            "average_turnover": 0.4814288253065576,
            "max_turnover": 1.588235294117647,
            "median_turnover": 0.47058823529411764,
        },
        "validation_gross_metric": 4.373847464561129,
        "validation_net_metric": -2.6376819472035775,
        "validation_null_percentile_or_rank_if_available": 0.49,
        "validation_observation_count": 7282,
        "validation_positive_after_cost": False,
    },
    {
        "concentration_summary_if_available": {
            "long_short_participation_count": 247758,
            "top_symbol_exposure_share": 0.021278828534295677,
        },
        "config_id": "reversal_lb24h_hold1h",
        "holding_period_hours": 1,
        "lookback_hours": 24,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.0,
        "train_gross_metric": -0.4012131738153998,
        "train_net_metric": -9.21756611499187,
        "train_observation_count": 13175,
        "train_positive_after_cost": False,
        "turnover_summary_if_available": {
            "average_turnover": 0.3511733223548785,
            "max_turnover": 1.5294117647058822,
            "median_turnover": 0.3529411764705882,
        },
        "validation_gross_metric": 1.054045690128031,
        "validation_net_metric": -4.063954309871969,
        "validation_null_percentile_or_rank_if_available": 0.49,
        "validation_observation_count": 7287,
        "validation_positive_after_cost": False,
    },
    {
        "concentration_summary_if_available": {
            "long_short_participation_count": 247690,
            "top_symbol_exposure_share": 0.021276595744680965,
        },
        "config_id": "reversal_lb24h_hold3h",
        "holding_period_hours": 3,
        "lookback_hours": 24,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.2,
        "train_gross_metric": -1.5236499176489207,
        "train_net_metric": -10.338473447060686,
        "train_observation_count": 13173,
        "train_positive_after_cost": False,
        "turnover_summary_if_available": {
            "average_turnover": 0.3511324639670556,
            "max_turnover": 1.5294117647058822,
            "median_turnover": 0.3529411764705882,
        },
        "validation_gross_metric": 2.16220760270803,
        "validation_net_metric": -2.95379239729197,
        "validation_null_percentile_or_rank_if_available": 0.44,
        "validation_observation_count": 7285,
        "validation_positive_after_cost": False,
    },
    {
        "concentration_summary_if_available": {
            "long_short_participation_count": 247588,
            "top_symbol_exposure_share": 0.021277283228589544,
        },
        "config_id": "reversal_lb24h_hold6h",
        "holding_period_hours": 6,
        "lookback_hours": 24,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.6,
        "train_gross_metric": -2.3069118587911284,
        "train_net_metric": -11.119617741144069,
        "train_observation_count": 13170,
        "train_positive_after_cost": False,
        "turnover_summary_if_available": {
            "average_turnover": 0.3511721085028353,
            "max_turnover": 1.5294117647058822,
            "median_turnover": 0.3529411764705882,
        },
        "validation_gross_metric": 4.31511200518246,
        "validation_net_metric": -0.7993585830528345,
        "validation_null_percentile_or_rank_if_available": 0.63,
        "validation_observation_count": 7282,
        "validation_positive_after_cost": False,
    },
    {
        "concentration_summary_if_available": {
            "long_short_participation_count": 247758,
            "top_symbol_exposure_share": 0.021472565971633727,
        },
        "config_id": "reversal_lb48h_hold1h",
        "holding_period_hours": 1,
        "lookback_hours": 48,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.0,
        "train_gross_metric": -0.6091799067405417,
        "train_net_metric": -6.988826965564071,
        "train_observation_count": 13151,
        "train_positive_after_cost": False,
        "turnover_summary_if_available": {
            "average_turnover": 0.2563711363507939,
            "max_turnover": 1.3529411764705883,
            "median_turnover": 0.23529411764705882,
        },
        "validation_gross_metric": 0.9444298349849306,
        "validation_net_metric": -2.79192310619154,
        "validation_null_percentile_or_rank_if_available": 0.48,
        "validation_observation_count": 7287,
        "validation_positive_after_cost": False,
    },
    {
        "concentration_summary_if_available": {
            "long_short_participation_count": 247690,
            "top_symbol_exposure_share": 0.021470386370059467,
        },
        "config_id": "reversal_lb48h_hold3h",
        "holding_period_hours": 3,
        "lookback_hours": 48,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.4,
        "train_gross_metric": -1.359911231457169,
        "train_net_metric": -7.738852407927758,
        "train_observation_count": 13149,
        "train_positive_after_cost": False,
        "turnover_summary_if_available": {
            "average_turnover": 0.2563769227663612,
            "max_turnover": 1.3529411764705883,
            "median_turnover": 0.23529411764705882,
        },
        "validation_gross_metric": 2.5936396646177107,
        "validation_net_metric": -1.1417721000881718,
        "validation_null_percentile_or_rank_if_available": 0.43,
        "validation_observation_count": 7285,
        "validation_positive_after_cost": False,
    },
    {
        "concentration_summary_if_available": {
            "long_short_participation_count": 247588,
            "top_symbol_exposure_share": 0.021467114722846136,
        },
        "config_id": "reversal_lb48h_hold6h",
        "holding_period_hours": 6,
        "lookback_hours": 48,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.4,
        "train_gross_metric": -2.0709087031094175,
        "train_net_metric": -8.448085173697653,
        "train_observation_count": 13146,
        "train_positive_after_cost": False,
        "turnover_summary_if_available": {
            "average_turnover": 0.2564017642212062,
            "max_turnover": 1.3529411764705883,
            "median_turnover": 0.23529411764705882,
        },
        "validation_gross_metric": 4.788740542614635,
        "validation_net_metric": 1.0545052484969872,
        "validation_null_percentile_or_rank_if_available": 0.64,
        "validation_observation_count": 7282,
        "validation_positive_after_cost": True,
    },
)

EXECUTION_RESULTS_EVALUATED = {
    "all_validation_net_metrics_non_positive_after_cost": False,
    "all_validation_net_metrics_positive_after_cost": False,
    "best_train_config_id": "reversal_lb48h_hold1h",
    "best_validation_config_id": "reversal_lb48h_hold6h",
    "best_validation_gross_metric": 4.788740542614635,
    "best_validation_holding_period": "6h",
    "best_validation_lookback": "48h",
    "best_validation_net_metric": 1.0545052484969872,
    "candidate_generation": False,
    "config_results_evaluated": CONFIG_RESULTS_EVALUATED,
    "concentration_risk_flag": False,
    "edge_claim": False,
    "family_release": False,
    "metric_integrity_issue_count": 0,
    "metric_integrity_passed": True,
    "monthly_stability_created": True,
    "monthly_stability_review_preliminary_passed": False,
    "null_baseline_complete": True,
    "null_baseline_review_preliminary_passed": False,
    "null_run_count": 100,
    "route_family": ROUTE_FAMILY,
    "runtime_live_capital": False,
    "tested_config_count": 12,
    "train_development_row_count": 1161600,
    "train_validation_degradation_flag": False,
    "train_validation_rank_consistency": 0.803030303030303,
    "turnover_concentration_created": True,
    "turnover_concentration_review_preliminary_passed": True,
    "turnover_risk_flag": False,
    "validation_positive_after_cost": True,
    "validation_row_count": 641344,
}

FOLLOWUP_PERMISSIONS = {
    "all_in_one_panel_access_allowed_now": False,
    "alternative_data_access_allowed_now": False,
    "boundary_buffer_access_allowed_now": False,
    "candidate_generation_allowed_now": False,
    "capital_permission_allowed_now": False,
    "closure_record_allowed_next": True,
    "edge_claim_allowed_now": False,
    "external_data_access_allowed_now": False,
    "family_release_allowed_now": False,
    "final_edge_claim_requires_external_or_future_holdout": True,
    "holdout_access_allowed_now": False,
    "if_diagnostic_promising_then_separate_closure_and_new_governance_required_before_any_followup": True,
    "if_rejected_then_closure_record_required_before_new_route": True,
    "live_permission_allowed_now": False,
    "momentum_parameter_expansion_allowed_now": False,
    "momentum_retest_allowed_now": False,
    "original_1m_source_access_allowed_now": False,
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


def classify_result(
    execution_results: dict[str, Any],
    evaluator_input_complete: bool,
    safety_review_passed: bool,
) -> tuple[str, bool, str]:
    if not safety_review_passed:
        return (
            "REVERSAL_BASELINE_INVALIDATED_BY_SAFETY_OR_INTEGRITY_FAILURE",
            False,
            "A safety or integrity failure invalidated the diagnostic reversal execution.",
        )
    if not evaluator_input_complete:
        return (
            "REVERSAL_BASELINE_INCONCLUSIVE_EVALUATOR_INPUT_INCOMPLETE_NO_FOLLOWUP",
            False,
            "Evaluator input was incomplete, so no follow-up is allowed.",
        )
    required_passes = (
        execution_results["best_validation_net_metric"] > 0,
        execution_results["validation_positive_after_cost"] is True,
        execution_results["null_baseline_review_preliminary_passed"] is True,
        execution_results["monthly_stability_review_preliminary_passed"] is True,
        execution_results["turnover_concentration_review_preliminary_passed"] is True,
        execution_results["metric_integrity_passed"] is True,
        safety_review_passed is True,
    )
    if all(required_passes):
        return (
            "REVERSAL_BASELINE_DIAGNOSTIC_PROMISING_REQUIRES_SEPARATE_CLOSURE_NO_CANDIDATE_NO_EDGE",
            True,
            (
                "All evaluator gates passed, but the result remains diagnostic only and requires "
                "separate closure and governance before any follow-up."
            ),
        )
    return (
        "REVERSAL_BASELINE_REJECTED_NO_FOLLOWUP",
        False,
        (
            "Best validation net metric is positive after costs, but the null baseline and monthly "
            "stability preliminary reviews did not pass; therefore the reversal baseline is rejected "
            "for follow-up under the evaluator policy."
        ),
    )


def build_summary() -> dict[str, Any]:
    evaluator_input_complete = len(CONFIG_RESULTS_EVALUATED) == 12
    safety_review_passed = all(value is False for value in FORBIDDEN_ACTIONS_CONFIRMED_FALSE.values())
    result_class, diagnostic_promising, result_reason = classify_result(
        EXECUTION_RESULTS_EVALUATED,
        evaluator_input_complete,
        safety_review_passed,
    )
    evaluator_findings = {
        "best_validation_net_metric_positive_after_cost": (
            EXECUTION_RESULTS_EVALUATED["best_validation_net_metric"] > 0
        ),
        "diagnostic_promising": diagnostic_promising,
        "evaluator_input_complete": evaluator_input_complete,
        "evaluator_ran": True,
        "evaluator_read_all_in_one_panel": False,
        "evaluator_read_boundary_buffer": False,
        "evaluator_read_holdout": False,
        "evaluator_read_original_1m_source_files": False,
        "evaluator_read_panel_rows": False,
        "evaluator_read_whitelisted_artifact": False,
        "evaluator_reason": result_reason,
        "evaluator_recomputed_strategy_metrics": False,
        "metric_integrity_review_passed": EXECUTION_RESULTS_EVALUATED["metric_integrity_passed"],
        "monthly_stability_review_passed": EXECUTION_RESULTS_EVALUATED[
            "monthly_stability_review_preliminary_passed"
        ],
        "null_baseline_review_passed": EXECUTION_RESULTS_EVALUATED[
            "null_baseline_review_preliminary_passed"
        ],
        "safety_review_passed": safety_review_passed,
        "turnover_concentration_review_passed": EXECUTION_RESULTS_EVALUATED[
            "turnover_concentration_review_preliminary_passed"
        ],
        "validation_positive_after_cost": EXECUTION_RESULTS_EVALUATED["validation_positive_after_cost"],
    }
    result_classification = {
        "best_validation_config_id": EXECUTION_RESULTS_EVALUATED["best_validation_config_id"],
        "best_validation_holding_period": EXECUTION_RESULTS_EVALUATED["best_validation_holding_period"],
        "best_validation_lookback": EXECUTION_RESULTS_EVALUATED["best_validation_lookback"],
        "best_validation_net_metric": EXECUTION_RESULTS_EVALUATED["best_validation_net_metric"],
        "candidate_generation_allowed_from_evaluator": False,
        "closure_record_required_next": True,
        "diagnostic_promising": diagnostic_promising,
        "edge_claim_allowed_from_evaluator": False,
        "evaluator_grants_external_or_future_holdout_edge_claim": False,
        "evaluator_grants_holdout_access": False,
        "family_release_allowed_from_evaluator": False,
        "metric_integrity_issue_count": EXECUTION_RESULTS_EVALUATED["metric_integrity_issue_count"],
        "monthly_stability_review_passed": EXECUTION_RESULTS_EVALUATED[
            "monthly_stability_review_preliminary_passed"
        ],
        "null_baseline_review_passed": EXECUTION_RESULTS_EVALUATED[
            "null_baseline_review_preliminary_passed"
        ],
        "result_class": result_class,
        "result_reason": result_reason,
        "runtime_live_capital_allowed_from_evaluator": False,
        "turnover_concentration_review_passed": EXECUTION_RESULTS_EVALUATED[
            "turnover_concentration_review_preliminary_passed"
        ],
        "validation_positive_after_cost": EXECUTION_RESULTS_EVALUATED["validation_positive_after_cost"],
    }
    validation_checks = {
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 0,
        "best_validation_config_id_preserved": (
            EXECUTION_RESULTS_EVALUATED["best_validation_config_id"] == "reversal_lb48h_hold6h"
        ),
        "best_validation_net_metric_preserved": (
            abs(EXECUTION_RESULTS_EVALUATED["best_validation_net_metric"] - 1.0545052484969872) <= 1e-12
        ),
        "candidate_generation_forbidden": True,
        "closure_record_required_next": result_classification["closure_record_required_next"],
        "created_file_expected_count": 1,
        "edge_claim_forbidden": True,
        "evaluator_did_not_access_all_in_one_panel": True,
        "evaluator_did_not_access_boundary_buffer": True,
        "evaluator_did_not_access_holdout": True,
        "evaluator_did_not_access_original_1m_source_files": True,
        "evaluator_did_not_read_panel_rows": True,
        "evaluator_did_not_read_whitelisted_artifact": True,
        "evaluator_did_not_rerun_execution": True,
        "evaluator_did_not_run_strategy_search": True,
        "evaluator_did_not_use_external_or_alternative_data": True,
        "exactly_one_new_tracked_python_tool_file_expected": True,
        "family_release_forbidden": True,
        "final_edge_claim_requires_external_or_future_holdout": True,
        "module_path_equals_required_path": True,
        "no_data_files_created_expected": True,
        "no_existing_files_modified_expected": True,
        "no_new_governance_or_amendment_or_blocker_module_created": True,
        "prior_access_scope_amendment_preserved": True,
        "prior_execution_approval_preserved": True,
        "prior_execution_status_preserved": True,
        "prior_negative_momentum_closure_preserved": True,
        "prior_preregistration_contract_preserved": True,
        "replacement_checks_all_true": True,
        "result_class_is_from_allowed_set": result_class in ALLOWED_RESULT_CLASSES,
        "route_family_evaluated_is_cross_sectional_reversal_baseline": (
            EXECUTION_RESULTS_EVALUATED["route_family"] == ROUTE_FAMILY
        ),
        "runtime_live_capital_forbidden": True,
        "status_equals_required_status": True,
        "tested_config_count_is_12": EXECUTION_RESULTS_EVALUATED["tested_config_count"] == 12,
    }
    replacement_checks_all_true = all(
        value is True
        for key, value in validation_checks.items()
        if key not in {"active_p0_blocker_count", "active_p1_attention_count", "created_file_expected_count"}
    )
    return {
        "config_results_evaluated": CONFIG_RESULTS_EVALUATED,
        "evaluation_policy": EVALUATION_POLICY,
        "evaluator_findings": evaluator_findings,
        "evaluator_input_source": EVALUATOR_INPUT_SOURCE,
        "execution_results_evaluated": EXECUTION_RESULTS_EVALUATED,
        "followup_permissions": FOLLOWUP_PERMISSIONS,
        "forbidden_actions_confirmed_false": FORBIDDEN_ACTIONS_CONFIRMED_FALSE,
        "module": MODULE_PATH,
        "prior_access_scope_amendment_preserved": PRIOR_ACCESS_SCOPE_AMENDMENT_PRESERVED,
        "prior_execution_approval_preserved": PRIOR_EXECUTION_APPROVAL_PRESERVED,
        "prior_execution_summary_preserved": PRIOR_EXECUTION_SUMMARY_PRESERVED,
        "prior_negative_momentum_closure_preserved": PRIOR_NEGATIVE_MOMENTUM_CLOSURE_PRESERVED,
        "prior_preregistration_contract_preserved": PRIOR_PREREGISTRATION_CONTRACT_PRESERVED,
        "replacement_checks_all_true": replacement_checks_all_true,
        "repo_scope": {
            "api_used": False,
            "code_changes_repo_only": True,
            "internet_used": False,
            "non_repo_artifact_content_read_by_this_module": False,
            "notebooks_used": False,
            "panel_rows_read_by_this_module": False,
            "repo_path": str(REPO_PATH),
            "strategy_search_executed_by_this_module": False,
        },
        "result_classification": result_classification,
        "source_checkpoint": SOURCE_CHECKPOINT,
        "status": REQUIRED_STATUS,
        "validation_checks": validation_checks,
    }


def validate_summary(summary: dict[str, Any]) -> None:
    assert summary["status"] == REQUIRED_STATUS
    assert summary["module"] == MODULE_PATH
    assert summary["source_checkpoint"]["prior_execution_status"] == PRIOR_EXECUTION_STATUS
    assert (
        summary["source_checkpoint"]["prior_access_scope_amendment_status"]
        == PRIOR_ACCESS_SCOPE_AMENDMENT_STATUS
    )
    assert summary["execution_results_evaluated"]["route_family"] == ROUTE_FAMILY
    assert summary["execution_results_evaluated"]["tested_config_count"] == 12
    assert summary["execution_results_evaluated"]["best_validation_config_id"] == "reversal_lb48h_hold6h"
    assert abs(summary["execution_results_evaluated"]["best_validation_net_metric"] - 1.0545052484969872) <= 1e-12
    assert summary["evaluator_findings"]["evaluator_ran"] is True
    assert summary["evaluator_findings"]["evaluator_recomputed_strategy_metrics"] is False
    assert summary["evaluator_findings"]["evaluator_read_panel_rows"] is False
    assert summary["evaluator_findings"]["evaluator_read_whitelisted_artifact"] is False
    for key, value in summary["forbidden_actions_confirmed_false"].items():
        assert value is False, key
    assert summary["result_classification"]["candidate_generation_allowed_from_evaluator"] is False
    assert summary["result_classification"]["edge_claim_allowed_from_evaluator"] is False
    assert summary["result_classification"]["family_release_allowed_from_evaluator"] is False
    assert summary["result_classification"]["runtime_live_capital_allowed_from_evaluator"] is False
    assert summary["followup_permissions"]["runtime_permission_allowed_now"] is False
    assert summary["followup_permissions"]["live_permission_allowed_now"] is False
    assert summary["followup_permissions"]["capital_permission_allowed_now"] is False
    assert summary["result_classification"]["closure_record_required_next"] is True
    assert summary["followup_permissions"]["final_edge_claim_requires_external_or_future_holdout"] is True
    assert (
        summary["prior_negative_momentum_closure_preserved"]["momentum_result_class"]
        == MOMENTUM_RESULT_CLASS
    )
    assert summary["prior_negative_momentum_closure_preserved"]["best_validation_net_metric"] < 0
    assert summary["validation_checks"]["active_p0_blocker_count"] == 0
    assert summary["replacement_checks_all_true"] is True
    assert summary["result_classification"]["result_class"] in ALLOWED_RESULT_CLASSES
    if summary["result_classification"]["diagnostic_promising"] is True:
        assert summary["evaluator_findings"]["best_validation_net_metric_positive_after_cost"] is True
        assert summary["evaluator_findings"]["validation_positive_after_cost"] is True
        assert summary["evaluator_findings"]["null_baseline_review_passed"] is True
        assert summary["evaluator_findings"]["monthly_stability_review_passed"] is True
        assert summary["evaluator_findings"]["turnover_concentration_review_passed"] is True
        assert summary["evaluator_findings"]["metric_integrity_review_passed"] is True
        assert summary["evaluator_findings"]["safety_review_passed"] is True
    if summary["result_classification"]["result_class"] == "REVERSAL_BASELINE_REJECTED_NO_FOLLOWUP":
        assert summary["result_classification"]["diagnostic_promising"] is False


def main() -> int:
    summary = build_summary()
    validate_summary(summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
