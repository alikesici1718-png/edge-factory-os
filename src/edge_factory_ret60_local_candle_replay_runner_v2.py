#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Replays the ret60_reversal_short strategy rules against local 1-minute candle CSV/parquet files in the workspace, constructing hourly close panels per symbol and simulating short entries based on configurable threshold parameters. Outputs a replay state JSON, trades CSV, and candle audit CSV to a timestamped directory under the configured output root.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List

import pandas as pd

WORKSPACE_DEFAULT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
CANDIDATE = "ret60_reversal_short"

TIME_ALIASES = ["event_time", "timestamp", "time", "datetime", "open_time", "ts"]
CLOSE_ALIASES = ["close", "c", "close_price", "last", "price"]
SYMBOL_ALIASES = ["symbol", "inst_id", "inst", "ticker", "coin"]

SKIP_DIR_MARKERS = [
    "edge_factory_ret60_",
    "edge_factory_os_",
    "paper_run_",
    "live_",
    "__pycache__",
]

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

def infer_symbol(path: Path) -> str:
    text = str(path).replace("\\", "/").upper()
    import re
    m = re.search(r"([A-Z0-9]+-USDT-SWAP)", text)
    if m:
        return m.group(1)
    m = re.search(r"([A-Z0-9]+USDT)", text)
    if m:
        return m.group(1).replace("USDT", "-USDT-SWAP")
    return path.stem.upper()

def should_skip(path: Path) -> bool:
    s = str(path).lower()
    return any(x.lower() in s for x in SKIP_DIR_MARKERS)

def pick_col(cols: List[str], aliases: List[str]) -> Optional[str]:
    low = {str(c).lower(): c for c in cols}
    for a in aliases:
        if a.lower() in low:
            return low[a.lower()]
    for c in cols:
        cl = str(c).lower()
        for a in aliases:
            if a.lower() == cl or a.lower() in cl:
                return c
    return None

def load_candidate_file(path: Path, max_rows_per_file: int) -> Optional[pd.DataFrame]:
    try:
        if path.suffix.lower() == ".parquet":
            df = pd.read_parquet(path)
        elif path.suffix.lower() == ".csv":
            df = pd.read_csv(path)
        else:
            return None
    except Exception:
        return None

    if df.empty:
        return None

    time_col = pick_col(list(df.columns), TIME_ALIASES)
    close_col = pick_col(list(df.columns), CLOSE_ALIASES)
    symbol_col = pick_col(list(df.columns), SYMBOL_ALIASES)

    if time_col is None or close_col is None:
        return None

    out = pd.DataFrame()
    out["event_time"] = pd.to_datetime(df[time_col], errors="coerce", utc=True)
    out["close"] = pd.to_numeric(df[close_col], errors="coerce")

    if symbol_col is not None:
        out["symbol"] = df[symbol_col].astype(str)
    else:
        out["symbol"] = infer_symbol(path)

    out = out.dropna(subset=["symbol", "event_time", "close"])
    out = out[out["close"] > 0]
    if out.empty:
        return None

    out = out[["symbol", "event_time", "close"]].sort_values(["symbol", "event_time"])

    if len(out) > max_rows_per_file:
        out = out.tail(max_rows_per_file)

    return out

def find_engine_path(workspace: Path) -> Optional[Path]:
    d = latest_dir(workspace / "edge_factory_ret60_shadow_runtime_engine_builder_v2", "ret60_runtime_engine_builder_v2_")
    if not d:
        return None
    p = d / "ret60_shadow_runtime_engine.py"
    return p if p.exists() else None

def scan_candle_files(workspace: Path, max_files: int, max_rows_per_file: int, min_rows_per_symbol: int) -> tuple[pd.DataFrame, List[Dict[str, Any]]]:
    files = []
    for ext in ("*.csv", "*.parquet"):
        files.extend(workspace.rglob(ext))

    files = [p for p in files if not should_skip(p)]
    files = sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)

    chunks = []
    audit = []
    used = 0

    for p in files:
        if used >= max_files:
            break

        df = load_candidate_file(p, max_rows_per_file=max_rows_per_file)
        if df is None or df.empty:
            continue

        by_symbol = df.groupby("symbol").size()
        strong_symbols = by_symbol[by_symbol >= min_rows_per_symbol].index.tolist()
        if not strong_symbols:
            audit.append({"path": str(p), "used": False, "rows": len(df), "reason": "not enough rows per symbol"})
            continue

        df = df[df["symbol"].isin(strong_symbols)]
        chunks.append(df)
        used += 1
        audit.append({"path": str(p), "used": True, "rows": len(df), "symbols": len(strong_symbols), "reason": "accepted"})

    if not chunks:
        return pd.DataFrame(columns=["symbol", "event_time", "close"]), audit

    merged = pd.concat(chunks, ignore_index=True)
    merged = merged.drop_duplicates(subset=["symbol", "event_time"]).sort_values(["symbol", "event_time"])
    return merged, audit

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", default=str(WORKSPACE_DEFAULT))
    ap.add_argument("--max_files", type=int, default=80)
    ap.add_argument("--max_rows_per_file", type=int, default=20000)
    ap.add_argument("--min_rows_per_symbol", type=int, default=900)
    ap.add_argument("--max_engine_rows", type=int, default=250000)
    ap.add_argument("--dry_run", action="store_true")
    args = ap.parse_args()

    ws = Path(args.workspace)
    out_dir = ws / "edge_factory_ret60_local_candle_replay_runner_v2" / f"ret60_local_replay_v2_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    engine = find_engine_path(ws)
    df, audit = scan_candle_files(
        ws,
        max_files=args.max_files,
        max_rows_per_file=args.max_rows_per_file,
        min_rows_per_symbol=args.min_rows_per_symbol,
    )

    replay_csv = out_dir / "ret60_real_local_candle_replay_input.csv"
    if not df.empty:
        df.to_csv(replay_csv, index=False)

    gates = []
    def gate(name: str, passed: bool, reason: str = ""):
        gates.append({"gate": name, "passed": bool(passed), "reason": str(reason)})

    gate("runtime_engine_exists", bool(engine and engine.exists()), str(engine))
    gate("replay_input_rows_positive", len(df) > 0, len(df))
    gate("replay_input_symbols_positive", df["symbol"].nunique() > 0 if not df.empty else False, df["symbol"].nunique() if not df.empty else 0)
    gate("dry_run_not_required", True, "dry_run=" + str(args.dry_run))
    gate("live_blocked", True, "local CSV replay only")
    gate("active_paper_blocked", True, "local CSV replay only")

    can_run = all(g["passed"] for g in gates) and not args.dry_run

    run_result = {
        "executed": False,
        "return_code": None,
        "stdout_tail": "",
        "stderr_tail": "",
        "sandbox_out_dir": str(out_dir / "market_replay_output"),
    }

    if can_run:
        sandbox_out = out_dir / "market_replay_output"
        cmd = [
            sys.executable,
            str(engine),
            "--shadow_runtime",
            str(replay_csv),
            "--out_dir",
            str(sandbox_out),
            "--max_rows",
            str(args.max_engine_rows),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        run_result = {
            "executed": True,
            "return_code": proc.returncode,
            "stdout_tail": proc.stdout[-5000:],
            "stderr_tail": proc.stderr[-5000:],
            "sandbox_out_dir": str(sandbox_out),
            "cmd": cmd,
        }

    native_csv = Path(run_result["sandbox_out_dir"]) / "ret60_shadow_native_events.csv"
    closed_csv = Path(run_result["sandbox_out_dir"]) / "ret60_shadow_closed_trades.csv"
    heartbeat_json = Path(run_result["sandbox_out_dir"]) / "ret60_shadow_heartbeat.json"
    state_json = Path(run_result["sandbox_out_dir"]) / "ret60_shadow_runtime_state.json"

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

    if can_run:
        gate("engine_return_code_ok", run_result["return_code"] == 0, run_result["return_code"])
        gate("market_native_output_exists", native_csv.exists(), native_csv)
        gate("market_closed_output_exists", closed_csv.exists(), closed_csv)
        gate("market_heartbeat_exists", heartbeat_json.exists(), heartbeat_json)
        gate("market_state_exists", state_json.exists(), state_json)

    passed = sum(1 for g in gates if g["passed"])
    total = len(gates)

    if args.dry_run:
        status = "RET60_LOCAL_CANDLE_REPLAY_PLAN_READY_NOT_EXECUTED"
    elif can_run and run_result["return_code"] == 0:
        status = "RET60_LOCAL_CANDLE_REPLAY_EXECUTED"
    elif can_run:
        status = "RET60_LOCAL_CANDLE_REPLAY_EXECUTION_FAILED"
    else:
        status = "RET60_LOCAL_CANDLE_REPLAY_BLOCKED"

    result = {
        "candidate": CANDIDATE,
        "status": status,
        "workspace": str(ws),
        "output_dir": str(out_dir),
        "runtime_engine_path": str(engine) if engine else None,
        "replay_input_csv": str(replay_csv),
        "replay_input_rows": int(len(df)),
        "replay_input_symbols": int(df["symbol"].nunique()) if not df.empty else 0,
        "dry_run": args.dry_run,
        "run_result": run_result,
        "native_csv": str(native_csv),
        "closed_csv": str(closed_csv),
        "heartbeat_json": str(heartbeat_json),
        "state_json": str(state_json),
        "native_rows": native_rows,
        "closed_rows": closed_rows,
        "net_pnl_sum": net_pnl_sum,
        "net_bps_mean": net_bps_mean,
        "gates_passed": passed,
        "gates_total": total,
        "gates": gates,
        "file_audit_sample": audit[:200],
        "market_drift_sample_ready": bool(native_rows > 0 and closed_rows > 0),
        "active_paper_allowed": False,
        "live_allowed": False,
        "next_action": "RUN_DRIFT_MONITOR_ON_LOCAL_MARKET_REPLAY" if native_rows > 0 else "INSPECT_CANDLE_SCAN_OR_INPUT_SCHEMA",
    }

    write_json(out_dir / "ret60_local_candle_replay_runner_v2_state.json", result)
    pd.DataFrame(gates).to_csv(out_dir / "ret60_local_candle_replay_runner_v2_gates.csv", index=False)
    pd.DataFrame(audit).to_csv(out_dir / "ret60_local_candle_file_audit.csv", index=False)

    print("EDGE FACTORY RET60 LOCAL CANDLE REPLAY RUNNER v2")
    print("=" * 100)
    print(f"workspace : {ws}")
    print(f"output_dir: {out_dir}")
    print(f"status: {status}")
    print(f"runtime_engine_path: {engine}")
    print(f"replay_input_csv: {replay_csv}")
    print(f"replay_input_rows: {len(df)}")
    print(f"replay_input_symbols: {df['symbol'].nunique() if not df.empty else 0}")
    print(f"executed: {run_result['executed']}")
    print(f"return_code: {run_result['return_code']}")
    print(f"native_rows: {native_rows}")
    print(f"closed_rows: {closed_rows}")
    print(f"net_pnl_sum: {net_pnl_sum}")
    print(f"net_bps_mean: {net_bps_mean}")
    print(f"gates: {passed}/{total}")
    print("active_paper_allowed: False")
    print("live_allowed: False")

    if passed != total or status.endswith("FAILED") or status.endswith("BLOCKED"):
        print()
        print("BLOCKERS")
        print("-" * 100)
        for g in gates:
            if not g["passed"]:
                print(f"- {g['gate']}: {g['reason']}")
        if run_result["stderr_tail"]:
            print("stderr_tail:")
            print(run_result["stderr_tail"])

    print()
    print(f"State: {out_dir / 'ret60_local_candle_replay_runner_v2_state.json'}")
    print(f"Gates: {out_dir / 'ret60_local_candle_replay_runner_v2_gates.csv'}")
    print(f"File audit: {out_dir / 'ret60_local_candle_file_audit.csv'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
