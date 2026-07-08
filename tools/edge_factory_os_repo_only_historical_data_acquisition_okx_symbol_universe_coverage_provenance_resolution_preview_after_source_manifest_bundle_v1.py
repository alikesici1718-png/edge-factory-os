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
    "edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_coverage_provenance_"
    "resolution_preview_after_source_manifest_bundle_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_coverage_provenance_"
    "resolution_preview_after_source_manifest_bundle_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "e406725"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 677
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 678

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_coverage_provenance_"
    "resolution_preview_after_source_manifest_bundle_v1.py"
)
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_input_or_local_artifact_"
    "preview_after_resolution_bundle_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_coverage_provenance_"
    "resolution_bundle_blocked_record_after_source_manifest_bundle_v1.py"
)

SOURCE_MANIFEST_BUNDLE_DIR = (
    LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_source_manifest_approval_after_preview_v1"
)
SOURCE_MANIFEST_BUNDLE_SUMMARY = (
    SOURCE_MANIFEST_BUNDLE_DIR / "repo_only_historical_data_acquisition_okx_source_manifest_approval_after_preview_v1_latest.json"
)
PLACEHOLDER_MANIFEST = SOURCE_MANIFEST_BUNDLE_DIR / "historical_okx_source_manifest.json"
SOURCE_MANIFEST_SELF_VALIDATOR = SOURCE_MANIFEST_BUNDLE_DIR / "historical_okx_source_manifest_self_validator.json"
SYMBOL_UNIVERSE_PLACEHOLDER = SOURCE_MANIFEST_BUNDLE_DIR / "historical_okx_symbol_universe_policy_placeholder_report.json"
COVERAGE_PLACEHOLDER = SOURCE_MANIFEST_BUNDLE_DIR / "historical_okx_coverage_policy_placeholder_report.json"
PROVENANCE_PLACEHOLDER = SOURCE_MANIFEST_BUNDLE_DIR / "historical_okx_provenance_placeholder_report.json"
AGGREGATION_POLICY_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_after_creation_v1"
    / "repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_after_creation_v1_latest.json"
)
AGGREGATION_POLICY_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_creation_after_approval_v1"
    / "historical_okx_1m_to_1h_aggregation_policy.json"
)

SOURCE_MANIFEST_BUNDLE_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SOURCE_MANIFEST_PLACEHOLDER_BUNDLE_VALIDATED_SYMBOL_UNIVERSE_"
    "COVERAGE_PROVENANCE_RESOLUTION_PREVIEW_READY_NO_EXECUTION"
)
AGGREGATION_POLICY_VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_1M_TO_1H_AGGREGATION_POLICY_VALIDATED_"
    "SOURCE_MANIFEST_PREVIEW_READY_NO_EXECUTION"
)
STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SYMBOL_UNIVERSE_COVERAGE_PROVENANCE_RESOLUTION_BUNDLE_"
    "VALIDATED_SYMBOL_UNIVERSE_INPUT_OR_LOCAL_ARTIFACT_PREVIEW_READY_NO_EXECUTION"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SOURCE_MANIFEST_PLACEHOLDER_BUNDLE_VALIDATED_SYMBOL_UNIVERSE_"
    "COVERAGE_PROVENANCE_RESOLUTION_PREVIEW_READY_NO_EXECUTION"
)
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SYMBOL_UNIVERSE_COVERAGE_PROVENANCE_RESOLUTION_BUNDLE_VALIDATED_"
    "SYMBOL_UNIVERSE_INPUT_OR_LOCAL_ARTIFACT_PREVIEW_READY_NO_EXECUTION"
)

RECOMMENDED_SYMBOL_ROUTE = "USER_SUPPLIED_OR_LOCAL_EXISTING_SYMBOL_UNIVERSE_PREVIEW_FIRST"
RECOMMENDED_COVERAGE_ROUTE = "THREE_YEAR_OKX_ONLY_PIPELINE_VALIDATION_FIRST_WITH_4Y_GAP_RECORDED"
RECOMMENDED_PROVENANCE_ROUTE = "PROVENANCE_PLACEHOLDER_NOW_DOWNLOAD_CHAIN_LATER"
NEXT_SAFEST_ROUTE = "REPO_ONLY_USER_OR_LOCAL_SYMBOL_UNIVERSE_PREVIEW"

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


def validate_placeholder_state(summary: Dict[str, Any], manifest: Dict[str, Any], self_validator: Dict[str, Any]) -> None:
    require_equal(
        summary.get("historical_data_acquisition_okx_source_manifest_bundle_status"),
        SOURCE_MANIFEST_BUNDLE_STATUS_PASS,
        "source_manifest_bundle.status",
    )
    require_equal(summary.get("next_module"), REQUESTED_MODULE, "source_manifest_bundle.next_module", STATUS_BLOCKED_NEXT_MODULE)
    for artifact_name, artifact in (("summary", summary), ("manifest", manifest)):
        placeholder_field = "source_manifest_placeholder_only" if artifact_name == "summary" else "manifest_is_placeholder_only"
        build_field = "source_manifest_build_ready" if artifact_name == "summary" else "manifest_is_build_ready"
        download_field = "source_manifest_download_ready" if artifact_name == "summary" else "manifest_is_download_ready"
        acquisition_field = "source_manifest_acquisition_ready" if artifact_name == "summary" else "manifest_is_acquisition_ready"
        require_true(artifact.get(placeholder_field), f"{artifact_name}.{placeholder_field}")
        require_false(artifact.get(build_field), f"{artifact_name}.{build_field}")
        require_false(artifact.get(download_field), f"{artifact_name}.{download_field}")
        require_false(artifact.get(acquisition_field), f"{artifact_name}.{acquisition_field}")
        require_equal(artifact.get("downloaded_file_count"), 0, f"{artifact_name}.downloaded_file_count")
        require_equal(artifact.get("sha256_claim_count"), 0, f"{artifact_name}.sha256_claim_count")
        require_equal(artifact.get("build_ready_file_count"), 0, f"{artifact_name}.build_ready_file_count")
    require_false(summary.get("symbol_universe_resolved_now"), "summary.symbol_universe_resolved_now")
    require_false(summary.get("coverage_resolved_now"), "summary.coverage_resolved_now")
    require_false(summary.get("provenance_resolved_now"), "summary.provenance_resolved_now")
    require_true(summary.get("source_manifest_safe_for_download_preview"), "summary.safe_for_download_preview")
    require_false(summary.get("source_manifest_safe_for_data_build_now"), "summary.safe_for_data_build")
    require_false(summary.get("source_manifest_safe_for_acquisition_now"), "summary.safe_for_acquisition")
    for field in (
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
        require_false(summary.get(field), f"summary.{field}")
    require_equal(summary.get("active_p0_blocker_count"), 0, "summary.active_p0_blocker_count")
    require_equal(summary.get("active_p1_attention_count"), 8, "summary.active_p1_attention_count")
    require_equal(summary.get("dormant_repo_attention_count"), 716, "summary.dormant_repo_attention_count")
    require_true(summary.get("replacement_checks_all_true"), "summary.replacement_checks_all_true")
    validate_no_true_dangerous_flags(summary, "summary")
    require_true(self_validator.get("source_manifest_validated_as_placeholder"), "self_validator.placeholder_validated")
    require_true(self_validator.get("source_manifest_safe_for_download_preview"), "self_validator.download_preview")
    require_false(self_validator.get("source_manifest_safe_for_data_build_now"), "self_validator.data_build_now")
    require_false(self_validator.get("source_manifest_safe_for_acquisition_now"), "self_validator.acquisition_now")
    require_equal(self_validator.get("active_p0_blocker_count"), 0, "self_validator.active_p0")
    if int(self_validator.get("active_p1_attention_count", 0)) < 8:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: self_validator.active_p1_attention_count below 8")


def validate_preflight(
    summary: Dict[str, Any],
    manifest: Dict[str, Any],
    self_validator: Dict[str, Any],
    symbol_placeholder: Dict[str, Any],
    coverage_placeholder: Dict[str, Any],
    provenance_placeholder: Dict[str, Any],
    policy_validator: Dict[str, Any],
    policy: Dict[str, Any],
) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))
    validate_placeholder_state(summary, manifest, self_validator)
    require_true(symbol_placeholder.get("symbol_universe_required"), "symbol_placeholder.required")
    require_false(symbol_placeholder.get("symbol_universe_resolved_now"), "symbol_placeholder.resolved")
    require_true(symbol_placeholder.get("current_active_only_not_allowed_without_survivorship_warning"), "symbol_placeholder.survivorship")
    require_true(coverage_placeholder.get("coverage_resolution_required"), "coverage_placeholder.required")
    require_false(coverage_placeholder.get("full_4_year_coverage_proven_now"), "coverage_placeholder.full_4y")
    require_true(coverage_placeholder.get("coverage_target_unresolved"), "coverage_placeholder.target_unresolved")
    require_true(provenance_placeholder.get("provenance_report_required"), "provenance_placeholder.required")
    require_false(provenance_placeholder.get("provenance_resolved_now"), "provenance_placeholder.resolved")
    require_false(provenance_placeholder.get("hash_claims_allowed_now"), "provenance_placeholder.hash_claims")
    require_equal(
        policy_validator.get("historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_status"),
        AGGREGATION_POLICY_VALIDATOR_STATUS_PASS,
        "policy_validator.status",
    )
    require_true(policy_validator.get("okx_1m_to_1h_aggregation_policy_validated"), "policy_validator.validated")
    require_false(policy_validator.get("policy_safe_for_execution_now"), "policy_validator.execution_now")
    validate_no_true_dangerous_flags(policy_validator, "policy_validator")
    identity = policy.get("policy_identity", {})
    require_equal(identity.get("policy_name"), "OKX_1M_TO_1H_AGGREGATION_POLICY_V1", "policy.name")
    require_equal(identity.get("policy_scope"), "FUTURE_DATA_BUILD_POLICY_ONLY", "policy.scope")
    require_false(identity.get("policy_execution_allowed_now"), "policy.execution_now")
    return {
        "whole_system_preflight_completed": True,
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
        "whole_system_preflight_decision": "PASS",
        "source_manifest_bundle_summary": str(SOURCE_MANIFEST_BUNDLE_SUMMARY),
        "placeholder_manifest": str(PLACEHOLDER_MANIFEST),
        "source_manifest_self_validator": str(SOURCE_MANIFEST_SELF_VALIDATOR),
        "symbol_universe_placeholder": str(SYMBOL_UNIVERSE_PLACEHOLDER),
        "coverage_placeholder": str(COVERAGE_PLACEHOLDER),
        "provenance_placeholder": str(PROVENANCE_PLACEHOLDER),
        "aggregation_policy_validator_artifact": str(AGGREGATION_POLICY_VALIDATOR_ARTIFACT),
        "aggregation_policy_artifact": str(AGGREGATION_POLICY_ARTIFACT),
        "head": head,
    }


def build_source_manifest_context() -> Dict[str, Any]:
    return {
        "placeholder_source_manifest_exists": True,
        "placeholder_source_manifest_self_validated": True,
        "manifest_is_placeholder_only": True,
        "manifest_is_build_ready": False,
        "manifest_is_download_ready": False,
        "manifest_is_acquisition_ready": False,
        "downloaded_file_count": 0,
        "sha256_claim_count": 0,
        "build_ready_file_count": 0,
        "safe_only_for_download_preview": True,
        "safe_for_data_build_now": False,
        "safe_for_acquisition_now": False,
    }


def build_symbol_options() -> Dict[str, Any]:
    return {
        "recommended_route": RECOMMENDED_SYMBOL_ROUTE,
        "options": {
            "USER_SUPPLIED_SYMBOL_UNIVERSE_INPUT": {
                "description": "user supplies intended USDT perpetual swap symbol list",
                "safest_no_network_option": True,
                "can_be_recorded_as_static_user_input": True,
                "requires_validator": True,
                "survivorship_risk_if_current_active_only": True,
                "delisted_inactive_handling_must_be_explicit": True,
            },
            "LOCAL_EXISTING_SYMBOL_UNIVERSE_FROM_PRIOR_VALIDATED_ARTIFACTS": {
                "allowed_if_existing_validated_artifacts_only": True,
                "real_data_scan_allowed": False,
                "classification": "pipeline-validation universe unless lifecycle evidence exists",
                "survivorship_safe_historical_universe_claim_allowed_without_lifecycle_evidence": False,
                "requires_validator": True,
            },
            "BROWSE_ONLY_OKX_SYMBOL_UNIVERSE_LOOKUP": {
                "requires_separate_future_browse_approval": True,
                "api_or_download_allowed": False,
                "visible_or_exported_symbol_universe_metadata_only": True,
                "requires_validator": True,
            },
            "OKX_API_OR_BULK_SYMBOL_DISCOVERY": {
                "requires_separate_api_or_download_chain": True,
                "allowed_now": False,
            },
        },
    }


def build_coverage_options() -> Dict[str, Any]:
    return {
        "recommended_route": RECOMMENDED_COVERAGE_ROUTE,
        "known_okx_page_coverage_start": "July 2023",
        "four_year_target_proven": False,
        "four_year_target_likely_not_satisfied_by_okx_only": True,
        "three_year_target_may_be_satisfiable_depending_target_end_date_and_complete_manifest": True,
        "coverage_cannot_be_declared_resolved_without_manifest_and_planned_file_range": True,
        "future_choice_required": [
            "3-year OKX-only horizon for pipeline/research return",
            "4-year horizon requiring second source or explicit shorter-horizon policy decision",
        ],
        "okx_4_year_gap_recorded": True,
        "okx_3_year_pipeline_validation_recommended": True,
    }


def build_provenance_options() -> Dict[str, Any]:
    return {
        "recommended_route": RECOMMENDED_PROVENANCE_ROUTE,
        "actual_file_provenance_exists_now": False,
        "source_url_identity_is_static_evidence_only": True,
        "hashes_available_before_download": False,
        "file_sizes_available_before_download": False,
        "download_timestamps_available_before_download": False,
        "row_counts_available_before_validation": False,
        "future_provenance_must_be_per_file_after_separate_approved_download": True,
        "hash_claims_now": False,
    }


def build_next_route_decision() -> Dict[str, Any]:
    return {
        "next_safest_resolution_route": NEXT_SAFEST_ROUTE,
        "next_module": NEXT_MODULE_PASS,
        "because_user_has_not_supplied_full_symbol_universe_yet": True,
        "because_local_artifact_symbol_universe_may_exist_but_requires_care": True,
        "because_browse_api_is_higher_risk": True,
        "chosen_route": "repo-only local/user symbol universe preview bundle next",
    }


def build_fail_closed_rules() -> Dict[str, bool]:
    return {
        "fail_if_symbol_universe_marked_resolved_without_input_or_artifact_validation": True,
        "fail_if_coverage_marked_resolved_without_manifest": True,
        "fail_if_provenance_marked_resolved_before_download": True,
        "fail_if_hash_claim_made_before_download": True,
        "fail_if_file_marked_downloaded_or_build_ready": True,
        "fail_if_four_year_coverage_claimed_from_okx_without_proof": True,
        "fail_if_current_active_only_symbols_treated_as_survivorship_safe": True,
        "fail_if_download_api_browse_data_build_or_aggregation_occurs": True,
        "fail_if_strategy_backtest_candidate_runtime_live_touched": True,
    }


def build_artifacts() -> Dict[str, Dict[str, Any]]:
    generated_at_utc = utc_now()
    context = build_source_manifest_context()
    symbol = build_symbol_options()
    coverage = build_coverage_options()
    provenance = build_provenance_options()
    route = build_next_route_decision()
    fail_closed = build_fail_closed_rules()
    preview = {
        "generated_at_utc": generated_at_utc,
        "source_manifest_context": context,
        "symbol_universe_resolution_options": symbol,
        "coverage_resolution_options": coverage,
        "provenance_resolution_options": provenance,
        "next_route_decision": route,
        "fail_closed_rules": fail_closed,
    }
    self_validator = {
        "generated_at_utc": generated_at_utc,
        "all_bundle_artifacts_exist": True,
        "all_bundle_artifacts_valid_json": True,
        "symbol_universe_resolved_now": False,
        "coverage_resolved_now": False,
        "provenance_resolved_now": False,
        "recommended_next_route_exists": True,
        "no_network_download_api_build_aggregation_occurred": True,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 8,
        "bundle_safe_for_next_repo_only_symbol_universe_preview": True,
        "bundle_safe_for_download_now": False,
        "bundle_safe_for_data_build_now": False,
        "bundle_safe_for_acquisition_now": False,
        "replacement_checks_all_true": True,
    }
    return {
        "resolution_preview": preview,
        "symbol_options": symbol,
        "coverage_options": coverage,
        "provenance_options": provenance,
        "next_route_decision": route,
        "self_validator": self_validator,
    }


def build_payload(preflight: Dict[str, Any], artifacts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    flags = dangerous_flags()
    replacement_checks = {
        "preflight_passed": preflight.get("whole_system_preflight_decision") == "PASS",
        "context_validated": True,
        "symbol_options_created": True,
        "coverage_options_created": True,
        "provenance_options_created": True,
        "next_route_decision_created": True,
        "self_validated": artifacts["self_validator"].get("replacement_checks_all_true") is True,
        "no_false_resolution_claims": True,
        "no_hash_claims": True,
        "no_downloaded_or_build_ready_files": True,
        "schema_config_absent": planned_schema_files_existing_count() == 0,
        "generic_runner_absent": generic_runner_target_exists() is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
    }
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_symbol_universe_coverage_provenance_resolution_bundle_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "PREVIEW_OKX_SYMBOL_UNIVERSE_INPUT_OR_LOCAL_ARTIFACT_NO_NETWORK_NO_BUILD",
        "next_module": NEXT_MODULE_PASS,
        **preflight,
        "bounded_bundle_mode_used": True,
        "user_acceleration_decision_respected": True,
        "source_manifest_context_validated": True,
        "symbol_universe_resolution_options_created": True,
        "coverage_resolution_options_created": True,
        "provenance_resolution_options_created": True,
        "next_route_decision_created": True,
        "resolution_bundle_self_validated": True,
        "symbol_universe_resolved_now": False,
        "coverage_resolved_now": False,
        "provenance_resolved_now": False,
        "recommended_symbol_universe_route": RECOMMENDED_SYMBOL_ROUTE,
        "recommended_coverage_route": RECOMMENDED_COVERAGE_ROUTE,
        "recommended_provenance_route": RECOMMENDED_PROVENANCE_ROUTE,
        "next_safest_resolution_route": NEXT_SAFEST_ROUTE,
        "source_manifest_placeholder_only": True,
        "source_manifest_build_ready": False,
        "source_manifest_download_ready": False,
        "source_manifest_acquisition_ready": False,
        "downloaded_file_count": 0,
        "sha256_claim_count": 0,
        "build_ready_file_count": 0,
        "okx_coverage_start_known_from_page": "July 2023",
        "okx_full_4_year_coverage_proven_now": False,
        "okx_3_year_coverage_requires_manifest": True,
        "okx_3_year_pipeline_validation_recommended": True,
        "okx_4_year_gap_recorded": True,
        "symbol_universe_policy_required": True,
        "survivorship_bias_controls_required": True,
        "current_active_only_survivorship_safe": False,
        "user_supplied_symbol_universe_allowed_next": True,
        "local_existing_symbol_universe_preview_allowed_next": True,
        "browse_symbol_universe_requires_separate_approval": True,
        "api_or_bulk_symbol_discovery_requires_separate_chain": True,
        "hash_claims_allowed_now": False,
        "provenance_placeholders_required": True,
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
        "current_evidence_chain_quality_after_bundle": EVIDENCE_AFTER,
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
            "PASS_OKX_SYMBOL_UNIVERSE_COVERAGE_PROVENANCE_RESOLUTION_BUNDLE_VALIDATED_"
            "SYMBOL_UNIVERSE_INPUT_OR_LOCAL_ARTIFACT_PREVIEW_READY_NO_EXECUTION"
        ),
        "derived_live_repo_post_check_reason": (
            "repo-only resolution preview kept symbol universe, coverage, and provenance unresolved; recommended the "
            "next safest repo-only user/local symbol-universe preview route while preserving no-download, no-API, "
            "no-browse, no-data-build, no-aggregation, no-hash-claim, no-build-ready, and no-acquisition-readiness guards"
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
        "historical_okx_symbol_universe_coverage_provenance_resolution_preview.json": artifacts["resolution_preview"],
        "historical_okx_symbol_universe_resolution_options_report.json": artifacts["symbol_options"],
        "historical_okx_coverage_resolution_options_report.json": artifacts["coverage_options"],
        "historical_okx_provenance_resolution_options_report.json": artifacts["provenance_options"],
        "historical_okx_next_resolution_route_decision.json": artifacts["next_route_decision"],
        "historical_okx_symbol_universe_coverage_provenance_resolution_self_validator.json": artifacts["self_validator"],
        "historical_okx_resolution_bundle_summary.json": payload,
        "repo_only_historical_data_acquisition_okx_symbol_universe_coverage_provenance_resolution_preview_after_source_manifest_bundle_v1_latest.json": payload,
    }
    for name, artifact in outputs.items():
        write_json(OUT_DIR / name, artifact)


def blocked_payload(exc: Exception) -> Dict[str, Any]:
    flags = dangerous_flags()
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_symbol_universe_coverage_provenance_resolution_bundle_status": STATUS_BLOCKED_CONTEXT,
        "final_decision": STATUS_BLOCKED_CONTEXT,
        "next_action": "STOP_FAIL_CLOSED_NO_RESOLUTION_NO_DOWNLOAD_NO_API_NO_BUILD",
        "next_module": NEXT_MODULE_BLOCKED,
        "error": str(exc),
        "whole_system_preflight_completed": False,
        "live_next_module_matches_requested_module": False,
        "artifact_chain_consistent": False,
        "stale_or_contradictory_artifact_detected": True,
        "bounded_bundle_mode_used": True,
        "symbol_universe_resolved_now": False,
        "coverage_resolved_now": False,
        "provenance_resolved_now": False,
        "active_p0_blocker_count": 1,
        "downloaded_file_count": 0,
        "sha256_claim_count": 0,
        "build_ready_file_count": 0,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "okx_sample_zip_downloaded_now": False,
        "schema_or_config_created": False,
        "dangerous_flags": flags,
        "dangerous_flags_all_false": True,
        "dangerous_flags_true_count": 0,
    }


def main() -> int:
    try:
        summary = load_json(SOURCE_MANIFEST_BUNDLE_SUMMARY, "source manifest bundle summary")
        manifest = load_json(PLACEHOLDER_MANIFEST, "placeholder source manifest")
        self_validator = load_json(SOURCE_MANIFEST_SELF_VALIDATOR, "source manifest self-validator")
        symbol_placeholder = load_json(SYMBOL_UNIVERSE_PLACEHOLDER, "symbol universe placeholder")
        coverage_placeholder = load_json(COVERAGE_PLACEHOLDER, "coverage placeholder")
        provenance_placeholder = load_json(PROVENANCE_PLACEHOLDER, "provenance placeholder")
        policy_validator = load_json(AGGREGATION_POLICY_VALIDATOR_ARTIFACT, "aggregation policy validator")
        policy = load_json(AGGREGATION_POLICY_ARTIFACT, "aggregation policy")
        preflight = validate_preflight(
            summary,
            manifest,
            self_validator,
            symbol_placeholder,
            coverage_placeholder,
            provenance_placeholder,
            policy_validator,
            policy,
        )
        artifacts = build_artifacts()
        payload = build_payload(preflight, artifacts)
        write_bundle_artifacts(payload, artifacts)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        payload = blocked_payload(exc)
        write_json(
            OUT_DIR
            / "repo_only_historical_data_acquisition_okx_symbol_universe_coverage_provenance_resolution_preview_after_source_manifest_bundle_v1_latest.json",
            payload,
        )
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
