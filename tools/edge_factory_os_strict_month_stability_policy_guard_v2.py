from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_strict_month_stability_policy_guard_v2"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

OLD_POLICY_LATEST = (
    BASE_DIR
    / "edge_factory_os_policy_guards"
    / "strict_month_stability_policy_latest.json"
)

MONTH_FIRST_EVAL_LATEST = (
    BASE_DIR
    / "edge_factory_os_month_first_feature_discovery_evaluator_v1"
    / "month_first_feature_discovery_evaluator_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"strict_month_stability_policy_guard_v2_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "strict_month_stability_policy_guard_v2_latest.json"
LATEST_MD = OUT_ROOT / "strict_month_stability_policy_guard_v2_latest.md"

POLICY_ROOT = BASE_DIR / "edge_factory_os_policy_guards"
POLICY_LATEST = POLICY_ROOT / "strict_month_stability_policy_latest.json"

MIN_ACTIVE_MONTHS = 12
MIN_POSITIVE_MONTHS = 12
MIN_POSITIVE_MONTH_RATE = 1.0


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


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_ROOT.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    old_policy = load_json(OLD_POLICY_LATEST)
    month_first_eval = load_json(MONTH_FIRST_EVAL_LATEST)

    if not isinstance(old_policy, dict):
        attention.append("old_strict_month_policy_missing_or_unreadable")
        old_policy = {}

    if not isinstance(month_first_eval, dict):
        attention.append("month_first_feature_discovery_evaluator_missing_or_unreadable")
        month_first_eval = {}

    old_min_active = None
    old_min_positive = None
    old_min_rate = None

    if old_policy:
        old_min_active = old_policy.get("release_requirement", {}).get("min_active_months")
        old_min_positive = old_policy.get("release_requirement", {}).get("min_positive_months")
        old_min_rate = old_policy.get("release_requirement", {}).get("min_positive_month_rate")

    policy = {
        "policy_schema": "edge_factory_os_strict_month_stability_policy_v2",
        "created_at_utc": NOW.isoformat(),
        "policy_key": "STRICT_MONTH_STABILITY_12_OF_12",
        "supersedes_policy_key": old_policy.get("policy_key"),
        "release_requirement": {
            "min_active_months": MIN_ACTIVE_MONTHS,
            "min_positive_months": MIN_POSITIVE_MONTHS,
            "min_positive_month_rate": MIN_POSITIVE_MONTH_RATE,
            "meaning": (
                "Any candidate/family release must trade across at least 12 active months, "
                "and all 12 active months must be positive. 11/12 is not enough."
            ),
        },
        "explicitly_deprecated_for_release": {
            "positive_month_rate_gte_0_55_only": True,
            "strict_11_of_12_policy": True,
            "reason": (
                "The user raised the standard to 12/12. 0.55 month-rate and 11/12 are both insufficient for release."
            ),
        },
        "hard_blocks": [
            "candidate_with_active_month_count_below_12",
            "candidate_with_positive_month_count_below_12",
            "candidate_with_any_negative_active_month",
            "candidate_with_positive_month_rate_below_1_0",
            "candidate_using_manual_bad_month_blacklist",
            "candidate_using_post_outcome_pnl_as_filter",
            "candidate_validated_only_on_paper_ledger",
            "candidate_passing_ai_or_manual_review_without_full_tests",
        ],
        "applies_to": [
            "family_candidate_release_gate",
            "candidate_backtest_evaluator",
            "month_stability_repair_evaluator",
            "month_first_feature_discovery_evaluator",
            "feature_conditioned_research_contract_builder",
            "all future family release gates",
            "all future promotion gates",
        ],
        "old_policy_snapshot": {
            "old_policy_key": old_policy.get("policy_key"),
            "old_min_active_months": old_min_active,
            "old_min_positive_months": old_min_positive,
            "old_min_positive_month_rate": old_min_rate,
        },
    }

    if critical:
        guard_status = "STRICT_MONTH_STABILITY_POLICY_GUARD_V2_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_INPUTS_BEFORE_POLICY_UPDATE"
        reason = "; ".join(critical)
        policy_written = False
    else:
        dump_json(POLICY_LATEST, policy)

        guard_status = "STRICT_MONTH_STABILITY_POLICY_GUARD_V2_ACTIVE_12_OF_12"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "RECHECK_FEATURE_CONDITIONED_RESEARCH_CONTRACT_UNDER_12_OF_12_POLICY"
        reason = "strict_rule_hardened=min_active_months:12;min_positive_months:12;positive_month_rate:1.0"
        policy_written = True

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "guard_status": guard_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "policy_written": policy_written,
        "policy_latest_path": str(POLICY_LATEST),
        "policy": policy,

        "month_first_feature_discovery_evaluator_summary": {
            "evaluator_status": month_first_eval.get("evaluator_status"),
            "strong_feature_signal_count": month_first_eval.get("feature_signal_summary", {}).get("strong_signal_count"),
            "feature_conditioned_research_contract_recommended": month_first_eval.get("decision", {}).get("feature_conditioned_research_contract_recommended"),
            "candidate_generation_recommended_now": month_first_eval.get("decision", {}).get("candidate_generation_recommended_now"),
            "family_release_recommended": month_first_eval.get("decision", {}).get("family_release_recommended"),
            "runtime_change_recommended": month_first_eval.get("decision", {}).get("runtime_change_recommended"),
            "capital_change_recommended": month_first_eval.get("decision", {}).get("capital_change_recommended"),
        },

        "release_gate_feed": {
            "STRICT_MONTH_STABILITY_POLICY_ACTIVE": policy_written,
            "STRICT_MONTH_STABILITY_POLICY_KEY": "STRICT_MONTH_STABILITY_12_OF_12",
            "STRICT_MONTH_STABILITY_MIN_ACTIVE_MONTHS": MIN_ACTIVE_MONTHS,
            "STRICT_MONTH_STABILITY_MIN_POSITIVE_MONTHS": MIN_POSITIVE_MONTHS,
            "STRICT_MONTH_STABILITY_MIN_POSITIVE_MONTH_RATE": MIN_POSITIVE_MONTH_RATE,
            "STRICT_11_OF_12_DEPRECATED_FOR_RELEASE": True,
            "LOOSE_055_MONTH_RATE_DEPRECATED_FOR_RELEASE": True,
            "RELEASE_PASS_FROM_THIS_POLICY_GUARD": False,
            "status": guard_status,
        },

        "decision": {
            "candidate_generation_recommended_now": False,
            "candidate_contract_recommended_now": False,
            "feature_conditioned_research_contract_allowed_without_recheck": False,
            "family_release_recommended": False,
            "promotion_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "next_module": "edge_factory_os_feature_conditioned_research_contract_builder_v1.py",
            "why_no_action": [
                "policy_guard_only",
                "12_of_12_policy_must_be_consumed_by_next_contract",
                "feature_discovery_is_diagnostic_only",
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

    out_json = RUN_DIR / "strict_month_stability_policy_guard_v2_state.json"
    out_md = RUN_DIR / "strict_month_stability_policy_guard_v2_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS STRICT MONTH STABILITY POLICY GUARD v2

guard_status: {guard_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

policy_written: {policy_written}  
policy_latest_path: {POLICY_LATEST}

## New Strict Policy

policy_key: STRICT_MONTH_STABILITY_12_OF_12  
min_active_months: {MIN_ACTIVE_MONTHS}  
min_positive_months: {MIN_POSITIVE_MONTHS}  
min_positive_month_rate: {MIN_POSITIVE_MONTH_RATE}  
strict_11_of_12_deprecated_for_release: True  
loose_055_month_rate_deprecated_for_release: True

## Month First Feature Discovery Evaluator Summary

{json.dumps(result["month_first_feature_discovery_evaluator_summary"], indent=2, default=str)}

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
    print("EDGE FACTORY OS STRICT MONTH STABILITY POLICY GUARD v2")
    print("=" * 100)
    print(f"guard_status: {guard_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("NEW STRICT POLICY")
    print("-" * 100)
    print("policy_key: STRICT_MONTH_STABILITY_12_OF_12")
    print(f"min_active_months: {MIN_ACTIVE_MONTHS}")
    print(f"min_positive_months: {MIN_POSITIVE_MONTHS}")
    print(f"min_positive_month_rate: {MIN_POSITIVE_MONTH_RATE}")
    print("strict_11_of_12_deprecated_for_release: True")
    print("loose_055_month_rate_deprecated_for_release: True")
    print()
    print("MONTH FIRST FEATURE DISCOVERY EVALUATOR SUMMARY")
    print("-" * 100)
    print(json.dumps(result["month_first_feature_discovery_evaluator_summary"], indent=2, default=str))
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
