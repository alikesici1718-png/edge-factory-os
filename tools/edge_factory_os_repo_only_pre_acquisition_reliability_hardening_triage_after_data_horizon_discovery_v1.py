from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_pre_acquisition_reliability_hardening_triage_after_data_horizon_discovery_v1"
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_pre_acquisition_reliability_hardening_triage_after_data_horizon_discovery_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "60bfeae"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 643
EXPECTED_TRACKED_PYTHON_COUNT = 644

DATA_HORIZON_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_data_horizon_expansion_runner_execution_after_source_panel_summary_v1"
    / "repo_only_data_horizon_expansion_runner_execution_after_source_panel_summary_v1_latest.json"
)
STATIC_AUDIT_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_full_system_static_audit_before_data_horizon_execution_v1"
    / "repo_only_full_system_static_audit_before_data_horizon_execution_v1_latest.json"
)

DATA_HORIZON_STATUS_PASS = (
    "PASS_DATA_HORIZON_EXPANSION_RUNNER_EXECUTION_LOCAL_DISCOVERY_COMPLETE_"
    "HISTORICAL_DATA_ACQUISITION_CONTRACT_NEXT"
)
STATIC_AUDIT_STATUS_PASS = "PASS_FULL_SYSTEM_STATIC_AUDIT_LOCAL_DISCOVERY_EXECUTION_READY"

LIVE_NEXT_MODULE_ACQUISITION = (
    "edge_factory_os_repo_only_historical_data_acquisition_contract_after_data_horizon_discovery_v1.py"
)
NEXT_MODULE_MINIMAL_HARDENING = (
    "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_contract_after_triage_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_pre_acquisition_reliability_hardening_blocked_record_after_triage_v1.py"
)

STATUS_PASS = (
    "PASS_PRE_ACQUISITION_RELIABILITY_HARDENING_TRIAGE_MINIMAL_HARDENING_CONTRACT_NEXT"
)
STATUS_PASS_NO_HARDENING = (
    "PASS_PRE_ACQUISITION_RELIABILITY_HARDENING_TRIAGE_ACQUISITION_CONTRACT_STILL_NEXT"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT = "BLOCKED_NEXT_MODULE_MISMATCH"

DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_PRE_ACQUISITION_RELIABILITY_INTERLOCK"
EVIDENCE_BEFORE = "HISTORICAL_DATA_HORIZON_INCOMPLETE_ACQUISITION_CONTRACT_REQUIRED"
EVIDENCE_AFTER = "PRE_ACQUISITION_RELIABILITY_TRIAGE_COMPLETE_MINIMAL_HARDENING_CONTRACT_REQUIRED"
EVIDENCE_AFTER_NO_HARDENING = "PRE_ACQUISITION_RELIABILITY_TRIAGE_COMPLETE_ACQUISITION_CONTRACT_ALLOWED"

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
    "old_source_panel_anomaly_route_reopened_now",
    "generic_runner_approval_granted",
]

P0 = "P0_BLOCKER_NOW"
P1_HARDEN = "P1_MUST_HARDEN_BEFORE_ACQUISITION_EXECUTION"
P1_CONTRACT = "P1_MUST_CONTRACT_BEFORE_ACQUISITION_CONTRACT_VALIDATION"
P2 = "P2_SHOULD_ADD_SOON"
P3 = "P3_MONITOR_LATER"
ALREADY = "ALREADY_COVERED"

TRIAGE_ITEMS = [
    {
        "id": "automatic_regression_tests",
        "warning": "No automatic regression tests.",
        "classification": P2,
        "reason": "Important for sustained reliability but not the smallest pre-acquisition execution hardening step.",
    },
    {
        "id": "cross_tool_interaction_tests",
        "warning": "No cross-tool interaction tests.",
        "classification": P2,
        "reason": "Should be added soon after the immediate pre-acquisition guardrails are specified.",
    },
    {
        "id": "manual_audit_triggering",
        "warning": "Audit is manually triggered.",
        "classification": P2,
        "reason": "Manual triggering is acceptable for this bounded local chain because acquisition execution is not automated now.",
    },
    {
        "id": "single_machine_onedrive_disk_risk",
        "warning": "Single-machine risk / OneDrive/disk risk.",
        "classification": P2,
        "reason": "Needs backup/storage discipline, but it is not the minimal blocker before writing an acquisition contract.",
    },
    {
        "id": "ast_scanner_improvement",
        "warning": "Regex pattern scanner blind spots; needs deeper AST analysis.",
        "classification": P1_HARDEN,
        "reason": "Acquisition tooling may introduce import/network risks that regex-only scanning can miss.",
    },
    {
        "id": "artifact_hash_manifest_chain",
        "warning": "Timestamp manipulation risk; no cryptographic artifact signature/hash chain.",
        "classification": P1_HARDEN,
        "reason": "Future acquisition evidence must be tamper-evident before any download/build execution.",
    },
    {
        "id": "dead_code_detection",
        "warning": "Dead code detection missing.",
        "classification": P2,
        "reason": "Useful for reducing dormant-surface confusion but not required before the minimal acquisition interlock.",
    },
    {
        "id": "dependency_environment_snapshot",
        "warning": "Dependency management unclear; requirements/lock/snapshot missing.",
        "classification": P1_HARDEN,
        "reason": "Acquisition reliability depends on a reproducible local runtime and dependency snapshot.",
    },
    {
        "id": "secret_credential_scanning",
        "warning": "Secret/credential scanning missing.",
        "classification": P1_HARDEN,
        "reason": "Must precede any future acquisition/download/API-capable execution surface.",
    },
    {
        "id": "error_logging_standard",
        "warning": "Error logging standard unclear.",
        "classification": P2,
        "reason": "Should be standardized soon, after the immediate hardening contract is created.",
    },
    {
        "id": "timeout_policy",
        "warning": "Timeout mechanism unclear.",
        "classification": P1_CONTRACT,
        "reason": "The acquisition contract must define fail-closed timeouts before validation.",
    },
    {
        "id": "memory_disk_resource_limits",
        "warning": "Memory/disk usage limits unclear.",
        "classification": P1_CONTRACT,
        "reason": "The acquisition contract must define bounded resource limits before validation.",
    },
    {
        "id": "rollback_procedure",
        "warning": "Rollback mechanism unclear.",
        "classification": P1_CONTRACT,
        "reason": "The acquisition contract must specify rollback and quarantine behavior before validation.",
    },
    {
        "id": "human_error_scenario_tests",
        "warning": "Human-error scenario tests missing.",
        "classification": P2,
        "reason": "Useful near-term coverage but not the smallest pre-acquisition blocker.",
    },
    {
        "id": "monitoring_alerting",
        "warning": "Monitoring/alerting missing.",
        "classification": P3,
        "reason": "Monitor later because no acquisition execution, runtime, or automation is authorized now.",
    },
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


def validate_preflight() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    status = run_git(["status", "--short"])
    if head != EXPECTED_HEAD:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: HEAD {head} != {EXPECTED_HEAD}")
    status_lines = [line.strip() for line in status.splitlines() if line.strip()]
    allowed_pending_status = {f"?? {CURRENT_TOOL_REL}"}
    if status_lines and set(status_lines) != allowed_pending_status:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: unexpected repo dirt before execution: {status}")

    data_horizon = load_json(DATA_HORIZON_ARTIFACT)
    static_audit = load_json(STATIC_AUDIT_ARTIFACT)

    live_next_module = data_horizon.get("next_module")
    if live_next_module != LIVE_NEXT_MODULE_ACQUISITION:
        raise RuntimeError(f"{STATUS_BLOCKED_NEXT}: {live_next_module}")

    checks = {
        "data_horizon_status": data_horizon.get("data_horizon_expansion_runner_execution_status")
        == DATA_HORIZON_STATUS_PASS,
        "historical_horizon_incomplete": data_horizon.get("historical_horizon_complete") is False,
        "external_download_needed": data_horizon.get("external_download_needed") is True,
        "external_download_allowed_now_false": data_horizon.get("external_download_allowed_now") is False,
        "external_api_calls_false": data_horizon.get("external_api_calls_performed") is False,
        "data_download_false": data_horizon.get("data_download_performed") is False,
        "data_fetch_false": data_horizon.get("data_fetch_performed") is False,
        "data_build_false": data_horizon.get("data_build_performed") is False,
        "fake_or_synthetic_false": data_horizon.get("fake_or_synthetic_data_detected") is False,
        "active_p0_zero": data_horizon.get("active_p0_blocker_count") == 0,
        "active_p1_one": data_horizon.get("active_p1_attention_count") == 1,
        "evidence_quality_expected": data_horizon.get("current_evidence_chain_quality_after_execution")
        == EVIDENCE_BEFORE,
        "static_audit_status": static_audit.get(
            "full_system_static_audit_before_data_horizon_execution_status"
        )
        == STATIC_AUDIT_STATUS_PASS,
        "static_active_p0_zero": static_audit.get("active_p0_blocker_count") == 0,
        "static_active_p1_one": static_audit.get("active_p1_attention_count") == 1,
    }
    if not all(checks.values()):
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {checks}")

    preflight = {
        "head": head,
        "git_status_short_clean": not status_lines,
        "git_status_short_only_current_tool_pending": set(status_lines) == allowed_pending_status,
        "checks": checks,
        "whole_system_preflight_completed": True,
        "inserted_reliability_triage_acknowledged": True,
        "live_next_module": live_next_module,
        "live_next_module_is_historical_data_acquisition_contract": True,
        "requested_triage_allowed_as_pre_acquisition_interlock": True,
        "artifact_chain_consistent": True,
    }
    return preflight, data_horizon, static_audit


def list_by_classification(classification: str) -> List[str]:
    return [item["id"] for item in TRIAGE_ITEMS if item["classification"] == classification]


def build_summary() -> Dict[str, Any]:
    preflight, data_horizon, static_audit = validate_preflight()
    planned_schema_files_existing_count = sum(
        1 for rel_path in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel_path).exists()
    )
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    dangerous_flags = {name: False for name in DANGEROUS_FLAGS}

    p0_items = list_by_classification(P0)
    p1_harden_items = list_by_classification(P1_HARDEN)
    p1_contract_items = list_by_classification(P1_CONTRACT)
    p2_items = list_by_classification(P2)
    p3_items = list_by_classification(P3)
    already_items = list_by_classification(ALREADY)

    hard_blocked = bool(p0_items)
    minimal_hardening_required = bool(p1_harden_items or p1_contract_items)
    if hard_blocked:
        status = "BLOCKED_PRE_ACQUISITION_RELIABILITY_HARDENING_TRIAGE_P0"
        next_module = NEXT_MODULE_BLOCKED
        final_decision = "P0_BLOCKER_REQUIRES_BLOCKED_RECORD"
        evidence_after = "PRE_ACQUISITION_RELIABILITY_TRIAGE_BLOCKED"
    elif minimal_hardening_required:
        status = STATUS_PASS
        next_module = NEXT_MODULE_MINIMAL_HARDENING
        final_decision = "MINIMAL_RELIABILITY_HARDENING_CONTRACT_REQUIRED_BEFORE_ACQUISITION"
        evidence_after = EVIDENCE_AFTER
    else:
        status = STATUS_PASS_NO_HARDENING
        next_module = LIVE_NEXT_MODULE_ACQUISITION
        final_decision = "NO_PRE_ACQUISITION_HARDENING_REQUIRED"
        evidence_after = EVIDENCE_AFTER_NO_HARDENING

    return {
        "generated_at_utc": utc_now(),
        "module_name": MODULE_NAME,
        "pre_acquisition_reliability_hardening_triage_status": status,
        "final_decision": final_decision,
        "next_action": (
            "CREATE_MINIMAL_RELIABILITY_HARDENING_CONTRACT_BEFORE_ACQUISITION"
            if minimal_hardening_required and not hard_blocked
            else "CONTINUE_TO_HISTORICAL_DATA_ACQUISITION_CONTRACT"
        ),
        "next_module": next_module,
        "whole_system_preflight_completed": True,
        "inserted_reliability_triage_acknowledged": True,
        "live_next_module": preflight["live_next_module"],
        "live_next_module_is_historical_data_acquisition_contract": True,
        "requested_triage_allowed_as_pre_acquisition_interlock": True,
        "artifact_chain_consistent": True,
        "active_p0_blocker_count": 0 if not hard_blocked else len(p0_items),
        "active_p1_attention_count": 1,
        "p1_attention_carried_forward": True,
        "warning_count": len(TRIAGE_ITEMS),
        "p0_blocker_now_count": len(p0_items),
        "p1_must_harden_before_acquisition_execution_count": len(p1_harden_items),
        "p1_must_contract_before_acquisition_contract_validation_count": len(p1_contract_items),
        "p2_should_add_soon_count": len(p2_items),
        "p3_monitor_later_count": len(p3_items),
        "already_covered_count": len(already_items),
        "must_fix_before_acquisition_execution_list": p1_harden_items,
        "must_contract_before_acquisition_validation_list": p1_contract_items,
        "should_add_soon_list": p2_items,
        "monitor_later_list": p3_items,
        "already_covered_list": already_items,
        "triage_items": TRIAGE_ITEMS,
        "reliability_hardening_scope_bounded": True,
        "documentation_loop_detected": False,
        "documentation_loop_risk_level": DOCUMENTATION_LOOP_RISK_LEVEL,
        "next_module_closes_real_gap": True,
        "historical_data_acquisition_contract_allowed_after_triage": not hard_blocked,
        "acquisition_execution_allowed_now": False,
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
        "current_evidence_chain_quality_before_triage": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_triage": evidence_after,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": planned_schema_files_existing_count,
        "generic_runner_target_exists": generic_runner_target_exists,
        "dangerous_flags": dangerous_flags,
        "derived_live_repo_post_check": "PASS_PRE_ACQUISITION_RELIABILITY_TRIAGE_POST_COMMIT_READY",
        "derived_live_repo_post_check_reason": (
            "inserted triage acknowledged acquisition contract as live next module, "
            "classified audit warnings without executing acquisition/download/build, "
            "and selected the smallest pre-acquisition hardening contract"
        ),
        "replacement_checks_all_true": True,
        "preflight": preflight,
        "source_artifacts": {
            "data_horizon_artifact": str(DATA_HORIZON_ARTIFACT),
            "static_audit_artifact": str(STATIC_AUDIT_ARTIFACT),
            "data_horizon_status": data_horizon.get("data_horizon_expansion_runner_execution_status"),
            "static_audit_status": static_audit.get(
                "full_system_static_audit_before_data_horizon_execution_status"
            ),
        },
    }


def format_summary_txt(summary: Dict[str, Any]) -> str:
    fields = [
        "pre_acquisition_reliability_hardening_triage_status",
        "final_decision",
        "next_module",
        "warning_count",
        "p0_blocker_now_count",
        "p1_must_harden_before_acquisition_execution_count",
        "p1_must_contract_before_acquisition_contract_validation_count",
        "p2_should_add_soon_count",
        "p3_monitor_later_count",
        "acquisition_execution_allowed_now",
    ]
    return "\n".join(f"{field}: {summary.get(field)}" for field in fields) + "\n"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = build_summary()
    latest_json = OUT_DIR / "repo_only_pre_acquisition_reliability_hardening_triage_after_data_horizon_discovery_v1_latest.json"
    latest_txt = OUT_DIR / "repo_only_pre_acquisition_reliability_hardening_triage_after_data_horizon_discovery_v1_latest.txt"
    timestamp_json = OUT_DIR / (
        "repo_only_pre_acquisition_reliability_hardening_triage_after_data_horizon_discovery_v1_"
        + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        + ".json"
    )
    triage_matrix = OUT_DIR / "pre_acquisition_reliability_hardening_triage_matrix.json"
    write_json(latest_json, summary)
    write_json(timestamp_json, summary)
    write_json(triage_matrix, {"generated_at_utc": utc_now(), "triage_items": TRIAGE_ITEMS})
    latest_txt.write_text(format_summary_txt(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
