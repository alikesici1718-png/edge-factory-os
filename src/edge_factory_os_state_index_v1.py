#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Aggregates state from all major Edge Factory OS components (command center, autopilot v4, invariant guard, process watchdog, candidate registry, and others) into a single indexed summary. Outputs a consolidated state index JSON to the edge_factory_os_state_index_v1 directory.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_os_state_index_v1"

COMPONENTS = [
    {
        "component": "command_center",
        "root": "edge_factory_os_command_center_v1",
        "prefix": "os_command_center_v1_",
        "state_file": "edge_factory_os_command_center_v1_state.json",
        "status_keys": ["command_center_status", "supervisor_status"],
    },
    {
        "component": "autopilot_v4",
        "root": "edge_factory_os_autopilot_loop_v4",
        "prefix": "",
        "state_file": "edge_factory_os_autopilot_v4_latest_state.json",
        "direct_file": True,
        "status_keys": ["decision.severity", "decision.status", "decision.invariant_status", "decision.process_status"],
    },
    {
        "component": "recovery_manifest_v2",
        "root": "edge_factory_os_recovery_manifest_v2",
        "prefix": "",
        "state_file": "edge_factory_os_recovery_manifest_latest.json",
        "direct_file": True,
        "status_keys": ["current_state.autopilot_status", "current_state.invariant_status", "current_state.process_status"],
    },
    {
        "component": "invariant_guard",
        "root": "edge_factory_os_invariant_guard_v1",
        "prefix": "os_invariant_guard_v1_",
        "state_file": "edge_factory_os_invariant_guard_v1_state.json",
        "status_keys": ["status"],
    },
    {
        "component": "process_watchdog",
        "root": "edge_factory_os_process_watchdog_v1",
        "prefix": "os_process_watchdog_v1_",
        "state_file": "edge_factory_os_process_watchdog_v1_state.json",
        "status_keys": ["status", "severity"],
    },
    {
        "component": "duplicate_launch_guard",
        "root": "edge_factory_os_duplicate_launch_guard_v1",
        "prefix": "duplicate_launch_guard_v1_",
        "state_file": "edge_factory_os_duplicate_launch_guard_v1_state.json",
        "status_keys": ["status"],
    },
    {
        "component": "candidate_lifecycle_registry",
        "root": "edge_factory_candidate_lifecycle_registry_v1",
        "prefix": "candidate_lifecycle_registry_v1_",
        "state_file": "candidate_lifecycle_registry_v1_state.json",
        "status_keys": ["registry_status"],
    },
    {
        "component": "research_brain",
        "root": "edge_factory_os_research_brain_v1",
        "prefix": "research_brain_v1_",
        "state_file": "edge_factory_os_research_brain_v1_state.json",
        "status_keys": ["research_brain_status"],
    },
    {
        "component": "offline_contract_schema",
        "root": "edge_factory_offline_experiment_contract_schema_v1",
        "prefix": "offline_experiment_contract_schema_v1_",
        "state_file": "offline_experiment_contract_schema_v1_state.json",
        "status_keys": ["status"],
    },
    {
        "component": "offline_contract_validator",
        "root": "edge_factory_offline_experiment_contract_validator_v1",
        "prefix": "contract_validator_v1_",
        "state_file": "offline_experiment_contract_validator_v1_state.json",
        "status_keys": ["validation_status"],
    },
    {
        "component": "offline_experiment_queue",
        "root": "edge_factory_offline_experiment_queue_v1",
        "prefix": "offline_experiment_queue_v1_",
        "state_file": "offline_experiment_queue_v1_state.json",
        "status_keys": ["queue_status"],
    },
    {
        "component": "os_interface_specs",
        "root": "edge_factory_os_interface_specs_v1",
        "prefix": "os_interface_specs_v1_",
        "state_file": "os_interface_specs_v1_state.json",
        "status_keys": ["status"],
    },
    {
        "component": "contract_to_runner_adapter",
        "root": "edge_factory_contract_to_runner_adapter_v1",
        "prefix": "contract_to_runner_adapter_v1_",
        "state_file": "contract_to_runner_adapter_v1_state.json",
        "status_keys": ["adapter_status"],
    },
    {
        "component": "result_to_lifecycle_adapter",
        "root": "edge_factory_result_to_lifecycle_adapter_v1",
        "prefix": "result_to_lifecycle_adapter_v1_",
        "state_file": "result_to_lifecycle_adapter_v1_state.json",
        "status_keys": ["adapter_status", "decision", "new_status"],
    },
]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def latest_dir(root: Path, prefix: str) -> Path | None:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    if not ds:
        return None
    return sorted(ds, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def read_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e)}

def dotted_get(obj: dict[str, Any], dotted: str, default=None):
    cur: Any = obj
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur

def component_state_path(c: dict[str, Any]) -> tuple[Path | None, Path | None]:
    root = WORKSPACE / c["root"]

    if c.get("direct_file"):
        path = root / c["state_file"]
        return root if root.exists() else None, path if path.exists() else None

    d = latest_dir(root, c["prefix"])
    if not d:
        return None, None

    path = d / c["state_file"]
    return d, path if path.exists() else None

def classify_component(component: str, state: dict[str, Any], exists: bool) -> tuple[str, str]:
    if not exists:
        return "MISSING", "ATTENTION"

    if "__read_error__" in state:
        return "READ_ERROR", "ATTENTION"

    # Explicit good statuses.
    vals = json.dumps(state, ensure_ascii=False)

    bad_markers = [
        "CRITICAL_FAIL",
        "CRITICAL",
        "ERRORS_PRESENT",
        "FAILED_TO_RUN",
    ]

    attention_markers = [
        "ATTENTION",
        "BLOCKED",
        "ARCHIVE_WAIT",
        "NO_RUNNER_REQUEST",
        "TEMPLATE_STRUCTURE_VALID_NOT_A_CANDIDATE",
    ]

    # Some blocked statuses are expected, not bad, for current stage.
    expected_blocked_components = {
        "offline_contract_validator",
        "contract_to_runner_adapter",
        "result_to_lifecycle_adapter",
        "candidate_lifecycle_registry",
        "offline_experiment_queue",
    }

    if any(x in vals for x in bad_markers):
        return "CHECK", "ATTENTION"

    if any(x in vals for x in attention_markers):
        if component in expected_blocked_components:
            return "EXPECTED_BLOCKED_OR_ARCHIVED", "OK"
        return "ATTENTION_STATE", "ATTENTION"

    return "OK", "OK"

def main() -> int:
    out_dir = OUT_ROOT / f"os_state_index_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    full_index: dict[str, Any] = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "index_status": "OS_STATE_INDEX_READY",
        "components": {},
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "State index only.",
            "Does not start or stop processes.",
            "Does not modify MASTER_UPPER_SYSTEM.",
            "Does not run experiments.",
            "Does not promote candidates.",
            "Does not place orders.",
        ],
    }

    for c in COMPONENTS:
        comp = c["component"]
        latest, state_path = component_state_path(c)
        state = read_json(state_path)
        exists = state_path is not None and state_path.exists()

        status_values = {}
        for key in c.get("status_keys", []):
            status_values[key] = dotted_get(state, key)

        health, severity = classify_component(comp, state, exists)

        mtime = None
        age_min = None
        if exists:
            mtime = datetime.fromtimestamp(state_path.stat().st_mtime, tz=timezone.utc).isoformat()
            age_min = round((datetime.now(timezone.utc).timestamp() - state_path.stat().st_mtime) / 60.0, 2)

        row = {
            "component": comp,
            "health": health,
            "severity": severity,
            "state_exists": exists,
            "latest_dir": str(latest) if latest else "",
            "state_path": str(state_path) if state_path else "",
            "state_mtime_utc": mtime,
            "state_age_min": age_min,
            "status_values": json.dumps(status_values, ensure_ascii=False),
        }
        rows.append(row)

        full_index["components"][comp] = {
            "latest_dir": row["latest_dir"],
            "state_path": row["state_path"],
            "health": health,
            "severity": severity,
            "state_mtime_utc": mtime,
            "state_age_min": age_min,
            "status_values": status_values,
        }

    critical_missing = [r for r in rows if r["severity"] == "ATTENTION" and r["component"] in {
        "command_center",
        "autopilot_v4",
        "recovery_manifest_v2",
        "invariant_guard",
        "process_watchdog",
    }]

    attention_count = sum(1 for r in rows if r["severity"] == "ATTENTION")

    if critical_missing:
        index_health = "OS_STATE_INDEX_ATTENTION_CORE_COMPONENT"
    elif attention_count:
        index_health = "OS_STATE_INDEX_ATTENTION_NON_CORE"
    else:
        index_health = "OS_STATE_INDEX_PASS"

    full_index["index_health"] = index_health
    full_index["attention_count"] = attention_count
    full_index["core_attention_components"] = [r["component"] for r in critical_missing]

    state_path = out_dir / "edge_factory_os_state_index_v1_state.json"
    csv_path = out_dir / "edge_factory_os_state_index_v1.csv"
    report_path = out_dir / "edge_factory_os_state_index_v1_report.md"
    latest_copy = OUT_ROOT / "edge_factory_os_state_index_latest.json"

    state_path.write_text(json.dumps(full_index, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_copy.write_text(json.dumps(full_index, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    pd.DataFrame(rows).to_csv(csv_path, index=False)

    md = []
    md.append("# Edge Factory OS State Index v1")
    md.append("")
    md.append(f"Index health: `{index_health}`")
    md.append(f"Attention count: `{attention_count}`")
    md.append("")
    md.append("## Components")
    for r in rows:
        md.append(f"- `{r['component']}` — `{r['health']}` / `{r['severity']}`")
        md.append(f"  - state: `{r['state_path']}`")
        md.append(f"  - status: `{r['status_values']}`")
    md.append("")
    md.append("## Safety")
    md.append("- live_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS STATE INDEX v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"index_health: {index_health}")
    print(f"attention_count: {attention_count}")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("COMPONENT INDEX")
    print("-" * 100)
    df = pd.DataFrame(rows)
    print(df[["component","health","severity","state_exists","state_age_min","status_values"]].to_string(index=False))
    print()
    print(f"State : {state_path}")
    print(f"Latest: {latest_copy}")
    print(f"CSV   : {csv_path}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
