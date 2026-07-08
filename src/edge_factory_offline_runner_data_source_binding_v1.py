#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_offline_runner_data_source_binding_v1"
MASTER = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"

def latest_request() -> Path | None:
    root = WORKSPACE / "edge_factory_contract_to_runner_adapter_v1"
    files = list(root.rglob("offline_runner_request_v1.json"))
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def read_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e)}

def get_columns(path: Path) -> list[str]:
    try:
        return list(pd.read_csv(path, nrows=5).columns)
    except Exception:
        return []

def infer_symbol(path: Path) -> str:
    name = path.name.upper()
    m = re.search(r"([A-Z0-9]+)-USDT-SWAP", name)
    if m:
        return m.group(1)
    return path.parents[2].name.upper() if len(path.parents) >= 3 else path.stem.upper()

def has_required_ohlcv(cols: list[str]) -> bool:
    low = {str(c).lower() for c in cols}
    has_time = bool(low & {"time", "timestamp", "datetime", "ts", "open_time"})
    has_close = bool(low & {"close", "c", "close_price", "last"})
    has_high = bool(low & {"high", "h"})
    has_low = bool(low & {"low", "l"})
    has_open = bool(low & {"open", "o"})
    has_vol = bool(low & {"volccyquote", "vol_ccy_quote", "quote_volume", "volume_quote", "turnover", "vol_quote", "volume"})
    return has_time and has_open and has_high and has_low and has_close and has_vol

def is_master_subpath(path: Path) -> bool:
    try:
        path.resolve().relative_to(MASTER.resolve())
        return True
    except Exception:
        return False

def main() -> int:
    ap = argparse.ArgumentParser(description="Bind broad raw candle sources to offline runner request.")
    ap.add_argument("--request", default="")
    ap.add_argument("--max_symbols", type=int, default=300)
    args = ap.parse_args()

    request_path = Path(args.request) if args.request else latest_request()

    out_dir = OUT_ROOT / f"data_source_binding_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    req = read_json(request_path)

    blockers = []
    if not request_path or not request_path.exists():
        blockers.append("RUNNER_REQUEST_NOT_FOUND")
    if "__read_error__" in req:
        blockers.append("RUNNER_REQUEST_READ_ERROR")

    # Broad all-coin raw candle pattern.
    patterns = [
        "*\\raw\\candles_long_1m\\*-USDT-SWAP_1m_2025-04-30_2026-04-30.csv",
        "*/raw/candles_long_1m/*-USDT-SWAP_1m_2025-04-30_2026-04-30.csv",
    ]

    files: list[Path] = []
    for pat in patterns:
        files.extend(WORKSPACE.glob(pat))

    # Fallback: broader 1m raw candle files.
    if not files:
        files.extend(WORKSPACE.glob("*\\raw\\candles_long_1m\\*.csv"))
        files.extend(WORKSPACE.glob("*/raw/candles_long_1m/*.csv"))

    unique = []
    seen = set()
    for p in files:
        if p in seen:
            continue
        seen.add(p)
        if is_master_subpath(p):
            continue
        unique.append(p)

    rows = []
    for p in unique:
        cols = get_columns(p)
        ok = has_required_ohlcv(cols)
        rows.append({
            "symbol": infer_symbol(p),
            "path": str(p),
            "ok_ohlcv": ok,
            "columns": cols,
            "size_mb": round(p.stat().st_size / (1024 * 1024), 3) if p.exists() else None,
            "mtime_utc": datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat() if p.exists() else None,
        })

    valid_rows = [r for r in rows if r["ok_ohlcv"]]
    valid_rows = sorted(valid_rows, key=lambda r: r["symbol"])[:args.max_symbols]

    if not valid_rows:
        blockers.append("NO_VALID_RAW_CANDLE_FILES_FOUND")

    if blockers:
        binding_status = "DATA_SOURCE_BINDING_BLOCKED"
        resolved_request_path = ""
        source_files = []
        next_action = "FIX_DATA_SOURCE_PATHS"
    else:
        binding_status = "DATA_SOURCE_BINDING_READY"
        source_files = [r["path"] for r in valid_rows]

        resolved_req = dict(req)
        resolved_req["source_files"] = source_files
        resolved_req["data_source_binding"] = {
            "binding_version": "edge_factory_data_source_binding_v1",
            "bound_at": datetime.now(timezone.utc).isoformat(),
            "source_type": "broad_raw_1m_candles_long",
            "symbol_count": len(valid_rows),
            "symbols": [r["symbol"] for r in valid_rows],
            "feature_build_required": True,
            "feature_plan": {
                "resample": "1m candles -> 1h bars",
                "coin_ret6_bps": "derive per symbol from 1h close pct_change(6)*10000",
                "coin_ret24_bps": "derive per symbol from 1h close pct_change(24)*10000",
                "mkt_ret6_bps": "derive from median market 1h close index pct_change(6)*10000",
                "mkt_ret24_bps": "derive from median market 1h close index pct_change(24)*10000",
                "entry_vol_quote": "derive from summed quote volume over 1h",
                "entry_range_bps": "derive from 1h high/low/close"
            },
            "runner_execution_allowed": False,
            "reason_runner_blocked": "feature panel must be built before offline runner",
        }

        resolved_request_path = str(out_dir / "offline_runner_request_v1_data_bound.json")
        Path(resolved_request_path).write_text(
            json.dumps(resolved_req, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8"
        )
        next_action = "BUILD_FEATURE_PANEL_FROM_BOUND_CANDLES"

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "request_path": str(request_path) if request_path else None,
        "candidate_key": req.get("candidate_key"),
        "family_key": req.get("family_key"),
        "binding_status": binding_status,
        "blockers": blockers,
        "raw_files_found": len(rows),
        "valid_ohlcv_files": len(valid_rows),
        "resolved_request_path": resolved_request_path,
        "next_action": next_action,
        "runner_execution_allowed": False,
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Binding only maps data files to runner request.",
            "Does not run backtests.",
            "Does not touch MASTER_UPPER_SYSTEM.",
            "Does not start/stop processes.",
            "Does not place orders.",
            "Does not enable live trading."
        ],
    }

    state_path = out_dir / "data_source_binding_v1_state.json"
    sources_csv = out_dir / "data_source_binding_v1_sources.csv"
    report_path = out_dir / "data_source_binding_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    pd.DataFrame(rows).drop(columns=["columns"], errors="ignore").to_csv(sources_csv, index=False)

    md = []
    md.append("# Edge Factory Offline Runner Data Source Binding v1")
    md.append("")
    md.append(f"Status: `{binding_status}`")
    md.append(f"Candidate: `{req.get('candidate_key')}`")
    md.append(f"Raw files found: `{len(rows)}`")
    md.append(f"Valid OHLCV files: `{len(valid_rows)}`")
    md.append(f"Next action: `{next_action}`")
    md.append("")
    if resolved_request_path:
        md.append("## Resolved request")
        md.append(f"`{resolved_request_path}`")
    md.append("")
    md.append("## Safety")
    md.append("- runner_execution_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OFFLINE RUNNER DATA SOURCE BINDING v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"request   : {request_path}")
    print(f"candidate : {req.get('candidate_key')}")
    print(f"binding_status: {binding_status}")
    print(f"raw_files_found: {len(rows)}")
    print(f"valid_ohlcv_files: {len(valid_rows)}")
    print(f"resolved_request_path: {resolved_request_path}")
    print(f"next_action: {next_action}")
    print("runner_execution_allowed: False")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("SAMPLE SOURCES")
    print("-" * 100)
    if valid_rows:
        df = pd.DataFrame(valid_rows[:30])
        print(df[["symbol", "ok_ohlcv", "size_mb", "path"]].to_string(index=False))
    else:
        print("No valid OHLCV files.")
    print()
    print(f"State : {state_path}")
    print(f"Sources: {sources_csv}")
    print(f"Report : {report_path}")

if __name__ == "__main__":
    main()
