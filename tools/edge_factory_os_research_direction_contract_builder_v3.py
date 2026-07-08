from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_research_direction_contract_builder_v3"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

QUEUE_V3_LATEST = (
    BASE_DIR
    / "edge_factory_os_new_research_direction_queue_v3"
    / "new_research_direction_queue_v3_latest.json"
)

STRICT_POLICY_LATEST = (
    BASE_DIR
    / "edge_factory_os_policy_guards"
    / "strict_month_stability_policy_latest.json"
)

CANONICAL_GUARD_LATEST = (
    BASE_DIR
    / "edge_factory_os_canonical_month_window_guard_v1"
    / "canonical_month_window_guard_latest.json"
)

ACTION_GUARD_LATEST = (
    BASE_DIR
    / "edge_factory_os_action_prerequisite_guard_v1"
    / "action_prerequisite_guard_latest.json"
)

UNIVERSE_GUARD_V2_LATEST = (
    BASE_DIR
    / "edge_factory_os_universe_coverage_guard_v2"
    / "universe_coverage_guard_v2_latest.json"
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

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"research_direction_contract_builder_v3_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "research_direction_contract_builder_v3_latest.json"
LATEST_MD = OUT_ROOT / "research_direction_contract_builder_v3_latest.md"

CONTRACT_ROOT = BASE_DIR / "edge_factory_os_research_direction_contracts"
CONTRACT_LATEST = CONTRACT_ROOT / "non_impulse_mean_reversion_archetype_contract_latest.json"


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


def all_auth_false(action_guard: Dict[str, Any]) -> bool:
    auth = action_guard.get("authorization")
    if not isinstance(auth, dict):
        return False
    return all(v is False for v in auth.values())


def extract_blocked_hashes(blocklist: Dict[str, Any]) -> List[str]:
    rows = blocklist.get("blocked_routes")
    if not isinstance(rows, list):
        return []

    out = []
    for row in rows:
        if isinstance(row, dict) and row.get("route_hash"):
            out.append(str(row["route_hash"]))
    return sorted(set(out))


def extract_lesson_ids(lesson_index: Dict[str, Any]) -> List[str]:
    rows = lesson_index.get("lessons")
    if not isinstance(rows, list):
        return []

    out = []
    for row in rows:
        if isinstance(row, dict) and row.get("lesson_id"):
            out.append(str(row["lesson_id"]))
    return sorted(set(out))


def select_direction(queue_v3: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    directions = queue_v3.get("directions")
    if not isinstance(directions, list):
        return None

    preferred = queue_v3.get("decision", {}).get("next_recommended_research_key")
    if preferred:
        for d in directions:
            if isinstance(d, dict) and d.get("research_key") == preferred:
                return d

    valid = [
        d for d in directions
        if isinstance(d, dict)
        and d.get("candidate_generation_allowed_now") is False
        and d.get("status") == "QUEUED_READ_ONLY_RESEARCH"
    ]
    valid.sort(key=lambda x: int(x.get("priority") or 0), reverse=True)
    return valid[0] if valid else None


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    CONTRACT_ROOT.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    queue_v3 = load_json(QUEUE_V3_LATEST)
    strict_policy = load_json(STRICT_POLICY_LATEST)
    canonical_guard = load_json(CANONICAL_GUARD_LATEST)
    action_guard = load_json(ACTION_GUARD_LATEST)
    universe = load_json(UNIVERSE_GUARD_V2_LATEST)
    blocklist = load_json(BLOCKLIST_PATH)
    lesson_index = load_json(LESSON_INDEX_PATH)

    if not isinstance(queue_v3, dict):
        critical.append("queue_v3_latest_missing")
        queue_v3 = {}

    if not isinstance(strict_policy, dict):
        critical.append("strict_policy_missing")
        strict_policy = {}

    if not isinstance(canonical_guard, dict):
        critical.append("canonical_guard_missing")
        canonical_guard = {}

    if not isinstance(action_guard, dict):
        critical.append("action_guard_missing")
        action_guard = {}

    if not isinstance(universe, dict):
        critical.append("universe_guard_v2_missing")
        universe = {}

    if not isinstance(blocklist, dict):
        critical.append("blocklist_missing")
        blocklist = {}

    if not isinstance(lesson_index, dict):
        attention.append("lesson_index_missing")
        lesson_index = {}

    if queue_v3.get("queue_status") != "NEW_RESEARCH_DIRECTIONS_V3_QUEUED_BRANCH_ROTATION":
        critical.append(f"unexpected_queue_status:{queue_v3.get('queue_status')}")

    if safe_get(queue_v3, ["release_gate_feed", "PRIOR_BRANCH_CLOSED"]) is not True:
        critical.append("prior_branch_not_closed")

    if strict_policy.get("policy_key") != "STRICT_MONTH_STABILITY_12_OF_12":
        critical.append(f"strict_policy_not_12_of_12:{strict_policy.get('policy_key')}")

    if canonical_guard.get("guard_status") != "CANONICAL_MONTH_WINDOW_GUARD_ACTIVE":
        critical.append(f"canonical_guard_not_active:{canonical_guard.get('guard_status')}")

    if safe_get(canonical_guard, ["month_window", "canonical_policy_month_count"]) != 12:
        critical.append("canonical_policy_month_count_not_12")

    if action_guard.get("guard_status") != "ACTION_PREREQUISITE_GUARD_ACTIVE_ACTIONS_BLOCKED":
        critical.append(f"action_guard_not_blocking:{action_guard.get('guard_status')}")

    if not all_auth_false(action_guard):
        critical.append("action_authorization_not_all_false")

    if universe.get("universe_status") != "UNIVERSE_COVERAGE_GUARD_V2_PASS_FULL_1Y_OKX_SWAP_PANEL_READY":
        critical.append(f"universe_guard_not_full_pass:{universe.get('universe_status')}")

    direction = select_direction(queue_v3)
    if not isinstance(direction, dict):
        critical.append("no_valid_research_direction_selected")
        direction = {}

    if direction.get("research_key") != "RD3_01_NON_IMPULSE_MEAN_REVERSION_ARCHETYPE_SEARCH":
        critical.append(f"unexpected_selected_research_key:{direction.get('research_key')}")

    blocked_hashes = extract_blocked_hashes(blocklist)
    lesson_ids = extract_lesson_ids(lesson_index)

    best_manifest = universe.get("best_universe_manifest") or {}
    panel_path = best_manifest.get("panel_path")

    if not panel_path or not Path(str(panel_path)).exists():
        critical.append(f"universe_panel_missing:{panel_path}")

    contract = None
    contract_written = False

    if critical:
        builder_status = "RESEARCH_DIRECTION_CONTRACT_BUILDER_V3_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_INPUTS_BEFORE_RD3_CONTRACT"
        reason = "; ".join(critical)

    else:
        contract_core = {
            "research_key": "NON_IMPULSE_MEAN_REVERSION_ARCHETYPE_SEARCH_V1",
            "direction_id": direction.get("direction_id"),
            "strict_policy_key": strict_policy.get("policy_key"),
            "canonical_months": safe_get(canonical_guard, ["month_window", "canonical_policy_months"]),
            "blocked_hashes": blocked_hashes,
            "panel_path": panel_path,
        }

        contract_hash = stable_hash(contract_core)
        contract_id = f"NON_IMPULSE_MEAN_REVERSION_ARCHETYPE_CONTRACT_V1_{contract_hash}_{NOW.strftime('%Y%m%d_%H%M%S')}"

        contract = {
            "contract_schema": "edge_factory_os_research_direction_contract_v3",
            "contract_id": contract_id,
            "contract_hash": contract_hash,
            "created_at_utc": NOW.isoformat(),

            "research_key": "NON_IMPULSE_MEAN_REVERSION_ARCHETYPE_SEARCH_V1",
            "contract_type": "READ_ONLY_ARCHETYPE_SEARCH_CONTRACT",

            "source_direction": direction,

            "purpose": (
                "Start a new branch after impulse continuation, repair, feature-conditioned, and broader month feature branches "
                "failed canonical strict 12/12. Search for non-impulse mean-reversion archetypes on the full 1Y OKX swap universe. "
                "This is read-only/offline research only and cannot create candidates, families, runtime patches, capital changes, "
                "active paper routes, live actions, or real orders."
            ),

            "why_new_branch": {
                "prior_branch_closed": True,
                "closed_branch_source": str(BASE_DIR / "edge_factory_os_broader_month_feature_engine_evaluator_v1" / "broader_month_feature_engine_evaluator_latest.json"),
                "do_not_repeat_prior_failures": [
                    "impulse continuation route",
                    "ret3 threshold route",
                    "symbol blacklist repair",
                    "strict month-stability repair route",
                    "month-first feature-conditioned repair",
                    "broader month feature repair branch",
                    "manual bad-month blacklist",
                    "13 raw calendar bucket pass logic",
                    "11/12 month stability",
                ],
            },

            "policy_context": {
                "strict_month_policy_key": strict_policy.get("policy_key"),
                "min_active_months": safe_get(strict_policy, ["release_requirement", "min_active_months"]),
                "min_positive_months": safe_get(strict_policy, ["release_requirement", "min_positive_months"]),
                "min_positive_month_rate": safe_get(strict_policy, ["release_requirement", "min_positive_month_rate"]),
                "canonical_guard_status": canonical_guard.get("guard_status"),
                "raw_calendar_month_count": safe_get(canonical_guard, ["month_window", "raw_calendar_month_count"]),
                "canonical_policy_month_count": safe_get(canonical_guard, ["month_window", "canonical_policy_month_count"]),
                "canonical_policy_months": safe_get(canonical_guard, ["month_window", "canonical_policy_months"]),
                "boundary_partial_months": safe_get(canonical_guard, ["month_window", "boundary_partial_months"]),
            },

            "universe_context": {
                "universe_status": universe.get("universe_status"),
                "panel_path": panel_path,
                "symbol_count": best_manifest.get("symbol_count"),
                "row_count": best_manifest.get("row_count"),
                "day_span": best_manifest.get("day_span"),
                "start": best_manifest.get("start_raw"),
                "end": best_manifest.get("end_raw"),
                "must_use_full_1y_okx_swap_panel": True,
            },

            "lesson_memory_context": {
                "blocked_route_hashes": blocked_hashes,
                "blocked_route_count": len(blocked_hashes),
                "lesson_ids": lesson_ids,
                "lesson_count": len(lesson_ids),
                "blocked_route_reuse_allowed": False,
            },

            "archetype_search_scope": {
                "archetype_family": "non_impulse_mean_reversion",
                "core_question": direction.get("primary_question"),
                "search_is_not_repair": True,
                "candidate_generation_allowed_now": False,
                "family_release_allowed_now": False,
                "runtime_change_allowed_now": False,
                "capital_change_allowed_now": False,
                "allowed_signal_families": [
                    "short_term_overextension_reversion",
                    "range_spike_reversion",
                    "drop_rebound_reversion",
                    "breadth_extreme_reversion",
                    "cross_sectional_loser_rebound",
                    "liquidity_shock_reversion_but_not_prior_failed_route",
                    "low_vol_mean_reversion",
                    "market_breadth_snapback",
                ],
                "explicitly_disallowed_signal_families": [
                    "impulse_long_continuation",
                    "ret3_threshold_hold_repair",
                    "manual_symbol_blacklist",
                    "manual_bad_month_blacklist",
                    "post_outcome_label_as_feature",
                    "single_symbol_overfit",
                    "paper_ledger_only_validation",
                ],
            },

            "required_runner_behavior": {
                "future_module": "edge_factory_os_non_impulse_mean_reversion_archetype_runner_v1.py",
                "diagnostic_or_research_only": True,
                "candidate_generation_allowed_now": False,
                "candidate_contract_allowed_now": False,
                "family_release_allowed_now": False,
                "promotion_allowed_now": False,
                "runtime_change_allowed_now": False,
                "capital_change_allowed_now": False,
                "must_consume_canonical_month_window_guard": True,
                "must_consume_strict_12_of_12_policy": True,
                "must_use_full_1y_okx_swap_panel": True,
                "must_output_archetype_scoreboard": True,
                "must_output_strict_12_of_12_preview": True,
                "must_output_overfit_warnings": True,
                "must_not_patch_runtime": True,
            },

            "required_validation_for_any_future_candidate": {
                "this_contract_cannot_create_candidate": True,
                "future_candidate_requires_separate_preflight": True,
                "policy_key_required": "STRICT_MONTH_STABILITY_12_OF_12",
                "canonical_policy_month_count_required": 12,
                "canonical_positive_month_count_required": 12,
                "canonical_negative_month_count_required": 0,
                "route_hash_not_in_blocklist": True,
                "full_universe_backtest_required": True,
                "train_oos_validation_required": True,
                "cost_slippage_sensitivity_required": True,
                "symbol_concentration_required": True,
                "regime_bucket_required": True,
                "risk_and_capital_safety_required": True,
                "manual_or_ai_review_non_override_required": True,
                "final_release_gate_required": True,
            },

            "expected_next_module": {
                "module_name": "edge_factory_os_non_impulse_mean_reversion_archetype_runner_v1.py",
                "purpose": (
                    "Search non-impulse mean-reversion archetype templates on full 1Y universe under canonical 12/12 policy. "
                    "Output research scoreboard only; no candidate/family/runtime/capital action."
                ),
                "execution_allowed_after_contract": True,
                "candidate_generation_allowed_after_contract": False,
                "candidate_contract_allowed_after_contract": False,
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

        contract_path = RUN_DIR / f"{contract_id}.json"
        dump_json(contract_path, contract)
        dump_json(CONTRACT_LATEST, contract)

        contract["contract_path"] = str(contract_path)
        contract["contract_latest_path"] = str(CONTRACT_LATEST)

        builder_status = "RESEARCH_DIRECTION_CONTRACT_V3_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_NON_IMPULSE_MEAN_REVERSION_ARCHETYPE_RUNNER"
        reason = (
            f"contract_id={contract_id}; "
            "research_key=NON_IMPULSE_MEAN_REVERSION_ARCHETYPE_SEARCH_V1"
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

        "selected_direction": direction,
        "contract": contract,
        "contract_written": contract_written,
        "contract_latest_path": str(CONTRACT_LATEST),

        "release_gate_feed": {
            "RESEARCH_DIRECTION_CONTRACT_V3_BUILT": contract_written,
            "RESEARCH_KEY": "NON_IMPULSE_MEAN_REVERSION_ARCHETYPE_SEARCH_V1" if contract_written else None,
            "CANONICAL_MONTH_WINDOW_REQUIRED": True,
            "STRICT_MONTH_STABILITY_POLICY_KEY": "STRICT_MONTH_STABILITY_12_OF_12" if contract_written else None,
            "CANDIDATE_GENERATION_ALLOWED": False,
            "CANDIDATE_CONTRACT_ALLOWED": False,
            "FAMILY_RELEASE_ALLOWED": False,
            "RUNTIME_CHANGE_ALLOWED": False,
            "CAPITAL_CHANGE_ALLOWED": False,
            "RELEASE_PASS_FROM_THIS_CONTRACT": False,
            "status": builder_status,
        },

        "decision": {
            "candidate_generation_recommended_now": False,
            "candidate_contract_recommended_now": False,
            "family_release_recommended": False,
            "promotion_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "active_paper_recommended": False,
            "live_or_real_order_recommended": False,
            "next_module": "edge_factory_os_non_impulse_mean_reversion_archetype_runner_v1.py" if contract_written else None,
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

    out_json = RUN_DIR / "research_direction_contract_builder_v3_state.json"
    out_md = RUN_DIR / "research_direction_contract_builder_v3_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS RESEARCH DIRECTION CONTRACT BUILDER v3

builder_status: {builder_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

contract_written: {contract_written}  
contract_latest_path: {CONTRACT_LATEST}

## Selected Direction

{json.dumps(direction, indent=2, default=str)}

## Contract Summary

contract_id: {contract.get("contract_id") if contract else None}  
research_key: {contract.get("research_key") if contract else None}  
contract_hash: {contract.get("contract_hash") if contract else None}  
canonical_policy_month_count: {safe_get(contract or {}, ["policy_context", "canonical_policy_month_count"])}  
strict_policy_key: {safe_get(contract or {}, ["policy_context", "strict_month_policy_key"])}  
candidate_generation_allowed_now: {safe_get(contract or {}, ["required_runner_behavior", "candidate_generation_allowed_now"])}  
candidate_contract_allowed_now: {safe_get(contract or {}, ["required_runner_behavior", "candidate_contract_allowed_now"])}  
family_release_allowed_now: {safe_get(contract or {}, ["required_runner_behavior", "family_release_allowed_now"])}  
next_module: {safe_get(contract or {}, ["expected_next_module", "module_name"])}

## Release Gate Feed

{json.dumps(result["release_gate_feed"], indent=2, default=str)}

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
    print("EDGE FACTORY OS RESEARCH DIRECTION CONTRACT BUILDER v3")
    print("=" * 100)
    print(f"builder_status: {builder_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("SELECTED DIRECTION")
    print("-" * 100)
    print(f"research_key: {direction.get('research_key')}")
    print(f"direction_id: {direction.get('direction_id')}")
    print(f"priority: {direction.get('priority')}")
    print(f"primary_question: {direction.get('primary_question')}")
    print()
    print("CONTRACT")
    print("-" * 100)
    if contract:
        print(f"contract_id: {contract.get('contract_id')}")
        print(f"research_key: {contract.get('research_key')}")
        print(f"contract_hash: {contract.get('contract_hash')}")
        print(f"contract_latest_path: {CONTRACT_LATEST}")
        print(f"canonical_policy_month_count: {safe_get(contract, ['policy_context', 'canonical_policy_month_count'])}")
        print(f"strict_policy_key: {safe_get(contract, ['policy_context', 'strict_month_policy_key'])}")
        print(f"candidate_generation_allowed_now: {safe_get(contract, ['required_runner_behavior', 'candidate_generation_allowed_now'])}")
        print(f"candidate_contract_allowed_now: {safe_get(contract, ['required_runner_behavior', 'candidate_contract_allowed_now'])}")
        print(f"family_release_allowed_now: {safe_get(contract, ['required_runner_behavior', 'family_release_allowed_now'])}")
        print(f"next_module: {safe_get(contract, ['expected_next_module', 'module_name'])}")
    else:
        print(None)
    print()
    print("RELEASE GATE FEED")
    print("-" * 100)
    print(result["release_gate_feed"])
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
