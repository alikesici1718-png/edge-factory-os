from __future__ import annotations

import ast
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_development_backlog_refresh_after_standard_os_status_backlog_status_refresh_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_repo_only_development_backlog_refresh_after_standard_os_status_backlog_status_refresh_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "ebdf1c6"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_development_backlog_refresh_after_standard_os_status_backlog_status_refresh_v1.py"

QUEUE_JSON = LAB_ROOT / "edge_factory_os_repo_only_development_queue_selector_after_standard_os_status_backlog_status_refresh_v1" / "repo_only_development_queue_selector_after_standard_os_status_backlog_status_refresh_v1_latest.json"
QUEUE_POST_JSON = LAB_ROOT / "edge_factory_os_repo_only_development_queue_selector_after_standard_os_status_backlog_status_refresh_post_commit_check" / "repo_only_development_queue_selector_after_standard_os_status_backlog_status_refresh_post_commit_check_latest.json"
SELECTOR_JSON = LAB_ROOT / "edge_factory_os_repo_only_next_action_selector_after_standard_os_status_backlog_status_refresh_v1" / "repo_only_next_action_selector_after_standard_os_status_backlog_status_refresh_v1_latest.json"
SELECTOR_POST_JSON = LAB_ROOT / "edge_factory_os_repo_only_next_action_selector_after_standard_os_status_backlog_status_refresh_post_commit_check" / "repo_only_next_action_selector_after_standard_os_status_backlog_status_refresh_post_commit_check_latest.json"

SELECTED_NEXT_MODULE = "edge_factory_os_repo_only_next_action_selector_after_standard_os_status_backlog_status_backlog_refresh_v1.py"

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

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_development_backlog_refresh_after_standard_os_status_backlog_status_refresh": True,
    "read_only_backlog_refresh_only": True,
    "development_queue_selector_after_standard_os_status_backlog_status_refresh_required": True,
    "next_action_selector_after_standard_os_status_backlog_status_backlog_refresh_allowed_next": True,

    "repo_only_governance_allowed": True,
    "repo_only_audit_allowed": True,
    "read_only_validation_allowed": True,

    "manual_approval_present": False,
    "manual_approval_valid": False,
    "approval_granted_now": False,
    "apply_allowed_now": False,

    "schema_file_creation_allowed_now": False,
    "schema_file_edit_allowed_now": False,
    "schema_apply_allowed_now": False,
    "schema_file_creation_performed_now": False,
    "schema_file_edit_performed_now": False,
    "schema_apply_performed_now": False,

    "framework_readme_edit_allowed_now": False,
    "framework_readme_edit_performed_now": False,
    "framework_file_creation_allowed_now": False,
    "framework_directory_creation_allowed_now": False,
    "framework_file_creation_performed_now": False,
    "framework_directory_creation_performed_now": False,

    "file_move_allowed_now": False,
    "file_delete_allowed_now": False,
    "repo_restructure_allowed_now": False,
    "overwrite_existing_files_allowed": False,
    "modify_existing_files_allowed": False,

    "manual_review_allowed_now": False,
    "risk_file_edit_allowed_now": False,
    "risk_file_execution_allowed_now": False,
    "patch_allowed_now": False,
    "apply_performed_now": False,
    "commit_performed_now": False,
    "stage_performed_now": False,
    "direct_apply_allowed": False,

    "runtime_touch_allowed": False,
    "launcher_allowed": False,
    "capital_change_allowed": False,
    "active_paper_allowed": False,
    "live_allowed": False,
    "real_orders_allowed": False,

    "candidate_generation_allowed": False,
    "candidate_release_allowed": False,
    "family_release_allowed": False,
    "strategy_research_allowed": False,
    "holdout_access_allowed": False,

    "gitignore_change_allowed": False,
    "backup_delete_allowed": False,
    "backup_move_allowed": False,
    "git_add_force_allowed": False,
    "mass_metadata_patch_allowed": False,
    "blind_fix_all_allowed": False,
}

FORBIDDEN_ACTIONS = [
    "create_schema_files_now",
    "edit_schema_files_now",
    "apply_schema_registry_now",
    "runtime_touch",
    "launcher_execution",
    "capital_change",
    "active_paper_change",
    "live_trading",
    "real_order_execution",
    "strategy_research",
    "candidate_generation",
    "candidate_release",
    "family_release",
    "holdout_access",
    "gitignore_change",
    "backup_delete",
    "backup_move",
    "git_add_force",
    "blind_fix_all",
    "mass_metadata_patch",
    "direct_apply",
    "overwrite_existing_files",
    "modify_existing_files",
    "move_files",
    "delete_files",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {args} returncode={result.returncode} stderr={result.stderr}")
    return result


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def physical_guard_snapshot() -> Dict[str, Any]:
    existing = planned_schema_existing_files()
    return {
        "planned_schema_rel_paths": PLANNED_SCHEMA_REL_PATHS,
        "planned_schema_path_count": len(PLANNED_SCHEMA_REL_PATHS),
        "existing_planned_schema_files": existing,
        "planned_schema_file_existing_count": len(existing),
        "schema_apply_performed_count": 0,
        "schema_file_creation_performed_count": 0,
        "schema_file_edit_performed_count": 0,
        "framework_readme_edit_performed_count": 0,
        "runtime_touch_performed": False,
        "capital_change_performed": False,
        "live_or_real_order_performed": False,
        "holdout_access_performed": False,
        "file_move_performed": False,
        "file_delete_performed": False,
        "repo_restructure_performed": False,
    }


def get_git_state() -> Dict[str, Any]:
    status_lines = [
        x
        for x in run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"]).stdout.splitlines()
        if x.strip()
    ]
    untracked = [x[3:] for x in status_lines if x.startswith("?? ")]
    dirty_tracked = [x for x in status_lines if not x.startswith("?? ")]

    return {
        "head": run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
        "branch": run_cmd(["git", "branch", "--show-current"]).stdout.strip(),
        "status_porcelain": status_lines,
        "dirty_tracked_count": len(dirty_tracked),
        "dirty_tracked_paths": [x[3:] for x in dirty_tracked],
        "untracked_count": len(untracked),
        "untracked_paths": untracked,
        "git_dirty": bool(status_lines),
        "remote_status_short": run_cmd(["git", "status", "-sb", "--untracked-files=all"]).stdout.splitlines(),
    }


def tracked_python_files() -> List[str]:
    return sorted(x.strip().replace("\\", "/") for x in run_cmd(["git", "ls-files", "*.py"]).stdout.splitlines() if x.strip())


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
    return sorted(x.strip().replace("\\", "/") for x in lines if x.strip())


def first_status(obj: Dict[str, Any]) -> Optional[str]:
    for key in [
        "development_queue_selector_after_standard_os_status_backlog_status_refresh_status",
        "audit_status",
        "next_action_selector_after_standard_os_status_backlog_status_refresh_status",
    ]:
        value = obj.get(key)
        if value:
            return str(value)
    return None


def source_record(path: Path, obj: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "path": str(path),
        "status": first_status(obj),
        "critical_issue_count": obj.get("critical_issue_count"),
        "warning_count": obj.get("warning_count"),
        "next_module": obj.get("next_module"),
        "final_decision": obj.get("final_decision"),
    }


def validate_count_zero(errors: List[str], key: str, record: Dict[str, Any], field: str) -> None:
    value = record.get(field)
    if value is None:
        errors.append(f"{key} {field} field missing")
        return
    if value != 0:
        errors.append(f"{key} {field} not 0: {value}")


def validate_status_record(errors: List[str], key: str, record: Dict[str, Any], expected_status: str, expected_next_module: Optional[str] = None) -> None:
    status = record.get("status")
    if status is None:
        errors.append(f"{key} status field missing")
    elif status != expected_status:
        errors.append(f"{key} status mismatch: expected={expected_status} actual={status}")

    validate_count_zero(errors, key, record, "critical_issue_count")
    validate_count_zero(errors, key, record, "warning_count")

    if expected_next_module is not None and record.get("next_module") != expected_next_module:
        errors.append(f"{key} next_module mismatch: expected={expected_next_module} actual={record.get('next_module')}")


def validate_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    loaded: Dict[str, Dict[str, Any]] = {}
    source_statuses: Dict[str, Dict[str, Any]] = {}
    checks: Dict[str, Any] = {}

    git_state = get_git_state()
    physical_before = physical_guard_snapshot()

    if not git_state["head"].startswith(EXPECTED_HEAD_PREFIX):
        errors.append(f"unexpected HEAD: {git_state['head']} expected {EXPECTED_HEAD_PREFIX}")

    expected_untracked = {CURRENT_TOOL_REL}
    actual_untracked = set(git_state["untracked_paths"])

    if git_state["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked paths present before backlog refresh: {git_state['dirty_tracked_paths']}")

    if actual_untracked != expected_untracked:
        errors.append(f"unexpected untracked set before backlog refresh: expected={sorted(expected_untracked)} actual={sorted(actual_untracked)}")

    if physical_before["planned_schema_file_existing_count"] != 0:
        errors.append(f"planned schema files existed before backlog refresh: {physical_before['existing_planned_schema_files']}")

    subject = commit_subject("HEAD")
    checks["head_commit_subject"] = subject
    if subject != "Add repo-only development queue selector after standard OS status backlog status refresh":
        errors.append(f"unexpected HEAD commit subject: {subject}")

    paths = commit_paths("HEAD")
    checks["head_commit_paths"] = paths
    if paths != ["tools/edge_factory_os_repo_only_development_queue_selector_after_standard_os_status_backlog_status_refresh_v1.py"]:
        errors.append(f"unexpected HEAD commit paths: {paths}")

    inputs = {
        "development_queue_selector": (
            QUEUE_JSON,
            "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_REFRESH_V1_READY",
            "edge_factory_os_repo_only_development_backlog_refresh_after_standard_os_status_backlog_status_refresh_v1.py",
        ),
        "development_queue_selector_post_check": (
            QUEUE_POST_JSON,
            "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_REFRESH_POST_COMMIT_CHECK_PASS",
            "edge_factory_os_repo_only_development_backlog_refresh_after_standard_os_status_backlog_status_refresh_v1.py",
        ),
        "next_action_selector": (
            SELECTOR_JSON,
            "REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_REFRESH_V1_READY",
            None,
        ),
        "next_action_selector_post_check": (
            SELECTOR_POST_JSON,
            "REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_REFRESH_POST_COMMIT_CHECK_PASS",
            None,
        ),
    }

    for key, spec in inputs.items():
        path, expected_status, expected_next_module = spec
        obj: Optional[Dict[str, Any]] = None
        record: Optional[Dict[str, Any]] = None

        try:
            obj = load_json(path)
            loaded[key] = obj
            record = source_record(path, obj)
        except Exception as exc:
            errors.append(f"cannot load {key}: {path} error={repr(exc)}")

        if record is not None:
            source_statuses[key] = record
            checks[key] = record
            validate_status_record(errors, key, record, expected_status, expected_next_module)

    py = validate_tracked_python()
    checks["tracked_python"] = {
        "tracked_python_file_count": py["tracked_python_file_count"],
        "syntax_error_count": py["syntax_error_count"],
        "bom_error_count": py["bom_error_count"],
    }

    if not py["pass"]:
        errors.append(f"tracked Python validation failed: syntax={py['syntax_errors'][:20]} bom={py['bom_errors']}")

    return {
        "pass": not errors,
        "errors": errors,
        "loaded": loaded,
        "source_statuses": source_statuses,
        "checks": checks,
        "git_state": git_state,
        "tracked_python_validation": py,
        "expected_untracked_during_run": sorted(expected_untracked),
        "actual_untracked_during_run": sorted(actual_untracked),
        "physical_before": physical_before,
        "clean_baseline": not errors,
    }


def build_backlog(validation: Dict[str, Any]) -> Dict[str, Any]:
    queue_obj = validation["loaded"]["development_queue_selector"]
    queue = queue_obj.get("development_queue_selector_after_standard_os_status_backlog_status_refresh", {})
    selected_task = queue.get("selected_development_task", {})
    queue_context = queue.get("context_summary", {})
    effective_schema_state = queue_context.get("effective_schema_state", {})
    effective_approval_state = queue_context.get("effective_approval_state", {})

    selector_obj = validation["loaded"]["next_action_selector"]
    selector = selector_obj.get("next_action_selector_after_standard_os_status_backlog_status_refresh", {})
    selected_action = selector.get("selected_action", {})

    physical_after = physical_guard_snapshot()

    prerequisites = {
        "queue_ready": queue_obj.get("development_queue_selector_after_standard_os_status_backlog_status_refresh_status") == "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_REFRESH_V1_READY",
        "queue_selected_this_backlog_refresh": selected_task.get("module") == "edge_factory_os_repo_only_development_backlog_refresh_after_standard_os_status_backlog_status_refresh_v1.py",
        "queue_selected_repo_only_scope": selected_task.get("scope") == "REPO_ONLY_OS_INTELLIGENCE",
        "selector_ready": selector_obj.get("next_action_selector_after_standard_os_status_backlog_status_refresh_status") == "REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_REFRESH_V1_READY",
        "selector_selected_queue": selected_action.get("module") == "edge_factory_os_repo_only_development_queue_selector_after_standard_os_status_backlog_status_refresh_v1.py",
        "manual_approval_absent": effective_approval_state.get("manual_approval_present") is False,
        "manual_approval_invalid": effective_approval_state.get("manual_approval_valid") is False,
        "approval_granted_false": effective_approval_state.get("approval_granted_now") is False,
        "schema_apply_allowed_false": effective_schema_state.get("schema_apply_allowed_now") is False,
        "schema_file_creation_allowed_false": effective_schema_state.get("schema_file_creation_allowed_now") is False,
        "schema_file_edit_allowed_false": effective_schema_state.get("schema_file_edit_allowed_now") is False,
        "planned_schema_files_absent_before": validation["physical_before"]["planned_schema_file_existing_count"] == 0,
        "planned_schema_files_absent_after": physical_after["planned_schema_file_existing_count"] == 0,
        "schema_apply_not_performed": physical_after["schema_apply_performed_count"] == 0,
        "schema_file_creation_not_performed": physical_after["schema_file_creation_performed_count"] == 0,
        "schema_file_edit_not_performed": physical_after["schema_file_edit_performed_count"] == 0,
        "runtime_touch_not_performed": physical_after["runtime_touch_performed"] is False,
        "capital_change_not_performed": physical_after["capital_change_performed"] is False,
        "live_or_real_order_not_performed": physical_after["live_or_real_order_performed"] is False,
        "holdout_access_not_performed": physical_after["holdout_access_performed"] is False,
        "file_move_not_performed": physical_after["file_move_performed"] is False,
        "file_delete_not_performed": physical_after["file_delete_performed"] is False,
        "repo_restructure_not_performed": physical_after["repo_restructure_performed"] is False,
        "tracked_python_clean": validation["tracked_python_validation"]["pass"] is True,
    }

    backlog_items = [
        {
            "rank": 1,
            "key": "NEXT_ACTION_SELECTOR_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH",
            "module": SELECTED_NEXT_MODULE,
            "scope": "REPO_ONLY_OS_INTELLIGENCE",
            "allowed": True,
            "reason": "Backlog refreshed after standard OS status backlog status refresh; select next repo-only development task.",
            "blocked_actions": [
                "schema_file_creation",
                "schema_file_edit",
                "schema_apply",
                "runtime_touch",
                "launcher_execution",
                "capital_change",
                "active_paper_change",
                "live_trading",
                "real_orders",
                "holdout_access",
                "strategy_research",
                "candidate_generation",
                "candidate_release",
                "family_release",
                "file_move",
                "file_delete",
                "repo_restructure",
            ],
        },
        {
            "rank": 2,
            "key": "SCHEMA_REGISTRY_APPLY_RETRY",
            "module": "edge_factory_os_repo_only_framework_schema_registry_apply_v1.py",
            "scope": "BLOCKED_REQUIRES_EXPLICIT_SCHEMA_APPROVAL",
            "allowed": False,
            "reason": "Schema apply remains blocked because no valid explicit manual approval exists.",
            "blocked_actions": ["schema_file_creation", "schema_file_edit", "schema_apply"],
        },
        {
            "rank": 3,
            "key": "RUNTIME_OR_CAPITAL_RESUME",
            "module": None,
            "scope": "BLOCKED",
            "allowed": False,
            "reason": "Runtime/capital/live actions remain blocked.",
            "blocked_actions": ["runtime_touch", "launcher_execution", "capital_change", "active_paper_change", "live_trading", "real_orders"],
        },
        {
            "rank": 4,
            "key": "STRATEGY_RESEARCH_RESUME",
            "module": None,
            "scope": "BLOCKED_REQUIRES_FUTURE_EXPLICIT_APPROVAL",
            "allowed": False,
            "reason": "Strategy research remains blocked until a future explicit governance decision.",
            "blocked_actions": ["strategy_research", "candidate_generation", "candidate_release", "family_release", "holdout_access"],
        },
    ]

    selected = backlog_items[0] if all(prerequisites.values()) else None

    return {
        "backlog_refresh_status": "DEVELOPMENT_BACKLOG_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_REFRESH_READY" if selected else "DEVELOPMENT_BACKLOG_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_REFRESH_BLOCKED",
        "backlog_items": backlog_items,
        "backlog_item_count": len(backlog_items),
        "allowed_backlog_item_count": sum(1 for item in backlog_items if item["allowed"]),
        "blocked_backlog_item_count": sum(1 for item in backlog_items if not item["allowed"]),
        "scope_counts": dict(Counter(item["scope"] for item in backlog_items)),
        "selected_next_backlog_item": selected,
        "selected_next_module": selected["module"] if selected else None,
        "selected_next_action": "BUILD_REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_V1" if selected else None,
        "selected_scope": selected["scope"] if selected else None,
        "prerequisites": prerequisites,
        "context_summary": {
            "queue_selected_module": selected_task.get("module"),
            "selector_selected_module": selected_action.get("module"),
            "effective_approval_state": effective_approval_state,
            "effective_schema_state": effective_schema_state,
            "queue_context": queue_context,
            "planned_schema_file_existing_count_before": validation["physical_before"]["planned_schema_file_existing_count"],
            "planned_schema_file_existing_count_after": physical_after["planned_schema_file_existing_count"],
        },
        "physical_guards": {
            "before": validation["physical_before"],
            "after": physical_after,
        },
        "backlog_policy": {
            "backlog_refresh_only": True,
            "next_action_selector_selected": True,
            "schema_apply_stays_blocked_without_exact_manual_approval": True,
            "no_schema_file_creation_or_edit": True,
            "no_runtime_or_capital_work": True,
            "no_strategy_research": True,
            "no_file_move_delete_restructure": True,
        },
        "invariants": {
            "backlog_prerequisites_all_true": all(prerequisites.values()),
            "selected_module_is_next_action_selector_after_standard_os_status_backlog_status_backlog_refresh": selected is not None and selected["module"] == SELECTED_NEXT_MODULE,
            "selected_scope_is_repo_only_os_intelligence": selected is not None and selected["scope"] == "REPO_ONLY_OS_INTELLIGENCE",
            "schema_apply_not_selected": selected is not None and selected["key"] != "SCHEMA_REGISTRY_APPLY_RETRY",
            "strategy_research_not_selected": selected is not None and selected["key"] != "STRATEGY_RESEARCH_RESUME",
            "runtime_or_capital_not_selected": selected is not None and selected["key"] != "RUNTIME_OR_CAPITAL_RESUME",
            "planned_schema_files_absent_before": validation["physical_before"]["planned_schema_file_existing_count"] == 0,
            "planned_schema_files_absent_after": physical_after["planned_schema_file_existing_count"] == 0,
            "schema_apply_not_performed": physical_after["schema_apply_performed_count"] == 0,
            "schema_file_creation_not_performed": physical_after["schema_file_creation_performed_count"] == 0,
            "schema_file_edit_not_performed": physical_after["schema_file_edit_performed_count"] == 0,
            "runtime_touch_not_performed": physical_after["runtime_touch_performed"] is False,
            "capital_change_not_performed": physical_after["capital_change_performed"] is False,
            "live_or_real_order_not_performed": physical_after["live_or_real_order_performed"] is False,
            "holdout_access_not_performed": physical_after["holdout_access_performed"] is False,
            "file_move_not_performed": physical_after["file_move_performed"] is False,
            "file_delete_not_performed": physical_after["file_delete_performed"] is False,
            "repo_restructure_not_performed": physical_after["repo_restructure_performed"] is False,
            "no_runtime_strategy_or_capital_authorized": True,
            "no_repo_file_creation_or_modification_performed_by_backlog_refresh": True,
        },
    }


def main() -> int:
    safety_errors = [key for key, value in SAFETY_FLAGS.items() if not isinstance(value, bool)]

    validation = validate_inputs()
    errors = list(validation["errors"])

    if safety_errors:
        errors.append(f"safety flags are not boolean: {safety_errors}")

    backlog = build_backlog(validation)

    for key, value in backlog["invariants"].items():
        if value is not True:
            errors.append(f"invariant {key} not true: {value}")

    passed = not errors

    payload = {
        "module": MODULE_NAME,
        "development_backlog_refresh_after_standard_os_status_backlog_status_refresh_status": "REPO_ONLY_DEVELOPMENT_BACKLOG_REFRESH_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_REFRESH_V1_READY" if passed else "REPO_ONLY_DEVELOPMENT_BACKLOG_REFRESH_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_REFRESH_V1_BLOCKED",
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": "DEVELOPMENT_BACKLOG_REFRESH_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_REFRESH_READY_FOR_NEXT_ACTION_SELECTOR" if passed else "KEEP_FREEZE_REVIEW_DEVELOPMENT_BACKLOG_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_REFRESH_ERRORS",
        "next_action": "BUILD_REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_V1" if passed else "REVIEW_DEVELOPMENT_BACKLOG_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_REFRESH_ERRORS",
        "next_module": SELECTED_NEXT_MODULE if passed else None,
        "reason": "Development backlog refreshed after standard OS status backlog status refresh; schema apply/create/edit remain blocked and physically absent." if passed else "Development backlog refresh after standard OS status backlog status refresh validation failed.",
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
            "clean_baseline": validation["clean_baseline"],
        },
        "development_backlog_refresh_after_standard_os_status_backlog_status_refresh": backlog,
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "apply_allowed_now": False,
        "apply_performed_now": False,
        "stage_recommended_now": False,
        "commit_recommended_now": False,
        "runtime_action_recommended_now": False,
        "capital_action_recommended_now": False,
        "holdout_action_recommended_now": False,
        "strategy_research_recommended_now": False,
        "candidate_generation_recommended_now": False,
        "candidate_release_recommended_now": False,
        "family_release_recommended_now": False,
        "schema_file_creation_allowed_now": False,
        "schema_file_edit_allowed_now": False,
        "schema_apply_allowed_now": False,
        "schema_file_creation_performed_now": False,
        "schema_file_edit_performed_now": False,
        "schema_apply_performed_now": False,
        "framework_file_creation_performed_now": False,
        "framework_directory_creation_performed_now": False,
        "framework_readme_edit_performed_now": False,
        "manual_approval_present": False,
        "manual_approval_valid": False,
        "approval_granted_now": False,
        "manual_review_allowed_now": False,
        "risk_file_edit_allowed_now": False,
        "risk_file_execution_allowed_now": False,
        "runtime_touched": False,
        "launcher_executed": False,
        "capital_changed": False,
        "live_or_real_orders": False,
        "holdout_accessed": False,
        "backup_deleted": False,
        "gitignore_changed": False,
        "git_add_force_used": False,
        "physical_planned_schema_file_existing_count_before": backlog["physical_guards"]["before"]["planned_schema_file_existing_count"],
        "physical_planned_schema_file_existing_count_after": backlog["physical_guards"]["after"]["planned_schema_file_existing_count"],
    }

    latest_json = OUT_DIR / "repo_only_development_backlog_refresh_after_standard_os_status_backlog_status_refresh_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_development_backlog_refresh_after_standard_os_status_backlog_status_refresh_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "repo_only_development_backlog_refresh_after_standard_os_status_backlog_status_refresh_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY DEVELOPMENT BACKLOG REFRESH AFTER STANDARD OS STATUS BACKLOG STATUS REFRESH v1",
        "=" * 100,
        f"development_backlog_refresh_after_standard_os_status_backlog_status_refresh_status: {payload['development_backlog_refresh_after_standard_os_status_backlog_status_refresh_status']}",
        f"severity: {payload['severity']}",
        f"final_decision: {payload['final_decision']}",
        f"next_action: {payload['next_action']}",
        f"next_module: {payload['next_module']}",
        f"reason: {payload['reason']}",
        f"critical_issue_count: {payload['critical_issue_count']}",
        f"warning_count: {payload['warning_count']}",
        "",
        "ERRORS",
        "-" * 100,
        json.dumps(errors, indent=2, sort_keys=True),
        "",
        "BACKLOG SUMMARY",
        "-" * 100,
        json.dumps(
            {
                "selected_next_backlog_item": backlog["selected_next_backlog_item"],
                "backlog_item_count": backlog["backlog_item_count"],
                "allowed_backlog_item_count": backlog["allowed_backlog_item_count"],
                "blocked_backlog_item_count": backlog["blocked_backlog_item_count"],
                "context_summary": backlog["context_summary"],
                "physical_guards": backlog["physical_guards"],
                "prerequisites": backlog["prerequisites"],
                "backlog_policy": backlog["backlog_policy"],
                "invariants": backlog["invariants"],
            },
            indent=2,
            sort_keys=True,
        ),
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
    print("\n".join(lines))
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())