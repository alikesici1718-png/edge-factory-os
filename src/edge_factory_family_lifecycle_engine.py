#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY FAMILY LIFECYCLE ENGINE v1
=======================================

Purpose
-------
Offline decision-state module for the Edge Factory OS.

This module consumes the latest Rolling OOS Validator outputs and converts raw validation
labels into a formal strategy-family lifecycle state:

    CORE_ACTIVE
    DIVERSIFIER_ACTIVE
    ACTIVE_REDUCED
    BACKUP_ONLY
    DISABLED
    RESEARCH_CANDIDATE
    REJECTED

It does NOT start paper/live trading.
It does NOT place orders.
It does NOT edit loggers.
It does NOT overwrite the sizing contract.

It produces a lifecycle state file that later modules can consume:
    - adaptive capital governor
    - kill-switch controller
    - autonomous research queue
    - paper/live preflight

Run
---
    python "C:\Users\alike\edge_factory_family_lifecycle_engine.py"

Optional explicit OOS folder:
    python "C:\Users\alike\edge_factory_family_lifecycle_engine.py" ^
      --oos_dir "C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_rolling_oos_validator\rolling_oos_20260510_165749"

Default workspace:
    C:\Users\alike\OneDrive\Desktop\edge_lab_new

Outputs
-------
    <workspace>\edge_factory_family_lifecycle\lifecycle_YYYYMMDD_HHMMSS\
        family_lifecycle_state.json
        family_lifecycle_report.md
        family_lifecycle_summary.csv
        family_lifecycle_actions.json

Current known architecture
--------------------------
old_short             = CORE_ENGINE
impulse_long          = HIGH_PRIORITY_DIVERSIFIER
market_relative_short = CAPPED_HALF_SIZE
weak_market_short     = BACKUP_ONLY
session_short         = DISABLED

Important design rule
---------------------
This engine is intentionally conservative. Strong historical/OOS result alone does not
automatically promote a backup family to full core. Promotion requires multiple modules later:
rolling OOS + execution realism + live/paper drift + bad-day/regime behavior.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_SCRIPT_DIR = Path(r"C:\Users\alike")

CURRENT_FAMILY_POLICY = {
    "old_short": {
        "current_role": "CORE_ENGINE",
        "current_state": "CORE_ACTIVE",
        "current_notional": 50.0,
        "priority": 100,
        "max_positions": 3,
        "promotion_allowed": False,
        "reduction_allowed": True,
        "disable_allowed": True,
    },
    "impulse_long": {
        "current_role": "HIGH_PRIORITY_DIVERSIFIER",
        "current_state": "DIVERSIFIER_ACTIVE",
        "current_notional": 50.0,
        "priority": 150,
        "max_positions": 2,
        "promotion_allowed": False,
        "reduction_allowed": True,
        "disable_allowed": True,
    },
    "market_relative_short": {
        "current_role": "CAPPED_HALF_SIZE",
        "current_state": "ACTIVE_REDUCED",
        "current_notional": 25.0,
        "priority": 70,
        "max_positions": 3,
        "promotion_allowed": True,
        "reduction_allowed": True,
        "disable_allowed": True,
    },
    "weak_market_short": {
        "current_role": "BACKUP_ONLY",
        "current_state": "BACKUP_ONLY",
        "current_notional": 25.0,
        "priority": 30,
        "max_positions": 2,
        "promotion_allowed": True,
        "reduction_allowed": True,
        "disable_allowed": True,
    },
    "session_short": {
        "current_role": "DISABLED",
        "current_state": "DISABLED",
        "current_notional": 0.0,
        "priority": 0,
        "max_positions": 0,
        "promotion_allowed": True,
        "reduction_allowed": False,
        "disable_allowed": True,
    },
}

ACTIVE_FAMILIES = ["old_short", "impulse_long", "market_relative_short", "weak_market_short"]
DISABLED_FAMILIES = ["session_short"]

# Optional new research candidates that appeared in the OOS scan and may deserve queueing,
# but should not be automatically activated by this lifecycle engine.
RESEARCH_CANDIDATE_PREFIX_ALLOWLIST = [
    "rel_extreme_reversion_short",
    "ret60_reversal_short",
    "relative_weakness_snapback_long",
    "market_panic_rebound_long",
    "capitulation_reversal_long",
]


@dataclass
class LifecycleEntry:
    family_key: str
    current_role: str
    previous_state: str
    validation_decision: str
    confidence: str
    new_state: str
    lifecycle_action: str
    capital_action_hint: str
    notional_current: float
    notional_floor_hint: float
    notional_ceiling_hint: float
    priority_current: int
    priority_hint: int
    max_positions_current: int
    max_positions_hint: int
    allow_paper_later: bool
    allow_live_later: bool
    requires_execution_check: bool
    requires_drift_check_after_paper: bool
    reasons: List[str]
    raw_validation: Dict[str, Any]


@dataclass
class LifecycleAction:
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
        return int(safe_float(x, default=default))
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


def discover_oos_dir(workspace: Path, explicit: Optional[Path]) -> Optional[Path]:
    if explicit:
        return explicit if explicit.exists() else None
    root = workspace / "edge_factory_rolling_oos_validator"
    return latest_child_dir(root, "rolling_oos_")


def load_oos_decisions(oos_dir: Path) -> List[Dict[str, Any]]:
    path = oos_dir / "rolling_oos_decisions.json"
    if not path.exists():
        return []
    obj = load_json(path)
    if isinstance(obj, list):
        return obj
    return []


def decision_score(decision: str) -> int:
    return {
        "STRONG_CANDIDATE": 5,
        "PASS_CANDIDATE": 3,
        "WATCH_WEAK_OOS": 1,
        "REDUCE_OR_BACKUP_ONLY": -1,
        "REJECT_OR_DISABLE": -5,
        "INSUFFICIENT_DATA": -2,
        "NO_USABLE_DATA": -3,
    }.get(str(decision), 0)


def extract_metrics(raw: Dict[str, Any]) -> Dict[str, Any]:
    metrics = raw.get("metrics") or {}
    oos = raw.get("oos_metrics") or {}
    window = raw.get("window_metrics") or {}
    symbol = raw.get("symbol_metrics") or {}
    return {
        "trade_count": safe_int(metrics.get("trade_count")),
        "total_pnl": safe_float(metrics.get("total_pnl")),
        "avg_pnl": safe_float(metrics.get("avg_pnl")),
        "win_rate": safe_float(metrics.get("win_rate")),
        "profit_factor": safe_float(metrics.get("profit_factor")),
        "max_drawdown": safe_float(metrics.get("max_drawdown")),
        "test_trade_count": safe_int((oos.get("test") or {}).get("trade_count")) if isinstance(oos.get("test"), dict) else 0,
        "test_avg_pnl": safe_float((oos.get("test") or {}).get("avg_pnl")) if isinstance(oos.get("test"), dict) else 0.0,
        "positive_valid_window_rate": window.get("positive_valid_window_rate"),
        "valid_window_count": safe_int(window.get("valid_window_count")),
        "max_consecutive_negative_windows": safe_int(window.get("max_consecutive_negative_windows")),
        "positive_valid_symbol_rate": symbol.get("positive_valid_symbol_rate"),
        "valid_symbol_count": safe_int(symbol.get("valid_symbol_count")),
    }


def is_research_candidate(family_key: str, raw: Dict[str, Any]) -> bool:
    if family_key in CURRENT_FAMILY_POLICY:
        return False
    if family_key in {"unknown", "nan", "{}", "none", "null", ""}:
        return False
    if any(family_key.startswith(p) for p in RESEARCH_CANDIDATE_PREFIX_ALLOWLIST):
        return True
    # Also allow any non-active family with large enough sample and strong validation.
    m = extract_metrics(raw)
    return raw.get("decision") == "STRONG_CANDIDATE" and m["trade_count"] >= 250 and m["profit_factor"] >= 1.5


def lifecycle_for_known_family(family_key: str, raw: Optional[Dict[str, Any]]) -> LifecycleEntry:
    policy = CURRENT_FAMILY_POLICY[family_key]
    previous_state = policy["current_state"]
    current_role = policy["current_role"]
    notional = float(policy["current_notional"])
    priority = int(policy["priority"])
    max_pos = int(policy["max_positions"])

    if raw is None:
        return LifecycleEntry(
            family_key=family_key,
            current_role=current_role,
            previous_state=previous_state,
            validation_decision="NO_USABLE_DATA",
            confidence="low",
            new_state=previous_state if family_key in DISABLED_FAMILIES else "BACKUP_ONLY",
            lifecycle_action="HOLD_OR_REPAIR_DATA",
            capital_action_hint="NO_INCREASE",
            notional_current=notional,
            notional_floor_hint=0.0 if family_key != "old_short" else min(notional, 25.0),
            notional_ceiling_hint=notional,
            priority_current=priority,
            priority_hint=priority,
            max_positions_current=max_pos,
            max_positions_hint=max_pos,
            allow_paper_later=False,
            allow_live_later=False,
            requires_execution_check=True,
            requires_drift_check_after_paper=True,
            reasons=["No OOS validation row found for known family; do not promote or increase."],
            raw_validation={},
        )

    validation_decision = str(raw.get("decision", "UNKNOWN"))
    confidence = str(raw.get("confidence", "low"))
    reasons = list(raw.get("reasons") or [])
    metrics = extract_metrics(raw)
    score = decision_score(validation_decision)

    # Base defaults.
    new_state = previous_state
    lifecycle_action = "KEEP_CURRENT_ROLE"
    capital_action = "KEEP_CURRENT_NOTIONAL"
    floor = 0.0
    ceiling = notional
    priority_hint = priority
    max_pos_hint = max_pos
    allow_paper = family_key not in DISABLED_FAMILIES
    allow_live = False  # live requires later paper/drift/execution checks no matter what
    requires_execution = True
    requires_drift = True
    extra_reasons: List[str] = []

    if family_key == "old_short":
        if validation_decision in {"STRONG_CANDIDATE", "PASS_CANDIDATE"}:
            new_state = "CORE_ACTIVE"
            lifecycle_action = "KEEP_CORE_ACTIVE"
            capital_action = "KEEP_50_USDT_BASELINE"
            floor = 25.0
            ceiling = 50.0
            priority_hint = 100
            max_pos_hint = 3
            extra_reasons.append("old_short remains the core engine; do not increase until execution realism and paper drift exist.")
        elif validation_decision == "WATCH_WEAK_OOS":
            new_state = "CORE_ACTIVE"
            lifecycle_action = "KEEP_CORE_BUT_WATCH"
            capital_action = "NO_INCREASE_CONSIDER_25_TO_50_RANGE"
            floor = 25.0
            ceiling = 50.0
        elif validation_decision == "REDUCE_OR_BACKUP_ONLY":
            new_state = "ACTIVE_REDUCED"
            lifecycle_action = "REDUCE_CORE_RISK"
            capital_action = "REDUCE_TOWARD_25_USDT"
            floor = 25.0
            ceiling = 50.0
            max_pos_hint = min(max_pos, 2)
        else:
            new_state = "BACKUP_ONLY"
            lifecycle_action = "CORE_FAILS_VALIDATION_REVIEW_REQUIRED"
            capital_action = "REDUCE_TO_MINIMUM_OR_DISABLE_AFTER_CONFIRMATION"
            floor = 0.0
            ceiling = 25.0
            max_pos_hint = 1
            allow_paper = False

    elif family_key == "impulse_long":
        if validation_decision in {"STRONG_CANDIDATE", "PASS_CANDIDATE"}:
            new_state = "DIVERSIFIER_ACTIVE"
            lifecycle_action = "KEEP_DIVERSIFIER_ACTIVE"
            capital_action = "KEEP_50_USDT_BASELINE"
            floor = 25.0
            ceiling = 50.0
            priority_hint = 150
            max_pos_hint = 2
            extra_reasons.append("impulse_long remains the high-priority diversifier; still requires execution and paper drift before live.")
        elif validation_decision == "WATCH_WEAK_OOS":
            new_state = "DIVERSIFIER_ACTIVE"
            lifecycle_action = "KEEP_DIVERSIFIER_BUT_WATCH"
            capital_action = "NO_INCREASE"
            floor = 25.0
            ceiling = 50.0
        elif validation_decision == "REDUCE_OR_BACKUP_ONLY":
            new_state = "BACKUP_ONLY"
            lifecycle_action = "DEMOTE_DIVERSIFIER_TO_BACKUP"
            capital_action = "REDUCE_TO_25_USDT_OR_LESS"
            floor = 0.0
            ceiling = 25.0
            max_pos_hint = 1
        else:
            new_state = "DISABLED"
            lifecycle_action = "DISABLE_DIVERSIFIER_CANDIDATE"
            capital_action = "ZERO_NOTIONAL"
            floor = 0.0
            ceiling = 0.0
            priority_hint = 0
            max_pos_hint = 0
            allow_paper = False

    elif family_key == "market_relative_short":
        if validation_decision == "STRONG_CANDIDATE":
            new_state = "ACTIVE_REDUCED"
            lifecycle_action = "KEEP_CAPPED_REDUCED_DESPITE_STRENGTH"
            capital_action = "KEEP_25_USDT_UNTIL_BAD_DAY_AND_EXECUTION_CLEAR"
            floor = 25.0
            ceiling = 25.0
            priority_hint = 70
            max_pos_hint = 3
            extra_reasons.append("Prior bad-day analysis already forced half-size; strong OOS alone is not enough to restore full size.")
        elif validation_decision in {"PASS_CANDIDATE", "WATCH_WEAK_OOS", "REDUCE_OR_BACKUP_ONLY"}:
            new_state = "ACTIVE_REDUCED" if validation_decision != "REDUCE_OR_BACKUP_ONLY" else "BACKUP_ONLY"
            lifecycle_action = "KEEP_REDUCED_OR_BACKUP"
            capital_action = "KEEP_25_USDT_CEILING_NO_INCREASE"
            floor = 0.0 if validation_decision == "REDUCE_OR_BACKUP_ONLY" else 12.5
            ceiling = 25.0
            priority_hint = 50 if validation_decision == "REDUCE_OR_BACKUP_ONLY" else 70
            max_pos_hint = 2 if validation_decision == "REDUCE_OR_BACKUP_ONLY" else 3
            extra_reasons.append("Validation supports the earlier decision: this family should not return to full size now.")
        else:
            new_state = "DISABLED"
            lifecycle_action = "DISABLE_MARKET_RELATIVE"
            capital_action = "ZERO_NOTIONAL"
            floor = 0.0
            ceiling = 0.0
            priority_hint = 0
            max_pos_hint = 0
            allow_paper = False

    elif family_key == "weak_market_short":
        if validation_decision == "STRONG_CANDIDATE":
            new_state = "BACKUP_ONLY"
            lifecycle_action = "KEEP_BACKUP_ONLY_WITH_PROMOTION_WATCH"
            capital_action = "KEEP_25_USDT_BACKUP_SIZE"
            floor = 12.5
            ceiling = 25.0
            priority_hint = 30
            max_pos_hint = 2
            extra_reasons.append("Strong OOS, but current architecture treats weak_market_short as backup; promotion requires execution realism and paper drift later.")
        elif validation_decision == "PASS_CANDIDATE":
            new_state = "BACKUP_ONLY"
            lifecycle_action = "KEEP_BACKUP_ONLY"
            capital_action = "KEEP_25_USDT_OR_LESS"
            floor = 0.0
            ceiling = 25.0
        elif validation_decision in {"WATCH_WEAK_OOS", "REDUCE_OR_BACKUP_ONLY"}:
            new_state = "BACKUP_ONLY"
            lifecycle_action = "KEEP_BACKUP_BUT_RESTRICT"
            capital_action = "NO_INCREASE_CONSIDER_12_5_USDT"
            floor = 0.0
            ceiling = 25.0
            max_pos_hint = 1
        else:
            new_state = "DISABLED"
            lifecycle_action = "DISABLE_BACKUP_FAMILY"
            capital_action = "ZERO_NOTIONAL"
            floor = 0.0
            ceiling = 0.0
            priority_hint = 0
            max_pos_hint = 0
            allow_paper = False

    elif family_key == "session_short":
        if validation_decision == "STRONG_CANDIDATE":
            new_state = "RESEARCH_CANDIDATE"
            lifecycle_action = "KEEP_DISABLED_BUT_RESEARCH"
            capital_action = "ZERO_NOTIONAL_UNTIL_REVALIDATED"
            floor = 0.0
            ceiling = 0.0
            priority_hint = 0
            max_pos_hint = 0
            allow_paper = False
            extra_reasons.append("session_short is disabled in current system; historical pass is not enough because prior architecture excluded it.")
        else:
            new_state = "DISABLED"
            lifecycle_action = "KEEP_DISABLED"
            capital_action = "ZERO_NOTIONAL"
            floor = 0.0
            ceiling = 0.0
            priority_hint = 0
            max_pos_hint = 0
            allow_paper = False
            extra_reasons.append("session_short remains disabled.")

    # Universal hard guardrails.
    if metrics["trade_count"] < 100 and family_key in ACTIVE_FAMILIES:
        new_state = "BACKUP_ONLY"
        lifecycle_action = "INSUFFICIENT_SAMPLE_RESTRICT"
        capital_action = "NO_INCREASE"
        ceiling = min(ceiling, notional)
        allow_live = False
        extra_reasons.append("Active family has insufficient sample in validator; restrict until more evidence.")

    if metrics["test_avg_pnl"] < 0 and validation_decision not in {"STRONG_CANDIDATE", "PASS_CANDIDATE"}:
        allow_paper = False
        allow_live = False
        extra_reasons.append("Negative OOS/test average blocks paper promotion.")

    all_reasons = reasons + extra_reasons

    return LifecycleEntry(
        family_key=family_key,
        current_role=current_role,
        previous_state=previous_state,
        validation_decision=validation_decision,
        confidence=confidence,
        new_state=new_state,
        lifecycle_action=lifecycle_action,
        capital_action_hint=capital_action,
        notional_current=notional,
        notional_floor_hint=floor,
        notional_ceiling_hint=ceiling,
        priority_current=priority,
        priority_hint=priority_hint,
        max_positions_current=max_pos,
        max_positions_hint=max_pos_hint,
        allow_paper_later=allow_paper,
        allow_live_later=allow_live,
        requires_execution_check=requires_execution,
        requires_drift_check_after_paper=requires_drift,
        reasons=all_reasons,
        raw_validation=raw,
    )


def lifecycle_for_research_candidate(family_key: str, raw: Dict[str, Any]) -> LifecycleEntry:
    m = extract_metrics(raw)
    validation_decision = str(raw.get("decision", "UNKNOWN"))
    confidence = str(raw.get("confidence", "low"))
    reasons = list(raw.get("reasons") or [])
    reasons.append("Non-master family detected as research candidate only; not eligible for immediate activation.")

    strong_enough = validation_decision == "STRONG_CANDIDATE" and m["trade_count"] >= 250
    state = "RESEARCH_CANDIDATE" if strong_enough else "REJECTED"
    action = "QUEUE_FOR_DEEP_RESEARCH" if strong_enough else "IGNORE_OR_ARCHIVE"

    return LifecycleEntry(
        family_key=family_key,
        current_role="RESEARCH_ONLY",
        previous_state="UNTRACKED",
        validation_decision=validation_decision,
        confidence=confidence,
        new_state=state,
        lifecycle_action=action,
        capital_action_hint="ZERO_NOTIONAL_RESEARCH_ONLY",
        notional_current=0.0,
        notional_floor_hint=0.0,
        notional_ceiling_hint=0.0,
        priority_current=0,
        priority_hint=0,
        max_positions_current=0,
        max_positions_hint=0,
        allow_paper_later=False,
        allow_live_later=False,
        requires_execution_check=True,
        requires_drift_check_after_paper=True,
        reasons=reasons,
        raw_validation=raw,
    )


def build_lifecycle(decisions: List[Dict[str, Any]], include_research_candidates: bool) -> List[LifecycleEntry]:
    by_family: Dict[str, Dict[str, Any]] = {}
    for raw in decisions:
        fam = str(raw.get("family_key", "")).strip()
        if not fam:
            continue
        # Keep the strongest/largest row for duplicates.
        if fam not in by_family:
            by_family[fam] = raw
        else:
            old = by_family[fam]
            old_score = decision_score(str(old.get("decision", "")))
            new_score = decision_score(str(raw.get("decision", "")))
            old_trades = extract_metrics(old)["trade_count"]
            new_trades = extract_metrics(raw)["trade_count"]
            if (new_score, new_trades) > (old_score, old_trades):
                by_family[fam] = raw

    entries: List[LifecycleEntry] = []
    for fam in CURRENT_FAMILY_POLICY:
        entries.append(lifecycle_for_known_family(fam, by_family.get(fam)))

    if include_research_candidates:
        candidates = []
        for fam, raw in by_family.items():
            if is_research_candidate(fam, raw):
                candidates.append(lifecycle_for_research_candidate(fam, raw))
        # Keep research candidates sorted by rough quality.
        candidates = sorted(
            candidates,
            key=lambda e: (
                decision_score(e.validation_decision),
                safe_float(e.raw_validation.get("metrics", {}).get("profit_factor"), 0.0),
                safe_int(e.raw_validation.get("metrics", {}).get("trade_count"), 0),
            ),
            reverse=True,
        )
        entries.extend(candidates[:20])

    return entries


def build_actions(entries: List[LifecycleEntry], oos_dir: Path) -> List[LifecycleAction]:
    actions: List[LifecycleAction] = []

    for e in entries:
        if e.family_key in CURRENT_FAMILY_POLICY:
            if e.new_state in {"CORE_ACTIVE", "DIVERSIFIER_ACTIVE", "ACTIVE_REDUCED", "BACKUP_ONLY"}:
                actions.append(LifecycleAction(
                    action_key=f"execution_check_{e.family_key}",
                    family_key=e.family_key,
                    severity="REQUIRED_BEFORE_LIVE",
                    title=f"Run execution realism check for {e.family_key}",
                    reason="Lifecycle allows future paper/live consideration, but execution cost/spread/slippage feasibility is not yet verified.",
                    safe_offline=True,
                    suggested_next_module="edge_factory_execution_realism_checker.py",
                    inputs=["family_lifecycle_state.json", "historical trade/symbol data", "position_sizing_contract.json"],
                    outputs=["execution_realism_report.json"],
                ))

            if e.allow_paper_later:
                actions.append(LifecycleAction(
                    action_key=f"preflight_later_{e.family_key}",
                    family_key=e.family_key,
                    severity="LATER",
                    title=f"Allow {e.family_key} into later paper preflight only after remaining validators",
                    reason="Paper boot is not the current step. This flag means the family is not blocked by lifecycle alone.",
                    safe_offline=True,
                    suggested_next_module="edge_factory_os_preflight_inspector.py",
                    inputs=["family_lifecycle_state.json", "capital_policy_proposal.json", "kill_switch_policy.json"],
                    outputs=["preflight_report.json"],
                ))

        elif e.new_state == "RESEARCH_CANDIDATE":
            actions.append(LifecycleAction(
                action_key=f"research_queue_{e.family_key}",
                family_key=e.family_key,
                severity="RESEARCH",
                title=f"Queue research candidate {e.family_key}",
                reason="Candidate appears strong in broad scan but is not part of MASTER_UPPER_SYSTEM. It needs isolated validation, not activation.",
                safe_offline=True,
                suggested_next_module="edge_factory_autonomous_research_queue.py",
                inputs=["family_lifecycle_state.json", str(oos_dir / "normalized_oos_trades.csv")],
                outputs=["research_queue.json"],
            ))

    # Global next modules.
    actions.append(LifecycleAction(
        action_key="build_adaptive_capital_governor_v2",
        family_key="SYSTEM",
        severity="NEXT_CORE_MODULE",
        title="Build adaptive capital governor v2",
        reason="Lifecycle state now exists. The next OS layer should convert lifecycle states into capital policy proposals without editing the live contract automatically.",
        safe_offline=True,
        suggested_next_module="edge_factory_adaptive_capital_governor_v2.py",
        inputs=["family_lifecycle_state.json", "guarded allocator outputs", "position_sizing_contract.json"],
        outputs=["capital_policy_proposal.json", "capital_governor_report.md"],
    ))

    actions.append(LifecycleAction(
        action_key="build_execution_realism_checker",
        family_key="SYSTEM",
        severity="NEXT_VALIDATOR",
        title="Build execution realism checker",
        reason="Before any paper/live step, the OS must estimate whether theoretical edge survives fees, spread, slippage, and liquidity constraints.",
        safe_offline=True,
        suggested_next_module="edge_factory_execution_realism_checker.py",
        inputs=["family_lifecycle_state.json", "normalized_oos_trades.csv", "market/symbol data if available"],
        outputs=["execution_realism_report.json"],
    ))

    return actions


def entries_to_summary_df(entries: List[LifecycleEntry]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for e in entries:
        m = extract_metrics(e.raw_validation) if e.raw_validation else {}
        rows.append({
            "family_key": e.family_key,
            "current_role": e.current_role,
            "previous_state": e.previous_state,
            "validation_decision": e.validation_decision,
            "confidence": e.confidence,
            "new_state": e.new_state,
            "lifecycle_action": e.lifecycle_action,
            "capital_action_hint": e.capital_action_hint,
            "notional_current": e.notional_current,
            "notional_floor_hint": e.notional_floor_hint,
            "notional_ceiling_hint": e.notional_ceiling_hint,
            "priority_current": e.priority_current,
            "priority_hint": e.priority_hint,
            "max_positions_current": e.max_positions_current,
            "max_positions_hint": e.max_positions_hint,
            "allow_paper_later": e.allow_paper_later,
            "allow_live_later": e.allow_live_later,
            "requires_execution_check": e.requires_execution_check,
            "requires_drift_check_after_paper": e.requires_drift_check_after_paper,
            "trade_count": m.get("trade_count"),
            "total_pnl": m.get("total_pnl"),
            "avg_pnl": m.get("avg_pnl"),
            "win_rate": m.get("win_rate"),
            "profit_factor": m.get("profit_factor"),
            "test_trade_count": m.get("test_trade_count"),
            "test_avg_pnl": m.get("test_avg_pnl"),
            "positive_valid_window_rate": m.get("positive_valid_window_rate"),
            "valid_window_count": m.get("valid_window_count"),
            "positive_valid_symbol_rate": m.get("positive_valid_symbol_rate"),
            "valid_symbol_count": m.get("valid_symbol_count"),
            "reason_summary": " | ".join(e.reasons[:6]),
        })
    return pd.DataFrame(rows)


def write_report_md(path: Path, workspace: Path, oos_dir: Path, entries: List[LifecycleEntry], actions: List[LifecycleAction], summary_df: pd.DataFrame) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory Family Lifecycle Report")
    lines.append("")
    lines.append(f"Generated: `{datetime.now().isoformat(timespec='seconds')}`")
    lines.append(f"Workspace: `{workspace}`")
    lines.append(f"OOS source: `{oos_dir}`")
    lines.append("")

    lines.append("## Executive state")
    lines.append("")
    lines.append("| Family | Role | Validation | New state | Action | Current notional | Ceiling hint | Paper later | Live later |")
    lines.append("|---|---:|---:|---:|---|---:|---:|---:|---:|")
    for _, r in summary_df.iterrows():
        lines.append(
            f"| {r['family_key']} | {r['current_role']} | {r['validation_decision']} | {r['new_state']} | "
            f"{r['lifecycle_action']} | {r['notional_current']} | {r['notional_ceiling_hint']} | "
            f"{r['allow_paper_later']} | {r['allow_live_later']} |"
        )
    lines.append("")

    lines.append("## Known-family interpretation")
    lines.append("")
    for e in entries:
        if e.family_key not in CURRENT_FAMILY_POLICY:
            continue
        lines.append(f"### {e.family_key}")
        lines.append("")
        lines.append(f"State: **{e.previous_state} → {e.new_state}**")
        lines.append(f"Lifecycle action: `{e.lifecycle_action}`")
        lines.append(f"Capital hint: `{e.capital_action_hint}`")
        lines.append(f"Notional range hint: `{e.notional_floor_hint}` to `{e.notional_ceiling_hint}` USDT")
        lines.append("")
        lines.append("Reasons:")
        for reason in e.reasons:
            lines.append(f"- {reason}")
        lines.append("")

    research = [e for e in entries if e.family_key not in CURRENT_FAMILY_POLICY]
    if research:
        lines.append("## Research-only candidates")
        lines.append("")
        lines.append("These are not part of MASTER_UPPER_SYSTEM. They are candidates for isolated research only, not activation.")
        lines.append("")
        lines.append("| Candidate | Validation | Trades | PF | State | Action |")
        lines.append("|---|---:|---:|---:|---:|---|")
        for e in research:
            m = extract_metrics(e.raw_validation)
            lines.append(
                f"| {e.family_key} | {e.validation_decision} | {m.get('trade_count')} | {m.get('profit_factor')} | "
                f"{e.new_state} | {e.lifecycle_action} |"
            )
        lines.append("")

    lines.append("## Next actions")
    lines.append("")
    lines.append("| Severity | Family | Action | Next module | Reason |")
    lines.append("|---|---:|---|---|---|")
    for a in actions:
        lines.append(f"| {a.severity} | {a.family_key} | {a.title} | `{a.suggested_next_module}` | {a.reason} |")
    lines.append("")

    lines.append("## Hard rules applied")
    lines.append("")
    lines.append("- Strong OOS does not automatically promote backup families.")
    lines.append("- Live is always blocked at this stage; `allow_live_later` remains false until paper drift and execution checks exist.")
    lines.append("- `market_relative_short` cannot regain full size merely from this result because prior bad-day analysis already justified half-size/capping.")
    lines.append("- `session_short` remains disabled unless reintroduced by a dedicated research cycle.")
    lines.append("- Research-only candidates receive zero notional and must go through isolated validation.")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory family lifecycle engine")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE), help="edge_lab_new workspace")
    p.add_argument("--oos_dir", default=None, help="explicit rolling_oos_YYYYMMDD_HHMMSS folder")
    p.add_argument("--out_dir", default=None, help="optional output root")
    p.add_argument("--include_research_candidates", action="store_true", help="include non-master strong candidates as research-only entries")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    oos_dir = discover_oos_dir(workspace, Path(args.oos_dir) if args.oos_dir else None)

    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_family_lifecycle"
    out_dir = out_root / f"lifecycle_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    if oos_dir is None:
        err = {
            "error": "No rolling OOS output directory found.",
            "expected_root": str(workspace / "edge_factory_rolling_oos_validator"),
            "hint": "Run edge_factory_rolling_oos_validator.py first or pass --oos_dir explicitly.",
        }
        write_json(out_dir / "fatal_error.json", err)
        print("EDGE FACTORY FAMILY LIFECYCLE ENGINE v1")
        print("No rolling OOS output directory found.")
        print(f"Details: {out_dir / 'fatal_error.json'}")
        return 2

    decisions = load_oos_decisions(oos_dir)
    if not decisions:
        err = {
            "error": "No rolling_oos_decisions.json rows found.",
            "oos_dir": str(oos_dir),
            "hint": "Check rolling OOS validator output.",
        }
        write_json(out_dir / "fatal_error.json", err)
        print("EDGE FACTORY FAMILY LIFECYCLE ENGINE v1")
        print("No OOS decisions found.")
        print(f"Details: {out_dir / 'fatal_error.json'}")
        return 2

    entries = build_lifecycle(decisions, include_research_candidates=args.include_research_candidates)
    actions = build_actions(entries, oos_dir=oos_dir)
    summary_df = entries_to_summary_df(entries)

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(workspace),
        "oos_dir": str(oos_dir),
        "engine_version": "v1",
        "known_family_policy": CURRENT_FAMILY_POLICY,
        "entries": [asdict(e) for e in entries],
        "actions": [asdict(a) for a in actions],
        "hard_rules": [
            "Strong OOS alone does not promote backup to core.",
            "Live remains blocked until execution realism and paper drift checks exist.",
            "market_relative_short remains capped because prior bad-day work justified half-size.",
            "session_short remains disabled unless a dedicated research cycle reintroduces it.",
        ],
    }

    write_json(out_dir / "family_lifecycle_state.json", state)
    write_json(out_dir / "family_lifecycle_actions.json", [asdict(a) for a in actions])
    summary_df.to_csv(out_dir / "family_lifecycle_summary.csv", index=False)
    write_report_md(out_dir / "family_lifecycle_report.md", workspace, oos_dir, entries, actions, summary_df)

    print("EDGE FACTORY FAMILY LIFECYCLE ENGINE v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"oos_dir   : {oos_dir}")
    print(f"output_dir: {out_dir}")
    print("")
    print("LIFECYCLE STATE")
    print("-" * 100)
    for e in entries:
        if e.family_key not in CURRENT_FAMILY_POLICY:
            continue
        print(
            f"{e.family_key:24s} role={e.current_role:24s} validation={e.validation_decision:22s} "
            f"state={e.previous_state:18s}->{e.new_state:18s} action={e.lifecycle_action}"
        )
        print(f"  capital: {e.capital_action_hint} | notional_hint={e.notional_floor_hint}..{e.notional_ceiling_hint} | paper_later={e.allow_paper_later} live_later={e.allow_live_later}")
        for r in e.reasons[:3]:
            print(f"  - {r}")
    research_count = len([e for e in entries if e.family_key not in CURRENT_FAMILY_POLICY])
    if research_count:
        print(f"\nResearch-only candidates included: {research_count}")
    print("")
    print("NEXT SYSTEM ACTIONS")
    print("-" * 100)
    for a in actions[-2:]:
        print(f"{a.severity:18s} -> {a.suggested_next_module}: {a.title}")
    print("")
    print(f"Open report: {out_dir / 'family_lifecycle_report.md'}")
    print(f"State      : {out_dir / 'family_lifecycle_state.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
