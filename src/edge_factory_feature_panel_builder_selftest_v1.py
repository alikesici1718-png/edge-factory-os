#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import numpy as np

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_feature_panel_builder_selftest_v1"

def latest_plan() -> Path | None:
    root = WORKSPACE / "edge_factory_feature_panel_build_planner_v1"
    files = list(root.rglob("feature_panel_build_plan_v1.json"))
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

def infer_symbol(path: Path) -> str:
    name = path.name.upper()
    m = re.search(r"([A-Z0-9]+)-USDT-SWAP", name)
    if m:
        return m.group(1)
    return path.parent.parent.parent.name.upper()

def parse_time_series(s: pd.Series) -> pd.Series:
    # OKX exports are often ms timestamps, but sometimes already ISO strings.
    if pd.api.types.is_numeric_dtype(s):
        med = float(pd.to_numeric(s, errors="coerce").dropna().median())
        if med > 1e12:
            return pd.to_datetime(s, unit="ms", utc=True, errors="coerce")
        if med > 1e9:
            return pd.to_datetime(s, unit="s", utc=True, errors="coerce")
    return pd.to_datetime(s, utc=True, errors="coerce")

def normalize_1m_file(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    required = ["time", "open", "high", "low", "close", "volCcyQuote"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"missing columns {missing} in {path}")

    symbol = infer_symbol(path)

    out = df[required].copy()
    out["time"] = parse_time_series(out["time"])

    for c in ["open", "high", "low", "close", "volCcyQuote"]:
        out[c] = pd.to_numeric(out[c], errors="coerce")

    out = out.dropna(subset=["time", "open", "high", "low", "close"])
    out = out.sort_values("time")
    out = out.drop_duplicates(subset=["time"], keep="last")
    out["symbol"] = symbol

    return out

def resample_to_1h(df_1m: pd.DataFrame) -> pd.DataFrame:
    symbol = str(df_1m["symbol"].iloc[0])
    x = df_1m.set_index("time").sort_index()

    h = x.resample("1h").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volCcyQuote": "sum",
    })

    h = h.dropna(subset=["open", "high", "low", "close"])
    h = h.reset_index()
    h["symbol"] = symbol
    h = h.rename(columns={"volCcyQuote": "entry_vol_quote"})
    h["entry_range_bps"] = ((h["high"] - h["low"]) / h["close"]) * 10000.0

    return h[["time", "symbol", "open", "high", "low", "close", "entry_vol_quote", "entry_range_bps"]]

def add_features(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.sort_values(["symbol", "time"]).copy()

    panel["coin_ret6_bps"] = panel.groupby("symbol")["close"].pct_change(6) * 10000.0
    panel["coin_ret24_bps"] = panel.groupby("symbol")["close"].pct_change(24) * 10000.0

    close_wide = panel.pivot(index="time", columns="symbol", values="close").sort_index()
    market_index = close_wide.median(axis=1, skipna=True)

    mkt = pd.DataFrame({
        "time": market_index.index,
        "mkt_close_median": market_index.values,
    })
    mkt["mkt_ret6_bps"] = mkt["mkt_close_median"].pct_change(6) * 10000.0
    mkt["mkt_ret24_bps"] = mkt["mkt_close_median"].pct_change(24) * 10000.0

    panel = panel.merge(
        mkt[["time", "mkt_ret6_bps", "mkt_ret24_bps"]],
        on="time",
        how="left",
    )

    return panel

def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Small-sample feature panel builder self-test.")
    ap.add_argument("--max_symbols", type=int, default=5)
    args = ap.parse_args()

    out_dir = OUT_ROOT / f"feature_panel_builder_selftest_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    plan_path = latest_plan()
    plan = read_json(plan_path)

    blockers = []
    if not plan_path or not plan_path.exists():
        blockers.append("BUILD_PLAN_NOT_FOUND")
    if "__read_error__" in plan:
        blockers.append("BUILD_PLAN_READ_ERROR")

    source_files = plan.get("source_files", []) if isinstance(plan.get("source_files"), list) else []
    candidate_key = plan.get("candidate_key", "UNKNOWN")

    if not source_files:
        blockers.append("NO_SOURCE_FILES_IN_BUILD_PLAN")

    selected = [Path(p) for p in source_files[:args.max_symbols]]

    per_file_rows = []
    hourly_parts = []

    if not blockers:
        for p in selected:
            try:
                raw = normalize_1m_file(p)
                hourly = resample_to_1h(raw)
                hourly_parts.append(hourly)

                per_file_rows.append({
                    "path": str(p),
                    "symbol": infer_symbol(p),
                    "ok": True,
                    "raw_rows": int(len(raw)),
                    "hourly_rows": int(len(hourly)),
                    "first_time": str(hourly["time"].min()) if len(hourly) else "",
                    "last_time": str(hourly["time"].max()) if len(hourly) else "",
                    "error": "",
                })
            except Exception as e:
                per_file_rows.append({
                    "path": str(p),
                    "symbol": infer_symbol(p),
                    "ok": False,
                    "raw_rows": 0,
                    "hourly_rows": 0,
                    "first_time": "",
                    "last_time": "",
                    "error": repr(e),
                })

    failed_files = [r for r in per_file_rows if not r["ok"]]

    panel = pd.DataFrame()
    if hourly_parts:
        panel = pd.concat(hourly_parts, ignore_index=True)
        panel = add_features(panel)

    required_output_cols = [
        "time", "symbol", "open", "high", "low", "close",
        "entry_vol_quote", "entry_range_bps",
        "coin_ret6_bps", "coin_ret24_bps",
        "mkt_ret6_bps", "mkt_ret24_bps",
    ]

    missing_output_cols = [c for c in required_output_cols if c not in panel.columns]

    non_null_summary = {}
    if not panel.empty:
        for c in required_output_cols:
            if c in panel.columns:
                non_null_summary[c] = int(panel[c].notna().sum())

    if blockers:
        selftest_status = "FEATURE_PANEL_SELFTEST_BLOCKED"
        next_action = "FIX_BUILD_PLAN"
    elif failed_files:
        selftest_status = "FEATURE_PANEL_SELFTEST_FILE_ERRORS"
        next_action = "INSPECT_FAILED_FILES"
    elif panel.empty:
        selftest_status = "FEATURE_PANEL_SELFTEST_NO_PANEL_ROWS"
        next_action = "INSPECT_RESAMPLE_LOGIC"
    elif missing_output_cols:
        selftest_status = "FEATURE_PANEL_SELFTEST_MISSING_OUTPUT_COLUMNS"
        next_action = "PATCH_FEATURE_DERIVATION"
    elif non_null_summary.get("coin_ret6_bps", 0) == 0 or non_null_summary.get("mkt_ret6_bps", 0) == 0:
        selftest_status = "FEATURE_PANEL_SELFTEST_FEATURES_ALL_NULL"
        next_action = "INSPECT_TIME_ALIGNMENT"
    else:
        selftest_status = "FEATURE_PANEL_SELFTEST_PASS"
        next_action = "BUILD_FULL_FEATURE_PANEL_CHUNKED_AFTER_APPROVAL"

    panel_csv = out_dir / f"{candidate_key}_selftest_feature_panel_1h.csv"
    panel_parquet = out_dir / f"{candidate_key}_selftest_feature_panel_1h.parquet"
    file_audit_csv = out_dir / "feature_panel_selftest_file_audit.csv"

    if not panel.empty:
        panel.to_csv(panel_csv, index=False)
        try:
            panel.to_parquet(panel_parquet, index=False)
            parquet_written = True
        except Exception:
            parquet_written = False
            panel_parquet = None
    else:
        parquet_written = False
        panel.to_csv(panel_csv, index=False)

    pd.DataFrame(per_file_rows).to_csv(file_audit_csv, index=False)

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "plan_path": str(plan_path) if plan_path else None,
        "candidate_key": candidate_key,
        "selftest_status": selftest_status,
        "max_symbols": args.max_symbols,
        "selected_files": [str(p) for p in selected],
        "file_count": len(selected),
        "failed_file_count": len(failed_files),
        "panel_rows": int(len(panel)),
        "panel_symbols": int(panel["symbol"].nunique()) if not panel.empty and "symbol" in panel.columns else 0,
        "first_time": str(panel["time"].min()) if not panel.empty and "time" in panel.columns else "",
        "last_time": str(panel["time"].max()) if not panel.empty and "time" in panel.columns else "",
        "missing_output_cols": missing_output_cols,
        "non_null_summary": non_null_summary,
        "panel_csv": str(panel_csv),
        "panel_parquet": str(panel_parquet) if parquet_written else "",
        "file_audit_csv": str(file_audit_csv),
        "next_action": next_action,
        "full_feature_build_allowed": selftest_status == "FEATURE_PANEL_SELFTEST_PASS",
        "runner_execution_allowed": False,
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Self-test only processes a small sample of symbols.",
            "Does not run backtest.",
            "Does not touch MASTER_UPPER_SYSTEM.",
            "Does not start/stop processes.",
            "Does not place orders.",
            "Does not enable live trading."
        ],
    }

    state_path = out_dir / "feature_panel_builder_selftest_v1_state.json"
    report_path = out_dir / "feature_panel_builder_selftest_v1_report.md"
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    md = []
    md.append("# Edge Factory Feature Panel Builder Self-Test v1")
    md.append("")
    md.append(f"Status: `{selftest_status}`")
    md.append(f"Candidate: `{candidate_key}`")
    md.append(f"Panel rows: `{len(panel)}`")
    md.append(f"Panel symbols: `{state['panel_symbols']}`")
    md.append(f"Failed files: `{len(failed_files)}`")
    md.append(f"Next action: `{next_action}`")
    md.append("")
    md.append("## Outputs")
    md.append(f"- CSV: `{panel_csv}`")
    if parquet_written:
        md.append(f"- Parquet: `{panel_parquet}`")
    md.append(f"- File audit: `{file_audit_csv}`")
    md.append("")
    md.append("## Safety")
    md.append("- runner_execution_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY FEATURE PANEL BUILDER SELF-TEST v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"candidate : {candidate_key}")
    print(f"selftest_status: {selftest_status}")
    print(f"selected_symbols: {args.max_symbols}")
    print(f"failed_file_count: {len(failed_files)}")
    print(f"panel_rows: {len(panel)}")
    print(f"panel_symbols: {state['panel_symbols']}")
    print(f"first_time: {state['first_time']}")
    print(f"last_time : {state['last_time']}")
    print(f"missing_output_cols: {missing_output_cols}")
    print(f"next_action: {next_action}")
    print(f"full_feature_build_allowed: {state['full_feature_build_allowed']}")
    print("runner_execution_allowed: False")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("NON NULL SUMMARY")
    print("-" * 100)
    print(json.dumps(non_null_summary, indent=2, ensure_ascii=False))
    print()
    print("FILE AUDIT")
    print("-" * 100)
    if per_file_rows:
        print(pd.DataFrame(per_file_rows).to_string(index=False))
    else:
        print("No files processed.")
    print()
    print(f"PanelCSV : {panel_csv}")
    if parquet_written:
        print(f"PanelParquet: {panel_parquet}")
    print(f"Audit    : {file_audit_csv}")
    print(f"State    : {state_path}")
    print(f"Report   : {report_path}")

if __name__ == "__main__":
    main()
