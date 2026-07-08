#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
SHADOW = WORKSPACE / "paper_run_shadow_rel_extreme_reversion_short"

def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

def read_json(path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}

def age_min(path: Path) -> float | None:
    if not path.exists():
        return None
    return round((datetime.now(timezone.utc).timestamp() - path.stat().st_mtime) / 60, 2)

def newest(pattern: str) -> Path | None:
    files = list(SHADOW.glob(pattern))
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def main():
    out_dir = WORKSPACE / "edge_factory_rel_extreme_shadow_postmortem_v1" / f"rel_extreme_shadow_postmortem_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    heartbeat = newest("*heartbeat*.json")
    signals_file = newest("*signals*.csv")
    closed_file = newest("*closed*.csv")
    audit_file = newest("*audit*.csv")

    heartbeat_json = read_json(heartbeat) if heartbeat else {}
    signals = read_csv(signals_file) if signals_file else pd.DataFrame()
    closed = read_csv(closed_file) if closed_file else pd.DataFrame()
    audit = read_csv(audit_file) if audit_file else pd.DataFrame()

    shadow_running_guess = heartbeat is not None and age_min(heartbeat) is not None and age_min(heartbeat) < 15

    if closed.empty and len(signals) > 0:
        verdict = "SHADOW_COLLECTED_SIGNALS_BUT_NO_CLOSED_YET"
        next_action = "KEEP_ARCHIVED_OR_RESTART_SHADOW_IF_WE_WANT_MORE_OBSERVATION"
    elif len(closed) > 0:
        verdict = "SHADOW_HAS_CLOSED_SAMPLE_READY_FOR_REVIEW"
        next_action = "RUN_SHADOW_DRIFT_OR_PERFORMANCE_REVIEW"
    elif len(signals) == 0:
        verdict = "SHADOW_NO_SIGNAL_SAMPLE"
        next_action = "OPTIONAL_RESTART_LATER"
    else:
        verdict = "SHADOW_STATUS_UNKNOWN"
        next_action = "MANUAL_REVIEW"

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "shadow_dir": str(SHADOW),
        "shadow_dir_exists": SHADOW.exists(),
        "shadow_running_guess": shadow_running_guess,
        "heartbeat_path": str(heartbeat) if heartbeat else None,
        "heartbeat_age_min": age_min(heartbeat) if heartbeat else None,
        "signals_file": str(signals_file) if signals_file else None,
        "signals_rows": int(len(signals)),
        "closed_file": str(closed_file) if closed_file else None,
        "closed_rows": int(len(closed)),
        "audit_file": str(audit_file) if audit_file else None,
        "audit_rows": int(len(audit)),
        "verdict": verdict,
        "next_action": next_action,
        "active_paper_allowed": False,
        "live_allowed": False,
    }

    state_path = out_dir / "rel_extreme_shadow_postmortem_state.json"
    signals_tail_path = out_dir / "rel_extreme_shadow_signals_tail.csv"
    closed_tail_path = out_dir / "rel_extreme_shadow_closed_tail.csv"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    signals.tail(50).to_csv(signals_tail_path, index=False)
    closed.tail(50).to_csv(closed_tail_path, index=False)

    print("EDGE FACTORY REL EXTREME SHADOW POSTMORTEM v1")
    print("=" * 100)
    print(f"shadow_dir         : {SHADOW}")
    print(f"shadow_running_guess: {shadow_running_guess}")
    print(f"heartbeat_age_min  : {state['heartbeat_age_min']}")
    print(f"signals_rows       : {len(signals)}")
    print(f"closed_rows        : {len(closed)}")
    print(f"verdict            : {verdict}")
    print(f"next_action        : {next_action}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print()
    print("FILES")
    print("-" * 100)
    print(f"heartbeat: {heartbeat}")
    print(f"signals  : {signals_file}")
    print(f"closed   : {closed_file}")
    print(f"audit    : {audit_file}")
    print()
    if not signals.empty:
        print("SIGNALS TAIL")
        print("-" * 100)
        print(signals.tail(10).to_string(index=False))
    if not closed.empty:
        print()
        print("CLOSED TAIL")
        print("-" * 100)
        print(closed.tail(10).to_string(index=False))
    print()
    print(f"State      : {state_path}")
    print(f"SignalsTail: {signals_tail_path}")
    print(f"ClosedTail : {closed_tail_path}")

if __name__ == "__main__":
    main()
