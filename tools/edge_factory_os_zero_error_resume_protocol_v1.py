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

MODULE_NAME = "edge_factory_os_zero_error_resume_protocol_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_zero_error_resume_protocol_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_START_HEAD_PREFIX = "0b2bd42"

WHOLE_SYSTEM_AUDIT_JSON = (
    LAB_ROOT
    / "edge_factory_os_whole_system_external_audit_no_repo_file"
    / "whole_system_external_audit_latest.json"
)

ZERO_ERROR_AUDIT_JSON = (
    LAB_ROOT
    / "edge_factory_os_zero_error_external_audit_after_untracked_cleanup"
    / "zero_error_external_final_audit_latest.json"
)

QUARANTINE_MANIFEST = (
    LAB_ROOT
    / "edge_factory_os_untracked_cleanup_quarantine"
    / "untracked_cleanup_20260514_111513"
    / "untracked_cleanup_manifest.json"
)

SAFETY_FLAGS: Dict[str, bool] = {
    "zero_error_resume_protocol": True,
    "os_development_resume_allowed_by_protocol": False,
    "requires_explicit_user_resume_approval": True,
    "read_only_preflight_required": True,
    "preview_required": True,
    "approval_required": True,
    "apply_audit_required": True,
    "post_commit_audit_required": True,
    "freeze_on_any_error": True,
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
    "runtime_touch_without_preflight",
    "launcher_execution",
    "capital_change",
    "active_paper_change",
    "live_trading",
    "real_order_execution",
    "strategy_research_without_resume_approval",
    "candidate_generation_without_resume_approval",
    "candidate_release",
    "family_release",
    "holdout_access",
    "gitignore_change",
    "backup_delete",
    "backup_move",
    "git_add_force",
    "blind_fix_all",
    "mass_metadata_patch",
    "direct_apply_without_approval",
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
        "dirty_tracked_paths": [x[3:] if len(x) > 3 else x for x in dirty_tracked],
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

    for rel in tracked_python_files():
        path = REPO_ROOT / rel
        try:
            data = path.read_bytes()
            if data.startswith(b"\xef\xbb\xbf"):
                bom_errors.append(rel)
            ast.parse(data.decode("utf-8"), filename=rel)
        except Exception as exc:
            syntax_errors.append({"path": rel, "error": repr(exc)})

    return {
        "tracked_python_file_count": len(tracked_python_files()),
        "syntax_error_count": len(syntax_errors),
        "bom_error_count": len(bom_errors),
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
        "pass": not syntax_errors and not bom_errors,
    }


def validate_protocol_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    checks: Dict[str, Any] = {}

    state = get_git_state()

    if not state["head"].startswith(EXPECTED_START_HEAD_PREFIX):
        errors.append(f"unexpected HEAD: {state['head']} expected {EXPECTED_START_HEAD_PREFIX}")

    # During protocol creation, this file may be the only untracked path.
    allowed_untracked = {"tools/edge_factory_os_zero_error_resume_protocol_v1.py"}
    untracked = set(state["untracked_paths"])
    unexpected_untracked = sorted(untracked - allowed_untracked)

    if state["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked paths present: {state['dirty_tracked_paths']}")

    if unexpected_untracked:
        errors.append(f"unexpected untracked paths present: {unexpected_untracked}")

    try:
        whole = load_json(WHOLE_SYSTEM_AUDIT_JSON)
        checks["whole_system_audit_status"] = whole.get("audit_status")
        checks["whole_system_critical_issue_count"] = whole.get("critical_issue_count")
        checks["whole_system_warning_count"] = whole.get("warning_count")
        if whole.get("audit_status") != "WHOLE_SYSTEM_EXTERNAL_AUDIT_PASS":
            errors.append(f"whole-system audit not PASS: {whole.get('audit_status')}")
        if whole.get("critical_issue_count") != 0:
            errors.append(f"whole-system critical_issue_count not 0: {whole.get('critical_issue_count')}")
        if whole.get("warning_count") != 0:
            errors.append(f"whole-system warning_count not 0: {whole.get('warning_count')}")
    except Exception as exc:
        errors.append(f"whole-system audit json check failed: {repr(exc)}")

    try:
        zero = load_json(ZERO_ERROR_AUDIT_JSON)
        checks["zero_error_audit_status"] = zero.get("audit_status")
        checks["zero_error_critical_issue_count"] = zero.get("critical_issue_count")
        checks["zero_error_warning_count"] = zero.get("warning_count")
        if zero.get("audit_status") != "ZERO_ERROR_EXTERNAL_FINAL_AUDIT_PASS":
            errors.append(f"zero-error audit not PASS: {zero.get('audit_status')}")
        if zero.get("critical_issue_count") != 0:
            errors.append(f"zero-error critical_issue_count not 0: {zero.get('critical_issue_count')}")
        if zero.get("warning_count") != 0:
            errors.append(f"zero-error warning_count not 0: {zero.get('warning_count')}")
    except Exception as exc:
        errors.append(f"zero-error audit json check failed: {repr(exc)}")

    try:
        quarantine = load_json(QUARANTINE_MANIFEST)
        checks["quarantine_manifest_status"] = quarantine.get("manifest_status")
        checks["quarantine_moved_file_count"] = quarantine.get("moved_file_count")
        if quarantine.get("manifest_status") != "UNTRACKED_CLEANUP_QUARANTINE_MANIFEST_READY":
            errors.append(f"quarantine manifest status bad: {quarantine.get('manifest_status')}")
        if quarantine.get("moved_file_count") != 6:
            errors.append(f"quarantine moved_file_count not 6: {quarantine.get('moved_file_count')}")
    except Exception as exc:
        errors.append(f"quarantine manifest check failed: {repr(exc)}")

    py = validate_tracked_python()
    checks["tracked_python_file_count"] = py["tracked_python_file_count"]
    checks["tracked_python_syntax_error_count"] = py["syntax_error_count"]
    checks["tracked_python_bom_error_count"] = py["bom_error_count"]

    if not py["pass"]:
        errors.append(f"tracked Python validation failed: syntax={py['syntax_errors'][:20]} bom={py['bom_errors']}")

    return {
        "pass": not errors,
        "errors": errors,
        "checks": checks,
        "git_state": state,
        "tracked_python_validation": py,
    }


def main() -> int:
    safety_shape_errors = [
        key for key, value in SAFETY_FLAGS.items()
        if not isinstance(value, bool)
    ]

    validation = validate_protocol_inputs()
    errors = list(validation["errors"])

    if safety_shape_errors:
        errors.append(f"safety flags are not boolean: {safety_shape_errors}")

    passed = not errors

    protocol = {
        "protocol_name": "EDGE_FACTORY_OS_ZERO_ERROR_RESUME_PROTOCOL_V1",
        "protocol_status": "READY" if passed else "BLOCKED",
        "freeze_default": True,
        "resume_requires_explicit_user_approval": True,
        "mandatory_chain_for_any_future_change": [
            "external_or_repo_read_only_preflight",
            "targeted_preview_no_apply",
            "approval_record",
            "exact_path_apply_only_if_approved",
            "read_only_audit_refresh",
            "exact_path_commit_no_force_add",
            "post_commit_external_audit",
        ],
        "hard_stop_conditions": [
            "git_dirty_before_start",
            "unknown_untracked_files",
            "tracked_python_syntax_error",
            "tracked_python_bom_error",
            "critical_issue_count_above_zero",
            "dangerous_safety_flag_true",
            "missing_or_stale_required_input_json",
            "attempted_runtime_or_launcher_or_capital_or_live_or_holdout_action",
            "any_request_for_fix_all_or_mass_patch",
        ],
        "allowed_work_after_resume": [
            "repo_only_governance",
            "repo_only_audit",
            "repo_only_contract_preview",
            "read_only_validation",
            "exact_path_commit_after_approval",
        ],
        "blocked_work_until_separate_approval": [
            "runtime_touch",
            "launcher_execution",
            "capital_change",
            "active_paper_change",
            "live_trading",
            "real_orders",
            "holdout_access",
            "strategy_research",
            "candidate_generation",
            "family_release",
        ],
    }

    payload = {
        "module": MODULE_NAME,
        "resume_protocol_status": (
            "ZERO_ERROR_RESUME_PROTOCOL_V1_READY"
            if passed
            else "ZERO_ERROR_RESUME_PROTOCOL_V1_BLOCKED"
        ),
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "ZERO_ERROR_RESUME_PROTOCOL_INSTALLATION",
        "final_decision": (
            "PROTOCOL_READY_COMMIT_THIS_TOOL_THEN_REQUIRE_USER_RESUME_APPROVAL"
            if passed
            else "KEEP_FREEZE_FIX_PROTOCOL_INPUT_ERRORS"
        ),
        "next_action": (
            "COMMIT_ZERO_ERROR_RESUME_PROTOCOL_EXACT_PATH_THEN_RUN_EXTERNAL_POST_COMMIT_CHECK"
            if passed
            else "REVIEW_PROTOCOL_ERRORS"
        ),
        "reason": (
            "Zero-error baseline verified; protocol installed as guard before any OS development resumes."
            if passed
            else "Protocol input validation errors detected."
        ),
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "critical_issue_count": len(errors),
        "warning_count": 0,
        "errors": errors,
        "warnings": [],
        "validation": validation,
        "protocol": protocol,
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
        "stage_recommended_now": False,
        "commit_recommended_now": False,
        "os_development_recommended_now": False,
        "runtime_action_recommended_now": False,
        "capital_action_recommended_now": False,
        "holdout_action_recommended_now": False,
        "runtime_touched": False,
        "launcher_executed": False,
        "capital_changed": False,
        "live_or_real_orders": False,
        "holdout_accessed": False,
        "backup_deleted": False,
        "gitignore_changed": False,
        "git_add_force_used": False,
    }

    latest_json = OUT_DIR / "zero_error_resume_protocol_v1_latest.json"
    timestamped_json = OUT_DIR / f"zero_error_resume_protocol_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "zero_error_resume_protocol_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS ZERO-ERROR RESUME PROTOCOL v1",
        "=" * 100,
        f"resume_protocol_status: {payload['resume_protocol_status']}",
        f"severity: {payload['severity']}",
        f"final_decision: {payload['final_decision']}",
        f"next_action: {payload['next_action']}",
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
        "PROTOCOL",
        "-" * 100,
        json.dumps(protocol, indent=2, sort_keys=True),
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