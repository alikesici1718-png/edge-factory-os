from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_non_impulse_mean_reversion_archetype_evaluator_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

RUNNER_LATEST = (
    BASE_DIR
    / "edge_factory_os_non_impulse_mean_reversion_archetype_runner_v1"
    / "non_impulse_mean_reversion_archetype_runner_latest.json"
)

ACTION_GUARD_LATEST = (
    BASE_DIR
    / "edge_factory_os_action_prerequisite_guard_v1"
    / "action_prerequisite_guard_latest.json"
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

LESSON_DIR = BASE_DIR / "edge_factory_os_lesson_memory"
LESSON_INDEX = LESSON_DIR / "lesson_memory_index.json"
BLOCKLIST = LESSON_DIR / "candidate_route_blocklist.json"

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"non_impulse_mean_reversion_archetype_evaluator_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "non_impulse_mean_reversion_archetype_evaluator_latest.json"
LATEST_MD = OUT_ROOT / "non_impulse_mean_reversion_archetype_evaluator_latest.md"


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


def all_auth_false(action_guard: Dict[str, Any]) -> bool:
    auth = action_guard.get("authorization")
    if not isinstance(auth, dict):
        return False
    return all(v is False for v in auth.values())


def load_or_init_json(path: Path, default: Any) -> Any:
    obj = load_json(path)
    return obj if obj is not None else default


def append_lesson(lesson: Dict[str, Any]) -> Dict[str, Any]:
    LESSON_DIR.mkdir(parents=True, exist_ok=True)

    index = load_or_init_json(LESSON_INDEX, {"lessons": []})
    if not isinstance(index, dict):
        index = {"lessons": []}
    if not isinstance(index.get("lessons"), list):
        index["lessons"] = []

    existing = {x.get("lesson_id") for x in index["lessons"] if isinstance(x, dict)}
    if lesson["lesson_id"] not in existing:
        index["lessons"].append(lesson)

    dump_json(LESSON_INDEX, index)
    return index


def append_blocklist(route_hash: str, reason: str, lesson_id: str) -> Dict[str, Any]:
    LESSON_DIR.mkdir(parents=True, exist_ok=True)

    blocklist = load_or_init_json(BLOCKLIST, {"blocked_routes": []})
    if not isinstance(blocklist, dict):
        blocklist = {"blocked_routes": []}
    if not isinstance(blocklist.get("blocked_routes"), list):
        blocklist["blocked_routes"] = []

    existing = {x.get("route_hash") for x in blocklist["blocked_routes"] if isinstance(x, dict)}
    if route_hash not in existing:
        blocklist["blocked_routes"].append({
            "route_hash": route_hash,
            "blocked_at_utc": NOW.isoformat(),
            "reason": reason,
            "lesson_id": lesson_id,
            "reopen_requires": [
                "genuinely new non-impulse mean reversion feature set",
                "canonical 12/12 positive months",
                "full universe backtest pass",
                "train/OOS pass",
                "cost/slippage pass",
                "symbol concentration pass",
                "regime bucket pass",
                "risk/capital safety pass",
                "final release gate pass",
            ],
        })

    dump_json(BLOCKLIST, blocklist)
    return blocklist


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    runner = load_json(RUNNER_LATEST)
    action_guard = load_json(ACTION_GUARD_LATEST)
    canonical_guard = load_json(CANONICAL_GUARD_LATEST)
    strict_policy = load_json(STRICT_POLICY_LATEST)

    if not isinstance(runner, dict):
        critical.append("non_impulse_mean_reversion_runner_latest_missing")
        runner = {}

    if not isinstance(action_guard, dict):
        critical.append("action_prerequisite_guard_latest_missing")
        action_guard = {}

    if not isinstance(canonical_guard, dict):
        critical.append("canonical_month_window_guard_latest_missing")
        canonical_guard = {}

    if not isinstance(strict_policy, dict):
        critical.append("strict_month_policy_latest_missing")
        strict_policy = {}

    if runner.get("runner_status") != "NON_IMPULSE_MEAN_REVERSION_ARCHETYPE_RUNNER_NO_STRICT_PREVIEW_FOUND":
        critical.append(f"unexpected_runner_status:{runner.get('runner_status')}")

    if safe_get(runner, ["release_gate_feed", "STRICT_12_OF_12_PREVIEW_FOUND"]) is not False:
        critical.append("runner_did_not_confirm_zero_strict_preview")

    if safe_get(runner, ["release_gate_feed", "RELEASE_PASS_FROM_THIS_RUNNER"]) is not False:
        critical.append("runner_claimed_release_pass_unexpectedly")

    if safe_get(runner, ["release_gate_feed", "CANONICAL_MONTH_WINDOW_CONSUMED"]) is not True:
        critical.append("runner_did_not_consume_canonical_month_window")

    if canonical_guard.get("guard_status") != "CANONICAL_MONTH_WINDOW_GUARD_ACTIVE":
        critical.append(f"canonical_guard_not_active:{canonical_guard.get('guard_status')}")

    if safe_get(canonical_guard, ["month_window", "canonical_policy_month_count"]) != 12:
        critical.append("canonical_policy_month_count_not_12")

    if strict_policy.get("policy_key") != "STRICT_MONTH_STABILITY_12_OF_12":
        critical.append(f"strict_policy_not_12_of_12:{strict_policy.get('policy_key')}")

    if action_guard.get("guard_status") != "ACTION_PREREQUISITE_GUARD_ACTIVE_ACTIONS_BLOCKED":
        critical.append(f"action_guard_not_blocking:{action_guard.get('guard_status')}")

    if not all_auth_false(action_guard):
        critical.append("authorization_not_all_false")

    summary = runner.get("search_summary") or {}
    rules_tested = int(summary.get("rules_tested") or 0)
    ok_result_count = int(summary.get("ok_result_count") or 0)
    strict_preview_count = int(summary.get("strict_12_preview_count") or 0)

    if critical:
        evaluator_status = "NON_IMPULSE_MEAN_REVERSION_ARCHETYPE_EVALUATOR_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_RUNNER_OR_GUARD_INPUTS"
        reason = "; ".join(critical)
        lesson_written = False
        blocklist_written = False

    else:
        evaluator_status = "NON_IMPULSE_MEAN_REVERSION_ARCHETYPE_EVALUATOR_BRANCH_CLOSED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "ROTATE_TO_MARKET_NEUTRAL_RELATIVE_VALUE_ARCHETYPE"
        reason = f"rules_tested={rules_tested}; strict_12_preview_count=0; branch_closed=True"

        route_hash = str(runner.get("contract_hash") or "NON_IMPULSE_MEAN_REVERSION_UNKNOWN_HASH")
        lesson_id = f"LESSON_NON_IMPULSE_MEAN_REVERSION_NO_STRICT_PREVIEW_{route_hash}"

        lesson = {
            "lesson_id": lesson_id,
            "created_at_utc": NOW.isoformat(),
            "lesson_type": "RESEARCH_BRANCH_FAILURE",
            "route_hash": route_hash,
            "claim": "Non-impulse mean reversion archetype search did not find any canonical strict 12/12 preview.",
            "evidence": {
                "runner_status": runner.get("runner_status"),
                "rules_tested": rules_tested,
                "ok_result_count": ok_result_count,
                "strict_12_preview_count": strict_preview_count,
                "top_results": runner.get("top_results", [])[:10],
                "canonical_month_window": runner.get("canonical_month_window"),
                "strict_policy": runner.get("strict_policy"),
            },
            "decision": {
                "candidate_generation_allowed": False,
                "candidate_contract_allowed": False,
                "family_release_allowed": False,
                "runtime_change_allowed": False,
                "capital_change_allowed": False,
                "branch_closed": True,
                "repeat_recommended": False,
                "next_research_family": "market_neutral_relative_value",
            },
        }

        append_lesson(lesson)
        append_blocklist(
            route_hash=route_hash,
            reason="non_impulse_mean_reversion_no_canonical_strict_12_preview",
            lesson_id=lesson_id,
        )

        lesson_written = True
        blocklist_written = True

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "runner_source": str(RUNNER_LATEST),
        "action_guard_source": str(ACTION_GUARD_LATEST),
        "canonical_guard_source": str(CANONICAL_GUARD_LATEST),
        "strict_policy_source": str(STRICT_POLICY_LATEST),

        "evaluation_summary": {
            "rules_tested": rules_tested,
            "ok_result_count": ok_result_count,
            "strict_12_preview_count": strict_preview_count,
            "strict_preview_found": strict_preview_count > 0,
            "branch_closed": strict_preview_count == 0 and not critical,
            "archetype_keys_tested": summary.get("archetype_keys_tested"),
        },

        "best_evidence": {
            "top_results": runner.get("top_results", [])[:20],
            "search_summary": runner.get("search_summary"),
        },

        "lesson_memory": {
            "lesson_written": lesson_written,
            "blocklist_written": blocklist_written,
            "lesson_index_path": str(LESSON_INDEX),
            "blocklist_path": str(BLOCKLIST),
        },

        "release_gate_feed": {
            "NON_IMPULSE_MEAN_REVERSION_ARCHETYPE_EVALUATED": True,
            "CANONICAL_MONTH_WINDOW_CONSUMED": True,
            "STRICT_MONTH_STABILITY_POLICY_KEY": "STRICT_MONTH_STABILITY_12_OF_12",
            "STRICT_12_OF_12_PREVIEW_FOUND": strict_preview_count > 0,
            "RESEARCH_BRANCH_CLOSED": strict_preview_count == 0 and not critical,
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
            "repeat_this_branch_recommended": False,
            "next_recommended_research_key": "RD3_02_MARKET_NEUTRAL_RELATIVE_VALUE_ARCHETYPE_SEARCH",
            "next_module": "edge_factory_os_research_direction_contract_builder_v4.py",
            "why_no_action": [
                "strict_12_preview_count_zero",
                "action_prerequisite_guard_blocks_all_actions",
                "candidate_family_runtime_capital_require_full_chain",
                "manual_override_not_allowed",
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

    out_json = RUN_DIR / "non_impulse_mean_reversion_archetype_evaluator_v1_state.json"
    out_md = RUN_DIR / "non_impulse_mean_reversion_archetype_evaluator_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS NON IMPULSE MEAN REVERSION ARCHETYPE EVALUATOR v1

evaluator_status: {evaluator_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

## Evaluation Summary

{json.dumps(result["evaluation_summary"], indent=2, default=str)}

## Lesson Memory

{json.dumps(result["lesson_memory"], indent=2, default=str)}

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
    print("EDGE FACTORY OS NON IMPULSE MEAN REVERSION ARCHETYPE EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {evaluator_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("EVALUATION SUMMARY")
    print("-" * 100)
    print(json.dumps(result["evaluation_summary"], indent=2, default=str))
    print()
    print("LESSON MEMORY")
    print("-" * 100)
    print(json.dumps(result["lesson_memory"], indent=2, default=str))
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
