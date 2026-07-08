from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_"
    "after_preview_approval_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_"
    "after_preview_approval_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "6b61b74"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 684
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 685

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_"
    "after_preview_approval_v1.py"
)
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_validator_"
    "after_execution_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_"
    "blocked_record_after_preview_approval_v1.py"
)

BUILD_PREVIEW_DIR = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_preview_after_download_validator_v1"
)
BUILD_PREVIEW_ARTIFACT = (
    BUILD_PREVIEW_DIR
    / "repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_preview_after_download_validator_v1_latest.json"
)
DOWNLOAD_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_validator_after_execution_v1"
    / "repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_validator_after_execution_v1_latest.json"
)
EXECUTION_DIR = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_after_preview_approval_v1"
)
EXECUTION_REPORT_ARTIFACT = EXECUTION_DIR / "historical_okx_single_symbol_smoke_test_download_execution_report.json"
PROVENANCE_REPORT_ARTIFACT = EXECUTION_DIR / "historical_okx_single_symbol_smoke_test_download_provenance_report.json"
ZIP_INVENTORY_REPORT_ARTIFACT = EXECUTION_DIR / "historical_okx_single_symbol_smoke_test_zip_inventory_report.json"
SCHEMA_SAMPLE_REPORT_ARTIFACT = EXECUTION_DIR / "historical_okx_single_symbol_smoke_test_schema_sample_report.json"
COMPLIANCE_REPORT_ARTIFACT = EXECUTION_DIR / "historical_okx_single_symbol_smoke_test_execution_compliance_report.json"
POLICY_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_after_creation_v1"
    / "repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_after_creation_v1_latest.json"
)
POLICY_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_creation_after_approval_v1"
    / "historical_okx_1m_to_1h_aggregation_policy.json"
)

BUILD_PREVIEW_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_1M_TO_1H_BUILD_PREVIEW_APPROVED_EXECUTION_NEXT_"
    "NO_BUILD_YET"
)
DOWNLOAD_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMOKE_TEST_DOWNLOAD_VALIDATED_BUILD_PREVIEW_READY_"
    "NO_EXECUTION"
)
POLICY_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_VALIDATED_"
    "SOURCE_MANIFEST_PREVIEW_READY_NO_EXECUTION"
)
STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_1M_TO_1H_BUILD_EXECUTED_PENDING_VALIDATOR_"
    "PIPELINE_SMOKE_TEST_ONLY"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_1M_TO_1H_BUILD_PREVIEW_APPROVED_EXECUTION_NEXT_"
    "NO_BUILD_YET"
)
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_1M_TO_1H_BUILD_EXECUTED_PENDING_VALIDATOR_"
    "PIPELINE_SMOKE_TEST_ONLY"
)

BUILD_SCOPE = "SINGLE_SYMBOL_SINGLE_DAY_1M_TO_1H_PIPELINE_SMOKE_TEST_ONLY"
TARGET_SYMBOL = "BTC-USDT-SWAP"
TARGET_URL = (
    "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/20260518/"
    "BTC-USDT-SWAP-candlesticks-2026-05-18.zip"
)
SOURCE_ZIP_SHA256 = "c33b6c18bf852d6a80d5caa872ae6ed26614166ad614ec601a5f533f22fa4f06"
SOURCE_ZIP_SIZE_BYTES = 43567
EXPECTED_INNER_CSV = "BTC-USDT-SWAP-candlesticks-2026-05-18.csv"
EXPECTED_INPUT_INTERVAL = "1m"
EXPECTED_OUTPUT_INTERVAL = "1h"
EXPECTED_SOURCE_ROWS = 1440
MAX_ALLOWED_SOURCE_ROWS = 2000
EXPECTED_COMPLETE_OUTPUT_HOURS = 24
MAX_ALLOWED_OUTPUT_ROWS = 24
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
EXPECTED_OUTPUT_SCHEMA = [
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
    "build_scope",
]

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


def iso_utc_from_ms(epoch_ms: int) -> str:
    return datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc).isoformat()


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


def validate_required_artifacts() -> Dict[str, Dict[str, Any]]:
    paths = {
        "build_preview": BUILD_PREVIEW_ARTIFACT,
        "download_validator": DOWNLOAD_VALIDATOR_ARTIFACT,
        "execution_report": EXECUTION_REPORT_ARTIFACT,
        "provenance_report": PROVENANCE_REPORT_ARTIFACT,
        "zip_inventory_report": ZIP_INVENTORY_REPORT_ARTIFACT,
        "schema_sample_report": SCHEMA_SAMPLE_REPORT_ARTIFACT,
        "compliance_report": COMPLIANCE_REPORT_ARTIFACT,
        "policy_validator": POLICY_VALIDATOR_ARTIFACT,
        "policy": POLICY_ARTIFACT,
    }
    return {label: load_json(path, label) for label, path in paths.items()}


def validate_preflight(artifacts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))

    preview = artifacts["build_preview"]
    download_validator = artifacts["download_validator"]
    execution = artifacts["execution_report"].get("execution_scope", {})
    provenance = artifacts["provenance_report"]
    inventory = artifacts["zip_inventory_report"]
    sample = artifacts["schema_sample_report"]
    compliance = artifacts["compliance_report"]
    policy_validator = artifacts["policy_validator"]
    policy = artifacts["policy"]

    require_equal(
        preview.get("historical_data_acquisition_okx_single_symbol_1m_to_1h_build_preview_bundle_status"),
        BUILD_PREVIEW_STATUS_PASS,
        "preview.status",
    )
    require_equal(preview.get("next_module"), REQUESTED_MODULE, "preview.next_module", STATUS_BLOCKED_NEXT_MODULE)
    require_true(preview.get("approval_grants_future_single_file_build_next"), "preview.future_build")
    require_false(preview.get("approval_grants_build_now"), "preview.build_now")
    require_false(preview.get("approval_grants_new_download_now"), "preview.new_download")
    require_equal(preview.get("future_build_scope_file_count"), 1, "preview.file_count")
    require_equal(preview.get("future_build_scope_symbol_count"), 1, "preview.symbol_count")
    require_equal(preview.get("future_build_scope_day_count"), 1, "preview.day_count")
    require_true(preview.get("future_build_scope_limited_to_single_file_symbol_day"), "preview.scope_limited")
    require_equal(preview.get("target_symbol"), TARGET_SYMBOL, "preview.target_symbol")
    require_equal(preview.get("source_zip_sha256"), SOURCE_ZIP_SHA256, "preview.sha256")
    require_equal(preview.get("expected_inner_csv"), EXPECTED_INNER_CSV, "preview.inner_csv")
    require_equal(preview.get("expected_input_interval"), EXPECTED_INPUT_INTERVAL, "preview.input_interval")
    require_equal(preview.get("expected_output_interval"), EXPECTED_OUTPUT_INTERVAL, "preview.output_interval")
    require_equal(preview.get("expected_source_rows"), EXPECTED_SOURCE_ROWS, "preview.source_rows")
    require_equal(preview.get("expected_complete_output_hours"), EXPECTED_COMPLETE_OUTPUT_HOURS, "preview.output_hours")
    require_false(preview.get("data_build_performed"), "preview.data_build")
    require_false(preview.get("aggregation_performed_now"), "preview.aggregation")
    require_false(preview.get("source_manifest_acquisition_ready"), "preview.manifest_ready")
    require_false(preview.get("broad_acquisition_execution_allowed_now"), "preview.broad_acquisition")
    require_equal(preview.get("active_p0_blocker_count"), 0, "preview.active_p0")
    require_equal(preview.get("dormant_repo_attention_count"), 716, "preview.dormant_attention")
    require_true(preview.get("replacement_checks_all_true"), "preview.replacement")
    validate_no_true_dangerous_flags(preview, "preview")

    require_true(download_validator.get("downloaded_zip_exists"), "download_validator.zip_exists")
    require_true(download_validator.get("downloaded_zip_sha256_matches"), "download_validator.sha256")
    require_true(download_validator.get("expected_inner_csv_present"), "download_validator.inner_csv")
    require_true(download_validator.get("safe_for_single_file_pipeline_build_preview"), "download_validator.safe_build_preview")
    require_false(download_validator.get("safe_for_broad_acquisition"), "download_validator.broad")
    require_false(download_validator.get("safe_for_research_backtest"), "download_validator.research")
    require_false(download_validator.get("safe_for_edge_claim"), "download_validator.edge")
    require_false(download_validator.get("data_build_performed"), "download_validator.data_build")
    require_false(download_validator.get("aggregation_performed_now"), "download_validator.aggregation")
    require_false(download_validator.get("new_download_performed_by_validator"), "download_validator.new_download")

    require_equal(execution.get("target_symbol"), TARGET_SYMBOL, "execution.target_symbol")
    require_equal(execution.get("expected_inner_csv"), EXPECTED_INNER_CSV, "execution.inner_csv")
    source_zip_path = Path(str(execution.get("downloaded_zip_path", "")))
    require_true(source_zip_path.exists() and source_zip_path.is_file(), "execution.source_zip_exists")

    require_equal(provenance.get("downloaded_zip_sha256"), SOURCE_ZIP_SHA256, "provenance.sha256")
    require_true(provenance.get("hash_computed_after_download"), "provenance.hash_after_download")
    require_true(inventory.get("zip_open_success"), "inventory.zip_open")
    require_equal(inventory.get("zip_member_count"), 1, "inventory.member_count")
    require_true(inventory.get("expected_inner_csv_present"), "inventory.csv_present")
    require_false(inventory.get("zip_path_traversal_detected"), "inventory.traversal")
    require_equal(sample.get("observed_columns"), EXPECTED_SCHEMA, "sample.schema")
    require_equal(sample.get("inferred_sample_interval"), EXPECTED_INPUT_INTERVAL, "sample.interval")
    require_true(sample.get("one_minute_interval_observed"), "sample.one_minute")

    require_false(compliance.get("data_build_performed"), "compliance.data_build")
    require_false(compliance.get("aggregation_performed_now"), "compliance.aggregation")
    require_false(compliance.get("okx_api_call_performed"), "compliance.api")
    require_false(compliance.get("okx_browse_performed"), "compliance.browse")
    require_false(compliance.get("file_marked_build_ready"), "compliance.file_build_ready")
    require_false(compliance.get("source_manifest_acquisition_ready"), "compliance.manifest_ready")

    require_equal(
        policy_validator.get("historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_status"),
        POLICY_VALIDATOR_STATUS_PASS,
        "policy_validator.status",
    )
    require_true(policy_validator.get("okx_1m_to_1h_aggregation_policy_validated"), "policy_validator.validated")
    require_false(policy_validator.get("policy_execution_allowed_now"), "policy_validator.execution")
    validate_no_true_dangerous_flags(policy_validator, "policy_validator")

    require_equal(policy.get("input_schema_policy", {}).get("expected_columns"), EXPECTED_SCHEMA, "policy.expected_columns")
    require_equal(policy.get("input_schema_policy", {}).get("timestamp_unit"), "epoch_milliseconds", "policy.timestamp_unit")
    require_equal(policy.get("input_schema_policy", {}).get("expected_open_time_delta_ms"), 60000, "policy.delta")
    require_false(policy.get("input_schema_policy", {}).get("direct_1h_input_expected"), "policy.direct_1h")
    require_equal(policy.get("canonical_time_policy", {}).get("output_hour_bucket_policy"), "FLOOR_OPEN_TIME_TO_UTC_HOUR", "policy.bucket")
    require_equal(policy.get("completeness_policy", {}).get("complete_hour_required_source_rows"), 60, "policy.complete_rows")
    require_false(policy.get("completeness_policy", {}).get("synthetic_fill_allowed"), "policy.synthetic_fill")

    return {
        "whole_system_preflight_completed": True,
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
        "build_preview_artifact": str(BUILD_PREVIEW_ARTIFACT),
        "download_validator_artifact": str(DOWNLOAD_VALIDATOR_ARTIFACT),
        "execution_report_artifact": str(EXECUTION_REPORT_ARTIFACT),
        "provenance_report_artifact": str(PROVENANCE_REPORT_ARTIFACT),
        "zip_inventory_report_artifact": str(ZIP_INVENTORY_REPORT_ARTIFACT),
        "schema_sample_report_artifact": str(SCHEMA_SAMPLE_REPORT_ARTIFACT),
        "compliance_report_artifact": str(COMPLIANCE_REPORT_ARTIFACT),
        "policy_validator_artifact": str(POLICY_VALIDATOR_ARTIFACT),
        "policy_artifact": str(POLICY_ARTIFACT),
        "source_zip_path": str(source_zip_path),
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


def parse_decimal(value: str, field: str, row_number: int) -> Decimal:
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: numeric parse failure {field} row={row_number}") from exc
    if not parsed.is_finite():
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: non-finite numeric value {field} row={row_number}")
    return parsed


def decimal_to_string(value: Decimal) -> str:
    normalized = value.normalize()
    if normalized == normalized.to_integral():
        return str(normalized.quantize(Decimal("1")))
    return format(normalized, "f")


def confirm_true(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y"}


def validate_zip_and_read_rows(zip_path: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    if recompute_sha256(zip_path) != SOURCE_ZIP_SHA256:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: source ZIP SHA256 mismatch before CSV read")
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        if len(names) != 1:
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: expected exactly one ZIP member")
        if any(zip_member_has_path_traversal(name) for name in names):
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: ZIP path traversal detected")
        if EXPECTED_INNER_CSV not in names:
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: expected inner CSV missing")
        rows: List[Dict[str, Any]] = []
        with zf.open(EXPECTED_INNER_CSV, "r") as raw:
            text = io.TextIOWrapper(raw, encoding="utf-8", newline="")
            reader = csv.DictReader(text)
            if reader.fieldnames != EXPECTED_SCHEMA:
                raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: CSV schema mismatch")
            for row_number, row in enumerate(reader, start=1):
                if row_number > MAX_ALLOWED_SOURCE_ROWS:
                    raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: source row count exceeds limit")
                symbol = row["instrument_name"]
                open_time = int(row["open_time"])
                open_value = parse_decimal(row["open"], "open", row_number)
                high_value = parse_decimal(row["high"], "high", row_number)
                low_value = parse_decimal(row["low"], "low", row_number)
                close_value = parse_decimal(row["close"], "close", row_number)
                vol = parse_decimal(row["vol"], "vol", row_number)
                vol_ccy = parse_decimal(row["vol_ccy"], "vol_ccy", row_number)
                vol_quote = parse_decimal(row["vol_quote"], "vol_quote", row_number)
                if high_value < max(open_value, close_value, low_value):
                    raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: invalid high row={row_number}")
                if low_value > min(open_value, close_value, high_value):
                    raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: invalid low row={row_number}")
                if vol < 0 or vol_ccy < 0 or vol_quote < 0:
                    raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: negative volume row={row_number}")
                rows.append(
                    {
                        "instrument_name": symbol,
                        "open": open_value,
                        "high": high_value,
                        "low": low_value,
                        "close": close_value,
                        "vol": vol,
                        "vol_ccy": vol_ccy,
                        "vol_quote": vol_quote,
                        "open_time": open_time,
                        "confirm": confirm_true(row["confirm"]),
                    }
                )
    metadata = {
        "source_zip_exists": True,
        "source_zip_sha256_matches": True,
        "expected_inner_csv_present": True,
        "schema_match": True,
        "full_csv_read_performed": True,
    }
    return rows, metadata


def analyze_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    if len(rows) != EXPECTED_SOURCE_ROWS:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: source_row_count={len(rows)} expected {EXPECTED_SOURCE_ROWS}")
    symbols = sorted({row["instrument_name"] for row in rows})
    if symbols != [TARGET_SYMBOL]:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: unexpected symbols {symbols}")
    open_times = [row["open_time"] for row in rows]
    duplicate_count = sum(count - 1 for count in Counter(open_times).values() if count > 1)
    if duplicate_count:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: duplicate open_time count={duplicate_count}")
    monotonic = all(open_times[idx] < open_times[idx + 1] for idx in range(len(open_times) - 1))
    if not monotonic:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: open_time non-monotonic")
    deltas = [open_times[idx + 1] - open_times[idx] for idx in range(len(open_times) - 1)]
    missing = sum((delta // 60000) - 1 for delta in deltas if delta > 60000 and delta % 60000 == 0)
    if any(delta != 60000 for delta in deltas):
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: non-1m interval detected")
    if missing:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: missing minute count={missing}")
    return {
        "source_row_count": len(rows),
        "expected_source_rows": EXPECTED_SOURCE_ROWS,
        "unique_symbol_count": len(symbols),
        "observed_symbol": symbols[0],
        "open_time_monotonic": monotonic,
        "duplicate_open_time_count": duplicate_count,
        "missing_minute_count": missing,
        "observed_first_open_time_ms": open_times[0],
        "observed_last_open_time_ms": open_times[-1],
        "observed_first_open_time_utc": iso_utc_from_ms(open_times[0]),
        "observed_last_open_time_utc": iso_utc_from_ms(open_times[-1]),
        "observed_interval_ms": 60000,
        "one_minute_interval_validated": True,
    }


def aggregate_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    grouped: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        hour_start = (row["open_time"] // 3_600_000) * 3_600_000
        grouped[hour_start].append(row)
    output: List[Dict[str, str]] = []
    for hour_start in sorted(grouped):
        group = sorted(grouped[hour_start], key=lambda item: item["open_time"])
        source_row_count = len(group)
        complete_hour = source_row_count == 60
        if not complete_hour:
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: incomplete hour encountered")
        output.append(
            {
                "instrument_name": TARGET_SYMBOL,
                "hour_start_epoch_ms": str(hour_start),
                "hour_start_iso_utc": iso_utc_from_ms(hour_start),
                "open": decimal_to_string(group[0]["open"]),
                "high": decimal_to_string(max(item["high"] for item in group)),
                "low": decimal_to_string(min(item["low"] for item in group)),
                "close": decimal_to_string(group[-1]["close"]),
                "vol": decimal_to_string(sum((item["vol"] for item in group), Decimal("0"))),
                "vol_ccy": decimal_to_string(sum((item["vol_ccy"] for item in group), Decimal("0"))),
                "vol_quote": decimal_to_string(sum((item["vol_quote"] for item in group), Decimal("0"))),
                "source_row_count": str(source_row_count),
                "complete_hour": "true",
                "confirm": "true" if all(item["confirm"] for item in group) else "false",
                "source_first_open_time": str(group[0]["open_time"]),
                "source_last_open_time": str(group[-1]["open_time"]),
                "source_zip_sha256": SOURCE_ZIP_SHA256,
                "source_csv_file": EXPECTED_INNER_CSV,
                "build_scope": BUILD_SCOPE,
            }
        )
    if len(output) > MAX_ALLOWED_OUTPUT_ROWS:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: output row count exceeds limit")
    if len(output) != EXPECTED_COMPLETE_OUTPUT_HOURS:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: output row count={len(output)} expected 24")
    return output


def write_output_csv(rows: List[Dict[str, str]]) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = (OUT_DIR / "historical_okx_single_symbol_1m_to_1h_output.csv").resolve()
    if not str(output_path).startswith(str(OUT_DIR.resolve())):
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: output path outside module output directory")
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPECTED_OUTPUT_SCHEMA)
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def build_reports(
    preflight: Dict[str, Any],
    zip_metadata: Dict[str, Any],
    input_validation: Dict[str, Any],
    output_rows: List[Dict[str, str]],
    output_path: Path,
) -> Dict[str, Dict[str, Any]]:
    complete_count = sum(1 for row in output_rows if row["complete_hour"] == "true")
    incomplete_count = len(output_rows) - complete_count
    output_schema_validated = list(output_rows[0].keys()) == EXPECTED_OUTPUT_SCHEMA if output_rows else False
    aggregation = {
        "aggregation_performed_now": True,
        "data_build_performed": True,
        "output_1h_row_count": len(output_rows),
        "complete_1h_row_count": complete_count,
        "incomplete_1h_row_count": incomplete_count,
        "expected_complete_output_hours": EXPECTED_COMPLETE_OUTPUT_HOURS,
        "all_hours_complete": incomplete_count == 0 and complete_count == EXPECTED_COMPLETE_OUTPUT_HOURS,
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "output_csv_created": output_path.exists(),
        "output_csv_path": str(output_path),
        "output_schema_validated": output_schema_validated,
    }
    gap_duplicate = {
        "duplicate_minute_count": input_validation["duplicate_open_time_count"],
        "missing_minute_count": input_validation["missing_minute_count"],
        "incomplete_hour_count": incomplete_count,
        "invalid_row_count": 0,
        "quarantined_row_count": 0,
        "gap_duplicate_status": "PASS_NO_GAPS_DUPLICATES_OR_INCOMPLETE_HOURS",
    }
    provenance = {
        "source_url": TARGET_URL,
        "source_zip_path": preflight["source_zip_path"],
        "source_zip_sha256": SOURCE_ZIP_SHA256,
        "source_zip_size_bytes": SOURCE_ZIP_SIZE_BYTES,
        "expected_inner_csv": EXPECTED_INNER_CSV,
        "build_timestamp_utc": utc_now(),
        "output_csv_path": str(output_path),
        "output_row_count": len(output_rows),
        "provenance_status": "SINGLE_FILE_PIPELINE_SMOKE_TEST_BUILD_OUTPUT",
    }
    compliance = {
        "no_new_download": True,
        "no_api": True,
        "no_browse": True,
        "no_multi_file": True,
        "no_multi_symbol": True,
        "no_strategy_backtest_candidate": True,
        "no_runtime_capital_live": True,
        "no_generic_runner": True,
        "no_repo_schema_config": True,
        "output_is_pipeline_smoke_test_only": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "source_manifest_acquisition_ready": False,
    }
    schema_report = {
        "input_schema": EXPECTED_SCHEMA,
        "output_schema": EXPECTED_OUTPUT_SCHEMA,
        "schema_match": zip_metadata["schema_match"],
        "output_schema_validated": output_schema_validated,
        "numeric_validation_passed": True,
        "timestamp_unit": "epoch_milliseconds",
    }
    return {
        "aggregation": aggregation,
        "gap_duplicate": gap_duplicate,
        "provenance": provenance,
        "compliance": compliance,
        "schema": schema_report,
    }


def build_payload(
    preflight: Dict[str, Any],
    zip_metadata: Dict[str, Any],
    input_validation: Dict[str, Any],
    reports: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    flags = dangerous_flags()
    aggregation = reports["aggregation"]
    compliance = reports["compliance"]
    replacement_checks = {
        "preflight_passed": preflight.get("whole_system_preflight_completed") is True,
        "source_zip_validated": zip_metadata["source_zip_sha256_matches"] is True,
        "single_csv_processed": True,
        "single_symbol_processed": input_validation["unique_symbol_count"] == 1,
        "source_rows_expected": input_validation["source_row_count"] == EXPECTED_SOURCE_ROWS,
        "output_rows_expected": aggregation["output_1h_row_count"] == EXPECTED_COMPLETE_OUTPUT_HOURS,
        "all_hours_complete": aggregation["all_hours_complete"] is True,
        "no_fill_used": aggregation["synthetic_fill_used"] is False
        and aggregation["forward_fill_used"] is False
        and aggregation["backfill_used"] is False,
        "output_schema_validated": aggregation["output_schema_validated"] is True,
        "no_new_download_api_browse": compliance["no_new_download"] and compliance["no_api"] and compliance["no_browse"],
        "not_research_backtest_edge": compliance["output_valid_for_research_backtest"] is False
        and compliance["output_valid_for_edge_claim"] is False,
        "schema_config_absent": planned_schema_files_existing_count() == 0,
        "generic_runner_absent": generic_runner_target_exists() is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
    }
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "VALIDATE_SINGLE_SYMBOL_1M_TO_1H_BUILD_EXECUTION_PIPELINE_SMOKE_TEST_ONLY",
        "next_module": NEXT_MODULE_PASS,
        **preflight,
        "build_execution_performed": True,
        "build_scope": BUILD_SCOPE,
        "target_symbol": TARGET_SYMBOL,
        "source_zip_sha256": SOURCE_ZIP_SHA256,
        "source_zip_sha256_matches": True,
        "expected_inner_csv": EXPECTED_INNER_CSV,
        "source_zip_exists": True,
        "expected_inner_csv_present": True,
        "schema_match": True,
        "full_csv_read_performed": True,
        **input_validation,
        "aggregation_performed_now": True,
        "data_build_performed": True,
        **aggregation,
        "output_is_pipeline_smoke_test_only": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "source_manifest_acquisition_ready": False,
        "no_new_download": True,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "new_download_performed_now": False,
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
            "built exactly one BTC-USDT-SWAP single-day smoke-test 1h output from the already-validated ZIP and expected "
            "CSV; read the full CSV only for this approved build, validated 1440 monotonic unique 1m rows, produced 24 "
            "complete UTC 1h rows with no synthetic fill, and performed no new download/API/browse, no multi-file or "
            "multi-symbol work, and no research/backtest/edge/runtime/capital/live/schema/config/generic-runner action"
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


def write_artifacts(payload: Dict[str, Any], reports: Dict[str, Dict[str, Any]]) -> None:
    execution_report = {
        "generated_at_utc": utc_now(),
        "execution_scope": {
            "build_execution_performed": True,
            "build_scope": BUILD_SCOPE,
            "target_symbol": TARGET_SYMBOL,
            "source_zip_sha256": SOURCE_ZIP_SHA256,
            "source_zip_path": payload["source_zip_path"],
            "expected_inner_csv": EXPECTED_INNER_CSV,
            "output_directory": str(OUT_DIR),
            "new_download_performed": False,
            "api_call_performed": False,
            "browse_performed": False,
            "multi_file_processing": False,
            "multi_symbol_processing": False,
        },
        "input_validation": {
            key: payload[key]
            for key in (
                "source_zip_exists",
                "source_zip_sha256_matches",
                "expected_inner_csv_present",
                "schema_match",
                "full_csv_read_performed",
                "source_row_count",
                "unique_symbol_count",
                "observed_symbol",
                "open_time_monotonic",
                "duplicate_open_time_count",
                "missing_minute_count",
                "observed_first_open_time_ms",
                "observed_last_open_time_ms",
                "observed_first_open_time_utc",
                "observed_last_open_time_utc",
                "observed_interval_ms",
                "one_minute_interval_validated",
            )
        },
        "aggregation_execution": reports["aggregation"],
        "next_module_decision": {"next_module": payload["next_module"], "next_action": payload["next_action"]},
    }
    outputs = {
        "historical_okx_single_symbol_1m_to_1h_build_execution_report.json": execution_report,
        "historical_okx_single_symbol_1m_to_1h_gap_duplicate_report.json": reports["gap_duplicate"],
        "historical_okx_single_symbol_1m_to_1h_schema_validation_report.json": reports["schema"],
        "historical_okx_single_symbol_1m_to_1h_output_provenance_report.json": reports["provenance"],
        "historical_okx_single_symbol_1m_to_1h_build_execution_compliance_report.json": reports["compliance"],
        "historical_okx_single_symbol_1m_to_1h_build_execution_summary.json": payload,
        "repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_after_preview_approval_v1_latest.json": payload,
    }
    for name, artifact in outputs.items():
        write_json(OUT_DIR / name, artifact)


def blocked_payload(exc: Exception) -> Dict[str, Any]:
    flags = dangerous_flags()
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_status": STATUS_BLOCKED_CONTEXT,
        "final_decision": STATUS_BLOCKED_CONTEXT,
        "next_action": "STOP_FAIL_CLOSED_NO_SINGLE_SYMBOL_1M_TO_1H_BUILD_OUTPUT",
        "next_module": NEXT_MODULE_BLOCKED,
        "error": str(exc),
        "whole_system_preflight_completed": False,
        "live_next_module_matches_requested_module": False,
        "artifact_chain_consistent": False,
        "stale_or_contradictory_artifact_detected": True,
        "build_execution_performed": False,
        "build_scope": BUILD_SCOPE,
        "target_symbol": TARGET_SYMBOL,
        "source_zip_sha256": SOURCE_ZIP_SHA256,
        "source_zip_sha256_matches": False,
        "expected_inner_csv": EXPECTED_INNER_CSV,
        "source_zip_exists": False,
        "expected_inner_csv_present": False,
        "schema_match": False,
        "full_csv_read_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "output_csv_created": False,
        "output_schema_validated": False,
        "output_is_pipeline_smoke_test_only": True,
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


def main() -> int:
    try:
        artifacts = validate_required_artifacts()
        preflight = validate_preflight(artifacts)
        rows, zip_metadata = validate_zip_and_read_rows(Path(preflight["source_zip_path"]))
        input_validation = analyze_rows(rows)
        output_rows = aggregate_rows(rows)
        output_path = write_output_csv(output_rows)
        reports = build_reports(preflight, zip_metadata, input_validation, output_rows, output_path)
        payload = build_payload(preflight, zip_metadata, input_validation, reports)
        write_artifacts(payload, reports)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        payload = blocked_payload(exc)
        write_json(
            OUT_DIR / "repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_after_preview_approval_v1_latest.json",
            payload,
        )
        write_json(OUT_DIR / "historical_okx_single_symbol_1m_to_1h_build_execution_summary.json", payload)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
