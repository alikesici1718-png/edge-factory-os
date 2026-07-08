#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Restricted Null Power Feasibility Review v1

Purpose:
- Consume Restricted Market-State Structure Retest Evaluator v1.
- Decide whether spending enough null runs to resolve tiny global alpha is justified.
- Do NOT run more nulls.
- Preserve the structure hint as underpowered/not validated.
- Close or rotate the restricted route if additional null power is not justified.
- Keep candidates, release, runtime, capital, active paper, live, and real orders blocked.
"""

from __future__ import annotations

import datetime as dt
import json
import math
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

FRAMEWORK_DIR = REPO_DIR / "edge_factory_os_framework"
POLICY_DIR = FRAMEWORK_DIR / "policies"
QUEUE_DIR = FRAMEWORK_DIR / "queues"

EVALUATOR_JSON = (
    BASE_DIR
    / "edge_factory_os_restricted_market_state_structure_retest_evaluator"
    / "restricted_market_state_structure_retest_evaluator_latest.json"
)
EVALUATOR_STATE_JSON = POLICY_DIR / "restricted_market_state_structure_retest_evaluator_state_v1.json"
RETEST_STATE_JSON = POLICY_DIR / "restricted_market_state_structure_retest_state_v1.json"
BUDGET_CONSUMPTION_JSON = POLICY_DIR / "restricted_market_state_structure_retest_budget_consumption_v1.json"
BUDGET_ALLOCATION_JSON = POLICY_DIR / "restricted_research_budget_allocation_v1.json"
GLOBAL_ALPHA_ACCOUNTING_JSON = POLICY_DIR / "global_route_family_alpha_accounting_v1.json"
PROMISING_VAULT_JSON = POLICY_DIR / "promising_signal_vault_v1.json"
UNTOUCHED_HOLDOUT_REGISTRY_JSON = FRAMEWORK_DIR / "registries" / "untouched_holdout_registry_v1.json"
HOLDOUT_ACCESS_CONTROL_JSON = POLICY_DIR / "holdout_access_control_policy_v1.json"

LESSON_INDEX_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

OUT_DIR = BASE_DIR / "edge_factory_os_restricted_null_power_feasibility_review"
OUT_JSON = OUT_DIR / "restricted_null_power_feasibility_review_latest.json"
OUT_TXT = OUT_DIR / "restricted_null_power_feasibility_review_latest.txt"

REPO_FEASIBILITY_STATE_JSON = POLICY_DIR / "restricted_null_power_feasibility_review_state_v1.json"
REPO_NEXT_QUEUE_JSON = QUEUE_DIR / "restricted_null_power_feasibility_next_queue_v1.json"
REPO_LESSON_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "restricted_market_state_underpowered_no_validation_lesson_latest.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD7_12_POLICY_LOCKED_RESEARCH_ROTATION_AFTER_RESTRICTED_RETEST"
NEXT_MODULE = "edge_factory_os_policy_locked_research_rotation_after_restricted_retest_v1.py"

SAFETY_FLAGS = {
    "candidate_generation_allowed": False,
    "candidate_contract_allowed": False,
    "family_release_allowed": False,
    "promotion_allowed": False,
    "runtime_touch_allowed": False,
    "launcher_allowed": False,
    "patch_runtime_allowed": False,
    "capital_change_allowed": False,
    "active_paper_allowed": False,
    "live_allowed": False,
    "real_orders_allowed": False,
    "execution_performed": False,
    "file_delete_performed": False,
    "file_move_performed": False,
    "archive_performed": False,
}


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def load_json(path: Path, default: Any = None) -> Any:
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_load_error": f"{type(exc).__name__}: {exc}", "_path": str(path)}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    tmp.replace(path)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        x = float(value)
        if math.isfinite(x):
            return x
    except Exception:
        pass
    return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def extract_list(obj: Any, key: str) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get(key), list):
        return [x for x in obj[key] if isinstance(x, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def route_hash_blocked(blocked_routes: List[Dict[str, Any]], route_hash: str) -> bool:
    return route_hash in {str(x.get("route_hash")) for x in blocked_routes if isinstance(x, dict)}


def append_blocklist(path: Path, record: Dict[str, Any]) -> Dict[str, Any]:
    obj = load_json(path, {})
    if isinstance(obj, list):
        existing = {str(x.get("route_hash")) for x in obj if isinstance(x, dict)}
        if str(record.get("route_hash")) not in existing:
            obj.append(record)
        write_json(path, obj)
        return {"mode": "list_root", "appended": True}

    if not isinstance(obj, dict):
        obj = {}

    rows = obj.get("blocked_routes")
    if not isinstance(rows, list):
        rows = []

    existing = {str(x.get("route_hash")) for x in rows if isinstance(x, dict)}
    appended = False
    if str(record.get("route_hash")) not in existing:
        rows.append(record)
        appended = True

    obj["blocked_routes"] = rows
    obj["updated_at_utc"] = utc_now_iso()
    write_json(path, obj)
    return {"mode": "dict_blocked_routes", "appended": appended}


def append_lesson_index(path: Path, record: Dict[str, Any]) -> Dict[str, Any]:
    obj = load_json(path, {})
    if isinstance(obj, list):
        existing = {str(x.get("lesson_id")) for x in obj if isinstance(x, dict)}
        if str(record.get("lesson_id")) not in existing:
            obj.append(record)
        write_json(path, obj)
        return {"mode": "list_root", "appended": True}

    if not isinstance(obj, dict):
        obj = {}

    rows = obj.get("lessons")
    if not isinstance(rows, list):
        rows = []

    existing = {str(x.get("lesson_id")) for x in rows if isinstance(x, dict)}
    appended = False
    if str(record.get("lesson_id")) not in existing:
        rows.append(record)
        appended = True

    obj["lessons"] = rows
    obj["updated_at_utc"] = utc_now_iso()
    write_json(path, obj)
    return {"mode": "dict_lessons", "appended": appended}


def build_text(result: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS RESTRICTED NULL POWER FEASIBILITY REVIEW v1")
    lines.append("=" * 100)

    for key in [
        "review_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "decision_class",
        "contract_id",
        "route_hash",
        "route_family",
        "alpha_budget",
        "route_budget",
        "route_budget_consumed",
        "observed_score_eta2",
        "max_p_empirical_plus_one",
        "alpha_budget_ratio",
        "required_runs_per_null_model_for_alpha",
        "current_runs_per_null_model",
        "estimated_total_required_null_runs",
        "additional_null_power_recommended",
        "additional_null_budget_allowed_now",
        "route_closed",
        "release_allowed",
        "candidate_generation_allowed",
        "family_release_allowed",
        "runtime_touch_allowed",
        "capital_change_allowed",
        "active_paper_allowed",
        "live_allowed",
        "real_orders_allowed",
        "next_recommended_research_key",
        "next_module",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("CORE DECISION")
    lines.append("-" * 100)
    lines.append("Do not spend more null power blindly.")
    lines.append("The current p estimate is far above the tiny global alpha, and the route budget is already consumed.")
    lines.append("The route is closed for release and preserved only as an underpowered/not-validated structure hint.")
    lines.append("Next step is policy-locked research rotation, not promotion.")

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        lines.append(f"{key}: {value}")

    lines.append("")
    lines.append("OUTPUT PATHS")
    lines.append("-" * 100)
    for key in [
        "output_json",
        "output_txt",
        "feasibility_state_json",
        "next_queue_json",
        "lesson_json",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS RESTRICTED NULL POWER FEASIBILITY REVIEW v1")
    print("=" * 100)
    print(f"review_status: {result.get('review_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"decision_class: {result.get('decision_class')}")
    print(f"contract_id: {result.get('contract_id')}")
    print(f"route_hash: {result.get('route_hash')}")
    print(f"route_family: {result.get('route_family')}")
    print(f"alpha_budget: {result.get('alpha_budget')}")
    print(f"route_budget: {result.get('route_budget')}")
    print(f"route_budget_consumed: {result.get('route_budget_consumed')}")
    print(f"observed_score_eta2: {result.get('observed_score_eta2')}")
    print(f"max_p_empirical_plus_one: {result.get('max_p_empirical_plus_one')}")
    print(f"alpha_budget_ratio: {result.get('alpha_budget_ratio')}")
    print(f"required_runs_per_null_model_for_alpha: {result.get('required_runs_per_null_model_for_alpha')}")
    print(f"current_runs_per_null_model: {result.get('current_runs_per_null_model')}")
    print(f"estimated_total_required_null_runs: {result.get('estimated_total_required_null_runs')}")
    print(f"additional_null_power_recommended: {result.get('additional_null_power_recommended')}")
    print(f"additional_null_budget_allowed_now: {result.get('additional_null_budget_allowed_now')}")
    print(f"route_closed: {result.get('route_closed')}")
    print(f"release_allowed: {result.get('release_allowed')}")
    print(f"next_recommended_research_key: {result.get('next_recommended_research_key')}")
    print(f"next_module: {result.get('next_module')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        print(f"{key}: {value}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"STATE: {result.get('feasibility_state_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    REPO_LESSON_JSON.parent.mkdir(parents=True, exist_ok=True)

    evaluator = load_json(EVALUATOR_JSON, {})
    evaluator_state = load_json(EVALUATOR_STATE_JSON, {})
    retest_state = load_json(RETEST_STATE_JSON, {})
    budget_consumption = load_json(BUDGET_CONSUMPTION_JSON, {})
    budget_allocation = load_json(BUDGET_ALLOCATION_JSON, {})
    vault = load_json(PROMISING_VAULT_JSON, {})
    alpha_accounting = load_json(GLOBAL_ALPHA_ACCOUNTING_JSON, {})
    holdout_registry = load_json(UNTOUCHED_HOLDOUT_REGISTRY_JSON, {})
    holdout_access = load_json(HOLDOUT_ACCESS_CONTROL_JSON, {})

    lessons_before = extract_list(load_json(LESSON_INDEX_JSON, {}), "lessons")
    blocked_before = extract_list(load_json(BLOCKLIST_JSON, {}), "blocked_routes")

    contract_id = evaluator.get("contract_id")
    route_hash = str(evaluator.get("route_hash") or "")
    route_family = str(evaluator.get("route_family") or "")

    alpha_budget = safe_float(evaluator.get("alpha_budget"))
    route_budget = safe_int(evaluator.get("route_budget"))
    observed_score = safe_float(evaluator.get("observed_score_eta2"))
    max_p = safe_float(evaluator.get("max_p_empirical_plus_one"), 1.0)
    min_p = safe_float(evaluator.get("min_resolvable_p_plus_one"), 1.0)
    required_runs = safe_int(evaluator.get("required_runs_per_null_model_for_alpha"))
    current_runs = safe_int(evaluator.get("current_runs_per_null_model"))
    estimated_total_required_null_runs = safe_int(evaluator.get("estimated_total_required_null_runs"))

    alpha_budget_ratio = (max_p / alpha_budget) if alpha_budget > 0 else float("inf")

    route_budget_consumed = evaluator.get("route_budget_consumed") is True or budget_consumption.get("route_budget_consumed") == 1
    route_already_blocked = route_hash_blocked(blocked_before, route_hash)

    alpha_resolution_pass = evaluator.get("alpha_resolution_pass") is True
    p_value_pass = evaluator.get("p_value_pass") is True
    policy_gate_pass = evaluator.get("restricted_retest_policy_gate_pass") is True

    # Feasibility rule:
    # - Do not allocate more null-power when current max empirical p is far above alpha.
    # - Do not allocate more when route budget is consumed.
    # - Do not allocate more if full null requirement is materially larger than current budget and no pass exists.
    far_above_alpha = alpha_budget_ratio > 10.0
    route_budget_exhausted = route_budget_consumed
    huge_null_requirement = estimated_total_required_null_runs >= 100000

    additional_null_power_recommended = bool(
        policy_gate_pass is True
        and alpha_resolution_pass is True
        and p_value_pass is True
        and not route_budget_exhausted
    )

    additional_null_budget_allowed_now = False
    route_closed = True

    if not alpha_resolution_pass and far_above_alpha and route_budget_exhausted:
        review_status = "RESTRICTED_NULL_POWER_FEASIBILITY_REVIEW_NOT_JUSTIFIED_ROUTE_CLOSED"
        decision_class = "NULL_POWER_NOT_JUSTIFIED_P_ESTIMATE_FAR_ABOVE_ALPHA_ROUTE_BUDGET_CONSUMED"
        reason = "Current empirical p estimate is far above tiny alpha and route budget is consumed; do not spend more null power."
    elif not alpha_resolution_pass:
        review_status = "RESTRICTED_NULL_POWER_FEASIBILITY_REVIEW_UNDERPOWERED_BUT_MORE_POWER_REQUIRES_NEW_GOVERNANCE"
        decision_class = "UNDERPOWERED_MORE_POWER_REQUIRES_SEPARATE_GOVERNANCE"
        reason = "Tiny alpha cannot be resolved with current null runs; more power requires separate governance and is not allowed now."
    elif not policy_gate_pass:
        review_status = "RESTRICTED_NULL_POWER_FEASIBILITY_REVIEW_POLICY_GATE_FAIL_ROUTE_CLOSED"
        decision_class = "POLICY_GATE_FAIL_ROUTE_CLOSED"
        reason = "Restricted retest failed policy gate; route closed for release."
    else:
        review_status = "RESTRICTED_NULL_POWER_FEASIBILITY_REVIEW_REVIEW_REQUIRED_NO_RELEASE"
        decision_class = "UNEXPECTED_REVIEW_REQUIRED_NO_RELEASE"
        reason = "Unexpected state; keep release blocked and require governance review."

    release_allowed = False

    block_record = {
        "route_hash": route_hash,
        "created_at_utc": utc_now_iso(),
        "blocked_reason": "RESTRICTED_MARKET_STATE_STRUCTURE_RETEST_UNDERPOWERED_NO_VALIDATION",
        "research_branch": "RESTRICTED_MARKET_STATE_STRUCTURE_RETEST",
        "research_key": "RESTRICTED_MARKET_STATE_STRUCTURE_RETEST_V1",
        "contract_id": contract_id,
        "route_family": route_family,
        "decision_class": decision_class,
        "alpha_budget": alpha_budget,
        "route_budget": route_budget,
        "route_budget_consumed": route_budget_consumed,
        "observed_score_eta2": observed_score,
        "max_p_empirical_plus_one": max_p,
        "alpha_budget_ratio": alpha_budget_ratio,
        "required_runs_per_null_model_for_alpha": required_runs,
        "estimated_total_required_null_runs": estimated_total_required_null_runs,
        "release_allowed": False,
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        "reopen_requirements": [
            "new_governance_budget_decision",
            "new_route_hash_or_explicit_reopen_approval",
            "null_power_budget_feasibility_pass",
            "pre_registered_contract_revision",
            "no_holdout_access",
            "no_candidate_or_release_without_full_validation",
        ],
    }

    lesson_record = {
        "lesson_id": f"LESSON_RESTRICTED_MARKET_STATE_UNDERPOWERED_{route_hash}",
        "created_at_utc": utc_now_iso(),
        "lesson_type": "RESTRICTED_RETEST_UNDERPOWERED_NOT_VALIDATED",
        "route_hash": route_hash,
        "contract_id": contract_id,
        "route_family": route_family,
        "decision_class": decision_class,
        "alpha_budget": alpha_budget,
        "max_p_empirical_plus_one": max_p,
        "alpha_budget_ratio": alpha_budget_ratio,
        "required_runs_per_null_model_for_alpha": required_runs,
        "estimated_total_required_null_runs": estimated_total_required_null_runs,
        "lesson": (
            "Restricted market-state structure retest did not validate under global tiny alpha. "
            "Do not spend large null-power budget automatically; rotate or require separate budget governance."
        ),
        **SAFETY_FLAGS,
    }

    block_append_status = append_blocklist(BLOCKLIST_JSON, block_record)
    lesson_append_status = append_lesson_index(LESSON_INDEX_JSON, lesson_record)
    write_json(REPO_LESSON_JSON, lesson_record)

    blocked_after = extract_list(load_json(BLOCKLIST_JSON, {}), "blocked_routes")
    lessons_after = extract_list(load_json(LESSON_INDEX_JSON, {}), "lessons")

    feasibility_state = {
        "state_name": "edge_factory_os_restricted_null_power_feasibility_review_state_v1",
        "created_at_utc": utc_now_iso(),
        "review_status": review_status,
        "decision_class": decision_class,
        "strict_policy_key": STRICT_POLICY_KEY,
        "contract_id": contract_id,
        "route_hash": route_hash,
        "route_family": route_family,
        "alpha_budget": alpha_budget,
        "route_budget": route_budget,
        "route_budget_consumed": route_budget_consumed,
        "observed_score_eta2": observed_score,
        "max_p_empirical_plus_one": max_p,
        "min_resolvable_p_plus_one": min_p,
        "alpha_budget_ratio": alpha_budget_ratio,
        "required_runs_per_null_model_for_alpha": required_runs,
        "current_runs_per_null_model": current_runs,
        "estimated_total_required_null_runs": estimated_total_required_null_runs,
        "far_above_alpha": far_above_alpha,
        "huge_null_requirement": huge_null_requirement,
        "additional_null_power_recommended": additional_null_power_recommended,
        "additional_null_budget_allowed_now": additional_null_budget_allowed_now,
        "route_closed": route_closed,
        "release_allowed": False,
        "next_recommended_research_key": NEXT_RESEARCH_KEY,
        "next_module": NEXT_MODULE,
        **SAFETY_FLAGS,
    }

    next_queue = {
        "queue_name": "edge_factory_os_restricted_null_power_feasibility_next_queue_v1",
        "created_at_utc": utc_now_iso(),
        "queue_status": "RESTRICTED_NULL_POWER_FEASIBILITY_NEXT_QUEUE_READY",
        "top_next_research_key": NEXT_RESEARCH_KEY,
        "top_next_module": NEXT_MODULE,
        "reason": "Restricted route is not validated and more null power is not justified automatically; rotate under policy lock.",
        "route_closed": True,
        "additional_null_budget_allowed_now": False,
        "research_execution_allowed_now": False,
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        "next_steps": [
            {
                "research_key": NEXT_RESEARCH_KEY,
                "module": NEXT_MODULE,
                "priority": 100,
                "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
                "purpose": "Rotate to a materially different policy-locked research direction after restricted retest closure.",
                "route_closed": True,
                "additional_null_budget_allowed_now": False,
                "candidate_generation_allowed": False,
                "family_release_allowed": False,
                "runtime_touch_allowed": False,
                "capital_change_allowed": False,
                "active_paper_allowed": False,
                "live_allowed": False,
                "real_orders_allowed": False,
            }
        ],
        **SAFETY_FLAGS,
    }

    result = {
        "review_name": "edge_factory_os_restricted_null_power_feasibility_review_v1",
        "created_at_utc": utc_now_iso(),
        "review_status": review_status,
        "severity": "ATTENTION",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "next_action": "BUILD_POLICY_LOCKED_RESEARCH_ROTATION_AFTER_RESTRICTED_RETEST_NO_RELEASE",
        "reason": reason,
        "decision_class": decision_class,
        "contract_id": contract_id,
        "route_hash": route_hash,
        "route_family": route_family,
        "alpha_budget": alpha_budget,
        "route_budget": route_budget,
        "route_budget_consumed": route_budget_consumed,
        "observed_score_eta2": observed_score,
        "max_p_empirical_plus_one": max_p,
        "min_resolvable_p_plus_one": min_p,
        "alpha_budget_ratio": alpha_budget_ratio,
        "required_runs_per_null_model_for_alpha": required_runs,
        "current_runs_per_null_model": current_runs,
        "estimated_total_required_null_runs": estimated_total_required_null_runs,
        "far_above_alpha": far_above_alpha,
        "huge_null_requirement": huge_null_requirement,
        "additional_null_power_recommended": additional_null_power_recommended,
        "additional_null_budget_allowed_now": additional_null_budget_allowed_now,
        "route_closed": route_closed,
        "route_already_blocked_before": route_already_blocked,
        "blocked_route_count_before": len(blocked_before),
        "blocked_route_count_after": len(blocked_after),
        "lesson_count_before": len(lessons_before),
        "lesson_count_after": len(lessons_after),
        "block_append_status": block_append_status,
        "lesson_append_status": lesson_append_status,
        "release_allowed": release_allowed,
        "input_evaluator_status": evaluator.get("evaluator_status"),
        "input_evaluator_state_status": evaluator_state.get("evaluator_status"),
        "input_retest_status": retest_state.get("runner_status"),
        "budget_consumption_status": budget_consumption.get("consumption_status"),
        "budget_allocation_status": budget_allocation.get("allocation_status"),
        "vault_status": vault.get("vault_status"),
        "global_alpha_accounting_status": alpha_accounting.get("accounting_status"),
        "holdout_selected": holdout_registry.get("holdout_selected"),
        "holdout_peeked": holdout_registry.get("holdout_peeked"),
        "holdout_access_allowed_now": holdout_access.get("holdout_access_allowed_now"),
        "next_recommended_research_key": NEXT_RESEARCH_KEY,
        "next_module": NEXT_MODULE,
        "feasibility_state": feasibility_state,
        "next_queue": next_queue,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "feasibility_state_json": str(REPO_FEASIBILITY_STATE_JSON),
        "next_queue_json": str(REPO_NEXT_QUEUE_JSON),
        "lesson_json": str(REPO_LESSON_JSON),
        **SAFETY_FLAGS,
    }

    write_json(REPO_FEASIBILITY_STATE_JSON, feasibility_state)
    write_json(REPO_NEXT_QUEUE_JSON, next_queue)
    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text(result))
    print_summary(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
