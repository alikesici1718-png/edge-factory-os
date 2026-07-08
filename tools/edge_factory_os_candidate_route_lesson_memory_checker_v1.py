from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_candidate_route_lesson_memory_checker_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

CANDIDATE_CONTRACT_LATEST = (
    BASE_DIR
    / "edge_factory_os_candidate_contracts"
    / "regime_filtered_impulse_candidate_contract_latest.json"
)

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

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"candidate_route_lesson_memory_checker_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "candidate_route_lesson_memory_checker_latest.json"
LATEST_MD = OUT_ROOT / "candidate_route_lesson_memory_checker_latest.md"


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

    contract = load_json(CANDIDATE_CONTRACT_LATEST)
    index = load_json(LESSON_INDEX_PATH)
    blocklist = load_json(BLOCKLIST_PATH)

    if not isinstance(contract, dict):
        critical.append("candidate_contract_latest_missing_or_unreadable")
        contract = {}

    if not isinstance(index, dict):
        attention.append("lesson_memory_index_missing_or_unreadable")
        index = {}

    if not isinstance(blocklist, dict):
        critical.append("candidate_route_blocklist_missing_or_unreadable")
        blocklist = {}

    candidate_route_hash = contract.get("candidate_route_hash")
    known_failed_route_hash = None

    blocked_guard = contract.get("blocked_route_guard")
    if isinstance(blocked_guard, dict):
        known_failed_route_hash = blocked_guard.get("known_failed_route_hash")

    candidate_route_is_same_as_blocked = bool(
        candidate_route_hash
        and known_failed_route_hash
        and candidate_route_hash == known_failed_route_hash
    )

    if not candidate_route_hash:
        critical.append("candidate_route_hash_missing")

    if candidate_route_is_same_as_blocked:
        critical.append("candidate_route_hash_matches_known_failed_route")

    blocked_route = find_blocked_route(blocklist, str(candidate_route_hash)) if candidate_route_hash else None
    matched_lesson = find_lesson(index, blocked_route.get("lesson_id") if blocked_route else None)

    if critical:
        checker_status = "CANDIDATE_ROUTE_LESSON_MEMORY_CHECKER_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_CANDIDATE_CONTRACT_OR_LESSON_MEMORY"
        reason = "; ".join(critical)

        candidate_route_lesson_memory_pass = False
        candidate_route_blocked_by_lesson_memory = True
        backtest_allowed_by_lesson_memory = False

    elif blocked_route:
        checker_status = "CANDIDATE_ROUTE_BLOCKED_BY_LESSON_MEMORY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "DO_NOT_BACKTEST_BLOCKED_CANDIDATE_ROUTE_BUILD_NEW_CONTRACT"
        reason = f"candidate_route_hash={candidate_route_hash}; matched_lesson_id={blocked_route.get('lesson_id')}"

        candidate_route_lesson_memory_pass = False
        candidate_route_blocked_by_lesson_memory = True
        backtest_allowed_by_lesson_memory = False

    else:
        checker_status = "CANDIDATE_ROUTE_LESSON_MEMORY_PASS_NEW_ROUTE"
        severity = "OK"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_REGIME_FILTERED_CANDIDATE_BACKTEST_RUNNER"
        reason = f"candidate_route_hash={candidate_route_hash}; not found in blocklist"

        candidate_route_lesson_memory_pass = True
        candidate_route_blocked_by_lesson_memory = False
        backtest_allowed_by_lesson_memory = True

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "checker_status": checker_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "candidate_contract_source": str(CANDIDATE_CONTRACT_LATEST),
        "lesson_index_path": str(LESSON_INDEX_PATH),
        "blocklist_path": str(BLOCKLIST_PATH),

        "candidate_key": contract.get("candidate_key"),
        "contract_id": contract.get("contract_id"),
        "candidate_route_hash": candidate_route_hash,
        "known_failed_route_hash": known_failed_route_hash,
        "candidate_route_is_same_as_known_failed_route": candidate_route_is_same_as_blocked,

        "candidate_route_blocked_by_lesson_memory": candidate_route_blocked_by_lesson_memory,
        "blocked_route": blocked_route,
        "matched_lesson": matched_lesson,

        "release_gate_feed": {
            "CANDIDATE_ROUTE_LESSON_MEMORY_PASS": candidate_route_lesson_memory_pass,
            "status": checker_status,
            "candidate_route_hash": candidate_route_hash,
            "candidate_route_blocked_by_lesson_memory": candidate_route_blocked_by_lesson_memory,
            "backtest_allowed_by_lesson_memory": backtest_allowed_by_lesson_memory,
            "release_allowed_from_lesson_memory_alone": False,
        },

        "decision": {
            "candidate_backtest_allowed_by_lesson_memory": backtest_allowed_by_lesson_memory,
            "candidate_generation_recommended_now": False,
            "family_release_recommended": False,
            "promotion_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "repeat_known_failed_route_recommended": False,
            "next_module": "edge_factory_os_regime_filtered_candidate_backtest_runner_v1.py" if backtest_allowed_by_lesson_memory else None,
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

    out_json = RUN_DIR / "candidate_route_lesson_memory_checker_v1_state.json"
    out_md = RUN_DIR / "candidate_route_lesson_memory_checker_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS CANDIDATE ROUTE LESSON MEMORY CHECKER v1

checker_status: {checker_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

candidate_key: {contract.get("candidate_key")}  
contract_id: {contract.get("contract_id")}  
candidate_route_hash: {candidate_route_hash}  
known_failed_route_hash: {known_failed_route_hash}  
candidate_route_is_same_as_known_failed_route: {candidate_route_is_same_as_blocked}  
candidate_route_blocked_by_lesson_memory: {candidate_route_blocked_by_lesson_memory}

## Release Gate Feed

{json.dumps(result["release_gate_feed"], indent=2, default=str)}

## Blocked Route

{json.dumps(blocked_route, indent=2, default=str)}

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
    print("EDGE FACTORY OS CANDIDATE ROUTE LESSON MEMORY CHECKER v1")
    print("=" * 100)
    print(f"checker_status: {checker_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("ROUTE")
    print("-" * 100)
    print(f"candidate_key: {contract.get('candidate_key')}")
    print(f"contract_id: {contract.get('contract_id')}")
    print(f"candidate_route_hash: {candidate_route_hash}")
    print(f"known_failed_route_hash: {known_failed_route_hash}")
    print(f"candidate_route_is_same_as_known_failed_route: {candidate_route_is_same_as_blocked}")
    print(f"candidate_route_blocked_by_lesson_memory: {candidate_route_blocked_by_lesson_memory}")
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
