#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Decides the next research routing action (guarded contract, new idea seeding, or blocked) by reading the learning-aware candidate selector v2 state and the research learning memory JSONL. Outputs a route decision state JSON to the edge_factory_research_route_decision_v1 directory based on top-candidate policy status, score, and accumulated failure tags.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_research_route_decision_v1"

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def latest_file(root: Path, pattern: str) -> Path | None:
    files = list(root.rglob(pattern)) if root.exists() else []
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def read_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e)}

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

def main() -> int:
    out_dir = OUT_ROOT / f"research_route_decision_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    selector_path = latest_file(
        WORKSPACE / "edge_factory_learning_aware_candidate_selector_v2",
        "learning_aware_candidate_selector_v2_state.json"
    )
    selector = read_json(selector_path)

    memory_path = WORKSPACE / "edge_factory_os_research_learning_controller_v1" / "edge_factory_research_learning_memory_master.jsonl"
    memories = read_jsonl(memory_path)

    top = selector.get("top_candidate") or {}
    ranked = selector.get("ranked_candidates") or []

    blockers = []
    if not selector:
        blockers.append("SELECTOR_V2_STATE_NOT_FOUND")
    if "__read_error__" in selector:
        blockers.append("SELECTOR_V2_STATE_READ_ERROR")

    candidate_key = top.get("candidate_key", "")
    family_key = top.get("family_key", "")
    policy_status = top.get("policy_status", "")
    score = float(top.get("selector_v2_score") or -999)

    guard_required = policy_status == "ALLOWED_WITH_GUARDS_REQUIRED"
    safe_direct_candidate = policy_status == "ALLOWED_FOR_NEXT_CONTRACT" and score >= 50
    low_score_guarded_candidate = guard_required and score < 50

    memory_failure_tags = sorted(set(
        tag
        for m in memories
        for tag in (m.get("failure_tags") or [])
    ))

    # Route logic.
    if blockers:
        route_status = "RESEARCH_ROUTE_BLOCKED"
        route_decision = "FIX_ROUTE_INPUTS"
        guarded_contract_allowed = False
        seed_new_ideas_allowed = False
        next_action = "FIX_SELECTOR_OR_MEMORY_INPUTS"

    elif not top:
        route_status = "RESEARCH_ROUTE_NO_CANDIDATE"
        route_decision = "SEED_NEW_ORTHOGONAL_IDEAS"
        guarded_contract_allowed = False
        seed_new_ideas_allowed = True
        next_action = "RUN_ORTHOGONAL_IDEA_SEEDER_V2"

    elif safe_direct_candidate:
        route_status = "RESEARCH_ROUTE_DIRECT_CONTRACT_ALLOWED"
        route_decision = "GENERATE_CONTRACT_FOR_TOP_CANDIDATE"
        guarded_contract_allowed = False
        seed_new_ideas_allowed = False
        next_action = "GENERATE_CONTRACT"

    elif guard_required:
        route_status = "RESEARCH_ROUTE_GUARDED_CANDIDATE_NEEDS_PRECONDITIONS"
        route_decision = "DO_NOT_RUN_GUARDED_CANDIDATE_YET"
        guarded_contract_allowed = False
        seed_new_ideas_allowed = True if low_score_guarded_candidate else False
        next_action = "CREATE_GUARD_SPEC_AND_SEED_ORTHOGONAL_IDEAS"

    else:
        route_status = "RESEARCH_ROUTE_NO_SAFE_EXISTING_CANDIDATE"
        route_decision = "SEED_NEW_ORTHOGONAL_IDEAS"
        guarded_contract_allowed = False
        seed_new_ideas_allowed = True
        next_action = "RUN_ORTHOGONAL_IDEA_SEEDER_V2"

    guard_spec = {
        "guard_spec_version": "edge_factory_guarded_candidate_preconditions_v1",
        "created_at": now_iso(),
        "applies_to_candidate": candidate_key,
        "applies_to_family": family_key,
        "guard_required": guard_required,
        "reason": "Candidate is similar to archived rel_extreme-style short reversion and must not repeat duplicate/stale shadow behavior.",
        "required_before_contract": [
            "Add deterministic signal_id = candidate_key + symbol + entry_time + rule_version hash.",
            "Enforce unique candidate_key + symbol + entry_time.",
            "Enforce 24h per-symbol cooldown before creating a second signal.",
            "Reject stale/replayed signals older than the current evaluation window.",
            "Add duplicate-signal audit before any runner/self-test.",
            "Feature builder must derive rel_ret_bps explicitly, not assume it exists.",
            "Contract must include anti-replay and duplicate guard fields.",
            "No active paper, no live, no capital change even if offline diagnostic passes."
        ],
        "required_feature_support": [
            "coin_ret6_bps",
            "coin_ret24_bps",
            "mkt_ret6_bps",
            "rel_ret_bps = coin_ret6_bps - mkt_ret6_bps",
            "entry_vol_quote",
            "entry_range_bps"
        ],
        "hard_blocks_if_missing": [
            "NO_SIGNAL_ID_GUARD",
            "NO_DUPLICATE_AUDIT",
            "NO_STALE_REPLAY_GUARD",
            "NO_REL_RET_DERIVATION",
            "NO_COOLDOWN"
        ],
        "guarded_contract_allowed_now": False
    }

    orthogonal_seed_directive = {
        "directive_version": "edge_factory_orthogonal_idea_seed_directive_v2",
        "created_at": now_iso(),
        "why": "Existing idea bank is mostly exhausted or blocked by learning memory. The only remaining idea is guarded/low-score.",
        "avoid_patterns": [
            "panic rebound without stabilization",
            "snapback long without stabilization",
            "threshold-only post impulse retune",
            "market_relative_short overlap",
            "rel_extreme duplicate/stale shadow pattern"
        ],
        "prefer_new_idea_families": [
            {
                "family_key": "volatility_compression_breakout",
                "side": "both",
                "hypothesis": "After volatility compression and market alignment, breakouts may continue with cleaner risk than raw impulse chasing."
            },
            {
                "family_key": "failed_breakout_reversal",
                "side": "short",
                "hypothesis": "Coins that break out then fail back below breakout level may reverse without relying on stale rel_extreme replay."
            },
            {
                "family_key": "liquidity_rotation_continuation",
                "side": "long",
                "hypothesis": "Coins receiving rising relative quote volume while market breadth is positive may continue."
            },
            {
                "family_key": "range_expansion_exhaustion",
                "side": "short",
                "hypothesis": "Extreme range expansion after multi-hour overextension may mean-revert only if exhaustion structure is present."
            },
            {
                "family_key": "market_breadth_filter_family",
                "side": "both",
                "hypothesis": "Use market-wide breadth features to avoid regimes where single-coin signals fail."
            }
        ],
        "required_new_feature_classes": [
            "market breadth",
            "volatility compression / expansion",
            "follow-through confirmation",
            "failed breakout structure",
            "liquidity rotation",
            "anti-duplicate event identity"
        ],
        "seed_new_ideas_allowed": seed_new_ideas_allowed
    }

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "route_status": route_status,
        "route_decision": route_decision,
        "next_action": next_action,
        "selector_path": str(selector_path) if selector_path else "",
        "memory_path": str(memory_path),
        "memory_count": len(memories),
        "memory_failure_tags": memory_failure_tags,
        "top_candidate": top,
        "ranked_candidate_count": len(ranked),
        "guard_required": guard_required,
        "guarded_contract_allowed": guarded_contract_allowed,
        "seed_new_ideas_allowed": seed_new_ideas_allowed,
        "safe_direct_candidate": safe_direct_candidate,
        "low_score_guarded_candidate": low_score_guarded_candidate,
        "guard_spec_path": "",
        "orthogonal_seed_directive_path": "",
        "promotion_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Route decision only.",
            "Does not generate contracts.",
            "Does not run backtests.",
            "Does not touch MASTER_UPPER_SYSTEM.",
            "Does not start/stop processes.",
            "Does not place orders.",
            "Does not enable live trading.",
            "Does not change capital."
        ],
    }

    guard_spec_path = out_dir / "guarded_candidate_preconditions_v1.json"
    seed_directive_path = out_dir / "orthogonal_idea_seed_directive_v2.json"
    state_path = out_dir / "research_route_decision_v1_state.json"
    report_path = out_dir / "research_route_decision_v1_report.md"

    guard_spec_path.write_text(json.dumps(guard_spec, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    seed_directive_path.write_text(json.dumps(orthogonal_seed_directive, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    state["guard_spec_path"] = str(guard_spec_path)
    state["orthogonal_seed_directive_path"] = str(seed_directive_path)

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    md = []
    md.append("# Edge Factory Research Route Decision v1")
    md.append("")
    md.append(f"Route status: `{route_status}`")
    md.append(f"Route decision: `{route_decision}`")
    md.append(f"Next action: `{next_action}`")
    md.append("")
    md.append("## Top candidate")
    if top:
        md.append(f"- `{candidate_key}` / `{family_key}` / score `{score}` / `{policy_status}`")
    else:
        md.append("- None")
    md.append("")
    md.append("## Decision")
    md.append(f"- guarded_contract_allowed: `{guarded_contract_allowed}`")
    md.append(f"- seed_new_ideas_allowed: `{seed_new_ideas_allowed}`")
    md.append("")
    md.append("## Safety")
    md.append("- promotion_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY RESEARCH ROUTE DECISION v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"route_status: {route_status}")
    print(f"route_decision: {route_decision}")
    print(f"top_candidate: {candidate_key}")
    print(f"family_key: {family_key}")
    print(f"policy_status: {policy_status}")
    print(f"score: {score}")
    print(f"guard_required: {guard_required}")
    print(f"guarded_contract_allowed: {guarded_contract_allowed}")
    print(f"seed_new_ideas_allowed: {seed_new_ideas_allowed}")
    print(f"next_action: {next_action}")
    print("promotion_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("GUARD REQUIREMENTS")
    print("-" * 100)
    for x in guard_spec["required_before_contract"]:
        print("-", x)
    print()
    print("ORTHOGONAL SEED FAMILIES")
    print("-" * 100)
    for x in orthogonal_seed_directive["prefer_new_idea_families"]:
        print(f"- {x['family_key']} / {x['side']}: {x['hypothesis']}")
    print()
    print(f"State    : {state_path}")
    print(f"GuardSpec: {guard_spec_path}")
    print(f"SeedPlan : {seed_directive_path}")
    print(f"Report   : {report_path}")

if __name__ == "__main__":
    main()
