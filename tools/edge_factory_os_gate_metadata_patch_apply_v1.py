from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]

PREVIEW_JSON = (
    REPO_ROOT
    / "edge_factory_os_gate_metadata_patch_preview"
    / "gate_metadata_patch_preview_latest.json"
)

APPROVAL_JSON = (
    REPO_ROOT
    / "edge_factory_os_gate_metadata_patch_approval"
    / "gate_metadata_patch_approval_latest.json"
)

OUT_DIR = REPO_ROOT / "edge_factory_os_gate_metadata_patch_apply"
OUT_JSON = OUT_DIR / "gate_metadata_patch_apply_latest.json"
OUT_TXT = OUT_DIR / "gate_metadata_patch_apply_latest.txt"

REQUIRED_APPROVAL_STATUS = "GATE_METADATA_PATCH_APPROVAL_READY_FOR_APPLY_MODULE"
REQUIRED_PREVIEW_STATUS = "GATE_METADATA_PATCH_PREVIEW_READY_NO_APPLY"

SAFETY_FLAGS = {
    "repo_only": True,
    "guarded_repo_mutation_only": True,
    "non_behavioral_metadata_only": True,
    "runtime_touch_allowed": False,
    "launcher_allowed": False,
    "runtime_patch_allowed": False,
    "backup_delete_allowed": False,
    "backup_move_allowed": False,
    "gitignore_change_allowed": False,
    "strategy_research_allowed": False,
    "candidate_generation_allowed": False,
    "family_release_allowed": False,
    "capital_change_allowed": False,
    "active_paper_allowed": False,
    "live_allowed": False,
    "real_orders_allowed": False,
    "file_delete_allowed": False,
    "file_move_allowed": False,
    "execution_allowed": False,
    "old_short_guarded_apply_allowed": False,
}

FORBIDDEN_ACTIONS = [
    "Do not run launcher.",
    "Do not touch runtime.",
    "Do not start processes.",
    "Do not run strategy research.",
    "Do not generate candidates.",
    "Do not change capital.",
    "Do not enable active paper.",
    "Do not enable live trading.",
    "Do not enable or send real orders.",
    "Do not touch holdout.",
    "Do not run old_short guarded apply.",
    "Do not delete or move unrelated backup files.",
    "Do not change .gitignore.",
    "Do not use git add -f.",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def timestamp_for_filename() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def rel_repo(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_cmd(args: List[str], timeout: int = 30) -> Dict[str, Any]:
    try:
        p = subprocess.run(
            args,
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": p.returncode == 0,
            "returncode": p.returncode,
            "stdout": p.stdout,
            "stderr": p.stderr,
        }
    except Exception as exc:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": repr(exc),
        }


def git_state() -> Dict[str, Any]:
    st = run_cmd(["git", "-C", str(REPO_ROOT), "status", "--short"])
    head = run_cmd(["git", "-C", str(REPO_ROOT), "rev-parse", "--short", "HEAD"])
    last = run_cmd(["git", "-C", str(REPO_ROOT), "log", "-1", "--pretty=%h %s"])

    lines = [x.strip().replace("\\", "/") for x in st["stdout"].splitlines() if x.strip()] if st["ok"] else []

    return {
        "status_ok": st["ok"],
        "head_short": head["stdout"].strip() if head["ok"] else None,
        "last_commit": last["stdout"].strip() if last["ok"] else None,
        "git_status_lines": lines,
        "untracked_or_dirty_count": len(lines),
        "known_backup_pending_count": len([
            x for x in lines
            if ".bak" in x
            or "_bak_" in x
            or "blocked_patch_bak" in x
            or "readonly_fix_bak" in x
        ]),
        "old_short_guarded_apply_untracked": any(
            "tools/edge_factory_os_old_short_guarded_runtime_reenable_apply_v1.py" in x
            for x in lines
        ),
        "universe_guard_review_required": any(
            "tools/edge_factory_os_universe_coverage_guard_v1.py" in x
            for x in lines
        ),
    }


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root is not object: {path}")
    return data


def syntax_check_python(text: str, rel_path: str) -> str:
    if not rel_path.endswith(".py"):
        return ""
    try:
        compile(text, rel_path, "exec", dont_inherit=True)
        return ""
    except SyntaxError as exc:
        return str(exc)


def validate_approval_and_preview(approval: Dict[str, Any], preview: Dict[str, Any]) -> Tuple[bool, List[str], List[Dict[str, Any]]]:
    errors: List[str] = []

    approval_status = approval.get("approval_status")
    if approval_status != REQUIRED_APPROVAL_STATUS:
        errors.append(f"APPROVAL_STATUS_MISMATCH:{approval_status}")

    validation = approval.get("validation", {})
    if not isinstance(validation, dict) or validation.get("ok") is not True:
        errors.append(f"APPROVAL_VALIDATION_NOT_OK:{validation}")

    if approval.get("target_file_mutation_approved_now") is not False:
        errors.append("APPROVAL_TARGET_FILE_MUTATION_FLAG_NOT_FALSE")

    preview_status = preview.get("preview_status")
    if preview_status != REQUIRED_PREVIEW_STATUS:
        errors.append(f"PREVIEW_STATUS_MISMATCH:{preview_status}")

    if preview.get("direct_apply_recommended_now") is not False:
        errors.append("PREVIEW_DIRECT_APPLY_FLAG_NOT_FALSE")

    counts = preview.get("counts", {})
    if not isinstance(counts, dict):
        errors.append("PREVIEW_COUNTS_NOT_OBJECT")
        counts = {}

    if counts.get("metadata_preview_blocked_count") != 0:
        errors.append(f"BLOCKED_COUNT_NOT_ZERO:{counts.get('metadata_preview_blocked_count')}")

    if counts.get("direct_apply_recommended_now") != 0:
        errors.append(f"DIRECT_APPLY_COUNT_NOT_ZERO:{counts.get('direct_apply_recommended_now')}")

    rows = preview.get("metadata_preview_possible", [])
    if not isinstance(rows, list):
        errors.append("METADATA_PREVIEW_POSSIBLE_NOT_LIST")
        rows = []

    if len(rows) != counts.get("metadata_preview_possible_count"):
        errors.append(
            f"POSSIBLE_ROWS_COUNT_MISMATCH:rows={len(rows)}:count={counts.get('metadata_preview_possible_count')}"
        )

    if not rows:
        errors.append("NO_METADATA_ROWS_TO_APPLY")

    for row in rows:
        if not isinstance(row, dict):
            errors.append("METADATA_ROW_NOT_OBJECT")
            continue
        if row.get("preview_possible") is not True:
            errors.append(f"ROW_PREVIEW_NOT_TRUE:{row.get('relative_path')}")
        if row.get("behavior_change_expected") is not False:
            errors.append(f"ROW_BEHAVIOR_CHANGE_NOT_FALSE:{row.get('relative_path')}")
        if row.get("proposed_patch_type") != "non_behavioral_gate_metadata_comment_block":
            errors.append(f"ROW_PATCH_TYPE_INVALID:{row.get('relative_path')}:{row.get('proposed_patch_type')}")
        if not row.get("relative_path"):
            errors.append("ROW_RELATIVE_PATH_MISSING")
        if not row.get("before_sha256") or not row.get("after_preview_sha256"):
            errors.append(f"ROW_HASH_MISSING:{row.get('relative_path')}")
        if not row.get("metadata_block_preview"):
            errors.append(f"ROW_METADATA_BLOCK_MISSING:{row.get('relative_path')}")

    return len(errors) == 0, errors, rows


def build_new_text(current_text: str, row: Dict[str, Any]) -> str:
    block = str(row.get("metadata_block_preview") or "")
    insert_strategy = row.get("insert_strategy", {})
    if not isinstance(insert_strategy, dict):
        raise RuntimeError(f"insert_strategy_not_object:{row.get('relative_path')}")

    insert_after_line = int(insert_strategy.get("insert_after_line", 0))
    lines = current_text.splitlines(keepends=True)

    if "EDGE_FACTORY_OS_EXPLICIT_GATE_METADATA_V1" in current_text:
        raise RuntimeError(f"metadata_already_present:{row.get('relative_path')}")

    if lines and insert_after_line < len(lines):
        return "".join(lines[:insert_after_line]) + block + "".join(lines[insert_after_line:])

    return current_text + ("\n" if current_text and not current_text.endswith("\n") else "") + block


def plan_apply(rows: List[Dict[str, Any]]) -> Tuple[bool, List[str], List[Dict[str, Any]], Dict[str, str]]:
    errors: List[str] = []
    planned: List[Dict[str, Any]] = []
    new_text_by_rel: Dict[str, str] = {}

    seen = set()
    for row in rows:
        rel_path = str(row.get("relative_path") or "").replace("\\", "/")
        if rel_path in seen:
            errors.append(f"DUPLICATE_TARGET:{rel_path}")
            continue
        seen.add(rel_path)

        target = REPO_ROOT / rel_path.replace("/", "\\")
        if not target.is_file():
            errors.append(f"TARGET_FILE_MISSING:{rel_path}")
            continue

        try:
            current_text = target.read_text(encoding="utf-8")
        except Exception as exc:
            errors.append(f"TARGET_READ_FAILED:{rel_path}:{exc!r}")
            continue

        current_hash = sha256_text(current_text)
        expected_before = str(row.get("before_sha256") or "")
        if current_hash != expected_before:
            errors.append(f"BEFORE_HASH_MISMATCH:{rel_path}:observed={current_hash}:expected={expected_before}")
            continue

        syntax_before = syntax_check_python(current_text, rel_path)
        if syntax_before:
            errors.append(f"SYNTAX_BEFORE_FAILED:{rel_path}:{syntax_before}")
            continue

        try:
            new_text = build_new_text(current_text, row)
        except Exception as exc:
            errors.append(f"BUILD_NEW_TEXT_FAILED:{rel_path}:{exc!r}")
            continue

        expected_after = str(row.get("after_preview_sha256") or "")
        observed_after = sha256_text(new_text)
        if observed_after != expected_after:
            errors.append(f"AFTER_PREVIEW_HASH_MISMATCH:{rel_path}:observed={observed_after}:expected={expected_after}")
            continue

        syntax_after = syntax_check_python(new_text, rel_path)
        if syntax_after:
            errors.append(f"SYNTAX_AFTER_FAILED:{rel_path}:{syntax_after}")
            continue

        planned.append({
            "relative_path": rel_path,
            "before_sha256": current_hash,
            "after_sha256": observed_after,
            "before_line_count": len(current_text.splitlines()),
            "after_line_count": len(new_text.splitlines()),
            "proposed_patch_type": row.get("proposed_patch_type"),
            "insert_strategy": row.get("insert_strategy"),
            "behavior_change_expected": False,
        })
        new_text_by_rel[rel_path] = new_text

    return len(errors) == 0, errors, planned, new_text_by_rel


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    generated_at = now_iso()
    ts = timestamp_for_filename()

    approval = load_json(APPROVAL_JSON)
    preview = load_json(PREVIEW_JSON)

    valid, validation_errors, rows = validate_approval_and_preview(approval, preview)
    plan_ok = False
    plan_errors: List[str] = []
    planned_changes: List[Dict[str, Any]] = []
    new_text_by_rel: Dict[str, str] = {}

    apply_status = "GATE_METADATA_PATCH_APPLY_BLOCKED"
    final_decision = "STOP_REVIEW_APPROVAL_OR_PREVIEW"
    next_action = "STOP_NO_TARGET_MUTATION"
    next_module = "edge_factory_os_gate_metadata_patch_preview_v1.py"

    backups_created: List[Dict[str, Any]] = []
    rollback = {
        "rollback_performed": False,
        "rollback_reason": "",
        "rollback_restored_files": [],
    }

    if valid:
        plan_ok, plan_errors, planned_changes, new_text_by_rel = plan_apply(rows)

    block_reasons = validation_errors + plan_errors

    if valid and plan_ok and not block_reasons:
        snapshots: Dict[str, bytes] = {}
        try:
            # Snapshot all target files before writing anything.
            for rel_path in new_text_by_rel:
                target = REPO_ROOT / rel_path.replace("/", "\\")
                snapshots[rel_path] = target.read_bytes()

            # Create backup files next to target files.
            for rel_path, original_bytes in snapshots.items():
                target = REPO_ROOT / rel_path.replace("/", "\\")
                backup = target.with_name(target.name + f".gate_metadata_patch_bak_{ts}")
                backup.write_bytes(original_bytes)
                backups_created.append({
                    "relative_path": rel_repo(backup),
                    "target_relative_path": rel_path,
                    "sha256": sha256_bytes(original_bytes),
                    "byte_len": len(original_bytes),
                })

            # Apply metadata comment block.
            for rel_path, new_text in new_text_by_rel.items():
                target = REPO_ROOT / rel_path.replace("/", "\\")
                target.write_text(new_text, encoding="utf-8")

            # Post-apply validation.
            for planned in planned_changes:
                rel_path = planned["relative_path"]
                target = REPO_ROOT / rel_path.replace("/", "\\")
                final_text = target.read_text(encoding="utf-8")
                final_hash = sha256_text(final_text)
                if final_hash != planned["after_sha256"]:
                    raise RuntimeError(f"POST_APPLY_HASH_MISMATCH:{rel_path}")

                syntax_after = syntax_check_python(final_text, rel_path)
                if syntax_after:
                    raise RuntimeError(f"POST_APPLY_SYNTAX_FAILED:{rel_path}:{syntax_after}")

                if "EDGE_FACTORY_OS_EXPLICIT_GATE_METADATA_V1" not in final_text:
                    raise RuntimeError(f"POST_APPLY_METADATA_MISSING:{rel_path}")

            apply_status = "GATE_METADATA_PATCH_APPLIED"
            final_decision = "RUN_FULL_SYSTEM_READ_ONLY_AUDIT_AGAIN"
            next_action = "RERUN_FULL_SYSTEM_READ_ONLY_AUDIT_TO_CONFIRM_ATTENTION_REDUCTION"
            next_module = "edge_factory_os_full_system_read_only_audit_v1.py"

        except Exception as exc:
            rollback["rollback_performed"] = True
            rollback["rollback_reason"] = repr(exc)
            for rel_path, original_bytes in snapshots.items():
                target = REPO_ROOT / rel_path.replace("/", "\\")
                try:
                    target.write_bytes(original_bytes)
                    rollback["rollback_restored_files"].append(rel_path)
                except Exception as rb_exc:
                    block_reasons.append(f"ROLLBACK_FAILED:{rel_path}:{rb_exc!r}")

            block_reasons.append(f"APPLY_FAILED_AND_ROLLBACK_ATTEMPTED:{exc!r}")
            planned_changes = []
            apply_status = "GATE_METADATA_PATCH_APPLY_BLOCKED"
            final_decision = "STOP_REVIEW_APPLY_FAILURE"
            next_action = "STOP_NO_RUNTIME_ACTION_REVIEW_ROLLBACK"
            next_module = "edge_factory_os_gate_metadata_patch_preview_v1.py"

    result = {
        "module": "edge_factory_os_gate_metadata_patch_apply_v1.py",
        "generated_at_utc": generated_at,
        "repo_root": str(REPO_ROOT),
        "apply_status": apply_status,
        "allowed_scope": "GUARDED_REPO_MUTATION_ONLY" if apply_status == "GATE_METADATA_PATCH_APPLIED" else "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "changed_file_count": len(planned_changes) if apply_status == "GATE_METADATA_PATCH_APPLIED" else 0,
        "backup_file_count": len(backups_created) if apply_status == "GATE_METADATA_PATCH_APPLIED" else 0,
        "validation": {
            "approval_preview_valid": valid,
            "validation_errors": validation_errors,
            "plan_ok": plan_ok,
            "plan_errors": plan_errors,
        },
        "changed_files": planned_changes if apply_status == "GATE_METADATA_PATCH_APPLIED" else [],
        "backup_files": backups_created if apply_status == "GATE_METADATA_PATCH_APPLIED" else [],
        "block_reasons": block_reasons,
        "rollback": rollback,
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "git_state": git_state(),
        "outputs": {
            "json": str(OUT_JSON),
            "txt": str(OUT_TXT),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines: List[str] = []
    lines.append("EDGE FACTORY OS GATE METADATA PATCH APPLY v1")
    lines.append("=" * 100)
    lines.append(f"apply_status: {apply_status}")
    lines.append(f"allowed_scope: {result['allowed_scope']}")
    lines.append(f"final_decision: {final_decision}")
    lines.append(f"next_action: {next_action}")
    lines.append(f"next_module: {next_module}")
    lines.append(f"changed_file_count: {result['changed_file_count']}")
    lines.append(f"backup_file_count: {result['backup_file_count']}")
    lines.append("")
    lines.append("VALIDATION")
    lines.append("-" * 100)
    lines.append(json.dumps(result["validation"], indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("CHANGED FILES")
    lines.append("-" * 100)
    lines.append(json.dumps(result["changed_files"], indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("BACKUP FILES")
    lines.append("-" * 100)
    lines.append(json.dumps(result["backup_files"], indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("BLOCK REASONS")
    lines.append("-" * 100)
    if block_reasons:
        for item in block_reasons:
            lines.append(str(item))
    else:
        lines.append("none")
    lines.append("")
    lines.append("ROLLBACK")
    lines.append("-" * 100)
    lines.append(json.dumps(rollback, indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    lines.append(json.dumps(SAFETY_FLAGS, indent=2, sort_keys=True, ensure_ascii=False))
    lines.append("")
    lines.append("FORBIDDEN ACTIONS")
    lines.append("-" * 100)
    for item in FORBIDDEN_ACTIONS:
        lines.append(f"- {item}")

    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"apply_status: {apply_status}")
    print(f"final_decision: {final_decision}")
    print(f"next_action: {next_action}")
    print(f"next_module: {next_module}")
    print(f"changed_file_count: {result['changed_file_count']}")
    print(f"backup_file_count: {result['backup_file_count']}")
    print("validation:")
    print(json.dumps(result["validation"], indent=2, ensure_ascii=False))
    if block_reasons:
        print("block_reasons:")
        print(json.dumps(block_reasons, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()