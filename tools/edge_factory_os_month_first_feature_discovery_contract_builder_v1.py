from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_month_first_feature_discovery_contract_builder_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

ARCHETYPE_EVAL_LATEST = (
    BASE_DIR
    / "edge_factory_os_strict_month_stable_archetype_evaluator_v1"
    / "strict_month_stable_archetype_evaluator_latest.json"
)

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
RUN_DIR = OUT_ROOT / f"month_first_feature_discovery_contract_builder_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "month_first_feature_discovery_contract_builder_latest.json"
LATEST_MD = OUT_ROOT / "month_first_feature_discovery_contract_builder_latest.md"

CONTRACT_ROOT = BASE_DIR / "edge_factory_os_research_direction_contracts"
CONTRACT_LATEST = CONTRACT_ROOT / "month_first_feature_discovery_contract_latest.json"


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


def find_direction(queue_state: Dict[str, Any], key: str) -> Optional[Dict[str, Any]]:
    directions = queue_state.get("directions")
    if not isinstance(directions, list):
        return None

    for d in directions:
        if isinstance(d, dict) and d.get("research_key") == key:
            return d

    return None


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
    archetype_eval: Dict[str, Any],
    direction: Dict[str, Any],
    strict_policy: Dict[str, Any],
    blocklist: Dict[str, Any],
    lesson_index: Dict[str, Any],
    universe: Dict[str, Any],
) -> Dict[str, Any]:
    blocked_hashes = extract_blocked_hashes(blocklist)
    lessons = lesson_index.get("lessons") if isinstance(lesson_index.get("lessons"), list) else []
    lesson_ids = [x.get("lesson_id") for x in lessons if isinstance(x, dict) and x.get("lesson_id")]

    best_manifest = universe.get("best_universe_manifest") or {}
    panel_path = best_manifest.get("panel_path")

    release_req = strict_policy.get("release_requirement") or {
        "min_active_months": 12,
        "min_positive_months": 11,
        "min_positive_month_rate": 11 / 12,
    }

    contract_core = {
        "research_key": "MONTH_FIRST_FEATURE_DISCOVERY_V1",
        "direction_id": direction.get("direction_id"),
        "blocked_hashes": blocked_hashes,
        "strict_policy": release_req,
        "scanner_v1_status": archetype_eval.get("evaluator_status"),
    }

    contract_hash = stable_hash(contract_core)
    contract_id = f"MONTH_FIRST_FEATURE_DISCOVERY_CONTRACT_V1_{contract_hash}_{NOW.strftime('%Y%m%d_%H%M%S')}"

    contract = {
        "contract_schema": "edge_factory_os_research_direction_contract_v2",
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "created_at_utc": NOW.isoformat(),

        "research_key": "MONTH_FIRST_FEATURE_DISCOVERY_V1",
        "contract_type": "DIAGNOSTIC_ONLY_FEATURE_DISCOVERY",

        "source_direction": {
            "direction_id": direction.get("direction_id"),
            "research_key": direction.get("research_key"),
            "priority": direction.get("priority"),
            "primary_question": direction.get("primary_question"),
            "hypothesis": direction.get("hypothesis"),
            "family_scope": direction.get("family_scope"),
        },

        "source_failure_context": {
            "archetype_evaluator_status": archetype_eval.get("evaluator_status"),
            "archetype_evaluator_reason": archetype_eval.get("reason"),
            "scanner_summary": archetype_eval.get("scanner_summary"),
            "top_failure_summary": archetype_eval.get("top_failure_summary"),
            "scanner_v1_archive_recommended": safe_get(archetype_eval, ["decision", "scanner_v1_archive_recommended"]),
        },

        "purpose": (
            "Discover pre-outcome month-level features that explain or predict strict month stability before constructing "
            "any new candidate. This contract exists because route-first searching failed: blocked impulse routes failed, "
            "repair filters failed strict 11-of-12 stability, and scanner v1 found no strict month-stable archetype."
        ),

        "lesson_memory_context": {
            "blocked_route_hashes": blocked_hashes,
            "known_lesson_ids": lesson_ids,
            "blocked_route_reuse_allowed": False,
            "must_not_repeat": [
                "90466e4144914fbc full-universe failure route",
                "85f9e6a4accb14c7 strict month-stability failure route",
                "strict scanner v1 failed templates as direct release candidates",
                "positive_month_rate >= 0.55 as release standard",
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
            "must_be_feature_discovery_target": True,
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

        "feature_discovery_scope": {
            "goal": (
                "Build a month-level feature table from full panel data and identify pre-outcome feature regimes "
                "associated with stable months, unstable months, positive-month count, and drawdown-like month clusters."
            ),
            "unit_of_analysis": [
                "month",
                "timestamp aggregate",
                "symbol cluster aggregate",
                "market breadth regime",
                "liquidity/range/volatility regime",
            ],
            "allowed_feature_groups": [
                "cross_sectional_return_dispersion",
                "market_breadth_positive_negative_share",
                "market_return_context",
                "liquidity_regime",
                "range_stress_regime",
                "impulse_density",
                "drop_density",
                "symbol_count_and_universe_health",
                "volatility_compression_expansion",
                "month_calendar_context_only_as_diagnostic_not_manual_blacklist",
            ],
            "explicitly_disallowed_features": [
                "future PnL",
                "future return outcome",
                "manual bad-month label used directly as live feature",
                "manual symbol blacklist",
                "known bad month blacklist",
                "post-trade information unavailable at entry time",
            ],
        },

        "required_outputs": {
            "month_feature_table": True,
            "feature_correlation_or_rank_table": True,
            "good_vs_bad_month_feature_differences": True,
            "strict_policy_feasibility_report": True,
            "recommended_feature_families_for_next_contract": True,
            "overfit_warnings": True,
            "release_gate_feed": True,
        },

        "pass_fail_policy": {
            "feature_discovery_pass_if": [
                "full panel loads",
                "month-level feature table is produced",
                "features are pre-outcome only",
                "strict 11-of-12 policy remains active",
                "no candidate/family/runtime/capital action is recommended",
                "next research contract recommendation is explicit",
            ],
            "feature_discovery_fail_if": [
                "uses future PnL as input feature",
                "uses manual bad-month blacklist",
                "uses manual symbol blacklist",
                "recommends release or runtime action",
                "ignores strict 12-active / 11-positive month policy",
            ],
            "release_pass_possible_in_this_module": False,
        },

        "expected_next_module": {
            "module_name": "edge_factory_os_month_first_feature_discovery_runner_v1.py",
            "purpose": (
                "Create full-panel month-level feature table and rank pre-outcome feature regimes that may explain "
                "strict month stability before candidate construction."
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

    archetype_eval = load_json(ARCHETYPE_EVAL_LATEST)
    queue_state = load_json(QUEUE_V2_LATEST)
    strict_policy = load_json(STRICT_POLICY_LATEST)
    blocklist = load_json(BLOCKLIST_PATH)
    lesson_index = load_json(LESSON_INDEX_PATH)
    universe = load_json(UNIVERSE_GUARD_V2_LATEST)

    if not isinstance(archetype_eval, dict):
        critical.append("strict_month_stable_archetype_evaluator_latest_missing")
        archetype_eval = {}

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

    if archetype_eval.get("evaluator_status") != "STRICT_MONTH_STABLE_ARCHETYPE_EVALUATOR_NO_STRICT_ARCHETYPE_FOUND":
        critical.append(f"unexpected_archetype_evaluator_status:{archetype_eval.get('evaluator_status')}")

    if safe_get(archetype_eval, ["decision", "scanner_v1_archive_recommended"]) is not True:
        critical.append("scanner_v1_archive_not_recommended")

    if safe_get(archetype_eval, ["decision", "next_recommended_research_key"]) != "RD2_02_MONTH_FIRST_FEATURE_DISCOVERY":
        critical.append(f"unexpected_next_research_key:{safe_get(archetype_eval, ['decision', 'next_recommended_research_key'])}")

    if strict_policy.get("policy_key") != "STRICT_MONTH_STABILITY_11_OF_12":
        critical.append(f"strict_policy_not_active:{strict_policy.get('policy_key')}")

    if universe.get("universe_status") != "UNIVERSE_COVERAGE_GUARD_V2_PASS_FULL_1Y_OKX_SWAP_PANEL_READY":
        critical.append(f"universe_not_full_pass:{universe.get('universe_status')}")

    direction = find_direction(queue_state, "RD2_02_MONTH_FIRST_FEATURE_DISCOVERY")
    if not isinstance(direction, dict):
        critical.append("rd2_02_month_first_feature_discovery_direction_missing")

    blocked_hashes = extract_blocked_hashes(blocklist)
    for h in ["90466e4144914fbc", "85f9e6a4accb14c7"]:
        if h not in blocked_hashes:
            attention.append(f"expected_blocked_hash_missing:{h}")

    contract = None
    contract_written = False

    if critical:
        builder_status = "MONTH_FIRST_FEATURE_DISCOVERY_CONTRACT_BUILDER_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_INPUTS_BEFORE_CONTRACT"
        reason = "; ".join(critical)

    else:
        contract = build_contract(archetype_eval, direction, strict_policy, blocklist, lesson_index, universe)

        contract_path = RUN_DIR / f"{contract['contract_id']}.json"
        dump_json(contract_path, contract)
        dump_json(CONTRACT_LATEST, contract)

        contract["contract_path"] = str(contract_path)
        contract["contract_latest_path"] = str(CONTRACT_LATEST)

        builder_status = "MONTH_FIRST_FEATURE_DISCOVERY_CONTRACT_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_MONTH_FIRST_FEATURE_DISCOVERY_RUNNER"
        reason = (
            f"contract_id={contract['contract_id']}; "
            f"research_key={contract['research_key']}; "
            "candidate_generation_allowed=False"
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

        "sources": {
            "archetype_evaluator": str(ARCHETYPE_EVAL_LATEST),
            "queue_v2": str(QUEUE_V2_LATEST),
            "strict_policy": str(STRICT_POLICY_LATEST),
            "blocklist": str(BLOCKLIST_PATH),
            "lesson_index": str(LESSON_INDEX_PATH),
            "universe_guard_v2": str(UNIVERSE_GUARD_V2_LATEST),
        },

        "decision": {
            "selected_research_key": "RD2_02_MONTH_FIRST_FEATURE_DISCOVERY" if contract_written else None,
            "contract_key": contract.get("research_key") if contract else None,
            "candidate_generation_recommended_now": False,
            "candidate_contract_recommended_now": False,
            "family_release_recommended": False,
            "promotion_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "repeat_blocked_routes_recommended": False,
            "next_module": "edge_factory_os_month_first_feature_discovery_runner_v1.py" if contract_written else None,
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

    out_json = RUN_DIR / "month_first_feature_discovery_contract_builder_v1_state.json"
    out_md = RUN_DIR / "month_first_feature_discovery_contract_builder_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS MONTH FIRST FEATURE DISCOVERY CONTRACT BUILDER v1

builder_status: {builder_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

contract_written: {contract_written}  
contract_latest_path: {CONTRACT_LATEST}

## Selected Direction

{json.dumps(direction, indent=2, default=str)[:12000]}

## Contract Summary

contract_id: {contract.get("contract_id") if contract else None}  
research_key: {contract.get("research_key") if contract else None}  
contract_hash: {contract.get("contract_hash") if contract else None}  
blocked_route_hashes: {safe_get(contract or {}, ["lesson_memory_context", "blocked_route_hashes"])}  
strict_min_active_months: {safe_get(contract or {}, ["strict_month_stability_policy", "min_active_months"])}  
strict_min_positive_months: {safe_get(contract or {}, ["strict_month_stability_policy", "min_positive_months"])}  
candidate_generation_allowed_after_contract: {safe_get(contract or {}, ["expected_next_module", "candidate_generation_allowed_after_contract"])}  
family_release_allowed_after_contract: {safe_get(contract or {}, ["expected_next_module", "family_release_allowed_after_contract"])}  
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
    print("EDGE FACTORY OS MONTH FIRST FEATURE DISCOVERY CONTRACT BUILDER v1")
    print("=" * 100)
    print(f"builder_status: {builder_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("SELECTED DIRECTION")
    print("-" * 100)
    if direction:
        print(f"research_key: {direction.get('research_key')}")
        print(f"direction_id: {direction.get('direction_id')}")
        print(f"priority: {direction.get('priority')}")
        print(f"primary_question: {direction.get('primary_question')}")
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
        print(f"candidate_generation_allowed_after_contract: {safe_get(contract, ['expected_next_module', 'candidate_generation_allowed_after_contract'])}")
        print(f"family_release_allowed_after_contract: {safe_get(contract, ['expected_next_module', 'family_release_allowed_after_contract'])}")
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
