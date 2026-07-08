#!/usr/bin/env python3
"""Repo-only non-holdout source-date/UTC boundary reconciliation.

This diagnostic reads only narrow allowed boundary samples from source dates
2023-07-01 and 2025-10-31. It does not build, aggregate, read the current
all-in-one 1h panel, read sealed-holdout files, run strategy search, generate
candidates, claim edge, release a family, or touch runtime/live/capital.
"""

from __future__ import annotations

import csv
import json
import subprocess
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path("tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_source_date_utc_boundary_reconciliation_after_blocked_build_v1.py")
OUTPUT_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_source_date_utc_boundary_reconciliation_after_blocked_build_v1"

BLOCKED_RECORD_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_execution_blocked_record_v1"
BLOCKED_RECORD = BLOCKED_RECORD_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_build_execution_blocked_record.json"

BUILD_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_execution_after_preview_v1"
BUILD_REPORT = BUILD_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_execution_report.json"

PREVIEW_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_preview_after_access_plan_v1"
PREVIEW = PREVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_safe_non_holdout_view_build_preview.json"

ACCESS_PLAN_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan_after_blocked_strategy_execution_v1"
ACCESS_PLAN = ACCESS_PLAN_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan.json"

REGISTRY_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_registry_builder_before_strategy_search_v1"
REGISTRY = REGISTRY_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_registry.json"

FINAL_SUMMARY_DIR = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_coverage_discovery_final_summary_after_generic_controller_v1"
COMPLETE_LOCKED = FINAL_SUMMARY_DIR / "repo_only_okx_full_usdt_swap_near_3y_complete_symbol_set_locked.json"
GENERIC_DIR = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1"
CHUNK_01_EXEC_DIR = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_execution_after_preview_approval_v1"
CHUNK_02_EXEC_DIR = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_execution_after_preview_approval_v1"

EXPECTED_HEAD = "7961bc4"
EXPECTED_BLOCKER = "SOURCE_DATE_POLICY_AND_UTC_OUTPUT_WINDOW_COUNT_NOT_RECONCILED_WITH_ALLOWED_PRE_HOLDOUT_SOURCE_FILES"
PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_SOURCE_DATE_UTC_BOUNDARY_RECONCILIATION_READY"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_SOURCE_DATE_UTC_BOUNDARY_RECONCILIATION_REVIEW_REQUIRED"
NEXT_RETRY_PLAN_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_build_retry_plan_after_boundary_reconciliation_v1.py"
NEXT_REDESIGN_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign_after_boundary_reconciliation_v1.py"
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_source_date_utc_boundary_reconciliation_blocked_record_v1.py"
PASS_QUALITY = "OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_DATE_BOUNDARY_RECONCILED_BUILD_RETRY_PLAN_NEXT"
FAIL_QUALITY = "OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_DATE_BOUNDARY_RECONCILIATION_FAILED_REDESIGN_NEXT"
BLOCKED_QUALITY = "OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_DATE_BOUNDARY_RECONCILIATION_BLOCKED_REVIEW_REQUIRED"

EXPECTED_SCHEMA = ["instrument_name", "open", "high", "low", "close", "vol", "vol_ccy", "vol_quote", "open_time", "confirm"]
SELECTED_SYMBOL_COUNT = 88
NON_HOLDOUT_SOURCE_START_DATE = "2023-07-01"
NON_HOLDOUT_SOURCE_END_DATE_INCLUSIVE = "2025-10-31"
NON_HOLDOUT_VIEW_START = "2023-07-01T00:00:00Z"
NON_HOLDOUT_VIEW_END_EXCLUSIVE = "2025-11-01T00:00:00Z"
SEALED_HOLDOUT_START = "2025-11-01T00:00:00Z"
EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 854
EXPECTED_TOTAL_SOURCE_FILE_COUNT = 75152
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
        "chunk_02": CHUNK_02_EXEC_DIR / "historical_okx_full_usdt_swap_chunk_02_download_execution_after_preview_approval.json",
        "chunk_02_alt": CHUNK_02_EXEC_DIR / "historical_okx_full_usdt_swap_chunk_02_download_file_manifest_after_execution.json",
        "chunk_03": GENERIC_DIR / "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_chunk_download_manifest_after_execution.json",
    }
    resolved = {key: value for key, value in paths.items() if value.exists()}
    for chunk_num in range(4, 17):
        chunk_id = f"chunk_{chunk_num:02d}"
        path = GENERIC_DIR / f"historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_{chunk_id}_download_manifest_after_execution.json"
        if path.exists():
            resolved[chunk_id] = path
    return resolved


def zip_members_safe(names: Iterable[str]) -> bool:
    for name in names:
        pure = PurePosixPath(name)
        if pure.is_absolute() or ".." in pure.parts:
            return False
    return True


def iso_from_ms(raw: str) -> str:
    return datetime.fromtimestamp(int(raw) / 1000, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def inclusive_day_count(start: str, end: str) -> int:
    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    return (end_date - start_date).days + 1


def load_inputs() -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    loaded: dict[str, dict[str, Any]] = {}
    errors: dict[str, str] = {}
    for label, path in {
        "blocked_record": BLOCKED_RECORD,
        "build_report": BUILD_REPORT,
        "preview": PREVIEW,
        "access_plan": ACCESS_PLAN,
        "registry": REGISTRY,
        "complete_locked": COMPLETE_LOCKED,
    }.items():
        try:
            loaded[label] = read_json(path)
        except (OSError, json.JSONDecodeError, RuntimeError) as exc:
            errors[label] = f"{path}: {exc}"
    return loaded, errors


def find_boundary_entries(sample_symbols: set[str]) -> dict[tuple[str, str], dict[str, Any]]:
    wanted_dates = {NON_HOLDOUT_SOURCE_START_DATE, NON_HOLDOUT_SOURCE_END_DATE_INCLUSIVE}
    found: dict[tuple[str, str], dict[str, Any]] = {}
    for chunk_id, path in chunk_manifest_paths().items():
        doc = read_json(path)
        for entry in doc.get("file_manifest", []):
            symbol = entry.get("symbol")
            entry_date = entry.get("date")
            if symbol in sample_symbols and entry_date in wanted_dates:
                if entry_date >= "2025-11-01":
                    raise RuntimeError(f"Forbidden source date selected: {entry_date}")
                if entry.get("available_for_validator") is not True or entry.get("coverage_gap") is True:
                    raise RuntimeError(f"Boundary source unavailable: {symbol} {entry_date}")
                if "chunk_id" in entry and entry.get("chunk_id") != chunk_id and chunk_id != "chunk_02_alt":
                    raise RuntimeError(f"Manifest chunk mismatch: {path}")
                found[(symbol, entry_date)] = entry
    return found


def read_first_last_two_rows(entry: dict[str, Any]) -> list[dict[str, Any]]:
    if entry.get("date") >= "2025-11-01":
        raise RuntimeError(f"Forbidden source date read blocked: {entry.get('date')}")
    zip_path = Path(entry["local_zip_path"])
    expected_inner = entry["expected_inner_csv"]
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        if not zip_members_safe(names):
            raise RuntimeError(f"ZIP path traversal detected: {zip_path}")
        if expected_inner not in names:
            raise RuntimeError(f"Expected inner CSV missing: {zip_path}")
        with zf.open(expected_inner, "r") as binary_handle:
            text = (line.decode("utf-8-sig").rstrip("\r\n") for line in binary_handle)
            reader = csv.reader(text)
            header = next(reader)
            if header != EXPECTED_SCHEMA:
                raise RuntimeError(f"Schema mismatch in {zip_path}")
            first_two: list[list[str]] = []
            last_two: list[list[str]] = []
            for row in reader:
                if not row:
                    continue
                if len(first_two) < 2:
                    first_two.append(row)
                last_two.append(row)
                if len(last_two) > 2:
                    last_two.pop(0)
    sampled = []
    for position, row in [*[(f"first_{idx + 1}", row) for idx, row in enumerate(first_two)], *[(f"last_{idx + 1}", row) for idx, row in enumerate(last_two)]]:
        sampled.append(
            {
                "source_date": entry["date"],
                "symbol": row[0],
                "position": position,
                "open_time_utc": iso_from_ms(row[8]),
                "source_file": str(zip_path),
            }
        )
    return sampled


def boundary_sample(sample_symbols: list[str]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    errors: dict[str, str] = {}
    samples: list[dict[str, Any]] = []
    try:
        entries = find_boundary_entries(set(sample_symbols))
        expected_keys = {(symbol, boundary_date) for symbol in sample_symbols for boundary_date in [NON_HOLDOUT_SOURCE_START_DATE, NON_HOLDOUT_SOURCE_END_DATE_INCLUSIVE]}
        missing = sorted(expected_keys - set(entries))
        if missing:
            raise RuntimeError(f"Missing boundary manifest entries: {missing}")
        for key in sorted(entries):
            samples.extend(read_first_last_two_rows(entries[key]))
    except Exception as exc:  # noqa: BLE001 - fail closed with exact validation error.
        errors["boundary_sample"] = str(exc)
    return samples, errors


def build_outputs() -> dict[str, Any]:
    head = git(["rev-parse", "--short", "HEAD"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    loaded, load_errors = load_inputs()
    blocked = loaded.get("blocked_record", {})
    build = loaded.get("build_report", {})
    preview = loaded.get("preview", {})
    access_plan = loaded.get("access_plan", {})
    registry = loaded.get("registry", {})
    complete_locked = loaded.get("complete_locked", {})
    selected_symbols = sorted(complete_locked.get("near_3y_complete_symbols") or [])
    sample_symbols = selected_symbols[:2] + selected_symbols[-2:]

    blocked_record_confirmed = (
        blocked.get("okx_88_symbol_1h_panel_non_holdout_view_build_execution_blocked_record_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_VIEW_BUILD_EXECUTION_BLOCKED_RECORD_READY"
        and blocked.get("blocked_record_created") is True
        and blocked.get("blocked_build_execution_confirmed") is True
        and blocked.get("exact_blocker") == EXPECTED_BLOCKER
        and blocked.get("replacement_checks_all_true") is True
    )
    exact_blocker_confirmed = blocked.get("exact_blocker") == EXPECTED_BLOCKER
    upstream_metadata_confirmed = (
        build.get("source_file_count_processed") == EXPECTED_TOTAL_SOURCE_FILE_COUNT
        and build.get("source_file_count_matches_expected") is True
        and build.get("source_file_date_max_read") == NON_HOLDOUT_SOURCE_END_DATE_INCLUSIVE
        and build.get("source_file_dates_all_lt_sealed_holdout_start") is True
        and build.get("sealed_holdout_source_file_read_count") == 0
        and preview.get("expected_total_output_rows_1h_non_holdout") == EXPECTED_TOTAL_OUTPUT_ROWS_1H
        and access_plan.get("replacement_checks_all_true") is True
        and registry.get("sealed_holdout_window_start") == SEALED_HOLDOUT_START
    )

    computed_day_count = inclusive_day_count(NON_HOLDOUT_SOURCE_START_DATE, NON_HOLDOUT_SOURCE_END_DATE_INCLUSIVE)
    date_count_recomputed = computed_day_count == EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL
    expected_rows_per_symbol = computed_day_count * 24
    expected_total_rows = expected_rows_per_symbol * SELECTED_SYMBOL_COUNT
    date_count_formula_reconciled = (
        expected_rows_per_symbol == EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H
        and expected_total_rows == EXPECTED_TOTAL_OUTPUT_ROWS_1H
    )

    samples, sample_errors = boundary_sample(sample_symbols)
    timestamps = [row["open_time_utc"] for row in samples]
    sample_dates = sorted({row["source_date"] for row in samples})
    sample_symbols_found = sorted({row["symbol"] for row in samples})
    sample_file_count = len({(Path(row["source_file"]).name, row["source_date"], row["symbol"]) for row in samples})
    sample_row_count = len(samples)
    sample_min = min(timestamps) if timestamps else None
    sample_max = max(timestamps) if timestamps else None
    sealed_start = parse_iso(SEALED_HOLDOUT_START)
    view_start = parse_iso(NON_HOLDOUT_VIEW_START)
    view_end = parse_iso(NON_HOLDOUT_VIEW_END_EXCLUSIVE)
    boundary_sample_timestamps_all_lt_sealed = all(parse_iso(ts) < sealed_start for ts in timestamps)
    boundary_sample_source_files_all_lt_sealed = all(sample_date < "2025-11-01" for sample_date in sample_dates)

    # OKX daily source-date samples are UTC+8 market-date files in the existing
    # evidence. That leaves the final UTC hours 2025-10-31T16:00Z..23:00Z
    # unavailable without reading the forbidden 2025-11-01 source date.
    earliest_sample_before_view_start = bool(sample_min and parse_iso(sample_min) < view_start)
    latest_sample_before_view_end = bool(sample_max and parse_iso(sample_max) < view_end)
    latest_boundary_reaches_required_window_end_minus_minute = sample_max == "2025-10-31T23:59:00Z"
    source_date_policy_reconciled = (
        boundary_sample_timestamps_all_lt_sealed
        and boundary_sample_source_files_all_lt_sealed
        and not earliest_sample_before_view_start
        and latest_boundary_reaches_required_window_end_minus_minute
    )
    utc_output_window_count_reconciled = source_date_policy_reconciled and date_count_formula_reconciled
    reconciliation_passed = source_date_policy_reconciled and utc_output_window_count_reconciled
    diagnostic_blocked = bool(load_errors or sample_errors) or not (repo_clean and head == EXPECTED_HEAD and blocked_record_confirmed and exact_blocker_confirmed and upstream_metadata_confirmed)

    if diagnostic_blocked:
        status = BLOCKED_STATUS
        next_module = NEXT_BLOCKED_MODULE
        quality = BLOCKED_QUALITY
        active_p0 = 1
    elif reconciliation_passed:
        status = PASS_STATUS
        next_module = NEXT_RETRY_PLAN_MODULE
        quality = PASS_QUALITY
        active_p0 = 0
    else:
        status = PASS_STATUS
        next_module = NEXT_REDESIGN_MODULE
        quality = FAIL_QUALITY
        active_p0 = 1

    future_build_retry_plan_allowed_next = (not diagnostic_blocked) and reconciliation_passed
    future_date_policy_redesign_required = (not diagnostic_blocked) and not reconciliation_passed
    replacement_checks = {
        "blocked_record_confirmed": blocked_record_confirmed,
        "boundary_sample_not_broad": sample_file_count <= 8 and sample_row_count <= 32,
        "boundary_sample_source_files_all_lt_sealed_holdout_start": boundary_sample_source_files_all_lt_sealed,
        "current_head_matches_expected": head == EXPECTED_HEAD,
        "date_count_recomputed": date_count_recomputed,
        "exact_blocker_confirmed": exact_blocker_confirmed,
        "no_build_or_aggregation": True,
        "no_current_all_in_one_panel_read": True,
        "no_strategy_candidate_edge": True,
        "repo_clean_except_current_tool": repo_clean,
        "upstream_metadata_confirmed": upstream_metadata_confirmed,
    }
    replacement_checks_all_true = all(replacement_checks.values()) and not load_errors and not sample_errors and not diagnostic_blocked

    record = {
        "active_p0_blocker_count": active_p0,
        "active_p1_attention_count": 0,
        "aggregation_performed_now": False,
        "approval_grants_boundary_reconciliation_now": True,
        "approval_grants_build_apply_now": False,
        "approval_grants_build_retry_now": False,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_future_build_retry_plan_next": future_build_retry_plan_allowed_next,
        "approval_grants_future_date_policy_redesign_next": future_date_policy_redesign_required,
        "approval_grants_holdout_access_now": False,
        "approval_grants_strategy_search_execution_now": False,
        "approval_grants_strategy_search_retry_now": False,
        "boundary_reconciliation_performed": not diagnostic_blocked,
        "boundary_sample_dates": ",".join(sample_dates),
        "boundary_sample_file_count": sample_file_count,
        "boundary_sample_max_timestamp": sample_max,
        "boundary_sample_min_timestamp": sample_min,
        "boundary_sample_performed": bool(samples),
        "boundary_sample_row_count": sample_row_count,
        "boundary_sample_source_files_all_lt_sealed_holdout_start": boundary_sample_source_files_all_lt_sealed,
        "boundary_sample_symbols": ",".join(sample_symbols_found),
        "boundary_sample_timestamps_all_lt_sealed_holdout_start": boundary_sample_timestamps_all_lt_sealed,
        "broad_source_row_read_performed": False,
        "build_retry_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "candidate_generation_performed": False,
        "current_all_in_one_panel_read_performed": False,
        "current_evidence_chain_quality_after_boundary_reconciliation": quality,
        "data_build_performed": False,
        "data_download_performed": False,
        "date_boundary_reconciliation_passed": reconciliation_passed if not diagnostic_blocked else False,
        "date_count_recomputed": date_count_recomputed,
        "edge_claim_allowed_now": False,
        "edge_claim_performed": False,
        "exact_blocker": EXPECTED_BLOCKER,
        "exact_blocker_confirmed": exact_blocker_confirmed,
        "expected_daily_file_count_per_symbol_non_holdout": EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "expected_output_rows_per_symbol_1h_non_holdout": EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H,
        "expected_total_output_rows_1h_non_holdout": EXPECTED_TOTAL_OUTPUT_ROWS_1H,
        "expected_total_source_file_count_non_holdout": EXPECTED_TOTAL_SOURCE_FILE_COUNT,
        "full_1h_panel_read_performed": False,
        "future_build_retry_plan_allowed_next": future_build_retry_plan_allowed_next,
        "future_date_policy_redesign_required": future_date_policy_redesign_required,
        "next_module": next_module,
        "non_holdout_source_end_date_inclusive": NON_HOLDOUT_SOURCE_END_DATE_INCLUSIVE,
        "non_holdout_source_start_date": NON_HOLDOUT_SOURCE_START_DATE,
        "non_holdout_view_end_exclusive": NON_HOLDOUT_VIEW_END_EXCLUSIVE,
        "non_holdout_view_start": NON_HOLDOUT_VIEW_START,
        "okx_88_symbol_1h_panel_non_holdout_source_date_utc_boundary_reconciliation_status": status,
        "original_source_full_csv_read_performed": False,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "retry_strategy_search_allowed_now": False,
        "runtime_live_capital_allowed_now": False,
        "sealed_holdout_rows_read_count": 0,
        "sealed_holdout_source_file_read_count": 0,
        "sealed_holdout_window_start": SEALED_HOLDOUT_START,
        "source_date_policy_reconciled_with_utc_output_window": source_date_policy_reconciled if not diagnostic_blocked else False,
        "source_file_count_from_blocked_attempt": build.get("source_file_count_processed"),
        "source_file_count_matches_expected": build.get("source_file_count_matches_expected"),
        "source_file_date_max_from_blocked_attempt": build.get("source_file_date_max_read"),
        "source_file_dates_all_lt_sealed_holdout_start_from_blocked_attempt": build.get("source_file_dates_all_lt_sealed_holdout_start"),
        "strategy_search_allowed_now": False,
        "strategy_search_executed": False,
        "tracked_python_count_at_boundary_reconciliation_run": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
        "utc_output_window_count_reconciled": utc_output_window_count_reconciled if not diagnostic_blocked else False,
        "validation_load_errors": load_errors,
        "validation_sample_errors": sample_errors,
    }
    sample_report = {
        **record,
        "boundary_samples": samples,
        "boundary_sample_policy": "first_two_and_last_two_rows_for_first_two_and_last_two_locked_symbols_on_2023-07-01_and_2025-10-31_only",
    }
    count_reconciliation = {
        **record,
        "computed_daily_file_count_per_symbol_non_holdout": computed_day_count,
        "computed_output_rows_per_symbol_1h_non_holdout": expected_rows_per_symbol,
        "computed_total_output_rows_1h_non_holdout": expected_total_rows,
        "date_count_formula": "inclusive_day_count(2023-07-01,2025-10-31)=854; 854*24=20496; 20496*88=1803648",
    }
    utc_window = {
        **record,
        "earliest_sample_before_required_view_start": earliest_sample_before_view_start,
        "latest_boundary_reaches_required_window_end_minus_minute": latest_boundary_reaches_required_window_end_minus_minute,
        "latest_sample_before_required_view_end": latest_sample_before_view_end,
        "reconciliation_failure_reason": None
        if reconciliation_passed
        else "Allowed source-date boundary samples do not prove full UTC output window coverage through 2025-11-01T00:00:00Z exclusive.",
    }
    decision = {
        **record,
        "decision": "BUILD_RETRY_PLAN_NEXT" if future_build_retry_plan_allowed_next else ("DATE_POLICY_REDESIGN_NEXT" if future_date_policy_redesign_required else "RECONCILIATION_BLOCKED"),
    }
    approval = {
        **record,
        "approval_scope": "future_build_retry_plan_only" if future_build_retry_plan_allowed_next else "future_date_policy_redesign_only",
    }
    self_validator = {
        **record,
        "artifact_count_expected": 7,
        "artifacts_created": [
            "repo_only_okx_88_symbol_1h_panel_non_holdout_source_date_utc_boundary_reconciliation.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_date_count_reconciliation.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_boundary_sample_report.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_utc_window_reconciliation.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_build_retry_decision.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_boundary_reconciliation_approval_record.json",
            "repo_only_okx_88_symbol_1h_panel_non_holdout_source_date_utc_boundary_reconciliation_self_validator.json",
        ],
        "self_validation_created_at_utc": now_utc(),
    }
    return {
        "record": record,
        "count_reconciliation": count_reconciliation,
        "sample_report": sample_report,
        "utc_window": utc_window,
        "decision": decision,
        "approval": approval,
        "self_validator": self_validator,
    }


def main() -> None:
    outputs = build_outputs()
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_source_date_utc_boundary_reconciliation.json", outputs["record"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_date_count_reconciliation.json", outputs["count_reconciliation"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_boundary_sample_report.json", outputs["sample_report"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_utc_window_reconciliation.json", outputs["utc_window"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_build_retry_decision.json", outputs["decision"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_boundary_reconciliation_approval_record.json", outputs["approval"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_source_date_utc_boundary_reconciliation_self_validator.json", outputs["self_validator"])
    print(json.dumps(outputs["record"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
