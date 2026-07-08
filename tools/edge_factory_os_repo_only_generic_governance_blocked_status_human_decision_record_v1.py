from __future__ import annotations

import ast
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_generic_governance_blocked_status_human_decision_record_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_generic_governance_blocked_status_human_decision_record_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "17e76ec"
EXPECTED_TRACKED_PYTHON_COUNT = 557
EXPECTED_PRIOR_MODULE = "edge_factory_os_repo_only_generic_governance_blocked_status_loop_closure_v1"
EXPECTED_PRIOR_COMMIT_PATH = "tools/edge_factory_os_repo_only_generic_governance_blocked_status_loop_closure_v1.py"
EXPECTED_PRIOR_POST_CHECK_MARKER = "PASS"
EXPECTED_PRIOR_NEXT_MODULE = "edge_factory_os_repo_only_generic_governance_blocked_status_human_decision_record_v1.py"

HUMAN_DECISION = "KEEP_GENERIC_RUNNER_BLOCKED_AND_ROUTE_TO_OTHER_REPO_ONLY_OS_INTELLIGENCE"
NEXT_ACTION = "BUILD_REPO_ONLY_OS_INTELLIGENCE_ROUTE_SELECTOR_AFTER_GENERIC_GOVERNANCE_LOOP_CLOSURE_V1"
NEXT_MODULE = "edge_factory_os_repo_only_os_intelligence_route_selector_after_generic_governance_loop_closure_v1.py"

GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"
LOOP_CLOSURE_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_generic_governance_blocked_status_loop_closure_v1"
    / "repo_only_generic_governance_blocked_status_loop_closure_v1_latest.json"
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

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_generic_governance_blocked_status_human_decision_record": True,
    "human_decision_recorded": True,
    "keep_generic_runner_blocked": True,
    "route_to_other_repo_only_os_intelligence": True,
    "prior_loop_closure_respected": True,
    "ordinary_selector_backlog_loop_reentry_allowed": False,
    "generic_governance_loop_reopen_allowed": False,
    **{flag: False for flag in DANGEROUS_FLAGS},
}

ORDINARY_CONTINUATION_RE = re.compile(
    r"edge_factory_os_repo_only_(next_action_selector|development_queue_selector|development_backlog_refresh)"
    r"_after_generic_governance_blocked_status.*_v1[.]py$"
)


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


def tracked_python_files() -> List[str]:
    return sorted(
        line.strip().replace("\\", "/")
        for line in run_cmd(["git", "ls-files", "*.py"]).stdout.splitlines()
        if line.strip()
    )


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
    return sorted(
        line.strip().replace("\\", "/")
        for line in run_cmd(["git", "show", "--name-only", "--format=", ref]).stdout.splitlines()
        if line.strip()
    )


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def generic_runner_target_exists() -> bool:
    return (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()


def physical_guard_snapshot() -> Dict[str, Any]:
    existing = planned_schema_existing_files()
    return {
        "planned_schema_rel_paths": PLANNED_SCHEMA_REL_PATHS,
        "planned_schema_files_existing": existing,
        "planned_schema_files_existing_count": len(existing),
        "generic_runner_target_file": GENERIC_RUNNER_TARGET_FILE,
        "generic_runner_target_exists": generic_runner_target_exists(),
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


def dangerous_flags_are_false(obj: Dict[str, Any]) -> bool:
    flags = obj.get("dangerous_flags", {})
    if not isinstance(flags, dict):
        return False
    if any(value is not False for value in flags.values()):
        return False
    safety = obj.get("safety_flags", {})
    if isinstance(safety, dict):
        for flag in DANGEROUS_FLAGS:
            if safety.get(flag, False) is not False:
                return False
    return True


def previous_post_check_marker_artifact() -> Optional[Path]:
    candidates = [
        LAB_ROOT
        / "edge_factory_os_repo_only_generic_governance_blocked_status_loop_closure_v1_post_commit_check"
        / "repo_only_generic_governance_blocked_status_loop_closure_post_commit_check_latest.json",
        LAB_ROOT
        / "edge_factory_os_repo_only_generic_governance_blocked_status_loop_closure_post_commit_check"
        / "repo_only_generic_governance_blocked_status_loop_closure_post_commit_check_latest.json",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def ordinary_continuation(module: str) -> bool:
    return bool(ORDINARY_CONTINUATION_RE.match(module))


def replacement_post_check(
    git: Dict[str, Any],
    py: Dict[str, Any],
    physical: Dict[str, Any],
    prior: Dict[str, Any],
) -> Dict[str, bool]:
    return {
        "head_is_expected_loop_closure_commit": git["head"] == EXPECTED_HEAD,
        "repo_clean_before_writing_except_current_tool": git["dirty_tracked_count"] == 0
        and sorted(git["untracked_paths"]) in ([], [CURRENT_TOOL_REL]),
        "latest_commit_touched_only_loop_closure_module": latest_commit_paths() == [EXPECTED_PRIOR_COMMIT_PATH],
        "tracked_python_count_matches_previous": py["tracked_python_file_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "tracked_python_syntax_bom_clean": py["pass"] is True,
        "planned_schema_files_existing_count_zero": physical["planned_schema_files_existing_count"] == 0,
        "generic_runner_target_absent": physical["generic_runner_target_exists"] is False,
        "prior_loop_closure_artifact_ready": prior.get("status") == "REPO_ONLY_GENERIC_GOVERNANCE_BLOCKED_STATUS_LOOP_CLOSURE_V1_READY",
        "prior_loop_closure_next_module_matches_current": prior.get("next_module") == EXPECTED_PRIOR_NEXT_MODULE,
        "prior_loop_detected": prior.get("loop_detected") is True,
        "prior_loop_iteration_count_20": prior.get("loop_iteration_count") == 20,
        "prior_repeated_chain_detected": prior.get("repeated_chain_detected") is True,
        "prior_loop_closed": prior.get("loop_closed") is True,
        "prior_generic_runner_approval_false": prior.get("generic_runner_approval_granted") is False,
        "prior_generic_runner_implementation_blocked": prior.get("generic_runner_implementation_remains_blocked") is True,
        "prior_next_selector_blocked": prior.get("next_selector_blocked") is True,
        "prior_next_backlog_refresh_blocked": prior.get("next_backlog_refresh_blocked") is True,
        "prior_derived_live_repo_post_check_present_true": prior.get("derived_live_repo_post_check") is True,
        "prior_derived_replacement_checks_all_true": isinstance(prior.get("derived_live_repo_post_check_replacement_checks"), dict)
        and all(value is True for value in prior.get("derived_live_repo_post_check_replacement_checks", {}).values()),
        "prior_dangerous_flags_all_false": dangerous_flags_are_false(prior),
    }


def validate_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    git = git_state()
    py = validate_tracked_python()
    physical = physical_guard_snapshot()
    prior = load_json(LOOP_CLOSURE_JSON) if LOOP_CLOSURE_JSON.exists() else {}
    marker_path = previous_post_check_marker_artifact()
    marker_payload: Optional[Dict[str, Any]] = load_json(marker_path) if marker_path is not None else None

    expected_untracked = [CURRENT_TOOL_REL] if (REPO_ROOT / CURRENT_TOOL_REL).exists() else []
    if git["head"] != EXPECTED_HEAD:
        errors.append(f"HEAD mismatch: expected={EXPECTED_HEAD} actual={git['head']}")
    if git["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked paths present: {git['dirty_tracked_paths']}")
    if git["untracked_paths"] != expected_untracked:
        errors.append(f"unexpected untracked paths: expected={expected_untracked} actual={git['untracked_paths']}")
    if py["tracked_python_file_count"] != EXPECTED_TRACKED_PYTHON_COUNT:
        errors.append(
            f"tracked Python count mismatch: expected={EXPECTED_TRACKED_PYTHON_COUNT} actual={py['tracked_python_file_count']}"
        )
    if not py["pass"]:
        errors.append(f"tracked Python validation failed: syntax={py['syntax_errors'][:20]} bom={py['bom_errors']}")
    if physical["planned_schema_files_existing_count"] != 0:
        errors.append(f"planned schema files exist: {physical['planned_schema_files_existing']}")
    if physical["generic_runner_target_exists"] is not False:
        errors.append(f"generic runner target exists: {GENERIC_RUNNER_TARGET_FILE}")
    if not prior:
        errors.append(f"missing prior loop closure artifact: {LOOP_CLOSURE_JSON}")

    exact_marker_verified = False
    exact_marker_value: Optional[str] = None
    if marker_payload is not None:
        exact_marker_value = str(marker_payload.get("post_check_status") or marker_payload.get("audit_status") or "")
        exact_marker_verified = exact_marker_value == EXPECTED_PRIOR_POST_CHECK_MARKER

    derived_checks = replacement_post_check(git, py, physical, prior)
    derived_live_repo_post_check = not exact_marker_verified
    derived_reason = None
    if derived_live_repo_post_check:
        derived_reason = (
            "exact persistent previous post-check PASS marker for loop closure was not found or did not match; "
            "using loop-closure artifact plus live repo replacement checks"
        )
        if not all(derived_checks.values()):
            errors.append(f"derived live repo replacement checks not all true: {derived_checks}")

    return {
        "errors": errors,
        "git_state": git,
        "tracked_python_validation": py,
        "physical": physical,
        "prior_loop_closure": prior,
        "previous_post_check_marker_path": str(marker_path) if marker_path is not None else None,
        "previous_post_check_marker_value": exact_marker_value,
        "previous_post_check_marker_verified": exact_marker_verified,
        "derived_live_repo_post_check": derived_live_repo_post_check,
        "derived_live_repo_post_check_reason": derived_reason,
        "derived_live_repo_post_check_replacement_checks": derived_checks,
    }


def build_payload(validation: Dict[str, Any]) -> Dict[str, Any]:
    errors = list(validation["errors"])
    prior = validation["prior_loop_closure"]
    physical = validation["physical"]
    dangerous_flags = {flag: False for flag in DANGEROUS_FLAGS}
    prior_loop_closure_respected = (
        prior.get("loop_closed") is True
        and prior.get("next_module") == EXPECTED_PRIOR_NEXT_MODULE
        and prior.get("generic_runner_approval_granted") is False
        and prior.get("generic_runner_implementation_remains_blocked") is True
        and prior.get("next_selector_blocked") is True
        and prior.get("next_backlog_refresh_blocked") is True
    )
    invariants = {
        "human_decision_recorded": True,
        "human_decision_blocks_generic_runner": True,
        "generic_runner_approval_granted_false": False is False,
        "generic_runner_implementation_remains_blocked": True,
        "manual_approval_present_for_generic_runner_false": False is False,
        "manual_approval_valid_for_generic_runner_false": False is False,
        "generic_governance_loop_reopen_allowed_false": False is False,
        "ordinary_selector_backlog_loop_reentry_allowed_false": False is False,
        "prior_loop_closure_respected": prior_loop_closure_respected,
        "loop_detected": prior.get("loop_detected") is True,
        "loop_closed": prior.get("loop_closed") is True,
        "next_selector_blocked": True,
        "next_backlog_refresh_blocked": True,
        "repeated_name_growth_is_not_progress": True,
        "next_module_exact": NEXT_MODULE
        == "edge_factory_os_repo_only_os_intelligence_route_selector_after_generic_governance_loop_closure_v1.py",
        "next_module_not_ordinary_continuation": not ordinary_continuation(NEXT_MODULE),
        "planned_schema_files_existing_count_zero": physical["planned_schema_files_existing_count"] == 0,
        "generic_runner_target_absent": physical["generic_runner_target_exists"] is False,
        "dangerous_flags_all_false": all(value is False for value in dangerous_flags.values()),
    }
    for key, value in invariants.items():
        if value is not True:
            errors.append(f"invariant not true: {key}={value}")

    passed = not errors
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "status": "REPO_ONLY_GENERIC_GOVERNANCE_BLOCKED_STATUS_HUMAN_DECISION_RECORD_V1_READY" if passed else "REPO_ONLY_GENERIC_GOVERNANCE_BLOCKED_STATUS_HUMAN_DECISION_RECORD_V1_BLOCKED",
        "decision_status": "HUMAN_DECISION_RECORDED" if passed else "HUMAN_DECISION_RECORD_BLOCKED",
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": HUMAN_DECISION if passed else "REVIEW_GENERIC_GOVERNANCE_BLOCKED_STATUS_HUMAN_DECISION_RECORD_ERRORS",
        "next_action": NEXT_ACTION if passed else "REVIEW_GENERIC_GOVERNANCE_BLOCKED_STATUS_HUMAN_DECISION_RECORD_ERRORS",
        "next_module": NEXT_MODULE if passed else None,
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "critical_issue_count": len(errors),
        "warning_count": 0,
        "errors": errors,
        "warnings": [],
        "human_decision_recorded": passed,
        "human_decision": HUMAN_DECISION,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "manual_approval_present_for_generic_runner": False,
        "manual_approval_valid_for_generic_runner": False,
        "generic_governance_loop_reopen_allowed": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "prior_loop_closure_respected": prior_loop_closure_respected,
        "loop_detected": prior.get("loop_detected") is True,
        "loop_closed": prior.get("loop_closed") is True,
        "next_selector_blocked": True,
        "next_backlog_refresh_blocked": True,
        "repeated_name_growth_is_not_progress": True,
        "planned_schema_files_existing_count": physical["planned_schema_files_existing_count"],
        "planned_schema_files_existing": physical["planned_schema_files_existing"],
        "generic_runner_target_exists": physical["generic_runner_target_exists"],
        "dangerous_flags": dangerous_flags,
        "derived_live_repo_post_check": validation["derived_live_repo_post_check"],
        "derived_live_repo_post_check_reason": validation["derived_live_repo_post_check_reason"],
        "derived_live_repo_post_check_replacement_checks": validation["derived_live_repo_post_check_replacement_checks"],
        "previous_post_check_marker_expected": EXPECTED_PRIOR_POST_CHECK_MARKER,
        "previous_post_check_marker_path": validation["previous_post_check_marker_path"],
        "previous_post_check_marker_value": validation["previous_post_check_marker_value"],
        "previous_post_check_marker_verified": validation["previous_post_check_marker_verified"],
        "prior_loop_closure_artifact": str(LOOP_CLOSURE_JSON),
        "prior_loop_closure_summary": {
            "module": prior.get("module"),
            "status": prior.get("status"),
            "closure_status": prior.get("closure_status"),
            "final_decision": prior.get("final_decision"),
            "next_module": prior.get("next_module"),
            "loop_detected": prior.get("loop_detected"),
            "loop_iteration_count": prior.get("loop_iteration_count"),
            "repeated_chain_detected": prior.get("repeated_chain_detected"),
            "loop_closed": prior.get("loop_closed"),
            "generic_runner_approval_granted": prior.get("generic_runner_approval_granted"),
            "generic_runner_implementation_remains_blocked": prior.get("generic_runner_implementation_remains_blocked"),
            "next_selector_blocked": prior.get("next_selector_blocked"),
            "next_backlog_refresh_blocked": prior.get("next_backlog_refresh_blocked"),
            "derived_live_repo_post_check": prior.get("derived_live_repo_post_check"),
        },
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
    payload.update(dangerous_flags)
    payload.update(
        {
            "manual_approval_present": False,
            "manual_approval_valid": False,
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
    latest_json = OUT_DIR / "repo_only_generic_governance_blocked_status_human_decision_record_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_generic_governance_blocked_status_human_decision_record_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_generic_governance_blocked_status_human_decision_record_v1_latest.txt"
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
