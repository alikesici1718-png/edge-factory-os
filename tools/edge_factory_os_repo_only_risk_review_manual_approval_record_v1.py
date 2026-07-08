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

MODULE_NAME = "edge_factory_os_repo_only_risk_review_manual_approval_record_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_repo_only_risk_review_manual_approval_record_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "b4a3fa1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_risk_review_manual_approval_record_v1.py"

PLAN_JSON = LAB_ROOT / "edge_factory_os_repo_only_approval_gated_risk_review_plan_v1" / "repo_only_approval_gated_risk_review_plan_v1_latest.json"
PLAN_POST_CHECK_JSON = LAB_ROOT / "edge_factory_os_repo_only_approval_gated_risk_review_plan_post_commit_check" / "repo_only_approval_gated_risk_review_plan_post_commit_check_latest.json"
RISKY_JSON = LAB_ROOT / "edge_factory_os_repo_only_risky_surface_review_v1" / "repo_only_risky_surface_review_v1_latest.json"
GOVERNOR_JSON = LAB_ROOT / "edge_factory_os_post_resume_zero_error_governor_panel_v1" / "post_resume_zero_error_governor_panel_v1_latest.json"

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only_risk_review_manual_approval_record": True,
    "read_only_approval_record_only": True,
    "approval_gated_plan_required": True,
    "risky_surface_review_required": True,
    "governor_panel_required": True,

    "repo_only_governance_allowed": True,
    "repo_only_audit_allowed": True,
    "repo_only_status_refresh_allowed": True,
    "repo_only_contract_preview_allowed": True,
    "read_only_validation_allowed": True,

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
        "approval_plan_status",
        "audit_status",
        "risky_surface_status",
        "governor_status",
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
    if head_subject != "Add approval-gated risk review plan":
        errors.append(f"unexpected HEAD commit subject: {head_subject}")

    inputs = {
        "approval_gated_plan": (PLAN_JSON, "REPO_ONLY_APPROVAL_GATED_RISK_REVIEW_PLAN_V1_READY", "edge_factory_os_repo_only_risk_review_manual_approval_record_v1.py"),
        "approval_gated_plan_post_check": (PLAN_POST_CHECK_JSON, "REPO_ONLY_APPROVAL_GATED_RISK_REVIEW_PLAN_POST_COMMIT_CHECK_PASS", "edge_factory_os_repo_only_risk_review_manual_approval_record_v1.py"),
        "risky_surface": (RISKY_JSON, "REPO_ONLY_OS_RISKY_SURFACE_REVIEW_V1_READY", None),
        "governor": (GOVERNOR_JSON, "POST_RESUME_ZERO_ERROR_GOVERNOR_PANEL_V1_READY", None),
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


def build_manual_approval_record(loaded: Dict[str, Dict[str, Any]], clean_baseline: bool) -> Dict[str, Any]:
    plan_payload = loaded.get("approval_gated_plan", {})
    plan = plan_payload.get("approval_gated_risk_review_plan", {})
    approval_model = plan.get("approval_model", {})
    required_next = plan.get("required_next_approval_module", {})

    manual_approval_present = False
    manual_approval_valid = False

    return {
        "manual_approval_record_status": "MANUAL_APPROVAL_RECORD_READY_NO_APPROVAL_PRESENT" if clean_baseline else "MANUAL_APPROVAL_RECORD_BLOCKED",
        "approval_scope": required_next.get("approval_scope", "REPO_ONLY_RISK_REVIEW_APPROVAL_NO_PATCH_NO_EXECUTION"),
        "approval_source": "ABSENT_BY_DESIGN",
        "manual_approval_present": manual_approval_present,
        "manual_approval_valid": manual_approval_valid,
        "approval_decision": "NO_VALID_APPROVAL_RISK_REVIEW_REMAINS_BLOCKED",
        "approval_model_from_plan": approval_model,
        "allowed_now": {
            "manual_risk_file_review": False,
            "risk_file_edit": False,
            "risk_file_execution": False,
            "patch_apply": False,
            "direct_fix": False,
            "runtime_touch": False,
            "launcher_execution": False,
            "capital_change": False,
            "live_trading": False,
            "real_orders": False,
            "holdout_access": False,
            "strategy_research": False,
            "candidate_generation": False,
            "candidate_release": False,
            "family_release": False,
        },
        "if_user_later_requests_review": {
            "required_phrase": "APPROVE_REPO_ONLY_RISK_REVIEW_NO_PATCH_NO_EXECUTION",
            "approval_limits": [
                "read-only manual review only",
                "no patch",
                "no execution",
                "no runtime",
                "no launcher",
                "no capital/live/real orders",
                "no holdout",
                "no strategy research",
                "no candidate/family release",
            ],
        },
        "invariants": {
            "manual_approval_present_false": manual_approval_present is False,
            "manual_approval_valid_false": manual_approval_valid is False,
            "manual_review_blocked": True,
            "patch_and_execution_blocked": True,
            "dangerous_actions_blocked": True,
        },
        "recommended_next_step": {
            "step": "BUILD_REPO_ONLY_GOVERNANCE_STATUS_SELECTOR",
            "module": "edge_factory_os_repo_only_governance_status_selector_v1.py",
            "scope": "REPO_ONLY_GOVERNANCE_PLANNING",
            "reason": "No valid manual approval exists, so do not review risky files; select next safe repo-only governance/status task.",
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

    record = build_manual_approval_record(
        validation["loaded"],
        bool(validation["clean_baseline"]) and not safety_errors,
    )

    if validation["pass"] and record["manual_approval_record_status"] != "MANUAL_APPROVAL_RECORD_READY_NO_APPROVAL_PRESENT":
        errors.append(f"manual approval record did not become ready: {record['manual_approval_record_status']}")

    invariants = record["invariants"]
    for key in [
        "manual_approval_present_false",
        "manual_approval_valid_false",
        "manual_review_blocked",
        "patch_and_execution_blocked",
        "dangerous_actions_blocked",
    ]:
        if invariants.get(key) is not True:
            errors.append(f"invariant {key} not true: {invariants.get(key)}")

    passed = not errors

    payload = {
        "module": MODULE_NAME,
        "manual_approval_record_status": (
            "REPO_ONLY_RISK_REVIEW_MANUAL_APPROVAL_RECORD_V1_READY"
            if passed
            else "REPO_ONLY_RISK_REVIEW_MANUAL_APPROVAL_RECORD_V1_BLOCKED"
        ),
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "REPO_ONLY_GOVERNANCE_APPROVAL_RECORD",
        "final_decision": (
            "NO_APPROVAL_PRESENT_RISK_REVIEW_BLOCKED_READY_FOR_GOVERNANCE_STATUS_SELECTOR"
            if passed
            else "KEEP_FREEZE_REVIEW_MANUAL_APPROVAL_RECORD_ERRORS"
        ),
        "next_action": (
            "BUILD_REPO_ONLY_GOVERNANCE_STATUS_SELECTOR_V1"
            if passed
            else "REVIEW_MANUAL_APPROVAL_RECORD_ERRORS"
        ),
        "next_module": (
            "edge_factory_os_repo_only_governance_status_selector_v1.py"
            if passed
            else None
        ),
        "reason": (
            "Recorded that no valid manual risk-review approval exists; risky file review, patching, and execution remain blocked."
            if passed
            else "Manual approval record validation failed."
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
        "manual_approval_record": record,
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

    latest_json = OUT_DIR / "repo_only_risk_review_manual_approval_record_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_risk_review_manual_approval_record_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "repo_only_risk_review_manual_approval_record_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS REPO-ONLY RISK REVIEW MANUAL APPROVAL RECORD v1",
        "=" * 100,
        f"manual_approval_record_status: {payload['manual_approval_record_status']}",
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
        "MANUAL APPROVAL RECORD",
        "-" * 100,
        json.dumps(record, indent=2, sort_keys=True),
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