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

MODULE_NAME = "edge_factory_os_post_resume_full_governance_panel_refresh_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_post_resume_full_governance_panel_refresh_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "0139861"
CURRENT_TOOL_REL = "tools/edge_factory_os_post_resume_full_governance_panel_refresh_v1.py"

INSTANTIATOR_JSON = LAB_ROOT / "edge_factory_os_zero_error_work_order_instantiator_v1" / "zero_error_work_order_instantiator_v1_latest.json"
INSTANTIATOR_POST_CHECK_JSON = LAB_ROOT / "edge_factory_os_zero_error_work_order_instantiator_post_commit_check" / "zero_error_work_order_instantiator_post_commit_check_latest.json"
GOVERNOR_JSON = LAB_ROOT / "edge_factory_os_post_resume_zero_error_governor_panel_v1" / "post_resume_zero_error_governor_panel_v1_latest.json"
TEMPLATE_JSON = LAB_ROOT / "edge_factory_os_zero_error_work_order_template_v1" / "zero_error_work_order_template_v1_latest.json"
BACKLOG_JSON = LAB_ROOT / "edge_factory_os_repo_only_development_backlog_refresh_v1" / "repo_only_development_backlog_refresh_v1_latest.json"

SAFETY_FLAGS: Dict[str, bool] = {
    "post_resume_full_governance_panel_refresh": True,
    "read_only_panel_refresh_only": True,
    "work_order_instance_required": True,
    "governor_panel_required": True,
    "work_order_template_required": True,
    "backlog_required": True,

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
        "instantiator_status",
        "audit_status",
        "governor_status",
        "template_status",
        "backlog_status",
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
    status = record.get("status")
    if status is None:
        errors.append(f"{key} status field missing")
    elif status != expected_status:
        errors.append(f"{key} status mismatch: expected={expected_status} actual={status}")

    validate_count_zero(errors, key, record, "critical_issue_count")
    validate_count_zero(errors, key, record, "warning_count")

    if expected_next_module is not None and record.get("next_module") != expected_next_module:
        errors.append(
            f"{key} next_module mismatch: expected={expected_next_module} actual={record.get('next_module')}"
        )


def validate_work_order_instance(errors: List[str], obj: Dict[str, Any]) -> Dict[str, Any]:
    work_order = obj.get("work_order_instance")
    if not isinstance(work_order, dict):
        errors.append("work_order_instance missing or invalid")
        return {}

    expected_module = "edge_factory_os_post_resume_full_governance_panel_refresh_v1.py"
    expected_tool = "tools/edge_factory_os_post_resume_full_governance_panel_refresh_v1.py"

    if work_order.get("work_order_status") != "ZERO_ERROR_WORK_ORDER_INSTANCE_ACTIVE":
        errors.append(f"work_order_status mismatch: {work_order.get('work_order_status')}")
    if work_order.get("target_next_module") != expected_module:
        errors.append(f"target_next_module mismatch: {work_order.get('target_next_module')}")
    if work_order.get("target_expected_single_untracked_path") != expected_tool:
        errors.append(f"target_expected_single_untracked_path mismatch: {work_order.get('target_expected_single_untracked_path')}")
    if work_order.get("target_exact_commit_paths") != [expected_tool]:
        errors.append(f"target_exact_commit_paths mismatch: {work_order.get('target_exact_commit_paths')}")
    if work_order.get("mutates_runtime") is not False:
        errors.append(f"mutates_runtime not false: {work_order.get('mutates_runtime')}")
    if work_order.get("allowed_scope") != "REPO_ONLY_GOVERNANCE_STATUS_REFRESH":
        errors.append(f"allowed_scope mismatch: {work_order.get('allowed_scope')}")

    return {
        "work_order_id": work_order.get("work_order_id"),
        "target_next_module": work_order.get("target_next_module"),
        "target_expected_single_untracked_path": work_order.get("target_expected_single_untracked_path"),
        "target_exact_commit_paths": work_order.get("target_exact_commit_paths"),
        "allowed_scope": work_order.get("allowed_scope"),
        "mutates_runtime": work_order.get("mutates_runtime"),
    }


def validate_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    checks: Dict[str, Any] = {}
    source_statuses: Dict[str, Dict[str, Any]] = {}
    work_order_summary: Dict[str, Any] = {}
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
    if head_subject != "Add zero-error work order instantiator":
        errors.append(f"unexpected HEAD commit subject: {head_subject}")

    inputs = {
        "instantiator": (INSTANTIATOR_JSON, "ZERO_ERROR_WORK_ORDER_INSTANTIATOR_V1_READY", "edge_factory_os_post_resume_full_governance_panel_refresh_v1.py"),
        "instantiator_post_check": (INSTANTIATOR_POST_CHECK_JSON, "ZERO_ERROR_WORK_ORDER_INSTANTIATOR_POST_COMMIT_CHECK_PASS", "edge_factory_os_post_resume_full_governance_panel_refresh_v1.py"),
        "governor": (GOVERNOR_JSON, "POST_RESUME_ZERO_ERROR_GOVERNOR_PANEL_V1_READY", None),
        "work_order_template": (TEMPLATE_JSON, "ZERO_ERROR_WORK_ORDER_TEMPLATE_V1_READY", None),
        "backlog": (BACKLOG_JSON, "REPO_ONLY_DEVELOPMENT_BACKLOG_REFRESH_V1_READY", None),
    }

    for key, spec in inputs.items():
        path, expected_status, expected_next_module = spec
        obj: Optional[Dict[str, Any]] = None
        record: Optional[Dict[str, Any]] = None

        try:
            obj = load_json(path)
            record = source_record(path, obj)
        except Exception as exc:
            errors.append(f"cannot load {key}: {path} error={repr(exc)}")

        if record is not None:
            source_statuses[key] = record
            checks[key] = record
            validate_status_record(errors, key, record, expected_status, expected_next_module)

        if key == "instantiator" and obj is not None:
            work_order_summary = validate_work_order_instance(errors, obj)

    py = validate_tracked_python()
    checks["tracked_python"] = {
        "tracked_python_file_count": py["tracked_python_file_count"],
        "syntax_error_count": py["syntax_error_count"],
        "bom_error_count": py["bom_error_count"],
    }

    if not py["pass"]:
        errors.append(f"tracked Python validation failed: syntax={py['syntax_errors'][:20]} bom={py['bom_errors']}")

    clean_baseline = not errors

    return {
        "pass": not errors,
        "errors": errors,
        "checks": checks,
        "git_state": git_state,
        "tracked_python_validation": py,
        "source_statuses": source_statuses,
        "work_order_summary": work_order_summary,
        "current_step_untracked_ok": current_step_untracked_ok,
        "expected_untracked_during_run": sorted(expected_untracked),
        "actual_untracked_during_run": sorted(actual_untracked),
        "clean_baseline": clean_baseline,
    }


def build_full_governance_panel(
    clean_baseline: bool,
    source_statuses: Dict[str, Dict[str, Any]],
    work_order_summary: Dict[str, Any],
    git_state: Dict[str, Any],
    py: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "panel_status": "POST_RESUME_FULL_GOVERNANCE_PANEL_ACTIVE" if clean_baseline else "POST_RESUME_FULL_GOVERNANCE_PANEL_BLOCKED",
        "panel_scope": "REPO_ONLY_GOVERNANCE_STATUS_REFRESH",
        "current_repo_state": {
            "head": git_state["head"],
            "branch": git_state["branch"],
            "dirty_tracked_count": git_state["dirty_tracked_count"],
            "untracked_count": git_state["untracked_count"],
            "tracked_python_file_count": py["tracked_python_file_count"],
            "tracked_python_syntax_error_count": py["syntax_error_count"],
            "tracked_python_bom_error_count": py["bom_error_count"],
        },
        "source_statuses": source_statuses,
        "work_order_summary": work_order_summary,
        "zero_error_chain_status": "ACTIVE" if clean_baseline else "BLOCKED",
        "allowed_now": [
            "repo_only_governance",
            "repo_only_audit",
            "repo_only_status_refresh",
            "repo_only_contract_preview",
            "read_only_validation",
        ],
        "blocked_without_separate_approval": [
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
            "gitignore_change",
            "backup_delete",
            "backup_move",
            "git_add_force",
            "fix_all",
            "mass_patch",
        ],
        "hard_freeze_triggers": [
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
            "step": "BUILD_REPO_ONLY_OS_CAPABILITY_MAP_REFRESH",
            "module": "edge_factory_os_repo_only_capability_map_refresh_v1.py",
            "scope": "REPO_ONLY_GOVERNANCE_DISCOVERY",
            "reason": "Full governance panel is refreshed; next safe repo-only step is capability map refresh before any larger OS development.",
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

    full_panel = build_full_governance_panel(
        bool(validation["clean_baseline"]) and not safety_errors,
        validation["source_statuses"],
        validation["work_order_summary"],
        validation["git_state"],
        validation["tracked_python_validation"],
    )

    if validation["pass"] and full_panel["panel_status"] != "POST_RESUME_FULL_GOVERNANCE_PANEL_ACTIVE":
        errors.append(f"full governance panel did not become active: {full_panel['panel_status']}")

    passed = not errors

    payload = {
        "module": MODULE_NAME,
        "refresh_status": (
            "POST_RESUME_FULL_GOVERNANCE_PANEL_REFRESH_V1_READY"
            if passed
            else "POST_RESUME_FULL_GOVERNANCE_PANEL_REFRESH_V1_BLOCKED"
        ),
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_GOVERNANCE_STATUS_REFRESH",
        "final_decision": (
            "FULL_GOVERNANCE_PANEL_READY_FOR_CAPABILITY_MAP_REFRESH"
            if passed
            else "KEEP_FREEZE_REVIEW_FULL_GOVERNANCE_PANEL_ERRORS"
        ),
        "next_action": (
            "BUILD_REPO_ONLY_OS_CAPABILITY_MAP_REFRESH_V1"
            if passed
            else "REVIEW_FULL_GOVERNANCE_PANEL_ERRORS"
        ),
        "next_module": (
            "edge_factory_os_repo_only_capability_map_refresh_v1.py"
            if passed
            else None
        ),
        "reason": (
            "Refreshed full repo-only governance panel under zero-error controls."
            if passed
            else "Full governance panel refresh validation failed."
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
            "work_order_summary": validation["work_order_summary"],
            "clean_baseline": validation["clean_baseline"],
        },
        "full_governance_panel": full_panel,
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
        "candidate_release_recommended_now": False,
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

    latest_json = OUT_DIR / "post_resume_full_governance_panel_refresh_v1_latest.json"
    timestamped_json = OUT_DIR / f"post_resume_full_governance_panel_refresh_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "post_resume_full_governance_panel_refresh_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS POST-RESUME FULL GOVERNANCE PANEL REFRESH v1",
        "=" * 100,
        f"refresh_status: {payload['refresh_status']}",
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
        "FULL GOVERNANCE PANEL",
        "-" * 100,
        json.dumps(full_panel, indent=2, sort_keys=True),
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