#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY AUTONOMOUS RESEARCH QUEUE v1
=========================================

Purpose
-------
Offline research-planning brain for the Edge Factory OS.

At this stage the OS has:
    - Rolling OOS validation
    - Family lifecycle state
    - Adaptive capital proposal
    - Execution realism decisions
    - Kill-switch policy
    - Preflight gate
    - Reconciled sizing contract

This module does NOT start paper/live trading.
It does NOT place orders.
It does NOT modify contracts/loggers.
It builds the next self-improvement queue:
    - what to validate next
    - what to repair
    - what to research
    - what to postpone until paper exists
    - what is blocked from live

Run:
    python "C:\Users\alike\edge_factory_autonomous_research_queue.py"

Outputs:
    <workspace>\edge_factory_autonomous_research_queue\research_queue_YYYYMMDD_HHMMSS\
        research_queue.json
        research_queue.csv
        research_queue_report.md
        os_next_actions.json
        candidate_family_watchlist.csv

Design principle
----------------
This queue is conservative. It does not promote a new strategy family from one broad scan.
It turns strong unknown candidates into isolated research tasks, not live/paper activation.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
KNOWN_FAMILIES = {"old_short", "impulse_long", "market_relative_short", "weak_market_short", "session_short"}

# These appeared as plausible non-master candidates in broad OOS scans.
# They should be researched in isolation, not activated automatically.
RESEARCH_NAME_HINTS = [
    "rel_extreme_reversion_short",
    "ret60_reversal_short",
    "relative_weakness_snapback_long",
    "market_panic_rebound_long",
    "capitulation_reversal_long",
    "relative_strength_continuation_long",
]

GARBAGE_FAMILY_NAMES = {"unknown", "nan", "none", "null", "{}", ""}


@dataclass
class ResearchTask:
    priority: int
    task_key: str
    title: str
    category: str
    status: str
    reason: str
    safe_offline: bool
    blocked_by: List[str]
    suggested_script_name: str
    suggested_command: str
    inputs: List[str]
    outputs: List[str]
    success_criteria: List[str]
    failure_criteria: List[str]


@dataclass
class CandidateWatch:
    family_key: str
    validation_decision: str
    confidence: str
    trade_count: int
    total_pnl: float
    avg_pnl: float
    win_rate: float
    profit_factor: float
    test_trade_count: int
    test_avg_pnl: float
    reason: str
    recommended_status: str


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_float(x: Any, default: float = 0.0) -> float:
    try:
        if x is None:
            return default
        if isinstance(x, str):
            s = x.strip().lower()
            if s in {"", "none", "null", "nan", "inf", "infinity"}:
                return default
        v = float(x)
        if math.isnan(v) or math.isinf(v):
            return default
        return v
    except Exception:
        return default


def safe_int(x: Any, default: int = 0) -> int:
    try:
        return int(round(safe_float(x, default=default)))
    except Exception:
        return default


def latest_child_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def optional_json(path: Optional[Path]) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        obj = load_json(path)
        return obj if isinstance(obj, dict) else {"_list": obj} if isinstance(obj, list) else {}
    except Exception:
        return {}


def discover_latest_artifacts(workspace: Path) -> Dict[str, Optional[Path]]:
    dirs = {
        "preflight": (workspace / "edge_factory_os_preflight", "preflight_", "preflight_report.json"),
        "kill_switch": (workspace / "edge_factory_kill_switch_controller", "kill_switch_", "kill_switch_policy.json"),
        "execution": (workspace / "edge_factory_execution_realism_checker", "execution_realism_", "execution_realism_decisions.json"),
        "capital": (workspace / "edge_factory_adaptive_capital_governor_v2", "capital_governor_", "capital_policy_proposal.json"),
        "lifecycle": (workspace / "edge_factory_family_lifecycle", "lifecycle_", "family_lifecycle_state.json"),
        "rolling_oos": (workspace / "edge_factory_rolling_oos_validator", "rolling_oos_", "rolling_oos_decisions.json"),
        "contract_reconciler": (workspace / "edge_factory_contract_reconciler", "contract_reconcile_", "contract_diff.json"),
    }
    out: Dict[str, Optional[Path]] = {}
    for key, (root, prefix, filename) in dirs.items():
        d = latest_child_dir(root, prefix)
        out[key] = d / filename if d and (d / filename).exists() else None
    return out


def decision_rows_from_oos(oos_obj: Dict[str, Any]) -> List[Dict[str, Any]]:
    if "_list" in oos_obj and isinstance(oos_obj["_list"], list):
        return [x for x in oos_obj["_list"] if isinstance(x, dict)]
    if isinstance(oos_obj.get("decisions"), list):
        return [x for x in oos_obj["decisions"] if isinstance(x, dict)]
    return []


def extract_metrics(row: Dict[str, Any]) -> Dict[str, Any]:
    m = row.get("metrics") or {}
    o = row.get("oos_metrics") or {}
    test = o.get("test") if isinstance(o.get("test"), dict) else {}
    return {
        "trade_count": safe_int(m.get("trade_count")),
        "total_pnl": safe_float(m.get("total_pnl")),
        "avg_pnl": safe_float(m.get("avg_pnl")),
        "win_rate": safe_float(m.get("win_rate")),
        "profit_factor": safe_float(m.get("profit_factor")),
        "test_trade_count": safe_int(test.get("trade_count")),
        "test_avg_pnl": safe_float(test.get("avg_pnl")),
    }


def is_candidate_name(name: str) -> bool:
    s = str(name).strip().lower()
    if s in GARBAGE_FAMILY_NAMES:
        return False
    if s in KNOWN_FAMILIES:
        return False
    if any(h in s for h in RESEARCH_NAME_HINTS):
        return True
    # Avoid numeric garbage / optimizer row ids.
    if s.isdigit():
        return False
    if len(s) < 4:
        return False
    return False


def build_candidate_watchlist(oos_rows: List[Dict[str, Any]]) -> List[CandidateWatch]:
    watches: List[CandidateWatch] = []
    for row in oos_rows:
        fam = str(row.get("family_key", "")).strip()
        if not is_candidate_name(fam):
            continue
        decision = str(row.get("decision", "UNKNOWN"))
        metrics = extract_metrics(row)
        if decision not in {"STRONG_CANDIDATE", "PASS_CANDIDATE"}:
            continue
        if metrics["trade_count"] < 100:
            continue
        reason = "strong broad-scan candidate; must be isolated and revalidated before any inclusion"
        status = "QUEUE_ISOLATED_RESEARCH"
        if metrics["trade_count"] < 250:
            status = "WATCH_LOW_SAMPLE"
            reason = "candidate passed but sample is small; queue only after higher-priority checks"
        watches.append(CandidateWatch(
            family_key=fam,
            validation_decision=decision,
            confidence=str(row.get("confidence", "low")),
            trade_count=metrics["trade_count"],
            total_pnl=metrics["total_pnl"],
            avg_pnl=metrics["avg_pnl"],
            win_rate=metrics["win_rate"],
            profit_factor=metrics["profit_factor"],
            test_trade_count=metrics["test_trade_count"],
            test_avg_pnl=metrics["test_avg_pnl"],
            reason=reason,
            recommended_status=status,
        ))
    watches.sort(key=lambda x: (x.recommended_status == "QUEUE_ISOLATED_RESEARCH", x.profit_factor, x.trade_count), reverse=True)
    return watches


def get_preflight_state(preflight: Dict[str, Any]) -> Tuple[str, List[str], List[str]]:
    decision = str(preflight.get("paper_boot_decision", "UNKNOWN"))
    warnings = list(preflight.get("warnings") or [])
    blockers = list(preflight.get("blockers") or [])
    return decision, warnings, blockers


def build_tasks(workspace: Path, artifacts: Dict[str, Optional[Path]], data: Dict[str, Dict[str, Any]], watchlist: List[CandidateWatch]) -> List[ResearchTask]:
    tasks: List[ResearchTask] = []
    preflight_decision, preflight_warnings, preflight_blockers = get_preflight_state(data.get("preflight", {}))

    # 1) Resolve/acknowledge current preflight warnings.
    if "estimated_bps_warning" in preflight_warnings:
        tasks.append(ResearchTask(
            priority=10,
            task_key="build_native_bps_and_cost_validation",
            title="Build native bps / cost validation pass",
            category="execution_quality",
            status="OPEN",
            reason="Execution passed, but some bps values were estimated rather than native. Live must remain blocked until paper/native bps confirms the edge.",
            safe_offline=True,
            blocked_by=[],
            suggested_script_name="edge_factory_native_bps_validator.py",
            suggested_command="python \"C:\\Users\\alike\\edge_factory_native_bps_validator.py\"",
            inputs=[str(artifacts.get("execution")), str(artifacts.get("rolling_oos"))],
            outputs=["native_bps_validation_report.json", "native_bps_family_summary.csv"],
            success_criteria=[
                "native or better bps estimate exists for each active family",
                "old_short and impulse_long still positive after realistic cost",
                "backup families remain capped even if they pass",
            ],
            failure_criteria=[
                "net avg bps <= 0 for core/diversifier",
                "net PF < 1 after realistic cost",
                "cost model cannot be estimated from available data",
            ],
        ))

    if "paper_dir_status" in preflight_warnings:
        tasks.append(ResearchTask(
            priority=20,
            task_key="paper_runtime_dry_run_plan",
            title="Create paper runtime dry-run plan, but do not start it automatically",
            category="paper_readiness",
            status="OPEN",
            reason="Preflight warns that paper dir is absent/not active because paper has not been started. The OS should define a supervised paper boot plan without launching yet.",
            safe_offline=True,
            blocked_by=["user approval before actual paper boot"],
            suggested_script_name="edge_factory_paper_boot_plan.py",
            suggested_command="python \"C:\\Users\\alike\\edge_factory_paper_boot_plan.py\"",
            inputs=[str(artifacts.get("preflight")), str(artifacts.get("kill_switch")), str(artifacts.get("capital"))],
            outputs=["paper_boot_plan.md", "paper_runtime_expected_files.json"],
            success_criteria=[
                "lists exact commands to start MASTER_UPPER_SYSTEM",
                "lists expected output folders/log files",
                "does not start paper automatically",
            ],
            failure_criteria=["missing launcher", "missing kill_switch_policy", "missing sizing contract"],
        ))

    if preflight_blockers:
        tasks.append(ResearchTask(
            priority=1,
            task_key="repair_preflight_blockers",
            title="Repair preflight blockers before any further boot planning",
            category="repair",
            status="BLOCKING",
            reason="Preflight contains blockers. Nothing should proceed until fixed.",
            safe_offline=True,
            blocked_by=[] ,
            suggested_script_name="manual_repair_then_rerun_preflight",
            suggested_command="python \"C:\\Users\\alike\\edge_factory_os_preflight_inspector.py\"",
            inputs=[str(artifacts.get("preflight"))],
            outputs=["clean preflight_report.json"],
            success_criteria=["blockers=0"],
            failure_criteria=["any blocker remains"],
        ))

    # 2) Data hygiene task: OOS validator polluted unknown family rows.
    tasks.append(ResearchTask(
        priority=30,
        task_key="patch_oos_validator_active_only_and_trade_level_filter",
        title="Patch Rolling OOS Validator to separate active families from candidate/summary rows",
        category="data_quality",
        status="OPEN",
        reason="The validator produced useful active-family results but also treated some numeric/summary/config rows as unknown families. This should be cleaned before future autonomous decisions.",
        safe_offline=True,
        blocked_by=[],
        suggested_script_name="edge_factory_rolling_oos_validator_v2.py",
        suggested_command="python \"C:\\Users\\alike\\edge_factory_rolling_oos_validator_v2.py\" --active_only",
        inputs=[str(artifacts.get("rolling_oos"))],
        outputs=["rolling_oos_v2_decisions.json", "rolling_oos_v2_active_summary.csv", "candidate_rows_separated.csv"],
        success_criteria=[
            "active family report contains only old_short, impulse_long, market_relative_short, weak_market_short, session_short",
            "research candidates are separated into a different file",
            "numeric/nan/{} family names are excluded",
        ],
        failure_criteria=["unknown garbage families still affect active-family summary"],
    ))

    # 3) Known-family next validations.
    tasks.append(ResearchTask(
        priority=40,
        task_key="market_relative_backup_retest",
        title="Retest market_relative_short as backup-only at 12.5 USDT",
        category="known_family_validation",
        status="OPEN",
        reason="Lifecycle demoted market_relative_short to BACKUP_ONLY and governor cut it to 12.5. It needs a focused backup-only validation, not full-size treatment.",
        safe_offline=True,
        blocked_by=[],
        suggested_script_name="edge_factory_market_relative_backup_validator.py",
        suggested_command="python \"C:\\Users\\alike\\edge_factory_market_relative_backup_validator.py\"",
        inputs=[str(artifacts.get("capital")), str(artifacts.get("kill_switch")), str(artifacts.get("rolling_oos"))],
        outputs=["market_relative_backup_report.json", "market_relative_bad_day_recheck.csv"],
        success_criteria=[
            "market_relative_short stays positive at 12.5 notional under stricter bad-day stop",
            "bad-day damage is bounded by kill-switch policy",
            "no recommendation to restore full size",
        ],
        failure_criteria=["rolling bad-day loss still dominates", "backup mode fails after cost"],
    ))

    tasks.append(ResearchTask(
        priority=45,
        task_key="weak_market_symbol_breadth_recheck",
        title="Recheck weak_market_short symbol breadth before any promotion",
        category="known_family_validation",
        status="OPEN",
        reason="Execution checker passed weak_market_short but flagged LOW_POSITIVE_SYMBOL_RATE. It remains backup-only until breadth improves.",
        safe_offline=True,
        blocked_by=[],
        suggested_script_name="edge_factory_weak_market_breadth_validator.py",
        suggested_command="python \"C:\\Users\\alike\\edge_factory_weak_market_breadth_validator.py\"",
        inputs=[str(artifacts.get("execution")), str(artifacts.get("rolling_oos"))],
        outputs=["weak_market_symbol_breadth_report.json", "weak_market_symbol_distribution.csv"],
        success_criteria=["positive valid symbol rate >= 0.55", "top symbol concentration acceptable", "backup-only status preserved until paper evidence"],
        failure_criteria=["edge concentrated in too few symbols", "positive symbol rate remains weak"],
    ))

    # 4) Candidate family queue from broad scan.
    base_priority = 60
    for i, cand in enumerate(watchlist[:8]):
        tasks.append(ResearchTask(
            priority=base_priority + i,
            task_key=f"research_candidate_{cand.family_key}",
            title=f"Isolated research validation for {cand.family_key}",
            category="new_family_research",
            status="OPEN" if cand.recommended_status == "QUEUE_ISOLATED_RESEARCH" else "WATCHLIST",
            reason=f"{cand.reason}. Broad scan: decision={cand.validation_decision}, trades={cand.trade_count}, PF={cand.profit_factor:.3f}.",
            safe_offline=True,
            blocked_by=["isolated OOS validator", "execution realism", "lifecycle review"],
            suggested_script_name="edge_factory_isolated_candidate_validator.py",
            suggested_command=f"python \"C:\\Users\\alike\\edge_factory_isolated_candidate_validator.py\" --candidate \"{cand.family_key}\"",
            inputs=[str(artifacts.get("rolling_oos"))],
            outputs=[f"candidate_{cand.family_key}_isolated_report.json", f"candidate_{cand.family_key}_trades.csv"],
            success_criteria=[
                "passes isolated time OOS",
                "passes symbol distribution robustness",
                "passes execution cost stress",
                "does not overlap destructively with old_short/impulse_long",
            ],
            failure_criteria=[
                "performance disappears outside broad scan",
                "single-symbol or single-month dependence",
                "cost-adjusted PF < 1.1",
            ],
        ))

    # 5) Later after paper starts.
    tasks.append(ResearchTask(
        priority=90,
        task_key="activate_drift_monitor_after_paper_closed_trades",
        title="Run live-vs-backtest drift monitor after paper has closed trades",
        category="after_paper_boot",
        status="BLOCKED_UNTIL_PAPER_DATA",
        reason="Drift monitor is meaningless until paper produces closed trades. It should be scheduled after paper boot, not before.",
        safe_offline=True,
        blocked_by=["paper closed trades"],
        suggested_script_name="edge_factory_live_vs_backtest_drift_monitor.py",
        suggested_command="python \"C:\\Users\\alike\\edge_factory_live_vs_backtest_drift_monitor.py\"",
        inputs=["paper closed trades", str(artifacts.get("capital")), str(artifacts.get("kill_switch"))],
        outputs=["drift_decisions.json", "drift_family_summary.csv"],
        success_criteria=["paper sample available", "family-level drift labels generated"],
        failure_criteria=["no closed paper trades", "logger output missing"],
    ))

    tasks.sort(key=lambda t: t.priority)
    return tasks


def task_df(tasks: List[ResearchTask]) -> pd.DataFrame:
    rows = []
    for t in tasks:
        r = asdict(t)
        for k in ["blocked_by", "inputs", "outputs", "success_criteria", "failure_criteria"]:
            r[k] = " | ".join(r[k])
        rows.append(r)
    return pd.DataFrame(rows)


def watch_df(watches: List[CandidateWatch]) -> pd.DataFrame:
    return pd.DataFrame([asdict(w) for w in watches])


def write_report(path: Path, context: Dict[str, Any], tasks: List[ResearchTask], watches: List[CandidateWatch]) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory Autonomous Research Queue Report")
    lines.append("")
    lines.append(f"Generated: `{context['generated_at']}`")
    lines.append(f"Workspace: `{context['workspace']}`")
    lines.append(f"Preflight decision: **{context['preflight_decision']}**")
    lines.append(f"Live gate: **{context['live_gate']}**")
    lines.append("")

    lines.append("## Executive next actions")
    lines.append("")
    lines.append("| Priority | Category | Status | Task | Script | Blocked by |")
    lines.append("|---:|---|---:|---|---|---|")
    for t in tasks[:20]:
        blocked = ", ".join(t.blocked_by)
        lines.append(f"| {t.priority} | {t.category} | {t.status} | {t.title} | `{t.suggested_script_name}` | {blocked} |")
    lines.append("")

    lines.append("## Candidate family watchlist")
    lines.append("")
    if not watches:
        lines.append("No clean non-master candidates passed the watchlist filter.")
    else:
        lines.append("| Candidate | Status | Decision | Trades | PF | Avg PnL | Test Avg | Reason |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---|")
        for w in watches[:15]:
            lines.append(f"| {w.family_key} | {w.recommended_status} | {w.validation_decision} | {w.trade_count} | {w.profit_factor:.3f} | {w.avg_pnl:.6f} | {w.test_avg_pnl:.6f} | {w.reason} |")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("This queue is the first self-improvement layer. It does not run research automatically; it decides what should be researched next and what is blocked.")
    lines.append("The most important current tasks are native bps/cost validation, OOS validator cleanup, and focused backup-family checks.")
    lines.append("Live remains blocked until paper drift exists and manual live review approves.")
    lines.append("")

    lines.append("## Artifact sources")
    lines.append("")
    for k, v in context.get("artifacts", {}).items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory autonomous research queue")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--out_dir", default=None)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_autonomous_research_queue"
    out_dir = out_root / f"research_queue_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    artifacts = discover_latest_artifacts(workspace)
    data = {k: optional_json(v) for k, v in artifacts.items()}

    oos_rows = decision_rows_from_oos(data.get("rolling_oos", {}))
    watchlist = build_candidate_watchlist(oos_rows)
    tasks = build_tasks(workspace, artifacts, data, watchlist)

    preflight_decision, preflight_warnings, preflight_blockers = get_preflight_state(data.get("preflight", {}))
    kill = data.get("kill_switch", {})
    live_gate = str(kill.get("live_gate", "LIVE_BLOCKED"))

    context = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(workspace),
        "preflight_decision": preflight_decision,
        "preflight_warnings": preflight_warnings,
        "preflight_blockers": preflight_blockers,
        "live_gate": live_gate,
        "artifacts": {k: str(v) if v else None for k, v in artifacts.items()},
        "task_count": len(tasks),
        "watchlist_count": len(watchlist),
    }

    queue_obj = {
        "context": context,
        "tasks": [asdict(t) for t in tasks],
        "candidate_watchlist": [asdict(w) for w in watchlist],
        "hard_rules": [
            "Do not activate new research candidates directly from broad scan.",
            "Do not run live before paper drift validation and manual live review.",
            "Backup-only families cannot self-promote.",
            "Estimated bps warning must be addressed through paper/native bps validation.",
        ],
    }

    write_json(out_dir / "research_queue.json", queue_obj)
    write_json(out_dir / "os_next_actions.json", [asdict(t) for t in tasks[:10]])
    task_df(tasks).to_csv(out_dir / "research_queue.csv", index=False)
    watch_df(watchlist).to_csv(out_dir / "candidate_family_watchlist.csv", index=False)
    write_report(out_dir / "research_queue_report.md", context, tasks, watchlist)

    print("EDGE FACTORY AUTONOMOUS RESEARCH QUEUE v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"output_dir: {out_dir}")
    print(f"preflight : {preflight_decision}")
    print(f"live_gate : {live_gate}")
    print(f"tasks     : {len(tasks)}")
    print(f"watchlist : {len(watchlist)}")
    print("")
    print("TOP NEXT TASKS")
    print("-" * 100)
    for t in tasks[:10]:
        blocked = ", ".join(t.blocked_by) if t.blocked_by else "none"
        print(f"P{t.priority:03d} [{t.category}] {t.status} -> {t.title}")
        print(f"     script : {t.suggested_script_name}")
        print(f"     blocked: {blocked}")
        print(f"     reason : {t.reason}")
    print("")
    if watchlist:
        print("CANDIDATE WATCHLIST")
        print("-" * 100)
        for w in watchlist[:8]:
            print(f"{w.family_key:40s} status={w.recommended_status:24s} trades={w.trade_count:5d} pf={w.profit_factor:.3f} avg={w.avg_pnl:.6f}")
        print("")
    print(f"Open report: {out_dir / 'research_queue_report.md'}")
    print(f"Queue      : {out_dir / 'research_queue.json'}")
    print(f"CSV        : {out_dir / 'research_queue.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
