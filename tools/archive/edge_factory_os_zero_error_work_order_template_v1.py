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

MODULE_NAME = "edge_factory_os_zero_error_work_order_template_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_zero_error_work_order_template_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "0338ef8"
CURRENT_TOOL_REL = "tools/edge_factory_os_zero_error_work_order_template_v1.py"

GOVERNOR_JSON = LAB_ROOT / "edge_factory_os_post_resume_zero_error_governor_panel_v1" / "post_resume_zero_error_governor_panel_v1_latest.json"
GOVERNOR_POST_CHECK_JSON = LAB_ROOT / "edge_factory_os_post_resume_zero_error_governor_panel_post_commit_check" / "post_resume_zero_error_governor_panel_post_commit_check_latest.json"
SELECTOR_JSON = LAB_ROOT / "edge_factory_os_repo_only_development_queue_selector_v1" / "repo_only_development_queue_selector_v1_latest.json"
ZERO_ERROR_PROTOCOL_JSON = LAB_ROOT / "edge_factory_os_zero_error_resume_protocol_v1" / "zero_error_resume_protocol_v1_latest.json"

SAFETY_FLAGS: Dict[str, bool] = {
    "zero_error_work_order_template": True,
    "read_only_template_only": True,
    "governor_panel_required": True,
    "zero_error_protocol_required": True,

    "repo_only_governance_allowed": True,
    "repo_only_audit_allowed": True,
    "repo_only_status_refresh_allowed": True,
    "repo_only_contract_preview_allowed": True,
    "read_only_validation_allowed": True,

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

FORBIDDEN_ACTIONS: List[str] = [
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
    "old_short_guarded_apply_execution",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def get_git_state() -> Dict[str, Any]:
    status_lines = [x for x in run_cmd(["git", "status", "--porcelain=v1"]).stdout.splitlines() if x.strip()]
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
        "remote_status_short": run_cmd(["git", "status", "-sb"]).stdout.splitlines(),
    }


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def tracked_python_files() -> List[str]:
    return sorted(x.strip() for x in run_cmd(["git", "ls-files", "*.py"]).stdout.splitlines() if x.strip())


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


def first_status(obj: Dict[str, Any]) -> Optional[str]:
    for key in [
        "governor_status",
        "audit_status",
        "selector_status",
        "resume_protocol_status",
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


def validate_status_record(
    errors: List[str],
    key: str,
    record: Dict[str, Any],
    expected_status: str,
    expected_next_module: Optional[str] = None,
) -> None:
    if record["status"] != expected_status:
        errors.append(f"{key} status mismatch: expected={expected_status} actual={record['status']}")

    validate_count_zero(errors, key, record, "critical_issue_count")
    validate_count_zero(errors, key, record, "warning_count")

    if expected_next_module is not None and record.get("next_module") != expected_next_module:
        errors.append(
            f"{key} next_module mismatch: expected={expected_next_module} actual={record.get('next_module')}"
        )


def validate_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    checks: Dict[str, Any] = {}
    source_statuses: Dict[str, Dict[str, Any]] = {}
    git_state = get_git_state()

    if not git_state["head"].startswith(EXPECTED_HEAD_PREFIX):
        errors.append(f"unexpected HEAD: {git_state['head']} expected {EXPECTED_HEAD_PREFIX}")

    expected_untracked = {CURRENT_TOOL_REL}
    actual_untracked = set(git_state["untracked_paths"])
    current_step_untracked_ok = actual_untracked == expected_untracked

    if git_state["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked paths present: {git_state['dirty_tracked_paths']}")

    if not current_step_untracked_ok:
        errors.append(
            "unexpected untracked set: "
            f"expected={sorted(expected_untracked)} actual={sorted(actual_untracked)}"
        )

    head_subject = commit_subject("HEAD")
    checks["head_commit_subject"] = head_subject
    if head_subject != "Add post-resume zero-error governor panel":
        errors.append(f"unexpected HEAD commit subject: {head_subject}")

    inputs = {
        "governor": (GOVERNOR_JSON, "POST_RESUME_ZERO_ERROR_GOVERNOR_PANEL_V1_READY", "edge_factory_os_zero_error_work_order_template_v1.py"),
        "governor_post_check": (GOVERNOR_POST_CHECK_JSON, "POST_RESUME_ZERO_ERROR_GOVERNOR_PANEL_POST_COMMIT_CHECK_PASS", "edge_factory_os_zero_error_work_order_template_v1.py"),
        # selector is historical provenance; do not require its historical next_module to equal current next step.
        "selector": (SELECTOR_JSON, "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_V1_READY", None),
        "zero_error_protocol": (ZERO_ERROR_PROTOCOL_JSON, "ZERO_ERROR_RESUME_PROTOCOL_V1_READY", None),
    }

    for key, spec in inputs.items():
        path, expected_status, expected_next_module = spec
        try:
            obj = load_json(path)
            record = source_record(path, obj)
            source_statuses[key] = record
            checks[key] = record
            validate_status_record(errors, key, record, expected_status, expected_next_module)
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

    clean_baseline = (
        not errors
        and current_step_untracked_ok
        and git_state["dirty_tracked_count"] == 0
        and py["syntax_error_count"] == 0
        and py["bom_error_count"] == 0
    )

    return {
        "pass": not errors,
        "errors": errors,
        "checks": checks,
        "git_state": git_state,
        "tracked_python_validation": py,
        "source_statuses": source_statuses,
        "current_step_untracked_ok": current_step_untracked_ok,
        "expected_untracked_during_run": sorted(expected_untracked),
        "actual_untracked_during_run": sorted(actual_untracked),
        "clean_baseline": clean_baseline,
    }


def build_work_order_template(
    clean_baseline: bool,
    source_statuses: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    required_fields = [
        "work_order_id",
        "purpose",
        "input_jsons",
        "mutates_repo_tracked_files",
        "mutates_runtime",
        "expected_single_untracked_path",
        "exact_commit_paths",
        "allowed_scope",
        "forbidden_actions",
        "fail_closed_conditions",
        "safety_flags",
        "pre_apply_checks",
        "post_commit_external_audit_checks",
        "rollback_or_freeze_rule",
    ]

    return {
        "template_status": "ZERO_ERROR_WORK_ORDER_TEMPLATE_ACTIVE" if clean_baseline else "ZERO_ERROR_WORK_ORDER_TEMPLATE_BLOCKED",
        "template_scope": "REPO_ONLY_GOVERNANCE_TEMPLATE",
        "source_statuses": source_statuses,
        "required_fields": required_fields,
        "field_rules": {
            "work_order_id": "must be stable, unique, and match target module/action",
            "purpose": "must state exactly what the change does and does not do",
            "input_jsons": "must list every JSON consumed by both PowerShell precheck and Python validation",
            "mutates_repo_tracked_files": "false for preview/preflight; exact-path list for approved apply/commit",
            "mutates_runtime": "must be false unless separate runtime approval exists",
            "expected_single_untracked_path": "must equal the one tool path created in current step",
            "exact_commit_paths": "must contain only approved path(s), never broad add",
            "allowed_scope": "must be one of repo-only governance/audit/status/template/read-only validation unless separately approved",
            "forbidden_actions": "must include runtime/launcher/capital/live/holdout/strategy/candidate/family/fix-all/mass-patch/git-add-force",
            "fail_closed_conditions": "must include dirty git, unexpected untracked, missing input JSON, issue_count>0, syntax/BOM errors",
            "safety_flags": "all values must be booleans; dangerous permissions false",
            "pre_apply_checks": "must verify HEAD, git status, input statuses, warning/critical zero",
            "post_commit_external_audit_checks": "must verify commit subject/path, git clean, syntax/BOM clean, output status READY/PASS",
            "rollback_or_freeze_rule": "on any failure, do not continue; keep freeze/review errors",
        },
        "default_forbidden_actions": FORBIDDEN_ACTIONS,
        "default_mandatory_chain": [
            "read_only_preflight",
            "targeted_preview_no_apply",
            "approval_record",
            "exact_path_apply_only_if_approved",
            "read_only_audit_refresh",
            "exact_path_commit_no_force_add",
            "post_commit_external_audit",
        ],
        "default_freeze_triggers": [
            "dirty_tracked_file_before_start",
            "unexpected_untracked_file",
            "syntax_or_bom_error",
            "critical_issue_count_above_zero",
            "warning_count_above_zero",
            "dangerous_safety_flag_true",
            "runtime_launcher_capital_live_holdout_attempt",
            "fix_all_or_mass_patch_request",
        ],
        "recommended_next_step": {
            "step": "BUILD_REPO_ONLY_DEVELOPMENT_BACKLOG_REFRESH",
            "module": "edge_factory_os_repo_only_development_backlog_refresh_v1.py",
            "scope": "REPO_ONLY_GOVERNANCE_PLANNING",
            "reason": "With the work-order template installed, refresh a repo-only backlog using the template constraints.",
        },
    }


def main() -> int:
    safety_errors = [
        key for key, value in SAFETY_FLAGS.items()
        if not isinstance(value, bool)
    ]

    validation = validate_inputs()
    errors = list(validation["errors"])

    if safety_errors:
        errors.append(f"safety flags are not boolean: {safety_errors}")

    work_order_template = build_work_order_template(
        bool(validation["clean_baseline"]) and not safety_errors,
        validation["source_statuses"],
    )

    if validation["pass"] and work_order_template["template_status"] != "ZERO_ERROR_WORK_ORDER_TEMPLATE_ACTIVE":
        errors.append(f"work-order template did not become active: {work_order_template['template_status']}")

    passed = not errors

    payload = {
        "module": MODULE_NAME,
        "template_status": (
            "ZERO_ERROR_WORK_ORDER_TEMPLATE_V1_READY"
            if passed
            else "ZERO_ERROR_WORK_ORDER_TEMPLATE_V1_BLOCKED"
        ),
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_GOVERNANCE_TEMPLATE",
        "final_decision": (
            "ZERO_ERROR_WORK_ORDER_TEMPLATE_READY_FOR_BACKLOG_REFRESH"
            if passed
            else "KEEP_FREEZE_REVIEW_WORK_ORDER_TEMPLATE_ERRORS"
        ),
        "next_action": (
            "BUILD_REPO_ONLY_DEVELOPMENT_BACKLOG_REFRESH_V1"
            if passed
            else "REVIEW_WORK_ORDER_TEMPLATE_ERRORS"
        ),
        "next_module": (
            "edge_factory_os_repo_only_development_backlog_refresh_v1.py"
            if passed
            else None
        ),
        "reason": (
            "Created reusable zero-error work-order template for future repo-only changes."
            if passed
            else "Work-order template validation failed."
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
            "current_step_untracked_ok": validation["current_step_untracked_ok"],
            "expected_untracked_during_run": validation["expected_untracked_during_run"],
            "actual_untracked_during_run": validation["actual_untracked_during_run"],
            "source_statuses": validation["source_statuses"],
            "clean_baseline": validation["clean_baseline"],
        },
        "work_order_template": work_order_template,
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
        "stage_recommended_now": False,
        "commit_recommended_now": False,
        "runtime_action_recommended_now": False,
        "capital_action_recommended_now": False,
        "holdout_action_recommended_now": False,
        "strategy_research_recommended_now": False,
        "candidate_generation_recommended_now": False,
        "family_release_recommended_now": False,
        "runtime_touched": False,
        "launcher_executed": False,
        "capital_changed": False,
        "live_or_real_orders": False,
        "holdout_accessed": False,
        "backup_deleted": False,
        "gitignore_changed": False,
        "git_add_force_used": False,
    }

    latest_json = OUT_DIR / "zero_error_work_order_template_v1_latest.json"
    timestamped_json = OUT_DIR / f"zero_error_work_order_template_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "zero_error_work_order_template_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS ZERO-ERROR WORK ORDER TEMPLATE v1",
        "=" * 100,
        f"template_status: {payload['template_status']}",
        f"severity: {payload['severity']}",
        f"final_decision: {payload['final_decision']}",
        f"next_action: {payload['next_action']}",
        f"next_module: {payload['next_module']}",
        f"reason: {payload['reason']}",
        f"critical_issue_count: {payload['critical_issue_count']}",
        f"warning_count: {payload['warning_count']}",
        "",
        "VALIDATION CHECKS",
        "-" * 100,
        json.dumps(validation["checks"], indent=2, sort_keys=True),
        "",
        "ERRORS",
        "-" * 100,
        json.dumps(errors, indent=2, sort_keys=True),
        "",
        "WORK ORDER TEMPLATE",
        "-" * 100,
        json.dumps(work_order_template, indent=2, sort_keys=True),
        "",
        "SAFETY",
        "-" * 100,
        json.dumps(SAFETY_FLAGS, indent=2, sort_keys=True),
        "",
        "GIT STATE",
        "-" * 100,
        json.dumps(validation["git_state"], indent=2, sort_keys=True),
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