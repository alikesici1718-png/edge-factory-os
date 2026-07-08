#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
edge_factory_os_bom_syntax_repair_preview_v1

Read-only preview: leading UTF-8 BOM (U+FEFF) removal for tools/*.py only.
Does not modify source files, run launcher, or touch runtime.
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]

AUDIT_JSON = (
    REPO_ROOT
    / "edge_factory_os_full_system_read_only_audit"
    / "full_system_read_only_audit_latest.json"
)

OUT_DIR = REPO_ROOT / "edge_factory_os_bom_syntax_repair_preview"
OUT_JSON = OUT_DIR / "bom_syntax_repair_preview_latest.json"
OUT_TXT = OUT_DIR / "bom_syntax_repair_preview_latest.txt"


SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only": True,
    "runtime_touch_allowed": False,
    "launcher_allowed": False,
    "runtime_patch_allowed": False,
    "patch_apply_allowed_now": False,
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
}

FORBIDDEN_ACTIONS: List[str] = [
    "Do not modify target Python files from this module.",
    "Do not run launcher.",
    "Do not touch runtime.",
    "Do not change capital.",
    "Do not enable active paper.",
    "Do not enable live trading.",
    "Do not enable real orders.",
    "Do not delete or move backup files.",
    "Do not change .gitignore.",
    "Do not use git add -f.",
]


@dataclass
class FilePreviewRow:
    path: str
    bom_confirmed_at_start: bool
    before_byte_len: int
    after_byte_len: int
    syntax_after_preview_ok: bool
    preview_safe: bool
    block_reason: str
    compile_error: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel_repo(p: Path) -> str:
    try:
        return str(p.relative_to(REPO_ROOT)).replace("\\", "/")
    except Exception:
        return str(p).replace("\\", "/")


def run_cmd(args: List[str], timeout: int = 30) -> Dict[str, Any]:
    try:
        proc = subprocess.run(
            args,
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except Exception as exc:
        return {"ok": False, "returncode": None, "stdout": "", "stderr": repr(exc)}


def git_state() -> Dict[str, Any]:
    st = run_cmd(["git", "-C", str(REPO_ROOT), "status", "--short"])
    head = run_cmd(["git", "-C", str(REPO_ROOT), "rev-parse", "--short", "HEAD"])
    last = run_cmd(["git", "-C", str(REPO_ROOT), "log", "-1", "--pretty=%h %s"])
    lines = [x.strip().replace("\\", "/") for x in st["stdout"].splitlines() if x.strip()]
    return {
        "status_ok": st["ok"],
        "head_short": head["stdout"].strip() if head["ok"] else None,
        "last_commit": last["stdout"].strip() if last["ok"] else None,
        "git_status_lines": lines,
        "untracked_or_dirty_count": len(lines),
    }


def load_audit() -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    if not AUDIT_JSON.is_file():
        return None, "audit_json_missing"
    try:
        with AUDIT_JSON.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return (data if isinstance(data, dict) else None), None
    except Exception as exc:
        return None, f"audit_json_unreadable:{exc!r}"


def extract_bom_tool_paths(issue_inventory: Any) -> List[str]:
    out: List[str] = []
    if not isinstance(issue_inventory, list):
        return out
    for row in issue_inventory:
        if not isinstance(row, dict):
            continue
        if row.get("category") != "python_syntax_errors":
            continue
        ev = row.get("evidence")
        if not isinstance(ev, str) or "\ufeff" not in ev and "U+FEFF" not in ev:
            continue
        p = row.get("path")
        if not isinstance(p, str) or not p.startswith("tools/"):
            continue
        out.append(p.replace("\\", "/"))
    # stable unique order
    seen = set()
    uniq: List[str] = []
    for p in out:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def preview_one(rel_path: str) -> FilePreviewRow:
    path = (REPO_ROOT / rel_path.replace("/", "\\")).resolve()
    rp = rel_path
    if not path.is_file():
        return FilePreviewRow(
            path=rp,
            bom_confirmed_at_start=False,
            before_byte_len=0,
            after_byte_len=0,
            syntax_after_preview_ok=False,
            preview_safe=False,
            block_reason="file_missing_on_disk",
            compile_error="",
        )
    try:
        raw = path.read_bytes()
    except Exception as exc:
        return FilePreviewRow(
            path=rp,
            bom_confirmed_at_start=False,
            before_byte_len=0,
            after_byte_len=0,
            syntax_after_preview_ok=False,
            preview_safe=False,
            block_reason=f"read_bytes_failed:{exc!r}",
            compile_error="",
        )
    before_len = len(raw)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return FilePreviewRow(
            path=rp,
            bom_confirmed_at_start=False,
            before_byte_len=before_len,
            after_byte_len=0,
            syntax_after_preview_ok=False,
            preview_safe=False,
            block_reason=f"utf8_decode_failed:{exc!r}",
            compile_error="",
        )

    bom_ok = len(text) > 0 and text[0] == "\ufeff"
    if not bom_ok:
        return FilePreviewRow(
            path=rp,
            bom_confirmed_at_start=False,
            before_byte_len=before_len,
            after_byte_len=before_len,
            syntax_after_preview_ok=False,
            preview_safe=False,
            block_reason="leading_bom_not_confirmed_first_char",
            compile_error="",
        )

    new_text = text[1:]
    after_len = len(new_text.encode("utf-8"))
    compile_err = ""
    syntax_ok = False
    try:
        compile(new_text, rp, "exec", dont_inherit=True)
        syntax_ok = True
    except SyntaxError as exc:
        compile_err = str(exc)

    preview_safe = syntax_ok
    block_reason = "" if preview_safe else ("syntax_error_after_bom_strip:" + compile_err[:500])

    return FilePreviewRow(
        path=rp,
        bom_confirmed_at_start=True,
        before_byte_len=before_len,
        after_byte_len=after_len,
        syntax_after_preview_ok=syntax_ok,
        preview_safe=preview_safe,
        block_reason=block_reason if not preview_safe else "",
        compile_error=compile_err[:1500] if compile_err else "",
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gs = git_state()
    audit, audit_err = load_audit()

    rows: List[FilePreviewRow] = []
    audit_meta: Dict[str, Any] = {
        "audit_path": rel_repo(AUDIT_JSON),
        "audit_loaded": audit is not None,
        "audit_error": audit_err,
    }
    if audit:
        audit_meta["audit_status"] = audit.get("audit_status")
        audit_meta["issue_count"] = audit.get("issue_count")

    candidate_paths: List[str] = []
    if audit is not None:
        candidate_paths = extract_bom_tool_paths(audit.get("issue_inventory"))

    for rp in candidate_paths:
        rows.append(preview_one(rp))

    candidate_count = len(rows)
    safe_preview_count = sum(1 for r in rows if r.preview_safe)
    unsafe_preview_count = candidate_count - safe_preview_count
    files_safe_to_repair = [r.path for r in rows if r.preview_safe]
    files_blocked = [
        {"path": r.path, "block_reason": r.block_reason or "not_safe", "compile_error": r.compile_error}
        for r in rows
        if not r.preview_safe
    ]

    if audit_err == "audit_json_missing":
        preview_status = "BOM_SYNTAX_REPAIR_PREVIEW_BLOCKED_AUDIT_MISSING"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        final_decision = "STOP_PROVIDE_FULL_SYSTEM_READ_ONLY_AUDIT_JSON_FIRST"
        next_action = "RUN_FULL_SYSTEM_READ_ONLY_AUDIT_THEN_RE_RUN_PREVIEW"
        next_module = "edge_factory_os_full_system_read_only_audit_v1.py"
    elif audit_err:
        preview_status = "BOM_SYNTAX_REPAIR_PREVIEW_BLOCKED_AUDIT_UNREADABLE"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        final_decision = "STOP_FIX_AUDIT_JSON_INPUT"
        next_action = "STOP_NO_FILE_MUTATION"
        next_module = "edge_factory_os_full_system_read_only_audit_v1.py"
    elif candidate_count == 0:
        preview_status = "BOM_SYNTAX_REPAIR_PREVIEW_READY_NO_APPLY"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        final_decision = "NO_BOM_TOOL_CANDIDATES_FROM_AUDIT_FILTER"
        next_action = "STOP_OR_RE_RUN_AUDIT_IF_SYNTAX_ERRORS_EXPECTED"
        next_module = None
    elif unsafe_preview_count == 0:
        preview_status = "BOM_SYNTAX_REPAIR_PREVIEW_READY_NO_APPLY"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        final_decision = "BUILD_BOM_SYNTAX_REPAIR_APPLY_NEXT_IF_PREVIEW_SAFE"
        next_action = "BUILD_APPLY_MODULE_DO_NOT_APPLY_FROM_PREVIEW"
        next_module = "edge_factory_os_bom_syntax_repair_apply_v1.py"
    else:
        preview_status = "BOM_SYNTAX_REPAIR_PREVIEW_READY_NO_APPLY"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        final_decision = "PARTIAL_PREVIEW_REVIEW_BLOCKED_FILES_BEFORE_APPLY"
        next_action = "FIX_BLOCKED_PATHS_OR_ADJUST_SCOPE_THEN_RE_PREVIEW"
        next_module = "edge_factory_os_bom_syntax_repair_apply_v1.py"

    payload: Dict[str, Any] = {
        "module": "edge_factory_os_bom_syntax_repair_preview_v1.py",
        "generated_at_utc": now_iso(),
        "preview_status": preview_status,
        "allowed_scope": allowed_scope,
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "candidate_count": candidate_count,
        "safe_preview_count": safe_preview_count,
        "unsafe_preview_count": unsafe_preview_count,
        "files_safe_to_repair": files_safe_to_repair,
        "files_blocked": files_blocked,
        "per_file_preview": [r.to_dict() for r in rows],
        "audit_input_meta": audit_meta,
        "candidate_paths_from_audit": candidate_paths,
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "git_state": gs,
        "outputs": {"json": str(OUT_JSON), "txt": str(OUT_TXT)},
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    txt_lines = [
        "Edge Factory OS — BOM syntax repair PREVIEW (no apply)",
        f"generated_at_utc: {payload['generated_at_utc']}",
        f"preview_status: {preview_status}",
        f"allowed_scope: {allowed_scope}",
        f"final_decision: {final_decision}",
        f"next_action: {next_action}",
        f"next_module: {next_module}",
        f"candidate_count: {candidate_count}",
        f"safe_preview_count: {safe_preview_count}",
        f"unsafe_preview_count: {unsafe_preview_count}",
        "",
        "files_safe_to_repair:",
        json.dumps(files_safe_to_repair, indent=2, ensure_ascii=False),
        "",
        "files_blocked:",
        json.dumps(files_blocked, indent=2, ensure_ascii=False),
        "",
        "per_file_preview:",
        json.dumps(payload["per_file_preview"], indent=2, ensure_ascii=False),
        "",
        "safety_flags:",
        json.dumps(SAFETY_FLAGS, indent=2, sort_keys=True, ensure_ascii=False),
        "",
        "git_state:",
        json.dumps(gs, indent=2, ensure_ascii=False),
    ]
    OUT_TXT.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
