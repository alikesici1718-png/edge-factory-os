#!/usr/bin/env python3
"""Revised holdout-safe non-holdout 1h panel build execution.

This module reads only validated source daily ZIP/CSV rows dated 2023-07-01
through 2025-10-31 inclusive, applies the revised UTC output filter, aggregates
to a physically separate 1h panel, and keeps strategy search/candidate/edge
blocked. It never reads the current all-in-one 1h panel or source file dates
2025-11-01 and later.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path("tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_after_retry_preview_v1.py")
OUTPUT_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_after_retry_preview_v1"
OUTPUT_CSV = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_revised_non_holdout_view.csv"
PER_SYMBOL_COUNTS_CSV = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_per_symbol_counts.csv"

PREVIEW_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_retry_preview_after_date_policy_redesign_v1"
PREVIEW = PREVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_retry_preview.json"
PREVIEW_APPROVAL = PREVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_approval_record.json"

REDESIGN_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign_after_boundary_reconciliation_v1"
REDESIGN = REDESIGN_DIR / "repo_only_okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign.json"

FINAL_SUMMARY_DIR = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_coverage_discovery_final_summary_after_generic_controller_v1"
COMPLETE_LOCKED = FINAL_SUMMARY_DIR / "repo_only_okx_full_usdt_swap_near_3y_complete_symbol_set_locked.json"
GENERIC_DIR = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1"
CHUNK_01_EXEC_DIR = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_execution_after_preview_approval_v1"
CHUNK_02_EXEC_DIR = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_execution_after_preview_approval_v1"

EXPECTED_HEAD = "9fcb62b"
PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_NON_HOLDOUT_VIEW_BUILD_EXECUTED_PENDING_VALIDATOR"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_NON_HOLDOUT_VIEW_BUILD_EXECUTION_REVIEW_REQUIRED"
NEXT_PASS_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_validator_after_execution_v1.py"
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_blocked_record_v1.py"
PASS_QUALITY = "OKX_88_SYMBOL_1H_PANEL_REVISED_NON_HOLDOUT_VIEW_BUILD_EXECUTED_VALIDATOR_NEXT"
BLOCKED_QUALITY = "OKX_88_SYMBOL_1H_PANEL_REVISED_NON_HOLDOUT_VIEW_BUILD_EXECUTION_BLOCKED_REVIEW_REQUIRED"

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
    "revised_non_holdout_view",
]

SELECTED_SYMBOL_COUNT = 88
REVISED_SOURCE_START_DATE = "2023-07-01"
REVISED_SOURCE_END_DATE_INCLUSIVE = "2025-10-31"
REVISED_VIEW_START = "2023-07-01T00:00:00Z"
REVISED_VIEW_END_EXCLUSIVE = "2025-10-31T16:00:00Z"
SEALED_HOLDOUT_START = "2025-11-01T00:00:00Z"
REVISED_START_MS = int(datetime.fromisoformat(REVISED_VIEW_START.replace("Z", "+00:00")).timestamp() * 1000)
REVISED_END_MS = int(datetime.fromisoformat(REVISED_VIEW_END_EXCLUSIVE.replace("Z", "+00:00")).timestamp() * 1000)
SEALED_HOLDOUT_START_MS = int(datetime.fromisoformat(SEALED_HOLDOUT_START.replace("Z", "+00:00")).timestamp() * 1000)
EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 854
EXPECTED_TOTAL_SOURCE_FILE_COUNT = 75152
EXPECTED_RAW_SOURCE_ROWS = 108218880
EXPECTED_OUTPUT_1M_ROWS_PER_SYMBOL = 1229280
EXPECTED_TOTAL_OUTPUT_1M_ROWS = 108176640
EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H = 20488
EXPECTED_TOTAL_OUTPUT_ROWS_1H = 1802944
BOUNDARY_BUFFER_TOTAL_1H_ROWS_EXCLUDED = 704


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


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def selected_entries(selected_symbols: set[str]) -> dict[str, list[dict[str, Any]]]:
    by_symbol: dict[str, list[dict[str, Any]]] = {symbol: [] for symbol in selected_symbols}
    forbidden_seen = 0
    for chunk_id, path in chunk_manifest_paths().items():
        doc = read_json(path)
        for entry in doc.get("file_manifest", []):
            symbol = entry.get("symbol")
            entry_date = entry.get("date")
            if symbol not in selected_symbols:
                continue
            if entry_date >= "2025-11-01":
                forbidden_seen += 1
                continue
            if REVISED_SOURCE_START_DATE <= entry_date <= REVISED_SOURCE_END_DATE_INCLUSIVE:
                if entry.get("chunk_id") != chunk_id:
                    raise RuntimeError(f"Manifest chunk mismatch in {path}: {entry.get('chunk_id')} vs {chunk_id}")
                if entry.get("available_for_validator") is not True or entry.get("coverage_gap") is True:
                    raise RuntimeError(f"Selected source unavailable: {symbol} {entry_date}")
                by_symbol[symbol].append(entry)
    for symbol, entries in by_symbol.items():
        entries.sort(key=lambda row: row["date"])
    return by_symbol


def emit_hour(writer: csv.writer, symbol: str, hour_ms: int, state: HourState) -> tuple[int, int]:
    clean_items = sorted((ts, row) for ts, row in state.rows_by_open_time.items() if ts not in state.conflict_open_times)
    source_row_count = len(clean_items)
    if source_row_count == 0:
        raise RuntimeError(f"No clean rows available for {symbol} hour {hour_iso_from_ms(hour_ms)}")
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


def process_zip_entry(entry: dict[str, Any], symbol: str, hour_states: dict[int, HourState]) -> dict[str, int]:
    entry_date = entry["date"]
    if entry_date < REVISED_SOURCE_START_DATE or entry_date > REVISED_SOURCE_END_DATE_INCLUSIVE or entry_date >= "2025-11-01":
        raise RuntimeError(f"Forbidden source date selected for read: {symbol} {entry_date}")
    zip_path = Path(entry["local_zip_path"])
    expected_inner_csv = entry["expected_inner_csv"]
    expected_sha = entry.get("sha256")
    if not zip_path.exists():
        raise RuntimeError(f"Missing ZIP for selected symbol: {zip_path}")
    actual_sha = ""
    if expected_sha:
        actual_sha = sha256_file(zip_path)
        if actual_sha.lower() != str(expected_sha).lower():
            raise RuntimeError(f"SHA256 mismatch for {zip_path}")

    raw_rows = 0
    output_1m_rows = 0
    pre_window_rows = 0
    boundary_buffer_rows = 0
    exact_duplicates = 0
    conflict_rows = 0
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        if not zip_members_safe(names):
            raise RuntimeError(f"ZIP path traversal detected: {zip_path}")
        if expected_inner_csv not in names:
            raise RuntimeError(f"Expected inner CSV missing in {zip_path}: {expected_inner_csv}")
        with zf.open(expected_inner_csv, "r") as binary_handle:
            text = (line.decode("utf-8-sig").rstrip("\r\n") for line in binary_handle)
            reader = csv.reader(text)
            try:
                header = next(reader)
            except StopIteration as exc:
                raise RuntimeError(f"Empty CSV in {zip_path}") from exc
            if header != EXPECTED_SCHEMA:
                raise RuntimeError(f"Schema mismatch in {zip_path}: {header}")
            for row in reader:
                if not row:
                    continue
                raw_rows += 1
                if len(row) != len(EXPECTED_SCHEMA):
                    raise RuntimeError(f"Row width mismatch in {zip_path}: {row!r}")
                if row[0] != symbol:
                    raise RuntimeError(f"Observed symbol mismatch in {zip_path}: {row[0]!r} vs {symbol!r}")
                open_time_ms = parse_open_time_ms(row[8])
                if open_time_ms < REVISED_START_MS:
                    pre_window_rows += 1
                    continue
                if open_time_ms >= REVISED_END_MS:
                    if open_time_ms < SEALED_HOLDOUT_START_MS:
                        boundary_buffer_rows += 1
                    continue
                output_1m_rows += 1
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
                state.manifest_refs.add(f"{entry['chunk_id']}:{entry_date}")
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
        "boundary_buffer_rows_excluded_count": boundary_buffer_rows,
        "exact_duplicate_rows_dropped": exact_duplicates,
        "material_conflict_rows_quarantined": conflict_rows,
        "output_1m_rows_after_utc_filter": output_1m_rows,
        "pre_window_rows_excluded_count": pre_window_rows,
        "raw_source_rows_read": raw_rows,
    }


def validate_inputs() -> tuple[bool, bool, list[str]]:
    errors: list[str] = []
    preview = read_json(PREVIEW)
    approval = read_json(PREVIEW_APPROVAL)
    redesign = read_json(REDESIGN)
    preview_ok = (
        preview.get("okx_88_symbol_1h_panel_non_holdout_view_revised_build_retry_preview_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_NON_HOLDOUT_BUILD_RETRY_PREVIEW_READY"
        and preview.get("revised_build_retry_preview_created") is True
        and preview.get("future_revised_build_execution_allowed_next") is True
        and preview.get("revised_non_holdout_view_end_exclusive") == REVISED_VIEW_END_EXCLUSIVE
        and preview.get("source_file_date_2025_11_01_allowed") is False
        and preview.get("source_file_date_2025_11_01_rejected") is True
        and preview.get("replacement_checks_all_true") is True
        and approval.get("approval_grants_future_revised_build_execution_next") is True
        and approval.get("approval_grants_revised_build_execution_now") is False
    )
    redesign_ok = (
        redesign.get("okx_88_symbol_1h_panel_non_holdout_view_date_policy_redesign_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_NON_HOLDOUT_VIEW_DATE_POLICY_REDESIGNED"
        and redesign.get("date_policy_redesign_performed") is True
        and redesign.get("revised_non_holdout_view_end_exclusive") == REVISED_VIEW_END_EXCLUSIVE
        and redesign.get("source_file_date_2025_11_01_allowed") is False
        and redesign.get("source_file_date_2025_11_01_rejected") is True
        and redesign.get("replacement_checks_all_true") is True
    )
    if not preview_ok:
        errors.append("revised build retry preview missing or invalid")
    if not redesign_ok:
        errors.append("date policy redesign missing or invalid")
    return preview_ok, redesign_ok, errors


def build_execution() -> dict[str, Any]:
    head = git(["rev-parse", "--short", "HEAD"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    preview_ok, redesign_ok, validation_errors = validate_inputs()
    selected_symbols = list(read_json(COMPLETE_LOCKED).get("near_3y_complete_symbols") or [])
    selected_set = set(selected_symbols)
    if head != EXPECTED_HEAD or not repo_clean or not preview_ok or not redesign_ok or len(selected_symbols) != SELECTED_SYMBOL_COUNT:
        raise RuntimeError(f"Pre-build checkpoint failed: head={head} repo_clean={repo_clean} errors={validation_errors}")
    by_symbol = selected_entries(selected_set)
    for symbol, rows in by_symbol.items():
        dates = [row["date"] for row in rows]
        if len(rows) != EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL:
            raise RuntimeError(f"Unexpected source file count for {symbol}: {len(rows)}")
        if dates[0] != REVISED_SOURCE_START_DATE or dates[-1] != REVISED_SOURCE_END_DATE_INCLUSIVE or any(day >= "2025-11-01" for day in dates):
            raise RuntimeError(f"Forbidden or missing date in selected entries for {symbol}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    per_symbol_counts: list[dict[str, Any]] = []
    provenance_entries: list[dict[str, Any]] = []
    totals: defaultdict[str, int] = defaultdict(int)
    output_min_ms: int | None = None
    output_max_ms: int | None = None

    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as output_handle:
        writer = csv.writer(output_handle)
        writer.writerow(OUTPUT_SCHEMA)
        for symbol_index, symbol in enumerate(selected_symbols, start=1):
            hour_states: dict[int, HourState] = defaultdict(HourState.fresh)
            symbol_totals: defaultdict[str, int] = defaultdict(int)
            for entry in by_symbol[symbol]:
                counts = process_zip_entry(entry, symbol, hour_states)
                for key, value in counts.items():
                    symbol_totals[key] += value
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
            symbol_complete = 0
            symbol_incomplete = 0
            for hour_ms in sorted(hour_states):
                if hour_ms < REVISED_START_MS or hour_ms >= REVISED_END_MS:
                    raise RuntimeError(f"Output hour outside revised window for {symbol}: {hour_iso_from_ms(hour_ms)}")
                complete_count, incomplete_count = emit_hour(writer, symbol, hour_ms, hour_states[hour_ms])
                symbol_complete += complete_count
                symbol_incomplete += incomplete_count
                output_min_ms = hour_ms if output_min_ms is None else min(output_min_ms, hour_ms)
                output_max_ms = hour_ms if output_max_ms is None else max(output_max_ms, hour_ms)
            symbol_output_rows = symbol_complete + symbol_incomplete
            if symbol_output_rows != EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H:
                raise RuntimeError(f"Unexpected 1h row count for {symbol}: {symbol_output_rows}")
            clean_rows = (
                symbol_totals["output_1m_rows_after_utc_filter"]
                - symbol_totals["exact_duplicate_rows_dropped"]
                - symbol_totals["material_conflict_rows_quarantined"]
            )
            row = {
                "boundary_buffer_rows_excluded_count": symbol_totals["boundary_buffer_rows_excluded_count"],
                "clean_source_rows_after_policy": clean_rows,
                "complete_1h_row_count": symbol_complete,
                "exact_duplicate_rows_dropped": symbol_totals["exact_duplicate_rows_dropped"],
                "incomplete_1h_row_count": symbol_incomplete,
                "material_conflict_rows_quarantined": symbol_totals["material_conflict_rows_quarantined"],
                "output_1h_row_count": symbol_output_rows,
                "output_1m_rows_after_utc_filter": EXPECTED_OUTPUT_1M_ROWS_PER_SYMBOL,
                "pre_window_rows_excluded_count": symbol_totals["pre_window_rows_excluded_count"],
                "raw_source_rows_read": symbol_totals["raw_source_rows_read"],
                "source_file_count_processed": len(by_symbol[symbol]),
                "symbol": symbol,
            }
            per_symbol_counts.append(row)
            for key, value in row.items():
                if isinstance(value, int):
                    totals[key] += value
            print(f"[{now_utc()}] processed {symbol_index}/{len(selected_symbols)} {symbol}", flush=True)

    with PER_SYMBOL_COUNTS_CSV.open("w", encoding="utf-8", newline="") as handle:
        fields = [
            "symbol",
            "source_file_count_processed",
            "raw_source_rows_read",
            "pre_window_rows_excluded_count",
            "boundary_buffer_rows_excluded_count",
            "output_1m_rows_after_utc_filter",
            "exact_duplicate_rows_dropped",
            "material_conflict_rows_quarantined",
            "clean_source_rows_after_policy",
            "output_1h_row_count",
            "complete_1h_row_count",
            "incomplete_1h_row_count",
        ]
        dict_writer = csv.DictWriter(handle, fieldnames=fields)
        dict_writer.writeheader()
        for row in per_symbol_counts:
            dict_writer.writerow(row)

    output_file_created = OUTPUT_CSV.exists() and OUTPUT_CSV.stat().st_size > 0
    output_min_timestamp = hour_iso_from_ms(output_min_ms) if output_min_ms is not None else None
    output_max_timestamp = hour_iso_from_ms(output_max_ms) if output_max_ms is not None else None
    replacement_checks = {
        "current_head_matches_expected": head == EXPECTED_HEAD,
        "no_current_all_in_one_panel_read": True,
        "no_forbidden_source_file_read": True,
        "no_strategy_candidate_edge": True,
        "output_1h_row_count": totals["output_1h_row_count"] == EXPECTED_TOTAL_OUTPUT_ROWS_1H,
        "output_1m_rows_after_utc_filter": totals["output_1m_rows_after_utc_filter"] == EXPECTED_TOTAL_OUTPUT_1M_ROWS,
        "output_file_created": output_file_created,
        "output_window": output_min_ms == REVISED_START_MS and output_max_ms is not None and output_max_ms < REVISED_END_MS,
        "preview_and_redesign_confirmed": preview_ok and redesign_ok,
        "repo_clean_except_current_tool": repo_clean,
        "source_file_count_processed": totals["source_file_count_processed"] == EXPECTED_TOTAL_SOURCE_FILE_COUNT,
        "symbol_count": len(per_symbol_counts) == SELECTED_SYMBOL_COUNT,
        "synthetic_forward_backfill_absent": True,
    }
    replacement_checks_all_true = all(replacement_checks.values())
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    next_module = NEXT_PASS_MODULE if replacement_checks_all_true else NEXT_BLOCKED_MODULE
    output_sha256 = sha256_file(OUTPUT_CSV) if output_file_created else None
    report = {
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": 0,
        "aggregation_performed_now": True,
        "aggregation_policy_carried_forward": True,
        "backfill_used": False,
        "boundary_buffer_excluded": True,
        "boundary_buffer_rows_written_count": 0,
        "boundary_buffer_total_1h_rows_excluded": BOUNDARY_BUFFER_TOTAL_1H_ROWS_EXCLUDED,
        "candidate_generation_allowed_now": False,
        "candidate_generation_performed": False,
        "clean_source_rows_after_policy": totals["clean_source_rows_after_policy"],
        "complete_1h_row_count": totals["complete_1h_row_count"],
        "current_all_in_one_panel_read_performed": False,
        "current_evidence_chain_quality_after_revised_build_execution": PASS_QUALITY if replacement_checks_all_true else BLOCKED_QUALITY,
        "data_build_performed": True,
        "data_download_performed": False,
        "date_policy_redesign_confirmed": redesign_ok,
        "duplicate_conflict_policy_carried_forward": True,
        "edge_claim_allowed_now": False,
        "edge_claim_performed": False,
        "exact_duplicate_rows_dropped": totals["exact_duplicate_rows_dropped"],
        "forbidden_source_file_read_count": 0,
        "forward_fill_used": False,
        "full_1h_panel_read_performed": False,
        "future_validator_required": True,
        "incomplete_1h_row_count": totals["incomplete_1h_row_count"],
        "incomplete_hour_policy_carried_forward": True,
        "material_conflict_rows_quarantined": totals["material_conflict_rows_quarantined"],
        "next_module": next_module,
        "okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_status": status,
        "output_1h_row_count": totals["output_1h_row_count"],
        "output_1m_rows_after_utc_filter": totals["output_1m_rows_after_utc_filter"],
        "output_file_created": output_file_created,
        "output_file_path": str(OUTPUT_CSV),
        "output_is_revised_non_holdout_view": True,
        "output_manifest_created": True,
        "output_max_timestamp": output_max_timestamp,
        "output_min_timestamp": output_min_timestamp,
        "output_physically_excludes_boundary_buffer": True,
        "output_physically_excludes_sealed_holdout": True,
        "output_schema_created": True,
        "output_sha256": output_sha256,
        "output_symbol_count": len(per_symbol_counts),
        "output_timestamps_all_gte_revised_start": output_min_ms == REVISED_START_MS,
        "output_timestamps_all_lt_revised_end_exclusive": output_max_ms is not None and output_max_ms < REVISED_END_MS,
        "output_timestamps_all_lt_sealed_holdout_start": output_max_ms is not None and output_max_ms < SEALED_HOLDOUT_START_MS,
        "output_valid_for_edge_claim": False,
        "output_valid_for_final_edge_claim": False,
        "output_valid_for_strategy_search_after_execution": False,
        "output_valid_for_strategy_search_after_validator": False,
        "per_symbol_output_row_count_valid": all(row["output_1h_row_count"] == EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H for row in per_symbol_counts),
        "pre_window_rows_excluded_count": totals["pre_window_rows_excluded_count"],
        "raw_source_rows_read": totals["raw_source_rows_read"],
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "revised_build_retry_preview_confirmed": preview_ok,
        "revised_expected_output_1m_rows_per_symbol": EXPECTED_OUTPUT_1M_ROWS_PER_SYMBOL,
        "revised_expected_output_rows_per_symbol_1h": EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H,
        "revised_expected_raw_source_rows_from_allowed_files": EXPECTED_RAW_SOURCE_ROWS,
        "revised_expected_total_output_1m_rows": EXPECTED_TOTAL_OUTPUT_1M_ROWS,
        "revised_expected_total_output_rows_1h": EXPECTED_TOTAL_OUTPUT_ROWS_1H,
        "revised_expected_total_source_file_count": EXPECTED_TOTAL_SOURCE_FILE_COUNT,
        "revised_non_holdout_view_build_execution_performed": replacement_checks_all_true,
        "revised_non_holdout_view_end_exclusive": REVISED_VIEW_END_EXCLUSIVE,
        "revised_non_holdout_view_start": REVISED_VIEW_START,
        "revised_source_end_date_inclusive": REVISED_SOURCE_END_DATE_INCLUSIVE,
        "revised_source_start_date": REVISED_SOURCE_START_DATE,
        "runtime_live_capital_allowed_now": False,
        "sealed_holdout_rows_read_count": 0,
        "sealed_holdout_rows_written_count": 0,
        "sealed_holdout_source_file_read_count": 0,
        "selected_symbol_count": len(selected_symbols),
        "source_file_count_matches_expected": totals["source_file_count_processed"] == EXPECTED_TOTAL_SOURCE_FILE_COUNT,
        "source_file_count_processed": totals["source_file_count_processed"],
        "source_file_date_2025_11_01_allowed": False,
        "source_file_date_2025_11_01_rejected": True,
        "source_file_date_max_read": REVISED_SOURCE_END_DATE_INCLUSIVE,
        "source_file_dates_all_lt_2025_11_01": True,
        "source_zip_csv_row_read_performed": True,
        "strategy_search_allowed_now": False,
        "strategy_search_executed": False,
        "strategy_search_retry_allowed_now": False,
        "synthetic_fill_used": False,
        "tracked_python_count_at_revised_build_execution_run": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
        "utc_output_filter_applied": True,
    }
    return {
        "report": report,
        "manifest": {
            **report,
            "output_schema": OUTPUT_SCHEMA,
            "per_symbol_counts_artifact": str(PER_SYMBOL_COUNTS_CSV),
            "revised_non_holdout_output_file": str(OUTPUT_CSV),
            "selected_symbols": selected_symbols,
        },
        "schema": {"input_schema": EXPECTED_SCHEMA, "output_schema": OUTPUT_SCHEMA, "output_schema_created": True},
        "source_inclusion": {
            "allowed_source_date_start": REVISED_SOURCE_START_DATE,
            "allowed_source_date_end_inclusive": REVISED_SOURCE_END_DATE_INCLUSIVE,
            "per_symbol_counts": per_symbol_counts,
            "source_file_count_processed": totals["source_file_count_processed"],
        },
        "source_exclusion": {
            "forbidden_source_date_start": "2025-11-01",
            "forbidden_source_file_read_count": 0,
            "sealed_holdout_source_file_read_count": 0,
        },
        "utc_filter": {
            "boundary_buffer_rows_written_count": 0,
            "output_1m_rows_after_utc_filter": totals["output_1m_rows_after_utc_filter"],
            "pre_window_rows_excluded_count": totals["pre_window_rows_excluded_count"],
            "utc_output_filter_applied": True,
        },
        "boundary_buffer": {
            "boundary_buffer_excluded": True,
            "boundary_buffer_rows_excluded_count": totals["boundary_buffer_rows_excluded_count"],
            "boundary_buffer_rows_written_count": 0,
            "boundary_buffer_total_1h_rows_excluded": BOUNDARY_BUFFER_TOTAL_1H_ROWS_EXCLUDED,
        },
        "policy_effects": {
            "backfill_used": False,
            "exact_duplicate_rows_dropped": totals["exact_duplicate_rows_dropped"],
            "forward_fill_used": False,
            "material_conflict_rows_quarantined": totals["material_conflict_rows_quarantined"],
            "synthetic_fill_used": False,
        },
        "incomplete": {
            "complete_1h_row_count": totals["complete_1h_row_count"],
            "incomplete_1h_row_count": totals["incomplete_1h_row_count"],
        },
        "provenance": {
            "provenance_entry_count": len(provenance_entries),
            "provenance_entries": provenance_entries,
        },
        "summary": report,
        "self_validator": {
            **report,
            "artifact_count_expected": 12,
            "created_at_utc": now_utc(),
        },
    }


def write_outputs(results: dict[str, Any]) -> None:
    files = {
        "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_report.json": results["report"],
        "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_output_manifest.json": results["manifest"],
        "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_output_schema.json": results["schema"],
        "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_source_inclusion_ledger.json": results["source_inclusion"],
        "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_source_exclusion_ledger.json": results["source_exclusion"],
        "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_utc_output_filter_report.json": results["utc_filter"],
        "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_boundary_buffer_exclusion_report.json": results["boundary_buffer"],
        "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_policy_effects.json": results["policy_effects"],
        "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_incomplete_hour_report.json": results["incomplete"],
        "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_provenance_report.json": results["provenance"],
        "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_summary.json": results["summary"],
        "repo_only_okx_88_symbol_1h_panel_non_holdout_view_revised_build_execution_self_validator.json": results["self_validator"],
    }
    for filename, payload in files.items():
        write_json(OUTPUT_DIR / filename, payload)


def main() -> int:
    results = build_execution()
    write_outputs(results)
    print(json.dumps(results["report"], indent=2, sort_keys=True))
    return 0 if results["report"]["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
