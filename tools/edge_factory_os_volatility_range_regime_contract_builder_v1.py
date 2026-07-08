from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_volatility_range_regime_contract_builder_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

MONTH_REGIME_EVAL_LATEST = (
    BASE_DIR
    / "edge_factory_os_month_regime_instability_evaluator_v1"
    / "month_regime_instability_evaluator_latest.json"
)

MONTH_REGIME_DIAG_LATEST = (
    BASE_DIR
    / "edge_factory_os_month_regime_instability_diagnostic_v1"
    / "month_regime_instability_diagnostic_latest.json"
)

UNIVERSE_GUARD_V2_LATEST = (
    BASE_DIR
    / "edge_factory_os_universe_coverage_guard_v2"
    / "universe_coverage_guard_v2_latest.json"
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

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"volatility_range_regime_contract_builder_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "volatility_range_regime_contract_builder_latest.json"
LATEST_MD = OUT_ROOT / "volatility_range_regime_contract_builder_latest.md"

CONTRACT_ROOT = BASE_DIR / "edge_factory_os_research_direction_contracts"
CONTRACT_LATEST = CONTRACT_ROOT / "volatility_range_regime_filter_contract_latest.json"


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


def safe_get(d: Dict[str, Any], path: List[str], default=None):
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def build_contract(
    evaluator: Dict[str, Any],
    diagnostic: Dict[str, Any],
    universe: Dict[str, Any],
    lesson_checker: Dict[str, Any],
    release_gate: Dict[str, Any],
) -> Dict[str, Any]:
    top_bucket = evaluator.get("top_explanatory_bucket") or {}
    bucket_class = evaluator.get("top_bucket_classification") or {}
    top_feature_diff = evaluator.get("top_feature_difference") or {}

    best_manifest = universe.get("best_universe_manifest") or {}
    panel_path = best_manifest.get("panel_path")

    blocked_route = diagnostic.get("blocked_route_reference") or {}

    contract_id = f"VOLATILITY_RANGE_REGIME_FILTER_DIAGNOSTIC_V1_CONTRACT_{NOW.strftime('%Y%m%d_%H%M%S')}"

    contract = {
        "contract_schema": "edge_factory_os_research_contract_v1",
        "contract_id": contract_id,
        "created_at_utc": NOW.isoformat(),

        "research_key": "VOLATILITY_RANGE_REGIME_FILTER_DIAGNOSTIC_V1",
        "research_type": "DIAGNOSTIC_ONLY_NOT_CANDIDATE_RELEASE",
        "priority": 100,

        "purpose": (
            "Test whether cross-sectional volatility, range, and liquidity regime features explain or avoid "
            "the bad months found in the blocked impulse route, without reopening the blocked ret3 threshold route."
        ),

        "source_evidence": {
            "month_regime_evaluator_status": evaluator.get("evaluator_status"),
            "month_regime_evaluator_reason": evaluator.get("reason"),
            "top_explanatory_bucket": top_bucket,
            "top_bucket_classification": bucket_class,
            "top_feature_difference": top_feature_diff,
            "month_summary_compact": evaluator.get("month_summary_compact"),
            "release_gate_v4_status": release_gate.get("release_status"),
            "lesson_checker_status": lesson_checker.get("checker_status"),
        },

        "blocked_route_guard": {
            "blocked_route_hash": blocked_route.get("route_hash") or lesson_checker.get("route_hash"),
            "route_blocked_by_lesson_memory": blocked_route.get("route_blocked_by_lesson_memory"),
            "repeat_same_route_allowed": False,
            "candidate_generation_from_blocked_route_allowed": False,
            "blocked_route_may_be_used_only_as": [
                "diagnostic baseline",
                "failure comparison target",
                "feature/regime explanation target",
            ],
            "explicitly_disallowed": [
                "releasing blocked ret3 threshold route",
                "patching runtime with volatility/range filter directly",
                "using avg_std_coin_ret3_bps>=200 as a live filter without a separate full release gate",
                "manual symbol blacklist",
                "paper-ledger-only validation",
                "AI/manual override of failed full-universe gate",
            ],
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

        "diagnostic_questions": [
            {
                "question_id": "Q1_HIGH_CROSS_SECTIONAL_VOLATILITY_BAD_REGIME",
                "question": "Does avg_std_coin_ret3_bps >= 200 consistently identify bad months or bad route windows?",
                "seed_evidence": top_bucket,
                "required_output": [
                    "monthly_hi_low_table",
                    "trade_count_by_bucket",
                    "total_net_bps_by_bucket",
                    "positive_month_rate_by_bucket",
                    "train_oos_bucket_stability_preview",
                ],
            },
            {
                "question_id": "Q2_HIGH_ENTRY_RANGE_BAD_REGIME",
                "question": "Does avg_entry_range_bps >= 200 or related range stress explain bad months?",
                "seed_evidence": "avg_entry_range_bps >= 200 was a secondary bad bucket in RD1 diagnostic.",
                "required_output": [
                    "entry_range_bucket_table",
                    "range_threshold_sensitivity",
                    "month_stability_by_range_bucket",
                ],
            },
            {
                "question_id": "Q3_LIQUIDITY_GOOD_MONTH_SEPARATION",
                "question": "Do higher avg/median entry_vol_quote regimes separate good months from bad months?",
                "seed_evidence": top_feature_diff,
                "required_output": [
                    "liquidity_bucket_table",
                    "good_vs_bad_liquidity_stats",
                    "liquidity_x_volatility_interaction",
                ],
            },
            {
                "question_id": "Q4_INTERACTION_FILTER_DIAGNOSTIC",
                "question": "Are bad months explained better by volatility/range/liquidity interaction than by any single feature?",
                "required_output": [
                    "volatility_range_liquidity_grid",
                    "interaction_month_stability_table",
                    "symbol_concentration_check_by_interaction_bucket",
                ],
            },
            {
                "question_id": "Q5_NEXT_DECISION",
                "question": "Should the result become a new candidate contract, another diagnostic, or an archive lesson?",
                "required_output": [
                    "new_candidate_contract_allowed",
                    "why_or_why_not",
                    "required_release_gate_tests",
                    "lesson_memory_route_hash_preview",
                ],
            },
        ],

        "allowed_feature_space": {
            "features_allowed": [
                "avg_std_coin_ret3_bps",
                "avg_entry_range_bps",
                "median_entry_range_bps",
                "avg_entry_vol_quote",
                "median_entry_vol_quote",
                "avg_mean_coin_ret3_bps",
                "avg_median_coin_ret3_bps",
                "avg_mean_coin_ret6_bps",
                "avg_median_coin_ret6_bps",
                "avg_breadth_ret3_pos",
                "avg_breadth_ret6_pos",
                "avg_impulse_250_share",
                "avg_impulse_350_share",
                "avg_large_range_share",
                "constructed_volatility_regime_label",
                "constructed_range_regime_label",
                "constructed_liquidity_regime_label",
                "constructed_interaction_regime_label",
            ],
            "features_disallowed_as_standalone_release": [
                "raw ret3 threshold alone",
                "fixed hold-hour selection alone",
                "entry_range cap alone",
                "manual symbol blacklist",
                "single winning symbol filter",
                "same blocked route hash",
            ],
            "must_be_known_before_outcome": True,
        },

        "experiment_design": {
            "diagnostic_only": True,
            "candidate_generation_allowed_now": False,
            "family_release_allowed_now": False,
            "promotion_allowed_now": False,
            "route_proxy_allowed_for_comparison_only": True,
            "minimum_months_required": 12,
            "minimum_route_trades_for_diagnostic": 300,
            "seed_thresholds": {
                "avg_std_coin_ret3_bps": [150, 175, 200, 225, 250],
                "avg_entry_range_bps": [150, 175, 200, 225, 250],
                "avg_large_range_share": [0.10, 0.15, 0.20, 0.25],
                "avg_entry_vol_quote_quantiles": [0.25, 0.50, 0.75],
            },
            "required_tables": [
                "monthly_bucket_table",
                "feature_threshold_sensitivity_table",
                "interaction_grid_table",
                "good_bad_month_feature_table",
                "candidate_contract_preview_table",
            ],
        },

        "pass_fail_policy": {
            "diagnostic_pass_if": [
                "full panel loads",
                "volatility/range/liquidity bucket diagnostics are produced",
                "blocked route is not recommended for release",
                "new evidence is classified as diagnostic/explanatory only",
                "next decision is explicit: new candidate contract, more diagnostic, or archive",
            ],
            "diagnostic_fail_if": [
                "panel missing",
                "blocked route is reopened as a candidate",
                "module recommends runtime/capital/live/family action",
                "module treats explanatory bucket as release pass",
            ],
            "release_pass_possible_in_this_module": False,
        },

        "expected_next_module": {
            "module_name": "edge_factory_os_volatility_range_regime_filter_diagnostic_v1.py",
            "purpose": "Run diagnostic-only volatility/range/liquidity regime analysis on the full panel.",
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

    evaluator = load_json(MONTH_REGIME_EVAL_LATEST)
    diagnostic = load_json(MONTH_REGIME_DIAG_LATEST)
    universe = load_json(UNIVERSE_GUARD_V2_LATEST)
    lesson_checker = load_json(LESSON_CHECKER_LATEST)
    release_gate = load_json(RELEASE_GATE_V4_LATEST)

    if not isinstance(evaluator, dict):
        critical.append("month_regime_evaluator_latest_missing")
        evaluator = {}

    if not isinstance(diagnostic, dict):
        critical.append("month_regime_diagnostic_latest_missing")
        diagnostic = {}

    if not isinstance(universe, dict):
        critical.append("universe_guard_v2_latest_missing")
        universe = {}

    if not isinstance(lesson_checker, dict):
        critical.append("lesson_checker_latest_missing")
        lesson_checker = {}

    if not isinstance(release_gate, dict):
        attention.append("release_gate_v4_latest_missing")
        release_gate = {}

    if evaluator.get("evaluator_status") != "MONTH_REGIME_INSTABILITY_EVALUATOR_NEW_CONTRACT_RECOMMENDED":
        critical.append(f"evaluator_not_new_contract_recommended:{evaluator.get('evaluator_status')}")

    rec = evaluator.get("new_contract_recommendation") or {}
    if rec.get("new_contract_recommended") is not True:
        critical.append("new_contract_not_recommended")

    if rec.get("recommended_contract_key") != "VOLATILITY_RANGE_REGIME_FILTER_DIAGNOSTIC_V1":
        critical.append(f"unexpected_recommended_contract_key:{rec.get('recommended_contract_key')}")

    if rec.get("candidate_generation_allowed_now") is not False:
        critical.append("evaluator_allows_candidate_generation_unexpectedly")

    if rec.get("must_not_reopen_blocked_route") is not True:
        critical.append("evaluator_does_not_enforce_blocked_route_guard")

    if universe.get("universe_status") != "UNIVERSE_COVERAGE_GUARD_V2_PASS_FULL_1Y_OKX_SWAP_PANEL_READY":
        critical.append(f"universe_guard_not_full_pass:{universe.get('universe_status')}")

    if lesson_checker.get("route_blocked_by_lesson_memory") is not True:
        critical.append("lesson_checker_does_not_block_route")

    contract = None
    contract_written = False

    if critical:
        builder_status = "VOLATILITY_RANGE_REGIME_CONTRACT_BUILDER_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_INPUTS_BEFORE_CONTRACT"
        reason = "; ".join(critical)

    else:
        contract = build_contract(evaluator, diagnostic, universe, lesson_checker, release_gate)

        contract_path = RUN_DIR / f"{contract['contract_id']}.json"
        dump_json(contract_path, contract)
        dump_json(CONTRACT_LATEST, contract)

        contract["contract_path"] = str(contract_path)
        contract["contract_latest_path"] = str(CONTRACT_LATEST)

        builder_status = "VOLATILITY_RANGE_REGIME_CONTRACT_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_VOLATILITY_RANGE_REGIME_FILTER_DIAGNOSTIC_RUNNER"
        reason = f"contract_id={contract['contract_id']}; diagnostic_only=True"
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
            "month_regime_evaluator": str(MONTH_REGIME_EVAL_LATEST),
            "month_regime_diagnostic": str(MONTH_REGIME_DIAG_LATEST),
            "universe_guard_v2": str(UNIVERSE_GUARD_V2_LATEST),
            "lesson_checker": str(LESSON_CHECKER_LATEST),
            "release_gate_v4": str(RELEASE_GATE_V4_LATEST),
        },

        "decision": {
            "contract_key": "VOLATILITY_RANGE_REGIME_FILTER_DIAGNOSTIC_V1" if contract_written else None,
            "candidate_generation_recommended_now": False,
            "family_release_recommended": False,
            "promotion_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "repeat_same_route_recommended": False,
            "next_module": "edge_factory_os_volatility_range_regime_filter_diagnostic_v1.py" if contract_written else None,
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

    out_json = RUN_DIR / "volatility_range_regime_contract_builder_v1_state.json"
    out_md = RUN_DIR / "volatility_range_regime_contract_builder_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS VOLATILITY RANGE REGIME CONTRACT BUILDER v1

builder_status: {builder_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

contract_written: {contract_written}  
contract_latest_path: {CONTRACT_LATEST}

## Contract Summary

contract_id: {contract.get("contract_id") if contract else None}  
research_key: {contract.get("research_key") if contract else None}  
diagnostic_only: {safe_get(contract or {}, ["experiment_design", "diagnostic_only"])}  
candidate_generation_allowed_now: {safe_get(contract or {}, ["experiment_design", "candidate_generation_allowed_now"])}  
family_release_allowed_now: {safe_get(contract or {}, ["experiment_design", "family_release_allowed_now"])}  
repeat_same_route_allowed: {safe_get(contract or {}, ["blocked_route_guard", "repeat_same_route_allowed"])}  
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
    print("EDGE FACTORY OS VOLATILITY RANGE REGIME CONTRACT BUILDER v1")
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
        print(f"research_key: {contract.get('research_key')}")
        print(f"contract_latest_path: {CONTRACT_LATEST}")
        print(f"panel_path: {safe_get(contract, ['universe_input', 'panel_path'])}")
        print(f"diagnostic_only: {safe_get(contract, ['experiment_design', 'diagnostic_only'])}")
        print(f"candidate_generation_allowed_now: {safe_get(contract, ['experiment_design', 'candidate_generation_allowed_now'])}")
        print(f"family_release_allowed_now: {safe_get(contract, ['experiment_design', 'family_release_allowed_now'])}")
        print(f"repeat_same_route_allowed: {safe_get(contract, ['blocked_route_guard', 'repeat_same_route_allowed'])}")
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
