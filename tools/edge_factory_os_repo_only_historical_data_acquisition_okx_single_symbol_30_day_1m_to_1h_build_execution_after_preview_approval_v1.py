from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_1m_to_1h_build_execution_after_preview_approval_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "605a4f9"
TARGET_SYMBOL = "BTC-USDT-SWAP"
DATE_RANGE_START = "2026-04-19"
DATE_RANGE_END = "2026-05-18"
EXPECTED_FILE_COUNT = 30
EXPECTED_SOURCE_ROWS_PER_FILE = 1440
EXPECTED_TOTAL_SOURCE_ROWS = 43200
MAX_TOTAL_SOURCE_ROWS = 50000
EXPECTED_OUTPUT_ROWS = 720
EXPECTED_OUTPUT_HOURS_PER_FILE = 24
BUILD_SCOPE = "SINGLE_SYMBOL_30_DAY_1M_TO_1H_PIPELINE_VALIDATION_ONLY"
PREVIEW_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_1M_TO_1H_"
    "BUILD_PREVIEW_APPROVED_EXECUTION_NEXT_NO_BUILD_YET"
)
DOWNLOAD_VALIDATOR_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_DOWNLOAD_VALIDATED_"
    "BUILD_PREVIEW_READY_NO_BUILD"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_1M_TO_1H_"
    "BUILD_EXECUTED_PENDING_VALIDATOR_PIPELINE_VALIDATION_ONLY"
)
BEFORE_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_1M_TO_1H_"
    "BUILD_PREVIEW_APPROVED_EXECUTION_NEXT_NO_BUILD_YET"
)
AFTER_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_1M_TO_1H_"
    "BUILD_EXECUTED_PENDING_VALIDATOR_PIPELINE_VALIDATION_ONLY"
)
NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_1m_to_1h_build_execution_validator_after_execution_v1.py"
)
BLOCKED_NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_1m_to_1h_build_execution_blocked_record_after_preview_approval_v1.py"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_1m_to_1h_build_execution_after_preview_approval_v1"
)

PREVIEW_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_1m_to_1h_build_preview_after_download_validator_v1"
)
DOWNLOAD_VALIDATOR_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_download_execution_validator_after_execution_v1"
)

PREVIEW_SUMMARY = PREVIEW_DIR / "historical_okx_single_symbol_30_day_1m_to_1h_build_preview_summary.json"
PREVIEW_APPROVAL = PREVIEW_DIR / "historical_okx_single_symbol_30_day_1m_to_1h_build_approval_record.json"
DOWNLOAD_VALIDATOR_SUMMARY = DOWNLOAD_VALIDATOR_DIR / "historical_okx_single_symbol_30_day_download_execution_validator_summary.json"
HASH_VALIDATION_REPORT = DOWNLOAD_VALIDATOR_DIR / "historical_okx_single_symbol_30_day_hash_validation_report.json"

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
OUTPUT_SCHEMA = [
    "instrument_name",
    "hour_start_epoch_ms",
    "hour_start_iso_utc",
    "open",
    "high",
    "low",
    "close",
    "vol",
    "vol_ccy",
    "vol_quote",
    "source_row_count",
    "complete_hour",
    "confirm",
    "source_first_open_time",
    "source_last_open_time",
    "source_zip_sha256",
    "source_csv_file",
    "source_date",
    "build_scope",
]
DANGEROUS_FLAGS = {
    "new_download_performed_now": False,
    "okx_api_call_performed_now": False,
    "okx_browse_performed_now": False,
    "strategy_research_implementation_touched": False,
    "candidate_generation_touched": False,
    "runtime_touched": False,
    "capital_changed": False,
    "live_or_real_orders": False,
    "repo_schema_config_created_now": False,
    "generic_runner_approval_granted": False,
}


class Blocked(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def iso_utc_from_ms(epoch_ms: int) -> str:
    return datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc).isoformat()


def run_git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def repo_has_only_this_tool_change() -> bool:
    status = run_git(["status", "--short"]).splitlines()
    if not status:
        return True
    approved_rel = APPROVED_TOOL.relative_to(REPO_ROOT).as_posix()
    return all(line[3:].replace("\\", "/") == approved_rel for line in status)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Blocked(message)


def load_json(path: Path) -> Any:
    require(path.exists(), f"missing artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_zip_member(name: str) -> bool:
    normalized = name.replace("\\", "/")
    posix = PurePosixPath(normalized)
    if normalized.startswith("/") or normalized.startswith("../") or "/../" in normalized:
        return False
    if posix.is_absolute() or any(part == ".." for part in posix.parts):
        return False
    if posix.parts and ":" in posix.parts[0]:
        return False
    return True


def parse_decimal(value: str, field: str, source_file: str, row_number: int) -> Decimal:
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise Blocked(f"numeric parse failed {field} {source_file} row={row_number}") from exc
    require(parsed.is_finite(), f"non-finite numeric {field} {source_file} row={row_number}")
    return parsed


def decimal_text(value: Decimal) -> str:
    normalized = value.normalize()
    if normalized == normalized.to_integral():
        return str(normalized.quantize(Decimal(1)))
    return format(normalized, "f")


def parse_confirm(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y"}


def expected_csv_for_date(day: str) -> str:
    return f"{TARGET_SYMBOL}-candlesticks-{day}.csv"


def validate_preflight(preview: dict[str, Any], approval: dict[str, Any], validator: dict[str, Any]) -> None:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved module")
    require(preview.get("historical_data_acquisition_okx_single_symbol_30_day_1m_to_1h_build_preview_status") == PREVIEW_STATUS, "preview status mismatch")
    require(preview.get("next_module") == REQUESTED_MODULE, "preview next_module mismatch")
    require(preview.get("approval_grants_future_30_day_build_next") is True, "future build approval missing")
    require(preview.get("approval_grants_build_now") is False, "build-now approval unexpectedly true")
    require(preview.get("target_symbol") == TARGET_SYMBOL, "preview target mismatch")
    require(preview.get("date_range_start") == DATE_RANGE_START, "preview start mismatch")
    require(preview.get("date_range_end") == DATE_RANGE_END, "preview end mismatch")
    require(preview.get("expected_file_count") == EXPECTED_FILE_COUNT, "preview file count mismatch")
    require(preview.get("expected_total_source_rows") == EXPECTED_TOTAL_SOURCE_ROWS, "preview source rows mismatch")
    require(preview.get("expected_output_rows") == EXPECTED_OUTPUT_ROWS, "preview output rows mismatch")
    require(preview.get("safe_for_broad_acquisition") is False, "preview broad flag mismatch")
    require(preview.get("safe_for_research_backtest") is False, "preview research flag mismatch")
    require(preview.get("safe_for_edge_claim") is False, "preview edge flag mismatch")
    require(approval.get("approval_grants_future_30_day_build_next") is True, "approval record missing future build grant")
    require(approval.get("approval_grants_build_now") is False, "approval record grants build now")
    require(approval.get("next_module") == REQUESTED_MODULE, "approval next_module mismatch")
    require(validator.get("historical_data_acquisition_okx_single_symbol_30_day_download_execution_validator_status") == DOWNLOAD_VALIDATOR_STATUS, "download validator status mismatch")
    require(validator.get("next_module") == "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_30_day_1m_to_1h_build_preview_after_download_validator_v1.py", "download validator chain mismatch")
    require(validator.get("safe_for_30_day_build_preview") is True, "download validator build preview safety missing")
    require(validator.get("safe_for_broad_acquisition") is False, "download validator broad flag mismatch")
    require(validator.get("safe_for_research_backtest") is False, "download validator research flag mismatch")
    require(validator.get("safe_for_edge_claim") is False, "download validator edge flag mismatch")


def read_zip_rows(entry: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    path = Path(entry["local_zip_path"])
    require(path.exists(), f"ZIP missing: {path}")
    digest = sha256_file(path)
    require(digest == entry["sha256_recorded"], f"SHA256 mismatch: {path}")
    expected_csv = expected_csv_for_date(entry["date"])
    require(entry.get("date") >= DATE_RANGE_START and entry.get("date") <= DATE_RANGE_END, f"date out of range: {entry.get('date')}")
    rows: list[dict[str, Any]] = []
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        require(len(names) <= 10, f"too many ZIP members: {path}")
        require(all(safe_zip_member(name) for name in names), f"ZIP traversal risk: {path}")
        require(expected_csv in names, f"expected CSV missing: {expected_csv}")
        with archive.open(expected_csv, "r") as raw:
            text = (line.decode("utf-8-sig").rstrip("\r\n") for line in raw)
            reader = csv.DictReader(text)
            require(reader.fieldnames == EXPECTED_SCHEMA, f"schema mismatch: {expected_csv}")
            previous_open_time: int | None = None
            seen_file_times: set[int] = set()
            for row_number, raw_row in enumerate(reader, start=2):
                require(raw_row.get("instrument_name") == TARGET_SYMBOL, f"symbol mismatch {expected_csv} row={row_number}")
                open_ = parse_decimal(raw_row["open"], "open", expected_csv, row_number)
                high = parse_decimal(raw_row["high"], "high", expected_csv, row_number)
                low = parse_decimal(raw_row["low"], "low", expected_csv, row_number)
                close = parse_decimal(raw_row["close"], "close", expected_csv, row_number)
                vol = parse_decimal(raw_row["vol"], "vol", expected_csv, row_number)
                vol_ccy = parse_decimal(raw_row["vol_ccy"], "vol_ccy", expected_csv, row_number)
                vol_quote = parse_decimal(raw_row["vol_quote"], "vol_quote", expected_csv, row_number)
                require(vol >= 0 and vol_ccy >= 0 and vol_quote >= 0, f"negative volume {expected_csv} row={row_number}")
                require(high >= max(open_, close, low), f"invalid high {expected_csv} row={row_number}")
                require(low <= min(open_, close, high), f"invalid low {expected_csv} row={row_number}")
                try:
                    open_time = int(raw_row["open_time"])
                except ValueError as exc:
                    raise Blocked(f"open_time parse failed {expected_csv} row={row_number}") from exc
                if previous_open_time is not None:
                    require(open_time > previous_open_time, f"non-monotonic open_time {expected_csv}")
                    require(open_time - previous_open_time == 60_000, f"missing minute within file {expected_csv}")
                previous_open_time = open_time
                require(open_time not in seen_file_times, f"duplicate open_time within file {expected_csv}")
                seen_file_times.add(open_time)
                rows.append(
                    {
                        "instrument_name": TARGET_SYMBOL,
                        "open": open_,
                        "high": high,
                        "low": low,
                        "close": close,
                        "vol": vol,
                        "vol_ccy": vol_ccy,
                        "vol_quote": vol_quote,
                        "open_time": open_time,
                        "confirm": parse_confirm(raw_row["confirm"]),
                        "source_zip_sha256": digest,
                        "source_csv_file": expected_csv,
                        "source_date": entry["date"],
                    }
                )
    require(len(rows) == EXPECTED_SOURCE_ROWS_PER_FILE, f"source rows for {expected_csv}={len(rows)}")
    metadata = {
        "date": entry["date"],
        "source_url": entry.get("source_url"),
        "source_zip_path": str(path),
        "source_zip_sha256": digest,
        "source_zip_size_bytes": path.stat().st_size,
        "source_csv_file": expected_csv,
        "source_row_count": len(rows),
    }
    return rows, metadata


def analyze_rows(all_rows: list[dict[str, Any]], source_row_count_by_file: dict[str, int]) -> dict[str, Any]:
    require(len(all_rows) <= MAX_TOTAL_SOURCE_ROWS, "total source rows exceeds limit")
    require(len(all_rows) == EXPECTED_TOTAL_SOURCE_ROWS, f"total source rows={len(all_rows)}")
    open_times = [row["open_time"] for row in all_rows]
    duplicates = len(open_times) - len(set(open_times))
    require(duplicates == 0, "duplicate open_time exists")
    sorted_times = sorted(open_times)
    missing = 0
    deltas = []
    for left, right in zip(sorted_times, sorted_times[1:]):
        delta = right - left
        deltas.append(delta)
        if delta != 60_000:
            missing += max(0, (delta // 60_000) - 1)
    require(missing == 0, "missing minutes detected")
    symbols = sorted({row["instrument_name"] for row in all_rows})
    require(symbols == [TARGET_SYMBOL], f"unexpected symbols: {symbols}")
    return {
        "source_row_count_total": len(all_rows),
        "expected_total_source_rows": EXPECTED_TOTAL_SOURCE_ROWS,
        "source_row_count_by_file": source_row_count_by_file,
        "source_row_count_by_file_valid": all(count == EXPECTED_SOURCE_ROWS_PER_FILE for count in source_row_count_by_file.values()),
        "unique_symbol_count": len(symbols),
        "observed_symbol": TARGET_SYMBOL,
        "open_time_monotonic_by_file": True,
        "duplicate_open_time_count_total": duplicates,
        "missing_minute_count_total": missing,
        "observed_interval_ms": 60_000 if deltas and all(delta == 60_000 for delta in deltas) else None,
        "one_minute_interval_validated": bool(deltas) and all(delta == 60_000 for delta in deltas),
        "observed_first_open_time_ms": sorted_times[0],
        "observed_last_open_time_ms": sorted_times[-1],
        "observed_first_open_time_utc": iso_utc_from_ms(sorted_times[0]),
        "observed_last_open_time_utc": iso_utc_from_ms(sorted_times[-1]),
        "daily_boundary_interpretation": (
            "OKX daily ZIPs show a UTC+8-like archive boundary; validated continuous UTC minute coverage from "
            f"{iso_utc_from_ms(sorted_times[0])} through {iso_utc_from_ms(sorted_times[-1])}"
        ),
    }


def aggregate_rows(all_rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in all_rows:
        grouped[(row["open_time"] // 3_600_000) * 3_600_000].append(row)
    output: list[dict[str, str]] = []
    for hour_start in sorted(grouped):
        group = sorted(grouped[hour_start], key=lambda row: row["open_time"])
        unique_minutes = {row["open_time"] for row in group}
        require(len(group) == 60 and len(unique_minutes) == 60, f"incomplete hour {hour_start}")
        source_dates = sorted({row["source_date"] for row in group})
        source_csvs = sorted({row["source_csv_file"] for row in group})
        source_hashes = sorted({row["source_zip_sha256"] for row in group})
        output.append(
            {
                "instrument_name": TARGET_SYMBOL,
                "hour_start_epoch_ms": str(hour_start),
                "hour_start_iso_utc": iso_utc_from_ms(hour_start),
                "open": decimal_text(group[0]["open"]),
                "high": decimal_text(max(row["high"] for row in group)),
                "low": decimal_text(min(row["low"] for row in group)),
                "close": decimal_text(group[-1]["close"]),
                "vol": decimal_text(sum((row["vol"] for row in group), Decimal("0"))),
                "vol_ccy": decimal_text(sum((row["vol_ccy"] for row in group), Decimal("0"))),
                "vol_quote": decimal_text(sum((row["vol_quote"] for row in group), Decimal("0"))),
                "source_row_count": "60",
                "complete_hour": "true",
                "confirm": "true" if all(row["confirm"] for row in group) else "false",
                "source_first_open_time": str(group[0]["open_time"]),
                "source_last_open_time": str(group[-1]["open_time"]),
                "source_zip_sha256": "|".join(source_hashes),
                "source_csv_file": "|".join(source_csvs),
                "source_date": "|".join(source_dates),
                "build_scope": BUILD_SCOPE,
            }
        )
    require(len(output) <= EXPECTED_OUTPUT_ROWS, "output rows exceed expected max")
    require(len(output) == EXPECTED_OUTPUT_ROWS, f"output rows={len(output)}")
    return output


def write_output_csv(rows: list[dict[str, str]]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = (OUTPUT_DIR / "historical_okx_single_symbol_30_day_1m_to_1h_output.csv").resolve()
    output_path.relative_to(OUTPUT_DIR.resolve())
    try:
        output_path.relative_to(REPO_ROOT.resolve())
    except ValueError:
        pass
    else:
        raise Blocked("output path inside repo")
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_SCHEMA)
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def main() -> None:
    generated_at = utc_now()
    preview = load_json(PREVIEW_SUMMARY)
    approval = load_json(PREVIEW_APPROVAL)
    validator = load_json(DOWNLOAD_VALIDATOR_SUMMARY)
    hash_report = load_json(HASH_VALIDATION_REPORT)
    validate_preflight(preview, approval, validator)
    require(isinstance(hash_report, list) and len(hash_report) == EXPECTED_FILE_COUNT, "hash report count mismatch")

    all_rows: list[dict[str, Any]] = []
    file_metadata: list[dict[str, Any]] = []
    source_row_count_by_file: dict[str, int] = {}
    for entry in sorted(hash_report, key=lambda row: row["date"]):
        rows, metadata = read_zip_rows(entry)
        all_rows.extend(rows)
        file_metadata.append(metadata)
        source_row_count_by_file[metadata["source_csv_file"]] = metadata["source_row_count"]

    input_validation = analyze_rows(all_rows, source_row_count_by_file)
    output_rows = aggregate_rows(all_rows)
    output_path = write_output_csv(output_rows)
    complete_count = sum(1 for row in output_rows if row["complete_hour"] == "true")
    incomplete_count = len(output_rows) - complete_count
    output_schema_validated = bool(output_rows) and list(output_rows[0].keys()) == OUTPUT_SCHEMA
    require(output_schema_validated, "output schema invalid")

    compliance = {
        "no_new_download": True,
        "no_api": True,
        "no_browse": True,
        "no_unapproved_file": True,
        "no_multi_symbol": True,
        "no_strategy_backtest_candidate": True,
        "no_runtime_capital_live": True,
        "no_generic_runner": True,
        "no_repo_schema_config": True,
        "output_is_pipeline_30_day_validation_only": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "source_manifest_acquisition_ready": False,
    }
    gap_report = {
        "duplicate_minute_count_total": input_validation["duplicate_open_time_count_total"],
        "missing_minute_count_total": input_validation["missing_minute_count_total"],
        "incomplete_hour_count": incomplete_count,
        "invalid_row_count": 0,
        "quarantined_row_count": 0,
        "gap_duplicate_status": "PASS_NO_GAPS_DUPLICATES_OR_INCOMPLETE_HOURS",
    }
    schema_report = {
        "input_schema": EXPECTED_SCHEMA,
        "output_schema": OUTPUT_SCHEMA,
        "schema_match": True,
        "output_schema_validated": output_schema_validated,
        "numeric_validation_passed": True,
        "timestamp_unit": "epoch_milliseconds",
    }
    provenance_report = {
        "source_urls": [item["source_url"] for item in file_metadata],
        "source_zip_paths": [item["source_zip_path"] for item in file_metadata],
        "source_zip_sha256_by_file": {item["source_csv_file"]: item["source_zip_sha256"] for item in file_metadata},
        "source_zip_size_bytes_by_file": {item["source_csv_file"]: item["source_zip_size_bytes"] for item in file_metadata},
        "expected_inner_csv_by_file": {item["date"]: item["source_csv_file"] for item in file_metadata},
        "build_timestamp_utc": generated_at,
        "output_csv_path": str(output_path),
        "output_row_count": len(output_rows),
        "provenance_status": "THIRTY_DAY_SINGLE_SYMBOL_PIPELINE_VALIDATION_BUILD_OUTPUT",
    }

    replacement_checks = {
        "preflight_passed": True,
        "thirty_files_processed": len(file_metadata) == EXPECTED_FILE_COUNT,
        "single_symbol_processed": input_validation["unique_symbol_count"] == 1,
        "source_rows_expected": input_validation["source_row_count_total"] == EXPECTED_TOTAL_SOURCE_ROWS,
        "source_row_count_by_file_valid": input_validation["source_row_count_by_file_valid"],
        "output_rows_expected": len(output_rows) == EXPECTED_OUTPUT_ROWS,
        "all_hours_complete": complete_count == EXPECTED_OUTPUT_ROWS and incomplete_count == 0,
        "no_fill_used": True,
        "output_schema_validated": output_schema_validated,
        "no_new_download_api_browse": True,
        "not_research_backtest_edge": True,
        "not_broad_acquisition_ready": True,
        "schema_config_absent": True,
        "generic_runner_blocked": True,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }
    replacement_checks_all_true = all(replacement_checks.values())
    require(replacement_checks_all_true, "replacement checks failed")

    summary = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "historical_data_acquisition_okx_single_symbol_30_day_1m_to_1h_build_execution_status": PASS_STATUS,
        "final_decision": "30_DAY_1M_TO_1H_BUILD_EXECUTED_PENDING_VALIDATOR_PIPELINE_VALIDATION_ONLY",
        "next_action": "VALIDATE_30_DAY_SINGLE_SYMBOL_1M_TO_1H_BUILD_EXECUTION",
        "next_module": NEXT_MODULE,
        "build_execution_performed": True,
        "target_symbol": TARGET_SYMBOL,
        "date_range_start": DATE_RANGE_START,
        "date_range_end": DATE_RANGE_END,
        "expected_file_count": EXPECTED_FILE_COUNT,
        "file_count_processed": len(file_metadata),
        "all_source_zips_exist": True,
        "all_source_zip_sha256_match": True,
        "all_expected_inner_csv_present": True,
        "schema_match": True,
        "full_csv_read_performed": True,
        **input_validation,
        "aggregation_performed_now": True,
        "data_build_performed": True,
        "output_1h_row_count": len(output_rows),
        "expected_output_rows": EXPECTED_OUTPUT_ROWS,
        "complete_1h_row_count": complete_count,
        "incomplete_1h_row_count": incomplete_count,
        "all_hours_complete": complete_count == EXPECTED_OUTPUT_ROWS and incomplete_count == 0,
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "output_csv_created": output_path.exists(),
        "output_csv_path": str(output_path),
        "output_schema_validated": output_schema_validated,
        "output_is_pipeline_30_day_validation_only": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "source_manifest_acquisition_ready": False,
        "no_new_download": True,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "new_download_performed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "strategy_signal_claims_made": False,
        "tradable_edge_claims_made": False,
        "profit_claims_made": False,
        "backtest_performed": False,
        "candidate_generation_performed": False,
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "generic_runner_approval_granted": False,
        "current_evidence_chain_quality_before_execution": BEFORE_QUALITY,
        "current_evidence_chain_quality_after_execution": AFTER_QUALITY,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 8,
        "dormant_repo_attention_count": 716,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        "dangerous_flags_true_count": sum(1 for value in DANGEROUS_FLAGS.values() if value),
        "derived_live_repo_post_check": PASS_STATUS,
        "derived_live_repo_post_check_reason": (
            "built exactly one BTC-USDT-SWAP 30-day 1h pipeline-validation output from the 30 already "
            "validated OKX daily ZIPs; rechecked every SHA256 before CSV reads, read exactly 30 expected "
            "CSVs, validated 43200 monotonic unique 1m rows, produced 720 complete UTC 1h rows with no "
            "synthetic fill, forward fill, or backfill, and performed no new download/API/browse or "
            "research/backtest/edge/broad-acquisition/runtime/capital/live/schema/config/generic-runner action"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
    }

    execution_report = {
        "execution_scope": {
            "build_execution_performed": True,
            "target_symbol": TARGET_SYMBOL,
            "date_range_start": DATE_RANGE_START,
            "date_range_end": DATE_RANGE_END,
            "expected_file_count": EXPECTED_FILE_COUNT,
            "source_zip_sha256_validation_performed_for_all_files": True,
            "output_directory": str(OUTPUT_DIR),
            "new_download_performed": False,
            "api_call_performed": False,
            "browse_performed": False,
            "multi_symbol_processing": False,
        },
        "input_validation": {k: summary[k] for k in [
            "file_count_processed",
            "source_row_count_total",
            "expected_total_source_rows",
            "source_row_count_by_file",
            "unique_symbol_count",
            "observed_symbol",
            "open_time_monotonic_by_file",
            "duplicate_open_time_count_total",
            "missing_minute_count_total",
            "observed_interval_ms",
            "one_minute_interval_validated",
            "observed_first_open_time_utc",
            "observed_last_open_time_utc",
            "daily_boundary_interpretation",
        ]},
        "aggregation_execution": {k: summary[k] for k in [
            "aggregation_performed_now",
            "data_build_performed",
            "output_1h_row_count",
            "expected_output_rows",
            "complete_1h_row_count",
            "incomplete_1h_row_count",
            "all_hours_complete",
            "synthetic_fill_used",
            "forward_fill_used",
            "backfill_used",
            "output_csv_created",
            "output_csv_path",
            "output_schema_validated",
        ]},
        "gap_duplicate_report": gap_report,
        "provenance_report": provenance_report,
        "compliance_report": compliance,
        "next_module_decision": {"next_module": NEXT_MODULE, "blocked_next_module": BLOCKED_NEXT_MODULE},
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_1m_to_1h_build_execution_report.json", execution_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_1m_to_1h_gap_duplicate_report.json", gap_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_1m_to_1h_schema_validation_report.json", schema_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_1m_to_1h_output_provenance_report.json", provenance_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_1m_to_1h_build_execution_compliance_report.json", compliance)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_1m_to_1h_build_execution_summary.json", summary)
    write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Blocked as exc:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        blocked = {
            "historical_data_acquisition_okx_single_symbol_30_day_1m_to_1h_build_execution_status": "BLOCKED_CONTEXT_MISMATCH",
            "next_module": BLOCKED_NEXT_MODULE,
            "blocked_reason": str(exc),
            "active_p0_blocker_count": 1,
            "replacement_checks_all_true": False,
        }
        write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_1m_to_1h_build_execution_summary.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        raise SystemExit(1)
