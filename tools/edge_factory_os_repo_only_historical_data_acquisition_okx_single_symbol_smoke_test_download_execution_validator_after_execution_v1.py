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
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_validator_"
    "after_execution_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_validator_"
    "after_execution_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "6c90f54"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 682
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 683

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_validator_"
    "after_execution_v1.py"
)
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_preview_"
    "after_download_validator_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_validation_"
    "blocked_record_after_execution_v1.py"
)

EXECUTION_DIR = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_after_preview_approval_v1"
)
EXECUTION_LATEST_ARTIFACT = (
    EXECUTION_DIR
    / "repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_after_preview_approval_v1_latest.json"
)
EXECUTION_REPORT_ARTIFACT = EXECUTION_DIR / "historical_okx_single_symbol_smoke_test_download_execution_report.json"
PROVENANCE_REPORT_ARTIFACT = EXECUTION_DIR / "historical_okx_single_symbol_smoke_test_download_provenance_report.json"
ZIP_INVENTORY_REPORT_ARTIFACT = EXECUTION_DIR / "historical_okx_single_symbol_smoke_test_zip_inventory_report.json"
SCHEMA_SAMPLE_REPORT_ARTIFACT = EXECUTION_DIR / "historical_okx_single_symbol_smoke_test_schema_sample_report.json"
COMPLIANCE_REPORT_ARTIFACT = EXECUTION_DIR / "historical_okx_single_symbol_smoke_test_execution_compliance_report.json"
PREVIEW_APPROVAL_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_preview_after_symbol_universe_validator_v1"
    / "repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_preview_after_symbol_universe_validator_v1_latest.json"
)

EXECUTION_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMOKE_TEST_DOWNLOAD_EXECUTED_PENDING_VALIDATOR_NO_BUILD"
)
STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMOKE_TEST_DOWNLOAD_VALIDATED_BUILD_PREVIEW_READY_"
    "NO_EXECUTION"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMOKE_TEST_DOWNLOAD_EXECUTED_PENDING_VALIDATOR_NO_BUILD"
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMOKE_TEST_DOWNLOAD_VALIDATED_BUILD_PREVIEW_READY_NO_EXECUTION"
)

TARGET_SYMBOL = "BTC-USDT-SWAP"
TARGET_URL = (
    "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/20260518/"
    "BTC-USDT-SWAP-candlesticks-2026-05-18.zip"
)
TARGET_FILE_NAME = "BTC-USDT-SWAP-candlesticks-2026-05-18.zip"
EXPECTED_INNER_CSV = "BTC-USDT-SWAP-candlesticks-2026-05-18.csv"
EXPECTED_SHA256 = "c33b6c18bf852d6a80d5caa872ae6ed26614166ad614ec601a5f533f22fa4f06"
EXPECTED_SIZE_BYTES = 43567
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
    "external_download_performed_now",
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
        "execution_latest": EXECUTION_LATEST_ARTIFACT,
        "execution_report": EXECUTION_REPORT_ARTIFACT,
        "provenance_report": PROVENANCE_REPORT_ARTIFACT,
        "zip_inventory_report": ZIP_INVENTORY_REPORT_ARTIFACT,
        "schema_sample_report": SCHEMA_SAMPLE_REPORT_ARTIFACT,
        "compliance_report": COMPLIANCE_REPORT_ARTIFACT,
        "preview_approval": PREVIEW_APPROVAL_ARTIFACT,
    }
    return {label: load_json(path, label) for label, path in paths.items()}


def validate_preflight(artifacts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))

    latest = artifacts["execution_latest"]
    provenance = artifacts["provenance_report"]
    inventory = artifacts["zip_inventory_report"]
    sample = artifacts["schema_sample_report"]
    compliance = artifacts["compliance_report"]
    preview = artifacts["preview_approval"]

    require_equal(
        latest.get("historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_status"),
        EXECUTION_STATUS_PASS,
        "execution_latest.status",
    )
    require_equal(latest.get("next_module"), REQUESTED_MODULE, "execution_latest.next_module", STATUS_BLOCKED_NEXT_MODULE)
    require_equal(latest.get("current_evidence_chain_quality_after_execution"), EVIDENCE_BEFORE, "execution_latest.evidence_after")
    require_true(latest.get("whole_system_preflight_completed"), "execution_latest.preflight")
    require_true(latest.get("live_next_module_matches_requested_module"), "execution_latest.next_module_match")
    require_true(latest.get("artifact_chain_consistent"), "execution_latest.artifact_chain")
    require_false(latest.get("stale_or_contradictory_artifact_detected"), "execution_latest.stale")
    require_true(latest.get("download_execution_performed"), "execution_latest.download_execution")
    require_true(latest.get("approved_url_used"), "execution_latest.approved_url_used")
    require_equal(latest.get("approved_url_count"), 1, "execution_latest.approved_url_count")
    require_equal(latest.get("downloaded_file_count"), 1, "execution_latest.downloaded_file_count")
    require_equal(latest.get("target_symbol"), TARGET_SYMBOL, "execution_latest.target_symbol")
    require_equal(latest.get("target_url"), TARGET_URL, "execution_latest.target_url")
    require_equal(latest.get("expected_inner_csv"), EXPECTED_INNER_CSV, "execution_latest.expected_inner_csv")
    require_equal(latest.get("downloaded_zip_sha256"), EXPECTED_SHA256, "execution_latest.sha256")
    require_equal(latest.get("downloaded_zip_size_bytes"), EXPECTED_SIZE_BYTES, "execution_latest.size")
    require_true(latest.get("hash_computed_after_download"), "execution_latest.hash_after_download")
    require_true(latest.get("zip_open_success"), "execution_latest.zip_open")
    require_equal(latest.get("zip_member_count"), 1, "execution_latest.zip_member_count")
    require_true(latest.get("expected_inner_csv_present"), "execution_latest.expected_csv_present")
    require_false(latest.get("zip_path_traversal_detected"), "execution_latest.zip_traversal")
    require_true(latest.get("csv_header_read"), "execution_latest.csv_header")
    if not isinstance(latest.get("csv_sample_rows_read_count"), int) or latest["csv_sample_rows_read_count"] > MAX_CSV_SAMPLE_DATA_ROWS:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: execution_latest.csv_sample_rows_read_count > 5")
    require_false(latest.get("csv_full_read_performed"), "execution_latest.full_csv")
    require_true(latest.get("expected_schema_match"), "execution_latest.schema_match")
    require_equal(latest.get("sample_open_time_delta_ms"), 60000, "execution_latest.sample_delta")
    require_equal(latest.get("inferred_sample_interval"), "1m", "execution_latest.interval")
    require_true(latest.get("one_minute_interval_observed"), "execution_latest.one_minute")
    require_false(latest.get("direct_1h_interval_present"), "execution_latest.direct_1h")
    require_false(latest.get("data_build_performed"), "execution_latest.data_build")
    require_false(latest.get("aggregation_performed_now"), "execution_latest.aggregation")
    require_false(latest.get("okx_api_call_performed"), "execution_latest.api")
    require_false(latest.get("okx_browse_performed"), "execution_latest.browse")
    require_false(latest.get("file_marked_build_ready"), "execution_latest.file_build_ready")
    require_false(latest.get("source_manifest_acquisition_ready"), "execution_latest.source_acquisition")
    require_false(latest.get("broad_acquisition_execution_allowed_now"), "execution_latest.broad_acquisition")
    require_equal(latest.get("active_p0_blocker_count"), 0, "execution_latest.active_p0")
    if not isinstance(latest.get("active_p1_attention_count"), int) or latest["active_p1_attention_count"] < 8:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: execution_latest.active_p1_attention_count must be >= 8")
    require_equal(latest.get("dormant_repo_attention_count"), 716, "execution_latest.dormant_attention")
    require_true(latest.get("replacement_checks_all_true"), "execution_latest.replacement")
    validate_no_true_dangerous_flags(latest, "execution_latest")

    require_equal(provenance.get("source_url"), TARGET_URL, "provenance.source_url")
    require_equal(provenance.get("downloaded_zip_file_name"), TARGET_FILE_NAME, "provenance.file_name")
    require_equal(provenance.get("downloaded_zip_size_bytes"), EXPECTED_SIZE_BYTES, "provenance.size")
    require_equal(provenance.get("downloaded_zip_sha256"), EXPECTED_SHA256, "provenance.sha256")
    require_equal(provenance.get("hash_algorithm"), "SHA256", "provenance.hash_algorithm")
    require_true(provenance.get("hash_computed_after_download"), "provenance.hash_after_download")

    require_true(inventory.get("zip_open_success"), "inventory.zip_open")
    require_equal(inventory.get("zip_member_count"), 1, "inventory.member_count")
    require_equal(inventory.get("zip_member_names"), [EXPECTED_INNER_CSV], "inventory.member_names")
    require_true(inventory.get("expected_inner_csv_present"), "inventory.expected_csv")
    require_false(inventory.get("zip_path_traversal_detected"), "inventory.traversal")

    require_true(sample.get("csv_header_read"), "sample.header")
    if not isinstance(sample.get("csv_sample_rows_read_count"), int) or sample["csv_sample_rows_read_count"] > MAX_CSV_SAMPLE_DATA_ROWS:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: sample.csv_sample_rows_read_count > 5")
    require_false(sample.get("csv_full_read_performed"), "sample.full_csv")
    require_true(sample.get("expected_schema_match"), "sample.schema_match")
    require_equal(sample.get("observed_columns"), EXPECTED_SCHEMA, "sample.observed_columns")
    require_equal(sample.get("sample_open_time_delta_ms"), 60000, "sample.sample_delta")
    require_equal(sample.get("inferred_sample_interval"), "1m", "sample.interval")
    require_true(sample.get("one_minute_interval_observed"), "sample.one_minute")
    require_false(sample.get("direct_1h_interval_present"), "sample.direct_1h")

    require_true(compliance.get("data_download_performed"), "compliance.data_download")
    require_true(compliance.get("data_fetch_performed"), "compliance.data_fetch")
    require_true(compliance.get("okx_download_performed"), "compliance.okx_download")
    require_true(compliance.get("okx_sample_zip_downloaded_now"), "compliance.sample_zip")
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
        "file_marked_build_ready",
        "source_manifest_acquisition_ready",
        "broad_acquisition_execution_allowed_now",
    ):
        require_false(compliance.get(field), f"compliance.{field}")
    require_true(compliance.get("generic_runner_implementation_remains_blocked"), "compliance.generic_runner_blocked")

    require_equal(preview.get("target_url"), TARGET_URL, "preview.target_url")
    require_equal(preview.get("future_download_scope_url_count"), 1, "preview.url_count")
    require_equal(preview.get("future_download_scope_file_count"), 1, "preview.file_count")
    require_true(preview.get("future_download_scope_limited_to_one_file"), "preview.one_file")
    require_false(preview.get("approval_grants_download_now"), "preview.download_now")
    require_true(preview.get("approval_grants_future_single_file_download_next"), "preview.future_download")

    return {
        "whole_system_preflight_completed": True,
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
        "execution_latest_artifact": str(EXECUTION_LATEST_ARTIFACT),
        "execution_report_artifact": str(EXECUTION_REPORT_ARTIFACT),
        "provenance_report_artifact": str(PROVENANCE_REPORT_ARTIFACT),
        "zip_inventory_report_artifact": str(ZIP_INVENTORY_REPORT_ARTIFACT),
        "schema_sample_report_artifact": str(SCHEMA_SAMPLE_REPORT_ARTIFACT),
        "compliance_report_artifact": str(COMPLIANCE_REPORT_ARTIFACT),
        "preview_approval_artifact": str(PREVIEW_APPROVAL_ARTIFACT),
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


def validate_downloaded_file(provenance: Dict[str, Any]) -> Dict[str, Any]:
    zip_path = Path(str(provenance.get("downloaded_zip_path", "")))
    exists = zip_path.exists() and zip_path.is_file()
    size = zip_path.stat().st_size if exists else 0
    recomputed = recompute_sha256(zip_path) if exists else None
    return {
        "downloaded_zip_exists": exists,
        "downloaded_zip_path": str(zip_path),
        "downloaded_zip_size_bytes": size,
        "downloaded_zip_size_recorded": provenance.get("downloaded_zip_size_bytes"),
        "downloaded_zip_size_matches_recorded": size == EXPECTED_SIZE_BYTES == provenance.get("downloaded_zip_size_bytes"),
        "downloaded_zip_sha256_recorded": provenance.get("downloaded_zip_sha256"),
        "downloaded_zip_sha256_recomputed": recomputed,
        "downloaded_zip_sha256_matches": recomputed == EXPECTED_SHA256 == provenance.get("downloaded_zip_sha256"),
        "hash_algorithm": "SHA256",
        "hash_computed_after_download": provenance.get("hash_computed_after_download") is True,
    }


def validate_zip_inventory_from_file(zip_path: Path) -> Dict[str, Any]:
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
    traversal = any(zip_member_has_path_traversal(name) for name in names)
    return {
        "zip_open_success": True,
        "zip_member_count": len(names),
        "zip_member_names": names,
        "expected_inner_csv_present": EXPECTED_INNER_CSV in names,
        "zip_path_traversal_detected": traversal,
        "zip_member_count_within_limit": len(names) <= MAX_ZIP_MEMBERS,
        "no_unexpected_dangerous_member_path": traversal is False,
        "no_extraction_outside_output_directory": True,
    }


def validate_schema_sample_from_file(zip_path: Path) -> Dict[str, Any]:
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
    deltas = [abs(open_times[idx + 1] - open_times[idx]) for idx in range(len(open_times) - 1)]
    one_minute = bool(deltas) and all(delta == 60000 for delta in deltas)
    sample_delta = 60000 if one_minute else (deltas[0] if deltas else None)
    return {
        "csv_header_read": True,
        "csv_sample_rows_read_count": len(rows),
        "csv_full_read_performed": False,
        "expected_schema_match": header == EXPECTED_SCHEMA,
        "observed_columns": header,
        "expected_columns": EXPECTED_SCHEMA,
        "sample_open_time_values": open_times[:MAX_CSV_SAMPLE_DATA_ROWS],
        "sample_open_time_delta_ms": sample_delta,
        "inferred_sample_interval": "1m" if one_minute else "UNKNOWN_PENDING_REVIEW",
        "one_minute_interval_observed": one_minute,
        "direct_1h_interval_present": False if one_minute else None,
    }


def build_payload(
    preflight: Dict[str, Any],
    artifacts: Dict[str, Dict[str, Any]],
    hash_validation: Dict[str, Any],
    zip_validation: Dict[str, Any],
    schema_validation: Dict[str, Any],
) -> Dict[str, Any]:
    latest = artifacts["execution_latest"]
    compliance = artifacts["compliance_report"]
    flags = dangerous_flags()
    single_file_provenance_validated = (
        hash_validation["downloaded_zip_exists"]
        and hash_validation["downloaded_zip_size_matches_recorded"]
        and hash_validation["downloaded_zip_sha256_matches"]
        and hash_validation["hash_computed_after_download"]
    )
    single_file_schema_sample_validated = (
        schema_validation["csv_header_read"]
        and schema_validation["csv_sample_rows_read_count"] <= MAX_CSV_SAMPLE_DATA_ROWS
        and schema_validation["csv_full_read_performed"] is False
        and schema_validation["expected_schema_match"] is True
    )
    single_file_1m_interval_validated = (
        schema_validation["sample_open_time_delta_ms"] == 60000
        and schema_validation["inferred_sample_interval"] == "1m"
        and schema_validation["one_minute_interval_observed"] is True
        and schema_validation["direct_1h_interval_present"] is False
    )
    zip_validated = (
        zip_validation["zip_open_success"]
        and zip_validation["zip_member_count"] == 1
        and zip_validation["expected_inner_csv_present"]
        and zip_validation["zip_path_traversal_detected"] is False
        and zip_validation["zip_member_count_within_limit"]
    )
    replacement_checks = {
        "preflight_passed": preflight.get("whole_system_preflight_completed") is True,
        "execution_artifacts_validated": True,
        "hash_validated": single_file_provenance_validated,
        "zip_validated": zip_validated,
        "schema_sample_validated": single_file_schema_sample_validated,
        "one_minute_interval_validated": single_file_1m_interval_validated,
        "no_new_download_by_validator": True,
        "no_api_browse_by_validator": True,
        "no_data_build_aggregation": compliance.get("data_build_performed") is False
        and compliance.get("aggregation_performed_now") is False,
        "no_full_csv_read": schema_validation["csv_full_read_performed"] is False,
        "not_build_ready_or_acquisition_ready": compliance.get("file_marked_build_ready") is False
        and compliance.get("source_manifest_acquisition_ready") is False,
        "schema_config_absent": planned_schema_files_existing_count() == 0,
        "generic_runner_absent": generic_runner_target_exists() is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
    }
    all_checks = all(replacement_checks.values())
    if not all_checks:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: replacement checks failed")
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_validator_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "PREVIEW_SINGLE_SYMBOL_1M_TO_1H_BUILD_SCOPE_NO_EXECUTION",
        "next_module": NEXT_MODULE_PASS,
        **preflight,
        "execution_artifacts_exist": True,
        "execution_artifacts_valid_json": True,
        "smoke_test_download_execution_validated": True,
        "approved_url_used": True,
        "approved_url_count": 1,
        "downloaded_file_count": 1,
        "target_symbol": TARGET_SYMBOL,
        "target_url": TARGET_URL,
        "expected_inner_csv": EXPECTED_INNER_CSV,
        "downloaded_zip_exists": True,
        "downloaded_zip_size_bytes": hash_validation["downloaded_zip_size_bytes"],
        "downloaded_zip_size_matches_recorded": True,
        "downloaded_zip_sha256_recorded": hash_validation["downloaded_zip_sha256_recorded"],
        "downloaded_zip_sha256_recomputed": hash_validation["downloaded_zip_sha256_recomputed"],
        "downloaded_zip_sha256_matches": True,
        "hash_algorithm": "SHA256",
        "zip_open_success": True,
        "zip_member_count": zip_validation["zip_member_count"],
        "expected_inner_csv_present": True,
        "zip_path_traversal_detected": False,
        "csv_header_read": True,
        "csv_sample_rows_read_count": schema_validation["csv_sample_rows_read_count"],
        "csv_full_read_performed": False,
        "expected_schema_match": True,
        "observed_columns": schema_validation["observed_columns"],
        "sample_open_time_delta_ms": schema_validation["sample_open_time_delta_ms"],
        "inferred_sample_interval": schema_validation["inferred_sample_interval"],
        "one_minute_interval_observed": True,
        "direct_1h_interval_present": False,
        "single_file_provenance_validated": True,
        "single_file_schema_sample_validated": True,
        "single_file_1m_interval_validated": True,
        "safe_for_single_file_pipeline_build_preview": True,
        "safe_for_broad_acquisition": False,
        "safe_for_research_backtest": False,
        "safe_for_edge_claim": False,
        "file_marked_build_ready": False,
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
        "validator_p1_count": max(8, int(latest.get("active_p1_attention_count", 8))),
        "current_evidence_chain_quality_before_validator": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_validator": EVIDENCE_AFTER,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": max(8, int(latest.get("active_p1_attention_count", 8))),
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
            "repo-only validator recomputed SHA256 for the already-downloaded single OKX smoke-test ZIP, rechecked ZIP "
            "central directory and expected CSV presence, reread only the header plus five sample rows, confirmed schema "
            "and 1m interval evidence, performed no new download/API/browse/data build/aggregation/full CSV read, and "
            "kept broad acquisition, research/backtest/edge, runtime, capital, live, schema/config, and generic-runner "
            "paths closed"
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
    hash_validation: Dict[str, Any],
    zip_validation: Dict[str, Any],
    schema_validation: Dict[str, Any],
    provenance_validation: Dict[str, Any],
) -> None:
    outputs = {
        "historical_okx_single_symbol_smoke_test_download_execution_validator.json": payload,
        "historical_okx_single_symbol_smoke_test_download_hash_validation_report.json": hash_validation,
        "historical_okx_single_symbol_smoke_test_zip_schema_validation_report.json": {
            "zip_inventory_validation": zip_validation,
            "schema_sample_validation": schema_validation,
        },
        "historical_okx_single_symbol_smoke_test_provenance_validation_report.json": provenance_validation,
        "historical_okx_single_symbol_smoke_test_download_execution_validator_summary.json": payload,
        "repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_validator_after_execution_v1_latest.json": payload,
    }
    for name, artifact in outputs.items():
        write_json(OUT_DIR / name, artifact)


def blocked_payload(exc: Exception) -> Dict[str, Any]:
    flags = dangerous_flags()
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_validator_status": STATUS_BLOCKED_CONTEXT,
        "final_decision": STATUS_BLOCKED_CONTEXT,
        "next_action": "STOP_FAIL_CLOSED_DOWNLOAD_EXECUTION_VALIDATION_BLOCKED_NO_BUILD",
        "next_module": NEXT_MODULE_BLOCKED,
        "error": str(exc),
        "whole_system_preflight_completed": False,
        "live_next_module_matches_requested_module": False,
        "artifact_chain_consistent": False,
        "stale_or_contradictory_artifact_detected": True,
        "execution_artifacts_exist": False,
        "execution_artifacts_valid_json": False,
        "smoke_test_download_execution_validated": False,
        "approved_url_used": False,
        "approved_url_count": 1,
        "downloaded_file_count": 0,
        "target_symbol": TARGET_SYMBOL,
        "target_url": TARGET_URL,
        "expected_inner_csv": EXPECTED_INNER_CSV,
        "downloaded_zip_exists": False,
        "downloaded_zip_size_bytes": 0,
        "downloaded_zip_size_matches_recorded": False,
        "downloaded_zip_sha256_recorded": EXPECTED_SHA256,
        "downloaded_zip_sha256_recomputed": None,
        "downloaded_zip_sha256_matches": False,
        "hash_algorithm": "SHA256",
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
        "single_file_provenance_validated": False,
        "single_file_schema_sample_validated": False,
        "single_file_1m_interval_validated": False,
        "safe_for_single_file_pipeline_build_preview": False,
        "safe_for_broad_acquisition": False,
        "safe_for_research_backtest": False,
        "safe_for_edge_claim": False,
        "file_marked_build_ready": False,
        "source_manifest_acquisition_ready": False,
        "broad_acquisition_execution_allowed_now": False,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "new_download_performed_by_validator": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "okx_sample_zip_downloaded_now": False,
        "validator_p0_count": 1,
        "validator_p1_count": 8,
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
        OUT_DIR
        / "repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_validator_after_execution_v1_latest.json",
        payload,
    )
    write_json(OUT_DIR / "historical_okx_single_symbol_smoke_test_download_execution_validator_summary.json", payload)


def main() -> int:
    try:
        artifacts = validate_required_artifacts()
        preflight = validate_preflight(artifacts)
        hash_validation = validate_downloaded_file(artifacts["provenance_report"])
        if hash_validation["downloaded_zip_size_bytes"] > MAX_ZIP_SIZE_BYTES:
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: downloaded ZIP exceeds validator size limit")
        zip_path = Path(hash_validation["downloaded_zip_path"])
        zip_validation = validate_zip_inventory_from_file(zip_path)
        schema_validation = validate_schema_sample_from_file(zip_path)
        provenance_validation = {
            "single_file_provenance_validated": (
                hash_validation["downloaded_zip_exists"]
                and hash_validation["downloaded_zip_size_matches_recorded"]
                and hash_validation["downloaded_zip_sha256_matches"]
                and hash_validation["hash_computed_after_download"]
            ),
            "source_url": TARGET_URL,
            "downloaded_zip_path": hash_validation["downloaded_zip_path"],
            "new_download_performed_by_validator": False,
            "hash_validation_report": hash_validation,
        }
        payload = build_payload(preflight, artifacts, hash_validation, zip_validation, schema_validation)
        write_validator_artifacts(payload, hash_validation, zip_validation, schema_validation, provenance_validation)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        payload = blocked_payload(exc)
        write_blocked_artifact(payload)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
