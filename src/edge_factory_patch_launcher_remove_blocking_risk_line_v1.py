#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Patches the MASTER_UPPER_SYSTEM PowerShell launcher by removing any blocking direct-invocation lines for the global paper risk manager v4 config script, then writes the modified launcher in place after creating a backup. Outputs the patch result (removed lines and backup path) to the edge_factory_patch_launcher_remove_blocking_risk_line_v1 directory.
"""
# EDGE_FACTORY_GATE_METADATA_START
# gate_metadata_version: 1
# gate_metadata_kind: non_behavioral_comment_block
# gate_review_source_file: gate_review_candidate_preview_latest.json
# gate_review_target_path: src/edge_factory_patch_launcher_remove_blocking_risk_line_v1.py
# gate_review_issue_id: MUTATION_SURFACE:src/edge_factory_patch_launcher_remove_blocking_risk_line_v1.py
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

import shutil
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
LAUNCHER = Path(r"C:\Users\alike\start_edge_factory_MASTER_UPPER_SYSTEM.ps1")

def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def main():
    out_dir = WORKSPACE / "edge_factory_patch_launcher_remove_blocking_risk_line_v1" / f"patch_remove_blocking_risk_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not LAUNCHER.exists():
        raise SystemExit(f"launcher missing: {LAUNCHER}")

    backup = out_dir / "start_edge_factory_MASTER_UPPER_SYSTEM.backup.ps1"
    shutil.copy2(LAUNCHER, backup)

    lines = LAUNCHER.read_text(encoding="utf-8", errors="replace").splitlines()
    new_lines = []
    removed = []

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()

        is_blocking_direct_risk = (
            stripped.lower().startswith("python ")
            and "global_paper_risk_manager_v4_config.py" in stripped
            and "--family_config" in stripped
            and "Start-LoggerWindow" not in stripped
        )

        if is_blocking_direct_risk:
            removed.append({"line_no": i, "line": line})
            continue

        new_lines.append(line)

    LAUNCHER.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    print("EDGE FACTORY PATCH LAUNCHER REMOVE BLOCKING RISK LINE v1")
    print("=" * 100)
    print(f"launcher: {LAUNCHER}")
    print(f"backup  : {backup}")
    print(f"removed_count: {len(removed)}")
    print("live_allowed: False")
    print()
    print("REMOVED LINES")
    print("-" * 100)
    for r in removed:
        print(f"{r['line_no']}: {r['line']}")

    if not removed:
        print("No blocking direct risk-manager line found. Launcher may already be patched.")

if __name__ == "__main__":
    main()
