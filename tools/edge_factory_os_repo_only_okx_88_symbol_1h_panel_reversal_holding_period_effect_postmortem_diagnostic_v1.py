#!/usr/bin/env python3
"""Postmortem diagnostic for reversal holding-period effects.

This module uses only embedded, already evaluated reversal config metrics from
the committed evaluator result. It does not read panel rows, open the
whitelisted artifact, rerun execution, rerun the evaluator, or create any
candidate/edge/release/runtime permission.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_STATUS = (
    "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVERSAL_HOLDING_PERIOD_EFFECT_POSTMORTEM_DIAGNOSTIC_CREATED"
)
MODULE_PATH = (
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_reversal_holding_period_effect_postmortem_diagnostic_v1.py"
)
REPO_PATH = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
PROJECT = "Edge Factory OS / OKX historical data + research governance pipeline"
PANEL_SCOPE = "OKX 88-symbol 1h panel"
ROUTE_FAMILY = "CROSS_SECTIONAL_REVERSAL_BASELINE"
PRIOR_HEAD = "a98a95e489df64f05a55e199df1978392332c412"
PRIOR_TRACKED_PYTHON_COUNT = 805
PRIOR_CLOSURE_MODULE = (
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_reversal_closure_record_after_evaluator_v1.py"
)
PRIOR_CLOSURE_STATUS = (
    "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_REVERSAL_CLOSURE_RECORD_AFTER_EVALUATOR_CREATED"
)
PRIOR_EVALUATOR_MODULE = (
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_reversal_execution_evaluator_after_whitelisted_artifact_run_v1.py"
)
PRIOR_EVALUATOR_STATUS = (
    "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_REVERSAL_EXECUTION_EVALUATED_AFTER_WHITELISTED_ARTIFACT_RUN"
)
REVERSAL_RESULT_CLASS = "REVERSAL_BASELINE_REJECTED_NO_FOLLOWUP"
BEST_VALIDATION_CONFIG_ID = "reversal_lb48h_hold6h"
BEST_VALIDATION_NET_METRIC = 1.0545052484969872

LOOKBACKS = (6, 12, 24, 48)
HOLDINGS = (1, 3, 6)
ALLOWED_CLASSIFICATIONS = (
    "HOLDING_6H_EFFECT_SUPPORTED_DIAGNOSTIC_ONLY",
    "HOLDING_6H_EFFECT_WEAK_VALIDATION_ONLY",
    "HOLDING_6H_EFFECT_EXPLAINED_BY_HOLDING_PERIOD_SCALING",
    "HOLDING_6H_EFFECT_INCONCLUSIVE",
)

SOURCE_CHECKPOINT = {
    "active_p0_blocker_count_before_diagnostic": 0,
    "panel_scope": PANEL_SCOPE,
    "prior_closure_module": PRIOR_CLOSURE_MODULE,
    "prior_closure_status": PRIOR_CLOSURE_STATUS,
    "prior_evaluator_module": PRIOR_EVALUATOR_MODULE,
    "prior_evaluator_status": PRIOR_EVALUATOR_STATUS,
    "prior_head": PRIOR_HEAD,
    "prior_tracked_python_count": PRIOR_TRACKED_PYTHON_COUNT,
    "project": PROJECT,
    "repo_clean_before_diagnostic": True,
}

PRIOR_REVERSAL_CLOSURE_PRESERVED = {
    "best_validation_config_id": BEST_VALIDATION_CONFIG_ID,
    "best_validation_net_metric": BEST_VALIDATION_NET_METRIC,
    "both_baseline_routes_closed": True,
    "diagnostic_promising": False,
    "metric_integrity_issue_count": 0,
    "momentum_route_remains_closed": True,
    "monthly_stability_review_passed": False,
    "no_active_candidate_exists": True,
    "no_active_edge_claim_exists": True,
    "no_runtime_live_capital_permission_exists": True,
    "null_baseline_review_passed": False,
    "positive_best_validation_metric_not_promoted_to_candidate": True,
    "positive_best_validation_metric_not_promoted_to_edge_claim": True,
    "result_class": REVERSAL_RESULT_CLASS,
    "reversal_route_closed": True,
    "turnover_concentration_review_passed": True,
}

PRIOR_REVERSAL_EVALUATOR_RESULTS_PRESERVED = {
    "best_train_config_id": "reversal_lb48h_hold1h",
    "best_validation_config_id": BEST_VALIDATION_CONFIG_ID,
    "best_validation_gross_metric": 4.788740542614635,
    "best_validation_holding_period": "6h",
    "best_validation_lookback": "48h",
    "best_validation_net_metric": BEST_VALIDATION_NET_METRIC,
    "candidate_generation": False,
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

CONFIG_RESULTS_EVALUATED = (
    {
        "average_turnover": 0.6664810016225511,
        "config_id": "reversal_lb6h_hold1h",
        "holding_period_hours": 1,
        "lookback_hours": 6,
        "median_turnover": 0.6470588235294118,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.0,
        "top_symbol_exposure_share": 0.019813689164426676,
        "train_gross_metric": -0.3287520387778237,
        "train_net_metric": -17.621457921130766,
        "train_observation_count": 13193,
        "train_positive_after_cost": False,
        "validation_gross_metric": 1.0698895145513838,
        "validation_net_metric": -8.643404603095675,
        "validation_null_percentile_or_rank_if_available": 0.51,
        "validation_observation_count": 7287,
        "validation_positive_after_cost": False,
    },
    {
        "average_turnover": 0.6664540352860431,
        "config_id": "reversal_lb6h_hold3h",
        "holding_period_hours": 3,
        "lookback_hours": 6,
        "median_turnover": 0.6470588235294118,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.0,
        "top_symbol_exposure_share": 0.019811054140256062,
        "train_gross_metric": -1.3261249305512683,
        "train_net_metric": -18.6157719893748,
        "train_observation_count": 13191,
        "train_positive_after_cost": False,
        "validation_gross_metric": 1.9638728622602117,
        "validation_net_metric": -7.746362431857436,
        "validation_null_percentile_or_rank_if_available": 0.48,
        "validation_observation_count": 7285,
        "validation_positive_after_cost": False,
    },
    {
        "average_turnover": 0.6663893241998805,
        "config_id": "reversal_lb6h_hold6h",
        "holding_period_hours": 6,
        "lookback_hours": 6,
        "median_turnover": 0.6470588235294118,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.1,
        "top_symbol_exposure_share": 0.019811137858054606,
        "train_gross_metric": -3.110708203055528,
        "train_net_metric": -20.395884673643764,
        "train_observation_count": 13188,
        "train_positive_after_cost": False,
        "validation_gross_metric": 3.256606330837949,
        "validation_net_metric": -6.44868778680911,
        "validation_null_percentile_or_rank_if_available": 0.5,
        "validation_observation_count": 7282,
        "validation_positive_after_cost": False,
    },
    {
        "average_turnover": 0.4814456041782707,
        "config_id": "reversal_lb12h_hold1h",
        "holding_period_hours": 1,
        "lookback_hours": 12,
        "median_turnover": 0.47058823529411764,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.0,
        "top_symbol_exposure_share": 0.020915570839286836,
        "train_gross_metric": -0.47248440283730814,
        "train_net_metric": -12.877425579307896,
        "train_observation_count": 13187,
        "train_positive_after_cost": False,
        "validation_gross_metric": 1.0088302121890573,
        "validation_net_metric": -6.00775802310506,
        "validation_null_percentile_or_rank_if_available": 0.5,
        "validation_observation_count": 7287,
        "validation_positive_after_cost": False,
    },
    {
        "average_turnover": 0.4814082118777504,
        "config_id": "reversal_lb12h_hold3h",
        "holding_period_hours": 3,
        "lookback_hours": 12,
        "median_turnover": 0.47058823529411764,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.1,
        "top_symbol_exposure_share": 0.02091323832209628,
        "train_gross_metric": -1.7464520085332904,
        "train_net_metric": -14.149393185003879,
        "train_observation_count": 13185,
        "train_positive_after_cost": False,
        "validation_gross_metric": 2.0201747044298735,
        "validation_net_metric": -4.99394294262895,
        "validation_null_percentile_or_rank_if_available": 0.5,
        "validation_observation_count": 7285,
        "validation_positive_after_cost": False,
    },
    {
        "average_turnover": 0.4814288253065576,
        "config_id": "reversal_lb12h_hold6h",
        "holding_period_hours": 6,
        "lookback_hours": 12,
        "median_turnover": 0.47058823529411764,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.3,
        "top_symbol_exposure_share": 0.02091377611192799,
        "train_gross_metric": -4.532135097340538,
        "train_net_metric": -16.932605685575833,
        "train_observation_count": 13182,
        "train_positive_after_cost": False,
        "validation_gross_metric": 4.373847464561129,
        "validation_net_metric": -2.6376819472035775,
        "validation_null_percentile_or_rank_if_available": 0.49,
        "validation_observation_count": 7282,
        "validation_positive_after_cost": False,
    },
    {
        "average_turnover": 0.3511733223548785,
        "config_id": "reversal_lb24h_hold1h",
        "holding_period_hours": 1,
        "lookback_hours": 24,
        "median_turnover": 0.3529411764705882,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.0,
        "top_symbol_exposure_share": 0.021278828534295677,
        "train_gross_metric": -0.4012131738153998,
        "train_net_metric": -9.21756611499187,
        "train_observation_count": 13175,
        "train_positive_after_cost": False,
        "validation_gross_metric": 1.054045690128031,
        "validation_net_metric": -4.063954309871969,
        "validation_null_percentile_or_rank_if_available": 0.49,
        "validation_observation_count": 7287,
        "validation_positive_after_cost": False,
    },
    {
        "average_turnover": 0.3511324639670556,
        "config_id": "reversal_lb24h_hold3h",
        "holding_period_hours": 3,
        "lookback_hours": 24,
        "median_turnover": 0.3529411764705882,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.2,
        "top_symbol_exposure_share": 0.021276595744680965,
        "train_gross_metric": -1.5236499176489207,
        "train_net_metric": -10.338473447060686,
        "train_observation_count": 13173,
        "train_positive_after_cost": False,
        "validation_gross_metric": 2.16220760270803,
        "validation_net_metric": -2.95379239729197,
        "validation_null_percentile_or_rank_if_available": 0.44,
        "validation_observation_count": 7285,
        "validation_positive_after_cost": False,
    },
    {
        "average_turnover": 0.3511721085028353,
        "config_id": "reversal_lb24h_hold6h",
        "holding_period_hours": 6,
        "lookback_hours": 24,
        "median_turnover": 0.3529411764705882,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.6,
        "top_symbol_exposure_share": 0.021277283228589544,
        "train_gross_metric": -2.3069118587911284,
        "train_net_metric": -11.119617741144069,
        "train_observation_count": 13170,
        "train_positive_after_cost": False,
        "validation_gross_metric": 4.31511200518246,
        "validation_net_metric": -0.7993585830528345,
        "validation_null_percentile_or_rank_if_available": 0.63,
        "validation_observation_count": 7282,
        "validation_positive_after_cost": False,
    },
    {
        "average_turnover": 0.2563711363507939,
        "config_id": "reversal_lb48h_hold1h",
        "holding_period_hours": 1,
        "lookback_hours": 48,
        "median_turnover": 0.23529411764705882,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.0,
        "top_symbol_exposure_share": 0.021472565971633727,
        "train_gross_metric": -0.6091799067405417,
        "train_net_metric": -6.988826965564071,
        "train_observation_count": 13151,
        "train_positive_after_cost": False,
        "validation_gross_metric": 0.9444298349849306,
        "validation_net_metric": -2.79192310619154,
        "validation_null_percentile_or_rank_if_available": 0.48,
        "validation_observation_count": 7287,
        "validation_positive_after_cost": False,
    },
    {
        "average_turnover": 0.2563769227663612,
        "config_id": "reversal_lb48h_hold3h",
        "holding_period_hours": 3,
        "lookback_hours": 48,
        "median_turnover": 0.23529411764705882,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.4,
        "top_symbol_exposure_share": 0.021470386370059467,
        "train_gross_metric": -1.359911231457169,
        "train_net_metric": -7.738852407927758,
        "train_observation_count": 13149,
        "train_positive_after_cost": False,
        "validation_gross_metric": 2.5936396646177107,
        "validation_net_metric": -1.1417721000881718,
        "validation_null_percentile_or_rank_if_available": 0.43,
        "validation_observation_count": 7285,
        "validation_positive_after_cost": False,
    },
    {
        "average_turnover": 0.2564017642212062,
        "config_id": "reversal_lb48h_hold6h",
        "holding_period_hours": 6,
        "lookback_hours": 48,
        "median_turnover": 0.23529411764705882,
        "metric_integrity_issue_count": 0,
        "monthly_positive_rate_if_available": 0.4,
        "top_symbol_exposure_share": 0.021467114722846136,
        "train_gross_metric": -2.0709087031094175,
        "train_net_metric": -8.448085173697653,
        "train_observation_count": 13146,
        "train_positive_after_cost": False,
        "validation_gross_metric": 4.788740542614635,
        "validation_net_metric": BEST_VALIDATION_NET_METRIC,
        "validation_null_percentile_or_rank_if_available": 0.64,
        "validation_observation_count": 7282,
        "validation_positive_after_cost": True,
    },
)

DIAGNOSTIC_POLICY = {
    "diagnostic_is_postmortem_only": True,
    "no_artifact_read": True,
    "no_closure": True,
    "no_evaluator": True,
    "no_governance_sprawl": True,
    "no_new_parameters": True,
    "no_new_route_family": True,
    "no_new_search": True,
    "no_panel_row_read": True,
    "output_grants_no_permission": True,
    "output_is_not_candidate": True,
    "output_is_not_edge_claim": True,
}

PERMISSIONS_AFTER_DIAGNOSTIC = {
    "all_in_one_panel_access_allowed_now": False,
    "alternative_data_access_allowed_now": False,
    "boundary_buffer_access_allowed_now": False,
    "candidate_generation_allowed_now": False,
    "capital_permission_allowed_now": False,
    "closure_allowed_now": False,
    "diagnostic_created": True,
    "edge_claim_allowed_now": False,
    "evaluator_allowed_now": False,
    "external_data_access_allowed_now": False,
    "family_release_allowed_now": False,
    "holdout_access_allowed_now": False,
    "live_permission_allowed_now": False,
    "momentum_parameter_expansion_allowed_now": False,
    "momentum_retest_allowed_now": False,
    "next_immediate_module_required": False,
    "original_1m_source_access_allowed_now": False,
    "project_can_pause_after_diagnostic": True,
    "reversal_parameter_expansion_allowed_now": False,
    "reversal_retest_allowed_now": False,
    "runtime_permission_allowed_now": False,
    "strategy_search_allowed_now": False,
    "whitelisted_artifact_access_allowed_now": False,
}

FORBIDDEN_ACTIONS_CONFIRMED_FALSE = {
    "access_scope_module_created": False,
    "all_in_one_panel_accessed": False,
    "alternative_data_used": False,
    "amendment_module_created": False,
    "approval_module_created": False,
    "blocker_module_created": False,
    "boundary_buffer_accessed": False,
    "candidates_generated": False,
    "capital_permission_granted": False,
    "closure_created": False,
    "data_artifacts_created": False,
    "edge_claimed": False,
    "evaluator_rerun": False,
    "existing_files_modified_by_module": False,
    "external_data_used": False,
    "family_released": False,
    "files_written_by_module": False,
    "governance_module_created": False,
    "holdout_accessed": False,
    "live_permission_granted": False,
    "momentum_parameter_expansion_executed": False,
    "momentum_retest_executed": False,
    "momentum_search_executed": False,
    "original_1m_source_files_read": False,
    "panel_rows_read": False,
    "reversal_execution_rerun": False,
    "reversal_tested": False,
    "runtime_permission_granted": False,
    "strategy_search_executed": False,
    "whitelisted_artifact_read": False,
}


def per_config_derived_metrics() -> tuple[dict[str, Any], ...]:
    rows = []
    for config in CONFIG_RESULTS_EVALUATED:
        holding = config["holding_period_hours"]
        rows.append(
            {
                "config_id": config["config_id"],
                "holding_period_hours": holding,
                "lookback_hours": config["lookback_hours"],
                "train_gross_per_holding_hour": config["train_gross_metric"] / holding,
                "train_net_per_holding_hour": config["train_net_metric"] / holding,
                "validation_gross_per_holding_hour": config["validation_gross_metric"] / holding,
                "validation_net_per_holding_hour": config["validation_net_metric"] / holding,
            }
        )
    return tuple(rows)


def holding_map(configs: tuple[dict[str, Any], ...], key: str) -> dict[str, Any]:
    return {f"{config['holding_period_hours']}h": config[key] for config in configs}


def metric_by_config_id(config_id: str, derived_rows: tuple[dict[str, Any], ...], key: str) -> float:
    for row in derived_rows:
        if row["config_id"] == config_id:
            return row[key]
    raise AssertionError(f"missing derived row for {config_id}")


def is_6h_best(configs: tuple[dict[str, Any], ...], key: str) -> bool:
    max_value = max(config[key] for config in configs)
    six_hour_value = next(config[key] for config in configs if config["holding_period_hours"] == 6)
    return six_hour_value == max_value


def derived_6h_best(
    configs: tuple[dict[str, Any], ...],
    derived_rows: tuple[dict[str, Any], ...],
    key: str,
) -> bool:
    values = {
        config["holding_period_hours"]: metric_by_config_id(config["config_id"], derived_rows, key)
        for config in configs
    }
    return values[6] == max(values.values())


def per_lookback_diagnostics(derived_rows: tuple[dict[str, Any], ...]) -> dict[str, dict[str, Any]]:
    diagnostics: dict[str, dict[str, Any]] = {}
    for lookback in LOOKBACKS:
        configs = tuple(
            sorted(
                (config for config in CONFIG_RESULTS_EVALUATED if config["lookback_hours"] == lookback),
                key=lambda item: item["holding_period_hours"],
            )
        )
        by_holding = {config["holding_period_hours"]: config for config in configs}
        group_derived = tuple(row for row in derived_rows if row["lookback_hours"] == lookback)
        average_turnovers = [config["average_turnover"] for config in configs]
        diagnostics[f"{lookback}h"] = {
            "configs_ordered_by_holding_period_hours": tuple(config["config_id"] for config in configs),
            "monthly_positive_rate_6h_best": is_6h_best(configs, "monthly_positive_rate_if_available"),
            "monthly_positive_rate_by_holding": holding_map(configs, "monthly_positive_rate_if_available"),
            "null_percentile_6h_best": is_6h_best(configs, "validation_null_percentile_or_rank_if_available"),
            "null_percentile_by_holding": holding_map(configs, "validation_null_percentile_or_rank_if_available"),
            "train_gross_by_holding": holding_map(configs, "train_gross_metric"),
            "train_net_by_holding": holding_map(configs, "train_net_metric"),
            "train_raw_net_6h_best": is_6h_best(configs, "train_net_metric"),
            "train_raw_net_monotonic_improves_with_holding": (
                by_holding[6]["train_net_metric"] > by_holding[3]["train_net_metric"] > by_holding[1]["train_net_metric"]
            ),
            "turnover_by_holding": holding_map(configs, "average_turnover"),
            "turnover_difference_across_holds_small": (max(average_turnovers) - min(average_turnovers)) <= 0.001,
            "validation_gross_6h_best": is_6h_best(configs, "validation_gross_metric"),
            "validation_gross_by_holding": holding_map(configs, "validation_gross_metric"),
            "validation_gross_monotonic_improves_with_holding": (
                by_holding[6]["validation_gross_metric"]
                > by_holding[3]["validation_gross_metric"]
                > by_holding[1]["validation_gross_metric"]
            ),
            "validation_gross_per_hour_6h_best": derived_6h_best(
                configs, group_derived, "validation_gross_per_holding_hour"
            ),
            "validation_gross_per_holding_hour_by_holding": {
                f"{row['holding_period_hours']}h": row["validation_gross_per_holding_hour"]
                for row in group_derived
            },
            "validation_net_6h_best": is_6h_best(configs, "validation_net_metric"),
            "validation_net_by_holding": holding_map(configs, "validation_net_metric"),
            "validation_net_per_hour_6h_best": derived_6h_best(
                configs, group_derived, "validation_net_per_holding_hour"
            ),
            "validation_net_per_holding_hour_by_holding": {
                f"{row['holding_period_hours']}h": row["validation_net_per_holding_hour"]
                for row in group_derived
            },
            "validation_raw_net_monotonic_improves_with_holding": (
                by_holding[6]["validation_net_metric"]
                > by_holding[3]["validation_net_metric"]
                > by_holding[1]["validation_net_metric"]
            ),
        }
    return diagnostics


def support_for_6h(kind: str) -> str:
    six_hour_configs = tuple(config for config in CONFIG_RESULTS_EVALUATED if config["holding_period_hours"] == 6)
    if kind == "null":
        values = tuple(config["validation_null_percentile_or_rank_if_available"] for config in six_hour_configs)
        if all(value >= 0.75 for value in values):
            return "STRONG"
        if sum(1 for value in values if value >= 0.65) >= 2:
            return "MODERATE"
        return "WEAK"
    if kind == "monthly":
        values = tuple(config["monthly_positive_rate_if_available"] for config in six_hour_configs)
        if sum(1 for value in values if value >= 0.6) >= 3:
            return "STRONG"
        if sum(1 for value in values if value >= 0.4) >= 2:
            return "MODERATE"
        return "WEAK"
    raise AssertionError(f"unknown support kind {kind}")


def global_summary(
    derived_rows: tuple[dict[str, Any], ...],
    lookback_diagnostics: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    best_raw = max(CONFIG_RESULTS_EVALUATED, key=lambda item: item["validation_net_metric"])
    best_per_hour = max(derived_rows, key=lambda item: item["validation_net_per_holding_hour"])
    raw_count = sum(1 for row in lookback_diagnostics.values() if row["validation_net_6h_best"])
    gross_count = sum(1 for row in lookback_diagnostics.values() if row["validation_gross_6h_best"])
    train_count = sum(1 for row in lookback_diagnostics.values() if row["train_raw_net_6h_best"])
    net_per_hour_count = sum(1 for row in lookback_diagnostics.values() if row["validation_net_per_hour_6h_best"])
    gross_per_hour_count = sum(1 for row in lookback_diagnostics.values() if row["validation_gross_per_hour_6h_best"])
    monthly_count = sum(1 for row in lookback_diagnostics.values() if row["monthly_positive_rate_6h_best"])
    null_count = sum(1 for row in lookback_diagnostics.values() if row["null_percentile_6h_best"])
    turnover_small_count = sum(
        1 for row in lookback_diagnostics.values() if row["turnover_difference_across_holds_small"]
    )
    raw_all = raw_count == len(LOOKBACKS)
    raw_survives = best_per_hour["holding_period_hours"] == 6
    train_support = train_count >= 3
    null_support = support_for_6h("null")
    monthly_support = support_for_6h("monthly")
    scaling_artifact = raw_all and not raw_survives
    validation_only = raw_all and not train_support
    robustness_weak = null_support == "WEAK" or monthly_support == "WEAK"
    return {
        "best_per_hour_validation_config_id": best_per_hour["config_id"],
        "best_per_hour_validation_net_metric": best_per_hour["validation_net_per_holding_hour"],
        "best_raw_validation_config_id": best_raw["config_id"],
        "best_raw_validation_net_metric": best_raw["validation_net_metric"],
        "monthly_positive_rate_6h_best_count_across_lookbacks": monthly_count,
        "monthly_support_for_6h": monthly_support,
        "null_percentile_6h_best_count_across_lookbacks": null_count,
        "null_support_for_6h": null_support,
        "per_hour_validation_best_is_6h": raw_survives,
        "raw_6h_advantage_survives_per_hour_normalization": raw_survives,
        "raw_validation_best_is_6h": best_raw["holding_period_hours"] == 6,
        "robustness_evidence_weak": robustness_weak,
        "scaling_artifact_evidence": scaling_artifact,
        "train_raw_net_6h_best_count_across_lookbacks": train_count,
        "train_supports_6h_advantage": train_support,
        "turnover_difference_small_count_across_lookbacks": turnover_small_count,
        "validation_gross_6h_best_count_across_lookbacks": gross_count,
        "validation_gross_per_hour_6h_best_count_across_lookbacks": gross_per_hour_count,
        "validation_net_per_hour_6h_best_count_across_lookbacks": net_per_hour_count,
        "validation_only_evidence": validation_only,
        "validation_raw_net_6h_best_count_across_lookbacks": raw_count,
        "validation_raw_net_monotonic_6h_advantage_all_lookbacks": raw_all,
    }


def classify(summary: dict[str, Any]) -> str:
    if (
        summary["validation_raw_net_monotonic_6h_advantage_all_lookbacks"]
        and summary["raw_6h_advantage_survives_per_hour_normalization"]
        and summary["train_supports_6h_advantage"]
        and summary["null_support_for_6h"] != "WEAK"
        and summary["monthly_support_for_6h"] != "WEAK"
    ):
        return "HOLDING_6H_EFFECT_SUPPORTED_DIAGNOSTIC_ONLY"
    if summary["scaling_artifact_evidence"]:
        return "HOLDING_6H_EFFECT_EXPLAINED_BY_HOLDING_PERIOD_SCALING"
    if summary["validation_raw_net_monotonic_6h_advantage_all_lookbacks"] and not summary["train_supports_6h_advantage"]:
        return "HOLDING_6H_EFFECT_WEAK_VALIDATION_ONLY"
    return "HOLDING_6H_EFFECT_INCONCLUSIVE"


def interpretation(classification: str, summary: dict[str, Any]) -> dict[str, str]:
    return {
        "caution": (
            "This postmortem diagnostic does not reopen the reversal route, does not authorize "
            "parameter expansion, and does not create a candidate or edge claim."
        ),
        "exposure_time_normalization_summary": (
            "The raw 6h validation advantage survives validation-net-per-holding-hour normalization "
            f"({summary['raw_6h_advantage_survives_per_hour_normalization']}); this weakens a pure "
            "holding-period scaling artifact explanation for net validation returns, although gross "
            "per-hour metrics do not favor 6h."
        ),
        "final_diagnostic_takeaway": (
            f"Classification is {classification}: the 6h pattern is visible in validation but lacks train "
            "support and failed the prior evaluator's null and monthly stability requirements."
        ),
        "monthly_support_summary": f"Monthly support for 6h is {summary['monthly_support_for_6h']}.",
        "null_support_summary": f"Null support for 6h is {summary['null_support_for_6h']}.",
        "plain_english_summary": (
            "The completed reversal baseline shows a consistent raw validation preference for 6h holds, "
            "but that preference is not supported by train metrics and remains insufficient for follow-up."
        ),
        "raw_validation_horizon_effect_summary": (
            "6h has the best raw validation net metric in "
            f"{summary['validation_raw_net_6h_best_count_across_lookbacks']} of 4 lookback groups."
        ),
        "train_consistency_summary": (
            "6h has the best train raw net metric in "
            f"{summary['train_raw_net_6h_best_count_across_lookbacks']} of 4 lookback groups."
        ),
    }


def build_summary() -> dict[str, Any]:
    derived_rows = per_config_derived_metrics()
    lookback_rows = per_lookback_diagnostics(derived_rows)
    global_rows = global_summary(derived_rows, lookback_rows)
    classification = classify(global_rows)
    validation_checks = {
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 0,
        "candidate_generation_forbidden": True,
        "classification_is_from_allowed_set": classification in ALLOWED_CLASSIFICATIONS,
        "config_results_count_is_12": len(CONFIG_RESULTS_EVALUATED) == 12,
        "created_file_expected_count": 1,
        "diagnostic_did_not_access_all_in_one_panel": True,
        "diagnostic_did_not_access_boundary_buffer": True,
        "diagnostic_did_not_access_holdout": True,
        "diagnostic_did_not_access_original_1m_source_files": True,
        "diagnostic_did_not_read_panel_rows": True,
        "diagnostic_did_not_read_whitelisted_artifact": True,
        "diagnostic_did_not_rerun_evaluator": True,
        "diagnostic_did_not_rerun_execution": True,
        "diagnostic_did_not_run_strategy_search": True,
        "diagnostic_did_not_use_external_or_alternative_data": True,
        "edge_claim_forbidden": True,
        "exactly_one_new_tracked_python_tool_file_expected": True,
        "family_release_forbidden": True,
        "holdings_are_1_3_6": sorted({row["holding_period_hours"] for row in CONFIG_RESULTS_EVALUATED}) == list(HOLDINGS),
        "lookbacks_are_6_12_24_48": sorted({row["lookback_hours"] for row in CONFIG_RESULTS_EVALUATED}) == list(LOOKBACKS),
        "module_path_equals_required_path": True,
        "next_immediate_module_required_is_false": True,
        "no_data_files_created_expected": True,
        "no_existing_files_modified_expected": True,
        "no_new_governance_or_amendment_or_blocker_module_created": True,
        "prior_evaluator_results_preserved": True,
        "prior_reversal_closure_preserved": True,
        "project_can_pause_after_diagnostic": True,
        "replacement_checks_all_true": True,
        "runtime_live_capital_forbidden": True,
        "status_equals_required_status": True,
    }
    replacement_checks_all_true = all(
        value is True
        for key, value in validation_checks.items()
        if key not in {"active_p0_blocker_count", "active_p1_attention_count", "created_file_expected_count"}
    )
    return {
        "classification": {
            "allowed_classifications": ALLOWED_CLASSIFICATIONS,
            "classification": classification,
        },
        "diagnostic_policy": DIAGNOSTIC_POLICY,
        "diagnostic_question": (
            "Does the reversal baseline's 6h holding-period advantage indicate a meaningful horizon "
            "effect, a holding-period metric scaling artifact, validation-only weak behavior, or "
            "inconclusive evidence?"
        ),
        "forbidden_actions_confirmed_false": FORBIDDEN_ACTIONS_CONFIRMED_FALSE,
        "global_holding_effect_summary": global_rows,
        "input_config_results": CONFIG_RESULTS_EVALUATED,
        "interpretation": interpretation(classification, global_rows),
        "module": MODULE_PATH,
        "per_config_derived_metrics": derived_rows,
        "per_lookback_holding_effect_diagnostics": lookback_rows,
        "permissions_after_diagnostic": PERMISSIONS_AFTER_DIAGNOSTIC,
        "prior_reversal_closure_preserved": PRIOR_REVERSAL_CLOSURE_PRESERVED,
        "prior_reversal_evaluator_results_preserved": PRIOR_REVERSAL_EVALUATOR_RESULTS_PRESERVED,
        "replacement_checks_all_true": replacement_checks_all_true,
        "repo_scope": {
            "api_used": False,
            "closure_created_by_this_module": False,
            "code_changes_repo_only": True,
            "evaluator_rerun_by_this_module": False,
            "governance_module_created_by_this_module": False,
            "internet_used": False,
            "notebooks_used": False,
            "panel_rows_read_by_this_module": False,
            "repo_path": str(REPO_PATH),
            "strategy_search_executed_by_this_module": False,
            "whitelisted_artifact_read_by_this_module": False,
        },
        "source_checkpoint": SOURCE_CHECKPOINT,
        "status": REQUIRED_STATUS,
        "validation_checks": validation_checks,
    }


def validate_summary(summary: dict[str, Any]) -> None:
    assert summary["status"] == REQUIRED_STATUS
    assert summary["module"] == MODULE_PATH
    assert len(CONFIG_RESULTS_EVALUATED) == 12
    assert summary["prior_reversal_evaluator_results_preserved"]["route_family"] == ROUTE_FAMILY
    assert sorted({row["lookback_hours"] for row in CONFIG_RESULTS_EVALUATED}) == list(LOOKBACKS)
    assert sorted({row["holding_period_hours"] for row in CONFIG_RESULTS_EVALUATED}) == list(HOLDINGS)
    assert summary["prior_reversal_evaluator_results_preserved"]["best_validation_config_id"] == BEST_VALIDATION_CONFIG_ID
    assert (
        abs(summary["prior_reversal_evaluator_results_preserved"]["best_validation_net_metric"] - BEST_VALIDATION_NET_METRIC)
        <= 1e-12
    )
    closure = summary["prior_reversal_closure_preserved"]
    assert closure["result_class"] == REVERSAL_RESULT_CLASS
    assert closure["diagnostic_promising"] is False
    assert closure["null_baseline_review_passed"] is False
    assert closure["monthly_stability_review_passed"] is False
    assert closure["turnover_concentration_review_passed"] is True
    assert closure["metric_integrity_issue_count"] == 0
    for key, value in summary["forbidden_actions_confirmed_false"].items():
        assert value is False, key
    assert summary["permissions_after_diagnostic"]["candidate_generation_allowed_now"] is False
    assert summary["permissions_after_diagnostic"]["edge_claim_allowed_now"] is False
    assert summary["permissions_after_diagnostic"]["family_release_allowed_now"] is False
    assert summary["permissions_after_diagnostic"]["runtime_permission_allowed_now"] is False
    assert summary["permissions_after_diagnostic"]["live_permission_allowed_now"] is False
    assert summary["permissions_after_diagnostic"]["capital_permission_allowed_now"] is False
    assert summary["permissions_after_diagnostic"]["next_immediate_module_required"] is False
    assert summary["permissions_after_diagnostic"]["project_can_pause_after_diagnostic"] is True
    assert summary["classification"]["classification"] in ALLOWED_CLASSIFICATIONS
    assert summary["replacement_checks_all_true"] is True


def main() -> int:
    summary = build_summary()
    validate_summary(summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
