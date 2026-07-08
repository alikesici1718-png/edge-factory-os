#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY OS DEPENDENCY / STALENESS CHECKER v2
=================================================

Purpose
-------
Semantic dependency and staleness checker for the Edge Factory OS.

v1 correctly detected timestamp staleness, but it treated every new contract_reconciler
artifact as a real upstream change. That creates a false positive when contract_reconciler
is run in PREVIEW_ONLY mode and all active contract values already MATCH the governor
proposal.

v2 fixes that:
    - contract_reconciler PREVIEW_ONLY + all MATCH = no semantic config change
    - contract_reconciler --apply / applied=True = semantic config change
    - preview with DIFF/MISSING = manual review required
    - downstream modules compare against semantic timestamps, not blind artifact timestamps

It does NOT start paper/live trading.
It does NOT execute rebuild commands.
It does NOT modify contracts/loggers.

Run:
    python "C:\Users\alike\edge_factory_os_dependency_staleness_checker_v2.py"

Outputs:
    <workspace>\edge_factory_os_dependency_staleness_v2\dependency_staleness_v2_YYYYMMDD_HHMMSS\
        os_dependency_staleness_v2_report.md
        os_dependency_staleness_v2.json
        os_artifact_states_v2.csv
        stale_rebuild_plan_v2.csv
        stale_rebuild_commands_v2.ps1
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_SCRIPT_DIR = Path(r"C:\Users\alike")

MODULES: Dict[str, Dict[str, Any]] = {
    "state_inspector": {"script": "edge_factory_os_state_inspector.py", "root": "edge_factory_os_state", "prefix": "state_inspection_", "file": "os_state_report.json", "required": True},
    "rolling_oos_validator": {"script": "edge_factory_rolling_oos_validator.py", "root": "edge_factory_rolling_oos_validator", "prefix": "rolling_oos_", "file": "rolling_oos_decisions.json", "required": True},
    "rolling_oos_validator_v2": {"script": "edge_factory_rolling_oos_validator_v2.py", "root": "edge_factory_rolling_oos_validator_v2", "prefix": "rolling_oos_v2_", "file": "clean_os_family_state_seed.json", "required": True, "deps": ["rolling_oos_validator"]},
    "family_lifecycle_engine": {"script": "edge_factory_family_lifecycle_engine.py", "root": "edge_factory_family_lifecycle", "prefix": "lifecycle_", "file": "family_lifecycle_state.json", "required": True, "deps": ["rolling_oos_validator_v2"]},
    "adaptive_capital_governor_v2": {"script": "edge_factory_adaptive_capital_governor_v2.py", "root": "edge_factory_adaptive_capital_governor_v2", "prefix": "capital_governor_", "file": "capital_policy_proposal.json", "required": True, "deps": ["family_lifecycle_engine"]},
    "contract_reconciler": {"script": "edge_factory_contract_reconciler.py", "root": "edge_factory_contract_reconciler", "prefix": "contract_reconcile_", "file": "contract_diff.json", "required": True, "deps": ["adaptive_capital_governor_v2"], "command_args": "--apply", "manual_apply": True},
    "execution_realism_checker": {"script": "edge_factory_execution_realism_checker.py", "root": "edge_factory_execution_realism_checker", "prefix": "execution_realism_", "file": "execution_realism_decisions.json", "required": True, "deps": ["adaptive_capital_governor_v2", "family_lifecycle_engine", "rolling_oos_validator"]},
    "kill_switch_controller": {"script": "edge_factory_kill_switch_controller.py", "root": "edge_factory_kill_switch_controller", "prefix": "kill_switch_", "file": "kill_switch_policy.json", "required": True, "deps": ["execution_realism_checker"]},
    "native_bps_validator": {"script": "edge_factory_native_bps_validator.py", "root": "edge_factory_native_bps_validator", "prefix": "native_bps_", "file": "native_bps_validation.json", "required": True, "deps": ["rolling_oos_validator", "adaptive_capital_governor_v2"]},
    "os_preflight_inspector": {"script": "edge_factory_os_preflight_inspector.py", "root": "edge_factory_os_preflight", "prefix": "preflight_", "file": "paper_boot_decision.json", "required": True, "deps": ["kill_switch_controller", "contract_reconciler", "native_bps_validator"]},
    "autonomous_research_queue": {"script": "edge_factory_autonomous_research_queue.py", "root": "edge_factory_autonomous_research_queue", "prefix": "research_queue_", "file": "research_queue.json", "required": True, "deps": ["os_preflight_inspector", "kill_switch_controller", "execution_realism_checker", "family_lifecycle_engine"]},
    "paper_boot_plan": {"script": "edge_factory_paper_boot_plan.py", "root": "edge_factory_paper_boot_plan", "prefix": "paper_boot_plan_", "file": "paper_boot_plan.json", "required": True, "deps": ["os_preflight_inspector", "native_bps_validator", "kill_switch_controller", "adaptive_capital_governor_v2"]},
    "task_reconciler": {"script": "edge_factory_os_task_reconciler.py", "root": "edge_factory_os_task_reconciler", "prefix": "task_reconcile_", "file": "os_task_reconciliation.json", "required": True, "deps": ["autonomous_research_queue", "paper_boot_plan", "native_bps_validator", "rolling_oos_validator_v2"]},
    "os_orchestrator_v2": {"script": "edge_factory_os_orchestrator_v2.py", "root": "edge_factory_os_orchestrator_v2", "prefix": "orchestrator_v2_", "file": "os_orchestrator_v2_state.json", "required": True, "deps": ["task_reconciler", "os_preflight_inspector", "kill_switch_controller", "native_bps_validator"]},
    "dependency_staleness_checker_v2": {"script": "edge_factory_os_dependency_staleness_checker_v2.py", "root": "edge_factory_os_dependency_staleness_v2", "prefix": "dependency_staleness_v2_", "file": "os_dependency_staleness_v2.json", "required": False, "deps": ["os_orchestrator_v2"]},
    "live_vs_backtest_drift_monitor": {"script": "edge_factory_live_vs_backtest_drift_monitor.py", "root": "edge_factory_drift_monitor", "prefix": "drift_report_", "file": "drift_report.json", "required": False, "deps": ["paper_boot_plan"], "blocked_by": ["supervised paper boot", "closed paper trades"]},
}


@dataclass
class ArtifactState:
    module_key: str
    script_path: str
    script_exists: bool
    artifact_root: str
    latest_dir: Optional[str]
    artifact_path: Optional[str]
    artifact_exists: bool
    artifact_modified_ts: Optional[float]
    artifact_modified_at: Optional[str]
    semantic_modified_ts: Optional[float]
    semantic_modified_at: Optional[str]
    semantic_basis: str
    required: bool
    deps: List[str]
    direct_stale_deps: List[str]
    transitive_stale_deps: List[str]
    status: str
    reason: str
    command: str
    safe_offline: bool
    blocked_by: List[str]


@dataclass
class RebuildStep:
    order: int
    module_key: str
    status: str
    reason: str
    command: str
    safe_offline: bool
    blocked_by: List[str]
    note: Optional[str]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def latest_child_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def file_mtime(path: Optional[Path]) -> Optional[float]:
    try:
        if path and path.exists():
            return path.stat().st_mtime
    except Exception:
        return None
    return None


def iso(ts: Optional[float]) -> Optional[str]:
    return datetime.fromtimestamp(ts).isoformat(timespec="seconds") if ts is not None else None


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def safe_load_json(path: Optional[Path]) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        obj = load_json(path)
        return obj if isinstance(obj, dict) else {}
    except Exception as e:
        return {"_load_error": str(e)}


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def command_for(script_dir: Path, key: str) -> str:
    spec = MODULES[key]
    args = str(spec.get("command_args", "")).strip()
    base = f'python "{script_dir / spec["script"]}"'
    return f"{base} {args}" if args else base


def contract_semantic_timestamp(workspace: Path, artifact_path: Optional[Path], artifact_ts: Optional[float]) -> Tuple[Optional[float], str, str]:
    """Return semantic timestamp, semantic_basis, reason for contract_reconciler."""
    active_contract = workspace / "edge_factory_position_sizing_contract" / "position_sizing_contract.json"
    active_ts = file_mtime(active_contract)
    obj = safe_load_json(artifact_path)
    applied = bool(obj.get("applied", False))
    diffs = obj.get("diffs") if isinstance(obj.get("diffs"), list) else []
    non_match = []
    for d in diffs:
        if not isinstance(d, dict):
            continue
        status = str(d.get("status", "")).upper()
        # MISSING session_short was acceptable before apply, but after the current contract it should be MATCH.
        if status not in {"MATCH"}:
            non_match.append(d)

    if applied:
        return artifact_ts, "CONTRACT_APPLIED_ARTIFACT_TS", "contract reconciler applied active config"
    if non_match:
        # Preview found differences; downstream config decision should wait for manual review.
        return artifact_ts, "PREVIEW_DIFF_REQUIRES_REVIEW", "preview found contract/governor mismatch"
    if active_ts is not None:
        return active_ts, "ACTIVE_CONTRACT_FILE_TS", "preview only and all contract diffs match; semantic dependency is active contract mtime"
    return artifact_ts, "PREVIEW_MATCH_NO_ACTIVE_CONTRACT_TS", "preview only and all match, but active contract mtime unavailable"


def collect_states(workspace: Path, script_dir: Path) -> Dict[str, ArtifactState]:
    states: Dict[str, ArtifactState] = {}
    for key, spec in MODULES.items():
        root = workspace / spec["root"]
        latest = latest_child_dir(root, spec["prefix"])
        artifact = latest / spec["file"] if latest else None
        artifact_exists = bool(artifact and artifact.exists() and artifact.is_file())
        artifact_ts = file_mtime(artifact) if artifact_exists else None
        semantic_ts = artifact_ts
        semantic_basis = "ARTIFACT_TS"
        reason = ""
        if key == "contract_reconciler" and artifact_exists:
            semantic_ts, semantic_basis, reason = contract_semantic_timestamp(workspace, artifact, artifact_ts)
        script = script_dir / spec["script"]
        states[key] = ArtifactState(
            module_key=key,
            script_path=str(script),
            script_exists=script.exists() and script.is_file(),
            artifact_root=str(root),
            latest_dir=str(latest) if latest else None,
            artifact_path=str(artifact) if artifact else None,
            artifact_exists=artifact_exists,
            artifact_modified_ts=artifact_ts,
            artifact_modified_at=iso(artifact_ts),
            semantic_modified_ts=semantic_ts,
            semantic_modified_at=iso(semantic_ts),
            semantic_basis=semantic_basis,
            required=bool(spec.get("required", True)),
            deps=list(spec.get("deps", [])),
            direct_stale_deps=[],
            transitive_stale_deps=[],
            status="UNKNOWN",
            reason=reason,
            command=command_for(script_dir, key),
            safe_offline=True,
            blocked_by=list(spec.get("blocked_by", [])),
        )
    return states


def direct_stale_deps(key: str, states: Dict[str, ArtifactState]) -> List[str]:
    cur = states[key]
    if not cur.artifact_exists or cur.artifact_modified_ts is None:
        return []
    stale: List[str] = []
    for dep in cur.deps:
        d = states.get(dep)
        if not d or not d.artifact_exists or d.semantic_modified_ts is None:
            continue
        if d.semantic_modified_ts > cur.artifact_modified_ts:
            stale.append(dep)
    return stale


def compute_transitive_stale(key: str, states: Dict[str, ArtifactState], memo: Dict[str, Set[str]]) -> Set[str]:
    if key in memo:
        return memo[key]
    s = states[key]
    stale: Set[str] = set(s.direct_stale_deps)
    for dep in s.deps:
        d = states.get(dep)
        if not d:
            continue
        if d.required and d.status in {"MISSING", "REQUIRED_SCRIPT_MISSING", "STALE_DIRECT", "STALE_TRANSITIVE", "MANUAL_REVIEW_REQUIRED"}:
            stale.add(dep)
        stale |= compute_transitive_stale(dep, states, memo)
    memo[key] = stale
    return stale


def evaluate(states: Dict[str, ArtifactState]) -> Dict[str, ArtifactState]:
    for key in states:
        states[key].direct_stale_deps = direct_stale_deps(key, states)

    for key, s in states.items():
        if not s.script_exists and s.required:
            s.status = "REQUIRED_SCRIPT_MISSING"
            s.reason = "required script is missing"
        elif not s.artifact_exists and s.required:
            s.status = "MISSING"
            s.reason = "required artifact is missing"
        elif not s.artifact_exists and not s.required:
            s.status = "OPTIONAL_MISSING"
            s.reason = "optional artifact missing"
        elif key == "contract_reconciler" and s.semantic_basis == "PREVIEW_DIFF_REQUIRES_REVIEW":
            s.status = "MANUAL_REVIEW_REQUIRED"
            s.reason = "contract preview found mismatch; manual apply/review required"
        elif s.direct_stale_deps:
            s.status = "STALE_DIRECT"
            s.reason = "upstream semantic artifact newer than this artifact: " + ", ".join(s.direct_stale_deps)
        else:
            s.status = "FRESH"
            if not s.reason:
                s.reason = "artifact exists and no newer semantic dependency detected"

    memo: Dict[str, Set[str]] = {}
    for key in states:
        states[key].transitive_stale_deps = sorted(compute_transitive_stale(key, states, memo))

    for key, s in states.items():
        if s.status == "FRESH" and s.transitive_stale_deps:
            if key == "live_vs_backtest_drift_monitor" and s.blocked_by:
                s.status = "OPTIONAL_WAITING"
                s.reason = "optional paper-dependent module waiting for: " + ", ".join(s.blocked_by)
            else:
                s.status = "STALE_TRANSITIVE"
                s.reason = "dependency chain contains stale/missing/review modules: " + ", ".join(s.transitive_stale_deps)
    return states


def topo_sort(states: Dict[str, ArtifactState]) -> List[str]:
    visited: Set[str] = set()
    out: List[str] = []

    def visit(k: str):
        if k in visited:
            return
        visited.add(k)
        for d in states[k].deps:
            if d in states:
                visit(d)
        out.append(k)

    for k in states:
        visit(k)
    return out


def build_rebuild_plan(states: Dict[str, ArtifactState]) -> List[RebuildStep]:
    statuses = {"MISSING", "REQUIRED_SCRIPT_MISSING", "STALE_DIRECT", "STALE_TRANSITIVE"}
    steps: List[RebuildStep] = []
    order = 1
    for key in topo_sort(states):
        s = states[key]
        if not s.required or s.status not in statuses:
            continue
        if key == "contract_reconciler" and MODULES[key].get("manual_apply"):
            # Rebuild plan should not execute mutating --apply automatically.
            steps.append(RebuildStep(order, key, "MANUAL_REVIEW_REQUIRED", "contract apply is manual; review preview first", s.command, True, [], "Uses --apply; do not auto-run."))
        else:
            steps.append(RebuildStep(order, key, s.status, s.reason, s.command, s.safe_offline, s.blocked_by, MODULES[key].get("note")))
        order += 1
    return steps


def states_df(states: Dict[str, ArtifactState]) -> pd.DataFrame:
    rows = []
    for s in states.values():
        d = asdict(s)
        d["deps"] = " | ".join(s.deps)
        d["direct_stale_deps"] = " | ".join(s.direct_stale_deps)
        d["transitive_stale_deps"] = " | ".join(s.transitive_stale_deps)
        d["blocked_by"] = " | ".join(s.blocked_by)
        rows.append(d)
    return pd.DataFrame(rows)


def rebuild_df(steps: List[RebuildStep]) -> pd.DataFrame:
    rows = []
    for s in steps:
        d = asdict(s)
        d["blocked_by"] = " | ".join(s.blocked_by)
        rows.append(d)
    return pd.DataFrame(rows)


def write_command_plan(path: Path, steps: List[RebuildStep]) -> None:
    lines = []
    lines.append("# EDGE FACTORY OS SEMANTIC STALENESS REBUILD PLAN v2")
    lines.append(f"# Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("# Plan only. No commands were executed.")
    lines.append("# Review manually. No paper/live launcher is included.")
    lines.append("")
    if not steps:
        lines.append("# No stale required control-plane artifacts detected.")
    for s in steps:
        lines.append(f"# Step {s.order}: {s.module_key} [{s.status}]")
        lines.append(f"# reason: {s.reason}")
        if s.note:
            lines.append(f"# note: {s.note}")
        if s.status == "MANUAL_REVIEW_REQUIRED":
            lines.append(f"# {s.command}")
        else:
            lines.append(s.command)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_report(path: Path, context: Dict[str, Any], states: Dict[str, ArtifactState], steps: List[RebuildStep]) -> None:
    counts: Dict[str, int] = {}
    for s in states.values():
        counts[s.status] = counts.get(s.status, 0) + 1

    lines: List[str] = []
    lines.append("# Edge Factory OS Dependency / Staleness v2 Report")
    lines.append("")
    lines.append(f"Generated: `{context['generated_at']}`")
    lines.append(f"Overall state: **{context['overall_state']}**")
    lines.append("")
    lines.append("## Status counts")
    lines.append("")
    for k in sorted(counts):
        lines.append(f"- {k}: **{counts[k]}**")
    lines.append("")
    lines.append("## Rebuild plan")
    lines.append("")
    if not steps:
        lines.append("No required stale/missing control-plane artifacts detected. Semantic dependency chain is current.")
    else:
        lines.append("| Order | Module | Status | Command | Reason |")
        lines.append("|---:|---|---:|---|---|")
        for s in steps:
            cmd = f"# {s.command}" if s.status == "MANUAL_REVIEW_REQUIRED" else s.command
            lines.append(f"| {s.order} | {s.module_key} | {s.status} | `{cmd}` | {s.reason} |")
    lines.append("")
    lines.append("## Artifact states")
    lines.append("")
    lines.append("| Module | Status | Artifact TS | Semantic TS | Semantic basis | Direct stale deps | Artifact |")
    lines.append("|---|---:|---:|---:|---:|---|---|")
    for key in topo_sort(states):
        s = states[key]
        lines.append(f"| {key} | {s.status} | {s.artifact_modified_at} | {s.semantic_modified_at} | {s.semantic_basis} | {', '.join(s.direct_stale_deps)} | `{s.artifact_path}` |")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("v2 uses semantic timestamps. A PREVIEW_ONLY contract reconciliation with all MATCH values does not make downstream artifacts stale, because the active contract did not change. If the preview finds DIFF/MISSING or an apply actually happened, downstream gates are marked stale or manual-review required.")
    lines.append("No paper/live actions were executed.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory OS semantic dependency/staleness checker v2")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--script_dir", default=str(DEFAULT_SCRIPT_DIR))
    p.add_argument("--out_dir", default=None)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    script_dir = Path(args.script_dir)
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_os_dependency_staleness_v2"
    out_dir = out_root / f"dependency_staleness_v2_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    states = evaluate(collect_states(workspace, script_dir))
    steps = build_rebuild_plan(states)
    bad = [s.module_key for s in states.values() if s.required and s.status in {"MISSING", "REQUIRED_SCRIPT_MISSING", "STALE_DIRECT", "STALE_TRANSITIVE", "MANUAL_REVIEW_REQUIRED"}]
    overall = "REBUILD_REQUIRED" if steps else "DEPENDENCY_CHAIN_CURRENT"
    if any(states[k].status == "MANUAL_REVIEW_REQUIRED" for k in states):
        overall = "MANUAL_REVIEW_REQUIRED"

    context = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(workspace),
        "script_dir": str(script_dir),
        "overall_state": overall,
        "rebuild_required_modules": bad,
        "rebuild_step_count": len(steps),
    }
    result = {
        "context": context,
        "artifact_states": {k: asdict(v) for k, v in states.items()},
        "rebuild_plan": [asdict(s) for s in steps],
        "hard_rules": [
            "Use semantic timestamps, not raw artifact timestamps, for preview-only config checks.",
            "Do not execute rebuild commands automatically.",
            "Do not start paper/live from staleness checker.",
            "Contract --apply stays manual review only.",
        ],
    }

    write_json(out_dir / "os_dependency_staleness_v2.json", result)
    states_df(states).to_csv(out_dir / "os_artifact_states_v2.csv", index=False)
    rebuild_df(steps).to_csv(out_dir / "stale_rebuild_plan_v2.csv", index=False)
    write_command_plan(out_dir / "stale_rebuild_commands_v2.ps1", steps)
    write_report(out_dir / "os_dependency_staleness_v2_report.md", context, states, steps)

    print("EDGE FACTORY OS DEPENDENCY / STALENESS CHECKER v2")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"script_dir: {script_dir}")
    print(f"output_dir: {out_dir}")
    print(f"overall   : {overall}")
    print(f"rebuild_steps: {len(steps)}")
    print("")
    print("STATUS COUNTS")
    print("-" * 100)
    counts: Dict[str, int] = {}
    for s in states.values():
        counts[s.status] = counts.get(s.status, 0) + 1
    for k in sorted(counts):
        print(f"{k:28s}: {counts[k]}")
    print("")
    print("REBUILD PLAN")
    print("-" * 100)
    if not steps:
        print("No required stale/missing semantic control-plane artifacts detected.")
    else:
        for s in steps:
            print(f"{s.order:02d}. {s.module_key:32s} status={s.status:22s}")
            print(f"    reason : {s.reason}")
            print(f"    command: {s.command}")
    print("")
    cr = states.get("contract_reconciler")
    if cr:
        print("CONTRACT SEMANTIC STATE")
        print("-" * 100)
        print(f"status        : {cr.status}")
        print(f"semantic_basis: {cr.semantic_basis}")
        print(f"artifact_ts   : {cr.artifact_modified_at}")
        print(f"semantic_ts   : {cr.semantic_modified_at}")
        print(f"reason        : {cr.reason}")
        print("")
    print(f"Report : {out_dir / 'os_dependency_staleness_v2_report.md'}")
    print(f"JSON   : {out_dir / 'os_dependency_staleness_v2.json'}")
    print(f"Plan   : {out_dir / 'stale_rebuild_commands_v2.ps1'}")
    return 0 if not steps else 2



if __name__ == "__main__":
    raise SystemExit(main())
