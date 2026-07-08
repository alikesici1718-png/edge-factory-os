from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_attention_issue_policy_classifier_after_gate_metadata_v4"
OUT_DIR = LAB_ROOT / "edge_factory_os_attention_issue_policy_classifier_after_gate_metadata_v4"
OUT_DIR.mkdir(parents=True, exist_ok=True)

REFRESH_JSON = (
    LAB_ROOT
    / "edge_factory_os_attention_triage_classifier_gate_review_refresh_after_metadata_v4"
    / "attention_triage_classifier_gate_review_refresh_after_metadata_v4_latest.json"
)

POST_COMMIT_JSON = (
    LAB_ROOT
    / "edge_factory_os_post_commit_read_only_status_after_gate_metadata_v4"
    / "post_commit_read_only_status_after_gate_metadata_v4_latest.json"
)

EXPECTED_HEAD_PREFIX = "578879b"

SAFETY_FLAGS: Dict[str, bool] = {
    "read_only_policy_classifier": True,
    "apply_performed_now": False,
    "commit_performed_now": False,
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
    "old_short_guarded_apply_allowed": False,
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
    "direct_apply",
    "old_short_guarded_apply_execution",
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


def fail_closed(reason: str, extra: Optional[Dict[str, Any]] = None) -> int:
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "classifier_status": "ATTENTION_ISSUE_POLICY_CLASSIFIER_AFTER_METADATA_V4_FAIL_CLOSED",
        "severity": "BLOCKED",
        "allowed_scope": "READ_ONLY_POLICY_CLASSIFICATION",
        "final_decision": "STOP_NO_APPLY",
        "next_action": "REVIEW_INPUT_STATUS_BEFORE_CONTINUING",
        "next_module": None,
        "reason": reason,
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "refresh_json": str(REFRESH_JSON),
        "post_commit_json": str(POST_COMMIT_JSON),
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
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

    out = OUT_DIR / "attention_issue_policy_classifier_after_metadata_v4_fail_closed_latest.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS ATTENTION ISSUE POLICY CLASSIFIER AFTER METADATA v4")
    print("=" * 100)
    print("classifier_status: ATTENTION_ISSUE_POLICY_CLASSIFIER_AFTER_METADATA_V4_FAIL_CLOSED")
    print(f"reason: {reason}")
    print(f"output: {out}")
    return 2


def classify_priority(row: Dict[str, Any]) -> Dict[str, Any]:
    path = str(row.get("path", ""))
    classification = str(row.get("classification", "UNKNOWN"))
    risk = str(row.get("risk", "UNKNOWN"))
    signals = row.get("risk_signals") if isinstance(row.get("risk_signals"), dict) else {}

    mutation_hits = signals.get("mutation_hits") if isinstance(signals.get("mutation_hits"), list) else []
    sensitive_hits = signals.get("sensitive_hits") if isinstance(signals.get("sensitive_hits"), list) else []
    read_only_hits = signals.get("read_only_hits") if isinstance(signals.get("read_only_hits"), list) else []

    if classification == "GATE_REVIEW_ATTENTION_METADATA_PRESENT_BUT_INVALID":
        policy_bucket = "P0_INVALID_EXISTING_METADATA_BLOCK"
        recommended_disposition = "INSPECT_METADATA_BLOCK_READ_ONLY_FIRST"
        priority_score = 100
        preview_fix_candidate_now = False

    elif classification == "UNTRACKED_MANUAL_REQUIRED_OLD_SHORT_GUARDED_APPLY_DO_NOT_RUN":
        policy_bucket = "P0_UNTRACKED_OLD_SHORT_GUARDED_APPLY_LOCKED"
        recommended_disposition = "DO_NOT_RUN_KEEP_MANUAL_REVIEW_ONLY"
        priority_score = 95
        preview_fix_candidate_now = False

    elif classification == "UNTRACKED_KNOWN_BACKUP_HYGIENE_NO_DELETE_MOVE":
        policy_bucket = "P1_BACKUP_HYGIENE_PENDING_NO_DELETE_MOVE_WITHOUT_APPROVAL"
        recommended_disposition = "RECORD_PENDING_HYGIENE_ONLY"
        priority_score = 80
        preview_fix_candidate_now = False

    elif classification == "UNTRACKED_REVIEW_REQUIRED_UNIVERSE_GUARD_NO_ACTION":
        policy_bucket = "P1_UNIVERSE_GUARD_REVIEW_REQUIRED_NO_ACTION"
        recommended_disposition = "REVIEW_SOURCE_AND_POLICY_BEFORE_STAGE_OR_DELETE"
        priority_score = 75
        preview_fix_candidate_now = False

    elif classification == "GATE_REVIEW_MANUAL_REQUIRED_MUTATION_SURFACE_NO_READ_ONLY_GATE":
        policy_bucket = "P2_MUTATION_SURFACE_NO_READ_ONLY_GATE_BROAD_REVIEW"
        recommended_disposition = "DO_NOT_PATCH_ALL_SAMPLE_AND_POLICY_REVIEW"
        priority_score = 60
        preview_fix_candidate_now = False

    elif classification == "GATE_REVIEW_ATTENTION_MUTATION_SURFACE_READ_ONLY_MARKERS_NO_METADATA":
        policy_bucket = "P3_MUTATION_SURFACE_READ_ONLY_MARKERS_NO_METADATA_BROAD_REVIEW"
        recommended_disposition = "NO_MASS_METADATA_PATCH_REQUIRE_TARGETED_CONTRACT"
        priority_score = 50
        preview_fix_candidate_now = False

    elif classification == "GATE_REVIEW_ATTENTION_RISKY_FILENAME_OR_SENSITIVE_TERMS_NO_METADATA":
        policy_bucket = "P4_RISKY_NAME_NO_METADATA_LOW_COUNT_REVIEW"
        recommended_disposition = "REVIEW_AFTER_P0_P1"
        priority_score = 40
        preview_fix_candidate_now = False

    elif classification.startswith("UNTRACKED_"):
        policy_bucket = "P5_UNTRACKED_INFO_OR_ATTENTION"
        recommended_disposition = "NO_ACTION_NOW"
        priority_score = 20 if risk == "ATTENTION" else 5
        preview_fix_candidate_now = False

    else:
        policy_bucket = "P9_NO_ACTION"
        recommended_disposition = "NO_ACTION_NOW"
        priority_score = 0
        preview_fix_candidate_now = False

    return {
        "path": path,
        "classification": classification,
        "risk": risk,
        "policy_bucket": policy_bucket,
        "recommended_disposition": recommended_disposition,
        "priority_score": priority_score,
        "preview_fix_candidate_now": preview_fix_candidate_now,
        "apply_recommended_now": False,
        "direct_apply_recommended_now": False,
        "mutation_hits": mutation_hits,
        "sensitive_hits": sensitive_hits,
        "read_only_hits": read_only_hits,
    }


def count_by_key(rows: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for row in rows:
        value = str(row.get(key, "UNKNOWN"))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


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
            "tracked files dirty; refusing policy classification continuation",
            {
                "git_state": git_state,
            },
        )

    try:
        refresh = load_json(REFRESH_JSON)
        post_commit = load_json(POST_COMMIT_JSON)
    except Exception as exc:
        return fail_closed(
            "could not load required input json",
            {
                "error": repr(exc),
                "git_state": git_state,
            },
        )

    if post_commit.get("status") != "POST_COMMIT_READ_ONLY_STATUS_AFTER_GATE_METADATA_V4_PASS":
        return fail_closed(
            "post-commit status is not PASS",
            {
                "post_commit_status": post_commit.get("status"),
                "git_state": git_state,
            },
        )

    if refresh.get("refresh_status") != "ATTENTION_TRIAGE_CLASSIFIER_GATE_REVIEW_REFRESH_AFTER_METADATA_V4_READY_NO_APPLY":
        return fail_closed(
            "triage/classifier refresh is not READY_NO_APPLY",
            {
                "refresh_status": refresh.get("refresh_status"),
                "git_state": git_state,
            },
        )

    if refresh.get("direct_apply_recommended_now") is not False:
        return fail_closed(
            "refresh direct_apply_recommended_now must be false",
            {
                "direct_apply_recommended_now": refresh.get("direct_apply_recommended_now"),
                "git_state": git_state,
            },
        )

    if refresh.get("critical_issue_count") != 0:
        return fail_closed(
            "refresh critical_issue_count must be 0",
            {
                "critical_issue_count": refresh.get("critical_issue_count"),
                "git_state": git_state,
            },
        )

    tracked_candidates = refresh.get("tracked_candidates")
    untracked_classifications = refresh.get("untracked_classifications")

    if not isinstance(tracked_candidates, list):
        return fail_closed("tracked_candidates missing or not list", {"git_state": git_state})

    if not isinstance(untracked_classifications, list):
        return fail_closed("untracked_classifications missing or not list", {"git_state": git_state})

    policy_rows = [classify_priority(row) for row in tracked_candidates + untracked_classifications]
    policy_rows_sorted = sorted(
        policy_rows,
        key=lambda row: (-int(row.get("priority_score", 0)), str(row.get("path", ""))),
    )

    policy_bucket_counts = count_by_key(policy_rows, "policy_bucket")
    disposition_counts = count_by_key(policy_rows, "recommended_disposition")

    p0_invalid_metadata = [
        row for row in policy_rows_sorted
        if row["policy_bucket"] == "P0_INVALID_EXISTING_METADATA_BLOCK"
    ]

    p0_old_short_locked = [
        row for row in policy_rows_sorted
        if row["policy_bucket"] == "P0_UNTRACKED_OLD_SHORT_GUARDED_APPLY_LOCKED"
    ]

    p1_hygiene = [
        row for row in policy_rows_sorted
        if row["policy_bucket"] == "P1_BACKUP_HYGIENE_PENDING_NO_DELETE_MOVE_WITHOUT_APPROVAL"
    ]

    p1_universe_guard = [
        row for row in policy_rows_sorted
        if row["policy_bucket"] == "P1_UNIVERSE_GUARD_REVIEW_REQUIRED_NO_ACTION"
    ]

    broad_mutation_review = [
        row for row in policy_rows_sorted
        if row["policy_bucket"] in {
            "P2_MUTATION_SURFACE_NO_READ_ONLY_GATE_BROAD_REVIEW",
            "P3_MUTATION_SURFACE_READ_ONLY_MARKERS_NO_METADATA_BROAD_REVIEW",
        }
    ]

    if p0_invalid_metadata:
        next_action = "BUILD_INVALID_EXISTING_METADATA_BLOCK_INSPECTOR_V1_READ_ONLY"
        next_module = "edge_factory_os_invalid_existing_metadata_block_inspector_v1.py"
        final_decision = "INSPECT_4_INVALID_METADATA_BLOCKS_BEFORE_ANY_NEW_PREVIEW"
        reason = f"P0 invalid existing metadata blocks found: {len(p0_invalid_metadata)}"
    elif p0_old_short_locked:
        next_action = "KEEP_OLD_SHORT_GUARDED_APPLY_LOCKED_MANUAL_REVIEW_ONLY"
        next_module = None
        final_decision = "NO_APPLY_REVIEW_OLD_SHORT_LOCKED_UNTRACKED"
        reason = "old_short guarded apply remains untracked and locked"
    elif p1_hygiene or p1_universe_guard:
        next_action = "BUILD_REPO_HYGIENE_AND_UNIVERSE_GUARD_REVIEW_PLAN_NO_DELETE_MOVE"
        next_module = "edge_factory_os_repo_hygiene_untracked_review_plan_v1.py"
        final_decision = "PLAN_ONLY_FOR_UNTRACKED_ATTENTION_NO_DELETE_MOVE"
        reason = f"P1 hygiene={len(p1_hygiene)} universe_guard={len(p1_universe_guard)}"
    else:
        next_action = "REVIEW_BROAD_MUTATION_SURFACE_POLICY_NO_FIX_ALL"
        next_module = "edge_factory_os_broad_mutation_surface_policy_sampler_v1.py"
        final_decision = "NO_MASS_PATCH_SAMPLE_BROAD_MUTATION_SURFACES"
        reason = f"broad mutation review remains: {len(broad_mutation_review)}"

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "classifier_status": "ATTENTION_ISSUE_POLICY_CLASSIFIER_AFTER_METADATA_V4_READY",
        "severity": "ATTENTION",
        "allowed_scope": "READ_ONLY_POLICY_CLASSIFICATION",
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "reason": reason,
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "source_refresh_json": str(REFRESH_JSON),
        "source_post_commit_json": str(POST_COMMIT_JSON),
        "latest_commit": git_state["head"],
        "counts": {
            "policy_row_count": len(policy_rows),
            "tracked_candidate_count": len(tracked_candidates),
            "untracked_classification_count": len(untracked_classifications),
            "p0_invalid_metadata_count": len(p0_invalid_metadata),
            "p0_old_short_locked_count": len(p0_old_short_locked),
            "p1_backup_hygiene_count": len(p1_hygiene),
            "p1_universe_guard_count": len(p1_universe_guard),
            "broad_mutation_review_count": len(broad_mutation_review),
            "direct_apply_recommended_now_count": 0,
            "apply_recommended_now_count": 0,
            "preview_fix_candidate_now_count": 0,
        },
        "policy_bucket_counts": policy_bucket_counts,
        "disposition_counts": disposition_counts,
        "p0_invalid_metadata": p0_invalid_metadata,
        "p0_old_short_locked": p0_old_short_locked,
        "p1_backup_hygiene": p1_hygiene,
        "p1_universe_guard": p1_universe_guard,
        "broad_mutation_review_preview_sample": broad_mutation_review[:25],
        "top_policy_rows": policy_rows_sorted[:60],
        "direct_apply_recommended_now": False,
        "apply_recommended_now": False,
        "preview_fix_candidate_now": False,
        "candidate_generation_recommended_now": False,
        "family_release_recommended_now": False,
        "runtime_action_recommended_now": False,
        "capital_action_recommended_now": False,
        "holdout_action_recommended_now": False,
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

    latest_json = OUT_DIR / "attention_issue_policy_classifier_after_metadata_v4_latest.json"
    timestamped_json = OUT_DIR / f"attention_issue_policy_classifier_after_metadata_v4_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "attention_issue_policy_classifier_after_metadata_v4_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    txt_lines = [
        "EDGE FACTORY OS ATTENTION ISSUE POLICY CLASSIFIER AFTER METADATA v4",
        "=" * 100,
        f"classifier_status: {payload['classifier_status']}",
        f"severity: {payload['severity']}",
        f"allowed_scope: {payload['allowed_scope']}",
        f"final_decision: {payload['final_decision']}",
        f"next_action: {payload['next_action']}",
        f"next_module: {payload['next_module']}",
        f"reason: {payload['reason']}",
        f"latest_commit: {payload['latest_commit']}",
        "",
        "COUNTS",
        "-" * 100,
        json.dumps(payload["counts"], indent=2, sort_keys=True),
        "",
        "POLICY BUCKET COUNTS",
        "-" * 100,
        json.dumps(policy_bucket_counts, indent=2, sort_keys=True),
        "",
        "DISPOSITION COUNTS",
        "-" * 100,
        json.dumps(disposition_counts, indent=2, sort_keys=True),
        "",
        "P0 INVALID METADATA",
        "-" * 100,
        json.dumps(p0_invalid_metadata, indent=2, sort_keys=True),
        "",
        "P0 OLD SHORT LOCKED",
        "-" * 100,
        json.dumps(p0_old_short_locked, indent=2, sort_keys=True),
        "",
        "P1 BACKUP HYGIENE",
        "-" * 100,
        json.dumps(p1_hygiene, indent=2, sort_keys=True),
        "",
        "P1 UNIVERSE GUARD",
        "-" * 100,
        json.dumps(p1_universe_guard, indent=2, sort_keys=True),
        "",
        "BROAD MUTATION REVIEW SAMPLE",
        "-" * 100,
        json.dumps(broad_mutation_review[:25], indent=2, sort_keys=True),
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