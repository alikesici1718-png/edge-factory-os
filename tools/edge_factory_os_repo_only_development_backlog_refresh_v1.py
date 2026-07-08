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

MODULE_NAME = "edge_factory_os_repo_only_development_backlog_refresh_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_repo_only_development_backlog_refresh_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "9e5153e"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_development_backlog_refresh_v1.py"

TEMPLATE_JSON = LAB_ROOT / "edge_factory_os_zero_error_work_order_template_v1" / "zero_error_work_order_template_v1_latest.json"
TEMPLATE_POST_CHECK_JSON = LAB_ROOT / "edge_factory_os_zero_error_work_order_template_post_commit_check" / "zero_error_work_order_template_post_commit_check_latest.json"
GOVERNOR_JSON = LAB_ROOT / "edge_factory_os_post_resume_zero_error_governor_panel_v1" / "post_resume_zero_error_governor_panel_v1_latest.json"
ZERO_ERROR_PROTOCOL_JSON = LAB_ROOT / "edge_factory_os_zero_error_resume_protocol_v1" / "zero_error_resume_protocol_v1_latest.json"

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_development_backlog_refresh": True,
    "read_only_backlog_refresh_only": True,
    "work_order_template_required": True,
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
        "template_status",
        "audit_status",
        "governor_status",
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
    if head_subject != "Add zero-error work order template":
        errors.append(f"unexpected HEAD commit subject: {head_subject}")

    inputs = {
        "work_order_template": (TEMPLATE_JSON, "ZERO_ERROR_WORK_ORDER_TEMPLATE_V1_READY", "edge_factory_os_repo_only_development_backlog_refresh_v1.py"),
        "work_order_template_post_check": (TEMPLATE_POST_CHECK_JSON, "ZERO_ERROR_WORK_ORDER_TEMPLATE_POST_COMMIT_CHECK_PASS", "edge_factory_os_repo_only_development_backlog_refresh_v1.py"),
        "governor": (GOVERNOR_JSON, "POST_RESUME_ZERO_ERROR_GOVERNOR_PANEL_V1_READY", None),
        "zero_error_protocol": (ZERO_ERROR_PROTOCOL_JSON, "ZERO_ERROR_RESUME_PROTOCOL_V1_READY", None),
    }

    for key, spec in inputs.items():
        path, expected_status, expected_next_module = spec
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
        "current_step_untracked_ok": current_step_untracked_ok,
        "expected_untracked_during_run": sorted(expected_untracked),
        "actual_untracked_during_run": sorted(actual_untracked),
        "clean_baseline": clean_baseline,
    }


def build_backlog(clean_baseline: bool, source_statuses: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    backlog_items = [
        {
            "rank": 1,
            "backlog_key": "ZERO_ERROR_WORK_ORDER_INSTANTIATOR",
            "module": "edge_factory_os_zero_error_work_order_instantiator_v1.py",
            "scope": "REPO_ONLY_GOVERNANCE_TEMPLATE_INSTANTIATION",
            "allowed_now": clean_baseline,
            "purpose": "Instantiate the work-order template for future repo-only changes before any implementation module is created.",
            "why_next": "A template exists, but future changes need a concrete work-order instance generator so each step starts from the same schema.",
        },
        {
            "rank": 2,
            "backlog_key": "POST_RESUME_FULL_GOVERNANCE_PANEL_REFRESH",
            "module": "edge_factory_os_post_resume_full_governance_panel_refresh_v1.py",
            "scope": "REPO_ONLY_GOVERNANCE_STATUS_REFRESH",
            "allowed_now": False,
            "blocked_until": "ZERO_ERROR_WORK_ORDER_INSTANTIATOR_READY",
            "purpose": "Refresh all governance state after work-order instantiation exists.",
        },
        {
            "rank": 3,
            "backlog_key": "REPO_ONLY_OS_CAPABILITY_MAP_REFRESH",
            "module": "edge_factory_os_repo_only_capability_map_refresh_v1.py",
            "scope": "REPO_ONLY_GOVERNANCE_DISCOVERY",
            "allowed_now": False,
            "blocked_until": "POST_RESUME_FULL_GOVERNANCE_PANEL_REFRESH_READY",
            "purpose": "Map existing repo-only OS capabilities before choosing any larger development path.",
        },
    ]

    allowed_items = [item for item in backlog_items if item.get("allowed_now") is True]

    if len(allowed_items) == 1:
        selection = {
            "selection_status": "SELECTED_ONE_BACKLOG_ITEM",
            "selected": allowed_items[0],
            "reason": "Exactly one repo-only backlog item is currently allowed under zero-error constraints.",
        }
    else:
        selection = {
            "selection_status": "BLOCKED_BACKLOG_SELECTION_NOT_UNIQUE",
            "selected": None,
            "reason": f"expected exactly one allowed backlog item, found {len(allowed_items)}",
        }

    return {
        "backlog_status": "REPO_ONLY_DEVELOPMENT_BACKLOG_ACTIVE" if clean_baseline else "REPO_ONLY_DEVELOPMENT_BACKLOG_BLOCKED",
        "source_statuses": source_statuses,
        "backlog_items": backlog_items,
        "selection": selection,
        "blocked_domains": [
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
        ],
        "recommended_next_step": {
            "step": "BUILD_ZERO_ERROR_WORK_ORDER_INSTANTIATOR",
            "module": "edge_factory_os_zero_error_work_order_instantiator_v1.py",
            "scope": "REPO_ONLY_GOVERNANCE_TEMPLATE_INSTANTIATION",
            "reason": "Backlog selected the work-order instantiator as the only currently allowed repo-only development item.",
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

    backlog = build_backlog(
        bool(validation["clean_baseline"]) and not safety_errors,
        validation["source_statuses"],
    )

    selection = backlog["selection"]
    if validation["pass"] and selection["selection_status"] != "SELECTED_ONE_BACKLOG_ITEM":
        errors.append(f"backlog selection failed: {selection['reason']}")

    passed = not errors
    selected_module = selection["selected"]["module"] if passed else None

    payload = {
        "module": MODULE_NAME,
        "backlog_status": (
            "REPO_ONLY_DEVELOPMENT_BACKLOG_REFRESH_V1_READY"
            if passed
            else "REPO_ONLY_DEVELOPMENT_BACKLOG_REFRESH_V1_BLOCKED"
        ),
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_GOVERNANCE_PLANNING",
        "final_decision": (
            "REPO_ONLY_BACKLOG_READY_FOR_WORK_ORDER_INSTANTIATOR"
            if passed
            else "KEEP_FREEZE_REVIEW_BACKLOG_REFRESH_ERRORS"
        ),
        "next_action": (
            "BUILD_ZERO_ERROR_WORK_ORDER_INSTANTIATOR_V1"
            if passed
            else "REVIEW_BACKLOG_REFRESH_ERRORS"
        ),
        "next_module": selected_module,
        "reason": (
            "Refreshed repo-only development backlog and selected the work-order instantiator."
            if passed
            else "Repo-only backlog refresh validation failed."
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
        "backlog": backlog,
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

    latest_json = OUT_DIR / "repo_only_development_backlog_refresh_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_development_backlog_refresh_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "repo_only_development_backlog_refresh_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY DEVELOPMENT BACKLOG REFRESH v1",
        "=" * 100,
        f"backlog_status: {payload['backlog_status']}",
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
        "BACKLOG",
        "-" * 100,
        json.dumps(backlog, indent=2, sort_keys=True),
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