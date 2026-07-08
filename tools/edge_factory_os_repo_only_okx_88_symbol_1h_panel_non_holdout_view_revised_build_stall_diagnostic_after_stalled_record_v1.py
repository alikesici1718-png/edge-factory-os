#!/usr/bin/env python3
"""Repo-only targeted stall diagnostic after revised non-holdout build stall.

This module inspects the stalled record, repo metadata, build tool/artifact
metadata, partial output metadata, and RSR-USDT-SWAP source manifest metadata.
It does not rerun the build, validate partial output, run strategy search,
read broad source rows, read the current all-in-one 1h panel, or patch tracked
files.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path(
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_stall_diagnostic_after_stalled_record_v1.py"
)
OUTPUT_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_stall_diagnostic_after_stalled_record_v1"
)

EXPECTED_HEAD = "abe431d2105d3a957f0d3738059fb71b9edce42f"
PREVIOUS_KNOWN_TRACKED_PYTHON_COUNT = 786
EXPECTED_LATEST_COMMIT_FILE = (
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_stalled_record_v1.py"
)
STALLED_RECORD_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_stalled_record_v1"
)
STALLED_RECORD = (
    STALLED_RECORD_DIR
    / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_stalled_record.json"
)
BUILD_TOOL_REL = Path(
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_after_retry_preview_v1.py"
)
BUILD_EXECUTION_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_after_retry_preview_v1"
)
PARTIAL_OUTPUT = BUILD_EXECUTION_DIR / "repo_only_okx_88_symbol_1h_panel_revised_non_holdout_view.csv"
PER_SYMBOL_COUNTS = (
    BUILD_EXECUTION_DIR
    / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_per_symbol_counts.csv"
)
BUILD_REPORT = (
    BUILD_EXECUTION_DIR
    / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_report.json"
)
PREVIEW_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_retry_preview_after_date_policy_redesign_v1"
)
PREVIEW = PREVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_retry_preview.json"
REDESIGN_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign_after_boundary_reconciliation_v1"
)
REDESIGN = REDESIGN_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign.json"
FINAL_SUMMARY_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_coverage_discovery_final_summary_after_generic_controller_v1"
)
COMPLETE_LOCKED = FINAL_SUMMARY_DIR / "repo_only_okx_full_usdt_swap_near_3y_complete_symbol_set_locked.json"
GENERIC_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1"
)
CHUNK_01_EXEC_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_execution_after_preview_approval_v1"
)
CHUNK_02_EXEC_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_execution_after_preview_approval_v1"
)

EXPECTED_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_BUILD_STALL_DIAGNOSTIC_READY"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_BUILD_STALL_DIAGNOSTIC_REVIEW_REQUIRED"
NEXT_RSR_MODULE = (
    "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_build_rsr_symbol_probe_after_stall_diagnostic_v1.py"
)
NEXT_PLAN_MODULE = (
    "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_build_resumable_execution_plan_after_stall_diagnostic_v1.py"
)
NEXT_BLOCKED_MODULE = (
    "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_build_stall_diagnostic_blocked_record_v1.py"
)
PASS_QUALITY = "OKX_88_SYMBOL_1H_PANEL_REVISED_BUILD_STALL_DIAGNOSTIC_READY_SAFE_FOLLOWUP_NEXT"
BLOCKED_QUALITY = "OKX_88_SYMBOL_1H_PANEL_REVISED_BUILD_STALL_DIAGNOSTIC_BLOCKED_REVIEW_REQUIRED"

LAST_REPORTED_SYMBOL_INDEX = 64
LAST_REPORTED_SYMBOL = "QTUM-USDT-SWAP"
SUSPECTED_NEXT_SYMBOL = "RSR-USDT-SWAP"
REVISED_SOURCE_START_DATE = "2023-07-01"
REVISED_SOURCE_END_DATE_INCLUSIVE = "2025-10-31"
EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 854


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
    unexpected = [line for line in lines if not line.replace("\\", "/").endswith(TOOL_REL.as_posix())]
    return not unexpected, unexpected


def latest_commit_changed_paths() -> list[str]:
    output = git(["show", "--name-only", "--format=", "HEAD"])
    return [line.strip() for line in output.splitlines() if line.strip()]


def is_tracked(rel_path: Path | str) -> bool:
    output = git(["ls-files", str(rel_path).replace("\\", "/")])
    return bool(output.strip())


def chunk_manifest_paths() -> dict[str, Path]:
    paths = {
        "chunk_01": CHUNK_01_EXEC_DIR / "historical_okx_full_usdt_swap_first_chunk_download_file_manifest_after_execution.json",
        "chunk_02": CHUNK_02_EXEC_DIR / "historical_okx_full_usdt_swap_chunk_02_download_file_manifest_after_execution.json",
        "chunk_03": GENERIC_DIR / "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_chunk_download_manifest_after_execution.json",
    }
    for chunk_num in range(4, 17):
        chunk_id = f"chunk_{chunk_num:02d}"
        paths[chunk_id] = (
            GENERIC_DIR
            / f"historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_{chunk_id}_download_manifest_after_execution.json"
        )
    return paths


def file_metadata(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "exists": False,
            "modified_time": None,
            "path": str(path),
            "size_bytes": None,
        }
    stat = path.stat()
    return {
        "exists": True,
        "modified_time": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "path": str(path),
        "size_bytes": stat.st_size,
    }


def tail_lines(path: Path, *, max_bytes: int = 65536, max_lines: int = 8) -> list[str]:
    if not path.exists() or path.stat().st_size <= 0:
        return []
    with path.open("rb") as handle:
        size = path.stat().st_size
        handle.seek(max(0, size - max_bytes))
        data = handle.read(max_bytes)
    text = data.decode("utf-8", errors="replace")
    lines = [line for line in text.splitlines() if line.strip()]
    return lines[-max_lines:]


def parse_tail_symbol_and_timestamp(lines: list[str]) -> tuple[str | None, str | None]:
    for line in reversed(lines):
        if line.startswith("symbol,"):
            continue
        parts = line.split(",")
        if len(parts) >= 2:
            return parts[0] or None, parts[1] or None
    return None, None


def partial_output_inventory() -> dict[str, Any]:
    meta = file_metadata(PARTIAL_OUTPUT)
    lines = tail_lines(PARTIAL_OUTPUT) if meta["exists"] else []
    last_symbol, last_timestamp = parse_tail_symbol_and_timestamp(lines)
    per_symbol_meta = file_metadata(PER_SYMBOL_COUNTS)
    report_meta = file_metadata(BUILD_REPORT)
    return {
        "partial_output_exists": meta["exists"],
        "partial_output_path": meta["path"],
        "partial_output_size_bytes": meta["size_bytes"],
        "partial_output_modified_time": meta["modified_time"],
        "partial_output_safe_tail_inspected": bool(lines),
        "partial_output_tail_line_count": len(lines),
        "partial_output_tail_last_symbol_detected": last_symbol,
        "partial_output_tail_last_timestamp_detected": last_timestamp,
        "partial_output_tail_sample": lines,
        "partial_output_approximate_row_count_skipped": True,
        "partial_output_approximate_row_count_skip_reason": "Avoid full scan of large partial output; diagnostic is metadata/tiny-tail only.",
        "per_symbol_counts_artifact_metadata": per_symbol_meta,
        "build_report_artifact_metadata": report_meta,
        "partial_output_must_not_be_used_for_strategy_search": True,
        "partial_output_valid": False,
        "partial_output_cleanup_allowed_now": False,
        "partial_output_delete_allowed_now": False,
        "partial_output_quarantine_allowed_now": False,
    }


def read_selected_symbol_context() -> dict[str, Any]:
    try:
        locked = read_json(COMPLETE_LOCKED)
        symbols = locked.get("near_3y_complete_symbols")
        if not isinstance(symbols, list):
            symbols = []
    except (OSError, json.JSONDecodeError, RuntimeError) as exc:
        return {
            "selected_symbol_context_error": repr(exc),
            "selected_symbol_count": None,
            "last_reported_symbol_from_locked_index": None,
            "suspected_next_symbol_from_locked_index": None,
            "suspected_next_symbol_index_from_locked": None,
        }
    last_from_locked = symbols[LAST_REPORTED_SYMBOL_INDEX - 1] if len(symbols) >= LAST_REPORTED_SYMBOL_INDEX else None
    next_from_locked = symbols[LAST_REPORTED_SYMBOL_INDEX] if len(symbols) > LAST_REPORTED_SYMBOL_INDEX else None
    return {
        "selected_symbol_context_error": None,
        "selected_symbol_count": len(symbols),
        "last_reported_symbol_from_locked_index": last_from_locked,
        "suspected_next_symbol_from_locked_index": next_from_locked,
        "suspected_next_symbol_index_from_locked": LAST_REPORTED_SYMBOL_INDEX + 1 if next_from_locked else None,
    }


def rsr_manifest_metadata() -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    manifest_errors: dict[str, str] = {}
    for chunk_id, path in chunk_manifest_paths().items():
        try:
            doc = read_json(path)
        except (OSError, json.JSONDecodeError, RuntimeError) as exc:
            manifest_errors[chunk_id] = f"{path}: {exc}"
            continue
        for entry in doc.get("file_manifest", []):
            if not isinstance(entry, dict) or entry.get("symbol") != SUSPECTED_NEXT_SYMBOL:
                continue
            date = str(entry.get("date", ""))
            entries.append(
                {
                    "available_for_validator": entry.get("available_for_validator"),
                    "chunk_id": entry.get("chunk_id"),
                    "coverage_gap": entry.get("coverage_gap"),
                    "date": date,
                    "expected_inner_csv": entry.get("expected_inner_csv"),
                    "local_zip_path_exists": Path(str(entry.get("local_zip_path", ""))).exists(),
                    "sha256_present": bool(entry.get("sha256")),
                }
            )
    allowed_entries = [
        row
        for row in entries
        if REVISED_SOURCE_START_DATE <= str(row.get("date", "")) <= REVISED_SOURCE_END_DATE_INCLUSIVE
    ]
    forbidden_metadata_entries = [row for row in entries if str(row.get("date", "")) >= "2025-11-01"]
    dates = [row["date"] for row in allowed_entries]
    return {
        "rsr_source_manifest_metadata_checked": True,
        "rsr_source_manifest_metadata_error_count": len(manifest_errors),
        "rsr_source_manifest_metadata_errors": manifest_errors,
        "rsr_allowed_manifest_entry_count": len(allowed_entries),
        "rsr_allowed_manifest_date_min": min(dates) if dates else None,
        "rsr_allowed_manifest_date_max": max(dates) if dates else None,
        "rsr_expected_allowed_manifest_entry_count": EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "rsr_allowed_manifest_entry_count_matches_expected": len(allowed_entries) == EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "rsr_forbidden_post_holdout_manifest_metadata_entry_count": len(forbidden_metadata_entries),
        "rsr_manifest_local_zip_missing_count": sum(1 for row in allowed_entries if row["local_zip_path_exists"] is not True),
        "rsr_manifest_unavailable_count": sum(1 for row in allowed_entries if row["available_for_validator"] is not True),
        "rsr_manifest_coverage_gap_count": sum(1 for row in allowed_entries if row["coverage_gap"] is True),
        "rsr_tiny_allowed_source_probe_performed": False,
        "rsr_tiny_probe_row_count": 0,
        "source_file_date_2025_11_01_read": False,
        "broad_source_row_read_performed": False,
    }


def confirm_stalled_record(record: dict[str, Any]) -> bool:
    return (
        record.get("stalled_record_status")
        == "STALLED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_NON_HOLDOUT_VIEW_BUILD_EXECUTION_RECORDED"
        and record.get("last_reported_symbol_index") == LAST_REPORTED_SYMBOL_INDEX
        and record.get("last_reported_symbol") == LAST_REPORTED_SYMBOL
        and record.get("suspected_next_symbol") == SUSPECTED_NEXT_SYMBOL
        and record.get("revised_build_execution_completed") is False
        and record.get("partial_output_valid") is False
        and record.get("strategy_search_allowed_now") is False
        and record.get("candidate_generation_allowed_now") is False
        and record.get("edge_claim_allowed_now") is False
        and record.get("replacement_checks_all_true") is False
    )


def determine_cause(partial: dict[str, Any], symbol_context: dict[str, Any], rsr: dict[str, Any]) -> tuple[str, str]:
    tail_symbol = partial.get("partial_output_tail_last_symbol_detected")
    if tail_symbol == LAST_REPORTED_SYMBOL:
        return "RSR_SOURCE_FILE_OPEN_OR_ZIP_STALL", NEXT_RSR_MODULE
    if tail_symbol == SUSPECTED_NEXT_SYMBOL:
        return "RSR_DATA_POLICY_EDGE_CASE", NEXT_RSR_MODULE
    if tail_symbol and tail_symbol != LAST_REPORTED_SYMBOL:
        return "PROCESS_INTERRUPTED_OR_BROWSER_CODEX_STALL", NEXT_PLAN_MODULE
    if partial.get("partial_output_exists") is True:
        return "PARTIAL_OUTPUT_ARTIFACT_CONSISTENCY_UNKNOWN", NEXT_PLAN_MODULE
    if rsr.get("rsr_allowed_manifest_entry_count_matches_expected") is not True:
        return "RSR_SOURCE_FILE_OPEN_OR_ZIP_STALL", NEXT_RSR_MODULE
    if symbol_context.get("suspected_next_symbol_from_locked_index") != SUSPECTED_NEXT_SYMBOL:
        return "UNKNOWN_REQUIRES_SAFE_RESUMABLE_BUILD_PLAN", NEXT_PLAN_MODULE
    return "UNKNOWN_REQUIRES_SAFE_RESUMABLE_BUILD_PLAN", NEXT_PLAN_MODULE


def build_outputs() -> dict[str, dict[str, Any]]:
    current_head = git(["rev-parse", "HEAD"])
    top_level = git(["rev-parse", "--show-toplevel"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    changed_paths = latest_commit_changed_paths()
    latest_commit_contains_only_stalled_record_tool = changed_paths == [EXPECTED_LATEST_COMMIT_FILE]
    current_count = tracked_python_count()
    delta = current_count - PREVIOUS_KNOWN_TRACKED_PYTHON_COUNT
    extra_explained = (
        delta == 2
        and latest_commit_contains_only_stalled_record_tool
        and is_tracked(BUILD_TOOL_REL)
        and is_tracked(EXPECTED_LATEST_COMMIT_FILE)
    )
    extra_explanation = (
        "Delta of +2 is explained by the pre-existing revised build execution tool plus the latest stalled-record tool."
        if extra_explained
        else "Tracked Python count delta from previous known value is not fully explained by the inspected commit/tool set."
    )

    load_errors: dict[str, str] = {}
    try:
        stalled_record = read_json(STALLED_RECORD)
    except (OSError, json.JSONDecodeError, RuntimeError) as exc:
        stalled_record = {}
        load_errors["stalled_record"] = f"{STALLED_RECORD}: {exc}"
    stalled_record_confirmed = confirm_stalled_record(stalled_record)
    try:
        preview = read_json(PREVIEW)
    except (OSError, json.JSONDecodeError, RuntimeError) as exc:
        preview = {}
        load_errors["preview"] = f"{PREVIEW}: {exc}"
    try:
        redesign = read_json(REDESIGN)
    except (OSError, json.JSONDecodeError, RuntimeError) as exc:
        redesign = {}
        load_errors["redesign"] = f"{REDESIGN}: {exc}"

    partial = partial_output_inventory()
    symbol_context = read_selected_symbol_context()
    rsr = rsr_manifest_metadata()
    suspected_cause, route_if_ready = determine_cause(partial, symbol_context, rsr)

    active_p1_attention_count = 0 if extra_explained else 1
    replacement_checks = {
        "correct_repo_path_confirmed": top_level == REPO.as_posix(),
        "current_head_matches_expected": current_head == EXPECTED_HEAD,
        "repo_clean_except_current_tool": repo_clean,
        "stalled_record_confirmed": stalled_record_confirmed,
        "last_reported_symbol_index_confirmed": stalled_record.get("last_reported_symbol_index") == LAST_REPORTED_SYMBOL_INDEX,
        "last_reported_symbol_confirmed": stalled_record.get("last_reported_symbol") == LAST_REPORTED_SYMBOL,
        "suspected_next_symbol_confirmed": stalled_record.get("suspected_next_symbol") == SUSPECTED_NEXT_SYMBOL,
        "partial_output_remains_invalid": partial["partial_output_valid"] is False,
        "partial_output_strategy_search_blocked": partial["partial_output_must_not_be_used_for_strategy_search"] is True,
        "revised_build_not_rerun": True,
        "validator_not_executed": True,
        "strategy_search_not_executed": True,
        "candidate_generation_not_performed": True,
        "edge_claim_not_performed": True,
        "no_cleanup_delete_or_quarantine": (
            partial["partial_output_cleanup_allowed_now"] is False
            and partial["partial_output_delete_allowed_now"] is False
            and partial["partial_output_quarantine_allowed_now"] is False
        ),
        "no_forbidden_source_or_panel_reads": (
            rsr["source_file_date_2025_11_01_read"] is False
            and rsr["broad_source_row_read_performed"] is False
        ),
        "revised_build_execution_tool_exists": (REPO / BUILD_TOOL_REL).exists(),
        "revised_build_execution_tool_tracked": is_tracked(BUILD_TOOL_REL),
        "safe_next_route_not_direct_build_or_strategy": route_if_ready in {NEXT_RSR_MODULE, NEXT_PLAN_MODULE},
    }
    replacement_checks_all_true = all(replacement_checks.values()) and not load_errors
    status = EXPECTED_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    next_module = route_if_ready if replacement_checks_all_true else NEXT_BLOCKED_MODULE
    quality = PASS_QUALITY if replacement_checks_all_true else BLOCKED_QUALITY

    approval_rsr = next_module == NEXT_RSR_MODULE
    approval_plan = next_module == NEXT_PLAN_MODULE
    record = {
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": active_p1_attention_count,
        "approval_grants_build_rerun_now": False,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_cleanup_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_future_resumable_execution_plan_next": approval_plan,
        "approval_grants_future_rsr_symbol_probe_next": approval_rsr,
        "approval_grants_stall_diagnostic_now": True,
        "approval_grants_strategy_search_execution_now": False,
        "approval_grants_strategy_search_retry_now": False,
        "approval_grants_validator_now": False,
        "broad_source_row_read_performed": False,
        "candidate_generation_allowed_now": False,
        "candidate_generation_performed": False,
        "changed_paths_latest_commit": changed_paths,
        "correct_repo_path": str(REPO),
        "created_at_utc": now_utc(),
        "current_all_in_one_panel_read_performed": False,
        "current_evidence_chain_quality_after_stall_diagnostic": quality,
        "edge_claim_allowed_now": False,
        "edge_claim_performed": False,
        "expected_completed_symbol_count_from_progress": LAST_REPORTED_SYMBOL_INDEX,
        "extra_tracked_python_count_explained": extra_explained,
        "extra_tracked_python_count_explanation": extra_explanation,
        "full_1h_panel_read_performed": False,
        "latest_commit_contains_only_stalled_record_tool": latest_commit_contains_only_stalled_record_tool,
        "load_errors": load_errors,
        "next_module": next_module,
        "okx_88_symbol_1h_panel_revised_build_stall_diagnostic_status": status,
        "output_valid_for_strategy_search": False,
        "partial_output_must_not_be_used_for_strategy_search": True,
        "partial_output_valid": False,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "retry_strategy_search_allowed_now": False,
        "revised_build_execution_completed": False,
        "revised_build_execution_tool_exists": (REPO / BUILD_TOOL_REL).exists(),
        "revised_build_execution_tool_tracked": is_tracked(BUILD_TOOL_REL),
        "revised_build_rerun_performed": False,
        "runtime_live_capital_allowed_now": False,
        "stall_diagnostic_performed": replacement_checks_all_true,
        "stalled_record_confirmed": stalled_record_confirmed,
        "strategy_search_allowed_now": False,
        "strategy_search_executed": False,
        "suspected_stall_cause_class": suspected_cause,
        "suspected_stall_symbol": SUSPECTED_NEXT_SYMBOL,
        "tracked_python_count_anomaly_attention": not extra_explained,
        "tracked_python_count_current": current_count,
        "tracked_python_count_delta_from_previous_known": delta,
        "tracked_python_count_previous_known": PREVIOUS_KNOWN_TRACKED_PYTHON_COUNT,
        "unexpected_git_status_entries": unexpected_status,
        "validator_executed": False,
    }
    record.update(
        {
            "last_reported_symbol_index": stalled_record.get("last_reported_symbol_index"),
            "last_reported_symbol": stalled_record.get("last_reported_symbol"),
            "suspected_next_symbol": stalled_record.get("suspected_next_symbol"),
        }
    )
    record.update(partial)
    record.update(rsr)

    git_context = {
        "changed_paths_latest_commit": changed_paths,
        "current_head": current_head,
        "latest_commit_contains_only_stalled_record_tool": latest_commit_contains_only_stalled_record_tool,
        "repo_clean_except_current_tool": repo_clean,
        "repo_top_level": top_level,
        "tracked_python_count_current": current_count,
        "tracked_python_count_delta_from_previous_known": delta,
        "tracked_python_count_previous_known": PREVIOUS_KNOWN_TRACKED_PYTHON_COUNT,
        "unexpected_git_status_entries": unexpected_status,
    }
    symbol_context_payload = {
        **symbol_context,
        **rsr,
        "expected_completed_symbol_count_from_progress": LAST_REPORTED_SYMBOL_INDEX,
        "last_reported_symbol": LAST_REPORTED_SYMBOL,
        "suspected_next_symbol": SUSPECTED_NEXT_SYMBOL,
        "suspected_stall_cause_class": suspected_cause,
        "suspected_stall_symbol": SUSPECTED_NEXT_SYMBOL,
    }
    approval = {
        "approval_grants_build_rerun_now": False,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_cleanup_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_future_resumable_execution_plan_next": approval_plan,
        "approval_grants_future_rsr_symbol_probe_next": approval_rsr,
        "approval_grants_stall_diagnostic_now": True,
        "approval_grants_strategy_search_execution_now": False,
        "approval_grants_strategy_search_retry_now": False,
        "approval_grants_validator_now": False,
        "next_module": next_module,
    }
    self_validator = {
        **record,
        "artifact_count_expected": 6,
        "artifacts_created": [
            "repo_only_okx_88_symbol_1h_panel_revised_build_stall_diagnostic.json",
            "repo_only_okx_88_symbol_1h_panel_revised_build_partial_output_inventory.json",
            "repo_only_okx_88_symbol_1h_panel_revised_build_stall_symbol_context.json",
            "repo_only_okx_88_symbol_1h_panel_revised_build_stall_git_context.json",
            "repo_only_okx_88_symbol_1h_panel_revised_build_stall_next_route_approval_record.json",
            "repo_only_okx_88_symbol_1h_panel_revised_build_stall_diagnostic_self_validator.json",
        ],
        "preview_status_observed": preview.get("okx_88_symbol_1h_panel_non_holdout_view_revised_build_retry_preview_status"),
        "redesign_status_observed": redesign.get("okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign_status"),
        "self_validation_created_at_utc": now_utc(),
    }
    return {
        "diagnostic": record,
        "partial_output_inventory": partial,
        "symbol_context": symbol_context_payload,
        "git_context": git_context,
        "approval": approval,
        "self_validator": self_validator,
    }


def write_outputs(outputs: dict[str, dict[str, Any]]) -> None:
    files = {
        "repo_only_okx_88_symbol_1h_panel_revised_build_stall_diagnostic.json": outputs["diagnostic"],
        "repo_only_okx_88_symbol_1h_panel_revised_build_partial_output_inventory.json": outputs[
            "partial_output_inventory"
        ],
        "repo_only_okx_88_symbol_1h_panel_revised_build_stall_symbol_context.json": outputs["symbol_context"],
        "repo_only_okx_88_symbol_1h_panel_revised_build_stall_git_context.json": outputs["git_context"],
        "repo_only_okx_88_symbol_1h_panel_revised_build_stall_next_route_approval_record.json": outputs[
            "approval"
        ],
        "repo_only_okx_88_symbol_1h_panel_revised_build_stall_diagnostic_self_validator.json": outputs[
            "self_validator"
        ],
    }
    for filename, payload in files.items():
        write_json(OUTPUT_DIR / filename, payload)


def main() -> int:
    outputs = build_outputs()
    write_outputs(outputs)
    print(json.dumps(outputs["diagnostic"], indent=2, sort_keys=True))
    return 0 if outputs["diagnostic"]["replacement_checks_all_true"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
