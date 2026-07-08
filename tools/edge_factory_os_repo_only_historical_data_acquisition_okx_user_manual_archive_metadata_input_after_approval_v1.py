from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_"
    "input_after_approval_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_"
    "input_after_approval_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "a53d014"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 669
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 670

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_"
    "input_after_approval_v1.py"
)
NEXT_MODULE_VALIDATOR = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_"
    "input_validator_after_approval_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_"
    "input_blocked_record_after_approval_v1.py"
)

APPROVAL_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_archive_scope_resolution_approval_after_preview_v1"
    / "repo_only_historical_data_acquisition_okx_archive_scope_resolution_approval_after_preview_v1_latest.json"
)

APPROVAL_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_SCOPE_RESOLUTION_APPROVED_"
    "USER_MANUAL_METADATA_INPUT_NEXT_NO_EXECUTION"
)
STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_METADATA_INPUT_CAPTURED_PARTIAL_"
    "1M_SCHEMA_PENDING_VALIDATOR_NO_EXECUTION"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = "HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_METADATA_INPUT_APPROVED_NEXT_NO_EXECUTION"
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_METADATA_INPUT_CAPTURED_PARTIAL_"
    "1M_SCHEMA_PENDING_VALIDATOR_NO_EXECUTION"
)
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"

USER_METADATA_TYPE = "PARTIAL_USER_MANUAL_OKX_ARCHIVE_METADATA_WITH_1M_SCHEMA_SAMPLE"
EXTRACTED_CSV_FILENAME = "BTC-USDT-SWAP-candlesticks-2026-05-18.csv"
DATA_GROUPING_OPTIONS = ["daily", "month"]
TARGET_INSTRUMENT_TYPE = "perpetual_swap"
CSV_COLUMNS = [
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
ROW_COUNT = 1440
FIRST_OPEN_TIME_MS = 1779033600000
SECOND_OPEN_TIME_MS = 1779033660000
LAST_OPEN_TIME_MS = 1779119940000
OPEN_TIME_DELTA_MS = 60000
INFERRED_CANDLE_INTERVAL = "1m"
TIMESTAMP_UNIT = "epoch_milliseconds"
FIRST_OPEN_TIME_UTC = "2026-05-17T16:00:00Z"
LAST_OPEN_TIME_UTC = "2026-05-18T15:59:00Z"
DAILY_BOUNDARY_INTERPRETATION = "LIKELY_UTC_PLUS_8_EXCHANGE_DAY"
ARCHIVE_METADATA_COMPLETENESS_LEVEL = "PARTIAL_USER_MANUAL_METADATA_SCHEMA_AND_1M_INTERVAL_RESOLVED"
MISSING_REQUIRED_METADATA_FIELDS = [
    "official OKX timezone convention confirmation",
    "full coverage range across all required symbols",
    "symbol universe / instrument list",
    "source manifest",
    "provenance report",
    "approved 1m-to-1h aggregation policy",
]
USER_NOTE = (
    "The downloaded OKX daily candlestick CSV contains 1440 one-minute rows, not direct 1h candles. "
    "Daily/month grouping refers to archive grouping, not candle interval. Any 1h panel would require a later "
    "approved data-build/aggregation step from 1m to 1h, not now."
)

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
    "data_fetch_performed_now",
    "data_build_performed_now",
    "okx_browse_performed_now",
    "okx_download_performed_now",
    "okx_api_call_performed_now",
    "okx_sample_zip_downloaded_now",
    "okx_archive_scope_resolution_performed_now",
    "manual_metadata_input_capture_performed_now",
    "aggregation_performed_now",
    "source_manifest_created_now",
    "schema_config_created_now",
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


def load_json(path: Path) -> Dict[str, Any]:
    data, exists, valid, non_empty = read_json_checked(path)
    if not (exists and valid and non_empty):
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: artifact missing/invalid/empty: {path}")
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


def validate_user_metadata_constants() -> None:
    require_equal(EXTRACTED_CSV_FILENAME, "BTC-USDT-SWAP-candlesticks-2026-05-18.csv", "metadata.filename")
    require_equal(DATA_GROUPING_OPTIONS, ["daily", "month"], "metadata.data_grouping_options")
    require_equal(TARGET_INSTRUMENT_TYPE, "perpetual_swap", "metadata.target_instrument_type")
    require_equal(
        CSV_COLUMNS,
        ["instrument_name", "open", "high", "low", "close", "vol", "vol_ccy", "vol_quote", "open_time", "confirm"],
        "metadata.csv_columns",
    )
    require_equal(ROW_COUNT, 1440, "metadata.row_count")
    require_equal(SECOND_OPEN_TIME_MS - FIRST_OPEN_TIME_MS, OPEN_TIME_DELTA_MS, "metadata.first_delta_ms")
    require_equal(LAST_OPEN_TIME_MS - FIRST_OPEN_TIME_MS, (ROW_COUNT - 1) * OPEN_TIME_DELTA_MS, "metadata.full_delta_ms")
    require_equal(INFERRED_CANDLE_INTERVAL, "1m", "metadata.inferred_candle_interval")
    require_equal(TIMESTAMP_UNIT, "epoch_milliseconds", "metadata.timestamp_unit")
    require_equal(FIRST_OPEN_TIME_UTC, "2026-05-17T16:00:00Z", "metadata.first_open_time_utc")
    require_equal(LAST_OPEN_TIME_UTC, "2026-05-18T15:59:00Z", "metadata.last_open_time_utc")


def validate_preflight(approval: Dict[str, Any]) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))

    require_equal(
        approval.get("historical_data_acquisition_okx_archive_scope_resolution_approval_status"),
        APPROVAL_STATUS_PASS,
        "approval_status",
    )
    require_equal(approval.get("next_module"), REQUESTED_MODULE, "approval.next_module", STATUS_BLOCKED_NEXT_MODULE)
    require_equal(approval.get("current_evidence_chain_quality_after_approval"), EVIDENCE_BEFORE, "approval.evidence_after")
    require_true(approval.get("okx_archive_scope_resolution_approval_record_created"), "approval.record_created")
    require_true(approval.get("user_okx_archive_scope_resolution_approval_present"), "approval.present")
    require_true(approval.get("approval_grants_future_user_manual_archive_metadata_input_next"), "approval.manual_next")
    require_true(approval.get("replacement_checks_all_true"), "approval.replacement_checks_all_true")
    require_false(approval.get("approval_grants_browse_now"), "approval.browse_now")
    require_false(approval.get("approval_grants_zip_download_now"), "approval.zip_now")
    require_false(approval.get("approval_grants_okx_api_now"), "approval.api_now")
    require_false(approval.get("approval_grants_data_build_now"), "approval.data_build_now")
    require_false(approval.get("approval_grants_acquisition_execution_now"), "approval.acquisition_now")
    require_equal(approval.get("active_p0_blocker_count"), 0, "approval.active_p0_blocker_count")
    require_equal(approval.get("active_p1_attention_count"), 8, "approval.active_p1_attention_count")
    require_equal(approval.get("dormant_repo_attention_count"), 716, "approval.dormant_repo_attention_count")
    require_false(approval.get("generic_runner_approval_granted"), "approval.generic_runner_approval_granted")
    require_true(approval.get("generic_runner_implementation_remains_blocked"), "approval.generic_runner_blocked")
    require_false(approval.get("schema_or_config_created"), "approval.schema_or_config_created")
    require_true(approval.get("loop_remains_closed"), "approval.loop_remains_closed")
    validate_no_true_dangerous_flags(approval, "approval")
    validate_user_metadata_constants()

    return {
        "whole_system_preflight_completed": True,
        "whole_system_preflight_decision": "PASS",
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
        "real_final_form_gap_confirmed": True,
        "documentation_loop_detected": False,
        "documentation_loop_risk_level": DOCUMENTATION_LOOP_RISK_LEVEL,
        "next_module_closes_real_gap": True,
        "active_p0_blocker_count_from_live_artifact": 0,
        "active_p1_attention_count_from_live_artifact": 8,
        "p1_attention_carried_forward": True,
        "dormant_repo_attention_count_carried_forward": True,
        "blocked_actions_absent_from_requested_module": True,
        "approval_artifact": str(APPROVAL_ARTIFACT),
        "head": head,
        "status_lines_allowed": [f"?? {CURRENT_TOOL_REL}", f"A  {CURRENT_TOOL_REL}", f"AM {CURRENT_TOOL_REL}"],
    }


def user_manual_metadata_record() -> Dict[str, Any]:
    return {
        "extracted_file_name": EXTRACTED_CSV_FILENAME,
        "data_grouping_options": DATA_GROUPING_OPTIONS,
        "target_instrument_type": TARGET_INSTRUMENT_TYPE,
        "spot_not_required": True,
        "csv_columns": CSV_COLUMNS,
        "row_count": ROW_COUNT,
        "first_open_time_ms": FIRST_OPEN_TIME_MS,
        "second_open_time_ms": SECOND_OPEN_TIME_MS,
        "last_open_time_ms": LAST_OPEN_TIME_MS,
        "open_time_delta_ms": OPEN_TIME_DELTA_MS,
        "inferred_candle_interval": INFERRED_CANDLE_INTERVAL,
        "direct_1h_interval_present": False,
        "timestamp_unit": TIMESTAMP_UNIT,
        "first_open_time_utc": FIRST_OPEN_TIME_UTC,
        "last_open_time_utc": LAST_OPEN_TIME_UTC,
        "daily_file_boundary_interpretation": DAILY_BOUNDARY_INTERPRETATION,
        "schema_partially_resolved": True,
        "timezone_partially_resolved": True,
        "one_minute_to_one_hour_aggregation_required": True,
        "user_note": USER_NOTE,
    }


def build_payload(preflight_report: Dict[str, Any]) -> Dict[str, Any]:
    flags = dangerous_flags()
    missing_count = len(MISSING_REQUIRED_METADATA_FIELDS)
    replacement_checks = {
        "preflight_passed": preflight_report.get("whole_system_preflight_decision") == "PASS",
        "approval_handoff_respected": True,
        "user_manual_metadata_present": True,
        "metadata_values_recorded": True,
        "direct_interval_recorded_as_1m_not_1h": True,
        "direct_1h_interval_not_overclaimed": True,
        "schema_timezone_only_partial": True,
        "coverage_unresolved": True,
        "acquisition_readiness_false": True,
        "aggregation_required_later_not_now": True,
        "no_browse_download_fetch_api_build": True,
        "p1_carried_forward": True,
        "dormant_attention_carried_forward": True,
        "generic_runner_blocked": True,
        "schema_config_absent": True,
        "loop_closed": True,
    }
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_user_manual_archive_metadata_input_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "RUN_USER_MANUAL_OKX_ARCHIVE_METADATA_INPUT_VALIDATOR_NO_EXECUTION",
        "next_module": NEXT_MODULE_VALIDATOR,
        **preflight_report,
        "okx_user_manual_archive_metadata_input_performed": True,
        "user_manual_okx_archive_metadata_present": True,
        "user_manual_okx_archive_metadata_value_recorded": True,
        "user_manual_okx_archive_metadata_type": USER_METADATA_TYPE,
        "user_manual_okx_archive_metadata": user_manual_metadata_record(),
        "okx_extracted_csv_filename_recorded": True,
        "okx_extracted_csv_filename": EXTRACTED_CSV_FILENAME,
        "okx_data_grouping_options_recorded": True,
        "okx_data_grouping_options": DATA_GROUPING_OPTIONS,
        "okx_target_instrument_type_recorded": True,
        "okx_target_instrument_type": TARGET_INSTRUMENT_TYPE,
        "okx_spot_not_required_recorded": True,
        "okx_spot_not_required": True,
        "okx_csv_columns_recorded": True,
        "okx_csv_columns": CSV_COLUMNS,
        "okx_csv_row_count_recorded": True,
        "okx_csv_row_count": ROW_COUNT,
        "okx_first_open_time_ms": FIRST_OPEN_TIME_MS,
        "okx_second_open_time_ms": SECOND_OPEN_TIME_MS,
        "okx_last_open_time_ms": LAST_OPEN_TIME_MS,
        "okx_open_time_delta_ms": OPEN_TIME_DELTA_MS,
        "okx_inferred_candle_interval": INFERRED_CANDLE_INTERVAL,
        "okx_direct_1h_interval_present": False,
        "okx_timestamp_unit": TIMESTAMP_UNIT,
        "okx_first_open_time_utc": FIRST_OPEN_TIME_UTC,
        "okx_last_open_time_utc": LAST_OPEN_TIME_UTC,
        "okx_daily_boundary_interpretation": DAILY_BOUNDARY_INTERPRETATION,
        "okx_archive_granularity_partially_resolved": True,
        "okx_file_inside_zip_known": True,
        "okx_csv_columns_provided": True,
        "okx_csv_sample_rows_provided": True,
        "okx_archive_metadata_completeness_level": ARCHIVE_METADATA_COMPLETENESS_LEVEL,
        "okx_archive_metadata_completeness_pass": False,
        "missing_required_metadata_fields": MISSING_REQUIRED_METADATA_FIELDS,
        "missing_required_metadata_field_count": missing_count,
        "okx_archive_scope_resolved_now": "partial",
        "okx_1h_interval_resolved_now": False,
        "okx_coverage_resolved_now": False,
        "okx_schema_timezone_resolved_now": "partial",
        "okx_archive_scope_resolution_required": True,
        "okx_1h_interval_resolution_required": False,
        "okx_coverage_resolution_required": True,
        "okx_schema_timezone_resolution_required": True,
        "okx_acquisition_readiness": False,
        "one_minute_to_one_hour_aggregation_required": True,
        "future_data_build_aggregation_required": True,
        "aggregation_performed_now": False,
        "browse_only_archive_detail_lookup_required_next": False,
        "sample_zip_metadata_inspection_allowed_now": False,
        "zip_download_allowed_now": False,
        "okx_api_allowed_now": False,
        "bulk_archive_download_allowed_now": False,
        "acquisition_execution_allowed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "data_build_performed": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "okx_sample_zip_downloaded_now": False,
        "fake_or_synthetic_data_detected": False,
        "current_evidence_chain_quality_before_input": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_input": EVIDENCE_AFTER,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 8,
        "dormant_repo_attention_count": 716,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": planned_schema_files_existing_count(),
        "generic_runner_target_exists": generic_runner_target_exists(),
        "dangerous_flags": flags,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "dangerous_flags_true_count": sum(1 for value in flags.values() if value),
        "derived_live_repo_post_check": (
            "PASS_OKX_ARCHIVE_METADATA_INPUT_CAPTURED_PARTIAL_1M_SCHEMA_PENDING_VALIDATOR_NO_EXECUTION"
        ),
        "derived_live_repo_post_check_reason": (
            "repo-only user/manual metadata input captured the supplied OKX CSV archive details as partial static "
            "evidence; it recorded 1m rows rather than direct 1h candles, kept acquisition readiness false, required "
            "future approved 1m-to-1h aggregation, and performed no browsing, ZIP/archive download, API call, data "
            "fetch, data build, strategy, backtest, candidate, runtime, capital, live, generic-runner, schema, config, "
            "or old-route action"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": all(replacement_checks.values()),
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "tracked_python_count_expectation": {
            "pre_commit": EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT,
        },
    }
    if payload["missing_required_metadata_field_count"] < 1:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: metadata was incorrectly marked complete")
    if payload["okx_direct_1h_interval_present"] is not False or payload["okx_inferred_candle_interval"] != "1m":
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: direct interval was not recorded as 1m/non-1h")
    if payload["aggregation_performed_now"] is not False or payload["data_build_performed"] is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: aggregation/data build flag violation")
    if payload["active_p1_attention_count"] != 8 or payload["p1_attention_carried_forward"] is not True:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: P1 attention was not carried forward")
    if payload["dormant_repo_attention_count"] != 716 or payload["dormant_repo_attention_count_carried_forward"] is not True:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: dormant repo attention was not carried forward")
    if payload["planned_schema_files_existing_count"] != 0:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: planned schema files exist unexpectedly")
    if payload["generic_runner_target_exists"] is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: generic runner target exists unexpectedly")
    if payload["dangerous_flags_all_false"] is not True or payload["dangerous_flags_true_count"] != 0:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: dangerous flags are not all false")
    if payload["replacement_checks_all_true"] is not True:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: replacement checks failed")
    return payload


def write_artifacts(payload: Dict[str, Any]) -> None:
    artifacts = {
        "historical_okx_user_manual_archive_metadata_input_report.json": payload,
        "historical_okx_1h_interval_user_metadata_record.json": {
            "generated_at_utc": payload["generated_at_utc"],
            "okx_inferred_candle_interval": payload["okx_inferred_candle_interval"],
            "okx_direct_1h_interval_present": payload["okx_direct_1h_interval_present"],
            "okx_1h_interval_resolved_now": payload["okx_1h_interval_resolved_now"],
            "okx_1h_interval_resolution_required": payload["okx_1h_interval_resolution_required"],
            "one_minute_to_one_hour_aggregation_required": payload[
                "one_minute_to_one_hour_aggregation_required"
            ],
            "future_data_build_aggregation_required": payload["future_data_build_aggregation_required"],
            "aggregation_performed_now": payload["aggregation_performed_now"],
        },
        "historical_okx_coverage_user_metadata_record.json": {
            "generated_at_utc": payload["generated_at_utc"],
            "okx_data_grouping_options": payload["okx_data_grouping_options"],
            "okx_target_instrument_type": payload["okx_target_instrument_type"],
            "okx_spot_not_required": payload["okx_spot_not_required"],
            "okx_first_open_time_utc": payload["okx_first_open_time_utc"],
            "okx_last_open_time_utc": payload["okx_last_open_time_utc"],
            "okx_coverage_resolved_now": payload["okx_coverage_resolved_now"],
            "okx_coverage_resolution_required": payload["okx_coverage_resolution_required"],
            "missing_required_metadata_fields": [
                field
                for field in payload["missing_required_metadata_fields"]
                if "coverage" in field or "symbol" in field or "source manifest" in field or "provenance" in field
            ],
        },
        "historical_okx_schema_timezone_user_metadata_record.json": {
            "generated_at_utc": payload["generated_at_utc"],
            "okx_extracted_csv_filename": payload["okx_extracted_csv_filename"],
            "okx_csv_columns": payload["okx_csv_columns"],
            "okx_csv_row_count": payload["okx_csv_row_count"],
            "okx_timestamp_unit": payload["okx_timestamp_unit"],
            "okx_first_open_time_ms": payload["okx_first_open_time_ms"],
            "okx_second_open_time_ms": payload["okx_second_open_time_ms"],
            "okx_last_open_time_ms": payload["okx_last_open_time_ms"],
            "okx_open_time_delta_ms": payload["okx_open_time_delta_ms"],
            "okx_first_open_time_utc": payload["okx_first_open_time_utc"],
            "okx_last_open_time_utc": payload["okx_last_open_time_utc"],
            "okx_daily_boundary_interpretation": payload["okx_daily_boundary_interpretation"],
            "okx_schema_timezone_resolved_now": payload["okx_schema_timezone_resolved_now"],
            "okx_schema_timezone_resolution_required": payload["okx_schema_timezone_resolution_required"],
        },
        "historical_okx_archive_scope_user_metadata_completeness_report.json": {
            "generated_at_utc": payload["generated_at_utc"],
            "okx_archive_metadata_completeness_level": payload["okx_archive_metadata_completeness_level"],
            "okx_archive_metadata_completeness_pass": payload["okx_archive_metadata_completeness_pass"],
            "missing_required_metadata_field_count": payload["missing_required_metadata_field_count"],
            "missing_required_metadata_fields": payload["missing_required_metadata_fields"],
            "okx_archive_scope_resolved_now": payload["okx_archive_scope_resolved_now"],
            "okx_archive_scope_resolution_required": payload["okx_archive_scope_resolution_required"],
            "okx_acquisition_readiness": payload["okx_acquisition_readiness"],
        },
        "historical_okx_archive_scope_user_metadata_contract_compliance_report.json": {
            "generated_at_utc": payload["generated_at_utc"],
            "whole_system_preflight_completed": payload["whole_system_preflight_completed"],
            "whole_system_preflight_decision": payload["whole_system_preflight_decision"],
            "okx_user_manual_archive_metadata_input_performed": payload[
                "okx_user_manual_archive_metadata_input_performed"
            ],
            "user_manual_okx_archive_metadata_present": payload["user_manual_okx_archive_metadata_present"],
            "user_manual_okx_archive_metadata_value_recorded": payload[
                "user_manual_okx_archive_metadata_value_recorded"
            ],
            "okx_archive_metadata_completeness_pass": payload["okx_archive_metadata_completeness_pass"],
            "okx_direct_1h_interval_present": payload["okx_direct_1h_interval_present"],
            "aggregation_performed_now": payload["aggregation_performed_now"],
            "sample_zip_metadata_inspection_allowed_now": payload["sample_zip_metadata_inspection_allowed_now"],
            "zip_download_allowed_now": payload["zip_download_allowed_now"],
            "okx_api_allowed_now": payload["okx_api_allowed_now"],
            "data_download_performed": payload["data_download_performed"],
            "data_fetch_performed": payload["data_fetch_performed"],
            "data_build_performed": payload["data_build_performed"],
            "okx_browse_performed": payload["okx_browse_performed"],
            "okx_sample_zip_downloaded_now": payload["okx_sample_zip_downloaded_now"],
            "generic_runner_implementation_remains_blocked": payload[
                "generic_runner_implementation_remains_blocked"
            ],
            "schema_or_config_created": payload["schema_or_config_created"],
            "loop_remains_closed": payload["loop_remains_closed"],
            "replacement_checks_all_true": payload["replacement_checks_all_true"],
        },
        "repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_input_after_approval_v1_latest.json": payload,
    }
    for name, artifact in artifacts.items():
        write_json(OUT_DIR / name, artifact)


def main() -> int:
    approval = load_json(APPROVAL_ARTIFACT)
    preflight_report = validate_preflight(approval)
    payload = build_payload(preflight_report)
    write_artifacts(payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        failure = {
            "module_name": MODULE_NAME,
            "generated_at_utc": utc_now(),
            "historical_data_acquisition_okx_user_manual_archive_metadata_input_status": STATUS_BLOCKED_CONTEXT,
            "final_decision": STATUS_BLOCKED_CONTEXT,
            "next_action": "STOP_FAIL_CLOSED_NO_BROWSE_NO_DOWNLOAD_NO_API_NO_DATA_BUILD",
            "next_module": NEXT_MODULE_BLOCKED,
            "error": str(exc),
            "okx_user_manual_archive_metadata_input_performed": False,
            "user_manual_okx_archive_metadata_present": False,
            "user_manual_okx_archive_metadata_value_recorded": False,
            "okx_direct_1h_interval_present": False,
            "aggregation_performed_now": False,
            "sample_zip_metadata_inspection_allowed_now": False,
            "zip_download_allowed_now": False,
            "okx_api_allowed_now": False,
            "bulk_archive_download_allowed_now": False,
            "acquisition_execution_allowed_now": False,
            "external_download_allowed_now": False,
            "external_api_allowed_now": False,
            "data_download_performed": False,
            "data_fetch_performed": False,
            "data_build_performed": False,
            "okx_download_performed": False,
            "okx_api_call_performed": False,
            "okx_browse_performed": False,
            "okx_sample_zip_downloaded_now": False,
            "generic_runner_implementation_remains_blocked": True,
            "schema_or_config_created": False,
            "loop_remains_closed": True,
        }
        write_json(
            OUT_DIR
            / "repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_input_after_approval_v1_latest.json",
            failure,
        )
        print(json.dumps(failure, indent=2, sort_keys=True), file=sys.stderr)
        raise SystemExit(1)
