#!/usr/bin/env python3
"""Approved 88-symbol OKX 1m-to-1h build execution.

The build is deliberately narrow: it processes only the locked 88 complete
symbols, reads only already validated local ZIP/CSV sources, writes
pipeline-validation-only 1h output, and keeps research/backtest/edge blocked.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path(
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_execution_after_preview_approval_v1.py"
)
OUTPUT_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_execution_after_preview_approval_v1"
)
BUILD_PREVIEW_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_preview_after_full_coverage_summary_v1"
)
FINAL_SUMMARY_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_coverage_discovery_final_summary_after_generic_controller_v1"
)
GENERIC_DIR = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1"
CHUNK_01_EXEC_DIR = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_execution_after_preview_approval_v1"
CHUNK_02_EXEC_DIR = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_execution_after_preview_approval_v1"

PREVIEW = BUILD_PREVIEW_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_preview.json"
PREVIEW_APPROVAL = BUILD_PREVIEW_DIR / "repo_only_okx_88_symbol_near_3y_build_execution_approval_record.json"
PREVIEW_INPUT = BUILD_PREVIEW_DIR / "repo_only_okx_88_symbol_near_3y_build_input_manifest_preview.json"
COMPLETE_LOCKED = FINAL_SUMMARY_DIR / "repo_only_okx_full_usdt_swap_near_3y_complete_symbol_set_locked.json"
GAP_LOCKED = FINAL_SUMMARY_DIR / "repo_only_okx_full_usdt_swap_coverage_gap_symbol_set_locked.json"

OUTPUT_CSV = OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_pipeline_validation_only.csv"

EXPECTED_HEAD = "3b828f4"
EXPECTED_SELECTED_SYMBOL_COUNT = 88
EXPECTED_GAP_SYMBOL_COUNT = 215
EXPECTED_DAILY_FILE_COUNT = 1053
EXPECTED_SOURCE_ROWS_PER_SYMBOL = 1053 * 1440
EXPECTED_TOTAL_SOURCE_FILE_COUNT = 88 * 1053
EXPECTED_TOTAL_SOURCE_ROWS = 88 * EXPECTED_SOURCE_ROWS_PER_SYMBOL
EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H = 1053 * 24
EXPECTED_TOTAL_OUTPUT_ROWS_1H = 88 * EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H
START_DATE = date(2023, 7, 1)
END_DATE = date(2026, 5, 18)
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
    "pipeline_validation_only",
]
PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_EXECUTED_PENDING_VALIDATOR"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_EXECUTION_FAILED"
NEXT_PASS_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_after_execution_v1.py"
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_execution_blocked_record_v1.py"


@dataclass
class HourState:
    rows_by_open_time: dict[int, tuple[Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal]]
    conflict_open_times: set[int]
    manifest_refs: set[str]
    sha_refs: set[str]

    @classmethod
    def fresh(cls) -> "HourState":
        return cls(rows_by_open_time={}, conflict_open_times=set(), manifest_refs=set(), sha_refs=set())


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


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
    allowed = {f"?? {TOOL_REL.as_posix()}", f" M {TOOL_REL.as_posix()}", f"A  {TOOL_REL.as_posix()}"}
    unexpected = [line for line in lines if line.replace("\\", "/") not in allowed]
    return not unexpected, unexpected


def expected_dates() -> list[str]:
    days: list[str] = []
    current = START_DATE
    while current <= END_DATE:
        days.append(current.isoformat())
        current += timedelta(days=1)
    return days


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


def load_selected_file_manifest(selected_symbols: set[str]) -> dict[str, list[dict[str, Any]]]:
    by_symbol: dict[str, list[dict[str, Any]]] = {symbol: [] for symbol in selected_symbols}
    for chunk_id, path in chunk_manifest_paths().items():
        doc = read_json(path)
        for entry in doc.get("file_manifest", []):
            symbol = entry.get("symbol")
            if symbol in selected_symbols:
                if entry.get("chunk_id") != chunk_id:
                    raise ValueError(f"Manifest chunk mismatch in {path}: {entry.get('chunk_id')} vs {chunk_id}")
                if entry.get("available_for_validator") is not True:
                    raise ValueError(f"Selected symbol has unavailable file: {symbol} {entry.get('date')}")
                if entry.get("coverage_gap") is True:
                    raise ValueError(f"Selected symbol has coverage_gap=true: {symbol} {entry.get('date')}")
                by_symbol[symbol].append(entry)
    for symbol, entries in by_symbol.items():
        entries.sort(key=lambda row: row["date"])
    return by_symbol


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def zip_members_safe(names: Iterable[str]) -> bool:
    for name in names:
        pure = PurePosixPath(name)
        if pure.is_absolute() or ".." in pure.parts:
            return False
    return True


def parse_decimal(raw: str, field: str, *, optional_zero: bool = False) -> Decimal:
    if optional_zero and raw in {"", "None", "none", "NULL", "null"}:
        return Decimal("0")
    try:
        return Decimal(raw)
    except (InvalidOperation, TypeError) as exc:
        raise ValueError(f"Invalid decimal in {field}: {raw!r}") from exc


def parse_open_time_ms(raw: str) -> int:
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid open_time: {raw!r}") from exc
    if value < 0:
        raise ValueError(f"Invalid negative open_time: {raw!r}")
    return value


def hour_iso_from_ms(hour_ms: int) -> str:
    return datetime.fromtimestamp(hour_ms / 1000, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def emit_hour(writer: csv.writer, symbol: str, hour_ms: int, state: HourState) -> tuple[int, int]:
    clean_items = sorted((ts, row) for ts, row in state.rows_by_open_time.items() if ts not in state.conflict_open_times)
    source_row_count = len(clean_items)
    if source_row_count == 0:
        raise ValueError(f"No clean rows available for {symbol} hour {hour_iso_from_ms(hour_ms)}")
    first_row = clean_items[0][1]
    last_row = clean_items[-1][1]
    high = max(item[1][1] for item in clean_items)
    low = min(item[1][2] for item in clean_items)
    vol = sum((item[1][4] for item in clean_items), Decimal("0"))
    vol_ccy = sum((item[1][5] for item in clean_items), Decimal("0"))
    vol_quote = sum((item[1][6] for item in clean_items), Decimal("0"))
    complete = source_row_count == 60 and not state.conflict_open_times
    writer.writerow(
        [
            symbol,
            hour_iso_from_ms(hour_ms),
            str(first_row[0]),
            str(high),
            str(low),
            str(last_row[3]),
            str(vol),
            str(vol_ccy),
            str(vol_quote),
            source_row_count,
            "true" if complete else "false",
            ";".join(sorted(state.manifest_refs)),
            ";".join(sorted(state.sha_refs)),
            "true",
        ]
    )
    return (1 if complete else 0, 0 if complete else 1)


def process_zip_entry(
    entry: dict[str, Any],
    symbol: str,
    hour_states: dict[int, HourState],
) -> dict[str, int]:
    zip_path = Path(entry["local_zip_path"])
    expected_inner_csv = entry["expected_inner_csv"]
    expected_sha = entry.get("sha256")
    if not zip_path.exists():
        raise ValueError(f"Missing ZIP for selected symbol: {zip_path}")
    if expected_sha:
        actual_sha = sha256_file(zip_path)
        if actual_sha.lower() != str(expected_sha).lower():
            raise ValueError(f"SHA256 mismatch for {zip_path}")
    else:
        actual_sha = ""

    raw_rows = 0
    exact_duplicates = 0
    conflict_rows = 0
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        if not zip_members_safe(names):
            raise ValueError(f"ZIP path traversal detected: {zip_path}")
        if expected_inner_csv not in names:
            raise ValueError(f"Expected inner CSV missing in {zip_path}: {expected_inner_csv}")
        with zf.open(expected_inner_csv, "r") as binary_handle:
            text = (line.decode("utf-8-sig").rstrip("\r\n") for line in binary_handle)
            reader = csv.reader(text)
            try:
                header = next(reader)
            except StopIteration as exc:
                raise ValueError(f"Empty CSV in {zip_path}") from exc
            if header != EXPECTED_SCHEMA:
                raise ValueError(f"Schema mismatch in {zip_path}: {header}")
            for row in reader:
                if not row:
                    continue
                raw_rows += 1
                if len(row) != len(EXPECTED_SCHEMA):
                    raise ValueError(f"Row width mismatch in {zip_path}: {row!r}")
                if row[0] != symbol:
                    raise ValueError(f"Observed symbol mismatch in {zip_path}: {row[0]!r} vs {symbol!r}")
                open_time_ms = parse_open_time_ms(row[8])
                hour_ms = (open_time_ms // 3_600_000) * 3_600_000
                numeric = (
                    parse_decimal(row[1], "open"),
                    parse_decimal(row[2], "high"),
                    parse_decimal(row[3], "low"),
                    parse_decimal(row[4], "close"),
                    parse_decimal(row[5], "vol", optional_zero=True),
                    parse_decimal(row[6], "vol_ccy", optional_zero=True),
                    parse_decimal(row[7], "vol_quote", optional_zero=True),
                )
                state = hour_states[hour_ms]
                state.manifest_refs.add(f"{entry['chunk_id']}:{entry['date']}")
                state.sha_refs.add(str(expected_sha or actual_sha))
                prior = state.rows_by_open_time.get(open_time_ms)
                if prior is None:
                    state.rows_by_open_time[open_time_ms] = numeric
                elif prior == numeric:
                    exact_duplicates += 1
                else:
                    if open_time_ms not in state.conflict_open_times:
                        conflict_rows += 1
                    conflict_rows += 1
                    state.conflict_open_times.add(open_time_ms)
    return {
        "exact_duplicate_rows_dropped": exact_duplicates,
        "material_conflict_rows_quarantined": conflict_rows,
        "raw_source_rows_read": raw_rows,
    }


def build_execution() -> dict[str, Any]:
    head = git(["rev-parse", "--short", "HEAD"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    preview = read_json(PREVIEW)
    approval = read_json(PREVIEW_APPROVAL)
    preview_input = read_json(PREVIEW_INPUT)
    complete_locked = read_json(COMPLETE_LOCKED)
    gap_locked = read_json(GAP_LOCKED)
    selected_symbols = list(complete_locked.get("near_3y_complete_symbols") or [])
    gap_symbols = list(gap_locked.get("coverage_gap_symbols") or [])
    selected_set = set(selected_symbols)
    gap_set = set(gap_symbols)
    dates = expected_dates()
    build_preview_confirmed = (
        preview.get("okx_88_symbol_near_3y_1m_to_1h_build_preview_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_PREVIEW_CREATED"
        and preview.get("replacement_checks_all_true") is True
        and approval.get("approval_grants_future_88_symbol_1m_to_1h_build_execution_next") is True
        and approval.get("approval_grants_build_execution_now") is False
        and preview.get("selected_symbol_count") == EXPECTED_SELECTED_SYMBOL_COUNT
        and preview.get("excluded_gap_symbol_count") == EXPECTED_GAP_SYMBOL_COUNT
    )
    selected_symbols_all_have_1053_files = (
        preview.get("selected_symbols_all_have_1053_files") is True
        and complete_locked.get("expected_daily_file_count_per_symbol") == EXPECTED_DAILY_FILE_COUNT
        and len(selected_symbols) == EXPECTED_SELECTED_SYMBOL_COUNT
    )
    if head != EXPECTED_HEAD or not repo_clean or not build_preview_confirmed or not selected_symbols_all_have_1053_files:
        raise RuntimeError("Pre-build checkpoint or approval validation failed")
    if selected_set & gap_set:
        raise RuntimeError("Selected/gap symbol overlap detected")
    if preview_input.get("excluded_gap_symbols") and set(preview_input["excluded_gap_symbols"]) != gap_set:
        raise RuntimeError("Preview input gap symbols mismatch")

    by_symbol = load_selected_file_manifest(selected_set)
    for symbol, entries in by_symbol.items():
        entry_dates = [entry["date"] for entry in entries]
        if len(entries) != EXPECTED_DAILY_FILE_COUNT or entry_dates != dates:
            raise RuntimeError(f"Selected symbol manifest does not cover expected dates: {symbol}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    per_symbol_counts: list[dict[str, Any]] = []
    provenance_entries: list[dict[str, Any]] = []
    totals = defaultdict(int)

    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as output_handle:
        writer = csv.writer(output_handle)
        writer.writerow(OUTPUT_SCHEMA)
        for symbol_index, symbol in enumerate(selected_symbols, start=1):
            hour_states: dict[int, HourState] = defaultdict(HourState.fresh)
            symbol_raw_rows = 0
            symbol_exact_duplicates = 0
            symbol_conflicts = 0
            for entry in by_symbol[symbol]:
                counts = process_zip_entry(entry, symbol, hour_states)
                symbol_raw_rows += counts["raw_source_rows_read"]
                symbol_exact_duplicates += counts["exact_duplicate_rows_dropped"]
                symbol_conflicts += counts["material_conflict_rows_quarantined"]
                provenance_entries.append(
                    {
                        "chunk_id": entry["chunk_id"],
                        "date": entry["date"],
                        "expected_inner_csv": entry["expected_inner_csv"],
                        "local_zip_path": entry["local_zip_path"],
                        "sha256": entry.get("sha256"),
                        "symbol": symbol,
                    }
                )
            symbol_complete_hours = 0
            symbol_incomplete_hours = 0
            for hour_ms in sorted(hour_states):
                complete_count, incomplete_count = emit_hour(writer, symbol, hour_ms, hour_states[hour_ms])
                symbol_complete_hours += complete_count
                symbol_incomplete_hours += incomplete_count
            symbol_output_rows = symbol_complete_hours + symbol_incomplete_hours
            if symbol_output_rows != EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H:
                raise RuntimeError(f"Unexpected 1h row count for {symbol}: {symbol_output_rows}")
            clean_rows = symbol_raw_rows - symbol_exact_duplicates - symbol_conflicts
            per_symbol_counts.append(
                {
                    "clean_source_rows_after_policy": clean_rows,
                    "complete_1h_row_count": symbol_complete_hours,
                    "exact_duplicate_rows_dropped": symbol_exact_duplicates,
                    "incomplete_1h_row_count": symbol_incomplete_hours,
                    "material_conflict_rows_quarantined": symbol_conflicts,
                    "output_1h_row_count": symbol_output_rows,
                    "raw_source_rows_read": symbol_raw_rows,
                    "source_file_count_processed": len(by_symbol[symbol]),
                    "symbol": symbol,
                }
            )
            totals["raw_source_rows_read"] += symbol_raw_rows
            totals["exact_duplicate_rows_dropped"] += symbol_exact_duplicates
            totals["material_conflict_rows_quarantined"] += symbol_conflicts
            totals["clean_source_rows_after_policy"] += clean_rows
            totals["output_1h_row_count"] += symbol_output_rows
            totals["complete_1h_row_count"] += symbol_complete_hours
            totals["incomplete_1h_row_count"] += symbol_incomplete_hours
            totals["source_file_count_processed"] += len(by_symbol[symbol])
            print(f"[{now_utc()}] processed {symbol_index}/{len(selected_symbols)} {symbol}", flush=True)

    per_symbol_csv = OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_per_symbol_counts.csv"
    with per_symbol_csv.open("w", encoding="utf-8", newline="") as handle:
        fields = [
            "symbol",
            "source_file_count_processed",
            "raw_source_rows_read",
            "exact_duplicate_rows_dropped",
            "material_conflict_rows_quarantined",
            "clean_source_rows_after_policy",
            "output_1h_row_count",
            "complete_1h_row_count",
            "incomplete_1h_row_count",
        ]
        csv_writer = csv.DictWriter(handle, fieldnames=fields)
        csv_writer.writeheader()
        for row in per_symbol_counts:
            csv_writer.writerow(row)

    output_file_created = OUTPUT_CSV.exists() and OUTPUT_CSV.stat().st_size > 0
    per_symbol_output_row_count_valid = all(
        row["output_1h_row_count"] == EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H for row in per_symbol_counts
    )
    replacement_checks = {
        "build_preview_confirmed": build_preview_confirmed,
        "excluded_gap_symbol_count": len(gap_symbols) == EXPECTED_GAP_SYMBOL_COUNT,
        "expected_head": head == EXPECTED_HEAD,
        "no_gap_symbol_processed": not any(row["symbol"] in gap_set for row in per_symbol_counts),
        "output_1h_row_count": totals["output_1h_row_count"] == EXPECTED_TOTAL_OUTPUT_ROWS_1H,
        "output_file_created": output_file_created,
        "per_symbol_output_row_count_valid": per_symbol_output_row_count_valid,
        "repo_clean": repo_clean,
        "selected_symbol_count": len(selected_symbols) == EXPECTED_SELECTED_SYMBOL_COUNT,
        "selected_symbols_all_have_1053_files": selected_symbols_all_have_1053_files,
        "source_file_count_processed": totals["source_file_count_processed"] == EXPECTED_TOTAL_SOURCE_FILE_COUNT,
        "synthetic_forward_backfill_absent": True,
    }
    replacement_checks_all_true = all(replacement_checks.values())
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    next_module = NEXT_PASS_MODULE if replacement_checks_all_true else NEXT_BLOCKED_MODULE
    summary = {
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": preview.get("active_p1_attention_count", 0),
        "aggregation_performed_now": True,
        "all_hours_complete": totals["incomplete_1h_row_count"] == 0,
        "backfill_used": False,
        "broad_acquisition_ready": False,
        "build_execution_performed": replacement_checks_all_true,
        "build_preview_confirmed": build_preview_confirmed,
        "clean_source_rows_after_policy": totals["clean_source_rows_after_policy"],
        "complete_1h_row_count": totals["complete_1h_row_count"],
        "current_evidence_chain_quality_after_execution": (
            "OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_EXECUTED_PENDING_VALIDATOR"
            if replacement_checks_all_true
            else "OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_EXECUTION_BLOCKED_REVIEW_REQUIRED"
        ),
        "data_build_performed": True,
        "data_download_performed": False,
        "exact_duplicate_rows_dropped": totals["exact_duplicate_rows_dropped"],
        "excluded_gap_symbol_count": len(gap_symbols),
        "expected_output_rows_per_symbol_1h": EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H,
        "expected_source_rows_per_symbol": EXPECTED_SOURCE_ROWS_PER_SYMBOL,
        "expected_total_output_rows_1h": EXPECTED_TOTAL_OUTPUT_ROWS_1H,
        "expected_total_source_file_count": EXPECTED_TOTAL_SOURCE_FILE_COUNT,
        "expected_total_source_rows": EXPECTED_TOTAL_SOURCE_ROWS,
        "forward_fill_used": False,
        "full_csv_read_performed": True,
        "incomplete_1h_row_count": totals["incomplete_1h_row_count"],
        "material_conflict_rows_quarantined": totals["material_conflict_rows_quarantined"],
        "next_module": next_module,
        "okx_88_symbol_near_3y_1m_to_1h_build_execution_status": status,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "output_1h_row_count": totals["output_1h_row_count"],
        "output_file": str(OUTPUT_CSV),
        "output_file_created": output_file_created,
        "output_is_pipeline_validation_only": True,
        "output_manifest_created": replacement_checks_all_true,
        "output_schema_created": True,
        "output_valid_for_edge_claim": False,
        "output_valid_for_research_backtest": False,
        "per_symbol_output_row_count_valid": per_symbol_output_row_count_valid,
        "raw_source_rows_read": totals["raw_source_rows_read"],
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "selected_symbol_count": len(selected_symbols),
        "selected_symbols_all_have_1053_files": selected_symbols_all_have_1053_files,
        "source_file_count_processed": totals["source_file_count_processed"],
        "source_manifest_acquisition_ready": False,
        "synthetic_fill_used": False,
        "symbols_processed_count": len(per_symbol_counts),
        "tracked_python_count": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
        "created_at_utc": now_utc(),
    }
    manifest = {
        **summary,
        "output_schema": OUTPUT_SCHEMA,
        "per_symbol_counts_artifact": "repo_only_okx_88_symbol_near_3y_1m_to_1h_per_symbol_counts.csv",
        "pipeline_validation_only_output_file": str(OUTPUT_CSV),
        "selected_symbols": selected_symbols,
    }
    policy_effects = {
        "backfill_used": False,
        "complete_1h_row_count": totals["complete_1h_row_count"],
        "exact_duplicate_rows_dropped": totals["exact_duplicate_rows_dropped"],
        "forward_fill_used": False,
        "incomplete_1h_row_count": totals["incomplete_1h_row_count"],
        "material_conflict_rows_quarantined": totals["material_conflict_rows_quarantined"],
        "no_averaging_conflicting_rows": True,
        "no_choosing_conflicting_rows": True,
        "no_merging_conflicting_rows": True,
        "synthetic_fill_used": False,
    }
    schema_report = {
        "input_schema": EXPECTED_SCHEMA,
        "output_schema": OUTPUT_SCHEMA,
        "output_schema_created": True,
        "pipeline_validation_only": True,
    }
    provenance = {
        "provenance_entry_count": len(provenance_entries),
        "provenance_entries": provenance_entries,
    }
    return {
        "manifest": manifest,
        "policy_effects": policy_effects,
        "provenance": provenance,
        "schema_report": schema_report,
        "summary": summary,
    }


def write_reports(results: dict[str, Any]) -> None:
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_report.json", results["summary"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_manifest.json", results["manifest"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_policy_effects_report.json", results["policy_effects"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_output_schema_report.json", results["schema_report"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_provenance_manifest.json", results["provenance"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_summary.json", results["summary"])


def main() -> int:
    results = build_execution()
    write_reports(results)
    print(json.dumps(results["summary"], indent=2, sort_keys=True))
    return 0 if results["summary"]["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
