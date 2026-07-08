#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY PAPER BOOT PLAN v1
===============================

Purpose
-------
Offline supervised paper boot planner for the Edge Factory OS.

This module DOES NOT start paper trading.
It DOES NOT open processes.
It DOES NOT place orders.
It DOES NOT modify loggers/contracts.

It reads the latest OS artifacts and writes a paper boot plan:
    - exact command to start MASTER_UPPER_SYSTEM later
    - expected active families and notionals
    - required native execution logging fields
    - expected output directories/files
    - kill-switch rules that must be enforced
    - pre-boot checklist
    - post-boot validation checklist

Current stage
-------------
Preflight says:
    PAPER_READY_WITH_WARNINGS_NOT_STARTED
    LIVE_BLOCKED_UNTIL_PAPER_DRIFT_AND_MANUAL_REVIEW

Native BPS validator says:
    PAPER_ALLOWED_BPS_QUALITY_ACCEPTABLE
    LIVE_BLOCKED_UNTIL_PAPER_NATIVE_BPS_AND_DRIFT

So the correct next step is not live, and not automatic paper.
The correct next step is a supervised paper boot plan with mandatory native execution fields.

Run:
    python "C:\Users\alike\edge_factory_paper_boot_plan.py"

Outputs:
    <workspace>\edge_factory_paper_boot_plan\paper_boot_plan_YYYYMMDD_HHMMSS\
        paper_boot_plan.md
        paper_boot_plan.json
        paper_launch_commands.ps1
        paper_runtime_expected_files.json
        required_native_log_fields.json
        paper_post_boot_checklist.json

Important
---------
The generated paper_launch_commands.ps1 is a PLAN file. It is not executed by this script.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_SCRIPT_DIR = Path(r"C:\Users\alike")
DEFAULT_LAUNCHER = DEFAULT_SCRIPT_DIR / "start_edge_factory_MASTER_UPPER_SYSTEM.ps1"
DEFAULT_PAPER_DIR = DEFAULT_WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"
DEFAULT_SIZING_CONTRACT = DEFAULT_WORKSPACE / "edge_factory_position_sizing_contract" / "position_sizing_contract.json"

ACTIVE_FAMILIES = ["old_short", "impulse_long", "market_relative_short", "weak_market_short"]
DISABLED_FAMILIES = ["session_short"]

LOGGER_SCRIPTS = {
    "old_short": DEFAULT_SCRIPT_DIR / "old_short_gate_aware_live_paper_logger.py",
    "impulse_long": DEFAULT_SCRIPT_DIR / "impulse_long_gate_aware_live_paper_logger.py",
    "market_relative_short": DEFAULT_SCRIPT_DIR / "market_relative_live_paper_logger.py",
    "weak_market_short": DEFAULT_SCRIPT_DIR / "weak_market_breakdown_short_live_paper_logger.py",
}

REQUIRED_NATIVE_FIELDS = [
    "family_key",
    "symbol",
    "side",
    "entry_time",
    "exit_time",
    "entry_price",
    "exit_price",
    "qty",
    "notional_usdt",
    "gross_pnl_usdt",
    "fee_usdt",
    "net_pnl_usdt",
    "gross_bps",
    "net_bps",
    "spread_bps_at_entry",
    "spread_bps_at_exit",
    "slippage_bps_est",
    "hold_seconds",
    "exit_reason",
    "strategy_signal_id",
]

RECOMMENDED_NATIVE_FIELDS = [
    "orderbook_best_bid_entry",
    "orderbook_best_ask_entry",
    "orderbook_best_bid_exit",
    "orderbook_best_ask_exit",
    "mid_price_entry",
    "mid_price_exit",
    "mark_price_entry",
    "mark_price_exit",
    "funding_rate",
    "market_regime",
    "raw_signal_value",
    "risk_block_reason",
    "kill_switch_state",
    "sizing_contract_version",
]


@dataclass
class ArtifactPath:
    key: str
    path: Optional[str]
    exists: bool
    status: str


@dataclass
class FamilyPaperPlan:
    family_key: str
    paper_enabled: bool
    live_enabled: bool
    role: str
    proposed_notional: float
    max_positions: int
    priority: int
    paper_gate: str
    daily_loss_stop_usdt: float
    rolling20_loss_stop_usdt: float
    max_consecutive_losses: int
    logger_script: str
    expected_log_dir: str
    required_fields: List[str]
    warnings: List[str]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def latest_child_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


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


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def optional_json(path: Optional[Path]) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        obj = load_json(path)
        return obj if isinstance(obj, dict) else {"_list": obj} if isinstance(obj, list) else {}
    except Exception:
        return {}


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def discover_artifacts(workspace: Path) -> Dict[str, Optional[Path]]:
    dirs = {
        "preflight": (workspace / "edge_factory_os_preflight", "preflight_", "paper_boot_decision.json"),
        "kill_switch": (workspace / "edge_factory_kill_switch_controller", "kill_switch_", "kill_switch_policy.json"),
        "native_bps": (workspace / "edge_factory_native_bps_validator", "native_bps_", "native_bps_validation.json"),
        "capital": (workspace / "edge_factory_adaptive_capital_governor_v2", "capital_governor_", "capital_policy_proposal.json"),
        "lifecycle": (workspace / "edge_factory_family_lifecycle", "lifecycle_", "family_lifecycle_state.json"),
        "execution": (workspace / "edge_factory_execution_realism_checker", "execution_realism_", "execution_realism_decisions.json"),
        "contract_reconciler": (workspace / "edge_factory_contract_reconciler", "contract_reconcile_", "contract_diff.json"),
    }
    out: Dict[str, Optional[Path]] = {}
    for key, (root, prefix, filename) in dirs.items():
        d = latest_child_dir(root, prefix)
        out[key] = d / filename if d and (d / filename).exists() else None
    return out


def artifact_refs(artifacts: Dict[str, Optional[Path]]) -> List[ArtifactPath]:
    rows: List[ArtifactPath] = []
    for key, path in artifacts.items():
        exists = bool(path and path.exists())
        rows.append(ArtifactPath(key, str(path) if path else None, exists, "PASS" if exists else "MISSING"))
    return rows


def family_capital_map(capital: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    rows = capital.get("family_decisions") or []
    out: Dict[str, Dict[str, Any]] = {}
    if isinstance(rows, list):
        for r in rows:
            if isinstance(r, dict) and r.get("family_key"):
                out[str(r["family_key"])] = r
    return out


def family_safety_map(kill: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    rows = kill.get("family_safety_states") or []
    out: Dict[str, Dict[str, Any]] = {}
    if isinstance(rows, list):
        for r in rows:
            if isinstance(r, dict) and r.get("family_key"):
                out[str(r["family_key"])] = r
    return out


def native_bps_map(native: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    rows = native.get("family_quality") or []
    out: Dict[str, Dict[str, Any]] = {}
    if isinstance(rows, list):
        for r in rows:
            if isinstance(r, dict) and r.get("family_key"):
                out[str(r["family_key"])] = r
    return out


def build_family_plans(workspace: Path, capital: Dict[str, Any], kill: Dict[str, Any], native: Dict[str, Any]) -> List[FamilyPaperPlan]:
    cap = family_capital_map(capital)
    safety = family_safety_map(kill)
    bps = native_bps_map(native)
    paper_families = set(kill.get("paper_eligible_families") or [])

    plans: List[FamilyPaperPlan] = []
    for fam in ACTIVE_FAMILIES + DISABLED_FAMILIES:
        cap_row = cap.get(fam, {})
        safety_row = safety.get(fam, {})
        bps_row = bps.get(fam, {})
        proposed = safe_float(cap_row.get("proposed_notional"), 0.0)
        paper_gate = str(safety_row.get("paper_gate", "UNKNOWN"))
        paper_enabled = fam in paper_families and proposed > 0 and not paper_gate.startswith("BLOCK")
        warnings: List[str] = []
        tier = str(bps_row.get("bps_quality_tier", "UNKNOWN"))
        if tier in {"ROW_NOTIONAL_ESTIMATED", "PROPOSED_NOTIONAL_ESTIMATED", "NATIVE_BPS_PARTIAL"}:
            warnings.append(f"bps_quality={tier}; native paper logging required")
        if fam in {"market_relative_short", "weak_market_short"}:
            warnings.append("backup/capped family; no self-promotion allowed")
        if fam == "session_short":
            warnings.append("disabled family; no paper/live entries")

        plans.append(FamilyPaperPlan(
            family_key=fam,
            paper_enabled=paper_enabled,
            live_enabled=False,
            role=str(cap_row.get("risk_tier", safety_row.get("risk_tier", "UNKNOWN"))),
            proposed_notional=proposed,
            max_positions=safe_int(cap_row.get("proposed_max_positions"), 0),
            priority=safe_int(cap_row.get("proposed_priority"), 0),
            paper_gate=paper_gate,
            daily_loss_stop_usdt=safe_float(safety_row.get("daily_loss_stop_usdt"), 0.0),
            rolling20_loss_stop_usdt=safe_float(safety_row.get("rolling_loss_stop_usdt"), 0.0),
            max_consecutive_losses=safe_int(safety_row.get("max_consecutive_losses"), 0),
            logger_script=str(LOGGER_SCRIPTS.get(fam, "")),
            expected_log_dir=str(DEFAULT_PAPER_DIR / fam),
            required_fields=REQUIRED_NATIVE_FIELDS,
            warnings=warnings,
        ))
    return plans


def build_expected_files(plans: List[FamilyPaperPlan]) -> Dict[str, Any]:
    family_files: Dict[str, Any] = {}
    for p in plans:
        if not p.paper_enabled:
            continue
        base = DEFAULT_PAPER_DIR / p.family_key
        family_files[p.family_key] = {
            "expected_dir": str(base),
            "acceptable_trade_files": [
                str(base / "closed_trades.csv"),
                str(base / "paper_trades.csv"),
                str(base / "trades.csv"),
            ],
            "acceptable_heartbeat_files": [
                str(base / "heartbeat.json"),
                str(base / "status.json"),
            ],
            "required_native_fields": REQUIRED_NATIVE_FIELDS,
            "recommended_native_fields": RECOMMENDED_NATIVE_FIELDS,
        }
    return {
        "paper_base_dir": str(DEFAULT_PAPER_DIR),
        "family_files": family_files,
        "system_files": {
            "health_check_expected": str(DEFAULT_PAPER_DIR / "health_check_latest.json"),
            "risk_manager_expected": str(DEFAULT_PAPER_DIR / "risk_manager_state.json"),
            "paper_boot_decision_source": "paper_boot_decision.json",
        },
    }


def build_launch_script_text(workspace: Path, script_dir: Path) -> str:
    launcher = script_dir / "start_edge_factory_MASTER_UPPER_SYSTEM.ps1"
    health = script_dir / "edge_factory_live_health_check_v5.py"
    perf = script_dir / "edge_factory_live_performance_analyzer_v3.py"
    dashboard = script_dir / "edge_factory_live_decision_dashboard.py"
    base_dir = workspace / "paper_run_gate_MASTER_UPPER_SYSTEM"

    return f'''# EDGE FACTORY PAPER BOOT PLAN - COMMANDS ONLY
# Generated: {datetime.now().isoformat(timespec="seconds")}
# IMPORTANT: This file is not executed by the planner.
# Review kill_switch_policy.json and paper_boot_decision.json before running anything.
# Live remains blocked.

# 1) Start supervised MASTER_UPPER_SYSTEM paper run later:
powershell -ExecutionPolicy Bypass -File "{launcher}"

# 2) Health check after boot:
python "{health}" --base_dir "{base_dir}"

# 3) Performance analyzer after enough closed paper trades:
python "{perf}" --base_dir "{base_dir}"

# 4) Decision dashboard:
python "{dashboard}" --base_dir "{base_dir}"

# 5) Drift monitor only after closed paper trades exist:
python "{script_dir / 'edge_factory_live_vs_backtest_drift_monitor.py'}" --base_dir "{base_dir}" --workspace "{workspace}"
'''


def build_checklists(plans: List[FamilyPaperPlan], artifacts: Dict[str, Optional[Path]]) -> Dict[str, Any]:
    return {
        "before_paper_start": [
            "Confirm paper_boot_decision is PAPER_READY_WITH_WARNINGS_NOT_STARTED or PAPER_READY_NOT_STARTED.",
            "Confirm live_gate is LIVE_BLOCKED_UNTIL_PAPER_DRIFT_AND_MANUAL_REVIEW.",
            "Confirm position_sizing_contract.json has market_relative_short = 12.5 USDT.",
            "Confirm kill_switch_policy.json exists and rule_count > 0.",
            "Confirm launcher exists: start_edge_factory_MASTER_UPPER_SYSTEM.ps1.",
            "Confirm all active logger scripts exist and support --sizing_contract / --default_notional.",
            "Confirm paper run is supervised and not real exchange live trading.",
        ],
        "during_first_30_minutes": [
            "Verify paper base dir is created.",
            "Verify each enabled family writes heartbeat/status files.",
            "Verify no family exceeds proposed notional cap.",
            "Verify no session_short entries are produced.",
            "Verify native execution fields are present in trade logs or logger schema.",
        ],
        "after_first_closed_trades": [
            "Check closed trade rows contain required native fields.",
            "Run health checker.",
            "Run performance analyzer only after meaningful sample starts forming.",
            "Run drift monitor only after enough closed trades exist.",
            "Do not consider live until paper drift validation passes and manual review approves.",
        ],
        "family_plans": [asdict(p) for p in plans],
        "artifact_sources": {k: str(v) if v else None for k, v in artifacts.items()},
    }


def write_report(path: Path, context: Dict[str, Any], plans: List[FamilyPaperPlan], expected: Dict[str, Any], checklists: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory Paper Boot Plan")
    lines.append("")
    lines.append(f"Generated: `{context['generated_at']}`")
    lines.append(f"Workspace: `{context['workspace']}`")
    lines.append(f"Paper decision: **{context['paper_decision']}**")
    lines.append(f"Live gate: **{context['live_gate']}**")
    lines.append("")

    lines.append("## Executive summary")
    lines.append("")
    lines.append("This is a plan only. It does not start paper/live trading.")
    lines.append("")
    lines.append(f"- Paper base dir: `{expected['paper_base_dir']}`")
    lines.append(f"- Launcher: `{context['launcher']}`")
    lines.append(f"- Sizing contract: `{context['sizing_contract']}`")
    lines.append("- Live allowed: **False**")
    lines.append("")

    lines.append("## Family paper plan")
    lines.append("")
    lines.append("| Family | Paper | Live | Role | Notional | Max pos | Priority | Paper gate | Daily stop | Rolling20 stop | Warnings |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    for p in plans:
        lines.append(
            f"| {p.family_key} | {p.paper_enabled} | {p.live_enabled} | {p.role} | {p.proposed_notional} | "
            f"{p.max_positions} | {p.priority} | {p.paper_gate} | {p.daily_loss_stop_usdt} | "
            f"{p.rolling20_loss_stop_usdt} | {'; '.join(p.warnings)} |"
        )
    lines.append("")

    lines.append("## Required native log fields")
    lines.append("")
    for f in REQUIRED_NATIVE_FIELDS:
        lines.append(f"- `{f}`")
    lines.append("")

    lines.append("## Recommended extra fields")
    lines.append("")
    for f in RECOMMENDED_NATIVE_FIELDS:
        lines.append(f"- `{f}`")
    lines.append("")

    lines.append("## Before paper start checklist")
    lines.append("")
    for item in checklists["before_paper_start"]:
        lines.append(f"- [ ] {item}")
    lines.append("")

    lines.append("## During first 30 minutes checklist")
    lines.append("")
    for item in checklists["during_first_30_minutes"]:
        lines.append(f"- [ ] {item}")
    lines.append("")

    lines.append("## After first closed trades checklist")
    lines.append("")
    for item in checklists["after_first_closed_trades"]:
        lines.append(f"- [ ] {item}")
    lines.append("")

    lines.append("## Planned commands")
    lines.append("")
    lines.append("Commands are written to `paper_launch_commands.ps1`. The planner did not execute them.")
    lines.append("")

    lines.append("## Artifact sources")
    lines.append("")
    for k, v in context["artifacts"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory paper boot planner")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--script_dir", default=str(DEFAULT_SCRIPT_DIR))
    p.add_argument("--out_dir", default=None)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    script_dir = Path(args.script_dir)
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_paper_boot_plan"
    out_dir = out_root / f"paper_boot_plan_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    artifacts = discover_artifacts(workspace)
    preflight = optional_json(artifacts.get("preflight"))
    kill = optional_json(artifacts.get("kill_switch"))
    native = optional_json(artifacts.get("native_bps"))
    capital = optional_json(artifacts.get("capital"))

    paper_decision = str(preflight.get("decision", preflight.get("paper_boot_decision", "UNKNOWN")))
    live_gate = str(preflight.get("live_gate", kill.get("live_gate", "LIVE_BLOCKED")))
    plans = build_family_plans(workspace, capital, kill, native)
    expected = build_expected_files(plans)
    checklists = build_checklists(plans, artifacts)
    launch_text = build_launch_script_text(workspace, script_dir)

    context = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(workspace),
        "script_dir": str(script_dir),
        "launcher": str(script_dir / "start_edge_factory_MASTER_UPPER_SYSTEM.ps1"),
        "sizing_contract": str(workspace / "edge_factory_position_sizing_contract" / "position_sizing_contract.json"),
        "paper_decision": paper_decision,
        "live_gate": live_gate,
        "paper_started": False,
        "live_allowed": False,
        "artifacts": {k: str(v) if v else None for k, v in artifacts.items()},
    }

    plan_obj = {
        "context": context,
        "family_plans": [asdict(p) for p in plans],
        "expected_files": expected,
        "checklists": checklists,
        "required_native_fields": REQUIRED_NATIVE_FIELDS,
        "recommended_native_fields": RECOMMENDED_NATIVE_FIELDS,
        "hard_rules": [
            "This module does not start paper/live.",
            "Live remains blocked until paper drift and manual live review.",
            "Paper must enforce kill_switch_policy.json.",
            "Paper logs must include native execution fields.",
            "Backup-only families cannot self-promote.",
        ],
    }

    write_json(out_dir / "paper_boot_plan.json", plan_obj)
    write_json(out_dir / "paper_runtime_expected_files.json", expected)
    write_json(out_dir / "required_native_log_fields.json", {
        "required_native_fields": REQUIRED_NATIVE_FIELDS,
        "recommended_native_fields": RECOMMENDED_NATIVE_FIELDS,
    })
    write_json(out_dir / "paper_post_boot_checklist.json", checklists)
    (out_dir / "paper_launch_commands.ps1").write_text(launch_text, encoding="utf-8")
    write_report(out_dir / "paper_boot_plan.md", context, plans, expected, checklists)

    print("EDGE FACTORY PAPER BOOT PLAN v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"output_dir: {out_dir}")
    print(f"paper_decision: {paper_decision}")
    print(f"live_gate     : {live_gate}")
    print("paper_started : False")
    print("live_allowed  : False")
    print("")
    print("FAMILY PLAN")
    print("-" * 100)
    for p in plans:
        print(
            f"{p.family_key:24s} paper={str(p.paper_enabled):5s} live={str(p.live_enabled):5s} "
            f"notional={p.proposed_notional:8.4f} max_pos={p.max_positions:2d} priority={p.priority:3d} gate={p.paper_gate}"
        )
        for w in p.warnings[:3]:
            print(f"  - {w}")
    print("")
    print("PLAN FILES")
    print("-" * 100)
    print(f"Plan markdown : {out_dir / 'paper_boot_plan.md'}")
    print(f"Plan JSON     : {out_dir / 'paper_boot_plan.json'}")
    print(f"Commands      : {out_dir / 'paper_launch_commands.ps1'}")
    print(f"Expected files: {out_dir / 'paper_runtime_expected_files.json'}")
    print("")
    print("Nothing was started. This is a supervised boot plan only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
