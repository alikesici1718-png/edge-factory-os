from __future__ import annotations

import ast
import difflib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_gate_metadata_patch_apply_v4"
OUT_DIR = LAB_ROOT / "edge_factory_os_gate_metadata_patch_apply_v4"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PREVIEW_JSON = LAB_ROOT / "edge_factory_os_gate_metadata_patch_preview_v4" / "gate_metadata_patch_preview_v4_latest.json"
APPROVAL_JSON = LAB_ROOT / "edge_factory_os_gate_metadata_patch_approval_v4" / "gate_metadata_patch_approval_v4_latest.json"

EXPECTED_HEAD_PREFIX = "f62e5bd"
EXPECTED_TARGET_COUNT = 11

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
    "apply_performed_now": True,
    "comment_only_apply": True,
    "non_behavioral_metadata_only": True,
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

    modified_tracked_paths: List[str] = []
    for line in dirty_tracked:
        path = line[3:] if len(line) > 3 else line
        modified_tracked_paths.append(path)

    return {
        "head": head.stdout.strip(),
        "branch": branch.stdout.strip(),
        "status_porcelain": status_lines,
        "remote_status_short": remote.stdout.splitlines(),
        "git_dirty": bool(status_lines),
        "dirty_tracked_count": len(dirty_tracked),
        "dirty_tracked_paths": modified_tracked_paths,
        "untracked_count": len(untracked),
        "untracked_paths": untracked,
    }


def fail_closed(reason: str, extra: Optional[Dict[str, Any]] = None) -> int:
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "apply_status": "GATE_METADATA_PATCH_APPLY_V4_FAIL_CLOSED",
        "severity": "BLOCKED",
        "allowed_scope": "COMMENT_ONLY_METADATA_APPLY",
        "final_decision": "STOP_NO_PARTIAL_APPLY",
        "next_action": "REVIEW_APPLY_FAILURE_NO_RUNTIME_ACTION",
        "reason": reason,
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "preview_json": str(PREVIEW_JSON),
        "approval_json": str(APPROVAL_JSON),
        "safety_flags": {**SAFETY_FLAGS, "apply_performed_now": False},
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "target_files_modified": [],
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

    out = OUT_DIR / "gate_metadata_patch_apply_v4_fail_closed_latest.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS GATE METADATA PATCH APPLY v4")
    print("=" * 100)
    print("apply_status: GATE_METADATA_PATCH_APPLY_V4_FAIL_CLOSED")
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


def is_tracked_file(rel_path: str) -> bool:
    result = run_cmd(["git", "ls-files", "--error-unmatch", rel_path])
    return result.returncode == 0


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


def find_insert_index(lines: List[str]) -> int:
    if not lines:
        return 0

    i = 0

    if lines and lines[0].startswith("#!"):
        i = 1

    while i < len(lines) and re.match(r"#.*coding[:=]\s*[-\w.]+", lines[i]):
        i += 1

    while i < len(lines) and not lines[i].strip():
        i += 1

    if i < len(lines) and lines[i].lstrip().startswith(('"""', "'''")):
        quote = '"""' if lines[i].lstrip().startswith('"""') else "'''"
        stripped = lines[i].strip()
        if stripped.count(quote) >= 2 and stripped.endswith(quote) and len(stripped) > 3:
            i += 1
        else:
            i += 1
            while i < len(lines):
                if quote in lines[i]:
                    i += 1
                    break
                i += 1

    while i < len(lines) and not lines[i].strip():
        i += 1

    return i


def clean_one_line(value: Any, max_len: int = 180) -> str:
    if isinstance(value, (dict, list)):
        text = json.dumps(value, sort_keys=True, default=str)
    else:
        text = str(value)
    text = text.replace("\r", " ").replace("\n", " ").strip()
    text = re.sub(r"\s+", " ", text)
    if len(text) > max_len:
        text = text[: max_len - 3] + "..."
    return text


def build_metadata_block_from_preview_item(item: Dict[str, Any]) -> List[str]:
    rel_path = validate_rel_path(item.get("target_path"))
    if rel_path is None:
        raise ValueError("invalid target_path in preview item")

    issue_id = clean_one_line(item.get("issue_id") or "UNKNOWN")
    classification = clean_one_line(item.get("classification") or "UNKNOWN")
    risk = clean_one_line(item.get("risk") or "UNKNOWN")

    evidence = "not provided"
    diff_text = item.get("diff", "")
    if isinstance(diff_text, str):
        for line in diff_text.splitlines():
            if line.startswith("+# gate_review_evidence: "):
                evidence = line[len("+# gate_review_evidence: "):]
                break

    block = [
        "# EDGE_FACTORY_GATE_METADATA_START",
        "# gate_metadata_version: 1",
        "# gate_metadata_kind: non_behavioral_comment_block",
        "# gate_review_source_file: gate_review_candidate_preview_latest.json",
        f"# gate_review_target_path: {rel_path}",
        f"# gate_review_issue_id: {issue_id}",
        f"# gate_review_classification: {classification}",
        f"# gate_review_risk: {risk}",
        f"# gate_review_evidence: {evidence}",
        "# allowed_scope: REPO_ONLY_OS_INTELLIGENCE",
        "# preview_only: true",
        "# non_behavioral_comment_only: true",
        "# runtime_touch_allowed: false",
        "# launcher_allowed: false",
        "# capital_change_allowed: false",
        "# active_paper_allowed: false",
        "# live_allowed: false",
        "# real_orders_allowed: false",
        "# candidate_generation_allowed: false",
        "# family_release_allowed: false",
        "# strategy_research_allowed: false",
        "# holdout_access_allowed: false",
        "# backup_delete_allowed: false",
        "# backup_move_allowed: false",
        "# direct_apply_allowed: false",
        "# EDGE_FACTORY_GATE_METADATA_END",
        "",
    ]

    if not all(line.startswith("#") or line == "" for line in block):
        raise ValueError("metadata block contains non-comment content")

    return block


def normalize_diff_text(text: str) -> str:
    return "\n".join(text.strip().splitlines()).strip()


def compute_candidate_apply(rel_path: str, item: Dict[str, Any]) -> Dict[str, Any]:
    target = REPO_ROOT / rel_path
    original_text = target.read_text(encoding="utf-8")

    if original_text.startswith("\ufeff"):
        raise ValueError(f"{rel_path} has BOM")

    if "EDGE_FACTORY_GATE_METADATA_START" in original_text:
        raise ValueError(f"{rel_path} already has metadata block")

    ast.parse(original_text, filename=rel_path)

    lines = original_text.splitlines()
    insert_at = find_insert_index(lines)
    block = build_metadata_block_from_preview_item(item)
    new_lines = lines[:insert_at] + block + lines[insert_at:]
    new_text = "\n".join(new_lines) + "\n"

    ast.parse(new_text, filename=rel_path)

    diff_lines = list(difflib.unified_diff(
        [line + "\n" for line in lines],
        [line + "\n" for line in new_lines],
        fromfile=f"a/{rel_path}",
        tofile=f"b/{rel_path}",
        lineterm="",
    ))
    generated_diff = "\n".join(diff_lines) + ("\n" if diff_lines else "")

    preview_diff = item.get("diff")
    if not isinstance(preview_diff, str) or not preview_diff.strip():
        raise ValueError(f"{rel_path} missing preview diff")

    if normalize_diff_text(generated_diff) != normalize_diff_text(preview_diff):
        raise ValueError(f"{rel_path} generated diff does not match approved preview diff")

    added_non_comment_lines = [
        line for line in generated_diff.splitlines()
        if line.startswith("+")
        and not line.startswith("+++")
        and line.strip() != "+"
        and not line.startswith("+#")
    ]
    if added_non_comment_lines:
        raise ValueError(f"{rel_path} generated diff contains non-comment added lines: {added_non_comment_lines[:5]}")

    return {
        "target_path": rel_path,
        "insert_line_1based": insert_at + 1,
        "original_text": original_text,
        "new_text": new_text,
        "generated_diff": generated_diff,
        "added_line_count": len([line for line in generated_diff.splitlines() if line.startswith("+") and not line.startswith("+++")]),
    }


def main() -> int:
    safety_error = assert_safety_shape()
    if safety_error:
        return fail_closed(safety_error)

    git_state_before = get_git_state()

    if not git_state_before["head"].startswith(EXPECTED_HEAD_PREFIX):
        return fail_closed(
            "unexpected git HEAD; refusing apply against unknown repo state",
            {
                "expected_head_prefix": EXPECTED_HEAD_PREFIX,
                "git_state_before": git_state_before,
            },
        )

    if git_state_before["dirty_tracked_count"] != 0:
        return fail_closed(
            "tracked files are dirty before apply; refusing partial/ambiguous apply",
            {
                "git_state_before": git_state_before,
            },
        )

    try:
        preview = load_json(PREVIEW_JSON)
        approval = load_json(APPROVAL_JSON)
    except Exception as exc:
        return fail_closed(
            "could not read preview/approval json",
            {
                "error": repr(exc),
                "git_state_before": git_state_before,
            },
        )

    if preview.get("preview_status") != "GATE_METADATA_PATCH_PREVIEW_V4_READY_NO_APPLY":
        return fail_closed(
            "preview v4 is not ready",
            {
                "preview_status": preview.get("preview_status"),
                "git_state_before": git_state_before,
            },
        )

    if approval.get("approval_status") != "GATE_METADATA_PATCH_APPROVAL_V4_READY_COMMENT_ONLY_APPLY_ALLOWED":
        return fail_closed(
            "approval v4 is not ready",
            {
                "approval_status": approval.get("approval_status"),
                "git_state_before": git_state_before,
            },
        )

    if approval.get("comment_only_apply_next_step_allowed") is not True:
        return fail_closed(
            "approval does not allow comment-only apply next step",
            {
                "comment_only_apply_next_step_allowed": approval.get("comment_only_apply_next_step_allowed"),
                "git_state_before": git_state_before,
            },
        )

    approved_targets = set(approval.get("approved_targets") or [])
    if approved_targets != EXPECTED_TARGETS:
        return fail_closed(
            "approved target set mismatch",
            {
                "expected_targets": sorted(EXPECTED_TARGETS),
                "approved_targets": sorted(approved_targets),
                "missing_targets": sorted(EXPECTED_TARGETS - approved_targets),
                "extra_targets": sorted(approved_targets - EXPECTED_TARGETS),
                "git_state_before": git_state_before,
            },
        )

    previews = preview.get("previews")
    if not isinstance(previews, list) or len(previews) != EXPECTED_TARGET_COUNT:
        return fail_closed(
            "preview items missing or wrong length",
            {
                "preview_items_length": len(previews) if isinstance(previews, list) else None,
                "git_state_before": git_state_before,
            },
        )

    items_by_target: Dict[str, Dict[str, Any]] = {}
    for item in previews:
        if not isinstance(item, dict):
            return fail_closed("preview item is not dict", {"item": repr(item)[:500], "git_state_before": git_state_before})

        if item.get("status") != "PREVIEW_READY_NON_BEHAVIORAL_COMMENT_ONLY":
            return fail_closed("preview item status not ready", {"item": item, "git_state_before": git_state_before})

        rel = validate_rel_path(item.get("target_path"))
        if rel is None:
            return fail_closed("preview item target_path invalid", {"item": item, "git_state_before": git_state_before})

        if rel not in EXPECTED_TARGETS:
            return fail_closed("preview item target_path unexpected", {"target_path": rel, "git_state_before": git_state_before})

        if rel in items_by_target:
            return fail_closed("duplicate preview target", {"target_path": rel, "git_state_before": git_state_before})

        if not is_tracked_file(rel):
            return fail_closed("target is not git-tracked", {"target_path": rel, "git_state_before": git_state_before})

        items_by_target[rel] = item

    if set(items_by_target.keys()) != EXPECTED_TARGETS:
        return fail_closed(
            "preview target set mismatch",
            {
                "expected_targets": sorted(EXPECTED_TARGETS),
                "preview_targets": sorted(items_by_target.keys()),
                "missing_targets": sorted(EXPECTED_TARGETS - set(items_by_target.keys())),
                "extra_targets": sorted(set(items_by_target.keys()) - EXPECTED_TARGETS),
                "git_state_before": git_state_before,
            },
        )

    prepared: Dict[str, Dict[str, Any]] = {}
    prepare_errors: List[Dict[str, Any]] = []

    for rel in sorted(EXPECTED_TARGETS):
        try:
            prepared[rel] = compute_candidate_apply(rel, items_by_target[rel])
        except Exception as exc:
            prepare_errors.append({"target_path": rel, "error": repr(exc)})

    if prepare_errors:
        return fail_closed(
            "one or more target files failed pre-apply validation; no files modified",
            {
                "prepare_errors": prepare_errors,
                "git_state_before": git_state_before,
            },
        )

    modified_targets: List[str] = []

    try:
        for rel in sorted(EXPECTED_TARGETS):
            target = REPO_ROOT / rel
            target.write_text(prepared[rel]["new_text"], encoding="utf-8")
            modified_targets.append(rel)
    except Exception as exc:
        return fail_closed(
            "write failed during apply; manual review required",
            {
                "error": repr(exc),
                "modified_targets_before_failure": modified_targets,
                "git_state_before": git_state_before,
                "git_state_after_failure": get_git_state(),
            },
        )

    post_validation_errors: List[Dict[str, Any]] = []

    for rel in sorted(EXPECTED_TARGETS):
        try:
            text = (REPO_ROOT / rel).read_text(encoding="utf-8")
            if text.startswith("\ufeff"):
                post_validation_errors.append({"target_path": rel, "error": "BOM detected after apply"})
            if text.count("EDGE_FACTORY_GATE_METADATA_START") != 1:
                post_validation_errors.append({"target_path": rel, "error": "metadata start marker count is not 1"})
            if text.count("EDGE_FACTORY_GATE_METADATA_END") != 1:
                post_validation_errors.append({"target_path": rel, "error": "metadata end marker count is not 1"})
            ast.parse(text, filename=rel)
        except Exception as exc:
            post_validation_errors.append({"target_path": rel, "error": repr(exc)})

    git_state_after = get_git_state()

    expected_dirty_subset = set(modified_targets)
    actual_dirty_tracked = set(git_state_after["dirty_tracked_paths"])

    unexpected_dirty = sorted(actual_dirty_tracked - expected_dirty_subset)
    missing_dirty = sorted(expected_dirty_subset - actual_dirty_tracked)

    if post_validation_errors or unexpected_dirty or missing_dirty:
        payload_extra = {
            "post_validation_errors": post_validation_errors,
            "unexpected_dirty_tracked_paths": unexpected_dirty,
            "missing_dirty_tracked_paths": missing_dirty,
            "modified_targets": modified_targets,
            "git_state_before": git_state_before,
            "git_state_after": git_state_after,
        }
        return fail_closed(
            "post-apply validation found issues; do not commit before review",
            payload_extra,
        )

    combined_diff_path = OUT_DIR / "gate_metadata_patch_apply_v4_applied_diff_latest.diff"
    combined_diff_path.write_text(
        "\n".join(prepared[rel]["generated_diff"] for rel in sorted(EXPECTED_TARGETS)),
        encoding="utf-8",
    )

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "apply_status": "GATE_METADATA_PATCH_APPLY_V4_COMMENT_ONLY_APPLIED",
        "severity": "ATTENTION",
        "allowed_scope": "COMMENT_ONLY_METADATA_APPLY",
        "final_decision": "RUN_FULL_SYSTEM_READ_ONLY_AUDIT_REFRESH_THEN_COMMIT_IF_CLEAN",
        "next_action": "RUN_FULL_SYSTEM_READ_ONLY_AUDIT_REFRESH_NO_RUNTIME_ACTION",
        "next_module": "full_system_read_only_audit_refresh",
        "reason": "11/11 approved targets received non-behavioral gate metadata comment blocks",
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "preview_json": str(PREVIEW_JSON),
        "approval_json": str(APPROVAL_JSON),
        "combined_applied_diff_path": str(combined_diff_path),
        "modified_target_count": len(modified_targets),
        "modified_targets": modified_targets,
        "target_files_modified": modified_targets,
        "post_validation_errors": post_validation_errors,
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "apply_performed_now": True,
        "runtime_touched": False,
        "launcher_executed": False,
        "capital_changed": False,
        "live_or_real_orders": False,
        "holdout_accessed": False,
        "backup_deleted_or_moved": False,
        "gitignore_changed": False,
        "git_add_force_used": False,
        "git_state_before": git_state_before,
        "git_state_after": git_state_after,
    }

    latest_json = OUT_DIR / "gate_metadata_patch_apply_v4_latest.json"
    timestamped_json = OUT_DIR / f"gate_metadata_patch_apply_v4_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "gate_metadata_patch_apply_v4_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    txt_lines = [
        "EDGE FACTORY OS GATE METADATA PATCH APPLY v4",
        "=" * 100,
        f"apply_status: {payload['apply_status']}",
        f"severity: {payload['severity']}",
        f"allowed_scope: {payload['allowed_scope']}",
        f"final_decision: {payload['final_decision']}",
        f"next_action: {payload['next_action']}",
        f"next_module: {payload['next_module']}",
        f"reason: {payload['reason']}",
        f"modified_target_count: {payload['modified_target_count']}",
        "",
        "MODIFIED TARGETS",
        "-" * 100,
        json.dumps(modified_targets, indent=2, sort_keys=True),
        "",
        "SAFETY",
        "-" * 100,
        json.dumps(SAFETY_FLAGS, indent=2, sort_keys=True),
        "",
        "GIT STATE BEFORE",
        "-" * 100,
        json.dumps(git_state_before, indent=2, sort_keys=True),
        "",
        "GIT STATE AFTER",
        "-" * 100,
        json.dumps(git_state_after, indent=2, sort_keys=True),
        "",
        "OUTPUTS",
        "-" * 100,
        f"latest_json: {latest_json}",
        f"timestamped_json: {timestamped_json}",
        f"latest_txt: {latest_txt}",
        f"combined_applied_diff_path: {combined_diff_path}",
    ]

    latest_txt.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")

    print("\n".join(txt_lines))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())