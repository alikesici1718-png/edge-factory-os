from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_post_check_artifact_reliability_enforcement_readiness_review_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_post_check_artifact_reliability_enforcement_readiness_review_v1.py"
PRIOR_TOOL_REL = "tools/edge_factory_os_repo_only_post_check_artifact_reliability_enforcement_validator_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "f42cdba"
EXPECTED_TRACKED_PYTHON_COUNT = 568
EXPECTED_PREVIOUS_POST_CHECK = "REPO_ONLY_POST_CHECK_ARTIFACT_RELIABILITY_ENFORCEMENT_VALIDATOR_POST_COMMIT_CHECK_PASS"

NEXT_ACTION = "BUILD_REPO_ONLY_POST_CHECK_ARTIFACT_RELIABILITY_ENFORCEMENT_ADOPTION_RECORD_V1"
NEXT_MODULE = "edge_factory_os_repo_only_post_check_artifact_reliability_enforcement_adoption_record_v1.py"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "DERIVED_OVERUSED_ATTENTION"
POST_CHECK_STATUS = "REPO_ONLY_POST_CHECK_ARTIFACT_RELIABILITY_ENFORCEMENT_READINESS_REVIEW_POST_COMMIT_CHECK_PASS"

POLICY_ARTIFACT_JSON = LAB_ROOT / "edge_factory_os_repo_only_post_check_artifact_reliability_policy_v1" / "repo_only_post_check_artifact_reliability_policy_v1_latest.json"
POLICY_VALIDATOR_ARTIFACT_JSON = LAB_ROOT / "edge_factory_os_repo_only_post_check_artifact_reliability_policy_validator_v1" / "repo_only_post_check_artifact_reliability_policy_validator_v1_latest.json"
ENFORCEMENT_PLAN_ARTIFACT_JSON = LAB_ROOT / "edge_factory_os_repo_only_post_check_artifact_reliability_enforcement_plan_v1" / "repo_only_post_check_artifact_reliability_enforcement_plan_v1_latest.json"
ENFORCEMENT_VALIDATOR_ARTIFACT_JSON = LAB_ROOT / "edge_factory_os_repo_only_post_check_artifact_reliability_enforcement_validator_v1" / "repo_only_post_check_artifact_reliability_enforcement_validator_v1_latest.json"
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

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_post_check_artifact_reliability_enforcement_readiness_review": True,
    "future_modules_must_classify_evidence_quality": True,
    "replacement_checks_are_not_equivalent_to_primary_artifact": True,
    "full_post_check_marker_preferred_over_plain_pass": True,
    "plain_pass_without_marker_is_attention": True,
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


def validate_tracked_python() -> Dict[str, Any]:
    syntax_errors: List[Dict[str, str]] = []
    bom_errors: List[str] = []
    files = tracked_files("*.py")
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
    existing = planned_schema_existing_files()
    return {
        "planned_schema_files_existing": existing,
        "planned_schema_files_existing_count": len(existing),
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


def load_artifacts() -> Dict[str, Dict[str, Any]]:
    return {
        "policy": load_json(POLICY_ARTIFACT_JSON) if POLICY_ARTIFACT_JSON.exists() else {},
        "policy_validator": load_json(POLICY_VALIDATOR_ARTIFACT_JSON) if POLICY_VALIDATOR_ARTIFACT_JSON.exists() else {},
        "enforcement_plan": load_json(ENFORCEMENT_PLAN_ARTIFACT_JSON) if ENFORCEMENT_PLAN_ARTIFACT_JSON.exists() else {},
        "enforcement_validator": load_json(ENFORCEMENT_VALIDATOR_ARTIFACT_JSON) if ENFORCEMENT_VALIDATOR_ARTIFACT_JSON.exists() else {},
    }


def replacement_checks(git: Dict[str, Any], py: Dict[str, Any], physical: Dict[str, Any], artifacts: Dict[str, Dict[str, Any]], flags: Dict[str, bool]) -> Dict[str, bool]:
    expected_untracked = [CURRENT_TOOL_REL] if (REPO_ROOT / CURRENT_TOOL_REL).exists() else []
    policy = artifacts["policy"]
    policy_validator = artifacts["policy_validator"]
    plan = artifacts["enforcement_plan"]
    validator = artifacts["enforcement_validator"]
    return {
        "head_is_expected_enforcement_validator_commit": git["head"] == EXPECTED_HEAD,
        "repo_clean_before_writing_except_current_tool": git["dirty_tracked_count"] == 0 and git["untracked_paths"] == expected_untracked,
        "tracked_python_count_matches_previous": py["tracked_python_file_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "tracked_python_syntax_bom_clean": py["pass"] is True,
        "latest_commit_touched_only_enforcement_validator_module": latest_commit_paths() == [PRIOR_TOOL_REL],
        "policy_artifact_exists": bool(policy),
        "policy_validator_artifact_exists": bool(policy_validator),
        "enforcement_plan_artifact_exists": bool(plan),
        "enforcement_validator_artifact_exists": bool(validator),
        "policy_status_ready": policy.get("policy_status") == "READY",
        "policy_validator_ready": policy_validator.get("validator_status") == "READY",
        "enforcement_plan_ready": plan.get("enforcement_plan_status") == "READY",
        "enforcement_validator_ready": validator.get("enforcement_validator_status") == "READY",
        "previous_post_check_marker_matches": validator.get("post_check_status") == EXPECTED_PREVIOUS_POST_CHECK,
        "prior_next_module_matches_current": validator.get("next_module") == "edge_factory_os_repo_only_post_check_artifact_reliability_enforcement_readiness_review_v1.py",
        "evidence_chain_policy_level_active": validator.get("evidence_chain_policy_level") == POLICY_LEVEL,
        "current_evidence_chain_quality_expected": validator.get("current_evidence_chain_quality") == CURRENT_EVIDENCE_CHAIN_QUALITY,
        "future_modules_must_classify_evidence_quality": validator.get("future_modules_must_classify_evidence_quality") is True,
        "derived_weaker_than_primary": validator.get("derived_live_repo_post_check_weaker_than_primary") is True,
        "plain_pass_attention": validator.get("plain_pass_without_marker_attention") is True,
        "full_marker_preferred": validator.get("full_post_check_marker_preferred") is True,
        "replacement_checks_not_equivalent": validator.get("replacement_checks_are_not_equivalent_to_primary_artifact") is True,
        "missing_evidence_fail_closed": validator.get("missing_primary_artifact_must_not_silently_pass") is True,
        "generic_runner_approval_false": validator.get("generic_runner_approval_granted") is False,
        "generic_runner_implementation_blocked": validator.get("generic_runner_implementation_remains_blocked") is True,
        "ordinary_selector_backlog_loop_reentry_false": validator.get("ordinary_selector_backlog_loop_reentry_allowed") is False,
        "loop_remains_closed": validator.get("loop_remains_closed") is True,
        "planned_schema_files_existing_count_zero": physical["planned_schema_files_existing_count"] == 0,
        "generic_runner_target_absent": physical["generic_runner_target_exists"] is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()) and all(dangerous_flags_are_false(obj) for obj in artifacts.values()),
    }


def validate_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    git = git_state()
    py = validate_tracked_python()
    physical = physical_guard_snapshot()
    flags = danger_flags()
    artifacts = load_artifacts()
    checks = replacement_checks(git, py, physical, artifacts, flags)
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
    if not checks_all_true:
        errors.append(f"replacement checks not all true: {checks}")

    return {
        "errors": errors,
        "git_state": git,
        "tracked_python_validation": py,
        "physical": physical,
        "artifacts": artifacts,
        "dangerous_flags": flags,
        "replacement_checks": checks,
        "replacement_checks_all_true": checks_all_true,
    }


def build_payload(validation: Dict[str, Any]) -> Dict[str, Any]:
    errors = list(validation["errors"])
    artifacts = validation["artifacts"]
    validator = artifacts["enforcement_validator"]
    physical = validation["physical"]
    flags = validation["dangerous_flags"]

    policy_found = bool(artifacts["policy"])
    policy_validated = artifacts["policy_validator"].get("policy_validated") is True
    enforcement_plan_found = bool(artifacts["enforcement_plan"])
    enforcement_validator_passed = validator.get("enforcement_validator_status") == "READY"
    enforcement_readiness_confirmed = policy_found and policy_validated and enforcement_plan_found and enforcement_validator_passed and validation["replacement_checks_all_true"]
    full_marker_preferred = validator.get("full_post_check_marker_preferred") is True
    plain_pass_attention = validator.get("plain_pass_without_marker_attention") is True

    invariants = {
        "enforcement_readiness_confirmed": enforcement_readiness_confirmed,
        "next_module_exact": NEXT_MODULE == "edge_factory_os_repo_only_post_check_artifact_reliability_enforcement_adoption_record_v1.py",
        "full_post_check_marker_preferred_over_plain_pass": full_marker_preferred,
        "plain_pass_without_marker_is_attention": plain_pass_attention,
        "replacement_checks_all_true": validation["replacement_checks_all_true"],
    }
    for key, value in invariants.items():
        if value is not True:
            errors.append(f"invariant not true: {key}={value}")

    passed = not errors
    derived_reason = (
        "Readiness review uses the policy, policy-validator, enforcement-plan, and enforcement-validator artifacts "
        "plus explicit live repo replacement checks; DERIVED_OVERUSED_ATTENTION remains weaker than primary artifact verification."
    )
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "status": "REPO_ONLY_POST_CHECK_ARTIFACT_RELIABILITY_ENFORCEMENT_READINESS_REVIEW_V1_READY" if passed else "REPO_ONLY_POST_CHECK_ARTIFACT_RELIABILITY_ENFORCEMENT_READINESS_REVIEW_V1_BLOCKED",
        "readiness_review_status": "READY" if passed else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS if passed else "REPO_ONLY_POST_CHECK_ARTIFACT_RELIABILITY_ENFORCEMENT_READINESS_REVIEW_POST_COMMIT_CHECK_FAIL_CLOSED",
        "previous_confirmed_post_check": EXPECTED_PREVIOUS_POST_CHECK,
        "final_decision": "POST_CHECK_ARTIFACT_RELIABILITY_ENFORCEMENT_READY_FOR_ADOPTION" if passed else "POST_CHECK_ARTIFACT_RELIABILITY_ENFORCEMENT_READINESS_FAIL_CLOSED",
        "next_action": NEXT_ACTION if passed else "REVIEW_POST_CHECK_ARTIFACT_RELIABILITY_ENFORCEMENT_READINESS_ERRORS",
        "next_module": NEXT_MODULE if passed else None,
        "created_at_utc": now_utc(),
        "critical_issue_count": len(errors),
        "errors": errors,
        "policy_found": policy_found,
        "policy_validated": policy_validated,
        "enforcement_plan_found": enforcement_plan_found,
        "enforcement_validator_passed": enforcement_validator_passed,
        "enforcement_readiness_confirmed": enforcement_readiness_confirmed,
        "evidence_chain_policy_level": POLICY_LEVEL,
        "current_evidence_chain_quality": CURRENT_EVIDENCE_CHAIN_QUALITY,
        "allowed_evidence_chain_quality_values": ALLOWED_EVIDENCE_CHAIN_QUALITY_VALUES,
        "future_modules_must_classify_evidence_quality": True,
        "full_post_check_marker_preferred_over_plain_pass": full_marker_preferred,
        "plain_pass_without_marker_is_attention": plain_pass_attention,
        "primary_artifact_preferred": True,
        "exact_post_check_marker_preferred": True,
        "derived_live_repo_post_check_weaker_than_primary": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "missing_primary_artifact_must_not_silently_pass": True,
        "replacement_checks_must_be_explicit": True,
        "replacement_checks_all_true_required": True,
        "prior_enforcement_validator_respected": enforcement_validator_passed,
        "prior_enforcement_plan_respected": validator.get("prior_enforcement_plan_respected") is True,
        "prior_policy_respected": validator.get("prior_policy_respected") is True,
        "prior_loop_closure_respected": validator.get("prior_loop_closure_respected") is True,
        "human_decision_respected": validator.get("human_decision_respected") is True,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "generic_governance_loop_reopen_allowed": False,
        "loop_remains_closed": validator.get("loop_remains_closed") is True,
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
    latest_json = OUT_DIR / "repo_only_post_check_artifact_reliability_enforcement_readiness_review_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_post_check_artifact_reliability_enforcement_readiness_review_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_post_check_artifact_reliability_enforcement_readiness_review_v1_latest.txt"
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
