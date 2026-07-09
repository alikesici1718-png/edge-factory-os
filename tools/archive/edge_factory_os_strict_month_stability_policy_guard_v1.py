from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_strict_month_stability_policy_guard_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

STRICT_EVAL_LATEST = (
    BASE_DIR
    / "edge_factory_os_month_stability_repair_evaluator_v1"
    / "month_stability_repair_evaluator_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"strict_month_stability_policy_guard_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "strict_month_stability_policy_guard_latest.json"
LATEST_MD = OUT_ROOT / "strict_month_stability_policy_guard_latest.md"

POLICY_ROOT = BASE_DIR / "edge_factory_os_policy_guards"
POLICY_LATEST = POLICY_ROOT / "strict_month_stability_policy_latest.json"

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


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_ROOT.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    strict_eval = load_json(STRICT_EVAL_LATEST)

    if not isinstance(strict_eval, dict):
        critical.append("strict_month_stability_evaluator_latest_missing")
        strict_eval = {}

    expected_statuses = {
        "MONTH_STABILITY_REPAIR_EVALUATOR_STRICT_11_OF_12_NOT_FOUND",
        "MONTH_STABILITY_REPAIR_EVALUATOR_STRICT_11_OF_12_REPAIR_FOUND",
        "MONTH_STABILITY_REPAIR_EVALUATOR_MONTH_STABLE_BUT_OTHER_CHECKS_FAIL",
    }

    evaluator_status = strict_eval.get("evaluator_status")
    if evaluator_status not in expected_statuses:
        critical.append(f"unexpected_strict_evaluator_status:{evaluator_status}")

    release_feed = strict_eval.get("release_gate_feed") or {}
    strict_found = release_feed.get("STRICT_11_OF_12_REPAIR_FOUND") is True
    release_from_eval = release_feed.get("RELEASE_PASS_FROM_THIS_EVALUATOR") is True

    if release_from_eval:
        critical.append("strict_evaluator_claimed_release_pass_unexpectedly")

    strict_month_policy = {
        "policy_schema": "edge_factory_os_strict_month_stability_policy_v1",
        "created_at_utc": NOW.isoformat(),
        "policy_key": "STRICT_MONTH_STABILITY_11_OF_12",
        "release_requirement": {
            "min_active_months": MIN_ACTIVE_MONTHS,
            "min_positive_months": MIN_POSITIVE_MONTHS,
            "min_positive_month_rate": MIN_POSITIVE_MONTH_RATE,
            "meaning": "Any candidate/family release must trade across at least 12 active months and at least 11 of those active months must be positive.",
        },
        "explicitly_deprecated_for_release": {
            "positive_month_rate_gte_0_55_only": True,
            "reason": "0.55 allows 7/12 positive months, which is not stable enough for Edge Factory OS release.",
        },
        "hard_blocks": [
            "candidate_with_active_month_count_below_12",
            "candidate_with_positive_month_count_below_11",
            "candidate_using_manual_bad_month_blacklist",
            "candidate_using_post_outcome_pnl_as_filter",
            "candidate_validated_only_on_paper_ledger",
            "candidate_passing_ai_or_manual_review_without_full_tests",
        ],
        "applies_to": [
            "family_candidate_release_gate",
            "candidate_backtest_evaluator",
            "month_stability_repair_evaluator",
            "all future family release gates",
            "all future promotion gates",
        ],
    }

    if critical:
        guard_status = "STRICT_MONTH_STABILITY_POLICY_GUARD_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_STRICT_EVALUATOR_INPUT"
        reason = "; ".join(critical)
        policy_written = False

    else:
        dump_json(POLICY_LATEST, strict_month_policy)

        guard_status = "STRICT_MONTH_STABILITY_POLICY_GUARD_ACTIVE"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "RECORD_STRICT_MONTH_STABILITY_FAILURE_LESSON_OR_QUEUE_NEW_RESEARCH"
        reason = (
            f"strict_rule_active=min_active_months:{MIN_ACTIVE_MONTHS};"
            f"min_positive_months:{MIN_POSITIVE_MONTHS};"
            f"strict_repair_found={strict_found}"
        )
        policy_written = True

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "guard_status": guard_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "strict_evaluator_source": str(STRICT_EVAL_LATEST),
        "policy_latest_path": str(POLICY_LATEST),
        "policy_written": policy_written,

        "strict_policy": strict_month_policy,

        "strict_evaluator_summary": {
            "evaluator_status": evaluator_status,
            "tested_filter_count": strict_eval.get("tested_filter_count"),
            "strict_month_only_count": strict_eval.get("strict_month_only_count"),
            "strict_full_quality_count": strict_eval.get("strict_full_quality_count"),
            "release_gate_feed": release_feed,
        },

        "release_gate_feed": {
            "STRICT_MONTH_STABILITY_POLICY_ACTIVE": policy_written,
            "STRICT_MONTH_STABILITY_MIN_ACTIVE_MONTHS": MIN_ACTIVE_MONTHS,
            "STRICT_MONTH_STABILITY_MIN_POSITIVE_MONTHS": MIN_POSITIVE_MONTHS,
            "STRICT_MONTH_STABILITY_MIN_POSITIVE_MONTH_RATE": MIN_POSITIVE_MONTH_RATE,
            "LOOSE_055_MONTH_RATE_DEPRECATED_FOR_RELEASE": True,
            "RELEASE_PASS_FROM_THIS_POLICY_GUARD": False,
            "status": guard_status,
        },

        "decision": {
            "candidate_generation_recommended_now": False,
            "repair_candidate_contract_recommended": False if not strict_found else True,
            "family_release_recommended": False,
            "promotion_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "next_module": "edge_factory_os_strict_month_stability_failure_lesson_recorder_v1.py" if not strict_found else None,
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

    out_json = RUN_DIR / "strict_month_stability_policy_guard_v1_state.json"
    out_md = RUN_DIR / "strict_month_stability_policy_guard_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS STRICT MONTH STABILITY POLICY GUARD v1

guard_status: {guard_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

policy_written: {policy_written}  
policy_latest_path: {POLICY_LATEST}

## Strict Policy

{json.dumps(strict_month_policy, indent=2, default=str)}

## Strict Evaluator Summary

{json.dumps(result["strict_evaluator_summary"], indent=2, default=str)}

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
    print("EDGE FACTORY OS STRICT MONTH STABILITY POLICY GUARD v1")
    print("=" * 100)
    print(f"guard_status: {guard_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("STRICT POLICY")
    print("-" * 100)
    print(f"min_active_months: {MIN_ACTIVE_MONTHS}")
    print(f"min_positive_months: {MIN_POSITIVE_MONTHS}")
    print(f"min_positive_month_rate: {MIN_POSITIVE_MONTH_RATE}")
    print("loose_055_month_rate_deprecated_for_release: True")
    print()
    print("STRICT EVALUATOR SUMMARY")
    print("-" * 100)
    print(result["strict_evaluator_summary"])
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
