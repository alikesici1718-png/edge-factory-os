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

MODULE_NAME = "edge_factory_os_repo_only_framework_schema_registry_approval_gate_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_repo_only_framework_schema_registry_approval_gate_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "fb953d7"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_framework_schema_registry_approval_gate_v1.py"

PREVIEW_JSON = LAB_ROOT / "edge_factory_os_repo_only_framework_schema_registry_preview_v1" / "repo_only_framework_schema_registry_preview_v1_latest.json"
PREVIEW_POST_JSON = LAB_ROOT / "edge_factory_os_repo_only_framework_schema_registry_preview_post_commit_check" / "repo_only_framework_schema_registry_preview_post_commit_check_latest.json"
CONTRACT_JSON = LAB_ROOT / "edge_factory_os_repo_only_framework_schema_registry_contract_v1" / "repo_only_framework_schema_registry_contract_v1_latest.json"
CONTRACT_POST_JSON = LAB_ROOT / "edge_factory_os_repo_only_framework_schema_registry_contract_post_commit_check" / "repo_only_framework_schema_registry_contract_post_commit_check_latest.json"
PANEL_JSON = LAB_ROOT / "edge_factory_os_repo_only_governance_status_panel_after_framework_skeleton_v1" / "repo_only_governance_status_panel_after_framework_skeleton_v1_latest.json"

SELECTED_NEXT_MODULE = "edge_factory_os_repo_only_framework_schema_registry_manual_approval_record_v1.py"

EXPECTED_APPROVAL_TEXT = "schema registry apply onaylıyorum"

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
    "repo_only_framework_schema_registry_approval_gate": True,
    "approval_gate_only": True,
    "schema_registry_preview_required": True,
    "manual_approval_record_required_next": True,

    "repo_only_governance_allowed": True,
    "repo_only_audit_allowed": True,
    "read_only_validation_allowed": True,

    "manual_approval_record_allowed_next": True,

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


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {args} returncode={result.returncode} stderr={result.stderr}")
    return result


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def get_existing_planned_schema_files() -> List[str]:
    return [rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists()]


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
        "framework_schema_registry_preview_status",
        "audit_status",
        "framework_schema_registry_contract_status",
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
        errors.append(f"dirty tracked paths present before schema registry approval gate: {git_state['dirty_tracked_paths']}")

    if actual_untracked != expected_untracked:
        errors.append(f"unexpected untracked set before schema registry approval gate: expected={sorted(expected_untracked)} actual={sorted(actual_untracked)}")

    subject = commit_subject("HEAD")
    checks["head_commit_subject"] = subject
    if subject != "Add repo-only framework schema registry preview":
        errors.append(f"unexpected HEAD commit subject: {subject}")

    paths = commit_paths("HEAD")
    checks["head_commit_paths"] = paths
    if paths != ["tools/edge_factory_os_repo_only_framework_schema_registry_preview_v1.py"]:
        errors.append(f"unexpected HEAD commit paths: {paths}")

    existing_schema_files_before_gate = get_existing_planned_schema_files()
    if existing_schema_files_before_gate:
        errors.append(f"planned schema files unexpectedly exist before approval gate: {existing_schema_files_before_gate}")

    inputs = {
        "framework_schema_registry_preview": (
            PREVIEW_JSON,
            "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_PREVIEW_V1_READY",
            "edge_factory_os_repo_only_framework_schema_registry_approval_gate_v1.py",
        ),
        "framework_schema_registry_preview_post_check": (
            PREVIEW_POST_JSON,
            "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_PREVIEW_POST_COMMIT_CHECK_PASS",
            "edge_factory_os_repo_only_framework_schema_registry_approval_gate_v1.py",
        ),
        "framework_schema_registry_contract": (
            CONTRACT_JSON,
            "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_CONTRACT_V1_READY",
            None,
        ),
        "framework_schema_registry_contract_post_check": (
            CONTRACT_POST_JSON,
            "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_CONTRACT_POST_COMMIT_CHECK_PASS",
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
        "existing_schema_files_before_gate": existing_schema_files_before_gate,
        "clean_baseline": not errors,
    }


def build_approval_gate(validation: Dict[str, Any]) -> Dict[str, Any]:
    preview_obj = validation["loaded"]["framework_schema_registry_preview"]
    preview = preview_obj.get("framework_schema_registry_preview", {})
    preview_policy = preview.get("preview_policy", {})
    preview_rows = preview.get("preview_rows", [])

    contract_obj = validation["loaded"]["framework_schema_registry_contract"]
    contract = contract_obj.get("framework_schema_registry_contract", {})

    panel_obj = validation["loaded"]["governance_panel"]
    panel = panel_obj.get("governance_status_panel_after_framework_skeleton", {})
    hard_blocks = panel.get("hard_blocks", {})

    hard_blocks_ok = bool(hard_blocks) and all(value is False for value in hard_blocks.values())

    manual_approval_text = ""
    manual_approval_present = False
    manual_approval_valid = False
    approval_granted_now = False

    existing_schema_files_after_gate = get_existing_planned_schema_files()
    previewed_schema_count = len(preview_rows) if isinstance(preview_rows, list) else 0

    approval_decision = {
        "approval_gate_final_decision": "MANUAL_APPROVAL_ABSENT_OR_INVALID_SCHEMA_APPLY_BLOCKED",
        "manual_approval_present": manual_approval_present,
        "manual_approval_valid": manual_approval_valid,
        "manual_approval_text": manual_approval_text,
        "required_future_approval_text": EXPECTED_APPROVAL_TEXT,
        "approval_granted_now": approval_granted_now,
        "apply_allowed_now": False,
        "schema_file_creation_allowed_now": False,
        "schema_file_edit_allowed_now": False,
        "schema_apply_allowed_now": False,
        "approved_schema_count": 0,
        "previewed_schema_count": previewed_schema_count,
        "reason": "No explicit schema registry apply approval was provided; schema apply remains blocked.",
    }

    prerequisites = {
        "preview_ready": preview_obj.get("framework_schema_registry_preview_status") == "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_PREVIEW_V1_READY",
        "preview_policy_preview_only": preview_policy.get("preview_only") is True,
        "preview_policy_outputs_outside_repo": preview_policy.get("preview_outputs_outside_repo") is True,
        "preview_policy_schema_creation_disallowed": preview_policy.get("schema_file_creation_allowed_now") is False,
        "preview_policy_schema_edit_disallowed": preview_policy.get("schema_file_edit_allowed_now") is False,
        "preview_policy_schema_apply_disallowed": preview_policy.get("schema_apply_allowed_now") is False,
        "previewed_schema_count_is_8": previewed_schema_count == 8,
        "existing_repo_schema_file_count_zero": preview.get("existing_repo_schema_file_count") == 0,
        "repo_schema_creation_performed_zero": preview.get("repo_schema_creation_performed_count") == 0,
        "repo_schema_edit_performed_zero": preview.get("repo_schema_edit_performed_count") == 0,
        "repo_schema_apply_performed_zero": preview.get("repo_schema_apply_performed_count") == 0,
        "no_existing_planned_schema_files_before_gate": not validation["existing_schema_files_before_gate"],
        "no_existing_planned_schema_files_after_gate": not existing_schema_files_after_gate,
        "contract_ready": contract_obj.get("framework_schema_registry_contract_status") == "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_CONTRACT_V1_READY",
        "contract_policy_requires_approval_before_schema_apply": contract.get("contract_policy", {}).get("approval_required_before_schema_apply") is True,
        "manual_approval_absent": manual_approval_present is False,
        "manual_approval_invalid": manual_approval_valid is False,
        "approval_granted_false": approval_granted_now is False,
        "hard_blocks_all_false": hard_blocks_ok,
        "tracked_python_clean": validation["tracked_python_validation"]["pass"] is True,
    }

    return {
        "approval_gate_status": "FRAMEWORK_SCHEMA_REGISTRY_APPROVAL_GATE_ACTIVE" if all(prerequisites.values()) else "FRAMEWORK_SCHEMA_REGISTRY_APPROVAL_GATE_BLOCKED",
        "approval_decision": approval_decision,
        "approval_policy": {
            "explicit_manual_approval_required_before_schema_apply": True,
            "exact_required_approval_text": EXPECTED_APPROVAL_TEXT,
            "schema_apply_blocked_without_approval": True,
            "schema_file_creation_blocked_without_approval": True,
            "schema_file_edit_blocked_without_approval": True,
            "manual_approval_record_required_next": True,
            "no_runtime_strategy_or_capital_work": True,
        },
        "prerequisites": prerequisites,
        "preview_summary": {
            "previewed_schema_count": previewed_schema_count,
            "preview_dir": preview.get("preview_dir"),
            "diff_dir": preview.get("diff_dir"),
            "existing_repo_schema_file_count": preview.get("existing_repo_schema_file_count"),
            "existing_planned_schema_files_before_gate": validation["existing_schema_files_before_gate"],
            "existing_planned_schema_files_after_gate": existing_schema_files_after_gate,
            "repo_schema_creation_performed_count": preview.get("repo_schema_creation_performed_count"),
            "repo_schema_edit_performed_count": preview.get("repo_schema_edit_performed_count"),
            "repo_schema_apply_performed_count": preview.get("repo_schema_apply_performed_count"),
        },
        "recommended_next_step": {
            "step": "BUILD_REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_MANUAL_APPROVAL_RECORD_V1",
            "module": SELECTED_NEXT_MODULE,
            "scope": "REPO_ONLY_SCHEMA_APPROVAL_RECORD",
            "reason": "Approval gate is ready but approval is absent; record absence and keep apply blocked.",
        },
        "invariants": {
            "approval_gate_prerequisites_all_true": all(prerequisites.values()),
            "manual_approval_present_false": manual_approval_present is False,
            "manual_approval_valid_false": manual_approval_valid is False,
            "approval_granted_false": approval_granted_now is False,
            "apply_allowed_false": approval_decision["apply_allowed_now"] is False,
            "schema_file_creation_allowed_false": approval_decision["schema_file_creation_allowed_now"] is False,
            "schema_file_edit_allowed_false": approval_decision["schema_file_edit_allowed_now"] is False,
            "schema_apply_allowed_false": approval_decision["schema_apply_allowed_now"] is False,
            "no_existing_planned_schema_files_before_gate": not validation["existing_schema_files_before_gate"],
            "no_existing_planned_schema_files_after_gate": not existing_schema_files_after_gate,
            "manual_approval_record_required_next": True,
            "hard_blocks_remain_false": hard_blocks_ok is True,
            "no_runtime_strategy_or_capital_authorized": True,
            "no_repo_file_creation_or_modification_performed_by_approval_gate": True,
        },
    }


def main() -> int:
    safety_errors = [key for key, value in SAFETY_FLAGS.items() if not isinstance(value, bool)]

    validation = validate_inputs()
    errors = list(validation["errors"])

    if safety_errors:
        errors.append(f"safety flags are not boolean: {safety_errors}")

    gate = build_approval_gate(validation)

    for key, value in gate["invariants"].items():
        if value is not True:
            errors.append(f"invariant {key} not true: {value}")

    passed = not errors

    payload = {
        "module": MODULE_NAME,
        "framework_schema_registry_approval_gate_status": "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_APPROVAL_GATE_V1_READY" if passed else "REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_APPROVAL_GATE_V1_BLOCKED",
        "severity": "ATTENTION" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_SCHEMA_APPROVAL_GATE",
        "final_decision": "FRAMEWORK_SCHEMA_REGISTRY_APPROVAL_GATE_READY_MANUAL_APPROVAL_REQUIRED_NO_APPLY" if passed else "KEEP_FREEZE_REVIEW_FRAMEWORK_SCHEMA_REGISTRY_APPROVAL_GATE_ERRORS",
        "next_action": "BUILD_REPO_ONLY_FRAMEWORK_SCHEMA_REGISTRY_MANUAL_APPROVAL_RECORD_V1" if passed else "REVIEW_FRAMEWORK_SCHEMA_REGISTRY_APPROVAL_GATE_ERRORS",
        "next_module": SELECTED_NEXT_MODULE if passed else None,
        "reason": "Schema registry approval gate is ready; manual approval is absent, so schema apply remains blocked." if passed else "Framework schema registry approval gate validation failed.",
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
            "existing_schema_files_before_gate": validation["existing_schema_files_before_gate"],
            "clean_baseline": validation["clean_baseline"],
        },
        "framework_schema_registry_approval_gate": gate,
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

    latest_json = OUT_DIR / "repo_only_framework_schema_registry_approval_gate_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_framework_schema_registry_approval_gate_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "repo_only_framework_schema_registry_approval_gate_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY FRAMEWORK SCHEMA REGISTRY APPROVAL GATE v1",
        "=" * 100,
        f"framework_schema_registry_approval_gate_status: {payload['framework_schema_registry_approval_gate_status']}",
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
        "APPROVAL GATE SUMMARY",
        "-" * 100,
        json.dumps(
            {
                "approval_decision": gate["approval_decision"],
                "approval_policy": gate["approval_policy"],
                "preview_summary": gate["preview_summary"],
                "prerequisites": gate["prerequisites"],
                "invariants": gate["invariants"],
                "recommended_next_step": gate["recommended_next_step"],
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