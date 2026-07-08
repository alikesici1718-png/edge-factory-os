from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_stabilization_tooling_commit_approval_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_stabilization_tooling_commit_approval_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "578879b"

COMMIT_PLAN_JSON = (
    LAB_ROOT
    / "edge_factory_os_untracked_stabilization_tooling_commit_plan_v1"
    / "untracked_stabilization_tooling_commit_plan_v1_latest.json"
)

APPROVAL_TOOL_REL = "tools/edge_factory_os_stabilization_tooling_commit_approval_v1.py"

PLAN_COMMIT_CANDIDATES: Set[str] = {
    "tools/edge_factory_os_attention_issue_policy_classifier_after_gate_metadata_v4.py",
    "tools/edge_factory_os_attention_triage_classifier_gate_review_refresh_after_metadata_v4.py",
    "tools/edge_factory_os_invalid_existing_metadata_block_inspector_v1.py",
    "tools/edge_factory_os_metadata_classifier_rule_refinement_apply_v1.py",
    "tools/edge_factory_os_metadata_classifier_rule_refinement_approval_v1.py",
    "tools/edge_factory_os_metadata_classifier_rule_refinement_preview_v1.py",
    "tools/edge_factory_os_old_short_guarded_apply_lock_registry_v1.py",
    "tools/edge_factory_os_post_commit_read_only_status_after_gate_metadata_v4.py",
    "tools/edge_factory_os_stabilization_freeze_error_closure_controller_v1.py",
    "tools/edge_factory_os_untracked_hygiene_and_universe_guard_review_plan_v1.py",
    "tools/edge_factory_os_untracked_stabilization_tooling_commit_plan_v1.py",
}

APPROVED_COMMIT_PATHS: Set[str] = PLAN_COMMIT_CANDIDATES | {APPROVAL_TOOL_REL}

LEAVE_UNTRACKED_LOCKED_OR_REVIEW: Set[str] = {
    "tools/edge_factory_os_gate_metadata_patch_preview_v2.py",
    "tools/edge_factory_os_gate_metadata_patch_preview_v3.py",
    "tools/edge_factory_os_joint_null_distribution_validator_v1.py.readonly_fix_bak_20260514_022123",
    "tools/edge_factory_os_old_short_guarded_runtime_reenable_apply_v1.py",
    "tools/edge_factory_os_source_panel_anomaly_discovery_runner_v1.py.blocked_patch_bak_20260514_000647",
    "tools/edge_factory_os_universe_coverage_guard_v1.py",
}

KNOWN_ALLOWED_UNTRACKED: Set[str] = APPROVED_COMMIT_PATHS | LEAVE_UNTRACKED_LOCKED_OR_REVIEW

SAFETY_FLAGS: Dict[str, bool] = {
    "stabilization_freeze_active": True,
    "approval_only": True,
    "stage_performed_now": False,
    "commit_performed_now": False,
    "apply_performed_now": False,
    "direct_apply_allowed": False,
    "os_development_allowed": False,
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
    "old_short_guarded_apply_allowed": False,
    "mass_metadata_patch_allowed": False,
}

FORBIDDEN_ACTIONS: List[str] = [
    "git_add_force",
    "gitignore_change",
    "backup_delete",
    "backup_move",
    "old_short_guarded_apply_execution",
    "universe_guard_stage_without_approval",
    "universe_guard_delete",
    "universe_guard_move",
    "os_feature_development",
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
    "blind_fix_all",
    "mass_metadata_patch",
    "direct_apply",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: List[str], cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def get_git_state() -> Dict[str, Any]:
    head = run_cmd(["git", "rev-parse", "--short", "HEAD"])
    branch = run_cmd(["git", "branch", "--show-current"])
    status = run_cmd(["git", "status", "--porcelain=v1"])
    remote = run_cmd(["git", "status", "-sb"])

    status_lines = [line for line in status.stdout.splitlines() if line.strip()]
    untracked = [line[3:] for line in status_lines if line.startswith("?? ")]
    dirty_tracked_lines = [line for line in status_lines if not line.startswith("?? ")]

    dirty_tracked_paths: List[str] = []
    for line in dirty_tracked_lines:
        path = line[3:] if len(line) > 3 else line
        dirty_tracked_paths.append(path)

    return {
        "head": head.stdout.strip(),
        "branch": branch.stdout.strip(),
        "status_porcelain": status_lines,
        "remote_status_short": remote.stdout.splitlines(),
        "git_dirty": bool(status_lines),
        "dirty_tracked_count": len(dirty_tracked_lines),
        "dirty_tracked_paths": dirty_tracked_paths,
        "untracked_count": len(untracked),
        "untracked_paths": untracked,
    }


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_record(rel_path: str) -> Dict[str, Any]:
    path = REPO_ROOT / rel_path
    exists = path.exists()

    record: Dict[str, Any] = {
        "path": rel_path,
        "exists": exists,
        "size_bytes": None,
        "sha256": None,
        "syntax_ok": None,
        "syntax_error": None,
        "bom_detected": None,
        "line_count": None,
    }

    if not exists:
        return record

    data = path.read_bytes()
    record["size_bytes"] = len(data)
    record["sha256"] = hashlib.sha256(data).hexdigest()
    record["bom_detected"] = data.startswith(b"\xef\xbb\xbf")

    text = data.decode("utf-8", errors="replace")
    lines = text.splitlines()
    record["line_count"] = len(lines)

    if rel_path.endswith(".py"):
        try:
            ast.parse(text, filename=rel_path)
            record["syntax_ok"] = True
        except Exception as exc:
            record["syntax_ok"] = False
            record["syntax_error"] = repr(exc)

    return record


def fail_closed(reason: str, extra: Optional[Dict[str, Any]] = None) -> int:
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "approval_status": "STABILIZATION_TOOLING_COMMIT_APPROVAL_V1_FAIL_CLOSED",
        "severity": "BLOCKED",
        "allowed_scope": "READ_ONLY_STABILIZATION_TOOLING_COMMIT_APPROVAL",
        "final_decision": "STOP_NO_STAGE_NO_COMMIT",
        "next_action": "REVIEW_APPROVAL_FAILURE",
        "next_module": None,
        "reason": reason,
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "commit_plan_json": str(COMMIT_PLAN_JSON),
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
        "stage_recommended_now": False,
        "commit_recommended_now": False,
        "runtime_touched": False,
        "launcher_executed": False,
        "capital_changed": False,
        "live_or_real_orders": False,
        "holdout_accessed": False,
        "backup_deleted_or_moved": False,
        "gitignore_changed": False,
        "git_add_force_used": False,
    }
    if extra:
        payload.update(extra)

    out = OUT_DIR / "stabilization_tooling_commit_approval_v1_fail_closed_latest.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS STABILIZATION TOOLING COMMIT APPROVAL v1")
    print("=" * 100)
    print("approval_status: STABILIZATION_TOOLING_COMMIT_APPROVAL_V1_FAIL_CLOSED")
    print(f"reason: {reason}")
    print(f"output: {out}")
    return 2


def main() -> int:
    for key, value in SAFETY_FLAGS.items():
        if not isinstance(value, bool):
            raise SystemExit(f"safety flag is not boolean: {key}")

    git_state = get_git_state()

    if not git_state["head"].startswith(EXPECTED_HEAD_PREFIX):
        return fail_closed(
            "unexpected HEAD",
            {
                "expected_head_prefix": EXPECTED_HEAD_PREFIX,
                "git_state": git_state,
            },
        )

    if git_state["dirty_tracked_count"] != 0:
        return fail_closed(
            "tracked files dirty; refusing commit approval",
            {
                "git_state": git_state,
            },
        )

    current_untracked = set(git_state["untracked_paths"])
    unknown_untracked = sorted(current_untracked - KNOWN_ALLOWED_UNTRACKED)
    if unknown_untracked:
        return fail_closed(
            "unknown untracked paths present",
            {
                "unknown_untracked": unknown_untracked,
                "git_state": git_state,
            },
        )

    missing_approved = sorted(APPROVED_COMMIT_PATHS - current_untracked)
    if missing_approved:
        return fail_closed(
            "approved commit paths missing from untracked set",
            {
                "missing_approved": missing_approved,
                "git_state": git_state,
            },
        )

    missing_leave = sorted(LEAVE_UNTRACKED_LOCKED_OR_REVIEW - current_untracked)
    if missing_leave:
        return fail_closed(
            "leave-untracked paths missing from untracked set",
            {
                "missing_leave": missing_leave,
                "git_state": git_state,
            },
        )

    try:
        plan = load_json(COMMIT_PLAN_JSON)
    except Exception as exc:
        return fail_closed(
            "could not load commit plan json",
            {
                "error": repr(exc),
                "git_state": git_state,
            },
        )

    if plan.get("plan_status") != "UNTRACKED_STABILIZATION_TOOLING_COMMIT_PLAN_V1_READY_NO_STAGE":
        return fail_closed(
            "commit plan status unexpected",
            {
                "plan_status": plan.get("plan_status"),
                "git_state": git_state,
            },
        )

    plan_records = plan.get("plan_records") if isinstance(plan.get("plan_records"), dict) else {}
    plan_commit_candidates = set(plan_records.get("commit_candidate_tools") or [])
    plan_leave = set(plan_records.get("leave_untracked_locked_or_review") or [])

    if plan_commit_candidates != PLAN_COMMIT_CANDIDATES:
        return fail_closed(
            "plan commit candidate set mismatch",
            {
                "expected": sorted(PLAN_COMMIT_CANDIDATES),
                "actual": sorted(plan_commit_candidates),
                "missing": sorted(PLAN_COMMIT_CANDIDATES - plan_commit_candidates),
                "extra": sorted(plan_commit_candidates - PLAN_COMMIT_CANDIDATES),
                "git_state": git_state,
            },
        )

    if plan_leave != LEAVE_UNTRACKED_LOCKED_OR_REVIEW:
        return fail_closed(
            "plan leave-untracked set mismatch",
            {
                "expected": sorted(LEAVE_UNTRACKED_LOCKED_OR_REVIEW),
                "actual": sorted(plan_leave),
                "missing": sorted(LEAVE_UNTRACKED_LOCKED_OR_REVIEW - plan_leave),
                "extra": sorted(plan_leave - LEAVE_UNTRACKED_LOCKED_OR_REVIEW),
                "git_state": git_state,
            },
        )

    approved_records = [file_record(path) for path in sorted(APPROVED_COMMIT_PATHS)]
    leave_records = [file_record(path) for path in sorted(LEAVE_UNTRACKED_LOCKED_OR_REVIEW)]

    approval_errors: List[str] = []

    for rec in approved_records:
        if not rec["exists"]:
            approval_errors.append(f"approved path missing: {rec['path']}")
        if rec["path"].endswith(".py") and rec["syntax_ok"] is not True:
            approval_errors.append(f"approved path syntax failed: {rec['path']} error={rec['syntax_error']}")
        if rec["bom_detected"] is True:
            approval_errors.append(f"approved path has BOM: {rec['path']}")

    for rec in leave_records:
        if not rec["exists"]:
            approval_errors.append(f"leave-untracked path missing: {rec['path']}")

    if approval_errors:
        return fail_closed(
            "approval validation errors",
            {
                "approval_errors": approval_errors,
                "approved_records": approved_records,
                "leave_records": leave_records,
                "git_state": git_state,
            },
        )

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "approval_status": "STABILIZATION_TOOLING_COMMIT_APPROVAL_V1_READY_FOR_EXACT_PATH_COMMIT",
        "severity": "ATTENTION",
        "allowed_scope": "READ_ONLY_STABILIZATION_TOOLING_COMMIT_APPROVAL",
        "final_decision": "COMMIT_APPROVED_STABILIZATION_TOOLING_EXACT_PATHS_NO_FORCE_ADD",
        "next_action": "RUN_EXACT_PATH_GIT_ADD_AND_COMMIT_STABILIZATION_TOOLING_NO_FORCE_ADD",
        "next_module": "powershell_exact_path_commit",
        "reason": "approved exact-path stabilization tooling commit set; locked/review/backups remain untracked",
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "commit_plan_json": str(COMMIT_PLAN_JSON),
        "counts": {
            "approved_commit_path_count": len(APPROVED_COMMIT_PATHS),
            "plan_commit_candidate_count": len(PLAN_COMMIT_CANDIDATES),
            "approval_tool_extra_count": 1,
            "leave_untracked_count": len(LEAVE_UNTRACKED_LOCKED_OR_REVIEW),
            "unknown_untracked_count": len(unknown_untracked),
            "approval_error_count": len(approval_errors),
            "direct_apply_recommended_now_count": 0,
            "apply_recommended_now_count": 0,
            "stage_recommended_now_count": 0,
            "commit_recommended_now_count": 0,
        },
        "approved_commit_paths": sorted(APPROVED_COMMIT_PATHS),
        "plan_commit_candidates": sorted(PLAN_COMMIT_CANDIDATES),
        "leave_untracked_locked_or_review": sorted(LEAVE_UNTRACKED_LOCKED_OR_REVIEW),
        "approved_records": approved_records,
        "leave_records": leave_records,
        "recommended_commit_message": "Record stabilization freeze and recurrence guard tooling",
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
        "stage_recommended_now": False,
        "commit_recommended_now": False,
        "candidate_generation_recommended_now": False,
        "family_release_recommended_now": False,
        "runtime_action_recommended_now": False,
        "capital_action_recommended_now": False,
        "holdout_action_recommended_now": False,
        "target_files_modified": [],
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "runtime_touched": False,
        "launcher_executed": False,
        "capital_changed": False,
        "live_or_real_orders": False,
        "holdout_accessed": False,
        "backup_deleted_or_moved": False,
        "gitignore_changed": False,
        "git_add_force_used": False,
        "git_state": git_state,
    }

    latest_json = OUT_DIR / "stabilization_tooling_commit_approval_v1_latest.json"
    timestamped_json = OUT_DIR / f"stabilization_tooling_commit_approval_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "stabilization_tooling_commit_approval_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    txt_lines = [
        "EDGE FACTORY OS STABILIZATION TOOLING COMMIT APPROVAL v1",
        "=" * 100,
        f"approval_status: {payload['approval_status']}",
        f"severity: {payload['severity']}",
        f"allowed_scope: {payload['allowed_scope']}",
        f"final_decision: {payload['final_decision']}",
        f"next_action: {payload['next_action']}",
        f"next_module: {payload['next_module']}",
        f"reason: {payload['reason']}",
        "",
        "COUNTS",
        "-" * 100,
        json.dumps(payload["counts"], indent=2, sort_keys=True),
        "",
        "APPROVED COMMIT PATHS",
        "-" * 100,
        json.dumps(payload["approved_commit_paths"], indent=2, sort_keys=True),
        "",
        "LEAVE UNTRACKED LOCKED OR REVIEW",
        "-" * 100,
        json.dumps(payload["leave_untracked_locked_or_review"], indent=2, sort_keys=True),
        "",
        "SAFETY",
        "-" * 100,
        json.dumps(SAFETY_FLAGS, indent=2, sort_keys=True),
        "",
        "GIT STATE",
        "-" * 100,
        json.dumps(git_state, indent=2, sort_keys=True),
        "",
        "OUTPUTS",
        "-" * 100,
        f"latest_json: {latest_json}",
        f"timestamped_json: {timestamped_json}",
        f"latest_txt: {latest_txt}",
    ]

    latest_txt.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")

    print("\n".join(txt_lines))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())