#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnoses the boot status of the MASTER_UPPER_SYSTEM by scanning running Python processes, syntax-checking all component scripts, and inspecting family paper-run directories for recent trade and heartbeat activity.
Outputs a structured boot diagnosis report JSON to the paper_run_gate_MASTER_UPPER_SYSTEM directory.
"""
from __future__ import annotations

import csv
import json
import py_compile
import subprocess
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
SCRIPT_DIR = Path(r"C:\Users\alike")
PAPER_DIR = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"

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
    "risk_manager": ["global_paper_risk_manager", "risk_manager", "risk manager"],
}

def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def compile_ok(path: Path):
    if not path.exists():
        return False, "missing"
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "OK"
    except Exception as e:
        return False, repr(e)

def get_python_processes():
    # PowerShell CIM is more reliable than tasklist for command lines.
    cmd = [
        "powershell",
        "-NoProfile",
        "-Command",
        "Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python' } | Select-Object ProcessId,CommandLine | ConvertTo-Json -Depth 3"
    ]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if p.returncode != 0 or not p.stdout.strip():
            return []
        obj = json.loads(p.stdout)
        if isinstance(obj, dict):
            obj = [obj]
        return obj
    except Exception as e:
        return [{"ProcessId": None, "CommandLine": f"PROCESS_SCAN_ERROR: {e!r}"}]

def process_match(component: str, procs):
    hits = []
    aliases = ALIASES.get(component, [component])
    for p in procs:
        cl = str(p.get("CommandLine") or "")
        low = cl.lower()
        if any(a.lower() in low for a in aliases):
            hits.append({
                "pid": p.get("ProcessId"),
                "command": cl,
            })
    return hits

def file_recent_info(path: Path):
    if not path.exists():
        return None
    st = path.stat()
    return {
        "path": str(path),
        "size": st.st_size,
        "mtime": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
    }

def scan_family_files(family: str):
    if not PAPER_DIR.exists():
        return {
            "paper_dir_exists": False,
            "csv_count": 0,
            "log_count": 0,
            "recent_files": [],
            "closed_like_csv_count": 0,
        }

    aliases = ALIASES.get(family, [family])
    candidates = []

    for p in PAPER_DIR.rglob("*"):
        if not p.is_file():
            continue
        low = str(p).lower()
        if any(a.lower() in low for a in aliases):
            candidates.append(p)

    csvs = [p for p in candidates if p.suffix.lower() == ".csv"]
    logs = [p for p in candidates if p.suffix.lower() in {".log", ".txt", ".json"}]
    closed_like = [p for p in csvs if any(x in str(p).lower() for x in ["closed", "trade", "native", "event"])]

    recent = sorted(candidates, key=lambda x: x.stat().st_mtime, reverse=True)[:10]

    return {
        "paper_dir_exists": PAPER_DIR.exists(),
        "csv_count": len(csvs),
        "log_count": len(logs),
        "closed_like_csv_count": len(closed_like),
        "recent_files": [file_recent_info(p) for p in recent],
    }

def main():
    out_dir = WORKSPACE / "edge_factory_master_upper_system_boot_diagnoser_v1" / f"boot_diag_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    procs = get_python_processes()
    rows = []

    for comp, script in COMPONENTS.items():
        ok, cerr = compile_ok(script)
        hits = process_match(comp, procs)
        files = scan_family_files(comp) if comp != "risk_manager" else scan_family_files("risk_manager")

        running = len(hits) > 0
        has_logs = files.get("csv_count", 0) > 0 or files.get("log_count", 0) > 0

        if comp == "risk_manager":
            expected_state = "RUNNING_OR_ONCE_OK" if running or ok else "BROKEN"
        else:
            expected_state = "RUNNING" if running else "NOT_RUNNING"

        rows.append({
            "component": comp,
            "script": str(script),
            "script_exists": script.exists(),
            "compile_ok": ok,
            "compile_error": cerr,
            "running_process_count": len(hits),
            "running": running,
            "process_hits": hits,
            "paper_dir_exists": files.get("paper_dir_exists"),
            "csv_count": files.get("csv_count"),
            "log_count": files.get("log_count"),
            "closed_like_csv_count": files.get("closed_like_csv_count"),
            "recent_files": files.get("recent_files"),
            "diagnosis": expected_state,
        })

    # Overall classification
    logger_rows = [r for r in rows if r["component"] != "risk_manager"]
    running_loggers = sum(1 for r in logger_rows if r["running"])
    compile_bad = [r for r in rows if not r["compile_ok"]]
    missing_scripts = [r for r in rows if not r["script_exists"]]

    if compile_bad or missing_scripts:
        overall = "BOOT_BLOCKED_SCRIPT_COMPILE_OR_MISSING"
    elif running_loggers == 4:
        overall = "MASTER_UPPER_SYSTEM_LOGGERS_RUNNING"
    elif running_loggers > 0:
        overall = "MASTER_UPPER_SYSTEM_PARTIAL_BOOT"
    else:
        overall = "MASTER_UPPER_SYSTEM_LOGGERS_NOT_RUNNING"

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "paper_dir": str(PAPER_DIR),
        "overall_status": overall,
        "running_logger_count": running_loggers,
        "expected_logger_count": 4,
        "components": rows,
        "live_allowed": False,
        "next_action": (
            "INSPECT_FAILED_COMPONENT_OUTPUTS"
            if overall != "MASTER_UPPER_SYSTEM_LOGGERS_RUNNING"
            else "RUN_HEALTH_CHECK_AND_WAIT_FOR_CLOSED_TRADES"
        )
    }

    state_path = out_dir / "master_upper_system_boot_diagnoser_v1_state.json"
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

    csv_path = out_dir / "master_upper_system_boot_diagnoser_v1_summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "component", "script_exists", "compile_ok", "running_process_count",
            "running", "csv_count", "log_count", "closed_like_csv_count", "diagnosis"
        ])
        w.writeheader()
        for r in rows:
            w.writerow({
                "component": r["component"],
                "script_exists": r["script_exists"],
                "compile_ok": r["compile_ok"],
                "running_process_count": r["running_process_count"],
                "running": r["running"],
                "csv_count": r["csv_count"],
                "log_count": r["log_count"],
                "closed_like_csv_count": r["closed_like_csv_count"],
                "diagnosis": r["diagnosis"],
            })

    print("EDGE FACTORY MASTER UPPER SYSTEM BOOT DIAGNOSER v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"paper_dir : {PAPER_DIR}")
    print(f"output_dir: {out_dir}")
    print(f"overall_status: {overall}")
    print(f"running_logger_count: {running_loggers}/4")
    print("live_allowed: False")
    print()
    print("SUMMARY")
    print("-" * 100)
    for r in rows:
        print(
            f"{r['component']:24s} "
            f"exists={str(r['script_exists']):5s} "
            f"compile={str(r['compile_ok']):5s} "
            f"running={str(r['running']):5s} "
            f"procs={r['running_process_count']} "
            f"csv={r['csv_count']} "
            f"logs={r['log_count']} "
            f"closed_like={r['closed_like_csv_count']} "
            f"diag={r['diagnosis']}"
        )
        if not r["compile_ok"]:
            print("   compile_error:", r["compile_error"])
        if r["process_hits"]:
            for h in r["process_hits"][:3]:
                print(f"   pid={h['pid']} cmd={h['command'][:220]}")
    print()
    print(f"State  : {state_path}")
    print(f"Summary: {csv_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
