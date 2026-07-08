#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY OS PREFLIGHT INSPECTOR v1
======================================

Purpose
-------
Final offline boot-gate for the Edge Factory OS before any paper run.

This module does NOT start paper/live trading.
It does NOT place orders.
It does NOT edit loggers.
It does NOT overwrite the sizing contract.

It verifies that the OS control-plane chain exists and is internally consistent:

    OS State Inspector
    Rolling OOS Validator
    Family Lifecycle Engine
    Adaptive Capital Governor v2
    Execution Realism Checker
    Kill-Switch Controller
    Position Sizing Contract
    Runtime Helper
    MASTER_UPPER_SYSTEM Launcher
    Active Logger Patch State

Then it emits:
    PAPER_READY_NOT_STARTED
    PAPER_BLOCKED
    PAPER_READY_WITH_WARNINGS_NOT_STARTED

Live is always blocked by this module until future paper drift validation exists.

Run
---
    python "C:\Users\alike\edge_factory_os_preflight_inspector.py"

Optional:
    python "C:\Users\alike\edge_factory_os_preflight_inspector.py" --strict

Outputs
-------
    <workspace>\edge_factory_os_preflight\preflight_YYYYMMDD_HHMMSS\
        preflight_report.md
        preflight_report.json
        paper_boot_decision.json
        preflight_checks.csv
        required_artifacts.json

Default project paths
---------------------
Workspace:
    C:\Users\alike\OneDrive\Desktop\edge_lab_new
Script dir:
    C:\Users\alike
Launcher:
    C:\Users\alike\start_edge_factory_MASTER_UPPER_SYSTEM.ps1
Sizing contract:
    C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_position_sizing_contract\position_sizing_contract.json
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_SCRIPT_DIR = Path(r"C:\Users\alike")
DEFAULT_PAPER_DIR_NAME = "paper_run_gate_MASTER_UPPER_SYSTEM"

ACTIVE_LOGGERS = {
    "old_short": "old_short_gate_aware_live_paper_logger.py",
    "impulse_long": "impulse_long_gate_aware_live_paper_logger.py",
    "market_relative_short": "market_relative_live_paper_logger.py",
    "weak_market_short": "weak_market_breakdown_short_live_paper_logger.py",
}

EXPECTED_POLICY_FROM_GOVERNOR = {
    "old_short": 50.0,
    "impulse_long": 50.0,
    "market_relative_short": 12.5,
    "weak_market_short": 25.0,
    "session_short": 0.0,
}

CURRENT_CONTRACT_BASELINE = {
    "old_short": 50.0,
    "impulse_long": 50.0,
    "market_relative_short": 25.0,
    "weak_market_short": 25.0,
}

REQUIRED_SCRIPTS = {
    "launcher": "start_edge_factory_MASTER_UPPER_SYSTEM.ps1",
    "runtime_helper": "sizing_contract_runtime.py",
    "state_inspector": "edge_factory_os_state_inspector.py",
    "rolling_oos_validator": "edge_factory_rolling_oos_validator.py",
    "family_lifecycle_engine": "edge_factory_family_lifecycle_engine.py",
    "adaptive_capital_governor_v2": "edge_factory_adaptive_capital_governor_v2.py",
    "execution_realism_checker": "edge_factory_execution_realism_checker.py",
    "kill_switch_controller": "edge_factory_kill_switch_controller.py",
    "live_vs_backtest_drift_monitor": "edge_factory_live_vs_backtest_drift_monitor.py",
}

ARTIFACT_ROOTS = {
    "os_state": ("edge_factory_os_state", "state_inspection_", "os_state_report.json"),
    "rolling_oos": ("edge_factory_rolling_oos_validator", "rolling_oos_", "rolling_oos_decisions.json"),
    "family_lifecycle": ("edge_factory_family_lifecycle", "lifecycle_", "family_lifecycle_state.json"),
    "capital_governor": ("edge_factory_adaptive_capital_governor_v2", "capital_governor_", "capital_policy_proposal.json"),
    "execution_realism": ("edge_factory_execution_realism_checker", "execution_realism_", "execution_realism_decisions.json"),
    "kill_switch": ("edge_factory_kill_switch_controller", "kill_switch_", "kill_switch_policy.json"),
}


@dataclass
class Check:
    key: str
    status: str          # PASS / WARN / FAIL
    severity: str        # INFO / WARNING / BLOCKER
    message: str
    path: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class ArtifactRef:
    key: str
    root: str
    latest_dir: Optional[str]
    required_file: str
    required_file_path: Optional[str]
    exists: bool
    modified: Optional[str]
    status: str


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def iso_mtime(path: Path) -> Optional[str]:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")
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


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


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


def latest_child_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def recursive_find_family_value(obj: Any, family_key: str, preferred_keys: List[str]) -> Optional[float]:
    if isinstance(obj, dict):
        if family_key in obj:
            node = obj[family_key]
            try:
                v = float(node)
                if math.isfinite(v):
                    return v
            except Exception:
                pass
            if isinstance(node, dict):
                for k in preferred_keys:
                    if k in node:
                        v = safe_float(node[k], default=float("nan"))
                        if math.isfinite(v):
                            return v
        for k in preferred_keys + ["expected_notional_by_family", "notional_by_family", "family_notional"]:
            node = obj.get(k)
            if isinstance(node, dict) and family_key in node:
                v = safe_float(node[family_key], default=float("nan"))
                if math.isfinite(v):
                    return v
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


def parse_contract_notional(contract: Dict[str, Any], family_key: str) -> Optional[float]:
    return recursive_find_family_value(contract, family_key, [
        "expected_notional",
        "expected_notional_usdt",
        "notional",
        "notional_usdt",
        "default_notional",
        "target_notional",
        "target_notional_usdt",
    ])


def check_file_exists(key: str, path: Path, required: bool = True) -> Check:
    if path.exists() and path.is_file() and path.stat().st_size > 0:
        return Check(key, "PASS", "INFO", "file exists", str(path), {"size_bytes": path.stat().st_size, "modified": iso_mtime(path)})
    if path.exists() and path.is_file():
        return Check(key, "FAIL" if required else "WARN", "BLOCKER" if required else "WARNING", "file exists but is empty", str(path))
    return Check(key, "FAIL" if required else "WARN", "BLOCKER" if required else "WARNING", "file missing", str(path))


def audit_scripts(script_dir: Path) -> List[Check]:
    checks: List[Check] = []
    for key, filename in REQUIRED_SCRIPTS.items():
        # Drift monitor is only needed after paper, so non-blocking at this boot stage.
        required = key != "live_vs_backtest_drift_monitor"
        checks.append(check_file_exists(f"script_{key}", script_dir / filename, required=required))
    for fam, filename in ACTIVE_LOGGERS.items():
        p = script_dir / filename
        c = check_file_exists(f"logger_{fam}", p, required=True)
        if c.status == "PASS":
            txt = read_text(p).lower()
            supports_sizing = "sizing_contract" in txt or "--sizing_contract" in txt or "--sizing-contract" in txt
            supports_notional = "default_notional" in txt or "--default_notional" in txt or "--default-notional" in txt
            if supports_sizing and supports_notional:
                c.message = "logger exists and appears patched for sizing contract"
                c.details = dict(c.details or {}, supports_sizing_contract=True, supports_default_notional=True, needs_patch=False)
            else:
                c.status = "FAIL"
                c.severity = "BLOCKER"
                c.message = "logger exists but sizing contract/default notional support is incomplete"
                c.details = dict(c.details or {}, supports_sizing_contract=supports_sizing, supports_default_notional=supports_notional, needs_patch=True)
        checks.append(c)
    return checks


def discover_artifacts(workspace: Path) -> Tuple[List[ArtifactRef], Dict[str, Any], List[Check]]:
    refs: List[ArtifactRef] = []
    loaded: Dict[str, Any] = {}
    checks: List[Check] = []

    for key, (root_name, prefix, required_file) in ARTIFACT_ROOTS.items():
        root = workspace / root_name
        latest = latest_child_dir(root, prefix)
        req_path = latest / required_file if latest else None
        exists = bool(req_path and req_path.exists() and req_path.is_file())
        ref = ArtifactRef(
            key=key,
            root=str(root),
            latest_dir=str(latest) if latest else None,
            required_file=required_file,
            required_file_path=str(req_path) if req_path else None,
            exists=exists,
            modified=iso_mtime(req_path) if exists and req_path else None,
            status="PASS" if exists else "FAIL",
        )
        refs.append(ref)
        if exists and req_path:
            try:
                loaded[key] = load_json(req_path)
                checks.append(Check(f"artifact_{key}", "PASS", "INFO", "artifact exists and JSON loaded", str(req_path)))
            except Exception as e:
                checks.append(Check(f"artifact_{key}", "FAIL", "BLOCKER", f"artifact exists but JSON load failed: {e}", str(req_path)))
        else:
            checks.append(Check(f"artifact_{key}", "FAIL", "BLOCKER", "required OS artifact missing", str(req_path) if req_path else str(root)))

    return refs, loaded, checks


def audit_contract(workspace: Path, loaded: Dict[str, Any]) -> List[Check]:
    checks: List[Check] = []
    contract_path = workspace / "edge_factory_position_sizing_contract" / "position_sizing_contract.json"
    base = check_file_exists("position_sizing_contract", contract_path, required=True)
    checks.append(base)
    if base.status != "PASS":
        return checks

    try:
        contract = load_json(contract_path)
        if not isinstance(contract, dict):
            checks.append(Check("position_sizing_contract_json", "FAIL", "BLOCKER", "contract is not a JSON object", str(contract_path)))
            return checks
    except Exception as e:
        checks.append(Check("position_sizing_contract_json", "FAIL", "BLOCKER", f"contract JSON load failed: {e}", str(contract_path)))
        return checks

    # Current active contract may still be old 25 USDT market_relative; governor proposal is not applied automatically.
    current_vals: Dict[str, Optional[float]] = {}
    for fam in CURRENT_CONTRACT_BASELINE:
        current_vals[fam] = parse_contract_notional(contract, fam)

    missing = [fam for fam, val in current_vals.items() if val is None]
    if missing:
        checks.append(Check("position_sizing_contract_family_values", "FAIL", "BLOCKER", "some active family notionals could not be parsed", str(contract_path), {"values": current_vals, "missing": missing}))
    else:
        checks.append(Check("position_sizing_contract_family_values", "PASS", "INFO", "active family notionals parsed", str(contract_path), {"values": current_vals}))

    # Compare against governor preview/proposal.
    cap = loaded.get("capital_governor") or {}
    proposed: Dict[str, float] = {}
    for row in cap.get("family_decisions", []) if isinstance(cap.get("family_decisions"), list) else []:
        if isinstance(row, dict) and row.get("family_key"):
            proposed[str(row["family_key"])] = safe_float(row.get("proposed_notional"), 0.0)

    if proposed:
        diffs = {}
        for fam, pval in proposed.items():
            if fam in current_vals and current_vals[fam] is not None:
                if abs(float(current_vals[fam]) - pval) > 1e-9:
                    diffs[fam] = {"contract": current_vals[fam], "governor_proposed": pval}
        if diffs:
            checks.append(Check("contract_vs_governor_proposal", "WARN", "WARNING", "active contract differs from governor proposal; expected because proposal is not auto-applied", str(contract_path), {"diffs": diffs}))
        else:
            checks.append(Check("contract_vs_governor_proposal", "PASS", "INFO", "active contract matches governor proposal", str(contract_path)))

    return checks


def audit_chain_consistency(loaded: Dict[str, Any], strict: bool) -> List[Check]:
    checks: List[Check] = []

    kill = loaded.get("kill_switch") or {}
    paper_gate = str(kill.get("paper_boot_gate", "UNKNOWN"))
    live_gate = str(kill.get("live_gate", "UNKNOWN"))
    paper_fams = list(kill.get("paper_eligible_families") or [])

    if paper_gate == "PAPER_BOOT_ALLOWED_AFTER_PREFLIGHT":
        checks.append(Check("kill_switch_paper_gate", "PASS", "INFO", "kill-switch allows paper after preflight", details={"paper_gate": paper_gate, "paper_families": paper_fams}))
    else:
        checks.append(Check("kill_switch_paper_gate", "FAIL", "BLOCKER", "kill-switch does not allow paper boot", details={"paper_gate": paper_gate, "paper_families": paper_fams}))

    if live_gate.startswith("LIVE_BLOCKED"):
        checks.append(Check("kill_switch_live_gate", "PASS", "INFO", "live is blocked as required", details={"live_gate": live_gate}))
    else:
        checks.append(Check("kill_switch_live_gate", "FAIL", "BLOCKER", "live is not blocked; this is unsafe at current OS stage", details={"live_gate": live_gate}))

    expected_paper = {"old_short", "impulse_long", "market_relative_short", "weak_market_short"}
    if expected_paper.issubset(set(paper_fams)):
        checks.append(Check("paper_family_set", "PASS", "INFO", "expected active families are paper-eligible after preflight", details={"paper_families": paper_fams}))
    else:
        missing = sorted(expected_paper - set(paper_fams))
        checks.append(Check("paper_family_set", "WARN" if not strict else "FAIL", "WARNING" if not strict else "BLOCKER", "some expected active families are not paper-eligible", details={"paper_families": paper_fams, "missing": missing}))

    cap = loaded.get("capital_governor") or {}
    total_current = safe_float(cap.get("total_current_notional_known_families"), 0.0)
    total_proposed = safe_float(cap.get("total_proposed_notional_known_families"), 0.0)
    if total_proposed <= 0:
        checks.append(Check("capital_total", "FAIL", "BLOCKER", "proposed total notional is zero or invalid", details={"total_proposed": total_proposed}))
    elif total_proposed <= 200.0:
        checks.append(Check("capital_total", "PASS", "INFO", "proposed total notional within soft cap", details={"current": total_current, "proposed": total_proposed}))
    else:
        checks.append(Check("capital_total", "WARN" if not strict else "FAIL", "WARNING" if not strict else "BLOCKER", "proposed total notional exceeds soft cap", details={"current": total_current, "proposed": total_proposed}))

    # Verify market_relative reduction made it through governor.
    cap_rows = cap.get("family_decisions") or []
    by_fam = {str(r.get("family_key")): r for r in cap_rows if isinstance(r, dict) and r.get("family_key")}
    mr = by_fam.get("market_relative_short")
    if mr and abs(safe_float(mr.get("proposed_notional"), 0.0) - 12.5) < 1e-9:
        checks.append(Check("market_relative_governor_cut", "PASS", "INFO", "market_relative_short governor cut confirmed at 12.5 USDT"))
    else:
        checks.append(Check("market_relative_governor_cut", "WARN" if not strict else "FAIL", "WARNING" if not strict else "BLOCKER", "market_relative_short 12.5 USDT proposal not confirmed", details={"row": mr}))

    exe = loaded.get("execution_realism") or {}
    exe_rows = exe.get("decisions") or []
    exe_by_fam = {str(r.get("family_key")): r for r in exe_rows if isinstance(r, dict) and r.get("family_key")}
    blockers = []
    for fam in ["old_short", "impulse_long", "market_relative_short", "weak_market_short"]:
        row = exe_by_fam.get(fam)
        if not row or str(row.get("decision")) not in {"EXECUTION_PASS", "EXECUTION_WATCH"}:
            blockers.append({"family": fam, "decision": None if not row else row.get("decision")})
    if blockers:
        checks.append(Check("execution_family_passes", "FAIL", "BLOCKER", "some active families do not pass execution realism", details={"blockers": blockers}))
    else:
        checks.append(Check("execution_family_passes", "PASS", "INFO", "active families pass/watch execution realism"))

    # BPS quality warning, not blocker.
    estimated_bps = []
    for fam, row in exe_by_fam.items():
        if "BPS_ESTIMATED_NOT_NATIVE" in (row.get("risk_flags") or []):
            estimated_bps.append(fam)
    if estimated_bps:
        checks.append(Check("estimated_bps_warning", "WARN", "WARNING", "some execution bps values are estimated; paper drift is mandatory", details={"families": estimated_bps}))
    else:
        checks.append(Check("estimated_bps_warning", "PASS", "INFO", "no estimated bps flag found"))

    lifecycle = loaded.get("family_lifecycle") or {}
    entries = lifecycle.get("entries") or []
    lc_by_fam = {str(e.get("family_key")): e for e in entries if isinstance(e, dict) and e.get("family_key")}
    session = lc_by_fam.get("session_short")
    if session and str(session.get("new_state")) == "DISABLED":
        checks.append(Check("session_short_disabled", "PASS", "INFO", "session_short remains disabled"))
    else:
        checks.append(Check("session_short_disabled", "FAIL" if strict else "WARN", "BLOCKER" if strict else "WARNING", "session_short disabled state not confirmed", details={"session_entry": session}))

    return checks


def determine_decision(checks: List[Check], strict: bool) -> Tuple[str, List[str], List[str]]:
    blockers = [c for c in checks if c.status == "FAIL" or c.severity == "BLOCKER" and c.status == "FAIL"]
    warnings = [c for c in checks if c.status == "WARN"]
    blocker_keys = [c.key for c in blockers]
    warning_keys = [c.key for c in warnings]

    if blockers:
        return "PAPER_BLOCKED", blocker_keys, warning_keys
    if warnings:
        return "PAPER_READY_WITH_WARNINGS_NOT_STARTED", [], warning_keys
    return "PAPER_READY_NOT_STARTED", [], []


def checks_dataframe(checks: List[Check]) -> pd.DataFrame:
    rows = []
    for c in checks:
        rows.append({
            "key": c.key,
            "status": c.status,
            "severity": c.severity,
            "message": c.message,
            "path": c.path,
            "details": json.dumps(c.details, ensure_ascii=False, default=str) if c.details is not None else "",
        })
    return pd.DataFrame(rows)


def write_report_md(path: Path, report: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory OS Preflight Report")
    lines.append("")
    lines.append(f"Generated: `{report['generated_at']}`")
    lines.append(f"Decision: **{report['paper_boot_decision']}**")
    lines.append(f"Live gate: **{report['live_gate']}**")
    lines.append("")

    lines.append("## Executive summary")
    lines.append("")
    lines.append(f"- Workspace: `{report['workspace']}`")
    lines.append(f"- Script dir: `{report['script_dir']}`")
    lines.append(f"- Paper output dir later: `{report['paper_dir']}`")
    lines.append(f"- Blockers: `{len(report['blockers'])}`")
    lines.append(f"- Warnings: `{len(report['warnings'])}`")
    lines.append("")

    if report["blockers"]:
        lines.append("Blockers:")
        for b in report["blockers"]:
            lines.append(f"- `{b}`")
        lines.append("")
    if report["warnings"]:
        lines.append("Warnings:")
        for w in report["warnings"]:
            lines.append(f"- `{w}`")
        lines.append("")

    lines.append("## Required artifacts")
    lines.append("")
    lines.append("| Key | Status | Latest dir | Required file | Modified |")
    lines.append("|---|---:|---|---|---:|")
    for a in report["artifacts"]:
        lines.append(f"| {a['key']} | {a['status']} | `{a['latest_dir']}` | `{a['required_file_path']}` | {a['modified']} |")
    lines.append("")

    lines.append("## Checks")
    lines.append("")
    lines.append("| Status | Severity | Key | Message | Path |")
    lines.append("|---|---:|---|---|---|")
    for c in report["checks"]:
        lines.append(f"| {c['status']} | {c['severity']} | `{c['key']}` | {c['message']} | `{c.get('path')}` |")
    lines.append("")

    lines.append("## Paper boot decision")
    lines.append("")
    lines.append("This preflight does not start paper. It only says whether paper boot is allowed after review.")
    lines.append("")
    lines.append(f"- Paper decision: **{report['paper_boot_decision']}**")
    lines.append(f"- Paper-eligible families: **{', '.join(report['paper_eligible_families']) if report['paper_eligible_families'] else 'none'}**")
    lines.append(f"- Live decision: **{report['live_gate']}**")
    lines.append("")

    lines.append("## Current OS chain")
    lines.append("")
    lines.append("1. Rolling OOS Validator: family robustness checked")
    lines.append("2. Family Lifecycle Engine: official family states created")
    lines.append("3. Adaptive Capital Governor v2: capital proposal created")
    lines.append("4. Execution Realism Checker: costs/stress checked")
    lines.append("5. Kill-Switch Controller: hard stop policy created")
    lines.append("6. Preflight Inspector: current gate completed")
    lines.append("")

    lines.append("## Next step")
    lines.append("")
    lines.append("If paper is not blocked, the next development module should be the autonomous research queue or a supervised paper launcher that reads this preflight gate. Live remains blocked until paper drift validation exists.")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory OS preflight inspector")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--script_dir", default=str(DEFAULT_SCRIPT_DIR))
    p.add_argument("--out_dir", default=None)
    p.add_argument("--strict", action="store_true", help="turn selected warnings into blockers")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    script_dir = Path(args.script_dir)
    paper_dir = workspace / DEFAULT_PAPER_DIR_NAME

    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_os_preflight"
    out_dir = out_root / f"preflight_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    checks: List[Check] = []

    checks.append(Check("workspace_exists", "PASS" if workspace.exists() else "FAIL", "INFO" if workspace.exists() else "BLOCKER", "workspace exists" if workspace.exists() else "workspace missing", str(workspace)))
    checks.append(Check("script_dir_exists", "PASS" if script_dir.exists() else "FAIL", "INFO" if script_dir.exists() else "BLOCKER", "script dir exists" if script_dir.exists() else "script dir missing", str(script_dir)))
    checks.append(Check("paper_dir_status", "PASS" if paper_dir.exists() else "WARN", "INFO" if paper_dir.exists() else "WARNING", "paper dir exists" if paper_dir.exists() else "paper dir does not exist yet; OK before first boot", str(paper_dir)))

    checks.extend(audit_scripts(script_dir))
    artifacts, loaded, artifact_checks = discover_artifacts(workspace)
    checks.extend(artifact_checks)
    checks.extend(audit_contract(workspace, loaded))
    checks.extend(audit_chain_consistency(loaded, strict=args.strict))

    decision, blockers, warnings = determine_decision(checks, strict=args.strict)

    kill = loaded.get("kill_switch") or {}
    paper_families = list(kill.get("paper_eligible_families") or [])
    live_gate = str(kill.get("live_gate", "LIVE_BLOCKED_UNTIL_PAPER_DRIFT_AND_MANUAL_REVIEW"))

    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(workspace),
        "script_dir": str(script_dir),
        "paper_dir": str(paper_dir),
        "strict": bool(args.strict),
        "paper_boot_decision": decision,
        "live_gate": live_gate,
        "paper_eligible_families": paper_families,
        "blockers": blockers,
        "warnings": warnings,
        "artifacts": [asdict(a) for a in artifacts],
        "checks": [asdict(c) for c in checks],
        "output_dir": str(out_dir),
    }

    paper_boot_decision = {
        "generated_at": report["generated_at"],
        "decision": decision,
        "paper_eligible_families": paper_families if decision != "PAPER_BLOCKED" else [],
        "live_gate": live_gate,
        "live_allowed": False,
        "paper_started": False,
        "blockers": blockers,
        "warnings": warnings,
        "required_before_paper_start": [],
        "required_after_paper_start": [
            "edge_factory_live_vs_backtest_drift_monitor.py after closed paper trades exist",
            "paper-vs-backtest drift review",
            "manual live review before any real live use",
        ],
        "note": "This file is a boot decision only. It does not start paper/live trading.",
    }

    if decision == "PAPER_READY_WITH_WARNINGS_NOT_STARTED":
        paper_boot_decision["required_before_paper_start"] = ["review warnings before boot"]
    if decision == "PAPER_BLOCKED":
        paper_boot_decision["required_before_paper_start"] = ["fix blockers and rerun preflight"]

    write_json(out_dir / "preflight_report.json", report)
    write_json(out_dir / "paper_boot_decision.json", paper_boot_decision)
    write_json(out_dir / "required_artifacts.json", [asdict(a) for a in artifacts])
    checks_dataframe(checks).to_csv(out_dir / "preflight_checks.csv", index=False)
    write_report_md(out_dir / "preflight_report.md", report)

    print("EDGE FACTORY OS PREFLIGHT INSPECTOR v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"script_dir: {script_dir}")
    print(f"output_dir: {out_dir}")
    print(f"decision  : {decision}")
    print(f"live_gate : {live_gate}")
    print(f"blockers  : {len(blockers)}")
    print(f"warnings  : {len(warnings)}")
    print("")

    if blockers:
        print("BLOCKERS")
        print("-" * 100)
        for b in blockers:
            print(f"- {b}")
        print("")

    if warnings:
        print("WARNINGS")
        print("-" * 100)
        for w in warnings:
            print(f"- {w}")
        print("")

    print("PAPER / LIVE GATE")
    print("-" * 100)
    print(f"paper_eligible_families: {paper_families}")
    print("paper_started          : False")
    print("live_allowed           : False")
    print("")
    print(f"Open report : {out_dir / 'preflight_report.md'}")
    print(f"Decision    : {out_dir / 'paper_boot_decision.json'}")
    print(f"Checks      : {out_dir / 'preflight_checks.csv'}")

    return 0 if decision != "PAPER_BLOCKED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
