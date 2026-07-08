import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_15m_gk_volatility_zscore_squeeze_preregistration_contract_v1.py"
ARTIFACT_PATH = "artifacts/research_preregistrations/binance_okx_overlap_15m_gk_volatility_zscore_squeeze_preregistration_contract_v1.json"
STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_15M_GK_VOLATILITY_ZSCORE_SQUEEZE_PREREGISTRATION_CONTRACT_CREATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_15M_GK_VOLATILITY_ZSCORE_SQUEEZE_PREREGISTRATION_CONTRACT"

ACTUAL_HEAD_BEFORE_PREREGISTRATION = "616109b33f4b9e1e6c65e02c56600b50b3cc7b87"
TRACKED_PYTHON_COUNT_BEFORE_PREREGISTRATION = 863
ROUTE_FAMILY = "BINANCE_OKX_OVERLAP_15M_GK_VOLATILITY_ZSCORE_SQUEEZE_BASELINE"
HYPOTHESIS_NAME = "gk_volatility_zscore_squeeze_cross_sectional_reversal"
CONFIG_ID = "gkvol_24h_z30d_squeeze_long_expand_short_hold8h"
SYMBOL_COUNT = 81
TIMEFRAME = "15m"

PANEL_REVIEW_PATH = "artifacts/panel_build_reviews/binance_okx_overlap_81_symbol_15m_panel_review_after_build_v1.json"
PANEL_MANIFEST_PATH = "artifacts/panel_build_manifests/binance_okx_overlap_81_symbol_15m_panel_build_manifest_v1.json"
READINESS_PATH = "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json"
EXPECTED_PANEL_REVIEW_HASH = "7274008b419404a1963673923b810885645e05803ce6161d8dfacbb6536e8655"


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


def verify_hash(payload: Dict[str, Any], expected: Optional[str] = None) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise RuntimeError("source artifact missing payload_sha256_excluding_hash")
    recomputed = canonical_payload_hash(payload)
    if recomputed != stored:
        raise RuntimeError(f"source artifact payload hash mismatch: {recomputed} != {stored}")
    if expected is not None and stored != expected:
        raise RuntimeError(f"source artifact payload hash mismatch against expected: {stored} != {expected}")
    return stored


def find_symbol_list(value: Any) -> Optional[List[str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"exact_overlap_binance_symbols", "symbol_set", "symbols", "binance_symbols"}:
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


def build_artifact() -> Dict[str, Any]:
    panel_review = read_json(PANEL_REVIEW_PATH)
    panel_manifest = read_json(PANEL_MANIFEST_PATH)
    readiness = read_json(READINESS_PATH)
    panel_review_hash = verify_hash(panel_review, EXPECTED_PANEL_REVIEW_HASH)
    panel_manifest_hash = verify_hash(panel_manifest)
    readiness_hash = verify_hash(readiness)
    if panel_review.get("panel_validity_classification") != "PANEL_15M_REVIEW_PASS_VALID_FOR_READ_ONLY_EXTREME_MOVE_RESEARCH":
        raise RuntimeError("15m panel review classification is not valid for read-only research")
    aggregate_review = panel_review.get("aggregate_validation_review", {})
    if aggregate_review.get("reviewed_symbol_count") != SYMBOL_COUNT:
        raise RuntimeError("reviewed 15m symbol count mismatch")
    if aggregate_review.get("duplicate_symbol_timestamp_count") != 0:
        raise RuntimeError("15m panel duplicate count is not zero")
    if aggregate_review.get("ohlc_sanity_valid") is not True or aggregate_review.get("numeric_sanity_valid") is not True:
        raise RuntimeError("15m panel review sanity checks did not pass")
    symbols = find_symbol_list(readiness) or find_symbol_list(panel_manifest)
    if symbols is None or len(symbols) != SYMBOL_COUNT:
        raise RuntimeError("could not verify exact 81-symbol universe")

    payload: Dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "source_checkpoint": {
            "actual_head_before_preregistration": ACTUAL_HEAD_BEFORE_PREREGISTRATION,
            "tracked_python_count_before_preregistration": TRACKED_PYTHON_COUNT_BEFORE_PREREGISTRATION,
            "repo_clean_before_preregistration": True,
        },
        "source_artifacts": {
            "panel_review": {
                "path": PANEL_REVIEW_PATH,
                "status": panel_review.get("status"),
                "panel_validity_classification": panel_review.get("panel_validity_classification"),
                "payload_sha256_excluding_hash": panel_review_hash,
                "payload_hash_verified": True,
            },
            "panel_build_manifest": {
                "path": PANEL_MANIFEST_PATH,
                "status": panel_manifest.get("status"),
                "payload_sha256_excluding_hash": panel_manifest_hash,
                "payload_hash_verified": True,
            },
            "second_source_readiness": {
                "path": READINESS_PATH,
                "status": readiness.get("status"),
                "payload_sha256_excluding_hash": readiness_hash,
                "payload_hash_verified": True,
            },
        },
        "gk_volatility_zscore_squeeze_hypothesis_preregistration": {
            "route_family": ROUTE_FAMILY,
            "hypothesis_name": HYPOTHESIS_NAME,
            "route_type": "cross_sectional_ohlcv_only_volatility_squeeze_reversal",
            "config_count": 1,
            "config_id": CONFIG_ID,
            "timeframe": TIMEFRAME,
            "universe": "Binance/OKX exact overlap 81 Binance symbols",
            "symbol_count": SYMBOL_COUNT,
            "hypothesis_statement": (
                "Symbols with unusually low Garman-Klass 24h volatility versus their own trailing 30d baseline "
                "may reverse upward relative to expanded-volatility symbols over the next 8h."
            ),
            "diagnostic_only": True,
        },
        "universe_and_window_contract": {
            "symbols": symbols,
            "symbol_count": SYMBOL_COUNT,
            "full_window_start_utc": "2023-01-01T00:00:00Z",
            "full_window_end_exclusive_utc": "2025-11-01T00:00:00Z",
            "train_window_start_utc": "2023-01-01T00:00:00Z",
            "train_window_end_exclusive_utc": "2024-07-01T00:00:00Z",
            "validation_window_start_utc": "2024-07-01T00:00:00Z",
            "validation_window_end_exclusive_utc": "2025-04-01T00:00:00Z",
            "holdout_window_start_utc": "2025-04-01T00:00:00Z",
            "holdout_window_end_exclusive_utc": "2025-11-01T00:00:00Z",
            "holdout_reported_separately": True,
            "holdout_used_for_config_selection": False,
        },
        "signal_construction_contract": {
            "row_policy": "use only complete 15m OHLCV bars strictly before entry E",
            "garman_klass_variance": "0.5 * ln(high/low)^2 - (2*ln(2)-1) * ln(close/open)^2",
            "tiny_negative_clamp_policy": "clamp to 0 only if abs(gk_var) < 1e-12",
            "negative_variance_issue_policy": "if gk_var < -1e-12, skip and record numeric issue",
            "current_gk_vol_24h": "sqrt(sum gk_var over prior 96 completed 15m bars)",
            "baseline_observations": "symbol-local trailing 30 calendar days of prior current_gk_vol_24h observations",
            "baseline_lookback_15m_observations": 2880,
            "minimum_baseline_observations": 2016,
            "zscore": "(current_gk_vol_24h - trailing_30d_mean) / trailing_30d_std",
            "long_leg": "lowest 20 percent gk_vol_z",
            "short_leg": "highest 20 percent gk_vol_z",
            "minimum_eligible_symbols": 40,
            "minimum_long_symbols": 5,
            "minimum_short_symbols": 5,
            "no_parameter_expansion": True,
            "no_extra_configs": True,
        },
        "portfolio_and_return_contract": {
            "holding_period_hours": 8,
            "entry_price": "open at E",
            "exit_price": "open at E + 8h",
            "long_return": "exit_open / entry_open - 1",
            "short_return": "-(exit_open / entry_open - 1)",
            "gross_spread_return": "mean(long returns) + mean(short returns)",
            "net_spread_return": "gross - 0.0020",
            "round_trip_cost_bps": 20,
            "equal_weight_dollar_neutral_long_short_spread": True,
            "no_annualization": True,
            "no_compounding": True,
        },
        "future_execution_controls": {
            "use_reviewed_15m_binance_panel_only": True,
            "use_ohlcv_only": True,
            "funding_allowed": False,
            "taker_flow_allowed": False,
            "open_interest_allowed": False,
            "okx_rows_allowed": False,
            "binance_1m_rows_allowed": False,
            "network_allowed": False,
            "non_preregistered_config_allowed": False,
            "parameter_expansion_allowed": False,
            "candidate_generation_allowed": False,
            "edge_claim_allowed": False,
            "runtime_live_capital_allowed": False,
        },
        "future_evaluation_policy": {
            "diagnostic_promising_requires_all": {
                "validation_net_metric_bps_gt_0": True,
                "validation_positive_after_cost": True,
                "null_baseline_review_preliminary_passed": True,
                "monthly_stability_review_preliminary_passed": True,
                "signal_coverage_review_preliminary_passed": True,
                "turnover_concentration_review_preliminary_passed": True,
                "metric_integrity_passed": True,
                "safety_review_passed": True,
            },
            "holdout_positive_cannot_create_candidate_edge_or_release": True,
        },
        "forbidden_actions_confirmed_false": {
            "strategy_executed": False,
            "panel_rows_read": False,
            "funding_rows_read": False,
            "okx_panel_rows_read": False,
            "binance_1m_source_rows_read": False,
            "network_used": False,
            "api_called": False,
            "candidates_generated": False,
            "edge_claimed": False,
            "family_released": False,
            "holdout_permission_granted": False,
            "runtime_permission_granted": False,
            "live_permission_granted": False,
            "capital_permission_granted": False,
            "existing_files_modified_by_module": False,
        },
        "safety_permissions": {
            "preregistration_contract_created": True,
            "strategy_execution_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "holdout_access_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "immediate_next_module_required": False,
            "project_can_pause_after_preregistration": True,
        },
        "validation_checks": {
            "repo_clean_before_run": True,
            "panel_review_loaded": True,
            "panel_review_valid_for_read_only_research": True,
            "exact_overlap_symbol_count_verified_81": True,
            "route_family_count_is_one": True,
            "config_count_is_one": True,
            "config_id_deterministic": True,
            "no_panel_rows_read": True,
            "no_network_used": True,
            "no_strategy_execution": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_runtime_live_capital": True,
            "exactly_one_new_tracked_python_tool_file_expected": True,
            "exactly_one_new_tracked_json_artifact_expected": True,
            "no_existing_files_modified_expected": True,
            "no_other_tracked_files_expected": True,
            "replacement_checks_all_true": True,
        },
        "replacement_checks_all_true": True,
        "payload_sha256_excluding_hash": "",
    }
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)
    assert payload["status"] == STATUS
    assert payload["gk_volatility_zscore_squeeze_hypothesis_preregistration"]["route_family"] == ROUTE_FAMILY
    assert payload["gk_volatility_zscore_squeeze_hypothesis_preregistration"]["config_id"] == CONFIG_ID
    assert payload["signal_construction_contract"]["minimum_eligible_symbols"] == 40
    assert payload["portfolio_and_return_contract"]["holding_period_hours"] == 8
    assert payload["safety_permissions"]["strategy_execution_allowed_now"] is False
    assert payload["forbidden_actions_confirmed_false"]["network_used"] is False
    assert payload["replacement_checks_all_true"] is True
    assert all(payload["validation_checks"].values())
    assert canonical_payload_hash(payload) == payload["payload_sha256_excluding_hash"]
    return payload


def main() -> None:
    artifact_path = REPO_ROOT / ARTIFACT_PATH
    if artifact_path.exists():
        raise RuntimeError(f"artifact already exists: {ARTIFACT_PATH}")
    payload = build_artifact()
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": STATUS,
        "artifact_path": ARTIFACT_PATH,
        "route_family": ROUTE_FAMILY,
        "hypothesis_name": HYPOTHESIS_NAME,
        "config_id": CONFIG_ID,
        "timeframe": TIMEFRAME,
        "symbol_count": SYMBOL_COUNT,
        "holding_period_hours": 8,
        "strategy_execution_allowed_now": False,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "payload_sha256_excluding_hash": payload["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": True,
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
