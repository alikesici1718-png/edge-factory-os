#!/usr/bin/env python3
"""Holdout-safe non-holdout 1h view build execution.

This execution fails closed before building if the approved source-date policy
cannot be reconciled with the required UTC output window/counts. It never reads
the current all-in-one 1h panel, never reads sealed-holdout source dates, and
never runs strategy search or candidate/edge actions.
"""

from __future__ import annotations

import csv
import json
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path("tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_execution_after_preview_v1.py")
OUTPUT_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_execution_after_preview_v1"

PREVIEW_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_preview_after_access_plan_v1"
PREVIEW = PREVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_preview.json"
PREVIEW_APPROVAL = PREVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_execution_approval_record.json"
ACCESS_PLAN = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan_after_blocked_strategy_execution_v1" / "repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan.json"

FINAL_SUMMARY_DIR = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_coverage_discovery_final_summary_after_generic_controller_v1"
COMPLETE_LOCKED = FINAL_SUMMARY_DIR / "repo_only_okx_full_usdt_swap_near_3y_complete_symbol_set_locked.json"
GENERIC_DIR = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1"
CHUNK_01_EXEC_DIR = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_execution_after_preview_approval_v1"
CHUNK_02_EXEC_DIR = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_execution_after_preview_approval_v1"

EXPECTED_HEAD = "880707a"
PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_VIEW_BUILD_EXECUTED_PENDING_VALIDATOR"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_VIEW_BUILD_EXECUTION_DATE_BOUNDARY_RECONCILIATION_REQUIRED"
NEXT_PASS_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_validator_after_execution_v1.py"
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_execution_blocked_record_v1.py"
PASS_QUALITY = "OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_VIEW_BUILD_EXECUTED_VALIDATOR_NEXT"
BLOCKED_QUALITY = "OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_VIEW_BUILD_EXECUTION_BLOCKED_DATE_BOUNDARY_RECONCILIATION_REQUIRED"
BLOCKER = "SOURCE_DATE_POLICY_AND_UTC_OUTPUT_WINDOW_COUNT_NOT_RECONCILED_WITH_ALLOWED_PRE_HOLDOUT_SOURCE_FILES"

EXPECTED_SCHEMA = ["instrument_name", "open", "high", "low", "close", "vol", "vol_ccy", "vol_quote", "open_time", "confirm"]
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
    "non_holdout_view",
]

SELECTED_SYMBOL_COUNT = 88
NON_HOLDOUT_VIEW_START = "2023-07-01T00:00:00Z"
NON_HOLDOUT_VIEW_END_EXCLUSIVE = "2025-11-01T00:00:00Z"
NON_HOLDOUT_SOURCE_START_DATE = "2023-07-01"
NON_HOLDOUT_SOURCE_END_DATE_INCLUSIVE = "2025-10-31"
SEALED_HOLDOUT_START = "2025-11-01T00:00:00Z"
EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 854
EXPECTED_TOTAL_SOURCE_FILE_COUNT = 75152
EXPECTED_TOTAL_SOURCE_ROWS = 108218880
EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H = 20496
EXPECTED_TOTAL_OUTPUT_ROWS_1H = 1803648


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def git(args: list[str]) -> str:
    proc = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={REPO.as_posix()}", "-C", str(REPO), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def tracked_python_count() -> int:
    output = git(["ls-files", "*.py"])
    return len([line for line in output.splitlines() if line.strip()])


def clean_status_allowing_tool() -> tuple[bool, list[str]]:
    lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    unexpected = [line for line in lines if not line.replace("\\", "/").endswith(TOOL_REL.as_posix())]
    return not unexpected, unexpected


def chunk_manifest_paths() -> dict[str, Path]:
    paths = {
        "chunk_01": CHUNK_01_EXEC_DIR / "historical_okx_full_usdt_swap_first_chunk_download_file_manifest_after_execution.json",
        "chunk_02": CHUNK_02_EXEC_DIR / "historical_okx_full_usdt_swap_chunk_02_download_file_manifest_after_execution.json",
        "chunk_03": GENERIC_DIR / "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_chunk_download_manifest_after_execution.json",
    }
    for chunk_num in range(4, 17):
        chunk_id = f"chunk_{chunk_num:02d}"
        paths[chunk_id] = GENERIC_DIR / f"historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_{chunk_id}_download_manifest_after_execution.json"
    return paths


def zip_members_safe(names: Iterable[str]) -> bool:
    for name in names:
        pure = PurePosixPath(name)
        if pure.is_absolute() or ".." in pure.parts:
            return False
    return True


def iso_from_ms(raw: str) -> str:
    value = int(raw)
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_inputs() -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    loaded: dict[str, dict[str, Any]] = {}
    errors: dict[str, str] = {}
    for label, path in {
        "preview": PREVIEW,
        "preview_approval": PREVIEW_APPROVAL,
        "access_plan": ACCESS_PLAN,
        "complete_locked": COMPLETE_LOCKED,
    }.items():
        try:
            loaded[label] = read_json(path)
        except (OSError, json.JSONDecodeError, RuntimeError) as exc:
            errors[label] = f"{path}: {exc}"
    return loaded, errors


def selected_non_holdout_entries(selected_symbols: set[str]) -> dict[str, list[dict[str, Any]]]:
    by_symbol: dict[str, list[dict[str, Any]]] = {symbol: [] for symbol in selected_symbols}
    for chunk_id, path in chunk_manifest_paths().items():
        doc = read_json(path)
        for entry in doc.get("file_manifest", []):
            symbol = entry.get("symbol")
            date = entry.get("date")
            if symbol in selected_symbols and NON_HOLDOUT_SOURCE_START_DATE <= date <= NON_HOLDOUT_SOURCE_END_DATE_INCLUSIVE:
                if entry.get("chunk_id") != chunk_id:
                    raise RuntimeError(f"Manifest chunk mismatch: {path}")
                if entry.get("available_for_validator") is not True or entry.get("coverage_gap") is True:
                    raise RuntimeError(f"Selected non-holdout source unavailable: {symbol} {date}")
                by_symbol[symbol].append(entry)
            if symbol in selected_symbols and date >= "2025-11-01":
                # Metadata only: count is not read from source files.
                continue
    for symbol, entries in by_symbol.items():
        entries.sort(key=lambda row: row["date"])
    return by_symbol


def read_boundary_rows(entries: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    """Read one allowed earliest row and one allowed latest row to prove timestamp boundaries."""
    first_symbol = sorted(entries)[0]
    earliest = entries[first_symbol][0]
    latest = entries[first_symbol][-1]
    samples = []
    for label, entry, want_last in [("earliest_allowed_source_file", earliest, False), ("latest_allowed_source_file", latest, True)]:
        zip_path = Path(entry["local_zip_path"])
        with zipfile.ZipFile(zip_path) as zf:
            names = zf.namelist()
            if not zip_members_safe(names):
                raise RuntimeError(f"ZIP path traversal detected: {zip_path}")
            expected_inner = entry["expected_inner_csv"]
            if expected_inner not in names:
                raise RuntimeError(f"Expected inner CSV missing: {zip_path}")
            with zf.open(expected_inner, "r") as binary_handle:
                text = (line.decode("utf-8-sig").rstrip("\r\n") for line in binary_handle)
                reader = csv.reader(text)
                header = next(reader)
                if header != EXPECTED_SCHEMA:
                    raise RuntimeError(f"Schema mismatch in {zip_path}")
                chosen = None
                for row in reader:
                    if row:
                        chosen = row
                        if not want_last:
                            break
                if chosen is None:
                    raise RuntimeError(f"No rows in {zip_path}")
                samples.append(
                    {
                        "date": entry["date"],
                        "label": label,
                        "open_time_utc": iso_from_ms(chosen[8]),
                        "symbol": chosen[0],
                    }
                )
    return {
        "boundary_samples": samples,
        "earliest_allowed_source_file_first_row_utc": samples[0]["open_time_utc"],
        "latest_allowed_source_file_last_row_utc": samples[1]["open_time_utc"],
        "raw_source_rows_read_for_boundary_proof": 2,
    }


def build_execution() -> dict[str, Any]:
    head = git(["rev-parse", "--short", "HEAD"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    loaded, load_errors = load_inputs()
    preview = loaded.get("preview", {})
    approval = loaded.get("preview_approval", {})
    access_plan = loaded.get("access_plan", {})
    complete_locked = loaded.get("complete_locked", {})
    selected_symbols = list(complete_locked.get("near_3y_complete_symbols") or [])
    selected_set = set(selected_symbols)

    build_preview_confirmed = (
        preview.get("okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_preview_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_VIEW_BUILD_PREVIEW_READY"
        and preview.get("replacement_checks_all_true") is True
        and preview.get("selected_symbol_count") == SELECTED_SYMBOL_COUNT
        and preview.get("expected_total_source_file_count_non_holdout") == EXPECTED_TOTAL_SOURCE_FILE_COUNT
        and preview.get("expected_total_output_rows_1h_non_holdout") == EXPECTED_TOTAL_OUTPUT_ROWS_1H
        and approval.get("approval_grants_future_non_holdout_view_build_execution_next") is True
        and approval.get("approval_grants_non_holdout_view_build_now") is False
    )
    access_plan_confirmed = (
        access_plan.get("okx_88_symbol_1h_panel_holdout_safe_access_plan_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_HOLDOUT_SAFE_ACCESS_PLAN_READY"
        and access_plan.get("replacement_checks_all_true") is True
    )

    entries: dict[str, list[dict[str, Any]]] = {}
    boundary: dict[str, Any] = {}
    metadata_confirmed = False
    exact_blocker: str | None = None
    try:
        entries = selected_non_holdout_entries(selected_set)
        metadata_confirmed = (
            len(selected_symbols) == SELECTED_SYMBOL_COUNT
            and all(len(rows) == EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL for rows in entries.values())
            and sum(len(rows) for rows in entries.values()) == EXPECTED_TOTAL_SOURCE_FILE_COUNT
            and max(row["date"] for rows in entries.values() for row in rows) == NON_HOLDOUT_SOURCE_END_DATE_INCLUSIVE
        )
        boundary = read_boundary_rows(entries) if metadata_confirmed else {}
    except Exception as exc:  # fail closed and record the exact cause
        exact_blocker = f"NON_HOLDOUT_SOURCE_METADATA_OR_BOUNDARY_PROOF_FAILED: {exc}"

    if exact_blocker is None:
        earliest = boundary.get("earliest_allowed_source_file_first_row_utc")
        latest = boundary.get("latest_allowed_source_file_last_row_utc")
        if earliest != "2023-06-30T16:00:00Z" or latest != "2025-10-31T15:59:00Z":
            exact_blocker = "UNEXPECTED_ALLOWED_SOURCE_FILE_TIMESTAMP_BOUNDARIES"
        else:
            exact_blocker = BLOCKER

    replacement_checks = {
        "access_plan_confirmed": access_plan_confirmed,
        "build_preview_confirmed": build_preview_confirmed,
        "current_all_in_one_panel_not_read": True,
        "current_head_matches_expected": head == EXPECTED_HEAD,
        "metadata_counts_confirmed": metadata_confirmed,
        "no_forbidden_source_dates_read": True,
        "repo_clean_except_current_tool": repo_clean,
        "strategy_search_not_executed": True,
    }
    # This execution is intentionally blocked because UTC output window/counts
    # cannot be reconciled with the approved source-date-only policy.
    replacement_checks_all_true = False
    status = BLOCKED_STATUS
    next_module = NEXT_BLOCKED_MODULE

    source_file_count = sum(len(rows) for rows in entries.values()) if entries else 0
    report = {
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 0,
        "access_plan_confirmed": access_plan_confirmed,
        "aggregation_performed_now": False,
        "aggregation_policy_carried_forward": True,
        "backfill_used": False,
        "build_preview_confirmed": build_preview_confirmed,
        "candidate_generation_allowed_now": False,
        "candidate_generation_performed": False,
        "clean_source_rows_after_policy": 0,
        "complete_1h_row_count": 0,
        "current_all_in_one_panel_read_performed": False,
        "current_evidence_chain_quality_after_build_execution": BLOCKED_QUALITY,
        "data_build_performed": False,
        "data_download_performed": False,
        "duplicate_conflict_policy_carried_forward": True,
        "edge_claim_allowed_now": False,
        "edge_claim_performed": False,
        "exact_blocker": exact_blocker,
        "exact_duplicate_rows_dropped": 0,
        "expected_daily_file_count_per_symbol_non_holdout": EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "expected_output_rows_per_symbol_1h_non_holdout": EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H,
        "expected_total_output_rows_1h_non_holdout": EXPECTED_TOTAL_OUTPUT_ROWS_1H,
        "expected_total_source_file_count_non_holdout": EXPECTED_TOTAL_SOURCE_FILE_COUNT,
        "expected_total_source_rows_non_holdout": EXPECTED_TOTAL_SOURCE_ROWS,
        "forward_fill_used": False,
        "full_1h_panel_read_performed": False,
        "future_validator_required": True,
        "incomplete_1h_row_count": 0,
        "incomplete_hour_policy_carried_forward": True,
        "material_conflict_rows_quarantined": 0,
        "next_module": next_module,
        "non_holdout_source_end_date_inclusive": NON_HOLDOUT_SOURCE_END_DATE_INCLUSIVE,
        "non_holdout_source_start_date": NON_HOLDOUT_SOURCE_START_DATE,
        "non_holdout_view_build_execution_performed": False,
        "non_holdout_view_end_exclusive": NON_HOLDOUT_VIEW_END_EXCLUSIVE,
        "non_holdout_view_start": NON_HOLDOUT_VIEW_START,
        "okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_execution_status": status,
        "output_1h_row_count": 0,
        "output_file_created": False,
        "output_is_non_holdout_view": False,
        "output_manifest_created": True,
        "output_max_timestamp": None,
        "output_min_timestamp": None,
        "output_physically_excludes_sealed_holdout": False,
        "output_schema_created": True,
        "output_symbol_count": 0,
        "output_timestamps_all_lt_sealed_holdout_start": False,
        "output_valid_for_edge_claim": False,
        "output_valid_for_strategy_search_after_execution": False,
        "output_valid_for_strategy_search_after_validator": False,
        "per_symbol_output_row_count_valid": False,
        "raw_source_rows_read": boundary.get("raw_source_rows_read_for_boundary_proof", 0),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "sealed_holdout_rows_read_count": 0,
        "sealed_holdout_rows_written_count": 0,
        "sealed_holdout_source_file_read_count": 0,
        "sealed_holdout_window_start": SEALED_HOLDOUT_START,
        "selected_symbol_count": len(selected_symbols),
        "source_file_count_matches_expected": source_file_count == EXPECTED_TOTAL_SOURCE_FILE_COUNT,
        "source_file_count_processed": source_file_count,
        "source_file_date_max_read": NON_HOLDOUT_SOURCE_END_DATE_INCLUSIVE if source_file_count else None,
        "source_file_dates_all_lt_sealed_holdout_start": True,
        "source_zip_csv_row_read_performed": boundary.get("raw_source_rows_read_for_boundary_proof", 0) > 0,
        "strategy_search_allowed_now": False,
        "strategy_search_executed": False,
        "strategy_search_retry_allowed_now": False,
        "runtime_live_capital_allowed_now": False,
        "synthetic_fill_used": False,
        "tracked_python_count_at_build_execution_run": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
        "validation_load_errors": load_errors,
        **boundary,
    }
    output_manifest = {
        "blocked_before_output_panel_write": True,
        "expected_output_schema": OUTPUT_SCHEMA,
        "non_holdout_output_file": str(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view.csv"),
        "output_file_created": False,
        "output_is_non_holdout_view": False,
        "output_valid_for_edge_claim": False,
        "output_valid_for_strategy_search_after_execution": False,
        "status": status,
    }
    source_inclusion = {
        "allowed_date_start": NON_HOLDOUT_SOURCE_START_DATE,
        "allowed_date_end_inclusive": NON_HOLDOUT_SOURCE_END_DATE_INCLUSIVE,
        "source_file_count_matches_expected": source_file_count == EXPECTED_TOTAL_SOURCE_FILE_COUNT,
        "source_file_count_processed": source_file_count,
        "source_file_dates_all_lt_sealed_holdout_start": True,
        "source_symbols_count": len(entries),
    }
    source_exclusion = {
        "forbidden_date_start": "2025-11-01",
        "metadata_only_exclusion_policy": True,
        "sealed_holdout_source_file_read_count": 0,
        "sealed_holdout_window_start": SEALED_HOLDOUT_START,
    }
    policy_effects = {
        "aggregation_policy_carried_forward": True,
        "duplicate_conflict_policy_carried_forward": True,
        "incomplete_hour_policy_carried_forward": True,
        "material_conflict_rows_quarantined": 0,
        "policy_not_applied_to_full_build_due_to_blocker": True,
    }
    incomplete = {
        "complete_1h_row_count": 0,
        "incomplete_1h_row_count": 0,
        "incomplete_hour_policy_carried_forward": True,
        "report_blocked_before_output_rows": True,
    }
    provenance = {
        "boundary_proof": boundary,
        "current_all_in_one_panel_read_performed": False,
        "sealed_holdout_source_file_read_count": 0,
        "source_zip_csv_row_read_performed": report["source_zip_csv_row_read_performed"],
    }
    summary = report.copy()
    self_validator = {
        "created_at_utc": now_utc(),
        "expected_head": EXPECTED_HEAD,
        "latest_head_at_run": head,
        "output_dir": str(OUTPUT_DIR),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "status": status,
        "tool_path": str(REPO / TOOL_REL),
    }
    return {
        "report": report,
        "output_manifest": output_manifest,
        "output_schema": {"output_schema": OUTPUT_SCHEMA, "output_schema_created": True},
        "source_inclusion": source_inclusion,
        "source_exclusion": source_exclusion,
        "policy_effects": policy_effects,
        "incomplete": incomplete,
        "provenance": provenance,
        "summary": summary,
        "self_validator": self_validator,
    }


def write_outputs(outputs: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    files = {
        "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_execution_report.json": outputs["report"],
        "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_output_manifest.json": outputs["output_manifest"],
        "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_output_schema.json": outputs["output_schema"],
        "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_source_inclusion_ledger.json": outputs["source_inclusion"],
        "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_source_exclusion_ledger.json": outputs["source_exclusion"],
        "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_policy_effects.json": outputs["policy_effects"],
        "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_incomplete_hour_report.json": outputs["incomplete"],
        "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_provenance_report.json": outputs["provenance"],
        "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_execution_summary.json": outputs["summary"],
        "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_execution_self_validator.json": outputs["self_validator"],
    }
    for filename, payload in files.items():
        write_json(OUTPUT_DIR / filename, payload)


def main() -> int:
    outputs = build_execution()
    write_outputs(outputs)
    print(json.dumps(outputs["report"], indent=2, sort_keys=True))
    return 0 if outputs["report"]["replacement_checks_all_true"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
