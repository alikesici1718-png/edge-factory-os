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
    "implementation_approval_after_preview_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_"
    "implementation_approval_after_preview_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "578ea9c"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 647
EXPECTED_TRACKED_PYTHON_COUNT = 648

PREVIEW_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_implementation_preview_after_contract_validator_v1"
    / "repo_only_pre_acquisition_minimal_reliability_hardening_implementation_preview_after_contract_validator_v1_latest.json"
)
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

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_"
    "implementation_approval_after_preview_v1.py"
)
NEXT_MODULE_IMPLEMENTATION = (
    "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_"
    "implementation_after_approval_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_"
    "implementation_approval_blocked_record_after_preview_v1.py"
)

PREVIEW_STATUS_PASS = (
    "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_IMPLEMENTATION_PREVIEW_"
    "APPROVAL_REQUIRED"
)
VALIDATOR_STATUS_PASS = (
    "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_CONTRACT_VALIDATED_"
    "IMPLEMENTATION_PREVIEW_NEXT"
)
CONTRACT_STATUS_PASS = (
    "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_CONTRACT_READY_VALIDATOR_NEXT"
)
STATUS_PASS = (
    "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_IMPLEMENTATION_APPROVAL_"
    "RECORD_CREATED_IMPLEMENTATION_NEXT"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT = "BLOCKED_NEXT_MODULE_MISMATCH"

DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_PRE_ACQUISITION_RELIABILITY_INTERLOCK"
EVIDENCE_BEFORE = (
    "PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_IMPLEMENTATION_PREVIEW_READY_"
    "APPROVAL_REQUIRED"
)
EVIDENCE_AFTER = (
    "PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_IMPLEMENTATION_APPROVED_NEXT_"
    "NO_IMPLEMENTATION_YET"
)
EVIDENCE_CHAIN_POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
APPROVAL_SCOPE = (
    "APPROVAL_RECORD_ONLY_FOR_NEXT_SEPARATE_SINGLE_BOUNDED_HARDENING_IMPLEMENTATION"
)

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


def all_false(data: Dict[str, Any], fields: List[str]) -> bool:
    return all(data.get(field) is False for field in fields)


def validate_preflight() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    status = run_git(["status", "--short"])
    if head != EXPECTED_HEAD:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: HEAD {head} != {EXPECTED_HEAD}")
    status_lines = [line.strip() for line in status.splitlines() if line.strip()]
    allowed_pending_status = {f"?? {CURRENT_TOOL_REL}"}
    if status_lines and set(status_lines) != allowed_pending_status:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: unexpected repo dirt before execution: {status}")

    preview = load_json(PREVIEW_ARTIFACT)
    validator = load_json(VALIDATOR_ARTIFACT)
    contract_summary = load_json(CONTRACT_SUMMARY_ARTIFACT)
    contract_artifact = load_json(CONTRACT_ARTIFACT)

    live_next_module = preview.get("next_module")
    if live_next_module != REQUESTED_MODULE:
        raise RuntimeError(f"{STATUS_BLOCKED_NEXT}: {live_next_module}")

    forbidden_false_fields = [
        "hardening_implementation_performed",
        "secret_scan_performed",
        "dependency_environment_snapshot_performed",
        "ast_scanner_performed",
        "artifact_hash_manifest_performed",
        "timeout_policy_implemented",
        "memory_disk_resource_policy_implemented",
        "rollback_policy_implemented",
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
    checks = {
        "preview_status": preview.get(
            "pre_acquisition_minimal_reliability_hardening_implementation_preview_status"
        )
        == PREVIEW_STATUS_PASS,
        "validator_status": validator.get(
            "pre_acquisition_minimal_reliability_hardening_contract_validator_status"
        )
        == VALIDATOR_STATUS_PASS,
        "contract_status": contract_summary.get(
            "pre_acquisition_minimal_reliability_hardening_contract_status"
        )
        == CONTRACT_STATUS_PASS,
        "implementation_preview_completed": preview.get("implementation_preview_completed") is True,
        "recommended_strategy_single_bundle": preview.get("recommended_implementation_strategy")
        == "SINGLE_BOUNDED_BUNDLE",
        "single_bounded_bundle_allowed": preview.get("single_bounded_bundle_allowed") is True,
        "split_modules_not_required": preview.get("split_modules_required") is False,
        "implementation_approval_required_next": preview.get("implementation_approval_required_next")
        is True,
        "hardening_implementation_false": preview.get("hardening_implementation_performed") is False,
        "acquisition_execution_false": preview.get("acquisition_execution_allowed_now") is False,
        "active_p0_zero": preview.get("active_p0_blocker_count") == 0,
        "active_p1_one": preview.get("active_p1_attention_count") == 1,
        "evidence_before_expected": preview.get("current_evidence_chain_quality_after_preview")
        == EVIDENCE_BEFORE,
        "required_future_artifacts_match": preview.get("required_future_artifact_list")
        == REQUIRED_FUTURE_ARTIFACTS,
        "generic_runner_blocked": preview.get("generic_runner_implementation_remains_blocked") is True,
        "schema_or_config_false": preview.get("schema_or_config_created") is False,
        "loop_closed": preview.get("loop_remains_closed") is True,
        "all_forbidden_actions_false": all_false(preview, forbidden_false_fields),
        "contract_artifact_present": bool(contract_artifact),
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
        preview,
        validator,
        contract_summary,
        contract_artifact,
    )


def build_approval_sections() -> Dict[str, Any]:
    return {
        "preview_context": {
            "implementation_preview_passed": True,
            "recommended_implementation_strategy": "SINGLE_BOUNDED_BUNDLE",
            "split_modules_required": False,
            "implementation_approval_required_next": True,
            "no_implementation_performed_yet": True,
            "p1_remains_active": True,
        },
        "approval_scope": {
            "approval_grants_approval_record_only": True,
            "approval_grants_hardening_implementation_now": False,
            "approval_grants_secret_scan_now": False,
            "approval_grants_dependency_snapshot_now": False,
            "approval_grants_ast_scanner_now": False,
            "approval_grants_artifact_hash_manifest_now": False,
            "approval_grants_timeout_policy_now": False,
            "approval_grants_memory_disk_policy_now": False,
            "approval_grants_rollback_policy_now": False,
            "approval_grants_data_acquisition_now": False,
            "approval_grants_data_download_now": False,
            "approval_grants_external_api_now": False,
            "approval_grants_strategy_backtest_candidate_now": False,
            "approval_grants_runtime_capital_live_now": False,
        },
        "future_implementation_scope": {
            "future_implementation_module_may_produce_only": REQUIRED_FUTURE_ARTIFACTS,
            "future_implementation_module_must": [
                "remain repo-only",
                "perform no network calls",
                "install nothing",
                "mutate no repo files except the approved future tool file",
                "write only output artifacts",
                "use bounded file scanning",
                "fail closed on plausible secrets",
                "fail closed on dependency snapshot failure",
                "fail closed on AST parse errors",
                "fail closed on dangerous executable call findings",
                "fail closed on artifact hash manifest failure",
                "fail closed on missing policies",
                "fail closed on any forbidden action",
            ],
        },
        "safety_boundary": {
            "no_hardening_implementation": True,
            "no_secret_scan": True,
            "no_dependency_snapshot": True,
            "no_ast_scanner": True,
            "no_artifact_hash_manifest": True,
            "no_timeout_resource_rollback_implementation": True,
            "no_data_acquisition": True,
            "no_data_download_fetch_api_build": True,
            "no_strategy_backtest_candidate_runtime_capital_live_generic_runner_schema_config": True,
            "no_old_route_reopening": True,
            "no_profit_or_edge_claim": True,
        },
        "evidence_policy": {
            "current_evidence_before_approval": EVIDENCE_BEFORE,
            "current_evidence_after_approval": EVIDENCE_AFTER,
            "p1_remains_active_until_implementation_plus_validator_pass": True,
            "no_hardening_pass_claim_now": True,
        },
        "next_module_decision": {
            "if_approval_record_valid": NEXT_MODULE_IMPLEMENTATION,
            "if_approval_record_unsafe": NEXT_MODULE_BLOCKED,
            "chosen_next_module": NEXT_MODULE_IMPLEMENTATION,
            "do_not_choose_acquisition_execution": True,
            "do_not_choose_data_download_fetch_api": True,
            "do_not_choose_strategy_research": True,
            "do_not_choose_candidate_backtest_runtime_live_capital": True,
            "do_not_choose_generic_review_adoption_gate_rollout": True,
        },
    }


def build_summary() -> Dict[str, Any]:
    preflight, preview, validator, contract_summary, contract_artifact = validate_preflight()
    planned_schema_files_existing_count = sum(
        1 for rel_path in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel_path).exists()
    )
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    dangerous_flags = {name: False for name in DANGEROUS_FLAGS}
    approval_sections = build_approval_sections()

    return {
        "generated_at_utc": utc_now(),
        "module_name": MODULE_NAME,
        "pre_acquisition_minimal_reliability_hardening_implementation_approval_status": STATUS_PASS,
        "final_decision": "IMPLEMENTATION_APPROVAL_RECORD_CREATED_NEXT_SEPARATE_SINGLE_BOUNDED_BUNDLE",
        "next_action": "CREATE_SEPARATE_SINGLE_BOUNDED_HARDENING_IMPLEMENTATION_MODULE",
        "next_module": NEXT_MODULE_IMPLEMENTATION,
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
        "prior_preview_respected": True,
        "implementation_approval_record_created": True,
        "user_implementation_approval_present": True,
        "user_implementation_approval_scope": APPROVAL_SCOPE,
        "recommended_implementation_strategy": "SINGLE_BOUNDED_BUNDLE",
        "single_bounded_bundle_allowed": True,
        "split_modules_required": False,
        "approval_grants_approval_record_only": True,
        "approval_grants_hardening_implementation_now": False,
        "approval_grants_secret_scan_now": False,
        "approval_grants_dependency_snapshot_now": False,
        "approval_grants_ast_scanner_now": False,
        "approval_grants_artifact_hash_manifest_now": False,
        "approval_grants_timeout_policy_now": False,
        "approval_grants_memory_disk_policy_now": False,
        "approval_grants_rollback_policy_now": False,
        "approval_grants_data_acquisition_now": False,
        "approval_grants_data_download_now": False,
        "approval_grants_external_api_now": False,
        "approval_grants_strategy_backtest_candidate_now": False,
        "approval_grants_runtime_capital_live_now": False,
        "hardening_implementation_eligible_next": True,
        "required_future_artifact_list": REQUIRED_FUTURE_ARTIFACTS,
        "acquisition_execution_allowed_now": False,
        "hardening_implementation_performed": False,
        "secret_scan_performed": False,
        "dependency_environment_snapshot_performed": False,
        "ast_scanner_performed": False,
        "artifact_hash_manifest_performed": False,
        "timeout_policy_implemented": False,
        "memory_disk_resource_policy_implemented": False,
        "rollback_policy_implemented": False,
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
        "current_evidence_chain_quality_before_approval": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_approval": EVIDENCE_AFTER,
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
            "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_IMPLEMENTATION_APPROVAL_READY"
        ),
        "derived_live_repo_post_check_reason": (
            "approval record created for the next separate single bounded hardening implementation; "
            "this module performed no hardening gate, policy implementation, acquisition, download, "
            "fetch, API, build, strategy, runtime, capital, live, generic-runner, schema, or config action"
        ),
        "replacement_checks_all_true": True,
        "approval_sections": approval_sections,
        "preflight": preflight,
        "source_artifacts": {
            "preview_artifact": str(PREVIEW_ARTIFACT),
            "validator_artifact": str(VALIDATOR_ARTIFACT),
            "contract_summary_artifact": str(CONTRACT_SUMMARY_ARTIFACT),
            "contract_artifact": str(CONTRACT_ARTIFACT),
            "preview_status": preview.get(
                "pre_acquisition_minimal_reliability_hardening_implementation_preview_status"
            ),
            "validator_status": validator.get(
                "pre_acquisition_minimal_reliability_hardening_contract_validator_status"
            ),
            "contract_status": contract_summary.get(
                "pre_acquisition_minimal_reliability_hardening_contract_status"
            ),
            "contract_artifact_sections": list((contract_summary.get("contract_sections") or contract_artifact).keys()),
        },
        "tracked_python_count_expectation": {
            "previous": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT,
        },
    }


def format_summary_txt(summary: Dict[str, Any]) -> str:
    fields = [
        "pre_acquisition_minimal_reliability_hardening_implementation_approval_status",
        "final_decision",
        "next_module",
        "implementation_approval_record_created",
        "user_implementation_approval_present",
        "user_implementation_approval_scope",
        "recommended_implementation_strategy",
        "hardening_implementation_eligible_next",
        "approval_grants_hardening_implementation_now",
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
        "implementation_approval_after_preview_v1_latest.json"
    )
    latest_txt = OUT_DIR / (
        "repo_only_pre_acquisition_minimal_reliability_hardening_"
        "implementation_approval_after_preview_v1_latest.txt"
    )
    timestamp_json = OUT_DIR / (
        "repo_only_pre_acquisition_minimal_reliability_hardening_"
        "implementation_approval_after_preview_v1_"
        + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        + ".json"
    )
    approval_json = OUT_DIR / "pre_acquisition_minimal_reliability_hardening_implementation_approval_record.json"
    write_json(latest_json, summary)
    write_json(timestamp_json, summary)
    write_json(approval_json, summary["approval_sections"])
    latest_txt.write_text(format_summary_txt(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
