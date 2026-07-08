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
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "download_execution_validator_after_execution_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "260f69e"
PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_DOWNLOAD_EXECUTED_"
    "PENDING_VALIDATOR_NO_BUILD_NO_AGGREGATION"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_DOWNLOAD_EXECUTION_"
    "VALIDATED_BUILD_PREVIEW_READY_NO_BUILD_NO_AGGREGATION"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_DOWNLOAD_EXECUTION_"
    "VALIDATION_AFTER_EXECUTION"
)
BEFORE_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_DOWNLOAD_EXECUTED_PENDING_"
    "VALIDATOR_NO_BUILD_NO_AGGREGATION"
)
AFTER_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_DOWNLOAD_EXECUTION_VALIDATED_"
    "BUILD_PREVIEW_READY_NO_BUILD_NO_AGGREGATION"
)
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "build_preview_after_download_validator_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "download_validation_blocked_record_after_execution_v1.py"
)

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
REUSED_SYMBOL = "BTC-USDT-SWAP"
DATE_RANGE_START = date(2023, 7, 1)
DATE_RANGE_END = date(2026, 5, 18)
EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 1_053
EXPECTED_TOTAL_PILOT_FILE_COUNT = 10_530
EXPECTED_REUSED_FILE_COUNT = 1_053
EXPECTED_NEW_DOWNLOAD_FILE_COUNT = 9_477
EXPECTED_NEW_SYMBOL_COUNT = 9
MAX_ZIP_MEMBERS_PER_FILE = 10
MAX_CSV_SAMPLE_ROWS_PER_FILE = 5
EXPECTED_DORMANT_REPO_ATTENTION_COUNT = 716
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

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
EXECUTION_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "download_execution_after_expansion_preview_approval_v1"
)

ARTIFACTS = {
    "execution_summary": EXECUTION_DIR / "historical_okx_10_symbol_pilot_download_execution_summary.json",
    "execution_report": EXECUTION_DIR / "historical_okx_10_symbol_pilot_download_execution_report.json",
    "provenance_report": EXECUTION_DIR / "historical_okx_10_symbol_pilot_download_provenance_report.json",
    "hash_manifest": EXECUTION_DIR / "historical_okx_10_symbol_pilot_hash_manifest.json",
    "zip_inventory_report": EXECUTION_DIR / "historical_okx_10_symbol_pilot_zip_inventory_report.json",
    "schema_sample_report": EXECUTION_DIR / "historical_okx_10_symbol_pilot_schema_sample_report.json",
    "coverage_gap_report": EXECUTION_DIR / "historical_okx_10_symbol_pilot_coverage_gap_report.json",
    "compliance_report": EXECUTION_DIR / "historical_okx_10_symbol_pilot_download_execution_compliance_report.json",
}

DANGEROUS_FLAGS = {
    "full_csv_read_performed": False,
    "new_download_performed_by_validator": False,
    "data_build_performed": False,
    "aggregation_performed_now": False,
    "okx_api_call_performed": False,
    "okx_browse_performed": False,
    "url_fetch_performed": False,
    "parquet_read_performed": False,
    "research_backtest_edge_claim_made": False,
    "full_universe_ready_claim_made": False,
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


def load_json(path: Path, label: str, exists: dict[str, bool], valid: dict[str, bool]) -> dict[str, Any]:
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


def inclusive_days(start: date, end: date) -> list[str]:
    days: list[str] = []
    current = start
    while current <= end:
        days.append(current.isoformat())
        current += timedelta(days=1)
    return days


def expected_csv(symbol: str, day: str) -> str:
    return f"{symbol}-candlesticks-{day}.csv"


def expected_zip(symbol: str, day: str) -> str:
    return f"{symbol}-candlesticks-{day}.zip"


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


def source_kind_counts(records: list[dict[str, Any]]) -> tuple[int, int]:
    reused_count = 0
    new_count = 0
    for record in records:
        source_kind = record.get("source_kind")
        symbol = record.get("symbol")
        if symbol == REUSED_SYMBOL and source_kind == "REUSED_VALIDATED_BTC_FILE_SET":
            reused_count += 1
        elif symbol != REUSED_SYMBOL and source_kind == "NEW_APPROVED_PILOT_DOWNLOAD":
            new_count += 1
        else:
            raise ValidationBlocked(f"unexpected source_kind/symbol pair: {symbol} {source_kind}")
    return reused_count, new_count


def validate_artifact_chain(artifacts: dict[str, dict[str, Any]]) -> None:
    summary = artifacts["execution_summary"]
    report = artifacts["execution_report"]
    provenance = artifacts["provenance_report"]
    hash_manifest = artifacts["hash_manifest"]
    zip_inventory = artifacts["zip_inventory_report"]
    schema_sample = artifacts["schema_sample_report"]
    coverage = artifacts["coverage_gap_report"]
    compliance = artifacts["compliance_report"]

    for label, data in [("summary", summary)]:
        require(
            data.get("historical_data_acquisition_okx_10_symbol_pilot_download_execution_status")
            == PREVIOUS_STATUS,
            f"{label} previous status mismatch",
        )
        require(data.get("next_module") == REQUESTED_MODULE, f"{label} next_module mismatch")
        require(data.get("download_execution_performed") is True, f"{label} execution flag mismatch")
        require(data.get("pilot_symbol_count") == len(PILOT_SYMBOLS), f"{label} pilot symbol count mismatch")
        require(data.get("pilot_symbols") == PILOT_SYMBOLS, f"{label} pilot symbols mismatch")
        require(data.get("date_range_start") == DATE_RANGE_START.isoformat(), f"{label} start date mismatch")
        require(data.get("date_range_end") == DATE_RANGE_END.isoformat(), f"{label} end date mismatch")
        require(data.get("expected_total_pilot_file_count") == EXPECTED_TOTAL_PILOT_FILE_COUNT, f"{label} total expected mismatch")
        require(data.get("expected_reused_file_count") == EXPECTED_REUSED_FILE_COUNT, f"{label} reused expected mismatch")
        require(data.get("expected_new_download_file_count") == EXPECTED_NEW_DOWNLOAD_FILE_COUNT, f"{label} new expected mismatch")
        require(data.get("reused_file_count") == EXPECTED_REUSED_FILE_COUNT, f"{label} reused count mismatch")
        require(data.get("new_download_file_count") == EXPECTED_NEW_DOWNLOAD_FILE_COUNT, f"{label} new count mismatch")
        require(data.get("final_pilot_file_set_count") == EXPECTED_TOTAL_PILOT_FILE_COUNT, f"{label} final count mismatch")
        require(data.get("missing_or_failed_file_count") == 0, f"{label} missing/failed files detected")
        require(data.get("coverage_gap_detected") is False, f"{label} coverage gap detected")
        require(data.get("approved_manifest_used") is True, f"{label} approved manifest flag mismatch")
        require(data.get("all_downloads_succeeded") is True, f"{label} download success mismatch")
        require(data.get("all_reused_files_validated") is True, f"{label} reused validation mismatch")
        require(data.get("all_hashes_computed_or_revalidated") is True, f"{label} hash flag mismatch")
        require(data.get("all_zip_open_success") is True, f"{label} zip open flag mismatch")
        require(data.get("all_expected_inner_csv_present") is True, f"{label} inner CSV flag mismatch")
        require(data.get("all_expected_schema_match") is True, f"{label} schema flag mismatch")
        require(data.get("all_observed_symbols_match_expected") is True, f"{label} symbol flag mismatch")
        require(data.get("max_csv_sample_rows_read_per_file") <= MAX_CSV_SAMPLE_ROWS_PER_FILE, f"{label} sample limit mismatch")
        require(data.get("full_csv_read_performed") is False, f"{label} full CSV read detected")
        require(data.get("data_build_performed") is False, f"{label} build detected")
        require(data.get("aggregation_performed_now") is False, f"{label} aggregation detected")
        require(data.get("okx_api_call_performed") is False, f"{label} API detected")
        require(data.get("okx_browse_performed") is False, f"{label} browse detected")
        require(data.get("files_marked_build_ready") is False, f"{label} build-ready claim detected")
        require(data.get("source_manifest_acquisition_ready") is False, f"{label} source manifest ready claim detected")
        require(data.get("broad_acquisition_execution_allowed_now") is False, f"{label} broad acquisition claim detected")
        require(data.get("output_valid_for_research_backtest") is False, f"{label} research/backtest claim detected")
        require(data.get("output_valid_for_edge_claim") is False, f"{label} edge claim detected")

    require(report.get("expected_total_pilot_file_count") == EXPECTED_TOTAL_PILOT_FILE_COUNT, "execution report total mismatch")
    require(report.get("final_pilot_file_set_count") == EXPECTED_TOTAL_PILOT_FILE_COUNT, "execution report final count mismatch")
    require(report.get("missing_or_failed_file_count") == 0, "execution report missing/failed files detected")
    require(report.get("coverage_gap_detected") is False, "execution report coverage gap detected")
    require(provenance.get("download_directory"), "provenance missing download directory")
    require(len(provenance.get("download_results", [])) == EXPECTED_NEW_DOWNLOAD_FILE_COUNT, "download result count mismatch")
    require(hash_manifest.get("hash_record_count") == EXPECTED_TOTAL_PILOT_FILE_COUNT, "hash manifest count mismatch")
    require(hash_manifest.get("all_hashes_computed_or_revalidated") is True, "hash manifest flag mismatch")
    require(zip_inventory.get("all_zip_open_success") is True, "zip inventory open flag mismatch")
    require(zip_inventory.get("all_expected_inner_csv_present") is True, "zip inventory inner CSV flag mismatch")
    require(zip_inventory.get("path_traversal_detected") is False, "zip inventory path traversal detected")
    require(schema_sample.get("all_expected_schema_match") is True, "schema sample schema flag mismatch")
    require(schema_sample.get("all_observed_symbols_match_expected") is True, "schema sample symbol flag mismatch")
    require(schema_sample.get("full_csv_read_performed") is False, "schema sample full CSV read detected")
    require(schema_sample.get("max_csv_sample_rows_read_per_file") <= MAX_CSV_SAMPLE_ROWS_PER_FILE, "schema sample row limit exceeded")
    require(coverage.get("missing_or_failed_file_count") == 0, "coverage report missing/failed files detected")
    require(coverage.get("coverage_gap_detected") is False, "coverage report gap detected")
    for key, expected in {
        "approved_manifest_used": True,
        "full_csv_read_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "parquet_read_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "files_marked_build_ready": False,
        "source_manifest_acquisition_ready": False,
        "broad_acquisition_execution_allowed_now": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "runtime_touched": False,
        "capital_changed": False,
        "live_or_real_orders": False,
        "schema_or_config_created": False,
        "generic_runner_implementation_remains_blocked": True,
    }.items():
        require(compliance.get(key) is expected, f"compliance {key} mismatch")


def expected_pairs() -> set[tuple[str, str]]:
    return {(symbol, day) for symbol in PILOT_SYMBOLS for day in inclusive_days(DATE_RANGE_START, DATE_RANGE_END)}


def validate_manifest_records(hash_manifest: dict[str, Any]) -> list[dict[str, Any]]:
    records = hash_manifest.get("hashes")
    require(isinstance(records, list), "hashes field is not a list")
    require(len(records) == EXPECTED_TOTAL_PILOT_FILE_COUNT, "hash record count mismatch")
    pairs = {(str(record.get("symbol")), str(record.get("date"))) for record in records}
    expected = expected_pairs()
    missing_pairs = sorted(expected - pairs)
    extra_pairs = sorted(pairs - expected)
    require(not missing_pairs, f"missing expected symbol/date pairs: {missing_pairs[:5]}")
    require(not extra_pairs, f"extra symbol/date pairs: {extra_pairs[:5]}")
    for record in records:
        symbol = str(record.get("symbol"))
        day = str(record.get("date"))
        path = Path(str(record.get("local_zip_path", "")))
        require(path.name == expected_zip(symbol, day), f"zip filename mismatch for {symbol} {day}: {path.name}")
        require(record.get("hash_computed_or_revalidated") is True, f"prior hash flag false for {symbol} {day}")
        require(isinstance(record.get("sha256"), str) and len(record["sha256"]) == 64, f"invalid recorded sha256 for {symbol} {day}")
    return records


def validate_physical_extra_files(records: list[dict[str, Any]]) -> dict[str, Any]:
    expected_paths = {Path(str(record["local_zip_path"])).resolve() for record in records}
    parent_dirs = {path.parent for path in expected_paths}
    observed_zip_paths: set[Path] = set()
    for directory in parent_dirs:
        require(directory.exists(), f"ZIP parent directory missing: {directory}")
        observed_zip_paths.update(path.resolve() for path in directory.glob("*.zip"))
    extra_paths = sorted(str(path) for path in (observed_zip_paths - expected_paths))
    missing_paths = sorted(str(path) for path in (expected_paths - observed_zip_paths))
    return {
        "physical_parent_directory_count": len(parent_dirs),
        "physical_observed_zip_count_in_parent_dirs": len(observed_zip_paths),
        "physical_expected_zip_count": len(expected_paths),
        "extra_zip_paths_in_parent_dirs": extra_paths,
        "missing_zip_paths_in_parent_dirs": missing_paths,
        "no_extra_files": not extra_paths,
        "no_missing_files": not missing_paths,
    }


def inspect_zip_record(record: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    symbol = str(record["symbol"])
    day = str(record["date"])
    path = Path(str(record["local_zip_path"]))
    recorded_hash = str(record["sha256"])
    source_kind = str(record.get("source_kind"))
    require(path.exists(), f"ZIP missing: {path}")
    recomputed_hash = sha256_file(path)
    hash_match = recomputed_hash == recorded_hash
    require(hash_match, f"hash mismatch for {symbol} {day}")

    expected_inner = expected_csv(symbol, day)
    header: list[str] = []
    rows: list[list[str]] = []
    zip_member_names: list[str] = []
    try:
        with zipfile.ZipFile(path) as archive:
            zip_member_names = archive.namelist()
            traversal = any(not safe_zip_member(name) for name in zip_member_names)
            require(len(zip_member_names) <= MAX_ZIP_MEMBERS_PER_FILE, f"too many ZIP members: {path}")
            require(not traversal, f"ZIP path traversal risk: {path}")
            require(expected_inner in zip_member_names, f"expected inner CSV missing: {expected_inner}")
            with archive.open(expected_inner, "r") as raw:
                lines = (line.decode("utf-8-sig").rstrip("\r\n") for line in raw)
                reader = csv.reader(lines)
                header = next(reader)
                for _, row in zip(range(MAX_CSV_SAMPLE_ROWS_PER_FILE), reader):
                    rows.append(row)
    except (OSError, StopIteration, zipfile.BadZipFile) as exc:
        raise ValidationBlocked(f"ZIP/schema validation failed for {symbol} {day}: {exc}") from exc

    sample_rows_read = len(rows)
    require(sample_rows_read <= MAX_CSV_SAMPLE_ROWS_PER_FILE, f"sample row limit exceeded for {symbol} {day}")
    schema_match = header == EXPECTED_SCHEMA
    require(schema_match, f"schema mismatch for {symbol} {day}")
    observed_symbols = sorted({row[0] for row in rows if row})
    symbols_match = all(value == symbol for value in observed_symbols) if observed_symbols else True
    require(symbols_match, f"sampled symbol mismatch for {symbol} {day}")
    open_times: list[int] = []
    for row in rows:
        if len(row) > 8:
            try:
                open_times.append(int(row[8]))
            except ValueError:
                pass
    deltas = [right - left for left, right in zip(open_times, open_times[1:])]
    one_minute = (deltas and all(delta == 60_000 for delta in deltas)) or sample_rows_read < 2
    require(one_minute, f"sample interval mismatch for {symbol} {day}")

    hash_item = {
        "symbol": symbol,
        "date": day,
        "local_zip_path": str(path),
        "file_size_bytes": path.stat().st_size,
        "source_kind": source_kind,
        "recorded_sha256": recorded_hash,
        "recomputed_sha256": recomputed_hash,
        "hash_match": hash_match,
    }
    zip_schema_item = {
        "symbol": symbol,
        "date": day,
        "zip_path": str(path),
        "zip_path_exists": True,
        "zip_open_success": True,
        "zip_member_count": len(zip_member_names),
        "zip_member_count_within_limit": len(zip_member_names) <= MAX_ZIP_MEMBERS_PER_FILE,
        "zip_path_traversal_detected": False,
        "expected_inner_csv": expected_inner,
        "expected_inner_csv_present": True,
        "csv_header_read": True,
        "csv_sample_rows_read_count": sample_rows_read,
        "full_csv_read_performed": False,
        "observed_schema": header,
        "expected_schema_match": schema_match,
        "observed_symbols": observed_symbols,
        "observed_symbols_match_expected": symbols_match,
        "one_minute_interval_observed_from_sample": one_minute,
        "zip_member_names": zip_member_names,
    }
    return hash_item, zip_schema_item


def validate_files(records: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    reused_count, new_count = source_kind_counts(records)
    physical_file_report = validate_physical_extra_files(records)
    require(physical_file_report["no_extra_files"], "extra ZIP files detected in final parent directories")
    require(physical_file_report["no_missing_files"], "missing ZIP files detected in final parent directories")

    recomputed_hashes: list[dict[str, Any]] = []
    zip_schema_items: list[dict[str, Any]] = []
    for record in sorted(records, key=lambda item: (item["symbol"], item["date"])):
        hash_item, zip_schema_item = inspect_zip_record(record)
        recomputed_hashes.append(hash_item)
        zip_schema_items.append(zip_schema_item)

    all_paths_exist = all(item["zip_path_exists"] for item in zip_schema_items)
    all_reused_revalidated = (
        sum(1 for item in recomputed_hashes if item["source_kind"] == "REUSED_VALIDATED_BTC_FILE_SET" and item["hash_match"])
        == EXPECTED_REUSED_FILE_COUNT
    )
    all_hashes_recomputed = len(recomputed_hashes) == EXPECTED_TOTAL_PILOT_FILE_COUNT
    all_hashes_match = all(item["hash_match"] for item in recomputed_hashes)
    all_zip_open = all(item["zip_open_success"] for item in zip_schema_items)
    all_inner_csv = all(item["expected_inner_csv_present"] for item in zip_schema_items)
    all_schema = all(item["expected_schema_match"] for item in zip_schema_items)
    all_symbols = all(item["observed_symbols_match_expected"] for item in zip_schema_items)
    all_one_minute = all(item["one_minute_interval_observed_from_sample"] for item in zip_schema_items)
    max_sample_rows = max((item["csv_sample_rows_read_count"] for item in zip_schema_items), default=0)

    per_symbol_counts = {
        symbol: sum(1 for item in recomputed_hashes if item["symbol"] == symbol)
        for symbol in PILOT_SYMBOLS
    }
    hash_validation = {
        "all_downloaded_zip_paths_exist": all_paths_exist,
        "all_reused_files_revalidated": all_reused_revalidated,
        "all_hashes_recomputed": all_hashes_recomputed,
        "all_hashes_match_recorded": all_hashes_match,
        "recomputed_hash_count": len(recomputed_hashes),
        "reused_file_count_revalidated": reused_count,
        "new_download_file_count_revalidated": new_count,
        "per_symbol_hash_count": per_symbol_counts,
        "hashes": recomputed_hashes,
    }
    zip_schema_validation = {
        "all_zip_open_success": all_zip_open,
        "all_zip_member_counts_within_limit": all(item["zip_member_count_within_limit"] for item in zip_schema_items),
        "zip_path_traversal_detected_count": sum(1 for item in zip_schema_items if item["zip_path_traversal_detected"]),
        "all_expected_inner_csv_present": all_inner_csv,
        "all_expected_schema_match": all_schema,
        "all_observed_symbols_match_expected": all_symbols,
        "all_one_minute_interval_observed_from_samples": all_one_minute,
        "max_csv_sample_rows_read_per_file": max_sample_rows,
        "full_csv_read_performed": False,
        "zip_schema_items": zip_schema_items,
    }
    coverage_validation = {
        "pilot_symbol_count": len(PILOT_SYMBOLS),
        "pilot_symbols": PILOT_SYMBOLS,
        "date_range_start": DATE_RANGE_START.isoformat(),
        "date_range_end": DATE_RANGE_END.isoformat(),
        "expected_daily_file_count_per_symbol": EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "expected_total_pilot_file_count": EXPECTED_TOTAL_PILOT_FILE_COUNT,
        "observed_file_count": len(records),
        "expected_reused_file_count": EXPECTED_REUSED_FILE_COUNT,
        "expected_new_download_file_count": EXPECTED_NEW_DOWNLOAD_FILE_COUNT,
        "reused_file_count": reused_count,
        "new_download_file_count": new_count,
        "final_pilot_file_set_count": len(records),
        "missing_or_failed_file_count": 0,
        "coverage_gap_detected": False,
        "approved_manifest_validated": True,
        "no_extra_symbols": True,
        "no_missing_symbols": True,
        "no_extra_files": physical_file_report["no_extra_files"],
        "no_missing_files": physical_file_report["no_missing_files"],
        "physical_file_report": physical_file_report,
    }
    return hash_validation, zip_schema_validation, coverage_validation


def main() -> None:
    generated_at = utc_now()
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved validator module")

    exists: dict[str, bool] = {}
    valid_json: dict[str, bool] = {}
    artifacts = {label: load_json(path, label, exists, valid_json) for label, path in ARTIFACTS.items()}
    validate_artifact_chain(artifacts)
    records = validate_manifest_records(artifacts["hash_manifest"])
    hash_validation, zip_schema_validation, coverage_validation = validate_files(records)

    require(hash_validation["all_downloaded_zip_paths_exist"], "not all ZIP paths exist")
    require(hash_validation["all_reused_files_revalidated"], "not all reused files revalidated")
    require(hash_validation["all_hashes_recomputed"], "not all hashes recomputed")
    require(hash_validation["all_hashes_match_recorded"], "hash mismatch found")
    require(zip_schema_validation["all_zip_open_success"], "ZIP open failure found")
    require(zip_schema_validation["zip_path_traversal_detected_count"] == 0, "ZIP path traversal found")
    require(zip_schema_validation["all_expected_inner_csv_present"], "expected inner CSV missing")
    require(zip_schema_validation["all_expected_schema_match"], "schema mismatch found")
    require(zip_schema_validation["all_observed_symbols_match_expected"], "sampled symbol mismatch found")
    require(zip_schema_validation["all_one_minute_interval_observed_from_samples"], "sampled interval mismatch found")
    require(zip_schema_validation["max_csv_sample_rows_read_per_file"] <= MAX_CSV_SAMPLE_ROWS_PER_FILE, "sample row limit exceeded")

    validator_p0_count = 0
    validator_p1_count = 12
    replacement_checks = {
        "preflight_passed": True,
        "execution_artifacts_exist": all(exists.values()),
        "execution_artifacts_valid_json": all(valid_json.values()),
        "pilot_symbol_count_10": coverage_validation["pilot_symbol_count"] == len(PILOT_SYMBOLS),
        "approved_symbols_exact": coverage_validation["pilot_symbols"] == PILOT_SYMBOLS,
        "final_file_count_10530": coverage_validation["final_pilot_file_set_count"] == EXPECTED_TOTAL_PILOT_FILE_COUNT,
        "reused_file_count_1053": coverage_validation["reused_file_count"] == EXPECTED_REUSED_FILE_COUNT,
        "new_download_file_count_9477": coverage_validation["new_download_file_count"] == EXPECTED_NEW_DOWNLOAD_FILE_COUNT,
        "missing_failed_zero": coverage_validation["missing_or_failed_file_count"] == 0,
        "coverage_gap_false": coverage_validation["coverage_gap_detected"] is False,
        "approved_manifest_validated": coverage_validation["approved_manifest_validated"],
        "no_extra_symbols": coverage_validation["no_extra_symbols"],
        "no_missing_symbols": coverage_validation["no_missing_symbols"],
        "no_extra_files": coverage_validation["no_extra_files"],
        "no_missing_files": coverage_validation["no_missing_files"],
        "all_zip_paths_exist": hash_validation["all_downloaded_zip_paths_exist"],
        "all_reused_files_revalidated": hash_validation["all_reused_files_revalidated"],
        "all_hashes_recomputed": hash_validation["all_hashes_recomputed"],
        "all_hashes_match_recorded": hash_validation["all_hashes_match_recorded"],
        "all_zip_open_success": zip_schema_validation["all_zip_open_success"],
        "no_zip_path_traversal": zip_schema_validation["zip_path_traversal_detected_count"] == 0,
        "all_expected_inner_csv_present": zip_schema_validation["all_expected_inner_csv_present"],
        "all_expected_schema_match": zip_schema_validation["all_expected_schema_match"],
        "all_observed_symbols_match_expected": zip_schema_validation["all_observed_symbols_match_expected"],
        "all_one_minute_interval_observed": zip_schema_validation["all_one_minute_interval_observed_from_samples"],
        "sample_limit_respected": zip_schema_validation["max_csv_sample_rows_read_per_file"] <= MAX_CSV_SAMPLE_ROWS_PER_FILE,
        "full_csv_read_false": True,
        "no_new_download_api_browse": True,
        "no_build_aggregation": True,
        "no_full_universe_research_backtest_edge_claim": True,
        "safe_for_10_symbol_build_preview": True,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }
    replacement_checks_all_true = all(replacement_checks.values())
    require(replacement_checks_all_true, "replacement checks did not all pass")

    summary_payload = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": head,
        "historical_data_acquisition_okx_10_symbol_pilot_download_execution_validator_status": PASS_STATUS,
        "download_execution_validated": True,
        "pilot_symbol_count": len(PILOT_SYMBOLS),
        "pilot_symbols": PILOT_SYMBOLS,
        "date_range_start": DATE_RANGE_START.isoformat(),
        "date_range_end": DATE_RANGE_END.isoformat(),
        "expected_total_pilot_file_count": EXPECTED_TOTAL_PILOT_FILE_COUNT,
        "final_pilot_file_set_count": coverage_validation["final_pilot_file_set_count"],
        "reused_file_count": coverage_validation["reused_file_count"],
        "new_download_file_count": coverage_validation["new_download_file_count"],
        "missing_or_failed_file_count": coverage_validation["missing_or_failed_file_count"],
        "coverage_gap_detected": coverage_validation["coverage_gap_detected"],
        "approved_manifest_validated": coverage_validation["approved_manifest_validated"],
        "all_downloaded_zip_paths_exist": hash_validation["all_downloaded_zip_paths_exist"],
        "all_reused_files_revalidated": hash_validation["all_reused_files_revalidated"],
        "all_hashes_recomputed": hash_validation["all_hashes_recomputed"],
        "all_hashes_match_recorded": hash_validation["all_hashes_match_recorded"],
        "all_zip_open_success": zip_schema_validation["all_zip_open_success"],
        "all_expected_inner_csv_present": zip_schema_validation["all_expected_inner_csv_present"],
        "all_expected_schema_match": zip_schema_validation["all_expected_schema_match"],
        "all_observed_symbols_match_expected": zip_schema_validation["all_observed_symbols_match_expected"],
        "all_one_minute_interval_observed_from_samples": zip_schema_validation["all_one_minute_interval_observed_from_samples"],
        "max_csv_sample_rows_read_per_file": zip_schema_validation["max_csv_sample_rows_read_per_file"],
        "full_csv_read_performed": False,
        "new_download_performed_by_validator": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "safe_for_10_symbol_build_preview": True,
        "safe_for_full_universe_acquisition": False,
        "safe_for_research_backtest": False,
        "safe_for_edge_claim": False,
        "validator_p0_count": validator_p0_count,
        "validator_p1_count": validator_p1_count,
        "current_evidence_chain_quality_before_validator": BEFORE_QUALITY,
        "current_evidence_chain_quality_after_validator": AFTER_QUALITY,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": validator_p1_count,
        "dormant_repo_attention_count": EXPECTED_DORMANT_REPO_ATTENTION_COUNT,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "next_module": NEXT_MODULE_PASS,
        "derived_live_repo_post_check": PASS_STATUS,
        "derived_live_repo_post_check_reason": (
            "validated existing 10-symbol OKX pilot ZIP set only; recomputed 10530 SHA256 hashes, "
            "opened all ZIPs, confirmed expected inner CSVs, exact header schema, sampled symbol, "
            "and sampled 1m interval using at most five rows per CSV; no new download, API, browse, "
            "full CSV read, build, aggregation, full-universe readiness, research, backtest, edge, "
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

    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_download_execution_validator.json", bundle)
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_hash_validation_report.json", hash_validation)
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_zip_schema_validation_report.json", zip_schema_validation)
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_coverage_validation_report.json", coverage_validation)
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_download_execution_validator_summary.json", summary_payload)
    print(json.dumps(summary_payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except ValidationBlocked as exc:
        blocked_payload = {
            "module_name": MODULE_NAME,
            "generated_at_utc": utc_now(),
            "historical_data_acquisition_okx_10_symbol_pilot_download_execution_validator_status": BLOCKED_STATUS,
            "download_execution_validated": False,
            "pilot_symbol_count": len(PILOT_SYMBOLS),
            "pilot_symbols": PILOT_SYMBOLS,
            "date_range_start": DATE_RANGE_START.isoformat(),
            "date_range_end": DATE_RANGE_END.isoformat(),
            "expected_total_pilot_file_count": EXPECTED_TOTAL_PILOT_FILE_COUNT,
            "final_pilot_file_set_count": 0,
            "reused_file_count": 0,
            "new_download_file_count": 0,
            "missing_or_failed_file_count": EXPECTED_TOTAL_PILOT_FILE_COUNT,
            "coverage_gap_detected": True,
            "approved_manifest_validated": False,
            "all_downloaded_zip_paths_exist": False,
            "all_reused_files_revalidated": False,
            "all_hashes_recomputed": False,
            "all_hashes_match_recorded": False,
            "all_zip_open_success": False,
            "all_expected_inner_csv_present": False,
            "all_expected_schema_match": False,
            "all_observed_symbols_match_expected": False,
            "all_one_minute_interval_observed_from_samples": False,
            "max_csv_sample_rows_read_per_file": 0,
            "full_csv_read_performed": False,
            "new_download_performed_by_validator": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "okx_api_call_performed": False,
            "okx_browse_performed": False,
            "safe_for_10_symbol_build_preview": False,
            "safe_for_full_universe_acquisition": False,
            "safe_for_research_backtest": False,
            "safe_for_edge_claim": False,
            "validator_p0_count": 1,
            "validator_p1_count": 0,
            "current_evidence_chain_quality_before_validator": BEFORE_QUALITY,
            "current_evidence_chain_quality_after_validator": BEFORE_QUALITY,
            "active_p0_blocker_count": 1,
            "active_p1_attention_count": 0,
            "dormant_repo_attention_count": EXPECTED_DORMANT_REPO_ATTENTION_COUNT,
            "generic_runner_implementation_remains_blocked": True,
            "schema_or_config_created": False,
            "ordinary_selector_backlog_loop_reentry_allowed": False,
            "loop_remains_closed": True,
            "next_module": NEXT_MODULE_BLOCKED,
            "derived_live_repo_post_check": BLOCKED_STATUS,
            "replacement_checks_all_true": False,
            "blocked_reason": str(exc),
        }
        write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_download_execution_validator_summary.json", blocked_payload)
        print(json.dumps(blocked_payload, indent=2, sort_keys=True))
        raise SystemExit(1)
