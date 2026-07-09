#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Plans the feature panel build step for an offline experiment by reading the data-bound runner request and locating the resolved candle source file. Reads the latest bound runner request JSON, samples the candle CSV to classify OHLCV columns, and writes a feature panel build plan JSON specifying the source file path and column mapping.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_feature_panel_build_planner_v1"

def latest_bound_request() -> Path | None:
    root = WORKSPACE / "edge_factory_offline_runner_data_source_binding_v1"
    files = list(root.rglob("offline_runner_request_v1_data_bound.json"))
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

def sample_file(path: Path) -> dict[str, Any]:
    try:
        df = pd.read_csv(path, nrows=1000)
        return {
            "ok": True,
            "columns": list(df.columns),
            "sample_rows": len(df),
            "first_row": df.head(1).to_dict(orient="records")[0] if len(df) else {},
        }
    except Exception as e:
        return {
            "ok": False,
            "error": repr(e),
            "columns": [],
            "sample_rows": 0,
            "first_row": {},
        }

def classify_columns(cols: list[str]) -> dict[str, str | None]:
    lower = {str(c).lower(): str(c) for c in cols}

    def pick(*names):
        for n in names:
            if n.lower() in lower:
                return lower[n.lower()]
        return None

    return {
        "time": pick("time", "timestamp", "datetime", "ts", "open_time"),
        "open": pick("open", "o"),
        "high": pick("high", "h"),
        "low": pick("low", "l"),
        "close": pick("close", "c", "close_price", "last"),
        "quote_volume": pick("volCcyQuote", "vol_ccy_quote", "quote_volume", "volume_quote", "turnover", "vol_quote", "volume"),
    }

def main() -> int:
    out_dir = OUT_ROOT / f"feature_panel_build_planner_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    request_path = latest_bound_request()
    req = read_json(request_path)

    blockers = []
    if not request_path or not request_path.exists():
        blockers.append("BOUND_RUNNER_REQUEST_NOT_FOUND")
    if "__read_error__" in req:
        blockers.append("BOUND_RUNNER_REQUEST_READ_ERROR")

    source_files = req.get("source_files", []) if isinstance(req.get("source_files"), list) else []
    candidate_key = req.get("candidate_key", "UNKNOWN")
    family_key = req.get("family_key", "UNKNOWN")
    required_columns = req.get("required_columns", [])

    if not source_files:
        blockers.append("NO_SOURCE_FILES_IN_BOUND_REQUEST")

    sample_rows = []
    total_size_mb = 0.0

    for p_raw in source_files[:30]:
        p = Path(p_raw)
        size_mb = round(p.stat().st_size / (1024 * 1024), 3) if p.exists() else None
        if size_mb:
            total_size_mb += size_mb

        smp = sample_file(p)
        colmap = classify_columns(smp.get("columns", []))

        sample_rows.append({
            "path": str(p),
            "exists": p.exists(),
            "size_mb": size_mb,
            "sample_ok": smp["ok"],
            "sample_rows": smp["sample_rows"],
            "time_col": colmap["time"],
            "open_col": colmap["open"],
            "high_col": colmap["high"],
            "low_col": colmap["low"],
            "close_col": colmap["close"],
            "quote_volume_col": colmap["quote_volume"],
            "schema_ok": all(colmap.values()),
            "error": smp.get("error", ""),
        })

    schema_fail = [r for r in sample_rows if not r["schema_ok"]]

    output_root = WORKSPACE / "edge_factory_feature_panels" / str(candidate_key)
    panel_1h_path = output_root / f"{candidate_key}_feature_panel_1h.parquet"
    manifest_path = output_root / f"{candidate_key}_feature_panel_manifest.json"

    if blockers:
        planner_status = "FEATURE_PANEL_BUILD_PLANNER_BLOCKED"
        next_action = "FIX_BOUND_REQUEST"
    elif schema_fail:
        planner_status = "FEATURE_PANEL_BUILD_PLANNER_SCHEMA_ATTENTION"
        next_action = "PATCH_COLUMN_MAPPING_BEFORE_BUILD"
    else:
        planner_status = "FEATURE_PANEL_BUILD_PLAN_READY"
        next_action = "BUILD_FEATURE_PANEL_CHUNKED"

    build_plan = {
        "plan_version": "edge_factory_feature_panel_build_plan_v1",
        "candidate_key": candidate_key,
        "family_key": family_key,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_file_count": len(source_files),
        "source_files": source_files,
        "required_columns": required_columns,
        "output_root": str(output_root),
        "outputs": {
            "feature_panel_1h_parquet": str(panel_1h_path),
            "feature_panel_manifest_json": str(manifest_path),
        },
        "processing_steps": [
            "Read each 1m OHLCV candle file independently.",
            "Infer symbol from filename.",
            "Map time/open/high/low/close/quote_volume columns.",
            "Parse time as UTC.",
            "Resample 1m candles to 1h bars per symbol.",
            "OHLC aggregation: open first, high max, low min, close last, quote volume sum.",
            "Build wide close matrix by symbol and hour.",
            "Build market median close index across symbols.",
            "Derive coin_ret6_bps and coin_ret24_bps per symbol.",
            "Derive mkt_ret6_bps and mkt_ret24_bps from market median index.",
            "Derive entry_vol_quote from 1h summed quote volume.",
            "Derive entry_range_bps from 1h high/low/close.",
            "Write normalized long-form 1h feature panel.",
        ],
        "feature_derivations": {
            "coin_ret6_bps": "per symbol 1h close pct_change(6) * 10000",
            "coin_ret24_bps": "per symbol 1h close pct_change(24) * 10000",
            "mkt_ret6_bps": "median market close index pct_change(6) * 10000",
            "mkt_ret24_bps": "median market close index pct_change(24) * 10000",
            "entry_vol_quote": "1h quote volume sum",
            "entry_range_bps": "(high - low) / close * 10000",
        },
        "resource_policy": {
            "chunk_by_symbol": True,
            "do_not_load_all_raw_files_at_once": True,
            "write_intermediate_hourly_per_symbol": True,
            "max_symbols_per_batch_recommended": 25,
        },
        "safety": {
            "touch_master": False,
            "run_backtest": False,
            "place_orders": False,
            "live_allowed": False,
            "active_paper_allowed": False,
            "capital_change_allowed": False,
        }
    }

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "request_path": str(request_path) if request_path else None,
        "candidate_key": candidate_key,
        "family_key": family_key,
        "planner_status": planner_status,
        "source_file_count": len(source_files),
        "sampled_file_count": len(sample_rows),
        "schema_fail_count": len(schema_fail),
        "blockers": blockers,
        "next_action": next_action,
        "build_plan_path": "",
        "output_root": str(output_root),
        "estimated_total_size_mb_from_first_30": round(total_size_mb, 3),
        "runner_execution_allowed": False,
        "feature_build_execution_allowed": False,
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Planner only creates feature build plan.",
            "Does not build panel.",
            "Does not run backtest.",
            "Does not touch MASTER_UPPER_SYSTEM.",
            "Does not start/stop processes.",
            "Does not place orders.",
        ],
    }

    plan_path = out_dir / "feature_panel_build_plan_v1.json"
    state["build_plan_path"] = str(plan_path)

    state_path = out_dir / "feature_panel_build_planner_v1_state.json"
    samples_csv = out_dir / "feature_panel_build_planner_v1_sample_schema.csv"
    report_path = out_dir / "feature_panel_build_planner_v1_report.md"

    plan_path.write_text(json.dumps(build_plan, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    pd.DataFrame(sample_rows).to_csv(samples_csv, index=False)

    md = []
    md.append("# Edge Factory Feature Panel Build Planner v1")
    md.append("")
    md.append(f"Status: `{planner_status}`")
    md.append(f"Candidate: `{candidate_key}`")
    md.append(f"Source files: `{len(source_files)}`")
    md.append(f"Sampled files: `{len(sample_rows)}`")
    md.append(f"Schema fail count: `{len(schema_fail)}`")
    md.append(f"Next action: `{next_action}`")
    md.append("")
    md.append("## Build plan")
    md.append(f"`{plan_path}`")
    md.append("")
    md.append("## Safety")
    md.append("- runner_execution_allowed: `False`")
    md.append("- feature_build_execution_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY FEATURE PANEL BUILD PLANNER v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"candidate : {candidate_key}")
    print(f"planner_status: {planner_status}")
    print(f"source_file_count: {len(source_files)}")
    print(f"sampled_file_count: {len(sample_rows)}")
    print(f"schema_fail_count: {len(schema_fail)}")
    print(f"next_action: {next_action}")
    print("runner_execution_allowed: False")
    print("feature_build_execution_allowed: False")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("SAMPLE SCHEMA")
    print("-" * 100)
    if sample_rows:
        df = pd.DataFrame(sample_rows)
        print(df[["schema_ok","time_col","open_col","high_col","low_col","close_col","quote_volume_col","path"]].head(20).to_string(index=False))
    else:
        print("No samples.")
    print()
    print(f"Plan   : {plan_path}")
    print(f"State  : {state_path}")
    print(f"Samples: {samples_csv}")
    print(f"Report : {report_path}")

if __name__ == "__main__":
    main()
