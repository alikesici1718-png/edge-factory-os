#!/usr/bin/env python
# -*- coding: utf-8 -*-
# EDGE_FACTORY_GATE_METADATA_START
# gate_metadata_version: 1
# gate_metadata_kind: non_behavioral_comment_block
# gate_review_source_file: gate_review_candidate_preview_latest.json
# gate_review_target_path: src/edge_factory_master_gate_compatibility_repair_v2.py
# gate_review_issue_id: MUTATION_SURFACE:src/edge_factory_master_gate_compatibility_repair_v2.py
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

def backup_file(p: Path, backup_dir: Path) -> str | None:
    if not p.exists():
        return None
    backup_dir.mkdir(parents=True, exist_ok=True)
    dst = backup_dir / p.name
    shutil.copy2(p, dst)
    return str(dst)

def ensure_true_family_config(apply: bool) -> dict:
    desired = {k: str(v) for k, v in EXPECTED_FAMILY_DIRS.items()}
    before = read_json(TRUE_FAMILY_CONFIG)
    content_ok_before = before == desired

    if apply and not content_ok_before:
        TRUE_FAMILY_CONFIG.parent.mkdir(parents=True, exist_ok=True)
        TRUE_FAMILY_CONFIG.write_text(json.dumps(desired, indent=2), encoding="utf-8")

    after = read_json(TRUE_FAMILY_CONFIG)

    return {
        "path": str(TRUE_FAMILY_CONFIG),
        "content_ok_before": content_ok_before,
        "content_ok_after": after == desired,
        "patched": bool(apply and not content_ok_before),
        "desired": desired,
        "before": before,
        "after": after,
    }

def patch_logger_script(path: Path, apply: bool, backup_dir: Path) -> dict:
    if not path.exists():
        return {"script": str(path), "exists": False, "would_patch": False, "patched": False}

    s = read_text(path)
    lines = s.splitlines()
    has_gate_arg = any('ap.add_argument("--global_gate_path"' in line for line in lines)

    new_lines = []
    changed = False

    for line in lines:
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]

        if has_gate_arg and 'ap.add_argument("--global_gate_path"' in line:
            replacement = f'{indent}ap.add_argument("--global_gate_path", default=r"{TRUE_GATE_PATH}")'
            new_lines.append(replacement)
            if replacement != line:
                changed = True
            continue

        new_lines.append(line)

        if not has_gate_arg and 'ap.add_argument("--require_global_gate"' in line:
            insert = f'{indent}ap.add_argument("--global_gate_path", default=r"{TRUE_GATE_PATH}")'
            new_lines.append(insert)
            changed = True

    new_s = "\n".join(new_lines) + ("\n" if s.endswith("\n") else "")

    if apply and changed:
        backup_file(path, backup_dir)
        write_text(path, new_s)

    return {
        "script": str(path),
        "exists": True,
        "would_patch": changed,
        "patched": bool(apply and changed),
        "contains_true_gate_before": str(TRUE_GATE_PATH) in s,
        "contains_true_gate_after": str(TRUE_GATE_PATH) in new_s,
    }

def patch_logger_defaults(apply: bool, backup_dir: Path) -> list[dict]:
    return [patch_logger_script(p, apply, backup_dir) for p in LOGGER_SCRIPTS]

def patch_launcher(apply: bool, backup_dir: Path) -> dict:
    if not LAUNCHER.exists():
        return {"launcher": str(LAUNCHER), "exists": False, "would_patch": False, "patched": False}

    s = read_text(LAUNCHER)
    new_s = s

    # IMPORTANT: use lambda replacement to avoid Python interpreting C:\Users as regex escape.
    new_s = re.sub(
        r'--family_config\s+("[^"]*"|\'[^\']*\'|\S+)',
        lambda m: f'--family_config "{TRUE_FAMILY_CONFIG}"',
        new_s,
        flags=re.IGNORECASE,
    )

    new_s = re.sub(
        r'--global_gate_path\s+("[^"]*global_gate_decisions\.csv"|\'[^\']*global_gate_decisions\.csv\'|\S*global_gate_decisions\.csv)',
        lambda m: f'--global_gate_path "{TRUE_GATE_PATH}"',
        new_s,
        flags=re.IGNORECASE,
    )

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
        "contains_true_family_config_before": str(TRUE_FAMILY_CONFIG) in s,
        "contains_true_gate_before": str(TRUE_GATE_PATH) in s,
        "contains_true_family_config_after": str(TRUE_FAMILY_CONFIG) in new_s,
        "contains_true_gate_after": str(TRUE_GATE_PATH) in new_s,
    }

def audit_runtime_files() -> dict:
    out = {
        "true_family_config": str(TRUE_FAMILY_CONFIG),
        "true_gate_path": str(TRUE_GATE_PATH),
        "family_config_exists": TRUE_FAMILY_CONFIG.exists(),
        "gate_exists": TRUE_GATE_PATH.exists(),
        "gate_size": TRUE_GATE_PATH.stat().st_size if TRUE_GATE_PATH.exists() else 0,
        "families": {},
    }

    for fam, folder in EXPECTED_FAMILY_DIRS.items():
        pending = folder / "pending_entries.csv"
        openp = folder / "open_positions.csv"
        rejected = folder / "rejected_entries.csv"

        def rows(p: Path):
            if not p.exists() or p.stat().st_size == 0:
                return 0
            try:
                return int(len(pd.read_csv(p)))
            except Exception:
                return -1

        out["families"][fam] = {
            "folder": str(folder),
            "folder_exists": folder.exists(),
            "pending_rows": rows(pending),
            "open_rows": rows(openp),
            "rejected_rows": rows(rejected),
        }

    return out

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    out_dir = WORKSPACE / "edge_factory_master_gate_compatibility_repair_v2" / f"master_gate_repair_v2_{stamp()}"
    backup_dir = out_dir / "backup"
    out_dir.mkdir(parents=True, exist_ok=True)

    family_result = ensure_true_family_config(args.apply)
    logger_results = patch_logger_defaults(args.apply, backup_dir)
    launcher_result = patch_launcher(args.apply, backup_dir)
    audit = audit_runtime_files()

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "apply": args.apply,
        "base": str(BASE),
        "true_family_config": str(TRUE_FAMILY_CONFIG),
        "true_gate_path": str(TRUE_GATE_PATH),
        "family_result": family_result,
        "logger_results": logger_results,
        "launcher_result": launcher_result,
        "audit": audit,
        "active_paper_allowed": False,
        "live_allowed": False,
        "important": [
            "This module does not start/stop processes.",
            "This module does not create dummy gate decisions.",
            "It only aligns family_config and logger global_gate_path.",
            "Restart MASTER_UPPER_SYSTEM after --apply."
        ],
    }

    state_path = out_dir / "master_gate_compatibility_repair_v2_state.json"
    csv_path = out_dir / "master_gate_compatibility_repair_v2_loggers.csv"
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    pd.DataFrame(logger_results).to_csv(csv_path, index=False)

    print("EDGE FACTORY MASTER GATE COMPATIBILITY REPAIR v2")
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
    print("FAMILY CONFIG RESULT")
    print("-" * 100)
    print(json.dumps(family_result, indent=2, ensure_ascii=False, default=str))
    print()
    print("LAUNCHER RESULT")
    print("-" * 100)
    print(json.dumps(launcher_result, indent=2, ensure_ascii=False, default=str))
    print()
    print("LOGGER RESULTS")
    print("-" * 100)
    print(pd.DataFrame(logger_results).to_string(index=False))
    print()
    print("AUDIT")
    print("-" * 100)
    print(json.dumps(audit, indent=2, ensure_ascii=False, default=str))
    print()
    print(f"State: {state_path}")
    print(f"CSV  : {csv_path}")
    print()

    if not args.apply:
        print("DRY RUN ONLY. If contains_true_*_after values are True, run:")
        print(f'python -u "{Path(__file__)}" --apply')
    else:
        print("PATCH APPLIED. Restart MASTER_UPPER_SYSTEM because current processes still use old args.")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
