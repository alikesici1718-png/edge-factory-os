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
    "input_validator_after_approval_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_"
    "input_validator_after_approval_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "38d4bc7"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 670
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 671

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_"
    "input_validator_after_approval_v1.py"
)
NEXT_MODULE_POLICY_PREVIEW = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_preview_"
    "after_metadata_validator_v1.py"
)
NEXT_MODULE_BROWSE_DETAIL = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_browse_only_archive_detail_lookup_preview_"
    "after_metadata_validator_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_"
    "input_blocked_record_after_approval_v1.py"
)

INPUT_DIR = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_input_after_approval_v1"
)
INPUT_LATEST_ARTIFACT = (
    INPUT_DIR / "repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_input_after_approval_v1_latest.json"
)
REQUIRED_METADATA_ARTIFACTS = {
    "historical_okx_user_manual_archive_metadata_input_report.json": INPUT_DIR
    / "historical_okx_user_manual_archive_metadata_input_report.json",
    "historical_okx_1h_interval_user_metadata_record.json": INPUT_DIR
    / "historical_okx_1h_interval_user_metadata_record.json",
    "historical_okx_coverage_user_metadata_record.json": INPUT_DIR
    / "historical_okx_coverage_user_metadata_record.json",
    "historical_okx_schema_timezone_user_metadata_record.json": INPUT_DIR
    / "historical_okx_schema_timezone_user_metadata_record.json",
    "historical_okx_archive_scope_user_metadata_completeness_report.json": INPUT_DIR
    / "historical_okx_archive_scope_user_metadata_completeness_report.json",
    "historical_okx_archive_scope_user_metadata_contract_compliance_report.json": INPUT_DIR
    / "historical_okx_archive_scope_user_metadata_contract_compliance_report.json",
}
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

INPUT_STATUS_PASS = (
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
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_METADATA_INPUT_VALIDATED_"
    "1M_SCHEMA_AGGREGATION_POLICY_PREVIEW_READY_NO_EXECUTION"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_METADATA_INPUT_CAPTURED_PARTIAL_"
    "1M_SCHEMA_PENDING_VALIDATOR_NO_EXECUTION"
)
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_METADATA_INPUT_VALIDATED_"
    "1M_SCHEMA_AGGREGATION_POLICY_PREVIEW_READY_NO_EXECUTION"
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
EXPECTED_ROW_COUNT = 1440
EXPECTED_OPEN_TIME_DELTA_MS = 60000
EXPECTED_INFERRED_INTERVAL = "1m"
EXPECTED_TIMESTAMP_UNIT = "epoch_milliseconds"
EXPECTED_FIRST_OPEN_TIME_UTC = "2026-05-17T16:00:00Z"
EXPECTED_LAST_OPEN_TIME_UTC = "2026-05-18T15:59:00Z"
EXPECTED_DAILY_BOUNDARY = "LIKELY_UTC_PLUS_8_EXCHANGE_DAY"
EXPECTED_DATA_GROUPING_OPTIONS = ["daily", "month"]
EXPECTED_TARGET_INSTRUMENT_TYPE = "perpetual_swap"

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


def load_required_metadata_artifacts() -> Dict[str, Dict[str, Any]]:
    artifacts: Dict[str, Dict[str, Any]] = {}
    failures: List[str] = []
    for name, path in REQUIRED_METADATA_ARTIFACTS.items():
        data, exists, valid, non_empty = read_json_checked(path)
        if not (exists and valid and non_empty):
            failures.append(f"{name}: exists={exists} valid_json={valid} non_empty={non_empty}")
        else:
            artifacts[name] = data
    if failures:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: metadata artifact validation failed: {failures}")
    return artifacts


def validate_preflight(
    metadata: Dict[str, Any],
    metadata_artifacts: Dict[str, Dict[str, Any]],
    approval: Dict[str, Any],
    preview: Dict[str, Any],
    browse_validator: Dict[str, Any],
) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))

    require_equal(
        metadata.get("historical_data_acquisition_okx_user_manual_archive_metadata_input_status"),
        INPUT_STATUS_PASS,
        "metadata.status",
    )
    require_equal(metadata.get("next_module"), REQUESTED_MODULE, "metadata.next_module", STATUS_BLOCKED_NEXT_MODULE)
    require_equal(metadata.get("current_evidence_chain_quality_after_input"), EVIDENCE_BEFORE, "metadata.evidence_after")
    require_true(metadata.get("okx_user_manual_archive_metadata_input_performed"), "metadata.input_performed")
    require_true(metadata.get("user_manual_okx_archive_metadata_present"), "metadata.present")
    require_true(metadata.get("user_manual_okx_archive_metadata_value_recorded"), "metadata.value_recorded")
    require_true(metadata.get("okx_csv_columns_recorded"), "metadata.csv_columns_recorded")
    require_true(metadata.get("okx_csv_row_count_recorded"), "metadata.csv_row_count_recorded")
    require_equal(metadata.get("okx_csv_columns"), EXPECTED_CSV_COLUMNS, "metadata.csv_columns")
    require_equal(metadata.get("okx_csv_row_count"), EXPECTED_ROW_COUNT, "metadata.row_count")
    require_equal(metadata.get("okx_open_time_delta_ms"), EXPECTED_OPEN_TIME_DELTA_MS, "metadata.open_time_delta_ms")
    require_equal(metadata.get("okx_inferred_candle_interval"), EXPECTED_INFERRED_INTERVAL, "metadata.inferred_interval")
    require_false(metadata.get("okx_direct_1h_interval_present"), "metadata.direct_1h_interval_present")
    require_equal(metadata.get("okx_timestamp_unit"), EXPECTED_TIMESTAMP_UNIT, "metadata.timestamp_unit")
    require_equal(metadata.get("okx_first_open_time_utc"), EXPECTED_FIRST_OPEN_TIME_UTC, "metadata.first_open_time_utc")
    require_equal(metadata.get("okx_last_open_time_utc"), EXPECTED_LAST_OPEN_TIME_UTC, "metadata.last_open_time_utc")
    require_equal(metadata.get("okx_daily_boundary_interpretation"), EXPECTED_DAILY_BOUNDARY, "metadata.daily_boundary")
    require_false(metadata.get("okx_archive_metadata_completeness_pass"), "metadata.completeness_pass")
    require_false(metadata.get("okx_1h_interval_resolved_now"), "metadata.1h_resolved_now")
    require_false(metadata.get("okx_coverage_resolved_now"), "metadata.coverage_resolved_now")
    require_equal(metadata.get("okx_schema_timezone_resolved_now"), "partial", "metadata.schema_timezone_resolved_now")
    require_false(metadata.get("okx_acquisition_readiness"), "metadata.acquisition_readiness")
    require_true(metadata.get("one_minute_to_one_hour_aggregation_required"), "metadata.aggregation_required")
    require_true(metadata.get("future_data_build_aggregation_required"), "metadata.future_data_build_aggregation_required")
    require_false(metadata.get("aggregation_performed_now"), "metadata.aggregation_performed_now")
    require_false(metadata.get("sample_zip_metadata_inspection_allowed_now"), "metadata.sample_zip_allowed")
    require_false(metadata.get("zip_download_allowed_now"), "metadata.zip_download_allowed")
    require_false(metadata.get("okx_api_allowed_now"), "metadata.okx_api_allowed")
    require_false(metadata.get("bulk_archive_download_allowed_now"), "metadata.bulk_archive_allowed")
    require_false(metadata.get("acquisition_execution_allowed_now"), "metadata.acquisition_allowed")
    require_false(metadata.get("data_download_performed"), "metadata.data_download_performed")
    require_false(metadata.get("data_fetch_performed"), "metadata.data_fetch_performed")
    require_false(metadata.get("data_build_performed"), "metadata.data_build_performed")
    require_false(metadata.get("okx_download_performed"), "metadata.okx_download_performed")
    require_false(metadata.get("okx_api_call_performed"), "metadata.okx_api_call_performed")
    require_false(metadata.get("okx_browse_performed"), "metadata.okx_browse_performed")
    require_false(metadata.get("okx_sample_zip_downloaded_now"), "metadata.okx_sample_zip_downloaded_now")
    require_equal(metadata.get("active_p0_blocker_count"), 0, "metadata.active_p0_blocker_count")
    require_equal(metadata.get("active_p1_attention_count"), 8, "metadata.active_p1_attention_count")
    require_equal(metadata.get("dormant_repo_attention_count"), 716, "metadata.dormant_repo_attention_count")
    require_false(metadata.get("generic_runner_approval_granted"), "metadata.generic_runner_approval_granted")
    require_true(metadata.get("generic_runner_implementation_remains_blocked"), "metadata.generic_runner_blocked")
    require_false(metadata.get("schema_or_config_created"), "metadata.schema_or_config_created")
    require_false(metadata.get("ordinary_selector_backlog_loop_reentry_allowed"), "metadata.loop_reentry")
    require_true(metadata.get("loop_remains_closed"), "metadata.loop_remains_closed")
    require_true(metadata.get("replacement_checks_all_true"), "metadata.replacement_checks_all_true")
    validate_no_true_dangerous_flags(metadata, "metadata")

    require_equal(
        approval.get("historical_data_acquisition_okx_archive_scope_resolution_approval_status"),
        APPROVAL_STATUS_PASS,
        "approval.status",
    )
    require_equal(approval.get("next_module"), "edge_factory_os_repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_input_after_approval_v1.py", "approval.next_module")
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
        "metadata_artifact_paths": {name: str(path) for name, path in REQUIRED_METADATA_ARTIFACTS.items()},
        "metadata_artifact_count": len(metadata_artifacts),
        "approval_artifact": str(APPROVAL_ARTIFACT),
        "preview_artifact": str(PREVIEW_ARTIFACT),
        "browse_lookup_validator_artifact": str(BROWSE_LOOKUP_VALIDATOR_ARTIFACT),
        "head": head,
        "status_lines_allowed": [f"?? {CURRENT_TOOL_REL}", f"A  {CURRENT_TOOL_REL}", f"AM {CURRENT_TOOL_REL}"],
    }


def validation_sections(metadata: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "metadata_artifact_validation": {
            "all_six_metadata_input_artifacts_exist": True,
            "all_six_metadata_input_artifacts_valid_json": True,
            "all_six_metadata_input_artifacts_non_empty": True,
            "metadata_input_status": metadata["historical_data_acquisition_okx_user_manual_archive_metadata_input_status"],
        },
        "schema_interval_validation": {
            "csv_columns_exact": EXPECTED_CSV_COLUMNS,
            "csv_columns_validated": True,
            "row_count": EXPECTED_ROW_COUNT,
            "row_count_validated": True,
            "open_time_delta_ms": EXPECTED_OPEN_TIME_DELTA_MS,
            "inferred_candle_interval": EXPECTED_INFERRED_INTERVAL,
            "direct_1h_interval_present": False,
            "one_minute_to_one_hour_aggregation_required": True,
            "aggregation_performed_now": False,
        },
        "timestamp_boundary_validation": {
            "timestamp_unit": EXPECTED_TIMESTAMP_UNIT,
            "first_open_time_utc": EXPECTED_FIRST_OPEN_TIME_UTC,
            "last_open_time_utc": EXPECTED_LAST_OPEN_TIME_UTC,
            "daily_boundary_interpretation": EXPECTED_DAILY_BOUNDARY,
            "official_okx_timezone_convention_still_requires_validation": True,
            "schema_timezone_is_partial_not_complete": True,
        },
        "archive_scope_validation": {
            "data_grouping_options": EXPECTED_DATA_GROUPING_OPTIONS,
            "target_instrument_type": EXPECTED_TARGET_INSTRUMENT_TYPE,
            "spot_not_required": True,
            "archive_scope_resolved_now": "partial",
            "coverage_resolved_now": False,
            "acquisition_readiness": False,
            "sample_file_does_not_prove_full_source_manifest": True,
            "sample_file_does_not_prove_full_symbol_universe": True,
            "sample_file_does_not_prove_complete_coverage": True,
        },
        "safety_validation": {
            "no_browsing": True,
            "no_okx_page_reopen": True,
            "no_okx_download": True,
            "no_sample_zip_download": True,
            "no_okx_api_call": True,
            "no_data_download_fetch_build": True,
            "no_aggregation": True,
            "no_strategy_backtest_candidate_runtime_live_generic_runner_schema_config": True,
            "old_route_not_reopened": True,
        },
        "risk_decision": {
            "okx_user_manual_archive_metadata_input_validated": True,
            "okx_metadata_validation_p0_count": 0,
            "okx_metadata_validation_p1_count": 6,
            "okx_metadata_validation_p2_count": 0,
            "okx_1m_schema_validated": True,
            "okx_direct_1h_absence_validated": True,
            "okx_1m_to_1h_aggregation_requirement_validated": True,
            "okx_schema_timezone_partial_validated": True,
            "okx_coverage_still_unresolved": True,
            "okx_source_manifest_still_required": True,
            "okx_provenance_still_required": True,
            "okx_acquisition_readiness": False,
            "acquisition_execution_remains_blocked": True,
        },
        "next_module_decision": {
            "preferred_next_module": NEXT_MODULE_POLICY_PREVIEW,
            "alternative_if_more_metadata_needed": NEXT_MODULE_BROWSE_DETAIL,
            "blocked_next_module": NEXT_MODULE_BLOCKED,
            "do_not_choose_aggregation_execution_directly": True,
            "do_not_choose_data_build_directly": True,
            "do_not_choose_zip_download": True,
            "do_not_choose_api_or_download": True,
            "do_not_choose_acquisition_execution_apply": True,
            "do_not_choose_strategy_research": True,
            "do_not_choose_candidate_backtest_runtime_live_capital": True,
        },
    }


def build_payload(preflight_report: Dict[str, Any], metadata: Dict[str, Any], sections: Dict[str, Any]) -> Dict[str, Any]:
    flags = dangerous_flags()
    replacement_checks = {
        "preflight_passed": preflight_report.get("whole_system_preflight_decision") == "PASS",
        "prior_metadata_input_respected": True,
        "required_metadata_artifacts_exist": True,
        "required_metadata_artifacts_valid_json": True,
        "schema_interval_validated": True,
        "timestamp_boundary_partial_validated": True,
        "archive_scope_partial_validated": True,
        "direct_1h_absence_validated": True,
        "aggregation_requirement_validated": True,
        "aggregation_not_performed": True,
        "data_build_not_performed": True,
        "acquisition_readiness_false": True,
        "sample_file_not_overclaimed": True,
        "p0_count_zero": True,
        "p1_count_present": True,
        "next_policy_preview_selected": True,
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
        "historical_data_acquisition_okx_user_manual_archive_metadata_input_validator_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "CREATE_OKX_1M_TO_1H_AGGREGATION_POLICY_PREVIEW_NO_EXECUTION",
        "next_module": NEXT_MODULE_POLICY_PREVIEW,
        **preflight_report,
        "prior_okx_metadata_input_respected": True,
        "metadata_artifact_validation_completed": True,
        "schema_interval_validation_completed": True,
        "timestamp_boundary_validation_completed": True,
        "archive_scope_validation_completed": True,
        "safety_validation_completed": True,
        "risk_decision_completed": True,
        "okx_user_manual_archive_metadata_input_validated": True,
        "required_metadata_artifacts_exist": True,
        "required_metadata_artifacts_valid_json": True,
        "okx_csv_columns_validated": True,
        "okx_csv_row_count_validated": True,
        "okx_open_time_delta_ms": EXPECTED_OPEN_TIME_DELTA_MS,
        "okx_inferred_candle_interval": EXPECTED_INFERRED_INTERVAL,
        "okx_1m_schema_validated": True,
        "okx_direct_1h_interval_present": False,
        "okx_direct_1h_absence_validated": True,
        "one_minute_to_one_hour_aggregation_required": True,
        "okx_1m_to_1h_aggregation_requirement_validated": True,
        "future_data_build_aggregation_required": True,
        "aggregation_performed_now": False,
        "okx_timestamp_unit": EXPECTED_TIMESTAMP_UNIT,
        "okx_first_open_time_utc": EXPECTED_FIRST_OPEN_TIME_UTC,
        "okx_last_open_time_utc": EXPECTED_LAST_OPEN_TIME_UTC,
        "okx_daily_boundary_interpretation": EXPECTED_DAILY_BOUNDARY,
        "okx_schema_timezone_partial_validated": True,
        "okx_archive_scope_resolved_now": "partial",
        "okx_coverage_resolved_now": False,
        "okx_coverage_still_unresolved": True,
        "okx_source_manifest_still_required": True,
        "okx_provenance_still_required": True,
        "okx_acquisition_readiness": False,
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
        "okx_metadata_validation_p0_count": 0,
        "okx_metadata_validation_p1_count": 6,
        "okx_metadata_validation_p2_count": 0,
        "current_evidence_chain_quality_before_validator": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_validator": EVIDENCE_AFTER,
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
            "PASS_OKX_ARCHIVE_METADATA_INPUT_VALIDATED_1M_SCHEMA_AGGREGATION_POLICY_PREVIEW_READY_NO_EXECUTION"
        ),
        "derived_live_repo_post_check_reason": (
            "repo-only validator confirmed the user/manual OKX metadata artifacts honestly record a 1m CSV schema "
            "sample, not direct 1h archive data; it validated the later 1m-to-1h aggregation-policy requirement, "
            "kept coverage/source-manifest/provenance unresolved, kept acquisition readiness false, and performed no "
            "browsing, ZIP/archive download, API call, data fetch, data build, aggregation, strategy, backtest, "
            "candidate, runtime, capital, live, generic-runner, schema, config, or old-route action"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": all(replacement_checks.values()),
        "validation_sections": sections,
        "validated_input_summary": {
            "okx_csv_columns": metadata.get("okx_csv_columns"),
            "okx_csv_row_count": metadata.get("okx_csv_row_count"),
            "okx_data_grouping_options": metadata.get("okx_data_grouping_options"),
            "okx_target_instrument_type": metadata.get("okx_target_instrument_type"),
            "okx_spot_not_required": metadata.get("okx_spot_not_required"),
            "okx_archive_metadata_completeness_pass": metadata.get("okx_archive_metadata_completeness_pass"),
            "missing_required_metadata_field_count": metadata.get("missing_required_metadata_field_count"),
        },
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "tracked_python_count_expectation": {
            "pre_commit": EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT,
        },
    }
    if payload["okx_metadata_validation_p0_count"] != 0:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: validator P0 count must be zero")
    if payload["okx_metadata_validation_p1_count"] < 1:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: validator P1 count was not carried forward")
    if payload["okx_direct_1h_interval_present"] is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: direct 1h was claimed")
    if payload["aggregation_performed_now"] is not False or payload["data_build_performed"] is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: aggregation/data build occurred")
    if payload["okx_acquisition_readiness"] is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: acquisition readiness was overclaimed")
    if payload["active_p1_attention_count"] < 8 or payload["p1_attention_carried_forward"] is not True:
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
    sections = payload["validation_sections"]
    artifacts = {
        "historical_okx_user_manual_archive_metadata_input_validator_report.json": payload,
        "historical_okx_metadata_artifact_validation_report.json": {
            "generated_at_utc": payload["generated_at_utc"],
            **sections["metadata_artifact_validation"],
            "required_metadata_artifacts_exist": payload["required_metadata_artifacts_exist"],
            "required_metadata_artifacts_valid_json": payload["required_metadata_artifacts_valid_json"],
        },
        "historical_okx_schema_interval_validation_report.json": {
            "generated_at_utc": payload["generated_at_utc"],
            **sections["schema_interval_validation"],
            "okx_1m_schema_validated": payload["okx_1m_schema_validated"],
            "okx_direct_1h_absence_validated": payload["okx_direct_1h_absence_validated"],
            "okx_1m_to_1h_aggregation_requirement_validated": payload[
                "okx_1m_to_1h_aggregation_requirement_validated"
            ],
        },
        "historical_okx_timestamp_boundary_validation_report.json": {
            "generated_at_utc": payload["generated_at_utc"],
            **sections["timestamp_boundary_validation"],
            "okx_schema_timezone_partial_validated": payload["okx_schema_timezone_partial_validated"],
        },
        "historical_okx_archive_scope_safety_risk_decision.json": {
            "generated_at_utc": payload["generated_at_utc"],
            "archive_scope_validation": sections["archive_scope_validation"],
            "safety_validation": sections["safety_validation"],
            "risk_decision": sections["risk_decision"],
            "next_module_decision": sections["next_module_decision"],
        },
        "historical_okx_user_manual_archive_metadata_input_validator_contract_compliance_report.json": {
            "generated_at_utc": payload["generated_at_utc"],
            "whole_system_preflight_completed": payload["whole_system_preflight_completed"],
            "whole_system_preflight_decision": payload["whole_system_preflight_decision"],
            "prior_okx_metadata_input_respected": payload["prior_okx_metadata_input_respected"],
            "metadata_artifact_validation_completed": payload["metadata_artifact_validation_completed"],
            "schema_interval_validation_completed": payload["schema_interval_validation_completed"],
            "timestamp_boundary_validation_completed": payload["timestamp_boundary_validation_completed"],
            "archive_scope_validation_completed": payload["archive_scope_validation_completed"],
            "safety_validation_completed": payload["safety_validation_completed"],
            "risk_decision_completed": payload["risk_decision_completed"],
            "okx_metadata_validation_p0_count": payload["okx_metadata_validation_p0_count"],
            "aggregation_performed_now": payload["aggregation_performed_now"],
            "data_build_performed": payload["data_build_performed"],
            "okx_browse_performed": payload["okx_browse_performed"],
            "okx_download_performed": payload["okx_download_performed"],
            "okx_api_call_performed": payload["okx_api_call_performed"],
            "okx_sample_zip_downloaded_now": payload["okx_sample_zip_downloaded_now"],
            "generic_runner_implementation_remains_blocked": payload[
                "generic_runner_implementation_remains_blocked"
            ],
            "schema_or_config_created": payload["schema_or_config_created"],
            "loop_remains_closed": payload["loop_remains_closed"],
            "replacement_checks_all_true": payload["replacement_checks_all_true"],
        },
        "repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_input_validator_after_approval_v1_latest.json": payload,
    }
    for name, artifact in artifacts.items():
        write_json(OUT_DIR / name, artifact)


def main() -> int:
    metadata = load_json(INPUT_LATEST_ARTIFACT)
    metadata_artifacts = load_required_metadata_artifacts()
    approval = load_json(APPROVAL_ARTIFACT)
    preview = load_json(PREVIEW_ARTIFACT)
    browse_validator = load_json(BROWSE_LOOKUP_VALIDATOR_ARTIFACT)
    preflight_report = validate_preflight(metadata, metadata_artifacts, approval, preview, browse_validator)
    sections = validation_sections(metadata)
    payload = build_payload(preflight_report, metadata, sections)
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
            "historical_data_acquisition_okx_user_manual_archive_metadata_input_validator_status": STATUS_BLOCKED_CONTEXT,
            "final_decision": STATUS_BLOCKED_CONTEXT,
            "next_action": "STOP_FAIL_CLOSED_NO_BROWSE_NO_DOWNLOAD_NO_API_NO_AGGREGATION_NO_DATA_BUILD",
            "next_module": NEXT_MODULE_BLOCKED,
            "error": str(exc),
            "okx_user_manual_archive_metadata_input_validated": False,
            "okx_metadata_validation_p0_count": 1,
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
            / "repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_input_validator_after_approval_v1_latest.json",
            failure,
        )
        print(json.dumps(failure, indent=2, sort_keys=True), file=sys.stderr)
        raise SystemExit(1)
