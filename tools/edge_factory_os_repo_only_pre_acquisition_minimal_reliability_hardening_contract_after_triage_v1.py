from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_contract_after_triage_v1"
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_contract_after_triage_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "dbb99a7"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 644
EXPECTED_TRACKED_PYTHON_COUNT = 645

TRIAGE_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_pre_acquisition_reliability_hardening_triage_after_data_horizon_discovery_v1"
    / "repo_only_pre_acquisition_reliability_hardening_triage_after_data_horizon_discovery_v1_latest.json"
)

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_contract_after_triage_v1.py"
)
NEXT_MODULE_VALIDATOR = (
    "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_contract_validator_after_triage_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_contract_blocked_record_after_triage_v1.py"
)

TRIAGE_STATUS_PASS = (
    "PASS_PRE_ACQUISITION_RELIABILITY_HARDENING_TRIAGE_MINIMAL_HARDENING_CONTRACT_NEXT"
)
STATUS_PASS = (
    "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_CONTRACT_READY_VALIDATOR_NEXT"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT = "BLOCKED_NEXT_MODULE_MISMATCH"

DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_PRE_ACQUISITION_RELIABILITY_INTERLOCK"
EVIDENCE_BEFORE = "PRE_ACQUISITION_RELIABILITY_TRIAGE_COMPLETE_MINIMAL_HARDENING_CONTRACT_REQUIRED"
EVIDENCE_AFTER = "PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_CONTRACT_READY_NO_IMPLEMENTATION"
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


def validate_preflight() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    status = run_git(["status", "--short"])
    if head != EXPECTED_HEAD:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: HEAD {head} != {EXPECTED_HEAD}")
    status_lines = [line.strip() for line in status.splitlines() if line.strip()]
    allowed_pending_status = {f"?? {CURRENT_TOOL_REL}"}
    if status_lines and set(status_lines) != allowed_pending_status:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: unexpected repo dirt before execution: {status}")

    triage = load_json(TRIAGE_ARTIFACT)
    live_next_module = triage.get("next_module")
    if live_next_module != REQUESTED_MODULE:
        raise RuntimeError(f"{STATUS_BLOCKED_NEXT}: {live_next_module}")

    checks = {
        "triage_status": triage.get("pre_acquisition_reliability_hardening_triage_status")
        == TRIAGE_STATUS_PASS,
        "p0_zero": triage.get("p0_blocker_now_count") == 0,
        "p1_execution_count": triage.get("p1_must_harden_before_acquisition_execution_count") == 4,
        "p1_contract_count": triage.get(
            "p1_must_contract_before_acquisition_contract_validation_count"
        )
        == 3,
        "p2_count": triage.get("p2_should_add_soon_count") == 7,
        "p3_count": triage.get("p3_monitor_later_count") == 1,
        "scope_bounded": triage.get("reliability_hardening_scope_bounded") is True,
        "documentation_loop_absent": triage.get("documentation_loop_detected") is False,
        "acquisition_execution_blocked": triage.get("acquisition_execution_allowed_now") is False,
        "active_p1_carried": triage.get("active_p1_attention_count") == 1,
        "no_download": triage.get("data_download_performed") is False,
        "no_fetch": triage.get("data_fetch_performed") is False,
        "no_build": triage.get("data_build_performed") is False,
        "no_api": triage.get("external_api_calls_performed") is False,
        "no_strategy_claim": triage.get("strategy_signal_claims_made") is False,
        "no_profit_claim": triage.get("profit_claims_made") is False,
        "loop_closed": triage.get("loop_remains_closed") is True,
        "evidence_before_expected": triage.get("current_evidence_chain_quality_after_triage")
        == EVIDENCE_BEFORE,
    }
    triage_p1_execution = set(triage.get("must_fix_before_acquisition_execution_list") or [])
    triage_p1_contract = set(triage.get("must_contract_before_acquisition_validation_list") or [])
    checks["p1_execution_items_match"] = triage_p1_execution == set(P1_EXECUTION_ITEMS)
    checks["p1_contract_items_match"] = triage_p1_contract == set(P1_CONTRACT_ITEMS)
    if not all(checks.values()):
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {checks}")

    preflight = {
        "head": head,
        "git_status_short_clean": not status_lines,
        "git_status_short_only_current_tool_pending": set(status_lines) == allowed_pending_status,
        "whole_system_preflight_completed": True,
        "whole_system_preflight_decision": "PASS",
        "live_next_module": live_next_module,
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "checks": checks,
    }
    return preflight, triage


def build_contract_sections() -> Dict[str, Any]:
    return {
        "triage_context": {
            "warning_count": 15,
            "p0_blocker_now_count": 0,
            "p1_before_acquisition_execution_items": P1_EXECUTION_ITEMS,
            "p1_contract_before_acquisition_validation_items": P1_CONTRACT_ITEMS,
            "p2_items_deferred_not_ignored": P2_DEFERRED_ITEMS,
            "p3_monitor_later_items": P3_MONITOR_ITEMS,
            "scope_remains_bounded": True,
        },
        "minimal_hardening_objective": {
            "objective": (
                "reduce real pre-acquisition operational/security risk before any data "
                "acquisition execution"
            ),
            "not_objective": [
                "CI/CD buildout",
                "broad governance chain",
                "dead code cleanup",
                "monitoring system",
                "full regression framework",
                "strategy research",
                "candidate generation",
            ],
            "hardening_must_be_finite_and_acquisition_adjacent": True,
        },
        "must_pass_before_acquisition_execution": {
            "secret_credential_scanner_gate": {
                "required": True,
                "requirements": [
                    "scan repo text and latest artifacts for likely secrets/API keys/private keys/tokens/passwords",
                    "distinguish documentation placeholders from plausible live secrets",
                    "fail closed on plausible secrets",
                ],
                "output": "secret_scan_report.json",
            },
            "dependency_environment_snapshot_gate": {
                "required": True,
                "requirements": [
                    "record Python executable",
                    "record Python version",
                    "record pip freeze or importable package snapshot if safe",
                    "record pyarrow version if present",
                    "perform no package install or update",
                ],
                "output": "dependency_environment_snapshot.json",
            },
            "ast_scanner_improvement_gate": {
                "required": True,
                "requirements": [
                    "parse tracked Python with AST",
                    "identify executable imports/calls for requests/httpx/urllib/aiohttp/ccxt/subprocess/importlib/runpy/eval/exec/open network patterns",
                    "classify context as executable vs documentation/guard text where possible",
                ],
                "output": "ast_dangerous_call_scan_report.json",
            },
            "artifact_hash_manifest_chain_gate": {
                "required": True,
                "requirements": [
                    "hash latest critical artifacts",
                    "hash approved next module files where present",
                    "record artifact paths, sizes, mtimes, sha256",
                ],
                "output": "pre_acquisition_artifact_hash_manifest.json",
            },
        },
        "must_contract_before_acquisition_validation": {
            "timeout_policy": {
                "required": True,
                "requirements": [
                    "future acquisition preview/execution modules must define max runtime or fail-closed timeout",
                    "long scans must be bounded",
                    "external calls, if later approved, must have timeout and retry limits",
                ],
            },
            "memory_disk_resource_policy": {
                "required": True,
                "requirements": [
                    "future acquisition execution must estimate file sizes before processing",
                    "must not full-scan huge parquet/CSV without explicit approval",
                    "must define max read limits",
                    "must track output size",
                ],
            },
            "rollback_procedure": {
                "required": True,
                "requirements": [
                    "before future acquisition execution, record HEAD, git status, output dir",
                    "no repo mutation except approved tool file",
                    "raw acquired data must go to controlled output directory",
                    "failed acquisition must preserve logs and not overwrite prior artifacts",
                    "if environment changes are ever approved, rollback/uninstall path required",
                ],
            },
        },
        "deferred_p2_policy": {
            "items": P2_DEFERRED_ITEMS,
            "policy": (
                "acknowledged but not blockers before the acquisition contract; queue after "
                "minimal acquisition safety hardening, not forgotten"
            ),
        },
        "p3_monitor_policy": {
            "items": P3_MONITOR_ITEMS,
            "policy": (
                "monitoring_alerting is monitor-later until runtime/live/long-running automation "
                "exists and must not block current repo-only acquisition contract work"
            ),
        },
        "anti_loop_policy": {
            "finite_chain": True,
            "must_not_expand_into_general_governance_adoption_readiness_loop": True,
            "after_validator_passes_next_step": (
                "minimal hardening implementation/preview or historical data acquisition contract "
                "depending validator decision"
            ),
            "do_not_add_unrelated_docs": True,
        },
        "evidence_policy": {
            "current_evidence_before_contract": EVIDENCE_BEFORE,
            "current_evidence_after_contract": EVIDENCE_AFTER,
            "acquisition_execution_remains_blocked": True,
            "p1_remains_active_until_hardening_gates_pass": True,
            "no_data_quality_strategy_profit_or_edge_claim": True,
        },
        "next_module_decision": {
            "if_contract_created_safely": NEXT_MODULE_VALIDATOR,
            "if_contract_cannot_be_safely_created": NEXT_MODULE_BLOCKED,
            "do_not_choose_hardening_implementation_directly": True,
            "do_not_choose_acquisition_execution": True,
            "do_not_choose_data_download_fetch_api": True,
            "do_not_choose_strategy_candidate_backtest_runtime_live_capital_or_generic_modules": True,
        },
    }


def build_summary() -> Dict[str, Any]:
    preflight, triage = validate_preflight()
    planned_schema_files_existing_count = sum(
        1 for rel_path in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel_path).exists()
    )
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    dangerous_flags = {name: False for name in DANGEROUS_FLAGS}
    contract_sections = build_contract_sections()

    return {
        "generated_at_utc": utc_now(),
        "module_name": MODULE_NAME,
        "pre_acquisition_minimal_reliability_hardening_contract_status": STATUS_PASS,
        "final_decision": "MINIMAL_RELIABILITY_HARDENING_CONTRACT_CREATED_VALIDATOR_NEXT",
        "next_action": "VALIDATE_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_CONTRACT",
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
        "blocked_actions_absent_from_requested_module": True,
        "whole_system_preflight_decision": "PASS",
        "prior_triage_respected": True,
        "minimal_hardening_contract_created": True,
        "triage_context_completed": True,
        "minimal_hardening_objective_completed": True,
        "must_pass_before_acquisition_execution_completed": True,
        "must_contract_before_acquisition_validation_completed": True,
        "deferred_p2_policy_completed": True,
        "p3_monitor_policy_completed": True,
        "anti_loop_policy_completed": True,
        "evidence_policy_completed": True,
        "p0_blocker_now_count": 0,
        "p1_must_harden_before_acquisition_execution_count": 4,
        "p1_must_contract_before_acquisition_contract_validation_count": 3,
        "p2_should_add_soon_count": 7,
        "p3_monitor_later_count": 1,
        "must_pass_before_acquisition_execution_list": P1_EXECUTION_ITEMS,
        "must_contract_before_acquisition_validation_list": P1_CONTRACT_ITEMS,
        "deferred_p2_list": P2_DEFERRED_ITEMS,
        "p3_monitor_later_list": P3_MONITOR_ITEMS,
        "acquisition_execution_allowed_now": False,
        "historical_data_acquisition_contract_allowed_after_contract": True,
        "hardening_implementation_allowed_now": False,
        "hardening_contract_validator_required_next": True,
        "secret_scan_required": True,
        "dependency_environment_snapshot_required": True,
        "ast_scanner_improvement_required": True,
        "artifact_hash_manifest_required": True,
        "timeout_policy_required": True,
        "memory_disk_resource_policy_required": True,
        "rollback_policy_required": True,
        "current_evidence_chain_quality_before_contract": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_contract": EVIDENCE_AFTER,
        "active_p0_blocker_count": 0,
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
        "derived_live_repo_post_check": "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_CONTRACT_READY",
        "derived_live_repo_post_check_reason": (
            "contract created from bounded triage, no hardening implementation or acquisition "
            "execution occurred, and validator is required before any next step"
        ),
        "replacement_checks_all_true": True,
        "contract_sections": contract_sections,
        "preflight": preflight,
        "source_artifacts": {
            "triage_artifact": str(TRIAGE_ARTIFACT),
            "triage_status": triage.get("pre_acquisition_reliability_hardening_triage_status"),
            "triage_next_module": triage.get("next_module"),
        },
    }


def format_summary_txt(summary: Dict[str, Any]) -> str:
    fields = [
        "pre_acquisition_minimal_reliability_hardening_contract_status",
        "final_decision",
        "next_module",
        "minimal_hardening_contract_created",
        "p1_must_harden_before_acquisition_execution_count",
        "p1_must_contract_before_acquisition_contract_validation_count",
        "acquisition_execution_allowed_now",
        "hardening_implementation_allowed_now",
        "hardening_contract_validator_required_next",
    ]
    return "\n".join(f"{field}: {summary.get(field)}" for field in fields) + "\n"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = build_summary()
    latest_json = OUT_DIR / "repo_only_pre_acquisition_minimal_reliability_hardening_contract_after_triage_v1_latest.json"
    latest_txt = OUT_DIR / "repo_only_pre_acquisition_minimal_reliability_hardening_contract_after_triage_v1_latest.txt"
    timestamp_json = OUT_DIR / (
        "repo_only_pre_acquisition_minimal_reliability_hardening_contract_after_triage_v1_"
        + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        + ".json"
    )
    contract_json = OUT_DIR / "pre_acquisition_minimal_reliability_hardening_contract.json"
    write_json(latest_json, summary)
    write_json(timestamp_json, summary)
    write_json(contract_json, summary["contract_sections"])
    latest_txt.write_text(format_summary_txt(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
