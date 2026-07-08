#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import pandas as pd
import numpy as np

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
SYMBOL_RE = re.compile(r"([A-Z0-9]{2,25}-USDT-SWAP)")
TIME_ALIASES = ["event_time", "timestamp", "time", "datetime", "open_time", "ts"]
CLOSE_ALIASES = ["close", "c", "close_price", "last", "price"]

def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def pick_col(cols, aliases):
    lower = {str(c).lower(): c for c in cols}
    for a in aliases:
        if a in lower:
            return lower[a]
    for c in cols:
        cl = str(c).lower()
        for a in aliases:
            if a in cl:
                return c
    return None

def infer_symbol(path: Path) -> Optional[str]:
    m = SYMBOL_RE.search(str(path).upper().replace("\\", "/"))
    return m.group(1) if m else None

def robust_time_parse(s: pd.Series) -> pd.Series:
    # Critical fix: numeric strings must be interpreted by magnitude, not default pd.to_datetime.
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

def read_one(path: Path):
    try:
        df = pd.read_csv(path)
        if len(df.columns) < 5:
            df2 = pd.read_csv(path, header=None)
            if len(df2.columns) >= 5:
                df = df2
    except Exception:
        return None, "read failed"

    cols = list(df.columns)

    # headerless OKX format fallback: ts, o, h, l, c...
    if len(cols) >= 5 and all(str(c).isdigit() for c in cols[:5]):
        time_col = cols[0]
        close_col = cols[4]
    else:
        time_col = pick_col(cols, TIME_ALIASES)
        close_col = pick_col(cols, CLOSE_ALIASES)

    if time_col is None or close_col is None:
        return None, f"missing cols: {cols[:10]}"

    symbol = infer_symbol(path)
    if not symbol:
        return None, "no symbol in path"

    out = pd.DataFrame()
    out["symbol"] = symbol
    out["event_time"] = robust_time_parse(df[time_col])
    out["close"] = pd.to_numeric(df[close_col], errors="coerce")
    out = out.dropna(subset=["event_time", "close"])
    out = out[out["close"] > 0].sort_values("event_time").reset_index(drop=True)

    if len(out) < 500:
        return None, "too few rows"

    return out, "ok"

def main():
    out_dir = WORKSPACE / "edge_factory_ret60_timestamp_parser_diagnostic_v4" / f"timestamp_diag_v4_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = []
    for p in WORKSPACE.rglob("*.csv"):
        s = str(p).lower()
        if "raw\\candles_long_1m" in s or "raw/candles_long_1m" in s:
            if infer_symbol(p):
                files.append(p)

    files = sorted(files)[:30]

    rows = []
    total_prior60 = 0
    total_hour8 = 0
    total_ret60_75 = 0

    for p in files:
        df, reason = read_one(p)
        if df is None:
            rows.append({"path": str(p), "used": False, "reason": reason})
            continue

        g = df.tail(50000).copy().sort_values("event_time").reset_index(drop=True)
        times = g["event_time"].astype("int64").to_numpy()
        closes = g["close"].to_numpy(dtype=float)
        hours = g["event_time"].dt.hour.to_numpy()

        diffs_sec = pd.Series(g["event_time"]).diff().dt.total_seconds().dropna()
        median_step = float(diffs_sec.median()) if len(diffs_sec) else None

        hour8_idxs = np.where(hours == 8)[0]
        prior60 = 0
        ret75 = 0
        max_ret = None

        rets = []
        for i in hour8_idxs:
            target = times[i] - 60 * 60 * 1_000_000_000
            j = np.searchsorted(times, target, side="right") - 1
            if j < 0:
                continue
            prior60 += 1
            ret = (closes[i] / closes[j] - 1.0) * 10000.0
            rets.append(ret)
            if ret >= 75:
                ret75 += 1

        if rets:
            max_ret = float(np.max(rets))

        total_hour8 += len(hour8_idxs)
        total_prior60 += prior60
        total_ret60_75 += ret75

        rows.append({
            "path": str(p),
            "used": True,
            "symbol": g["symbol"].iloc[0],
            "rows": len(g),
            "first_time": str(g["event_time"].min()),
            "last_time": str(g["event_time"].max()),
            "median_step_sec": median_step,
            "hour8_rows": int(len(hour8_idxs)),
            "prior60_available": int(prior60),
            "ret60_ge_75": int(ret75),
            "ret60_max_bps": max_ret,
            "reason": reason,
        })

    result = {
        "files_checked": len(files),
        "total_hour8_rows": int(total_hour8),
        "total_prior60_available": int(total_prior60),
        "total_ret60_ge_75": int(total_ret60_75),
        "verdict": "TIMESTAMP_PARSE_FIXED" if total_prior60 > 0 else "TIMESTAMP_PARSE_STILL_BROKEN",
        "active_paper_allowed": False,
        "live_allowed": False,
    }

    pd.DataFrame(rows).to_csv(out_dir / "timestamp_parser_diagnostic_v4_by_file.csv", index=False)
    (out_dir / "timestamp_parser_diagnostic_v4_state.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("EDGE FACTORY RET60 TIMESTAMP PARSER DIAGNOSTIC v4")
    print("=" * 100)
    print(f"output_dir: {out_dir}")
    print(f"files_checked: {result['files_checked']}")
    print(f"total_hour8_rows: {result['total_hour8_rows']}")
    print(f"total_prior60_available: {result['total_prior60_available']}")
    print(f"total_ret60_ge_75: {result['total_ret60_ge_75']}")
    print(f"verdict: {result['verdict']}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print()
    print(pd.DataFrame(rows).head(20).to_string(index=False))
    print()
    print(f"State: {out_dir / 'timestamp_parser_diagnostic_v4_state.json'}")
    print(f"By file: {out_dir / 'timestamp_parser_diagnostic_v4_by_file.csv'}")

if __name__ == "__main__":
    main()
