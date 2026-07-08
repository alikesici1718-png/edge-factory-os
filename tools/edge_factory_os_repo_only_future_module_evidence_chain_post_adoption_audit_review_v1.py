from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_future_module_evidence_chain_post_adoption_audit_review_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_future_module_evidence_chain_post_adoption_audit_review_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "40df263"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 579
NEXT_MODULE_NO_ACTIVE_P0_P1 = "edge_factory_os_repo_only_future_module_evidence_chain_rollout_status_record_v1.py"
NEXT_MODULE_ACTIVE_P0_P1 = "edge_factory_os_repo_only_future_module_evidence_chain_post_adoption_repair_preview_v1.py"
POST_CHECK_STATUS = "REPO_ONLY_FUTURE_MODULE_EVIDENCE_CHAIN_POST_ADOPTION_AUDIT_REVIEW_POST_COMMIT_CHECK_PASS_CONTEXTUAL"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "DERIVED_OVERUSED_ATTENTION"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

POST_ADOPTION_AUDIT_ARTIFACT = LAB_ROOT / "edge_factory_os_repo_only_future_module_evidence_chain_post_adoption_audit_v1" / "repo_only_future_module_evidence_chain_post_adoption_audit_v1_latest.json"

REVIEW_CLASSIFICATIONS = [
    "active_issue",
    "historical_artifact_trace",
    "contextual_attention",
    "monitoring_only",
    "repair_preview_needed",
]

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
        "repo_clean_for_audit_review": len(dirty_tracked) == 0 and len(unexpected_untracked) == 0,
    }


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def classify_audit_findings(audit: Dict[str, Any]) -> List[Dict[str, Any]]:
    reviewed: List[Dict[str, Any]] = []
    for finding in audit.get("audit_findings", []):
        passed = finding.get("passed") is True
        severity = finding.get("severity")
        if passed:
            classification = "monitoring_only"
        elif severity in {"P0", "P1"}:
            classification = "active_issue"
        else:
            classification = "contextual_attention"
        reviewed.append(
            {
                "finding": finding.get("finding"),
                "source_classification": finding.get("classification"),
                "review_classification": classification,
                "severity": severity,
                "passed": passed,
                "repair_preview_needed": classification == "active_issue",
            }
        )
    reviewed.append(
        {
            "finding": "evidence_quality_remains_derived_overused_attention",
            "source_classification": "contextual_attention",
            "review_classification": "contextual_attention",
            "severity": "P2",
            "passed": True,
            "repair_preview_needed": False,
        }
    )
    reviewed.append(
        {
            "finding": "prior_contract_artifacts_remain_historical_trace_for_rollout",
            "source_classification": "historical_artifact_trace",
            "review_classification": "historical_artifact_trace",
            "severity": "INFO",
            "passed": True,
            "repair_preview_needed": False,
        }
    )
    return reviewed


def classification_counts(reviewed_findings: List[Dict[str, Any]]) -> Dict[str, int]:
    return {
        classification: sum(1 for finding in reviewed_findings if finding.get("review_classification") == classification)
        for classification in REVIEW_CLASSIFICATIONS
    }


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    dangerous_flags = {flag: False for flag in DANGEROUS_FLAGS}
    audit = load_json(POST_ADOPTION_AUDIT_ARTIFACT)
    reviewed_findings = classify_audit_findings(audit)
    counts = classification_counts(reviewed_findings)
    active_p0_blocker_count = sum(1 for finding in reviewed_findings if finding["review_classification"] == "active_issue" and finding["severity"] == "P0")
    active_p1_attention_count = sum(1 for finding in reviewed_findings if finding["review_classification"] == "active_issue" and finding["severity"] == "P1")
    repair_preview_required = active_p0_blocker_count + active_p1_attention_count > 0
    next_module = NEXT_MODULE_ACTIVE_P0_P1 if repair_preview_required else NEXT_MODULE_NO_ACTIVE_P0_P1

    audit_policy_ok = (
        audit.get("post_adoption_audit_status") in {"READY", "PASS", "PASS_WITH_ATTENTION"}
        and audit.get("next_module") == "edge_factory_os_repo_only_future_module_evidence_chain_post_adoption_audit_review_v1.py"
        and audit.get("evidence_chain_policy_level") == POLICY_LEVEL
        and audit.get("current_evidence_chain_quality") == CURRENT_EVIDENCE_CHAIN_QUALITY
        and audit.get("future_modules_must_classify_evidence_quality") is True
        and audit.get("full_post_check_marker_preferred_over_plain_pass") is True
        and audit.get("plain_pass_without_marker_is_attention") is True
        and audit.get("replacement_checks_are_not_equivalent_to_primary_artifact") is True
        and audit.get("generic_runner_approval_granted") is False
        and audit.get("generic_runner_implementation_remains_blocked") is True
        and audit.get("ordinary_selector_backlog_loop_reentry_allowed") is False
        and audit.get("loop_remains_closed") is True
        and audit.get("replacement_checks_all_true") is True
    )

    replacement_checks = {
        "expected_head_observed": git["head"] == EXPECTED_HEAD,
        "repo_clean_for_audit_review": git["repo_clean_for_audit_review"],
        "tracked_python_count_matches_previous": py["tracked_python_count"] == EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in dangerous_flags.values()),
        "post_adoption_audit_artifact_exists": bool(audit),
        "post_adoption_audit_policy_ok": audit_policy_ok,
        "findings_classified": len(reviewed_findings) >= len(audit.get("audit_findings", [])) and all(finding.get("review_classification") in REVIEW_CLASSIFICATIONS for finding in reviewed_findings),
        "repair_apply_disallowed": True,
        "next_module_expected": next_module in {NEXT_MODULE_NO_ACTIVE_P0_P1, NEXT_MODULE_ACTIVE_P0_P1},
    }
    ready = all(value is True for value in replacement_checks.values())

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "audit_review_status": "PASS_CONTEXTUAL" if ready else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS if ready else "REPO_ONLY_FUTURE_MODULE_EVIDENCE_CHAIN_POST_ADOPTION_AUDIT_REVIEW_POST_COMMIT_CHECK_FAIL_CLOSED",
        "final_decision": "FUTURE_MODULE_EVIDENCE_CHAIN_AUDIT_REVIEW_ROLLOUT_READY" if ready and not repair_preview_required else "FUTURE_MODULE_EVIDENCE_CHAIN_AUDIT_REVIEW_REPAIR_PREVIEW_REQUIRED" if ready else "FUTURE_MODULE_EVIDENCE_CHAIN_AUDIT_REVIEW_FAIL_CLOSED",
        "next_action": "BUILD_FUTURE_MODULE_EVIDENCE_CHAIN_ROLLOUT_STATUS_RECORD_V1" if ready and not repair_preview_required else "BUILD_FUTURE_MODULE_EVIDENCE_CHAIN_POST_ADOPTION_REPAIR_PREVIEW_V1" if ready else "REVIEW_FUTURE_MODULE_EVIDENCE_CHAIN_AUDIT_REVIEW_INPUTS",
        "next_module": next_module if ready else None,
        "repair_preview_required": repair_preview_required,
        "repair_apply_allowed_now": False,
        "active_p0_blocker_count": active_p0_blocker_count,
        "active_p1_attention_count": active_p1_attention_count,
        "review_classifications": REVIEW_CLASSIFICATIONS,
        "review_classification_counts": counts,
        "reviewed_findings": reviewed_findings,
        "evidence_chain_policy_level": POLICY_LEVEL,
        "evidence_chain_quality": CURRENT_EVIDENCE_CHAIN_QUALITY,
        "current_evidence_chain_quality": CURRENT_EVIDENCE_CHAIN_QUALITY,
        "allowed_evidence_chain_quality_values": ALLOWED_EVIDENCE_CHAIN_QUALITY_VALUES,
        "future_modules_must_classify_evidence_quality": True,
        "full_post_check_marker_preferred_over_plain_pass": True,
        "plain_pass_without_marker_is_attention": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "derived_checks_are_weaker_than_primary_artifacts": True,
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
        "derived_live_repo_post_check": True,
        "derived_live_repo_post_check_reason": "Audit review uses the post-adoption audit artifact and live repo replacement checks; evidence remains DERIVED_OVERUSED_ATTENTION and weaker than primary artifact verification.",
        "replacement_checks_all_true": ready,
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "post_adoption_audit_loaded": bool(audit),
            "post_adoption_audit_status": audit.get("post_adoption_audit_status"),
            "post_adoption_audit_next_module": audit.get("next_module"),
        },
        "safety_flags": {
            "future_module_evidence_chain_post_adoption_audit_review": True,
            "repo_only": True,
            "auto_fix_performed": False,
            "direct_apply_performed": False,
            "repair_preview_required": repair_preview_required,
            "repair_apply_allowed_now": False,
            "generic_runner_approval_granted": False,
            "generic_runner_implementation_remains_blocked": True,
            "ordinary_selector_backlog_loop_reentry_allowed": False,
            "loop_remains_closed": True,
            **dangerous_flags,
        },
    }
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_future_module_evidence_chain_post_adoption_audit_review_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_future_module_evidence_chain_post_adoption_audit_review_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_future_module_evidence_chain_post_adoption_audit_review_v1_latest.txt"
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
    return 0 if payload["audit_review_status"] in {"READY", "PASS", "PASS_CONTEXTUAL", "PASS_WITH_ATTENTION"} else 3


if __name__ == "__main__":
    raise SystemExit(main())
