#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnoses why pending entries are not transitioning to open positions by reading pending, open, closed, and error CSV files from each active strategy family folder under MASTER_UPPER_SYSTEM. Outputs a timestamped diagnostic JSON and summary CSV to the edge_factory_pending_to_open_diagnoser_v1 directory.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

BASE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_MASTER_UPPER_SYSTEM")
WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

FOLDERS = {
    "old_short": "live_blowoff_short_paper_realistic",
    "impulse_long": "live_impulse_event_long_paper",
    "market_relative_short": "live_market_relative_extreme_reversion_short_paper",
    "weak_market_short": "live_weak_market_breakdown_short_paper",
}

def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def read_csv_safe(p: Path) -> pd.DataFrame:
    if not p.exists() or p.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(p)
    except Exception:
        return pd.DataFrame()

def read_json_safe(p: Path) -> dict[str, Any]:
    if not p.exists() or p.stat().st_size == 0:
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}

def newest_files(folder: Path, patterns: list[str], limit: int = 10) -> list[Path]:
    files = []
    for pat in patterns:
        files.extend(folder.glob(pat))
    files = [p for p in files if p.is_file()]
    return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[:limit]

def file_tail(path: Path, n: int = 20) -> str:
    try:
        txt = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(txt[-n:])
    except Exception as e:
        return f"READ_ERROR: {e!r}"

def summarize_pending(df: pd.DataFrame) -> dict[str, Any]:
    now = pd.Timestamp.now(tz="UTC")
    out = {
        "pending_rows": int(len(df)),
        "due_rows": 0,
        "future_rows": 0,
        "oldest_target_entry_time": None,
        "newest_target_entry_time": None,
    }

    if df.empty:
        return out

    target_col = None
    for c in ["target_entry_time", "entry_time", "planned_entry_time"]:
        if c in df.columns:
            target_col = c
            break

    if not target_col:
        out["warning"] = "no target entry time column"
        return out

    ts = pd.to_datetime(df[target_col], errors="coerce", utc=True)
    out["oldest_target_entry_time"] = str(ts.min()) if ts.notna().any() else None
    out["newest_target_entry_time"] = str(ts.max()) if ts.notna().any() else None
    out["due_rows"] = int((ts.notna() & (ts <= now)).sum())
    out["future_rows"] = int((ts.notna() & (ts > now)).sum())
    return out

def main():
    out_dir = WORKSPACE / "edge_factory_pending_to_open_diagnoser_v1" / f"pending_to_open_diag_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    rows = []
    details = {}

    print("EDGE FACTORY PENDING TO OPEN DIAGNOSER v1")
    print("=" * 100)
    print(f"UTC now : {now.isoformat()}")
    print(f"base    : {BASE}")
    print(f"out_dir : {out_dir}")
    print("live_allowed: False")
    print()

    for family, folder_name in FOLDERS.items():
        folder = BASE / folder_name

        pending_files = newest_files(folder, ["*pending*.csv", "pending_entries.csv"], 5)
        open_files = newest_files(folder, ["*open*.csv", "open_positions.csv"], 5)
        closed_files = newest_files(folder, ["*closed*.csv", "*trades*.csv"], 5)
        rejected_files = newest_files(folder, ["*reject*.csv", "*rejected*.csv"], 5)
        heartbeat_files = newest_files(folder, ["*heartbeat*.json", "*heartbeat*.csv", "state.json"], 5)
        log_files = newest_files(folder, ["*.log", "*.txt"], 10)
        gate_files = newest_files(folder, ["*gate*.json", "*risk*.json", "*.json"], 20)

        pending_df = read_csv_safe(pending_files[0]) if pending_files else pd.DataFrame()
        open_df = read_csv_safe(open_files[0]) if open_files else pd.DataFrame()
        closed_df = read_csv_safe(closed_files[0]) if closed_files else pd.DataFrame()
        rejected_df = read_csv_safe(rejected_files[0]) if rejected_files else pd.DataFrame()

        pend_sum = summarize_pending(pending_df)

        row = {
            "family_key": family,
            "folder_exists": folder.exists(),
            "pending_file": str(pending_files[0]) if pending_files else None,
            "open_file": str(open_files[0]) if open_files else None,
            "closed_file": str(closed_files[0]) if closed_files else None,
            "rejected_file": str(rejected_files[0]) if rejected_files else None,
            "pending_rows": pend_sum["pending_rows"],
            "pending_due_rows": pend_sum["due_rows"],
            "pending_future_rows": pend_sum["future_rows"],
            "open_rows": int(len(open_df)),
            "closed_rows": int(len(closed_df)),
            "rejected_rows": int(len(rejected_df)),
            "oldest_target_entry_time": pend_sum.get("oldest_target_entry_time"),
            "newest_target_entry_time": pend_sum.get("newest_target_entry_time"),
            "diagnosis": "",
        }

        if row["pending_due_rows"] > 0 and row["open_rows"] == 0:
            row["diagnosis"] = "BLOCKER_DUE_PENDING_NOT_OPENING"
        elif row["pending_rows"] > 0 and row["pending_due_rows"] == 0:
            row["diagnosis"] = "WAITING_TARGET_ENTRY_TIME"
        elif row["open_rows"] > 0:
            row["diagnosis"] = "OPEN_POSITIONS_EXIST"
        elif row["pending_rows"] == 0:
            row["diagnosis"] = "NO_PENDING"
        else:
            row["diagnosis"] = "UNKNOWN"

        rows.append(row)

        details[family] = {
            "folder": str(folder),
            "pending_files": [str(p) for p in pending_files],
            "open_files": [str(p) for p in open_files],
            "closed_files": [str(p) for p in closed_files],
            "rejected_files": [str(p) for p in rejected_files],
            "heartbeat_files": [str(p) for p in heartbeat_files],
            "gate_files": [str(p) for p in gate_files],
            "log_files": [str(p) for p in log_files],
            "pending_tail": pending_df.tail(20).to_dict("records") if not pending_df.empty else [],
            "open_tail": open_df.tail(20).to_dict("records") if not open_df.empty else [],
            "rejected_tail": rejected_df.tail(30).to_dict("records") if not rejected_df.empty else [],
            "heartbeat_jsons": {str(p): read_json_safe(p) for p in heartbeat_files if p.suffix.lower() == ".json"},
            "gate_jsons": {str(p): read_json_safe(p) for p in gate_files if p.suffix.lower() == ".json"},
            "log_tails": {str(p): file_tail(p, 40) for p in log_files[:5]},
        }

    summary = pd.DataFrame(rows)
    summary_path = out_dir / "pending_to_open_diagnoser_summary.csv"
    state_path = out_dir / "pending_to_open_diagnoser_state.json"

    summary.to_csv(summary_path, index=False)

    state = {
        "generated_at": now.isoformat(),
        "base": str(BASE),
        "overall_status": "PENDING_TO_OPEN_BLOCKER_DETECTED" if (summary["diagnosis"] == "BLOCKER_DUE_PENDING_NOT_OPENING").any() else "NO_DUE_PENDING_BLOCKER_DETECTED",
        "live_allowed": False,
        "details": details,
    }
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    print("SUMMARY")
    print("-" * 100)
    print(summary.to_string(index=False))
    print()

    for family in FOLDERS:
        print("=" * 100)
        print(family)
        print("-" * 100)

        d = details[family]

        print("FILES")
        print("pending:", d["pending_files"][:3])
        print("open   :", d["open_files"][:3])
        print("closed :", d["closed_files"][:3])
        print("reject :", d["rejected_files"][:3])
        print("logs   :", d["log_files"][:3])
        print()

        if d["rejected_tail"]:
            print("REJECTED TAIL")
            print(pd.DataFrame(d["rejected_tail"]).tail(20).to_string(index=False))
            print()

        if d["pending_tail"]:
            print("PENDING TAIL")
            print(pd.DataFrame(d["pending_tail"]).tail(10).to_string(index=False))
            print()

        if d["log_tails"]:
            print("LOG TAILS")
            for p, tail in d["log_tails"].items():
                print(f"--- {p} ---")
                print(tail[-2500:])
                print()

    print(f"State  : {state_path}")
    print(f"Summary: {summary_path}")

if __name__ == "__main__":
    main()
