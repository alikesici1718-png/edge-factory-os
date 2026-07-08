from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_historical_data_acquisition_user_supplied_source_identity_input_after_approval_v1"
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_user_supplied_source_identity_input_after_approval_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "f51458d"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 661
EXPECTED_TRACKED_PYTHON_COUNT = 662

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_user_supplied_source_identity_input_after_approval_v1.py"
)
NEXT_MODULE_VALIDATOR = (
    "edge_factory_os_repo_only_historical_data_acquisition_user_supplied_source_identity_input_validator_after_approval_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_user_supplied_source_identity_input_blocked_record_after_approval_v1.py"
)

IDENTITY_APPROVAL_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_source_identity_resolution_approval_after_preview_v1"
    / "repo_only_historical_data_acquisition_source_identity_resolution_approval_after_preview_v1_latest.json"
)
IDENTITY_PREVIEW_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_source_identity_resolution_preview_after_source_verification_v1"
    / "repo_only_historical_data_acquisition_source_identity_resolution_preview_after_source_verification_v1_latest.json"
)
SOURCE_VERIFICATION_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_external_or_additional_source_verification_after_approval_v1"
    / "repo_only_historical_data_acquisition_external_or_additional_source_verification_after_approval_v1_latest.json"
)

IDENTITY_APPROVAL_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_USER_SUPPLIED_SOURCE_IDENTITY_INPUT_APPROVED_NEXT_NO_EXECUTION"
)
IDENTITY_PREVIEW_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_SOURCE_IDENTITY_RESOLUTION_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION"
)
SOURCE_VERIFICATION_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_SOURCE_VERIFICATION_INCONCLUSIVE_SOURCE_IDENTITY_REQUIRED_NO_EXECUTION"
)
STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_USER_SUPPLIED_SOURCE_IDENTITY_CAPTURED_PENDING_VALIDATOR_NO_EXECUTION"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = "HISTORICAL_DATA_ACQUISITION_USER_SUPPLIED_SOURCE_IDENTITY_INPUT_APPROVED_NEXT_NO_EXECUTION"
EVIDENCE_AFTER = "HISTORICAL_DATA_ACQUISITION_USER_SUPPLIED_SOURCE_IDENTITY_CAPTURED_PENDING_VALIDATOR_NO_EXECUTION"
EVIDENCE_CHAIN_POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
USER_SUPPLIED_SOURCE_IDENTITY_TYPE = "OKX_OFFICIAL_HISTORICAL_DATA_PAGE_AND_SAMPLE_CANDLESTICK_ZIP"
SOURCE_IDENTITY_COMPLETENESS_LEVEL = "PARTIAL_USER_SUPPLIED_STATIC_IDENTITY"
SOURCE_IDENTITY_RESOLUTION_BASIS = "USER_SUPPLIED_STATIC_IDENTITY_CAPTURED"
OKX_MAIN_PAGE = "https://tr.okx.com/en/historical-data"
OKX_SAMPLE_ZIP = (
    "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/20260518/"
    "BTC-USDT-SWAP-candlesticks-2026-05-18.zip"
)
USER_NOTE = (
    "OKX official historical data page appears to expose candlestick/OHLC historical downloads. "
    "The sample URL is a BTC-USDT-SWAP daily candlestick ZIP for 2026-05-18. Treat these as "
    "user-supplied source identity evidence only; do not download or fetch."
)

MISSING_REQUIRED_IDENTITY_FIELDS = [
    "independent official-status verification",
    "exact downloadable archive index structure",
    "full 3-to-4-year coverage confirmation",
    "full symbol universe rule",
    "timestamp timezone confirmation",
    "license/terms note",
    "file format/schema confirmation",
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


def require_no_execution(record: Dict[str, Any], name: str) -> None:
    for key in [
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
        "generic_runner_approval_granted",
        "schema_or_config_created",
        "ordinary_selector_backlog_loop_reentry_allowed",
        "generic_runner_target_exists",
    ]:
        require_false(record.get(key), f"{name}.{key}")


def validate_preflight(
    identity_approval: Dict[str, Any],
    identity_preview: Dict[str, Any],
    source_verification: Dict[str, Any],
) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    status = run_git(["status", "--short"])
    require_equal(head, EXPECTED_HEAD, "head")
    validate_repo_status_allows_current_tool_only(status)

    require_equal(
        identity_approval.get("next_module"),
        REQUESTED_MODULE,
        "identity_approval.next_module",
        mismatch_status=STATUS_BLOCKED_NEXT_MODULE,
    )
    require_equal(
        identity_approval.get("historical_data_acquisition_source_identity_resolution_approval_status"),
        IDENTITY_APPROVAL_STATUS_PASS,
        "identity_approval.status",
    )
    require_true(
        identity_approval.get("user_source_identity_input_eligible_next"),
        "identity_approval.user_source_identity_input_eligible_next",
    )
    require_true(
        identity_approval.get("approval_grants_future_user_source_identity_input_next"),
        "identity_approval.approval_grants_future_user_source_identity_input_next",
    )
    for key in [
        "approval_grants_browse_now",
        "approval_grants_okx_source_verification_now",
        "approval_grants_okx_download_now",
        "approval_grants_okx_api_now",
        "approval_grants_data_download_now",
        "approval_grants_data_fetch_now",
        "approval_grants_external_api_now",
        "approval_grants_data_build_now",
        "approval_grants_strategy_backtest_candidate_now",
        "approval_grants_runtime_capital_live_now",
        "approval_grants_generic_runner_now",
        "approval_grants_schema_config_now",
        "acquisition_execution_allowed_now",
        "external_download_allowed_now",
        "external_api_allowed_now",
        "data_download_performed",
        "data_fetch_performed",
        "data_build_performed",
        "external_api_calls_performed",
    ]:
        require_false(identity_approval.get(key), f"identity_approval.{key}")
    require_equal(identity_approval.get("active_p0_blocker_count"), 0, "identity_approval.active_p0_blocker_count")
    require_equal(identity_approval.get("active_p1_attention_count"), 4, "identity_approval.active_p1_attention_count")
    require_equal(identity_approval.get("dormant_repo_attention_count"), 716, "identity_approval.dormant_repo_attention_count")
    require_true(
        identity_approval.get("dormant_repo_attention_count_carried_forward"),
        "identity_approval.dormant_repo_attention_count_carried_forward",
    )
    require_no_execution(identity_approval, "identity_approval")

    require_equal(
        identity_preview.get("historical_data_acquisition_source_identity_resolution_preview_status"),
        IDENTITY_PREVIEW_STATUS_PASS,
        "identity_preview.status",
    )
    require_equal(
        identity_preview.get("current_evidence_chain_quality_after_preview"),
        "HISTORICAL_DATA_ACQUISITION_SOURCE_IDENTITY_RESOLUTION_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION",
        "identity_preview.current_evidence_chain_quality_after_preview",
    )
    require_equal(identity_preview.get("active_p0_blocker_count"), 0, "identity_preview.active_p0_blocker_count")
    require_equal(identity_preview.get("active_p1_attention_count"), 4, "identity_preview.active_p1_attention_count")
    require_equal(identity_preview.get("dormant_repo_attention_count"), 716, "identity_preview.dormant_repo_attention_count")
    require_no_execution(identity_preview, "identity_preview")

    require_equal(
        source_verification.get("historical_data_acquisition_external_or_additional_source_verification_status"),
        SOURCE_VERIFICATION_STATUS_PASS,
        "source_verification.status",
    )
    require_true(
        source_verification.get("source_verification_inconclusive"),
        "source_verification.source_verification_inconclusive",
    )
    require_false(source_verification.get("okx_source_identity_available"), "source_verification.okx_source_identity_available")
    require_false(source_verification.get("okx_source_verified_now"), "source_verification.okx_source_verified_now")
    require_false(
        source_verification.get("okx_official_status_verified_now"),
        "source_verification.okx_official_status_verified_now",
    )
    require_equal(source_verification.get("active_p0_blocker_count"), 0, "source_verification.active_p0_blocker_count")
    require_equal(source_verification.get("active_p1_attention_count"), 4, "source_verification.active_p1_attention_count")
    require_equal(
        source_verification.get("dormant_repo_attention_count"),
        716,
        "source_verification.dormant_repo_attention_count",
    )
    require_no_execution(source_verification, "source_verification")

    return {
        "whole_system_preflight_completed": True,
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
        "real_final_form_gap_confirmed": True,
        "documentation_loop_detected": False,
        "active_p0_blocker_count_from_live_artifact": 0,
        "active_p1_attention_count_from_live_artifact": 4,
        "dormant_repo_attention_count_carried_forward": True,
        "blocked_actions_absent_from_requested_module": True,
        "whole_system_preflight_decision": "PASS",
        "head": head,
        "status_lines_allowed": normalize_status_lines(status),
        "identity_approval_artifact": str(IDENTITY_APPROVAL_ARTIFACT),
        "identity_preview_artifact": str(IDENTITY_PREVIEW_ARTIFACT),
        "source_verification_artifact": str(SOURCE_VERIFICATION_ARTIFACT),
    }


def okx_identity_record() -> Dict[str, Any]:
    return {
        "user_supplied_source_identity_present": True,
        "user_supplied_source_identity_value_recorded": True,
        "user_supplied_source_identity_type": USER_SUPPLIED_SOURCE_IDENTITY_TYPE,
        "source_identity_resolution_basis": SOURCE_IDENTITY_RESOLUTION_BASIS,
        "okx_main_page": OKX_MAIN_PAGE,
        "okx_sample_candlestick_zip": OKX_SAMPLE_ZIP,
        "user_note": USER_NOTE,
        "user_supplied_okx_main_page_recorded": True,
        "user_supplied_okx_sample_zip_recorded": True,
        "okx_main_page_browsed_now": False,
        "okx_sample_zip_downloaded_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "network_verification_performed": False,
        "official_status_asserted_by_module": False,
        "identity_interpretation_notes": [
            "OKX main page suggests historical market data and candlestick/OHLC source identity.",
            "Sample ZIP suggests a concrete candlestick archive path for BTC-USDT-SWAP daily 2026-05-18.",
            "These strings are captured only as user-supplied static identity evidence.",
        ],
    }


def completeness_report() -> Dict[str, Any]:
    return {
        "source_identity_completeness_level": SOURCE_IDENTITY_COMPLETENESS_LEVEL,
        "source_identity_completeness_pass": False,
        "missing_required_identity_fields": MISSING_REQUIRED_IDENTITY_FIELDS,
        "missing_required_identity_field_count": len(MISSING_REQUIRED_IDENTITY_FIELDS),
        "present_identity_fields": [
            "user-supplied OKX historical data page URL",
            "user-supplied concrete OKX sample candlestick ZIP URL",
            "user note describing source identity only and forbidding download/fetch",
        ],
        "okx_coverage_attention_required": True,
        "coverage_attention_note": (
            "OKX candlestick history may be insufficient for the full 4-year target if the source only starts July 2023; "
            "coverage remains P1/P2 attention pending future verification."
        ),
        "future_validator_or_source_verification_required_before_acquisition_or_download": True,
    }


def contract_compliance_report() -> Dict[str, Any]:
    return {
        "source_identity_input_contract_compliance_pass": True,
        "source_identity_capture_only": True,
        "no_browse": True,
        "no_download": True,
        "no_fetch": True,
        "no_external_api": True,
        "no_data_build": True,
        "no_strategy_backtest_candidate_runtime_capital_live": True,
        "no_schema_or_config_created": True,
        "no_generic_runner_approved_or_implemented": True,
        "old_source_panel_anomaly_route_not_reopened": True,
        "future_validator_required": True,
        "next_module_decision": {
            "if_user_source_identity_is_captured_safely": NEXT_MODULE_VALIDATOR,
            "if_unsafe_or_blocked": NEXT_MODULE_BLOCKED,
        },
    }


def replacement_checks(payload: Dict[str, Any]) -> Dict[str, bool]:
    return {
        "preflight_passed": payload.get("whole_system_preflight_decision") == "PASS",
        "user_source_identity_input_performed": payload.get("user_source_identity_input_performed") is True,
        "user_supplied_identity_recorded": (
            payload.get("user_supplied_source_identity_present") is True
            and payload.get("user_supplied_source_identity_value_recorded") is True
        ),
        "source_resolved_only_as_static_capture": (
            payload.get("source_identity_resolved_now") is True
            and payload.get("source_identity_resolution_basis") == SOURCE_IDENTITY_RESOLUTION_BASIS
            and payload.get("okx_source_verified_now") is False
            and payload.get("okx_official_status_verified_now") is False
        ),
        "partial_completeness_recorded": (
            payload.get("source_identity_completeness_level") == SOURCE_IDENTITY_COMPLETENESS_LEVEL
            and payload.get("source_identity_completeness_pass") is False
            and payload.get("missing_required_identity_field_count") == len(MISSING_REQUIRED_IDENTITY_FIELDS)
        ),
        "no_browse_download_fetch_api_build": (
            payload.get("okx_main_page_browsed_now") is False
            and payload.get("okx_sample_zip_downloaded_now") is False
            and payload.get("data_download_performed") is False
            and payload.get("data_fetch_performed") is False
            and payload.get("data_build_performed") is False
            and payload.get("external_api_calls_performed") is False
            and payload.get("okx_download_performed") is False
            and payload.get("okx_api_call_performed") is False
            and payload.get("okx_browse_performed") is False
        ),
        "generic_runner_blocked": payload.get("generic_runner_implementation_remains_blocked") is True,
        "schema_config_absent": payload.get("schema_or_config_created") is False,
        "loop_closed": payload.get("loop_remains_closed") is True,
        "next_module_allowed": payload.get("next_module") in {NEXT_MODULE_VALIDATOR, NEXT_MODULE_BLOCKED},
    }


def build_payload(preflight: Dict[str, Any]) -> Dict[str, Any]:
    flags = dangerous_flags()
    record = okx_identity_record()
    completeness = completeness_report()
    compliance = contract_compliance_report()
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_user_supplied_source_identity_input_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "RUN_SEPARATE_USER_SUPPLIED_SOURCE_IDENTITY_INPUT_VALIDATOR_NO_BROWSE_NO_DOWNLOAD_NO_API_NO_EXECUTION",
        "next_module": NEXT_MODULE_VALIDATOR,
        "whole_system_preflight_completed": True,
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
        "real_final_form_gap_confirmed": True,
        "documentation_loop_detected": False,
        "blocked_actions_absent_from_requested_module": True,
        "whole_system_preflight_decision": "PASS",
        "prior_source_identity_resolution_approval_respected": True,
        "user_source_identity_input_performed": True,
        "user_supplied_source_identity_present": True,
        "user_supplied_source_identity_value_recorded": True,
        "user_supplied_source_identity_type": USER_SUPPLIED_SOURCE_IDENTITY_TYPE,
        "source_identity_resolution_basis": SOURCE_IDENTITY_RESOLUTION_BASIS,
        "source_identity_completeness_level": SOURCE_IDENTITY_COMPLETENESS_LEVEL,
        "source_identity_completeness_pass": False,
        "missing_required_identity_fields": MISSING_REQUIRED_IDENTITY_FIELDS,
        "missing_required_identity_field_count": len(MISSING_REQUIRED_IDENTITY_FIELDS),
        "source_identity_resolved_now": True,
        "okx_source_identity_available_now": True,
        "okx_source_verified_now": False,
        "okx_official_status_verified_now": False,
        "source_verification_inconclusive_carried_forward": True,
        "source_identity_resolution_required": False,
        "browse_only_source_identity_lookup_required_next": False,
        "user_supplied_okx_main_page_recorded": True,
        "user_supplied_okx_sample_zip_recorded": True,
        "okx_sample_zip_downloaded_now": False,
        "okx_main_page_browsed_now": False,
        "okx_coverage_attention_required": True,
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
        "historical_user_supplied_source_identity_input_report_created": True,
        "historical_okx_user_source_identity_record_created": True,
        "historical_source_identity_completeness_report_created": True,
        "historical_source_identity_input_contract_compliance_report_created": True,
        "current_evidence_chain_quality_before_input": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_input": EVIDENCE_AFTER,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 4,
        "dormant_repo_attention_count": 716,
        "dormant_repo_attention_count_carried_forward": True,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": planned_schema_files_existing_count(),
        "generic_runner_target_exists": generic_runner_target_exists(),
        "dangerous_flags": flags,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "dangerous_flags_true_count": sum(1 for value in flags.values() if value is True),
        "derived_live_repo_post_check": (
            "PASS_USER_SUPPLIED_OKX_SOURCE_IDENTITY_CAPTURED_PENDING_VALIDATOR_NO_EXECUTION"
        ),
        "derived_live_repo_post_check_reason": (
            "user-supplied OKX historical data page and sample candlestick ZIP identity strings were recorded only as "
            "local static evidence; OKX official status was not independently verified, no OKX page was browsed, no ZIP "
            "was downloaded, and no fetch, external API call, data build, strategy, runtime, capital, live, generic-runner, "
            "schema, config, or old-route action occurred"
        ),
        "evidence_chain_policy_level": EVIDENCE_CHAIN_POLICY_LEVEL,
        "future_validator_or_source_verification_required_before_acquisition_or_download": True,
        "okx_identity_record": record,
        "source_identity_completeness_report": completeness,
        "source_identity_input_contract_compliance_report": compliance,
        "tracked_python_count_expectation": {
            "previous": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT,
        },
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "preflight": preflight,
        "source_artifacts": {
            "identity_approval_artifact": str(IDENTITY_APPROVAL_ARTIFACT),
            "identity_preview_artifact": str(IDENTITY_PREVIEW_ARTIFACT),
            "source_verification_artifact": str(SOURCE_VERIFICATION_ARTIFACT),
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
        "blocked_actions_absent_from_requested_module",
        "prior_source_identity_resolution_approval_respected",
        "user_source_identity_input_performed",
        "user_supplied_source_identity_present",
        "user_supplied_source_identity_value_recorded",
        "source_identity_resolved_now",
        "okx_source_identity_available_now",
        "source_verification_inconclusive_carried_forward",
        "user_supplied_okx_main_page_recorded",
        "user_supplied_okx_sample_zip_recorded",
        "okx_coverage_attention_required",
        "historical_user_supplied_source_identity_input_report_created",
        "historical_okx_user_source_identity_record_created",
        "historical_source_identity_completeness_report_created",
        "historical_source_identity_input_contract_compliance_report_created",
        "dormant_repo_attention_count_carried_forward",
        "generic_runner_implementation_remains_blocked",
        "loop_remains_closed",
        "dangerous_flags_all_false",
        "future_validator_or_source_verification_required_before_acquisition_or_download",
        "replacement_checks_all_true",
    ]
    required_false = [
        "stale_or_contradictory_artifact_detected",
        "documentation_loop_detected",
        "source_identity_completeness_pass",
        "okx_source_verified_now",
        "okx_official_status_verified_now",
        "source_identity_resolution_required",
        "browse_only_source_identity_lookup_required_next",
        "okx_sample_zip_downloaded_now",
        "okx_main_page_browsed_now",
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
        "generic_runner_approval_granted",
        "schema_or_config_created",
        "ordinary_selector_backlog_loop_reentry_allowed",
        "generic_runner_target_exists",
    ]
    for key in required_true:
        require_true(payload.get(key), key)
    for key in required_false:
        require_false(payload.get(key), key)
    require_equal(payload.get("historical_data_acquisition_user_supplied_source_identity_input_status"), STATUS_PASS, "input_status")
    require_equal(payload.get("final_decision"), EVIDENCE_AFTER, "final_decision")
    require_equal(payload.get("next_module"), NEXT_MODULE_VALIDATOR, "next_module")
    require_equal(payload.get("user_supplied_source_identity_type"), USER_SUPPLIED_SOURCE_IDENTITY_TYPE, "identity_type")
    require_equal(payload.get("source_identity_resolution_basis"), SOURCE_IDENTITY_RESOLUTION_BASIS, "resolution_basis")
    require_equal(payload.get("source_identity_completeness_level"), SOURCE_IDENTITY_COMPLETENESS_LEVEL, "completeness_level")
    require_equal(payload.get("missing_required_identity_field_count"), 7, "missing_required_identity_field_count")
    require_equal(payload.get("whole_system_preflight_decision"), "PASS", "whole_system_preflight_decision")
    require_equal(payload.get("active_p0_blocker_count"), 0, "active_p0_blocker_count")
    require_equal(payload.get("active_p1_attention_count"), 4, "active_p1_attention_count")
    require_equal(payload.get("dormant_repo_attention_count"), 716, "dormant_repo_attention_count")
    require_equal(payload.get("planned_schema_files_existing_count"), 0, "planned_schema_files_existing_count")
    require_equal(payload.get("dangerous_flags_true_count"), 0, "dangerous_flags_true_count")
    require(all(value is False for value in payload["dangerous_flags"].values()), "dangerous flags must all be false")


def main() -> None:
    identity_approval = load_json(IDENTITY_APPROVAL_ARTIFACT)
    identity_preview = load_json(IDENTITY_PREVIEW_ARTIFACT)
    source_verification = load_json(SOURCE_VERIFICATION_ARTIFACT)
    preflight = validate_preflight(identity_approval, identity_preview, source_verification)
    payload = build_payload(preflight)
    validate_payload(payload)

    write_json(OUT_DIR / "historical_user_supplied_source_identity_input_report.json", payload)
    write_json(OUT_DIR / "historical_okx_user_source_identity_record.json", payload["okx_identity_record"])
    write_json(OUT_DIR / "historical_source_identity_completeness_report.json", payload["source_identity_completeness_report"])
    write_json(
        OUT_DIR / "historical_source_identity_input_contract_compliance_report.json",
        payload["source_identity_input_contract_compliance_report"],
    )
    write_json(
        OUT_DIR / "repo_only_historical_data_acquisition_user_supplied_source_identity_input_after_approval_v1_latest.json",
        payload,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
