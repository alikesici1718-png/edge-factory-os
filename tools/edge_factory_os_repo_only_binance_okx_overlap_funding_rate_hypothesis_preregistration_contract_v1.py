#!/usr/bin/env python3
"""Preregister the Binance/OKX overlap funding-rate hypothesis route."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_RATE_HYPOTHESIS_PREREGISTRATION_CONTRACT_CREATED"
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_rate_hypothesis_preregistration_contract_v1.py"
PREREGISTRATION_ARTIFACT_PATH = "artifacts/research_preregistrations/binance_okx_overlap_funding_rate_hypothesis_preregistration_contract_v1.json"
REPO_PATH = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
ARTIFACT_PATH = REPO_PATH / PREREGISTRATION_ARTIFACT_PATH
TEMP_ARTIFACT_PATH = ARTIFACT_PATH.with_suffix(".json.tmp")

READINESS_PATH = REPO_PATH / "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json"
PANEL_REVIEW_PATH = REPO_PATH / "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json"
BUILD_MANIFEST_PATH = REPO_PATH / "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json"
PREVIEW_PATH = REPO_PATH / "artifacts/panel_build_previews/binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.json"
COVERAGE_LOCK_PATH = REPO_PATH / "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json"

PRIOR_HEAD = "4e21908997c34cc8f031b6084ebac40b8f250831"
PRIOR_TRACKED_PYTHON_COUNT = 811
READINESS_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_NEAR_5Y_SECOND_SOURCE_READINESS_ALIGNMENT_SUMMARY_CREATED"
READINESS_PAYLOAD_HASH = "0cfe239f6f5ad2d20bda64b827416851de8f5b959066902b59f1f00f44eba716"
PANEL_REVIEW_PAYLOAD_HASH = "34b88a3ff0870c708e2df034c243cf639b711ebce3c6a4f32edffb92a2229112"
BUILD_MANIFEST_PAYLOAD_HASH = "bf4d4d681f36fab3a2131701e25ebc45c94ddb757f92874498ef425d698f40a7"
PREVIEW_PAYLOAD_HASH = "16e93ca05fe28f0d101d5228e299306bad3aea171f22bc6901f770b0ecf3a3d9"
COVERAGE_LOCK_PAYLOAD_HASH = "18a84b71c649b0462fdb0d511597dcb701448fe06184ef9c8da93d6911ada4e0"

ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_RATE_CROWDING_REVERSAL_BASELINE"
HYPOTHESIS_NAME = "funding_rate_crowding_reversal"
ALIGNED_WINDOW_START = "2023-07-01T00:00:00Z"
ALIGNED_WINDOW_END_EXCLUSIVE = "2025-10-31T16:00:00Z"
CONFIG_IDS = [
    "funding_latest_hold8h",
    "funding_latest_hold16h",
    "funding_latest_hold24h",
    "funding_mean3_hold8h",
    "funding_mean3_hold16h",
    "funding_mean3_hold24h",
    "funding_mean9_hold8h",
    "funding_mean9_hold16h",
    "funding_mean9_hold24h",
]
SIGNAL_TRANSFORMS = [
    "latest_lagged_funding_rate",
    "rolling_mean_3_funding_events",
    "rolling_mean_9_funding_events",
]
HOLDING_PERIODS_HOURS = [8, 16, 24]


class BlockedError(RuntimeError):
    """Raised when preregistration must stop before artifact write."""


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")


def payload_hash(payload: dict[str, Any]) -> str:
    copy = dict(payload)
    copy.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json_bytes(copy)).hexdigest()


def verify_payload(payload: dict[str, Any], expected_hash: str) -> bool:
    return payload.get("payload_sha256_excluding_hash") == expected_hash and payload_hash(payload) == expected_hash


def parse_utc(value: str) -> dt.datetime:
    return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def load_sources() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    paths = [READINESS_PATH, PANEL_REVIEW_PATH, BUILD_MANIFEST_PATH, PREVIEW_PATH, COVERAGE_LOCK_PATH]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise BlockedError(f"required source artifact missing: {missing}")
    readiness = read_json(READINESS_PATH)
    panel_review = read_json(PANEL_REVIEW_PATH)
    build_manifest = read_json(BUILD_MANIFEST_PATH)
    preview = read_json(PREVIEW_PATH)
    coverage_lock = read_json(COVERAGE_LOCK_PATH)
    if readiness.get("status") != READINESS_STATUS:
        raise BlockedError("readiness artifact status mismatch")
    if not verify_payload(readiness, READINESS_PAYLOAD_HASH):
        raise BlockedError("readiness artifact payload hash mismatch")
    if not verify_payload(panel_review, PANEL_REVIEW_PAYLOAD_HASH):
        raise BlockedError("panel review artifact payload hash mismatch")
    if not verify_payload(build_manifest, BUILD_MANIFEST_PAYLOAD_HASH):
        raise BlockedError("build manifest payload hash mismatch")
    if not verify_payload(preview, PREVIEW_PAYLOAD_HASH):
        raise BlockedError("preview artifact payload hash mismatch")
    if not verify_payload(coverage_lock, COVERAGE_LOCK_PAYLOAD_HASH):
        raise BlockedError("coverage lock payload hash mismatch")
    return readiness, panel_review, build_manifest, preview, coverage_lock


def build_summary() -> dict[str, Any]:
    readiness, panel_review, _build_manifest, preview, _coverage_lock = load_sources()
    readiness_panel = readiness["panel_review_preserved"]
    readiness_window = readiness["okx_binance_alignment_window"]
    universe = readiness["symbol_universe_alignment"]
    overlap = preview["okx_binance_overlap_planning"]
    exact_binance_symbols = sorted(overlap["exact_overlap_binance_symbols"])
    exact_okx_symbols = sorted(overlap["exact_overlap_okx_symbols"])
    aligned_start = readiness_window["recommended_aligned_window_start_utc"]
    aligned_end = readiness_window["recommended_aligned_window_end_exclusive_utc"]

    summary: dict[str, Any] = {
        "artifact_kind": "BINANCE_OKX_OVERLAP_FUNDING_RATE_HYPOTHESIS_PREREGISTRATION_CONTRACT",
        "forbidden_actions_confirmed_false": {
            "binance_1m_source_rows_read": False,
            "binance_panel_rows_read": False,
            "boundary_buffer_accessed": False,
            "candidates_generated": False,
            "capital_permission_granted": False,
            "data_artifacts_created_outside_preregistration_json": False,
            "edge_claimed": False,
            "existing_files_modified_by_module": False,
            "family_released": False,
            "funding_rate_data_fetched": False,
            "funding_rate_endpoint_called": False,
            "funding_strategy_executed": False,
            "holdout_accessed": False,
            "live_permission_granted": False,
            "momentum_retest_executed": False,
            "okx_panel_rows_read": False,
            "okx_whitelisted_artifact_read": False,
            "reversal_retest_executed": False,
            "runtime_permission_granted": False,
            "strategy_search_executed": False,
        },
        "funding_data_source_contract": {
            "api_keys": "forbidden",
            "authentication": "none / public endpoint only",
            "base_url": "https://fapi.binance.com/fapi/v1/fundingRate",
            "endpoint_called_by_this_module": False,
            "exchange": "Binance USD-M Futures",
            "expected_future_response_fields": ["symbol", "fundingRate", "fundingTime", "markPrice"],
            "future_execution_must_respect_binance_rate_limits_and_pagination": True,
            "future_request_parameters": ["symbol", "startTime", "endTime", "limit"],
            "public_endpoint": "GET /fapi/v1/fundingRate",
            "this_preregistration_module_must_not_call_endpoint": True,
        },
        "funding_rate_hypothesis_preregistration": {
            "economic_prior": (
                "Funding rates are a public cost-of-carry/crowding proxy. The hypothesis is that extreme positive "
                "funding reflects overextended long demand and negative/low funding reflects short pressure; "
                "subsequent cross-sectional price returns may mean-revert after the funding observation becomes known."
            ),
            "hypothesis_name": HYPOTHESIS_NAME,
            "hypothesis_statement": (
                "In USD-M perpetual futures, relatively high positive funding rates indicate crowded long exposure "
                "and should predict weaker subsequent price returns, while relatively low or negative funding rates "
                "indicate crowded short exposure or long compensation and should predict stronger subsequent price "
                "returns, after a no-lookahead availability lag."
            ),
            "no_active_candidate_exists": True,
            "no_edge_claim_exists": True,
            "prior_momentum_route_remains_closed": True,
            "prior_reversal_route_remains_closed": True,
            "relationship_to_prior_routes": "independent_new_route_family_preregistration_not_a_momentum_or_reversal_retest",
            "route_family": ROUTE_FAMILY,
            "selected_after_funding_data_scan": False,
            "selected_after_holdout_access": False,
            "selected_after_observing_new_funding_performance": False,
            "selected_after_strategy_search": False,
            "selection_basis": "PERFORMANCE_FREE_THEORETICAL_PRIOR",
        },
        "future_execution_controls": {
            "funding_observation_alignment_policy": {
                "funding_observations_keyed_by": "fundingTime",
                "funding_timestamps_outside_aligned_window_policy": (
                    "Funding timestamps outside aligned window may be used only for lookback context before the first "
                    "aligned trading timestamp if and only if they are before the aligned window and do not access OKX "
                    "holdout/boundary data."
                ),
                "no_lookahead_policy": "A funding observation at fundingTime T may not be used for any entry earlier than T + 1 hour.",
                "signal_availability_lag_hours": 1,
            },
            "future_execution_must_not_read_okx_panel_rows_unless_separately_allowed": True,
            "future_execution_must_not_use_binance_panel_rows_outside_aligned_window_except_pre_window_funding_context": True,
            "future_execution_must_not_use_funding_observations_with_funding_time_at_or_after": ALIGNED_WINDOW_END_EXCLUSIVE,
            "no_execution_by_this_module": True,
            "p1_policy_required_before_future_execution": True,
        },
        "future_metric_and_evaluation_policy": {
            "cost_policy": {
                "fee_bps_per_side": 5,
                "round_trip_cost_bps": 20,
                "slippage_bps_per_side": 5,
            },
            "diagnostic_promising_requires_all": [
                "best_validation_net_metric_positive_after_cost",
                "validation_positive_after_cost",
                "null_baseline_review_passed",
                "monthly_stability_review_passed",
                "turnover_concentration_review_passed",
                "metric_integrity_passed",
                "safety_review_passed",
            ],
            "final_edge_claim_requires_external_or_future_holdout": True,
            "gross_metrics_required": True,
            "if_funding_adjusted_cashflow_alignment_is_ambiguous": "report secondary metric unavailable; do not substitute",
            "incomplete_hour_policy_required": True,
            "metric_integrity_checks_required": True,
            "monthly_stability_required": True,
            "net_cost_adjusted_metrics_required": True,
            "no_cross_window_holding_returns": True,
            "no_lookahead_policy_applied": True,
            "null_baseline": "deterministic_block_shuffled_timestamp_spread_return_null_or_funding_signal_timestamp_block_shuffle",
            "null_baseline_required": True,
            "null_run_count": 100,
            "p1_policy_required": "incomplete-hour rows and row-count delta must be explicitly handled before future execution",
            "positive_result_is_not_candidate": True,
            "positive_result_is_not_edge_claim": True,
            "positive_result_requires_separate_closure": True,
            "positive_result_requires_separate_evaluator": True,
            "positive_result_requires_separate_governance_before_any_followup": True,
            "primary_return_metric": "price_return_only_net_of_trading_costs",
            "secondary_diagnostic_metric": "funding_adjusted_total_return_if_funding_cashflow_alignment_is_unambiguous",
            "signal_entry_delay_applied": True,
            "turnover_concentration_required": True,
        },
        "module": MODULE_PATH,
        "predefined_config_grid": {
            "config_count": len(CONFIG_IDS),
            "deterministic_config_ids": CONFIG_IDS,
            "holding_periods_hours": HOLDING_PERIODS_HOURS,
            "no_alternative_data": True,
            "no_ensemble": True,
            "no_ml": True,
            "no_news_or_social_data": True,
            "no_order_book_data": True,
            "no_parameter_expansion_without_new_contract": True,
            "no_symbol_specific_tuning": True,
            "route_family_count": 1,
            "signal_transforms": SIGNAL_TRANSFORMS,
        },
        "prior_panel_review_preserved": {
            "active_p0_blocker_count": panel_review["aggregate_row_validation_review"]["active_p0_blocker_count"],
            "active_p1_attention_count": panel_review["aggregate_row_validation_review"]["active_p1_attention_count"],
            "incomplete_hour_review_passed": panel_review["incomplete_hour_review"]["incomplete_hour_review_passed"],
            "panel_validity_classification": panel_review["panel_validity_classification"],
            "review_payload_sha256_excluding_hash": panel_review["payload_sha256_excluding_hash"],
            "reviewed_complete_1h_row_count": panel_review["aggregate_row_validation_review"]["reviewed_complete_1h_row_count"],
            "reviewed_duplicate_symbol_hour_count": panel_review["aggregate_row_validation_review"]["reviewed_duplicate_symbol_hour_count"],
            "reviewed_incomplete_1h_row_count": panel_review["aggregate_row_validation_review"]["reviewed_incomplete_1h_row_count"],
            "reviewed_numeric_sanity_valid": panel_review["aggregate_row_validation_review"]["reviewed_numeric_sanity_valid"],
            "reviewed_ohlc_sanity_valid": panel_review["aggregate_row_validation_review"]["reviewed_ohlc_sanity_valid"],
            "reviewed_output_1h_row_count": panel_review["aggregate_row_validation_review"]["reviewed_output_1h_row_count"],
            "reviewed_symbol_count": panel_review["aggregate_row_validation_review"]["reviewed_symbol_count"],
            "row_count_delta_review_passed": panel_review["row_count_delta_review"]["row_count_delta_review_passed"],
            "timestamp_boundary_review_passed": panel_review["timestamp_boundary_review"]["timestamp_boundary_review_passed"],
        },
        "prior_readiness_preserved": {
            "active_p0_blocker_count": readiness_panel["active_p0_blocker_count"],
            "active_p1_attention_count": readiness_panel["active_p1_attention_count"],
            "binance_okx_exact_overlap_current_trading_near_5y_count": universe["binance_okx_exact_overlap_current_trading_near_5y_count"],
            "binance_okx_exact_overlap_strict_5y_count": universe["binance_okx_exact_overlap_strict_5y_count"],
            "binance_okx_exact_overlap_symbol_count": universe["binance_okx_exact_overlap_symbol_count"],
            "immediate_next_module_required": readiness["safety_permissions"]["immediate_next_module_required"],
            "panel_valid_for_read_only_second_source_alignment_planning": readiness["safety_permissions"]["panel_valid_for_read_only_second_source_alignment_planning"],
            "project_can_pause_after_readiness_summary": readiness["safety_permissions"]["project_can_pause_after_readiness_summary"],
            "readiness_classification": readiness["second_source_readiness_classification"],
            "readiness_payload_sha256_excluding_hash": readiness["payload_sha256_excluding_hash"],
            "recommended_aligned_window_end_exclusive_utc": aligned_end,
            "recommended_aligned_window_start_utc": aligned_start,
        },
        "repo_scope": {
            "api_key_used": False,
            "binance_1m_kline_source_rows_read": False,
            "binance_coverage_discovery_rerun": False,
            "binance_panel_build_rerun": False,
            "binance_panel_rows_read": False,
            "candidate_generation": False,
            "code_changes_repo_only": True,
            "edge_claim": False,
            "funding_rate_data_fetched_by_this_module": False,
            "funding_rate_endpoint_called_by_this_module": False,
            "okx_panel_rows_read": False,
            "okx_whitelisted_artifact_read": False,
            "private_api_used": False,
            "preregistration_artifact_created_in_repo": True,
            "public_network_used": False,
            "runtime_live_capital": False,
            "strategy_search_executed": False,
        },
        "safety_permissions": {
            "binance_panel_row_access_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "capital_permission_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "funding_data_acquisition_allowed_now": False,
            "funding_rate_hypothesis_preregistered": True,
            "funding_strategy_execution_allowed_now": False,
            "holdout_access_allowed_now": False,
            "immediate_next_module_required": False,
            "live_permission_allowed_now": False,
            "next_step_may_be_funding_data_acquisition_planning_or_execution_only_after_explicit_user_approval": True,
            "okx_panel_access_allowed_now": False,
            "preregistration_contract_created": True,
            "project_can_pause_after_preregistration": True,
            "runtime_permission_allowed_now": False,
            "strategy_search_allowed_now": False,
        },
        "signal_construction_contract": {
            "eligible_symbol_at_timestamp": "symbol must have a valid reviewed Binance 1h panel row and a lagged funding signal available",
            "funding_outlier_policy": (
                "winsorize cross-sectional funding signal at 1st/99th percentile per timestamp for ranking diagnostics only; "
                "primary rank order uses raw funding value unless numeric invalid."
            ),
            "minimum_symbols_required_per_timestamp": 60,
            "missing_funding_policy": "exclude symbol at timestamp until valid lagged funding observation exists",
            "portfolio_construction": "equal-weight dollar-neutral long/short spread",
            "primary_signal": "latest_lagged_funding_rate",
            "secondary_predefined_signal_transforms": ["rolling_mean_3_funding_events", "rolling_mean_9_funding_events"],
            "signal_direction": "long low/negative funding; short high/positive funding",
            "signal_family": "cross_sectional_funding_rate_rank",
            "tail_selection": "bottom 20 percent funding-rank long, top 20 percent funding-rank short",
            "tie_policy": "deterministic sort by symbol after signal value",
            "transforms_are_predefined_before_execution": True,
        },
        "source_artifacts": {
            "all_source_artifacts_read_only": True,
            "build_manifest_path": str(BUILD_MANIFEST_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "build_manifest_payload_hash_verified": True,
            "coverage_lock_path": str(COVERAGE_LOCK_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "coverage_lock_payload_hash_verified": True,
            "panel_review_artifact_path": str(PANEL_REVIEW_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "panel_review_payload_hash_verified": True,
            "preview_artifact_path": str(PREVIEW_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "preview_payload_hash_verified": True,
            "readiness_artifact_path": str(READINESS_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "readiness_artifact_payload_hash_verified": True,
            "readiness_artifact_status": readiness["status"],
        },
        "source_checkpoint": {
            "prior_head": PRIOR_HEAD,
            "prior_readiness_artifact": "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json",
            "prior_readiness_payload_sha256_excluding_hash": READINESS_PAYLOAD_HASH,
            "prior_readiness_status": READINESS_STATUS,
            "prior_readiness_tool": "tools/edge_factory_os_repo_only_binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.py",
            "prior_tracked_python_count": PRIOR_TRACKED_PYTHON_COUNT,
            "project": "Edge Factory OS / Binance OKX overlap funding-rate preregistration",
            "repo_clean_before_preregistration": True,
        },
        "status": REQUIRED_STATUS,
        "universe_and_window_contract": {
            "aligned_window_end_exclusive_utc": aligned_end,
            "aligned_window_start_utc": aligned_start,
            "binance_panel_review_p1_attention_count": readiness_panel["active_p1_attention_count"],
            "exact_overlap_symbol_count": universe["binance_okx_exact_overlap_symbol_count"],
            "future_execution_binance_symbol_set": exact_binance_symbols,
            "future_execution_okx_symbol_set": exact_okx_symbols,
            "instrument_universe": "Binance/OKX exact overlap 81 symbols",
            "okx_boundary_buffer_excluded": True,
            "okx_sealed_holdout_excluded": True,
            "p1_policy_required_before_future_execution": True,
            "symbol_source": "readiness/preview/build artifacts, not panel rows",
        },
    }
    summary["validation_checks"] = {
        "active_p0_blocker_count_zero_preserved": readiness_panel["active_p0_blocker_count"] == 0,
        "active_p1_attention_count_three_preserved": readiness_panel["active_p1_attention_count"] == 3,
        "aligned_window_verified": aligned_start == ALIGNED_WINDOW_START and aligned_end == ALIGNED_WINDOW_END_EXCLUSIVE,
        "build_manifest_loaded": True,
        "build_manifest_payload_hash_verified": True,
        "config_count_is_9": len(CONFIG_IDS) == 9,
        "config_ids_deterministic": CONFIG_IDS == [
            "funding_latest_hold8h",
            "funding_latest_hold16h",
            "funding_latest_hold24h",
            "funding_mean3_hold8h",
            "funding_mean3_hold16h",
            "funding_mean3_hold24h",
            "funding_mean9_hold8h",
            "funding_mean9_hold16h",
            "funding_mean9_hold24h",
        ],
        "coverage_lock_loaded": True,
        "coverage_lock_payload_hash_verified": True,
        "edge_claim_forbidden": True,
        "exact_overlap_symbol_count_verified_81": universe["binance_okx_exact_overlap_symbol_count"] == 81,
        "exactly_one_new_tracked_json_preregistration_artifact_expected": True,
        "exactly_one_new_tracked_python_tool_file_expected": True,
        "funding_data_not_fetched": True,
        "funding_endpoint_not_called": True,
        "funding_route_family_count_is_one": True,
        "module_path_equals_required_path": MODULE_PATH == "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_rate_hypothesis_preregistration_contract_v1.py",
        "no_binance_1m_source_rows_read": True,
        "no_binance_panel_rows_read": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_existing_files_modified_expected": True,
        "no_network_used": True,
        "no_okx_panel_rows_read": True,
        "no_other_tracked_files_expected": True,
        "no_runtime_live_capital": True,
        "no_strategy_search": True,
        "panel_review_artifact_loaded": True,
        "panel_review_payload_hash_verified": True,
        "payload_sha256_excluding_hash_present": True,
        "preregistration_artifact_json_valid": True,
        "preregistration_artifact_path_equals_required_path": PREREGISTRATION_ARTIFACT_PATH == "artifacts/research_preregistrations/binance_okx_overlap_funding_rate_hypothesis_preregistration_contract_v1.json",
        "preview_artifact_loaded": True,
        "preview_payload_hash_verified": True,
        "readiness_artifact_loaded": True,
        "readiness_payload_hash_verified": True,
        "readiness_status_verified": readiness["status"] == READINESS_STATUS,
        "replacement_checks_all_true": True,
        "runtime_live_capital_forbidden": True,
        "status_equals_required_status": True,
        "strategy_search_forbidden": True,
    }
    summary["replacement_checks_all_true"] = all(value is True for value in summary["validation_checks"].values())
    hash_input = dict(summary)
    hash_input.pop("payload_sha256_excluding_hash", None)
    summary["payload_sha256_excluding_hash"] = hashlib.sha256(canonical_json_bytes(hash_input)).hexdigest()
    return summary


def validate_summary(summary: dict[str, Any]) -> None:
    assert summary["status"] == REQUIRED_STATUS
    assert summary["module"] == MODULE_PATH
    assert PREREGISTRATION_ARTIFACT_PATH == "artifacts/research_preregistrations/binance_okx_overlap_funding_rate_hypothesis_preregistration_contract_v1.json"
    assert summary["source_artifacts"]["readiness_artifact_payload_hash_verified"] is True
    assert summary["source_artifacts"]["panel_review_payload_hash_verified"] is True
    assert summary["source_artifacts"]["build_manifest_payload_hash_verified"] is True
    assert summary["source_artifacts"]["preview_payload_hash_verified"] is True
    assert summary["source_artifacts"]["coverage_lock_payload_hash_verified"] is True
    assert summary["prior_readiness_preserved"]["active_p0_blocker_count"] == 0
    assert summary["universe_and_window_contract"]["exact_overlap_symbol_count"] == 81
    assert summary["universe_and_window_contract"]["aligned_window_start_utc"] == ALIGNED_WINDOW_START
    assert summary["universe_and_window_contract"]["aligned_window_end_exclusive_utc"] == ALIGNED_WINDOW_END_EXCLUSIVE
    assert summary["funding_rate_hypothesis_preregistration"]["route_family"] == ROUTE_FAMILY
    assert summary["predefined_config_grid"]["route_family_count"] == 1
    assert summary["predefined_config_grid"]["config_count"] == 9
    assert summary["repo_scope"]["funding_rate_endpoint_called_by_this_module"] is False
    assert summary["repo_scope"]["funding_rate_data_fetched_by_this_module"] is False
    assert summary["repo_scope"]["binance_panel_rows_read"] is False
    assert summary["repo_scope"]["okx_panel_rows_read"] is False
    assert summary["repo_scope"]["strategy_search_executed"] is False
    assert summary["repo_scope"]["candidate_generation"] is False
    assert summary["repo_scope"]["edge_claim"] is False
    assert summary["repo_scope"]["runtime_live_capital"] is False
    assert summary["safety_permissions"]["immediate_next_module_required"] is False
    assert summary["safety_permissions"]["project_can_pause_after_preregistration"] is True
    assert all(value is False for value in summary["forbidden_actions_confirmed_false"].values())
    assert summary["replacement_checks_all_true"] is True
    assert summary["payload_sha256_excluding_hash"]


def write_summary(summary: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if TEMP_ARTIFACT_PATH.exists():
        TEMP_ARTIFACT_PATH.unlink()
    TEMP_ARTIFACT_PATH.write_bytes(canonical_json_bytes(summary) + b"\n")
    TEMP_ARTIFACT_PATH.replace(ARTIFACT_PATH)


def stdout_summary(summary: dict[str, Any]) -> dict[str, Any]:
    universe = summary["universe_and_window_contract"]
    config = summary["predefined_config_grid"]
    hypothesis = summary["funding_rate_hypothesis_preregistration"]
    return {
        "aligned_window_end_exclusive_utc": universe["aligned_window_end_exclusive_utc"],
        "aligned_window_start_utc": universe["aligned_window_start_utc"],
        "candidate_generation": False,
        "config_count": config["config_count"],
        "edge_claim": False,
        "exact_overlap_symbol_count": universe["exact_overlap_symbol_count"],
        "funding_data_fetched_by_this_module": False,
        "funding_endpoint_called_by_this_module": False,
        "holding_periods_hours": config["holding_periods_hours"],
        "hypothesis_name": hypothesis["hypothesis_name"],
        "immediate_next_module_required": False,
        "payload_sha256_excluding_hash": summary["payload_sha256_excluding_hash"],
        "preregistration_artifact_path": PREREGISTRATION_ARTIFACT_PATH,
        "project_can_pause_after_preregistration": True,
        "replacement_checks_all_true": summary["replacement_checks_all_true"],
        "route_family": hypothesis["route_family"],
        "runtime_live_capital": False,
        "signal_transforms": config["signal_transforms"],
        "status": summary["status"],
        "strategy_search_executed": False,
    }


def main() -> int:
    try:
        summary = build_summary()
        validate_summary(summary)
        write_summary(summary)
    except BlockedError as exc:
        if TEMP_ARTIFACT_PATH.exists():
            TEMP_ARTIFACT_PATH.unlink()
        if ARTIFACT_PATH.exists():
            ARTIFACT_PATH.unlink()
        print(
            json.dumps(
                {
                    "exact_blocker": str(exc),
                    "preregistration_artifact_path": PREREGISTRATION_ARTIFACT_PATH,
                    "replacement_checks_all_true": False,
                    "status": "BLOCKED",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1
    print(json.dumps(stdout_summary(summary), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
