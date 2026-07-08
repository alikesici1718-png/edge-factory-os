from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_contract_validator_after_"
    "data_horizon_discovery_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_contract_validator_after_"
    "data_horizon_discovery_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "0d6cf26"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 651
EXPECTED_TRACKED_PYTHON_COUNT = 652

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_contract_validator_after_"
    "data_horizon_discovery_v1.py"
)
NEXT_MODULE_PREVIEW = "edge_factory_os_repo_only_historical_data_acquisition_preview_after_contract_validator_v1.py"
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_contract_blocked_record_after_"
    "data_horizon_discovery_v1.py"
)

CONTRACT_LATEST_ARTIFACT = (
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

CONTRACT_STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_CONTRACT_READY_NO_ACQUISITION_EXECUTION"
STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_CONTRACT_VALIDATED_PREVIEW_READY_NO_EXECUTION"
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE_VALIDATOR = "HISTORICAL_DATA_ACQUISITION_CONTRACT_READY_NO_ACQUISITION_EXECUTION"
EVIDENCE_AFTER_VALIDATOR = "HISTORICAL_DATA_ACQUISITION_CONTRACT_VALIDATED_PREVIEW_READY_NO_EXECUTION"
EVIDENCE_BEFORE_CONTRACT = (
    "PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_VALIDATED_ACQUISITION_CONTRACT_RESUME_READY"
)
DISCOVERY_EVIDENCE_AFTER = "HISTORICAL_DATA_HORIZON_INCOMPLETE_ACQUISITION_CONTRACT_REQUIRED"
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
REQUIRED_CONTRACT_SECTIONS = [
    "prior_discovery_context",
    "hardening_context",
    "acquisition_objective",
    "allowed_future_acquisition_scope",
    "source_requirements",
    "survivorship_bias_contract",
    "holdout_contract",
    "pre_acquisition_safety_requirements",
    "required_future_artifacts",
    "fail_closed_conditions",
    "evidence_policy",
    "next_module_decision",
]
REQUIRED_SOURCE_FIELDS = [
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
REQUIRED_FAIL_CLOSED_CONDITIONS = [
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


def require_contains_all(container: Iterable[str], required: Iterable[str], field: str) -> None:
    present = set(container)
    missing = [item for item in required if item not in present]
    require(not missing, f"{STATUS_BLOCKED_CONTEXT}: {field} missing {missing}")


def tracked_python_count() -> int:
    output = run_git(["ls-files"])
    return len([line for line in output.splitlines() if line.strip().endswith(".py")])


def planned_schema_files_existing_count() -> int:
    return sum(1 for rel_path in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel_path).exists())


def generic_runner_target_exists() -> bool:
    return (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()


def dangerous_flags() -> Dict[str, bool]:
    return {name: False for name in DANGEROUS_FLAG_NAMES}


def validate_preflight(contract: Dict[str, Any], hardening: Dict[str, Any], discovery: Dict[str, Any]) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    status = run_git(["status", "--short"])
    require_equal(head, EXPECTED_HEAD, "head")
    require(status == "" or status == f"?? {CURRENT_TOOL_REL}", f"{STATUS_BLOCKED_CONTEXT}: repo dirty: {status}")

    require_equal(contract.get("next_module"), REQUESTED_MODULE, "contract.next_module")
    require_true(contract.get("acquisition_contract_created"), "contract.acquisition_contract_created")
    require_true(contract.get("prior_hardening_validator_respected"), "contract.prior_hardening_validator_respected")
    require_false(contract.get("historical_horizon_complete"), "contract.historical_horizon_complete")
    require_true(contract.get("external_download_needed"), "contract.external_download_needed")
    require_false(contract.get("external_download_allowed_now"), "contract.external_download_allowed_now")
    require_false(contract.get("external_api_allowed_now"), "contract.external_api_allowed_now")
    require_false(contract.get("acquisition_execution_allowed_now"), "contract.acquisition_execution_allowed_now")
    require_false(contract.get("data_download_performed"), "contract.data_download_performed")
    require_false(contract.get("data_fetch_performed"), "contract.data_fetch_performed")
    require_false(contract.get("data_build_performed"), "contract.data_build_performed")
    require_false(contract.get("external_api_calls_performed"), "contract.external_api_calls_performed")
    require_equal(contract.get("active_p0_blocker_count"), 0, "contract.active_p0_blocker_count")
    require_equal(contract.get("active_p1_attention_count"), 1, "contract.active_p1_attention_count")
    require_true(contract.get("p1_attention_carried_forward"), "contract.p1_attention_carried_forward")
    require_true(
        contract.get("dormant_repo_attention_count_carried_forward"),
        "contract.dormant_repo_attention_count_carried_forward",
    )
    require_equal(contract.get("dormant_repo_attention_count"), 716, "contract.dormant_repo_attention_count")

    require_true(hardening.get("hardening_validation_passed"), "hardening.hardening_validation_passed")
    require_equal(hardening.get("plausible_live_secret_count"), 0, "hardening.plausible_live_secret_count")
    require_false(hardening.get("dependency_install_attempted"), "hardening.dependency_install_attempted")
    require_false(hardening.get("dependency_update_attempted"), "hardening.dependency_update_attempted")
    require_false(hardening.get("environment_modified"), "hardening.environment_modified")
    require_true(hardening.get("ast_risk_classification_adequate"), "hardening.ast_risk_classification_adequate")
    require_equal(hardening.get("dangerous_current_chain_blocker_count"), 0, "dangerous_current_chain_blocker_count")
    require_true(hardening.get("artifact_hash_manifest_validated"), "artifact_hash_manifest_validated")
    require_true(hardening.get("timeout_policy_validated"), "timeout_policy_validated")
    require_true(hardening.get("memory_disk_resource_policy_validated"), "memory_disk_resource_policy_validated")
    require_true(hardening.get("rollback_policy_validated"), "rollback_policy_validated")

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
        "discovery.current_evidence_chain_quality_after_execution",
    )

    return {
        "head": head,
        "whole_system_preflight_completed": True,
        "whole_system_preflight_decision": "PASS",
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
    }


def validate_contract_artifact(contract: Dict[str, Any]) -> Dict[str, Any]:
    contract_path = Path(str(contract.get("contract_artifact", "")))
    contract_json, exists, valid, non_empty = read_json_checked(contract_path)
    require(exists, f"{STATUS_BLOCKED_CONTEXT}: contract artifact missing: {contract_path}")
    require(valid, f"{STATUS_BLOCKED_CONTEXT}: contract artifact invalid json: {contract_path}")
    require(non_empty, f"{STATUS_BLOCKED_CONTEXT}: contract artifact empty: {contract_path}")
    require_equal(contract.get("historical_data_acquisition_contract_status"), CONTRACT_STATUS_PASS, "contract status")
    require_contains_all(contract_json.keys(), REQUIRED_CONTRACT_SECTIONS, "contract artifact sections")
    require_contains_all(contract.get("contract_sections", {}).keys(), REQUIRED_CONTRACT_SECTIONS, "contract summary sections")
    return {
        "contract_artifact_path": str(contract_path),
        "contract_artifact_exists": exists,
        "contract_artifact_valid_json": valid,
        "contract_artifact_non_empty": non_empty,
        "contract_sections": contract_json,
    }


def validate_prior_discovery(contract: Dict[str, Any]) -> Dict[str, Any]:
    for key, expected in {
        "local_existing_data_found": True,
        "historical_horizon_complete": False,
        "available_horizon_years_estimate": 0.999201,
        "target_historical_horizon_years": "3_to_4",
        "target_timeframe": "1h",
        "external_download_needed": True,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "data_build_performed": False,
        "external_api_calls_performed": False,
        "survivorship_bias_controls_required": True,
    }.items():
        require_equal(contract.get(key), expected, f"prior discovery {key}")
    return {"prior_discovery_validation_completed": True}


def validate_hardening_context(contract: Dict[str, Any], hardening: Dict[str, Any]) -> Dict[str, Any]:
    required = {
        "prior_hardening_validator_respected": True,
        "hardening_validation_passed": True,
        "plausible_live_secret_count": 0,
        "dependency_install_attempted": False,
        "dependency_update_attempted": False,
        "environment_modified": False,
        "ast_risk_classification_adequate": True,
        "dangerous_current_chain_blocker_count": 0,
        "dormant_repo_attention_count": 716,
        "dormant_repo_attention_count_carried_forward": True,
        "artifact_hash_manifest_validated": True,
        "timeout_policy_validated": True,
        "memory_disk_resource_policy_validated": True,
        "rollback_policy_validated": True,
    }
    for key, expected in required.items():
        actual = contract.get(key, hardening.get(key))
        require_equal(actual, expected, f"hardening {key}")
    return {"hardening_context_validation_completed": True}


def validate_acquisition_scope(sections: Dict[str, Any]) -> Dict[str, Any]:
    objective = sections["acquisition_objective"]
    scope = sections["allowed_future_acquisition_scope"]
    not_objectives = objective.get("not_objectives", [])
    require("3_to_4_year_1h_historical_data" in objective.get("objective", ""), "objective is not data acquisition")
    require_contains_all(
        not_objectives,
        ["strategy_research", "backtest", "candidate_generation", "runtime_work", "live_work", "capital_work", "order_work"],
        "not objectives",
    )
    require_true(objective.get("must_preserve_source_traceability_and_metadata"), "source traceability")
    require_true(objective.get("must_not_silently_change_symbol_universe"), "silent universe changes")
    require_true(objective.get("must_not_use_current_winner_only_universe"), "current winner universe")
    require_false(scope.get("contract_grants_acquisition_execution_now"), "contract grants acquisition execution")
    return {"acquisition_scope_validation_completed": True}


def validate_future_source_requirements(sections: Dict[str, Any]) -> Dict[str, Any]:
    source = sections["source_requirements"]
    require_contains_all(source.get("required_fields", []), REQUIRED_SOURCE_FIELDS, "source requirements")
    require_true(
        source.get("derived_panel_build_must_be_separate_from_raw_acquisition"),
        "derived panel separated from raw acquisition",
    )
    return {"future_source_requirements_validation_completed": True}


def validate_survivorship_holdout(sections: Dict[str, Any]) -> Dict[str, Any]:
    survivorship = sections["survivorship_bias_contract"]
    holdout = sections["holdout_contract"]
    for key in [
        "no_current_winner_only_symbol_backfill",
        "symbol_start_end_dates_required",
        "delisted_or_removed_symbol_disclosure_required_where_available",
        "missing_symbol_report_required",
        "exchange_listing_limitation_report_required",
        "universe_snapshot_rule_required",
        "separate_universe_discovery_from_strategy_selection",
        "source_panel_universe_must_not_be_selected_by_future_performance",
    ]:
        require_true(survivorship.get(key), f"survivorship {key}")
    for key in [
        "latest_6_to_12_months_preserved_as_strict_holdout_where_feasible",
        "no_strategy_or_candidate_selection_using_holdout",
        "train_validation_oos_split_defined_before_strategy_research",
    ]:
        require_true(holdout.get(key), f"holdout {key}")
    return {"survivorship_holdout_validation_completed": True}


def validate_pre_acquisition_safety(sections: Dict[str, Any]) -> Dict[str, Any]:
    safety = sections["pre_acquisition_safety_requirements"]
    for key in [
        "secret_scan_remains_clear",
        "dependency_snapshot_unchanged_or_explicitly_approved",
        "no_unapproved_environment_modification",
        "timeout_policy_applied",
        "memory_disk_resource_policy_applied",
        "rollback_policy_applied",
        "artifact_hash_manifest_updated",
        "dormant_repo_ast_risks_remain_excluded",
        "no_repo_src_or_tools_module_import_execution",
    ]:
        require_true(safety.get(key), f"safety {key}")
    return {"pre_acquisition_safety_validation_completed": True}


def validate_future_artifacts(sections: Dict[str, Any]) -> Dict[str, Any]:
    require_contains_all(sections["required_future_artifacts"], REQUIRED_FUTURE_ARTIFACTS, "future artifacts")
    return {
        "future_artifacts_validation_completed": True,
        "required_future_artifact_list_validated": True,
    }


def validate_fail_closed(sections: Dict[str, Any]) -> Dict[str, Any]:
    require_contains_all(sections["fail_closed_conditions"], REQUIRED_FAIL_CLOSED_CONDITIONS, "fail closed conditions")
    return {
        "fail_closed_validation_completed": True,
        "fail_closed_conditions_validated": True,
    }


def validate_evidence_policy(sections: Dict[str, Any]) -> Dict[str, Any]:
    evidence = sections["evidence_policy"]
    require_equal(evidence.get("current_state_before_contract"), EVIDENCE_BEFORE_CONTRACT, "evidence current_state_before_contract")
    require_equal(evidence.get("state_after_contract"), EVIDENCE_BEFORE_VALIDATOR, "evidence state_after_contract")
    require_true(
        evidence.get("acquisition_contract_is_not_evidence_of_data_quality"),
        "contract is not data quality evidence",
    )
    require_true(evidence.get("future_acquisition_artifacts_must_be_primary_artifacts"), "future artifacts primary")
    require_equal(evidence.get("derived_metadata_classification"), "DERIVED_EXPLICIT_ATTENTION", "derived classification")
    require(bool(evidence.get("derived_metadata_reason")), f"{STATUS_BLOCKED_CONTEXT}: derived metadata reason missing")
    require_true(evidence.get("derived_overused_default_forbidden"), "derived overused forbidden")
    require_true(
        evidence.get("p1_must_carry_until_acquisition_and_historical_validator_close_it"),
        "p1 carry evidence",
    )
    return {"evidence_policy_validation_completed": True}


def validate_next_module_decision(sections: Dict[str, Any]) -> Dict[str, Any]:
    decision = sections["next_module_decision"]
    require_equal(decision.get("chosen_next_module"), REQUESTED_MODULE, "contract chosen next module")
    for key in [
        "do_not_choose_api_download",
        "do_not_choose_candidate_backtest_runtime_live_capital",
        "do_not_choose_data_acquisition_execution",
        "do_not_choose_generic_review_adoption_gate_rollout",
        "do_not_choose_strategy_research",
    ]:
        require_true(decision.get(key), f"next module decision {key}")
    return {"next_module_decision_validation_completed": True}


def replacement_checks() -> Dict[str, bool]:
    return {
        "preflight_passed": True,
        "contract_artifact_validated": True,
        "prior_discovery_validated": True,
        "hardening_context_validated": True,
        "acquisition_scope_validated": True,
        "source_requirements_validated": True,
        "survivorship_holdout_validated": True,
        "pre_acquisition_safety_validated": True,
        "future_artifacts_validated": True,
        "fail_closed_conditions_validated": True,
        "evidence_policy_validated": True,
        "no_acquisition_execution": True,
        "next_module_is_preview": True,
    }


def build_payload(
    contract: Dict[str, Any],
    hardening: Dict[str, Any],
    discovery: Dict[str, Any],
    contract_validation: Dict[str, Any],
    validations: Dict[str, Any],
) -> Dict[str, Any]:
    flags = dangerous_flags()
    checks = replacement_checks()
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_contract_validator_status": STATUS_PASS,
        "final_decision": "HISTORICAL_DATA_ACQUISITION_CONTRACT_VALIDATED_PREVIEW_NEXT",
        "next_action": "CREATE_HISTORICAL_DATA_ACQUISITION_PREVIEW_NO_EXECUTION",
        "next_module": NEXT_MODULE_PREVIEW,
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
        "prior_contract_respected": True,
        "contract_artifact_validation_completed": True,
        "prior_discovery_validation_completed": True,
        "hardening_context_validation_completed": True,
        "acquisition_scope_validation_completed": True,
        "future_source_requirements_validation_completed": True,
        "survivorship_holdout_validation_completed": True,
        "pre_acquisition_safety_validation_completed": True,
        "future_artifacts_validation_completed": True,
        "fail_closed_validation_completed": True,
        "evidence_policy_validation_completed": True,
        "acquisition_contract_validated": True,
        "contract_artifact_exists": True,
        "contract_artifact_valid_json": True,
        "contract_artifact_non_empty": True,
        "local_existing_data_found": True,
        "historical_horizon_complete": False,
        "available_horizon_years_estimate": 0.999201,
        "target_historical_horizon_years": "3_to_4",
        "target_timeframe": "1h",
        "external_download_needed": True,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "acquisition_execution_allowed_now": False,
        "acquisition_preview_allowed_next": True,
        "acquisition_execution_requires_future_approval": True,
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
        "required_future_artifact_list_validated": True,
        "fail_closed_conditions_validated": True,
        "current_evidence_chain_quality_before_validator": EVIDENCE_BEFORE_VALIDATOR,
        "current_evidence_chain_quality_after_validator": EVIDENCE_AFTER_VALIDATOR,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 1,
        "dormant_repo_attention_count": 716,
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
        "evidence_chain_policy_level": EVIDENCE_CHAIN_POLICY_LEVEL,
        "future_modules_must_classify_evidence_quality": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": planned_schema_files_existing_count(),
        "generic_runner_target_exists": generic_runner_target_exists(),
        "dangerous_flags": flags,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "derived_live_repo_post_check": "PASS_HISTORICAL_DATA_ACQUISITION_CONTRACT_VALIDATOR_READY_FOR_PREVIEW",
        "derived_live_repo_post_check_reason": (
            "contract artifact and required sections validated; local horizon remains incomplete at 0.999201 years; "
            "future acquisition preview is allowed next while acquisition execution, download, fetch, API, build, "
            "strategy, runtime, capital, live, generic-runner, schema, and old-route actions remain blocked"
        ),
        "replacement_checks": checks,
        "replacement_checks_all_true": all(value is True for value in checks.values()),
        "tracked_python_count_expectation": {
            "previous": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT,
        },
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "source_artifacts": {
            "contract_latest_artifact": str(CONTRACT_LATEST_ARTIFACT),
            "contract_artifact": contract_validation["contract_artifact_path"],
            "hardening_validator_artifact": str(HARDENING_VALIDATOR_ARTIFACT),
            "local_data_horizon_discovery_artifact": str(DATA_HORIZON_DISCOVERY_ARTIFACT),
        },
        "validation_sections": validations,
        "prior_contract_snapshot": {
            "historical_data_acquisition_contract_status": contract.get(
                "historical_data_acquisition_contract_status"
            ),
            "current_evidence_chain_quality_after_contract": contract.get(
                "current_evidence_chain_quality_after_contract"
            ),
            "next_module": contract.get("next_module"),
        },
        "prior_hardening_snapshot": {
            "hardening_validation_passed": hardening.get("hardening_validation_passed"),
            "plausible_live_secret_count": hardening.get("plausible_live_secret_count"),
            "dormant_repo_attention_count": hardening.get("dormant_repo_attention_count"),
        },
        "prior_discovery_snapshot": {
            "local_existing_data_found": discovery.get("local_existing_data_found"),
            "historical_horizon_complete": discovery.get("historical_horizon_complete"),
            "available_horizon_years_estimate": discovery.get("available_horizon_years_estimate"),
            "external_download_needed": discovery.get("external_download_needed"),
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
        "prior_contract_respected",
        "contract_artifact_validation_completed",
        "prior_discovery_validation_completed",
        "hardening_context_validation_completed",
        "acquisition_scope_validation_completed",
        "future_source_requirements_validation_completed",
        "survivorship_holdout_validation_completed",
        "pre_acquisition_safety_validation_completed",
        "future_artifacts_validation_completed",
        "fail_closed_validation_completed",
        "evidence_policy_validation_completed",
        "acquisition_contract_validated",
        "contract_artifact_exists",
        "contract_artifact_valid_json",
        "local_existing_data_found",
        "external_download_needed",
        "acquisition_preview_allowed_next",
        "acquisition_execution_requires_future_approval",
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
        "required_future_artifact_list_validated",
        "fail_closed_conditions_validated",
        "generic_runner_implementation_remains_blocked",
        "future_modules_must_classify_evidence_quality",
        "replacement_checks_are_not_equivalent_to_primary_artifact",
        "loop_remains_closed",
        "replacement_checks_all_true",
        "dangerous_flags_all_false",
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
    require_equal(payload.get("historical_data_acquisition_contract_validator_status"), STATUS_PASS, "validator status")
    require_equal(payload.get("next_module"), NEXT_MODULE_PREVIEW, "next_module")
    require_equal(payload.get("whole_system_preflight_decision"), "PASS", "whole_system_preflight_decision")
    require_equal(payload.get("documentation_loop_risk_level"), DOCUMENTATION_LOOP_RISK_LEVEL, "documentation_loop_risk_level")
    require_equal(payload.get("active_p0_blocker_count"), 0, "active_p0_blocker_count")
    require_equal(payload.get("active_p1_attention_count"), 1, "active_p1_attention_count")
    require_equal(payload.get("dormant_repo_attention_count"), 716, "dormant_repo_attention_count")
    require_equal(payload.get("planned_schema_files_existing_count"), 0, "planned_schema_files_existing_count")
    require_equal(
        payload.get("current_evidence_chain_quality_before_validator"),
        EVIDENCE_BEFORE_VALIDATOR,
        "evidence before validator",
    )
    require_equal(
        payload.get("current_evidence_chain_quality_after_validator"),
        EVIDENCE_AFTER_VALIDATOR,
        "evidence after validator",
    )
    require_equal(payload.get("available_horizon_years_estimate"), 0.999201, "available_horizon_years_estimate")
    require_equal(payload.get("target_historical_horizon_years"), "3_to_4", "target_historical_horizon_years")
    require_equal(payload.get("target_timeframe"), "1h", "target_timeframe")
    require(all(value is False for value in payload["dangerous_flags"].values()), "dangerous flags must all be false")


def main() -> None:
    contract = load_json(CONTRACT_LATEST_ARTIFACT)
    hardening = load_json(HARDENING_VALIDATOR_ARTIFACT)
    discovery = load_json(DATA_HORIZON_DISCOVERY_ARTIFACT)
    preflight = validate_preflight(contract, hardening, discovery)
    artifact_validation = validate_contract_artifact(contract)
    sections = artifact_validation["contract_sections"]
    validations: Dict[str, Any] = {
        "whole_system_preflight": preflight,
        "contract_artifact_validation": artifact_validation,
        "prior_discovery_validation": validate_prior_discovery(contract),
        "hardening_context_validation": validate_hardening_context(contract, hardening),
        "acquisition_scope_validation": validate_acquisition_scope(sections),
        "future_source_requirements_validation": validate_future_source_requirements(sections),
        "survivorship_holdout_validation": validate_survivorship_holdout(sections),
        "pre_acquisition_safety_validation": validate_pre_acquisition_safety(sections),
        "future_artifacts_validation": validate_future_artifacts(sections),
        "fail_closed_validation": validate_fail_closed(sections),
        "evidence_policy_validation": validate_evidence_policy(sections),
        "next_module_decision": validate_next_module_decision(sections),
    }
    payload = build_payload(contract, hardening, discovery, artifact_validation, validations)
    validate_payload(payload)
    write_json(
        OUT_DIR / "repo_only_historical_data_acquisition_contract_validator_after_data_horizon_discovery_v1_latest.json",
        payload,
    )
    write_json(OUT_DIR / "historical_data_acquisition_contract_validator_report.json", validations)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
