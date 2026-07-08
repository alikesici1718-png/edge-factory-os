#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_os_duplicate_launch_guard_v1"

COMPONENTS = {
    "risk_manager": ["global_paper_risk_manager_v4_config.py", "global_paper_risk_manager_v3_priority.py"],
    "old_short_logger": ["old_short_gate_aware_live_paper_logger.py"],
    "impulse_long_logger": ["impulse_long_gate_aware_live_paper_logger.py"],
    "market_relative_logger": ["market_relative_live_paper_logger.py"],
    "weak_market_logger": ["weak_market_breakdown_short_live_paper_logger.py"],
    "autopilot_v4": ["edge_factory_os_autopilot_loop_v4.py"],
}

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def get_processes() -> list[dict[str, Any]]:
    ps = r'''
Get-CimInstance Win32_Process |
Where-Object { $_.CommandLine -match "python|Python|powershell" } |
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
    out_dir = OUT_ROOT / f"duplicate_launch_guard_v1_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    procs = get_processes()
    rows = []

    for component, patterns in COMPONENTS.items():
        matches = []
        for proc in procs:
            cmd = str(proc.get("CommandLine") or "")
            if any(p.lower() in cmd.lower() for p in patterns):
                matches.append(proc)

        rows.append({
            "component": component,
            "running": len(matches) > 0,
            "process_count": len(matches),
            "pids": ", ".join(str(x.get("ProcessId")) for x in matches),
            "sample_command": str(matches[0].get("CommandLine"))[:700] if matches else "",
        })

    df = pd.DataFrame(rows)

    missing = df[df["running"] == False]["component"].tolist()

    # PowerShell parent + Python child often gives count=2 for logger windows.
    # That is acceptable. True duplicate danger is usually >2 for logger/risk components or >1 for autopilot_v4.
    duplicate_alerts = []

    for _, r in df.iterrows():
        comp = r["component"]
        count = int(r["process_count"])

        if comp == "autopilot_v4":
            if count > 1:
                duplicate_alerts.append(f"{comp}: process_count={count}")
        else:
            if count > 2:
                duplicate_alerts.append(f"{comp}: process_count={count}")

    if duplicate_alerts:
        status = "DUPLICATE_LAUNCH_GUARD_ATTENTION_DUPLICATES"
        launch_master_allowed = False
        launch_autopilot_allowed = False
        recommendation = "DO_NOT_START_NEW_MASTER_OR_AUTOPILOT; inspect duplicate processes first."
    elif missing:
        status = "DUPLICATE_LAUNCH_GUARD_ATTENTION_MISSING"
        launch_master_allowed = False
        launch_autopilot_allowed = "autopilot_v4" in missing
        recommendation = "Do not start full MASTER blindly. Start only missing component after manual review."
    else:
        status = "DUPLICATE_LAUNCH_GUARD_PASS_ALREADY_RUNNING"
        launch_master_allowed = False
        launch_autopilot_allowed = False
        recommendation = "MASTER and Autopilot are already running. Do not launch duplicates."

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "status": status,
        "missing": missing,
        "duplicate_alerts": duplicate_alerts,
        "launch_master_allowed": launch_master_allowed,
        "launch_autopilot_allowed": launch_autopilot_allowed,
        "recommendation": recommendation,
        "components": rows,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Read-only guard.",
            "Does not start processes.",
            "Does not stop processes.",
            "Does not modify MASTER.",
            "Does not place orders.",
        ],
    }

    state_path = out_dir / "edge_factory_os_duplicate_launch_guard_v1_state.json"
    csv_path = out_dir / "edge_factory_os_duplicate_launch_guard_v1_summary.csv"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    df.to_csv(csv_path, index=False)

    print("EDGE FACTORY OS DUPLICATE LAUNCH GUARD v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"status    : {status}")
    print(f"missing   : {missing}")
    print(f"duplicates: {duplicate_alerts}")
    print(f"launch_master_allowed   : {launch_master_allowed}")
    print(f"launch_autopilot_allowed: {launch_autopilot_allowed}")
    print(f"recommendation: {recommendation}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("COMPONENT SUMMARY")
    print("-" * 100)
    print(df.to_string(index=False))
    print()
    print(f"State: {state_path}")
    print(f"CSV  : {csv_path}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
