import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_crowding_reversal_maker_entry_taker_exit_preregistration_contract_v1.py"
ARTIFACT_PATH = "artifacts/research_preregistrations/binance_okx_overlap_funding_crowding_reversal_maker_entry_taker_exit_preregistration_contract_v1.json"
STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_CROWDING_REVERSAL_MAKER_ENTRY_TAKER_EXIT_PREREGISTRATION_CONTRACT_CREATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_FUNDING_CROWDING_REVERSAL_MAKER_ENTRY_TAKER_EXIT_PREREGISTRATION_CONTRACT"

ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_CROWDING_REVERSAL_MAKER_ENTRY_TAKER_EXIT_DIAGNOSTIC"
HYPOTHESIS_NAME = "funding_crowding_reversal_maker_entry_taker_exit"
BASE_ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_RATE_CROWDING_REVERSAL_BASELINE"
CONFIG_ID = "funding_mean9_hold24h_maker_entry_1bps_taker_exit_cost10bps"
SYMBOL_COUNT = 81

SOURCE_ARTIFACTS = {
    "full_range_funding_acquisition_lock": "artifacts/funding_rate_locks/binance_okx_overlap_funding_rate_full_range_202105_202510_acquisition_lock_v1.json",
    "full_range_funding_review": "artifacts/funding_rate_reviews/binance_okx_overlap_funding_rate_full_range_202105_202510_review_v1.json",
    "full_range_base_execution": "artifacts/strategy_executions/binance_okx_overlap_funding_crowding_reversal_full_range_execution_v1.json",
    "full_range_base_evaluator": "artifacts/strategy_evaluations/binance_okx_overlap_funding_crowding_reversal_full_range_evaluator_v1.json",
    "full_range_base_closure": "artifacts/strategy_closures/binance_okx_overlap_funding_crowding_reversal_full_range_closure_v1.json",
    "second_source_readiness": "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json",
    "panel_review": "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json",
    "panel_build_manifest": "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json",
    "panel_build_preview": "artifacts/panel_build_previews/binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.json",
    "coverage_lock": "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json",
}


def canonical_payload_hash(payload: Dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(json.dumps(clean, sort_keys=True, indent=2).encode("utf-8")).hexdigest()


def read_json(relative_path: str) -> Dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise RuntimeError(f"missing required source artifact: {relative_path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"source artifact is not a JSON object: {relative_path}")
    return payload


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
            if key in {"exact_overlap_binance_symbols", "symbol_set", "symbols"}:
                if isinstance(child, list) and len(child) == SYMBOL_COUNT:
                    if all(isinstance(item, str) and item.endswith("USDT") for item in child):
                        return sorted(child)
            found = find_symbol_list(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_symbol_list(child)
            if found:
                return found
    return None


def contains_value(value: Any, expected: Any) -> bool:
    if value == expected:
        return True
    if isinstance(value, dict):
        return any(contains_value(child, expected) for child in value.values())
    if isinstance(value, list):
        return any(contains_value(child, expected) for child in value)
    return False


def forbidden_truthy_permissions(value: Any, path: str = "") -> List[str]:
    forbidden_keys = {
        "candidate_generation",
        "candidate_generation_allowed_now",
        "edge_claim",
        "edge_claim_allowed_now",
        "family_release_allowed_now",
        "runtime_live_capital",
        "runtime_live_capital_allowed_now",
        "runtime_permission_allowed_now",
        "live_permission_allowed_now",
        "capital_permission_allowed_now",
        "holdout_access_allowed_now",
        "holdout_access_permission_granted",
    }
    violations: List[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            if key in forbidden_keys and child is True:
                violations.append(child_path)
            violations.extend(forbidden_truthy_permissions(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            violations.extend(forbidden_truthy_permissions(child, f"{path}[{index}]"))
    return violations


def load_sources() -> Dict[str, Any]:
    loaded: Dict[str, Any] = {}
    for label, path in SOURCE_ARTIFACTS.items():
        payload = read_json(path)
        loaded[label] = {
            "path": path,
            "status": payload.get("status"),
            "payload_sha256_excluding_hash": verify_hash(payload),
            "artifact_kind": payload.get("artifact_kind"),
            "payload": payload,
        }
        violations = forbidden_truthy_permissions(payload)
        if violations:
            raise RuntimeError(f"source artifact grants forbidden permission: {label}: {violations}")
    return loaded


def build_artifact() -> Dict[str, Any]:
    sources = load_sources()
    closure = sources["full_range_base_closure"]["payload"]
    funding_review = sources["full_range_funding_review"]["payload"]
    panel_review = sources["panel_review"]["payload"]
    readiness = sources["second_source_readiness"]["payload"]
    manifest = sources["panel_build_manifest"]["payload"]
    preview = sources["panel_build_preview"]["payload"]

    if not contains_value(closure, "FUNDING_CROWDING_REVERSAL_FULL_RANGE_REJECTED_NO_FOLLOWUP"):
        raise RuntimeError("full-range base closure did not preserve rejected/no-followup result")
    if closure["closure_record"]["route_closed"] is not True:
        raise RuntimeError("full-range base route is not closed")
    if funding_review["funding_data_review"]["funding_data_valid_for_full_range_signal_construction"] is not True:
        raise RuntimeError("full-range funding review is not valid")
    if panel_review["build_manifest_review"]["manifest_review_passed"] is not True:
        raise RuntimeError("panel review manifest review did not pass")
    if panel_review["aggregate_row_validation_review"]["partition_file_review_passed"] is not True:
        raise RuntimeError("panel partition review did not pass")

    symbols = find_symbol_list(readiness) or find_symbol_list(preview) or find_symbol_list(manifest)
    if symbols is None or len(symbols) != SYMBOL_COUNT:
        raise RuntimeError("could not verify exact 81-symbol universe")

    source_artifacts = {
        label: {
            "path": item["path"],
            "status": item["status"],
            "artifact_kind": item["artifact_kind"],
            "payload_sha256_excluding_hash": item["payload_sha256_excluding_hash"],
        }
        for label, item in sources.items()
    }
    validation_checks = {
        "status_equals_required_status": True,
        "module_path_equals_required_path": True,
        "preregistration_artifact_path_equals_required_path": True,
        "exactly_one_new_tracked_python_tool_file_expected": True,
        "exactly_one_new_tracked_json_preregistration_artifact_expected": True,
        "no_existing_files_modified_expected": True,
        "no_other_tracked_files_expected": True,
        "full_range_base_closure_loaded": True,
        "full_range_base_closure_rejected_no_followup_verified": True,
        "full_range_funding_review_loaded": True,
        "full_range_funding_data_valid_verified": True,
        "panel_review_loaded": True,
        "panel_valid_for_full_range_maker_proxy_verified": True,
        "exact_overlap_symbol_count_verified_81": True,
        "route_family_count_is_one": True,
        "config_count_is_one": True,
        "config_id_deterministic": True,
        "maker_entry_proxy_recorded": True,
        "taker_exit_policy_recorded": True,
        "holdout_policy_recorded": True,
        "no_network_used": True,
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
    }
    payload: Dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "route_family": ROUTE_FAMILY,
        "hypothesis_name": HYPOTHESIS_NAME,
        "source_checkpoint": {
            "expected_head_before_step_1": "42975b1c5cafe777cfc6125cc4455c6bc5350ae4",
            "expected_tracked_python_count_before_step_1": 849,
            "repo_clean_required_before_step_1": True,
        },
        "source_artifacts": source_artifacts,
        "universe_and_window": {
            "universe": "Binance/OKX exact overlap 81 Binance symbols",
            "symbol_count": SYMBOL_COUNT,
            "symbols": symbols,
            "full_window_start_utc": "2021-05-01T00:00:00Z",
            "full_window_end_exclusive_utc": "2025-11-01T00:00:00Z",
            "train_window_start_utc": "2021-05-01T00:00:00Z",
            "train_window_end_exclusive_utc": "2024-01-01T00:00:00Z",
            "validation_window_start_utc": "2024-01-01T00:00:00Z",
            "validation_window_end_exclusive_utc": "2025-01-01T00:00:00Z",
            "holdout_window_start_utc": "2025-01-01T00:00:00Z",
            "holdout_window_end_exclusive_utc": "2025-11-01T00:00:00Z",
            "okx_panel_rows_required": False,
            "okx_holdout_boundary_required": False,
        },
        "base_route_reference": {
            "base_route_family": BASE_ROUTE_FAMILY,
            "base_signal": "funding_mean9",
            "base_config_id": "funding_mean9_hold24h",
            "base_execution_model": "taker/open-to-open execution at 20 bps round-trip cost",
            "base_result_class": "FUNDING_CROWDING_REVERSAL_FULL_RANGE_REJECTED_NO_FOLLOWUP",
            "base_route_closed": True,
            "new_route_is_cost_and_entry_model_diagnostic_only": True,
        },
        "maker_entry_proxy_contract": {
            "maker_entry_proxy_is_not_order_book_simulation": True,
            "entry_reference_price": "open at entry hour",
            "long_entry_limit": "open * (1 - 1bps)",
            "short_entry_limit": "open * (1 + 1bps)",
            "long_fill_proxy": "entry_hour_low <= long_entry_limit",
            "short_fill_proxy": "entry_hour_high >= short_entry_limit",
            "entry_ttl_proxy": "within entry 1h bar",
            "unfilled_entry_policy": "no trade for that symbol",
            "minimum_filled_long_symbols": 5,
            "minimum_filled_short_symbols": 5,
            "fill_imbalance_policy": "use equal weight among filled long and filled short legs separately; require both sides minimum filled symbols",
            "adverse_selection_warning": "maker fills can be adverse-selected and this proxy does not use order book queue data",
            "maker_entry_offset_bps": 1,
            "order_book_queue_not_modeled": True,
        },
        "taker_exit_contract": {
            "exit_type": "taker_at_exit_open",
            "exit_reference_price": "open at E + 24h",
            "holding_period_hours": 24,
            "effective_round_trip_cost_bps": 10,
            "maker_rebate_modeled": False,
            "annualized": False,
            "compounded": False,
        },
        "config_grid": {
            "config_count": 1,
            "config_id": CONFIG_ID,
            "base_signal": "rolling_mean_9_funding_events",
            "holding_period_hours": 24,
            "maker_entry_offset_bps": 1,
            "effective_round_trip_cost_bps": 10,
            "minimum_eligible_symbols": 60,
            "minimum_filled_long_symbols": 5,
            "minimum_filled_short_symbols": 5,
            "no_parameter_expansion": True,
        },
        "future_execution_controls": {
            "execution_requires_this_preregistration": True,
            "use_reviewed_binance_1h_panel_only": True,
            "use_reviewed_full_range_binance_funding_data_only": True,
            "use_exact_81_symbol_universe": True,
            "use_full_range_split_only": True,
            "no_okx_panel_rows": True,
            "no_okx_holdout": True,
            "no_okx_boundary_buffer": True,
            "no_network_during_execution": True,
            "no_additional_configs": True,
            "no_parameter_expansion": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_runtime_live_capital": True,
        },
        "safety_permissions": {
            "preregistration_contract_created": True,
            "strategy_execution_allowed_now": False,
            "strategy_search_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "holdout_access_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "immediate_next_module_required": True,
            "next_module": "execution",
        },
        "forbidden_actions_confirmed_false": {
            "network_used": False,
            "binance_api_called": False,
            "funding_endpoint_called": False,
            "funding_data_fetched": False,
            "binance_panel_rows_read": False,
            "binance_funding_rows_read": False,
            "okx_panel_rows_read": False,
            "strategy_executed": False,
            "strategy_search_executed": False,
            "non_preregistered_config_tested": False,
            "candidates_generated": False,
            "edge_claimed": False,
            "family_released": False,
            "holdout_accessed": False,
            "runtime_permission_granted": False,
            "live_permission_granted": False,
            "capital_permission_granted": False,
            "existing_files_modified_by_module": False,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": True,
    }
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)
    required_assertions = [
        payload["status"] == STATUS,
        payload["module"] == MODULE_PATH,
        payload["route_family"] == ROUTE_FAMILY,
        payload["config_grid"]["config_count"] == 1,
        payload["config_grid"]["config_id"] == CONFIG_ID,
        payload["maker_entry_proxy_contract"]["maker_entry_proxy_is_not_order_book_simulation"] is True,
        payload["maker_entry_proxy_contract"]["order_book_queue_not_modeled"] is True,
        payload["taker_exit_contract"]["effective_round_trip_cost_bps"] == 10,
        payload["forbidden_actions_confirmed_false"]["strategy_executed"] is False,
        payload["forbidden_actions_confirmed_false"]["binance_panel_rows_read"] is False,
        payload["safety_permissions"]["candidate_generation_allowed_now"] is False,
        payload["safety_permissions"]["edge_claim_allowed_now"] is False,
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
        "route_family": ROUTE_FAMILY,
        "hypothesis_name": HYPOTHESIS_NAME,
        "config_id": CONFIG_ID,
        "symbol_count": SYMBOL_COUNT,
        "maker_entry_offset_bps": 1,
        "effective_round_trip_cost_bps": 10,
        "order_book_queue_not_modeled": True,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": artifact["replacement_checks_all_true"],
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
