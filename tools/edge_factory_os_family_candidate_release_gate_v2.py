from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_family_candidate_release_gate_v2"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

UNIVERSE_V2_LATEST = (
    BASE_DIR
    / "edge_factory_os_universe_coverage_guard_v2"
    / "universe_coverage_guard_v2_latest.json"
)

COST_EVAL_LATEST = (
    BASE_DIR
    / "edge_factory_os_cost_sensitivity_evaluator_v1"
    / "cost_sensitivity_evaluator_latest.json"
)

REGIME_EVAL_LATEST = (
    BASE_DIR
    / "edge_factory_os_regime_bucket_evaluator_v1"
    / "regime_bucket_evaluator_latest.json"
)

SYNTH_LATEST = (
    BASE_DIR
    / "edge_factory_os_offline_research_result_synthesizer_v1"
    / "offline_research_result_synthesizer_latest.json"
)

RUNNER_PLAN_LATEST = (
    BASE_DIR
    / "edge_factory_os_offline_research_runner_plan_v1"
    / "offline_research_runner_plan_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"family_candidate_release_gate_v2_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "family_candidate_release_gate_v2_latest.json"
LATEST_MD = OUT_ROOT / "family_candidate_release_gate_v2_latest.md"


REQUIRED_TESTS = [
    "UNIVERSE_FULL_1Y_OKX_SWAP_PASS",
    "FULL_UNIVERSE_OFFLINE_BACKTEST_PASS",
    "OOS_OR_ROLLING_VALIDATION_PASS",
    "MONTH_STABILITY_PASS",
    "COST_SLIPPAGE_SENSITIVITY_PASS",
    "SYMBOL_CONCENTRATION_RISK_PASS",
    "REGIME_BUCKET_DIAGNOSTIC_PASS",
    "SAMPLE_SIZE_MINIMUM_PASS",
    "LESSON_MEMORY_NO_REPEAT_FAILURE_PASS",
    "RISK_AND_CAPITAL_SAFETY_PASS",
    "MANUAL_OR_AI_REVIEW_PASS",
]


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def dump_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, default=str)


def safe_get(d: Dict[str, Any], path: List[str], default=None):
    cur = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def make_check(pass_value: bool, status: str, evidence: Dict[str, object], block_if_fail: bool = True) -> Dict[str, object]:
    return {
        "pass": bool(pass_value),
        "status": status,
        "evidence": evidence,
        "block_if_fail": block_if_fail,
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    universe = load_json(UNIVERSE_V2_LATEST)
    cost_eval = load_json(COST_EVAL_LATEST)
    regime_eval = load_json(REGIME_EVAL_LATEST)
    synth = load_json(SYNTH_LATEST)
    runner_plan = load_json(RUNNER_PLAN_LATEST)

    if universe is None:
        critical.append("universe_guard_v2_latest_missing")
        universe = {}

    if cost_eval is None:
        attention.append("cost_sensitivity_evaluator_latest_missing")
        cost_eval = {}

    if regime_eval is None:
        attention.append("regime_bucket_evaluator_latest_missing")
        regime_eval = {}

    if synth is None:
        attention.append("offline_research_synthesizer_latest_missing")
        synth = {}

    if runner_plan is None:
        attention.append("runner_plan_latest_missing")
        runner_plan = {}

    checks: Dict[str, Dict[str, object]] = {}

    universe_pass = universe.get("universe_status") == "UNIVERSE_COVERAGE_GUARD_V2_PASS_FULL_1Y_OKX_SWAP_PANEL_READY"
    checks["UNIVERSE_FULL_1Y_OKX_SWAP_PASS"] = make_check(
        universe_pass,
        str(universe.get("universe_status")),
        {
            "best_universe_manifest": universe.get("best_universe_manifest"),
            "family_generation_allowed_by_universe_guard": universe.get("family_generation_allowed_by_universe_guard"),
            "candidate_generation_allowed_by_universe_guard": universe.get("candidate_generation_allowed_by_universe_guard"),
            "promotion_allowed_by_universe_guard": universe.get("promotion_allowed_by_universe_guard"),
        },
    )

    checks["FULL_UNIVERSE_OFFLINE_BACKTEST_PASS"] = make_check(
        False,
        "MISSING_FULL_UNIVERSE_OFFLINE_BACKTEST_RESULT",
        {
            "note": "Current completed tests used paper/live closed-trade ledger. Need full 285-symbol 1Y panel offline backtest before family release.",
            "required_panel": safe_get(universe, ["best_universe_manifest", "panel_path"]),
        },
    )

    checks["OOS_OR_ROLLING_VALIDATION_PASS"] = make_check(
        False,
        "MISSING_OOS_OR_ROLLING_VALIDATION_RESULT",
        {
            "note": "Need time OOS / rolling validation after full-universe offline candidate test.",
        },
    )

    checks["MONTH_STABILITY_PASS"] = make_check(
        False,
        "MISSING_MONTH_STABILITY_RESULT",
        {
            "note": "Need monthly stability / positive month rate over full universe.",
        },
    )

    cost_feed = cost_eval.get("release_gate_feed") or {}
    cost_pass = cost_feed.get("COST_SLIPPAGE_SENSITIVITY_PASS") is True

    checks["COST_SLIPPAGE_SENSITIVITY_PASS"] = make_check(
        cost_pass,
        str(cost_feed.get("status") or cost_eval.get("evaluator_status")),
        {
            "release_gate_feed": cost_feed,
            "baseline": cost_eval.get("baseline"),
            "scenario_table": cost_eval.get("scenario_table"),
            "findings": cost_eval.get("findings"),
            "interpretation": "RH4 ran. It is not missing anymore; it failed release pass because edge was not recovered even under fee-only/better cost scenarios.",
        },
    )

    regime_feed = regime_eval.get("release_gate_feed") or {}
    regime_pass = regime_feed.get("REGIME_BUCKET_DIAGNOSTIC_PASS") is True

    checks["REGIME_BUCKET_DIAGNOSTIC_PASS"] = make_check(
        regime_pass,
        str(regime_feed.get("status") or regime_eval.get("evaluator_status")),
        {
            "release_gate_feed": regime_feed,
            "baseline": regime_eval.get("baseline"),
            "best_filter": regime_eval.get("best_filter"),
            "findings": regime_eval.get("findings"),
            "interpretation": "RH3 ran. It is promising but not release-pass due small selected sample, symbol dependence, missing columns, and full-universe/OOS requirement.",
        },
    )

    # Symbol risk is not cleared if regime evaluator or synthesizer reports symbol dependence / overfit.
    warnings = synth.get("warnings") or []
    symbol_risk_clear = False

    checks["SYMBOL_CONCENTRATION_RISK_PASS"] = make_check(
        symbol_risk_clear,
        "SYMBOL_CONCENTRATION_RISK_NOT_CLEARED",
        {
            "synthesizer_warnings": warnings,
            "regime_findings": regime_eval.get("findings"),
            "cost_findings": cost_eval.get("findings"),
            "interpretation": "LAB/USELESS concentration and symbol ablation overfit risk remain unresolved.",
        },
    )

    selected_sample = safe_get(regime_eval, ["best_filter", "selected_summary", "trade_count"], 0)
    baseline_sample = safe_get(cost_eval, ["baseline", "trade_count"], 0)
    sample_count = max(int(selected_sample or 0), int(baseline_sample or 0))

    checks["SAMPLE_SIZE_MINIMUM_PASS"] = make_check(
        sample_count >= 50,
        "PASS" if sample_count >= 50 else "FAIL_SMALL_SAMPLE",
        {
            "largest_relevant_sample_count": sample_count,
            "required_release_minimum": 50,
            "selected_sample": selected_sample,
            "baseline_sample": baseline_sample,
        },
    )

    checks["LESSON_MEMORY_NO_REPEAT_FAILURE_PASS"] = make_check(
        False,
        "LESSON_MEMORY_CHECK_NOT_RUN_FOR_THIS_CANDIDATE",
        {
            "note": "Need lesson memory candidate/index check before release.",
        },
    )

    checks["RISK_AND_CAPITAL_SAFETY_PASS"] = make_check(
        False,
        "CAPITAL_REVIEW_NOT_READY_OR_NOT_ALLOWED",
        {
            "capital_remaining": runner_plan.get("capital_remaining"),
            "capital_change_allowed": False,
            "note": "No capital or runtime action allowed from these tests.",
        },
    )

    checks["MANUAL_OR_AI_REVIEW_PASS"] = make_check(
        False,
        "MANUAL_OR_AI_REVIEW_NOT_COMPLETED",
        {
            "note": "Final release needs explicit review after all test evidence exists. API is optional; manual review can satisfy this later.",
        },
    )

    passed_checks = [k for k, v in checks.items() if v.get("pass") is True]
    failed_checks = [k for k, v in checks.items() if v.get("pass") is not True]

    family_release_allowed = len(failed_checks) == 0
    candidate_family_output_allowed = family_release_allowed
    promotion_allowed = family_release_allowed

    if critical:
        release_status = "FAMILY_CANDIDATE_RELEASE_GATE_V2_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_MISSING_REQUIRED_INPUTS"
        reason = "; ".join(critical)

    elif family_release_allowed:
        release_status = "FAMILY_CANDIDATE_RELEASE_GATE_V2_PASS"
        severity = "ATTENTION"
        allowed_scope = "RELEASE_REVIEW_ONLY"
        next_action = "MANUAL_FINAL_REVIEW_BEFORE_ANY_RUNTIME_OR_PAPER_CHANGE"
        reason = "all required tests passed"

    else:
        release_status = "FAMILY_CANDIDATE_RELEASE_GATE_V2_BLOCKED_TESTS_FAILED_OR_INCOMPLETE"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_FULL_UNIVERSE_OFFLINE_BACKTEST_AND_OOS_VALIDATION"
        reason = f"failed_required_checks={len(failed_checks)}; rh3_rh4_completed_but_not_passed"

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "release_status": release_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "rule": {
            "do_not_release_family_until_all_required_tests_pass": True,
            "do_not_release_from_paper_ledger_only": True,
            "do_not_release_from_single_symbol_or_small_sample": True,
            "do_not_release_from_ai_or_manual_opinion_without_tests": True,
            "do_not_patch_runtime_until_release_gate_pass": True,
            "do_not_change_capital_until_capital_gate_pass": True,
        },

        "sources": {
            "universe_guard_v2": str(UNIVERSE_V2_LATEST),
            "cost_sensitivity_evaluator_v1": str(COST_EVAL_LATEST),
            "regime_bucket_evaluator_v1": str(REGIME_EVAL_LATEST),
            "offline_research_result_synthesizer_v1": str(SYNTH_LATEST),
            "runner_plan": str(RUNNER_PLAN_LATEST),
        },

        "passed_check_count": len(passed_checks),
        "failed_check_count": len(failed_checks),
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "checks": checks,

        "candidate_family_output_allowed": candidate_family_output_allowed,
        "family_release_allowed": family_release_allowed,
        "promotion_allowed": promotion_allowed,

        "current_completed_research_is_lesson_candidate_only": True,
        "current_completed_research_not_a_family_release": True,

        "next_missing_work_order": [
            "FULL_UNIVERSE_OFFLINE_BACKTEST_PASS",
            "OOS_OR_ROLLING_VALIDATION_PASS",
            "MONTH_STABILITY_PASS",
            "LESSON_MEMORY_NO_REPEAT_FAILURE_PASS",
            "RISK_AND_CAPITAL_SAFETY_PASS",
            "MANUAL_OR_AI_REVIEW_PASS",
        ],

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

    out_json = RUN_DIR / "family_candidate_release_gate_v2_state.json"
    out_md = RUN_DIR / "family_candidate_release_gate_v2_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS FAMILY CANDIDATE RELEASE GATE v2

release_status: {release_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

## Decision

candidate_family_output_allowed: {candidate_family_output_allowed}  
family_release_allowed: {family_release_allowed}  
promotion_allowed: {promotion_allowed}

## Check Summary

passed_check_count: {len(passed_checks)}  
failed_check_count: {len(failed_checks)}

passed_checks:
{json.dumps(passed_checks, indent=2)}

failed_checks:
{json.dumps(failed_checks, indent=2)}

## Full Checks

{json.dumps(checks, indent=2, default=str)[:24000]}

## Next Missing Work Order

{json.dumps(result["next_missing_work_order"], indent=2)}

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
    print("EDGE FACTORY OS FAMILY CANDIDATE RELEASE GATE v2")
    print("=" * 100)
    print(f"release_status: {release_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("DECISION")
    print("-" * 100)
    print(f"candidate_family_output_allowed: {candidate_family_output_allowed}")
    print(f"family_release_allowed: {family_release_allowed}")
    print(f"promotion_allowed: {promotion_allowed}")
    print()
    print("CHECK SUMMARY")
    print("-" * 100)
    print(f"passed_check_count: {len(passed_checks)}")
    print(f"failed_check_count: {len(failed_checks)}")
    print()
    print("PASSED CHECKS")
    print("-" * 100)
    for c in passed_checks:
        print(c)
    print()
    print("FAILED CHECKS")
    print("-" * 100)
    for c in failed_checks:
        print(c)
    print()
    print("KEY CHECK DETAILS")
    print("-" * 100)
    for k, v in checks.items():
        print(f"{k}: pass={v.get('pass')} status={v.get('status')}")
    print()
    print("NEXT MISSING WORK ORDER")
    print("-" * 100)
    for item in result["next_missing_work_order"]:
        print(item)
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
