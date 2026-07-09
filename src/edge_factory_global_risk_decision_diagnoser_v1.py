#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnoses global risk decision state by reading the risk manager config, global gate decisions CSV, risk snapshot, and violations files from the MASTER_UPPER_SYSTEM paper run directory. Runs the risk manager script via subprocess and writes a risk decision diagnosis report with pending entry counts, gate status, and family priority configuration.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

USERDIR = Path(r"C:\Users\alike")
WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
RUN = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"

RISK_MANAGER = USERDIR / "global_paper_risk_manager_v4_config.py"
FAMILY_CONFIG = RUN / "family_config.json"
GATE = RUN / "global_gate_decisions.csv"
SNAPSHOT = RUN / "global_risk_snapshot.csv"
VIOLATIONS = RUN / "global_risk_violations.csv"

MAX_PER_FAMILY_JSON = '{"old_short":3,"impulse_long":2,"market_relative_short":3,"weak_market_short":2}'
FAMILY_PRIORITY_JSON = '{"impulse_long":150,"old_short":100,"market_relative_short":70,"weak_market_short":30}'

def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def read_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"READ_ERROR": repr(e)}

def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception as e:
        return pd.DataFrame({"READ_ERROR": [repr(e)]})

def due_summary(path: Path) -> dict:
    df = read_csv(path)
    now = pd.Timestamp.now(tz="UTC")

    out = {
        "path": str(path),
        "exists": path.exists(),
        "rows": int(len(df)),
        "due_rows": 0,
        "future_rows": 0,
        "oldest_target": None,
        "newest_target": None,
        "columns": list(df.columns) if not df.empty else [],
    }

    if df.empty:
        return out

    target_col = None
    for c in ["target_entry_time", "entry_time", "planned_entry_time"]:
        if c in df.columns:
            target_col = c
            break

    if not target_col:
        out["warning"] = "no target time column"
        return out

    ts = pd.to_datetime(df[target_col], errors="coerce", utc=True)
    out["due_rows"] = int((ts.notna() & (ts <= now)).sum())
    out["future_rows"] = int((ts.notna() & (ts > now)).sum())
    out["oldest_target"] = str(ts.min()) if ts.notna().any() else None
    out["newest_target"] = str(ts.max()) if ts.notna().any() else None
    return out

def process_lines():
    ps = r'''
Get-CimInstance Win32_Process |
Where-Object { $_.CommandLine -match "global_paper_risk_manager|old_short|impulse_long|market_relative|weak_market" } |
Select-Object ProcessId,CommandLine |
ConvertTo-Json -Depth 3
'''
    proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=30)
    return {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}

def main():
    out_dir = WORKSPACE / "edge_factory_global_risk_decision_diagnoser_v1" / f"global_risk_decision_diag_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    family_config = read_json(FAMILY_CONFIG) or {}

    family_pending = {}
    if isinstance(family_config, dict):
        for fam, folder in family_config.items():
            folder = Path(str(folder))
            family_pending[fam] = {
                "folder": str(folder),
                "pending": due_summary(folder / "pending_entries.csv"),
                "open_rows": int(len(read_csv(folder / "open_positions.csv"))),
                "rejected_rows": int(len(read_csv(folder / "rejected_entries.csv"))),
                "closed_rows": int(len(read_csv(folder / "closed_trades.csv"))),
            }

    gate_df = read_csv(GATE)
    snapshot_df = read_csv(SNAPSHOT)
    violations_df = read_csv(VIOLATIONS)

    cmd = [
        sys.executable,
        str(RISK_MANAGER),
        "--family_config", str(FAMILY_CONFIG),
        "--out_dir", str(RUN),
        "--global_max_positions", "6",
        "--max_short_positions", "5",
        "--max_long_positions", "2",
        "--max_per_family_json", MAX_PER_FAMILY_JSON,
        "--family_priority_json", FAMILY_PRIORITY_JSON,
        "--weak_market_backup_only",
        "--pending_grace_minutes", "180",
        "--poll_seconds", "10",
        "--once",
    ]

    once_proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

    gate_after = read_csv(GATE)
    snapshot_after = read_csv(SNAPSHOT)
    violations_after = read_csv(VIOLATIONS)

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "run": str(RUN),
        "risk_manager": str(RISK_MANAGER),
        "family_config": str(FAMILY_CONFIG),
        "gate": str(GATE),
        "snapshot": str(SNAPSHOT),
        "violations": str(VIOLATIONS),
        "processes": process_lines(),
        "family_config_obj": family_config,
        "family_pending": family_pending,
        "before": {
            "gate_exists": GATE.exists(),
            "gate_size": GATE.stat().st_size if GATE.exists() else 0,
            "gate_rows": int(len(gate_df)),
            "gate_columns": list(gate_df.columns) if not gate_df.empty else [],
            "gate_tail": gate_df.tail(20).to_dict("records") if not gate_df.empty else [],
            "snapshot_rows": int(len(snapshot_df)),
            "snapshot_tail": snapshot_df.tail(10).to_dict("records") if not snapshot_df.empty else [],
            "violations_rows": int(len(violations_df)),
            "violations_tail": violations_df.tail(20).to_dict("records") if not violations_df.empty else [],
        },
        "once_run": {
            "cmd": cmd,
            "returncode": once_proc.returncode,
            "stdout_tail": once_proc.stdout[-5000:],
            "stderr_tail": once_proc.stderr[-5000:],
        },
        "after": {
            "gate_rows": int(len(gate_after)),
            "gate_columns": list(gate_after.columns) if not gate_after.empty else [],
            "gate_tail": gate_after.tail(30).to_dict("records") if not gate_after.empty else [],
            "snapshot_rows": int(len(snapshot_after)),
            "snapshot_tail": snapshot_after.tail(10).to_dict("records") if not snapshot_after.empty else [],
            "violations_rows": int(len(violations_after)),
            "violations_tail": violations_after.tail(20).to_dict("records") if not violations_after.empty else [],
        },
        "live_allowed": False,
    }

    state_path = out_dir / "global_risk_decision_diagnoser_state.json"
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    print("EDGE FACTORY GLOBAL RISK DECISION DIAGNOSER v1")
    print("=" * 100)
    print(f"UTC now: {datetime.now(timezone.utc).isoformat()}")
    print(f"run    : {RUN}")
    print(f"out_dir: {out_dir}")
    print("live_allowed: False")
    print()

    print("FAMILY PENDING SUMMARY")
    print("-" * 100)
    for fam, obj in family_pending.items():
        p = obj["pending"]
        print(
            f"{fam:24s} rows={p['rows']:4d} due={p['due_rows']:4d} future={p['future_rows']:4d} "
            f"open={obj['open_rows']:3d} rejected={obj['rejected_rows']:3d} folder={obj['folder']}"
        )
    print()

    print("BEFORE")
    print("-" * 100)
    print(f"gate_exists={GATE.exists()} gate_size={GATE.stat().st_size if GATE.exists() else 0} gate_rows={len(gate_df)}")
    print(f"snapshot_rows={len(snapshot_df)} violations_rows={len(violations_df)}")
    if not snapshot_df.empty:
        print("snapshot tail:")
        print(snapshot_df.tail(5).to_string(index=False))
    print()

    print("RISK MANAGER ONCE RUN")
    print("-" * 100)
    print("returncode:", once_proc.returncode)
    print("STDOUT:")
    print(once_proc.stdout[-3000:])
    print("STDERR:")
    print(once_proc.stderr[-3000:])
    print()

    print("AFTER")
    print("-" * 100)
    print(f"gate_rows={len(gate_after)} snapshot_rows={len(snapshot_after)} violations_rows={len(violations_after)}")
    if not gate_after.empty:
        print("gate tail:")
        print(gate_after.tail(30).to_string(index=False))
    else:
        print("gate is still empty/header-only")
    print()
    if not snapshot_after.empty:
        print("snapshot tail:")
        print(snapshot_after.tail(5).to_string(index=False))
    print()

    print("PROCESS COMMANDS")
    print("-" * 100)
    print(state["processes"]["stdout"][-5000:])
    print()
    print(f"State: {state_path}")

if __name__ == "__main__":
    main()
