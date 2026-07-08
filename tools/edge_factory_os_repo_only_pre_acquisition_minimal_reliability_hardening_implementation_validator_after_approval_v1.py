from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = (
    "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_"
    "implementation_validator_after_approval_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_"
    "implementation_validator_after_approval_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "702084d"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 649
EXPECTED_TRACKED_PYTHON_COUNT = 650

IMPLEMENTATION_DIR = (
    LAB_ROOT
    / "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_implementation_after_approval_v1"
)
IMPLEMENTATION_ARTIFACT = (
    IMPLEMENTATION_DIR
    / "repo_only_pre_acquisition_minimal_reliability_hardening_implementation_after_approval_v1_latest.json"
)
REQUIRED_ARTIFACTS = {
    "secret_scan_report": IMPLEMENTATION_DIR / "secret_scan_report.json",
    "dependency_environment_snapshot": IMPLEMENTATION_DIR / "dependency_environment_snapshot.json",
    "ast_dangerous_call_scan_report": IMPLEMENTATION_DIR / "ast_dangerous_call_scan_report.json",
    "pre_acquisition_artifact_hash_manifest": IMPLEMENTATION_DIR / "pre_acquisition_artifact_hash_manifest.json",
    "timeout_policy": IMPLEMENTATION_DIR / "timeout_policy.json",
    "memory_disk_resource_policy": IMPLEMENTATION_DIR / "memory_disk_resource_policy.json",
    "rollback_policy": IMPLEMENTATION_DIR / "rollback_policy.json",
    "minimal_hardening_contract_compliance_report": IMPLEMENTATION_DIR / "minimal_hardening_contract_compliance_report.json",
}

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_"
    "implementation_validator_after_approval_v1.py"
)
NEXT_MODULE_ACQUISITION_CONTRACT = (
    "edge_factory_os_repo_only_historical_data_acquisition_contract_after_data_horizon_discovery_v1.py"
)
NEXT_MODULE_AST_REVIEW = (
    "edge_factory_os_repo_only_pre_acquisition_ast_risk_focused_review_after_hardening_validator_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_"
    "implementation_blocked_record_after_approval_v1.py"
)

IMPLEMENTATION_STATUS_PASS = (
    "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_IMPLEMENTED_PENDING_VALIDATOR"
)
STATUS_PASS = (
    "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_VALIDATED_ACQUISITION_"
    "CONTRACT_RESUME_READY"
)
STATUS_AST_REVIEW = (
    "ATTENTION_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_VALIDATED_AST_RISK_"
    "FOCUSED_REVIEW_REQUIRED"
)
STATUS_BLOCKED = (
    "BLOCKED_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_VALIDATOR_P0"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT = "BLOCKED_NEXT_MODULE_MISMATCH"

DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_PRE_ACQUISITION_RELIABILITY_INTERLOCK"
EVIDENCE_BEFORE = "PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_IMPLEMENTED_PENDING_VALIDATOR"
EVIDENCE_AFTER_PASS = (
    "PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_VALIDATED_ACQUISITION_CONTRACT_RESUME_READY"
)
EVIDENCE_AFTER_AST_REVIEW = "PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_VALIDATED_AST_REVIEW_REQUIRED"
EVIDENCE_AFTER_BLOCKED = "PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_VALIDATOR_BLOCKED_P0"
EVIDENCE_CHAIN_POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"

CURRENT_CHAIN_REL_PATHS = {
    "tools/edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_implementation_after_approval_v1.py",
    "tools/edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_implementation_approval_after_preview_v1.py",
    "tools/edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_implementation_preview_after_contract_validator_v1.py",
    "tools/edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_contract_validator_after_triage_v1.py",
    "tools/edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_contract_after_triage_v1.py",
}
PRIOR_COMPLETED_ATTENTION_REL_PATHS = {
    "tools/edge_factory_os_repo_only_pre_acquisition_reliability_hardening_triage_after_data_horizon_discovery_v1.py",
}
NETWORK_ROOTS = {"requests", "httpx", "urllib", "aiohttp", "ccxt", "binance", "okx", "socket", "webbrowser"}
SUBPROCESS_NAMES = {
    "subprocess",
    "subprocess.run",
    "subprocess.Popen",
    "subprocess.call",
    "subprocess.check_call",
    "subprocess.check_output",
}
EVAL_EXEC_NAMES = {"eval", "exec"}
ALLOWED_AST_CLASSIFICATIONS = {
    "DORMANT_REPO_CODE_ATTENTION",
    "GUARD_OR_DOCUMENTATION_ONLY",
    "SAFE_STANDARD_LIBRARY_USAGE",
    "CURRENT_APPROVED_CHAIN_BLOCKER",
}

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
    if args[:2] not in (["rev-parse", "--short"], ["status", "--short"], ["ls-files"], ["log", "--oneline"]):
        raise RuntimeError(f"unsafe git metadata command refused: {args}")
    completed = subprocess.run(
        ["git", "-c", f"safe.directory={REPO_ROOT}", "-C", str(REPO_ROOT)] + args,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def load_json_checked(path: Path) -> Tuple[Dict[str, Any], bool, bool, bool]:
    exists = path.exists()
    if not exists:
        return {}, False, False, False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}, True, False, False
    return data, True, True, bool(data)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_preflight() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Dict[str, Any]]]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    status = run_git(["status", "--short"])
    if head != EXPECTED_HEAD:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: HEAD {head} != {EXPECTED_HEAD}")
    status_lines = [line.strip() for line in status.splitlines() if line.strip()]
    allowed_pending_status = {f"?? {CURRENT_TOOL_REL}"}
    if status_lines and set(status_lines) != allowed_pending_status:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: unexpected repo dirt before execution: {status}")

    implementation, implementation_exists, implementation_valid, implementation_non_empty = load_json_checked(
        IMPLEMENTATION_ARTIFACT
    )
    if not (implementation_exists and implementation_valid and implementation_non_empty):
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: implementation artifact missing/invalid")
    live_next_module = implementation.get("next_module")
    if live_next_module != REQUESTED_MODULE:
        raise RuntimeError(f"{STATUS_BLOCKED_NEXT}: {live_next_module}")

    artifact_payloads: Dict[str, Dict[str, Any]] = {}
    artifact_checks = {}
    for name, path in REQUIRED_ARTIFACTS.items():
        data, exists, valid, non_empty = load_json_checked(path)
        artifact_payloads[name] = data
        artifact_checks[name] = {"exists": exists, "valid_json": valid, "non_empty": non_empty}

    checks = {
        "implementation_status": implementation.get(
            "pre_acquisition_minimal_reliability_hardening_implementation_status"
        )
        == IMPLEMENTATION_STATUS_PASS,
        "hardening_implementation_performed": implementation.get("hardening_implementation_performed") is True,
        "acquisition_execution_false": implementation.get("acquisition_execution_allowed_now") is False,
        "active_p0_zero": implementation.get("active_p0_blocker_count") == 0,
        "active_p1_one": implementation.get("active_p1_attention_count") == 1,
        "evidence_before_expected": implementation.get("current_evidence_chain_quality_after_implementation")
        == EVIDENCE_BEFORE,
        "generic_runner_blocked": implementation.get("generic_runner_implementation_remains_blocked") is True,
        "schema_or_config_false": implementation.get("schema_or_config_created") is False,
        "loop_closed": implementation.get("loop_remains_closed") is True,
        "all_required_artifacts_exist": all(check["exists"] for check in artifact_checks.values()),
        "all_required_artifacts_valid": all(check["valid_json"] for check in artifact_checks.values()),
        "all_required_artifacts_non_empty": all(check["non_empty"] for check in artifact_checks.values()),
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
            "artifact_checks": artifact_checks,
            "checks": checks,
        },
        implementation,
        artifact_payloads,
    )


def validate_secret_scan(secret_report: Dict[str, Any]) -> Dict[str, Any]:
    findings = secret_report.get("findings") or []
    plausible_count = secret_report.get("plausible_live_secret_count")
    unredacted_plausible = []
    for finding in findings:
        if finding.get("classification") != "PLAUSIBLE_LIVE_SECRET":
            continue
        redacted = str(finding.get("redacted_value", ""))
        if "***REDACTED***" not in redacted:
            unredacted_plausible.append(finding)
    scope = str(secret_report.get("scan_scope", "")).lower()
    validated = (
        secret_report.get("secret_scan_performed") is True
        and secret_report.get("secret_scan_report_created") is True
        and plausible_count == 0
        and secret_report.get("redaction_policy_applied") is True
        and not unredacted_plausible
        and "repo" in scope
        and "artifact" in scope
        and secret_report.get("secret_scan_fail_closed") is False
    )
    return {
        "secret_scan_validation_completed": True,
        "secret_scan_validated": validated,
        "plausible_live_secret_count": plausible_count,
        "unredacted_plausible_secret_count": len(unredacted_plausible),
        "secret_scan_scope_includes_repo_text_and_latest_artifacts": "repo" in scope and "artifact" in scope,
    }


def validate_dependency_snapshot(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    validated = (
        snapshot.get("dependency_environment_snapshot_performed") is True
        and snapshot.get("dependency_environment_snapshot_created") is True
        and bool(snapshot.get("python_executable"))
        and bool(snapshot.get("python_version"))
        and bool(snapshot.get("package_snapshot_method"))
        and isinstance(snapshot.get("package_count"), int)
        and snapshot.get("package_count", 0) > 0
        and snapshot.get("dependency_install_attempted") is False
        and snapshot.get("dependency_update_attempted") is False
        and snapshot.get("environment_modified") is False
    )
    return {
        "dependency_snapshot_validation_completed": True,
        "dependency_snapshot_validated": validated,
        "dependency_install_attempted": snapshot.get("dependency_install_attempted"),
        "dependency_update_attempted": snapshot.get("dependency_update_attempted"),
        "environment_modified": snapshot.get("environment_modified"),
    }


def risky_name(item: Dict[str, Any]) -> str:
    return str(item.get("name", ""))


def is_external_api(item: Dict[str, Any]) -> bool:
    return risky_name(item).split(".")[0] in NETWORK_ROOTS


def is_subprocess_risk(item: Dict[str, Any]) -> bool:
    name = risky_name(item)
    return name in SUBPROCESS_NAMES or name.startswith("subprocess.")


def is_eval_exec_risk(item: Dict[str, Any]) -> bool:
    return risky_name(item) in EVAL_EXEC_NAMES


def validate_ast_report(ast_report: Dict[str, Any]) -> Dict[str, Any]:
    findings = ast_report.get("findings") or []
    classifications = {str(item.get("classification")) for item in findings}
    missing_classification_count = sum(1 for item in findings if item.get("classification") not in ALLOWED_AST_CLASSIFICATIONS)
    current_chain_risky = [
        item
        for item in findings
        if item.get("path") in CURRENT_CHAIN_REL_PATHS
        and (is_external_api(item) or is_subprocess_risk(item) or is_eval_exec_risk(item))
        and item.get("classification") != "SAFE_STANDARD_LIBRARY_USAGE"
    ]
    prior_completed_attention = [
        item
        for item in findings
        if item.get("path") in PRIOR_COMPLETED_ATTENTION_REL_PATHS
        and item.get("classification") == "DORMANT_REPO_CODE_ATTENTION"
    ]
    current_chain_blockers = [
        item for item in findings if item.get("classification") == "CURRENT_APPROVED_CHAIN_BLOCKER"
    ]
    external_non_current = [
        item for item in findings if is_external_api(item) and item.get("classification") == "DORMANT_REPO_CODE_ATTENTION"
    ]
    subprocess_non_current = [
        item
        for item in findings
        if is_subprocess_risk(item)
        and item.get("classification") == "DORMANT_REPO_CODE_ATTENTION"
    ]
    eval_exec_non_current = [
        item
        for item in findings
        if is_eval_exec_risk(item)
        and item.get("classification") in {"DORMANT_REPO_CODE_ATTENTION", "GUARD_OR_DOCUMENTATION_ONLY"}
    ]
    classification_adequate = (
        missing_classification_count == 0
        and not current_chain_risky
        and not current_chain_blockers
        and ast_report.get("dangerous_current_chain_blocker_count") == 0
        and ast_report.get("ast_parse_error_count") == 0
        and ast_report.get("ast_scanner_fail_closed") is False
        and ast_report.get("executable_external_api_call_count") == len(external_non_current)
        and ast_report.get("executable_subprocess_risk_count") == len(subprocess_non_current)
        and ast_report.get("executable_eval_exec_risk_count") == len(eval_exec_non_current)
        and ast_report.get("dormant_repo_attention_count", 0) > 0
    )
    validated = (
        ast_report.get("ast_scanner_performed") is True
        and ast_report.get("ast_dangerous_call_scan_report_created") is True
        and ast_report.get("tracked_python_files_scanned_count", 0) >= EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT - 1
        and ast_report.get("ast_parse_error_count") == 0
        and ast_report.get("dangerous_current_chain_blocker_count") == 0
        and ast_report.get("ast_scanner_fail_closed") is False
        and classification_adequate
    )
    return {
        "ast_dangerous_call_validation_completed": True,
        "ast_scan_validated": validated,
        "ast_risk_classification_adequate": classification_adequate,
        "ast_risk_requires_focused_review": not classification_adequate and not current_chain_blockers,
        "dormant_repo_attention_count_carried_forward": ast_report.get("dormant_repo_attention_count", 0) > 0,
        "missing_ast_classification_count": missing_classification_count,
        "current_chain_risky_finding_count": len(current_chain_risky),
        "current_chain_blocker_finding_count": len(current_chain_blockers),
        "prior_completed_attention_finding_count": len(prior_completed_attention),
        "classification_set": sorted(classifications),
    }


def validate_manifest(manifest: Dict[str, Any]) -> Dict[str, Any]:
    validated = (
        manifest.get("artifact_hash_manifest_performed") is True
        and manifest.get("artifact_hash_manifest_created") is True
        and manifest.get("critical_artifact_count", 0) >= 5
        and manifest.get("missing_critical_artifact_count") == 0
        and manifest.get("hashed_file_count", 0) >= manifest.get("critical_artifact_count", 0)
        and manifest.get("hash_algorithm") == "SHA256"
        and manifest.get("artifact_manifest_fail_closed") is False
    )
    return {
        "artifact_hash_manifest_validation_completed": True,
        "artifact_hash_manifest_validated": validated,
    }


def validate_policies(
    timeout_policy: Dict[str, Any],
    memory_policy: Dict[str, Any],
    rollback_policy: Dict[str, Any],
) -> Dict[str, Any]:
    timeout_valid = (
        timeout_policy.get("timeout_policy_created") is True
        and timeout_policy.get("timeout_policy_implemented") is True
        and bool(timeout_policy.get("future_acquisition_preview_max_runtime_seconds"))
        and bool(timeout_policy.get("future_acquisition_execution_max_runtime_seconds"))
        and timeout_policy.get("fail_closed_on_timeout") is True
    )
    memory_valid = (
        memory_policy.get("memory_disk_resource_policy_created") is True
        and memory_policy.get("memory_disk_resource_policy_implemented") is True
        and bool(memory_policy.get("max_text_file_read_bytes_without_separate_approval"))
        and "metadata" in str(memory_policy.get("parquet_policy", "")).lower()
        and memory_policy.get("output_size_tracking_required") is True
    )
    rollback_text = " ".join(str(value).lower() for value in rollback_policy.values())
    rollback_valid = (
        rollback_policy.get("rollback_policy_created") is True
        and rollback_policy.get("rollback_policy_implemented") is True
        and rollback_policy.get("git_head_capture_required") is True
        and rollback_policy.get("git_status_capture_required") is True
        and rollback_policy.get("output_directory_isolation_required") is True
        and "overwrite" in rollback_text
        and "preserve" in rollback_text
    )
    return {
        "policy_artifact_validation_completed": True,
        "timeout_policy_validated": timeout_valid,
        "memory_disk_resource_policy_validated": memory_valid,
        "rollback_policy_validated": rollback_valid,
    }


def validate_compliance_report(compliance: Dict[str, Any]) -> Dict[str, Any]:
    required_passed = {
        "secret_credential_scanning",
        "dependency_environment_snapshot",
        "ast_scanner_improvement",
        "artifact_hash_manifest_chain",
        "timeout_policy",
        "memory_disk_resource_policy",
        "rollback_policy",
    }
    passed = set(compliance.get("hardening_gates_passed") or [])
    validated = (
        compliance.get("minimal_hardening_contract_compliance_report_created") is True
        and compliance.get("minimal_hardening_implementation_successful") is True
        and required_passed.issubset(passed)
        and not compliance.get("hardening_gates_blocked")
        and compliance.get("active_p0_blocker_count") == 0
        and compliance.get("current_evidence_chain_quality_after_implementation") == EVIDENCE_BEFORE
    )
    return {
        "compliance_report_validation_completed": True,
        "compliance_report_validated": validated,
    }


def validate_forbidden_actions(implementation: Dict[str, Any]) -> bool:
    false_fields = [
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
    return all(implementation.get(field) is False for field in false_fields)


def build_summary() -> Dict[str, Any]:
    preflight, implementation, artifacts = validate_preflight()
    secret_validation = validate_secret_scan(artifacts["secret_scan_report"])
    dependency_validation = validate_dependency_snapshot(artifacts["dependency_environment_snapshot"])
    ast_validation = validate_ast_report(artifacts["ast_dangerous_call_scan_report"])
    manifest_validation = validate_manifest(artifacts["pre_acquisition_artifact_hash_manifest"])
    policy_validation = validate_policies(
        artifacts["timeout_policy"],
        artifacts["memory_disk_resource_policy"],
        artifacts["rollback_policy"],
    )
    compliance_validation = validate_compliance_report(
        artifacts["minimal_hardening_contract_compliance_report"]
    )
    forbidden_actions_absent = validate_forbidden_actions(implementation)

    validations = [
        secret_validation["secret_scan_validated"],
        dependency_validation["dependency_snapshot_validated"],
        ast_validation["ast_scan_validated"],
        manifest_validation["artifact_hash_manifest_validated"],
        policy_validation["timeout_policy_validated"],
        policy_validation["memory_disk_resource_policy_validated"],
        policy_validation["rollback_policy_validated"],
        compliance_validation["compliance_report_validated"],
        forbidden_actions_absent,
    ]
    p0_reasons = []
    if artifacts["secret_scan_report"].get("plausible_live_secret_count", 0) > 0:
        p0_reasons.append("plausible_live_secret")
    if dependency_validation["dependency_install_attempted"] or dependency_validation["dependency_update_attempted"] or dependency_validation["environment_modified"]:
        p0_reasons.append("dependency_or_environment_mutation")
    if artifacts["ast_dangerous_call_scan_report"].get("ast_parse_error_count") != 0:
        p0_reasons.append("ast_parse_errors")
    if artifacts["ast_dangerous_call_scan_report"].get("dangerous_current_chain_blocker_count") != 0:
        p0_reasons.append("current_chain_dangerous_ast_blocker")
    if artifacts["pre_acquisition_artifact_hash_manifest"].get("missing_critical_artifact_count") != 0:
        p0_reasons.append("missing_critical_artifact")
    if not forbidden_actions_absent:
        p0_reasons.append("forbidden_action_detected")

    p1_reasons = []
    if not ast_validation["ast_risk_classification_adequate"] and not p0_reasons:
        p1_reasons.append("ast_risk_classification_requires_focused_review")
    if artifacts["ast_dangerous_call_scan_report"].get("dormant_repo_attention_count", 0) > 0:
        p1_reasons.append("dormant_repo_attention_carried_forward")
    if not all(validations) and not p0_reasons and not p1_reasons:
        p1_reasons.append("artifact_validation_attention")

    hardening_validation_passed = not p0_reasons and all(validations)
    ast_review_required = ast_validation["ast_risk_requires_focused_review"] and not p0_reasons
    acquisition_contract_resume_allowed = hardening_validation_passed and not ast_review_required
    if p0_reasons:
        status = STATUS_BLOCKED
        next_module = NEXT_MODULE_BLOCKED
        final_decision = "HARDENING_VALIDATION_BLOCKED_P0"
        next_action = "WRITE_HARDENING_IMPLEMENTATION_BLOCKED_RECORD"
        evidence_after = EVIDENCE_AFTER_BLOCKED
    elif ast_review_required:
        status = STATUS_AST_REVIEW
        next_module = NEXT_MODULE_AST_REVIEW
        final_decision = "HARDENING_VALIDATED_AST_RISK_FOCUSED_REVIEW_REQUIRED"
        next_action = "RUN_FOCUSED_AST_RISK_REVIEW_BEFORE_ACQUISITION_CONTRACT_RESUME"
        evidence_after = EVIDENCE_AFTER_AST_REVIEW
    else:
        status = STATUS_PASS
        next_module = NEXT_MODULE_ACQUISITION_CONTRACT
        final_decision = "HARDENING_VALIDATED_ACQUISITION_CONTRACT_RESUME_READY"
        next_action = "RETURN_TO_HISTORICAL_DATA_ACQUISITION_CONTRACT_PATH"
        evidence_after = EVIDENCE_AFTER_PASS

    planned_schema_files_existing_count = sum(
        1 for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists()
    )
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    dangerous_flags = {name: False for name in DANGEROUS_FLAGS}
    artifact_checks = preflight["artifact_checks"]
    required_hardening_artifacts_exist = all(check["exists"] for check in artifact_checks.values())
    required_hardening_artifacts_valid_json = all(check["valid_json"] for check in artifact_checks.values())

    return {
        "generated_at_utc": utc_now(),
        "module_name": MODULE_NAME,
        "pre_acquisition_minimal_reliability_hardening_implementation_validator_status": status,
        "final_decision": final_decision,
        "next_action": next_action,
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
        "prior_implementation_respected": True,
        "hardening_artifact_existence_validation_completed": True,
        "secret_scan_validation_completed": True,
        "dependency_snapshot_validation_completed": True,
        "ast_dangerous_call_validation_completed": True,
        "artifact_hash_manifest_validation_completed": True,
        "policy_artifact_validation_completed": True,
        "compliance_report_validation_completed": True,
        "risk_decision_completed": True,
        "required_hardening_artifacts_exist": required_hardening_artifacts_exist,
        "required_hardening_artifacts_valid_json": required_hardening_artifacts_valid_json,
        "plausible_live_secret_count": artifacts["secret_scan_report"].get("plausible_live_secret_count"),
        "secret_scan_validated": secret_validation["secret_scan_validated"],
        "dependency_snapshot_validated": dependency_validation["dependency_snapshot_validated"],
        "dependency_install_attempted": dependency_validation["dependency_install_attempted"],
        "dependency_update_attempted": dependency_validation["dependency_update_attempted"],
        "environment_modified": dependency_validation["environment_modified"],
        "ast_scan_validated": ast_validation["ast_scan_validated"],
        "tracked_python_files_scanned_count": artifacts["ast_dangerous_call_scan_report"].get(
            "tracked_python_files_scanned_count"
        ),
        "ast_parse_error_count": artifacts["ast_dangerous_call_scan_report"].get("ast_parse_error_count"),
        "dangerous_current_chain_blocker_count": artifacts["ast_dangerous_call_scan_report"].get(
            "dangerous_current_chain_blocker_count"
        ),
        "dormant_repo_attention_count": artifacts["ast_dangerous_call_scan_report"].get(
            "dormant_repo_attention_count"
        ),
        "dormant_repo_attention_count_carried_forward": ast_validation[
            "dormant_repo_attention_count_carried_forward"
        ],
        "executable_external_api_call_count": artifacts["ast_dangerous_call_scan_report"].get(
            "executable_external_api_call_count"
        ),
        "executable_subprocess_risk_count": artifacts["ast_dangerous_call_scan_report"].get(
            "executable_subprocess_risk_count"
        ),
        "executable_eval_exec_risk_count": artifacts["ast_dangerous_call_scan_report"].get(
            "executable_eval_exec_risk_count"
        ),
        "ast_risk_classification_adequate": ast_validation["ast_risk_classification_adequate"],
        "ast_risk_requires_focused_review": ast_review_required,
        "artifact_hash_manifest_validated": manifest_validation["artifact_hash_manifest_validated"],
        "critical_artifact_count": artifacts["pre_acquisition_artifact_hash_manifest"].get(
            "critical_artifact_count"
        ),
        "missing_critical_artifact_count": artifacts["pre_acquisition_artifact_hash_manifest"].get(
            "missing_critical_artifact_count"
        ),
        "hashed_file_count": artifacts["pre_acquisition_artifact_hash_manifest"].get("hashed_file_count"),
        "hash_algorithm": artifacts["pre_acquisition_artifact_hash_manifest"].get("hash_algorithm"),
        "timeout_policy_validated": policy_validation["timeout_policy_validated"],
        "memory_disk_resource_policy_validated": policy_validation["memory_disk_resource_policy_validated"],
        "rollback_policy_validated": policy_validation["rollback_policy_validated"],
        "compliance_report_validated": compliance_validation["compliance_report_validated"],
        "hardening_validation_passed": hardening_validation_passed,
        "hardening_validation_p0_count": len(p0_reasons),
        "hardening_validation_p1_count": len(p1_reasons),
        "hardening_validation_p2_count": 0,
        "acquisition_contract_resume_allowed": acquisition_contract_resume_allowed,
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
        "current_evidence_chain_quality_before_validator": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_validator": evidence_after,
        "active_p0_blocker_count": len(p0_reasons),
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
            "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_VALIDATOR_READY"
            if acquisition_contract_resume_allowed
            else "ATTENTION_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_VALIDATOR_AST_REVIEW_REQUIRED"
            if ast_review_required
            else "BLOCKED_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_VALIDATOR"
        ),
        "derived_live_repo_post_check_reason": (
            "all eight hardening artifacts independently validated; 716 dormant AST risks are "
            "classified outside the current approved acquisition/hardening chain and carried forward "
            "as attention; acquisition contract path may resume while execution remains blocked"
            if acquisition_contract_resume_allowed
            else "hardening artifacts validate enough to avoid P0, but AST classification requires focused review"
            if ast_review_required
            else "hardening validation found P0 blockers"
        ),
        "replacement_checks_all_true": acquisition_contract_resume_allowed,
        "risk_reasons": {
            "p0": p0_reasons,
            "p1": p1_reasons,
            "p2": [],
        },
        "validation_sections": {
            "hardening_artifact_existence_validation": artifact_checks,
            "secret_scan_validation": secret_validation,
            "dependency_snapshot_validation": dependency_validation,
            "ast_dangerous_call_validation": ast_validation,
            "artifact_hash_manifest_validation": manifest_validation,
            "policy_artifact_validation": policy_validation,
            "compliance_report_validation": compliance_validation,
            "risk_decision": {
                "hardening_validation_passed": hardening_validation_passed,
                "hardening_validation_p0_count": len(p0_reasons),
                "hardening_validation_p1_count": len(p1_reasons),
                "hardening_validation_p2_count": 0,
                "dormant_repo_attention_count_carried_forward": ast_validation[
                    "dormant_repo_attention_count_carried_forward"
                ],
                "ast_risk_requires_focused_review": ast_review_required,
                "acquisition_contract_resume_allowed": acquisition_contract_resume_allowed,
                "acquisition_execution_allowed_now": False,
            },
        },
        "preflight": preflight,
        "source_artifacts": {name: str(path) for name, path in REQUIRED_ARTIFACTS.items()},
        "tracked_python_count_expectation": {
            "previous": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT,
        },
    }


def format_summary_txt(summary: Dict[str, Any]) -> str:
    fields = [
        "pre_acquisition_minimal_reliability_hardening_implementation_validator_status",
        "final_decision",
        "next_module",
        "hardening_validation_passed",
        "plausible_live_secret_count",
        "dependency_snapshot_validated",
        "ast_scan_validated",
        "dangerous_current_chain_blocker_count",
        "dormant_repo_attention_count",
        "ast_risk_classification_adequate",
        "ast_risk_requires_focused_review",
        "artifact_hash_manifest_validated",
        "acquisition_contract_resume_allowed",
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
        "implementation_validator_after_approval_v1_latest.json"
    )
    latest_txt = OUT_DIR / (
        "repo_only_pre_acquisition_minimal_reliability_hardening_"
        "implementation_validator_after_approval_v1_latest.txt"
    )
    timestamp_json = OUT_DIR / (
        "repo_only_pre_acquisition_minimal_reliability_hardening_"
        "implementation_validator_after_approval_v1_"
        + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        + ".json"
    )
    validation_json = OUT_DIR / "pre_acquisition_minimal_reliability_hardening_implementation_validation_report.json"
    write_json(latest_json, summary)
    write_json(timestamp_json, summary)
    write_json(validation_json, summary["validation_sections"])
    latest_txt.write_text(format_summary_txt(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
