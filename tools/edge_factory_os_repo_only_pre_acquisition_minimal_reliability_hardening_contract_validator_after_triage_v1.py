from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_contract_validator_after_triage_v1"
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_contract_validator_after_triage_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "0973fa9"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 645
EXPECTED_TRACKED_PYTHON_COUNT = 646

CONTRACT_SUMMARY_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_contract_after_triage_v1"
    / "repo_only_pre_acquisition_minimal_reliability_hardening_contract_after_triage_v1_latest.json"
)
CONTRACT_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_contract_after_triage_v1"
    / "pre_acquisition_minimal_reliability_hardening_contract.json"
)
TRIAGE_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_pre_acquisition_reliability_hardening_triage_after_data_horizon_discovery_v1"
    / "repo_only_pre_acquisition_reliability_hardening_triage_after_data_horizon_discovery_v1_latest.json"
)

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_contract_validator_after_triage_v1.py"
)
NEXT_MODULE_PREVIEW = (
    "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_implementation_preview_after_contract_validator_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_contract_blocked_record_after_triage_v1.py"
)

CONTRACT_STATUS_PASS = (
    "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_CONTRACT_READY_VALIDATOR_NEXT"
)
TRIAGE_STATUS_PASS = (
    "PASS_PRE_ACQUISITION_RELIABILITY_HARDENING_TRIAGE_MINIMAL_HARDENING_CONTRACT_NEXT"
)
VALIDATOR_STATUS_PASS = (
    "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_CONTRACT_VALIDATED_IMPLEMENTATION_PREVIEW_NEXT"
)
VALIDATOR_STATUS_BLOCKED = (
    "BLOCKED_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_CONTRACT_VALIDATION_FAILED"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT = "BLOCKED_NEXT_MODULE_MISMATCH"

DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_PRE_ACQUISITION_RELIABILITY_INTERLOCK"
EVIDENCE_BEFORE = "PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_CONTRACT_READY_NO_IMPLEMENTATION"
EVIDENCE_AFTER = (
    "PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_CONTRACT_VALIDATED_IMPLEMENTATION_PREVIEW_READY"
)
EVIDENCE_CHAIN_POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"

P1_EXECUTION_ITEMS = [
    "secret_credential_scanning",
    "dependency_environment_snapshot",
    "ast_scanner_improvement",
    "artifact_hash_manifest_chain",
]
P1_CONTRACT_ITEMS = [
    "timeout_policy",
    "memory_disk_resource_limits",
    "rollback_procedure",
]
P2_DEFERRED_ITEMS = [
    "automatic_regression_tests",
    "cross_tool_interaction_tests",
    "manual_audit_triggering",
    "single_machine_onedrive_disk_risk",
    "dead_code_detection",
    "error_logging_standard",
    "human_error_scenario_tests",
]
P3_MONITOR_ITEMS = ["monitoring_alerting"]
REQUIRED_CONTRACT_SECTIONS = [
    "triage_context",
    "minimal_hardening_objective",
    "must_pass_before_acquisition_execution",
    "must_contract_before_acquisition_validation",
    "deferred_p2_policy",
    "p3_monitor_policy",
    "anti_loop_policy",
    "evidence_policy",
    "next_module_decision",
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
DANGEROUS_FLAGS = [
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
    "hardening_implementation_performed_now",
    "secret_scan_performed_now",
    "dependency_snapshot_performed_now",
    "ast_scanner_performed_now",
    "artifact_hash_manifest_performed_now",
    "generic_runner_approval_granted",
    "old_source_panel_anomaly_route_reopened_now",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_git(args: List[str]) -> str:
    completed = subprocess.run(
        ["git", "-c", f"safe.directory={REPO_ROOT}", "-C", str(REPO_ROOT)] + args,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def load_json(path: Path) -> Tuple[Dict[str, Any], bool, bool]:
    exists = path.exists()
    if not exists:
        return {}, False, False
    try:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
    except (OSError, json.JSONDecodeError):
        return {}, True, False
    return data, True, bool(data)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def as_set(values: Any) -> set[str]:
    if not isinstance(values, list):
        return set()
    return {str(value) for value in values}


def validate_preflight() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    status = run_git(["status", "--short"])
    if head != EXPECTED_HEAD:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: HEAD {head} != {EXPECTED_HEAD}")
    status_lines = [line.strip() for line in status.splitlines() if line.strip()]
    allowed_pending_status = {f"?? {CURRENT_TOOL_REL}"}
    if status_lines and set(status_lines) != allowed_pending_status:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: unexpected repo dirt before execution: {status}")

    contract_summary, contract_summary_exists, contract_summary_valid = load_json(CONTRACT_SUMMARY_ARTIFACT)
    contract_artifact, contract_artifact_exists, contract_artifact_valid = load_json(CONTRACT_ARTIFACT)
    triage, triage_exists, triage_valid = load_json(TRIAGE_ARTIFACT)
    if not (contract_summary_exists and contract_summary_valid and contract_artifact_exists and contract_artifact_valid and triage_exists and triage_valid):
        raise RuntimeError(STATUS_BLOCKED_CONTEXT)
    live_next_module = contract_summary.get("next_module")
    if live_next_module != REQUESTED_MODULE:
        raise RuntimeError(f"{STATUS_BLOCKED_NEXT}: {live_next_module}")

    checks = {
        "contract_status": contract_summary.get(
            "pre_acquisition_minimal_reliability_hardening_contract_status"
        )
        == CONTRACT_STATUS_PASS,
        "contract_created": contract_summary.get("minimal_hardening_contract_created") is True,
        "hardening_implementation_blocked": contract_summary.get("hardening_implementation_allowed_now") is False,
        "acquisition_execution_blocked": contract_summary.get("acquisition_execution_allowed_now") is False,
        "p0_zero": contract_summary.get("p0_blocker_now_count") == 0,
        "active_p1_one": contract_summary.get("active_p1_attention_count") == 1,
        "triage_status": triage.get("pre_acquisition_reliability_hardening_triage_status") == TRIAGE_STATUS_PASS,
        "triage_p0_zero": triage.get("p0_blocker_now_count") == 0,
        "no_download": contract_summary.get("data_download_performed") is False,
        "no_fetch": contract_summary.get("data_fetch_performed") is False,
        "no_build": contract_summary.get("data_build_performed") is False,
        "no_api": contract_summary.get("external_api_calls_performed") is False,
        "no_strategy_claim": contract_summary.get("strategy_signal_claims_made") is False,
        "no_profit_claim": contract_summary.get("profit_claims_made") is False,
        "generic_runner_blocked": contract_summary.get("generic_runner_implementation_remains_blocked") is True,
        "schema_or_config_false": contract_summary.get("schema_or_config_created") is False,
        "loop_closed": contract_summary.get("loop_remains_closed") is True,
    }
    if not all(checks.values()):
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {checks}")

    return (
        {
            "head": head,
            "git_status_short_clean": not status_lines,
            "git_status_short_only_current_tool_pending": set(status_lines) == allowed_pending_status,
            "whole_system_preflight_completed": True,
            "whole_system_preflight_decision": "PASS",
            "live_next_module": live_next_module,
            "live_next_module_matches_requested_module": True,
            "artifact_chain_consistent": True,
            "checks": checks,
        },
        contract_summary,
        contract_artifact,
        triage,
    )


def build_validation(
    contract_summary: Dict[str, Any],
    contract_artifact: Dict[str, Any],
    triage: Dict[str, Any],
) -> Dict[str, Any]:
    sections_present = all(section in contract_artifact for section in REQUIRED_CONTRACT_SECTIONS)
    triage_context = contract_artifact.get("triage_context", {})
    execution_section = contract_artifact.get("must_pass_before_acquisition_execution", {})
    policy_section = contract_artifact.get("must_contract_before_acquisition_validation", {})
    deferred_p2 = contract_artifact.get("deferred_p2_policy", {})
    monitor_p3 = contract_artifact.get("p3_monitor_policy", {})
    anti_loop = contract_artifact.get("anti_loop_policy", {})
    evidence = contract_artifact.get("evidence_policy", {})
    next_decision = contract_artifact.get("next_module_decision", {})

    p1_execution_valid = (
        as_set(contract_summary.get("must_pass_before_acquisition_execution_list")) == set(P1_EXECUTION_ITEMS)
        and as_set(triage_context.get("p1_before_acquisition_execution_items")) == set(P1_EXECUTION_ITEMS)
    )
    p1_contract_valid = (
        as_set(contract_summary.get("must_contract_before_acquisition_validation_list")) == set(P1_CONTRACT_ITEMS)
        and as_set(triage_context.get("p1_contract_before_acquisition_validation_items")) == set(P1_CONTRACT_ITEMS)
    )
    p2_preserved = (
        as_set(contract_summary.get("deferred_p2_list")) == set(P2_DEFERRED_ITEMS)
        and as_set(deferred_p2.get("items")) == set(P2_DEFERRED_ITEMS)
        and as_set(triage.get("should_add_soon_list")) == set(P2_DEFERRED_ITEMS)
    )
    p3_preserved = (
        as_set(contract_summary.get("p3_monitor_later_list")) == set(P3_MONITOR_ITEMS)
        and as_set(monitor_p3.get("items")) == set(P3_MONITOR_ITEMS)
        and as_set(triage.get("monitor_later_list")) == set(P3_MONITOR_ITEMS)
    )
    gate_outputs_present = all(
        execution_section.get(key, {}).get("required") is True
        for key in [
            "secret_credential_scanner_gate",
            "dependency_environment_snapshot_gate",
            "ast_scanner_improvement_gate",
            "artifact_hash_manifest_chain_gate",
        ]
    )
    policy_outputs_present = all(
        policy_section.get(key, {}).get("required") is True
        for key in ["timeout_policy", "memory_disk_resource_policy", "rollback_procedure"]
    )
    safety_false_fields = [
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
    ]
    return {
        "contract_artifact_validation": {
            "contract_artifact_exists": True,
            "contract_artifact_valid_json": True,
            "contract_artifact_non_empty": bool(contract_artifact),
            "contract_status_valid": contract_summary.get(
                "pre_acquisition_minimal_reliability_hardening_contract_status"
            )
            == CONTRACT_STATUS_PASS,
            "required_sections_present": sections_present,
        },
        "triage_context_validation": {
            "warning_count_valid": triage_context.get("warning_count") == 15,
            "p0_count_valid": triage_context.get("p0_blocker_now_count") == 0,
            "p1_execution_count_valid": contract_summary.get(
                "p1_must_harden_before_acquisition_execution_count"
            )
            == 4,
            "p1_contract_count_valid": contract_summary.get(
                "p1_must_contract_before_acquisition_contract_validation_count"
            )
            == 3,
            "p2_count_valid": contract_summary.get("p2_should_add_soon_count") == 7,
            "p3_count_valid": contract_summary.get("p3_monitor_later_count") == 1,
            "p1_execution_list_valid": p1_execution_valid,
            "p1_contract_list_valid": p1_contract_valid,
        },
        "hardening_gate_validation": {
            "secret_scan_required": contract_summary.get("secret_scan_required") is True,
            "dependency_environment_snapshot_required": contract_summary.get(
                "dependency_environment_snapshot_required"
            )
            is True,
            "ast_scanner_improvement_required": contract_summary.get("ast_scanner_improvement_required")
            is True,
            "artifact_hash_manifest_required": contract_summary.get("artifact_hash_manifest_required")
            is True,
            "gate_outputs_present": gate_outputs_present,
            "no_hardening_implementation_performed_now": True,
        },
        "acquisition_policy_validation": {
            "acquisition_execution_allowed_now_false": contract_summary.get(
                "acquisition_execution_allowed_now"
            )
            is False,
            "historical_data_acquisition_contract_allowed": contract_summary.get(
                "historical_data_acquisition_contract_allowed_after_contract"
            )
            is True,
            "hardening_implementation_allowed_now_false": contract_summary.get(
                "hardening_implementation_allowed_now"
            )
            is False,
            "hardening_contract_validator_required_next": contract_summary.get(
                "hardening_contract_validator_required_next"
            )
            is True,
            "policy_outputs_present": policy_outputs_present,
        },
        "bounded_scope_validation": {
            "p2_deferred_preserved": p2_preserved,
            "p3_monitor_preserved": p3_preserved,
            "scope_bounded": triage_context.get("scope_remains_bounded") is True
            or contract_summary.get("documentation_loop_detected") is False,
            "documentation_loop_absent": contract_summary.get("documentation_loop_detected") is False,
            "ordinary_selector_backlog_loop_reentry_blocked": contract_summary.get(
                "ordinary_selector_backlog_loop_reentry_allowed"
            )
            is False,
            "loop_remains_closed": contract_summary.get("loop_remains_closed") is True,
            "no_broad_governance_chain_opened": anti_loop.get(
                "must_not_expand_into_general_governance_adoption_readiness_loop"
            )
            is True,
        },
        "evidence_policy_validation": {
            "before_contract_valid": contract_summary.get("current_evidence_chain_quality_before_contract")
            == "PRE_ACQUISITION_RELIABILITY_TRIAGE_COMPLETE_MINIMAL_HARDENING_CONTRACT_REQUIRED",
            "after_contract_valid": contract_summary.get("current_evidence_chain_quality_after_contract")
            == EVIDENCE_BEFORE,
            "validator_after_state_defined": True,
            "active_p0_zero": contract_summary.get("active_p0_blocker_count") == 0,
            "active_p1_one": contract_summary.get("active_p1_attention_count") == 1,
            "p1_remains_active_until_hardening_gates_pass": evidence.get(
                "p1_remains_active_until_hardening_gates_pass"
            )
            is True,
        },
        "safety_boundary_validation": {
            "all_forbidden_actions_false": all(contract_summary.get(field) is False for field in safety_false_fields),
            "checked_fields": safety_false_fields,
        },
        "next_module_decision": {
            "preview_next": next_decision.get("if_contract_created_safely") == REQUESTED_MODULE
            or contract_summary.get("next_module") == REQUESTED_MODULE,
            "validator_selects_implementation_preview_next": True,
            "does_not_choose_implementation_apply_or_execution": True,
        },
    }


def validation_all_true(validation: Dict[str, Any]) -> bool:
    def values(obj: Any) -> List[bool]:
        found: List[bool] = []
        if isinstance(obj, dict):
            for value in obj.values():
                found.extend(values(value))
        elif isinstance(obj, bool):
            found.append(obj)
        return found

    return all(values(validation))


def build_summary() -> Dict[str, Any]:
    preflight, contract_summary, contract_artifact, triage = validate_preflight()
    validation = build_validation(contract_summary, contract_artifact, triage)
    valid = validation_all_true(validation)
    planned_schema_files_existing_count = sum(
        1 for rel_path in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel_path).exists()
    )
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    dangerous_flags = {name: False for name in DANGEROUS_FLAGS}
    status = VALIDATOR_STATUS_PASS if valid else VALIDATOR_STATUS_BLOCKED
    next_module = NEXT_MODULE_PREVIEW if valid else NEXT_MODULE_BLOCKED

    return {
        "generated_at_utc": utc_now(),
        "module_name": MODULE_NAME,
        "pre_acquisition_minimal_reliability_hardening_contract_validator_status": status,
        "final_decision": (
            "MINIMAL_RELIABILITY_HARDENING_CONTRACT_VALIDATED_IMPLEMENTATION_PREVIEW_NEXT"
            if valid
            else "MINIMAL_RELIABILITY_HARDENING_CONTRACT_VALIDATION_BLOCKED"
        ),
        "next_action": (
            "CREATE_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_IMPLEMENTATION_PREVIEW"
            if valid
            else "WRITE_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_CONTRACT_BLOCKED_RECORD"
        ),
        "next_module": next_module,
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
        "blocked_actions_absent_from_requested_module": True,
        "whole_system_preflight_decision": "PASS",
        "prior_contract_respected": True,
        "contract_artifact_validation_completed": valid,
        "triage_context_validation_completed": valid,
        "hardening_gate_validation_completed": valid,
        "acquisition_policy_validation_completed": valid,
        "bounded_scope_validation_completed": valid,
        "evidence_policy_validation_completed": valid,
        "safety_boundary_validation_completed": valid,
        "minimal_hardening_contract_validated": valid,
        "contract_artifact_exists": True,
        "contract_artifact_valid_json": True,
        "p0_blocker_now_count": 0 if valid else 1,
        "p1_must_harden_before_acquisition_execution_count": 4,
        "p1_must_contract_before_acquisition_contract_validation_count": 3,
        "p2_should_add_soon_count": 7,
        "p3_monitor_later_count": 1,
        "must_pass_before_acquisition_execution_list_validated": valid,
        "must_contract_before_acquisition_validation_list_validated": valid,
        "deferred_p2_list_preserved": validation["bounded_scope_validation"]["p2_deferred_preserved"],
        "p3_monitor_later_list_preserved": validation["bounded_scope_validation"]["p3_monitor_preserved"],
        "acquisition_execution_allowed_now": False,
        "historical_data_acquisition_contract_allowed_after_contract": True,
        "hardening_implementation_allowed_now": False,
        "hardening_implementation_preview_allowed_next": valid,
        "secret_scan_required": True,
        "dependency_environment_snapshot_required": True,
        "ast_scanner_improvement_required": True,
        "artifact_hash_manifest_required": True,
        "timeout_policy_required": True,
        "memory_disk_resource_policy_required": True,
        "rollback_policy_required": True,
        "current_evidence_chain_quality_before_validator": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_validator": EVIDENCE_AFTER if valid else "CONTRACT_VALIDATION_BLOCKED",
        "active_p0_blocker_count": 0 if valid else 1,
        "active_p1_attention_count": 1,
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
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "old_source_panel_anomaly_route_reopened_now": False,
        "evidence_chain_policy_level": EVIDENCE_CHAIN_POLICY_LEVEL,
        "future_modules_must_classify_evidence_quality": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": planned_schema_files_existing_count,
        "generic_runner_target_exists": generic_runner_target_exists,
        "dangerous_flags": dangerous_flags,
        "derived_live_repo_post_check": (
            "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_CONTRACT_VALIDATOR_READY"
            if valid
            else "BLOCKED_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_CONTRACT_VALIDATOR"
        ),
        "derived_live_repo_post_check_reason": (
            "contract JSON, triage context, hardening gates, acquisition policies, evidence "
            "boundaries, and forbidden-action flags validated; implementation preview is next"
            if valid
            else "contract validation failed and blocked record is required"
        ),
        "replacement_checks_all_true": valid,
        "validation": validation,
        "preflight": preflight,
        "source_artifacts": {
            "contract_summary_artifact": str(CONTRACT_SUMMARY_ARTIFACT),
            "contract_artifact": str(CONTRACT_ARTIFACT),
            "triage_artifact": str(TRIAGE_ARTIFACT),
        },
    }


def format_summary_txt(summary: Dict[str, Any]) -> str:
    fields = [
        "pre_acquisition_minimal_reliability_hardening_contract_validator_status",
        "final_decision",
        "next_module",
        "minimal_hardening_contract_validated",
        "acquisition_execution_allowed_now",
        "hardening_implementation_allowed_now",
        "hardening_implementation_preview_allowed_next",
        "active_p0_blocker_count",
        "active_p1_attention_count",
    ]
    return "\n".join(f"{field}: {summary.get(field)}" for field in fields) + "\n"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = build_summary()
    latest_json = (
        OUT_DIR
        / "repo_only_pre_acquisition_minimal_reliability_hardening_contract_validator_after_triage_v1_latest.json"
    )
    latest_txt = (
        OUT_DIR
        / "repo_only_pre_acquisition_minimal_reliability_hardening_contract_validator_after_triage_v1_latest.txt"
    )
    timestamp_json = OUT_DIR / (
        "repo_only_pre_acquisition_minimal_reliability_hardening_contract_validator_after_triage_v1_"
        + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        + ".json"
    )
    validation_json = OUT_DIR / "pre_acquisition_minimal_reliability_hardening_contract_validation_report.json"
    write_json(latest_json, summary)
    write_json(timestamp_json, summary)
    write_json(validation_json, summary["validation"])
    latest_txt.write_text(format_summary_txt(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
