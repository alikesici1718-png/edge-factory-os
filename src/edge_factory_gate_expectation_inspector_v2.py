#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Inspects gate decision files and logger scripts to verify that global gate paths, pending entry queues, and risk snapshot references are consistent across all active family loggers. Reads global gate CSV/JSON files and logger Python source files, then writes a gate expectation inspection report with per-family gate path verdicts.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd

USER_DIR = Path(r"C:\Users\alike")
WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
BASE = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"

SCRIPTS = {
    "old_short": USER_DIR / "old_short_gate_aware_live_paper_logger.py",
    "impulse_long": USER_DIR / "impulse_long_gate_aware_live_paper_logger.py",
    "market_relative_short": USER_DIR / "market_relative_live_paper_logger.py",
    "weak_market_short": USER_DIR / "weak_market_breakdown_short_live_paper_logger.py",
    "risk_manager_v4": USER_DIR / "global_paper_risk_manager_v4_config.py",
    "risk_manager_v3": USER_DIR / "global_paper_risk_manager_v3_priority.py",
    "launcher": USER_DIR / "start_edge_factory_MASTER_UPPER_SYSTEM.ps1",
}

GLOBAL_FILES = [
    BASE / "global_gate_decisions.csv",
    BASE / "global_risk_snapshot.csv",
    BASE / "global_risk_violations.csv",
    BASE / "global_risk_config.json",
    BASE / "family_config.json",
    BASE / "edge_factory_config_MASTER_UPPER_SYSTEM.json",
]

SEARCH_TERMS = [
    "global_gate_timeout_gate_file_missing",
    "gate_file_missing",
    "global_gate",
    "gate_decision",
    "gate_decisions",
    "global_risk_snapshot",
    "global_risk_violations",
    "wait",
    "timeout",
    "pending_entries",
    "open_positions",
    "rejected_entries",
    "family_config",
    "out_dir",
    "base_dir",
]

def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def safe_read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")

def read_csv_safe(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception as e:
        return pd.DataFrame({"READ_ERROR": [repr(e)]})

def read_json_safe(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"READ_ERROR": repr(e)}

def snippets_for_terms(path: Path, terms: list[str], radius: int = 12) -> list[dict]:
    text = safe_read(path)
    if not text:
        return []

    lines = text.splitlines()
    out = []
    seen = set()

    for i, line in enumerate(lines):
        low = line.lower()
        hits = [t for t in terms if t.lower() in low]
        if not hits:
            continue

        start = max(0, i - radius)
        end = min(len(lines), i + radius + 1)
        key = (start, end)
        if key in seen:
            continue
        seen.add(key)

        out.append({
            "script": str(path),
            "hit_line": i + 1,
            "hits": "|".join(hits),
            "snippet": "\n".join(f"{j+1}: {lines[j]}" for j in range(start, end)),
        })

    return out

def extract_argparse_lines(path: Path) -> list[dict]:
    text = safe_read(path)
    out = []
    for i, line in enumerate(text.splitlines(), start=1):
        if "add_argument" in line or "ArgumentParser" in line:
            out.append({"script": str(path), "line": i, "text": line.strip()})
    return out

def extract_paths_and_csv_names(path: Path) -> list[dict]:
    text = safe_read(path)
    out = []

    # quoted strings ending in likely filenames
    pat = r'["\']([^"\']*(?:\.csv|\.json|pending_entries|open_positions|rejected_entries|global_gate|global_risk|gate_decisions)[^"\']*)["\']'
    for m in re.finditer(pat, text, flags=re.I):
        out.append({
            "script": str(path),
            "literal": m.group(1),
        })

    return out

def summarize_global_files() -> list[dict]:
    rows = []
    for p in GLOBAL_FILES:
        d = {
            "path": str(p),
            "exists": p.exists(),
            "size": p.stat().st_size if p.exists() else 0,
            "mtime": datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds") if p.exists() else None,
            "columns_or_keys": None,
            "rows": None,
            "head": None,
            "tail": None,
        }

        if p.suffix.lower() == ".csv" and p.exists():
            df = read_csv_safe(p)
            d["rows"] = int(len(df))
            d["columns_or_keys"] = list(df.columns)
            d["head"] = df.head(5).to_dict("records")
            d["tail"] = df.tail(10).to_dict("records")
        elif p.suffix.lower() == ".json" and p.exists():
            obj = read_json_safe(p)
            if isinstance(obj, dict):
                d["columns_or_keys"] = list(obj.keys())
                d["head"] = obj

        rows.append(d)
    return rows

def find_family_files():
    rows = []
    if not BASE.exists():
        return rows
    for fam_dir in BASE.iterdir():
        if not fam_dir.is_dir():
            continue
        for p in fam_dir.glob("*"):
            if not p.is_file():
                continue
            if any(x in p.name.lower() for x in ["gate", "risk", "pending", "open", "reject", "heartbeat", "config"]):
                rows.append({
                    "folder": fam_dir.name,
                    "name": p.name,
                    "path": str(p),
                    "size": p.stat().st_size,
                    "mtime": datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds"),
                })
    return rows

def main():
    out_dir = WORKSPACE / "edge_factory_gate_expectation_inspector_v2" / f"gate_expectation_inspect_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    snippet_rows = []
    argparse_rows = []
    literal_rows = []

    for name, script in SCRIPTS.items():
        snippet_rows.extend(snippets_for_terms(script, SEARCH_TERMS))
        argparse_rows.extend(extract_argparse_lines(script))
        literal_rows.extend(extract_paths_and_csv_names(script))

    snippets_df = pd.DataFrame(snippet_rows)
    argparse_df = pd.DataFrame(argparse_rows)
    literals_df = pd.DataFrame(literal_rows)
    global_rows = summarize_global_files()
    family_files = find_family_files()

    snippets_df.to_csv(out_dir / "script_gate_snippets.csv", index=False)
    argparse_df.to_csv(out_dir / "script_argparse_lines.csv", index=False)
    literals_df.to_csv(out_dir / "script_path_literals.csv", index=False)
    pd.DataFrame(family_files).to_csv(out_dir / "family_gate_related_files.csv", index=False)

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "base": str(BASE),
        "scripts": {k: str(v) for k, v in SCRIPTS.items()},
        "global_files": global_rows,
        "family_files": family_files,
        "snippet_count": len(snippet_rows),
        "argparse_count": len(argparse_rows),
        "literal_count": len(literal_rows),
        "output_dir": str(out_dir),
        "live_allowed": False,
    }

    (out_dir / "gate_expectation_inspector_state.json").write_text(
        json.dumps(state, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

    print("EDGE FACTORY GATE EXPECTATION INSPECTOR v2")
    print("=" * 100)
    print(f"base    : {BASE}")
    print(f"out_dir : {out_dir}")
    print(f"snippet_count: {len(snippet_rows)}")
    print(f"argparse_count: {len(argparse_rows)}")
    print(f"literal_count: {len(literal_rows)}")
    print("live_allowed: False")
    print()

    print("GLOBAL FILE SUMMARIES")
    print("-" * 100)
    for g in global_rows:
        print(f"\nPATH: {g['path']}")
        print(f"exists={g['exists']} size={g['size']} mtime={g['mtime']}")
        print(f"columns_or_keys={g['columns_or_keys']}")
        if g["tail"] is not None:
            print("TAIL:")
            print(pd.DataFrame(g["tail"]).to_string(index=False))
        elif g["head"] is not None:
            print("JSON:")
            print(json.dumps(g["head"], indent=2, ensure_ascii=False, default=str)[:4000])

    print()
    print("PATH LITERALS / EXPECTED FILE NAMES")
    print("-" * 100)
    if not literals_df.empty:
        print(literals_df.drop_duplicates().head(200).to_string(index=False))
    else:
        print("NONE")

    print()
    print("ARGPARSE LINES")
    print("-" * 100)
    if not argparse_df.empty:
        print(argparse_df.to_string(index=False))
    else:
        print("NONE")

    print()
    print("MOST IMPORTANT SNIPPETS")
    print("-" * 100)
    if not snippets_df.empty:
        # Print snippets containing the exact failure first.
        exact = snippets_df[snippets_df["snippet"].str.contains("global_gate_timeout_gate_file_missing", case=False, na=False)]
        other = snippets_df[~snippets_df.index.isin(exact.index)]
        show = pd.concat([exact, other]).head(25)

        for _, r in show.iterrows():
            print("=" * 100)
            print(f"SCRIPT: {r['script']}")
            print(f"HIT LINE: {r['hit_line']} HITS: {r['hits']}")
            print(r["snippet"])
    else:
        print("NONE")

    print()
    print("FAMILY GATE RELATED FILES")
    print("-" * 100)
    fam_df = pd.DataFrame(family_files)
    if not fam_df.empty:
        print(fam_df.head(200).to_string(index=False))
    else:
        print("NONE")

    print()
    print(f"State   : {out_dir / 'gate_expectation_inspector_state.json'}")
    print(f"Snips   : {out_dir / 'script_gate_snippets.csv'}")
    print(f"Args    : {out_dir / 'script_argparse_lines.csv'}")
    print(f"Literals: {out_dir / 'script_path_literals.csv'}")
    print(f"Files   : {out_dir / 'family_gate_related_files.csv'}")

if __name__ == "__main__":
    main()
