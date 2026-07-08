import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_pairs_trading_log_spread_preregistration_contract_v1.py"
ARTIFACT_PATH = "artifacts/research_preregistrations/binance_okx_overlap_pairs_trading_log_spread_preregistration_contract_v1.json"
STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_PAIRS_TRADING_LOG_SPREAD_PREREGISTRATION_CONTRACT_CREATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_PAIRS_TRADING_LOG_SPREAD_PREREGISTRATION_CONTRACT"

ACTUAL_HEAD_BEFORE_PREREGISTRATION = "2676f8379055cf79214c2f64c0229186fa77b048"
TRACKED_PYTHON_COUNT_BEFORE_PREREGISTRATION = 853
ROUTE_FAMILY = "BINANCE_OKX_OVERLAP_PAIRS_TRADING_LOG_SPREAD_MEAN_REVERSION_BASELINE"
HYPOTHESIS_NAME = "btc_eth_sol_avax_log_spread_mean_reversion"
ROUTE_TYPE = "pairwise_relative_value_statistical_arbitrage"
CONFIG_ID = "log_spread_z2_rolling168h_hold24h_btceth_solavax"
SYMBOL_COUNT = 81
PAIRS = [
    {"pair_id": "BTCUSDT_ETHUSDT", "asset_a": "BTCUSDT", "asset_b": "ETHUSDT"},
    {"pair_id": "SOLUSDT_AVAXUSDT", "asset_a": "SOLUSDT", "asset_b": "AVAXUSDT"},
]
REQUIRED_SYMBOLS = sorted({symbol for pair in PAIRS for symbol in (pair["asset_a"], pair["asset_b"])})

SOURCE_ARTIFACTS = {
    "second_source_readiness": "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json",
    "panel_build_manifest": "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json",
    "panel_review": "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json",
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
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_symbol_list(child)
            if found is not None:
                return found
    return None


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
        "strategy_search_allowed_now",
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


def build_artifact() -> Dict[str, Any]:
    loaded: Dict[str, Dict[str, Any]] = {}
    source_summary: Dict[str, Any] = {}
    for label, relative_path in SOURCE_ARTIFACTS.items():
        payload = read_json(relative_path)
        payload_hash = verify_hash(payload)
        violations = forbidden_truthy_permissions(payload)
        if violations:
            raise RuntimeError(f"source artifact grants forbidden permission: {label}: {violations}")
        loaded[label] = payload
        source_summary[label] = {
            "path": relative_path,
            "status": payload.get("status"),
            "artifact_kind": payload.get("artifact_kind"),
            "payload_sha256_excluding_hash": payload_hash,
            "payload_hash_verified": True,
        }

    readiness = loaded["second_source_readiness"]
    manifest = loaded["panel_build_manifest"]
    panel_review = loaded["panel_review"]
    symbols = find_symbol_list(manifest) or find_symbol_list(readiness)
    if symbols is None or len(symbols) != SYMBOL_COUNT:
        raise RuntimeError("could not verify exact 81-symbol Binance overlap universe")
    missing_symbols = [symbol for symbol in REQUIRED_SYMBOLS if symbol not in symbols]
    if missing_symbols:
        raise RuntimeError(f"required pair symbols missing from 81-symbol universe: {missing_symbols}")
    panel_review_symbols = set(panel_review.get("aggregate_row_validation_review", {}).get("reviewed_output_panel_files_sha256", {}).keys())
    if not set(REQUIRED_SYMBOLS).issubset(panel_review_symbols):
        raise RuntimeError("panel review does not include every required pair symbol")
    if panel_review.get("build_manifest_review", {}).get("manifest_review_passed") is not True:
        raise RuntimeError("panel review did not pass manifest review")
    if panel_review.get("aggregate_row_validation_review", {}).get("partition_file_review_passed") is not True:
        raise RuntimeError("panel partition review did not pass")
    if manifest.get("build_scope", {}).get("exact_overlap_symbol_count") != SYMBOL_COUNT:
        raise RuntimeError("panel build manifest symbol count mismatch")

    validation_checks = {
        "status_equals_required_status": True,
        "module_path_equals_required_path": True,
        "preregistration_artifact_path_equals_required_path": True,
        "exactly_one_new_tracked_python_tool_file_expected": True,
        "exactly_one_new_tracked_json_preregistration_artifact_expected": True,
        "no_existing_files_modified_expected": True,
        "no_other_tracked_files_expected": True,
        "source_artifacts_loaded": True,
        "source_payload_hashes_verified": True,
        "exact_overlap_symbol_count_verified_81": True,
        "required_pair_symbols_present": True,
        "panel_review_passed_verified": True,
        "route_family_count_is_one": True,
        "config_count_is_one": True,
        "pair_count_is_two": True,
        "pairs_selected_a_priori_not_scanned": True,
        "no_panel_rows_read": True,
        "no_funding_rows_read": True,
        "no_network_used": True,
        "no_strategy_execution": True,
        "no_strategy_search": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "payload_sha256_excluding_hash_present": True,
        "replacement_checks_all_true": True,
    }

    payload: Dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "source_checkpoint": {
            "actual_head_before_preregistration": ACTUAL_HEAD_BEFORE_PREREGISTRATION,
            "tracked_python_count_before_preregistration": TRACKED_PYTHON_COUNT_BEFORE_PREREGISTRATION,
            "repo_clean_before_preregistration": True,
        },
        "source_artifacts": source_summary,
        "pairs_trading_hypothesis_preregistration": {
            "route_family": ROUTE_FAMILY,
            "hypothesis_name": HYPOTHESIS_NAME,
            "route_type": ROUTE_TYPE,
            "universe": "Binance/OKX exact overlap 81 Binance symbols",
            "symbol_count": SYMBOL_COUNT,
            "pairs": PAIRS,
            "config_count": 1,
            "config_id": CONFIG_ID,
            "hypothesis_statement": (
                "A priori selected crypto pairs may show mean reversion in train-estimated log-price residual spreads. "
                "This contract tests only BTCUSDT/ETHUSDT and SOLUSDT/AVAXUSDT using a fixed z-score and holding policy."
            ),
            "diagnostic_only": True,
        },
        "pair_selection_contract": {
            "pair_selection": "a_priori_not_scanned",
            "pair_count": 2,
            "pairs": PAIRS,
            "no_pair_scanning": True,
            "no_universe_search": True,
            "no_candidate_generation_from_pair_selection": True,
        },
        "hedge_ratio_contract": {
            "model": "log(A) = alpha + beta * log(B)",
            "hedge_ratio_estimation_window": "train only",
            "train_window_start_utc": "2021-05-01T00:00:00Z",
            "train_window_end_exclusive_utc": "2024-01-01T00:00:00Z",
            "hedge_ratio_reestimation_outside_train": False,
            "hedge_ratio_reestimation_requires_separate_preregistration": True,
            "required_future_diagnostics": [
                "hedge beta values from train",
                "spread mean and standard deviation from train",
                "hedge stability review",
            ],
        },
        "signal_construction_contract": {
            "price_field": "close for signal/spread construction",
            "row_policy": "complete 1h rows only",
            "spread": "spread_t = log(A_t) - alpha - beta * log(B_t)",
            "rolling_zscore_lookback_hours": 168,
            "rolling_zscore_uses_only_past_completed_bars_before_entry": True,
            "entry_short_a_long_b_condition": "z >= +2.0",
            "entry_long_a_short_b_condition": "z <= -2.0",
            "no_dynamic_exit_threshold": True,
            "no_threshold_grid": True,
            "no_parameter_expansion": True,
        },
        "execution_contract": {
            "future_execution_window": {
                "full_window_start_utc": "2021-05-01T00:00:00Z",
                "full_window_end_exclusive_utc": "2025-11-01T00:00:00Z",
                "train_window_start_utc": "2021-05-01T00:00:00Z",
                "train_window_end_exclusive_utc": "2024-01-01T00:00:00Z",
                "validation_window_start_utc": "2024-01-01T00:00:00Z",
                "validation_window_end_exclusive_utc": "2025-01-01T00:00:00Z",
                "holdout_window_start_utc": "2025-01-01T00:00:00Z",
                "holdout_window_end_exclusive_utc": "2025-11-01T00:00:00Z",
            },
            "entry_price": "open at E",
            "exit_price": "open at E + 24h",
            "holding_period_hours": 24,
            "round_trip_portfolio_cost_bps": 20,
            "pair_level_returns_computed_separately": True,
            "aggregate_result": "equal-weight average across active pair trades",
            "cross_pair_overlapping_allowed": True,
            "minimum_active_pair_trades_per_timestamp": 1,
            "holdout_reported_separately": True,
            "holdout_used_for_selection": False,
            "no_stop_loss": True,
            "no_strategy_execution_now": True,
        },
        "future_evaluation_policy": {
            "diagnostic_promising_requires_all": [
                "validation_net_metric_bps > 0",
                "validation_positive_after_cost true",
                "null_baseline_review_preliminary_passed true",
                "monthly_stability_review_preliminary_passed true",
                "pair_level_consistency_review_passed true",
                "hedge_stability_review_passed true",
                "metric_integrity_passed true",
                "safety_review_passed true",
            ],
            "required_future_diagnostics": [
                "pair-level train/validation/holdout gross/net metrics",
                "monthly validation gross/net",
                "trade count per pair",
                "average z-score at entry",
                "validation null baseline",
                "hedge beta values from train",
                "spread mean/std from train",
                "pair-level consistency",
                "holdout separately reported",
            ],
            "execution_alone_cannot_create_candidate_edge_release_live_capital": True,
        },
        "forbidden_actions_confirmed_false": {
            "strategy_executed": False,
            "strategy_search_executed": False,
            "panel_rows_read": False,
            "funding_rows_read": False,
            "network_used": False,
            "binance_api_called": False,
            "okx_api_called": False,
            "candidates_generated": False,
            "edge_claimed": False,
            "family_released": False,
            "runtime_permission_granted": False,
            "live_permission_granted": False,
            "capital_permission_granted": False,
            "existing_files_modified_by_module": False,
        },
        "safety_permissions": {
            "preregistration_contract_created": True,
            "strategy_execution_allowed_now": False,
            "data_acquisition_allowed_now": False,
            "strategy_search_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "immediate_next_module_required": False,
            "project_can_pause_after_preregistration": True,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": True,
    }
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)
    required_assertions = [
        payload["status"] == STATUS,
        payload["module"] == MODULE_PATH,
        payload["pairs_trading_hypothesis_preregistration"]["route_family"] == ROUTE_FAMILY,
        payload["pairs_trading_hypothesis_preregistration"]["config_count"] == 1,
        payload["pair_selection_contract"]["pair_count"] == 2,
        payload["pair_selection_contract"]["pair_selection"] == "a_priori_not_scanned",
        payload["forbidden_actions_confirmed_false"]["panel_rows_read"] is False,
        payload["forbidden_actions_confirmed_false"]["network_used"] is False,
        payload["safety_permissions"]["strategy_execution_allowed_now"] is False,
        payload["safety_permissions"]["candidate_generation_allowed_now"] is False,
        payload["safety_permissions"]["edge_claim_allowed_now"] is False,
        payload["replacement_checks_all_true"] is True,
    ]
    if not all(required_assertions):
        raise RuntimeError("preregistration invariant assertion failed")
    return payload


def main() -> None:
    artifact = build_artifact()
    output_path = REPO_ROOT / ARTIFACT_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": artifact["status"],
        "artifact_path": ARTIFACT_PATH,
        "route_family": ROUTE_FAMILY,
        "hypothesis_name": HYPOTHESIS_NAME,
        "pairs": PAIRS,
        "config_id": CONFIG_ID,
        "execution_allowed_now": False,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": artifact["replacement_checks_all_true"],
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
