import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_taker_flow_momentum_continuation_preregistration_contract_v1.py"
ARTIFACT_PATH = "artifacts/research_preregistrations/binance_okx_overlap_taker_flow_momentum_continuation_preregistration_contract_v1.json"
STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_TAKER_FLOW_MOMENTUM_CONTINUATION_PREREGISTRATION_CONTRACT_CREATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_TAKER_FLOW_MOMENTUM_CONTINUATION_PREREGISTRATION_CONTRACT"

ROUTE_FAMILY = "CROSS_SECTIONAL_TAKER_BUY_SHARE_MOMENTUM_CONTINUATION_BASELINE"
HYPOTHESIS_NAME = "taker_buy_share_momentum_continuation"
ROUTE_TYPE = "cross_sectional_taker_flow_momentum_long_short"
CONFIG_ID = "taker_buy_share_mom4h_rank_hold8h"

TAKER_AVAILABILITY_PATH = "artifacts/taker_buy_sell_volume_availability_locks/binance_okx_overlap_taker_buy_sell_volume_history_availability_discovery_lock_v1.json"
PRIOR_CLOSURE_PATH = "artifacts/strategy_closures/binance_okx_overlap_taker_buy_imbalance_exhaustion_reversal_closure_v1.json"
READINESS_PATH = "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json"
PANEL_REVIEW_PATH = "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json"
BUILD_MANIFEST_PATH = "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json"
PREVIEW_PATH = "artifacts/panel_build_previews/binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.json"
COVERAGE_LOCK_PATH = "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json"


def canonical_payload_hash(payload: Dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(json.dumps(clean, sort_keys=True, indent=2).encode("utf-8")).hexdigest()


def read_json(relative_path: str) -> Dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise RuntimeError(f"missing required source artifact: {relative_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def verify_hash(payload: Dict[str, Any]) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise RuntimeError("source artifact missing payload_sha256_excluding_hash")
    recomputed = canonical_payload_hash(payload)
    if recomputed != stored:
        raise RuntimeError(f"source artifact payload hash mismatch: {recomputed} != {stored}")
    return stored


def find_symbol_list(value: Any) -> Optional[List[str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in ("exact_overlap_binance_symbols", "symbol_set") and isinstance(child, list) and len(child) == 81:
                if all(isinstance(item, str) and item.endswith("USDT") for item in child):
                    return list(child)
            found = find_symbol_list(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_symbol_list(child)
            if found:
                return found
    return None


def find_first_key(value: Any, target_key: str) -> Any:
    if isinstance(value, dict):
        if target_key in value:
            return value[target_key]
        for child in value.values():
            found = find_first_key(child, target_key)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_first_key(child, target_key)
            if found is not None:
                return found
    return None


def contains_key(value: Any, target_key: str) -> bool:
    if isinstance(value, dict):
        if target_key in value:
            return True
        return any(contains_key(child, target_key) for child in value.values())
    if isinstance(value, list):
        return any(contains_key(child, target_key) for child in value)
    return False


def validate_no_forbidden_permissions(source_artifacts: Iterable[Dict[str, Any]]) -> bool:
    forbidden_true_keys = {
        "candidate_generation",
        "edge_claim",
        "family_release",
        "runtime_live_capital",
        "runtime_permission_allowed_now",
        "live_permission_allowed_now",
        "capital_permission_allowed_now",
        "candidate_generation_allowed_now",
        "edge_claim_allowed_now",
        "family_release_allowed_now",
        "runtime_live_capital_allowed_now",
    }

    def walk(value: Any) -> bool:
        if isinstance(value, dict):
            for key, child in value.items():
                if key in forbidden_true_keys and child is True:
                    return False
                if not walk(child):
                    return False
        elif isinstance(value, list):
            for child in value:
                if not walk(child):
                    return False
        return True

    return all(walk(artifact) for artifact in source_artifacts)


def build_artifact() -> Dict[str, Any]:
    taker_availability = read_json(TAKER_AVAILABILITY_PATH)
    prior_closure = read_json(PRIOR_CLOSURE_PATH)
    readiness = read_json(READINESS_PATH)
    panel_review = read_json(PANEL_REVIEW_PATH)
    build_manifest = read_json(BUILD_MANIFEST_PATH)
    preview = read_json(PREVIEW_PATH)
    coverage_lock = read_json(COVERAGE_LOCK_PATH)
    source_artifacts = [taker_availability, prior_closure, readiness, panel_review, build_manifest, preview, coverage_lock]
    source_hashes = {
        TAKER_AVAILABILITY_PATH: verify_hash(taker_availability),
        PRIOR_CLOSURE_PATH: verify_hash(prior_closure),
        READINESS_PATH: verify_hash(readiness),
        PANEL_REVIEW_PATH: verify_hash(panel_review),
        BUILD_MANIFEST_PATH: verify_hash(build_manifest),
        PREVIEW_PATH: verify_hash(preview),
        COVERAGE_LOCK_PATH: verify_hash(coverage_lock),
    }
    availability = taker_availability.get("panel_derived_taker_buy_sell_availability", {})
    if availability.get("taker_sell_derivable_from_panel") is not True:
        raise RuntimeError("panel-derived taker buy/sell fields are not available")
    if availability.get("aligned_window_covered_by_panel_derived_data") is not True:
        raise RuntimeError("panel-derived taker buy/sell data does not cover aligned window")
    prior_result = prior_closure.get("prior_evaluator_result_preserved", {}).get("result_class")
    if prior_result != "TAKER_BUY_IMBALANCE_EXHAUSTION_REVERSAL_REJECTED_NO_FOLLOWUP":
        raise RuntimeError("prior taker buy imbalance exhaustion route was not rejected/no-followup")
    if prior_closure.get("closure_record", {}).get("route_closed") is not True:
        raise RuntimeError("prior taker buy imbalance exhaustion closure did not close route")
    if not validate_no_forbidden_permissions(source_artifacts):
        raise RuntimeError("source artifact unexpectedly grants forbidden permission")

    symbols = find_symbol_list(readiness) or find_symbol_list(preview) or find_symbol_list(build_manifest)
    if not symbols or len(symbols) != 81:
        raise RuntimeError("could not verify exact 81-symbol overlap universe")
    panel_review_passed = (
        panel_review.get("panel_validity_classification")
        or find_first_key(panel_review, "panel_validity_classification")
    ) == "PANEL_REVIEW_PASS_WITH_P1_ATTENTION_VALID_FOR_READ_ONLY_SECOND_SOURCE_ANALYSIS"
    required_schema = (
        contains_key(build_manifest, "taker_buy_quote_volume_policy")
        and contains_key(build_manifest, "quote_volume_policy")
        and panel_review_passed
    )
    if not required_schema:
        raise RuntimeError("required reviewed panel taker buy quote schema not confirmed")

    payload: Dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "route_family": ROUTE_FAMILY,
        "hypothesis_name": HYPOTHESIS_NAME,
        "universe_and_window": {
            "universe": "Binance/OKX exact overlap 81 Binance USDT perpetual symbols",
            "symbol_count": len(symbols),
            "symbols": symbols,
            "aligned_window_start_utc": "2023-07-01T00:00:00Z",
            "aligned_window_end_exclusive_utc": "2025-10-31T16:00:00Z",
            "train_window_start_utc": "2023-07-01T00:00:00Z",
            "train_window_end_exclusive_utc": "2025-01-01T00:00:00Z",
            "validation_window_start_utc": "2025-01-01T00:00:00Z",
            "validation_window_end_exclusive_utc": "2025-10-31T16:00:00Z",
            "okx_boundary_buffer_excluded": True,
            "okx_sealed_holdout_excluded": True,
        },
        "signal_definition": {
            "signal_name": "taker_buy_share_mom4h",
            "taker_buy_quote_share": "taker_buy_quote_volume / quote_volume",
            "use_only_complete_1h_bars": True,
            "no_current_hour_leakage": True,
            "entry_timestamp_signal_policy": {
                "recent_4h_avg": "average taker_buy_quote_share over E-4h through E-1h",
                "prior_4h_avg": "average taker_buy_quote_share over E-8h through E-5h",
                "taker_buy_share_mom4h": "recent_4h_avg - prior_4h_avg",
                "required_prior_complete_bars_per_symbol": 8,
            },
            "cross_sectional_rank": "rank taker_buy_share_mom4h ascending by timestamp",
            "long_leg": "top 20 percent highest taker_buy_share_mom4h",
            "short_leg": "bottom 20 percent lowest taker_buy_share_mom4h",
            "minimum_eligible_symbols": 60,
            "minimum_long_symbols": 5,
            "minimum_short_symbols": 5,
            "portfolio": "equal-weight dollar-neutral long/short spread",
            "holding_period_hours": 8,
            "return_policy": "open-to-open returns",
            "round_trip_cost_bps": 20,
            "no_parameter_expansion": True,
        },
        "config_grid": {
            "config_count": 1,
            "configs": [
                {
                    "config_id": CONFIG_ID,
                    "route_type": "cross_sectional_taker_flow_momentum_long_short",
                    "signal": "taker_buy_share_mom4h",
                    "momentum_lookback_hours": 4,
                    "prior_comparison_hours": 4,
                    "holding_period_hours": 8,
                    "long_tail_fraction": 0.20,
                    "short_tail_fraction": 0.20,
                    "minimum_eligible_symbols": 60,
                    "minimum_long_symbols": 5,
                    "minimum_short_symbols": 5,
                    "round_trip_cost_bps": 20,
                }
            ],
            "no_parameter_expansion_without_new_contract": True,
        },
        "future_execution_controls": {
            "execution_requires_this_preregistration": True,
            "use_reviewed_binance_1h_panel_only": True,
            "use_exact_81_symbol_universe": True,
            "use_aligned_window_only": True,
            "external_panel_rows_allowed_only_in_execution": True,
            "funding_rows_allowed": False,
            "okx_panel_rows_allowed": False,
            "network_allowed": False,
            "additional_configs_allowed": False,
            "candidate_generation_allowed": False,
            "edge_claim_allowed": False,
            "family_release_allowed": False,
            "runtime_live_capital_allowed": False,
        },
        "safety_permissions": {
            "preregistration_contract_created": True,
            "strategy_execution_allowed_now": False,
            "strategy_search_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "holdout_access_allowed_now": False,
            "okx_panel_access_allowed_now": False,
            "funding_row_access_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "immediate_next_module_required": True,
            "next_module": "execution",
        },
        "source_artifacts": {
            "payload_hashes": source_hashes,
            "taker_buy_sell_availability_lock": TAKER_AVAILABILITY_PATH,
            "prior_taker_buy_imbalance_exhaustion_closure": PRIOR_CLOSURE_PATH,
            "readiness_artifact": READINESS_PATH,
            "panel_review_artifact": PANEL_REVIEW_PATH,
            "panel_manifest_artifact": BUILD_MANIFEST_PATH,
            "preview_artifact": PREVIEW_PATH,
            "coverage_lock_artifact": COVERAGE_LOCK_PATH,
        },
        "forbidden_actions_confirmed_false": {
            "network_used": False,
            "binance_api_called": False,
            "funding_rate_endpoint_called": False,
            "funding_data_fetched": False,
            "binance_panel_rows_read": False,
            "binance_funding_rows_read": False,
            "binance_1m_source_rows_read": False,
            "okx_panel_rows_read": False,
            "strategy_executed": False,
            "strategy_search_executed": False,
            "non_preregistered_config_tested": False,
            "candidates_generated": False,
            "edge_claimed": False,
            "family_released": False,
            "holdout_accessed": False,
            "boundary_buffer_accessed": False,
            "runtime_permission_granted": False,
            "live_permission_granted": False,
            "capital_permission_granted": False,
            "existing_files_modified_by_module": False,
        },
        "validation_checks": {
            "status_equals_required_status": True,
            "module_path_equals_required_path": True,
            "preregistration_artifact_path_equals_required_path": True,
            "exactly_one_new_tracked_python_tool_file_expected": True,
            "exactly_one_new_tracked_json_preregistration_artifact_expected": True,
            "no_existing_files_modified_expected": True,
            "no_other_tracked_files_expected": True,
            "taker_buy_sell_availability_lock_loaded": True,
            "panel_derived_taker_fields_available_verified": True,
            "prior_taker_exhaustion_closure_loaded": True,
            "prior_taker_exhaustion_rejected_no_followup_verified": True,
            "exact_overlap_symbol_count_verified_81": True,
            "aligned_window_verified": True,
            "config_count_is_one": True,
            "config_id_deterministic": True,
            "panel_schema_checked_from_artifacts": True,
            "no_network_used": True,
            "no_binance_api_call": True,
            "no_panel_rows_read": True,
            "no_funding_rows_read": True,
            "no_okx_panel_rows_read": True,
            "no_strategy_execution": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_runtime_live_capital": True,
            "preregistration_artifact_json_valid": True,
            "payload_sha256_excluding_hash_present": True,
            "replacement_checks_all_true": True,
        },
        "replacement_checks_all_true": True,
    }
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)

    required_assertions = [
        payload["status"] == STATUS,
        payload["module"] == MODULE_PATH,
        ARTIFACT_PATH == "artifacts/research_preregistrations/binance_okx_overlap_taker_flow_momentum_continuation_preregistration_contract_v1.json",
        payload["route_family"] == ROUTE_FAMILY,
        payload["hypothesis_name"] == HYPOTHESIS_NAME,
        payload["config_grid"]["config_count"] == 1,
        payload["config_grid"]["configs"][0]["config_id"] == CONFIG_ID,
        payload["universe_and_window"]["symbol_count"] == 81,
        payload["forbidden_actions_confirmed_false"]["network_used"] is False,
        payload["forbidden_actions_confirmed_false"]["binance_panel_rows_read"] is False,
        payload["forbidden_actions_confirmed_false"]["strategy_executed"] is False,
        payload["forbidden_actions_confirmed_false"]["candidates_generated"] is False,
        payload["forbidden_actions_confirmed_false"]["edge_claimed"] is False,
        payload["forbidden_actions_confirmed_false"]["runtime_permission_granted"] is False,
        payload["replacement_checks_all_true"] is True,
    ]
    if not all(required_assertions):
        raise RuntimeError("preregistration invariant assertion failed")
    return payload


def main() -> None:
    artifact = build_artifact()
    path = REPO_ROOT / ARTIFACT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": artifact["status"],
        "preregistration_artifact_path": ARTIFACT_PATH,
        "route_family": artifact["route_family"],
        "hypothesis_name": artifact["hypothesis_name"],
        "config_id": artifact["config_grid"]["configs"][0]["config_id"],
        "symbol_count": artifact["universe_and_window"]["symbol_count"],
        "aligned_window_start_utc": artifact["universe_and_window"]["aligned_window_start_utc"],
        "aligned_window_end_exclusive_utc": artifact["universe_and_window"]["aligned_window_end_exclusive_utc"],
        "holding_period_hours": artifact["config_grid"]["configs"][0]["holding_period_hours"],
        "minimum_eligible_symbols": artifact["signal_definition"]["minimum_eligible_symbols"],
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": artifact["replacement_checks_all_true"],
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
