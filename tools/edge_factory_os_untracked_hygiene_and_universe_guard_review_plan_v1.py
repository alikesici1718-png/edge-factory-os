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

MODULE_NAME = "edge_factory_os_untracked_hygiene_and_universe_guard_review_plan_v1"
OUT_DIR = LAB_ROOT / "edge_factory_os_untracked_hygiene_and_universe_guard_review_plan_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HEAD_PREFIX = "578879b"

POLICY_JSON = (
    LAB_ROOT
    / "edge_factory_os_attention_issue_policy_classifier_after_gate_metadata_v4"
    / "attention_issue_policy_classifier_after_metadata_v4_latest.json"
)

OLD_SHORT_LOCK_JSON = (
    LAB_ROOT
    / "edge_factory_os_old_short_guarded_apply_lock_registry_v1"
    / "old_short_guarded_apply_lock_registry_v1_latest.json"
)

BACKUP_PATHS: Set[str] = {
    "tools/edge_factory_os_joint_null_distribution_validator_v1.py.readonly_fix_bak_20260514_022123",
    "tools/edge_factory_os_source_panel_anomaly_discovery_runner_v1.py.blocked_patch_bak_20260514_000647",
}

UNIVERSE_GUARD_PATH = "tools/edge_factory_os_universe_coverage_guard_v1.py"

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
    "tools/edge_factory_os_untracked_hygiene_and_universe_guard_review_plan_v1.py",
    "tools/edge_factory_os_universe_coverage_guard_v1.py",
}

SAFETY_FLAGS: Dict[str, bool] = {
    "stabilization_freeze_active": True,
    "read_only_review_plan": True,
    "backup_delete_allowed": False,
    "backup_move_allowed": False,
    "universe_guard_stage_allowed": False,
    "universe_guard_delete_allowed": False,
    "universe_guard_move_allowed": False,
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
    "git_add_force_allowed": False,
    "old_short_guarded_apply_allowed": False,
    "mass_metadata_patch_allowed": False,
}

FORBIDDEN_ACTIONS: List[str] = [
    "backup_delete",
    "backup_move",
    "universe_guard_stage",
    "universe_guard_delete",
    "universe_guard_move",
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


def sha256_file(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_summary(rel_path: str) -> Dict[str, Any]:
    path = REPO_ROOT / rel_path
    exists = path.exists()

    if not exists:
        return {
            "path": rel_path,
            "exists": False,
            "size_bytes": None,
            "sha256": None,
            "first_line": None,
            "line_count": None,
        }

    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    return {
        "path": rel_path,
        "exists": True,
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "first_line": lines[0][:240] if lines else "",
        "line_count": len(lines),
    }


def fail_closed(reason: str, extra: Optional[Dict[str, Any]] = None) -> int:
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "plan_status": "UNTRACKED_HYGIENE_AND_UNIVERSE_GUARD_REVIEW_PLAN_V1_FAIL_CLOSED",
        "severity": "BLOCKED",
        "allowed_scope": "READ_ONLY_UNTRACKED_REVIEW_PLAN",
        "final_decision": "STOP_NO_DELETE_NO_MOVE_NO_STAGE",
        "next_action": "REVIEW_PLAN_FAILURE",
        "next_module": None,
        "reason": reason,
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "policy_json": str(POLICY_JSON),
        "old_short_lock_json": str(OLD_SHORT_LOCK_JSON),
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
        "delete_or_move_recommended_now": False,
        "stage_recommended_now": False,
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

    out = OUT_DIR / "untracked_hygiene_and_universe_guard_review_plan_v1_fail_closed_latest.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS UNTRACKED HYGIENE + UNIVERSE GUARD REVIEW PLAN v1")
    print("=" * 100)
    print("plan_status: UNTRACKED_HYGIENE_AND_UNIVERSE_GUARD_REVIEW_PLAN_V1_FAIL_CLOSED")
    print(f"reason: {reason}")
    print(f"output: {out}")
    return 2


def classify_backup(path: str) -> Dict[str, Any]:
    summary = file_summary(path)
    return {
        **summary,
        "review_class": "BACKUP_HYGIENE_RECORD_ONLY",
        "decision": "KEEP_UNTRACKED_PENDING_EXPLICIT_CLEANUP_APPROVAL",
        "delete_allowed_now": False,
        "move_allowed_now": False,
        "stage_allowed_now": False,
        "gitignore_allowed_now": False,
        "required_future_chain": [
            "explicit user cleanup approval",
            "backup hash record",
            "preview delete/move plan",
            "approval",
            "apply",
            "audit refresh",
        ],
    }


def classify_universe_guard(path: str) -> Dict[str, Any]:
    summary = file_summary(path)

    text = ""
    if (REPO_ROOT / path).exists():
        text = (REPO_ROOT / path).read_text(encoding="utf-8", errors="replace").lower()

    signal_hits = [
        token for token in [
            "universe",
            "coverage",
            "guard",
            "full",
            "1y",
            "okx",
            "swap",
            "panel",
            "read_only",
            "promotion_allowed",
            "family_generation_allowed",
        ]
        if token in text
    ]

    return {
        **summary,
        "review_class": "UNIVERSE_GUARD_REVIEW_RECORD_ONLY",
        "decision": "KEEP_UNTRACKED_PENDING_SOURCE_REVIEW_AND_EXPLICIT_STAGE_OR_DISCARD_APPROVAL",
        "stage_allowed_now": False,
        "delete_allowed_now": False,
        "move_allowed_now": False,
        "gitignore_allowed_now": False,
        "signal_hits_for_awareness_only": signal_hits,
        "required_future_chain": [
            "read-only source review",
            "decide useful/superseded",
            "if useful: stage approval only, no git add -f",
            "if not useful: explicit delete/move approval required",
            "audit refresh",
        ],
    }


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
            "tracked files dirty; refusing untracked review plan",
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

    try:
        policy = load_json(POLICY_JSON)
        old_short = load_json(OLD_SHORT_LOCK_JSON)
    except Exception as exc:
        return fail_closed(
            "could not load policy/old_short lock json",
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
            "p0 invalid metadata must remain zero",
            {
                "counts": counts,
                "git_state": git_state,
            },
        )

    if old_short.get("lock_status") != "OLD_SHORT_GUARDED_APPLY_LOCK_REGISTRY_V1_LOCKED_DO_NOT_RUN_CONFIRMED":
        return fail_closed(
            "old_short lock registry not confirmed",
            {
                "old_short_lock_status": old_short.get("lock_status"),
                "git_state": git_state,
            },
        )

    untracked_set = set(git_state["untracked_paths"])

    missing_backup_paths = sorted(BACKUP_PATHS - untracked_set)
    if missing_backup_paths:
        return fail_closed(
            "expected backup files are not untracked/present in git status",
            {
                "missing_backup_paths": missing_backup_paths,
                "git_state": git_state,
            },
        )

    if UNIVERSE_GUARD_PATH not in untracked_set:
        return fail_closed(
            "universe guard path is not untracked/present in git status",
            {
                "universe_guard_path": UNIVERSE_GUARD_PATH,
                "git_state": git_state,
            },
        )

    backup_records = [classify_backup(path) for path in sorted(BACKUP_PATHS)]
    universe_guard_record = classify_universe_guard(UNIVERSE_GUARD_PATH)

    file_existence_errors: List[str] = []
    for rec in backup_records + [universe_guard_record]:
        if not rec["exists"]:
            file_existence_errors.append(f"missing file: {rec['path']}")

    if file_existence_errors:
        return fail_closed(
            "one or more expected untracked files missing",
            {
                "file_existence_errors": file_existence_errors,
                "backup_records": backup_records,
                "universe_guard_record": universe_guard_record,
                "git_state": git_state,
            },
        )

    p1_closure_records = [
        {
            "id": "P1_BACKUP_HYGIENE",
            "status": "CLOSED_AS_RECORDED_PENDING_EXPLICIT_CLEANUP_APPROVAL",
            "severity": "INFO",
            "evidence": {
                "backup_count": len(backup_records),
                "paths": sorted(BACKUP_PATHS),
                "hashes": {rec["path"]: rec["sha256"] for rec in backup_records},
            },
            "closed_for_stabilization": True,
            "remaining_future_action": "Optional cleanup only after explicit approval; no delete/move now.",
        },
        {
            "id": "P1_UNIVERSE_GUARD_REVIEW",
            "status": "CLOSED_AS_RECORDED_PENDING_EXPLICIT_STAGE_OR_DISCARD_APPROVAL",
            "severity": "INFO",
            "evidence": {
                "path": UNIVERSE_GUARD_PATH,
                "sha256": universe_guard_record["sha256"],
                "signal_hits": universe_guard_record["signal_hits_for_awareness_only"],
            },
            "closed_for_stabilization": True,
            "remaining_future_action": "Optional source review/stage/discard only through explicit approval; no action now.",
        },
    ]

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "plan_status": "UNTRACKED_HYGIENE_AND_UNIVERSE_GUARD_REVIEW_PLAN_V1_RECORDED_NO_ACTION",
        "severity": "ATTENTION",
        "allowed_scope": "READ_ONLY_UNTRACKED_REVIEW_PLAN",
        "final_decision": "CLOSE_P1_UNTRACKED_HYGIENE_FOR_STABILIZATION_NO_DELETE_MOVE_STAGE",
        "next_action": "BUILD_UNTRACKED_STABILIZATION_TOOLING_COMMIT_OR_DISCARD_PLAN_NO_FORCE_ADD",
        "next_module": "edge_factory_os_untracked_stabilization_tooling_commit_plan_v1.py",
        "reason": "backup files and universe guard recorded with hashes; no delete/move/stage/gitignore action allowed or performed",
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "policy_json": str(POLICY_JSON),
        "old_short_lock_json": str(OLD_SHORT_LOCK_JSON),
        "counts": {
            "backup_record_count": len(backup_records),
            "universe_guard_record_count": 1,
            "p1_closed_for_stabilization_count": len(p1_closure_records),
            "delete_or_move_recommended_now_count": 0,
            "stage_recommended_now_count": 0,
            "direct_apply_recommended_now_count": 0,
            "apply_recommended_now_count": 0,
        },
        "backup_records": backup_records,
        "universe_guard_record": universe_guard_record,
        "p1_closure_records": p1_closure_records,
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
        "delete_or_move_recommended_now": False,
        "stage_recommended_now": False,
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
        "universe_guard_modified": False,
        "gitignore_changed": False,
        "git_add_force_used": False,
        "git_state": git_state,
    }

    latest_json = OUT_DIR / "untracked_hygiene_and_universe_guard_review_plan_v1_latest.json"
    timestamped_json = OUT_DIR / f"untracked_hygiene_and_universe_guard_review_plan_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "untracked_hygiene_and_universe_guard_review_plan_v1_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    txt_lines = [
        "EDGE FACTORY OS UNTRACKED HYGIENE + UNIVERSE GUARD REVIEW PLAN v1",
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
        "BACKUP RECORDS",
        "-" * 100,
        json.dumps(backup_records, indent=2, sort_keys=True),
        "",
        "UNIVERSE GUARD RECORD",
        "-" * 100,
        json.dumps(universe_guard_record, indent=2, sort_keys=True),
        "",
        "P1 CLOSURE RECORDS",
        "-" * 100,
        json.dumps(p1_closure_records, indent=2, sort_keys=True),
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