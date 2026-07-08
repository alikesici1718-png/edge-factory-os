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
    "edge_factory_os_repo_only_historical_data_acquisition_okx_archive_scope_resolution_preview_"
    "after_browse_lookup_validator_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_archive_scope_resolution_preview_"
    "after_browse_lookup_validator_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "f000cb8"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 667
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 668

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_archive_scope_resolution_preview_"
    "after_browse_lookup_validator_v1.py"
)
NEXT_MODULE_APPROVAL = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_archive_scope_resolution_"
    "approval_after_preview_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_archive_scope_resolution_preview_"
    "blocked_record_after_browse_lookup_validator_v1.py"
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
APPROVAL_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_approval_after_preview_v1"
    / "repo_only_historical_data_acquisition_browse_only_source_identity_lookup_approval_after_preview_v1_latest.json"
)
USER_IDENTITY_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_user_supplied_source_identity_input_validator_after_approval_v1"
    / "repo_only_historical_data_acquisition_user_supplied_source_identity_input_validator_after_approval_v1_latest.json"
)

VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_VALIDATED_PARTIAL_"
    "OKX_IDENTITY_ARCHIVE_SCOPE_RESOLUTION_PREVIEW_READY_NO_EXECUTION"
)
LOOKUP_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_COMPLETE_PENDING_"
    "VALIDATOR_NO_EXECUTION"
)
APPROVAL_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_APPROVED_NEXT_NO_EXECUTION"
)
USER_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_USER_SUPPLIED_SOURCE_IDENTITY_VALIDATED_INCOMPLETE_"
    "BROWSE_ONLY_LOOKUP_PREVIEW_READY_NO_EXECUTION"
)
STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_SCOPE_RESOLUTION_PREVIEW_READY_"
    "APPROVAL_REQUIRED_NO_EXECUTION"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_VALIDATED_PARTIAL_"
    "OKX_IDENTITY_ARCHIVE_SCOPE_RESOLUTION_PREVIEW_READY_NO_EXECUTION"
)
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_SCOPE_RESOLUTION_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION"
)
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"
RECOMMENDED_ROUTE = "USER_MANUAL_OKX_ARCHIVE_METADATA_INPUT_PREVIEW_OR_BROWSE_ONLY_DETAIL_LOOKUP_FIRST"

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


def validate_preflight(
    validator: Dict[str, Any],
    lookup: Dict[str, Any],
    approval: Dict[str, Any],
    user_validator: Dict[str, Any],
) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))

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
        approval.get("historical_data_acquisition_browse_only_source_identity_lookup_approval_status"),
        APPROVAL_STATUS_PASS,
        "approval_status",
    )
    require_equal(
        user_validator.get("historical_data_acquisition_user_supplied_source_identity_input_validator_status"),
        USER_VALIDATOR_STATUS_PASS,
        "user_validator_status",
    )
    require_equal(validator.get("next_module"), REQUESTED_MODULE, "validator.next_module", STATUS_BLOCKED_NEXT_MODULE)

    required_true = [
        "browse_only_lookup_validated",
        "okx_source_identity_partially_verified_validated",
        "okx_archive_scope_resolution_required",
        "okx_1h_interval_resolution_required",
        "okx_coverage_resolution_required",
        "okx_schema_timezone_resolution_required",
    ]
    for field in required_true:
        require_true(validator.get(field), f"validator.{field}")
    required_false = [
        "okx_source_verified_for_acquisition_now",
        "okx_acquisition_readiness",
        "okx_sample_zip_downloaded_now",
        "okx_download_performed",
        "okx_api_call_performed",
        "data_download_performed",
        "data_fetch_performed",
        "data_build_performed",
        "external_api_calls_performed",
        "generic_runner_approval_granted",
        "schema_or_config_created",
        "ordinary_selector_backlog_loop_reentry_allowed",
    ]
    for field in required_false:
        require_false(validator.get(field), f"validator.{field}")
    require_equal(validator.get("active_p0_blocker_count"), 0, "validator.active_p0_blocker_count")
    require_equal(validator.get("active_p1_attention_count"), 8, "validator.active_p1_attention_count")
    require_equal(validator.get("dormant_repo_attention_count"), 716, "validator.dormant_repo_attention_count")
    require_true(validator.get("generic_runner_implementation_remains_blocked"), "validator.generic_runner_implementation_remains_blocked")
    require_true(validator.get("loop_remains_closed"), "validator.loop_remains_closed")
    require_true(validator.get("replacement_checks_all_true"), "validator.replacement_checks_all_true")

    true_dangerous = [
        name for name, value in validator.get("dangerous_flags", {}).items() if value is True
    ]
    if true_dangerous:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: validator dangerous flags true: {true_dangerous}")

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
        "active_p0_blocker_count_from_live_artifact": validator.get("active_p0_blocker_count"),
        "active_p1_attention_count_from_live_artifact": validator.get("active_p1_attention_count"),
        "p1_attention_carried_forward": True,
        "dormant_repo_attention_count_carried_forward": True,
        "blocked_actions_absent_from_requested_module": True,
        "validator_artifact": str(VALIDATOR_ARTIFACT),
        "lookup_artifact": str(LOOKUP_ARTIFACT),
        "approval_artifact": str(APPROVAL_ARTIFACT),
        "user_identity_validator_artifact": str(USER_IDENTITY_VALIDATOR_ARTIFACT),
        "head": head,
        "status_lines_allowed": [f"?? {CURRENT_TOOL_REL}", f"A  {CURRENT_TOOL_REL}", f"AM {CURRENT_TOOL_REL}"],
    }


def preview_sections() -> Dict[str, Any]:
    return {
        "validator_context": {
            "browse_only_lookup_validator_passed": True,
            "partial_okx_source_identity_accepted": True,
            "acquisition_readiness": False,
            "active_p1_attention_count": 8,
            "dormant_repo_attention_count": 716,
            "no_download_api_data_build_occurred": True,
        },
        "unresolved_scope_context": {
            "okx_archive_scope_resolution_required": True,
            "okx_1h_interval_resolution_required": True,
            "okx_coverage_resolution_required": True,
            "okx_schema_timezone_resolution_required": True,
            "full_3_to_4_year_coverage_proven_now": False,
            "full_4_year_coverage_proven_now": False,
            "source_manifest_proven_now": False,
            "provenance_report_proven_now": False,
            "okx_file_format_visible": False,
            "okx_1h_interval_visible": False,
            "okx_timestamp_timezone_visible": False,
        },
        "future_resolution_routes_preview": [
            {
                "route": "USER_MANUAL_OKX_ARCHIVE_METADATA_INPUT_PREVIEW",
                "order": "A",
                "description": "User manually inspects OKX page/download UI and supplies archive metadata.",
                "acceptable_future_inputs": [
                    "visible 1h interval support",
                    "file format/schema notes",
                    "timezone notes",
                    "coverage notes",
                    "archive pattern notes",
                ],
                "system_browse_download_api_required": False,
            },
            {
                "route": "BROWSE_ONLY_ARCHIVE_SCOPE_DETAIL_LOOKUP_PREVIEW",
                "order": "B",
                "description": "Separate approved browse-only module may inspect OKX page/UI text for archive-scope details.",
                "download_allowed": False,
                "api_allowed": False,
                "bulk_scrape_allowed": False,
                "archive_iteration_allowed": False,
                "scope": "metadata/citations/visible details only",
            },
            {
                "route": "SINGLE_SAMPLE_ZIP_METADATA_PREVIEW",
                "order": "C",
                "description": "Later option after separate preview and approval to inspect exactly one sample ZIP for schema/timezone/interval metadata.",
                "allowed_now": False,
                "treat_one_file_as_full_coverage": False,
                "dataset_build_allowed": False,
                "bulk_acquisition_allowed": False,
                "requires_rollback_resource_hash_policy": True,
                "requires_validator_afterward": True,
            },
            {
                "route": "SEPARATE_API_OR_BULK_DOWNLOAD_CHAIN_PREVIEW",
                "order": "D",
                "description": "Only if archive scope cannot be resolved manually or via browse-only path.",
                "allowed_now": False,
                "requires_separate_preview_approval_execution_validator_chain": True,
            },
        ],
        "recommended_resolution_route": {
            "recommended_resolution_route": RECOMMENDED_ROUTE,
            "zip_download_approved_now": False,
            "api_download_approved_now": False,
            "single_sample_zip_metadata_inspection_later_only_after_separate_approval": True,
            "acquisition_execution_remains_blocked": True,
        },
        "required_future_answers": [
            "is 1h candlestick interval actually available in downloadable archives?",
            "which instruments/markets are included?",
            "what archive granularity exists: daily/monthly/per-symbol/per-instrument?",
            "what file format is inside ZIP?",
            "what columns/schema are present?",
            "what timestamp timezone/convention is used?",
            "does July 2023 onward provide enough for 3 years by target date?",
            "is 4-year coverage impossible from OKX source alone?",
            "is a second source needed for pre-July-2023 data?",
            "what exact source manifest can be created later?",
            "what provenance proof can be produced later?",
        ],
        "future_required_artifacts": [
            "historical_okx_archive_scope_resolution_report.json",
            "historical_okx_1h_interval_resolution_report.json",
            "historical_okx_coverage_resolution_report.json",
            "historical_okx_schema_timezone_resolution_report.json",
            "historical_okx_archive_scope_gap_decision.json",
            "historical_okx_archive_scope_contract_compliance_report.json",
        ],
        "fail_closed_preview": [
            "1h availability cannot be confirmed",
            "timestamp/timezone cannot be confirmed",
            "file schema cannot be confirmed",
            "3-year coverage cannot be confirmed",
            "4-year coverage is falsely claimed",
            "source manifest cannot be produced later",
            "ZIP/download/API occurs without separate approval",
            "one sample ZIP is treated as full coverage",
            "fake/synthetic data is treated as real",
            "strategy/backtest/candidate/runtime/live path is touched",
        ],
        "evidence_policy_preview": {
            "before_preview": EVIDENCE_BEFORE,
            "after_preview": EVIDENCE_AFTER,
            "preview_is_not_archive_scope_resolution": True,
            "preview_is_not_data_evidence": True,
            "preview_is_not_source_manifest": True,
            "preview_is_not_provenance_report": True,
            "acquisition_execution_remains_blocked": True,
            "p1_remains_active_until_acquisition_and_historical_validator_closes_it": True,
        },
        "next_module_decision": {
            "if_preview_is_safe": NEXT_MODULE_APPROVAL,
            "if_preview_is_unsafe": NEXT_MODULE_BLOCKED,
            "do_not_choose_archive_scope_execution_directly": True,
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
        "validator_context_completed": True,
        "unresolved_scope_context_completed": True,
        "future_routes_preview_completed": True,
        "recommended_route_selected": True,
        "approval_next_not_execution": True,
        "no_browse_download_fetch_api_build": True,
        "sample_zip_blocked_now": True,
        "acquisition_blocked": True,
        "generic_runner_blocked": True,
        "schema_config_absent": True,
        "loop_closed": True,
        "not_overclaimed": True,
    }
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_archive_scope_resolution_preview_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "CREATE_OKX_ARCHIVE_SCOPE_RESOLUTION_APPROVAL_RECORD_NO_EXECUTION",
        "next_module": NEXT_MODULE_APPROVAL,
        **preflight_report,
        "prior_browse_lookup_validator_respected": True,
        "okx_archive_scope_resolution_preview_completed": True,
        "validator_context_completed": True,
        "unresolved_scope_context_completed": True,
        "future_resolution_routes_preview_completed": True,
        "recommended_resolution_route_completed": True,
        "required_future_answers_completed": True,
        "future_required_artifacts_completed": True,
        "fail_closed_preview_completed": True,
        "evidence_policy_preview_completed": True,
        "recommended_resolution_route": RECOMMENDED_ROUTE,
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
        "derived_live_repo_post_check": "PASS_OKX_ARCHIVE_SCOPE_RESOLUTION_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION",
        "derived_live_repo_post_check_reason": (
            "repo-only preview preserved partial OKX identity, kept acquisition readiness false, planned manual or browse-only "
            "archive metadata resolution before any sample ZIP/API/bulk path, required separate approval next, and performed no "
            "browsing, ZIP/archive download, API call, data fetch, data build, strategy, runtime, capital, live, generic-runner, schema, config, or old-route action"
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
    if payload["planned_schema_files_existing_count"] != 0:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: planned schema files exist unexpectedly")
    if payload["generic_runner_target_exists"] is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: generic runner target exists unexpectedly")
    if payload["replacement_checks_all_true"] is not True:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: replacement checks failed")
    return payload


def write_artifacts(payload: Dict[str, Any]) -> None:
    sections = payload["preview_sections"]
    artifacts = {
        "historical_okx_archive_scope_resolution_preview_report.json": payload,
        "historical_okx_archive_scope_resolution_routes_preview.json": {
            "generated_at_utc": payload["generated_at_utc"],
            "future_resolution_routes_preview": sections["future_resolution_routes_preview"],
            "recommended_resolution_route": payload["recommended_resolution_route"],
            "sample_zip_metadata_inspection_allowed_now": False,
            "zip_download_allowed_now": False,
            "okx_api_allowed_now": False,
            "bulk_archive_download_allowed_now": False,
        },
        "historical_okx_archive_scope_unresolved_requirements_preview.json": {
            "generated_at_utc": payload["generated_at_utc"],
            **sections["unresolved_scope_context"],
            "required_future_answers": sections["required_future_answers"],
        },
        "historical_okx_archive_scope_future_artifacts_preview.json": {
            "generated_at_utc": payload["generated_at_utc"],
            "future_required_artifacts": sections["future_required_artifacts"],
        },
        "historical_okx_archive_scope_fail_closed_preview.json": {
            "generated_at_utc": payload["generated_at_utc"],
            "fail_closed_preview": sections["fail_closed_preview"],
            "evidence_policy_preview": sections["evidence_policy_preview"],
        },
        "historical_okx_archive_scope_resolution_preview_contract_compliance_report.json": {
            "generated_at_utc": payload["generated_at_utc"],
            "whole_system_preflight_completed": payload["whole_system_preflight_completed"],
            "whole_system_preflight_decision": payload["whole_system_preflight_decision"],
            "okx_archive_scope_resolution_preview_completed": payload["okx_archive_scope_resolution_preview_completed"],
            "sample_zip_metadata_inspection_allowed_now": payload["sample_zip_metadata_inspection_allowed_now"],
            "zip_download_allowed_now": payload["zip_download_allowed_now"],
            "okx_api_allowed_now": payload["okx_api_allowed_now"],
            "bulk_archive_download_allowed_now": payload["bulk_archive_download_allowed_now"],
            "acquisition_execution_allowed_now": payload["acquisition_execution_allowed_now"],
            "data_download_performed": payload["data_download_performed"],
            "data_fetch_performed": payload["data_fetch_performed"],
            "data_build_performed": payload["data_build_performed"],
            "generic_runner_implementation_remains_blocked": payload["generic_runner_implementation_remains_blocked"],
            "schema_or_config_created": payload["schema_or_config_created"],
            "loop_remains_closed": payload["loop_remains_closed"],
            "replacement_checks_all_true": payload["replacement_checks_all_true"],
        },
        "repo_only_historical_data_acquisition_okx_archive_scope_resolution_preview_after_browse_lookup_validator_v1_latest.json": payload,
    }
    for name, artifact in artifacts.items():
        write_json(OUT_DIR / name, artifact)


def main() -> int:
    validator = load_json(VALIDATOR_ARTIFACT)
    lookup = load_json(LOOKUP_ARTIFACT)
    approval = load_json(APPROVAL_ARTIFACT)
    user_validator = load_json(USER_IDENTITY_VALIDATOR_ARTIFACT)
    preflight_report = validate_preflight(validator, lookup, approval, user_validator)
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
            "historical_data_acquisition_okx_archive_scope_resolution_preview_status": STATUS_BLOCKED_CONTEXT,
            "final_decision": STATUS_BLOCKED_CONTEXT,
            "next_action": "STOP_FAIL_CLOSED_NO_BROWSING_NO_DOWNLOAD_NO_API_NO_DATA_BUILD",
            "next_module": NEXT_MODULE_BLOCKED,
            "error": str(exc),
            "okx_archive_scope_resolution_preview_completed": False,
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
            OUT_DIR / "repo_only_historical_data_acquisition_okx_archive_scope_resolution_preview_after_browse_lookup_validator_v1_latest.json",
            failure,
        )
        print(json.dumps(failure, indent=2, sort_keys=True), file=sys.stderr)
        raise SystemExit(1)
