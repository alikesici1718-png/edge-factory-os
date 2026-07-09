#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Builds feature panels for offline strategy research by reading OKX candle CSV files and computing return, volume, and market-relative feature columns. Reads the latest feature panel build plan JSON and its linked candle source file, then writes a feature panel Parquet or CSV and a manifest JSON describing the output.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_feature_panel_builder_v1"

def latest_plan() -> Path | None:
    root = WORKSPACE / "edge_factory_feature_panel_build_planner_v1"
    files = list(root.rglob("feature_panel_build_plan_v1.json"))
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def latest_selftest_state() -> dict[str, Any]:
    root = WORKSPACE / "edge_factory_feature_panel_builder_selftest_v1"
    files = list(root.rglob("feature_panel_builder_selftest_v1_state.json"))
    if not files:
        return {}
    p = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[0]
    try:
        return json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}

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
    if pd.api.types.is_numeric_dtype(s):
        clean = pd.to_numeric(s, errors="coerce").dropna()
        if len(clean):
            med = float(clean.median())
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
        raise ValueError(f"missing columns {missing}")

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

def write_parquet_or_csv(df: pd.DataFrame, parquet_path: Path, csv_path: Path) -> tuple[str, bool]:
    try:
        df.to_parquet(parquet_path, index=False)
        return str(parquet_path), True
    except Exception:
        df.to_csv(csv_path, index=False)
        return str(csv_path), False

def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Build full 1h feature panel from bound raw 1m candles.")
    ap.add_argument("--max_symbols", type=int, default=0, help="0 = all symbols from plan.")
    ap.add_argument("--batch_size", type=int, default=25)
    args = ap.parse_args()

    run_dir = OUT_ROOT / f"feature_panel_builder_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir.mkdir(parents=True, exist_ok=True)

    plan_path = latest_plan()
    plan = read_json(plan_path)
    selftest = latest_selftest_state()

    blockers = []
    if not plan_path or not plan_path.exists():
        blockers.append("BUILD_PLAN_NOT_FOUND")
    if "__read_error__" in plan:
        blockers.append("BUILD_PLAN_READ_ERROR")
    if selftest.get("selftest_status") != "FEATURE_PANEL_SELFTEST_PASS":
        blockers.append(f"SELFTEST_NOT_PASS:{selftest.get('selftest_status')}")

    source_files = plan.get("source_files", []) if isinstance(plan.get("source_files"), list) else []
    candidate_key = plan.get("candidate_key", "UNKNOWN")
    family_key = plan.get("family_key", "UNKNOWN")

    if not source_files:
        blockers.append("NO_SOURCE_FILES_IN_PLAN")

    if args.max_symbols and args.max_symbols > 0:
        source_files = source_files[:args.max_symbols]

    output_root = WORKSPACE / "edge_factory_feature_panels" / str(candidate_key)
    hourly_root = output_root / "hourly_by_symbol"
    output_root.mkdir(parents=True, exist_ok=True)
    hourly_root.mkdir(parents=True, exist_ok=True)

    audit_rows = []
    hourly_paths = []

    builder_status = "FEATURE_PANEL_BUILDER_BLOCKED" if blockers else "FEATURE_PANEL_BUILD_RUNNING"

    if not blockers:
        for i, raw_path in enumerate(source_files, start=1):
            p = Path(raw_path)
            symbol = infer_symbol(p)

            try:
                raw = normalize_1m_file(p)
                hourly = resample_to_1h(raw)

                sym_parquet = hourly_root / f"{symbol}_1h.parquet"
                sym_csv = hourly_root / f"{symbol}_1h.csv"
                written_path, wrote_parquet = write_parquet_or_csv(hourly, sym_parquet, sym_csv)

                hourly_paths.append(written_path)

                audit_rows.append({
                    "symbol": symbol,
                    "path": str(p),
                    "ok": True,
                    "raw_rows": int(len(raw)),
                    "hourly_rows": int(len(hourly)),
                    "first_time": str(hourly["time"].min()) if len(hourly) else "",
                    "last_time": str(hourly["time"].max()) if len(hourly) else "",
                    "written_path": written_path,
                    "wrote_parquet": wrote_parquet,
                    "error": "",
                })

                if i % args.batch_size == 0:
                    print(f"[progress] processed {i}/{len(source_files)} symbols")

            except Exception as e:
                audit_rows.append({
                    "symbol": symbol,
                    "path": str(p),
                    "ok": False,
                    "raw_rows": 0,
                    "hourly_rows": 0,
                    "first_time": "",
                    "last_time": "",
                    "written_path": "",
                    "wrote_parquet": False,
                    "error": repr(e),
                })

        failed = [r for r in audit_rows if not r["ok"]]

        hourly_parts = []
        for hp in hourly_paths:
            hp_path = Path(hp)
            try:
                if hp_path.suffix.lower() == ".parquet":
                    hourly_parts.append(pd.read_parquet(hp_path))
                else:
                    hourly_parts.append(pd.read_csv(hp_path))
            except Exception as e:
                failed.append({
                    "symbol": hp_path.stem,
                    "path": hp,
                    "ok": False,
                    "error": f"read_hourly_failed:{repr(e)}",
                })

        if hourly_parts:
            panel = pd.concat(hourly_parts, ignore_index=True)
            panel["time"] = pd.to_datetime(panel["time"], utc=True, errors="coerce")
            panel = panel.dropna(subset=["time", "symbol", "close"])
            panel = panel.sort_values(["symbol", "time"])

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

            required_output_cols = [
                "time", "symbol", "open", "high", "low", "close",
                "entry_vol_quote", "entry_range_bps",
                "coin_ret6_bps", "coin_ret24_bps",
                "mkt_ret6_bps", "mkt_ret24_bps",
            ]

            missing_output_cols = [c for c in required_output_cols if c not in panel.columns]

            non_null_summary = {}
            for c in required_output_cols:
                if c in panel.columns:
                    non_null_summary[c] = int(panel[c].notna().sum())

            final_parquet = output_root / f"{candidate_key}_feature_panel_1h.parquet"
            final_csv = output_root / f"{candidate_key}_feature_panel_1h.csv"
            final_path, final_is_parquet = write_parquet_or_csv(panel, final_parquet, final_csv)

            manifest = {
                "manifest_version": "edge_factory_feature_panel_manifest_v1",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "candidate_key": candidate_key,
                "family_key": family_key,
                "source_file_count": len(source_files),
                "processed_symbol_count": int(panel["symbol"].nunique()),
                "panel_rows": int(len(panel)),
                "first_time": str(panel["time"].min()),
                "last_time": str(panel["time"].max()),
                "feature_panel_path": final_path,
                "final_is_parquet": final_is_parquet,
                "missing_output_cols": missing_output_cols,
                "non_null_summary": non_null_summary,
                "failed_file_count": len([r for r in audit_rows if not r["ok"]]),
                "live_allowed": False,
                "active_paper_allowed": False,
                "capital_change_allowed": False,
            }

            manifest_path = output_root / f"{candidate_key}_feature_panel_manifest.json"
            manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

            if missing_output_cols:
                builder_status = "FEATURE_PANEL_BUILD_MISSING_OUTPUT_COLUMNS"
                full_panel_ready = False
                next_action = "PATCH_FEATURE_BUILD"
            elif non_null_summary.get("coin_ret6_bps", 0) == 0 or non_null_summary.get("mkt_ret6_bps", 0) == 0:
                builder_status = "FEATURE_PANEL_BUILD_FEATURES_ALL_NULL"
                full_panel_ready = False
                next_action = "INSPECT_FEATURE_ALIGNMENT"
            else:
                builder_status = "FEATURE_PANEL_BUILD_PASS"
                full_panel_ready = True
                next_action = "RUN_PANEL_QUALITY_AUDIT"

        else:
            panel = pd.DataFrame()
            final_path = ""
            manifest_path = None
            missing_output_cols = []
            non_null_summary = {}
            builder_status = "FEATURE_PANEL_BUILD_NO_HOURLY_PARTS"
            full_panel_ready = False
            next_action = "INSPECT_FILE_AUDIT"

    else:
        panel = pd.DataFrame()
        final_path = ""
        manifest_path = None
        missing_output_cols = []
        non_null_summary = {}
        full_panel_ready = False
        next_action = "FIX_BLOCKERS"

    audit_csv = run_dir / "feature_panel_builder_v1_file_audit.csv"
    pd.DataFrame(audit_rows).to_csv(audit_csv, index=False)

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "candidate_key": candidate_key,
        "family_key": family_key,
        "plan_path": str(plan_path) if plan_path else None,
        "builder_status": builder_status,
        "blockers": blockers,
        "source_file_count": len(source_files),
        "processed_ok_count": len([r for r in audit_rows if r.get("ok")]),
        "failed_file_count": len([r for r in audit_rows if not r.get("ok")]),
        "panel_rows": int(len(panel)),
        "panel_symbols": int(panel["symbol"].nunique()) if not panel.empty and "symbol" in panel.columns else 0,
        "first_time": str(panel["time"].min()) if not panel.empty and "time" in panel.columns else "",
        "last_time": str(panel["time"].max()) if not panel.empty and "time" in panel.columns else "",
        "feature_panel_path": final_path,
        "manifest_path": str(manifest_path) if manifest_path else "",
        "audit_csv": str(audit_csv),
        "missing_output_cols": missing_output_cols,
        "non_null_summary": non_null_summary,
        "full_panel_ready": full_panel_ready,
        "runner_execution_allowed": False,
        "next_action": next_action,
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Builds offline feature panel only.",
            "Does not run strategy backtest.",
            "Does not touch MASTER_UPPER_SYSTEM.",
            "Does not start/stop MASTER processes.",
            "Does not place orders.",
            "Does not enable live trading.",
        ],
    }

    state_path = run_dir / "feature_panel_builder_v1_state.json"
    report_path = run_dir / "feature_panel_builder_v1_report.md"
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    md = []
    md.append("# Edge Factory Feature Panel Builder v1")
    md.append("")
    md.append(f"Status: `{builder_status}`")
    md.append(f"Candidate: `{candidate_key}`")
    md.append(f"Source files: `{len(source_files)}`")
    md.append(f"Processed OK: `{state['processed_ok_count']}`")
    md.append(f"Failed files: `{state['failed_file_count']}`")
    md.append(f"Panel rows: `{state['panel_rows']}`")
    md.append(f"Panel symbols: `{state['panel_symbols']}`")
    md.append(f"Next action: `{next_action}`")
    md.append("")
    md.append("## Outputs")
    md.append(f"- Panel: `{final_path}`")
    md.append(f"- Manifest: `{state['manifest_path']}`")
    md.append(f"- Audit: `{audit_csv}`")
    md.append("")
    md.append("## Safety")
    md.append("- runner_execution_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY FEATURE PANEL BUILDER v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"run_dir   : {run_dir}")
    print(f"candidate : {candidate_key}")
    print(f"builder_status: {builder_status}")
    print(f"source_file_count: {len(source_files)}")
    print(f"processed_ok_count: {state['processed_ok_count']}")
    print(f"failed_file_count : {state['failed_file_count']}")
    print(f"panel_rows  : {state['panel_rows']}")
    print(f"panel_symbols: {state['panel_symbols']}")
    print(f"first_time: {state['first_time']}")
    print(f"last_time : {state['last_time']}")
    print(f"full_panel_ready: {full_panel_ready}")
    print(f"next_action: {next_action}")
    print("runner_execution_allowed: False")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("NON NULL SUMMARY")
    print("-" * 100)
    print(json.dumps(non_null_summary, indent=2, ensure_ascii=False))
    print()
    print(f"Panel   : {final_path}")
    print(f"Manifest: {state['manifest_path']}")
    print(f"Audit   : {audit_csv}")
    print(f"State   : {state_path}")
    print(f"Report  : {report_path}")

if __name__ == "__main__":
    main()
