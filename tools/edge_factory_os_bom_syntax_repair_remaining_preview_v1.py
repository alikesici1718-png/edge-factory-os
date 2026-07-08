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

OUT_DIR = REPO_ROOT / "edge_factory_os_bom_syntax_repair_remaining_preview"
OUT_JSON = OUT_DIR / "bom_syntax_repair_remaining_preview_latest.json"
OUT_TXT = OUT_DIR / "bom_syntax_repair_remaining_preview_latest.txt"

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

@dataclass
class PreviewRow:
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
        p = subprocess.run(
            args,
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {"ok": p.returncode == 0, "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
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
        data = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None, None
    except Exception as exc:
        return None, f"audit_json_unreadable:{exc!r}"


def extract_bom_paths(issue_inventory: Any) -> List[str]:
    out: List[str] = []
    if not isinstance(issue_inventory, list):
        return out

    for row in issue_inventory:
        if not isinstance(row, dict):
            continue
        if row.get("category") != "python_syntax_errors":
            continue

        evidence = row.get("evidence")
        if not isinstance(evidence, str):
            continue
        if "U+FEFF" not in evidence and "\ufeff" not in evidence:
            continue

        p = row.get("path")
        if not isinstance(p, str):
            continue

        p = p.replace("\\", "/")
        if not (p.startswith("src/") or p.startswith("tools/")):
            continue
        if not p.endswith(".py"):
            continue

        out.append(p)

    seen = set()
    uniq: List[str] = []
    for p in out:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def preview_one(rel_path: str) -> PreviewRow:
    path = (REPO_ROOT / rel_path.replace("/", "\\")).resolve()

    if not path.is_file():
        return PreviewRow(rel_path, False, 0, 0, False, False, "file_missing_on_disk", "")

    try:
        raw = path.read_bytes()
    except Exception as exc:
        return PreviewRow(rel_path, False, 0, 0, False, False, f"read_failed:{exc!r}", "")

    before_len = len(raw)

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return PreviewRow(rel_path, False, before_len, 0, False, False, f"utf8_decode_failed:{exc!r}", "")

    if not text or text[0] != "\ufeff":
        return PreviewRow(rel_path, False, before_len, before_len, False, False, "leading_bom_not_confirmed", "")

    new_text = text[1:]
    new_raw = new_text.encode("utf-8")
    compile_error = ""
    syntax_ok = False

    try:
        compile(new_text, rel_path, "exec", dont_inherit=True)
        syntax_ok = True
    except SyntaxError as exc:
        compile_error = str(exc)

    return PreviewRow(
        path=rel_path,
        bom_confirmed_at_start=True,
        before_byte_len=before_len,
        after_byte_len=len(new_raw),
        syntax_after_preview_ok=syntax_ok,
        preview_safe=syntax_ok,
        block_reason="" if syntax_ok else "syntax_error_after_bom_strip",
        compile_error=compile_error,
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    audit, audit_err = load_audit()
    candidate_paths: List[str] = []

    if audit is not None:
        candidate_paths = extract_bom_paths(audit.get("issue_inventory"))

    rows = [preview_one(p) for p in candidate_paths]

    candidate_count = len(rows)
    safe_preview_count = sum(1 for r in rows if r.preview_safe)
    unsafe_preview_count = candidate_count - safe_preview_count

    files_safe_to_repair = [r.path for r in rows if r.preview_safe]
    files_blocked = [
        {"path": r.path, "block_reason": r.block_reason, "compile_error": r.compile_error}
        for r in rows if not r.preview_safe
    ]

    if audit_err:
        preview_status = "BOM_SYNTAX_REPAIR_REMAINING_PREVIEW_BLOCKED_AUDIT_INPUT"
        final_decision = "STOP_FIX_AUDIT_INPUT"
        next_action = "STOP_NO_FILE_MUTATION"
        next_module = "edge_factory_os_full_system_read_only_audit_v1.py"
    elif candidate_count == 0:
        preview_status = "BOM_SYNTAX_REPAIR_REMAINING_PREVIEW_READY_NO_APPLY"
        final_decision = "NO_REMAINING_BOM_CANDIDATES"
        next_action = "RERUN_AUDIT_OR_STOP"
        next_module = None
    elif unsafe_preview_count == 0:
        preview_status = "BOM_SYNTAX_REPAIR_REMAINING_PREVIEW_READY_NO_APPLY"
        final_decision = "BUILD_REMAINING_BOM_SYNTAX_REPAIR_APPLY_NEXT_IF_PREVIEW_SAFE"
        next_action = "BUILD_APPLY_MODULE_FOR_REMAINING_BOM_ONLY"
        next_module = "edge_factory_os_bom_syntax_repair_remaining_apply_v1.py"
    else:
        preview_status = "BOM_SYNTAX_REPAIR_REMAINING_PREVIEW_READY_NO_APPLY"
        final_decision = "PARTIAL_PREVIEW_REVIEW_BLOCKED_FILES_BEFORE_APPLY"
        next_action = "REVIEW_UNSAFE_PREVIEW_ROWS"
        next_module = "edge_factory_os_bom_syntax_repair_remaining_apply_v1.py"

    payload: Dict[str, Any] = {
        "module": "edge_factory_os_bom_syntax_repair_remaining_preview_v1.py",
        "generated_at_utc": now_iso(),
        "preview_status": preview_status,
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "candidate_count": candidate_count,
        "safe_preview_count": safe_preview_count,
        "unsafe_preview_count": unsafe_preview_count,
        "files_safe_to_repair": files_safe_to_repair,
        "files_blocked": files_blocked,
        "per_file_preview": [r.to_dict() for r in rows],
        "audit_input": {
            "path": rel_repo(AUDIT_JSON),
            "loaded": audit is not None,
            "error": audit_err,
            "audit_status": audit.get("audit_status") if audit else None,
            "critical_issue_count": audit.get("critical_issue_count") if audit else None,
        },
        "safety_flags": SAFETY_FLAGS,
        "git_state": git_state(),
        "outputs": {"json": str(OUT_JSON), "txt": str(OUT_TXT)},
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    txt = [
        "EDGE FACTORY OS REMAINING BOM SYNTAX REPAIR PREVIEW v1",
        "=" * 100,
        f"preview_status: {preview_status}",
        f"candidate_count: {candidate_count}",
        f"safe_preview_count: {safe_preview_count}",
        f"unsafe_preview_count: {unsafe_preview_count}",
        f"final_decision: {final_decision}",
        f"next_module: {next_module}",
        "",
        "files_safe_to_repair:",
        json.dumps(files_safe_to_repair, indent=2, ensure_ascii=False),
        "",
        "files_blocked:",
        json.dumps(files_blocked, indent=2, ensure_ascii=False),
        "",
        "safety_flags:",
        json.dumps(SAFETY_FLAGS, indent=2, sort_keys=True, ensure_ascii=False),
    ]
    OUT_TXT.write_text("\n".join(txt) + "\n", encoding="utf-8")

    print(f"preview_status: {preview_status}")
    print(f"candidate_count: {candidate_count}")
    print(f"safe_preview_count: {safe_preview_count}")
    print(f"unsafe_preview_count: {unsafe_preview_count}")
    print(f"next_module: {next_module}")


if __name__ == "__main__":
    main()
