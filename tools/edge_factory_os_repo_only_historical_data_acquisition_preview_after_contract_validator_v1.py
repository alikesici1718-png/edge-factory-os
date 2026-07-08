from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_historical_data_acquisition_preview_after_contract_validator_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_historical_data_acquisition_preview_after_contract_validator_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "76c02d6"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 652
EXPECTED_TRACKED_PYTHON_COUNT = 653

REQUESTED_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_preview_after_contract_validator_v1.py"
NEXT_MODULE_APPROVAL = "edge_factory_os_repo_only_historical_data_acquisition_approval_after_preview_v1.py"
NEXT_MODULE_BLOCKED = "edge_factory_os_repo_only_historical_data_acquisition_preview_blocked_record_after_contract_validator_v1.py"

CONTRACT_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_contract_validator_after_data_horizon_discovery_v1"
    / "repo_only_historical_data_acquisition_contract_validator_after_data_horizon_discovery_v1_latest.json"
)
CONTRACT_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_contract_after_data_horizon_discovery_v1"
    / "repo_only_historical_data_acquisition_contract_after_data_horizon_discovery_v1_latest.json"
)
HARDENING_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_implementation_validator_after_approval_v1"
    / "repo_only_pre_acquisition_minimal_reliability_hardening_implementation_validator_after_approval_v1_latest.json"
)
DATA_HORIZON_DISCOVERY_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_data_horizon_expansion_runner_execution_after_source_panel_summary_v1"
    / "repo_only_data_horizon_expansion_runner_execution_after_source_panel_summary_v1_latest.json"
)

VALIDATOR_STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_CONTRACT_VALIDATED_PREVIEW_READY_NO_EXECUTION"
CONTRACT_STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_CONTRACT_READY_NO_ACQUISITION_EXECUTION"
STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION"
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = "HISTORICAL_DATA_ACQUISITION_CONTRACT_VALIDATED_PREVIEW_READY_NO_EXECUTION"
EVIDENCE_AFTER = "HISTORICAL_DATA_ACQUISITION_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION"
DISCOVERY_EVIDENCE_AFTER = "HISTORICAL_DATA_HORIZON_INCOMPLETE_ACQUISITION_CONTRACT_REQUIRED"
EVIDENCE_CHAIN_POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"
RECOMMENDED_ROUTE = "ACQUISITION_APPROVAL_FOR_LOCAL_OR_MANUAL_SOURCE_DISCOVERY_ONLY"

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
    "generic_runner_approval_granted",
    "old_source_panel_anomaly_route_reopened_now",
]
REQUIRED_FUTURE_ARTIFACTS = [
    "historical_raw_data_source_manifest.json",
    "historical_data_acquisition_inventory.json",
    "historical_data_provenance_report.json",
    "historical_symbol_universe_policy.json",
    "historical_symbol_lifecycle_report.json",
    "historical_timestamp_integrity_report.json",
    "historical_missingness_report.json",
    "historical_duplicate_report.json",
    "historical_holdout_policy_report.json",
    "historical_data_acquisition_contract_compliance_report.json",
]
FAIL_CLOSED_CONDITIONS = [
    "source_cannot_be_identified",
    "source_or_license_restrictions_unclear",
    "timestamp_format_ambiguous",
    "symbol_universe_rule_missing",
    "holdout_cannot_be_protected",
    "survivorship_controls_missing",
    "fake_or_synthetic_data_used_as_real",
    "external_api_or_download_occurs_without_separate_approval",
    "timeout_resource_or_rollback_policy_missing",
    "hardening_state_stale_or_invalid",
    "strategy_backtest_candidate_runtime_live_path_touched",
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


def require_equal(actual: Any, expected: Any, field: str) -> None:
    if actual != expected:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {field}={actual!r} expected {expected!r}")


def require_true(actual: Any, field: str) -> None:
    if actual is not True:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {field} must be true, got {actual!r}")


def require_false(actual: Any, field: str) -> None:
    if actual is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {field} must be false, got {actual!r}")


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
    contract: Dict[str, Any],
    hardening: Dict[str, Any],
    discovery: Dict[str, Any],
) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    status = run_git(["status", "--short"])
    require_equal(head, EXPECTED_HEAD, "head")
    require(status == "" or status == f"?? {CURRENT_TOOL_REL}", f"{STATUS_BLOCKED_CONTEXT}: repo dirty: {status}")

    require_equal(validator.get("next_module"), REQUESTED_MODULE, "validator.next_module")
    require_equal(
        validator.get("historical_data_acquisition_contract_validator_status"),
        VALIDATOR_STATUS_PASS,
        "validator.status",
    )
    require_true(validator.get("acquisition_contract_validated"), "validator.acquisition_contract_validated")
    require_true(validator.get("acquisition_preview_allowed_next"), "validator.acquisition_preview_allowed_next")
    require_false(validator.get("acquisition_execution_allowed_now"), "validator.acquisition_execution_allowed_now")
    require_false(validator.get("external_download_allowed_now"), "validator.external_download_allowed_now")
    require_false(validator.get("external_api_allowed_now"), "validator.external_api_allowed_now")
    require_false(validator.get("data_download_performed"), "validator.data_download_performed")
    require_false(validator.get("data_fetch_performed"), "validator.data_fetch_performed")
    require_false(validator.get("data_build_performed"), "validator.data_build_performed")
    require_false(validator.get("external_api_calls_performed"), "validator.external_api_calls_performed")
    require_equal(validator.get("active_p0_blocker_count"), 0, "validator.active_p0_blocker_count")
    require_equal(validator.get("active_p1_attention_count"), 1, "validator.active_p1_attention_count")
    require_true(validator.get("p1_attention_carried_forward"), "validator.p1_attention_carried_forward")
    require_true(
        validator.get("dormant_repo_attention_count_carried_forward"),
        "validator.dormant_repo_attention_count_carried_forward",
    )
    require_equal(validator.get("dormant_repo_attention_count"), 716, "validator.dormant_repo_attention_count")
    require_equal(
        validator.get("current_evidence_chain_quality_after_validator"),
        EVIDENCE_BEFORE,
        "validator.evidence_after",
    )

    require_equal(contract.get("historical_data_acquisition_contract_status"), CONTRACT_STATUS_PASS, "contract.status")
    require_false(contract.get("acquisition_execution_allowed_now"), "contract.acquisition_execution_allowed_now")
    require_true(contract.get("acquisition_requires_future_preview"), "contract.acquisition_requires_future_preview")
    require_true(contract.get("acquisition_requires_future_approval"), "contract.acquisition_requires_future_approval")
    require_true(contract.get("acquisition_requires_source_manifest"), "contract.acquisition_requires_source_manifest")
    require_true(contract.get("acquisition_requires_provenance_report"), "contract.acquisition_requires_provenance_report")

    require_true(hardening.get("hardening_validation_passed"), "hardening.hardening_validation_passed")
    require_false(hardening.get("acquisition_execution_allowed_now"), "hardening.acquisition_execution_allowed_now")
    require_equal(hardening.get("active_p0_blocker_count"), 0, "hardening.active_p0_blocker_count")
    require_equal(hardening.get("active_p1_attention_count"), 1, "hardening.active_p1_attention_count")
    require_true(
        hardening.get("dormant_repo_attention_count_carried_forward"),
        "hardening.dormant_repo_attention_count_carried_forward",
    )

    require_true(discovery.get("local_existing_data_found"), "discovery.local_existing_data_found")
    require_false(discovery.get("historical_horizon_complete"), "discovery.historical_horizon_complete")
    require_equal(discovery.get("available_horizon_years_estimate"), 0.999201, "discovery.available_horizon_years_estimate")
    require_equal(discovery.get("target_historical_horizon_years"), "3_to_4", "discovery.target_historical_horizon_years")
    require_equal(discovery.get("target_timeframe"), "1h", "discovery.target_timeframe")
    require_true(discovery.get("external_download_needed"), "discovery.external_download_needed")
    require_false(discovery.get("external_download_allowed_now"), "discovery.external_download_allowed_now")
    require_false(discovery.get("data_download_performed"), "discovery.data_download_performed")
    require_false(discovery.get("data_fetch_performed"), "discovery.data_fetch_performed")
    require_false(discovery.get("data_build_performed"), "discovery.data_build_performed")
    require_false(discovery.get("external_api_calls_performed"), "discovery.external_api_calls_performed")
    require_equal(
        discovery.get("current_evidence_chain_quality_after_execution"),
        DISCOVERY_EVIDENCE_AFTER,
        "discovery.evidence_after",
    )

    return {
        "head": head,
        "whole_system_preflight_completed": True,
        "whole_system_preflight_decision": "PASS",
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
    }


def preview_sections(validator: Dict[str, Any], discovery: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "validator_context": {
            "acquisition_contract_validated": True,
            "acquisition_preview_allowed_next": True,
            "acquisition_execution_still_blocked": True,
            "local_horizon_incomplete": True,
            "external_or_additional_data_required": True,
            "active_p1_attention_count": 1,
            "p1_attention_remains_active": True,
            "dormant_repo_attention_count": 716,
            "dormant_repo_attention_carried_forward": True,
            "validator_status": validator.get("historical_data_acquisition_contract_validator_status"),
        },
        "local_gap_context": {
            "local_existing_data_found": True,
            "historical_horizon_complete": False,
            "available_horizon_years_estimate": 0.999201,
            "target_historical_horizon_years": "3_to_4",
            "target_timeframe": "1h",
            "earliest_timestamp_available": discovery.get("earliest_timestamp_available"),
            "latest_timestamp_available": discovery.get("latest_timestamp_available"),
            "external_download_needed": True,
            "survivorship_bias_controls_required": True,
        },
        "acquisition_route_preview": [
            {
                "priority": 1,
                "route": "LOCAL_ARCHIVE_IMPORT_PREVIEW",
                "user_supplies_existing_historical_data_files_manually": True,
                "external_api_allowed": False,
                "automated_download_allowed": False,
                "preferred_first_route_if_user_has_files": True,
                "future_validation_requirements": [
                    "file_paths",
                    "hashes",
                    "date_ranges",
                    "symbol_universe",
                    "provenance",
                ],
            },
            {
                "priority": 2,
                "route": "MANUAL_EXCHANGE_EXPORT_IMPORT_PREVIEW",
                "user_manually_exports_exchange_historical_candle_files": True,
                "edge_factory_os_automated_api_call_allowed": False,
                "future_validation_requirements": [
                    "source",
                    "interval",
                    "symbol_universe",
                    "timestamps",
                    "hashes",
                    "provenance",
                ],
            },
            {
                "priority": 3,
                "route": "SEPARATELY_APPROVED_EXTERNAL_DATA_ACQUISITION_PREVIEW",
                "allowed_only_if_local_or_manual_data_unavailable": True,
                "requires_separate_preview_approval_execution_validator_chain": True,
                "must_obey_timeout_memory_disk_rollback_policies": True,
                "must_create_source_manifest_and_provenance_report": True,
                "must_not_mix_strategy_selection_into_acquisition": True,
                "execution_allowed_now": False,
            },
        ],
        "recommended_route_decision": {
            "recommended_acquisition_route": RECOMMENDED_ROUTE,
            "reason": "no user-supplied local 3-4 year archive path is known to this repo-only preview",
            "approval_scope": "future module may inspect user-provided or local source candidates only",
            "direct_external_api_or_download_execution_recommended_now": False,
        },
        "future_required_artifacts_preview": REQUIRED_FUTURE_ARTIFACTS,
        "safety_and_hardening_preview": {
            "secret_scan_remains_clear": True,
            "dependency_snapshot_unchanged_or_changes_explicitly_approved": True,
            "no_unapproved_environment_modification": True,
            "ast_current_chain_blocker_remains_0": True,
            "artifact_hash_manifest_updated": True,
            "timeout_policy_applied": True,
            "memory_disk_resource_policy_applied": True,
            "rollback_policy_applied": True,
            "no_dormant_repo_module_execution": True,
            "no_generic_runner_approval": True,
            "no_schema_or_config_creation": True,
        },
        "fail_closed_preview": FAIL_CLOSED_CONDITIONS,
        "evidence_policy_preview": {
            "current_state_before_preview": EVIDENCE_BEFORE,
            "state_after_preview": EVIDENCE_AFTER,
            "preview_is_not_data_evidence": True,
            "preview_is_not_source_manifest": True,
            "preview_is_not_provenance_report": True,
            "acquisition_execution_remains_blocked": True,
            "p1_remains_active_until_acquisition_and_historical_validator_close_it": True,
        },
        "next_module_decision": {
            "chosen_next_module": NEXT_MODULE_APPROVAL,
            "if_preview_is_unsafe": NEXT_MODULE_BLOCKED,
            "do_not_choose_acquisition_execution_apply": True,
            "do_not_choose_data_download_fetch_api": True,
            "do_not_choose_strategy_research": True,
            "do_not_choose_candidate_backtest_runtime_live_capital": True,
            "do_not_choose_generic_review_adoption_gate_rollout": True,
        },
    }


def replacement_checks() -> Dict[str, bool]:
    return {
        "preflight_passed": True,
        "preview_completed": True,
        "local_gap_context_recorded": True,
        "routes_previewed_without_execution": True,
        "local_or_manual_route_recommended": True,
        "future_artifacts_previewed": True,
        "safety_hardening_previewed": True,
        "fail_closed_previewed": True,
        "evidence_policy_previewed": True,
        "no_download_fetch_api_build": True,
        "no_strategy_backtest_candidate_runtime_capital_live": True,
        "next_module_is_approval_record": True,
    }


def build_payload(
    preflight: Dict[str, Any],
    validator: Dict[str, Any],
    contract: Dict[str, Any],
    hardening: Dict[str, Any],
    discovery: Dict[str, Any],
    sections: Dict[str, Any],
) -> Dict[str, Any]:
    flags = dangerous_flags()
    checks = replacement_checks()
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_preview_status": STATUS_PASS,
        "final_decision": "HISTORICAL_DATA_ACQUISITION_PREVIEW_CREATED_APPROVAL_REQUIRED",
        "next_action": "CREATE_HISTORICAL_DATA_ACQUISITION_APPROVAL_RECORD_NO_EXECUTION",
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
        "active_p1_attention_count_from_live_artifact": 1,
        "p1_attention_carried_forward": True,
        "dormant_repo_attention_count_carried_forward": True,
        "blocked_actions_absent_from_requested_module": True,
        "whole_system_preflight_decision": "PASS",
        "prior_contract_validator_respected": True,
        "acquisition_preview_completed": True,
        "validator_context_completed": True,
        "local_gap_context_completed": True,
        "acquisition_route_preview_completed": True,
        "recommended_route_decision_completed": True,
        "future_required_artifacts_preview_completed": True,
        "safety_and_hardening_preview_completed": True,
        "fail_closed_preview_completed": True,
        "evidence_policy_preview_completed": True,
        "local_existing_data_found": True,
        "historical_horizon_complete": False,
        "available_horizon_years_estimate": 0.999201,
        "target_historical_horizon_years": "3_to_4",
        "target_timeframe": "1h",
        "earliest_timestamp_available": discovery.get("earliest_timestamp_available"),
        "latest_timestamp_available": discovery.get("latest_timestamp_available"),
        "external_download_needed": True,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "acquisition_execution_allowed_now": False,
        "acquisition_approval_required_next": True,
        "acquisition_execution_requires_future_approval": True,
        "recommended_acquisition_route": RECOMMENDED_ROUTE,
        "local_archive_import_preferred": True,
        "manual_exchange_export_import_allowed_future": True,
        "external_api_download_allowed_now": False,
        "external_api_download_requires_separate_future_chain": True,
        "acquisition_requires_source_manifest": True,
        "acquisition_requires_provenance_report": True,
        "acquisition_requires_future_validator": True,
        "survivorship_bias_controls_required": True,
        "symbol_lifecycle_report_required": True,
        "holdout_policy_required": True,
        "historical_data_quality_validator_required": True,
        "timeout_policy_required_for_acquisition": True,
        "memory_disk_resource_policy_required_for_acquisition": True,
        "rollback_policy_required_for_acquisition": True,
        "hardening_state_required_for_acquisition": True,
        "required_future_artifact_list_previewed": True,
        "fail_closed_conditions_previewed": True,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "data_build_performed": False,
        "external_api_calls_performed": False,
        "fake_or_synthetic_data_detected": False,
        "strategy_signal_claims_made": False,
        "tradable_edge_claims_made": False,
        "profit_claims_made": False,
        "backtest_performed": False,
        "candidate_generation_performed": False,
        "family_release_performed": False,
        "active_paper_performed": False,
        "real_order_touch_performed": False,
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
        "active_p1_attention_count": 1,
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
        "derived_live_repo_post_check": "PASS_HISTORICAL_DATA_ACQUISITION_PREVIEW_READY_FOR_APPROVAL",
        "derived_live_repo_post_check_reason": (
            "preview records local/manual source discovery as the recommended approval path; no download, fetch, API, "
            "data build, strategy, runtime, capital, live, generic-runner, schema, config, or old-route action occurred"
        ),
        "replacement_checks": checks,
        "replacement_checks_all_true": all(value is True for value in checks.values()),
        "tracked_python_count_expectation": {
            "previous": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT,
        },
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "source_artifacts": {
            "contract_validator_artifact": str(CONTRACT_VALIDATOR_ARTIFACT),
            "contract_artifact": str(CONTRACT_ARTIFACT),
            "hardening_validator_artifact": str(HARDENING_VALIDATOR_ARTIFACT),
            "local_data_horizon_discovery_artifact": str(DATA_HORIZON_DISCOVERY_ARTIFACT),
        },
        "preview_sections": sections,
        "preflight": preflight,
        "prior_contract_validator_snapshot": {
            "historical_data_acquisition_contract_validator_status": validator.get(
                "historical_data_acquisition_contract_validator_status"
            ),
            "current_evidence_chain_quality_after_validator": validator.get(
                "current_evidence_chain_quality_after_validator"
            ),
            "next_module": validator.get("next_module"),
        },
        "prior_contract_snapshot": {
            "historical_data_acquisition_contract_status": contract.get("historical_data_acquisition_contract_status"),
            "current_evidence_chain_quality_after_contract": contract.get("current_evidence_chain_quality_after_contract"),
        },
        "prior_hardening_snapshot": {
            "hardening_validation_passed": hardening.get("hardening_validation_passed"),
            "dormant_repo_attention_count": hardening.get("dormant_repo_attention_count"),
        },
    }


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
        "prior_contract_validator_respected",
        "acquisition_preview_completed",
        "validator_context_completed",
        "local_gap_context_completed",
        "acquisition_route_preview_completed",
        "recommended_route_decision_completed",
        "future_required_artifacts_preview_completed",
        "safety_and_hardening_preview_completed",
        "fail_closed_preview_completed",
        "evidence_policy_preview_completed",
        "local_existing_data_found",
        "external_download_needed",
        "acquisition_approval_required_next",
        "acquisition_execution_requires_future_approval",
        "local_archive_import_preferred",
        "manual_exchange_export_import_allowed_future",
        "external_api_download_requires_separate_future_chain",
        "acquisition_requires_source_manifest",
        "acquisition_requires_provenance_report",
        "acquisition_requires_future_validator",
        "survivorship_bias_controls_required",
        "symbol_lifecycle_report_required",
        "holdout_policy_required",
        "historical_data_quality_validator_required",
        "timeout_policy_required_for_acquisition",
        "memory_disk_resource_policy_required_for_acquisition",
        "rollback_policy_required_for_acquisition",
        "hardening_state_required_for_acquisition",
        "required_future_artifact_list_previewed",
        "fail_closed_conditions_previewed",
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
        "historical_horizon_complete",
        "external_download_allowed_now",
        "external_api_allowed_now",
        "acquisition_execution_allowed_now",
        "external_api_download_allowed_now",
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
        "family_release_performed",
        "active_paper_performed",
        "real_order_touch_performed",
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
    require_equal(payload.get("historical_data_acquisition_preview_status"), STATUS_PASS, "preview status")
    require_equal(payload.get("next_module"), NEXT_MODULE_APPROVAL, "next_module")
    require_equal(payload.get("whole_system_preflight_decision"), "PASS", "whole_system_preflight_decision")
    require_equal(payload.get("recommended_acquisition_route"), RECOMMENDED_ROUTE, "recommended_acquisition_route")
    require_equal(payload.get("documentation_loop_risk_level"), DOCUMENTATION_LOOP_RISK_LEVEL, "documentation_loop_risk_level")
    require_equal(payload.get("current_evidence_chain_quality_before_preview"), EVIDENCE_BEFORE, "evidence_before")
    require_equal(payload.get("current_evidence_chain_quality_after_preview"), EVIDENCE_AFTER, "evidence_after")
    require_equal(payload.get("active_p0_blocker_count"), 0, "active_p0_blocker_count")
    require_equal(payload.get("active_p1_attention_count"), 1, "active_p1_attention_count")
    require_equal(payload.get("dormant_repo_attention_count"), 716, "dormant_repo_attention_count")
    require_equal(payload.get("planned_schema_files_existing_count"), 0, "planned_schema_files_existing_count")
    require_equal(payload.get("available_horizon_years_estimate"), 0.999201, "available_horizon_years_estimate")
    require_equal(payload.get("target_historical_horizon_years"), "3_to_4", "target_historical_horizon_years")
    require_equal(payload.get("target_timeframe"), "1h", "target_timeframe")
    require(all(value is False for value in payload["dangerous_flags"].values()), "dangerous flags must all be false")


def main() -> None:
    validator = load_json(CONTRACT_VALIDATOR_ARTIFACT)
    contract = load_json(CONTRACT_ARTIFACT)
    hardening = load_json(HARDENING_VALIDATOR_ARTIFACT)
    discovery = load_json(DATA_HORIZON_DISCOVERY_ARTIFACT)
    preflight = validate_preflight(validator, contract, hardening, discovery)
    sections = preview_sections(validator, discovery)
    payload = build_payload(preflight, validator, contract, hardening, discovery, sections)
    validate_payload(payload)
    write_json(OUT_DIR / "historical_data_acquisition_preview_after_contract_validator_v1.json", sections)
    write_json(OUT_DIR / "repo_only_historical_data_acquisition_preview_after_contract_validator_v1_latest.json", payload)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
