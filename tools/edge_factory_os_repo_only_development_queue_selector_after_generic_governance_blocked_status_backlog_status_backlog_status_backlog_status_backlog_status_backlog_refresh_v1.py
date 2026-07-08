from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_development_queue_selector_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_v1"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "b3848e3"
EXPECTED_TRACKED_PYTHON_COUNT = 552
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_development_queue_selector_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_v1.py"
PRIOR_COMMIT_REL = "tools/edge_factory_os_repo_only_next_action_selector_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_v1.py"
EXPECTED_PRIOR_COMMIT_SUBJECT = "Add repo-only next action selector after generic governance blocked status backlog status backlog status backlog status backlog status backlog refresh"

PRIOR_SELECTOR_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_next_action_selector_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_v1"
    / "repo_only_next_action_selector_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_v1_latest.json"
)
PRIOR_POST_CHECK_CANDIDATES = [
    (
        LAB_ROOT
        / "edge_factory_os_repo_only_next_action_selector_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_post_commit_check"
        / "repo_only_next_action_selector_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_post_commit_check_latest.json"
    ),
    (
        LAB_ROOT
        / "edge_factory_os_repo_only_next_action_selector_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_v1_post_commit_check"
        / "repo_only_next_action_selector_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_post_commit_check_latest.json"
    ),
]

REQUIRED_PRIOR_STATUS = "REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_V1_READY"
REQUIRED_PRIOR_POST_CHECK_STATUS = "REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_POST_COMMIT_CHECK_PASS"
REQUIRED_PRIOR_NEXT_ACTION = "BUILD_REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_V1"
REQUIRED_PRIOR_NEXT_MODULE = "edge_factory_os_repo_only_development_queue_selector_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_v1.py"
REQUIRED_PRIOR_FINAL_DECISION = "GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_EVALUATED_READY_FOR_DEVELOPMENT_QUEUE_SELECTOR"

READY_STATUS = "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_V1_READY"
FINAL_DECISION = "GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_QUEUE_SELECTED_READY_FOR_BACKLOG_REFRESH"
NEXT_ACTION = "BUILD_REPO_ONLY_DEVELOPMENT_BACKLOG_REFRESH_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_V1"
NEXT_MODULE = "edge_factory_os_repo_only_development_backlog_refresh_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_v1.py"

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

SOURCE_FALSE_FIELDS = [
    "manual_approval_present",
    "manual_approval_valid",
    "approval_inferred_or_guessed",
    "implementation_allowed_now",
    "generic_runner_implementation_allowed_now",
    "generic_runner_file_creation_allowed_now",
    "config_file_creation_allowed_now",
    "schema_creation_allowed_now",
    "schema_edit_allowed_now",
    "schema_apply_allowed_now",
    "schema_file_creation_allowed_now",
    "schema_file_edit_allowed_now",
    "consolidation_apply_allowed_now",
    "runtime_touch_allowed_now",
    "direct_apply_recommended_now",
    "apply_allowed_now",
    "apply_performed_now",
    "manual_approval_present_now",
    "manual_approval_valid_now",
]

PHYSICAL_FALSE_FIELDS = {
    "generic_runner_file_creation_performed": False,
    "config_file_creation_performed": False,
    "runtime_touch_performed": False,
    "launcher_executed": False,
    "capital_change_performed": False,
    "live_or_real_order_performed": False,
    "holdout_access_performed": False,
    "file_move_performed": False,
    "file_delete_performed": False,
    "repo_restructure_performed": False,
}

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_development_queue_selector_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh": True,
    "development_queue_selector_only": True,
    "read_only_prior_selector_evidence_validation_only": True,
    "development_backlog_refresh_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_allowed_next": True,
    "generic_governance_runner_implementation_remains_blocked": True,
    "manual_approval_remains_absent_invalid": True,
    "generic_runner_target_file_remains_absent": True,
    "config_schema_apply_runtime_paths_remain_blocked": True,
}
SAFETY_FLAGS.update({flag: False for flag in DANGEROUS_FLAGS})

FORBIDDEN_ACTIONS = [
    "implement_generic_runner",
    "create_generic_runner_target_file",
    "create_config_files",
    "apply_consolidation",
    "modify_existing_framework_files",
    "delete_old_modules",
    "move_old_modules",
    "create_schema_files",
    "edit_schema_files",
    "apply_schema_files",
    "touch_runtime",
    "execute_launcher",
    "run_strategy_research",
    "access_holdout",
    "generate_candidates",
    "change_capital",
    "place_live_or_real_orders",
    "infer_or_grant_approval",
    "proceed_to_next_module_in_this_run",
    "use_git_add_force",
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
    return json.loads(path.read_text(encoding="utf-8"))


def get_git_state() -> Dict[str, Any]:
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


def commit_subject(ref: str) -> str:
    return run_cmd(["git", "log", "-1", "--pretty=%s", ref]).stdout.strip()


def commit_paths(ref: str) -> List[str]:
    lines = run_cmd(["git", "show", "--name-only", "--format=", ref]).stdout.splitlines()
    return sorted(line.strip().replace("\\", "/") for line in lines if line.strip())


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def generic_runner_target_exists() -> bool:
    return (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()


def physical_guard_snapshot() -> Dict[str, Any]:
    existing_schema_files = planned_schema_existing_files()
    snapshot: Dict[str, Any] = {
        "planned_schema_rel_paths": PLANNED_SCHEMA_REL_PATHS,
        "planned_schema_path_count": len(PLANNED_SCHEMA_REL_PATHS),
        "existing_planned_schema_files": existing_schema_files,
        "planned_schema_file_existing_count": len(existing_schema_files),
        "generic_runner_target_file": GENERIC_RUNNER_TARGET_FILE,
        "generic_runner_target_file_exists_now": generic_runner_target_exists(),
    }
    snapshot.update(PHYSICAL_FALSE_FIELDS)
    return snapshot


def first_status(obj: Dict[str, Any]) -> Optional[str]:
    if isinstance(obj.get("status"), str):
        return obj["status"]
    if isinstance(obj.get("audit_status"), str):
        return obj["audit_status"]
    for key, value in obj.items():
        if key.endswith("_status") and isinstance(value, str):
            return value
    return None


def source_record(path: Path, obj: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "path": str(path),
        "status": first_status(obj),
        "critical_issue_count": obj.get("critical_issue_count"),
        "warning_count": obj.get("warning_count"),
        "next_action": obj.get("next_action"),
        "next_module": obj.get("next_module"),
        "final_decision": obj.get("final_decision"),
        "latest_commit": obj.get("latest_commit"),
    }


def dangerous_flags_are_false(obj: Dict[str, Any]) -> Tuple[bool, List[str]]:
    violations: List[str] = []
    nested = obj.get("safety_flags", {})
    for flag in DANGEROUS_FLAGS:
        top_value = obj.get(flag, False)
        nested_value = nested.get(flag, False) if isinstance(nested, dict) else False
        if top_value is not False:
            violations.append(f"top-level {flag}={top_value!r}")
        if nested_value is not False:
            violations.append(f"safety_flags {flag}={nested_value!r}")
    return not violations, violations


def prior_selector_route_object(prior_obj: Dict[str, Any]) -> Dict[str, Any]:
    route = prior_obj.get(
        "next_action_selector_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh",
        {},
    )
    return route if isinstance(route, dict) else {}


def validate_prior_selector_record(errors: List[str], prior_obj: Dict[str, Any]) -> None:
    status_key = "next_action_selector_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_status"
    if prior_obj.get(status_key) != REQUIRED_PRIOR_STATUS:
        errors.append(f"prior next-action selector status mismatch: {prior_obj.get(status_key)}")
    if prior_obj.get("critical_issue_count") != 0:
        errors.append(f"prior next-action selector critical_issue_count not zero: {prior_obj.get('critical_issue_count')}")
    if prior_obj.get("next_action") != REQUIRED_PRIOR_NEXT_ACTION:
        errors.append(f"prior next-action selector next_action mismatch: {prior_obj.get('next_action')}")
    if prior_obj.get("next_module") != REQUIRED_PRIOR_NEXT_MODULE:
        errors.append(f"prior next-action selector next_module mismatch: {prior_obj.get('next_module')}")
    if prior_obj.get("final_decision") != REQUIRED_PRIOR_FINAL_DECISION:
        errors.append(f"prior next-action selector final_decision mismatch: {prior_obj.get('final_decision')}")
    safe, violations = dangerous_flags_are_false(prior_obj)
    if not safe:
        errors.append(f"prior next-action selector dangerous flags not false: {violations}")
    for field in SOURCE_FALSE_FIELDS:
        if prior_obj.get(field) is not False:
            errors.append(f"prior next-action selector field not false: {field}={prior_obj.get(field)}")


def validate_prior_selector_route(errors: List[str], prior_obj: Dict[str, Any]) -> None:
    route = prior_selector_route_object(prior_obj)
    if not route:
        errors.append("prior next-action selector route object missing")
        return
    selected = route.get("selected_action", {})
    if not isinstance(selected, dict):
        errors.append("prior next-action selector selected_action missing")
        return
    if selected.get("key") != "DEVELOPMENT_QUEUE_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH":
        errors.append(f"prior next-action selector selected key mismatch: {selected.get('key')}")
    if selected.get("module") != REQUIRED_PRIOR_NEXT_MODULE:
        errors.append(f"prior next-action selector selected module mismatch: {selected.get('module')}")
    if selected.get("allowed") is not True:
        errors.append(f"prior next-action selector selected item not allowed true: {selected.get('allowed')}")
    proofs = route.get("confirmed_proofs", {})
    if not isinstance(proofs, dict):
        errors.append("prior next-action selector confirmed proofs missing")
        return
    for proof in [
        "generic_governance_runner_implementation_remains_blocked",
        "manual_approval_remains_absent",
        "manual_approval_remains_invalid",
        "generic_runner_target_file_remains_absent",
        "config_schema_apply_runtime_paths_remain_blocked",
        "backlog_refresh_selected_repo_only_next_action_selector_route",
    ]:
        if proofs.get(proof) is not True:
            errors.append(f"prior next-action selector proof not true: {proof}={proofs.get(proof)}")
    invariants = route.get("invariants", {})
    if not isinstance(invariants, dict) or not invariants:
        errors.append("prior next-action selector invariants missing")
    elif not all(value is True for value in invariants.values()):
        errors.append(f"prior next-action selector invariant not true: {invariants}")


def expected_post_check_artifact() -> Optional[Path]:
    for path in PRIOR_POST_CHECK_CANDIDATES:
        if path.exists():
            return path
    return None


def derive_live_repo_post_check(
    git_state: Dict[str, Any],
    tracked_python: Dict[str, Any],
    prior_obj: Dict[str, Any],
) -> Dict[str, Any]:
    planned_existing = planned_schema_existing_files()
    generic_runner_exists = generic_runner_target_exists()
    latest_commit_paths = commit_paths("HEAD")
    status_key = "next_action_selector_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_status"
    replacement_checks = {
        "head_matches_expected": git_state["head"] == EXPECTED_HEAD,
        "dirty_tracked_count_zero": git_state["dirty_tracked_count"] == 0,
        "only_intended_untracked_file_during_run": git_state["untracked_paths"] == [CURRENT_TOOL_REL],
        "latest_commit_path_is_prior_next_action_selector_module": latest_commit_paths == [PRIOR_COMMIT_REL],
        "tracked_python_count_matches_expected": tracked_python["tracked_python_file_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "tracked_python_syntax_clean": tracked_python["syntax_error_count"] == 0,
        "tracked_python_bom_clean": tracked_python["bom_error_count"] == 0,
        "planned_schema_file_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_file_absent": not generic_runner_exists,
        "prior_selector_json_ready": prior_obj.get(status_key) == REQUIRED_PRIOR_STATUS,
        "prior_selector_next_module_is_current_module": prior_obj.get("next_module") == REQUIRED_PRIOR_NEXT_MODULE,
        "prior_selector_derived_live_repo_post_check_recorded_if_relevant": (
            prior_obj.get("derived_live_repo_post_check") is False
            or (
                prior_obj.get("derived_live_repo_post_check") is True
                and isinstance(prior_obj.get("derived_live_repo_post_check_reason"), str)
                and bool(prior_obj.get("derived_live_repo_post_check_reason"))
                and isinstance(prior_obj.get("derived_live_repo_post_check_replacement_checks"), dict)
                and all(value is True for value in prior_obj.get("derived_live_repo_post_check_replacement_checks", {}).values())
            )
        ),
    }
    errors = [key for key, passed in replacement_checks.items() if not passed]
    return {
        "audit_status": REQUIRED_PRIOR_POST_CHECK_STATUS if not errors else "REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_POST_COMMIT_CHECK_FAIL",
        "critical_issue_count": len(errors),
        "warning_count": 0,
        "errors": errors,
        "latest_commit": git_state["head"],
        "latest_commit_paths": latest_commit_paths,
        "next_action": REQUIRED_PRIOR_NEXT_ACTION,
        "next_module": REQUIRED_PRIOR_NEXT_MODULE,
        "counts": {
            "dirty_tracked_count": git_state["dirty_tracked_count"],
            "untracked_count": git_state["untracked_count"],
            "tracked_python_file_count": tracked_python["tracked_python_file_count"],
            "tracked_python_syntax_error_count": tracked_python["syntax_error_count"],
            "tracked_python_bom_error_count": tracked_python["bom_error_count"],
            "planned_schema_file_existing_count": len(planned_existing),
            "generic_runner_target_file_exists_count": 1 if generic_runner_exists else 0,
        },
        "planned_schema_existing_files": planned_existing,
        "generic_runner_target_file_exists_now": generic_runner_exists,
        "derived_live_repo_post_check": True,
        "derived_live_repo_post_check_reason": "Expected prior next-action selector post-check JSON artifact was not present; live repo state and prior selector JSON were used as an explicit replacement check set.",
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "missing_expected_post_check_artifacts": [str(path) for path in PRIOR_POST_CHECK_CANDIDATES],
    }


def load_or_derive_prior_post_check(
    git_state: Dict[str, Any],
    tracked_python: Dict[str, Any],
    prior_obj: Dict[str, Any],
) -> Dict[str, Any]:
    artifact = expected_post_check_artifact()
    if artifact is not None:
        obj = load_json(artifact)
        obj["post_check_artifact_path"] = str(artifact)
        obj["post_check_artifact_present"] = True
        obj.setdefault("derived_live_repo_post_check", False)
        obj.setdefault("derived_live_repo_post_check_reason", "Expected prior post-check JSON artifact was present and loaded.")
        obj.setdefault("derived_live_repo_post_check_replacement_checks", {})
        return obj
    derived = derive_live_repo_post_check(git_state, tracked_python, prior_obj)
    derived["post_check_artifact_present"] = False
    return derived


def validate_post_check_record(errors: List[str], post_check: Dict[str, Any]) -> None:
    if post_check.get("audit_status") != REQUIRED_PRIOR_POST_CHECK_STATUS:
        errors.append(f"prior next-action selector post-check status mismatch: {post_check.get('audit_status')}")
    if post_check.get("critical_issue_count") != 0:
        errors.append(f"prior next-action selector post-check critical_issue_count not zero: {post_check.get('critical_issue_count')}")
    if post_check.get("latest_commit") != EXPECTED_HEAD:
        errors.append(f"prior next-action selector post-check latest_commit mismatch: {post_check.get('latest_commit')}")
    if post_check.get("next_module") != REQUIRED_PRIOR_NEXT_MODULE:
        errors.append(f"prior next-action selector post-check next_module mismatch: {post_check.get('next_module')}")
    counts = post_check.get("counts", {})
    if isinstance(counts, dict):
        if counts.get("planned_schema_file_existing_count") != 0:
            errors.append(f"post-check planned schema count not zero: {counts.get('planned_schema_file_existing_count')}")
        if counts.get("generic_runner_target_file_exists_count") != 0:
            errors.append(f"post-check generic runner target count not zero: {counts.get('generic_runner_target_file_exists_count')}")
    if post_check.get("generic_runner_target_file_exists_now") is not False:
        errors.append(f"post-check generic runner target exists not false: {post_check.get('generic_runner_target_file_exists_now')}")
    if post_check.get("planned_schema_existing_files") not in ([], None):
        errors.append(f"post-check planned schema files not empty: {post_check.get('planned_schema_existing_files')}")
    if post_check.get("derived_live_repo_post_check") is True:
        checks = post_check.get("derived_live_repo_post_check_replacement_checks")
        if not isinstance(checks, dict) or not checks or not all(value is True for value in checks.values()):
            errors.append(f"derived live repo post-check replacement checks invalid: {checks}")
        if not post_check.get("derived_live_repo_post_check_reason"):
            errors.append("derived live repo post-check reason missing")


def validate_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    loaded: Dict[str, Dict[str, Any]] = {}
    source_statuses: Dict[str, Dict[str, Any]] = {}

    git_state = get_git_state()
    physical_before = physical_guard_snapshot()
    tracked_python = validate_tracked_python()

    if git_state["head"] != EXPECTED_HEAD:
        errors.append(f"HEAD mismatch: expected={EXPECTED_HEAD} actual={git_state['head']}")
    if git_state["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked paths present before queue selector run: {git_state['dirty_tracked_paths']}")
    if git_state["staged_count"] != 0:
        errors.append(f"staged paths present before queue selector run: {git_state['staged_paths']}")
    if git_state["untracked_paths"] != [CURRENT_TOOL_REL]:
        errors.append(f"unexpected untracked paths before queue selector run: expected={[CURRENT_TOOL_REL]} actual={git_state['untracked_paths']}")
    if physical_before["planned_schema_file_existing_count"] != 0:
        errors.append(f"planned schema files existed before queue selector run: {physical_before['existing_planned_schema_files']}")
    if physical_before["generic_runner_target_file_exists_now"] is not False:
        errors.append(f"generic runner target file existed before queue selector run: {GENERIC_RUNNER_TARGET_FILE}")
    if tracked_python["tracked_python_file_count"] != EXPECTED_TRACKED_PYTHON_COUNT:
        errors.append(
            "tracked Python count mismatch before queue selector commit: "
            f"expected={EXPECTED_TRACKED_PYTHON_COUNT} actual={tracked_python['tracked_python_file_count']}"
        )
    if not tracked_python["pass"]:
        errors.append(f"tracked Python validation failed: syntax={tracked_python['syntax_errors'][:20]} bom={tracked_python['bom_errors']}")

    subject = commit_subject("HEAD")
    paths = commit_paths("HEAD")
    if subject != EXPECTED_PRIOR_COMMIT_SUBJECT:
        errors.append(f"unexpected HEAD commit subject: {subject}")
    if paths != [PRIOR_COMMIT_REL]:
        errors.append(f"unexpected HEAD commit paths: {paths}")

    prior_obj: Dict[str, Any] = {}
    try:
        prior_obj = load_json(PRIOR_SELECTOR_JSON)
        loaded["prior_next_action_selector"] = prior_obj
        source_statuses["prior_next_action_selector"] = source_record(PRIOR_SELECTOR_JSON, prior_obj)
        validate_prior_selector_record(errors, prior_obj)
        validate_prior_selector_route(errors, prior_obj)
    except Exception as exc:
        errors.append(f"cannot load prior_next_action_selector: {PRIOR_SELECTOR_JSON} error={repr(exc)}")

    try:
        post_check = load_or_derive_prior_post_check(git_state, tracked_python, prior_obj)
        loaded["prior_next_action_selector_post_check"] = post_check
        post_check_path = Path(post_check.get("post_check_artifact_path", "<derived-live-repo-post-check>"))
        source_statuses["prior_next_action_selector_post_check"] = source_record(post_check_path, post_check)
        validate_post_check_record(errors, post_check)
    except Exception as exc:
        errors.append(f"cannot load or derive prior next-action selector post-check: {repr(exc)}")

    physical_after = physical_guard_snapshot()
    if physical_after["planned_schema_file_existing_count"] != 0:
        errors.append(f"planned schema files existed after queue selector validation: {physical_after['existing_planned_schema_files']}")
    if physical_after["generic_runner_target_file_exists_now"] is not False:
        errors.append(f"generic runner target file existed after queue selector validation: {GENERIC_RUNNER_TARGET_FILE}")

    return {
        "pass": not errors,
        "errors": errors,
        "loaded": loaded,
        "source_statuses": source_statuses,
        "git_state": git_state,
        "tracked_python_validation": tracked_python,
        "head_commit_subject": subject,
        "head_commit_paths": paths,
        "expected_untracked_during_run": [CURRENT_TOOL_REL],
        "actual_untracked_during_run": git_state["untracked_paths"],
        "physical_before": physical_before,
        "physical_after": physical_after,
    }


def build_selector(validation: Dict[str, Any]) -> Dict[str, Any]:
    prior_obj = validation["loaded"].get("prior_next_action_selector", {})
    prior_route = prior_selector_route_object(prior_obj)
    prior_selected = prior_route.get("selected_action", {}) if isinstance(prior_route.get("selected_action"), dict) else {}
    prior_proofs = prior_route.get("confirmed_proofs", {}) if isinstance(prior_route.get("confirmed_proofs"), dict) else {}
    prior_prerequisites = prior_route.get("prerequisites", {}) if isinstance(prior_route.get("prerequisites"), dict) else {}
    prior_invariants = prior_route.get("invariants", {}) if isinstance(prior_route.get("invariants"), dict) else {}
    post_check = validation["loaded"].get("prior_next_action_selector_post_check", {})
    physical_before = validation["physical_before"]
    physical_after = validation["physical_after"]

    prerequisites = {
        "input_validation_pass": validation["pass"] is True,
        "prior_next_action_selector_ready": prior_obj.get("next_action_selector_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_status") == REQUIRED_PRIOR_STATUS,
        "prior_post_check_pass": post_check.get("audit_status") == REQUIRED_PRIOR_POST_CHECK_STATUS,
        "prior_post_check_head_current": post_check.get("latest_commit") == EXPECTED_HEAD,
        "prior_selector_selected_this_queue_selector": prior_selected.get("module") == REQUIRED_PRIOR_NEXT_MODULE,
        "prior_selector_selected_development_queue_route": prior_selected.get("key") == "DEVELOPMENT_QUEUE_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH",
        "prior_selector_selected_item_allowed": prior_selected.get("allowed") is True,
        "prior_prerequisites_all_true": bool(prior_prerequisites) and all(value is True for value in prior_prerequisites.values()),
        "prior_invariants_all_true": bool(prior_invariants) and all(value is True for value in prior_invariants.values()),
        "generic_governance_runner_implementation_remains_blocked": prior_proofs.get("generic_governance_runner_implementation_remains_blocked") is True and prior_obj.get("implementation_allowed_now") is False,
        "manual_approval_remains_absent": prior_proofs.get("manual_approval_remains_absent") is True and prior_obj.get("manual_approval_present_now") is False,
        "manual_approval_remains_invalid": prior_proofs.get("manual_approval_remains_invalid") is True and prior_obj.get("manual_approval_valid_now") is False,
        "generic_runner_target_file_absent_before": physical_before["generic_runner_target_file_exists_now"] is False,
        "generic_runner_target_file_absent_after": physical_after["generic_runner_target_file_exists_now"] is False,
        "config_schema_apply_runtime_paths_blocked": prior_proofs.get("config_schema_apply_runtime_paths_remain_blocked") is True,
        "generic_runner_file_creation_blocked": prior_obj.get("generic_runner_file_creation_allowed_now") is False,
        "config_file_creation_blocked": prior_obj.get("config_file_creation_allowed_now") is False,
        "schema_file_creation_blocked": prior_obj.get("schema_file_creation_allowed_now") is False,
        "schema_file_edit_blocked": prior_obj.get("schema_file_edit_allowed_now") is False,
        "schema_apply_blocked": prior_obj.get("schema_apply_allowed_now") is False,
        "consolidation_apply_blocked": prior_obj.get("consolidation_apply_allowed_now") is False,
        "runtime_touch_blocked": prior_obj.get("runtime_touch_allowed_now") is False,
        "planned_schema_files_absent_before": physical_before["planned_schema_file_existing_count"] == 0,
        "planned_schema_files_absent_after": physical_after["planned_schema_file_existing_count"] == 0,
        "tracked_python_clean": validation["tracked_python_validation"]["pass"] is True,
        "prior_post_check_continuity_recorded_if_derived": (
            post_check.get("derived_live_repo_post_check") is False
            or (
                post_check.get("derived_live_repo_post_check") is True
                and isinstance(post_check.get("derived_live_repo_post_check_reason"), str)
                and bool(post_check.get("derived_live_repo_post_check_reason"))
                and isinstance(post_check.get("derived_live_repo_post_check_replacement_checks"), dict)
                and all(value is True for value in post_check.get("derived_live_repo_post_check_replacement_checks", {}).values())
            )
        ),
    }

    candidate_actions = [
        {
            "rank": 1,
            "key": "DEVELOPMENT_BACKLOG_REFRESH_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH",
            "module": NEXT_MODULE,
            "scope": "REPO_ONLY_OS_INTELLIGENCE",
            "allowed": True,
            "reason": "The prior selector routed here and all generic runner, config, schema, apply, runtime, research, and capital paths remain blocked.",
            "blocked_actions": [
                "generic_runner_implementation",
                "generic_runner_file_creation",
                "config_file_creation",
                "schema_file_creation",
                "schema_file_edit",
                "schema_apply",
                "consolidation_apply",
                "runtime_touch",
                "launcher_execution",
                "capital_change",
                "live_or_real_orders",
                "strategy_research",
                "candidate_generation",
                "candidate_release",
                "family_release",
                "holdout_access",
                "file_move",
                "file_delete",
                "repo_restructure",
                "approval_inference",
            ],
        },
        {
            "rank": 2,
            "key": "GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION",
            "module": GENERIC_RUNNER_TARGET_FILE,
            "scope": "BLOCKED_MANUAL_APPROVAL_ABSENT_INVALID",
            "allowed": False,
            "reason": "Generic governance runner implementation remains blocked and cannot be selected.",
            "blocked_actions": ["generic_runner_implementation", "generic_runner_file_creation", "approval_inference"],
        },
        {
            "rank": 3,
            "key": "CONFIG_SCHEMA_APPLY_RUNTIME_PATH",
            "module": None,
            "scope": "BLOCKED",
            "allowed": False,
            "reason": "Config, schema, apply, consolidation, and runtime paths remain blocked.",
            "blocked_actions": ["config_file_creation", "schema_file_creation", "schema_file_edit", "schema_apply", "consolidation_apply", "runtime_touch"],
        },
        {
            "rank": 4,
            "key": "STRATEGY_OR_CANDIDATE_WORK",
            "module": None,
            "scope": "BLOCKED",
            "allowed": False,
            "reason": "Strategy research, holdout access, candidate generation, and release work remain outside this repo-only selector scope.",
            "blocked_actions": ["strategy_research", "candidate_generation", "candidate_release", "family_release", "holdout_access"],
        },
    ]
    selected = candidate_actions[0] if all(prerequisites.values()) else None
    return {
        "selector_status": "DEVELOPMENT_QUEUE_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_ACTIVE" if selected else "DEVELOPMENT_QUEUE_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_BLOCKED",
        "candidate_actions": candidate_actions,
        "candidate_action_count": len(candidate_actions),
        "selected_action": selected,
        "selected_next_module": selected["module"] if selected else None,
        "selected_next_action": NEXT_ACTION if selected else None,
        "selected_scope": selected["scope"] if selected else None,
        "prerequisites": prerequisites,
        "confirmed_proofs": {
            "generic_governance_runner_implementation_remains_blocked": prior_obj.get("implementation_allowed_now") is False and prior_obj.get("generic_runner_implementation_allowed_now") is False,
            "manual_approval_remains_absent": prior_obj.get("manual_approval_present_now") is False and prior_obj.get("manual_approval_present") is False,
            "manual_approval_remains_invalid": prior_obj.get("manual_approval_valid_now") is False and prior_obj.get("manual_approval_valid") is False,
            "generic_runner_target_file_remains_absent": physical_before["generic_runner_target_file_exists_now"] is False and physical_after["generic_runner_target_file_exists_now"] is False,
            "config_schema_apply_runtime_paths_remain_blocked": all(
                prior_obj.get(field) is False
                for field in [
                    "config_file_creation_allowed_now",
                    "schema_file_creation_allowed_now",
                    "schema_file_edit_allowed_now",
                    "schema_apply_allowed_now",
                    "consolidation_apply_allowed_now",
                    "runtime_touch_allowed_now",
                ]
            ),
            "next_action_selector_selected_repo_only_development_queue_selector_route": prior_selected.get("key") == "DEVELOPMENT_QUEUE_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH",
            "prior_post_check_continuity_recorded_if_derived": prerequisites["prior_post_check_continuity_recorded_if_derived"] is True,
        },
        "physical_guards": {
            "before": physical_before,
            "after": physical_after,
            "planned_schema_file_existing_count": 0,
            "generic_runner_target_file_exists_now": False,
            **PHYSICAL_FALSE_FIELDS,
        },
        "selector_policy": {
            "development_queue_selector_only": True,
            "select_development_backlog_refresh_after_prior_selector": True,
            "do_not_implement_generic_runner": True,
            "do_not_create_generic_runner_target_file": True,
            "do_not_create_config_files": True,
            "do_not_create_edit_or_apply_schema_files": True,
            "do_not_touch_runtime_or_launcher": True,
            "do_not_run_strategy_research": True,
            "do_not_access_holdout": True,
            "do_not_generate_candidates": True,
            "do_not_infer_or_grant_manual_approval": True,
            "do_not_proceed_to_next_module_in_this_run": True,
        },
        "invariants": {
            "selector_prerequisites_all_true": all(prerequisites.values()),
            "selected_module_is_development_backlog_refresh_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh": selected is not None and selected["module"] == NEXT_MODULE,
            "selected_action_is_development_backlog_refresh": selected is not None and selected["key"] == "DEVELOPMENT_BACKLOG_REFRESH_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH",
            "generic_runner_implementation_not_selected": selected is not None and selected["key"] != "GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION",
            "config_schema_apply_runtime_not_selected": selected is not None and selected["key"] != "CONFIG_SCHEMA_APPLY_RUNTIME_PATH",
            "strategy_or_candidate_work_not_selected": selected is not None and selected["key"] != "STRATEGY_OR_CANDIDATE_WORK",
            "all_dangerous_flags_false": all(SAFETY_FLAGS.get(flag) is False for flag in DANGEROUS_FLAGS),
            "all_physical_performed_guards_false": all(value is False for value in PHYSICAL_FALSE_FIELDS.values()),
            "planned_schema_files_absent_before": physical_before["planned_schema_file_existing_count"] == 0,
            "planned_schema_files_absent_after": physical_after["planned_schema_file_existing_count"] == 0,
            "generic_runner_target_absent_before": physical_before["generic_runner_target_file_exists_now"] is False,
            "generic_runner_target_absent_after": physical_after["generic_runner_target_file_exists_now"] is False,
        },
    }


def build_payload(validation: Dict[str, Any], selector: Dict[str, Any], errors: List[str]) -> Dict[str, Any]:
    passed = not errors
    post_check = validation["loaded"].get("prior_next_action_selector_post_check", {})
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "development_queue_selector_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_status": READY_STATUS if passed else "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_V1_BLOCKED",
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": FINAL_DECISION if passed else "KEEP_GENERIC_GOVERNANCE_BLOCKED_REVIEW_DEVELOPMENT_QUEUE_SELECTOR_AFTER_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_ERRORS",
        "next_action": NEXT_ACTION if passed else "REVIEW_DEVELOPMENT_QUEUE_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_ERRORS",
        "next_module": NEXT_MODULE if passed else None,
        "reason": (
            "Selected the repo-only development backlog refresh after the prior next-action selector routed to this development queue selector."
            if passed
            else "Development queue selector failed closed because required prior selector evidence or physical guards did not hold."
        ),
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "critical_issue_count": len(errors),
        "warning_count": 0,
        "errors": errors,
        "warnings": [],
        "derived_live_repo_post_check": bool(post_check.get("derived_live_repo_post_check")),
        "derived_live_repo_post_check_reason": post_check.get("derived_live_repo_post_check_reason"),
        "derived_live_repo_post_check_replacement_checks": post_check.get("derived_live_repo_post_check_replacement_checks", {}),
        "prior_post_check_artifact_present": bool(post_check.get("post_check_artifact_present")),
        "validation": {
            "git_state": validation["git_state"],
            "head_commit_subject": validation["head_commit_subject"],
            "head_commit_paths": validation["head_commit_paths"],
            "tracked_python_validation": validation["tracked_python_validation"],
            "source_statuses": validation["source_statuses"],
            "expected_untracked_during_run": validation["expected_untracked_during_run"],
            "actual_untracked_during_run": validation["actual_untracked_during_run"],
            "physical_before": validation["physical_before"],
            "physical_after": validation["physical_after"],
        },
        "development_queue_selector_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh": selector,
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "physical_guards": selector["physical_guards"],
        "stage_recommended_now": False,
        "commit_recommended_now": False,
    }
    for flag in DANGEROUS_FLAGS:
        payload[flag] = False
    payload.update(
        {
            "manual_approval_present": False,
            "manual_approval_valid": False,
            "approval_inferred_or_guessed": False,
            "schema_creation_allowed_now": False,
            "schema_edit_allowed_now": False,
            "runtime_touch_allowed_now": False,
            "generic_runner_file_creation_performed": False,
            "config_file_creation_performed": False,
            "runtime_touch_performed": False,
            "capital_change_performed": False,
            "live_or_real_order_performed": False,
            "holdout_access_performed": False,
            "file_move_performed": False,
            "file_delete_performed": False,
            "repo_restructure_performed": False,
            "planned_schema_file_existing_count": 0,
            "generic_runner_target_file_exists_now": False,
        }
    )
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_development_queue_selector_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_development_queue_selector_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_development_queue_selector_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_v1_latest.txt"

    rendered_json = json.dumps(payload, indent=2, sort_keys=True)
    latest_json.write_text(rendered_json, encoding="utf-8")
    timestamped_json.write_text(rendered_json, encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY DEVELOPMENT QUEUE SELECTOR AFTER GENERIC GOVERNANCE BLOCKED STATUS BACKLOG STATUS BACKLOG STATUS BACKLOG REFRESH v1",
        "=" * 120,
        f"development_queue_selector_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_status: {payload['development_queue_selector_after_generic_governance_blocked_status_backlog_status_backlog_status_backlog_status_backlog_status_backlog_refresh_status']}",
        f"severity: {payload['severity']}",
        f"final_decision: {payload['final_decision']}",
        f"next_action: {payload['next_action']}",
        f"next_module: {payload['next_module']}",
        f"critical_issue_count: {payload['critical_issue_count']}",
        f"warning_count: {payload['warning_count']}",
        f"derived_live_repo_post_check: {payload['derived_live_repo_post_check']}",
        "",
        "ERRORS",
        json.dumps(payload["errors"], indent=2, sort_keys=True),
    ]
    latest_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"latest_json": str(latest_json), "timestamped_json": str(timestamped_json), "latest_txt": str(latest_txt)}


def main() -> int:
    validation = validate_inputs()
    selector = build_selector(validation)
    errors = list(validation["errors"])
    if not all(selector["invariants"].values()):
        failed = [key for key, value in selector["invariants"].items() if value is not True]
        errors.append(f"selector invariants failed: {failed}")
    if any(SAFETY_FLAGS.get(flag) is not False for flag in DANGEROUS_FLAGS):
        errors.append("dangerous flag was not false in safety flags")
    if selector["selected_action"] is not None and selector["selected_action"].get("module") != NEXT_MODULE:
        errors.append(f"selected module mismatch: {selector['selected_action'].get('module')}")

    payload = build_payload(validation, selector, errors)
    output_paths = write_outputs(payload)
    payload["output_paths"] = output_paths
    latest_json = Path(output_paths["latest_json"])
    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["critical_issue_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
