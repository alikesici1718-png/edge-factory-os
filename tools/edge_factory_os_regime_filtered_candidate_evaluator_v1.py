from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_regime_filtered_candidate_evaluator_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

RUNNER_LATEST = (
    BASE_DIR
    / "edge_factory_os_regime_filtered_candidate_backtest_runner_v1"
    / "regime_filtered_candidate_backtest_runner_latest.json"
)

CANDIDATE_CONTRACT_LATEST = (
    BASE_DIR
    / "edge_factory_os_candidate_contracts"
    / "regime_filtered_impulse_candidate_contract_latest.json"
)

LESSON_CHECKER_LATEST = (
    BASE_DIR
    / "edge_factory_os_candidate_route_lesson_memory_checker_v1"
    / "candidate_route_lesson_memory_checker_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"regime_filtered_candidate_evaluator_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "regime_filtered_candidate_evaluator_latest.json"
LATEST_MD = OUT_ROOT / "regime_filtered_candidate_evaluator_latest.md"


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


def fnum(v: Any, default=None):
    try:
        if v is None:
            return default
        return float(v)
    except Exception:
        return default


def inum(v: Any, default=0):
    try:
        if v is None:
            return default
        return int(float(v))
    except Exception:
        return default


def safe_get(d: Dict[str, Any], path: List[str], default=None):
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def check_release_criteria(runner: Dict[str, Any]) -> Dict[str, Any]:
    candidate = runner.get("candidate_summary") or {}
    symbols = runner.get("candidate_symbol_concentration") or {}

    all_s = candidate.get("all") or {}
    train_s = candidate.get("train") or {}
    oos_s = candidate.get("oos") or {}

    checks = {
        "all_trade_count": {
            "pass": inum(all_s.get("trade_count")) >= 300,
            "value": all_s.get("trade_count"),
            "required": ">=300",
        },
        "oos_trade_count": {
            "pass": inum(oos_s.get("trade_count")) >= 75,
            "value": oos_s.get("trade_count"),
            "required": ">=75",
        },
        "all_mean_positive": {
            "pass": fnum(all_s.get("mean_net_bps"), -999999) > 0,
            "value": all_s.get("mean_net_bps"),
            "required": ">0",
        },
        "train_mean_positive": {
            "pass": fnum(train_s.get("mean_net_bps"), -999999) > 0,
            "value": train_s.get("mean_net_bps"),
            "required": ">0",
        },
        "oos_mean_positive": {
            "pass": fnum(oos_s.get("mean_net_bps"), -999999) > 0,
            "value": oos_s.get("mean_net_bps"),
            "required": ">0",
        },
        "train_profit_factor": {
            "pass": fnum(train_s.get("profit_factor"), 0) >= 1.10,
            "value": train_s.get("profit_factor"),
            "required": ">=1.10",
        },
        "oos_profit_factor": {
            "pass": fnum(oos_s.get("profit_factor"), 0) >= 1.10,
            "value": oos_s.get("profit_factor"),
            "required": ">=1.10",
        },
        "oos_win_rate": {
            "pass": fnum(oos_s.get("win_rate"), 0) >= 0.45,
            "value": oos_s.get("win_rate"),
            "required": ">=0.45",
        },
        "all_positive_month_rate": {
            "pass": fnum(all_s.get("positive_month_rate"), 0) >= 0.55,
            "value": all_s.get("positive_month_rate"),
            "required": ">=0.55",
        },
        "oos_positive_month_rate": {
            "pass": fnum(oos_s.get("positive_month_rate"), 0) >= 0.50,
            "value": oos_s.get("positive_month_rate"),
            "required": ">=0.50",
        },
        "symbol_concentration": {
            "pass": (
                symbols.get("top_symbol_abs_share") is None
                or fnum(symbols.get("top_symbol_abs_share"), 999) <= 0.50
            ),
            "value": symbols.get("top_symbol_abs_share"),
            "required": "<=0.50",
        },
    }

    passed = [k for k, v in checks.items() if v.get("pass") is True]
    failed = [k for k, v in checks.items() if v.get("pass") is not True]

    return {
        "checks": checks,
        "passed": passed,
        "failed": failed,
        "full_release_quality_pass": len(failed) == 0,
    }


def compare_candidate_to_baseline(runner: Dict[str, Any]) -> Dict[str, Any]:
    candidate = runner.get("candidate_summary") or {}
    baseline = runner.get("baseline_summary_old_route_comparison_only") or {}

    ca = candidate.get("all") or {}
    ct = candidate.get("train") or {}
    co = candidate.get("oos") or {}

    ba = baseline.get("all") or {}
    bt = baseline.get("train") or {}
    bo = baseline.get("oos") or {}

    return {
        "all_total_improvement_bps": fnum(ca.get("total_net_bps"), 0) - fnum(ba.get("total_net_bps"), 0),
        "all_mean_improvement_bps": fnum(ca.get("mean_net_bps"), 0) - fnum(ba.get("mean_net_bps"), 0),
        "all_pf_improvement": fnum(ca.get("profit_factor"), 0) - fnum(ba.get("profit_factor"), 0),
        "all_win_rate_improvement": fnum(ca.get("win_rate"), 0) - fnum(ba.get("win_rate"), 0),

        "train_total_improvement_bps": fnum(ct.get("total_net_bps"), 0) - fnum(bt.get("total_net_bps"), 0),
        "train_mean_improvement_bps": fnum(ct.get("mean_net_bps"), 0) - fnum(bt.get("mean_net_bps"), 0),
        "train_pf_improvement": fnum(ct.get("profit_factor"), 0) - fnum(bt.get("profit_factor"), 0),
        "train_win_rate_improvement": fnum(ct.get("win_rate"), 0) - fnum(bt.get("win_rate"), 0),

        "oos_total_delta_bps": fnum(co.get("total_net_bps"), 0) - fnum(bo.get("total_net_bps"), 0),
        "oos_mean_improvement_bps": fnum(co.get("mean_net_bps"), 0) - fnum(bo.get("mean_net_bps"), 0),
        "oos_pf_improvement": fnum(co.get("profit_factor"), 0) - fnum(bo.get("profit_factor"), 0),
        "oos_win_rate_delta": fnum(co.get("win_rate"), 0) - fnum(bo.get("win_rate"), 0),

        "candidate_trade_count": ca.get("trade_count"),
        "baseline_trade_count": ba.get("trade_count"),
        "candidate_positive_month_rate": ca.get("positive_month_rate"),
        "baseline_positive_month_rate": ba.get("positive_month_rate"),
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    runner = load_json(RUNNER_LATEST)
    contract = load_json(CANDIDATE_CONTRACT_LATEST)
    lesson = load_json(LESSON_CHECKER_LATEST)

    if not isinstance(runner, dict):
        critical.append("regime_filtered_candidate_runner_latest_missing")
        runner = {}

    if not isinstance(contract, dict):
        critical.append("candidate_contract_latest_missing")
        contract = {}

    if not isinstance(lesson, dict):
        critical.append("candidate_route_lesson_checker_latest_missing")
        lesson = {}

    if runner.get("runner_status") != "REGIME_FILTERED_CANDIDATE_BACKTEST_COMPLETE":
        critical.append(f"runner_not_complete:{runner.get('runner_status')}")

    if contract.get("candidate_key") != "REGIME_FILTERED_IMPULSE_ROUTE_CANDIDATE_V1":
        critical.append(f"unexpected_candidate_key:{contract.get('candidate_key')}")

    if lesson.get("checker_status") != "CANDIDATE_ROUTE_LESSON_MEMORY_PASS_NEW_ROUTE":
        critical.append(f"lesson_memory_not_pass:{lesson.get('checker_status')}")

    if runner.get("candidate_route_hash") != contract.get("candidate_route_hash"):
        critical.append("runner_contract_route_hash_mismatch")

    if contract.get("candidate_route_hash") != lesson.get("candidate_route_hash"):
        critical.append("contract_lesson_route_hash_mismatch")

    criteria = check_release_criteria(runner)
    comparison = compare_candidate_to_baseline(runner)

    failed = criteria["failed"]
    full_pass = criteria["full_release_quality_pass"]

    only_month_stability_failed = (
        failed == ["all_positive_month_rate"]
        or set(failed) == {"all_positive_month_rate"}
    )

    candidate = runner.get("candidate_summary") or {}
    all_s = candidate.get("all") or {}
    train_s = candidate.get("train") or {}
    oos_s = candidate.get("oos") or {}

    candidate_promising = (
        fnum(all_s.get("total_net_bps"), 0) > 10000
        and fnum(all_s.get("profit_factor"), 0) >= 1.30
        and fnum(train_s.get("profit_factor"), 0) >= 1.20
        and fnum(oos_s.get("profit_factor"), 0) >= 1.50
        and fnum(oos_s.get("positive_month_rate"), 0) >= 0.50
        and inum(all_s.get("trade_count")) >= 300
        and inum(oos_s.get("trade_count")) >= 75
    )

    findings = []

    if candidate_promising:
        findings.append({
            "finding_id": "RFC_EVAL_F1_STRONG_PROMISING_CANDIDATE",
            "severity": "HIGH",
            "claim": "Regime-filtered candidate materially improves baseline and passes most quality checks.",
            "evidence": {
                "candidate_all": all_s,
                "candidate_train": train_s,
                "candidate_oos": oos_s,
                "comparison_to_baseline": comparison,
                "passed_checks": criteria["passed"],
                "failed_checks": criteria["failed"],
            },
        })

    if only_month_stability_failed:
        findings.append({
            "finding_id": "RFC_EVAL_F2_MONTH_STABILITY_BLOCKER_ONLY",
            "severity": "HIGH",
            "claim": "The only release blocker is all-period positive month rate.",
            "evidence": {
                "all_positive_month_rate": safe_get(criteria, ["checks", "all_positive_month_rate", "value"]),
                "required": safe_get(criteria, ["checks", "all_positive_month_rate", "required"]),
                "candidate_monthly_total_net_bps": safe_get(all_s, ["monthly_total_net_bps"]),
            },
            "interpretation": "This supports a month-stability repair diagnostic, not release.",
        })

    if not full_pass:
        findings.append({
            "finding_id": "RFC_EVAL_F3_RELEASE_STILL_BLOCKED",
            "severity": "CONTROL",
            "claim": "Candidate does not pass full release criteria.",
            "evidence": {
                "failed_checks": failed,
                "full_release_quality_pass": full_pass,
            },
        })

    if critical:
        evaluator_status = "REGIME_FILTERED_CANDIDATE_EVALUATOR_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_RUNNER_OR_CONTRACT_INPUTS"
        reason = "; ".join(critical)

    elif full_pass:
        evaluator_status = "REGIME_FILTERED_CANDIDATE_EVALUATOR_RELEASE_QUALITY_PREVIEW_PASS"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "RUN_STRICT_RELEASE_GATE_AND_MANUAL_REVIEW_NO_RUNTIME_ACTION"
        reason = "all release-quality preview checks passed"

    elif candidate_promising and only_month_stability_failed:
        evaluator_status = "REGIME_FILTERED_CANDIDATE_EVALUATOR_PROMISING_MONTH_STABILITY_BLOCKED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_MONTH_STABILITY_REPAIR_DIAGNOSTIC_CONTRACT"
        reason = "candidate promising but all_positive_month_rate failed"

    elif candidate_promising:
        evaluator_status = "REGIME_FILTERED_CANDIDATE_EVALUATOR_PROMISING_BUT_BLOCKED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "DIAGNOSE_FAILED_RELEASE_CHECKS"
        reason = f"candidate promising but failed_checks={failed}"

    else:
        evaluator_status = "REGIME_FILTERED_CANDIDATE_EVALUATOR_REJECT_OR_ARCHIVE"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "RECORD_LESSON_OR_QUEUE_NEW_RESEARCH_DIRECTION"
        reason = f"candidate not promising enough; failed_checks={failed}"

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "runner_source": str(RUNNER_LATEST),
        "contract_source": str(CANDIDATE_CONTRACT_LATEST),
        "lesson_checker_source": str(LESSON_CHECKER_LATEST),

        "candidate_key": contract.get("candidate_key"),
        "contract_id": contract.get("contract_id"),
        "candidate_route_hash": contract.get("candidate_route_hash"),

        "candidate_summary": candidate,
        "baseline_summary_old_route_comparison_only": runner.get("baseline_summary_old_route_comparison_only"),
        "comparison_to_baseline": comparison,

        "release_quality_checks": criteria["checks"],
        "passed_checks": criteria["passed"],
        "failed_checks": criteria["failed"],
        "full_release_quality_pass": full_pass,
        "candidate_promising": candidate_promising,
        "only_month_stability_failed": only_month_stability_failed,

        "findings": findings,

        "release_gate_feed": {
            "REGIME_FILTERED_CANDIDATE_EVALUATED": True,
            "REGIME_FILTERED_CANDIDATE_PROMISING": bool(candidate_promising),
            "REGIME_FILTERED_CANDIDATE_FULL_RELEASE_PASS": bool(full_pass),
            "REGIME_FILTERED_CANDIDATE_MONTH_STABILITY_BLOCKED": bool(only_month_stability_failed),
            "status": evaluator_status,
            "candidate_route_hash": contract.get("candidate_route_hash"),
            "release_allowed_from_this_evaluator_alone": False,
        },

        "decision": {
            "candidate_generation_recommended_now": False,
            "candidate_contract_recommended_next": bool(candidate_promising and only_month_stability_failed),
            "family_release_recommended": False,
            "promotion_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "repeat_known_failed_route_recommended": False,
            "next_module": (
                "edge_factory_os_month_stability_repair_contract_builder_v1.py"
                if candidate_promising and only_month_stability_failed
                else None
            ),
            "why_no_action": [
                "evaluator_is_read_only",
                "release_gate_required",
                "all_positive_month_rate_failed",
                "no_runtime_or_capital_action_allowed",
            ],
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

    out_json = RUN_DIR / "regime_filtered_candidate_evaluator_v1_state.json"
    out_md = RUN_DIR / "regime_filtered_candidate_evaluator_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS REGIME FILTERED CANDIDATE EVALUATOR v1

evaluator_status: {evaluator_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

candidate_key: {contract.get("candidate_key")}  
contract_id: {contract.get("contract_id")}  
candidate_route_hash: {contract.get("candidate_route_hash")}

## Candidate Summary

{json.dumps(candidate, indent=2, default=str)[:18000]}

## Comparison To Baseline

{json.dumps(comparison, indent=2, default=str)}

## Release Quality Checks

{json.dumps(criteria["checks"], indent=2, default=str)}

full_release_quality_pass: {full_pass}  
candidate_promising: {candidate_promising}  
only_month_stability_failed: {only_month_stability_failed}  
passed_checks: {criteria["passed"]}  
failed_checks: {criteria["failed"]}

## Release Gate Feed

{json.dumps(result["release_gate_feed"], indent=2, default=str)}

## Findings

{json.dumps(findings, indent=2, default=str)}

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
    print("EDGE FACTORY OS REGIME FILTERED CANDIDATE EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {evaluator_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("SUMMARY")
    print("-" * 100)
    print(f"candidate_route_hash: {contract.get('candidate_route_hash')}")
    print(f"full_release_quality_pass: {full_pass}")
    print(f"candidate_promising: {candidate_promising}")
    print(f"only_month_stability_failed: {only_month_stability_failed}")
    print(f"passed_checks: {criteria['passed']}")
    print(f"failed_checks: {criteria['failed']}")
    print()
    print("COMPARISON TO BASELINE")
    print("-" * 100)
    print(json.dumps(comparison, indent=2, default=str))
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
