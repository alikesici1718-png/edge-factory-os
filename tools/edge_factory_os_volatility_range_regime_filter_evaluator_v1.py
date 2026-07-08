from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_volatility_range_regime_filter_evaluator_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

DIAG_LATEST = (
    BASE_DIR
    / "edge_factory_os_volatility_range_regime_filter_diagnostic_v1"
    / "volatility_range_regime_filter_diagnostic_latest.json"
)

CONTRACT_LATEST = (
    BASE_DIR
    / "edge_factory_os_research_direction_contracts"
    / "volatility_range_regime_filter_contract_latest.json"
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
RUN_DIR = OUT_ROOT / f"volatility_range_regime_filter_evaluator_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "volatility_range_regime_filter_evaluator_latest.json"
LATEST_MD = OUT_ROOT / "volatility_range_regime_filter_evaluator_latest.md"


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


def summarize_diag(diag: Dict[str, Any]) -> Dict[str, Any]:
    route = diag.get("route_proxy_used_for_diagnostic_only") or {}
    top_thresholds = diag.get("top_threshold_diagnostics") or []
    interactions = diag.get("interaction_grid") or []

    best_interaction = None
    worst_interaction = None

    valid_interactions = []
    for row in interactions:
        if not isinstance(row, dict):
            continue
        summary = row.get("summary") or {}
        valid_interactions.append(row)

    if valid_interactions:
        best_interaction = sorted(
            valid_interactions,
            key=lambda r: fnum(safe_get(r, ["summary", "total_net_bps"]), -999999),
            reverse=True,
        )[0]
        worst_interaction = sorted(
            valid_interactions,
            key=lambda r: fnum(safe_get(r, ["summary", "total_net_bps"]), 999999),
        )[0]

    top_threshold = top_thresholds[0] if top_thresholds else None

    trade_level_vol_200 = None
    for row in top_thresholds:
        if (
            isinstance(row, dict)
            and row.get("feature") == "std_coin_ret3_bps"
            and fnum(row.get("threshold")) == 200.0
        ):
            trade_level_vol_200 = row
            break

    month_level_vol_200 = None
    for row in top_thresholds:
        if (
            isinstance(row, dict)
            and row.get("feature") == "avg_std_coin_ret3_bps"
            and fnum(row.get("threshold")) == 200.0
        ):
            month_level_vol_200 = row
            break

    return {
        "route": route,
        "top_threshold": top_threshold,
        "month_level_vol_200": month_level_vol_200,
        "trade_level_vol_200": trade_level_vol_200,
        "best_interaction": best_interaction,
        "worst_interaction": worst_interaction,
    }


def classify_strength(summary: Dict[str, Any]) -> Dict[str, Any]:
    best = summary.get("best_interaction") or {}
    worst = summary.get("worst_interaction") or {}
    trade_vol = summary.get("trade_level_vol_200") or {}
    month_vol = summary.get("month_level_vol_200") or {}

    best_s = best.get("summary") or {}
    worst_s = worst.get("summary") or {}

    best_trades = inum(best_s.get("trade_count"))
    best_total = fnum(best_s.get("total_net_bps"), 0.0) or 0.0
    best_wr = fnum(best_s.get("win_rate"), 0.0) or 0.0
    best_pf = fnum(best_s.get("profit_factor"), 0.0) or 0.0

    worst_trades = inum(worst_s.get("trade_count"))
    worst_total = fnum(worst_s.get("total_net_bps"), 0.0) or 0.0
    worst_wr = fnum(worst_s.get("win_rate"), 0.0) or 0.0
    worst_pf = fnum(worst_s.get("profit_factor"), 0.0) or 0.0

    trade_hi = trade_vol.get("trade_hi") or {}
    trade_lo = trade_vol.get("trade_lo") or {}

    vol_hi_total = fnum(trade_hi.get("total_net_bps"), 0.0) or 0.0
    vol_lo_total = fnum(trade_lo.get("total_net_bps"), 0.0) or 0.0
    vol_hi_pf = fnum(trade_hi.get("profit_factor"), 0.0) or 0.0
    vol_lo_pf = fnum(trade_lo.get("profit_factor"), 0.0) or 0.0
    vol_hi_wr = fnum(trade_hi.get("win_rate"), 0.0) or 0.0
    vol_lo_wr = fnum(trade_lo.get("win_rate"), 0.0) or 0.0

    month_hi = month_vol.get("month_hi") or {}
    month_lo = month_vol.get("month_lo") or {}

    month_hi_count = inum(month_hi.get("month_count"))
    month_lo_count = inum(month_lo.get("month_count"))
    month_hi_total = fnum(month_hi.get("total_route_net_bps"), 0.0) or 0.0
    month_lo_total = fnum(month_lo.get("total_route_net_bps"), 0.0) or 0.0
    month_hi_pos = fnum(month_hi.get("positive_month_rate"), 0.0) or 0.0
    month_lo_pos = fnum(month_lo.get("positive_month_rate"), 0.0) or 0.0

    strong_interaction = (
        best_trades >= 250
        and best_total > 10000
        and best_wr >= 0.55
        and best_pf >= 1.50
        and worst_trades >= 100
        and worst_total < -5000
        and worst_pf < 0.80
    )

    strong_trade_vol = (
        vol_hi_total < -10000
        and vol_lo_total > 10000
        and vol_hi_pf < 0.80
        and vol_lo_pf > 1.20
        and vol_lo_wr > vol_hi_wr
    )

    strong_month_vol = (
        month_hi_count >= 2
        and month_lo_count >= 8
        and month_hi_total < 0
        and month_lo_total > 0
        and month_hi_pos < month_lo_pos
    )

    strength_score = 0
    if strong_interaction:
        strength_score += 40
    if strong_trade_vol:
        strength_score += 35
    if strong_month_vol:
        strength_score += 25

    if strength_score >= 80:
        classification = "STRONG_DIAGNOSTIC_SUPPORT_FOR_NEW_CANDIDATE_CONTRACT"
    elif strength_score >= 50:
        classification = "MODERATE_DIAGNOSTIC_SUPPORT_FOR_MORE_RESEARCH"
    else:
        classification = "WEAK_OR_INCONCLUSIVE_DIAGNOSTIC_SUPPORT"

    return {
        "classification": classification,
        "strength_score": strength_score,
        "strong_interaction": strong_interaction,
        "strong_trade_volatility_split": strong_trade_vol,
        "strong_month_volatility_split": strong_month_vol,
        "best_interaction_metrics": {
            "trade_count": best_trades,
            "total_net_bps": best_total,
            "win_rate": best_wr,
            "profit_factor": best_pf,
            "interaction_regime": best.get("interaction_regime"),
        },
        "worst_interaction_metrics": {
            "trade_count": worst_trades,
            "total_net_bps": worst_total,
            "win_rate": worst_wr,
            "profit_factor": worst_pf,
            "interaction_regime": worst.get("interaction_regime"),
        },
        "trade_volatility_split_metrics": {
            "feature": "std_coin_ret3_bps",
            "threshold": 200,
            "hi_total_net_bps": vol_hi_total,
            "lo_total_net_bps": vol_lo_total,
            "hi_profit_factor": vol_hi_pf,
            "lo_profit_factor": vol_lo_pf,
            "hi_win_rate": vol_hi_wr,
            "lo_win_rate": vol_lo_wr,
        },
        "month_volatility_split_metrics": {
            "feature": "avg_std_coin_ret3_bps",
            "threshold": 200,
            "hi_month_count": month_hi_count,
            "lo_month_count": month_lo_count,
            "hi_total_route_net_bps": month_hi_total,
            "lo_total_route_net_bps": month_lo_total,
            "hi_positive_month_rate": month_hi_pos,
            "lo_positive_month_rate": month_lo_pos,
        },
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    diag = load_json(DIAG_LATEST)
    contract = load_json(CONTRACT_LATEST)
    lesson_checker = load_json(LESSON_CHECKER_LATEST)
    release_gate = load_json(RELEASE_GATE_V4_LATEST)

    if diag is None:
        critical.append("volatility_range_regime_diagnostic_latest_missing")
        diag = {}

    if contract is None:
        critical.append("volatility_range_regime_contract_latest_missing")
        contract = {}

    if lesson_checker is None:
        attention.append("lesson_checker_latest_missing")
        lesson_checker = {}

    if release_gate is None:
        attention.append("release_gate_v4_latest_missing")
        release_gate = {}

    if diag.get("diagnostic_status") != "VOLATILITY_RANGE_REGIME_FILTER_DIAGNOSTIC_COMPLETE":
        critical.append(f"diagnostic_not_complete:{diag.get('diagnostic_status')}")

    if contract.get("research_key") != "VOLATILITY_RANGE_REGIME_FILTER_DIAGNOSTIC_V1":
        critical.append(f"unexpected_contract_key:{contract.get('research_key')}")

    if safe_get(contract, ["experiment_design", "diagnostic_only"]) is not True:
        critical.append("contract_not_diagnostic_only")

    if safe_get(contract, ["experiment_design", "candidate_generation_allowed_now"]) is not False:
        critical.append("contract_allows_candidate_generation")

    if safe_get(contract, ["blocked_route_guard", "repeat_same_route_allowed"]) is not False:
        critical.append("contract_allows_blocked_route_repeat")

    diag_summary = summarize_diag(diag)
    strength = classify_strength(diag_summary)

    findings = []

    if strength.get("strong_interaction"):
        findings.append({
            "finding_id": "VRRE_F1_STRONG_INTERACTION_SPLIT",
            "severity": "HIGH",
            "claim": "Volatility/range/liquidity interaction strongly separates good and bad route outcomes.",
            "evidence": {
                "best_interaction": strength.get("best_interaction_metrics"),
                "worst_interaction": strength.get("worst_interaction_metrics"),
            },
            "interpretation": "This supports a new candidate-contract proposal, not a live/runtime change.",
        })

    if strength.get("strong_trade_volatility_split"):
        findings.append({
            "finding_id": "VRRE_F2_TRADE_LEVEL_VOLATILITY_SPLIT",
            "severity": "HIGH",
            "claim": "Trade-level cross-sectional volatility split strongly separates outcomes.",
            "evidence": strength.get("trade_volatility_split_metrics"),
            "interpretation": "High std_coin_ret3_bps is adverse; low side is materially better.",
        })

    if strength.get("strong_month_volatility_split"):
        findings.append({
            "finding_id": "VRRE_F3_MONTH_LEVEL_VOLATILITY_SPLIT",
            "severity": "HIGH",
            "claim": "Month-level cross-sectional volatility split explains major bad months.",
            "evidence": strength.get("month_volatility_split_metrics"),
            "interpretation": "This explains month instability but does not pass release by itself.",
        })

    findings.append({
        "finding_id": "VRRE_F4_NO_DIRECT_RELEASE_OR_RUNTIME_ACTION",
        "severity": "CONTROL",
        "claim": "Diagnostic evidence cannot directly release a family or patch runtime.",
        "evidence": {
            "contract_diagnostic_only": safe_get(contract, ["experiment_design", "diagnostic_only"]),
            "candidate_generation_allowed_now": safe_get(contract, ["experiment_design", "candidate_generation_allowed_now"]),
            "family_release_allowed_now": safe_get(contract, ["experiment_design", "family_release_allowed_now"]),
            "repeat_same_route_allowed": safe_get(contract, ["blocked_route_guard", "repeat_same_route_allowed"]),
            "known_failed_route_status": lesson_checker.get("checker_status"),
        },
    })

    new_candidate_contract_recommended = (
        strength.get("classification") == "STRONG_DIAGNOSTIC_SUPPORT_FOR_NEW_CANDIDATE_CONTRACT"
    )

    if critical:
        evaluator_status = "VOLATILITY_RANGE_REGIME_EVALUATOR_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_DIAGNOSTIC_OR_CONTRACT_INPUT"
        reason = "; ".join(critical)

    elif new_candidate_contract_recommended:
        evaluator_status = "VOLATILITY_RANGE_REGIME_EVALUATOR_NEW_CANDIDATE_CONTRACT_RECOMMENDED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_REGIME_FILTER_CANDIDATE_CONTRACT_NO_RUNTIME_ACTION"
        reason = (
            f"classification={strength.get('classification')}; "
            f"strength_score={strength.get('strength_score')}; "
            "diagnostic_support_strong_but_release_still_blocked"
        )

    else:
        evaluator_status = "VOLATILITY_RANGE_REGIME_EVALUATOR_MORE_DIAGNOSTIC_REQUIRED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "ARCHIVE_OR_COLLECT_MORE_DIAGNOSTIC_EVIDENCE"
        reason = f"classification={strength.get('classification')}; strength_score={strength.get('strength_score')}"

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "diagnostic_source": str(DIAG_LATEST),
        "contract_source": str(CONTRACT_LATEST),
        "lesson_checker_source": str(LESSON_CHECKER_LATEST),
        "release_gate_v4_source": str(RELEASE_GATE_V4_LATEST),

        "diagnostic_status": diag.get("diagnostic_status"),
        "contract_id": contract.get("contract_id"),
        "research_key": contract.get("research_key"),

        "diagnostic_summary": diag_summary,
        "strength_classification": strength,

        "findings": findings,

        "new_candidate_contract_recommendation": {
            "new_candidate_contract_recommended": new_candidate_contract_recommended,
            "recommended_contract_key": "REGIME_FILTERED_IMPULSE_ROUTE_CANDIDATE_CONTRACT_V1" if new_candidate_contract_recommended else None,
            "recommended_contract_purpose": (
                "Create a new offline-only candidate contract using volatility/range/liquidity regime features as a pre-outcome filter, "
                "while treating the old ret3 threshold route as blocked unless materially modified and fully revalidated."
                if new_candidate_contract_recommended
                else None
            ),
            "candidate_generation_allowed_now": False,
            "family_release_allowed_now": False,
            "runtime_or_capital_action_allowed_now": False,
            "must_pass_future_gates": [
                "lesson_memory_new_route_hash_not_blocked",
                "full_universe_offline_backtest",
                "train_oos_validation",
                "month_stability",
                "cost_slippage_sensitivity",
                "symbol_concentration_risk",
                "release_gate",
            ],
        },

        "release_gate_feed": {
            "VOLATILITY_RANGE_REGIME_DIAGNOSTIC_RAN": True,
            "VOLATILITY_RANGE_REGIME_DIAGNOSTIC_STRONG": bool(new_candidate_contract_recommended),
            "NEW_CANDIDATE_CONTRACT_RECOMMENDED": bool(new_candidate_contract_recommended),
            "RELEASE_PASS_FROM_THIS_DIAGNOSTIC": False,
            "status": evaluator_status,
        },

        "decision": {
            "candidate_generation_recommended_now": False,
            "candidate_contract_recommended": bool(new_candidate_contract_recommended),
            "family_release_recommended": False,
            "promotion_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "repeat_same_route_recommended": False,
            "why_no_action": [
                "diagnostic_only_contract",
                "known_failed_route_cannot_be_released",
                "new_candidate_contract_required_before candidate generation",
                "full_release_gate_required",
                "no runtime_or_capital_action_allowed",
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

    out_json = RUN_DIR / "volatility_range_regime_filter_evaluator_v1_state.json"
    out_md = RUN_DIR / "volatility_range_regime_filter_evaluator_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS VOLATILITY RANGE REGIME FILTER EVALUATOR v1

evaluator_status: {evaluator_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

## Strength Classification

{json.dumps(strength, indent=2, default=str)}

## New Candidate Contract Recommendation

{json.dumps(result["new_candidate_contract_recommendation"], indent=2, default=str)}

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
    print("EDGE FACTORY OS VOLATILITY RANGE REGIME FILTER EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {evaluator_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("STRENGTH CLASSIFICATION")
    print("-" * 100)
    print(json.dumps(strength, indent=2, default=str))
    print()
    print("NEW CANDIDATE CONTRACT RECOMMENDATION")
    print("-" * 100)
    print(json.dumps(result["new_candidate_contract_recommendation"], indent=2, default=str))
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
