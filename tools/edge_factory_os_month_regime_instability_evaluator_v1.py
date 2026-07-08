from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_month_regime_instability_evaluator_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

DIAG_LATEST = (
    BASE_DIR
    / "edge_factory_os_month_regime_instability_diagnostic_v1"
    / "month_regime_instability_diagnostic_latest.json"
)

RELEASE_GATE_V4_LATEST = (
    BASE_DIR
    / "edge_factory_os_family_candidate_release_gate_v4"
    / "family_candidate_release_gate_v4_latest.json"
)

LESSON_CHECKER_LATEST = (
    BASE_DIR
    / "edge_factory_os_lesson_memory_checker_v1"
    / "lesson_memory_checker_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"month_regime_instability_evaluator_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "month_regime_instability_evaluator_latest.json"
LATEST_MD = OUT_ROOT / "month_regime_instability_evaluator_latest.md"


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


def safe_get(d: Dict[str, Any], path: List[str], default=None):
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def extract_top_bucket(diag: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    buckets = diag.get("explanatory_buckets_top_20")
    if isinstance(buckets, list) and buckets:
        return buckets[0]
    return None


def extract_top_feature_diff(diag: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    diffs = diag.get("feature_diff_top_20")
    if isinstance(diffs, list) and diffs:
        return diffs[0]
    return None


def classify_bucket(bucket: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(bucket, dict):
        return {
            "bucket_signal_found": False,
            "classification": "NO_BUCKET",
            "reason": "no explanatory bucket available",
        }

    hi_month_count = int(bucket.get("hi_month_count") or 0)
    lo_month_count = int(bucket.get("lo_month_count") or 0)
    hi_total = fnum(bucket.get("hi_total_route_net_bps"), 0.0) or 0.0
    lo_total = fnum(bucket.get("lo_total_route_net_bps"), 0.0) or 0.0
    hi_pos = fnum(bucket.get("hi_positive_month_rate"))
    lo_pos = fnum(bucket.get("lo_positive_month_rate"))

    high_side_bad = (
        hi_month_count >= 2
        and lo_month_count >= 5
        and hi_total < 0
        and lo_total > 0
        and hi_pos is not None
        and lo_pos is not None
        and hi_pos < lo_pos
    )

    low_side_bad = (
        lo_month_count >= 2
        and hi_month_count >= 5
        and lo_total < 0
        and hi_total > 0
        and hi_pos is not None
        and lo_pos is not None
        and lo_pos < hi_pos
    )

    if high_side_bad:
        classification = "HIGH_SIDE_BAD_REGIME_SIGNAL"
        direction = "avoid_or_explain_high_side"
    elif low_side_bad:
        classification = "LOW_SIDE_BAD_REGIME_SIGNAL"
        direction = "avoid_or_explain_low_side"
    else:
        classification = "WEAK_OR_UNBALANCED_BUCKET_SIGNAL"
        direction = "diagnostic_only"

    return {
        "bucket_signal_found": high_side_bad or low_side_bad,
        "classification": classification,
        "direction": direction,
        "feature": bucket.get("feature"),
        "threshold": bucket.get("threshold"),
        "hi_month_count": hi_month_count,
        "lo_month_count": lo_month_count,
        "hi_total_route_net_bps": hi_total,
        "lo_total_route_net_bps": lo_total,
        "hi_positive_month_rate": hi_pos,
        "lo_positive_month_rate": lo_pos,
        "diagnostic_score": bucket.get("diagnostic_score"),
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    diag = load_json(DIAG_LATEST)
    release_gate = load_json(RELEASE_GATE_V4_LATEST)
    lesson_checker = load_json(LESSON_CHECKER_LATEST)

    if diag is None:
        critical.append("month_regime_diagnostic_latest_missing")
        diag = {}

    if release_gate is None:
        attention.append("release_gate_v4_latest_missing")
        release_gate = {}

    if lesson_checker is None:
        attention.append("lesson_checker_latest_missing")
        lesson_checker = {}

    diagnostic_status = diag.get("diagnostic_status")
    if diagnostic_status != "MONTH_REGIME_INSTABILITY_DIAGNOSTIC_COMPLETE":
        critical.append(f"month_regime_diagnostic_not_complete:{diagnostic_status}")

    blocked_route = diag.get("blocked_route_reference") or {}
    if blocked_route.get("route_blocked_by_lesson_memory") is not True:
        critical.append("blocked_route_not_confirmed_in_diagnostic")

    if blocked_route.get("repeat_same_route_allowed") is not False:
        critical.append("repeat_same_route_not_blocked")

    if blocked_route.get("candidate_generation_allowed_from_this_contract") is not False:
        critical.append("diagnostic_contract_allows_candidate_generation_unexpectedly")

    month_summary = diag.get("month_summary") or {}
    good_count = int(month_summary.get("good_month_count") or 0)
    bad_count = int(month_summary.get("bad_month_count") or 0)
    month_count = int(month_summary.get("month_count") or 0)

    route_proxy = diag.get("route_proxy_used_for_diagnostic_only") or {}
    route_trade_count = int(route_proxy.get("route_trade_count") or 0)
    route_total = fnum(route_proxy.get("route_total_net_bps"))
    route_win_rate = fnum(route_proxy.get("route_win_rate"))

    top_bucket = extract_top_bucket(diag)
    top_feature_diff = extract_top_feature_diff(diag)
    bucket_classification = classify_bucket(top_bucket)

    findings = []

    if month_count >= 12 and good_count > 0 and bad_count > 0:
        findings.append({
            "finding_id": "MRIE_F1_MONTH_INSTABILITY_CONFIRMED",
            "severity": "HIGH",
            "claim": "The blocked route has material month-to-month instability.",
            "evidence": {
                "month_count": month_count,
                "good_month_count": good_count,
                "bad_month_count": bad_count,
                "route_trade_count": route_trade_count,
                "route_total_net_bps": route_total,
                "route_win_rate": route_win_rate,
            },
        })

    if bucket_classification.get("bucket_signal_found"):
        findings.append({
            "finding_id": "MRIE_F2_EXPLANATORY_REGIME_BUCKET_FOUND",
            "severity": "HIGH",
            "claim": "A market/regime bucket appears to explain a major part of blocked-route instability.",
            "evidence": bucket_classification,
            "interpretation": "This is evidence for a new diagnostic/feature contract, not a release filter.",
        })

    if isinstance(top_feature_diff, dict):
        findings.append({
            "finding_id": "MRIE_F3_GOOD_BAD_MONTH_FEATURE_DIFFERENCE_FOUND",
            "severity": "MEDIUM_HIGH",
            "claim": "Good and bad months differ on measurable pre-outcome features.",
            "evidence": top_feature_diff,
            "interpretation": "Feature differences can seed a new contract but cannot release a family.",
        })

    findings.append({
        "finding_id": "MRIE_F4_BLOCKED_ROUTE_REMAINS_CLOSED",
        "severity": "CONTROL",
        "claim": "The evaluation does not reopen the known failed route.",
        "evidence": {
            "route_hash": blocked_route.get("route_hash"),
            "route_blocked_by_lesson_memory": blocked_route.get("route_blocked_by_lesson_memory"),
            "repeat_same_route_allowed": blocked_route.get("repeat_same_route_allowed"),
            "candidate_generation_allowed_from_this_contract": blocked_route.get("candidate_generation_allowed_from_this_contract"),
        },
    })

    strong_new_contract_signal = (
        bucket_classification.get("bucket_signal_found") is True
        and month_count >= 12
        and good_count >= 3
        and bad_count >= 3
        and route_trade_count >= 300
    )

    if critical:
        evaluator_status = "MONTH_REGIME_INSTABILITY_EVALUATOR_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_DIAGNOSTIC_INPUT"
        reason = "; ".join(critical)

        new_contract_recommended = False

    elif strong_new_contract_signal:
        evaluator_status = "MONTH_REGIME_INSTABILITY_EVALUATOR_NEW_CONTRACT_RECOMMENDED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_VOLATILITY_RANGE_REGIME_RESEARCH_CONTRACT_DO_NOT_RELEASE"
        reason = (
            f"explanatory_bucket={bucket_classification.get('feature')}>={bucket_classification.get('threshold')}; "
            f"month_count={month_count}; route_trade_count={route_trade_count}"
        )

        new_contract_recommended = True

    else:
        evaluator_status = "MONTH_REGIME_INSTABILITY_EVALUATOR_DIAGNOSTIC_ONLY_INCONCLUSIVE"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "ARCHIVE_OR_COLLECT_MORE_FEATURES_BEFORE_NEW_CONTRACT"
        reason = "diagnostic evidence not strong enough for a new contract"

        new_contract_recommended = False

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "diagnostic_source": str(DIAG_LATEST),
        "release_gate_v4_source": str(RELEASE_GATE_V4_LATEST),
        "lesson_checker_source": str(LESSON_CHECKER_LATEST),

        "diagnostic_status": diagnostic_status,
        "month_summary_compact": {
            "month_count": month_count,
            "good_month_count": good_count,
            "bad_month_count": bad_count,
            "route_trade_count": route_trade_count,
            "route_total_net_bps": route_total,
            "route_win_rate": route_win_rate,
        },

        "top_explanatory_bucket": top_bucket,
        "top_bucket_classification": bucket_classification,
        "top_feature_difference": top_feature_diff,

        "findings": findings,

        "new_contract_recommendation": {
            "new_contract_recommended": new_contract_recommended,
            "recommended_contract_key": "VOLATILITY_RANGE_REGIME_FILTER_DIAGNOSTIC_V1" if new_contract_recommended else None,
            "recommended_contract_purpose": (
                "Test whether cross-sectional volatility/range/liquidity regime features can explain or avoid bad months "
                "without reopening the blocked ret3 threshold route."
                if new_contract_recommended
                else None
            ),
            "candidate_generation_allowed_now": False,
            "family_release_allowed_now": False,
            "must_not_reopen_blocked_route": True,
            "must_use_full_universe_panel": True,
        },

        "release_gate_feed": {
            "MONTH_REGIME_INSTABILITY_DIAGNOSTIC_RAN": True,
            "MONTH_REGIME_INSTABILITY_EXPLANATORY_SIGNAL_FOUND": bool(bucket_classification.get("bucket_signal_found")),
            "NEW_RESEARCH_CONTRACT_RECOMMENDED": new_contract_recommended,
            "RELEASE_PASS_FROM_THIS_DIAGNOSTIC": False,
            "status": evaluator_status,
        },

        "decision": {
            "candidate_generation_recommended_now": False,
            "family_release_recommended": False,
            "promotion_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "repeat_same_route_recommended": False,
            "why_no_action": [
                "diagnostic_only",
                "blocked_route_known_failure",
                "new_contract_needed_before any candidate generation",
                "release_gate_still_required",
                "explanatory_bucket_is_not_a_release_filter",
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

    out_json = RUN_DIR / "month_regime_instability_evaluator_v1_state.json"
    out_md = RUN_DIR / "month_regime_instability_evaluator_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS MONTH REGIME INSTABILITY EVALUATOR v1

evaluator_status: {evaluator_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

## Month Summary

{json.dumps(result["month_summary_compact"], indent=2, default=str)}

## Top Explanatory Bucket

{json.dumps(top_bucket, indent=2, default=str)}

## Bucket Classification

{json.dumps(bucket_classification, indent=2, default=str)}

## New Contract Recommendation

{json.dumps(result["new_contract_recommendation"], indent=2, default=str)}

## Release Gate Feed

{json.dumps(result["release_gate_feed"], indent=2, default=str)}

## Findings

{json.dumps(findings, indent=2, default=str)}

## Decision

candidate_generation_recommended_now: False  
family_release_recommended: False  
promotion_recommended: False  
runtime_change_recommended: False  
capital_change_recommended: False  
repeat_same_route_recommended: False

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
    print("EDGE FACTORY OS MONTH REGIME INSTABILITY EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {evaluator_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("MONTH SUMMARY")
    print("-" * 100)
    print(result["month_summary_compact"])
    print()
    print("TOP EXPLANATORY BUCKET")
    print("-" * 100)
    print(top_bucket)
    print()
    print("BUCKET CLASSIFICATION")
    print("-" * 100)
    print(bucket_classification)
    print()
    print("NEW CONTRACT RECOMMENDATION")
    print("-" * 100)
    print(result["new_contract_recommendation"])
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
