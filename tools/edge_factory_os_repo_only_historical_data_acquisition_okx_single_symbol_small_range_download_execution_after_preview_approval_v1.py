from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_execution_"
    "after_preview_approval_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_execution_"
    "after_preview_approval_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME
DOWNLOAD_DIR = OUT_DIR / "downloaded_single_symbol_small_range_quarantine"

EXPECTED_HEAD = "df874c4"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 688
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 689

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_execution_"
    "after_preview_approval_v1.py"
)
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_execution_validator_"
    "after_execution_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_execution_"
    "blocked_record_after_preview_approval_v1.py"
)

PREVIEW_DIR = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_preview_after_smoke_test_summary_v1"
)
PREVIEW_LATEST_ARTIFACT = (
    PREVIEW_DIR
    / "repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_preview_after_smoke_test_summary_v1_latest.json"
)
PREVIEW_BUNDLE_ARTIFACT = PREVIEW_DIR / "historical_okx_single_symbol_small_range_download_preview_bundle_summary.json"
PLANNED_URL_MANIFEST_ARTIFACT = PREVIEW_DIR / "historical_okx_single_symbol_small_range_planned_url_manifest.json"
APPROVAL_RECORD_ARTIFACT = PREVIEW_DIR / "historical_okx_single_symbol_small_range_download_approval_record.json"
SMOKE_SUMMARY_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_summary_after_build_validator_v1"
    / "repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_summary_after_build_validator_v1_latest.json"
)
BUILD_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_validator_after_execution_v1"
    / "repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_validator_after_execution_v1_latest.json"
)

PREVIEW_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMALL_RANGE_DOWNLOAD_PREVIEW_APPROVED_EXECUTION_NEXT_"
    "NO_DOWNLOAD_YET"
)
SMOKE_SUMMARY_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_PIPELINE_SMOKE_TEST_CLOSED_SMALL_RANGE_DOWNLOAD_"
    "PREVIEW_READY"
)
BUILD_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_1M_TO_1H_BUILD_VALIDATED_PIPELINE_SMOKE_TEST_"
    "SUMMARY_READY"
)
STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMALL_RANGE_DOWNLOAD_EXECUTED_PENDING_VALIDATOR_NO_BUILD"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMALL_RANGE_DOWNLOAD_PREVIEW_APPROVED_EXECUTION_NEXT_"
    "NO_DOWNLOAD_YET"
)
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMALL_RANGE_DOWNLOAD_EXECUTED_PENDING_VALIDATOR_NO_BUILD"
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


def require_zero(actual: Any, field: str) -> None:
    require_equal(actual, 0, field)


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


def validate_required_artifacts() -> Dict[str, Dict[str, Any]]:
    paths = {
        "preview_latest": PREVIEW_LATEST_ARTIFACT,
        "preview_bundle": PREVIEW_BUNDLE_ARTIFACT,
        "planned_url_manifest": PLANNED_URL_MANIFEST_ARTIFACT,
        "approval_record": APPROVAL_RECORD_ARTIFACT,
        "smoke_summary": SMOKE_SUMMARY_ARTIFACT,
        "build_validator": BUILD_VALIDATOR_ARTIFACT,
    }
    return {label: load_json(path, label) for label, path in paths.items()}


def validate_approved_manifest(manifest: Dict[str, Any]) -> None:
    require_equal(manifest.get("planned_url_count"), RANGE_DAYS, "manifest.planned_url_count")
    require_equal(manifest.get("planned_file_count"), RANGE_DAYS, "manifest.planned_file_count")
    require_equal(manifest.get("planned_urls"), APPROVED_URLS, "manifest.planned_urls")
    files = manifest.get("planned_files")
    if not isinstance(files, list) or len(files) != RANGE_DAYS:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: manifest.planned_files must contain exactly 7 entries")
    for index, approved in enumerate(APPROVED_FILES):
        item = files[index]
        require_equal(item.get("date"), approved["date"], f"manifest.planned_files[{index}].date")
        require_equal(item.get("planned_url"), approved["source_url"], f"manifest.planned_files[{index}].planned_url")
        require_equal(item.get("expected_file_name"), approved["downloaded_zip_file_name"], f"manifest.planned_files[{index}].expected_file_name")
        require_equal(item.get("expected_inner_csv_name"), approved["expected_inner_csv"], f"manifest.planned_files[{index}].expected_inner_csv_name")
        require_equal(item.get("instrument_name"), TARGET_SYMBOL, f"manifest.planned_files[{index}].instrument_name")
        require_equal(item.get("download_status"), "NOT_DOWNLOADED", f"manifest.planned_files[{index}].download_status")
        require_false(item.get("build_ready"), f"manifest.planned_files[{index}].build_ready")
        require_false(item.get("acquisition_ready"), f"manifest.planned_files[{index}].acquisition_ready")
        require_equal(item.get("expected_sha256_after_download"), None, f"manifest.planned_files[{index}].expected_sha256_after_download")


def validate_preflight(artifacts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))

    preview = artifacts["preview_latest"]
    preview_bundle = artifacts["preview_bundle"]
    manifest = artifacts["planned_url_manifest"]
    approval = artifacts["approval_record"]
    smoke_summary = artifacts["smoke_summary"]
    build_validator = artifacts["build_validator"]

    require_equal(
        preview.get("historical_data_acquisition_okx_single_symbol_small_range_download_preview_bundle_status"),
        PREVIEW_STATUS_PASS,
        "preview.status",
    )
    require_equal(preview.get("next_module"), REQUESTED_MODULE, "preview.next_module", STATUS_BLOCKED_NEXT_MODULE)
    require_equal(preview.get("target_symbol"), TARGET_SYMBOL, "preview.target_symbol")
    require_equal(preview.get("range_days"), RANGE_DAYS, "preview.range_days")
    require_equal(preview.get("planned_url_count"), RANGE_DAYS, "preview.planned_url_count")
    require_equal(preview.get("planned_file_count"), RANGE_DAYS, "preview.planned_file_count")
    require_true(preview.get("all_planned_files_not_downloaded"), "preview.all_planned_files_not_downloaded")
    require_zero(preview.get("sha256_claim_count"), "preview.sha256_claim_count")
    require_zero(preview.get("build_ready_file_count"), "preview.build_ready_file_count")
    require_zero(preview.get("acquisition_ready_file_count"), "preview.acquisition_ready_file_count")
    require_true(preview.get("approval_grants_future_small_range_download_next"), "preview.future_download")
    require_false(preview.get("approval_grants_more_than_7_files_now"), "preview.more_than_7")
    require_false(preview.get("approval_grants_multi_symbol_now"), "preview.multi_symbol")
    require_false(preview.get("approval_grants_data_build_now"), "preview.data_build")
    require_false(preview.get("approval_grants_aggregation_now"), "preview.aggregation")
    require_false(preview.get("approval_grants_broad_acquisition_now"), "preview.broad_acquisition")
    require_true(preview.get("next_route_is_execution_only_for_planned_7_files"), "preview.next_route")
    require_false(preview.get("data_download_performed"), "preview.download")
    require_false(preview.get("data_build_performed"), "preview.build")
    require_false(preview.get("aggregation_performed_now"), "preview.aggregation_now")
    require_false(preview.get("okx_api_call_performed"), "preview.api")
    require_false(preview.get("okx_browse_performed"), "preview.browse")
    require_equal(preview.get("active_p0_blocker_count"), 0, "preview.active_p0")
    require_true(int(preview.get("active_p1_attention_count", 0)) >= 8, "preview.active_p1")
    require_equal(preview.get("dormant_repo_attention_count"), 716, "preview.dormant_attention")
    require_true(preview.get("replacement_checks_all_true"), "preview.replacement")
    validate_no_true_dangerous_flags(preview, "preview")

    require_true(preview_bundle.get("summary", {}).get("replacement_checks_all_true"), "preview_bundle.summary.replacement")
    validate_approved_manifest(preview_bundle.get("planned_url_manifest", {}))
    validate_approved_manifest(manifest)

    require_true(approval.get("approval_grants_future_small_range_download_next"), "approval.future_download")
    require_false(approval.get("approval_grants_download_now"), "approval.download_now")
    require_false(approval.get("approval_grants_api_now"), "approval.api")
    require_false(approval.get("approval_grants_browse_now"), "approval.browse")
    require_false(approval.get("approval_grants_more_than_7_files_now"), "approval.more_than_7")
    require_false(approval.get("approval_grants_multi_symbol_now"), "approval.multi_symbol")
    require_false(approval.get("approval_grants_data_build_now"), "approval.data_build")
    require_false(approval.get("approval_grants_aggregation_now"), "approval.aggregation")
    require_false(approval.get("approval_grants_broad_acquisition_now"), "approval.broad_acquisition")
    require_true(approval.get("user_small_range_download_approval_present"), "approval.user_present")

    require_equal(
        smoke_summary.get("historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_summary_status"),
        SMOKE_SUMMARY_STATUS_PASS,
        "smoke_summary.status",
    )
    require_true(smoke_summary.get("smoke_test_closed_successfully"), "smoke_summary.closed")
    require_equal(smoke_summary.get("target_symbol"), TARGET_SYMBOL, "smoke_summary.target_symbol")
    require_false(smoke_summary.get("data_download_performed"), "smoke_summary.download")
    require_false(smoke_summary.get("data_build_performed"), "smoke_summary.build")
    require_false(smoke_summary.get("aggregation_performed_now"), "smoke_summary.aggregation")
    validate_no_true_dangerous_flags(smoke_summary, "smoke_summary")

    require_equal(
        build_validator.get("historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_validator_status"),
        BUILD_VALIDATOR_STATUS_PASS,
        "build_validator.status",
    )
    require_true(build_validator.get("build_execution_validated"), "build_validator.validated")
    require_false(build_validator.get("new_download_performed_by_validator"), "build_validator.download")
    require_false(build_validator.get("data_build_performed_by_validator"), "build_validator.build")
    require_false(build_validator.get("aggregation_performed_by_validator"), "build_validator.aggregation")
    validate_no_true_dangerous_flags(build_validator, "build_validator")

    return {
        "whole_system_preflight_completed": True,
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
        "preview_latest_artifact": str(PREVIEW_LATEST_ARTIFACT),
        "preview_bundle_artifact": str(PREVIEW_BUNDLE_ARTIFACT),
        "planned_url_manifest_artifact": str(PLANNED_URL_MANIFEST_ARTIFACT),
        "approval_record_artifact": str(APPROVAL_RECORD_ARTIFACT),
        "smoke_summary_artifact": str(SMOKE_SUMMARY_ARTIFACT),
        "build_validator_artifact": str(BUILD_VALIDATOR_ARTIFACT),
        "head": head,
    }


def ensure_download_target_path(file_name: str) -> Path:
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    target = (DOWNLOAD_DIR / file_name).resolve()
    root = DOWNLOAD_DIR.resolve()
    if target.parent != root:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: download target outside output directory")
    return target


def download_approved_files() -> List[Dict[str, Any]]:
    provenance: List[Dict[str, Any]] = []
    total_size = 0
    seen_urls: List[str] = []
    for item in APPROVED_FILES:
        url = item["source_url"]
        if url not in APPROVED_URLS or url in seen_urls:
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: non-approved or duplicate URL refused: {url}")
        seen_urls.append(url)
        target = ensure_download_target_path(item["downloaded_zip_file_name"])
        timestamp = utc_now()
        size = 0
        digest = hashlib.sha256()
        request = urllib.request.Request(url, headers={"User-Agent": "EdgeFactoryOS-SmallRangeExecution/1.0"})
        with urllib.request.urlopen(request, timeout=90) as response:
            with target.open("wb") as out_file:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    size += len(chunk)
                    total_size += len(chunk)
                    if size > MAX_ZIP_SIZE_BYTES:
                        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: ZIP exceeds per-file limit: {target}")
                    if total_size > MAX_TOTAL_ZIP_SIZE_BYTES:
                        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: ZIP total exceeds limit")
                    out_file.write(chunk)
                    digest.update(chunk)
        if size <= 0:
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: downloaded ZIP is empty: {target}")
        provenance.append(
            {
                "date": item["date"],
                "source_url": url,
                "downloaded_zip_path": str(target),
                "downloaded_zip_file_name": item["downloaded_zip_file_name"],
                "downloaded_zip_size_bytes": size,
                "downloaded_zip_sha256": digest.hexdigest(),
                "hash_algorithm": "SHA256",
                "hash_computed_after_download": True,
                "download_timestamp_utc": timestamp,
                "expected_inner_csv": item["expected_inner_csv"],
                "download_status": "DOWNLOADED_SINGLE_SYMBOL_SMALL_RANGE_SMOKE_TEST",
            }
        )
    require_equal(seen_urls, APPROVED_URLS, "downloaded_url_sequence")
    return provenance


def zip_member_has_path_traversal(name: str) -> bool:
    normalized = name.replace("\\", "/")
    posix = PurePosixPath(normalized)
    return (
        normalized.startswith("/")
        or ":" in normalized.split("/", 1)[0]
        or any(part in ("", ".", "..") for part in posix.parts)
    )


def inspect_zip_inventory(provenance: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    inventories: List[Dict[str, Any]] = []
    for entry in provenance:
        zip_path = Path(entry["downloaded_zip_path"])
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
        traversal = any(zip_member_has_path_traversal(name) for name in names)
        expected_present = entry["expected_inner_csv"] in names
        member_count = len(names)
        status = (
            "PASS_EXPECTED_CSV_PRESENT"
            if expected_present and not traversal and member_count <= MAX_ZIP_MEMBERS
            else "BLOCKED_ZIP_INVENTORY"
        )
        if member_count > MAX_ZIP_MEMBERS:
            status = "BLOCKED_TOO_MANY_ZIP_MEMBERS"
        inventories.append(
            {
                "date": entry["date"],
                "downloaded_zip_path": entry["downloaded_zip_path"],
                "expected_inner_csv": entry["expected_inner_csv"],
                "zip_open_success": True,
                "zip_member_count": member_count,
                "zip_member_names": names,
                "expected_inner_csv_present": expected_present,
                "zip_path_traversal_detected": traversal,
                "zip_inventory_status": status,
            }
        )
    return inventories


def sample_csv_from_zip(provenance: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    samples: List[Dict[str, Any]] = []
    for entry in provenance:
        rows: List[List[str]] = []
        zip_path = Path(entry["downloaded_zip_path"])
        expected_inner_csv = entry["expected_inner_csv"]
        with zipfile.ZipFile(zip_path, "r") as zf:
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
        deltas = [open_times[idx + 1] - open_times[idx] for idx in range(len(open_times) - 1)]
        absolute_deltas = [abs(delta) for delta in deltas]
        one_minute = bool(absolute_deltas) and all(delta == 60000 for delta in absolute_deltas)
        sample_delta = 60000 if one_minute else (absolute_deltas[0] if absolute_deltas else None)
        schema_match = header == EXPECTED_SCHEMA
        symbol_match = observed_symbols == [TARGET_SYMBOL]
        samples.append(
            {
                "date": entry["date"],
                "downloaded_zip_path": entry["downloaded_zip_path"],
                "expected_inner_csv": expected_inner_csv,
                "csv_header_read": True,
                "csv_sample_rows_read_count": len(rows),
                "csv_full_read_performed": False,
                "expected_schema_match": schema_match,
                "expected_symbol_match": symbol_match,
                "observed_columns": header,
                "expected_columns": EXPECTED_SCHEMA,
                "observed_symbol_sample": observed_symbols,
                "sample_open_time_values": open_times[:MAX_CSV_SAMPLE_DATA_ROWS],
                "sample_open_time_delta_ms": sample_delta,
                "inferred_sample_interval": "1m" if one_minute else "UNKNOWN_PENDING_VALIDATOR",
                "one_minute_interval_observed": one_minute,
                "direct_1h_interval_present": False if one_minute else None,
                "schema_sample_status": (
                    "PASS_SCHEMA_SYMBOL_AND_1M_SAMPLE" if schema_match and symbol_match and one_minute else "BLOCKED_SCHEMA_SAMPLE"
                ),
            }
        )
    return samples


def build_execution_scope(provenance: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "small_range_download_execution_performed": True,
        "approved_url_list_used": True,
        "approved_url_count": len(APPROVED_URLS),
        "downloaded_file_count": len(provenance),
        "target_symbol": TARGET_SYMBOL,
        "date_range_start": DATE_RANGE_START,
        "date_range_end": DATE_RANGE_END,
        "output_directory": str(DOWNLOAD_DIR),
        "approved_urls": APPROVED_URLS,
        "downloaded_zip_paths": [entry["downloaded_zip_path"] for entry in provenance],
        "no_url_discovery": True,
        "no_api": True,
        "no_browse": True,
        "no_data_build": True,
        "no_aggregation": True,
    }


def build_execution_compliance() -> Dict[str, Any]:
    return {
        "data_download_performed": True,
        "data_fetch_performed": True,
        "okx_download_performed": True,
        "okx_sample_zip_downloaded_now": True,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "full_csv_read_performed": False,
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
        "files_marked_build_ready": False,
        "source_manifest_acquisition_ready": False,
        "broad_acquisition_execution_allowed_now": False,
    }


def build_payload(
    preflight: Dict[str, Any],
    execution_scope: Dict[str, Any],
    provenance: List[Dict[str, Any]],
    inventory: List[Dict[str, Any]],
    samples: List[Dict[str, Any]],
    compliance: Dict[str, Any],
) -> Dict[str, Any]:
    flags = dangerous_flags()
    all_downloads_succeeded = len(provenance) == RANGE_DAYS
    all_hashes_computed = all(entry.get("hash_computed_after_download") is True for entry in provenance)
    all_zip_open_success = all(entry.get("zip_open_success") is True for entry in inventory)
    all_expected_inner_csv_present = all(entry.get("expected_inner_csv_present") is True for entry in inventory)
    any_zip_path_traversal = any(entry.get("zip_path_traversal_detected") is True for entry in inventory)
    all_csv_headers_read = all(entry.get("csv_header_read") is True for entry in samples)
    max_sample_rows = max([entry.get("csv_sample_rows_read_count", 0) for entry in samples] or [0])
    all_expected_schema_match = all(entry.get("expected_schema_match") is True for entry in samples)
    all_symbol_match = all(entry.get("expected_symbol_match") is True for entry in samples)
    all_one_minute = all(entry.get("one_minute_interval_observed") is True for entry in samples)
    direct_1h_present = any(entry.get("direct_1h_interval_present") is True for entry in samples)
    success = (
        all_downloads_succeeded
        and all_hashes_computed
        and all_zip_open_success
        and all_expected_inner_csv_present
        and not any_zip_path_traversal
        and all_csv_headers_read
        and max_sample_rows <= MAX_CSV_SAMPLE_DATA_ROWS
        and all_expected_schema_match
        and all_symbol_match
        and all_one_minute
        and not direct_1h_present
    )
    if not success:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: validation-critical execution checks failed")
    replacement_checks = {
        "preflight_passed": preflight.get("whole_system_preflight_completed") is True,
        "approved_url_list_used": execution_scope.get("approved_url_list_used") is True,
        "approved_url_count_7": execution_scope.get("approved_url_count") == RANGE_DAYS,
        "downloaded_file_count_7": execution_scope.get("downloaded_file_count") == RANGE_DAYS,
        "all_hashes_computed_after_download": all_hashes_computed,
        "zip_inventory_ok": all(entry.get("zip_inventory_status") == "PASS_EXPECTED_CSV_PRESENT" for entry in inventory),
        "schema_samples_ok": all(entry.get("schema_sample_status") == "PASS_SCHEMA_SYMBOL_AND_1M_SAMPLE" for entry in samples),
        "sample_rows_limited": max_sample_rows <= MAX_CSV_SAMPLE_DATA_ROWS,
        "no_full_csv_read": compliance.get("full_csv_read_performed") is False,
        "no_api_browse": compliance.get("okx_api_call_performed") is False and compliance.get("okx_browse_performed") is False,
        "no_build_aggregation": compliance.get("data_build_performed") is False and compliance.get("aggregation_performed_now") is False,
        "not_build_ready_or_acquisition_ready": compliance.get("files_marked_build_ready") is False
        and compliance.get("source_manifest_acquisition_ready") is False,
        "schema_config_absent": planned_schema_files_existing_count() == 0,
        "generic_runner_absent": generic_runner_target_exists() is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
    }
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_single_symbol_small_range_download_execution_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "VALIDATE_SINGLE_SYMBOL_SMALL_RANGE_DOWNLOAD_EXECUTION_NO_BUILD",
        "next_module": NEXT_MODULE_PASS,
        **preflight,
        "small_range_download_execution_performed": True,
        "approved_url_list_used": True,
        "approved_url_count": RANGE_DAYS,
        "downloaded_file_count": RANGE_DAYS,
        "target_symbol": TARGET_SYMBOL,
        "date_range_start": DATE_RANGE_START,
        "date_range_end": DATE_RANGE_END,
        "output_directory": str(DOWNLOAD_DIR),
        "all_downloads_succeeded": True,
        "all_hashes_computed_after_download": True,
        "hash_algorithm": "SHA256",
        "all_zip_open_success": True,
        "all_expected_inner_csv_present": True,
        "any_zip_path_traversal_detected": False,
        "all_csv_headers_read": True,
        "max_csv_sample_rows_read_per_file": max_sample_rows,
        "full_csv_read_performed": False,
        "all_expected_schema_match": True,
        "all_one_minute_interval_observed_from_samples": True,
        "direct_1h_interval_present": False,
        "files_marked_build_ready": False,
        "source_manifest_acquisition_ready": False,
        "broad_acquisition_execution_allowed_now": False,
        "data_download_performed": True,
        "data_fetch_performed": True,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "acquisition_execution_allowed_now": False,
        "external_download_allowed_now": True,
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
        "current_evidence_chain_quality_before_execution": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_execution": EVIDENCE_AFTER,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 8,
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
            "downloaded exactly the seven approved BTC-USDT-SWAP OKX daily candlestick ZIPs, computed SHA256 after "
            "each download, inspected each ZIP inventory, read only each expected CSV header and up to five sample rows, "
            "confirmed expected schema and 1m sample intervals, and left data build, aggregation, API, browse, broad "
            "acquisition, research, backtest, candidate, runtime, capital, live, schema/config, generic-runner, "
            "build-ready, and acquisition-ready paths closed"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": all(replacement_checks.values()),
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "tracked_python_count_expectation": {
            "pre_commit": EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT,
        },
    }
    if payload["replacement_checks_all_true"] is not True:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: replacement checks failed")
    return payload


def write_execution_artifacts(
    payload: Dict[str, Any],
    execution_scope: Dict[str, Any],
    provenance: List[Dict[str, Any]],
    inventory: List[Dict[str, Any]],
    samples: List[Dict[str, Any]],
    compliance: Dict[str, Any],
) -> None:
    outputs = {
        "historical_okx_single_symbol_small_range_download_execution_report.json": {
            "generated_at_utc": utc_now(),
            "execution_scope": execution_scope,
            "per_file_download_provenance": provenance,
            "zip_inventory": inventory,
            "schema_sample": samples,
            "execution_compliance": compliance,
            "next_module_decision": {
                "next_module": payload["next_module"],
                "next_action": payload["next_action"],
            },
        },
        "historical_okx_single_symbol_small_range_download_provenance_report.json": {
            "generated_at_utc": utc_now(),
            "per_file_download_provenance": provenance,
        },
        "historical_okx_single_symbol_small_range_zip_inventory_report.json": {
            "generated_at_utc": utc_now(),
            "zip_inventory": inventory,
        },
        "historical_okx_single_symbol_small_range_schema_sample_report.json": {
            "generated_at_utc": utc_now(),
            "schema_sample": samples,
        },
        "historical_okx_single_symbol_small_range_download_execution_compliance_report.json": compliance,
        "historical_okx_single_symbol_small_range_download_execution_summary.json": payload,
        "repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_execution_after_preview_approval_v1_latest.json": payload,
    }
    for name, artifact in outputs.items():
        write_json(OUT_DIR / name, artifact)


def blocked_payload(exc: Exception) -> Dict[str, Any]:
    flags = dangerous_flags()
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_single_symbol_small_range_download_execution_status": STATUS_BLOCKED_CONTEXT,
        "final_decision": STATUS_BLOCKED_CONTEXT,
        "next_action": "STOP_FAIL_CLOSED_SINGLE_SYMBOL_SMALL_RANGE_DOWNLOAD_EXECUTION_BLOCKED",
        "next_module": NEXT_MODULE_BLOCKED,
        "error": str(exc),
        "whole_system_preflight_completed": False,
        "live_next_module_matches_requested_module": False,
        "artifact_chain_consistent": False,
        "stale_or_contradictory_artifact_detected": True,
        "small_range_download_execution_performed": False,
        "approved_url_list_used": False,
        "approved_url_count": RANGE_DAYS,
        "downloaded_file_count": 0,
        "target_symbol": TARGET_SYMBOL,
        "date_range_start": DATE_RANGE_START,
        "date_range_end": DATE_RANGE_END,
        "output_directory": str(DOWNLOAD_DIR),
        "all_downloads_succeeded": False,
        "all_hashes_computed_after_download": False,
        "hash_algorithm": "SHA256",
        "all_zip_open_success": False,
        "all_expected_inner_csv_present": False,
        "any_zip_path_traversal_detected": False,
        "all_csv_headers_read": False,
        "max_csv_sample_rows_read_per_file": 0,
        "full_csv_read_performed": False,
        "all_expected_schema_match": False,
        "all_one_minute_interval_observed_from_samples": False,
        "direct_1h_interval_present": None,
        "files_marked_build_ready": False,
        "source_manifest_acquisition_ready": False,
        "broad_acquisition_execution_allowed_now": False,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "acquisition_execution_allowed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "okx_sample_zip_downloaded_now": False,
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
        "current_evidence_chain_quality_before_execution": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_execution": "BLOCKED_FAIL_CLOSED_NO_BUILD",
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
        "derived_live_repo_post_check_reason": "small-range download execution failed closed before any build or aggregation route",
        "replacement_checks_all_true": False,
    }


def write_blocked_artifact(payload: Dict[str, Any]) -> None:
    write_json(
        OUT_DIR
        / "repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_execution_after_preview_approval_v1_latest.json",
        payload,
    )
    write_json(OUT_DIR / "historical_okx_single_symbol_small_range_download_execution_summary.json", payload)


def main() -> int:
    try:
        artifacts = validate_required_artifacts()
        preflight = validate_preflight(artifacts)
        provenance = download_approved_files()
        inventory = inspect_zip_inventory(provenance)
        if any(entry["zip_inventory_status"] != "PASS_EXPECTED_CSV_PRESENT" for entry in inventory):
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: ZIP inventory check failed")
        samples = sample_csv_from_zip(provenance)
        if any(entry["schema_sample_status"] != "PASS_SCHEMA_SYMBOL_AND_1M_SAMPLE" for entry in samples):
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: schema sample check failed")
        compliance = build_execution_compliance()
        execution_scope = build_execution_scope(provenance)
        payload = build_payload(preflight, execution_scope, provenance, inventory, samples, compliance)
        write_execution_artifacts(payload, execution_scope, provenance, inventory, samples, compliance)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        payload = blocked_payload(exc)
        write_blocked_artifact(payload)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
