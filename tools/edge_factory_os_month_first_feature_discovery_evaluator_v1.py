from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_month_first_feature_discovery_evaluator_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

RUNNER_LATEST = (
    BASE_DIR
    / "edge_factory_os_month_first_feature_discovery_runner_v1"
    / "month_first_feature_discovery_runner_latest.json"
)

CONTRACT_LATEST = (
    BASE_DIR
    / "edge_factory_os_research_direction_contracts"
    / "month_first_feature_discovery_contract_latest.json"
)

STRICT_POLICY_LATEST = (
    BASE_DIR
    / "edge_factory_os_policy_guards"
    / "strict_month_stability_policy_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"month_first_feature_discovery_evaluator_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "month_first_feature_discovery_evaluator_latest.json"
LATEST_MD = OUT_ROOT / "month_first_feature_discovery_evaluator_latest.md"


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


def score_feature_candidate(row: Dict[str, Any]) -> Dict[str, Any]:
    selected_month_count = inum(row.get("selected_month_count"))
    selected_pos_rate = fnum(row.get("selected_positive_month_rate"), None)
    selected_mean = fnum(row.get("selected_mean_label"), None)
    excluded_mean = fnum(row.get("excluded_mean_label"), None)
    sep = fnum(row.get("separation_score"), 0.0) or 0.0

    # Diagnostic strength: separation matters, but tiny month groups are not enough.
    month_sample_ok = selected_month_count >= 6
    tiny_sample = selected_month_count < 6

    # A feature can be useful either as a "good regime" selector or "bad regime" avoider.
    good_regime_signal = (
        selected_pos_rate is not None
        and selected_pos_rate >= 0.70
        and selected_mean is not None
        and selected_mean > 0
        and selected_month_count >= 4
    )

    bad_regime_signal = (
        selected_pos_rate is not None
        and selected_pos_rate <= 0.20
        and selected_mean is not None
        and selected_mean < 0
        and excluded_mean is not None
        and excluded_mean > selected_mean
        and selected_month_count >= 6
    )

    strong_separation = sep >= 120
    moderate_separation = sep >= 80

    diagnostic_score = 0.0
    diagnostic_score += min(sep, 250.0)
    diagnostic_score += 30 if month_sample_ok else 0
    diagnostic_score -= 35 if tiny_sample else 0
    diagnostic_score += 40 if good_regime_signal else 0
    diagnostic_score += 30 if bad_regime_signal else 0

    if strong_separation and (good_regime_signal or bad_regime_signal):
        classification = "FEATURE_DIAGNOSTIC_SIGNAL_STRONG"
    elif moderate_separation:
        classification = "FEATURE_DIAGNOSTIC_SIGNAL_MODERATE"
    else:
        classification = "FEATURE_DIAGNOSTIC_SIGNAL_WEAK"

    return {
        "feature": row.get("feature"),
        "label": row.get("label"),
        "threshold": row.get("threshold"),
        "direction": row.get("direction"),
        "selected_month_count": selected_month_count,
        "selected_positive_month_rate": selected_pos_rate,
        "selected_mean_label": selected_mean,
        "excluded_mean_label": excluded_mean,
        "separation_score": sep,
        "month_sample_ok": month_sample_ok,
        "tiny_sample": tiny_sample,
        "good_regime_signal": good_regime_signal,
        "bad_regime_signal": bad_regime_signal,
        "classification": classification,
        "diagnostic_score": diagnostic_score,
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    runner = load_json(RUNNER_LATEST)
    contract = load_json(CONTRACT_LATEST)
    strict_policy = load_json(STRICT_POLICY_LATEST)

    if not isinstance(runner, dict):
        critical.append("month_first_feature_discovery_runner_latest_missing")
        runner = {}

    if not isinstance(contract, dict):
        critical.append("month_first_feature_discovery_contract_latest_missing")
        contract = {}

    if not isinstance(strict_policy, dict):
        attention.append("strict_month_policy_latest_missing")
        strict_policy = {}

    if runner.get("runner_status") != "MONTH_FIRST_FEATURE_DISCOVERY_RUNNER_COMPLETE":
        critical.append(f"runner_not_complete:{runner.get('runner_status')}")

    if contract.get("research_key") != "MONTH_FIRST_FEATURE_DISCOVERY_V1":
        critical.append(f"unexpected_contract_key:{contract.get('research_key')}")

    if safe_get(runner, ["release_gate_feed", "RELEASE_PASS_FROM_THIS_RUNNER"]) is not False:
        critical.append("runner_claimed_release_pass_unexpectedly")

    top_candidates = runner.get("top_feature_candidates")
    if not isinstance(top_candidates, list):
        top_candidates = []

    if not top_candidates:
        critical.append("top_feature_candidates_missing")

    scored = [score_feature_candidate(x) for x in top_candidates if isinstance(x, dict)]
    scored.sort(key=lambda x: x["diagnostic_score"], reverse=True)

    strong = [x for x in scored if x["classification"] == "FEATURE_DIAGNOSTIC_SIGNAL_STRONG"]
    moderate = [x for x in scored if x["classification"] == "FEATURE_DIAGNOSTIC_SIGNAL_MODERATE"]
    good_regime = [x for x in scored if x["good_regime_signal"]]
    bad_regime = [x for x in scored if x["bad_regime_signal"]]
    tiny_sample_top = [x for x in scored[:10] if x["tiny_sample"]]

    month_count = inum(safe_get(runner, ["month_feature_table_summary", "month_count"]))
    feature_count = inum(safe_get(runner, ["month_feature_table_summary", "feature_count"]))
    ranked_feature_count = len(runner.get("top_feature_rankings") or [])

    findings = []

    findings.append({
        "finding_id": "MFFD_EVAL_F1_FEATURE_TABLE_AND_RANKINGS_READY",
        "severity": "INFO",
        "claim": "Month-first feature discovery produced a usable diagnostic table and feature rankings.",
        "evidence": {
            "month_count": month_count,
            "feature_count": feature_count,
            "ranked_feature_count": ranked_feature_count,
            "outputs": runner.get("outputs"),
        },
    })

    if strong:
        findings.append({
            "finding_id": "MFFD_EVAL_F2_STRONG_DIAGNOSTIC_FEATURE_SIGNAL_FOUND",
            "severity": "ATTENTION",
            "claim": "Some pre-outcome features show strong diagnostic separation across months.",
            "evidence": {
                "strong_count": len(strong),
                "top_strong": strong[:10],
            },
            "interpretation": "This can justify a feature-conditioned research contract, not a candidate or release.",
        })
    elif moderate:
        findings.append({
            "finding_id": "MFFD_EVAL_F2_MODERATE_DIAGNOSTIC_FEATURE_SIGNAL_FOUND",
            "severity": "ATTENTION",
            "claim": "Feature rankings show moderate diagnostic separation, but not enough for candidate construction.",
            "evidence": {
                "moderate_count": len(moderate),
                "top_moderate": moderate[:10],
            },
            "interpretation": "Broader feature engine or more robust month labels are needed before candidate contracts.",
        })
    else:
        findings.append({
            "finding_id": "MFFD_EVAL_F2_FEATURE_SIGNAL_WEAK",
            "severity": "ATTENTION",
            "claim": "No sufficiently strong diagnostic feature signal was found.",
            "evidence": {
                "top_scored": scored[:10],
            },
        })

    if tiny_sample_top:
        findings.append({
            "finding_id": "MFFD_EVAL_F3_TOP_FEATURES_HAVE_SMALL_MONTH_SAMPLE_RISK",
            "severity": "HIGH",
            "claim": "Some top-ranked feature separations rely on very small month subsets.",
            "evidence": {
                "tiny_sample_top": tiny_sample_top,
            },
            "interpretation": "Small month subsets cannot become release or candidate filters without a new contract and full validation.",
        })

    findings.append({
        "finding_id": "MFFD_EVAL_F4_DIAGNOSTIC_LABELS_NOT_LIVE_FEATURES",
        "severity": "CONTROL",
        "claim": "The outcome labels are diagnostic only and cannot be used as live/paper features.",
        "evidence": {
            "diagnostic_label_columns": safe_get(runner, ["month_feature_table_summary", "diagnostic_label_columns"]),
        },
    })

    feature_conditioned_contract_recommended = bool(strong)
    broader_feature_engine_recommended = not bool(strong)

    if critical:
        evaluator_status = "MONTH_FIRST_FEATURE_DISCOVERY_EVALUATOR_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_RUNNER_OR_CONTRACT_INPUT"
        reason = "; ".join(critical)

    elif feature_conditioned_contract_recommended:
        evaluator_status = "MONTH_FIRST_FEATURE_DISCOVERY_EVALUATOR_FEATURE_CONTRACT_RECOMMENDED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_FEATURE_CONDITIONED_RESEARCH_CONTRACT_NO_CANDIDATE"
        reason = f"strong_feature_signal_count={len(strong)}; candidate_generation_still_blocked"

    else:
        evaluator_status = "MONTH_FIRST_FEATURE_DISCOVERY_EVALUATOR_BROADER_FEATURE_ENGINE_RECOMMENDED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_BROADER_MONTH_FEATURE_ENGINE_OR_EXPAND_FEATURE_DISCOVERY"
        reason = f"strong_feature_signal_count=0; moderate_feature_signal_count={len(moderate)}"

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "runner_source": str(RUNNER_LATEST),
        "contract_source": str(CONTRACT_LATEST),
        "strict_policy_source": str(STRICT_POLICY_LATEST),

        "runner_summary": {
            "runner_status": runner.get("runner_status"),
            "month_count": month_count,
            "feature_count": feature_count,
            "ranked_feature_count": ranked_feature_count,
            "release_gate_feed": runner.get("release_gate_feed"),
        },

        "strict_month_policy": {
            "policy_key": strict_policy.get("policy_key"),
            "min_active_months": safe_get(strict_policy, ["release_requirement", "min_active_months"], 12),
            "min_positive_months": safe_get(strict_policy, ["release_requirement", "min_positive_months"], 11),
            "min_positive_month_rate": safe_get(strict_policy, ["release_requirement", "min_positive_month_rate"], 11 / 12),
            "loose_055_month_rate_deprecated_for_release": safe_get(
                strict_policy,
                ["explicitly_deprecated_for_release", "positive_month_rate_gte_0_55_only"],
                True,
            ),
        },

        "feature_signal_summary": {
            "scored_candidate_count": len(scored),
            "strong_signal_count": len(strong),
            "moderate_signal_count": len(moderate),
            "good_regime_signal_count": len(good_regime),
            "bad_regime_signal_count": len(bad_regime),
            "tiny_sample_top_count": len(tiny_sample_top),
            "top_scored_features": scored[:20],
            "top_good_regime_features": good_regime[:10],
            "top_bad_regime_features": bad_regime[:10],
        },

        "findings": findings,

        "release_gate_feed": {
            "MONTH_FIRST_FEATURE_DISCOVERY_EVALUATED": True,
            "STRONG_FEATURE_DIAGNOSTIC_SIGNAL_FOUND": bool(strong),
            "FEATURE_CONDITIONED_RESEARCH_CONTRACT_RECOMMENDED": feature_conditioned_contract_recommended,
            "BROADER_FEATURE_ENGINE_RECOMMENDED": broader_feature_engine_recommended,
            "RELEASE_PASS_FROM_THIS_EVALUATOR": False,
            "status": evaluator_status,
        },

        "decision": {
            "candidate_generation_recommended_now": False,
            "candidate_contract_recommended_now": False,
            "feature_conditioned_research_contract_recommended": feature_conditioned_contract_recommended,
            "broader_feature_engine_recommended": broader_feature_engine_recommended,
            "family_release_recommended": False,
            "promotion_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "repeat_blocked_routes_recommended": False,
            "next_module": (
                "edge_factory_os_feature_conditioned_research_contract_builder_v1.py"
                if feature_conditioned_contract_recommended
                else "edge_factory_os_broader_month_feature_engine_contract_builder_v1.py"
            ),
            "why_no_action": [
                "feature_discovery_evaluator_is_read_only",
                "diagnostic_labels_are_not_live_features",
                "feature_conditioned_contract_required_before candidate generation",
                "strict_month_policy_required",
                "release_gate_required",
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

    out_json = RUN_DIR / "month_first_feature_discovery_evaluator_v1_state.json"
    out_md = RUN_DIR / "month_first_feature_discovery_evaluator_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS MONTH FIRST FEATURE DISCOVERY EVALUATOR v1

evaluator_status: {evaluator_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

## Runner Summary

{json.dumps(result["runner_summary"], indent=2, default=str)}

## Strict Month Policy

{json.dumps(result["strict_month_policy"], indent=2, default=str)}

## Feature Signal Summary

{json.dumps(result["feature_signal_summary"], indent=2, default=str)[:24000]}

## Findings

{json.dumps(findings, indent=2, default=str)}

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
    print("EDGE FACTORY OS MONTH FIRST FEATURE DISCOVERY EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {evaluator_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("RUNNER SUMMARY")
    print("-" * 100)
    print(result["runner_summary"])
    print()
    print("FEATURE SIGNAL SUMMARY")
    print("-" * 100)
    print(f"scored_candidate_count: {len(scored)}")
    print(f"strong_signal_count: {len(strong)}")
    print(f"moderate_signal_count: {len(moderate)}")
    print(f"good_regime_signal_count: {len(good_regime)}")
    print(f"bad_regime_signal_count: {len(bad_regime)}")
    print(f"tiny_sample_top_count: {len(tiny_sample_top)}")
    print("top_scored_features:")
    for row in scored[:10]:
        print(row)
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
