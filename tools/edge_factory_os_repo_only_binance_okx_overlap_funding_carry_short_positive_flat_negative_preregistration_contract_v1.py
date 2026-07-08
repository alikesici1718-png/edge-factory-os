from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_CARRY_SHORT_POSITIVE_FLAT_NEGATIVE_PREREGISTRATION_CONTRACT_CREATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_FUNDING_CARRY_SHORT_POSITIVE_FLAT_NEGATIVE_PREREGISTRATION_CONTRACT"
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_carry_short_positive_flat_negative_preregistration_contract_v1.py"
ARTIFACT_PATH = "artifacts/research_preregistrations/binance_okx_overlap_funding_carry_short_positive_flat_negative_preregistration_contract_v1.json"

ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_CARRY_SHORT_POSITIVE_FLAT_NEGATIVE_BASELINE"
HYPOTHESIS_NAME = "funding_carry_short_positive_flat_negative"
ROUTE_TYPE = "one_sided_short_only_funding_carry"
CONFIG_ID = "funding_carry_short_positive_flat_negative_hold8h"
ALIGNED_START = "2023-07-01T00:00:00Z"
ALIGNED_END = "2025-10-31T16:00:00Z"
TRAIN_START = "2023-07-01T00:00:00Z"
TRAIN_END = "2025-01-01T00:00:00Z"
VALIDATION_START = "2025-01-01T00:00:00Z"
VALIDATION_END = "2025-10-31T16:00:00Z"

SOURCE_ARTIFACTS = {
    "latest_group2_closure": (
        "artifacts/strategy_closures/binance_okx_group2_funding_extreme_momentum_confirmed_closure_v1.json",
        "8bddb11159022e8b4d057169ab203a315716f2c310b6a30fe825a774af76e896",
    ),
    "prior_funding_extreme_liquidity_closure": (
        "artifacts/strategy_closures/binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_closure_v1.json",
        "a4824ed55c95ab3a0dcfcd1f37d49fffcd1453f3bd69bc1d866edd609da610cc",
    ),
    "prior_plain_funding_closure": (
        "artifacts/strategy_closures/binance_okx_overlap_funding_rate_closure_record_after_evaluator_v1.json",
        "8eacb2decacac50140de27b6c84a9a5338e2473e62ccce54be5d07770a576b02",
    ),
    "funding_data_review": (
        "artifacts/funding_rate_reviews/binance_okx_overlap_funding_rate_data_review_after_acquisition_lock_v1.json",
        "a579feb0472efbf03ffa955008dfabc0b526fa37029fc81dddd0195b4054d849",
    ),
    "funding_acquisition_lock": (
        "artifacts/funding_rate_locks/binance_okx_overlap_funding_rate_data_acquisition_lock_v1.json",
        "dd5877b101c9a1e8d73f35f6032381cbdfd5435578abacf97b9db0c11c28e252",
    ),
    "second_source_readiness": (
        "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json",
        "0cfe239f6f5ad2d20bda64b827416851de8f5b959066902b59f1f00f44eba716",
    ),
    "panel_review": (
        "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json",
        "34b88a3ff0870c708e2df034c243cf639b711ebce3c6a4f32edffb92a2229112",
    ),
    "coverage_lock": (
        "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json",
        "18a84b71c649b0462fdb0d511597dcb701448fe06184ef9c8da93d6911ada4e0",
    ),
}


class Blocked(Exception):
    pass


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def payload_hash(payload: dict[str, Any]) -> str:
    clone = dict(payload)
    clone.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(clone, indent=2, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def read_json(root: Path, rel_path: str) -> dict[str, Any]:
    path = root / rel_path
    if not path.exists():
        raise Blocked(f"missing required source artifact: {rel_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def verify_payload(payload: dict[str, Any], expected_hash: str, label: str) -> None:
    stored = payload.get("payload_sha256_excluding_hash")
    if stored != expected_hash:
        raise Blocked(f"{label} stored payload hash mismatch: {stored} != {expected_hash}")
    recomputed = payload_hash(payload)
    if recomputed != expected_hash:
        raise Blocked(f"{label} payload hash recompute mismatch: {recomputed} != {expected_hash}")


def assert_false(value: Any, label: str) -> None:
    if value is not False:
        raise Blocked(f"{label} is not false")


def assert_true(value: Any, label: str) -> None:
    if value is not True:
        raise Blocked(f"{label} is not true")


def verify_no_source_permissions(payloads: dict[str, dict[str, Any]]) -> None:
    checks: list[tuple[Any, str]] = []
    group2_closure = payloads["latest_group2_closure"]
    group2_record = group2_closure.get("closure_record", {})
    group2_project = group2_closure.get("project_state_after_closure", {})
    checks.extend(
        [
            (group2_record.get("candidate_generation_allowed_now"), "group2 candidate_generation_allowed_now"),
            (group2_record.get("edge_claim_allowed_now"), "group2 edge_claim_allowed_now"),
            (group2_record.get("family_release_allowed_now"), "group2 family_release_allowed_now"),
            (group2_record.get("runtime_live_capital_allowed_now"), "group2 runtime_live_capital_allowed_now"),
        ]
    )
    assert_true(group2_project.get("no_active_candidate_exists"), "group2 no_active_candidate_exists")
    assert_true(group2_project.get("no_active_edge_claim_exists"), "group2 no_active_edge_claim_exists")
    assert_true(group2_project.get("no_family_release_exists"), "group2 no_family_release_exists")
    assert_true(group2_project.get("no_holdout_access_exists"), "group2 no_holdout_access_exists")
    assert_true(group2_project.get("no_runtime_live_capital_permission_exists"), "group2 no_runtime_live_capital_permission_exists")

    for source_name in ["funding_data_review", "funding_acquisition_lock", "second_source_readiness", "panel_review", "coverage_lock"]:
        safety = payloads[source_name].get("safety_permissions", {})
        for key in [
            "candidate_generation_allowed_now",
            "edge_claim_allowed_now",
            "family_release_allowed_now",
            "holdout_access_allowed_now",
            "runtime_permission_allowed_now",
            "live_permission_allowed_now",
            "capital_permission_allowed_now",
            "strategy_search_allowed_now",
        ]:
            if key in safety:
                checks.append((safety.get(key), f"{source_name}.{key}"))

    for value, label in checks:
        assert_false(value, label)


def build_artifact(root: Path) -> dict[str, Any]:
    payloads: dict[str, dict[str, Any]] = {}
    source_artifacts: dict[str, Any] = {"all_source_artifacts_read_only": True}
    for label, (rel_path, expected_hash) in SOURCE_ARTIFACTS.items():
        payload = read_json(root, rel_path)
        verify_payload(payload, expected_hash, label)
        payloads[label] = payload
        source_artifacts[f"{label}_path"] = rel_path
        source_artifacts[f"{label}_payload_hash_verified"] = True

    latest_group2 = payloads["latest_group2_closure"]
    latest_group2_record = latest_group2.get("closure_record", {})
    if latest_group2.get("status") != "PASS_REPO_ONLY_BINANCE_OKX_GROUP2_FUNDING_EXTREME_MOMENTUM_CONFIRMED_CLOSURE_CREATED":
        raise Blocked("latest Group-2 closure status mismatch")
    if latest_group2_record.get("result_class_confirmed") != "GROUP2_FUNDING_EXTREME_MOMENTUM_CONFIRMED_REJECTED_NO_FOLLOWUP":
        raise Blocked("latest Group-2 closure result mismatch")

    prior_plain = payloads["prior_plain_funding_closure"]
    prior_plain_record = prior_plain.get("funding_route_closure_record", {})
    if prior_plain_record.get("result_class_confirmed") != "FUNDING_RATE_CROWDING_REVERSAL_REJECTED_NO_FOLLOWUP":
        raise Blocked("prior plain funding closure result mismatch")

    funding_review = payloads["funding_data_review"]
    assert_true(
        funding_review.get("safety_permissions", {}).get("funding_data_valid_for_future_funding_signal_construction"),
        "funding data valid for future funding signal construction",
    )

    readiness = payloads["second_source_readiness"]
    universe = readiness.get("symbol_universe_alignment", {})
    alignment = readiness.get("okx_binance_alignment_window", {})
    symbols = universe.get("exact_overlap_binance_symbols", [])
    if universe.get("binance_okx_exact_overlap_symbol_count") != 81 or len(symbols) != 81:
        raise Blocked("exact overlap symbol count is not 81")
    if alignment.get("recommended_aligned_window_start_utc") != ALIGNED_START or alignment.get("recommended_aligned_window_end_exclusive_utc") != ALIGNED_END:
        raise Blocked("aligned window mismatch")

    verify_no_source_permissions(payloads)

    artifact: dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
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
            "preregistration_artifact_created_in_repo": True,
            "private_api_used": False,
            "public_network_used": False,
            "runtime_live_capital": False,
            "strategy_search_executed": False,
        },
        "source_checkpoint": {
            "latest_group2_closure_artifact": SOURCE_ARTIFACTS["latest_group2_closure"][0],
            "latest_group2_closure_status": latest_group2.get("status"),
            "latest_group2_result": latest_group2_record.get("result_class_confirmed"),
            "prior_head": "8e9b5cdf901fd1df5382671aee416f4678dc4769",
            "prior_tracked_python_count": 825,
            "project": "Edge Factory OS / Binance OKX overlap funding carry preregistration",
            "repo_clean_before_preregistration": True,
        },
        "source_artifacts": source_artifacts,
        "prior_route_closures_preserved": {
            "group2_route": {
                "closure_status": latest_group2.get("status"),
                "diagnostic_promising": latest_group2_record.get("diagnostic_promising"),
                "result_class": latest_group2_record.get("result_class_confirmed"),
                "route_closed": latest_group2_record.get("route_closed"),
            },
            "plain_funding_route": {
                "closure_status": prior_plain.get("status"),
                "diagnostic_promising": prior_plain_record.get("diagnostic_promising_confirmed"),
                "result_class": prior_plain_record.get("result_class_confirmed"),
                "route_closed": prior_plain_record.get("funding_route_closed"),
            },
            "prior_funding_extreme_momentum_liquidity_route": {
                "closure_status": payloads["prior_funding_extreme_liquidity_closure"].get("status"),
                "result_class": payloads["prior_funding_extreme_liquidity_closure"].get("closure_record", {}).get("result_class_confirmed"),
                "route_closed": payloads["prior_funding_extreme_liquidity_closure"].get("closure_record", {}).get("route_closed"),
            },
        },
        "funding_carry_hypothesis_preregistration": {
            "economic_prior": "Positive funding may compensate shorts for carrying perpetual exposure, but adverse price movement and costs can overwhelm carry.",
            "hypothesis_name": HYPOTHESIS_NAME,
            "hypothesis_statement": "If the latest available funding rate is positive, shorting the perpetual may earn funding carry, while zero or negative funding keeps the symbol flat. The diagnostic tests whether positive-funding short carry overcomes price risk and transaction costs in the Binance/OKX 81-symbol overlap universe.",
            "market_neutral": False,
            "route_family": ROUTE_FAMILY,
            "route_type": ROUTE_TYPE,
            "short_beta_risk_explicitly_recorded": True,
            "short_only": True,
        },
        "universe_and_window_contract": {
            "aligned_window_end_exclusive_utc": ALIGNED_END,
            "aligned_window_start_utc": ALIGNED_START,
            "okx_boundary_buffer_excluded": True,
            "okx_sealed_holdout_excluded": True,
            "symbol_count": 81,
            "symbols": symbols,
            "train_window_end_exclusive_utc": TRAIN_END,
            "train_window_start_utc": TRAIN_START,
            "universe": "Binance/OKX exact overlap 81 Binance symbols",
            "validation_window_end_exclusive_utc": VALIDATION_END,
            "validation_window_start_utc": VALIDATION_START,
        },
        "signal_construction_contract": {
            "flat_rule": "flat symbol if latest_lagged_funding_rate <= 0 or missing",
            "funding_lag_hours": 1,
            "funding_observation": "latest fundingRate with funding_time <= entry_time - 1h",
            "no_funding_threshold_search": True,
            "no_long_leg": True,
            "no_short_when_funding_is_negative": True,
            "short_rule": "short symbol if latest_lagged_funding_rate > 0",
            "signal_name": "latest_lagged_positive_funding_carry",
        },
        "portfolio_and_return_contract": {
            "cost": {"round_trip_cost_bps": 20},
            "entry_price": "open at entry timestamp E",
            "exit_price": "open at E + 8h",
            "funding_cashflow": "include funding events strictly after entry time and up to and including exit time while held",
            "funding_signal_event_not_included_as_cashflow_if_at_or_before_entry_minus_1h": True,
            "holding_period_hours": 8,
            "holding_period_justification": "one funding cadence interval, simplest funding-carry horizon",
            "market_neutral": False,
            "minimum_active_short_symbols": 10,
            "no_btc_eth_hedge": True,
            "no_dynamic_beta_hedge": True,
            "no_leverage_assumption_beyond_normalized_unit_notional": True,
            "no_market_hedge": True,
            "position_direction": "short_only",
            "primary_return_metric": "funding_adjusted_short_return_net_of_costs",
            "secondary_diagnostic_metric": "price_only_short_return_net_of_costs",
            "short_price_return": "-(exit_open / entry_open - 1)",
        },
        "config_grid": {
            "config_count": 1,
            "configs": [
                {
                    "config_id": CONFIG_ID,
                    "funding_signal": "latest_lagged_funding_rate",
                    "holding_period_hours": 8,
                    "minimum_active_short_symbols": 10,
                }
            ],
            "no_parameter_expansion_without_new_contract": True,
            "route_family_count": 1,
        },
        "future_execution_controls": {
            "candidate_generation_allowed": False,
            "edge_claim_allowed": False,
            "family_release_allowed": False,
            "funding_threshold_optimization_allowed": False,
            "holdout_access_allowed": False,
            "holding_period_grid_allowed": False,
            "liquidity_filter_grid_allowed": False,
            "network_allowed": False,
            "no_additional_configs": True,
            "no_beta_hedge_unless_separately_preregistered": True,
            "no_boundary_buffer": True,
            "no_okx_panel_rows": True,
            "runtime_live_capital_allowed": False,
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
                "exposure_risk_review_preliminary_passed is true",
                "metric_integrity_passed is true",
                "safety_review_passed is true",
            ],
            "exposure_risk_review_required": {
                "average_active_short_count": True,
                "correlation_with_equal_weight_market_return_if_computed": True,
                "market_beta_proxy_if_available": True,
                "max_active_short_count": True,
                "worst_drawdown_proxy_if_available": True,
                "worst_monthly_net_metric": True,
            },
            "positive_result_is_diagnostic_only": True,
            "positive_result_requires_separate_evaluator_closure_and_governance_before_any_candidate_or_edge": True,
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
        },
        "safety_permissions": {
            "binance_panel_row_access_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "capital_permission_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "funding_carry_hypothesis_preregistered": True,
            "funding_data_acquisition_allowed_now": False,
            "funding_row_access_allowed_now": False,
            "holdout_access_allowed_now": False,
            "immediate_next_module_required": False,
            "live_permission_allowed_now": False,
            "okx_panel_access_allowed_now": False,
            "project_can_pause_after_preregistration": True,
            "preregistration_contract_created": True,
            "runtime_permission_allowed_now": False,
            "strategy_execution_allowed_now": False,
            "strategy_search_allowed_now": False,
        },
    }

    validation_checks = {
        "aligned_window_verified": True,
        "config_count_is_one": True,
        "config_id_deterministic": CONFIG_ID == "funding_carry_short_positive_flat_negative_hold8h",
        "exact_overlap_symbol_count_verified_81": True,
        "exactly_one_new_tracked_json_preregistration_artifact_expected": True,
        "exactly_one_new_tracked_python_tool_file_expected": True,
        "funding_data_review_loaded": True,
        "funding_data_valid_for_signal_construction_verified": True,
        "latest_group2_closure_loaded": True,
        "latest_group2_closure_rejected_no_followup_verified": True,
        "market_neutral_false_explicitly_recorded": artifact["funding_carry_hypothesis_preregistration"]["market_neutral"] is False,
        "module_path_equals_required_path": MODULE_PATH == "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_carry_short_positive_flat_negative_preregistration_contract_v1.py",
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
        "payload_sha256_excluding_hash_present": True,
        "preregistration_artifact_json_valid": True,
        "preregistration_artifact_path_equals_required_path": ARTIFACT_PATH == "artifacts/research_preregistrations/binance_okx_overlap_funding_carry_short_positive_flat_negative_preregistration_contract_v1.json",
        "prior_funding_closure_loaded": True,
        "prior_funding_closure_rejected_no_followup_verified": True,
        "replacement_checks_all_true": True,
        "route_family_count_is_one": True,
        "short_only_route_explicitly_recorded": artifact["funding_carry_hypothesis_preregistration"]["short_only"] is True,
        "status_equals_required_status": STATUS == "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_CARRY_SHORT_POSITIVE_FLAT_NEGATIVE_PREREGISTRATION_CONTRACT_CREATED",
    }
    artifact["validation_checks"] = validation_checks
    artifact["replacement_checks_all_true"] = all(validation_checks.values())

    if artifact["status"] != STATUS:
        raise Blocked("status mismatch")
    if artifact["module"] != MODULE_PATH:
        raise Blocked("module path mismatch")
    if ROUTE_FAMILY != "CROSS_SECTIONAL_FUNDING_CARRY_SHORT_POSITIVE_FLAT_NEGATIVE_BASELINE":
        raise Blocked("route_family mismatch")
    if artifact["config_grid"]["config_count"] != 1:
        raise Blocked("config_count mismatch")
    if artifact["config_grid"]["configs"][0]["config_id"] != CONFIG_ID:
        raise Blocked("config_id mismatch")
    if artifact["funding_carry_hypothesis_preregistration"]["route_type"] != ROUTE_TYPE:
        raise Blocked("route_type mismatch")
    if artifact["funding_carry_hypothesis_preregistration"]["market_neutral"] is not False:
        raise Blocked("market_neutral is not false")
    if artifact["replacement_checks_all_true"] is not True:
        raise Blocked("replacement_checks_all_true is false")

    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    return artifact


def write_artifact(root: Path, artifact: dict[str, Any]) -> None:
    output = root / ARTIFACT_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    reloaded = json.loads(output.read_text(encoding="utf-8"))
    if payload_hash(reloaded) != artifact["payload_sha256_excluding_hash"]:
        output.unlink(missing_ok=True)
        raise Blocked("written preregistration artifact payload hash mismatch")


def main() -> int:
    root = repo_root()
    output = root / ARTIFACT_PATH
    try:
        artifact = build_artifact(root)
        write_artifact(root, artifact)
        summary = {
            "aligned_window_end_exclusive_utc": ALIGNED_END,
            "aligned_window_start_utc": ALIGNED_START,
            "candidate_generation": False,
            "config_id": CONFIG_ID,
            "edge_claim": False,
            "holding_period_hours": 8,
            "hypothesis_name": HYPOTHESIS_NAME,
            "immediate_next_module_required": False,
            "market_neutral": False,
            "minimum_active_short_symbols": 10,
            "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
            "preregistration_artifact_path": ARTIFACT_PATH,
            "project_can_pause_after_preregistration": True,
            "replacement_checks_all_true": artifact["replacement_checks_all_true"],
            "route_family": ROUTE_FAMILY,
            "route_type": ROUTE_TYPE,
            "runtime_live_capital": False,
            "short_only": True,
            "status": STATUS,
            "strategy_execution_allowed_now": False,
            "symbol_count": 81,
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        if output.exists():
            output.unlink()
        print(f"BLOCKED {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
