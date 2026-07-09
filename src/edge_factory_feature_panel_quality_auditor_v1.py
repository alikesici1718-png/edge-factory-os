#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Audits the quality of a built feature panel by checking required column presence, data completeness, and value range sanity. Reads the latest feature panel manifest JSON to locate the panel CSV/Parquet file, runs schema and statistical gate checks, and writes an audit report with pass/fail verdicts per gate.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_feature_panel_quality_auditor_v1"

REQUIRED_COLS = [
    "time", "symbol", "open", "high", "low", "close",
    "entry_vol_quote", "entry_range_bps",
    "coin_ret6_bps", "coin_ret24_bps",
    "mkt_ret6_bps", "mkt_ret24_bps",
]

def latest_manifest() -> Path | None:
    root = WORKSPACE / "edge_factory_feature_panels"
    files = list(root.rglob("*_feature_panel_manifest.json"))
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

def add_gate(rows, gate, passed, severity, evidence):
    rows.append({
        "gate": gate,
        "passed": bool(passed),
        "severity": severity,
        "evidence": str(evidence),
    })

def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Audit built Edge Factory feature panel quality.")
    ap.add_argument("--manifest", default="")
    args = ap.parse_args()

    out_dir = OUT_ROOT / f"feature_panel_quality_audit_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = Path(args.manifest) if args.manifest else latest_manifest()
    manifest = read_json(manifest_path)

    blockers = []
    if not manifest_path or not manifest_path.exists():
        blockers.append("MANIFEST_NOT_FOUND")
    if "__read_error__" in manifest:
        blockers.append("MANIFEST_READ_ERROR")

    panel_path = Path(str(manifest.get("feature_panel_path", ""))) if manifest else None
    candidate_key = manifest.get("candidate_key", "UNKNOWN") if manifest else "UNKNOWN"

    if not panel_path or not panel_path.exists():
        blockers.append("PANEL_NOT_FOUND")

    gates = []
    df = pd.DataFrame()

    if not blockers:
        if panel_path.suffix.lower() == ".parquet":
            df = pd.read_parquet(panel_path)
        else:
            df = pd.read_csv(panel_path)

        df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce")

        row_count = len(df)
        symbol_count = int(df["symbol"].nunique()) if "symbol" in df.columns else 0
        first_time = df["time"].min()
        last_time = df["time"].max()

        missing_cols = [c for c in REQUIRED_COLS if c not in df.columns]
        add_gate(gates, "required_columns_present", len(missing_cols) == 0, "CRITICAL", missing_cols)

        add_gate(gates, "row_count_min_1m", row_count >= 1_000_000, "CRITICAL", row_count)
        add_gate(gates, "symbol_count_min_200", symbol_count >= 200, "CRITICAL", symbol_count)

        if "time" in df.columns:
            span_days = (last_time - first_time).total_seconds() / 86400 if pd.notna(first_time) and pd.notna(last_time) else 0
        else:
            span_days = 0
        add_gate(gates, "time_span_min_300_days", span_days >= 300, "CRITICAL", span_days)

        duplicate_count = int(df.duplicated(subset=["time", "symbol"]).sum()) if {"time", "symbol"}.issubset(df.columns) else -1
        add_gate(gates, "no_duplicate_time_symbol", duplicate_count == 0, "CRITICAL", duplicate_count)

        numeric_cols = [c for c in REQUIRED_COLS if c in df.columns and c not in {"time", "symbol"}]
        inf_counts = {}
        nan_ratios = {}
        p999_abs = {}

        for c in numeric_cols:
            s = pd.to_numeric(df[c], errors="coerce")
            inf_counts[c] = int(np.isinf(s).sum())
            nan_ratios[c] = float(s.isna().mean())
            clean = s.replace([np.inf, -np.inf], np.nan).dropna()
            p999_abs[c] = float(clean.abs().quantile(0.999)) if len(clean) else None

        add_gate(gates, "no_inf_numeric_values", sum(inf_counts.values()) == 0, "CRITICAL", inf_counts)

        # Returns need first 6/24h nulls, so tolerate small NaN ratios.
        for c in ["open", "high", "low", "close", "entry_vol_quote", "entry_range_bps"]:
            if c in nan_ratios:
                add_gate(gates, f"nan_ratio_low:{c}", nan_ratios[c] < 0.001, "CRITICAL", nan_ratios[c])

        for c in ["coin_ret6_bps", "coin_ret24_bps", "mkt_ret6_bps", "mkt_ret24_bps"]:
            if c in nan_ratios:
                add_gate(gates, f"nan_ratio_acceptable:{c}", nan_ratios[c] < 0.01, "ATTENTION", nan_ratios[c])

        if "entry_vol_quote" in df.columns:
            vol = pd.to_numeric(df["entry_vol_quote"], errors="coerce")
            add_gate(gates, "entry_vol_quote_non_negative", int((vol < 0).sum()) == 0, "CRITICAL", int((vol < 0).sum()))
            add_gate(gates, "entry_vol_quote_has_positive_values", int((vol > 0).sum()) > row_count * 0.5, "ATTENTION", int((vol > 0).sum()))

        if "entry_range_bps" in df.columns:
            rng = pd.to_numeric(df["entry_range_bps"], errors="coerce")
            add_gate(gates, "entry_range_bps_non_negative", int((rng < 0).sum()) == 0, "CRITICAL", int((rng < 0).sum()))
            add_gate(gates, "entry_range_bps_reasonable_p999", float(rng.quantile(0.999)) < 10000, "ATTENTION", float(rng.quantile(0.999)))

        symbol_summary = df.groupby("symbol").agg(
            rows=("time", "count"),
            first_time=("time", "min"),
            last_time=("time", "max"),
            close_nonnull=("close", lambda x: int(pd.notna(x).sum())),
        ).reset_index() if {"symbol", "time", "close"}.issubset(df.columns) else pd.DataFrame()

        if not symbol_summary.empty:
            weak_symbols = symbol_summary[symbol_summary["rows"] < 500]
            add_gate(gates, "few_symbols_with_too_little_data", len(weak_symbols) <= 10, "ATTENTION", len(weak_symbols))
        else:
            weak_symbols = pd.DataFrame()

        critical_failed = [g for g in gates if not g["passed"] and g["severity"] == "CRITICAL"]
        attention_failed = [g for g in gates if not g["passed"] and g["severity"] == "ATTENTION"]

        if critical_failed:
            audit_status = "FEATURE_PANEL_QUALITY_CRITICAL_FAIL"
            runner_panel_allowed = False
            next_action = "FIX_PANEL_CRITICAL_ISSUES"
        elif attention_failed:
            audit_status = "FEATURE_PANEL_QUALITY_ATTENTION_PASS_WITH_WARNINGS"
            runner_panel_allowed = True
            next_action = "REVIEW_WARNINGS_THEN_CREATE_OFFLINE_RUNNER_PLAN"
        else:
            audit_status = "FEATURE_PANEL_QUALITY_PASS"
            runner_panel_allowed = True
            next_action = "CREATE_OFFLINE_RUNNER_PLAN"

        quality_summary = {
            "row_count": row_count,
            "symbol_count": symbol_count,
            "first_time": str(first_time),
            "last_time": str(last_time),
            "span_days": span_days,
            "duplicate_count": duplicate_count,
            "nan_ratios": nan_ratios,
            "inf_counts": inf_counts,
            "p999_abs": p999_abs,
            "weak_symbol_count": int(len(weak_symbols)),
        }

    else:
        audit_status = "FEATURE_PANEL_QUALITY_AUDIT_BLOCKED"
        runner_panel_allowed = False
        next_action = "FIX_AUDIT_INPUTS"
        critical_failed = []
        attention_failed = []
        quality_summary = {}

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "candidate_key": candidate_key,
        "manifest_path": str(manifest_path) if manifest_path else None,
        "panel_path": str(panel_path) if panel_path else None,
        "audit_status": audit_status,
        "blockers": blockers,
        "critical_failed": len(critical_failed),
        "attention_failed": len(attention_failed),
        "runner_panel_allowed": runner_panel_allowed,
        "runner_execution_allowed": False,
        "next_action": next_action,
        "quality_summary": quality_summary,
        "gates": gates,
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Quality auditor only reads feature panel.",
            "Does not run strategy backtest.",
            "Does not touch MASTER_UPPER_SYSTEM.",
            "Does not start/stop processes.",
            "Does not place orders.",
            "Does not enable live trading."
        ],
    }

    state_path = out_dir / "feature_panel_quality_audit_v1_state.json"
    gates_csv = out_dir / "feature_panel_quality_audit_v1_gates.csv"
    symbol_csv = out_dir / "feature_panel_quality_audit_v1_symbol_summary.csv"
    report_path = out_dir / "feature_panel_quality_audit_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    pd.DataFrame(gates).to_csv(gates_csv, index=False)

    if not df.empty and "symbol_summary" in locals() and not symbol_summary.empty:
        symbol_summary.to_csv(symbol_csv, index=False)
    else:
        pd.DataFrame().to_csv(symbol_csv, index=False)

    md = []
    md.append("# Edge Factory Feature Panel Quality Audit v1")
    md.append("")
    md.append(f"Status: `{audit_status}`")
    md.append(f"Candidate: `{candidate_key}`")
    md.append(f"Critical failed: `{len(critical_failed)}`")
    md.append(f"Attention failed: `{len(attention_failed)}`")
    md.append(f"Runner panel allowed: `{runner_panel_allowed}`")
    md.append(f"Next action: `{next_action}`")
    md.append("")
    md.append("## Failed gates")
    failed = critical_failed + attention_failed
    if failed:
        for g in failed:
            md.append(f"- `{g['severity']}` `{g['gate']}` — {g['evidence']}")
    else:
        md.append("- None")
    md.append("")
    md.append("## Safety")
    md.append("- runner_execution_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY FEATURE PANEL QUALITY AUDIT v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"candidate : {candidate_key}")
    print(f"audit_status: {audit_status}")
    print(f"critical_failed : {len(critical_failed)}")
    print(f"attention_failed: {len(attention_failed)}")
    print(f"runner_panel_allowed: {runner_panel_allowed}")
    print(f"runner_execution_allowed: False")
    print(f"next_action: {next_action}")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("QUALITY SUMMARY")
    print("-" * 100)
    print(json.dumps(quality_summary, indent=2, ensure_ascii=False))
    print()
    print("FAILED GATES")
    print("-" * 100)
    failed_df = pd.DataFrame([g for g in gates if not g["passed"]])
    if failed_df.empty:
        print("NONE")
    else:
        print(failed_df[["severity", "gate", "evidence"]].to_string(index=False))
    print()
    print(f"State : {state_path}")
    print(f"Gates : {gates_csv}")
    print(f"Symbol: {symbol_csv}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
