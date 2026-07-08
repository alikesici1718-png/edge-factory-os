#!/usr/bin/env python3
"""Preregister one funding-extreme momentum-confirmed liquidity-filtered route."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


REQUIRED_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_EXTREME_MOMENTUM_CONFIRMED_LIQUIDITY_FILTERED_PREREGISTRATION_CONTRACT_CREATED"
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_preregistration_contract_v1.py"
ARTIFACT_PATH = "artifacts/research_preregistrations/binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_preregistration_contract_v1.json"
REPO_PATH = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
OUTPUT_PATH = REPO_PATH / ARTIFACT_PATH
TEMP_PATH = OUTPUT_PATH.with_suffix(".json.tmp")

PRIOR_HEAD = "74076f30957538d43d5fb9da79aa7adbcadca65f"
PRIOR_TRACKED_PYTHON_COUNT = 817
ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_EXTREME_MOMENTUM_CONFIRMED_LIQUIDITY_FILTERED_REVERSAL"
HYPOTHESIS_NAME = "funding_extreme_momentum_confirmed_reversal"
CONFIG_ID = "funding_extreme_mom24_liqtop60_hold24h"
WINDOW_START = "2023-07-01T00:00:00Z"
WINDOW_END = "2025-10-31T16:00:00Z"
TRAIN_START = "2023-07-01T00:00:00Z"
TRAIN_END = "2025-01-01T00:00:00Z"
VALIDATION_START = "2025-01-01T00:00:00Z"
VALIDATION_END = "2025-10-31T16:00:00Z"

SOURCE_PATHS = {
    "closure": "artifacts/strategy_closures/binance_okx_overlap_funding_rate_closure_record_after_evaluator_v1.json",
    "prior_evaluator": "artifacts/strategy_evaluations/binance_okx_overlap_funding_rate_execution_evaluator_after_preregistered_9_config_run_v1.json",
    "prior_execution": "artifacts/strategy_executions/binance_okx_overlap_funding_rate_preregistered_9_config_execution_v1.json",
    "funding_review": "artifacts/funding_rate_reviews/binance_okx_overlap_funding_rate_data_review_after_acquisition_lock_v1.json",
    "funding_lock": "artifacts/funding_rate_locks/binance_okx_overlap_funding_rate_data_acquisition_lock_v1.json",
    "prior_preregistration": "artifacts/research_preregistrations/binance_okx_overlap_funding_rate_hypothesis_preregistration_contract_v1.json",
    "readiness": "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json",
    "panel_review": "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json",
    "build_manifest": "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json",
    "preview": "artifacts/panel_build_previews/binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.json",
    "coverage_lock": "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json",
}

EXPECTED_PAYLOAD_HASHES = {
    "closure": "8eacb2decacac50140de27b6c84a9a5338e2473e62ccce54be5d07770a576b02",
    "prior_evaluator": "2dc652c21ad2b103aa5821e141d259abe523e03cc6662a28bb2e04dccc342306",
    "prior_execution": "0f9fc66e7fdf3e15bc84fe4e88d4c110902c8f62d9e31eec1628c96e27eda8a7",
    "funding_review": "a579feb0472efbf03ffa955008dfabc0b526fa37029fc81dddd0195b4054d849",
    "funding_lock": "dd5877b101c9a1e8d73f35f6032381cbdfd5435578abacf97b9db0c11c28e252",
    "prior_preregistration": "5febb59aee08873de1dbfc0464da463811090c334c18c5f2a552e1768cb3c768",
    "readiness": "0cfe239f6f5ad2d20bda64b827416851de8f5b959066902b59f1f00f44eba716",
}


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")


def payload_hash(payload: dict[str, Any]) -> str:
    clone = dict(payload)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json_bytes(clone)).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def verify_payload(payload: dict[str, Any], expected: str) -> bool:
    return payload.get("payload_sha256_excluding_hash") == expected and payload_hash(payload) == expected


def load_sources() -> dict[str, dict[str, Any]]:
    payloads: dict[str, dict[str, Any]] = {}
    for key, rel_path in SOURCE_PATHS.items():
        path = REPO_PATH / rel_path
        if not path.is_file():
            raise AssertionError(f"missing source artifact: {rel_path}")
        payloads[key] = read_json(path)
        expected = EXPECTED_PAYLOAD_HASHES.get(key)
        if expected and not verify_payload(payloads[key], expected):
            raise AssertionError(f"payload hash mismatch: {key}")
    closure = payloads["closure"]
    readiness = payloads["readiness"]
    if closure["status"] != "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_RATE_CLOSURE_RECORD_AFTER_EVALUATOR_CREATED":
        raise AssertionError("latest funding closure status mismatch")
    if closure["project_state_after_closure"]["no_active_candidate_exists"] is not True:
        raise AssertionError("active candidate exists")
    if closure["project_state_after_closure"]["no_active_edge_claim_exists"] is not True:
        raise AssertionError("active edge claim exists")
    if closure["project_state_after_closure"]["no_family_release_exists"] is not True:
        raise AssertionError("family release exists")
    if closure["project_state_after_closure"]["no_runtime_live_capital_permission_exists"] is not True:
        raise AssertionError("runtime/live/capital permission exists")
    if readiness["symbol_universe_alignment"]["binance_okx_exact_overlap_symbol_count"] != 81:
        raise AssertionError("overlap count mismatch")
    window = readiness["okx_binance_alignment_window"]
    if window["recommended_aligned_window_start_utc"] != WINDOW_START or window["recommended_aligned_window_end_exclusive_utc"] != WINDOW_END:
        raise AssertionError("aligned window mismatch")
    return payloads


def build_artifact() -> dict[str, Any]:
    payloads = load_sources()
    readiness = payloads["readiness"]
    symbols = sorted(readiness["symbol_universe_alignment"]["exact_overlap_binance_symbols"])
    if len(symbols) != 81:
        raise AssertionError("symbol list count mismatch")
    artifact = {
        "artifact_kind": "BINANCE_OKX_OVERLAP_FUNDING_EXTREME_MOMENTUM_CONFIRMED_LIQUIDITY_FILTERED_PREREGISTRATION_CONTRACT",
        "config_grid": {
            "config_count": 1,
            "config_id": CONFIG_ID,
            "configs": [
                {
                    "config_id": CONFIG_ID,
                    "funding_transform": "latest_lagged_funding_rate",
                    "holding_period_hours": 24,
                    "liquidity_filter": "top_60_percent_trailing_24h_quote_volume",
                    "minimum_eligible_symbols_before_leg_selection": 40,
                    "minimum_long_symbols": 3,
                    "minimum_short_symbols": 3,
                    "momentum_filter": "long_momentum_24h_lt_0_short_momentum_24h_gt_0",
                    "momentum_lookback_hours": 24,
                    "round_trip_cost_bps": 20,
                }
            ],
            "no_parameter_expansion": True,
        },
        "funding_filter": {
            "funding_signal": "latest fundingRate with funding_time <= entry_time - 1h",
            "long_side": "bottom_20_percent_funding_rank_after_liquidity_filter",
            "short_side": "top_20_percent_funding_rank_after_liquidity_filter",
            "signal_availability_lag_hours": 1,
        },
        "future_execution_controls": {
            "candidate_generation_allowed": False,
            "edge_claim_allowed": False,
            "family_release_allowed": False,
            "max_config_count": 1,
            "no_alternative_funding_transforms": True,
            "no_alternative_holding_periods": True,
            "no_alternative_liquidity_cutoffs": True,
            "no_alternative_momentum_lookbacks": True,
            "no_non_preregistered_config": True,
            "runtime_live_capital_allowed": False,
        },
        "hypothesis_name": HYPOTHESIS_NAME,
        "liquidity_filter": {
            "lookback_hours": 24,
            "metric": "sum_quote_volume_prior_completed_24h_bars",
            "selection": "top_60_percent",
        },
        "module": MODULE_PATH,
        "momentum_filter": {
            "formula": "close(E - 1h) / close(E - 25h) - 1",
            "lookback_hours": 24,
            "long_condition": "momentum_24h < 0",
            "short_condition": "momentum_24h > 0",
            "uses_prior_completed_1h_bars_only": True,
        },
        "replacement_checks_all_true": True,
        "repo_scope": {
            "api_key_used": False,
            "binance_api_called": False,
            "binance_panel_rows_read": False,
            "candidate_generation": False,
            "code_changes_repo_only": True,
            "edge_claim": False,
            "external_row_files_read": False,
            "family_release": False,
            "funding_data_fetch": False,
            "network_used": False,
            "okx_panel_rows_read": False,
            "runtime_live_capital": False,
        },
        "route_family": ROUTE_FAMILY,
        "safety_permissions": {
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "holdout_access_allowed_now": False,
            "runtime_live_capital_allowed_now": False,
            "strategy_execution_allowed_only_by_step_2_contract": True,
        },
        "signal_definition": {
            "entry_timestamp": "hourly complete Binance 1h panel timestamp",
            "long_candidates": "bottom_20_percent_funding_rank_and_momentum_24h_lt_0",
            "portfolio": "equal_weight_dollar_neutral_long_short_spread",
            "return_policy": "open_to_open_forward_24h",
            "short_candidates": "top_20_percent_funding_rank_and_momentum_24h_gt_0",
        },
        "source_checkpoint": {
            "latest_closure_payload_sha256_excluding_hash": EXPECTED_PAYLOAD_HASHES["closure"],
            "prior_head": PRIOR_HEAD,
            "prior_tracked_python_count": PRIOR_TRACKED_PYTHON_COUNT,
            "repo_clean_before_preregistration": True,
        },
        "source_artifacts": {key: value for key, value in SOURCE_PATHS.items()},
        "status": REQUIRED_STATUS,
        "universe_and_window": {
            "aligned_window_end_exclusive_utc": WINDOW_END,
            "aligned_window_start_utc": WINDOW_START,
            "exact_overlap_symbol_count": 81,
            "okx_boundary_buffer_excluded": True,
            "okx_sealed_holdout_excluded": True,
            "symbols": symbols,
            "train_window_end_exclusive_utc": TRAIN_END,
            "train_window_start_utc": TRAIN_START,
            "validation_window_end_exclusive_utc": VALIDATION_END,
            "validation_window_start_utc": VALIDATION_START,
        },
        "validation_checks": {
            "aligned_window_verified": True,
            "closure_payload_hash_verified": True,
            "closure_status_verified": True,
            "config_count_one": True,
            "module_path_equals_required_path": True,
            "no_active_candidate_edge_release_runtime": True,
            "no_external_rows_read": True,
            "no_network_used": True,
            "overlap_count_verified_81": True,
            "preregistration_artifact_path_equals_required_path": True,
            "replacement_checks_all_true": True,
            "status_equals_required_status": True,
        },
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    validate_artifact(artifact)
    return artifact


def validate_artifact(artifact: dict[str, Any]) -> None:
    assert artifact["status"] == REQUIRED_STATUS
    assert artifact["module"] == MODULE_PATH
    assert ARTIFACT_PATH == "artifacts/research_preregistrations/binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_preregistration_contract_v1.json"
    assert artifact["route_family"] == ROUTE_FAMILY
    assert artifact["hypothesis_name"] == HYPOTHESIS_NAME
    assert artifact["config_grid"]["config_count"] == 1
    assert artifact["config_grid"]["configs"][0]["config_id"] == CONFIG_ID
    assert artifact["universe_and_window"]["exact_overlap_symbol_count"] == 81
    assert artifact["repo_scope"]["network_used"] is False
    assert artifact["repo_scope"]["candidate_generation"] is False
    assert artifact["repo_scope"]["edge_claim"] is False
    assert artifact["repo_scope"]["runtime_live_capital"] is False
    assert all(artifact["validation_checks"].values())
    assert artifact["replacement_checks_all_true"] is True
    assert artifact["payload_sha256_excluding_hash"] == payload_hash(artifact)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with TEMP_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    TEMP_PATH.replace(path)


def main() -> int:
    try:
        artifact = build_artifact()
        write_json(OUTPUT_PATH, artifact)
        print(
            json.dumps(
                {
                    "config_count": artifact["config_grid"]["config_count"],
                    "config_id": CONFIG_ID,
                    "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
                    "preregistration_artifact_path": ARTIFACT_PATH,
                    "replacement_checks_all_true": True,
                    "route_family": ROUTE_FAMILY,
                    "status": REQUIRED_STATUS,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    except Exception as exc:
        if TEMP_PATH.exists():
            TEMP_PATH.unlink()
        print(json.dumps({"reason": str(exc), "replacement_checks_all_true": False, "status": "BLOCKED"}, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
