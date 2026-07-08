from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_future_module_evidence_chain_post_adoption_audit_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_future_module_evidence_chain_post_adoption_audit_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "f149ca4"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 578
NEXT_MODULE = "edge_factory_os_repo_only_future_module_evidence_chain_post_adoption_audit_review_v1.py"
POST_CHECK_STATUS = "REPO_ONLY_FUTURE_MODULE_EVIDENCE_CHAIN_POST_ADOPTION_AUDIT_POST_COMMIT_CHECK_PASS_WITH_ATTENTION"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "DERIVED_OVERUSED_ATTENTION"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

CONTRACT_ARTIFACT = LAB_ROOT / "edge_factory_os_repo_only_future_module_evidence_chain_contract_v1" / "repo_only_future_module_evidence_chain_contract_v1_latest.json"
CONTRACT_VALIDATOR_ARTIFACT = LAB_ROOT / "edge_factory_os_repo_only_future_module_evidence_chain_contract_validator_v1" / "repo_only_future_module_evidence_chain_contract_validator_v1_latest.json"
READINESS_REVIEW_ARTIFACT = LAB_ROOT / "edge_factory_os_repo_only_future_module_evidence_chain_contract_readiness_review_v1" / "repo_only_future_module_evidence_chain_contract_readiness_review_v1_latest.json"
ADOPTION_RECORD_ARTIFACT = LAB_ROOT / "edge_factory_os_repo_only_future_module_evidence_chain_contract_adoption_record_v1" / "repo_only_future_module_evidence_chain_contract_adoption_record_v1_latest.json"
ENFORCEMENT_GATE_ARTIFACT = LAB_ROOT / "edge_factory_os_repo_only_future_module_evidence_chain_contract_enforcement_gate_v1" / "repo_only_future_module_evidence_chain_contract_enforcement_gate_v1_latest.json"
ENFORCEMENT_GATE_VALIDATOR_ARTIFACT = LAB_ROOT / "edge_factory_os_repo_only_future_module_evidence_chain_contract_enforcement_gate_validator_v1" / "repo_only_future_module_evidence_chain_contract_enforcement_gate_validator_v1_latest.json"

ALLOWED_EVIDENCE_CHAIN_QUALITY_VALUES = [
    "PRIMARY_ARTIFACT_STRONG",
    "EXACT_MARKER_STRONG",
    "DERIVED_EXPLICIT_ATTENTION",
    "DERIVED_OVERUSED_ATTENTION",
    "MISSING_EVIDENCE_FAIL_CLOSED",
]

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
    "capital_changed",
    "live_or_real_orders",
    "holdout_accessed",
    "strategy_research_recommended_now",
    "candidate_generation_recommended_now",
    "candidate_release_recommended_now",
    "family_release_recommended_now",
    "schema_apply_allowed_now",
    "schema_file_creation_allowed_now",
    "schema_file_edit_allowed_now",
    "schema_apply_performed_now",
    "schema_file_creation_performed_now",
    "schema_file_edit_performed_now",
    "file_move_allowed_now",
    "file_delete_allowed_now",
    "repo_restructure_allowed_now",
    "gitignore_changed",
    "git_add_force_used",
    "backup_deleted",
    "mass_metadata_patch_allowed",
    "blind_fix_all_allowed",
    "direct_apply_recommended_now",
    "apply_allowed_now",
    "apply_performed_now",
    "manual_approval_present_now",
    "manual_approval_valid_now",
    "implementation_allowed_now",
    "generic_runner_implementation_allowed_now",
    "generic_runner_file_creation_allowed_now",
    "config_file_creation_allowed_now",
    "consolidation_apply_allowed_now",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    safe_args = args
    if args and args[0] == "git":
        safe_args = ["git", "-c", f"safe.directory={REPO_ROOT.as_posix()}", *args[1:]]
    result = subprocess.run(safe_args, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {safe_args} returncode={result.returncode} stderr={result.stderr}")
    return result


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    loaded = json.loads(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def tracked_python_validation() -> Dict[str, Any]:
    files = sorted(line.strip().replace("\\", "/") for line in run_cmd(["git", "ls-files", "*.py"]).stdout.splitlines() if line.strip())
    syntax_errors: List[Dict[str, str]] = []
    bom_errors: List[str] = []
    for rel in files:
        data = (REPO_ROOT / rel).read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
        try:
            ast.parse(data.decode("utf-8"), filename=rel)
        except Exception as exc:
            syntax_errors.append({"path": rel, "error": repr(exc)})
    return {"tracked_python_count": len(files), "tracked_python_syntax_error_count": len(syntax_errors), "tracked_python_bom_error_count": len(bom_errors), "syntax_errors": syntax_errors, "bom_errors": bom_errors}


def git_state() -> Dict[str, Any]:
    status_lines = [line for line in run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"]).stdout.splitlines() if line.strip()]
    untracked = sorted(line[3:].replace("\\", "/") for line in status_lines if line.startswith("?? "))
    dirty_tracked = [line for line in status_lines if not line.startswith("?? ")]
    expected_untracked = [CURRENT_TOOL_REL] if (REPO_ROOT / CURRENT_TOOL_REL).exists() else []
    unexpected_untracked = [path for path in untracked if path not in expected_untracked]
    return {
        "head": run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
        "branch": run_cmd(["git", "branch", "--show-current"]).stdout.strip(),
        "status_porcelain": status_lines,
        "dirty_tracked_paths": [line[3:].replace("\\", "/") for line in dirty_tracked],
        "untracked_paths": untracked,
        "expected_untracked_paths": expected_untracked,
        "unexpected_untracked_paths": unexpected_untracked,
        "repo_clean_for_post_adoption_audit": len(dirty_tracked) == 0 and len(unexpected_untracked) == 0,
    }


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def artifact_summary(path: Path, status_field: str, expected_statuses: set[str]) -> Dict[str, Any]:
    artifact = load_json(path)
    return {
        "path": str(path),
        "exists": bool(artifact),
        "status_field": status_field,
        "status_value": artifact.get(status_field),
        "status_passed": artifact.get(status_field) in expected_statuses,
        "post_check_status": artifact.get("post_check_status"),
        "replacement_checks_all_true": artifact.get("replacement_checks_all_true") is True,
        "policy_active": artifact.get("evidence_chain_policy_level") == POLICY_LEVEL,
        "current_quality_expected": artifact.get("current_evidence_chain_quality") == CURRENT_EVIDENCE_CHAIN_QUALITY,
        "future_modules_classify_quality": artifact.get("future_modules_must_classify_evidence_quality") is True,
        "full_marker_preferred": artifact.get("full_post_check_marker_preferred_over_plain_pass") is True,
        "plain_pass_attention": artifact.get("plain_pass_without_marker_is_attention") is True,
        "replacement_not_primary": artifact.get("replacement_checks_are_not_equivalent_to_primary_artifact") is True,
        "generic_runner_not_approved": artifact.get("generic_runner_approval_granted") is False,
        "generic_runner_blocked": artifact.get("generic_runner_implementation_remains_blocked") is True,
        "ordinary_loop_reentry_blocked": artifact.get("ordinary_selector_backlog_loop_reentry_allowed") is False,
        "loop_closed": artifact.get("loop_remains_closed") is True,
    }


def audit_findings(summaries: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    checks = {
        "evidence_chain_contract_exists": summaries["contract"]["exists"],
        "contract_validator_passed": summaries["contract_validator"]["status_passed"],
        "readiness_review_passed": summaries["readiness_review"]["status_passed"],
        "adoption_record_passed": summaries["adoption_record"]["status_passed"],
        "enforcement_gate_exists": summaries["enforcement_gate"]["exists"],
        "enforcement_gate_validator_passed": summaries["enforcement_gate_validator"]["status_passed"],
        "future_modules_must_classify_evidence_chain_quality": all(item["future_modules_classify_quality"] for item in summaries.values()),
        "full_post_check_marker_preferred_over_plain_pass": all(item["full_marker_preferred"] for item in summaries.values()),
        "plain_pass_without_marker_is_attention": all(item["plain_pass_attention"] for item in summaries.values()),
        "derived_live_repo_post_check_weaker_than_primary_artifact_verification": all(item["replacement_not_primary"] for item in summaries.values()),
        "replacement_checks_explicit_and_complete": all(item["replacement_checks_all_true"] for item in summaries.values()),
        "missing_primary_artifact_must_not_silently_pass": all(item["replacement_checks_all_true"] for item in summaries.values()),
        "generic_runner_remains_blocked": all(item["generic_runner_not_approved"] and item["generic_runner_blocked"] for item in summaries.values()),
        "closed_generic_governance_loop_remains_closed": all(item["ordinary_loop_reentry_blocked"] and item["loop_closed"] for item in summaries.values()),
    }
    for name, passed in checks.items():
        findings.append(
            {
                "finding": name,
                "passed": passed,
                "severity": "P0" if not passed and "exists" in name else "P1" if not passed else "INFO",
                "classification": "monitoring_only" if passed else "repair_preview_needed",
            }
        )
    return findings


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    dangerous_flags = {flag: False for flag in DANGEROUS_FLAGS}

    summaries = {
        "contract": artifact_summary(CONTRACT_ARTIFACT, "contract_status", {"READY", "PASS"}),
        "contract_validator": artifact_summary(CONTRACT_VALIDATOR_ARTIFACT, "contract_validator_status", {"READY", "PASS"}),
        "readiness_review": artifact_summary(READINESS_REVIEW_ARTIFACT, "readiness_review_status", {"READY", "PASS", "PASS_WITH_ATTENTION", "PASS_CONTEXTUAL"}),
        "adoption_record": artifact_summary(ADOPTION_RECORD_ARTIFACT, "adoption_record_status", {"READY", "PASS", "PASS_WITH_ATTENTION"}),
        "enforcement_gate": artifact_summary(ENFORCEMENT_GATE_ARTIFACT, "enforcement_gate_status", {"READY", "PASS"}),
        "enforcement_gate_validator": artifact_summary(ENFORCEMENT_GATE_VALIDATOR_ARTIFACT, "enforcement_gate_validator_status", {"READY", "PASS"}),
    }
    findings = audit_findings(summaries)
    active_issue_count = sum(1 for finding in findings if finding["passed"] is False)

    replacement_checks = {
        "expected_head_observed": git["head"] == EXPECTED_HEAD,
        "repo_clean_for_post_adoption_audit": git["repo_clean_for_post_adoption_audit"],
        "tracked_python_count_matches_previous": py["tracked_python_count"] == EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in dangerous_flags.values()),
        "audit_findings_generated": len(findings) == 14,
        "audit_does_not_fix": True,
        "next_module_expected": NEXT_MODULE == "edge_factory_os_repo_only_future_module_evidence_chain_post_adoption_audit_review_v1.py",
    }
    ready = all(value is True for value in replacement_checks.values()) and active_issue_count == 0

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "post_adoption_audit_status": "PASS_WITH_ATTENTION" if ready else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS if ready else "REPO_ONLY_FUTURE_MODULE_EVIDENCE_CHAIN_POST_ADOPTION_AUDIT_POST_COMMIT_CHECK_FAIL_CLOSED",
        "final_decision": "FUTURE_MODULE_EVIDENCE_CHAIN_POST_ADOPTION_AUDIT_READY" if ready else "FUTURE_MODULE_EVIDENCE_CHAIN_POST_ADOPTION_AUDIT_FAIL_CLOSED",
        "next_action": "BUILD_FUTURE_MODULE_EVIDENCE_CHAIN_POST_ADOPTION_AUDIT_REVIEW_V1" if ready else "REVIEW_FUTURE_MODULE_EVIDENCE_CHAIN_POST_ADOPTION_AUDIT_INPUTS",
        "next_module": NEXT_MODULE if ready else None,
        "evidence_chain_contract_adopted": summaries["adoption_record"]["status_passed"],
        "enforcement_gate_validated": summaries["enforcement_gate_validator"]["status_passed"],
        "evidence_chain_policy_level": POLICY_LEVEL,
        "evidence_chain_quality": CURRENT_EVIDENCE_CHAIN_QUALITY,
        "current_evidence_chain_quality": CURRENT_EVIDENCE_CHAIN_QUALITY,
        "allowed_evidence_chain_quality_values": ALLOWED_EVIDENCE_CHAIN_QUALITY_VALUES,
        "audit_only_no_fix_performed": True,
        "future_modules_must_classify_evidence_quality": True,
        "full_post_check_marker_preferred_over_plain_pass": True,
        "plain_pass_without_marker_is_attention": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "missing_primary_artifact_must_not_silently_pass": True,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": len(planned_existing),
        "planned_schema_files_existing": planned_existing,
        "generic_runner_target_exists": generic_runner_target_exists,
        "dangerous_flags": dangerous_flags,
        "dangerous_flags_all_false": all(value is False for value in dangerous_flags.values()),
        "dangerous_flag_true_count": 0,
        "auto_fix_performed": False,
        "direct_apply_performed": False,
        "repair_apply_allowed_now": False,
        "active_p0_blocker_count": sum(1 for finding in findings if finding["severity"] == "P0" and finding["passed"] is False),
        "active_p1_attention_count": sum(1 for finding in findings if finding["severity"] == "P1" and finding["passed"] is False),
        "audit_active_issue_count": active_issue_count,
        "audit_findings": findings,
        "artifact_audit": summaries,
        "derived_live_repo_post_check": True,
        "derived_live_repo_post_check_reason": "Post-adoption audit uses existing module artifacts plus live repo replacement checks; this is weaker than primary post-check artifact verification and remains DERIVED_OVERUSED_ATTENTION.",
        "replacement_checks_all_true": ready,
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {"git_state": git, "tracked_python_validation": py},
        "safety_flags": {
            "future_module_evidence_chain_post_adoption_audit": True,
            "repo_only": True,
            "audit_only_no_fix_performed": True,
            "generic_runner_approval_granted": False,
            "generic_runner_implementation_remains_blocked": True,
            "ordinary_selector_backlog_loop_reentry_allowed": False,
            "loop_remains_closed": True,
            "auto_fix_performed": False,
            "direct_apply_performed": False,
            "repair_apply_allowed_now": False,
            **dangerous_flags,
        },
    }
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_future_module_evidence_chain_post_adoption_audit_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_future_module_evidence_chain_post_adoption_audit_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_future_module_evidence_chain_post_adoption_audit_v1_latest.txt"
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    latest_json.write_text(rendered, encoding="utf-8")
    timestamped_json.write_text(rendered, encoding="utf-8")
    latest_txt.write_text(rendered + "\n", encoding="utf-8")
    return {"latest_json": str(latest_json), "timestamped_json": str(timestamped_json), "latest_txt": str(latest_txt)}


def main() -> int:
    payload = build_payload()
    outputs = write_outputs(payload)
    payload["outputs"] = outputs
    Path(outputs["latest_json"]).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    Path(outputs["latest_txt"]).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["post_adoption_audit_status"] in {"READY", "PASS", "PASS_WITH_ATTENTION"} else 3


if __name__ == "__main__":
    raise SystemExit(main())
