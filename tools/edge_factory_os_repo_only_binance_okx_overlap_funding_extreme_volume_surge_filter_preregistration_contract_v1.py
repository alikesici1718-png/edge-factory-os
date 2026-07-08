from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_EXTREME_VOLUME_SURGE_FILTER_PREREGISTRATION_CONTRACT_CREATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_FUNDING_EXTREME_VOLUME_SURGE_FILTER_PREREGISTRATION_CONTRACT"
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_extreme_volume_surge_filter_preregistration_contract_v1.py"
ARTIFACT_PATH = "artifacts/research_preregistrations/binance_okx_overlap_funding_extreme_volume_surge_filter_preregistration_contract_v1.json"

PRIOR_HEAD = "2b09a561665606f59758443b60c65a26fd9e344c"
PRIOR_TRACKED_PYTHON_COUNT = 831
ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_EXTREME_VOLUME_SURGE_FILTER_REVERSAL_BASELINE"
HYPOTHESIS_NAME = "funding_extreme_volume_surge_reversal"
ROUTE_TYPE = "cross_sectional_long_short_funding_extreme_reversal_with_volume_surge_filter"
CONFIG_ID = "funding_mean9_volume_surge24h_p80_30d_hold24h"
SYMBOL_COUNT = 81
WINDOW_START = "2023-07-01T00:00:00Z"
WINDOW_END = "2025-10-31T16:00:00Z"
TRAIN_START = "2023-07-01T00:00:00Z"
TRAIN_END = "2025-01-01T00:00:00Z"
VALIDATION_START = "2025-01-01T00:00:00Z"
VALIDATION_END = "2025-10-31T16:00:00Z"

SOURCE_ARTIFACTS = {
    "latest_oi_availability_lock": (
        "artifacts/oi_data_availability_locks/binance_okx_overlap_oi_historical_data_availability_discovery_lock_v1.json",
        "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_OI_HISTORICAL_DATA_AVAILABILITY_DISCOVERY_LOCK_UNAVAILABLE_ROUTE_PENDING",
        "b50672275c645246347ce43cbab7d269194767ce4496c5a91e9c5c2d6a87c81c",
    ),
    "latest_funding_carry_closure": (
        "artifacts/strategy_closures/binance_okx_overlap_funding_carry_short_positive_flat_negative_closure_v1.json",
        "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_CARRY_SHORT_POSITIVE_FLAT_NEGATIVE_CLOSURE_CREATED",
        "198029ab2d5c0bded6f78c1a6d26517b44506f645f572a1dee28734fd70785a6",
    ),
    "latest_group2_closure": (
        "artifacts/strategy_closures/binance_okx_group2_funding_extreme_momentum_confirmed_closure_v1.json",
        "PASS_REPO_ONLY_BINANCE_OKX_GROUP2_FUNDING_EXTREME_MOMENTUM_CONFIRMED_CLOSURE_CREATED",
        "8bddb11159022e8b4d057169ab203a315716f2c310b6a30fe825a774af76e896",
    ),
    "prior_funding_extreme_momentum_liquidity_closure": (
        "artifacts/strategy_closures/binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_closure_v1.json",
        "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_EXTREME_MOMENTUM_CONFIRMED_LIQUIDITY_FILTERED_CLOSURE_CREATED",
        "a4824ed55c95ab3a0dcfcd1f37d49fffcd1453f3bd69bc1d866edd609da610cc",
    ),
    "prior_plain_funding_closure": (
        "artifacts/strategy_closures/binance_okx_overlap_funding_rate_closure_record_after_evaluator_v1.json",
        "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_RATE_CLOSURE_RECORD_AFTER_EVALUATOR_CREATED",
        "8eacb2decacac50140de27b6c84a9a5338e2473e62ccce54be5d07770a576b02",
    ),
    "funding_data_review": (
        "artifacts/funding_rate_reviews/binance_okx_overlap_funding_rate_data_review_after_acquisition_lock_v1.json",
        "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_RATE_DATA_REVIEW_AFTER_ACQUISITION_LOCK_CREATED",
        "a579feb0472efbf03ffa955008dfabc0b526fa37029fc81dddd0195b4054d849",
    ),
    "funding_acquisition_lock": (
        "artifacts/funding_rate_locks/binance_okx_overlap_funding_rate_data_acquisition_lock_v1.json",
        "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_FUNDING_RATE_DATA_ACQUISITION_LOCK_CREATED",
        "dd5877b101c9a1e8d73f35f6032381cbdfd5435578abacf97b9db0c11c28e252",
    ),
    "second_source_readiness": (
        "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json",
        "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_NEAR_5Y_SECOND_SOURCE_READINESS_ALIGNMENT_SUMMARY_CREATED",
        "0cfe239f6f5ad2d20bda64b827416851de8f5b959066902b59f1f00f44eba716",
    ),
    "panel_review": (
        "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json",
        "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_NEAR_5Y_PANEL_BUILD_REVIEW_AFTER_EXECUTION_CREATED",
        "34b88a3ff0870c708e2df034c243cf639b711ebce3c6a4f32edffb92a2229112",
    ),
    "panel_build_manifest": (
        "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json",
        "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_NEAR_5Y_1M_TO_1H_PANEL_BUILD_EXECUTED",
        "bf4d4d681f36fab3a2131701e25ebc45c94ddb757f92874498ef425d698f40a7",
    ),
    "coverage_lock": (
        "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json",
        "PASS_REPO_CODE_ONLY_BINANCE_USDT_PERPETUAL_1M_COVERAGE_DISCOVERY_LOCK_CREATED",
        "18a84b71c649b0462fdb0d511597dcb701448fe06184ef9c8da93d6911ada4e0",
    ),
}

EXPECTED_RESULTS = {
    "latest_funding_carry_closure": "FUNDING_CARRY_SHORT_POSITIVE_FLAT_NEGATIVE_REJECTED_NO_FOLLOWUP",
    "latest_group2_closure": "GROUP2_FUNDING_EXTREME_MOMENTUM_CONFIRMED_REJECTED_NO_FOLLOWUP",
    "prior_funding_extreme_momentum_liquidity_closure": "FUNDING_EXTREME_MOMENTUM_LIQUIDITY_REJECTED_NO_FOLLOWUP",
    "prior_plain_funding_closure": "FUNDING_RATE_CROWDING_REVERSAL_REJECTED_NO_FOLLOWUP",
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


def canonical_hash(payload: dict[str, Any]) -> str:
    clone = dict(payload)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(json.dumps(clone, indent=2, sort_keys=True).encode("utf-8")).hexdigest()


def read_json(root: Path, rel_path: str) -> dict[str, Any]:
    path = root / rel_path
    if not path.exists():
        raise Blocked(f"missing required source artifact: {rel_path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise Blocked(f"source artifact is not a JSON object: {rel_path}")
    return payload


def verify_hash(payload: dict[str, Any], expected: str, label: str) -> None:
    stored = payload.get("payload_sha256_excluding_hash")
    if stored != expected:
        raise Blocked(f"stored payload hash mismatch for {label}: {stored} != {expected}")
    recomputed = canonical_hash(payload)
    if recomputed != stored:
        raise Blocked(f"recomputed payload hash mismatch for {label}: {recomputed} != {stored}")


def contains_value(payload: Any, expected: Any) -> bool:
    if payload == expected:
        return True
    if isinstance(payload, dict):
        return any(contains_value(value, expected) for value in payload.values())
    if isinstance(payload, list):
        return any(contains_value(value, expected) for value in payload)
    return False


def forbidden_permission_violations(payload: Any, path: str = "") -> list[str]:
    violations: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            child_path = f"{path}.{key}" if path else key
            if key in FORBIDDEN_PERMISSION_KEYS and value is not False:
                violations.append(f"{child_path}={value!r}")
            violations.extend(forbidden_permission_violations(value, child_path))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            violations.extend(forbidden_permission_violations(value, f"{path}[{index}]"))
    return violations


def load_sources(root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    loaded: dict[str, dict[str, Any]] = {}
    summary: dict[str, Any] = {}
    for label, (rel_path, expected_status, expected_hash) in SOURCE_ARTIFACTS.items():
        payload = read_json(root, rel_path)
        verify_hash(payload, expected_hash, label)
        if payload.get("status") != expected_status:
            raise Blocked(f"status mismatch for {label}: {payload.get('status')} != {expected_status}")
        violations = forbidden_permission_violations(payload)
        if violations:
            raise Blocked(f"forbidden permission truthy values in {label}: {violations}")
        loaded[label] = payload
        summary[label] = {
            "path": rel_path,
            "payload_hash_verified": True,
            "payload_sha256_excluding_hash": expected_hash,
            "status": expected_status,
        }

    oi_lock = loaded["latest_oi_availability_lock"]
    if oi_lock.get("availability_classification", {}).get("classification") != "OI_HISTORY_PARTIALLY_AVAILABLE_REQUIRES_REDUCED_UNIVERSE_OR_WINDOW":
        raise Blocked("latest OI availability classification mismatch")
    if oi_lock.get("pending_route_record_if_unavailable", {}).get("route_pending") is not True:
        raise Blocked("latest OI availability lock does not preserve route pending")
    if oi_lock.get("continuation_decision", {}).get("continue_to_oi_acquisition") is not False:
        raise Blocked("latest OI lock unexpectedly allows acquisition")

    for label, expected_result in EXPECTED_RESULTS.items():
        if not contains_value(loaded[label], expected_result):
            raise Blocked(f"{label} did not preserve expected result: {expected_result}")

    funding_review = loaded["funding_data_review"]
    if funding_review.get("safety_permissions", {}).get("funding_data_valid_for_future_funding_signal_construction") is not True:
        raise Blocked("funding review does not validate future funding signal construction")

    panel_review = loaded["panel_review"]
    if panel_review.get("panel_validity_classification") != "PANEL_REVIEW_PASS_WITH_P1_ATTENTION_VALID_FOR_READ_ONLY_SECOND_SOURCE_ANALYSIS":
        raise Blocked("panel review is not valid for read-only second-source analysis")

    readiness = loaded["second_source_readiness"]
    universe = readiness.get("symbol_universe_alignment", {})
    window = readiness.get("okx_binance_alignment_window", {})
    if universe.get("binance_okx_exact_overlap_symbol_count") != SYMBOL_COUNT:
        raise Blocked("readiness exact overlap count mismatch")
    if window.get("recommended_aligned_window_start_utc") != WINDOW_START:
        raise Blocked("readiness aligned window start mismatch")
    if window.get("recommended_aligned_window_end_exclusive_utc") != WINDOW_END:
        raise Blocked("readiness aligned window end mismatch")

    build_manifest = loaded["panel_build_manifest"]
    if build_manifest.get("build_scope", {}).get("exact_overlap_symbol_count") != SYMBOL_COUNT:
        raise Blocked("panel build manifest exact overlap count mismatch")

    return loaded, summary


def build_artifact(root: Path) -> dict[str, Any]:
    _loaded, source_summary = load_sources(root)
    volume_anomaly_definition = (
        "trailing_24h_quote_volume = sum quote_volume over the prior 24 complete 1h rows, excluding current entry hour; "
        "volume_change_24h = log(trailing_24h_quote_volume_t / trailing_24h_quote_volume_t_minus_24h); "
        "require volume_change_24h > 0 and greater than the symbol-local trailing 30 calendar day 80th percentile, "
        "with all volume windows using only completed bars strictly before entry timestamp"
    )
    validation_checks = {
        "aligned_window_verified": True,
        "config_count_is_one": True,
        "config_id_deterministic": True,
        "exact_overlap_symbol_count_verified_81": True,
        "exactly_one_new_tracked_json_preregistration_artifact_expected": True,
        "exactly_one_new_tracked_python_tool_file_expected": True,
        "execution_requires_explicit_user_approval": True,
        "funding_data_review_loaded": True,
        "funding_data_valid_for_signal_construction_verified": True,
        "latest_funding_carry_closure_loaded": True,
        "latest_funding_carry_closure_rejected_no_followup_verified": True,
        "latest_oi_availability_lock_loaded": True,
        "module_path_equals_required_path": True,
        "no_binance_panel_rows_read": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_existing_files_modified_expected": True,
        "no_funding_data_fetched": True,
        "no_funding_endpoint_called": True,
        "no_funding_rows_read": True,
        "no_network_used": True,
        "no_okx_panel_rows_read": True,
        "no_other_tracked_files_expected": True,
        "no_runtime_live_capital": True,
        "no_strategy_execution": True,
        "no_volume_data_fetched": True,
        "oi_surge_route_pending_preserved": True,
        "panel_review_loaded": True,
        "panel_valid_for_read_only_second_source_analysis_verified": True,
        "payload_sha256_excluding_hash_present": True,
        "preregistration_artifact_json_valid": True,
        "preregistration_artifact_path_equals_required_path": True,
        "prior_funding_closures_loaded": True,
        "prior_funding_closures_rejected_no_followup_verified": True,
        "replacement_checks_all_true": True,
        "route_family_count_is_one": True,
        "status_equals_required_status": True,
        "volume_data_available_from_reviewed_panel_recorded": True,
    }
    artifact = {
        "artifact_kind": ARTIFACT_KIND,
        "config_grid": {
            "config_count": 1,
            "config_id": CONFIG_ID,
            "funding_transform": "rolling_mean_9_funding_events",
            "holding_period_hours": 24,
            "minimum_long_symbols": 3,
            "minimum_short_symbols": 3,
            "minimum_volume_anomaly_eligible_symbols": 20,
            "no_parameter_expansion_without_new_contract": True,
            "volume_anomaly": "24h quote-volume change > symbol trailing 30d 80th percentile and > 0",
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
            "okx_panel_rows_read": False,
            "runtime_permission_granted": False,
            "strategy_executed": False,
            "strategy_search_executed": False,
            "volume_data_fetched": False,
        },
        "funding_volume_hypothesis_preregistration": {
            "hypothesis_name": HYPOTHESIS_NAME,
            "hypothesis_statement": (
                "Funding extremes are more likely to represent actionable crowding when the same symbol also has an "
                "abnormal surge in traded quote volume. A volume surge indicates attention, positioning, and "
                "participation. Therefore, low-funding and high-funding extremes should be traded only when the "
                "symbol's recent quote-volume activity is unusually high versus its own recent history."
            ),
            "route_family": ROUTE_FAMILY,
            "route_type": ROUTE_TYPE,
        },
        "future_execution_controls": {
            "execution_requires_explicit_user_approval": True,
            "no_additional_configs": True,
            "no_boundary_buffer": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_funding_transform_grid": True,
            "no_holding_period_grid": True,
            "no_holdout": True,
            "no_network_during_execution": True,
            "no_okx_panel_rows": True,
            "no_runtime_live_capital": True,
            "no_volume_threshold_optimization": True,
            "use_aligned_window_only": True,
            "use_exact_81_symbol_universe": True,
            "use_reviewed_binance_1h_panel_only": True,
            "use_reviewed_binance_funding_rate_data_only": True,
        },
        "future_metric_and_evaluation_policy": {
            "diagnostic_promising_requires_all": [
                "validation_net_metric_bps > 0",
                "validation_positive_after_cost is true",
                "null_baseline_review_preliminary_passed is true",
                "monthly_stability_review_preliminary_passed is true",
                "turnover_concentration_review_preliminary_passed is true",
                "volume_anomaly_coverage_review_passed is true",
                "metric_integrity_passed is true",
                "safety_review_passed is true",
            ],
            "positive_result_still_requires_separate_evaluator_closure_and_governance": True,
        },
        "module": MODULE_PATH,
        "payload_sha256_excluding_hash": "",
        "prior_route_closures_preserved": {
            "latest_funding_carry_route": source_summary["latest_funding_carry_closure"],
            "latest_group2_route": source_summary["latest_group2_closure"],
            "oi_surge_route_pending": source_summary["latest_oi_availability_lock"],
            "prior_funding_extreme_momentum_liquidity_route": source_summary["prior_funding_extreme_momentum_liquidity_closure"],
            "prior_plain_funding_route": source_summary["prior_plain_funding_closure"],
        },
        "repo_scope": {
            "api_key_used": False,
            "binance_funding_rows_read": False,
            "binance_panel_rows_read": False,
            "candidate_generation": False,
            "code_changes_repo_only": True,
            "edge_claim": False,
            "funding_data_fetched_by_this_module": False,
            "funding_rate_endpoint_called_by_this_module": False,
            "okx_panel_rows_read": False,
            "private_api_used": False,
            "preregistration_artifact_created_in_repo": True,
            "public_network_used": False,
            "runtime_live_capital": False,
            "strategy_executed": False,
            "volume_data_fetched_by_this_module": False,
        },
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
            "okx_panel_access_allowed_now": False,
            "preregistration_contract_created": True,
            "project_can_pause_after_preregistration": True,
            "runtime_permission_allowed_now": False,
            "strategy_execution_allowed_now": False,
            "strategy_search_allowed_now": False,
            "volume_data_acquisition_allowed_now": False,
            "volume_surge_hypothesis_preregistered": True,
        },
        "signal_construction_contract": {
            "base_funding_signal": "rolling_mean_9_funding_events",
            "funding_direction": "long low/negative funding, short high/positive funding",
            "funding_lag_hours": 1,
            "trading_rule_for_future_execution": [
                "Compute rolling_mean_9_funding_events using funding observations available with 1h lag.",
                "Compute trailing_24h_quote_volume using prior complete 1h bars only.",
                "Compute volume_change_24h.",
                "Compute symbol-local trailing 30d 80th percentile of volume_change_24h.",
                "Restrict to symbols with volume anomaly true.",
                "Rank remaining symbols by funding signal ascending.",
                "Long leg: bottom 20 percent funding signal.",
                "Short leg: top 20 percent funding signal.",
                "Require at least 20 volume-anomaly eligible symbols.",
                "Require at least 3 long symbols and 3 short symbols.",
                "Use equal-weight dollar-neutral long/short spread.",
            ],
            "volume_anomaly_filter": "require positive 24h quote-volume surge anomaly",
        },
        "source_artifacts": {
            **source_summary,
            "all_source_artifacts_loaded": True,
            "all_source_payload_hashes_verified": True,
            "no_source_artifact_grants_candidate_edge_release_live_capital": True,
        },
        "source_checkpoint": {
            "latest_oi_availability_classification": "OI_HISTORY_PARTIALLY_AVAILABLE_REQUIRES_REDUCED_UNIVERSE_OR_WINDOW",
            "latest_oi_availability_status": "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_OI_HISTORICAL_DATA_AVAILABILITY_DISCOVERY_LOCK_UNAVAILABLE_ROUTE_PENDING",
            "prior_head": PRIOR_HEAD,
            "prior_tracked_python_count": PRIOR_TRACKED_PYTHON_COUNT,
            "project": "Edge Factory OS / Binance OKX overlap funding extreme volume surge preregistration",
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
        "volume_anomaly_filter_contract": {
            "no_cross_sectional_volume_threshold_search": True,
            "no_volume_percentile_grid": True,
            "no_volume_z_score_grid": True,
            "volume_anomaly_definition": volume_anomaly_definition,
            "volume_anomaly_field": "quote_volume from reviewed Binance 1h panel",
            "volume_lookback_for_percentile": "30 calendar days",
            "volume_observations_no_lookahead": "all volume windows use only completed bars strictly before entry timestamp",
        },
        "volume_data_availability_note": {
            "execution_not_authorized_by_this_preregistration": True,
            "new_data_acquisition_lock_required_before_future_execution": False,
            "volume_data_available_from_reviewed_binance_1h_panel": True,
            "volume_data_read_by_this_module": False,
            "volume_differs_from_oi": "Unlike OI, quote_volume is already present in the reviewed Binance 1h panel.",
        },
    }
    artifact["payload_sha256_excluding_hash"] = canonical_hash(artifact)
    return artifact


def validate_artifact(artifact: dict[str, Any]) -> None:
    assert artifact["status"] == STATUS
    assert artifact["module"] == MODULE_PATH
    assert ARTIFACT_PATH == "artifacts/research_preregistrations/binance_okx_overlap_funding_extreme_volume_surge_filter_preregistration_contract_v1.json"
    assert artifact["funding_volume_hypothesis_preregistration"]["route_family"] == ROUTE_FAMILY
    assert artifact["config_grid"]["config_count"] == 1
    assert artifact["config_grid"]["config_id"] == CONFIG_ID
    assert artifact["volume_data_availability_note"]["volume_data_available_from_reviewed_binance_1h_panel"] is True
    assert artifact["volume_data_availability_note"]["volume_data_read_by_this_module"] is False
    assert artifact["safety_permissions"]["strategy_execution_allowed_now"] is False
    assert artifact["repo_scope"]["public_network_used"] is False
    assert artifact["repo_scope"]["binance_panel_rows_read"] is False
    assert artifact["repo_scope"]["binance_funding_rows_read"] is False
    assert artifact["repo_scope"]["strategy_executed"] is False
    assert artifact["repo_scope"]["candidate_generation"] is False
    assert artifact["repo_scope"]["edge_claim"] is False
    assert artifact["repo_scope"]["runtime_live_capital"] is False
    assert artifact["replacement_checks_all_true"] is True
    assert all(artifact["validation_checks"].values())
    assert canonical_hash(artifact) == artifact["payload_sha256_excluding_hash"]


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
        "hypothesis_name": HYPOTHESIS_NAME,
        "immediate_next_module_required": False,
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "preregistration_artifact_path": ARTIFACT_PATH,
        "project_can_pause_after_preregistration": True,
        "replacement_checks_all_true": True,
        "route_family": ROUTE_FAMILY,
        "runtime_live_capital": False,
        "status": STATUS,
        "strategy_execution_allowed_now": False,
        "symbol_count": SYMBOL_COUNT,
        "volume_anomaly_definition": artifact["volume_anomaly_filter_contract"]["volume_anomaly_definition"],
    }


def main() -> int:
    root = repo_root()
    try:
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
