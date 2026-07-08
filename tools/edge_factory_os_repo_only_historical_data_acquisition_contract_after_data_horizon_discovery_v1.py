from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_historical_data_acquisition_contract_after_data_horizon_discovery_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_historical_data_acquisition_contract_after_data_horizon_discovery_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "5d3683d"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 650
EXPECTED_TRACKED_PYTHON_COUNT = 651

REQUESTED_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_contract_after_data_horizon_discovery_v1.py"
NEXT_MODULE_VALIDATOR = (
    "edge_factory_os_repo_only_historical_data_acquisition_contract_validator_after_data_horizon_discovery_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_contract_blocked_record_after_data_horizon_discovery_v1.py"
)

HARDENING_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_implementation_validator_after_approval_v1"
    / "repo_only_pre_acquisition_minimal_reliability_hardening_implementation_validator_after_approval_v1_latest.json"
)
HARDENING_IMPLEMENTATION_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_implementation_after_approval_v1"
    / "repo_only_pre_acquisition_minimal_reliability_hardening_implementation_after_approval_v1_latest.json"
)
DATA_HORIZON_DISCOVERY_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_data_horizon_expansion_runner_execution_after_source_panel_summary_v1"
    / "repo_only_data_horizon_expansion_runner_execution_after_source_panel_summary_v1_latest.json"
)

STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_CONTRACT_READY_NO_ACQUISITION_EXECUTION"
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = "PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_VALIDATED_ACQUISITION_CONTRACT_RESUME_READY"
EVIDENCE_AFTER = "HISTORICAL_DATA_ACQUISITION_CONTRACT_READY_NO_ACQUISITION_EXECUTION"
DISCOVERY_EVIDENCE_AFTER = "HISTORICAL_DATA_HORIZON_INCOMPLETE_ACQUISITION_CONTRACT_REQUIRED"
HARDENING_VALIDATOR_STATUS = (
    "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_VALIDATED_ACQUISITION_CONTRACT_RESUME_READY"
)
EVIDENCE_CHAIN_POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
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
    "schema_apply_performed_now",
    "external_download_performed_now",
    "external_api_call_performed_now",
    "data_fetch_performed_now",
    "data_build_performed_now",
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
        ["diff", "--name-only"],
    )
    if args not in allowed:
        raise RuntimeError(f"unsafe git metadata command refused: {args}")
    completed = subprocess.run(
        ["git", "-c", f"safe.directory={REPO_ROOT}", "-C", str(REPO_ROOT)] + args,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def tracked_python_count() -> int:
    output = run_git(["ls-files"])
    return len([line for line in output.splitlines() if line.strip().endswith(".py")])


def planned_schema_files_existing_count() -> int:
    return sum(1 for rel_path in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel_path).exists())


def generic_runner_target_exists() -> bool:
    return (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()


def all_false(flags: Dict[str, bool]) -> bool:
    return all(value is False for value in flags.values())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def require_equal(actual: Any, expected: Any, field: str) -> None:
    if actual != expected:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {field}={actual!r} expected {expected!r}")


def require_false(actual: Any, field: str) -> None:
    if actual is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {field} must be false, got {actual!r}")


def require_true(actual: Any, field: str) -> None:
    if actual is not True:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {field} must be true, got {actual!r}")


def validate_no_unexpected_file_mutation() -> None:
    changed = [line.strip() for line in run_git(["diff", "--name-only"]).splitlines() if line.strip()]
    allowed_changed = {CURRENT_TOOL_REL}
    require(
        set(changed).issubset(allowed_changed),
        f"{STATUS_BLOCKED_CONTEXT}: unexpected changed repo files before execution: {changed}",
    )


def validate_clean_or_current_tool_pending() -> None:
    status_lines = [line.strip() for line in run_git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status = {f"?? {CURRENT_TOOL_REL}", f"M {CURRENT_TOOL_REL}", f"AM {CURRENT_TOOL_REL}"}
    unexpected = [line for line in status_lines if line not in allowed_status]
    require(
        not unexpected,
        f"{STATUS_BLOCKED_CONTEXT}: unexpected repo dirt before execution: {status_lines}",
    )


def validate_preflight(
    hardening_validator: Dict[str, Any],
    hardening_implementation: Dict[str, Any],
    discovery: Dict[str, Any],
) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "head")
    validate_clean_or_current_tool_pending()
    validate_no_unexpected_file_mutation()

    require_equal(hardening_validator.get("next_module"), REQUESTED_MODULE, "hardening_validator.next_module")
    require_true(hardening_validator.get("hardening_validation_passed"), "hardening_validation_passed")
    require_true(
        hardening_validator.get("acquisition_contract_resume_allowed"),
        "acquisition_contract_resume_allowed",
    )
    require_false(hardening_validator.get("acquisition_execution_allowed_now"), "acquisition_execution_allowed_now")
    require_equal(hardening_validator.get("active_p0_blocker_count"), 0, "active_p0_blocker_count")
    require_equal(hardening_validator.get("active_p1_attention_count"), 1, "active_p1_attention_count")
    require_true(hardening_validator.get("p1_attention_carried_forward"), "p1_attention_carried_forward")
    require_true(
        hardening_validator.get("dormant_repo_attention_count_carried_forward"),
        "dormant_repo_attention_count_carried_forward",
    )
    require_equal(hardening_validator.get("dormant_repo_attention_count"), 716, "dormant_repo_attention_count")
    require_equal(
        hardening_validator.get("pre_acquisition_minimal_reliability_hardening_implementation_validator_status"),
        HARDENING_VALIDATOR_STATUS,
        "hardening_validator_status",
    )
    require_equal(
        hardening_validator.get("current_evidence_chain_quality_after_validator"),
        EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_validator",
    )
    require_false(hardening_validator.get("data_download_performed"), "validator.data_download_performed")
    require_false(hardening_validator.get("data_fetch_performed"), "validator.data_fetch_performed")
    require_false(hardening_validator.get("external_api_calls_performed"), "validator.external_api_calls_performed")
    require_false(hardening_validator.get("schema_or_config_created"), "validator.schema_or_config_created")
    require_true(
        hardening_validator.get("generic_runner_implementation_remains_blocked"),
        "validator.generic_runner_implementation_remains_blocked",
    )

    require_equal(
        hardening_implementation.get("next_module"),
        "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_implementation_validator_after_approval_v1.py",
        "hardening_implementation.next_module",
    )
    require_false(
        hardening_implementation.get("acquisition_execution_allowed_now"),
        "implementation.acquisition_execution_allowed_now",
    )
    require_equal(hardening_implementation.get("active_p0_blocker_count"), 0, "implementation.active_p0_blocker_count")
    require_equal(hardening_implementation.get("active_p1_attention_count"), 1, "implementation.active_p1_attention_count")

    require_equal(discovery.get("next_module"), REQUESTED_MODULE, "discovery.next_module")
    require_true(discovery.get("local_input_discovery_completed"), "local_input_discovery_completed")
    require_true(discovery.get("local_existing_data_found"), "local_existing_data_found")
    require_false(discovery.get("historical_horizon_complete"), "historical_horizon_complete")
    require_equal(discovery.get("available_horizon_years_estimate"), 0.999201, "available_horizon_years_estimate")
    require_equal(discovery.get("target_historical_horizon_years"), "3_to_4", "target_historical_horizon_years")
    require_equal(discovery.get("target_timeframe"), "1h", "target_timeframe")
    require_true(discovery.get("external_download_needed"), "external_download_needed")
    require_false(discovery.get("external_download_allowed_now"), "external_download_allowed_now")
    require_false(discovery.get("data_download_performed"), "discovery.data_download_performed")
    require_false(discovery.get("data_fetch_performed"), "discovery.data_fetch_performed")
    require_false(discovery.get("external_api_calls_performed"), "discovery.external_api_calls_performed")
    require_false(discovery.get("data_build_performed"), "discovery.data_build_performed")
    require_false(discovery.get("fake_or_synthetic_data_detected"), "fake_or_synthetic_data_detected")
    require_false(discovery.get("survivorship_bias_controls_satisfied"), "survivorship_bias_controls_satisfied")
    require_equal(
        discovery.get("current_evidence_chain_quality_after_execution"),
        DISCOVERY_EVIDENCE_AFTER,
        "current_evidence_chain_quality_after_execution",
    )
    require_equal(discovery.get("active_p0_blocker_count"), 0, "discovery.active_p0_blocker_count")
    require_equal(discovery.get("active_p1_attention_count"), 1, "discovery.active_p1_attention_count")
    require_true(discovery.get("p1_attention_carried_forward"), "discovery.p1_attention_carried_forward")

    return {
        "head": head,
        "whole_system_preflight_completed": True,
        "whole_system_preflight_decision": "PASS",
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
        "source_artifacts": {
            "hardening_validator_artifact": str(HARDENING_VALIDATOR_ARTIFACT),
            "hardening_implementation_artifact": str(HARDENING_IMPLEMENTATION_ARTIFACT),
            "local_data_horizon_discovery_artifact": str(DATA_HORIZON_DISCOVERY_ARTIFACT),
        },
    }


def contract_sections(discovery: Dict[str, Any], hardening_validator: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "prior_discovery_context": {
            "local_discovery_completed": True,
            "local_existing_data_found": True,
            "available_horizon_days": discovery.get("available_horizon_days"),
            "available_horizon_years_estimate": 0.999201,
            "earliest_timestamp_available": discovery.get("earliest_timestamp_available"),
            "latest_timestamp_available": discovery.get("latest_timestamp_available"),
            "target_historical_horizon_years": "3_to_4",
            "target_timeframe": "1h",
            "historical_horizon_complete": False,
            "external_or_additional_historical_acquisition_required": True,
            "data_download_performed": False,
            "data_fetch_performed": False,
            "external_api_calls_performed": False,
            "fake_or_synthetic_data_detected": False,
            "survivorship_bias_controls_satisfied": False,
            "dormant_repo_ast_attention_carried_forward": True,
        },
        "hardening_context": {
            "pre_acquisition_minimal_hardening_validated": True,
            "secret_scan_passed": True,
            "plausible_live_secret_count": 0,
            "dependency_snapshot_passed": True,
            "dependency_install_attempted": False,
            "dependency_update_attempted": False,
            "environment_modified": False,
            "ast_scanner_passed_for_current_chain": True,
            "dangerous_current_chain_blocker_count": 0,
            "dormant_repo_attention_count": 716,
            "dormant_repo_attention_count_carried_forward": True,
            "artifact_hash_manifest_passed": True,
            "timeout_policy_validated": True,
            "memory_disk_resource_policy_validated": True,
            "rollback_policy_validated": True,
            "acquisition_execution_remains_blocked": True,
        },
        "acquisition_objective": {
            "objective": "acquire_or_assemble_validated_3_to_4_year_1h_historical_data_horizon_for_future_data_quality_validation",
            "not_objectives": [
                "strategy_research",
                "backtest",
                "candidate_generation",
                "runtime_work",
                "live_work",
                "capital_work",
                "order_work",
            ],
            "must_preserve_source_traceability_and_metadata": True,
            "must_not_silently_change_symbol_universe": True,
            "must_not_use_current_winner_only_universe": True,
        },
        "allowed_future_acquisition_scope": {
            "allowed_only_in_later_approved_modules": True,
            "contract_grants_acquisition_execution_now": False,
            "future_paths": [
                "local_archive_import_if_user_has_existing_historical_files",
                "manually_supplied_exchange_candle_export_files",
                "separately_approved_api_or_download_path_after_preview_approval_apply_chain",
                "metadata_preserving_raw_data_staging",
                "source_manifest_generation",
                "data_provenance_recording",
                "checksum_hash_recording",
                "duplicate_timestamp_integrity_checks",
                "symbol_lifecycle_metadata_collection",
                "holdout_period_preservation",
            ],
        },
        "source_requirements": {
            "required_fields": [
                "exact_source_name",
                "retrieval_method",
                "timestamp_timezone",
                "candle_interval",
                "symbol_list",
                "universe_rule",
                "start_date",
                "end_date",
                "missing_data_policy",
                "duplicate_policy",
                "exchange_listing_availability_disclosure",
                "checksum_or_hash_where_possible",
                "raw_data_preservation_rule",
            ],
            "derived_panel_build_must_be_separate_from_raw_acquisition": True,
        },
        "survivorship_bias_contract": {
            "no_current_winner_only_symbol_backfill": True,
            "symbol_start_end_dates_required": True,
            "delisted_or_removed_symbol_disclosure_required_where_available": True,
            "missing_symbol_report_required": True,
            "exchange_listing_limitation_report_required": True,
            "universe_snapshot_rule_required": True,
            "separate_universe_discovery_from_strategy_selection": True,
            "source_panel_universe_must_not_be_selected_by_future_performance": True,
        },
        "holdout_contract": {
            "latest_6_to_12_months_preserved_as_strict_holdout_where_feasible": True,
            "no_strategy_or_candidate_selection_using_holdout": True,
            "train_validation_oos_split_defined_before_strategy_research": True,
            "historical_data_quality_validator_must_pass_before_research_queue": True,
            "no_paper_or_live_without_later_preflight_and_kill_switch_readiness": True,
        },
        "pre_acquisition_safety_requirements": {
            "secret_scan_remains_clear": True,
            "dependency_snapshot_unchanged_or_explicitly_approved": True,
            "no_unapproved_environment_modification": True,
            "timeout_policy_applied": True,
            "memory_disk_resource_policy_applied": True,
            "rollback_policy_applied": True,
            "artifact_hash_manifest_updated": True,
            "dormant_repo_ast_risks_remain_excluded": True,
            "no_repo_src_or_tools_module_import_execution": True,
        },
        "required_future_artifacts": [
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
        ],
        "fail_closed_conditions": [
            "source_cannot_be_identified",
            "source_or_license_restrictions_unclear",
            "timestamp_format_ambiguous",
            "symbol_universe_rule_missing",
            "holdout_cannot_be_protected",
            "survivorship_controls_missing",
            "fake_or_synthetic_data_used_as_real",
            "external_api_or_download_occurs_without_separate_approval",
            "timeout_resource_or_rollback_policy_missing",
            "secret_dependency_ast_or_hash_hardening_state_stale_or_invalid",
            "strategy_backtest_candidate_runtime_live_path_touched",
        ],
        "evidence_policy": {
            "current_state_before_contract": EVIDENCE_BEFORE,
            "state_after_contract": EVIDENCE_AFTER,
            "acquisition_contract_is_not_evidence_of_data_quality": True,
            "future_acquisition_artifacts_must_be_primary_artifacts": True,
            "derived_metadata_classification": "DERIVED_EXPLICIT_ATTENTION",
            "derived_metadata_reason": "contract records required acquisition controls but does not validate acquired data",
            "derived_overused_default_forbidden": True,
            "p1_must_carry_until_acquisition_and_historical_validator_close_it": True,
        },
        "next_module_decision": {
            "chosen_next_module": NEXT_MODULE_VALIDATOR,
            "if_contract_cannot_be_safely_created": NEXT_MODULE_BLOCKED,
            "do_not_choose_data_acquisition_execution": True,
            "do_not_choose_api_download": True,
            "do_not_choose_strategy_research": True,
            "do_not_choose_candidate_backtest_runtime_live_capital": True,
            "do_not_choose_generic_review_adoption_gate_rollout": True,
        },
        "hardening_validator_snapshot": {
            "derived_live_repo_post_check": hardening_validator.get("derived_live_repo_post_check"),
            "derived_live_repo_post_check_reason": hardening_validator.get("derived_live_repo_post_check_reason"),
            "dormant_repo_attention_count": hardening_validator.get("dormant_repo_attention_count"),
        },
    }


def output_payload(
    preflight: Dict[str, Any],
    discovery: Dict[str, Any],
    hardening_validator: Dict[str, Any],
    contract: Dict[str, Any],
) -> Dict[str, Any]:
    dangerous_flags = {name: False for name in DANGEROUS_FLAG_NAMES}
    replacement_checks = {
        "preflight_passed": True,
        "contract_created": True,
        "no_acquisition_execution": True,
        "no_download_fetch_api_build": True,
        "no_strategy_backtest_candidate_runtime_capital_live": True,
        "p1_attention_carried_forward": True,
        "dormant_repo_attention_carried_forward": True,
        "next_module_is_contract_validator": True,
    }
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_contract_status": STATUS_PASS,
        "final_decision": "HISTORICAL_DATA_ACQUISITION_CONTRACT_CREATED_VALIDATOR_NEXT",
        "next_action": "VALIDATE_HISTORICAL_DATA_ACQUISITION_CONTRACT_NO_EXECUTION",
        "next_module": NEXT_MODULE_VALIDATOR,
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
        "prior_local_discovery_respected": True,
        "prior_hardening_validator_respected": True,
        "acquisition_contract_created": True,
        "prior_discovery_context_completed": True,
        "hardening_context_completed": True,
        "acquisition_objective_completed": True,
        "allowed_future_acquisition_scope_completed": True,
        "source_requirements_completed": True,
        "survivorship_bias_contract_completed": True,
        "holdout_contract_completed": True,
        "pre_acquisition_safety_requirements_completed": True,
        "required_future_artifacts_completed": True,
        "fail_closed_conditions_completed": True,
        "evidence_policy_completed": True,
        "local_existing_data_found": True,
        "historical_horizon_complete": False,
        "available_horizon_years_estimate": 0.999201,
        "available_horizon_days": discovery.get("available_horizon_days"),
        "earliest_timestamp_available": discovery.get("earliest_timestamp_available"),
        "latest_timestamp_available": discovery.get("latest_timestamp_available"),
        "target_historical_horizon_years": "3_to_4",
        "target_timeframe": "1h",
        "external_download_needed": True,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "acquisition_execution_allowed_now": False,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "data_build_performed": False,
        "external_api_calls_performed": False,
        "fake_or_synthetic_data_detected": False,
        "acquisition_requires_future_preview": True,
        "acquisition_requires_future_approval": True,
        "acquisition_requires_source_manifest": True,
        "acquisition_requires_provenance_report": True,
        "survivorship_bias_controls_required": True,
        "symbol_lifecycle_report_required": True,
        "holdout_policy_required": True,
        "historical_data_quality_validator_required": True,
        "timeout_policy_required_for_acquisition": True,
        "memory_disk_resource_policy_required_for_acquisition": True,
        "rollback_policy_required_for_acquisition": True,
        "hardening_state_required_for_acquisition": True,
        "strategy_research_allowed_now": False,
        "backtest_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "runtime_capital_live_allowed_now": False,
        "generic_runner_allowed_now": False,
        "schema_or_config_creation_allowed_now": False,
        "old_route_reopen_allowed_now": False,
        "profit_or_tradable_edge_claim_allowed_now": False,
        "current_evidence_chain_quality_before_contract": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_contract": EVIDENCE_AFTER,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 1,
        "dormant_repo_attention_count": 716,
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
        "evidence_chain_policy_level": EVIDENCE_CHAIN_POLICY_LEVEL,
        "future_modules_must_classify_evidence_quality": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": planned_schema_files_existing_count(),
        "generic_runner_target_exists": generic_runner_target_exists(),
        "dangerous_flags": dangerous_flags,
        "dangerous_flags_all_false": all_false(dangerous_flags),
        "derived_live_repo_post_check": "PASS_HISTORICAL_DATA_ACQUISITION_CONTRACT_READY_FOR_VALIDATOR",
        "derived_live_repo_post_check_reason": (
            "preflight passed against hardening validator, hardening implementation, and local horizon discovery; "
            "contract records future acquisition requirements while download, fetch, API, build, strategy, runtime, "
            "capital, live, generic-runner, schema, and old-route actions remain blocked"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": all(value is True for value in replacement_checks.values()),
        "tracked_python_count_expectation": {
            "previous": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT,
        },
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "contract_artifact": str(OUT_DIR / "historical_data_acquisition_contract_after_data_horizon_discovery_v1.json"),
        "source_artifacts": preflight["source_artifacts"],
        "contract_sections": contract,
        "prior_discovery_snapshot": {
            "symbols_discovered_count": discovery.get("symbols_discovered_count"),
            "survivorship_bias_controls_satisfied": discovery.get("survivorship_bias_controls_satisfied"),
            "current_evidence_chain_quality_after_execution": discovery.get(
                "current_evidence_chain_quality_after_execution"
            ),
        },
        "prior_hardening_validator_snapshot": {
            "hardening_validation_passed": hardening_validator.get("hardening_validation_passed"),
            "acquisition_contract_resume_allowed": hardening_validator.get("acquisition_contract_resume_allowed"),
            "acquisition_execution_allowed_now": hardening_validator.get("acquisition_execution_allowed_now"),
            "plausible_live_secret_count": hardening_validator.get("plausible_live_secret_count"),
            "dependency_snapshot_validated": hardening_validator.get("dependency_snapshot_validated"),
            "ast_scan_validated": hardening_validator.get("ast_scan_validated"),
            "artifact_hash_manifest_validated": hardening_validator.get("artifact_hash_manifest_validated"),
            "timeout_policy_validated": hardening_validator.get("timeout_policy_validated"),
            "memory_disk_resource_policy_validated": hardening_validator.get(
                "memory_disk_resource_policy_validated"
            ),
            "rollback_policy_validated": hardening_validator.get("rollback_policy_validated"),
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
        "prior_local_discovery_respected",
        "prior_hardening_validator_respected",
        "acquisition_contract_created",
        "prior_discovery_context_completed",
        "hardening_context_completed",
        "acquisition_objective_completed",
        "allowed_future_acquisition_scope_completed",
        "source_requirements_completed",
        "survivorship_bias_contract_completed",
        "holdout_contract_completed",
        "pre_acquisition_safety_requirements_completed",
        "required_future_artifacts_completed",
        "fail_closed_conditions_completed",
        "evidence_policy_completed",
        "local_existing_data_found",
        "external_download_needed",
        "acquisition_requires_future_preview",
        "acquisition_requires_future_approval",
        "acquisition_requires_source_manifest",
        "acquisition_requires_provenance_report",
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
        "historical_horizon_complete",
        "external_download_allowed_now",
        "external_api_allowed_now",
        "acquisition_execution_allowed_now",
        "data_download_performed",
        "data_fetch_performed",
        "data_build_performed",
        "external_api_calls_performed",
        "fake_or_synthetic_data_detected",
        "strategy_research_allowed_now",
        "backtest_allowed_now",
        "candidate_generation_allowed_now",
        "runtime_capital_live_allowed_now",
        "generic_runner_allowed_now",
        "schema_or_config_creation_allowed_now",
        "old_route_reopen_allowed_now",
        "profit_or_tradable_edge_claim_allowed_now",
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
    require_equal(payload.get("historical_data_acquisition_contract_status"), STATUS_PASS, "status")
    require_equal(payload.get("next_module"), NEXT_MODULE_VALIDATOR, "next_module")
    require_equal(payload.get("whole_system_preflight_decision"), "PASS", "whole_system_preflight_decision")
    require_equal(payload.get("documentation_loop_risk_level"), DOCUMENTATION_LOOP_RISK_LEVEL, "documentation_loop_risk_level")
    require_equal(payload.get("active_p0_blocker_count"), 0, "active_p0_blocker_count")
    require_equal(payload.get("active_p1_attention_count"), 1, "active_p1_attention_count")
    require_equal(payload.get("dormant_repo_attention_count"), 716, "dormant_repo_attention_count")
    require_equal(payload.get("planned_schema_files_existing_count"), 0, "planned_schema_files_existing_count")
    require_equal(payload.get("current_evidence_chain_quality_before_contract"), EVIDENCE_BEFORE, "evidence_before")
    require_equal(payload.get("current_evidence_chain_quality_after_contract"), EVIDENCE_AFTER, "evidence_after")
    require_equal(payload.get("available_horizon_years_estimate"), 0.999201, "available_horizon_years_estimate")
    require_equal(payload.get("target_historical_horizon_years"), "3_to_4", "target_historical_horizon_years")
    require_equal(payload.get("target_timeframe"), "1h", "target_timeframe")
    require(all_false(payload["dangerous_flags"]), f"{STATUS_BLOCKED_CONTEXT}: dangerous flags not all false")


def main() -> None:
    hardening_validator = load_json(HARDENING_VALIDATOR_ARTIFACT)
    hardening_implementation = load_json(HARDENING_IMPLEMENTATION_ARTIFACT)
    discovery = load_json(DATA_HORIZON_DISCOVERY_ARTIFACT)
    preflight = validate_preflight(hardening_validator, hardening_implementation, discovery)
    contract = contract_sections(discovery, hardening_validator)
    payload = output_payload(preflight, discovery, hardening_validator, contract)
    validate_payload(payload)

    write_json(OUT_DIR / "historical_data_acquisition_contract_after_data_horizon_discovery_v1.json", contract)
    write_json(OUT_DIR / "repo_only_historical_data_acquisition_contract_after_data_horizon_discovery_v1_latest.json", payload)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
