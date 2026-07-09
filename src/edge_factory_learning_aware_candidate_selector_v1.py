#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Selects the next candidate strategy to research by combining idea bank scores with research learning memory to avoid repeating past failed approaches. Reads the candidate idea bank JSONL ledger and the research learning memory JSONL, scores ideas against learned failure patterns, and writes a selector state JSON with the top-ranked next candidate recommendation.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_learning_aware_candidate_selector_v1"

IDEA_LEDGER = WORKSPACE / "edge_factory_candidate_idea_bank_v1" / "candidate_idea_bank_master_ledger.jsonl"
LEARNING_MEMORY = WORKSPACE / "edge_factory_os_research_learning_controller_v1" / "edge_factory_research_learning_memory_master.jsonl"

ACTIVE_MASTER_FAMILIES = {
    "old_short": {"side": "short", "role": "core_short"},
    "impulse_long": {"side": "long", "role": "active_long_diversifier"},
    "market_relative_short": {"side": "short", "role": "capped_short"},
    "weak_market_short": {"side": "short", "role": "backup_short"},
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

def text_blob(idea: dict[str, Any]) -> str:
    fields = [
        "candidate_key", "family_key", "side", "edge", "regime",
        "why", "failure_modes", "entry_rule", "exit_rule", "hold_time", "cooldown"
    ]
    return " ".join(str(idea.get(k, "")) for k in fields).lower()

def has_any(txt: str, words: list[str]) -> bool:
    return any(w.lower() in txt for w in words)

def has_stabilization_filter(txt: str) -> bool:
    stabilization_terms = [
        "stabilization",
        "stabilize",
        "coin_ret1_bps > 0",
        "mkt_ret1_bps > 0",
        "recovery",
        "close above",
        "above recent low",
        "range compression",
        "reversal confirmation",
        "low recovery",
        "market stabilization",
    ]
    return has_any(txt, stabilization_terms)

def score_candidate(
    idea: dict[str, Any],
    failed_exact_candidates: set[str],
    failed_patterns: set[str],
) -> dict[str, Any]:
    candidate_key = str(idea.get("candidate_key", ""))
    family_key = str(idea.get("family_key", ""))
    side = str(idea.get("side", ""))
    readiness = float(idea.get("readiness_score") or 0.0)
    contract_ready = bool(idea.get("contract_ready", False))
    txt = text_blob(idea)

    score = 0.0
    reasons = []
    blockers = []
    required_redesign = []

    # Base.
    score += readiness * 0.35
    reasons.append(f"readiness_score={readiness}")

    if contract_ready:
        score += 20
        reasons.append("contract_ready")
    else:
        blockers.append("NOT_CONTRACT_READY")

    # Exact failed candidate is blocked.
    if candidate_key in failed_exact_candidates:
        blockers.append("EXACT_CANDIDATE_FAILED_NEGATIVE_SELFTEST")
        score -= 999
        required_redesign.append("Exact current rule is blocked until redesigned.")
        reasons.append("blocked_by_learning_memory_exact_failure")

    # Learned negative pattern: panic rebound without stabilization.
    is_panic_rebound_like = has_any(txt, ["panic", "rebound", "flush", "liquidation", "market dumps"])
    is_snapback_like = has_any(txt, ["snapback", "relative weakness", "underperforms", "isolated coin weakness"])

    if "panic_rebound_without_stabilization" in failed_patterns:
        if is_panic_rebound_like and not has_stabilization_filter(txt):
            blockers.append("LEARNED_BLOCK_PANIC_REBOUND_WITHOUT_STABILIZATION")
            score -= 120
            required_redesign.extend([
                "Add stabilization confirmation before long entry.",
                "Add short-term reversal or recovery feature.",
                "Do not use market dump + coin dump alone."
            ])

        if is_snapback_like and side == "long" and not has_stabilization_filter(txt):
            blockers.append("LEARNED_CAUTION_SNAPBACK_LONG_WITHOUT_STABILIZATION")
            score -= 45
            required_redesign.extend([
                "Snapback long also needs stabilization/reversal confirmation.",
                "Avoid catching isolated falling knife without recovery evidence."
            ])

    # MASTER overlap.
    if "impulse" in family_key or "impulse" in candidate_key:
        score -= 12
        reasons.append("overlaps_active_impulse_long_but_not_failed_pattern")

    if "relative_continuation" in family_key or "market_relative" in family_key:
        score -= 18
        reasons.append("overlaps_active_market_relative_short_family")

    if "weak_market" in family_key:
        score -= 12
        reasons.append("overlaps_weak_market_backup_family")

    # Archived rel_extreme-like caution.
    if side == "short" and has_any(txt, ["blowoff", "extreme", "reversion", "rel_ret_bps >= 600"]):
        score -= 30
        blockers.append("CAUTION_SIMILAR_TO_ARCHIVED_REL_EXTREME_REVERSION")
        required_redesign.append("Must avoid duplicate/stale shadow pattern seen in rel_extreme.")

    # Diversification logic.
    if side == "long":
        score += 10
        reasons.append("long_side_diversifies_short_heavy_master")
    elif side == "short":
        score += 2
        reasons.append("short_side_less_diversifying_current_master")

    # Prefer momentum/drift long over falling-knife rebound after learned failure.
    if side == "long" and has_any(txt, ["impulse", "drift", "momentum", "market confirmation", "breakout"]):
        score += 22
        reasons.append("preferred_after_panic_rebound_failure_positive_momentum_long")

    # Prefer candidates whose failure mode is not the learned one.
    if not is_panic_rebound_like and not is_snapback_like:
        score += 8
        reasons.append("orthogonal_to_failed_panic_rebound_pattern")

    # Determine policy status.
    if "EXACT_CANDIDATE_FAILED_NEGATIVE_SELFTEST" in blockers:
        policy_status = "BLOCKED_ARCHIVE_WAIT_REDESIGN_REQUIRED"
        allowed_for_contract = False
    elif any(b.startswith("LEARNED_BLOCK_") for b in blockers):
        policy_status = "BLOCKED_BY_RESEARCH_LEARNING_POLICY"
        allowed_for_contract = False
    elif contract_ready:
        policy_status = "ALLOWED_FOR_NEXT_CONTRACT_WITH_CAUTION" if blockers else "ALLOWED_FOR_NEXT_CONTRACT"
        allowed_for_contract = True
    else:
        policy_status = "INCOMPLETE_NOT_ALLOWED"
        allowed_for_contract = False

    return {
        "candidate_key": candidate_key,
        "family_key": family_key,
        "side": side,
        "learning_aware_score": round(score, 2),
        "policy_status": policy_status,
        "allowed_for_contract": allowed_for_contract,
        "contract_ready": contract_ready,
        "readiness_score": readiness,
        "reasons": reasons,
        "blockers": blockers,
        "required_redesign": sorted(set(required_redesign)),
        "contract_generator_command": idea.get("contract_generator_command", ""),
        "promotion_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
    }

def main() -> int:
    out_dir = OUT_ROOT / f"learning_aware_candidate_selector_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    ideas = read_jsonl(IDEA_LEDGER)
    memories = read_jsonl(LEARNING_MEMORY)

    failed_exact_candidates = set()
    failed_patterns = set()

    for m in memories:
        if m.get("decision") == "FULL_RUN_BLOCKED_NEGATIVE_SELFTEST":
            ck = m.get("candidate_key")
            if ck:
                failed_exact_candidates.add(str(ck))
            for tag in m.get("failure_tags", []):
                failed_patterns.add(str(tag))

    scored = [
        score_candidate(idea, failed_exact_candidates, failed_patterns)
        for idea in ideas
    ]

    scored = sorted(scored, key=lambda x: x["learning_aware_score"], reverse=True)

    allowed = [x for x in scored if x["allowed_for_contract"]]
    blocked = [x for x in scored if not x["allowed_for_contract"]]

    top = allowed[0] if allowed else None

    if top:
        selector_status = "LEARNING_AWARE_SELECTION_READY"
        next_action = "GENERATE_CONTRACT_FOR_SELECTED_CANDIDATE"
    elif scored:
        selector_status = "NO_ALLOWED_CANDIDATES_AFTER_LEARNING_POLICY"
        next_action = "GENERATE_NEW_IDEAS_OR_REDESIGN_BLOCKED_CANDIDATES"
    else:
        selector_status = "NO_IDEAS_AVAILABLE"
        next_action = "SEED_OR_ADD_IDEAS"

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "selector_status": selector_status,
        "idea_count": len(ideas),
        "learning_memory_count": len(memories),
        "failed_exact_candidates": sorted(failed_exact_candidates),
        "failed_patterns": sorted(failed_patterns),
        "top_candidate": top,
        "ranked_candidates": scored,
        "allowed_count": len(allowed),
        "blocked_count": len(blocked),
        "next_action": next_action,
        "policy_summary": {
            "panic_rebound_without_stabilization": "blocked after negative self-test",
            "snapback_long_without_stabilization": "allowed only with caution/redesign",
            "exact_failed_candidate": "archive_wait_redesign_required",
            "rel_extreme_like_short_reversion": "caution due stale/duplicate shadow history"
        },
        "promotion_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Selector only ranks ideas using learning memory.",
            "Does not generate contracts by itself.",
            "Does not run backtests.",
            "Does not touch MASTER_UPPER_SYSTEM.",
            "Does not start/stop processes.",
            "Does not place orders.",
            "Does not enable live trading.",
            "Does not change capital."
        ],
    }

    state_path = out_dir / "learning_aware_candidate_selector_v1_state.json"
    ranked_csv = out_dir / "learning_aware_candidate_selector_v1_ranked.csv"
    report_path = out_dir / "learning_aware_candidate_selector_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    pd.DataFrame(scored).to_csv(ranked_csv, index=False)

    md = []
    md.append("# Edge Factory Learning-Aware Candidate Selector v1")
    md.append("")
    md.append(f"Status: `{selector_status}`")
    md.append(f"Ideas: `{len(ideas)}`")
    md.append(f"Learning memories: `{len(memories)}`")
    md.append(f"Next action: `{next_action}`")
    md.append("")
    if top:
        md.append("## Selected candidate")
        md.append(f"- `{top['candidate_key']}` score `{top['learning_aware_score']}` status `{top['policy_status']}`")
        md.append("")
        md.append("## Contract generator command")
        md.append("```powershell")
        md.append(top.get("contract_generator_command", ""))
        md.append("```")
    md.append("")
    md.append("## Ranked candidates")
    for x in scored:
        md.append(f"- `{x['candidate_key']}` — score `{x['learning_aware_score']}` / `{x['policy_status']}`")
    md.append("")
    md.append("## Safety")
    md.append("- promotion_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY LEARNING-AWARE CANDIDATE SELECTOR v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"selector_status: {selector_status}")
    print(f"idea_count: {len(ideas)}")
    print(f"learning_memory_count: {len(memories)}")
    print(f"failed_exact_candidates: {sorted(failed_exact_candidates)}")
    print(f"failed_patterns: {sorted(failed_patterns)}")
    print(f"allowed_count: {len(allowed)}")
    print(f"blocked_count: {len(blocked)}")
    print(f"next_action: {next_action}")
    print("promotion_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()

    print("RANKED CANDIDATES")
    print("-" * 100)
    if scored:
        df = pd.DataFrame(scored)
        print(df[["candidate_key","family_key","side","learning_aware_score","policy_status","allowed_for_contract"]].to_string(index=False))
    else:
        print("No candidates.")

    print()
    print("SELECTED")
    print("-" * 100)
    if top:
        print(f"{top['candidate_key']} -> {top['policy_status']} score={top['learning_aware_score']}")
        print()
        print("CONTRACT GENERATOR COMMAND")
        print("-" * 100)
        print(top.get("contract_generator_command", ""))
    else:
        print("No allowed candidate.")

    print()
    print(f"State : {state_path}")
    print(f"Ranked: {ranked_csv}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
