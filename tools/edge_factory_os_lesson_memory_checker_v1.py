from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_lesson_memory_checker_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

LESSON_INDEX_PATH = (
    BASE_DIR
    / "edge_factory_os_lesson_memory"
    / "lesson_memory_index.json"
)

BLOCKLIST_PATH = (
    BASE_DIR
    / "edge_factory_os_lesson_memory"
    / "candidate_route_blocklist.json"
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

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"lesson_memory_checker_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "lesson_memory_checker_latest.json"
LATEST_MD = OUT_ROOT / "lesson_memory_checker_latest.md"


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


def find_blocked_route(blocklist: Dict[str, Any], route_hash: str) -> Optional[Dict[str, Any]]:
    routes = blocklist.get("blocked_routes")

    if not isinstance(routes, list):
        return None

    for route in routes:
        if isinstance(route, dict) and route.get("route_hash") == route_hash:
            return route

    return None


def find_lesson(index: Dict[str, Any], lesson_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not lesson_id:
        return None

    lessons = index.get("lessons")

    if not isinstance(lessons, list):
        return None

    for lesson in lessons:
        if isinstance(lesson, dict) and lesson.get("lesson_id") == lesson_id:
            return lesson

    return None


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    index = load_json(LESSON_INDEX_PATH)
    blocklist = load_json(BLOCKLIST_PATH)
    full_eval = load_json(FULL_UNIVERSE_EVAL_LATEST)
    regime_eval = load_json(REGIME_EVAL_LATEST)

    if not isinstance(index, dict):
        critical.append("lesson_memory_index_missing_or_unreadable")
        index = {}

    if not isinstance(blocklist, dict):
        critical.append("candidate_route_blocklist_missing_or_unreadable")
        blocklist = {}

    if not isinstance(full_eval, dict):
        critical.append("full_universe_evaluator_latest_missing")
        full_eval = {}

    if not isinstance(regime_eval, dict):
        attention.append("regime_evaluator_latest_missing")
        regime_eval = {}

    route_payload = route_signature_payload(full_eval, regime_eval)
    route_hash = stable_hash(route_payload)

    blocked_route = find_blocked_route(blocklist, route_hash)
    lesson = find_lesson(index, blocked_route.get("lesson_id") if blocked_route else None)

    if critical:
        checker_status = "LESSON_MEMORY_CHECKER_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_LESSON_MEMORY_INPUTS"
        reason = "; ".join(critical)

        lesson_memory_no_repeat_failure_pass = False
        route_blocked_by_lesson_memory = False

    elif blocked_route:
        checker_status = "LESSON_MEMORY_ROUTE_BLOCKED_KNOWN_FAILURE"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "DO_NOT_REPEAT_ROUTE_WITHOUT_NEW_EVIDENCE_QUEUE_NEW_RESEARCH_DIRECTION"
        reason = f"route_hash={route_hash}; lesson_id={blocked_route.get('lesson_id')}"

        lesson_memory_no_repeat_failure_pass = False
        route_blocked_by_lesson_memory = True

    else:
        checker_status = "LESSON_MEMORY_NO_REPEAT_FAILURE_FOUND"
        severity = "OK"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "ALLOW_RESEARCH_ROUTE_TO_CONTINUE_TO_OTHER_GATES"
        reason = f"route_hash={route_hash}; not found in blocklist"

        lesson_memory_no_repeat_failure_pass = True
        route_blocked_by_lesson_memory = False

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "checker_status": checker_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "lesson_index_path": str(LESSON_INDEX_PATH),
        "blocklist_path": str(BLOCKLIST_PATH),

        "route_signature": route_payload,
        "route_hash": route_hash,
        "route_blocked_by_lesson_memory": route_blocked_by_lesson_memory,
        "blocked_route": blocked_route,
        "matched_lesson": lesson,

        "release_gate_feed": {
            "LESSON_MEMORY_NO_REPEAT_FAILURE_PASS": lesson_memory_no_repeat_failure_pass,
            "status": checker_status,
            "route_hash": route_hash,
            "route_blocked_by_lesson_memory": route_blocked_by_lesson_memory,
            "release_allowed_from_lesson_memory_alone": False,
        },

        "decision": {
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "family_disable_recommended": False,
            "live_or_real_order_recommended": False,
            "repeat_same_route_recommended": False if route_blocked_by_lesson_memory else None,
            "why_no_repeat": (
                [
                    "route_already_failed_full_universe_release_validation",
                    "same_ret3_threshold_hold_route_blocked_without_new_evidence",
                    "paper_ledger_improvement_not_sufficient_to_reopen",
                    "manual_or_ai_opinion_not_sufficient_to_reopen",
                ]
                if route_blocked_by_lesson_memory
                else []
            ),
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

    out_json = RUN_DIR / "lesson_memory_checker_v1_state.json"
    out_md = RUN_DIR / "lesson_memory_checker_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS LESSON MEMORY CHECKER v1

checker_status: {checker_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

route_hash: {route_hash}  
route_blocked_by_lesson_memory: {route_blocked_by_lesson_memory}

## Release Gate Feed

{json.dumps(result["release_gate_feed"], indent=2, default=str)}

## Route Signature

{json.dumps(route_payload, indent=2, default=str)}

## Blocked Route

{json.dumps(blocked_route, indent=2, default=str)}

## Matched Lesson

{json.dumps(lesson, indent=2, default=str)[:16000]}

## Decision

runtime_change_recommended: False  
capital_change_recommended: False  
family_disable_recommended: False  
live_or_real_order_recommended: False

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
    print("EDGE FACTORY OS LESSON MEMORY CHECKER v1")
    print("=" * 100)
    print(f"checker_status: {checker_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("ROUTE")
    print("-" * 100)
    print(f"route_hash: {route_hash}")
    print(f"route_blocked_by_lesson_memory: {route_blocked_by_lesson_memory}")
    print(f"lesson_id: {blocked_route.get('lesson_id') if blocked_route else None}")
    print()
    print("RELEASE GATE FEED")
    print("-" * 100)
    print(result["release_gate_feed"])
    print()
    print("DECISION")
    print("-" * 100)
    print("runtime_change_recommended: False")
    print("capital_change_recommended: False")
    print("family_disable_recommended: False")
    print("live_or_real_order_recommended: False")
    print(f"repeat_same_route_recommended: {result['decision'].get('repeat_same_route_recommended')}")
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
