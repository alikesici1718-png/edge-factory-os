from __future__ import annotations

import ast
import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_execution_validator_after_execution_v1"
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "ea05629"
PREVIOUS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_CHUNK_02_DOWNLOAD_EXECUTED_WITH_COVERAGE_GAPS_PENDING_VALIDATOR_NO_BUILD"
PASS_GAP_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_CHUNK_02_DOWNLOAD_VALIDATED_WITH_COVERAGE_GAPS_COVERAGE_SUMMARY_READY_NO_BUILD"
PASS_COMPLETE_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_CHUNK_02_DOWNLOAD_VALIDATED_COMPLETE_COVERAGE_SUMMARY_READY_NO_BUILD"
BLOCKED_STATUS = "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_CHUNK_02_DOWNLOAD_VALIDATION_FAILED"
NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_coverage_summary_after_validator_v1.py"
FAILED_NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_validation_blocked_record_v1.py"
AFTER_QUALITY_GAP = "HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_CHUNK_02_DOWNLOAD_VALIDATED_WITH_COVERAGE_GAPS_COVERAGE_SUMMARY_READY_NO_BUILD"
AFTER_QUALITY_COMPLETE = "HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_CHUNK_02_DOWNLOAD_VALIDATED_COMPLETE_COVERAGE_SUMMARY_READY_NO_BUILD"

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
EXECUTION_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_execution_after_preview_approval_v1"

ARTIFACTS = {
    "execution_report": EXECUTION_DIR / "historical_okx_full_usdt_swap_chunk_02_download_execution_report.json",
    "file_manifest": EXECUTION_DIR / "historical_okx_full_usdt_swap_chunk_02_download_file_manifest_after_execution.json",
    "gap_report": EXECUTION_DIR / "historical_okx_full_usdt_swap_chunk_02_download_gap_report.json",
    "reuse_report": EXECUTION_DIR / "historical_okx_full_usdt_swap_chunk_02_reuse_validation_report.json",
    "sha256_report": EXECUTION_DIR / "historical_okx_full_usdt_swap_chunk_02_sha256_report.json",
    "zip_inventory_report": EXECUTION_DIR / "historical_okx_full_usdt_swap_chunk_02_zip_inventory_report.json",
    "schema_sample_report": EXECUTION_DIR / "historical_okx_full_usdt_swap_chunk_02_schema_sample_report.json",
    "compliance_report": EXECUTION_DIR / "historical_okx_full_usdt_swap_chunk_02_download_execution_compliance_report.json",
    "execution_summary": EXECUTION_DIR / "historical_okx_full_usdt_swap_chunk_02_download_execution_summary.json",
}

REQUIRED_OUTPUTS = [
    "historical_okx_full_usdt_swap_chunk_02_download_execution_validator.json",
    "historical_okx_full_usdt_swap_chunk_02_download_validation_report.json",
    "historical_okx_full_usdt_swap_chunk_02_per_symbol_coverage_validation_report.json",
    "historical_okx_full_usdt_swap_chunk_02_gap_validation_report.json",
    "historical_okx_full_usdt_swap_chunk_02_reuse_validation_validator_report.json",
    "historical_okx_full_usdt_swap_chunk_02_sha256_validation_report.json",
    "historical_okx_full_usdt_swap_chunk_02_zip_schema_sample_validation_report.json",
    "historical_okx_full_usdt_swap_chunk_02_download_execution_validator_summary.json",
]

CHUNK_ID = "chunk_02"
CHUNK_SYMBOLS = [
    "APE-USDT-SWAP",
    "API3-USDT-SWAP",
    "APR-USDT-SWAP",
    "APT-USDT-SWAP",
    "AR-USDT-SWAP",
    "ARB-USDT-SWAP",
    "ARKM-USDT-SWAP",
    "ARM-USDT-SWAP",
    "ASTER-USDT-SWAP",
    "AT-USDT-SWAP",
    "ATH-USDT-SWAP",
    "ATOM-USDT-SWAP",
    "AUCTION-USDT-SWAP",
    "AVAX-USDT-SWAP",
    "AVGO-USDT-SWAP",
    "AVNT-USDT-SWAP",
    "AXS-USDT-SWAP",
    "AZTEC-USDT-SWAP",
    "BABY-USDT-SWAP",
    "BAND-USDT-SWAP",
]
EXPECTED_GAP_SYMBOLS = [
    "APR-USDT-SWAP",
    "ARKM-USDT-SWAP",
    "ARM-USDT-SWAP",
    "ASTER-USDT-SWAP",
    "AT-USDT-SWAP",
    "ATH-USDT-SWAP",
    "AUCTION-USDT-SWAP",
    "AVGO-USDT-SWAP",
    "AVNT-USDT-SWAP",
    "AZTEC-USDT-SWAP",
    "BABY-USDT-SWAP",
]
DATE_START = date(2023, 7, 1)
DATE_END = date(2026, 5, 18)
EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 1_053
EXPECTED_CHUNK_FILE_COUNT = 21_060
EXPECTED_FINAL_AVAILABLE_FILE_COUNT = 13_053
EXPECTED_MISSING_OR_FAILED_FILE_COUNT = 8_007
EXPECTED_REUSED_FILE_COUNT = 1_053
EXPECTED_SUCCESSFUL_NEW_DOWNLOAD_COUNT = 12_000
EXPECTED_NEW_DOWNLOAD_ATTEMPT_COUNT = 20_007
EXPECTED_FULL_COVERAGE_SYMBOL_COUNT = 9
EXPECTED_GAP_SYMBOL_COUNT = 11
MAX_CSV_SAMPLE_ROWS_PER_FILE = 5


class ValidationBlocked(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationBlocked(message)


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
        raw = (REPO_ROOT / rel).read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
        try:
            ast.parse(raw.decode("utf-8"), filename=rel)
        except Exception as exc:
            syntax_errors.append({"path": rel, "error": repr(exc)})
    return {
        "tracked_python_count": len(files),
        "syntax_error_count": len(syntax_errors),
        "bom_error_count": len(bom_errors),
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
    }


def load_json(path: Path, label: str, exists: dict[str, bool], valid_json: dict[str, bool]) -> dict[str, Any]:
    exists[label] = path.exists()
    require(path.exists(), f"missing artifact {label}: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        valid_json[label] = False
        raise ValidationBlocked(f"invalid JSON artifact {label}: {exc}") from exc
    valid_json[label] = True
    require(isinstance(payload, dict), f"artifact {label} is not a JSON object")
    return payload


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def date_values() -> list[str]:
    values: list[str] = []
    current = DATE_START
    while current <= DATE_END:
        values.append(current.isoformat())
        current += timedelta(days=1)
    return values


def load_artifacts() -> tuple[dict[str, dict[str, Any]], dict[str, bool], dict[str, bool]]:
    exists: dict[str, bool] = {}
    valid_json: dict[str, bool] = {}
    artifacts = {label: load_json(path, label, exists, valid_json) for label, path in ARTIFACTS.items()}
    return artifacts, exists, valid_json


def validate_preconditions(py_state: dict[str, Any]) -> dict[str, bool]:
    head = run_git(["rev-parse", "HEAD"])
    checks = {
        "current_head_guard_passed": head.startswith(EXPECTED_HEAD),
        "current_path_guard_passed": APPROVED_TOOL.exists(),
        "repo_has_only_approved_tool_change": repo_has_only_this_tool_change(),
        "python_syntax_bom_clean": py_state["syntax_error_count"] == 0 and py_state["bom_error_count"] == 0,
    }
    require(all(checks.values()), f"precondition failure: {checks}")
    return checks


def validate_execution_summary(summary: dict[str, Any]) -> dict[str, bool]:
    checks = {
        "previous_status_passed": summary.get("historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_execution_status") == PREVIOUS_STATUS,
        "download_execution_performed": summary.get("download_execution_performed") is True,
        "current_next_module_matches": summary.get("next_module") == REQUESTED_MODULE,
        "chunk_id_valid": summary.get("chunk_id") == CHUNK_ID,
        "chunk_symbol_count_valid": summary.get("chunk_symbol_count") == len(CHUNK_SYMBOLS),
        "expected_file_count_valid": summary.get("expected_chunk_file_count") == EXPECTED_CHUNK_FILE_COUNT,
        "planned_file_count_valid": summary.get("planned_file_count") == EXPECTED_CHUNK_FILE_COUNT,
        "final_available_count_valid": summary.get("final_available_file_count") == EXPECTED_FINAL_AVAILABLE_FILE_COUNT,
        "missing_failed_count_valid": summary.get("missing_or_failed_file_count") == EXPECTED_MISSING_OR_FAILED_FILE_COUNT,
        "count_reconciliation_pass": summary.get("final_available_file_count", -1) + summary.get("missing_or_failed_file_count", -1) == summary.get("planned_file_count"),
        "reused_count_valid": summary.get("reused_file_count") == EXPECTED_REUSED_FILE_COUNT,
        "successful_new_count_valid": summary.get("successful_new_download_count") == EXPECTED_SUCCESSFUL_NEW_DOWNLOAD_COUNT,
        "new_download_attempt_count_valid": summary.get("new_download_attempt_count") == EXPECTED_NEW_DOWNLOAD_ATTEMPT_COUNT,
        "available_count_matches_reuse_plus_new": summary.get("reused_file_count", -1) + summary.get("successful_new_download_count", -1) == summary.get("final_available_file_count"),
        "coverage_gap_detected": summary.get("coverage_gap_detected") is True,
        "full_symbol_count_valid": summary.get("symbols_with_full_file_coverage_count") == EXPECTED_FULL_COVERAGE_SYMBOL_COUNT,
        "gap_symbol_count_valid": summary.get("symbols_with_coverage_gaps_count") == EXPECTED_GAP_SYMBOL_COUNT,
        "expected_gap_symbols_valid": summary.get("symbols_with_coverage_gaps") == EXPECTED_GAP_SYMBOLS,
        "hashes_available_flag": summary.get("all_hashes_computed_or_revalidated") is True,
        "zip_open_available_flag": summary.get("all_available_zips_open_success") is True,
        "no_zip_path_traversal_flag": summary.get("any_zip_path_traversal_detected") is False,
        "inner_csv_available_flag": summary.get("all_available_expected_inner_csv_present") is True,
        "schema_available_flag": summary.get("all_available_expected_schema_match") is True,
        "sample_symbol_available_flag": summary.get("all_available_observed_symbols_match_expected") is True,
        "sample_limit_valid": summary.get("max_csv_sample_rows_read_per_file") == MAX_CSV_SAMPLE_ROWS_PER_FILE,
        "no_full_csv_read": summary.get("full_csv_read_performed") is False,
        "no_build_ready_claim": summary.get("files_marked_build_ready") is False,
        "no_acquisition_ready_claim": summary.get("source_manifest_acquisition_ready") is False,
        "no_full_universe_allowed": summary.get("full_universe_acquisition_allowed_now") is False,
        "no_data_build_allowed": summary.get("data_build_allowed_now") is False,
        "no_edge_allowed": summary.get("strategy_backtest_edge_allowed_now") is False,
        "no_api": summary.get("okx_api_call_performed") is False,
        "no_browse": summary.get("okx_browse_performed") is False,
        "no_data_build": summary.get("data_build_performed") is False,
        "no_aggregation": summary.get("aggregation_performed_now") is False,
        "no_research_backtest_claim": summary.get("output_valid_for_research_backtest") is False,
        "no_edge_claim": summary.get("output_valid_for_edge_claim") is False,
        "no_full_universe_ready_claim": summary.get("safe_for_full_universe_acquisition") is False and summary.get("broad_acquisition_ready") is False,
        "execution_replacement_checks_true": summary.get("replacement_checks_all_true") is True,
    }
    require(all(checks.values()), f"execution summary validation failure: {checks}")
    return checks


def extract_lists(artifacts: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    lists = {
        "file_manifest": artifacts["file_manifest"].get("file_manifest", []),
        "gaps": artifacts["gap_report"].get("coverage_gaps", []),
        "reuse_records": artifacts["reuse_report"].get("reuse_validation_records", []),
        "sha256_records": artifacts["sha256_report"].get("sha256_records", []),
        "zip_inventory": artifacts["zip_inventory_report"].get("zip_inventory", []),
        "schema_samples": artifacts["schema_sample_report"].get("schema_samples", []),
        "download_results": artifacts["execution_report"].get("download_results", []),
    }
    for label, rows in lists.items():
        require(isinstance(rows, list), f"{label} is not a list")
        require(all(isinstance(row, dict) for row in rows), f"{label} contains non-object rows")
    return lists


def key(row: dict[str, Any]) -> tuple[str, str]:
    return str(row.get("symbol")), str(row.get("date"))


def validate_manifest_and_counts(lists: dict[str, list[dict[str, Any]]], execution_summary: dict[str, Any]) -> dict[str, Any]:
    manifest = lists["file_manifest"]
    gaps = lists["gaps"]
    sha_records = lists["sha256_records"]
    zip_records = lists["zip_inventory"]
    schema_records = lists["schema_samples"]
    download_results = lists["download_results"]
    allowed_symbols = set(CHUNK_SYMBOLS)
    allowed_dates = set(date_values())
    require(len(manifest) == EXPECTED_CHUNK_FILE_COUNT, "file manifest row count mismatch")
    manifest_keys = [key(row) for row in manifest]
    require(len(set(manifest_keys)) == EXPECTED_CHUNK_FILE_COUNT, "duplicate symbol/date rows in file manifest")
    expected_keys = {(symbol, day) for symbol in CHUNK_SYMBOLS for day in allowed_dates}
    require(set(manifest_keys) == expected_keys, "manifest symbol/date universe mismatch")
    require(all(row.get("chunk_id") == CHUNK_ID for row in manifest), "manifest contains unapproved chunk_id")
    require(all(row.get("symbol") in allowed_symbols for row in manifest), "manifest contains unapproved symbol")
    require(all(row.get("date") in allowed_dates for row in manifest), "manifest contains unapproved date")
    require(all(row.get("build_ready") is False and row.get("acquisition_ready") is False for row in manifest), "manifest has build/acquisition-ready row")

    available_manifest = [row for row in manifest if row.get("available_for_validator") is True]
    gap_manifest = [row for row in manifest if row.get("coverage_gap") is True]
    require(len(available_manifest) == EXPECTED_FINAL_AVAILABLE_FILE_COUNT, "available manifest count mismatch")
    require(len(gap_manifest) == EXPECTED_MISSING_OR_FAILED_FILE_COUNT, "gap manifest count mismatch")
    require(len(gaps) == EXPECTED_MISSING_OR_FAILED_FILE_COUNT, "gap report row count mismatch")
    require({key(row) for row in gaps} == {key(row) for row in gap_manifest}, "gap report and manifest gap keys mismatch")
    require(len(sha_records) == EXPECTED_CHUNK_FILE_COUNT, "sha256 record count mismatch")
    require(len(zip_records) == EXPECTED_CHUNK_FILE_COUNT, "zip inventory count mismatch")
    require(len(schema_records) == EXPECTED_CHUNK_FILE_COUNT, "schema sample count mismatch")
    require({key(row) for row in sha_records} == expected_keys, "sha keys mismatch")
    require({key(row) for row in zip_records} == expected_keys, "zip keys mismatch")
    require({key(row) for row in schema_records} == expected_keys, "schema keys mismatch")

    available_keys = {key(row) for row in available_manifest}
    gap_keys = {key(row) for row in gap_manifest}
    require(available_keys.isdisjoint(gap_keys), "available and gap keys overlap")
    sha_by_key = {key(row): row for row in sha_records}
    zip_by_key = {key(row): row for row in zip_records}
    schema_by_key = {key(row): row for row in schema_records}
    require(all(sha_by_key[item].get("hash_computed_or_revalidated") is True for item in available_keys), "available file without hash")
    require(all(isinstance(sha_by_key[item].get("sha256"), str) and len(str(sha_by_key[item]["sha256"])) == 64 for item in available_keys), "available file invalid sha256")
    require(all(zip_by_key[item].get("zip_open_success") is True for item in available_keys), "available file ZIP did not open")
    require(all(zip_by_key[item].get("path_traversal_detected") is False for item in available_keys), "available file path traversal detected")
    require(all(zip_by_key[item].get("expected_inner_csv_present") is True for item in available_keys), "available file missing expected inner CSV")
    require(all(schema_by_key[item].get("schema_match") is True for item in available_keys), "available file schema mismatch")
    require(all(schema_by_key[item].get("observed_symbols_match_expected") is True for item in available_keys), "available file sampled symbol mismatch")
    require(all(int(schema_by_key[item].get("sample_rows_read", 0)) <= MAX_CSV_SAMPLE_ROWS_PER_FILE for item in available_keys), "sample row limit exceeded")
    require(all(sha_by_key[item].get("hash_computed_or_revalidated") is False for item in gap_keys), "gap file unexpectedly has hash flag")
    require(all(zip_by_key[item].get("zip_open_success") is False for item in gap_keys), "gap file unexpectedly opened ZIP")
    require(all(schema_by_key[item].get("schema_match") is False for item in gap_keys), "gap file unexpectedly has schema match")

    status_counts = Counter((row.get("download_attempted"), row.get("download_succeeded"), row.get("coverage_gap"), row.get("source_kind")) for row in manifest)
    reused_file_count = sum(1 for row in manifest if row.get("source_kind") == "REUSE_CANDIDATE_ALREADY_VALIDATED_PILOT_FILE_REVALIDATED" and row.get("available_for_validator") is True)
    successful_new_download_count = sum(
        1
        for row in manifest
        if row.get("source_kind") in {"DOWNLOADED_THIS_RUN", "EXISTING_APPROVED_CHUNK_02_FILE"}
        and row.get("available_for_validator") is True
    )
    failed_download_attempt_count = sum(1 for row in manifest if row.get("download_attempted") is True and row.get("download_succeeded") is False)
    missing_coverage_gap_count = len(gap_manifest)
    not_attempted_or_preclassified_gap_count = sum(1 for row in gap_manifest if row.get("download_attempted") is not True)
    new_download_attempt_count = int(execution_summary.get("new_download_attempt_count", -1))
    download_result_row_count = len(download_results)
    require(new_download_attempt_count == EXPECTED_NEW_DOWNLOAD_ATTEMPT_COUNT, "top-level new download attempt count mismatch")
    require(new_download_attempt_count == successful_new_download_count + failed_download_attempt_count, "new download attempts do not reconcile with success plus failure counts")
    require(download_result_row_count == new_download_attempt_count, "download result rows do not reconcile with new download attempts")
    require(failed_download_attempt_count == missing_coverage_gap_count, "failed attempts and missing gaps do not reconcile")
    require(not_attempted_or_preclassified_gap_count == 0, "silent/preclassified gaps found without attempt")
    require(reused_file_count == EXPECTED_REUSED_FILE_COUNT, "reused file count mismatch")
    require(successful_new_download_count == EXPECTED_SUCCESSFUL_NEW_DOWNLOAD_COUNT, "successful new download count mismatch")
    require(reused_file_count + successful_new_download_count == EXPECTED_FINAL_AVAILABLE_FILE_COUNT, "reuse plus new does not equal available")

    return {
        "available_keys": available_keys,
        "gap_keys": gap_keys,
        "status_counts": {str(item): count for item, count in status_counts.items()},
        "reused_file_count": reused_file_count,
        "successful_new_download_count": successful_new_download_count,
        "new_download_attempt_count": new_download_attempt_count,
        "new_download_attempt_count_valid": True,
        "not_attempted_or_preclassified_gap_count": not_attempted_or_preclassified_gap_count,
        "failed_download_attempt_count": failed_download_attempt_count,
        "missing_coverage_gap_count": missing_coverage_gap_count,
        "download_result_row_count": download_result_row_count,
    }


def classify_symbols(lists: dict[str, list[dict[str, Any]]]) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    manifest = lists["file_manifest"]
    by_symbol: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in manifest:
        by_symbol[str(row["symbol"])].append(row)
    classifications: list[dict[str, Any]] = []
    full_symbols: list[str] = []
    gap_symbols: list[str] = []
    for symbol in CHUNK_SYMBOLS:
        rows = sorted(by_symbol[symbol], key=lambda row: row["date"])
        available_rows = [row for row in rows if row.get("available_for_validator") is True]
        gap_rows = [row for row in rows if row.get("coverage_gap") is True]
        coverage_complete = len(available_rows) == EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL and not gap_rows
        if coverage_complete:
            full_symbols.append(symbol)
        else:
            gap_symbols.append(symbol)
        classifications.append(
            {
                "symbol": symbol,
                "planned_file_count": len(rows),
                "available_file_count": len(available_rows),
                "missing_or_failed_file_count": len(gap_rows),
                "coverage_complete": coverage_complete,
                "coverage_gap_detected": bool(gap_rows),
                "first_available_date": available_rows[0]["date"] if available_rows else None,
                "last_available_date": available_rows[-1]["date"] if available_rows else None,
                "full_near_3y_archive_coverage_validated": coverage_complete,
                "download_validated_for_available_files": all(row.get("available_for_validator") is True for row in available_rows),
                "build_ready": False,
                "acquisition_ready": False,
            }
        )
    require(gap_symbols == EXPECTED_GAP_SYMBOLS, "symbol gap classification mismatch")
    require(len(full_symbols) == EXPECTED_FULL_COVERAGE_SYMBOL_COUNT, "full coverage symbol count mismatch")
    require(len(gap_symbols) == EXPECTED_GAP_SYMBOL_COUNT, "gap symbol count mismatch")
    return classifications, full_symbols, gap_symbols


def validate_compliance(artifacts: dict[str, dict[str, Any]]) -> dict[str, bool]:
    compliance = artifacts["compliance_report"]
    checks = {
        "validator_new_download_false": True,
        "no_full_csv_read": compliance.get("full_csv_read_performed") is False,
        "no_api": compliance.get("okx_api_call_performed") is False,
        "no_browse": compliance.get("okx_browse_performed") is False,
        "no_build": compliance.get("data_build_performed") is False,
        "no_aggregation": compliance.get("aggregation_performed_now") is False,
        "no_build_ready": compliance.get("files_marked_build_ready") is False,
        "no_acquisition_ready": compliance.get("source_manifest_acquisition_ready") is False,
        "no_research_backtest": compliance.get("output_valid_for_research_backtest") is False,
        "no_edge": compliance.get("output_valid_for_edge_claim") is False,
        "no_runtime": compliance.get("runtime_touched") is not True,
        "no_capital": compliance.get("capital_changed") is not True,
        "no_live": compliance.get("live_or_real_orders") is not True,
        "no_schema_config": compliance.get("schema_or_config_created") is not True,
    }
    require(all(checks.values()), f"compliance validation failure: {checks}")
    return checks


def build_common_summary(
    py_state: dict[str, Any],
    execution_summary: dict[str, Any],
    count_state: dict[str, Any],
    full_symbols: list[str],
    gap_symbols: list[str],
    replacement_checks: dict[str, bool],
) -> dict[str, Any]:
    coverage_gap_detected = execution_summary["coverage_gap_detected"] is True
    status = PASS_GAP_STATUS if coverage_gap_detected else PASS_COMPLETE_STATUS
    quality = AFTER_QUALITY_GAP if coverage_gap_detected else AFTER_QUALITY_COMPLETE
    near_3y_complete = full_symbols
    return {
        "historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_execution_validator_status": status,
        "download_execution_validated": True,
        "chunk_id": CHUNK_ID,
        "chunk_symbol_count": len(CHUNK_SYMBOLS),
        "expected_chunk_file_count": EXPECTED_CHUNK_FILE_COUNT,
        "expected_chunk_02_file_count": EXPECTED_CHUNK_FILE_COUNT,
        "planned_file_count": EXPECTED_CHUNK_FILE_COUNT,
        "final_available_file_count": EXPECTED_FINAL_AVAILABLE_FILE_COUNT,
        "missing_or_failed_file_count": EXPECTED_MISSING_OR_FAILED_FILE_COUNT,
        "count_reconciliation_pass": True,
        "reused_file_count": count_state["reused_file_count"],
        "successful_new_download_count": count_state["successful_new_download_count"],
        "available_file_count_matches_reuse_plus_new_download": True,
        "new_download_attempt_count": execution_summary["new_download_attempt_count"],
        "new_download_attempt_count_valid": count_state["new_download_attempt_count_valid"],
        "not_attempted_or_preclassified_gap_count": count_state["not_attempted_or_preclassified_gap_count"],
        "failed_download_attempt_count": count_state["failed_download_attempt_count"],
        "missing_coverage_gap_count": count_state["missing_coverage_gap_count"],
        "coverage_gap_detected": True,
        "symbols_with_full_file_coverage_count": len(full_symbols),
        "symbols_with_full_file_coverage": full_symbols,
        "symbols_with_coverage_gaps_count": len(gap_symbols),
        "symbols_with_coverage_gaps": gap_symbols,
        "all_hashes_computed_or_revalidated": True,
        "all_available_zips_open_success": True,
        "any_zip_path_traversal_detected": False,
        "all_available_expected_inner_csv_present": True,
        "all_available_expected_schema_match": True,
        "all_available_observed_symbols_match_expected": True,
        "max_csv_sample_rows_read_per_file": MAX_CSV_SAMPLE_ROWS_PER_FILE,
        "full_csv_read_performed": False,
        "new_download_performed_by_validator": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "data_build_performed_by_validator": False,
        "aggregation_performed_by_validator": False,
        "files_marked_build_ready": False,
        "source_manifest_acquisition_ready": False,
        "near_3y_eligible_symbol_count_after_validator": len(near_3y_complete),
        "symbols_near_3y_download_coverage_complete": near_3y_complete,
        "chunk_download_validated_for_coverage_summary": True,
        "chunk_02_download_validated_for_coverage_summary": True,
        "full_universe_acquisition_allowed_now": False,
        "data_build_allowed_now": False,
        "strategy_backtest_edge_allowed_now": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "validator_p0_count": 0,
        "validator_p1_count": max(int(execution_summary.get("active_p1_attention_count", 0)), 505),
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": max(int(execution_summary.get("active_p1_attention_count", 0)), 505),
        "dormant_repo_attention_count": 716,
        "current_evidence_chain_quality_after_validator": quality,
        "next_module": NEXT_MODULE,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": all(replacement_checks.values()),
        "tracked_python_count": py_state["tracked_python_count"],
        "syntax_error_count": py_state["syntax_error_count"],
        "bom_error_count": py_state["bom_error_count"],
        "created_at_utc": utc_now(),
    }


def run_validator() -> dict[str, Any]:
    py_state = tracked_python_validation()
    precondition_checks = validate_preconditions(py_state)
    artifacts, artifact_exists, artifact_valid_json = load_artifacts()
    summary_checks = validate_execution_summary(artifacts["execution_summary"])
    lists = extract_lists(artifacts)
    count_state = validate_manifest_and_counts(lists, artifacts["execution_summary"])
    per_symbol, full_symbols, gap_symbols = classify_symbols(lists)
    compliance_checks = validate_compliance(artifacts)
    replacement_checks = {
        **precondition_checks,
        "artifacts_exist": all(artifact_exists.values()),
        "artifacts_valid_json": all(artifact_valid_json.values()),
        **summary_checks,
        "manifest_counts_reconciled": True,
        "gaps_explicit_not_silent": count_state["not_attempted_or_preclassified_gap_count"] == 0,
        "counter_semantics_reconciled": (
            count_state["failed_download_attempt_count"] == count_state["missing_coverage_gap_count"]
            and count_state["new_download_attempt_count_valid"]
        ),
        "per_symbol_classification_created": True,
        "near_3y_complete_symbols_are_full_coverage_only": len(full_symbols) == EXPECTED_FULL_COVERAGE_SYMBOL_COUNT,
        **compliance_checks,
        "next_module_is_coverage_summary": True,
    }
    common = build_common_summary(py_state, artifacts["execution_summary"], count_state, full_symbols, gap_symbols, replacement_checks)
    require(common["replacement_checks_all_true"], f"replacement checks failed: {replacement_checks}")
    validation_report = {
        **common,
        "artifact_type": "download_validation_report",
        "artifact_exists_by_label": artifact_exists,
        "artifact_valid_json_by_label": artifact_valid_json,
        "counter_status_counts": count_state["status_counts"],
    }
    per_symbol_report = {
        **common,
        "artifact_type": "per_symbol_coverage_validation_report",
        "per_symbol_coverage": per_symbol,
    }
    gap_report = {
        **common,
        "artifact_type": "gap_validation_report",
        "validated_gap_count": len(lists["gaps"]),
        "gap_records": lists["gaps"],
    }
    reuse_report = {
        **common,
        "artifact_type": "reuse_validation_validator_report",
        "reuse_records_validated_count": len(lists["reuse_records"]),
        "reuse_records": lists["reuse_records"],
    }
    sha_report = {
        **common,
        "artifact_type": "sha256_validation_report",
        "available_sha256_record_count": len(count_state["available_keys"]),
        "sha256_records_total": len(lists["sha256_records"]),
    }
    zip_schema_report = {
        **common,
        "artifact_type": "zip_schema_sample_validation_report",
        "zip_inventory_record_count": len(lists["zip_inventory"]),
        "schema_sample_record_count": len(lists["schema_samples"]),
    }
    validator_bundle = {
        **common,
        "artifact_type": "download_execution_validator",
        "validation_report": validation_report,
        "per_symbol_coverage_validation": per_symbol,
    }
    summary = {
        **common,
        "artifact_type": "download_execution_validator_summary",
        "artifact_count": len(REQUIRED_OUTPUTS),
    }
    outputs = {
        "historical_okx_full_usdt_swap_chunk_02_download_execution_validator.json": validator_bundle,
        "historical_okx_full_usdt_swap_chunk_02_download_validation_report.json": validation_report,
        "historical_okx_full_usdt_swap_chunk_02_per_symbol_coverage_validation_report.json": per_symbol_report,
        "historical_okx_full_usdt_swap_chunk_02_gap_validation_report.json": gap_report,
        "historical_okx_full_usdt_swap_chunk_02_reuse_validation_validator_report.json": reuse_report,
        "historical_okx_full_usdt_swap_chunk_02_sha256_validation_report.json": sha_report,
        "historical_okx_full_usdt_swap_chunk_02_zip_schema_sample_validation_report.json": zip_schema_report,
        "historical_okx_full_usdt_swap_chunk_02_download_execution_validator_summary.json": summary,
    }
    for name, payload in outputs.items():
        write_json(OUTPUT_DIR / name, payload)
    missing = [name for name in REQUIRED_OUTPUTS if not (OUTPUT_DIR / name).exists()]
    require(not missing, f"missing validator outputs: {missing}")
    return summary


def blocked_payload(message: str) -> dict[str, Any]:
    return {
        "historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_execution_validator_status": BLOCKED_STATUS,
        "download_execution_validated": False,
        "blocked_reason": message,
        "chunk_id": CHUNK_ID,
        "planned_file_count": 0,
        "final_available_file_count": 0,
        "missing_or_failed_file_count": EXPECTED_CHUNK_FILE_COUNT,
        "count_reconciliation_pass": False,
        "reused_file_count": 0,
        "successful_new_download_count": 0,
        "available_file_count_matches_reuse_plus_new_download": False,
        "new_download_attempt_count": 0,
        "new_download_attempt_count_valid": False,
        "not_attempted_or_preclassified_gap_count": 0,
        "failed_download_attempt_count": 0,
        "missing_coverage_gap_count": 0,
        "coverage_gap_detected": True,
        "symbols_with_full_file_coverage_count": 0,
        "symbols_with_full_file_coverage": [],
        "symbols_with_coverage_gaps_count": len(CHUNK_SYMBOLS),
        "symbols_with_coverage_gaps": CHUNK_SYMBOLS,
        "all_hashes_computed_or_revalidated": False,
        "all_available_zips_open_success": False,
        "any_zip_path_traversal_detected": False,
        "all_available_expected_inner_csv_present": False,
        "all_available_expected_schema_match": False,
        "all_available_observed_symbols_match_expected": False,
        "full_csv_read_performed": False,
        "new_download_performed_by_validator": False,
        "data_build_performed_by_validator": False,
        "aggregation_performed_by_validator": False,
        "near_3y_eligible_symbol_count_after_validator": 0,
        "symbols_near_3y_download_coverage_complete": [],
        "chunk_download_validated_for_coverage_summary": False,
        "chunk_02_download_validated_for_coverage_summary": False,
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 505,
        "current_evidence_chain_quality_after_validator": "CHUNK_02_DOWNLOAD_VALIDATION_FAILED_CLOSED",
        "next_module": FAILED_NEXT_MODULE,
        "replacement_checks_all_true": False,
        "created_at_utc": utc_now(),
    }


def main() -> int:
    try:
        summary = run_validator()
    except Exception as exc:
        blocked = blocked_payload(type(exc).__name__ + ": " + str(exc))
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        write_json(OUTPUT_DIR / "historical_okx_full_usdt_swap_chunk_02_download_execution_validator_summary.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
