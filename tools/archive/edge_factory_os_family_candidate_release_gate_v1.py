from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_family_candidate_release_gate_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

UNIVERSE_V2_LATEST = (
    BASE_DIR
    / "edge_factory_os_universe_coverage_guard_v2"
    / "universe_coverage_guard_v2_latest.json"
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

THRESHOLD_LATEST = (
    BASE_DIR
    / "edge_factory_os_offline_threshold_sweep_runner_v1"
    / "offline_threshold_sweep_runner_latest.json"
)

SYMBOL_LATEST = (
    BASE_DIR
    / "edge_factory_os_symbol_concentration_diagnostic_v1"
    / "symbol_concentration_diagnostic_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"family_candidate_release_gate_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "family_candidate_release_gate_latest.json"
LATEST_MD = OUT_ROOT / "family_candidate_release_gate_latest.md"


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


def is_ok_status(text: Any) -> bool:
    s = str(text or "").upper()
    return "PASS" in s or "READY" in s or "COMPLETE" in s or "OK" in s


def safe_get(d: Dict[str, Any], path: List[str], default=None):
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def evaluate_gate(
    universe: Dict[str, Any],
    synth: Dict[str, Any],
    runner_plan: Dict[str, Any],
    threshold: Dict[str, Any],
    symbol: Dict[str, Any],
) -> Dict[str, Any]:
    checks: Dict[str, Dict[str, Any]] = {}

    universe_status = universe.get("universe_status")
    universe_full_pass = universe_status == "UNIVERSE_COVERAGE_GUARD_V2_PASS_FULL_1Y_OKX_SWAP_PANEL_READY"

    checks["UNIVERSE_FULL_1Y_OKX_SWAP_PASS"] = {
        "pass": bool(universe_full_pass),
        "status": universe_status,
        "evidence": {
            "best_universe_manifest": universe.get("best_universe_manifest"),
            "family_generation_allowed_by_universe_guard": universe.get("family_generation_allowed_by_universe_guard"),
            "candidate_generation_allowed_by_universe_guard": universe.get("candidate_generation_allowed_by_universe_guard"),
            "promotion_allowed_by_universe_guard": universe.get("promotion_allowed_by_universe_guard"),
        },
        "block_if_fail": True,
    }

    # These two are complete but explicitly small-sample/live-ledger diagnostics, not full-universe release tests.
    threshold_complete = threshold.get("runner_status") == "OFFLINE_THRESHOLD_SWEEP_RUNNER_COMPLETE"
    symbol_complete = symbol.get("diagnostic_status") == "SYMBOL_CONCENTRATION_DIAGNOSTIC_COMPLETE"

    threshold_baseline_count = safe_get(threshold, ["sweep_result", "baseline", "trade_count"], 0)
    threshold_best_count = safe_get(threshold, ["sweep_result", "ranked_results", 0, "summary", "trade_count"], 0)

    checks["FULL_UNIVERSE_OFFLINE_BACKTEST_PASS"] = {
        "pass": False,
        "status": "MISSING_FULL_UNIVERSE_BACKTEST_RESULT",
        "evidence": {
            "current_threshold_runner_complete": threshold_complete,
            "note": "Threshold runner used current primary paper ledger sample, not full 285-symbol 1Y universe backtest.",
        },
        "block_if_fail": True,
    }

    checks["OOS_OR_ROLLING_VALIDATION_PASS"] = {
        "pass": False,
        "status": "MISSING_OOS_OR_ROLLING_VALIDATION_RESULT",
        "evidence": {
            "runner_plan_status": runner_plan.get("plan_status"),
        },
        "block_if_fail": True,
    }

    checks["MONTH_STABILITY_PASS"] = {
        "pass": False,
        "status": "MISSING_MONTH_STABILITY_RESULT",
        "evidence": {
            "note": "Need positive month rate / monthly stability over full universe backtest or rolling OOS.",
        },
        "block_if_fail": True,
    }

    checks["COST_SLIPPAGE_SENSITIVITY_PASS"] = {
        "pass": False,
        "status": "RH4_COST_SENSITIVITY_NOT_RUN",
        "evidence": {
            "required_module_future": "edge_factory_os_cost_sensitivity_matrix_v1.py",
        },
        "block_if_fail": True,
    }

    # Symbol diagnostic completed but it showed overfit risk, so not pass.
    checks["SYMBOL_CONCENTRATION_RISK_PASS"] = {
        "pass": False,
        "status": "SYMBOL_CONCENTRATION_DIAGNOSTIC_COMPLETE_BUT_RISK_NOT_CLEARED",
        "evidence": {
            "symbol_complete": symbol_complete,
            "baseline": safe_get(symbol, ["diagnostic_result", "baseline"]),
            "warnings_from_synthesizer": synth.get("warnings"),
            "note": "Symbol ablation improved PnL but from small sample and removing multiple symbols; not a release pass.",
        },
        "block_if_fail": True,
    }

    checks["REGIME_BUCKET_DIAGNOSTIC_PASS"] = {
        "pass": False,
        "status": "RH3_REGIME_BUCKET_DIAGNOSTIC_NOT_RUN",
        "evidence": {
            "required_module_future": "edge_factory_os_regime_bucket_diagnostic_v1.py",
        },
        "block_if_fail": True,
    }

    # Current sample size is too small for release.
    sample_min_pass = bool(threshold_baseline_count and int(threshold_baseline_count) >= 50)

    checks["SAMPLE_SIZE_MINIMUM_PASS"] = {
        "pass": sample_min_pass,
        "status": "PASS" if sample_min_pass else "FAIL_SMALL_SAMPLE",
        "evidence": {
            "baseline_trade_count": threshold_baseline_count,
            "best_threshold_trade_count": threshold_best_count,
            "required_min_for_release": 50,
            "note": "This is release minimum, not research minimum.",
        },
        "block_if_fail": True,
    }

    checks["LESSON_MEMORY_NO_REPEAT_FAILURE_PASS"] = {
        "pass": False,
        "status": "LESSON_MEMORY_CHECK_NOT_RUN_FOR_THIS_CANDIDATE",
        "evidence": {
            "note": "Need check against OS memory/lesson index before any family release.",
        },
        "block_if_fail": True,
    }

    checks["RISK_AND_CAPITAL_SAFETY_PASS"] = {
        "pass": False,
        "status": "CAPITAL_REVIEW_NOT_READY_OR_NOT_ALLOWED",
        "evidence": {
            "capital_remaining": runner_plan.get("capital_remaining"),
            "capital_change_allowed": False,
            "note": "Capital/live/action remains blocked.",
        },
        "block_if_fail": True,
    }

    checks["MANUAL_OR_AI_REVIEW_PASS"] = {
        "pass": False,
        "status": "MANUAL_OR_AI_REVIEW_NOT_COMPLETED",
        "evidence": {
            "note": "API is optional, but a final release review must be explicit before release.",
        },
        "block_if_fail": True,
    }

    failed = [k for k, v in checks.items() if not v.get("pass")]
    passed = [k for k, v in checks.items() if v.get("pass")]

    return {
        "checks": checks,
        "passed_checks": passed,
        "failed_checks": failed,
        "required_tests": REQUIRED_TESTS,
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    universe = load_json(UNIVERSE_V2_LATEST)
    synth = load_json(SYNTH_LATEST)
    runner_plan = load_json(RUNNER_PLAN_LATEST)
    threshold = load_json(THRESHOLD_LATEST)
    symbol = load_json(SYMBOL_LATEST)

    if universe is None:
        critical.append("universe_guard_v2_latest_missing")
        universe = {}

    if synth is None:
        attention.append("synthesizer_latest_missing")
        synth = {}

    if runner_plan is None:
        attention.append("runner_plan_latest_missing")
        runner_plan = {}

    if threshold is None:
        attention.append("threshold_runner_latest_missing")
        threshold = {}

    if symbol is None:
        attention.append("symbol_diagnostic_latest_missing")
        symbol = {}

    gate_eval = evaluate_gate(universe, synth, runner_plan, threshold, symbol)

    failed_checks = gate_eval["failed_checks"]
    passed_checks = gate_eval["passed_checks"]

    release_allowed = len(failed_checks) == 0
    candidate_family_output_allowed = release_allowed
    promotion_allowed = release_allowed

    if critical:
        release_status = "FAMILY_CANDIDATE_RELEASE_GATE_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_MISSING_REQUIRED_INPUTS"
        reason = "; ".join(critical)

    elif release_allowed:
        release_status = "FAMILY_CANDIDATE_RELEASE_GATE_PASS"
        severity = "ATTENTION"
        allowed_scope = "RELEASE_REVIEW_ONLY"
        next_action = "MANUAL_FINAL_REVIEW_BEFORE_ANY_RUNTIME_OR_PAPER_CHANGE"
        reason = "all required tests passed"

    else:
        release_status = "FAMILY_CANDIDATE_RELEASE_GATE_BLOCKED_TESTS_INCOMPLETE"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "COMPLETE_MISSING_REQUIRED_TESTS_BEFORE_FAMILY_RELEASE"
        reason = f"failed_required_checks={len(failed_checks)}"

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
            "offline_research_result_synthesizer": str(SYNTH_LATEST),
            "runner_plan": str(RUNNER_PLAN_LATEST),
            "threshold_runner": str(THRESHOLD_LATEST),
            "symbol_concentration_diagnostic": str(SYMBOL_LATEST),
        },

        "passed_check_count": len(passed_checks),
        "failed_check_count": len(failed_checks),
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "checks": gate_eval["checks"],

        "candidate_family_output_allowed": candidate_family_output_allowed,
        "family_release_allowed": release_allowed,
        "promotion_allowed": promotion_allowed,

        "current_completed_research_is_lesson_candidate_only": True,
        "current_completed_research_not_a_family_release": True,

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

    out_json = RUN_DIR / "family_candidate_release_gate_v1_state.json"
    out_md = RUN_DIR / "family_candidate_release_gate_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md_lines = [
        "# EDGE FACTORY OS FAMILY CANDIDATE RELEASE GATE v1",
        "",
        f"release_status: {release_status}",
        f"severity: {severity}",
        f"allowed_scope: {allowed_scope}",
        f"next_action: {next_action}",
        f"reason: {reason}",
        "",
        "## Decision",
        "",
        f"candidate_family_output_allowed: {candidate_family_output_allowed}",
        f"family_release_allowed: {release_allowed}",
        f"promotion_allowed: {promotion_allowed}",
        "",
        "## Checks",
        "",
        f"passed_check_count: {len(passed_checks)}",
        f"failed_check_count: {len(failed_checks)}",
        "",
        "### Passed",
        "",
        json.dumps(passed_checks, indent=2),
        "",
        "### Failed",
        "",
        json.dumps(failed_checks, indent=2),
        "",
        "## Full Check Detail",
        "",
        json.dumps(gate_eval["checks"], indent=2, default=str)[:20000],
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
    print("EDGE FACTORY OS FAMILY CANDIDATE RELEASE GATE v1")
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
    print(f"family_release_allowed: {release_allowed}")
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
    for k, v in gate_eval["checks"].items():
        print(f"{k}: pass={v.get('pass')} status={v.get('status')}")
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
