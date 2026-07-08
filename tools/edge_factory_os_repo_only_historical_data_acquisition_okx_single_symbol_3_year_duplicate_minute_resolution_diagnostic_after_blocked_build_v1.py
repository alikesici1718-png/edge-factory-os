from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
import zipfile
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_duplicate_minute_resolution_diagnostic_after_blocked_build_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "06510c6"
TARGET_SYMBOL = "BTC-USDT-SWAP"
MAX_AVAILABLE_START = date(2023, 7, 1)
MAX_AVAILABLE_END = date(2026, 5, 18)
EXPECTED_FILE_COUNT = 1053
OBSERVED_SOURCE_ROWS = 1_516_641
EXPECTED_TOTAL_SOURCE_ROWS = 1_516_320
EXPECTED_UNIQUE_OPEN_TIME_COUNT = 1_516_320
EXPECTED_DUPLICATE_EXTRA_ROW_COUNT = 321
EXPECTED_MISSING_MINUTE_COUNT = 0
PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_BUILD_BLOCKED_RECORD_"
    "DUPLICATE_MINUTE_RESOLUTION_DIAGNOSTIC_READY"
)
PASS_STATUS_EXACT = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_DUPLICATE_MINUTE_"
    "DIAGNOSTIC_EXACT_DEDUPE_REBUILD_READY"
)
PASS_STATUS_CONFLICT = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_DUPLICATE_MINUTE_"
    "DIAGNOSTIC_CONFLICTING_DATA_QUALITY_REVIEW_REQUIRED"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_DUPLICATE_MINUTE_DIAGNOSTIC"
)
BEFORE_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_BUILD_BLOCKED_DUPLICATE_"
    "MINUTE_RESOLUTION_DIAGNOSTIC_READY"
)
AFTER_QUALITY_EXACT = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_DUPLICATES_DIAGNOSED_"
    "EXACT_DEDUPE_REBUILD_READY"
)
AFTER_QUALITY_CONFLICT = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_DUPLICATES_CONFLICTING_"
    "DATA_QUALITY_REVIEW_REQUIRED"
)
NEXT_MODULE_EXACT = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_exact_dedupe_rebuild_execution_after_duplicate_diagnostic_v1.py"
)
NEXT_MODULE_CONFLICT = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_conflicting_duplicate_data_quality_review_after_diagnostic_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_duplicate_minute_diagnostic_blocked_record_v1.py"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
BLOCKED_RECORD_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_1m_to_1h_build_execution_blocked_record_after_preview_approval_v1"
)
DOWNLOAD_VALIDATOR_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_download_execution_validator_after_execution_v1"
)

BLOCKED_RECORD_SUMMARY = BLOCKED_RECORD_DIR / f"{BLOCKED_RECORD_DIR.name}_latest.json"
BLOCKED_RECORD_ARTIFACT = BLOCKED_RECORD_DIR / "historical_okx_single_symbol_3_year_build_blocked_record.json"
BLOCKED_APPROVAL_ARTIFACT = BLOCKED_RECORD_DIR / "historical_okx_single_symbol_3_year_duplicate_minute_resolution_approval_record.json"
DOWNLOAD_VALIDATOR_SUMMARY = DOWNLOAD_VALIDATOR_DIR / "historical_okx_single_symbol_3_year_download_execution_validator_summary.json"
HASH_VALIDATION_REPORT = DOWNLOAD_VALIDATOR_DIR / "historical_okx_single_symbol_3_year_hash_validation_report.json"

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
CANONICAL_FIELDS = [
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
DANGEROUS_FLAGS = {
    "download_performed_now": False,
    "api_call_performed_now": False,
    "browse_performed_now": False,
    "url_fetch_performed_now": False,
    "data_build_performed": False,
    "aggregation_performed_now": False,
    "output_csv_created": False,
    "deduped_source_output_created_now": False,
    "synthetic_fill_used": False,
    "forward_fill_used": False,
    "backfill_used": False,
    "conflicting_row_choice_performed": False,
    "ohlcv_modification_performed": False,
    "research_backtest_edge_claim_made": False,
    "broad_acquisition_ready_claim_made": False,
    "strict_3y_completeness_claimed": False,
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


def repo_has_only_this_tool_change() -> bool:
    status = run_git(["status", "--short"]).splitlines()
    if not status:
        return True
    approved_rel = APPROVED_TOOL.relative_to(REPO_ROOT).as_posix()
    return all(line[3:].replace("\\", "/") == approved_rel for line in status)


def tracked_python_count() -> int:
    return sum(1 for path in run_git(["ls-files"]).splitlines() if path.endswith(".py"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Blocked(message)


def load_json(path: Path) -> Any:
    require(path.exists(), f"missing artifact: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"artifact is not a JSON object: {path}")
    return data


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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


def inclusive_days(start: date, end: date) -> list[str]:
    days: list[str] = []
    current = start
    while current <= end:
        days.append(current.isoformat())
        current += timedelta(days=1)
    return days


def expected_csv_for_date(day: str) -> str:
    return f"{TARGET_SYMBOL}-candlesticks-{day}.csv"


def normalize_decimal_or_raw(value: Any) -> str:
    text = str(value).strip()
    try:
        parsed = Decimal(text)
    except (InvalidOperation, ValueError):
        return text
    require(parsed.is_finite(), f"non-finite decimal value: {text!r}")
    normalized = parsed.normalize()
    if normalized == normalized.to_integral():
        return str(normalized.quantize(Decimal(1)))
    return format(normalized, "f")


def normalize_confirm(value: Any) -> str:
    text = str(value).strip().lower()
    if text in {"1", "true", "t", "yes", "y"}:
        return "true"
    if text in {"0", "false", "f", "no", "n"}:
        return "false"
    return text


def canonical_row(row: dict[str, Any]) -> dict[str, str]:
    return {
        "instrument_name": str(row["instrument_name"]).strip(),
        "open": normalize_decimal_or_raw(row["open"]),
        "high": normalize_decimal_or_raw(row["high"]),
        "low": normalize_decimal_or_raw(row["low"]),
        "close": normalize_decimal_or_raw(row["close"]),
        "vol": normalize_decimal_or_raw(row["vol"]),
        "vol_ccy": normalize_decimal_or_raw(row["vol_ccy"]),
        "vol_quote": normalize_decimal_or_raw(row["vol_quote"]),
        "open_time": str(int(str(row["open_time"]).strip())),
        "confirm": normalize_confirm(row["confirm"]),
    }


def canonical_key(canon: dict[str, str]) -> tuple[str, ...]:
    return tuple(canon[field] for field in CANONICAL_FIELDS)


def occurrence(row: dict[str, Any], source_csv: str, source_date: str, source_zip_path: Path, row_number: int) -> dict[str, Any]:
    return {
        "source_date": source_date,
        "source_csv_file": source_csv,
        "source_zip_path": str(source_zip_path),
        "row_number": row_number,
        "raw_values": {field: row.get(field) for field in CANONICAL_FIELDS},
        "canonical_values": canonical_row(row),
    }


def validate_preflight(blocked_summary: dict[str, Any], blocked_record: dict[str, Any], blocked_approval: dict[str, Any], validator: dict[str, Any]) -> None:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved module")
    require(
        blocked_summary.get("historical_data_acquisition_okx_single_symbol_3_year_build_blocked_record_status")
        == PREVIOUS_STATUS,
        "blocked record status mismatch",
    )
    require(blocked_summary.get("next_module") == REQUESTED_MODULE, "blocked record next_module mismatch")
    require(blocked_summary.get("block_reason") == "DUPLICATE_OPEN_TIME_ROWS", "block reason mismatch")
    require(blocked_summary.get("target_symbol") == TARGET_SYMBOL, "target symbol mismatch")
    require(blocked_summary.get("expected_file_count") == EXPECTED_FILE_COUNT, "expected file count mismatch")
    require(blocked_summary.get("file_count_processed") == EXPECTED_FILE_COUNT, "file count processed mismatch")
    require(blocked_summary.get("source_row_count_total") == OBSERVED_SOURCE_ROWS, "source row count mismatch")
    require(blocked_summary.get("expected_total_source_rows") == EXPECTED_TOTAL_SOURCE_ROWS, "expected row count mismatch")
    require(blocked_summary.get("duplicate_open_time_count_total") == EXPECTED_DUPLICATE_EXTRA_ROW_COUNT, "duplicate count mismatch")
    require(blocked_summary.get("missing_minute_count_total") == EXPECTED_MISSING_MINUTE_COUNT, "missing minute count mismatch")
    require(blocked_summary.get("active_p0_blocker_count") == 1, "P0 blocker count mismatch")
    require(blocked_summary.get("build_execution_blocked") is True, "build not marked blocked")
    require(blocked_summary.get("data_build_performed") is False, "data build flag mismatch")
    require(blocked_summary.get("aggregation_performed_now") is False, "aggregation flag mismatch")
    require(blocked_summary.get("output_csv_created") is False, "output CSV flag mismatch")
    require(blocked_record.get("build_execution_blocked") is True, "blocked artifact mismatch")
    require(blocked_record.get("duplicate_open_time_count_total") == EXPECTED_DUPLICATE_EXTRA_ROW_COUNT, "blocked artifact duplicate mismatch")
    require(blocked_approval.get("approval_grants_future_duplicate_diagnosis_next") is True, "future diagnostic approval missing")
    require(blocked_approval.get("approval_grants_rebuild_now") is False, "rebuild-now approval mismatch")
    require(blocked_approval.get("approval_grants_download_now") is False, "download approval mismatch")
    require(
        validator.get("historical_data_acquisition_okx_single_symbol_3_year_download_execution_validator_status")
        == "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_DOWNLOAD_EXECUTION_VALIDATED_BUILD_PREVIEW_READY_MAX_AVAILABLE_NO_BUILD",
        "download validator status mismatch",
    )
    require(validator.get("all_downloaded_zip_paths_exist") is True, "validator ZIP path flag mismatch")
    require(validator.get("all_hashes_match_recorded") is True, "validator hash flag mismatch")
    require(validator.get("all_expected_inner_csv_present") is True, "validator inner CSV flag mismatch")
    require(validator.get("all_expected_schema_match") is True, "validator schema flag mismatch")
    require(validator.get("all_observed_symbols_match_target") is True, "validator symbol flag mismatch")


def load_hash_entries(hash_report: dict[str, Any]) -> list[dict[str, Any]]:
    require(hash_report.get("all_downloaded_zip_paths_exist") is True, "hash report ZIP path flag mismatch")
    require(hash_report.get("all_hashes_recomputed") is True, "hash report recompute flag mismatch")
    require(hash_report.get("all_hashes_match_recorded") is True, "hash report hash flag mismatch")
    items = hash_report.get("hashes")
    require(isinstance(items, list), "hash report hashes is not a list")
    require(len(items) == EXPECTED_FILE_COUNT, f"hash report count mismatch: {len(items)}")
    expected_days = inclusive_days(MAX_AVAILABLE_START, MAX_AVAILABLE_END)
    by_date: dict[str, dict[str, Any]] = {}
    for item in items:
        require(isinstance(item, dict), "hash report item is not an object")
        day = item.get("date")
        require(isinstance(day, str), "hash report item missing date")
        require(day not in by_date, f"duplicate hash date: {day}")
        by_date[day] = item
    require(list(by_date) == expected_days, "hash report date coverage mismatch")
    return [by_date[day] for day in expected_days]


def diagnose_duplicates(entries: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    first_by_open_time: dict[int, dict[str, Any]] = {}
    duplicate_groups: dict[int, dict[str, Any]] = {}
    open_times: list[int] = []
    symbols: set[str] = set()
    total_rows = 0
    file_count = 0
    all_source_zips_revalidated = True
    all_expected_inner_csv_present = True
    schema_match = True

    for entry in entries:
        day = str(entry.get("date"))
        path = Path(str(entry.get("local_zip_path", "")))
        require(path.exists(), f"ZIP missing: {path}")
        digest = sha256_file(path)
        recorded_hash = str(entry.get("recorded_sha256", ""))
        hash_match = digest == recorded_hash
        all_source_zips_revalidated = all_source_zips_revalidated and hash_match
        require(hash_match, f"SHA256 mismatch: {path}")
        expected_csv = expected_csv_for_date(day)
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            require(len(names) <= 10, f"too many ZIP members: {path}")
            require(all(safe_zip_member(name) for name in names), f"ZIP traversal risk: {path}")
            expected_present = expected_csv in names
            all_expected_inner_csv_present = all_expected_inner_csv_present and expected_present
            require(expected_present, f"expected CSV missing: {expected_csv}")
            with archive.open(expected_csv, "r") as raw:
                text = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
                reader = csv.DictReader(text)
                header_match = reader.fieldnames == EXPECTED_SCHEMA
                schema_match = schema_match and header_match
                require(header_match, f"schema mismatch: {expected_csv}")
                for row_number, row in enumerate(reader, start=2):
                    require(row.get("instrument_name") == TARGET_SYMBOL, f"symbol mismatch {expected_csv} row={row_number}")
                    open_time = int(str(row["open_time"]).strip())
                    symbols.add(str(row["instrument_name"]).strip())
                    canon = canonical_row(row)
                    occ = occurrence(row, expected_csv, day, path, row_number)
                    open_times.append(open_time)
                    total_rows += 1
                    if open_time not in first_by_open_time:
                        first_by_open_time[open_time] = {
                            "canonical_key": canonical_key(canon),
                            "first_occurrence": occ,
                        }
                    else:
                        if open_time not in duplicate_groups:
                            first = first_by_open_time[open_time]
                            duplicate_groups[open_time] = {
                                "open_time": open_time,
                                "occurrences": [first["first_occurrence"]],
                                "canonical_keys": Counter({first["canonical_key"]: 1}),
                            }
                        group = duplicate_groups[open_time]
                        group["occurrences"].append(occ)
                        group["canonical_keys"][canonical_key(canon)] += 1
        file_count += 1

    sorted_unique_times = sorted(first_by_open_time)
    missing_minute_count = 0
    for left, right in zip(sorted_unique_times, sorted_unique_times[1:]):
        delta = right - left
        if delta != 60_000:
            missing_minute_count += max(0, (delta // 60_000) - 1)

    group_reports: list[dict[str, Any]] = []
    conflict_reports: list[dict[str, Any]] = []
    exact_group_count = 0
    exact_extra_count = 0
    conflict_group_count = 0
    conflict_extra_count = 0
    within_file_group_count = 0
    cross_file_group_count = 0
    both_location_group_count = 0

    for open_time in sorted(duplicate_groups):
        group = duplicate_groups[open_time]
        occurrences = group["occurrences"]
        group_size = len(occurrences)
        duplicate_extra_count = group_size - 1
        source_csv_counts = Counter(occ["source_csv_file"] for occ in occurrences)
        within_file = any(count > 1 for count in source_csv_counts.values())
        cross_file = len(source_csv_counts) > 1
        canonical_variant_count = len(group["canonical_keys"])
        exact = canonical_variant_count == 1
        conflict = not exact
        exact_group_count += 1 if exact else 0
        exact_extra_count += duplicate_extra_count if exact else 0
        conflict_group_count += 1 if conflict else 0
        conflict_extra_count += duplicate_extra_count if conflict else 0
        within_file_group_count += 1 if within_file else 0
        cross_file_group_count += 1 if cross_file else 0
        both_location_group_count += 1 if within_file and cross_file else 0
        row = {
            "open_time": open_time,
            "group_size": group_size,
            "duplicate_extra_count": duplicate_extra_count,
            "exact_duplicate_group": exact,
            "conflicting_duplicate_group": conflict,
            "within_file_duplicate_group": within_file,
            "cross_file_duplicate_group": cross_file,
            "source_csv_files": sorted(source_csv_counts),
            "source_csv_counts": dict(sorted(source_csv_counts.items())),
            "canonical_variant_count": canonical_variant_count,
            "occurrences": occurrences,
        }
        group_reports.append(row)
        if conflict:
            conflict_reports.append(row)

    duplicate_extra_total = total_rows - len(first_by_open_time)
    diagnostic = {
        "file_count_processed": file_count,
        "source_row_count_total": total_rows,
        "expected_total_source_rows": EXPECTED_TOTAL_SOURCE_ROWS,
        "duplicate_open_time_count_total": duplicate_extra_total,
        "diagnostic_duplicate_extra_row_count": duplicate_extra_total,
        "duplicate_open_time_group_count": len(group_reports),
        "exact_duplicate_group_count": exact_group_count,
        "exact_duplicate_extra_row_count": exact_extra_count,
        "conflicting_duplicate_group_count": conflict_group_count,
        "conflicting_duplicate_extra_row_count": conflict_extra_count,
        "missing_minute_count_total": missing_minute_count,
        "unique_open_time_count": len(first_by_open_time),
        "expected_unique_open_time_count": EXPECTED_UNIQUE_OPEN_TIME_COUNT,
        "source_row_count_after_exact_dedupe": len(first_by_open_time) if conflict_group_count == 0 else None,
        "exact_dedupe_would_restore_expected_row_count": conflict_group_count == 0
        and len(first_by_open_time) == EXPECTED_TOTAL_SOURCE_ROWS,
        "all_duplicates_exact": conflict_group_count == 0 and duplicate_extra_total == EXPECTED_DUPLICATE_EXTRA_ROW_COUNT,
        "any_conflicting_duplicates": conflict_group_count > 0,
        "duplicate_locations_classified": True,
        "within_file_duplicate_group_count": within_file_group_count,
        "cross_file_duplicate_group_count": cross_file_group_count,
        "both_within_and_cross_file_duplicate_group_count": both_location_group_count,
        "all_source_zips_revalidated": all_source_zips_revalidated and file_count == EXPECTED_FILE_COUNT,
        "all_expected_inner_csv_present": all_expected_inner_csv_present,
        "schema_match": schema_match,
        "unique_symbol_count": len(symbols),
        "observed_symbol": TARGET_SYMBOL if symbols == {TARGET_SYMBOL} else "|".join(sorted(symbols)),
    }
    return diagnostic, group_reports, conflict_reports


def main() -> None:
    generated_at = utc_now()
    blocked_summary = load_json(BLOCKED_RECORD_SUMMARY)
    blocked_record = load_json(BLOCKED_RECORD_ARTIFACT)
    blocked_approval = load_json(BLOCKED_APPROVAL_ARTIFACT)
    validator = load_json(DOWNLOAD_VALIDATOR_SUMMARY)
    hash_report = load_json(HASH_VALIDATION_REPORT)
    validate_preflight(blocked_summary, blocked_record, blocked_approval, validator)
    entries = load_hash_entries(hash_report)
    diagnostic, group_reports, conflict_reports = diagnose_duplicates(entries)

    safe_exact = (
        diagnostic["source_row_count_total"] == OBSERVED_SOURCE_ROWS
        and diagnostic["duplicate_open_time_count_total"] == EXPECTED_DUPLICATE_EXTRA_ROW_COUNT
        and diagnostic["diagnostic_duplicate_extra_row_count"] == EXPECTED_DUPLICATE_EXTRA_ROW_COUNT
        and diagnostic["exact_duplicate_extra_row_count"] == EXPECTED_DUPLICATE_EXTRA_ROW_COUNT
        and diagnostic["conflicting_duplicate_group_count"] == 0
        and diagnostic["conflicting_duplicate_extra_row_count"] == 0
        and diagnostic["missing_minute_count_total"] == EXPECTED_MISSING_MINUTE_COUNT
        and diagnostic["unique_open_time_count"] == EXPECTED_UNIQUE_OPEN_TIME_COUNT
        and diagnostic["exact_dedupe_would_restore_expected_row_count"] is True
        and diagnostic["all_source_zips_revalidated"] is True
        and diagnostic["all_expected_inner_csv_present"] is True
        and diagnostic["schema_match"] is True
        and diagnostic["unique_symbol_count"] == 1
        and diagnostic["observed_symbol"] == TARGET_SYMBOL
    )

    next_module = NEXT_MODULE_EXACT if safe_exact else NEXT_MODULE_CONFLICT
    status = PASS_STATUS_EXACT if safe_exact else PASS_STATUS_CONFLICT
    after_quality = AFTER_QUALITY_EXACT if safe_exact else AFTER_QUALITY_CONFLICT
    active_p0 = 0 if safe_exact else 1
    active_p1 = 8 if safe_exact else 9
    source_row_count_after_exact_dedupe = (
        diagnostic["source_row_count_after_exact_dedupe"]
        if diagnostic["source_row_count_after_exact_dedupe"] is not None
        else diagnostic["unique_open_time_count"]
    )

    exact_dedupe_preview = {
        "exact_dedupe_rebuild_preview_created": safe_exact,
        "preview_only": True,
        "diagnostic_supports_exact_dedupe_rebuild": safe_exact,
        "dedupe_policy": "DROP_ONLY_EXACT_DUPLICATE_ROWS_KEEP_FIRST_CANONICAL_ROW_PER_OPEN_TIME",
        "duplicate_rows_removed_must_be_audit_recorded_in_future_rebuild": True,
        "no_conflicting_rows_may_be_removed": True,
        "no_ohlcv_values_may_be_altered": True,
        "no_synthetic_fill_forward_fill_or_backfill": True,
        "future_rebuild_may_aggregate_after_exact_dedupe_only": safe_exact,
        "future_rebuild_pipeline_validation_only_not_research_backtest_edge": True,
        "conflicting_duplicate_group_count": diagnostic["conflicting_duplicate_group_count"],
        "exact_duplicate_extra_row_count": diagnostic["exact_duplicate_extra_row_count"],
    }
    approval_record = {
        "exact_dedupe_rebuild_approval_record_created": safe_exact,
        "approval_grants_rebuild_now": False,
        "approval_grants_future_exact_dedupe_rebuild_next": safe_exact,
        "approval_grants_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "approval_grants_conflicting_duplicate_resolution_now": False,
        "next_module": next_module,
    }
    replacement_checks = {
        "preflight_passed": True,
        "diagnostic_performed": True,
        "file_count_1053": diagnostic["file_count_processed"] == EXPECTED_FILE_COUNT,
        "source_rows_observed": diagnostic["source_row_count_total"] == OBSERVED_SOURCE_ROWS,
        "expected_rows_preserved": diagnostic["expected_total_source_rows"] == EXPECTED_TOTAL_SOURCE_ROWS,
        "duplicate_extra_count_321": diagnostic["duplicate_open_time_count_total"] == EXPECTED_DUPLICATE_EXTRA_ROW_COUNT,
        "diagnostic_duplicate_extra_count_321": diagnostic["diagnostic_duplicate_extra_row_count"] == EXPECTED_DUPLICATE_EXTRA_ROW_COUNT,
        "missing_minutes_zero": diagnostic["missing_minute_count_total"] == EXPECTED_MISSING_MINUTE_COUNT,
        "unique_open_time_expected": diagnostic["unique_open_time_count"] == EXPECTED_UNIQUE_OPEN_TIME_COUNT,
        "locations_classified": diagnostic["duplicate_locations_classified"] is True,
        "all_source_zips_revalidated": diagnostic["all_source_zips_revalidated"] is True,
        "all_expected_inner_csv_present": diagnostic["all_expected_inner_csv_present"] is True,
        "schema_match": diagnostic["schema_match"] is True,
        "single_symbol": diagnostic["unique_symbol_count"] == 1 and diagnostic["observed_symbol"] == TARGET_SYMBOL,
        "exact_route_consistent": (
            safe_exact
            and diagnostic["all_duplicates_exact"] is True
            and diagnostic["any_conflicting_duplicates"] is False
            and approval_record["approval_grants_future_exact_dedupe_rebuild_next"] is True
        )
        or (
            not safe_exact
            and diagnostic["any_conflicting_duplicates"] is True
            and approval_record["approval_grants_future_exact_dedupe_rebuild_next"] is False
        ),
        "no_download_api_browse": True,
        "no_build_aggregation_output": True,
        "not_research_backtest_edge_broad": True,
        "strict_3y_not_claimed": True,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        "next_module_valid": next_module in {NEXT_MODULE_EXACT, NEXT_MODULE_CONFLICT},
    }
    replacement_checks_all_true = all(replacement_checks.values())
    require(replacement_checks_all_true, "replacement checks failed")

    diagnostic_artifact = {
        "diagnostic_performed": True,
        "target_symbol": TARGET_SYMBOL,
        **diagnostic,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "output_csv_created": False,
        "strict_3y_completeness_claimed": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "duplicate_normalization_policy": {
            "instrument_name": "exact string",
            "open_time": "integer",
            "open_high_low_close_vol_vol_ccy_vol_quote": "normalized decimal string when decimal parse succeeds, otherwise raw stripped string",
            "confirm": "boolean-equivalent normalized string",
            "rounding_used": False,
        },
    }
    group_report = {
        "duplicate_open_time_group_count": diagnostic["duplicate_open_time_group_count"],
        "diagnostic_duplicate_extra_row_count": diagnostic["diagnostic_duplicate_extra_row_count"],
        "exact_duplicate_group_count": diagnostic["exact_duplicate_group_count"],
        "exact_duplicate_extra_row_count": diagnostic["exact_duplicate_extra_row_count"],
        "conflicting_duplicate_group_count": diagnostic["conflicting_duplicate_group_count"],
        "conflicting_duplicate_extra_row_count": diagnostic["conflicting_duplicate_extra_row_count"],
        "within_file_duplicate_group_count": diagnostic["within_file_duplicate_group_count"],
        "cross_file_duplicate_group_count": diagnostic["cross_file_duplicate_group_count"],
        "groups": group_reports,
    }
    conflict_report = {
        "any_conflicting_duplicates": diagnostic["any_conflicting_duplicates"],
        "conflicting_duplicate_group_count": diagnostic["conflicting_duplicate_group_count"],
        "conflicting_duplicate_extra_row_count": diagnostic["conflicting_duplicate_extra_row_count"],
        "conflicting_groups": conflict_reports,
    }
    summary = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "historical_data_acquisition_okx_single_symbol_3_year_duplicate_minute_diagnostic_status": status,
        "diagnostic_performed": True,
        "target_symbol": TARGET_SYMBOL,
        "expected_file_count": EXPECTED_FILE_COUNT,
        **diagnostic,
        "source_row_count_after_exact_dedupe": source_row_count_after_exact_dedupe,
        "exact_dedupe_would_restore_expected_row_count": source_row_count_after_exact_dedupe == EXPECTED_TOTAL_SOURCE_ROWS
        and diagnostic["conflicting_duplicate_group_count"] == 0,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "output_csv_created": False,
        "exact_dedupe_rebuild_preview_created": safe_exact,
        "exact_dedupe_rebuild_approval_record_created": safe_exact,
        "approval_grants_rebuild_now": False,
        "approval_grants_future_exact_dedupe_rebuild_next": safe_exact,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "strict_3y_completeness_claimed": False,
        "active_p0_blocker_count": active_p0,
        "active_p1_attention_count": active_p1,
        "current_evidence_chain_quality_before_diagnostic": BEFORE_QUALITY,
        "current_evidence_chain_quality_after_diagnostic": after_quality,
        "next_module": next_module,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": True,
        "tracked_python_count_at_diagnostic_run": tracked_python_count(),
    }

    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_duplicate_minute_diagnostic.json", diagnostic_artifact)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_duplicate_minute_group_report.json", group_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_duplicate_minute_conflict_report.json", conflict_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_exact_dedupe_rebuild_preview.json", exact_dedupe_preview)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_exact_dedupe_rebuild_approval_record.json", approval_record)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_duplicate_minute_diagnostic_summary.json", summary)
    write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Blocked as exc:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        blocked = {
            "module_name": MODULE_NAME,
            "generated_at_utc": utc_now(),
            "historical_data_acquisition_okx_single_symbol_3_year_duplicate_minute_diagnostic_status": BLOCKED_STATUS,
            "diagnostic_performed": False,
            "target_symbol": TARGET_SYMBOL,
            "expected_file_count": EXPECTED_FILE_COUNT,
            "source_row_count_total": None,
            "expected_total_source_rows": EXPECTED_TOTAL_SOURCE_ROWS,
            "duplicate_open_time_count_total": None,
            "diagnostic_duplicate_extra_row_count": None,
            "missing_minute_count_total": None,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "output_csv_created": False,
            "exact_dedupe_rebuild_preview_created": False,
            "exact_dedupe_rebuild_approval_record_created": False,
            "approval_grants_rebuild_now": False,
            "approval_grants_future_exact_dedupe_rebuild_next": False,
            "output_valid_for_research_backtest": False,
            "output_valid_for_edge_claim": False,
            "broad_acquisition_ready": False,
            "strict_3y_completeness_claimed": False,
            "active_p0_blocker_count": 1,
            "active_p1_attention_count": 0,
            "current_evidence_chain_quality_before_diagnostic": BEFORE_QUALITY,
            "current_evidence_chain_quality_after_diagnostic": BEFORE_QUALITY,
            "next_module": NEXT_MODULE_BLOCKED,
            "replacement_checks_all_true": False,
            "blocked_reason": str(exc),
        }
        write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_duplicate_minute_diagnostic_summary.json", blocked)
        write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        raise SystemExit(1)
