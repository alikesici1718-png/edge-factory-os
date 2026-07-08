from __future__ import annotations

import ast
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_development_queue_selector_after_generic_governance_blocked_status_backlog_refresh_v1"
OUT_DIR = LAB_ROOT / MODULE_NAME
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD = "e228c85"
EXPECTED_TRACKED_PYTHON_COUNT = 540
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_development_queue_selector_after_generic_governance_blocked_status_backlog_refresh_v1.py"
APPROVED_CURRENT_MODULE = "edge_factory_os_repo_only_development_queue_selector_after_generic_governance_blocked_status_backlog_refresh_v1.py"

SELECTED_NEXT_ACTION = "BUILD_REPO_ONLY_DEVELOPMENT_BACKLOG_REFRESH_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_REFRESH_V1"
SELECTED_NEXT_MODULE = "edge_factory_os_repo_only_development_backlog_refresh_after_generic_governance_blocked_status_backlog_refresh_v1.py"

READY_STATUS = "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_REFRESH_V1_READY"
FINAL_DECISION = "GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_REFRESH_QUEUE_SELECTED_READY_FOR_BACKLOG_REFRESH"

SELECTOR_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_next_action_selector_after_generic_governance_blocked_status_backlog_refresh_v1"
    / "repo_only_next_action_selector_after_generic_governance_blocked_status_backlog_refresh_v1_latest.json"
)
SELECTOR_POST_JSON = (
    LAB_ROOT
    / "edge_factory_os_repo_only_next_action_selector_after_generic_governance_blocked_status_backlog_refresh_post_commit_check"
    / "repo_only_next_action_selector_after_generic_governance_blocked_status_backlog_refresh_post_commit_check_latest.json"
)

EXPECTED_SELECTOR_STATUS = "REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_REFRESH_V1_READY"
EXPECTED_SELECTOR_POST_STATUS = "REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_REFRESH_POST_COMMIT_CHECK_PASS"
EXPECTED_SELECTOR_ACTION = "BUILD_REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_REFRESH_V1"
EXPECTED_SELECTOR_FINAL_DECISION = "GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_REFRESH_EVALUATED_READY_FOR_DEVELOPMENT_QUEUE_SELECTOR"

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
    "repo_only_development_queue_selector_after_generic_governance_blocked_status_backlog_refresh": True,
    "development_queue_selector_only": True,
    "read_only_next_action_selector_evidence_validation_only": True,
    "development_backlog_refresh_after_generic_governance_blocked_status_backlog_refresh_allowed_next": True,
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

INPUTS: Dict[str, Tuple[Path, str, Optional[str]]] = {
    "next_action_selector": (SELECTOR_JSON, EXPECTED_SELECTOR_STATUS, APPROVED_CURRENT_MODULE),
    "next_action_selector_post_check": (SELECTOR_POST_JSON, EXPECTED_SELECTOR_POST_STATUS, APPROVED_CURRENT_MODULE),
}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {args} returncode={result.returncode} stderr={result.stderr}")
    return result


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def first_status(obj: Dict[str, Any]) -> Optional[str]:
    if isinstance(obj.get("status"), str):
        return obj["status"]
    if isinstance(obj.get("audit_status"), str):
        return obj["audit_status"]
    for key, value in obj.items():
        if key.endswith("_status") and isinstance(value, str):
            return value
    return None


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def generic_runner_target_exists() -> bool:
    return (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()


def physical_guard_snapshot() -> Dict[str, Any]:
    existing = planned_schema_existing_files()
    snapshot: Dict[str, Any] = {
        "planned_schema_rel_paths": PLANNED_SCHEMA_REL_PATHS,
        "planned_schema_path_count": len(PLANNED_SCHEMA_REL_PATHS),
        "existing_planned_schema_files": existing,
        "planned_schema_file_existing_count": len(existing),
        "generic_runner_target_file": GENERIC_RUNNER_TARGET_FILE,
        "generic_runner_target_file_exists_now": generic_runner_target_exists(),
    }
    snapshot.update(PHYSICAL_FALSE_FIELDS)
    return snapshot


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


def source_record(path: Path, obj: Dict[str, Any]) -> Dict[str, Any]:
    counts = obj.get("counts", {})
    return {
        "path": str(path),
        "status": first_status(obj),
        "severity": obj.get("severity"),
        "critical_issue_count": obj.get("critical_issue_count"),
        "warning_count": obj.get("warning_count"),
        "next_action": obj.get("next_action"),
        "next_module": obj.get("next_module"),
        "final_decision": obj.get("final_decision"),
        "latest_commit": obj.get("latest_commit"),
        "git_head": obj.get("git_state", {}).get("head") if isinstance(obj.get("git_state"), dict) else None,
        "counts": counts if isinstance(counts, dict) else {},
    }


def validate_zero(errors: List[str], key: str, record: Dict[str, Any], field: str) -> None:
    value = record.get(field)
    if value is None:
        errors.append(f"{key} {field} field missing")
    elif value != 0:
        errors.append(f"{key} {field} not zero: {value}")


def validate_input_record(
    errors: List[str],
    key: str,
    record: Dict[str, Any],
    expected_status: str,
    expected_next_module: Optional[str],
) -> None:
    if record.get("status") != expected_status:
        errors.append(f"{key} status mismatch: expected={expected_status} actual={record.get('status')}")
    validate_zero(errors, key, record, "critical_issue_count")
    validate_zero(errors, key, record, "warning_count")
    if expected_next_module is not None and record.get("next_module") != expected_next_module:
        errors.append(f"{key} next_module mismatch: expected={expected_next_module} actual={record.get('next_module')}")


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


def validate_selector_proofs(errors: List[str], selector_obj: Dict[str, Any]) -> None:
    detail = selector_obj.get("next_action_selector_after_generic_governance_blocked_status_backlog_refresh", {})
    if not isinstance(detail, dict):
        errors.append("next-action selector detail object missing")
        return

    selected_action = detail.get("selected_action", {})
    if not isinstance(selected_action, dict):
        errors.append("next-action selector selected_action missing")
        return

    if selected_action.get("key") != "DEVELOPMENT_QUEUE_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_REFRESH":
        errors.append(f"selector selected key mismatch: {selected_action.get('key')}")
    if selected_action.get("module") != APPROVED_CURRENT_MODULE:
        errors.append(f"selector selected module mismatch: {selected_action.get('module')}")
    if selected_action.get("allowed") is not True:
        errors.append(f"selector selected action allowed not true: {selected_action.get('allowed')}")
    if selected_action.get("scope") != "REPO_ONLY_OS_INTELLIGENCE":
        errors.append(f"selector selected action scope mismatch: {selected_action.get('scope')}")

    proofs = detail.get("confirmed_proofs", {})
    if not isinstance(proofs, dict):
        errors.append("next-action selector confirmed proofs missing")
        return
    for key in [
        "generic_governance_runner_implementation_remains_blocked",
        "manual_approval_remains_absent",
        "manual_approval_remains_invalid",
        "generic_runner_target_file_remains_absent",
        "config_schema_apply_runtime_paths_remain_blocked",
        "backlog_refresh_selected_repo_only_next_action_selector_route",
    ]:
        if proofs.get(key) is not True:
            errors.append(f"next-action selector proof not true: {key}={proofs.get(key)}")

    if selector_obj.get("implementation_allowed_now") is not False:
        errors.append(f"selector implementation_allowed_now not false: {selector_obj.get('implementation_allowed_now')}")
    if selector_obj.get("generic_runner_implementation_allowed_now") is not False:
        errors.append(
            "selector generic_runner_implementation_allowed_now not false: "
            f"{selector_obj.get('generic_runner_implementation_allowed_now')}"
        )
    if selector_obj.get("manual_approval_present_now") is not False:
        errors.append(f"selector manual_approval_present_now not false: {selector_obj.get('manual_approval_present_now')}")
    if selector_obj.get("manual_approval_valid_now") is not False:
        errors.append(f"selector manual_approval_valid_now not false: {selector_obj.get('manual_approval_valid_now')}")
    for field in [
        "generic_runner_file_creation_allowed_now",
        "config_file_creation_allowed_now",
        "schema_file_creation_allowed_now",
        "schema_file_edit_allowed_now",
        "schema_apply_allowed_now",
        "consolidation_apply_allowed_now",
        "runtime_touch_allowed_now",
        "direct_apply_recommended_now",
        "apply_allowed_now",
        "apply_performed_now",
    ]:
        if selector_obj.get(field) is not False:
            errors.append(f"selector blocked path flag not false: {field}={selector_obj.get(field)}")


def validate_post_check_physical_guards(errors: List[str], post_check: Dict[str, Any]) -> None:
    counts = post_check.get("counts", {})
    if not isinstance(counts, dict):
        errors.append("selector post-check counts missing")
        return
    expected_counts = {
        "dirty_tracked_count": 0,
        "untracked_count": 0,
        "planned_schema_file_existing_count": 0,
        "generic_runner_target_file_exists_count": 0,
        "tracked_python_bom_error_count": 0,
        "tracked_python_syntax_error_count": 0,
    }
    for key, expected in expected_counts.items():
        if counts.get(key) != expected:
            errors.append(f"selector post-check count mismatch: {key}={counts.get(key)} expected={expected}")
    if counts.get("tracked_python_file_count") != EXPECTED_TRACKED_PYTHON_COUNT:
        errors.append(
            "selector post-check tracked Python count mismatch: "
            f"{counts.get('tracked_python_file_count')} expected={EXPECTED_TRACKED_PYTHON_COUNT}"
        )
    if post_check.get("generic_runner_target_file_exists_now") is not False:
        errors.append(
            "selector post-check generic runner target exists not false: "
            f"{post_check.get('generic_runner_target_file_exists_now')}"
        )
    if post_check.get("planned_schema_existing_files") != []:
        errors.append(f"selector post-check planned schema existing files not empty: {post_check.get('planned_schema_existing_files')}")
    if post_check.get("dangerous_flags_all_false") is not True:
        errors.append(f"selector post-check dangerous flags all false not true: {post_check.get('dangerous_flags_all_false')}")


def validate_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    loaded: Dict[str, Dict[str, Any]] = {}
    source_statuses: Dict[str, Dict[str, Any]] = {}
    checks: Dict[str, Any] = {}

    git_state = get_git_state()
    physical_before = physical_guard_snapshot()

    if git_state["head"] != EXPECTED_HEAD:
        errors.append(f"HEAD mismatch: expected={EXPECTED_HEAD} actual={git_state['head']}")
    if git_state["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked paths present before queue selector: {git_state['dirty_tracked_paths']}")
    if git_state["staged_count"] != 0:
        errors.append(f"staged paths present before queue selector: {git_state['staged_paths']}")
    if git_state["untracked_paths"] != [CURRENT_TOOL_REL]:
        errors.append(f"unexpected untracked paths before queue selector: expected={[CURRENT_TOOL_REL]} actual={git_state['untracked_paths']}")
    if physical_before["planned_schema_file_existing_count"] != 0:
        errors.append(f"planned schema files existed before queue selector: {physical_before['existing_planned_schema_files']}")
    if physical_before["generic_runner_target_file_exists_now"] is not False:
        errors.append(f"generic runner target file existed before queue selector: {GENERIC_RUNNER_TARGET_FILE}")

    subject = commit_subject("HEAD")
    paths = commit_paths("HEAD")
    checks["head_commit_subject"] = subject
    checks["head_commit_paths"] = paths
    if subject != "Add repo-only next action selector after generic governance blocked status backlog refresh":
        errors.append(f"unexpected HEAD commit subject: {subject}")
    if paths != ["tools/edge_factory_os_repo_only_next_action_selector_after_generic_governance_blocked_status_backlog_refresh_v1.py"]:
        errors.append(f"unexpected HEAD commit paths: {paths}")

    for key, spec in INPUTS.items():
        path, expected_status, expected_next_module = spec
        try:
            obj = load_json(path)
        except Exception as exc:
            errors.append(f"cannot load required input {key}: path={path} error={exc!r}")
            continue
        loaded[key] = obj
        record = source_record(path, obj)
        source_statuses[key] = record
        checks[key] = record
        validate_input_record(errors, key, record, expected_status, expected_next_module)
        safe, violations = dangerous_flags_are_false(obj)
        if not safe:
            errors.append(f"{key} dangerous flags not false: {violations}")

    selector_obj = loaded.get("next_action_selector", {})
    selector_post = loaded.get("next_action_selector_post_check", {})
    if selector_obj:
        if selector_obj.get("next_action") != EXPECTED_SELECTOR_ACTION:
            errors.append(f"selector next_action mismatch: {selector_obj.get('next_action')}")
        if selector_obj.get("final_decision") != EXPECTED_SELECTOR_FINAL_DECISION:
            errors.append(f"selector final_decision mismatch: {selector_obj.get('final_decision')}")
        validate_selector_proofs(errors, selector_obj)
    if selector_post:
        if selector_post.get("latest_commit") != EXPECTED_HEAD:
            errors.append(f"selector post-check latest_commit mismatch: expected={EXPECTED_HEAD} actual={selector_post.get('latest_commit')}")
        if selector_post.get("git_state", {}).get("head") != EXPECTED_HEAD:
            errors.append(f"selector post-check git head mismatch: expected={EXPECTED_HEAD} actual={selector_post.get('git_state', {}).get('head')}")
        if selector_post.get("next_action") != EXPECTED_SELECTOR_ACTION:
            errors.append(f"selector post-check next_action mismatch: {selector_post.get('next_action')}")
        validate_post_check_physical_guards(errors, selector_post)

    py = validate_tracked_python()
    checks["tracked_python"] = {
        "tracked_python_file_count": py["tracked_python_file_count"],
        "syntax_error_count": py["syntax_error_count"],
        "bom_error_count": py["bom_error_count"],
    }
    if py["tracked_python_file_count"] != EXPECTED_TRACKED_PYTHON_COUNT:
        errors.append(f"tracked Python count mismatch: expected={EXPECTED_TRACKED_PYTHON_COUNT} actual={py['tracked_python_file_count']}")
    if not py["pass"]:
        errors.append(f"tracked Python validation failed: syntax={py['syntax_errors'][:20]} bom={py['bom_errors']}")

    physical_after = physical_guard_snapshot()
    if physical_after["planned_schema_file_existing_count"] != 0:
        errors.append(f"planned schema files existed after queue selector: {physical_after['existing_planned_schema_files']}")
    if physical_after["generic_runner_target_file_exists_now"] is not False:
        errors.append(f"generic runner target file existed after queue selector: {GENERIC_RUNNER_TARGET_FILE}")

    return {
        "pass": not errors,
        "errors": errors,
        "loaded": loaded,
        "source_statuses": source_statuses,
        "checks": checks,
        "git_state": git_state,
        "tracked_python_validation": py,
        "expected_untracked_during_run": [CURRENT_TOOL_REL],
        "actual_untracked_during_run": git_state["untracked_paths"],
        "physical_before": physical_before,
        "physical_after": physical_after,
        "clean_baseline": not errors,
    }


def build_queue(validation: Dict[str, Any]) -> Dict[str, Any]:
    selector_obj = validation["loaded"].get("next_action_selector", {})
    selector = selector_obj.get("next_action_selector_after_generic_governance_blocked_status_backlog_refresh", {})
    selected_action = selector.get("selected_action", {}) if isinstance(selector, dict) else {}
    proofs = selector.get("confirmed_proofs", {}) if isinstance(selector, dict) else {}
    physical_after = validation["physical_after"]

    prerequisites = {
        "input_validation_pass": validation["pass"] is True,
        "selector_ready": selector_obj.get("next_action_selector_after_generic_governance_blocked_status_backlog_refresh_status") == EXPECTED_SELECTOR_STATUS,
        "selector_post_check_pass": validation["source_statuses"].get("next_action_selector_post_check", {}).get("status") == EXPECTED_SELECTOR_POST_STATUS,
        "selector_post_check_head_current": validation["source_statuses"].get("next_action_selector_post_check", {}).get("latest_commit") == EXPECTED_HEAD,
        "selector_selected_this_queue_selector": selected_action.get("module") == APPROVED_CURRENT_MODULE,
        "selector_selected_repo_only_scope": selected_action.get("scope") == "REPO_ONLY_OS_INTELLIGENCE",
        "selector_selected_allowed": selected_action.get("allowed") is True,
        "generic_governance_runner_implementation_remains_blocked": (
            proofs.get("generic_governance_runner_implementation_remains_blocked") is True
            and selector_obj.get("implementation_allowed_now") is False
            and selector_obj.get("generic_runner_implementation_allowed_now") is False
        ),
        "manual_approval_remains_absent": (
            proofs.get("manual_approval_remains_absent") is True
            and selector_obj.get("manual_approval_present_now") is False
            and selector_obj.get("manual_approval_present") is False
        ),
        "manual_approval_remains_invalid": (
            proofs.get("manual_approval_remains_invalid") is True
            and selector_obj.get("manual_approval_valid_now") is False
            and selector_obj.get("manual_approval_valid") is False
        ),
        "generic_runner_target_file_absent_before": validation["physical_before"]["generic_runner_target_file_exists_now"] is False,
        "generic_runner_target_file_absent_after": physical_after["generic_runner_target_file_exists_now"] is False,
        "generic_runner_file_creation_blocked": selector_obj.get("generic_runner_file_creation_allowed_now") is False,
        "config_file_creation_blocked": selector_obj.get("config_file_creation_allowed_now") is False,
        "config_schema_apply_runtime_paths_blocked": proofs.get("config_schema_apply_runtime_paths_remain_blocked") is True,
        "schema_apply_blocked": selector_obj.get("schema_apply_allowed_now") is False,
        "schema_file_creation_blocked": selector_obj.get("schema_file_creation_allowed_now") is False,
        "schema_file_edit_blocked": selector_obj.get("schema_file_edit_allowed_now") is False,
        "consolidation_apply_blocked": selector_obj.get("consolidation_apply_allowed_now") is False,
        "runtime_touch_blocked": selector_obj.get("runtime_touch_allowed_now") is False,
        "planned_schema_files_absent_before": validation["physical_before"]["planned_schema_file_existing_count"] == 0,
        "planned_schema_files_absent_after": physical_after["planned_schema_file_existing_count"] == 0,
        "tracked_python_clean": validation["tracked_python_validation"]["pass"] is True,
    }

    queue_items = [
        {
            "rank": 1,
            "key": "DEVELOPMENT_BACKLOG_REFRESH_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_REFRESH",
            "module": SELECTED_NEXT_MODULE,
            "scope": "REPO_ONLY_OS_INTELLIGENCE",
            "allowed": True,
            "reason": "Generic governance runner remains blocked; refresh the repo-only development backlog before any further selector step.",
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
            "reason": "Generic governance runner implementation remains blocked; no approval can be inferred.",
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
            "key": "STRATEGY_RESEARCH_OR_CANDIDATE_WORK",
            "module": None,
            "scope": "BLOCKED",
            "allowed": False,
            "reason": "Strategy research, holdout, candidate, and family release work remain outside this repo-only selector scope.",
            "blocked_actions": ["strategy_research", "holdout_access", "candidate_generation", "candidate_release", "family_release"],
        },
    ]
    selected = queue_items[0] if all(prerequisites.values()) else None

    return {
        "development_queue_status": (
            "DEVELOPMENT_QUEUE_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_REFRESH_ACTIVE"
            if selected
            else "DEVELOPMENT_QUEUE_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_REFRESH_BLOCKED"
        ),
        "queue_items": queue_items,
        "queue_item_count": len(queue_items),
        "allowed_queue_item_count": sum(1 for item in queue_items if item["allowed"]),
        "blocked_queue_item_count": sum(1 for item in queue_items if not item["allowed"]),
        "scope_counts": dict(Counter(item["scope"] for item in queue_items)),
        "selected_development_task": selected,
        "selected_next_module": selected["module"] if selected else None,
        "selected_next_action": SELECTED_NEXT_ACTION if selected else None,
        "selected_scope": selected["scope"] if selected else None,
        "prerequisites": prerequisites,
        "confirmed_proofs": {
            "generic_governance_runner_implementation_remains_blocked": prerequisites["generic_governance_runner_implementation_remains_blocked"],
            "manual_approval_remains_absent": prerequisites["manual_approval_remains_absent"],
            "manual_approval_remains_invalid": prerequisites["manual_approval_remains_invalid"],
            "generic_runner_target_file_remains_absent": (
                prerequisites["generic_runner_target_file_absent_before"]
                and prerequisites["generic_runner_target_file_absent_after"]
            ),
            "config_schema_apply_runtime_paths_remain_blocked": prerequisites["config_schema_apply_runtime_paths_blocked"],
            "next_action_selector_selected_repo_only_development_queue_selector_route": selected_action.get("module") == APPROVED_CURRENT_MODULE,
        },
        "context_summary": {
            "selector_status": selector_obj.get("next_action_selector_after_generic_governance_blocked_status_backlog_refresh_status"),
            "selector_final_decision": selector_obj.get("final_decision"),
            "selector_next_action": selector_obj.get("next_action"),
            "selector_next_module": selector_obj.get("next_module"),
            "selector_selected_module": selected_action.get("module"),
            "selector_selected_scope": selected_action.get("scope"),
            "selector_confirmed_proofs": proofs,
            "tracked_python_file_count": validation["tracked_python_validation"]["tracked_python_file_count"],
            "planned_schema_file_existing_count_before": validation["physical_before"]["planned_schema_file_existing_count"],
            "planned_schema_file_existing_count_after": physical_after["planned_schema_file_existing_count"],
            "generic_runner_target_file_exists_before": validation["physical_before"]["generic_runner_target_file_exists_now"],
            "generic_runner_target_file_exists_after": physical_after["generic_runner_target_file_exists_now"],
        },
        "physical_guards": {
            "before": validation["physical_before"],
            "after": physical_after,
            "planned_schema_file_existing_count": 0,
            "generic_runner_target_file_exists_now": False,
            **PHYSICAL_FALSE_FIELDS,
        },
        "queue_policy": {
            "development_backlog_refresh_selected": True,
            "generic_runner_implementation_stays_blocked": True,
            "manual_approval_stays_absent_invalid": True,
            "no_generic_runner_file_creation": True,
            "no_config_file_creation": True,
            "no_schema_file_creation_or_edit": True,
            "no_schema_apply": True,
            "no_consolidation_apply": True,
            "no_runtime_or_launcher": True,
            "no_capital_live_or_real_orders": True,
            "no_strategy_research_or_candidates": True,
            "no_holdout_access": True,
            "no_file_move_delete_restructure": True,
        },
        "invariants": {
            "queue_prerequisites_all_true": all(prerequisites.values()),
            "selected_module_is_development_backlog_refresh_after_generic_governance_blocked_status_backlog_refresh": (
                selected is not None and selected["module"] == SELECTED_NEXT_MODULE
            ),
            "selected_action_is_development_backlog_refresh": selected is not None and selected["key"] == "DEVELOPMENT_BACKLOG_REFRESH_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_REFRESH",
            "selected_scope_is_repo_only_os_intelligence": selected is not None and selected["scope"] == "REPO_ONLY_OS_INTELLIGENCE",
            "generic_runner_implementation_not_selected": selected is not None and selected["key"] != "GENERIC_GOVERNANCE_RUNNER_IMPLEMENTATION",
            "config_schema_apply_runtime_not_selected": selected is not None and selected["key"] != "CONFIG_SCHEMA_APPLY_RUNTIME_PATH",
            "strategy_research_or_candidate_work_not_selected": selected is not None and selected["key"] != "STRATEGY_RESEARCH_OR_CANDIDATE_WORK",
            "all_dangerous_flags_false": all(SAFETY_FLAGS.get(flag) is False for flag in DANGEROUS_FLAGS),
            "all_physical_performed_guards_false": all(value is False for value in PHYSICAL_FALSE_FIELDS.values()),
            "planned_schema_files_absent_before": validation["physical_before"]["planned_schema_file_existing_count"] == 0,
            "planned_schema_files_absent_after": physical_after["planned_schema_file_existing_count"] == 0,
            "generic_runner_target_absent_before": validation["physical_before"]["generic_runner_target_file_exists_now"] is False,
            "generic_runner_target_absent_after": physical_after["generic_runner_target_file_exists_now"] is False,
        },
    }


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_development_queue_selector_after_generic_governance_blocked_status_backlog_refresh_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_development_queue_selector_after_generic_governance_blocked_status_backlog_refresh_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_development_queue_selector_after_generic_governance_blocked_status_backlog_refresh_v1_latest.txt"

    rendered_json = json.dumps(payload, indent=2, sort_keys=True)
    latest_json.write_text(rendered_json, encoding="utf-8")
    timestamped_json.write_text(rendered_json, encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY DEVELOPMENT QUEUE SELECTOR AFTER GENERIC GOVERNANCE BLOCKED STATUS BACKLOG REFRESH v1",
        "=" * 100,
        f"development_queue_selector_after_generic_governance_blocked_status_backlog_refresh_status: {payload['development_queue_selector_after_generic_governance_blocked_status_backlog_refresh_status']}",
        f"severity: {payload['severity']}",
        f"final_decision: {payload['final_decision']}",
        f"next_action: {payload['next_action']}",
        f"next_module: {payload['next_module']}",
        f"critical_issue_count: {payload['critical_issue_count']}",
        f"warning_count: {payload['warning_count']}",
        "",
        "QUEUE SUMMARY",
        "-" * 100,
        json.dumps(
            {
                "selected_development_task": payload["development_queue_selector_after_generic_governance_blocked_status_backlog_refresh"]["selected_development_task"],
                "confirmed_proofs": payload["development_queue_selector_after_generic_governance_blocked_status_backlog_refresh"]["confirmed_proofs"],
                "queue_item_count": payload["development_queue_selector_after_generic_governance_blocked_status_backlog_refresh"]["queue_item_count"],
                "allowed_queue_item_count": payload["development_queue_selector_after_generic_governance_blocked_status_backlog_refresh"]["allowed_queue_item_count"],
                "blocked_queue_item_count": payload["development_queue_selector_after_generic_governance_blocked_status_backlog_refresh"]["blocked_queue_item_count"],
                "context_summary": payload["development_queue_selector_after_generic_governance_blocked_status_backlog_refresh"]["context_summary"],
                "physical_guards": payload["physical_guards"],
                "prerequisites": payload["development_queue_selector_after_generic_governance_blocked_status_backlog_refresh"]["prerequisites"],
                "queue_policy": payload["development_queue_selector_after_generic_governance_blocked_status_backlog_refresh"]["queue_policy"],
                "invariants": payload["development_queue_selector_after_generic_governance_blocked_status_backlog_refresh"]["invariants"],
            },
            indent=2,
            sort_keys=True,
        ),
        "",
        "ERRORS",
        "-" * 100,
        json.dumps(payload["errors"], indent=2, sort_keys=True),
        "",
        "SAFETY",
        "-" * 100,
        json.dumps(SAFETY_FLAGS, indent=2, sort_keys=True),
        "",
        "OUTPUTS",
        "-" * 100,
        f"latest_json: {latest_json}",
        f"timestamped_json: {timestamped_json}",
        f"latest_txt: {latest_txt}",
    ]
    latest_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "latest_json": str(latest_json),
        "timestamped_json": str(timestamped_json),
        "latest_txt": str(latest_txt),
    }


def main() -> int:
    safety_errors = [key for key, value in SAFETY_FLAGS.items() if not isinstance(value, bool)]
    validation = validate_inputs()
    errors = list(validation["errors"])
    if safety_errors:
        errors.append(f"safety flags are not boolean: {safety_errors}")

    queue = build_queue(validation)
    for key, value in queue["confirmed_proofs"].items():
        if value is not True:
            errors.append(f"confirmed proof not true: {key}={value}")
    for key, value in queue["invariants"].items():
        if value is not True:
            errors.append(f"invariant not true: {key}={value}")

    passed = not errors
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "development_queue_selector_after_generic_governance_blocked_status_backlog_refresh_status": (
            READY_STATUS
            if passed
            else "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_REFRESH_V1_BLOCKED"
        ),
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": FINAL_DECISION if passed else "KEEP_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_REFRESH_QUEUE_SELECTOR_ERRORS",
        "next_action": SELECTED_NEXT_ACTION if passed else "REVIEW_DEVELOPMENT_QUEUE_SELECTOR_AFTER_GENERIC_GOVERNANCE_BLOCKED_STATUS_BACKLOG_REFRESH_ERRORS",
        "next_module": SELECTED_NEXT_MODULE if passed else None,
        "reason": (
            "Selected repo-only development backlog refresh after the generic governance blocked-status backlog-refresh selector; all generic runner, config, schema, apply, runtime, approval, capital, strategy, candidate, and holdout paths remain blocked."
            if passed
            else "Development queue selector after generic governance blocked-status backlog refresh failed closed."
        ),
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "critical_issue_count": len(errors),
        "warning_count": 0,
        "errors": errors,
        "warnings": [],
        "validation": {
            "checks": validation["checks"],
            "git_state": validation["git_state"],
            "tracked_python_validation": validation["tracked_python_validation"],
            "source_statuses": validation["source_statuses"],
            "expected_untracked_during_run": validation["expected_untracked_during_run"],
            "actual_untracked_during_run": validation["actual_untracked_during_run"],
            "physical_before": validation["physical_before"],
            "physical_after": validation["physical_after"],
            "clean_baseline": validation["clean_baseline"],
        },
        "development_queue_selector_after_generic_governance_blocked_status_backlog_refresh": queue,
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "physical_guards": queue["physical_guards"],
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

    outputs = write_outputs(payload)
    payload["outputs"] = outputs
    write_outputs(payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["critical_issue_count"] == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
