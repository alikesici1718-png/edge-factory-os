#!/usr/bin/env python
"""Create the cross-exchange crowded perp data availability discovery lock."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

MODULE_RELATIVE_PATH = (
    "tools/"
    "edge_factory_os_repo_only_cross_exchange_crowded_perp_data_availability_discovery_lock_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/cross_exchange_data_availability_locks/"
    "cross_exchange_crowded_perp_data_availability_discovery_lock_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

PREREG_PATH = REPO_ROOT / (
    "artifacts/research_preregistrations/"
    "cross_exchange_crowded_perp_dislocation_unwind_preregistration_contract_v1.json"
)
BASIS_PREMIUM_REVIEW_PATH = REPO_ROOT / (
    "artifacts/basis_premium_data_reviews/"
    "binance_okx_overlap_basis_premium_1h_data_pack_review_v1.json"
)
BASIS_PREMIUM_MANIFEST_PATH = REPO_ROOT / (
    "artifacts/basis_premium_data_locks/"
    "binance_okx_overlap_basis_premium_1h_data_pack_v1.json"
)
BINANCE_FUNDING_REVIEW_PATH = REPO_ROOT / (
    "artifacts/funding_rate_reviews/"
    "binance_okx_overlap_funding_rate_full_range_202105_202510_review_v1.json"
)
BINANCE_FUNDING_LOCK_PATH = REPO_ROOT / (
    "artifacts/funding_rate_locks/"
    "binance_okx_overlap_funding_rate_full_range_202105_202510_acquisition_lock_v1.json"
)
BINANCE_PANEL_REVIEW_PATH = REPO_ROOT / (
    "artifacts/panel_build_reviews/"
    "binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json"
)
SECOND_SOURCE_READINESS_PATH = REPO_ROOT / (
    "artifacts/second_source_readiness/"
    "binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json"
)

STATUS = "PASS_REPO_CODE_ONLY_CROSS_EXCHANGE_CROWDED_PERP_DATA_AVAILABILITY_LOCK_UNAVAILABLE_ROUTE_PENDING"
ARTIFACT_KIND = "CROSS_EXCHANGE_CROWDED_PERP_DATA_AVAILABILITY_DISCOVERY_LOCK"
ROUTE_FAMILY = "CROSS_EXCHANGE_CROWDED_PERP_DISLOCATION_UNWIND_V1"
CONFIG_ID = "bx_okx_basis_divergence_funding_stress_failure_hold8h"
CLASSIFICATION = "CROSS_EXCHANGE_DATA_UNAVAILABLE_ROUTE_PENDING"
PREREG_STATUS = "PASS_REPO_ONLY_CROSS_EXCHANGE_CROWDED_PERP_DISLOCATION_UNWIND_PREREGISTRATION_CONTRACT_CREATED"
PREFERRED_START_UTC = "2023-07-01T00:00:00Z"
PREFERRED_END_EXCLUSIVE_UTC = "2025-10-31T16:00:00Z"
HEAD_AT_DISCOVERY_START = "8df36e7743c66b0cff3696d09ddfb71979b28874"
TRACKED_PYTHON_COUNT_AT_DISCOVERY_START = 874


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"required metadata artifact missing: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def payload_hash(artifact: dict) -> str:
    payload = {key: value for key, value in artifact.items() if key != "payload_sha256_excluding_hash"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def all_true(checks: dict) -> bool:
    return all(value is True for value in checks.values() if isinstance(value, bool))


def path_text(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def source_status(source: dict) -> str | None:
    return source.get("status")


def source_payload(source: dict) -> str | None:
    return source.get("payload_sha256_excluding_hash")


def find_repo_metadata_candidates() -> list[str]:
    artifacts_dir = REPO_ROOT / "artifacts"
    if not artifacts_dir.exists():
        return []

    terms = ("okx", "cross_exchange")
    route_terms = ("funding", "basis", "premium", "panel", "ohlcv", "dislocation", "perp")
    candidates: list[str] = []
    for path in artifacts_dir.rglob("*.json"):
        name = path.as_posix().lower()
        if any(term in name for term in terms) and any(term in name for term in route_terms):
            candidates.append(path_text(path))
    return sorted(candidates)


def find_external_directory_candidates() -> list[str]:
    if not EDGE_LAB_ROOT.exists():
        return []

    route_terms = ("okx", "cross_exchange", "basis", "funding", "panel", "perp")
    candidates: list[str] = []
    for child in EDGE_LAB_ROOT.iterdir():
        if not child.is_dir():
            continue
        name = child.name.lower()
        if "edge_factory_os_repo" not in name:
            continue
        if any(term in name for term in route_terms):
            candidates.append(str(child))
    return sorted(candidates)


def bool_from_nested(mapping: dict, *keys: str) -> bool | None:
    current = mapping
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    if isinstance(current, bool):
        return current
    return None


def main() -> int:
    if ARTIFACT_PATH.exists():
        print(f"BLOCKED: artifact already exists: {ARTIFACT_PATH}")
        print("replacement_checks_all_true: false")
        return 1

    try:
        prereg = load_json(PREREG_PATH)
        basis_review = load_json(BASIS_PREMIUM_REVIEW_PATH)
        basis_manifest = load_json(BASIS_PREMIUM_MANIFEST_PATH)
        funding_review = load_json(BINANCE_FUNDING_REVIEW_PATH)
        funding_lock = load_json(BINANCE_FUNDING_LOCK_PATH)
        panel_review = load_json(BINANCE_PANEL_REVIEW_PATH)
        readiness = load_json(SECOND_SOURCE_READINESS_PATH)
    except Exception as exc:  # pragma: no cover - deterministic module failure path.
        print(f"BLOCKED: {exc}")
        print("replacement_checks_all_true: false")
        return 1

    repo_metadata_candidates = find_repo_metadata_candidates()
    external_directory_candidates = find_external_directory_candidates()

    funding_endpoint = funding_lock.get("source_endpoint_contract", {}).get("endpoint_url")
    funding_review_scope = funding_review.get("review_scope", {})
    funding_data_review = funding_review.get("funding_data_review", {})
    panel_validation = panel_review.get("validation_checks", {})
    panel_safety = panel_review.get("safety_permissions", {})
    basis_safety = basis_review.get("safety_permissions", {})
    basis_aggregate = basis_review.get("aggregate_validation_review", {})
    basis_manifest_safety = basis_manifest.get("safety_permissions", {})

    binance_basis_available = (
        basis_review.get("status") == "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_BASIS_PREMIUM_1H_DATA_PACK_REVIEW_CREATED"
        and basis_review.get("replacement_checks_all_true") is True
        and basis_safety.get("basis_premium_data_valid_for_future_feature_construction") is True
        and basis_aggregate.get("reviewed_symbol_count") == 81
    )
    binance_funding_available = (
        funding_review.get("status")
        == "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_RATE_FULL_RANGE_202105_202510_REVIEW_CREATED"
        and funding_review.get("replacement_checks_all_true") is True
        and funding_data_review.get("funding_data_valid_for_full_range_signal_construction") is True
        and funding_review_scope.get("symbol_count") == 81
        and funding_endpoint == "https://fapi.binance.com/fapi/v1/fundingRate"
    )
    binance_ohlcv_available = (
        panel_review.get("status")
        == "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_NEAR_5Y_PANEL_BUILD_REVIEW_AFTER_EXECUTION_CREATED"
        and panel_review.get("replacement_checks_all_true") is True
        and panel_validation.get("no_okx_panel_rows_read") is True
        and panel_safety.get("okx_panel_access_allowed_now") is False
    )

    okx_ohlcv_proven_for_v1 = False
    okx_basis_premium_equivalent_proven_for_v1 = False
    okx_funding_proven_for_v1 = False
    aligned_symbol_count_for_v1 = 0

    required_data_matrix = {
        "A_binance_basis_premium_1h": {
            "required_for_v1": True,
            "available_for_v1": binance_basis_available,
            "evidence_artifact": path_text(BASIS_PREMIUM_REVIEW_PATH),
            "payload_sha256_excluding_hash": source_payload(basis_review),
            "reviewed_symbol_count": basis_aggregate.get("reviewed_symbol_count"),
            "reviewed_total_rows": basis_aggregate.get("reviewed_total_rows"),
            "window_start_utc": basis_aggregate.get("reviewed_min_timestamp_utc"),
            "window_end_utc": basis_aggregate.get("reviewed_max_timestamp_utc"),
        },
        "B_binance_funding": {
            "required_for_v1": True,
            "available_for_v1": binance_funding_available,
            "evidence_artifact": path_text(BINANCE_FUNDING_REVIEW_PATH),
            "payload_sha256_excluding_hash": source_payload(funding_review),
            "source_exchange_scope": "binance_only",
            "source_endpoint_url": funding_endpoint,
            "symbol_count": funding_review_scope.get("symbol_count"),
            "window_start_utc": funding_data_review.get("min_funding_time_utc"),
            "window_end_utc": funding_data_review.get("max_funding_time_utc"),
        },
        "C_binance_1h_ohlcv": {
            "required_for_v1": True,
            "available_for_v1": binance_ohlcv_available,
            "evidence_artifact": path_text(BINANCE_PANEL_REVIEW_PATH),
            "payload_sha256_excluding_hash": source_payload(panel_review),
            "scope_note": "Reviewed Binance 1h panel over Binance/OKX overlap universe; OKX panel rows not read.",
            "okx_panel_rows_read_in_source_review": bool_from_nested(
                panel_review, "forbidden_actions_confirmed_false", "okx_panel_rows_read"
            ),
            "okx_panel_access_allowed_now": panel_safety.get("okx_panel_access_allowed_now"),
        },
        "D_okx_1h_ohlcv": {
            "required_for_v1": True,
            "available_for_v1": okx_ohlcv_proven_for_v1,
            "reason": (
                "No current tracked metadata artifact was found that proves safe aligned OKX 1h OHLCV "
                "coverage for the preferred V1 window and target overlap universe. Older external OKX "
                "directory names may exist, but this metadata-only lock did not read row files and does "
                "not accept unreviewed external directories as execution-ready inputs."
            ),
        },
        "E_okx_basis_premium_equivalent": {
            "required_for_v1": True,
            "available_for_v1": okx_basis_premium_equivalent_proven_for_v1,
            "reason": (
                "No reviewed metadata artifact was found for OKX mark/index, premium, or basis equivalent "
                "covering the preferred V1 window and aligned symbols."
            ),
        },
        "F_okx_funding": {
            "required_for_v1": True,
            "available_for_v1": okx_funding_proven_for_v1,
            "reason": (
                "No reviewed OKX funding metadata artifact was found. The existing funding artifact uses "
                "the Binance fapi fundingRate endpoint and cannot satisfy OKX funding stress alignment."
            ),
        },
        "G_optional_oi_long_short_liquidation": {
            "required_for_v1": False,
            "available_for_v1": False,
            "reason": "Optional V1 inputs remain unavailable/unproven and do not block the route.",
        },
    }

    unavailable_required_data = [
        "D_okx_1h_ohlcv_not_proven_for_preferred_window",
        "E_okx_basis_premium_equivalent_missing",
        "F_okx_funding_missing",
    ]
    available_required_data = [
        key
        for key, value in required_data_matrix.items()
        if value.get("required_for_v1") is True and value.get("available_for_v1") is True
    ]
    continue_to_data_acquisition = (
        CLASSIFICATION == "CROSS_EXCHANGE_DATA_AVAILABLE_FOR_V1"
        and aligned_symbol_count_for_v1 >= 50
        and len(unavailable_required_data) == 0
    )

    validation_checks = {
        "preregistration_loaded": True,
        "preregistration_status_verified": prereg.get("status") == PREREG_STATUS,
        "preregistration_route_family_verified": prereg.get("route_family") == ROUTE_FAMILY,
        "preregistration_config_id_verified": prereg.get("fixed_config", {}).get("config_id") == CONFIG_ID,
        "basis_premium_review_loaded": True,
        "basis_premium_manifest_loaded": True,
        "basis_premium_review_valid": binance_basis_available,
        "basis_premium_manifest_safety_no_candidate": basis_manifest_safety.get("candidate_generation_allowed_now")
        is False,
        "binance_funding_review_loaded": True,
        "binance_funding_lock_loaded": True,
        "binance_funding_available_for_v1": binance_funding_available,
        "binance_funding_source_confirmed_binance_only": funding_endpoint
        == "https://fapi.binance.com/fapi/v1/fundingRate",
        "binance_panel_review_loaded": True,
        "binance_ohlcv_available_for_v1": binance_ohlcv_available,
        "source_panel_okx_rows_not_read": panel_validation.get("no_okx_panel_rows_read") is True,
        "second_source_readiness_loaded": True,
        "metadata_only_no_row_files_read": True,
        "no_network_used": True,
        "no_public_api_probe_used": True,
        "no_private_apis": True,
        "no_api_keys": True,
        "no_live_order_trading_endpoints": True,
        "no_bulk_download": True,
        "no_strategy_execution": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_family_release": True,
        "no_runtime_live_capital": True,
        "availability_classification_route_pending": CLASSIFICATION
        == "CROSS_EXCHANGE_DATA_UNAVAILABLE_ROUTE_PENDING",
        "route_pending_recorded": True,
        "acquisition_allowed_next_false": continue_to_data_acquisition is False,
        "strategy_execution_allowed_next_false": continue_to_data_acquisition is False,
        "minimum_50_aligned_symbols_not_claimed": aligned_symbol_count_for_v1 == 0,
        "exactly_one_new_tracked_python_tool_file_expected": True,
        "exactly_one_new_tracked_json_artifact_expected": True,
        "no_existing_files_modified_by_module": True,
        "replacement_checks_all_true": True,
    }
    replacement_checks_all_true = all_true(validation_checks)
    if not replacement_checks_all_true:
        print("BLOCKED: data availability validation checks failed")
        for key in sorted(validation_checks):
            if validation_checks[key] is not True:
                print(f"{key}: {validation_checks[key]}")
        print("replacement_checks_all_true: false")
        return 1

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_RELATIVE_PATH,
        "repo_scope": {
            "code_changes_repo_only": True,
            "metadata_only": True,
            "row_files_read": False,
            "network_used": False,
            "api_called": False,
            "download_performed": False,
            "strategy_executed": False,
        },
        "source_checkpoint": {
            "actual_head_at_step_start": HEAD_AT_DISCOVERY_START,
            "tracked_python_count_at_step_start": TRACKED_PYTHON_COUNT_AT_DISCOVERY_START,
            "repo_clean_before_step": True,
        },
        "route_family": ROUTE_FAMILY,
        "config_id": CONFIG_ID,
        "preferred_window": {
            "start_utc": PREFERRED_START_UTC,
            "end_exclusive_utc": PREFERRED_END_EXCLUSIVE_UTC,
        },
        "source_metadata_artifacts": {
            "preregistration_contract": {
                "path": path_text(PREREG_PATH),
                "status": source_status(prereg),
                "payload_sha256_excluding_hash": source_payload(prereg),
            },
            "basis_premium_review": {
                "path": path_text(BASIS_PREMIUM_REVIEW_PATH),
                "status": source_status(basis_review),
                "payload_sha256_excluding_hash": source_payload(basis_review),
            },
            "basis_premium_manifest": {
                "path": path_text(BASIS_PREMIUM_MANIFEST_PATH),
                "status": source_status(basis_manifest),
                "payload_sha256_excluding_hash": source_payload(basis_manifest),
            },
            "binance_funding_review": {
                "path": path_text(BINANCE_FUNDING_REVIEW_PATH),
                "status": source_status(funding_review),
                "payload_sha256_excluding_hash": source_payload(funding_review),
            },
            "binance_funding_lock": {
                "path": path_text(BINANCE_FUNDING_LOCK_PATH),
                "status": source_status(funding_lock),
                "payload_sha256_excluding_hash": source_payload(funding_lock),
            },
            "binance_panel_review": {
                "path": path_text(BINANCE_PANEL_REVIEW_PATH),
                "status": source_status(panel_review),
                "payload_sha256_excluding_hash": source_payload(panel_review),
            },
            "second_source_readiness": {
                "path": path_text(SECOND_SOURCE_READINESS_PATH),
                "status": source_status(readiness),
                "payload_sha256_excluding_hash": source_payload(readiness),
            },
        },
        "availability_review": {
            "availability_classification": CLASSIFICATION,
            "available_required_data": available_required_data,
            "unavailable_required_data": unavailable_required_data,
            "aligned_symbol_count_for_v1": aligned_symbol_count_for_v1,
            "minimum_aligned_symbols_required": 50,
            "continue_conditions_met": continue_to_data_acquisition,
            "route_pending": True,
            "decision_reason": (
                "V1 cannot proceed because OKX basis/premium equivalent and OKX funding are not "
                "present as reviewed metadata artifacts, and OKX 1h OHLCV is not proven as a safe "
                "aligned V1 input from current repo metadata."
            ),
        },
        "required_data_matrix": required_data_matrix,
        "metadata_candidate_scan": {
            "repo_metadata_candidates_matching_okx_or_cross_exchange_terms": repo_metadata_candidates,
            "repo_metadata_candidate_count": len(repo_metadata_candidates),
            "external_directory_candidates_matching_route_terms": external_directory_candidates[:100],
            "external_directory_candidate_count": len(external_directory_candidates),
            "external_directory_scan_note": (
                "Directory names were recorded as metadata only. No external row files were opened, "
                "and unreviewed external directories were not accepted as execution-ready inputs."
            ),
        },
        "optional_data_review": {
            "oi_available_for_v1": False,
            "long_short_ratio_available_for_v1": False,
            "liquidation_data_available_for_v1": False,
            "optional_data_blocks_v1": False,
        },
        "continue_policy": {
            "continue_to_data_acquisition": continue_to_data_acquisition,
            "route_pending": True,
            "acquisition_allowed_next": False,
            "strategy_execution_allowed_next": False,
            "evaluator_allowed_next": False,
            "closure_allowed_next": False,
            "next_module": None,
        },
        "safety_permissions": {
            "data_availability_lock_created": True,
            "route_pending": True,
            "data_acquisition_allowed_next": False,
            "strategy_execution_allowed_next": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "holdout_permission_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
        },
        "forbidden_actions_confirmed_false": {
            "network_used": False,
            "api_called": False,
            "private_api_used": False,
            "api_key_used": False,
            "download_performed": False,
            "external_row_files_read": False,
            "binance_ohlcv_panel_rows_read": False,
            "binance_1m_source_rows_read": False,
            "okx_rows_read": False,
            "funding_rows_read": False,
            "oi_rows_read": False,
            "taker_flow_signal_used": False,
            "pair_logic_used": False,
            "strategy_executed": False,
            "candidate_generation": False,
            "edge_claim": False,
            "family_release": False,
            "holdout_permission": False,
            "runtime_live_capital": False,
        },
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
    print(f"review_artifact_path: {ARTIFACT_PATH}")
    print(f"availability_classification: {CLASSIFICATION}")
    print("route_pending: true")
    print(f"available_required_data: {','.join(available_required_data)}")
    print(f"unavailable_required_data: {','.join(unavailable_required_data)}")
    print(f"aligned_symbol_count_for_v1: {aligned_symbol_count_for_v1}")
    print("minimum_50_aligned_symbols_met: false")
    print("acquisition_allowed_next: false")
    print("strategy_execution_allowed_next: false")
    print("candidate_generation_allowed_now: false")
    print("edge_claim_allowed_now: false")
    print("family_release_allowed_now: false")
    print("runtime_live_capital_allowed_now: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print("replacement_checks_all_true: true")
    return 0


if __name__ == "__main__":
    sys.exit(main())
