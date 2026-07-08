from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]

PREVIEW_JSON = (
    REPO_ROOT
    / "edge_factory_os_bom_syntax_repair_preview"
    / "bom_syntax_repair_preview_latest.json"
)

OUT_DIR = REPO_ROOT / "edge_factory_os_bom_syntax_repair_apply"
OUT_JSON = OUT_DIR / "bom_syntax_repair_apply_latest.json"
OUT_TXT = OUT_DIR / "bom_syntax_repair_apply_latest.txt"

REQUIRED_PREVIEW_STATUS = "BOM_SYNTAX_REPAIR_PREVIEW_READY_NO_APPLY"
REQUIRED_PREVIEW_FINAL_DECISION = "BUILD_BOM_SYNTAX_REPAIR_APPLY_NEXT_IF_PREVIEW_SAFE"

UTF8_BOM_BYTES = b"\xef\xbb\xbf"


SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only": True,
    "guarded_repo_mutation_only": True,
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
    "pycache_allowed": False,
    "imports_allowed": False,
    "target_module_execution_allowed": False,
}

FORBIDDEN_ACTIONS: List[str] = [
    "Do not run launcher.",
    "Do not touch runtime.",
    "Do not run strategy research.",
    "Do not generate candidates.",
    "Do not change capital.",
    "Do not enable active paper.",
    "Do not enable live trading.",
    "Do not enable or send real orders.",
    "Do not delete or move backup files.",
    "Do not change .gitignore.",
    "Do not use git add -f.",
    "Do not import target modules.",
    "Do not execute target modules.",
    "Do not write .pyc or create __pycache__.",
]


@dataclass
class BomChangeRecord:
    relative_path: str
    before_sha256: str
    after_sha256: str
    before_byte_len: int
    after_byte_len: int
    removed_prefix: str
    syntax_after_apply_ok: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel_repo(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def is_under_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(REPO_ROOT.resolve())
        return True
    except Exception:
        return False


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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

    lines = st["stdout"].splitlines() if st["ok"] else []
    lines = [x.strip().replace("\\", "/") for x in lines if x.strip()]

    return {
        "status_ok": st["ok"],
        "head_short": head["stdout"].strip() if head["ok"] else None,
        "last_commit": last["stdout"].strip() if last["ok"] else None,
        "git_status_lines": lines,
        "untracked_or_dirty_count": len(lines),
        "backup_like_untracked_or_dirty": [
            x for x in lines
            if ".bak" in x
            or "_bak_" in x
            or "blocked_patch_bak" in x
            or "readonly_fix_bak" in x
            or ".guarded_reenable_bak_" in x
        ],
        "universe_guard_in_status": any(
            "tools/edge_factory_os_universe_coverage_guard_v1.py" in x
            for x in lines
        ),
    }


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def syntax_compile_check(source: str, filename: str) -> Optional[str]:
    try:
        compile(source, filename, "exec", dont_inherit=True)
        return None
    except SyntaxError as exc:
        return str(exc)


def validate_preview(preview: Optional[Dict[str, Any]]) -> Tuple[bool, List[str], List[str], Dict[str, Any]]:
    errors: List[str] = []
    files: List[str] = []

    detail: Dict[str, Any] = {
        "preview_path": rel_repo(PREVIEW_JSON),
        "preview_loaded": preview is not None,
    }

    if preview is None:
        return False, ["PREVIEW_JSON_MISSING_OR_UNREADABLE"], files, detail

    preview_status = preview.get("preview_status")
    final_decision = preview.get("final_decision")
    candidate_count = preview.get("candidate_count")
    safe_preview_count = preview.get("safe_preview_count")
    unsafe_preview_count = preview.get("unsafe_preview_count")
    files_safe = preview.get("files_safe_to_repair")

    detail.update({
        "preview_status": preview_status,
        "required_preview_status": REQUIRED_PREVIEW_STATUS,
        "final_decision": final_decision,
        "required_final_decision": REQUIRED_PREVIEW_FINAL_DECISION,
        "candidate_count": candidate_count,
        "safe_preview_count": safe_preview_count,
        "unsafe_preview_count": unsafe_preview_count,
    })

    if preview_status != REQUIRED_PREVIEW_STATUS:
        errors.append("PREVIEW_STATUS_MISMATCH")

    if final_decision != REQUIRED_PREVIEW_FINAL_DECISION:
        errors.append("PREVIEW_FINAL_DECISION_MISMATCH")

    if unsafe_preview_count != 0:
        errors.append(f"UNSAFE_PREVIEW_COUNT_NOT_ZERO:{unsafe_preview_count}")

    if not isinstance(files_safe, list):
        errors.append("FILES_SAFE_TO_REPAIR_NOT_LIST")
        return False, errors, files, detail

    for item in files_safe:
        if not isinstance(item, str):
            errors.append("FILES_SAFE_TO_REPAIR_CONTAINS_NON_STRING")
            continue
        norm = item.replace("\\", "/")
        if not norm.startswith("tools/") or not norm.endswith(".py"):
            errors.append(f"UNSAFE_PATH_SCOPE:{norm}")
            continue
        files.append(norm)

    deduped: List[str] = []
    seen = set()
    for f in files:
        if f not in seen:
            seen.add(f)
            deduped.append(f)

    if len(deduped) != len(files):
        errors.append("DUPLICATE_FILES_SAFE_TO_REPAIR")

    files = deduped

    if safe_preview_count != len(files):
        errors.append(f"SAFE_PREVIEW_COUNT_MISMATCH:observed={safe_preview_count}:files={len(files)}")

    if candidate_count != len(files):
        errors.append(f"CANDIDATE_COUNT_MISMATCH:observed={candidate_count}:files={len(files)}")

    if not files:
        errors.append("NO_SAFE_FILES_TO_REPAIR")

    return len(errors) == 0, errors, files, detail


def plan_one_file(rel_path: str) -> Tuple[Optional[BomChangeRecord], Optional[bytes], Optional[str]]:
    path = (REPO_ROOT / rel_path.replace("/", "\\")).resolve()

    if not is_under_repo(path):
        return None, None, f"path_not_under_repo:{rel_path}"

    if not path.is_file():
        return None, None, f"file_missing:{rel_path}"

    try:
        raw = path.read_bytes()
    except Exception as exc:
        return None, None, f"read_bytes_failed:{rel_path}:{exc!r}"

    before_len = len(raw)

    if not raw.startswith(UTF8_BOM_BYTES):
        return None, None, f"utf8_bom_bytes_not_at_start:{rel_path}"

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return None, None, f"utf8_decode_failed:{rel_path}:{exc!r}"

    if not text or text[0] != "\ufeff":
        return None, None, f"leading_ufeff_not_confirmed:{rel_path}"

    new_text = text[1:]
    new_bytes = new_text.encode("utf-8")

    # Ultra-strict content preservation check:
    # the after bytes must equal original bytes after the 3-byte UTF-8 BOM.
    if new_bytes != raw[len(UTF8_BOM_BYTES):]:
        return None, None, f"content_preservation_check_failed:{rel_path}"

    compile_err = syntax_compile_check(new_text, rel_path)
    if compile_err:
        return None, None, f"syntax_after_bom_strip_failed:{rel_path}:{compile_err}"

    rec = BomChangeRecord(
        relative_path=rel_path,
        before_sha256=sha256_bytes(raw),
        after_sha256=sha256_bytes(new_bytes),
        before_byte_len=before_len,
        after_byte_len=len(new_bytes),
        removed_prefix="UTF8_BOM_EF_BB_BF",
        syntax_after_apply_ok=True,
    )

    return rec, new_bytes, None


def write_outputs(result: Dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    lines: List[str] = []
    lines.append("EDGE FACTORY OS BOM SYNTAX REPAIR APPLY v1")
    lines.append("=" * 100)
    lines.append(f"apply_status: {result['apply_status']}")
    lines.append(f"allowed_scope: {result['allowed_scope']}")
    lines.append(f"final_decision: {result['final_decision']}")
    lines.append(f"next_action: {result['next_action']}")
    lines.append(f"next_module: {result['next_module']}")
    lines.append(f"changed_file_count: {result['changed_file_count']}")
    lines.append("")
    lines.append("PREVIEW VALIDATION")
    lines.append("-" * 100)
    lines.append(json.dumps(result["preview_validation"], indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("CHANGED FILES")
    lines.append("-" * 100)
    lines.append(json.dumps(result["changed_files"], indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("BLOCK REASONS")
    lines.append("-" * 100)
    if result["block_reasons"]:
        for item in result["block_reasons"]:
            lines.append(str(item))
    else:
        lines.append("none")
    lines.append("")
    lines.append("ROLLBACK")
    lines.append("-" * 100)
    lines.append(json.dumps(result["rollback"], indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    lines.append(json.dumps(result["safety_flags"], indent=2, sort_keys=True, ensure_ascii=False))
    lines.append("")
    lines.append("FORBIDDEN ACTIONS")
    lines.append("-" * 100)
    for item in result["forbidden_actions"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("GIT STATE")
    lines.append("-" * 100)
    lines.append(json.dumps(result["git_state"], indent=2, ensure_ascii=False))

    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    generated_at = now_iso()
    gs_before = git_state()
    preview = load_json(PREVIEW_JSON)

    preview_ok, preview_errors, files_to_repair, preview_detail = validate_preview(preview)

    block_reasons: List[str] = []
    changed_records: List[BomChangeRecord] = []
    planned_after_bytes: Dict[str, bytes] = {}

    apply_status = "BOM_SYNTAX_REPAIR_APPLY_BLOCKED"
    allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
    final_decision = "STOP_REVIEW_BOM_PREVIEW_OR_FILE_DRIFT"
    next_action = "STOP_NO_FILE_MUTATION_REVIEW_PREVIEW"
    next_module = "edge_factory_os_bom_syntax_repair_preview_v1.py"

    rollback_info: Dict[str, Any] = {
        "rollback_performed": False,
        "rollback_reason": "",
        "rollback_restored_files": [],
    }

    if not preview_ok:
        block_reasons.extend(preview_errors)
    else:
        snapshots: Dict[str, bytes] = {}

        for rel_path in files_to_repair:
            rec, new_bytes, err = plan_one_file(rel_path)
            if err:
                block_reasons.append(err)
                continue
            assert rec is not None
            assert new_bytes is not None
            changed_records.append(rec)
            planned_after_bytes[rel_path] = new_bytes

        if len(changed_records) != len(files_to_repair):
            block_reasons.append(
                f"PLANNED_CHANGE_COUNT_MISMATCH:planned={len(changed_records)}:expected={len(files_to_repair)}"
            )

        if not block_reasons:
            try:
                # Snapshot all first.
                for rel_path in files_to_repair:
                    path = (REPO_ROOT / rel_path.replace("/", "\\")).resolve()
                    snapshots[rel_path] = path.read_bytes()

                # Write after all validations passed.
                for rel_path, new_bytes in planned_after_bytes.items():
                    path = (REPO_ROOT / rel_path.replace("/", "\\")).resolve()
                    path.write_bytes(new_bytes)

                # Post-write validation.
                for rec in changed_records:
                    path = (REPO_ROOT / rec.relative_path.replace("/", "\\")).resolve()
                    after_raw = path.read_bytes()
                    if sha256_bytes(after_raw) != rec.after_sha256:
                        raise RuntimeError(f"post_write_hash_mismatch:{rec.relative_path}")

                    after_text = after_raw.decode("utf-8")
                    compile_err = syntax_compile_check(after_text, rec.relative_path)
                    if compile_err:
                        raise RuntimeError(f"post_write_syntax_failed:{rec.relative_path}:{compile_err}")

                apply_status = "BOM_SYNTAX_REPAIR_APPLIED"
                allowed_scope = "GUARDED_REPO_MUTATION_ONLY"
                final_decision = "RUN_FULL_SYSTEM_READ_ONLY_AUDIT_AGAIN"
                next_action = "RERUN_FULL_SYSTEM_READ_ONLY_AUDIT_TO_CONFIRM_CRITICAL_REDUCTION"
                next_module = "edge_factory_os_full_system_read_only_audit_v1.py"

            except Exception as exc:
                rollback_info["rollback_performed"] = True
                rollback_info["rollback_reason"] = repr(exc)
                for rel_path, original_bytes in snapshots.items():
                    path = (REPO_ROOT / rel_path.replace("/", "\\")).resolve()
                    try:
                        path.write_bytes(original_bytes)
                        rollback_info["rollback_restored_files"].append(rel_path)
                    except Exception as rb_exc:
                        block_reasons.append(f"ROLLBACK_FAILED:{rel_path}:{rb_exc!r}")

                block_reasons.append(f"APPLY_FAILED_AND_ROLLBACK_ATTEMPTED:{exc!r}")
                changed_records = []
                apply_status = "BOM_SYNTAX_REPAIR_APPLY_BLOCKED"
                allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
                final_decision = "STOP_REVIEW_BOM_PREVIEW_OR_FILE_DRIFT"
                next_action = "STOP_NO_FILE_MUTATION_REVIEW_PREVIEW"
                next_module = "edge_factory_os_bom_syntax_repair_preview_v1.py"

    result: Dict[str, Any] = {
        "module": "edge_factory_os_bom_syntax_repair_apply_v1.py",
        "generated_at_utc": generated_at,
        "repo_root": str(REPO_ROOT),
        "apply_status": apply_status,
        "allowed_scope": allowed_scope,
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "changed_file_count": len(changed_records) if apply_status == "BOM_SYNTAX_REPAIR_APPLIED" else 0,
        "planned_file_count": len(files_to_repair),
        "preview_validation": {
            "ok": preview_ok,
            "errors": preview_errors,
            "detail": preview_detail,
        },
        "changed_files": [
            rec.to_dict() for rec in changed_records
        ] if apply_status == "BOM_SYNTAX_REPAIR_APPLIED" else [],
        "block_reasons": block_reasons,
        "rollback": rollback_info,
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "git_state": gs_before,
        "outputs": {
            "json": str(OUT_JSON),
            "txt": str(OUT_TXT),
        },
    }

    write_outputs(result)

    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_TXT}")
    print(f"apply_status={apply_status}")
    print(f"changed_file_count={result['changed_file_count']}")


if __name__ == "__main__":
    main()
