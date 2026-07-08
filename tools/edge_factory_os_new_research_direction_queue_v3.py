from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_new_research_direction_queue_v3"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

BROADER_EVAL_LATEST = (
    BASE_DIR
    / "edge_factory_os_broader_month_feature_engine_evaluator_v1"
    / "broader_month_feature_engine_evaluator_latest.json"
)

STRICT_POLICY_LATEST = (
    BASE_DIR
    / "edge_factory_os_policy_guards"
    / "strict_month_stability_policy_latest.json"
)

CANONICAL_GUARD_LATEST = (
    BASE_DIR
    / "edge_factory_os_canonical_month_window_guard_v1"
    / "canonical_month_window_guard_latest.json"
)

ACTION_GUARD_LATEST = (
    BASE_DIR
    / "edge_factory_os_action_prerequisite_guard_v1"
    / "action_prerequisite_guard_latest.json"
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
RUN_DIR = OUT_ROOT / f"new_research_direction_queue_v3_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "new_research_direction_queue_v3_latest.json"
LATEST_MD = OUT_ROOT / "new_research_direction_queue_v3_latest.md"


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
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def extract_blocked_hashes(blocklist: Dict[str, Any]) -> List[str]:
    rows = blocklist.get("blocked_routes")
    if not isinstance(rows, list):
        return []

    out = []
    for row in rows:
        if isinstance(row, dict) and row.get("route_hash"):
            out.append(str(row["route_hash"]))
    return sorted(set(out))


def extract_lesson_ids(lesson_index: Dict[str, Any]) -> List[str]:
    rows = lesson_index.get("lessons")
    if not isinstance(rows, list):
        return []

    out = []
    for row in rows:
        if isinstance(row, dict) and row.get("lesson_id"):
            out.append(str(row["lesson_id"]))
    return sorted(set(out))


def make_direction(priority: int, key: str, question: str, rationale: str, archetype_family: str) -> Dict[str, Any]:
    direction_id = "RD3_" + stable_hash({
        "priority": priority,
        "key": key,
        "question": question,
        "archetype_family": archetype_family,
    })

    return {
        "priority": priority,
        "research_key": key,
        "direction_id": direction_id,
        "primary_question": question,
        "rationale": rationale,
        "archetype_family": archetype_family,
        "strict_month_policy_required": True,
        "canonical_month_window_required": True,
        "candidate_generation_allowed_now": False,
        "candidate_contract_allowed_now": False,
        "family_release_allowed_now": False,
        "runtime_change_allowed_now": False,
        "capital_change_allowed_now": False,
        "release_allowed_now": False,
        "status": "QUEUED_READ_ONLY_RESEARCH",
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    broader_eval = load_json(BROADER_EVAL_LATEST)
    strict_policy = load_json(STRICT_POLICY_LATEST)
    canonical_guard = load_json(CANONICAL_GUARD_LATEST)
    action_guard = load_json(ACTION_GUARD_LATEST)
    lesson_index = load_json(LESSON_INDEX_PATH)
    blocklist = load_json(BLOCKLIST_PATH)

    if not isinstance(broader_eval, dict):
        critical.append("broader_month_feature_engine_evaluator_latest_missing")
        broader_eval = {}

    if not isinstance(strict_policy, dict):
        critical.append("strict_policy_missing")
        strict_policy = {}

    if not isinstance(canonical_guard, dict):
        critical.append("canonical_guard_missing")
        canonical_guard = {}

    if not isinstance(action_guard, dict):
        critical.append("action_guard_missing")
        action_guard = {}

    if not isinstance(lesson_index, dict):
        attention.append("lesson_index_missing")
        lesson_index = {}

    if not isinstance(blocklist, dict):
        critical.append("blocklist_missing")
        blocklist = {}

    if broader_eval.get("evaluator_status") != "BROADER_MONTH_FEATURE_ENGINE_EVALUATOR_NO_STRICT_SIGNAL_BRANCH_CLOSED":
        critical.append(f"unexpected_broader_eval_status:{broader_eval.get('evaluator_status')}")

    if safe_get(broader_eval, ["release_gate_feed", "RESEARCH_BRANCH_CLOSED"]) is not True:
        critical.append("broader_branch_not_closed")

    if safe_get(broader_eval, ["release_gate_feed", "STRICT_12_OF_12_SIGNAL_FOUND"]) is not False:
        critical.append("broader_eval_did_not_confirm_zero_strict_signal")

    if strict_policy.get("policy_key") != "STRICT_MONTH_STABILITY_12_OF_12":
        critical.append(f"strict_policy_not_12_of_12:{strict_policy.get('policy_key')}")

    if canonical_guard.get("guard_status") != "CANONICAL_MONTH_WINDOW_GUARD_ACTIVE":
        critical.append(f"canonical_guard_not_active:{canonical_guard.get('guard_status')}")

    if safe_get(canonical_guard, ["month_window", "canonical_policy_month_count"]) != 12:
        critical.append("canonical_policy_month_count_not_12")

    if action_guard.get("guard_status") != "ACTION_PREREQUISITE_GUARD_ACTIVE_ACTIONS_BLOCKED":
        critical.append(f"action_guard_not_blocking:{action_guard.get('guard_status')}")

    auth = action_guard.get("authorization") if isinstance(action_guard.get("authorization"), dict) else {}
    for k, v in auth.items():
        if v is not False:
            critical.append(f"authorization_not_false:{k}={v}")

    blocked_hashes = extract_blocked_hashes(blocklist)
    lesson_ids = extract_lesson_ids(lesson_index)

    directions = [
        make_direction(
            100,
            "RD3_01_NON_IMPULSE_MEAN_REVERSION_ARCHETYPE_SEARCH",
            "Can non-impulse mean-reversion archetypes satisfy canonical 12/12 stability on the full 1Y OKX swap universe?",
            "Impulse continuation, regime repair, feature-conditioned repair, and broader month feature repair all failed strict 12/12.",
            "non_impulse_mean_reversion",
        ),
        make_direction(
            94,
            "RD3_02_MARKET_NEUTRAL_RELATIVE_VALUE_ARCHETYPE_SEARCH",
            "Can market-neutral relative-value / spread-style features produce more month-stable edges than directional impulse routes?",
            "Directional impulse branches failed month stability; relative-value may reduce market regime dependency.",
            "market_neutral_relative_value",
        ),
        make_direction(
            88,
            "RD3_03_CALM_MARKET_LOW_VOL_CONTINUATION_ARCHETYPE_SEARCH",
            "Can calm-market / low-volatility continuation archetypes pass canonical 12/12 where high-volatility impulse routes failed?",
            "Prior diagnostics repeatedly showed high volatility regimes as unstable; test calm-regime archetypes from scratch.",
            "calm_market_low_vol_continuation",
        ),
        make_direction(
            82,
            "RD3_04_INTRADAY_REVERSAL_TIMING_ARCHETYPE_SEARCH",
            "Can intraday reversal timing features produce stable month-level behavior without fixed-hold impulse assumptions?",
            "Fixed hold and impulse repairs failed; timing/exit logic should be tested as a new archetype, not as repair.",
            "intraday_reversal_timing",
        ),
        make_direction(
            76,
            "RD3_05_SYMBOL_CLUSTER_NATIVE_ARCHETYPE_SEARCH",
            "Can stable symbol-cluster archetypes be discovered without manual blacklist or single-symbol overfit?",
            "Symbol loss concentration appeared earlier but was not safe as manual filtering; cluster-native archetypes may be safer.",
            "symbol_cluster_native",
        ),
        make_direction(
            70,
            "RD3_06_RESEARCH_ENGINE_META_UPGRADE",
            "Should the OS upgrade its search generator to produce broader archetype families before writing more hand-built scanners?",
            "Multiple hand-built branches failed; the Edge Factory OS needs a broader automatic archetype generator.",
            "meta_research_generator",
        ),
    ]

    if critical:
        queue_status = "NEW_RESEARCH_DIRECTIONS_V3_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_INPUTS_BEFORE_NEW_RESEARCH_QUEUE"
        reason = "; ".join(critical)
        queued = []
    else:
        queue_status = "NEW_RESEARCH_DIRECTIONS_V3_QUEUED_BRANCH_ROTATION"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_RESEARCH_DIRECTION_CONTRACT_BUILDER_V3_FOR_TOP_NEW_ARCHETYPE"
        reason = (
            f"direction_count={len(directions)}; "
            f"blocked_route_count={len(blocked_hashes)}; "
            "prior_branch_closed=True"
        )
        queued = directions

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "queue_status": queue_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "source_status": {
            "broader_evaluator_status": broader_eval.get("evaluator_status"),
            "broader_reason": broader_eval.get("reason"),
            "branch_closed": safe_get(broader_eval, ["release_gate_feed", "RESEARCH_BRANCH_CLOSED"]),
            "strict_signal_found": safe_get(broader_eval, ["release_gate_feed", "STRICT_12_OF_12_SIGNAL_FOUND"]),
            "strict_policy_key": strict_policy.get("policy_key"),
            "canonical_policy_month_count": safe_get(canonical_guard, ["month_window", "canonical_policy_month_count"]),
            "action_guard_status": action_guard.get("guard_status"),
        },

        "lesson_memory_context": {
            "blocked_route_hashes": blocked_hashes,
            "blocked_route_count": len(blocked_hashes),
            "lesson_ids": lesson_ids,
            "lesson_count": len(lesson_ids),
        },

        "directions": queued,

        "decision": {
            "candidate_generation_recommended_now": False,
            "candidate_contract_recommended_now": False,
            "family_release_recommended": False,
            "promotion_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "active_paper_recommended": False,
            "live_or_real_order_recommended": False,
            "repeat_closed_branch_recommended": False,
            "next_recommended_research_key": queued[0]["research_key"] if queued else None,
            "next_module": "edge_factory_os_research_direction_contract_builder_v3.py" if queued else None,
        },

        "release_gate_feed": {
            "NEW_RESEARCH_DIRECTIONS_V3_QUEUED": bool(queued),
            "PRIOR_BRANCH_CLOSED": True if queued else False,
            "STRICT_MONTH_STABILITY_POLICY_KEY": "STRICT_MONTH_STABILITY_12_OF_12" if queued else None,
            "CANONICAL_MONTH_WINDOW_REQUIRED": True,
            "CANDIDATE_GENERATION_ALLOWED": False,
            "CANDIDATE_CONTRACT_ALLOWED": False,
            "FAMILY_RELEASE_ALLOWED": False,
            "RUNTIME_CHANGE_ALLOWED": False,
            "CAPITAL_CHANGE_ALLOWED": False,
            "RELEASE_PASS_FROM_THIS_QUEUE": False,
            "status": queue_status,
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

    out_json = RUN_DIR / "new_research_direction_queue_v3_state.json"
    out_md = RUN_DIR / "new_research_direction_queue_v3_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS NEW RESEARCH DIRECTION QUEUE v3

queue_status: {queue_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

## Source Status

{json.dumps(result["source_status"], indent=2, default=str)}

## Lesson Memory Context

{json.dumps(result["lesson_memory_context"], indent=2, default=str)}

## Directions

{json.dumps(queued, indent=2, default=str)}

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
    print("EDGE FACTORY OS NEW RESEARCH DIRECTION QUEUE v3")
    print("=" * 100)
    print(f"queue_status: {queue_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("DIRECTIONS")
    print("-" * 100)
    for d in queued:
        print(f"{d['priority']} | {d['research_key']} | {d['direction_id']}")
        print(f"  {d['primary_question']}")
        print(f"  candidate_generation_allowed_now: {d['candidate_generation_allowed_now']}")
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
