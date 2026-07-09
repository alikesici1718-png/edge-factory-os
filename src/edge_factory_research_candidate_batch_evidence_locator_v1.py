#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Batch evidence locator that scans the workspace for CSV, JSON, TXT, and MD files mentioning any of the configured research candidate keys and extracts matching rows and column presence information. Outputs a per-candidate evidence summary JSON and a flat evidence CSV to a timestamped directory under edge_factory_research_candidate_batch_evidence_locator_v1.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

CANDIDATES = [
    "rel_extreme_reversion_short",
    "relative_weakness_snapback_long",
    "market_panic_rebound_long",
    "capitulation_reversal_long",
]

SEARCH_EXTS = [".csv", ".json", ".txt", ".md"]

SKIP_MARKERS = [
    "__pycache__",
    ".git",
    "paper_run_gate_MASTER_UPPER_SYSTEM",
    "paper_run_shadow",
    "edge_factory_paper_sample_watcher",
    "edge_factory_master_upper_system_boot_diagnoser",
]

def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def safe_read_text(path: Path, max_chars: int = 500000) -> str:
    try:
        if path.stat().st_size > max_chars:
            with path.open("r", encoding="utf-8", errors="replace") as f:
                return f.read(max_chars)
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

def should_skip(path: Path) -> bool:
    s = str(path).lower()
    return any(x.lower() in s for x in SKIP_MARKERS)

def scan_file_for_candidates(path: Path) -> list[dict[str, Any]]:
    text = safe_read_text(path)
    if not text:
        return []

    low = text.lower()
    out = []

    for cand in CANDIDATES:
        count = low.count(cand.lower())
        if count > 0:
            out.append({
                "candidate": cand,
                "path": str(path),
                "suffix": path.suffix.lower(),
                "size": path.stat().st_size,
                "mtime": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
                "mention_count": count,
            })

    return out

def try_extract_csv_rows(path: Path, candidate: str) -> dict[str, Any]:
    if path.suffix.lower() != ".csv":
        return {"csv_read": False}

    try:
        df = pd.read_csv(path)
    except Exception as e:
        return {"csv_read": False, "csv_error": repr(e)}

    rows = len(df)
    cols = list(df.columns)

    candidate_rows = 0
    matching_cols = []

    for c in cols:
        try:
            mask = df[c].astype(str).str.contains(candidate, case=False, na=False)
            n = int(mask.sum())
            if n > 0:
                candidate_rows += n
                matching_cols.append(c)
        except Exception:
            pass

    return {
        "csv_read": True,
        "csv_rows": rows,
        "csv_cols": len(cols),
        "candidate_rows_or_mentions": candidate_rows,
        "matching_cols": matching_cols[:10],
    }

def classify_candidate(cand: str, hits: list[dict[str, Any]]) -> dict[str, Any]:
    if not hits:
        return {
            "candidate": cand,
            "evidence_status": "NO_LOCAL_EVIDENCE_FOUND",
            "next_action": "RUN_RULE_DISCOVERY_OR_RESEARCH_SCAN",
            "hit_count": 0,
            "best_path": None,
            "live_allowed": False,
            "active_paper_allowed": False,
        }

    # Prefer CSVs with candidate rows, then recent files.
    enriched = []
    for h in hits:
        extra = try_extract_csv_rows(Path(h["path"]), cand)
        h2 = dict(h)
        h2.update(extra)
        enriched.append(h2)

    csv_row_hits = [h for h in enriched if h.get("csv_read") and h.get("candidate_rows_or_mentions", 0) > 0]
    if csv_row_hits:
        best = sorted(csv_row_hits, key=lambda x: (x.get("candidate_rows_or_mentions", 0), x.get("mtime", "")), reverse=True)[0]
        status = "STRUCTURED_CSV_EVIDENCE_FOUND"
        next_action = "RUN_CANDIDATE_RULE_EXTRACTION_AND_MARKET_REPLAY"
    else:
        best = sorted(enriched, key=lambda x: (x.get("mention_count", 0), x.get("mtime", "")), reverse=True)[0]
        status = "TEXT_OR_ARTIFACT_MENTION_FOUND"
        next_action = "INSPECT_ARTIFACT_AND_EXTRACT_RULE"

    return {
        "candidate": cand,
        "evidence_status": status,
        "next_action": next_action,
        "hit_count": len(hits),
        "best_path": best.get("path"),
        "best_suffix": best.get("suffix"),
        "best_mention_count": best.get("mention_count"),
        "best_csv_rows": best.get("csv_rows"),
        "best_candidate_rows_or_mentions": best.get("candidate_rows_or_mentions"),
        "best_matching_cols": best.get("matching_cols"),
        "live_allowed": False,
        "active_paper_allowed": False,
    }

def main():
    out_dir = WORKSPACE / "edge_factory_research_candidate_batch_evidence_locator_v1" / f"candidate_evidence_locator_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    all_hits = []

    files = []
    for ext in SEARCH_EXTS:
        files.extend(WORKSPACE.rglob(f"*{ext}"))

    for p in files:
        if not p.is_file() or should_skip(p):
            continue
        all_hits.extend(scan_file_for_candidates(p))

    hit_df = pd.DataFrame(all_hits)
    if not hit_df.empty:
        hit_df.to_csv(out_dir / "candidate_evidence_hits.csv", index=False)

    summary_rows = []
    for cand in CANDIDATES:
        hits = [h for h in all_hits if h["candidate"] == cand]
        summary_rows.append(classify_candidate(cand, hits))

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(out_dir / "candidate_evidence_summary.csv", index=False)

    structured_count = int((summary_df["evidence_status"] == "STRUCTURED_CSV_EVIDENCE_FOUND").sum())
    missing_count = int((summary_df["evidence_status"] == "NO_LOCAL_EVIDENCE_FOUND").sum())

    if structured_count > 0:
        overall = "CANDIDATE_BATCH_EVIDENCE_FOUND_READY_FOR_NEXT_RULE_EXTRACTION"
    elif missing_count == len(CANDIDATES):
        overall = "CANDIDATE_BATCH_EVIDENCE_MISSING_NEEDS_RESEARCH_SCAN"
    else:
        overall = "CANDIDATE_BATCH_PARTIAL_TEXT_EVIDENCE_FOUND"

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "overall_status": overall,
        "candidate_count": len(CANDIDATES),
        "structured_evidence_count": structured_count,
        "missing_count": missing_count,
        "total_hits": len(all_hits),
        "live_allowed": False,
        "active_paper_allowed": False,
        "next_action": "BUILD_CANDIDATE_BATCH_RULE_EXTRACTOR" if structured_count > 0 else "RUN_CANDIDATE_RESEARCH_SCAN",
    }

    (out_dir / "candidate_evidence_locator_state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")

    print("EDGE FACTORY RESEARCH CANDIDATE BATCH EVIDENCE LOCATOR v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"overall_status: {overall}")
    print(f"candidate_count: {len(CANDIDATES)}")
    print(f"structured_evidence_count: {structured_count}")
    print(f"missing_count: {missing_count}")
    print(f"total_hits: {len(all_hits)}")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print()
    print("SUMMARY")
    print("-" * 100)
    print(summary_df.to_string(index=False))
    print()
    print(f"State  : {out_dir / 'candidate_evidence_locator_state.json'}")
    print(f"Summary: {out_dir / 'candidate_evidence_summary.csv'}")
    print(f"Hits   : {out_dir / 'candidate_evidence_hits.csv'}")

if __name__ == "__main__":
    main()
