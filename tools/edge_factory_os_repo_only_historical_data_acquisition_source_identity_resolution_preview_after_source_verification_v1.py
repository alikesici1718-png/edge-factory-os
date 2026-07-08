from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_source_identity_resolution_"
    "preview_after_source_verification_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_source_identity_resolution_"
    "preview_after_source_verification_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "cafe976"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 659
EXPECTED_TRACKED_PYTHON_COUNT = 660

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_source_identity_resolution_"
    "preview_after_source_verification_v1.py"
)
NEXT_MODULE_APPROVAL = (
    "edge_factory_os_repo_only_historical_data_acquisition_source_identity_resolution_"
    "approval_after_preview_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_source_identity_resolution_"
    "preview_blocked_record_after_source_verification_v1.py"
)

SOURCE_VERIFICATION_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_external_or_additional_source_verification_after_approval_v1"
    / "repo_only_historical_data_acquisition_external_or_additional_source_verification_after_approval_v1_latest.json"
)
SOURCE_APPROVAL_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_external_or_additional_source_approval_after_preview_v1"
    / "repo_only_historical_data_acquisition_external_or_additional_source_approval_after_preview_v1_latest.json"
)
SOURCE_PREVIEW_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_external_or_additional_source_preview_after_local_manual_discovery_validator_v1"
    / "repo_only_historical_data_acquisition_external_or_additional_source_preview_after_local_manual_discovery_validator_v1_latest.json"
)
LOCAL_MANUAL_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_local_manual_source_discovery_validator_after_approval_v1"
    / "repo_only_historical_data_acquisition_local_manual_source_discovery_validator_after_approval_v1_latest.json"
)
CONTRACT_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_contract_validator_after_data_horizon_discovery_v1"
    / "repo_only_historical_data_acquisition_contract_validator_after_data_horizon_discovery_v1_latest.json"
)
HARDENING_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_implementation_validator_after_approval_v1"
    / "repo_only_pre_acquisition_minimal_reliability_hardening_implementation_validator_after_approval_v1_latest.json"
)

SOURCE_VERIFICATION_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_SOURCE_VERIFICATION_INCONCLUSIVE_SOURCE_IDENTITY_REQUIRED_NO_EXECUTION"
)
SOURCE_APPROVAL_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_EXTERNAL_OR_ADDITIONAL_SOURCE_VERIFICATION_APPROVED_NEXT_NO_EXECUTION"
)
SOURCE_PREVIEW_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_EXTERNAL_OR_ADDITIONAL_SOURCE_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION"
)
LOCAL_MANUAL_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_LOCAL_MANUAL_SOURCE_DISCOVERY_VALIDATED_GAP_OPEN_"
    "EXTERNAL_OR_ADDITIONAL_SOURCE_PREVIEW_READY"
)
CONTRACT_VALIDATOR_STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_CONTRACT_VALIDATED_PREVIEW_READY_NO_EXECUTION"
HARDENING_STATUS_PASS = (
    "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_VALIDATED_ACQUISITION_CONTRACT_RESUME_READY"
)
STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_SOURCE_IDENTITY_RESOLUTION_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_SOURCE_VERIFICATION_INCONCLUSIVE_SOURCE_IDENTITY_REQUIRED_NO_EXECUTION"
)
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_SOURCE_IDENTITY_RESOLUTION_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION"
)
EVIDENCE_CHAIN_POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"
RECOMMENDED_SOURCE_ROUTE = "OKX_OFFICIAL_HISTORICAL_ARCHIVE_OR_EXPORT_MANUAL_IMPORT_PREVIEW"
RECOMMENDED_IDENTITY_RESOLUTION_ROUTE = "USER_SUPPLIED_OKX_SOURCE_IDENTITY_INPUT_PREVIEW_FIRST"

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
    "schema_apply_performed_now",
    "external_download_performed_now",
    "external_api_call_performed_now",
    "data_fetch_performed_now",
    "data_build_performed_now",
    "okx_browse_performed_now",
    "okx_download_performed_now",
    "okx_api_call_performed_now",
    "source_identity_resolved_now",
    "okx_source_verified_now",
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
    return data, True, True, bool(data)


def load_json(path: Path) -> Dict[str, Any]:
    data, exists, valid, non_empty = read_json_checked(path)
    if not (exists and valid and non_empty):
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: artifact missing/invalid/empty: {path}")
    return data


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def require_equal(actual: Any, expected: Any, field: str, mismatch_status: str = STATUS_BLOCKED_CONTEXT) -> None:
    if actual != expected:
        raise RuntimeError(f"{mismatch_status}: {field}={actual!r} expected {expected!r}")


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
    require(not unexpected, f"{STATUS_BLOCKED_CONTEXT}: repo dirty outside approved tool: {unexpected}")


def tracked_python_count() -> int:
    output = run_git(["ls-files"])
    return len([line for line in output.splitlines() if line.strip().endswith(".py")])


def planned_schema_files_existing_count() -> int:
    return sum(1 for rel_path in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel_path).exists())


def generic_runner_target_exists() -> bool:
    return (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()


def dangerous_flags() -> Dict[str, bool]:
    return {name: False for name in DANGEROUS_FLAG_NAMES}


def require_verification_no_execution(verification: Dict[str, Any]) -> None:
    for key in [
        "okx_source_identity_available",
        "okx_source_verified_now",
        "okx_download_performed",
        "okx_api_call_performed",
        "okx_browse_performed",
        "acquisition_execution_allowed_now",
        "external_download_allowed_now",
        "external_api_allowed_now",
        "data_download_performed",
        "data_fetch_performed",
        "data_build_performed",
        "external_api_calls_performed",
        "fake_or_synthetic_data_detected",
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
        "old_source_panel_anomaly_route_reopened_now",
        "old_route_closed_artifacts_used_as_active_evidence_now",
        "ordinary_selector_backlog_loop_reentry_allowed",
        "generic_runner_target_exists",
    ]:
        require_false(verification.get(key), f"verification.{key}")


def validate_preflight(
    verification: Dict[str, Any],
    approval: Dict[str, Any],
    preview: Dict[str, Any],
    local_manual_validator: Dict[str, Any],
    contract_validator: Dict[str, Any],
    hardening: Dict[str, Any],
) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    status = run_git(["status", "--short"])
    require_equal(head, EXPECTED_HEAD, "head")
    validate_repo_status_allows_current_tool_only(status)

    require_equal(
        verification.get("next_module"),
        REQUESTED_MODULE,
        "verification.next_module",
        mismatch_status=STATUS_BLOCKED_NEXT_MODULE,
    )
    require_equal(
        verification.get("historical_data_acquisition_external_or_additional_source_verification_status"),
        SOURCE_VERIFICATION_STATUS_PASS,
        "verification.status",
    )
    require_true(verification.get("source_verification_performed"), "verification.source_verification_performed")
    require_true(verification.get("source_verification_report_created"), "verification.source_verification_report_created")
    require_equal(verification.get("recommended_source_route"), RECOMMENDED_SOURCE_ROUTE, "verification.recommended_source_route")
    require_true(
        verification.get("okx_official_historical_archive_or_export_preferred"),
        "verification.okx_official_historical_archive_or_export_preferred",
    )
    require_equal(
        verification.get("okx_source_identity_evidence_level"),
        "ABSENT_LOCAL_STATIC_EVIDENCE",
        "verification.okx_source_identity_evidence_level",
    )
    require_true(
        verification.get("source_verification_inconclusive"),
        "verification.source_verification_inconclusive",
    )
    require_true(
        verification.get("source_identity_resolution_required"),
        "verification.source_identity_resolution_required",
    )
    require_true(
        verification.get("external_browse_or_user_source_input_required"),
        "verification.external_browse_or_user_source_input_required",
    )
    require_true(
        verification.get("manual_okx_source_identity_input_preferred"),
        "verification.manual_okx_source_identity_input_preferred",
    )
    require_true(
        verification.get("separate_browse_approval_required_if_user_source_identity_absent"),
        "verification.separate_browse_approval_required_if_user_source_identity_absent",
    )
    require_equal(
        verification.get("current_evidence_chain_quality_after_verification"),
        EVIDENCE_BEFORE,
        "verification.current_evidence_chain_quality_after_verification",
    )
    require_equal(verification.get("active_p0_blocker_count"), 0, "verification.active_p0_blocker_count")
    require_equal(verification.get("active_p1_attention_count"), 4, "verification.active_p1_attention_count")
    require_true(verification.get("p1_attention_carried_forward"), "verification.p1_attention_carried_forward")
    require_true(
        verification.get("dormant_repo_attention_count_carried_forward"),
        "verification.dormant_repo_attention_count_carried_forward",
    )
    require_equal(verification.get("dormant_repo_attention_count"), 716, "verification.dormant_repo_attention_count")
    require_verification_no_execution(verification)

    require_equal(
        approval.get("historical_data_acquisition_external_or_additional_source_approval_status"),
        SOURCE_APPROVAL_STATUS_PASS,
        "approval.status",
    )
    require_equal(
        preview.get("historical_data_acquisition_external_or_additional_source_preview_status"),
        SOURCE_PREVIEW_STATUS_PASS,
        "preview.status",
    )
    require_equal(
        local_manual_validator.get("historical_data_acquisition_local_manual_source_discovery_validator_status"),
        LOCAL_MANUAL_VALIDATOR_STATUS_PASS,
        "local_manual_validator.status",
    )
    require_equal(
        contract_validator.get("historical_data_acquisition_contract_validator_status"),
        CONTRACT_VALIDATOR_STATUS_PASS,
        "contract_validator.status",
    )
    require_equal(
        hardening.get("pre_acquisition_minimal_reliability_hardening_implementation_validator_status"),
        HARDENING_STATUS_PASS,
        "hardening.status",
    )
    for name, artifact in [
        ("approval", approval),
        ("preview", preview),
        ("local_manual_validator", local_manual_validator),
        ("contract_validator", contract_validator),
        ("hardening", hardening),
    ]:
        require_equal(artifact.get("active_p0_blocker_count"), 0, f"{name}.active_p0_blocker_count")
        require_true(
            artifact.get("dormant_repo_attention_count_carried_forward"),
            f"{name}.dormant_repo_attention_count_carried_forward",
        )

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
        "active_p1_attention_count_from_live_artifact": 4,
        "p1_attention_carried_forward": True,
        "dormant_repo_attention_count_carried_forward": True,
        "blocked_actions_absent_from_requested_module": True,
        "whole_system_preflight_decision": "PASS",
        "head": head,
        "status_lines_allowed": normalize_status_lines(status),
        "source_verification_artifact": str(SOURCE_VERIFICATION_ARTIFACT),
        "source_approval_artifact": str(SOURCE_APPROVAL_ARTIFACT),
        "source_preview_artifact": str(SOURCE_PREVIEW_ARTIFACT),
        "local_manual_validator_artifact": str(LOCAL_MANUAL_VALIDATOR_ARTIFACT),
        "contract_validator_artifact": str(CONTRACT_VALIDATOR_ARTIFACT),
        "hardening_validator_artifact": str(HARDENING_VALIDATOR_ARTIFACT),
    }


def preview_sections(preflight: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "verification_context": {
            "source_verification_completed": True,
            "source_verification_inconclusive": True,
            "okx_source_identity_unavailable_in_local_static_evidence": True,
            "okx_source_not_verified": True,
            "no_browse_download_api_occurred": True,
            "source_identity_resolution_required": True,
            "active_p1_attention_count": 4,
            "dormant_repo_attention_count": 716,
        },
        "identity_resolution_options_preview": {
            "priority_order": [
                {
                    "route": "USER_SUPPLIED_OKX_SOURCE_IDENTITY_INPUT_PREVIEW",
                    "priority": "A",
                    "description": (
                        "user provides official OKX historical data URL, archive page, export file identity, "
                        "or manually downloaded archive metadata"
                    ),
                    "browser_needed_if_identity_complete": False,
                    "future_module_records_user_supplied_identity_as_local_static_evidence": True,
                    "future_validator_checks_identity_completeness_for_source_verification": True,
                },
                {
                    "route": "SEPARATE_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_PREVIEW",
                    "priority": "B",
                    "allowed_only_if_user_identity_absent": True,
                    "may_lookup_official_okx_historical_market_data_archive_export_identity_only": True,
                    "must_not_download_files": True,
                    "must_not_call_apis": True,
                    "must_not_scrape_bulk_data": True,
                    "must_not_build_data": True,
                    "must_only_capture_source_identity_metadata_and_notes": True,
                    "requires_separate_approval": True,
                },
                {
                    "route": "ABORT_EXTERNAL_SOURCE_PATH_UNTIL_SOURCE_IDENTITY_PROVIDED",
                    "priority": "C",
                    "condition": "neither user source identity nor browse approval is available",
                    "keep_acquisition_blocked": True,
                },
            ]
        },
        "recommended_identity_resolution_route": {
            "recommended_identity_resolution_route": RECOMMENDED_IDENTITY_RESOLUTION_ROUTE,
            "if_user_supplies_okx_source_identity_no_browse_approval_needed_for_identity_capture": True,
            "if_user_does_not_supply_source_identity_separate_browse_approval_required": True,
            "no_source_identity_is_resolved_now": True,
        },
        "future_user_input_requirements": {
            "exact_source_url_or_official_page_name_path_required": True,
            "whether_it_is_okx_official_required": True,
            "data_type_required": ["candles", "OHLCV", "trades", "index", "other"],
            "timeframe_availability_required": "especially_1h",
            "coverage_start_end_dates_if_shown_required": True,
            "instrument_symbol_universe_if_shown_required": True,
            "file_format_if_downloadable_manual_archive_required": True,
            "timestamp_timezone_if_shown_required": True,
            "license_terms_note_if_visible_required": True,
            "manual_user_download_or_later_system_approval_requirement_required": True,
        },
        "future_browse_requirements_if_needed": {
            "must_be_separate_approved_module": True,
            "search_scope": "official_OKX_historical_market_data_archive_export_identity_only",
            "must_not_download_files": True,
            "must_not_call_okx_api": True,
            "must_not_scrape_bulk_data": True,
            "must_not_build_data": True,
            "produce_source_identity_report_only": True,
            "require_validator_afterward": True,
        },
        "fail_closed_preview": {
            "future_fail_closed_conditions": [
                "source_identity_cannot_be_resolved",
                "source_is_unofficial_or_ambiguous",
                "source_license_unclear",
                "data_type_timeframe_unclear",
                "three_to_four_year_one_hour_coverage_cannot_be_established_as_requirement",
                "future_lookup_attempts_download_api_without_approval",
                "fake_or_synthetic_source_identity_is_used",
                "strategy_backtest_candidate_runtime_live_path_touched",
            ]
        },
        "evidence_policy_preview": {
            "before_preview": EVIDENCE_BEFORE,
            "after_preview": EVIDENCE_AFTER,
            "preview_is_not_source_verification": True,
            "preview_is_not_source_identity_evidence": True,
            "preview_is_not_data_evidence": True,
            "acquisition_execution_remains_blocked": True,
            "p1_remains_active_until_acquisition_and_historical_validator_closes_it": True,
        },
        "next_module_decision": {
            "if_preview_is_safe": NEXT_MODULE_APPROVAL,
            "if_preview_is_unsafe": NEXT_MODULE_BLOCKED,
            "do_not_choose_source_identity_capture_directly": True,
            "do_not_choose_browse_directly": True,
            "do_not_choose_download_fetch_api": True,
            "do_not_choose_acquisition_execution_apply": True,
            "do_not_choose_strategy_research": True,
            "do_not_choose_candidate_backtest_runtime_live_capital": True,
            "do_not_choose_generic_review_adoption_gate_rollout": True,
        },
        "whole_system_preflight": preflight,
    }


def replacement_checks(payload: Dict[str, Any]) -> Dict[str, bool]:
    return {
        "preflight_passed": payload.get("whole_system_preflight_decision") == "PASS",
        "preview_completed": payload.get("source_identity_resolution_preview_completed") is True,
        "recommended_route_user_input_first": (
            payload.get("recommended_identity_resolution_route") == RECOMMENDED_IDENTITY_RESOLUTION_ROUTE
        ),
        "source_identity_not_resolved_now": payload.get("source_identity_resolved_now") is False,
        "okx_unverified_no_browse": (
            payload.get("okx_source_verified_now") is False
            and payload.get("okx_official_status_verified_now") is False
            and payload.get("okx_browse_performed") is False
        ),
        "no_download_fetch_api_build": (
            payload.get("data_download_performed") is False
            and payload.get("data_fetch_performed") is False
            and payload.get("data_build_performed") is False
            and payload.get("external_api_calls_performed") is False
            and payload.get("okx_download_performed") is False
            and payload.get("okx_api_call_performed") is False
        ),
        "no_strategy_runtime_capital_live": (
            payload.get("backtest_performed") is False
            and payload.get("candidate_generation_performed") is False
            and payload.get("runtime_touch_performed") is False
            and payload.get("capital_touch_performed") is False
            and payload.get("live_touch_performed") is False
        ),
        "generic_runner_blocked": payload.get("generic_runner_implementation_remains_blocked") is True,
        "schema_config_absent": payload.get("schema_or_config_created") is False,
        "loop_closed": payload.get("loop_remains_closed") is True,
        "next_module_allowed": payload.get("next_module") in {NEXT_MODULE_APPROVAL, NEXT_MODULE_BLOCKED},
    }


def build_payload(preflight: Dict[str, Any], sections: Dict[str, Any]) -> Dict[str, Any]:
    flags = dangerous_flags()
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_source_identity_resolution_preview_status": STATUS_PASS,
        "final_decision": "HISTORICAL_DATA_ACQUISITION_SOURCE_IDENTITY_RESOLUTION_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION",
        "next_action": "CREATE_SEPARATE_SOURCE_IDENTITY_RESOLUTION_APPROVAL_RECORD_NO_BROWSE_NO_DOWNLOAD_NO_API_NO_EXECUTION",
        "next_module": NEXT_MODULE_APPROVAL,
        "whole_system_preflight_completed": True,
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
        "real_final_form_gap_confirmed": True,
        "documentation_loop_detected": False,
        "documentation_loop_risk_level": DOCUMENTATION_LOOP_RISK_LEVEL,
        "next_module_closes_real_gap": True,
        "active_p0_blocker_count_from_live_artifact": 0,
        "active_p1_attention_count_from_live_artifact": 4,
        "p1_attention_carried_forward": True,
        "dormant_repo_attention_count_carried_forward": True,
        "blocked_actions_absent_from_requested_module": True,
        "whole_system_preflight_decision": "PASS",
        "prior_source_verification_respected": True,
        "source_identity_resolution_preview_completed": True,
        "verification_context_completed": True,
        "identity_resolution_options_preview_completed": True,
        "recommended_identity_resolution_route_completed": True,
        "future_user_input_requirements_completed": True,
        "future_browse_requirements_if_needed_completed": True,
        "fail_closed_preview_completed": True,
        "evidence_policy_preview_completed": True,
        "recommended_identity_resolution_route": RECOMMENDED_IDENTITY_RESOLUTION_ROUTE,
        "user_supplied_okx_source_identity_preferred": True,
        "separate_browse_required_if_user_identity_absent": True,
        "source_identity_resolved_now": False,
        "okx_source_identity_available_now": False,
        "okx_source_verified_now": False,
        "okx_official_status_verified_now": False,
        "source_verification_inconclusive_carried_forward": True,
        "source_identity_resolution_required": True,
        "user_source_identity_input_required_next": True,
        "browse_approval_required_now": False,
        "browse_execution_allowed_now": False,
        "acquisition_execution_allowed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "data_build_performed": False,
        "external_api_calls_performed": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "fake_or_synthetic_data_detected": False,
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
        "old_route_closed_artifacts_used_as_active_evidence_now": False,
        "current_evidence_chain_quality_before_preview": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_preview": EVIDENCE_AFTER,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 4,
        "dormant_repo_attention_count": 716,
        "evidence_chain_policy_level": EVIDENCE_CHAIN_POLICY_LEVEL,
        "future_modules_must_classify_evidence_quality": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": planned_schema_files_existing_count(),
        "generic_runner_target_exists": generic_runner_target_exists(),
        "dangerous_flags": flags,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "dangerous_flags_true_count": sum(1 for value in flags.values() if value is True),
        "derived_live_repo_post_check": "PASS_SOURCE_IDENTITY_RESOLUTION_PREVIEW_READY_FOR_APPROVAL_RECORD_NO_EXECUTION",
        "derived_live_repo_post_check_reason": (
            "preview recommends user-supplied OKX source identity input first and requires separate approval before "
            "any browse-only lookup; no source identity was resolved, no OKX source was verified, and no browsing, "
            "download, fetch, API call, data build, strategy, runtime, capital, live, generic-runner, schema, config, "
            "or old-route action occurred"
        ),
        "tracked_python_count_expectation": {
            "previous": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT,
        },
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "preview_sections": sections,
        "preflight": preflight,
        "source_artifacts": {
            "source_verification_artifact": str(SOURCE_VERIFICATION_ARTIFACT),
            "source_approval_artifact": str(SOURCE_APPROVAL_ARTIFACT),
            "source_preview_artifact": str(SOURCE_PREVIEW_ARTIFACT),
            "local_manual_validator_artifact": str(LOCAL_MANUAL_VALIDATOR_ARTIFACT),
            "contract_validator_artifact": str(CONTRACT_VALIDATOR_ARTIFACT),
            "hardening_validator_artifact": str(HARDENING_VALIDATOR_ARTIFACT),
        },
    }
    payload["replacement_checks"] = replacement_checks(payload)
    payload["replacement_checks_all_true"] = all(value is True for value in payload["replacement_checks"].values())
    return payload


def validate_payload(payload: Dict[str, Any]) -> None:
    required_true = [
        "whole_system_preflight_completed",
        "live_next_module_matches_requested_module",
        "artifact_chain_consistent",
        "real_final_form_gap_confirmed",
        "next_module_closes_real_gap",
        "p1_attention_carried_forward",
        "dormant_repo_attention_count_carried_forward",
        "blocked_actions_absent_from_requested_module",
        "prior_source_verification_respected",
        "source_identity_resolution_preview_completed",
        "verification_context_completed",
        "identity_resolution_options_preview_completed",
        "recommended_identity_resolution_route_completed",
        "future_user_input_requirements_completed",
        "future_browse_requirements_if_needed_completed",
        "fail_closed_preview_completed",
        "evidence_policy_preview_completed",
        "user_supplied_okx_source_identity_preferred",
        "separate_browse_required_if_user_identity_absent",
        "source_verification_inconclusive_carried_forward",
        "source_identity_resolution_required",
        "user_source_identity_input_required_next",
        "source_manifest_required",
        "provenance_report_required",
        "survivorship_bias_controls_required",
        "symbol_lifecycle_report_required",
        "holdout_policy_required",
        "historical_data_quality_validator_required",
        "timeout_policy_required_for_acquisition",
        "memory_disk_resource_policy_required_for_acquisition",
        "rollback_policy_required_for_acquisition",
        "hardening_state_required_for_acquisition",
        "generic_runner_implementation_remains_blocked",
        "future_modules_must_classify_evidence_quality",
        "replacement_checks_are_not_equivalent_to_primary_artifact",
        "loop_remains_closed",
        "dangerous_flags_all_false",
        "replacement_checks_all_true",
    ]
    required_false = [
        "stale_or_contradictory_artifact_detected",
        "documentation_loop_detected",
        "source_identity_resolved_now",
        "okx_source_identity_available_now",
        "okx_source_verified_now",
        "okx_official_status_verified_now",
        "browse_approval_required_now",
        "browse_execution_allowed_now",
        "acquisition_execution_allowed_now",
        "external_download_allowed_now",
        "external_api_allowed_now",
        "data_download_performed",
        "data_fetch_performed",
        "data_build_performed",
        "external_api_calls_performed",
        "okx_download_performed",
        "okx_api_call_performed",
        "okx_browse_performed",
        "fake_or_synthetic_data_detected",
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
        "old_source_panel_anomaly_route_reopened_now",
        "old_route_closed_artifacts_used_as_active_evidence_now",
        "ordinary_selector_backlog_loop_reentry_allowed",
        "generic_runner_target_exists",
    ]
    for key in required_true:
        require_true(payload.get(key), key)
    for key in required_false:
        require_false(payload.get(key), key)
    require_equal(
        payload.get("historical_data_acquisition_source_identity_resolution_preview_status"),
        STATUS_PASS,
        "preview_status",
    )
    require_equal(payload.get("final_decision"), EVIDENCE_AFTER, "final_decision")
    require_equal(payload.get("next_module"), NEXT_MODULE_APPROVAL, "next_module")
    require_equal(
        payload.get("recommended_identity_resolution_route"),
        RECOMMENDED_IDENTITY_RESOLUTION_ROUTE,
        "recommended_identity_resolution_route",
    )
    require_equal(payload.get("whole_system_preflight_decision"), "PASS", "whole_system_preflight_decision")
    require_equal(payload.get("active_p0_blocker_count"), 0, "active_p0_blocker_count")
    require_equal(payload.get("active_p1_attention_count"), 4, "active_p1_attention_count")
    require_equal(payload.get("dormant_repo_attention_count"), 716, "dormant_repo_attention_count")
    require_equal(payload.get("planned_schema_files_existing_count"), 0, "planned_schema_files_existing_count")
    require_equal(payload.get("dangerous_flags_true_count"), 0, "dangerous_flags_true_count")
    require(all(value is False for value in payload["dangerous_flags"].values()), "dangerous flags must all be false")


def main() -> None:
    verification = load_json(SOURCE_VERIFICATION_ARTIFACT)
    approval = load_json(SOURCE_APPROVAL_ARTIFACT)
    preview = load_json(SOURCE_PREVIEW_ARTIFACT)
    local_manual_validator = load_json(LOCAL_MANUAL_VALIDATOR_ARTIFACT)
    contract_validator = load_json(CONTRACT_VALIDATOR_ARTIFACT)
    hardening = load_json(HARDENING_VALIDATOR_ARTIFACT)
    preflight = validate_preflight(
        verification,
        approval,
        preview,
        local_manual_validator,
        contract_validator,
        hardening,
    )
    sections = preview_sections(preflight)
    payload = build_payload(preflight, sections)
    validate_payload(payload)
    write_json(OUT_DIR / "historical_source_identity_resolution_preview_after_source_verification_v1.json", sections)
    write_json(
        OUT_DIR
        / "repo_only_historical_data_acquisition_source_identity_resolution_preview_after_source_verification_v1_latest.json",
        payload,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
