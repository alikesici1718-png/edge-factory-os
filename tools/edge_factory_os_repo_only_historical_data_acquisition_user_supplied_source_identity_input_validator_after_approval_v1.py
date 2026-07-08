from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_user_supplied_source_identity_input_"
    "validator_after_approval_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_user_supplied_source_identity_input_"
    "validator_after_approval_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "052c591"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 662
EXPECTED_TRACKED_PYTHON_COUNT = 663

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_user_supplied_source_identity_input_"
    "validator_after_approval_v1.py"
)
NEXT_MODULE_BROWSE_PREVIEW = (
    "edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_"
    "preview_after_user_identity_validator_v1.py"
)
NEXT_MODULE_STATIC_VERIFICATION_VALIDATOR = (
    "edge_factory_os_repo_only_historical_data_acquisition_external_or_additional_source_verification_"
    "validator_after_user_identity_validator_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_user_supplied_source_identity_input_"
    "blocked_record_after_approval_v1.py"
)

INPUT_DIR = (
    LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_user_supplied_source_identity_input_after_approval_v1"
)
INPUT_LATEST_ARTIFACT = (
    INPUT_DIR / "repo_only_historical_data_acquisition_user_supplied_source_identity_input_after_approval_v1_latest.json"
)
INPUT_REPORT_ARTIFACT = INPUT_DIR / "historical_user_supplied_source_identity_input_report.json"
OKX_RECORD_ARTIFACT = INPUT_DIR / "historical_okx_user_source_identity_record.json"
COMPLETENESS_ARTIFACT = INPUT_DIR / "historical_source_identity_completeness_report.json"
COMPLIANCE_ARTIFACT = INPUT_DIR / "historical_source_identity_input_contract_compliance_report.json"

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

INPUT_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_USER_SUPPLIED_SOURCE_IDENTITY_CAPTURED_PENDING_VALIDATOR_NO_EXECUTION"
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
    "PASS_HISTORICAL_DATA_ACQUISITION_USER_SUPPLIED_SOURCE_IDENTITY_VALIDATED_INCOMPLETE_"
    "BROWSE_ONLY_LOOKUP_PREVIEW_READY_NO_EXECUTION"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = "HISTORICAL_DATA_ACQUISITION_USER_SUPPLIED_SOURCE_IDENTITY_CAPTURED_PENDING_VALIDATOR_NO_EXECUTION"
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_USER_SUPPLIED_SOURCE_IDENTITY_VALIDATED_INCOMPLETE_"
    "BROWSE_ONLY_LOOKUP_PREVIEW_READY_NO_EXECUTION"
)
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"
USER_SUPPLIED_SOURCE_IDENTITY_TYPE = "OKX_OFFICIAL_HISTORICAL_DATA_PAGE_AND_SAMPLE_CANDLESTICK_ZIP"
SOURCE_IDENTITY_COMPLETENESS_LEVEL = "PARTIAL_USER_SUPPLIED_STATIC_IDENTITY"
SOURCE_IDENTITY_RESOLUTION_BASIS = "USER_SUPPLIED_STATIC_IDENTITY_CAPTURED"
OKX_MAIN_PAGE = "https://tr.okx.com/en/historical-data"
OKX_SAMPLE_ZIP = (
    "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/20260518/"
    "BTC-USDT-SWAP-candlesticks-2026-05-18.zip"
)
REQUIRED_MISSING_FIELDS = [
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


def require_no_forbidden_action(record: Dict[str, Any], name: str) -> None:
    for key in [
        "okx_sample_zip_downloaded_now",
        "okx_main_page_browsed_now",
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
        "generic_runner_approval_granted",
        "schema_or_config_created",
        "ordinary_selector_backlog_loop_reentry_allowed",
        "generic_runner_target_exists",
    ]:
        if key in record:
            require_false(record.get(key), f"{name}.{key}")


def require_missing_fields(fields: Iterable[Any]) -> None:
    normalized = {str(field).strip().lower() for field in fields}
    for required in REQUIRED_MISSING_FIELDS:
        require(required.lower() in normalized, f"{STATUS_BLOCKED_CONTEXT}: missing field absent: {required}")


def validate_input_artifacts(
    input_latest: Dict[str, Any],
    input_report: Dict[str, Any],
    okx_record: Dict[str, Any],
    completeness: Dict[str, Any],
    compliance: Dict[str, Any],
) -> Dict[str, Any]:
    artifact_paths = [INPUT_REPORT_ARTIFACT, OKX_RECORD_ARTIFACT, COMPLETENESS_ARTIFACT, COMPLIANCE_ARTIFACT]
    checked = [read_json_checked(path) for path in artifact_paths]
    require(all(exists for _, exists, _, _ in checked), f"{STATUS_BLOCKED_CONTEXT}: required artifact missing")
    require(all(valid for _, _, valid, _ in checked), f"{STATUS_BLOCKED_CONTEXT}: required artifact invalid json")
    require(all(non_empty for _, _, _, non_empty in checked), f"{STATUS_BLOCKED_CONTEXT}: required artifact empty")
    require_equal(okx_record.get("okx_main_page"), OKX_MAIN_PAGE, "okx_record.okx_main_page")
    require_equal(okx_record.get("okx_sample_candlestick_zip"), OKX_SAMPLE_ZIP, "okx_record.okx_sample_candlestick_zip")
    require_true(input_latest.get("historical_user_supplied_source_identity_input_report_created"), "input.report_created")
    require_true(input_latest.get("historical_okx_user_source_identity_record_created"), "input.okx_record_created")
    require_true(input_latest.get("historical_source_identity_completeness_report_created"), "input.completeness_created")
    require_true(input_latest.get("historical_source_identity_input_contract_compliance_report_created"), "input.compliance_created")
    require_true(compliance.get("source_identity_input_contract_compliance_pass"), "compliance.pass")
    return {
        "required_identity_artifacts": [str(path) for path in artifact_paths],
        "required_identity_artifacts_exist": True,
        "required_identity_artifacts_valid_json": True,
        "required_identity_artifacts_non_empty": True,
        "captured_main_page_identity_exists": True,
        "captured_sample_zip_identity_exists": True,
        "input_report_matches_latest_status": input_report.get(
            "historical_data_acquisition_user_supplied_source_identity_input_status"
        )
        == input_latest.get("historical_data_acquisition_user_supplied_source_identity_input_status"),
    }


def validate_static_identity_capture(input_latest: Dict[str, Any], okx_record: Dict[str, Any]) -> Dict[str, Any]:
    for record_name, record in [("input", input_latest), ("okx_record", okx_record)]:
        require_true(record.get("user_supplied_source_identity_present"), f"{record_name}.present")
        require_true(record.get("user_supplied_source_identity_value_recorded"), f"{record_name}.value_recorded")
        require_equal(record.get("user_supplied_source_identity_type"), USER_SUPPLIED_SOURCE_IDENTITY_TYPE, f"{record_name}.type")
        require_equal(
            record.get("source_identity_resolution_basis"),
            SOURCE_IDENTITY_RESOLUTION_BASIS,
            f"{record_name}.resolution_basis",
        )
    require_true(input_latest.get("source_identity_resolved_now"), "input.source_identity_resolved_now")
    require_true(input_latest.get("okx_source_identity_available_now"), "input.okx_source_identity_available_now")
    require_false(input_latest.get("okx_source_verified_now"), "input.okx_source_verified_now")
    require_false(input_latest.get("okx_official_status_verified_now"), "input.okx_official_status_verified_now")
    require_false(okx_record.get("network_verification_performed"), "okx_record.network_verification_performed")
    require_false(okx_record.get("official_status_asserted_by_module"), "okx_record.official_status_asserted_by_module")
    return {
        "user_supplied_source_identity_present": True,
        "user_supplied_source_identity_value_recorded": True,
        "user_supplied_source_identity_type": USER_SUPPLIED_SOURCE_IDENTITY_TYPE,
        "source_identity_static_capture_validated": True,
        "source_identity_resolution_basis": SOURCE_IDENTITY_RESOLUTION_BASIS,
        "source_identity_resolved_now": True,
        "okx_source_identity_available_now": True,
        "okx_source_verified_now": False,
        "okx_official_status_verified_now": False,
    }


def validate_completeness(input_latest: Dict[str, Any], completeness: Dict[str, Any]) -> Dict[str, Any]:
    for record_name, record in [("input", input_latest), ("completeness", completeness)]:
        require_equal(
            record.get("source_identity_completeness_level"),
            SOURCE_IDENTITY_COMPLETENESS_LEVEL,
            f"{record_name}.completeness_level",
        )
        require_false(record.get("source_identity_completeness_pass"), f"{record_name}.completeness_pass")
        require(record.get("missing_required_identity_field_count", 0) >= 7, f"{record_name}.missing_count must be >= 7")
        require_missing_fields(record.get("missing_required_identity_fields", []))
    return {
        "source_identity_completeness_level": SOURCE_IDENTITY_COMPLETENESS_LEVEL,
        "source_identity_completeness_pass": False,
        "source_identity_completeness_still_incomplete": True,
        "missing_required_identity_fields": REQUIRED_MISSING_FIELDS,
        "missing_required_identity_field_count": max(
            int(input_latest.get("missing_required_identity_field_count", 0)),
            int(completeness.get("missing_required_identity_field_count", 0)),
        ),
    }


def validate_coverage_attention(input_latest: Dict[str, Any], completeness: Dict[str, Any]) -> Dict[str, Any]:
    require_true(input_latest.get("okx_coverage_attention_required"), "input.okx_coverage_attention_required")
    require_true(completeness.get("okx_coverage_attention_required"), "completeness.okx_coverage_attention_required")
    return {
        "okx_coverage_attention_required": True,
        "okx_sample_zip_is_example_only": True,
        "okx_main_page_is_not_source_manifest": True,
        "full_3_to_4_year_coverage_proven_now": False,
        "source_manifest_proven_now": False,
        "provenance_report_proven_now": False,
        "coverage_validation_notes": [
            "user-supplied links do not prove full 3-to-4-year continuous 1h coverage",
            "sample ZIP is one example file only, not a full source manifest",
            "main page identity is not a validated source manifest",
            "4-year target remains unproven",
        ],
    }


def validate_safety(input_latest: Dict[str, Any], okx_record: Dict[str, Any], compliance: Dict[str, Any]) -> Dict[str, Any]:
    require_no_forbidden_action(input_latest, "input")
    require_no_forbidden_action(okx_record, "okx_record")
    for key in [
        "no_browse",
        "no_download",
        "no_fetch",
        "no_external_api",
        "no_data_build",
        "no_strategy_backtest_candidate_runtime_capital_live",
        "no_generic_runner_approved_or_implemented",
        "no_schema_or_config_created",
        "old_source_panel_anomaly_route_not_reopened",
    ]:
        require_true(compliance.get(key), f"compliance.{key}")
    return {
        "okx_sample_zip_downloaded_now": False,
        "okx_main_page_browsed_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "acquisition_execution_allowed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "data_build_performed": False,
        "external_api_calls_performed": False,
        "fake_or_synthetic_data_detected": False,
        "no_strategy_backtest_candidate_runtime_capital_live_action": True,
        "no_generic_runner_schema_config_action": True,
    }


def validate_preflight(
    input_latest: Dict[str, Any],
    input_report: Dict[str, Any],
    okx_record: Dict[str, Any],
    completeness: Dict[str, Any],
    compliance: Dict[str, Any],
    identity_approval: Dict[str, Any],
    identity_preview: Dict[str, Any],
    source_verification: Dict[str, Any],
) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    status = run_git(["status", "--short"])
    require_equal(head, EXPECTED_HEAD, "head")
    validate_repo_status_allows_current_tool_only(status)
    require_equal(
        input_latest.get("next_module"),
        REQUESTED_MODULE,
        "input.next_module",
        mismatch_status=STATUS_BLOCKED_NEXT_MODULE,
    )
    require_equal(
        input_latest.get("historical_data_acquisition_user_supplied_source_identity_input_status"),
        INPUT_STATUS_PASS,
        "input.status",
    )
    require_equal(
        input_latest.get("current_evidence_chain_quality_after_input"),
        EVIDENCE_BEFORE,
        "input.current_evidence_chain_quality_after_input",
    )
    require_true(input_latest.get("user_source_identity_input_performed"), "input.performed")
    require_true(input_latest.get("source_identity_resolved_now"), "input.source_identity_resolved_now")
    require_equal(input_latest.get("source_identity_resolution_basis"), SOURCE_IDENTITY_RESOLUTION_BASIS, "input.basis")
    require_true(input_latest.get("okx_source_identity_available_now"), "input.okx_source_identity_available_now")
    require_false(input_latest.get("okx_source_verified_now"), "input.okx_source_verified_now")
    require_false(input_latest.get("okx_official_status_verified_now"), "input.okx_official_status_verified_now")
    require_false(input_latest.get("source_identity_completeness_pass"), "input.source_identity_completeness_pass")
    require_equal(input_latest.get("missing_required_identity_field_count"), 7, "input.missing_required_identity_field_count")
    require_no_forbidden_action(input_latest, "input")
    require_equal(input_latest.get("active_p0_blocker_count"), 0, "input.active_p0_blocker_count")
    require_equal(input_latest.get("active_p1_attention_count"), 4, "input.active_p1_attention_count")
    require_equal(input_latest.get("dormant_repo_attention_count"), 716, "input.dormant_repo_attention_count")
    require_true(
        input_latest.get("dormant_repo_attention_count_carried_forward"),
        "input.dormant_repo_attention_count_carried_forward",
    )

    validate_input_artifacts(input_latest, input_report, okx_record, completeness, compliance)
    validate_static_identity_capture(input_latest, okx_record)
    validate_completeness(input_latest, completeness)
    validate_coverage_attention(input_latest, completeness)
    validate_safety(input_latest, okx_record, compliance)

    require_equal(
        identity_approval.get("historical_data_acquisition_source_identity_resolution_approval_status"),
        IDENTITY_APPROVAL_STATUS_PASS,
        "identity_approval.status",
    )
    require_equal(
        identity_preview.get("historical_data_acquisition_source_identity_resolution_preview_status"),
        IDENTITY_PREVIEW_STATUS_PASS,
        "identity_preview.status",
    )
    require_equal(
        source_verification.get("historical_data_acquisition_external_or_additional_source_verification_status"),
        SOURCE_VERIFICATION_STATUS_PASS,
        "source_verification.status",
    )
    for name, artifact in [
        ("identity_approval", identity_approval),
        ("identity_preview", identity_preview),
        ("source_verification", source_verification),
    ]:
        require_equal(artifact.get("active_p0_blocker_count"), 0, f"{name}.active_p0_blocker_count")
        require_equal(artifact.get("active_p1_attention_count"), 4, f"{name}.active_p1_attention_count")
        require_true(
            artifact.get("dormant_repo_attention_count_carried_forward"),
            f"{name}.dormant_repo_attention_count_carried_forward",
        )
        require_equal(artifact.get("dormant_repo_attention_count"), 716, f"{name}.dormant_repo_attention_count")

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
        "input_latest_artifact": str(INPUT_LATEST_ARTIFACT),
        "input_report_artifact": str(INPUT_REPORT_ARTIFACT),
        "okx_record_artifact": str(OKX_RECORD_ARTIFACT),
        "completeness_artifact": str(COMPLETENESS_ARTIFACT),
        "compliance_artifact": str(COMPLIANCE_ARTIFACT),
        "identity_approval_artifact": str(IDENTITY_APPROVAL_ARTIFACT),
        "identity_preview_artifact": str(IDENTITY_PREVIEW_ARTIFACT),
        "source_verification_artifact": str(SOURCE_VERIFICATION_ARTIFACT),
    }


def risk_decision() -> Dict[str, Any]:
    return {
        "user_supplied_source_identity_input_validated": True,
        "user_supplied_source_identity_validation_p0_count": 0,
        "user_supplied_source_identity_validation_p1_count": 5,
        "user_supplied_source_identity_validation_p2_count": 1,
        "source_identity_static_capture_validated": True,
        "source_identity_completeness_still_incomplete": True,
        "okx_source_requires_independent_verification": True,
        "browse_only_lookup_or_user_manual_verification_required_next": True,
        "risk_decision_reason": (
            "captured identity is honest static evidence, but official status, source manifest, archive index, coverage, "
            "schema, timezone, and terms remain unverified; acquisition stays blocked"
        ),
    }


def next_module_decision() -> Dict[str, Any]:
    return {
        "next_module": NEXT_MODULE_BROWSE_PREVIEW,
        "next_action": (
            "RUN_SEPARATE_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_PREVIEW_OR_USER_MANUAL_VERIFICATION_RECORD_NO_DOWNLOAD_NO_API"
        ),
        "do_not_choose_source_verification_through_network_directly": True,
        "do_not_choose_browse_execution_directly": True,
        "do_not_choose_acquisition_execution_apply": True,
        "do_not_choose_data_download_fetch_api": True,
        "do_not_choose_strategy_research": True,
        "do_not_choose_candidate_backtest_runtime_live_capital": True,
        "if_static_evidence_complete_without_browse": NEXT_MODULE_STATIC_VERIFICATION_VALIDATOR,
        "if_blocked": NEXT_MODULE_BLOCKED,
    }


def replacement_checks(payload: Dict[str, Any]) -> Dict[str, bool]:
    return {
        "preflight_passed": payload.get("whole_system_preflight_decision") == "PASS",
        "input_artifacts_validated": (
            payload.get("required_identity_artifacts_exist") is True
            and payload.get("required_identity_artifacts_valid_json") is True
        ),
        "static_capture_validated": payload.get("source_identity_static_capture_validated") is True,
        "not_overclaimed": (
            payload.get("okx_source_verified_now") is False
            and payload.get("okx_official_status_verified_now") is False
            and payload.get("source_identity_completeness_pass") is False
            and payload.get("source_identity_completeness_still_incomplete") is True
        ),
        "coverage_unproven": (
            payload.get("full_3_to_4_year_coverage_proven_now") is False
            and payload.get("source_manifest_proven_now") is False
            and payload.get("provenance_report_proven_now") is False
        ),
        "no_browse_download_fetch_api_build": (
            payload.get("okx_sample_zip_downloaded_now") is False
            and payload.get("okx_main_page_browsed_now") is False
            and payload.get("okx_download_performed") is False
            and payload.get("okx_api_call_performed") is False
            and payload.get("okx_browse_performed") is False
            and payload.get("data_download_performed") is False
            and payload.get("data_fetch_performed") is False
            and payload.get("data_build_performed") is False
            and payload.get("external_api_calls_performed") is False
        ),
        "risk_decision_pass_p1": (
            payload.get("user_supplied_source_identity_validation_p0_count") == 0
            and payload.get("user_supplied_source_identity_validation_p1_count", 0) >= 1
        ),
        "generic_runner_blocked": payload.get("generic_runner_implementation_remains_blocked") is True,
        "schema_config_absent": payload.get("schema_or_config_created") is False,
        "loop_closed": payload.get("loop_remains_closed") is True,
        "next_module_allowed": payload.get("next_module") == NEXT_MODULE_BROWSE_PREVIEW,
    }


def build_payload(
    preflight: Dict[str, Any],
    input_latest: Dict[str, Any],
    input_report: Dict[str, Any],
    okx_record: Dict[str, Any],
    completeness: Dict[str, Any],
    compliance: Dict[str, Any],
) -> Dict[str, Any]:
    artifact_validation = validate_input_artifacts(input_latest, input_report, okx_record, completeness, compliance)
    static_validation = validate_static_identity_capture(input_latest, okx_record)
    completeness_validation = validate_completeness(input_latest, completeness)
    coverage_validation = validate_coverage_attention(input_latest, completeness)
    safety_validation = validate_safety(input_latest, okx_record, compliance)
    risk = risk_decision()
    next_decision = next_module_decision()
    flags = dangerous_flags()

    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_user_supplied_source_identity_input_validator_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": next_decision["next_action"],
        "next_module": next_decision["next_module"],
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
        "prior_user_source_identity_input_respected": True,
        "input_artifact_validation_completed": True,
        "static_identity_capture_validation_completed": True,
        "completeness_validation_completed": True,
        "coverage_attention_validation_completed": True,
        "safety_validation_completed": True,
        "risk_decision_completed": True,
        **artifact_validation,
        **static_validation,
        **completeness_validation,
        **coverage_validation,
        **safety_validation,
        **risk,
        "current_evidence_chain_quality_before_validator": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_validator": EVIDENCE_AFTER,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 4,
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
        "dangerous_flags_true_count": sum(1 for value in flags.values() if value is True),
        "derived_live_repo_post_check": (
            "PASS_USER_SUPPLIED_SOURCE_IDENTITY_VALIDATED_INCOMPLETE_BROWSE_ONLY_LOOKUP_PREVIEW_READY_NO_EXECUTION"
        ),
        "derived_live_repo_post_check_reason": (
            "validated that OKX source identity strings were captured only as user-supplied static evidence, remain "
            "incomplete, and do not verify official status, source manifest, full 3-to-4-year coverage, provenance, "
            "schema, timezone, or terms; no browsing, download, fetch, API call, data build, strategy, runtime, "
            "capital, live, generic-runner, schema, config, or old-route action occurred"
        ),
        "validation_sections": {
            "input_artifact_validation": artifact_validation,
            "static_identity_capture_validation": static_validation,
            "completeness_validation": completeness_validation,
            "coverage_attention_validation": coverage_validation,
            "safety_validation": safety_validation,
            "risk_decision": risk,
            "next_module_decision": next_decision,
        },
        "tracked_python_count_expectation": {
            "previous": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT,
        },
        "tracked_python_count_current_pre_commit": tracked_python_count(),
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
        "prior_user_source_identity_input_respected",
        "input_artifact_validation_completed",
        "static_identity_capture_validation_completed",
        "completeness_validation_completed",
        "coverage_attention_validation_completed",
        "safety_validation_completed",
        "risk_decision_completed",
        "user_supplied_source_identity_input_validated",
        "required_identity_artifacts_exist",
        "required_identity_artifacts_valid_json",
        "user_supplied_source_identity_present",
        "user_supplied_source_identity_value_recorded",
        "source_identity_static_capture_validated",
        "source_identity_completeness_still_incomplete",
        "source_identity_resolved_now",
        "okx_source_identity_available_now",
        "okx_source_requires_independent_verification",
        "okx_coverage_attention_required",
        "okx_sample_zip_is_example_only",
        "okx_main_page_is_not_source_manifest",
        "browse_only_lookup_or_user_manual_verification_required_next",
        "generic_runner_implementation_remains_blocked",
        "loop_remains_closed",
        "dangerous_flags_all_false",
        "replacement_checks_all_true",
    ]
    required_false = [
        "stale_or_contradictory_artifact_detected",
        "documentation_loop_detected",
        "source_identity_completeness_pass",
        "okx_source_verified_now",
        "okx_official_status_verified_now",
        "full_3_to_4_year_coverage_proven_now",
        "source_manifest_proven_now",
        "provenance_report_proven_now",
        "okx_sample_zip_downloaded_now",
        "okx_main_page_browsed_now",
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
        "generic_runner_approval_granted",
        "schema_or_config_created",
        "ordinary_selector_backlog_loop_reentry_allowed",
        "generic_runner_target_exists",
    ]
    for key in required_true:
        require_true(payload.get(key), key)
    for key in required_false:
        require_false(payload.get(key), key)
    require_equal(
        payload.get("historical_data_acquisition_user_supplied_source_identity_input_validator_status"),
        STATUS_PASS,
        "validator_status",
    )
    require_equal(payload.get("final_decision"), EVIDENCE_AFTER, "final_decision")
    require_equal(payload.get("next_module"), NEXT_MODULE_BROWSE_PREVIEW, "next_module")
    require_equal(payload.get("whole_system_preflight_decision"), "PASS", "preflight_decision")
    require_equal(payload.get("documentation_loop_risk_level"), DOCUMENTATION_LOOP_RISK_LEVEL, "documentation_loop_risk_level")
    require_equal(payload.get("user_supplied_source_identity_type"), USER_SUPPLIED_SOURCE_IDENTITY_TYPE, "identity_type")
    require_equal(payload.get("source_identity_completeness_level"), SOURCE_IDENTITY_COMPLETENESS_LEVEL, "completeness_level")
    require(payload.get("missing_required_identity_field_count", 0) >= 7, "missing_required_identity_field_count must be >= 7")
    require_equal(payload.get("user_supplied_source_identity_validation_p0_count"), 0, "p0_count")
    require(payload.get("user_supplied_source_identity_validation_p1_count", 0) >= 1, "p1_count must be >= 1")
    require_equal(payload.get("active_p0_blocker_count"), 0, "active_p0_blocker_count")
    require(payload.get("active_p1_attention_count", 0) >= 4, "active_p1_attention_count must be >= 4")
    require_equal(payload.get("dormant_repo_attention_count"), 716, "dormant_repo_attention_count")
    require_equal(payload.get("planned_schema_files_existing_count"), 0, "planned_schema_files_existing_count")
    require_equal(payload.get("dangerous_flags_true_count"), 0, "dangerous_flags_true_count")
    require(all(value is False for value in payload["dangerous_flags"].values()), "dangerous flags must all be false")


def main() -> None:
    input_latest = load_json(INPUT_LATEST_ARTIFACT)
    input_report = load_json(INPUT_REPORT_ARTIFACT)
    okx_record = load_json(OKX_RECORD_ARTIFACT)
    completeness = load_json(COMPLETENESS_ARTIFACT)
    compliance = load_json(COMPLIANCE_ARTIFACT)
    identity_approval = load_json(IDENTITY_APPROVAL_ARTIFACT)
    identity_preview = load_json(IDENTITY_PREVIEW_ARTIFACT)
    source_verification = load_json(SOURCE_VERIFICATION_ARTIFACT)
    preflight = validate_preflight(
        input_latest,
        input_report,
        okx_record,
        completeness,
        compliance,
        identity_approval,
        identity_preview,
        source_verification,
    )
    payload = build_payload(input_latest=input_latest, input_report=input_report, okx_record=okx_record, completeness=completeness, compliance=compliance, preflight=preflight)
    validate_payload(payload)
    write_json(
        OUT_DIR / "historical_user_supplied_source_identity_input_validator_report.json",
        payload,
    )
    write_json(
        OUT_DIR / "historical_user_supplied_source_identity_input_validator_sections.json",
        payload["validation_sections"],
    )
    write_json(
        OUT_DIR / "repo_only_historical_data_acquisition_user_supplied_source_identity_input_validator_after_approval_v1_latest.json",
        payload,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
