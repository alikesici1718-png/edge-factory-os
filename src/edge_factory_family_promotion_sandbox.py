#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY FAMILY PROMOTION SANDBOX v1
========================================

Purpose
-------
Create isolated promotion sandboxes for research candidates that passed evidence synthesis.

This module is the next OS layer after:
    - schema-aware validator v2
    - candle universe inventory v2
    - rolling/time-OOS validator
    - evidence synthesis engine

It is built for decisions like:
    ret60_reversal_short -> PROMOTION_SANDBOX_CANDIDATE

It DOES NOT:
    - start paper
    - start live
    - run loggers
    - mutate active config
    - edit the sizing contract
    - promote strategies
    - change capital
    - run --apply

It DOES:
    - read latest evidence synthesis decisions
    - find PROMOTION_SANDBOX_CANDIDATE rows
    - create isolated sandbox folders
    - write sandbox manifests and validation gates
    - write a shadow-paper research plan, reference-only
    - write required checks before any future paper inclusion
    - optionally append evidence-only records to the research ledger

Run:
    python "C:\Users\alike\edge_factory_family_promotion_sandbox.py"

Run one candidate:
    python "C:\Users\alike\edge_factory_family_promotion_sandbox.py" --candidate ret60_reversal_short

Core rule
---------
Sandbox means quarantine. A sandbox candidate is not active, not paper-enabled, and not live-enabled.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_SCRIPT_DIR = Path(r"C:\Users\alike")

ACTIVE_FAMILIES = {"old_short", "impulse_long", "market_relative_short", "weak_market_short", "session_short"}
PROMOTION_DECISION = "PROMOTION_SANDBOX_CANDIDATE"


@dataclass
class CandidateEvidence:
    candidate_key: str
    role: str
    os_decision: str
    schema_status: str
    time_status: str
    schema_clean_rows: Optional[int]
    schema_symbols: Optional[int]
    schema_pf: Optional[float]
    time_clean_rows: Optional[int]
    time_valid_folds: Optional[int]
    time_pos_fold_rate: Optional[float]
    time_month_pos_rate: Optional[float]
    time_test_total: Optional[float]
    time_test_pf: Optional[float]
    time_worst_fold: Optional[float]
    paper_permission_hint: str
    promotion_permission_hint: str
    source_decisions_path: str


@dataclass
class SandboxGate:
    gate_id: str
    category: str
    required: bool
    passed: bool
    status: str
    reason: str


@dataclass
class SandboxRecord:
    candidate_key: str
    sandbox_status: str
    sandbox_dir: str
    persistent_dir: str
    evidence_score: float
    gate_passed_required: int
    gate_total_required: int
    shadow_paper_allowed: bool
    active_paper_allowed: bool
    live_allowed: bool
    next_action: str
    reasons: List[str]
    warnings: List[str]


@dataclass
class SandboxState:
    generated_at: str
    workspace: str
    source_decisions_path: Optional[str]
    candidates_seen: int
    sandboxes_created: int
    shadow_paper_allowed_count: int
    active_paper_allowed_count: int
    live_allowed: bool
    overall_state: str
    reasons: List[str]
    warnings: List[str]
    hard_rules: List[str]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def stable_hash(obj: Any) -> str:
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def safe_key(x: Any) -> str:
    return str(x or "").strip().lower().replace(" ", "_")


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


def read_csv_optional(path: Optional[Path]) -> pd.DataFrame:
    if not path or not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def latest_synthesis_decisions(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_evidence_synthesis_engine", "evidence_synthesis_")
    if not d:
        return None
    p = d / "evidence_synthesis_decisions.csv"
    return p if p.exists() else None


def latest_synthesis_state(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_evidence_synthesis_engine", "evidence_synthesis_")
    if not d:
        return None
    p = d / "evidence_synthesis_state.json"
    return p if p.exists() else None


def latest_schema_v2_summary(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_schema_aware_validator_v2", "schema_aware_v2_")
    if not d:
        return None
    p = d / "schema_aware_validator_v2_summary.csv"
    return p if p.exists() else None


def latest_rolling_summary(workspace: Path) -> Optional[Path]:
    root = workspace / "edge_factory_rolling_retrain_validator"
    if not root.exists():
        return None
    paths = [p for p in root.rglob("rolling_time_oos_summary.csv") if p.exists()]
    if not paths:
        return None
    return sorted(paths, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def latest_candle_inventory_state(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_candle_universe_inventory_v2", "candle_inventory_v2_")
    if not d:
        return None
    p = d / "candle_universe_inventory_v2_state.json"
    return p if p.exists() else None


def to_int(x: Any) -> Optional[int]:
    try:
        if pd.isna(x):
            return None
        return int(float(x))
    except Exception:
        return None


def to_float(x: Any) -> Optional[float]:
    try:
        if pd.isna(x):
            return None
        return float(x)
    except Exception:
        return None


def load_candidates(workspace: Path, candidate_filter: Optional[str]) -> List[CandidateEvidence]:
    decisions_path = latest_synthesis_decisions(workspace)
    df = read_csv_optional(decisions_path)
    if df.empty:
        return []
    rows: List[CandidateEvidence] = []
    for _, row in df.iterrows():
        key = safe_key(row.get("target_key"))
        if candidate_filter and key != safe_key(candidate_filter):
            continue
        if str(row.get("os_decision", "")) != PROMOTION_DECISION:
            continue
        if key in ACTIVE_FAMILIES:
            continue
        rows.append(CandidateEvidence(
            candidate_key=key,
            role=str(row.get("role", "RESEARCH_CANDIDATE")),
            os_decision=str(row.get("os_decision", "")),
            schema_status=str(row.get("schema_status", "")),
            time_status=str(row.get("time_status", "")),
            schema_clean_rows=to_int(row.get("schema_clean_rows")),
            schema_symbols=to_int(row.get("schema_symbols")),
            schema_pf=to_float(row.get("schema_pf")),
            time_clean_rows=to_int(row.get("time_clean_rows")),
            time_valid_folds=to_int(row.get("time_valid_folds")),
            time_pos_fold_rate=to_float(row.get("time_pos_fold_rate")),
            time_month_pos_rate=to_float(row.get("time_month_pos_rate")),
            time_test_total=to_float(row.get("time_test_total")),
            time_test_pf=to_float(row.get("time_test_pf")),
            time_worst_fold=to_float(row.get("time_worst_fold")),
            paper_permission_hint=str(row.get("paper_permission_hint", "")),
            promotion_permission_hint=str(row.get("promotion_permission_hint", "")),
            source_decisions_path=str(decisions_path),
        ))
    return rows


def evidence_score(ev: CandidateEvidence) -> float:
    score = 0.0
    if ev.schema_status == "ROBUST_COIN_FIT_SCHEMA_CLEAN":
        score += 25
    elif "CONCENTRATED" in ev.schema_status:
        score += 10
    if ev.time_status == "TIME_OOS_PASS":
        score += 35
    elif ev.time_status == "TIME_OOS_WATCHLIST":
        score += 15
    if ev.schema_symbols and ev.schema_symbols >= 50:
        score += 15
    elif ev.schema_symbols and ev.schema_symbols >= 10:
        score += 5
    if ev.time_valid_folds and ev.time_valid_folds >= 4:
        score += 10
    if ev.time_pos_fold_rate is not None and ev.time_pos_fold_rate >= 0.70:
        score += 10
    elif ev.time_pos_fold_rate is not None and ev.time_pos_fold_rate >= 0.55:
        score += 5
    if ev.time_test_total is not None and ev.time_test_total > 0:
        score += 5
    return round(score, 4)


def build_gates(ev: CandidateEvidence, workspace: Path) -> List[SandboxGate]:
    gates: List[SandboxGate] = []

    def add(gate_id: str, category: str, required: bool, passed: bool, reason: str) -> None:
        gates.append(SandboxGate(
            gate_id=gate_id,
            category=category,
            required=required,
            passed=bool(passed),
            status="PASS" if passed else "FAIL",
            reason=reason,
        ))

    add("not_active_family", "safety", True, ev.candidate_key not in ACTIVE_FAMILIES, "candidate must not already be an active family")
    add("synthesis_decision", "evidence", True, ev.os_decision == PROMOTION_DECISION, "evidence synthesis must mark candidate as promotion sandbox candidate")
    add("schema_clean_robust", "evidence", True, ev.schema_status == "ROBUST_COIN_FIT_SCHEMA_CLEAN", "candidate must pass schema-aware robust coin-fit evidence")
    add("time_oos_pass", "evidence", True, ev.time_status == "TIME_OOS_PASS", "candidate must pass rolling/time-OOS evidence")
    add("enough_clean_rows", "evidence", True, (ev.time_clean_rows or 0) >= 300, "candidate should have at least 300 clean time-OOS rows for sandbox")
    add("enough_symbols", "evidence", True, (ev.schema_symbols or 0) >= 50, "candidate should have broad enough symbol coverage")
    add("enough_folds", "evidence", True, (ev.time_valid_folds or 0) >= 4, "candidate should have at least 4 valid time-OOS folds")
    add("positive_fold_rate", "evidence", True, (ev.time_pos_fold_rate or 0.0) >= 0.55, "positive time-OOS fold rate must be acceptable")
    add("positive_test_total", "evidence", True, (ev.time_test_total or 0.0) > 0, "time-OOS test total must be positive")
    add("worst_fold_not_catastrophic", "risk", True, (ev.time_worst_fold is not None and ev.time_worst_fold > -100.0), "worst fold must not be catastrophic at research scale")
    add("schema_v2_summary_exists", "artifact", True, latest_schema_v2_summary(workspace) is not None, "schema-aware v2 summary must exist")
    add("rolling_summary_exists", "artifact", True, latest_rolling_summary(workspace) is not None, "rolling/time-OOS summary must exist")
    add("candle_inventory_v2_exists", "artifact", True, latest_candle_inventory_state(workspace) is not None, "candle universe inventory v2 must exist")
    add("live_blocked", "safety", True, True, "live must remain blocked")
    add("active_paper_not_allowed_yet", "safety", True, True, "candidate must not be inserted into active paper before sandbox review")
    return gates


def write_markdown(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_sandbox_files(workspace: Path, out_dir: Path, ev: CandidateEvidence, gates: List[SandboxGate], stamp: str) -> SandboxRecord:
    root = workspace / "edge_factory_family_promotion_sandbox"
    persistent = root / "sandboxes" / ev.candidate_key
    run_dir = out_dir / "sandboxes" / ev.candidate_key
    persistent.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    for sub in ["evidence", "shadow_plan", "results", "notes", "logs"]:
        (persistent / sub).mkdir(parents=True, exist_ok=True)
        (run_dir / sub).mkdir(parents=True, exist_ok=True)

    required = [g for g in gates if g.required]
    passed_required = [g for g in required if g.passed]
    all_required_passed = len(passed_required) == len(required)
    score = evidence_score(ev)

    warnings: List[str] = []
    reasons: List[str] = []
    if all_required_passed:
        sandbox_status = "SANDBOX_READY_REVIEW_ONLY"
        shadow_allowed = True
        next_action = "BUILD_SHADOW_PAPER_RESEARCH_PLAN_OR_VALIDATOR"
        reasons.append("all required sandbox gates passed")
    else:
        sandbox_status = "SANDBOX_BLOCKED_GATES_FAILED"
        shadow_allowed = False
        next_action = "REPAIR_FAILED_GATES_BEFORE_SANDBOX"
        warnings.append("one or more required sandbox gates failed")
    if ev.time_worst_fold is not None and ev.time_worst_fold < 0:
        warnings.append(f"candidate has negative worst fold: {ev.time_worst_fold}")

    active_paper_allowed = False
    live_allowed = False

    manifest = {
        "candidate_evidence": asdict(ev),
        "sandbox_status": sandbox_status,
        "evidence_score": score,
        "gates": [asdict(g) for g in gates],
        "permissions": {
            "shadow_paper_allowed_reference_only": shadow_allowed,
            "active_paper_allowed": active_paper_allowed,
            "live_allowed": live_allowed,
            "mutates_active_config": False,
            "changes_sizing_contract": False,
            "promotion_applied": False,
        },
        "paths": {
            "persistent_dir": str(persistent),
            "run_dir": str(run_dir),
        },
    }
    write_json(persistent / "sandbox_manifest.json", manifest)
    write_json(run_dir / "sandbox_manifest.json", manifest)

    gates_df = pd.DataFrame([asdict(g) for g in gates])
    gates_df.to_csv(persistent / "sandbox_gates.csv", index=False)
    gates_df.to_csv(run_dir / "sandbox_gates.csv", index=False)

    readme = f"""# Promotion Sandbox: `{ev.candidate_key}`

Status: **{sandbox_status}**

This sandbox is isolated. It is not active paper and not live.

## Evidence

- Schema status: `{ev.schema_status}`
- Time-OOS status: `{ev.time_status}`
- Schema clean rows: `{ev.schema_clean_rows}`
- Schema symbols: `{ev.schema_symbols}`
- Time clean rows: `{ev.time_clean_rows}`
- Time valid folds: `{ev.time_valid_folds}`
- Positive fold rate: `{ev.time_pos_fold_rate}`
- Test total: `{ev.time_test_total}`
- Test PF: `{ev.time_test_pf}`
- Worst fold: `{ev.time_worst_fold}`
- Evidence score: `{score}`

## Permissions

- Shadow paper reference allowed: `{shadow_allowed}`
- Active paper allowed: `False`
- Live allowed: `False`
- Active config mutation: `False`

## Next action

`{next_action}`

## Required rule

Do not add this family to MASTER_UPPER_SYSTEM until a future sandbox-specific paper/research plan passes and the user manually approves.
"""
    write_markdown(persistent / "README.md", readme)
    write_markdown(run_dir / "README.md", readme)

    plan = f"""# Shadow Paper Research Plan - `{ev.candidate_key}`

This is a reference-only plan. It does not start anything.

## Goal

Test `{ev.candidate_key}` in quarantine before any active paper inclusion.

## Required future modules/checks

1. Build a candidate-specific signal/logger adapter in sandbox only.
2. Verify native execution fields are logged.
3. Run shadow paper without touching MASTER_UPPER_SYSTEM.
4. Compare shadow paper vs schema-clean backtest.
5. Run drift monitor on candidate-specific closed paper trades.
6. Re-run evidence synthesis with sandbox results.
7. Manual review before any active paper inclusion.

## Current prohibition

- Do not edit `position_sizing_contract.json`.
- Do not edit `start_edge_factory_MASTER_UPPER_SYSTEM.ps1`.
- Do not add candidate logger to active launcher.
- Do not permit live.
"""
    write_markdown(persistent / "shadow_plan" / "shadow_paper_research_plan.md", plan)
    write_markdown(run_dir / "shadow_plan" / "shadow_paper_research_plan.md", plan)

    reference_ps1 = f"""# REFERENCE ONLY - DO NOT EXECUTE AS ACTIVE SYSTEM
# Candidate: {ev.candidate_key}
# This file is intentionally comments only.
# Future sandbox-only launcher can be generated after a candidate logger adapter exists.
# No command is approved yet.
"""
    write_markdown(persistent / "shadow_plan" / "shadow_paper_REFERENCE_ONLY.ps1", reference_ps1)
    write_markdown(run_dir / "shadow_plan" / "shadow_paper_REFERENCE_ONLY.ps1", reference_ps1)

    return SandboxRecord(
        candidate_key=ev.candidate_key,
        sandbox_status=sandbox_status,
        sandbox_dir=str(run_dir),
        persistent_dir=str(persistent),
        evidence_score=score,
        gate_passed_required=len(passed_required),
        gate_total_required=len(required),
        shadow_paper_allowed=shadow_allowed,
        active_paper_allowed=active_paper_allowed,
        live_allowed=live_allowed,
        next_action=next_action,
        reasons=reasons,
        warnings=warnings,
    )


def append_ledger(workspace: Path, rec: SandboxRecord) -> Optional[str]:
    try:
        root = workspace / "edge_factory_research_result_ledger"
        ledger = root / "master_research_result_ledger.jsonl"
        status = "PASS" if rec.sandbox_status == "SANDBOX_READY_REVIEW_ONLY" else "WATCHLIST"
        raw = {
            "recorded_at": datetime.now().isoformat(timespec="seconds"),
            "task_id": f"promotion_sandbox_{rec.candidate_key}",
            "result_status": status,
            "score": rec.evidence_score,
            "summary": f"{rec.candidate_key}: {rec.sandbox_status}, gates={rec.gate_passed_required}/{rec.gate_total_required}, shadow_allowed={rec.shadow_paper_allowed}",
            "evidence_path": str(Path(rec.sandbox_dir) / "sandbox_manifest.json"),
            "family": None,
            "candidate": rec.candidate_key,
            "tags": ["promotion_sandbox", "offline", "no_active_promotion", "no_live"],
            "reviewer": "family_promotion_sandbox_v1",
            "source": "edge_factory_family_promotion_sandbox_v1",
            "safe_for_auto_promotion": False,
            "live_allowed": False,
            "notes": "Sandbox creation only. No active paper/live/config mutation.",
        }
        result_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{stable_hash(raw)}"
        row = {"result_id": result_id, **raw}
        ledger.parent.mkdir(parents=True, exist_ok=True)
        with ledger.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
        rows = []
        with ledger.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        pd.DataFrame(rows).to_csv(root / "master_research_result_ledger.csv", index=False)
        return result_id
    except Exception:
        return None


def records_df(records: List[SandboxRecord]) -> pd.DataFrame:
    rows = []
    for r in records:
        d = asdict(r)
        d["reasons"] = " | ".join(r.reasons)
        d["warnings"] = " | ".join(r.warnings)
        rows.append(d)
    return pd.DataFrame(rows)


def write_report(path: Path, state: SandboxState, records: List[SandboxRecord]) -> None:
    lines = [
        "# Edge Factory Family Promotion Sandbox Report",
        "",
        f"Generated: `{state.generated_at}`",
        f"Overall state: **{state.overall_state}**",
        f"Candidates seen: **{state.candidates_seen}**",
        f"Sandboxes created: **{state.sandboxes_created}**",
        f"Shadow paper allowed count: **{state.shadow_paper_allowed_count}**",
        f"Active paper allowed count: **{state.active_paper_allowed_count}**",
        f"Live allowed: **{state.live_allowed}**",
        "",
        "## Sandboxes",
        "",
    ]
    if records:
        lines += ["| Candidate | Status | Score | Gates | Shadow allowed | Active paper | Live | Next |", "|---|---:|---:|---:|---:|---:|---:|---|"]
        for r in records:
            lines.append(f"| {r.candidate_key} | {r.sandbox_status} | {r.evidence_score} | {r.gate_passed_required}/{r.gate_total_required} | {r.shadow_paper_allowed} | {r.active_paper_allowed} | {r.live_allowed} | {r.next_action} |")
    else:
        lines.append("No promotion sandbox candidates found.")
    lines += ["", "## Reasons", ""]
    for reason in state.reasons:
        lines.append(f"- {reason}")
    if state.warnings:
        lines += ["", "## Warnings", ""]
        for w in state.warnings:
            lines.append(f"- {w}")
    lines += ["", "## Hard rules", ""]
    for rule in state.hard_rules:
        lines.append(f"- {rule}")
    lines += ["", "## Interpretation", "", "Sandbox creation is quarantine only. It allows future sandbox-specific research planning, not active paper inclusion and never live.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory family promotion sandbox")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--candidate", default=None)
    p.add_argument("--out_dir", default=None)
    p.add_argument("--no_ledger_append", action="store_true")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_family_promotion_sandbox"
    out_dir = out_root / f"promotion_sandbox_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    source_decisions = latest_synthesis_decisions(workspace)
    candidates = load_candidates(workspace, args.candidate)
    records: List[SandboxRecord] = []
    warnings: List[str] = []
    ledger_count = 0

    for ev in candidates:
        gates = build_gates(ev, workspace)
        rec = write_sandbox_files(workspace, out_dir, ev, gates, stamp)
        records.append(rec)
        if not args.no_ledger_append:
            rid = append_ledger(workspace, rec)
            if rid:
                ledger_count += 1
            else:
                warnings.append(f"ledger append failed for {ev.candidate_key}")

    if not candidates:
        warnings.append("No PROMOTION_SANDBOX_CANDIDATE rows found in latest evidence synthesis output.")

    shadow_allowed_count = len([r for r in records if r.shadow_paper_allowed])
    active_allowed_count = len([r for r in records if r.active_paper_allowed])
    if records and shadow_allowed_count == len(records):
        overall = "SANDBOX_READY_REVIEW_ONLY"
    elif records:
        overall = "SANDBOX_CREATED_WITH_BLOCKED_GATES"
    else:
        overall = "NO_SANDBOX_CANDIDATES"

    state = SandboxState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        source_decisions_path=str(source_decisions) if source_decisions else None,
        candidates_seen=len(candidates),
        sandboxes_created=len(records),
        shadow_paper_allowed_count=shadow_allowed_count,
        active_paper_allowed_count=active_allowed_count,
        live_allowed=False,
        overall_state=overall,
        reasons=[
            "Promotion sandbox builder read latest evidence synthesis output.",
            "Sandboxes are isolated quarantine zones and do not alter active system state.",
        ],
        warnings=warnings,
        hard_rules=[
            "Promotion sandbox never starts paper/live.",
            "Promotion sandbox never mutates active config.",
            "Promotion sandbox never edits position sizing contract.",
            "Sandbox candidate cannot enter active paper without future sandbox-specific plan and manual approval.",
            "Live remains blocked.",
        ],
    )

    state_path = out_dir / "family_promotion_sandbox_state.json"
    write_json(state_path, {"state": asdict(state), "sandboxes": [asdict(r) for r in records]})
    records_df(records).to_csv(out_dir / "family_promotion_sandbox_summary.csv", index=False)
    write_report(out_dir / "family_promotion_sandbox_report.md", state, records)

    print("EDGE FACTORY FAMILY PROMOTION SANDBOX v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"output_dir: {out_dir}")
    print(f"overall_state: {state.overall_state}")
    print(f"source_decisions: {state.source_decisions_path}")
    print(f"candidates_seen: {state.candidates_seen}")
    print(f"sandboxes_created: {state.sandboxes_created}")
    print(f"shadow_paper_allowed_count: {state.shadow_paper_allowed_count}")
    print(f"active_paper_allowed_count: {state.active_paper_allowed_count}")
    print(f"ledger_records_appended: {ledger_count}")
    print("live_allowed: False")
    print("")
    print("SANDBOXES")
    print("-" * 100)
    for r in records:
        print(f"{r.candidate_key:32s} status={r.sandbox_status:32s} score={r.evidence_score:6.2f} gates={r.gate_passed_required}/{r.gate_total_required} shadow_allowed={r.shadow_paper_allowed} active_paper={r.active_paper_allowed} live={r.live_allowed}")
        print(f"     persistent: {r.persistent_dir}")
        print(f"     next: {r.next_action}")
        if r.warnings:
            print(f"     warnings: {' | '.join(r.warnings[:3])}")
    if state.warnings:
        print("")
        print("WARNINGS")
        print("-" * 100)
        for w in state.warnings:
            print(f"- {w}")
    print("")
    print("IMPORTANT")
    print("-" * 100)
    print("This module did not start paper/live, did not mutate active config, and did not promote any strategy.")
    print("")
    print(f"Report : {out_dir / 'family_promotion_sandbox_report.md'}")
    print(f"State  : {state_path}")
    print(f"Summary: {out_dir / 'family_promotion_sandbox_summary.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
