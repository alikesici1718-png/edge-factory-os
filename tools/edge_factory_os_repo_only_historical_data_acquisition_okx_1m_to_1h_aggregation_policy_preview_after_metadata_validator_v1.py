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
    "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_preview_"
    "after_metadata_validator_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_preview_"
    "after_metadata_validator_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "959eb5e"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 671
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 672

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_preview_"
    "after_metadata_validator_v1.py"
)
NEXT_MODULE_APPROVAL = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_approval_"
    "after_preview_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_preview_"
    "blocked_record_after_metadata_validator_v1.py"
)

VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_input_validator_after_approval_v1"
    / "repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_input_validator_after_approval_v1_latest.json"
)
METADATA_INPUT_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_input_after_approval_v1"
    / "repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_input_after_approval_v1_latest.json"
)
APPROVAL_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_archive_scope_resolution_approval_after_preview_v1"
    / "repo_only_historical_data_acquisition_okx_archive_scope_resolution_approval_after_preview_v1_latest.json"
)
PREVIEW_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_archive_scope_resolution_preview_after_browse_lookup_validator_v1"
    / "repo_only_historical_data_acquisition_okx_archive_scope_resolution_preview_after_browse_lookup_validator_v1_latest.json"
)
BROWSE_LOOKUP_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_validator_after_approval_v1"
    / "repo_only_historical_data_acquisition_browse_only_source_identity_lookup_validator_after_approval_v1_latest.json"
)

VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_METADATA_INPUT_VALIDATED_"
    "1M_SCHEMA_AGGREGATION_POLICY_PREVIEW_READY_NO_EXECUTION"
)
METADATA_INPUT_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_METADATA_INPUT_CAPTURED_PARTIAL_"
    "1M_SCHEMA_PENDING_VALIDATOR_NO_EXECUTION"
)
APPROVAL_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_SCOPE_RESOLUTION_APPROVED_"
    "USER_MANUAL_METADATA_INPUT_NEXT_NO_EXECUTION"
)
PREVIEW_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_SCOPE_RESOLUTION_PREVIEW_READY_"
    "APPROVAL_REQUIRED_NO_EXECUTION"
)
BROWSE_LOOKUP_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_VALIDATED_PARTIAL_"
    "OKX_IDENTITY_ARCHIVE_SCOPE_RESOLUTION_PREVIEW_READY_NO_EXECUTION"
)
STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_PREVIEW_READY_"
    "APPROVAL_REQUIRED_NO_EXECUTION"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_METADATA_INPUT_VALIDATED_"
    "1M_SCHEMA_AGGREGATION_POLICY_PREVIEW_READY_NO_EXECUTION"
)
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_PREVIEW_READY_"
    "APPROVAL_REQUIRED_NO_EXECUTION"
)
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"

EXPECTED_CSV_COLUMNS = [
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
EXPECTED_OPEN_TIME_DELTA_MS = 60000
EXPECTED_INFERRED_INTERVAL = "1m"
EXPECTED_TIMESTAMP_UNIT = "epoch_milliseconds"
EXPECTED_BOUNDARY = "LIKELY_UTC_PLUS_8_EXCHANGE_DAY"

CANONICAL_AGGREGATION_TIME_BASIS = "UTC_HOURLY_BUCKETS_FROM_OPEN_TIME_EPOCH_MS"
OUTPUT_HOUR_BUCKET_POLICY = "FLOOR_OPEN_TIME_TO_UTC_HOUR"
INCOMPLETE_HOUR_POLICY = "EXCLUDE_OR_FLAG_NEVER_FILL"
DUPLICATE_MINUTE_POLICY = "FAIL_CLOSED_OR_QUARANTINE_UNLESS_LATER_DEDUP_POLICY_APPROVED"
MISSING_MINUTE_POLICY = "INCOMPLETE_HOUR_FAIL_CLOSED_OR_FLAGGED"
CONFIRM_POLICY = "OUTPUT_CONFIRM_TRUE_ONLY_IF_ALL_SOURCE_ROWS_CONFIRMED"
COMPLETE_HOUR_REQUIRED_SOURCE_ROWS = 60

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
    "okx_page_reopened_now",
    "okx_archive_scope_resolution_performed_now",
    "aggregation_policy_created_now",
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


def validate_preflight(
    validator: Dict[str, Any],
    metadata_input: Dict[str, Any],
    approval: Dict[str, Any],
    preview: Dict[str, Any],
    browse_validator: Dict[str, Any],
) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))

    require_equal(
        validator.get("historical_data_acquisition_okx_user_manual_archive_metadata_input_validator_status"),
        VALIDATOR_STATUS_PASS,
        "validator.status",
    )
    require_equal(validator.get("next_module"), REQUESTED_MODULE, "validator.next_module", STATUS_BLOCKED_NEXT_MODULE)
    require_equal(validator.get("current_evidence_chain_quality_after_validator"), EVIDENCE_BEFORE, "validator.evidence_after")
    require_true(validator.get("okx_1m_schema_validated"), "validator.okx_1m_schema_validated")
    require_false(validator.get("okx_direct_1h_interval_present"), "validator.okx_direct_1h_interval_present")
    require_true(validator.get("okx_direct_1h_absence_validated"), "validator.okx_direct_1h_absence_validated")
    require_true(validator.get("one_minute_to_one_hour_aggregation_required"), "validator.aggregation_required")
    require_true(
        validator.get("okx_1m_to_1h_aggregation_requirement_validated"),
        "validator.aggregation_requirement_validated",
    )
    require_true(validator.get("future_data_build_aggregation_required"), "validator.future_data_build_aggregation_required")
    require_false(validator.get("aggregation_performed_now"), "validator.aggregation_performed_now")
    require_equal(validator.get("okx_open_time_delta_ms"), EXPECTED_OPEN_TIME_DELTA_MS, "validator.open_time_delta_ms")
    require_equal(validator.get("okx_inferred_candle_interval"), EXPECTED_INFERRED_INTERVAL, "validator.interval")
    require_equal(validator.get("okx_timestamp_unit"), EXPECTED_TIMESTAMP_UNIT, "validator.timestamp_unit")
    require_equal(validator.get("okx_daily_boundary_interpretation"), EXPECTED_BOUNDARY, "validator.boundary")
    require_false(validator.get("okx_acquisition_readiness"), "validator.acquisition_readiness")
    require_false(validator.get("acquisition_execution_allowed_now"), "validator.acquisition_execution_allowed_now")
    require_false(validator.get("data_download_performed"), "validator.data_download_performed")
    require_false(validator.get("data_fetch_performed"), "validator.data_fetch_performed")
    require_false(validator.get("data_build_performed"), "validator.data_build_performed")
    require_false(validator.get("okx_download_performed"), "validator.okx_download_performed")
    require_false(validator.get("okx_api_call_performed"), "validator.okx_api_call_performed")
    require_false(validator.get("okx_browse_performed"), "validator.okx_browse_performed")
    require_false(validator.get("okx_sample_zip_downloaded_now"), "validator.okx_sample_zip_downloaded_now")
    require_equal(validator.get("active_p0_blocker_count"), 0, "validator.active_p0_blocker_count")
    require_equal(validator.get("active_p1_attention_count"), 8, "validator.active_p1_attention_count")
    require_equal(validator.get("dormant_repo_attention_count"), 716, "validator.dormant_repo_attention_count")
    require_false(validator.get("generic_runner_approval_granted"), "validator.generic_runner_approval_granted")
    require_true(validator.get("generic_runner_implementation_remains_blocked"), "validator.generic_runner_blocked")
    require_false(validator.get("schema_or_config_created"), "validator.schema_or_config_created")
    require_false(validator.get("ordinary_selector_backlog_loop_reentry_allowed"), "validator.loop_reentry")
    require_true(validator.get("loop_remains_closed"), "validator.loop_remains_closed")
    require_true(validator.get("replacement_checks_all_true"), "validator.replacement_checks_all_true")
    validate_no_true_dangerous_flags(validator, "validator")

    require_equal(
        metadata_input.get("historical_data_acquisition_okx_user_manual_archive_metadata_input_status"),
        METADATA_INPUT_STATUS_PASS,
        "metadata_input.status",
    )
    require_equal(metadata_input.get("okx_csv_columns"), EXPECTED_CSV_COLUMNS, "metadata_input.csv_columns")
    require_equal(metadata_input.get("okx_open_time_delta_ms"), EXPECTED_OPEN_TIME_DELTA_MS, "metadata_input.open_time_delta_ms")
    require_equal(metadata_input.get("okx_inferred_candle_interval"), EXPECTED_INFERRED_INTERVAL, "metadata_input.interval")
    require_false(metadata_input.get("okx_direct_1h_interval_present"), "metadata_input.direct_1h")
    require_false(metadata_input.get("aggregation_performed_now"), "metadata_input.aggregation_performed_now")
    require_false(metadata_input.get("data_build_performed"), "metadata_input.data_build_performed")
    require_false(metadata_input.get("okx_acquisition_readiness"), "metadata_input.acquisition_readiness")
    require_true(metadata_input.get("replacement_checks_all_true"), "metadata_input.replacement_checks_all_true")
    validate_no_true_dangerous_flags(metadata_input, "metadata_input")

    require_equal(
        approval.get("historical_data_acquisition_okx_archive_scope_resolution_approval_status"),
        APPROVAL_STATUS_PASS,
        "approval.status",
    )
    require_true(approval.get("replacement_checks_all_true"), "approval.replacement_checks_all_true")
    validate_no_true_dangerous_flags(approval, "approval")

    require_equal(
        preview.get("historical_data_acquisition_okx_archive_scope_resolution_preview_status"),
        PREVIEW_STATUS_PASS,
        "preview.status",
    )
    require_true(preview.get("replacement_checks_all_true"), "preview.replacement_checks_all_true")
    validate_no_true_dangerous_flags(preview, "preview")

    require_equal(
        browse_validator.get("historical_data_acquisition_browse_only_source_identity_lookup_validator_status"),
        BROWSE_LOOKUP_VALIDATOR_STATUS_PASS,
        "browse_validator.status",
    )
    require_true(browse_validator.get("okx_source_identity_partially_verified_validated"), "browse_validator.partial_identity")
    require_false(browse_validator.get("okx_source_verified_for_acquisition_now"), "browse_validator.source_verified_now")
    require_false(browse_validator.get("okx_acquisition_readiness"), "browse_validator.acquisition_readiness")
    require_true(browse_validator.get("replacement_checks_all_true"), "browse_validator.replacement_checks_all_true")
    validate_no_true_dangerous_flags(browse_validator, "browse_validator")

    return {
        "whole_system_preflight_completed": True,
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
        "whole_system_preflight_decision": "PASS",
        "validator_artifact": str(VALIDATOR_ARTIFACT),
        "metadata_input_artifact": str(METADATA_INPUT_ARTIFACT),
        "approval_artifact": str(APPROVAL_ARTIFACT),
        "preview_artifact": str(PREVIEW_ARTIFACT),
        "browse_lookup_validator_artifact": str(BROWSE_LOOKUP_VALIDATOR_ARTIFACT),
        "head": head,
        "status_lines_allowed": [f"?? {CURRENT_TOOL_REL}", f"A  {CURRENT_TOOL_REL}", f"AM {CURRENT_TOOL_REL}"],
    }


def preview_sections() -> Dict[str, Any]:
    return {
        "validator_context": {
            "okx_metadata_validator_passed": True,
            "okx_1m_schema_validated": True,
            "okx_direct_1h_absence_validated": True,
            "one_minute_to_one_hour_aggregation_required": True,
            "future_data_build_aggregation_required": True,
            "aggregation_performed_now": False,
            "data_build_performed": False,
            "okx_acquisition_readiness": False,
            "active_p1_attention_count": 8,
            "dormant_repo_attention_count": 716,
        },
        "canonical_input_schema_policy": {
            "expected_1m_input_columns": EXPECTED_CSV_COLUMNS,
            "open_time_unit": EXPECTED_TIMESTAMP_UNIT,
            "direct_interval": EXPECTED_INFERRED_INTERVAL,
            "expected_open_time_delta_ms": EXPECTED_OPEN_TIME_DELTA_MS,
            "rows_must_be_sorted_by": ["instrument_name", "open_time"],
            "duplicate_open_time_per_instrument_policy": DUPLICATE_MINUTE_POLICY,
        },
        "hour_bucket_policy": {
            "canonical_aggregation_time_basis": CANONICAL_AGGREGATION_TIME_BASIS,
            "hour_bucket_start": "floor open_time UTC to hour",
            "output_1h_candle_timestamp": "hour bucket start in UTC epoch ms and ISO UTC",
            "daily_archive_boundary_note": (
                "OKX archive file daily boundary may be UTC+8, but aggregation buckets must use canonical UTC "
                "unless a future validator explicitly changes this"
            ),
            "cross_file_hours_policy": "future build must handle cross-file hours caused by UTC+8 daily file boundaries",
            "incomplete_file_edge_hour_policy": (
                "incomplete first/last hour of each downloaded file must not be assumed complete without adjacent files"
            ),
            "local_machine_timezone_allowed": False,
        },
        "ohlcv_aggregation_rules": {
            "group_by": ["instrument_name", "UTC hour bucket"],
            "open": "first 1m open by open_time",
            "high": "max 1m high",
            "low": "min 1m low",
            "close": "last 1m close by open_time",
            "vol": "sum 1m vol",
            "vol_ccy": "sum 1m vol_ccy",
            "vol_quote": "sum 1m vol_quote",
            "confirm": CONFIRM_POLICY,
            "instrument_name": "input instrument_name",
            "source_row_count": "count of 1m rows in bucket",
            "completeness_flag": "complete only when exactly 60 expected unique 1m rows exist",
        },
        "missing_data_policy": {
            "complete_1h_candle_requires_exactly_unique_minute_rows": COMPLETE_HOUR_REQUIRED_SOURCE_ROWS,
            "missing_minute_count_gt_zero_policy": "hour incomplete",
            "duplicate_minute_rows_policy": DUPLICATE_MINUTE_POLICY,
            "non_monotonic_open_time_within_instrument_policy": "fail validation",
            "open_time_delta_not_60000_policy": "trigger gap/duplicate detection",
            "incomplete_hours_policy": INCOMPLETE_HOUR_POLICY,
            "forward_fill_backfill_synthetic_candles_allowed": False,
            "fake_or_synthetic_data_treated_as_real_allowed": False,
        },
        "numeric_validation_policy": {
            "open_high_low_close_must_parse_as_numeric": True,
            "volume_fields_must_parse_as_numeric": True,
            "high_sanity_check": "high >= max(open, close, low) or equivalent OHLC sanity check",
            "low_sanity_check": "low <= min(open, close, high) or equivalent OHLC sanity check",
            "negative_volume_policy": "fail or flag row",
            "zero_volume_policy": "allowed only if source row is otherwise valid and policy allows",
            "parse_failure_policy": "fail closed or produce quarantine artifact",
        },
        "coverage_policy": {
            "okx_july_2023_onwards_does_not_prove_full_4_year_coverage": True,
            "three_year_coverage_may_be_possible_but_requires_source_manifest": True,
            "four_year_target_requires_other_source_or_explicit_shorter_horizon_policy": True,
            "source_manifest_required_before_acquisition_execution": True,
            "provenance_report_required_before_acquisition_execution": True,
            "symbol_universe_required_before_acquisition_execution": True,
        },
        "future_required_artifacts": [
            "historical_okx_1m_to_1h_aggregation_policy.json",
            "historical_okx_1m_to_1h_aggregation_policy_validator.json",
            "historical_okx_1m_to_1h_build_preview.json",
            "historical_okx_1m_to_1h_build_approval.json",
            "historical_okx_1m_to_1h_build_run_report.json",
            "historical_okx_1m_to_1h_build_validator.json",
            "historical_okx_1h_completeness_report.json",
            "historical_okx_1h_gap_duplicate_report.json",
            "historical_okx_1h_schema_report.json",
            "historical_okx_1h_provenance_report.json",
        ],
        "fail_closed_preview": [
            "input schema differs",
            "timestamp unit differs",
            "open_time is not 1m spaced",
            "duplicate minute rows exist",
            "missing minutes exist",
            "fewer than 60 unique rows in an output hour",
            "OHLC parse fails",
            "volume parse fails",
            "confirm policy fails",
            "source manifest absent",
            "provenance absent",
            "symbol universe absent",
            "coverage requirement unresolved",
            "aggregation tries to fill missing candles synthetically",
            "strategy/backtest/candidate/runtime/live path is touched",
        ],
        "evidence_policy_preview": {
            "before_preview": EVIDENCE_BEFORE,
            "after_preview": EVIDENCE_AFTER,
            "preview_is_not_aggregation": True,
            "preview_is_not_data_build": True,
            "preview_is_not_acquisition_execution": True,
            "preview_is_not_source_manifest": True,
            "preview_is_not_provenance_report": True,
            "p1_remains_active_until_acquisition_build_historical_validator_closes_it": True,
        },
        "next_module_decision": {
            "if_preview_is_safe": NEXT_MODULE_APPROVAL,
            "if_preview_is_unsafe": NEXT_MODULE_BLOCKED,
            "do_not_choose_aggregation_implementation_directly": True,
            "do_not_choose_data_build_directly": True,
            "do_not_choose_zip_download": True,
            "do_not_choose_api_download": True,
            "do_not_choose_acquisition_execution_apply": True,
            "do_not_choose_strategy_research": True,
            "do_not_choose_candidate_backtest_runtime_live_capital": True,
        },
    }


def build_payload(preflight_report: Dict[str, Any], sections: Dict[str, Any]) -> Dict[str, Any]:
    flags = dangerous_flags()
    replacement_checks = {
        "preflight_passed": preflight_report.get("whole_system_preflight_decision") == "PASS",
        "prior_validator_respected": True,
        "policy_preview_completed": True,
        "policy_preview_not_executable_policy": True,
        "aggregation_not_performed": True,
        "data_build_not_performed": True,
        "no_browse_download_fetch_api": True,
        "source_manifest_not_created": True,
        "schema_config_absent": True,
        "acquisition_blocked": True,
        "future_approval_required": True,
        "p1_carried_forward": True,
        "dormant_attention_carried_forward": True,
        "generic_runner_blocked": True,
        "loop_closed": True,
    }
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_1m_to_1h_aggregation_policy_preview_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "CREATE_OKX_1M_TO_1H_AGGREGATION_POLICY_APPROVAL_RECORD_NO_EXECUTION",
        "next_module": NEXT_MODULE_APPROVAL,
        **preflight_report,
        "prior_okx_metadata_validator_respected": True,
        "okx_1m_to_1h_aggregation_policy_preview_completed": True,
        "validator_context_completed": True,
        "canonical_input_schema_policy_completed": True,
        "hour_bucket_policy_completed": True,
        "ohlcv_aggregation_rules_completed": True,
        "missing_data_policy_completed": True,
        "numeric_validation_policy_completed": True,
        "coverage_policy_completed": True,
        "future_required_artifacts_completed": True,
        "fail_closed_preview_completed": True,
        "evidence_policy_preview_completed": True,
        "okx_1m_schema_validated": True,
        "okx_direct_1h_interval_present": False,
        "okx_direct_1h_absence_validated": True,
        "one_minute_to_one_hour_aggregation_required": True,
        "aggregation_policy_required": True,
        "aggregation_policy_created_now": False,
        "aggregation_performed_now": False,
        "data_build_performed": False,
        "okx_timestamp_unit": EXPECTED_TIMESTAMP_UNIT,
        "okx_open_time_delta_ms": EXPECTED_OPEN_TIME_DELTA_MS,
        "canonical_aggregation_time_basis": CANONICAL_AGGREGATION_TIME_BASIS,
        "output_hour_bucket_policy": OUTPUT_HOUR_BUCKET_POLICY,
        "complete_hour_required_source_rows": COMPLETE_HOUR_REQUIRED_SOURCE_ROWS,
        "synthetic_fill_allowed": False,
        "incomplete_hour_policy": INCOMPLETE_HOUR_POLICY,
        "duplicate_minute_policy": DUPLICATE_MINUTE_POLICY,
        "missing_minute_policy": MISSING_MINUTE_POLICY,
        "confirm_policy": CONFIRM_POLICY,
        "coverage_still_unresolved": True,
        "source_manifest_required": True,
        "provenance_report_required": True,
        "symbol_universe_required": True,
        "okx_acquisition_readiness": False,
        "aggregation_execution_allowed_now": False,
        "acquisition_execution_allowed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "okx_sample_zip_downloaded_now": False,
        "fake_or_synthetic_data_detected": False,
        "future_aggregation_policy_approval_required_next": True,
        "future_data_build_requires_separate_approval": True,
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
        "old_source_panel_anomaly_route_reopened_now": False,
        "current_evidence_chain_quality_before_preview": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_preview": EVIDENCE_AFTER,
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
        "derived_live_repo_post_check": (
            "PASS_OKX_1M_TO_1H_AGGREGATION_POLICY_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION"
        ),
        "derived_live_repo_post_check_reason": (
            "repo-only policy preview defined future OKX 1m-to-1h aggregation rules without creating an executable "
            "policy, aggregating data, building data, browsing, downloading, calling APIs, creating source manifest, "
            "creating schema/config, or touching strategy, backtest, candidate, runtime, capital, live, generic-runner, "
            "or old-route paths"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": all(replacement_checks.values()),
        "preview_sections": sections,
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "tracked_python_count_expectation": {
            "pre_commit": EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT,
        },
    }
    if payload["aggregation_policy_created_now"] is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: executable aggregation policy was created")
    if payload["aggregation_performed_now"] is not False or payload["data_build_performed"] is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: aggregation/data build occurred")
    if payload["okx_acquisition_readiness"] is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: acquisition readiness was overclaimed")
    if payload["active_p1_attention_count"] != 8 or payload["p1_attention_carried_forward"] is not True:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: active P1 attention was not carried forward")
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
    sections = payload["preview_sections"]
    artifacts = {
        "historical_okx_1m_to_1h_aggregation_policy_preview_report.json": payload,
        "historical_okx_1m_to_1h_canonical_input_schema_policy_preview.json": {
            "generated_at_utc": payload["generated_at_utc"],
            **sections["canonical_input_schema_policy"],
            "aggregation_policy_created_now": payload["aggregation_policy_created_now"],
        },
        "historical_okx_1m_to_1h_hour_bucket_policy_preview.json": {
            "generated_at_utc": payload["generated_at_utc"],
            **sections["hour_bucket_policy"],
            "canonical_aggregation_time_basis": payload["canonical_aggregation_time_basis"],
            "output_hour_bucket_policy": payload["output_hour_bucket_policy"],
        },
        "historical_okx_1m_to_1h_ohlcv_missing_numeric_policy_preview.json": {
            "generated_at_utc": payload["generated_at_utc"],
            "ohlcv_aggregation_rules": sections["ohlcv_aggregation_rules"],
            "missing_data_policy": sections["missing_data_policy"],
            "numeric_validation_policy": sections["numeric_validation_policy"],
        },
        "historical_okx_1m_to_1h_coverage_fail_closed_policy_preview.json": {
            "generated_at_utc": payload["generated_at_utc"],
            "coverage_policy": sections["coverage_policy"],
            "future_required_artifacts": sections["future_required_artifacts"],
            "fail_closed_preview": sections["fail_closed_preview"],
        },
        "historical_okx_1m_to_1h_aggregation_policy_preview_contract_compliance_report.json": {
            "generated_at_utc": payload["generated_at_utc"],
            "whole_system_preflight_completed": payload["whole_system_preflight_completed"],
            "whole_system_preflight_decision": payload["whole_system_preflight_decision"],
            "okx_1m_to_1h_aggregation_policy_preview_completed": payload[
                "okx_1m_to_1h_aggregation_policy_preview_completed"
            ],
            "aggregation_policy_created_now": payload["aggregation_policy_created_now"],
            "aggregation_performed_now": payload["aggregation_performed_now"],
            "data_build_performed": payload["data_build_performed"],
            "aggregation_execution_allowed_now": payload["aggregation_execution_allowed_now"],
            "acquisition_execution_allowed_now": payload["acquisition_execution_allowed_now"],
            "okx_download_performed": payload["okx_download_performed"],
            "okx_api_call_performed": payload["okx_api_call_performed"],
            "okx_browse_performed": payload["okx_browse_performed"],
            "okx_sample_zip_downloaded_now": payload["okx_sample_zip_downloaded_now"],
            "generic_runner_implementation_remains_blocked": payload[
                "generic_runner_implementation_remains_blocked"
            ],
            "schema_or_config_created": payload["schema_or_config_created"],
            "loop_remains_closed": payload["loop_remains_closed"],
            "replacement_checks_all_true": payload["replacement_checks_all_true"],
        },
        "repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_preview_after_metadata_validator_v1_latest.json": payload,
    }
    for name, artifact in artifacts.items():
        write_json(OUT_DIR / name, artifact)


def main() -> int:
    validator = load_json(VALIDATOR_ARTIFACT)
    metadata_input = load_json(METADATA_INPUT_ARTIFACT)
    approval = load_json(APPROVAL_ARTIFACT)
    preview = load_json(PREVIEW_ARTIFACT)
    browse_validator = load_json(BROWSE_LOOKUP_VALIDATOR_ARTIFACT)
    preflight_report = validate_preflight(validator, metadata_input, approval, preview, browse_validator)
    sections = preview_sections()
    payload = build_payload(preflight_report, sections)
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
            "historical_data_acquisition_okx_1m_to_1h_aggregation_policy_preview_status": STATUS_BLOCKED_CONTEXT,
            "final_decision": STATUS_BLOCKED_CONTEXT,
            "next_action": "STOP_FAIL_CLOSED_NO_AGGREGATION_NO_DATA_BUILD_NO_BROWSE_NO_DOWNLOAD_NO_API",
            "next_module": NEXT_MODULE_BLOCKED,
            "error": str(exc),
            "active_p0_blocker_count": 1,
            "aggregation_policy_created_now": False,
            "aggregation_performed_now": False,
            "data_build_performed": False,
            "aggregation_execution_allowed_now": False,
            "acquisition_execution_allowed_now": False,
            "external_download_allowed_now": False,
            "external_api_allowed_now": False,
            "okx_download_performed": False,
            "okx_api_call_performed": False,
            "okx_browse_performed": False,
            "okx_sample_zip_downloaded_now": False,
            "fake_or_synthetic_data_detected": False,
            "generic_runner_implementation_remains_blocked": True,
            "schema_or_config_created": False,
            "loop_remains_closed": True,
        }
        write_json(
            OUT_DIR
            / "repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_preview_after_metadata_validator_v1_latest.json",
            failure,
        )
        print(json.dumps(failure, indent=2, sort_keys=True), file=sys.stderr)
        raise SystemExit(1)
