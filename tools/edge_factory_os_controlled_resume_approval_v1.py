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

MODULE_NAME = "edge_factory_os_controlled_resume_approval_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_controlled_resume_approval_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "0f5b103"

ZERO_ERROR_PROTOCOL_JSON = (
    LAB_ROOT
    / "edge_factory_os_zero_error_resume_protocol_v1"
    / "zero_error_resume_protocol_v1_latest.json"
)

ZERO_ERROR_POST_CHECK_JSON = (
    LAB_ROOT
    / "edge_factory_os_zero_error_resume_protocol_post_commit_check"
    / "zero_error_resume_protocol_post_commit_check_latest.json"
)

WHOLE_SYSTEM_AUDIT_JSON = (
    LAB_ROOT
    / "edge_factory_os_whole_system_external_audit_no_repo_file"
    / "whole_system_external_audit_latest.json"
)

ZERO_ERROR_FINAL_AUDIT_JSON = (
    LAB_ROOT
    / "edge_factory_os_zero_error_external_audit_after_untracked_cleanup"
    / "zero_error_external_final_audit_latest.json"
)

SAFETY_FLAGS: Dict[str, bool] = {
    "controlled_resume_approval": True,
    "os_development_resume_approved": True,
    "zero_error_protocol_required": True,
    "read_only_preflight_required": True,
    "targeted_preview_required": True,
    "approval_required": True,
    "exact_path_apply_required": True,
    "audit_refresh_required": True,
    "post_commit_external_audit_required": True,
    "freeze_on_any_error": True,

    "repo_only_governance_allowed": True,
    "repo_only_audit_allowed": True,
    "repo_only_contract_preview_allowed": True,
    "read_only_validation_allowed": True,
    "exact_path_commit_after_approval_allowed": True,

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
    "runtime_touch_without_separate_approval",
    "launcher_execution",
    "capital_change",
    "active_paper_change",
    "live_trading",
    "real_order_execution",
    "strategy_research_without_separate_approval",
    "candidate_generation_without_separate_approval",
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


def validate_inputs() -> Dict[str, Any]:
    errors: List[str] = []
    checks: Dict[str, Any] = {}

    git_state = get_git_state()

    if not git_state["head"].startswith(EXPECTED_HEAD_PREFIX):
        errors.append(f"unexpected HEAD: {git_state['head']} expected {EXPECTED_HEAD_PREFIX}")

    # During creation, this file may be the only untracked file.
    allowed_untracked = {"tools/edge_factory_os_controlled_resume_approval_v1.py"}
    unexpected_untracked = sorted(set(git_state["untracked_paths"]) - allowed_untracked)

    if git_state["dirty_tracked_count"] != 0:
        errors.append(f"dirty tracked paths present: {git_state['dirty_tracked_paths']}")
    if unexpected_untracked:
        errors.append(f"unexpected untracked paths present: {unexpected_untracked}")

    inputs = {
        "zero_error_protocol": ZERO_ERROR_PROTOCOL_JSON,
        "zero_error_post_check": ZERO_ERROR_POST_CHECK_JSON,
        "whole_system_audit": WHOLE_SYSTEM_AUDIT_JSON,
        "zero_error_final_audit": ZERO_ERROR_FINAL_AUDIT_JSON,
    }

    loaded: Dict[str, Dict[str, Any]] = {}

    for key, path in inputs.items():
        try:
            loaded[key] = load_json(path)
            checks[key] = {
                "path": str(path),
                "status": loaded[key].get("resume_protocol_status") or loaded[key].get("audit_status"),
                "critical_issue_count": loaded[key].get("critical_issue_count"),
                "warning_count": loaded[key].get("warning_count"),
            }
        except Exception as exc:
            errors.append(f"cannot load {key}: {path} error={repr(exc)}")

    if "zero_error_protocol" in loaded:
        if loaded["zero_error_protocol"].get("resume_protocol_status") != "ZERO_ERROR_RESUME_PROTOCOL_V1_READY":
            errors.append(f"zero_error_protocol not ready: {loaded['zero_error_protocol'].get('resume_protocol_status')}")
        if loaded["zero_error_protocol"].get("critical_issue_count") != 0:
            errors.append("zero_error_protocol critical_issue_count not 0")

    if "zero_error_post_check" in loaded:
        if loaded["zero_error_post_check"].get("audit_status") != "ZERO_ERROR_RESUME_PROTOCOL_POST_COMMIT_CHECK_PASS":
            errors.append(f"zero_error_post_check not pass: {loaded['zero_error_post_check'].get('audit_status')}")
        if loaded["zero_error_post_check"].get("critical_issue_count") != 0:
            errors.append("zero_error_post_check critical_issue_count not 0")

    if "whole_system_audit" in loaded:
        if loaded["whole_system_audit"].get("audit_status") != "WHOLE_SYSTEM_EXTERNAL_AUDIT_PASS":
            errors.append(f"whole_system_audit not pass: {loaded['whole_system_audit'].get('audit_status')}")
        if loaded["whole_system_audit"].get("critical_issue_count") != 0:
            errors.append("whole_system_audit critical_issue_count not 0")

    if "zero_error_final_audit" in loaded:
        if loaded["zero_error_final_audit"].get("audit_status") != "ZERO_ERROR_EXTERNAL_FINAL_AUDIT_PASS":
            errors.append(f"zero_error_final_audit not pass: {loaded['zero_error_final_audit'].get('audit_status')}")
        if loaded["zero_error_final_audit"].get("critical_issue_count") != 0:
            errors.append("zero_error_final_audit critical_issue_count not 0")

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


def main() -> int:
    safety_errors = [
        key for key, value in SAFETY_FLAGS.items()
        if not isinstance(value, bool)
    ]

    validation = validate_inputs()
    errors = list(validation["errors"])

    if safety_errors:
        errors.append(f"safety flags are not boolean: {safety_errors}")

    passed = not errors

    resume_policy = {
        "resume_policy_name": "EDGE_FACTORY_OS_CONTROLLED_RESUME_APPROVAL_V1",
        "resume_policy_status": "APPROVED_UNDER_ZERO_ERROR_PROTOCOL" if passed else "BLOCKED",
        "resume_scope": "CONTROLLED_REPO_ONLY_OS_DEVELOPMENT",
        "allowed_next_work": [
            "repo_only_os_governance_module",
            "repo_only_status_refresh",
            "read_only_preflight",
            "targeted_preview_no_apply",
            "approval_record",
            "exact_path_commit_after_post_audit",
        ],
        "still_blocked_without_separate_approval": [
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
        "mandatory_zero_error_chain": [
            "read_only_preflight",
            "targeted_preview_no_apply",
            "approval_record",
            "exact_path_apply_only_if_approved",
            "read_only_audit_refresh",
            "exact_path_commit_no_force_add",
            "post_commit_external_audit",
        ],
        "freeze_triggers": [
            "any_dirty_tracked_file_before_start",
            "any_untracked_file_not_created_by_current_step",
            "any_syntax_or_bom_error",
            "any_critical_issue_count_above_zero",
            "any_dangerous_safety_flag_true",
            "any_runtime_or_launcher_or_capital_or_live_or_holdout_attempt",
            "any_fix_all_or_mass_patch_request",
        ],
    }

    payload = {
        "module": MODULE_NAME,
        "resume_approval_status": (
            "CONTROLLED_RESUME_APPROVAL_V1_READY"
            if passed
            else "CONTROLLED_RESUME_APPROVAL_V1_BLOCKED"
        ),
        "severity": "OK" if passed else "BLOCKED",
        "allowed_scope": "CONTROLLED_REPO_ONLY_OS_DEVELOPMENT_RESUME_APPROVAL",
        "final_decision": (
            "CONTROLLED_OS_DEVELOPMENT_RESUME_APPROVED_UNDER_ZERO_ERROR_PROTOCOL"
            if passed
            else "KEEP_FREEZE_FIX_RESUME_APPROVAL_ERRORS"
        ),
        "next_action": (
            "START_NEXT_OS_DEVELOPMENT_STEP_WITH_READ_ONLY_PREFLIGHT_ONLY"
            if passed
            else "REVIEW_RESUME_APPROVAL_ERRORS"
        ),
        "next_module": (
            "edge_factory_os_next_step_read_only_preflight_v1.py"
            if passed
            else None
        ),
        "reason": (
            "Whole-system zero-error baseline is clean; controlled repo-only OS development may resume under mandatory zero-error chain."
            if passed
            else "Resume approval input validation failed."
        ),
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "critical_issue_count": len(errors),
        "warning_count": 0,
        "errors": errors,
        "warnings": [],
        "validation": validation,
        "resume_policy": resume_policy,
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
        "stage_recommended_now": False,
        "commit_recommended_now": False,
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

    latest_json = OUT_DIR / "controlled_resume_approval_v1_latest.json"
    timestamped_json = OUT_DIR / f"controlled_resume_approval_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "controlled_resume_approval_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "EDGE FACTORY OS CONTROLLED RESUME APPROVAL v1",
        "=" * 100,
        f"resume_approval_status: {payload['resume_approval_status']}",
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
        "RESUME POLICY",
        "-" * 100,
        json.dumps(resume_policy, indent=2, sort_keys=True),
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