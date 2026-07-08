#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_os_state_index_v2"

COMPONENTS = [
    {
        "component": "command_center",
        "root": "edge_factory_os_command_center_v1",
        "prefix": "os_command_center_v1_",
        "state_file": "edge_factory_os_command_center_v1_state.json",
        "direct_file": False,
    },
    {
        "component": "autopilot_v4",
        "root": "edge_factory_os_autopilot_loop_v4",
        "state_file": "edge_factory_os_autopilot_v4_latest_state.json",
        "direct_file": True,
    },
    {
        "component": "recovery_manifest_v2",
        "root": "edge_factory_os_recovery_manifest_v2",
        "state_file": "edge_factory_os_recovery_manifest_latest.json",
        "direct_file": True,
    },
    {
        "component": "invariant_guard",
        "root": "edge_factory_os_invariant_guard_v1",
        "prefix": "os_invariant_guard_v1_",
        "state_file": "edge_factory_os_invariant_guard_v1_state.json",
        "direct_file": False,
    },
    {
        "component": "process_watchdog",
        "root": "edge_factory_os_process_watchdog_v1",
        "prefix": "os_process_watchdog_v1_",
        "state_file": "edge_factory_os_process_watchdog_v1_state.json",
        "direct_file": False,
    },
    {
        "component": "duplicate_launch_guard",
        "root": "edge_factory_os_duplicate_launch_guard_v1",
        "prefix": "duplicate_launch_guard_v1_",
        "state_file": "edge_factory_os_duplicate_launch_guard_v1_state.json",
        "direct_file": False,
    },
    {
        "component": "candidate_lifecycle_registry",
        "root": "edge_factory_candidate_lifecycle_registry_v1",
        "prefix": "candidate_lifecycle_registry_v1_",
        "state_file": "candidate_lifecycle_registry_v1_state.json",
        "direct_file": False,
    },
    {
        "component": "research_brain",
        "root": "edge_factory_os_research_brain_v1",
        "prefix": "research_brain_v1_",
        "state_file": "edge_factory_os_research_brain_v1_state.json",
        "direct_file": False,
    },
    {
        "component": "offline_contract_schema",
        "root": "edge_factory_offline_experiment_contract_schema_v1",
        "prefix": "offline_experiment_contract_schema_v1_",
        "state_file": "offline_experiment_contract_schema_v1_state.json",
        "direct_file": False,
    },
    {
        "component": "offline_contract_validator",
        "root": "edge_factory_offline_experiment_contract_validator_v1",
        "prefix": "contract_validator_v1_",
        "state_file": "offline_experiment_contract_validator_v1_state.json",
        "direct_file": False,
    },
    {
        "component": "offline_experiment_queue",
        "root": "edge_factory_offline_experiment_queue_v1",
        "prefix": "offline_experiment_queue_v1_",
        "state_file": "offline_experiment_queue_v1_state.json",
        "direct_file": False,
    },
    {
        "component": "os_interface_specs",
        "root": "edge_factory_os_interface_specs_v1",
        "prefix": "os_interface_specs_v1_",
        "state_file": "os_interface_specs_v1_state.json",
        "direct_file": False,
    },
    {
        "component": "contract_to_runner_adapter",
        "root": "edge_factory_contract_to_runner_adapter_v1",
        "prefix": "contract_to_runner_adapter_v1_",
        "state_file": "contract_to_runner_adapter_v1_state.json",
        "direct_file": False,
    },
    {
        "component": "result_to_lifecycle_adapter",
        "root": "edge_factory_result_to_lifecycle_adapter_v1",
        "prefix": "result_to_lifecycle_adapter_v1_",
        "state_file": "result_to_lifecycle_adapter_v1_state.json",
        "direct_file": False,
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

    d = latest_dir(root, c.get("prefix", ""))
    if not d:
        return None, None

    path = d / c["state_file"]
    return d, path if path.exists() else None

def classify(component: str, state: dict[str, Any], exists: bool) -> tuple[str, str, dict[str, Any]]:
    if not exists:
        return "MISSING", "ATTENTION", {}

    if "__read_error__" in state:
        return "READ_ERROR", "ATTENTION", {"read_error": state["__read_error__"]}

    status_values = {}

    if component == "command_center":
        status_values = {
            "command_center_status": state.get("command_center_status"),
            "supervisor_status": state.get("supervisor_status"),
            "open": state.get("open"),
            "pending": state.get("pending"),
            "closed": state.get("closed"),
            "errors": state.get("errors"),
        }
        if state.get("errors", 0):
            return "ERRORS_PRESENT", "ATTENTION", status_values
        if state.get("command_center_status") == "RUNNING_COLLECTING_SAMPLE_DO_NOT_TOUCH":
            return "OK", "OK", status_values
        return "CHECK", "ATTENTION", status_values

    if component == "autopilot_v4":
        d = state.get("decision", {})
        status_values = {
            "severity": d.get("severity"),
            "status": d.get("status"),
            "invariant_status": d.get("invariant_status"),
            "process_status": d.get("process_status"),
            "open": d.get("open"),
            "pending": d.get("pending"),
            "closed": d.get("closed"),
            "errors": d.get("errors"),
        }
        if d.get("severity") == "OK" and d.get("invariant_status") == "INVARIANT_GUARD_PASS" and d.get("process_status") == "PROCESS_WATCHDOG_PASS":
            return "OK", "OK", status_values
        return "CHECK", "ATTENTION", status_values

    if component == "recovery_manifest_v2":
        cs = state.get("current_state", {})
        status_values = {
            "autopilot_status": cs.get("autopilot_status"),
            "autopilot_severity": cs.get("autopilot_severity"),
            "invariant_status": cs.get("invariant_status"),
            "process_status": cs.get("process_status"),
            "open": cs.get("open"),
            "pending": cs.get("pending"),
            "closed": cs.get("closed"),
            "errors": cs.get("errors"),
        }
        if cs.get("autopilot_severity") == "OK" and cs.get("invariant_status") == "INVARIANT_GUARD_PASS" and cs.get("process_status") == "PROCESS_WATCHDOG_PASS":
            return "OK", "OK", status_values
        return "CHECK", "ATTENTION", status_values

    if component == "invariant_guard":
        status_values = {
            "status": state.get("status"),
            "critical_failed_count": state.get("critical_failed_count"),
            "attention_failed_count": state.get("attention_failed_count"),
        }
        if state.get("status") == "INVARIANT_GUARD_PASS":
            return "OK", "OK", status_values
        return "CHECK", "ATTENTION", status_values

    if component == "process_watchdog":
        status_values = {
            "status": state.get("status"),
            "severity": state.get("severity"),
            "missing_components": state.get("missing_components"),
        }
        if state.get("status") == "PROCESS_WATCHDOG_PASS":
            return "OK", "OK", status_values
        return "CHECK", "ATTENTION", status_values

    if component == "duplicate_launch_guard":
        status_values = {
            "status": state.get("status"),
            "missing": state.get("missing"),
            "duplicate_alerts": state.get("duplicate_alerts"),
        }
        if state.get("status") == "DUPLICATE_LAUNCH_GUARD_PASS_ALREADY_RUNNING":
            return "OK", "OK", status_values
        return "CHECK", "ATTENTION", status_values

    if component == "candidate_lifecycle_registry":
        candidates = state.get("candidates", [])
        status_values = {
            "registry_status": state.get("registry_status"),
            "candidate_count": len(candidates),
            "archived": [c.get("candidate") for c in candidates if c.get("lifecycle_status") == "ARCHIVE_WAIT"],
        }
        if state.get("registry_status") == "CANDIDATE_LIFECYCLE_REGISTRY_UPDATED":
            return "OK", "OK", status_values
        return "CHECK", "ATTENTION", status_values

    if component == "research_brain":
        status_values = {
            "research_brain_status": state.get("research_brain_status"),
            "open": state.get("open"),
            "pending": state.get("pending"),
            "closed": state.get("closed"),
            "errors": state.get("errors"),
        }
        if state.get("research_brain_status") == "RESEARCH_BRAIN_PLAN_READY":
            return "OK", "OK", status_values
        return "CHECK", "ATTENTION", status_values

    if component == "offline_contract_schema":
        status_values = {"status": state.get("status")}
        if state.get("status") == "OFFLINE_EXPERIMENT_CONTRACT_SCHEMA_READY":
            return "OK", "OK", status_values
        return "CHECK", "ATTENTION", status_values

    if component == "offline_contract_validator":
        status_values = {
            "validation_status": state.get("validation_status"),
            "critical_failed_count": state.get("critical_failed_count"),
            "attention_failed_count": state.get("attention_failed_count"),
            "is_template": state.get("is_template"),
        }
        if state.get("critical_failed_count") == 0:
            return "OK_EXPECTED_TEMPLATE_OR_VALID_CONTRACT", "OK", status_values
        return "CHECK", "ATTENTION", status_values

    if component == "offline_experiment_queue":
        status_values = {
            "queue_status": state.get("queue_status"),
            "closed": state.get("closed"),
            "errors": state.get("errors"),
            "task_count": state.get("task_count"),
        }
        if state.get("queue_status") == "OFFLINE_EXPERIMENT_QUEUE_READY":
            return "OK", "OK", status_values
        return "CHECK", "ATTENTION", status_values

    if component == "os_interface_specs":
        status_values = {"status": state.get("status")}
        if state.get("status") == "OS_INTERFACE_SPECS_READY":
            return "OK", "OK", status_values
        return "CHECK", "ATTENTION", status_values

    if component == "contract_to_runner_adapter":
        status_values = {
            "adapter_status": state.get("adapter_status"),
            "blockers": state.get("blockers"),
            "is_template": state.get("is_template"),
        }
        # Current expected status: blocked because only template exists.
        if state.get("adapter_status") in {"ADAPTER_BLOCKED_NO_RUNNER_REQUEST", "ADAPTER_RUNNER_REQUEST_READY"}:
            return "OK_EXPECTED_BLOCKED_OR_READY", "OK", status_values
        return "CHECK", "ATTENTION", status_values

    if component == "result_to_lifecycle_adapter":
        status_values = {
            "adapter_status": state.get("adapter_status"),
            "decision": state.get("decision"),
            "new_status": state.get("new_status"),
            "blockers": state.get("blockers"),
        }
        if state.get("adapter_status") == "RESULT_TO_LIFECYCLE_DECISION_READY":
            return "OK", "OK", status_values
        return "CHECK", "ATTENTION", status_values

    return "UNKNOWN_COMPONENT", "ATTENTION", {}

def main() -> int:
    out_dir = OUT_ROOT / f"os_state_index_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    full_index = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "index_status": "OS_STATE_INDEX_V2_READY",
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

        health, severity, status_values = classify(comp, state, exists)

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

    attention = [r for r in rows if r["severity"] == "ATTENTION"]
    core = {"command_center", "autopilot_v4", "recovery_manifest_v2", "invariant_guard", "process_watchdog"}
    core_attention = [r for r in attention if r["component"] in core]

    if core_attention:
        index_health = "OS_STATE_INDEX_V2_ATTENTION_CORE"
    elif attention:
        index_health = "OS_STATE_INDEX_V2_ATTENTION_NON_CORE"
    else:
        index_health = "OS_STATE_INDEX_V2_PASS"

    full_index["index_health"] = index_health
    full_index["attention_count"] = len(attention)
    full_index["core_attention_components"] = [r["component"] for r in core_attention]

    state_path = out_dir / "edge_factory_os_state_index_v2_state.json"
    csv_path = out_dir / "edge_factory_os_state_index_v2.csv"
    latest_copy = OUT_ROOT / "edge_factory_os_state_index_v2_latest.json"
    report_path = out_dir / "edge_factory_os_state_index_v2_report.md"

    state_path.write_text(json.dumps(full_index, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_copy.write_text(json.dumps(full_index, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    pd.DataFrame(rows).to_csv(csv_path, index=False)

    md = []
    md.append("# Edge Factory OS State Index v2")
    md.append("")
    md.append(f"Index health: `{index_health}`")
    md.append(f"Attention count: `{len(attention)}`")
    md.append("")
    for r in rows:
        md.append(f"- `{r['component']}` — `{r['health']}` / `{r['severity']}`")
    md.append("")
    md.append("## Safety")
    md.append("- live_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS STATE INDEX v2")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"index_health: {index_health}")
    print(f"attention_count: {len(attention)}")
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
