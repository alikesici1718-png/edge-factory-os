#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Collects failure signals from the MASTER_UPPER_SYSTEM by scanning running processes, family error CSVs, and paper-run logs to produce a consolidated failure report for diagnostic purposes.
Outputs a failure collection JSON and optionally triggers the system launcher script if all components are confirmed down.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
SCRIPT_DIR = Path(r"C:\Users\alike")
PAPER_DIR = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"
LAUNCHER = SCRIPT_DIR / "start_edge_factory_MASTER_UPPER_SYSTEM.ps1"

COMPONENTS = {
    "old_short": SCRIPT_DIR / "old_short_gate_aware_live_paper_logger.py",
    "impulse_long": SCRIPT_DIR / "impulse_long_gate_aware_live_paper_logger.py",
    "market_relative_short": SCRIPT_DIR / "market_relative_live_paper_logger.py",
    "weak_market_short": SCRIPT_DIR / "weak_market_breakdown_short_live_paper_logger.py",
    "risk_manager": SCRIPT_DIR / "global_paper_risk_manager_v4_config.py",
}

ALIASES = {
    "old_short": ["old_short", "old-short", "old short"],
    "impulse_long": ["impulse_long", "impulse-long", "impulse long"],
    "market_relative_short": ["market_relative", "market-relative", "market relative"],
    "weak_market_short": ["weak_market", "weak-market", "weak market"],
    "risk_manager": ["risk_manager", "global_paper_risk_manager", "global risk"],
}

def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def tail_text(path: Path, max_chars: int = 6000) -> str:
    try:
        txt = path.read_text(encoding="utf-8", errors="replace")
        return txt[-max_chars:]
    except Exception as e:
        return f"READ_ERROR: {e!r}"

def run_help(script: Path) -> dict:
    if not script.exists():
        return {"executed": False, "return_code": None, "stdout": "", "stderr": "missing"}
    try:
        p = subprocess.run(
            [sys.executable, str(script), "--help"],
            capture_output=True,
            text=True,
            timeout=20,
        )
        return {
            "executed": True,
            "return_code": p.returncode,
            "stdout": p.stdout[-5000:],
            "stderr": p.stderr[-5000:],
        }
    except Exception as e:
        return {"executed": False, "return_code": None, "stdout": "", "stderr": repr(e)}

def scan_files(component: str):
    if not PAPER_DIR.exists():
        return []

    aliases = ALIASES.get(component, [component])
    hits = []

    for p in PAPER_DIR.rglob("*"):
        if not p.is_file():
            continue

        low = str(p).lower()
        if not any(a.lower() in low for a in aliases):
            continue

        if p.suffix.lower() not in {".log", ".txt", ".csv", ".json"}:
            continue

        st = p.stat()
        hits.append({
            "path": str(p),
            "suffix": p.suffix.lower(),
            "size": st.st_size,
            "mtime": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
            "tail": tail_text(p, 5000) if p.suffix.lower() in {".log", ".txt", ".json"} else "",
        })

    hits = sorted(hits, key=lambda x: x["mtime"], reverse=True)
    return hits[:20]

def launcher_relevant_lines():
    if not LAUNCHER.exists():
        return []

    lines = LAUNCHER.read_text(encoding="utf-8", errors="replace").splitlines()
    out = []

    keywords = [
        "old_short_gate_aware_live_paper_logger.py",
        "impulse_long_gate_aware_live_paper_logger.py",
        "market_relative_live_paper_logger.py",
        "weak_market_breakdown_short_live_paper_logger.py",
        "global_paper_risk_manager",
        "MASTER_UPPER_SYSTEM",
        "Start-Process",
        "python",
    ]

    for i, line in enumerate(lines, start=1):
        if any(k.lower() in line.lower() for k in keywords):
            out.append({"line_no": i, "line": line})

    return out

def main():
    out_dir = WORKSPACE / "edge_factory_master_upper_system_failure_collector_v1" / f"failure_collect_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    launcher_lines = launcher_relevant_lines()

    components = []
    for name, script in COMPONENTS.items():
        help_result = run_help(script)
        files = scan_files(name)
        components.append({
            "component": name,
            "script": str(script),
            "script_exists": script.exists(),
            "help": help_result,
            "files": files,
        })

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "paper_dir": str(PAPER_DIR),
        "launcher": str(LAUNCHER),
        "launcher_exists": LAUNCHER.exists(),
        "launcher_relevant_lines": launcher_lines,
        "components": components,
        "live_allowed": False,
        "note": "Collector only reads files and --help. It does not start paper/live.",
    }

    state_path = out_dir / "master_upper_system_failure_collector_v1_state.json"
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

    print("EDGE FACTORY MASTER UPPER SYSTEM FAILURE COLLECTOR v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"paper_dir : {PAPER_DIR}")
    print(f"launcher  : {LAUNCHER}")
    print(f"output_dir: {out_dir}")
    print("live_allowed: False")
    print()

    print("LAUNCHER RELEVANT LINES")
    print("-" * 100)
    for x in launcher_lines[:120]:
        print(f"{x['line_no']:>4}: {x['line']}")

    print()
    print("COMPONENT HELP + RECENT FILES")
    print("-" * 100)

    for c in components:
        print()
        print("=" * 100)
        print(c["component"])
        print("-" * 100)
        print(f"script_exists: {c['script_exists']}")
        print(f"help_rc: {c['help']['return_code']}")
        if c["help"]["stderr"]:
            print("HELP STDERR:")
            print(c["help"]["stderr"])
        if c["help"]["stdout"]:
            print("HELP STDOUT:")
            print(c["help"]["stdout"][:2500])

        print("RECENT FILES:")
        if not c["files"]:
            print("  none")
        for f in c["files"][:10]:
            print(f"  {f['mtime']} size={f['size']} {f['path']}")
            if f["tail"]:
                print("  ---- tail ----")
                print(f["tail"][-1500:])
                print("  ------------")

    print()
    print(f"State: {state_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
