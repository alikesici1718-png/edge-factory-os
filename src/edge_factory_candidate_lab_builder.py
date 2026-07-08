#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY CANDIDATE LAB BUILDER v1
=====================================

Purpose
-------
Create isolated research labs/sandboxes for candidate strategy families.

This is part of the Edge Factory self-improvement layer. It converts the research
backlog/watchlist into safe, isolated lab folders where future validators can write
results without touching the active MASTER_UPPER_SYSTEM.

It DOES NOT:
    - start paper
    - start live
    - run loggers
    - mutate active config
    - promote strategies
    - change capital
    - run --apply
    - execute candidate validators

It DOES:
    - read the research result ledger registry/backlog
    - read OOS v2 candidate hints if available
    - create isolated lab folders under edge_factory_candidate_lab
    - write manifests, validation plans, README files, and placeholder configs
    - emit a lab index and next-action queue

Run:
    python "C:\Users\alike\edge_factory_candidate_lab_builder.py"

Optional filters:
    python "C:\Users\alike\edge_factory_candidate_lab_builder.py" --candidate rel_extreme_reversion_short
    python "C:\Users\alike\edge_factory_candidate_lab_builder.py" --max_candidates 3

Outputs:
    <workspace>\edge_factory_candidate_lab\lab_build_YYYYMMDD_HHMMSS\
        candidate_lab_builder_report.md
        candidate_lab_builder_state.json
        candidate_lab_index.csv
        candidate_lab_next_actions.csv

Persistent lab root:
    <workspace>\edge_factory_candidate_lab\labs\<candidate_key>\
        README.md
        candidate_manifest.json
        validation_plan.md
        research_config_stub.json
        results\
        artifacts\
        logs\
        notes\

Core principle
--------------
Candidate labs are quarantine zones. Nothing created here is active trading config.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_SCRIPT_DIR = Path(r"C:\Users\alike")

RESEARCH_CANDIDATE_HINTS = [
    "rel_extreme_reversion_short",
    "ret60_reversal_short",
    "relative_weakness_snapback_long",
    "market_panic_rebound_long",
    "capitulation_reversal_long",
]

ACTIVE_FAMILIES = {"old_short", "impulse_long", "market_relative_short", "weak_market_short"}
DISABLED_FAMILIES = {"session_short"}


@dataclass
class CandidateSource:
    candidate_key: str
    source: str
    source_task_id: Optional[str]
    priority: int
    category: str
    status: str
    reason: str
    target: str


@dataclass
class LabRecord:
    candidate_key: str
    lab_dir: str
    created_or_updated: str
    source: str
    source_task_id: Optional[str]
    priority: int
    category: str
    status: str
    is_active_family: bool
    is_disabled_family: bool
    validation_status: str
    next_action: str
    safe_offline: bool
    promotes_or_trades: bool


@dataclass
class BuilderState:
    generated_at: str
    workspace: str
    lab_root: str
    source_registry: Optional[str]
    candidates_seen: int
    labs_created_or_updated: int
    active_family_count: int
    research_candidate_count: int
    skipped_count: int
    live_allowed: bool
    reasons: List[str]
    warnings: List[str]
    hard_rules: List[str]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_key(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9_\-]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "unknown_candidate"


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


def latest_child_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def discover_registry(workspace: Path, explicit: Optional[Path]) -> Optional[Path]:
    if explicit:
        return explicit if explicit.exists() else None
    p = workspace / "edge_factory_research_result_ledger" / "master_research_task_registry.json"
    return p if p.exists() else None


def discover_latest_oos_v2(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_rolling_oos_validator_v2", "rolling_oos_v2_")
    if not d:
        return None
    p = d / "clean_os_family_state_seed.json"
    return p if p.exists() else None


def registry_candidates(registry_path: Optional[Path]) -> List[CandidateSource]:
    obj = optional_json(registry_path)
    if not isinstance(obj, dict):
        return []
    out: List[CandidateSource] = []
    for task_id, row in obj.items():
        if not isinstance(row, dict):
            continue
        category = str(row.get("category", ""))
        target = str(row.get("target", ""))
        title = str(row.get("title", ""))
        status = str(row.get("status", ""))
        if category not in {"CANDIDATE_VALIDATION", "ACTIVE_FAMILY_ROBUSTNESS"}:
            continue
        key = safe_key(target or task_id)
        if not key:
            continue
        out.append(CandidateSource(
            candidate_key=key,
            source="research_task_registry",
            source_task_id=str(task_id),
            priority=int(row.get("priority", 999)),
            category=category,
            status=status,
            reason=str(row.get("reason", title)),
            target=target,
        ))
    return out


def oos_hint_candidates(workspace: Path) -> List[CandidateSource]:
    # Conservative fallback: use known OOS v2 candidates from planner output.
    out: List[CandidateSource] = []
    for i, name in enumerate(RESEARCH_CANDIDATE_HINTS, start=1):
        out.append(CandidateSource(
            candidate_key=safe_key(name),
            source="oos_v2_known_candidate_hint",
            source_task_id=None,
            priority=100 + i,
            category="CANDIDATE_VALIDATION",
            status="WAITING_FOR_MODULE",
            reason="Known research candidate from rolling OOS v2 cleanup; lab created for isolated validation.",
            target=name,
        ))
    return out


def merge_candidates(items: List[CandidateSource]) -> List[CandidateSource]:
    best: Dict[str, CandidateSource] = {}
    for item in items:
        key = safe_key(item.candidate_key)
        if key not in best or item.priority < best[key].priority:
            best[key] = item
    return sorted(best.values(), key=lambda x: (x.priority, x.candidate_key))


def read_existing_manifest(lab_dir: Path) -> Dict[str, Any]:
    p = lab_dir / "candidate_manifest.json"
    obj = optional_json(p)
    return obj if isinstance(obj, dict) else {}


def write_readme(path: Path, rec: LabRecord) -> None:
    lines = [
        f"# Candidate Lab: `{rec.candidate_key}`",
        "",
        "This is an isolated research sandbox created by Edge Factory Candidate Lab Builder.",
        "",
        "## Safety",
        "",
        "- This lab is not active trading config.",
        "- Nothing here starts paper/live.",
        "- Nothing here promotes a family.",
        "- Results must be written to the research result ledger before any later review.",
        "",
        "## Current state",
        "",
        f"- Source: `{rec.source}`",
        f"- Source task: `{rec.source_task_id}`",
        f"- Category: `{rec.category}`",
        f"- Status: `{rec.status}`",
        f"- Validation status: `{rec.validation_status}`",
        f"- Next action: `{rec.next_action}`",
        "",
        "## Directory layout",
        "",
        "- `results/` validator outputs go here.",
        "- `artifacts/` generated research artifacts go here.",
        "- `logs/` run logs go here.",
        "- `notes/` manual notes go here.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_validation_plan(path: Path, candidate_key: str, is_active: bool) -> None:
    title = "Active family robustness plan" if is_active else "Research candidate validation plan"
    lines = [
        f"# {title}: `{candidate_key}`",
        "",
        "## Required gates before any promotion discussion",
        "",
        "1. Time out-of-sample split.",
        "2. Rolling window stability.",
        "3. Coin-subset robustness / coin-family fit.",
        "4. Fee, spread, and slippage realism.",
        "5. Parameter sensitivity.",
        "6. Monthly / regime stability.",
        "7. Paper-vs-backtest drift if it ever reaches paper.",
        "8. Manual review. No automatic promotion.",
        "",
        "## Kill criteria",
        "",
        "- Single-period dependency.",
        "- Tiny edge erased by fees/slippage.",
        "- Only works on one symbol without a clear reason.",
        "- Unstable parameter island.",
        "- Bad live/paper drift.",
        "",
        "## Output contract",
        "",
        "Validator outputs should write a summary JSON/CSV under `results/` and then record a result through `edge_factory_research_result_ledger.py`.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_config_stub(path: Path, src: CandidateSource, lab_dir: Path) -> None:
    obj = {
        "candidate_key": src.candidate_key,
        "source": src.source,
        "source_task_id": src.source_task_id,
        "category": src.category,
        "target": src.target,
        "status": src.status,
        "lab_dir": str(lab_dir),
        "active_config": False,
        "paper_enabled": False,
        "live_enabled": False,
        "promotion_allowed": False,
        "notes": "Research-only config stub. Validators may read this, but active system must not.",
    }
    write_json(path, obj)


def build_lab(workspace: Path, lab_root: Path, src: CandidateSource, overwrite: bool) -> LabRecord:
    key = safe_key(src.candidate_key)
    lab_dir = lab_root / "labs" / key
    lab_dir.mkdir(parents=True, exist_ok=True)
    for sub in ["results", "artifacts", "logs", "notes"]:
        (lab_dir / sub).mkdir(parents=True, exist_ok=True)

    existing = read_existing_manifest(lab_dir)
    created_at = existing.get("created_at") or datetime.now().isoformat(timespec="seconds")
    updated_at = datetime.now().isoformat(timespec="seconds")
    is_active = key in ACTIVE_FAMILIES
    is_disabled = key in DISABLED_FAMILIES
    validation_status = "LAB_READY_ACTIVE_FAMILY_ROBUSTNESS" if is_active else "LAB_READY_RESEARCH_CANDIDATE"
    if is_disabled:
        validation_status = "LAB_READY_DISABLED_REFERENCE_ONLY"
    next_action = "RUN_ACTIVE_FAMILY_ROBUSTNESS_VALIDATOR" if is_active else "RUN_RESEARCH_CANDIDATE_VALIDATOR"

    rec = LabRecord(
        candidate_key=key,
        lab_dir=str(lab_dir),
        created_or_updated=updated_at,
        source=src.source,
        source_task_id=src.source_task_id,
        priority=src.priority,
        category=src.category,
        status=src.status,
        is_active_family=is_active,
        is_disabled_family=is_disabled,
        validation_status=validation_status,
        next_action=next_action,
        safe_offline=True,
        promotes_or_trades=False,
    )

    manifest = {
        "candidate_key": key,
        "created_at": created_at,
        "updated_at": updated_at,
        "source": asdict(src),
        "lab_record": asdict(rec),
        "safety": {
            "active_config": False,
            "paper_enabled": False,
            "live_enabled": False,
            "promotion_allowed": False,
            "mutates_active_system": False,
        },
    }
    write_json(lab_dir / "candidate_manifest.json", manifest)
    write_readme(lab_dir / "README.md", rec)
    write_validation_plan(lab_dir / "validation_plan.md", key, is_active)
    write_config_stub(lab_dir / "research_config_stub.json", src, lab_dir)
    return rec


def records_df(records: List[LabRecord]) -> pd.DataFrame:
    return pd.DataFrame([asdict(r) for r in records])


def write_next_actions(path: Path, records: List[LabRecord]) -> None:
    rows = []
    for r in records:
        rows.append({
            "priority": r.priority,
            "candidate_key": r.candidate_key,
            "status": "READY_FOR_VALIDATOR_MODULE",
            "next_action": r.next_action,
            "lab_dir": r.lab_dir,
            "blocked_by": "research_candidate_validator" if not r.is_active_family else "coin_subset_validator",
            "safe_offline": True,
            "promotes_or_trades": False,
        })
    pd.DataFrame(rows).to_csv(path, index=False)


def write_report(path: Path, state: BuilderState, records: List[LabRecord]) -> None:
    lines = [
        "# Edge Factory Candidate Lab Builder Report",
        "",
        f"Generated: `{state.generated_at}`",
        f"Lab root: `{state.lab_root}`",
        f"Candidates seen: **{state.candidates_seen}**",
        f"Labs created/updated: **{state.labs_created_or_updated}**",
        f"Active family labs: **{state.active_family_count}**",
        f"Research candidate labs: **{state.research_candidate_count}**",
        f"Live allowed: **{state.live_allowed}**",
        "",
        "## Reasons",
        "",
    ]
    for r in state.reasons:
        lines.append(f"- {r}")
    if state.warnings:
        lines += ["", "## Warnings", ""]
        for w in state.warnings:
            lines.append(f"- {w}")
    lines += ["", "## Labs", ""]
    if records:
        lines += ["| Priority | Candidate | Category | Validation status | Lab |", "|---:|---|---|---|---|"]
        for r in records:
            lines.append(f"| {r.priority} | {r.candidate_key} | {r.category} | {r.validation_status} | `{r.lab_dir}` |")
    else:
        lines.append("No labs created.")
    lines += ["", "## Hard rules", ""]
    for rule in state.hard_rules:
        lines.append(f"- {rule}")
    lines += ["", "## Interpretation", "", "Candidate labs are isolated research sandboxes. They are not active trading configuration and cannot promote or trade by themselves.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory candidate lab builder")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--registry", default=None)
    p.add_argument("--candidate", default=None)
    p.add_argument("--max_candidates", type=int, default=50)
    p.add_argument("--out_dir", default=None)
    p.add_argument("--overwrite", action="store_true")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    lab_root = workspace / "edge_factory_candidate_lab"
    out_root = Path(args.out_dir) if args.out_dir else lab_root
    out_dir = out_root / f"lab_build_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    registry_path = discover_registry(workspace, Path(args.registry) if args.registry else None)
    candidates = registry_candidates(registry_path)
    if not candidates:
        candidates = oos_hint_candidates(workspace)
    else:
        # Add hints too; merge will remove duplicates and prefer registry priority.
        candidates.extend(oos_hint_candidates(workspace))
    candidates = merge_candidates(candidates)

    if args.candidate:
        wanted = safe_key(args.candidate)
        candidates = [c for c in candidates if safe_key(c.candidate_key) == wanted or safe_key(c.target) == wanted]

    max_candidates = max(1, int(args.max_candidates))
    selected = candidates[:max_candidates]

    records: List[LabRecord] = []
    warnings: List[str] = []
    for src in selected:
        try:
            records.append(build_lab(workspace, lab_root, src, bool(args.overwrite)))
        except Exception as e:
            warnings.append(f"failed to build lab for {src.candidate_key}: {e}")

    active_count = len([r for r in records if r.is_active_family])
    research_count = len([r for r in records if not r.is_active_family])
    state = BuilderState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        lab_root=str(lab_root),
        source_registry=str(registry_path) if registry_path else None,
        candidates_seen=len(candidates),
        labs_created_or_updated=len(records),
        active_family_count=active_count,
        research_candidate_count=research_count,
        skipped_count=max(0, len(candidates) - len(selected)),
        live_allowed=False,
        reasons=[
            "Candidate labs were built from the research task registry and OOS v2 candidate hints.",
            "Labs are isolated from active MASTER_UPPER_SYSTEM config.",
        ],
        warnings=warnings,
        hard_rules=[
            "Candidate lab builder never starts paper/live.",
            "Candidate lab builder never mutates active trading config.",
            "Candidate lab builder never promotes candidates automatically.",
            "All labs are research-only quarantine zones.",
            "Live remains blocked.",
        ],
    )

    result = {
        "state": asdict(state),
        "labs": [asdict(r) for r in records],
    }
    write_json(out_dir / "candidate_lab_builder_state.json", result)
    records_df(records).to_csv(out_dir / "candidate_lab_index.csv", index=False)
    write_next_actions(out_dir / "candidate_lab_next_actions.csv", records)
    write_report(out_dir / "candidate_lab_builder_report.md", state, records)

    # Persistent index.
    persistent_index = lab_root / "candidate_lab_master_index.csv"
    records_df(records).to_csv(persistent_index, index=False)

    print("EDGE FACTORY CANDIDATE LAB BUILDER v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"lab_root  : {lab_root}")
    print(f"output_dir: {out_dir}")
    print(f"source_registry: {state.source_registry}")
    print(f"candidates_seen: {state.candidates_seen}")
    print(f"labs_created_or_updated: {state.labs_created_or_updated}")
    print(f"active_family_count: {state.active_family_count}")
    print(f"research_candidate_count: {state.research_candidate_count}")
    print("live_allowed: False")
    print("")
    print("LABS")
    print("-" * 100)
    for r in records[:30]:
        print(f"P{r.priority:03d} {r.candidate_key:40s} {r.validation_status}")
        print(f"     lab: {r.lab_dir}")
        print(f"     next: {r.next_action}")
    if warnings:
        print("")
        print("WARNINGS")
        print("-" * 100)
        for w in warnings:
            print(f"- {w}")
    print("")
    print("IMPORTANT")
    print("-" * 100)
    print("This module did not start paper/live, did not mutate active config, and did not promote any strategy.")
    print("")
    print(f"Report : {out_dir / 'candidate_lab_builder_report.md'}")
    print(f"State  : {out_dir / 'candidate_lab_builder_state.json'}")
    print(f"Index  : {out_dir / 'candidate_lab_index.csv'}")
    print(f"Master : {persistent_index}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
