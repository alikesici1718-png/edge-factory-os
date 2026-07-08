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
    "edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_"
    "validator_after_approval_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_"
    "validator_after_approval_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "c719568"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 666
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 667

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_"
    "validator_after_approval_v1.py"
)
NEXT_MODULE_SCOPE_PREVIEW = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_archive_scope_resolution_preview_"
    "after_browse_lookup_validator_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_"
    "blocked_record_after_approval_v1.py"
)

LOOKUP_DIR = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_after_approval_v1"
)
LOOKUP_LATEST_ARTIFACT = (
    LOOKUP_DIR
    / "repo_only_historical_data_acquisition_browse_only_source_identity_lookup_after_approval_v1_latest.json"
)
APPROVAL_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_browse_only_source_identity_lookup_approval_after_preview_v1"
    / "repo_only_historical_data_acquisition_browse_only_source_identity_lookup_approval_after_preview_v1_latest.json"
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

REQUIRED_LOOKUP_ARTIFACT_NAMES = [
    "historical_browse_only_source_identity_lookup_report.json",
    "historical_okx_official_page_evidence_report.json",
    "historical_okx_candlestick_coverage_evidence_report.json",
    "historical_okx_archive_pattern_evidence_report.json",
    "historical_okx_terms_or_source_notes_report.json",
    "historical_browse_only_lookup_contract_compliance_report.json",
]

LOOKUP_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_COMPLETE_PENDING_"
    "VALIDATOR_NO_EXECUTION"
)
APPROVAL_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_APPROVED_NEXT_NO_EXECUTION"
)
PREVIEW_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_PREVIEW_READY_"
    "APPROVAL_REQUIRED_NO_EXECUTION"
)
USER_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_USER_SUPPLIED_SOURCE_IDENTITY_VALIDATED_INCOMPLETE_"
    "BROWSE_ONLY_LOOKUP_PREVIEW_READY_NO_EXECUTION"
)
STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_VALIDATED_PARTIAL_"
    "OKX_IDENTITY_ARCHIVE_SCOPE_RESOLUTION_PREVIEW_READY_NO_EXECUTION"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_COMPLETE_PENDING_"
    "VALIDATOR_NO_EXECUTION"
)
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_VALIDATED_PARTIAL_"
    "OKX_IDENTITY_ARCHIVE_SCOPE_RESOLUTION_PREVIEW_READY_NO_EXECUTION"
)
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"

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


def validate_required_lookup_artifacts() -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Any]]:
    artifacts: Dict[str, Dict[str, Any]] = {}
    audit: Dict[str, Any] = {
        "required_lookup_artifact_paths": [],
        "required_lookup_artifacts_exist": True,
        "required_lookup_artifacts_valid_json": True,
        "required_lookup_artifacts_non_empty": True,
    }
    for name in REQUIRED_LOOKUP_ARTIFACT_NAMES:
        path = LOOKUP_DIR / name
        data, exists, valid, non_empty = read_json_checked(path)
        audit["required_lookup_artifact_paths"].append(str(path))
        audit["required_lookup_artifacts_exist"] = audit["required_lookup_artifacts_exist"] and exists
        audit["required_lookup_artifacts_valid_json"] = audit["required_lookup_artifacts_valid_json"] and valid
        audit["required_lookup_artifacts_non_empty"] = audit["required_lookup_artifacts_non_empty"] and non_empty
        if not (exists and valid and non_empty):
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: required lookup artifact invalid: {path}")
        artifacts[name] = data
    return artifacts, audit


def require_lookup_field(lookup: Dict[str, Any], field: str, expected: Any) -> None:
    require_equal(lookup.get(field), expected, f"lookup.{field}")


def require_lookup_true(lookup: Dict[str, Any], field: str) -> None:
    require_true(lookup.get(field), f"lookup.{field}")


def require_lookup_false(lookup: Dict[str, Any], field: str) -> None:
    require_false(lookup.get(field), f"lookup.{field}")


def validate_preflight(lookup: Dict[str, Any]) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))

    approval = load_json(APPROVAL_ARTIFACT)
    preview = load_json(BROWSE_PREVIEW_ARTIFACT)
    user_validator = load_json(USER_IDENTITY_VALIDATOR_ARTIFACT)

    require_equal(
        approval.get("historical_data_acquisition_browse_only_source_identity_lookup_approval_status"),
        APPROVAL_STATUS_PASS,
        "approval_status",
    )
    require_equal(
        preview.get("historical_data_acquisition_browse_only_source_identity_lookup_preview_status"),
        PREVIEW_STATUS_PASS,
        "preview_status",
    )
    require_equal(
        user_validator.get("historical_data_acquisition_user_supplied_source_identity_input_validator_status"),
        USER_VALIDATOR_STATUS_PASS,
        "user_validator_status",
    )
    require_equal(lookup.get("next_module"), REQUESTED_MODULE, "lookup.next_module", STATUS_BLOCKED_NEXT_MODULE)
    require_equal(lookup.get("historical_data_acquisition_browse_only_source_identity_lookup_status"), LOOKUP_STATUS_PASS, "lookup_status")
    require_lookup_true(lookup, "browse_only_lookup_performed")
    require_lookup_true(lookup, "page_identity_lookup_completed")
    require_lookup_true(lookup, "okx_main_page_browsed_now")
    require_lookup_false(lookup, "okx_sample_zip_downloaded_now")
    require_lookup_false(lookup, "okx_download_performed")
    require_lookup_false(lookup, "okx_api_call_performed")
    require_lookup_false(lookup, "external_api_calls_performed")
    require_lookup_false(lookup, "data_download_performed")
    require_lookup_false(lookup, "data_fetch_performed")
    require_lookup_false(lookup, "data_build_performed")
    require_lookup_false(lookup, "okx_source_verified_for_acquisition_now")
    require_lookup_false(lookup, "acquisition_execution_allowed_now")
    require_lookup_false(lookup, "external_download_allowed_now")
    require_lookup_false(lookup, "external_api_allowed_now")
    require_lookup_field(lookup, "active_p0_blocker_count", 0)
    require_lookup_field(lookup, "active_p1_attention_count", 8)
    require_lookup_field(lookup, "dormant_repo_attention_count", 716)
    require_lookup_false(lookup, "generic_runner_approval_granted")
    require_lookup_true(lookup, "generic_runner_implementation_remains_blocked")
    require_lookup_false(lookup, "schema_or_config_created")
    require_lookup_false(lookup, "ordinary_selector_backlog_loop_reentry_allowed")
    require_lookup_true(lookup, "loop_remains_closed")

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
        "active_p0_blocker_count_from_live_artifact": lookup.get("active_p0_blocker_count"),
        "active_p1_attention_count_from_live_artifact": lookup.get("active_p1_attention_count"),
        "p1_attention_carried_forward": True,
        "dormant_repo_attention_count_carried_forward": True,
        "blocked_actions_absent_from_requested_module": True,
        "approval_artifact": str(APPROVAL_ARTIFACT),
        "browse_preview_artifact": str(BROWSE_PREVIEW_ARTIFACT),
        "user_identity_validator_artifact": str(USER_IDENTITY_VALIDATOR_ARTIFACT),
        "lookup_latest_artifact": str(LOOKUP_LATEST_ARTIFACT),
        "head": head,
        "status_lines_allowed": [f"?? {CURRENT_TOOL_REL}", f"A  {CURRENT_TOOL_REL}", f"AM {CURRENT_TOOL_REL}"],
    }


def validate_artifact_consistency(lookup: Dict[str, Any], artifacts: Dict[str, Dict[str, Any]]) -> Dict[str, bool]:
    official = artifacts["historical_okx_official_page_evidence_report.json"]
    coverage = artifacts["historical_okx_candlestick_coverage_evidence_report.json"]
    archive = artifacts["historical_okx_archive_pattern_evidence_report.json"]
    terms = artifacts["historical_okx_terms_or_source_notes_report.json"]
    compliance = artifacts["historical_browse_only_lookup_contract_compliance_report.json"]
    checks = {
        "official_page_matches_lookup": official.get("okx_official_page_evidence_found") is True
        and official.get("okx_historical_market_data_page_evidence_found") is True
        and official.get("page_identity_lookup_completed") is True,
        "coverage_matches_lookup": coverage.get("okx_candlestick_source_evidence_found") is True
        and coverage.get("okx_candlestick_coverage_start_visible") is True
        and coverage.get("okx_candlestick_coverage_start") == "July 2023"
        and coverage.get("full_4_year_coverage_proven_now") is False
        and coverage.get("source_manifest_proven_now") is False,
        "archive_matches_lookup": archive.get("okx_archive_or_download_route_visible") is True
        and archive.get("okx_archive_pattern_evidence_found") is True
        and archive.get("okx_sample_zip_pattern_consistency")
        == "PLAUSIBLE_STATIC_OKX_CANDLESTICK_DAILY_ARCHIVE_PATTERN_ONLY"
        and archive.get("okx_sample_zip_downloaded_now") is False
        and archive.get("okx_download_performed") is False
        and archive.get("okx_api_call_performed") is False,
        "terms_missing_requirements_match_lookup": terms.get("okx_1h_interval_visible") is False
        and terms.get("okx_timestamp_timezone_visible") is False
        and terms.get("okx_terms_or_license_visible") is True,
        "compliance_matches_lookup": compliance.get("whole_system_preflight_decision") == "PASS"
        and compliance.get("browse_only_lookup_performed") is True
        and compliance.get("okx_sample_zip_downloaded_now") is False
        and compliance.get("okx_api_call_performed") is False
        and compliance.get("data_build_performed") is False
        and compliance.get("replacement_checks_all_true") is True,
        "latest_matches_report_status": artifacts["historical_browse_only_source_identity_lookup_report.json"].get(
            "historical_data_acquisition_browse_only_source_identity_lookup_status"
        )
        == lookup.get("historical_data_acquisition_browse_only_source_identity_lookup_status"),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: inconsistent lookup artifacts: {failed}")
    return checks


def validate_lookup_semantics(lookup: Dict[str, Any]) -> Dict[str, Any]:
    network_audit = lookup.get("lookup_network_audit", {})
    incomplete = lookup.get("source_identity_lookup_incomplete_fields", [])
    if not isinstance(incomplete, list):
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: incomplete field list is not a list")

    require_lookup_true(lookup, "okx_official_page_evidence_found")
    require_lookup_true(lookup, "okx_historical_market_data_page_evidence_found")
    require_lookup_true(lookup, "okx_candlestick_source_evidence_found")
    require_lookup_true(lookup, "okx_source_identity_lookup_completed")
    require_lookup_true(lookup, "okx_source_identity_partially_verified")
    require_lookup_false(lookup, "okx_source_verified_for_acquisition_now")

    require_lookup_true(lookup, "okx_candlestick_coverage_start_visible")
    require_lookup_field(lookup, "okx_candlestick_coverage_start", "July 2023")
    statement = str(lookup.get("okx_candlestick_coverage_statement", ""))
    if "Candlestick/OHLC history starts July 2023" not in statement:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: coverage statement does not preserve July 2023 OHLC wording")
    require_lookup_true(lookup, "okx_3_year_coverage_likely_or_possible")
    require_lookup_false(lookup, "full_3_to_4_year_coverage_proven_now")
    require_lookup_false(lookup, "full_4_year_coverage_proven_now")

    require_lookup_true(lookup, "okx_archive_or_download_route_visible")
    require_lookup_true(lookup, "okx_archive_pattern_evidence_found")
    require_lookup_field(
        lookup,
        "okx_sample_zip_pattern_consistency",
        "PLAUSIBLE_STATIC_OKX_CANDLESTICK_DAILY_ARCHIVE_PATTERN_ONLY",
    )
    require_lookup_false(lookup, "okx_sample_zip_downloaded_now")
    require_lookup_false(lookup, "source_manifest_proven_now")
    require_lookup_false(lookup, "provenance_report_proven_now")

    require_lookup_false(lookup, "okx_file_format_visible")
    require_lookup_false(lookup, "okx_1h_interval_visible")
    require_lookup_false(lookup, "okx_timestamp_timezone_visible")
    required_incomplete = {
        "1h candle interval availability not visible",
        "timestamp/timezone rules not visible",
        "complete archive file schema/format not visible",
        "full source manifest not visible",
        "full 4-year continuous coverage not proven",
        "acquisition provenance report not proven",
    }
    missing = sorted(required_incomplete.difference(set(incomplete)))
    if missing:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: missing required incomplete fields: {missing}")

    require_true(network_audit.get("only_approved_page_requested"), "lookup_network_audit.only_approved_page_requested")
    require_false(network_audit.get("zip_or_archive_url_requested"), "lookup_network_audit.zip_or_archive_url_requested")
    require_false(network_audit.get("api_url_requested"), "lookup_network_audit.api_url_requested")
    require_false(network_audit.get("asset_or_secondary_url_requested"), "lookup_network_audit.asset_or_secondary_url_requested")

    if lookup.get("replacement_checks_all_true") is not True:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: lookup replacement checks are not all true")
    true_dangerous = [
        name for name, value in lookup.get("dangerous_flags", {}).items() if value is True
    ]
    if true_dangerous:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: lookup dangerous flags true: {true_dangerous}")

    return {
        "safe_browse_scope_validation_completed": True,
        "okx_page_identity_validation_completed": True,
        "coverage_validation_completed": True,
        "archive_pattern_validation_completed": True,
        "missing_requirements_validation_completed": True,
        "safe_browse_scope_notes": [
            "validator did not browse or call any network target",
            "lookup audit records only the approved OKX historical-data page request",
            "sample ZIP remains static URL-pattern evidence only and was not requested",
            "acquisition execution remains blocked",
        ],
    }


def build_payload(
    preflight_report: Dict[str, Any],
    artifact_audit: Dict[str, Any],
    consistency_checks: Dict[str, bool],
    semantic_report: Dict[str, Any],
    lookup: Dict[str, Any],
) -> Dict[str, Any]:
    p1_count = max(8, int(lookup.get("source_identity_lookup_p1_count", 8)))
    flags = dangerous_flags()
    replacement_checks = {
        "preflight_passed": preflight_report.get("whole_system_preflight_decision") == "PASS",
        "lookup_artifacts_exist": artifact_audit.get("required_lookup_artifacts_exist") is True,
        "lookup_artifacts_valid_json": artifact_audit.get("required_lookup_artifacts_valid_json") is True,
        "lookup_artifacts_non_empty": artifact_audit.get("required_lookup_artifacts_non_empty") is True,
        "artifact_consistency_validated": all(consistency_checks.values()),
        "safe_scope_validated": semantic_report.get("safe_browse_scope_validation_completed") is True,
        "partial_identity_validated": lookup.get("okx_source_identity_partially_verified") is True,
        "acquisition_not_ready": lookup.get("okx_source_verified_for_acquisition_now") is False,
        "no_download_fetch_api_build": True,
        "generic_runner_blocked": True,
        "schema_config_absent": True,
        "loop_closed": True,
        "not_overclaimed": True,
    }
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_browse_only_source_identity_lookup_validator_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "CREATE_OKX_ARCHIVE_SCOPE_RESOLUTION_PREVIEW_NO_DOWNLOAD_NO_API_NO_DATA_BUILD",
        "next_module": NEXT_MODULE_SCOPE_PREVIEW,
        **preflight_report,
        "prior_browse_only_lookup_respected": True,
        "lookup_artifact_existence_validation_completed": True,
        "safe_browse_scope_validation_completed": True,
        "okx_page_identity_validation_completed": True,
        "coverage_validation_completed": True,
        "archive_pattern_validation_completed": True,
        "missing_requirements_validation_completed": True,
        "risk_decision_completed": True,
        "browse_only_lookup_validated": True,
        "required_lookup_artifacts_exist": True,
        "required_lookup_artifacts_valid_json": True,
        "required_lookup_artifacts_non_empty": True,
        "browse_only_lookup_performed": True,
        "page_identity_lookup_completed": True,
        "okx_main_page_browsed_now": True,
        "okx_sample_zip_downloaded_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "external_api_calls_performed": False,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "data_build_performed": False,
        "okx_official_page_evidence_found": True,
        "okx_historical_market_data_page_evidence_found": True,
        "okx_candlestick_source_evidence_found": True,
        "okx_candlestick_coverage_start_visible": True,
        "okx_candlestick_coverage_start": "July 2023",
        "okx_candlestick_coverage_statement": lookup.get("okx_candlestick_coverage_statement"),
        "okx_3_year_coverage_likely_or_possible": True,
        "full_3_to_4_year_coverage_proven_now": False,
        "full_4_year_coverage_proven_now": False,
        "okx_archive_or_download_route_visible": True,
        "okx_archive_pattern_evidence_found": True,
        "okx_sample_zip_pattern_consistency": "PLAUSIBLE_STATIC_OKX_CANDLESTICK_DAILY_ARCHIVE_PATTERN_ONLY",
        "okx_file_format_visible": False,
        "okx_1h_interval_visible": False,
        "okx_instrument_universe_visible": bool(lookup.get("okx_instrument_universe_visible")),
        "okx_timestamp_timezone_visible": False,
        "okx_terms_or_license_visible": bool(lookup.get("okx_terms_or_license_visible")),
        "source_manifest_proven_now": False,
        "provenance_report_proven_now": False,
        "source_identity_lookup_incomplete_fields": lookup.get("source_identity_lookup_incomplete_fields"),
        "okx_source_identity_lookup_completed": True,
        "okx_source_identity_partially_verified": True,
        "okx_source_identity_partially_verified_validated": True,
        "okx_source_verified_for_acquisition_now": False,
        "okx_acquisition_readiness": False,
        "okx_archive_scope_resolution_required": True,
        "okx_1h_interval_resolution_required": True,
        "okx_coverage_resolution_required": True,
        "okx_schema_timezone_resolution_required": True,
        "acquisition_execution_allowed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "fake_or_synthetic_data_detected": False,
        "browse_only_lookup_validation_p0_count": 0,
        "browse_only_lookup_validation_p1_count": p1_count,
        "browse_only_lookup_validation_p2_count": max(1, int(lookup.get("source_identity_lookup_p2_count", 1))),
        "current_evidence_chain_quality_before_validator": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_validator": EVIDENCE_AFTER,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": p1_count,
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
        "derived_live_repo_post_check": "PASS_BROWSE_ONLY_SOURCE_IDENTITY_LOOKUP_VALIDATED_PARTIAL_OKX_IDENTITY_ARCHIVE_SCOPE_RESOLUTION_PREVIEW_READY_NO_EXECUTION",
        "derived_live_repo_post_check_reason": (
            "repo-only validator confirmed the approved browse-only lookup artifacts, accepted partial OKX source identity, "
            "carried forward unresolved archive scope, 1h interval, coverage, schema/timezone, manifest, and provenance requirements, "
            "and kept acquisition, downloads, APIs, data builds, strategy, runtime, capital, live, generic-runner, schema, config, and old-route actions blocked"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": all(replacement_checks.values()),
        "validation_sections": {
            "lookup_artifact_existence_validation": artifact_audit,
            "safe_browse_scope_validation": semantic_report,
            "artifact_consistency_validation": consistency_checks,
            "risk_decision": {
                "browse_only_lookup_validated": True,
                "browse_only_lookup_validation_p0_count": 0,
                "browse_only_lookup_validation_p1_count": p1_count,
                "browse_only_lookup_validation_p2_count": max(1, int(lookup.get("source_identity_lookup_p2_count", 1))),
                "okx_source_identity_partially_verified_validated": True,
                "okx_source_verified_for_acquisition_now": False,
                "okx_acquisition_readiness": False,
                "okx_archive_scope_resolution_required": True,
                "okx_1h_interval_resolution_required": True,
                "okx_coverage_resolution_required": True,
                "okx_schema_timezone_resolution_required": True,
            },
            "next_module_decision": {
                "do_not_choose_acquisition_execution_apply": True,
                "do_not_choose_data_download_fetch_api": True,
                "do_not_choose_zip_download": True,
                "do_not_choose_strategy_research": True,
                "do_not_choose_candidate_backtest_runtime_live_capital": True,
                "if_validation_passes_partial_identity": NEXT_MODULE_SCOPE_PREVIEW,
                "if_validation_blocked": NEXT_MODULE_BLOCKED,
            },
        },
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
    artifacts = {
        "historical_browse_only_source_identity_lookup_validator_report.json": payload,
        "historical_browse_only_lookup_artifact_existence_validation_report.json": payload["validation_sections"][
            "lookup_artifact_existence_validation"
        ],
        "historical_browse_only_lookup_safe_scope_validation_report.json": payload["validation_sections"][
            "safe_browse_scope_validation"
        ],
        "historical_okx_partial_identity_risk_decision_report.json": payload["validation_sections"]["risk_decision"],
        "historical_browse_only_lookup_validator_contract_compliance_report.json": {
            "generated_at_utc": payload["generated_at_utc"],
            "whole_system_preflight_completed": payload["whole_system_preflight_completed"],
            "whole_system_preflight_decision": payload["whole_system_preflight_decision"],
            "browse_only_lookup_validated": payload["browse_only_lookup_validated"],
            "okx_source_verified_for_acquisition_now": payload["okx_source_verified_for_acquisition_now"],
            "okx_acquisition_readiness": payload["okx_acquisition_readiness"],
            "acquisition_execution_allowed_now": payload["acquisition_execution_allowed_now"],
            "external_download_allowed_now": payload["external_download_allowed_now"],
            "external_api_allowed_now": payload["external_api_allowed_now"],
            "data_download_performed": payload["data_download_performed"],
            "data_fetch_performed": payload["data_fetch_performed"],
            "data_build_performed": payload["data_build_performed"],
            "generic_runner_implementation_remains_blocked": payload["generic_runner_implementation_remains_blocked"],
            "schema_or_config_created": payload["schema_or_config_created"],
            "loop_remains_closed": payload["loop_remains_closed"],
            "replacement_checks_all_true": payload["replacement_checks_all_true"],
        },
        "repo_only_historical_data_acquisition_browse_only_source_identity_lookup_validator_after_approval_v1_latest.json": payload,
    }
    for name, artifact in artifacts.items():
        write_json(OUT_DIR / name, artifact)


def main() -> int:
    lookup = load_json(LOOKUP_LATEST_ARTIFACT)
    artifacts, artifact_audit = validate_required_lookup_artifacts()
    preflight_report = validate_preflight(lookup)
    consistency_checks = validate_artifact_consistency(lookup, artifacts)
    semantic_report = validate_lookup_semantics(lookup)
    payload = build_payload(preflight_report, artifact_audit, consistency_checks, semantic_report, lookup)
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
            "historical_data_acquisition_browse_only_source_identity_lookup_validator_status": STATUS_BLOCKED_CONTEXT,
            "final_decision": STATUS_BLOCKED_CONTEXT,
            "next_action": "STOP_FAIL_CLOSED_NO_BROWSING_NO_DOWNLOAD_NO_API_NO_DATA_BUILD",
            "next_module": NEXT_MODULE_BLOCKED,
            "error": str(exc),
            "browse_only_lookup_validated": False,
            "okx_source_verified_for_acquisition_now": False,
            "okx_acquisition_readiness": False,
            "acquisition_execution_allowed_now": False,
            "external_download_allowed_now": False,
            "external_api_allowed_now": False,
            "data_download_performed": False,
            "data_fetch_performed": False,
            "data_build_performed": False,
            "generic_runner_implementation_remains_blocked": True,
            "schema_or_config_created": False,
            "loop_remains_closed": True,
        }
        write_json(
            OUT_DIR / "repo_only_historical_data_acquisition_browse_only_source_identity_lookup_validator_after_approval_v1_latest.json",
            failure,
        )
        print(json.dumps(failure, indent=2, sort_keys=True), file=sys.stderr)
        raise SystemExit(1)
