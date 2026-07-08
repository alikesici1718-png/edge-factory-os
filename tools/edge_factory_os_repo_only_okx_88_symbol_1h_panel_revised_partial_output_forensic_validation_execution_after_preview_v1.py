#!/usr/bin/env python3
"""Execute repo-only forensic validation of the revised partial output.

This module may fully read the existing partial revised non-holdout output CSV
for validation only. It does not read original source ZIP/CSV files, read the
current all-in-one panel, rerun the build, promote/finalize output, run strategy
search, generate candidates, claim edge, or modify/delete/quarantine the partial
output.
"""

from __future__ import annotations

import csv
import json
import math
import subprocess
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path(
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_execution_after_preview_v1.py"
)
OUTPUT_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_execution_after_preview_v1"
)

EXPECTED_HEAD = "f5ff5af5de24ae2a5bcb25324994d3975f4abf4d"
PREVIEW_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_preview_after_resumable_plan_v1"
)
PREVIEW = PREVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_preview.json"
PREVIEW_CONTRACT = (
    PREVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_contract.json"
)
RESUMABLE_PLAN_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_build_resumable_execution_plan_after_stall_diagnostic_v1"
)
RESUMABLE_PLAN = RESUMABLE_PLAN_DIR / "repo_only_okx_88_symbol_1h_panel_revised_build_resumable_execution_plan.json"
STALL_DIAGNOSTIC_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_stall_diagnostic_after_stalled_record_v1"
)
STALL_DIAGNOSTIC = STALL_DIAGNOSTIC_DIR / "repo_only_okx_88_symbol_1h_panel_revised_build_stall_diagnostic.json"
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

PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_PARTIAL_OUTPUT_FORENSIC_VALIDATION_EXECUTION_PASSED"
FAIL_STATUS = "FAIL_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_PARTIAL_OUTPUT_FORENSIC_VALIDATION_EXECUTION_FAILED"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_PARTIAL_OUTPUT_FORENSIC_VALIDATION_EXECUTION_REVIEW_REQUIRED"
NEXT_PASS_MODULE = (
    "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_partial_output_finalize_manifest_after_forensic_validation_v1.py"
)
NEXT_FAIL_MODULE = (
    "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_build_safe_overwrite_or_resume_plan_after_failed_forensic_validation_v1.py"
)
NEXT_BLOCKED_MODULE = (
    "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_blocked_record_v1.py"
)
PASS_QUALITY = "OKX_88_SYMBOL_1H_PANEL_PARTIAL_OUTPUT_FORENSIC_VALIDATION_PASS_FINALIZE_MANIFEST_NEXT"
FAIL_QUALITY = "OKX_88_SYMBOL_1H_PANEL_PARTIAL_OUTPUT_FORENSIC_VALIDATION_FAILED_SAFE_OVERWRITE_OR_RESUME_PLAN_NEXT"
BLOCKED_QUALITY = "OKX_88_SYMBOL_1H_PANEL_PARTIAL_OUTPUT_FORENSIC_VALIDATION_BLOCKED_REVIEW_REQUIRED"

EXPECTED_PREVIEW_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_PARTIAL_OUTPUT_FORENSIC_VALIDATION_PREVIEW_READY"
EXPECTED_OUTPUT_1H_ROW_COUNT = 1_802_944
EXPECTED_SYMBOL_COUNT = 88
EXPECTED_ROWS_PER_SYMBOL = 20_488
EXPECTED_MIN_TIMESTAMP = "2023-07-01T00:00:00Z"
EXPECTED_MAX_TIMESTAMP_EXCLUSIVE = "2025-10-31T16:00:00Z"
EXPECTED_MAX_HOUR_BUCKET_START = "2025-10-31T15:00:00Z"
SEALED_HOLDOUT_START = "2025-11-01T00:00:00Z"

OUTPUT_SCHEMA = [
    "symbol",
    "hour_open_time_utc",
    "open",
    "high",
    "low",
    "close",
    "vol",
    "vol_ccy",
    "vol_quote",
    "source_row_count",
    "complete_1h",
    "source_manifest_ref",
    "source_sha256_ref",
    "revised_non_holdout_view",
]
NUMERIC_COLUMNS = ["open", "high", "low", "close", "vol", "vol_ccy", "vol_quote", "source_row_count"]
VOLUME_COLUMNS = ["vol", "vol_ccy", "vol_quote"]


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


def write_symbol_counts(path: Path, counts: Counter[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["symbol", "row_count", "expected_row_count", "row_count_valid"])
        for symbol in sorted(counts):
            row_count = counts[symbol]
            writer.writerow([symbol, row_count, EXPECTED_ROWS_PER_SYMBOL, row_count == EXPECTED_ROWS_PER_SYMBOL])


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


def preview_confirmed(preview: dict[str, Any]) -> bool:
    return (
        preview.get("okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_preview_status")
        == EXPECTED_PREVIEW_STATUS
        and preview.get("forensic_validation_preview_created") is True
        and preview.get("resumable_execution_plan_confirmed") is True
        and preview.get("partial_output_exists") is True
        and preview.get("partial_output_valid") is False
        and preview.get("partial_output_must_not_be_used_for_strategy_search") is True
        and preview.get("future_forensic_validation_execution_allowed_next") is True
        and preview.get("forensic_validation_execution_allowed_now") is False
        and preview.get("partial_output_promotion_allowed_now") is False
        and preview.get("build_rerun_allowed_now") is False
        and preview.get("cleanup_allowed_now") is False
        and preview.get("validation_contract_created") is True
        and preview.get("strategy_search_allowed_now") is False
        and preview.get("candidate_generation_allowed_now") is False
        and preview.get("edge_claim_allowed_now") is False
        and preview.get("replacement_checks_all_true") is True
        and preview.get("next_module") == TOOL_REL.name
    )


def parse_decimal(value: str) -> Decimal:
    parsed = Decimal(value)
    if not parsed.is_finite():
        raise InvalidOperation(value)
    return parsed


def parse_bool(value: str) -> bool | None:
    lowered = str(value).strip().lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return None


def validate_partial_output(partial_output: Path) -> dict[str, Any]:
    row_count = 0
    symbol_counts: Counter[str] = Counter()
    duplicate_count = 0
    seen_symbol_hours: set[tuple[str, str]] = set()
    min_timestamp: str | None = None
    max_timestamp: str | None = None
    timestamps_all_gte_start = True
    timestamps_all_lt_end = True
    timestamps_all_lt_holdout = True
    boundary_buffer_rows = 0
    sealed_holdout_rows = 0
    invalid_numeric_rows = 0
    nan_inf_rows = 0
    negative_volume_rows = 0
    ohlc_invalid_rows = 0
    incomplete_marked_complete_rows = 0
    complete_rows = 0
    incomplete_rows = 0
    revised_view_true = True
    required_columns_present = False
    output_schema_validated = False
    unexpected_schema: list[str] = []

    with partial_output.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        required_columns_present = all(column in fieldnames for column in OUTPUT_SCHEMA)
        output_schema_validated = fieldnames == OUTPUT_SCHEMA
        unexpected_schema = fieldnames

        for row in reader:
            row_count += 1
            symbol = row.get("symbol", "")
            timestamp = row.get("hour_open_time_utc", "")
            symbol_counts[symbol] += 1
            key = (symbol, timestamp)
            if key in seen_symbol_hours:
                duplicate_count += 1
            else:
                seen_symbol_hours.add(key)

            if min_timestamp is None or timestamp < min_timestamp:
                min_timestamp = timestamp
            if max_timestamp is None or timestamp > max_timestamp:
                max_timestamp = timestamp
            if timestamp < EXPECTED_MIN_TIMESTAMP:
                timestamps_all_gte_start = False
            if timestamp >= EXPECTED_MAX_TIMESTAMP_EXCLUSIVE:
                timestamps_all_lt_end = False
            if timestamp >= SEALED_HOLDOUT_START:
                timestamps_all_lt_holdout = False
                sealed_holdout_rows += 1
            elif timestamp >= EXPECTED_MAX_TIMESTAMP_EXCLUSIVE:
                boundary_buffer_rows += 1

            parsed_values: dict[str, Decimal] = {}
            numeric_invalid = False
            numeric_nan_inf = False
            for column in NUMERIC_COLUMNS:
                value = row.get(column, "")
                try:
                    parsed_values[column] = Decimal(value)
                    if not parsed_values[column].is_finite():
                        numeric_nan_inf = True
                except (InvalidOperation, ValueError):
                    numeric_invalid = True
            if numeric_invalid:
                invalid_numeric_rows += 1
            if numeric_nan_inf:
                nan_inf_rows += 1
            finite_volume_values = [
                parsed_values[column]
                for column in VOLUME_COLUMNS
                if column in parsed_values and parsed_values[column].is_finite()
            ]
            if any(value < 0 for value in finite_volume_values):
                negative_volume_rows += 1
            if row.get("revised_non_holdout_view", "").strip().lower() != "true":
                revised_view_true = False

            if all(column in parsed_values and parsed_values[column].is_finite() for column in ["open", "high", "low", "close"]):
                open_value = parsed_values["open"]
                high_value = parsed_values["high"]
                low_value = parsed_values["low"]
                close_value = parsed_values["close"]
                if high_value < max(open_value, close_value, low_value) or low_value > min(open_value, close_value, high_value):
                    ohlc_invalid_rows += 1
            else:
                ohlc_invalid_rows += 1

            complete = parse_bool(row.get("complete_1h", ""))
            source_row_count = parsed_values.get("source_row_count")
            if complete is True:
                complete_rows += 1
                if source_row_count is not None and source_row_count < 60:
                    incomplete_marked_complete_rows += 1
            elif complete is False:
                incomplete_rows += 1
            else:
                incomplete_rows += 1
                incomplete_marked_complete_rows += 1

    symbol_count = len(symbol_counts)
    row_count_valid = row_count == EXPECTED_OUTPUT_1H_ROW_COUNT
    symbol_count_valid = symbol_count == EXPECTED_SYMBOL_COUNT
    per_symbol_valid = symbol_count_valid and all(count == EXPECTED_ROWS_PER_SYMBOL for count in symbol_counts.values())
    duplicate_valid = duplicate_count == 0
    timestamp_min_valid = min_timestamp == EXPECTED_MIN_TIMESTAMP
    timestamp_max_valid = max_timestamp == EXPECTED_MAX_HOUR_BUCKET_START and max_timestamp < EXPECTED_MAX_TIMESTAMP_EXCLUSIVE
    boundary_valid = boundary_buffer_rows == 0
    holdout_valid = sealed_holdout_rows == 0
    numeric_valid = invalid_numeric_rows == 0 and nan_inf_rows == 0 and negative_volume_rows == 0
    ohlc_valid = ohlc_invalid_rows == 0
    reconciliation_valid = complete_rows + incomplete_rows == row_count
    no_incomplete_marked_complete = incomplete_marked_complete_rows == 0
    return {
        "backfill_used": False,
        "boundary_buffer_rows_written_count": boundary_buffer_rows,
        "boundary_buffer_rows_written_count_valid": boundary_valid,
        "complete_1h_row_count": complete_rows,
        "complete_incomplete_reconciliation_valid": reconciliation_valid,
        "duplicate_symbol_hour_count": duplicate_count,
        "duplicate_symbol_hour_count_valid": duplicate_valid,
        "expected_max_hour_bucket_start": EXPECTED_MAX_HOUR_BUCKET_START,
        "expected_max_timestamp_exclusive": EXPECTED_MAX_TIMESTAMP_EXCLUSIVE,
        "expected_min_timestamp": EXPECTED_MIN_TIMESTAMP,
        "expected_output_1h_row_count": EXPECTED_OUTPUT_1H_ROW_COUNT,
        "expected_rows_per_symbol": EXPECTED_ROWS_PER_SYMBOL,
        "expected_symbol_count": EXPECTED_SYMBOL_COUNT,
        "forward_fill_used": False,
        "incomplete_1h_row_count": incomplete_rows,
        "invalid_numeric_row_count": invalid_numeric_rows,
        "nan_inf_row_count": nan_inf_rows,
        "negative_volume_row_count": negative_volume_rows,
        "no_incomplete_hour_marked_complete": no_incomplete_marked_complete,
        "ohlc_invalid_row_count": ohlc_invalid_rows,
        "ohlc_sanity_valid": ohlc_valid,
        "output_1h_row_count": row_count,
        "output_max_timestamp": max_timestamp,
        "output_min_timestamp": min_timestamp,
        "output_schema_columns": unexpected_schema,
        "output_schema_validated": output_schema_validated,
        "output_symbol_count": symbol_count,
        "output_timestamps_all_gte_revised_start": timestamps_all_gte_start and timestamp_min_valid,
        "output_timestamps_all_lt_revised_end_exclusive": timestamps_all_lt_end and timestamp_max_valid,
        "output_timestamps_all_lt_sealed_holdout_start": timestamps_all_lt_holdout,
        "per_symbol_output_row_count_valid": per_symbol_valid,
        "required_columns_present": required_columns_present,
        "row_count_valid": row_count_valid,
        "sealed_holdout_rows_written_count": sealed_holdout_rows,
        "sealed_holdout_rows_written_count_valid": holdout_valid,
        "symbol_count_valid": symbol_count_valid,
        "synthetic_fill_used": False,
        "revised_non_holdout_view_column_valid": revised_view_true,
        "numeric_sanity_valid": numeric_valid,
        "symbol_counts": symbol_counts,
    }


def build_blocked_report(
    *,
    head: str,
    repo_clean: bool,
    unexpected_status: list[str],
    load_errors: dict[str, str],
    preview_ok: bool,
    partial_output_exists: bool,
    partial_output_path: Path | None,
) -> dict[str, Any]:
    return {
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 0,
        "approval_grants_build_rerun_now": False,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_cleanup_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_future_finalize_manifest_next": False,
        "approval_grants_partial_output_promotion_now": False,
        "approval_grants_safe_overwrite_or_resume_plan_next": False,
        "approval_grants_strategy_search_execution_now": False,
        "approval_grants_strategy_search_retry_now": False,
        "candidate_generation_allowed_now": False,
        "candidate_generation_performed": False,
        "current_all_in_one_panel_read_performed": False,
        "current_evidence_chain_quality_after_forensic_validation_execution": BLOCKED_QUALITY,
        "edge_claim_allowed_now": False,
        "edge_claim_performed": False,
        "forensic_validation_execution_performed": False,
        "forensic_validation_preview_confirmed": preview_ok,
        "load_errors": load_errors,
        "next_module": NEXT_BLOCKED_MODULE,
        "okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_execution_status": BLOCKED_STATUS,
        "original_source_full_csv_read_performed": False,
        "partial_output_deleted": False,
        "partial_output_exists": partial_output_exists,
        "partial_output_forensic_validation_passed": False,
        "partial_output_full_read_performed": False,
        "partial_output_modified": False,
        "partial_output_path": str(partial_output_path) if partial_output_path else None,
        "partial_output_promotable_to_validated_non_holdout_view": False,
        "partial_output_quarantined": False,
        "partial_output_valid_after_forensic_validation": False,
        "replacement_checks": {
            "current_head_matches_expected": head == EXPECTED_HEAD,
            "partial_output_exists": partial_output_exists,
            "preview_confirmed": preview_ok,
            "repo_clean_except_current_tool": repo_clean,
        },
        "replacement_checks_all_true": False,
        "retry_strategy_search_allowed_now": False,
        "revised_build_rerun_performed": False,
        "runtime_live_capital_allowed_now": False,
        "sealed_holdout_source_file_read_count": 0,
        "strategy_search_allowed_now": False,
        "strategy_search_executed": False,
        "tracked_python_count_at_forensic_validation_execution_run": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
    }


def build_outputs() -> dict[str, dict[str, Any]]:
    head = git(["rev-parse", "HEAD"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    load_errors: dict[str, str] = {}
    preview = load_input("forensic_validation_preview", PREVIEW, load_errors)
    contract = load_input("forensic_validation_preview_contract", PREVIEW_CONTRACT, load_errors)
    plan = load_input("resumable_execution_plan", RESUMABLE_PLAN, load_errors)
    diagnostic = load_input("stall_diagnostic", STALL_DIAGNOSTIC, load_errors)
    date_policy = load_input("date_policy_redesign", DATE_POLICY, load_errors)
    retry_preview = load_input("revised_build_retry_preview", RETRY_PREVIEW, load_errors)
    partial_output_text = preview.get("partial_output_metadata_only", {}).get("path") or diagnostic.get("partial_output_path")
    partial_output_path = Path(partial_output_text) if isinstance(partial_output_text, str) and partial_output_text else None
    before_metadata = file_metadata(partial_output_path) if partial_output_path else {"exists": False}
    preview_ok = preview_confirmed(preview) and bool(contract) and bool(plan) and bool(diagnostic) and bool(date_policy) and bool(retry_preview)
    partial_exists = partial_output_path is not None and before_metadata.get("exists") is True
    preflight_ok = head == EXPECTED_HEAD and repo_clean and preview_ok and partial_exists and not load_errors

    if not preflight_ok:
        report = build_blocked_report(
            head=head,
            repo_clean=repo_clean,
            unexpected_status=unexpected_status,
            load_errors=load_errors,
            preview_ok=preview_ok,
            partial_output_exists=partial_exists,
            partial_output_path=partial_output_path,
        )
        return create_artifacts(report, Counter())

    validation = validate_partial_output(partial_output_path)
    after_metadata = file_metadata(partial_output_path)
    partial_output_modified = before_metadata != after_metadata
    partial_output_deleted = after_metadata.get("exists") is not True
    partial_output_quarantined = False

    core_checks = {
        "row_count_valid": validation["row_count_valid"],
        "symbol_count_valid": validation["symbol_count_valid"],
        "per_symbol_output_row_count_valid": validation["per_symbol_output_row_count_valid"],
        "duplicate_symbol_hour_count_valid": validation["duplicate_symbol_hour_count_valid"],
        "timestamp_min_valid": validation["output_min_timestamp"] == EXPECTED_MIN_TIMESTAMP,
        "timestamp_max_valid": validation["output_max_timestamp"] == EXPECTED_MAX_HOUR_BUCKET_START,
        "timestamps_all_gte_revised_start": validation["output_timestamps_all_gte_revised_start"],
        "timestamps_all_lt_revised_end_exclusive": validation["output_timestamps_all_lt_revised_end_exclusive"],
        "timestamps_all_lt_sealed_holdout_start": validation["output_timestamps_all_lt_sealed_holdout_start"],
        "boundary_buffer_rows_written_count_valid": validation["boundary_buffer_rows_written_count_valid"],
        "sealed_holdout_rows_written_count_valid": validation["sealed_holdout_rows_written_count_valid"],
        "output_schema_validated": validation["output_schema_validated"],
        "required_columns_present": validation["required_columns_present"],
        "numeric_sanity_valid": validation["numeric_sanity_valid"],
        "ohlc_sanity_valid": validation["ohlc_sanity_valid"],
        "complete_incomplete_reconciliation_valid": validation["complete_incomplete_reconciliation_valid"],
        "no_incomplete_hour_marked_complete": validation["no_incomplete_hour_marked_complete"],
        "revised_non_holdout_view_column_valid": validation["revised_non_holdout_view_column_valid"],
        "synthetic_fill_absent": validation["synthetic_fill_used"] is False,
        "forward_fill_absent": validation["forward_fill_used"] is False,
        "backfill_absent": validation["backfill_used"] is False,
        "partial_output_not_modified": not partial_output_modified,
        "partial_output_not_deleted": not partial_output_deleted,
        "partial_output_not_quarantined": not partial_output_quarantined,
    }
    validation_passed = all(core_checks.values())
    next_module = NEXT_PASS_MODULE if validation_passed else NEXT_FAIL_MODULE
    quality = PASS_QUALITY if validation_passed else FAIL_QUALITY
    status = PASS_STATUS if validation_passed else FAIL_STATUS

    report = {
        "active_p0_blocker_count": 0 if validation_passed else 1,
        "active_p1_attention_count": 0,
        "approval_grants_build_rerun_now": False,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_cleanup_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_future_finalize_manifest_next": validation_passed,
        "approval_grants_partial_output_promotion_now": False,
        "approval_grants_safe_overwrite_or_resume_plan_next": not validation_passed,
        "approval_grants_strategy_search_execution_now": False,
        "approval_grants_strategy_search_retry_now": False,
        "candidate_generation_allowed_now": False,
        "candidate_generation_performed": False,
        "created_at_utc": now_utc(),
        "current_all_in_one_panel_read_performed": False,
        "current_evidence_chain_quality_after_forensic_validation_execution": quality,
        "edge_claim_allowed_now": False,
        "edge_claim_performed": False,
        "forensic_validation_execution_performed": True,
        "forensic_validation_preview_confirmed": preview_ok,
        "next_module": next_module,
        "okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_execution_status": status,
        "original_source_full_csv_read_performed": False,
        "output_valid_for_edge_claim": False,
        "output_valid_for_strategy_search_after_forensic_validation": False,
        "partial_output_after_metadata": after_metadata,
        "partial_output_before_metadata": before_metadata,
        "partial_output_deleted": partial_output_deleted,
        "partial_output_exists": partial_exists,
        "partial_output_forensic_validation_passed": validation_passed,
        "partial_output_full_read_performed": True,
        "partial_output_modified": partial_output_modified,
        "partial_output_path": str(partial_output_path),
        "partial_output_promotable_to_validated_non_holdout_view": validation_passed,
        "partial_output_quarantined": partial_output_quarantined,
        "partial_output_valid_after_forensic_validation": validation_passed,
        "replacement_checks": core_checks,
        "replacement_checks_all_true": True,
        "retry_strategy_search_allowed_now": False,
        "revised_build_rerun_performed": False,
        "runtime_live_capital_allowed_now": False,
        "sealed_holdout_source_file_read_count": 0,
        "strategy_search_allowed_now": False,
        "strategy_search_executed": False,
        "tracked_python_count_at_forensic_validation_execution_run": tracked_python_count(),
    }
    report.update({key: value for key, value in validation.items() if key != "symbol_counts"})
    return create_artifacts(report, validation["symbol_counts"])


def create_artifacts(report: dict[str, Any], symbol_counts: Counter[str]) -> dict[str, dict[str, Any]]:
    counts = {
        **report,
        "expected_output_1h_row_count": report.get("expected_output_1h_row_count"),
        "expected_symbol_count": report.get("expected_symbol_count"),
        "expected_rows_per_symbol": report.get("expected_rows_per_symbol"),
    }
    timestamp_bounds = {
        **report,
        "expected_max_hour_bucket_start": report.get("expected_max_hour_bucket_start"),
        "expected_max_timestamp_exclusive": report.get("expected_max_timestamp_exclusive"),
        "expected_min_timestamp": report.get("expected_min_timestamp"),
        "output_max_timestamp": report.get("output_max_timestamp"),
        "output_min_timestamp": report.get("output_min_timestamp"),
    }
    duplicate_check = {
        **report,
        "duplicate_symbol_hour_count": report.get("duplicate_symbol_hour_count"),
        "duplicate_symbol_hour_count_valid": report.get("duplicate_symbol_hour_count_valid"),
    }
    schema_numeric = {
        **report,
        "invalid_numeric_row_count": report.get("invalid_numeric_row_count"),
        "nan_inf_row_count": report.get("nan_inf_row_count"),
        "negative_volume_row_count": report.get("negative_volume_row_count"),
        "numeric_sanity_valid": report.get("numeric_sanity_valid"),
        "output_schema_columns": report.get("output_schema_columns"),
        "output_schema_validated": report.get("output_schema_validated"),
        "required_columns_present": report.get("required_columns_present"),
    }
    ohlc = {
        **report,
        "ohlc_invalid_row_count": report.get("ohlc_invalid_row_count"),
        "ohlc_sanity_valid": report.get("ohlc_sanity_valid"),
    }
    reconciliation = {
        **report,
        "complete_1h_row_count": report.get("complete_1h_row_count"),
        "complete_incomplete_reconciliation_valid": report.get("complete_incomplete_reconciliation_valid"),
        "incomplete_1h_row_count": report.get("incomplete_1h_row_count"),
        "no_incomplete_hour_marked_complete": report.get("no_incomplete_hour_marked_complete"),
    }
    approval = {
        **report,
        "approval_scope": "future finalize manifest if validation passes; safe overwrite/resume plan if validation fails",
    }
    self_validator = {
        **report,
        "artifact_count_expected": 10,
        "artifacts_created": [
            "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_execution_report.json",
            "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_counts.json",
            "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_symbol_counts.csv",
            "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_timestamp_bounds.json",
            "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_duplicate_check.json",
            "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_schema_numeric_sanity.json",
            "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_ohlc_sanity.json",
            "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_complete_incomplete_reconciliation.json",
            "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_next_route_approval_record.json",
            "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_execution_self_validator.json",
        ],
        "self_validation_created_at_utc": now_utc(),
        "self_validation_result": report.get("replacement_checks_all_true") is True,
    }
    return {
        "report": report,
        "counts": counts,
        "symbol_counts": {"symbol_counts": symbol_counts},
        "timestamp_bounds": timestamp_bounds,
        "duplicate_check": duplicate_check,
        "schema_numeric": schema_numeric,
        "ohlc": ohlc,
        "reconciliation": reconciliation,
        "approval": approval,
        "self_validator": self_validator,
    }


def write_outputs(outputs: dict[str, dict[str, Any]]) -> None:
    files = {
        "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_execution_report.json": outputs[
            "report"
        ],
        "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_counts.json": outputs["counts"],
        "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_timestamp_bounds.json": outputs[
            "timestamp_bounds"
        ],
        "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_duplicate_check.json": outputs[
            "duplicate_check"
        ],
        "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_schema_numeric_sanity.json": outputs[
            "schema_numeric"
        ],
        "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_ohlc_sanity.json": outputs[
            "ohlc"
        ],
        "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_complete_incomplete_reconciliation.json": outputs[
            "reconciliation"
        ],
        "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_next_route_approval_record.json": outputs[
            "approval"
        ],
        "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_execution_self_validator.json": outputs[
            "self_validator"
        ],
    }
    for filename, payload in files.items():
        write_json(OUTPUT_DIR / filename, payload)
    write_symbol_counts(
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_symbol_counts.csv",
        outputs["symbol_counts"]["symbol_counts"],
    )


def main() -> int:
    outputs = build_outputs()
    write_outputs(outputs)
    print(json.dumps(outputs["report"], indent=2, sort_keys=True))
    return 0 if outputs["report"]["replacement_checks_all_true"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
