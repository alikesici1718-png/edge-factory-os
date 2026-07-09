#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Batch rule profiler that reads trade/signal CSV files for multiple research candidates, extracts candidate-specific rows, and computes family-level performance metrics (profit factor, win rate, drawdown, symbol breadth) for each. Outputs a profiler state JSON and a per-candidate results CSV to a timestamped directory under edge_factory_research_candidate_batch_rule_profiler_v1.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import numpy as np

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

CANDIDATES = [
    "rel_extreme_reversion_short",
    "relative_weakness_snapback_long",
    "market_panic_rebound_long",
    "capitulation_reversal_long",
]

FAMILY_COL_CANDIDATES = ["family", "candidate", "target_key", "family_key", "variant_key", "strategy"]
PNL_COL_CANDIDATES = ["pnl", "net_pnl", "net_pnl_usdt", "pnl_usdt", "total_pnl", "ret_bps", "net_ret_bps", "return_bps"]
SYMBOL_COL_CANDIDATES = ["symbol", "coin", "inst", "inst_id", "ticker"]
TIME_COL_CANDIDATES = ["event_time", "signal_time", "entry_time", "exit_time", "timestamp", "time", "datetime"]
VARIANT_COL_CANDIDATES = ["variant_key", "variant", "candidate", "family", "strategy"]

def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def latest_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    return sorted(ds, key=lambda x: x.stat().st_mtime, reverse=True)[0] if ds else None

def write_json(path: Path, obj: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

def find_col(df: pd.DataFrame, names: list[str]) -> Optional[str]:
    lower = {str(c).lower(): c for c in df.columns}
    for n in names:
        if n.lower() in lower:
            return lower[n.lower()]
    for c in df.columns:
        cl = str(c).lower()
        for n in names:
            if n.lower() in cl:
                return c
    return None

def numeric_cols(df: pd.DataFrame) -> list[str]:
    out = []
    for c in df.columns:
        s = pd.to_numeric(df[c], errors="coerce")
        if s.notna().mean() > 0.70:
            out.append(c)
    return out

def extract_candidate_rows(df: pd.DataFrame, cand: str) -> pd.DataFrame:
    masks = []

    for c in df.columns:
        try:
            s = df[c].astype(str)
            m = s.str.contains(cand, case=False, na=False)
            if m.any():
                masks.append(m)
        except Exception:
            pass

    if not masks:
        return pd.DataFrame()

    mask = masks[0]
    for m in masks[1:]:
        mask = mask | m

    return df[mask].copy()

def profit_factor(pnl: pd.Series) -> float:
    x = pd.to_numeric(pnl, errors="coerce").dropna()
    if x.empty:
        return 0.0
    wins = x[x > 0].sum()
    losses = -x[x < 0].sum()
    if losses <= 0:
        return 999999.0 if wins > 0 else 0.0
    return float(wins / losses)

def summarize_numeric_features(df: pd.DataFrame, pnl_col: Optional[str]) -> list[dict[str, Any]]:
    nums = numeric_cols(df)
    banned = set()
    if pnl_col:
        banned.add(pnl_col)

    feature_rows = []

    for c in nums:
        if c in banned:
            continue

        s = pd.to_numeric(df[c], errors="coerce")
        if s.notna().sum() < 20:
            continue

        name = str(c).lower()

        # Prefer rule-like/feature-like columns over pure bookkeeping.
        score = 0
        for key in ["ret", "bps", "rel", "market", "weak", "panic", "capit", "rank", "z", "move", "range", "vol", "dd", "draw", "threshold"]:
            if key in name:
                score += 2
        for bad in ["pnl", "equity", "id", "count", "rows"]:
            if bad in name:
                score -= 3

        row = {
            "column": c,
            "score": score,
            "non_null": int(s.notna().sum()),
            "min": float(s.min()),
            "q05": float(s.quantile(0.05)),
            "median": float(s.median()),
            "q95": float(s.quantile(0.95)),
            "max": float(s.max()),
            "mean": float(s.mean()),
        }

        if pnl_col:
            pnl = pd.to_numeric(df[pnl_col], errors="coerce")
            ok = s.notna() & pnl.notna()
            if ok.sum() >= 20 and s[ok].nunique() > 2:
                try:
                    row["corr_with_pnl"] = float(s[ok].corr(pnl[ok]))
                except Exception:
                    row["corr_with_pnl"] = None

        feature_rows.append(row)

    return sorted(feature_rows, key=lambda r: (r.get("score", 0), abs(r.get("corr_with_pnl") or 0)), reverse=True)[:30]

def profile_candidate(cand: str, path: Path, out_dir: Path) -> dict[str, Any]:
    try:
        df = pd.read_csv(path)
    except Exception as e:
        return {
            "candidate": cand,
            "source_path": str(path),
            "status": "READ_FAIL",
            "error": repr(e),
            "live_allowed": False,
            "active_paper_allowed": False,
        }

    cdf = extract_candidate_rows(df, cand)
    if cdf.empty:
        return {
            "candidate": cand,
            "source_path": str(path),
            "status": "NO_ROWS_FOR_CANDIDATE",
            "source_rows": int(len(df)),
            "live_allowed": False,
            "active_paper_allowed": False,
        }

    family_col = find_col(cdf, FAMILY_COL_CANDIDATES)
    pnl_col = find_col(cdf, PNL_COL_CANDIDATES)
    symbol_col = find_col(cdf, SYMBOL_COL_CANDIDATES)
    time_col = find_col(cdf, TIME_COL_CANDIDATES)
    variant_col = find_col(cdf, VARIANT_COL_CANDIDATES)

    out_candidate_dir = out_dir / "candidates" / cand
    out_candidate_dir.mkdir(parents=True, exist_ok=True)

    sample_path = out_candidate_dir / f"{cand}_matched_rows_sample.csv"
    cdf.head(5000).to_csv(sample_path, index=False)

    pnl_summary = {}
    if pnl_col:
        pnl = pd.to_numeric(cdf[pnl_col], errors="coerce")
        pnl_summary = {
            "pnl_col": pnl_col,
            "pnl_non_null": int(pnl.notna().sum()),
            "pnl_sum": float(pnl.sum()),
            "pnl_mean": float(pnl.mean()),
            "pnl_median": float(pnl.median()),
            "win_rate": float((pnl > 0).mean()),
            "profit_factor": profit_factor(pnl),
            "pnl_min": float(pnl.min()),
            "pnl_max": float(pnl.max()),
        }

    symbol_summary = {}
    if symbol_col:
        syms = cdf[symbol_col].astype(str)
        symbol_summary = {
            "symbol_col": symbol_col,
            "symbol_count": int(syms.nunique()),
            "top_symbols": syms.value_counts().head(20).to_dict(),
        }

    time_summary = {}
    if time_col:
        ts = pd.to_datetime(cdf[time_col], errors="coerce", utc=True)
        time_summary = {
            "time_col": time_col,
            "time_non_null": int(ts.notna().sum()),
            "first_time": str(ts.min()) if ts.notna().any() else None,
            "last_time": str(ts.max()) if ts.notna().any() else None,
        }

    variant_summary = {}
    if variant_col:
        variant_summary = {
            "variant_col": variant_col,
            "variant_count": int(cdf[variant_col].astype(str).nunique()),
            "top_variants": cdf[variant_col].astype(str).value_counts().head(25).to_dict(),
        }

    feature_summary = summarize_numeric_features(cdf, pnl_col)
    pd.DataFrame(feature_summary).to_csv(out_candidate_dir / f"{cand}_numeric_feature_profile.csv", index=False)

    status = "RULE_PROFILE_READY_FOR_EXACT_EXTRACTION"
    blockers = []

    if not pnl_col:
        blockers.append("pnl column not identified")
    if not symbol_col:
        blockers.append("symbol column not identified")
    if not feature_summary:
        blockers.append("no feature-like numeric columns found")

    if blockers:
        status = "RULE_PROFILE_PARTIAL_NEEDS_MANUAL_COLUMN_MAPPING"

    return {
        "candidate": cand,
        "source_path": str(path),
        "status": status,
        "source_rows": int(len(df)),
        "matched_rows": int(len(cdf)),
        "matched_sample_path": str(sample_path),
        "family_col": family_col,
        "pnl_col": pnl_col,
        "symbol_col": symbol_col,
        "time_col": time_col,
        "variant_col": variant_col,
        "pnl_summary": pnl_summary,
        "symbol_summary": symbol_summary,
        "time_summary": time_summary,
        "variant_summary": variant_summary,
        "top_feature_candidates": feature_summary[:15],
        "blockers": blockers,
        "next_action": "BUILD_EXACT_RULE_EXTRACTOR_FOR_CANDIDATE" if not blockers else "ADD_COLUMN_MAPPING_THEN_EXTRACT_RULE",
        "live_allowed": False,
        "active_paper_allowed": False,
    }

def main():
    out_dir = WORKSPACE / "edge_factory_research_candidate_batch_rule_profiler_v1" / f"candidate_rule_profile_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    loc_dir = latest_dir(WORKSPACE / "edge_factory_research_candidate_batch_evidence_locator_v1", "candidate_evidence_locator_")
    summary_path = loc_dir / "candidate_evidence_summary.csv" if loc_dir else None

    if not summary_path or not summary_path.exists():
        raise SystemExit("candidate evidence summary not found; run locator first")

    locator_df = pd.read_csv(summary_path)

    results = []
    for cand in CANDIDATES:
        row = locator_df[locator_df["candidate"].astype(str) == cand]
        if row.empty:
            results.append({
                "candidate": cand,
                "status": "MISSING_FROM_LOCATOR",
                "live_allowed": False,
                "active_paper_allowed": False,
            })
            continue

        best_path = Path(str(row.iloc[-1]["best_path"]))
        results.append(profile_candidate(cand, best_path, out_dir))

    flat_rows = []
    for r in results:
        pnl = r.get("pnl_summary") or {}
        sym = r.get("symbol_summary") or {}
        tim = r.get("time_summary") or {}
        var = r.get("variant_summary") or {}

        flat_rows.append({
            "candidate": r.get("candidate"),
            "status": r.get("status"),
            "source_path": r.get("source_path"),
            "source_rows": r.get("source_rows"),
            "matched_rows": r.get("matched_rows"),
            "pnl_col": r.get("pnl_col"),
            "pnl_sum": pnl.get("pnl_sum"),
            "pnl_mean": pnl.get("pnl_mean"),
            "win_rate": pnl.get("win_rate"),
            "profit_factor": pnl.get("profit_factor"),
            "symbol_col": r.get("symbol_col"),
            "symbol_count": sym.get("symbol_count"),
            "time_col": r.get("time_col"),
            "first_time": tim.get("first_time"),
            "last_time": tim.get("last_time"),
            "variant_col": r.get("variant_col"),
            "variant_count": var.get("variant_count"),
            "blockers": " | ".join(r.get("blockers") or []),
            "next_action": r.get("next_action"),
            "live_allowed": False,
            "active_paper_allowed": False,
        })

    flat_df = pd.DataFrame(flat_rows)
    flat_df.to_csv(out_dir / "candidate_rule_profiler_summary.csv", index=False)

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "locator_summary": str(summary_path),
        "candidate_count": len(results),
        "ready_count": int((flat_df["status"] == "RULE_PROFILE_READY_FOR_EXACT_EXTRACTION").sum()),
        "partial_count": int(flat_df["status"].astype(str).str.contains("PARTIAL").sum()),
        "live_allowed": False,
        "active_paper_allowed": False,
        "results": results,
        "next_action": "BUILD_CANDIDATE_EXACT_RULE_EXTRACTOR_BATCH",
    }

    write_json(out_dir / "candidate_rule_profiler_state.json", state)

    print("EDGE FACTORY RESEARCH CANDIDATE BATCH RULE PROFILER v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"candidate_count: {state['candidate_count']}")
    print(f"ready_count: {state['ready_count']}")
    print(f"partial_count: {state['partial_count']}")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print()
    print("SUMMARY")
    print("-" * 100)
    print(flat_df.to_string(index=False))
    print()
    print(f"State  : {out_dir / 'candidate_rule_profiler_state.json'}")
    print(f"Summary: {out_dir / 'candidate_rule_profiler_summary.csv'}")

if __name__ == "__main__":
    main()
