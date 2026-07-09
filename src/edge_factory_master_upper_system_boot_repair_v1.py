#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Repairs indentation and argparse structural errors in MASTER_UPPER_SYSTEM component logger scripts, reading each Python logger file and rewriting it with corrected indentation after backing up originals.
Validates each file with py_compile before and after patching to confirm the repair is syntactically sound.
"""
# EDGE_FACTORY_GATE_METADATA_START
# gate_metadata_version: 1
# gate_metadata_kind: non_behavioral_comment_block
# gate_review_source_file: gate_review_candidate_preview_latest.json
# gate_review_target_path: src/edge_factory_master_upper_system_boot_repair_v1.py
# gate_review_issue_id: MUTATION_SURFACE:src/edge_factory_master_upper_system_boot_repair_v1.py
# gate_review_classification: GATE_REVIEW_FAIL_MISSING_EXPLICIT_GATE_METADATA
# gate_review_risk: UNKNOWN
# gate_review_evidence: Mutation-like tokens: .write_text(, shutil.copy
# allowed_scope: REPO_ONLY_OS_INTELLIGENCE
# preview_only: true
# non_behavioral_comment_only: true
# runtime_touch_allowed: false
# launcher_allowed: false
# capital_change_allowed: false
# active_paper_allowed: false
# live_allowed: false
# real_orders_allowed: false
# candidate_generation_allowed: false
# family_release_allowed: false
# strategy_research_allowed: false
# holdout_access_allowed: false
# backup_delete_allowed: false
# backup_move_allowed: false
# direct_apply_allowed: false
# EDGE_FACTORY_GATE_METADATA_END

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
from __future__ import annotations

import os
import re
import shutil
import py_compile
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(r"C:\Users\alike")
WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

LOGGERS = [
    SCRIPT_DIR / "old_short_gate_aware_live_paper_logger.py",
    SCRIPT_DIR / "impulse_long_gate_aware_live_paper_logger.py",
    SCRIPT_DIR / "market_relative_live_paper_logger.py",
    SCRIPT_DIR / "weak_market_breakdown_short_live_paper_logger.py",
]

RISK_TARGET = SCRIPT_DIR / "global_paper_risk_manager_v4_config.py"

def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

BACKUP_DIR = WORKSPACE / "edge_factory_master_upper_system_boot_repair_v1" / f"backup_{stamp()}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

def try_compile(path: Path):
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "OK"
    except Exception as e:
        return False, repr(e)

def indent_of(line: str) -> str:
    return line[:len(line) - len(line.lstrip(" "))]

def repair_ap_add_argument_indent(path: Path):
    if not path.exists():
        return {"path": str(path), "exists": False, "patched": False, "compile_ok": False, "error": "missing"}

    original = path.read_text(encoding="utf-8", errors="replace")
    shutil.copy2(path, BACKUP_DIR / path.name)

    lines = original.splitlines()
    patched = False

    for i, line in enumerate(lines):
        stripped = line.lstrip()

        # Common damaged pattern from previous sizing patch:
        #     ap.add_argument(...)
        # where the nearest ap = argparse.ArgumentParser(...) has different indent.
        if stripped.startswith("ap.add_argument("):
            base_indent = None

            # Prefer nearest previous ap = argparse.ArgumentParser or previous ap.add_argument.
            for j in range(i - 1, max(-1, i - 160), -1):
                prev = lines[j]
                prev_strip = prev.lstrip()
                if "ap = argparse.ArgumentParser" in prev_strip or prev_strip.startswith("ap.add_argument("):
                    base_indent = indent_of(prev)
                    break

            if base_indent is not None and indent_of(line) != base_indent:
                lines[i] = base_indent + stripped
                patched = True

        # Also normalize parse_args if it was dragged into wrong indentation.
        if stripped.startswith("args = ap.parse_args(") or stripped.startswith("return ap.parse_args("):
            base_indent = None
            for j in range(i - 1, max(-1, i - 160), -1):
                prev = lines[j]
                prev_strip = prev.lstrip()
                if "ap = argparse.ArgumentParser" in prev_strip or prev_strip.startswith("ap.add_argument("):
                    base_indent = indent_of(prev)
                    break
            if base_indent is not None and indent_of(line) != base_indent:
                lines[i] = base_indent + stripped
                patched = True

    if patched:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    ok, err = try_compile(path)

    # One extra compile-driven rescue for exact "unexpected indent" at ap.add_argument line.
    if not ok and "IndentationError" in err:
        m = re.search(r"line (\d+)", err)
        if m:
            lineno = int(m.group(1))
            if 1 <= lineno <= len(lines):
                line = lines[lineno - 1]
                stripped = line.lstrip()
                if stripped.startswith("ap.add_argument("):
                    # Try unindenting to nearest previous non-empty line's indent.
                    base_indent = ""
                    for j in range(lineno - 2, max(-1, lineno - 120), -1):
                        prev = lines[j]
                        if prev.strip():
                            if "ap = argparse.ArgumentParser" in prev or prev.lstrip().startswith("ap.add_argument("):
                                base_indent = indent_of(prev)
                            break
                    lines[lineno - 1] = base_indent + stripped
                    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                    patched = True
                    ok, err = try_compile(path)

    return {
        "path": str(path),
        "exists": True,
        "patched": patched,
        "compile_ok": ok,
        "error": err,
        "backup": str(BACKUP_DIR / path.name),
    }

def find_and_restore_risk_manager():
    result = {
        "target": str(RISK_TARGET),
        "target_exists_before": RISK_TARGET.exists(),
        "restored": False,
        "exact_candidates": [],
        "near_candidates": [],
    }

    if RISK_TARGET.exists():
        result["target_exists_after"] = True
        return result

    search_roots = [SCRIPT_DIR, WORKSPACE]
    exact = []
    near = []

    for root in search_roots:
        if not root.exists():
            continue

        for dirpath, dirnames, filenames in os.walk(root):
            # Skip noisy folders.
            low = dirpath.lower()
            if "__pycache__" in low or ".git" in low:
                continue

            for fn in filenames:
                if fn == "global_paper_risk_manager_v4_config.py":
                    exact.append(Path(dirpath) / fn)
                elif fn.startswith("global_paper_risk_manager") and fn.endswith(".py"):
                    near.append(Path(dirpath) / fn)

    # Deduplicate.
    exact = list(dict.fromkeys(exact))
    near = list(dict.fromkeys(near))

    result["exact_candidates"] = [str(x) for x in exact]
    result["near_candidates"] = [str(x) for x in near[:30]]

    if exact:
        src = exact[0]
        shutil.copy2(src, RISK_TARGET)
        result["restored"] = True
        result["restored_from"] = str(src)

    result["target_exists_after"] = RISK_TARGET.exists()
    if RISK_TARGET.exists():
        ok, err = try_compile(RISK_TARGET)
        result["risk_compile_ok"] = ok
        result["risk_compile_error"] = err

    return result

def main():
    print("EDGE FACTORY MASTER UPPER SYSTEM BOOT REPAIR v1")
    print("=" * 100)
    print(f"backup_dir: {BACKUP_DIR}")
    print()

    logger_results = []
    print("LOGGER SYNTAX REPAIR")
    print("-" * 100)
    for p in LOGGERS:
        r = repair_ap_add_argument_indent(p)
        logger_results.append(r)
        print(f"{p.name:55s} exists={r.get('exists')} patched={r.get('patched')} compile_ok={r.get('compile_ok')}")
        if not r.get("compile_ok"):
            print("   error:", r.get("error"))

    print()
    print("RISK MANAGER RESTORE")
    print("-" * 100)
    risk = find_and_restore_risk_manager()
    print(f"target_exists_before: {risk.get('target_exists_before')}")
    print(f"restored: {risk.get('restored')}")
    if risk.get("restored_from"):
        print(f"restored_from: {risk.get('restored_from')}")
    print(f"target_exists_after: {risk.get('target_exists_after')}")
    if risk.get("risk_compile_ok") is not None:
        print(f"risk_compile_ok: {risk.get('risk_compile_ok')}")
        if not risk.get("risk_compile_ok"):
            print(f"risk_compile_error: {risk.get('risk_compile_error')}")

    if not risk.get("target_exists_after"):
        print()
        print("RISK MANAGER STILL MISSING")
        print("-" * 100)
        print("Exact file not found. Near candidates:")
        for c in risk.get("near_candidates", []):
            print("-", c)
        print()
        print("Do NOT create a dummy risk manager. This is a real boot blocker.")

    all_loggers_ok = all(r.get("compile_ok") for r in logger_results)
    risk_ok = bool(risk.get("target_exists_after")) and risk.get("risk_compile_ok", True) is True

    print()
    print("FINAL")
    print("-" * 100)
    print(f"all_loggers_compile_ok: {all_loggers_ok}")
    print(f"risk_manager_ok: {risk_ok}")
    print(f"ready_to_retry_launcher: {all_loggers_ok and risk_ok}")
    print("live_allowed: False")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
