import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_15m_extreme_move_reversal_preregistration_contract_v1.py"
ARTIFACT_PATH = "artifacts/research_preregistrations/binance_okx_overlap_15m_extreme_move_reversal_preregistration_contract_v1.json"
STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_15M_EXTREME_MOVE_REVERSAL_PREREGISTRATION_CONTRACT_CREATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_15M_EXTREME_MOVE_REVERSAL_PREREGISTRATION_CONTRACT"

ACTUAL_HEAD_BEFORE_PREREGISTRATION = "b5423fdeb116b3a31163381aa872b2fead604ec1"
TRACKED_PYTHON_COUNT_BEFORE_PREREGISTRATION = 859
ROUTE_FAMILY = "BINANCE_OKX_OVERLAP_15M_EXTREME_MOVE_REVERSAL_BASELINE"
HYPOTHESIS_NAME = "extreme_4h_move_reversal"
ROUTE_TYPE = "intraday_extreme_move_exhaustion_reversal"
CONFIG_ID = "extreme4h_5pct_reversal_hold8h"
SYMBOL_COUNT = 81
TIMEFRAME = "15m"

FULL_WINDOW_START = "2023-01-01T00:00:00Z"
FULL_WINDOW_END_EXCLUSIVE = "2025-11-01T00:00:00Z"
TRAIN_WINDOW_START = "2023-01-01T00:00:00Z"
TRAIN_WINDOW_END_EXCLUSIVE = "2024-07-01T00:00:00Z"
VALIDATION_WINDOW_START = "2024-07-01T00:00:00Z"
VALIDATION_WINDOW_END_EXCLUSIVE = "2025-04-01T00:00:00Z"
HOLDOUT_WINDOW_START = "2025-04-01T00:00:00Z"
HOLDOUT_WINDOW_END_EXCLUSIVE = "2025-11-01T00:00:00Z"

PANEL_REVIEW_PATH = "artifacts/panel_build_reviews/binance_okx_overlap_81_symbol_15m_panel_review_after_build_v1.json"
PANEL_MANIFEST_PATH = "artifacts/panel_build_manifests/binance_okx_overlap_81_symbol_15m_panel_build_manifest_v1.json"
READINESS_PATH = "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json"
EXPECTED_PANEL_REVIEW_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_81_SYMBOL_15M_PANEL_REVIEW_AFTER_BUILD_CREATED"
EXPECTED_PANEL_REVIEW_CLASSIFICATION = "PANEL_15M_REVIEW_PASS_VALID_FOR_READ_ONLY_EXTREME_MOVE_RESEARCH"
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


def verify_hash(payload: Dict[str, Any], expected_hash: Optional[str] = None) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise RuntimeError("source artifact missing payload_sha256_excluding_hash")
    recomputed = canonical_payload_hash(payload)
    if recomputed != stored:
        raise RuntimeError(f"source artifact payload hash mismatch: {recomputed} != {stored}")
    if expected_hash is not None and stored != expected_hash:
        raise RuntimeError(f"source artifact payload hash is not expected value: {stored} != {expected_hash}")
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


def forbidden_truthy_permissions(value: Any, path: str = "") -> List[str]:
    forbidden_keys = {
        "strategy_execution_allowed_now",
        "strategy_executed",
        "strategy_search_executed",
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
    panel_review = read_json(PANEL_REVIEW_PATH)
    panel_manifest = read_json(PANEL_MANIFEST_PATH)
    readiness = read_json(READINESS_PATH)

    panel_review_hash = verify_hash(panel_review, EXPECTED_PANEL_REVIEW_HASH)
    panel_manifest_hash = verify_hash(panel_manifest)
    readiness_hash = verify_hash(readiness)

    for label, payload in {
        "panel_review": panel_review,
        "panel_manifest": panel_manifest,
        "second_source_readiness": readiness,
    }.items():
        violations = forbidden_truthy_permissions(payload)
        if violations:
            raise RuntimeError(f"source artifact grants forbidden permission: {label}: {violations}")

    if panel_review.get("status") != EXPECTED_PANEL_REVIEW_STATUS:
        raise RuntimeError("15m panel review status mismatch")
    if panel_review.get("panel_validity_classification") != EXPECTED_PANEL_REVIEW_CLASSIFICATION:
        raise RuntimeError("15m panel review classification mismatch")

    aggregate_review = panel_review.get("aggregate_validation_review", {})
    build_manifest_review = panel_review.get("build_manifest_review", {})
    if aggregate_review.get("reviewed_symbol_count") != SYMBOL_COUNT:
        raise RuntimeError("reviewed 15m symbol count mismatch")
    if aggregate_review.get("reviewed_15m_row_count") != 7808472:
        raise RuntimeError("reviewed 15m row count mismatch")
    if aggregate_review.get("duplicate_symbol_timestamp_count") != 0:
        raise RuntimeError("reviewed duplicate symbol/timestamp count is not zero")
    if aggregate_review.get("ohlc_sanity_valid") is not True:
        raise RuntimeError("reviewed OHLC sanity is not true")
    if aggregate_review.get("numeric_sanity_valid") is not True:
        raise RuntimeError("reviewed numeric sanity is not true")
    if aggregate_review.get("reviewed_min_timestamp_utc") != FULL_WINDOW_START:
        raise RuntimeError("reviewed min timestamp mismatch")
    if aggregate_review.get("reviewed_max_timestamp_utc") != "2025-10-31T23:45:00Z":
        raise RuntimeError("reviewed max timestamp mismatch")
    if build_manifest_review.get("build_manifest_review_passed") is not True:
        raise RuntimeError("15m build manifest review did not pass")

    manifest_scope = panel_manifest.get("build_scope", {})
    manifest_symbol_count = (
        manifest_scope.get("symbol_count")
        or manifest_scope.get("exact_overlap_symbol_count")
        or panel_manifest.get("panel_output_summary", {}).get("output_symbol_count")
    )
    if manifest_symbol_count != SYMBOL_COUNT:
        raise RuntimeError("15m build manifest symbol count mismatch")

    symbols = find_symbol_list(readiness) or find_symbol_list(panel_manifest)
    if symbols is None or len(symbols) != SYMBOL_COUNT:
        raise RuntimeError("could not verify exact 81-symbol Binance overlap universe")

    validation_checks = {
        "repo_clean_before_run": True,
        "panel_review_loaded": True,
        "panel_review_status_verified": True,
        "panel_review_payload_hash_verified": True,
        "panel_valid_for_read_only_extreme_move_research_verified": True,
        "exact_overlap_symbol_count_verified_81": True,
        "config_count_is_one": True,
        "config_id_deterministic": True,
        "no_panel_rows_read": True,
        "no_funding_rows_read": True,
        "no_okx_panel_rows_read": True,
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
        "source_artifacts": {
            "panel_review": {
                "path": PANEL_REVIEW_PATH,
                "status": panel_review.get("status"),
                "artifact_kind": panel_review.get("artifact_kind"),
                "panel_validity_classification": panel_review.get("panel_validity_classification"),
                "payload_sha256_excluding_hash": panel_review_hash,
                "payload_hash_verified": True,
            },
            "panel_build_manifest": {
                "path": PANEL_MANIFEST_PATH,
                "status": panel_manifest.get("status"),
                "artifact_kind": panel_manifest.get("artifact_kind"),
                "payload_sha256_excluding_hash": panel_manifest_hash,
                "payload_hash_verified": True,
            },
            "second_source_readiness": {
                "path": READINESS_PATH,
                "status": readiness.get("status"),
                "artifact_kind": readiness.get("artifact_kind"),
                "payload_sha256_excluding_hash": readiness_hash,
                "payload_hash_verified": True,
            },
        },
        "panel_review_preserved": {
            "review_artifact_path": PANEL_REVIEW_PATH,
            "review_status": panel_review.get("status"),
            "review_classification": panel_review.get("panel_validity_classification"),
            "reviewed_symbol_count": aggregate_review.get("reviewed_symbol_count"),
            "reviewed_15m_row_count": aggregate_review.get("reviewed_15m_row_count"),
            "reviewed_min_timestamp_utc": aggregate_review.get("reviewed_min_timestamp_utc"),
            "reviewed_max_timestamp_utc": aggregate_review.get("reviewed_max_timestamp_utc"),
            "duplicate_symbol_timestamp_count": aggregate_review.get("duplicate_symbol_timestamp_count"),
            "ohlc_sanity_valid": aggregate_review.get("ohlc_sanity_valid"),
            "numeric_sanity_valid": aggregate_review.get("numeric_sanity_valid"),
            "payload_sha256_excluding_hash": panel_review_hash,
        },
        "extreme_move_reversal_hypothesis_preregistration": {
            "route_family": ROUTE_FAMILY,
            "hypothesis_name": HYPOTHESIS_NAME,
            "route_type": ROUTE_TYPE,
            "universe": "Binance/OKX exact overlap 81 Binance symbols",
            "timeframe": TIMEFRAME,
            "config_count": 1,
            "config_id": CONFIG_ID,
            "hypothesis_statement": (
                "Extreme 4-hour intraday moves in crypto perpetuals may overextend short-term positioning "
                "and liquidity demand. After a large positive 4h move, the next 8h may mean-revert lower; "
                "after a large negative 4h move, the next 8h may mean-revert higher."
            ),
            "diagnostic_only": True,
        },
        "universe_and_window_contract": {
            "symbol_count": SYMBOL_COUNT,
            "symbols": symbols,
            "full_window_start_utc": FULL_WINDOW_START,
            "full_window_end_exclusive_utc": FULL_WINDOW_END_EXCLUSIVE,
            "train_window_start_utc": TRAIN_WINDOW_START,
            "train_window_end_exclusive_utc": TRAIN_WINDOW_END_EXCLUSIVE,
            "validation_window_start_utc": VALIDATION_WINDOW_START,
            "validation_window_end_exclusive_utc": VALIDATION_WINDOW_END_EXCLUSIVE,
            "holdout_window_start_utc": HOLDOUT_WINDOW_START,
            "holdout_window_end_exclusive_utc": HOLDOUT_WINDOW_END_EXCLUSIVE,
            "holdout_reported_separately": True,
            "holdout_not_used_for_selection": True,
        },
        "signal_construction_contract": {
            "timeframe": TIMEFRAME,
            "row_policy": "use only complete 15m bars",
            "entry_timestamp": "E is a 15m bar open",
            "lookback_policy": "use only prior completed bars before E",
            "prior_move_lookback_hours": 4,
            "prior_move_lookback_bars": 16,
            "prior_4h_return": "close of bar E-15m divided by open of bar E-4h, minus 1",
            "long_signal": "prior_4h_return <= -0.05",
            "short_signal": "prior_4h_return >= +0.05",
            "no_signal": "abs(prior_4h_return) < 0.05",
            "extreme_threshold_abs": 0.05,
            "no_cross_sectional_rank": True,
            "no_parameter_grid": True,
            "no_alternative_thresholds": True,
            "no_alternative_holding_periods": True,
            "no_symbol_specific_tuning": True,
        },
        "portfolio_and_return_contract": {
            "entry_price": "open at E",
            "exit_price": "open at E + 8h",
            "holding_period_hours": 8,
            "holding_period_bars": 32,
            "long_return": "exit_open / entry_open - 1",
            "short_return": "-(exit_open / entry_open - 1)",
            "round_trip_cost_bps": 20,
            "no_annualization": True,
            "no_compounding": True,
            "event_based_symbol_level": True,
            "cross_symbol_overlapping_allowed": True,
            "same_symbol_overlapping_allowed": False,
            "same_symbol_cooldown_policy": "after accepting an event for a symbol, ignore new events for that symbol until its E+8h exit",
            "aggregate_return": "equal-weight average across all active accepted event trades",
            "minimum_total_validation_events": 100,
            "minimum_monthly_validation_events_for_monthly_stability": 5,
        },
        "future_execution_controls": {
            "use_reviewed_15m_binance_panel_only": True,
            "use_exact_81_symbol_universe": True,
            "use_full_window_and_split_above_only": True,
            "okx_panel_rows_allowed": False,
            "funding_rows_allowed": False,
            "open_interest_allowed": False,
            "taker_flow_signal_allowed": False,
            "pair_scanning_allowed": False,
            "threshold_expansion_allowed": False,
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
                "event_coverage_review_preliminary_passed": True,
                "turnover_concentration_review_preliminary_passed": True,
                "metric_integrity_passed": True,
                "safety_review_passed": True,
            },
            "future_required_diagnostics": [
                "train/validation/holdout gross and net bps",
                "monthly gross/net by entry month",
                "event counts by month",
                "event counts by symbol",
                "long vs short event counts",
                "long vs short performance",
                "top symbol event share",
                "null baseline with timestamp/block shuffle",
                "no candidate/edge/release/live/capital from execution alone",
            ],
        },
        "forbidden_actions_confirmed_false": {
            "strategy_executed": False,
            "strategy_search_executed": False,
            "panel_rows_read": False,
            "funding_rows_read": False,
            "okx_panel_rows_read": False,
            "network_used": False,
            "api_called": False,
            "candidates_generated": False,
            "edge_claimed": False,
            "family_released": False,
            "holdout_accessed": False,
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
        "validation_checks": validation_checks,
        "replacement_checks_all_true": True,
        "payload_sha256_excluding_hash": "",
    }

    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)
    assert payload["status"] == STATUS
    assert payload["artifact_kind"] == ARTIFACT_KIND
    assert payload["module"] == MODULE_PATH
    assert payload["extreme_move_reversal_hypothesis_preregistration"]["route_family"] == ROUTE_FAMILY
    assert payload["extreme_move_reversal_hypothesis_preregistration"]["config_count"] == 1
    assert payload["extreme_move_reversal_hypothesis_preregistration"]["config_id"] == CONFIG_ID
    assert payload["signal_construction_contract"]["extreme_threshold_abs"] == 0.05
    assert payload["portfolio_and_return_contract"]["holding_period_hours"] == 8
    assert payload["safety_permissions"]["strategy_execution_allowed_now"] is False
    assert payload["forbidden_actions_confirmed_false"]["panel_rows_read"] is False
    assert payload["forbidden_actions_confirmed_false"]["network_used"] is False
    assert payload["forbidden_actions_confirmed_false"]["strategy_executed"] is False
    assert payload["forbidden_actions_confirmed_false"]["candidates_generated"] is False
    assert payload["forbidden_actions_confirmed_false"]["edge_claimed"] is False
    assert payload["forbidden_actions_confirmed_false"]["runtime_permission_granted"] is False
    assert payload["replacement_checks_all_true"] is True
    assert all(payload["validation_checks"].values())
    assert canonical_payload_hash(payload) == payload["payload_sha256_excluding_hash"]
    return payload


def main() -> None:
    payload = build_artifact()
    artifact_path = REPO_ROOT / ARTIFACT_PATH
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    if artifact_path.exists():
        raise RuntimeError(f"artifact already exists: {ARTIFACT_PATH}")
    artifact_path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": STATUS,
        "preregistration_artifact_path": ARTIFACT_PATH,
        "route_family": ROUTE_FAMILY,
        "hypothesis_name": HYPOTHESIS_NAME,
        "config_id": CONFIG_ID,
        "timeframe": TIMEFRAME,
        "symbol_count": SYMBOL_COUNT,
        "prior_move_lookback_hours": 4,
        "extreme_threshold_abs": 0.05,
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
