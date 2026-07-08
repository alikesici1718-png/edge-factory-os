#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY EXECUTION REALISM CHECKER v1
=========================================

Purpose
-------
Offline execution-feasibility validator for the Edge Factory OS.

This module consumes:
    1) latest adaptive capital governor proposal
    2) latest lifecycle state referenced by the proposal
    3) normalized historical/OOS trades referenced by lifecycle/OOS output

Then it stress-tests each family under estimated execution costs:
    - fees
    - spread/slippage
    - extra adverse selection buffer
    - notional feasibility
    - per-symbol concentration
    - edge-after-cost survival

It does NOT start paper/live trading.
It does NOT place orders.
It does NOT edit loggers.
It does NOT overwrite the sizing contract.

Run
---
    python "C:\Users\alike\edge_factory_execution_realism_checker.py"

Optional stricter stress:
    python "C:\Users\alike\edge_factory_execution_realism_checker.py" --stress_multiplier 2.0

Optional explicit capital governor folder:
    python "C:\Users\alike\edge_factory_execution_realism_checker.py" ^
      --capital_dir "C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_adaptive_capital_governor_v2\capital_governor_20260510_170507"

Outputs
-------
    <workspace>\edge_factory_execution_realism_checker\execution_realism_YYYYMMDD_HHMMSS\
        execution_realism_report.md
        execution_realism_summary.csv
        execution_realism_decisions.json
        execution_risk_flags.csv
        execution_stress_trades.csv
        execution_actions.json

Decision labels
---------------
    EXECUTION_PASS
    EXECUTION_WATCH
    EXECUTION_REDUCE
    EXECUTION_BLOCK_PAPER
    ZERO_NOTIONAL_OR_DISABLED
    INSUFFICIENT_DATA

Important assumptions
---------------------
The default bps cost model is deliberately conservative but parameterized:
    fee_roundtrip_bps          default 10.0
    spread_slippage_bps        default 2.0
    adverse_selection_bps      default 1.0
    stress_multiplier          default 1.0

If the historical trade file already contains return_bps, the checker uses it.
If not, it estimates bps from pnl and notional. If notional is unavailable, it uses the
family's proposed notional, and marks bps_quality as ESTIMATED_FROM_PROPOSED_NOTIONAL.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
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


@dataclass
class ExecutionDecision:
    family_key: str
    lifecycle_state: str
    capital_action: str
    proposed_notional: float
    decision: str
    confidence: str
    trade_count: int
    bps_quality: str
    gross_avg_bps: float
    gross_median_bps: float
    total_cost_bps: float
    net_avg_bps: float
    net_median_bps: float
    net_win_rate: float
    net_profit_factor: float
    net_total_pnl_est: float
    net_avg_pnl_est: float
    max_drawdown_est: float
    breakeven_cost_buffer_bps: float
    positive_symbol_rate: Optional[float]
    top3_symbol_abs_pnl_concentration: Optional[float]
    risk_flags: List[str]
    blocked_until: List[str]
    recommended_execution_state: str
    reasons: List[str]


@dataclass
class ExecutionAction:
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


def profit_factor(vals: Sequence[float]) -> float:
    arr = np.asarray(list(vals), dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return 0.0
    gains = arr[arr > 0].sum()
    losses = -arr[arr < 0].sum()
    if losses <= 0 and gains > 0:
        return float("inf")
    if losses <= 0:
        return 0.0
    return float(gains / losses)


def max_drawdown(vals: Sequence[float]) -> float:
    arr = np.asarray(list(vals), dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return 0.0
    equity = np.cumsum(arr)
    peak = np.maximum.accumulate(equity)
    dd = equity - peak
    return float(dd.min())


def latest_child_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def discover_capital_dir(workspace: Path, explicit: Optional[Path]) -> Optional[Path]:
    if explicit:
        return explicit if explicit.exists() else None
    return latest_child_dir(workspace / "edge_factory_adaptive_capital_governor_v2", "capital_governor_")


def load_capital_policy(capital_dir: Path) -> Dict[str, Any]:
    path = capital_dir / "capital_policy_proposal.json"
    if not path.exists():
        raise FileNotFoundError(f"capital_policy_proposal.json not found: {path}")
    obj = load_json(path)
    if not isinstance(obj, dict):
        raise ValueError("capital policy proposal is not a JSON object")
    return obj


def load_lifecycle_state_from_policy(policy: Dict[str, Any]) -> Tuple[Optional[Path], Dict[str, Any]]:
    lifecycle_dir_raw = policy.get("lifecycle_dir")
    if not lifecycle_dir_raw:
        return None, {}
    lifecycle_dir = Path(str(lifecycle_dir_raw))
    path = lifecycle_dir / "family_lifecycle_state.json"
    if not path.exists():
        return lifecycle_dir, {}
    obj = load_json(path)
    return lifecycle_dir, obj if isinstance(obj, dict) else {}


def locate_oos_trades(lifecycle_state: Dict[str, Any]) -> Tuple[Optional[Path], Optional[Path]]:
    oos_dir_raw = lifecycle_state.get("oos_dir")
    if not oos_dir_raw:
        return None, None
    oos_dir = Path(str(oos_dir_raw))
    trades_path = oos_dir / "normalized_oos_trades.csv"
    if trades_path.exists():
        return oos_dir, trades_path
    return oos_dir, None


def capital_decision_map(policy: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    rows = policy.get("family_decisions") or []
    out: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        if isinstance(r, dict) and r.get("family_key"):
            out[str(r["family_key"])] = r
    return out


def normalize_trade_table(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Normalize expected columns from prior validator.
    for col in ["family_key", "symbol", "pnl", "return_bps", "notional", "event_time"]:
        if col not in df.columns:
            if col in {"family_key", "symbol"}:
                df[col] = "unknown"
            else:
                df[col] = np.nan
    df["family_key"] = df["family_key"].astype(str)
    df["symbol"] = df["symbol"].astype(str).str.upper()
    df["pnl"] = pd.to_numeric(df["pnl"], errors="coerce")
    df["return_bps"] = pd.to_numeric(df["return_bps"], errors="coerce")
    df["notional"] = pd.to_numeric(df["notional"], errors="coerce")
    df["event_time"] = pd.to_datetime(df["event_time"], errors="coerce")
    df = df[df["pnl"].notna()].copy()
    return df


def prepare_family_trades(df: pd.DataFrame, family_key: str, proposed_notional: float) -> Tuple[pd.DataFrame, str]:
    g = df[df["family_key"] == family_key].copy()
    if g.empty:
        return g, "NO_DATA"

    # Preferred: existing return_bps.
    if g["return_bps"].notna().sum() >= max(10, int(len(g) * 0.50)):
        g["gross_bps"] = g["return_bps"]
        quality = "RETURN_BPS_NATIVE"
        return g[g["gross_bps"].notna()].copy(), quality

    # Second: pnl/notional if notional exists.
    valid_notional = g["notional"].notna() & (g["notional"].abs() > 1e-12)
    if valid_notional.sum() >= max(10, int(len(g) * 0.50)):
        g.loc[valid_notional, "gross_bps"] = g.loc[valid_notional, "pnl"] / g.loc[valid_notional, "notional"].abs() * 10000.0
        quality = "ESTIMATED_FROM_ROW_NOTIONAL"
        return g[g["gross_bps"].notna()].copy(), quality

    # Last resort: pnl/proposed_notional. This can be scale-distorted but still useful as a rough stress proxy.
    if proposed_notional > 0:
        g["gross_bps"] = g["pnl"] / proposed_notional * 10000.0
        quality = "ESTIMATED_FROM_PROPOSED_NOTIONAL"
        return g[g["gross_bps"].notna()].copy(), quality

    return pd.DataFrame(), "NO_NOTIONAL_BASIS"


def symbol_robustness(g: pd.DataFrame, pnl_col: str = "net_pnl_est") -> Tuple[Optional[float], Optional[float], List[str]]:
    flags: List[str] = []
    if g.empty or "symbol" not in g.columns:
        return None, None, ["NO_SYMBOL_DATA"]
    sym = g.groupby("symbol")[pnl_col].agg(["count", "sum"]).reset_index()
    valid = sym[sym["count"] >= 5].copy()
    if valid.empty:
        return None, None, ["LOW_SYMBOL_SAMPLE"]
    pos_rate = float((valid["sum"] > 0).mean())
    total_abs = valid["sum"].abs().sum()
    top3 = None
    if total_abs > 1e-12:
        top3 = float(valid["sum"].abs().sort_values(ascending=False).head(3).sum() / total_abs)
    if pos_rate < 0.45:
        flags.append("LOW_POSITIVE_SYMBOL_RATE")
    if top3 is not None and top3 > 0.75:
        flags.append("HIGH_TOP3_SYMBOL_CONCENTRATION")
    return pos_rate, top3, flags


def execution_decision_for_family(
    family_key: str,
    cap: Dict[str, Any],
    trades: pd.DataFrame,
    total_cost_bps: float,
    min_trades: int,
    min_net_avg_bps: float,
    min_net_pf: float,
    min_net_win_rate: float,
) -> Tuple[ExecutionDecision, pd.DataFrame]:
    state = str(cap.get("lifecycle_state", "UNKNOWN"))
    action = str(cap.get("capital_action", "UNKNOWN"))
    proposed_notional = safe_float(cap.get("proposed_notional"), 0.0)
    allow_paper_later = bool(cap.get("allow_paper_later", False))
    allow_live_later = bool(cap.get("allow_live_later", False))
    blocked_until = list(cap.get("blocked_until") or [])

    if proposed_notional <= 0 or state in {"DISABLED", "REJECTED", "RESEARCH_CANDIDATE"}:
        return ExecutionDecision(
            family_key=family_key,
            lifecycle_state=state,
            capital_action=action,
            proposed_notional=proposed_notional,
            decision="ZERO_NOTIONAL_OR_DISABLED",
            confidence="high",
            trade_count=0,
            bps_quality="NOT_APPLICABLE",
            gross_avg_bps=0.0,
            gross_median_bps=0.0,
            total_cost_bps=total_cost_bps,
            net_avg_bps=0.0,
            net_median_bps=0.0,
            net_win_rate=0.0,
            net_profit_factor=0.0,
            net_total_pnl_est=0.0,
            net_avg_pnl_est=0.0,
            max_drawdown_est=0.0,
            breakeven_cost_buffer_bps=0.0,
            positive_symbol_rate=None,
            top3_symbol_abs_pnl_concentration=None,
            risk_flags=["ZERO_NOTIONAL_OR_DISABLED"],
            blocked_until=sorted(set(blocked_until + ["not_active"])),
            recommended_execution_state="BLOCKED_BY_CAPITAL_POLICY",
            reasons=["Family has zero proposed notional or disabled/research-only lifecycle state."],
        ), pd.DataFrame()

    g, quality = prepare_family_trades(trades, family_key, proposed_notional)
    if g.empty or len(g) < min_trades:
        return ExecutionDecision(
            family_key=family_key,
            lifecycle_state=state,
            capital_action=action,
            proposed_notional=proposed_notional,
            decision="INSUFFICIENT_DATA",
            confidence="low",
            trade_count=int(len(g)),
            bps_quality=quality,
            gross_avg_bps=0.0,
            gross_median_bps=0.0,
            total_cost_bps=total_cost_bps,
            net_avg_bps=0.0,
            net_median_bps=0.0,
            net_win_rate=0.0,
            net_profit_factor=0.0,
            net_total_pnl_est=0.0,
            net_avg_pnl_est=0.0,
            max_drawdown_est=0.0,
            breakeven_cost_buffer_bps=0.0,
            positive_symbol_rate=None,
            top3_symbol_abs_pnl_concentration=None,
            risk_flags=["INSUFFICIENT_EXECUTION_SAMPLE"],
            blocked_until=sorted(set(blocked_until + ["more_historical_or_paper_data"])),
            recommended_execution_state="DO_NOT_PROMOTE",
            reasons=[f"Usable execution sample {len(g)} < min_trades {min_trades}."],
        ), g

    g = g.copy()
    g["total_cost_bps"] = total_cost_bps
    g["net_bps_after_cost"] = g["gross_bps"] - total_cost_bps
    g["net_pnl_est"] = proposed_notional * g["net_bps_after_cost"] / 10000.0

    net_bps = pd.to_numeric(g["net_bps_after_cost"], errors="coerce").dropna()
    net_pnl = pd.to_numeric(g["net_pnl_est"], errors="coerce").dropna()
    gross_bps = pd.to_numeric(g["gross_bps"], errors="coerce").dropna()

    gross_avg = float(gross_bps.mean())
    gross_med = float(gross_bps.median())
    net_avg = float(net_bps.mean())
    net_med = float(net_bps.median())
    net_wr = float((net_bps > 0).mean())
    net_pf = profit_factor(net_pnl.tolist())
    net_total = float(net_pnl.sum())
    net_avg_pnl = float(net_pnl.mean())
    dd = max_drawdown(net_pnl.tolist())
    buffer_bps = gross_avg - total_cost_bps
    pos_sym_rate, top3_conc, sym_flags = symbol_robustness(g)

    flags: List[str] = []
    reasons: List[str] = []
    score = 0

    if quality != "RETURN_BPS_NATIVE":
        flags.append("BPS_ESTIMATED_NOT_NATIVE")
        reasons.append(f"Return bps quality is {quality}; execution result is approximate.")

    if net_avg <= 0:
        score -= 4
        flags.append("NEGATIVE_NET_AVG_BPS")
        reasons.append("Net average bps after cost is not positive.")
    elif net_avg < min_net_avg_bps:
        score -= 2
        flags.append("LOW_NET_AVG_BPS")
        reasons.append(f"Net average bps {net_avg:.4f} is below threshold {min_net_avg_bps:.4f}.")
    else:
        score += 2
        reasons.append("Net average bps survives execution cost threshold.")

    if net_pf < 1.0:
        score -= 3
        flags.append("NET_PF_BELOW_1")
        reasons.append("Net profit factor after execution cost is below 1.")
    elif net_pf < min_net_pf:
        score -= 1
        flags.append("LOW_NET_PF")
        reasons.append(f"Net profit factor {net_pf:.4f} is below threshold {min_net_pf:.4f}.")
    else:
        score += 1
        reasons.append("Net profit factor survives execution cost threshold.")

    if net_wr < min_net_win_rate:
        score -= 1
        flags.append("LOW_NET_WIN_RATE")
        reasons.append(f"Net win rate {net_wr:.2%} is below threshold {min_net_win_rate:.2%}.")
    else:
        score += 1
        reasons.append("Net win rate is acceptable after execution cost.")

    if buffer_bps < 0:
        score -= 3
        flags.append("NEGATIVE_BREAKEVEN_COST_BUFFER")
        reasons.append("Average gross edge is smaller than the modeled cost.")
    elif buffer_bps < total_cost_bps * 0.25:
        score -= 1
        flags.append("THIN_COST_BUFFER")
        reasons.append("Breakeven cost buffer is thin.")
    else:
        score += 1
        reasons.append("Breakeven cost buffer is acceptable.")

    flags.extend(sym_flags)
    if pos_sym_rate is not None:
        if pos_sym_rate < 0.45:
            score -= 1
            reasons.append("Less than 45% of valid symbols remain profitable after cost.")
        elif pos_sym_rate >= 0.60:
            score += 1
            reasons.append("Symbol-level profitability remains broad after cost.")
    if top3_conc is not None and top3_conc > 0.75:
        score -= 1
        reasons.append("Net PnL is concentrated in the top 3 symbols.")

    # State-specific constraints.
    if state == "BACKUP_ONLY":
        flags.append("BACKUP_ONLY_NOT_PROMOTABLE_YET")
        reasons.append("Lifecycle is backup-only; execution pass can allow paper later but not promotion/live.")
    if family_key == "market_relative_short":
        flags.append("PRIOR_BAD_DAY_FAMILY")
        reasons.append("market_relative_short has prior bad-day/capping concern; execution pass does not remove cap.")

    if score >= 4:
        decision = "EXECUTION_PASS"
        rec_state = "ALLOW_PAPER_PREFLIGHT_LATER" if allow_paper_later else "PASS_BUT_CAPITAL_BLOCKED"
        confidence = "high" if quality == "RETURN_BPS_NATIVE" else "medium"
    elif score >= 1:
        decision = "EXECUTION_WATCH"
        rec_state = "ALLOW_SMALL_PAPER_ONLY_AFTER_KILL_SWITCH" if allow_paper_later else "WATCH_CAPITAL_BLOCKED"
        confidence = "medium"
    elif score >= -2:
        decision = "EXECUTION_REDUCE"
        rec_state = "REDUCE_OR_KEEP_BACKUP_ONLY"
        confidence = "medium"
        blocked_until.append("execution_retest_or_lower_cost_model")
    else:
        decision = "EXECUTION_BLOCK_PAPER"
        rec_state = "BLOCK_PAPER_FOR_THIS_FAMILY"
        confidence = "high"
        allow_paper_later = False
        blocked_until.append("execution_failure_review")

    # Live remains blocked universally.
    allow_live_later = False
    blocked_until.extend(["kill_switch_policy", "paper_drift_check_after_boot"])

    return ExecutionDecision(
        family_key=family_key,
        lifecycle_state=state,
        capital_action=action,
        proposed_notional=proposed_notional,
        decision=decision,
        confidence=confidence,
        trade_count=int(len(g)),
        bps_quality=quality,
        gross_avg_bps=gross_avg,
        gross_median_bps=gross_med,
        total_cost_bps=total_cost_bps,
        net_avg_bps=net_avg,
        net_median_bps=net_med,
        net_win_rate=net_wr,
        net_profit_factor=net_pf,
        net_total_pnl_est=net_total,
        net_avg_pnl_est=net_avg_pnl,
        max_drawdown_est=dd,
        breakeven_cost_buffer_bps=buffer_bps,
        positive_symbol_rate=pos_sym_rate,
        top3_symbol_abs_pnl_concentration=top3_conc,
        risk_flags=sorted(set(flags)),
        blocked_until=sorted(set(blocked_until)),
        recommended_execution_state=rec_state,
        reasons=reasons,
    ), g


def build_actions(decisions: List[ExecutionDecision]) -> List[ExecutionAction]:
    actions: List[ExecutionAction] = []
    for d in decisions:
        if d.decision in {"EXECUTION_BLOCK_PAPER", "EXECUTION_REDUCE"}:
            actions.append(ExecutionAction(
                action_key=f"execution_review_{d.family_key}",
                family_key=d.family_key,
                severity="REVIEW_REQUIRED",
                title=f"Review execution feasibility for {d.family_key}",
                reason=f"Decision={d.decision}; net_avg_bps={d.net_avg_bps:.4f}, net_pf={d.net_profit_factor:.4f}",
                safe_offline=True,
                suggested_next_module="manual_review_or_lower_cost_sensitivity",
                inputs=["execution_realism_decisions.json", "execution_stress_trades.csv"],
                outputs=["revised_execution_assumptions_or_family_reduction"],
            ))

    actions.append(ExecutionAction(
        action_key="build_kill_switch_controller",
        family_key="SYSTEM",
        severity="NEXT_SAFETY_MODULE",
        title="Build kill-switch controller",
        reason="Execution check now exists. Before paper boot, the OS needs hard stop rules for family/system drawdown, drift, missing logs, and bad-day behavior.",
        safe_offline=True,
        suggested_next_module="edge_factory_kill_switch_controller.py",
        inputs=["capital_policy_proposal.json", "family_lifecycle_state.json", "execution_realism_decisions.json"],
        outputs=["kill_switch_policy.json", "kill_switch_report.md"],
    ))

    actions.append(ExecutionAction(
        action_key="build_preflight_inspector_later",
        family_key="SYSTEM",
        severity="BOOT_LATER",
        title="Build/run paper preflight after kill-switch",
        reason="Preflight should happen only after lifecycle, capital, execution realism, and kill-switch policy exist.",
        safe_offline=True,
        suggested_next_module="edge_factory_os_preflight_inspector.py",
        inputs=["kill_switch_policy.json", "capital_policy_proposal.json", "execution_realism_decisions.json"],
        outputs=["preflight_report.json"],
    ))
    return actions


def summary_df(decisions: List[ExecutionDecision]) -> pd.DataFrame:
    return pd.DataFrame([asdict(d) for d in decisions])


def flags_df(decisions: List[ExecutionDecision]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for d in decisions:
        for flag in d.risk_flags:
            rows.append({
                "family_key": d.family_key,
                "decision": d.decision,
                "risk_flag": flag,
                "severity": "HIGH" if flag in {"NEGATIVE_NET_AVG_BPS", "NET_PF_BELOW_1", "NEGATIVE_BREAKEVEN_COST_BUFFER"} else "MEDIUM",
                "net_avg_bps": d.net_avg_bps,
                "net_profit_factor": d.net_profit_factor,
                "proposed_notional": d.proposed_notional,
            })
    return pd.DataFrame(rows)


def write_report_md(path: Path, context: Dict[str, Any], decisions: List[ExecutionDecision], actions: List[ExecutionAction]) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory Execution Realism Report")
    lines.append("")
    lines.append(f"Generated: `{context['generated_at']}`")
    lines.append(f"Workspace: `{context['workspace']}`")
    lines.append(f"Capital source: `{context['capital_dir']}`")
    lines.append(f"OOS trades: `{context.get('trades_path')}`")
    lines.append("")

    lines.append("## Cost model")
    lines.append("")
    lines.append(f"- fee_roundtrip_bps: `{context['fee_roundtrip_bps']}`")
    lines.append(f"- spread_slippage_bps: `{context['spread_slippage_bps']}`")
    lines.append(f"- adverse_selection_bps: `{context['adverse_selection_bps']}`")
    lines.append(f"- stress_multiplier: `{context['stress_multiplier']}`")
    lines.append(f"- total_cost_bps: **{context['total_cost_bps']}**")
    lines.append("")

    lines.append("## Family execution decisions")
    lines.append("")
    lines.append("| Family | State | Notional | Decision | BPS quality | Gross avg bps | Cost bps | Net avg bps | Net PF | Net WR | Buffer bps | Flags |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    for d in decisions:
        pf_txt = "inf" if str(d.net_profit_factor) == "inf" else f"{d.net_profit_factor:.3f}"
        flags = ", ".join(d.risk_flags[:5])
        lines.append(
            f"| {d.family_key} | {d.lifecycle_state} | {d.proposed_notional:.4f} | {d.decision} | {d.bps_quality} | "
            f"{d.gross_avg_bps:.4f} | {d.total_cost_bps:.4f} | {d.net_avg_bps:.4f} | {pf_txt} | "
            f"{d.net_win_rate:.2%} | {d.breakeven_cost_buffer_bps:.4f} | {flags} |"
        )
    lines.append("")

    lines.append("## Family reasoning")
    lines.append("")
    for d in decisions:
        lines.append(f"### {d.family_key}")
        lines.append("")
        lines.append(f"Decision: **{d.decision}** / confidence: **{d.confidence}**")
        lines.append(f"Recommended execution state: `{d.recommended_execution_state}`")
        lines.append(f"Blocked until: `{', '.join(d.blocked_until)}`")
        lines.append("")
        lines.append("Reasons:")
        for r in d.reasons[:12]:
            lines.append(f"- {r}")
        lines.append("")

    lines.append("## Next actions")
    lines.append("")
    lines.append("| Severity | Family | Action | Next module | Reason |")
    lines.append("|---|---:|---|---|---|")
    for a in actions:
        lines.append(f"| {a.severity} | {a.family_key} | {a.title} | `{a.suggested_next_module}` | {a.reason} |")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("This is an offline stress test. It does not prove live fill quality. It tells the OS which families are too thin to deserve paper/live promotion under the chosen cost model.")
    lines.append("Live remains blocked. The next safety module should be the kill-switch controller.")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory execution realism checker")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--capital_dir", default=None, help="explicit capital_governor_YYYYMMDD_HHMMSS folder")
    p.add_argument("--out_dir", default=None)
    p.add_argument("--fee_roundtrip_bps", type=float, default=10.0)
    p.add_argument("--spread_slippage_bps", type=float, default=2.0)
    p.add_argument("--adverse_selection_bps", type=float, default=1.0)
    p.add_argument("--stress_multiplier", type=float, default=1.0)
    p.add_argument("--min_trades", type=int, default=100)
    p.add_argument("--min_net_avg_bps", type=float, default=1.0)
    p.add_argument("--min_net_pf", type=float, default=1.05)
    p.add_argument("--min_net_win_rate", type=float, default=0.45)
    p.add_argument("--known_only", action="store_true", default=True)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    capital_dir = discover_capital_dir(workspace, Path(args.capital_dir) if args.capital_dir else None)

    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_execution_realism_checker"
    out_dir = out_root / f"execution_realism_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    if capital_dir is None:
        err = {
            "error": "No capital governor output directory found.",
            "expected_root": str(workspace / "edge_factory_adaptive_capital_governor_v2"),
            "hint": "Run edge_factory_adaptive_capital_governor_v2.py first or pass --capital_dir explicitly.",
        }
        write_json(out_dir / "fatal_error.json", err)
        print("EDGE FACTORY EXECUTION REALISM CHECKER v1")
        print("No capital governor directory found.")
        print(f"Details: {out_dir / 'fatal_error.json'}")
        return 2

    policy = load_capital_policy(capital_dir)
    lifecycle_dir, lifecycle_state = load_lifecycle_state_from_policy(policy)
    oos_dir, trades_path = locate_oos_trades(lifecycle_state)

    if trades_path is None:
        err = {
            "error": "No normalized_oos_trades.csv found from lifecycle/OOS source.",
            "capital_dir": str(capital_dir),
            "lifecycle_dir": str(lifecycle_dir) if lifecycle_dir else None,
            "oos_dir": str(oos_dir) if oos_dir else None,
            "hint": "Run rolling OOS validator and lifecycle engine first.",
        }
        write_json(out_dir / "fatal_error.json", err)
        print("EDGE FACTORY EXECUTION REALISM CHECKER v1")
        print("No normalized OOS trades found.")
        print(f"Details: {out_dir / 'fatal_error.json'}")
        return 2

    trades = normalize_trade_table(trades_path)
    cap_map = capital_decision_map(policy)

    total_cost_bps = (args.fee_roundtrip_bps + args.spread_slippage_bps + args.adverse_selection_bps) * args.stress_multiplier

    decisions: List[ExecutionDecision] = []
    stress_frames: List[pd.DataFrame] = []

    families = [f for f in KNOWN_FAMILIES if f in cap_map]
    for fam in families:
        d, stress_g = execution_decision_for_family(
            family_key=fam,
            cap=cap_map[fam],
            trades=trades,
            total_cost_bps=total_cost_bps,
            min_trades=args.min_trades,
            min_net_avg_bps=args.min_net_avg_bps,
            min_net_pf=args.min_net_pf,
            min_net_win_rate=args.min_net_win_rate,
        )
        decisions.append(d)
        if not stress_g.empty:
            keep_cols = [c for c in [
                "family_key", "symbol", "event_time", "pnl", "notional", "return_bps",
                "gross_bps", "total_cost_bps", "net_bps_after_cost", "net_pnl_est", "source_file", "source_row"
            ] if c in stress_g.columns]
            stress_frames.append(stress_g[keep_cols].copy())

    actions = build_actions(decisions)

    context = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(workspace),
        "capital_dir": str(capital_dir),
        "lifecycle_dir": str(lifecycle_dir) if lifecycle_dir else None,
        "oos_dir": str(oos_dir) if oos_dir else None,
        "trades_path": str(trades_path),
        "fee_roundtrip_bps": args.fee_roundtrip_bps,
        "spread_slippage_bps": args.spread_slippage_bps,
        "adverse_selection_bps": args.adverse_selection_bps,
        "stress_multiplier": args.stress_multiplier,
        "total_cost_bps": total_cost_bps,
        "min_trades": args.min_trades,
        "min_net_avg_bps": args.min_net_avg_bps,
        "min_net_pf": args.min_net_pf,
        "min_net_win_rate": args.min_net_win_rate,
    }

    summary = summary_df(decisions)
    flags = flags_df(decisions)
    stress = pd.concat(stress_frames, ignore_index=True) if stress_frames else pd.DataFrame()
    if not stress.empty and "event_time" in stress.columns:
        stress["event_time"] = stress["event_time"].astype(str)

    write_json(out_dir / "execution_realism_decisions.json", {
        "context": context,
        "decisions": [asdict(d) for d in decisions],
        "actions": [asdict(a) for a in actions],
    })
    write_json(out_dir / "execution_actions.json", [asdict(a) for a in actions])
    summary.to_csv(out_dir / "execution_realism_summary.csv", index=False)
    flags.to_csv(out_dir / "execution_risk_flags.csv", index=False)
    stress.to_csv(out_dir / "execution_stress_trades.csv", index=False)
    write_report_md(out_dir / "execution_realism_report.md", context, decisions, actions)

    print("EDGE FACTORY EXECUTION REALISM CHECKER v1")
    print("=" * 100)
    print(f"workspace   : {workspace}")
    print(f"capital_dir : {capital_dir}")
    print(f"trades_path : {trades_path}")
    print(f"output_dir  : {out_dir}")
    print(f"total_cost_bps: {total_cost_bps:.4f}")
    print("")
    print("EXECUTION DECISIONS")
    print("-" * 100)
    for d in decisions:
        pf_txt = "inf" if str(d.net_profit_factor) == "inf" else f"{d.net_profit_factor:.3f}"
        print(
            f"{d.family_key:24s} state={d.lifecycle_state:18s} notional={d.proposed_notional:8.4f} "
            f"decision={d.decision:22s} gross_avg_bps={d.gross_avg_bps:10.4f} "
            f"net_avg_bps={d.net_avg_bps:10.4f} net_pf={pf_txt:>8s} net_wr={d.net_win_rate:7.2%}"
        )
        for r in d.reasons[:3]:
            print(f"  - {r}")
        if d.risk_flags:
            print(f"  flags: {', '.join(d.risk_flags[:6])}")
    print("")
    print("NEXT ACTIONS")
    print("-" * 100)
    for a in actions[-2:]:
        print(f"{a.severity:18s} -> {a.suggested_next_module}: {a.title}")
    print("")
    print(f"Open report: {out_dir / 'execution_realism_report.md'}")
    print(f"Summary    : {out_dir / 'execution_realism_summary.csv'}")
    print(f"Decisions  : {out_dir / 'execution_realism_decisions.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
