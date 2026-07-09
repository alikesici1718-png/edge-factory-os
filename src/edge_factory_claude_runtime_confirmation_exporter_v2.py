"""
Generates a single-file runtime confirmation packet for the Edge Factory MASTER_UPPER_SYSTEM by collecting live paper run logs, gate decisions, risk snapshots, and process status outputs. Reads the paper run directory and runs diagnostic subprocess commands, then writes a consolidated Markdown confirmation file for Claude review.
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
RUN = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"
OUTDIR = WORKSPACE / "edge_factory_claude_runtime_confirmation"
OUT = OUTDIR / "CLAUDE_RUNTIME_CONFIRMATION_SINGLE_FILE_v2.md"

OUTDIR.mkdir(parents=True, exist_ok=True)

def run_cmd(cmd: list[str], timeout: int = 180) -> str:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (
            f"$ {' '.join(cmd)}\n"
            f"returncode={p.returncode}\n\n"
            f"STDOUT:\n{p.stdout}\n\n"
            f"STDERR:\n{p.stderr}\n"
        )
    except Exception as e:
        return f"$ {' '.join(cmd)}\nEXCEPTION: {e!r}\n"

def read_tail(path: Path, n: int = 120) -> str:
    if not path.exists():
        return f"MISSING: {path}"
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[-n:])
    except Exception as e:
        return f"READ_ERROR {path}: {e!r}"

def read_all(path: Path) -> str:
    if not path.exists():
        return f"MISSING: {path}"
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"READ_ERROR {path}: {e!r}"

def latest_file(root: Path, pattern: str) -> Path | None:
    if not root.exists():
        return None
    files = list(root.rglob(pattern))
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def section(title: str, body: str) -> str:
    return f"\n\n---\n# {title}\n---\n\n```text\n{body}\n```\n"

prompt = """Claude, this is a single-file runtime confirmation packet for my Edge Factory OS / MASTER_UPPER_SYSTEM.

Please do NOT praise it. I want a hostile verification of the final runtime state.

Question:
Can I safely leave the system alone now and let it collect paper sample, or is there still a blocker?

Current expected interpretation:
- MASTER should be running under v5 supervised launcher.
- Process watchdog should pass.
- Health check should be OK.
- Existing 6 errors should be acknowledged network/exchange fetch warnings only.
- No logic/safety/unknown errors should be present.
- Command Center v1 may still say ATTENTION_REQUIRED_ERRORS_PRESENT because it does not read the acknowledger.
- Command Center v2 Overlay is the authority for runtime interpretation.
- active_paper_allowed=false
- live_allowed=false
- capital_change_allowed=false
- real orders=false
- next_action should be KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH

Please verify:
1. Is v2 overlay interpretation correct?
2. Are acknowledged network warnings safe to not block runtime?
3. Is there any sign of live/order/capital risk?
4. Is there any reason to restart, patch, or touch the running system now?
5. Should the current decision be DO_NOT_TOUCH / collect sample?
6. What remaining monitoring thresholds matter? closed>=20 drift, closed>=50 capital governor.

Give final answer as:
- Verdict: OK_TO_LEAVE_RUNNING or NOT_OK
- Blockers:
- Warnings:
- Do not touch / next action:
"""

summary = """Expected final state:

overlay_status = RUNTIME_HEALTHY_WITH_ACKNOWLEDGED_NETWORK_WARNINGS
severity = OK_ACKNOWLEDGED_WARNINGS
runtime_ok = True
next_action = KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH

Process watchdog should pass with all components running:
- risk_manager
- old_short_logger
- impulse_long_logger
- market_relative_logger
- weak_market_logger
- autopilot_v4

Health check should pass:
- old_short heartbeat OK
- impulse_long heartbeat OK
- market_relative_short heartbeat OK
- weak_market_short heartbeat OK

Errors:
- total_errors = 6
- all classified as NETWORK_OR_EXCHANGE_FETCH_WARNING
- logic_or_safety_error_count = 0
- unknown_error_count = 0
- acknowledged = True
- errors.csv was NOT deleted

Safety:
- active_paper_allowed = False
- live_allowed = False
- capital_change_allowed = False
- real orders = NO

Current intended action:
KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH
"""

parts: list[str] = []
parts.append("# CLAUDE RUNTIME CONFIRMATION SINGLE FILE v2\n")
parts.append(f"Generated: {datetime.now().isoformat()}\n\n")
parts.append(prompt)
parts.append(section("MY CURRENT SUMMARY", summary))

parts.append(section(
    "PROCESS WATCHDOG FRESH OUTPUT",
    run_cmd(["python", "-u", r"C:\Users\alike\edge_factory_os_process_watchdog_v1.py"])
))

parts.append(section(
    "HEALTH CHECK FRESH OUTPUT",
    run_cmd([
        "python",
        r"C:\Users\alike\edge_factory_live_health_check_v5.py",
        "--base_dir",
        str(RUN),
    ])
))

parts.append(section(
    "COMMAND CENTER V2 OVERLAY FRESH OUTPUT",
    run_cmd(["python", "-u", r"C:\Users\alike\edge_factory_os_command_center_v2_overlay.py"])
))

ps_snapshot = r"""
Get-CimInstance Win32_Process |
Where-Object {
    $_.Name -match 'python|powershell' -and
    $_.CommandLine -match 'startup_runners_v5|global_paper_risk|gate_aware|market_relative|weak_market|autopilot_loop_v4'
} |
Select-Object ProcessId, Name, CommandLine |
Format-List
"""
parts.append(section(
    "PROCESS SNAPSHOT FRESH OUTPUT",
    run_cmd(["powershell", "-NoProfile", "-Command", ps_snapshot])
))

overlay_latest = WORKSPACE / "edge_factory_os_command_center_v2_overlay" / "os_command_center_v2_overlay_latest.json"
ack_latest = WORKSPACE / "edge_factory_error_acknowledger_v1" / "error_acknowledger_latest.json"
classifier_latest = latest_file(WORKSPACE / "edge_factory_error_classifier_v1", "error_classifier_v1_state.json")
watchdog_latest = latest_file(WORKSPACE / "edge_factory_os_process_watchdog_v1", "edge_factory_os_process_watchdog_v1_state.json")

parts.append(section("COMMAND CENTER V2 OVERLAY LATEST JSON", read_all(overlay_latest)))
parts.append(section("ERROR ACKNOWLEDGER LATEST JSON", read_all(ack_latest)))

if classifier_latest:
    parts.append(section("LATEST ERROR CLASSIFIER STATE JSON", read_all(classifier_latest)))
else:
    parts.append(section("LATEST ERROR CLASSIFIER STATE JSON", "MISSING"))

if watchdog_latest:
    parts.append(section("LATEST PROCESS WATCHDOG STATE JSON", read_all(watchdog_latest)))
else:
    parts.append(section("LATEST PROCESS WATCHDOG STATE JSON", "MISSING"))

log_dir = RUN / "startup_logs_v5_supervised"
if log_dir.exists():
    exit_lines = []
    for p in sorted(log_dir.glob("*.combined.log")):
        txt = read_all(p)
        for line in txt.splitlines():
            if "SUPERVISOR START" in line or "PROCESS EXITED" in line or "EXCEPTION" in line:
                exit_lines.append(f"{p.name}: {line}")
    parts.append(section("V5 SUPERVISED LOG EXIT/EXCEPTION SUMMARY", "\n".join(exit_lines[-160:])))
else:
    parts.append(section("V5 SUPERVISED LOG EXIT/EXCEPTION SUMMARY", f"MISSING: {log_dir}"))

for name in [
    "risk_manager",
    "old_short_logger",
    "impulse_long_logger",
    "market_relative_logger",
    "weak_market_logger",
    "autopilot_v4",
]:
    parts.append(section(f"{name} v5 log tail", read_tail(log_dir / f"{name}.combined.log", 120)))

OUT.write_text("\n".join(parts), encoding="utf-8")

print("CLAUDE RUNTIME CONFIRMATION v2 CREATED")
print("=" * 100)
print(OUT)
print(f"size_bytes={OUT.stat().st_size}")
