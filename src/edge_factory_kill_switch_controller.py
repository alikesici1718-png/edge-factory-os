#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY KILL-SWITCH CONTROLLER v1
======================================

Purpose
-------
Offline safety-policy generator for the Edge Factory OS.

This module consumes the latest execution realism output and produces hard stop rules for
future paper/live operation. It does NOT monitor live logs in real time yet. It defines the
policy that a future runtime monitor/preflight layer must enforce.

Inputs
------
Latest execution realism folder:
    <workspace>\edge_factory_execution_realism_checker\execution_realism_YYYYMMDD_HHMMSS

It reads:
    execution_realism_decisions.json

Through that file it also knows:
    capital governor source
    lifecycle source
    OOS trades source

Outputs
-------
    <workspace>\edge_factory_kill_switch_controller\kill_switch_YYYYMMDD_HHMMSS\
        kill_switch_policy.json
        kill_switch_rules.csv
        kill_switch_report.md
        kill_switch_actions.json
        paper_boot_gate.json

Run
---
    python "C:\Users\alike\edge_factory_kill_switch_controller.py"

Optional explicit execution folder:
    python "C:\Users\alike\edge_factory_kill_switch_controller.py" ^
      --execution_dir "C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_execution_realism_checker\execution_realism_20260510_170729"

Core idea
---------
The OS must know in advance when to stop a family/system. This module turns lifecycle,
capital, and execution results into enforceable rules:
    - system-level max daily loss
    - system-level max drawdown
    - missing log / heartbeat stop
    - family daily loss stop
    - family rolling trade stop
    - family consecutive loss stop
    - execution drift stop
    - backup-family stricter gating
    - live remains blocked until paper evidence exists

Important
---------
This policy is conservative by design. It is not a trading signal and it does not modify
any active contract or logger.
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
DEFAULT_BASE_EQUITY = 1000.0

KNOWN_FAMILIES = [
    "old_short",
    "impulse_long",
    "market_relative_short",
    "weak_market_short",
    "session_short",
]

STATE_RISK_MULTIPLIER = {
    "CORE_ACTIVE": 1.00,
    "DIVERSIFIER_ACTIVE": 0.90,
    "ACTIVE_REDUCED": 0.65,
    "BACKUP_ONLY": 0.50,
    "DISABLED": 0.00,
    "RESEARCH_CANDIDATE": 0.00,
    "REJECTED": 0.00,
}

STATE_MIN_TRADES_BEFORE_HARD_DISABLE = {
    "CORE_ACTIVE": 60,
    "DIVERSIFIER_ACTIVE": 50,
    "ACTIVE_REDUCED": 40,
    "BACKUP_ONLY": 30,
    "DISABLED": 0,
}


@dataclass
class KillRule:
    scope: str                 # SYSTEM / FAMILY
    family_key: str            # SYSTEM or family
    rule_key: str
    severity: str              # INFO / WARN / REDUCE / DISABLE / HARD_STOP
    metric: str
    operator: str
    threshold: Any
    lookback: str
    action: str
    enabled: bool
    paper_applies: bool
    live_applies: bool
    reason: str


@dataclass
class FamilySafetyState:
    family_key: str
    lifecycle_state: str
    execution_decision: str
    proposed_notional: float
    paper_allowed_by_inputs: bool
    live_allowed_by_inputs: bool
    paper_gate: str
    live_gate: str
    risk_tier: str
    safety_score: int
    daily_loss_stop_usdt: float
    rolling_loss_stop_usdt: float
    max_consecutive_losses: int
    min_trades_before_disable: int
    rule_count: int
    reasons: List[str]


@dataclass
class KillAction:
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


def discover_execution_dir(workspace: Path, explicit: Optional[Path]) -> Optional[Path]:
    if explicit:
        return explicit if explicit.exists() else None
    return latest_child_dir(workspace / "edge_factory_execution_realism_checker", "execution_realism_")


def load_execution_decisions(execution_dir: Path) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    path = execution_dir / "execution_realism_decisions.json"
    if not path.exists():
        raise FileNotFoundError(f"execution_realism_decisions.json not found: {path}")
    obj = load_json(path)
    if not isinstance(obj, dict):
        raise ValueError("execution_realism_decisions.json is not a JSON object")
    context = obj.get("context") or {}
    decisions = obj.get("decisions") or []
    if not isinstance(decisions, list):
        decisions = []
    return context, decisions


def family_decision_map(decisions: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for d in decisions:
        if isinstance(d, dict) and d.get("family_key"):
            out[str(d["family_key"])] = d
    return out


def safety_score_for_execution(d: Dict[str, Any]) -> Tuple[int, List[str]]:
    score = 0
    reasons: List[str] = []
    decision = str(d.get("decision", "UNKNOWN"))
    state = str(d.get("lifecycle_state", "UNKNOWN"))
    flags = list(d.get("risk_flags") or [])
    net_avg_bps = safe_float(d.get("net_avg_bps"), 0.0)
    net_pf = safe_float(d.get("net_profit_factor"), 0.0)
    net_wr = safe_float(d.get("net_win_rate"), 0.0)
    proposed = safe_float(d.get("proposed_notional"), 0.0)

    if proposed <= 0 or decision == "ZERO_NOTIONAL_OR_DISABLED":
        return -99, ["Zero notional or disabled; no trading allowed."]

    if decision == "EXECUTION_PASS":
        score += 3
        reasons.append("Execution realism passed.")
    elif decision == "EXECUTION_WATCH":
        score += 1
        reasons.append("Execution realism is watch-level, not clean pass.")
    elif decision == "EXECUTION_REDUCE":
        score -= 2
        reasons.append("Execution realism suggests reduction.")
    elif decision == "EXECUTION_BLOCK_PAPER":
        score -= 5
        reasons.append("Execution realism blocks paper.")

    if state in {"CORE_ACTIVE", "DIVERSIFIER_ACTIVE"}:
        score += 1
        reasons.append("Lifecycle is active/core-grade.")
    elif state == "BACKUP_ONLY":
        score -= 1
        reasons.append("Backup-only lifecycle receives stricter kill-switch treatment.")
    elif state in {"DISABLED", "REJECTED", "RESEARCH_CANDIDATE"}:
        score -= 5
        reasons.append("Lifecycle is not tradable.")

    if net_avg_bps >= 5:
        score += 1
    elif net_avg_bps <= 0:
        score -= 3
        reasons.append("Net average bps is non-positive.")

    if net_pf >= 1.20:
        score += 1
    elif net_pf < 1.0:
        score -= 3
        reasons.append("Net profit factor is below 1.")

    if net_wr < 0.45:
        score -= 1
        reasons.append("Net win rate is weak.")

    high_risk_flags = {
        "NEGATIVE_NET_AVG_BPS",
        "NET_PF_BELOW_1",
        "NEGATIVE_BREAKEVEN_COST_BUFFER",
        "LOW_POSITIVE_SYMBOL_RATE",
        "PRIOR_BAD_DAY_FAMILY",
        "BPS_ESTIMATED_NOT_NATIVE",
    }
    hit_flags = [f for f in flags if f in high_risk_flags]
    score -= min(3, len(hit_flags))
    if hit_flags:
        reasons.append("Risk flags detected: " + ", ".join(hit_flags[:6]))

    return score, reasons


def classify_gate(score: int, d: Dict[str, Any]) -> Tuple[str, str]:
    decision = str(d.get("decision", "UNKNOWN"))
    proposed = safe_float(d.get("proposed_notional"), 0.0)
    state = str(d.get("lifecycle_state", "UNKNOWN"))

    if proposed <= 0 or state in {"DISABLED", "REJECTED", "RESEARCH_CANDIDATE"}:
        return "BLOCKED_ZERO_OR_DISABLED", "LIVE_BLOCKED"
    if decision == "EXECUTION_BLOCK_PAPER" or score <= -3:
        return "PAPER_BLOCKED_BY_SAFETY", "LIVE_BLOCKED"
    if decision == "EXECUTION_REDUCE" or score <= 0:
        return "PAPER_ALLOWED_REDUCED_ONLY", "LIVE_BLOCKED"
    if state == "BACKUP_ONLY":
        return "PAPER_ALLOWED_BACKUP_ONLY", "LIVE_BLOCKED"
    return "PAPER_ALLOWED_AFTER_PREFLIGHT", "LIVE_BLOCKED"


def compute_loss_stops(base_equity: float, proposed_notional: float, state: str, family_key: str) -> Tuple[float, float, int]:
    """
    Returns daily_loss_stop_usdt, rolling_loss_stop_usdt, max_consecutive_losses.
    Conservative and proportional to proposed notional, but with minimum practical values.
    """
    if proposed_notional <= 0:
        return 0.0, 0.0, 0

    mult = STATE_RISK_MULTIPLIER.get(state, 0.50)

    # Daily stop: roughly 20% of family notional for active core, tighter for backup.
    daily = proposed_notional * 0.20 * mult
    daily = max(1.0, daily)

    # Rolling loss stop: smaller, used over 20 closed trades.
    rolling = proposed_notional * 0.10 * mult
    rolling = max(0.75, rolling)

    # Family-specific extra conservatism.
    if family_key == "market_relative_short":
        daily *= 0.70
        rolling *= 0.70
    if family_key == "weak_market_short":
        daily *= 0.80
        rolling *= 0.80

    if state == "CORE_ACTIVE":
        max_losses = 8
    elif state == "DIVERSIFIER_ACTIVE":
        max_losses = 7
    elif state == "ACTIVE_REDUCED":
        max_losses = 6
    elif state == "BACKUP_ONLY":
        max_losses = 5
    else:
        max_losses = 0

    return round(daily, 4), round(rolling, 4), max_losses


def build_system_rules(base_equity: float, total_proposed_notional: float, paper_families: List[str]) -> List[KillRule]:
    rules: List[KillRule] = []

    # Conservative system-level paper stops. These are not exchange liquidation controls;
    # they are OS-level trading stop conditions.
    system_daily_loss = max(5.0, min(base_equity * 0.015, total_proposed_notional * 0.12))
    system_rolling_loss = max(7.5, min(base_equity * 0.025, total_proposed_notional * 0.20))
    max_open_notional = min(base_equity * 0.20, max(total_proposed_notional, 1.0))

    rules.extend([
        KillRule("SYSTEM", "SYSTEM", "system_missing_heartbeat", "HARD_STOP", "minutes_since_last_heartbeat", ">", 5, "runtime", "STOP_ALL_FAMILIES", True, True, True, "No system should trade if logger/risk-manager heartbeat is stale."),
        KillRule("SYSTEM", "SYSTEM", "system_missing_trade_log_update", "HARD_STOP", "minutes_since_trade_log_update", ">", 30, "runtime", "STOP_ALL_FAMILIES", True, True, True, "A silent logger can hide losses or broken exits."),
        KillRule("SYSTEM", "SYSTEM", "system_daily_loss_stop", "HARD_STOP", "system_realized_pnl_today_usdt", "<=", -round(system_daily_loss, 4), "current_UTC_day", "STOP_ALL_FAMILIES_UNTIL_NEXT_DAY_REVIEW", True, True, True, "System-level daily realized loss limit."),
        KillRule("SYSTEM", "SYSTEM", "system_rolling_loss_stop", "HARD_STOP", "system_realized_pnl_rolling_100_trades_usdt", "<=", -round(system_rolling_loss, 4), "last_100_closed_trades", "STOP_ALL_FAMILIES_AND_REQUIRE_REVIEW", True, True, True, "Rolling realized loss stop prevents slow bleed."),
        KillRule("SYSTEM", "SYSTEM", "system_max_open_notional", "HARD_STOP", "system_open_notional_usdt", ">", round(max_open_notional, 4), "runtime", "BLOCK_NEW_ENTRIES_AND_CLOSE_EXCESS_IF_SAFE", True, True, True, "Total open notional cannot exceed OS proposal cap."),
        KillRule("SYSTEM", "SYSTEM", "system_no_live_without_paper", "HARD_STOP", "paper_drift_status", "!=", "PASS", "before_live", "BLOCK_LIVE", True, False, True, "Live remains blocked until paper drift validation passes."),
        KillRule("SYSTEM", "SYSTEM", "system_no_live_without_manual_review", "HARD_STOP", "manual_live_review", "!=", "APPROVED", "before_live", "BLOCK_LIVE", True, False, True, "This OS stage can prepare paper, not unsupervised live."),
    ])

    if not paper_families:
        rules.append(KillRule("SYSTEM", "SYSTEM", "system_no_paper_families", "HARD_STOP", "paper_allowed_family_count", "==", 0, "preflight", "BLOCK_PAPER_BOOT", True, True, False, "No family is allowed through paper gate."))

    return rules


def build_family_rules(family_key: str, d: Dict[str, Any], safety_score: int, paper_gate: str, live_gate: str, base_equity: float) -> Tuple[FamilySafetyState, List[KillRule]]:
    state = str(d.get("lifecycle_state", "UNKNOWN"))
    execution_decision = str(d.get("decision", "UNKNOWN"))
    proposed = safe_float(d.get("proposed_notional"), 0.0)
    allow_paper_input = bool(d.get("recommended_execution_state", "").startswith("ALLOW")) or bool(d.get("decision") == "EXECUTION_PASS")
    allow_live_input = bool(d.get("allow_live_later", False))
    flags = list(d.get("risk_flags") or [])

    daily_stop, rolling_stop, max_losses = compute_loss_stops(base_equity, proposed, state, family_key)
    min_trades_disable = STATE_MIN_TRADES_BEFORE_HARD_DISABLE.get(state, 30)
    paper_applies = paper_gate not in {"BLOCKED_ZERO_OR_DISABLED", "PAPER_BLOCKED_BY_SAFETY"} and proposed > 0

    rules: List[KillRule] = []
    reasons: List[str] = []

    if proposed <= 0 or state in {"DISABLED", "REJECTED", "RESEARCH_CANDIDATE"}:
        rules.append(KillRule("FAMILY", family_key, "family_zero_notional_block", "HARD_STOP", "proposed_notional", "<=", 0, "preflight", "BLOCK_FAMILY", True, True, True, "Family has zero proposed notional or non-tradable lifecycle state."))
        reasons.append("Family is blocked by zero notional/non-tradable state.")
    else:
        rules.extend([
            KillRule("FAMILY", family_key, "family_daily_loss_stop", "DISABLE", "family_realized_pnl_today_usdt", "<=", -daily_stop, "current_UTC_day", "DISABLE_FAMILY_UNTIL_REVIEW", True, True, True, "Family-specific daily realized loss stop."),
            KillRule("FAMILY", family_key, "family_rolling_loss_stop", "REDUCE", "family_realized_pnl_rolling_20_trades_usdt", "<=", -rolling_stop, "last_20_closed_trades", "REDUCE_OR_DISABLE_FAMILY", True, True, True, "Rolling trade loss stop catches short-term decay."),
            KillRule("FAMILY", family_key, "family_consecutive_losses", "REDUCE", "family_consecutive_closed_losses", ">=", max_losses, "closed_trades", "REDUCE_OR_DISABLE_FAMILY", True, True, True, "Consecutive losses indicate regime mismatch or broken execution."),
            KillRule("FAMILY", family_key, "family_net_pf_drift", "DISABLE", "family_paper_profit_factor_rolling_50", "<", 0.85, "min_50_closed_trades", "DISABLE_FAMILY_UNTIL_REVIEW", True, True, True, "Paper/live PF drift below survival threshold."),
            KillRule("FAMILY", family_key, "family_net_avg_pnl_drift", "DISABLE", "family_avg_pnl_rolling_50_usdt", "<", 0, "min_50_closed_trades", "DISABLE_FAMILY_UNTIL_REVIEW", True, True, True, "Average realized PnL turned negative over a meaningful sample."),
            KillRule("FAMILY", family_key, "family_missing_log_update", "HARD_STOP", "minutes_since_family_log_update", ">", 30, "runtime", "BLOCK_FAMILY_NEW_ENTRIES", True, True, True, "Family logger must keep writing logs."),
            KillRule("FAMILY", family_key, "family_notional_cap", "HARD_STOP", "family_open_notional_usdt", ">", proposed, "runtime", "BLOCK_NEW_ENTRIES_FOR_FAMILY", True, True, True, "Family cannot exceed proposed notional cap."),
        ])
        reasons.append("Standard family kill rules generated.")

    if state == "BACKUP_ONLY" and proposed > 0:
        rules.append(KillRule("FAMILY", family_key, "backup_no_promotion_without_review", "HARD_STOP", "family_state_change_request", "==", "PROMOTE", "preflight/runtime", "BLOCK_PROMOTION", True, True, True, "Backup-only families cannot self-promote from historical results alone."))
        rules.append(KillRule("FAMILY", family_key, "backup_one_bad_day_review", "DISABLE", "family_bad_day_count_rolling_7d", ">=", 1, "rolling_7_days", "DISABLE_BACKUP_UNTIL_REVIEW", True, True, True, "Backup families get stricter bad-day treatment."))
        reasons.append("Backup-only strict rules applied.")

    if family_key == "market_relative_short" and proposed > 0:
        rules.append(KillRule("FAMILY", family_key, "market_relative_prior_bad_day_guard", "DISABLE", "family_realized_pnl_today_usdt", "<=", -max(0.5, daily_stop * 0.75), "current_UTC_day", "DISABLE_MARKET_RELATIVE_UNTIL_REVIEW", True, True, True, "Prior bad-day analysis requires stricter market_relative_short stop."))
        reasons.append("Prior bad-day guard applied to market_relative_short.")

    if family_key == "weak_market_short" and proposed > 0:
        rules.append(KillRule("FAMILY", family_key, "weak_market_symbol_breadth_guard", "WARN", "positive_symbol_rate_rolling", "<", 0.45, "rolling_symbol_sample", "KEEP_BACKUP_NO_PROMOTION", True, True, True, "Execution realism flagged weak symbol breadth; prevent promotion."))
        reasons.append("Symbol breadth guard applied to weak_market_short.")

    if "BPS_ESTIMATED_NOT_NATIVE" in flags and proposed > 0:
        rules.append(KillRule("FAMILY", family_key, "estimated_bps_requires_paper_confirmation", "WARN", "bps_quality", "!=", "NATIVE_CONFIRMED", "before_live", "BLOCK_LIVE_AND_REQUIRE_PAPER_DRIFT", True, False, True, "Execution bps were estimated, so paper confirmation is mandatory."))
        reasons.append("BPS quality is estimated; live requires paper confirmation.")

    if paper_gate in {"PAPER_BLOCKED_BY_SAFETY", "BLOCKED_ZERO_OR_DISABLED"}:
        rules.append(KillRule("FAMILY", family_key, "paper_gate_block", "HARD_STOP", "paper_gate", "in", ["PAPER_BLOCKED_BY_SAFETY", "BLOCKED_ZERO_OR_DISABLED"], "preflight", "BLOCK_FAMILY_FROM_PAPER", True, True, False, "Paper gate blocks this family."))

    risk_tier = state
    if safety_score <= 0 and proposed > 0:
        risk_tier = state + "_HIGH_RISK"
    elif safety_score >= 4 and proposed > 0:
        risk_tier = state + "_STABLE"

    fstate = FamilySafetyState(
        family_key=family_key,
        lifecycle_state=state,
        execution_decision=execution_decision,
        proposed_notional=proposed,
        paper_allowed_by_inputs=allow_paper_input,
        live_allowed_by_inputs=allow_live_input,
        paper_gate=paper_gate,
        live_gate=live_gate,
        risk_tier=risk_tier,
        safety_score=safety_score,
        daily_loss_stop_usdt=daily_stop,
        rolling_loss_stop_usdt=rolling_stop,
        max_consecutive_losses=max_losses,
        min_trades_before_disable=min_trades_disable,
        rule_count=len(rules),
        reasons=reasons,
    )
    return fstate, rules


def build_policy(workspace: Path, execution_dir: Path, context: Dict[str, Any], decisions: List[Dict[str, Any]], base_equity: float) -> Tuple[Dict[str, Any], List[KillRule], List[FamilySafetyState], List[KillAction]]:
    by_family = family_decision_map(decisions)
    families = [f for f in KNOWN_FAMILIES if f in by_family]

    family_states: List[FamilySafetyState] = []
    family_rules: List[KillRule] = []

    for fam in families:
        d = by_family[fam]
        score, score_reasons = safety_score_for_execution(d)
        paper_gate, live_gate = classify_gate(score, d)
        fs, rules = build_family_rules(fam, d, score, paper_gate, live_gate, base_equity)
        fs.reasons.extend(score_reasons)
        family_states.append(fs)
        family_rules.extend(rules)

    paper_families = [s.family_key for s in family_states if s.paper_gate not in {"BLOCKED_ZERO_OR_DISABLED", "PAPER_BLOCKED_BY_SAFETY"} and s.proposed_notional > 0]
    total_proposed = sum(s.proposed_notional for s in family_states if s.proposed_notional > 0)
    system_rules = build_system_rules(base_equity, total_proposed, paper_families)
    all_rules = system_rules + family_rules

    paper_boot_gate = "PAPER_BOOT_ALLOWED_AFTER_PREFLIGHT" if paper_families else "PAPER_BOOT_BLOCKED_NO_ELIGIBLE_FAMILIES"
    live_gate = "LIVE_BLOCKED_UNTIL_PAPER_DRIFT_AND_MANUAL_REVIEW"

    # Global caveats from execution checker.
    caveats: List[str] = []
    if any("BPS_ESTIMATED_NOT_NATIVE" in (d.get("risk_flags") or []) for d in decisions):
        caveats.append("Some execution bps were estimated, not native; paper drift confirmation is mandatory.")
    if any("PRIOR_BAD_DAY_FAMILY" in (d.get("risk_flags") or []) for d in decisions):
        caveats.append("At least one family has prior bad-day risk flag; stricter family stop rules applied.")
    if any("LOW_POSITIVE_SYMBOL_RATE" in (d.get("risk_flags") or []) for d in decisions):
        caveats.append("At least one family has weak symbol breadth; no promotion without symbol-level improvement.")

    policy = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "engine_version": "edge_factory_kill_switch_controller_v1",
        "workspace": str(workspace),
        "execution_dir": str(execution_dir),
        "source_context": context,
        "base_equity": base_equity,
        "paper_boot_gate": paper_boot_gate,
        "live_gate": live_gate,
        "paper_eligible_families": paper_families,
        "live_eligible_families": [],
        "total_proposed_notional": round(total_proposed, 4),
        "rule_count": len(all_rules),
        "system_rule_count": len(system_rules),
        "family_rule_count": len(family_rules),
        "caveats": caveats,
        "family_safety_states": [asdict(s) for s in family_states],
        "rules": [asdict(r) for r in all_rules],
        "hard_principles": [
            "No live until paper drift passes and manual live review approves.",
            "Missing heartbeat/log update stops the system or family.",
            "Backup-only families cannot self-promote.",
            "Family notional caps are hard caps, not targets to exceed.",
            "Execution-estimated bps require paper confirmation.",
        ],
    }

    actions = build_actions(policy)
    return policy, all_rules, family_states, actions


def build_actions(policy: Dict[str, Any]) -> List[KillAction]:
    actions: List[KillAction] = []

    if policy["paper_boot_gate"] == "PAPER_BOOT_ALLOWED_AFTER_PREFLIGHT":
        actions.append(KillAction(
            action_key="build_preflight_inspector",
            family_key="SYSTEM",
            severity="NEXT_BOOT_GATE_MODULE",
            title="Build/run OS preflight inspector",
            reason="Kill-switch policy now exists. The next step is a preflight gate that checks all OS artifacts before any paper boot.",
            safe_offline=True,
            suggested_next_module="edge_factory_os_preflight_inspector.py",
            inputs=["kill_switch_policy.json", "capital_policy_proposal.json", "family_lifecycle_state.json", "execution_realism_decisions.json"],
            outputs=["preflight_report.json", "paper_boot_decision.json"],
        ))
    else:
        actions.append(KillAction(
            action_key="paper_blocked_review",
            family_key="SYSTEM",
            severity="BLOCKER",
            title="Paper boot blocked by kill-switch policy",
            reason="No family is eligible for paper under current policy.",
            safe_offline=True,
            suggested_next_module="manual_review_or_research_queue",
            inputs=["kill_switch_policy.json"],
            outputs=["revised_family_policy_or_research_queue"],
        ))

    actions.append(KillAction(
        action_key="build_live_vs_backtest_drift_monitor_later",
        family_key="SYSTEM",
        severity="AFTER_PAPER_BOOT",
        title="Use live-vs-backtest drift monitor after paper produces closed trades",
        reason="Drift monitor becomes meaningful only after paper logs closed trades.",
        safe_offline=True,
        suggested_next_module="edge_factory_live_vs_backtest_drift_monitor.py",
        inputs=["paper closed trades", "backtest/OOS references"],
        outputs=["drift_decisions.json"],
    ))

    actions.append(KillAction(
        action_key="build_autonomous_research_queue",
        family_key="SYSTEM",
        severity="OS_EVOLUTION_MODULE",
        title="Build autonomous research queue",
        reason="Once safety gates exist, the OS should queue new family research and replacement cycles.",
        safe_offline=True,
        suggested_next_module="edge_factory_autonomous_research_queue.py",
        inputs=["family_lifecycle_state.json", "execution_realism_decisions.json", "kill_switch_policy.json"],
        outputs=["research_queue.json"],
    ))

    return actions


def rules_dataframe(rules: List[KillRule]) -> pd.DataFrame:
    return pd.DataFrame([asdict(r) for r in rules])


def states_dataframe(states: List[FamilySafetyState]) -> pd.DataFrame:
    rows = []
    for s in states:
        r = asdict(s)
        r["reasons"] = " | ".join(s.reasons)
        rows.append(r)
    return pd.DataFrame(rows)


def write_report_md(path: Path, policy: Dict[str, Any], actions: List[KillAction]) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory Kill-Switch Policy Report")
    lines.append("")
    lines.append(f"Generated: `{policy['generated_at']}`")
    lines.append(f"Execution source: `{policy['execution_dir']}`")
    lines.append(f"Paper boot gate: **{policy['paper_boot_gate']}**")
    lines.append(f"Live gate: **{policy['live_gate']}**")
    lines.append("")

    lines.append("## Executive safety state")
    lines.append("")
    lines.append(f"Paper-eligible families: **{', '.join(policy['paper_eligible_families']) if policy['paper_eligible_families'] else 'none'}**")
    lines.append(f"Live-eligible families: **none**")
    lines.append(f"Total proposed notional: **{policy['total_proposed_notional']} USDT**")
    lines.append(f"Total rules: **{policy['rule_count']}**")
    lines.append("")
    if policy.get("caveats"):
        lines.append("Caveats:")
        for c in policy["caveats"]:
            lines.append(f"- {c}")
        lines.append("")

    lines.append("## Family gates")
    lines.append("")
    lines.append("| Family | State | Execution | Notional | Safety score | Paper gate | Live gate | Daily stop | Rolling stop | Max loss streak |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for s in policy["family_safety_states"]:
        lines.append(
            f"| {s['family_key']} | {s['lifecycle_state']} | {s['execution_decision']} | {s['proposed_notional']} | "
            f"{s['safety_score']} | {s['paper_gate']} | {s['live_gate']} | {s['daily_loss_stop_usdt']} | "
            f"{s['rolling_loss_stop_usdt']} | {s['max_consecutive_losses']} |"
        )
    lines.append("")

    lines.append("## System hard-stop rules")
    lines.append("")
    system_rules = [r for r in policy["rules"] if r["scope"] == "SYSTEM"]
    lines.append("| Rule | Severity | Metric | Condition | Action | Reason |")
    lines.append("|---|---:|---|---:|---|---|")
    for r in system_rules:
        lines.append(f"| {r['rule_key']} | {r['severity']} | `{r['metric']}` | {r['operator']} `{r['threshold']}` | {r['action']} | {r['reason']} |")
    lines.append("")

    lines.append("## Family rule highlights")
    lines.append("")
    for s in policy["family_safety_states"]:
        fam = s["family_key"]
        lines.append(f"### {fam}")
        lines.append("")
        fam_rules = [r for r in policy["rules"] if r["scope"] == "FAMILY" and r["family_key"] == fam]
        if not fam_rules:
            lines.append("No family rules generated.")
        else:
            for r in fam_rules[:10]:
                lines.append(f"- **{r['severity']}** `{r['rule_key']}`: `{r['metric']} {r['operator']} {r['threshold']}` → `{r['action']}`")
        lines.append("")

    lines.append("## Next actions")
    lines.append("")
    lines.append("| Severity | Action | Next module | Reason |")
    lines.append("|---|---|---|---|")
    for a in actions:
        lines.append(f"| {a.severity} | {a.title} | `{a.suggested_next_module}` | {a.reason} |")
    lines.append("")

    lines.append("## Hard principles")
    lines.append("")
    for p in policy["hard_principles"]:
        lines.append(f"- {p}")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("This policy does not start paper or live. It defines the safety contract that the future preflight/runtime monitor must enforce.")
    lines.append("The system is now closer to an OS: lifecycle decides who exists, governor decides size, execution checker decides feasibility, kill-switch decides when to stop.")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory kill-switch controller")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--execution_dir", default=None, help="explicit execution_realism_YYYYMMDD_HHMMSS folder")
    p.add_argument("--out_dir", default=None)
    p.add_argument("--base_equity", type=float, default=DEFAULT_BASE_EQUITY)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    execution_dir = discover_execution_dir(workspace, Path(args.execution_dir) if args.execution_dir else None)

    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_kill_switch_controller"
    out_dir = out_root / f"kill_switch_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    if execution_dir is None:
        err = {
            "error": "No execution realism output directory found.",
            "expected_root": str(workspace / "edge_factory_execution_realism_checker"),
            "hint": "Run edge_factory_execution_realism_checker.py first or pass --execution_dir explicitly.",
        }
        write_json(out_dir / "fatal_error.json", err)
        print("EDGE FACTORY KILL-SWITCH CONTROLLER v1")
        print("No execution realism directory found.")
        print(f"Details: {out_dir / 'fatal_error.json'}")
        return 2

    context, decisions = load_execution_decisions(execution_dir)
    policy, rules, family_states, actions = build_policy(workspace, execution_dir, context, decisions, args.base_equity)

    write_json(out_dir / "kill_switch_policy.json", policy)
    write_json(out_dir / "kill_switch_actions.json", [asdict(a) for a in actions])
    write_json(out_dir / "paper_boot_gate.json", {
        "generated_at": policy["generated_at"],
        "paper_boot_gate": policy["paper_boot_gate"],
        "live_gate": policy["live_gate"],
        "paper_eligible_families": policy["paper_eligible_families"],
        "live_eligible_families": policy["live_eligible_families"],
        "required_before_paper": ["edge_factory_os_preflight_inspector.py"],
        "required_after_paper": ["edge_factory_live_vs_backtest_drift_monitor.py"],
    })
    rules_dataframe(rules).to_csv(out_dir / "kill_switch_rules.csv", index=False)
    states_dataframe(family_states).to_csv(out_dir / "family_safety_states.csv", index=False)
    write_report_md(out_dir / "kill_switch_report.md", policy, actions)

    print("EDGE FACTORY KILL-SWITCH CONTROLLER v1")
    print("=" * 100)
    print(f"workspace    : {workspace}")
    print(f"execution_dir: {execution_dir}")
    print(f"output_dir   : {out_dir}")
    print(f"paper_gate   : {policy['paper_boot_gate']}")
    print(f"live_gate    : {policy['live_gate']}")
    print(f"rules        : {policy['rule_count']} total ({policy['system_rule_count']} system, {policy['family_rule_count']} family)")
    print("")
    print("FAMILY SAFETY GATES")
    print("-" * 100)
    for s in family_states:
        print(
            f"{s.family_key:24s} state={s.lifecycle_state:18s} exec={s.execution_decision:24s} "
            f"notional={s.proposed_notional:8.4f} score={s.safety_score:4d} "
            f"paper={s.paper_gate:34s} live={s.live_gate}"
        )
        print(
            f"  stops: daily={s.daily_loss_stop_usdt} USDT | rolling20={s.rolling_loss_stop_usdt} USDT | "
            f"max_consecutive_losses={s.max_consecutive_losses}"
        )
        for r in s.reasons[:3]:
            print(f"  - {r}")
    print("")
    print("NEXT ACTIONS")
    print("-" * 100)
    for a in actions:
        print(f"{a.severity:22s} -> {a.suggested_next_module}: {a.title}")
    print("")
    print(f"Open report : {out_dir / 'kill_switch_report.md'}")
    print(f"Policy      : {out_dir / 'kill_switch_policy.json'}")
    print(f"Rules       : {out_dir / 'kill_switch_rules.csv'}")
    print(f"Paper gate  : {out_dir / 'paper_boot_gate.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
