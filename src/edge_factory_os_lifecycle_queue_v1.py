#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
MASTER_BASE = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

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

def read_csv(path: Path | None) -> pd.DataFrame:
    if not path or not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

def add_task(tasks, priority, task_key, task_type, status, reason, command="", blocker="", live_allowed=False):
    tasks.append({
        "priority": priority,
        "task_key": task_key,
        "task_type": task_type,
        "status": status,
        "reason": reason,
        "command": command,
        "blocker": blocker,
        "live_allowed": bool(live_allowed),
        "active_paper_allowed": False,
        "capital_change_allowed": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_os_lifecycle_queue_v1" / f"os_lifecycle_queue_v1_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    sup_dir = latest_dir(WORKSPACE / "edge_factory_os_supervisor_v1", "os_supervisor_v1_")
    sup_state = read_json(sup_dir / "edge_factory_os_supervisor_v1_state.json" if sup_dir else None)
    decision = sup_state.get("decision", {})

    total_open = int(decision.get("total_open") or 0)
    total_pending = int(decision.get("total_pending") or 0)
    total_closed = int(decision.get("total_closed") or 0)
    total_errors = int(decision.get("total_errors") or 0)

    tasks = []

    if total_errors > 0:
        add_task(
            tasks, 1000,
            "inspect_errors",
            "safety",
            "READY",
            f"errors present: {total_errors}",
            command=f'python "C:\\Users\\alike\\edge_factory_live_health_check_v5.py" --base_dir "{MASTER_BASE}"',
            blocker=""
        )

    if total_open > 0 or total_pending > 0:
        add_task(
            tasks, 900,
            "collect_master_paper_sample",
            "runtime_monitoring",
            "ACTIVE_WAIT",
            f"MASTER is running with open={total_open}, pending={total_pending}, closed={total_closed}. Do not debug unless health fails.",
            command=f'python "C:\\Users\\alike\\edge_factory_live_performance_analyzer_v3.py" --base_dir "{MASTER_BASE}"',
        )
    else:
        add_task(
            tasks, 850,
            "wait_for_master_signals",
            "runtime_monitoring",
            "WAIT",
            "MASTER has no open/pending positions yet.",
            command=f'python "C:\\Users\\alike\\edge_factory_live_health_check_v5.py" --base_dir "{MASTER_BASE}"',
        )

    if total_closed < 20:
        add_task(
            tasks, 800,
            "block_drift_until_min_sample",
            "drift_monitoring",
            "BLOCKED",
            f"closed sample too small: {total_closed}/20",
            blocker="MIN_CLOSED_SAMPLE_NOT_MET",
        )
    else:
        add_task(
            tasks, 800,
            "run_live_vs_backtest_drift_monitor",
            "drift_monitoring",
            "READY",
            f"closed sample sufficient: {total_closed}",
            command='python "C:\\Users\\alike\\edge_factory_active_family_drift_monitor_planner_v1.py"',
        )

    if total_closed < 50:
        add_task(
            tasks, 700,
            "block_capital_governor_until_larger_sample",
            "capital_governor",
            "BLOCKED",
            f"closed sample too small for capital changes: {total_closed}/50",
            blocker="MIN_CLOSED_FOR_CAPITAL_REVIEW_NOT_MET",
        )
    else:
        add_task(
            tasks, 700,
            "run_capital_governor_review",
            "capital_governor",
            "READY",
            f"closed sample sufficient for capital review: {total_closed}",
            command='python "C:\\Users\\alike\\edge_factory_active_capital_governor_review_v2.py"',
        )

    # Research candidate side: rel_extreme exists as a validated candidate, but should remain shadow until live/paper sample exists.
    rel_shadow_dir = WORKSPACE / "paper_run_shadow_rel_extreme_reversion_short"
    rel_heartbeat = list(rel_shadow_dir.glob("*heartbeat*.json")) if rel_shadow_dir.exists() else []
    rel_signals = read_csv(rel_shadow_dir / "rel_extreme_shadow_signals.csv")
    rel_closed = read_csv(rel_shadow_dir / "rel_extreme_shadow_closed_trades.csv")

    if rel_shadow_dir.exists() and rel_heartbeat:
        add_task(
            tasks, 600,
            "monitor_rel_extreme_shadow",
            "candidate_shadow",
            "ACTIVE_WAIT",
            f"rel_extreme shadow exists; signals={len(rel_signals)}, closed={len(rel_closed)}",
            command='Get-ChildItem "C:\\Users\\alike\\OneDrive\\Desktop\\edge_lab_new\\paper_run_shadow_rel_extreme_reversion_short"',
        )
    else:
        add_task(
            tasks, 600,
            "start_or_confirm_rel_extreme_shadow",
            "candidate_shadow",
            "OPTIONAL_READY",
            "rel_extreme passed shadow gate previously, but shadow runtime is not confirmed running by this queue.",
            command='python -u "C:\\Users\\alike\\edge_factory_rel_extreme_shadow_start_gate_v1.py"',
        )

    # Candidate research queue: only after runtime stable; do not distract while MASTER is collecting first sample.
    if total_closed < 20:
        add_task(
            tasks, 500,
            "pause_new_candidate_research",
            "research_queue",
            "WAIT",
            "Do not add new families until MASTER produces initial closed sample.",
            blocker="MASTER_INITIAL_SAMPLE_NOT_READY",
        )
    else:
        add_task(
            tasks, 500,
            "resume_candidate_batch_pipeline",
            "research_queue",
            "READY",
            "MASTER has enough sample to resume candidate queue.",
            command='python "C:\\Users\\alike\\edge_factory_batch_family_pipeline_planner.py"',
        )

    tasks_sorted = sorted(tasks, key=lambda x: x["priority"], reverse=True)

    queue_df = pd.DataFrame(tasks_sorted)
    queue_path = out_dir / "edge_factory_os_lifecycle_queue_v1.csv"
    state_path = out_dir / "edge_factory_os_lifecycle_queue_v1_state.json"
    report_path = out_dir / "edge_factory_os_lifecycle_queue_v1_report.md"

    queue_df.to_csv(queue_path, index=False)

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "master_base": str(MASTER_BASE),
        "supervisor_state": str(sup_dir / "edge_factory_os_supervisor_v1_state.json") if sup_dir else None,
        "total_open": total_open,
        "total_pending": total_pending,
        "total_closed": total_closed,
        "total_errors": total_errors,
        "queue_count": len(tasks_sorted),
        "tasks": tasks_sorted,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
    }
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    report = []
    report.append("# EDGE FACTORY OS LIFECYCLE QUEUE v1")
    report.append("")
    report.append(f"open: `{total_open}`")
    report.append(f"pending: `{total_pending}`")
    report.append(f"closed: `{total_closed}`")
    report.append(f"errors: `{total_errors}`")
    report.append("")
    report.append("## Queue")
    for t in tasks_sorted:
        report.append(f"- `{t['status']}` `{t['task_key']}` — {t['reason']}")
    report.append("")
    report.append("## Hard safety")
    report.append("- active_paper_allowed: `False`")
    report.append("- live_allowed: `False`")
    report.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS LIFECYCLE QUEUE v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"master    : {MASTER_BASE}")
    print(f"output_dir: {out_dir}")
    print(f"open      : {total_open}")
    print(f"pending   : {total_pending}")
    print(f"closed    : {total_closed}")
    print(f"errors    : {total_errors}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("QUEUE")
    print("-" * 100)
    print(queue_df[["priority","task_key","task_type","status","reason","blocker"]].to_string(index=False))
    print()
    print(f"State : {state_path}")
    print(f"Queue : {queue_path}")
    print(f"Report: {report_path}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
