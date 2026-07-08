#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
RUN = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"
LOG_DIR = RUN / "startup_logs_v2"
OUT_ROOT = WORKSPACE / "edge_factory_master_startup_diagnoser_v1"

COMPONENTS = {
    "risk_manager": ["global_paper_risk_manager_v4_config.py", "global_paper_risk_manager_v3_priority.py"],
    "old_short_logger": ["old_short_gate_aware_live_paper_logger.py"],
    "impulse_long_logger": ["impulse_long_gate_aware_live_paper_logger.py"],
    "market_relative_logger": ["market_relative_live_paper_logger.py"],
    "weak_market_logger": ["weak_market_breakdown_short_live_paper_logger.py"],
    "autopilot_v4": ["edge_factory_os_autopilot_loop_v4.py"],
}

def get_processes():
    cmd = r"""
Get-CimInstance Win32_Process |
Select-Object ProcessId, Name, CommandLine |
ConvertTo-Json -Depth 3
"""
    try:
        p = subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True,
            text=True,
            timeout=30,
        )
        raw = p.stdout.strip()
        if not raw:
            return []
        data = json.loads(raw)
        if isinstance(data, dict):
            return [data]
        return data
    except Exception:
        return []

def tail(path: Path, n: int = 80) -> str:
    if not path.exists():
        return "MISSING"
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[-n:])
    except Exception as e:
        return f"READ_ERROR: {e!r}"

def main():
    out_dir = OUT_ROOT / f"master_startup_diagnoser_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    procs = get_processes()
    rows = []

    for name, patterns in COMPONENTS.items():
        matches = []
        for pr in procs:
            cmd = str(pr.get("CommandLine") or "")
            for pat in patterns:
                if pat.lower() in cmd.lower():
                    matches.append(pr)
                    break

        stdout = LOG_DIR / f"{name}.stdout.log"
        stderr = LOG_DIR / f"{name}.stderr.log"

        rows.append({
            "component": name,
            "patterns": patterns,
            "running": len(matches) > 0,
            "process_count": len(matches),
            "pids": [m.get("ProcessId") for m in matches],
            "sample_command": str(matches[0].get("CommandLine"))[:800] if matches else "",
            "stdout_path": str(stdout),
            "stderr_path": str(stderr),
            "stdout_tail": tail(stdout, 40),
            "stderr_tail": tail(stderr, 40),
        })

    missing = [r["component"] for r in rows if not r["running"]]
    stderr_nonempty = []
    for r in rows:
        st = r["stderr_tail"]
        if st and st != "MISSING" and st.strip():
            stderr_nonempty.append(r["component"])

    if missing:
        status = "STARTUP_DIAGNOSIS_MISSING_COMPONENTS"
        restart_allowed = False
    elif stderr_nonempty:
        status = "STARTUP_DIAGNOSIS_RUNNING_WITH_STDERR_WARNINGS"
        restart_allowed = True
    else:
        status = "STARTUP_DIAGNOSIS_ALL_COMPONENTS_RUNNING"
        restart_allowed = True

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "run": str(RUN),
        "log_dir": str(LOG_DIR),
        "status": status,
        "restart_allowed": restart_allowed,
        "missing": missing,
        "stderr_nonempty_components": stderr_nonempty,
        "components": rows,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
    }

    state_path = out_dir / "master_startup_diagnoser_v1_state.json"
    report_path = out_dir / "master_startup_diagnoser_v1_report.md"
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    md = []
    md.append("# Edge Factory Master Startup Diagnoser v1")
    md.append("")
    md.append(f"Status: `{status}`")
    md.append(f"Restart allowed: `{restart_allowed}`")
    md.append(f"Missing: `{missing}`")
    md.append("")
    for r in rows:
        md.append(f"## {r['component']}")
        md.append(f"- running: `{r['running']}`")
        md.append(f"- process_count: `{r['process_count']}`")
        md.append(f"- pids: `{r['pids']}`")
        md.append("")
        md.append("### stderr tail")
        md.append("```text")
        md.append(r["stderr_tail"])
        md.append("```")
        md.append("")
        md.append("### stdout tail")
        md.append("```text")
        md.append(r["stdout_tail"])
        md.append("```")
        md.append("")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY MASTER STARTUP DIAGNOSER v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"run       : {RUN}")
    print(f"log_dir   : {LOG_DIR}")
    print(f"out_dir   : {out_dir}")
    print(f"status    : {status}")
    print(f"restart_allowed: {restart_allowed}")
    print(f"missing   : {missing}")
    print(f"stderr_nonempty_components: {stderr_nonempty}")
    print()
    print("COMPONENT SUMMARY")
    print("-" * 100)
    for r in rows:
        print(f"{r['component']}: running={r['running']} count={r['process_count']} pids={r['pids']}")
    print()
    print("STDERR TAILS")
    print("-" * 100)
    for r in rows:
        print(f"\n### {r['component']} stderr")
        print(r["stderr_tail"])
    print()
    print(f"State : {state_path}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
