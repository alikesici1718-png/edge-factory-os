from __future__ import annotations

import csv
import hashlib
import json
import math
import subprocess
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_validator_"
    "after_execution_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_validator_"
    "after_execution_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "29e9956"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 685
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 686

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_validator_"
    "after_execution_v1.py"
)
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_summary_"
    "after_build_validator_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_validation_"
    "blocked_record_after_execution_v1.py"
)

BUILD_EXECUTION_DIR = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_after_preview_approval_v1"
)
BUILD_EXECUTION_LATEST_ARTIFACT = (
    BUILD_EXECUTION_DIR
    / "repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_after_preview_approval_v1_latest.json"
)
BUILD_EXECUTION_REPORT_ARTIFACT = BUILD_EXECUTION_DIR / "historical_okx_single_symbol_1m_to_1h_build_execution_report.json"
GAP_DUPLICATE_REPORT_ARTIFACT = BUILD_EXECUTION_DIR / "historical_okx_single_symbol_1m_to_1h_gap_duplicate_report.json"
SCHEMA_VALIDATION_REPORT_ARTIFACT = BUILD_EXECUTION_DIR / "historical_okx_single_symbol_1m_to_1h_schema_validation_report.json"
OUTPUT_PROVENANCE_REPORT_ARTIFACT = BUILD_EXECUTION_DIR / "historical_okx_single_symbol_1m_to_1h_output_provenance_report.json"
BUILD_EXECUTION_COMPLIANCE_REPORT_ARTIFACT = BUILD_EXECUTION_DIR / "historical_okx_single_symbol_1m_to_1h_build_execution_compliance_report.json"
BUILD_EXECUTION_SUMMARY_ARTIFACT = BUILD_EXECUTION_DIR / "historical_okx_single_symbol_1m_to_1h_build_execution_summary.json"

BUILD_PREVIEW_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_preview_after_download_validator_v1"
    / "repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_preview_after_download_validator_v1_latest.json"
)
DOWNLOAD_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_validator_after_execution_v1"
    / "repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_validator_after_execution_v1_latest.json"
)
POLICY_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_after_creation_v1"
    / "repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_after_creation_v1_latest.json"
)

EXECUTION_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_1M_TO_1H_BUILD_EXECUTED_PENDING_VALIDATOR_"
    "PIPELINE_SMOKE_TEST_ONLY"
)
STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_1M_TO_1H_BUILD_VALIDATED_PIPELINE_SMOKE_TEST_"
    "SUMMARY_READY"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_1M_TO_1H_BUILD_EXECUTED_PENDING_VALIDATOR_"
    "PIPELINE_SMOKE_TEST_ONLY"
)
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_1M_TO_1H_BUILD_VALIDATED_PIPELINE_SMOKE_TEST_SUMMARY_READY"
)

BUILD_SCOPE = "SINGLE_SYMBOL_SINGLE_DAY_1M_TO_1H_PIPELINE_SMOKE_TEST_ONLY"
TARGET_SYMBOL = "BTC-USDT-SWAP"
SOURCE_ZIP_SHA256 = "c33b6c18bf852d6a80d5caa872ae6ed26614166ad614ec601a5f533f22fa4f06"
EXPECTED_INNER_CSV = "BTC-USDT-SWAP-candlesticks-2026-05-18.csv"
EXPECTED_SOURCE_ROWS = 1440
EXPECTED_OUTPUT_ROWS = 24
EXPECTED_SOURCE_ROWS_PER_HOUR = 60
EXPECTED_INTERVAL_MS = 3_600_000
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
    return sum(1 for path in run_git(["ls-files"]).splitlines() if path.endswith(".py"))


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
        "build_execution_latest": BUILD_EXECUTION_LATEST_ARTIFACT,
        "build_execution_report": BUILD_EXECUTION_REPORT_ARTIFACT,
        "gap_duplicate_report": GAP_DUPLICATE_REPORT_ARTIFACT,
        "schema_validation_report": SCHEMA_VALIDATION_REPORT_ARTIFACT,
        "output_provenance_report": OUTPUT_PROVENANCE_REPORT_ARTIFACT,
        "build_execution_compliance_report": BUILD_EXECUTION_COMPLIANCE_REPORT_ARTIFACT,
        "build_execution_summary": BUILD_EXECUTION_SUMMARY_ARTIFACT,
        "build_preview": BUILD_PREVIEW_ARTIFACT,
        "download_validator": DOWNLOAD_VALIDATOR_ARTIFACT,
        "policy_validator": POLICY_VALIDATOR_ARTIFACT,
    }
    artifacts: Dict[str, Dict[str, Any]] = {}
    artifact_status: Dict[str, Any] = {
        "required_artifact_paths": {label: str(path) for label, path in paths.items()},
        "artifact_exists_by_label": {},
        "artifact_valid_json_by_label": {},
    }
    for label, path in paths.items():
        data, exists, valid, non_empty = read_json_checked(path)
        artifact_status["artifact_exists_by_label"][label] = exists
        artifact_status["artifact_valid_json_by_label"][label] = valid and non_empty
        if not (exists and valid and non_empty):
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {label} missing/invalid/empty: {path}")
        artifacts[label] = data
    artifact_status["execution_artifacts_exist"] = all(artifact_status["artifact_exists_by_label"].values())
    artifact_status["execution_artifacts_valid_json"] = all(artifact_status["artifact_valid_json_by_label"].values())
    return artifacts, artifact_status


def validate_preflight(artifacts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))

    summary = artifacts["build_execution_summary"]
    latest = artifacts["build_execution_latest"]
    execution_report = artifacts["build_execution_report"]
    gap_duplicate = artifacts["gap_duplicate_report"]
    schema = artifacts["schema_validation_report"]
    provenance = artifacts["output_provenance_report"]
    compliance = artifacts["build_execution_compliance_report"]
    preview = artifacts["build_preview"]
    download_validator = artifacts["download_validator"]
    policy_validator = artifacts["policy_validator"]

    require_equal(summary.get("historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_status"), EXECUTION_STATUS_PASS, "summary.status")
    require_equal(latest.get("historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_status"), EXECUTION_STATUS_PASS, "latest.status")
    require_equal(summary.get("next_module"), REQUESTED_MODULE, "summary.next_module", STATUS_BLOCKED_NEXT_MODULE)
    require_equal(latest.get("next_module"), REQUESTED_MODULE, "latest.next_module", STATUS_BLOCKED_NEXT_MODULE)
    require_equal(execution_report.get("next_module_decision", {}).get("next_module"), REQUESTED_MODULE, "execution_report.next_module", STATUS_BLOCKED_NEXT_MODULE)

    for label, data in (("summary", summary), ("latest", latest)):
        require_true(data.get("build_execution_performed"), f"{label}.build_execution_performed")
        require_equal(data.get("build_scope"), BUILD_SCOPE, f"{label}.build_scope")
        require_equal(data.get("target_symbol"), TARGET_SYMBOL, f"{label}.target_symbol")
        require_true(data.get("source_zip_sha256_matches"), f"{label}.source_zip_sha256_matches")
        require_equal(data.get("expected_inner_csv"), EXPECTED_INNER_CSV, f"{label}.expected_inner_csv")
        require_true(data.get("source_zip_exists"), f"{label}.source_zip_exists")
        require_true(data.get("expected_inner_csv_present"), f"{label}.expected_inner_csv_present")
        require_true(data.get("schema_match"), f"{label}.schema_match")
        require_true(data.get("full_csv_read_performed"), f"{label}.full_csv_read_performed")
        require_equal(data.get("source_row_count"), EXPECTED_SOURCE_ROWS, f"{label}.source_row_count")
        require_equal(data.get("unique_symbol_count"), 1, f"{label}.unique_symbol_count")
        require_equal(data.get("observed_symbol"), TARGET_SYMBOL, f"{label}.observed_symbol")
        require_true(data.get("open_time_monotonic"), f"{label}.open_time_monotonic")
        require_equal(data.get("duplicate_open_time_count"), 0, f"{label}.duplicate_open_time_count")
        require_equal(data.get("missing_minute_count"), 0, f"{label}.missing_minute_count")
        require_equal(data.get("observed_interval_ms"), 60_000, f"{label}.observed_interval_ms")
        require_true(data.get("one_minute_interval_validated"), f"{label}.one_minute_interval_validated")
        require_true(data.get("aggregation_performed_now"), f"{label}.aggregation_performed_now")
        require_true(data.get("data_build_performed"), f"{label}.data_build_performed")
        require_equal(data.get("output_1h_row_count"), EXPECTED_OUTPUT_ROWS, f"{label}.output_1h_row_count")
        require_equal(data.get("complete_1h_row_count"), EXPECTED_OUTPUT_ROWS, f"{label}.complete_1h_row_count")
        require_equal(data.get("incomplete_1h_row_count"), 0, f"{label}.incomplete_1h_row_count")
        require_true(data.get("all_hours_complete"), f"{label}.all_hours_complete")
        require_false(data.get("synthetic_fill_used"), f"{label}.synthetic_fill_used")
        require_false(data.get("forward_fill_used"), f"{label}.forward_fill_used")
        require_false(data.get("backfill_used"), f"{label}.backfill_used")
        require_true(data.get("output_csv_created"), f"{label}.output_csv_created")
        require_true(data.get("output_schema_validated"), f"{label}.output_schema_validated")
        require_true(data.get("output_is_pipeline_smoke_test_only"), f"{label}.output_is_pipeline_smoke_test_only")
        require_false(data.get("output_valid_for_research_backtest"), f"{label}.output_valid_for_research_backtest")
        require_false(data.get("output_valid_for_edge_claim"), f"{label}.output_valid_for_edge_claim")
        require_false(data.get("broad_acquisition_ready"), f"{label}.broad_acquisition_ready")
        require_false(data.get("source_manifest_acquisition_ready"), f"{label}.source_manifest_acquisition_ready")
        require_true(data.get("no_new_download"), f"{label}.no_new_download")
        require_false(data.get("data_download_performed"), f"{label}.data_download_performed")
        require_false(data.get("data_fetch_performed"), f"{label}.data_fetch_performed")
        require_false(data.get("new_download_performed_now"), f"{label}.new_download_performed_now")
        require_false(data.get("okx_api_call_performed"), f"{label}.okx_api_call_performed")
        require_false(data.get("okx_browse_performed"), f"{label}.okx_browse_performed")
        require_equal(data.get("active_p0_blocker_count"), 0, f"{label}.active_p0_blocker_count")
        require_equal(data.get("dormant_repo_attention_count"), 716, f"{label}.dormant_repo_attention_count")
        require_true(data.get("generic_runner_implementation_remains_blocked"), f"{label}.generic_runner_blocked")
        require_false(data.get("schema_or_config_created"), f"{label}.schema_or_config_created")
        validate_no_true_dangerous_flags(data, label)

    execution_scope = execution_report.get("execution_scope", {})
    input_validation = execution_report.get("input_validation", {})
    aggregation_execution = execution_report.get("aggregation_execution", {})
    require_true(execution_scope.get("build_execution_performed"), "execution_scope.build_execution_performed")
    require_equal(execution_scope.get("build_scope"), BUILD_SCOPE, "execution_scope.build_scope")
    require_equal(execution_scope.get("target_symbol"), TARGET_SYMBOL, "execution_scope.target_symbol")
    require_equal(execution_scope.get("source_zip_sha256"), SOURCE_ZIP_SHA256, "execution_scope.source_zip_sha256")
    require_equal(execution_scope.get("expected_inner_csv"), EXPECTED_INNER_CSV, "execution_scope.expected_inner_csv")
    require_false(execution_scope.get("new_download_performed"), "execution_scope.new_download")
    require_false(execution_scope.get("api_call_performed"), "execution_scope.api")
    require_false(execution_scope.get("browse_performed"), "execution_scope.browse")
    require_false(execution_scope.get("multi_file_processing"), "execution_scope.multi_file")
    require_false(execution_scope.get("multi_symbol_processing"), "execution_scope.multi_symbol")
    require_equal(input_validation.get("source_row_count"), EXPECTED_SOURCE_ROWS, "execution_input.source_row_count")
    require_equal(input_validation.get("unique_symbol_count"), 1, "execution_input.unique_symbol_count")
    require_equal(input_validation.get("observed_symbol"), TARGET_SYMBOL, "execution_input.observed_symbol")
    require_true(input_validation.get("open_time_monotonic"), "execution_input.open_time_monotonic")
    require_equal(input_validation.get("duplicate_open_time_count"), 0, "execution_input.duplicate_open_time_count")
    require_equal(input_validation.get("missing_minute_count"), 0, "execution_input.missing_minute_count")
    require_equal(input_validation.get("observed_interval_ms"), 60_000, "execution_input.observed_interval_ms")
    require_true(input_validation.get("one_minute_interval_validated"), "execution_input.one_minute_interval_validated")
    require_equal(aggregation_execution.get("output_1h_row_count"), EXPECTED_OUTPUT_ROWS, "aggregation.output_1h_row_count")
    require_equal(aggregation_execution.get("complete_1h_row_count"), EXPECTED_OUTPUT_ROWS, "aggregation.complete_1h_row_count")
    require_equal(aggregation_execution.get("incomplete_1h_row_count"), 0, "aggregation.incomplete_1h_row_count")
    require_true(aggregation_execution.get("all_hours_complete"), "aggregation.all_hours_complete")
    require_false(aggregation_execution.get("synthetic_fill_used"), "aggregation.synthetic_fill_used")
    require_false(aggregation_execution.get("forward_fill_used"), "aggregation.forward_fill_used")
    require_false(aggregation_execution.get("backfill_used"), "aggregation.backfill_used")
    require_true(aggregation_execution.get("output_csv_created"), "aggregation.output_csv_created")
    require_true(aggregation_execution.get("output_schema_validated"), "aggregation.output_schema_validated")

    require_equal(gap_duplicate.get("duplicate_minute_count"), 0, "gap_duplicate.duplicate_minute_count")
    require_equal(gap_duplicate.get("missing_minute_count"), 0, "gap_duplicate.missing_minute_count")
    require_equal(gap_duplicate.get("incomplete_hour_count"), 0, "gap_duplicate.incomplete_hour_count")
    require_true(schema.get("output_schema_validated"), "schema.output_schema_validated")
    require_equal(schema.get("output_schema"), EXPECTED_OUTPUT_SCHEMA, "schema.output_schema")
    require_true(schema.get("numeric_validation_passed"), "schema.numeric_validation_passed")
    require_equal(provenance.get("source_zip_sha256"), SOURCE_ZIP_SHA256, "provenance.source_zip_sha256")
    require_equal(provenance.get("expected_inner_csv"), EXPECTED_INNER_CSV, "provenance.expected_inner_csv")
    require_equal(provenance.get("output_row_count"), EXPECTED_OUTPUT_ROWS, "provenance.output_row_count")
    require_equal(provenance.get("provenance_status"), "SINGLE_FILE_PIPELINE_SMOKE_TEST_BUILD_OUTPUT", "provenance.status")
    require_true(isinstance(provenance.get("source_url"), str) and bool(provenance.get("source_url")), "provenance.source_url")
    require_true(isinstance(provenance.get("output_csv_path"), str) and bool(provenance.get("output_csv_path")), "provenance.output_csv_path")
    require_true(compliance.get("no_new_download"), "compliance.no_new_download")
    require_true(compliance.get("no_api"), "compliance.no_api")
    require_true(compliance.get("no_browse"), "compliance.no_browse")
    require_true(compliance.get("no_multi_file"), "compliance.no_multi_file")
    require_true(compliance.get("no_multi_symbol"), "compliance.no_multi_symbol")
    require_true(compliance.get("no_strategy_backtest_candidate"), "compliance.no_strategy_backtest_candidate")
    require_true(compliance.get("no_runtime_capital_live"), "compliance.no_runtime_capital_live")
    require_true(compliance.get("no_generic_runner"), "compliance.no_generic_runner")
    require_true(compliance.get("no_repo_schema_config"), "compliance.no_repo_schema_config")
    require_true(compliance.get("output_is_pipeline_smoke_test_only"), "compliance.output_is_pipeline_smoke_test_only")
    require_false(compliance.get("output_valid_for_research_backtest"), "compliance.output_valid_for_research_backtest")
    require_false(compliance.get("output_valid_for_edge_claim"), "compliance.output_valid_for_edge_claim")
    require_false(compliance.get("broad_acquisition_ready"), "compliance.broad_acquisition_ready")
    require_false(compliance.get("source_manifest_acquisition_ready"), "compliance.source_manifest_acquisition_ready")

    require_equal(preview.get("next_module"), "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_after_preview_approval_v1.py", "preview.next_module")
    require_true(download_validator.get("safe_for_single_file_pipeline_build_preview"), "download_validator.safe_for_single_file_pipeline_build_preview")
    require_true(policy_validator.get("okx_1m_to_1h_aggregation_policy_validated"), "policy_validator.validated")

    output_path = Path(str(provenance["output_csv_path"]))
    require_equal(str(output_path), str(aggregation_execution.get("output_csv_path")), "output_path.report_consistency")
    require_equal(str(output_path), str(summary.get("output_csv_path")), "output_path.summary_consistency")

    return {
        "whole_system_preflight_completed": True,
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
        "head": head,
        "output_csv_path": str(output_path),
    }


def parse_decimal(value: str) -> Decimal:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(str(exc)) from exc
    if not parsed.is_finite():
        raise ValueError("non-finite")
    return parsed


def bool_from_csv(value: str) -> bool:
    return str(value).strip().lower() == "true"


def validate_output_csv(output_path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    output_csv_exists = output_path.exists() and output_path.is_file()
    if not output_csv_exists:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: output CSV missing: {output_path}")
    try:
        with output_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames or []
            rows = list(reader)
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: output CSV unreadable: {output_path}") from exc

    schema_match = fieldnames == EXPECTED_OUTPUT_SCHEMA
    if not schema_match:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: output CSV schema mismatch")
    if len(rows) != EXPECTED_OUTPUT_ROWS:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: output row count={len(rows)} expected {EXPECTED_OUTPUT_ROWS}")

    symbols = sorted({row["instrument_name"] for row in rows})
    scopes = sorted({row["build_scope"] for row in rows})
    hashes = sorted({row["source_zip_sha256"] for row in rows})
    source_row_counts = [int(row["source_row_count"]) for row in rows]
    complete_hour_flags = [bool_from_csv(row["complete_hour"]) for row in rows]
    source_csv_files = sorted({row["source_csv_file"] for row in rows})
    require_equal(symbols, [TARGET_SYMBOL], "output.symbols")
    require_equal(scopes, [BUILD_SCOPE], "output.scopes")
    require_equal(hashes, [SOURCE_ZIP_SHA256], "output.hashes")
    require_equal(source_csv_files, [EXPECTED_INNER_CSV], "output.source_csv_files")
    if any(value != EXPECTED_SOURCE_ROWS_PER_HOUR for value in source_row_counts):
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: output source_row_count not all 60")
    if any(flag is not True for flag in complete_hour_flags):
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: output complete_hour not all true")

    hour_values = [int(row["hour_start_epoch_ms"]) for row in rows]
    monotonic = all(hour_values[index] < hour_values[index + 1] for index in range(len(hour_values) - 1))
    duplicate_hour_count = len(hour_values) - len(set(hour_values))
    missing_hour_count = 0
    if monotonic:
        missing_hour_count = sum(
            (hour_values[index + 1] - hour_values[index]) // EXPECTED_INTERVAL_MS - 1
            for index in range(len(hour_values) - 1)
            if hour_values[index + 1] - hour_values[index] > EXPECTED_INTERVAL_MS
        )
    require_true(monotonic, "output.hours_monotonic")
    require_equal(duplicate_hour_count, 0, "output.duplicate_hour_count")
    require_equal(missing_hour_count, 0, "output.missing_hour_count")
    require_equal(len(set(hour_values)), EXPECTED_OUTPUT_ROWS, "output.unique_hour_count")

    timezone_safe = all(
        row["hour_start_iso_utc"].endswith("+00:00")
        and datetime.fromisoformat(row["hour_start_iso_utc"]).tzinfo is not None
        and int(row["hour_start_epoch_ms"]) % EXPECTED_INTERVAL_MS == 0
        for row in rows
    )
    require_true(timezone_safe, "output.utc_timezone_fields")

    invalid_numeric_rows = 0
    negative_volume_rows = 0
    nan_inf_rows = 0
    numeric_fields = ["open", "high", "low", "close", "vol", "vol_ccy", "vol_quote"]
    for row in rows:
        parsed: Dict[str, Decimal] = {}
        row_invalid = False
        row_negative_volume = False
        row_nan_inf = False
        for field in numeric_fields:
            try:
                parsed[field] = parse_decimal(row[field])
            except ValueError:
                row_invalid = True
                try:
                    as_float = float(row[field])
                    if math.isnan(as_float) or math.isinf(as_float):
                        row_nan_inf = True
                except ValueError:
                    pass
        if not row_invalid:
            if parsed["high"] < max(parsed["open"], parsed["close"], parsed["low"]):
                row_invalid = True
            if parsed["low"] > min(parsed["open"], parsed["close"], parsed["high"]):
                row_invalid = True
            if parsed["vol"] < 0 or parsed["vol_ccy"] < 0 or parsed["vol_quote"] < 0:
                row_negative_volume = True
        invalid_numeric_rows += 1 if row_invalid else 0
        negative_volume_rows += 1 if row_negative_volume else 0
        nan_inf_rows += 1 if row_nan_inf else 0

    if invalid_numeric_rows or negative_volume_rows or nan_inf_rows:
        raise RuntimeError(
            f"{STATUS_BLOCKED_CONTEXT}: numeric sanity failed invalid={invalid_numeric_rows} "
            f"negative_volume={negative_volume_rows} nan_inf={nan_inf_rows}"
        )

    output_validation = {
        "output_csv_exists": True,
        "output_csv_readable": True,
        "output_csv_row_count": len(rows),
        "output_schema_validated": True,
        "output_expected_schema_match": True,
        "output_symbol_count": len(symbols),
        "output_observed_symbol": symbols[0],
        "output_hour_count": len(hour_values),
        "output_unique_hour_count": len(set(hour_values)),
        "output_duplicate_hour_count": duplicate_hour_count,
        "output_missing_hour_count": missing_hour_count,
        "output_hours_monotonic": monotonic,
        "output_all_source_row_count_60": True,
        "output_all_complete_hour_true": True,
        "output_no_local_timezone_dependence": True,
        "source_zip_sha256_matches_output": True,
        "output_csv_sha256": sha256_file(output_path),
    }
    numeric_report = {
        "numeric_sanity_validated": True,
        "invalid_numeric_row_count": invalid_numeric_rows,
        "negative_volume_row_count": negative_volume_rows,
        "nan_inf_row_count": nan_inf_rows,
        "validated_numeric_fields": numeric_fields,
        "ohlc_order_validated": True,
        "volume_non_negative_validated": True,
    }
    return output_validation, numeric_report


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_payload(
    artifacts: Dict[str, Dict[str, Any]],
    artifact_status: Dict[str, Any],
    preflight: Dict[str, Any],
    output_validation: Dict[str, Any],
    numeric_report: Dict[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    summary = artifacts["build_execution_summary"]
    gap_duplicate = artifacts["gap_duplicate_report"]
    provenance = artifacts["output_provenance_report"]
    compliance = artifacts["build_execution_compliance_report"]
    flags = dangerous_flags()
    provenance_validation = {
        "provenance_validated": True,
        "source_url_recorded": True,
        "source_zip_sha256_recorded": True,
        "source_csv_file_recorded": True,
        "output_path_recorded": True,
        "source_url": provenance["source_url"],
        "source_zip_sha256": provenance["source_zip_sha256"],
        "source_csv_file": provenance["expected_inner_csv"],
        "output_csv_path": provenance["output_csv_path"],
        "output_is_pipeline_smoke_test_only": True,
        "provenance_does_not_imply_broad_source_manifest_readiness": True,
        "provenance_does_not_imply_research_backtest_edge_readiness": True,
    }
    compliance_validation = {
        "no_new_download": True,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "new_download_performed_by_validator": False,
        "data_build_performed_by_validator": False,
        "aggregation_performed_by_validator": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "okx_sample_zip_downloaded_now": False,
        "no_api": compliance["no_api"],
        "no_browse": compliance["no_browse"],
        "no_multi_file_work": compliance["no_multi_file"],
        "no_multi_symbol_work": compliance["no_multi_symbol"],
        "no_strategy_backtest_candidate_runtime_live_capital": True,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
    }
    replacement_checks = {
        "preflight_passed": preflight["whole_system_preflight_completed"] is True,
        "artifact_chain_consistent": preflight["artifact_chain_consistent"] is True,
        "execution_artifacts_validated": artifact_status["execution_artifacts_exist"] is True
        and artifact_status["execution_artifacts_valid_json"] is True,
        "build_execution_validated": True,
        "output_csv_validated": output_validation["output_csv_row_count"] == EXPECTED_OUTPUT_ROWS
        and output_validation["output_expected_schema_match"] is True,
        "output_hours_validated": output_validation["output_unique_hour_count"] == EXPECTED_OUTPUT_ROWS
        and output_validation["output_duplicate_hour_count"] == 0
        and output_validation["output_missing_hour_count"] == 0,
        "numeric_sanity_validated": numeric_report["numeric_sanity_validated"] is True,
        "provenance_validated": provenance_validation["provenance_validated"] is True,
        "no_validator_download_build_aggregation": compliance_validation["new_download_performed_by_validator"] is False
        and compliance_validation["data_build_performed_by_validator"] is False
        and compliance_validation["aggregation_performed_by_validator"] is False,
        "not_research_backtest_edge": True,
        "broad_and_multi_symbol_blocked": True,
        "schema_config_absent": planned_schema_files_existing_count() == 0,
        "generic_runner_absent": generic_runner_target_exists() is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
    }
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_validator_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "WRITE_SINGLE_SYMBOL_PIPELINE_SMOKE_TEST_SUMMARY_NO_BROAD_ACQUISITION",
        "next_module": NEXT_MODULE_PASS,
        **preflight,
        **artifact_status,
        "build_execution_validated": True,
        "single_symbol_1h_output_validated": True,
        "build_scope": BUILD_SCOPE,
        "target_symbol": TARGET_SYMBOL,
        **output_validation,
        "complete_1h_row_count": summary["complete_1h_row_count"],
        "incomplete_1h_row_count": summary["incomplete_1h_row_count"],
        "all_hours_complete": summary["all_hours_complete"],
        "synthetic_fill_used": summary["synthetic_fill_used"],
        "forward_fill_used": summary["forward_fill_used"],
        "backfill_used": summary["backfill_used"],
        "duplicate_minute_count": gap_duplicate["duplicate_minute_count"],
        "missing_minute_count": gap_duplicate["missing_minute_count"],
        **numeric_report,
        **provenance_validation,
        "output_valid_for_pipeline_smoke_test": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_single_symbol_pipeline_smoke_test_summary": True,
        "safe_for_broad_acquisition": False,
        "safe_for_multi_symbol_build": False,
        **compliance_validation,
        "strategy_signal_claims_made": False,
        "tradable_edge_claims_made": False,
        "profit_claims_made": False,
        "backtest_performed": False,
        "candidate_generation_performed": False,
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "generic_runner_approval_granted": False,
        "validator_p0_count": 0,
        "validator_p1_count": max(8, int(summary.get("active_p1_attention_count", 8))),
        "current_evidence_chain_quality_before_validator": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_validator": EVIDENCE_AFTER,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": max(8, int(summary.get("active_p1_attention_count", 8))),
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
            "validated the previous BTC-USDT-SWAP single-day 1m-to-1h pipeline smoke-test build from existing JSON "
            "artifacts and the existing 24-row 1h output CSV only; the validator performed no new download, API call, "
            "browse, data build, aggregation, multi-file, multi-symbol, research, backtest, candidate, runtime, capital, "
            "live, schema/config, or generic-runner action"
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

    reports = {
        "execution_artifact_validation": {
            "execution_artifacts_exist": True,
            "execution_artifacts_valid_json": True,
            "execution_status_validated": True,
            "build_scope_single_symbol_single_day_only": True,
            "target_symbol_validated": True,
            "no_new_download_api_browse_during_build": True,
            "artifact_status": artifact_status,
        },
        "output_csv_validation": output_validation,
        "aggregation_result_validation": {
            "complete_1h_row_count": payload["complete_1h_row_count"],
            "incomplete_1h_row_count": payload["incomplete_1h_row_count"],
            "all_hours_complete": payload["all_hours_complete"],
            "synthetic_fill_used": payload["synthetic_fill_used"],
            "forward_fill_used": payload["forward_fill_used"],
            "backfill_used": payload["backfill_used"],
            "duplicate_minute_count": payload["duplicate_minute_count"],
            "missing_minute_count": payload["missing_minute_count"],
            "output_not_research_backtest_edge_ready": True,
        },
        "numeric_sanity_validation": numeric_report,
        "provenance_validation": provenance_validation,
        "compliance_validation": compliance_validation,
        "risk_decision": {
            "build_execution_validated": True,
            "single_symbol_1h_output_validated": True,
            "output_valid_for_pipeline_smoke_test": True,
            "output_valid_for_research_backtest": False,
            "output_valid_for_edge_claim": False,
            "safe_for_single_symbol_pipeline_smoke_test_summary": True,
            "safe_for_broad_acquisition": False,
            "safe_for_multi_symbol_build": False,
            "validator_p0_count": 0,
            "validator_p1_count": payload["validator_p1_count"],
        },
        "next_module_decision": {
            "next_module": NEXT_MODULE_PASS,
            "next_action": payload["next_action"],
        },
    }
    return payload, reports


def write_artifacts(payload: Dict[str, Any], reports: Dict[str, Dict[str, Any]]) -> None:
    outputs = {
        "historical_okx_single_symbol_1m_to_1h_build_execution_validator.json": {
            "generated_at_utc": utc_now(),
            **reports,
            "summary": payload,
        },
        "historical_okx_single_symbol_1m_to_1h_output_validation_report.json": reports["output_csv_validation"],
        "historical_okx_single_symbol_1m_to_1h_output_numeric_sanity_report.json": reports["numeric_sanity_validation"],
        "historical_okx_single_symbol_1m_to_1h_output_provenance_validation_report.json": reports["provenance_validation"],
        "historical_okx_single_symbol_1m_to_1h_build_execution_validator_summary.json": payload,
        "repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_validator_after_execution_v1_latest.json": payload,
    }
    for name, artifact in outputs.items():
        write_json(OUT_DIR / name, artifact)


def blocked_payload(exc: Exception) -> Dict[str, Any]:
    flags = dangerous_flags()
    message = str(exc)
    blocked_status = STATUS_BLOCKED_NEXT_MODULE if STATUS_BLOCKED_NEXT_MODULE in message else STATUS_BLOCKED_CONTEXT
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_validator_status": blocked_status,
        "final_decision": blocked_status,
        "next_action": "STOP_FAIL_CLOSED_NO_SINGLE_SYMBOL_1M_TO_1H_BUILD_VALIDATION",
        "next_module": NEXT_MODULE_BLOCKED,
        "error": message,
        "whole_system_preflight_completed": False,
        "live_next_module_matches_requested_module": False,
        "artifact_chain_consistent": False,
        "stale_or_contradictory_artifact_detected": True,
        "execution_artifacts_exist": False,
        "execution_artifacts_valid_json": False,
        "build_execution_validated": False,
        "build_scope": BUILD_SCOPE,
        "target_symbol": TARGET_SYMBOL,
        "output_csv_exists": False,
        "output_csv_readable": False,
        "output_csv_row_count": 0,
        "output_schema_validated": False,
        "output_expected_schema_match": False,
        "output_symbol_count": 0,
        "output_observed_symbol": "",
        "output_hour_count": 0,
        "output_unique_hour_count": 0,
        "output_duplicate_hour_count": 0,
        "output_missing_hour_count": 0,
        "output_hours_monotonic": False,
        "output_all_source_row_count_60": False,
        "output_all_complete_hour_true": False,
        "complete_1h_row_count": 0,
        "incomplete_1h_row_count": 0,
        "all_hours_complete": False,
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "duplicate_minute_count": 0,
        "missing_minute_count": 0,
        "numeric_sanity_validated": False,
        "invalid_numeric_row_count": 0,
        "negative_volume_row_count": 0,
        "nan_inf_row_count": 0,
        "provenance_validated": False,
        "source_zip_sha256_matches_output": False,
        "output_is_pipeline_smoke_test_only": True,
        "output_valid_for_pipeline_smoke_test": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_single_symbol_pipeline_smoke_test_summary": False,
        "safe_for_broad_acquisition": False,
        "safe_for_multi_symbol_build": False,
        "no_new_download": True,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "new_download_performed_by_validator": False,
        "data_build_performed_by_validator": False,
        "aggregation_performed_by_validator": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "okx_sample_zip_downloaded_now": False,
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
        "current_evidence_chain_quality_after_validator": blocked_status,
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
        "derived_live_repo_post_check": blocked_status,
        "derived_live_repo_post_check_reason": message,
        "replacement_checks_all_true": False,
    }


def main() -> int:
    try:
        artifacts, artifact_status = validate_required_artifacts()
        preflight = validate_preflight(artifacts)
        output_validation, numeric_report = validate_output_csv(Path(preflight["output_csv_path"]))
        payload, reports = build_payload(artifacts, artifact_status, preflight, output_validation, numeric_report)
        write_artifacts(payload, reports)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        payload = blocked_payload(exc)
        write_json(
            OUT_DIR
            / "repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_validator_after_execution_v1_latest.json",
            payload,
        )
        write_json(OUT_DIR / "historical_okx_single_symbol_1m_to_1h_build_execution_validator_summary.json", payload)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
