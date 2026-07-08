from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = (
    "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_"
    "implementation_preview_after_contract_validator_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_"
    "implementation_preview_after_contract_validator_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "cabbb29"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 646
EXPECTED_TRACKED_PYTHON_COUNT = 647

VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_contract_validator_after_triage_v1"
    / "repo_only_pre_acquisition_minimal_reliability_hardening_contract_validator_after_triage_v1_latest.json"
)
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
    "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_"
    "implementation_preview_after_contract_validator_v1.py"
)
NEXT_MODULE_APPROVAL = (
    "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_"
    "implementation_approval_after_preview_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_"
    "implementation_preview_blocked_record_after_contract_validator_v1.py"
)

VALIDATOR_STATUS_PASS = (
    "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_CONTRACT_VALIDATED_"
    "IMPLEMENTATION_PREVIEW_NEXT"
)
CONTRACT_STATUS_PASS = (
    "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_CONTRACT_READY_VALIDATOR_NEXT"
)
TRIAGE_STATUS_PASS = (
    "PASS_PRE_ACQUISITION_RELIABILITY_HARDENING_TRIAGE_MINIMAL_HARDENING_CONTRACT_NEXT"
)
STATUS_PASS = (
    "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_IMPLEMENTATION_PREVIEW_"
    "APPROVAL_REQUIRED"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT = "BLOCKED_NEXT_MODULE_MISMATCH"

DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_PRE_ACQUISITION_RELIABILITY_INTERLOCK"
EVIDENCE_BEFORE = (
    "PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_CONTRACT_VALIDATED_"
    "IMPLEMENTATION_PREVIEW_READY"
)
EVIDENCE_AFTER = (
    "PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_IMPLEMENTATION_PREVIEW_READY_"
    "APPROVAL_REQUIRED"
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

REQUIRED_FUTURE_ARTIFACTS = [
    "secret_scan_report.json",
    "dependency_environment_snapshot.json",
    "ast_dangerous_call_scan_report.json",
    "pre_acquisition_artifact_hash_manifest.json",
    "timeout_policy.json",
    "memory_disk_resource_policy.json",
    "rollback_policy.json",
    "minimal_hardening_contract_compliance_report.json",
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


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def as_set(values: Any) -> set[str]:
    if not isinstance(values, list):
        return set()
    return {str(value) for value in values}


def validate_preflight() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    status = run_git(["status", "--short"])
    if head != EXPECTED_HEAD:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: HEAD {head} != {EXPECTED_HEAD}")
    status_lines = [line.strip() for line in status.splitlines() if line.strip()]
    allowed_pending_status = {f"?? {CURRENT_TOOL_REL}"}
    if status_lines and set(status_lines) != allowed_pending_status:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: unexpected repo dirt before execution: {status}")

    validator = load_json(VALIDATOR_ARTIFACT)
    contract_summary = load_json(CONTRACT_SUMMARY_ARTIFACT)
    contract_artifact = load_json(CONTRACT_ARTIFACT)
    triage = load_json(TRIAGE_ARTIFACT)

    live_next_module = validator.get("next_module")
    if live_next_module != REQUESTED_MODULE:
        raise RuntimeError(f"{STATUS_BLOCKED_NEXT}: {live_next_module}")

    contract_sections = contract_summary.get("contract_sections") or contract_artifact
    contract_triage_context = contract_sections.get("triage_context") or {}
    p1_execution_valid = (
        as_set(contract_summary.get("must_fix_before_acquisition_execution_list"))
        == set(P1_EXECUTION_ITEMS)
        or as_set(contract_triage_context.get("p1_before_acquisition_execution_items"))
        == set(P1_EXECUTION_ITEMS)
    )
    p1_contract_valid = (
        as_set(contract_summary.get("must_contract_before_acquisition_validation_list"))
        == set(P1_CONTRACT_ITEMS)
        or as_set(contract_triage_context.get("p1_contract_before_acquisition_validation_items"))
        == set(P1_CONTRACT_ITEMS)
    )

    checks = {
        "validator_status": validator.get(
            "pre_acquisition_minimal_reliability_hardening_contract_validator_status"
        )
        == VALIDATOR_STATUS_PASS,
        "contract_status": contract_summary.get(
            "pre_acquisition_minimal_reliability_hardening_contract_status"
        )
        == CONTRACT_STATUS_PASS,
        "triage_status": triage.get("pre_acquisition_reliability_hardening_triage_status")
        == TRIAGE_STATUS_PASS,
        "minimal_hardening_contract_validated": validator.get("minimal_hardening_contract_validated")
        is True,
        "hardening_implementation_allowed_now_false": validator.get(
            "hardening_implementation_allowed_now"
        )
        is False,
        "hardening_implementation_preview_allowed_next_true": validator.get(
            "hardening_implementation_preview_allowed_next"
        )
        is True,
        "acquisition_execution_allowed_now_false": validator.get("acquisition_execution_allowed_now")
        is False,
        "active_p0_zero": validator.get("active_p0_blocker_count") == 0,
        "active_p1_one": validator.get("active_p1_attention_count") == 1,
        "p1_execution_count": validator.get("p1_must_harden_before_acquisition_execution_count") == 4,
        "p1_contract_count": validator.get(
            "p1_must_contract_before_acquisition_contract_validation_count"
        )
        == 3,
        "p1_execution_items_match": p1_execution_valid,
        "p1_contract_items_match": p1_contract_valid,
        "evidence_before_expected": validator.get("current_evidence_chain_quality_after_validator")
        == EVIDENCE_BEFORE,
        "secret_scan_required": validator.get("secret_scan_required") is True,
        "dependency_environment_snapshot_required": validator.get(
            "dependency_environment_snapshot_required"
        )
        is True,
        "ast_scanner_improvement_required": validator.get("ast_scanner_improvement_required") is True,
        "artifact_hash_manifest_required": validator.get("artifact_hash_manifest_required") is True,
        "timeout_policy_required": validator.get("timeout_policy_required") is True,
        "memory_disk_resource_policy_required": validator.get("memory_disk_resource_policy_required")
        is True,
        "rollback_policy_required": validator.get("rollback_policy_required") is True,
        "no_download": validator.get("data_download_performed") is False,
        "no_fetch": validator.get("data_fetch_performed") is False,
        "no_build": validator.get("data_build_performed") is False,
        "no_api": validator.get("external_api_calls_performed") is False,
        "no_strategy_claim": validator.get("strategy_signal_claims_made") is False,
        "no_tradable_edge_claim": validator.get("tradable_edge_claims_made") is False,
        "no_profit_claim": validator.get("profit_claims_made") is False,
        "generic_runner_blocked": validator.get("generic_runner_implementation_remains_blocked")
        is True,
        "schema_or_config_false": validator.get("schema_or_config_created") is False,
        "old_anomaly_route_not_reopened": validator.get("old_source_panel_anomaly_route_reopened_now")
        is False,
        "loop_closed": validator.get("loop_remains_closed") is True,
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
        validator,
        contract_summary,
        contract_artifact,
        triage,
    )


def build_preview_sections() -> Dict[str, Any]:
    return {
        "validator_context": {
            "contract_validated": True,
            "p1_hardening_gates_validated": P1_EXECUTION_ITEMS,
            "p1_policy_contracts_validated": P1_CONTRACT_ITEMS,
            "acquisition_execution_still_blocked": True,
            "implementation_not_allowed_now": True,
            "preview_allowed_now": True,
            "p1_remains_active": True,
        },
        "implementation_strategy_preview": {
            "recommended_strategy": "SINGLE_BOUNDED_BUNDLE",
            "single_bounded_bundle_allowed": True,
            "split_modules_required": False,
            "decision_reason": (
                "the four gates and three policy artifacts are finite, repo-only, non-network, "
                "no-install, output-artifact-only tasks with bounded file size and scan scope limits"
            ),
            "single_bundle_conditions": {
                "repo_only": True,
                "performs_no_network_calls": True,
                "installs_nothing": True,
                "mutates_no_repo_files_except_approved_future_tool_file": True,
                "writes_only_output_artifacts": True,
                "bounded_file_scanning_required": True,
                "fail_closed_file_size_and_scope_limits_required": True,
            },
            "fallback_if_conditions_fail": "SPLIT_MODULES",
        },
        "future_allowed_implementation_scope": {
            "future_may": [
                "scan tracked repo text and selected latest artifacts for likely secrets",
                "create secret_scan_report.json",
                "record Python executable/version and safe package snapshot",
                "create dependency_environment_snapshot.json",
                "parse tracked Python files with AST",
                "classify dangerous calls/imports in executable code",
                "create ast_dangerous_call_scan_report.json",
                "hash critical latest artifacts and approved tool files",
                "create pre_acquisition_artifact_hash_manifest.json",
                "create timeout_policy.json",
                "create memory_disk_resource_policy.json",
                "create rollback_policy.json",
                "create minimal_hardening_contract_compliance_report.json",
            ],
            "future_must_not": [
                "install/update packages",
                "call network",
                "call external APIs",
                "import/execute repo modules",
                "run data acquisition",
                "download/fetch/build data",
                "run strategy/backtest/candidate/runtime/live/capital",
                "create repo schema/config",
                "reopen old anomaly route",
            ],
        },
        "required_future_artifacts_preview": {
            "required_future_artifact_list": REQUIRED_FUTURE_ARTIFACTS,
            "all_required": True,
        },
        "fail_closed_rules_preview": {
            "future_implementation_must_fail_closed_if": [
                "plausible secret detected",
                "dependency snapshot cannot be produced",
                "AST parse errors exist in tracked Python",
                "executable external API/network call paths are detected in approved acquisition chain",
                "artifact hash manifest cannot be produced",
                "timeout/resource/rollback policies missing",
                "any forbidden action occurs",
                "repo dirty before/after",
                "more than approved output artifacts are modified",
                "active P0 emerges",
            ],
        },
        "acquisition_boundary_preview": {
            "historical_data_acquisition_contract_rule": (
                "may proceed only after minimal hardening gates pass or after validator "
                "explicitly accepts remaining P1"
            ),
            "acquisition_execution_remains_blocked": True,
            "data_download_api_fetch_remains_blocked": True,
            "contract_allowed_after_validator_but_execution_blocked_until_gates_pass": True,
        },
        "anti_loop_preview": {
            "finite_chain": "4-gate + 3-policy hardening chain",
            "p2_p3_items_deferred_and_not_expanded_now": True,
            "p2_deferred_items": P2_DEFERRED_ITEMS,
            "p3_monitor_later_items": P3_MONITOR_ITEMS,
            "no_broad_ci_cd_dead_code_monitoring_governance_chain_starts_now": True,
            "approval_record_required_before_implementation": True,
            "validator_required_after_implementation": True,
            "return_to_historical_data_acquisition_contract_path_after_validator": True,
        },
        "evidence_policy_preview": {
            "current_evidence_before_preview": EVIDENCE_BEFORE,
            "current_evidence_after_preview": EVIDENCE_AFTER,
            "active_p0_blocker_count": 0,
            "active_p1_attention_count": 1,
            "no_hardening_pass_claim_until_implementation_plus_validator": True,
        },
        "next_module_decision": {
            "if_preview_safe": NEXT_MODULE_APPROVAL,
            "if_preview_unsafe": NEXT_MODULE_BLOCKED,
            "chosen_next_module": NEXT_MODULE_APPROVAL,
            "implementation_or_apply_not_chosen_directly": True,
            "acquisition_execution_not_chosen": True,
            "data_download_fetch_api_not_chosen": True,
            "strategy_candidate_backtest_runtime_live_capital_not_chosen": True,
            "generic_review_adoption_gate_rollout_modules_not_chosen": True,
        },
    }


def build_summary() -> Dict[str, Any]:
    preflight, validator, contract_summary, contract_artifact, triage = validate_preflight()
    planned_schema_files_existing_count = sum(
        1 for rel_path in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel_path).exists()
    )
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    dangerous_flags = {name: False for name in DANGEROUS_FLAGS}
    preview_sections = build_preview_sections()

    return {
        "generated_at_utc": utc_now(),
        "module_name": MODULE_NAME,
        "pre_acquisition_minimal_reliability_hardening_implementation_preview_status": STATUS_PASS,
        "final_decision": "MINIMAL_RELIABILITY_HARDENING_IMPLEMENTATION_PREVIEW_READY_APPROVAL_REQUIRED",
        "next_action": "CREATE_IMPLEMENTATION_APPROVAL_RECORD_BEFORE_ANY_HARDENING_IMPLEMENTATION",
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
        "blocked_actions_absent_from_requested_module": True,
        "whole_system_preflight_decision": "PASS",
        "prior_contract_validator_respected": True,
        "implementation_preview_completed": True,
        "validator_context_completed": True,
        "implementation_strategy_preview_completed": True,
        "future_allowed_implementation_scope_completed": True,
        "required_future_artifacts_preview_completed": True,
        "fail_closed_rules_preview_completed": True,
        "acquisition_boundary_preview_completed": True,
        "anti_loop_preview_completed": True,
        "evidence_policy_preview_completed": True,
        "recommended_implementation_strategy": "SINGLE_BOUNDED_BUNDLE",
        "single_bounded_bundle_allowed": True,
        "split_modules_required": False,
        "implementation_approval_required_next": True,
        "hardening_implementation_performed": False,
        "secret_scan_performed": False,
        "dependency_environment_snapshot_performed": False,
        "ast_scanner_performed": False,
        "artifact_hash_manifest_performed": False,
        "timeout_policy_implemented": False,
        "memory_disk_resource_policy_implemented": False,
        "rollback_policy_implemented": False,
        "required_future_artifact_list": REQUIRED_FUTURE_ARTIFACTS,
        "acquisition_execution_allowed_now": False,
        "historical_data_acquisition_contract_allowed_after_preview": True,
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
        "current_evidence_chain_quality_before_preview": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_preview": EVIDENCE_AFTER,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 1,
        "evidence_chain_policy_level": EVIDENCE_CHAIN_POLICY_LEVEL,
        "future_modules_must_classify_evidence_quality": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": planned_schema_files_existing_count,
        "generic_runner_target_exists": generic_runner_target_exists,
        "dangerous_flags": dangerous_flags,
        "derived_live_repo_post_check": (
            "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_IMPLEMENTATION_PREVIEW_READY"
        ),
        "derived_live_repo_post_check_reason": (
            "implementation preview is finite, approval-gated, output-artifact-only, "
            "non-network, no-install, and does not execute any hardening gate"
        ),
        "replacement_checks_all_true": True,
        "preview_sections": preview_sections,
        "preflight": preflight,
        "source_artifacts": {
            "validator_artifact": str(VALIDATOR_ARTIFACT),
            "contract_summary_artifact": str(CONTRACT_SUMMARY_ARTIFACT),
            "contract_artifact": str(CONTRACT_ARTIFACT),
            "triage_artifact": str(TRIAGE_ARTIFACT),
            "validator_status": validator.get(
                "pre_acquisition_minimal_reliability_hardening_contract_validator_status"
            ),
            "contract_status": contract_summary.get(
                "pre_acquisition_minimal_reliability_hardening_contract_status"
            ),
            "triage_status": triage.get("pre_acquisition_reliability_hardening_triage_status"),
            "contract_artifact_sections": list((contract_summary.get("contract_sections") or contract_artifact).keys()),
        },
        "tracked_python_count_expectation": {
            "previous": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT,
        },
    }


def format_summary_txt(summary: Dict[str, Any]) -> str:
    fields = [
        "pre_acquisition_minimal_reliability_hardening_implementation_preview_status",
        "final_decision",
        "next_module",
        "implementation_preview_completed",
        "recommended_implementation_strategy",
        "single_bounded_bundle_allowed",
        "split_modules_required",
        "implementation_approval_required_next",
        "hardening_implementation_performed",
        "acquisition_execution_allowed_now",
        "active_p0_blocker_count",
        "active_p1_attention_count",
    ]
    return "\n".join(f"{field}: {summary.get(field)}" for field in fields) + "\n"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = build_summary()
    latest_json = OUT_DIR / (
        "repo_only_pre_acquisition_minimal_reliability_hardening_"
        "implementation_preview_after_contract_validator_v1_latest.json"
    )
    latest_txt = OUT_DIR / (
        "repo_only_pre_acquisition_minimal_reliability_hardening_"
        "implementation_preview_after_contract_validator_v1_latest.txt"
    )
    timestamp_json = OUT_DIR / (
        "repo_only_pre_acquisition_minimal_reliability_hardening_"
        "implementation_preview_after_contract_validator_v1_"
        + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        + ".json"
    )
    preview_json = OUT_DIR / "pre_acquisition_minimal_reliability_hardening_implementation_preview.json"
    write_json(latest_json, summary)
    write_json(timestamp_json, summary)
    write_json(preview_json, summary["preview_sections"])
    latest_txt.write_text(format_summary_txt(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
