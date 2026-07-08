#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Restricted Research Contract Preflight Validator v1

Purpose:
- Validate the restricted pre-registered research contract proposal.
- Confirm it is non-executable right now.
- Confirm broad strategy search remains blocked.
- Confirm holdout access is forbidden.
- Confirm alpha/budget are still zero.
- Confirm procedural null, nested validation, pre-registration, blocklist preflight are required.
- Confirm candidate/family/runtime/capital/active-paper/live/real-order actions remain blocked.

This validator does NOT:
- run research
- allocate nonzero alpha/budget
- select/expose/use final holdout
- generate candidates
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
FACTORY_STATE_JSON = POLICY_DIR / "restricted_pre_registered_research_contract_factory_state_v1.json"
FACTORY_NEXT_QUEUE_JSON = QUEUE_DIR / "restricted_pre_registered_research_contract_factory_next_queue_v1.json"

REOPEN_STATE_JSON = POLICY_DIR / "governed_research_reopen_gate_state_v1.json"
REOPEN_POLICY_JSON = POLICY_DIR / "governed_research_reopen_policy_v1.json"
RESTRICTED_TEMPLATE_JSON = CONTRACT_DIR / "restricted_pre_registered_research_contract_template_v1.json"

PROMISING_VAULT_JSON = POLICY_DIR / "promising_signal_vault_v1.json"
GLOBAL_ALPHA_ACCOUNTING_JSON = POLICY_DIR / "global_route_family_alpha_accounting_v1.json"
GLOBAL_ALPHA_POLICY_JSON = POLICY_DIR / "global_alpha_spending_policy_v1.json"
UNTOUCHED_HOLDOUT_REGISTRY_JSON = REGISTRY_DIR / "untouched_holdout_registry_v1.json"
NESTED_VALIDATION_POLICY_JSON = POLICY_DIR / "nested_validation_policy_v1.json"
HOLDOUT_ACCESS_CONTROL_JSON = POLICY_DIR / "holdout_access_control_policy_v1.json"
PRE_REG_POLICY_JSON = POLICY_DIR / "pre_registration_policy_v1.json"
ROUTE_BUDGET_POLICY_JSON = POLICY_DIR / "route_budget_allocation_policy_v1.json"

LESSON_INDEX_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

OUT_DIR = BASE_DIR / "edge_factory_os_restricted_research_contract_preflight_validator"
OUT_JSON = OUT_DIR / "restricted_research_contract_preflight_validator_latest.json"
OUT_TXT = OUT_DIR / "restricted_research_contract_preflight_validator_latest.txt"
OUT_GATES_CSV = OUT_DIR / "restricted_research_contract_preflight_gates_latest.csv"

REPO_PREFLIGHT_STATE_JSON = POLICY_DIR / "restricted_research_contract_preflight_validation_state_v1.json"
REPO_NEXT_QUEUE_JSON = QUEUE_DIR / "restricted_research_contract_preflight_next_queue_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD7_07_RESTRICTED_RESEARCH_BUDGET_ALLOCATION_GATE"
NEXT_MODULE = "edge_factory_os_restricted_research_budget_allocation_gate_v1.py"

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


def list_has_items(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0


def build_text(result: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS RESTRICTED RESEARCH CONTRACT PREFLIGHT VALIDATOR v1")
    lines.append("=" * 100)

    for key in [
        "preflight_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "preflight_pass",
        "failed_gate_count",
        "failed_gate_keys",
        "contract_id",
        "route_hash",
        "route_hash_blocked",
        "contract_pre_registered",
        "contract_non_executable",
        "broad_strategy_search_allowed",
        "research_execution_allowed_now",
        "holdout_access_allowed",
        "alpha_budget_requested",
        "route_budget_requested",
        "next_recommended_research_key",
        "next_module",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("CORE DECISION")
    lines.append("-" * 100)
    lines.append("The restricted contract passes preflight only as a NON-EXECUTABLE proposal.")
    lines.append("No research execution is allowed from this validator.")
    lines.append("If preflight passes, the next module may consider explicit budget allocation governance.")
    lines.append("Candidate/family/runtime/capital/active-paper/live/real-order actions remain blocked.")

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
        "preflight_state_json",
        "next_queue_json",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS RESTRICTED RESEARCH CONTRACT PREFLIGHT VALIDATOR v1")
    print("=" * 100)
    print(f"preflight_status: {result.get('preflight_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"preflight_pass: {result.get('preflight_pass')}")
    print(f"failed_gate_count: {result.get('failed_gate_count')}")
    print(f"failed_gate_keys: {result.get('failed_gate_keys')}")
    print(f"contract_id: {result.get('contract_id')}")
    print(f"route_hash: {result.get('route_hash')}")
    print(f"route_hash_blocked: {result.get('route_hash_blocked')}")
    print(f"contract_pre_registered: {result.get('contract_pre_registered')}")
    print(f"contract_non_executable: {result.get('contract_non_executable')}")
    print(f"broad_strategy_search_allowed: {result.get('broad_strategy_search_allowed')}")
    print(f"research_execution_allowed_now: {result.get('research_execution_allowed_now')}")
    print(f"holdout_access_allowed: {result.get('holdout_access_allowed')}")
    print(f"alpha_budget_requested: {result.get('alpha_budget_requested')}")
    print(f"route_budget_requested: {result.get('route_budget_requested')}")
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
    print(f"STATE: {result.get('preflight_state_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    contract = load_json(PROPOSED_CONTRACT_JSON, {})
    factory_state = load_json(FACTORY_STATE_JSON, {})
    factory_queue = load_json(FACTORY_NEXT_QUEUE_JSON, {})
    reopen_state = load_json(REOPEN_STATE_JSON, {})
    reopen_policy = load_json(REOPEN_POLICY_JSON, {})
    template = load_json(RESTRICTED_TEMPLATE_JSON, {})
    vault = load_json(PROMISING_VAULT_JSON, {})
    alpha_accounting = load_json(GLOBAL_ALPHA_ACCOUNTING_JSON, {})
    alpha_policy = load_json(GLOBAL_ALPHA_POLICY_JSON, {})
    holdout_registry = load_json(UNTOUCHED_HOLDOUT_REGISTRY_JSON, {})
    nested_policy = load_json(NESTED_VALIDATION_POLICY_JSON, {})
    holdout_access = load_json(HOLDOUT_ACCESS_CONTROL_JSON, {})
    pre_reg_policy = load_json(PRE_REG_POLICY_JSON, {})
    route_budget_policy = load_json(ROUTE_BUDGET_POLICY_JSON, {})

    lessons = extract_list(load_json(LESSON_INDEX_JSON, {}), "lessons")
    blocked_routes = extract_list(load_json(BLOCKLIST_JSON, {}), "blocked_routes")
    vault_items = extract_list(vault, "vault_items")

    route_hash = str(contract.get("route_hash") or "")
    route_is_blocked = route_hash_blocked(blocked_routes, route_hash)

    budget_allocation = contract.get("budget_allocation_pre_declared")
    if not isinstance(budget_allocation, dict):
        budget_allocation = {}

    success_criteria = contract.get("success_criteria_pre_declared")
    if not isinstance(success_criteria, dict):
        success_criteria = {}

    failure_criteria = contract.get("failure_criteria_pre_declared")
    if not isinstance(failure_criteria, dict):
        failure_criteria = {}

    nested_plan = contract.get("nested_validation_plan")
    if not isinstance(nested_plan, dict):
        nested_plan = {}

    alpha_budget_requested = float(budget_allocation.get("alpha_budget_requested", -1))
    route_budget_requested = int(budget_allocation.get("route_budget_requested", -1))

    gates: List[Dict[str, Any]] = [
        gate("PROPOSED_CONTRACT_EXISTS", bool(contract), bool(contract), True),
        gate("CONTRACT_STATUS_READY_NOT_EXECUTABLE", contract.get("contract_status") == "RESTRICTED_RESEARCH_CONTRACT_PROPOSAL_READY_NOT_EXECUTABLE", contract.get("contract_status"), "RESTRICTED_RESEARCH_CONTRACT_PROPOSAL_READY_NOT_EXECUTABLE"),
        gate("CONTRACT_ID_PRESENT", bool(contract.get("contract_id")), contract.get("contract_id"), "non-empty"),
        gate("ROUTE_HASH_PRESENT", bool(route_hash), route_hash, "non-empty"),
        gate("ROUTE_HASH_NOT_BLOCKED", not route_is_blocked, route_is_blocked, False),
        gate("RESEARCH_KEY_PRESENT", bool(contract.get("research_key")), contract.get("research_key"), "non-empty"),
        gate("ROUTE_FAMILY_PRESENT", bool(contract.get("route_family")), contract.get("route_family"), "non-empty"),
        gate("HYPOTHESIS_PRESENT", bool(contract.get("hypothesis_plain_english")), contract.get("hypothesis_plain_english"), "non-empty"),
        gate("BROAD_STRATEGY_SEARCH_BLOCKED_IN_CONTRACT", contract.get("broad_strategy_search_allowed") is False, contract.get("broad_strategy_search_allowed"), False),
        gate("RESEARCH_EXECUTION_BLOCKED_IN_CONTRACT", contract.get("research_execution_allowed_now") is False, contract.get("research_execution_allowed_now"), False),
        gate("CONTRACT_PREFLIGHT_REQUIRED", contract.get("contract_preflight_required") is True, contract.get("contract_preflight_required"), True),
        gate("HOLDOUT_ACCESS_FORBIDDEN_IN_CONTRACT", contract.get("holdout_access_allowed") is False and contract.get("holdout_access_policy") == "FORBIDDEN", {"holdout_access_allowed": contract.get("holdout_access_allowed"), "holdout_access_policy": contract.get("holdout_access_policy")}, "False/FORBIDDEN"),
        gate("FEATURE_FAMILY_PRE_DECLARED", list_has_items(contract.get("feature_family_pre_declared")), contract.get("feature_family_pre_declared"), "non-empty list"),
        gate("THRESHOLD_GRID_PRE_DECLARED", list_has_items(contract.get("threshold_grid_pre_declared")), contract.get("threshold_grid_pre_declared"), "non-empty list"),
        gate("AXIS_FAMILY_PRE_DECLARED", list_has_items(contract.get("axis_family_pre_declared")), contract.get("axis_family_pre_declared"), "non-empty list"),
        gate("NULL_MODELS_PRE_DECLARED", list_has_items(contract.get("null_models_pre_declared")), contract.get("null_models_pre_declared"), "non-empty list"),
        gate("PROCEDURAL_NULL_REQUIRED", contract.get("procedural_null_required") is True and "procedural_joint_null_full_search" in contract.get("null_models_pre_declared", []), contract.get("null_models_pre_declared"), "procedural_joint_null_full_search present"),
        gate("SUCCESS_CRITERIA_PRE_DECLARED", bool(success_criteria), success_criteria, "non-empty dict"),
        gate("FAILURE_CRITERIA_PRE_DECLARED", bool(failure_criteria), failure_criteria, "non-empty dict"),
        gate("POST_HOC_MUTATION_INVALIDATES_ROUTE", contract.get("contract_mutation_after_start_invalidates_route") is True, contract.get("contract_mutation_after_start_invalidates_route"), True),
        gate("SAME_ROUTE_HASH_REUSE_BLOCKED", contract.get("same_route_hash_reuse_allowed") is False, contract.get("same_route_hash_reuse_allowed"), False),
        gate("BLOCKED_ROUTE_PREFLIGHT_REQUIRED", contract.get("blocked_route_preflight_required") is True, contract.get("blocked_route_preflight_required"), True),
        gate("ALPHA_BUDGET_ZERO_AT_PREFLIGHT", alpha_budget_requested == 0.0, alpha_budget_requested, 0.0),
        gate("ROUTE_BUDGET_ZERO_AT_PREFLIGHT", route_budget_requested == 0, route_budget_requested, 0),
        gate("NESTED_PLAN_PRESENT", bool(nested_plan), nested_plan, "non-empty dict"),
        gate("NESTED_PREFLIGHT_REQUIRED", nested_plan.get("preflight_validator_required") is True, nested_plan.get("preflight_validator_required"), True),
        gate("FACTORY_STATE_PROPOSAL_CREATED", factory_state.get("restricted_contract_proposal_created") is True, factory_state.get("restricted_contract_proposal_created"), True),
        gate("FACTORY_STATE_RESEARCH_EXECUTION_BLOCKED", factory_state.get("research_execution_allowed_now") is False, factory_state.get("research_execution_allowed_now"), False),
        gate("FACTORY_QUEUE_READY", factory_queue.get("queue_status") == "RESTRICTED_CONTRACT_FACTORY_NEXT_QUEUE_READY", factory_queue.get("queue_status"), "RESTRICTED_CONTRACT_FACTORY_NEXT_QUEUE_READY"),
        gate("REOPEN_GATE_PASS", reopen_state.get("governed_reopen_gate_pass") is True, reopen_state.get("governed_reopen_gate_pass"), True),
        gate("REOPEN_POLICY_RESTRICTED_ONLY", reopen_policy.get("policy_status") == "GOVERNED_RESEARCH_REOPEN_POLICY_ACTIVE_RESTRICTED_CONTRACTS_ONLY", reopen_policy.get("policy_status"), "GOVERNED_RESEARCH_REOPEN_POLICY_ACTIVE_RESTRICTED_CONTRACTS_ONLY"),
        gate("TEMPLATE_READY", template.get("template_status") == "RESTRICTED_PRE_REGISTERED_RESEARCH_CONTRACT_TEMPLATE_READY", template.get("template_status"), "RESTRICTED_PRE_REGISTERED_RESEARCH_CONTRACT_TEMPLATE_READY"),
        gate("VAULT_ACTIVE_AND_HAS_ITEM", vault.get("vault_status") == "PROMISING_SIGNAL_VAULT_ACTIVE_RELEASE_BLOCKED" and len(vault_items) >= 1, {"vault_status": vault.get("vault_status"), "vault_items": len(vault_items)}, "active and >=1"),
        gate("ALPHA_ACCOUNTING_PASS", alpha_accounting.get("global_alpha_accounting_pass") is True, alpha_accounting.get("global_alpha_accounting_pass"), True),
        gate("ALPHA_POLICY_ZERO_STRATEGY_BUDGET", float(alpha_policy.get("current_total_strategy_alpha_budget", -1)) == 0.0 and int(alpha_policy.get("current_total_strategy_route_budget", -1)) == 0, {"alpha": alpha_policy.get("current_total_strategy_alpha_budget"), "routes": alpha_policy.get("current_total_strategy_route_budget")}, "0.0/0"),
        gate("HOLDOUT_NOT_SELECTED", holdout_registry.get("holdout_selected") is False, holdout_registry.get("holdout_selected"), False),
        gate("HOLDOUT_NOT_PEEKED", holdout_registry.get("holdout_peeked") is False, holdout_registry.get("holdout_peeked"), False),
        gate("HOLDOUT_NOT_USABLE_NOW", holdout_registry.get("holdout_usable_now") is False, holdout_registry.get("holdout_usable_now"), False),
        gate("HOLDOUT_ACCESS_BLOCKED", holdout_access.get("holdout_access_allowed_now") is False, holdout_access.get("holdout_access_allowed_now"), False),
        gate("NESTED_VALIDATION_READY", nested_policy.get("policy_status") == "NESTED_VALIDATION_POLICY_READY_STRATEGY_SEARCH_LOCKED", nested_policy.get("policy_status"), "NESTED_VALIDATION_POLICY_READY_STRATEGY_SEARCH_LOCKED"),
        gate("PRE_REG_POLICY_READY", pre_reg_policy.get("policy_status") == "PRE_REGISTRATION_POLICY_DRAFT_READY", pre_reg_policy.get("policy_status"), "PRE_REGISTRATION_POLICY_DRAFT_READY"),
        gate("POST_HOC_SUCCESS_CRITERIA_FORBIDDEN", pre_reg_policy.get("post_hoc_success_criteria_allowed") is False, pre_reg_policy.get("post_hoc_success_criteria_allowed"), False),
        gate("ROUTE_BUDGET_POLICY_READY", route_budget_policy.get("policy_status") == "ROUTE_BUDGET_ALLOCATION_POLICY_DRAFT_READY", route_budget_policy.get("policy_status"), "ROUTE_BUDGET_ALLOCATION_POLICY_DRAFT_READY"),
        gate("LESSON_MEMORY_PRESENT", len(lessons) >= 1, len(lessons), ">=1"),
        gate("BLOCKLIST_PRESENT", len(blocked_routes) >= 1, len(blocked_routes), ">=1"),
    ]

    gates.extend(safety_flags_all_false(contract, "CONTRACT"))
    gates.extend(safety_flags_all_false(factory_state, "FACTORY_STATE"))
    gates.extend(safety_flags_all_false(reopen_state, "REOPEN_STATE"))
    gates.extend(safety_flags_all_false(reopen_policy, "REOPEN_POLICY"))
    gates.extend(safety_flags_all_false(alpha_accounting, "ALPHA_ACCOUNTING"))
    gates.extend(safety_flags_all_false(alpha_policy, "ALPHA_POLICY"))
    gates.extend(safety_flags_all_false(holdout_registry, "HOLDOUT_REGISTRY"))
    gates.extend(safety_flags_all_false(holdout_access, "HOLDOUT_ACCESS"))

    failed = [row["gate_key"] for row in gates if row["passed"] is not True]
    preflight_pass = len(failed) == 0

    if preflight_pass:
        preflight_status = "RESTRICTED_RESEARCH_CONTRACT_PREFLIGHT_PASS_NON_EXECUTABLE"
        severity = "ATTENTION"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        next_action = "BUILD_RESTRICTED_RESEARCH_BUDGET_ALLOCATION_GATE_NO_EXECUTION"
        reason = "restricted contract proposal passes preflight as non-executable; next step may evaluate explicit budget allocation governance"
        next_module = NEXT_MODULE
        return_code = 0
    else:
        preflight_status = "RESTRICTED_RESEARCH_CONTRACT_PREFLIGHT_FAIL_REVIEW_REQUIRED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_RESTRICTED_CONTRACT_PREFLIGHT_FAILURES_BEFORE_BUDGET"
        reason = f"failed_gate_count={len(failed)}"
        next_module = None
        return_code = 2

    preflight_state = {
        "state_name": "edge_factory_os_restricted_research_contract_preflight_validation_state_v1",
        "created_at_utc": utc_now_iso(),
        "preflight_status": preflight_status,
        "strict_policy_key": STRICT_POLICY_KEY,
        "preflight_pass": preflight_pass,
        "contract_id": contract.get("contract_id"),
        "route_hash": route_hash,
        "route_hash_blocked": route_is_blocked,
        "contract_pre_registered": preflight_pass,
        "contract_non_executable": True,
        "broad_strategy_search_allowed": False,
        "research_execution_allowed_now": False,
        "holdout_access_allowed": False,
        "alpha_budget_requested": alpha_budget_requested,
        "route_budget_requested": route_budget_requested,
        "failed_gate_count": len(failed),
        "failed_gate_keys": failed,
        "next_recommended_research_key": NEXT_RESEARCH_KEY if preflight_pass else None,
        "next_module": next_module,
        **SAFETY_FLAGS,
    }

    next_queue = {
        "queue_name": "edge_factory_os_restricted_research_contract_preflight_next_queue_v1",
        "created_at_utc": utc_now_iso(),
        "queue_status": "RESTRICTED_PREFLIGHT_NEXT_QUEUE_READY" if preflight_pass else "RESTRICTED_PREFLIGHT_QUEUE_BLOCKED_REVIEW_REQUIRED",
        "research_execution_allowed_now": False,
        "budget_allocation_allowed_to_be_considered": preflight_pass,
        "top_next_research_key": NEXT_RESEARCH_KEY if preflight_pass else None,
        "top_next_module": next_module,
        "next_steps": [
            {
                "research_key": NEXT_RESEARCH_KEY,
                "module": NEXT_MODULE,
                "priority": 100,
                "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
                "purpose": "Evaluate whether a tiny explicit research budget may be allocated to this restricted pre-registered contract without enabling candidates or execution yet.",
                "research_execution_allowed_now": False,
                "broad_strategy_search_allowed": False,
                "candidate_generation_allowed": False,
                "family_release_allowed": False,
                "runtime_touch_allowed": False,
                "capital_change_allowed": False,
                "active_paper_allowed": False,
                "live_allowed": False,
                "real_orders_allowed": False,
            }
        ] if preflight_pass else [],
        **SAFETY_FLAGS,
    }

    write_csv(OUT_GATES_CSV, gates)
    write_json(REPO_PREFLIGHT_STATE_JSON, preflight_state)
    write_json(REPO_NEXT_QUEUE_JSON, next_queue)

    result = {
        "validator_name": "edge_factory_os_restricted_research_contract_preflight_validator_v1",
        "created_at_utc": utc_now_iso(),
        "preflight_status": preflight_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "strict_policy_key": STRICT_POLICY_KEY,
        "preflight_pass": preflight_pass,
        "failed_gate_count": len(failed),
        "failed_gate_keys": failed,
        "contract_id": contract.get("contract_id"),
        "route_hash": route_hash,
        "route_hash_blocked": route_is_blocked,
        "contract_pre_registered": preflight_pass,
        "contract_non_executable": True,
        "broad_strategy_search_allowed": False,
        "research_execution_allowed_now": False,
        "holdout_access_allowed": False,
        "alpha_budget_requested": alpha_budget_requested,
        "route_budget_requested": route_budget_requested,
        "next_recommended_research_key": NEXT_RESEARCH_KEY if preflight_pass else None,
        "next_module": next_module,
        "gate_rows": gates,
        "preflight_state": preflight_state,
        "next_queue": next_queue,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "gates_csv": str(OUT_GATES_CSV),
        "preflight_state_json": str(REPO_PREFLIGHT_STATE_JSON),
        "next_queue_json": str(REPO_NEXT_QUEUE_JSON),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text(result))
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
