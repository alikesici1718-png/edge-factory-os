#!/usr/bin/env python
"""Create the preregistration contract for one basis/premium diagnostic config."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
MODULE_RELATIVE_PATH = (
    "tools/"
    "edge_factory_os_repo_only_binance_okx_overlap_basis_premium_zscore_mean_reversion_"
    "preregistration_contract_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/research_preregistrations/"
    "binance_okx_overlap_basis_premium_zscore_mean_reversion_preregistration_contract_v1.json"
)
REVIEW_RELATIVE_PATH = (
    "artifacts/basis_premium_data_reviews/"
    "binance_okx_overlap_basis_premium_1h_data_pack_review_v1.json"
)
MANIFEST_RELATIVE_PATH = (
    "artifacts/basis_premium_data_locks/"
    "binance_okx_overlap_basis_premium_1h_data_pack_v1.json"
)

ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH
REVIEW_PATH = REPO_ROOT / REVIEW_RELATIVE_PATH
MANIFEST_PATH = REPO_ROOT / MANIFEST_RELATIVE_PATH

STATUS = (
    "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_BASIS_PREMIUM_ZSCORE_MEAN_REVERSION_"
    "PREREGISTRATION_CONTRACT_CREATED"
)
ARTIFACT_KIND = (
    "BINANCE_OKX_OVERLAP_BASIS_PREMIUM_ZSCORE_MEAN_REVERSION_PREREGISTRATION_CONTRACT"
)
ROUTE_FAMILY = "BINANCE_OKX_OVERLAP_BASIS_PREMIUM_ZSCORE_MEAN_REVERSION_BASELINE"
HYPOTHESIS_NAME = "basis_premium_zscore_mean_reversion"
ROUTE_TYPE = "cross_sectional_perp_basis_relative_value_mean_reversion"
CONFIG_ID = "mark_index_basis_z30d_reversal_hold8h"
EXPECTED_REVIEW_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_BASIS_PREMIUM_1H_DATA_PACK_REVIEW_CREATED"
EXPECTED_REVIEW_CLASSIFICATION = (
    "BASIS_PREMIUM_REVIEW_PASS_WITH_P1_ATTENTION_VALID_FOR_FUTURE_BASIS_PREMIUM_FEATURE_CONSTRUCTION"
)
EXPECTED_REVIEW_PAYLOAD = "9fca2469059be23e9a1bee77c4772f0cc5a06cb01c916f1b7356a69fa2278f4a"
EXPECTED_SYMBOL_COUNT = 81


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

    review = load_json(REVIEW_PATH)
    manifest = load_json(MANIFEST_PATH)

    review_safety = review.get("safety_permissions", {})
    manifest_safety = manifest.get("safety_permissions", {})
    review_aggregate = review.get("aggregate_validation_review", {})
    manifest_summary = manifest.get("acquisition_summary", {})

    validation_checks = {
        "review_artifact_loaded": True,
        "manifest_artifact_loaded": True,
        "review_status_verified": review.get("status") == EXPECTED_REVIEW_STATUS,
        "review_payload_hash_verified": review.get("payload_sha256_excluding_hash") == EXPECTED_REVIEW_PAYLOAD,
        "review_classification_verified": review.get("basis_premium_data_validity_classification")
        == EXPECTED_REVIEW_CLASSIFICATION,
        "basis_premium_data_valid_for_future_feature_construction": review_safety.get(
            "basis_premium_data_valid_for_future_feature_construction"
        )
        is True,
        "reviewed_symbol_count_verified_81": review_aggregate.get("reviewed_symbol_count")
        == EXPECTED_SYMBOL_COUNT,
        "manifest_symbol_count_verified_81": manifest_summary.get("symbol_count") == EXPECTED_SYMBOL_COUNT,
        "reviewed_total_rows_verified": review_aggregate.get("reviewed_total_rows") == 1_952_156,
        "review_duplicate_count_zero": review_aggregate.get("duplicate_symbol_timestamp_count") == 0,
        "review_missing_field_count_zero": review_aggregate.get("required_field_missing_count") == 0,
        "review_invalid_numeric_count_zero": review_aggregate.get("invalid_numeric_count") == 0,
        "review_mark_index_sanity_true": review_aggregate.get("mark_index_price_sanity_valid") is True,
        "review_premium_numeric_sanity_true": review_aggregate.get("premium_numeric_sanity_valid") is True,
        "exactly_one_config_preregistered": True,
        "no_parameter_expansion": True,
        "no_network_used": True,
        "no_external_row_files_read": True,
        "no_strategy_execution": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_family_release": True,
        "no_holdout_permission": True,
        "no_runtime_live_capital": True,
        "source_review_strategy_permission_false": review_safety.get("strategy_execution_allowed_now") is False,
        "source_review_candidate_permission_false": review_safety.get("candidate_generation_allowed_now") is False,
        "source_review_edge_permission_false": review_safety.get("edge_claim_allowed_now") is False,
        "source_review_release_permission_false": review_safety.get("family_release_allowed_now") is False,
        "source_review_runtime_permission_false": review_safety.get("runtime_permission_allowed_now") is False,
        "source_review_live_permission_false": review_safety.get("live_permission_allowed_now") is False,
        "source_review_capital_permission_false": review_safety.get("capital_permission_allowed_now") is False,
        "source_manifest_strategy_permission_false": manifest_safety.get("strategy_execution_allowed_now") is False,
        "source_manifest_candidate_permission_false": manifest_safety.get("candidate_generation_allowed_now") is False,
        "source_manifest_edge_permission_false": manifest_safety.get("edge_claim_allowed_now") is False,
        "source_manifest_runtime_permission_false": manifest_safety.get("runtime_permission_allowed_now") is False,
        "source_manifest_live_permission_false": manifest_safety.get("live_permission_allowed_now") is False,
        "source_manifest_capital_permission_false": manifest_safety.get("capital_permission_allowed_now") is False,
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
        "strategy_execution_allowed_next_for_single_preregistered_config_only": True,
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
        "route_family": ROUTE_FAMILY,
        "hypothesis_name": HYPOTHESIS_NAME,
        "route_type": ROUTE_TYPE,
        "universe_and_window": {
            "timeframe": "1h",
            "universe": "Binance/OKX exact overlap 81 symbols",
            "symbol_count": EXPECTED_SYMBOL_COUNT,
            "full_window_start_utc": "2023-01-01T00:00:00Z",
            "full_window_end_exclusive_utc": "2025-11-01T00:00:00Z",
            "train_start_utc": "2023-01-01T00:00:00Z",
            "train_end_exclusive_utc": "2024-07-01T00:00:00Z",
            "validation_start_utc": "2024-07-01T00:00:00Z",
            "validation_end_exclusive_utc": "2025-04-01T00:00:00Z",
            "holdout_start_utc": "2025-04-01T00:00:00Z",
            "holdout_end_exclusive_utc": "2025-11-01T00:00:00Z",
            "holdout_reported_separately": True,
            "holdout_used_for_config_selection": False,
        },
        "signal_definition": {
            "basis_close": "mark_close / index_close - 1",
            "premium_close_role": "secondary_diagnostic_only",
            "entry_timestamp": "hourly timestamp E",
            "lookback_rule": "use only rows strictly before E",
            "trailing_30d_context_prior_observations": 720,
            "minimum_prior_observations": 504,
            "basis_z": "(latest basis_close before E - trailing_30d_mean) / trailing_30d_std",
            "std_guard": "if trailing_std <= 0, symbol ineligible",
            "ranking": "rank basis_z cross-sectionally ascending",
            "long_leg": "bottom 20 percent lowest basis_z",
            "short_leg": "top 20 percent highest basis_z",
            "minimum_eligible_symbols": 60,
            "minimum_long_symbols": 5,
            "minimum_short_symbols": 5,
            "portfolio": "equal-weight dollar-neutral long/short spread",
            "holding_period_hours": 8,
            "entry_exit_prices": "mark_open at E and mark_open at E+8h",
            "cost_round_trip_bps": 20,
            "parameter_expansion_allowed": False,
        },
        "config_grid": [
            {
                "config_id": CONFIG_ID,
                "basis_metric": "mark_index_basis_close",
                "zscore_lookback_hours": 720,
                "minimum_prior_observations": 504,
                "long_quantile": 0.20,
                "short_quantile": 0.20,
                "minimum_eligible_symbols": 60,
                "minimum_long_symbols": 5,
                "minimum_short_symbols": 5,
                "holding_period_hours": 8,
                "cost_round_trip_bps": 20,
                "return_price": "mark_open",
                "no_parameter_expansion": True,
            }
        ],
        "future_execution_controls": {
            "execution_step_may_read_external_basis_premium_rows": True,
            "execution_step_must_read_only_reviewed_basis_premium_jsonl_gz_rows": True,
            "execution_step_must_execute_exactly_one_config": True,
            "execution_step_must_not_test_extra_configs": True,
            "execution_step_must_not_tune_parameters": True,
            "execution_step_must_report_holdout_separately": True,
            "holdout_positive_cannot_create_candidate_edge_or_release": True,
        },
        "source_artifacts": {
            "basis_premium_review": {
                "path": REVIEW_RELATIVE_PATH,
                "status": review.get("status"),
                "classification": review.get("basis_premium_data_validity_classification"),
                "payload_sha256_excluding_hash": review.get("payload_sha256_excluding_hash"),
            },
            "basis_premium_manifest": {
                "path": MANIFEST_RELATIVE_PATH,
                "status": manifest.get("status"),
                "payload_sha256_excluding_hash": manifest.get("payload_sha256_excluding_hash"),
            },
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
    print(f"reviewed_symbol_count: {review_aggregate.get('reviewed_symbol_count')}")
    print(f"review_payload_sha256_verified: {validation_checks['review_payload_hash_verified']}")
    print("candidate_generation_allowed_now: false")
    print("edge_claim_allowed_now: false")
    print("family_release_allowed_now: false")
    print("holdout_permission_allowed_now: false")
    print("runtime_live_capital_allowed_now: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(replacement_checks_all_true).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
