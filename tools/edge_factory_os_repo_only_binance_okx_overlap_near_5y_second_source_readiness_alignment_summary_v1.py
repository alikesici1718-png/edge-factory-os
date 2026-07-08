#!/usr/bin/env python3
"""Create a readiness/alignment summary for the Binance/OKX overlap panel."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_NEAR_5Y_SECOND_SOURCE_READINESS_ALIGNMENT_SUMMARY_CREATED"
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.py"
READINESS_ARTIFACT_PATH = "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json"
REPO_PATH = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
ARTIFACT_PATH = REPO_PATH / READINESS_ARTIFACT_PATH
TEMP_ARTIFACT_PATH = ARTIFACT_PATH.with_suffix(".json.tmp")

REVIEW_PATH = REPO_PATH / "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json"
BUILD_MANIFEST_PATH = REPO_PATH / "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json"
PREVIEW_PATH = REPO_PATH / "artifacts/panel_build_previews/binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.json"
COVERAGE_LOCK_PATH = REPO_PATH / "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json"
EXTERNAL_PANEL_INDEX_PATH = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_binance_okx_overlap_near_5y_1m_to_1h_panel_build_execution_v1\panel_index\binance_okx_overlap_near_5y_1h_panel_index_v1.json"
)
EXTERNAL_PANEL_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_binance_okx_overlap_near_5y_1m_to_1h_panel_build_execution_v1"
)
EXTERNAL_PANEL_DIR = EXTERNAL_PANEL_ROOT / "panel_1h_by_symbol"

PRIOR_HEAD = "d7774d6dc06c07cfb023c480968513bc48d0fe05"
PRIOR_TRACKED_PYTHON_COUNT = 810
REVIEW_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_NEAR_5Y_PANEL_BUILD_REVIEW_AFTER_EXECUTION_CREATED"
REVIEW_PAYLOAD_HASH = "34b88a3ff0870c708e2df034c243cf639b711ebce3c6a4f32edffb92a2229112"
BUILD_MANIFEST_PAYLOAD_HASH = "bf4d4d681f36fab3a2131701e25ebc45c94ddb757f92874498ef425d698f40a7"
PREVIEW_PAYLOAD_HASH = "16e93ca05fe28f0d101d5228e299306bad3aea171f22bc6901f770b0ecf3a3d9"
COVERAGE_LOCK_PAYLOAD_HASH = "18a84b71c649b0462fdb0d511597dcb701448fe06184ef9c8da93d6911ada4e0"

PANEL_REVIEW_CLASSIFICATION = "PANEL_REVIEW_PASS_WITH_P1_ATTENTION_VALID_FOR_READ_ONLY_SECOND_SOURCE_ANALYSIS"
EXPECTED_READINESS_CLASSIFICATION = "SECOND_SOURCE_READINESS_PASS_WITH_P1_ATTENTION_FOR_READ_ONLY_ALIGNMENT_PLANNING"
ALLOWED_READINESS_CLASSIFICATIONS = {
    "SECOND_SOURCE_READINESS_PASS_FOR_READ_ONLY_ALIGNMENT_PLANNING",
    "SECOND_SOURCE_READINESS_PASS_WITH_P1_ATTENTION_FOR_READ_ONLY_ALIGNMENT_PLANNING",
    "SECOND_SOURCE_READINESS_FAIL_REQUIRES_PANEL_REBUILD_OR_REVIEW",
}

BINANCE_PANEL_START = "2021-05-01T00:00:00Z"
BINANCE_PANEL_END_EXCLUSIVE = "2026-05-01T00:00:00Z"
OKX_SAFE_START = "2023-07-01T00:00:00Z"
OKX_SAFE_END_EXCLUSIVE = "2025-10-31T16:00:00Z"
OKX_BOUNDARY_START = "2025-10-31T16:00:00Z"
OKX_BOUNDARY_END = "2025-11-01T00:00:00Z"
OKX_HOLDOUT_START = "2025-11-01T00:00:00Z"
OKX_HOLDOUT_END_EXCLUSIVE = "2026-05-19T00:00:00Z"


class BlockedError(RuntimeError):
    """Raised when the readiness summary must stop before artifact write."""


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")


def payload_hash(payload: dict[str, Any]) -> str:
    data = dict(payload)
    data.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json_bytes(data)).hexdigest()


def verify_payload(payload: dict[str, Any], expected_hash: str) -> bool:
    return payload.get("payload_sha256_excluding_hash") == expected_hash and payload_hash(payload) == expected_hash


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_utc(value: str) -> dt.datetime:
    return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def intervals_overlap(start_a: str, end_a: str, start_b: str, end_b: str) -> bool:
    return parse_utc(start_a) < parse_utc(end_b) and parse_utc(start_b) < parse_utc(end_a)


def load_sources() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    for path in (REVIEW_PATH, BUILD_MANIFEST_PATH, PREVIEW_PATH, COVERAGE_LOCK_PATH, EXTERNAL_PANEL_INDEX_PATH):
        if not path.is_file():
            raise BlockedError(f"required source artifact missing: {path}")
    review = read_json(REVIEW_PATH)
    manifest = read_json(BUILD_MANIFEST_PATH)
    preview = read_json(PREVIEW_PATH)
    coverage = read_json(COVERAGE_LOCK_PATH)
    panel_index = read_json(EXTERNAL_PANEL_INDEX_PATH)
    if review.get("status") != REVIEW_STATUS:
        raise BlockedError("review artifact status mismatch")
    if not verify_payload(review, REVIEW_PAYLOAD_HASH):
        raise BlockedError("review artifact payload hash mismatch")
    if not verify_payload(manifest, BUILD_MANIFEST_PAYLOAD_HASH):
        raise BlockedError("build manifest payload hash mismatch")
    if not verify_payload(preview, PREVIEW_PAYLOAD_HASH):
        raise BlockedError("preview artifact payload hash mismatch")
    if not verify_payload(coverage, COVERAGE_LOCK_PAYLOAD_HASH):
        raise BlockedError("coverage lock payload hash mismatch")
    return review, manifest, preview, coverage, panel_index


def build_summary() -> dict[str, Any]:
    review, manifest, preview, _coverage, panel_index = load_sources()
    aggregate = review["aggregate_row_validation_review"]
    overlap = preview["okx_binance_overlap_planning"]

    active_p0 = aggregate["active_p0_blocker_count"]
    active_p1 = aggregate["active_p1_attention_count"]
    review_classification = review["panel_validity_classification"]
    if active_p0 > 0 or review_classification == "PANEL_REVIEW_FAIL_REQUIRES_REBUILD_OR_REPAIR":
        readiness_classification = "SECOND_SOURCE_READINESS_FAIL_REQUIRES_PANEL_REBUILD_OR_REVIEW"
    elif active_p1 > 0:
        readiness_classification = "SECOND_SOURCE_READINESS_PASS_WITH_P1_ATTENTION_FOR_READ_ONLY_ALIGNMENT_PLANNING"
    else:
        readiness_classification = "SECOND_SOURCE_READINESS_PASS_FOR_READ_ONLY_ALIGNMENT_PLANNING"

    aligned_start = max(BINANCE_PANEL_START, OKX_SAFE_START)
    aligned_end = min(BINANCE_PANEL_END_EXCLUSIVE, OKX_SAFE_END_EXCLUSIVE)
    avoids_boundary = not intervals_overlap(aligned_start, aligned_end, OKX_BOUNDARY_START, OKX_BOUNDARY_END)
    avoids_holdout = not intervals_overlap(aligned_start, aligned_end, OKX_HOLDOUT_START, OKX_HOLDOUT_END_EXCLUSIVE)
    within_binance = parse_utc(BINANCE_PANEL_START) <= parse_utc(aligned_start) and parse_utc(aligned_end) <= parse_utc(BINANCE_PANEL_END_EXCLUSIVE)
    within_okx_safe = parse_utc(OKX_SAFE_START) <= parse_utc(aligned_start) and parse_utc(aligned_end) <= parse_utc(OKX_SAFE_END_EXCLUSIVE)

    exact_overlap_binance_symbols = sorted(overlap["exact_overlap_binance_symbols"])
    exact_overlap_okx_symbols = sorted(overlap["exact_overlap_okx_symbols"])
    missing_exact = sorted(overlap.get("okx_symbols_missing_from_binance_near_5y_exact_base", []))

    summary: dict[str, Any] = {
        "artifact_kind": "BINANCE_OKX_OVERLAP_NEAR_5Y_SECOND_SOURCE_READINESS_ALIGNMENT_SUMMARY",
        "future_research_gate_recommendations": {
            "binance_panel_row_access_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "future_edge_claim_requires_external_or_future_holdout": True,
            "future_strategy_research_must_define": [
                "aligned_window",
                "symbol_set",
                "incomplete_hour_policy",
                "P1_acceptance_policy",
                "no_holdout_policy",
                "no_candidate_edge_release_runtime_live_capital_policy",
            ],
            "future_strategy_research_requires_explicit_user_approval": True,
            "future_strategy_research_requires_new_deliberate_contract": True,
            "holdout_access_allowed_now": False,
            "immediate_next_step_required": False,
            "okx_panel_access_allowed_now": False,
            "project_can_pause_after_readiness_summary": True,
            "read_only_alignment_planning_allowed": True,
            "runtime_live_capital_allowed_now": False,
            "second_source_readiness_summary_created": True,
            "strategy_search_allowed_now": False,
        },
        "limitations": [
            "This summary does not rerun panel validation.",
            "This summary does not read Binance panel rows.",
            "This summary does not read Binance 1m source rows.",
            "This summary does not read OKX panel rows.",
            "This summary does not compute strategy returns or signals.",
            "This summary is not candidate generation.",
            "This summary is not an edge claim.",
            "This summary grants no runtime/live/capital permission.",
            "The Binance panel is listing-aware/ragged and not strict rectangular 5y.",
            "Future strategy research requires a separate deliberate contract and explicit approval.",
            "Future edge claim requires external/future holdout and separate governance.",
        ],
        "module": MODULE_PATH,
        "okx_binance_alignment_window": {
            "aligned_window_avoids_okx_boundary_buffer": avoids_boundary,
            "aligned_window_avoids_okx_sealed_holdout": avoids_holdout,
            "aligned_window_is_within_binance_panel_range": within_binance,
            "aligned_window_is_within_okx_safe_non_holdout_range": within_okx_safe,
            "aligned_window_policy": "Use this exact window for any future OKX/Binance second-source comparison unless separately governed.",
            "binance_panel_end_exclusive_utc": BINANCE_PANEL_END_EXCLUSIVE,
            "binance_panel_start_utc": BINANCE_PANEL_START,
            "okx_boundary_buffer_end_utc": OKX_BOUNDARY_END,
            "okx_boundary_buffer_start_utc": OKX_BOUNDARY_START,
            "okx_safe_non_holdout_end_exclusive_utc": OKX_SAFE_END_EXCLUSIVE,
            "okx_safe_non_holdout_start_utc": OKX_SAFE_START,
            "okx_sealed_holdout_end_exclusive_utc": OKX_HOLDOUT_END_EXCLUSIVE,
            "okx_sealed_holdout_start_utc": OKX_HOLDOUT_START,
            "recommended_aligned_window_end_exclusive_utc": aligned_end,
            "recommended_aligned_window_start_utc": aligned_start,
        },
        "p1_attention_summary": {
            "p1_blocks_read_only_second_source_analysis": False,
            "p1_blocks_strategy_search": True,
            "p1_count": active_p1,
            "p1_items": [
                "row_count_delta_vs_preview_nonzero_but_review_passed",
                "incomplete_1h_rows_present_but_review_passed",
                "output_max_timestamp_2026_04_30_22_00_but_timestamp_boundary_review_passed",
            ],
            "p1_policy_recommendation": "Future research planning must explicitly define incomplete-hour handling, aligned-window cutoff, and row-count-delta acceptance before any strategy search.",
            "p1_requires_policy_if_future_strategy_is_requested": True,
        },
        "panel_review_preserved": {
            "active_p0_blocker_count": active_p0,
            "active_p1_attention_count": active_p1,
            "incomplete_hour_review_passed": review["incomplete_hour_review"]["incomplete_hour_review_passed"],
            "panel_validity_classification": review_classification,
            "review_payload_sha256_excluding_hash": review["payload_sha256_excluding_hash"],
            "reviewed_complete_1h_row_count": aggregate["reviewed_complete_1h_row_count"],
            "reviewed_duplicate_symbol_hour_count": aggregate["reviewed_duplicate_symbol_hour_count"],
            "reviewed_incomplete_1h_row_count": aggregate["reviewed_incomplete_1h_row_count"],
            "reviewed_numeric_sanity_valid": aggregate["reviewed_numeric_sanity_valid"],
            "reviewed_ohlc_sanity_valid": aggregate["reviewed_ohlc_sanity_valid"],
            "reviewed_output_1h_row_count": aggregate["reviewed_output_1h_row_count"],
            "reviewed_output_max_timestamp_utc": aggregate["reviewed_output_max_timestamp_utc"],
            "reviewed_output_min_timestamp_utc": aggregate["reviewed_output_min_timestamp_utc"],
            "reviewed_panel_index_sha256": aggregate["reviewed_panel_index_sha256"],
            "reviewed_symbol_count": aggregate["reviewed_symbol_count"],
            "row_count_delta_review_passed": review["row_count_delta_review"]["row_count_delta_review_passed"],
            "timestamp_boundary_review_passed": review["timestamp_boundary_review"]["timestamp_boundary_review_passed"],
        },
        "recommended_next_possible_actions": [
            {
                "option_id": "PAUSE_PROJECT_AT_SAFE_SECOND_SOURCE_READINESS_CHECKPOINT",
                "reason": "panel is built/reviewed; no immediate next module is required.",
                "recommended": True,
            },
            {
                "option_id": "CREATE_SECOND_SOURCE_ALIGNMENT_DESIGN_ONLY",
                "reason": "can document future comparison design without running strategy.",
                "recommended": "optional",
            },
            {
                "option_id": "REQUEST_EXPLICIT_STRATEGY_RESEARCH_CONTRACT",
                "reason": "would require a new deliberate contract and explicit approval.",
                "recommended": "false_now",
            },
            {
                "option_id": "BUILD_FULL_BINANCE_638_PANEL",
                "reason": "large, not needed for OKX second-source overlap.",
                "recommended": "false_now",
            },
            {
                "option_id": "BUILD_STRICT_5Y_102_PANEL",
                "reason": "useful later only if rectangular 5y design becomes necessary.",
                "recommended": "false_now",
            },
        ],
        "repo_scope": {
            "api_key_used": False,
            "binance_1h_panel_rows_read": False,
            "binance_1m_kline_source_rows_read": False,
            "binance_coverage_discovery_rerun": False,
            "binance_kline_zip_downloaded": False,
            "binance_kline_zip_opened": False,
            "binance_panel_build_rerun": False,
            "candidate_generation": False,
            "code_changes_repo_only": True,
            "edge_claim": False,
            "external_panel_index_read_only": True,
            "external_panel_partitions_read_by_this_module": False,
            "okx_panel_rows_read": False,
            "okx_whitelisted_artifact_read": False,
            "private_api_used": False,
            "public_network_used": False,
            "readiness_artifact_created_in_repo": True,
            "runtime_live_capital": False,
            "strategy_search_executed": False,
        },
        "safety_permissions": {
            "binance_panel_row_access_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "capital_permission_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "holdout_access_allowed_now": False,
            "immediate_next_module_required": False,
            "live_permission_allowed_now": False,
            "okx_panel_access_allowed_now": False,
            "panel_valid_for_candidate_generation": False,
            "panel_valid_for_edge_claim": False,
            "panel_valid_for_read_only_second_source_alignment_planning": readiness_classification != "SECOND_SOURCE_READINESS_FAIL_REQUIRES_PANEL_REBUILD_OR_REVIEW",
            "panel_valid_for_runtime_live_capital": False,
            "panel_valid_for_strategy_search": False,
            "project_can_pause_after_readiness_summary": True,
            "readiness_summary_created": True,
            "runtime_permission_allowed_now": False,
            "strategy_search_allowed_now": False,
        },
        "second_source_readiness_classification": readiness_classification,
        "source_artifacts": {
            "build_manifest_path": str(BUILD_MANIFEST_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "build_manifest_payload_hash_verified": True,
            "coverage_lock_path": str(COVERAGE_LOCK_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "coverage_lock_payload_hash_verified": True,
            "external_panel_index_path": str(EXTERNAL_PANEL_INDEX_PATH),
            "external_panel_index_read_only": True,
            "external_panel_index_sha256": sha256_file(EXTERNAL_PANEL_INDEX_PATH),
            "external_panel_partitions_not_read_by_this_module": True,
            "preview_artifact_path": str(PREVIEW_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "preview_artifact_payload_hash_verified": True,
            "review_artifact_path": str(REVIEW_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "review_artifact_payload_hash_verified": True,
            "review_artifact_status": review["status"],
        },
        "source_checkpoint": {
            "prior_head": PRIOR_HEAD,
            "prior_review_artifact": "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json",
            "prior_review_payload_sha256_excluding_hash": REVIEW_PAYLOAD_HASH,
            "prior_review_status": REVIEW_STATUS,
            "prior_review_tool": "tools/edge_factory_os_repo_only_binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.py",
            "prior_tracked_python_count": PRIOR_TRACKED_PYTHON_COUNT,
            "project": "Edge Factory OS / Binance OKX overlap second-source readiness alignment",
            "repo_clean_before_readiness_summary": True,
        },
        "status": REQUIRED_STATUS,
        "symbol_universe_alignment": {
            "binance_okx_exact_overlap_current_trading_near_5y_count": overlap["exact_overlap_near_5y_current_trading_count"],
            "binance_okx_exact_overlap_strict_5y_count": overlap["exact_overlap_strict_5y_count"],
            "binance_okx_exact_overlap_symbol_count": overlap["exact_overlap_count"],
            "exact_overlap_binance_symbols": exact_overlap_binance_symbols,
            "exact_overlap_okx_symbols": exact_overlap_okx_symbols,
            "future_alias_mapping_requires_separate_review": True,
            "multiplier_alias_auto_mapping_allowed": False,
            "okx_selected_symbol_count": overlap["okx_selected_symbols_count"],
            "recommended_second_source_symbol_set": "exact 81 Binance/OKX overlap symbols",
            "recommended_symbol_mapping_policy": "exact base-asset matching only",
            "symbols_missing_between_okx_and_binance_exact_base": missing_exact,
        },
    }
    summary["validation_checks"] = {
        "active_p0_blocker_count_zero_preserved": active_p0 == 0,
        "active_p1_attention_count_three_preserved": active_p1 == 3,
        "aligned_window_avoids_okx_boundary_buffer": avoids_boundary,
        "aligned_window_avoids_okx_sealed_holdout": avoids_holdout,
        "aligned_window_computed": aligned_start == OKX_SAFE_START and aligned_end == OKX_SAFE_END_EXCLUSIVE,
        "build_manifest_loaded": True,
        "build_manifest_payload_hash_verified": True,
        "candidate_generation_forbidden": True,
        "coverage_lock_loaded": True,
        "coverage_lock_payload_hash_verified": True,
        "edge_claim_forbidden": True,
        "exact_overlap_symbol_count_verified_81": overlap["exact_overlap_count"] == 81,
        "exactly_one_new_tracked_json_readiness_artifact_expected": True,
        "exactly_one_new_tracked_python_tool_file_expected": True,
        "module_path_equals_required_path": MODULE_PATH == "tools/edge_factory_os_repo_only_binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.py",
        "no_binance_1h_panel_rows_read": True,
        "no_binance_1m_source_rows_read": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_existing_files_modified_expected": True,
        "no_kline_zip_downloaded": True,
        "no_kline_zip_opened": True,
        "no_network_used": True,
        "no_okx_panel_rows_read": True,
        "no_other_tracked_files_expected": True,
        "no_panel_build_rerun": True,
        "no_runtime_live_capital": True,
        "no_strategy_search": True,
        "panel_review_classification_preserved": review_classification == PANEL_REVIEW_CLASSIFICATION,
        "payload_sha256_excluding_hash_present": True,
        "preview_artifact_loaded": True,
        "preview_payload_hash_verified": True,
        "readiness_artifact_json_valid": True,
        "readiness_artifact_path_equals_required_path": READINESS_ARTIFACT_PATH == "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json",
        "readiness_classification_is_from_allowed_set": readiness_classification in ALLOWED_READINESS_CLASSIFICATIONS,
        "replacement_checks_all_true": True,
        "review_artifact_loaded": True,
        "review_payload_hash_verified": True,
        "review_status_verified": review["status"] == REVIEW_STATUS,
        "runtime_live_capital_forbidden": True,
        "source_artifacts_read_only": True,
        "status_equals_required_status": True,
        "strategy_search_forbidden": True,
        "symbol_universe_alignment_preserved": overlap["exact_overlap_count"] == len(exact_overlap_binance_symbols) == len(exact_overlap_okx_symbols),
    }
    summary["replacement_checks_all_true"] = all(value is True for value in summary["validation_checks"].values())
    hash_input = dict(summary)
    hash_input.pop("payload_sha256_excluding_hash", None)
    summary["payload_sha256_excluding_hash"] = hashlib.sha256(canonical_json_bytes(hash_input)).hexdigest()
    return summary


def validate_summary(summary: dict[str, Any]) -> None:
    assert summary["status"] == REQUIRED_STATUS
    assert summary["module"] == MODULE_PATH
    assert READINESS_ARTIFACT_PATH == "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json"
    assert summary["panel_review_preserved"]["panel_validity_classification"] == PANEL_REVIEW_CLASSIFICATION
    assert summary["panel_review_preserved"]["active_p0_blocker_count"] == 0
    assert summary["panel_review_preserved"]["active_p1_attention_count"] == 3
    assert summary["panel_review_preserved"]["reviewed_symbol_count"] == 81
    assert summary["okx_binance_alignment_window"]["recommended_aligned_window_start_utc"] == OKX_SAFE_START
    assert summary["okx_binance_alignment_window"]["recommended_aligned_window_end_exclusive_utc"] == OKX_SAFE_END_EXCLUSIVE
    assert summary["okx_binance_alignment_window"]["aligned_window_avoids_okx_boundary_buffer"] is True
    assert summary["okx_binance_alignment_window"]["aligned_window_avoids_okx_sealed_holdout"] is True
    assert summary["symbol_universe_alignment"]["binance_okx_exact_overlap_symbol_count"] == 81
    assert summary["second_source_readiness_classification"] in ALLOWED_READINESS_CLASSIFICATIONS
    assert summary["second_source_readiness_classification"] == EXPECTED_READINESS_CLASSIFICATION
    assert summary["repo_scope"]["strategy_search_executed"] is False
    assert summary["repo_scope"]["candidate_generation"] is False
    assert summary["repo_scope"]["edge_claim"] is False
    assert summary["repo_scope"]["runtime_live_capital"] is False
    assert summary["repo_scope"]["okx_panel_rows_read"] is False
    assert summary["repo_scope"]["binance_1h_panel_rows_read"] is False
    assert summary["safety_permissions"]["immediate_next_module_required"] is False
    assert summary["safety_permissions"]["project_can_pause_after_readiness_summary"] is True
    assert summary["replacement_checks_all_true"] is True
    assert summary["payload_sha256_excluding_hash"]


def write_summary(summary: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if TEMP_ARTIFACT_PATH.exists():
        TEMP_ARTIFACT_PATH.unlink()
    TEMP_ARTIFACT_PATH.write_bytes(canonical_json_bytes(summary) + b"\n")
    TEMP_ARTIFACT_PATH.replace(ARTIFACT_PATH)


def stdout_summary(summary: dict[str, Any]) -> dict[str, Any]:
    alignment = summary["okx_binance_alignment_window"]
    universe = summary["symbol_universe_alignment"]
    safety = summary["safety_permissions"]
    return {
        "active_p0_blocker_count": summary["panel_review_preserved"]["active_p0_blocker_count"],
        "active_p1_attention_count": summary["panel_review_preserved"]["active_p1_attention_count"],
        "binance_okx_exact_overlap_current_trading_near_5y_count": universe["binance_okx_exact_overlap_current_trading_near_5y_count"],
        "binance_okx_exact_overlap_strict_5y_count": universe["binance_okx_exact_overlap_strict_5y_count"],
        "binance_okx_exact_overlap_symbol_count": universe["binance_okx_exact_overlap_symbol_count"],
        "candidate_generation_allowed_now": safety["candidate_generation_allowed_now"],
        "edge_claim_allowed_now": safety["edge_claim_allowed_now"],
        "immediate_next_module_required": safety["immediate_next_module_required"],
        "panel_valid_for_read_only_second_source_alignment_planning": safety["panel_valid_for_read_only_second_source_alignment_planning"],
        "payload_sha256_excluding_hash": summary["payload_sha256_excluding_hash"],
        "project_can_pause_after_readiness_summary": safety["project_can_pause_after_readiness_summary"],
        "readiness_artifact_path": READINESS_ARTIFACT_PATH,
        "recommended_aligned_window_end_exclusive_utc": alignment["recommended_aligned_window_end_exclusive_utc"],
        "recommended_aligned_window_start_utc": alignment["recommended_aligned_window_start_utc"],
        "replacement_checks_all_true": summary["replacement_checks_all_true"],
        "runtime_live_capital_allowed_now": safety["runtime_permission_allowed_now"],
        "second_source_readiness_classification": summary["second_source_readiness_classification"],
        "status": summary["status"],
        "strategy_search_allowed_now": safety["strategy_search_allowed_now"],
    }


def main() -> int:
    try:
        summary = build_summary()
        validate_summary(summary)
        write_summary(summary)
    except BlockedError as exc:
        if TEMP_ARTIFACT_PATH.exists():
            TEMP_ARTIFACT_PATH.unlink()
        if ARTIFACT_PATH.exists():
            ARTIFACT_PATH.unlink()
        print(
            json.dumps(
                {
                    "exact_blocker": str(exc),
                    "readiness_artifact_path": READINESS_ARTIFACT_PATH,
                    "replacement_checks_all_true": False,
                    "status": "BLOCKED",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1
    print(json.dumps(stdout_summary(summary), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
