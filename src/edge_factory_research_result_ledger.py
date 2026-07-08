#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY RESEARCH RESULT LEDGER v1
======================================

Purpose
-------
Persistent research memory for the self-improving Edge Factory OS.

The self-improvement planner can produce a queue:
    - build modules
    - validate candidates
    - coin-subset robustness
    - wait for paper-dependent tasks

But a self-improving OS needs durable research memory:
    - What task was planned?
    - What result was recorded?
    - Which candidates were validated/rejected/promoted-to-watchlist?
    - Which evidence file supports that result?
    - Has the same task been repeated?
    - What is the current research backlog state?

This module provides that memory layer.

It DOES NOT:
    - start paper
    - start live
    - run loggers
    - run validators
    - mutate active trading config
    - promote strategies
    - change capital
    - run --apply

Default run
-----------
Bootstraps/updates the research task registry from latest:
    edge_factory_os_self_improvement_planner\self_improve_*\os_self_improvement_queue.json

Run:
    python "C:\Users\alike\edge_factory_research_result_ledger.py"

Record a research result manually/reference-only:
    python "C:\Users\alike\edge_factory_research_result_ledger.py" ^
      --record_result ^
      --task_id "validate_candidate_rel_extreme_reversion_short" ^
      --result_status "WATCHLIST" ^
      --score 0.0 ^
      --summary "placeholder summary" ^
      --evidence_path "C:\path\to\evidence.json"

Outputs
-------
    <workspace>\edge_factory_research_result_ledger\research_ledger_run_YYYYMMDD_HHMMSS\
        research_result_ledger_report.md
        research_result_ledger_state.json
        research_task_registry.csv
        research_result_history_tail.csv
        research_backlog.csv
        research_watchlist.csv
        research_rejections.csv

Persistent files
----------------
    <workspace>\edge_factory_research_result_ledger\master_research_result_ledger.jsonl
    <workspace>\edge_factory_research_result_ledger\master_research_result_ledger.csv
    <workspace>\edge_factory_research_result_ledger\master_research_task_registry.json
    <workspace>\edge_factory_research_result_ledger\master_research_task_registry.csv

Core principle
--------------
This is memory only. It records research state and evidence. It never changes the live/paper system.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

VALID_RESULT_STATUSES = {
    "UNTESTED",
    "PASS",
    "FAIL",
    "WATCHLIST",
    "REJECT",
    "NEEDS_MORE_DATA",
    "PROMOTION_CANDIDATE_REVIEW_ONLY",
    "DUPLICATE",
    "INCONCLUSIVE",
}

PROMOTION_FORBIDDEN_STATUSES = {
    "PROMOTE",
    "LIVE",
    "ENABLE_LIVE",
    "CHANGE_CAPITAL",
    "APPLY",
}


@dataclass
class QueueTask:
    task_id: str
    priority: int
    category: str
    status: str
    title: str
    reason: str
    target: str
    command: Optional[str]
    safe_offline: bool
    blocked_by: List[str]
    expected_output: str
    promotes_or_trades: bool
    first_seen_at: str
    last_seen_at: str
    source_queue_path: str


@dataclass
class ResearchResult:
    result_id: str
    recorded_at: str
    task_id: str
    result_status: str
    score: Optional[float]
    summary: str
    evidence_path: Optional[str]
    family: Optional[str]
    candidate: Optional[str]
    tags: List[str]
    source: str
    reviewer: str
    safe_for_auto_promotion: bool
    live_allowed: bool
    notes: str


@dataclass
class LedgerState:
    generated_at: str
    mode: str
    source_queue_path: Optional[str]
    queue_tasks_loaded: int
    registry_task_count: int
    ledger_result_count: int
    backlog_count: int
    watchlist_count: int
    rejection_count: int
    duplicate_task_count: int
    recorded_result_id: Optional[str]
    top_backlog_task: Optional[str]
    live_allowed: bool
    reasons: List[str]
    warnings: List[str]
    hard_rules: List[str]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


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


def optional_json(path: Optional[Path]) -> Any:
    if not path or not path.exists():
        return None
    try:
        return load_json(path)
    except Exception:
        return None


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def stable_hash(obj: Any) -> str:
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def discover_latest_self_improvement_queue(workspace: Path, explicit: Optional[Path]) -> Optional[Path]:
    if explicit:
        return explicit if explicit.exists() else None
    d = latest_child_dir(workspace / "edge_factory_os_self_improvement_planner", "self_improve_")
    if not d:
        return None
    p = d / "os_self_improvement_queue.json"
    return p if p.exists() else None


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows


def append_jsonl(path: Path, row: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")


def queue_task_from_row(row: Dict[str, Any], source_queue_path: Path, now: str, existing: Optional[Dict[str, Any]]) -> QueueTask:
    blocked = row.get("blocked_by")
    if isinstance(blocked, str):
        blocked_by = [x.strip() for x in blocked.split("|") if x.strip()]
    elif isinstance(blocked, list):
        blocked_by = [str(x) for x in blocked]
    else:
        blocked_by = []

    task_id = str(row.get("task_id", "unknown_task"))
    first_seen = str(existing.get("first_seen_at")) if existing else now

    return QueueTask(
        task_id=task_id,
        priority=int(row.get("priority", 999)),
        category=str(row.get("category", "UNKNOWN")),
        status=str(row.get("status", "UNKNOWN")),
        title=str(row.get("title", "")),
        reason=str(row.get("reason", "")),
        target=str(row.get("target", "")),
        command=str(row.get("command")) if row.get("command") else None,
        safe_offline=bool(row.get("safe_offline", True)),
        blocked_by=blocked_by,
        expected_output=str(row.get("expected_output", "")),
        promotes_or_trades=bool(row.get("promotes_or_trades", False)),
        first_seen_at=first_seen,
        last_seen_at=now,
        source_queue_path=str(source_queue_path),
    )


def load_registry(path: Path) -> Dict[str, Dict[str, Any]]:
    obj = optional_json(path)
    if isinstance(obj, dict):
        return {str(k): v for k, v in obj.items() if isinstance(v, dict)}
    return {}


def update_registry_from_queue(registry: Dict[str, Dict[str, Any]], queue_path: Optional[Path]) -> Tuple[Dict[str, Dict[str, Any]], int, List[str]]:
    warnings: List[str] = []
    if queue_path is None:
        warnings.append("No self-improvement queue found; registry was not updated from planner queue.")
        return registry, 0, warnings
    obj = optional_json(queue_path)
    if not isinstance(obj, list):
        warnings.append("Self-improvement queue JSON is not a list; registry was not updated.")
        return registry, 0, warnings
    now = datetime.now().isoformat(timespec="seconds")
    loaded = 0
    for row in obj:
        if not isinstance(row, dict):
            continue
        task_id = str(row.get("task_id", ""))
        if not task_id:
            continue
        existing = registry.get(task_id)
        task = queue_task_from_row(row, queue_path, now, existing)
        registry[task_id] = asdict(task)
        loaded += 1
    return registry, loaded, warnings


def validate_result_status(status: str) -> Tuple[str, List[str]]:
    warnings: List[str] = []
    normalized = status.strip().upper()
    if normalized in PROMOTION_FORBIDDEN_STATUSES:
        warnings.append(f"Forbidden result status '{status}' was converted to PROMOTION_CANDIDATE_REVIEW_ONLY.")
        return "PROMOTION_CANDIDATE_REVIEW_ONLY", warnings
    if normalized not in VALID_RESULT_STATUSES:
        warnings.append(f"Unknown result status '{status}' was converted to INCONCLUSIVE.")
        return "INCONCLUSIVE", warnings
    return normalized, warnings


def build_result(args: argparse.Namespace) -> Tuple[ResearchResult, List[str]]:
    status, warnings = validate_result_status(str(args.result_status or "INCONCLUSIVE"))
    tags = []
    if args.tags:
        tags = [x.strip() for x in str(args.tags).split(",") if x.strip()]
    raw = {
        "recorded_at": datetime.now().isoformat(timespec="seconds"),
        "task_id": str(args.task_id or "manual_result_without_task"),
        "result_status": status,
        "score": args.score,
        "summary": str(args.summary or ""),
        "evidence_path": str(args.evidence_path) if args.evidence_path else None,
        "family": str(args.family) if args.family else None,
        "candidate": str(args.candidate) if args.candidate else None,
        "tags": tags,
        "reviewer": str(args.reviewer),
    }
    result_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{stable_hash(raw)}"
    return ResearchResult(
        result_id=result_id,
        recorded_at=raw["recorded_at"],
        task_id=raw["task_id"],
        result_status=status,
        score=float(args.score) if args.score is not None else None,
        summary=raw["summary"],
        evidence_path=raw["evidence_path"],
        family=raw["family"],
        candidate=raw["candidate"],
        tags=tags,
        source="manual_record_result_cli",
        reviewer=str(args.reviewer),
        safe_for_auto_promotion=False,
        live_allowed=False,
        notes=str(args.notes or ""),
    ), warnings


def result_status_by_task(results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = {}
    for r in results:
        task_id = str(r.get("task_id", ""))
        if not task_id:
            continue
        out.setdefault(task_id, []).append(r)
    return out


def build_backlog(registry: Dict[str, Dict[str, Any]], results: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], int]:
    by_task = result_status_by_task(results)
    backlog: List[Dict[str, Any]] = []
    watchlist: List[Dict[str, Any]] = []
    rejections: List[Dict[str, Any]] = []
    duplicate_count = 0

    for task_id, task in registry.items():
        task_results = by_task.get(task_id, [])
        latest = task_results[-1] if task_results else None
        row = dict(task)
        row["result_count"] = len(task_results)
        row["latest_result_status"] = str(latest.get("result_status")) if latest else "UNTESTED"
        row["latest_result_id"] = str(latest.get("result_id")) if latest else ""
        if len(task_results) > 1:
            duplicate_count += 1
        if latest and str(latest.get("result_status")) in {"WATCHLIST", "PROMOTION_CANDIDATE_REVIEW_ONLY", "PASS", "NEEDS_MORE_DATA"}:
            watchlist.append(row)
        elif latest and str(latest.get("result_status")) in {"REJECT", "FAIL", "DUPLICATE"}:
            rejections.append(row)
        else:
            backlog.append(row)

    backlog.sort(key=lambda x: int(x.get("priority", 999)))
    watchlist.sort(key=lambda x: int(x.get("priority", 999)))
    rejections.sort(key=lambda x: int(x.get("priority", 999)))
    return backlog, watchlist, rejections, duplicate_count


def write_registry_csv(path: Path, registry: Dict[str, Dict[str, Any]]) -> None:
    rows = list(registry.values())
    if not rows:
        pd.DataFrame().to_csv(path, index=False)
        return
    df = pd.DataFrame(rows)
    if "blocked_by" in df.columns:
        df["blocked_by"] = df["blocked_by"].apply(lambda x: " | ".join(x) if isinstance(x, list) else x)
    df.to_csv(path, index=False)


def write_rows_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        pd.DataFrame().to_csv(path, index=False)
        return
    df = pd.DataFrame(rows)
    if "blocked_by" in df.columns:
        df["blocked_by"] = df["blocked_by"].apply(lambda x: " | ".join(x) if isinstance(x, list) else x)
    if "tags" in df.columns:
        df["tags"] = df["tags"].apply(lambda x: " | ".join(x) if isinstance(x, list) else x)
    df.to_csv(path, index=False)


def write_report(path: Path, state: LedgerState, registry: Dict[str, Dict[str, Any]], results: List[Dict[str, Any]], backlog: List[Dict[str, Any]], watchlist: List[Dict[str, Any]], rejections: List[Dict[str, Any]]) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory Research Result Ledger Report")
    lines.append("")
    lines.append(f"Generated: `{state.generated_at}`")
    lines.append(f"Mode: **{state.mode}**")
    lines.append(f"Source queue: `{state.source_queue_path}`")
    lines.append(f"Queue tasks loaded: **{state.queue_tasks_loaded}**")
    lines.append(f"Registry task count: **{state.registry_task_count}**")
    lines.append(f"Ledger result count: **{state.ledger_result_count}**")
    lines.append(f"Backlog count: **{state.backlog_count}**")
    lines.append(f"Watchlist count: **{state.watchlist_count}**")
    lines.append(f"Rejection count: **{state.rejection_count}**")
    lines.append(f"Top backlog task: **{state.top_backlog_task}**")
    lines.append(f"Live allowed: **{state.live_allowed}**")
    lines.append("")

    lines.append("## Reasons")
    lines.append("")
    for r in state.reasons:
        lines.append(f"- {r}")
    lines.append("")

    if state.warnings:
        lines.append("## Warnings")
        lines.append("")
        for w in state.warnings:
            lines.append(f"- {w}")
        lines.append("")

    lines.append("## Top backlog")
    lines.append("")
    if not backlog:
        lines.append("No backlog tasks.")
    else:
        lines.append("| Priority | Status | Category | Task | Target | Latest result |")
        lines.append("|---:|---:|---|---|---|---:|")
        for row in backlog[:30]:
            lines.append(f"| {row.get('priority')} | {row.get('status')} | {row.get('category')} | {row.get('task_id')} | {row.get('target')} | {row.get('latest_result_status')} |")
    lines.append("")

    lines.append("## Watchlist")
    lines.append("")
    if not watchlist:
        lines.append("No watchlist tasks yet.")
    else:
        lines.append("| Priority | Category | Task | Latest result |")
        lines.append("|---:|---|---|---:|")
        for row in watchlist[:30]:
            lines.append(f"| {row.get('priority')} | {row.get('category')} | {row.get('task_id')} | {row.get('latest_result_status')} |")
    lines.append("")

    lines.append("## Hard rules")
    lines.append("")
    for rule in state.hard_rules:
        lines.append(f"- {rule}")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("This module gives the self-improvement layer persistent memory. It records research tasks and results, but it cannot promote, trade, start paper/live, or alter active configuration.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Edge Factory research result ledger")
    parser.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    parser.add_argument("--queue", default=None)
    parser.add_argument("--out_dir", default=None)
    parser.add_argument("--record_result", action="store_true")
    parser.add_argument("--task_id", default=None)
    parser.add_argument("--result_status", default="INCONCLUSIVE")
    parser.add_argument("--score", type=float, default=None)
    parser.add_argument("--summary", default="")
    parser.add_argument("--evidence_path", default=None)
    parser.add_argument("--family", default=None)
    parser.add_argument("--candidate", default=None)
    parser.add_argument("--tags", default="")
    parser.add_argument("--reviewer", default="manual_user")
    parser.add_argument("--notes", default="")
    parser.add_argument("--no_append", action="store_true")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    root = workspace / "edge_factory_research_result_ledger"
    out_root = Path(args.out_dir) if args.out_dir else root
    out_dir = out_root / f"research_ledger_run_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    queue_path = discover_latest_self_improvement_queue(workspace, Path(args.queue) if args.queue else None)
    registry_path = root / "master_research_task_registry.json"
    registry_csv = root / "master_research_task_registry.csv"
    ledger_jsonl = root / "master_research_result_ledger.jsonl"
    ledger_csv = root / "master_research_result_ledger.csv"

    registry = load_registry(registry_path)
    registry, loaded_count, warnings = update_registry_from_queue(registry, queue_path)

    recorded_result: Optional[ResearchResult] = None
    if args.record_result:
        recorded_result, w = build_result(args)
        warnings.extend(w)
        if not args.no_append:
            append_jsonl(ledger_jsonl, asdict(recorded_result))

    results = read_jsonl(ledger_jsonl)
    backlog, watchlist, rejections, duplicate_count = build_backlog(registry, results)

    write_json(registry_path, registry)
    write_registry_csv(registry_csv, registry)
    write_rows_csv(ledger_csv, results)

    mode = "RECORD_RESULT" if args.record_result else "BOOTSTRAP_OR_SYNC_REGISTRY"
    reasons = []
    if queue_path:
        reasons.append("Research task registry was synchronized from latest self-improvement planner queue.")
    else:
        reasons.append("No planner queue found; ledger maintained existing registry only.")
    if recorded_result:
        reasons.append(f"Research result recorded: {recorded_result.result_id} status={recorded_result.result_status}.")
    else:
        reasons.append("No research result was recorded in this run.")

    state = LedgerState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        mode=mode,
        source_queue_path=str(queue_path) if queue_path else None,
        queue_tasks_loaded=loaded_count,
        registry_task_count=len(registry),
        ledger_result_count=len(results),
        backlog_count=len(backlog),
        watchlist_count=len(watchlist),
        rejection_count=len(rejections),
        duplicate_task_count=duplicate_count,
        recorded_result_id=recorded_result.result_id if recorded_result else None,
        top_backlog_task=str(backlog[0].get("task_id")) if backlog else None,
        live_allowed=False,
        reasons=reasons,
        warnings=warnings,
        hard_rules=[
            "Research ledger never starts paper/live.",
            "Research ledger never mutates active trading config.",
            "Research ledger never promotes candidates automatically.",
            "Recorded statuses are memory only; promotion requires separate sandbox and manual review.",
            "Live remains blocked.",
        ],
    )

    result_obj = {
        "state": asdict(state),
        "recorded_result": asdict(recorded_result) if recorded_result else None,
        "registry_task_count": len(registry),
        "ledger_result_count": len(results),
        "backlog": backlog,
        "watchlist": watchlist,
        "rejections": rejections,
    }
    write_json(out_dir / "research_result_ledger_state.json", result_obj)
    write_registry_csv(out_dir / "research_task_registry.csv", registry)
    write_rows_csv(out_dir / "research_result_history_tail.csv", results[-100:])
    write_rows_csv(out_dir / "research_backlog.csv", backlog)
    write_rows_csv(out_dir / "research_watchlist.csv", watchlist)
    write_rows_csv(out_dir / "research_rejections.csv", rejections)
    write_report(out_dir / "research_result_ledger_report.md", state, registry, results, backlog, watchlist, rejections)

    print("EDGE FACTORY RESEARCH RESULT LEDGER v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"output_dir: {out_dir}")
    print(f"mode      : {state.mode}")
    print(f"source_queue: {state.source_queue_path}")
    print(f"queue_tasks_loaded: {state.queue_tasks_loaded}")
    print(f"registry_task_count: {state.registry_task_count}")
    print(f"ledger_result_count: {state.ledger_result_count}")
    print(f"backlog_count: {state.backlog_count}")
    print(f"watchlist_count: {state.watchlist_count}")
    print(f"rejection_count: {state.rejection_count}")
    print(f"top_backlog_task: {state.top_backlog_task}")
    print("live_allowed: False")
    print("")
    print("REASONS")
    print("-" * 100)
    for r in state.reasons:
        print(f"- {r}")
    if state.warnings:
        print("")
        print("WARNINGS")
        print("-" * 100)
        for w in state.warnings:
            print(f"- {w}")
    print("")
    print("TOP BACKLOG")
    print("-" * 100)
    for row in backlog[:15]:
        print(f"P{int(row.get('priority', 999)):03d} [{row.get('status')}] {row.get('category')} -> {row.get('task_id')}")
        print(f"     target: {row.get('target')}")
        print(f"     latest_result: {row.get('latest_result_status')}")
    print("")
    print("IMPORTANT")
    print("-" * 100)
    print("This module did not start paper/live, did not mutate config, and did not promote any strategy.")
    print("")
    print(f"Report  : {out_dir / 'research_result_ledger_report.md'}")
    print(f"State   : {out_dir / 'research_result_ledger_state.json'}")
    print(f"Registry: {registry_path}")
    print(f"Ledger  : {ledger_jsonl}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
