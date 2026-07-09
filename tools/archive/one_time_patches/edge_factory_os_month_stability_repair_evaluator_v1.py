from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_month_stability_repair_evaluator_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

DIAG_LATEST = (
    BASE_DIR
    / "edge_factory_os_month_stability_repair_diagnostic_v1"
    / "month_stability_repair_diagnostic_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"month_stability_repair_evaluator_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "month_stability_repair_evaluator_latest.json"
LATEST_MD = OUT_ROOT / "month_stability_repair_evaluator_latest.md"

MIN_ACTIVE_MONTHS = 12
MIN_POSITIVE_MONTHS = 11
MIN_POSITIVE_MONTH_RATE = 11 / 12


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


def strict_month_stats(summary: Dict[str, Any]) -> Dict[str, Any]:
    monthly = summary.get("monthly_total_net_bps") or {}

    if not isinstance(monthly, dict):
        monthly = {}

    active_month_count = len(monthly)
    positive_month_count = 0
    negative_month_count = 0
    flat_month_count = 0

    for _, value in monthly.items():
        x = fnum(value, 0.0) or 0.0
        if x > 0:
            positive_month_count += 1
        elif x < 0:
            negative_month_count += 1
        else:
            flat_month_count += 1

    positive_month_rate = positive_month_count / active_month_count if active_month_count else None

    strict_pass = (
        active_month_count >= MIN_ACTIVE_MONTHS
        and positive_month_count >= MIN_POSITIVE_MONTHS
        and positive_month_rate is not None
        and positive_month_rate >= MIN_POSITIVE_MONTH_RATE
    )

    return {
        "active_month_count": active_month_count,
        "positive_month_count": positive_month_count,
        "negative_month_count": negative_month_count,
        "flat_month_count": flat_month_count,
        "positive_month_rate": positive_month_rate,
        "required_active_months": MIN_ACTIVE_MONTHS,
        "required_positive_months": MIN_POSITIVE_MONTHS,
        "required_positive_month_rate": MIN_POSITIVE_MONTH_RATE,
        "strict_11_of_12_month_stability_pass": strict_pass,
        "monthly_total_net_bps": monthly,
    }


def evaluate_filter(row: Dict[str, Any]) -> Dict[str, Any]:
    kept_all = row.get("kept_all") or {}
    kept_train = row.get("kept_train") or {}
    kept_oos = row.get("kept_oos") or {}
    sym = row.get("symbol_concentration") or {}

    strict_month = strict_month_stats(kept_all)

    checks = {
        "strict_year_spread_11_of_12": {
            "pass": strict_month["strict_11_of_12_month_stability_pass"],
            "value": {
                "active_month_count": strict_month["active_month_count"],
                "positive_month_count": strict_month["positive_month_count"],
                "positive_month_rate": strict_month["positive_month_rate"],
            },
            "required": "active_month_count>=12 AND positive_month_count>=11",
        },
        "all_trade_count": {
            "pass": inum(kept_all.get("trade_count")) >= 300,
            "value": kept_all.get("trade_count"),
            "required": ">=300",
        },
        "oos_trade_count": {
            "pass": inum(kept_oos.get("trade_count")) >= 75,
            "value": kept_oos.get("trade_count"),
            "required": ">=75",
        },
        "all_mean_positive": {
            "pass": fnum(kept_all.get("mean_net_bps"), -999999) > 0,
            "value": kept_all.get("mean_net_bps"),
            "required": ">0",
        },
        "train_mean_positive": {
            "pass": fnum(kept_train.get("mean_net_bps"), -999999) > 0,
            "value": kept_train.get("mean_net_bps"),
            "required": ">0",
        },
        "oos_mean_positive": {
            "pass": fnum(kept_oos.get("mean_net_bps"), -999999) > 0,
            "value": kept_oos.get("mean_net_bps"),
            "required": ">0",
        },
        "train_profit_factor": {
            "pass": fnum(kept_train.get("profit_factor"), 0) >= 1.10,
            "value": kept_train.get("profit_factor"),
            "required": ">=1.10",
        },
        "oos_profit_factor": {
            "pass": fnum(kept_oos.get("profit_factor"), 0) >= 1.10,
            "value": kept_oos.get("profit_factor"),
            "required": ">=1.10",
        },
        "oos_positive_month_rate": {
            "pass": fnum(kept_oos.get("positive_month_rate"), 0) >= 0.50,
            "value": kept_oos.get("positive_month_rate"),
            "required": ">=0.50",
        },
        "symbol_concentration": {
            "pass": sym.get("top_symbol_abs_share") is None or fnum(sym.get("top_symbol_abs_share"), 999) <= 0.50,
            "value": sym.get("top_symbol_abs_share"),
            "required": "<=0.50",
        },
    }

    passed = [k for k, v in checks.items() if v.get("pass") is True]
    failed = [k for k, v in checks.items() if v.get("pass") is not True]

    return {
        "filter_name": row.get("filter_name"),
        "strict_month_stats": strict_month,
        "checks": checks,
        "passed_checks": passed,
        "failed_checks": failed,
        "strict_full_quality_pass": len(failed) == 0,
        "kept_all": kept_all,
        "kept_train": kept_train,
        "kept_oos": kept_oos,
        "symbol_concentration": sym,
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    diag = load_json(DIAG_LATEST)

    if not isinstance(diag, dict):
        critical.append("month_stability_repair_diagnostic_latest_missing")
        diag = {}

    if diag.get("diagnostic_status") != "MONTH_STABILITY_REPAIR_DIAGNOSTIC_COMPLETE":
        critical.append(f"diagnostic_not_complete:{diag.get('diagnostic_status')}")

    outputs = diag.get("outputs") or {}
    filter_results_path = outputs.get("filter_results_json")

    all_filters: List[Dict[str, Any]] = []

    if filter_results_path:
        loaded = load_json(Path(str(filter_results_path)))
        if isinstance(loaded, dict) and isinstance(loaded.get("filter_results"), list):
            all_filters = [x for x in loaded["filter_results"] if isinstance(x, dict)]

    if not all_filters:
        top = diag.get("top_filter_results")
        if isinstance(top, list):
            all_filters = [x for x in top if isinstance(x, dict)]

    if not all_filters:
        critical.append("no_filter_results_available")

    evaluated_filters = [evaluate_filter(row) for row in all_filters]
    strict_pass_filters = [r for r in evaluated_filters if r.get("strict_full_quality_pass") is True]

    strict_month_only_filters = [
        r for r in evaluated_filters
        if safe_get(r, ["strict_month_stats", "strict_11_of_12_month_stability_pass"]) is True
    ]

    evaluated_filters.sort(
        key=lambda r: (
            1 if safe_get(r, ["strict_month_stats", "strict_11_of_12_month_stability_pass"]) else 0,
            inum(safe_get(r, ["kept_all", "trade_count"])),
            fnum(safe_get(r, ["kept_all", "total_net_bps"]), -999999),
        ),
        reverse=True,
    )

    best_strict_pass = strict_pass_filters[0] if strict_pass_filters else None
    best_strict_month = strict_month_only_filters[0] if strict_month_only_filters else None
    best_old_preview = diag.get("best_full_quality_preview_filter")

    old_preview_eval = evaluate_filter(best_old_preview) if isinstance(best_old_preview, dict) else None

    if critical:
        evaluator_status = "MONTH_STABILITY_REPAIR_EVALUATOR_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_DIAGNOSTIC_INPUTS"
        reason = "; ".join(critical)

    elif best_strict_pass:
        evaluator_status = "MONTH_STABILITY_REPAIR_EVALUATOR_STRICT_11_OF_12_REPAIR_FOUND"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_STRICT_MONTH_STABILITY_REPAIR_CANDIDATE_CONTRACT_NO_RELEASE"
        reason = f"strict_pass_filter={best_strict_pass.get('filter_name')}"

    elif best_strict_month:
        evaluator_status = "MONTH_STABILITY_REPAIR_EVALUATOR_MONTH_STABLE_BUT_OTHER_CHECKS_FAIL"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "REVIEW_STRICT_MONTH_FILTER_FAILURES_NO_RELEASE"
        reason = f"strict_month_filter_found_but_full_checks_fail={best_strict_month.get('filter_name')}"

    else:
        evaluator_status = "MONTH_STABILITY_REPAIR_EVALUATOR_STRICT_11_OF_12_NOT_FOUND"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "DO_NOT_BUILD_REPAIR_CANDIDATE_CONTRACT_QUEUE_NEW_RESEARCH_OR_STRONGER_FILTERS"
        reason = "no tested pre-outcome repair filter achieved 12 active months and at least 11 positive months"

    findings = []

    if old_preview_eval:
        findings.append({
            "finding_id": "MSRE_F1_OLD_PREVIEW_WAS_TOO_LOOSE",
            "severity": "HIGH",
            "claim": "The previous full-quality preview used a loose positive-month-rate rule and is not valid under strict 11-of-12 month stability.",
            "evidence": {
                "old_filter_name": old_preview_eval.get("filter_name"),
                "strict_month_stats": old_preview_eval.get("strict_month_stats"),
                "old_preview_strict_full_quality_pass": old_preview_eval.get("strict_full_quality_pass"),
                "old_preview_failed_checks_under_strict_rule": old_preview_eval.get("failed_checks"),
            },
        })

    if best_strict_pass:
        findings.append({
            "finding_id": "MSRE_F2_STRICT_REPAIR_FOUND",
            "severity": "ATTENTION",
            "claim": "A tested pre-outcome filter meets strict 11-of-12 month stability and all other preview checks.",
            "evidence": best_strict_pass,
            "interpretation": "Still not release. Requires new contract/hash/full runner/evaluator/release gate.",
        })
    else:
        findings.append({
            "finding_id": "MSRE_F2_NO_STRICT_REPAIR_FOUND",
            "severity": "HIGH",
            "claim": "No tested repair filter meets the strict 1-year spread requirement.",
            "evidence": {
                "tested_filter_count": len(evaluated_filters),
                "strict_month_only_count": len(strict_month_only_filters),
                "strict_full_quality_count": len(strict_pass_filters),
                "best_ranked_filter_under_strict_sort": evaluated_filters[0] if evaluated_filters else None,
            },
        })

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "diagnostic_source": str(DIAG_LATEST),

        "strict_rule": {
            "min_active_months": MIN_ACTIVE_MONTHS,
            "min_positive_months": MIN_POSITIVE_MONTHS,
            "min_positive_month_rate": MIN_POSITIVE_MONTH_RATE,
            "meaning": "A candidate must trade across at least 12 active months and at least 11 of those months must be positive.",
        },

        "tested_filter_count": len(evaluated_filters),
        "strict_month_only_count": len(strict_month_only_filters),
        "strict_full_quality_count": len(strict_pass_filters),

        "best_strict_full_quality_filter": best_strict_pass,
        "best_strict_month_only_filter": best_strict_month,
        "old_best_full_quality_preview_filter_under_strict_rule": old_preview_eval,
        "top_evaluated_filters_under_strict_sort": evaluated_filters[:20],

        "findings": findings,

        "release_gate_feed": {
            "MONTH_STABILITY_REPAIR_EVALUATED_STRICT_11_OF_12": True,
            "STRICT_11_OF_12_REPAIR_FOUND": bool(best_strict_pass),
            "STRICT_MONTH_ONLY_FILTER_FOUND": bool(best_strict_month),
            "RELEASE_PASS_FROM_THIS_EVALUATOR": False,
            "status": evaluator_status,
        },

        "decision": {
            "candidate_generation_recommended_now": False,
            "repair_candidate_contract_recommended": bool(best_strict_pass),
            "family_release_recommended": False,
            "promotion_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "why_no_action": [
                "strict_11_of_12_rule_required",
                "this_evaluator_does_not_release",
                "new_contract_hash_and_full_validation_required_even_if_strict_repair_exists",
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

    out_json = RUN_DIR / "month_stability_repair_evaluator_v1_state.json"
    out_md = RUN_DIR / "month_stability_repair_evaluator_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS MONTH STABILITY REPAIR EVALUATOR v1

evaluator_status: {evaluator_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

## Strict Rule

{json.dumps(result["strict_rule"], indent=2, default=str)}

tested_filter_count: {len(evaluated_filters)}  
strict_month_only_count: {len(strict_month_only_filters)}  
strict_full_quality_count: {len(strict_pass_filters)}

## Old Best Preview Under Strict Rule

{json.dumps(old_preview_eval, indent=2, default=str)[:12000]}

## Best Strict Full Quality Filter

{json.dumps(best_strict_pass, indent=2, default=str)[:12000]}

## Best Strict Month Only Filter

{json.dumps(best_strict_month, indent=2, default=str)[:12000]}

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
    print("EDGE FACTORY OS MONTH STABILITY REPAIR EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {evaluator_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("STRICT RULE")
    print("-" * 100)
    print(result["strict_rule"])
    print()
    print("SUMMARY")
    print("-" * 100)
    print(f"tested_filter_count: {len(evaluated_filters)}")
    print(f"strict_month_only_count: {len(strict_month_only_filters)}")
    print(f"strict_full_quality_count: {len(strict_pass_filters)}")
    print()
    print("OLD BEST PREVIEW UNDER STRICT RULE")
    print("-" * 100)
    print(json.dumps(old_preview_eval, indent=2, default=str)[:5000])
    print()
    print("BEST STRICT FULL QUALITY FILTER")
    print("-" * 100)
    print(json.dumps(best_strict_pass, indent=2, default=str)[:5000])
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
