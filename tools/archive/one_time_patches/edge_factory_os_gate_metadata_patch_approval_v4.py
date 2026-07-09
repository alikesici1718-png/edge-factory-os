from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_gate_metadata_patch_approval_v4"
OUT_DIR = LAB_ROOT / "edge_factory_os_gate_metadata_patch_approval_v4"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PREVIEW_JSON = LAB_ROOT / "edge_factory_os_gate_metadata_patch_preview_v4" / "gate_metadata_patch_preview_v4_latest.json"
PREVIEW_DIFF = LAB_ROOT / "edge_factory_os_gate_metadata_patch_preview_v4" / "gate_metadata_patch_preview_v4_latest.diff"

EXPECTED_HEAD_PREFIX = "f62e5bd"
EXPECTED_GATE_REVIEW_CANDIDATE_COUNT = 25
EXPECTED_PREVIEW_FIX_CANDIDATE_COUNT = 11

EXPECTED_TARGETS: Set[str] = {
    "tools/edge_factory_os_month_stability_repair_diagnostic_v1.py",
    "tools/edge_factory_os_repo_cleanup_plan_v1.py",
    "src/edge_factory_claude_critical_patch_v1.py",
    "src/edge_factory_master_gate_compatibility_repair_v1.py",
    "src/edge_factory_master_gate_compatibility_repair_v2.py",
    "src/edge_factory_master_launcher_gate_repair_v3.py",
    "src/edge_factory_master_upper_system_boot_repair_v1.py",
    "src/edge_factory_patch_launcher_remove_blocking_risk_line_v1.py",
    "src/edge_factory_patch_master_launcher_risk_args_v1.py",
    "src/edge_factory_risk_manager_v4_wrapper_patch_v2.py",
    "src/edge_factory_signal_id_fallback_line_patch_v2.py",
}

SAFETY_FLAGS: Dict[str, bool] = {
    "approval_only": True,
    "apply_performed_now": False,
    "direct_apply_allowed": False,
    "comment_only_apply_next_step_allowed": True,
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
    dirty_tracked = [line for line in status_lines if not line.startswith("?? ")]

    return {
        "head": head.stdout.strip(),
        "branch": branch.stdout.strip(),
        "status_porcelain": status_lines,
        "remote_status_short": remote.stdout.splitlines(),
        "git_dirty": bool(status_lines),
        "dirty_tracked_count": len(dirty_tracked),
        "untracked_count": len(untracked),
        "untracked_paths": untracked,
    }


def is_tracked_file(rel_path: str) -> bool:
    result = run_cmd(["git", "ls-files", "--error-unmatch", rel_path])
    return result.returncode == 0


def fail_closed(reason: str, extra: Optional[Dict[str, Any]] = None) -> int:
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "approval_status": "GATE_METADATA_PATCH_APPROVAL_V4_FAIL_CLOSED",
        "severity": "BLOCKED",
        "allowed_scope": "READ_ONLY_REPO_APPROVAL_ONLY",
        "final_decision": "STOP_NO_APPLY",
        "next_action": "REVIEW_APPROVAL_FAILURE_BEFORE_APPLY",
        "reason": reason,
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "preview_json": str(PREVIEW_JSON),
        "preview_diff": str(PREVIEW_DIFF),
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "apply_performed_now": False,
        "comment_only_apply_next_step_allowed": False,
    }
    if extra:
        payload.update(extra)

    out = OUT_DIR / "gate_metadata_patch_approval_v4_fail_closed_latest.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS GATE METADATA PATCH APPROVAL v4")
    print("=" * 100)
    print("approval_status: GATE_METADATA_PATCH_APPROVAL_V4_FAIL_CLOSED")
    print(f"reason: {reason}")
    print(f"output: {out}")
    return 2


def assert_safety_shape() -> Optional[str]:
    for key, value in SAFETY_FLAGS.items():
        if not isinstance(value, bool):
            return f"safety_flags[{key}] is not boolean"
    if not isinstance(FORBIDDEN_ACTIONS, list) or not all(isinstance(x, str) for x in FORBIDDEN_ACTIONS):
        return "forbidden_actions must be list[str]"
    return None


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def validate_rel_path(path: Any) -> Optional[str]:
    if not isinstance(path, str):
        return None

    rel = path.strip().replace("\\", "/")
    if not rel:
        return None
    if rel.startswith("/") or ":" in rel:
        return None
    if ".." in Path(rel).parts:
        return None
    if not (rel.startswith("tools/") or rel.startswith("src/")):
        return None
    if not rel.endswith(".py"):
        return None
    if ".bak" in rel or "readonly_fix_bak" in rel or "blocked_patch_bak" in rel:
        return None
    if rel == "tools/edge_factory_os_old_short_guarded_runtime_reenable_apply_v1.py":
        return None
    return rel


def validate_diff_is_comment_only(diff_text: str) -> Dict[str, Any]:
    diff_targets: Set[str] = set()
    added_non_comment_lines: List[str] = []
    missing_metadata_markers: List[str] = []

    current_target: Optional[str] = None
    target_added_lines: Dict[str, List[str]] = {}

    for raw_line in diff_text.splitlines():
        if raw_line.startswith("+++ b/"):
            candidate = validate_rel_path(raw_line[len("+++ b/"):])
            if candidate:
                current_target = candidate
                diff_targets.add(candidate)
                target_added_lines.setdefault(candidate, [])
            else:
                added_non_comment_lines.append(f"invalid diff target line: {raw_line}")
                current_target = None
            continue

        if raw_line.startswith("+") and not raw_line.startswith("+++"):
            added = raw_line[1:]
            if added != "" and not added.startswith("#"):
                added_non_comment_lines.append(raw_line)
            if current_target is not None:
                target_added_lines.setdefault(current_target, []).append(added)

    for target, added_lines in target_added_lines.items():
        joined = "\n".join(added_lines)
        if "EDGE_FACTORY_GATE_METADATA_START" not in joined or "EDGE_FACTORY_GATE_METADATA_END" not in joined:
            missing_metadata_markers.append(target)

    return {
        "diff_targets": sorted(diff_targets),
        "added_non_comment_lines": added_non_comment_lines,
        "missing_metadata_markers": missing_metadata_markers,
        "target_added_line_counts": {k: len(v) for k, v in sorted(target_added_lines.items())},
    }


def main() -> int:
    safety_error = assert_safety_shape()
    if safety_error:
        return fail_closed(safety_error)

    git_state = get_git_state()

    if not git_state["head"].startswith(EXPECTED_HEAD_PREFIX):
        return fail_closed(
            "unexpected git HEAD; refusing approval against unknown repo state",
            {
                "expected_head_prefix": EXPECTED_HEAD_PREFIX,
                "git_state": git_state,
            },
        )

    if git_state["dirty_tracked_count"] != 0:
        return fail_closed(
            "tracked files are dirty before approval; refusing to approve apply chain",
            {
                "git_state": git_state,
            },
        )

    try:
        preview = load_json(PREVIEW_JSON)
    except Exception as exc:
        return fail_closed(
            "could not read v4 preview json",
            {
                "error": repr(exc),
                "git_state": git_state,
            },
        )

    if not PREVIEW_DIFF.exists():
        return fail_closed(
            "v4 preview diff is missing",
            {
                "preview_diff": str(PREVIEW_DIFF),
                "git_state": git_state,
            },
        )

    diff_text = PREVIEW_DIFF.read_text(encoding="utf-8")

    required_preview_checks = {
        "preview_status": preview.get("preview_status"),
        "allowed_scope": preview.get("allowed_scope"),
        "final_decision": preview.get("final_decision"),
        "next_module": preview.get("next_module"),
        "direct_apply_recommended_now": preview.get("direct_apply_recommended_now"),
        "apply_allowed_now": preview.get("apply_allowed_now"),
        "preview_ready_count": preview.get("preview_ready_count"),
        "already_present_count": preview.get("already_present_count"),
        "blocked_statuses": preview.get("blocked_statuses"),
        "normalized_preview_fix_candidate_count": preview.get("normalized_preview_fix_candidate_count"),
    }

    if preview.get("preview_status") != "GATE_METADATA_PATCH_PREVIEW_V4_READY_NO_APPLY":
        return fail_closed("v4 preview status is not ready", {"preview_checks": required_preview_checks, "git_state": git_state})

    if preview.get("allowed_scope") != "READ_ONLY_REPO_PREVIEW_ONLY":
        return fail_closed("v4 preview allowed_scope mismatch", {"preview_checks": required_preview_checks, "git_state": git_state})

    if preview.get("next_module") != "edge_factory_os_gate_metadata_patch_approval_v4.py":
        return fail_closed("v4 preview next_module mismatch", {"preview_checks": required_preview_checks, "git_state": git_state})

    if preview.get("direct_apply_recommended_now") is not False:
        return fail_closed("v4 preview direct_apply_recommended_now must be false", {"preview_checks": required_preview_checks, "git_state": git_state})

    if preview.get("apply_allowed_now") is not False:
        return fail_closed("v4 preview apply_allowed_now must be false", {"preview_checks": required_preview_checks, "git_state": git_state})

    if preview.get("preview_ready_count") != EXPECTED_PREVIEW_FIX_CANDIDATE_COUNT:
        return fail_closed("v4 preview_ready_count mismatch", {"preview_checks": required_preview_checks, "git_state": git_state})

    if preview.get("already_present_count") != 0:
        return fail_closed("v4 already_present_count must be 0", {"preview_checks": required_preview_checks, "git_state": git_state})

    if preview.get("blocked_statuses") != []:
        return fail_closed("v4 blocked_statuses must be empty", {"preview_checks": required_preview_checks, "git_state": git_state})

    counts = preview.get("counts") if isinstance(preview.get("counts"), dict) else {}
    if counts.get("gate_review_candidate_count") != EXPECTED_GATE_REVIEW_CANDIDATE_COUNT:
        return fail_closed("gate_review_candidate_count mismatch in v4 preview", {"counts": counts, "git_state": git_state})

    if counts.get("preview_fix_candidate_count") != EXPECTED_PREVIEW_FIX_CANDIDATE_COUNT:
        return fail_closed("preview_fix_candidate_count mismatch in v4 preview", {"counts": counts, "git_state": git_state})

    status_counts = preview.get("status_counts") if isinstance(preview.get("status_counts"), dict) else {}
    if status_counts != {"PREVIEW_READY_NON_BEHAVIORAL_COMMENT_ONLY": EXPECTED_PREVIEW_FIX_CANDIDATE_COUNT}:
        return fail_closed("v4 status_counts are not exactly clean", {"status_counts": status_counts, "git_state": git_state})

    preview_safety = preview.get("safety_flags") if isinstance(preview.get("safety_flags"), dict) else {}
    required_false_preview_flags = [
        "apply_allowed",
        "runtime_touch_allowed",
        "launcher_allowed",
        "capital_change_allowed",
        "active_paper_allowed",
        "live_allowed",
        "real_orders_allowed",
        "candidate_generation_allowed",
        "candidate_release_allowed",
        "family_release_allowed",
        "strategy_research_allowed",
        "holdout_access_allowed",
        "gitignore_change_allowed",
        "backup_delete_allowed",
        "backup_move_allowed",
        "git_add_force_allowed",
    ]
    flag_failures = [
        key for key in required_false_preview_flags
        if preview_safety.get(key) is not False
    ]
    if preview_safety.get("preview_only") is not True or flag_failures:
        return fail_closed(
            "v4 preview safety flags are not acceptable",
            {
                "preview_safety_flags": preview_safety,
                "flag_failures": flag_failures,
                "git_state": git_state,
            },
        )

    previews = preview.get("previews")
    if not isinstance(previews, list) or len(previews) != EXPECTED_PREVIEW_FIX_CANDIDATE_COUNT:
        return fail_closed(
            "v4 preview list missing or wrong length",
            {
                "preview_list_type": type(previews).__name__,
                "preview_list_length": len(previews) if isinstance(previews, list) else None,
                "git_state": git_state,
            },
        )

    preview_targets: Set[str] = set()
    bad_preview_items: List[Dict[str, Any]] = []

    for item in previews:
        if not isinstance(item, dict):
            bad_preview_items.append({"reason": "preview item is not dict", "item": repr(item)[:500]})
            continue

        if item.get("status") != "PREVIEW_READY_NON_BEHAVIORAL_COMMENT_ONLY":
            bad_preview_items.append({"reason": "preview item status not ready", "item": item})
            continue

        rel = validate_rel_path(item.get("target_path"))
        if rel is None:
            bad_preview_items.append({"reason": "invalid target_path", "item": item})
            continue

        if rel not in EXPECTED_TARGETS:
            bad_preview_items.append({"reason": "unexpected target_path", "target_path": rel})
            continue

        if not is_tracked_file(rel):
            bad_preview_items.append({"reason": "target not tracked", "target_path": rel})
            continue

        target = REPO_ROOT / rel
        if not target.exists():
            bad_preview_items.append({"reason": "target missing", "target_path": rel})
            continue

        text = target.read_text(encoding="utf-8")
        if text.startswith("\ufeff"):
            bad_preview_items.append({"reason": "target has BOM", "target_path": rel})
            continue

        if "EDGE_FACTORY_GATE_METADATA_START" in text:
            bad_preview_items.append({"reason": "target already has metadata block", "target_path": rel})
            continue

        item_diff = item.get("diff")
        if not isinstance(item_diff, str) or not item_diff.strip():
            bad_preview_items.append({"reason": "missing item diff", "target_path": rel})
            continue

        preview_targets.add(rel)

    if bad_preview_items:
        return fail_closed(
            "one or more v4 preview items failed approval checks",
            {
                "bad_preview_items": bad_preview_items,
                "git_state": git_state,
            },
        )

    if preview_targets != EXPECTED_TARGETS:
        return fail_closed(
            "v4 preview targets do not match expected 11-target set",
            {
                "expected_targets": sorted(EXPECTED_TARGETS),
                "actual_targets": sorted(preview_targets),
                "missing_targets": sorted(EXPECTED_TARGETS - preview_targets),
                "extra_targets": sorted(preview_targets - EXPECTED_TARGETS),
                "git_state": git_state,
            },
        )

    diff_validation = validate_diff_is_comment_only(diff_text)
    diff_targets = set(diff_validation["diff_targets"])

    if diff_validation["added_non_comment_lines"]:
        return fail_closed(
            "v4 diff contains added non-comment lines",
            {
                "diff_validation": diff_validation,
                "git_state": git_state,
            },
        )

    if diff_validation["missing_metadata_markers"]:
        return fail_closed(
            "v4 diff target is missing metadata markers",
            {
                "diff_validation": diff_validation,
                "git_state": git_state,
            },
        )

    if diff_targets != EXPECTED_TARGETS:
        return fail_closed(
            "v4 diff targets do not match expected targets",
            {
                "expected_targets": sorted(EXPECTED_TARGETS),
                "actual_diff_targets": sorted(diff_targets),
                "missing_targets": sorted(EXPECTED_TARGETS - diff_targets),
                "extra_targets": sorted(diff_targets - EXPECTED_TARGETS),
                "diff_validation": diff_validation,
                "git_state": git_state,
            },
        )

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "approval_status": "GATE_METADATA_PATCH_APPROVAL_V4_READY_COMMENT_ONLY_APPLY_ALLOWED",
        "severity": "ATTENTION",
        "allowed_scope": "REPO_ONLY_COMMENT_METADATA_APPROVAL",
        "final_decision": "BUILD_AND_RUN_GATE_METADATA_PATCH_APPLY_V4_COMMENT_ONLY",
        "next_action": "BUILD_GATE_METADATA_PATCH_APPLY_V4_COMMENT_ONLY_THEN_AUDIT_REFRESH",
        "next_module": "edge_factory_os_gate_metadata_patch_apply_v4.py",
        "reason": "v4 preview clean; 11/11 targets approved for non-behavioral comment-only metadata apply",
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "preview_json": str(PREVIEW_JSON),
        "preview_diff": str(PREVIEW_DIFF),
        "approved_target_count": len(preview_targets),
        "approved_targets": sorted(preview_targets),
        "expected_targets": sorted(EXPECTED_TARGETS),
        "counts": counts,
        "status_counts": status_counts,
        "diff_validation": diff_validation,
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "apply_performed_now": False,
        "comment_only_apply_next_step_allowed": True,
        "target_files_modified_now": [],
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

    latest_json = OUT_DIR / "gate_metadata_patch_approval_v4_latest.json"
    timestamped_json = OUT_DIR / f"gate_metadata_patch_approval_v4_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "gate_metadata_patch_approval_v4_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    txt_lines = [
        "EDGE FACTORY OS GATE METADATA PATCH APPROVAL v4",
        "=" * 100,
        f"approval_status: {payload['approval_status']}",
        f"severity: {payload['severity']}",
        f"allowed_scope: {payload['allowed_scope']}",
        f"final_decision: {payload['final_decision']}",
        f"next_action: {payload['next_action']}",
        f"next_module: {payload['next_module']}",
        f"reason: {payload['reason']}",
        "",
        "APPROVED TARGETS",
        "-" * 100,
        json.dumps(payload["approved_targets"], indent=2, sort_keys=True),
        "",
        "DIFF VALIDATION",
        "-" * 100,
        json.dumps(diff_validation, indent=2, sort_keys=True),
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