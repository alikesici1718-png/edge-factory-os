#!/usr/bin/env python3
"""Finalize manifest/provenance after partial-output forensic validation.

This module binds the existing forensic-validated revised non-holdout output as
a validated research input artifact by writing manifest/provenance/schema and
eligibility records. It does not build data, aggregate, run strategy search,
generate candidates, claim edge, access holdout/source rows, or modify the
validated output file.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path(
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_partial_output_finalize_manifest_after_forensic_validation_v1.py"
)
OUTPUT_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_partial_output_finalize_manifest_after_forensic_validation_v1"
)

EXPECTED_HEAD = "81647db3649b907746da310de9e0b25916c7b242"
VALIDATION_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_execution_after_preview_v1"
)
VALIDATION_REPORT = (
    VALIDATION_DIR
    / "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_execution_report.json"
)
VALIDATION_COUNTS = (
    VALIDATION_DIR / "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_counts.json"
)
VALIDATION_SCHEMA = (
    VALIDATION_DIR
    / "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_schema_numeric_sanity.json"
)
VALIDATION_OHLC = (
    VALIDATION_DIR / "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_ohlc_sanity.json"
)
VALIDATION_RECONCILIATION = (
    VALIDATION_DIR
    / "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_complete_incomplete_reconciliation.json"
)
PREVIEW_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_preview_after_resumable_plan_v1"
)
PREVIEW = PREVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_preview.json"
RESUMABLE_PLAN_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_build_resumable_execution_plan_after_stall_diagnostic_v1"
)
RESUMABLE_PLAN = RESUMABLE_PLAN_DIR / "repo_only_okx_88_symbol_1h_panel_revised_build_resumable_execution_plan.json"
DATE_POLICY_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign_after_boundary_reconciliation_v1"
)
DATE_POLICY = DATE_POLICY_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign.json"
RETRY_PREVIEW_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_retry_preview_after_date_policy_redesign_v1"
)
RETRY_PREVIEW = RETRY_PREVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_retry_preview.json"
HOLDOUT_REGISTRY_DIR = (
    EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_registry_builder_before_strategy_search_v1"
)
HOLDOUT_REGISTRY = HOLDOUT_REGISTRY_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_registry.json"
HOLDOUT_ACCESS_RULES = HOLDOUT_REGISTRY_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_access_rules.json"

PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_PARTIAL_OUTPUT_FINALIZE_MANIFEST_COMPLETE"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_PARTIAL_OUTPUT_FINALIZE_MANIFEST_REVIEW_REQUIRED"
NEXT_PASS_MODULE = (
    "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_preview_after_revised_non_holdout_view_finalization_v1.py"
)
NEXT_BLOCKED_MODULE = (
    "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_partial_output_finalize_manifest_blocked_record_v1.py"
)
PASS_QUALITY = "OKX_88_SYMBOL_1H_PANEL_REVISED_NON_HOLDOUT_VIEW_FINALIZED_STRATEGY_RETRY_PREVIEW_NEXT"
BLOCKED_QUALITY = "OKX_88_SYMBOL_1H_PANEL_REVISED_NON_HOLDOUT_VIEW_FINALIZATION_BLOCKED_REVIEW_REQUIRED"

EXPECTED_VALIDATION_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_PARTIAL_OUTPUT_FORENSIC_VALIDATION_EXECUTION_PASSED"
EXPECTED_OUTPUT_1H_ROW_COUNT = 1_802_944
EXPECTED_SYMBOL_COUNT = 88
EXPECTED_ROWS_PER_SYMBOL = 20_488
EXPECTED_START = "2023-07-01T00:00:00Z"
EXPECTED_END_EXCLUSIVE = "2025-10-31T16:00:00Z"
EXPECTED_MAX_TIMESTAMP = "2025-10-31T15:00:00Z"
EXPECTED_COMPLETE_ROWS = 1_802_935
EXPECTED_INCOMPLETE_ROWS = 9


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git(args: list[str]) -> str:
    proc = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={REPO.as_posix()}", "-C", str(REPO), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} did not contain a JSON object")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def tracked_python_count() -> int:
    output = git(["ls-files", "*.py"])
    return len([line for line in output.splitlines() if line.strip()])


def clean_status_allowing_tool() -> tuple[bool, list[str]]:
    lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_suffix = TOOL_REL.as_posix()
    unexpected = [line for line in lines if not line.replace("\\", "/").endswith(allowed_suffix)]
    return not unexpected, unexpected


def load_input(label: str, path: Path, errors: dict[str, str]) -> dict[str, Any]:
    try:
        return read_json(path)
    except (OSError, json.JSONDecodeError, RuntimeError) as exc:
        errors[label] = f"{path}: {exc}"
        return {}


def file_metadata(path: Path) -> dict[str, Any]:
    try:
        stat = path.stat()
    except OSError as exc:
        return {"exists": False, "metadata_error": str(exc), "path": str(path)}
    modified = datetime.fromtimestamp(stat.st_mtime, timezone.utc).replace(microsecond=0)
    return {
        "exists": path.is_file(),
        "modified_time": modified.isoformat().replace("+00:00", "Z"),
        "path": str(path),
        "size_bytes": stat.st_size,
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validation_confirmed(report: dict[str, Any]) -> bool:
    return (
        report.get("okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_execution_status")
        == EXPECTED_VALIDATION_STATUS
        and report.get("forensic_validation_execution_performed") is True
        and report.get("forensic_validation_preview_confirmed") is True
        and report.get("partial_output_exists") is True
        and report.get("partial_output_forensic_validation_passed") is True
        and report.get("partial_output_valid_after_forensic_validation") is True
        and report.get("partial_output_promotable_to_validated_non_holdout_view") is True
        and report.get("output_valid_for_strategy_search_after_forensic_validation") is False
        and report.get("output_valid_for_edge_claim") is False
        and report.get("output_1h_row_count") == EXPECTED_OUTPUT_1H_ROW_COUNT
        and report.get("row_count_valid") is True
        and report.get("output_symbol_count") == EXPECTED_SYMBOL_COUNT
        and report.get("symbol_count_valid") is True
        and report.get("expected_rows_per_symbol") == EXPECTED_ROWS_PER_SYMBOL
        and report.get("per_symbol_output_row_count_valid") is True
        and report.get("duplicate_symbol_hour_count") == 0
        and report.get("duplicate_symbol_hour_count_valid") is True
        and report.get("output_min_timestamp") == EXPECTED_START
        and report.get("output_max_timestamp") == EXPECTED_MAX_TIMESTAMP
        and report.get("output_timestamps_all_gte_revised_start") is True
        and report.get("output_timestamps_all_lt_revised_end_exclusive") is True
        and report.get("output_timestamps_all_lt_sealed_holdout_start") is True
        and report.get("boundary_buffer_rows_written_count") == 0
        and report.get("sealed_holdout_rows_written_count") == 0
        and report.get("output_schema_validated") is True
        and report.get("required_columns_present") is True
        and report.get("invalid_numeric_row_count") == 0
        and report.get("nan_inf_row_count") == 0
        and report.get("negative_volume_row_count") == 0
        and report.get("numeric_sanity_valid") is True
        and report.get("ohlc_sanity_valid") is True
        and report.get("complete_1h_row_count") == EXPECTED_COMPLETE_ROWS
        and report.get("incomplete_1h_row_count") == EXPECTED_INCOMPLETE_ROWS
        and report.get("complete_incomplete_reconciliation_valid") is True
        and report.get("synthetic_fill_used") is False
        and report.get("forward_fill_used") is False
        and report.get("backfill_used") is False
        and report.get("original_source_full_csv_read_performed") is False
        and report.get("current_all_in_one_panel_read_performed") is False
        and report.get("sealed_holdout_source_file_read_count") == 0
        and report.get("revised_build_rerun_performed") is False
        and report.get("partial_output_modified") is False
        and report.get("partial_output_deleted") is False
        and report.get("partial_output_quarantined") is False
        and report.get("strategy_search_executed") is False
        and report.get("candidate_generation_performed") is False
        and report.get("edge_claim_performed") is False
        and report.get("approval_grants_future_finalize_manifest_next") is True
        and report.get("replacement_checks_all_true") is True
        and report.get("next_module") == TOOL_REL.name
    )


def build_outputs() -> dict[str, dict[str, Any]]:
    head = git(["rev-parse", "HEAD"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    load_errors: dict[str, str] = {}
    validation = load_input("forensic_validation_execution_report", VALIDATION_REPORT, load_errors)
    counts = load_input("forensic_validation_counts", VALIDATION_COUNTS, load_errors)
    schema = load_input("forensic_validation_schema_numeric_sanity", VALIDATION_SCHEMA, load_errors)
    ohlc = load_input("forensic_validation_ohlc_sanity", VALIDATION_OHLC, load_errors)
    reconciliation = load_input("forensic_validation_reconciliation", VALIDATION_RECONCILIATION, load_errors)
    preview = load_input("forensic_validation_preview", PREVIEW, load_errors)
    resumable_plan = load_input("resumable_execution_plan", RESUMABLE_PLAN, load_errors)
    date_policy = load_input("date_policy_redesign", DATE_POLICY, load_errors)
    retry_preview = load_input("revised_build_retry_preview", RETRY_PREVIEW, load_errors)
    holdout_registry = load_input("holdout_registry", HOLDOUT_REGISTRY, load_errors)
    holdout_access_rules = load_input("holdout_access_rules", HOLDOUT_ACCESS_RULES, load_errors)

    output_path_text = validation.get("partial_output_path")
    output_path = Path(output_path_text) if isinstance(output_path_text, str) and output_path_text else None
    before_metadata = file_metadata(output_path) if output_path else {"exists": False}
    hash_from_validation = validation.get("output_sha256") or validation.get("output_hash")
    output_hash_computed_now = not bool(hash_from_validation)
    output_hash = None
    if output_path and before_metadata.get("exists") is True:
        output_hash = hash_from_validation or sha256_file(output_path)
    after_metadata = file_metadata(output_path) if output_path else {"exists": False}

    output_file_modified = before_metadata != after_metadata
    output_file_deleted = after_metadata.get("exists") is not True
    output_file_moved = False
    output_file_quarantined = False
    forensic_ok = validation_confirmed(validation)
    related_artifacts_loaded = all(
        bool(item)
        for item in [
            counts,
            schema,
            ohlc,
            reconciliation,
            preview,
            resumable_plan,
            date_policy,
            retry_preview,
            holdout_registry,
            holdout_access_rules,
        ]
    )

    approval = {
        "approval_grants_finalize_manifest_now": True,
        "approval_grants_future_restricted_strategy_search_retry_preview_next": True,
        "approval_grants_strategy_search_execution_now": False,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_family_release_now": False,
        "approval_grants_runtime_live_capital_now": False,
        "approval_grants_holdout_access_now": False,
        "approval_grants_build_rerun_now": False,
        "approval_grants_cleanup_now": False,
    }
    action_state = {
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "original_source_full_csv_read_performed": False,
        "current_all_in_one_panel_read_performed": False,
        "sealed_holdout_source_file_read_count": 0,
        "revised_build_rerun_performed": False,
        "strategy_search_executed": False,
        "candidate_generation_performed": False,
        "edge_claim_performed": False,
    }
    eligibility = {
        "output_valid_for_strategy_search_after_finalization": True,
        "output_valid_for_restricted_momentum_search_input": True,
        "output_valid_for_edge_claim": False,
        "output_valid_for_final_edge_claim": False,
        "output_valid_for_runtime_or_live": False,
        "strategy_search_allowed_now": False,
        "retry_strategy_search_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
        "runtime_live_capital_allowed_now": False,
        "future_restricted_strategy_search_retry_preview_allowed_next": True,
    }

    replacement_checks = {
        "current_head_matches_expected": head == EXPECTED_HEAD,
        "repo_clean_except_current_tool": repo_clean,
        "forensic_validation_confirmed": forensic_ok,
        "related_artifacts_loaded": related_artifacts_loaded,
        "output_file_exists": before_metadata.get("exists") is True,
        "output_file_not_modified": not output_file_modified,
        "output_file_not_deleted": not output_file_deleted,
        "output_file_not_moved": not output_file_moved,
        "output_file_not_quarantined": not output_file_quarantined,
        "output_hash_available": bool(output_hash),
        "edge_claim_not_enabled": eligibility["output_valid_for_edge_claim"] is False
        and eligibility["output_valid_for_final_edge_claim"] is False,
        "runtime_live_not_enabled": eligibility["output_valid_for_runtime_or_live"] is False,
        "strategy_execution_blocked_now": eligibility["strategy_search_allowed_now"] is False,
        "no_strategy_candidate_edge_execution": action_state["strategy_search_executed"] is False
        and action_state["candidate_generation_performed"] is False
        and action_state["edge_claim_performed"] is False,
        "no_build_or_aggregation": action_state["data_build_performed"] is False
        and action_state["aggregation_performed_now"] is False,
        "no_forbidden_source_or_panel_reads": action_state["original_source_full_csv_read_performed"] is False
        and action_state["current_all_in_one_panel_read_performed"] is False
        and action_state["sealed_holdout_source_file_read_count"] == 0,
    }
    replacement_checks_all_true = all(replacement_checks.values()) and not load_errors
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    next_module = NEXT_PASS_MODULE if replacement_checks_all_true else NEXT_BLOCKED_MODULE
    quality = PASS_QUALITY if replacement_checks_all_true else BLOCKED_QUALITY

    base = {
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": 0,
        "boundary_buffer_rows_written_count": validation.get("boundary_buffer_rows_written_count"),
        "complete_1h_row_count": validation.get("complete_1h_row_count"),
        "complete_incomplete_reconciliation_valid": validation.get("complete_incomplete_reconciliation_valid"),
        "created_at_utc": now_utc(),
        "current_evidence_chain_quality_after_finalize_manifest": quality,
        "duplicate_symbol_hour_count": validation.get("duplicate_symbol_hour_count"),
        "expected_output_1h_row_count": EXPECTED_OUTPUT_1H_ROW_COUNT,
        "expected_rows_per_symbol": EXPECTED_ROWS_PER_SYMBOL,
        "expected_symbol_count": EXPECTED_SYMBOL_COUNT,
        "final_eligibility_record_created": replacement_checks_all_true,
        "final_manifest_created": replacement_checks_all_true,
        "final_provenance_created": replacement_checks_all_true,
        "final_schema_binding_created": replacement_checks_all_true,
        "finalize_manifest_performed": replacement_checks_all_true,
        "forensic_validation_confirmed": forensic_ok,
        "holdout_registry_artifact_path": str(HOLDOUT_REGISTRY),
        "incomplete_1h_row_count": validation.get("incomplete_1h_row_count"),
        "load_errors": load_errors,
        "next_module": next_module,
        "numeric_sanity_valid": validation.get("numeric_sanity_valid"),
        "ohlc_sanity_valid": validation.get("ohlc_sanity_valid"),
        "okx_88_symbol_1h_panel_revised_partial_output_finalize_manifest_status": status,
        "output_1h_row_count": validation.get("output_1h_row_count"),
        "output_file_after_metadata": after_metadata,
        "output_file_before_metadata": before_metadata,
        "output_file_deleted": output_file_deleted,
        "output_file_modified": output_file_modified,
        "output_file_moved": output_file_moved,
        "output_file_path": str(output_path) if output_path else None,
        "output_file_quarantined": output_file_quarantined,
        "output_hash": output_hash,
        "output_hash_available": bool(output_hash),
        "output_hash_computed_now": output_hash_computed_now,
        "output_max_timestamp": validation.get("output_max_timestamp"),
        "output_min_timestamp": validation.get("output_min_timestamp"),
        "output_promoted_to_validated_revised_non_holdout_view": replacement_checks_all_true,
        "output_schema_columns": validation.get("output_schema_columns"),
        "output_symbol_count": validation.get("output_symbol_count"),
        "output_timestamps_all_gte_revised_start": validation.get("output_timestamps_all_gte_revised_start"),
        "output_timestamps_all_lt_revised_end_exclusive": validation.get(
            "output_timestamps_all_lt_revised_end_exclusive"
        ),
        "output_timestamps_all_lt_sealed_holdout_start": validation.get(
            "output_timestamps_all_lt_sealed_holdout_start"
        ),
        "partial_output_forensic_validation_passed": validation.get("partial_output_forensic_validation_passed"),
        "partial_output_valid_after_forensic_validation": validation.get("partial_output_valid_after_forensic_validation"),
        "per_symbol_output_row_count_valid": validation.get("per_symbol_output_row_count_valid"),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "revised_non_holdout_view_end_exclusive": EXPECTED_END_EXCLUSIVE,
        "revised_non_holdout_view_start": EXPECTED_START,
        "sealed_holdout_rows_written_count": validation.get("sealed_holdout_rows_written_count"),
        "selected_symbol_count": EXPECTED_SYMBOL_COUNT,
        "synthetic_fill_used": validation.get("synthetic_fill_used"),
        "forward_fill_used": validation.get("forward_fill_used"),
        "backfill_used": validation.get("backfill_used"),
        "tracked_python_count_at_finalize_manifest_run": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
    }
    base.update(approval)
    base.update(action_state)
    base.update(eligibility)

    manifest = {
        **base,
        "artifact_semantics": "revised OKX 88-symbol non-holdout 1h panel",
        "physically_excludes_boundary_buffer": True,
        "physically_excludes_sealed_holdout": True,
        "not_final_holdout_proof": True,
    }
    schema_binding = {
        **base,
        "schema_columns": validation.get("output_schema_columns"),
        "schema_source": str(VALIDATION_SCHEMA),
        "schema_validated_by_forensic_execution": True,
    }
    provenance = {
        **base,
        "date_policy_artifact": str(DATE_POLICY),
        "forensic_validation_artifact": str(VALIDATION_REPORT),
        "hash_policy": "computed now by stream-reading only the finalized output file"
        if output_hash_computed_now
        else "reused from forensic validation artifact",
        "resumable_plan_artifact": str(RESUMABLE_PLAN),
        "retry_preview_artifact": str(RETRY_PREVIEW),
    }
    eligibility_record = {
        **base,
        "eligibility_reason": (
            "Finalization binds the forensic-validated non-holdout view for a future restricted "
            "strategy-search retry preview only; no strategy execution is granted now."
        ),
    }
    release_blocks = {
        **base,
        "edge_claim_blocked": True,
        "family_release_blocked": True,
        "holdout_access_blocked": True,
        "runtime_live_capital_blocked": True,
        "strategy_execution_blocked_now": True,
    }
    approval_record = {
        **base,
        "approval_scope": "future restricted strategy-search retry preview only",
    }
    self_validator = {
        **base,
        "artifact_count_expected": 7,
        "artifacts_created": [
            "repo_only_okx_88_symbol_1h_panel_revised_non_holdout_final_manifest.json",
            "repo_only_okx_88_symbol_1h_panel_revised_non_holdout_final_schema_binding.json",
            "repo_only_okx_88_symbol_1h_panel_revised_non_holdout_final_provenance.json",
            "repo_only_okx_88_symbol_1h_panel_revised_non_holdout_final_eligibility_record.json",
            "repo_only_okx_88_symbol_1h_panel_revised_non_holdout_final_release_blocks.json",
            "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_preview_approval_record.json",
            "repo_only_okx_88_symbol_1h_panel_revised_partial_output_finalize_manifest_self_validator.json",
        ],
        "self_validation_created_at_utc": now_utc(),
        "self_validation_result": replacement_checks_all_true,
    }
    return {
        "manifest": manifest,
        "schema_binding": schema_binding,
        "provenance": provenance,
        "eligibility": eligibility_record,
        "release_blocks": release_blocks,
        "approval": approval_record,
        "self_validator": self_validator,
    }


def write_outputs(outputs: dict[str, dict[str, Any]]) -> None:
    files = {
        "repo_only_okx_88_symbol_1h_panel_revised_non_holdout_final_manifest.json": outputs["manifest"],
        "repo_only_okx_88_symbol_1h_panel_revised_non_holdout_final_schema_binding.json": outputs["schema_binding"],
        "repo_only_okx_88_symbol_1h_panel_revised_non_holdout_final_provenance.json": outputs["provenance"],
        "repo_only_okx_88_symbol_1h_panel_revised_non_holdout_final_eligibility_record.json": outputs["eligibility"],
        "repo_only_okx_88_symbol_1h_panel_revised_non_holdout_final_release_blocks.json": outputs["release_blocks"],
        "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_preview_approval_record.json": outputs[
            "approval"
        ],
        "repo_only_okx_88_symbol_1h_panel_revised_partial_output_finalize_manifest_self_validator.json": outputs[
            "self_validator"
        ],
    }
    for filename, payload in files.items():
        write_json(OUTPUT_DIR / filename, payload)


def main() -> int:
    outputs = build_outputs()
    write_outputs(outputs)
    print(json.dumps(outputs["manifest"], indent=2, sort_keys=True))
    return 0 if outputs["manifest"]["replacement_checks_all_true"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
