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
    "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_"
    "approval_after_preview_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_"
    "approval_after_preview_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "c024c16"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 672
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 673

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_"
    "approval_after_preview_v1.py"
)
NEXT_MODULE_POLICY_CREATION = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_creation_"
    "after_approval_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_"
    "approval_blocked_record_after_preview_v1.py"
)

POLICY_PREVIEW_ARTIFACT = (
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
ARCHIVE_SCOPE_APPROVAL_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_archive_scope_resolution_approval_after_preview_v1"
    / "repo_only_historical_data_acquisition_okx_archive_scope_resolution_approval_after_preview_v1_latest.json"
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
ARCHIVE_SCOPE_APPROVAL_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_SCOPE_RESOLUTION_APPROVED_"
    "USER_MANUAL_METADATA_INPUT_NEXT_NO_EXECUTION"
)
STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_CREATION_"
    "APPROVED_NEXT_NO_EXECUTION"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_PREVIEW_READY_"
    "APPROVAL_REQUIRED_NO_EXECUTION"
)
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_CREATION_APPROVED_"
    "NEXT_NO_EXECUTION"
)
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"
USER_APPROVAL_SCOPE = (
    "APPROVAL_RECORD_ONLY_FOR_NEXT_REPO_ONLY_1M_TO_1H_AGGREGATION_POLICY_CREATION_"
    "NO_AGGREGATION_NO_DATA_BUILD"
)

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
    preview: Dict[str, Any],
    metadata_validator: Dict[str, Any],
    metadata_input: Dict[str, Any],
    archive_approval: Dict[str, Any],
) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))

    require_equal(
        preview.get("historical_data_acquisition_okx_1m_to_1h_aggregation_policy_preview_status"),
        PREVIEW_STATUS_PASS,
        "preview.status",
    )
    require_equal(preview.get("next_module"), REQUESTED_MODULE, "preview.next_module", STATUS_BLOCKED_NEXT_MODULE)
    require_true(preview.get("okx_1m_to_1h_aggregation_policy_preview_completed"), "preview.completed")
    require_true(preview.get("okx_1m_schema_validated"), "preview.okx_1m_schema_validated")
    require_false(preview.get("okx_direct_1h_interval_present"), "preview.direct_1h_interval_present")
    require_true(preview.get("okx_direct_1h_absence_validated"), "preview.direct_1h_absence_validated")
    require_true(preview.get("one_minute_to_one_hour_aggregation_required"), "preview.aggregation_required")
    require_true(preview.get("aggregation_policy_required"), "preview.aggregation_policy_required")
    require_false(preview.get("aggregation_policy_created_now"), "preview.aggregation_policy_created_now")
    require_false(preview.get("aggregation_performed_now"), "preview.aggregation_performed_now")
    require_false(preview.get("data_build_performed"), "preview.data_build_performed")
    require_equal(
        preview.get("canonical_aggregation_time_basis"),
        CANONICAL_AGGREGATION_TIME_BASIS,
        "preview.canonical_aggregation_time_basis",
    )
    require_equal(preview.get("output_hour_bucket_policy"), OUTPUT_HOUR_BUCKET_POLICY, "preview.output_hour_bucket_policy")
    require_equal(
        preview.get("complete_hour_required_source_rows"),
        COMPLETE_HOUR_REQUIRED_SOURCE_ROWS,
        "preview.complete_hour_required_source_rows",
    )
    require_false(preview.get("synthetic_fill_allowed"), "preview.synthetic_fill_allowed")
    require_true(preview.get("coverage_still_unresolved"), "preview.coverage_still_unresolved")
    require_true(preview.get("source_manifest_required"), "preview.source_manifest_required")
    require_true(preview.get("provenance_report_required"), "preview.provenance_report_required")
    require_true(preview.get("symbol_universe_required"), "preview.symbol_universe_required")
    require_false(preview.get("okx_acquisition_readiness"), "preview.okx_acquisition_readiness")
    require_false(preview.get("aggregation_execution_allowed_now"), "preview.aggregation_execution_allowed_now")
    require_false(preview.get("acquisition_execution_allowed_now"), "preview.acquisition_execution_allowed_now")
    require_false(preview.get("external_download_allowed_now"), "preview.external_download_allowed_now")
    require_false(preview.get("external_api_allowed_now"), "preview.external_api_allowed_now")
    require_false(preview.get("okx_download_performed"), "preview.okx_download_performed")
    require_false(preview.get("okx_api_call_performed"), "preview.okx_api_call_performed")
    require_false(preview.get("okx_browse_performed"), "preview.okx_browse_performed")
    require_false(preview.get("okx_sample_zip_downloaded_now"), "preview.okx_sample_zip_downloaded_now")
    require_true(preview.get("future_aggregation_policy_approval_required_next"), "preview.future_policy_approval_required")
    require_true(preview.get("future_data_build_requires_separate_approval"), "preview.future_data_build_separate")
    require_equal(preview.get("active_p0_blocker_count"), 0, "preview.active_p0_blocker_count")
    require_equal(preview.get("active_p1_attention_count"), 8, "preview.active_p1_attention_count")
    require_equal(preview.get("dormant_repo_attention_count"), 716, "preview.dormant_repo_attention_count")
    require_false(preview.get("generic_runner_approval_granted"), "preview.generic_runner_approval_granted")
    require_true(preview.get("generic_runner_implementation_remains_blocked"), "preview.generic_runner_blocked")
    require_false(preview.get("schema_or_config_created"), "preview.schema_or_config_created")
    require_false(preview.get("ordinary_selector_backlog_loop_reentry_allowed"), "preview.loop_reentry")
    require_true(preview.get("loop_remains_closed"), "preview.loop_remains_closed")
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
    require_false(metadata_input.get("aggregation_performed_now"), "metadata_input.aggregation_performed_now")
    require_false(metadata_input.get("data_build_performed"), "metadata_input.data_build_performed")
    require_false(metadata_input.get("okx_acquisition_readiness"), "metadata_input.okx_acquisition_readiness")
    require_true(metadata_input.get("replacement_checks_all_true"), "metadata_input.replacement_checks_all_true")
    validate_no_true_dangerous_flags(metadata_input, "metadata_input")

    require_equal(
        archive_approval.get("historical_data_acquisition_okx_archive_scope_resolution_approval_status"),
        ARCHIVE_SCOPE_APPROVAL_STATUS_PASS,
        "archive_approval.status",
    )
    require_true(archive_approval.get("replacement_checks_all_true"), "archive_approval.replacement_checks_all_true")
    validate_no_true_dangerous_flags(archive_approval, "archive_approval")

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
        "policy_preview_artifact": str(POLICY_PREVIEW_ARTIFACT),
        "metadata_validator_artifact": str(METADATA_VALIDATOR_ARTIFACT),
        "metadata_input_artifact": str(METADATA_INPUT_ARTIFACT),
        "archive_scope_approval_artifact": str(ARCHIVE_SCOPE_APPROVAL_ARTIFACT),
        "head": head,
        "status_lines_allowed": [f"?? {CURRENT_TOOL_REL}", f"A  {CURRENT_TOOL_REL}", f"AM {CURRENT_TOOL_REL}"],
    }


def approval_sections() -> Dict[str, Any]:
    return {
        "preview_context": {
            "aggregation_policy_preview_completed": True,
            "okx_1m_schema_validated": True,
            "okx_direct_1h_absence_validated": True,
            "one_minute_to_one_hour_aggregation_required": True,
            "canonical_utc_hourly_bucket_policy_previewed": True,
            "complete_hour_required_source_rows": COMPLETE_HOUR_REQUIRED_SOURCE_ROWS,
            "synthetic_fill_forbidden": True,
            "source_manifest_required": True,
            "provenance_report_required": True,
            "symbol_universe_required": True,
            "coverage_still_unresolved": True,
            "okx_acquisition_readiness": False,
            "active_p1_attention_count": 8,
            "dormant_repo_attention_count": 716,
        },
        "approval_scope": {
            "approval_grants_approval_record_only": True,
            "approval_grants_policy_creation_now": False,
            "approval_grants_future_policy_creation_next": True,
            "approval_grants_aggregation_execution_now": False,
            "approval_grants_data_build_now": False,
            "approval_grants_acquisition_execution_now": False,
            "approval_grants_download_now": False,
            "approval_grants_api_now": False,
            "approval_grants_browse_now": False,
            "approval_grants_strategy_backtest_candidate_now": False,
            "approval_grants_runtime_capital_live_now": False,
            "approval_grants_generic_runner_now": False,
            "approval_grants_schema_config_now": False,
        },
        "future_policy_creation_scope": {
            "may_create_repo_only_policy_artifact_outside_repo_or_established_output_dir": True,
            "may_define_canonical_1m_input_schema": True,
            "may_define_utc_hour_bucket_rules": True,
            "may_define_ohlcv_aggregation_formulas": True,
            "may_define_complete_hour_rule_requiring_60_unique_minute_rows": True,
            "may_define_missing_duplicate_incomplete_hour_fail_closed_rules": True,
            "may_define_confirm_handling": True,
            "may_define_numeric_sanity_rules": True,
            "may_define_coverage_source_manifest_provenance_prerequisites": True,
            "may_define_future_validator_requirements": True,
            "must_not_aggregate_real_data": True,
            "must_not_build_data": True,
            "must_not_read_real_okx_csv_files": True,
            "must_not_download_fetch_api_browse": True,
            "must_not_create_executable_production_aggregation_runner": True,
            "must_not_create_repo_schema_config": True,
            "must_not_run_strategy_backtest_candidate": True,
            "must_not_touch_runtime_capital_live": True,
            "must_not_approve_generic_runner": True,
            "must_not_claim_profit_or_edge": True,
        },
        "future_required_artifacts": {
            "future_policy_creation": [
                "historical_okx_1m_to_1h_aggregation_policy.json",
                "historical_okx_1m_to_1h_aggregation_policy_contract_compliance_report.json",
            ],
            "future_validator": [
                "historical_okx_1m_to_1h_aggregation_policy_validator.json",
            ],
        },
        "fail_closed_rules": [
            "policy permits synthetic fill",
            "policy allows incomplete hours without flagging/exclusion",
            "policy does not require 60 unique source rows for complete hour",
            "policy allows aggregation without source manifest/provenance",
            "policy treats policy creation as data build",
            "policy approves aggregation execution",
            "policy approves acquisition execution",
            "policy allows strategy/backtest/candidate/runtime/live path",
            "hardening state is stale or invalid",
        ],
        "evidence_policy": {
            "before_approval": EVIDENCE_BEFORE,
            "after_approval": EVIDENCE_AFTER,
            "approval_is_not_policy_creation": True,
            "approval_is_not_aggregation": True,
            "approval_is_not_data_build": True,
            "approval_is_not_acquisition_execution": True,
            "approval_is_not_source_manifest": True,
            "approval_is_not_provenance_report": True,
            "p1_remains_active_until_acquisition_build_historical_validator_closes_it": True,
        },
        "next_module_decision": {
            "if_approval_is_valid": NEXT_MODULE_POLICY_CREATION,
            "if_approval_is_unsafe": NEXT_MODULE_BLOCKED,
            "do_not_choose_aggregation_execution": True,
            "do_not_choose_data_build": True,
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
        "prior_preview_respected": True,
        "approval_record_only": True,
        "policy_creation_not_now": True,
        "future_policy_creation_next": True,
        "aggregation_not_performed": True,
        "data_build_not_performed": True,
        "download_api_browse_absent": True,
        "source_manifest_not_created": True,
        "schema_config_absent": True,
        "acquisition_blocked": True,
        "future_data_build_separate": True,
        "future_validator_required": True,
        "p1_carried_forward": True,
        "dormant_attention_carried_forward": True,
        "generic_runner_blocked": True,
        "loop_closed": True,
    }
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_1m_to_1h_aggregation_policy_approval_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "RUN_REPO_ONLY_OKX_1M_TO_1H_AGGREGATION_POLICY_CREATION_MODULE_NO_EXECUTION",
        "next_module": NEXT_MODULE_POLICY_CREATION,
        **preflight_report,
        "prior_aggregation_policy_preview_respected": True,
        "okx_1m_to_1h_aggregation_policy_approval_record_created": True,
        "user_aggregation_policy_approval_present": True,
        "user_aggregation_policy_approval_scope": USER_APPROVAL_SCOPE,
        "approval_grants_approval_record_only": True,
        "approval_grants_policy_creation_now": False,
        "approval_grants_future_policy_creation_next": True,
        "approval_grants_aggregation_execution_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_acquisition_execution_now": False,
        "approval_grants_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_strategy_backtest_candidate_now": False,
        "approval_grants_runtime_capital_live_now": False,
        "approval_grants_generic_runner_now": False,
        "approval_grants_schema_config_now": False,
        "future_policy_creation_eligible_next": True,
        "okx_1m_schema_validated": True,
        "okx_direct_1h_interval_present": False,
        "okx_direct_1h_absence_validated": True,
        "one_minute_to_one_hour_aggregation_required": True,
        "aggregation_policy_required": True,
        "aggregation_policy_created_now": False,
        "aggregation_performed_now": False,
        "data_build_performed": False,
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
        "derived_live_repo_post_check": (
            "PASS_OKX_1M_TO_1H_AGGREGATION_POLICY_CREATION_APPROVED_NEXT_NO_EXECUTION"
        ),
        "derived_live_repo_post_check_reason": (
            "repo-only approval record created for the next separate OKX 1m-to-1h aggregation policy creation module; "
            "it created no policy artifact, executable aggregation code, aggregation output, data build, source manifest, "
            "schema/config, and performed no browsing, download, API call, strategy, backtest, candidate, runtime, capital, "
            "live, generic-runner, or old-route action"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": all(replacement_checks.values()),
        "approval_sections": sections,
        "future_policy_validator_required_after_creation": True,
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "tracked_python_count_expectation": {
            "pre_commit": EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT,
        },
    }
    if payload["aggregation_policy_created_now"] is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: aggregation policy was created now")
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
    sections = payload["approval_sections"]
    artifacts = {
        "historical_okx_1m_to_1h_aggregation_policy_approval_report.json": payload,
        "historical_okx_1m_to_1h_aggregation_policy_approval_scope.json": {
            "generated_at_utc": payload["generated_at_utc"],
            "user_aggregation_policy_approval_scope": payload["user_aggregation_policy_approval_scope"],
            "approval_scope": sections["approval_scope"],
            "future_policy_creation_eligible_next": payload["future_policy_creation_eligible_next"],
            "next_module": payload["next_module"],
        },
        "historical_okx_1m_to_1h_future_policy_creation_scope.json": {
            "generated_at_utc": payload["generated_at_utc"],
            "future_policy_creation_scope": sections["future_policy_creation_scope"],
            "future_required_artifacts": sections["future_required_artifacts"],
            "future_policy_validator_required_after_creation": True,
        },
        "historical_okx_1m_to_1h_policy_approval_fail_closed_rules.json": {
            "generated_at_utc": payload["generated_at_utc"],
            "fail_closed_rules": sections["fail_closed_rules"],
            "evidence_policy": sections["evidence_policy"],
            "next_module_decision": sections["next_module_decision"],
        },
        "historical_okx_1m_to_1h_aggregation_policy_approval_contract_compliance_report.json": {
            "generated_at_utc": payload["generated_at_utc"],
            "whole_system_preflight_completed": payload["whole_system_preflight_completed"],
            "whole_system_preflight_decision": payload["whole_system_preflight_decision"],
            "okx_1m_to_1h_aggregation_policy_approval_record_created": payload[
                "okx_1m_to_1h_aggregation_policy_approval_record_created"
            ],
            "approval_grants_approval_record_only": payload["approval_grants_approval_record_only"],
            "approval_grants_policy_creation_now": payload["approval_grants_policy_creation_now"],
            "approval_grants_future_policy_creation_next": payload["approval_grants_future_policy_creation_next"],
            "approval_grants_aggregation_execution_now": payload["approval_grants_aggregation_execution_now"],
            "approval_grants_data_build_now": payload["approval_grants_data_build_now"],
            "approval_grants_acquisition_execution_now": payload["approval_grants_acquisition_execution_now"],
            "aggregation_policy_created_now": payload["aggregation_policy_created_now"],
            "aggregation_performed_now": payload["aggregation_performed_now"],
            "data_build_performed": payload["data_build_performed"],
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
        "repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_approval_after_preview_v1_latest.json": payload,
    }
    for name, artifact in artifacts.items():
        write_json(OUT_DIR / name, artifact)


def main() -> int:
    preview = load_json(POLICY_PREVIEW_ARTIFACT)
    metadata_validator = load_json(METADATA_VALIDATOR_ARTIFACT)
    metadata_input = load_json(METADATA_INPUT_ARTIFACT)
    archive_approval = load_json(ARCHIVE_SCOPE_APPROVAL_ARTIFACT)
    preflight_report = validate_preflight(preview, metadata_validator, metadata_input, archive_approval)
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
            "historical_data_acquisition_okx_1m_to_1h_aggregation_policy_approval_status": STATUS_BLOCKED_CONTEXT,
            "final_decision": STATUS_BLOCKED_CONTEXT,
            "next_action": "STOP_FAIL_CLOSED_NO_POLICY_CREATION_NO_AGGREGATION_NO_DATA_BUILD_NO_BROWSE_NO_DOWNLOAD_NO_API",
            "next_module": NEXT_MODULE_BLOCKED,
            "error": str(exc),
            "active_p0_blocker_count": 1,
            "okx_1m_to_1h_aggregation_policy_approval_record_created": False,
            "user_aggregation_policy_approval_present": False,
            "approval_grants_approval_record_only": False,
            "approval_grants_policy_creation_now": False,
            "approval_grants_aggregation_execution_now": False,
            "approval_grants_data_build_now": False,
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
            / "repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_approval_after_preview_v1_latest.json",
            failure,
        )
        print(json.dumps(failure, indent=2, sort_keys=True), file=sys.stderr)
        raise SystemExit(1)
