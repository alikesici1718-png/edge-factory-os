#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_os_research_brain_v1"

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

def add_task(tasks, priority, key, domain, status, reason, allowed_now, command="", blocker=""):
    tasks.append({
        "priority": priority,
        "task_key": key,
        "domain": domain,
        "status": status,
        "allowed_now": bool(allowed_now),
        "reason": reason,
        "blocker": blocker,
        "command": command,
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

def main() -> int:
    out_dir = OUT_ROOT / f"research_brain_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = read_json(WORKSPACE / "edge_factory_os_recovery_manifest_v2" / "edge_factory_os_recovery_manifest_latest.json")

    cc_dir = latest_dir(WORKSPACE / "edge_factory_os_command_center_v1", "os_command_center_v1_")
    cc = read_json(cc_dir / "edge_factory_os_command_center_v1_state.json" if cc_dir else None)

    cand_dir = latest_dir(WORKSPACE / "edge_factory_candidate_lifecycle_registry_v1", "candidate_lifecycle_registry_v1_")
    cand = read_json(cand_dir / "candidate_lifecycle_registry_v1_state.json" if cand_dir else None)

    current = manifest.get("current_state", {})
    open_n = int(current.get("open") or cc.get("open") or 0)
    pending_n = int(current.get("pending") or cc.get("pending") or 0)
    closed_n = int(current.get("closed") or cc.get("closed") or 0)
    errors_n = int(current.get("errors") or cc.get("errors") or 0)

    candidates = cand.get("candidates", [])
    archived = [c.get("candidate") for c in candidates if c.get("lifecycle_status") == "ARCHIVE_WAIT"]

    tasks = []

    # 1. Runtime sample collection is the current dominant task.
    add_task(
        tasks, 1000,
        "protect_running_master_sample",
        "runtime",
        "ACTIVE_WAIT",
        f"MASTER is collecting sample: open={open_n}, pending={pending_n}, closed={closed_n}, errors={errors_n}.",
        allowed_now=True,
        command='python -u "C:\\Users\\alike\\edge_factory_os_command_center_v1.py"',
    )

    # 2. Drift is blocked until closed sample exists.
    if closed_n < 20:
        add_task(
            tasks, 900,
            "defer_drift_until_closed_20",
            "validation",
            "BLOCKED",
            f"Closed sample too small for drift monitor: {closed_n}/20.",
            allowed_now=False,
            blocker="MIN_CLOSED_20_NOT_MET",
        )
    else:
        add_task(
            tasks, 900,
            "run_live_vs_backtest_drift_monitor",
            "validation",
            "READY",
            f"Closed sample sufficient for drift: {closed_n}.",
            allowed_now=True,
            command='python -u "C:\\Users\\alike\\edge_factory_active_family_drift_monitor_planner_v1.py"',
        )

    # 3. Capital governor remains blocked.
    if closed_n < 50:
        add_task(
            tasks, 850,
            "defer_capital_governor_until_closed_50",
            "capital",
            "BLOCKED",
            f"Closed sample too small for capital review: {closed_n}/50.",
            allowed_now=False,
            blocker="MIN_CLOSED_50_NOT_MET",
        )
    else:
        add_task(
            tasks, 850,
            "run_capital_governor_review",
            "capital",
            "READY",
            f"Closed sample sufficient for capital review: {closed_n}.",
            allowed_now=True,
            command='python -u "C:\\Users\\alike\\edge_factory_active_capital_governor_review_v2.py"',
        )

    # 4. Research can continue only as offline planning/spec, not as new live/paper families.
    add_task(
        tasks, 800,
        "build_offline_experiment_contract_schema",
        "research_os",
        "READY_OFFLINE_ONLY",
        "Define standard contract for future offline experiments: data source, rule, OOS split, costs, promotion gates.",
        allowed_now=True,
        command="CREATE_SPEC_ONLY_NO_MASTER_CHANGE",
    )

    add_task(
        tasks, 760,
        "build_candidate_validation_gate_policy",
        "research_os",
        "READY_OFFLINE_ONLY",
        "Create policy: no candidate can enter active paper without OOS, market replay, shadow, no-duplicate runtime, and minimum closed sample.",
        allowed_now=True,
        command="CREATE_POLICY_ONLY_NO_MASTER_CHANGE",
    )

    # 5. Archived candidates remain blocked from promotion.
    for c in archived:
        add_task(
            tasks, 700,
            f"keep_{c}_archived",
            "candidate_lifecycle",
            "ARCHIVE_WAIT",
            f"{c} remains archived; stale/duplicate shadow or missing closed sample.",
            allowed_now=False,
            blocker="ARCHIVE_WAIT_DO_NOT_PROMOTE",
        )

    # 6. Future autonomous research queue, but blocked from execution until current sample stable.
    if closed_n < 20:
        add_task(
            tasks, 650,
            "defer_new_family_search_execution",
            "research_execution",
            "BLOCKED",
            "Do not execute new family search while MASTER initial sample is immature.",
            allowed_now=False,
            blocker="MASTER_INITIAL_SAMPLE_NOT_READY",
        )
    else:
        add_task(
            tasks, 650,
            "resume_new_family_search_planning",
            "research_execution",
            "READY_READ_ONLY_PLANNING",
            "Initial sample exists; can resume offline candidate planning.",
            allowed_now=True,
            command='python -u "C:\\Users\\alike\\edge_factory_batch_family_pipeline_planner.py"',
        )

    tasks = sorted(tasks, key=lambda x: x["priority"], reverse=True)

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "research_brain_status": "RESEARCH_BRAIN_PLAN_READY",
        "open": open_n,
        "pending": pending_n,
        "closed": closed_n,
        "errors": errors_n,
        "archived_candidates": archived,
        "tasks": tasks,
        "hard_rules": [
            "Does not touch MASTER_UPPER_SYSTEM.",
            "Does not start or stop processes.",
            "Does not add new active paper families.",
            "Does not change capital.",
            "Does not enable live trading.",
            "Does not place orders.",
            "Only creates research/validation/lifecycle planning outputs.",
        ],
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
    }

    state_path = out_dir / "edge_factory_os_research_brain_v1_state.json"
    csv_path = out_dir / "edge_factory_os_research_brain_v1_tasks.csv"
    report_path = out_dir / "edge_factory_os_research_brain_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    pd.DataFrame(tasks).to_csv(csv_path, index=False)

    md = []
    md.append("# Edge Factory OS Research Brain v1")
    md.append("")
    md.append(f"Status: `{state['research_brain_status']}`")
    md.append(f"Open: `{open_n}`")
    md.append(f"Pending: `{pending_n}`")
    md.append(f"Closed: `{closed_n}`")
    md.append(f"Errors: `{errors_n}`")
    md.append("")
    md.append("## Tasks")
    for t in tasks:
        md.append(f"- `{t['status']}` `{t['task_key']}` — {t['reason']}")
    md.append("")
    md.append("## Hard rules")
    for r in state["hard_rules"]:
        md.append(f"- {r}")
    md.append("")
    report_path.write_text("\n".join(md), encoding="utf-8")

    print("EDGE FACTORY OS RESEARCH BRAIN v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print("research_brain_status: RESEARCH_BRAIN_PLAN_READY")
    print(f"open   : {open_n}")
    print(f"pending: {pending_n}")
    print(f"closed : {closed_n}")
    print(f"errors : {errors_n}")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("TASKS")
    print("-" * 100)
    df = pd.DataFrame(tasks)
    print(df[["priority","task_key","domain","status","allowed_now","reason","blocker"]].to_string(index=False))
    print()
    print(f"State : {state_path}")
    print(f"Tasks : {csv_path}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
