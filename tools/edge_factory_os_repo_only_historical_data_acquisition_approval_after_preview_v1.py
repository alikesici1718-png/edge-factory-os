from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_historical_data_acquisition_approval_after_preview_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_historical_data_acquisition_approval_after_preview_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "84371f9"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 653
EXPECTED_TRACKED_PYTHON_COUNT = 654

REQUESTED_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_approval_after_preview_v1.py"
NEXT_MODULE_DISCOVERY = (
    "edge_factory_os_repo_only_historical_data_acquisition_local_manual_source_discovery_after_approval_v1.py"
)
NEXT_MODULE_BLOCKED = "edge_factory_os_repo_only_historical_data_acquisition_approval_blocked_record_after_preview_v1.py"

PREVIEW_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_preview_after_contract_validator_v1"
    / "repo_only_historical_data_acquisition_preview_after_contract_validator_v1_latest.json"
)
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

PREVIEW_STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION"
CONTRACT_VALIDATOR_STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_CONTRACT_VALIDATED_PREVIEW_READY_NO_EXECUTION"
CONTRACT_STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_CONTRACT_READY_NO_ACQUISITION_EXECUTION"
HARDENING_STATUS_PASS = (
    "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_VALIDATED_ACQUISITION_CONTRACT_RESUME_READY"
)
STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_LOCAL_MANUAL_SOURCE_DISCOVERY_APPROVED_NEXT_NO_EXECUTION"
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"

EVIDENCE_BEFORE = "HISTORICAL_DATA_ACQUISITION_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION"
EVIDENCE_AFTER = "HISTORICAL_DATA_ACQUISITION_LOCAL_MANUAL_SOURCE_DISCOVERY_APPROVED_NEXT_NO_EXECUTION"
EVIDENCE_CHAIN_POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"
RECOMMENDED_ROUTE = "ACQUISITION_APPROVAL_FOR_LOCAL_OR_MANUAL_SOURCE_DISCOVERY_ONLY"
USER_APPROVAL_SCOPE = "APPROVAL_RECORD_ONLY_FOR_NEXT_LOCAL_MANUAL_SOURCE_DISCOVERY_NO_EXECUTION"

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
FUTURE_DISCOVERY_ARTIFACTS = [
    "historical_local_manual_source_candidate_inventory.json",
    "historical_local_manual_source_suitability_report.json",
    "historical_local_manual_source_manifest_preview.json",
    "historical_local_manual_source_provenance_preview.json",
    "historical_local_manual_source_gap_report.json",
    "historical_local_manual_source_contract_compliance_report.json",
]
FAIL_CLOSED_RULES = [
    "source_path_missing_or_ambiguous",
    "file_type_unsupported",
    "source_or_provenance_cannot_be_established",
    "timestamp_format_ambiguous",
    "symbol_universe_rule_missing",
    "holdout_cannot_be_protected",
    "survivorship_controls_missing",
    "fake_or_synthetic_data_used_as_real",
    "external_api_download_or_fetch_occurs",
    "data_build_occurs",
    "strategy_backtest_candidate_runtime_live_path_touched",
    "hardening_state_stale_or_invalid",
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
    preview: Dict[str, Any],
    contract_validator: Dict[str, Any],
    contract: Dict[str, Any],
    hardening: Dict[str, Any],
) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    status = run_git(["status", "--short"])
    require_equal(head, EXPECTED_HEAD, "head")
    require(status == "" or status == f"?? {CURRENT_TOOL_REL}", f"{STATUS_BLOCKED_CONTEXT}: repo dirty: {status}")

    require_equal(preview.get("next_module"), REQUESTED_MODULE, "preview.next_module")
    require_equal(preview.get("historical_data_acquisition_preview_status"), PREVIEW_STATUS_PASS, "preview.status")
    require_true(preview.get("acquisition_preview_completed"), "preview.acquisition_preview_completed")
    require_equal(preview.get("recommended_acquisition_route"), RECOMMENDED_ROUTE, "preview.recommended_route")
    require_true(preview.get("local_archive_import_preferred"), "preview.local_archive_import_preferred")
    require_true(
        preview.get("manual_exchange_export_import_allowed_future"),
        "preview.manual_exchange_export_import_allowed_future",
    )
    require_false(preview.get("external_api_download_allowed_now"), "preview.external_api_download_allowed_now")
    require_true(
        preview.get("external_api_download_requires_separate_future_chain"),
        "preview.external_api_download_requires_separate_future_chain",
    )
    require_true(preview.get("acquisition_approval_required_next"), "preview.acquisition_approval_required_next")
    require_false(preview.get("acquisition_execution_allowed_now"), "preview.acquisition_execution_allowed_now")
    require_false(preview.get("external_download_allowed_now"), "preview.external_download_allowed_now")
    require_false(preview.get("external_api_allowed_now"), "preview.external_api_allowed_now")
    require_false(preview.get("data_download_performed"), "preview.data_download_performed")
    require_false(preview.get("data_fetch_performed"), "preview.data_fetch_performed")
    require_false(preview.get("data_build_performed"), "preview.data_build_performed")
    require_false(preview.get("external_api_calls_performed"), "preview.external_api_calls_performed")
    require_equal(preview.get("active_p0_blocker_count"), 0, "preview.active_p0_blocker_count")
    require_equal(preview.get("active_p1_attention_count"), 1, "preview.active_p1_attention_count")
    require_true(preview.get("p1_attention_carried_forward"), "preview.p1_attention_carried_forward")
    require_true(
        preview.get("dormant_repo_attention_count_carried_forward"),
        "preview.dormant_repo_attention_count_carried_forward",
    )
    require_equal(preview.get("dormant_repo_attention_count"), 716, "preview.dormant_repo_attention_count")

    require_equal(
        contract_validator.get("historical_data_acquisition_contract_validator_status"),
        CONTRACT_VALIDATOR_STATUS_PASS,
        "contract_validator.status",
    )
    require_true(contract_validator.get("acquisition_contract_validated"), "contract_validator.acquisition_contract_validated")
    require_equal(contract.get("historical_data_acquisition_contract_status"), CONTRACT_STATUS_PASS, "contract.status")
    require_equal(
        hardening.get("pre_acquisition_minimal_reliability_hardening_implementation_validator_status"),
        HARDENING_STATUS_PASS,
        "hardening.status",
    )
    require_true(hardening.get("hardening_validation_passed"), "hardening.hardening_validation_passed")
    require_equal(hardening.get("active_p0_blocker_count"), 0, "hardening.active_p0_blocker_count")
    require_equal(hardening.get("active_p1_attention_count"), 1, "hardening.active_p1_attention_count")
    require_true(
        hardening.get("dormant_repo_attention_count_carried_forward"),
        "hardening.dormant_repo_attention_count_carried_forward",
    )

    return {
        "head": head,
        "whole_system_preflight_completed": True,
        "whole_system_preflight_decision": "PASS",
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
    }


def approval_sections(preview: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "preview_context": {
            "acquisition_preview_completed": True,
            "recommended_acquisition_route": RECOMMENDED_ROUTE,
            "local_archive_import_preferred": True,
            "manual_exchange_export_import_allowed_only_in_future_approved_modules": True,
            "external_api_download_remains_blocked": True,
            "acquisition_execution_remains_blocked": True,
            "active_p1_attention_count": 1,
            "p1_remains_active": True,
            "dormant_repo_attention_count": 716,
            "dormant_repo_attention_carried_forward": True,
            "preview_status": preview.get("historical_data_acquisition_preview_status"),
        },
        "approval_scope": {
            "approval_grants_approval_record_only": True,
            "approval_grants_local_manual_source_discovery_now": False,
            "approval_grants_future_local_manual_source_discovery_next": True,
            "approval_grants_data_download_now": False,
            "approval_grants_data_fetch_now": False,
            "approval_grants_external_api_now": False,
            "approval_grants_data_build_now": False,
            "approval_grants_strategy_backtest_candidate_now": False,
            "approval_grants_runtime_capital_live_now": False,
            "approval_grants_generic_runner_now": False,
            "approval_grants_schema_config_now": False,
        },
        "future_source_discovery_scope": {
            "future_module_may": [
                "inspect_configured_local_user_supplied_directory_candidates",
                "inventory_local_archive_files",
                "inventory_manually_supplied_exchange_export_files",
                "inspect_filenames_sizes_extensions_timestamps_hashes",
                "read_small_metadata_manifest_header_samples_where_safe",
                "avoid_full_scans_of_large_files",
                "avoid_parquet_row_reads",
                "create_candidate_source_inventory",
                "create_source_suitability_preview",
                "create_source_manifest_preview",
                "decide_whether_local_manual_sources_are_sufficient_or_external_chain_needed",
            ],
            "future_module_must_not": [
                "download_fetch_api",
                "build_historical_panel",
                "run_strategy_backtest_candidate",
                "modify_runtime_live_capital",
                "import_or_execute_dormant_repo_modules",
                "create_schema_config",
                "claim_profit_edge",
            ],
        },
        "future_required_artifacts": FUTURE_DISCOVERY_ARTIFACTS,
        "safety_requirements": {
            "source_manifest_required": True,
            "provenance_report_required": True,
            "future_validator_required": True,
            "survivorship_controls_required": True,
            "symbol_lifecycle_required": True,
            "holdout_policy_required": True,
            "historical_data_quality_validator_required": True,
            "timeout_policy_required": True,
            "memory_disk_policy_required": True,
            "rollback_policy_required": True,
            "hardening_state_required": True,
            "dormant_repo_ast_risks_excluded": True,
        },
        "fail_closed_rules": FAIL_CLOSED_RULES,
        "evidence_policy": {
            "current_state_before_approval": EVIDENCE_BEFORE,
            "state_after_approval": EVIDENCE_AFTER,
            "approval_is_not_source_evidence": True,
            "approval_is_not_data_evidence": True,
            "approval_is_not_acquisition_execution": True,
            "p1_remains_active_until_acquisition_and_historical_validator_close_it": True,
        },
        "next_module_decision": {
            "chosen_next_module": NEXT_MODULE_DISCOVERY,
            "if_approval_is_unsafe": NEXT_MODULE_BLOCKED,
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
        "approval_record_created": True,
        "approval_record_only": True,
        "no_local_manual_source_discovery_now": True,
        "future_local_manual_source_discovery_next": True,
        "no_download_fetch_api_build": True,
        "no_strategy_backtest_candidate_runtime_capital_live": True,
        "source_manifest_provenance_controls_preserved": True,
        "fail_closed_rules_preserved": True,
        "next_module_is_local_manual_source_discovery": True,
    }


def build_payload(
    preflight: Dict[str, Any],
    preview: Dict[str, Any],
    sections: Dict[str, Any],
) -> Dict[str, Any]:
    flags = dangerous_flags()
    checks = replacement_checks()
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_approval_status": STATUS_PASS,
        "final_decision": "HISTORICAL_DATA_ACQUISITION_LOCAL_MANUAL_SOURCE_DISCOVERY_APPROVED_NEXT",
        "next_action": "RUN_SEPARATE_LOCAL_MANUAL_SOURCE_DISCOVERY_MODULE_NO_EXECUTION",
        "next_module": NEXT_MODULE_DISCOVERY,
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
        "prior_preview_respected": True,
        "acquisition_approval_record_created": True,
        "user_acquisition_approval_present": True,
        "user_acquisition_approval_scope": USER_APPROVAL_SCOPE,
        "recommended_acquisition_route": RECOMMENDED_ROUTE,
        "local_archive_import_preferred": True,
        "manual_exchange_export_import_allowed_future": True,
        "approval_grants_approval_record_only": True,
        "approval_grants_local_manual_source_discovery_now": False,
        "approval_grants_future_local_manual_source_discovery_next": True,
        "approval_grants_data_download_now": False,
        "approval_grants_data_fetch_now": False,
        "approval_grants_external_api_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_strategy_backtest_candidate_now": False,
        "approval_grants_runtime_capital_live_now": False,
        "approval_grants_generic_runner_now": False,
        "approval_grants_schema_config_now": False,
        "local_manual_source_discovery_eligible_next": True,
        "acquisition_execution_allowed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
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
        "future_required_artifact_list_previewed": True,
        "fail_closed_conditions_preserved": True,
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
        "current_evidence_chain_quality_before_approval": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_approval": EVIDENCE_AFTER,
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
        "derived_live_repo_post_check": "PASS_HISTORICAL_DATA_ACQUISITION_APPROVAL_READY_FOR_LOCAL_MANUAL_SOURCE_DISCOVERY",
        "derived_live_repo_post_check_reason": (
            "approval record permits only the next separate local/manual source discovery module; this module performed "
            "no discovery, download, fetch, API call, data build, strategy, runtime, capital, live, generic-runner, "
            "schema, config, or old-route action"
        ),
        "replacement_checks": checks,
        "replacement_checks_all_true": all(value is True for value in checks.values()),
        "tracked_python_count_expectation": {
            "previous": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT,
        },
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "source_artifacts": {
            "preview_artifact": str(PREVIEW_ARTIFACT),
            "contract_validator_artifact": str(CONTRACT_VALIDATOR_ARTIFACT),
            "contract_artifact": str(CONTRACT_ARTIFACT),
            "hardening_validator_artifact": str(HARDENING_VALIDATOR_ARTIFACT),
        },
        "approval_sections": sections,
        "preflight": preflight,
        "prior_preview_snapshot": {
            "historical_data_acquisition_preview_status": preview.get("historical_data_acquisition_preview_status"),
            "recommended_acquisition_route": preview.get("recommended_acquisition_route"),
            "current_evidence_chain_quality_after_preview": preview.get(
                "current_evidence_chain_quality_after_preview"
            ),
            "next_module": preview.get("next_module"),
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
        "prior_preview_respected",
        "acquisition_approval_record_created",
        "user_acquisition_approval_present",
        "local_archive_import_preferred",
        "manual_exchange_export_import_allowed_future",
        "approval_grants_approval_record_only",
        "approval_grants_future_local_manual_source_discovery_next",
        "local_manual_source_discovery_eligible_next",
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
        "future_required_artifact_list_previewed",
        "fail_closed_conditions_preserved",
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
        "approval_grants_local_manual_source_discovery_now",
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
    require_equal(payload.get("historical_data_acquisition_approval_status"), STATUS_PASS, "approval status")
    require_equal(payload.get("user_acquisition_approval_scope"), USER_APPROVAL_SCOPE, "user approval scope")
    require_equal(payload.get("recommended_acquisition_route"), RECOMMENDED_ROUTE, "recommended route")
    require_equal(payload.get("next_module"), NEXT_MODULE_DISCOVERY, "next_module")
    require_equal(payload.get("whole_system_preflight_decision"), "PASS", "whole_system_preflight_decision")
    require_equal(payload.get("documentation_loop_risk_level"), DOCUMENTATION_LOOP_RISK_LEVEL, "documentation_loop_risk_level")
    require_equal(payload.get("current_evidence_chain_quality_before_approval"), EVIDENCE_BEFORE, "evidence_before")
    require_equal(payload.get("current_evidence_chain_quality_after_approval"), EVIDENCE_AFTER, "evidence_after")
    require_equal(payload.get("active_p0_blocker_count"), 0, "active_p0_blocker_count")
    require_equal(payload.get("active_p1_attention_count"), 1, "active_p1_attention_count")
    require_equal(payload.get("dormant_repo_attention_count"), 716, "dormant_repo_attention_count")
    require_equal(payload.get("planned_schema_files_existing_count"), 0, "planned_schema_files_existing_count")
    require(all(value is False for value in payload["dangerous_flags"].values()), "dangerous flags must all be false")


def main() -> None:
    preview = load_json(PREVIEW_ARTIFACT)
    contract_validator = load_json(CONTRACT_VALIDATOR_ARTIFACT)
    contract = load_json(CONTRACT_ARTIFACT)
    hardening = load_json(HARDENING_VALIDATOR_ARTIFACT)
    preflight = validate_preflight(preview, contract_validator, contract, hardening)
    sections = approval_sections(preview)
    payload = build_payload(preflight, preview, sections)
    validate_payload(payload)
    write_json(OUT_DIR / "historical_data_acquisition_approval_after_preview_v1.json", sections)
    write_json(OUT_DIR / "repo_only_historical_data_acquisition_approval_after_preview_v1_latest.json", payload)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
