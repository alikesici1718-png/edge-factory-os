#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Any
import pandas as pd
import numpy as np

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
SYMBOL_RE = re.compile(r"([A-Z0-9]{1,25}-USDT-SWAP)")

def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def infer_symbol(path: Path) -> Optional[str]:
    m = SYMBOL_RE.search(str(path).upper().replace("\\", "/"))
    return m.group(1) if m else None

def robust_time_parse(s: pd.Series) -> pd.Series:
    num = pd.to_numeric(s, errors="coerce")
    numeric_ratio = float(num.notna().mean()) if len(num) else 0.0

    if numeric_ratio >= 0.80:
        med = float(num.dropna().median())
        if med > 1e17:
            return pd.to_datetime(num, unit="ns", errors="coerce", utc=True)
        if med > 1e14:
            return pd.to_datetime(num, unit="us", errors="coerce", utc=True)
        if med > 1e11:
            return pd.to_datetime(num, unit="ms", errors="coerce", utc=True)
        if med > 1e8:
            return pd.to_datetime(num, unit="s", errors="coerce", utc=True)

    return pd.to_datetime(s, errors="coerce", utc=True)

def read_candle(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    # OKX raw candle generally: ts, open, high, low, close...
    # If header exists, column names may already be meaningful.
    cols = list(df.columns)

    # If columns are unnamed numeric-looking strings, treat as OKX raw.
    if len(cols) >= 5 and all(str(c).isdigit() for c in cols[:5]):
        time_col = cols[0]
        close_col = cols[4]
    else:
        lower = {str(c).lower(): c for c in cols}
        time_col = lower.get("event_time") or lower.get("timestamp") or lower.get("time") or lower.get("open_time") or cols[0]
        close_col = lower.get("close") or lower.get("c") or lower.get("close_price") or cols[4]

    symbol = infer_symbol(path)
    out = pd.DataFrame()
    out["symbol"] = symbol
    out["event_time"] = robust_time_parse(df[time_col])
    out["close"] = pd.to_numeric(df[close_col], errors="coerce")
    out = out.dropna(subset=["event_time", "close"])
    out = out[out["close"] > 0]
    out = out.sort_values("event_time").reset_index(drop=True)
    return out

def diagnose_file(path: Path) -> dict[str, Any]:
    df = read_candle(path).tail(50000).copy()
    df = df.sort_values("event_time").reset_index(drop=True)

    times_ns = df["event_time"].astype("int64").to_numpy()
    time_set = set(times_ns.tolist())

    hour8 = df[df["event_time"].dt.hour == 8].copy()
    hour8_ns = hour8["event_time"].astype("int64").to_numpy()

    exact_set_count = 0
    search_count = 0
    search_gap_ok_count = 0
    first_examples = []

    for idx, t_ns in enumerate(hour8_ns[:5000]):
        target = int(t_ns - 60 * 60 * 1_000_000_000)

        if target in time_set:
            exact_set_count += 1

        j = np.searchsorted(times_ns, target, side="right") - 1
        if j >= 0:
            search_count += 1
            gap_sec = (target - int(times_ns[j])) / 1_000_000_000
            if 0 <= gap_sec <= 90:
                search_gap_ok_count += 1

            if len(first_examples) < 5:
                first_examples.append({
                    "signal_time": str(pd.to_datetime(t_ns, utc=True)),
                    "target_prior_time": str(pd.to_datetime(target, utc=True)),
                    "matched_time": str(pd.to_datetime(int(times_ns[j]), utc=True)),
                    "gap_sec": gap_sec,
                })

    # merge_asof method
    full = df[["event_time", "close"]].copy().sort_values("event_time")
    events = hour8[["event_time", "close"]].copy().sort_values("event_time")
    events["target_prior_time"] = events["event_time"] - pd.Timedelta(minutes=60)

    merged = pd.merge_asof(
        events.sort_values("target_prior_time"),
        full.rename(columns={"event_time": "prior_time", "close": "prior_close"}).sort_values("prior_time"),
        left_on="target_prior_time",
        right_on="prior_time",
        direction="backward",
        tolerance=pd.Timedelta(seconds=90),
    )

    merge_count = int(merged["prior_close"].notna().sum())

    diffs = df["event_time"].diff().dt.total_seconds().dropna()
    return {
        "path": str(path),
        "symbol": infer_symbol(path),
        "rows": int(len(df)),
        "first_time": str(df["event_time"].min()),
        "last_time": str(df["event_time"].max()),
        "median_step_sec": float(diffs.median()) if len(diffs) else None,
        "hour8_rows": int(len(hour8)),
        "exact_set_prior60_count_first5000": int(exact_set_count),
        "search_prior_count_first5000": int(search_count),
        "search_gap_ok_count_first5000": int(search_gap_ok_count),
        "merge_asof_prior60_count_total": int(merge_count),
        "first_examples": first_examples,
    }

def main():
    out_dir = WORKSPACE / "edge_factory_ret60_prior60_match_diagnostic_v5" / f"prior60_diag_v5_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = []
    for p in WORKSPACE.rglob("*.csv"):
        s = str(p).lower()
        if ("raw\\candles_long_1m" in s or "raw/candles_long_1m" in s) and infer_symbol(p):
            files.append(p)

    files = sorted(files)[:10]

    rows = []
    for p in files:
        try:
            rows.append(diagnose_file(p))
        except Exception as e:
            rows.append({"path": str(p), "error": repr(e)})

    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "prior60_match_diagnostic_v5_by_file.csv", index=False)

    total_hour8 = int(df.get("hour8_rows", pd.Series(dtype=int)).fillna(0).sum())
    total_merge = int(df.get("merge_asof_prior60_count_total", pd.Series(dtype=int)).fillna(0).sum())
    total_exact = int(df.get("exact_set_prior60_count_first5000", pd.Series(dtype=int)).fillna(0).sum())

    verdict = "PRIOR60_MATCH_WORKS_WITH_MERGE_ASOF" if total_merge > 0 else "PRIOR60_MATCH_STILL_BROKEN"

    state = {
        "verdict": verdict,
        "files_checked": len(files),
        "total_hour8_rows": total_hour8,
        "total_exact_set_first5000": total_exact,
        "total_merge_asof_prior60": total_merge,
        "active_paper_allowed": False,
        "live_allowed": False,
    }

    (out_dir / "prior60_match_diagnostic_v5_state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")

    print("EDGE FACTORY RET60 PRIOR60 MATCH DIAGNOSTIC v5")
    print("=" * 100)
    print(f"output_dir: {out_dir}")
    print(f"files_checked: {len(files)}")
    print(f"total_hour8_rows: {total_hour8}")
    print(f"total_exact_set_first5000: {total_exact}")
    print(f"total_merge_asof_prior60: {total_merge}")
    print(f"verdict: {verdict}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print()
    print(df[[
        "symbol",
        "rows",
        "first_time",
        "last_time",
        "median_step_sec",
        "hour8_rows",
        "exact_set_prior60_count_first5000",
        "search_gap_ok_count_first5000",
        "merge_asof_prior60_count_total"
    ]].to_string(index=False))
    print()
    print(f"State: {out_dir / 'prior60_match_diagnostic_v5_state.json'}")
    print(f"By file: {out_dir / 'prior60_match_diagnostic_v5_by_file.csv'}")

if __name__ == "__main__":
    main()
