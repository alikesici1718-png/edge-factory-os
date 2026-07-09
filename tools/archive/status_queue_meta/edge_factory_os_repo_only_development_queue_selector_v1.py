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

MODULE_NAME = "edge_factory_os_repo_only_development_queue_selector_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_repo_only_development_queue_selector_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "3d8fb03"

STATUS_REFRESH_JSON = (
    LAB_ROOT
    / "edge_factory_os_post_resume_repo_only_status_refresh_v1"
    / "post_resume_repo_only_status_refresh_v1_latest.json"
)

STATUS_REFRESH_POST_CHECK_JSON = (
    LAB_ROOT
    / "edge_factory_os_post_resume_repo_only_status_refresh_post_commit_check"
    / "post_resume_repo_only_status_refresh_post_commit_check_latest.json"
)

PREFLIGHT_JSON = (
    LAB_ROOT
    / "edge_factory_os_next_step_read_only_preflight_v1"
    / "next_step_read_only_preflight_v1_latest.json"
)

CONTROLLED_RESUME_JSON = (
    LAB_ROOT
    / "edge_factory_os_controlled_resume_approval_v1"
    / "controlled_resume_approval_v1_latest.json"
)

ZERO_ERROR_PROTOCOL_JSON = (
    LAB_ROOT
    / "edge_factory_os_zero_error_resume_protocol_v1"
    / "zero_error_resume_protocol_v1_latest.json"
)

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_development_queue_selector": True,
    "read_only_selection_only": True,
    "controlled_resume_confirmed": True,
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


def validate_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    checks: Dict[str, Any] = {}
    git_state = get_git_state()

    if not git_state["head"].startswith(EXPECTED_HEAD_PREFIX):
        errors.append(f"unexpected HEAD: {git_state['head']} expected {EXPECTED_HEAD_PREFIX}")

    allowed_untracked = {"tools/edge_factory_os_repo_only_development_queue_selector_v1.py"}
    unexpected_untracked = sorted(set(git_state["untracked_paths"]) - allowed_untracked)

    if git_state["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked paths present: {git_state['dirty_tracked_paths']}")

    if unexpected_untracked:
        errors.append(f"unexpected untracked paths present: {unexpected_untracked}")

    head_subject = commit_subject("HEAD")
    checks["head_commit_subject"] = head_subject
    if head_subject != "Add post-resume repo-only status refresh":
        errors.append(f"unexpected HEAD commit subject: {head_subject}")

    inputs = {
        "status_refresh": STATUS_REFRESH_JSON,
        "status_refresh_post_check": STATUS_REFRESH_POST_CHECK_JSON,
        "preflight": PREFLIGHT_JSON,
        "controlled_resume": CONTROLLED_RESUME_JSON,
        "zero_error_protocol": ZERO_ERROR_PROTOCOL_JSON,
    }

    loaded: Dict[str, Dict[str, Any]] = {}

    for key, path in inputs.items():
        try:
            loaded[key] = load_json(path)
            checks[key] = {
                "path": str(path),
                "status": loaded[key].get("refresh_status")
                or loaded[key].get("audit_status")
                or loaded[key].get("preflight_status")
                or loaded[key].get("resume_approval_status")
                or loaded[key].get("resume_protocol_status"),
                "critical_issue_count": loaded[key].get("critical_issue_count"),
                "warning_count": loaded[key].get("warning_count"),
            }
        except Exception as exc:
            errors.append(f"cannot load {key}: {path} error={repr(exc)}")

    if "status_refresh" in loaded:
        if loaded["status_refresh"].get("refresh_status") != "POST_RESUME_REPO_ONLY_STATUS_REFRESH_V1_READY":
            errors.append(f"status refresh not ready: {loaded['status_refresh'].get('refresh_status')}")
        if loaded["status_refresh"].get("critical_issue_count") != 0:
            errors.append("status refresh critical_issue_count not 0")

    if "status_refresh_post_check" in loaded:
        if loaded["status_refresh_post_check"].get("audit_status") != "POST_RESUME_REPO_ONLY_STATUS_REFRESH_POST_COMMIT_CHECK_PASS":
            errors.append(f"status refresh post-check not pass: {loaded['status_refresh_post_check'].get('audit_status')}")
        if loaded["status_refresh_post_check"].get("critical_issue_count") != 0:
            errors.append("status refresh post-check critical_issue_count not 0")

    if "preflight" in loaded:
        if loaded["preflight"].get("preflight_status") != "NEXT_STEP_READ_ONLY_PREFLIGHT_V1_READY":
            errors.append(f"preflight not ready: {loaded['preflight'].get('preflight_status')}")
        if loaded["preflight"].get("critical_issue_count") != 0:
            errors.append("preflight critical_issue_count not 0")

    if "controlled_resume" in loaded:
        if loaded["controlled_resume"].get("resume_approval_status") != "CONTROLLED_RESUME_APPROVAL_V1_READY":
            errors.append(f"controlled resume not ready: {loaded['controlled_resume'].get('resume_approval_status')}")
        if loaded["controlled_resume"].get("critical_issue_count") != 0:
            errors.append("controlled resume critical_issue_count not 0")

    if "zero_error_protocol" in loaded:
        if loaded["zero_error_protocol"].get("resume_protocol_status") != "ZERO_ERROR_RESUME_PROTOCOL_V1_READY":
            errors.append(f"zero-error protocol not ready: {loaded['zero_error_protocol'].get('resume_protocol_status')}")
        if loaded["zero_error_protocol"].get("critical_issue_count") != 0:
            errors.append("zero-error protocol critical_issue_count not 0")

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
        "checks": checks,
        "git_state": git_state,
        "tracked_python_validation": py,
    }


def build_queue(validation: Dict[str, Any]) -> List[Dict[str, Any]]:
    git_state = validation["git_state"]
    py = validation["tracked_python_validation"]

    clean_validation = (
        validation["pass"]
        and git_state["dirty_tracked_count"] == 0
        and py["syntax_error_count"] == 0
        and py["bom_error_count"] == 0
    )

    clean_reason = [
        f"validation_pass={validation['pass']}",
        f"dirty_tracked_count={git_state['dirty_tracked_count']}",
        f"tracked_python_syntax_error_count={py['syntax_error_count']}",
        f"tracked_python_bom_error_count={py['bom_error_count']}",
    ]

    return [
        {
            "rank": 1,
            "queue_key": "POST_RESUME_ZERO_ERROR_GOVERNOR_PANEL",
            "module": "edge_factory_os_post_resume_zero_error_governor_panel_v1.py",
            "scope": "REPO_ONLY_GOVERNANCE_STATUS_PANEL",
            "allowed_now": clean_validation,
            "reason": "Create a compact repo-only panel that future steps can read before any work; no runtime/research/candidate action.",
            "validation_basis": clean_reason,
            "blocked_actions": [
                "runtime_touch",
                "launcher_execution",
                "capital_change",
                "strategy_research",
                "candidate_generation",
                "family_release",
            ],
        },
        {
            "rank": 2,
            "queue_key": "ZERO_ERROR_WORK_ORDER_TEMPLATE",
            "module": "edge_factory_os_zero_error_work_order_template_v1.py",
            "scope": "REPO_ONLY_GOVERNANCE_TEMPLATE",
            "allowed_now": False,
            "reason": "Useful after the governor panel exists; template should consume panel state.",
            "blocked_until": "POST_RESUME_ZERO_ERROR_GOVERNOR_PANEL_READY",
        },
        {
            "rank": 3,
            "queue_key": "REPO_ONLY_DEVELOPMENT_BACKLOG_REFRESH",
            "module": "edge_factory_os_repo_only_development_backlog_refresh_v1.py",
            "scope": "REPO_ONLY_GOVERNANCE_PLANNING",
            "allowed_now": False,
            "reason": "Backlog refresh should follow governor panel and work-order template.",
            "blocked_until": "ZERO_ERROR_WORK_ORDER_TEMPLATE_READY",
        },
    ]


def choose_queue_item(queue: List[Dict[str, Any]]) -> Dict[str, Any]:
    allowed = [item for item in queue if item.get("allowed_now") is True]
    if len(allowed) != 1:
        return {
            "selection_status": "BLOCKED_AMBIGUOUS_ALLOWED_QUEUE",
            "selected": None,
            "reason": f"expected exactly one allowed queue item, found {len(allowed)}",
        }

    return {
        "selection_status": "SELECTED_ONE_REPO_ONLY_QUEUE_ITEM",
        "selected": allowed[0],
        "reason": "Selected the only currently allowed repo-only governance item under zero-error constraints.",
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

    queue = build_queue(validation)
    selection = choose_queue_item(queue)

    if validation["pass"] and selection["selection_status"] != "SELECTED_ONE_REPO_ONLY_QUEUE_ITEM":
        errors.append(f"queue selection failed: {selection['reason']}")

    passed = not errors

    selected_module = None
    next_action = "REVIEW_QUEUE_SELECTOR_ERRORS"
    if passed:
        selected_module = selection["selected"]["module"]
        next_action = "BUILD_POST_RESUME_ZERO_ERROR_GOVERNOR_PANEL_V1"

    payload = {
        "module": MODULE_NAME,
        "selector_status": (
            "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_V1_READY"
            if passed
            else "REPO_ONLY_DEVELOPMENT_QUEUE_SELECTOR_V1_BLOCKED"
        ),
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_GOVERNANCE_QUEUE_SELECTION",
        "final_decision": (
            "SELECTED_REPO_ONLY_ZERO_ERROR_GOVERNOR_PANEL"
            if passed
            else "KEEP_FREEZE_REVIEW_QUEUE_SELECTOR_ERRORS"
        ),
        "next_action": next_action,
        "next_module": selected_module,
        "reason": (
            "Selected the next repo-only development item without enabling runtime, research, candidates, or family release."
            if passed
            else "Repo-only development queue selector validation failed."
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
        },
        "queue": queue,
        "selection": selection,
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

    latest_json = OUT_DIR / "repo_only_development_queue_selector_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_development_queue_selector_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "repo_only_development_queue_selector_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY DEVELOPMENT QUEUE SELECTOR v1",
        "=" * 100,
        f"selector_status: {payload['selector_status']}",
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
        "QUEUE",
        "-" * 100,
        json.dumps(queue, indent=2, sort_keys=True),
        "",
        "SELECTION",
        "-" * 100,
        json.dumps(selection, indent=2, sort_keys=True),
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