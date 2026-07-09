#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tracks and classifies the lifecycle state of research candidate strategies by inspecting their shadow paper trading directories for heartbeat, signal, and closed trade files. Reads shadow directory outputs for each tracked candidate and writes a registry state JSON with lifecycle classifications such as ARCHIVE_WAIT.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REGISTRY_ROOT = WORKSPACE / "edge_factory_candidate_lifecycle_registry_v1"

CANDIDATES = {
    "rel_extreme_reversion_short": {
        "role": "RESEARCH_CANDIDATE_SHADOW",
        "shadow_dir": WORKSPACE / "paper_run_shadow_rel_extreme_reversion_short",
        "expected_status": "ARCHIVE_WAIT",
    }
}

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def latest_dir(root: Path, prefix: str) -> Path | None:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    return sorted(ds, key=lambda p: p.stat().st_mtime, reverse=True)[0] if ds else None

def read_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}

def read_csv(path: Path | None) -> pd.DataFrame:
    if not path or not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

def file_age_min(path: Path | None) -> float | None:
    if not path or not path.exists():
        return None
    return round((datetime.now(timezone.utc).timestamp() - path.stat().st_mtime) / 60.0, 2)

def newest(folder: Path, pattern: str) -> Path | None:
    if not folder.exists():
        return None
    files = list(folder.glob(pattern))
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def classify_rel_extreme() -> dict[str, Any]:
    key = "rel_extreme_reversion_short"
    shadow = CANDIDATES[key]["shadow_dir"]

    heartbeat = newest(shadow, "*heartbeat*.json")
    signals_file = newest(shadow, "*signals*.csv")
    closed_file = newest(shadow, "*closed*.csv")

    signals = read_csv(signals_file)
    closed = read_csv(closed_file)

    heartbeat_age = file_age_min(heartbeat)
    running_guess = heartbeat_age is not None and heartbeat_age <= 15

    duplicate_signal_warning = False
    duplicate_key = None
    duplicate_count = 0

    if not signals.empty:
        cols = [c for c in ["candidate", "symbol", "side", "signal_time", "entry_time", "planned_exit_time"] if c in signals.columns]
        if cols:
            grouped = signals.groupby(cols, dropna=False).size().sort_values(ascending=False)
            if len(grouped) > 0:
                duplicate_count = int(grouped.iloc[0])
                duplicate_key = str(grouped.index[0])
                duplicate_signal_warning = duplicate_count >= 5

    reasons = []
    blockers = []

    if len(signals) > 0:
        reasons.append(f"shadow_signals_collected={len(signals)}")
    else:
        blockers.append("NO_SHADOW_SIGNALS")

    if len(closed) == 0:
        blockers.append("NO_SHADOW_CLOSED_SAMPLE")
    else:
        reasons.append(f"shadow_closed_sample={len(closed)}")

    if not running_guess:
        reasons.append(f"shadow_not_running_or_stale_heartbeat_age_min={heartbeat_age}")

    if duplicate_signal_warning:
        blockers.append("DUPLICATE_OR_STALE_SIGNAL_REPLAY_PATTERN")
        reasons.append(f"top_duplicate_signal_count={duplicate_count}")

    if len(closed) == 0 or duplicate_signal_warning:
        lifecycle_status = "ARCHIVE_WAIT"
        promotion_allowed = False
        active_paper_allowed = False
        live_allowed = False
        next_action = "DO_NOT_PROMOTE_KEEP_ARCHIVED_UNTIL_REALTIME_SHADOW_FIXED"
    else:
        lifecycle_status = "READY_FOR_SHADOW_REVIEW"
        promotion_allowed = False
        active_paper_allowed = False
        live_allowed = False
        next_action = "RUN_SHADOW_PERFORMANCE_REVIEW"

    return {
        "candidate": key,
        "role": CANDIDATES[key]["role"],
        "lifecycle_status": lifecycle_status,
        "shadow_dir": str(shadow),
        "shadow_running_guess": running_guess,
        "heartbeat_path": str(heartbeat) if heartbeat else None,
        "heartbeat_age_min": heartbeat_age,
        "signals_file": str(signals_file) if signals_file else None,
        "signals_rows": int(len(signals)),
        "closed_file": str(closed_file) if closed_file else None,
        "closed_rows": int(len(closed)),
        "duplicate_signal_warning": duplicate_signal_warning,
        "top_duplicate_signal_count": duplicate_count,
        "top_duplicate_key": duplicate_key,
        "reasons": reasons,
        "blockers": blockers,
        "next_action": next_action,
        "promotion_allowed": promotion_allowed,
        "active_paper_allowed": active_paper_allowed,
        "live_allowed": live_allowed,
        "capital_change_allowed": False,
    }

def main() -> int:
    out_dir = REGISTRY_ROOT / f"candidate_lifecycle_registry_v1_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    rows.append(classify_rel_extreme())

    df = pd.DataFrame(rows)

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "registry_status": "CANDIDATE_LIFECYCLE_REGISTRY_UPDATED",
        "candidate_count": len(rows),
        "candidates": rows,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "This registry does not start candidates.",
            "This registry does not promote candidates.",
            "This registry does not modify MASTER_UPPER_SYSTEM.",
            "This registry does not place orders.",
            "This registry records lifecycle state only.",
        ],
    }

    state_path = out_dir / "candidate_lifecycle_registry_v1_state.json"
    csv_path = out_dir / "candidate_lifecycle_registry_v1.csv"
    ledger_path = REGISTRY_ROOT / "candidate_lifecycle_master_ledger.jsonl"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    df.to_csv(csv_path, index=False)

    with ledger_path.open("a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps({
                "logged_at": datetime.now(timezone.utc).isoformat(),
                **r,
            }, ensure_ascii=False, default=str) + "\n")

    print("EDGE FACTORY CANDIDATE LIFECYCLE REGISTRY v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print("registry_status: CANDIDATE_LIFECYCLE_REGISTRY_UPDATED")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("CANDIDATES")
    print("-" * 100)
    show_cols = [
        "candidate", "role", "lifecycle_status", "signals_rows", "closed_rows",
        "shadow_running_guess", "heartbeat_age_min", "duplicate_signal_warning",
        "top_duplicate_signal_count", "promotion_allowed", "next_action"
    ]
    print(df[show_cols].to_string(index=False))
    print()
    print("BLOCKERS / REASONS")
    print("-" * 100)
    for r in rows:
        print(r["candidate"])
        print("  blockers:", r["blockers"])
        print("  reasons :", r["reasons"])
    print()
    print(f"State : {state_path}")
    print(f"CSV   : {csv_path}")
    print(f"Ledger: {ledger_path}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
