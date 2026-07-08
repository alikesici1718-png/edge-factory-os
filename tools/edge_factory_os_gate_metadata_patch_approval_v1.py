from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]

PREVIEW_JSON = (
    REPO_ROOT
    / "edge_factory_os_gate_metadata_patch_preview"
    / "gate_metadata_patch_preview_latest.json"
)

OUT_DIR = REPO_ROOT / "edge_factory_os_gate_metadata_patch_approval"
OUT_JSON = OUT_DIR / "gate_metadata_patch_approval_latest.json"
OUT_TXT = OUT_DIR / "gate_metadata_patch_approval_latest.txt"

REQUIRED_PREVIEW_STATUS = "GATE_METADATA_PATCH_PREVIEW_READY_NO_APPLY"
REQUIRED_FINAL_DECISION = "METADATA_PATCH_PREVIEW_READY_REQUIRE_APPROVAL_BEFORE_APPLY"

SAFETY_FLAGS = {
    "repo_only": True,
    "approval_only": True,
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
    "target_file_mutation_allowed_now": False,
    "old_short_guarded_apply_allowed": False,
}

FORBIDDEN_ACTIONS = [
    "Do not modify target files.",
    "Do not apply metadata patches from this module.",
    "Do not create backup files.",
    "Do not delete or move backup files.",
    "Do not change .gitignore.",
    "Do not use git add -f.",
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
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel_repo(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


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


def validate_preview(preview: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []

    preview_status = preview.get("preview_status")
    final_decision = preview.get("final_decision")
    direct_apply = preview.get("direct_apply_recommended_now")
    counts = preview.get("counts", {})
    if not isinstance(counts, dict):
        counts = {}

    candidate_count = counts.get("candidate_count")
    possible_count = counts.get("metadata_preview_possible_count")
    blocked_count = counts.get("metadata_preview_blocked_count")
    direct_apply_count = counts.get("direct_apply_recommended_now")

    possible_rows = preview.get("metadata_preview_possible", [])
    blocked_rows = preview.get("metadata_preview_blocked", [])

    if preview_status != REQUIRED_PREVIEW_STATUS:
        errors.append(f"PREVIEW_STATUS_MISMATCH:{preview_status}")

    if final_decision != REQUIRED_FINAL_DECISION:
        errors.append(f"FINAL_DECISION_MISMATCH:{final_decision}")

    if direct_apply is not False:
        errors.append(f"DIRECT_APPLY_FLAG_NOT_FALSE:{direct_apply}")

    if direct_apply_count != 0:
        errors.append(f"DIRECT_APPLY_COUNT_NOT_ZERO:{direct_apply_count}")

    if blocked_count != 0:
        errors.append(f"BLOCKED_COUNT_NOT_ZERO:{blocked_count}")

    if candidate_count != possible_count:
        errors.append(f"CANDIDATE_POSSIBLE_COUNT_MISMATCH:candidate={candidate_count}:possible={possible_count}")

    if not isinstance(possible_rows, list):
        errors.append("METADATA_PREVIEW_POSSIBLE_NOT_LIST")
        possible_rows = []

    if not isinstance(blocked_rows, list):
        errors.append("METADATA_PREVIEW_BLOCKED_NOT_LIST")
        blocked_rows = []

    if len(possible_rows) != possible_count:
        errors.append(f"POSSIBLE_ROWS_COUNT_MISMATCH:rows={len(possible_rows)}:count={possible_count}")

    if len(blocked_rows) != 0:
        errors.append(f"BLOCKED_ROWS_NOT_EMPTY:{len(blocked_rows)}")

    behavior_change_bad = []
    for row in possible_rows:
        if not isinstance(row, dict):
            behavior_change_bad.append("non_dict_row")
            continue
        if row.get("behavior_change_expected") is not False:
            behavior_change_bad.append(row.get("relative_path"))

    if behavior_change_bad:
        errors.append(f"BEHAVIOR_CHANGE_EXPECTED_NOT_FALSE:{behavior_change_bad}")

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "observed": {
            "preview_status": preview_status,
            "final_decision": final_decision,
            "direct_apply_recommended_now": direct_apply,
            "candidate_count": candidate_count,
            "metadata_preview_possible_count": possible_count,
            "metadata_preview_blocked_count": blocked_count,
            "direct_apply_count": direct_apply_count,
            "possible_rows": len(possible_rows),
            "blocked_rows": len(blocked_rows),
        },
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    preview = load_json(PREVIEW_JSON)
    validation = validate_preview(preview)

    if validation["ok"]:
        approval_status = "GATE_METADATA_PATCH_APPROVAL_READY_FOR_APPLY_MODULE"
        final_decision = "APPROVAL_RECORDED_BUILD_METADATA_PATCH_APPLY_MODULE_NEXT"
        next_action = "BUILD_METADATA_PATCH_APPLY_MODULE_DO_NOT_RUN_RUNTIME_OR_LAUNCHER"
        next_module = "edge_factory_os_gate_metadata_patch_apply_v1.py"
    else:
        approval_status = "GATE_METADATA_PATCH_APPROVAL_BLOCKED"
        final_decision = "STOP_REVIEW_METADATA_PATCH_PREVIEW"
        next_action = "STOP_NO_APPLY_REVIEW_PREVIEW_ERRORS"
        next_module = "edge_factory_os_gate_metadata_patch_preview_v1.py"

    result = {
        "module": "edge_factory_os_gate_metadata_patch_approval_v1.py",
        "generated_at_utc": now_iso(),
        "repo_root": str(REPO_ROOT),
        "approval_status": approval_status,
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "approval_scope": "NON_BEHAVIORAL_GATE_METADATA_COMMENT_BLOCKS_ONLY",
        "target_file_mutation_approved_now": False,
        "runtime_launcher_capital_live_real_order_approved": False,
        "preview_input": {
            "path": rel_repo(PREVIEW_JSON),
            "preview_status": preview.get("preview_status"),
            "final_decision": preview.get("final_decision"),
            "counts": preview.get("counts"),
            "classification_counts": preview.get("classification_counts"),
        },
        "validation": validation,
        "approved_future_apply_constraints": {
            "future_apply_may_only_touch": "metadata_preview_possible.relative_path files",
            "future_apply_patch_type": "non_behavioral_gate_metadata_comment_block",
            "future_apply_must_preserve_behavior": True,
            "future_apply_must_recheck_hashes": True,
            "future_apply_must_compile_python_targets": True,
            "future_apply_must_create_backups": True,
            "future_apply_must_not_touch_runtime_launcher_capital_live_real_orders": True,
        },
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
    lines.append("EDGE FACTORY OS GATE METADATA PATCH APPROVAL v1")
    lines.append("=" * 100)
    lines.append(f"approval_status: {approval_status}")
    lines.append(f"allowed_scope: {result['allowed_scope']}")
    lines.append(f"final_decision: {final_decision}")
    lines.append(f"next_action: {next_action}")
    lines.append(f"next_module: {next_module}")
    lines.append(f"target_file_mutation_approved_now: {result['target_file_mutation_approved_now']}")
    lines.append("")
    lines.append("VALIDATION")
    lines.append("-" * 100)
    lines.append(json.dumps(validation, indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("APPROVED FUTURE APPLY CONSTRAINTS")
    lines.append("-" * 100)
    lines.append(json.dumps(result["approved_future_apply_constraints"], indent=2, ensure_ascii=False))
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

    print(f"approval_status: {approval_status}")
    print(f"final_decision: {final_decision}")
    print(f"next_action: {next_action}")
    print(f"next_module: {next_module}")
    print("validation:")
    print(json.dumps(validation, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()