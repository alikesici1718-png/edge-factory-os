#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Locates and summarizes available rolling time-OOS evidence files for each active strategy family. Reads OOS summary and fold CSVs from the rolling retrain validator output directory and writes a state JSON with per-family evidence paths, rolling status labels, and fold-level statistics.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

ACTIVE_FAMILIES = [
    "old_short",
    "impulse_long",
    "market_relative_short",
    "weak_market_short",
]

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

def candidate_summary_files() -> list[Path]:
    root = WORKSPACE / "edge_factory_rolling_retrain_validator"
    if not root.exists():
        return []

    files = []
    for d in root.glob("rolling_time_oos_*"):
        if not d.is_dir():
            continue
        p = d / "rolling_time_oos_summary.csv"
        if p.exists():
            files.append(p)

    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)

def normalize(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    family_col = None
    for c in ["family_key", "target_key", "candidate", "target", "family", "name"]:
        if c in out.columns:
            family_col = c
            break

    if family_col is None:
        out["family_key"] = "UNKNOWN"
    else:
        out["family_key"] = out[family_col].astype(str)

    status_col = None
    for c in ["validation_status", "status", "time_oos_status", "verdict", "ledger_result_status"]:
        if c in out.columns:
            status_col = c
            break

    if status_col is None:
        out["rolling_status"] = "UNKNOWN"
    else:
        out["rolling_status"] = out[status_col].astype(str)

    return out

def pick_latest_evidence_for_family(files: list[Path], family: str) -> Optional[Dict[str, Any]]:
    for p in files:
        try:
            df = pd.read_csv(p)
        except Exception:
            continue

        df = normalize(df)
        m = df[df["family_key"].astype(str) == family]
        if m.empty:
            continue

        row = m.iloc[-1].to_dict()
        return {
            "family_key": family,
            "found": True,
            "summary_path": str(p),
            "summary_mtime": datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds"),
            "row": row,
        }

    return {
        "family_key": family,
        "found": False,
        "summary_path": None,
        "summary_mtime": None,
        "row": {},
    }

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_active_family_evidence_locator_v2" / f"active_family_evidence_locator_v2_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = candidate_summary_files()
    rows = []
    detailed = []

    for fam in ACTIVE_FAMILIES:
        ev = pick_latest_evidence_for_family(files, fam)
        detailed.append(ev)

        row = ev.get("row", {}) or {}
        rows.append({
            "family_key": fam,
            "found": ev["found"],
            "summary_path": ev["summary_path"],
            "summary_mtime": ev["summary_mtime"],
            "rolling_status": row.get("validation_status") or row.get("rolling_status") or row.get("status"),
            "target_type": row.get("target_type"),
            "rows_after_cleaning": row.get("rows_after_cleaning"),
            "valid_fold_count": row.get("valid_fold_count"),
            "positive_test_fold_rate": row.get("positive_test_fold_rate"),
            "monthly_positive_rate": row.get("monthly_positive_rate"),
            "test_total_sum": row.get("test_total_sum"),
            "test_pf_aggregate": row.get("test_pf_aggregate"),
            "worst_test_fold": row.get("worst_test_fold"),
            "full_symbol_count": row.get("full_symbol_count"),
            "warnings": row.get("warnings"),
            "reasons": row.get("reasons"),
        })

    df = pd.DataFrame(rows)
    found_count = int(df["found"].sum()) if len(df) else 0

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "locator_status": "ACTIVE_FAMILY_EVIDENCE_FOUND" if found_count == len(ACTIVE_FAMILIES) else "ACTIVE_FAMILY_EVIDENCE_PARTIAL_OR_MISSING",
        "summary_files_scanned": len(files),
        "active_family_count": len(ACTIVE_FAMILIES),
        "found_count": found_count,
        "missing_families": df.loc[~df["found"], "family_key"].tolist() if len(df) else ACTIVE_FAMILIES,
        "active_paper_allowed": False,
        "live_allowed": False,
        "details": detailed,
    }

    write_json(out_dir / "active_family_evidence_locator_v2_state.json", state)
    df.to_csv(out_dir / "active_family_evidence_locator_v2_summary.csv", index=False)

    print("EDGE FACTORY ACTIVE FAMILY EVIDENCE LOCATOR v2")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"locator_status: {state['locator_status']}")
    print(f"summary_files_scanned: {state['summary_files_scanned']}")
    print(f"found_count: {found_count}/{len(ACTIVE_FAMILIES)}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print()
    print("SUMMARY")
    print("-" * 100)
    print(df.to_string(index=False))
    print()
    print(f"State  : {out_dir / 'active_family_evidence_locator_v2_state.json'}")
    print(f"Summary: {out_dir / 'active_family_evidence_locator_v2_summary.csv'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
