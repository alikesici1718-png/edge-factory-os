#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Restricted Research Execution Gate v1

Purpose:
- Consume restricted pre-registered contract proposal.
- Consume preflight validation.
- Consume tiny research-only budget allocation.
- Decide whether a bounded OFFLINE/READ-ONLY restricted research runner may be built/executed.
- Keep broad strategy search blocked.
- Keep final holdout access forbidden.
- Keep candidate/family/runtime/capital/active-paper/live/real-order actions blocked.

This gate does NOT:
- run research
- generate candidates
- create candidate trading contracts
- release families
- touch runtime
- change capital
- start active paper
- enable live
- place real orders
- delete/move/archive files
"""

from __future__ import annotations

import csv
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

FRAMEWORK_DIR = REPO_DIR / "edge_factory_os_framework"
POLICY_DIR = FRAMEWORK_DIR / "policies"
CONTRACT_DIR = FRAMEWORK_DIR / "contracts"
REGISTRY_DIR = FRAMEWORK_DIR / "registries"
QUEUE_DIR = FRAMEWORK_DIR / "queues"

PROPOSED_CONTRACT_JSON = CONTRACT_DIR / "restricted_pre_registered_research_contract_proposal_v1.json"
PREFLIGHT_STATE_JSON = POLICY_DIR / "restricted_research_contract_preflight_validation_state_v1.json"
BUDGET_ALLOCATION_JSON = POLICY_DIR / "restricted_research_budget_allocation_v1.json"
BUDGET_GATE_STATE_JSON = POLICY_DIR / "restricted_research_budget_allocation_gate_state_v1.json"
BUDGET_NEXT_QUEUE_JSON = QUEUE_DIR / "restricted_research_budget_allocation_next_queue_v1.json"

GLOBAL_ALPHA_ACCOUNTING_JSON = POLICY_DIR / "global_route_family_alpha_accounting_v1.json"
GLOBAL_ALPHA_POLICY_JSON = POLICY_DIR / "global_alpha_spending_policy_v1.json"
GLOBAL_LEDGER_JSON = POLICY_DIR / "global_multiple_testing_ledger_v1.json"
PROMISING_VAULT_JSON = POLICY_DIR / "promising_signal_vault_v1.json"

UNTOUCHED_HOLDOUT_REGISTRY_JSON = REGISTRY_DIR / "untouched_holdout_registry_v1.json"
NESTED_VALIDATION_POLICY_JSON = POLICY_DIR / "nested_validation_policy_v1.json"
HOLDOUT_ACCESS_CONTROL_JSON = POLICY_DIR / "holdout_access_control_policy_v1.json"
PRE_REG_POLICY_JSON = POLICY_DIR / "pre_registration_policy_v1.json"

LESSON_INDEX_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

OUT_DIR = BASE_DIR / "edge_factory_os_restricted_research_execution_gate"
OUT_JSON = OUT_DIR / "restricted_research_execution_gate_latest.json"
OUT_TXT = OUT_DIR / "restricted_research_execution_gate_latest.txt"
OUT_GATES_CSV = OUT_DIR / "restricted_research_execution_gate_checks_latest.csv"

REPO_EXECUTION_GATE_STATE_JSON = POLICY_DIR / "restricted_research_execution_gate_state_v1.json"
REPO_EXECUTION_POLICY_JSON = POLICY_DIR / "restricted_research_execution_policy_v1.json"
REPO_NEXT_QUEUE_JSON = QUEUE_DIR / "restricted_research_execution_next_queue_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD7_09_RESTRICTED_MARKET_STATE_STRUCTURE_RETEST_RUNNER"
NEXT_MODULE = "edge_factory_os_restricted_market_state_structure_retest_runner_v1.py"

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


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fields: List[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def extract_list(obj: Any, key: str) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get(key), list):
        return [x for x in obj[key] if isinstance(x, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def route_hash_blocked(blocked_routes: List[Dict[str, Any]], route_hash: str) -> bool:
    return route_hash in {str(x.get("route_hash")) for x in blocked_routes if isinstance(x, dict)}


def gate(key: str, passed: bool, observed: Any, required: Any, severity: str = "HARD") -> Dict[str, Any]:
    return {
        "gate_key": key,
        "severity": severity,
        "passed": bool(passed),
        "observed": observed,
        "required": required,
    }


def safety_flags_all_false(obj: Dict[str, Any], label: str) -> List[Dict[str, Any]]:
    rows = []
    for key in SAFETY_FLAGS:
        observed = obj.get(key, False)
        rows.append({
            "gate_key": f"{label}_{key.upper()}_FALSE",
            "severity": "HARD",
            "passed": observed is False,
            "observed": observed,
            "required": False,
        })
    return rows


def build_text(result: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS RESTRICTED RESEARCH EXECUTION GATE v1")
    lines.append("=" * 100)

    for key in [
        "execution_gate_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "execution_gate_pass",
        "restricted_offline_research_runner_allowed",
        "broad_strategy_search_allowed",
        "holdout_access_allowed",
        "candidate_generation_allowed",
        "family_release_allowed",
        "runtime_touch_allowed",
        "capital_change_allowed",
        "active_paper_allowed",
        "live_allowed",
        "real_orders_allowed",
        "contract_id",
        "route_hash",
        "route_family",
        "alpha_budget",
        "route_budget",
        "failed_gate_count",
        "failed_gate_keys",
        "next_recommended_research_key",
        "next_module",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("CORE DECISION")
    lines.append("-" * 100)
    lines.append("Only one bounded offline/read-only research runner may be built if this gate passes.")
    lines.append("The runner must consume the pre-registered contract exactly as written.")
    lines.append("No broad search, no holdout access, no candidate generation, no release, no runtime/capital/live.")
    lines.append("Even if the runner later finds something, it must go to evaluator/governance, not promotion.")

    lines.append("")
    lines.append("FAILED GATES")
    lines.append("-" * 100)
    for key in result.get("failed_gate_keys", []):
        lines.append(f"- {key}")

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
        "gates_csv",
        "execution_gate_state_json",
        "execution_policy_json",
        "next_queue_json",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS RESTRICTED RESEARCH EXECUTION GATE v1")
    print("=" * 100)
    print(f"execution_gate_status: {result.get('execution_gate_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"execution_gate_pass: {result.get('execution_gate_pass')}")
    print(f"restricted_offline_research_runner_allowed: {result.get('restricted_offline_research_runner_allowed')}")
    print(f"broad_strategy_search_allowed: {result.get('broad_strategy_search_allowed')}")
    print(f"holdout_access_allowed: {result.get('holdout_access_allowed')}")
    print(f"contract_id: {result.get('contract_id')}")
    print(f"route_hash: {result.get('route_hash')}")
    print(f"route_family: {result.get('route_family')}")
    print(f"alpha_budget: {result.get('alpha_budget')}")
    print(f"route_budget: {result.get('route_budget')}")
    print(f"failed_gate_count: {result.get('failed_gate_count')}")
    print(f"failed_gate_keys: {result.get('failed_gate_keys')}")
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
    print(f"GATES: {result.get('gates_csv')}")
    print(f"STATE: {result.get('execution_gate_state_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    contract = load_json(PROPOSED_CONTRACT_JSON, {})
    preflight = load_json(PREFLIGHT_STATE_JSON, {})
    allocation = load_json(BUDGET_ALLOCATION_JSON, {})
    budget_gate_state = load_json(BUDGET_GATE_STATE_JSON, {})
    budget_queue = load_json(BUDGET_NEXT_QUEUE_JSON, {})
    alpha_accounting = load_json(GLOBAL_ALPHA_ACCOUNTING_JSON, {})
    alpha_policy = load_json(GLOBAL_ALPHA_POLICY_JSON, {})
    ledger = load_json(GLOBAL_LEDGER_JSON, {})
    vault = load_json(PROMISING_VAULT_JSON, {})
    holdout_registry = load_json(UNTOUCHED_HOLDOUT_REGISTRY_JSON, {})
    nested = load_json(NESTED_VALIDATION_POLICY_JSON, {})
    holdout_access = load_json(HOLDOUT_ACCESS_CONTROL_JSON, {})
    pre_reg = load_json(PRE_REG_POLICY_JSON, {})
    lessons = extract_list(load_json(LESSON_INDEX_JSON, {}), "lessons")
    blocked_routes = extract_list(load_json(BLOCKLIST_JSON, {}), "blocked_routes")
    vault_items = extract_list(vault, "vault_items")

    contract_id = contract.get("contract_id")
    route_hash = str(contract.get("route_hash") or "")
    route_family = str(contract.get("route_family") or "")
    route_is_blocked = route_hash_blocked(blocked_routes, route_hash)

    alpha_budget = float(allocation.get("proposed_alpha_budget", 0.0))
    route_budget = int(allocation.get("proposed_route_budget", 0))
    diagnostic_alpha = float(allocation.get("diagnostic_alpha_after_pressure", 0.0))

    gates: List[Dict[str, Any]] = [
        gate("CONTRACT_READY_NOT_EXECUTABLE", contract.get("contract_status") == "RESTRICTED_RESEARCH_CONTRACT_PROPOSAL_READY_NOT_EXECUTABLE", contract.get("contract_status"), "RESTRICTED_RESEARCH_CONTRACT_PROPOSAL_READY_NOT_EXECUTABLE"),
        gate("CONTRACT_ID_PRESENT", bool(contract_id), contract_id, "non-empty"),
        gate("ROUTE_HASH_PRESENT", bool(route_hash), route_hash, "non-empty"),
        gate("ROUTE_HASH_NOT_BLOCKED", not route_is_blocked, route_is_blocked, False),
        gate("ROUTE_FAMILY_MARKET_STATE_ONLY", route_family == "MARKET_STATE_TRANSITION_FAMILY", route_family, "MARKET_STATE_TRANSITION_FAMILY"),
        gate("PREFLIGHT_PASS", preflight.get("preflight_pass") is True, preflight.get("preflight_pass"), True),
        gate("PREFLIGHT_NON_EXECUTABLE", preflight.get("contract_non_executable") is True, preflight.get("contract_non_executable"), True),
        gate("BUDGET_GATE_PASS", budget_gate_state.get("budget_gate_pass") is True, budget_gate_state.get("budget_gate_pass"), True),
        gate("BUDGET_ALLOCATION_CREATED", allocation.get("budget_gate_pass") is True, allocation.get("budget_gate_pass"), True),
        gate("BUDGET_QUEUE_READY", budget_queue.get("queue_status") == "RESTRICTED_RESEARCH_BUDGET_ALLOCATION_NEXT_QUEUE_READY", budget_queue.get("queue_status"), "RESTRICTED_RESEARCH_BUDGET_ALLOCATION_NEXT_QUEUE_READY"),
        gate("ALPHA_BUDGET_POSITIVE", alpha_budget > 0.0, alpha_budget, ">0"),
        gate("ALPHA_BUDGET_NOT_ABOVE_DIAGNOSTIC_ALPHA", alpha_budget <= diagnostic_alpha, {"alpha_budget": alpha_budget, "diagnostic_alpha": diagnostic_alpha}, "<= diagnostic_alpha"),
        gate("ROUTE_BUDGET_EXACTLY_ONE", route_budget == 1, route_budget, 1),
        gate("GLOBAL_ALPHA_ACCOUNTING_PASS", alpha_accounting.get("global_alpha_accounting_pass") is True, alpha_accounting.get("global_alpha_accounting_pass"), True),
        gate("GLOBAL_ALPHA_POLICY_ACTIVE", alpha_policy.get("policy_status") == "GLOBAL_ALPHA_SPENDING_POLICY_ACTIVE_ZERO_STRATEGY_BUDGET", alpha_policy.get("policy_status"), "GLOBAL_ALPHA_SPENDING_POLICY_ACTIVE_ZERO_STRATEGY_BUDGET"),
        gate("GLOBAL_LEDGER_ACTIVE", ledger.get("ledger_status") == "GLOBAL_MULTIPLE_TESTING_LEDGER_ACTIVE_RESEARCH_LOCKED", ledger.get("ledger_status"), "GLOBAL_MULTIPLE_TESTING_LEDGER_ACTIVE_RESEARCH_LOCKED"),
        gate("PRE_REGISTRATION_POLICY_ACTIVE", pre_reg.get("all_future_research_must_be_pre_registered") is True, pre_reg.get("all_future_research_must_be_pre_registered"), True),
        gate("POST_HOC_SUCCESS_CRITERIA_FORBIDDEN", pre_reg.get("post_hoc_success_criteria_allowed") is False, pre_reg.get("post_hoc_success_criteria_allowed"), False),
        gate("NESTED_VALIDATION_READY", nested.get("policy_status") == "NESTED_VALIDATION_POLICY_READY_STRATEGY_SEARCH_LOCKED", nested.get("policy_status"), "NESTED_VALIDATION_POLICY_READY_STRATEGY_SEARCH_LOCKED"),
        gate("HOLDOUT_ACCESS_FORBIDDEN", holdout_access.get("holdout_access_allowed_now") is False and contract.get("holdout_access_allowed") is False, {"policy": holdout_access.get("holdout_access_allowed_now"), "contract": contract.get("holdout_access_allowed")}, "all False"),
        gate("HOLDOUT_NOT_SELECTED", holdout_registry.get("holdout_selected") is False, holdout_registry.get("holdout_selected"), False),
        gate("HOLDOUT_NOT_PEEKED", holdout_registry.get("holdout_peeked") is False, holdout_registry.get("holdout_peeked"), False),
        gate("HOLDOUT_NOT_USABLE_NOW", holdout_registry.get("holdout_usable_now") is False, holdout_registry.get("holdout_usable_now"), False),
        gate("BROAD_STRATEGY_SEARCH_BLOCKED", contract.get("broad_strategy_search_allowed") is False and allocation.get("broad_strategy_search_allowed") is False, {"contract": contract.get("broad_strategy_search_allowed"), "allocation": allocation.get("broad_strategy_search_allowed")}, "all False"),
        gate("PROCEDURAL_NULL_REQUIRED", contract.get("procedural_null_required") is True and "procedural_joint_null_full_search" in contract.get("null_models_pre_declared", []), contract.get("null_models_pre_declared"), "procedural_joint_null_full_search present"),
        gate("RESEARCH_CONTRACT_MUTATION_LOCKED", contract.get("contract_mutation_after_start_invalidates_route") is True, contract.get("contract_mutation_after_start_invalidates_route"), True),
        gate("VAULT_ACTIVE_AND_HAS_ITEM", vault.get("vault_status") == "PROMISING_SIGNAL_VAULT_ACTIVE_RELEASE_BLOCKED" and len(vault_items) >= 1, {"vault_status": vault.get("vault_status"), "vault_items": len(vault_items)}, "active and >=1"),
        gate("LESSONS_PRESENT", len(lessons) >= 1, len(lessons), ">=1"),
        gate("BLOCKLIST_PRESENT", len(blocked_routes) >= 1, len(blocked_routes), ">=1"),
    ]

    gates.extend(safety_flags_all_false(contract, "CONTRACT"))
    gates.extend(safety_flags_all_false(preflight, "PREFLIGHT"))
    gates.extend(safety_flags_all_false(allocation, "BUDGET_ALLOCATION"))
    gates.extend(safety_flags_all_false(budget_gate_state, "BUDGET_GATE_STATE"))
    gates.extend(safety_flags_all_false(alpha_accounting, "ALPHA_ACCOUNTING"))
    gates.extend(safety_flags_all_false(alpha_policy, "ALPHA_POLICY"))
    gates.extend(safety_flags_all_false(holdout_registry, "HOLDOUT_REGISTRY"))
    gates.extend(safety_flags_all_false(holdout_access, "HOLDOUT_ACCESS"))

    failed = [row["gate_key"] for row in gates if row["passed"] is not True]
    execution_gate_pass = len(failed) == 0

    restricted_runner_allowed = execution_gate_pass

    if execution_gate_pass:
        execution_gate_status = "RESTRICTED_RESEARCH_EXECUTION_GATE_PASS_OFFLINE_RUNNER_ALLOWED"
        severity = "ATTENTION"
        allowed_scope = "OFFLINE_RESEARCH_ONLY"
        next_action = "BUILD_RESTRICTED_MARKET_STATE_STRUCTURE_RETEST_RUNNER_NO_CANDIDATES_NO_RELEASE"
        reason = "restricted offline research runner may be built/executed once; no candidates, no release, no runtime/capital/live, no holdout access"
        next_module = NEXT_MODULE
        return_code = 0
    else:
        execution_gate_status = "RESTRICTED_RESEARCH_EXECUTION_GATE_FAIL_REVIEW_REQUIRED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_RESTRICTED_EXECUTION_GATE_FAILURES_BEFORE_RUNNER"
        reason = f"failed_gate_count={len(failed)}"
        next_module = None
        return_code = 2

    execution_policy = {
        "policy_name": "edge_factory_os_restricted_research_execution_policy_v1",
        "created_at_utc": utc_now_iso(),
        "policy_status": "RESTRICTED_RESEARCH_EXECUTION_POLICY_ACTIVE_OFFLINE_ONLY" if execution_gate_pass else "RESTRICTED_RESEARCH_EXECUTION_POLICY_BLOCKED",
        "restricted_offline_research_runner_allowed": restricted_runner_allowed,
        "allowed_runner_module": NEXT_MODULE if execution_gate_pass else None,
        "allowed_contract_id": contract_id if execution_gate_pass else None,
        "allowed_route_hash": route_hash if execution_gate_pass else None,
        "allowed_route_family": route_family if execution_gate_pass else None,
        "alpha_budget": alpha_budget if execution_gate_pass else 0.0,
        "route_budget": route_budget if execution_gate_pass else 0,
        "run_limit": 1 if execution_gate_pass else 0,
        "allowed_scope": "OFFLINE_RESEARCH_ONLY" if execution_gate_pass else "READ_ONLY_REVIEW",
        "broad_strategy_search_allowed": False,
        "holdout_access_allowed": False,
        "candidate_generation_allowed": False,
        "candidate_contract_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        "must_output": [
            "restricted_market_state_structure_retest_runner_latest.json",
            "restricted_market_state_structure_retest_runner_latest.txt",
            "restricted_market_state_structure_retest_summary_latest.csv",
            "procedural_null_summary",
            "governance_gate_feed",
        ],
        "must_not_output": [
            "candidate_contract",
            "family_release",
            "runtime_patch",
            "capital_change",
            "live_order",
            "active_paper_enable",
        ],
        "hard_rules": [
            "consume pre-registered contract exactly",
            "no post-hoc feature/threshold/axis expansion",
            "no holdout access",
            "one route budget only",
            "procedural null must be included",
            "result cannot promote directly",
            "result must go to evaluator/governance",
        ],
        "release_gate_feed": {
            "RESTRICTED_RESEARCH_EXECUTION_GATE_PASS": execution_gate_pass,
            "RESTRICTED_OFFLINE_RESEARCH_RUNNER_ALLOWED": restricted_runner_allowed,
            "BROAD_STRATEGY_SEARCH_ALLOWED": False,
            "HOLDOUT_ACCESS_ALLOWED": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_EXECUTION_POLICY": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_EXECUTION_POLICY": False,
            "FAMILY_RELEASE_ALLOWED_FROM_EXECUTION_POLICY": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_EXECUTION_POLICY": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_EXECUTION_POLICY": False,
            "ACTIVE_PAPER_ALLOWED_FROM_EXECUTION_POLICY": False,
            "LIVE_ALLOWED_FROM_EXECUTION_POLICY": False,
            "REAL_ORDERS_ALLOWED_FROM_EXECUTION_POLICY": False,
        },
        **SAFETY_FLAGS,
    }

    execution_gate_state = {
        "state_name": "edge_factory_os_restricted_research_execution_gate_state_v1",
        "created_at_utc": utc_now_iso(),
        "execution_gate_status": execution_gate_status,
        "execution_gate_pass": execution_gate_pass,
        "restricted_offline_research_runner_allowed": restricted_runner_allowed,
        "contract_id": contract_id,
        "route_hash": route_hash,
        "route_family": route_family,
        "alpha_budget": alpha_budget if execution_gate_pass else 0.0,
        "route_budget": route_budget if execution_gate_pass else 0,
        "broad_strategy_search_allowed": False,
        "holdout_access_allowed": False,
        "failed_gate_count": len(failed),
        "failed_gate_keys": failed,
        "next_recommended_research_key": NEXT_RESEARCH_KEY if execution_gate_pass else None,
        "next_module": next_module,
        **SAFETY_FLAGS,
    }

    next_queue = {
        "queue_name": "edge_factory_os_restricted_research_execution_next_queue_v1",
        "created_at_utc": utc_now_iso(),
        "queue_status": "RESTRICTED_RESEARCH_EXECUTION_NEXT_QUEUE_READY" if execution_gate_pass else "RESTRICTED_RESEARCH_EXECUTION_QUEUE_BLOCKED_REVIEW_REQUIRED",
        "restricted_offline_research_runner_allowed": restricted_runner_allowed,
        "broad_strategy_search_allowed": False,
        "holdout_access_allowed": False,
        "top_next_research_key": NEXT_RESEARCH_KEY if execution_gate_pass else None,
        "top_next_module": next_module,
        "next_steps": [
            {
                "research_key": NEXT_RESEARCH_KEY,
                "module": NEXT_MODULE,
                "priority": 100,
                "allowed_scope": "OFFLINE_RESEARCH_ONLY",
                "purpose": "Run the restricted market-state structure retest exactly once under pre-registered contract and procedural null, with no candidates/release/runtime/capital/live.",
                "contract_id": contract_id,
                "route_hash": route_hash,
                "alpha_budget": alpha_budget,
                "route_budget": route_budget,
                "broad_strategy_search_allowed": False,
                "holdout_access_allowed": False,
                "candidate_generation_allowed": False,
                "family_release_allowed": False,
                "runtime_touch_allowed": False,
                "capital_change_allowed": False,
                "active_paper_allowed": False,
                "live_allowed": False,
                "real_orders_allowed": False,
            }
        ] if execution_gate_pass else [],
        **SAFETY_FLAGS,
    }

    write_csv(OUT_GATES_CSV, gates)
    write_json(REPO_EXECUTION_GATE_STATE_JSON, execution_gate_state)
    write_json(REPO_EXECUTION_POLICY_JSON, execution_policy)
    write_json(REPO_NEXT_QUEUE_JSON, next_queue)

    result = {
        "gate_name": "edge_factory_os_restricted_research_execution_gate_v1",
        "created_at_utc": utc_now_iso(),
        "execution_gate_status": execution_gate_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "execution_gate_pass": execution_gate_pass,
        "restricted_offline_research_runner_allowed": restricted_runner_allowed,
        "broad_strategy_search_allowed": False,
        "holdout_access_allowed": False,
        "contract_id": contract_id,
        "route_hash": route_hash,
        "route_family": route_family,
        "alpha_budget": alpha_budget if execution_gate_pass else 0.0,
        "route_budget": route_budget if execution_gate_pass else 0,
        "failed_gate_count": len(failed),
        "failed_gate_keys": failed,
        "next_recommended_research_key": NEXT_RESEARCH_KEY if execution_gate_pass else None,
        "next_module": next_module,
        "gate_rows": gates,
        "execution_gate_state": execution_gate_state,
        "execution_policy": execution_policy,
        "next_queue": next_queue,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "gates_csv": str(OUT_GATES_CSV),
        "execution_gate_state_json": str(REPO_EXECUTION_GATE_STATE_JSON),
        "execution_policy_json": str(REPO_EXECUTION_POLICY_JSON),
        "next_queue_json": str(REPO_NEXT_QUEUE_JSON),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text(result))
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
