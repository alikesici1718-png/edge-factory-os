#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Scores and ranks candidate strategy ideas from the idea bank ledger by evaluating readiness, contract completeness, side alignment with active families, and regime clarity. Reads the candidate idea bank JSONL ledger and writes a prioritized ranking CSV and state JSON for downstream selector modules.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_candidate_idea_prioritizer_v1"
IDEA_LEDGER = WORKSPACE / "edge_factory_candidate_idea_bank_v1" / "candidate_idea_bank_master_ledger.jsonl"

ACTIVE_MASTER_FAMILIES = {
    "old_short": {"side": "short", "role": "core_short"},
    "impulse_long": {"side": "long", "role": "active_long_diversifier"},
    "market_relative_short": {"side": "short", "role": "capped_short"},
    "weak_market_short": {"side": "short", "role": "backup_short"},
}

ARCHIVED_FAMILIES = {
    "rel_extreme_reversion_short": {
        "family": "rel_extreme_reversion_short",
        "reason": "duplicate_or_stale_shadow_and_no_closed_sample",
    }
}

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows

def contains_any(text: str, words: list[str]) -> bool:
    t = text.lower()
    return any(w.lower() in t for w in words)

def score_idea(idea: dict[str, Any]) -> dict[str, Any]:
    candidate_key = str(idea.get("candidate_key", ""))
    family_key = str(idea.get("family_key", ""))
    side = str(idea.get("side", ""))
    edge = str(idea.get("edge", ""))
    regime = str(idea.get("regime", ""))
    entry_rule = str(idea.get("entry_rule", ""))
    readiness = float(idea.get("readiness_score") or 0.0)
    contract_ready = bool(idea.get("contract_ready", False))

    score = 0.0
    reasons = []
    blockers = []

    # Base readiness.
    score += readiness * 0.40
    reasons.append(f"readiness_score={readiness}")

    if contract_ready:
        score += 20
        reasons.append("contract_ready")
    else:
        blockers.append("NOT_CONTRACT_READY")

    # Diversification versus current MASTER: currently short-heavy, so new long ideas get boost,
    # but avoid over-boosting impulse_long because impulse_long is already active.
    if side == "long":
        score += 15
        reasons.append("long_diversifier_against_short_heavy_master")
    elif side == "short":
        score += 5
        reasons.append("short_candidate_but_master_already_short_heavy")

    # Penalize direct overlap with active family names/roles.
    overlap_penalty = 0

    if "impulse" in family_key or "impulse" in candidate_key:
        overlap_penalty += 12
        blockers.append("OVERLAPS_ACTIVE_IMPULSE_LONG_FAMILY")

    if "relative" in family_key and side == "short":
        overlap_penalty += 10
        blockers.append("OVERLAPS_MARKET_RELATIVE_SHORT_CONCEPT")

    if "weak_market" in family_key:
        overlap_penalty += 10
        blockers.append("OVERLAPS_WEAK_MARKET_BACKUP")

    # Penalize rel_extreme-like stale duplicate risk: extreme pump reversion short is useful,
    # but close to archived rel_extreme and must be handled carefully.
    if contains_any(candidate_key + " " + family_key + " " + edge + " " + entry_rule, ["blowoff", "extreme", "rel_ret_bps >= 600"]):
        overlap_penalty += 8
        blockers.append("SIMILAR_TO_ARCHIVED_REL_EXTREME_REVERSION_FAMILY")

    score -= overlap_penalty
    if overlap_penalty:
        reasons.append(f"overlap_penalty={overlap_penalty}")

    # Novelty / orthogonality boosts.
    if contains_any(candidate_key + " " + edge + " " + regime, ["panic", "rebound", "liquidation", "flush"]):
        score += 18
        reasons.append("high_regime_diversification_panic_rebound")

    if contains_any(candidate_key + " " + edge, ["snapback", "underperforms", "relative weakness"]):
        score += 12
        reasons.append("relative_weakness_long_diversifier")

    if contains_any(candidate_key + " " + edge, ["continuation"]) and side == "short":
        score += 4
        reasons.append("continuation_short_possible_but_less_diversifying")

    # Operational simplicity.
    if "fixed_hold" in str(idea.get("exit_rule", "")):
        score += 8
        reasons.append("simple_fixed_hold_exit")

    if "liquidity_floor" in entry_rule:
        score += 4
        reasons.append("has_liquidity_filter_placeholder")

    # Rank class.
    if blockers and "NOT_CONTRACT_READY" in blockers:
        priority_class = "BLOCKED"
    elif score >= 80:
        priority_class = "HIGH_PRIORITY_CONTRACT_CANDIDATE"
    elif score >= 65:
        priority_class = "MEDIUM_PRIORITY_CONTRACT_CANDIDATE"
    else:
        priority_class = "LOW_PRIORITY_OR_OVERLAP"

    return {
        "candidate_key": candidate_key,
        "family_key": family_key,
        "side": side,
        "priority_score": round(score, 2),
        "priority_class": priority_class,
        "contract_ready": contract_ready,
        "readiness_score": readiness,
        "reasons": reasons,
        "blockers": blockers,
        "contract_generator_command": idea.get("contract_generator_command", ""),
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
    }

def main() -> int:
    out_dir = OUT_ROOT / f"candidate_idea_prioritizer_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    ideas = read_jsonl(IDEA_LEDGER)
    scored = [score_idea(x) for x in ideas]
    scored = sorted(scored, key=lambda x: x["priority_score"], reverse=True)

    top = scored[0] if scored else None

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "prioritizer_status": "IDEA_PRIORITIZATION_READY" if scored else "NO_IDEAS_TO_PRIORITIZE",
        "idea_count": len(ideas),
        "top_candidate": top,
        "ranked_candidates": scored,
        "active_master_families": ACTIVE_MASTER_FAMILIES,
        "archived_families": ARCHIVED_FAMILIES,
        "next_action": (
            "GENERATE_CONTRACT_FOR_TOP_CANDIDATE"
            if top and top["contract_ready"]
            else "ADD_OR_COMPLETE_IDEAS"
        ),
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Prioritizer does not generate contracts by itself.",
            "Prioritizer does not run backtests.",
            "Prioritizer does not touch MASTER_UPPER_SYSTEM.",
            "Prioritizer does not start/stop processes.",
            "Prioritizer does not promote candidates.",
            "Prioritizer does not place orders.",
        ],
    }

    state_path = out_dir / "candidate_idea_prioritizer_v1_state.json"
    csv_path = out_dir / "candidate_idea_prioritizer_v1_ranked.csv"
    report_path = out_dir / "candidate_idea_prioritizer_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    pd.DataFrame(scored).to_csv(csv_path, index=False)

    md = []
    md.append("# Edge Factory Candidate Idea Prioritizer v1")
    md.append("")
    md.append(f"Status: `{state['prioritizer_status']}`")
    md.append(f"Idea count: `{len(ideas)}`")
    md.append("")
    if top:
        md.append("## Top candidate")
        md.append(f"- `{top['candidate_key']}` score `{top['priority_score']}` class `{top['priority_class']}`")
        md.append("")
        md.append("## Contract generator command")
        md.append("```powershell")
        md.append(top.get("contract_generator_command", ""))
        md.append("```")
    md.append("")
    md.append("## Ranked candidates")
    for x in scored:
        md.append(f"- `{x['candidate_key']}` — score `{x['priority_score']}` / `{x['priority_class']}`")
    md.append("")
    md.append("## Safety")
    md.append("- live_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY CANDIDATE IDEA PRIORITIZER v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"prioritizer_status: {state['prioritizer_status']}")
    print(f"idea_count: {len(ideas)}")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("capital_change_allowed: False")
    print()

    print("RANKED CANDIDATES")
    print("-" * 100)
    if scored:
        df = pd.DataFrame(scored)
        print(df[["candidate_key","family_key","side","priority_score","priority_class","contract_ready"]].to_string(index=False))
    else:
        print("No ideas.")

    print()
    print("TOP NEXT ACTION")
    print("-" * 100)
    if top:
        print(f"{top['candidate_key']} -> {state['next_action']}")
        print()
        print("CONTRACT GENERATOR COMMAND")
        print("-" * 100)
        print(top.get("contract_generator_command", ""))
    else:
        print("No top candidate.")

    print()
    print(f"State : {state_path}")
    print(f"CSV   : {csv_path}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
