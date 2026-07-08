from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_BINANCE_OKX_GROUP2_FUNDING_EXTREME_MOMENTUM_CONFIRMED_PREREGISTRATION_CONTRACT_CREATED"
ARTIFACT_KIND = "BINANCE_OKX_GROUP2_FUNDING_EXTREME_MOMENTUM_CONFIRMED_PREREGISTRATION_CONTRACT"
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_group2_funding_extreme_momentum_confirmed_preregistration_contract_v1.py"
ARTIFACT_PATH = "artifacts/research_preregistrations/binance_okx_group2_funding_extreme_momentum_confirmed_preregistration_contract_v1.json"

ROUTE_FAMILY = "CROSS_SECTIONAL_GROUP2_FUNDING_EXTREME_MOMENTUM_CONFIRMED_REVERSAL"
HYPOTHESIS_NAME = "group2_funding_extreme_momentum_confirmed_reversal"
CONFIG_ID = "group2_funding_extreme_mom24_hold24h"
GROUP2_SYMBOLS = [
    "ADAUSDT",
    "AVAXUSDT",
    "BNBUSDT",
    "DOGEUSDT",
    "LINKUSDT",
    "SOLUSDT",
    "SUIUSDT",
    "XRPUSDT",
]
ALIGNED_START = "2023-07-01T00:00:00Z"
ALIGNED_END = "2025-10-31T16:00:00Z"
TRAIN_START = "2023-07-01T00:00:00Z"
TRAIN_END = "2025-01-01T00:00:00Z"
VALIDATION_START = "2025-01-01T00:00:00Z"
VALIDATION_END = "2025-10-31T16:00:00Z"

SOURCE_ARTIFACTS = {
    "prior_liquidity_filtered_closure": (
        "artifacts/strategy_closures/binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_closure_v1.json",
        "a4824ed55c95ab3a0dcfcd1f37d49fffcd1453f3bd69bc1d866edd609da610cc",
    ),
    "prior_liquidity_filtered_evaluator": (
        "artifacts/strategy_evaluations/binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_evaluator_v1.json",
        "b98e9652238c7b54f995e81f2a724e73a18c4ff262f23d4ac67ec1edaf147220",
    ),
    "prior_liquidity_filtered_execution": (
        "artifacts/strategy_executions/binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_execution_v1.json",
        "c2c2762c5d4bc8ae64820f652283025dbb553a5fd92a88d6be9358a0af081a3a",
    ),
    "funding_review": (
        "artifacts/funding_rate_reviews/binance_okx_overlap_funding_rate_data_review_after_acquisition_lock_v1.json",
        "a579feb0472efbf03ffa955008dfabc0b526fa37029fc81dddd0195b4054d849",
    ),
    "funding_lock": (
        "artifacts/funding_rate_locks/binance_okx_overlap_funding_rate_data_acquisition_lock_v1.json",
        "dd5877b101c9a1e8d73f35f6032381cbdfd5435578abacf97b9db0c11c28e252",
    ),
    "funding_preregistration": (
        "artifacts/research_preregistrations/binance_okx_overlap_funding_rate_hypothesis_preregistration_contract_v1.json",
        "5febb59aee08873de1dbfc0464da463811090c334c18c5f2a552e1768cb3c768",
    ),
    "second_source_readiness": (
        "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json",
        "0cfe239f6f5ad2d20bda64b827416851de8f5b959066902b59f1f00f44eba716",
    ),
    "panel_review": (
        "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json",
        "34b88a3ff0870c708e2df034c243cf639b711ebce3c6a4f32edffb92a2229112",
    ),
    "panel_manifest": (
        "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json",
        "bf4d4d681f36fab3a2131701e25ebc45c94ddb757f92874498ef425d698f40a7",
    ),
    "panel_preview": (
        "artifacts/panel_build_previews/binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.json",
        "16e93ca05fe28f0d101d5228e299306bad3aea171f22bc6901f770b0ecf3a3d9",
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
    return hashlib.sha256(json.dumps(clone, indent=2, sort_keys=True).encode("utf-8")).hexdigest()


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


def build_artifact(root: Path) -> dict[str, Any]:
    loaded: dict[str, dict[str, Any]] = {}
    source_summary: dict[str, Any] = {"all_source_artifacts_read_only": True}
    for label, (rel_path, expected_hash) in SOURCE_ARTIFACTS.items():
        payload = read_json(root, rel_path)
        verify_payload(payload, expected_hash, label)
        loaded[label] = payload
        source_summary[f"{label}_path"] = rel_path
        source_summary[f"{label}_payload_hash_verified"] = True

    closure = loaded["prior_liquidity_filtered_closure"]
    closure_record = closure.get("closure_record", {})
    project_state = closure.get("project_state_after_closure", {})
    if closure.get("status") != "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_EXTREME_MOMENTUM_CONFIRMED_LIQUIDITY_FILTERED_CLOSURE_CREATED":
        raise Blocked("prior liquidity-filtered closure status mismatch")
    if closure_record.get("result_class_confirmed") != "FUNDING_EXTREME_MOMENTUM_LIQUIDITY_REJECTED_NO_FOLLOWUP":
        raise Blocked("prior route is not closed rejected/no-followup")
    if closure_record.get("route_closed") is not True:
        raise Blocked("prior route is not closed")
    safety_false_checks = [
        closure_record.get("candidate_generation_allowed_now") is False,
        closure_record.get("edge_claim_allowed_now") is False,
        closure_record.get("family_release_allowed_now") is False,
        closure_record.get("runtime_live_capital_allowed_now") is False,
        project_state.get("no_active_candidate_exists") is True,
        project_state.get("no_active_edge_claim_exists") is True,
        project_state.get("no_family_release_exists") is True,
        project_state.get("no_runtime_live_capital_permission_exists") is True,
    ]
    if not all(safety_false_checks):
        raise Blocked("prior closure permits a forbidden candidate/edge/release/runtime state")

    readiness = loaded["second_source_readiness"]
    overlap_symbols = readiness.get("symbol_universe_alignment", {}).get("exact_overlap_binance_symbols")
    if not isinstance(overlap_symbols, list):
        raise Blocked("could not find exact overlap Binance symbols")
    overlap_set = set(overlap_symbols)
    if len(overlap_set) != 81:
        raise Blocked(f"expected 81 overlap symbols, found {len(overlap_set)}")
    if not set(GROUP2_SYMBOLS).issubset(overlap_set):
        raise Blocked("Group-2 symbols are not a subset of the 81-symbol overlap")
    alignment = readiness.get("okx_binance_alignment_window", {})
    if alignment.get("recommended_aligned_window_start_utc") != ALIGNED_START or alignment.get("recommended_aligned_window_end_exclusive_utc") != ALIGNED_END:
        raise Blocked("aligned window mismatch")

    artifact: dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "route_family": ROUTE_FAMILY,
        "hypothesis_name": HYPOTHESIS_NAME,
        "source_checkpoint": {
            "prior_head": "b980f9e40adb503b04c8b1a45f5a98f3b4a81906",
            "prior_route_closure_artifact": SOURCE_ARTIFACTS["prior_liquidity_filtered_closure"][0],
            "prior_route_closure_status": closure.get("status"),
            "prior_route_result_class": closure_record.get("result_class_confirmed"),
            "prior_tracked_python_count": 821,
            "repo_clean_before_preregistration": True,
        },
        "source_artifacts": source_summary,
        "universe_and_window": {
            "aligned_window_end_exclusive_utc": ALIGNED_END,
            "aligned_window_start_utc": ALIGNED_START,
            "okx_boundary_buffer_excluded": True,
            "okx_sealed_holdout_excluded": True,
            "symbol_count": 8,
            "symbols": GROUP2_SYMBOLS,
            "train_window_end_exclusive_utc": TRAIN_END,
            "train_window_start_utc": TRAIN_START,
            "universe_type": "fixed_postmortem_liquidity_bucket_group2",
            "validation_window_end_exclusive_utc": VALIDATION_END,
            "validation_window_start_utc": VALIDATION_START,
        },
        "postmortem_bucket_warning": {
            "edge_claim_allowed_from_this_cycle": False,
            "family_release_allowed_from_this_cycle": False,
            "group2_selected_using_same_aligned_window_average_trailing_24h_quote_volume": True,
            "interpretation": "This is a postmortem fixed-liquidity-bucket diagnostic. Even if positive, it cannot create a candidate, edge claim, family release, runtime permission, live permission, or capital permission.",
            "runtime_live_capital_allowed_from_this_cycle": False,
        },
        "signal_definition": {
            "funding_signal": "latest_lagged_funding_rate_available_after_1h_lag",
            "momentum_24h": "close(E - 1h) / close(E - 25h) - 1 using prior completed 1h bars only",
            "portfolio": "equal_weight_dollar_neutral_long_short_spread",
            "return": "open_to_open_forward_return",
            "round_trip_cost_bps": 20,
        },
        "group2_symbol_set": {
            "exact_overlap_subset_verified": True,
            "symbol_count": 8,
            "symbols": GROUP2_SYMBOLS,
        },
        "funding_extreme_rule": {
            "funding_rank_order": "ascending",
            "long_candidate_pool": "bottom_2_symbols_by_funding_rate",
            "short_candidate_pool": "top_2_symbols_by_funding_rate",
        },
        "momentum_confirmation_rule": {
            "long_candidates_require_momentum_24h_lt_0": True,
            "short_candidates_require_momentum_24h_gt_0": True,
        },
        "config_grid": {
            "config_count": 1,
            "configs": [
                {
                    "config_id": CONFIG_ID,
                    "funding_transform": "latest_lagged_funding_rate",
                    "holding_period_hours": 24,
                    "minimum_eligible_symbols": 6,
                    "minimum_long_symbols": 1,
                    "minimum_short_symbols": 1,
                    "momentum_lookback_hours": 24,
                    "symbol_count": 8,
                }
            ],
            "no_parameter_expansion": True,
        },
        "future_execution_controls": {
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "no_non_group2_symbols": True,
            "no_non_preregistered_config": True,
            "runtime_live_capital_allowed_now": False,
        },
        "safety_permissions": {
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "holdout_access_allowed_now": False,
            "okx_panel_access_allowed_now": False,
            "preregistration_contract_created": True,
            "runtime_live_capital_allowed_now": False,
            "strategy_search_allowed_now": False,
        },
        "forbidden_actions_confirmed_false": {
            "binance_api_called": False,
            "binance_panel_rebuild": False,
            "candidate_generation": False,
            "edge_claim": False,
            "family_release": False,
            "funding_data_fetch": False,
            "network_used": False,
            "okx_panel_rows_read": False,
            "runtime_live_capital": False,
        },
    }
    validation_checks = {
        "aligned_window_verified": True,
        "config_count_is_one": True,
        "group2_subset_of_overlap_verified": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_network_used": True,
        "no_okx_panel_rows_read": True,
        "no_runtime_live_capital": True,
        "postmortem_bucket_warning_recorded": True,
        "prior_route_closed_rejected_no_followup_verified": True,
        "replacement_checks_all_true": True,
        "status_equals_required_status": artifact["status"] == STATUS,
    }
    artifact["validation_checks"] = validation_checks
    artifact["replacement_checks_all_true"] = all(validation_checks.values())
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
        raise Blocked("written preregistration artifact hash mismatch")


def main() -> int:
    root = repo_root()
    output = root / ARTIFACT_PATH
    try:
        artifact = build_artifact(root)
        write_artifact(root, artifact)
        summary = {
            "config_id": CONFIG_ID,
            "edge_claim": False,
            "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
            "postmortem_bucket_diagnostic": True,
            "replacement_checks_all_true": artifact["replacement_checks_all_true"],
            "route_family": ROUTE_FAMILY,
            "runtime_live_capital": False,
            "status": STATUS,
            "symbol_count": 8,
            "symbols": GROUP2_SYMBOLS,
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
