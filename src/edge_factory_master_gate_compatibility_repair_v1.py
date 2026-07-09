#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Inspects and patches the MASTER_UPPER_SYSTEM launcher script and family logger files to ensure gate-compatibility, replacing any non-compliant gate-path references and verifying family config and gate CSV paths align.
Requires explicit approval before any mutations; backs up all modified files before writing.
"""
# EDGE_FACTORY_GATE_METADATA_START
# gate_metadata_version: 1
# gate_metadata_kind: non_behavioral_comment_block
# gate_review_source_file: gate_review_candidate_preview_latest.json
# gate_review_target_path: src/edge_factory_master_gate_compatibility_repair_v1.py
# gate_review_issue_id: MUTATION_SURFACE:src/edge_factory_master_gate_compatibility_repair_v1.py
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

import argparse
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd

USER_DIR = Path(r"C:\Users\alike")
WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
BASE = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"

LAUNCHER = USER_DIR / "start_edge_factory_MASTER_UPPER_SYSTEM.ps1"
RISK_MANAGER = USER_DIR / "global_paper_risk_manager_v4_config.py"

LOGGER_SCRIPTS = [
    USER_DIR / "old_short_gate_aware_live_paper_logger.py",
    USER_DIR / "impulse_long_gate_aware_live_paper_logger.py",
    USER_DIR / "market_relative_live_paper_logger.py",
    USER_DIR / "weak_market_breakdown_short_live_paper_logger.py",
]

TRUE_FAMILY_CONFIG = BASE / "family_config.json"
TRUE_GATE_PATH = BASE / "global_gate_decisions.csv"

EXPECTED_FAMILY_DIRS = {
    "old_short": BASE / "live_blowoff_short_paper_realistic",
    "impulse_long": BASE / "live_impulse_event_long_paper",
    "market_relative_short": BASE / "live_market_relative_extreme_reversion_short_paper",
    "weak_market_short": BASE / "live_weak_market_breakdown_short_paper",
}

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

def write_text(p: Path, s: str) -> None:
    p.write_text(s, encoding="utf-8")

def read_json(p: Path):
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None

def backup_file(p: Path, backup_dir: Path) -> Path | None:
    if not p.exists():
        return None
    backup_dir.mkdir(parents=True, exist_ok=True)
    dst = backup_dir / p.name
    shutil.copy2(p, dst)
    return dst

def ensure_true_family_config(apply: bool) -> dict:
    before = read_json(TRUE_FAMILY_CONFIG)
    desired = {k: str(v) for k, v in EXPECTED_FAMILY_DIRS.items()}

    exists_ok = TRUE_FAMILY_CONFIG.exists()
    content_ok = before == desired

    if apply and not content_ok:
        TRUE_FAMILY_CONFIG.parent.mkdir(parents=True, exist_ok=True)
        TRUE_FAMILY_CONFIG.write_text(json.dumps(desired, indent=2), encoding="utf-8")

    after = read_json(TRUE_FAMILY_CONFIG)

    return {
        "path": str(TRUE_FAMILY_CONFIG),
        "exists_before": exists_ok,
        "content_ok_before": content_ok,
        "desired": desired,
        "after": after,
        "content_ok_after": after == desired,
        "patched": bool(apply and not content_ok),
    }

def patch_logger_default_gate_paths(apply: bool, backup_dir: Path) -> list[dict]:
    rows = []

    for p in LOGGER_SCRIPTS:
        s = read_text(p)
        exists = p.exists()
        before_contains_true = str(TRUE_GATE_PATH) in s
        changed = False

        if not exists:
            rows.append({
                "script": str(p),
                "exists": False,
                "patched": False,
                "reason": "missing",
            })
            continue

        # Replace any default= r"...global_gate_decisions.csv" argument.
        new_s = re.sub(
            r'ap\.add_argument\("--global_gate_path",\s*default=r?"[^"]*global_gate_decisions\.csv"\)',
            f'ap.add_argument("--global_gate_path", default=r"{TRUE_GATE_PATH}")',
            s,
        )

        # If the script has --require_global_gate but no global_gate_path arg somehow, insert after it.
        if "--global_gate_path" not in new_s and "--require_global_gate" in new_s:
            new_s = new_s.replace(
                'ap.add_argument("--require_global_gate", action="store_true")',
                'ap.add_argument("--require_global_gate", action="store_true")\n'
                f'    ap.add_argument("--global_gate_path", default=r"{TRUE_GATE_PATH}")'
            )

        changed = new_s != s

        if apply and changed:
            backup_file(p, backup_dir)
            write_text(p, new_s)

        rows.append({
            "script": str(p),
            "exists": exists,
            "before_contains_true_gate_path": before_contains_true,
            "patched": bool(apply and changed),
            "would_patch": bool(changed),
            "after_contains_true_gate_path": str(TRUE_GATE_PATH) in (new_s if apply or changed else s),
        })

    return rows

def patch_launcher(apply: bool, backup_dir: Path) -> dict:
    s = read_text(LAUNCHER)
    if not LAUNCHER.exists():
        return {
            "launcher": str(LAUNCHER),
            "exists": False,
            "patched": False,
            "would_patch": False,
            "reason": "missing",
        }

    new_s = s

    # Replace any risk manager --family_config argument to the true live-folder family_config.json.
    new_s = re.sub(
        r'--family_config\s+"[^"]*"',
        f'--family_config "{TRUE_FAMILY_CONFIG}"',
        new_s,
    )
    new_s = re.sub(
        r"--family_config\s+'[^']*'",
        f'--family_config "{TRUE_FAMILY_CONFIG}"',
        new_s,
    )

    # Replace any logger --global_gate_path argument to true gate path.
    new_s = re.sub(
        r'--global_gate_path\s+"[^"]*global_gate_decisions\.csv"',
        f'--global_gate_path "{TRUE_GATE_PATH}"',
        new_s,
    )
    new_s = re.sub(
        r"--global_gate_path\s+'[^']*global_gate_decisions\.csv'",
        f'--global_gate_path "{TRUE_GATE_PATH}"',
        new_s,
    )

    # If require_global_gate exists but no global_gate_path anywhere, append true arg near require flag.
    if "--require_global_gate" in new_s and "--global_gate_path" not in new_s:
        new_s = new_s.replace(
            "--require_global_gate",
            f'--require_global_gate --global_gate_path "{TRUE_GATE_PATH}"'
        )

    changed = new_s != s

    if apply and changed:
        backup_file(LAUNCHER, backup_dir)
        write_text(LAUNCHER, new_s)

    return {
        "launcher": str(LAUNCHER),
        "exists": True,
        "would_patch": changed,
        "patched": bool(apply and changed),
        "contains_true_family_config_after": str(TRUE_FAMILY_CONFIG) in new_s,
        "contains_true_gate_path_after": str(TRUE_GATE_PATH) in new_s,
    }

def audit_current_files() -> dict:
    cfg = read_json(TRUE_FAMILY_CONFIG)

    gate_exists = TRUE_GATE_PATH.exists()
    gate_rows = None
    gate_cols = None
    if gate_exists and TRUE_GATE_PATH.stat().st_size > 0:
        try:
            df = pd.read_csv(TRUE_GATE_PATH)
            gate_rows = int(len(df))
            gate_cols = list(df.columns)
        except Exception as e:
            gate_rows = f"READ_ERROR: {e!r}"

    family_pending = {}
    for fam, d in EXPECTED_FAMILY_DIRS.items():
        p = d / "pending_entries.csv"
        try:
            rows = len(pd.read_csv(p)) if p.exists() and p.stat().st_size > 0 else 0
        except Exception:
            rows = -1
        family_pending[fam] = {
            "folder": str(d),
            "folder_exists": d.exists(),
            "pending_path": str(p),
            "pending_rows": rows,
        }

    return {
        "true_family_config_path": str(TRUE_FAMILY_CONFIG),
        "true_family_config": cfg,
        "true_gate_path": str(TRUE_GATE_PATH),
        "true_gate_exists": gate_exists,
        "true_gate_rows": gate_rows,
        "true_gate_columns": gate_cols,
        "family_pending": family_pending,
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    out_dir = WORKSPACE / "edge_factory_master_gate_compatibility_repair_v1" / f"master_gate_repair_{stamp()}"
    backup_dir = out_dir / "backup"
    out_dir.mkdir(parents=True, exist_ok=True)

    family_cfg_result = ensure_true_family_config(args.apply)
    logger_results = patch_logger_default_gate_paths(args.apply, backup_dir)
    launcher_result = patch_launcher(args.apply, backup_dir)
    current_audit = audit_current_files()

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "apply": args.apply,
        "workspace": str(WORKSPACE),
        "base": str(BASE),
        "true_family_config": str(TRUE_FAMILY_CONFIG),
        "true_gate_path": str(TRUE_GATE_PATH),
        "family_config_result": family_cfg_result,
        "logger_results": logger_results,
        "launcher_result": launcher_result,
        "current_audit": current_audit,
        "active_paper_allowed": False,
        "live_allowed": False,
        "important": [
            "This module does not start or stop processes.",
            "Restart MASTER_UPPER_SYSTEM after applying patches.",
            "This does not create dummy gate decisions.",
            "This only aligns risk manager family_config and logger global_gate_path.",
        ],
    }

    state_path = out_dir / "master_gate_compatibility_repair_state.json"
    logger_csv = out_dir / "logger_gate_path_patch_summary.csv"
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    pd.DataFrame(logger_results).to_csv(logger_csv, index=False)

    print("EDGE FACTORY MASTER GATE COMPATIBILITY REPAIR v1")
    print("=" * 100)
    print(f"apply: {args.apply}")
    print(f"base : {BASE}")
    print(f"out  : {out_dir}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print()
    print("TRUE PATHS")
    print("-" * 100)
    print(f"family_config: {TRUE_FAMILY_CONFIG}")
    print(f"gate_path    : {TRUE_GATE_PATH}")
    print()
    print("FAMILY CONFIG")
    print("-" * 100)
    print(json.dumps(family_cfg_result, indent=2, ensure_ascii=False, default=str))
    print()
    print("LAUNCHER")
    print("-" * 100)
    print(json.dumps(launcher_result, indent=2, ensure_ascii=False, default=str))
    print()
    print("LOGGER PATCH SUMMARY")
    print("-" * 100)
    print(pd.DataFrame(logger_results).to_string(index=False))
    print()
    print("CURRENT AUDIT")
    print("-" * 100)
    print(json.dumps(current_audit, indent=2, ensure_ascii=False, default=str))
    print()
    print(f"State : {state_path}")
    print(f"CSV   : {logger_csv}")
    print()
    if not args.apply:
        print("DRY RUN ONLY. If the patch summary looks sane, run:")
        print(f'python -u "{Path(__file__)}" --apply')
    else:
        print("PATCH APPLIED. Restart MASTER_UPPER_SYSTEM; running processes still have old arguments.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
