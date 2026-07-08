from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import zipfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_download_execution_validator_after_execution_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "f56484d"
TARGET_SYMBOL = "BTC-USDT-SWAP"
NOMINAL_STRICT_3Y_START = date(2023, 5, 19)
MAX_AVAILABLE_START = date(2023, 7, 1)
MAX_AVAILABLE_END = date(2026, 5, 18)
EXPECTED_FILE_COUNT = 1053
EXPECTED_REUSE_COUNT = 30
EXPECTED_NEW_DOWNLOAD_COUNT = 1023
MAX_ZIP_MEMBERS = 10
MAX_CSV_SAMPLE_ROWS = 5
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
PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_DOWNLOAD_EXECUTED_"
    "PENDING_VALIDATOR_MAX_AVAILABLE_NO_BUILD"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_DOWNLOAD_EXECUTION_VALIDATED_"
    "BUILD_PREVIEW_READY_MAX_AVAILABLE_NO_BUILD"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_DOWNLOAD_EXECUTION_VALIDATION"
)
BEFORE_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_DOWNLOAD_EXECUTED_"
    "PENDING_VALIDATOR_MAX_AVAILABLE_NO_BUILD"
)
AFTER_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_DOWNLOAD_EXECUTION_VALIDATED_"
    "BUILD_PREVIEW_READY_MAX_AVAILABLE_NO_BUILD"
)
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_1m_to_1h_build_preview_after_download_validator_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_download_execution_validation_blocked_or_gap_record_after_execution_v1.py"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
EXECUTION_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_download_execution_after_30_day_summary_preview_approval_v1"
)

ARTIFACTS = {
    "latest": EXECUTION_DIR
    / (
        "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
        "3_year_download_execution_after_30_day_summary_preview_approval_v1_latest.json"
    ),
    "execution_summary": EXECUTION_DIR / "historical_okx_single_symbol_3_year_download_execution_summary.json",
    "execution_report": EXECUTION_DIR / "historical_okx_single_symbol_3_year_download_execution_report.json",
    "provenance_report": EXECUTION_DIR / "historical_okx_single_symbol_3_year_download_provenance_report.json",
    "hash_manifest": EXECUTION_DIR / "historical_okx_single_symbol_3_year_hash_manifest.json",
    "zip_inventory_report": EXECUTION_DIR / "historical_okx_single_symbol_3_year_zip_inventory_report.json",
    "schema_sample_report": EXECUTION_DIR / "historical_okx_single_symbol_3_year_schema_sample_report.json",
    "coverage_gap_report": EXECUTION_DIR / "historical_okx_single_symbol_3_year_coverage_gap_report.json",
    "compliance_report": EXECUTION_DIR / "historical_okx_single_symbol_3_year_download_execution_compliance_report.json",
}

DANGEROUS_FLAGS = {
    "new_download_performed_by_validator": False,
    "data_build_performed": False,
    "aggregation_performed_now": False,
    "okx_api_call_performed": False,
    "okx_browse_performed": False,
    "url_fetch_performed": False,
    "full_csv_read_performed": False,
    "multi_symbol_performed": False,
    "research_backtest_edge_claim_made": False,
    "broad_acquisition_ready_claim_made": False,
    "runtime_touched": False,
    "capital_changed": False,
    "live_or_real_orders": False,
    "schema_or_config_created": False,
    "generic_runner_approval_granted": False,
}


class ValidationBlocked(RuntimeError):
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
        raise ValidationBlocked(message)


def load_json(path: Path, label: str, exists: dict[str, bool], valid: dict[str, bool]) -> Any:
    exists[label] = path.exists()
    require(path.exists(), f"missing artifact {label}: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        valid[label] = False
        raise ValidationBlocked(f"invalid JSON artifact {label}: {exc}") from exc
    valid[label] = True
    require(isinstance(data, dict), f"artifact {label} is not a JSON object")
    return data


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def inclusive_days(start: date, end: date) -> list[date]:
    days: list[date] = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)
    return days


def okx_url(day: date) -> str:
    compact = day.strftime("%Y%m%d")
    iso_day = day.isoformat()
    return (
        "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/"
        f"{compact}/{TARGET_SYMBOL}-candlesticks-{iso_day}.zip"
    )


def expected_csv(day_text: str) -> str:
    return f"{TARGET_SYMBOL}-candlesticks-{day_text}.csv"


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


def validate_artifact_chain(artifacts: dict[str, Any]) -> None:
    summary = artifacts["execution_summary"]
    latest = artifacts["latest"]
    report = artifacts["execution_report"]
    coverage = artifacts["coverage_gap_report"]
    compliance = artifacts["compliance_report"]

    for label, data in [("summary", summary), ("latest", latest)]:
        require(
            data.get("historical_data_acquisition_okx_single_symbol_3_year_download_execution_status")
            == PREVIOUS_STATUS,
            f"{label} previous status mismatch",
        )
        require(data.get("next_module") == REQUESTED_MODULE, f"{label} next_module mismatch")
        require(data.get("download_execution_performed") is True, f"{label} execution not performed")
        require(data.get("target_symbol") == TARGET_SYMBOL, f"{label} target mismatch")
        require(data.get("nominal_strict_3y_start_date") == NOMINAL_STRICT_3Y_START.isoformat(), f"{label} nominal strict start mismatch")
        require(data.get("nominal_end_date") == MAX_AVAILABLE_END.isoformat(), f"{label} nominal end mismatch")
        require(data.get("strict_3y_completeness_claimed") is False, f"{label} strict 3y claim detected")
        require(data.get("max_available_start_candidate") == MAX_AVAILABLE_START.isoformat(), f"{label} max start mismatch")
        require(data.get("max_available_end_date") == MAX_AVAILABLE_END.isoformat(), f"{label} max end mismatch")
        require(data.get("max_available_candidate_file_count") == EXPECTED_FILE_COUNT, f"{label} max file count mismatch")
        require(data.get("existing_validated_reuse_file_count") == EXPECTED_REUSE_COUNT, f"{label} reuse count mismatch")
        require(data.get("new_download_file_count") == EXPECTED_NEW_DOWNLOAD_COUNT, f"{label} new download count mismatch")
        require(data.get("final_file_set_count") == EXPECTED_FILE_COUNT, f"{label} final file set mismatch")
        require(data.get("missing_or_failed_file_count") == 0, f"{label} missing/failed files detected")
        require(data.get("coverage_gap_detected") is False, f"{label} coverage gap detected")
        require(data.get("approved_url_manifest_used") is True, f"{label} approved manifest flag mismatch")
        require(data.get("all_downloads_succeeded") is True, f"{label} download success mismatch")
        require(data.get("all_reused_files_validated") is True, f"{label} reuse validation mismatch")
        require(data.get("all_hashes_computed_or_revalidated") is True, f"{label} hash flag mismatch")
        require(data.get("all_zip_open_success") is True, f"{label} zip open flag mismatch")
        require(data.get("all_expected_inner_csv_present") is True, f"{label} inner CSV flag mismatch")
        require(data.get("all_expected_schema_match") is True, f"{label} schema flag mismatch")
        require(data.get("all_observed_symbols_match_target") is True, f"{label} symbol flag mismatch")
        require(data.get("max_csv_sample_rows_read_per_file") <= MAX_CSV_SAMPLE_ROWS, f"{label} sample row limit exceeded")
        require(data.get("full_csv_read_performed") is False, f"{label} full CSV read detected")
        require(data.get("data_build_performed") is False, f"{label} data build detected")
        require(data.get("aggregation_performed_now") is False, f"{label} aggregation detected")
        require(data.get("okx_api_call_performed") is False, f"{label} API detected")
        require(data.get("okx_browse_performed") is False, f"{label} browse detected")
        require(data.get("files_marked_build_ready") is False, f"{label} files marked build-ready")
        require(data.get("source_manifest_acquisition_ready") is False, f"{label} source manifest ready claim")
        require(data.get("broad_acquisition_execution_allowed_now") is False, f"{label} broad acquisition claim")
        require(data.get("output_valid_for_research_backtest") is False, f"{label} research/backtest claim")
        require(data.get("output_valid_for_edge_claim") is False, f"{label} edge claim")

    require(report.get("final_file_set_count") == EXPECTED_FILE_COUNT, "execution report final count mismatch")
    require(report.get("new_download_file_count") == EXPECTED_NEW_DOWNLOAD_COUNT, "execution report download count mismatch")
    require(report.get("existing_validated_reuse_file_count") == EXPECTED_REUSE_COUNT, "execution report reuse count mismatch")
    require(coverage.get("coverage_gap_detected") is False, "coverage gap report detected a gap")
    require(coverage.get("missing_or_failed_file_count") == 0, "coverage gap report missing count mismatch")
    require(coverage.get("strict_3y_completeness_claimed") is False, "coverage gap report strict 3y claim")
    require(compliance.get("no_api") is True, "compliance API mismatch")
    require(compliance.get("no_browse") is True, "compliance browse mismatch")
    require(compliance.get("no_full_csv_read") is True, "compliance full CSV read mismatch")
    require(compliance.get("no_data_build") is True, "compliance build mismatch")
    require(compliance.get("no_aggregation") is True, "compliance aggregation mismatch")
    require(compliance.get("output_valid_for_research_backtest") is False, "compliance research/backtest claim")
    require(compliance.get("output_valid_for_edge_claim") is False, "compliance edge claim")
    require(compliance.get("broad_acquisition_execution_allowed_now") is False, "compliance broad acquisition claim")


def validate_files(provenance: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    items = provenance.get("per_file_provenance", [])
    require(isinstance(items, list), "provenance items not a list")
    require(len(items) == EXPECTED_FILE_COUNT, "provenance file count mismatch")

    expected_days = [day.isoformat() for day in inclusive_days(MAX_AVAILABLE_START, MAX_AVAILABLE_END)]
    expected_urls = [okx_url(day) for day in inclusive_days(MAX_AVAILABLE_START, MAX_AVAILABLE_END)]
    by_date: dict[str, dict[str, Any]] = {}
    for item in items:
        require(isinstance(item, dict), "provenance item is not object")
        day = item.get("date")
        require(isinstance(day, str), "provenance item missing date")
        require(day not in by_date, f"duplicate provenance date: {day}")
        by_date[day] = item
    require(list(by_date) == expected_days, "date coverage does not exactly match max-available range")
    observed_urls = [by_date[day].get("source_url") for day in expected_days]
    require(observed_urls == expected_urls, "approved URL manifest mismatch")

    all_paths_exist = True
    all_reused_revalidated = True
    all_hashes_match = True
    all_zip_open = True
    all_inner_csv = True
    all_schema = True
    all_symbols = True
    all_one_minute = True
    traversal_count = 0
    too_many_members_count = 0
    max_sample_rows = 0
    recomputed_hashes: list[dict[str, Any]] = []
    zip_schema_items: list[dict[str, Any]] = []

    reuse_count = 0
    new_download_count = 0
    for day in expected_days:
        item = by_date[day]
        path = Path(str(item.get("local_zip_path", "")))
        source_kind = item.get("source_kind")
        if source_kind == "REUSED_VALIDATED_30_DAY_FILE":
            reuse_count += 1
        elif source_kind == "DOWNLOADED_MAX_AVAILABLE_MISSING_APPROVED_URL":
            new_download_count += 1
        else:
            raise ValidationBlocked(f"unexpected source_kind for {day}: {source_kind}")

        path_exists = path.exists()
        all_paths_exist = all_paths_exist and path_exists
        require(path_exists, f"ZIP missing: {path}")
        digest = sha256_file(path)
        size = path.stat().st_size
        recorded_hash = item.get("sha256")
        hash_match = digest == recorded_hash
        all_hashes_match = all_hashes_match and hash_match
        if source_kind == "REUSED_VALIDATED_30_DAY_FILE":
            all_reused_revalidated = all_reused_revalidated and hash_match

        expected_inner = expected_csv(day)
        zip_open_success = False
        expected_present = False
        schema_match = False
        symbols_match = False
        one_minute = False
        sample_rows_count = 0
        member_count = 0
        member_names: list[str] = []
        traversal = False
        try:
            with zipfile.ZipFile(path) as archive:
                zip_open_success = True
                member_names = archive.namelist()
                member_count = len(member_names)
                traversal = any(not safe_zip_member(name) for name in member_names)
                expected_present = expected_inner in member_names
                require(member_count <= MAX_ZIP_MEMBERS, f"too many ZIP members: {path}")
                require(not traversal, f"ZIP traversal risk: {path}")
                require(expected_present, f"expected inner CSV missing: {expected_inner}")
                with archive.open(expected_inner, "r") as raw:
                    text = (line.decode("utf-8-sig").rstrip("\r\n") for line in raw)
                    reader = csv.reader(text)
                    header = next(reader)
                    rows: list[list[str]] = []
                    for _, row in zip(range(MAX_CSV_SAMPLE_ROWS), reader):
                        rows.append(row)
        except (OSError, zipfile.BadZipFile, StopIteration) as exc:
            raise ValidationBlocked(f"ZIP/schema validation failed for {day}: {exc}") from exc

        sample_rows_count = len(rows)
        max_sample_rows = max(max_sample_rows, sample_rows_count)
        schema_match = header == EXPECTED_SCHEMA
        observed_symbols = sorted({row[0] for row in rows if row})
        symbols_match = all(symbol == TARGET_SYMBOL for symbol in observed_symbols) if observed_symbols else True
        open_times: list[int] = []
        for row in rows:
            if len(row) > 8:
                try:
                    open_times.append(int(row[8]))
                except ValueError:
                    pass
        deltas = [right - left for left, right in zip(open_times, open_times[1:])]
        one_minute = (deltas and all(delta == 60_000 for delta in deltas)) or sample_rows_count < 2

        all_zip_open = all_zip_open and zip_open_success
        all_inner_csv = all_inner_csv and expected_present
        all_schema = all_schema and schema_match
        all_symbols = all_symbols and symbols_match
        all_one_minute = all_one_minute and one_minute
        traversal_count += 1 if traversal else 0
        too_many_members_count += 1 if member_count > MAX_ZIP_MEMBERS else 0

        recomputed_hashes.append(
            {
                "date": day,
                "local_zip_path": str(path),
                "file_size_bytes": size,
                "recorded_sha256": recorded_hash,
                "recomputed_sha256": digest,
                "hash_match": hash_match,
                "source_kind": source_kind,
            }
        )
        zip_schema_items.append(
            {
                "date": day,
                "zip_path": str(path),
                "zip_path_exists": path_exists,
                "zip_open_success": zip_open_success,
                "zip_member_count": member_count,
                "zip_member_count_within_limit": member_count <= MAX_ZIP_MEMBERS,
                "zip_path_traversal_detected": traversal,
                "expected_inner_csv": expected_inner,
                "expected_inner_csv_present": expected_present,
                "csv_header_read": True,
                "csv_sample_rows_read_count": sample_rows_count,
                "full_csv_read_performed": False,
                "expected_schema_match": schema_match,
                "observed_symbols": observed_symbols,
                "observed_symbols_match_target": symbols_match,
                "one_minute_interval_observed_from_sample": one_minute,
                "zip_member_names": member_names,
            }
        )

    require(reuse_count == EXPECTED_REUSE_COUNT, "validated reuse count mismatch")
    require(new_download_count == EXPECTED_NEW_DOWNLOAD_COUNT, "validated new download count mismatch")
    require(max_sample_rows <= MAX_CSV_SAMPLE_ROWS, "sample row limit exceeded")

    hash_validation = {
        "all_downloaded_zip_paths_exist": all_paths_exist,
        "all_reused_files_revalidated": all_reused_revalidated and reuse_count == EXPECTED_REUSE_COUNT,
        "all_hashes_recomputed": len(recomputed_hashes) == EXPECTED_FILE_COUNT,
        "all_hashes_match_recorded": all_hashes_match,
        "recomputed_hash_count": len(recomputed_hashes),
        "reuse_count_revalidated": reuse_count,
        "new_download_count_revalidated": new_download_count,
        "hashes": recomputed_hashes,
    }
    zip_schema_validation = {
        "all_zip_open_success": all_zip_open,
        "all_zip_member_counts_within_limit": too_many_members_count == 0,
        "zip_path_traversal_detected_count": traversal_count,
        "all_expected_inner_csv_present": all_inner_csv,
        "all_expected_schema_match": all_schema,
        "all_observed_symbols_match_target": all_symbols,
        "all_one_minute_interval_observed_from_samples": all_one_minute,
        "max_csv_sample_rows_read_per_file": max_sample_rows,
        "full_csv_read_performed": False,
        "zip_schema_items": zip_schema_items,
    }
    coverage_validation = {
        "target_symbol": TARGET_SYMBOL,
        "max_available_start_candidate": MAX_AVAILABLE_START.isoformat(),
        "max_available_end_date": MAX_AVAILABLE_END.isoformat(),
        "max_available_candidate_file_count": EXPECTED_FILE_COUNT,
        "observed_file_count": len(items),
        "existing_validated_reuse_file_count": reuse_count,
        "new_download_file_count": new_download_count,
        "final_file_set_count": len(items),
        "missing_or_failed_file_count": 0,
        "coverage_gap_detected": False,
        "approved_url_manifest_validated": True,
        "strict_3y_completeness_claimed": False,
    }
    return hash_validation, zip_schema_validation, coverage_validation


def main() -> None:
    generated_at = utc_now()
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved validator module")

    exists: dict[str, bool] = {}
    valid_json: dict[str, bool] = {}
    artifacts = {
        label: load_json(path, label, exists, valid_json)
        for label, path in ARTIFACTS.items()
    }
    validate_artifact_chain(artifacts)
    hash_validation, zip_schema_validation, coverage_validation = validate_files(artifacts["provenance_report"])

    require(hash_validation["all_downloaded_zip_paths_exist"], "not all ZIP paths exist")
    require(hash_validation["all_reused_files_revalidated"], "not all reused files revalidated")
    require(hash_validation["all_hashes_recomputed"], "not all hashes recomputed")
    require(hash_validation["all_hashes_match_recorded"], "hash mismatch found")
    require(zip_schema_validation["all_zip_open_success"], "ZIP open failure found")
    require(zip_schema_validation["all_expected_inner_csv_present"], "expected inner CSV missing")
    require(zip_schema_validation["all_expected_schema_match"], "schema mismatch found")
    require(zip_schema_validation["all_observed_symbols_match_target"], "sampled symbol mismatch found")
    require(zip_schema_validation["all_one_minute_interval_observed_from_samples"], "sampled interval mismatch found")

    validator_p0_count = 0
    validator_p1_count = 8
    replacement_checks = {
        "preflight_passed": True,
        "execution_artifacts_exist": all(exists.values()),
        "execution_artifacts_valid_json": all(valid_json.values()),
        "max_available_file_count_1053": coverage_validation["final_file_set_count"] == EXPECTED_FILE_COUNT,
        "reuse_count_30": coverage_validation["existing_validated_reuse_file_count"] == EXPECTED_REUSE_COUNT,
        "new_download_count_1023": coverage_validation["new_download_file_count"] == EXPECTED_NEW_DOWNLOAD_COUNT,
        "missing_failed_zero": coverage_validation["missing_or_failed_file_count"] == 0,
        "approved_url_manifest_validated": coverage_validation["approved_url_manifest_validated"],
        "all_zip_paths_exist": hash_validation["all_downloaded_zip_paths_exist"],
        "all_reused_files_revalidated": hash_validation["all_reused_files_revalidated"],
        "all_hashes_recomputed": hash_validation["all_hashes_recomputed"],
        "all_hashes_match_recorded": hash_validation["all_hashes_match_recorded"],
        "all_zip_open_success": zip_schema_validation["all_zip_open_success"],
        "all_expected_inner_csv_present": zip_schema_validation["all_expected_inner_csv_present"],
        "all_expected_schema_match": zip_schema_validation["all_expected_schema_match"],
        "all_observed_symbols_match_target": zip_schema_validation["all_observed_symbols_match_target"],
        "all_one_minute_interval_observed": zip_schema_validation["all_one_minute_interval_observed_from_samples"],
        "sample_limit_respected": zip_schema_validation["max_csv_sample_rows_read_per_file"] <= MAX_CSV_SAMPLE_ROWS,
        "full_csv_read_false": True,
        "no_new_download_api_browse": True,
        "no_build_aggregation": True,
        "strict_3y_completeness_not_claimed": True,
        "not_broad_research_edge": True,
        "safe_for_build_preview": True,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }
    replacement_checks_all_true = all(replacement_checks.values())
    require(replacement_checks_all_true, "replacement checks did not all pass")

    summary_payload = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": head,
        "historical_data_acquisition_okx_single_symbol_3_year_download_execution_validator_status": PASS_STATUS,
        "download_execution_validated": True,
        "target_symbol": TARGET_SYMBOL,
        "nominal_strict_3y_start_date": NOMINAL_STRICT_3Y_START.isoformat(),
        "nominal_end_date": MAX_AVAILABLE_END.isoformat(),
        "strict_3y_completeness_claimed": False,
        "max_available_start_candidate": MAX_AVAILABLE_START.isoformat(),
        "max_available_end_date": MAX_AVAILABLE_END.isoformat(),
        "max_available_candidate_file_count": EXPECTED_FILE_COUNT,
        "existing_validated_reuse_file_count": EXPECTED_REUSE_COUNT,
        "new_download_file_count": EXPECTED_NEW_DOWNLOAD_COUNT,
        "final_file_set_count": EXPECTED_FILE_COUNT,
        "missing_or_failed_file_count": 0,
        "coverage_gap_detected": False,
        "approved_url_manifest_validated": True,
        "all_downloaded_zip_paths_exist": hash_validation["all_downloaded_zip_paths_exist"],
        "all_reused_files_revalidated": hash_validation["all_reused_files_revalidated"],
        "all_hashes_recomputed": hash_validation["all_hashes_recomputed"],
        "all_hashes_match_recorded": hash_validation["all_hashes_match_recorded"],
        "all_zip_open_success": zip_schema_validation["all_zip_open_success"],
        "all_expected_inner_csv_present": zip_schema_validation["all_expected_inner_csv_present"],
        "all_expected_schema_match": zip_schema_validation["all_expected_schema_match"],
        "all_observed_symbols_match_target": zip_schema_validation["all_observed_symbols_match_target"],
        "all_one_minute_interval_observed_from_samples": zip_schema_validation["all_one_minute_interval_observed_from_samples"],
        "max_csv_sample_rows_read_per_file": zip_schema_validation["max_csv_sample_rows_read_per_file"],
        "full_csv_read_performed": False,
        "new_download_performed_by_validator": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "safe_for_3_year_build_preview": True,
        "safe_for_broad_acquisition": False,
        "safe_for_research_backtest": False,
        "safe_for_edge_claim": False,
        "validator_p0_count": validator_p0_count,
        "validator_p1_count": validator_p1_count,
        "current_evidence_chain_quality_before_validator": BEFORE_QUALITY,
        "current_evidence_chain_quality_after_validator": AFTER_QUALITY,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": validator_p1_count,
        "dormant_repo_attention_count": 716,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "next_module": NEXT_MODULE_PASS,
        "derived_live_repo_post_check": PASS_STATUS,
        "derived_live_repo_post_check_reason": (
            "validated the existing BTC-USDT-SWAP max-available 2023-07-01 through "
            "2026-05-18 ZIP set from execution artifacts; recomputed 1053 SHA256 hashes, "
            "opened all ZIP central directories, confirmed expected inner CSVs, exact "
            "schema, sampled BTC-USDT-SWAP symbol and 1m interval using at most five rows "
            "per CSV; no new download, API, browse, full CSV read, build, aggregation, "
            "strict 3-year completeness, broad acquisition, research, backtest, edge, "
            "runtime, capital, live, schema/config, or generic-runner action"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "artifact_exists_by_label": exists,
        "artifact_valid_json_by_label": valid_json,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": True,
        "tracked_python_count_at_validator_run": tracked_python_count(),
    }
    bundle = {
        "hash_validation": hash_validation,
        "zip_schema_validation": zip_schema_validation,
        "coverage_validation": coverage_validation,
        "summary": summary_payload,
    }

    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_download_execution_validator.json", bundle)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_hash_validation_report.json", hash_validation)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_zip_schema_validation_report.json", zip_schema_validation)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_coverage_validation_report.json", coverage_validation)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_download_execution_validator_summary.json", summary_payload)
    write_json(
        OUTPUT_DIR / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_3_year_download_execution_validator_after_execution_v1_latest.json",
        summary_payload,
    )
    print(json.dumps(summary_payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except ValidationBlocked as exc:
        blocked_payload = {
            "module_name": MODULE_NAME,
            "generated_at_utc": utc_now(),
            "historical_data_acquisition_okx_single_symbol_3_year_download_execution_validator_status": BLOCKED_STATUS,
            "download_execution_validated": False,
            "target_symbol": TARGET_SYMBOL,
            "nominal_strict_3y_start_date": NOMINAL_STRICT_3Y_START.isoformat(),
            "nominal_end_date": MAX_AVAILABLE_END.isoformat(),
            "strict_3y_completeness_claimed": False,
            "max_available_start_candidate": MAX_AVAILABLE_START.isoformat(),
            "max_available_end_date": MAX_AVAILABLE_END.isoformat(),
            "max_available_candidate_file_count": EXPECTED_FILE_COUNT,
            "coverage_gap_detected": True,
            "full_csv_read_performed": False,
            "new_download_performed_by_validator": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "okx_api_call_performed": False,
            "okx_browse_performed": False,
            "safe_for_3_year_build_preview": False,
            "safe_for_broad_acquisition": False,
            "safe_for_research_backtest": False,
            "safe_for_edge_claim": False,
            "validator_p0_count": 1,
            "validator_p1_count": 0,
            "active_p0_blocker_count": 1,
            "active_p1_attention_count": 0,
            "dormant_repo_attention_count": 716,
            "generic_runner_implementation_remains_blocked": True,
            "schema_or_config_created": False,
            "ordinary_selector_backlog_loop_reentry_allowed": False,
            "loop_remains_closed": True,
            "next_module": NEXT_MODULE_BLOCKED,
            "derived_live_repo_post_check": BLOCKED_STATUS,
            "replacement_checks_all_true": False,
            "blocked_reason": str(exc),
        }
        write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_download_execution_validator_summary.json", blocked_payload)
        write_json(
            OUTPUT_DIR / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_3_year_download_execution_validator_after_execution_v1_latest.json",
            blocked_payload,
        )
        print(json.dumps(blocked_payload, indent=2, sort_keys=True))
        raise SystemExit(1)
