#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Supervisor module for the Edge Factory OS paper trading runtime that reads per-family CSV files (pending entries, open positions, closed trades, heartbeats) from the MASTER_UPPER_SYSTEM paper directory and produces a family-level health summary. Outputs a supervisor state JSON to a timestamped directory under edge_factory_os_supervisor_v1.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
MASTER_BASE = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"

FAMILIES = {
    "old_short": "live_blowoff_short_paper_realistic",
    "impulse_long": "live_impulse_event_long_paper",
    "market_relative_short": "live_market_relative_extreme_reversion_short_paper",
    "weak_market_short": "live_weak_market_breakdown_short_paper",
}

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def read_csv_safe(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

def read_json_safe(path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}

def latest_dir(root: Path, prefix: str) -> Path | None:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    if not ds:
        return None
    return sorted(ds, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def file_age_minutes(path: Path) -> float | None:
    if not path.exists():
        return None
    now = datetime.now(timezone.utc).timestamp()
    return round((now - path.stat().st_mtime) / 60.0, 2)

def family_state(family_key: str, folder_name: str) -> dict[str, Any]:
    folder = MASTER_BASE / folder_name

    pending = read_csv_safe(folder / "pending_entries.csv")
    openp = read_csv_safe(folder / "open_positions.csv")
    closed = read_csv_safe(folder / "closed_trades.csv")
    rejected = read_csv_safe(folder / "rejected_entries.csv")
    errors = read_csv_safe(folder / "errors.csv")

    heartbeat_candidates = list(folder.glob("*heartbeat*.json"))
    heartbeat_path = sorted(heartbeat_candidates, key=lambda p: p.stat().st_mtime, reverse=True)[0] if heartbeat_candidates else None

    return {
        "family_key": family_key,
        "folder": str(folder),
        "folder_exists": folder.exists(),
        "heartbeat_path": str(heartbeat_path) if heartbeat_path else None,
        "heartbeat_age_min": file_age_minutes(heartbeat_path) if heartbeat_path else None,
        "pending_rows": int(len(pending)),
        "open_rows": int(len(openp)),
        "closed_rows": int(len(closed)),
        "rejected_rows": int(len(rejected)),
        "error_rows": int(len(errors)),
        "latest_reject_reason": str(rejected.tail(1)["reason"].iloc[0]) if (not rejected.empty and "reason" in rejected.columns) else None,
        "latest_error": errors.tail(1).to_dict("records")[0] if not errors.empty else None,
    }

def summarize_gate() -> dict[str, Any]:
    gate = read_csv_safe(MASTER_BASE / "global_gate_decisions.csv")
    snap = read_csv_safe(MASTER_BASE / "global_risk_snapshot.csv")

    out = {
        "gate_path": str(MASTER_BASE / "global_gate_decisions.csv"),
        "gate_rows": int(len(gate)),
        "snapshot_rows": int(len(snap)),
        "last_gate_time": None,
        "last_snapshot_time": None,
        "last_decision_counts": {},
        "snapshot_pending_entries": None,
        "snapshot_open_positions": None,
    }

    if not gate.empty:
        if "log_time" in gate.columns:
            out["last_gate_time"] = str(gate["log_time"].iloc[-1])
        if "decision" in gate.columns:
            out["last_decision_counts"] = gate.tail(50)["decision"].value_counts().to_dict()

    if not snap.empty:
        if "log_time" in snap.columns:
            out["last_snapshot_time"] = str(snap["log_time"].iloc[-1])
        if "pending_entries" in snap.columns:
            out["snapshot_pending_entries"] = int(float(snap["pending_entries"].iloc[-1]))
        if "open_positions" in snap.columns:
            out["snapshot_open_positions"] = int(float(snap["open_positions"].iloc[-1]))

    return out

def latest_optional_states() -> dict[str, Any]:
    states: dict[str, Any] = {}

    refresh_dir = latest_dir(WORKSPACE / "edge_factory_active_family_robustness_refresh_v2", "active_family_refresh_v2_")
    if refresh_dir:
        states["active_family_refresh_v2"] = {
            "dir": str(refresh_dir),
            "summary": str(refresh_dir / "active_family_robustness_refresh_v2_summary.csv"),
            "state": str(refresh_dir / "active_family_robustness_refresh_v2_state.json"),
        }

    cap_dir = latest_dir(WORKSPACE / "edge_factory_active_capital_governor_review_v2", "active_capital_governor_v2_")
    if cap_dir:
        states["capital_governor_v2"] = {
            "dir": str(cap_dir),
            "summary": str(cap_dir / "active_capital_governor_review_v2_summary.csv"),
            "state": str(cap_dir / "active_capital_governor_review_v2_state.json"),
        }

    rel_shadow = WORKSPACE / "paper_run_shadow_rel_extreme_reversion_short"
    if rel_shadow.exists():
        states["rel_extreme_shadow"] = {
            "dir": str(rel_shadow),
            "heartbeat_age_min": min(
                [file_age_minutes(p) for p in rel_shadow.glob("*heartbeat*.json") if file_age_minutes(p) is not None] or [None]
            ),
            "signals_rows": int(len(read_csv_safe(rel_shadow / "rel_extreme_shadow_signals.csv"))),
            "closed_rows": int(len(read_csv_safe(rel_shadow / "rel_extreme_shadow_closed_trades.csv"))),
        }

    return states

def decide(families: list[dict[str, Any]], gate: dict[str, Any]) -> dict[str, Any]:
    total_open = sum(x["open_rows"] for x in families)
    total_pending = sum(x["pending_rows"] for x in families)
    total_closed = sum(x["closed_rows"] for x in families)
    total_errors = sum(x["error_rows"] for x in families)

    stale = [
        x["family_key"]
        for x in families
        if x["heartbeat_age_min"] is not None and x["heartbeat_age_min"] > 10
    ]

    critical = []
    warnings = []
    next_actions = []

    if stale:
        critical.append(f"STALE_HEARTBEAT: {stale}")
        next_actions.append("RUN_HEALTH_CHECK_AND_RESTART_STALE_FAMILY_ONLY")

    if total_errors > 0:
        warnings.append("ERROR_ROWS_PRESENT_REVIEW_ERRORS_CSV")
        next_actions.append("INSPECT_ERRORS_CSV")

    if gate["gate_rows"] == 0:
        critical.append("GLOBAL_GATE_DECISIONS_EMPTY")
        next_actions.append("RUN_RISK_MANAGER_ONCE_TEST")

    if total_open > 0:
        next_actions.append("DO_NOT_DEBUG_MASTER_COLLECT_CLOSED_SAMPLE")
    elif total_pending > 0:
        next_actions.append("WAIT_FOR_PENDING_TO_GATE_OR_OPEN")
    else:
        next_actions.append("WAIT_FOR_SIGNALS")

    if total_closed < 20:
        next_actions.append("DRIFT_MONITOR_BLOCKED_UNTIL_MIN_CLOSED_SAMPLE")
    else:
        next_actions.append("RUN_LIVE_VS_BACKTEST_DRIFT_MONITOR")

    if total_closed >= 50:
        next_actions.append("RUN_CAPITAL_GOVERNOR_REVIEW")
    else:
        next_actions.append("NO_CAPITAL_CHANGE_YET")

    if critical:
        status = "OS_SUPERVISOR_ATTENTION_REQUIRED"
    elif total_open > 0 or total_pending > 0:
        status = "OS_SUPERVISOR_RUNNING_COLLECTING_SAMPLE"
    else:
        status = "OS_SUPERVISOR_IDLE_WAITING_FOR_SIGNALS"

    return {
        "status": status,
        "total_open": total_open,
        "total_pending": total_pending,
        "total_closed": total_closed,
        "total_errors": total_errors,
        "critical": critical,
        "warnings": warnings,
        "next_actions": list(dict.fromkeys(next_actions)),
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
    }

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_os_supervisor_v1" / f"os_supervisor_v1_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    families = [family_state(k, v) for k, v in FAMILIES.items()]
    gate = summarize_gate()
    optional = latest_optional_states()
    decision = decide(families, gate)

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "master_base": str(MASTER_BASE),
        "decision": decision,
        "families": families,
        "gate": gate,
        "optional_states": optional,
        "hard_rules": [
            "Read-only supervisor.",
            "Does not start/stop processes.",
            "Does not change capital.",
            "Does not place orders.",
            "Does not enable live trading.",
        ],
    }

    state_path = out_dir / "edge_factory_os_supervisor_v1_state.json"
    families_path = out_dir / "edge_factory_os_supervisor_v1_families.csv"
    report_path = out_dir / "edge_factory_os_supervisor_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    pd.DataFrame(families).to_csv(families_path, index=False)

    report = []
    report.append("# EDGE FACTORY OS SUPERVISOR v1")
    report.append("")
    report.append(f"status: `{decision['status']}`")
    report.append(f"open: `{decision['total_open']}`")
    report.append(f"pending: `{decision['total_pending']}`")
    report.append(f"closed: `{decision['total_closed']}`")
    report.append(f"errors: `{decision['total_errors']}`")
    report.append("")
    report.append("## Next actions")
    for a in decision["next_actions"]:
        report.append(f"- `{a}`")
    report.append("")
    report.append("## Hard safety")
    report.append("- active_paper_allowed: `False`")
    report.append("- live_allowed: `False`")
    report.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS SUPERVISOR v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"master    : {MASTER_BASE}")
    print(f"output_dir: {out_dir}")
    print(f"status    : {decision['status']}")
    print(f"open      : {decision['total_open']}")
    print(f"pending   : {decision['total_pending']}")
    print(f"closed    : {decision['total_closed']}")
    print(f"errors    : {decision['total_errors']}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()

    print("FAMILY SUMMARY")
    print("-" * 100)
    print(pd.DataFrame(families).to_string(index=False))
    print()

    print("GATE SUMMARY")
    print("-" * 100)
    print(json.dumps(gate, indent=2, ensure_ascii=False, default=str))
    print()

    print("NEXT ACTIONS")
    print("-" * 100)
    for a in decision["next_actions"]:
        print("-", a)

    print()
    print(f"State  : {state_path}")
    print(f"Family : {families_path}")
    print(f"Report : {report_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
