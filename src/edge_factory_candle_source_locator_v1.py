#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Scans the workspace to locate and validate OHLCV candle source CSV files for use in offline strategy research. Applies path heuristics to distinguish real candle files from paper/live/validation outputs, normalizes OKX 1-minute OHLCV files, and writes a candle source inventory report.
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_candle_source_locator_v1"

BAD_PATH_HINTS = [
    "paper_run_",
    "live_",
    "shadow",
    "sim_",
    "backtest",
    "validation",
    "lag_guard",
    "portfolio",
    "contract",
    "validator",
    "adapter",
    "autopilot",
    "command_center",
    "state_index",
    "recovery_manifest",
    "process_watchdog",
    "duplicate_launch_guard",
    "idea_bank",
    "idea_seeder",
    "idea_prioritizer",
    "research_brain",
    "result_to_lifecycle",
    "offline_runner_outputs",
    "offline_runner_data_resolver",
]

GOOD_PATH_HINTS = [
    "candle",
    "candles",
    "kline",
    "klines",
    "ohlcv",
    "panel",
    "cache",
    "raw",
    "okx",
    "swap",
    "market",
    "data",
    "1h",
    "hour",
]

SYMBOL_ALIASES = ["symbol", "coin", "instId", "inst_id", "instrument", "ticker"]
TIME_ALIASES = ["time", "timestamp", "datetime", "ts", "open_time", "date"]
OPEN_ALIASES = ["open", "o"]
HIGH_ALIASES = ["high", "h"]
LOW_ALIASES = ["low", "l"]
CLOSE_ALIASES = ["close", "c", "close_price", "last"]
QUOTE_VOL_ALIASES = [
    "volCcyQuote",
    "vol_ccy_quote",
    "quote_volume",
    "volume_quote",
    "turnover",
    "volume_usdt",
    "vol_quote",
]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def path_text(p: Path) -> str:
    return str(p).replace("\\", "/").lower()

def has_any(text: str, words: list[str]) -> bool:
    return any(w.lower() in text for w in words)

def get_columns(path: Path) -> list[str]:
    try:
        if path.suffix.lower() == ".csv":
            return list(pd.read_csv(path, nrows=5).columns)
        if path.suffix.lower() == ".parquet":
            try:
                import pyarrow.parquet as pq
                return list(pq.ParquetFile(path).schema.names)
            except Exception:
                return list(pd.read_parquet(path).head(1).columns)
    except Exception:
        return []
    return []

def colmap(cols: list[str]) -> dict[str, str]:
    return {str(c).lower(): str(c) for c in cols}

def find_alias(cols: list[str], aliases: list[str]) -> str | None:
    m = colmap(cols)
    for a in aliases:
        if a.lower() in m:
            return m[a.lower()]
    return None

def maybe_symbol_from_filename(path: Path) -> str | None:
    stem = path.stem.upper()
    stem = stem.replace("-USDT-SWAP", "").replace("_USDT_SWAP", "")
    # Avoid returning generic stems.
    bad = {"CANDLES", "KLINES", "PANEL", "CACHE", "DATA", "OHLCV", "MERGED"}
    parts = re.split(r"[^A-Z0-9]+", stem)
    parts = [p for p in parts if p and p not in bad]
    if len(parts) == 1 and 2 <= len(parts[0]) <= 12:
        return parts[0]
    return None

def score_file(path: Path, cols: list[str]) -> dict[str, Any]:
    txt = path_text(path)

    symbol_col = find_alias(cols, SYMBOL_ALIASES)
    time_col = find_alias(cols, TIME_ALIASES)
    open_col = find_alias(cols, OPEN_ALIASES)
    high_col = find_alias(cols, HIGH_ALIASES)
    low_col = find_alias(cols, LOW_ALIASES)
    close_col = find_alias(cols, CLOSE_ALIASES)
    quote_vol_col = find_alias(cols, QUOTE_VOL_ALIASES)

    symbol_from_file = maybe_symbol_from_filename(path)
    has_symbol = symbol_col is not None or symbol_from_file is not None
    has_time = time_col is not None
    has_close = close_col is not None
    has_hilo = high_col is not None and low_col is not None
    has_ohlc = open_col is not None and high_col is not None and low_col is not None and close_col is not None
    has_quote_vol = quote_vol_col is not None

    score = 0
    reasons = []
    warnings = []

    if has_any(txt, GOOD_PATH_HINTS):
        score += 25
        reasons.append("good_path_hint")
    if has_any(txt, BAD_PATH_HINTS):
        score -= 25
        warnings.append("bad_path_hint_possible_generated_output")

    if has_symbol:
        score += 12
        reasons.append("symbol_available")
    else:
        warnings.append("symbol_missing")

    if has_time:
        score += 18
        reasons.append("time_available")
    else:
        warnings.append("time_missing")

    if has_close:
        score += 30
        reasons.append("close_available")
    else:
        warnings.append("close_missing")

    if has_ohlc:
        score += 20
        reasons.append("ohlc_available")
    elif has_hilo and has_close:
        score += 12
        reasons.append("high_low_close_available")
    else:
        warnings.append("full_ohlc_or_hilo_missing")

    if has_quote_vol:
        score += 14
        reasons.append("quote_volume_available")
    else:
        warnings.append("quote_volume_missing")

    # Prefer parquet/panel/cache for large research.
    if path.suffix.lower() == ".parquet":
        score += 8
        reasons.append("parquet_preferred")

    try:
        size_mb = round(path.stat().st_size / (1024 * 1024), 3)
        mtime_utc = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()
    except Exception:
        size_mb = None
        mtime_utc = None

    return {
        "path": str(path),
        "parent": str(path.parent),
        "suffix": path.suffix.lower(),
        "score": score,
        "size_mb": size_mb,
        "mtime_utc": mtime_utc,
        "symbol_col": symbol_col,
        "symbol_from_file": symbol_from_file,
        "time_col": time_col,
        "open_col": open_col,
        "high_col": high_col,
        "low_col": low_col,
        "close_col": close_col,
        "quote_vol_col": quote_vol_col,
        "has_symbol": has_symbol,
        "has_time": has_time,
        "has_close": has_close,
        "has_ohlc": has_ohlc,
        "has_quote_vol": has_quote_vol,
        "reasons": reasons,
        "warnings": warnings,
        "columns": cols,
    }

def scan(max_files: int) -> list[dict[str, Any]]:
    rows = []
    scanned = 0

    for root, dirs, files in os.walk(WORKSPACE):
        root_path = Path(root)
        txt = path_text(root_path)

        # Do not fully skip bad dirs because some useful outputs may be under old research;
        # but skip obvious OS/log runtime dirs to keep it fast.
        if any(x in txt for x in [
            "paper_run_gate_master_upper_system",
            "paper_run_shadow",
            "edge_factory_os_autopilot",
            "edge_factory_os_command_center",
            "edge_factory_os_state_index",
            "edge_factory_os_recovery_manifest",
        ]):
            dirs[:] = []
            continue

        for f in files:
            if not (f.lower().endswith(".csv") or f.lower().endswith(".parquet")):
                continue

            p = root_path / f
            scanned += 1
            if scanned > max_files:
                return rows

            cols = get_columns(p)
            if not cols:
                continue

            scored = score_file(p, cols)

            # Keep candidates with at least time+close or close+good hint; otherwise too many trade logs.
            if (scored["has_time"] and scored["has_close"]) or (scored["has_close"] and "good_path_hint" in scored["reasons"]):
                rows.append(scored)

    return rows

def group_sources(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not rows:
        return []

    df = pd.DataFrame(rows)
    groups = []

    for parent, g in df.groupby("parent"):
        g_sorted = g.sort_values("score", ascending=False)
        best = g_sorted.iloc[0].to_dict()
        groups.append({
            "parent": parent,
            "file_count": int(len(g)),
            "best_score": float(g_sorted["score"].max()),
            "mean_score": float(g_sorted["score"].mean()),
            "has_multi_files": len(g) >= 5,
            "sample_file": best["path"],
            "best_columns": best["columns"],
            "best_warnings": best["warnings"],
            "candidate_dataset_type": (
                "MULTI_FILE_CANDLE_DATASET" if len(g) >= 5
                else "SINGLE_OR_SMALL_CANDLE_SOURCE"
            ),
        })

    return sorted(groups, key=lambda x: (x["best_score"], x["file_count"]), reverse=True)

def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Locate candle/OHLCV/panel sources for Edge Factory offline runner.")
    ap.add_argument("--max_files", type=int, default=5000)
    args = ap.parse_args()

    out_dir = OUT_ROOT / f"candle_source_locator_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = scan(args.max_files)
    rows = sorted(rows, key=lambda x: x["score"], reverse=True)
    groups = group_sources(rows)

    top = rows[0] if rows else None
    top_group = groups[0] if groups else None

    if top_group and top_group["best_score"] >= 70:
        locator_status = "CANDLE_SOURCE_CANDIDATE_FOUND"
        next_action = "BUILD_DATA_SOURCE_BINDING_FOR_RUNNER_REQUEST"
    elif top:
        locator_status = "CANDLE_SOURCE_WEAK_CANDIDATE_FOUND"
        next_action = "MANUAL_REVIEW_TOP_SOURCES"
    else:
        locator_status = "NO_CANDLE_SOURCE_FOUND"
        next_action = "PROVIDE_CANDLE_DATA_SOURCE_PATH"

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "locator_status": locator_status,
        "files_ranked": len(rows),
        "groups_ranked": len(groups),
        "top_file": top,
        "top_group": top_group,
        "next_action": next_action,
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Locator only scans local files.",
            "Does not run backtests.",
            "Does not touch MASTER_UPPER_SYSTEM.",
            "Does not start/stop processes.",
            "Does not place orders."
        ],
    }

    state_path = out_dir / "candle_source_locator_v1_state.json"
    files_json = out_dir / "candle_source_locator_v1_ranked_files.json"
    groups_json = out_dir / "candle_source_locator_v1_ranked_groups.json"
    files_csv = out_dir / "candle_source_locator_v1_ranked_files.csv"
    groups_csv = out_dir / "candle_source_locator_v1_ranked_groups.csv"
    report_path = out_dir / "candle_source_locator_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    files_json.write_text(json.dumps(rows[:200], indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    groups_json.write_text(json.dumps(groups[:100], indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    if rows:
        pd.DataFrame(rows[:200]).drop(columns=["columns"], errors="ignore").to_csv(files_csv, index=False)
    else:
        pd.DataFrame().to_csv(files_csv, index=False)

    if groups:
        pd.DataFrame(groups[:100]).to_csv(groups_csv, index=False)
    else:
        pd.DataFrame().to_csv(groups_csv, index=False)

    md = []
    md.append("# Edge Factory Candle Source Locator v1")
    md.append("")
    md.append(f"Status: `{locator_status}`")
    md.append(f"Files ranked: `{len(rows)}`")
    md.append(f"Groups ranked: `{len(groups)}`")
    md.append(f"Next action: `{next_action}`")
    md.append("")
    if top_group:
        md.append("## Top group")
        md.append(f"- Parent: `{top_group['parent']}`")
        md.append(f"- File count: `{top_group['file_count']}`")
        md.append(f"- Best score: `{top_group['best_score']}`")
        md.append(f"- Sample: `{top_group['sample_file']}`")
    md.append("")
    md.append("## Safety")
    md.append("- live_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY CANDLE SOURCE LOCATOR v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"locator_status: {locator_status}")
    print(f"files_ranked : {len(rows)}")
    print(f"groups_ranked: {len(groups)}")
    print(f"next_action  : {next_action}")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("capital_change_allowed: False")
    print()

    print("TOP GROUPS")
    print("-" * 100)
    if groups:
        gdf = pd.DataFrame(groups[:20])
        print(gdf[["best_score","file_count","candidate_dataset_type","parent","sample_file"]].to_string(index=False))
    else:
        print("No groups.")

    print()
    print("TOP FILES")
    print("-" * 100)
    if rows:
        fdf = pd.DataFrame(rows[:20])
        print(fdf[["score","has_symbol","has_time","has_close","has_ohlc","has_quote_vol","path"]].to_string(index=False))
    else:
        print("No files.")

    print()
    if top:
        print("TOP FILE DETAILS")
        print("-" * 100)
        print("path:", top["path"])
        print("columns:", top["columns"])
        print("reasons:", top["reasons"])
        print("warnings:", top["warnings"])

    print()
    print(f"State : {state_path}")
    print(f"Files : {files_json}")
    print(f"Groups: {groups_json}")
    print(f"CSV files : {files_csv}")
    print(f"CSV groups: {groups_csv}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
