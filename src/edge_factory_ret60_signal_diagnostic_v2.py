#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reads the candle replay CSV produced by the local candle replay runner and computes per-symbol signal diagnostic statistics for the ret60_reversal_short rule (hour-8 UTC, signal_ret60_bps >= 75).
Outputs a per-symbol summary CSV and a JSON state report to a stamped directory showing signal hit counts and return distributions.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd
import numpy as np

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
CANDIDATE = "ret60_reversal_short"

def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def latest_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    return sorted(ds, key=lambda x: x.stat().st_mtime, reverse=True)[0] if ds else None

def read_json(path: Optional[Path]) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def write_json(path: Path, obj: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_ret60_signal_diagnostic_v2" / f"ret60_signal_diag_v2_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    rdir = latest_dir(WORKSPACE / "edge_factory_ret60_local_candle_replay_runner_v2", "ret60_local_replay_v2_")
    state_path = rdir / "ret60_local_candle_replay_runner_v2_state.json" if rdir else None
    state = read_json(state_path)

    replay_csv = Path(state.get("replay_input_csv", "")) if state.get("replay_input_csv") else None
    if not replay_csv or not replay_csv.exists():
        print("replay input not found:", replay_csv)
        return 2

    df = pd.read_csv(replay_csv)
    df["event_time"] = pd.to_datetime(df["event_time"], errors="coerce", utc=True)
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["symbol", "event_time", "close"])
    df = df[df["close"] > 0].sort_values(["symbol", "event_time"]).reset_index(drop=True)

    rows = []
    total_hour8 = 0
    total_prior60 = 0
    total_signal75 = 0

    for symbol, g in df.groupby("symbol", sort=False):
        g = g.sort_values("event_time").reset_index(drop=True)
        times = g["event_time"].astype("int64").to_numpy()
        close = g["close"].to_numpy(dtype=float)
        hour = g["event_time"].dt.hour.to_numpy()

        hour8_idx = np.where(hour == 8)[0]
        total_hour8 += len(hour8_idx)

        rets = []
        signal_count = 0
        prior_count = 0

        for i in hour8_idx:
            t = times[i]
            target_prior = t - 60 * 60 * 1_000_000_000
            j = np.searchsorted(times, target_prior, side="right") - 1
            if j < 0:
                continue
            prior_count += 1
            ret = (close[i] / close[j] - 1.0) * 10000.0
            rets.append(ret)
            if ret >= 75:
                signal_count += 1

        total_prior60 += prior_count
        total_signal75 += signal_count

        if rets:
            arr = np.array(rets, dtype=float)
            max_ret = float(np.nanmax(arr))
            q95 = float(np.nanpercentile(arr, 95))
            mean_ret = float(np.nanmean(arr))
        else:
            max_ret = None
            q95 = None
            mean_ret = None

        rows.append({
            "symbol": symbol,
            "rows": int(len(g)),
            "first_time": str(g["event_time"].min()),
            "last_time": str(g["event_time"].max()),
            "hour8_rows": int(len(hour8_idx)),
            "prior60_available": int(prior_count),
            "ret60_ge_75_count": int(signal_count),
            "ret60_max_bps": max_ret,
            "ret60_q95_bps": q95,
            "ret60_mean_bps": mean_ret,
        })

    sdf = pd.DataFrame(rows).sort_values(["ret60_ge_75_count", "ret60_max_bps"], ascending=[False, False])
    summary = {
        "candidate": CANDIDATE,
        "replay_input_csv": str(replay_csv),
        "rows": int(len(df)),
        "symbols": int(df["symbol"].nunique()),
        "total_hour8_rows": int(total_hour8),
        "total_prior60_available": int(total_prior60),
        "total_ret60_ge_75_count": int(total_signal75),
        "verdict": (
            "SIGNALS_EXIST_ENGINE_FILTER_OR_EXIT_PROBLEM"
            if total_signal75 > 0 else
            "NO_RET60_GE_75_AT_HOUR8_IN_REPLAY_INPUT"
        ),
        "active_paper_allowed": False,
        "live_allowed": False,
    }

    write_json(out_dir / "ret60_signal_diagnostic_v2_state.json", summary)
    sdf.to_csv(out_dir / "ret60_signal_diagnostic_by_symbol.csv", index=False)

    print("EDGE FACTORY RET60 SIGNAL DIAGNOSTIC v2")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"replay_input_csv: {replay_csv}")
    print(f"rows: {summary['rows']}")
    print(f"symbols: {summary['symbols']}")
    print(f"total_hour8_rows: {summary['total_hour8_rows']}")
    print(f"total_prior60_available: {summary['total_prior60_available']}")
    print(f"total_ret60_ge_75_count: {summary['total_ret60_ge_75_count']}")
    print(f"verdict: {summary['verdict']}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print()
    print("TOP SYMBOLS")
    print("-" * 100)
    print(sdf.head(20).to_string(index=False))
    print()
    print(f"State: {out_dir / 'ret60_signal_diagnostic_v2_state.json'}")
    print(f"By symbol: {out_dir / 'ret60_signal_diagnostic_by_symbol.csv'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
