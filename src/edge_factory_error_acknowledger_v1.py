#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_error_acknowledger_v1"

def latest_file(root: Path, pattern: str) -> Path | None:
    files = list(root.rglob(pattern)) if root.exists() else []
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def read_json(path: Path | None) -> dict:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e)}

def main():
    out_dir = OUT_ROOT / f"error_acknowledger_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    classifier_state_path = latest_file(
        WORKSPACE / "edge_factory_error_classifier_v1",
        "error_classifier_v1_state.json"
    )
    classifier = read_json(classifier_state_path)

    blockers = []
    if not classifier:
        blockers.append("ERROR_CLASSIFIER_STATE_NOT_FOUND")
    if classifier.get("severity") not in {"WARNING", "OK"}:
        blockers.append(f"CLASSIFIER_SEVERITY_NOT_ACKNOWLEDGEABLE:{classifier.get('severity')}")
    if classifier.get("logic_or_safety_error_count", 0) != 0:
        blockers.append("LOGIC_OR_SAFETY_ERRORS_PRESENT")
    if classifier.get("unknown_error_count", 0) != 0:
        blockers.append("UNKNOWN_ERRORS_PRESENT")
    if classifier.get("acknowledge_network_warnings_allowed") is not True:
        blockers.append("ACKNOWLEDGE_NOT_ALLOWED_BY_CLASSIFIER")

    if blockers:
        status = "ERROR_ACKNOWLEDGER_BLOCKED"
        os_error_severity = "ATTENTION"
        command_center_overlay_status = "KEEP_ATTENTION_ERRORS_PRESENT"
        acknowledged = False
    else:
        status = "ERROR_ACKNOWLEDGER_NETWORK_WARNINGS_ACKNOWLEDGED"
        os_error_severity = "ACKNOWLEDGED_WARNING"
        command_center_overlay_status = "RUNTIME_HEALTHY_WITH_ACKNOWLEDGED_NETWORK_WARNINGS"
        acknowledged = True

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "status": status,
        "acknowledged": acknowledged,
        "classifier_state_path": str(classifier_state_path) if classifier_state_path else "",
        "blockers": blockers,
        "total_errors": classifier.get("total_errors"),
        "network_warning_count": classifier.get("network_warning_count"),
        "logic_or_safety_error_count": classifier.get("logic_or_safety_error_count"),
        "unknown_error_count": classifier.get("unknown_error_count"),
        "os_error_severity": os_error_severity,
        "command_center_overlay_status": command_center_overlay_status,
        "notes": [
            "Does not delete errors.csv.",
            "Does not modify family logs.",
            "Only creates an acknowledgement artifact for OS-level interpretation.",
            "Future new logic/safety/unknown errors must still trigger attention.",
            "Network/exchange fetch warnings are acknowledged as non-logic blockers."
        ],
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False
    }

    state_path = out_dir / "error_acknowledger_v1_state.json"
    latest_path = OUT_ROOT / "error_acknowledger_latest.json"
    report_path = out_dir / "error_acknowledger_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    md = []
    md.append("# Edge Factory Error Acknowledger v1")
    md.append("")
    md.append(f"Status: `{status}`")
    md.append(f"Acknowledged: `{acknowledged}`")
    md.append(f"Command center overlay: `{command_center_overlay_status}`")
    md.append("")
    md.append("## Counts")
    md.append(f"- total_errors: `{state['total_errors']}`")
    md.append(f"- network_warning_count: `{state['network_warning_count']}`")
    md.append(f"- logic_or_safety_error_count: `{state['logic_or_safety_error_count']}`")
    md.append(f"- unknown_error_count: `{state['unknown_error_count']}`")
    md.append("")
    md.append("## Safety")
    md.append("- Does not delete errors.csv.")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY ERROR ACKNOWLEDGER v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"out_dir   : {out_dir}")
    print(f"status    : {status}")
    print(f"acknowledged: {acknowledged}")
    print(f"command_center_overlay_status: {command_center_overlay_status}")
    print(f"total_errors: {state['total_errors']}")
    print(f"network_warning_count: {state['network_warning_count']}")
    print(f"logic_or_safety_error_count: {state['logic_or_safety_error_count']}")
    print(f"unknown_error_count: {state['unknown_error_count']}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("BLOCKERS")
    print("-" * 100)
    print("\n".join(f"- {b}" for b in blockers) if blockers else "NONE")
    print()
    print(f"State : {state_path}")
    print(f"Latest: {latest_path}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
