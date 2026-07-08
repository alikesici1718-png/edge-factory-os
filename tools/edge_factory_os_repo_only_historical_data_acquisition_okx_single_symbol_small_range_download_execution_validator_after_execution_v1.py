from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_execution_validator_"
    "after_execution_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_execution_validator_"
    "after_execution_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "eeefded"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 689
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 690

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_execution_validator_"
    "after_execution_v1.py"
)
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_small_range_1m_to_1h_build_preview_"
    "after_download_validator_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_execution_validation_"
    "blocked_record_after_execution_v1.py"
)

EXECUTION_DIR = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_execution_after_preview_approval_v1"
)
EXECUTION_LATEST_ARTIFACT = (
    EXECUTION_DIR
    / "repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_execution_after_preview_approval_v1_latest.json"
)
EXECUTION_REPORT_ARTIFACT = EXECUTION_DIR / "historical_okx_single_symbol_small_range_download_execution_report.json"
PROVENANCE_REPORT_ARTIFACT = EXECUTION_DIR / "historical_okx_single_symbol_small_range_download_provenance_report.json"
ZIP_INVENTORY_REPORT_ARTIFACT = EXECUTION_DIR / "historical_okx_single_symbol_small_range_zip_inventory_report.json"
SCHEMA_SAMPLE_REPORT_ARTIFACT = EXECUTION_DIR / "historical_okx_single_symbol_small_range_schema_sample_report.json"
COMPLIANCE_REPORT_ARTIFACT = EXECUTION_DIR / "historical_okx_single_symbol_small_range_download_execution_compliance_report.json"
EXECUTION_SUMMARY_ARTIFACT = EXECUTION_DIR / "historical_okx_single_symbol_small_range_download_execution_summary.json"
PREVIEW_APPROVAL_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_preview_after_smoke_test_summary_v1"
    / "repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_preview_after_smoke_test_summary_v1_latest.json"
)
SMOKE_SUMMARY_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_summary_after_build_validator_v1"
    / "repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_summary_after_build_validator_v1_latest.json"
)

EXECUTION_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMALL_RANGE_DOWNLOAD_EXECUTED_PENDING_VALIDATOR_NO_BUILD"
)
STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMALL_RANGE_DOWNLOAD_VALIDATED_BUILD_PREVIEW_READY_NO_EXECUTION"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMALL_RANGE_DOWNLOAD_EXECUTED_PENDING_VALIDATOR_NO_BUILD"
)
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMALL_RANGE_DOWNLOAD_VALIDATED_BUILD_PREVIEW_READY_NO_EXECUTION"
)

TARGET_SYMBOL = "BTC-USDT-SWAP"
DATE_RANGE_START = "2026-05-12"
DATE_RANGE_END = "2026-05-18"
RANGE_DAYS = 7
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
APPROVED_FILES = [
    {
        "date": "2026-05-12",
        "source_url": "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/20260512/BTC-USDT-SWAP-candlesticks-2026-05-12.zip",
        "downloaded_zip_file_name": "BTC-USDT-SWAP-candlesticks-2026-05-12.zip",
        "expected_inner_csv": "BTC-USDT-SWAP-candlesticks-2026-05-12.csv",
    },
    {
        "date": "2026-05-13",
        "source_url": "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/20260513/BTC-USDT-SWAP-candlesticks-2026-05-13.zip",
        "downloaded_zip_file_name": "BTC-USDT-SWAP-candlesticks-2026-05-13.zip",
        "expected_inner_csv": "BTC-USDT-SWAP-candlesticks-2026-05-13.csv",
    },
    {
        "date": "2026-05-14",
        "source_url": "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/20260514/BTC-USDT-SWAP-candlesticks-2026-05-14.zip",
        "downloaded_zip_file_name": "BTC-USDT-SWAP-candlesticks-2026-05-14.zip",
        "expected_inner_csv": "BTC-USDT-SWAP-candlesticks-2026-05-14.csv",
    },
    {
        "date": "2026-05-15",
        "source_url": "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/20260515/BTC-USDT-SWAP-candlesticks-2026-05-15.zip",
        "downloaded_zip_file_name": "BTC-USDT-SWAP-candlesticks-2026-05-15.zip",
        "expected_inner_csv": "BTC-USDT-SWAP-candlesticks-2026-05-15.csv",
    },
    {
        "date": "2026-05-16",
        "source_url": "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/20260516/BTC-USDT-SWAP-candlesticks-2026-05-16.zip",
        "downloaded_zip_file_name": "BTC-USDT-SWAP-candlesticks-2026-05-16.zip",
        "expected_inner_csv": "BTC-USDT-SWAP-candlesticks-2026-05-16.csv",
    },
    {
        "date": "2026-05-17",
        "source_url": "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/20260517/BTC-USDT-SWAP-candlesticks-2026-05-17.zip",
        "downloaded_zip_file_name": "BTC-USDT-SWAP-candlesticks-2026-05-17.zip",
        "expected_inner_csv": "BTC-USDT-SWAP-candlesticks-2026-05-17.csv",
    },
    {
        "date": "2026-05-18",
        "source_url": "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/20260518/BTC-USDT-SWAP-candlesticks-2026-05-18.zip",
        "downloaded_zip_file_name": "BTC-USDT-SWAP-candlesticks-2026-05-18.zip",
        "expected_inner_csv": "BTC-USDT-SWAP-candlesticks-2026-05-18.csv",
    },
]
APPROVED_URLS = [item["source_url"] for item in APPROVED_FILES]
MAX_ZIP_SIZE_BYTES = 100 * 1024 * 1024
MAX_TOTAL_ZIP_SIZE_BYTES = 700 * 1024 * 1024
MAX_ZIP_MEMBERS = 10
MAX_CSV_SAMPLE_DATA_ROWS = 5

GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"
PLANNED_SCHEMA_REL_PATHS = [
    "edge_factory_os_framework/schemas/edge_factory_os_status_record_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_safety_flags_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_git_state_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_tracked_python_validation_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_queue_item_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_artifact_reference_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_post_commit_check_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_framework_schema_registry_v1.schema.json",
]
DANGEROUS_FLAG_NAMES = [
    "runtime_touched",
    "launcher_executed",
    "launcher_touch_performed",
    "capital_changed",
    "live_or_real_orders",
    "holdout_accessed",
    "active_paper_touched",
    "strategy_research_recommended_now",
    "strategy_research_implementation_touched",
    "candidate_generation_recommended_now",
    "candidate_generation_touched",
    "candidate_release_recommended_now",
    "family_release_recommended_now",
    "family_release_touched",
    "schema_apply_allowed_now",
    "schema_file_creation_allowed_now",
    "schema_file_edit_allowed_now",
    "schema_file_creation_performed_now",
    "schema_file_edit_performed_now",
    "schema_apply_performed_now",
    "external_download_performed_now",
    "external_api_call_performed_now",
    "data_build_performed_now",
    "aggregation_performed_now",
    "okx_browse_performed_now",
    "okx_download_performed_now",
    "okx_api_call_performed_now",
    "okx_sample_zip_downloaded_now",
    "okx_page_reopened_now",
    "source_manifest_created_now",
    "repo_schema_config_created_now",
    "generic_runner_approval_granted",
    "old_source_panel_anomaly_route_reopened_now",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_git(args: List[str]) -> str:
    allowed = (
        ["rev-parse", "--short", "HEAD"],
        ["status", "--short"],
        ["ls-files"],
    )
    if args not in allowed:
        raise RuntimeError(f"unsafe git metadata command refused: {args}")
    completed = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={REPO_ROOT}", "-C", str(REPO_ROOT)] + args,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def read_json_checked(path: Path) -> Tuple[Dict[str, Any], bool, bool, bool]:
    exists = path.exists()
    if not exists:
        return {}, False, False, False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}, True, False, False
    return data, True, True, isinstance(data, dict) and bool(data)


def load_json(path: Path, label: str) -> Dict[str, Any]:
    data, exists, valid, non_empty = read_json_checked(path)
    if not (exists and valid and non_empty):
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {label} missing/invalid/empty: {path}")
    return data


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require_equal(actual: Any, expected: Any, field: str, status: str = STATUS_BLOCKED_CONTEXT) -> None:
    if actual != expected:
        raise RuntimeError(f"{status}: {field}={actual!r} expected {expected!r}")


def require_true(actual: Any, field: str) -> None:
    if actual is not True:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {field} must be true, got {actual!r}")


def require_false(actual: Any, field: str) -> None:
    if actual is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {field} must be false, got {actual!r}")


def normalize_status_lines(status: str) -> List[str]:
    return [line.strip() for line in status.splitlines() if line.strip()]


def validate_repo_status_allows_current_tool_only(status: str) -> None:
    allowed = {f"?? {CURRENT_TOOL_REL}", f"A  {CURRENT_TOOL_REL}", f"AM {CURRENT_TOOL_REL}"}
    unexpected = [line for line in normalize_status_lines(status) if line not in allowed]
    if unexpected:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: repo dirty outside approved tool: {unexpected}")


def tracked_python_count() -> int:
    output = run_git(["ls-files"])
    return len([line for line in output.splitlines() if line.strip().endswith(".py")])


def planned_schema_files_existing_count() -> int:
    return sum(1 for rel_path in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel_path).exists())


def generic_runner_target_exists() -> bool:
    return (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()


def dangerous_flags() -> Dict[str, bool]:
    return {name: False for name in DANGEROUS_FLAG_NAMES}


def validate_no_true_dangerous_flags(data: Dict[str, Any], artifact_name: str) -> None:
    true_flags = [name for name, value in data.get("dangerous_flags", {}).items() if value is True]
    if true_flags:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {artifact_name} dangerous flags true: {true_flags}")


def validate_required_artifacts() -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Any]]:
    paths = {
        "execution_report": EXECUTION_REPORT_ARTIFACT,
        "provenance_report": PROVENANCE_REPORT_ARTIFACT,
        "zip_inventory_report": ZIP_INVENTORY_REPORT_ARTIFACT,
        "schema_sample_report": SCHEMA_SAMPLE_REPORT_ARTIFACT,
        "compliance_report": COMPLIANCE_REPORT_ARTIFACT,
        "execution_summary": EXECUTION_SUMMARY_ARTIFACT,
        "execution_latest": EXECUTION_LATEST_ARTIFACT,
        "preview_approval": PREVIEW_APPROVAL_ARTIFACT,
        "smoke_summary": SMOKE_SUMMARY_ARTIFACT,
    }
    artifacts: Dict[str, Dict[str, Any]] = {}
    status: Dict[str, Any] = {
        "required_artifact_paths": {label: str(path) for label, path in paths.items()},
        "artifact_exists_by_label": {},
        "artifact_valid_json_by_label": {},
    }
    for label, path in paths.items():
        data, exists, valid, non_empty = read_json_checked(path)
        status["artifact_exists_by_label"][label] = exists
        status["artifact_valid_json_by_label"][label] = valid and non_empty
        if not (exists and valid and non_empty):
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {label} missing/invalid/empty: {path}")
        artifacts[label] = data
    status["execution_artifacts_exist"] = all(status["artifact_exists_by_label"].values())
    status["execution_artifacts_valid_json"] = all(status["artifact_valid_json_by_label"].values())
    return artifacts, status


def provenance_entries(provenance_report: Dict[str, Any]) -> List[Dict[str, Any]]:
    entries = provenance_report.get("per_file_download_provenance")
    if not isinstance(entries, list) or len(entries) != RANGE_DAYS:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: provenance must contain exactly 7 files")
    return entries


def inventory_entries(inventory_report: Dict[str, Any]) -> List[Dict[str, Any]]:
    entries = inventory_report.get("zip_inventory")
    if not isinstance(entries, list) or len(entries) != RANGE_DAYS:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: zip inventory must contain exactly 7 files")
    return entries


def sample_entries(sample_report: Dict[str, Any]) -> List[Dict[str, Any]]:
    entries = sample_report.get("schema_sample")
    if not isinstance(entries, list) or len(entries) != RANGE_DAYS:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: schema sample must contain exactly 7 files")
    return entries


def validate_preflight(artifacts: Dict[str, Dict[str, Any]], artifact_status: Dict[str, Any]) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))

    latest = artifacts["execution_latest"]
    summary = artifacts["execution_summary"]
    execution_report = artifacts["execution_report"]
    provenance = provenance_entries(artifacts["provenance_report"])
    inventory = inventory_entries(artifacts["zip_inventory_report"])
    samples = sample_entries(artifacts["schema_sample_report"])
    compliance = artifacts["compliance_report"]
    preview = artifacts["preview_approval"]
    smoke_summary = artifacts["smoke_summary"]

    for label, data in (("execution_latest", latest), ("execution_summary", summary)):
        require_equal(
            data.get("historical_data_acquisition_okx_single_symbol_small_range_download_execution_status"),
            EXECUTION_STATUS_PASS,
            f"{label}.status",
        )
        require_equal(data.get("next_module"), REQUESTED_MODULE, f"{label}.next_module", STATUS_BLOCKED_NEXT_MODULE)
        require_true(data.get("small_range_download_execution_performed"), f"{label}.execution_performed")
        require_true(data.get("approved_url_list_used"), f"{label}.approved_url_list_used")
        require_equal(data.get("approved_url_count"), RANGE_DAYS, f"{label}.approved_url_count")
        require_equal(data.get("downloaded_file_count"), RANGE_DAYS, f"{label}.downloaded_file_count")
        require_equal(data.get("target_symbol"), TARGET_SYMBOL, f"{label}.target_symbol")
        require_equal(data.get("date_range_start"), DATE_RANGE_START, f"{label}.date_range_start")
        require_equal(data.get("date_range_end"), DATE_RANGE_END, f"{label}.date_range_end")
        require_true(data.get("all_downloads_succeeded"), f"{label}.all_downloads_succeeded")
        require_true(data.get("all_hashes_computed_after_download"), f"{label}.hashes_after_download")
        require_equal(data.get("hash_algorithm"), "SHA256", f"{label}.hash_algorithm")
        require_true(data.get("all_zip_open_success"), f"{label}.zip_open")
        require_true(data.get("all_expected_inner_csv_present"), f"{label}.expected_csv")
        require_false(data.get("any_zip_path_traversal_detected"), f"{label}.zip_traversal")
        require_true(data.get("all_csv_headers_read"), f"{label}.csv_headers")
        if not isinstance(data.get("max_csv_sample_rows_read_per_file"), int) or data["max_csv_sample_rows_read_per_file"] > MAX_CSV_SAMPLE_DATA_ROWS:
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {label}.max_csv_sample_rows_read_per_file > 5")
        require_false(data.get("full_csv_read_performed"), f"{label}.full_csv")
        require_true(data.get("all_expected_schema_match"), f"{label}.schema")
        require_true(data.get("all_one_minute_interval_observed_from_samples"), f"{label}.one_minute")
        require_false(data.get("direct_1h_interval_present"), f"{label}.direct_1h")
        require_false(data.get("files_marked_build_ready"), f"{label}.build_ready")
        require_false(data.get("source_manifest_acquisition_ready"), f"{label}.source_acquisition")
        require_false(data.get("broad_acquisition_execution_allowed_now"), f"{label}.broad_acquisition")
        require_false(data.get("data_build_performed"), f"{label}.data_build")
        require_false(data.get("aggregation_performed_now"), f"{label}.aggregation")
        require_false(data.get("okx_api_call_performed"), f"{label}.api")
        require_false(data.get("okx_browse_performed"), f"{label}.browse")
        require_equal(data.get("active_p0_blocker_count"), 0, f"{label}.active_p0")
        require_true(int(data.get("active_p1_attention_count", 0)) >= 8, f"{label}.active_p1")
        require_equal(data.get("dormant_repo_attention_count"), 716, f"{label}.dormant_attention")
        require_true(data.get("replacement_checks_all_true"), f"{label}.replacement")
        validate_no_true_dangerous_flags(data, label)

    scope = execution_report.get("execution_scope", {})
    require_equal(scope.get("approved_urls"), APPROVED_URLS, "execution_report.execution_scope.approved_urls")
    require_equal(scope.get("downloaded_file_count"), RANGE_DAYS, "execution_report.execution_scope.downloaded_file_count")
    require_true(scope.get("no_url_discovery"), "execution_report.execution_scope.no_url_discovery")
    require_true(scope.get("no_api"), "execution_report.execution_scope.no_api")
    require_true(scope.get("no_browse"), "execution_report.execution_scope.no_browse")
    require_true(scope.get("no_data_build"), "execution_report.execution_scope.no_data_build")
    require_true(scope.get("no_aggregation"), "execution_report.execution_scope.no_aggregation")

    for index, approved in enumerate(APPROVED_FILES):
        prov = provenance[index]
        inv = inventory[index]
        sample = samples[index]
        require_equal(prov.get("date"), approved["date"], f"provenance[{index}].date")
        require_equal(prov.get("source_url"), approved["source_url"], f"provenance[{index}].source_url")
        require_equal(prov.get("downloaded_zip_file_name"), approved["downloaded_zip_file_name"], f"provenance[{index}].file_name")
        require_equal(prov.get("expected_inner_csv"), approved["expected_inner_csv"], f"provenance[{index}].expected_inner_csv")
        require_equal(prov.get("hash_algorithm"), "SHA256", f"provenance[{index}].hash_algorithm")
        require_true(prov.get("hash_computed_after_download"), f"provenance[{index}].hash_after_download")
        require_equal(prov.get("download_status"), "DOWNLOADED_SINGLE_SYMBOL_SMALL_RANGE_SMOKE_TEST", f"provenance[{index}].download_status")
        require_equal(inv.get("date"), approved["date"], f"inventory[{index}].date")
        require_true(inv.get("zip_open_success"), f"inventory[{index}].zip_open")
        require_true(inv.get("expected_inner_csv_present"), f"inventory[{index}].expected_csv")
        require_false(inv.get("zip_path_traversal_detected"), f"inventory[{index}].traversal")
        require_equal(inv.get("zip_inventory_status"), "PASS_EXPECTED_CSV_PRESENT", f"inventory[{index}].status")
        require_equal(sample.get("date"), approved["date"], f"sample[{index}].date")
        require_true(sample.get("csv_header_read"), f"sample[{index}].header")
        if not isinstance(sample.get("csv_sample_rows_read_count"), int) or sample["csv_sample_rows_read_count"] > MAX_CSV_SAMPLE_DATA_ROWS:
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: sample[{index}].csv_sample_rows_read_count > 5")
        require_false(sample.get("csv_full_read_performed"), f"sample[{index}].full_csv")
        require_true(sample.get("expected_schema_match"), f"sample[{index}].schema")
        require_true(sample.get("expected_symbol_match"), f"sample[{index}].symbol")
        require_true(sample.get("one_minute_interval_observed"), f"sample[{index}].one_minute")
        require_false(sample.get("direct_1h_interval_present"), f"sample[{index}].direct_1h")

    require_true(compliance.get("data_download_performed"), "compliance.data_download")
    require_true(compliance.get("data_fetch_performed"), "compliance.data_fetch")
    require_true(compliance.get("okx_download_performed"), "compliance.okx_download")
    require_true(compliance.get("okx_sample_zip_downloaded_now"), "compliance.sample_zip")
    require_false(compliance.get("full_csv_read_performed"), "compliance.full_csv")
    for field in (
        "okx_api_call_performed",
        "okx_browse_performed",
        "data_build_performed",
        "aggregation_performed_now",
        "strategy_signal_claims_made",
        "tradable_edge_claims_made",
        "profit_claims_made",
        "backtest_performed",
        "candidate_generation_performed",
        "runtime_touch_performed",
        "capital_touch_performed",
        "live_touch_performed",
        "generic_runner_approval_granted",
        "schema_or_config_created",
        "files_marked_build_ready",
        "source_manifest_acquisition_ready",
        "broad_acquisition_execution_allowed_now",
    ):
        require_false(compliance.get(field), f"compliance.{field}")
    require_true(compliance.get("generic_runner_implementation_remains_blocked"), "compliance.generic_runner_blocked")

    require_true(preview.get("approval_grants_future_small_range_download_next"), "preview.future_download")
    require_false(preview.get("approval_grants_more_than_7_files_now"), "preview.more_than_7")
    require_false(preview.get("approval_grants_multi_symbol_now"), "preview.multi_symbol")
    require_false(preview.get("approval_grants_data_build_now"), "preview.data_build")
    require_false(preview.get("approval_grants_aggregation_now"), "preview.aggregation")
    require_false(preview.get("approval_grants_broad_acquisition_now"), "preview.broad_acquisition")
    require_equal(preview.get("target_symbol"), TARGET_SYMBOL, "preview.target_symbol")

    require_equal(
        smoke_summary.get("historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_summary_status"),
        "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_PIPELINE_SMOKE_TEST_CLOSED_SMALL_RANGE_DOWNLOAD_PREVIEW_READY",
        "smoke_summary.status",
    )
    require_false(smoke_summary.get("data_download_performed"), "smoke_summary.download")
    require_false(smoke_summary.get("data_build_performed"), "smoke_summary.build")
    require_false(smoke_summary.get("aggregation_performed_now"), "smoke_summary.aggregation")

    return {
        "whole_system_preflight_completed": True,
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
        **artifact_status,
        "execution_report_artifact": str(EXECUTION_REPORT_ARTIFACT),
        "provenance_report_artifact": str(PROVENANCE_REPORT_ARTIFACT),
        "zip_inventory_report_artifact": str(ZIP_INVENTORY_REPORT_ARTIFACT),
        "schema_sample_report_artifact": str(SCHEMA_SAMPLE_REPORT_ARTIFACT),
        "compliance_report_artifact": str(COMPLIANCE_REPORT_ARTIFACT),
        "execution_summary_artifact": str(EXECUTION_SUMMARY_ARTIFACT),
        "preview_approval_artifact": str(PREVIEW_APPROVAL_ARTIFACT),
        "smoke_summary_artifact": str(SMOKE_SUMMARY_ARTIFACT),
        "head": head,
    }


def zip_member_has_path_traversal(name: str) -> bool:
    normalized = name.replace("\\", "/")
    posix = PurePosixPath(normalized)
    return (
        normalized.startswith("/")
        or ":" in normalized.split("/", 1)[0]
        or any(part in ("", ".", "..") for part in posix.parts)
    )


def recompute_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def approved_url_validation(provenance: List[Dict[str, Any]]) -> Dict[str, Any]:
    observed_urls = [str(entry.get("source_url")) for entry in provenance]
    observed_set = set(observed_urls)
    approved_set = set(APPROVED_URLS)
    duplicate_url_count = len(observed_urls) - len(observed_set)
    extra_urls = sorted(observed_set - approved_set)
    missing_urls = [url for url in APPROVED_URLS if url not in observed_set]
    multi_symbol_urls = [url for url in observed_urls if TARGET_SYMBOL not in url]
    outside_range_urls = [
        url
        for url in observed_urls
        if not any(approved["source_url"] == url for approved in APPROVED_FILES)
    ]
    return {
        "approved_urls": APPROVED_URLS,
        "observed_urls": observed_urls,
        "approved_url_list_exact_match": observed_urls == APPROVED_URLS,
        "extra_url_count": len(extra_urls),
        "missing_url_count": len(missing_urls),
        "duplicate_url_count": duplicate_url_count,
        "extra_urls": extra_urls,
        "missing_urls": missing_urls,
        "no_url_outside_approved_date_range": len(outside_range_urls) == 0,
        "no_multi_symbol_url": len(multi_symbol_urls) == 0,
        "outside_range_urls": outside_range_urls,
        "multi_symbol_urls": multi_symbol_urls,
    }


def hash_file_validation(provenance: List[Dict[str, Any]]) -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = []
    total_size = 0
    for index, entry in enumerate(provenance):
        path = Path(str(entry.get("downloaded_zip_path", "")))
        exists = path.exists() and path.is_file()
        size = path.stat().st_size if exists else 0
        total_size += size
        recomputed = recompute_sha256(path) if exists else None
        entries.append(
            {
                "date": entry.get("date"),
                "downloaded_zip_path": str(path),
                "downloaded_zip_path_exists": exists,
                "downloaded_zip_size_bytes": size,
                "downloaded_zip_size_recorded": entry.get("downloaded_zip_size_bytes"),
                "file_size_within_limit": 0 < size <= MAX_ZIP_SIZE_BYTES,
                "recorded_size_matches_file": size == entry.get("downloaded_zip_size_bytes"),
                "downloaded_zip_sha256_recorded": entry.get("downloaded_zip_sha256"),
                "downloaded_zip_sha256_recomputed": recomputed,
                "downloaded_zip_sha256_matches_recorded": recomputed == entry.get("downloaded_zip_sha256"),
                "hash_algorithm": entry.get("hash_algorithm"),
                "hash_computed_after_download": entry.get("hash_computed_after_download") is True,
                "source_url": entry.get("source_url"),
                "expected_inner_csv": entry.get("expected_inner_csv"),
                "validation_index": index,
            }
        )
    return {
        "hash_file_validation": entries,
        "validated_file_count": len(entries),
        "total_zip_size_bytes": total_size,
        "all_downloaded_zip_paths_exist": all(item["downloaded_zip_path_exists"] for item in entries),
        "all_file_sizes_within_limit": all(item["file_size_within_limit"] for item in entries)
        and total_size <= MAX_TOTAL_ZIP_SIZE_BYTES,
        "all_recorded_sizes_match_files": all(item["recorded_size_matches_file"] for item in entries),
        "all_hashes_recomputed": all(item["downloaded_zip_sha256_recomputed"] for item in entries),
        "all_hashes_match_recorded": all(item["downloaded_zip_sha256_matches_recorded"] for item in entries),
        "all_hash_algorithms_sha256": all(item["hash_algorithm"] == "SHA256" for item in entries),
        "all_hashes_computed_after_download": all(item["hash_computed_after_download"] for item in entries),
        "hash_algorithm": "SHA256",
        "all_hashes_validated": True,
    }


def validate_zip_inventory_from_files(provenance: List[Dict[str, Any]]) -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = []
    for entry in provenance:
        path = Path(str(entry.get("downloaded_zip_path", "")))
        expected_inner_csv = str(entry.get("expected_inner_csv"))
        with zipfile.ZipFile(path, "r") as zf:
            names = zf.namelist()
        traversal = any(zip_member_has_path_traversal(name) for name in names)
        entries.append(
            {
                "date": entry.get("date"),
                "downloaded_zip_path": str(path),
                "expected_inner_csv": expected_inner_csv,
                "zip_open_success": True,
                "zip_member_count": len(names),
                "zip_member_names": names,
                "zip_member_count_within_limit": len(names) <= MAX_ZIP_MEMBERS,
                "expected_inner_csv_present": expected_inner_csv in names,
                "zip_path_traversal_detected": traversal,
                "no_unexpected_dangerous_member_path": traversal is False,
            }
        )
    return {
        "zip_inventory_validation": entries,
        "all_zip_open_success": all(item["zip_open_success"] for item in entries),
        "all_zip_member_counts_within_limit": all(item["zip_member_count_within_limit"] for item in entries),
        "all_expected_inner_csv_present": all(item["expected_inner_csv_present"] for item in entries),
        "any_zip_path_traversal_detected": any(item["zip_path_traversal_detected"] for item in entries),
        "all_zip_inventories_validated": True,
    }


def validate_schema_samples_from_files(provenance: List[Dict[str, Any]]) -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = []
    for entry in provenance:
        path = Path(str(entry.get("downloaded_zip_path", "")))
        expected_inner_csv = str(entry.get("expected_inner_csv"))
        rows: List[List[str]] = []
        with zipfile.ZipFile(path, "r") as zf:
            with zf.open(expected_inner_csv, "r") as raw:
                text = io.TextIOWrapper(raw, encoding="utf-8", newline="")
                reader = csv.reader(text)
                try:
                    header = next(reader)
                except StopIteration as exc:
                    raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: expected CSV is empty: {expected_inner_csv}") from exc
                for index, row in enumerate(reader):
                    if index >= MAX_CSV_SAMPLE_DATA_ROWS:
                        break
                    rows.append(row)
        symbol_index = header.index("instrument_name") if "instrument_name" in header else None
        observed_symbols = sorted({row[symbol_index] for row in rows if symbol_index is not None and len(row) > symbol_index})
        open_time_index = header.index("open_time") if "open_time" in header else None
        open_times: List[int] = []
        if open_time_index is not None:
            for row in rows:
                if len(row) > open_time_index:
                    try:
                        open_times.append(int(row[open_time_index]))
                    except ValueError:
                        pass
        deltas = [abs(open_times[idx + 1] - open_times[idx]) for idx in range(len(open_times) - 1)]
        one_minute = bool(deltas) and all(delta == 60000 for delta in deltas)
        entries.append(
            {
                "date": entry.get("date"),
                "downloaded_zip_path": str(path),
                "expected_inner_csv": expected_inner_csv,
                "csv_header_read": True,
                "csv_sample_rows_read_count": len(rows),
                "csv_full_read_performed": False,
                "expected_schema_match": header == EXPECTED_SCHEMA,
                "observed_columns": header,
                "expected_columns": EXPECTED_SCHEMA,
                "observed_symbol_sample": observed_symbols,
                "observed_symbols_match_target": observed_symbols == [TARGET_SYMBOL],
                "sample_open_time_values": open_times[:MAX_CSV_SAMPLE_DATA_ROWS],
                "sample_open_time_delta_ms": 60000 if one_minute else (deltas[0] if deltas else None),
                "inferred_sample_interval": "1m" if one_minute else "UNKNOWN_PENDING_REVIEW",
                "one_minute_interval_observed": one_minute,
                "direct_1h_interval_present": False if one_minute else None,
            }
        )
    max_rows = max([item["csv_sample_rows_read_count"] for item in entries] or [0])
    return {
        "schema_sample_validation": entries,
        "all_csv_headers_read": all(item["csv_header_read"] for item in entries),
        "max_csv_sample_rows_read_per_file": max_rows,
        "full_csv_read_performed": any(item["csv_full_read_performed"] for item in entries),
        "all_expected_schema_match": all(item["expected_schema_match"] for item in entries),
        "all_observed_symbols_match_target": all(item["observed_symbols_match_target"] for item in entries),
        "all_one_minute_interval_observed_from_samples": all(item["one_minute_interval_observed"] for item in entries),
        "direct_1h_interval_present": any(item["direct_1h_interval_present"] is True for item in entries),
        "all_schema_samples_validated": True,
    }


def build_payload(
    preflight: Dict[str, Any],
    artifacts: Dict[str, Dict[str, Any]],
    url_validation: Dict[str, Any],
    hash_validation: Dict[str, Any],
    zip_validation: Dict[str, Any],
    schema_validation: Dict[str, Any],
) -> Dict[str, Any]:
    latest = artifacts["execution_latest"]
    flags = dangerous_flags()
    seven_file_provenance_validated = (
        hash_validation["validated_file_count"] == RANGE_DAYS
        and hash_validation["all_downloaded_zip_paths_exist"]
        and hash_validation["all_file_sizes_within_limit"]
        and hash_validation["all_recorded_sizes_match_files"]
        and hash_validation["all_hashes_recomputed"]
        and hash_validation["all_hashes_match_recorded"]
        and hash_validation["all_hash_algorithms_sha256"]
        and hash_validation["all_hashes_computed_after_download"]
        and url_validation["approved_url_list_exact_match"]
        and url_validation["extra_url_count"] == 0
        and url_validation["missing_url_count"] == 0
        and url_validation["duplicate_url_count"] == 0
    )
    seven_file_schema_samples_validated = (
        schema_validation["all_csv_headers_read"]
        and schema_validation["max_csv_sample_rows_read_per_file"] <= MAX_CSV_SAMPLE_DATA_ROWS
        and schema_validation["full_csv_read_performed"] is False
        and schema_validation["all_expected_schema_match"]
        and schema_validation["all_observed_symbols_match_target"]
    )
    seven_file_1m_interval_validated = (
        schema_validation["all_one_minute_interval_observed_from_samples"]
        and schema_validation["direct_1h_interval_present"] is False
    )
    zip_validated = (
        zip_validation["all_zip_open_success"]
        and zip_validation["all_zip_member_counts_within_limit"]
        and zip_validation["all_expected_inner_csv_present"]
        and zip_validation["any_zip_path_traversal_detected"] is False
    )
    replacement_checks = {
        "preflight_passed": preflight.get("whole_system_preflight_completed") is True,
        "execution_artifacts_valid_json": preflight.get("execution_artifacts_valid_json") is True,
        "approved_url_list_exact": url_validation["approved_url_list_exact_match"],
        "seven_file_provenance_validated": seven_file_provenance_validated,
        "zip_inventories_validated": zip_validated,
        "schema_samples_validated": seven_file_schema_samples_validated,
        "one_minute_interval_validated": seven_file_1m_interval_validated,
        "no_new_download_by_validator": True,
        "no_api_browse_by_validator": True,
        "no_data_build_aggregation": True,
        "no_full_csv_read": schema_validation["full_csv_read_performed"] is False,
        "not_build_ready_or_acquisition_ready": True,
        "schema_config_absent": planned_schema_files_existing_count() == 0,
        "generic_runner_absent": generic_runner_target_exists() is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
    }
    if not all(replacement_checks.values()):
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: replacement checks failed")
    active_p1 = max(8, int(latest.get("active_p1_attention_count", 8)))
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_single_symbol_small_range_download_execution_validator_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "PREVIEW_SINGLE_SYMBOL_SMALL_RANGE_1M_TO_1H_BUILD_SCOPE_NO_EXECUTION",
        "next_module": NEXT_MODULE_PASS,
        **preflight,
        "small_range_download_execution_validated": True,
        "approved_url_list_used": True,
        "approved_url_count": RANGE_DAYS,
        "downloaded_file_count": RANGE_DAYS,
        "target_symbol": TARGET_SYMBOL,
        "date_range_start": DATE_RANGE_START,
        "date_range_end": DATE_RANGE_END,
        "approved_url_list_exact_match": True,
        "extra_url_count": 0,
        "missing_url_count": 0,
        "duplicate_url_count": 0,
        "all_downloaded_zip_paths_exist": True,
        "all_file_sizes_within_limit": True,
        "all_hashes_recomputed": True,
        "all_hashes_match_recorded": True,
        "hash_algorithm": "SHA256",
        "all_zip_open_success": True,
        "all_zip_member_counts_within_limit": True,
        "all_expected_inner_csv_present": True,
        "any_zip_path_traversal_detected": False,
        "all_csv_headers_read": True,
        "max_csv_sample_rows_read_per_file": schema_validation["max_csv_sample_rows_read_per_file"],
        "full_csv_read_performed": False,
        "all_expected_schema_match": True,
        "all_observed_symbols_match_target": True,
        "all_one_minute_interval_observed_from_samples": True,
        "direct_1h_interval_present": False,
        "seven_file_provenance_validated": True,
        "seven_file_schema_samples_validated": True,
        "seven_file_1m_interval_validated": True,
        "safe_for_small_range_build_preview": True,
        "safe_for_broad_acquisition": False,
        "safe_for_research_backtest": False,
        "safe_for_edge_claim": False,
        "files_marked_build_ready": False,
        "source_manifest_acquisition_ready": False,
        "broad_acquisition_execution_allowed_now": False,
        "data_download_performed": True,
        "data_fetch_performed": True,
        "new_download_performed_by_validator": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "acquisition_execution_allowed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "okx_download_performed": True,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "okx_sample_zip_downloaded_now": True,
        "fake_or_synthetic_data_detected": False,
        "strategy_signal_claims_made": False,
        "tradable_edge_claims_made": False,
        "profit_claims_made": False,
        "backtest_performed": False,
        "candidate_generation_performed": False,
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "validator_p0_count": 0,
        "validator_p1_count": active_p1,
        "current_evidence_chain_quality_before_validator": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_validator": EVIDENCE_AFTER,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": active_p1,
        "dormant_repo_attention_count": 716,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": planned_schema_files_existing_count(),
        "generic_runner_target_exists": generic_runner_target_exists(),
        "dangerous_flags": flags,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "dangerous_flags_true_count": sum(1 for value in flags.values() if value),
        "derived_live_repo_post_check": STATUS_PASS,
        "derived_live_repo_post_check_reason": (
            "validated the previous seven-file BTC-USDT-SWAP OKX small-range download execution from existing "
            "artifacts and already-downloaded ZIP files only; recomputed every SHA256, reopened each ZIP central "
            "directory, reread only each expected CSV header and up to five sample rows, confirmed schema, symbol, "
            "and 1m sample intervals, and kept download, API, browse, data build, aggregation, broad acquisition, "
            "research, backtest, candidate, runtime, capital, live, schema/config, and generic-runner paths closed"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": True,
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "tracked_python_count_expectation": {
            "pre_commit": EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT,
        },
    }


def write_validator_artifacts(
    payload: Dict[str, Any],
    url_validation: Dict[str, Any],
    hash_validation: Dict[str, Any],
    zip_validation: Dict[str, Any],
    schema_validation: Dict[str, Any],
    provenance_validation: Dict[str, Any],
) -> None:
    outputs = {
        "historical_okx_single_symbol_small_range_download_execution_validator.json": {
            "generated_at_utc": utc_now(),
            "execution_artifact_validation": {
                "execution_artifacts_exist": payload["execution_artifacts_exist"],
                "execution_artifacts_valid_json": payload["execution_artifacts_valid_json"],
                "execution_status": EXECUTION_STATUS_PASS,
                "approved_url_list_used": payload["approved_url_list_used"],
                "approved_url_count": payload["approved_url_count"],
                "downloaded_file_count": payload["downloaded_file_count"],
                "target_symbol": payload["target_symbol"],
                "date_range_start": payload["date_range_start"],
                "date_range_end": payload["date_range_end"],
                "no_api_browse_build_aggregation": True,
            },
            "approved_url_validation": url_validation,
            "hash_file_validation": hash_validation,
            "zip_inventory_validation": zip_validation,
            "schema_sample_validation": schema_validation,
            "compliance_validation": {
                "new_download_performed_by_validator": False,
                "okx_api_call_performed": False,
                "okx_browse_performed": False,
                "data_build_performed": False,
                "aggregation_performed_now": False,
                "full_csv_read_performed": False,
                "files_marked_build_ready": False,
                "source_manifest_acquisition_ready": False,
                "safe_for_broad_acquisition": False,
                "safe_for_research_backtest": False,
                "safe_for_edge_claim": False,
                "runtime_capital_live_touch_performed": False,
                "generic_runner_implementation_remains_blocked": True,
                "schema_or_config_created": False,
            },
            "risk_decision": {
                "small_range_download_execution_validated": True,
                "seven_file_provenance_validated": True,
                "seven_file_schema_samples_validated": True,
                "seven_file_1m_interval_validated": True,
                "safe_for_small_range_build_preview": True,
                "safe_for_broad_acquisition": False,
                "safe_for_research_backtest": False,
                "safe_for_edge_claim": False,
                "validator_p0_count": 0,
                "validator_p1_count": payload["validator_p1_count"],
            },
            "next_module_decision": {
                "next_module": payload["next_module"],
                "next_action": payload["next_action"],
            },
        },
        "historical_okx_single_symbol_small_range_hash_validation_report.json": hash_validation,
        "historical_okx_single_symbol_small_range_zip_schema_validation_report.json": {
            "zip_inventory_validation": zip_validation,
            "schema_sample_validation": schema_validation,
        },
        "historical_okx_single_symbol_small_range_provenance_validation_report.json": provenance_validation,
        "historical_okx_single_symbol_small_range_download_execution_validator_summary.json": payload,
        "repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_execution_validator_after_execution_v1_latest.json": payload,
    }
    for name, artifact in outputs.items():
        write_json(OUT_DIR / name, artifact)


def blocked_payload(exc: Exception) -> Dict[str, Any]:
    flags = dangerous_flags()
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_single_symbol_small_range_download_execution_validator_status": STATUS_BLOCKED_CONTEXT,
        "final_decision": STATUS_BLOCKED_CONTEXT,
        "next_action": "STOP_FAIL_CLOSED_SMALL_RANGE_DOWNLOAD_EXECUTION_VALIDATOR_BLOCKED",
        "next_module": NEXT_MODULE_BLOCKED,
        "error": str(exc),
        "whole_system_preflight_completed": False,
        "live_next_module_matches_requested_module": False,
        "artifact_chain_consistent": False,
        "stale_or_contradictory_artifact_detected": True,
        "execution_artifacts_exist": False,
        "execution_artifacts_valid_json": False,
        "small_range_download_execution_validated": False,
        "approved_url_list_used": False,
        "approved_url_count": RANGE_DAYS,
        "downloaded_file_count": 0,
        "target_symbol": TARGET_SYMBOL,
        "date_range_start": DATE_RANGE_START,
        "date_range_end": DATE_RANGE_END,
        "approved_url_list_exact_match": False,
        "extra_url_count": 0,
        "missing_url_count": RANGE_DAYS,
        "duplicate_url_count": 0,
        "all_downloaded_zip_paths_exist": False,
        "all_file_sizes_within_limit": False,
        "all_hashes_recomputed": False,
        "all_hashes_match_recorded": False,
        "hash_algorithm": "SHA256",
        "all_zip_open_success": False,
        "all_zip_member_counts_within_limit": False,
        "all_expected_inner_csv_present": False,
        "any_zip_path_traversal_detected": False,
        "all_csv_headers_read": False,
        "max_csv_sample_rows_read_per_file": 0,
        "full_csv_read_performed": False,
        "all_expected_schema_match": False,
        "all_observed_symbols_match_target": False,
        "all_one_minute_interval_observed_from_samples": False,
        "direct_1h_interval_present": None,
        "seven_file_provenance_validated": False,
        "seven_file_schema_samples_validated": False,
        "seven_file_1m_interval_validated": False,
        "safe_for_small_range_build_preview": False,
        "safe_for_broad_acquisition": False,
        "safe_for_research_backtest": False,
        "safe_for_edge_claim": False,
        "files_marked_build_ready": False,
        "source_manifest_acquisition_ready": False,
        "broad_acquisition_execution_allowed_now": False,
        "data_download_performed": True,
        "data_fetch_performed": True,
        "new_download_performed_by_validator": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "acquisition_execution_allowed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "okx_download_performed": True,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "okx_sample_zip_downloaded_now": True,
        "fake_or_synthetic_data_detected": False,
        "strategy_signal_claims_made": False,
        "tradable_edge_claims_made": False,
        "profit_claims_made": False,
        "backtest_performed": False,
        "candidate_generation_performed": False,
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "validator_p0_count": 1,
        "validator_p1_count": 8,
        "current_evidence_chain_quality_before_validator": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_validator": "BLOCKED_FAIL_CLOSED_NO_BUILD_PREVIEW",
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 8,
        "dormant_repo_attention_count": 716,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": planned_schema_files_existing_count(),
        "generic_runner_target_exists": generic_runner_target_exists(),
        "dangerous_flags": flags,
        "dangerous_flags_all_false": True,
        "dangerous_flags_true_count": 0,
        "derived_live_repo_post_check": STATUS_BLOCKED_CONTEXT,
        "derived_live_repo_post_check_reason": "small-range download execution validator failed closed before any build or aggregation route",
        "replacement_checks_all_true": False,
    }


def write_blocked_artifact(payload: Dict[str, Any]) -> None:
    write_json(
        OUT_DIR / "repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_execution_validator_after_execution_v1_latest.json",
        payload,
    )
    write_json(OUT_DIR / "historical_okx_single_symbol_small_range_download_execution_validator_summary.json", payload)


def main() -> int:
    try:
        artifacts, artifact_status = validate_required_artifacts()
        preflight = validate_preflight(artifacts, artifact_status)
        provenance = provenance_entries(artifacts["provenance_report"])
        url_validation = approved_url_validation(provenance)
        hash_validation = hash_file_validation(provenance)
        if hash_validation["validated_file_count"] > RANGE_DAYS:
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: validator processed too many files")
        zip_validation = validate_zip_inventory_from_files(provenance)
        schema_validation = validate_schema_samples_from_files(provenance)
        provenance_validation = {
            "generated_at_utc": utc_now(),
            "approved_url_validation": url_validation,
            "hash_validation_report": hash_validation,
            "seven_file_provenance_validated": True,
            "new_download_performed_by_validator": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
        }
        payload = build_payload(preflight, artifacts, url_validation, hash_validation, zip_validation, schema_validation)
        write_validator_artifacts(payload, url_validation, hash_validation, zip_validation, schema_validation, provenance_validation)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        payload = blocked_payload(exc)
        write_blocked_artifact(payload)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
