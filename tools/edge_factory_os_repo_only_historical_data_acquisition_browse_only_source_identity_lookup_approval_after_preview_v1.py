from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_approval_after_preview_v1"
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_approval_after_preview_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "731348a"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 664
EXPECTED_TRACKED_PYTHON_COUNT = 665

REQUESTED_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_approval_after_preview_v1.py"
NEXT_MODULE_LOOKUP = "edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_after_approval_v1.py"
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_"
    "approval_blocked_record_after_preview_v1.py"
)

BROWSE_PREVIEW_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_preview_after_user_identity_validator_v1"
    / "repo_only_historical_data_acquisition_browse_only_source_identity_lookup_preview_after_user_identity_validator_v1_latest.json"
)
USER_IDENTITY_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_user_supplied_source_identity_input_validator_after_approval_v1"
    / "repo_only_historical_data_acquisition_user_supplied_source_identity_input_validator_after_approval_v1_latest.json"
)
USER_IDENTITY_INPUT_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_user_supplied_source_identity_input_after_approval_v1"
    / "repo_only_historical_data_acquisition_user_supplied_source_identity_input_after_approval_v1_latest.json"
)
IDENTITY_APPROVAL_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_source_identity_resolution_approval_after_preview_v1"
    / "repo_only_historical_data_acquisition_source_identity_resolution_approval_after_preview_v1_latest.json"
)
SOURCE_VERIFICATION_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_external_or_additional_source_verification_after_approval_v1"
    / "repo_only_historical_data_acquisition_external_or_additional_source_verification_after_approval_v1_latest.json"
)
EXTERNAL_SOURCE_APPROVAL_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_external_or_additional_source_approval_after_preview_v1"
    / "repo_only_historical_data_acquisition_external_or_additional_source_approval_after_preview_v1_latest.json"
)

BROWSE_PREVIEW_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION"
)
USER_IDENTITY_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_USER_SUPPLIED_SOURCE_IDENTITY_VALIDATED_INCOMPLETE_"
    "BROWSE_ONLY_LOOKUP_PREVIEW_READY_NO_EXECUTION"
)
USER_IDENTITY_INPUT_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_USER_SUPPLIED_SOURCE_IDENTITY_CAPTURED_PENDING_VALIDATOR_NO_EXECUTION"
)
IDENTITY_APPROVAL_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_USER_SUPPLIED_SOURCE_IDENTITY_INPUT_APPROVED_NEXT_NO_EXECUTION"
)
SOURCE_VERIFICATION_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_SOURCE_VERIFICATION_INCONCLUSIVE_SOURCE_IDENTITY_REQUIRED_NO_EXECUTION"
)
EXTERNAL_APPROVAL_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_EXTERNAL_OR_ADDITIONAL_SOURCE_VERIFICATION_APPROVED_NEXT_NO_EXECUTION"
)
STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_APPROVED_NEXT_NO_EXECUTION"
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = "HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION"
EVIDENCE_AFTER = "HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_APPROVED_NEXT_NO_EXECUTION"
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"
EVIDENCE_CHAIN_POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
USER_APPROVAL_SCOPE = "APPROVAL_RECORD_ONLY_FOR_NEXT_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_NO_DOWNLOAD_NO_API_NO_DATA_BUILD"
OKX_MAIN_PAGE = "https://tr.okx.com/en/historical-data"
OKX_SAMPLE_ZIP = (
    "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/20260518/"
    "BTC-USDT-SWAP-candlesticks-2026-05-18.zip"
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
    "schema_apply_performed_now",
    "external_download_performed_now",
    "external_api_call_performed_now",
    "data_fetch_performed_now",
    "data_build_performed_now",
    "okx_browse_performed_now",
    "okx_download_performed_now",
    "okx_api_call_performed_now",
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


def require_no_forbidden_actions(record: Dict[str, Any], name: str) -> None:
    for key in [
        "approval_grants_browse_now",
        "approval_grants_okx_page_open_now",
        "approval_grants_okx_zip_download_now",
        "approval_grants_okx_api_now",
        "approval_grants_data_download_now",
        "approval_grants_data_fetch_now",
        "approval_grants_external_api_now",
        "approval_grants_data_build_now",
        "approval_grants_strategy_backtest_candidate_now",
        "approval_grants_runtime_capital_live_now",
        "approval_grants_generic_runner_now",
        "approval_grants_schema_config_now",
        "browse_execution_allowed_now",
        "source_verification_allowed_now",
        "okx_source_verified_now",
        "okx_official_status_verified_now",
        "full_3_to_4_year_coverage_proven_now",
        "source_manifest_proven_now",
        "provenance_report_proven_now",
        "okx_download_performed",
        "okx_api_call_performed",
        "okx_browse_performed",
        "okx_sample_zip_downloaded_now",
        "okx_main_page_browsed_now",
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
        if key in record:
            require_false(record.get(key), f"{name}.{key}")


def require_attention(record: Dict[str, Any], name: str) -> None:
    require_equal(record.get("active_p0_blocker_count"), 0, f"{name}.active_p0_blocker_count")
    require_equal(record.get("active_p1_attention_count"), 4, f"{name}.active_p1_attention_count")
    require_true(record.get("dormant_repo_attention_count_carried_forward"), f"{name}.dormant_carried")
    require_equal(record.get("dormant_repo_attention_count"), 716, f"{name}.dormant_repo_attention_count")


def validate_preflight(
    browse_preview: Dict[str, Any],
    user_validator: Dict[str, Any],
    user_input: Dict[str, Any],
    identity_approval: Dict[str, Any],
    source_verification: Dict[str, Any],
    external_approval: Dict[str, Any],
) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    status = run_git(["status", "--short"])
    require_equal(head, EXPECTED_HEAD, "head")
    validate_repo_status_allows_current_tool_only(status)

    require_equal(
        browse_preview.get("next_module"),
        REQUESTED_MODULE,
        "browse_preview.next_module",
        mismatch_status=STATUS_BLOCKED_NEXT_MODULE,
    )
    require_equal(
        browse_preview.get("historical_data_acquisition_browse_only_source_identity_lookup_preview_status"),
        BROWSE_PREVIEW_STATUS_PASS,
        "browse_preview.status",
    )
    require_true(browse_preview.get("browse_only_lookup_preview_completed"), "browse_preview.completed")
    require_true(browse_preview.get("browse_only_lookup_approval_required_next"), "browse_preview.approval_required_next")
    for key in [
        "browse_execution_allowed_now",
        "source_verification_allowed_now",
        "okx_source_verified_now",
        "okx_official_status_verified_now",
        "full_3_to_4_year_coverage_proven_now",
        "source_manifest_proven_now",
        "provenance_report_proven_now",
        "okx_download_performed",
        "okx_api_call_performed",
        "okx_browse_performed",
        "okx_sample_zip_downloaded_now",
        "okx_main_page_browsed_now",
        "acquisition_execution_allowed_now",
        "external_download_allowed_now",
        "external_api_allowed_now",
        "data_download_performed",
        "data_fetch_performed",
        "data_build_performed",
        "external_api_calls_performed",
    ]:
        require_false(browse_preview.get(key), f"browse_preview.{key}")
    require_equal(browse_preview.get("okx_main_page_to_check"), OKX_MAIN_PAGE, "browse_preview.okx_main_page")
    require_equal(browse_preview.get("okx_sample_zip_identity_to_check"), OKX_SAMPLE_ZIP, "browse_preview.okx_sample_zip")
    require_no_forbidden_actions(browse_preview, "browse_preview")
    require_attention(browse_preview, "browse_preview")

    require_equal(
        user_validator.get("historical_data_acquisition_user_supplied_source_identity_input_validator_status"),
        USER_IDENTITY_VALIDATOR_STATUS_PASS,
        "user_validator.status",
    )
    require_true(user_validator.get("user_supplied_source_identity_input_validated"), "user_validator.validated")
    require_no_forbidden_actions(user_validator, "user_validator")
    require_attention(user_validator, "user_validator")

    require_equal(
        user_input.get("historical_data_acquisition_user_supplied_source_identity_input_status"),
        USER_IDENTITY_INPUT_STATUS_PASS,
        "user_input.status",
    )
    require_no_forbidden_actions(user_input, "user_input")
    require_attention(user_input, "user_input")

    require_equal(
        identity_approval.get("historical_data_acquisition_source_identity_resolution_approval_status"),
        IDENTITY_APPROVAL_STATUS_PASS,
        "identity_approval.status",
    )
    require_no_forbidden_actions(identity_approval, "identity_approval")
    require_attention(identity_approval, "identity_approval")

    require_equal(
        source_verification.get("historical_data_acquisition_external_or_additional_source_verification_status"),
        SOURCE_VERIFICATION_STATUS_PASS,
        "source_verification.status",
    )
    require_no_forbidden_actions(source_verification, "source_verification")
    require_attention(source_verification, "source_verification")

    require_equal(
        external_approval.get("historical_data_acquisition_external_or_additional_source_approval_status"),
        EXTERNAL_APPROVAL_STATUS_PASS,
        "external_approval.status",
    )
    require_no_forbidden_actions(external_approval, "external_approval")
    require_attention(external_approval, "external_approval")

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
        "browse_preview_artifact": str(BROWSE_PREVIEW_ARTIFACT),
        "user_identity_validator_artifact": str(USER_IDENTITY_VALIDATOR_ARTIFACT),
        "user_identity_input_artifact": str(USER_IDENTITY_INPUT_ARTIFACT),
        "identity_approval_artifact": str(IDENTITY_APPROVAL_ARTIFACT),
        "source_verification_artifact": str(SOURCE_VERIFICATION_ARTIFACT),
        "external_source_approval_artifact": str(EXTERNAL_SOURCE_APPROVAL_ARTIFACT),
    }


def approval_sections(preflight: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "preview_context": {
            "browse_only_lookup_preview_completed": True,
            "okx_main_page_and_sample_zip_identity_recorded": True,
            "okx_source_still_not_verified": True,
            "okx_official_status_still_not_verified": True,
            "full_3_to_4_year_coverage_still_not_proven": True,
            "source_manifest_still_not_proven": True,
            "provenance_report_still_not_proven": True,
            "no_browse_download_api_build_occurred": True,
            "active_p1_attention_count": 4,
            "dormant_repo_attention_count": 716,
        },
        "approval_scope": {
            "approval_grants_approval_record_only": True,
            "approval_grants_browse_now": False,
            "approval_grants_future_browse_only_lookup_next": True,
            "approval_grants_okx_page_open_now": False,
            "approval_grants_okx_zip_download_now": False,
            "approval_grants_okx_api_now": False,
            "approval_grants_data_download_now": False,
            "approval_grants_data_fetch_now": False,
            "approval_grants_external_api_now": False,
            "approval_grants_data_build_now": False,
            "approval_grants_strategy_backtest_candidate_now": False,
            "approval_grants_runtime_capital_live_now": False,
            "approval_grants_generic_runner_now": False,
            "approval_grants_schema_config_now": False,
        },
        "future_browse_only_lookup_scope": {
            "future_module_may": [
                "open only the user-supplied OKX historical data page",
                "inspect visible page/source metadata",
                "inspect official OKX page/domain evidence",
                "inspect stated candlestick/OHLC/OHLCV availability",
                "inspect stated coverage start/end information",
                "inspect stated file format/archive/download pattern",
                "inspect stated instrument/market/symbol/timeframe information",
                "inspect visible timestamp/timezone/schema notes if present",
                "inspect visible terms/license/source notes if present",
                "record citations/notes/source identity facts",
            ],
            "future_module_must_not": [
                "download ZIP/files",
                "call OKX API",
                "scrape bulk data",
                "iterate archive URLs",
                "build data",
                "import/execute dormant repo modules",
                "run strategy/backtest/candidate",
                "touch runtime/capital/live",
                "approve generic runner",
                "create schema/config",
            ],
        },
        "future_required_artifacts": [
            "historical_browse_only_source_identity_lookup_report.json",
            "historical_okx_official_page_evidence_report.json",
            "historical_okx_candlestick_coverage_evidence_report.json",
            "historical_okx_archive_pattern_evidence_report.json",
            "historical_okx_terms_or_source_notes_report.json",
            "historical_browse_only_lookup_contract_compliance_report.json",
        ],
        "fail_closed_rules": [
            "source is not official or official status cannot be determined",
            "source page cannot be accessed",
            "1h candle availability is not shown",
            "coverage date range is unclear",
            "archive/export pattern is unclear",
            "API/download occurs without separate approval",
            "ZIP/file download occurs",
            "bulk scraping occurs",
            "source/license terms unclear",
            "fake/synthetic source identity is used",
            "strategy/backtest/candidate/runtime/live path is touched",
        ],
        "evidence_policy": {
            "before_approval": EVIDENCE_BEFORE,
            "after_approval": EVIDENCE_AFTER,
            "approval_is_not_browse_result": True,
            "approval_is_not_source_verification": True,
            "approval_is_not_data_evidence": True,
            "approval_is_not_source_manifest": True,
            "acquisition_execution_remains_blocked": True,
            "p1_remains_active_until_acquisition_and_historical_validator_closes_it": True,
        },
        "next_module_decision": {
            "if_approval_is_valid": NEXT_MODULE_LOOKUP,
            "if_approval_is_unsafe": NEXT_MODULE_BLOCKED,
            "do_not_choose_acquisition_execution_apply": True,
            "do_not_choose_data_download_fetch_api": True,
            "do_not_choose_strategy_research": True,
            "do_not_choose_candidate_backtest_runtime_live_capital": True,
        },
        "whole_system_preflight": preflight,
    }


def replacement_checks(payload: Dict[str, Any]) -> Dict[str, bool]:
    return {
        "preflight_passed": payload.get("whole_system_preflight_decision") == "PASS",
        "approval_record_created": payload.get("browse_only_lookup_approval_record_created") is True,
        "approval_scope_correct": (
            payload.get("approval_grants_approval_record_only") is True
            and payload.get("approval_grants_browse_now") is False
            and payload.get("approval_grants_future_browse_only_lookup_next") is True
        ),
        "next_lookup_eligible": payload.get("browse_only_lookup_eligible_next") is True,
        "no_browse_now": (
            payload.get("browse_execution_allowed_now") is False
            and payload.get("okx_browse_performed") is False
            and payload.get("okx_main_page_browsed_now") is False
        ),
        "no_download_fetch_api_build": (
            payload.get("okx_download_performed") is False
            and payload.get("okx_api_call_performed") is False
            and payload.get("okx_sample_zip_downloaded_now") is False
            and payload.get("data_download_performed") is False
            and payload.get("data_fetch_performed") is False
            and payload.get("data_build_performed") is False
            and payload.get("external_api_calls_performed") is False
        ),
        "generic_runner_blocked": payload.get("generic_runner_implementation_remains_blocked") is True,
        "schema_config_absent": payload.get("schema_or_config_created") is False,
        "loop_closed": payload.get("loop_remains_closed") is True,
        "next_module_allowed": payload.get("next_module") in {NEXT_MODULE_LOOKUP, NEXT_MODULE_BLOCKED},
    }


def build_payload(preflight: Dict[str, Any], sections: Dict[str, Any]) -> Dict[str, Any]:
    flags = dangerous_flags()
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_browse_only_source_identity_lookup_approval_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "RUN_SEPARATE_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_MODULE_NO_DOWNLOAD_NO_API_NO_DATA_BUILD",
        "next_module": NEXT_MODULE_LOOKUP,
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
        "prior_browse_only_lookup_preview_respected": True,
        "browse_only_lookup_approval_record_created": True,
        "user_browse_only_lookup_approval_present": True,
        "user_browse_only_lookup_approval_scope": USER_APPROVAL_SCOPE,
        "approval_grants_approval_record_only": True,
        "approval_grants_browse_now": False,
        "approval_grants_future_browse_only_lookup_next": True,
        "approval_grants_okx_page_open_now": False,
        "approval_grants_okx_zip_download_now": False,
        "approval_grants_okx_api_now": False,
        "approval_grants_data_download_now": False,
        "approval_grants_data_fetch_now": False,
        "approval_grants_external_api_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_strategy_backtest_candidate_now": False,
        "approval_grants_runtime_capital_live_now": False,
        "approval_grants_generic_runner_now": False,
        "approval_grants_schema_config_now": False,
        "browse_only_lookup_eligible_next": True,
        "okx_main_page_to_check": OKX_MAIN_PAGE,
        "okx_sample_zip_identity_to_check": OKX_SAMPLE_ZIP,
        "browse_execution_allowed_now": False,
        "source_verification_allowed_now": False,
        "okx_source_verified_now": False,
        "okx_official_status_verified_now": False,
        "full_3_to_4_year_coverage_proven_now": False,
        "source_manifest_proven_now": False,
        "provenance_report_proven_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "okx_sample_zip_downloaded_now": False,
        "okx_main_page_browsed_now": False,
        "acquisition_execution_allowed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "data_build_performed": False,
        "external_api_calls_performed": False,
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
        "current_evidence_chain_quality_before_approval": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_approval": EVIDENCE_AFTER,
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
        "derived_live_repo_post_check": "PASS_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_APPROVED_NEXT_NO_EXECUTION",
        "derived_live_repo_post_check_reason": (
            "approval record authorizes only the next separate browse-only source identity lookup for the user-supplied "
            "OKX page/source identity facts; this module performed no browse, OKX page open, source verification, "
            "download, fetch, API call, scraping, data build, strategy, runtime, capital, live, generic-runner, schema, "
            "config, old-route, profit, or tradable-edge action"
        ),
        "tracked_python_count_expectation": {
            "previous": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT,
        },
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "approval_sections": sections,
        "preflight": preflight,
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
        "prior_browse_only_lookup_preview_respected",
        "browse_only_lookup_approval_record_created",
        "user_browse_only_lookup_approval_present",
        "approval_grants_approval_record_only",
        "approval_grants_future_browse_only_lookup_next",
        "browse_only_lookup_eligible_next",
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
        "approval_grants_browse_now",
        "approval_grants_okx_page_open_now",
        "approval_grants_okx_zip_download_now",
        "approval_grants_okx_api_now",
        "approval_grants_data_download_now",
        "approval_grants_data_fetch_now",
        "approval_grants_external_api_now",
        "approval_grants_data_build_now",
        "approval_grants_strategy_backtest_candidate_now",
        "approval_grants_runtime_capital_live_now",
        "approval_grants_generic_runner_now",
        "approval_grants_schema_config_now",
        "browse_execution_allowed_now",
        "source_verification_allowed_now",
        "okx_source_verified_now",
        "okx_official_status_verified_now",
        "full_3_to_4_year_coverage_proven_now",
        "source_manifest_proven_now",
        "provenance_report_proven_now",
        "okx_download_performed",
        "okx_api_call_performed",
        "okx_browse_performed",
        "okx_sample_zip_downloaded_now",
        "okx_main_page_browsed_now",
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
    ]
    for key in required_true:
        require_true(payload.get(key), key)
    for key in required_false:
        require_false(payload.get(key), key)
    require_equal(
        payload.get("historical_data_acquisition_browse_only_source_identity_lookup_approval_status"),
        STATUS_PASS,
        "approval_status",
    )
    require_equal(payload.get("user_browse_only_lookup_approval_scope"), USER_APPROVAL_SCOPE, "approval_scope")
    require_equal(payload.get("final_decision"), EVIDENCE_AFTER, "final_decision")
    require_equal(payload.get("next_module"), NEXT_MODULE_LOOKUP, "next_module")
    require_equal(payload.get("okx_main_page_to_check"), OKX_MAIN_PAGE, "okx_main_page")
    require_equal(payload.get("okx_sample_zip_identity_to_check"), OKX_SAMPLE_ZIP, "okx_sample_zip")
    require_equal(payload.get("whole_system_preflight_decision"), "PASS", "preflight_decision")
    require_equal(payload.get("active_p0_blocker_count"), 0, "active_p0_blocker_count")
    require_equal(payload.get("active_p1_attention_count"), 4, "active_p1_attention_count")
    require_equal(payload.get("dormant_repo_attention_count"), 716, "dormant_repo_attention_count")
    require_equal(payload.get("planned_schema_files_existing_count"), 0, "planned_schema_files_existing_count")
    require_equal(payload.get("dangerous_flags_true_count"), 0, "dangerous_flags_true_count")
    require(all(value is False for value in payload["dangerous_flags"].values()), "dangerous flags must all be false")


def main() -> None:
    browse_preview = load_json(BROWSE_PREVIEW_ARTIFACT)
    user_validator = load_json(USER_IDENTITY_VALIDATOR_ARTIFACT)
    user_input = load_json(USER_IDENTITY_INPUT_ARTIFACT)
    identity_approval = load_json(IDENTITY_APPROVAL_ARTIFACT)
    source_verification = load_json(SOURCE_VERIFICATION_ARTIFACT)
    external_approval = load_json(EXTERNAL_SOURCE_APPROVAL_ARTIFACT)
    preflight = validate_preflight(
        browse_preview,
        user_validator,
        user_input,
        identity_approval,
        source_verification,
        external_approval,
    )
    sections = approval_sections(preflight)
    payload = build_payload(preflight, sections)
    validate_payload(payload)
    write_json(OUT_DIR / "historical_browse_only_source_identity_lookup_approval_report.json", payload)
    write_json(OUT_DIR / "historical_browse_only_source_identity_lookup_approval_sections.json", sections)
    write_json(
        OUT_DIR / "repo_only_historical_data_acquisition_browse_only_source_identity_lookup_approval_after_preview_v1_latest.json",
        payload,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
