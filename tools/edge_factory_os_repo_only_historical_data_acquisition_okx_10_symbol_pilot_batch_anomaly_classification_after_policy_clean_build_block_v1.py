from __future__ import annotations

import ast
import csv
import hashlib
import io
import json
import subprocess
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "batch_anomaly_classification_after_policy_clean_build_block_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "batch_anomaly_classification_after_policy_clean_build_block_v1.py"
)
EXPECTED_HEAD = "4a26cdc"
PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_POLICY_CLEAN_BUILD_"
    "ANOMALY_RECORD_BATCH_CLASSIFICATION_READY_AUDIT_CONFIRMED"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BATCH_ANOMALY_"
    "CLASSIFIED_BATCH_POLICY_READY"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BATCH_ANOMALY_"
    "CLASSIFICATION_FAILED_REVIEW"
)
NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "batch_policy_after_batch_anomaly_classification_v1.py"
)
FAILED_NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "batch_anomaly_classification_blocked_record_v1.py"
)
AFTER_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BATCH_ANOMALY_CLASSIFIED_"
    "BATCH_POLICY_READY"
)

DATE_RANGE_START = "2023-07-01"
DATE_RANGE_END = "2026-05-18"
EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 1_053
EXPECTED_UNIQUE_OPEN_TIME_COUNT = 1_516_320
EXPECTED_HOUR_COUNT_PER_SYMBOL = 25_272
EXPECTED_MINUTE_MS = 60_000
EXPECTED_HOUR_MS = 3_600_000
DORMANT_REPO_ATTENTION_COUNT = 716

PILOT_SYMBOLS = [
    "BTC-USDT-SWAP",
    "ETH-USDT-SWAP",
    "SOL-USDT-SWAP",
    "XRP-USDT-SWAP",
    "DOGE-USDT-SWAP",
    "ADA-USDT-SWAP",
    "AVAX-USDT-SWAP",
    "LINK-USDT-SWAP",
    "LTC-USDT-SWAP",
    "DOT-USDT-SWAP",
]
EXPECTED_SCHEMA = [
    "instrument_name",
    "open",
    "high",
    "low",
    "close",
    "vol",
    "vol_ccy",
    "vol_quote",
    "open_time",
    "confirm",
]
OHLC_VOLUME_FIELDS = ["open", "high", "low", "close", "vol", "vol_ccy", "vol_quote"]
CONFIRM_FIELD = "confirm"
CANONICAL_FIELDS = EXPECTED_SCHEMA
CLASSIFICATIONS = {
    "CLEAN_NO_ANOMALY",
    "EXACT_DUPLICATE_ONLY",
    "MATERIAL_DUPLICATE_CONFLICT",
    "CONFIRM_ONLY_CONFLICT",
    "MISSING_MINUTE",
    "SCHEMA_MISMATCH",
    "SYMBOL_MISMATCH",
    "COVERAGE_GAP",
    "MIXED_ANOMALY",
    "UNKNOWN",
}

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
PRIOR_RECORD_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "policy_clean_build_execution_blocked_or_anomaly_record_after_sol_policy_v1"
)
DOWNLOAD_EXECUTION_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "download_execution_after_expansion_preview_approval_v1"
)
DOWNLOAD_VALIDATOR_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "download_execution_validator_after_execution_v1"
)

ARTIFACTS = {
    "prior_batch_route_summary": PRIOR_RECORD_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_batch_route_summary.json",
    "prior_batch_route_approval": PRIOR_RECORD_DIR
    / "historical_okx_10_symbol_pilot_batch_anomaly_classification_approval_record.json",
    "prior_partial_quarantine": PRIOR_RECORD_DIR
    / "historical_okx_10_symbol_pilot_partial_output_quarantine_record_after_sol_policy_block.json",
    "download_validator_summary": DOWNLOAD_VALIDATOR_DIR
    / "historical_okx_10_symbol_pilot_download_execution_validator_summary.json",
    "download_hash_validation_report": DOWNLOAD_VALIDATOR_DIR
    / "historical_okx_10_symbol_pilot_hash_validation_report.json",
    "download_zip_schema_validation_report": DOWNLOAD_VALIDATOR_DIR
    / "historical_okx_10_symbol_pilot_zip_schema_validation_report.json",
    "download_execution_summary": DOWNLOAD_EXECUTION_DIR
    / "historical_okx_10_symbol_pilot_download_execution_summary.json",
    "download_provenance_report": DOWNLOAD_EXECUTION_DIR
    / "historical_okx_10_symbol_pilot_download_provenance_report.json",
}

DANGEROUS_FLAGS = {
    "download_performed_now": False,
    "api_call_performed_now": False,
    "browse_performed_now": False,
    "url_fetch_performed_now": False,
    "data_build_performed": False,
    "aggregation_performed_now": False,
    "output_csv_created": False,
    "output_manifest_created": False,
    "rebuild_execution_performed_now": False,
    "dedupe_execution_performed_now": False,
    "quarantine_execution_performed_now": False,
    "row_selection_for_final_data_performed_now": False,
    "synthetic_fill_used": False,
    "forward_fill_used": False,
    "backfill_used": False,
    "research_backtest_edge_claim_made": False,
    "candidate_generation_performed_now": False,
    "full_universe_ready_claim_made": False,
    "broad_acquisition_ready_claim_made": False,
    "runtime_touched": False,
    "capital_changed": False,
    "live_or_real_orders": False,
    "schema_or_config_created": False,
    "generic_runner_approval_granted": False,
}


class Blocked(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_git(args: list[str]) -> str:
    completed = subprocess.run(
        [
            "git",
            "-c",
            "core.longpaths=true",
            "-c",
            f"safe.directory={REPO_ROOT}",
            "-C",
            str(REPO_ROOT),
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def current_tool_rel() -> str:
    return APPROVED_TOOL.relative_to(REPO_ROOT).as_posix()


def repo_has_only_this_tool_change() -> bool:
    status = [line for line in run_git(["status", "--short"]).splitlines() if line.strip()]
    if not status:
        return True
    rel = current_tool_rel()
    return all(line[3:].replace("\\", "/") == rel for line in status)


def tracked_python_files_including_current() -> list[str]:
    files = sorted(path for path in run_git(["ls-files"]).splitlines() if path.endswith(".py"))
    rel = current_tool_rel()
    if APPROVED_TOOL.exists() and rel not in files:
        files.append(rel)
    return sorted(files)


def tracked_python_validation() -> dict[str, Any]:
    syntax_errors: list[dict[str, str]] = []
    bom_errors: list[str] = []
    files = tracked_python_files_including_current()
    for rel in files:
        data = (REPO_ROOT / rel).read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
        try:
            ast.parse(data.decode("utf-8"), filename=rel)
        except Exception as exc:
            syntax_errors.append({"path": rel, "error": repr(exc)})
    return {
        "tracked_python_count": len(files),
        "syntax_error_count": len(syntax_errors),
        "bom_error_count": len(bom_errors),
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
    }


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Blocked(message)


def load_json(path: Path, label: str, exists: dict[str, bool], valid: dict[str, bool]) -> dict[str, Any]:
    exists[label] = path.exists()
    require(path.exists(), f"missing artifact {label}: {path}")
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        valid[label] = False
        raise Blocked(f"invalid JSON artifact {label}: {exc}") from exc
    valid[label] = True
    require(isinstance(loaded, dict), f"artifact {label} is not a JSON object")
    return loaded


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_start_end_ms() -> tuple[int, int]:
    start = datetime.fromisoformat(DATE_RANGE_START).replace(tzinfo=timezone.utc)
    end = datetime.fromisoformat(DATE_RANGE_END).replace(tzinfo=timezone.utc)
    start_ms = int(start.timestamp() * 1000)
    end_ms = int(end.timestamp() * 1000) + (24 * 60 * 60 * 1000) - EXPECTED_MINUTE_MS
    return start_ms, end_ms


def safe_zip_member_name(symbol: str, date: str, zf: zipfile.ZipFile) -> str:
    expected_inner = f"{symbol}-candlesticks-{date}.csv"
    names = zf.namelist()
    require(expected_inner in names, f"missing expected CSV member {expected_inner}")
    require(all(PurePosixPath(name).name == name for name in names), f"zip path traversal risk in {symbol} {date}")
    return expected_inner


def row_projection(row: dict[str, str]) -> dict[str, str]:
    return {field: row.get(field, "") for field in CANONICAL_FIELDS}


def classify_duplicate_group(rows: list[dict[str, str]]) -> str:
    first = rows[0]
    if all(all(row.get(field, "") == first.get(field, "") for field in CANONICAL_FIELDS) for row in rows[1:]):
        return "EXACT_DUPLICATE"
    material_diff = any(
        any(row.get(field, "") != first.get(field, "") for field in OHLC_VOLUME_FIELDS)
        for row in rows[1:]
    )
    if material_diff:
        return "MATERIAL_DUPLICATE_CONFLICT"
    non_confirm_fields = [field for field in CANONICAL_FIELDS if field != CONFIRM_FIELD]
    only_confirm_diff = all(
        all(row.get(field, "") == first.get(field, "") for field in non_confirm_fields)
        for row in rows[1:]
    ) and any(row.get(CONFIRM_FIELD, "") != first.get(CONFIRM_FIELD, "") for row in rows[1:])
    if only_confirm_diff:
        return "CONFIRM_ONLY_CONFLICT"
    return "UNKNOWN_DUPLICATE"


def missing_minutes_and_hours(open_times: set[int]) -> tuple[int, int]:
    start_ms, end_ms = expected_start_end_ms()
    in_range = sorted(value for value in open_times if start_ms <= value <= end_ms)
    if not in_range:
        return EXPECTED_UNIQUE_OPEN_TIME_COUNT, EXPECTED_HOUR_COUNT_PER_SYMBOL
    missing = 0
    affected_hours: set[int] = set()
    first = in_range[0]
    if first > start_ms:
        count = (first - start_ms) // EXPECTED_MINUTE_MS
        missing += count
        for value in range(start_ms, first, EXPECTED_MINUTE_MS):
            affected_hours.add((value // EXPECTED_HOUR_MS) * EXPECTED_HOUR_MS)
    previous = first
    for value in in_range[1:]:
        gap = (value - previous) // EXPECTED_MINUTE_MS - 1
        if gap > 0:
            missing += gap
            for missing_value in range(previous + EXPECTED_MINUTE_MS, value, EXPECTED_MINUTE_MS):
                affected_hours.add((missing_value // EXPECTED_HOUR_MS) * EXPECTED_HOUR_MS)
        previous = value
    if previous < end_ms:
        count = (end_ms - previous) // EXPECTED_MINUTE_MS
        missing += count
        for value in range(previous + EXPECTED_MINUTE_MS, end_ms + EXPECTED_MINUTE_MS, EXPECTED_MINUTE_MS):
            affected_hours.add((value // EXPECTED_HOUR_MS) * EXPECTED_HOUR_MS)
    return missing, len(affected_hours)


def symbol_classification(row: dict[str, Any]) -> str:
    flags = {
        "schema": row["schema_mismatch_count"] > 0,
        "symbol": row["symbol_mismatch_count"] > 0,
        "coverage": row["coverage_gap_count"] > 0,
        "missing": row["missing_minute_count"] > 0,
        "exact": row["exact_duplicate_group_count"] > 0,
        "material": row["material_conflict_group_count"] > 0,
        "confirm": row["confirm_only_conflict_group_count"] > 0,
        "unknown": row["unknown_duplicate_group_count"] > 0,
    }
    if flags["schema"]:
        return "SCHEMA_MISMATCH"
    if flags["symbol"]:
        return "SYMBOL_MISMATCH"
    if flags["unknown"]:
        return "UNKNOWN"
    active = [name for name, value in flags.items() if value]
    if not active:
        return "CLEAN_NO_ANOMALY"
    if active == ["exact"]:
        return "EXACT_DUPLICATE_ONLY"
    if active == ["material"]:
        return "MATERIAL_DUPLICATE_CONFLICT"
    if active == ["confirm"]:
        return "CONFIRM_ONLY_CONFLICT"
    if active == ["missing"]:
        return "MISSING_MINUTE"
    if active == ["coverage"]:
        return "COVERAGE_GAP"
    return "MIXED_ANOMALY"


def scan_symbol(symbol: str, hash_items: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    require(len(hash_items) == EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL, f"{symbol} file count mismatch")
    raw_row_count = 0
    schema_mismatch_count = 0
    symbol_mismatch_count = 0
    out_of_range_count = 0
    seen_open_times: set[int] = set()
    first_rows: dict[int, dict[str, str]] = {}
    duplicate_groups: dict[int, list[dict[str, str]]] = {}
    hash_mismatch_count = 0
    zip_open_count = 0
    start_ms, end_ms = expected_start_end_ms()

    for item in sorted(hash_items, key=lambda value: str(value["date"])):
        zip_path = Path(item["local_zip_path"])
        require(zip_path.exists(), f"missing ZIP for {symbol}: {zip_path}")
        observed_sha = sha256_file(zip_path)
        if observed_sha != item.get("recorded_sha256") or observed_sha != item.get("recomputed_sha256"):
            hash_mismatch_count += 1
            continue
        with zipfile.ZipFile(zip_path) as zf:
            member_name = safe_zip_member_name(symbol, str(item["date"]), zf)
            zip_open_count += 1
            with zf.open(member_name, "r") as raw_handle:
                text_handle = io.TextIOWrapper(raw_handle, encoding="utf-8", newline="")
                reader = csv.DictReader(text_handle)
                if reader.fieldnames != EXPECTED_SCHEMA:
                    schema_mismatch_count += 1
                    continue
                for row in reader:
                    raw_row_count += 1
                    if row.get("instrument_name") != symbol:
                        symbol_mismatch_count += 1
                    try:
                        open_time = int(row.get("open_time", ""))
                    except ValueError:
                        schema_mismatch_count += 1
                        continue
                    if open_time < start_ms or open_time > end_ms:
                        out_of_range_count += 1
                    projection = row_projection(row)
                    if open_time in seen_open_times:
                        if open_time not in duplicate_groups:
                            duplicate_groups[open_time] = [first_rows[open_time]]
                        duplicate_groups[open_time].append(projection)
                    else:
                        seen_open_times.add(open_time)
                        first_rows[open_time] = projection
    require(hash_mismatch_count == 0, f"{symbol} SHA256 mismatch count {hash_mismatch_count}")
    require(zip_open_count == EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL, f"{symbol} ZIP open count mismatch")

    missing_minute_count, missing_hour_count = missing_minutes_and_hours(seen_open_times)
    duplicate_group_rows: list[dict[str, Any]] = []
    material_samples: list[dict[str, Any]] = []
    exact_group_count = 0
    exact_extra_rows = 0
    material_group_count = 0
    material_rows = 0
    confirm_only_group_count = 0
    unknown_group_count = 0
    material_affected_hours: set[int] = set()
    for open_time, rows in sorted(duplicate_groups.items()):
        duplicate_type = classify_duplicate_group(rows)
        extra_rows = len(rows) - 1
        if duplicate_type == "EXACT_DUPLICATE":
            exact_group_count += 1
            exact_extra_rows += extra_rows
        elif duplicate_type == "MATERIAL_DUPLICATE_CONFLICT":
            material_group_count += 1
            material_rows += len(rows)
            material_affected_hours.add((open_time // EXPECTED_HOUR_MS) * EXPECTED_HOUR_MS)
            if len(material_samples) < 25:
                material_samples.append(
                    {
                        "symbol": symbol,
                        "open_time": open_time,
                        "duplicate_type": duplicate_type,
                        "row_count": len(rows),
                        "raw_rows": rows,
                    }
                )
        elif duplicate_type == "CONFIRM_ONLY_CONFLICT":
            confirm_only_group_count += 1
        else:
            unknown_group_count += 1
        if len(duplicate_group_rows) < 250:
            duplicate_group_rows.append(
                {
                    "symbol": symbol,
                    "open_time": open_time,
                    "duplicate_type": duplicate_type,
                    "row_count": len(rows),
                    "extra_row_count": extra_rows,
                    "raw_rows_sample": rows[:4],
                }
            )

    duplicate_group_count = len(duplicate_groups)
    duplicate_extra_row_count = raw_row_count - len(seen_open_times)
    affected_hour_count = len(material_affected_hours) + missing_hour_count
    row = {
        "symbol": symbol,
        "raw_row_count": raw_row_count,
        "unique_open_time_count": len(seen_open_times),
        "expected_unique_open_time_count": EXPECTED_UNIQUE_OPEN_TIME_COUNT,
        "duplicate_group_count": duplicate_group_count,
        "duplicate_extra_row_count": duplicate_extra_row_count,
        "exact_duplicate_group_count": exact_group_count,
        "exact_duplicate_extra_rows": exact_extra_rows,
        "material_conflict_group_count": material_group_count,
        "material_conflict_rows": material_rows,
        "confirm_only_conflict_group_count": confirm_only_group_count,
        "unknown_duplicate_group_count": unknown_group_count,
        "missing_minute_count": missing_minute_count,
        "affected_hour_count": affected_hour_count,
        "schema_mismatch_count": schema_mismatch_count,
        "symbol_mismatch_count": symbol_mismatch_count,
        "coverage_gap_count": out_of_range_count,
    }
    row["symbol_classification"] = symbol_classification(row)
    missing_report = {
        "symbol": symbol,
        "missing_minute_count": missing_minute_count,
        "affected_hour_count": affected_hour_count,
        "material_conflict_affected_hour_count": len(material_affected_hours),
        "coverage_gap_count": out_of_range_count,
    }
    duplicate_summary = {
        "symbol": symbol,
        "duplicate_group_count": duplicate_group_count,
        "duplicate_extra_row_count": duplicate_extra_row_count,
        "exact_duplicate_group_count": exact_group_count,
        "exact_duplicate_extra_rows": exact_extra_rows,
        "material_conflict_group_count": material_group_count,
        "material_conflict_rows": material_rows,
        "confirm_only_conflict_group_count": confirm_only_group_count,
        "unknown_duplicate_group_count": unknown_group_count,
        "duplicate_group_samples": duplicate_group_rows,
    }
    return row, duplicate_summary, material_samples, [missing_report]


def validate_inputs(artifacts: dict[str, dict[str, Any]], py: dict[str, Any]) -> None:
    require(run_git(["rev-parse", "--short", "HEAD"]) == EXPECTED_HEAD, "HEAD mismatch")
    require(current_tool_rel() == CURRENT_TOOL_REL, "target path guard mismatch")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved batch classifier module")
    require(py["syntax_error_count"] == 0, "tracked Python syntax errors present")
    require(py["bom_error_count"] == 0, "tracked Python BOM errors present")
    prior = artifacts["prior_batch_route_summary"]
    approval = artifacts["prior_batch_route_approval"]
    quarantine = artifacts["prior_partial_quarantine"]
    require(
        prior.get("historical_data_acquisition_okx_10_symbol_pilot_policy_clean_build_anomaly_record_status")
        == PREVIOUS_STATUS,
        "previous anomaly record status mismatch",
    )
    require(prior.get("one_symbol_policy_loop_should_continue") is False, "one-symbol loop should not continue")
    require(prior.get("one_symbol_policy_loop_terminated") is True, "one-symbol loop not terminated")
    require(prior.get("batch_anomaly_classification_required") is True, "batch classification not required")
    require(prior.get("partial_output_trusted") is False, "partial output trusted")
    require(prior.get("partial_output_quarantined") is True, "partial output not quarantined")
    require(prior.get("partial_output_valid_for_any_downstream_use") is False, "partial output downstream use allowed")
    require(prior.get("active_p0_blocker_count") == 1, "previous P0 mismatch")
    require(prior.get("active_p1_attention_count", 0) >= 505, "previous P1 attention mismatch")
    require(prior.get("dormant_repo_attention_count") == DORMANT_REPO_ATTENTION_COUNT, "dormant attention mismatch")
    require(prior.get("next_module") == REQUESTED_MODULE, "current next_module mismatch")
    require(approval.get("approval_grants_future_batch_anomaly_classification_next") is True, "future batch approval missing")
    require(approval.get("approval_grants_rebuild_now") is False, "rebuild approval unexpectedly granted")
    require(quarantine.get("partial_output_quarantined") is True, "quarantine artifact mismatch")

    validator = artifacts["download_validator_summary"]
    hash_report = artifacts["download_hash_validation_report"]
    provenance = artifacts["download_provenance_report"]
    require(validator.get("download_execution_validated") is True, "download validator not validated")
    require(validator.get("all_hashes_match_recorded") is True, "validator hash mismatch")
    require(validator.get("all_zip_open_success") is True, "validator ZIP open mismatch")
    require(validator.get("all_expected_inner_csv_present") is True, "validator inner CSV mismatch")
    require(validator.get("pilot_symbols") == PILOT_SYMBOLS, "validator symbols mismatch")
    require(hash_report.get("all_hashes_match_recorded") is True, "hash report mismatch")
    require(len(hash_report.get("hashes", [])) == EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL * len(PILOT_SYMBOLS), "hash item count mismatch")
    require(isinstance(provenance.get("download_results"), list), "provenance download results missing")


def build_hash_items_by_symbol(hash_report: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    by_symbol: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in hash_report.get("hashes", []):
        symbol = item.get("symbol")
        if symbol in PILOT_SYMBOLS:
            by_symbol[symbol].append(item)
    for symbol in PILOT_SYMBOLS:
        require(symbol in by_symbol, f"missing hash items for {symbol}")
    return by_symbol


def build_outputs(
    generated_at: str,
    artifacts: dict[str, dict[str, Any]],
    exists: dict[str, bool],
    valid: dict[str, bool],
    py: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    by_symbol = build_hash_items_by_symbol(artifacts["download_hash_validation_report"])
    per_symbol_rows: list[dict[str, Any]] = []
    duplicate_summaries: list[dict[str, Any]] = []
    material_samples: list[dict[str, Any]] = []
    missing_reports: list[dict[str, Any]] = []
    for symbol in PILOT_SYMBOLS:
        row, duplicate_summary, symbol_material_samples, symbol_missing_reports = scan_symbol(symbol, by_symbol[symbol])
        per_symbol_rows.append(row)
        duplicate_summaries.append(duplicate_summary)
        material_samples.extend(symbol_material_samples)
        missing_reports.extend(symbol_missing_reports)

    totals = {
        "total_raw_rows_scanned": sum(row["raw_row_count"] for row in per_symbol_rows),
        "total_unique_open_time_count": sum(row["unique_open_time_count"] for row in per_symbol_rows),
        "total_duplicate_group_count": sum(row["duplicate_group_count"] for row in per_symbol_rows),
        "total_duplicate_extra_row_count": sum(row["duplicate_extra_row_count"] for row in per_symbol_rows),
        "total_exact_duplicate_group_count": sum(row["exact_duplicate_group_count"] for row in per_symbol_rows),
        "total_exact_duplicate_extra_rows": sum(row["exact_duplicate_extra_rows"] for row in per_symbol_rows),
        "total_material_conflict_group_count": sum(row["material_conflict_group_count"] for row in per_symbol_rows),
        "total_material_conflict_rows": sum(row["material_conflict_rows"] for row in per_symbol_rows),
        "total_confirm_only_conflict_group_count": sum(row["confirm_only_conflict_group_count"] for row in per_symbol_rows),
        "total_unknown_duplicate_group_count": sum(row["unknown_duplicate_group_count"] for row in per_symbol_rows),
        "total_missing_minute_count": sum(row["missing_minute_count"] for row in per_symbol_rows),
    }
    symbols_with_clean_no_anomaly = [row["symbol"] for row in per_symbol_rows if row["symbol_classification"] == "CLEAN_NO_ANOMALY"]
    symbols_with_exact_duplicate_only = [
        row["symbol"] for row in per_symbol_rows if row["symbol_classification"] == "EXACT_DUPLICATE_ONLY"
    ]
    symbols_with_material_duplicate_conflict = [
        row["symbol"] for row in per_symbol_rows if row["material_conflict_group_count"] > 0
    ]
    symbols_with_missing_minutes = [row["symbol"] for row in per_symbol_rows if row["missing_minute_count"] > 0]
    symbols_with_schema_mismatch = [row["symbol"] for row in per_symbol_rows if row["schema_mismatch_count"] > 0]
    symbols_with_symbol_mismatch = [row["symbol"] for row in per_symbol_rows if row["symbol_mismatch_count"] > 0]
    symbols_with_unknown = [row["symbol"] for row in per_symbol_rows if row["unknown_duplicate_group_count"] > 0]
    symbols_with_confirm_only = [row["symbol"] for row in per_symbol_rows if row["confirm_only_conflict_group_count"] > 0]
    symbols_with_coverage_gap = [row["symbol"] for row in per_symbol_rows if row["coverage_gap_count"] > 0]

    all_classifiable = not (symbols_with_unknown or symbols_with_schema_mismatch or symbols_with_symbol_mismatch)
    active_p0 = 0 if all_classifiable else 1
    active_p1 = max(artifacts["prior_batch_route_summary"].get("active_p1_attention_count", 0), 505)
    total_incomplete_hours_after_policy = len(
        {
            (row["symbol"], report["symbol"], index)
            for index, report in enumerate(missing_reports)
            for row in per_symbol_rows
            if row["symbol"] == report["symbol"] and report["affected_hour_count"] > 0
        }
    )
    total_incomplete_hours_after_policy = sum(report["affected_hour_count"] for report in missing_reports)
    total_expected_clean_source_rows_after_policy = (
        totals["total_raw_rows_scanned"]
        - totals["total_exact_duplicate_extra_rows"]
        - totals["total_material_conflict_rows"]
    )
    total_expected_complete_1h_rows_after_policy = (
        EXPECTED_HOUR_COUNT_PER_SYMBOL * len(PILOT_SYMBOLS) - total_incomplete_hours_after_policy
    )

    shared = {
        "batch_classification_performed": True,
        "pilot_symbol_count": len(PILOT_SYMBOLS),
        "symbols_classified_count": len(per_symbol_rows),
        "date_range_start": DATE_RANGE_START,
        "date_range_end": DATE_RANGE_END,
        "expected_unique_open_time_count_per_symbol": EXPECTED_UNIQUE_OPEN_TIME_COUNT,
        **totals,
        "symbols_with_clean_no_anomaly": symbols_with_clean_no_anomaly,
        "symbols_with_exact_duplicate_only": symbols_with_exact_duplicate_only,
        "symbols_with_material_duplicate_conflict": symbols_with_material_duplicate_conflict,
        "symbols_with_missing_minutes": symbols_with_missing_minutes,
        "symbols_with_schema_mismatch": symbols_with_schema_mismatch,
        "symbols_with_symbol_mismatch": symbols_with_symbol_mismatch,
        "symbols_with_unknown": symbols_with_unknown,
        "one_symbol_policy_loop_terminated": True,
        "next_route_is_batch_policy": True,
        "approval_grants_batch_policy_now": False,
        "approval_grants_future_batch_policy_next": True,
        "approval_grants_rebuild_now": False,
        "approval_grants_download_now": False,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "output_csv_created": False,
        "output_manifest_created": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "active_p0_blocker_count": active_p0,
        "active_p1_attention_count": active_p1,
        "dormant_repo_attention_count": DORMANT_REPO_ATTENTION_COUNT,
        "current_evidence_chain_quality_after_classification": AFTER_QUALITY,
        "next_module": NEXT_MODULE if all_classifiable else FAILED_NEXT_MODULE,
    }
    batch_policy_preview = {
        "batch_policy_preview_created": True,
        "preview_only": True,
        "general_exact_duplicate_policy": "DROP_ONLY_EXACT_DUPLICATE_EXTRA_ROWS_KEEP_ONE_CANONICAL_ROW",
        "general_material_conflict_policy": "QUARANTINE_ALL_ROWS_IN_MATERIAL_CONFLICT_OPEN_TIME_GROUP",
        "general_confirm_only_policy": "DO_NOT_RESOLVE_NOW_UNLESS_EXPLICIT_BATCH_POLICY_SAYS_OTHERWISE",
        "general_missing_minute_policy": "NO_SYNTHETIC_FILL_AFFECTED_HOUR_INCOMPLETE_OR_SYMBOL_BLOCKED_BY_SEVERITY",
        "general_coverage_gap_policy": "CLASSIFY_AS_BATCH_POLICY_ATTENTION_NO_FILL_NO_SYMBOL_SPECIFIC_LOOP",
        "general_schema_symbol_mismatch_policy": "FAIL_CLOSED_BLOCK_AFFECTED_SYMBOL",
        "batch_exact_duplicate_symbol_count": sum(1 for row in per_symbol_rows if row["exact_duplicate_group_count"] > 0),
        "batch_material_conflict_symbol_count": len(symbols_with_material_duplicate_conflict),
        "batch_clean_symbol_count": len(symbols_with_clean_no_anomaly),
        "batch_missing_minute_symbol_count": len(symbols_with_missing_minutes),
        "batch_schema_mismatch_symbol_count": len(symbols_with_schema_mismatch),
        "batch_symbol_mismatch_symbol_count": len(symbols_with_symbol_mismatch),
        "batch_unknown_symbol_count": len(symbols_with_unknown),
        "batch_confirm_only_symbol_count": len(symbols_with_confirm_only),
        "total_exact_duplicate_extra_rows_to_drop": totals["total_exact_duplicate_extra_rows"],
        "total_material_conflict_rows_to_quarantine": totals["total_material_conflict_rows"],
        "total_material_conflict_unique_open_time_count": totals["total_material_conflict_group_count"],
        "total_expected_clean_source_rows_after_policy": total_expected_clean_source_rows_after_policy,
        "total_expected_complete_1h_rows_after_policy": total_expected_complete_1h_rows_after_policy,
        "total_expected_incomplete_1h_rows_after_policy": total_incomplete_hours_after_policy,
        "symbols_safe_for_batch_policy_clean_build": [row["symbol"] for row in per_symbol_rows if row["symbol_classification"] != "UNKNOWN"],
        "symbols_blocked_pending_manual_review": symbols_with_unknown,
        "symbols_with_coverage_gap_attention": symbols_with_coverage_gap,
        "no_research_backtest_edge_readiness": True,
        **shared,
    }
    approval_record = {
        "batch_policy_approval_record_created": True,
        "approval_grants_batch_policy_now": False,
        "approval_grants_future_batch_policy_next": all_classifiable,
        "approval_grants_rebuild_now": False,
        "approval_grants_download_now": False,
        "approval_grants_dedupe_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "next_module": NEXT_MODULE if all_classifiable else FAILED_NEXT_MODULE,
        **shared,
    }
    self_validator = {
        "batch_anomaly_classification_self_validator_created": True,
        "required_artifacts_exist": all(exists.values()),
        "required_artifacts_valid_json": all(valid.values()),
        "all_10_symbols_classified": len(per_symbol_rows) == len(PILOT_SYMBOLS),
        "all_symbol_classifications_known": all(row["symbol_classification"] in CLASSIFICATIONS for row in per_symbol_rows),
        "sha256_reconfirmed_before_csv_reads": True,
        "batch_policy_preview_created": batch_policy_preview["batch_policy_preview_created"],
        "batch_policy_approval_record_created": approval_record["batch_policy_approval_record_created"],
        "next_route_is_batch_policy": shared["next_route_is_batch_policy"],
        "no_per_symbol_next_module": not any("_sol_" in shared["next_module"].lower() or "_eth_" in shared["next_module"].lower() for _ in [0]),
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        "tracked_python_syntax_clean": py["syntax_error_count"] == 0,
        "tracked_python_bom_clean": py["bom_error_count"] == 0,
        "no_build_aggregation_output": shared["data_build_performed"] is False
        and shared["aggregation_performed_now"] is False
        and shared["output_csv_created"] is False,
    }
    replacement_checks = {
        "batch_classification_performed": shared["batch_classification_performed"],
        "all_symbols_classified": shared["symbols_classified_count"] == 10,
        "expected_date_range": shared["date_range_start"] == DATE_RANGE_START and shared["date_range_end"] == DATE_RANGE_END,
        "batch_policy_preview_created": batch_policy_preview["batch_policy_preview_created"],
        "batch_policy_approval_record_created": approval_record["batch_policy_approval_record_created"],
        "one_symbol_policy_loop_terminated": shared["one_symbol_policy_loop_terminated"],
        "next_route_is_batch_policy": shared["next_route_is_batch_policy"],
        "future_batch_policy_next": approval_record["approval_grants_future_batch_policy_next"] is True,
        "no_download_build_aggregation_output_now": shared["data_download_performed"] is False
        and shared["data_build_performed"] is False
        and shared["aggregation_performed_now"] is False
        and shared["output_csv_created"] is False
        and shared["output_manifest_created"] is False,
        "no_api_browse": shared["okx_api_call_performed"] is False and shared["okx_browse_performed"] is False,
        "no_research_backtest_edge_claim": shared["output_valid_for_research_backtest"] is False
        and shared["output_valid_for_edge_claim"] is False
        and shared["safe_for_full_universe_acquisition"] is False
        and shared["broad_acquisition_ready"] is False,
        "all_anomalies_classifiable": all_classifiable,
        "self_validator_passed": all(value is True for value in self_validator.values() if isinstance(value, bool)),
    }
    replacement_checks_all_true = all(replacement_checks.values())
    summary = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "historical_data_acquisition_okx_10_symbol_pilot_batch_anomaly_classification_status": PASS_STATUS
        if replacement_checks_all_true
        else BLOCKED_STATUS,
        "batch_policy_preview_created": batch_policy_preview["batch_policy_preview_created"],
        "batch_policy_approval_record_created": approval_record["batch_policy_approval_record_created"],
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": True,
        "tracked_python_count_at_classification_run": py["tracked_python_count"],
        **shared,
    }
    report = {
        "summary": summary,
        "per_symbol_anomaly_table": per_symbol_rows,
        "duplicate_group_summary": duplicate_summaries,
        "material_conflict_sample_count": len(material_samples),
        "missing_minute_report": missing_reports,
    }
    payloads = {
        "historical_okx_10_symbol_pilot_batch_anomaly_classification_report.json": report,
        "historical_okx_10_symbol_pilot_batch_per_symbol_anomaly_table.json": {"symbols": per_symbol_rows},
        "historical_okx_10_symbol_pilot_batch_duplicate_group_summary.json": {"symbols": duplicate_summaries},
        "historical_okx_10_symbol_pilot_batch_material_conflict_sample_report.json": {"material_conflict_samples": material_samples},
        "historical_okx_10_symbol_pilot_batch_missing_minute_report.json": {"symbols": missing_reports},
        "historical_okx_10_symbol_pilot_batch_policy_preview.json": batch_policy_preview,
        "historical_okx_10_symbol_pilot_batch_policy_approval_record.json": approval_record,
        "historical_okx_10_symbol_pilot_batch_anomaly_classification_self_validator.json": self_validator,
        "historical_okx_10_symbol_pilot_batch_anomaly_classification_summary.json": summary,
        f"{MODULE_NAME}_latest.json": summary,
    }
    return summary, payloads


def validate_written(summary: dict[str, Any]) -> dict[str, bool]:
    required = [
        "historical_okx_10_symbol_pilot_batch_anomaly_classification_report.json",
        "historical_okx_10_symbol_pilot_batch_per_symbol_anomaly_table.json",
        "historical_okx_10_symbol_pilot_batch_duplicate_group_summary.json",
        "historical_okx_10_symbol_pilot_batch_material_conflict_sample_report.json",
        "historical_okx_10_symbol_pilot_batch_missing_minute_report.json",
        "historical_okx_10_symbol_pilot_batch_policy_preview.json",
        "historical_okx_10_symbol_pilot_batch_policy_approval_record.json",
        "historical_okx_10_symbol_pilot_batch_anomaly_classification_self_validator.json",
        "historical_okx_10_symbol_pilot_batch_anomaly_classification_summary.json",
    ]
    loaded = {}
    for filename in required:
        path = OUTPUT_DIR / filename
        require(path.exists(), f"missing output artifact {filename}")
        loaded[filename] = json.loads(path.read_text(encoding="utf-8"))
    table = loaded["historical_okx_10_symbol_pilot_batch_per_symbol_anomaly_table.json"]["symbols"]
    approval = loaded["historical_okx_10_symbol_pilot_batch_policy_approval_record.json"]
    checks = {
        "required_artifacts_exist": True,
        "all_10_symbols_classified": len(table) == 10,
        "batch_policy_preview_exists": loaded["historical_okx_10_symbol_pilot_batch_policy_preview.json"].get(
            "batch_policy_preview_created"
        )
        is True,
        "batch_policy_approval_exists": approval.get("batch_policy_approval_record_created") is True,
        "future_batch_policy_next": approval.get("approval_grants_future_batch_policy_next") is True,
        "no_build_aggregation_output": summary.get("data_build_performed") is False
        and summary.get("aggregation_performed_now") is False
        and summary.get("output_csv_created") is False,
        "next_module_batch_policy": summary.get("next_module") == NEXT_MODULE,
        "replacement_checks_all_true": summary.get("replacement_checks_all_true") is True,
    }
    checks["written_artifacts_valid"] = all(checks.values())
    return checks


def main() -> None:
    generated_at = utc_now()
    exists: dict[str, bool] = {}
    valid: dict[str, bool] = {}
    py = tracked_python_validation()
    artifacts = {label: load_json(path, label, exists, valid) for label, path in ARTIFACTS.items()}
    validate_inputs(artifacts, py)
    summary, payloads = build_outputs(generated_at, artifacts, exists, valid, py)
    for filename, payload in payloads.items():
        write_json(OUTPUT_DIR / filename, payload)
    require(summary["replacement_checks_all_true"] is True, "replacement checks failed")
    written = validate_written(summary)
    require(written["written_artifacts_valid"] is True, f"written artifact validation failed: {written}")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Blocked as exc:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        payload = {
            "module_name": MODULE_NAME,
            "generated_at_utc": utc_now(),
            "historical_data_acquisition_okx_10_symbol_pilot_batch_anomaly_classification_status": BLOCKED_STATUS,
            "batch_classification_performed": False,
            "pilot_symbol_count": len(PILOT_SYMBOLS),
            "symbols_classified_count": 0,
            "date_range_start": DATE_RANGE_START,
            "date_range_end": DATE_RANGE_END,
            "expected_unique_open_time_count_per_symbol": EXPECTED_UNIQUE_OPEN_TIME_COUNT,
            "batch_policy_preview_created": False,
            "batch_policy_approval_record_created": False,
            "one_symbol_policy_loop_terminated": True,
            "next_route_is_batch_policy": False,
            "approval_grants_future_batch_policy_next": False,
            "data_download_performed": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "output_csv_created": False,
            "okx_api_call_performed": False,
            "okx_browse_performed": False,
            "active_p0_blocker_count": 1,
            "active_p1_attention_count": 505,
            "dormant_repo_attention_count": DORMANT_REPO_ATTENTION_COUNT,
            "current_evidence_chain_quality_after_classification": PREVIOUS_STATUS,
            "next_module": FAILED_NEXT_MODULE,
            "replacement_checks_all_true": False,
            "blocked_reason": str(exc),
        }
        write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", payload)
        print(json.dumps(payload, indent=2, sort_keys=True))
        raise SystemExit(1)
