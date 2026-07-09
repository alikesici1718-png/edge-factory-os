#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reads the candidate idea bank ledger and research learning memory to score and rank offline strategy candidates against active master families, selecting the best candidates for further pipeline processing.
Outputs ranked candidate selections as JSON to the edge_factory_learning_aware_candidate_selector_v2 workspace directory.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_learning_aware_candidate_selector_v2"

IDEA_LEDGER = WORKSPACE / "edge_factory_candidate_idea_bank_v1" / "candidate_idea_bank_master_ledger.jsonl"
MEMORY = WORKSPACE / "edge_factory_os_research_learning_controller_v1" / "edge_factory_research_learning_memory_master.jsonl"

ACTIVE_MASTER_FAMILIES = {
    "old_short": {"side": "short", "role": "core_short"},
    "impulse_long": {"side": "long", "role": "active_long_diversifier"},
    "market_relative_short": {"side": "short", "role": "capped_short"},
    "weak_market_short": {"side": "short", "role": "backup_short"},
}

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}

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

def latest_file(root: Path, pattern: str) -> Path | None:
    files = list(root.rglob(pattern)) if root.exists() else []
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def text_blob(idea: dict[str, Any]) -> str:
    keys = [
        "candidate_key", "family_key", "side", "edge", "regime",
        "why", "failure_modes", "entry_rule", "exit_rule", "hold_time", "cooldown"
    ]
    return " ".join(str(idea.get(k, "")) for k in keys).lower()

def has_any(txt: str, terms: list[str]) -> bool:
    return any(t.lower() in txt for t in terms)

def extract_policy_inputs() -> dict[str, Any]:
    memories = read_jsonl(MEMORY)

    blocklist_path = latest_file(
        WORKSPACE / "edge_factory_strict_validation_learning_finalizer_v1",
        "learning_selector_blocklist_v1.json"
    )
    archive_path = latest_file(
        WORKSPACE / "edge_factory_strict_validation_learning_finalizer_v1",
        "candidate_archive_policy_v1.json"
    )
    directive_path = latest_file(
        WORKSPACE / "edge_factory_strict_validation_learning_finalizer_v1",
        "next_research_directive_v1.json"
    )

    blocklist = read_json(blocklist_path)
    archive = read_json(archive_path)
    directive = read_json(directive_path)

    exact_blocks = set()
    family_cooldowns = set()
    failed_patterns = set()
    hard_blocks = set()

    for m in memories:
        ck = m.get("candidate_key")
        base = m.get("base_candidate_key")
        fam = m.get("family_key")

        if m.get("decision") in {
            "FULL_RUN_BLOCKED_NEGATIVE_SELFTEST",
            "STRICT_VALIDATION_FAIL",
            "STRICT_VALIDATION_FAIL_ARCHIVE_OR_REDESIGN",
        }:
            if ck:
                exact_blocks.add(str(ck))
            if base:
                exact_blocks.add(str(base))
            if fam:
                family_cooldowns.add(str(fam))

        for tag in m.get("failure_tags", []):
            failed_patterns.add(str(tag))
        for hb in m.get("hard_blocks", []):
            hard_blocks.add(str(hb))

    for x in blocklist.get("exact_candidate_blocks", []):
        ck = x.get("candidate_key")
        if ck:
            exact_blocks.add(str(ck))

    for x in blocklist.get("family_cooldowns", []):
        fk = x.get("family_key")
        if fk:
            family_cooldowns.add(str(fk))

    archive_updates = archive.get("candidate_updates", {})
    if isinstance(archive_updates, dict):
        for ck, info in archive_updates.items():
            if info.get("exact_rule_blocked") or info.get("exact_original_rule_blocked") or info.get("threshold_only_retune_blocked"):
                exact_blocks.add(str(ck))

    family_updates = archive.get("family_updates", {})
    if isinstance(family_updates, dict):
        for fk, info in family_updates.items():
            if info.get("research_status") == "COOLDOWN_REQUIRES_NEW_FEATURE_EVIDENCE":
                family_cooldowns.add(str(fk))

    return {
        "memories": memories,
        "blocklist_path": str(blocklist_path) if blocklist_path else "",
        "archive_path": str(archive_path) if archive_path else "",
        "directive_path": str(directive_path) if directive_path else "",
        "blocklist": blocklist,
        "archive": archive,
        "directive": directive,
        "exact_blocks": sorted(exact_blocks),
        "family_cooldowns": sorted(family_cooldowns),
        "failed_patterns": sorted(failed_patterns),
        "hard_blocks": sorted(hard_blocks),
    }

def score_idea(idea: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    ck = str(idea.get("candidate_key", ""))
    fk = str(idea.get("family_key", ""))
    side = str(idea.get("side", ""))
    readiness = float(idea.get("readiness_score") or 0.0)
    contract_ready = bool(idea.get("contract_ready", False))
    txt = text_blob(idea)

    exact_blocks = set(policy["exact_blocks"])
    family_cooldowns = set(policy["family_cooldowns"])
    failed_patterns = set(policy["failed_patterns"])
    hard_blocks_memory = set(policy["hard_blocks"])

    score = readiness * 0.25
    reasons = [f"readiness_score={readiness}"]
    blockers = []
    caution = []
    required_before_contract = []

    if not contract_ready:
        blockers.append("NOT_CONTRACT_READY")

    if ck in exact_blocks:
        blockers.append("EXACT_CANDIDATE_BLOCKED_BY_LEARNING_MEMORY")
        score -= 1000
        required_before_contract.append("Requires genuinely new feature evidence, not threshold retune.")

    if fk in family_cooldowns:
        blockers.append("FAMILY_IN_RESEARCH_COOLDOWN_REQUIRES_NEW_FEATURE_EVIDENCE")
        score -= 300
        required_before_contract.append("Family cooldown: must introduce new explanatory feature before retest.")

    # Learned failure pattern: panic/snapback long without stabilization.
    if "panic_rebound_without_stabilization" in failed_patterns:
        if has_any(txt, ["panic", "rebound", "flush", "liquidation"]) and not has_any(txt, ["stabilization", "recovery", "coin_ret1", "mkt_ret1", "close above", "range compression"]):
            blockers.append("LEARNED_BLOCK_PANIC_REBOUND_WITHOUT_STABILIZATION")
            score -= 200

        if has_any(txt, ["snapback", "relative weakness", "underperforms"]) and side == "long" and not has_any(txt, ["stabilization", "recovery", "coin_ret1", "mkt_ret1", "close above"]):
            blockers.append("LEARNED_BLOCK_SNAPBACK_LONG_WITHOUT_STABILIZATION")
            score -= 150

    # Learned failure pattern: threshold-only retune after strict fail.
    if "BLOCK_FULL_RUN_FULL_PF_BELOW_ONE" in hard_blocks_memory or "strict_validation_failed" in failed_patterns:
        if has_any(txt, ["impulse", "drift"]) and fk in family_cooldowns:
            blockers.append("LEARNED_BLOCK_THRESHOLD_ONLY_IMPULSE_DRIFT_RETUNE")
            score -= 250

    # Existing family overlap.
    if "market_relative" in fk or "relative_continuation" in fk:
        blockers.append("OVERLAPS_ACTIVE_MARKET_RELATIVE_SHORT_FAMILY")
        score -= 120

    if "impulse" in fk and fk not in family_cooldowns:
        caution.append("OVERLAPS_ACTIVE_IMPULSE_LONG_FAMILY")
        score -= 25

    if side == "short" and has_any(txt, ["blowoff", "extreme", "reversion", "rel_ret_bps"]):
        caution.append("SIMILAR_TO_ARCHIVED_REL_EXTREME_REQUIRES_DUPLICATE_SHADOW_GUARD")
        score -= 35
        required_before_contract.append("Must include duplicate/stale shadow safeguards and anti-replay rule.")

    # Reward orthogonality.
    if not blockers:
        score += 30
        reasons.append("no_hard_learning_block")

    if side == "long":
        score += 8
        reasons.append("long_diversifies_short_heavy_master")
    else:
        score += 3
        reasons.append("short_less_diversifying_current_master")

    if side == "short" and not ("market_relative" in fk or "relative_continuation" in fk):
        score += 10
        reasons.append("short_candidate_not_direct_market_relative_family")

    if blockers:
        policy_status = "BLOCKED_BY_LEARNING_POLICY"
        allowed_for_contract = False
    elif caution:
        policy_status = "ALLOWED_WITH_GUARDS_REQUIRED"
        allowed_for_contract = True
    else:
        policy_status = "ALLOWED_FOR_NEXT_CONTRACT"
        allowed_for_contract = True

    return {
        "candidate_key": ck,
        "family_key": fk,
        "side": side,
        "selector_v2_score": round(score, 2),
        "policy_status": policy_status,
        "allowed_for_contract": allowed_for_contract,
        "contract_ready": contract_ready,
        "reasons": reasons,
        "blockers": blockers,
        "caution": caution,
        "required_before_contract": sorted(set(required_before_contract)),
        "contract_generator_command": idea.get("contract_generator_command", ""),
        "promotion_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
    }

def main() -> int:
    out_dir = OUT_ROOT / f"learning_aware_candidate_selector_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    ideas = read_jsonl(IDEA_LEDGER)
    policy = extract_policy_inputs()

    scored = [score_idea(x, policy) for x in ideas]
    scored = sorted(scored, key=lambda x: x["selector_v2_score"], reverse=True)

    allowed = [x for x in scored if x["allowed_for_contract"]]
    blocked = [x for x in scored if not x["allowed_for_contract"]]
    top = allowed[0] if allowed else None

    if top and top["policy_status"] == "ALLOWED_WITH_GUARDS_REQUIRED":
        selector_status = "SELECTOR_V2_GUARDED_CANDIDATE_AVAILABLE"
        next_action = "CREATE_GUARDED_CONTRACT_OR_SEED_NEW_ORTHOGONAL_IDEAS"
    elif top:
        selector_status = "SELECTOR_V2_SELECTION_READY"
        next_action = "GENERATE_CONTRACT_FOR_SELECTED_CANDIDATE"
    else:
        selector_status = "SELECTOR_V2_NO_SAFE_EXISTING_CANDIDATE"
        next_action = "SEED_NEW_ORTHOGONAL_IDEAS"

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "selector_status": selector_status,
        "idea_count": len(ideas),
        "memory_count": len(policy["memories"]),
        "exact_blocks": policy["exact_blocks"],
        "family_cooldowns": policy["family_cooldowns"],
        "failed_patterns": policy["failed_patterns"],
        "hard_blocks": policy["hard_blocks"],
        "blocklist_path": policy["blocklist_path"],
        "archive_path": policy["archive_path"],
        "directive_path": policy["directive_path"],
        "allowed_count": len(allowed),
        "blocked_count": len(blocked),
        "top_candidate": top,
        "ranked_candidates": scored,
        "next_action": next_action,
        "os_intelligence_gain": [
            "Reads strict validation failures, not only self-test failures.",
            "Blocks exact failed candidates and base candidates.",
            "Applies family cooldown when threshold-only retune failed.",
            "Requires guards for rel_extreme-like short reversion ideas.",
            "Can decide to seed new ideas instead of forcing remaining weak ideas."
        ],
        "promotion_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
    }

    state_path = out_dir / "learning_aware_candidate_selector_v2_state.json"
    ranked_csv = out_dir / "learning_aware_candidate_selector_v2_ranked.csv"
    report_path = out_dir / "learning_aware_candidate_selector_v2_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    pd.DataFrame(scored).to_csv(ranked_csv, index=False)

    md = []
    md.append("# Edge Factory Learning-Aware Candidate Selector v2")
    md.append("")
    md.append(f"Status: `{selector_status}`")
    md.append(f"Memory count: `{len(policy['memories'])}`")
    md.append(f"Allowed: `{len(allowed)}`")
    md.append(f"Blocked: `{len(blocked)}`")
    md.append(f"Next action: `{next_action}`")
    md.append("")
    if top:
        md.append("## Top candidate")
        md.append(f"- `{top['candidate_key']}` score `{top['selector_v2_score']}` status `{top['policy_status']}`")
        if top["required_before_contract"]:
            md.append("")
            md.append("### Required before contract")
            for x in top["required_before_contract"]:
                md.append(f"- {x}")
    else:
        md.append("No safe existing candidate.")
    md.append("")
    md.append("## Ranked")
    for x in scored:
        md.append(f"- `{x['candidate_key']}` — `{x['policy_status']}` score `{x['selector_v2_score']}`")
    md.append("")
    md.append("## Safety")
    md.append("- promotion_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY LEARNING-AWARE CANDIDATE SELECTOR v2")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"selector_status: {selector_status}")
    print(f"idea_count: {len(ideas)}")
    print(f"memory_count: {len(policy['memories'])}")
    print(f"exact_blocks: {policy['exact_blocks']}")
    print(f"family_cooldowns: {policy['family_cooldowns']}")
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
        print(df[["candidate_key","family_key","side","selector_v2_score","policy_status","allowed_for_contract"]].to_string(index=False))
    else:
        print("No ideas.")
    print()
    print("TOP")
    print("-" * 100)
    if top:
        print(f"{top['candidate_key']} -> {top['policy_status']} score={top['selector_v2_score']}")
        if top["required_before_contract"]:
            print("required_before_contract:")
            for x in top["required_before_contract"]:
                print("-", x)
        print()
        print("CONTRACT COMMAND")
        print("-" * 100)
        print(top.get("contract_generator_command", ""))
    else:
        print("No safe existing candidate. Seed new orthogonal ideas.")
    print()
    print(f"State : {state_path}")
    print(f"Ranked: {ranked_csv}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
