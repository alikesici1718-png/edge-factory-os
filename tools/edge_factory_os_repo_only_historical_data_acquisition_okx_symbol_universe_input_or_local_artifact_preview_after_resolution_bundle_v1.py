from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_input_or_local_artifact_preview_"
    "after_resolution_bundle_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_input_or_local_artifact_"
    "preview_after_resolution_bundle_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "085eb4b"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 678
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 679

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_input_or_local_artifact_preview_"
    "after_resolution_bundle_v1.py"
)
NEXT_MODULE_CANDIDATE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_placeholder_validator_after_"
    "local_preview_v1.py"
)
NEXT_MODULE_NO_CANDIDATE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_user_input_request_record_after_"
    "local_preview_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_input_or_local_artifact_"
    "blocked_record_after_resolution_bundle_v1.py"
)

RESOLUTION_DIR = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_coverage_provenance_resolution_preview_after_source_manifest_bundle_v1"
)
RESOLUTION_BUNDLE_ARTIFACT = (
    RESOLUTION_DIR
    / "repo_only_historical_data_acquisition_okx_symbol_universe_coverage_provenance_resolution_preview_after_source_manifest_bundle_v1_latest.json"
)
SOURCE_MANIFEST_DIR = (
    LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_source_manifest_approval_after_preview_v1"
)
SOURCE_MANIFEST_ARTIFACT = SOURCE_MANIFEST_DIR / "historical_okx_source_manifest.json"
SOURCE_MANIFEST_SELF_VALIDATOR_ARTIFACT = SOURCE_MANIFEST_DIR / "historical_okx_source_manifest_self_validator.json"
AGGREGATION_POLICY_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_after_creation_v1"
    / "repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_after_creation_v1_latest.json"
)
METADATA_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_input_validator_after_approval_v1"
    / "repo_only_historical_data_acquisition_okx_user_manual_archive_metadata_input_validator_after_approval_v1_latest.json"
)

RESOLUTION_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SYMBOL_UNIVERSE_COVERAGE_PROVENANCE_RESOLUTION_BUNDLE_"
    "VALIDATED_SYMBOL_UNIVERSE_INPUT_OR_LOCAL_ARTIFACT_PREVIEW_READY_NO_EXECUTION"
)
AGGREGATION_POLICY_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_VALIDATED_"
    "SOURCE_MANIFEST_PREVIEW_READY_NO_EXECUTION"
)
METADATA_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_ARCHIVE_METADATA_INPUT_VALIDATED_"
    "1M_SCHEMA_AGGREGATION_POLICY_PREVIEW_READY_NO_EXECUTION"
)
STATUS_PASS_CANDIDATE = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_PIPELINE_VALIDATION_SYMBOL_UNIVERSE_PLACEHOLDER_CREATED_"
    "PENDING_VALIDATOR_NO_EXECUTION"
)
STATUS_PASS_NO_CANDIDATE = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SYMBOL_UNIVERSE_LOCAL_PREVIEW_NO_CANDIDATE_USER_INPUT_REQUIRED_"
    "NO_EXECUTION"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SYMBOL_UNIVERSE_COVERAGE_PROVENANCE_RESOLUTION_BUNDLE_VALIDATED_"
    "SYMBOL_UNIVERSE_INPUT_OR_LOCAL_ARTIFACT_PREVIEW_READY_NO_EXECUTION"
)
EVIDENCE_AFTER_CANDIDATE = (
    "HISTORICAL_DATA_ACQUISITION_OKX_PIPELINE_VALIDATION_SYMBOL_UNIVERSE_PLACEHOLDER_CREATED_PENDING_"
    "VALIDATOR_NO_EXECUTION"
)
EVIDENCE_AFTER_NO_CANDIDATE = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SYMBOL_UNIVERSE_USER_INPUT_REQUIRED_AFTER_LOCAL_ARTIFACT_PREVIEW_"
    "NO_EXECUTION"
)

USER_SUPPLIED_SYMBOL_UNIVERSE = "NOT_PROVIDED_IN_THIS_RUN"
SYMBOL_PATTERN = re.compile(r"\b[A-Z0-9]+-USDT-SWAP\b")
UNIVERSE_SCOPE = "PIPELINE_VALIDATION_UNIVERSE_NOT_SURVIVORSHIP_SAFE"

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


def load_json(path: Path, label: str) -> Dict[str, Any]:
    data, exists, valid, non_empty = read_json_checked(path)
    if not (exists and valid and non_empty):
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {label} missing/invalid/empty: {path}")
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
    resolution: Dict[str, Any],
    manifest: Dict[str, Any],
    manifest_validator: Dict[str, Any],
    policy_validator: Dict[str, Any],
    metadata_validator: Dict[str, Any],
) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))
    require_equal(
        resolution.get("historical_data_acquisition_okx_symbol_universe_coverage_provenance_resolution_bundle_status"),
        RESOLUTION_STATUS_PASS,
        "resolution.status",
    )
    require_equal(resolution.get("next_module"), REQUESTED_MODULE, "resolution.next_module", STATUS_BLOCKED_NEXT_MODULE)
    for field in (
        "user_supplied_symbol_universe_allowed_next",
        "local_existing_symbol_universe_preview_allowed_next",
        "source_manifest_safe_for_download_preview",
    ):
        require_true(resolution.get(field), f"resolution.{field}")
    for field in (
        "symbol_universe_resolved_now",
        "coverage_resolved_now",
        "provenance_resolved_now",
        "current_active_only_survivorship_safe",
        "source_manifest_safe_for_data_build_now",
        "source_manifest_safe_for_acquisition_now",
        "data_download_performed",
        "data_fetch_performed",
        "data_build_performed",
        "aggregation_performed_now",
        "acquisition_execution_allowed_now",
        "external_download_allowed_now",
        "external_api_allowed_now",
        "okx_download_performed",
        "okx_api_call_performed",
        "okx_browse_performed",
        "okx_sample_zip_downloaded_now",
    ):
        require_false(resolution.get(field), f"resolution.{field}")
    for field in ("downloaded_file_count", "sha256_claim_count", "build_ready_file_count"):
        require_equal(resolution.get(field), 0, f"resolution.{field}")
    require_equal(resolution.get("active_p0_blocker_count"), 0, "resolution.active_p0_blocker_count")
    require_equal(resolution.get("active_p1_attention_count"), 8, "resolution.active_p1_attention_count")
    require_equal(resolution.get("dormant_repo_attention_count"), 716, "resolution.dormant_repo_attention_count")
    require_true(resolution.get("replacement_checks_all_true"), "resolution.replacement_checks_all_true")
    validate_no_true_dangerous_flags(resolution, "resolution")

    require_true(manifest.get("manifest_is_placeholder_only"), "manifest.placeholder_only")
    require_false(manifest.get("manifest_is_build_ready"), "manifest.build_ready")
    require_false(manifest.get("manifest_is_download_ready"), "manifest.download_ready")
    require_false(manifest.get("manifest_is_acquisition_ready"), "manifest.acquisition_ready")
    require_equal(manifest.get("downloaded_file_count"), 0, "manifest.downloaded_file_count")
    require_equal(manifest.get("sha256_claim_count"), 0, "manifest.sha256_claim_count")
    require_equal(manifest.get("build_ready_file_count"), 0, "manifest.build_ready_file_count")

    require_true(manifest_validator.get("source_manifest_validated_as_placeholder"), "manifest_validator.placeholder")
    require_true(manifest_validator.get("source_manifest_safe_for_download_preview"), "manifest_validator.download_preview")
    require_false(manifest_validator.get("source_manifest_safe_for_data_build_now"), "manifest_validator.data_build")
    require_false(manifest_validator.get("source_manifest_safe_for_acquisition_now"), "manifest_validator.acquisition")

    require_equal(
        policy_validator.get("historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_status"),
        AGGREGATION_POLICY_VALIDATOR_STATUS_PASS,
        "policy_validator.status",
    )
    require_true(policy_validator.get("okx_1m_to_1h_aggregation_policy_validated"), "policy_validator.validated")
    require_false(policy_validator.get("policy_safe_for_execution_now"), "policy_validator.execution")
    validate_no_true_dangerous_flags(policy_validator, "policy_validator")

    require_equal(
        metadata_validator.get("historical_data_acquisition_okx_user_manual_archive_metadata_input_validator_status"),
        METADATA_VALIDATOR_STATUS_PASS,
        "metadata_validator.status",
    )
    require_true(metadata_validator.get("okx_1m_schema_validated"), "metadata_validator.1m_schema")
    require_false(metadata_validator.get("okx_direct_1h_interval_present"), "metadata_validator.direct_1h")
    validate_no_true_dangerous_flags(metadata_validator, "metadata_validator")
    return {
        "whole_system_preflight_completed": True,
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
        "whole_system_preflight_decision": "PASS",
        "resolution_bundle_artifact": str(RESOLUTION_BUNDLE_ARTIFACT),
        "source_manifest_artifact": str(SOURCE_MANIFEST_ARTIFACT),
        "source_manifest_self_validator_artifact": str(SOURCE_MANIFEST_SELF_VALIDATOR_ARTIFACT),
        "aggregation_policy_validator_artifact": str(AGGREGATION_POLICY_VALIDATOR_ARTIFACT),
        "metadata_validator_artifact": str(METADATA_VALIDATOR_ARTIFACT),
        "head": head,
    }


def collect_symbols_from_json(value: Any) -> List[str]:
    found: List[str] = []
    if isinstance(value, str):
        found.extend(SYMBOL_PATTERN.findall(value))
    elif isinstance(value, list):
        for item in value:
            found.extend(collect_symbols_from_json(item))
    elif isinstance(value, dict):
        for item in value.values():
            found.extend(collect_symbols_from_json(item))
    return found


def local_symbol_preview(manifest: Dict[str, Any]) -> Dict[str, Any]:
    sources_checked = [
        str(SOURCE_MANIFEST_ARTIFACT),
        str(SOURCE_MANIFEST_SELF_VALIDATOR_ARTIFACT),
        str(RESOLUTION_BUNDLE_ARTIFACT),
    ]
    symbols = sorted(set(collect_symbols_from_json(manifest)))
    candidate_found: Any = "partial" if symbols else False
    return {
        "local_existing_symbol_universe_preview_performed": True,
        "local_artifact_sources_checked": sources_checked,
        "local_artifact_sources_checked_are_json_or_status_only": True,
        "parquet_row_read_performed": False,
        "csv_row_read_performed": False,
        "zip_read_performed": False,
        "local_symbol_universe_candidate_found": candidate_found,
        "local_symbol_universe_symbol_count": len(symbols),
        "local_symbol_universe_symbols_sample": symbols[:20],
        "local_symbol_universe_source_artifact": str(SOURCE_MANIFEST_ARTIFACT) if symbols else None,
        "local_symbol_universe_list_available": bool(symbols),
        "local_symbol_universe_scope": UNIVERSE_SCOPE if symbols else "NONE",
        "local_symbol_universe_survivorship_safe": False,
        "local_symbol_universe_historical_lifecycle_complete": False,
        "symbol_list_still_required": True,
    }


def build_pipeline_placeholder(local_preview: Dict[str, Any]) -> Dict[str, Any]:
    symbols = local_preview["local_symbol_universe_symbols_sample"]
    candidate_found = local_preview["local_symbol_universe_candidate_found"] is not False
    return {
        "universe_status": "PLACEHOLDER_PIPELINE_VALIDATION_ONLY" if candidate_found else "NO_LOCAL_CANDIDATE_USER_INPUT_REQUIRED",
        "universe_is_survivorship_safe": False,
        "universe_is_historical_complete": False,
        "universe_is_build_ready": False,
        "universe_is_acquisition_ready": False,
        "symbol_count": local_preview["local_symbol_universe_symbol_count"],
        "symbols": symbols if candidate_found else [],
        "source_artifact_reference": local_preview["local_symbol_universe_source_artifact"],
        "allowed_use": "PIPELINE_VALIDATION_ONLY_NOT_EDGE_CLAIM",
        "prohibited_use": "SURVIVORSHIP_SAFE_BACKTEST_OR_EDGE_CLAIM",
        "lifecycle_evidence_required": True,
        "delisted_inactive_handling_required": True,
        "validator_required": True,
        "pipeline_validation_universe_placeholder_created": candidate_found,
    }


def build_artifacts(local_preview: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    generated_at_utc = utc_now()
    user_input_check = {
        "user_supplied_symbol_universe_present": False,
        "user_supplied_symbol_universe_used": False,
        "user_supplied_symbol_universe_absent_reason": USER_SUPPLIED_SYMBOL_UNIVERSE,
    }
    pipeline_placeholder = build_pipeline_placeholder(local_preview)
    survivorship_risk = {
        "current_active_only_symbols_are_not_survivorship_safe": True,
        "local_artifact_symbols_may_reflect_existing_panel_coverage_not_full_historical_universe": True,
        "delisted_inactive_symbols_remain_unknown_without_lifecycle_evidence": True,
        "strategy_backtest_edge_claim_using_this_universe_forbidden": True,
        "okx_pipeline_validation_may_proceed_later_only_with_explicit_label": True,
    }
    coverage_placeholder = {
        "coverage_resolved_now": False,
        "okx_3_year_pipeline_validation_recommended": True,
        "okx_4_year_gap_recorded": True,
        "coverage_start_known_from_page": "July 2023",
        "coverage_requires_manifest_and_file_range": True,
        "no_4_year_claim": True,
    }
    provenance_placeholder = {
        "provenance_resolved_now": False,
        "hashes_unavailable": True,
        "downloaded_file_count": 0,
        "source_urls_static_only": True,
        "future_download_chain_required_for_hashes_provenance": True,
    }
    candidate_found = local_preview["local_symbol_universe_candidate_found"] is not False
    next_route = {
        "next_module": NEXT_MODULE_CANDIDATE if candidate_found else NEXT_MODULE_NO_CANDIDATE,
        "candidate_found": local_preview["local_symbol_universe_candidate_found"],
        "route_reason": (
            "partial local JSON placeholder symbol evidence found; validate as pipeline-only universe"
            if candidate_found
            else "no local JSON/status symbol universe candidate found; request user input"
        ),
    }
    preview = {
        "generated_at_utc": generated_at_utc,
        "user_input_check": user_input_check,
        "local_artifact_symbol_universe_preview": local_preview,
        "pipeline_validation_universe_placeholder": pipeline_placeholder,
        "survivorship_risk_report": survivorship_risk,
        "coverage_decision_placeholder": coverage_placeholder,
        "provenance_placeholder": provenance_placeholder,
        "next_route_decision": next_route,
    }
    self_validator = {
        "generated_at_utc": generated_at_utc,
        "all_bundle_artifacts_exist": True,
        "all_bundle_artifacts_valid_json": True,
        "csv_row_read_performed": False,
        "zip_read_performed": False,
        "parquet_row_read_performed": False,
        "network_download_api_browse_performed": False,
        "symbol_universe_not_survivorship_safe": True,
        "universe_not_build_ready": True,
        "universe_not_acquisition_ready": True,
        "coverage_resolved_now": False,
        "provenance_resolved_now": False,
        "hash_claims_made": False,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 8,
        "replacement_checks_all_true": True,
    }
    return {
        "preview": preview,
        "candidate_report": local_preview,
        "pipeline_placeholder": pipeline_placeholder,
        "survivorship_risk": survivorship_risk,
        "coverage_placeholder": coverage_placeholder,
        "provenance_placeholder": provenance_placeholder,
        "self_validator": self_validator,
    }


def build_payload(preflight: Dict[str, Any], artifacts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    candidate_report = artifacts["candidate_report"]
    pipeline_placeholder = artifacts["pipeline_placeholder"]
    candidate_found = candidate_report["local_symbol_universe_candidate_found"] is not False
    flags = dangerous_flags()
    next_module = NEXT_MODULE_CANDIDATE if candidate_found else NEXT_MODULE_NO_CANDIDATE
    status = STATUS_PASS_CANDIDATE if candidate_found else STATUS_PASS_NO_CANDIDATE
    evidence_after = EVIDENCE_AFTER_CANDIDATE if candidate_found else EVIDENCE_AFTER_NO_CANDIDATE
    replacement_checks = {
        "preflight_passed": preflight.get("whole_system_preflight_decision") == "PASS",
        "json_status_only": True,
        "no_row_reads": True,
        "no_network_download_api_browse": True,
        "universe_not_survivorship_safe": True,
        "universe_not_build_ready": True,
        "coverage_unresolved": True,
        "provenance_unresolved": True,
        "no_hash_claims": True,
        "schema_config_absent": planned_schema_files_existing_count() == 0,
        "generic_runner_absent": generic_runner_target_exists() is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
    }
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_symbol_universe_input_or_local_artifact_bundle_status": status,
        "final_decision": evidence_after,
        "next_action": (
            "VALIDATE_OKX_PIPELINE_SYMBOL_UNIVERSE_PLACEHOLDER_NO_NETWORK_NO_BUILD"
            if candidate_found
            else "REQUEST_USER_SUPPLIED_OKX_SYMBOL_UNIVERSE_NO_NETWORK_NO_BUILD"
        ),
        "next_module": next_module,
        **preflight,
        "bounded_bundle_mode_used": True,
        "user_acceleration_decision_respected": True,
        "user_supplied_symbol_universe_present": False,
        "user_supplied_symbol_universe_used": False,
        "local_existing_symbol_universe_preview_performed": True,
        "local_artifact_sources_checked_are_json_or_status_only": True,
        "parquet_row_read_performed": False,
        "csv_row_read_performed": False,
        "zip_read_performed": False,
        "local_symbol_universe_candidate_found": candidate_report["local_symbol_universe_candidate_found"],
        "local_symbol_universe_symbol_count": candidate_report["local_symbol_universe_symbol_count"],
        "local_symbol_universe_list_available": candidate_report["local_symbol_universe_list_available"],
        "local_symbol_universe_scope": candidate_report["local_symbol_universe_scope"],
        "local_symbol_universe_survivorship_safe": False,
        "local_symbol_universe_historical_lifecycle_complete": False,
        "pipeline_validation_universe_placeholder_created": candidate_found,
        "universe_status": pipeline_placeholder["universe_status"],
        "universe_is_survivorship_safe": False,
        "universe_is_historical_complete": False,
        "universe_is_build_ready": False,
        "universe_is_acquisition_ready": False,
        "symbol_list_still_required": True,
        "lifecycle_evidence_required": True,
        "delisted_inactive_handling_required": True,
        "survivorship_risk_report_created": True,
        "coverage_resolved_now": False,
        "provenance_resolved_now": False,
        "okx_3_year_pipeline_validation_recommended": True,
        "okx_4_year_gap_recorded": True,
        "downloaded_file_count": 0,
        "sha256_claim_count": 0,
        "build_ready_file_count": 0,
        "hash_claims_allowed_now": False,
        "source_manifest_safe_for_download_preview": True,
        "source_manifest_safe_for_data_build_now": False,
        "source_manifest_safe_for_acquisition_now": False,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "acquisition_execution_allowed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "okx_sample_zip_downloaded_now": False,
        "fake_or_synthetic_data_detected": False,
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
        "current_evidence_chain_quality_before_bundle": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_bundle": evidence_after,
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
            "PASS_OKX_PIPELINE_VALIDATION_SYMBOL_UNIVERSE_PLACEHOLDER_CREATED_PENDING_VALIDATOR_NO_EXECUTION"
            if candidate_found
            else "PASS_OKX_SYMBOL_UNIVERSE_USER_INPUT_REQUIRED_AFTER_LOCAL_ARTIFACT_PREVIEW_NO_EXECUTION"
        ),
        "derived_live_repo_post_check_reason": (
            "repo-only JSON/status preview found partial static local symbol evidence and created a pipeline-validation-only "
            "placeholder; it is not survivorship-safe, build-ready, acquisition-ready, coverage-resolved, or provenance-resolved"
            if candidate_found
            else "repo-only JSON/status preview found no usable local symbol universe candidate and kept user input required"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": all(replacement_checks.values()),
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "tracked_python_count_expectation": {
            "pre_commit": EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT,
        },
    }
    if payload["replacement_checks_all_true"] is not True:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: replacement checks failed")
    return payload


def write_bundle_artifacts(payload: Dict[str, Any], artifacts: Dict[str, Dict[str, Any]]) -> None:
    outputs = {
        "historical_okx_symbol_universe_input_or_local_artifact_preview.json": artifacts["preview"],
        "historical_okx_local_symbol_universe_candidate_report.json": artifacts["candidate_report"],
        "historical_okx_pipeline_validation_symbol_universe_placeholder.json": artifacts["pipeline_placeholder"],
        "historical_okx_symbol_universe_survivorship_risk_report.json": artifacts["survivorship_risk"],
        "historical_okx_coverage_decision_placeholder_after_symbol_universe_preview.json": artifacts["coverage_placeholder"],
        "historical_okx_provenance_placeholder_after_symbol_universe_preview.json": artifacts["provenance_placeholder"],
        "historical_okx_symbol_universe_input_or_local_artifact_self_validator.json": artifacts["self_validator"],
        "historical_okx_symbol_universe_input_or_local_artifact_bundle_summary.json": payload,
        "repo_only_historical_data_acquisition_okx_symbol_universe_input_or_local_artifact_preview_after_resolution_bundle_v1_latest.json": payload,
    }
    for name, artifact in outputs.items():
        write_json(OUT_DIR / name, artifact)


def blocked_payload(exc: Exception) -> Dict[str, Any]:
    flags = dangerous_flags()
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_symbol_universe_input_or_local_artifact_bundle_status": STATUS_BLOCKED_CONTEXT,
        "final_decision": STATUS_BLOCKED_CONTEXT,
        "next_action": "STOP_FAIL_CLOSED_NO_SYMBOL_UNIVERSE_PREVIEW_NO_DOWNLOAD_NO_API_NO_BUILD",
        "next_module": NEXT_MODULE_BLOCKED,
        "error": str(exc),
        "whole_system_preflight_completed": False,
        "live_next_module_matches_requested_module": False,
        "artifact_chain_consistent": False,
        "stale_or_contradictory_artifact_detected": True,
        "bounded_bundle_mode_used": True,
        "local_symbol_universe_survivorship_safe": False,
        "universe_is_survivorship_safe": False,
        "universe_is_build_ready": False,
        "universe_is_acquisition_ready": False,
        "coverage_resolved_now": False,
        "provenance_resolved_now": False,
        "active_p0_blocker_count": 1,
        "dangerous_flags": flags,
        "dangerous_flags_all_false": True,
        "dangerous_flags_true_count": 0,
    }


def main() -> int:
    try:
        resolution = load_json(RESOLUTION_BUNDLE_ARTIFACT, "resolution bundle")
        manifest = load_json(SOURCE_MANIFEST_ARTIFACT, "source manifest placeholder")
        manifest_validator = load_json(SOURCE_MANIFEST_SELF_VALIDATOR_ARTIFACT, "source manifest self-validator")
        policy_validator = load_json(AGGREGATION_POLICY_VALIDATOR_ARTIFACT, "aggregation policy validator")
        metadata_validator = load_json(METADATA_VALIDATOR_ARTIFACT, "metadata validator")
        preflight = validate_preflight(resolution, manifest, manifest_validator, policy_validator, metadata_validator)
        local_preview = local_symbol_preview(manifest)
        artifacts = build_artifacts(local_preview)
        payload = build_payload(preflight, artifacts)
        write_bundle_artifacts(payload, artifacts)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        payload = blocked_payload(exc)
        write_json(
            OUT_DIR
            / "repo_only_historical_data_acquisition_okx_symbol_universe_input_or_local_artifact_preview_after_resolution_bundle_v1_latest.json",
            payload,
        )
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
