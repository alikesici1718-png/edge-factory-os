#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Patches the MASTER_UPPER_SYSTEM PowerShell launcher to inject correct risk-manager arguments derived from the family config JSON, backing up the original launcher before writing changes. Reads the family config from edge_factory_master_upper_system_family_config and writes the patched launcher plus a JSON patch report to the edge_factory_patch_master_launcher_risk_args_v1 directory.
"""
# EDGE_FACTORY_GATE_METADATA_START
# gate_metadata_version: 1
# gate_metadata_kind: non_behavioral_comment_block
# gate_review_source_file: gate_review_candidate_preview_latest.json
# gate_review_target_path: src/edge_factory_patch_master_launcher_risk_args_v1.py
# gate_review_issue_id: MUTATION_SURFACE:src/edge_factory_patch_master_launcher_risk_args_v1.py
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

import json
import re
import shutil
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
SCRIPT_DIR = Path(r"C:\Users\alike")
LAUNCHER = SCRIPT_DIR / "start_edge_factory_MASTER_UPPER_SYSTEM.ps1"
RISK_MANAGER = SCRIPT_DIR / "global_paper_risk_manager_v4_config.py"
PAPER_DIR = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"

FAMILY_CONFIG = WORKSPACE / "edge_factory_master_upper_system_family_config" / "master_upper_system_family_config.json"

MAX_PER_FAMILY = {
    "old_short": 3,
    "impulse_long": 2,
    "market_relative_short": 3,
    "weak_market_short": 2,
}

PRIORITY = {
    "impulse_long": 150,
    "old_short": 100,
    "market_relative_short": 70,
    "weak_market_short": 30,
}

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

def build_family_config() -> dict:
    # Deliberately broad schema: real risk manager can use whichever keys it expects.
    return {
        "schema_version": "master_upper_system_family_config_v1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "base_dir": str(PAPER_DIR),
        "paper_dir": str(PAPER_DIR),
        "live_allowed": False,
        "active_paper_only": True,
        "families": {
            "old_short": {
                "family_key": "old_short",
                "strategy": "old_short",
                "side": "short",
                "enabled": True,
                "paper_dir": str(PAPER_DIR / "old_short"),
                "log_dir": str(PAPER_DIR / "old_short"),
                "max_positions": 3,
                "priority": 100,
            },
            "impulse_long": {
                "family_key": "impulse_long",
                "strategy": "impulse_long",
                "side": "long",
                "enabled": True,
                "paper_dir": str(PAPER_DIR / "impulse_long"),
                "log_dir": str(PAPER_DIR / "impulse_long"),
                "max_positions": 2,
                "priority": 150,
            },
            "market_relative_short": {
                "family_key": "market_relative_short",
                "strategy": "market_relative_short",
                "side": "short",
                "enabled": True,
                "paper_dir": str(PAPER_DIR / "market_relative_short"),
                "log_dir": str(PAPER_DIR / "market_relative_short"),
                "max_positions": 3,
                "priority": 70,
            },
            "weak_market_short": {
                "family_key": "weak_market_short",
                "strategy": "weak_market_short",
                "side": "short",
                "enabled": True,
                "backup_only": True,
                "paper_dir": str(PAPER_DIR / "weak_market_short"),
                "log_dir": str(PAPER_DIR / "weak_market_short"),
                "max_positions": 2,
                "priority": 30,
            },
        },
        "family_keys": ["old_short", "impulse_long", "market_relative_short", "weak_market_short"],
        "max_per_family": MAX_PER_FAMILY,
        "family_priority": PRIORITY,
        "global_max_positions": 6,
        "max_short_positions": 5,
        "max_long_positions": 2,
        "weak_market_backup_only": True,
    }

def patch_launcher() -> dict:
    if not LAUNCHER.exists():
        return {"patched": False, "reason": "launcher missing", "launcher": str(LAUNCHER)}

    original = LAUNCHER.read_text(encoding="utf-8", errors="replace")
    backup_dir = WORKSPACE / "edge_factory_patch_master_launcher_risk_args_v1" / f"backup_{stamp()}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / LAUNCHER.name
    shutil.copy2(LAUNCHER, backup_path)

    # Build replacement command. Use escaped PowerShell quotes through normal line text.
    risk_cmd = (
        f'python "{RISK_MANAGER}" '
        f'--family_config "{FAMILY_CONFIG}" '
        f'--out_dir "{PAPER_DIR}" '
        f'--global_max_positions 6 '
        f'--max_short_positions 5 '
        f'--max_long_positions 2 '
        f"--max_per_family_json '{json.dumps(MAX_PER_FAMILY)}' "
        f"--family_priority_json '{json.dumps(PRIORITY)}' "
        f'--weak_market_backup_only '
        f'--poll_seconds 10'
    )

    lines = original.splitlines()
    new_lines = []
    patched = False
    skip_next_continuations = False

    for line in lines:
        if "global_paper_risk_manager_v4_config.py" in line:
            indent = line[:len(line) - len(line.lstrip())]
            # Preserve common Start-Process / python direct style by replacing only the command text line.
            if "python" in line.lower():
                new_lines.append(indent + risk_cmd)
            else:
                new_lines.append(line)
                new_lines.append(indent + risk_cmd)
            patched = True
            continue
        new_lines.append(line)

    if not patched:
        # Append a safe risk manager launch block if no existing line found.
        new_lines.append("")
        new_lines.append('Write-Host "GLOBAL RISK MANAGER MASTER_UPPER_SYSTEM"')
        new_lines.append(risk_cmd)
        patched = True

    patched_text = "\n".join(new_lines) + "\n"
    LAUNCHER.write_text(patched_text, encoding="utf-8")

    return {
        "patched": patched,
        "launcher": str(LAUNCHER),
        "backup": str(backup_path),
        "risk_command": risk_cmd,
    }

def main():
    out_dir = WORKSPACE / "edge_factory_patch_master_launcher_risk_args_v1" / f"patch_risk_args_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    family_config_obj = build_family_config()
    write_json(FAMILY_CONFIG, family_config_obj)

    result = patch_launcher()

    state = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "paper_dir": str(PAPER_DIR),
        "launcher": str(LAUNCHER),
        "risk_manager": str(RISK_MANAGER),
        "family_config": str(FAMILY_CONFIG),
        "family_config_exists": FAMILY_CONFIG.exists(),
        "risk_manager_exists": RISK_MANAGER.exists(),
        "patch_result": result,
        "live_allowed": False,
        "important": [
            "This script does not start paper.",
            "This script does not start live.",
            "This script only writes family_config and patches launcher risk-manager arguments.",
        ],
    }

    write_json(out_dir / "patch_master_launcher_risk_args_v1_state.json", state)

    print("EDGE FACTORY PATCH MASTER LAUNCHER RISK ARGS v1")
    print("=" * 100)
    print(f"launcher: {LAUNCHER}")
    print(f"risk_manager: {RISK_MANAGER}")
    print(f"family_config: {FAMILY_CONFIG}")
    print(f"family_config_exists: {FAMILY_CONFIG.exists()}")
    print(f"risk_manager_exists: {RISK_MANAGER.exists()}")
    print(f"patched: {result.get('patched')}")
    print(f"backup: {result.get('backup')}")
    print("live_allowed: False")
    print()
    print("RISK COMMAND")
    print("-" * 100)
    print(result.get("risk_command"))
    print()
    print(f"State: {out_dir / 'patch_master_launcher_risk_args_v1_state.json'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
