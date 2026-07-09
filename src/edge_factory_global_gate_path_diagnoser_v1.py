#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnoses global gate path configuration issues by scanning the paper run directory for gate-related JSON and CSV files and inspecting logger script source for gate-path references. Reads gate decision files, risk config JSONs, and logger Python source files, then writes a gate path diagnosis report identifying mismatches or missing gate files.
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

SCRIPTS = [
    USER_DIR / "old_short_gate_aware_live_paper_logger.py",
    USER_DIR / "impulse_long_gate_aware_live_paper_logger.py",
    USER_DIR / "market_relative_live_paper_logger.py",
    USER_DIR / "weak_market_breakdown_short_live_paper_logger.py",
    USER_DIR / "global_paper_risk_manager_v4_config.py",
    USER_DIR / "global_paper_risk_manager_v3_priority.py",
    USER_DIR / "start_edge_factory_MASTER_UPPER_SYSTEM.ps1",
]

def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def safe_read(p: Path) -> str:
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="replace")

def find_gate_like_files(root: Path) -> list[dict]:
    rows = []
    if not root.exists():
        return rows

    patterns = [
        "*gate*.json", "*gate*.csv", "*risk*.json", "*risk*.csv",
        "*decision*.json", "*family_config*.json", "*config*.json",
        "*approval*.json",
    ]

    seen = set()
    for pat in patterns:
        for p in root.rglob(pat):
            if p in seen or not p.is_file():
                continue
            seen.add(p)
            rows.append({
                "path": str(p),
                "name": p.name,
                "rel": str(p.relative_to(root)),
                "size": p.stat().st_size,
                "mtime": datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds"),
            })
    return sorted(rows, key=lambda x: x["mtime"], reverse=True)

def extract_gate_strings(script: Path) -> list[dict]:
    text = safe_read(script)
    rows = []
    if not text:
        return rows

    lines = text.splitlines()

    keywords = [
        "gate", "risk", "allow", "decision", "global",
        "timeout", "pending", "open_positions", "rejected_entries",
        "family_config", "out_dir", "base_dir",
    ]

    for i, line in enumerate(lines, start=1):
        low = line.lower()
        if any(k in low for k in keywords):
            if len(line.strip()) > 0:
                rows.append({
                    "script": str(script),
                    "line": i,
                    "text": line.strip()[:500],
                })

    return rows

def extract_literal_paths(script: Path) -> list[dict]:
    text = safe_read(script)
    rows = []
    if not text:
        return rows

    # Quoted strings that look like paths/files.
    for m in re.finditer(r'["\']([^"\']*(?:gate|risk|decision|config|pending|open|reject)[^"\']*)["\']', text, flags=re.I):
        val = m.group(1)
        rows.append({
            "script": str(script),
            "literal": val,
        })
    return rows

def read_json_safe(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None

def main():
    out_dir = WORKSPACE / "edge_factory_global_gate_path_diagnoser_v1" / f"global_gate_path_diag_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    gate_files = find_gate_like_files(BASE)
    script_lines = []
    literals = []

    for s in SCRIPTS:
        script_lines.extend(extract_gate_strings(s))
        literals.extend(extract_literal_paths(s))

    gate_df = pd.DataFrame(gate_files)
    lines_df = pd.DataFrame(script_lines)
    lit_df = pd.DataFrame(literals)

    gate_df.to_csv(out_dir / "gate_like_files_found.csv", index=False)
    lines_df.to_csv(out_dir / "script_gate_related_lines.csv", index=False)
    lit_df.to_csv(out_dir / "script_gate_related_literals.csv", index=False)

    # Try to inspect JSON gate/risk/config files.
    json_summaries = []
    for row in gate_files:
        p = Path(row["path"])
        if p.suffix.lower() != ".json":
            continue
        obj = read_json_safe(p)
        if isinstance(obj, dict):
            json_summaries.append({
                "path": str(p),
                "top_keys": list(obj.keys())[:50],
                "family_keys": list((obj.get("families") or {}).keys()) if isinstance(obj.get("families"), dict) else None,
                "live_allowed": obj.get("live_allowed"),
                "active_paper_only": obj.get("active_paper_only"),
                "global_max_positions": obj.get("global_max_positions"),
                "max_short_positions": obj.get("max_short_positions"),
                "max_long_positions": obj.get("max_long_positions"),
            })

    json_df = pd.DataFrame(json_summaries)
    json_df.to_csv(out_dir / "json_gate_config_summaries.csv", index=False)

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "base": str(BASE),
        "scripts": [str(s) for s in SCRIPTS],
        "gate_like_file_count": len(gate_files),
        "script_gate_related_line_count": len(script_lines),
        "script_gate_related_literal_count": len(literals),
        "output_dir": str(out_dir),
        "live_allowed": False,
    }
    (out_dir / "global_gate_path_diagnoser_state.json").write_text(
        json.dumps(state, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

    print("EDGE FACTORY GLOBAL GATE PATH DIAGNOSER v1")
    print("=" * 100)
    print(f"base    : {BASE}")
    print(f"out_dir : {out_dir}")
    print(f"gate_like_file_count: {len(gate_files)}")
    print(f"script_gate_related_line_count: {len(script_lines)}")
    print(f"script_gate_related_literal_count: {len(literals)}")
    print("live_allowed: False")
    print()

    print("GATE/RISK/CONFIG FILES FOUND")
    print("-" * 100)
    if not gate_df.empty:
        print(gate_df.head(80).to_string(index=False))
    else:
        print("NONE")
    print()

    print("SCRIPT LITERALS")
    print("-" * 100)
    if not lit_df.empty:
        print(lit_df.head(120).to_string(index=False))
    else:
        print("NONE")
    print()

    print("JSON SUMMARIES")
    print("-" * 100)
    if not json_df.empty:
        print(json_df.head(80).to_string(index=False))
    else:
        print("NONE")

    print()
    print(f"State  : {out_dir / 'global_gate_path_diagnoser_state.json'}")
    print(f"Files  : {out_dir / 'gate_like_files_found.csv'}")
    print(f"Lines  : {out_dir / 'script_gate_related_lines.csv'}")
    print(f"Lits   : {out_dir / 'script_gate_related_literals.csv'}")
    print(f"Json   : {out_dir / 'json_gate_config_summaries.csv'}")

if __name__ == "__main__":
    main()
