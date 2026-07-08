from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_feature_conditioned_research_runner_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

FEATURE_CONTRACT_LATEST = (
    BASE_DIR
    / "edge_factory_os_research_direction_contracts"
    / "feature_conditioned_research_contract_latest.json"
)

ACTION_GUARD_LATEST = (
    BASE_DIR
    / "edge_factory_os_action_prerequisite_guard_v1"
    / "action_prerequisite_guard_latest.json"
)

POLICY_LATEST = (
    BASE_DIR
    / "edge_factory_os_policy_guards"
    / "strict_month_stability_policy_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"feature_conditioned_research_runner_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "feature_conditioned_research_runner_latest.json"
LATEST_MD = OUT_ROOT / "feature_conditioned_research_runner_latest.md"


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


def strict_12_of_12_stats(values: List[float]) -> Dict[str, Any]:
    active_month_count = len(values)
    positive_month_count = sum(1 for x in values if fnum(x, 0.0) > 0)
    negative_month_count = sum(1 for x in values if fnum(x, 0.0) < 0)
    flat_month_count = sum(1 for x in values if fnum(x, 0.0) == 0)

    positive_month_rate = (
        positive_month_count / active_month_count
        if active_month_count
        else None
    )

    strict_pass = (
        active_month_count >= 12
        and positive_month_count >= 12
        and positive_month_rate == 1.0
    )

    return {
        "active_month_count": active_month_count,
        "positive_month_count": positive_month_count,
        "negative_month_count": negative_month_count,
        "flat_month_count": flat_month_count,
        "positive_month_rate": positive_month_rate,
        "strict_12_of_12_pass": strict_pass,
        "required_active_months": 12,
        "required_positive_months": 12,
        "required_positive_month_rate": 1.0,
    }


def evaluate_condition(month_df, condition: Dict[str, Any], label_col: str) -> Dict[str, Any]:
    feature = condition.get("feature")
    threshold = fnum(condition.get("threshold"))
    direction = condition.get("direction")

    if not feature or feature not in month_df.columns:
        return {
            "condition": condition,
            "label": label_col,
            "available": False,
            "reason": f"feature_missing:{feature}",
        }

    if label_col not in month_df.columns:
        return {
            "condition": condition,
            "label": label_col,
            "available": False,
            "reason": f"label_missing:{label_col}",
        }

    if threshold is None:
        return {
            "condition": condition,
            "label": label_col,
            "available": False,
            "reason": "threshold_missing",
        }

    if direction == ">=":
        selected = month_df[month_df[feature] >= threshold].copy()
        excluded = month_df[month_df[feature] < threshold].copy()
    elif direction == "<=":
        selected = month_df[month_df[feature] <= threshold].copy()
        excluded = month_df[month_df[feature] > threshold].copy()
    else:
        return {
            "condition": condition,
            "label": label_col,
            "available": False,
            "reason": f"bad_direction:{direction}",
        }

    selected_vals = [fnum(x, 0.0) for x in selected[label_col].dropna().tolist()]
    excluded_vals = [fnum(x, 0.0) for x in excluded[label_col].dropna().tolist()]
    all_vals = [fnum(x, 0.0) for x in month_df[label_col].dropna().tolist()]

    selected_stats = strict_12_of_12_stats(selected_vals)
    excluded_stats = strict_12_of_12_stats(excluded_vals)
    all_stats = strict_12_of_12_stats(all_vals)

    selected_mean = sum(selected_vals) / len(selected_vals) if selected_vals else None
    excluded_mean = sum(excluded_vals) / len(excluded_vals) if excluded_vals else None
    all_mean = sum(all_vals) / len(all_vals) if all_vals else None

    selected_total = sum(selected_vals) if selected_vals else 0.0
    excluded_total = sum(excluded_vals) if excluded_vals else 0.0
    all_total = sum(all_vals) if all_vals else 0.0

    # Diagnostic-only score. Not release approval.
    score = 0.0
    score += 1000 if selected_stats["strict_12_of_12_pass"] else 0
    score += selected_stats["positive_month_count"] * 50
    score += selected_stats["active_month_count"] * 10
    score += max(selected_mean or 0.0, 0.0)
    score -= selected_stats["negative_month_count"] * 100
    score -= 500 if selected_stats["active_month_count"] < 12 else 0

    return {
        "condition": condition,
        "label": label_col,
        "available": True,
        "feature": feature,
        "threshold": threshold,
        "direction": direction,

        "selected_months": selected["month"].astype(str).tolist() if "month" in selected.columns else [],
        "excluded_months": excluded["month"].astype(str).tolist() if "month" in excluded.columns else [],

        "selected_stats": selected_stats,
        "excluded_stats": excluded_stats,
        "all_stats": all_stats,

        "selected_mean_label": selected_mean,
        "excluded_mean_label": excluded_mean,
        "all_mean_label": all_mean,

        "selected_total_label": selected_total,
        "excluded_total_label": excluded_total,
        "all_total_label": all_total,

        "strict_12_of_12_condition_pass": selected_stats["strict_12_of_12_pass"],
        "diagnostic_score": score,
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    contract = load_json(FEATURE_CONTRACT_LATEST)
    action_guard = load_json(ACTION_GUARD_LATEST)
    policy = load_json(POLICY_LATEST)

    if not isinstance(contract, dict):
        critical.append("feature_conditioned_research_contract_latest_missing")
        contract = {}

    if not isinstance(action_guard, dict):
        critical.append("action_prerequisite_guard_latest_missing")
        action_guard = {}

    if not isinstance(policy, dict):
        critical.append("strict_month_policy_latest_missing")
        policy = {}

    if contract.get("research_key") != "FEATURE_CONDITIONED_RESEARCH_V1":
        critical.append(f"unexpected_contract_key:{contract.get('research_key')}")

    if safe_get(contract, ["policy_context", "policy_key"]) != "STRICT_MONTH_STABILITY_12_OF_12":
        critical.append(f"contract_policy_not_12_of_12:{safe_get(contract, ['policy_context', 'policy_key'])}")

    if policy.get("policy_key") != "STRICT_MONTH_STABILITY_12_OF_12":
        critical.append(f"latest_policy_not_12_of_12:{policy.get('policy_key')}")

    if safe_get(policy, ["release_requirement", "min_active_months"]) != 12:
        critical.append("policy_min_active_months_not_12")

    if safe_get(policy, ["release_requirement", "min_positive_months"]) != 12:
        critical.append("policy_min_positive_months_not_12")

    if float(safe_get(policy, ["release_requirement", "min_positive_month_rate"], 0.0)) != 1.0:
        critical.append("policy_positive_month_rate_not_1_0")

    if action_guard.get("guard_status") != "ACTION_PREREQUISITE_GUARD_ACTIVE_ACTIONS_BLOCKED":
        critical.append(f"action_guard_not_blocking:{action_guard.get('guard_status')}")

    auth = action_guard.get("authorization") or {}
    for key, val in auth.items():
        if val is not False:
            critical.append(f"authorization_not_false:{key}={val}")

    if safe_get(contract, ["required_runner_behavior", "candidate_generation_allowed_now"]) is not False:
        critical.append("contract_allows_candidate_generation_unexpectedly")

    if safe_get(contract, ["required_runner_behavior", "candidate_contract_allowed_now"]) is not False:
        critical.append("contract_allows_candidate_contract_unexpectedly")

    if safe_get(contract, ["required_runner_behavior", "family_release_allowed_now"]) is not False:
        critical.append("contract_allows_family_release_unexpectedly")

    month_table_path = safe_get(contract, ["input_artifacts", "month_feature_table_csv"])
    rankings_path = safe_get(contract, ["input_artifacts", "feature_rankings_json"])
    panel_path = safe_get(contract, ["input_artifacts", "panel_path"])

    if not month_table_path:
        critical.append("month_feature_table_csv_missing_from_contract")

    if month_table_path and not Path(str(month_table_path)).exists():
        critical.append(f"month_feature_table_csv_not_found:{month_table_path}")

    if panel_path and not Path(str(panel_path)).exists():
        attention.append(f"panel_path_not_found_but_month_table_available:{panel_path}")

    usable_conditions = safe_get(contract, ["feature_conditions_to_retest", "usable_feature_conditions"], [])
    if not isinstance(usable_conditions, list):
        critical.append("usable_feature_conditions_not_list")
        usable_conditions = []

    if not usable_conditions:
        critical.append("usable_feature_conditions_empty")

    if critical:
        runner_status = "FEATURE_CONDITIONED_RESEARCH_RUNNER_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_CONTRACT_OR_GUARD_INPUTS"
        reason = "; ".join(critical)

        result = {
            "module": MODULE,
            "created_at_utc": NOW.isoformat(),
            "runner_status": runner_status,
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

        dump_json(RUN_DIR / "feature_conditioned_research_runner_v1_state.json", result)
        dump_json(LATEST_JSON, result)

        print("=" * 100)
        print("EDGE FACTORY OS FEATURE CONDITIONED RESEARCH RUNNER v1")
        print("=" * 100)
        print(f"runner_status: {runner_status}")
        print(f"severity: {severity}")
        print(f"reason: {reason}")
        print(f"latest_json: {LATEST_JSON}")
        print("=" * 100)
        return 2

    import pandas as pd

    month_df = pd.read_csv(month_table_path)

    label_cols = [
        c for c in month_df.columns
        if c.startswith("label_") and c != "label_best_broad_template"
    ]

    preferred_labels = [
        "label_best_broad_avg_net_bps",
        "label_avg_diag_label_long_net_6h_bps",
        "label_avg_diag_label_long_net_12h_bps",
        "label_avg_diag_label_short_net_6h_bps",
        "label_avg_diag_label_short_net_12h_bps",
    ]

    labels_to_test = [x for x in preferred_labels if x in label_cols]
    if not labels_to_test:
        labels_to_test = label_cols[:8]

    condition_results: List[Dict[str, Any]] = []

    for condition in usable_conditions:
        if not isinstance(condition, dict):
            continue

        for label in labels_to_test:
            try:
                row = evaluate_condition(month_df, condition, label)
                condition_results.append(row)
            except Exception as exc:
                attention.append(f"condition_eval_failed:{condition.get('feature')}:{label}:{exc}")

    condition_results.sort(
        key=lambda x: (
            1 if x.get("strict_12_of_12_condition_pass") else 0,
            x.get("diagnostic_score") or 0.0,
        ),
        reverse=True,
    )

    strict_12_passes = [
        x for x in condition_results
        if x.get("strict_12_of_12_condition_pass") is True
    ]

    available_results = [
        x for x in condition_results
        if x.get("available") is True
    ]

    best_result = available_results[0] if available_results else None

    scoreboard_path = RUN_DIR / "feature_conditioned_research_scoreboard.json"
    scoreboard_csv_path = RUN_DIR / "feature_conditioned_research_scoreboard.csv"

    dump_json(scoreboard_path, {"scoreboard": condition_results})

    flat_rows = []
    for r in condition_results:
        flat_rows.append({
            "available": r.get("available"),
            "feature": r.get("feature"),
            "direction": r.get("direction"),
            "threshold": r.get("threshold"),
            "label": r.get("label"),
            "strict_12_of_12_condition_pass": r.get("strict_12_of_12_condition_pass"),
            "diagnostic_score": r.get("diagnostic_score"),
            "selected_active_month_count": safe_get(r, ["selected_stats", "active_month_count"]),
            "selected_positive_month_count": safe_get(r, ["selected_stats", "positive_month_count"]),
            "selected_negative_month_count": safe_get(r, ["selected_stats", "negative_month_count"]),
            "selected_positive_month_rate": safe_get(r, ["selected_stats", "positive_month_rate"]),
            "selected_mean_label": r.get("selected_mean_label"),
            "excluded_mean_label": r.get("excluded_mean_label"),
            "selected_total_label": r.get("selected_total_label"),
            "excluded_total_label": r.get("excluded_total_label"),
        })

    pd.DataFrame(flat_rows).to_csv(scoreboard_csv_path, index=False)

    if strict_12_passes:
        runner_status = "FEATURE_CONDITIONED_RESEARCH_RUNNER_STRICT_12_OF_12_SIGNAL_FOUND"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "EVALUATE_FEATURE_CONDITIONED_RESEARCH_RESULTS_NO_ACTIONS"
        reason = f"strict_12_of_12_signal_count={len(strict_12_passes)}; candidate_actions_still_blocked"
    else:
        runner_status = "FEATURE_CONDITIONED_RESEARCH_RUNNER_NO_STRICT_12_OF_12_SIGNAL_FOUND"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "EVALUATE_FEATURE_CONDITIONED_RESEARCH_RESULTS_AND_DECIDE_NEXT_RESEARCH"
        reason = f"tested_conditions={len(condition_results)}; strict_12_of_12_signal_count=0"

    findings = []

    findings.append({
        "finding_id": "FCR_RUNNER_F1_ACTION_GUARD_CONFIRMED_BLOCKING",
        "severity": "CONTROL",
        "claim": "Action prerequisite guard is active and all action authorization flags are false.",
        "evidence": {
            "guard_status": action_guard.get("guard_status"),
            "authorization": auth,
        },
    })

    findings.append({
        "finding_id": "FCR_RUNNER_F2_POLICY_12_OF_12_CONSUMED",
        "severity": "CONTROL",
        "claim": "Feature-conditioned research consumed STRICT_MONTH_STABILITY_12_OF_12.",
        "evidence": {
            "policy_key": policy.get("policy_key"),
            "min_active_months": safe_get(policy, ["release_requirement", "min_active_months"]),
            "min_positive_months": safe_get(policy, ["release_requirement", "min_positive_months"]),
            "min_positive_month_rate": safe_get(policy, ["release_requirement", "min_positive_month_rate"]),
        },
    })

    if strict_12_passes:
        findings.append({
            "finding_id": "FCR_RUNNER_F3_STRICT_12_OF_12_DIAGNOSTIC_SIGNAL_FOUND",
            "severity": "ATTENTION",
            "claim": "At least one feature-conditioned diagnostic split achieved strict 12/12 on diagnostic labels.",
            "evidence": {
                "strict_12_pass_count": len(strict_12_passes),
                "top_strict_12_passes": strict_12_passes[:10],
            },
            "interpretation": "This is not a candidate or release. It only goes to evaluator.",
        })
    else:
        findings.append({
            "finding_id": "FCR_RUNNER_F3_NO_STRICT_12_OF_12_DIAGNOSTIC_SIGNAL_FOUND",
            "severity": "ATTENTION",
            "claim": "No tested feature-conditioned diagnostic split achieved strict 12/12.",
            "evidence": {
                "tested_condition_count": len(condition_results),
                "best_result": best_result,
            },
        })

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "runner_status": runner_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "contract_source": str(FEATURE_CONTRACT_LATEST),
        "action_guard_source": str(ACTION_GUARD_LATEST),
        "policy_source": str(POLICY_LATEST),

        "contract_id": contract.get("contract_id"),
        "contract_hash": contract.get("contract_hash"),
        "research_key": contract.get("research_key"),

        "month_feature_table_csv": str(month_table_path),
        "panel_path": str(panel_path),
        "rankings_path": str(rankings_path),

        "policy": {
            "policy_key": policy.get("policy_key"),
            "min_active_months": safe_get(policy, ["release_requirement", "min_active_months"], 12),
            "min_positive_months": safe_get(policy, ["release_requirement", "min_positive_months"], 12),
            "min_positive_month_rate": safe_get(policy, ["release_requirement", "min_positive_month_rate"], 1.0),
        },

        "test_summary": {
            "month_count": int(len(month_df)),
            "usable_feature_condition_count": len(usable_conditions),
            "label_count": len(labels_to_test),
            "condition_result_count": len(condition_results),
            "strict_12_of_12_signal_count": len(strict_12_passes),
        },

        "best_result": best_result,
        "top_results": condition_results[:30],
        "strict_12_of_12_passes": strict_12_passes[:20],

        "outputs": {
            "scoreboard_json": str(scoreboard_path),
            "scoreboard_csv": str(scoreboard_csv_path),
        },

        "findings": findings,

        "release_gate_feed": {
            "FEATURE_CONDITIONED_RESEARCH_RUNNER_RAN": True,
            "STRICT_12_OF_12_POLICY_CONSUMED": True,
            "ACTION_PREREQUISITE_GUARD_CONFIRMED_BLOCKING": True,
            "STRICT_12_OF_12_DIAGNOSTIC_SIGNAL_FOUND": bool(strict_12_passes),
            "CANDIDATE_GENERATION_ALLOWED": False,
            "CANDIDATE_CONTRACT_ALLOWED": False,
            "FAMILY_RELEASE_ALLOWED": False,
            "RUNTIME_CHANGE_ALLOWED": False,
            "CAPITAL_CHANGE_ALLOWED": False,
            "ACTIVE_PAPER_ALLOWED": False,
            "LIVE_ALLOWED": False,
            "REAL_ORDERS_ALLOWED": False,
            "RELEASE_PASS_FROM_THIS_RUNNER": False,
            "status": runner_status,
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
            "next_module": "edge_factory_os_feature_conditioned_research_evaluator_v1.py",
            "why_no_action": [
                "action_prerequisite_guard_blocks_all_actions",
                "runner_is_diagnostic_only",
                "feature_conditions_are_not_candidates",
                "strict_12_of_12_signal_if_any_requires_evaluator_and_full_chain",
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
            "execution_performed": True,
        },

        "critical": critical,
        "attention": attention,
        "info": info,
    }

    out_json = RUN_DIR / "feature_conditioned_research_runner_v1_state.json"
    out_md = RUN_DIR / "feature_conditioned_research_runner_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS FEATURE CONDITIONED RESEARCH RUNNER v1

runner_status: {runner_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

contract_id: {contract.get("contract_id")}  
research_key: {contract.get("research_key")}

## Policy

{json.dumps(result["policy"], indent=2, default=str)}

## Test Summary

{json.dumps(result["test_summary"], indent=2, default=str)}

## Best Result

{json.dumps(best_result, indent=2, default=str)[:12000]}

## Strict 12 Of 12 Passes

{json.dumps(strict_12_passes[:10], indent=2, default=str)[:16000]}

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
execution_performed: True

critical: {critical}  
attention: {attention}  
info: {info}
"""

    out_md.write_text(md, encoding="utf-8")
    LATEST_MD.write_text(md, encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS FEATURE CONDITIONED RESEARCH RUNNER v1")
    print("=" * 100)
    print(f"runner_status: {runner_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("POLICY")
    print("-" * 100)
    print(json.dumps(result["policy"], indent=2, default=str))
    print()
    print("TEST SUMMARY")
    print("-" * 100)
    print(json.dumps(result["test_summary"], indent=2, default=str))
    print()
    print("BEST RESULT")
    print("-" * 100)
    print(json.dumps(best_result, indent=2, default=str)[:6000])
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
    print("execution_performed: True")
    print()
    print(f"latest_json: {LATEST_JSON}")
    print("=" * 100)

    return 0 if severity != "CRITICAL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
