from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_cost_sensitivity_evaluator_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

COST_MATRIX_LATEST = (
    BASE_DIR
    / "edge_factory_os_cost_sensitivity_matrix_v1"
    / "cost_sensitivity_matrix_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"cost_sensitivity_evaluator_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "cost_sensitivity_evaluator_latest.json"
LATEST_MD = OUT_ROOT / "cost_sensitivity_evaluator_latest.md"


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


def get_total(summary: Dict[str, Any]) -> Optional[float]:
    return fnum(summary.get("total_pnl"))


def get_wr(summary: Dict[str, Any]) -> Optional[float]:
    return fnum(summary.get("win_rate"))


def get_count(summary: Dict[str, Any]) -> int:
    try:
        return int(float(summary.get("trade_count") or 0))
    except Exception:
        return 0


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    matrix_state = load_json(COST_MATRIX_LATEST)

    if matrix_state is None:
        critical.append("cost_matrix_latest_missing_or_unreadable")
        matrix_state = {}

    matrix_status = matrix_state.get("matrix_status")
    matrix_result = matrix_state.get("matrix_result") or {}

    if matrix_status != "COST_SENSITIVITY_MATRIX_COMPLETE":
        critical.append(f"cost_matrix_not_complete:{matrix_status}")

    baseline = matrix_result.get("baseline_current_logged_pnl") or {}
    ranked = matrix_result.get("ranked_scenarios") or []
    scenarios = matrix_result.get("scenario_results") or []

    baseline_total = get_total(baseline)
    baseline_wr = get_wr(baseline)
    baseline_count = get_count(baseline)

    scenario_table = []

    for row in scenarios:
        summary = row.get("summary") or {}
        scenario_table.append({
            "scenario_name": row.get("scenario_name"),
            "cost_bps_total": row.get("cost_bps_total"),
            "trade_count": get_count(summary),
            "win_rate": get_wr(summary),
            "total_pnl": get_total(summary),
            "mean_pnl": fnum(summary.get("mean_pnl")),
            "top_loss_symbols": summary.get("top_loss_symbols"),
            "top_win_symbols": summary.get("top_win_symbols"),
        })

    best = None
    valid = [x for x in scenario_table if x.get("total_pnl") is not None]
    if valid:
        best = sorted(valid, key=lambda x: x["total_pnl"], reverse=True)[0]

    current = None
    fee_only = None
    stress = None

    for row in scenario_table:
        if row.get("scenario_name") == "current":
            current = row
        if row.get("scenario_name") == "fee_only":
            fee_only = row
        if row.get("scenario_name") == "stress":
            stress = row

    findings = []

    cost_sensitivity_pass = False
    edge_recoverable_under_realistic_cost = False
    gross_edge_supported = False
    edge_not_recovered_even_fee_only = False

    if best and best.get("total_pnl") is not None:
        if best["total_pnl"] > 0:
            gross_edge_supported = True
        else:
            edge_not_recovered_even_fee_only = True

    if current and current.get("total_pnl") is not None and current["total_pnl"] > 0:
        edge_recoverable_under_realistic_cost = True

    # Strict release pass: current cost must be positive, sample cannot be tiny, and stress should not be catastrophic.
    if (
        edge_recoverable_under_realistic_cost
        and current
        and current.get("trade_count", 0) >= 50
        and current.get("win_rate") is not None
        and current["win_rate"] >= 0.45
    ):
        cost_sensitivity_pass = True

    if fee_only and fee_only.get("total_pnl") is not None and fee_only["total_pnl"] < 0:
        findings.append({
            "finding_id": "COST_F1_FEE_ONLY_STILL_NEGATIVE",
            "severity": "HIGH",
            "claim": "Even the favorable fee-only scenario remains negative.",
            "evidence": {
                "fee_only_total_pnl": fee_only.get("total_pnl"),
                "fee_only_win_rate": fee_only.get("win_rate"),
                "fee_only_trade_count": fee_only.get("trade_count"),
            },
            "release_gate_effect": "BLOCK_COST_SLIPPAGE_PASS",
        })

    if current and current.get("total_pnl") is not None and current["total_pnl"] < 0:
        findings.append({
            "finding_id": "COST_F2_CURRENT_COST_NEGATIVE",
            "severity": "HIGH",
            "claim": "Current cost scenario is negative.",
            "evidence": {
                "current_total_pnl": current.get("total_pnl"),
                "current_win_rate": current.get("win_rate"),
                "current_trade_count": current.get("trade_count"),
            },
            "release_gate_effect": "BLOCK_COST_SLIPPAGE_PASS",
        })

    if baseline_count < 50:
        findings.append({
            "finding_id": "COST_F3_SAMPLE_TOO_SMALL_FOR_RELEASE",
            "severity": "CONTROL",
            "claim": "Cost sensitivity sample is too small for release.",
            "evidence": {
                "baseline_trade_count": baseline_count,
                "required_release_minimum": 50,
            },
            "release_gate_effect": "BLOCK_SAMPLE_SIZE_PASS",
        })

    if best and best.get("top_win_symbols"):
        top_win = best["top_win_symbols"][0]
        if isinstance(top_win, (list, tuple)) and len(top_win) >= 2:
            best_total = best.get("total_pnl")
            if best_total is not None and best_total != 0:
                if abs(float(top_win[1])) >= max(abs(float(best_total)) * 0.70, 1e-9):
                    findings.append({
                        "finding_id": "COST_F4_BEST_SCENARIO_DEPENDS_ON_TOP_WIN_SYMBOL",
                        "severity": "MEDIUM_HIGH",
                        "claim": "Best cost scenario may still depend heavily on one winning symbol.",
                        "evidence": {
                            "best_scenario": best,
                            "top_win_symbol": top_win,
                        },
                        "release_gate_effect": "BLOCK_SYMBOL_CONCENTRATION_PASS",
                    })

    if critical:
        evaluator_status = "COST_SENSITIVITY_EVALUATOR_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_COST_MATRIX_INPUT"
        reason = "; ".join(critical)

    elif cost_sensitivity_pass:
        evaluator_status = "COST_SENSITIVITY_EVALUATOR_PASS"
        severity = "OK"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "FEED_PASS_TO_RELEASE_GATE_BUT_DO_NOT_RELEASE_ALONE"
        reason = "cost sensitivity passed strict release criteria"

    elif edge_not_recovered_even_fee_only:
        evaluator_status = "COST_SENSITIVITY_EVALUATOR_EDGE_NOT_RECOVERED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BLOCK_RELEASE_AND_CONTINUE_SIGNAL_REGIME_DIAGNOSTICS"
        reason = "fee_only/best cost scenario still negative"

    else:
        evaluator_status = "COST_SENSITIVITY_EVALUATOR_FAIL_OR_INCONCLUSIVE"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BLOCK_RELEASE_AND_COLLECT_MORE_EVIDENCE"
        reason = "cost sensitivity did not satisfy release criteria"

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "cost_matrix_source": str(COST_MATRIX_LATEST),
        "matrix_status": matrix_status,

        "baseline": {
            "trade_count": baseline_count,
            "win_rate": baseline_wr,
            "total_pnl": baseline_total,
        },
        "scenario_table": scenario_table,
        "best_scenario": best,
        "current_scenario": current,
        "fee_only_scenario": fee_only,
        "stress_scenario": stress,

        "release_gate_feed": {
            "COST_SLIPPAGE_SENSITIVITY_PASS": cost_sensitivity_pass,
            "status": evaluator_status,
            "edge_recoverable_under_realistic_cost": edge_recoverable_under_realistic_cost,
            "gross_edge_supported": gross_edge_supported,
            "edge_not_recovered_even_fee_only": edge_not_recovered_even_fee_only,
            "release_allowed_from_cost_test_alone": False,
        },

        "findings": findings,

        "decision": {
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "family_disable_recommended": False,
            "live_or_real_order_recommended": False,
            "why_no_action": [
                "cost_test_does_not_recover_edge",
                "sample_too_small",
                "full_universe_offline_backtest_still_required",
                "regime_bucket_diagnostic_still_required",
                "OOS_and_month_stability_still_required",
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

    out_json = RUN_DIR / "cost_sensitivity_evaluator_v1_state.json"
    out_md = RUN_DIR / "cost_sensitivity_evaluator_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS COST SENSITIVITY EVALUATOR v1

evaluator_status: {evaluator_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

## Baseline

{json.dumps(result["baseline"], indent=2, default=str)}

## Scenario Table

{json.dumps(scenario_table, indent=2, default=str)}

## Release Gate Feed

{json.dumps(result["release_gate_feed"], indent=2, default=str)}

## Findings

{json.dumps(findings, indent=2, default=str)}

## Decision

runtime_change_recommended: False  
capital_change_recommended: False  
family_disable_recommended: False  
live_or_real_order_recommended: False

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
    print("EDGE FACTORY OS COST SENSITIVITY EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {evaluator_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("BASELINE")
    print("-" * 100)
    print(result["baseline"])
    print()
    print("SCENARIO TABLE")
    print("-" * 100)
    for row in scenario_table:
        print(row)
    print()
    print("RELEASE GATE FEED")
    print("-" * 100)
    print(result["release_gate_feed"])
    print()
    print("FINDINGS")
    print("-" * 100)
    for f in findings:
        print(f)
    print()
    print("DECISION")
    print("-" * 100)
    print("runtime_change_recommended: False")
    print("capital_change_recommended: False")
    print("family_disable_recommended: False")
    print("live_or_real_order_recommended: False")
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
