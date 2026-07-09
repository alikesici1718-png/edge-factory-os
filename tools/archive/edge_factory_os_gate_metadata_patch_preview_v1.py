from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]

GATE_REVIEW_JSON = (
    REPO_ROOT
    / "edge_factory_os_gate_review_candidate_preview"
    / "gate_review_candidate_preview_latest.json"
)

OUT_DIR = REPO_ROOT / "edge_factory_os_gate_metadata_patch_preview"
OUT_JSON = OUT_DIR / "gate_metadata_patch_preview_latest.json"
OUT_TXT = OUT_DIR / "gate_metadata_patch_preview_latest.txt"

SAFETY_FLAGS = {
    "repo_only": True,
    "preview_only": True,
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
    "Do not modify target files.",
    "Do not apply metadata patches.",
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

METADATA_BLOCK_TEMPLATE = '''\
# EDGE_FACTORY_OS_EXPLICIT_GATE_METADATA_V1
# allowed_scope: REPO_ONLY_GOVERNED_TOOLING
# runtime_touch_allowed: False
# launcher_allowed: False
# capital_change_allowed: False
# live_allowed: False
# real_orders_allowed: False
# backup_delete_allowed: False
# backup_move_allowed: False
# gitignore_change_allowed: False
# requires_preview_before_apply: True
# requires_explicit_approval_before_mutation: True
# behavior_change: False
'''


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel_repo(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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


def read_text(path_str: str) -> str:
    p = REPO_ROOT / path_str.replace("/", "\\")
    try:
        if p.is_file():
            return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    return ""


def syntax_check_python(text: str, rel_path: str) -> str:
    if not rel_path.endswith(".py"):
        return ""
    try:
        compile(text, rel_path, "exec", dont_inherit=True)
        return ""
    except SyntaxError as exc:
        return str(exc)


def get_candidate_path(row: Dict[str, Any]) -> str:
    issue = row.get("issue")
    if isinstance(issue, dict):
        path = issue.get("path")
        if isinstance(path, str) and path:
            return path.replace("\\", "/")
    path = row.get("path")
    if isinstance(path, str):
        return path.replace("\\", "/")
    return ""


def get_candidate_issue_id(row: Dict[str, Any]) -> str:
    issue = row.get("issue")
    if isinstance(issue, dict):
        val = issue.get("issue_id")
        if isinstance(val, str):
            return val
    val = row.get("issue_id")
    return val if isinstance(val, str) else ""


def choose_insert_strategy(text: str, rel_path: str) -> Dict[str, Any]:
    lines = text.splitlines(keepends=True)

    if not lines:
        return {
            "strategy": "prepend_to_empty_file",
            "insert_after_line": 0,
            "reason": "File is empty; metadata would be the first content.",
        }

    start = 0
    if lines and lines[0].startswith("#!"):
        start = 1

    if start < len(lines) and "coding" in lines[start].lower():
        start += 1

    # If the file begins with a module docstring, preview inserting after the docstring
    # only when a simple triple-quote boundary is visible. Otherwise use top-of-file comments.
    stripped_join = "".join(lines[start:start + 20])
    if stripped_join.lstrip().startswith(('"""', "'''")):
        quote = '"""' if stripped_join.lstrip().startswith('"""') else "'''"
        quote_count = 0
        for idx in range(start, min(len(lines), start + 80)):
            quote_count += lines[idx].count(quote)
            if quote_count >= 2:
                return {
                    "strategy": "insert_after_initial_docstring",
                    "insert_after_line": idx + 1,
                    "reason": "Initial module docstring detected; metadata preview would be inserted after it.",
                }

    return {
        "strategy": "insert_after_shebang_encoding_if_any",
        "insert_after_line": start,
        "reason": "Metadata preview would be inserted near top of file after shebang/encoding line if present.",
    }


def build_preview_for_candidate(row: Dict[str, Any]) -> Dict[str, Any]:
    rel_path = get_candidate_path(row)
    issue_id = get_candidate_issue_id(row)
    classification = str(row.get("classification") or "")
    reason = str(row.get("reason") or "")
    prior_action = str(row.get("proposed_next_action") or "")

    text = read_text(rel_path)
    file_exists = bool(text)
    path_obj = REPO_ROOT / rel_path.replace("/", "\\")

    if not rel_path:
        return {
            "issue_id": issue_id,
            "relative_path": rel_path,
            "classification": classification,
            "preview_possible": False,
            "blocked_reason": "candidate_path_missing_in_review_row",
            "proposed_patch_type": "none",
        }

    if not path_obj.is_file():
        return {
            "issue_id": issue_id,
            "relative_path": rel_path,
            "classification": classification,
            "preview_possible": False,
            "blocked_reason": "target_file_missing_on_disk",
            "proposed_patch_type": "none",
        }

    if "EDGE_FACTORY_OS_EXPLICIT_GATE_METADATA_V1" in text:
        return {
            "issue_id": issue_id,
            "relative_path": rel_path,
            "classification": classification,
            "preview_possible": False,
            "blocked_reason": "metadata_already_present",
            "proposed_patch_type": "none",
            "before_sha256": sha256_text(text),
        }

    syntax_before = syntax_check_python(text, rel_path)
    if syntax_before:
        return {
            "issue_id": issue_id,
            "relative_path": rel_path,
            "classification": classification,
            "preview_possible": False,
            "blocked_reason": "target_file_has_existing_syntax_error",
            "syntax_error": syntax_before,
            "proposed_patch_type": "none",
            "before_sha256": sha256_text(text),
        }

    insert_strategy = choose_insert_strategy(text, rel_path)
    insert_after_line = int(insert_strategy["insert_after_line"])
    lines = text.splitlines(keepends=True)

    block = METADATA_BLOCK_TEMPLATE
    if lines and insert_after_line < len(lines):
        new_text = "".join(lines[:insert_after_line]) + block + "".join(lines[insert_after_line:])
    else:
        new_text = text + ("\n" if text and not text.endswith("\n") else "") + block

    syntax_after = syntax_check_python(new_text, rel_path)
    preview_possible = syntax_after == ""

    return {
        "issue_id": issue_id,
        "relative_path": rel_path,
        "classification": classification,
        "prior_reason": reason,
        "prior_action": prior_action,
        "preview_possible": preview_possible,
        "blocked_reason": "" if preview_possible else "metadata_preview_would_break_syntax",
        "syntax_after_preview_error": syntax_after,
        "proposed_patch_type": "non_behavioral_gate_metadata_comment_block",
        "insert_strategy": insert_strategy,
        "metadata_block_preview": METADATA_BLOCK_TEMPLATE,
        "before_sha256": sha256_text(text),
        "after_preview_sha256": sha256_text(new_text),
        "before_line_count": len(text.splitlines()),
        "after_preview_line_count": len(new_text.splitlines()),
        "behavior_change_expected": False,
        "target_file_exists": file_exists,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    gate_review = load_json(GATE_REVIEW_JSON)

    preview_candidates = gate_review.get("preview_fix_candidates", [])
    if not isinstance(preview_candidates, list):
        preview_candidates = []

    proposed = [
        build_preview_for_candidate(row)
        for row in preview_candidates
        if isinstance(row, dict)
    ]

    possible = [row for row in proposed if row.get("preview_possible") is True]
    blocked = [row for row in proposed if row.get("preview_possible") is not True]

    class_counts = {}
    for row in proposed:
        cls = str(row.get("classification") or "UNKNOWN")
        class_counts[cls] = class_counts.get(cls, 0) + 1

    preview_status = "GATE_METADATA_PATCH_PREVIEW_READY_NO_APPLY"

    # Still no direct apply from this module.
    direct_apply_recommended_now = False

    if possible and not blocked:
        final_decision = "METADATA_PATCH_PREVIEW_READY_REQUIRE_APPROVAL_BEFORE_APPLY"
        next_action = "REVIEW_METADATA_PATCH_PREVIEW_THEN_BUILD_APPROVAL_GATE"
        next_module = "edge_factory_os_gate_metadata_patch_approval_v1.py"
    elif possible and blocked:
        final_decision = "PARTIAL_METADATA_PATCH_PREVIEW_REVIEW_BLOCKED_ROWS"
        next_action = "REVIEW_BLOCKED_ROWS_BEFORE_ANY_APPROVAL"
        next_module = "edge_factory_os_gate_metadata_patch_preview_v1.py"
    else:
        final_decision = "NO_METADATA_PATCH_PREVIEW_APPLICABLE"
        next_action = "CONTINUE_RUNTIME_SURFACE_MANUAL_REVIEW_PACKET"
        next_module = "edge_factory_os_runtime_surface_manual_review_packet_v1.py"

    result = {
        "module": "edge_factory_os_gate_metadata_patch_preview_v1.py",
        "generated_at_utc": now_iso(),
        "repo_root": str(REPO_ROOT),
        "preview_status": preview_status,
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "direct_apply_recommended_now": direct_apply_recommended_now,
        "gate_review_input": {
            "path": rel_repo(GATE_REVIEW_JSON),
            "preview_status": gate_review.get("preview_status"),
            "counts": gate_review.get("counts"),
            "classification_counts": gate_review.get("classification_counts"),
            "risk_counts": gate_review.get("risk_counts"),
        },
        "counts": {
            "candidate_count": len(preview_candidates),
            "metadata_preview_possible_count": len(possible),
            "metadata_preview_blocked_count": len(blocked),
            "direct_apply_recommended_now": 0,
        },
        "classification_counts": class_counts,
        "metadata_patch_previews": proposed,
        "metadata_preview_possible": possible,
        "metadata_preview_blocked": blocked,
        "recommended_policy": [
            {
                "policy": "Metadata patch preview is non-behavioral only.",
                "reason": "The preview proposes comment metadata blocks only; it must not change execution logic.",
            },
            {
                "policy": "Approval required before apply.",
                "reason": "Even non-behavioral metadata patches should be applied only after review.",
            },
            {
                "policy": "No target file mutation in preview module.",
                "reason": "This module writes only its own JSON/TXT artifacts.",
            },
        ],
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
    lines.append("EDGE FACTORY OS GATE METADATA PATCH PREVIEW v1")
    lines.append("=" * 100)
    lines.append(f"preview_status: {preview_status}")
    lines.append(f"allowed_scope: {result['allowed_scope']}")
    lines.append(f"final_decision: {final_decision}")
    lines.append(f"next_action: {next_action}")
    lines.append(f"next_module: {next_module}")
    lines.append(f"direct_apply_recommended_now: {direct_apply_recommended_now}")
    lines.append("")
    lines.append("COUNTS")
    lines.append("-" * 100)
    lines.append(json.dumps(result["counts"], indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("CLASSIFICATION COUNTS")
    lines.append("-" * 100)
    lines.append(json.dumps(class_counts, indent=2, sort_keys=True, ensure_ascii=False))
    lines.append("")
    lines.append("METADATA PREVIEW POSSIBLE")
    lines.append("-" * 100)
    lines.append(json.dumps(possible, indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("METADATA PREVIEW BLOCKED")
    lines.append("-" * 100)
    lines.append(json.dumps(blocked, indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("RECOMMENDED POLICY")
    lines.append("-" * 100)
    lines.append(json.dumps(result["recommended_policy"], indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("FORBIDDEN ACTIONS")
    lines.append("-" * 100)
    for item in FORBIDDEN_ACTIONS:
        lines.append(f"- {item}")

    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"preview_status: {preview_status}")
    print(f"final_decision: {final_decision}")
    print(f"next_action: {next_action}")
    print(f"next_module: {next_module}")
    print(f"direct_apply_recommended_now: {direct_apply_recommended_now}")
    print("counts:")
    print(json.dumps(result["counts"], indent=2, ensure_ascii=False))
    print("classification_counts:")
    print(json.dumps(class_counts, indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()