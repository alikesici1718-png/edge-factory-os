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

MODULE_NAME = "edge_factory_os_repo_only_development_queue_selector_after_post_framework_status_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_repo_only_development_queue_selector_after_post_framework_status_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "13b2ff2"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_development_queue_selector_after_post_framework_status_v1.py"

SELECTOR_JSON = LAB_ROOT / "edge_factory_os_repo_only_next_action_selector_after_post_framework_status_v1" / "repo_only_next_action_selector_after_post_framework_status_v1_latest.json"
SELECTOR_POST_JSON = LAB_ROOT / "edge_factory_os_repo_only_next_action_selector_after_post_framework_status_post_commit_check" / "repo_only_next_action_selector_after_post_framework_status_post_commit_check_latest.json"
STATUS_JSON = LAB_ROOT / "edge_factory_os_repo_only_post_framework_status_refresh_v1" / "repo_only_post_framework_status_refresh_v1_latest.json"
STATUS_POST_JSON = LAB_ROOT / "edge_factory_os_repo_only_post_framework_status_refresh_post_commit_check" / "repo_only_post_framework_status_refresh_post_commit_check_latest.json"
BACKLOG_JSON = LAB_ROOT / "edge_factory_os_repo_only_development_backlog_refresh_after_framework_readme_gate_v1" / "repo_only_development_backlog_refresh_after_framework_readme_gate_v1_latest.json"
PANEL_JSON = LAB_ROOT / "edge_factory_os_repo_only_governance_status_panel_after_framework_skeleton_v1" / "repo_only_governance_status_panel_after_framework_skeleton_v1_latest.json"
MANIFEST_JSON = LAB_ROOT / "edge_factory_os_repo_only_active_core_manifest_refresh_after_framework_skeleton_v1" / "repo_only_active_core_manifest_refresh_after_framework_skeleton_v1_latest.json"
MODULE_INDEX_JSON = LAB_ROOT / "edge_factory_os_repo_only_module_index_refresh_after_framework_skeleton_v1" / "repo_only_module_index_refresh_after_framework_skeleton_v1_latest.json"
CAPABILITY_JSON = LAB_ROOT / "edge_factory_os_repo_only_capability_map_refresh_after_framework_skeleton_v1" / "repo_only_capability_map_refresh_after_framework_skeleton_v1_latest.json"

SELECTED_NEXT_MODULE = "edge_factory_os_repo_only_framework_schema_registry_contract_v1.py"

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_development_queue_selector_after_post_framework_status": True,
    "read_only_development_queue_selection_only": True,
    "next_action_selector_after_post_framework_status_required": True,
    "readme_apply_block_respected": True,

    "repo_only_governance_allowed": True,
    "repo_only_audit_allowed": True,
    "read_only_validation_allowed": True,

    "framework_schema_registry_contract_allowed_next": True,

    "manual_approval_present": False,
    "manual_approval_valid": False,
    "approval_granted_now": False,
    "apply_allowed_now": False,

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


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {args} returncode={result.returncode} stderr={result.stderr}")
    return result


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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
        "next_action_selector_after_post_framework_status_status",
        "audit_status",
        "post_framework_status_refresh_status",
        "development_backlog_refresh_after_framework_readme_gate_status",
        "governance_status_panel_after_framework_skeleton_status",
        "active_core_manifest_after_framework_skeleton_status",
        "module_index_after_framework_skeleton_status",
        "capability_map_after_framework_skeleton_status",
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

    if not git_state["head"].startswith(EXPECTED_HEAD_PREFIX):
        errors.append(f"unexpected HEAD: {git_state['head']} expected {EXPECTED_HEAD_PREFIX}")

    expected_untracked = {CURRENT_TOOL_REL}
    actual_untracked = set(git_state["untracked_paths"])

    if git_state["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked paths present before development queue selector: {git_state['dirty_tracked_paths']}")

    if actual_untracked != expected_untracked:
        errors.append(f"unexpected untracked set before development queue selector: expected={sorted(expected_untracked)} actual={sorted(actual_untracked)}")

    subject = commit_subject("HEAD")
    checks["head_commit_subject"] = subject
    if subject != "Add repo-only next-action selector after post-framework status":
        errors.append(f"unexpected HEAD commit subject: {subject}")

    paths = commit_paths("HEAD")
    checks["head_commit_paths"] = paths
    if paths != ["tools/edge_factory_os_repo_only_next_action_selector_after_post_framework_status_v1.py"]:
        errors.append(f"unexpected HEAD commit paths: {paths}")

    inputs = {
        "next_action_selector": (
            SELECTOR_JSON,
            "REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_POST_FRAMEWORK_STATUS_V1_READY",
            "edge_factory_os_repo_only_development_queue_selector_after_post_framework_status_v1.py",
        ),
        "next_action_selector_post_check": (
            SELECTOR_POST_JSON,
            "REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_POST_FRAMEWORK_STATUS_POST_COMMIT_CHECK_PASS",
            "edge_factory_os_repo_only_development_queue_selector_after_post_framework_status_v1.py",
        ),
        "post_framework_status_refresh": (
            STATUS_JSON,
            "REPO_ONLY_POST_FRAMEWORK_STATUS_REFRESH_V1_READY",
            None,
        ),
        "post_framework_status_refresh_post_check": (
            STATUS_POST_JSON,
            "REPO_ONLY_POST_FRAMEWORK_STATUS_REFRESH_POST_COMMIT_CHECK_PASS",
            None,
        ),
        "backlog_refresh": (
            BACKLOG_JSON,
            "REPO_ONLY_DEVELOPMENT_BACKLOG_REFRESH_AFTER_FRAMEWORK_README_GATE_V1_READY",
            None,
        ),
        "governance_panel": (
            PANEL_JSON,
            "REPO_ONLY_GOVERNANCE_STATUS_PANEL_AFTER_FRAMEWORK_SKELETON_V1_READY",
            None,
        ),
        "active_core_manifest": (
            MANIFEST_JSON,
            "REPO_ONLY_ACTIVE_CORE_MANIFEST_REFRESH_AFTER_FRAMEWORK_SKELETON_V1_READY",
            None,
        ),
        "module_index": (
            MODULE_INDEX_JSON,
            "REPO_ONLY_MODULE_INDEX_REFRESH_AFTER_FRAMEWORK_SKELETON_V1_READY",
            None,
        ),
        "capability_map": (
            CAPABILITY_JSON,
            "REPO_ONLY_CAPABILITY_MAP_REFRESH_AFTER_FRAMEWORK_SKELETON_V1_READY",
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
        "clean_baseline": not errors,
    }


def build_development_queue(validation: Dict[str, Any]) -> Dict[str, Any]:
    selector_obj = validation["loaded"]["next_action_selector"]
    selector = selector_obj.get("next_action_selector_after_post_framework_status", {})
    selected_action = selector.get("selected_action", {})
    selector_context = selector.get("context_summary", {})

    status_obj = validation["loaded"]["post_framework_status_refresh"]
    status = status_obj.get("post_framework_status_refresh", {})
    status_flags = status.get("status_flags", {})

    backlog_obj = validation["loaded"]["backlog_refresh"]
    backlog = backlog_obj.get("development_backlog_refresh_after_framework_readme_gate", {})
    backlog_context = backlog.get("context_summary", {})

    panel_obj = validation["loaded"]["governance_panel"]
    panel = panel_obj.get("governance_status_panel_after_framework_skeleton", {})
    hard_blocks = panel.get("hard_blocks", {})

    manifest_obj = validation["loaded"]["active_core_manifest"]
    manifest = manifest_obj.get("active_core_manifest_after_framework_skeleton", {})

    module_index_obj = validation["loaded"]["module_index"]
    module_index = module_index_obj.get("module_index_after_framework_skeleton", {})

    capability_obj = validation["loaded"]["capability_map"]
    capability = capability_obj.get("capability_map_after_framework_skeleton", {})

    hard_blocks_ok = bool(hard_blocks) and all(value is False for value in hard_blocks.values())

    prerequisites = {
        "parent_selector_ready": selector_obj.get("next_action_selector_after_post_framework_status_status") == "REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_POST_FRAMEWORK_STATUS_V1_READY",
        "parent_selected_this_queue_selector": selected_action.get("module") == "edge_factory_os_repo_only_development_queue_selector_after_post_framework_status_v1.py",
        "parent_selected_scope_repo_only": selected_action.get("scope") == "REPO_ONLY_OS_INTELLIGENCE",
        "post_framework_status_ready": status_obj.get("post_framework_status_refresh_status") == "REPO_ONLY_POST_FRAMEWORK_STATUS_REFRESH_V1_READY",
        "status_flags_all_true": bool(status_flags) and all(value is True for value in status_flags.values()),
        "backlog_ready": backlog_obj.get("development_backlog_refresh_after_framework_readme_gate_status") == "REPO_ONLY_DEVELOPMENT_BACKLOG_REFRESH_AFTER_FRAMEWORK_README_GATE_V1_READY",
        "readme_apply_blocked": backlog_context.get("readme_apply_blocked") is True and selector_context.get("readme_apply_blocked") is True,
        "manual_approval_present_false": backlog_context.get("manual_approval_present") is False and selector_context.get("manual_approval_present") is False,
        "manual_approval_valid_false": backlog_context.get("manual_approval_valid") is False and selector_context.get("manual_approval_valid") is False,
        "governance_panel_pass": panel.get("governance_pass") is True,
        "hard_blocks_all_false": hard_blocks_ok,
        "active_core_manifest_ready": manifest_obj.get("active_core_manifest_after_framework_skeleton_status") == "REPO_ONLY_ACTIVE_CORE_MANIFEST_REFRESH_AFTER_FRAMEWORK_SKELETON_V1_READY",
        "module_index_ready": module_index_obj.get("module_index_after_framework_skeleton_status") == "REPO_ONLY_MODULE_INDEX_REFRESH_AFTER_FRAMEWORK_SKELETON_V1_READY",
        "capability_map_ready": capability_obj.get("capability_map_after_framework_skeleton_status") == "REPO_ONLY_CAPABILITY_MAP_REFRESH_AFTER_FRAMEWORK_SKELETON_V1_READY",
        "tracked_python_clean": validation["tracked_python_validation"]["pass"] is True,
    }

    queue_items = [
        {
            "rank": 1,
            "key": "FRAMEWORK_SCHEMA_REGISTRY_CONTRACT",
            "module": SELECTED_NEXT_MODULE,
            "scope": "REPO_ONLY_SCHEMA_CONTRACT",
            "allowed": True,
            "reason": "Framework skeleton and post-framework status are clean; next safe repo-only step is a schema registry contract, not schema apply.",
            "allowed_outputs_only": [
                "lab_root_json",
                "lab_root_txt",
                "tool_source_commit",
            ],
            "blocked_actions": [
                "schema_file_creation",
                "schema_file_edit",
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
                "readme_apply",
                "readme_edit",
            ],
        },
        {
            "rank": 2,
            "key": "FRAMEWORK_README_CONTENT_APPLY",
            "module": "edge_factory_os_repo_only_framework_readme_content_apply_v1.py",
            "scope": "REPO_ONLY_DOCUMENTATION_APPLY",
            "allowed": False,
            "reason": "Blocked because manual README approval is absent/invalid.",
            "allowed_outputs_only": [],
            "blocked_actions": ["readme_apply", "readme_edit"],
        },
        {
            "rank": 3,
            "key": "STRATEGY_RESEARCH_RESUME",
            "module": None,
            "scope": "BLOCKED_REQUIRES_EXPLICIT_FUTURE_APPROVAL",
            "allowed": False,
            "reason": "Strategy research remains blocked until future explicit approval and prerequisite guard chain.",
            "allowed_outputs_only": [],
            "blocked_actions": [
                "strategy_research",
                "candidate_generation",
                "candidate_release",
                "family_release",
                "holdout_access",
                "runtime_touch",
                "capital_change",
            ],
        },
        {
            "rank": 4,
            "key": "RUNTIME_OR_CAPITAL_RESUME",
            "module": None,
            "scope": "BLOCKED",
            "allowed": False,
            "reason": "Runtime/capital/live actions remain blocked by governance.",
            "allowed_outputs_only": [],
            "blocked_actions": [
                "runtime_touch",
                "launcher_execution",
                "capital_change",
                "active_paper_change",
                "live_trading",
                "real_orders",
            ],
        },
    ]

    selected = queue_items[0] if all(prerequisites.values()) else None
    status_counts = dict(Counter(item["scope"] for item in queue_items))

    return {
        "development_queue_status": "DEVELOPMENT_QUEUE_AFTER_POST_FRAMEWORK_STATUS_ACTIVE" if selected else "DEVELOPMENT_QUEUE_AFTER_POST_FRAMEWORK_STATUS_BLOCKED",
        "queue_items": queue_items,
        "queue_item_count": len(queue_items),
        "scope_counts": status_counts,
        "selected_development_task": selected,
        "selected_next_module": selected["module"] if selected else None,
        "selected_next_action": "BUILD_REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_CONTRACT_V1" if selected else None,
        "selected_scope": selected["scope"] if selected else None,
        "prerequisites": prerequisites,
        "context_summary": {
            "active_core_record_count": manifest.get("record_count"),
            "module_index_record_count": module_index.get("record_count"),
            "capability_record_count": capability.get("record_count"),
            "capability_counts_are_multilabel": capability.get("capability_counts_are_multilabel"),
            "framework_readme_count": manifest.get("framework_readme_count"),
            "readme_apply_blocked": backlog_context.get("readme_apply_blocked"),
            "manual_approval_present": backlog_context.get("manual_approval_present"),
            "manual_approval_valid": backlog_context.get("manual_approval_valid"),
            "parent_selected_module": selected_action.get("module"),
        },
        "queue_policy": {
            "select_contract_before_schema_apply": True,
            "schema_registry_contract_only_next": True,
            "readme_apply_stays_blocked_without_explicit_manual_approval": True,
            "strategy_research_stays_blocked_without_future_explicit_approval": True,
            "no_runtime_or_capital_work": True,
            "no_file_move_delete_restructure": True,
        },
        "blocked_runtime_or_trading_actions": {
            "runtime_touch_allowed": False,
            "launcher_allowed": False,
            "capital_change_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
            "strategy_research_allowed": False,
            "candidate_generation_allowed": False,
            "candidate_release_allowed": False,
            "family_release_allowed": False,
            "holdout_access_allowed": False,
            "readme_apply_allowed": False,
            "readme_edit_allowed": False,
            "schema_apply_allowed": False,
        },
        "invariants": {
            "queue_prerequisites_all_true": all(prerequisites.values()),
            "selected_module_is_framework_schema_registry_contract": selected is not None and selected["module"] == SELECTED_NEXT_MODULE,
            "selected_scope_is_repo_only_schema_contract": selected is not None and selected["scope"] == "REPO_ONLY_SCHEMA_CONTRACT",
            "readme_apply_not_selected": selected is not None and selected["key"] != "FRAMEWORK_README_CONTENT_APPLY",
            "strategy_research_not_selected": selected is not None and selected["key"] != "STRATEGY_RESEARCH_RESUME",
            "runtime_or_capital_not_selected": selected is not None and selected["key"] != "RUNTIME_OR_CAPITAL_RESUME",
            "hard_blocks_remain_false": hard_blocks_ok is True,
            "no_runtime_strategy_or_capital_authorized": True,
            "no_file_creation_or_modification_performed_by_queue_selector": True,
        },
    }


def main() -> int:
    safety_errors = [key for key, value in SAFETY_FLAGS.items() if not isinstance(value, bool)]

    validation = validate_inputs()
    errors = list(validation["errors"])

    if safety_errors:
        errors.append(f"safety flags are not boolean: {safety_errors}")

    queue = build_development_queue(validation)

    for key, value in queue["invariants"].items():
        if value is not True:
            errors.append(f"invariant {key} not true: {value}")

    passed = not errors

    payload = {
        "module": MODULE_NAME,
        "development_queue_selector_after_post_framework_status_status": "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_POST_FRAMEWORK_STATUS_V1_READY" if passed else "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_POST_FRAMEWORK_STATUS_V1_BLOCKED",
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": "DEVELOPMENT_QUEUE_SELECTED_FRAMEWORK_SCHEMA_REGISTRY_CONTRACT" if passed else "KEEP_FREEZE_REVIEW_DEVELOPMENT_QUEUE_AFTER_POST_FRAMEWORK_STATUS_ERRORS",
        "next_action": "BUILD_REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_CONTRACT_V1" if passed else "REVIEW_DEVELOPMENT_QUEUE_AFTER_POST_FRAMEWORK_STATUS_ERRORS",
        "next_module": SELECTED_NEXT_MODULE if passed else None,
        "reason": "Selected repo-only framework schema registry contract; no schema apply, runtime, strategy, or capital action authorized." if passed else "Development queue selector after post-framework status validation failed.",
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
            "clean_baseline": validation["clean_baseline"],
        },
        "development_queue_selector_after_post_framework_status": queue,
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
        "schema_file_creation_performed_now": False,
        "schema_file_edit_performed_now": False,
        "framework_file_creation_performed_now": False,
        "framework_directory_creation_performed_now": False,
        "framework_readme_edit_performed_now": False,
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
    }

    latest_json = OUT_DIR / "repo_only_development_queue_selector_after_post_framework_status_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_development_queue_selector_after_post_framework_status_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "repo_only_development_queue_selector_after_post_framework_status_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY DEVELOPMENT QUEUE SELECTOR AFTER POST-FRAMEWORK STATUS v1",
        "=" * 100,
        f"development_queue_selector_after_post_framework_status_status: {payload['development_queue_selector_after_post_framework_status_status']}",
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
        "QUEUE SUMMARY",
        "-" * 100,
        json.dumps(
            {
                "selected_development_task": queue["selected_development_task"],
                "context_summary": queue["context_summary"],
                "prerequisites": queue["prerequisites"],
                "queue_policy": queue["queue_policy"],
                "invariants": queue["invariants"],
                "blocked_runtime_or_trading_actions": queue["blocked_runtime_or_trading_actions"],
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