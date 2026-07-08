#!/usr/bin/env python
"""Create the preregistration contract for the cross-exchange crowded perp route."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
ARTIFACT_RELATIVE_PATH = (
    "artifacts/research_preregistrations/"
    "cross_exchange_crowded_perp_dislocation_unwind_preregistration_contract_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH
MODULE_RELATIVE_PATH = (
    "tools/"
    "edge_factory_os_repo_only_cross_exchange_crowded_perp_dislocation_unwind_"
    "preregistration_contract_v1.py"
)

BASIS_PREMIUM_CLOSURE_PATH = REPO_ROOT / (
    "artifacts/strategy_closures/"
    "binance_okx_overlap_basis_premium_zscore_mean_reversion_closure_v1.json"
)
BASIS_PREMIUM_REVIEW_PATH = REPO_ROOT / (
    "artifacts/basis_premium_data_reviews/"
    "binance_okx_overlap_basis_premium_1h_data_pack_review_v1.json"
)
BASIS_PREMIUM_MANIFEST_PATH = REPO_ROOT / (
    "artifacts/basis_premium_data_locks/"
    "binance_okx_overlap_basis_premium_1h_data_pack_v1.json"
)

STATUS = "PASS_REPO_ONLY_CROSS_EXCHANGE_CROWDED_PERP_DISLOCATION_UNWIND_PREREGISTRATION_CONTRACT_CREATED"
ARTIFACT_KIND = "CROSS_EXCHANGE_CROWDED_PERP_DISLOCATION_UNWIND_PREREGISTRATION_CONTRACT"
ROUTE_FAMILY = "CROSS_EXCHANGE_CROWDED_PERP_DISLOCATION_UNWIND_V1"
HYPOTHESIS_NAME = "cross_exchange_crowded_perp_dislocation_unwind"
ROUTE_TYPE = "cross_exchange_market_neutral_perp_basis_dislocation_unwind"
CONFIG_ID = "bx_okx_basis_divergence_funding_stress_failure_hold8h"
CURRENT_HEAD_AT_START = "3b224443d032889a40adb8b5075ff006b226d04f"
TRACKED_PYTHON_COUNT_AT_START = 873

PRIOR_REJECTED_CLASS = "BASIS_PREMIUM_ZSCORE_MEAN_REVERSION_REJECTED_NO_FOLLOWUP"
EXPECTED_REVIEW_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_BASIS_PREMIUM_1H_DATA_PACK_REVIEW_CREATED"
EXPECTED_REVIEW_PAYLOAD = "9fca2469059be23e9a1bee77c4772f0cc5a06cb01c916f1b7356a69fa2278f4a"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def payload_hash(artifact: dict) -> str:
    payload = {key: value for key, value in artifact.items() if key != "payload_sha256_excluding_hash"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def all_true(checks: dict) -> bool:
    return all(value is True for value in checks.values() if isinstance(value, bool))


def main() -> int:
    if ARTIFACT_PATH.exists():
        print(f"BLOCKED: artifact already exists: {ARTIFACT_PATH}")
        print("replacement_checks_all_true: false")
        return 1

    prior_closure = load_json(BASIS_PREMIUM_CLOSURE_PATH)
    basis_review = load_json(BASIS_PREMIUM_REVIEW_PATH)
    basis_manifest = load_json(BASIS_PREMIUM_MANIFEST_PATH)

    prior_closure_record = prior_closure.get("closure_record", {})
    basis_review_safety = basis_review.get("safety_permissions", {})
    manifest_safety = basis_manifest.get("safety_permissions", {})

    validation_checks = {
        "prior_basis_premium_closure_loaded": True,
        "prior_basis_premium_route_rejected_no_followup": prior_closure_record.get("result_classification")
        == PRIOR_REJECTED_CLASS,
        "prior_basis_premium_route_closed": prior_closure_record.get("route_closed") is True,
        "basis_premium_review_loaded": True,
        "basis_premium_review_status_verified": basis_review.get("status") == EXPECTED_REVIEW_STATUS,
        "basis_premium_review_payload_verified": basis_review.get("payload_sha256_excluding_hash")
        == EXPECTED_REVIEW_PAYLOAD,
        "basis_premium_manifest_loaded": True,
        "basis_premium_review_valid_for_future_feature_construction": basis_review_safety.get(
            "basis_premium_data_valid_for_future_feature_construction"
        )
        is True,
        "config_count_exactly_one": True,
        "no_parameter_expansion": True,
        "execution_blocked_until_availability_acquisition_review_pass": True,
        "metadata_only_no_row_files_read": True,
        "no_network_used": True,
        "no_private_apis": True,
        "no_api_keys": True,
        "no_live_order_trading_endpoints": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_family_release": True,
        "no_runtime_live_capital": True,
        "source_review_candidate_permission_false": basis_review_safety.get("candidate_generation_allowed_now")
        is False,
        "source_review_edge_permission_false": basis_review_safety.get("edge_claim_allowed_now") is False,
        "source_review_release_permission_false": basis_review_safety.get("family_release_allowed_now")
        is False,
        "source_review_runtime_permission_false": basis_review_safety.get("runtime_permission_allowed_now")
        is False,
        "source_review_live_permission_false": basis_review_safety.get("live_permission_allowed_now") is False,
        "source_review_capital_permission_false": basis_review_safety.get("capital_permission_allowed_now")
        is False,
        "source_manifest_candidate_permission_false": manifest_safety.get("candidate_generation_allowed_now")
        is False,
        "source_manifest_edge_permission_false": manifest_safety.get("edge_claim_allowed_now") is False,
        "source_manifest_runtime_permission_false": manifest_safety.get("runtime_permission_allowed_now")
        is False,
        "source_manifest_live_permission_false": manifest_safety.get("live_permission_allowed_now") is False,
        "source_manifest_capital_permission_false": manifest_safety.get("capital_permission_allowed_now")
        is False,
    }
    replacement_checks_all_true = all_true(validation_checks)
    if not replacement_checks_all_true:
        print("BLOCKED: preregistration validation checks failed")
        for key in sorted(validation_checks):
            if validation_checks[key] is not True:
                print(f"{key}: {validation_checks[key]}")
        print("replacement_checks_all_true: false")
        return 1

    safety_permissions = {
        "preregistration_contract_created": True,
        "data_availability_discovery_allowed_next": True,
        "data_acquisition_allowed_now": False,
        "strategy_execution_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
        "holdout_permission_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
    }

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_RELATIVE_PATH,
        "source_checkpoint": {
            "actual_head_at_route_start": CURRENT_HEAD_AT_START,
            "tracked_python_count_at_route_start": TRACKED_PYTHON_COUNT_AT_START,
            "repo_clean_before_start": True,
        },
        "route_family": ROUTE_FAMILY,
        "hypothesis_name": HYPOTHESIS_NAME,
        "route_type": ROUTE_TYPE,
        "route_context": {
            "prior_route": "BINANCE_OKX_OVERLAP_BASIS_PREMIUM_ZSCORE_MEAN_REVERSION",
            "prior_route_result_classification": prior_closure_record.get("result_classification"),
            "prior_route_retest_allowed_now": False,
            "do_not_retest_prior_basis_premium_route": True,
            "do_not_expand_prior_parameters": True,
        },
        "fixed_config": {
            "config_count": 1,
            "config_id": CONFIG_ID,
            "timeframe": "1h",
            "universe": "exact Binance/OKX overlap symbols available on both exchanges, target 81 if data supports it",
            "holding_period_hours": 8,
            "cost_round_trip_bps": 20,
            "no_parameter_expansion": True,
            "minimum_eligible_symbols_per_timestamp": 20,
            "minimum_active_trades_per_timestamp": 1,
        },
        "target_window": {
            "preferred_start_utc": "2023-07-01T00:00:00Z",
            "preferred_end_exclusive_utc": "2025-10-31T16:00:00Z",
            "narrower_window_allowed_only_if_safely_supported_by_okx_data": True,
        },
        "signal_definition": {
            "binance_basis": "Binance mark_close / Binance index_close - 1",
            "okx_basis": "OKX mark/index equivalent, or best verified OKX premium/basis equivalent",
            "divergence": "binance_basis - okx_basis",
            "divergence_z": "symbol-local trailing 30d z-score using only observations strictly before E",
            "funding_stress": "lagged Binance and/or OKX funding confirms crowded side if available",
            "continuation_failure_filter": {
                "prior_return_hours": 4,
                "high_positive_divergence_skip_if_expensive_leg_up_gt": 0.02,
                "low_negative_divergence_skip_if_cheap_leg_down_lt": -0.02,
                "fixed_not_tunable": True,
            },
            "entry_rules": {
                "z_gte_plus_2": "short Binance, long OKX",
                "z_lte_minus_2": "long Binance, short OKX",
            },
            "portfolio": "equal-dollar long/short cross-exchange spread, delta-neutral by symbol",
            "funding_cashflow_primary_result": "excluded unless both exchanges are unambiguously aligned",
        },
        "future_execution_controls": {
            "execution_blocked_until_cross_exchange_data_availability_lock_available": True,
            "execution_blocked_until_data_acquisition_lock_created": True,
            "execution_blocked_until_cross_exchange_data_review_pass": True,
            "data_unavailable_means_route_pending": True,
            "do_not_test_extra_configs": True,
            "do_not_tune_parameters": True,
            "do_not_generate_candidate_edge_release_or_permissions": True,
        },
        "required_data_for_execution": {
            "binance_basis_premium_1h": "already acquired and reviewed",
            "binance_funding": "already acquired and reviewed for aligned window",
            "binance_1h_ohlcv": "already acquired and reviewed",
            "okx_1h_ohlcv": "must verify existing safe non-holdout external artifact if present",
            "okx_basis_premium_equivalent": "must verify or discover availability",
            "okx_funding": "must verify or discover availability",
            "optional_oi_long_short_liquidation": "not required for V1",
        },
        "source_artifacts": {
            "prior_basis_premium_closure": str(BASIS_PREMIUM_CLOSURE_PATH.relative_to(REPO_ROOT)),
            "basis_premium_review": str(BASIS_PREMIUM_REVIEW_PATH.relative_to(REPO_ROOT)),
            "basis_premium_manifest": str(BASIS_PREMIUM_MANIFEST_PATH.relative_to(REPO_ROOT)),
        },
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": None,
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(artifact, handle, indent=2)
        handle.write("\n")

    print(f"status: {STATUS}")
    print(f"artifact_path: {ARTIFACT_PATH}")
    print(f"route_family: {ROUTE_FAMILY}")
    print(f"config_id: {CONFIG_ID}")
    print("config_count: 1")
    print("execution_blocked_until_data_availability_acquisition_review_pass: true")
    print("data_availability_discovery_allowed_next: true")
    print("candidate_generation_allowed_now: false")
    print("edge_claim_allowed_now: false")
    print("family_release_allowed_now: false")
    print("runtime_live_capital_allowed_now: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print("replacement_checks_all_true: true")
    return 0


if __name__ == "__main__":
    sys.exit(main())
