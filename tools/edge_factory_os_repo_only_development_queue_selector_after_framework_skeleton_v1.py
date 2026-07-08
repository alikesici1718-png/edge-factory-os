from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_development_queue_selector_after_framework_skeleton_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_repo_only_development_queue_selector_after_framework_skeleton_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "b0f71ec"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_development_queue_selector_after_framework_skeleton_v1.py"

NEXT_ACTION_SELECTOR_JSON = LAB_ROOT / "edge_factory_os_repo_only_next_action_selector_after_framework_skeleton_v1" / "repo_only_next_action_selector_after_framework_skeleton_v1_latest.json"
NEXT_ACTION_SELECTOR_POST_JSON = LAB_ROOT / "edge_factory_os_repo_only_next_action_selector_after_framework_skeleton_post_commit_check" / "repo_only_next_action_selector_after_framework_skeleton_post_commit_check_latest.json"
PANEL_JSON = LAB_ROOT / "edge_factory_os_repo_only_governance_status_panel_after_framework_skeleton_v1" / "repo_only_governance_status_panel_after_framework_skeleton_v1_latest.json"
MANIFEST_JSON = LAB_ROOT / "edge_factory_os_repo_only_active_core_manifest_refresh_after_framework_skeleton_v1" / "repo_only_active_core_manifest_refresh_after_framework_skeleton_v1_latest.json"
CAPABILITY_JSON = LAB_ROOT / "edge_factory_os_repo_only_capability_map_refresh_after_framework_skeleton_v1" / "repo_only_capability_map_refresh_after_framework_skeleton_v1_latest.json"
MODULE_INDEX_JSON = LAB_ROOT / "edge_factory_os_repo_only_module_index_refresh_after_framework_skeleton_v1" / "repo_only_module_index_refresh_after_framework_skeleton_v1_latest.json"

SELECTED_NEXT_MODULE = "edge_factory_os_repo_only_framework_readme_content_contract_v1.py"

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_development_queue_selector_after_framework_skeleton": True,
    "read_only_development_queue_selection_only": True,
    "next_action_selector_after_framework_skeleton_required": True,
    "governance_status_panel_after_framework_skeleton_required": True,
    "framework_skeleton_complete_required": True,

    "repo_only_governance_allowed": True,
    "repo_only_audit_allowed": True,
    "read_only_validation_allowed": True,

    "framework_readme_content_contract_allowed_next": True,
    "framework_file_creation_allowed_now": False,
    "framework_directory_creation_allowed_now": False,
    "framework_file_creation_performed_now": False,
    "framework_directory_creation_performed_now": False,
    "framework_readme_edit_allowed_now": False,
    "framework_readme_edit_performed_now": False,

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
        "next_action_selector_after_framework_skeleton_status",
        "audit_status",
        "governance_status_panel_after_framework_skeleton_status",
        "active_core_manifest_after_framework_skeleton_status",
        "capability_map_after_framework_skeleton_status",
        "module_index_after_framework_skeleton_status",
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
    if subject != "Add repo-only next-action selector after framework skeleton":
        errors.append(f"unexpected HEAD commit subject: {subject}")

    paths = commit_paths("HEAD")
    checks["head_commit_paths"] = paths
    if paths != ["tools/edge_factory_os_repo_only_next_action_selector_after_framework_skeleton_v1.py"]:
        errors.append(f"unexpected HEAD commit paths: {paths}")

    inputs = {
        "next_action_selector_after_framework_skeleton": (
            NEXT_ACTION_SELECTOR_JSON,
            "REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_FRAMEWORK_SKELETON_V1_READY",
            "edge_factory_os_repo_only_development_queue_selector_after_framework_skeleton_v1.py",
        ),
        "next_action_selector_after_framework_skeleton_post_check": (
            NEXT_ACTION_SELECTOR_POST_JSON,
            "REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_FRAMEWORK_SKELETON_POST_COMMIT_CHECK_PASS",
            "edge_factory_os_repo_only_development_queue_selector_after_framework_skeleton_v1.py",
        ),
        "governance_status_panel_after_framework_skeleton": (
            PANEL_JSON,
            "REPO_ONLY_GOVERNANCE_STATUS_PANEL_AFTER_FRAMEWORK_SKELETON_V1_READY",
            None,
        ),
        "active_core_manifest_after_framework_skeleton": (
            MANIFEST_JSON,
            "REPO_ONLY_ACTIVE_CORE_MANIFEST_REFRESH_AFTER_FRAMEWORK_SKELETON_V1_READY",
            None,
        ),
        "capability_map_after_framework_skeleton": (
            CAPABILITY_JSON,
            "REPO_ONLY_CAPABILITY_MAP_REFRESH_AFTER_FRAMEWORK_SKELETON_V1_READY",
            None,
        ),
        "module_index_after_framework_skeleton": (
            MODULE_INDEX_JSON,
            "REPO_ONLY_MODULE_INDEX_REFRESH_AFTER_FRAMEWORK_SKELETON_V1_READY",
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
    selector_obj = validation["loaded"]["next_action_selector_after_framework_skeleton"]
    selector = selector_obj.get("next_action_selector_after_framework_skeleton", {})
    selected_from_parent = selector.get("selected_action", {})
    prerequisites = selector.get("prerequisites", {})
    invariants = selector.get("invariants", {})

    panel_obj = validation["loaded"]["governance_status_panel_after_framework_skeleton"]
    panel = panel_obj.get("governance_status_panel_after_framework_skeleton", {})
    hard_blocks = panel.get("hard_blocks", {})

    manifest_obj = validation["loaded"]["active_core_manifest_after_framework_skeleton"]
    manifest = manifest_obj.get("active_core_manifest_after_framework_skeleton", {})

    capability_obj = validation["loaded"]["capability_map_after_framework_skeleton"]
    capability = capability_obj.get("capability_map_after_framework_skeleton", {})

    module_index_obj = validation["loaded"]["module_index_after_framework_skeleton"]
    module_index = module_index_obj.get("module_index_after_framework_skeleton", {})

    hard_blocks_ok = bool(hard_blocks) and all(value is False for value in hard_blocks.values())

    candidate_queue = [
        {
            "rank": 1,
            "key": "FRAMEWORK_README_CONTENT_CONTRACT",
            "module": SELECTED_NEXT_MODULE,
            "scope": "REPO_ONLY_DOCUMENTATION_CONTRACT",
            "allowed": True,
            "reason": "Framework skeleton exists and is audited; next safest work is a contract-only README content plan, with no apply/edit yet.",
            "allowed_outputs_only": [
                "lab_root_json",
                "lab_root_txt",
                "tool_source_commit",
            ],
            "blocked_actions": [
                "edit_framework_readmes_now",
                "apply_content_now",
                "runtime_touch",
                "launcher_execution",
                "capital_change",
                "live_trading",
                "real_orders",
                "strategy_research",
                "candidate_generation",
                "candidate_release",
                "family_release",
                "holdout_access",
            ],
        },
        {
            "rank": 2,
            "key": "RISK_REVIEW_MANUAL_APPROVAL_RECORD_REFRESH",
            "module": "edge_factory_os_repo_only_risk_review_manual_approval_record_refresh_v1.py",
            "scope": "REPO_ONLY_GOVERNANCE",
            "allowed": False,
            "reason": "Useful later, but documentation contract is safer after framework skeleton creation.",
            "allowed_outputs_only": [],
            "blocked_actions": [],
        },
        {
            "rank": 3,
            "key": "BACKUP_HYGIENE_APPROVAL_REVIEW_CONTRACT",
            "module": "edge_factory_os_repo_only_backup_hygiene_approval_review_contract_v1.py",
            "scope": "REPO_ONLY_GOVERNANCE_CONTRACT",
            "allowed": False,
            "reason": "Only after explicit cleanup/hygiene approval boundaries are revisited; no delete/move allowed now.",
            "allowed_outputs_only": [],
            "blocked_actions": [],
        },
    ]

    selected = candidate_queue[0]

    prerequisites_summary = {
        "parent_selector_ready": selector_obj.get("next_action_selector_after_framework_skeleton_status") == "REPO_ONLY_NEXT_ACTION_SELECTOR_AFTER_FRAMEWORK_SKELETON_V1_READY",
        "parent_selected_development_queue_selector": selected_from_parent.get("module") == "edge_factory_os_repo_only_development_queue_selector_after_framework_skeleton_v1.py",
        "parent_prerequisites_all_true": bool(prerequisites) and all(value is True for value in prerequisites.values()),
        "parent_invariants_all_true": bool(invariants) and all(value is True for value in invariants.values()),
        "governance_panel_pass": panel.get("governance_pass") is True,
        "hard_blocks_all_false": hard_blocks_ok,
        "active_core_manifest_ready": manifest_obj.get("active_core_manifest_after_framework_skeleton_status") == "REPO_ONLY_ACTIVE_CORE_MANIFEST_REFRESH_AFTER_FRAMEWORK_SKELETON_V1_READY",
        "capability_map_ready": capability_obj.get("capability_map_after_framework_skeleton_status") == "REPO_ONLY_CAPABILITY_MAP_REFRESH_AFTER_FRAMEWORK_SKELETON_V1_READY",
        "module_index_ready": module_index_obj.get("module_index_after_framework_skeleton_status") == "REPO_ONLY_MODULE_INDEX_REFRESH_AFTER_FRAMEWORK_SKELETON_V1_READY",
        "framework_readme_count_is_8": manifest.get("framework_readme_count") == 8,
        "capability_map_multilabel": capability.get("capability_counts_are_multilabel") is True,
        "module_index_record_count_positive": isinstance(module_index.get("record_count"), int) and module_index.get("record_count") > 0,
    }

    return {
        "development_queue_status": "DEVELOPMENT_QUEUE_SELECTOR_AFTER_FRAMEWORK_SKELETON_ACTIVE" if all(prerequisites_summary.values()) else "DEVELOPMENT_QUEUE_SELECTOR_AFTER_FRAMEWORK_SKELETON_BLOCKED",
        "candidate_queue": candidate_queue,
        "selected_development_task": selected if all(prerequisites_summary.values()) else None,
        "selected_next_module": selected["module"] if all(prerequisites_summary.values()) else None,
        "selected_next_action": "BUILD_REPO_ONLY_FRAMEWORK_README_CONTENT_CONTRACT_V1" if all(prerequisites_summary.values()) else None,
        "selected_scope": selected["scope"] if all(prerequisites_summary.values()) else None,
        "prerequisites": prerequisites_summary,
        "queue_policy": {
            "prefer_contract_before_apply": True,
            "prefer_documentation_contract_after_skeleton_creation": True,
            "no_readme_edit_without_contract_preview_approval_apply_chain": True,
            "no_runtime_strategy_or_capital_work": True,
            "backup_delete_move_requires_explicit_future_approval": True,
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
        },
        "invariants": {
            "development_queue_prerequisites_all_true": all(prerequisites_summary.values()),
            "selected_module_is_framework_readme_content_contract": selected["module"] == SELECTED_NEXT_MODULE,
            "selected_scope_is_repo_only_documentation_contract": selected["scope"] == "REPO_ONLY_DOCUMENTATION_CONTRACT",
            "selected_task_is_contract_not_apply": "CONTRACT" in selected["key"] and "APPLY" not in selected["key"],
            "hard_blocks_remain_false": hard_blocks_ok is True,
            "no_framework_readme_edit_authorized_now": True,
            "no_runtime_strategy_or_capital_authorized": True,
            "no_file_creation_or_modification_performed_by_development_queue_selector": True,
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
        "development_queue_selector_after_framework_skeleton_status": "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_FRAMEWORK_SKELETON_V1_READY" if passed else "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_FRAMEWORK_SKELETON_V1_BLOCKED",
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": "DEVELOPMENT_QUEUE_SELECTED_FRAMEWORK_README_CONTENT_CONTRACT" if passed else "KEEP_FREEZE_REVIEW_DEVELOPMENT_QUEUE_SELECTOR_ERRORS",
        "next_action": "BUILD_REPO_ONLY_FRAMEWORK_README_CONTENT_CONTRACT_V1" if passed else "REVIEW_DEVELOPMENT_QUEUE_SELECTOR_ERRORS",
        "next_module": SELECTED_NEXT_MODULE if passed else None,
        "reason": "Selected contract-only framework README content planning as next safest repo-only development task." if passed else "Development queue selector validation failed.",
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
        "development_queue_selector_after_framework_skeleton": queue,
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
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

    latest_json = OUT_DIR / "repo_only_development_queue_selector_after_framework_skeleton_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_development_queue_selector_after_framework_skeleton_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "repo_only_development_queue_selector_after_framework_skeleton_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY DEVELOPMENT QUEUE SELECTOR AFTER FRAMEWORK SKELETON v1",
        "=" * 100,
        f"development_queue_selector_after_framework_skeleton_status: {payload['development_queue_selector_after_framework_skeleton_status']}",
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