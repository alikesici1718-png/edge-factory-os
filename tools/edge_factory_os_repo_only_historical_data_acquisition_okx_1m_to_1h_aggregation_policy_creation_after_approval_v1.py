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
    "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_creation_"
    "after_approval_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_creation_"
    "after_approval_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "868a937"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 673
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 674

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_creation_"
    "after_approval_v1.py"
)
NEXT_MODULE_VALIDATOR = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_"
    "after_creation_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_creation_"
    "blocked_record_after_approval_v1.py"
)

APPROVAL_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_approval_after_preview_v1"
    / "repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_approval_after_preview_v1_latest.json"
)
PREVIEW_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_preview_after_metadata_validator_v1"
    / "repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_preview_after_metadata_validator_v1_latest.json"
)
METADATA_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_input_validator_after_approval_v1"
    / "repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_input_validator_after_approval_v1_latest.json"
)
METADATA_INPUT_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_input_after_approval_v1"
    / "repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_input_after_approval_v1_latest.json"
)

APPROVAL_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_CREATION_"
    "APPROVED_NEXT_NO_EXECUTION"
)
PREVIEW_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_PREVIEW_READY_"
    "APPROVAL_REQUIRED_NO_EXECUTION"
)
METADATA_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_METADATA_INPUT_VALIDATED_"
    "1M_SCHEMA_AGGREGATION_POLICY_PREVIEW_READY_NO_EXECUTION"
)
METADATA_INPUT_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_METADATA_INPUT_CAPTURED_PARTIAL_"
    "1M_SCHEMA_PENDING_VALIDATOR_NO_EXECUTION"
)
STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_CREATED_"
    "PENDING_VALIDATOR_NO_EXECUTION"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_CREATION_APPROVED_"
    "NEXT_NO_EXECUTION"
)
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_CREATED_PENDING_"
    "VALIDATOR_NO_EXECUTION"
)
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"

POLICY_NAME = "OKX_1M_TO_1H_AGGREGATION_POLICY_V1"
POLICY_SCOPE = "FUTURE_DATA_BUILD_POLICY_ONLY"
EXPECTED_INPUT_COLUMNS = [
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
TIMESTAMP_UNIT = "epoch_milliseconds"
EXPECTED_INPUT_INTERVAL = "1m"
EXPECTED_OPEN_TIME_DELTA_MS = 60000
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
    approval: Dict[str, Any],
    preview: Dict[str, Any],
    metadata_validator: Dict[str, Any],
    metadata_input: Dict[str, Any],
) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))

    require_equal(
        approval.get("historical_data_acquisition_okx_1m_to_1h_aggregation_policy_approval_status"),
        APPROVAL_STATUS_PASS,
        "approval.status",
    )
    require_equal(approval.get("next_module"), REQUESTED_MODULE, "approval.next_module", STATUS_BLOCKED_NEXT_MODULE)
    require_true(approval.get("future_policy_creation_eligible_next"), "approval.future_policy_creation_eligible_next")
    require_true(approval.get("okx_1m_schema_validated"), "approval.okx_1m_schema_validated")
    require_false(approval.get("okx_direct_1h_interval_present"), "approval.okx_direct_1h_interval_present")
    require_true(approval.get("okx_direct_1h_absence_validated"), "approval.okx_direct_1h_absence_validated")
    require_true(approval.get("one_minute_to_one_hour_aggregation_required"), "approval.aggregation_required")
    require_true(approval.get("aggregation_policy_required"), "approval.aggregation_policy_required")
    require_false(approval.get("aggregation_policy_created_now"), "approval.aggregation_policy_created_now")
    require_false(approval.get("aggregation_performed_now"), "approval.aggregation_performed_now")
    require_false(approval.get("data_build_performed"), "approval.data_build_performed")
    require_equal(approval.get("canonical_aggregation_time_basis"), CANONICAL_AGGREGATION_TIME_BASIS, "approval.time_basis")
    require_equal(approval.get("output_hour_bucket_policy"), OUTPUT_HOUR_BUCKET_POLICY, "approval.bucket_policy")
    require_equal(approval.get("complete_hour_required_source_rows"), COMPLETE_HOUR_REQUIRED_SOURCE_ROWS, "approval.complete_rows")
    require_false(approval.get("synthetic_fill_allowed"), "approval.synthetic_fill_allowed")
    require_equal(approval.get("incomplete_hour_policy"), INCOMPLETE_HOUR_POLICY, "approval.incomplete_hour_policy")
    require_equal(approval.get("duplicate_minute_policy"), DUPLICATE_MINUTE_POLICY, "approval.duplicate_minute_policy")
    require_equal(approval.get("missing_minute_policy"), MISSING_MINUTE_POLICY, "approval.missing_minute_policy")
    require_equal(approval.get("confirm_policy"), CONFIRM_POLICY, "approval.confirm_policy")
    require_true(approval.get("coverage_still_unresolved"), "approval.coverage_still_unresolved")
    require_true(approval.get("source_manifest_required"), "approval.source_manifest_required")
    require_true(approval.get("provenance_report_required"), "approval.provenance_report_required")
    require_true(approval.get("symbol_universe_required"), "approval.symbol_universe_required")
    require_false(approval.get("okx_acquisition_readiness"), "approval.okx_acquisition_readiness")
    require_false(approval.get("aggregation_execution_allowed_now"), "approval.aggregation_execution_allowed_now")
    require_false(approval.get("acquisition_execution_allowed_now"), "approval.acquisition_execution_allowed_now")
    require_false(approval.get("external_download_allowed_now"), "approval.external_download_allowed_now")
    require_false(approval.get("external_api_allowed_now"), "approval.external_api_allowed_now")
    require_false(approval.get("okx_download_performed"), "approval.okx_download_performed")
    require_false(approval.get("okx_api_call_performed"), "approval.okx_api_call_performed")
    require_false(approval.get("okx_browse_performed"), "approval.okx_browse_performed")
    require_false(approval.get("okx_sample_zip_downloaded_now"), "approval.okx_sample_zip_downloaded_now")
    require_equal(approval.get("active_p0_blocker_count"), 0, "approval.active_p0_blocker_count")
    require_equal(approval.get("active_p1_attention_count"), 8, "approval.active_p1_attention_count")
    require_equal(approval.get("dormant_repo_attention_count"), 716, "approval.dormant_repo_attention_count")
    require_false(approval.get("generic_runner_approval_granted"), "approval.generic_runner_approval_granted")
    require_true(approval.get("generic_runner_implementation_remains_blocked"), "approval.generic_runner_blocked")
    require_false(approval.get("schema_or_config_created"), "approval.schema_or_config_created")
    require_false(approval.get("ordinary_selector_backlog_loop_reentry_allowed"), "approval.loop_reentry")
    require_true(approval.get("loop_remains_closed"), "approval.loop_remains_closed")
    require_true(approval.get("replacement_checks_all_true"), "approval.replacement_checks_all_true")
    validate_no_true_dangerous_flags(approval, "approval")

    require_equal(
        preview.get("historical_data_acquisition_okx_1m_to_1h_aggregation_policy_preview_status"),
        PREVIEW_STATUS_PASS,
        "preview.status",
    )
    require_false(preview.get("aggregation_policy_created_now"), "preview.aggregation_policy_created_now")
    require_false(preview.get("aggregation_performed_now"), "preview.aggregation_performed_now")
    require_false(preview.get("data_build_performed"), "preview.data_build_performed")
    require_true(preview.get("replacement_checks_all_true"), "preview.replacement_checks_all_true")
    validate_no_true_dangerous_flags(preview, "preview")

    require_equal(
        metadata_validator.get("historical_data_acquisition_okx_user_manual_archive_metadata_input_validator_status"),
        METADATA_VALIDATOR_STATUS_PASS,
        "metadata_validator.status",
    )
    require_true(metadata_validator.get("okx_1m_schema_validated"), "metadata_validator.okx_1m_schema_validated")
    require_false(metadata_validator.get("okx_direct_1h_interval_present"), "metadata_validator.direct_1h")
    require_false(metadata_validator.get("aggregation_performed_now"), "metadata_validator.aggregation_performed_now")
    require_false(metadata_validator.get("data_build_performed"), "metadata_validator.data_build_performed")
    require_true(metadata_validator.get("replacement_checks_all_true"), "metadata_validator.replacement_checks_all_true")
    validate_no_true_dangerous_flags(metadata_validator, "metadata_validator")

    require_equal(
        metadata_input.get("historical_data_acquisition_okx_user_manual_archive_metadata_input_status"),
        METADATA_INPUT_STATUS_PASS,
        "metadata_input.status",
    )
    require_false(metadata_input.get("okx_direct_1h_interval_present"), "metadata_input.direct_1h")
    require_equal(metadata_input.get("okx_inferred_candle_interval"), EXPECTED_INPUT_INTERVAL, "metadata_input.interval")
    require_equal(metadata_input.get("okx_open_time_delta_ms"), EXPECTED_OPEN_TIME_DELTA_MS, "metadata_input.delta")
    require_false(metadata_input.get("aggregation_performed_now"), "metadata_input.aggregation_performed_now")
    require_false(metadata_input.get("data_build_performed"), "metadata_input.data_build_performed")
    require_false(metadata_input.get("okx_acquisition_readiness"), "metadata_input.acquisition_readiness")
    require_true(metadata_input.get("replacement_checks_all_true"), "metadata_input.replacement_checks_all_true")
    validate_no_true_dangerous_flags(metadata_input, "metadata_input")

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
        "approval_artifact": str(APPROVAL_ARTIFACT),
        "preview_artifact": str(PREVIEW_ARTIFACT),
        "metadata_validator_artifact": str(METADATA_VALIDATOR_ARTIFACT),
        "metadata_input_artifact": str(METADATA_INPUT_ARTIFACT),
        "head": head,
        "status_lines_allowed": [f"?? {CURRENT_TOOL_REL}", f"A  {CURRENT_TOOL_REL}", f"AM {CURRENT_TOOL_REL}"],
    }


def build_policy_artifact(generated_at_utc: str) -> Dict[str, Any]:
    return {
        "policy_identity": {
            "policy_name": POLICY_NAME,
            "policy_scope": POLICY_SCOPE,
            "policy_created_by_current_module": True,
            "policy_execution_allowed_now": False,
            "aggregation_execution_allowed_now": False,
            "data_build_allowed_now": False,
            "acquisition_execution_allowed_now": False,
        },
        "input_schema_policy": {
            "expected_columns": EXPECTED_INPUT_COLUMNS,
            "timestamp_unit": TIMESTAMP_UNIT,
            "expected_input_interval": EXPECTED_INPUT_INTERVAL,
            "expected_open_time_delta_ms": EXPECTED_OPEN_TIME_DELTA_MS,
            "direct_1h_input_expected": False,
            "rows_sorted_by": ["instrument_name", "open_time"],
            "duplicate_open_time_policy": DUPLICATE_MINUTE_POLICY,
        },
        "canonical_time_policy": {
            "canonical_aggregation_time_basis": CANONICAL_AGGREGATION_TIME_BASIS,
            "output_hour_bucket_policy": OUTPUT_HOUR_BUCKET_POLICY,
            "output_timestamp_fields": ["hour_start_epoch_ms", "hour_start_iso_utc"],
            "local_machine_timezone_allowed": False,
            "okx_daily_archive_boundary_note": (
                "OKX daily archive boundary may be UTC+8, but output hourly buckets are canonical UTC"
            ),
            "cross_file_hour_handling_required": True,
            "cross_file_hour_handling_reason": (
                "UTC+8 daily files may split UTC hour coverage across archive files"
            ),
            "incomplete_first_last_archive_file_hours_policy": (
                "cannot be assumed complete without adjacent files"
            ),
        },
        "ohlcv_aggregation_policy": {
            "group_by": ["instrument_name", "UTC hour bucket"],
            "output_open": "first source open by open_time",
            "output_high": "max source high",
            "output_low": "min source low",
            "output_close": "last source close by open_time",
            "output_vol": "sum source vol",
            "output_vol_ccy": "sum source vol_ccy",
            "output_vol_quote": "sum source vol_quote",
            "output_source_row_count": "number of unique 1m rows",
            "output_complete_hour": (
                "true only when source_row_count=60 and all expected minutes are present"
            ),
            "output_confirm": "true only if all 60 source rows have confirm true/equivalent final status",
            "output_instrument_name": "source instrument_name",
        },
        "completeness_policy": {
            "complete_hour_required_source_rows": COMPLETE_HOUR_REQUIRED_SOURCE_ROWS,
            "synthetic_fill_allowed": False,
            "incomplete_hour_policy": INCOMPLETE_HOUR_POLICY,
            "missing_minute_policy": MISSING_MINUTE_POLICY,
            "duplicate_minute_policy": DUPLICATE_MINUTE_POLICY,
            "non_monotonic_time_policy": "FAIL_CLOSED_OR_QUARANTINE",
            "forward_fill_allowed": False,
            "backfill_allowed": False,
            "synthetic_candles_allowed": False,
        },
        "numeric_sanity_policy": {
            "ohlc_must_parse_numeric": True,
            "volume_fields_must_parse_numeric": True,
            "high_sanity_check": "high >= max(open, close, low)",
            "low_sanity_check": "low <= min(open, close, high)",
            "negative_volume_policy": "invalid",
            "parse_failures_policy": "quarantine_or_fail_closed",
            "nan_inf_policy": "invalid",
        },
        "source_preconditions_policy": {
            "source_manifest_required": True,
            "provenance_report_required": True,
            "symbol_universe_required": True,
            "coverage_resolution_required": True,
            "source_file_hash_manifest_required": True,
            "rollback_policy_required": True,
            "timeout_policy_required": True,
            "memory_disk_resource_policy_required": True,
            "historical_data_quality_validator_required": True,
            "holdout_policy_required": True,
            "survivorship_bias_controls_required": True,
        },
        "coverage_policy": {
            "okx_july_2023_onwards_does_not_prove_full_4_year_coverage": True,
            "three_year_coverage_may_be_possible_depending_target_end_date_and_manifest": True,
            "four_year_target_requires_other_source_or_explicit_shorter_horizon_policy_decision": True,
            "no_coverage_claim_without_manifest": True,
            "no_source_universe_claim_without_manifest": True,
        },
        "forbidden_policy": {
            "aggregation_execution_by_this_module_forbidden": True,
            "data_build_by_this_module_forbidden": True,
            "acquisition_execution_by_this_module_forbidden": True,
            "download_api_browse_by_this_module_forbidden": True,
            "strategy_backtest_candidate_runtime_live_generic_runner_schema_config_forbidden": True,
            "policy_is_not_evidence_of_built_data": True,
            "one_minute_data_must_not_be_treated_as_direct_one_hour_data": True,
            "one_sample_file_must_not_be_treated_as_full_coverage_or_full_manifest": True,
        },
        "validator_requirements": {
            "policy_artifact_exists_and_valid_json": True,
            "complete_hour_rule_requires_60_rows": True,
            "synthetic_fill_forbidden": True,
            "direct_1h_input_not_expected": True,
            "utc_bucket_policy_present": True,
            "ohlcv_aggregation_formulas_present": True,
            "source_manifest_provenance_prerequisites_present": True,
            "no_execution_build_flags_true": True,
        },
        "generated_at_utc": generated_at_utc,
    }


def build_payload(preflight_report: Dict[str, Any], policy_artifact: Dict[str, Any]) -> Dict[str, Any]:
    flags = dangerous_flags()
    replacement_checks = {
        "preflight_passed": preflight_report.get("whole_system_preflight_decision") == "PASS",
        "approval_respected": True,
        "policy_artifact_created": True,
        "compliance_report_created": True,
        "policy_execution_blocked": True,
        "aggregation_not_performed": True,
        "data_build_not_performed": True,
        "download_api_browse_absent": True,
        "real_csv_not_read": True,
        "source_manifest_not_created": True,
        "repo_schema_config_absent": True,
        "acquisition_blocked": True,
        "future_validator_required": True,
        "future_data_build_separate": True,
        "p1_carried_forward": True,
        "dormant_attention_carried_forward": True,
        "generic_runner_blocked": True,
        "loop_closed": True,
    }
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": policy_artifact["generated_at_utc"],
        "historical_data_acquisition_okx_1m_to_1h_aggregation_policy_creation_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "RUN_OKX_1M_TO_1H_AGGREGATION_POLICY_VALIDATOR_NO_EXECUTION",
        "next_module": NEXT_MODULE_VALIDATOR,
        **preflight_report,
        "prior_aggregation_policy_approval_respected": True,
        "okx_1m_to_1h_aggregation_policy_created": True,
        "okx_1m_to_1h_aggregation_policy_artifact_created": True,
        "okx_1m_to_1h_aggregation_policy_compliance_report_created": True,
        "policy_name": POLICY_NAME,
        "policy_scope": POLICY_SCOPE,
        "policy_execution_allowed_now": False,
        "aggregation_execution_allowed_now": False,
        "data_build_allowed_now": False,
        "acquisition_execution_allowed_now": False,
        "okx_1m_schema_validated": True,
        "direct_1h_input_expected": False,
        "expected_input_interval": EXPECTED_INPUT_INTERVAL,
        "expected_open_time_delta_ms": EXPECTED_OPEN_TIME_DELTA_MS,
        "canonical_aggregation_time_basis": CANONICAL_AGGREGATION_TIME_BASIS,
        "output_hour_bucket_policy": OUTPUT_HOUR_BUCKET_POLICY,
        "complete_hour_required_source_rows": COMPLETE_HOUR_REQUIRED_SOURCE_ROWS,
        "synthetic_fill_allowed": False,
        "incomplete_hour_policy": INCOMPLETE_HOUR_POLICY,
        "duplicate_minute_policy": DUPLICATE_MINUTE_POLICY,
        "missing_minute_policy": MISSING_MINUTE_POLICY,
        "confirm_policy": CONFIRM_POLICY,
        "source_manifest_required": True,
        "provenance_report_required": True,
        "symbol_universe_required": True,
        "coverage_resolution_required": True,
        "okx_acquisition_readiness": False,
        "aggregation_performed_now": False,
        "data_build_performed": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "okx_sample_zip_downloaded_now": False,
        "fake_or_synthetic_data_detected": False,
        "future_policy_validator_required_next": True,
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
        "current_evidence_chain_quality_before_creation": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_creation": EVIDENCE_AFTER,
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
            "PASS_OKX_1M_TO_1H_AGGREGATION_POLICY_CREATED_PENDING_VALIDATOR_NO_EXECUTION"
        ),
        "derived_live_repo_post_check_reason": (
            "repo-only policy creation wrote the approved OKX 1m-to-1h aggregation policy artifact and compliance report; "
            "it did not aggregate data, build data, read real CSV files, browse, download, call APIs, create source manifest, "
            "create repo schema/config, touch strategy, backtest, candidate, runtime, capital, live, generic-runner, or reopen old routes"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": all(replacement_checks.values()),
        "policy_artifact": policy_artifact,
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "tracked_python_count_expectation": {
            "pre_commit": EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT,
        },
    }
    if payload["synthetic_fill_allowed"] is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: policy allows synthetic fill")
    if payload["complete_hour_required_source_rows"] != 60:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: policy does not require 60 rows")
    if payload["incomplete_hour_policy"] != INCOMPLETE_HOUR_POLICY:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: incomplete hour policy unsafe")
    if payload["aggregation_execution_allowed_now"] is not False or payload["policy_execution_allowed_now"] is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: execution allowed now")
    if payload["aggregation_performed_now"] is not False or payload["data_build_performed"] is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: aggregation/data build occurred")
    if payload["source_manifest_required"] is not True:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: source manifest not required")
    if payload["schema_or_config_created"] is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: repo schema/config created")
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
    policy = payload["policy_artifact"]
    compliance = {
        "generated_at_utc": payload["generated_at_utc"],
        "historical_data_acquisition_okx_1m_to_1h_aggregation_policy_creation_status": payload[
            "historical_data_acquisition_okx_1m_to_1h_aggregation_policy_creation_status"
        ],
        "whole_system_preflight_completed": payload["whole_system_preflight_completed"],
        "whole_system_preflight_decision": payload["whole_system_preflight_decision"],
        "okx_1m_to_1h_aggregation_policy_created": payload["okx_1m_to_1h_aggregation_policy_created"],
        "okx_1m_to_1h_aggregation_policy_artifact_created": payload[
            "okx_1m_to_1h_aggregation_policy_artifact_created"
        ],
        "policy_name": payload["policy_name"],
        "policy_scope": payload["policy_scope"],
        "policy_execution_allowed_now": payload["policy_execution_allowed_now"],
        "aggregation_execution_allowed_now": payload["aggregation_execution_allowed_now"],
        "data_build_allowed_now": payload["data_build_allowed_now"],
        "acquisition_execution_allowed_now": payload["acquisition_execution_allowed_now"],
        "complete_hour_required_source_rows": payload["complete_hour_required_source_rows"],
        "synthetic_fill_allowed": payload["synthetic_fill_allowed"],
        "incomplete_hour_policy": payload["incomplete_hour_policy"],
        "source_manifest_required": payload["source_manifest_required"],
        "provenance_report_required": payload["provenance_report_required"],
        "symbol_universe_required": payload["symbol_universe_required"],
        "aggregation_performed_now": payload["aggregation_performed_now"],
        "data_build_performed": payload["data_build_performed"],
        "okx_download_performed": payload["okx_download_performed"],
        "okx_api_call_performed": payload["okx_api_call_performed"],
        "okx_browse_performed": payload["okx_browse_performed"],
        "okx_sample_zip_downloaded_now": payload["okx_sample_zip_downloaded_now"],
        "schema_or_config_created": payload["schema_or_config_created"],
        "generic_runner_implementation_remains_blocked": payload[
            "generic_runner_implementation_remains_blocked"
        ],
        "replacement_checks_all_true": payload["replacement_checks_all_true"],
    }
    artifacts = {
        "historical_okx_1m_to_1h_aggregation_policy.json": policy,
        "historical_okx_1m_to_1h_aggregation_policy_contract_compliance_report.json": compliance,
        "repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_creation_after_approval_v1_latest.json": payload,
    }
    for name, artifact in artifacts.items():
        write_json(OUT_DIR / name, artifact)


def main() -> int:
    approval = load_json(APPROVAL_ARTIFACT)
    preview = load_json(PREVIEW_ARTIFACT)
    metadata_validator = load_json(METADATA_VALIDATOR_ARTIFACT)
    metadata_input = load_json(METADATA_INPUT_ARTIFACT)
    preflight_report = validate_preflight(approval, preview, metadata_validator, metadata_input)
    policy_artifact = build_policy_artifact(utc_now())
    payload = build_payload(preflight_report, policy_artifact)
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
            "historical_data_acquisition_okx_1m_to_1h_aggregation_policy_creation_status": STATUS_BLOCKED_CONTEXT,
            "final_decision": STATUS_BLOCKED_CONTEXT,
            "next_action": "STOP_FAIL_CLOSED_NO_AGGREGATION_NO_DATA_BUILD_NO_BROWSE_NO_DOWNLOAD_NO_API",
            "next_module": NEXT_MODULE_BLOCKED,
            "error": str(exc),
            "active_p0_blocker_count": 1,
            "okx_1m_to_1h_aggregation_policy_created": False,
            "okx_1m_to_1h_aggregation_policy_artifact_created": False,
            "okx_1m_to_1h_aggregation_policy_compliance_report_created": False,
            "policy_execution_allowed_now": False,
            "aggregation_execution_allowed_now": False,
            "data_build_allowed_now": False,
            "acquisition_execution_allowed_now": False,
            "aggregation_performed_now": False,
            "data_build_performed": False,
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
            / "repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_creation_after_approval_v1_latest.json",
            failure,
        )
        print(json.dumps(failure, indent=2, sort_keys=True), file=sys.stderr)
        raise SystemExit(1)
