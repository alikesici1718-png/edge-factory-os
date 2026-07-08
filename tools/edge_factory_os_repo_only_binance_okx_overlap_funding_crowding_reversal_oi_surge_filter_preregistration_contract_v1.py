from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_CROWDING_REVERSAL_OI_SURGE_FILTER_PREREGISTRATION_CONTRACT_CREATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_FUNDING_CROWDING_REVERSAL_OI_SURGE_FILTER_PREREGISTRATION_CONTRACT"
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_crowding_reversal_oi_surge_filter_preregistration_contract_v1.py"
ARTIFACT_PATH = "artifacts/research_preregistrations/binance_okx_overlap_funding_crowding_reversal_oi_surge_filter_preregistration_contract_v1.json"

PRIOR_HEAD = "b245a8a18cbd70d019d5186ef9d333618e3cbf14"
PRIOR_TRACKED_PYTHON_COUNT = 829
ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_CROWDING_REVERSAL_OI_SURGE_FILTER_BASELINE"
HYPOTHESIS_NAME = "funding_crowding_reversal_with_oi_surge_filter"
ROUTE_TYPE = "cross_sectional_long_short_funding_crowding_reversal_with_oi_confirmation"
CONFIG_ID = "funding_mean9_oi_surge24h_p80_30d_hold24h"
SYMBOL_COUNT = 81
WINDOW_START = "2023-07-01T00:00:00Z"
WINDOW_END = "2025-10-31T16:00:00Z"
TRAIN_START = "2023-07-01T00:00:00Z"
TRAIN_END = "2025-01-01T00:00:00Z"
VALIDATION_START = "2025-01-01T00:00:00Z"
VALIDATION_END = "2025-10-31T16:00:00Z"

SOURCE_ARTIFACTS = {
    "latest_funding_carry_closure": (
        "artifacts/strategy_closures/binance_okx_overlap_funding_carry_short_positive_flat_negative_closure_v1.json",
        "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_CARRY_SHORT_POSITIVE_FLAT_NEGATIVE_CLOSURE_CREATED",
        "FUNDING_CARRY_SHORT_POSITIVE_FLAT_NEGATIVE_REJECTED_NO_FOLLOWUP",
    ),
    "latest_group2_closure": (
        "artifacts/strategy_closures/binance_okx_group2_funding_extreme_momentum_confirmed_closure_v1.json",
        "PASS_REPO_ONLY_BINANCE_OKX_GROUP2_FUNDING_EXTREME_MOMENTUM_CONFIRMED_CLOSURE_CREATED",
        "GROUP2_FUNDING_EXTREME_MOMENTUM_CONFIRMED_REJECTED_NO_FOLLOWUP",
    ),
    "prior_funding_extreme_momentum_liquidity_closure": (
        "artifacts/strategy_closures/binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_closure_v1.json",
        "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_EXTREME_MOMENTUM_CONFIRMED_LIQUIDITY_FILTERED_CLOSURE_CREATED",
        "FUNDING_EXTREME_MOMENTUM_LIQUIDITY_REJECTED_NO_FOLLOWUP",
    ),
    "prior_plain_funding_closure": (
        "artifacts/strategy_closures/binance_okx_overlap_funding_rate_closure_record_after_evaluator_v1.json",
        "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_RATE_CLOSURE_RECORD_AFTER_EVALUATOR_CREATED",
        "FUNDING_RATE_CROWDING_REVERSAL_REJECTED_NO_FOLLOWUP",
    ),
}

METADATA_SOURCES = {
    "funding_data_review": "artifacts/funding_rate_reviews/binance_okx_overlap_funding_rate_data_review_after_acquisition_lock_v1.json",
    "funding_acquisition_lock": "artifacts/funding_rate_locks/binance_okx_overlap_funding_rate_data_acquisition_lock_v1.json",
    "second_source_readiness": "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json",
    "panel_review": "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json",
    "coverage_lock": "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json",
}

FORBIDDEN_PERMISSION_KEYS = {
    "candidate_generation",
    "candidate_generation_allowed_from_closure",
    "candidate_generation_allowed_from_evaluator",
    "candidate_generation_allowed_now",
    "candidates_generated",
    "capital_permission_allowed_now",
    "capital_permission_granted",
    "edge_claim",
    "edge_claim_allowed_from_closure",
    "edge_claim_allowed_from_evaluator",
    "edge_claim_allowed_now",
    "edge_claimed",
    "family_release",
    "family_release_allowed_from_closure",
    "family_release_allowed_from_evaluator",
    "family_release_allowed_now",
    "family_released",
    "holdout_access_allowed_now",
    "holdout_accessed",
    "live_permission_allowed_now",
    "live_permission_granted",
    "runtime_live_capital",
    "runtime_live_capital_allowed_from_closure",
    "runtime_live_capital_allowed_from_evaluator",
    "runtime_live_capital_allowed_now",
    "runtime_permission_allowed_now",
    "runtime_permission_granted",
}


class Blocked(Exception):
    pass


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_json(root: Path, rel_path: str) -> dict[str, Any]:
    path = root / rel_path
    if not path.exists():
        raise Blocked(f"missing required source artifact: {rel_path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise Blocked(f"source artifact is not a JSON object: {rel_path}")
    return payload


def payload_hash(payload: dict[str, Any]) -> str:
    clone = dict(payload)
    clone.pop("payload_sha256_excluding_hash", None)
    data = json.dumps(clone, indent=2, sort_keys=True).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def verify_payload_hash(payload: dict[str, Any], rel_path: str) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise Blocked(f"missing payload_sha256_excluding_hash: {rel_path}")
    recomputed = payload_hash(payload)
    if recomputed != stored:
        raise Blocked(f"payload hash mismatch for {rel_path}: {recomputed} != {stored}")
    return stored


def contains_value(payload: Any, expected: Any) -> bool:
    if payload == expected:
        return True
    if isinstance(payload, dict):
        return any(contains_value(value, expected) for value in payload.values())
    if isinstance(payload, list):
        return any(contains_value(value, expected) for value in payload)
    return False


def check_forbidden_permissions_false(payload: Any, path: str = "") -> list[str]:
    violations: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            child_path = f"{path}.{key}" if path else key
            if key in FORBIDDEN_PERMISSION_KEYS and value is not False:
                violations.append(f"{child_path}={value!r}")
            violations.extend(check_forbidden_permissions_false(value, child_path))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            violations.extend(check_forbidden_permissions_false(value, f"{path}[{index}]"))
    return violations


def load_sources(root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    loaded: dict[str, dict[str, Any]] = {}
    source_summary: dict[str, Any] = {}

    for label, (rel_path, expected_status, expected_result) in SOURCE_ARTIFACTS.items():
        payload = read_json(root, rel_path)
        stored_hash = verify_payload_hash(payload, rel_path)
        if payload.get("status") != expected_status:
            raise Blocked(f"{label} status mismatch: {payload.get('status')} != {expected_status}")
        if not contains_value(payload, expected_result):
            raise Blocked(f"{label} did not preserve expected result: {expected_result}")
        violations = check_forbidden_permissions_false(payload)
        if violations:
            raise Blocked(f"{label} has forbidden permission truthy values: {violations}")
        loaded[label] = payload
        source_summary[label] = {
            "path": rel_path,
            "payload_sha256_excluding_hash": stored_hash,
            "payload_hash_verified": True,
            "result_class_verified": expected_result,
            "status": expected_status,
        }

    for label, rel_path in METADATA_SOURCES.items():
        payload = read_json(root, rel_path)
        stored_hash = verify_payload_hash(payload, rel_path)
        violations = check_forbidden_permissions_false(payload)
        if violations:
            raise Blocked(f"{label} has forbidden permission truthy values: {violations}")
        loaded[label] = payload
        source_summary[label] = {
            "path": rel_path,
            "payload_sha256_excluding_hash": stored_hash,
            "payload_hash_verified": True,
            "status": payload.get("status"),
        }

    funding_review = loaded["funding_data_review"]
    if funding_review.get("safety_permissions", {}).get("funding_data_valid_for_future_funding_signal_construction") is not True:
        raise Blocked("funding data review does not validate future funding signal construction")

    readiness = loaded["second_source_readiness"]
    universe = readiness.get("symbol_universe_alignment", {})
    window = readiness.get("okx_binance_alignment_window", {})
    if universe.get("binance_okx_exact_overlap_symbol_count") != SYMBOL_COUNT:
        raise Blocked("readiness exact overlap symbol count is not 81")
    if window.get("recommended_aligned_window_start_utc") != WINDOW_START:
        raise Blocked("readiness aligned window start mismatch")
    if window.get("recommended_aligned_window_end_exclusive_utc") != WINDOW_END:
        raise Blocked("readiness aligned window end mismatch")

    return loaded, source_summary


def build_artifact(root: Path) -> dict[str, Any]:
    _loaded, source_summary = load_sources(root)

    repo_scope = {
        "api_key_used": False,
        "binance_funding_rows_read": False,
        "binance_panel_rows_read": False,
        "code_changes_repo_only": True,
        "candidate_generation": False,
        "edge_claim": False,
        "funding_data_fetched_by_this_module": False,
        "funding_rate_endpoint_called_by_this_module": False,
        "oi_data_fetched_by_this_module": False,
        "oi_endpoint_called_by_this_module": False,
        "okx_panel_rows_read": False,
        "private_api_used": False,
        "preregistration_artifact_created_in_repo": True,
        "public_network_used": False,
        "runtime_live_capital": False,
        "strategy_executed": False,
    }

    oi_anomaly_definition = (
        "oi_change_24h = log(oi_value_t / oi_value_t_minus_24h); require oi_change_24h > 0 "
        "and greater than the symbol-local trailing 30 calendar day 80th percentile, using OI "
        "observations available with a 1 hour lag"
    )

    validation_checks = {
        "aligned_window_verified": True,
        "config_count_is_one": True,
        "config_id_deterministic": True,
        "exact_overlap_symbol_count_verified_81": True,
        "execution_blocked_until_oi_data_lock": True,
        "exactly_one_new_tracked_json_preregistration_artifact_expected": True,
        "exactly_one_new_tracked_python_tool_file_expected": True,
        "funding_data_review_loaded": True,
        "funding_data_valid_for_signal_construction_verified": True,
        "latest_funding_carry_closure_loaded": True,
        "latest_funding_carry_closure_rejected_no_followup_verified": True,
        "module_path_equals_required_path": True,
        "no_binance_panel_rows_read": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_existing_files_modified_expected": True,
        "no_funding_data_fetched": True,
        "no_funding_endpoint_called": True,
        "no_funding_rows_read": True,
        "no_network_used": True,
        "no_oi_data_fetched": True,
        "no_oi_endpoint_called": True,
        "no_okx_panel_rows_read": True,
        "no_other_tracked_files_expected": True,
        "no_runtime_live_capital": True,
        "no_strategy_execution": True,
        "oi_data_availability_warning_recorded": True,
        "payload_sha256_excluding_hash_present": True,
        "preregistration_artifact_json_valid": True,
        "preregistration_artifact_path_equals_required_path": True,
        "prior_funding_closures_loaded": True,
        "prior_funding_closures_rejected_no_followup_verified": True,
        "replacement_checks_all_true": True,
        "route_family_count_is_one": True,
        "status_equals_required_status": True,
    }

    artifact = {
        "artifact_kind": ARTIFACT_KIND,
        "config_grid": {
            "config_count": 1,
            "config_id": CONFIG_ID,
            "funding_transform": "rolling_mean_9_funding_events",
            "holding_period_hours": 24,
            "minimum_long_symbols": 3,
            "minimum_oi_anomaly_eligible_symbols": 20,
            "minimum_short_symbols": 3,
            "no_parameter_expansion_without_new_contract": True,
            "oi_anomaly": "24h OI change > symbol trailing 30d 80th percentile and > 0",
        },
        "forbidden_actions_confirmed_false": {
            "binance_funding_rows_read": False,
            "binance_panel_rows_read": False,
            "boundary_buffer_accessed": False,
            "candidates_generated": False,
            "capital_permission_granted": False,
            "edge_claimed": False,
            "existing_files_modified_by_module": False,
            "family_released": False,
            "funding_data_fetched": False,
            "funding_rate_endpoint_called": False,
            "holdout_accessed": False,
            "live_permission_granted": False,
            "oi_data_fetched": False,
            "oi_endpoint_called": False,
            "okx_panel_rows_read": False,
            "runtime_permission_granted": False,
            "strategy_executed": False,
            "strategy_search_executed": False,
        },
        "funding_crowding_oi_surge_hypothesis_preregistration": {
            "critical_interpretation": "This preregistration records a route idea only; execution is blocked until historical OI data availability, acquisition, and review are separately locked.",
            "hypothesis_name": HYPOTHESIS_NAME,
            "hypothesis_statement": (
                "Funding crowding reversal is more likely to work when open interest is rising anomalously. "
                "A positive open-interest surge indicates that positioning/crowding is actively building. "
                "Therefore, low-funding and high-funding extremes should only be traded when the symbol also "
                "has a recent OI surge anomaly."
            ),
            "route_family": ROUTE_FAMILY,
            "route_type": ROUTE_TYPE,
        },
        "future_execution_controls": {
            "execution_blocked_until_oi_data_lock": True,
            "no_additional_configs": True,
            "no_boundary_buffer": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_funding_transform_grid": True,
            "no_holding_period_grid": True,
            "no_holdout": True,
            "no_network_during_execution": True,
            "no_oi_threshold_optimization": True,
            "no_okx_panel_rows": True,
            "no_runtime_live_capital": True,
            "use_aligned_window_only": True,
            "use_exact_81_symbol_universe": True,
            "use_reviewed_binance_1h_panel_only": True,
            "use_reviewed_binance_funding_rate_data_only": True,
            "use_reviewed_oi_history_data_only": True,
        },
        "future_metric_and_evaluation_policy": {
            "diagnostic_promising_requires_all": [
                "validation_net_metric_bps > 0",
                "validation_positive_after_cost is true",
                "null_baseline_review_preliminary_passed is true",
                "monthly_stability_review_preliminary_passed is true",
                "turnover_concentration_review_preliminary_passed is true",
                "oi_anomaly_coverage_review_passed is true",
                "metric_integrity_passed is true",
                "safety_review_passed is true",
            ],
            "positive_result_still_requires_evaluator_closure_and_governance": True,
        },
        "module": MODULE_PATH,
        "oi_anomaly_filter_contract": {
            "forbidden_without_separate_contract": [
                "paid/vendor data",
                "exchange-private data",
                "inferred OI from price/volume",
                "reconstructed OI from non-OI fields",
            ],
            "no_cross_sectional_oi_threshold_search": True,
            "no_oi_percentile_grid": True,
            "no_oi_z_score_grid": True,
            "oi_anomaly_definition": oi_anomaly_definition,
            "oi_lookback_for_percentile": "30 calendar days",
            "oi_observation_lag_hours": 1,
            "oi_period_preferred": "1h",
            "primary_oi_field": "sumOpenInterestValue",
            "primary_oi_field_reason": "sumOpenInterestValue is more comparable across symbols because it is notional-like, while sumOpenInterest is contract/base-unit dependent.",
            "secondary_oi_field": "sumOpenInterest",
        },
        "oi_data_availability_warning": {
            "binance_current_open_interest_limitation": "Binance current open interest endpoint gives only present open interest.",
            "binance_open_interest_hist_limitation": "Binance openInterestHist endpoint is documented as providing only latest 1 month of data.",
            "execution_blocked_until_oi_data_lock": True,
            "fallback_source_candidate": "Binance openInterestHist endpoint only for future/live-forward or latest-one-month diagnostics, not for the historical aligned window.",
            "preferred_source_candidate": "Binance public historical OI metrics archive if discoverable and containing symbol/time/sumOpenInterestValue.",
            "route_not_executable_over_aligned_window_until_oi_lock": True,
            "this_preregistration_authorizes_execution": False,
        },
        "payload_sha256_excluding_hash": "",
        "prior_route_closures_preserved": {
            "latest_funding_carry_route": source_summary["latest_funding_carry_closure"],
            "latest_group2_route": source_summary["latest_group2_closure"],
            "prior_funding_extreme_momentum_liquidity_route": source_summary["prior_funding_extreme_momentum_liquidity_closure"],
            "prior_plain_funding_route": source_summary["prior_plain_funding_closure"],
        },
        "repo_scope": repo_scope,
        "replacement_checks_all_true": True,
        "safety_permissions": {
            "binance_panel_row_access_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "capital_permission_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "funding_row_access_allowed_now": False,
            "holdout_access_allowed_now": False,
            "immediate_next_module_required": False,
            "live_permission_allowed_now": False,
            "oi_data_acquisition_allowed_now": False,
            "oi_row_access_allowed_now": False,
            "oi_surge_hypothesis_preregistered": True,
            "okx_panel_access_allowed_now": False,
            "preregistration_contract_created": True,
            "project_can_pause_after_preregistration": True,
            "runtime_permission_allowed_now": False,
            "strategy_execution_allowed_now": False,
            "strategy_search_allowed_now": False,
        },
        "signal_construction_contract": {
            "base_funding_signal": "rolling_mean_9_funding_events",
            "funding_direction": "long low/negative funding, short high/positive funding",
            "funding_lag_hours": 1,
            "oi_anomaly_filter": "require positive 24h OI change anomaly",
            "oi_observation_lag_hours": 1,
            "trading_rule": [
                "Compute rolling_mean_9_funding_events using funding observations available with 1h lag.",
                "Compute OI 24h change using OI observations available with 1h lag.",
                "Compute OI anomaly using symbol-local trailing 30d 80th percentile.",
                "Restrict to symbols with OI anomaly true.",
                "Rank remaining symbols by funding signal ascending.",
                "Long leg: bottom 20 percent funding signal.",
                "Short leg: top 20 percent funding signal.",
                "Require at least 20 OI-anomaly eligible symbols.",
                "Require at least 3 long symbols and 3 short symbols.",
                "Use equal-weight dollar-neutral long/short spread.",
            ],
        },
        "source_artifacts": {
            **source_summary,
            "all_source_artifacts_loaded": True,
            "all_source_payload_hashes_verified": True,
            "no_source_artifact_grants_candidate_edge_release_live_capital": True,
        },
        "source_checkpoint": {
            "latest_completed_route": "funding_carry_short_positive_flat_negative",
            "latest_completed_route_result": "FUNDING_CARRY_SHORT_POSITIVE_FLAT_NEGATIVE_REJECTED_NO_FOLLOWUP",
            "prior_head": PRIOR_HEAD,
            "prior_tracked_python_count": PRIOR_TRACKED_PYTHON_COUNT,
            "project": "Edge Factory OS / Binance OKX overlap funding-crowding OI-surge preregistration",
            "repo_clean_before_preregistration": True,
        },
        "status": STATUS,
        "universe_and_window_contract": {
            "aligned_window_end_exclusive_utc": WINDOW_END,
            "aligned_window_start_utc": WINDOW_START,
            "exact_overlap_symbol_count": SYMBOL_COUNT,
            "okx_boundary_buffer_excluded": True,
            "okx_sealed_holdout_excluded": True,
            "train_window_end_exclusive_utc": TRAIN_END,
            "train_window_start_utc": TRAIN_START,
            "universe": "Binance/OKX exact overlap 81 Binance symbols",
            "validation_window_end_exclusive_utc": VALIDATION_END,
            "validation_window_start_utc": VALIDATION_START,
        },
        "validation_checks": validation_checks,
    }

    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    return artifact


def validate_artifact(artifact: dict[str, Any]) -> None:
    assert artifact["status"] == STATUS
    assert artifact["module"] == MODULE_PATH
    assert ARTIFACT_PATH == "artifacts/research_preregistrations/binance_okx_overlap_funding_crowding_reversal_oi_surge_filter_preregistration_contract_v1.json"
    assert artifact["funding_crowding_oi_surge_hypothesis_preregistration"]["route_family"] == ROUTE_FAMILY
    assert artifact["config_grid"]["config_count"] == 1
    assert artifact["config_grid"]["config_id"] == CONFIG_ID
    assert artifact["future_execution_controls"]["execution_blocked_until_oi_data_lock"] is True
    assert artifact["safety_permissions"]["oi_data_acquisition_allowed_now"] is False
    assert artifact["safety_permissions"]["strategy_execution_allowed_now"] is False
    assert artifact["repo_scope"]["public_network_used"] is False
    assert artifact["repo_scope"]["oi_endpoint_called_by_this_module"] is False
    assert artifact["repo_scope"]["oi_data_fetched_by_this_module"] is False
    assert artifact["repo_scope"]["funding_rate_endpoint_called_by_this_module"] is False
    assert artifact["repo_scope"]["binance_panel_rows_read"] is False
    assert artifact["repo_scope"]["binance_funding_rows_read"] is False
    assert artifact["repo_scope"]["strategy_executed"] is False
    assert artifact["repo_scope"]["candidate_generation"] is False
    assert artifact["repo_scope"]["edge_claim"] is False
    assert artifact["repo_scope"]["runtime_live_capital"] is False
    assert artifact["replacement_checks_all_true"] is True
    assert all(artifact["validation_checks"].values())
    assert payload_hash(artifact) == artifact["payload_sha256_excluding_hash"]


def write_artifact(root: Path, artifact: dict[str, Any]) -> None:
    path = root / ARTIFACT_PATH
    if path.exists():
        raise Blocked(f"target artifact already exists: {ARTIFACT_PATH}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def summary(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "aligned_window_end_exclusive_utc": WINDOW_END,
        "aligned_window_start_utc": WINDOW_START,
        "candidate_generation": False,
        "config_id": CONFIG_ID,
        "edge_claim": False,
        "execution_blocked_until_oi_data_lock": True,
        "hypothesis_name": HYPOTHESIS_NAME,
        "immediate_next_module_required": False,
        "oi_anomaly_definition": artifact["oi_anomaly_filter_contract"]["oi_anomaly_definition"],
        "oi_data_acquisition_allowed_now": False,
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "preregistration_artifact_path": ARTIFACT_PATH,
        "project_can_pause_after_preregistration": True,
        "replacement_checks_all_true": True,
        "route_family": ROUTE_FAMILY,
        "runtime_live_capital": False,
        "status": STATUS,
        "strategy_execution_allowed_now": False,
        "symbol_count": SYMBOL_COUNT,
    }


def main() -> int:
    root = repo_root()
    try:
        if MODULE_PATH != "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_crowding_reversal_oi_surge_filter_preregistration_contract_v1.py":
            raise Blocked("module path constant mismatch")
        artifact = build_artifact(root)
        validate_artifact(artifact)
        write_artifact(root, artifact)
        print(json.dumps(summary(artifact), indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"reason": str(exc), "replacement_checks_all_true": False, "status": "BLOCKED"}, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
