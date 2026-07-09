#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Audits the schema of candidate trade CSV artifacts to ensure column classification is unambiguous before robustness validators are trusted. Reads source trade CSVs and validator output files, classifies each column as symbol, PnL, outcome, feature/parameter, or time, and writes a schema audit report with pass/fail verdicts per candidate.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

CANDIDATES = [
    "rel_extreme_reversion_short",
    "relative_weakness_snapback_long",
    "market_panic_rebound_long",
    "capitulation_reversal_long",
]

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

def classify_col(name: str) -> str:
    n = name.lower()

    if n in {"symbol", "coin", "inst", "inst_id", "ticker"}:
        return "SYMBOL"
    if "symbol" in n or n == "coin":
        return "SYMBOL_LIKELY"

    if "pnl" in n or "profit" in n:
        return "PNL_LIKELY"

    if any(x in n for x in ["future", "fwd", "forward", "exit", "hold", "target_ret", "realized", "net_ret"]):
        return "OUTCOME_LIKELY"

    if any(x in n for x in ["ret", "bps", "z", "rank", "threshold", "market", "relative", "weak", "panic", "capitulation", "range", "vol"]):
        return "FEATURE_OR_PARAM"

    if any(x in n for x in ["time", "date", "timestamp"]):
        return "TIME"

    if any(x in n for x in ["variant", "candidate", "family", "strategy"]):
        return "IDENTIFIER"

    return "OTHER"

def candidate_rows(df: pd.DataFrame, cand: str) -> pd.DataFrame:
    masks = []
    for c in df.columns:
        try:
            m = df[c].astype(str).str.contains(cand, case=False, na=False)
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

def numeric_summary(s: pd.Series) -> dict[str, Any]:
    x = pd.to_numeric(s, errors="coerce")
    if x.notna().sum() == 0:
        return {}

    return {
        "non_null": int(x.notna().sum()),
        "min": float(x.min()),
        "q05": float(x.quantile(0.05)),
        "median": float(x.median()),
        "mean": float(x.mean()),
        "q95": float(x.quantile(0.95)),
        "max": float(x.max()),
        "positive_rate": float((x > 0).mean()),
        "negative_rate": float((x < 0).mean()),
        "zero_rate": float((x == 0).mean()),
    }

def audit_source(cand: str, path: Path, out_dir: Path) -> dict[str, Any]:
    try:
        df = pd.read_csv(path)
    except Exception as e:
        return {
            "candidate": cand,
            "source_path": str(path),
            "status": "READ_FAIL",
            "error": repr(e),
        }

    cdf = candidate_rows(df, cand)
    if cdf.empty:
        return {
            "candidate": cand,
            "source_path": str(path),
            "status": "NO_CANDIDATE_ROWS",
            "source_rows": len(df),
        }

    cdir = out_dir / "candidates" / cand
    cdir.mkdir(parents=True, exist_ok=True)

    cdf.head(1000).to_csv(cdir / f"{cand}_sample_rows.csv", index=False)

    col_rows = []
    for c in cdf.columns:
        cls = classify_col(str(c))
        row = {
            "candidate": cand,
            "column": c,
            "classification": cls,
            "dtype": str(cdf[c].dtype),
            "non_null": int(cdf[c].notna().sum()),
            "unique_count": int(cdf[c].astype(str).nunique()),
            "sample_values": " | ".join(cdf[c].astype(str).dropna().head(8).tolist()),
        }
        ns = numeric_summary(cdf[c])
        row.update({f"num_{k}": v for k, v in ns.items()})
        col_rows.append(row)

    col_df = pd.DataFrame(col_rows)
    col_df.to_csv(cdir / f"{cand}_column_audit.csv", index=False)

    # Conservative mapping.
    symbol_candidates = col_df[col_df["classification"].isin(["SYMBOL", "SYMBOL_LIKELY"])]["column"].tolist()
    outcome_candidates = col_df[col_df["classification"].isin(["PNL_LIKELY", "OUTCOME_LIKELY"])]["column"].tolist()
    feature_candidates = col_df[col_df["classification"].eq("FEATURE_OR_PARAM")]["column"].tolist()
    id_candidates = col_df[col_df["classification"].eq("IDENTIFIER")]["column"].tolist()
    time_candidates = col_df[col_df["classification"].eq("TIME")]["column"].tolist()

    # Explicit warning rules.
    warnings = []
    if "coin_ret_bps" in cdf.columns:
        warnings.append("coin_ret_bps looks like feature/input return, not safe as realized PnL without confirmation")
    if not outcome_candidates:
        warnings.append("no safe realized/outcome/PnL column identified")
    if not symbol_candidates:
        warnings.append("no safe symbol column identified")
    if any("threshold" in str(x).lower() for x in symbol_candidates):
        warnings.append("symbol mapping suspicious: threshold column classified as symbol")

    if outcome_candidates and symbol_candidates:
        status = "SCHEMA_READY_FOR_RULE_EXTRACTION_WITH_OUTCOME"
    elif symbol_candidates and feature_candidates:
        status = "SCHEMA_RULE_FEATURES_READY_BUT_OUTCOME_MISSING"
    else:
        status = "SCHEMA_PARTIAL_NEEDS_MANUAL_MAPPING"

    return {
        "candidate": cand,
        "source_path": str(path),
        "status": status,
        "source_rows": int(len(df)),
        "candidate_rows": int(len(cdf)),
        "symbol_candidates": symbol_candidates,
        "outcome_candidates": outcome_candidates,
        "feature_candidates_top": feature_candidates[:30],
        "identifier_candidates": id_candidates,
        "time_candidates": time_candidates,
        "warnings": warnings,
        "sample_rows": str(cdir / f"{cand}_sample_rows.csv"),
        "column_audit": str(cdir / f"{cand}_column_audit.csv"),
        "live_allowed": False,
        "active_paper_allowed": False,
    }

def main():
    out_dir = WORKSPACE / "edge_factory_candidate_artifact_schema_auditor_v2" / f"candidate_schema_audit_v2_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    profiler_dir = latest_dir(WORKSPACE / "edge_factory_research_candidate_batch_rule_profiler_v1", "candidate_rule_profile_")
    summary_path = profiler_dir / "candidate_rule_profiler_summary.csv" if profiler_dir else None

    if not summary_path or not summary_path.exists():
        raise SystemExit("candidate_rule_profiler_summary.csv not found")

    prof = pd.read_csv(summary_path)

    results = []
    for cand in CANDIDATES:
        row = prof[prof["candidate"].astype(str) == cand]
        if row.empty:
            results.append({"candidate": cand, "status": "MISSING_FROM_PROFILER"})
            continue
        source_path = Path(str(row.iloc[-1]["source_path"]))
        results.append(audit_source(cand, source_path, out_dir))

    flat = []
    for r in results:
        flat.append({
            "candidate": r.get("candidate"),
            "status": r.get("status"),
            "source_path": r.get("source_path"),
            "source_rows": r.get("source_rows"),
            "candidate_rows": r.get("candidate_rows"),
            "symbol_candidates": " | ".join(r.get("symbol_candidates") or []),
            "outcome_candidates": " | ".join(r.get("outcome_candidates") or []),
            "feature_candidates_top": " | ".join((r.get("feature_candidates_top") or [])[:15]),
            "identifier_candidates": " | ".join(r.get("identifier_candidates") or []),
            "time_candidates": " | ".join(r.get("time_candidates") or []),
            "warnings": " | ".join(r.get("warnings") or []),
            "live_allowed": False,
            "active_paper_allowed": False,
        })

    flat_df = pd.DataFrame(flat)
    flat_df.to_csv(out_dir / "candidate_schema_audit_v2_summary.csv", index=False)

    ready_with_outcome = int((flat_df["status"] == "SCHEMA_READY_FOR_RULE_EXTRACTION_WITH_OUTCOME").sum())
    ready_features_only = int((flat_df["status"] == "SCHEMA_RULE_FEATURES_READY_BUT_OUTCOME_MISSING").sum())

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "profiler_summary": str(summary_path),
        "candidate_count": len(results),
        "ready_with_outcome_count": ready_with_outcome,
        "ready_features_only_count": ready_features_only,
        "live_allowed": False,
        "active_paper_allowed": False,
        "results": results,
        "next_action": "EXTRACT_RULES_FOR_READY_CANDIDATES_BUT_REQUIRE_OUTCOME_CONFIRMATION",
    }

    write_json(out_dir / "candidate_schema_audit_v2_state.json", state)

    print("EDGE FACTORY CANDIDATE ARTIFACT SCHEMA AUDITOR v2")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"candidate_count: {len(results)}")
    print(f"ready_with_outcome_count: {ready_with_outcome}")
    print(f"ready_features_only_count: {ready_features_only}")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print()
    print("SUMMARY")
    print("-" * 100)
    print(flat_df.to_string(index=False))
    print()
    print(f"State  : {out_dir / 'candidate_schema_audit_v2_state.json'}")
    print(f"Summary: {out_dir / 'candidate_schema_audit_v2_summary.csv'}")

if __name__ == "__main__":
    main()
