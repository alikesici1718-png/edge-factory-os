#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Watches paper trading sample accumulation across active strategy families by reading closed trade CSV files from the MASTER_UPPER_SYSTEM paper directory and comparing row counts against per-family thresholds. Outputs a sample watcher state JSON indicating whether each family has reached its drift-ready sample size.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

BASE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_MASTER_UPPER_SYSTEM")
WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

THRESHOLDS = {
    "old_short": 50,
    "impulse_long": 25,
    "market_relative_short": 25,
    "weak_market_short": 20,
}

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

def newest_file(folder: Path, patterns):
    files = []
    for pat in patterns:
        files.extend(folder.glob(pat))
    files = [p for p in files if p.is_file()]
    if not files:
        return None
    return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[0]

def heartbeat_age_min(path: Path):
    if not path.exists():
        return None
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    now = datetime.now(timezone.utc)
    return round((now - mtime).total_seconds() / 60.0, 2)

def analyze_family(family, folder_name):
    folder = BASE / folder_name
    hb = newest_file(folder, ["heartbeat.csv", "*heartbeat*.csv", "state.json"])

    closed_file = newest_file(folder, [
        "*closed*.csv",
        "*trades*.csv",
        "*native*.csv",
        "*events*.csv",
    ])

    pending_file = newest_file(folder, ["pending_entries.csv", "*pending*.csv"])
    open_file = newest_file(folder, ["open_positions.csv", "*open*.csv"])

    closed_df = read_csv_safe(closed_file) if closed_file else pd.DataFrame()
    pending_df = read_csv_safe(pending_file) if pending_file else pd.DataFrame()
    open_df = read_csv_safe(open_file) if open_file else pd.DataFrame()

    # Avoid counting pending/open as closed if file name is misleading.
    closed_count = 0
    if closed_file:
        low = closed_file.name.lower()
        if "closed" in low or "trade" in low or "native" in low or "event" in low:
            closed_count = len(closed_df)

    threshold = THRESHOLDS[family]
    ready = closed_count >= threshold

    if not folder.exists():
        status = "FOLDER_MISSING"
    elif hb is None:
        status = "NO_HEARTBEAT"
    elif heartbeat_age_min(hb) is not None and heartbeat_age_min(hb) > 5:
        status = "HEARTBEAT_STALE"
    elif ready:
        status = "DRIFT_SAMPLE_READY"
    elif closed_count > 0:
        status = "COLLECTING_CLOSED_SAMPLE"
    else:
        status = "RUNNING_WAITING_FOR_FIRST_CLOSE"

    return {
        "family_key": family,
        "folder": str(folder),
        "folder_exists": folder.exists(),
        "heartbeat_file": str(hb) if hb else None,
        "heartbeat_age_min": heartbeat_age_min(hb) if hb else None,
        "closed_file": str(closed_file) if closed_file else None,
        "closed_count": int(closed_count),
        "threshold": int(threshold),
        "remaining_to_threshold": max(0, int(threshold - closed_count)),
        "pending_count": int(len(pending_df)),
        "open_count": int(len(open_df)),
        "status": status,
        "ready_for_drift": ready,
    }

def main():
    out_dir = WORKSPACE / "edge_factory_paper_sample_watcher_v1" / f"paper_sample_watch_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = [analyze_family(f, folder) for f, folder in FOLDERS.items()]
    df = pd.DataFrame(rows)

    ready_count = int(df["ready_for_drift"].sum())
    stale_count = int(df["status"].astype(str).str.contains("STALE|NO_HEARTBEAT|FOLDER_MISSING").sum())

    if stale_count > 0:
        overall = "PAPER_SAMPLE_WATCHER_RUNTIME_WARNING"
    elif ready_count == len(df):
        overall = "ALL_FAMILIES_READY_FOR_DRIFT"
    elif ready_count > 0:
        overall = "PARTIAL_FAMILIES_READY_FOR_DRIFT"
    else:
        overall = "PAPER_RUNNING_WAITING_FOR_CLOSED_SAMPLE"

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base": str(BASE),
        "overall_status": overall,
        "ready_family_count": ready_count,
        "family_count": len(df),
        "stale_or_missing_count": stale_count,
        "live_allowed": False,
        "next_action": "RUN_DRIFT_MONITOR_FOR_READY_FAMILIES" if ready_count else "KEEP_PAPER_RUNNING_AND_CONTINUE_OFFLINE_RESEARCH",
        "families": rows,
    }

    (out_dir / "paper_sample_watcher_v1_state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    df.to_csv(out_dir / "paper_sample_watcher_v1_summary.csv", index=False)

    print("EDGE FACTORY PAPER SAMPLE WATCHER v1")
    print("=" * 100)
    print(f"base: {BASE}")
    print(f"output_dir: {out_dir}")
    print(f"overall_status: {overall}")
    print(f"ready_family_count: {ready_count}/{len(df)}")
    print(f"stale_or_missing_count: {stale_count}")
    print("live_allowed: False")
    print()
    print(df[[
        "family_key",
        "status",
        "heartbeat_age_min",
        "closed_count",
        "threshold",
        "remaining_to_threshold",
        "pending_count",
        "open_count",
        "ready_for_drift",
    ]].to_string(index=False))
    print()
    print(f"State  : {out_dir / 'paper_sample_watcher_v1_state.json'}")
    print(f"Summary: {out_dir / 'paper_sample_watcher_v1_summary.csv'}")

if __name__ == "__main__":
    main()
