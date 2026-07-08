from __future__ import annotations

import ast
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_generic_governance_blocked_status_loop_closure_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_generic_governance_blocked_status_loop_closure_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "fa26144"
EXPECTED_TRACKED_PYTHON_COUNT = 556
EXPECTED_PREVIOUS_POST_CHECK_STATUS = (
    "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_"
    "BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_POST_COMMIT_CHECK_PASS"
)
PREVIOUS_ORDINARY_NEXT_MODULE = (
    "edge_factory_os_repo_only_development_backlog_refresh_after_generic_governance_blocked_status_"
    "backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_v1.py"
)
NEXT_MODULE = "edge_factory_os_repo_only_generic_governance_blocked_status_human_decision_record_v1.py"
NEXT_ACTION = "BUILD_REPO_ONLY_GENERIC_GOVERNANCE_BLOCKED_STATUS_HUMAN_DECISION_RECORD_V1"

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

SAFE_TRUE_FLAGS: Dict[str, bool] = {
    "repo_only_generic_governance_blocked_status_loop_closure": True,
    "loop_closure_record_only": True,
    "external_adversarial_audit_loop_confirmed": True,
    "previous_next_module_superseded_by_human_decision": True,
    "human_decision_record_selected_next": True,
    "generic_runner_implementation_remains_blocked": True,
    "manual_approval_remains_absent_invalid": True,
    "repeated_name_growth_is_not_progress": True,
    "next_selector_blocked": True,
    "next_backlog_refresh_blocked": True,
}
SAFETY_FLAGS: Dict[str, bool] = {**SAFE_TRUE_FLAGS, **{flag: False for flag in DANGEROUS_FLAGS}}

LOOP_FILE_RE = re.compile(
    r"^tools/edge_factory_os_repo_only_"
    r"(?P<kind>next_action_selector|development_queue_selector|development_backlog_refresh)"
    r"_after_generic_governance_blocked_status(?P<suffix>.*)_v1[.]py$"
)
ORDINARY_CONTINUATION_RE = re.compile(
    r"edge_factory_os_repo_only_"
    r"(next_action_selector|development_queue_selector|development_backlog_refresh)"
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


def validate_python_files(files: List[str]) -> Dict[str, Any]:
    syntax_errors: List[Dict[str, str]] = []
    bom_errors: List[str] = []
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


def recent_commit_subjects(limit: int = 30) -> List[str]:
    return [
        line.strip()
        for line in run_cmd(["git", "log", f"--max-count={limit}", "--pretty=%h %s", "--", "tools"]).stdout.splitlines()
        if line.strip()
    ]


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def generic_runner_target_exists() -> bool:
    return (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()


def physical_guard_snapshot() -> Dict[str, Any]:
    existing_schema_files = planned_schema_existing_files()
    return {
        "planned_schema_rel_paths": PLANNED_SCHEMA_REL_PATHS,
        "planned_schema_files_existing": existing_schema_files,
        "planned_schema_files_existing_count": len(existing_schema_files),
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
    }


def loop_matching_files() -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for rel in tracked_files("tools/*.py"):
        match = LOOP_FILE_RE.match(rel)
        if not match:
            continue
        suffix = match.group("suffix")
        records.append(
            {
                "path": rel,
                "module": Path(rel).name,
                "kind": match.group("kind"),
                "suffix": suffix,
                "backlog_status_token_count": suffix.count("backlog_status"),
                "has_backlog_refresh_suffix": suffix.endswith("_backlog_refresh"),
            }
        )
    return sorted(records, key=lambda item: (item["backlog_status_token_count"], item["kind"], item["path"]))


def recent_loop_commits(subjects: List[str]) -> List[str]:
    markers = [
        "next action selector after generic governance blocked status",
        "development queue selector after generic governance blocked status",
        "development backlog refresh after generic governance blocked status",
    ]
    return [subject for subject in subjects if any(marker in subject for marker in markers)]


def detect_loop(files: List[Dict[str, Any]], subjects: List[str]) -> Dict[str, Any]:
    kind_counts = Counter(str(item["kind"]) for item in files)
    suffix_counts = Counter(str(item["suffix"]) for item in files)
    max_suffix_depth = max((int(item["backlog_status_token_count"]) for item in files), default=0)
    recent_loop = recent_loop_commits(subjects)
    repeated_chain_detected = (
        len(files) >= 9
        and all(kind_counts.get(kind, 0) >= 5 for kind in ["next_action_selector", "development_queue_selector", "development_backlog_refresh"])
        and max_suffix_depth >= 4
        and len(recent_loop) >= 9
    )
    return {
        "matching_file_count": len(files),
        "kind_counts": dict(sorted(kind_counts.items())),
        "suffix_counts": dict(sorted(suffix_counts.items())),
        "max_backlog_status_suffix_depth": max_suffix_depth,
        "recent_matching_commit_count": len(recent_loop),
        "recent_matching_commits": recent_loop,
        "repeated_chain_detected": repeated_chain_detected,
        "loop_detected": repeated_chain_detected,
        "loop_iteration_count": len(files),
        "pattern": "next_action_selector -> development_queue_selector -> development_backlog_refresh with repeated backlog_status name growth",
    }


def prior_post_check_candidates() -> List[Path]:
    stem = (
        "repo_only_development_queue_selector_after_generic_governance_blocked_status_"
        "backlog_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh"
    )
    dirs = [
        "edge_factory_os_repo_only_development_queue_selector_after_generic_governance_blocked_status_"
        "backlog_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_post_commit_check",
        "edge_factory_os_repo_only_development_queue_selector_after_generic_governance_blocked_status_"
        "backlog_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_v1_post_commit_check",
    ]
    return [LAB_ROOT / directory / f"{stem}_post_commit_check_latest.json" for directory in dirs]


def load_prior_post_check() -> Tuple[Optional[Dict[str, Any]], List[str]]:
    missing: List[str] = []
    for path in prior_post_check_candidates():
        if not path.exists():
            missing.append(str(path))
            continue
        return json.loads(path.read_text(encoding="utf-8")), missing
    return None, missing


def replacement_post_check(git: Dict[str, Any], py: Dict[str, Any], physical: Dict[str, Any], loop: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "head_is_expected": git["head"] == EXPECTED_HEAD,
        "repo_clean_before_writing_except_current_tool": git["dirty_tracked_count"] == 0
        and sorted(git["untracked_paths"]) in ([], [CURRENT_TOOL_REL]),
        "latest_commit_touched_previous_queue_selector": latest_commit_paths() == [
            "tools/edge_factory_os_repo_only_development_queue_selector_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_v1.py"
        ],
        "tracked_python_count_matches_previous": py["tracked_python_file_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "tracked_python_syntax_bom_clean": py["pass"] is True,
        "planned_schema_files_existing_count_zero": physical["planned_schema_files_existing_count"] == 0,
        "generic_runner_target_absent": physical["generic_runner_target_exists"] is False,
        "dangerous_flags_all_false": all(SAFETY_FLAGS.get(flag) is False for flag in DANGEROUS_FLAGS),
        "loop_detected_from_tracked_files_and_recent_commits": loop["loop_detected"] is True,
    }


def ordinary_chain_continuation(module: str) -> bool:
    return bool(ORDINARY_CONTINUATION_RE.match(module))


def validate_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    git = git_state()
    python_files = tracked_python_files()
    python_validation = validate_python_files(python_files)
    physical = physical_guard_snapshot()
    subjects = recent_commit_subjects()
    files = loop_matching_files()
    loop = detect_loop(files, subjects)
    prior_post, missing_prior_paths = load_prior_post_check()

    expected_untracked = [CURRENT_TOOL_REL] if (REPO_ROOT / CURRENT_TOOL_REL).exists() else []
    if git["head"] != EXPECTED_HEAD:
        errors.append(f"HEAD mismatch: expected={EXPECTED_HEAD} actual={git['head']}")
    if git["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked paths present: {git['dirty_tracked_paths']}")
    if git["untracked_paths"] != expected_untracked:
        errors.append(f"unexpected untracked paths: expected={expected_untracked} actual={git['untracked_paths']}")
    if python_validation["tracked_python_file_count"] != EXPECTED_TRACKED_PYTHON_COUNT:
        errors.append(
            "tracked Python count mismatch before loop closure is tracked: "
            f"expected={EXPECTED_TRACKED_PYTHON_COUNT} actual={python_validation['tracked_python_file_count']}"
        )
    if not python_validation["pass"]:
        errors.append(
            f"tracked Python validation failed: syntax={python_validation['syntax_errors'][:20]} "
            f"bom={python_validation['bom_errors']}"
        )
    if physical["planned_schema_files_existing_count"] != 0:
        errors.append(f"planned schema files exist: {physical['planned_schema_files_existing']}")
    if physical["generic_runner_target_exists"] is not False:
        errors.append(f"generic runner target exists: {GENERIC_RUNNER_TARGET_FILE}")
    if not loop["loop_detected"]:
        errors.append("loop not detected from git-tracked matching files and recent commits")

    derived_checks = replacement_post_check(git, python_validation, physical, loop)
    if prior_post is None:
        derived_live_repo_post_check = True
        derived_live_repo_post_check_reason = (
            "required prior post-check artifact for latest generic governance blocked-status queue selector was not found; "
            "using explicit live repo replacement checks"
        )
        if not all(derived_checks.values()):
            errors.append(f"derived live repo replacement checks not all true: {derived_checks}")
    else:
        derived_live_repo_post_check = False
        derived_live_repo_post_check_reason = None
        if prior_post.get("audit_status") != EXPECTED_PREVIOUS_POST_CHECK_STATUS:
            errors.append(f"prior post-check status mismatch: {prior_post.get('audit_status')}")
        if prior_post.get("critical_issue_count") != 0:
            errors.append(f"prior post-check critical_issue_count not zero: {prior_post.get('critical_issue_count')}")

    return {
        "errors": errors,
        "git_state": git,
        "tracked_python_validation": python_validation,
        "physical": physical,
        "recent_commit_subjects": subjects,
        "loop_matching_files": files,
        "loop_detection": loop,
        "prior_post_check": prior_post,
        "prior_post_check_missing_paths": missing_prior_paths,
        "derived_live_repo_post_check": derived_live_repo_post_check,
        "derived_live_repo_post_check_reason": derived_live_repo_post_check_reason,
        "derived_live_repo_post_check_replacement_checks": derived_checks,
    }


def build_payload(validation: Dict[str, Any]) -> Dict[str, Any]:
    errors = list(validation["errors"])
    loop = validation["loop_detection"]
    physical = validation["physical"]
    dangerous_flags = {flag: False for flag in DANGEROUS_FLAGS}

    invariants = {
        "loop_detected": loop["loop_detected"] is True,
        "repeated_chain_detected": loop["repeated_chain_detected"] is True,
        "loop_closed": True,
        "next_selector_blocked": True,
        "next_backlog_refresh_blocked": True,
        "previous_next_module_superseded_by_human_decision": True,
        "next_module_is_human_decision_record": NEXT_MODULE == "edge_factory_os_repo_only_generic_governance_blocked_status_human_decision_record_v1.py",
        "next_module_is_not_ordinary_continuation": not ordinary_chain_continuation(NEXT_MODULE),
        "previous_ordinary_continuation_was_ordinary": ordinary_chain_continuation(PREVIOUS_ORDINARY_NEXT_MODULE),
        "generic_runner_approval_granted_false": False is False,
        "generic_runner_implementation_remains_blocked": True,
        "manual_approval_valid_for_generic_runner_false": False is False,
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
        "status": "REPO_ONLY_GENERIC_GOVERNANCE_BLOCKED_STATUS_LOOP_CLOSURE_V1_READY" if passed else "REPO_ONLY_GENERIC_GOVERNANCE_BLOCKED_STATUS_LOOP_CLOSURE_V1_BLOCKED",
        "closure_status": "LOOP_CLOSED" if passed else "LOOP_CLOSURE_BLOCKED",
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": "MECHANICAL_LOOP_CLOSED_AWAIT_HUMAN_DECISION" if passed else "KEEP_GENERIC_GOVERNANCE_BLOCKED_STATUS_LOOP_OPEN_REVIEW_ERRORS",
        "next_action": NEXT_ACTION if passed else "REVIEW_GENERIC_GOVERNANCE_BLOCKED_STATUS_LOOP_CLOSURE_ERRORS",
        "next_module": NEXT_MODULE if passed else None,
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "critical_issue_count": len(errors),
        "warning_count": 0,
        "errors": errors,
        "warnings": [],
        "loop_detected": bool(loop["loop_detected"]),
        "loop_iteration_count": int(loop["loop_iteration_count"]),
        "repeated_chain_detected": bool(loop["repeated_chain_detected"]),
        "repeated_name_growth_is_not_progress": True,
        "loop_closed": passed,
        "loop_closure_reason": "manual_approval_absent_no_progress_possible_without_human_action",
        "previous_next_module_superseded_by_human_decision": True,
        "previous_ordinary_next_module": PREVIOUS_ORDINARY_NEXT_MODULE,
        "supersede_reason": "external_adversarial_audit_confirmed_mechanical_loop_blocker",
        "external_audit_verdict": "LOOP_CONFIRMED",
        "external_audit_severity": "BLOCKER",
        "loop_closure_approved_by_human": True,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "manual_approval_present_for_generic_runner": False,
        "manual_approval_valid_for_generic_runner": False,
        "next_selector_blocked": True,
        "next_backlog_refresh_blocked": True,
        "requires_human_decision": True,
        "allowed_next_human_decisions": [
            "provide_manual_approval_for_generic_runner",
            "explicitly_abandon_generic_runner_path",
            "keep_generic_runner_blocked_and_route_to_other_repo_only_os_intelligence",
        ],
        "planned_schema_files_existing_count": physical["planned_schema_files_existing_count"],
        "planned_schema_files_existing": physical["planned_schema_files_existing"],
        "generic_runner_target_exists": physical["generic_runner_target_exists"],
        "dangerous_flags": dangerous_flags,
        "derived_live_repo_post_check": validation["derived_live_repo_post_check"],
        "derived_live_repo_post_check_reason": validation["derived_live_repo_post_check_reason"],
        "derived_live_repo_post_check_replacement_checks": validation["derived_live_repo_post_check_replacement_checks"],
        "derived_live_repo_post_check_overuse_attention": bool(validation["derived_live_repo_post_check"]),
        "previous_confirmed_post_check": EXPECTED_PREVIOUS_POST_CHECK_STATUS,
        "prior_post_check_artifact_present": validation["prior_post_check"] is not None,
        "prior_post_check_missing_paths": validation["prior_post_check_missing_paths"],
        "loop_detection": loop,
        "loop_matching_files": validation["loop_matching_files"],
        "validation": {
            "git_state": validation["git_state"],
            "tracked_python_validation": validation["tracked_python_validation"],
            "physical": physical,
            "recent_commit_subjects": validation["recent_commit_subjects"],
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
    latest_json = OUT_DIR / "repo_only_generic_governance_blocked_status_loop_closure_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_generic_governance_blocked_status_loop_closure_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_generic_governance_blocked_status_loop_closure_v1_latest.txt"
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
