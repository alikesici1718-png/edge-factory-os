from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_strict_month_stability_failure_lesson_recorder_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

POLICY_GUARD_LATEST = (
    BASE_DIR
    / "edge_factory_os_strict_month_stability_policy_guard_v1"
    / "strict_month_stability_policy_guard_latest.json"
)

STRICT_EVAL_LATEST = (
    BASE_DIR
    / "edge_factory_os_month_stability_repair_evaluator_v1"
    / "month_stability_repair_evaluator_latest.json"
)

REGIME_FILTERED_EVAL_LATEST = (
    BASE_DIR
    / "edge_factory_os_regime_filtered_candidate_evaluator_v1"
    / "regime_filtered_candidate_evaluator_latest.json"
)

CANDIDATE_CONTRACT_LATEST = (
    BASE_DIR
    / "edge_factory_os_candidate_contracts"
    / "regime_filtered_impulse_candidate_contract_latest.json"
)

LESSON_INDEX_ROOT = BASE_DIR / "edge_factory_os_lesson_memory"
LESSON_INDEX_PATH = LESSON_INDEX_ROOT / "lesson_memory_index.json"
BLOCKLIST_PATH = LESSON_INDEX_ROOT / "candidate_route_blocklist.json"

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"strict_month_stability_failure_lesson_recorder_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "strict_month_stability_failure_lesson_recorder_latest.json"
LATEST_MD = OUT_ROOT / "strict_month_stability_failure_lesson_recorder_latest.md"


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


def safe_get(d: Dict[str, Any], path: List[str], default=None):
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def load_index() -> Dict[str, Any]:
    obj = load_json(LESSON_INDEX_PATH)
    if isinstance(obj, dict):
        if not isinstance(obj.get("lessons"), list):
            obj["lessons"] = []
        return obj

    return {
        "schema": "edge_factory_os_lesson_memory_index_v1",
        "created_at_utc": NOW.isoformat(),
        "updated_at_utc": NOW.isoformat(),
        "lessons": [],
    }


def load_blocklist() -> Dict[str, Any]:
    obj = load_json(BLOCKLIST_PATH)
    if isinstance(obj, dict):
        if not isinstance(obj.get("blocked_routes"), list):
            obj["blocked_routes"] = []
        return obj

    return {
        "schema": "edge_factory_os_candidate_route_blocklist_v1",
        "created_at_utc": NOW.isoformat(),
        "updated_at_utc": NOW.isoformat(),
        "blocked_routes": [],
    }


def upsert_lesson(index: Dict[str, Any], lesson: Dict[str, Any]) -> Dict[str, Any]:
    lessons = index.get("lessons")
    if not isinstance(lessons, list):
        lessons = []

    lesson_id = lesson.get("lesson_id")
    replaced = False
    new_lessons = []

    for old in lessons:
        if isinstance(old, dict) and old.get("lesson_id") == lesson_id:
            new_lessons.append(lesson)
            replaced = True
        else:
            new_lessons.append(old)

    if not replaced:
        new_lessons.append(lesson)

    index["lessons"] = new_lessons
    index["updated_at_utc"] = NOW.isoformat()
    return index


def upsert_blocklist(blocklist: Dict[str, Any], route_hash: str, record: Dict[str, Any]) -> Dict[str, Any]:
    routes = blocklist.get("blocked_routes")
    if not isinstance(routes, list):
        routes = []

    replaced = False
    new_routes = []

    for old in routes:
        if isinstance(old, dict) and old.get("route_hash") == route_hash:
            new_routes.append(record)
            replaced = True
        else:
            new_routes.append(old)

    if not replaced:
        new_routes.append(record)

    blocklist["blocked_routes"] = new_routes
    blocklist["updated_at_utc"] = NOW.isoformat()
    return blocklist


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    LESSON_INDEX_ROOT.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    policy_guard = load_json(POLICY_GUARD_LATEST)
    strict_eval = load_json(STRICT_EVAL_LATEST)
    candidate_eval = load_json(REGIME_FILTERED_EVAL_LATEST)
    candidate_contract = load_json(CANDIDATE_CONTRACT_LATEST)

    if not isinstance(policy_guard, dict):
        critical.append("strict_month_stability_policy_guard_latest_missing")
        policy_guard = {}

    if not isinstance(strict_eval, dict):
        critical.append("strict_month_stability_repair_evaluator_latest_missing")
        strict_eval = {}

    if not isinstance(candidate_eval, dict):
        critical.append("regime_filtered_candidate_evaluator_latest_missing")
        candidate_eval = {}

    if not isinstance(candidate_contract, dict):
        critical.append("candidate_contract_latest_missing")
        candidate_contract = {}

    if policy_guard.get("guard_status") != "STRICT_MONTH_STABILITY_POLICY_GUARD_ACTIVE":
        critical.append(f"policy_guard_not_active:{policy_guard.get('guard_status')}")

    if strict_eval.get("evaluator_status") != "MONTH_STABILITY_REPAIR_EVALUATOR_STRICT_11_OF_12_NOT_FOUND":
        critical.append(f"strict_eval_not_failure:{strict_eval.get('evaluator_status')}")

    strict_feed = strict_eval.get("release_gate_feed") or {}
    if strict_feed.get("STRICT_11_OF_12_REPAIR_FOUND") is not False:
        critical.append("strict_eval_did_not_confirm_no_11_of_12_repair")

    if strict_feed.get("RELEASE_PASS_FROM_THIS_EVALUATOR") is not False:
        critical.append("strict_eval_release_pass_unexpected")

    candidate_route_hash = candidate_eval.get("candidate_route_hash") or candidate_contract.get("candidate_route_hash")
    known_failed_route_hash = safe_get(candidate_contract, ["blocked_route_guard", "known_failed_route_hash"])

    if not candidate_route_hash:
        critical.append("candidate_route_hash_missing")

    lesson_id = f"LESSON_STRICT_MONTH_STABILITY_FAILURE_{candidate_route_hash}"

    if critical:
        recorder_status = "STRICT_MONTH_STABILITY_FAILURE_LESSON_RECORDER_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_INPUTS_BEFORE_LESSON_RECORD"
        reason = "; ".join(critical)
        lesson_written = False
        blocklist_written = False
        lesson = None

    else:
        strict_rule = policy_guard.get("strict_policy") or safe_get(policy_guard, ["strict_policy"], {})
        old_preview = strict_eval.get("old_best_full_quality_preview_filter_under_strict_rule")
        top_evaluated = strict_eval.get("top_evaluated_filters_under_strict_sort")

        lesson = {
            "lesson_schema": "edge_factory_os_failure_lesson_v1",
            "lesson_id": lesson_id,
            "created_at_utc": NOW.isoformat(),

            "lesson_type": "STRICT_MONTH_STABILITY_FAILURE",
            "severity": "HIGH",

            "family": "regime_filtered_impulse_long_research",
            "candidate_key": candidate_contract.get("candidate_key"),
            "candidate_route_hash": candidate_route_hash,
            "known_prior_failed_route_hash": known_failed_route_hash,

            "claim": (
                "The regime-filtered impulse candidate was promising on trade/PF/OOS metrics, "
                "but failed strict one-year month stability. No tested repair filter achieved "
                "12 active months with at least 11 positive months."
            ),

            "strict_policy": {
                "min_active_months": 12,
                "min_positive_months": 11,
                "min_positive_month_rate": 11 / 12,
                "loose_055_month_rate_deprecated_for_release": True,
                "release_requires_strict_11_of_12": True,
            },

            "evidence_summary": {
                "policy_guard_status": policy_guard.get("guard_status"),
                "strict_eval_status": strict_eval.get("evaluator_status"),
                "tested_filter_count": strict_eval.get("tested_filter_count"),
                "strict_month_only_count": strict_eval.get("strict_month_only_count"),
                "strict_full_quality_count": strict_eval.get("strict_full_quality_count"),
                "release_gate_feed": strict_eval.get("release_gate_feed"),

                "candidate_evaluator_status": candidate_eval.get("evaluator_status"),
                "candidate_promising": candidate_eval.get("candidate_promising"),
                "candidate_full_release_quality_pass": candidate_eval.get("full_release_quality_pass"),
                "candidate_only_month_stability_failed": candidate_eval.get("only_month_stability_failed"),
                "candidate_failed_checks": candidate_eval.get("failed_checks"),
                "candidate_passed_checks": candidate_eval.get("passed_checks"),
                "candidate_comparison_to_baseline": candidate_eval.get("comparison_to_baseline"),

                "old_loose_preview_filter_under_strict_rule": old_preview,
                "top_evaluated_filters_under_strict_sort": top_evaluated[:5] if isinstance(top_evaluated, list) else top_evaluated,
            },

            "failure_modes": [
                "promising_trade_metrics_but_failed_strict_month_stability",
                "loose_positive_month_rate_055_was_insufficient",
                "no_pre_outcome_repair_filter_reached_11_of_12",
                "candidate_cannot_be_released_or_repaired_under_current_evidence",
            ],

            "block_rule": {
                "block_releasing_this_candidate_route": True,
                "blocked_route_hash": candidate_route_hash,
                "blocked_candidate_key": candidate_contract.get("candidate_key"),
                "blocked_reason": "strict_11_of_12_month_stability_not_found",
                "minimum_new_evidence_required_to_reopen": [
                    "a new route hash materially different from this candidate",
                    "strict month stability >=12 active months and >=11 positive months",
                    "full-universe backtest on 285-symbol 1Y panel",
                    "train/OOS pass",
                    "cost/slippage pass",
                    "symbol concentration pass",
                    "release gate pass",
                ],
                "not_sufficient_to_reopen": [
                    "positive_month_rate >= 0.55 only",
                    "7/12 positive months",
                    "10/12 active months",
                    "PF or OOS improvement without strict month stability",
                    "manual bad-month blacklist",
                    "single-symbol or paper-ledger improvement",
                    "AI/manual opinion without full tests",
                ],
            },

            "recommended_next_research": [
                "Do not build a repair candidate contract from this diagnostic result.",
                "Queue a new research direction or stronger pre-outcome filters.",
                "Keep strict 11-of-12 month stability as a global release policy.",
                "Archive this candidate route unless genuinely new features create a new route hash.",
            ],

            "actions_allowed_now": {
                "candidate_generation_recommended": False,
                "repair_candidate_contract_recommended": False,
                "family_release_recommended": False,
                "promotion_recommended": False,
                "runtime_change_recommended": False,
                "capital_change_recommended": False,
                "live_or_real_order_recommended": False,
            },

            "sources": {
                "policy_guard_latest": str(POLICY_GUARD_LATEST),
                "strict_evaluator_latest": str(STRICT_EVAL_LATEST),
                "candidate_evaluator_latest": str(REGIME_FILTERED_EVAL_LATEST),
                "candidate_contract_latest": str(CANDIDATE_CONTRACT_LATEST),
            },
        }

        index = load_index()
        blocklist = load_blocklist()

        index = upsert_lesson(index, lesson)

        block_record = {
            "route_hash": candidate_route_hash,
            "lesson_id": lesson_id,
            "created_at_utc": NOW.isoformat(),
            "family": "regime_filtered_impulse_long_research",
            "candidate_key": candidate_contract.get("candidate_key"),
            "block_repeating_same_route_without_new_evidence": True,
            "blocked_reason": "strict_11_of_12_month_stability_failure",
            "minimum_new_evidence_required_to_reopen": lesson["block_rule"]["minimum_new_evidence_required_to_reopen"],
            "not_sufficient_to_reopen": lesson["block_rule"]["not_sufficient_to_reopen"],
        }

        blocklist = upsert_blocklist(blocklist, candidate_route_hash, block_record)

        dump_json(LESSON_INDEX_PATH, index)
        dump_json(BLOCKLIST_PATH, blocklist)
        dump_json(RUN_DIR / f"{lesson_id}.json", lesson)

        recorder_status = "STRICT_MONTH_STABILITY_FAILURE_LESSON_RECORDED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "QUEUE_NEW_RESEARCH_DIRECTION_OR_RUN_TOP_LEVEL_RELEASE_GATE_UPDATE"
        reason = f"lesson_id={lesson_id}; blocked_route_hash={candidate_route_hash}"
        lesson_written = True
        blocklist_written = True

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "recorder_status": recorder_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "lesson": lesson,
        "lesson_id": lesson_id if candidate_route_hash else None,
        "candidate_route_hash": candidate_route_hash,
        "known_prior_failed_route_hash": known_failed_route_hash,

        "lesson_index_path": str(LESSON_INDEX_PATH),
        "blocklist_path": str(BLOCKLIST_PATH),
        "lesson_written": lesson_written,
        "blocklist_written": blocklist_written,

        "release_gate_feed": {
            "STRICT_MONTH_STABILITY_FAILURE_LESSON_RECORDED": lesson_written,
            "CANDIDATE_ROUTE_BLOCKED_BY_STRICT_MONTH_STABILITY_LESSON": blocklist_written,
            "STRICT_11_OF_12_REQUIRED_FOR_REOPEN": True,
            "RELEASE_PASS_FROM_THIS_RECORDER": False,
            "status": recorder_status,
        },

        "decision": {
            "candidate_generation_recommended_now": False,
            "repair_candidate_contract_recommended": False,
            "family_release_recommended": False,
            "promotion_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "next_module": "edge_factory_os_new_research_direction_queue_v2.py" if lesson_written else None,
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

    out_json = RUN_DIR / "strict_month_stability_failure_lesson_recorder_v1_state.json"
    out_md = RUN_DIR / "strict_month_stability_failure_lesson_recorder_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS STRICT MONTH STABILITY FAILURE LESSON RECORDER v1

recorder_status: {recorder_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

lesson_written: {lesson_written}  
blocklist_written: {blocklist_written}  
lesson_id: {lesson_id if candidate_route_hash else None}  
candidate_route_hash: {candidate_route_hash}  
known_prior_failed_route_hash: {known_failed_route_hash}

lesson_index_path: {LESSON_INDEX_PATH}  
blocklist_path: {BLOCKLIST_PATH}

## Release Gate Feed

{json.dumps(result["release_gate_feed"], indent=2, default=str)}

## Lesson Summary

{json.dumps(lesson, indent=2, default=str)[:24000]}

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
    print("EDGE FACTORY OS STRICT MONTH STABILITY FAILURE LESSON RECORDER v1")
    print("=" * 100)
    print(f"recorder_status: {recorder_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("LESSON")
    print("-" * 100)
    print(f"lesson_written: {lesson_written}")
    print(f"blocklist_written: {blocklist_written}")
    print(f"lesson_id: {lesson_id if candidate_route_hash else None}")
    print(f"candidate_route_hash: {candidate_route_hash}")
    print(f"known_prior_failed_route_hash: {known_failed_route_hash}")
    print(f"lesson_index_path: {LESSON_INDEX_PATH}")
    print(f"blocklist_path: {BLOCKLIST_PATH}")
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
