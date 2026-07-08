from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_regime_filtered_candidate_contract_builder_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

VOL_REGIME_EVAL_LATEST = (
    BASE_DIR
    / "edge_factory_os_volatility_range_regime_filter_evaluator_v1"
    / "volatility_range_regime_filter_evaluator_latest.json"
)

VOL_REGIME_DIAG_LATEST = (
    BASE_DIR
    / "edge_factory_os_volatility_range_regime_filter_diagnostic_v1"
    / "volatility_range_regime_filter_diagnostic_latest.json"
)

LESSON_CHECKER_LATEST = (
    BASE_DIR
    / "edge_factory_os_lesson_memory_checker_v1"
    / "lesson_memory_checker_latest.json"
)

RELEASE_GATE_V4_LATEST = (
    BASE_DIR
    / "edge_factory_os_family_candidate_release_gate_v4"
    / "family_candidate_release_gate_v4_latest.json"
)

UNIVERSE_GUARD_V2_LATEST = (
    BASE_DIR
    / "edge_factory_os_universe_coverage_guard_v2"
    / "universe_coverage_guard_v2_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"regime_filtered_candidate_contract_builder_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "regime_filtered_candidate_contract_builder_latest.json"
LATEST_MD = OUT_ROOT / "regime_filtered_candidate_contract_builder_latest.md"

CONTRACT_ROOT = BASE_DIR / "edge_factory_os_candidate_contracts"
CONTRACT_LATEST = CONTRACT_ROOT / "regime_filtered_impulse_candidate_contract_latest.json"


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


def build_route_signature(eval_state: Dict[str, Any], diag_state: Dict[str, Any]) -> Dict[str, Any]:
    strength = eval_state.get("strength_classification") or {}
    best = strength.get("best_interaction_metrics") or {}
    route_proxy = diag_state.get("route_proxy_used_for_diagnostic_only") or {}

    return {
        "family": "regime_filtered_impulse_long_research",
        "base_family": "impulse_long",
        "candidate_source": "volatility_range_liquidity_regime_filtered_impulse",
        "base_signal": {
            "threshold_coin_ret3_bps": route_proxy.get("threshold_coin_ret3_bps"),
            "hold_hours": route_proxy.get("hold_hours"),
            "entry_range_cap_bps": route_proxy.get("entry_range_cap_bps"),
            "mkt_filter": route_proxy.get("mkt_filter"),
            "cost_bps_total": route_proxy.get("cost_bps_total"),
        },
        "new_regime_filter": {
            "vol_high": False,
            "range_high": False,
            "liq_low": False,
            "interaction_regime": best.get("interaction_regime"),
            "std_coin_ret3_bps_max": 200,
            "mean_entry_range_bps_max": 200,
            "mean_entry_vol_quote_quantile_filter": "above_low_liquidity_cutoff",
        },
        "difference_from_blocked_route": [
            "adds pre-outcome cross-sectional volatility filter",
            "adds pre-outcome range stress filter",
            "adds pre-outcome liquidity stress filter",
            "requires new route hash and full validation",
        ],
    }


def build_contract(
    eval_state: Dict[str, Any],
    diag_state: Dict[str, Any],
    lesson_checker: Dict[str, Any],
    release_gate: Dict[str, Any],
    universe: Dict[str, Any],
) -> Dict[str, Any]:
    strength = eval_state.get("strength_classification") or {}
    recommendation = eval_state.get("new_candidate_contract_recommendation") or {}

    route_signature = build_route_signature(eval_state, diag_state)
    candidate_route_hash = stable_hash(route_signature)

    blocked_route_hash = lesson_checker.get("route_hash")
    best_manifest = universe.get("best_universe_manifest") or {}
    panel_path = best_manifest.get("panel_path")

    contract_id = f"REGIME_FILTERED_IMPULSE_ROUTE_CANDIDATE_CONTRACT_V1_{candidate_route_hash}_{NOW.strftime('%Y%m%d_%H%M%S')}"

    contract = {
        "contract_schema": "edge_factory_os_candidate_contract_v1",
        "contract_id": contract_id,
        "created_at_utc": NOW.isoformat(),

        "candidate_key": "REGIME_FILTERED_IMPULSE_ROUTE_CANDIDATE_V1",
        "candidate_route_hash": candidate_route_hash,
        "candidate_family_name": "regime_filtered_impulse_long_research",
        "base_family_reference": "impulse_long",
        "contract_type": "OFFLINE_CANDIDATE_CONTRACT_ONLY",

        "purpose": (
            "Define an offline-only candidate route using volatility/range/liquidity regime filters derived from diagnostic evidence. "
            "This contract does not approve runtime, active paper, live, capital, or family release."
        ),

        "source_evidence": {
            "volatility_range_evaluator_status": eval_state.get("evaluator_status"),
            "volatility_range_evaluator_reason": eval_state.get("reason"),
            "strength_classification": strength,
            "new_candidate_contract_recommendation": recommendation,
            "diagnostic_route_proxy": diag_state.get("route_proxy_used_for_diagnostic_only"),
            "release_gate_v4_status": release_gate.get("release_status"),
            "lesson_checker_status": lesson_checker.get("checker_status"),
        },

        "blocked_route_guard": {
            "known_failed_route_hash": blocked_route_hash,
            "candidate_route_hash": candidate_route_hash,
            "candidate_route_is_same_as_blocked_route": candidate_route_hash == blocked_route_hash,
            "blocked_route_reuse_allowed": False,
            "old_route_can_be_used_only_as_baseline": True,
            "must_reject_contract_if_hash_matches_blocked_route": True,
            "must_pass_lesson_memory_checker_for_new_hash": True,
        },

        "route_signature": route_signature,

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

        "candidate_definition": {
            "base_signal_rules": {
                "coin_ret3_bps_min": safe_get(route_signature, ["base_signal", "threshold_coin_ret3_bps"]),
                "hold_hours": safe_get(route_signature, ["base_signal", "hold_hours"]),
                "entry_range_cap_bps": safe_get(route_signature, ["base_signal", "entry_range_cap_bps"]),
                "market_filter": safe_get(route_signature, ["base_signal", "mkt_filter"]),
                "cost_bps_total": safe_get(route_signature, ["base_signal", "cost_bps_total"]),
            },
            "new_regime_filter_rules": {
                "std_coin_ret3_bps_max": 200,
                "mean_entry_range_bps_max": 200,
                "liquidity_filter": "mean_entry_vol_quote > low_liquidity_cutoff",
                "interaction_regime_target": "vol_high=False|range_high=False|liq_low=False",
                "all_filters_must_be_known_before_trade_outcome": True,
            },
            "explicitly_not_allowed": [
                "manual symbol blacklist",
                "single-symbol filter",
                "paper-sample-only rule",
                "AI/manual release override",
                "runtime patch from this contract alone",
                "capital change from this contract alone",
            ],
        },

        "required_validation_plan": {
            "step_1_lesson_memory_new_route_hash_check": {
                "required": True,
                "pass_condition": "candidate_route_hash is not in known failure blocklist",
            },
            "step_2_full_universe_offline_backtest": {
                "required": True,
                "minimum_all_trades": 300,
                "minimum_oos_trades": 75,
                "minimum_all_mean_net_bps": 0,
                "minimum_train_mean_net_bps": 0,
                "minimum_oos_mean_net_bps": 0,
                "minimum_train_profit_factor": 1.10,
                "minimum_oos_profit_factor": 1.10,
                "minimum_oos_win_rate": 0.45,
            },
            "step_3_month_stability": {
                "required": True,
                "minimum_all_positive_month_rate": 0.55,
                "minimum_oos_positive_month_rate": 0.50,
                "must_not_depend_on_one_good_month": True,
            },
            "step_4_cost_sensitivity": {
                "required": True,
                "must_survive_current_cost": True,
                "must_not_only_work_fee_only": True,
                "stress_cost_review_required": True,
            },
            "step_5_symbol_concentration": {
                "required": True,
                "manual_symbol_blacklist_not_allowed": True,
                "single_symbol_dependency_not_allowed": True,
            },
            "step_6_release_gate": {
                "required": True,
                "must_pass_future_release_gate": True,
                "manual_or_ai_review_cannot_override_failed_tests": True,
            },
        },

        "execution_policy": {
            "contract_creation_execution_performed": False,
            "candidate_backtest_execution_allowed_by_this_contract": False,
            "future_backtest_runner_required": "edge_factory_os_regime_filtered_candidate_backtest_runner_v1.py",
            "future_evaluator_required": "edge_factory_os_regime_filtered_candidate_evaluator_v1.py",
            "candidate_generation_allowed_now": False,
            "family_release_allowed_now": False,
            "promotion_allowed_now": False,
            "runtime_change_allowed_now": False,
            "capital_change_allowed_now": False,
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

    eval_state = load_json(VOL_REGIME_EVAL_LATEST)
    diag_state = load_json(VOL_REGIME_DIAG_LATEST)
    lesson_checker = load_json(LESSON_CHECKER_LATEST)
    release_gate = load_json(RELEASE_GATE_V4_LATEST)
    universe = load_json(UNIVERSE_GUARD_V2_LATEST)

    if not isinstance(eval_state, dict):
        critical.append("volatility_range_regime_evaluator_latest_missing")
        eval_state = {}

    if not isinstance(diag_state, dict):
        critical.append("volatility_range_regime_diagnostic_latest_missing")
        diag_state = {}

    if not isinstance(lesson_checker, dict):
        critical.append("lesson_checker_latest_missing")
        lesson_checker = {}

    if not isinstance(release_gate, dict):
        attention.append("release_gate_v4_latest_missing")
        release_gate = {}

    if not isinstance(universe, dict):
        critical.append("universe_guard_v2_latest_missing")
        universe = {}

    if eval_state.get("evaluator_status") != "VOLATILITY_RANGE_REGIME_EVALUATOR_NEW_CANDIDATE_CONTRACT_RECOMMENDED":
        critical.append(f"evaluator_not_recommending_candidate_contract:{eval_state.get('evaluator_status')}")

    rec = eval_state.get("new_candidate_contract_recommendation") or {}
    if rec.get("new_candidate_contract_recommended") is not True:
        critical.append("new_candidate_contract_not_recommended")

    if rec.get("candidate_generation_allowed_now") is not False:
        critical.append("evaluator_allows_candidate_generation_now_unexpectedly")

    if rec.get("family_release_allowed_now") is not False:
        critical.append("evaluator_allows_family_release_now_unexpectedly")

    if diag_state.get("diagnostic_status") != "VOLATILITY_RANGE_REGIME_FILTER_DIAGNOSTIC_COMPLETE":
        critical.append(f"diagnostic_not_complete:{diag_state.get('diagnostic_status')}")

    if lesson_checker.get("route_blocked_by_lesson_memory") is not True:
        critical.append("known_failed_route_not_blocked_by_lesson_memory")

    if universe.get("universe_status") != "UNIVERSE_COVERAGE_GUARD_V2_PASS_FULL_1Y_OKX_SWAP_PANEL_READY":
        critical.append(f"universe_not_full_pass:{universe.get('universe_status')}")

    contract = None
    contract_written = False

    if critical:
        builder_status = "REGIME_FILTERED_CANDIDATE_CONTRACT_BUILDER_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_INPUTS_BEFORE_CONTRACT"
        reason = "; ".join(critical)

    else:
        contract = build_contract(eval_state, diag_state, lesson_checker, release_gate, universe)

        if safe_get(contract, ["blocked_route_guard", "candidate_route_is_same_as_blocked_route"]) is True:
            critical.append("candidate_route_hash_matches_known_failed_route")
            builder_status = "REGIME_FILTERED_CANDIDATE_CONTRACT_BUILDER_CRITICAL_BLOCKED"
            severity = "CRITICAL"
            allowed_scope = "READ_ONLY_REVIEW"
            next_action = "REDESIGN_ROUTE_SIGNATURE"
            reason = "; ".join(critical)
            contract_written = False
        else:
            contract_path = RUN_DIR / f"{contract['contract_id']}.json"
            dump_json(contract_path, contract)
            dump_json(CONTRACT_LATEST, contract)

            contract["contract_path"] = str(contract_path)
            contract["contract_latest_path"] = str(CONTRACT_LATEST)

            builder_status = "REGIME_FILTERED_CANDIDATE_CONTRACT_READY"
            severity = "ATTENTION"
            allowed_scope = "READ_ONLY_RESEARCH"
            next_action = "RUN_LESSON_MEMORY_CHECK_FOR_NEW_CANDIDATE_ROUTE_HASH"
            reason = (
                f"contract_id={contract['contract_id']}; "
                f"candidate_route_hash={contract['candidate_route_hash']}; "
                f"known_failed_route_hash={safe_get(contract, ['blocked_route_guard', 'known_failed_route_hash'])}"
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

        "contract": contract,
        "contract_written": contract_written,
        "contract_latest_path": str(CONTRACT_LATEST),

        "sources": {
            "volatility_range_regime_evaluator": str(VOL_REGIME_EVAL_LATEST),
            "volatility_range_regime_diagnostic": str(VOL_REGIME_DIAG_LATEST),
            "lesson_checker": str(LESSON_CHECKER_LATEST),
            "release_gate_v4": str(RELEASE_GATE_V4_LATEST),
            "universe_guard_v2": str(UNIVERSE_GUARD_V2_LATEST),
        },

        "decision": {
            "candidate_contract_ready": bool(contract_written),
            "candidate_generation_recommended_now": False,
            "candidate_backtest_recommended_next": bool(contract_written),
            "family_release_recommended": False,
            "promotion_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "repeat_same_route_recommended": False,
            "next_module": "edge_factory_os_candidate_route_lesson_memory_checker_v1.py" if contract_written else None,
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

    out_json = RUN_DIR / "regime_filtered_candidate_contract_builder_v1_state.json"
    out_md = RUN_DIR / "regime_filtered_candidate_contract_builder_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS REGIME FILTERED CANDIDATE CONTRACT BUILDER v1

builder_status: {builder_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

contract_written: {contract_written}  
contract_latest_path: {CONTRACT_LATEST}

## Contract Summary

contract_id: {contract.get("contract_id") if contract else None}  
candidate_key: {contract.get("candidate_key") if contract else None}  
candidate_route_hash: {contract.get("candidate_route_hash") if contract else None}  
known_failed_route_hash: {safe_get(contract or {}, ["blocked_route_guard", "known_failed_route_hash"])}  
candidate_route_is_same_as_blocked_route: {safe_get(contract or {}, ["blocked_route_guard", "candidate_route_is_same_as_blocked_route"])}  
candidate_generation_allowed_now: {safe_get(contract or {}, ["execution_policy", "candidate_generation_allowed_now"])}  
family_release_allowed_now: {safe_get(contract or {}, ["execution_policy", "family_release_allowed_now"])}  
runtime_change_allowed_now: {safe_get(contract or {}, ["execution_policy", "runtime_change_allowed_now"])}  
future_backtest_runner_required: {safe_get(contract or {}, ["execution_policy", "future_backtest_runner_required"])}

## Route Signature

{json.dumps(contract.get("route_signature") if contract else None, indent=2, default=str)}

## Required Validation Plan

{json.dumps(contract.get("required_validation_plan") if contract else None, indent=2, default=str)}

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
    print("EDGE FACTORY OS REGIME FILTERED CANDIDATE CONTRACT BUILDER v1")
    print("=" * 100)
    print(f"builder_status: {builder_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("CONTRACT")
    print("-" * 100)
    if contract:
        print(f"contract_id: {contract.get('contract_id')}")
        print(f"candidate_key: {contract.get('candidate_key')}")
        print(f"candidate_route_hash: {contract.get('candidate_route_hash')}")
        print(f"known_failed_route_hash: {safe_get(contract, ['blocked_route_guard', 'known_failed_route_hash'])}")
        print(f"candidate_route_is_same_as_blocked_route: {safe_get(contract, ['blocked_route_guard', 'candidate_route_is_same_as_blocked_route'])}")
        print(f"candidate_generation_allowed_now: {safe_get(contract, ['execution_policy', 'candidate_generation_allowed_now'])}")
        print(f"family_release_allowed_now: {safe_get(contract, ['execution_policy', 'family_release_allowed_now'])}")
        print(f"runtime_change_allowed_now: {safe_get(contract, ['execution_policy', 'runtime_change_allowed_now'])}")
        print(f"future_backtest_runner_required: {safe_get(contract, ['execution_policy', 'future_backtest_runner_required'])}")
        print(f"contract_latest_path: {CONTRACT_LATEST}")
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
