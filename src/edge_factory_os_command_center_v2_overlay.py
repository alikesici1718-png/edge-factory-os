#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OS command center overlay (v2) that reads the latest outputs from various OS submodules and the MASTER_UPPER_SYSTEM run directory to produce a consolidated read-only state snapshot, writing timestamped JSON/Markdown reports to edge_factory_os_command_center_v2_overlay/ in the workspace.
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
RUN = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"
OUT_ROOT = WORKSPACE / "edge_factory_os_command_center_v2_overlay"

def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e)}

def latest_file(root: Path, pattern: str) -> Path | None:
    files = list(root.rglob(pattern)) if root.exists() else []
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def run_cmd(args: list[str]) -> dict:
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=120)
        return {
            "ok": p.returncode == 0,
            "returncode": p.returncode,
            "stdout": p.stdout,
            "stderr": p.stderr,
        }
    except Exception as e:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": repr(e),
        }

def main():
    out_dir = OUT_ROOT / f"os_command_center_v2_overlay_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    health = run_cmd([
        "python",
        "C:\\Users\\alike\\edge_factory_live_health_check_v5.py",
        "--base_dir",
        str(RUN),
    ])

    watchdog = run_cmd([
        "python",
        "-u",
        "C:\\Users\\alike\\edge_factory_os_process_watchdog_v1.py",
    ])

    command_center = run_cmd([
        "python",
        "-u",
        "C:\\Users\\alike\\edge_factory_os_command_center_v1.py",
    ])

    invariant = run_cmd([
        "python",
        "-u",
        "C:\\Users\\alike\\edge_factory_os_invariant_guard_v1.py",
    ])

    ack_path = WORKSPACE / "edge_factory_error_acknowledger_v1" / "error_acknowledger_latest.json"
    ack = read_json(ack_path)

    classifier_path = latest_file(WORKSPACE / "edge_factory_error_classifier_v1", "error_classifier_v1_state.json")
    classifier = read_json(classifier_path) if classifier_path else {}

    process_pass = "PROCESS_WATCHDOG_PASS" in watchdog["stdout"]
    health_ok = "OK: gate-aware paper system looks healthy" in health["stdout"]
    command_center_attention_errors = "ATTENTION_REQUIRED_ERRORS_PRESENT" in command_center["stdout"]

    errors_acknowledged = (
        ack.get("acknowledged") is True
        and ack.get("logic_or_safety_error_count", 0) == 0
        and ack.get("unknown_error_count", 0) == 0
        and ack.get("command_center_overlay_status") == "RUNTIME_HEALTHY_WITH_ACKNOWLEDGED_NETWORK_WARNINGS"
    )

    if process_pass and health_ok and command_center_attention_errors and errors_acknowledged:
        overlay_status = "RUNTIME_HEALTHY_WITH_ACKNOWLEDGED_NETWORK_WARNINGS"
        severity = "OK_ACKNOWLEDGED_WARNINGS"
        next_action = "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH"
        runtime_ok = True
    elif process_pass and health_ok and not command_center_attention_errors:
        overlay_status = "RUNTIME_HEALTHY"
        severity = "OK"
        next_action = "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH"
        runtime_ok = True
    elif not process_pass:
        overlay_status = "RUNTIME_ATTENTION_PROCESS_WATCHDOG_NOT_PASS"
        severity = "ATTENTION"
        next_action = "INSPECT_PROCESS_WATCHDOG"
        runtime_ok = False
    elif not health_ok:
        overlay_status = "RUNTIME_ATTENTION_HEALTH_NOT_OK"
        severity = "ATTENTION"
        next_action = "INSPECT_HEALTH"
        runtime_ok = False
    else:
        overlay_status = "RUNTIME_ATTENTION_REVIEW_REQUIRED"
        severity = "ATTENTION"
        next_action = "REVIEW_COMMAND_CENTER_AND_ACKNOWLEDGER"
        runtime_ok = False

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "master": str(RUN),
        "overlay_status": overlay_status,
        "severity": severity,
        "runtime_ok": runtime_ok,
        "next_action": next_action,
        "process_watchdog_pass": process_pass,
        "health_ok": health_ok,
        "command_center_attention_errors": command_center_attention_errors,
        "errors_acknowledged": errors_acknowledged,
        "acknowledger_path": str(ack_path),
        "classifier_path": str(classifier_path) if classifier_path else "",
        "acknowledger": ack,
        "classifier": classifier,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "notes": [
            "This overlay does not delete errors.csv.",
            "It does not modify command_center_v1.",
            "It only interprets acknowledged network warnings as non-blocking when process watchdog and health pass.",
            "Any logic/safety/unknown error should remain blocking.",
        ],
    }

    state_path = out_dir / "os_command_center_v2_overlay_state.json"
    latest_path = OUT_ROOT / "os_command_center_v2_overlay_latest.json"
    report_path = out_dir / "os_command_center_v2_overlay_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    report = []
    report.append("# Edge Factory OS Command Center v2 Overlay")
    report.append("")
    report.append(f"Overlay status: `{overlay_status}`")
    report.append(f"Severity: `{severity}`")
    report.append(f"Runtime OK: `{runtime_ok}`")
    report.append(f"Next action: `{next_action}`")
    report.append("")
    report.append("## Checks")
    report.append(f"- process_watchdog_pass: `{process_pass}`")
    report.append(f"- health_ok: `{health_ok}`")
    report.append(f"- command_center_attention_errors: `{command_center_attention_errors}`")
    report.append(f"- errors_acknowledged: `{errors_acknowledged}`")
    report.append("")
    report.append("## Safety")
    report.append("- active_paper_allowed: `False`")
    report.append("- live_allowed: `False`")
    report.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS COMMAND CENTER v2 OVERLAY")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"master    : {RUN}")
    print(f"out_dir   : {out_dir}")
    print(f"overlay_status: {overlay_status}")
    print(f"severity      : {severity}")
    print(f"runtime_ok    : {runtime_ok}")
    print(f"next_action   : {next_action}")
    print(f"process_watchdog_pass: {process_pass}")
    print(f"health_ok: {health_ok}")
    print(f"command_center_attention_errors: {command_center_attention_errors}")
    print(f"errors_acknowledged: {errors_acknowledged}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("INTERPRETATION")
    print("-" * 100)
    if overlay_status == "RUNTIME_HEALTHY_WITH_ACKNOWLEDGED_NETWORK_WARNINGS":
        print("MASTER is running healthy. Existing errors are acknowledged network/exchange fetch warnings, not logic/safety blockers.")
    elif runtime_ok:
        print("MASTER is running healthy.")
    else:
        print("Runtime needs review.")
    print()
    print(f"State : {state_path}")
    print(f"Latest: {latest_path}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
