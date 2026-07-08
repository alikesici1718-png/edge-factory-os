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

MODULE_NAME = "edge_factory_os_repo_only_development_queue_selector_after_standard_os_status_backlog_status_backlog_refresh_v1"
OUT_DIR = LAB_ROOT / MODULE_NAME
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD = "a3c12b2"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_development_queue_selector_after_standard_os_status_backlog_status_backlog_refresh_v1.py"
APPROVED_CURRENT_MODULE = "edge_factory_os_repo_only_development_queue_selector_after_standard_os_status_backlog_status_backlog_refresh_v1.py"
SELECTED_NEXT_MODULE = "edge_factory_os_repo_only_development_backlog_refresh_after_standard_os_status_backlog_status_backlog_refresh_v1.py"

AUTOPILOT_JSON = LAB_ROOT / "edge_factory_os_repo_only_autopilot_until_research_gate_v1" / "repo_only_autopilot_until_research_gate_v1_latest.json"
AUTOPILOT_POST_JSON = LAB_ROOT / "edge_factory_os_repo_only_autopilot_until_research_gate_post_commit_check" / "repo_only_autopilot_until_research_gate_post_commit_check_latest.json"
SELECTOR_JSON = LAB_ROOT / "edge_factory_os_repo_only_next_action_selector_after_standard_os_status_backlog_status_backlog_refresh_v1" / "repo_only_next_action_selector_after_standard_os_status_backlog_status_backlog_refresh_v1_latest.json"
SELECTOR_POST_JSON = LAB_ROOT / "edge_factory_os_repo_only_next_action_selector_after_standard_os_status_backlog_status_backlog_refresh_post_commit_check" / "repo_only_next_action_selector_after_standard_os_status_backlog_status_backlog_refresh_post_commit_check_latest.json"
BACKLOG_JSON = LAB_ROOT / "edge_factory_os_repo_only_development_backlog_refresh_after_standard_os_status_backlog_status_refresh_v1" / "repo_only_development_backlog_refresh_after_standard_os_status_backlog_status_refresh_v1_latest.json"
BACKLOG_POST_JSON = LAB_ROOT / "edge_factory_os_repo_only_development_backlog_refresh_after_standard_os_status_backlog_status_refresh_post_commit_check" / "repo_only_development_backlog_refresh_after_standard_os_status_backlog_status_refresh_post_commit_check_latest.json"

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
]

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_development_queue_selector_after_standard_os_status_backlog_status_backlog_refresh": True,
    "read_only_development_queue_selection_only": True,
    "autopilot_until_research_gate_required": True,
    "next_action_selector_after_standard_os_status_backlog_status_backlog_refresh_required": True,
    "development_backlog_refresh_after_standard_os_status_backlog_status_backlog_refresh_allowed_next": True,
    "repo_only_governance_allowed": True,
    "repo_only_audit_allowed": True,
    "read_only_validation_allowed": True,
}
SAFETY_FLAGS.update({name: False for name in DANGEROUS_FLAGS})

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

INPUTS: Dict[str, Tuple[Path, str, Optional[str]]] = {
    "autopilot": (AUTOPILOT_JSON, "PASS", APPROVED_CURRENT_MODULE),
    "autopilot_post_check": (
        AUTOPILOT_POST_JSON,
        "REPO_ONLY_AUTOPILOT_UNTIL_RESEARCH_GATE_POST_COMMIT_CHECK_PASS",
        APPROVED_CURRENT_MODULE,
    ),
    "next_action_selector": (
        SELECTOR_JSON,
        "REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_V1_READY",
        APPROVED_CURRENT_MODULE,
    ),
    "next_action_selector_post_check": (
        SELECTOR_POST_JSON,
        "REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_POST_COMMIT_CHECK_PASS",
        APPROVED_CURRENT_MODULE,
    ),
    "development_backlog": (
        BACKLOG_JSON,
        "REPO_ONLY_DEVELOPMENT_BACKLOG_REFRESH_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_REFRESH_V1_READY",
        "edge_factory_os_repo_only_next_action_selector_after_standard_os_status_backlog_status_backlog_refresh_v1.py",
    ),
    "development_backlog_post_check": (
        BACKLOG_POST_JSON,
        "REPO_ONLY_DEVELOPMENT_BACKLOG_REFRESH_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_REFRESH_POST_COMMIT_CHECK_PASS",
        "edge_factory_os_repo_only_next_action_selector_after_standard_os_status_backlog_status_backlog_refresh_v1.py",
    ),
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
        "runtime_touch_performed": False,
        "launcher_executed": False,
        "capital_change_performed": False,
        "live_or_real_order_performed": False,
        "holdout_access_performed": False,
        "file_move_performed": False,
        "file_delete_performed": False,
        "repo_restructure_performed": False,
    }


def get_git_state() -> Dict[str, Any]:
    status_lines = [
        line
        for line in run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"]).stdout.splitlines()
        if line.strip()
    ]
    untracked = [line[3:].replace("\\", "/") for line in status_lines if line.startswith("?? ")]
    dirty_tracked = [line for line in status_lines if not line.startswith("?? ")]
    return {
        "head": run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
        "branch": run_cmd(["git", "branch", "--show-current"]).stdout.strip(),
        "status_porcelain": status_lines,
        "dirty_tracked_count": len(dirty_tracked),
        "dirty_tracked_paths": [line[3:].replace("\\", "/") for line in dirty_tracked],
        "untracked_count": len(untracked),
        "untracked_paths": sorted(untracked),
        "git_dirty": bool(status_lines),
        "remote_status_short": run_cmd(["git", "status", "-sb", "--untracked-files=all"]).stdout.splitlines(),
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
        "next_module": obj.get("next_module"),
        "next_action": obj.get("next_action"),
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
        errors.append(
            f"{key} next_module mismatch: expected={expected_next_module} actual={record.get('next_module')}"
        )


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


def validate_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    loaded: Dict[str, Dict[str, Any]] = {}
    source_statuses: Dict[str, Dict[str, Any]] = {}
    checks: Dict[str, Any] = {}

    git_state = get_git_state()
    physical_before = physical_guard_snapshot()

    if git_state["head"] != EXPECTED_HEAD:
        errors.append(f"unexpected HEAD: expected={EXPECTED_HEAD} actual={git_state['head']}")

    expected_untracked = [CURRENT_TOOL_REL]
    if git_state["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked paths present before queue selector: {git_state['dirty_tracked_paths']}")
    if git_state["untracked_paths"] != expected_untracked:
        errors.append(f"unexpected untracked set before queue selector: expected={expected_untracked} actual={git_state['untracked_paths']}")
    if physical_before["planned_schema_file_existing_count"] != 0:
        errors.append(f"planned schema files existed before queue selector: {physical_before['existing_planned_schema_files']}")

    subject = commit_subject("HEAD")
    paths = commit_paths("HEAD")
    checks["head_commit_subject"] = subject
    checks["head_commit_paths"] = paths
    if subject != "Add repo-only autopilot until research gate":
        errors.append(f"unexpected HEAD commit subject: {subject}")
    if paths != ["tools/edge_factory_os_repo_only_autopilot_until_research_gate_v1.py"]:
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

    autopilot_post = source_statuses.get("autopilot_post_check", {})
    autopilot = loaded.get("autopilot", {})
    if autopilot_post.get("latest_commit") != EXPECTED_HEAD:
        errors.append(f"autopilot post-check latest_commit mismatch: expected={EXPECTED_HEAD} actual={autopilot_post.get('latest_commit')}")
    if autopilot_post.get("git_head") != EXPECTED_HEAD:
        errors.append(f"autopilot post-check git head mismatch: expected={EXPECTED_HEAD} actual={autopilot_post.get('git_head')}")
    if autopilot.get("autopilot_route_allowed_for_next_repo_only_step") is not True:
        errors.append("autopilot route is not allowed")
    if autopilot.get("research_or_manual_gate_required") is not False:
        errors.append("autopilot indicates research/manual gate required")

    selector = loaded.get("next_action_selector", {})
    selector_detail = selector.get("next_action_selector_after_standard_os_status_backlog_status_backlog_refresh", {})
    selected_action = selector_detail.get("selected_action", {}) if isinstance(selector_detail, dict) else {}
    latest_next_modules = sorted(
        set(
            str(value)
            for value in [
                autopilot.get("next_module"),
                autopilot_post.get("next_module"),
                selector.get("next_module"),
                selected_action.get("module"),
            ]
            if value
        )
    )
    checks["latest_next_modules"] = latest_next_modules
    if latest_next_modules != [APPROVED_CURRENT_MODULE]:
        errors.append(f"ambiguous or unexpected approved current module: expected={[APPROVED_CURRENT_MODULE]} actual={latest_next_modules}")
    if selected_action.get("allowed") is not True:
        errors.append("latest selector selected action is not allowed")
    if selected_action.get("scope") != "REPO_ONLY_OS_INTELLIGENCE":
        errors.append(f"latest selector selected action scope mismatch: {selected_action.get('scope')}")

    py = validate_tracked_python()
    checks["tracked_python"] = {
        "tracked_python_file_count": py["tracked_python_file_count"],
        "syntax_error_count": py["syntax_error_count"],
        "bom_error_count": py["bom_error_count"],
    }
    if not py["pass"]:
        errors.append(f"tracked Python validation failed: syntax={py['syntax_errors'][:20]} bom={py['bom_errors']}")
    if py["tracked_python_file_count"] != 509:
        errors.append(f"tracked Python count mismatch: expected=509 actual={py['tracked_python_file_count']}")

    physical_after = physical_guard_snapshot()
    if physical_after["planned_schema_file_existing_count"] != 0:
        errors.append(f"planned schema files existed after queue selector: {physical_after['existing_planned_schema_files']}")

    return {
        "pass": not errors,
        "errors": errors,
        "loaded": loaded,
        "source_statuses": source_statuses,
        "checks": checks,
        "git_state": git_state,
        "tracked_python_validation": py,
        "expected_untracked_during_run": expected_untracked,
        "actual_untracked_during_run": git_state["untracked_paths"],
        "physical_before": physical_before,
        "physical_after": physical_after,
        "clean_baseline": not errors,
    }


def build_queue(validation: Dict[str, Any]) -> Dict[str, Any]:
    selector_obj = validation["loaded"].get("next_action_selector", {})
    selector = selector_obj.get("next_action_selector_after_standard_os_status_backlog_status_backlog_refresh", {})
    selected_action = selector.get("selected_action", {}) if isinstance(selector, dict) else {}
    selector_context = selector.get("context_summary", {}) if isinstance(selector, dict) else {}
    effective_schema_state = selector_context.get("effective_schema_state", {})
    effective_approval_state = selector_context.get("effective_approval_state", {})
    physical_after = validation["physical_after"]

    prerequisites = {
        "autopilot_post_check_pass": validation["source_statuses"].get("autopilot_post_check", {}).get("status") == "REPO_ONLY_AUTOPILOT_UNTIL_RESEARCH_GATE_POST_COMMIT_CHECK_PASS",
        "autopilot_head_current": validation["source_statuses"].get("autopilot_post_check", {}).get("latest_commit") == EXPECTED_HEAD,
        "autopilot_route_allowed": validation["loaded"].get("autopilot", {}).get("autopilot_route_allowed_for_next_repo_only_step") is True,
        "autopilot_no_research_manual_gate": validation["loaded"].get("autopilot", {}).get("research_or_manual_gate_required") is False,
        "selector_ready": selector_obj.get("next_action_selector_after_standard_os_status_backlog_status_backlog_refresh_status") == "REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_V1_READY",
        "selector_selected_this_queue_selector": selected_action.get("module") == APPROVED_CURRENT_MODULE,
        "selector_selected_repo_only_scope": selected_action.get("scope") == "REPO_ONLY_OS_INTELLIGENCE",
        "selector_selected_allowed": selected_action.get("allowed") is True,
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
        "launcher_not_executed": physical_after["launcher_executed"] is False,
        "capital_change_not_performed": physical_after["capital_change_performed"] is False,
        "live_or_real_order_not_performed": physical_after["live_or_real_order_performed"] is False,
        "holdout_access_not_performed": physical_after["holdout_access_performed"] is False,
        "file_move_not_performed": physical_after["file_move_performed"] is False,
        "file_delete_not_performed": physical_after["file_delete_performed"] is False,
        "repo_restructure_not_performed": physical_after["repo_restructure_performed"] is False,
        "tracked_python_clean": validation["tracked_python_validation"]["pass"] is True,
    }

    queue_items = [
        {
            "rank": 1,
            "key": "DEVELOPMENT_BACKLOG_REFRESH_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH",
            "module": SELECTED_NEXT_MODULE,
            "scope": "REPO_ONLY_OS_INTELLIGENCE",
            "allowed": True,
            "reason": "Autopilot-approved queue selector is clean; refresh repo-only development backlog before any further selector step.",
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
            "key": "SCHEMA_REGISTRY_APPLY",
            "module": "edge_factory_os_repo_only_framework_schema_registry_apply_v1.py",
            "scope": "BLOCKED_REQUIRES_EXPLICIT_SCHEMA_APPROVAL",
            "allowed": False,
            "reason": "Schema apply remains blocked without exact manual approval.",
            "blocked_actions": ["schema_file_creation", "schema_file_edit", "schema_apply"],
        },
        {
            "rank": 3,
            "key": "RUNTIME_OR_CAPITAL_RESUME",
            "module": None,
            "scope": "BLOCKED",
            "allowed": False,
            "reason": "Runtime, launcher, capital, live, and real-order actions remain blocked.",
            "blocked_actions": ["runtime_touch", "launcher_execution", "capital_change", "active_paper_change", "live_trading", "real_orders"],
        },
        {
            "rank": 4,
            "key": "STRATEGY_RESEARCH_OR_CANDIDATE_WORK",
            "module": None,
            "scope": "BLOCKED_REQUIRES_FUTURE_EXPLICIT_APPROVAL",
            "allowed": False,
            "reason": "Strategy research, holdout, candidate, and family release work remain blocked.",
            "blocked_actions": ["strategy_research", "candidate_generation", "candidate_release", "family_release", "holdout_access"],
        },
    ]
    selected = queue_items[0] if all(prerequisites.values()) else None

    return {
        "development_queue_status": "DEVELOPMENT_QUEUE_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_ACTIVE" if selected else "DEVELOPMENT_QUEUE_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_BLOCKED",
        "queue_items": queue_items,
        "queue_item_count": len(queue_items),
        "allowed_queue_item_count": sum(1 for item in queue_items if item["allowed"]),
        "blocked_queue_item_count": sum(1 for item in queue_items if not item["allowed"]),
        "scope_counts": dict(Counter(item["scope"] for item in queue_items)),
        "selected_development_task": selected,
        "selected_next_module": selected["module"] if selected else None,
        "selected_next_action": "BUILD_REPO_ONLY_DEVELOPMENT_BACKLOG_REFRESH_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_V1" if selected else None,
        "selected_scope": selected["scope"] if selected else None,
        "prerequisites": prerequisites,
        "context_summary": {
            "autopilot_next_module": validation["loaded"].get("autopilot", {}).get("next_module"),
            "selector_selected_module": selected_action.get("module"),
            "selector_selected_scope": selected_action.get("scope"),
            "effective_approval_state": effective_approval_state,
            "effective_schema_state": effective_schema_state,
            "tracked_python_file_count": validation["tracked_python_validation"]["tracked_python_file_count"],
            "planned_schema_file_existing_count_before": validation["physical_before"]["planned_schema_file_existing_count"],
            "planned_schema_file_existing_count_after": physical_after["planned_schema_file_existing_count"],
        },
        "physical_guards": {
            "before": validation["physical_before"],
            "after": physical_after,
        },
        "queue_policy": {
            "autopilot_route_obeyed": True,
            "development_backlog_refresh_selected": True,
            "schema_apply_stays_blocked_without_exact_manual_approval": True,
            "no_schema_file_creation_or_edit": True,
            "no_runtime_or_capital_work": True,
            "no_strategy_research_or_candidates": True,
            "no_holdout_access": True,
            "no_file_move_delete_restructure": True,
        },
        "invariants": {
            "queue_prerequisites_all_true": all(prerequisites.values()),
            "selected_module_is_development_backlog_refresh_after_standard_os_status_backlog_status_backlog_refresh": selected is not None and selected["module"] == SELECTED_NEXT_MODULE,
            "selected_scope_is_repo_only_os_intelligence": selected is not None and selected["scope"] == "REPO_ONLY_OS_INTELLIGENCE",
            "schema_apply_not_selected": selected is not None and selected["key"] != "SCHEMA_REGISTRY_APPLY",
            "runtime_or_capital_not_selected": selected is not None and selected["key"] != "RUNTIME_OR_CAPITAL_RESUME",
            "strategy_research_or_candidate_work_not_selected": selected is not None and selected["key"] != "STRATEGY_RESEARCH_OR_CANDIDATE_WORK",
            "planned_schema_files_absent_before": validation["physical_before"]["planned_schema_file_existing_count"] == 0,
            "planned_schema_files_absent_after": physical_after["planned_schema_file_existing_count"] == 0,
            "schema_apply_not_performed": physical_after["schema_apply_performed_count"] == 0,
            "schema_file_creation_not_performed": physical_after["schema_file_creation_performed_count"] == 0,
            "schema_file_edit_not_performed": physical_after["schema_file_edit_performed_count"] == 0,
            "runtime_touch_not_performed": physical_after["runtime_touch_performed"] is False,
            "launcher_not_executed": physical_after["launcher_executed"] is False,
            "capital_change_not_performed": physical_after["capital_change_performed"] is False,
            "live_or_real_order_not_performed": physical_after["live_or_real_order_performed"] is False,
            "holdout_access_not_performed": physical_after["holdout_access_performed"] is False,
            "file_move_not_performed": physical_after["file_move_performed"] is False,
            "file_delete_not_performed": physical_after["file_delete_performed"] is False,
            "repo_restructure_not_performed": physical_after["repo_restructure_performed"] is False,
            "no_runtime_strategy_capital_holdout_or_candidates_authorized": True,
        },
    }


def main() -> int:
    safety_errors = [key for key, value in SAFETY_FLAGS.items() if not isinstance(value, bool)]
    validation = validate_inputs()
    errors = list(validation["errors"])
    if safety_errors:
        errors.append(f"safety flags are not boolean: {safety_errors}")

    queue = build_queue(validation)
    for key, value in queue["invariants"].items():
        if value is not True:
            errors.append(f"invariant {key} not true: {value}")

    passed = not errors
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "development_queue_selector_after_standard_os_status_backlog_status_backlog_refresh_status": "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_V1_READY" if passed else "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_V1_BLOCKED",
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": "DEVELOPMENT_QUEUE_SELECTED_BACKLOG_REFRESH_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH" if passed else "KEEP_FREEZE_REVIEW_DEVELOPMENT_QUEUE_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_ERRORS",
        "next_action": "BUILD_REPO_ONLY_DEVELOPMENT_BACKLOG_REFRESH_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_V1" if passed else "REVIEW_DEVELOPMENT_QUEUE_AFTER_STANDARD_OS_STATUS_BACKLOG_STATUS_BACKLOG_REFRESH_ERRORS",
        "next_module": SELECTED_NEXT_MODULE if passed else None,
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
        "development_queue_selector_after_standard_os_status_backlog_status_backlog_refresh": queue,
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "stage_recommended_now": False,
        "commit_recommended_now": False,
    }
    for flag in DANGEROUS_FLAGS:
        payload[flag] = False

    latest_json = OUT_DIR / "repo_only_development_queue_selector_after_standard_os_status_backlog_status_backlog_refresh_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_development_queue_selector_after_standard_os_status_backlog_status_backlog_refresh_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "repo_only_development_queue_selector_after_standard_os_status_backlog_status_backlog_refresh_v1_latest.txt"
    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY DEVELOPMENT QUEUE SELECTOR AFTER STANDARD OS STATUS BACKLOG STATUS BACKLOG REFRESH v1",
        "=" * 100,
        f"status: {payload['development_queue_selector_after_standard_os_status_backlog_status_backlog_refresh_status']}",
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
                "selected_development_task": queue["selected_development_task"],
                "queue_item_count": queue["queue_item_count"],
                "allowed_queue_item_count": queue["allowed_queue_item_count"],
                "blocked_queue_item_count": queue["blocked_queue_item_count"],
                "context_summary": queue["context_summary"],
                "physical_guards": queue["physical_guards"],
                "prerequisites": queue["prerequisites"],
                "queue_policy": queue["queue_policy"],
                "invariants": queue["invariants"],
            },
            indent=2,
            sort_keys=True,
        ),
        "",
        "ERRORS",
        "-" * 100,
        json.dumps(errors, indent=2, sort_keys=True),
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
