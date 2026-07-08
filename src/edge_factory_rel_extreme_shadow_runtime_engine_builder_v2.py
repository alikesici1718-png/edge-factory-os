#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
CANDIDATE = "rel_extreme_reversion_short"

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def latest_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    return sorted(ds, key=lambda x: x.stat().st_mtime, reverse=True)[0] if ds else None

def read_json(path: Optional[Path]) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

def compile_ok(path: Path):
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "OK"
    except Exception as e:
        return False, repr(e)

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_rel_extreme_shadow_runtime_engine_builder_v2" / f"rel_extreme_runtime_engine_builder_v2_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    adapter_dir = latest_dir(
        WORKSPACE / "edge_factory_rel_extreme_shadow_logger_adapter_builder_v1",
        "rel_extreme_adapter_builder_",
    )
    adapter_audit_dir = latest_dir(
        WORKSPACE / "edge_factory_rel_extreme_shadow_adapter_implementation_auditor_v1",
        "rel_extreme_adapter_audit_",
    )
    spec_dir = latest_dir(
        WORKSPACE / "edge_factory_rel_extreme_shadow_spec_review_v1",
        "rel_extreme_shadow_spec_",
    )

    manifest_path = adapter_dir / "rel_extreme_shadow_adapter_manifest.json" if adapter_dir else None
    adapter_audit_path = adapter_audit_dir / "rel_extreme_shadow_adapter_implementation_audit_state.json" if adapter_audit_dir else None
    spec_path = spec_dir / "rel_extreme_shadow_spec.json" if spec_dir else None

    manifest = read_json(manifest_path)
    adapter_audit = read_json(adapter_audit_path)
    spec = read_json(spec_path)

    adapter_path = Path(str(manifest.get("adapter_path", ""))) if manifest.get("adapter_path") else None

    if not adapter_path or not adapter_path.exists():
        raise SystemExit("adapter missing; run adapter builder first")
    if adapter_audit.get("implementation_audit_passed") is not True:
        raise SystemExit("adapter audit has not passed")
    if spec.get("live_allowed") is not False or spec.get("active_paper_allowed") is not False:
        raise SystemExit("unsafe spec flags")

    engine_path = out_dir / "rel_extreme_shadow_runtime_engine_v2.py"
    sandbox_root = WORKSPACE / "paper_run_shadow_rel_extreme_reversion_short"

    engine_code = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import pandas as pd

ADAPTER_PATH = Path(r"{adapter_path}")
WORKSPACE = Path(r"{WORKSPACE}")
SANDBOX_ROOT_DEFAULT = Path(r"{sandbox_root}")
SYMBOL_RE = re.compile(r"([A-Z0-9]{{1,25}})-USDT-SWAP", re.I)

CANDIDATE_KEY = "rel_extreme_reversion_short"
SANDBOX_ONLY = True
LIVE_ALLOWED = False
ACTIVE_PAPER_ALLOWED = False
SHADOW_START_ALLOWED_BY_THIS_FILE = False
PRIVATE_EXCHANGE_API_ALLOWED = False
ORDER_PLACEMENT_ALLOWED = False

LOOKBACK_HOURS = 6
HOLD_HOURS = 24
COST_BPS = 25.0
CAP_SIGNALS_PER_HOUR = 1

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def load_adapter():
    spec = importlib.util.spec_from_file_location("rel_extreme_shadow_adapter", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import adapter: {{ADAPTER_PATH}}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str), encoding="utf-8")

def append_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            w.writeheader()
        for r in rows:
            w.writerow(r)

def infer_symbol(path: Path) -> Optional[str]:
    m = SYMBOL_RE.search(str(path).upper().replace("\\\\", "/"))
    return m.group(1) if m else None

def robust_time_parse(s: pd.Series) -> pd.Series:
    num = pd.to_numeric(s, errors="coerce")
    if len(num) and num.notna().mean() >= 0.80:
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

def find_candle_files(candle_dir: Path, max_files: int = 0) -> list[Path]:
    root = candle_dir if candle_dir.exists() else WORKSPACE
    files = []
    for p in root.rglob("*.csv"):
        s = str(p).lower()
        if ("raw\\\\candles_long_1m" in s or "raw/candles_long_1m" in s) and infer_symbol(p):
            files.append(p)
    files = sorted(files)
    if max_files and max_files > 0:
        files = files[:max_files]
    return files

def read_hourly_close(path: Path, max_rows_per_file: int = 0) -> Optional[pd.Series]:
    symbol = infer_symbol(path)
    if not symbol:
        return None

    try:
        df = pd.read_csv(path)
        if len(df.columns) < 5:
            df2 = pd.read_csv(path, header=None)
            if len(df2.columns) >= 5:
                df = df2
    except Exception:
        return None

    if max_rows_per_file and max_rows_per_file > 0 and len(df) > max_rows_per_file:
        df = df.tail(max_rows_per_file).copy()

    cols = list(df.columns)

    if len(cols) >= 5 and all(str(c).isdigit() for c in cols[:5]):
        time_col = cols[0]
        close_col = cols[4]
    else:
        lower = {{str(c).lower(): c for c in cols}}
        time_col = lower.get("event_time") or lower.get("timestamp") or lower.get("time") or lower.get("open_time") or cols[0]
        close_col = lower.get("close") or lower.get("c") or lower.get("close_price") or cols[4]

    tmp = pd.DataFrame()
    tmp["time"] = robust_time_parse(df[time_col])
    tmp["close"] = pd.to_numeric(df[close_col], errors="coerce")
    tmp = tmp.dropna(subset=["time", "close"])
    tmp = tmp[tmp["close"] > 0].copy()

    if len(tmp) < 1000:
        return None

    tmp["hour"] = tmp["time"].dt.floor("h")
    hourly = tmp.sort_values("time").groupby("hour")["close"].last()
    hourly.name = symbol

    if len(hourly) < LOOKBACK_HOURS + HOLD_HOURS + 10:
        return None

    return hourly

def build_close_panel(candle_dir: Path, max_files: int = 0, max_rows_per_file: int = 0) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    files = find_candle_files(candle_dir, max_files=max_files)
    series = []
    audit = []

    for p in files:
        sym = infer_symbol(p)
        s = read_hourly_close(p, max_rows_per_file=max_rows_per_file)
        if s is None:
            audit.append({{"path": str(p), "symbol": sym, "used": False, "reason": "unreadable_or_too_few_rows"}})
            continue
        series.append(s)
        audit.append({{"path": str(p), "symbol": sym, "used": True, "hourly_rows": int(len(s)), "first_hour": str(s.index.min()), "last_hour": str(s.index.max())}})

    if not series:
        return pd.DataFrame(), audit

    close = pd.concat(series, axis=1, sort=True).sort_index()
    close = close.dropna(axis=1, how="all")

    if close.columns.duplicated().any():
        close = close.T.groupby(level=0).last().T
        close = close.sort_index()

    return close, audit

def run_shadow_runtime_once(candle_dir: Path, out_dir: Path, max_files: int = 0, max_rows_per_file: int = 0, market_method: str = "median") -> dict[str, Any]:
    adapter = load_adapter()
    out_dir.mkdir(parents=True, exist_ok=True)

    close, audit = build_close_panel(candle_dir, max_files=max_files, max_rows_per_file=max_rows_per_file)
    audit_csv = out_dir / "rel_extreme_shadow_candle_file_audit.csv"
    if audit:
        pd.DataFrame(audit).to_csv(audit_csv, index=False)

    if close.empty:
        hb = write_heartbeat(out_dir, {{"runtime_mode": "shadow_runtime_once", "status": "NO_USABLE_CANDLES"}})
        return {{"ok": False, "status": "NO_USABLE_CANDLES", "heartbeat_json": str(hb), "audit_csv": str(audit_csv), "live_allowed": False, "active_paper_allowed": False}}

    coin_ret = (close / close.shift(LOOKBACK_HOURS) - 1.0) * 10000.0
    market_ret = coin_ret.median(axis=1, skipna=True) if market_method == "median" else coin_ret.mean(axis=1, skipna=True)
    rel_ret = coin_ret.sub(market_ret, axis=0)

    latest_hour = close.index.max()
    signal_rows = []

    for sym in close.columns:
        try:
            entry_close = float(close.loc[latest_hour, sym])
            prior = close[sym].shift(LOOKBACK_HOURS).loc[latest_hour]
            coin_ret_bps = adapter.compute_coin_return_bps(entry_close, float(prior))
            mkt_bps = float(market_ret.loc[latest_hour])
            if adapter.rel_rule_pass(coin_ret_bps, mkt_bps):
                signal_rows.append(adapter.build_signal_row(sym, latest_hour, coin_ret_bps, mkt_bps, entry_close))
        except Exception:
            continue

    capped = adapter.rank_and_cap_signals(signal_rows)

    signals_csv = out_dir / "rel_extreme_shadow_signals.csv"
    append_csv(signals_csv, capped)

    # Historical closed-trade file only if the panel has future data after selected signal hour.
    # In a real forward shadow run this usually remains empty until exit time is reached.
    closed_rows = []
    exit_hour = latest_hour + pd.Timedelta(hours=HOLD_HOURS)

    if exit_hour in close.index:
        for r in capped:
            sym = r["symbol"]
            try:
                exit_close = float(close.loc[exit_hour, sym])
                entry_close = float(r["entry_close"])
                net_bps = adapter.compute_short_return_bps(entry_close, exit_close)
                closed_rows.append({{**r, "exit_time": str(exit_hour), "exit_close": exit_close, "net_return_bps": net_bps, "closed_at": utc_now_iso(), "runtime_mode": "shadow_runtime_once", "live_allowed": False, "active_paper_allowed": False}})
            except Exception:
                pass

    closed_csv = out_dir / "rel_extreme_shadow_closed_trades.csv"
    append_csv(closed_csv, closed_rows)

    hb = write_heartbeat(out_dir, {{
        "runtime_mode": "shadow_runtime_once",
        "status": "OK",
        "latest_hour": str(latest_hour),
        "close_rows": int(close.shape[0]),
        "close_symbols": int(close.shape[1]),
        "raw_signal_count": len(signal_rows),
        "capped_signal_count": len(capped),
        "closed_count": len(closed_rows),
        "signals_csv": str(signals_csv),
        "closed_csv": str(closed_csv),
        "audit_csv": str(audit_csv),
    }})

    result = {{
        "ok": True,
        "status": "OK",
        "latest_hour": str(latest_hour),
        "close_rows": int(close.shape[0]),
        "close_symbols": int(close.shape[1]),
        "raw_signal_count": len(signal_rows),
        "capped_signal_count": len(capped),
        "closed_count": len(closed_rows),
        "signals_csv": str(signals_csv),
        "closed_trades_csv": str(closed_csv),
        "heartbeat_json": str(hb),
        "audit_csv": str(audit_csv),
        "live_allowed": False,
        "active_paper_allowed": False,
    }}

    write_json(out_dir / "rel_extreme_shadow_runtime_result.json", result)
    return result

def write_heartbeat(out_dir: Path, extra: dict[str, Any] | None = None) -> Path:
    hb = {{
        "candidate": CANDIDATE_KEY,
        "timestamp": utc_now_iso(),
        "sandbox_only": True,
        "live_allowed": False,
        "active_paper_allowed": False,
        "shadow_start_allowed_by_this_file": False,
        "private_exchange_api_allowed": False,
        "order_placement_allowed": False,
    }}
    if extra:
        hb.update(extra)
    p = out_dir / "rel_extreme_shadow_heartbeat.json"
    write_json(p, hb)
    return p

def self_test(out_dir: Path) -> dict[str, Any]:
    adapter = load_adapter()
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_rows = [
        adapter.build_signal_row("AAA", pd.Timestamp("2026-01-01T12:00:00Z"), 1000.0, 200.0, 1100.0),
        adapter.build_signal_row("BBB", pd.Timestamp("2026-01-01T12:00:00Z"), 900.0, 200.0, 1040.0),
        adapter.build_signal_row("CCC", pd.Timestamp("2026-01-01T12:00:00Z"), 800.0, 100.0, 1030.0),
    ]

    capped = adapter.rank_and_cap_signals(raw_rows)
    signals_csv = out_dir / "rel_extreme_shadow_signals.csv"
    append_csv(signals_csv, capped)

    closed_rows = []
    for r in capped:
        entry = float(r["entry_close"])
        exit_close = entry * 0.97
        net_bps = adapter.compute_short_return_bps(entry, exit_close)
        closed_rows.append({{**r, "exit_close": exit_close, "net_return_bps": net_bps, "closed_at": utc_now_iso(), "runtime_mode": "self_test_shadow_runtime", "live_allowed": False, "active_paper_allowed": False}})

    closed_csv = out_dir / "rel_extreme_shadow_closed_trades.csv"
    append_csv(closed_csv, closed_rows)

    hb = write_heartbeat(out_dir, {{"runtime_mode": "self_test_shadow_runtime", "raw_signal_count": len(raw_rows), "capped_signal_count": len(capped), "closed_count": len(closed_rows)}})

    result = {{"ok": len(capped) == 1 and len(closed_rows) == 1, "raw_signal_count": len(raw_rows), "capped_signal_count": len(capped), "closed_count": len(closed_rows), "signals_csv": str(signals_csv), "closed_trades_csv": str(closed_csv), "heartbeat_json": str(hb), "live_allowed": False, "active_paper_allowed": False}}
    write_json(out_dir / "rel_extreme_shadow_runtime_self_test_result.json", result)
    return result

def main():
    ap = argparse.ArgumentParser(description="Rel extreme real market shadow runtime engine v2.")
    ap.add_argument("--self_test", action="store_true")
    ap.add_argument("--shadow_runtime", action="store_true")
    ap.add_argument("--candle_dir", default=str(WORKSPACE))
    ap.add_argument("--out_dir", default=str(SANDBOX_ROOT_DEFAULT))
    ap.add_argument("--max_files", type=int, default=0)
    ap.add_argument("--max_rows_per_file", type=int, default=0)
    ap.add_argument("--market_method", choices=["median", "mean"], default="median")
    ap.add_argument("--poll_seconds", type=int, default=60)
    ap.add_argument("--once", action="store_true")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)

    if args.self_test:
        result = self_test(out_dir)
        print("REL EXTREME SHADOW RUNTIME ENGINE v2 SELF TEST")
        print("=" * 80)
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result.get("ok") else 1)

    if args.shadow_runtime:
        if args.once:
            result = run_shadow_runtime_once(Path(args.candle_dir), out_dir, args.max_files, args.max_rows_per_file, args.market_method)
            print("REL EXTREME SHADOW RUNTIME ENGINE v2 ONCE")
            print("=" * 80)
            print(json.dumps(result, indent=2))
            raise SystemExit(0 if result.get("ok") else 1)

        while True:
            result = run_shadow_runtime_once(Path(args.candle_dir), out_dir, args.max_files, args.max_rows_per_file, args.market_method)
            print(json.dumps(result, indent=2))
            time.sleep(max(10, int(args.poll_seconds)))

    print("Use --self_test or --shadow_runtime --once. Safety flags remain false.")
    print("live_allowed: False")
    print("active_paper_allowed: False")

if __name__ == "__main__":
    main()
'''

    engine_path.write_text(engine_code, encoding="utf-8")

    comp_ok, comp_err = compile_ok(engine_path)

    self_test_dir = out_dir / "self_test"
    proc_self = subprocess.run(
        [sys.executable, str(engine_path), "--self_test", "--out_dir", str(self_test_dir)],
        capture_output=True,
        text=True,
        timeout=45,
    )
    self_result = read_json(self_test_dir / "rel_extreme_shadow_runtime_self_test_result.json")
    self_ok = proc_self.returncode == 0 and self_result.get("ok") is True

    runtime_test_dir = out_dir / "shadow_runtime_once_test"
    proc_runtime = subprocess.run(
        [
            sys.executable,
            str(engine_path),
            "--shadow_runtime",
            "--once",
            "--out_dir",
            str(runtime_test_dir),
            "--candle_dir",
            str(WORKSPACE),
            "--max_files",
            "40",
            "--max_rows_per_file",
            "50000",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    runtime_result = read_json(runtime_test_dir / "rel_extreme_shadow_runtime_result.json")
    runtime_ok = proc_runtime.returncode == 0 and runtime_result.get("ok") is True

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "output_dir": str(out_dir),
        "builder_status": "REL_EXTREME_SHADOW_RUNTIME_ENGINE_V2_WRITTEN_NOT_APPROVED_TO_START",
        "runtime_engine_path": str(engine_path),
        "adapter_path": str(adapter_path),
        "spec_path": str(spec_path),
        "engine_compiles": comp_ok,
        "compile_error": comp_err,
        "self_test_ok": self_ok,
        "shadow_runtime_once_test_ok": runtime_ok,
        "self_test_stdout": proc_self.stdout[-3000:],
        "self_test_stderr": proc_self.stderr[-3000:],
        "runtime_test_stdout": proc_runtime.stdout[-3000:],
        "runtime_test_stderr": proc_runtime.stderr[-3000:],
        "runtime_result": runtime_result,
        "sandbox_root": str(sandbox_root),
        "shadow_start_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "next_action": "RUN_REL_EXTREME_RUNTIME_ENGINE_AUDITOR_V2_THEN_PREFLIGHT",
    }

    write_json(out_dir / "rel_extreme_shadow_runtime_engine_builder_v2_state.json", state)

    print("EDGE FACTORY REL EXTREME SHADOW RUNTIME ENGINE BUILDER v2")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"runtime_engine_path: {engine_path}")
    print(f"engine_compiles: {comp_ok}")
    print(f"self_test_ok: {self_ok}")
    print(f"shadow_runtime_once_test_ok: {runtime_ok}")
    print(f"sandbox_root: {sandbox_root}")
    print("shadow_start_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print()

    if not comp_ok:
        print("COMPILE ERROR")
        print(comp_err)
    if proc_self.stdout:
        print("SELF TEST STDOUT")
        print("-" * 100)
        print(proc_self.stdout[-2000:])
    if proc_self.stderr:
        print("SELF TEST STDERR")
        print("-" * 100)
        print(proc_self.stderr[-2000:])
    if proc_runtime.stdout:
        print("SHADOW RUNTIME ONCE TEST STDOUT")
        print("-" * 100)
        print(proc_runtime.stdout[-2500:])
    if proc_runtime.stderr:
        print("SHADOW RUNTIME ONCE TEST STDERR")
        print("-" * 100)
        print(proc_runtime.stderr[-2500:])

    print(f"State : {out_dir / 'rel_extreme_shadow_runtime_engine_builder_v2_state.json'}")
    print(f"Engine: {engine_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
