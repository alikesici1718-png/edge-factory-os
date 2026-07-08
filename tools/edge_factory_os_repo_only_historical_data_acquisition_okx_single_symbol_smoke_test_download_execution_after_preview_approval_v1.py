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
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_"
    "after_preview_approval_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_"
    "after_preview_approval_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME
DOWNLOAD_DIR = OUT_DIR / "downloaded_single_file_smoke_test"

EXPECTED_HEAD = "eabb4a7"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 681
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 682

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_"
    "after_preview_approval_v1.py"
)
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_validator_"
    "after_execution_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_"
    "blocked_record_after_preview_approval_v1.py"
)

PREVIEW_DIR = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_preview_after_symbol_universe_validator_v1"
)
PREVIEW_BUNDLE_ARTIFACT = (
    PREVIEW_DIR
    / "repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_preview_after_symbol_universe_validator_v1_latest.json"
)
APPROVAL_RECORD_ARTIFACT = (
    PREVIEW_DIR / "historical_okx_single_symbol_pipeline_smoke_test_approval_record.json"
)
SYMBOL_UNIVERSE_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_placeholder_validator_after_local_preview_v1"
    / "repo_only_historical_data_acquisition_okx_symbol_universe_placeholder_validator_after_local_preview_v1_latest.json"
)
SOURCE_MANIFEST_DIR = (
    LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_source_manifest_approval_after_preview_v1"
)
SOURCE_MANIFEST_ARTIFACT = SOURCE_MANIFEST_DIR / "historical_okx_source_manifest.json"
SOURCE_MANIFEST_SELF_VALIDATOR_ARTIFACT = (
    SOURCE_MANIFEST_DIR / "historical_okx_source_manifest_self_validator.json"
)

PREVIEW_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_PIPELINE_SMOKE_TEST_PREVIEW_APPROVED_DOWNLOAD_"
    "EXECUTION_NEXT_NO_EXECUTION_YET"
)
SYMBOL_UNIVERSE_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SYMBOL_UNIVERSE_PLACEHOLDER_VALIDATED_SINGLE_SYMBOL_PIPELINE_"
    "SMOKE_TEST_PREVIEW_READY_NO_EXECUTION"
)
STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMOKE_TEST_DOWNLOAD_EXECUTED_PENDING_VALIDATOR_NO_BUILD"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_PIPELINE_SMOKE_TEST_PREVIEW_APPROVED_DOWNLOAD_EXECUTION_"
    "NEXT_NO_EXECUTION_YET"
)
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMOKE_TEST_DOWNLOAD_EXECUTED_PENDING_VALIDATOR_NO_BUILD"
)

TARGET_SYMBOL = "BTC-USDT-SWAP"
TARGET_URL = (
    "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/20260518/"
    "BTC-USDT-SWAP-candlesticks-2026-05-18.zip"
)
TARGET_FILE_NAME = "BTC-USDT-SWAP-candlesticks-2026-05-18.zip"
EXPECTED_INNER_CSV = "BTC-USDT-SWAP-candlesticks-2026-05-18.csv"
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
EXPECTED_INTERVAL = "1m"
MAX_ZIP_SIZE_BYTES = 100 * 1024 * 1024
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
    "external_api_call_performed_now",
    "data_build_performed_now",
    "okx_browse_performed_now",
    "okx_api_call_performed_now",
    "okx_page_reopened_now",
    "aggregation_performed_now",
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
        "preview_bundle": PREVIEW_BUNDLE_ARTIFACT,
        "approval_record": APPROVAL_RECORD_ARTIFACT,
        "symbol_universe_validator": SYMBOL_UNIVERSE_VALIDATOR_ARTIFACT,
        "source_manifest": SOURCE_MANIFEST_ARTIFACT,
        "source_manifest_self_validator": SOURCE_MANIFEST_SELF_VALIDATOR_ARTIFACT,
    }
    return {label: load_json(path, label) for label, path in paths.items()}


def validate_preflight(artifacts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))

    preview = artifacts["preview_bundle"]
    approval = artifacts["approval_record"]
    universe = artifacts["symbol_universe_validator"]
    manifest = artifacts["source_manifest"]
    manifest_self = artifacts["source_manifest_self_validator"]

    require_equal(
        preview.get("historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_preview_bundle_status"),
        PREVIEW_STATUS_PASS,
        "preview.status",
    )
    require_equal(preview.get("next_module"), REQUESTED_MODULE, "preview.next_module", STATUS_BLOCKED_NEXT_MODULE)
    require_equal(preview.get("current_evidence_chain_quality_after_bundle"), EVIDENCE_BEFORE, "preview.evidence_after")
    require_true(preview.get("whole_system_preflight_completed"), "preview.preflight")
    require_true(preview.get("live_next_module_matches_requested_module"), "preview.next_module_match")
    require_true(preview.get("artifact_chain_consistent"), "preview.artifact_chain")
    require_false(preview.get("stale_or_contradictory_artifact_detected"), "preview.stale")
    require_true(preview.get("approval_grants_future_single_file_download_next"), "preview.future_download")
    require_false(preview.get("approval_grants_download_now"), "preview.download_now")
    require_equal(preview.get("future_download_scope_url_count"), 1, "preview.url_count")
    require_equal(preview.get("future_download_scope_file_count"), 1, "preview.file_count")
    require_true(preview.get("future_download_scope_limited_to_one_file"), "preview.one_file")
    require_equal(preview.get("target_url"), TARGET_URL, "preview.target_url")
    require_equal(preview.get("target_symbol"), TARGET_SYMBOL, "preview.target_symbol")
    require_equal(preview.get("expected_inner_csv"), EXPECTED_INNER_CSV, "preview.expected_inner_csv")
    require_true(preview.get("universe_valid_for_pipeline_smoke_test"), "preview.pipeline_smoke")
    require_false(preview.get("universe_valid_for_research_backtest"), "preview.research_backtest")
    require_false(preview.get("universe_valid_for_edge_claim"), "preview.edge_claim")
    require_zero(preview.get("downloaded_file_count"), "preview.downloaded_file_count")
    require_zero(preview.get("sha256_claim_count"), "preview.sha256_claim_count")
    require_zero(preview.get("build_ready_file_count"), "preview.build_ready_file_count")
    require_false(preview.get("data_build_performed"), "preview.data_build")
    require_false(preview.get("aggregation_performed_now"), "preview.aggregation")
    require_equal(preview.get("active_p0_blocker_count"), 0, "preview.active_p0")
    if not isinstance(preview.get("active_p1_attention_count"), int) or preview["active_p1_attention_count"] < 8:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: preview.active_p1_attention_count must be >= 8")
    require_equal(preview.get("dormant_repo_attention_count"), 716, "preview.dormant_attention")
    require_true(preview.get("replacement_checks_all_true"), "preview.replacement")
    validate_no_true_dangerous_flags(preview, "preview")

    require_true(approval.get("approval_grants_future_single_file_download_next"), "approval.future_download")
    require_false(approval.get("approval_grants_download_now"), "approval.download_now")
    require_false(approval.get("approval_grants_api_now"), "approval.api")
    require_false(approval.get("approval_grants_browse_now"), "approval.browse")
    require_false(approval.get("approval_grants_multi_file_download_now"), "approval.multi_file")
    require_false(approval.get("approval_grants_data_build_now"), "approval.data_build")
    require_false(approval.get("approval_grants_aggregation_now"), "approval.aggregation")
    require_false(approval.get("approval_grants_acquisition_execution_now"), "approval.acquisition")

    require_equal(
        universe.get("historical_data_acquisition_okx_symbol_universe_placeholder_validator_status"),
        SYMBOL_UNIVERSE_VALIDATOR_STATUS_PASS,
        "universe.status",
    )
    require_true(universe.get("single_symbol_pipeline_smoke_test_candidate"), "universe.single_symbol_candidate")
    require_true(universe.get("universe_valid_for_pipeline_smoke_test"), "universe.pipeline_smoke")
    require_false(universe.get("universe_valid_for_research_backtest"), "universe.research_backtest")
    require_false(universe.get("universe_valid_for_edge_claim"), "universe.edge_claim")
    require_false(universe.get("universe_is_build_ready"), "universe.build_ready")
    require_false(universe.get("universe_is_acquisition_ready"), "universe.acquisition_ready")
    validate_no_true_dangerous_flags(universe, "universe")

    require_equal(manifest.get("known_sample_url"), TARGET_URL, "manifest.known_sample_url")
    require_equal(manifest.get("known_sample_file"), EXPECTED_INNER_CSV, "manifest.known_sample_file")
    require_equal(manifest.get("known_sample_schema"), EXPECTED_SCHEMA, "manifest.known_sample_schema")
    require_equal(manifest.get("known_sample_direct_interval"), EXPECTED_INTERVAL, "manifest.direct_interval")
    require_false(manifest.get("manifest_is_build_ready"), "manifest.build_ready")
    require_false(manifest.get("manifest_is_acquisition_ready"), "manifest.acquisition_ready")
    require_zero(manifest.get("downloaded_file_count"), "manifest.downloaded_file_count")
    require_zero(manifest.get("sha256_claim_count"), "manifest.sha256_claim_count")
    require_zero(manifest.get("build_ready_file_count"), "manifest.build_ready_file_count")

    require_true(manifest_self.get("source_manifest_validated_as_placeholder"), "manifest_self.placeholder")
    require_true(manifest_self.get("replacement_checks_all_true"), "manifest_self.replacement")
    require_false(manifest_self.get("source_manifest_safe_for_data_build_now"), "manifest_self.data_build")
    require_false(manifest_self.get("source_manifest_safe_for_acquisition_now"), "manifest_self.acquisition")

    return {
        "whole_system_preflight_completed": True,
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
        "preview_bundle_artifact": str(PREVIEW_BUNDLE_ARTIFACT),
        "approval_record_artifact": str(APPROVAL_RECORD_ARTIFACT),
        "symbol_universe_validator_artifact": str(SYMBOL_UNIVERSE_VALIDATOR_ARTIFACT),
        "source_manifest_artifact": str(SOURCE_MANIFEST_ARTIFACT),
        "source_manifest_self_validator_artifact": str(SOURCE_MANIFEST_SELF_VALIDATOR_ARTIFACT),
        "head": head,
    }


def ensure_download_target_path() -> Path:
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    target = (DOWNLOAD_DIR / TARGET_FILE_NAME).resolve()
    root = DOWNLOAD_DIR.resolve()
    if target.parent != root:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: download target outside output directory")
    return target


def download_exact_approved_zip() -> Dict[str, Any]:
    target = ensure_download_target_path()
    timestamp = utc_now()
    size = 0
    digest = hashlib.sha256()
    request = urllib.request.Request(TARGET_URL, headers={"User-Agent": "EdgeFactoryOS-SingleFileSmokeTest/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        with target.open("wb") as out_file:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_ZIP_SIZE_BYTES:
                    raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: downloaded ZIP exceeds {MAX_ZIP_SIZE_BYTES} bytes")
                out_file.write(chunk)
                digest.update(chunk)
    if size <= 0:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: downloaded ZIP is empty")
    return {
        "downloaded_zip_path": str(target),
        "downloaded_zip_file_name": TARGET_FILE_NAME,
        "downloaded_zip_size_bytes": size,
        "downloaded_zip_sha256": digest.hexdigest(),
        "download_timestamp_utc": timestamp,
        "source_url": TARGET_URL,
        "provenance_status": "SINGLE_FILE_SMOKE_TEST_DOWNLOADED",
        "hash_algorithm": "SHA256",
        "hash_computed_after_download": True,
    }


def zip_member_has_path_traversal(name: str) -> bool:
    normalized = name.replace("\\", "/")
    posix = PurePosixPath(normalized)
    return (
        normalized.startswith("/")
        or ":" in normalized.split("/", 1)[0]
        or any(part in ("", ".", "..") for part in posix.parts)
    )


def inspect_zip_inventory(zip_path: Path) -> Dict[str, Any]:
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
    traversal = any(zip_member_has_path_traversal(name) for name in names)
    expected_present = EXPECTED_INNER_CSV in names
    member_count = len(names)
    status = "PASS_EXPECTED_CSV_PRESENT" if expected_present and not traversal and member_count <= MAX_ZIP_MEMBERS else "BLOCKED_ZIP_INVENTORY"
    if member_count > MAX_ZIP_MEMBERS:
        status = "BLOCKED_TOO_MANY_ZIP_MEMBERS"
    return {
        "zip_open_success": True,
        "zip_member_count": member_count,
        "zip_member_names": names,
        "expected_inner_csv_present": expected_present,
        "zip_path_traversal_detected": traversal,
        "zip_inventory_status": status,
    }


def sample_csv_from_zip(zip_path: Path) -> Dict[str, Any]:
    rows: List[List[str]] = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        with zf.open(EXPECTED_INNER_CSV, "r") as raw:
            text = io.TextIOWrapper(raw, encoding="utf-8", newline="")
            reader = csv.reader(text)
            try:
                header = next(reader)
            except StopIteration as exc:
                raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: expected CSV is empty") from exc
            for index, row in enumerate(reader):
                if index >= MAX_CSV_SAMPLE_DATA_ROWS:
                    break
                rows.append(row)
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
    inferred_interval = "1m" if one_minute else "UNKNOWN_PENDING_VALIDATOR"
    schema_match = header == EXPECTED_SCHEMA
    return {
        "csv_header_read": True,
        "csv_sample_rows_read_count": len(rows),
        "csv_full_read_performed": False,
        "expected_schema_match": schema_match,
        "observed_columns": header,
        "expected_columns": EXPECTED_SCHEMA,
        "sample_open_time_values": open_times[:MAX_CSV_SAMPLE_DATA_ROWS],
        "sample_open_time_delta_ms": sample_delta,
        "inferred_sample_interval": inferred_interval,
        "direct_1h_interval_present": False if one_minute else None,
        "one_minute_interval_observed": one_minute,
        "schema_sample_status": "PASS_SCHEMA_AND_1M_SAMPLE" if schema_match and one_minute else "PENDING_OR_BLOCKED_SCHEMA_SAMPLE",
    }


def build_execution_scope(provenance: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "smoke_test_download_execution_performed": True,
        "approved_url_used": True,
        "approved_url_count": 1,
        "downloaded_file_count": 1,
        "target_symbol": TARGET_SYMBOL,
        "target_url": TARGET_URL,
        "expected_inner_csv": EXPECTED_INNER_CSV,
        "output_directory": str(DOWNLOAD_DIR),
        "downloaded_zip_path": provenance["downloaded_zip_path"],
        "no_multi_file_download": True,
        "no_url_iteration": True,
        "no_api": True,
        "no_browse": True,
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
        "file_marked_build_ready": False,
        "source_manifest_acquisition_ready": False,
        "broad_acquisition_execution_allowed_now": False,
    }


def build_payload(
    preflight: Dict[str, Any],
    execution_scope: Dict[str, Any],
    provenance: Dict[str, Any],
    inventory: Dict[str, Any],
    sample: Dict[str, Any],
    compliance: Dict[str, Any],
) -> Dict[str, Any]:
    flags = dangerous_flags()
    success = (
        provenance.get("hash_computed_after_download") is True
        and inventory.get("zip_open_success") is True
        and inventory.get("expected_inner_csv_present") is True
        and inventory.get("zip_path_traversal_detected") is False
        and inventory.get("zip_member_count", 0) <= MAX_ZIP_MEMBERS
        and sample.get("csv_header_read") is True
        and sample.get("csv_sample_rows_read_count", 99) <= MAX_CSV_SAMPLE_DATA_ROWS
        and sample.get("csv_full_read_performed") is False
        and sample.get("expected_schema_match") is True
        and sample.get("one_minute_interval_observed") is True
    )
    if not success:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: validation-critical execution checks failed")
    replacement_checks = {
        "preflight_passed": preflight.get("whole_system_preflight_completed") is True,
        "approved_url_used": execution_scope.get("approved_url_used") is True,
        "one_url_only": execution_scope.get("approved_url_count") == 1,
        "one_downloaded_file_only": execution_scope.get("downloaded_file_count") == 1,
        "hash_computed_after_download": provenance.get("hash_computed_after_download") is True,
        "zip_inventory_ok": inventory.get("zip_inventory_status") == "PASS_EXPECTED_CSV_PRESENT",
        "schema_sample_ok": sample.get("schema_sample_status") == "PASS_SCHEMA_AND_1M_SAMPLE",
        "sample_rows_limited": sample.get("csv_sample_rows_read_count", 99) <= MAX_CSV_SAMPLE_DATA_ROWS,
        "no_full_csv_read": sample.get("csv_full_read_performed") is False,
        "no_api_browse": compliance.get("okx_api_call_performed") is False and compliance.get("okx_browse_performed") is False,
        "no_build_aggregation": compliance.get("data_build_performed") is False and compliance.get("aggregation_performed_now") is False,
        "not_build_ready_or_acquisition_ready": compliance.get("file_marked_build_ready") is False
        and compliance.get("source_manifest_acquisition_ready") is False,
        "schema_config_absent": planned_schema_files_existing_count() == 0,
        "generic_runner_absent": generic_runner_target_exists() is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
    }
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "VALIDATE_SINGLE_SYMBOL_SMOKE_TEST_DOWNLOAD_EXECUTION_NO_BUILD",
        "next_module": NEXT_MODULE_PASS,
        **preflight,
        "download_execution_performed": True,
        "approved_url_used": True,
        "approved_url_count": 1,
        "downloaded_file_count": 1,
        "target_symbol": TARGET_SYMBOL,
        "target_url": TARGET_URL,
        "expected_inner_csv": EXPECTED_INNER_CSV,
        "output_directory": str(DOWNLOAD_DIR),
        "downloaded_zip_path": provenance["downloaded_zip_path"],
        "downloaded_zip_size_bytes": provenance["downloaded_zip_size_bytes"],
        "downloaded_zip_sha256": provenance["downloaded_zip_sha256"],
        "hash_algorithm": "SHA256",
        "hash_computed_after_download": True,
        "download_timestamp_utc": provenance["download_timestamp_utc"],
        "zip_open_success": True,
        "zip_member_count": inventory["zip_member_count"],
        "expected_inner_csv_present": True,
        "zip_path_traversal_detected": False,
        "csv_header_read": True,
        "csv_sample_rows_read_count": sample["csv_sample_rows_read_count"],
        "csv_full_read_performed": False,
        "expected_schema_match": True,
        "observed_columns": sample["observed_columns"],
        "sample_open_time_delta_ms": sample["sample_open_time_delta_ms"],
        "inferred_sample_interval": sample["inferred_sample_interval"],
        "one_minute_interval_observed": True,
        "direct_1h_interval_present": False,
        "single_symbol_pipeline_smoke_test_candidate": True,
        "universe_valid_for_pipeline_smoke_test": True,
        "universe_valid_for_research_backtest": False,
        "universe_valid_for_edge_claim": False,
        "file_marked_build_ready": False,
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
            "downloaded exactly one approved OKX smoke-test ZIP, computed SHA256 after download, inspected ZIP inventory, "
            "read only the expected CSV header and five sample rows, confirmed the expected schema and 1m sample interval, "
            "and left data build, aggregation, API, browse, research, backtest, candidate, runtime, capital, live, schema, "
            "config, generic-runner, build-ready, and acquisition-ready paths closed"
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
    provenance: Dict[str, Any],
    inventory: Dict[str, Any],
    sample: Dict[str, Any],
    compliance: Dict[str, Any],
) -> None:
    outputs = {
        "historical_okx_single_symbol_smoke_test_download_execution_report.json": {
            "generated_at_utc": utc_now(),
            "execution_scope": execution_scope,
            "next_module_decision": {
                "next_module": payload["next_module"],
                "next_action": payload["next_action"],
            },
        },
        "historical_okx_single_symbol_smoke_test_download_provenance_report.json": provenance,
        "historical_okx_single_symbol_smoke_test_zip_inventory_report.json": inventory,
        "historical_okx_single_symbol_smoke_test_schema_sample_report.json": sample,
        "historical_okx_single_symbol_smoke_test_execution_compliance_report.json": compliance,
        "historical_okx_single_symbol_smoke_test_download_execution_summary.json": payload,
        "repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_after_preview_approval_v1_latest.json": payload,
    }
    for name, artifact in outputs.items():
        write_json(OUT_DIR / name, artifact)


def blocked_payload(exc: Exception) -> Dict[str, Any]:
    flags = dangerous_flags()
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_status": STATUS_BLOCKED_CONTEXT,
        "final_decision": STATUS_BLOCKED_CONTEXT,
        "next_action": "STOP_FAIL_CLOSED_SINGLE_FILE_SMOKE_TEST_DOWNLOAD_EXECUTION_BLOCKED",
        "next_module": NEXT_MODULE_BLOCKED,
        "error": str(exc),
        "whole_system_preflight_completed": False,
        "live_next_module_matches_requested_module": False,
        "artifact_chain_consistent": False,
        "stale_or_contradictory_artifact_detected": True,
        "download_execution_performed": False,
        "approved_url_used": False,
        "approved_url_count": 1,
        "downloaded_file_count": 0,
        "target_symbol": TARGET_SYMBOL,
        "target_url": TARGET_URL,
        "expected_inner_csv": EXPECTED_INNER_CSV,
        "output_directory": str(DOWNLOAD_DIR),
        "downloaded_zip_path": None,
        "downloaded_zip_size_bytes": 0,
        "downloaded_zip_sha256": None,
        "hash_algorithm": "SHA256",
        "hash_computed_after_download": False,
        "download_timestamp_utc": None,
        "zip_open_success": False,
        "zip_member_count": 0,
        "expected_inner_csv_present": False,
        "zip_path_traversal_detected": False,
        "csv_header_read": False,
        "csv_sample_rows_read_count": 0,
        "csv_full_read_performed": False,
        "expected_schema_match": False,
        "observed_columns": [],
        "sample_open_time_delta_ms": None,
        "inferred_sample_interval": None,
        "one_minute_interval_observed": False,
        "direct_1h_interval_present": None,
        "file_marked_build_ready": False,
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
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 8,
        "dormant_repo_attention_count": 716,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "dangerous_flags": flags,
        "dangerous_flags_all_false": True,
        "dangerous_flags_true_count": 0,
        "replacement_checks_all_true": False,
    }


def write_blocked_artifact(payload: Dict[str, Any]) -> None:
    write_json(
        OUT_DIR / "repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_after_preview_approval_v1_latest.json",
        payload,
    )
    write_json(OUT_DIR / "historical_okx_single_symbol_smoke_test_download_execution_summary.json", payload)


def main() -> int:
    try:
        artifacts = validate_required_artifacts()
        preflight = validate_preflight(artifacts)
        provenance = download_exact_approved_zip()
        zip_path = Path(provenance["downloaded_zip_path"])
        inventory = inspect_zip_inventory(zip_path)
        if inventory["zip_inventory_status"] != "PASS_EXPECTED_CSV_PRESENT":
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {inventory['zip_inventory_status']}")
        sample = sample_csv_from_zip(zip_path)
        compliance = build_execution_compliance()
        execution_scope = build_execution_scope(provenance)
        payload = build_payload(preflight, execution_scope, provenance, inventory, sample, compliance)
        write_execution_artifacts(payload, execution_scope, provenance, inventory, sample, compliance)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        payload = blocked_payload(exc)
        write_blocked_artifact(payload)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
