#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY OS STATE INSPECTOR v1
==================================

Goal
----
This is the first OFFLINE control-plane module for the Edge Factory OS.
It does not start live/paper trading. It does not place orders. It does not edit logger files.

It answers one question:
    "What is the current state of the Edge Factory project, and what should the OS build/check next?"

Current project assumptions
---------------------------
Workspace:
    C:\Users\alike\OneDrive\Desktop\edge_lab_new
Script dir:
    C:\Users\alike
Launcher:
    C:\Users\alike\start_edge_factory_MASTER_UPPER_SYSTEM.ps1
Sizing contract:
    C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_position_sizing_contract\position_sizing_contract.json
Runtime helper:
    C:\Users\alike\sizing_contract_runtime.py

Run
---
    python "C:\Users\alike\edge_factory_os_state_inspector.py"

Optional:
    python "C:\Users\alike\edge_factory_os_state_inspector.py" --workspace "C:\Users\alike\OneDrive\Desktop\edge_lab_new" --script_dir "C:\Users\alike"

Output
------
Creates:
    <workspace>\edge_factory_os_state\state_inspection_YYYYMMDD_HHMMSS\
        os_state_report.md
        os_state_report.json
        next_task_queue.json

Readiness states
----------------
    NOT_READY_CORE_FILES_MISSING
    READY_FOR_OFFLINE_OS_BUILD
    READY_FOR_PAPER_BOOT_LATER

Important
---------
This script intentionally treats live/paper as NOT REQUIRED.
If no paper trades exist, that is not a failure at this stage.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_SCRIPT_DIR = Path(r"C:\Users\alike")
DEFAULT_PAPER_DIR_NAME = "paper_run_gate_MASTER_UPPER_SYSTEM"

ACTIVE_LOGGERS = {
    "old_short": "old_short_gate_aware_live_paper_logger.py",
    "impulse_long": "impulse_long_gate_aware_live_paper_logger.py",
    "market_relative_short": "market_relative_live_paper_logger.py",
    "weak_market_short": "weak_market_breakdown_short_live_paper_logger.py",
}

DISABLED_FAMILIES = {
    "session_short": "disabled by current MASTER_UPPER_SYSTEM policy",
}

CORE_SCRIPTS = {
    "launcher": "start_edge_factory_MASTER_UPPER_SYSTEM.ps1",
    "autopilot": "edge_factory_autopilot.py",
    "master_optimizer": "edge_factory_master_optimizer.py",
    "bad_day_investigator": "edge_factory_bad_day_investigator.py",
    "guarded_allocator_optimizer": "edge_factory_guarded_allocator_optimizer.py",
    "capital_governor": "edge_factory_capital_governor.py",
    "position_sizing_contract_builder": "edge_factory_position_sizing_contract.py",
    "logger_sizing_patcher": "edge_factory_logger_sizing_patcher_v2.py",
    "risk_manager_config": "global_paper_risk_manager_v4_config.py",
    "runtime_helper": "sizing_contract_runtime.py",
}

EXPECTED_NOTIONAL = {
    "old_short": 50.0,
    "impulse_long": 50.0,
    "market_relative_short": 25.0,
    "weak_market_short": 25.0,
}

IMPORTANT_OUTPUT_DIRS = {
    "master_optimizer": "edge_factory_master_optimizer",
    "bad_day_investigation": "edge_factory_bad_day_investigation",
    "guarded_allocator_optimizer": "edge_factory_guarded_allocator_optimizer",
    "capital_governor": "edge_factory_capital_governor",
    "position_sizing_contract": "edge_factory_position_sizing_contract",
    "logger_sizing_patch": "edge_factory_logger_sizing_patch_v2",
    "portfolio_family_overlap_validation": "portfolio_family_overlap_validation",
    "paper_master_upper_system": DEFAULT_PAPER_DIR_NAME,
    "drift_monitor": "edge_factory_drift_monitor",
    "os_state": "edge_factory_os_state",
}


@dataclass
class FileCheck:
    key: str
    path: str
    exists: bool
    size_bytes: Optional[int]
    last_modified: Optional[str]
    status: str
    message: str


@dataclass
class LoggerAudit:
    family_key: str
    path: str
    exists: bool
    size_bytes: Optional[int]
    supports_sizing_contract_literal: bool
    supports_default_notional_literal: bool
    imports_or_mentions_runtime_helper: bool
    contains_family_key: bool
    needs_patch: bool
    status: str
    message: str


@dataclass
class ContractAudit:
    path: str
    exists: bool
    readable: bool
    expected_notional_by_family: Dict[str, Optional[float]]
    matches_expected_policy: Dict[str, bool]
    raw_top_level_keys: List[str]
    status: str
    message: str


@dataclass
class OutputDirAudit:
    key: str
    path: str
    exists: bool
    file_count: int
    newest_file: Optional[str]
    newest_file_mtime: Optional[str]
    status: str
    message: str


@dataclass
class OSTask:
    priority: int
    task_key: str
    title: str
    module_type: str
    reason: str
    safe_offline: bool
    suggested_script_name: str
    inputs: List[str]
    outputs: List[str]
    blocked_by: List[str]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def iso_mtime(path: Path) -> Optional[str]:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")
    except Exception:
        return None


def file_size(path: Path) -> Optional[int]:
    try:
        return int(path.stat().st_size)
    except Exception:
        return None


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        try:
            return path.read_text(encoding="cp1254", errors="replace")
        except Exception:
            return ""


def load_json(path: Path) -> Tuple[bool, Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        if isinstance(obj, dict):
            return True, obj
        return True, {"_non_dict_json": obj}
    except Exception:
        return False, {}


def find_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        if isinstance(value, str):
            s = value.strip().replace("%", "")
            if s == "" or s.lower() in {"none", "null", "nan"}:
                return None
            return float(s)
        return float(value)
    except Exception:
        return None


def recursive_find_family_value(obj: Any, family_key: str, preferred_keys: List[str]) -> Optional[float]:
    """Flexible contract parser. Searches common shapes without depending on one schema."""
    if isinstance(obj, dict):
        # Direct shape: {"old_short": 50} or {"old_short": {"notional": 50}}
        if family_key in obj:
            direct = obj[family_key]
            direct_float = find_float(direct)
            if direct_float is not None:
                return direct_float
            if isinstance(direct, dict):
                for k in preferred_keys:
                    if k in direct:
                        v = find_float(direct[k])
                        if v is not None:
                            return v
                # Percent + equity shape inside family node.
                pct = None
                for k in ["notional_pct", "pct", "capital_pct", "allocation_pct"]:
                    if k in direct:
                        pct = find_float(direct[k])
                        break
                equity = None
                for k in ["base_equity", "base_equity_usdt", "equity", "account_equity"]:
                    if k in obj:
                        equity = find_float(obj[k])
                        break
                if pct is not None and equity is not None:
                    if pct > 1.0:
                        pct /= 100.0
                    return equity * pct

        # Map shape: {"expected_notional": {"old_short": 50}}
        for k in preferred_keys + ["notional_by_family", "family_notional", "expected_notional_by_family"]:
            node = obj.get(k)
            if isinstance(node, dict) and family_key in node:
                v = find_float(node[family_key])
                if v is not None:
                    return v

        # Recurse.
        for v in obj.values():
            found = recursive_find_family_value(v, family_key, preferred_keys)
            if found is not None:
                return found

    elif isinstance(obj, list):
        for item in obj:
            found = recursive_find_family_value(item, family_key, preferred_keys)
            if found is not None:
                return found

    return None


def audit_file(key: str, path: Path, required: bool = True) -> FileCheck:
    exists = path.exists()
    if exists:
        size = file_size(path)
        status = "PASS"
        msg = "found"
        if size == 0:
            status = "WARN" if not required else "FAIL"
            msg = "file exists but is empty"
        return FileCheck(
            key=key,
            path=str(path),
            exists=True,
            size_bytes=size,
            last_modified=iso_mtime(path),
            status=status,
            message=msg,
        )
    return FileCheck(
        key=key,
        path=str(path),
        exists=False,
        size_bytes=None,
        last_modified=None,
        status="FAIL" if required else "WARN",
        message="missing" if required else "optional file missing",
    )


def audit_logger(family_key: str, path: Path) -> LoggerAudit:
    exists = path.exists()
    txt = read_text(path) if exists else ""
    lower = txt.lower()

    supports_sizing = "sizing_contract" in lower or "--sizing_contract" in lower or "--sizing-contract" in lower
    supports_notional = "default_notional" in lower or "--default_notional" in lower or "--default-notional" in lower
    mentions_runtime = "sizing_contract_runtime" in lower or "load_sizing" in lower or "position_sizing" in lower
    contains_family = family_key.lower() in lower or family_key.lower() in str(path).lower()
    needs_patch = not (supports_sizing and supports_notional)

    if not exists:
        status = "FAIL"
        msg = "logger script missing"
    elif needs_patch:
        status = "FAIL"
        msg = "logger exists but sizing contract/default notional support is incomplete"
    elif not mentions_runtime:
        status = "WARN"
        msg = "logger has sizing literals but runtime helper import/mention was not detected; verify manually if needed"
    else:
        status = "PASS"
        msg = "logger appears patched for sizing contract"

    return LoggerAudit(
        family_key=family_key,
        path=str(path),
        exists=exists,
        size_bytes=file_size(path) if exists else None,
        supports_sizing_contract_literal=supports_sizing,
        supports_default_notional_literal=supports_notional,
        imports_or_mentions_runtime_helper=mentions_runtime,
        contains_family_key=contains_family,
        needs_patch=needs_patch,
        status=status,
        message=msg,
    )


def audit_contract(path: Path) -> ContractAudit:
    exists = path.exists()
    readable, obj = load_json(path) if exists else (False, {})
    preferred_keys = [
        "expected_notional",
        "expected_notional_usdt",
        "notional",
        "notional_usdt",
        "default_notional",
        "target_notional",
        "target_notional_usdt",
    ]

    values: Dict[str, Optional[float]] = {}
    matches: Dict[str, bool] = {}
    for fam, expected in EXPECTED_NOTIONAL.items():
        val = recursive_find_family_value(obj, fam, preferred_keys) if readable else None
        values[fam] = val
        matches[fam] = bool(val is not None and abs(val - expected) < 1e-9)

    if not exists:
        status = "FAIL"
        msg = "sizing contract missing"
    elif not readable:
        status = "FAIL"
        msg = "sizing contract exists but is not readable JSON"
    elif all(matches.values()):
        status = "PASS"
        msg = "contract readable and matches current expected policy"
    elif all(values[f] is not None for f in EXPECTED_NOTIONAL):
        status = "WARN"
        msg = "contract readable but some notionals differ from expected current policy"
    else:
        status = "WARN"
        msg = "contract readable but not all family notionals could be parsed; manual check may be needed"

    return ContractAudit(
        path=str(path),
        exists=exists,
        readable=readable,
        expected_notional_by_family=values,
        matches_expected_policy=matches,
        raw_top_level_keys=sorted(list(obj.keys()))[:100] if isinstance(obj, dict) else [],
        status=status,
        message=msg,
    )


def newest_file_in_dir(path: Path) -> Tuple[int, Optional[Path]]:
    if not path.exists() or not path.is_dir():
        return 0, None
    count = 0
    newest: Optional[Path] = None
    newest_mtime = -1.0
    for root, _, files in os.walk(path):
        for fn in files:
            p = Path(root) / fn
            count += 1
            try:
                mt = p.stat().st_mtime
                if mt > newest_mtime:
                    newest_mtime = mt
                    newest = p
            except Exception:
                pass
    return count, newest


def audit_output_dir(key: str, path: Path) -> OutputDirAudit:
    exists = path.exists() and path.is_dir()
    count, newest = newest_file_in_dir(path)

    if not exists:
        if key == "paper_master_upper_system":
            status = "WARN"
            msg = "paper output dir missing; OK before boot, not a core OS build failure"
        else:
            status = "WARN"
            msg = "output dir missing or not generated yet"
    elif count == 0:
        status = "WARN"
        msg = "output dir exists but has no files"
    else:
        status = "PASS"
        msg = "output dir has files"

    return OutputDirAudit(
        key=key,
        path=str(path),
        exists=exists,
        file_count=count,
        newest_file=str(newest) if newest else None,
        newest_file_mtime=iso_mtime(newest) if newest else None,
        status=status,
        message=msg,
    )


def detect_existing_os_modules(script_dir: Path) -> Dict[str, bool]:
    expected = {
        "state_inspector": script_dir / "edge_factory_os_state_inspector.py",
        "preflight_inspector": script_dir / "edge_factory_os_preflight_inspector.py",
        "live_vs_backtest_drift_monitor": script_dir / "edge_factory_live_vs_backtest_drift_monitor.py",
        "adaptive_capital_governor_v2": script_dir / "edge_factory_adaptive_capital_governor_v2.py",
        "family_lifecycle_engine": script_dir / "edge_factory_family_lifecycle_engine.py",
        "execution_realism_checker": script_dir / "edge_factory_execution_realism_checker.py",
        "rolling_oos_validator": script_dir / "edge_factory_rolling_oos_validator.py",
        "autonomous_research_queue": script_dir / "edge_factory_autonomous_research_queue.py",
        "kill_switch_controller": script_dir / "edge_factory_kill_switch_controller.py",
    }
    return {k: p.exists() for k, p in expected.items()}


def build_next_task_queue(
    workspace: Path,
    script_dir: Path,
    core_file_checks: List[FileCheck],
    logger_audits: List[LoggerAudit],
    contract_audit: ContractAudit,
    output_audits: List[OutputDirAudit],
) -> List[OSTask]:
    modules = detect_existing_os_modules(script_dir)
    core_failures = [c.key for c in core_file_checks if c.status == "FAIL"]
    logger_failures = [a.family_key for a in logger_audits if a.status == "FAIL"]
    contract_bad = contract_audit.status == "FAIL"

    tasks: List[OSTask] = []

    if core_failures or logger_failures or contract_bad:
        tasks.append(OSTask(
            priority=10,
            task_key="repair_core_runtime_prerequisites",
            title="Repair missing core runtime prerequisites",
            module_type="repair/check",
            reason="Core files, logger patches, or sizing contract are missing/broken. OS cannot safely advance until these are fixed.",
            safe_offline=True,
            suggested_script_name="manual_repair_then_rerun_state_inspector",
            inputs=["core file audit", "logger audit", "contract audit"],
            outputs=["clean OS state inspection"],
            blocked_by=[],
        ))
        return sorted(tasks, key=lambda x: x.priority)

    if not modules.get("preflight_inspector", False):
        tasks.append(OSTask(
            priority=20,
            task_key="build_preflight_inspector",
            title="Build boot preflight inspector",
            module_type="offline control-plane",
            reason="Before paper boot later, the OS needs a dedicated preflight layer that validates launch readiness without starting anything.",
            safe_offline=True,
            suggested_script_name="edge_factory_os_preflight_inspector.py",
            inputs=["workspace paths", "logger audit", "sizing contract", "launcher"],
            outputs=["preflight_report.json", "preflight_report.md"],
            blocked_by=[],
        ))

    if not modules.get("rolling_oos_validator", False):
        tasks.append(OSTask(
            priority=30,
            task_key="build_rolling_oos_validator",
            title="Build rolling out-of-sample validator",
            module_type="offline research validator",
            reason="The OS must be able to break/kill strategy families before live/paper by testing time-split robustness and rolling degradation.",
            safe_offline=True,
            suggested_script_name="edge_factory_rolling_oos_validator.py",
            inputs=["historical family backtest outputs", "candidate family configs"],
            outputs=["rolling_oos_summary.csv", "family_robustness_scores.json"],
            blocked_by=[],
        ))

    if not modules.get("family_lifecycle_engine", False):
        tasks.append(OSTask(
            priority=40,
            task_key="build_family_lifecycle_engine",
            title="Build family lifecycle engine",
            module_type="offline decision engine",
            reason="The OS needs a formal promote / keep / reduce / disable state machine for strategy families.",
            safe_offline=True,
            suggested_script_name="edge_factory_family_lifecycle_engine.py",
            inputs=["master optimizer outputs", "bad-day investigation", "guarded allocator", "rolling OOS validator later"],
            outputs=["family_lifecycle_state.json", "family_lifecycle_report.md"],
            blocked_by=["build_rolling_oos_validator recommended first, but not strictly required"],
        ))

    if not modules.get("adaptive_capital_governor_v2", False):
        tasks.append(OSTask(
            priority=50,
            task_key="build_adaptive_capital_governor_v2",
            title="Build adaptive family capital governor v2",
            module_type="offline allocator",
            reason="Current capital policy is static. The OS target requires family capital to adjust from evidence, not from manual guesses.",
            safe_offline=True,
            suggested_script_name="edge_factory_adaptive_capital_governor_v2.py",
            inputs=["family lifecycle state", "guarded allocator outputs", "bad-day stats", "drift decisions later"],
            outputs=["capital_policy_proposal.json", "capital_governor_report.md"],
            blocked_by=["family_lifecycle_engine preferred first"],
        ))

    if not modules.get("execution_realism_checker", False):
        tasks.append(OSTask(
            priority=60,
            task_key="build_execution_realism_checker",
            title="Build execution realism checker",
            module_type="offline/live-readiness validator",
            reason="Before real live, the OS must estimate fee, spread, slippage, partial fill, and notional feasibility risk.",
            safe_offline=True,
            suggested_script_name="edge_factory_execution_realism_checker.py",
            inputs=["historical trades", "spread/liquidity data if available", "family configs", "position sizing contract"],
            outputs=["execution_realism_report.json", "execution_risk_flags.csv"],
            blocked_by=[],
        ))

    if not modules.get("kill_switch_controller", False):
        tasks.append(OSTask(
            priority=70,
            task_key="build_kill_switch_controller",
            title="Build kill-switch controller design",
            module_type="safety/control",
            reason="The OS needs hard rules for when a family/system must be stopped, but this should be built after lifecycle/governor rules exist.",
            safe_offline=True,
            suggested_script_name="edge_factory_kill_switch_controller.py",
            inputs=["lifecycle state", "capital governor proposal", "future drift monitor", "future live health checks"],
            outputs=["kill_switch_policy.json", "kill_switch_report.md"],
            blocked_by=["family_lifecycle_engine", "adaptive_capital_governor_v2"],
        ))

    if not modules.get("autonomous_research_queue", False):
        tasks.append(OSTask(
            priority=80,
            task_key="build_autonomous_research_queue",
            title="Build autonomous research queue",
            module_type="research scheduler",
            reason="The final Edge Factory OS must know what to research next: new families, coin subsets, robustness tests, and retire/replace cycles.",
            safe_offline=True,
            suggested_script_name="edge_factory_autonomous_research_queue.py",
            inputs=["family lifecycle results", "rolling OOS results", "failed family archive", "market universe"],
            outputs=["research_queue.json", "research_queue_report.md"],
            blocked_by=["rolling_oos_validator", "family_lifecycle_engine"],
        ))

    # Drift monitor is intentionally later, only useful once paper/live is running.
    if not modules.get("live_vs_backtest_drift_monitor", False):
        tasks.append(OSTask(
            priority=90,
            task_key="build_live_vs_backtest_drift_monitor_later",
            title="Build live-vs-backtest drift monitor later",
            module_type="paper/live monitoring",
            reason="Useful only after paper/live has produced closed trades. Not required for current offline OS build stage.",
            safe_offline=True,
            suggested_script_name="edge_factory_live_vs_backtest_drift_monitor.py",
            inputs=["paper/live closed trades", "backtest reference"],
            outputs=["drift_decisions.json", "drift_family_summary.csv"],
            blocked_by=["paper/live boot later"],
        ))

    return sorted(tasks, key=lambda x: x.priority)


def determine_readiness(core_checks: List[FileCheck], logger_audits: List[LoggerAudit], contract_audit: ContractAudit) -> Tuple[str, List[str]]:
    blocking: List[str] = []

    for c in core_checks:
        if c.status == "FAIL" and c.key in {"launcher", "runtime_helper"}:
            blocking.append(f"missing_or_bad_core_file:{c.key}")

    for a in logger_audits:
        if a.status == "FAIL":
            blocking.append(f"logger_not_ready:{a.family_key}")

    if contract_audit.status == "FAIL":
        blocking.append("sizing_contract_not_ready")

    if blocking:
        return "NOT_READY_CORE_FILES_MISSING", blocking

    # Paper output is intentionally not required.
    warnings = []
    for c in core_checks:
        if c.status == "WARN":
            warnings.append(f"warn_core_file:{c.key}")
    for a in logger_audits:
        if a.status == "WARN":
            warnings.append(f"warn_logger:{a.family_key}")
    if contract_audit.status == "WARN":
        warnings.append("warn_contract_parse_or_policy_mismatch")

    if warnings:
        return "READY_FOR_OFFLINE_OS_BUILD", warnings

    return "READY_FOR_OFFLINE_OS_BUILD", []


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def write_report_md(path: Path, report: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory OS State Inspection Report")
    lines.append("")
    lines.append(f"Generated: `{report['generated_at']}`")
    lines.append(f"Readiness: **{report['readiness']}**")
    lines.append("")
    lines.append("## Paths")
    lines.append("")
    lines.append(f"- Workspace: `{report['workspace']}`")
    lines.append(f"- Script dir: `{report['script_dir']}`")
    lines.append(f"- Paper dir later: `{report['paper_dir']}`")
    lines.append("")

    lines.append("## Core files")
    lines.append("")
    lines.append("| Key | Status | Exists | Size | Modified | Path | Message |")
    lines.append("|---|---:|---:|---:|---:|---|---|")
    for c in report["core_file_checks"]:
        lines.append(f"| {c['key']} | {c['status']} | {c['exists']} | {c['size_bytes']} | {c['last_modified']} | `{c['path']}` | {c['message']} |")
    lines.append("")

    lines.append("## Logger audit")
    lines.append("")
    lines.append("| Family | Status | Exists | Sizing contract | Default notional | Runtime helper | Needs patch | Message |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---|")
    for a in report["logger_audit"]:
        lines.append(
            f"| {a['family_key']} | {a['status']} | {a['exists']} | "
            f"{a['supports_sizing_contract_literal']} | {a['supports_default_notional_literal']} | "
            f"{a['imports_or_mentions_runtime_helper']} | {a['needs_patch']} | {a['message']} |"
        )
    lines.append("")

    lines.append("## Sizing contract")
    lines.append("")
    ca = report["contract_audit"]
    lines.append(f"Status: **{ca['status']}** — {ca['message']}")
    lines.append("")
    lines.append("| Family | Parsed notional | Expected policy match |")
    lines.append("|---|---:|---:|")
    for fam, val in ca["expected_notional_by_family"].items():
        lines.append(f"| {fam} | {val} | {ca['matches_expected_policy'].get(fam)} |")
    lines.append("")

    lines.append("## Existing output directories")
    lines.append("")
    lines.append("| Key | Status | Exists | Files | Newest file | Message |")
    lines.append("|---|---:|---:|---:|---|---|")
    for o in report["output_dir_audit"]:
        newest = f"`{o['newest_file']}`" if o.get("newest_file") else ""
        lines.append(f"| {o['key']} | {o['status']} | {o['exists']} | {o['file_count']} | {newest} | {o['message']} |")
    lines.append("")

    lines.append("## Next task queue")
    lines.append("")
    if not report["next_task_queue"]:
        lines.append("No tasks generated. This usually means all known OS modules already exist.")
    else:
        lines.append("| Priority | Task | Script | Safe offline | Reason | Blocked by |")
        lines.append("|---:|---|---|---:|---|---|")
        for t in report["next_task_queue"]:
            blocked = ", ".join(t.get("blocked_by") or [])
            lines.append(
                f"| {t['priority']} | {t['title']} | `{t['suggested_script_name']}` | "
                f"{t['safe_offline']} | {t['reason']} | {blocked} |"
            )
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("- No paper/live trades are required at this stage.")
    lines.append("- The current goal is to build the OS control plane offline first.")
    lines.append("- Paper/live boot comes only after validation, lifecycle, governor, execution realism, and kill-switch logic are defined.")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def run_inspection(args: argparse.Namespace) -> Dict[str, Any]:
    workspace = Path(args.workspace)
    script_dir = Path(args.script_dir)
    paper_dir = workspace / DEFAULT_PAPER_DIR_NAME
    sizing_contract = workspace / "edge_factory_position_sizing_contract" / "position_sizing_contract.json"

    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_os_state"
    out_dir = out_root / f"state_inspection_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    core_file_checks: List[FileCheck] = []
    for key, filename in CORE_SCRIPTS.items():
        required = key in {"launcher", "runtime_helper"}
        core_file_checks.append(audit_file(key, script_dir / filename, required=required))

    logger_audits = [audit_logger(fam, script_dir / fn) for fam, fn in ACTIVE_LOGGERS.items()]
    contract_audit = audit_contract(sizing_contract)

    output_audits = [
        audit_output_dir(key, workspace / dirname)
        for key, dirname in IMPORTANT_OUTPUT_DIRS.items()
    ]

    readiness, readiness_notes = determine_readiness(core_file_checks, logger_audits, contract_audit)
    next_tasks = build_next_task_queue(workspace, script_dir, core_file_checks, logger_audits, contract_audit, output_audits)

    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(workspace),
        "script_dir": str(script_dir),
        "paper_dir": str(paper_dir),
        "sizing_contract": str(sizing_contract),
        "readiness": readiness,
        "readiness_notes": readiness_notes,
        "core_file_checks": [asdict(x) for x in core_file_checks],
        "logger_audit": [asdict(x) for x in logger_audits],
        "contract_audit": asdict(contract_audit),
        "disabled_families": DISABLED_FAMILIES,
        "output_dir_audit": [asdict(x) for x in output_audits],
        "existing_os_modules": detect_existing_os_modules(script_dir),
        "next_task_queue": [asdict(x) for x in next_tasks],
        "output_dir": str(out_dir),
    }

    write_json(out_dir / "os_state_report.json", report)
    write_json(out_dir / "next_task_queue.json", report["next_task_queue"])
    write_report_md(out_dir / "os_state_report.md", report)

    return report


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory OS offline state inspector")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE), help="edge_lab_new workspace path")
    p.add_argument("--script_dir", default=str(DEFAULT_SCRIPT_DIR), help="script folder path")
    p.add_argument("--out_dir", default=None, help="optional output root")
    p.add_argument("--json_only", action="store_true", help="print compact JSON only")
    return p


def main() -> int:
    args = build_arg_parser().parse_args()
    report = run_inspection(args)

    if args.json_only:
        print(json.dumps({
            "readiness": report["readiness"],
            "readiness_notes": report["readiness_notes"],
            "output_dir": report["output_dir"],
            "next_task_queue": report["next_task_queue"][:5],
        }, indent=2, ensure_ascii=False))
        return 0

    print("EDGE FACTORY OS STATE INSPECTOR v1")
    print("=" * 90)
    print(f"workspace : {report['workspace']}")
    print(f"script_dir: {report['script_dir']}")
    print(f"readiness : {report['readiness']}")
    if report["readiness_notes"]:
        print("notes     : " + ", ".join(report["readiness_notes"][:8]))
    print(f"output_dir: {report['output_dir']}")
    print("")

    print("LOGGER AUDIT")
    print("-" * 90)
    for a in report["logger_audit"]:
        print(
            f"{a['family_key']:24s} status={a['status']:5s} "
            f"sizing={str(a['supports_sizing_contract_literal']):5s} "
            f"notional={str(a['supports_default_notional_literal']):5s} "
            f"needs_patch={str(a['needs_patch']):5s}"
        )
    print("")

    print("CONTRACT AUDIT")
    print("-" * 90)
    ca = report["contract_audit"]
    print(f"status: {ca['status']} | {ca['message']}")
    for fam, val in ca["expected_notional_by_family"].items():
        print(f"{fam:24s} parsed_notional={val} expected_match={ca['matches_expected_policy'].get(fam)}")
    print("")

    print("NEXT TASK QUEUE")
    print("-" * 90)
    for t in report["next_task_queue"][:10]:
        blocked = ", ".join(t.get("blocked_by") or [])
        print(f"P{t['priority']:03d} {t['task_key']} -> {t['suggested_script_name']}")
        print(f"     {t['reason']}")
        if blocked:
            print(f"     blocked_by: {blocked}")
    print("")
    print(f"Open report: {Path(report['output_dir']) / 'os_state_report.md'}")
    print(f"Task queue : {Path(report['output_dir']) / 'next_task_queue.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
