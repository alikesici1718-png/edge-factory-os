#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

REAL_V3 = Path(r"C:\Users\alike\global_paper_risk_manager_v3_priority.py")
OUT_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_MASTER_UPPER_SYSTEM")
FAMILY_CONFIG = OUT_DIR / "family_config.json"

MAX_PER_FAMILY = {"old_short": 3, "impulse_long": 2, "market_relative_short": 3, "weak_market_short": 2}
FAMILY_PRIORITY = {"impulse_long": 150, "old_short": 100, "market_relative_short": 70, "weak_market_short": 30}

def drop_legacy_args(args: list[str]) -> list[str]:
    cleaned = []
    skip_next = False
    for arg in args:
        if skip_next:
            skip_next = False
            continue
        if arg == "--config":
            skip_next = True
            continue
        cleaned.append(arg)
    return cleaned

def main():
    if not REAL_V3.exists():
        raise SystemExit(f"REAL risk manager missing: {REAL_V3}")

    original_args = drop_legacy_args(sys.argv[1:])
    if "--family_config" in original_args and "--out_dir" in original_args:
        new_args = [str(REAL_V3), *original_args]
    else:
        # Compatibility fallback for older launchers that called this wrapper with
        # stale or unsupported flags such as --config.
        keep_once = "--once" in original_args
        new_args = [
            str(REAL_V3),
            "--family_config", str(FAMILY_CONFIG),
            "--out_dir", str(OUT_DIR),
            "--global_max_positions", "6",
            "--max_short_positions", "5",
            "--max_long_positions", "2",
            "--max_per_family_json", json.dumps(MAX_PER_FAMILY),
            "--family_priority_json", json.dumps(FAMILY_PRIORITY),
            "--weak_market_backup_only",
            "--pending_grace_minutes", "180",
            "--poll_seconds", "10",
        ]
        if keep_once:
            new_args.append("--once")

    sys.argv = new_args
    return runpy.run_path(str(REAL_V3), run_name="__main__")

if __name__ == "__main__":
    main()
