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

MODULE_NAME = "edge_factory_os_repo_only_safe_development_resume_queue_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_repo_only_safe_development_resume_queue_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "14ad4a9"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_safe_development_resume_queue_v1.py"

SELECTOR_JSON = LAB_ROOT / "edge_factory_os_repo_only_governance_status_selector_v1" / "repo_only_governance_status_selector_v1_latest.json"
SELECTOR_POST_CHECK_JSON = LAB_ROOT / "edge_factory_os_repo_only_governance_status_selector_post_commit_check" / "repo_only_governance_status_selector_post_commit_check_latest.json"
APPROVAL_JSON = LAB_ROOT / "edge_factory_os_repo_only_risk_review_manual_approval_record_v1" / "repo_only_risk_review_manual_approval_record_v1_latest.json"
PLAN_JSON = LAB_ROOT / "edge_factory_os_repo_only_approval_gated_risk_review_plan_v1" / "repo_only_approval_gated_risk_review_plan_v1_latest.json"
PANEL_JSON = LAB_ROOT / "edge_factory_os_post_resume_full_governance_panel_refresh_v1" / "post_resume_full_governance_panel_refresh_v1_latest.json"

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_safe_development_resume_queue": True,
    "read_only_queue_only": True,
    "governance_status_selector_required": True,
    "manual_approval_record_required": True,
    "approval_gated_plan_required": True,
    "full_governance_panel_required": True,

    "repo_only_governance_allowed": True,
    "repo_only_audit_allowed": True,
    "repo_only_status_refresh_allowed": True,
    "repo_only_contract_preview_allowed": True,
    "read_only_validation_allowed": True,
    "repo_only_manifest_allowed": True,

    "manual_approval_present": False,
    "manual_approval_valid": False,
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
    "manual_risk_file_review_without_valid_approval",
    "risk_file_edit_without_approval",
    "risk_file_execution_without_approval",
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
        "selector_status",
        "audit_status",
        "manual_approval_record_status",
        "approval_plan_status",
        "refresh_status",
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
    loaded: Dict[str, Dict[str, Any]] = {}
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
    if head_subject != "Add repo-only governance status selector":
        errors.append(f"unexpected HEAD commit subject: {head_subject}")

    inputs = {
        "selector": (
            SELECTOR_JSON,
            "REPO_ONLY_GOVERNANCE_STATUS_SELECTOR_V1_READY",
            "edge_factory_os_repo_only_safe_development_resume_queue_v1.py",
        ),
        "selector_post_check": (
            SELECTOR_POST_CHECK_JSON,
            "REPO_ONLY_GOVERNANCE_STATUS_SELECTOR_POST_COMMIT_CHECK_PASS",
            "edge_factory_os_repo_only_safe_development_resume_queue_v1.py",
        ),
        "manual_approval_record": (
            APPROVAL_JSON,
            "REPO_ONLY_RISK_REVIEW_MANUAL_APPROVAL_RECORD_V1_READY",
            None,
        ),
        "approval_gated_plan": (
            PLAN_JSON,
            "REPO_ONLY_APPROVAL_GATED_RISK_REVIEW_PLAN_V1_READY",
            None,
        ),
        "full_governance_panel": (
            PANEL_JSON,
            "POST_RESUME_FULL_GOVERNANCE_PANEL_REFRESH_V1_READY",
            None,
        ),
    }

    for key, spec in inputs.items():
        path, expected_status, expected_next_module = spec
        obj: Optional[Dict[str, Any]] = None
        record: Optional[Dict[str, Any]] = None

        try:
            obj = load_json(path)
            record = source_record(path, obj)
            loaded[key] = obj
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
        "checks": checks,
        "git_state": git_state,
        "tracked_python_validation": py,
        "source_statuses": source_statuses,
        "loaded": loaded,
        "current_step_untracked_ok": current_step_untracked_ok,
        "expected_untracked_during_run": sorted(expected_untracked),
        "actual_untracked_during_run": sorted(actual_untracked),
        "clean_baseline": not errors,
    }


def build_resume_queue(loaded: Dict[str, Dict[str, Any]], clean_baseline: bool) -> Dict[str, Any]:
    selector_payload = loaded.get("selector", {})
    selector = selector_payload.get("governance_status_selector", {})
    risk_state = selector.get("risk_review_state", {})

    manual_risk_review_blocked = (
        risk_state.get("manual_approval_present") is False
        and risk_state.get("manual_approval_valid") is False
        and risk_state.get("risky_review_blocked") is True
        and risk_state.get("manual_review_allowed_now") is False
        and risk_state.get("risk_file_edit_allowed_now") is False
        and risk_state.get("risk_file_execution_allowed_now") is False
        and risk_state.get("patch_apply_allowed_now") is False
    )

    queue_items = [
        {
            "rank": 1,
            "key": "ACTIVE_CORE_MANIFEST_REFRESH",
            "module": "edge_factory_os_repo_only_active_core_manifest_refresh_v1.py",
            "scope": "REPO_ONLY_GOVERNANCE_DISCOVERY",
            "allowed_now": bool(clean_baseline and manual_risk_review_blocked),
            "reason": "Resume safe OS development by refreshing the active-core manifest before any larger module work.",
            "forbidden_actions": FORBIDDEN_ACTIONS,
        },
        {
            "rank": 2,
            "key": "GENERIC_FRAMEWORK_SKELETON_PLAN",
            "module": "edge_factory_os_repo_only_generic_framework_skeleton_plan_v1.py",
            "scope": "REPO_ONLY_GOVERNANCE_PLANNING",
            "allowed_now": False,
            "reason": "Wait until active-core manifest is refreshed.",
            "forbidden_actions": FORBIDDEN_ACTIONS,
        },
        {
            "rank": 3,
            "key": "RISKY_FILE_MANUAL_REVIEW",
            "module": None,
            "scope": "BLOCKED_UNTIL_EXPLICIT_APPROVAL",
            "allowed_now": False,
            "reason": "No valid manual approval exists for risky file review.",
            "forbidden_actions": FORBIDDEN_ACTIONS,
        },
        {
            "rank": 4,
            "key": "ANY_RUNTIME_OR_STRATEGY_ACTION",
            "module": None,
            "scope": "BLOCKED",
            "allowed_now": False,
            "reason": "Runtime, strategy, candidate, family, capital, live, and holdout actions remain blocked.",
            "forbidden_actions": FORBIDDEN_ACTIONS,
        },
    ]

    allowed_items = [item for item in queue_items if item["allowed_now"] is True]
    selected = allowed_items[0] if len(allowed_items) == 1 else None

    return {
        "resume_queue_status": "SAFE_DEVELOPMENT_RESUME_QUEUE_ACTIVE" if clean_baseline else "SAFE_DEVELOPMENT_RESUME_QUEUE_BLOCKED",
        "resume_queue_scope": "REPO_ONLY_GOVERNANCE_PLANNING",
        "manual_risk_review_blocked": manual_risk_review_blocked,
        "queue_items": queue_items,
        "selection": {
            "selection_status": (
                "SAFE_REPO_ONLY_ACTIVE_CORE_MANIFEST_REFRESH_SELECTED"
                if selected is not None
                else "SAFE_DEVELOPMENT_RESUME_QUEUE_SELECTION_BLOCKED"
            ),
            "allowed_selection_count": len(allowed_items),
            "selected": selected,
        },
        "blocked_domains": [
            "manual_risk_file_review",
            "risk_file_edit",
            "risk_file_execution",
            "patch_apply",
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
        "invariants": {
            "manual_risk_review_blocked": manual_risk_review_blocked is True,
            "exactly_one_allowed_queue_item": len(allowed_items) == 1,
            "selected_module_is_active_core_manifest_refresh": (
                selected is not None
                and selected.get("module") == "edge_factory_os_repo_only_active_core_manifest_refresh_v1.py"
            ),
            "no_runtime_strategy_or_patch_selected": True,
        },
        "recommended_next_step": {
            "step": "BUILD_REPO_ONLY_ACTIVE_CORE_MANIFEST_REFRESH",
            "module": "edge_factory_os_repo_only_active_core_manifest_refresh_v1.py",
            "scope": "REPO_ONLY_GOVERNANCE_DISCOVERY",
            "reason": "Safe development can resume with a read-only active-core manifest refresh.",
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

    queue = build_resume_queue(
        validation["loaded"],
        bool(validation["clean_baseline"]) and not safety_errors,
    )

    if validation["pass"] and queue["resume_queue_status"] != "SAFE_DEVELOPMENT_RESUME_QUEUE_ACTIVE":
        errors.append(f"resume queue did not become active: {queue['resume_queue_status']}")

    invariants = queue["invariants"]
    for key in [
        "manual_risk_review_blocked",
        "exactly_one_allowed_queue_item",
        "selected_module_is_active_core_manifest_refresh",
        "no_runtime_strategy_or_patch_selected",
    ]:
        if invariants.get(key) is not True:
            errors.append(f"invariant {key} not true: {invariants.get(key)}")

    passed = not errors
    selected = queue["selection"]["selected"]
    next_module = selected["module"] if passed and isinstance(selected, dict) else None

    payload = {
        "module": MODULE_NAME,
        "resume_queue_status": (
            "REPO_ONLY_SAFE_DEVELOPMENT_RESUME_QUEUE_V1_READY"
            if passed
            else "REPO_ONLY_SAFE_DEVELOPMENT_RESUME_QUEUE_V1_BLOCKED"
        ),
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_GOVERNANCE_PLANNING",
        "final_decision": (
            "SAFE_DEVELOPMENT_QUEUE_SELECTED_ACTIVE_CORE_MANIFEST_REFRESH"
            if passed
            else "KEEP_FREEZE_REVIEW_SAFE_DEVELOPMENT_RESUME_QUEUE_ERRORS"
        ),
        "next_action": (
            "BUILD_REPO_ONLY_ACTIVE_CORE_MANIFEST_REFRESH_V1"
            if passed
            else "REVIEW_SAFE_DEVELOPMENT_RESUME_QUEUE_ERRORS"
        ),
        "next_module": next_module,
        "reason": (
            "Selected a safe repo-only active-core manifest refresh as the next development step."
            if passed
            else "Safe development resume queue validation failed."
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
        "safe_development_resume_queue": queue,
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

    latest_json = OUT_DIR / "repo_only_safe_development_resume_queue_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_safe_development_resume_queue_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "repo_only_safe_development_resume_queue_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY SAFE DEVELOPMENT RESUME QUEUE v1",
        "=" * 100,
        f"resume_queue_status: {payload['resume_queue_status']}",
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
        "SELECTION",
        "-" * 100,
        json.dumps(queue["selection"], indent=2, sort_keys=True),
        "",
        "INVARIANTS",
        "-" * 100,
        json.dumps(queue["invariants"], indent=2, sort_keys=True),
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