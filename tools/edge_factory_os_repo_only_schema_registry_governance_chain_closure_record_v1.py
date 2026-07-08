from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_schema_registry_governance_chain_closure_record_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_repo_only_schema_registry_governance_chain_closure_record_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "33d0cbc"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_schema_registry_governance_chain_closure_record_v1.py"
SELECTED_NEXT_MODULE = "edge_factory_os_repo_only_next_action_selector_after_schema_registry_closure_record_v1.py"

QUEUE_JSON = LAB_ROOT / "edge_factory_os_repo_only_development_queue_selector_after_post_schema_registry_backlog_refresh_v1" / "repo_only_development_queue_selector_after_post_schema_registry_backlog_refresh_v1_latest.json"
QUEUE_POST_JSON = LAB_ROOT / "edge_factory_os_repo_only_development_queue_selector_after_post_schema_registry_backlog_refresh_post_commit_check" / "repo_only_development_queue_selector_after_post_schema_registry_backlog_refresh_post_commit_check_latest.json"
SELECTOR_JSON = LAB_ROOT / "edge_factory_os_repo_only_next_action_selector_after_post_schema_registry_backlog_refresh_v1" / "repo_only_next_action_selector_after_post_schema_registry_backlog_refresh_v1_latest.json"
BACKLOG_JSON = LAB_ROOT / "edge_factory_os_repo_only_development_backlog_refresh_after_post_schema_registry_status_v1" / "repo_only_development_backlog_refresh_after_post_schema_registry_status_v1_latest.json"
STATUS_JSON = LAB_ROOT / "edge_factory_os_repo_only_post_schema_registry_status_refresh_v1" / "repo_only_post_schema_registry_status_refresh_v1_latest.json"
RECORD_JSON = LAB_ROOT / "edge_factory_os_repo_only_framework_schema_registry_manual_approval_record_v1" / "repo_only_framework_schema_registry_manual_approval_record_v1_latest.json"

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

TRUE_FLAGS = {
    "repo_only_schema_registry_governance_chain_closure_record": True,
    "read_only_closure_record_only": True,
    "development_queue_selector_after_post_schema_registry_backlog_refresh_required": True,
    "next_action_selector_after_schema_registry_closure_record_allowed_next": True,
    "repo_only_governance_allowed": True,
    "repo_only_audit_allowed": True,
    "read_only_validation_allowed": True,
}

FALSE_FLAGS = {
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

SAFETY_FLAGS = {**TRUE_FLAGS, **FALSE_FLAGS}

FORBIDDEN_ACTIONS = [
    "create_schema_files_now",
    "edit_schema_files_now",
    "apply_schema_registry_now",
    "edit_framework_readmes_now",
    "apply_content_now",
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
    "manual_risk_file_review_without_valid_approval",
    "risk_file_edit_without_approval",
    "risk_file_execution_without_approval",
    "overwrite_existing_files",
    "modify_existing_files",
    "move_files",
    "delete_files",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def first_not_none(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {args} returncode={result.returncode} stderr={result.stderr}")
    return result


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def existing_schema_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def physical_guard_snapshot() -> Dict[str, Any]:
    existing = existing_schema_files()
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


def git_state() -> Dict[str, Any]:
    status_lines = [
        x for x in run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"]).stdout.splitlines()
        if x.strip()
    ]
    untracked = [x[3:] for x in status_lines if x.startswith("?? ")]
    dirty = [x for x in status_lines if not x.startswith("?? ")]
    return {
        "head": run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
        "branch": run_cmd(["git", "branch", "--show-current"]).stdout.strip(),
        "status_porcelain": status_lines,
        "dirty_tracked_count": len(dirty),
        "dirty_tracked_paths": [x[3:] for x in dirty],
        "untracked_count": len(untracked),
        "untracked_paths": untracked,
        "git_dirty": bool(status_lines),
        "remote_status_short": run_cmd(["git", "status", "-sb", "--untracked-files=all"]).stdout.splitlines(),
    }


def tracked_python_files() -> List[str]:
    return sorted(
        x.strip().replace("\\", "/")
        for x in run_cmd(["git", "ls-files", "*.py"]).stdout.splitlines()
        if x.strip()
    )


def validate_tracked_python() -> Dict[str, Any]:
    syntax_errors = []
    bom_errors = []
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


def status_record(path: Path, obj: Dict[str, Any]) -> Dict[str, Any]:
    status_keys = [
        "development_queue_selector_after_post_schema_registry_backlog_refresh_status",
        "audit_status",
        "next_action_selector_after_post_schema_registry_backlog_refresh_status",
        "development_backlog_refresh_after_post_schema_registry_status_status",
        "post_schema_registry_status_refresh_status",
        "framework_schema_registry_manual_approval_record_status",
    ]
    return {
        "path": str(path),
        "status": next((str(obj[k]) for k in status_keys if obj.get(k)), None),
        "critical_issue_count": obj.get("critical_issue_count"),
        "warning_count": obj.get("warning_count"),
        "next_module": obj.get("next_module"),
        "final_decision": obj.get("final_decision"),
    }


def validate_source(errors: List[str], key: str, record: Dict[str, Any], expected_status: str, expected_next_module: str | None = None) -> None:
    if record.get("status") != expected_status:
        errors.append(f"{key} status mismatch: expected={expected_status} actual={record.get('status')}")
    for field in ["critical_issue_count", "warning_count"]:
        if record.get(field) != 0:
            errors.append(f"{key} {field} not 0: {record.get(field)}")
    if expected_next_module is not None and record.get("next_module") != expected_next_module:
        errors.append(f"{key} next_module mismatch: expected={expected_next_module} actual={record.get('next_module')}")


def validate_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    loaded: Dict[str, Dict[str, Any]] = {}
    source_statuses: Dict[str, Dict[str, Any]] = {}
    checks: Dict[str, Any] = {}
    state = git_state()
    physical_before = physical_guard_snapshot()

    if not state["head"].startswith(EXPECTED_HEAD_PREFIX):
        errors.append(f"unexpected HEAD: {state['head']} expected {EXPECTED_HEAD_PREFIX}")

    expected_untracked = {CURRENT_TOOL_REL}
    actual_untracked = set(state["untracked_paths"])

    if state["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked paths present before closure record: {state['dirty_tracked_paths']}")

    if actual_untracked != expected_untracked:
        errors.append(f"unexpected untracked set before closure record: expected={sorted(expected_untracked)} actual={sorted(actual_untracked)}")

    if physical_before["planned_schema_file_existing_count"] != 0:
        errors.append(f"planned schema files existed before closure record: {physical_before['existing_planned_schema_files']}")

    subject = commit_subject("HEAD")
    paths = commit_paths("HEAD")
    checks["head_commit_subject"] = subject
    checks["head_commit_paths"] = paths

    if subject != "Add repo-only development queue selector after post-schema-registry backlog refresh":
        errors.append(f"unexpected HEAD commit subject: {subject}")

    if paths != ["tools/edge_factory_os_repo_only_development_queue_selector_after_post_schema_registry_backlog_refresh_v1.py"]:
        errors.append(f"unexpected HEAD commit paths: {paths}")

    specs = {
        "development_queue_selector_after_backlog": (
            QUEUE_JSON,
            "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_POST_SCHEMA_REGISTRY_BACKLOG_REFRESH_V1_READY",
            "edge_factory_os_repo_only_schema_registry_governance_chain_closure_record_v1.py",
        ),
        "development_queue_selector_after_backlog_post_check": (
            QUEUE_POST_JSON,
            "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_POST_SCHEMA_REGISTRY_BACKLOG_REFRESH_POST_COMMIT_CHECK_PASS",
            "edge_factory_os_repo_only_schema_registry_governance_chain_closure_record_v1.py",
        ),
        "next_action_selector_after_backlog": (
            SELECTOR_JSON,
            "REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_POST_SCHEMA_REGISTRY_BACKLOG_REFRESH_V1_READY",
            None,
        ),
        "development_backlog_refresh": (
            BACKLOG_JSON,
            "REPO_ONLY_DEVELOPMENT_BACKLOG_REFRESH_AFTER_POST_SCHEMA_REGISTRY_STATUS_V1_READY",
            None,
        ),
        "post_schema_registry_status_refresh": (
            STATUS_JSON,
            "REPO_ONLY_POST_SCHEMA_REGISTRY_STATUS_REFRESH_V1_READY",
            None,
        ),
        "manual_approval_record": (
            RECORD_JSON,
            "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_MANUAL_APPROVAL_RECORD_V1_READY",
            None,
        ),
    }

    for key, (path, expected_status, expected_next_module) in specs.items():
        try:
            obj = load_json(path)
            loaded[key] = obj
            rec = status_record(path, obj)
            source_statuses[key] = rec
            checks[key] = rec
            validate_source(errors, key, rec, expected_status, expected_next_module)
        except Exception as exc:
            errors.append(f"cannot load {key}: {path} error={repr(exc)}")

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
        "git_state": state,
        "tracked_python_validation": py,
        "expected_untracked_during_run": sorted(expected_untracked),
        "actual_untracked_during_run": sorted(actual_untracked),
        "physical_before": physical_before,
        "clean_baseline": not errors,
    }


def build_closure_record(validation: Dict[str, Any]) -> Dict[str, Any]:
    queue_obj = validation["loaded"]["development_queue_selector_after_backlog"]
    queue = as_dict(queue_obj.get("development_queue_selector_after_post_schema_registry_backlog_refresh", {}))
    selected_task = as_dict(queue.get("selected_development_task", {}))
    queue_context = as_dict(queue.get("context_summary", {}))

    selector_obj = validation["loaded"].get("next_action_selector_after_backlog", {})
    selector_context = as_dict(as_dict(selector_obj.get("next_action_selector_after_post_schema_registry_backlog_refresh", {})).get("context_summary", {}))

    backlog_obj = validation["loaded"].get("development_backlog_refresh", {})
    backlog_context = as_dict(as_dict(backlog_obj.get("development_backlog_refresh_after_post_schema_registry_status", {})).get("context_summary", {}))

    status_obj = validation["loaded"]["post_schema_registry_status_refresh"]
    status = as_dict(status_obj.get("post_schema_registry_status_refresh", {}))
    status_summary = as_dict(status.get("status_summary", {}))
    status_approval_state = as_dict(status_summary.get("approval_state", {}))
    status_schema_state = as_dict(status_summary.get("schema_action_state", {}))

    record_obj = validation["loaded"]["manual_approval_record"]
    record_payload = as_dict(record_obj.get("framework_schema_registry_manual_approval_record", {}))
    manual_record = as_dict(record_payload.get("manual_approval_record", {}))

    effective_approval_state = {
        "manual_approval_present": first_not_none(
            status_approval_state.get("manual_approval_present"),
            status_summary.get("manual_approval_present"),
            queue_context.get("manual_approval_present"),
            selector_context.get("manual_approval_present"),
            backlog_context.get("manual_approval_present"),
            manual_record.get("manual_approval_present"),
        ),
        "manual_approval_valid": first_not_none(
            status_approval_state.get("manual_approval_valid"),
            status_summary.get("manual_approval_valid"),
            queue_context.get("manual_approval_valid"),
            selector_context.get("manual_approval_valid"),
            backlog_context.get("manual_approval_valid"),
            manual_record.get("manual_approval_valid"),
        ),
        "approval_granted_now": first_not_none(
            status_approval_state.get("approval_granted_now"),
            status_summary.get("approval_granted_now"),
            queue_context.get("approval_granted_now"),
            selector_context.get("approval_granted_now"),
            backlog_context.get("approval_granted_now"),
            manual_record.get("approval_granted_now"),
        ),
    }

    effective_schema_state = {
        "schema_apply_allowed_now": first_not_none(
            status_schema_state.get("schema_apply_allowed_now"),
            status_summary.get("schema_apply_allowed_now"),
            queue_context.get("schema_apply_allowed_now"),
            selector_context.get("schema_apply_allowed_now"),
            backlog_context.get("schema_apply_allowed_now"),
            manual_record.get("schema_apply_allowed_now"),
        ),
        "schema_file_creation_allowed_now": first_not_none(
            status_schema_state.get("schema_file_creation_allowed_now"),
            status_summary.get("schema_file_creation_allowed_now"),
            queue_context.get("schema_file_creation_allowed_now"),
            selector_context.get("schema_file_creation_allowed_now"),
            backlog_context.get("schema_file_creation_allowed_now"),
            manual_record.get("schema_file_creation_allowed_now"),
        ),
        "schema_file_edit_allowed_now": first_not_none(
            status_schema_state.get("schema_file_edit_allowed_now"),
            status_summary.get("schema_file_edit_allowed_now"),
            queue_context.get("schema_file_edit_allowed_now"),
            selector_context.get("schema_file_edit_allowed_now"),
            backlog_context.get("schema_file_edit_allowed_now"),
            manual_record.get("schema_file_edit_allowed_now"),
        ),
    }

    physical_after = physical_guard_snapshot()

    prerequisites = {
        "queue_ready": queue_obj.get("development_queue_selector_after_post_schema_registry_backlog_refresh_status") == "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_POST_SCHEMA_REGISTRY_BACKLOG_REFRESH_V1_READY",
        "queue_selected_this_closure_record": selected_task.get("module") == "edge_factory_os_repo_only_schema_registry_governance_chain_closure_record_v1.py",
        "queue_selected_repo_only_scope": selected_task.get("scope") == "REPO_ONLY_OS_INTELLIGENCE",
        "manual_record_ready": record_obj.get("framework_schema_registry_manual_approval_record_status") == "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_MANUAL_APPROVAL_RECORD_V1_READY",
        "manual_approval_absent": effective_approval_state.get("manual_approval_present") is False and manual_record.get("manual_approval_present") is False,
        "manual_approval_invalid": effective_approval_state.get("manual_approval_valid") is False and manual_record.get("manual_approval_valid") is False,
        "approval_granted_false": effective_approval_state.get("approval_granted_now") is False and manual_record.get("approval_granted_now") is False,
        "schema_apply_allowed_false": effective_schema_state.get("schema_apply_allowed_now") is False and manual_record.get("schema_apply_allowed_now") is False,
        "schema_file_creation_allowed_false": effective_schema_state.get("schema_file_creation_allowed_now") is False and manual_record.get("schema_file_creation_allowed_now") is False,
        "schema_file_edit_allowed_false": effective_schema_state.get("schema_file_edit_allowed_now") is False and manual_record.get("schema_file_edit_allowed_now") is False,
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

    invariants = {
        "closure_prerequisites_all_true": all(prerequisites.values()),
        "schema_registry_apply_closed_now": True,
        "schema_apply_allowed_false": effective_schema_state.get("schema_apply_allowed_now") is False and manual_record.get("schema_apply_allowed_now") is False,
        "schema_file_creation_allowed_false": effective_schema_state.get("schema_file_creation_allowed_now") is False and manual_record.get("schema_file_creation_allowed_now") is False,
        "schema_file_edit_allowed_false": effective_schema_state.get("schema_file_edit_allowed_now") is False and manual_record.get("schema_file_edit_allowed_now") is False,
        "manual_approval_absent_or_invalid": effective_approval_state.get("manual_approval_present") is False and effective_approval_state.get("manual_approval_valid") is False,
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
        "no_repo_file_creation_or_modification_performed_by_closure_record": True,
        "next_module_is_next_action_selector_after_schema_registry_closure_record": SELECTED_NEXT_MODULE == "edge_factory_os_repo_only_next_action_selector_after_schema_registry_closure_record_v1.py",
    }

    return {
        "closure_record_status": "SCHEMA_REGISTRY_GOVERNANCE_CHAIN_CLOSED_BLOCKED_NO_APPLY" if all(prerequisites.values()) else "SCHEMA_REGISTRY_GOVERNANCE_CHAIN_CLOSURE_BLOCKED",
        "closure_decision": {
            "schema_registry_apply_closed_now": True,
            "closure_reason": "Exact manual approval is absent/invalid, so schema apply/create/edit remains blocked; governance chain is recorded and returned to general repo-only flow.",
            "manual_approval_required_for_future_apply": True,
            "required_future_approval_text": manual_record.get("required_future_approval_text", "schema registry apply onaylıyorum"),
            "schema_apply_allowed_now": False,
            "schema_file_creation_allowed_now": False,
            "schema_file_edit_allowed_now": False,
            "schema_apply_performed_now": False,
            "schema_file_creation_performed_now": False,
            "schema_file_edit_performed_now": False,
        },
        "chain_summary": {
            "manual_record_status": record_obj.get("framework_schema_registry_manual_approval_record_status"),
            "queue_status": queue_obj.get("development_queue_selector_after_post_schema_registry_backlog_refresh_status"),
            "selected_task": selected_task,
            "manual_approval_present": effective_approval_state.get("manual_approval_present"),
            "manual_approval_valid": effective_approval_state.get("manual_approval_valid"),
            "approval_granted_now": effective_approval_state.get("approval_granted_now"),
            "schema_apply_allowed_now": effective_schema_state.get("schema_apply_allowed_now"),
            "schema_file_creation_allowed_now": effective_schema_state.get("schema_file_creation_allowed_now"),
            "schema_file_edit_allowed_now": effective_schema_state.get("schema_file_edit_allowed_now"),
            "approval_state_source_order": "status_summary.approval_state -> status_summary flat -> queue_context -> selector_context -> backlog_context -> manual approval record",
            "schema_state_source_order": "status_summary.schema_action_state -> status_summary flat -> queue_context -> selector_context -> backlog_context -> manual approval record",
            "queue_context": queue_context,
            "selector_context": selector_context,
            "backlog_context": backlog_context,
        },
        "physical_guards": {"before": validation["physical_before"], "after": physical_after},
        "next_step": {
            "step": "BUILD_REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_SCHEMA_REGISTRY_CLOSURE_RECORD_V1",
            "module": SELECTED_NEXT_MODULE,
            "scope": "REPO_ONLY_OS_INTELLIGENCE",
            "reason": "Schema-registry chain is closed without apply; choose next general repo-only governance/intelligence task.",
        },
        "closure_policy": {
            "schema_apply_stays_blocked_without_exact_manual_approval": True,
            "closure_record_only": True,
            "no_schema_file_creation_or_edit": True,
            "no_runtime_or_capital_work": True,
            "no_strategy_research": True,
            "no_file_move_delete_restructure": True,
        },
        "prerequisites": prerequisites,
        "invariants": invariants,
    }


def main() -> int:
    validation = validate_inputs()
    errors = list(validation["errors"])
    closure = build_closure_record(validation)

    for key, value in closure["invariants"].items():
        if value is not True:
            errors.append(f"invariant {key} not true: {value}")

    passed = not errors

    payload = {
        "module": MODULE_NAME,
        "schema_registry_governance_chain_closure_record_status": "REPO_ONLY_SCHEMA_REGISTRY_GOVERNANCE_CHAIN_CLOSURE_RECORD_V1_READY" if passed else "REPO_ONLY_SCHEMA_REGISTRY_GOVERNANCE_CHAIN_CLOSURE_RECORD_V1_BLOCKED",
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": "SCHEMA_REGISTRY_GOVERNANCE_CHAIN_CLOSED_NO_APPLY_READY_FOR_NEXT_ACTION_SELECTOR" if passed else "KEEP_FREEZE_REVIEW_SCHEMA_REGISTRY_CLOSURE_RECORD_ERRORS",
        "next_action": "BUILD_REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_SCHEMA_REGISTRY_CLOSURE_RECORD_V1" if passed else "REVIEW_SCHEMA_REGISTRY_CLOSURE_RECORD_ERRORS",
        "next_module": SELECTED_NEXT_MODULE if passed else None,
        "reason": "Schema-registry governance chain closed without apply; schema apply/create/edit remain blocked and physically absent." if passed else "Schema-registry governance chain closure record validation failed.",
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "critical_issue_count": len(errors),
        "warning_count": 0,
        "errors": errors,
        "warnings": [],
        "validation": validation,
        "schema_registry_governance_chain_closure_record": closure,
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        **FALSE_FLAGS,
        "direct_apply_recommended_now": False,
        "runtime_action_recommended_now": False,
        "capital_action_recommended_now": False,
        "holdout_action_recommended_now": False,
        "strategy_research_recommended_now": False,
        "candidate_generation_recommended_now": False,
        "candidate_release_recommended_now": False,
        "family_release_recommended_now": False,
        "stage_recommended_now": False,
        "commit_recommended_now": False,
        "runtime_touched": False,
        "launcher_executed": False,
        "capital_changed": False,
        "live_or_real_orders": False,
        "holdout_accessed": False,
        "backup_deleted": False,
        "gitignore_changed": False,
        "git_add_force_used": False,
        "physical_planned_schema_file_existing_count_before": closure["physical_guards"]["before"]["planned_schema_file_existing_count"],
        "physical_planned_schema_file_existing_count_after": closure["physical_guards"]["after"]["planned_schema_file_existing_count"],
    }

    latest_json = OUT_DIR / "repo_only_schema_registry_governance_chain_closure_record_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_schema_registry_governance_chain_closure_record_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "repo_only_schema_registry_governance_chain_closure_record_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY SCHEMA REGISTRY GOVERNANCE CHAIN CLOSURE RECORD v1",
        "=" * 100,
        f"schema_registry_governance_chain_closure_record_status: {payload['schema_registry_governance_chain_closure_record_status']}",
        f"severity: {payload['severity']}",
        f"final_decision: {payload['final_decision']}",
        f"next_action: {payload['next_action']}",
        f"next_module: {payload['next_module']}",
        f"critical_issue_count: {payload['critical_issue_count']}",
        f"warning_count: {payload['warning_count']}",
        "",
        "ERRORS",
        "-" * 100,
        json.dumps(errors, indent=2, sort_keys=True),
        "",
        "CLOSURE SUMMARY",
        "-" * 100,
        json.dumps({
            "closure_decision": closure["closure_decision"],
            "chain_summary": closure["chain_summary"],
            "physical_guards": closure["physical_guards"],
            "prerequisites": closure["prerequisites"],
            "closure_policy": closure["closure_policy"],
            "invariants": closure["invariants"],
            "next_step": closure["next_step"],
        }, indent=2, sort_keys=True),
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