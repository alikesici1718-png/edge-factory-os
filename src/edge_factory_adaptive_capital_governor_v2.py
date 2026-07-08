#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY ADAPTIVE CAPITAL GOVERNOR v2
=========================================

Purpose
-------
Offline capital-policy brain for the Edge Factory OS.

This module consumes the latest family lifecycle state and current sizing contract, then
produces a proposed capital allocation policy.

It does NOT start paper/live trading.
It does NOT place orders.
It does NOT edit logger files.
It does NOT overwrite position_sizing_contract.json by default.

It only writes a proposal:
    - which family should receive how much notional
    - which family is capped/reduced/disabled
    - which changes are allowed now vs blocked until execution/paper drift checks

Current architecture input expected
-----------------------------------
Lifecycle state:
    <workspace>\edge_factory_family_lifecycle\lifecycle_YYYYMMDD_HHMMSS\family_lifecycle_state.json

Sizing contract:
    <workspace>\edge_factory_position_sizing_contract\position_sizing_contract.json

Run
---
    python "C:\Users\alike\edge_factory_adaptive_capital_governor_v2.py"

Optional explicit lifecycle folder:
    python "C:\Users\alike\edge_factory_adaptive_capital_governor_v2.py" ^
      --lifecycle_dir "C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_family_lifecycle\lifecycle_20260510_170035"

Outputs
-------
    <workspace>\edge_factory_adaptive_capital_governor_v2\capital_governor_YYYYMMDD_HHMMSS\
        capital_policy_proposal.json
        capital_policy_summary.csv
        capital_governor_report.md
        proposed_sizing_contract_preview.json
        capital_actions.json

Decision principles
-------------------
1) Strong OOS alone does not increase live size.
2) Live is blocked until execution realism and paper drift exist.
3) Core/diversifier may keep baseline if lifecycle remains strong.
4) Backup-only means no increase; reduced target unless explicitly protected.
5) Disabled/research-only families receive zero notional.
6) The current contract is never overwritten automatically.
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
DEFAULT_BASE_EQUITY = 1000.0

KNOWN_FAMILIES = [
    "old_short",
    "impulse_long",
    "market_relative_short",
    "weak_market_short",
    "session_short",
]

CURRENT_EXPECTED_NOTIONAL = {
    "old_short": 50.0,
    "impulse_long": 50.0,
    "market_relative_short": 25.0,
    "weak_market_short": 25.0,
    "session_short": 0.0,
}

CURRENT_PRIORITY = {
    "old_short": 100,
    "impulse_long": 150,
    "market_relative_short": 70,
    "weak_market_short": 30,
    "session_short": 0,
}

CURRENT_MAX_POSITIONS = {
    "old_short": 3,
    "impulse_long": 2,
    "market_relative_short": 3,
    "weak_market_short": 2,
    "session_short": 0,
}


@dataclass
class FamilyCapitalDecision:
    family_key: str
    lifecycle_state: str
    lifecycle_action: str
    validation_decision: str
    confidence: str
    current_notional: float
    proposed_notional: float
    proposed_pct_of_equity: float
    notional_delta: float
    change_pct: Optional[float]
    current_priority: int
    proposed_priority: int
    current_max_positions: int
    proposed_max_positions: int
    capital_action: str
    risk_tier: str
    allow_paper_later: bool
    allow_live_later: bool
    blocked_until: List[str]
    reasons: List[str]
    raw_entry: Dict[str, Any]


@dataclass
class CapitalAction:
    action_key: str
    family_key: str
    severity: str
    title: str
    reason: str
    safe_offline: bool
    suggested_next_module: str
    inputs: List[str]
    outputs: List[str]


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


def pct_change(new: float, old: float) -> Optional[float]:
    if abs(old) < 1e-12:
        return None
    return (new - old) / abs(old)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def latest_child_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def discover_lifecycle_dir(workspace: Path, explicit: Optional[Path]) -> Optional[Path]:
    if explicit:
        return explicit if explicit.exists() else None
    return latest_child_dir(workspace / "edge_factory_family_lifecycle", "lifecycle_")


def load_lifecycle_state(lifecycle_dir: Path) -> Dict[str, Any]:
    path = lifecycle_dir / "family_lifecycle_state.json"
    if not path.exists():
        raise FileNotFoundError(f"family_lifecycle_state.json not found: {path}")
    obj = load_json(path)
    if not isinstance(obj, dict):
        raise ValueError(f"lifecycle state is not a JSON object: {path}")
    return obj


def load_contract(workspace: Path, explicit: Optional[Path]) -> Tuple[Optional[Path], Dict[str, Any]]:
    path = explicit if explicit else workspace / "edge_factory_position_sizing_contract" / "position_sizing_contract.json"
    if not path.exists():
        return path, {}
    try:
        obj = load_json(path)
        return path, obj if isinstance(obj, dict) else {"_non_dict_json": obj}
    except Exception:
        return path, {}


def recursive_find_family_value(obj: Any, family_key: str, preferred_keys: List[str]) -> Optional[float]:
    if isinstance(obj, dict):
        if family_key in obj:
            direct = obj[family_key]
            direct_float = None
            try:
                direct_float = float(direct)
            except Exception:
                direct_float = None
            if direct_float is not None and math.isfinite(direct_float):
                return direct_float
            if isinstance(direct, dict):
                for k in preferred_keys:
                    if k in direct:
                        v = safe_float(direct[k], default=float("nan"))
                        if math.isfinite(v):
                            return v
        for k in preferred_keys + ["notional_by_family", "family_notional", "expected_notional_by_family"]:
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


def parse_current_contract_notional(contract: Dict[str, Any], family_key: str, fallback: float) -> float:
    preferred = [
        "expected_notional",
        "expected_notional_usdt",
        "notional",
        "notional_usdt",
        "default_notional",
        "target_notional",
        "target_notional_usdt",
    ]
    found = recursive_find_family_value(contract, family_key, preferred)
    return fallback if found is None else float(found)


def entry_metric(entry: Dict[str, Any], key: str, default: float = 0.0) -> float:
    raw = entry.get("raw_validation") or {}
    metrics = raw.get("metrics") or {}
    return safe_float(metrics.get(key), default=default)


def entry_oos_metric(entry: Dict[str, Any], key: str, default: float = 0.0) -> float:
    raw = entry.get("raw_validation") or {}
    oos = raw.get("oos_metrics") or {}
    test = oos.get("test") if isinstance(oos.get("test"), dict) else {}
    return safe_float(test.get(key), default=default)


def capital_decision_for_entry(
    entry: Dict[str, Any],
    current_contract: Dict[str, Any],
    base_equity: float,
    mode: str,
) -> FamilyCapitalDecision:
    fam = str(entry.get("family_key", "unknown"))
    state = str(entry.get("new_state", entry.get("lifecycle_state", "UNKNOWN")))
    lifecycle_action = str(entry.get("lifecycle_action", "UNKNOWN"))
    validation = str(entry.get("validation_decision", "UNKNOWN"))
    confidence = str(entry.get("confidence", "low"))
    raw_reasons = list(entry.get("reasons") or [])

    fallback_current = CURRENT_EXPECTED_NOTIONAL.get(fam, safe_float(entry.get("notional_current"), 0.0))
    current_notional = parse_current_contract_notional(current_contract, fam, fallback=fallback_current)

    ceiling = safe_float(entry.get("notional_ceiling_hint"), current_notional)
    floor = safe_float(entry.get("notional_floor_hint"), 0.0)
    priority_current = CURRENT_PRIORITY.get(fam, safe_int(entry.get("priority_current"), 0))
    priority_hint = safe_int(entry.get("priority_hint"), priority_current)
    max_pos_current = CURRENT_MAX_POSITIONS.get(fam, safe_int(entry.get("max_positions_current"), 0))
    max_pos_hint = safe_int(entry.get("max_positions_hint"), max_pos_current)
    allow_paper = bool(entry.get("allow_paper_later", False))
    allow_live = bool(entry.get("allow_live_later", False))

    proposed = current_notional
    proposed_priority = priority_hint
    proposed_max_pos = max_pos_hint
    capital_action = "KEEP"
    risk_tier = "UNKNOWN"
    blocked_until: List[str] = []
    reasons: List[str] = []

    avg_pnl = entry_metric(entry, "avg_pnl", 0.0)
    profit_factor = entry_metric(entry, "profit_factor", 0.0)
    test_avg_pnl = entry_oos_metric(entry, "avg_pnl", 0.0)
    trade_count = entry_metric(entry, "trade_count", 0.0)

    # State-based allocation rules.
    if state == "CORE_ACTIVE":
        risk_tier = "CORE"
        proposed = min(max(current_notional, floor), ceiling)
        if validation in {"STRONG_CANDIDATE", "PASS_CANDIDATE"} and avg_pnl > 0 and test_avg_pnl > 0:
            proposed = min(50.0, ceiling if ceiling > 0 else 50.0)
            capital_action = "KEEP_CORE_BASELINE"
            reasons.append("Core family passed lifecycle validation; keep baseline size, no increase.")
        else:
            proposed = min(current_notional, 25.0)
            capital_action = "REDUCE_CORE_UNTIL_REVALIDATED"
            reasons.append("Core family did not cleanly pass validation; reduce until revalidated.")

    elif state == "DIVERSIFIER_ACTIVE":
        risk_tier = "DIVERSIFIER"
        proposed = min(max(current_notional, floor), ceiling)
        if validation in {"STRONG_CANDIDATE", "PASS_CANDIDATE"} and avg_pnl > 0 and test_avg_pnl > 0:
            proposed = min(50.0, ceiling if ceiling > 0 else 50.0)
            capital_action = "KEEP_DIVERSIFIER_BASELINE"
            reasons.append("Diversifier passed lifecycle validation; keep baseline size, no increase.")
        else:
            proposed = min(current_notional, 25.0)
            capital_action = "REDUCE_DIVERSIFIER_UNTIL_REVALIDATED"
            reasons.append("Diversifier validation is not clean; reduce until revalidated.")

    elif state == "ACTIVE_REDUCED":
        risk_tier = "REDUCED_ACTIVE"
        proposed = min(current_notional, ceiling)
        proposed = max(proposed, floor) if ceiling > 0 else 0.0
        capital_action = "KEEP_REDUCED_CEILING"
        reasons.append("Family is active-reduced; keep capped size and block increases.")

    elif state == "BACKUP_ONLY":
        risk_tier = "BACKUP"
        # Backup-only default: reduce fragile families, preserve known backup if strong.
        if fam == "weak_market_short" and validation == "STRONG_CANDIDATE":
            proposed = min(current_notional, ceiling, 25.0)
            proposed = max(proposed, 12.5)
            capital_action = "KEEP_BACKUP_SIZE_PROMOTION_WATCH"
            reasons.append("weak_market_short is strong but remains backup-only; keep 25 USDT ceiling, no promotion.")
        elif fam == "market_relative_short":
            # This is the first real adaptive cut: lifecycle demoted it from active-reduced to backup-only.
            if mode == "aggressive_cut":
                proposed = 0.0
                capital_action = "CUT_MARKET_RELATIVE_TO_ZERO"
                reasons.append("market_relative_short is backup-only and weak in rolling windows; aggressive mode cuts to zero.")
            else:
                proposed = min(12.5, ceiling)
                capital_action = "REDUCE_MARKET_RELATIVE_TO_HALF_BACKUP_SIZE"
                reasons.append("market_relative_short was demoted to backup-only; reduce from 25 to 12.5 USDT proposal.")
        else:
            proposed = min(current_notional, ceiling, 25.0)
            if validation not in {"STRONG_CANDIDATE", "PASS_CANDIDATE"}:
                proposed = min(proposed, 12.5)
                capital_action = "RESTRICT_BACKUP_SIZE"
                reasons.append("Backup family lacks strong validation; restrict size.")
            else:
                capital_action = "KEEP_BACKUP_CAPPED"
                reasons.append("Backup family passed validation but remains capped.")
        proposed_priority = min(priority_hint, priority_current)
        proposed_max_pos = min(max_pos_hint, max_pos_current)

    elif state in {"DISABLED", "REJECTED"}:
        risk_tier = "DISABLED"
        proposed = 0.0
        proposed_priority = 0
        proposed_max_pos = 0
        capital_action = "ZERO_NOTIONAL"
        allow_paper = False
        allow_live = False
        reasons.append("Family is disabled/rejected; force zero notional in proposal.")

    elif state == "RESEARCH_CANDIDATE":
        risk_tier = "RESEARCH_ONLY"
        proposed = 0.0
        proposed_priority = 0
        proposed_max_pos = 0
        capital_action = "ZERO_NOTIONAL_RESEARCH_ONLY"
        allow_paper = False
        allow_live = False
        blocked_until.append("isolated_research_validation")
        reasons.append("Research candidate is not part of MASTER_UPPER_SYSTEM; zero notional.")

    else:
        risk_tier = "UNKNOWN_RESTRICTED"
        proposed = 0.0
        proposed_priority = 0
        proposed_max_pos = 0
        capital_action = "UNKNOWN_STATE_ZERO_NOTIONAL"
        allow_paper = False
        allow_live = False
        reasons.append("Unknown lifecycle state; zero notional for safety.")

    # Universal gates.
    if bool(entry.get("requires_execution_check", True)):
        blocked_until.append("execution_realism_check")
    if bool(entry.get("requires_drift_check_after_paper", True)):
        blocked_until.append("paper_drift_check_after_boot")

    # No live allowed at this stage, even if entry says otherwise.
    allow_live = False
    if "paper_drift_check_after_boot" not in blocked_until:
        blocked_until.append("paper_drift_check_after_boot")
    if "kill_switch_policy" not in blocked_until:
        blocked_until.append("kill_switch_policy")

    # Mode-level conservatism.
    if mode == "freeze" and fam in CURRENT_EXPECTED_NOTIONAL:
        proposed = CURRENT_EXPECTED_NOTIONAL[fam]
        capital_action = "FREEZE_CURRENT_POLICY"
        reasons.append("Freeze mode selected; proposal equals current expected policy.")
    elif mode == "conservative" and proposed > current_notional:
        proposed = current_notional
        reasons.append("Conservative mode blocks notional increases.")

    # Hard safety rounding.
    proposed = max(0.0, round(float(proposed), 4))
    if proposed == 0.0:
        proposed_priority = 0
        proposed_max_pos = 0
        allow_paper = False

    # Add lifecycle reasons last but avoid excessive bloat.
    for r in raw_reasons[:6]:
        if r not in reasons:
            reasons.append(r)

    return FamilyCapitalDecision(
        family_key=fam,
        lifecycle_state=state,
        lifecycle_action=lifecycle_action,
        validation_decision=validation,
        confidence=confidence,
        current_notional=current_notional,
        proposed_notional=proposed,
        proposed_pct_of_equity=proposed / base_equity if base_equity > 0 else 0.0,
        notional_delta=proposed - current_notional,
        change_pct=pct_change(proposed, current_notional),
        current_priority=priority_current,
        proposed_priority=proposed_priority,
        current_max_positions=max_pos_current,
        proposed_max_positions=proposed_max_pos,
        capital_action=capital_action,
        risk_tier=risk_tier,
        allow_paper_later=allow_paper,
        allow_live_later=allow_live,
        blocked_until=sorted(set(blocked_until)),
        reasons=reasons,
        raw_entry=entry,
    )


def build_capital_decisions(
    lifecycle_state: Dict[str, Any],
    contract: Dict[str, Any],
    base_equity: float,
    mode: str,
    include_research: bool,
) -> List[FamilyCapitalDecision]:
    entries = lifecycle_state.get("entries") or []
    if not isinstance(entries, list):
        entries = []

    by_family: Dict[str, Dict[str, Any]] = {}
    for e in entries:
        if not isinstance(e, dict):
            continue
        fam = str(e.get("family_key", "")).strip()
        if not fam:
            continue
        by_family[fam] = e

    ordered: List[str] = []
    for fam in KNOWN_FAMILIES:
        if fam in by_family:
            ordered.append(fam)
    if include_research:
        for fam in sorted(by_family):
            if fam not in ordered:
                ordered.append(fam)

    decisions: List[FamilyCapitalDecision] = []
    for fam in ordered:
        decisions.append(capital_decision_for_entry(by_family[fam], contract, base_equity, mode))
    return decisions


def build_policy_proposal(
    workspace: Path,
    lifecycle_dir: Path,
    contract_path: Optional[Path],
    decisions: List[FamilyCapitalDecision],
    base_equity: float,
    mode: str,
) -> Dict[str, Any]:
    total_current = sum(d.current_notional for d in decisions if d.family_key in KNOWN_FAMILIES)
    total_proposed = sum(d.proposed_notional for d in decisions if d.family_key in KNOWN_FAMILIES)
    active_proposed = {d.family_key: d.proposed_notional for d in decisions if d.proposed_notional > 0}

    max_total_notional_soft = min(base_equity * 0.20, 200.0)  # 20% soft cap at 1000 equity = 200
    max_total_notional_hard = min(base_equity * 0.30, 300.0)

    status = "OK"
    warnings: List[str] = []
    if total_proposed > max_total_notional_soft:
        status = "WARN_SOFT_TOTAL_NOTIONAL_CAP"
        warnings.append(f"total proposed notional {total_proposed} exceeds soft cap {max_total_notional_soft}")
    if total_proposed > max_total_notional_hard:
        status = "BLOCK_HARD_TOTAL_NOTIONAL_CAP"
        warnings.append(f"total proposed notional {total_proposed} exceeds hard cap {max_total_notional_hard}")

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "engine_version": "adaptive_capital_governor_v2",
        "mode": mode,
        "workspace": str(workspace),
        "lifecycle_dir": str(lifecycle_dir),
        "source_contract": str(contract_path) if contract_path else None,
        "base_equity": base_equity,
        "status": status,
        "warnings": warnings,
        "total_current_notional_known_families": round(total_current, 4),
        "total_proposed_notional_known_families": round(total_proposed, 4),
        "total_notional_delta": round(total_proposed - total_current, 4),
        "active_proposed_families": active_proposed,
        "soft_total_notional_cap": max_total_notional_soft,
        "hard_total_notional_cap": max_total_notional_hard,
        "family_decisions": [asdict(d) for d in decisions],
        "hard_rules": [
            "No live permission at this stage.",
            "No automatic overwrite of position_sizing_contract.json.",
            "Strong OOS can preserve current allocation but cannot increase allocation without execution and paper drift checks.",
            "market_relative_short demoted to backup-only is reduced by default in conservative mode.",
            "Research-only candidates receive zero notional.",
        ],
    }


def build_contract_preview(policy: Dict[str, Any]) -> Dict[str, Any]:
    decisions = policy.get("family_decisions") or []
    family_notional = {}
    family_pct = {}
    family_priority = {}
    family_max_positions = {}
    family_state = {}
    allow_paper = {}
    allow_live = {}

    base_equity = safe_float(policy.get("base_equity"), DEFAULT_BASE_EQUITY)

    for d in decisions:
        fam = d.get("family_key")
        if not fam:
            continue
        notional = safe_float(d.get("proposed_notional"), 0.0)
        family_notional[fam] = notional
        family_pct[fam] = notional / base_equity if base_equity > 0 else 0.0
        family_priority[fam] = safe_int(d.get("proposed_priority"), 0)
        family_max_positions[fam] = safe_int(d.get("proposed_max_positions"), 0)
        family_state[fam] = d.get("lifecycle_state")
        allow_paper[fam] = bool(d.get("allow_paper_later"))
        allow_live[fam] = bool(d.get("allow_live_later"))

    return {
        "preview_only": True,
        "do_not_use_as_live_contract_until_reviewed": True,
        "generated_at": policy.get("generated_at"),
        "source": "edge_factory_adaptive_capital_governor_v2",
        "base_equity": base_equity,
        "expected_notional_by_family": family_notional,
        "notional_pct_by_family": family_pct,
        "priority_by_family": family_priority,
        "max_positions_by_family": family_max_positions,
        "lifecycle_state_by_family": family_state,
        "allow_paper_later_by_family": allow_paper,
        "allow_live_later_by_family": allow_live,
        "notes": [
            "This is a proposal preview, not the active position_sizing_contract.json.",
            "Apply only after execution realism, kill-switch policy, and manual review.",
        ],
    }


def build_actions(policy: Dict[str, Any]) -> List[CapitalAction]:
    actions: List[CapitalAction] = []
    decisions = policy.get("family_decisions") or []

    for d in decisions:
        fam = d.get("family_key")
        delta = safe_float(d.get("notional_delta"), 0.0)
        proposed = safe_float(d.get("proposed_notional"), 0.0)
        action = str(d.get("capital_action", ""))
        if abs(delta) > 1e-9:
            severity = "CAPITAL_CHANGE_PROPOSED"
            if proposed == 0:
                severity = "ZERO_NOTIONAL_PROPOSED"
            elif delta < 0:
                severity = "REDUCTION_PROPOSED"
            elif delta > 0:
                severity = "INCREASE_PROPOSED_BLOCKED_BY_REVIEW"
            actions.append(CapitalAction(
                action_key=f"capital_change_{fam}",
                family_key=str(fam),
                severity=severity,
                title=f"Capital proposal for {fam}: {action}",
                reason=f"Current notional {d.get('current_notional')} -> proposed {d.get('proposed_notional')}",
                safe_offline=True,
                suggested_next_module="manual_review_or_contract_builder_later",
                inputs=["capital_policy_proposal.json", "proposed_sizing_contract_preview.json"],
                outputs=["reviewed_position_sizing_contract.json later"],
            ))

    actions.append(CapitalAction(
        action_key="build_execution_realism_checker",
        family_key="SYSTEM",
        severity="NEXT_VALIDATOR",
        title="Build execution realism checker",
        reason="Capital proposal still ignores live spread, fees, slippage, fill risk, and symbol liquidity. This must be checked before paper/live.",
        safe_offline=True,
        suggested_next_module="edge_factory_execution_realism_checker.py",
        inputs=["capital_policy_proposal.json", "family_lifecycle_state.json", "historical/symbol data"],
        outputs=["execution_realism_report.json", "execution_risk_flags.csv"],
    ))

    actions.append(CapitalAction(
        action_key="build_kill_switch_controller",
        family_key="SYSTEM",
        severity="SAFETY_REQUIRED",
        title="Build kill-switch controller after execution realism",
        reason="No paper/live boot should happen until family/system stop rules exist.",
        safe_offline=True,
        suggested_next_module="edge_factory_kill_switch_controller.py",
        inputs=["capital_policy_proposal.json", "execution_realism_report.json", "family_lifecycle_state.json"],
        outputs=["kill_switch_policy.json"],
    ))

    return actions


def summary_df(decisions: List[FamilyCapitalDecision]) -> pd.DataFrame:
    rows = []
    for d in decisions:
        rows.append({
            "family_key": d.family_key,
            "lifecycle_state": d.lifecycle_state,
            "validation_decision": d.validation_decision,
            "confidence": d.confidence,
            "risk_tier": d.risk_tier,
            "capital_action": d.capital_action,
            "current_notional": d.current_notional,
            "proposed_notional": d.proposed_notional,
            "notional_delta": d.notional_delta,
            "change_pct": d.change_pct,
            "proposed_pct_of_equity": d.proposed_pct_of_equity,
            "current_priority": d.current_priority,
            "proposed_priority": d.proposed_priority,
            "current_max_positions": d.current_max_positions,
            "proposed_max_positions": d.proposed_max_positions,
            "allow_paper_later": d.allow_paper_later,
            "allow_live_later": d.allow_live_later,
            "blocked_until": ",".join(d.blocked_until),
            "reason_summary": " | ".join(d.reasons[:6]),
        })
    return pd.DataFrame(rows)


def write_report_md(path: Path, policy: Dict[str, Any], actions: List[CapitalAction]) -> None:
    decisions = policy.get("family_decisions") or []
    lines: List[str] = []
    lines.append("# Edge Factory Adaptive Capital Governor v2 Report")
    lines.append("")
    lines.append(f"Generated: `{policy.get('generated_at')}`")
    lines.append(f"Mode: **{policy.get('mode')}**")
    lines.append(f"Status: **{policy.get('status')}**")
    lines.append(f"Lifecycle source: `{policy.get('lifecycle_dir')}`")
    lines.append(f"Sizing contract source: `{policy.get('source_contract')}`")
    lines.append("")

    lines.append("## Executive capital proposal")
    lines.append("")
    lines.append(f"Current known-family notional total: **{policy.get('total_current_notional_known_families')} USDT**")
    lines.append(f"Proposed known-family notional total: **{policy.get('total_proposed_notional_known_families')} USDT**")
    lines.append(f"Delta: **{policy.get('total_notional_delta')} USDT**")
    lines.append("")
    if policy.get("warnings"):
        lines.append("Warnings:")
        for w in policy.get("warnings"):
            lines.append(f"- {w}")
        lines.append("")

    lines.append("| Family | State | Validation | Risk tier | Capital action | Current | Proposed | Delta | Priority | Max pos | Paper later | Live later |")
    lines.append("|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|")
    for d in decisions:
        lines.append(
            f"| {d.get('family_key')} | {d.get('lifecycle_state')} | {d.get('validation_decision')} | {d.get('risk_tier')} | "
            f"{d.get('capital_action')} | {d.get('current_notional')} | {d.get('proposed_notional')} | "
            f"{round(safe_float(d.get('notional_delta')), 4)} | {d.get('proposed_priority')} | {d.get('proposed_max_positions')} | "
            f"{d.get('allow_paper_later')} | {d.get('allow_live_later')} |"
        )
    lines.append("")

    lines.append("## Family reasoning")
    lines.append("")
    for d in decisions:
        lines.append(f"### {d.get('family_key')}")
        lines.append("")
        lines.append(f"Action: **{d.get('capital_action')}**")
        lines.append(f"Notional: `{d.get('current_notional')}` → `{d.get('proposed_notional')}` USDT")
        lines.append(f"Blocked until: `{', '.join(d.get('blocked_until') or [])}`")
        lines.append("")
        lines.append("Reasons:")
        for r in (d.get("reasons") or [])[:10]:
            lines.append(f"- {r}")
        lines.append("")

    lines.append("## Next actions")
    lines.append("")
    lines.append("| Severity | Family | Action | Next module | Reason |")
    lines.append("|---|---:|---|---|---|")
    for a in actions:
        lines.append(f"| {a.severity} | {a.family_key} | {a.title} | `{a.suggested_next_module}` | {a.reason} |")
    lines.append("")

    lines.append("## Hard rules")
    lines.append("")
    for r in policy.get("hard_rules") or []:
        lines.append(f"- {r}")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("This is a proposal, not an applied contract. The active `position_sizing_contract.json` is not modified.")
    lines.append("The most important current adaptive change is whether `market_relative_short` should be cut from 25 USDT to 12.5 USDT after lifecycle demotion to backup-only.")
    lines.append("Paper/live remains blocked until execution realism, kill-switch, and later paper drift checks exist.")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory adaptive capital governor v2")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE), help="edge_lab_new workspace")
    p.add_argument("--lifecycle_dir", default=None, help="explicit lifecycle_YYYYMMDD_HHMMSS folder")
    p.add_argument("--contract", default=None, help="explicit position_sizing_contract.json path")
    p.add_argument("--out_dir", default=None, help="optional output root")
    p.add_argument("--base_equity", type=float, default=DEFAULT_BASE_EQUITY)
    p.add_argument("--mode", choices=["conservative", "freeze", "aggressive_cut"], default="conservative")
    p.add_argument("--include_research", action="store_true", help="include research candidates if lifecycle state contains them")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    lifecycle_dir = discover_lifecycle_dir(workspace, Path(args.lifecycle_dir) if args.lifecycle_dir else None)

    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_adaptive_capital_governor_v2"
    out_dir = out_root / f"capital_governor_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    if lifecycle_dir is None:
        err = {
            "error": "No lifecycle output directory found.",
            "expected_root": str(workspace / "edge_factory_family_lifecycle"),
            "hint": "Run edge_factory_family_lifecycle_engine.py first or pass --lifecycle_dir explicitly.",
        }
        write_json(out_dir / "fatal_error.json", err)
        print("EDGE FACTORY ADAPTIVE CAPITAL GOVERNOR v2")
        print("No lifecycle directory found.")
        print(f"Details: {out_dir / 'fatal_error.json'}")
        return 2

    lifecycle_state = load_lifecycle_state(lifecycle_dir)
    contract_path, contract = load_contract(workspace, Path(args.contract) if args.contract else None)

    decisions = build_capital_decisions(
        lifecycle_state=lifecycle_state,
        contract=contract,
        base_equity=args.base_equity,
        mode=args.mode,
        include_research=args.include_research,
    )
    policy = build_policy_proposal(
        workspace=workspace,
        lifecycle_dir=lifecycle_dir,
        contract_path=contract_path,
        decisions=decisions,
        base_equity=args.base_equity,
        mode=args.mode,
    )
    preview = build_contract_preview(policy)
    actions = build_actions(policy)
    df = summary_df(decisions)

    write_json(out_dir / "capital_policy_proposal.json", policy)
    write_json(out_dir / "proposed_sizing_contract_preview.json", preview)
    write_json(out_dir / "capital_actions.json", [asdict(a) for a in actions])
    df.to_csv(out_dir / "capital_policy_summary.csv", index=False)
    write_report_md(out_dir / "capital_governor_report.md", policy, actions)

    print("EDGE FACTORY ADAPTIVE CAPITAL GOVERNOR v2")
    print("=" * 100)
    print(f"workspace    : {workspace}")
    print(f"lifecycle_dir: {lifecycle_dir}")
    print(f"contract     : {contract_path}")
    print(f"mode         : {args.mode}")
    print(f"output_dir   : {out_dir}")
    print("")
    print("CAPITAL PROPOSAL")
    print("-" * 100)
    print(f"current_total : {policy['total_current_notional_known_families']} USDT")
    print(f"proposed_total: {policy['total_proposed_notional_known_families']} USDT")
    print(f"delta         : {policy['total_notional_delta']} USDT")
    print("")
    for d in decisions:
        print(
            f"{d.family_key:24s} state={d.lifecycle_state:18s} validation={d.validation_decision:22s} "
            f"action={d.capital_action:42s} {d.current_notional:8.4f} -> {d.proposed_notional:8.4f} USDT "
            f"paper_later={d.allow_paper_later} live_later={d.allow_live_later}"
        )
        for r in d.reasons[:3]:
            print(f"  - {r}")
    print("")
    print("NEXT ACTIONS")
    print("-" * 100)
    for a in actions[-2:]:
        print(f"{a.severity:18s} -> {a.suggested_next_module}: {a.title}")
    print("")
    print(f"Open report : {out_dir / 'capital_governor_report.md'}")
    print(f"Proposal    : {out_dir / 'capital_policy_proposal.json'}")
    print(f"Preview     : {out_dir / 'proposed_sizing_contract_preview.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
