from __future__ import annotations

import ast
import difflib
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_framework_schema_registry_preview_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_repo_only_framework_schema_registry_preview_v1"
PREVIEW_DIR = OUT_DIR / "preview_files"
DIFF_DIR = OUT_DIR / "diff_files"
OUT_DIR.mkdir(parents=True, exist_ok=True)
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
DIFF_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "d5bc4b1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_framework_schema_registry_preview_v1.py"

CONTRACT_JSON = LAB_ROOT / "edge_factory_os_repo_only_framework_schema_registry_contract_v1" / "repo_only_framework_schema_registry_contract_v1_latest.json"
CONTRACT_POST_JSON = LAB_ROOT / "edge_factory_os_repo_only_framework_schema_registry_contract_post_commit_check" / "repo_only_framework_schema_registry_contract_post_commit_check_latest.json"
QUEUE_JSON = LAB_ROOT / "edge_factory_os_repo_only_development_queue_selector_after_post_framework_status_v1" / "repo_only_development_queue_selector_after_post_framework_status_v1_latest.json"
PANEL_JSON = LAB_ROOT / "edge_factory_os_repo_only_governance_status_panel_after_framework_skeleton_v1" / "repo_only_governance_status_panel_after_framework_skeleton_v1_latest.json"

SELECTED_NEXT_MODULE = "edge_factory_os_repo_only_framework_schema_registry_approval_gate_v1.py"

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
    "repo_only_framework_schema_registry_preview": True,
    "preview_only": True,
    "schema_registry_contract_required": True,
    "approval_gate_required_next": True,

    "repo_only_governance_allowed": True,
    "repo_only_audit_allowed": True,
    "read_only_validation_allowed": True,

    "schema_registry_approval_gate_allowed_next": True,
    "schema_preview_outputs_created_outside_repo": True,

    "schema_file_creation_allowed_now": False,
    "schema_file_edit_allowed_now": False,
    "schema_apply_allowed_now": False,
    "schema_file_creation_performed_now": False,
    "schema_file_edit_performed_now": False,
    "schema_apply_performed_now": False,

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


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def is_inside_path(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


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
        "framework_schema_registry_contract_status",
        "audit_status",
        "development_queue_selector_after_post_framework_status_status",
        "governance_status_panel_after_framework_skeleton_status",
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
        errors.append(f"dirty tracked paths present before schema registry preview: {git_state['dirty_tracked_paths']}")

    if actual_untracked != expected_untracked:
        errors.append(f"unexpected untracked set before schema registry preview: expected={sorted(expected_untracked)} actual={sorted(actual_untracked)}")

    subject = commit_subject("HEAD")
    checks["head_commit_subject"] = subject
    if subject != "Add repo-only framework schema registry contract":
        errors.append(f"unexpected HEAD commit subject: {subject}")

    paths = commit_paths("HEAD")
    checks["head_commit_paths"] = paths
    if paths != ["tools/edge_factory_os_repo_only_framework_schema_registry_contract_v1.py"]:
        errors.append(f"unexpected HEAD commit paths: {paths}")

    inputs = {
        "framework_schema_registry_contract": (
            CONTRACT_JSON,
            "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_CONTRACT_V1_READY",
            "edge_factory_os_repo_only_framework_schema_registry_preview_v1.py",
        ),
        "framework_schema_registry_contract_post_check": (
            CONTRACT_POST_JSON,
            "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_CONTRACT_POST_COMMIT_CHECK_PASS",
            "edge_factory_os_repo_only_framework_schema_registry_preview_v1.py",
        ),
        "development_queue_selector": (
            QUEUE_JSON,
            "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_AFTER_POST_FRAMEWORK_STATUS_V1_READY",
            None,
        ),
        "governance_panel": (
            PANEL_JSON,
            "REPO_ONLY_GOVERNANCE_STATUS_PANEL_AFTER_FRAMEWORK_SKELETON_V1_READY",
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

    existing_schema_files = [rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists()]
    if existing_schema_files:
        errors.append(f"planned schema files unexpectedly exist before preview-only step: {existing_schema_files}")

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
        "existing_schema_files_before_preview": existing_schema_files,
        "clean_baseline": not errors,
    }


def schema_template(schema_key: str, title: str, required_fields: List[str]) -> Dict[str, Any]:
    properties: Dict[str, Any] = {}
    for field in required_fields:
        properties[field] = {"description": f"Required field: {field}"}

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://edge-factory-os.local/schemas/{schema_key}.schema.json",
        "title": title,
        "type": "object",
        "additionalProperties": True,
        "required": required_fields,
        "properties": properties,
    }


def build_schema_preview(row: Dict[str, Any]) -> Dict[str, Any]:
    schema_key = str(row["schema_key"])
    title = schema_key.replace("_", " ").title()
    required_fields = list(row.get("required_fields", []))
    schema = schema_template(schema_key, title, required_fields)
    schema_text = json.dumps(schema, indent=2, sort_keys=True) + "\n"

    planned_repo_path = str(row["planned_repo_path"])
    existing_path = REPO_ROOT / planned_repo_path

    diff_lines = list(
        difflib.unified_diff(
            [],
            schema_text.splitlines(),
            fromfile=f"a/{planned_repo_path}",
            tofile=f"b/{planned_repo_path}",
            lineterm="",
        )
    )
    diff_text = "\n".join(diff_lines) + "\n"

    preview_path = PREVIEW_DIR / f"{schema_key}.schema.json.preview"
    diff_path = DIFF_DIR / f"{schema_key}.schema.json.diff.txt"

    preview_path.write_text(schema_text, encoding="utf-8")
    diff_path.write_text(diff_text, encoding="utf-8")

    return {
        "schema_key": schema_key,
        "planned_repo_path": planned_repo_path,
        "preview_path": str(preview_path),
        "diff_path": str(diff_path),
        "preview_path_inside_repo": is_inside_path(preview_path, REPO_ROOT),
        "diff_path_inside_repo": is_inside_path(diff_path, REPO_ROOT),
        "existing_repo_file": existing_path.exists(),
        "required_field_count": len(required_fields),
        "preview_sha256": sha256_text(schema_text),
        "diff_sha256": sha256_text(diff_text),
        "schema_file_created_in_repo": False,
        "schema_file_edited_in_repo": False,
        "schema_apply_performed_in_repo": False,
    }


def build_preview(validation: Dict[str, Any]) -> Dict[str, Any]:
    contract_obj = validation["loaded"]["framework_schema_registry_contract"]
    contract = contract_obj.get("framework_schema_registry_contract", {})
    registry_plan = contract.get("schema_registry_plan", [])
    contract_policy = contract.get("contract_policy", {})

    panel_obj = validation["loaded"]["governance_panel"]
    panel = panel_obj.get("governance_status_panel_after_framework_skeleton", {})
    hard_blocks = panel.get("hard_blocks", {})

    hard_blocks_ok = bool(hard_blocks) and all(value is False for value in hard_blocks.values())

    preview_rows: List[Dict[str, Any]] = []
    if isinstance(registry_plan, list):
        for row in registry_plan:
            preview_rows.append(build_schema_preview(row))

    existing_repo_file_count = sum(1 for row in preview_rows if row["existing_repo_file"])
    repo_created_count = sum(1 for row in preview_rows if row["schema_file_created_in_repo"])
    repo_edited_count = sum(1 for row in preview_rows if row["schema_file_edited_in_repo"])
    repo_apply_count = sum(1 for row in preview_rows if row["schema_apply_performed_in_repo"])

    preview_dirs_outside_repo = (
        not is_inside_path(PREVIEW_DIR, REPO_ROOT)
        and not is_inside_path(DIFF_DIR, REPO_ROOT)
    )
    preview_files_outside_repo = all(not row["preview_path_inside_repo"] for row in preview_rows)
    diff_files_outside_repo = all(not row["diff_path_inside_repo"] for row in preview_rows)
    existing_schema_files_after_preview = [rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists()]

    prerequisites = {
        "contract_ready": contract_obj.get("framework_schema_registry_contract_status") == "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_CONTRACT_V1_READY",
        "contract_policy_contract_only": contract_policy.get("contract_only") is True,
        "contract_policy_preview_required_next": contract_policy.get("preview_required_next") is True,
        "contract_policy_schema_creation_disallowed": contract_policy.get("schema_file_creation_allowed_now") is False,
        "contract_policy_schema_edit_disallowed": contract_policy.get("schema_file_edit_allowed_now") is False,
        "contract_policy_schema_apply_disallowed": contract_policy.get("schema_apply_allowed_now") is False,
        "registry_plan_is_list": isinstance(registry_plan, list),
        "registry_plan_count_is_8": len(registry_plan) == 8 if isinstance(registry_plan, list) else False,
        "preview_row_count_is_8": len(preview_rows) == 8,
        "preview_dirs_outside_repo": preview_dirs_outside_repo,
        "preview_files_outside_repo": preview_files_outside_repo,
        "diff_files_outside_repo": diff_files_outside_repo,
        "no_existing_repo_schema_files": existing_repo_file_count == 0,
        "no_existing_planned_schema_files_after_preview": not existing_schema_files_after_preview,
        "no_repo_schema_creation_performed": repo_created_count == 0,
        "no_repo_schema_edit_performed": repo_edited_count == 0,
        "no_repo_schema_apply_performed": repo_apply_count == 0,
        "hard_blocks_all_false": hard_blocks_ok,
        "tracked_python_clean": validation["tracked_python_validation"]["pass"] is True,
    }

    return {
        "preview_status": "FRAMEWORK_SCHEMA_REGISTRY_PREVIEW_ACTIVE" if all(prerequisites.values()) else "FRAMEWORK_SCHEMA_REGISTRY_PREVIEW_BLOCKED",
        "preview_policy": {
            "preview_only": True,
            "preview_outputs_outside_repo": True,
            "approval_required_before_schema_apply": True,
            "apply_allowed_now": False,
            "schema_file_creation_allowed_now": False,
            "schema_file_edit_allowed_now": False,
            "schema_apply_allowed_now": False,
            "no_repo_file_modification_now_except_tool_source_commit": True,
        },
        "preview_rows": preview_rows,
        "previewed_schema_count": len(preview_rows),
        "existing_repo_schema_file_count": existing_repo_file_count,
        "existing_planned_schema_files_after_preview": existing_schema_files_after_preview,
        "repo_schema_creation_performed_count": repo_created_count,
        "repo_schema_edit_performed_count": repo_edited_count,
        "repo_schema_apply_performed_count": repo_apply_count,
        "preview_dir": str(PREVIEW_DIR),
        "diff_dir": str(DIFF_DIR),
        "preview_dirs_outside_repo": preview_dirs_outside_repo,
        "preview_files_outside_repo": preview_files_outside_repo,
        "diff_files_outside_repo": diff_files_outside_repo,
        "prerequisites": prerequisites,
        "recommended_next_step": {
            "step": "BUILD_REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_APPROVAL_GATE_V1",
            "module": SELECTED_NEXT_MODULE,
            "scope": "REPO_ONLY_SCHEMA_APPROVAL_GATE",
            "reason": "Preview is ready; approval gate must block apply unless explicit approval exists.",
        },
        "invariants": {
            "preview_prerequisites_all_true": all(prerequisites.values()),
            "preview_only_policy_true": True,
            "previewed_schema_count_is_8": len(preview_rows) == 8,
            "preview_outputs_created_outside_repo": PREVIEW_DIR.exists() and DIFF_DIR.exists() and preview_dirs_outside_repo and preview_files_outside_repo and diff_files_outside_repo,
            "no_existing_repo_schema_files": existing_repo_file_count == 0,
            "no_existing_planned_schema_files_after_preview": not existing_schema_files_after_preview,
            "no_repo_schema_creation_performed": repo_created_count == 0,
            "no_repo_schema_edit_performed": repo_edited_count == 0,
            "no_repo_schema_apply_performed": repo_apply_count == 0,
            "approval_required_before_schema_apply": True,
            "schema_file_creation_disallowed_now": True,
            "schema_file_edit_disallowed_now": True,
            "schema_apply_disallowed_now": True,
            "hard_blocks_remain_false": hard_blocks_ok is True,
            "no_runtime_strategy_or_capital_authorized": True,
            "no_repo_file_creation_or_modification_performed_by_preview": True,
        },
    }


def main() -> int:
    safety_errors = [key for key, value in SAFETY_FLAGS.items() if not isinstance(value, bool)]

    validation = validate_inputs()
    errors = list(validation["errors"])

    if safety_errors:
        errors.append(f"safety flags are not boolean: {safety_errors}")

    preview = build_preview(validation)

    for key, value in preview["invariants"].items():
        if value is not True:
            errors.append(f"invariant {key} not true: {value}")

    passed = not errors

    payload = {
        "module": MODULE_NAME,
        "framework_schema_registry_preview_status": "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_PREVIEW_V1_READY" if passed else "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_PREVIEW_V1_BLOCKED",
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_SCHEMA_PREVIEW",
        "final_decision": "FRAMEWORK_SCHEMA_REGISTRY_PREVIEW_READY_FOR_APPROVAL_GATE" if passed else "KEEP_FREEZE_REVIEW_FRAMEWORK_SCHEMA_REGISTRY_PREVIEW_ERRORS",
        "next_action": "BUILD_REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_APPROVAL_GATE_V1" if passed else "REVIEW_FRAMEWORK_SCHEMA_REGISTRY_PREVIEW_ERRORS",
        "next_module": SELECTED_NEXT_MODULE if passed else None,
        "reason": "Schema registry preview is ready; preview/diff outputs were written outside repo only." if passed else "Framework schema registry preview validation failed.",
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
            "existing_schema_files_before_preview": validation["existing_schema_files_before_preview"],
            "clean_baseline": validation["clean_baseline"],
        },
        "framework_schema_registry_preview": preview,
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
        "schema_apply_performed_now": False,
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

    latest_json = OUT_DIR / "repo_only_framework_schema_registry_preview_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_framework_schema_registry_preview_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "repo_only_framework_schema_registry_preview_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY FRAMEWORK SCHEMA REGISTRY PREVIEW v1",
        "=" * 100,
        f"framework_schema_registry_preview_status: {payload['framework_schema_registry_preview_status']}",
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
        "PREVIEW SUMMARY",
        "-" * 100,
        json.dumps(
            {
                "preview_policy": preview["preview_policy"],
                "previewed_schema_count": preview["previewed_schema_count"],
                "existing_repo_schema_file_count": preview["existing_repo_schema_file_count"],
                "existing_planned_schema_files_after_preview": preview["existing_planned_schema_files_after_preview"],
                "repo_schema_creation_performed_count": preview["repo_schema_creation_performed_count"],
                "repo_schema_edit_performed_count": preview["repo_schema_edit_performed_count"],
                "repo_schema_apply_performed_count": preview["repo_schema_apply_performed_count"],
                "preview_dir": preview["preview_dir"],
                "diff_dir": preview["diff_dir"],
                "preview_dirs_outside_repo": preview["preview_dirs_outside_repo"],
                "preview_files_outside_repo": preview["preview_files_outside_repo"],
                "diff_files_outside_repo": preview["diff_files_outside_repo"],
                "prerequisites": preview["prerequisites"],
                "invariants": preview["invariants"],
                "recommended_next_step": preview["recommended_next_step"],
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