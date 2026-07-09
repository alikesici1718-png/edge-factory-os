#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Backup snapshot of the process watchdog (autopilot v4 era, 2026-05-11) that checks whether expected Edge Factory OS processes are running and writes a watchdog state report. Functionally identical to edge_factory_os_process_watchdog_v1 but targets the v3-only autopilot process set.
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_os_process_watchdog_v1"

EXPECTED = {
    "risk_manager": ["global_paper_risk_manager_v4_config.py", "global_paper_risk_manager_v3_priority.py"],
    "old_short_logger": ["old_short_gate_aware_live_paper_logger.py"],
    "impulse_long_logger": ["impulse_long_gate_aware_live_paper_logger.py"],
    "market_relative_logger": ["market_relative_live_paper_logger.py"],
    "weak_market_logger": ["weak_market_breakdown_short_live_paper_logger.py"],
    "autopilot_v3": ["edge_factory_os_autopilot_loop_v3.py"],
}

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def get_python_processes() -> list[dict[str, Any]]:
    ps = r'''
Get-CimInstance Win32_Process |
Where-Object { $_.CommandLine -match "python|Python" } |
Select-Object ProcessId,Name,CommandLine |
ConvertTo-Json -Depth 4
'''
    p = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps],
        capture_output=True,
        text=True,
        timeout=30,
    )

    if p.returncode != 0 or not p.stdout.strip():
        return []

    try:
        obj = json.loads(p.stdout)
    except Exception:
        return []

    if isinstance(obj, dict):
        return [obj]
    if isinstance(obj, list):
        return obj
    return []

def main() -> int:
    out_dir = OUT_ROOT / f"os_process_watchdog_v1_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    procs = get_python_processes()
    rows = []

    for key, patterns in EXPECTED.items():
        matches = []
        for proc in procs:
            cmd = str(proc.get("CommandLine") or "")
            if any(pat.lower() in cmd.lower() for pat in patterns):
                matches.append(proc)

        rows.append({
            "component": key,
            "expected_patterns": " | ".join(patterns),
            "running": len(matches) > 0,
            "process_count": len(matches),
            "pids": ", ".join(str(x.get("ProcessId")) for x in matches),
            "sample_command": str(matches[0].get("CommandLine"))[:500] if matches else "",
        })

    df = pd.DataFrame(rows)

    missing = df[df["running"] == False]["component"].tolist()

    if missing:
        status = "PROCESS_WATCHDOG_ATTENTION_MISSING_COMPONENTS"
        severity = "ATTENTION"
    else:
        status = "PROCESS_WATCHDOG_PASS"
        severity = "OK"

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "status": status,
        "severity": severity,
        "missing_components": missing,
        "components": rows,
        "all_python_process_count": len(procs),
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Read-only process watchdog.",
            "Does not start processes.",
            "Does not stop processes.",
            "Does not modify files except its own reports.",
            "Does not place orders.",
        ],
        "recovery_commands": {
            "start_master": 'powershell -ExecutionPolicy Bypass -File "C:\\Users\\alike\\start_edge_factory_MASTER_UPPER_SYSTEM.ps1"',
            "start_autopilot_v3": 'python -u "C:\\Users\\alike\\edge_factory_os_autopilot_loop_v3.py" --interval_seconds 300 --safe_execute',
        }
    }

    state_path = out_dir / "edge_factory_os_process_watchdog_v1_state.json"
    csv_path = out_dir / "edge_factory_os_process_watchdog_v1_summary.csv"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    df.to_csv(csv_path, index=False)

    print("EDGE FACTORY OS PROCESS WATCHDOG v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"status    : {status}")
    print(f"severity  : {severity}")
    print(f"missing   : {missing}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("PROCESS SUMMARY")
    print("-" * 100)
    print(df.to_string(index=False))
    print()
    print(f"State: {state_path}")
    print(f"CSV  : {csv_path}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
