from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_post_check_artifact_reliability_enforcement_validator_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_post_check_artifact_reliability_enforcement_validator_v1.py"
ENFORCEMENT_PLAN_TOOL_REL = "tools/edge_factory_os_repo_only_post_check_artifact_reliability_enforcement_plan_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "14b4ee2"
EXPECTED_TRACKED_PYTHON_COUNT = 567
EXPECTED_PREVIOUS_POST_CHECK = "REPO_ONLY_POST_CHECK_ARTIFACT_RELIABILITY_ENFORCEMENT_PLAN_POST_COMMIT_CHECK_PASS"

NEXT_ACTION = "BUILD_REPO_ONLY_POST_CHECK_ARTIFACT_RELIABILITY_ENFORCEMENT_READINESS_REVIEW_V1"
NEXT_MODULE = "edge_factory_os_repo_only_post_check_artifact_reliability_enforcement_readiness_review_v1.py"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "DERIVED_OVERUSED_ATTENTION"
POST_CHECK_STATUS = "REPO_ONLY_POST_CHECK_ARTIFACT_RELIABILITY_ENFORCEMENT_VALIDATOR_POST_COMMIT_CHECK_PASS"

ENFORCEMENT_PLAN_ARTIFACT_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_post_check_artifact_reliability_enforcement_plan_v1"
    / "repo_only_post_check_artifact_reliability_enforcement_plan_v1_latest.json"
)
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

ALLOWED_EVIDENCE_CHAIN_QUALITY_VALUES = [
    "PRIMARY_ARTIFACT_STRONG",
    "EXACT_MARKER_STRONG",
    "DERIVED_EXPLICIT_ATTENTION",
    "DERIVED_OVERUSED_ATTENTION",
    "MISSING_EVIDENCE_FAIL_CLOSED",
]

REQUIRED_ENFORCEMENT_STEPS = [
    "require_evidence_chain_quality",
    "prefer_primary_artifact",
    "prefer_exact_marker",
    "constrain_derived_live_repo_post_check",
    "classify_derived_as_weaker",
    "keep_overuse_attention",
    "block_missing_primary_silent_pass",
    "preserve_closed_generic_governance_loop",
]

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_post_check_artifact_reliability_enforcement_validator": True,
    "prior_enforcement_plan_respected": True,
    "prior_policy_respected": True,
    "prior_loop_closure_respected": True,
    "human_decision_respected": True,
    "repeated_name_growth_is_not_progress": True,
    "future_modules_must_classify_evidence_quality": True,
    "derived_live_repo_post_check_weaker_than_primary": True,
    "replacement_checks_are_not_equivalent_to_primary_artifact": True,
    "ordinary_selector_backlog_loop_reentry_allowed": False,
    "generic_governance_loop_reopen_allowed": False,
    "generic_runner_implementation_remains_blocked": True,
    **{flag: False for flag in DANGEROUS_FLAGS},
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


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git_state() -> Dict[str, Any]:
    status_lines = [
        line
        for line in run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"]).stdout.splitlines()
        if line.strip()
    ]
    untracked = [line[3:].replace("\\", "/") for line in status_lines if line.startswith("?? ")]
    dirty_tracked = [line for line in status_lines if not line.startswith("?? ")]
    staged = [line for line in dirty_tracked if line[0] != " "]
    return {
        "head": run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
        "branch": run_cmd(["git", "branch", "--show-current"]).stdout.strip(),
        "status_porcelain": status_lines,
        "dirty_tracked_count": len(dirty_tracked),
        "dirty_tracked_paths": [line[3:].replace("\\", "/") for line in dirty_tracked],
        "staged_count": len(staged),
        "staged_paths": [line[3:].replace("\\", "/") for line in staged],
        "untracked_count": len(untracked),
        "untracked_paths": sorted(untracked),
        "git_dirty": bool(status_lines),
    }


def tracked_files(pattern: str) -> List[str]:
    return sorted(line.strip().replace("\\", "/") for line in run_cmd(["git", "ls-files", pattern]).stdout.splitlines() if line.strip())


def tracked_python_files() -> List[str]:
    return tracked_files("*.py")


def validate_tracked_python() -> Dict[str, Any]:
    syntax_errors: List[Dict[str, str]] = []
    bom_errors: List[str] = []
    files = tracked_python_files()
    for rel in files:
        path = REPO_ROOT / rel
        try:
            data = path.read_bytes()
            if data.startswith(b"\xef\xbb\xbf"):
                bom_errors.append(rel)
            ast.parse(data.decode("utf-8"), filename=rel)
        except Exception as exc:
            syntax_errors.append({"path": rel, "error": repr(exc)})
    return {
        "tracked_python_file_count": len(files),
        "syntax_error_count": len(syntax_errors),
        "bom_error_count": len(bom_errors),
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
        "pass": not syntax_errors and not bom_errors,
    }


def latest_commit_paths(ref: str = "HEAD") -> List[str]:
    return sorted(line.strip().replace("\\", "/") for line in run_cmd(["git", "show", "--name-only", "--format=", ref]).stdout.splitlines() if line.strip())


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def physical_guard_snapshot() -> Dict[str, Any]:
    planned_existing = planned_schema_existing_files()
    return {
        "planned_schema_files_existing": planned_existing,
        "planned_schema_files_existing_count": len(planned_existing),
        "generic_runner_target_file": GENERIC_RUNNER_TARGET_FILE,
        "generic_runner_target_exists": (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists(),
        "runtime_touch_performed": False,
        "launcher_executed": False,
        "capital_change_performed": False,
        "live_or_real_order_performed": False,
        "holdout_access_performed": False,
        "candidate_generation_performed": False,
        "family_release_performed": False,
        "strategy_research_performed": False,
        "schema_file_creation_performed": False,
        "schema_file_edit_performed": False,
        "generic_runner_file_creation_performed": False,
        "config_file_creation_performed": False,
    }


def danger_flags() -> Dict[str, bool]:
    return {flag: False for flag in DANGEROUS_FLAGS}


def dangerous_flags_are_false(obj: Dict[str, Any]) -> bool:
    flags = obj.get("dangerous_flags")
    return isinstance(flags, dict) and all(value is False for value in flags.values())


def enforcement_steps_complete(plan: Dict[str, Any]) -> bool:
    items = plan.get("enforcement_plan")
    if not isinstance(items, list):
        return False
    steps = [item.get("step") for item in items if isinstance(item, dict)]
    return steps == REQUIRED_ENFORCEMENT_STEPS and all(item.get("fail_closed_if_missing") is True for item in items)


def plan_internals(plan: Dict[str, Any]) -> Dict[str, bool]:
    return {
        "enforcement_plan_status_ready": plan.get("enforcement_plan_status") == "READY",
        "post_check_marker_full": plan.get("post_check_status") == EXPECTED_PREVIOUS_POST_CHECK,
        "evidence_chain_policy_level": plan.get("evidence_chain_policy_level") == POLICY_LEVEL,
        "current_evidence_chain_quality": plan.get("current_evidence_chain_quality") == CURRENT_EVIDENCE_CHAIN_QUALITY,
        "allowed_evidence_chain_quality_values_exact": plan.get("allowed_evidence_chain_quality_values") == ALLOWED_EVIDENCE_CHAIN_QUALITY_VALUES,
        "future_modules_must_classify_evidence_quality": plan.get("future_modules_must_classify_evidence_quality") is True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": plan.get("replacement_checks_are_not_equivalent_to_primary_artifact") is True,
        "derived_live_repo_post_check_weaker_than_primary": plan.get("derived_live_repo_post_check_weaker_than_primary") is True,
        "missing_primary_artifact_must_not_silently_pass": plan.get("missing_primary_artifact_must_not_silently_pass") is True,
        "full_post_check_marker_preferred": plan.get("full_post_check_marker_preferred") is True,
        "plain_pass_without_marker_attention": plan.get("plain_pass_without_marker_attention") is True,
        "derived_overuse_attention": plan.get("derived_live_repo_post_check_overuse_attention") is True,
        "prior_policy_respected": plan.get("prior_policy_respected") is True,
        "prior_loop_closure_respected": plan.get("prior_loop_closure_respected") is True,
        "human_decision_respected": plan.get("human_decision_respected") is True,
        "generic_runner_approval_false": plan.get("generic_runner_approval_granted") is False,
        "generic_runner_implementation_blocked": plan.get("generic_runner_implementation_remains_blocked") is True,
        "ordinary_selector_backlog_loop_reentry_false": plan.get("ordinary_selector_backlog_loop_reentry_allowed") is False,
        "loop_remains_closed": plan.get("loop_remains_closed") is True,
        "next_module_matches_current": plan.get("next_module") == "edge_factory_os_repo_only_post_check_artifact_reliability_enforcement_validator_v1.py",
        "derived_live_repo_post_check_present": plan.get("derived_live_repo_post_check") is True,
        "derived_live_repo_post_check_reason_present": isinstance(plan.get("derived_live_repo_post_check_reason"), str)
        and bool(plan.get("derived_live_repo_post_check_reason")),
        "replacement_checks_all_true": plan.get("replacement_checks_all_true") is True,
        "enforcement_steps_complete": enforcement_steps_complete(plan),
        "plan_dangerous_flags_all_false": dangerous_flags_are_false(plan),
    }


def replacement_checks(git: Dict[str, Any], py: Dict[str, Any], physical: Dict[str, Any], plan: Dict[str, Any], flags: Dict[str, bool]) -> Dict[str, bool]:
    expected_untracked = [CURRENT_TOOL_REL] if (REPO_ROOT / CURRENT_TOOL_REL).exists() else []
    internals = plan_internals(plan)
    return {
        "head_is_expected_enforcement_plan_commit": git["head"] == EXPECTED_HEAD,
        "repo_clean_before_writing_except_current_tool": git["dirty_tracked_count"] == 0 and git["untracked_paths"] == expected_untracked,
        "tracked_python_count_matches_previous": py["tracked_python_file_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "tracked_python_syntax_bom_clean": py["pass"] is True,
        "latest_commit_touched_only_enforcement_plan_module": latest_commit_paths() == [ENFORCEMENT_PLAN_TOOL_REL],
        "enforcement_plan_artifact_exists": ENFORCEMENT_PLAN_ARTIFACT_JSON.exists(),
        "enforcement_plan_internal_checks_all_true": bool(internals) and all(value is True for value in internals.values()),
        "planned_schema_files_existing_count_zero": physical["planned_schema_files_existing_count"] == 0,
        "generic_runner_target_absent": physical["generic_runner_target_exists"] is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()) and dangerous_flags_are_false(plan),
    }


def validate_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    git = git_state()
    py = validate_tracked_python()
    physical = physical_guard_snapshot()
    flags = danger_flags()
    plan = load_json(ENFORCEMENT_PLAN_ARTIFACT_JSON) if ENFORCEMENT_PLAN_ARTIFACT_JSON.exists() else {}
    internals = plan_internals(plan) if plan else {}
    checks = replacement_checks(git, py, physical, plan, flags)
    checks_all_true = bool(checks) and all(value is True for value in checks.values())

    if git["head"] != EXPECTED_HEAD:
        errors.append(f"HEAD mismatch: expected={EXPECTED_HEAD} actual={git['head']}")
    if git["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked paths present: {git['dirty_tracked_paths']}")
    expected_untracked = [CURRENT_TOOL_REL] if (REPO_ROOT / CURRENT_TOOL_REL).exists() else []
    if git["untracked_paths"] != expected_untracked:
        errors.append(f"unexpected untracked paths: expected={expected_untracked} actual={git['untracked_paths']}")
    if py["tracked_python_file_count"] != EXPECTED_TRACKED_PYTHON_COUNT:
        errors.append(f"tracked Python count mismatch: expected={EXPECTED_TRACKED_PYTHON_COUNT} actual={py['tracked_python_file_count']}")
    if not py["pass"]:
        errors.append(f"tracked Python validation failed: syntax={py['syntax_errors'][:20]} bom={py['bom_errors']}")
    if physical["planned_schema_files_existing_count"] != 0:
        errors.append(f"planned schema files exist: {physical['planned_schema_files_existing']}")
    if physical["generic_runner_target_exists"] is not False:
        errors.append(f"generic runner target exists: {GENERIC_RUNNER_TARGET_FILE}")
    if not plan:
        errors.append(f"missing enforcement plan artifact: {ENFORCEMENT_PLAN_ARTIFACT_JSON}")
    for key, value in internals.items():
        if value is not True:
            errors.append(f"plan invariant not true: {key}={value}")
    if not checks_all_true:
        errors.append(f"replacement checks not all true: {checks}")

    return {
        "errors": errors,
        "git_state": git,
        "tracked_python_validation": py,
        "physical": physical,
        "enforcement_plan": plan,
        "plan_internals": internals,
        "dangerous_flags": flags,
        "replacement_checks": checks,
        "replacement_checks_all_true": checks_all_true,
    }


def build_payload(validation: Dict[str, Any]) -> Dict[str, Any]:
    errors = list(validation["errors"])
    plan = validation["enforcement_plan"]
    physical = validation["physical"]
    flags = validation["dangerous_flags"]

    prior_enforcement_plan_respected = (
        plan.get("enforcement_plan_status") == "READY"
        and plan.get("next_module") == "edge_factory_os_repo_only_post_check_artifact_reliability_enforcement_validator_v1.py"
        and validation["replacement_checks_all_true"] is True
    )
    invariants = {
        "prior_enforcement_plan_respected": prior_enforcement_plan_respected,
        "evidence_chain_policy_level": plan.get("evidence_chain_policy_level") == POLICY_LEVEL,
        "current_evidence_chain_quality": plan.get("current_evidence_chain_quality") == CURRENT_EVIDENCE_CHAIN_QUALITY,
        "future_modules_must_classify_evidence_quality": plan.get("future_modules_must_classify_evidence_quality") is True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": plan.get("replacement_checks_are_not_equivalent_to_primary_artifact") is True,
        "generic_runner_approval_false": plan.get("generic_runner_approval_granted") is False,
        "generic_runner_implementation_blocked": plan.get("generic_runner_implementation_remains_blocked") is True,
        "ordinary_selector_backlog_loop_reentry_false": plan.get("ordinary_selector_backlog_loop_reentry_allowed") is False,
        "loop_remains_closed": plan.get("loop_remains_closed") is True,
        "planned_schema_files_existing_count_zero": physical["planned_schema_files_existing_count"] == 0,
        "generic_runner_target_absent": physical["generic_runner_target_exists"] is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "replacement_checks_all_true": validation["replacement_checks_all_true"],
    }
    for key, value in invariants.items():
        if value is not True:
            errors.append(f"invariant not true: {key}={value}")

    passed = not errors
    derived_reason = (
        "Enforcement validator uses the enforcement-plan artifact plus explicit live repo replacement checks; "
        "it confirms DERIVED_OVERUSED_ATTENTION remains weaker than primary artifact verification."
    )
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "status": "REPO_ONLY_POST_CHECK_ARTIFACT_RELIABILITY_ENFORCEMENT_VALIDATOR_V1_READY" if passed else "REPO_ONLY_POST_CHECK_ARTIFACT_RELIABILITY_ENFORCEMENT_VALIDATOR_V1_BLOCKED",
        "enforcement_validator_status": "READY" if passed else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS if passed else "REPO_ONLY_POST_CHECK_ARTIFACT_RELIABILITY_ENFORCEMENT_VALIDATOR_POST_COMMIT_CHECK_FAIL_CLOSED",
        "previous_confirmed_post_check": EXPECTED_PREVIOUS_POST_CHECK,
        "severity": "ATTENTION" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": "POST_CHECK_ARTIFACT_RELIABILITY_ENFORCEMENT_VALIDATED" if passed else "POST_CHECK_ARTIFACT_RELIABILITY_ENFORCEMENT_VALIDATOR_FAIL_CLOSED",
        "next_action": NEXT_ACTION if passed else "REVIEW_POST_CHECK_ARTIFACT_RELIABILITY_ENFORCEMENT_VALIDATOR_ERRORS",
        "next_module": NEXT_MODULE if passed else None,
        "created_at_utc": now_utc(),
        "critical_issue_count": len(errors),
        "warning_count": 1 if passed else 0,
        "errors": errors,
        "warnings": ["batch stop after this second module; no third module is authorized"] if passed else [],
        "evidence_chain_policy_level": POLICY_LEVEL,
        "current_evidence_chain_quality": CURRENT_EVIDENCE_CHAIN_QUALITY,
        "allowed_evidence_chain_quality_values": ALLOWED_EVIDENCE_CHAIN_QUALITY_VALUES,
        "enforcement_validated": passed,
        "prior_enforcement_plan_respected": prior_enforcement_plan_respected,
        "future_modules_must_classify_evidence_quality": plan.get("future_modules_must_classify_evidence_quality") is True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": plan.get("replacement_checks_are_not_equivalent_to_primary_artifact") is True,
        "primary_artifact_preferred": plan.get("primary_artifact_preferred") is True,
        "exact_post_check_marker_preferred": plan.get("exact_post_check_marker_preferred") is True,
        "derived_live_repo_post_check_weaker_than_primary": plan.get("derived_live_repo_post_check_weaker_than_primary") is True,
        "missing_primary_artifact_must_not_silently_pass": plan.get("missing_primary_artifact_must_not_silently_pass") is True,
        "full_post_check_marker_preferred": plan.get("full_post_check_marker_preferred") is True,
        "plain_pass_without_marker_attention": plan.get("plain_pass_without_marker_attention") is True,
        "derived_live_repo_post_check_recent_count": plan.get("derived_live_repo_post_check_recent_count"),
        "exact_post_check_marker_recent_count": plan.get("exact_post_check_marker_recent_count"),
        "derived_live_repo_post_check_overuse_attention": plan.get("derived_live_repo_post_check_overuse_attention") is True,
        "prior_policy_respected": plan.get("prior_policy_respected") is True,
        "prior_loop_closure_respected": plan.get("prior_loop_closure_respected") is True,
        "human_decision_respected": plan.get("human_decision_respected") is True,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "generic_governance_loop_reopen_allowed": False,
        "loop_remains_closed": plan.get("loop_remains_closed") is True,
        "repeated_name_growth_is_not_progress": True,
        "planned_schema_files_existing_count": physical["planned_schema_files_existing_count"],
        "planned_schema_files_existing": physical["planned_schema_files_existing"],
        "generic_runner_target_exists": physical["generic_runner_target_exists"],
        "dangerous_flags": flags,
        "derived_live_repo_post_check": True,
        "derived_live_repo_post_check_reason": derived_reason,
        "replacement_checks_all_true": validation["replacement_checks_all_true"],
        "derived_live_repo_post_check_replacement_checks": validation["replacement_checks"],
        "validation": {
            "git_state": validation["git_state"],
            "tracked_python_validation": validation["tracked_python_validation"],
            "physical": physical,
            "plan_internals": validation["plan_internals"],
            "invariants": invariants,
        },
        "safety_flags": SAFETY_FLAGS,
        "stage_recommended_now": False,
        "commit_recommended_now": False,
    }
    payload.update(flags)
    payload.update(
        {
            "manual_approval_present": False,
            "manual_approval_valid": False,
            "manual_approval_present_for_generic_runner": False,
            "manual_approval_valid_for_generic_runner": False,
            "approval_inferred_or_guessed": False,
            "implementation_allowed_now": False,
            "generic_runner_implementation_allowed_now": False,
            "schema_creation_allowed_now": False,
            "schema_edit_allowed_now": False,
            "runtime_touch_allowed_now": False,
            "generic_runner_file_creation_performed": False,
            "config_file_creation_performed": False,
            "schema_file_creation_performed": False,
            "schema_file_edit_performed": False,
            "runtime_touch_performed": False,
            "capital_change_performed": False,
            "live_or_real_order_performed": False,
            "holdout_access_performed": False,
        }
    )
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_post_check_artifact_reliability_enforcement_validator_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_post_check_artifact_reliability_enforcement_validator_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_post_check_artifact_reliability_enforcement_validator_v1_latest.txt"
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    latest_json.write_text(rendered, encoding="utf-8")
    timestamped_json.write_text(rendered, encoding="utf-8")
    latest_txt.write_text(rendered + "\n", encoding="utf-8")
    return {"latest_json": str(latest_json), "timestamped_json": str(timestamped_json), "latest_txt": str(latest_txt)}


def main() -> int:
    validation = validate_inputs()
    payload = build_payload(validation)
    outputs = write_outputs(payload)
    payload["outputs"] = outputs
    Path(outputs["latest_json"]).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["critical_issue_count"] == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
