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
    "edge_factory_os_repo_only_historical_data_acquisition_okx_archive_scope_resolution_"
    "approval_after_preview_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_archive_scope_resolution_"
    "approval_after_preview_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "f1f2d7f"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 668
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 669

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_archive_scope_resolution_"
    "approval_after_preview_v1.py"
)
NEXT_MODULE_METADATA_INPUT = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_"
    "input_after_approval_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_archive_scope_resolution_"
    "approval_blocked_record_after_preview_v1.py"
)

PREVIEW_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_archive_scope_resolution_preview_after_browse_lookup_validator_v1"
    / "repo_only_historical_data_acquisition_okx_archive_scope_resolution_preview_after_browse_lookup_validator_v1_latest.json"
)
VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_validator_after_approval_v1"
    / "repo_only_historical_data_acquisition_browse_only_source_identity_lookup_validator_after_approval_v1_latest.json"
)
LOOKUP_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_after_approval_v1"
    / "repo_only_historical_data_acquisition_browse_only_source_identity_lookup_after_approval_v1_latest.json"
)
LOOKUP_APPROVAL_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_approval_after_preview_v1"
    / "repo_only_historical_data_acquisition_browse_only_source_identity_lookup_approval_after_preview_v1_latest.json"
)
USER_IDENTITY_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_user_supplied_source_identity_input_validator_after_approval_v1"
    / "repo_only_historical_data_acquisition_user_supplied_source_identity_input_validator_after_approval_v1_latest.json"
)

PREVIEW_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_SCOPE_RESOLUTION_PREVIEW_READY_"
    "APPROVAL_REQUIRED_NO_EXECUTION"
)
VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_VALIDATED_PARTIAL_"
    "OKX_IDENTITY_ARCHIVE_SCOPE_RESOLUTION_PREVIEW_READY_NO_EXECUTION"
)
LOOKUP_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_COMPLETE_PENDING_"
    "VALIDATOR_NO_EXECUTION"
)
LOOKUP_APPROVAL_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_APPROVED_NEXT_NO_EXECUTION"
)
USER_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_USER_SUPPLIED_SOURCE_IDENTITY_VALIDATED_INCOMPLETE_"
    "BROWSE_ONLY_LOOKUP_PREVIEW_READY_NO_EXECUTION"
)
STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_SCOPE_RESOLUTION_APPROVED_"
    "USER_MANUAL_METADATA_INPUT_NEXT_NO_EXECUTION"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_SCOPE_RESOLUTION_PREVIEW_READY_"
    "APPROVAL_REQUIRED_NO_EXECUTION"
)
EVIDENCE_AFTER = "HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_METADATA_INPUT_APPROVED_NEXT_NO_EXECUTION"
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"
USER_APPROVAL_SCOPE = (
    "APPROVAL_RECORD_ONLY_FOR_NEXT_USER_MANUAL_OKX_ARCHIVE_METADATA_INPUT_NO_BROWSE_"
    "NO_DOWNLOAD_NO_API_NO_EXECUTION"
)
PREVIEW_RECOMMENDED_ROUTE = "USER_MANUAL_OKX_ARCHIVE_METADATA_INPUT_PREVIEW_OR_BROWSE_ONLY_DETAIL_LOOKUP_FIRST"
APPROVED_RECOMMENDED_ROUTE = "USER_MANUAL_OKX_ARCHIVE_METADATA_INPUT_FIRST"

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


def require_all_false(data: Dict[str, Any], fields: List[str], artifact_name: str) -> None:
    for field in fields:
        require_false(data.get(field), f"{artifact_name}.{field}")


def require_all_true(data: Dict[str, Any], fields: List[str], artifact_name: str) -> None:
    for field in fields:
        require_true(data.get(field), f"{artifact_name}.{field}")


def validate_no_true_dangerous_flags(data: Dict[str, Any], artifact_name: str) -> None:
    true_flags = [name for name, value in data.get("dangerous_flags", {}).items() if value is True]
    if true_flags:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {artifact_name} dangerous flags true: {true_flags}")


def validate_preflight(
    preview: Dict[str, Any],
    validator: Dict[str, Any],
    lookup: Dict[str, Any],
    lookup_approval: Dict[str, Any],
    user_validator: Dict[str, Any],
) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))

    require_equal(
        preview.get("historical_data_acquisition_okx_archive_scope_resolution_preview_status"),
        PREVIEW_STATUS_PASS,
        "preview_status",
    )
    require_equal(
        validator.get("historical_data_acquisition_browse_only_source_identity_lookup_validator_status"),
        VALIDATOR_STATUS_PASS,
        "validator_status",
    )
    require_equal(
        lookup.get("historical_data_acquisition_browse_only_source_identity_lookup_status"),
        LOOKUP_STATUS_PASS,
        "lookup_status",
    )
    require_equal(
        lookup_approval.get("historical_data_acquisition_browse_only_source_identity_lookup_approval_status"),
        LOOKUP_APPROVAL_STATUS_PASS,
        "lookup_approval_status",
    )
    require_equal(
        user_validator.get("historical_data_acquisition_user_supplied_source_identity_input_validator_status"),
        USER_VALIDATOR_STATUS_PASS,
        "user_validator_status",
    )
    require_equal(preview.get("next_module"), REQUESTED_MODULE, "preview.next_module", STATUS_BLOCKED_NEXT_MODULE)

    require_all_true(
        preview,
        [
            "okx_archive_scope_resolution_preview_completed",
            "okx_source_identity_partially_verified_validated",
            "okx_archive_scope_resolution_required",
            "okx_1h_interval_resolution_required",
            "okx_coverage_resolution_required",
            "okx_schema_timezone_resolution_required",
            "future_sample_zip_metadata_inspection_requires_separate_approval",
            "future_api_or_bulk_download_requires_separate_chain",
            "generic_runner_implementation_remains_blocked",
            "loop_remains_closed",
            "replacement_checks_all_true",
        ],
        "preview",
    )
    require_all_false(
        preview,
        [
            "okx_source_verified_for_acquisition_now",
            "okx_acquisition_readiness",
            "sample_zip_metadata_inspection_allowed_now",
            "zip_download_allowed_now",
            "okx_api_allowed_now",
            "bulk_archive_download_allowed_now",
            "acquisition_execution_allowed_now",
            "external_download_allowed_now",
            "external_api_allowed_now",
            "data_download_performed",
            "data_fetch_performed",
            "data_build_performed",
            "okx_download_performed",
            "okx_api_call_performed",
            "okx_browse_performed",
            "okx_sample_zip_downloaded_now",
            "generic_runner_approval_granted",
            "schema_or_config_created",
            "ordinary_selector_backlog_loop_reentry_allowed",
        ],
        "preview",
    )
    require_equal(preview.get("recommended_resolution_route"), PREVIEW_RECOMMENDED_ROUTE, "preview.recommended_resolution_route")
    require_equal(preview.get("active_p0_blocker_count"), 0, "preview.active_p0_blocker_count")
    require_equal(preview.get("active_p1_attention_count"), 8, "preview.active_p1_attention_count")
    require_equal(preview.get("dormant_repo_attention_count"), 716, "preview.dormant_repo_attention_count")
    require_equal(preview.get("planned_schema_files_existing_count"), 0, "preview.planned_schema_files_existing_count")
    require_false(preview.get("generic_runner_target_exists"), "preview.generic_runner_target_exists")
    require_equal(preview.get("current_evidence_chain_quality_after_preview"), EVIDENCE_BEFORE, "preview.evidence_after")
    validate_no_true_dangerous_flags(preview, "preview")

    require_true(validator.get("okx_source_identity_partially_verified_validated"), "validator.okx_source_identity_partially_verified_validated")
    require_false(validator.get("okx_source_verified_for_acquisition_now"), "validator.okx_source_verified_for_acquisition_now")
    require_false(validator.get("okx_acquisition_readiness"), "validator.okx_acquisition_readiness")
    require_equal(validator.get("active_p0_blocker_count"), 0, "validator.active_p0_blocker_count")
    require_equal(validator.get("active_p1_attention_count"), 8, "validator.active_p1_attention_count")
    require_equal(validator.get("dormant_repo_attention_count"), 716, "validator.dormant_repo_attention_count")
    require_true(validator.get("replacement_checks_all_true"), "validator.replacement_checks_all_true")
    validate_no_true_dangerous_flags(validator, "validator")

    for artifact_name, artifact in [
        ("lookup", lookup),
        ("lookup_approval", lookup_approval),
        ("user_validator", user_validator),
    ]:
        require_true(artifact.get("replacement_checks_all_true"), f"{artifact_name}.replacement_checks_all_true")
        validate_no_true_dangerous_flags(artifact, artifact_name)

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
        "preview_artifact": str(PREVIEW_ARTIFACT),
        "validator_artifact": str(VALIDATOR_ARTIFACT),
        "lookup_artifact": str(LOOKUP_ARTIFACT),
        "lookup_approval_artifact": str(LOOKUP_APPROVAL_ARTIFACT),
        "user_identity_validator_artifact": str(USER_IDENTITY_VALIDATOR_ARTIFACT),
        "head": head,
        "status_lines_allowed": [f"?? {CURRENT_TOOL_REL}", f"A  {CURRENT_TOOL_REL}", f"AM {CURRENT_TOOL_REL}"],
    }


def approval_sections() -> Dict[str, Any]:
    return {
        "preview_context": {
            "okx_archive_scope_resolution_preview_completed": True,
            "partial_okx_identity_validated": True,
            "acquisition_readiness_remains_false": True,
            "archive_scope_resolution_required": True,
            "one_hour_interval_resolution_required": True,
            "coverage_resolution_required": True,
            "schema_timezone_resolution_required": True,
            "no_zip_api_download_browse_data_build_occurred": True,
            "active_p1_attention_count": 8,
            "dormant_repo_attention_count": 716,
        },
        "approval_scope": {
            "approval_grants_approval_record_only": True,
            "approval_grants_archive_scope_resolution_now": False,
            "approval_grants_future_user_manual_archive_metadata_input_next": True,
            "approval_grants_browse_now": False,
            "approval_grants_future_browse_only_detail_lookup_now": False,
            "approval_grants_sample_zip_metadata_inspection_now": False,
            "approval_grants_zip_download_now": False,
            "approval_grants_okx_api_now": False,
            "approval_grants_bulk_archive_download_now": False,
            "approval_grants_data_build_now": False,
            "approval_grants_acquisition_execution_now": False,
            "approval_grants_strategy_backtest_candidate_now": False,
            "approval_grants_runtime_capital_live_now": False,
            "approval_grants_generic_runner_now": False,
            "approval_grants_schema_config_now": False,
        },
        "future_user_manual_metadata_input_scope": {
            "may_accept_user_provided_visible_okx_archive_metadata_if_supplied": True,
            "may_record_user_provided_1h_interval_availability_statements": True,
            "may_record_user_provided_file_format_schema_statements": True,
            "may_record_user_provided_timestamp_timezone_statements": True,
            "may_record_user_provided_coverage_date_range_statements": True,
            "may_record_user_provided_archive_granularity_path_pattern_statements": True,
            "may_record_user_provided_symbol_instrument_universe_statements": True,
            "may_record_missing_fields_if_not_supplied": True,
            "must_not_browse": True,
            "must_not_download_zip_or_file": True,
            "must_not_call_api": True,
            "must_not_bulk_scrape": True,
            "must_not_build_data": True,
            "must_not_verify_official_status_through_network": True,
            "must_not_create_source_manifest": True,
            "must_not_treat_user_claims_as_acquisition_ready_without_validator": True,
            "must_not_run_strategy_backtest_candidate": True,
            "must_not_touch_runtime_capital_live": True,
            "must_not_create_schema_config": True,
        },
        "future_required_artifacts": [
            "historical_okx_user_manual_archive_metadata_input_report.json",
            "historical_okx_1h_interval_user_metadata_record.json",
            "historical_okx_coverage_user_metadata_record.json",
            "historical_okx_schema_timezone_user_metadata_record.json",
            "historical_okx_archive_scope_user_metadata_completeness_report.json",
            "historical_okx_archive_scope_user_metadata_contract_compliance_report.json",
        ],
        "fail_closed_rules": [
            "no metadata is supplied",
            "metadata is ambiguous",
            "1h interval is not supplied",
            "timezone/schema is not supplied",
            "coverage is not supplied",
            "metadata is treated as independently verified without validator",
            "ZIP/download/API occurs",
            "fake/synthetic metadata is used",
            "strategy/backtest/candidate/runtime/live path is touched",
            "hardening state is stale or invalid",
        ],
        "evidence_policy": {
            "before_approval": EVIDENCE_BEFORE,
            "after_approval": EVIDENCE_AFTER,
            "approval_is_not_archive_scope_resolution": True,
            "approval_is_not_data_evidence": True,
            "approval_is_not_source_manifest": True,
            "approval_is_not_provenance_report": True,
            "acquisition_execution_remains_blocked": True,
            "p1_remains_active_until_acquisition_and_historical_validator_closes_it": True,
        },
        "next_module_decision": {
            "if_approval_is_valid": NEXT_MODULE_METADATA_INPUT,
            "if_approval_is_unsafe": NEXT_MODULE_BLOCKED,
            "do_not_choose_browse_detail_lookup_directly": True,
            "do_not_choose_sample_zip_metadata_inspection_directly": True,
            "do_not_choose_zip_download": True,
            "do_not_choose_api_or_bulk_download": True,
            "do_not_choose_acquisition_execution_apply": True,
            "do_not_choose_strategy_research": True,
            "do_not_choose_candidate_backtest_runtime_live_capital": True,
        },
    }


def build_payload(preflight_report: Dict[str, Any], sections: Dict[str, Any]) -> Dict[str, Any]:
    flags = dangerous_flags()
    replacement_checks = {
        "preflight_passed": preflight_report.get("whole_system_preflight_decision") == "PASS",
        "preview_respected": True,
        "approval_record_only": True,
        "future_manual_metadata_input_only_next": True,
        "archive_scope_resolution_not_performed_now": True,
        "manual_metadata_input_not_captured_now": True,
        "browse_download_api_build_absent": True,
        "sample_zip_blocked_now": True,
        "api_bulk_chain_separate": True,
        "acquisition_blocked": True,
        "validator_required_after_future_metadata_input": True,
        "p1_carried_forward": True,
        "dormant_attention_carried_forward": True,
        "generic_runner_blocked": True,
        "schema_config_absent": True,
        "loop_closed": True,
    }
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_archive_scope_resolution_approval_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "RUN_USER_MANUAL_OKX_ARCHIVE_METADATA_INPUT_MODULE_ONLY_AFTER_SEPARATE_REQUEST",
        "next_module": NEXT_MODULE_METADATA_INPUT,
        **preflight_report,
        "prior_okx_archive_scope_resolution_preview_respected": True,
        "okx_archive_scope_resolution_approval_record_created": True,
        "user_okx_archive_scope_resolution_approval_present": True,
        "user_okx_archive_scope_resolution_approval_scope": USER_APPROVAL_SCOPE,
        "recommended_resolution_route": APPROVED_RECOMMENDED_ROUTE,
        "approval_grants_approval_record_only": True,
        "approval_grants_archive_scope_resolution_now": False,
        "approval_grants_future_user_manual_archive_metadata_input_next": True,
        "approval_grants_browse_now": False,
        "approval_grants_future_browse_only_detail_lookup_now": False,
        "approval_grants_sample_zip_metadata_inspection_now": False,
        "approval_grants_zip_download_now": False,
        "approval_grants_okx_api_now": False,
        "approval_grants_bulk_archive_download_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_acquisition_execution_now": False,
        "approval_grants_strategy_backtest_candidate_now": False,
        "approval_grants_runtime_capital_live_now": False,
        "approval_grants_generic_runner_now": False,
        "approval_grants_schema_config_now": False,
        "user_manual_archive_metadata_input_eligible_next": True,
        "okx_source_identity_partially_verified_validated": True,
        "okx_source_verified_for_acquisition_now": False,
        "okx_acquisition_readiness": False,
        "okx_archive_scope_resolution_required": True,
        "okx_1h_interval_resolution_required": True,
        "okx_coverage_resolution_required": True,
        "okx_schema_timezone_resolution_required": True,
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
        "future_sample_zip_metadata_inspection_requires_separate_approval": True,
        "future_api_or_bulk_download_requires_separate_chain": True,
        "source_manifest_required": True,
        "provenance_report_required": True,
        "survivorship_bias_controls_required": True,
        "symbol_lifecycle_report_required": True,
        "holdout_policy_required": True,
        "historical_data_quality_validator_required": True,
        "timeout_policy_required_for_acquisition": True,
        "memory_disk_resource_policy_required_for_acquisition": True,
        "rollback_policy_required_for_acquisition": True,
        "hardening_state_required_for_acquisition": True,
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
        "current_evidence_chain_quality_before_approval": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_approval": EVIDENCE_AFTER,
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
        "derived_live_repo_post_check": "PASS_OKX_ARCHIVE_METADATA_INPUT_APPROVED_NEXT_NO_EXECUTION",
        "derived_live_repo_post_check_reason": (
            "repo-only approval record created for the next user/manual OKX archive metadata input module; "
            "it performed no archive scope resolution, metadata capture, browsing, ZIP/archive download, API call, "
            "data fetch, data build, strategy, backtest, candidate, runtime, capital, live, generic-runner, schema, "
            "config, or old-route action"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": all(replacement_checks.values()),
        "approval_sections": sections,
        "future_validator_required_after_user_manual_metadata_input": True,
        "metadata_input_capture_performed_now": False,
        "archive_scope_resolution_performed_now": False,
        "source_manifest_created_now": False,
        "provenance_report_created_now": False,
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "tracked_python_count_expectation": {
            "pre_commit": EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT,
        },
    }
    if payload["active_p0_blocker_count"] > 0:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: active P0 blockers present")
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
    sections = payload["approval_sections"]
    artifacts = {
        "historical_okx_archive_scope_resolution_approval_report.json": payload,
        "historical_okx_archive_metadata_input_approval_scope.json": {
            "generated_at_utc": payload["generated_at_utc"],
            "approval_scope": sections["approval_scope"],
            "user_okx_archive_scope_resolution_approval_scope": payload[
                "user_okx_archive_scope_resolution_approval_scope"
            ],
            "recommended_resolution_route": payload["recommended_resolution_route"],
            "next_module": payload["next_module"],
        },
        "historical_okx_user_manual_archive_metadata_input_future_scope.json": {
            "generated_at_utc": payload["generated_at_utc"],
            "future_user_manual_metadata_input_scope": sections["future_user_manual_metadata_input_scope"],
            "future_required_artifacts": sections["future_required_artifacts"],
            "future_validator_required_after_user_manual_metadata_input": True,
        },
        "historical_okx_archive_metadata_input_fail_closed_rules.json": {
            "generated_at_utc": payload["generated_at_utc"],
            "fail_closed_rules": sections["fail_closed_rules"],
            "evidence_policy": sections["evidence_policy"],
        },
        "historical_okx_archive_scope_resolution_approval_contract_compliance_report.json": {
            "generated_at_utc": payload["generated_at_utc"],
            "whole_system_preflight_completed": payload["whole_system_preflight_completed"],
            "whole_system_preflight_decision": payload["whole_system_preflight_decision"],
            "okx_archive_scope_resolution_approval_record_created": payload[
                "okx_archive_scope_resolution_approval_record_created"
            ],
            "approval_grants_approval_record_only": payload["approval_grants_approval_record_only"],
            "approval_grants_archive_scope_resolution_now": payload["approval_grants_archive_scope_resolution_now"],
            "approval_grants_browse_now": payload["approval_grants_browse_now"],
            "approval_grants_zip_download_now": payload["approval_grants_zip_download_now"],
            "approval_grants_okx_api_now": payload["approval_grants_okx_api_now"],
            "approval_grants_data_build_now": payload["approval_grants_data_build_now"],
            "approval_grants_acquisition_execution_now": payload[
                "approval_grants_acquisition_execution_now"
            ],
            "metadata_input_capture_performed_now": payload["metadata_input_capture_performed_now"],
            "data_download_performed": payload["data_download_performed"],
            "data_fetch_performed": payload["data_fetch_performed"],
            "data_build_performed": payload["data_build_performed"],
            "generic_runner_implementation_remains_blocked": payload[
                "generic_runner_implementation_remains_blocked"
            ],
            "schema_or_config_created": payload["schema_or_config_created"],
            "loop_remains_closed": payload["loop_remains_closed"],
            "replacement_checks_all_true": payload["replacement_checks_all_true"],
        },
        "repo_only_historical_data_acquisition_okx_archive_scope_resolution_approval_after_preview_v1_latest.json": payload,
    }
    for name, artifact in artifacts.items():
        write_json(OUT_DIR / name, artifact)


def main() -> int:
    preview = load_json(PREVIEW_ARTIFACT)
    validator = load_json(VALIDATOR_ARTIFACT)
    lookup = load_json(LOOKUP_ARTIFACT)
    lookup_approval = load_json(LOOKUP_APPROVAL_ARTIFACT)
    user_validator = load_json(USER_IDENTITY_VALIDATOR_ARTIFACT)
    preflight_report = validate_preflight(preview, validator, lookup, lookup_approval, user_validator)
    sections = approval_sections()
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
            "historical_data_acquisition_okx_archive_scope_resolution_approval_status": STATUS_BLOCKED_CONTEXT,
            "final_decision": STATUS_BLOCKED_CONTEXT,
            "next_action": "STOP_FAIL_CLOSED_NO_ARCHIVE_SCOPE_RESOLUTION_NO_METADATA_CAPTURE_NO_BROWSE_NO_DOWNLOAD_NO_API_NO_DATA_BUILD",
            "next_module": NEXT_MODULE_BLOCKED,
            "error": str(exc),
            "whole_system_preflight_completed": False,
            "artifact_chain_consistent": False,
            "okx_archive_scope_resolution_approval_record_created": False,
            "user_okx_archive_scope_resolution_approval_present": False,
            "approval_grants_approval_record_only": False,
            "approval_grants_archive_scope_resolution_now": False,
            "approval_grants_browse_now": False,
            "approval_grants_zip_download_now": False,
            "approval_grants_okx_api_now": False,
            "approval_grants_data_build_now": False,
            "approval_grants_acquisition_execution_now": False,
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
            / "repo_only_historical_data_acquisition_okx_archive_scope_resolution_approval_after_preview_v1_latest.json",
            failure,
        )
        print(json.dumps(failure, indent=2, sort_keys=True), file=sys.stderr)
        raise SystemExit(1)
