from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_old_short_guarded_apply_lock_registry_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_old_short_guarded_apply_lock_registry_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "578879b"

POLICY_JSON = (
    LAB_ROOT
    / "edge_factory_os_attention_issue_policy_classifier_after_gate_metadata_v4"
    / "attention_issue_policy_classifier_after_metadata_v4_latest.json"
)

OLD_SHORT_REL = "tools/edge_factory_os_old_short_guarded_runtime_reenable_apply_v1.py"
OLD_SHORT_PATH = REPO_ROOT / OLD_SHORT_REL

KNOWN_ALLOWED_UNTRACKED: Set[str] = {
    "tools/edge_factory_os_attention_issue_policy_classifier_after_gate_metadata_v4.py",
    "tools/edge_factory_os_attention_triage_classifier_gate_review_refresh_after_metadata_v4.py",
    "tools/edge_factory_os_gate_metadata_patch_preview_v2.py",
    "tools/edge_factory_os_gate_metadata_patch_preview_v3.py",
    "tools/edge_factory_os_invalid_existing_metadata_block_inspector_v1.py",
    "tools/edge_factory_os_joint_null_distribution_validator_v1.py.readonly_fix_bak_20260514_022123",
    "tools/edge_factory_os_metadata_classifier_rule_refinement_apply_v1.py",
    "tools/edge_factory_os_metadata_classifier_rule_refinement_approval_v1.py",
    "tools/edge_factory_os_metadata_classifier_rule_refinement_preview_v1.py",
    "tools/edge_factory_os_old_short_guarded_apply_lock_registry_v1.py",
    "tools/edge_factory_os_old_short_guarded_runtime_reenable_apply_v1.py",
    "tools/edge_factory_os_post_commit_read_only_status_after_gate_metadata_v4.py",
    "tools/edge_factory_os_source_panel_anomaly_discovery_runner_v1.py.blocked_patch_bak_20260514_000647",
    "tools/edge_factory_os_stabilization_freeze_error_closure_controller_v1.py",
    "tools/edge_factory_os_universe_coverage_guard_v1.py",
}

SAFETY_FLAGS: Dict[str, bool] = {
    "stabilization_freeze_active": True,
    "read_only_lock_registry": True,
    "old_short_apply_file_executed": False,
    "old_short_guarded_apply_allowed": False,
    "apply_performed_now": False,
    "commit_performed_now": False,
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
    "mass_metadata_patch_allowed": False,
}

FORBIDDEN_ACTIONS: List[str] = [
    "old_short_guarded_apply_execution",
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
    "gitignore_change",
    "backup_delete",
    "backup_move",
    "git_add_force",
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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fail_closed(reason: str, extra: Optional[Dict[str, Any]] = None) -> int:
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "lock_status": "OLD_SHORT_GUARDED_APPLY_LOCK_REGISTRY_V1_FAIL_CLOSED",
        "severity": "BLOCKED",
        "allowed_scope": "READ_ONLY_LOCK_REGISTRY",
        "final_decision": "STOP_NO_EXECUTION_NO_APPLY",
        "next_action": "REVIEW_LOCK_REGISTRY_FAILURE",
        "next_module": None,
        "reason": reason,
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "old_short_rel": OLD_SHORT_REL,
        "policy_json": str(POLICY_JSON),
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
        "old_short_execution_recommended_now": False,
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

    out = OUT_DIR / "old_short_guarded_apply_lock_registry_v1_fail_closed_latest.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS OLD SHORT GUARDED APPLY LOCK REGISTRY v1")
    print("=" * 100)
    print("lock_status: OLD_SHORT_GUARDED_APPLY_LOCK_REGISTRY_V1_FAIL_CLOSED")
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
            "tracked files dirty; refusing lock registry",
            {
                "git_state": git_state,
            },
        )

    unknown_untracked = sorted(set(git_state["untracked_paths"]) - KNOWN_ALLOWED_UNTRACKED)
    if unknown_untracked:
        return fail_closed(
            "unknown untracked paths present",
            {
                "unknown_untracked": unknown_untracked,
                "git_state": git_state,
            },
        )

    if OLD_SHORT_REL not in set(git_state["untracked_paths"]):
        return fail_closed(
            "old_short guarded apply file is not untracked as expected",
            {
                "old_short_rel": OLD_SHORT_REL,
                "git_state": git_state,
            },
        )

    if not OLD_SHORT_PATH.exists():
        return fail_closed(
            "old_short guarded apply file missing",
            {
                "old_short_rel": OLD_SHORT_REL,
                "git_state": git_state,
            },
        )

    try:
        policy = load_json(POLICY_JSON)
    except Exception as exc:
        return fail_closed(
            "could not load policy classifier json",
            {
                "error": repr(exc),
                "git_state": git_state,
            },
        )

    if policy.get("classifier_status") != "ATTENTION_ISSUE_POLICY_CLASSIFIER_AFTER_METADATA_V4_READY":
        return fail_closed(
            "policy classifier status unexpected",
            {
                "classifier_status": policy.get("classifier_status"),
                "git_state": git_state,
            },
        )

    counts = policy.get("counts") if isinstance(policy.get("counts"), dict) else {}
    if counts.get("p0_invalid_metadata_count") != 0:
        return fail_closed(
            "p0 invalid metadata must remain zero before old_short lock",
            {
                "counts": counts,
                "git_state": git_state,
            },
        )

    if counts.get("p0_old_short_locked_count") != 1:
        return fail_closed(
            "expected exactly one old_short locked item",
            {
                "counts": counts,
                "git_state": git_state,
            },
        )

    p0_old_short = policy.get("p0_old_short_locked")
    if not isinstance(p0_old_short, list) or len(p0_old_short) != 1:
        return fail_closed(
            "p0_old_short_locked list missing or wrong length",
            {
                "p0_old_short_locked": p0_old_short,
                "git_state": git_state,
            },
        )

    old_short_row = p0_old_short[0]
    if old_short_row.get("path") != OLD_SHORT_REL:
        return fail_closed(
            "old_short locked path mismatch",
            {
                "old_short_row": old_short_row,
                "git_state": git_state,
            },
        )

    if old_short_row.get("recommended_disposition") != "DO_NOT_RUN_KEEP_MANUAL_REVIEW_ONLY":
        return fail_closed(
            "old_short disposition must be DO_NOT_RUN_KEEP_MANUAL_REVIEW_ONLY",
            {
                "old_short_row": old_short_row,
                "git_state": git_state,
            },
        )

    content = OLD_SHORT_PATH.read_text(encoding="utf-8", errors="replace")
    old_short_hash = sha256_file(OLD_SHORT_PATH)

    suspicious_execution_keywords = [
        "subprocess.run",
        "os.system",
        "launcher",
        "live",
        "real_order",
        "send_order",
        "place_order",
        "capital",
        "active_paper",
        "runtime",
    ]

    keyword_hits = [
        keyword for keyword in suspicious_execution_keywords
        if keyword.lower() in content.lower()
    ]

    lock_record = {
        "lock_id": "OLD_SHORT_GUARDED_APPLY_LOCKED_DO_NOT_RUN_20260514",
        "path": OLD_SHORT_REL,
        "sha256": old_short_hash,
        "file_exists": True,
        "git_state": "UNTRACKED",
        "policy_classifier_bucket": old_short_row.get("policy_bucket"),
        "policy_classifier_disposition": old_short_row.get("recommended_disposition"),
        "lock_decision": "LOCKED_DO_NOT_RUN",
        "execution_allowed": False,
        "stage_allowed_without_explicit_approval": False,
        "delete_allowed_without_explicit_approval": False,
        "move_allowed_without_explicit_approval": False,
        "gitignore_allowed_without_explicit_approval": False,
        "runtime_allowed": False,
        "launcher_allowed": False,
        "capital_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        "keyword_hits_for_awareness_only": keyword_hits,
        "note": "This registry intentionally does not execute, delete, move, stage, or modify the old_short guarded apply file.",
    }

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "lock_status": "OLD_SHORT_GUARDED_APPLY_LOCK_REGISTRY_V1_LOCKED_DO_NOT_RUN_CONFIRMED",
        "severity": "ATTENTION",
        "allowed_scope": "READ_ONLY_LOCK_REGISTRY",
        "final_decision": "TREAT_OLD_SHORT_GUARDED_APPLY_AS_LOCKED_NON_EXECUTABLE_UNTIL_EXPLICIT_APPROVAL",
        "next_action": "BUILD_UNTRACKED_HYGIENE_AND_UNIVERSE_GUARD_REVIEW_PLAN_NO_DELETE_MOVE",
        "next_module": "edge_factory_os_untracked_hygiene_and_universe_guard_review_plan_v1.py",
        "reason": "old_short guarded apply remains untracked and locked; no execution/stage/delete/move/gitignore action allowed",
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "policy_json": str(POLICY_JSON),
        "old_short_lock_record": lock_record,
        "counts": {
            "p0_invalid_metadata_count": counts.get("p0_invalid_metadata_count"),
            "p0_old_short_locked_count": counts.get("p0_old_short_locked_count"),
            "old_short_execution_allowed_count": 0,
            "direct_apply_recommended_now_count": 0,
            "apply_recommended_now_count": 0,
        },
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
        "old_short_execution_recommended_now": False,
        "candidate_generation_recommended_now": False,
        "family_release_recommended_now": False,
        "runtime_action_recommended_now": False,
        "capital_action_recommended_now": False,
        "holdout_action_recommended_now": False,
        "target_file_modified_now": False,
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

    latest_json = OUT_DIR / "old_short_guarded_apply_lock_registry_v1_latest.json"
    timestamped_json = OUT_DIR / f"old_short_guarded_apply_lock_registry_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "old_short_guarded_apply_lock_registry_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    txt_lines = [
        "EDGE FACTORY OS OLD SHORT GUARDED APPLY LOCK REGISTRY v1",
        "=" * 100,
        f"lock_status: {payload['lock_status']}",
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
        "OLD SHORT LOCK RECORD",
        "-" * 100,
        json.dumps(lock_record, indent=2, sort_keys=True),
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