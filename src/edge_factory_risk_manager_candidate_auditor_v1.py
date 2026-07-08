#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import py_compile
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(r"C:\Users\alike")
WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TARGET = SCRIPT_DIR / "global_paper_risk_manager_v4_config.py"

CANDIDATES = [
    SCRIPT_DIR / "global_paper_risk_manager_v3_priority.py",
    SCRIPT_DIR / "global_paper_risk_manager_v2.py",
    SCRIPT_DIR / "global_paper_risk_manager.py",
    SCRIPT_DIR / "Downloads" / "global_paper_risk_manager_v3_priority.py",
    SCRIPT_DIR / "Downloads" / "global_paper_risk_manager_v2.py",
    SCRIPT_DIR / "Downloads" / "global_paper_risk_manager.py",
]

REQUIRED_MARKERS = [
    "argparse",
    "base_dir",
    "max_global",
    "max_short",
    "max_long",
]

GOOD_MARKERS = [
    "old_short",
    "impulse_long",
    "market_relative",
    "weak_market",
    "priority",
    "paper",
    "risk",
]

FORBIDDEN_MARKERS = [
    "create_order",
    "market_order",
    "private_post",
    "apiKey",
    "apiSecret",
    "fetch_balance",
]

def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def compile_ok(path: Path):
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "OK"
    except Exception as e:
        return False, repr(e)

def run_help(path: Path):
    try:
        p = subprocess.run(
            [sys.executable, str(path), "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return {
            "executed": True,
            "return_code": p.returncode,
            "stdout_tail": p.stdout[-3000:],
            "stderr_tail": p.stderr[-3000:],
        }
    except Exception as e:
        return {
            "executed": False,
            "return_code": None,
            "stdout_tail": "",
            "stderr_tail": repr(e),
        }

def audit_candidate(path: Path):
    exists = path.exists()
    if not exists:
        return {
            "path": str(path),
            "exists": False,
            "score": -999,
            "recommendation": "MISSING",
        }

    ok, err = compile_ok(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    low = text.lower()

    required_hits = [m for m in REQUIRED_MARKERS if m.lower() in low]
    good_hits = [m for m in GOOD_MARKERS if m.lower() in low]
    forbidden_hits = [m for m in FORBIDDEN_MARKERS if m.lower() in low]

    help_result = run_help(path) if ok else {
        "executed": False,
        "return_code": None,
        "stdout_tail": "",
        "stderr_tail": "compile failed",
    }

    score = 0
    score += 50 if ok else -100
    score += len(required_hits) * 10
    score += len(good_hits) * 5
    score -= len(forbidden_hits) * 100

    if "v3_priority" in path.name:
        score += 20
    if help_result["executed"] and help_result["return_code"] in (0, 1, 2):
        score += 5

    if forbidden_hits:
        rec = "REJECT_FORBIDDEN_MARKERS"
    elif not ok:
        rec = "REJECT_COMPILE_FAIL"
    elif len(required_hits) >= 3:
        rec = "CANDIDATE_COMPATIBLE_ENOUGH_FOR_COPY_REVIEW"
    else:
        rec = "WEAK_CANDIDATE_NEEDS_MANUAL_REVIEW"

    return {
        "path": str(path),
        "exists": True,
        "compile_ok": ok,
        "compile_error": err,
        "required_hits": required_hits,
        "good_hits": good_hits,
        "forbidden_hits": forbidden_hits,
        "help": help_result,
        "score": score,
        "recommendation": rec,
    }

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    out_dir = WORKSPACE / "edge_factory_risk_manager_candidate_auditor_v1" / f"risk_manager_audit_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    results = [audit_candidate(p) for p in CANDIDATES]
    existing = [r for r in results if r.get("exists")]
    compatible = [
        r for r in existing
        if r.get("recommendation") == "CANDIDATE_COMPATIBLE_ENOUGH_FOR_COPY_REVIEW"
    ]
    compatible = sorted(compatible, key=lambda r: r.get("score", -999), reverse=True)

    best = compatible[0] if compatible else None

    applied = False
    backup_path = None
    if args.apply and best:
        backup_dir = out_dir / "backup"
        backup_dir.mkdir(parents=True, exist_ok=True)
        if TARGET.exists():
            backup_path = backup_dir / TARGET.name
            shutil.copy2(TARGET, backup_path)

        shutil.copy2(Path(best["path"]), TARGET)
        applied = True

    target_compile_ok = False
    target_compile_error = "target missing"
    if TARGET.exists():
        target_compile_ok, target_compile_error = compile_ok(TARGET)

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "target": str(TARGET),
        "target_exists_before": TARGET.exists() if not applied else False,
        "apply_requested": args.apply,
        "applied": applied,
        "backup_path": str(backup_path) if backup_path else None,
        "best_candidate": best,
        "target_exists_after": TARGET.exists(),
        "target_compile_ok": target_compile_ok,
        "target_compile_error": target_compile_error,
        "results": results,
        "ready_to_retry_launcher": bool(TARGET.exists() and target_compile_ok),
        "live_allowed": False,
        "hard_rules": [
            "No dummy risk manager is created.",
            "Only an existing real candidate may be copied.",
            "No paper/live is started.",
            "No active config or sizing contract is changed.",
        ],
    }

    (out_dir / "risk_manager_candidate_audit_state.json").write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("EDGE FACTORY RISK MANAGER CANDIDATE AUDITOR v1")
    print("=" * 100)
    print(f"target: {TARGET}")
    print(f"output_dir: {out_dir}")
    print(f"apply_requested: {args.apply}")
    print(f"applied: {applied}")
    print(f"target_exists_after: {TARGET.exists()}")
    print(f"target_compile_ok: {target_compile_ok}")
    print(f"ready_to_retry_launcher: {state['ready_to_retry_launcher']}")
    print("live_allowed: False")
    print()

    print("CANDIDATES")
    print("-" * 100)
    for r in sorted(results, key=lambda x: x.get("score", -999), reverse=True):
        print(f"score={r.get('score'):>4} exists={r.get('exists')} compile={r.get('compile_ok')} rec={r.get('recommendation')} path={r.get('path')}")
        if r.get("forbidden_hits"):
            print("   forbidden:", r.get("forbidden_hits"))
        if r.get("required_hits"):
            print("   required_hits:", r.get("required_hits"))
        if r.get("good_hits"):
            print("   good_hits:", r.get("good_hits"))

    print()
    if best:
        print("BEST CANDIDATE")
        print("-" * 100)
        print(best["path"])
        print("Run with --apply to copy it to:")
        print(TARGET)
    else:
        print("NO COMPATIBLE CANDIDATE FOUND")
        print("Do not retry launcher yet.")

    print()
    print(f"State: {out_dir / 'risk_manager_candidate_audit_state.json'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
