from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_research_direction_contract_builder_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

QUEUE_LATEST = (
    BASE_DIR
    / "edge_factory_os_new_research_direction_queue_v1"
    / "new_research_direction_queue_latest.json"
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
RUN_DIR = OUT_ROOT / f"research_direction_contract_builder_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "research_direction_contract_builder_latest.json"
LATEST_MD = OUT_ROOT / "research_direction_contract_builder_latest.md"

CONTRACT_ROOT = BASE_DIR / "edge_factory_os_research_direction_contracts"
CONTRACT_LATEST = CONTRACT_ROOT / "research_direction_contract_latest.json"


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


def select_top_direction(queue_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    directions = queue_state.get("directions")

    if not isinstance(directions, list) or not directions:
        return None

    valid = [
        d for d in directions
        if isinstance(d, dict)
        and d.get("status") == "QUEUED_READ_ONLY_RESEARCH"
        and d.get("release_candidate_allowed_now") is False
    ]

    if not valid:
        return None

    valid.sort(key=lambda x: int(x.get("priority") or 0), reverse=True)
    return valid[0]


def build_rd1_contract(
    direction: Dict[str, Any],
    universe: Dict[str, Any],
    lesson_checker: Dict[str, Any],
    release_gate: Dict[str, Any],
) -> Dict[str, Any]:
    best_manifest = universe.get("best_universe_manifest") or {}
    panel_path = best_manifest.get("panel_path")

    blocked_route_hash = lesson_checker.get("route_hash")
    blocked_route = lesson_checker.get("blocked_route")

    contract_id = f"RD1_MONTH_REGIME_INSTABILITY_FEATURES_CONTRACT_{NOW.strftime('%Y%m%d_%H%M%S')}"

    contract = {
        "contract_schema": "edge_factory_os_research_direction_contract_v1",
        "contract_id": contract_id,
        "created_at_utc": NOW.isoformat(),

        "research_direction": {
            "direction_id": direction.get("direction_id"),
            "research_key": direction.get("research_key"),
            "priority": direction.get("priority"),
            "primary_question": direction.get("primary_question"),
            "hypothesis": direction.get("hypothesis"),
            "family_scope": direction.get("family_scope"),
        },

        "selected_reason": {
            "why_selected": [
                "highest priority queued read-only research direction",
                "blocked route should not be repeated",
                "full-universe failure was dominated by month/train/OOS instability",
                "month/regime features are the next missing explanatory layer",
            ],
            "source_release_gate_status": release_gate.get("release_status"),
            "source_lesson_status": lesson_checker.get("checker_status"),
            "source_route_blocked": lesson_checker.get("route_blocked_by_lesson_memory"),
        },

        "blocked_route_guard": {
            "blocked_route_hash": blocked_route_hash,
            "blocked_route": blocked_route,
            "repeat_same_route_allowed": False,
            "must_not_test_as_candidate_family": [
                "same ret3 threshold grid",
                "same fixed hold-hour grid",
                "same entry_range cap grid",
                "same market filter grid",
                "paper-ledger-only improvement",
                "single-symbol improvement",
            ],
            "allowed_use_of_blocked_route": [
                "diagnostic target only",
                "failure-mode explanation only",
                "feature discovery benchmark only",
            ],
            "not_allowed_use_of_blocked_route": [
                "candidate release",
                "runtime patch",
                "capital decision",
                "family promotion",
                "same-route rerun without new evidence",
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

        "research_objectives": [
            {
                "objective_id": "O1_MONTH_FAILURE_MAP",
                "question": "Which months/regimes caused the blocked impulse route to fail?",
                "required_outputs": [
                    "monthly_return_table",
                    "monthly_trade_count_table",
                    "bad_month_list",
                    "good_month_list",
                    "bad_month_feature_profile",
                    "good_month_feature_profile",
                ],
            },
            {
                "objective_id": "O2_FEATURE_SEPARATION",
                "question": "Which available features separate good months from bad months before PnL is evaluated?",
                "required_outputs": [
                    "candidate_feature_columns_detected",
                    "feature_bucket_performance_table",
                    "good_vs_bad_month_feature_statistics",
                    "feature_missingness_report",
                ],
            },
            {
                "objective_id": "O3_STABILITY_FILTER_DISCOVERY",
                "question": "Can a non-blocked feature/regime filter improve month stability without reproducing the failed route?",
                "required_outputs": [
                    "candidate_regime_filters",
                    "filter_month_stability",
                    "train_oos_stability_preview",
                    "symbol_concentration_check",
                    "cost_sensitivity_requirement",
                ],
            },
            {
                "objective_id": "O4_RESEARCH_DECISION",
                "question": "Should this produce a new candidate contract, or only a lesson/failure report?",
                "required_outputs": [
                    "new_candidate_contract_allowed",
                    "reason_if_not_allowed",
                    "required_next_validation",
                    "release_gate_impact_preview",
                ],
            },
        ],

        "allowed_feature_search_space": {
            "must_be_available_before_pnl_filtering": True,
            "allowed_columns_or_families": [
                "mkt_ret3_bps",
                "mkt_ret6_bps",
                "coin_ret3_bps",
                "coin_ret6_bps",
                "entry_vol_quote",
                "entry_range_bps",
                "cross_sectional_return_rank_if_constructed",
                "cross_sectional_volatility_rank_if_constructed",
                "market_breadth_if_constructed",
                "market_dispersion_if_constructed",
                "monthly_regime_label_if_constructed",
                "volatility_regime_label_if_constructed",
                "liquidity_regime_label_if_constructed",
            ],
            "disallowed_as_primary_release_filter": [
                "the exact blocked route hash",
                "raw ret3 threshold alone",
                "fixed hold-hour selection alone",
                "manual symbol blacklist",
                "single winning symbol filter",
                "paper-ledger-only filter",
            ],
        },

        "candidate_generation_rules": {
            "candidate_generation_allowed_from_this_contract": False,
            "this_contract_is_diagnostic_only": True,
            "new_candidate_contract_may_be_created_later_only_if": [
                "new regime/feature evidence is not equivalent to blocked ret3 threshold route",
                "feature exists across full universe panel",
                "feature is known before trade outcome",
                "candidate passes full-universe backtest",
                "candidate passes train/OOS and month stability",
                "candidate passes cost/slippage sensitivity",
                "candidate passes symbol concentration risk",
                "lesson memory checker does not block the new route hash",
            ],
        },

        "pass_fail_policy": {
            "diagnostic_pass_if": [
                "full panel is loaded",
                "monthly failure map produced",
                "bad vs good month features compared",
                "candidate feature/regime hypotheses generated",
                "blocked route is not recommended for release",
            ],
            "diagnostic_fail_if": [
                "panel missing",
                "feature columns unavailable and no constructable alternatives",
                "diagnostic repeats blocked route as a candidate",
                "outputs recommend runtime/capital/live changes",
            ],
            "release_pass_possible_in_this_module": False,
        },

        "expected_next_module": {
            "module_name": "edge_factory_os_month_regime_instability_diagnostic_v1.py",
            "purpose": "Execute this contract read-only on the full 1Y OKX swap panel.",
            "execution_allowed_after_contract": True,
            "still_release_candidate_allowed": False,
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

    queue_state = load_json(QUEUE_LATEST)
    universe = load_json(UNIVERSE_GUARD_V2_LATEST)
    lesson_checker = load_json(LESSON_CHECKER_LATEST)
    release_gate = load_json(RELEASE_GATE_V4_LATEST)

    if not isinstance(queue_state, dict):
        critical.append("new_research_direction_queue_latest_missing")
        queue_state = {}

    if not isinstance(universe, dict):
        critical.append("universe_guard_v2_latest_missing")
        universe = {}

    if not isinstance(lesson_checker, dict):
        critical.append("lesson_memory_checker_latest_missing")
        lesson_checker = {}

    if not isinstance(release_gate, dict):
        attention.append("release_gate_v4_latest_missing")
        release_gate = {}

    top_direction = select_top_direction(queue_state)

    if top_direction is None:
        critical.append("no_queued_read_only_research_direction_found")

    if top_direction and top_direction.get("research_key") != "RD1_MONTH_REGIME_INSTABILITY_FEATURES":
        attention.append(f"top_direction_not_rd1:{top_direction.get('research_key')}")

    universe_ok = universe.get("universe_status") == "UNIVERSE_COVERAGE_GUARD_V2_PASS_FULL_1Y_OKX_SWAP_PANEL_READY"

    if not universe_ok:
        critical.append(f"universe_guard_not_pass:{universe.get('universe_status')}")

    route_blocked = lesson_checker.get("route_blocked_by_lesson_memory") is True

    if not route_blocked:
        attention.append("blocked_route_not_confirmed_by_lesson_checker")

    contract = None
    contract_written = False

    if critical:
        builder_status = "RESEARCH_DIRECTION_CONTRACT_BUILDER_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_MISSING_INPUTS"
        reason = "; ".join(critical)

    else:
        contract = build_rd1_contract(top_direction, universe, lesson_checker, release_gate)

        contract_path = RUN_DIR / f"{contract['contract_id']}.json"
        dump_json(contract_path, contract)
        dump_json(CONTRACT_LATEST, contract)

        contract["contract_path"] = str(contract_path)
        contract["contract_latest_path"] = str(CONTRACT_LATEST)

        builder_status = "RESEARCH_DIRECTION_CONTRACT_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_MONTH_REGIME_INSTABILITY_DIAGNOSTIC_RUNNER"
        reason = f"contract_id={contract['contract_id']}; research_key={top_direction.get('research_key')}"
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
            "queue_latest": str(QUEUE_LATEST),
            "universe_guard_v2": str(UNIVERSE_GUARD_V2_LATEST),
            "lesson_checker": str(LESSON_CHECKER_LATEST),
            "release_gate_v4": str(RELEASE_GATE_V4_LATEST),
        },

        "decision": {
            "selected_research_key": top_direction.get("research_key") if top_direction else None,
            "repeat_same_route_recommended": False,
            "candidate_generation_recommended_now": False,
            "family_release_recommended": False,
            "promotion_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "next_module": "edge_factory_os_month_regime_instability_diagnostic_v1.py" if contract_written else None,
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

    out_json = RUN_DIR / "research_direction_contract_builder_v1_state.json"
    out_md = RUN_DIR / "research_direction_contract_builder_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md_lines = [
        "# EDGE FACTORY OS RESEARCH DIRECTION CONTRACT BUILDER v1",
        "",
        f"builder_status: {builder_status}",
        f"severity: {severity}",
        f"allowed_scope: {allowed_scope}",
        f"next_action: {next_action}",
        f"reason: {reason}",
        "",
        "## Selected Direction",
        "",
        json.dumps(top_direction, indent=2, default=str)[:8000],
        "",
        "## Contract",
        "",
        json.dumps(contract, indent=2, default=str)[:20000],
        "",
        "## Decision",
        "",
        json.dumps(result["decision"], indent=2, default=str),
        "",
        "## Safety",
        "",
        "read_only: True",
        "offline_only: True",
        "mutate_runtime_allowed: False",
        "launcher_allowed: False",
        "patch_runtime_allowed: False",
        "active_paper_allowed: False",
        "live_allowed: False",
        "capital_change_allowed: False",
        "family_disable_allowed: False",
        "real_orders_allowed: False",
        "execution_performed: False",
        "",
        f"critical: {critical}",
        f"attention: {attention}",
        f"info: {info}",
    ]

    out_md.write_text("\n".join(md_lines), encoding="utf-8")
    LATEST_MD.write_text("\n".join(md_lines), encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS RESEARCH DIRECTION CONTRACT BUILDER v1")
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
        print(f"contract_latest_path: {CONTRACT_LATEST}")
        print(f"panel_path: {safe_get(contract, ['universe_input', 'panel_path'])}")
        print(f"repeat_same_route_allowed: {safe_get(contract, ['blocked_route_guard', 'repeat_same_route_allowed'])}")
        print(f"candidate_generation_allowed_from_this_contract: {safe_get(contract, ['candidate_generation_rules', 'candidate_generation_allowed_from_this_contract'])}")
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
