from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_research_direction_contract_builder_v2"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

QUEUE_V2_LATEST = (
    BASE_DIR
    / "edge_factory_os_new_research_direction_queue_v2"
    / "new_research_direction_queue_v2_latest.json"
)

STRICT_POLICY_LATEST = (
    BASE_DIR
    / "edge_factory_os_policy_guards"
    / "strict_month_stability_policy_latest.json"
)

BLOCKLIST_PATH = (
    BASE_DIR
    / "edge_factory_os_lesson_memory"
    / "candidate_route_blocklist.json"
)

LESSON_INDEX_PATH = (
    BASE_DIR
    / "edge_factory_os_lesson_memory"
    / "lesson_memory_index.json"
)

UNIVERSE_GUARD_V2_LATEST = (
    BASE_DIR
    / "edge_factory_os_universe_coverage_guard_v2"
    / "universe_coverage_guard_v2_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"research_direction_contract_builder_v2_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "research_direction_contract_builder_v2_latest.json"
LATEST_MD = OUT_ROOT / "research_direction_contract_builder_v2_latest.md"

CONTRACT_ROOT = BASE_DIR / "edge_factory_os_research_direction_contracts"
CONTRACT_LATEST = CONTRACT_ROOT / "strict_month_stable_new_archetype_search_contract_latest.json"


def load_json(path: Path) -> Optional[Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, default=str)


def stable_hash(obj: Any) -> str:
    text = json.dumps(obj, sort_keys=True, default=str)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def safe_get(d: Dict[str, Any], path: List[str], default=None):
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def select_top_direction(queue_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    directions = queue_state.get("directions")
    if not isinstance(directions, list):
        return None

    valid = [
        d for d in directions
        if isinstance(d, dict)
        and d.get("status") == "QUEUED_READ_ONLY_RESEARCH"
        and d.get("candidate_generation_allowed_now") is False
        and d.get("strict_month_policy_required") is True
    ]

    if not valid:
        return None

    valid.sort(key=lambda x: int(x.get("priority") or 0), reverse=True)
    return valid[0]


def extract_blocked_hashes(blocklist: Dict[str, Any]) -> List[str]:
    routes = blocklist.get("blocked_routes")
    if not isinstance(routes, list):
        return []

    out = []
    for row in routes:
        if isinstance(row, dict) and row.get("route_hash"):
            out.append(str(row["route_hash"]))

    return sorted(set(out))


def build_contract(
    direction: Dict[str, Any],
    strict_policy: Dict[str, Any],
    blocklist: Dict[str, Any],
    lesson_index: Dict[str, Any],
    universe: Dict[str, Any],
) -> Dict[str, Any]:
    blocked_hashes = extract_blocked_hashes(blocklist)
    best_manifest = universe.get("best_universe_manifest") or {}
    panel_path = best_manifest.get("panel_path")

    release_req = strict_policy.get("release_requirement") or {
        "min_active_months": 12,
        "min_positive_months": 11,
        "min_positive_month_rate": 11 / 12,
    }

    contract_core = {
        "research_key": direction.get("research_key"),
        "direction_id": direction.get("direction_id"),
        "blocked_hashes": blocked_hashes,
        "strict_month_policy": release_req,
        "purpose": "strict_month_stable_new_archetype_search",
    }

    contract_hash = stable_hash(contract_core)
    contract_id = f"STRICT_MONTH_STABLE_NEW_ARCHETYPE_SEARCH_CONTRACT_V1_{contract_hash}_{NOW.strftime('%Y%m%d_%H%M%S')}"

    lessons = lesson_index.get("lessons") if isinstance(lesson_index.get("lessons"), list) else []
    lesson_ids = [
        lesson.get("lesson_id")
        for lesson in lessons
        if isinstance(lesson, dict) and lesson.get("lesson_id")
    ]

    contract = {
        "contract_schema": "edge_factory_os_research_direction_contract_v2",
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "created_at_utc": NOW.isoformat(),

        "research_key": "STRICT_MONTH_STABLE_NEW_ARCHETYPE_SEARCH_V1",
        "source_direction": {
            "direction_id": direction.get("direction_id"),
            "research_key": direction.get("research_key"),
            "priority": direction.get("priority"),
            "primary_question": direction.get("primary_question"),
            "hypothesis": direction.get("hypothesis"),
            "family_scope": direction.get("family_scope"),
        },

        "purpose": (
            "Search for completely new strategy archetypes that can satisfy strict 12-active-month / "
            "11-positive-month stability on the full 1Y OKX swap universe. This is research-contract creation only; "
            "it does not create a family, candidate, runtime patch, active paper change, live change, or capital change."
        ),

        "lesson_memory_context": {
            "blocked_route_hashes": blocked_hashes,
            "required_blocked_route_hashes_present": {
                "90466e4144914fbc": "90466e4144914fbc" in blocked_hashes,
                "85f9e6a4accb14c7": "85f9e6a4accb14c7" in blocked_hashes,
            },
            "known_lesson_ids": lesson_ids,
            "blocked_route_reuse_allowed": False,
            "do_not_repeat": [
                "old ret3 threshold / fixed hold impulse route",
                "regime-filtered impulse route hash 85f9e6a4accb14c7",
                "loose 0.55 positive-month-rate repair",
                "manual bad-month blacklist",
                "manual symbol blacklist",
                "paper-ledger-only validation",
            ],
        },

        "strict_month_stability_policy": {
            "policy_key": strict_policy.get("policy_key"),
            "min_active_months": safe_get(strict_policy, ["release_requirement", "min_active_months"], 12),
            "min_positive_months": safe_get(strict_policy, ["release_requirement", "min_positive_months"], 11),
            "min_positive_month_rate": safe_get(strict_policy, ["release_requirement", "min_positive_month_rate"], 11 / 12),
            "loose_055_month_rate_deprecated_for_release": safe_get(
                strict_policy,
                ["explicitly_deprecated_for_release", "positive_month_rate_gte_0_55_only"],
                True,
            ),
            "must_apply_to_all_future_candidates": True,
        },

        "universe_input": {
            "universe_guard_status": universe.get("universe_status"),
            "panel_path": panel_path,
            "panel_path_exists": bool(Path(str(panel_path)).exists()) if panel_path else False,
            "symbol_count": best_manifest.get("symbol_count"),
            "row_count": best_manifest.get("row_count"),
            "day_span": best_manifest.get("day_span"),
            "start": best_manifest.get("start_raw"),
            "end": best_manifest.get("end_raw"),
            "required": {
                "must_use_full_1y_okx_swap_panel": True,
                "paper_ledger_only_allowed": False,
                "single_symbol_only_allowed": False,
            },
        },

        "archetype_search_space": {
            "allowed_new_archetypes": [
                {
                    "archetype_key": "relative_weakness_snapback_long",
                    "direction": "long",
                    "description": "Long candidates after relative weakness or underperformance snapback, not impulse continuation.",
                    "must_not_share_blocked_route_hash": True,
                },
                {
                    "archetype_key": "panic_rebound_with_strict_regime_guard",
                    "direction": "long",
                    "description": "Long candidates after broad market panic / capitulation rebound with strict month-stability filter.",
                    "must_not_share_blocked_route_hash": True,
                },
                {
                    "archetype_key": "failed_breakout_reversion_short",
                    "direction": "short",
                    "description": "Short/reversion candidates after failed upside breakout or failed impulse follow-through.",
                    "must_not_share_blocked_route_hash": True,
                },
                {
                    "archetype_key": "market_relative_continuation_short",
                    "direction": "short",
                    "description": "Short candidates based on weak market-relative continuation, distinct from impulse-long route.",
                    "must_not_share_blocked_route_hash": True,
                },
                {
                    "archetype_key": "liquidity_shock_mean_reversion",
                    "direction": "long_or_short",
                    "description": "Mean-reversion around liquidity shock/regime extremes, using pre-outcome liquidity/range features.",
                    "must_not_share_blocked_route_hash": True,
                },
                {
                    "archetype_key": "breadth_extreme_reversal",
                    "direction": "long_or_short",
                    "description": "Reversal candidates when market breadth reaches extreme pre-outcome conditions.",
                    "must_not_share_blocked_route_hash": True,
                },
            ],
            "explicitly_disallowed": [
                "same ret3 threshold fixed-hold impulse route",
                "same regime-filtered impulse candidate route",
                "candidate based only on increasing ret3 threshold",
                "candidate based only on fixed hold-hour grid",
                "candidate passing only 7/12 or 8/12 positive months",
                "candidate passing only loose positive_month_rate>=0.55",
                "manual bad-month blacklist",
                "manual symbol blacklist",
            ],
        },

        "required_scanner_behavior": {
            "diagnostic_or_scanner_only": True,
            "candidate_generation_allowed_now": False,
            "family_release_allowed_now": False,
            "promotion_allowed_now": False,
            "runtime_change_allowed_now": False,
            "capital_change_allowed_now": False,
            "must_output_archetype_scoreboard": True,
            "must_output_route_hash_preview_for_each_archetype": True,
            "must_reject_hashes_in_blocklist": True,
            "must_compute_strict_month_stats": True,
            "must_show_positive_month_count_not_only_rate": True,
        },

        "required_validation_policy_for_any_future_candidate": {
            "lesson_memory_route_hash_check": True,
            "full_universe_backtest": True,
            "min_all_trade_count": 300,
            "min_oos_trade_count": 75,
            "min_active_months": safe_get(strict_policy, ["release_requirement", "min_active_months"], 12),
            "min_positive_months": safe_get(strict_policy, ["release_requirement", "min_positive_months"], 11),
            "min_positive_month_rate": safe_get(strict_policy, ["release_requirement", "min_positive_month_rate"], 11 / 12),
            "train_mean_net_bps_must_be_positive": True,
            "oos_mean_net_bps_must_be_positive": True,
            "train_profit_factor_min": 1.10,
            "oos_profit_factor_min": 1.10,
            "cost_slippage_sensitivity_required": True,
            "symbol_concentration_required": True,
            "manual_or_ai_review_cannot_override_failed_tests": True,
        },

        "expected_next_module": {
            "module_name": "edge_factory_os_strict_month_stable_archetype_scanner_v1.py",
            "purpose": (
                "Read this contract and scan multiple new archetype templates on the full 1Y OKX swap panel, "
                "scoring them with strict 12-active-month / 11-positive-month policy. Scanner cannot release or patch anything."
            ),
            "execution_allowed_after_contract": True,
            "candidate_generation_allowed_after_contract": False,
            "family_release_allowed_after_contract": False,
        },

        "safety": {
            "read_only": True,
            "offline_only": True,
            "mutate_runtime_allowed": False,
            "launcher_allowed": False,
            "patch_runtime_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "capital_change_allowed": False,
            "family_disable_allowed": False,
            "real_orders_allowed": False,
            "execution_performed": False,
        },
    }

    return contract


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    CONTRACT_ROOT.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    queue_state = load_json(QUEUE_V2_LATEST)
    strict_policy = load_json(STRICT_POLICY_LATEST)
    blocklist = load_json(BLOCKLIST_PATH)
    lesson_index = load_json(LESSON_INDEX_PATH)
    universe = load_json(UNIVERSE_GUARD_V2_LATEST)

    if not isinstance(queue_state, dict):
        critical.append("new_research_direction_queue_v2_latest_missing")
        queue_state = {}

    if not isinstance(strict_policy, dict):
        critical.append("strict_month_stability_policy_missing")
        strict_policy = {}

    if not isinstance(blocklist, dict):
        critical.append("candidate_route_blocklist_missing")
        blocklist = {}

    if not isinstance(lesson_index, dict):
        attention.append("lesson_index_missing")
        lesson_index = {}

    if not isinstance(universe, dict):
        critical.append("universe_guard_v2_missing")
        universe = {}

    if queue_state.get("queue_status") != "NEW_RESEARCH_DIRECTIONS_V2_QUEUED_LESSON_AWARE":
        critical.append(f"queue_v2_not_ready:{queue_state.get('queue_status')}")

    if strict_policy.get("policy_key") != "STRICT_MONTH_STABILITY_11_OF_12":
        critical.append(f"strict_policy_not_active:{strict_policy.get('policy_key')}")

    if universe.get("universe_status") != "UNIVERSE_COVERAGE_GUARD_V2_PASS_FULL_1Y_OKX_SWAP_PANEL_READY":
        critical.append(f"universe_not_full_pass:{universe.get('universe_status')}")

    top_direction = select_top_direction(queue_state)

    if top_direction is None:
        critical.append("no_valid_top_direction_found")

    elif top_direction.get("research_key") != "RD2_01_STRICT_MONTH_STABLE_NEW_ARCHETYPE_SEARCH":
        attention.append(f"top_direction_not_rd2_01:{top_direction.get('research_key')}")

    blocked_hashes = extract_blocked_hashes(blocklist)
    for required_hash in ["90466e4144914fbc", "85f9e6a4accb14c7"]:
        if required_hash not in blocked_hashes:
            attention.append(f"expected_blocked_hash_missing:{required_hash}")

    contract = None
    contract_written = False

    if critical:
        builder_status = "RESEARCH_DIRECTION_CONTRACT_BUILDER_V2_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_INPUTS_BEFORE_CONTRACT"
        reason = "; ".join(critical)

    else:
        contract = build_contract(top_direction, strict_policy, blocklist, lesson_index, universe)

        contract_path = RUN_DIR / f"{contract['contract_id']}.json"
        dump_json(contract_path, contract)
        dump_json(CONTRACT_LATEST, contract)

        contract["contract_path"] = str(contract_path)
        contract["contract_latest_path"] = str(CONTRACT_LATEST)

        builder_status = "RESEARCH_DIRECTION_CONTRACT_V2_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_STRICT_MONTH_STABLE_ARCHETYPE_SCANNER"
        reason = (
            f"contract_id={contract['contract_id']}; "
            f"research_key={contract['research_key']}; "
            f"blocked_route_count={len(blocked_hashes)}"
        )
        contract_written = True

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "builder_status": builder_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "selected_direction": top_direction,
        "contract": contract,
        "contract_written": contract_written,
        "contract_latest_path": str(CONTRACT_LATEST),

        "sources": {
            "queue_v2_latest": str(QUEUE_V2_LATEST),
            "strict_policy_latest": str(STRICT_POLICY_LATEST),
            "blocklist_path": str(BLOCKLIST_PATH),
            "lesson_index_path": str(LESSON_INDEX_PATH),
            "universe_guard_v2": str(UNIVERSE_GUARD_V2_LATEST),
        },

        "decision": {
            "selected_research_key": top_direction.get("research_key") if top_direction else None,
            "contract_key": contract.get("research_key") if contract else None,
            "candidate_generation_recommended_now": False,
            "family_release_recommended": False,
            "promotion_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "repeat_blocked_routes_recommended": False,
            "next_module": "edge_factory_os_strict_month_stable_archetype_scanner_v1.py" if contract_written else None,
        },

        "safety": {
            "read_only": True,
            "offline_only": True,
            "mutate_runtime_allowed": False,
            "launcher_allowed": False,
            "patch_runtime_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "capital_change_allowed": False,
            "family_disable_allowed": False,
            "real_orders_allowed": False,
            "execution_performed": False,
        },

        "critical": critical,
        "attention": attention,
        "info": info,
    }

    out_json = RUN_DIR / "research_direction_contract_builder_v2_state.json"
    out_md = RUN_DIR / "research_direction_contract_builder_v2_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS RESEARCH DIRECTION CONTRACT BUILDER v2

builder_status: {builder_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

contract_written: {contract_written}  
contract_latest_path: {CONTRACT_LATEST}

## Selected Direction

{json.dumps(top_direction, indent=2, default=str)[:10000]}

## Contract Summary

contract_id: {contract.get("contract_id") if contract else None}  
research_key: {contract.get("research_key") if contract else None}  
contract_hash: {contract.get("contract_hash") if contract else None}  
blocked_route_hashes: {safe_get(contract or {}, ["lesson_memory_context", "blocked_route_hashes"])}  
strict_min_active_months: {safe_get(contract or {}, ["strict_month_stability_policy", "min_active_months"])}  
strict_min_positive_months: {safe_get(contract or {}, ["strict_month_stability_policy", "min_positive_months"])}  
next_module: {safe_get(contract or {}, ["expected_next_module", "module_name"])}

## Decision

{json.dumps(result["decision"], indent=2, default=str)}

## Safety

read_only: True  
offline_only: True  
mutate_runtime_allowed: False  
launcher_allowed: False  
patch_runtime_allowed: False  
active_paper_allowed: False  
live_allowed: False  
capital_change_allowed: False  
family_disable_allowed: False  
real_orders_allowed: False  
execution_performed: False

critical: {critical}  
attention: {attention}  
info: {info}
"""

    out_md.write_text(md, encoding="utf-8")
    LATEST_MD.write_text(md, encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS RESEARCH DIRECTION CONTRACT BUILDER v2")
    print("=" * 100)
    print(f"builder_status: {builder_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("SELECTED DIRECTION")
    print("-" * 100)
    if top_direction:
        print(f"research_key: {top_direction.get('research_key')}")
        print(f"direction_id: {top_direction.get('direction_id')}")
        print(f"priority: {top_direction.get('priority')}")
        print(f"question: {top_direction.get('primary_question')}")
    else:
        print(None)
    print()
    print("CONTRACT")
    print("-" * 100)
    if contract:
        print(f"contract_id: {contract.get('contract_id')}")
        print(f"research_key: {contract.get('research_key')}")
        print(f"contract_hash: {contract.get('contract_hash')}")
        print(f"contract_latest_path: {CONTRACT_LATEST}")
        print(f"blocked_route_hashes: {safe_get(contract, ['lesson_memory_context', 'blocked_route_hashes'])}")
        print(f"strict_min_active_months: {safe_get(contract, ['strict_month_stability_policy', 'min_active_months'])}")
        print(f"strict_min_positive_months: {safe_get(contract, ['strict_month_stability_policy', 'min_positive_months'])}")
        print(f"candidate_generation_allowed_now: {safe_get(contract, ['required_scanner_behavior', 'candidate_generation_allowed_now'])}")
        print(f"family_release_allowed_now: {safe_get(contract, ['required_scanner_behavior', 'family_release_allowed_now'])}")
        print(f"next_module: {safe_get(contract, ['expected_next_module', 'module_name'])}")
    else:
        print(None)
    print()
    print("DECISION")
    print("-" * 100)
    print(json.dumps(result["decision"], indent=2, default=str))
    print()
    print("SAFETY")
    print("-" * 100)
    print("read_only: True")
    print("offline_only: True")
    print("mutate_runtime_allowed: False")
    print("launcher_allowed: False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print("family_disable_allowed: False")
    print("real_orders_allowed: False")
    print("execution_performed: False")
    print()
    print(f"latest_json: {LATEST_JSON}")
    print("=" * 100)

    return 0 if severity != "CRITICAL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
