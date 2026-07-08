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

MODULE_NAME = "edge_factory_os_repo_only_development_queue_selector_after_schema_registry_approval_record_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_repo_only_development_queue_selector_after_schema_registry_approval_record_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "eb1c6de"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_development_queue_selector_after_schema_registry_approval_record_v1.py"

RECORD_JSON = LAB_ROOT / "edge_factory_os_repo_only_framework_schema_registry_manual_approval_record_v1" / "repo_only_framework_schema_registry_manual_approval_record_v1_latest.json"
RECORD_POST_JSON = LAB_ROOT / "edge_factory_os_repo_only_framework_schema_registry_manual_approval_record_post_commit_check" / "repo_only_framework_schema_registry_manual_approval_record_post_commit_check_latest.json"
GATE_JSON = LAB_ROOT / "edge_factory_os_repo_only_framework_schema_registry_approval_gate_v1" / "repo_only_framework_schema_registry_approval_gate_v1_latest.json"
GATE_POST_JSON = LAB_ROOT / "edge_factory_os_repo_only_framework_schema_registry_approval_gate_post_commit_check" / "repo_only_framework_schema_registry_approval_gate_post_commit_check_latest.json"
PREVIEW_JSON = LAB_ROOT / "edge_factory_os_repo_only_framework_schema_registry_preview_v1" / "repo_only_framework_schema_registry_preview_v1_latest.json"
CONTRACT_JSON = LAB_ROOT / "edge_factory_os_repo_only_framework_schema_registry_contract_v1" / "repo_only_framework_schema_registry_contract_v1_latest.json"

SELECTED_NEXT_MODULE = "edge_factory_os_repo_only_post_schema_registry_status_refresh_v1.py"

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
    "repo_only_development_queue_selector_after_schema_registry_approval_record": True,
    "read_only_development_queue_selection_only": True,
    "manual_approval_record_required": True,
    "post_schema_registry_status_refresh_allowed_next": True,

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


def get_existing_planned_schema_files(paths: Optional[List[str]] = None) -> List[str]:
    checked_paths = paths if paths is not None else PLANNED_SCHEMA_REL_PATHS
    return sorted(str(rel) for rel in checked_paths if (REPO_ROOT / str(rel)).exists())


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
        "framework_schema_registry_manual_approval_record_status",
        "audit_status",
        "framework_schema_registry_approval_gate_status",
        "framework_schema_registry_preview_status",
        "framework_schema_registry_contract_status",
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
        errors.append(f"dirty tracked paths present before queue selector: {git_state['dirty_tracked_paths']}")

    if actual_untracked != expected_untracked:
        errors.append(f"unexpected untracked set before queue selector: expected={sorted(expected_untracked)} actual={sorted(actual_untracked)}")

    subject = commit_subject("HEAD")
    checks["head_commit_subject"] = subject
    if subject != "Add repo-only framework schema registry manual approval record":
        errors.append(f"unexpected HEAD commit subject: {subject}")

    paths = commit_paths("HEAD")
    checks["head_commit_paths"] = paths
    if paths != ["tools/edge_factory_os_repo_only_framework_schema_registry_manual_approval_record_v1.py"]:
        errors.append(f"unexpected HEAD commit paths: {paths}")

    existing_schema_files_before_queue = get_existing_planned_schema_files()
    if existing_schema_files_before_queue:
        errors.append(f"planned schema files unexpectedly exist before queue selector: {existing_schema_files_before_queue}")

    inputs = {
        "manual_approval_record": (
            RECORD_JSON,
            "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_MANUAL_APPROVAL_RECORD_V1_READY",
            "edge_factory_os_repo_only_development_queue_selector_after_schema_registry_approval_record_v1.py",
        ),
        "manual_approval_record_post_check": (
            RECORD_POST_JSON,
            "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_MANUAL_APPROVAL_RECORD_POST_COMMIT_CHECK_PASS",
            "edge_factory_os_repo_only_development_queue_selector_after_schema_registry_approval_record_v1.py",
        ),
        "approval_gate": (
            GATE_JSON,
            "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_APPROVAL_GATE_V1_READY",
            None,
        ),
        "approval_gate_post_check": (
            GATE_POST_JSON,
            "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_APPROVAL_GATE_POST_COMMIT_CHECK_PASS",
            None,
        ),
        "preview": (
            PREVIEW_JSON,
            "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_PREVIEW_V1_READY",
            None,
        ),
        "contract": (
            CONTRACT_JSON,
            "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_CONTRACT_V1_READY",
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
        "existing_schema_files_before_queue": existing_schema_files_before_queue,
        "clean_baseline": not errors,
    }


def planned_schema_paths_from_record(record_payload: Dict[str, Any]) -> List[str]:
    schema_guard = record_payload.get("schema_file_guard", {})
    paths = schema_guard.get("planned_schema_rel_paths", [])
    if isinstance(paths, list):
        return [str(x) for x in paths]
    return []


def build_development_queue(validation: Dict[str, Any]) -> Dict[str, Any]:
    record_obj = validation["loaded"]["manual_approval_record"]
    record_payload = record_obj.get("framework_schema_registry_manual_approval_record", {})
    manual_record = record_payload.get("manual_approval_record", {})
    record_policy = record_payload.get("record_policy", {})

    record_schema_paths = planned_schema_paths_from_record(record_payload)
    schema_paths = record_schema_paths if record_schema_paths else list(PLANNED_SCHEMA_REL_PATHS)
    existing_schema_files = get_existing_planned_schema_files(schema_paths)
    existing_schema_files_constant_guard = get_existing_planned_schema_files()

    gate_obj = validation["loaded"]["approval_gate"]
    gate = gate_obj.get("framework_schema_registry_approval_gate", {})
    gate_decision = gate.get("approval_decision", {})

    preview_obj = validation["loaded"]["preview"]
    preview = preview_obj.get("framework_schema_registry_preview", {})

    contract_obj = validation["loaded"]["contract"]
    contract = contract_obj.get("framework_schema_registry_contract", {})

    prerequisites = {
        "manual_record_ready": record_obj.get("framework_schema_registry_manual_approval_record_status") == "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_MANUAL_APPROVAL_RECORD_V1_READY",
        "manual_record_next_selected_this_module": record_obj.get("next_module") == "edge_factory_os_repo_only_development_queue_selector_after_schema_registry_approval_record_v1.py",
        "manual_approval_not_granted": manual_record.get("approval_status") == "SCHEMA_REGISTRY_MANUAL_APPROVAL_NOT_GRANTED",
        "manual_approval_present_false": manual_record.get("manual_approval_present") is False,
        "manual_approval_valid_false": manual_record.get("manual_approval_valid") is False,
        "approval_granted_false": manual_record.get("approval_granted_now") is False,
        "apply_allowed_false": manual_record.get("apply_allowed_now") is False,
        "schema_apply_allowed_false": manual_record.get("schema_apply_allowed_now") is False,
        "schema_file_creation_allowed_false": manual_record.get("schema_file_creation_allowed_now") is False,
        "schema_file_edit_allowed_false": manual_record.get("schema_file_edit_allowed_now") is False,
        "schema_file_creation_performed_false": manual_record.get("schema_file_creation_performed_now") is False,
        "schema_file_edit_performed_false": manual_record.get("schema_file_edit_performed_now") is False,
        "schema_apply_performed_false": manual_record.get("schema_apply_performed_now") is False,
        "record_policy_blocks_apply": record_policy.get("schema_apply_blocked_without_exact_manual_approval") is True,
        "approval_gate_ready": gate_obj.get("framework_schema_registry_approval_gate_status") == "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_APPROVAL_GATE_V1_READY",
        "approval_gate_blocks_apply": gate_decision.get("apply_allowed_now") is False,
        "approval_gate_blocks_schema_apply": gate_decision.get("schema_apply_allowed_now") is False,
        "preview_ready": preview_obj.get("framework_schema_registry_preview_status") == "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_PREVIEW_V1_READY",
        "previewed_schema_count_is_8": preview.get("previewed_schema_count") == 8,
        "contract_ready": contract_obj.get("framework_schema_registry_contract_status") == "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_CONTRACT_V1_READY",
        "record_schema_path_count_is_8": len(record_schema_paths) == 8,
        "planned_schema_path_count_is_8": len(schema_paths) == 8,
        "no_planned_schema_files_exist_before_queue": not validation["existing_schema_files_before_queue"],
        "no_planned_schema_files_exist": not existing_schema_files,
        "no_planned_schema_files_exist_constant_guard": not existing_schema_files_constant_guard,
        "tracked_python_clean": validation["tracked_python_validation"]["pass"] is True,
    }

    queue_items = [
        {
            "rank": 1,
            "key": "POST_SCHEMA_REGISTRY_STATUS_REFRESH",
            "module": SELECTED_NEXT_MODULE,
            "scope": "REPO_ONLY_OS_INTELLIGENCE",
            "allowed": True,
            "reason": "Schema registry apply remains blocked; refresh consolidated repo-only status after schema-registry governance chain.",
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
                "readme_apply",
                "readme_edit",
            ],
        },
        {
            "rank": 2,
            "key": "SCHEMA_REGISTRY_APPLY",
            "module": "edge_factory_os_repo_only_framework_schema_registry_apply_v1.py",
            "scope": "BLOCKED_REQUIRES_EXPLICIT_SCHEMA_APPROVAL",
            "allowed": False,
            "reason": "Blocked because exact manual approval is absent.",
            "blocked_actions": ["schema_file_creation", "schema_file_edit", "schema_apply"],
        },
        {
            "rank": 3,
            "key": "STRATEGY_RESEARCH_RESUME",
            "module": None,
            "scope": "BLOCKED_REQUIRES_FUTURE_EXPLICIT_APPROVAL",
            "allowed": False,
            "reason": "Strategy research remains blocked; this queue is repo-only governance/intelligence only.",
            "blocked_actions": ["strategy_research", "candidate_generation", "candidate_release", "family_release", "holdout_access"],
        },
        {
            "rank": 4,
            "key": "RUNTIME_OR_CAPITAL_RESUME",
            "module": None,
            "scope": "BLOCKED",
            "allowed": False,
            "reason": "Runtime/capital/live actions remain blocked.",
            "blocked_actions": ["runtime_touch", "launcher_execution", "capital_change", "active_paper_change", "live_trading", "real_orders"],
        },
    ]

    selected = queue_items[0] if all(prerequisites.values()) else None
    scope_counts = dict(Counter(item["scope"] for item in queue_items))

    return {
        "development_queue_status": "DEVELOPMENT_QUEUE_AFTER_SCHEMA_REGISTRY_APPROVAL_RECORD_ACTIVE" if selected else "DEVELOPMENT_QUEUE_AFTER_SCHEMA_REGISTRY_APPROVAL_RECORD_BLOCKED",
        "queue_items": queue_items,
        "queue_item_count": len(queue_items),
        "scope_counts": scope_counts,
        "selected_development_task": selected,
        "selected_next_module": selected["module"] if selected else None,
        "selected_next_action": "BUILD_REPO_ONLY_POST_SCHEMA_REGISTRY_STATUS_REFRESH_V1" if selected else None,
        "selected_scope": selected["scope"] if selected else None,
        "prerequisites": prerequisites,
        "context_summary": {
            "manual_approval_status": manual_record.get("approval_status"),
            "manual_approval_present": manual_record.get("manual_approval_present"),
            "manual_approval_valid": manual_record.get("manual_approval_valid"),
            "schema_apply_allowed_now": manual_record.get("schema_apply_allowed_now"),
            "previewed_schema_count": preview.get("previewed_schema_count"),
            "record_schema_path_count": len(record_schema_paths),
            "planned_schema_path_count": len(schema_paths),
            "existing_planned_schema_files_before_queue": validation["existing_schema_files_before_queue"],
            "existing_planned_schema_files": existing_schema_files,
            "existing_planned_schema_files_constant_guard": existing_schema_files_constant_guard,
            "planned_schema_file_existing_count": len(existing_schema_files),
            "parent_next_module": record_obj.get("next_module"),
        },
        "queue_policy": {
            "schema_apply_stays_blocked_without_exact_manual_approval": True,
            "post_schema_registry_status_refresh_selected": True,
            "no_schema_file_creation_or_edit": True,
            "no_runtime_or_capital_work": True,
            "no_strategy_research": True,
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
            "schema_file_creation_allowed": False,
            "schema_file_edit_allowed": False,
        },
        "invariants": {
            "queue_prerequisites_all_true": all(prerequisites.values()),
            "selected_module_is_post_schema_registry_status_refresh": selected is not None and selected["module"] == SELECTED_NEXT_MODULE,
            "selected_scope_is_repo_only_os_intelligence": selected is not None and selected["scope"] == "REPO_ONLY_OS_INTELLIGENCE",
            "schema_apply_not_selected": selected is not None and selected["key"] != "SCHEMA_REGISTRY_APPLY",
            "strategy_research_not_selected": selected is not None and selected["key"] != "STRATEGY_RESEARCH_RESUME",
            "runtime_or_capital_not_selected": selected is not None and selected["key"] != "RUNTIME_OR_CAPITAL_RESUME",
            "schema_apply_remains_blocked": manual_record.get("schema_apply_allowed_now") is False,
            "no_planned_schema_files_exist_before_queue": not validation["existing_schema_files_before_queue"],
            "no_planned_schema_files_exist": not existing_schema_files,
            "no_planned_schema_files_exist_constant_guard": not existing_schema_files_constant_guard,
            "no_runtime_strategy_or_capital_authorized": True,
            "no_repo_file_creation_or_modification_performed_by_queue_selector": True,
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
        "development_queue_selector_after_schema_registry_approval_record_status": "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_SCHEMA_REGISTRY_APPROVAL_RECORD_V1_READY" if passed else "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_SCHEMA_REGISTRY_APPROVAL_RECORD_V1_BLOCKED",
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": "DEVELOPMENT_QUEUE_SELECTED_POST_SCHEMA_REGISTRY_STATUS_REFRESH" if passed else "KEEP_FREEZE_REVIEW_DEVELOPMENT_QUEUE_AFTER_SCHEMA_REGISTRY_APPROVAL_RECORD_ERRORS",
        "next_action": "BUILD_REPO_ONLY_POST_SCHEMA_REGISTRY_STATUS_REFRESH_V1" if passed else "REVIEW_DEVELOPMENT_QUEUE_AFTER_SCHEMA_REGISTRY_APPROVAL_RECORD_ERRORS",
        "next_module": SELECTED_NEXT_MODULE if passed else None,
        "reason": "Selected repo-only post-schema-registry status refresh; schema apply/create/edit remain blocked." if passed else "Development queue selector after schema registry approval record validation failed.",
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
            "existing_schema_files_before_queue": validation["existing_schema_files_before_queue"],
            "clean_baseline": validation["clean_baseline"],
        },
        "development_queue_selector_after_schema_registry_approval_record": queue,
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
    }

    latest_json = OUT_DIR / "repo_only_development_queue_selector_after_schema_registry_approval_record_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_development_queue_selector_after_schema_registry_approval_record_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "repo_only_development_queue_selector_after_schema_registry_approval_record_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY DEVELOPMENT QUEUE SELECTOR AFTER SCHEMA REGISTRY APPROVAL RECORD v1",
        "=" * 100,
        f"development_queue_selector_after_schema_registry_approval_record_status: {payload['development_queue_selector_after_schema_registry_approval_record_status']}",
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