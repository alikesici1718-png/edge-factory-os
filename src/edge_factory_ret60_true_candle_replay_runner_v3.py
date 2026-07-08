#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List, Tuple

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
CANDIDATE = "ret60_reversal_short"

SYMBOL_RE = re.compile(r"([A-Z0-9]{2,25}-USDT-SWAP)")
BAD_PATH_MARKERS = [
    "edge_factory_", "paper_run_", "live_", "__pycache__",
    "global_risk", "risk_snapshot", "snapshot", "ledger", "audit",
    "report", "state", "gate", "monitor", "observer", "summary",
    "result", "decision", "approval", "manifest", "reconciler",
    "optimizer", "governor", "health", "dashboard"
]
GOOD_PATH_MARKERS = ["candle", "candles", "kline", "klines", "1m", "minute"]

TIME_ALIASES = ["event_time", "timestamp", "time", "datetime", "open_time", "ts"]
CLOSE_ALIASES = ["close", "c", "close_price", "last", "price"]
SYMBOL_ALIASES = ["symbol", "inst_id", "inst", "ticker", "coin"]

def stamp() -> str:
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

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

def infer_symbol_from_path(path: Path) -> Optional[str]:
    m = SYMBOL_RE.search(str(path).upper().replace("\\", "/"))
    return m.group(1) if m else None

def bad_path(path: Path) -> bool:
    s = str(path).lower()
    return any(x in s for x in BAD_PATH_MARKERS)

def likely_candle_path(path: Path) -> bool:
    s = str(path).lower()
    return any(x in s for x in GOOD_PATH_MARKERS) or bool(infer_symbol_from_path(path))

def pick_col(cols: List[Any], aliases: List[str]) -> Optional[Any]:
    lower = {str(c).lower(): c for c in cols}
    for a in aliases:
        if a.lower() in lower:
            return lower[a.lower()]
    for c in cols:
        cl = str(c).lower()
        for a in aliases:
            if a.lower() in cl:
                return c
    return None

def read_table(path: Path) -> Optional[pd.DataFrame]:
    try:
        if path.suffix.lower() == ".parquet":
            return pd.read_parquet(path)
        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path)
            if len(df.columns) < 5:
                df2 = pd.read_csv(path, header=None)
                if len(df2.columns) >= 5:
                    return df2
            return df
    except Exception:
        return None
    return None

def normalize_time(s: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(s):
        x = pd.to_numeric(s, errors="coerce")
        med = x.dropna().median() if x.notna().any() else None
        if med and med > 1e12:
            return pd.to_datetime(x, unit="ms", errors="coerce", utc=True)
        if med and med > 1e9:
            return pd.to_datetime(x, unit="s", errors="coerce", utc=True)
    return pd.to_datetime(s, errors="coerce", utc=True)

def normalize_candle_file(path: Path, max_rows_per_file: int, min_rows: int) -> Tuple[Optional[pd.DataFrame], Dict[str, Any]]:
    audit = {"path": str(path), "used": False, "reason": "", "rows": 0, "symbols": 0}

    if bad_path(path):
        audit["reason"] = "bad path marker"
        return None, audit
    if not likely_candle_path(path):
        audit["reason"] = "not candle-like path"
        return None, audit

    df = read_table(path)
    if df is None or df.empty:
        audit["reason"] = "unreadable or empty"
        return None, audit

    cols = list(df.columns)

    # OKX raw candle fallback: [ts, open, high, low, close, ...]
    if len(cols) >= 5 and all(str(c).isdigit() for c in cols[:5]):
        time_col = cols[0]
        close_col = cols[4]
        symbol_col = pick_col(cols, SYMBOL_ALIASES)
    else:
        time_col = pick_col(cols, TIME_ALIASES)
        close_col = pick_col(cols, CLOSE_ALIASES)
        symbol_col = pick_col(cols, SYMBOL_ALIASES)

    if time_col is None or close_col is None:
        audit["reason"] = "missing time/close columns"
        return None, audit

    inferred_symbol = infer_symbol_from_path(path)
    out = pd.DataFrame()
    out["event_time"] = normalize_time(df[time_col])
    out["close"] = pd.to_numeric(df[close_col], errors="coerce")

    if symbol_col is not None:
        out["symbol"] = df[symbol_col].astype(str).str.upper()
    elif inferred_symbol:
        out["symbol"] = inferred_symbol
    else:
        audit["reason"] = "no valid symbol"
        return None, audit

    out = out.dropna(subset=["symbol", "event_time", "close"])
    out = out[out["close"] > 0]
    out = out[out["symbol"].astype(str).str.match(r"^[A-Z0-9]{2,25}-USDT-SWAP$")]

    if out.empty:
        audit["reason"] = "no valid OKX swap symbols"
        return None, audit

    out = out[["symbol", "event_time", "close"]].drop_duplicates()
    out = out.sort_values(["symbol", "event_time"])

    # Keep only symbols with enough rows.
    counts = out.groupby("symbol").size()
    good_symbols = counts[counts >= min_rows].index.tolist()
    out = out[out["symbol"].isin(good_symbols)]

    if out.empty:
        audit["reason"] = "not enough rows per valid symbol"
        return None, audit

    if len(out) > max_rows_per_file:
        out = out.groupby("symbol", group_keys=False).tail(max_rows_per_file)

    audit["used"] = True
    audit["reason"] = "accepted"
    audit["rows"] = int(len(out))
    audit["symbols"] = int(out["symbol"].nunique())
    audit["first_time"] = str(out["event_time"].min())
    audit["last_time"] = str(out["event_time"].max())
    return out, audit

def find_engine_path(ws: Path) -> Optional[Path]:
    d = latest_dir(ws / "edge_factory_ret60_shadow_runtime_engine_builder_v2", "ret60_runtime_engine_builder_v2_")
    if not d:
        return None
    p = d / "ret60_shadow_runtime_engine.py"
    return p if p.exists() else None

def scan(ws: Path, max_files: int, max_rows_per_file: int, min_rows: int) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    all_files = []
    for ext in ("*.csv", "*.parquet"):
        all_files.extend(ws.rglob(ext))

    # Prefer files with candle-like path and real symbol in path.
    all_files = sorted(
        all_files,
        key=lambda p: (
            0 if infer_symbol_from_path(p) else 1,
            0 if likely_candle_path(p) else 1,
            -p.stat().st_mtime
        )
    )

    chunks = []
    audits = []
    used = 0

    for p in all_files:
        if used >= max_files:
            break
        df, audit = normalize_candle_file(p, max_rows_per_file=max_rows_per_file, min_rows=min_rows)
        audits.append(audit)
        if df is not None and not df.empty:
            chunks.append(df)
            used += 1

    if not chunks:
        return pd.DataFrame(columns=["symbol", "event_time", "close"]), audits

    merged = pd.concat(chunks, ignore_index=True)
    merged = merged.drop_duplicates(subset=["symbol", "event_time"])
    merged = merged.sort_values(["symbol", "event_time"]).reset_index(drop=True)
    return merged, audits

def signal_preview(df: pd.DataFrame) -> Dict[str, Any]:
    total_hour8 = 0
    total_prior60 = 0
    total_signal75 = 0

    for symbol, g in df.groupby("symbol", sort=False):
        g = g.sort_values("event_time").reset_index(drop=True)
        times = g["event_time"].astype("int64").to_numpy()
        closes = g["close"].astype(float).to_numpy()
        hours = g["event_time"].dt.hour.to_numpy()
        idxs = [i for i, h in enumerate(hours) if h == 8]
        total_hour8 += len(idxs)
        import numpy as np
        for i in idxs:
            target = times[i] - 60 * 60 * 1_000_000_000
            j = np.searchsorted(times, target, side="right") - 1
            if j < 0:
                continue
            total_prior60 += 1
            ret = (closes[i] / closes[j] - 1.0) * 10000.0
            if ret >= 75:
                total_signal75 += 1

    return {
        "hour8_rows": int(total_hour8),
        "prior60_available": int(total_prior60),
        "ret60_ge_75_count": int(total_signal75),
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", default=str(WORKSPACE))
    ap.add_argument("--max_files", type=int, default=120)
    ap.add_argument("--max_rows_per_file", type=int, default=50000)
    ap.add_argument("--min_rows", type=int, default=500)
    ap.add_argument("--dry_run", action="store_true")
    args = ap.parse_args()

    ws = Path(args.workspace)
    out_dir = ws / "edge_factory_ret60_true_candle_replay_runner_v3" / f"ret60_true_candle_replay_v3_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    engine = find_engine_path(ws)
    df, audits = scan(ws, args.max_files, args.max_rows_per_file, args.min_rows)

    replay_csv = out_dir / "ret60_true_candle_replay_input.csv"
    if not df.empty:
        df.to_csv(replay_csv, index=False)

    preview = signal_preview(df) if not df.empty else {"hour8_rows": 0, "prior60_available": 0, "ret60_ge_75_count": 0}

    run_result = {"executed": False, "return_code": None, "stdout_tail": "", "stderr_tail": ""}
    output_root = out_dir / "market_replay_output"

    can_run = bool(engine and engine.exists() and not df.empty and not args.dry_run)

    if can_run:
        cmd = [
            sys.executable,
            str(engine),
            "--shadow_runtime",
            str(replay_csv),
            "--out_dir",
            str(output_root),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        run_result = {
            "executed": True,
            "return_code": proc.returncode,
            "stdout_tail": proc.stdout[-5000:],
            "stderr_tail": proc.stderr[-5000:],
            "cmd": cmd,
        }

    native_csv = output_root / "ret60_shadow_native_events.csv"
    closed_csv = output_root / "ret60_shadow_closed_trades.csv"
    native_rows = 0
    closed_rows = 0
    net_pnl_sum = 0.0
    net_bps_mean = 0.0

    if native_csv.exists():
        ndf = pd.read_csv(native_csv)
        native_rows = len(ndf)
        net_pnl_sum = float(pd.to_numeric(ndf.get("net_pnl_usdt", pd.Series(dtype=float)), errors="coerce").sum()) if native_rows else 0.0
        net_bps_mean = float(pd.to_numeric(ndf.get("net_return_bps_native", pd.Series(dtype=float)), errors="coerce").mean()) if native_rows else 0.0

    if closed_csv.exists():
        cdf = pd.read_csv(closed_csv)
        closed_rows = len(cdf)

    gates = []
    def gate(name, passed, reason=""):
        gates.append({"gate": name, "passed": bool(passed), "reason": str(reason)})

    gate("engine_exists", bool(engine and engine.exists()), engine)
    gate("valid_replay_rows", len(df) > 0, len(df))
    gate("valid_replay_symbols", df["symbol"].nunique() > 0 if not df.empty else False, df["symbol"].nunique() if not df.empty else 0)
    gate("not_global_risk_snapshot", not (df["symbol"].astype(str).str.contains("GLOBAL_RISK", case=False).any() if not df.empty else True), "")
    gate("prior60_available", preview["prior60_available"] > 0, preview["prior60_available"])
    gate("live_blocked", True, "local CSV only")
    gate("active_paper_blocked", True, "local CSV only")
    if can_run:
        gate("engine_return_code_ok", run_result["return_code"] == 0, run_result["return_code"])

    passed = sum(1 for g in gates if g["passed"])
    total = len(gates)

    if args.dry_run:
        status = "RET60_TRUE_CANDLE_REPLAY_PLAN_READY_NOT_EXECUTED"
    elif can_run and run_result["return_code"] == 0 and native_rows > 0:
        status = "RET60_TRUE_CANDLE_REPLAY_EXECUTED_WITH_SIGNALS"
    elif can_run and run_result["return_code"] == 0 and native_rows == 0:
        status = "RET60_TRUE_CANDLE_REPLAY_EXECUTED_NO_SIGNALS"
    elif can_run:
        status = "RET60_TRUE_CANDLE_REPLAY_ENGINE_FAILED"
    else:
        status = "RET60_TRUE_CANDLE_REPLAY_BLOCKED"

    result = {
        "candidate": CANDIDATE,
        "status": status,
        "workspace": str(ws),
        "output_dir": str(out_dir),
        "engine_path": str(engine) if engine else None,
        "replay_csv": str(replay_csv),
        "replay_rows": int(len(df)),
        "replay_symbols": int(df["symbol"].nunique()) if not df.empty else 0,
        "preview": preview,
        "run_result": run_result,
        "native_csv": str(native_csv),
        "closed_csv": str(closed_csv),
        "native_rows": native_rows,
        "closed_rows": closed_rows,
        "net_pnl_sum": net_pnl_sum,
        "net_bps_mean": net_bps_mean,
        "gates_passed": passed,
        "gates_total": total,
        "gates": gates,
        "accepted_files": [a for a in audits if a.get("used")],
        "active_paper_allowed": False,
        "live_allowed": False,
        "next_action": "RUN_MARKET_REPLAY_DRIFT_MONITOR" if native_rows > 0 else "INSPECT_TRUE_CANDLE_SIGNAL_PREVIEW_OR_RULE_BASIS",
    }

    write_json(out_dir / "ret60_true_candle_replay_runner_v3_state.json", result)
    pd.DataFrame(gates).to_csv(out_dir / "ret60_true_candle_replay_runner_v3_gates.csv", index=False)
    pd.DataFrame(audits).to_csv(out_dir / "ret60_true_candle_file_audit_v3.csv", index=False)

    print("EDGE FACTORY RET60 TRUE CANDLE REPLAY RUNNER v3")
    print("=" * 100)
    print(f"workspace : {ws}")
    print(f"output_dir: {out_dir}")
    print(f"status: {status}")
    print(f"engine_path: {engine}")
    print(f"replay_csv: {replay_csv}")
    print(f"replay_rows: {len(df)}")
    print(f"replay_symbols: {df['symbol'].nunique() if not df.empty else 0}")
    print(f"hour8_rows: {preview['hour8_rows']}")
    print(f"prior60_available: {preview['prior60_available']}")
    print(f"ret60_ge_75_count: {preview['ret60_ge_75_count']}")
    print(f"executed: {run_result['executed']}")
    print(f"return_code: {run_result['return_code']}")
    print(f"native_rows: {native_rows}")
    print(f"closed_rows: {closed_rows}")
    print(f"net_pnl_sum: {net_pnl_sum}")
    print(f"net_bps_mean: {net_bps_mean}")
    print(f"gates: {passed}/{total}")
    print("active_paper_allowed: False")
    print("live_allowed: False")

    if passed != total or "BLOCKED" in status or "FAILED" in status:
        print()
        print("BLOCKERS")
        print("-" * 100)
        for g in gates:
            if not g["passed"]:
                print(f"- {g['gate']}: {g['reason']}")
        if run_result.get("stderr_tail"):
            print("stderr_tail:")
            print(run_result["stderr_tail"])

    print()
    print("ACCEPTED FILES SAMPLE")
    print("-" * 100)
    for a in [x for x in audits if x.get("used")][:20]:
        print(f"rows={a.get('rows')} symbols={a.get('symbols')} path={a.get('path')}")

    print()
    print(f"State: {out_dir / 'ret60_true_candle_replay_runner_v3_state.json'}")
    print(f"Gates: {out_dir / 'ret60_true_candle_replay_runner_v3_gates.csv'}")
    print(f"Audit: {out_dir / 'ret60_true_candle_file_audit_v3.csv'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
