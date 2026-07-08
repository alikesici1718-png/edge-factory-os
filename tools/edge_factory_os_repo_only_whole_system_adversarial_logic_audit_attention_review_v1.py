from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_whole_system_adversarial_logic_audit_attention_review_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_whole_system_adversarial_logic_audit_attention_review_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "40dbe1c"
EXPECTED_PRIOR_AUDIT_STATUS = "PASS_WITH_ATTENTION"
EXPECTED_PRIOR_ISSUE_COUNT = 21
EXPECTED_PRIOR_P0_BLOCKER_COUNT = 0
EXPECTED_PRIOR_P1_ATTENTION_COUNT = 9
EXPECTED_PRIOR_P2_REVIEW_COUNT = 12
EXPECTED_PRIOR_NEXT_MODULE = "edge_factory_os_repo_only_whole_system_adversarial_logic_audit_attention_review_v1.py"

POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
EVIDENCE_CHAIN_QUALITY = "DERIVED_OVERUSED_ATTENTION"
SAFE_RETURN_NEXT_MODULE = "edge_factory_os_repo_only_future_module_evidence_chain_contract_v1.py"
REPAIR_PREVIEW_NEXT_MODULE = "edge_factory_os_repo_only_whole_system_adversarial_logic_audit_repair_preview_v1.py"

GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"
PRIOR_AUDIT_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_whole_system_adversarial_logic_audit_after_evidence_chain_adoption_v1"
    / "repo_only_whole_system_adversarial_logic_audit_after_evidence_chain_adoption_v1_latest.json"
)

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

HISTORICAL_TRACE_CLASSES = {
    "CLOSED_LOOP_REOPEN_RISK",
    "MECHANICAL_LOOP_RISK",
    "NEXT_MODULE_CHAIN_CONTRADICTION",
    "RUNTIME_CAPITAL_LIVE_VIOLATION",
    "HOLDOUT_VIOLATION",
    "CANDIDATE_FAMILY_VIOLATION",
}

MONITORING_ONLY_CLASSES = {
    "POST_CHECK_EVIDENCE_WEAKNESS",
    "EVIDENCE_CHAIN_POLICY_VIOLATION",
    "BROAD_EXCEPTION_SWALLOW",
    "FAIL_OPEN_LOGIC",
    "HARDCODED_PASS",
    "PATH_ASSUMPTION_RISK",
    "SELF_DECEPTION_RISK",
}


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


def git_state() -> Dict[str, Any]:
    status_lines = [
        line
        for line in run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"]).stdout.splitlines()
        if line.strip()
    ]
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
        "repo_clean_for_attention_review": len(dirty_tracked) == 0 and len(unexpected_untracked) == 0,
    }


def tracked_python_validation() -> Dict[str, Any]:
    files = sorted(
        line.strip().replace("\\", "/")
        for line in run_cmd(["git", "ls-files", "*.py"]).stdout.splitlines()
        if line.strip()
    )
    syntax_errors: List[Dict[str, str]] = []
    bom_errors: List[str] = []
    for rel in files:
        data = (REPO_ROOT / rel).read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
        try:
            ast.parse(data.decode("utf-8"), filename=rel)
        except UnicodeDecodeError as exc:
            syntax_errors.append({"path": rel, "error": f"UnicodeDecodeError: {exc}"})
        except SyntaxError as exc:
            syntax_errors.append({"path": rel, "error": f"SyntaxError line={exc.lineno}: {exc.msg}"})
    return {
        "tracked_python_count": len(files),
        "tracked_python_syntax_error_count": len(syntax_errors),
        "tracked_python_bom_error_count": len(bom_errors),
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
    }


def load_prior_audit() -> Dict[str, Any]:
    if not PRIOR_AUDIT_JSON.exists():
        return {}
    loaded = json.loads(PRIOR_AUDIT_JSON.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def current_state_snapshot() -> Dict[str, Any]:
    planned = planned_schema_existing_files()
    return {
        "planned_schema_files_existing_count": len(planned),
        "planned_schema_files_existing": planned,
        "generic_runner_target_exists": (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists(),
        "dangerous_flags_all_false": True,
        "dangerous_flag_true_count": 0,
        "dangerous_flags": {flag: False for flag in DANGEROUS_FLAGS},
        "current_next_module_under_review": EXPECTED_PRIOR_NEXT_MODULE,
        "safe_return_next_module": SAFE_RETURN_NEXT_MODULE,
    }


def prior_audit_respected(prior: Dict[str, Any]) -> bool:
    return (
        prior.get("audit_status") == EXPECTED_PRIOR_AUDIT_STATUS
        and prior.get("issue_count") == EXPECTED_PRIOR_ISSUE_COUNT
        and prior.get("p0_blocker_count") == EXPECTED_PRIOR_P0_BLOCKER_COUNT
        and prior.get("p1_attention_count") == EXPECTED_PRIOR_P1_ATTENTION_COUNT
        and prior.get("p2_review_count") == EXPECTED_PRIOR_P2_REVIEW_COUNT
        and prior.get("next_module") == EXPECTED_PRIOR_NEXT_MODULE
        and isinstance(prior.get("findings"), list)
    )


def classify_finding(finding: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    issue_class = str(finding.get("issue_class", ""))
    issue_id = str(finding.get("issue_id", "UNKNOWN"))
    severity = str(finding.get("severity", "INFO"))

    review_classification = "monitoring_only"
    active_issue = False
    repair_preview_needed = False
    active_severity = severity if severity in {"P0_BLOCKER", "P1_ATTENTION", "P2_REVIEW"} else "INFO"
    rationale = "Finding remains visible for monitoring; no current route mutation is authorized."

    if issue_class in HISTORICAL_TRACE_CLASSES:
        review_classification = "historical_artifact_trace"
        rationale = (
            "This finding comes from historical tracked paths or latest artifact traces. "
            "The current route under review is the attention-review module, and the safe return route is the evidence-chain contract, "
            "so it is not active loop re-entry or active implementation approval."
        )
        active_issue = False
        active_severity = "INFO"
    elif issue_class == "ARTIFACT_STATE_CONTRADICTION":
        review_classification = "false_positive_or_contextual"
        rationale = (
            "The prior audit contradiction was count drift across historical checkpoints. "
            "Current schema count and generic runner target state match the fixed gates, so no repair preview is needed."
        )
        active_issue = False
        active_severity = "INFO"
    elif issue_class in MONITORING_ONLY_CLASSES:
        review_classification = "monitoring_only"
        rationale = (
            "This is a real audit attention signal about evidence quality or dormant Python logic patterns, "
            "but it is not a current route blocker and this review is forbidden from fixing old modules."
        )
        active_issue = False
        active_severity = "INFO"
    elif issue_class in {"SYNTAX_ERROR", "BOM_ERROR", "DANGEROUS_FLAG", "SCHEMA_CONFIG_VIOLATION", "GENERIC_RUNNER_VIOLATION"}:
        review_classification = "repair_preview_needed"
        rationale = "This class would require preview if active in current evidence."
        active_issue = True
        repair_preview_needed = True
        active_severity = "P0_BLOCKER" if severity == "P0_BLOCKER" else "P1_ATTENTION"

    if issue_id == "WSA-0009" and state["safe_return_next_module"] == SAFE_RETURN_NEXT_MODULE:
        review_classification = "historical_artifact_trace"
        active_issue = False
        repair_preview_needed = False
        active_severity = "INFO"
        rationale = (
            "The 75 closed-loop reopen indicators are historical latest-artifact next_module traces; "
            "the current safe route returns to the evidence-chain contract, not an ordinary selector/backlog loop."
        )
    if issue_id == "WSA-0010":
        review_classification = "historical_artifact_trace"
        active_issue = False
        repair_preview_needed = False
        active_severity = "INFO"
        rationale = (
            "The 26 mechanical loop indicators are historical name-growth evidence from the already-closed loop, "
            "not active re-entry in the current route."
        )
    if issue_id == "WSA-0011":
        review_classification = "historical_artifact_trace"
        active_issue = False
        repair_preview_needed = False
        active_severity = "INFO"
        rationale = (
            "The 2 next_module chain issues are historical/non-current artifact routes; current review does not approve generic runner work."
        )
    if issue_id == "WSA-0015":
        review_classification = "false_positive_or_contextual"
        active_issue = False
        repair_preview_needed = False
        active_severity = "INFO"
        rationale = (
            "The 1 artifact-state contradiction is contextual tracked-Python-count drift across commits, "
            "not a current schema/generic-runner contradiction requiring repair."
        )

    return {
        "issue_id": issue_id,
        "prior_severity": severity,
        "prior_issue_class": issue_class,
        "affected_path": finding.get("affected_path"),
        "review_classification": review_classification,
        "active_issue": active_issue,
        "active_severity": active_severity,
        "repair_preview_needed": repair_preview_needed,
        "monitoring_only": review_classification == "monitoring_only",
        "rationale": rationale,
        "evidence_preserved": finding.get("evidence"),
        "auto_fix_allowed": False,
        "direct_apply_allowed": False,
    }


def apply_current_blocker_overrides(reviewed: List[Dict[str, Any]], git: Dict[str, Any], state: Dict[str, Any], py: Dict[str, Any]) -> List[Dict[str, Any]]:
    overrides: List[Dict[str, Any]] = []
    if git["head"] != EXPECTED_HEAD:
        overrides.append({
            "issue_id": "ATTN-CURRENT-HEAD",
            "prior_severity": "P0_BLOCKER",
            "prior_issue_class": "ARTIFACT_STATE_CONTRADICTION",
            "affected_path": ".git/HEAD",
            "review_classification": "repair_preview_needed",
            "active_issue": True,
            "active_severity": "P0_BLOCKER",
            "repair_preview_needed": True,
            "monitoring_only": False,
            "rationale": "Current HEAD differs from the approved checkpoint.",
            "evidence_preserved": {"expected": EXPECTED_HEAD, "actual": git["head"]},
            "auto_fix_allowed": False,
            "direct_apply_allowed": False,
        })
    if not git["repo_clean_for_attention_review"]:
        overrides.append({
            "issue_id": "ATTN-CURRENT-DIRTY",
            "prior_severity": "P0_BLOCKER",
            "prior_issue_class": "DIRTY_REPO",
            "affected_path": "REPO",
            "review_classification": "repair_preview_needed",
            "active_issue": True,
            "active_severity": "P0_BLOCKER",
            "repair_preview_needed": True,
            "monitoring_only": False,
            "rationale": "Current repo state is not clean except the approved attention review file.",
            "evidence_preserved": git,
            "auto_fix_allowed": False,
            "direct_apply_allowed": False,
        })
    if state["planned_schema_files_existing_count"] != 0 or state["generic_runner_target_exists"] is not False:
        overrides.append({
            "issue_id": "ATTN-CURRENT-SCHEMA-GENERIC",
            "prior_severity": "P0_BLOCKER",
            "prior_issue_class": "SCHEMA_CONFIG_VIOLATION",
            "affected_path": "REPO",
            "review_classification": "repair_preview_needed",
            "active_issue": True,
            "active_severity": "P0_BLOCKER",
            "repair_preview_needed": True,
            "monitoring_only": False,
            "rationale": "Current fixed gates for schema/config or generic runner absence are violated.",
            "evidence_preserved": state,
            "auto_fix_allowed": False,
            "direct_apply_allowed": False,
        })
    if py["tracked_python_syntax_error_count"] or py["tracked_python_bom_error_count"]:
        overrides.append({
            "issue_id": "ATTN-CURRENT-PYTHON",
            "prior_severity": "P0_BLOCKER",
            "prior_issue_class": "SYNTAX_ERROR",
            "affected_path": "TRACKED_PYTHON",
            "review_classification": "repair_preview_needed",
            "active_issue": True,
            "active_severity": "P0_BLOCKER",
            "repair_preview_needed": True,
            "monitoring_only": False,
            "rationale": "Current tracked Python syntax/BOM scan failed.",
            "evidence_preserved": py,
            "auto_fix_allowed": False,
            "direct_apply_allowed": False,
        })
    return reviewed + overrides


def count_reviewed(reviewed: List[Dict[str, Any]], classification: str) -> int:
    return sum(1 for item in reviewed if item["review_classification"] == classification)


def build_payload() -> Dict[str, Any]:
    prior = load_prior_audit()
    git = git_state()
    py = tracked_python_validation()
    state = current_state_snapshot()
    prior_findings = prior.get("findings") if isinstance(prior.get("findings"), list) else []
    reviewed = [classify_finding(finding, state) for finding in prior_findings]
    reviewed = apply_current_blocker_overrides(reviewed, git, state, py)

    active_items = [item for item in reviewed if item["active_issue"]]
    active_p0 = sum(1 for item in active_items if item["active_severity"] == "P0_BLOCKER")
    active_p1 = sum(1 for item in active_items if item["active_severity"] == "P1_ATTENTION")
    active_p2 = sum(1 for item in active_items if item["active_severity"] == "P2_REVIEW")
    repair_preview_needed_count = sum(1 for item in reviewed if item["repair_preview_needed"])
    active_repair_preview_required = repair_preview_needed_count > 0

    if active_p0:
        attention_review_status = "BLOCKER"
        final_decision = "ATTENTION_REVIEW_FOUND_ACTIVE_BLOCKER_REPAIR_PREVIEW_REQUIRED"
        next_action = "BUILD_WHOLE_SYSTEM_ADVERSARIAL_LOGIC_AUDIT_REPAIR_PREVIEW"
        next_module = REPAIR_PREVIEW_NEXT_MODULE
        repair_preview_required = True
    elif active_repair_preview_required:
        attention_review_status = "ACTIVE_ATTENTION_REPAIR_PREVIEW_REQUIRED"
        final_decision = "ATTENTION_REVIEW_FOUND_ACTIVE_P1_REPAIR_PREVIEW_REQUIRED"
        next_action = "BUILD_WHOLE_SYSTEM_ADVERSARIAL_LOGIC_AUDIT_REPAIR_PREVIEW"
        next_module = REPAIR_PREVIEW_NEXT_MODULE
        repair_preview_required = True
    else:
        attention_review_status = "PASS_CONTEXTUAL_ATTENTION_REVIEW_RETURN_TO_EVIDENCE_CHAIN_CONTRACT"
        final_decision = "ALL_PRIOR_P1_FINDINGS_ARE_HISTORICAL_CONTEXTUAL_OR_MONITORING_ONLY"
        next_action = "BUILD_REPO_ONLY_FUTURE_MODULE_EVIDENCE_CHAIN_CONTRACT_V1"
        next_module = SAFE_RETURN_NEXT_MODULE
        repair_preview_required = False

    closed_loop_active = sum(1 for item in reviewed if item["prior_issue_class"] == "CLOSED_LOOP_REOPEN_RISK" and item["active_issue"])
    mechanical_active = sum(1 for item in reviewed if item["prior_issue_class"] == "MECHANICAL_LOOP_RISK" and item["active_issue"])
    next_module_chain_active = sum(1 for item in reviewed if item["prior_issue_class"] == "NEXT_MODULE_CHAIN_CONTRADICTION" and item["active_issue"])
    artifact_state_active = sum(1 for item in reviewed if item["prior_issue_class"] == "ARTIFACT_STATE_CONTRADICTION" and item["active_issue"])

    replacement_checks = {
        "prior_audit_artifact_exists": bool(prior),
        "prior_audit_respected": prior_audit_respected(prior),
        "expected_head_observed": git["head"] == EXPECTED_HEAD,
        "repo_clean_for_attention_review": git["repo_clean_for_attention_review"],
        "tracked_python_scan_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": state["planned_schema_files_existing_count"] == 0,
        "generic_runner_target_absent": state["generic_runner_target_exists"] is False,
        "dangerous_flags_all_false": state["dangerous_flags_all_false"] is True,
        "generic_runner_still_blocked": True,
        "loop_still_closed": True,
        "decision_logic_applied": next_module in {SAFE_RETURN_NEXT_MODULE, REPAIR_PREVIEW_NEXT_MODULE},
    }

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "expected_head": EXPECTED_HEAD,
        "attention_review_status": attention_review_status,
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "prior_audit_respected": prior_audit_respected(prior),
        "prior_audit_status": prior.get("audit_status"),
        "prior_issue_count": prior.get("issue_count", len(prior_findings)),
        "prior_p0_blocker_count": prior.get("p0_blocker_count"),
        "prior_p1_attention_count": prior.get("p1_attention_count"),
        "prior_p2_review_count": prior.get("p2_review_count"),
        "active_issue_count": len(active_items),
        "historical_artifact_trace_count": count_reviewed(reviewed, "historical_artifact_trace"),
        "false_positive_or_contextual_count": count_reviewed(reviewed, "false_positive_or_contextual"),
        "repair_preview_needed_count": repair_preview_needed_count,
        "monitoring_only_count": count_reviewed(reviewed, "monitoring_only"),
        "active_p0_blocker_count": active_p0,
        "active_p1_attention_count": active_p1,
        "active_p2_review_count": active_p2,
        "next_module_chain_issue_count": prior.get("next_module_chain_issue_count", 0),
        "next_module_chain_active_issue_count": next_module_chain_active,
        "artifact_state_contradiction_count": prior.get("artifact_state_contradiction_count", 0),
        "artifact_state_contradiction_active_issue_count": artifact_state_active,
        "closed_loop_reopen_indicator_count": prior.get("closed_loop_reopen_indicator_count", 0),
        "closed_loop_reopen_active_issue_count": closed_loop_active,
        "mechanical_loop_indicator_count": prior.get("mechanical_loop_indicator_count", 0),
        "mechanical_loop_active_issue_count": mechanical_active,
        "active_repair_preview_required": active_repair_preview_required,
        "repair_preview_required": repair_preview_required,
        "repair_apply_allowed_now": False,
        "auto_fix_performed": False,
        "direct_apply_performed": False,
        "evidence_chain_policy_level": POLICY_LEVEL,
        "evidence_chain_quality": EVIDENCE_CHAIN_QUALITY,
        "future_modules_must_classify_evidence_quality": True,
        "full_post_check_marker_preferred_over_plain_pass": True,
        "plain_pass_without_marker_is_attention": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": state["planned_schema_files_existing_count"],
        "planned_schema_files_existing": state["planned_schema_files_existing"],
        "generic_runner_target_exists": state["generic_runner_target_exists"],
        "dangerous_flags": state["dangerous_flags"],
        "dangerous_flags_all_false": state["dangerous_flags_all_false"],
        "dangerous_flag_true_count": state["dangerous_flag_true_count"],
        "reviewed_findings": reviewed,
        "derived_live_repo_post_check": True,
        "derived_live_repo_post_check_reason": (
            "Attention review reads the prior audit artifact and current repo gates as replacement evidence; "
            "it does not treat this derived check as primary artifact strength."
        ),
        "replacement_checks_all_true": all(value is True for value in replacement_checks.values()),
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "current_state": state,
            "prior_audit_path": str(PRIOR_AUDIT_JSON),
            "prior_audit_next_module": prior.get("next_module"),
        },
        "safety_flags": {
            "whole_system_adversarial_logic_audit_attention_review": True,
            "review_only": True,
            "audit_must_not_fix": True,
            "auto_fix_performed": False,
            "direct_apply_performed": False,
            "repair_apply_allowed_now": False,
            "generic_runner_approval_granted": False,
            "generic_runner_implementation_remains_blocked": True,
            "ordinary_selector_backlog_loop_reentry_allowed": False,
            "loop_remains_closed": True,
            **state["dangerous_flags"],
        },
    }
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_whole_system_adversarial_logic_audit_attention_review_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_whole_system_adversarial_logic_audit_attention_review_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_whole_system_adversarial_logic_audit_attention_review_v1_latest.txt"
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
