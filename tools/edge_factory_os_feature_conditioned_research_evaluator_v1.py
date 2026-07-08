from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_feature_conditioned_research_evaluator_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

FEATURE_RUNNER_LATEST = (
    BASE_DIR
    / "edge_factory_os_feature_conditioned_research_runner_v1"
    / "feature_conditioned_research_runner_latest.json"
)

CANONICAL_GUARD_LATEST = (
    BASE_DIR
    / "edge_factory_os_canonical_month_window_guard_v1"
    / "canonical_month_window_guard_latest.json"
)

STRICT_POLICY_LATEST = (
    BASE_DIR
    / "edge_factory_os_policy_guards"
    / "strict_month_stability_policy_latest.json"
)

ACTION_GUARD_LATEST = (
    BASE_DIR
    / "edge_factory_os_action_prerequisite_guard_v1"
    / "action_prerequisite_guard_latest.json"
)

FEATURE_CONTRACT_LATEST = (
    BASE_DIR
    / "edge_factory_os_research_direction_contracts"
    / "feature_conditioned_research_contract_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"feature_conditioned_research_evaluator_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "feature_conditioned_research_evaluator_latest.json"
LATEST_MD = OUT_ROOT / "feature_conditioned_research_evaluator_latest.md"


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
        x = float(v)
        return x if math.isfinite(x) else default
    except Exception:
        return default


def safe_get(d: Dict[str, Any], path: List[str], default=None):
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def strict_canonical_stats(month_values: Dict[str, float], canonical_months: List[str]) -> Dict[str, Any]:
    vals = []
    monthly = {}

    for month in canonical_months:
        val = fnum(month_values.get(month), None)
        monthly[month] = val
        if val is not None:
            vals.append(val)

    active = len(vals)
    positive = sum(1 for x in vals if x > 0)
    negative = sum(1 for x in vals if x < 0)
    flat = sum(1 for x in vals if x == 0)
    total = float(sum(vals)) if vals else 0.0
    mean = total / active if active else None
    positive_rate = positive / active if active else None

    strict_pass = (
        active == 12
        and positive == 12
        and negative == 0
        and positive_rate == 1.0
    )

    return {
        "canonical_policy_month_count": len(canonical_months),
        "active_month_count": active,
        "positive_month_count": positive,
        "negative_month_count": negative,
        "flat_month_count": flat,
        "positive_month_rate": positive_rate,
        "total_label": total,
        "mean_label": mean,
        "monthly_values": monthly,
        "strict_12_of_12_canonical_pass": strict_pass,
        "required": {
            "canonical_policy_month_count": 12,
            "active_month_count": 12,
            "positive_month_count": 12,
            "negative_month_count": 0,
            "positive_month_rate": 1.0,
        },
    }


def evaluate_condition_on_canonical(month_df, condition_row: Dict[str, Any], canonical_months: List[str]) -> Dict[str, Any]:
    feature = condition_row.get("feature")
    label = condition_row.get("label")
    direction = condition_row.get("direction")
    threshold = fnum(condition_row.get("threshold"), None)

    if not feature or feature not in month_df.columns:
        return {
            "available": False,
            "reason": f"feature_missing:{feature}",
            "source_condition": condition_row,
        }

    if not label or label not in month_df.columns:
        return {
            "available": False,
            "reason": f"label_missing:{label}",
            "source_condition": condition_row,
        }

    if threshold is None:
        return {
            "available": False,
            "reason": "threshold_missing",
            "source_condition": condition_row,
        }

    canonical_df = month_df[month_df["month"].astype(str).isin(canonical_months)].copy()

    if direction == ">=":
        selected = canonical_df[canonical_df[feature] >= threshold].copy()
    elif direction == "<=":
        selected = canonical_df[canonical_df[feature] <= threshold].copy()
    else:
        return {
            "available": False,
            "reason": f"bad_direction:{direction}",
            "source_condition": condition_row,
        }

    selected_values = {
        str(row["month"]): fnum(row[label], None)
        for _, row in selected.iterrows()
    }

    all_values = {
        str(row["month"]): fnum(row[label], None)
        for _, row in canonical_df.iterrows()
    }

    selected_stats = strict_canonical_stats(selected_values, canonical_months)
    all_stats = strict_canonical_stats(all_values, canonical_months)

    return {
        "available": True,
        "feature": feature,
        "label": label,
        "direction": direction,
        "threshold": threshold,
        "selected_months": selected["month"].astype(str).tolist(),
        "canonical_months": canonical_months,
        "selected_stats_canonical": selected_stats,
        "all_stats_canonical": all_stats,
        "strict_12_of_12_canonical_condition_pass": selected_stats["strict_12_of_12_canonical_pass"],
        "source_condition": condition_row,
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    runner = load_json(FEATURE_RUNNER_LATEST)
    canonical_guard = load_json(CANONICAL_GUARD_LATEST)
    strict_policy = load_json(STRICT_POLICY_LATEST)
    action_guard = load_json(ACTION_GUARD_LATEST)
    contract = load_json(FEATURE_CONTRACT_LATEST)

    if not isinstance(runner, dict):
        critical.append("feature_conditioned_runner_latest_missing")
        runner = {}

    if not isinstance(canonical_guard, dict):
        critical.append("canonical_month_window_guard_latest_missing")
        canonical_guard = {}

    if not isinstance(strict_policy, dict):
        critical.append("strict_month_policy_latest_missing")
        strict_policy = {}

    if not isinstance(action_guard, dict):
        critical.append("action_prerequisite_guard_latest_missing")
        action_guard = {}

    if not isinstance(contract, dict):
        critical.append("feature_conditioned_contract_latest_missing")
        contract = {}

    if canonical_guard.get("guard_status") != "CANONICAL_MONTH_WINDOW_GUARD_ACTIVE":
        critical.append(f"canonical_guard_not_active:{canonical_guard.get('guard_status')}")

    canonical_months = safe_get(canonical_guard, ["month_window", "canonical_policy_months"], [])
    raw_month_count = safe_get(canonical_guard, ["month_window", "raw_calendar_month_count"])
    canonical_count = safe_get(canonical_guard, ["month_window", "canonical_policy_month_count"])

    if not isinstance(canonical_months, list) or len(canonical_months) != 12:
        critical.append(f"canonical_policy_months_not_12:{canonical_months}")

    if canonical_count != 12:
        critical.append(f"canonical_policy_month_count_not_12:{canonical_count}")

    if strict_policy.get("policy_key") != "STRICT_MONTH_STABILITY_12_OF_12":
        critical.append(f"strict_policy_not_12_of_12:{strict_policy.get('policy_key')}")

    if safe_get(strict_policy, ["release_requirement", "min_active_months"]) != 12:
        critical.append("strict_policy_min_active_not_12")

    if safe_get(strict_policy, ["release_requirement", "min_positive_months"]) != 12:
        critical.append("strict_policy_min_positive_not_12")

    if float(safe_get(strict_policy, ["release_requirement", "min_positive_month_rate"], 0.0)) != 1.0:
        critical.append("strict_policy_positive_rate_not_1_0")

    if action_guard.get("guard_status") != "ACTION_PREREQUISITE_GUARD_ACTIVE_ACTIONS_BLOCKED":
        critical.append(f"action_guard_not_blocking:{action_guard.get('guard_status')}")

    authorization = action_guard.get("authorization") or {}
    for k, v in authorization.items():
        if v is not False:
            critical.append(f"authorization_not_false:{k}={v}")

    if runner.get("runner_status") not in {
        "FEATURE_CONDITIONED_RESEARCH_RUNNER_NO_STRICT_12_OF_12_SIGNAL_FOUND",
        "FEATURE_CONDITIONED_RESEARCH_RUNNER_STRICT_12_OF_12_SIGNAL_FOUND",
    }:
        attention.append(f"unexpected_runner_status:{runner.get('runner_status')}")

    if safe_get(runner, ["release_gate_feed", "RELEASE_PASS_FROM_THIS_RUNNER"]) is not False:
        critical.append("runner_claimed_release_pass_unexpectedly")

    month_table_csv = runner.get("month_feature_table_csv")
    if not month_table_csv:
        month_table_csv = safe_get(contract, ["input_artifacts", "month_feature_table_csv"])

    if not month_table_csv:
        critical.append("month_feature_table_csv_missing")

    if month_table_csv and not Path(str(month_table_csv)).exists():
        critical.append(f"month_feature_table_csv_not_found:{month_table_csv}")

    top_results = runner.get("top_results")
    if not isinstance(top_results, list):
        top_results = []

    if not top_results:
        attention.append("runner_top_results_empty")

    if critical:
        evaluator_status = "FEATURE_CONDITIONED_RESEARCH_EVALUATOR_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_INPUTS_BEFORE_EVALUATION"
        reason = "; ".join(critical)

        result = {
            "module": MODULE,
            "created_at_utc": NOW.isoformat(),
            "evaluator_status": evaluator_status,
            "severity": severity,
            "allowed_scope": allowed_scope,
            "next_action": next_action,
            "reason": reason,
            "critical": critical,
            "attention": attention,
            "info": info,
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

        dump_json(RUN_DIR / "feature_conditioned_research_evaluator_v1_state.json", result)
        dump_json(LATEST_JSON, result)

        print("=" * 100)
        print("EDGE FACTORY OS FEATURE CONDITIONED RESEARCH EVALUATOR v1")
        print("=" * 100)
        print(f"evaluator_status: {evaluator_status}")
        print(f"severity: {severity}")
        print(f"reason: {reason}")
        print(f"latest_json: {LATEST_JSON}")
        print("=" * 100)
        return 2

    import pandas as pd

    month_df = pd.read_csv(month_table_csv)
    month_df["month"] = month_df["month"].astype(str)

    canonical_results = []

    for row in top_results:
        if not isinstance(row, dict):
            continue
        evaluated = evaluate_condition_on_canonical(month_df, row, canonical_months)
        canonical_results.append(evaluated)

    canonical_results = [r for r in canonical_results if isinstance(r, dict)]
    strict_passes = [
        r for r in canonical_results
        if r.get("strict_12_of_12_canonical_condition_pass") is True
    ]

    available_results = [r for r in canonical_results if r.get("available") is True]

    # Sort best first by canonical pass, then positive month count, then total/mean.
    available_results.sort(
        key=lambda r: (
            1 if r.get("strict_12_of_12_canonical_condition_pass") else 0,
            safe_get(r, ["selected_stats_canonical", "positive_month_count"], 0) or 0,
            safe_get(r, ["selected_stats_canonical", "total_label"], -999999) or -999999,
        ),
        reverse=True,
    )

    best_canonical = available_results[0] if available_results else None

    canonical_scoreboard_path = RUN_DIR / "feature_conditioned_canonical_scoreboard.json"
    dump_json(canonical_scoreboard_path, {"canonical_scoreboard": available_results})

    findings = []

    findings.append({
        "finding_id": "FCR_EVAL_F1_CANONICAL_MONTH_GUARD_CONSUMED",
        "severity": "CONTROL",
        "claim": "Evaluator consumed canonical month policy and did not use raw calendar month count for release logic.",
        "evidence": {
            "raw_calendar_month_count": raw_month_count,
            "canonical_policy_month_count": canonical_count,
            "canonical_policy_months": canonical_months,
            "boundary_partial_months": safe_get(canonical_guard, ["month_window", "boundary_partial_months"]),
        },
    })

    findings.append({
        "finding_id": "FCR_EVAL_F2_ACTION_GUARD_STILL_BLOCKING",
        "severity": "CONTROL",
        "claim": "Action prerequisite guard remains blocking all candidate/family/runtime/capital actions.",
        "evidence": {
            "guard_status": action_guard.get("guard_status"),
            "authorization": authorization,
        },
    })

    if strict_passes:
        findings.append({
            "finding_id": "FCR_EVAL_F3_CANONICAL_STRICT_12_OF_12_SIGNAL_FOUND",
            "severity": "ATTENTION",
            "claim": "At least one feature-conditioned diagnostic split passes canonical strict 12/12 on diagnostic labels.",
            "evidence": {
                "strict_pass_count": len(strict_passes),
                "top_strict_passes": strict_passes[:5],
            },
            "interpretation": "This is still not candidate generation. It only justifies the next preflight/research step if all guards agree.",
        })
    else:
        findings.append({
            "finding_id": "FCR_EVAL_F3_NO_CANONICAL_STRICT_12_OF_12_SIGNAL_FOUND",
            "severity": "ATTENTION",
            "claim": "No feature-conditioned diagnostic split passed canonical strict 12/12.",
            "evidence": {
                "evaluated_condition_count": len(available_results),
                "best_canonical_result": best_canonical,
            },
        })

    if strict_passes:
        evaluator_status = "FEATURE_CONDITIONED_RESEARCH_EVALUATOR_CANONICAL_12_OF_12_SIGNAL_FOUND_NO_ACTION"
        next_action = "RUN_NEW_CANDIDATE_PREFLIGHT_GUARD_ONLY_IF_ACTION_GUARD_CHAIN_REMAINS_BLOCKING"
        reason = f"canonical_strict_12_of_12_signal_count={len(strict_passes)}; all_actions_still_blocked"
    else:
        evaluator_status = "FEATURE_CONDITIONED_RESEARCH_EVALUATOR_NO_CANONICAL_12_OF_12_SIGNAL_FOUND"
        next_action = "QUEUE_BROADER_FEATURE_ENGINE_OR_NEW_RESEARCH_DIRECTION"
        reason = f"evaluated_condition_count={len(available_results)}; canonical_strict_12_of_12_signal_count=0"

    severity = "ATTENTION"
    allowed_scope = "READ_ONLY_RESEARCH"

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "sources": {
            "feature_runner": str(FEATURE_RUNNER_LATEST),
            "canonical_guard": str(CANONICAL_GUARD_LATEST),
            "strict_policy": str(STRICT_POLICY_LATEST),
            "action_guard": str(ACTION_GUARD_LATEST),
            "feature_contract": str(FEATURE_CONTRACT_LATEST),
            "month_feature_table_csv": str(month_table_csv),
        },

        "canonical_month_window": {
            "raw_calendar_month_count": raw_month_count,
            "canonical_policy_month_count": canonical_count,
            "canonical_policy_months": canonical_months,
            "boundary_partial_months": safe_get(canonical_guard, ["month_window", "boundary_partial_months"]),
            "canonicalization_method": safe_get(canonical_guard, ["month_window", "canonicalization_method"]),
        },

        "policy": {
            "policy_key": strict_policy.get("policy_key"),
            "min_active_months": safe_get(strict_policy, ["release_requirement", "min_active_months"]),
            "min_positive_months": safe_get(strict_policy, ["release_requirement", "min_positive_months"]),
            "min_positive_month_rate": safe_get(strict_policy, ["release_requirement", "min_positive_month_rate"]),
        },

        "evaluation_summary": {
            "runner_status": runner.get("runner_status"),
            "runner_raw_strict_signal_found": safe_get(runner, ["release_gate_feed", "STRICT_12_OF_12_DIAGNOSTIC_SIGNAL_FOUND"]),
            "evaluated_condition_count": len(available_results),
            "canonical_strict_12_of_12_signal_count": len(strict_passes),
            "raw_calendar_month_count": raw_month_count,
            "canonical_policy_month_count": canonical_count,
        },

        "best_canonical_result": best_canonical,
        "canonical_strict_12_of_12_passes": strict_passes[:20],
        "top_canonical_results": available_results[:30],

        "outputs": {
            "canonical_scoreboard_json": str(canonical_scoreboard_path),
        },

        "findings": findings,

        "release_gate_feed": {
            "FEATURE_CONDITIONED_RESEARCH_EVALUATED": True,
            "CANONICAL_MONTH_WINDOW_GUARD_CONSUMED": True,
            "RAW_CALENDAR_MONTH_COUNT_IGNORED_FOR_RELEASE": True,
            "CANONICAL_POLICY_MONTH_COUNT": canonical_count,
            "STRICT_MONTH_STABILITY_POLICY_KEY": "STRICT_MONTH_STABILITY_12_OF_12",
            "CANONICAL_STRICT_12_OF_12_SIGNAL_FOUND": bool(strict_passes),
            "ACTION_PREREQUISITE_GUARD_STILL_BLOCKING": True,
            "CANDIDATE_GENERATION_ALLOWED": False,
            "CANDIDATE_CONTRACT_ALLOWED": False,
            "FAMILY_RELEASE_ALLOWED": False,
            "RUNTIME_CHANGE_ALLOWED": False,
            "CAPITAL_CHANGE_ALLOWED": False,
            "ACTIVE_PAPER_ALLOWED": False,
            "LIVE_ALLOWED": False,
            "REAL_ORDERS_ALLOWED": False,
            "RELEASE_PASS_FROM_THIS_EVALUATOR": False,
            "status": evaluator_status,
        },

        "decision": {
            "candidate_generation_recommended_now": False,
            "candidate_contract_recommended_now": False,
            "family_release_recommended": False,
            "promotion_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "active_paper_recommended": False,
            "live_or_real_order_recommended": False,
            "next_module": (
                "edge_factory_os_candidate_contract_preflight_guard_v1.py"
                if strict_passes else
                "edge_factory_os_broader_month_feature_engine_contract_builder_v1.py"
            ),
            "why_no_action": [
                "canonical_month_window_guard_required_and_consumed",
                "action_prerequisite_guard_blocks_all_actions",
                "evaluator_is_read_only",
                "feature_conditioned_diagnostic_signal_is_not_candidate_generation",
                "full_chain_still_required_before candidate/family/runtime/capital",
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

    out_json = RUN_DIR / "feature_conditioned_research_evaluator_v1_state.json"
    out_md = RUN_DIR / "feature_conditioned_research_evaluator_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS FEATURE CONDITIONED RESEARCH EVALUATOR v1

evaluator_status: {evaluator_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

## Canonical Month Window

{json.dumps(result["canonical_month_window"], indent=2, default=str)}

## Policy

{json.dumps(result["policy"], indent=2, default=str)}

## Evaluation Summary

{json.dumps(result["evaluation_summary"], indent=2, default=str)}

## Best Canonical Result

{json.dumps(best_canonical, indent=2, default=str)[:14000]}

## Canonical Strict 12/12 Passes

{json.dumps(strict_passes[:10], indent=2, default=str)[:18000]}

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
    print("EDGE FACTORY OS FEATURE CONDITIONED RESEARCH EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {evaluator_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("CANONICAL MONTH WINDOW")
    print("-" * 100)
    print(json.dumps(result["canonical_month_window"], indent=2, default=str))
    print()
    print("EVALUATION SUMMARY")
    print("-" * 100)
    print(json.dumps(result["evaluation_summary"], indent=2, default=str))
    print()
    print("BEST CANONICAL RESULT")
    print("-" * 100)
    print(json.dumps(best_canonical, indent=2, default=str)[:7000])
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
