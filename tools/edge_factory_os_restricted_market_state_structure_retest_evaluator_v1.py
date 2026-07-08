#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Restricted Market-State Structure Retest Evaluator v1

Purpose:
- Evaluate the restricted market-state structure retest runner.
- Mark underpowered tiny-alpha result as NOT VALIDATED.
- Record that the restricted route budget was consumed.
- Preserve the idea as informational / underpowered, not releaseable.
- Queue a null-power feasibility review instead of blindly running 230k+ nulls.
- Keep candidate/family/runtime/capital/active-paper/live/real-order actions blocked.

This evaluator does NOT:
- run research
- rerun nulls
- allocate more budget
- generate candidates
- release families
- touch runtime
- change capital
- access holdout
- start active paper
- enable live
- place real orders
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

RUNNER_JSON = BASE_DIR / "edge_factory_os_restricted_market_state_structure_retest_runner" / "restricted_market_state_structure_retest_runner_latest.json"
RUNNER_STATE_JSON = POLICY_DIR / "restricted_market_state_structure_retest_state_v1.json"
BUDGET_CONSUMPTION_JSON = POLICY_DIR / "restricted_market_state_structure_retest_budget_consumption_v1.json"

EXECUTION_POLICY_JSON = POLICY_DIR / "restricted_research_execution_policy_v1.json"
BUDGET_ALLOCATION_JSON = POLICY_DIR / "restricted_research_budget_allocation_v1.json"
PROMISING_VAULT_JSON = POLICY_DIR / "promising_signal_vault_v1.json"
GLOBAL_ALPHA_ACCOUNTING_JSON = POLICY_DIR / "global_route_family_alpha_accounting_v1.json"
UNTOUCHED_HOLDOUT_REGISTRY_JSON = FRAMEWORK_DIR / "registries" / "untouched_holdout_registry_v1.json"
HOLDOUT_ACCESS_CONTROL_JSON = POLICY_DIR / "holdout_access_control_policy_v1.json"

OUT_DIR = BASE_DIR / "edge_factory_os_restricted_market_state_structure_retest_evaluator"
OUT_JSON = OUT_DIR / "restricted_market_state_structure_retest_evaluator_latest.json"
OUT_TXT = OUT_DIR / "restricted_market_state_structure_retest_evaluator_latest.txt"

REPO_EVALUATOR_STATE_JSON = POLICY_DIR / "restricted_market_state_structure_retest_evaluator_state_v1.json"
REPO_NEXT_QUEUE_JSON = QUEUE_DIR / "restricted_market_state_structure_retest_evaluator_next_queue_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD7_11_RESTRICTED_NULL_POWER_FEASIBILITY_REVIEW"
NEXT_MODULE = "edge_factory_os_restricted_null_power_feasibility_review_v1.py"

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


def required_runs_for_alpha(alpha: float) -> int:
    if alpha <= 0:
        return 0
    return int(math.ceil((1.0 / alpha) - 1.0))


def build_text(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS RESTRICTED MARKET-STATE STRUCTURE RETEST EVALUATOR v1")
    lines.append("=" * 100)

    for key in [
        "evaluator_status",
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
        "observed_score_eta2",
        "max_p_empirical_plus_one",
        "min_resolvable_p_plus_one",
        "required_runs_per_null_model_for_alpha",
        "current_runs_per_null_model",
        "estimated_total_required_null_runs",
        "alpha_resolution_pass",
        "p_value_pass",
        "restricted_retest_policy_gate_pass",
        "route_budget_consumed",
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
    lines.append("The retest is NOT validated because alpha resolution failed.")
    lines.append("The route budget was consumed by the single allowed restricted runner.")
    lines.append("The structure hint is preserved as informational, but no release/candidate/runtime/capital/live action is allowed.")
    lines.append("Further null-power expansion requires a separate feasibility/budget governance review.")

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        lines.append(f"{key}: {value}")

    lines.append("")
    lines.append("OUTPUT PATHS")
    lines.append("-" * 100)
    for key in ["output_json", "output_txt", "evaluator_state_json", "next_queue_json"]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS RESTRICTED MARKET-STATE STRUCTURE RETEST EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {result.get('evaluator_status')}")
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
    print(f"observed_score_eta2: {result.get('observed_score_eta2')}")
    print(f"max_p_empirical_plus_one: {result.get('max_p_empirical_plus_one')}")
    print(f"min_resolvable_p_plus_one: {result.get('min_resolvable_p_plus_one')}")
    print(f"required_runs_per_null_model_for_alpha: {result.get('required_runs_per_null_model_for_alpha')}")
    print(f"current_runs_per_null_model: {result.get('current_runs_per_null_model')}")
    print(f"estimated_total_required_null_runs: {result.get('estimated_total_required_null_runs')}")
    print(f"alpha_resolution_pass: {result.get('alpha_resolution_pass')}")
    print(f"p_value_pass: {result.get('p_value_pass')}")
    print(f"restricted_retest_policy_gate_pass: {result.get('restricted_retest_policy_gate_pass')}")
    print(f"route_budget_consumed: {result.get('route_budget_consumed')}")
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
    print(f"STATE: {result.get('evaluator_state_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    runner = load_json(RUNNER_JSON, {})
    runner_state = load_json(RUNNER_STATE_JSON, {})
    budget_consumption = load_json(BUDGET_CONSUMPTION_JSON, {})
    execution_policy = load_json(EXECUTION_POLICY_JSON, {})
    budget_allocation = load_json(BUDGET_ALLOCATION_JSON, {})
    vault = load_json(PROMISING_VAULT_JSON, {})
    alpha_accounting = load_json(GLOBAL_ALPHA_ACCOUNTING_JSON, {})
    holdout_registry = load_json(UNTOUCHED_HOLDOUT_REGISTRY_JSON, {})
    holdout_access = load_json(HOLDOUT_ACCESS_CONTROL_JSON, {})

    contract_id = runner.get("contract_id")
    route_hash = runner.get("route_hash")
    route_family = runner.get("route_family")

    alpha_budget = safe_float(runner.get("alpha_budget"))
    route_budget = safe_int(runner.get("route_budget"))
    observed_score_eta2 = safe_float(runner.get("observed_score_eta2"))
    max_p = safe_float(runner.get("max_p_empirical_plus_one"), 1.0)
    min_p = safe_float(runner.get("min_resolvable_p_plus_one"), 1.0)
    current_runs = safe_int(runner.get("runs_per_null_model"))
    null_model_count = safe_int(runner.get("null_model_count"))

    required_runs = required_runs_for_alpha(alpha_budget)
    estimated_total_required_null_runs = required_runs * max(1, null_model_count)

    alpha_resolution_pass = runner.get("alpha_resolution_pass") is True
    p_value_pass = runner.get("p_value_pass") is True
    policy_gate_pass = runner.get("restricted_retest_policy_gate_pass") is True
    offline_exec = runner.get("offline_research_execution_performed") is True
    route_budget_consumed = budget_consumption.get("route_budget_consumed") == 1 or offline_exec

    if policy_gate_pass:
        evaluator_status = "RESTRICTED_MARKET_STATE_STRUCTURE_RETEST_EVALUATOR_RESEARCH_ONLY_SIGNAL_NEEDS_GOVERNANCE"
        decision_class = "RESEARCH_ONLY_POLICY_GATE_PASS_NO_RELEASE"
        reason = "Restricted retest passed its policy gate, but release/candidate/runtime/capital/live remain blocked."
    elif not alpha_resolution_pass:
        evaluator_status = "RESTRICTED_MARKET_STATE_STRUCTURE_RETEST_EVALUATOR_UNDERPOWERED_NO_VALIDATION"
        decision_class = "UNDERPOWERED_FOR_TINY_GLOBAL_ALPHA_ROUTE_BUDGET_CONSUMED"
        reason = "Null run count cannot resolve the tiny global alpha budget; route is not validated and cannot release."
    else:
        evaluator_status = "RESTRICTED_MARKET_STATE_STRUCTURE_RETEST_EVALUATOR_POLICY_GATE_FAIL_ROUTE_NOT_VALIDATED"
        decision_class = "PROCEDURAL_NULL_OR_POLICY_GATE_FAIL_ROUTE_NOT_VALIDATED"
        reason = "Restricted retest failed its empirical/policy gate; route is not validated and cannot release."

    release_allowed = False

    evaluator_state = {
        "state_name": "edge_factory_os_restricted_market_state_structure_retest_evaluator_state_v1",
        "created_at_utc": utc_now_iso(),
        "evaluator_status": evaluator_status,
        "decision_class": decision_class,
        "strict_policy_key": STRICT_POLICY_KEY,
        "contract_id": contract_id,
        "route_hash": route_hash,
        "route_family": route_family,
        "alpha_budget": alpha_budget,
        "route_budget": route_budget,
        "observed_score_eta2": observed_score_eta2,
        "max_p_empirical_plus_one": max_p,
        "min_resolvable_p_plus_one": min_p,
        "required_runs_per_null_model_for_alpha": required_runs,
        "current_runs_per_null_model": current_runs,
        "estimated_total_required_null_runs": estimated_total_required_null_runs,
        "alpha_resolution_pass": alpha_resolution_pass,
        "p_value_pass": p_value_pass,
        "restricted_retest_policy_gate_pass": policy_gate_pass,
        "route_budget_consumed": route_budget_consumed,
        "release_allowed": False,
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        "next_recommended_research_key": NEXT_RESEARCH_KEY,
        "next_module": NEXT_MODULE,
        **SAFETY_FLAGS,
    }

    next_queue = {
        "queue_name": "edge_factory_os_restricted_market_state_structure_retest_evaluator_next_queue_v1",
        "created_at_utc": utc_now_iso(),
        "queue_status": "RESTRICTED_RETEST_EVALUATOR_NEXT_QUEUE_READY",
        "top_next_research_key": NEXT_RESEARCH_KEY,
        "top_next_module": NEXT_MODULE,
        "reason": "Do not blindly run more nulls. First evaluate feasibility/cost of required null power under governance.",
        "required_runs_per_null_model_for_alpha": required_runs,
        "current_runs_per_null_model": current_runs,
        "estimated_total_required_null_runs": estimated_total_required_null_runs,
        "release_allowed": False,
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
                "purpose": "Estimate whether allocating enough null-power to resolve tiny alpha is justified, without executing more research.",
                "required_runs_per_null_model_for_alpha": required_runs,
                "estimated_total_required_null_runs": estimated_total_required_null_runs,
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
        "evaluator_name": "edge_factory_os_restricted_market_state_structure_retest_evaluator_v1",
        "created_at_utc": utc_now_iso(),
        "evaluator_status": evaluator_status,
        "severity": "ATTENTION",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "next_action": "BUILD_RESTRICTED_NULL_POWER_FEASIBILITY_REVIEW_NO_EXECUTION",
        "reason": reason,
        "decision_class": decision_class,
        "contract_id": contract_id,
        "route_hash": route_hash,
        "route_family": route_family,
        "alpha_budget": alpha_budget,
        "route_budget": route_budget,
        "observed_score_eta2": observed_score_eta2,
        "max_p_empirical_plus_one": max_p,
        "min_resolvable_p_plus_one": min_p,
        "required_runs_per_null_model_for_alpha": required_runs,
        "current_runs_per_null_model": current_runs,
        "estimated_total_required_null_runs": estimated_total_required_null_runs,
        "alpha_resolution_pass": alpha_resolution_pass,
        "p_value_pass": p_value_pass,
        "restricted_retest_policy_gate_pass": policy_gate_pass,
        "route_budget_consumed": route_budget_consumed,
        "release_allowed": release_allowed,
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        "input_runner_status": runner.get("runner_status"),
        "input_runner_json": str(RUNNER_JSON),
        "input_runner_state_json": str(RUNNER_STATE_JSON),
        "budget_consumption_json": str(BUDGET_CONSUMPTION_JSON),
        "execution_policy_status": execution_policy.get("policy_status"),
        "budget_allocation_status": budget_allocation.get("allocation_status"),
        "vault_status": vault.get("vault_status"),
        "global_alpha_accounting_status": alpha_accounting.get("accounting_status"),
        "holdout_selected": holdout_registry.get("holdout_selected"),
        "holdout_peeked": holdout_registry.get("holdout_peeked"),
        "holdout_access_allowed_now": holdout_access.get("holdout_access_allowed_now"),
        "next_recommended_research_key": NEXT_RESEARCH_KEY,
        "next_module": NEXT_MODULE,
        "evaluator_state": evaluator_state,
        "next_queue": next_queue,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "evaluator_state_json": str(REPO_EVALUATOR_STATE_JSON),
        "next_queue_json": str(REPO_NEXT_QUEUE_JSON),
        **SAFETY_FLAGS,
    }

    write_json(REPO_EVALUATOR_STATE_JSON, evaluator_state)
    write_json(REPO_NEXT_QUEUE_JSON, next_queue)
    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text(result))
    print_summary(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
