from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_full_universe_failure_lesson_recorder_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

RELEASE_GATE_V3_LATEST = (
    BASE_DIR
    / "edge_factory_os_family_candidate_release_gate_v3"
    / "family_candidate_release_gate_v3_latest.json"
)

FULL_UNIVERSE_EVAL_LATEST = (
    BASE_DIR
    / "edge_factory_os_full_universe_offline_backtest_evaluator_v1"
    / "full_universe_offline_backtest_evaluator_latest.json"
)

REGIME_EVAL_LATEST = (
    BASE_DIR
    / "edge_factory_os_regime_bucket_evaluator_v1"
    / "regime_bucket_evaluator_latest.json"
)

COST_EVAL_LATEST = (
    BASE_DIR
    / "edge_factory_os_cost_sensitivity_evaluator_v1"
    / "cost_sensitivity_evaluator_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"full_universe_failure_lesson_recorder_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "full_universe_failure_lesson_recorder_latest.json"
LATEST_MD = OUT_ROOT / "full_universe_failure_lesson_recorder_latest.md"

LESSON_INDEX_ROOT = BASE_DIR / "edge_factory_os_lesson_memory"
LESSON_INDEX_PATH = LESSON_INDEX_ROOT / "lesson_memory_index.json"
LESSON_BLOCKLIST_PATH = LESSON_INDEX_ROOT / "candidate_route_blocklist.json"


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


def stable_hash(obj: Any) -> str:
    text = json.dumps(obj, sort_keys=True, default=str)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def safe_get(d: Dict[str, Any], path: List[str], default=None):
    cur = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def load_index(path: Path) -> Dict[str, Any]:
    obj = load_json(path)
    if isinstance(obj, dict):
        return obj

    return {
        "schema": "edge_factory_os_lesson_memory_index_v1",
        "created_at_utc": NOW.isoformat(),
        "updated_at_utc": NOW.isoformat(),
        "lessons": [],
    }


def load_blocklist(path: Path) -> Dict[str, Any]:
    obj = load_json(path)
    if isinstance(obj, dict):
        return obj

    return {
        "schema": "edge_factory_os_candidate_route_blocklist_v1",
        "created_at_utc": NOW.isoformat(),
        "updated_at_utc": NOW.isoformat(),
        "blocked_routes": [],
    }


def route_signature_payload(full_eval: Dict[str, Any], regime_eval: Dict[str, Any]) -> Dict[str, Any]:
    best = full_eval.get("best_candidate") or {}
    params = best.get("params") or {}

    return {
        "family": "impulse_long",
        "route_family": "post_impulse_drift_long",
        "candidate_source": "ret3_threshold_hold_entry_range_market_filter",
        "best_candidate_id": best.get("candidate_id"),
        "threshold_coin_ret3_bps": params.get("threshold_coin_ret3_bps"),
        "hold_hours": params.get("hold_hours"),
        "entry_range_cap_bps": params.get("entry_range_cap_bps"),
        "mkt_filter": params.get("mkt_filter"),
        "regime_best_filter_id": safe_get(regime_eval, ["best_filter", "filter_id"]),
        "regime_best_filter_description": safe_get(regime_eval, ["best_filter", "description"]),
    }


def build_lesson(
    release_gate: Dict[str, Any],
    full_eval: Dict[str, Any],
    regime_eval: Dict[str, Any],
    cost_eval: Dict[str, Any],
) -> Dict[str, Any]:
    route_payload = route_signature_payload(full_eval, regime_eval)
    route_hash = stable_hash(route_payload)

    lesson_id = f"LESSON_FULL_UNIVERSE_FAILURE_{route_hash}"

    failed_checks = release_gate.get("failed_checks") or []
    passed_checks = release_gate.get("passed_checks") or []

    lesson = {
        "lesson_schema": "edge_factory_os_failure_lesson_v1",
        "lesson_id": lesson_id,
        "created_at_utc": NOW.isoformat(),

        "lesson_type": "FULL_UNIVERSE_RELEASE_FAILURE",
        "severity": "HIGH",
        "family": "impulse_long",
        "route_hash": route_hash,
        "route_signature": route_payload,

        "claim": (
            "The impulse_long ret3-threshold / hold / entry-range / market-filter route showed paper-sample promise "
            "but failed full-universe release-quality validation."
        ),

        "evidence_summary": {
            "release_gate_status": release_gate.get("release_status"),
            "candidate_family_output_allowed": release_gate.get("candidate_family_output_allowed"),
            "family_release_allowed": release_gate.get("family_release_allowed"),
            "promotion_allowed": release_gate.get("promotion_allowed"),

            "full_universe_status": full_eval.get("evaluator_status"),
            "evaluated_candidate_count": full_eval.get("evaluated_candidate_count"),
            "release_pass_candidate_count": full_eval.get("release_pass_candidate_count"),
            "failed_reason_counts": full_eval.get("failed_reason_counts"),

            "best_candidate_id": safe_get(full_eval, ["best_candidate", "candidate_id"]),
            "best_candidate_failed_checks": safe_get(full_eval, ["best_candidate", "failed_checks"]),
            "best_candidate_summary_all": safe_get(full_eval, ["best_candidate", "summary_all"]),
            "best_candidate_summary_train": safe_get(full_eval, ["best_candidate", "summary_train"]),
            "best_candidate_summary_oos": safe_get(full_eval, ["best_candidate", "summary_oos"]),

            "regime_status": regime_eval.get("evaluator_status"),
            "regime_release_gate_feed": regime_eval.get("release_gate_feed"),

            "cost_status": cost_eval.get("evaluator_status"),
            "cost_release_gate_feed": cost_eval.get("release_gate_feed"),

            "passed_release_checks": passed_checks,
            "failed_release_checks": failed_checks,
        },

        "failure_modes": [
            "no_release_quality_candidate_across_full_universe_grid",
            "month_stability_failure",
            "train_oos_instability",
            "cost_sensitivity_not_recovered",
            "regime_filter_promising_but_not_release_pass",
            "symbol_concentration_risk_not_cleared",
        ],

        "block_rule": {
            "block_repeating_same_route_without_new_evidence": True,
            "blocked_route_hash": route_hash,
            "blocked_family": "impulse_long",
            "blocked_candidate_source": "ret3_threshold_hold_entry_range_market_filter",
            "minimum_new_evidence_required_to_reopen": [
                "new_feature_columns_not_used_in_this_test",
                "new_exit_logic_or_hold_logic_not_equivalent_to_current_grid",
                "new_full_universe_panel_or_new_time_period",
                "new validation method that directly addresses failed month/train/OOS stability",
                "clear evidence that previous failure was caused by data/implementation error",
            ],
            "not_sufficient_to_reopen": [
                "same ret3 threshold grid",
                "same hold-hour grid",
                "same entry_range cap grid",
                "paper ledger improvement only",
                "single symbol improvement",
                "AI/manual opinion without new full-universe evidence",
            ],
        },

        "recommended_next_research": [
            "Do not keep tuning the same ret3 threshold route blindly.",
            "Queue a new research direction focused on features that explain month/regime instability.",
            "Consider different family archetypes instead of trying to rescue this route.",
            "If revisiting impulse_long, require new explanatory features or materially different exit logic.",
        ],

        "actions_allowed_now": {
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "family_disable_recommended": False,
            "live_or_real_order_recommended": False,
            "candidate_release_recommended": False,
            "promotion_recommended": False,
        },

        "sources": {
            "release_gate_v3": str(RELEASE_GATE_V3_LATEST),
            "full_universe_evaluator": str(FULL_UNIVERSE_EVAL_LATEST),
            "regime_evaluator": str(REGIME_EVAL_LATEST),
            "cost_evaluator": str(COST_EVAL_LATEST),
        },
    }

    return lesson


def upsert_lesson(index: Dict[str, Any], lesson: Dict[str, Any]) -> Dict[str, Any]:
    lessons = index.get("lessons")
    if not isinstance(lessons, list):
        lessons = []

    lesson_id = lesson.get("lesson_id")

    replaced = False
    new_lessons = []

    for existing in lessons:
        if isinstance(existing, dict) and existing.get("lesson_id") == lesson_id:
            new_lessons.append(lesson)
            replaced = True
        else:
            new_lessons.append(existing)

    if not replaced:
        new_lessons.append(lesson)

    index["lessons"] = new_lessons
    index["updated_at_utc"] = NOW.isoformat()
    return index


def upsert_block_route(blocklist: Dict[str, Any], lesson: Dict[str, Any]) -> Dict[str, Any]:
    blocked_routes = blocklist.get("blocked_routes")
    if not isinstance(blocked_routes, list):
        blocked_routes = []

    block_rule = lesson.get("block_rule") or {}
    route_hash = block_rule.get("blocked_route_hash")

    record = {
        "route_hash": route_hash,
        "lesson_id": lesson.get("lesson_id"),
        "created_at_utc": lesson.get("created_at_utc"),
        "family": lesson.get("family"),
        "candidate_source": block_rule.get("blocked_candidate_source"),
        "block_repeating_same_route_without_new_evidence": True,
        "minimum_new_evidence_required_to_reopen": block_rule.get("minimum_new_evidence_required_to_reopen"),
        "not_sufficient_to_reopen": block_rule.get("not_sufficient_to_reopen"),
    }

    replaced = False
    new_routes = []

    for existing in blocked_routes:
        if isinstance(existing, dict) and existing.get("route_hash") == route_hash:
            new_routes.append(record)
            replaced = True
        else:
            new_routes.append(existing)

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

    release_gate = load_json(RELEASE_GATE_V3_LATEST)
    full_eval = load_json(FULL_UNIVERSE_EVAL_LATEST)
    regime_eval = load_json(REGIME_EVAL_LATEST)
    cost_eval = load_json(COST_EVAL_LATEST)

    if not isinstance(release_gate, dict):
        critical.append("release_gate_v3_latest_missing")
        release_gate = {}

    if not isinstance(full_eval, dict):
        critical.append("full_universe_evaluator_latest_missing")
        full_eval = {}

    if not isinstance(regime_eval, dict):
        attention.append("regime_evaluator_latest_missing")
        regime_eval = {}

    if not isinstance(cost_eval, dict):
        attention.append("cost_evaluator_latest_missing")
        cost_eval = {}

    release_status = release_gate.get("release_status")
    full_status = full_eval.get("evaluator_status")

    if release_status != "FAMILY_CANDIDATE_RELEASE_GATE_V3_BLOCKED_FULL_UNIVERSE_FAILED":
        attention.append(f"release_gate_v3_not_full_universe_failed_status:{release_status}")

    if full_status != "FULL_UNIVERSE_BACKTEST_EVALUATOR_NO_RELEASE_CANDIDATE":
        attention.append(f"full_universe_evaluator_not_no_release_candidate:{full_status}")

    if critical:
        recorder_status = "FULL_UNIVERSE_FAILURE_LESSON_RECORDER_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_MISSING_INPUTS"
        reason = "; ".join(critical)
        lesson = None
        index_written = False
        blocklist_written = False

    else:
        lesson = build_lesson(release_gate, full_eval, regime_eval, cost_eval)

        index = load_index(LESSON_INDEX_PATH)
        blocklist = load_blocklist(LESSON_BLOCKLIST_PATH)

        index = upsert_lesson(index, lesson)
        blocklist = upsert_block_route(blocklist, lesson)

        dump_json(LESSON_INDEX_PATH, index)
        dump_json(LESSON_BLOCKLIST_PATH, blocklist)

        lesson_path = RUN_DIR / f"{lesson['lesson_id']}.json"
        dump_json(lesson_path, lesson)

        recorder_status = "FULL_UNIVERSE_FAILURE_LESSON_RECORDED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "QUEUE_NEW_RESEARCH_DIRECTION_AND_UPDATE_RELEASE_GATE_WITH_LESSON_MEMORY"
        reason = f"lesson_id={lesson['lesson_id']}; route_hash={lesson['route_hash']}"
        index_written = True
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

        "lesson_index_path": str(LESSON_INDEX_PATH),
        "blocklist_path": str(LESSON_BLOCKLIST_PATH),
        "index_written": index_written,
        "blocklist_written": blocklist_written,

        "sources": {
            "release_gate_v3": str(RELEASE_GATE_V3_LATEST),
            "full_universe_evaluator": str(FULL_UNIVERSE_EVAL_LATEST),
            "regime_evaluator": str(REGIME_EVAL_LATEST),
            "cost_evaluator": str(COST_EVAL_LATEST),
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

    out_json = RUN_DIR / "full_universe_failure_lesson_recorder_v1_state.json"
    out_md = RUN_DIR / "full_universe_failure_lesson_recorder_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS FULL UNIVERSE FAILURE LESSON RECORDER v1

recorder_status: {recorder_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

lesson_index_path: {LESSON_INDEX_PATH}  
blocklist_path: {LESSON_BLOCKLIST_PATH}  
index_written: {index_written}  
blocklist_written: {blocklist_written}

## Lesson

{json.dumps(lesson, indent=2, default=str)[:24000]}

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
    print("EDGE FACTORY OS FULL UNIVERSE FAILURE LESSON RECORDER v1")
    print("=" * 100)
    print(f"recorder_status: {recorder_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("LESSON MEMORY")
    print("-" * 100)
    print(f"lesson_index_path: {LESSON_INDEX_PATH}")
    print(f"blocklist_path: {LESSON_BLOCKLIST_PATH}")
    print(f"index_written: {index_written}")
    print(f"blocklist_written: {blocklist_written}")
    print()
    print("LESSON")
    print("-" * 100)
    print(json.dumps(lesson, indent=2, default=str)[:8000])
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
