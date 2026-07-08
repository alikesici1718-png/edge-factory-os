#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
MASTER = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"

def latest_dir(root: Path, prefix: str) -> Path | None:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    return sorted(ds, key=lambda p: p.stat().st_mtime, reverse=True)[0] if ds else None

def read_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_os_recovery_manifest_v2"
    out_dir.mkdir(parents=True, exist_ok=True)

    cc_dir = latest_dir(WORKSPACE / "edge_factory_os_command_center_v1", "os_command_center_v1_")
    inv_dir = latest_dir(WORKSPACE / "edge_factory_os_invariant_guard_v1", "os_invariant_guard_v1_")
    proc_dir = latest_dir(WORKSPACE / "edge_factory_os_process_watchdog_v1", "os_process_watchdog_v1_")
    cand_dir = latest_dir(WORKSPACE / "edge_factory_candidate_lifecycle_registry_v1", "candidate_lifecycle_registry_v1_")

    autopilot_v4_latest = WORKSPACE / "edge_factory_os_autopilot_loop_v4" / "edge_factory_os_autopilot_v4_latest_state.json"

    cc = read_json(cc_dir / "edge_factory_os_command_center_v1_state.json" if cc_dir else None)
    inv = read_json(inv_dir / "edge_factory_os_invariant_guard_v1_state.json" if inv_dir else None)
    proc = read_json(proc_dir / "edge_factory_os_process_watchdog_v1_state.json" if proc_dir else None)
    cand = read_json(cand_dir / "candidate_lifecycle_registry_v1_state.json" if cand_dir else None)
    auto = read_json(autopilot_v4_latest)

    auto_decision = auto.get("decision", {})

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": "Edge Factory OS / MASTER_UPPER_SYSTEM",
        "workspace": str(WORKSPACE),
        "master_base": str(MASTER),
        "current_autopilot": "v4",

        "current_state": {
            "command_center_status": cc.get("command_center_status"),
            "supervisor_status": cc.get("supervisor_status"),
            "autopilot_status": auto_decision.get("status"),
            "autopilot_severity": auto_decision.get("severity"),
            "invariant_status": inv.get("status"),
            "process_status": proc.get("status"),
            "open": auto_decision.get("open", cc.get("open")),
            "pending": auto_decision.get("pending", cc.get("pending")),
            "closed": auto_decision.get("closed", cc.get("closed")),
            "errors": auto_decision.get("errors", cc.get("errors")),
            "missing_processes": proc.get("missing_components"),
        },

        "candidate_lifecycle": cand.get("candidates", []),

        "critical_commands": {
            "start_master": 'powershell -ExecutionPolicy Bypass -File "C:\\Users\\alike\\start_edge_factory_MASTER_UPPER_SYSTEM.ps1"',
            "start_autopilot_v4": 'python -u "C:\\Users\\alike\\edge_factory_os_autopilot_loop_v4.py" --interval_seconds 300 --safe_execute',
            "command_center_once": 'python -u "C:\\Users\\alike\\edge_factory_os_command_center_v1.py"',
            "invariant_guard_once": 'python -u "C:\\Users\\alike\\edge_factory_os_invariant_guard_v1.py"',
            "process_watchdog_once": 'python -u "C:\\Users\\alike\\edge_factory_os_process_watchdog_v1.py"',
            "candidate_registry_once": 'python -u "C:\\Users\\alike\\edge_factory_candidate_lifecycle_registry_v1.py"',
            "health_check": 'python "C:\\Users\\alike\\edge_factory_live_health_check_v5.py" --base_dir "C:\\Users\\alike\\OneDrive\\Desktop\\edge_lab_new\\paper_run_gate_MASTER_UPPER_SYSTEM"',
            "performance_check": 'python "C:\\Users\\alike\\edge_factory_live_performance_analyzer_v3.py" --base_dir "C:\\Users\\alike\\OneDrive\\Desktop\\edge_lab_new\\paper_run_gate_MASTER_UPPER_SYSTEM"',
        },

        "do_not_do_now": [
            "Do not add new strategy families before initial closed sample.",
            "Do not run drift decision before closed >= 20.",
            "Do not run capital review/change before closed >= 50.",
            "Do not promote rel_extreme; it is ARCHIVE_WAIT due to duplicate/stale shadow signals and no closed sample.",
            "Do not enable live trading.",
            "Do not add exchange API keys.",
            "Do not place real orders.",
        ],

        "next_thresholds": {
            "closed_20": "Autopilot v4 may run drift monitor/planner read-only.",
            "closed_50": "Autopilot v4 may run capital governor review read-only.",
            "errors_gt_0": "Autopilot v4 reports ATTENTION; inspect errors before anything else.",
            "process_watchdog_not_pass": "Inspect missing process; restart only the missing component if needed.",
            "invariant_not_pass": "Do not run optional actions; inspect invariant guard report.",
        },

        "safety": {
            "active_paper_allowed": False,
            "live_allowed": False,
            "capital_change_allowed": False,
            "real_orders": False,
            "api_keys_required": False,
        },
    }

    manifest_path = out_dir / "edge_factory_os_recovery_manifest_latest.json"
    manifest_md = out_dir / "edge_factory_os_recovery_manifest_latest.md"

    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    md = []
    md.append("# Edge Factory OS Recovery Manifest v2")
    md.append("")
    md.append(f"Generated: `{manifest['generated_at']}`")
    md.append(f"Current autopilot: `{manifest['current_autopilot']}`")
    md.append("")
    md.append("## Current state")
    for k, v in manifest["current_state"].items():
        md.append(f"- `{k}`: `{v}`")
    md.append("")
    md.append("## Start / check commands")
    for k, v in manifest["critical_commands"].items():
        md.append(f"### {k}")
        md.append("```powershell")
        md.append(v)
        md.append("```")
    md.append("")
    md.append("## Do not do now")
    for x in manifest["do_not_do_now"]:
        md.append(f"- {x}")
    md.append("")
    md.append("## Thresholds")
    for k, v in manifest["next_thresholds"].items():
        md.append(f"- `{k}`: {v}")
    md.append("")

    manifest_md.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS RECOVERY MANIFEST v2")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"master    : {MASTER}")
    print(f"manifest  : {manifest_path}")
    print(f"markdown  : {manifest_md}")
    print()
    print("CURRENT STATE")
    print("-" * 100)
    for k, v in manifest["current_state"].items():
        print(f"{k}: {v}")
    print()
    print("PRIMARY RECOVERY COMMAND")
    print("-" * 100)
    print(manifest["critical_commands"]["start_autopilot_v4"])
    print()
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("capital_change_allowed: False")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
