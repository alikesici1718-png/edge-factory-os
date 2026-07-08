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

MODULE_NAME = "edge_factory_os_untracked_stabilization_tooling_commit_plan_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_untracked_stabilization_tooling_commit_plan_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "578879b"

UNTRACKED_HYGIENE_JSON = (
    LAB_ROOT
    / "edge_factory_os_untracked_hygiene_and_universe_guard_review_plan_v1"
    / "untracked_hygiene_and_universe_guard_review_plan_v1_latest.json"
)

OLD_SHORT_LOCK_JSON = (
    LAB_ROOT
    / "edge_factory_os_old_short_guarded_apply_lock_registry_v1"
    / "old_short_guarded_apply_lock_registry_v1_latest.json"
)

POLICY_JSON = (
    LAB_ROOT
    / "edge_factory_os_attention_issue_policy_classifier_after_gate_metadata_v4"
    / "attention_issue_policy_classifier_after_metadata_v4_latest.json"
)

COMMIT_CANDIDATE_TOOLS: Set[str] = {
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

LEAVE_UNTRACKED_LOCKED_OR_REVIEW: Set[str] = {
    "tools/edge_factory_os_gate_metadata_patch_preview_v2.py",
    "tools/edge_factory_os_gate_metadata_patch_preview_v3.py",
    "tools/edge_factory_os_joint_null_distribution_validator_v1.py.readonly_fix_bak_20260514_022123",
    "tools/edge_factory_os_old_short_guarded_runtime_reenable_apply_v1.py",
    "tools/edge_factory_os_source_panel_anomaly_discovery_runner_v1.py.blocked_patch_bak_20260514_000647",
    "tools/edge_factory_os_universe_coverage_guard_v1.py",
}

KNOWN_ALLOWED_UNTRACKED: Set[str] = COMMIT_CANDIDATE_TOOLS | LEAVE_UNTRACKED_LOCKED_OR_REVIEW

SAFETY_FLAGS: Dict[str, bool] = {
    "stabilization_freeze_active": True,
    "read_only_commit_plan": True,
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
        "plan_status": "UNTRACKED_STABILIZATION_TOOLING_COMMIT_PLAN_V1_FAIL_CLOSED",
        "severity": "BLOCKED",
        "allowed_scope": "READ_ONLY_UNTRACKED_TOOLING_COMMIT_PLAN",
        "final_decision": "STOP_NO_STAGE_NO_COMMIT",
        "next_action": "REVIEW_COMMIT_PLAN_FAILURE",
        "next_module": None,
        "reason": reason,
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
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

    out = OUT_DIR / "untracked_stabilization_tooling_commit_plan_v1_fail_closed_latest.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS UNTRACKED STABILIZATION TOOLING COMMIT PLAN v1")
    print("=" * 100)
    print("plan_status: UNTRACKED_STABILIZATION_TOOLING_COMMIT_PLAN_V1_FAIL_CLOSED")
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
            "tracked files dirty; refusing commit plan",
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

    missing_commit_candidates = sorted(COMMIT_CANDIDATE_TOOLS - current_untracked)
    missing_leave_items = sorted(LEAVE_UNTRACKED_LOCKED_OR_REVIEW - current_untracked)

    if missing_commit_candidates:
        return fail_closed(
            "expected stabilization commit candidate tools missing from untracked set",
            {
                "missing_commit_candidates": missing_commit_candidates,
                "git_state": git_state,
            },
        )

    if missing_leave_items:
        return fail_closed(
            "expected leave-untracked items missing from untracked set",
            {
                "missing_leave_items": missing_leave_items,
                "git_state": git_state,
            },
        )

    try:
        hygiene = load_json(UNTRACKED_HYGIENE_JSON)
        old_short = load_json(OLD_SHORT_LOCK_JSON)
        policy = load_json(POLICY_JSON)
    except Exception as exc:
        return fail_closed(
            "could not load required closure JSON inputs",
            {
                "error": repr(exc),
                "git_state": git_state,
            },
        )

    if hygiene.get("plan_status") != "UNTRACKED_HYGIENE_AND_UNIVERSE_GUARD_REVIEW_PLAN_V1_RECORDED_NO_ACTION":
        return fail_closed(
            "untracked hygiene plan status unexpected",
            {
                "plan_status": hygiene.get("plan_status"),
                "git_state": git_state,
            },
        )

    if old_short.get("lock_status") != "OLD_SHORT_GUARDED_APPLY_LOCK_REGISTRY_V1_LOCKED_DO_NOT_RUN_CONFIRMED":
        return fail_closed(
            "old_short lock status unexpected",
            {
                "lock_status": old_short.get("lock_status"),
                "git_state": git_state,
            },
        )

    counts = policy.get("counts") if isinstance(policy.get("counts"), dict) else {}
    if counts.get("p0_invalid_metadata_count") != 0:
        return fail_closed(
            "p0 invalid metadata count must be zero before commit plan",
            {
                "policy_counts": counts,
                "git_state": git_state,
            },
        )

    commit_candidate_records = [file_record(path) for path in sorted(COMMIT_CANDIDATE_TOOLS)]
    leave_records = [file_record(path) for path in sorted(LEAVE_UNTRACKED_LOCKED_OR_REVIEW)]

    commit_record_errors: List[str] = []
    for rec in commit_candidate_records:
        if not rec["exists"]:
            commit_record_errors.append(f"commit candidate missing: {rec['path']}")
        if rec["path"].endswith(".py") and rec["syntax_ok"] is not True:
            commit_record_errors.append(f"commit candidate syntax failed: {rec['path']} error={rec['syntax_error']}")
        if rec["bom_detected"] is True:
            commit_record_errors.append(f"commit candidate has BOM: {rec['path']}")

    if commit_record_errors:
        return fail_closed(
            "commit candidate validation failed",
            {
                "commit_record_errors": commit_record_errors,
                "commit_candidate_records": commit_candidate_records,
                "git_state": git_state,
            },
        )

    leave_policy_records = [
        {
            "path": rec["path"],
            "decision": (
                "LEAVE_UNTRACKED_SUPERSEDED_PREVIEW_TOOL_NO_ACTION"
                if rec["path"] in {
                    "tools/edge_factory_os_gate_metadata_patch_preview_v2.py",
                    "tools/edge_factory_os_gate_metadata_patch_preview_v3.py",
                }
                else "LEAVE_UNTRACKED_BACKUP_PENDING_EXPLICIT_CLEANUP_APPROVAL"
                if ".bak_" in rec["path"] or "readonly_fix_bak" in rec["path"] or "blocked_patch_bak" in rec["path"]
                else "LEAVE_UNTRACKED_LOCKED_DO_NOT_RUN"
                if rec["path"] == "tools/edge_factory_os_old_short_guarded_runtime_reenable_apply_v1.py"
                else "LEAVE_UNTRACKED_UNIVERSE_GUARD_PENDING_EXPLICIT_STAGE_OR_DISCARD_APPROVAL"
            ),
            "stage_allowed_now": False,
            "delete_allowed_now": False,
            "move_allowed_now": False,
            "gitignore_allowed_now": False,
            "record": rec,
        }
        for rec in leave_records
    ]

    plan_records = {
        "commit_candidate_tools": sorted(COMMIT_CANDIDATE_TOOLS),
        "leave_untracked_locked_or_review": sorted(LEAVE_UNTRACKED_LOCKED_OR_REVIEW),
        "commit_candidate_records": commit_candidate_records,
        "leave_policy_records": leave_policy_records,
        "recommended_commit_message": "Record stabilization freeze and recurrence guard tooling",
        "stage_command_policy": {
            "git_add_force_allowed": False,
            "stage_only_exact_paths": sorted(COMMIT_CANDIDATE_TOOLS),
            "forbidden_stage_paths": sorted(LEAVE_UNTRACKED_LOCKED_OR_REVIEW),
        },
    }

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "plan_status": "UNTRACKED_STABILIZATION_TOOLING_COMMIT_PLAN_V1_READY_NO_STAGE",
        "severity": "ATTENTION",
        "allowed_scope": "READ_ONLY_UNTRACKED_TOOLING_COMMIT_PLAN",
        "final_decision": "REVIEW_THEN_APPROVE_COMMIT_OF_STABILIZATION_TOOLING_ONLY",
        "next_action": "BUILD_STABILIZATION_TOOLING_COMMIT_APPROVAL_V1_NO_FORCE_ADD",
        "next_module": "edge_factory_os_stabilization_tooling_commit_approval_v1.py",
        "reason": "stabilization tooling can be committed as exact-path set; locked/review/backups remain untracked",
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "counts": {
            "commit_candidate_tool_count": len(COMMIT_CANDIDATE_TOOLS),
            "leave_untracked_count": len(LEAVE_UNTRACKED_LOCKED_OR_REVIEW),
            "unknown_untracked_count": len(unknown_untracked),
            "commit_record_error_count": len(commit_record_errors),
            "direct_apply_recommended_now_count": 0,
            "apply_recommended_now_count": 0,
            "stage_recommended_now_count": 0,
            "commit_recommended_now_count": 0,
        },
        "plan_records": plan_records,
        "source_jsons": {
            "untracked_hygiene": str(UNTRACKED_HYGIENE_JSON),
            "old_short_lock": str(OLD_SHORT_LOCK_JSON),
            "policy": str(POLICY_JSON),
        },
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

    latest_json = OUT_DIR / "untracked_stabilization_tooling_commit_plan_v1_latest.json"
    timestamped_json = OUT_DIR / f"untracked_stabilization_tooling_commit_plan_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "untracked_stabilization_tooling_commit_plan_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    txt_lines = [
        "EDGE FACTORY OS UNTRACKED STABILIZATION TOOLING COMMIT PLAN v1",
        "=" * 100,
        f"plan_status: {payload['plan_status']}",
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
        "COMMIT CANDIDATE TOOLS",
        "-" * 100,
        json.dumps(sorted(COMMIT_CANDIDATE_TOOLS), indent=2, sort_keys=True),
        "",
        "LEAVE UNTRACKED LOCKED OR REVIEW",
        "-" * 100,
        json.dumps(sorted(LEAVE_UNTRACKED_LOCKED_OR_REVIEW), indent=2, sort_keys=True),
        "",
        "LEAVE POLICY RECORDS",
        "-" * 100,
        json.dumps(leave_policy_records, indent=2, sort_keys=True),
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