#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Restricted Research Budget Allocation Gate v1

Purpose:
- Consume restricted research contract preflight validation.
- Consume global alpha spending policy and route-family alpha accounting.
- Propose a tiny explicit research-only budget for the restricted pre-registered contract.
- Keep research execution blocked until a separate execution gate.
- Keep broad strategy search, candidate generation, family release, runtime touch, capital,
  active paper, live trading, and real orders blocked.

This gate does NOT:
- run research
- execute any strategy
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
PREFLIGHT_STATE_JSON = POLICY_DIR / "restricted_research_contract_preflight_validation_state_v1.json"
PREFLIGHT_NEXT_QUEUE_JSON = QUEUE_DIR / "restricted_research_contract_preflight_next_queue_v1.json"

GLOBAL_ALPHA_ACCOUNTING_JSON = POLICY_DIR / "global_route_family_alpha_accounting_v1.json"
GLOBAL_ALPHA_POLICY_JSON = POLICY_DIR / "global_alpha_spending_policy_v1.json"
GLOBAL_LEDGER_JSON = POLICY_DIR / "global_multiple_testing_ledger_v1.json"
RESEARCH_BUDGET_POLICY_JSON = POLICY_DIR / "research_budget_policy_v1.json"
PROMISING_VAULT_JSON = POLICY_DIR / "promising_signal_vault_v1.json"

UNTOUCHED_HOLDOUT_REGISTRY_JSON = REGISTRY_DIR / "untouched_holdout_registry_v1.json"
NESTED_VALIDATION_POLICY_JSON = POLICY_DIR / "nested_validation_policy_v1.json"
HOLDOUT_ACCESS_CONTROL_JSON = POLICY_DIR / "holdout_access_control_policy_v1.json"
PRE_REG_POLICY_JSON = POLICY_DIR / "pre_registration_policy_v1.json"
ROUTE_BUDGET_POLICY_JSON = POLICY_DIR / "route_budget_allocation_policy_v1.json"

LESSON_INDEX_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

OUT_DIR = BASE_DIR / "edge_factory_os_restricted_research_budget_allocation_gate"
OUT_JSON = OUT_DIR / "restricted_research_budget_allocation_gate_latest.json"
OUT_TXT = OUT_DIR / "restricted_research_budget_allocation_gate_latest.txt"
OUT_GATES_CSV = OUT_DIR / "restricted_research_budget_allocation_gates_latest.csv"

REPO_BUDGET_ALLOCATION_JSON = POLICY_DIR / "restricted_research_budget_allocation_v1.json"
REPO_BUDGET_GATE_STATE_JSON = POLICY_DIR / "restricted_research_budget_allocation_gate_state_v1.json"
REPO_NEXT_QUEUE_JSON = QUEUE_DIR / "restricted_research_budget_allocation_next_queue_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD7_08_RESTRICTED_RESEARCH_EXECUTION_GATE"
NEXT_MODULE = "edge_factory_os_restricted_research_execution_gate_v1.py"

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


def family_row_for_contract(alpha_accounting: Dict[str, Any], route_family: str) -> Dict[str, Any]:
    rows = alpha_accounting.get("route_family_rows", [])
    if not isinstance(rows, list):
        return {}
    for row in rows:
        if isinstance(row, dict) and str(row.get("route_family")) == route_family:
            return row
    return {}


def build_text(result: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS RESTRICTED RESEARCH BUDGET ALLOCATION GATE v1")
    lines.append("=" * 100)

    for key in [
        "budget_gate_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "budget_gate_pass",
        "failed_gate_count",
        "failed_gate_keys",
        "contract_id",
        "route_hash",
        "route_family",
        "proposed_alpha_budget",
        "proposed_route_budget",
        "diagnostic_alpha_after_pressure",
        "research_execution_allowed_now",
        "budget_allocation_created",
        "broad_strategy_search_allowed",
        "holdout_access_allowed",
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
    lines.append("A tiny explicit research-only budget may be proposed if all gates pass.")
    lines.append("This does not execute research.")
    lines.append("This does not authorize candidates, family release, runtime, capital, active paper, live, or real orders.")
    lines.append("A separate execution gate must pass before any runner can run.")

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
        "budget_allocation_json",
        "budget_gate_state_json",
        "next_queue_json",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS RESTRICTED RESEARCH BUDGET ALLOCATION GATE v1")
    print("=" * 100)
    print(f"budget_gate_status: {result.get('budget_gate_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"budget_gate_pass: {result.get('budget_gate_pass')}")
    print(f"failed_gate_count: {result.get('failed_gate_count')}")
    print(f"failed_gate_keys: {result.get('failed_gate_keys')}")
    print(f"contract_id: {result.get('contract_id')}")
    print(f"route_hash: {result.get('route_hash')}")
    print(f"route_family: {result.get('route_family')}")
    print(f"proposed_alpha_budget: {result.get('proposed_alpha_budget')}")
    print(f"proposed_route_budget: {result.get('proposed_route_budget')}")
    print(f"diagnostic_alpha_after_pressure: {result.get('diagnostic_alpha_after_pressure')}")
    print(f"research_execution_allowed_now: {result.get('research_execution_allowed_now')}")
    print(f"budget_allocation_created: {result.get('budget_allocation_created')}")
    print(f"broad_strategy_search_allowed: {result.get('broad_strategy_search_allowed')}")
    print(f"holdout_access_allowed: {result.get('holdout_access_allowed')}")
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
    print(f"BUDGET: {result.get('budget_allocation_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    contract = load_json(PROPOSED_CONTRACT_JSON, {})
    preflight = load_json(PREFLIGHT_STATE_JSON, {})
    preflight_queue = load_json(PREFLIGHT_NEXT_QUEUE_JSON, {})
    alpha_accounting = load_json(GLOBAL_ALPHA_ACCOUNTING_JSON, {})
    alpha_policy = load_json(GLOBAL_ALPHA_POLICY_JSON, {})
    ledger = load_json(GLOBAL_LEDGER_JSON, {})
    research_budget_policy = load_json(RESEARCH_BUDGET_POLICY_JSON, {})
    vault = load_json(PROMISING_VAULT_JSON, {})
    holdout_registry = load_json(UNTOUCHED_HOLDOUT_REGISTRY_JSON, {})
    nested_policy = load_json(NESTED_VALIDATION_POLICY_JSON, {})
    holdout_access = load_json(HOLDOUT_ACCESS_CONTROL_JSON, {})
    pre_reg_policy = load_json(PRE_REG_POLICY_JSON, {})
    route_budget_policy = load_json(ROUTE_BUDGET_POLICY_JSON, {})

    lessons = extract_list(load_json(LESSON_INDEX_JSON, {}), "lessons")
    blocked_routes = extract_list(load_json(BLOCKLIST_JSON, {}), "blocked_routes")
    vault_items = extract_list(vault, "vault_items")

    contract_id = contract.get("contract_id")
    route_hash = str(contract.get("route_hash") or "")
    route_family = str(contract.get("route_family") or "UNKNOWN")
    route_is_blocked = route_hash_blocked(blocked_routes, route_hash)

    family_row = family_row_for_contract(alpha_accounting, route_family)

    diagnostic_alpha_after_pressure = float(
        alpha_accounting.get("diagnostic_alpha_after_pressure")
        or ledger.get("global_testing_pressure", {}).get("diagnostic_alpha_after_pressure")
        or 0.0
    )

    # Tiny research-only budget. This is a proposal, not execution permission.
    # It deliberately uses the already pressure-adjusted diagnostic alpha.
    proposed_alpha_budget = diagnostic_alpha_after_pressure
    proposed_route_budget = 1

    current_total_strategy_alpha_budget = float(alpha_policy.get("current_total_strategy_alpha_budget", 0.0))
    current_total_strategy_route_budget = int(alpha_policy.get("current_total_strategy_route_budget", 0))

    gates: List[Dict[str, Any]] = [
        gate("PREFLIGHT_PASS", preflight.get("preflight_pass") is True, preflight.get("preflight_pass"), True),
        gate("PREFLIGHT_NON_EXECUTABLE", preflight.get("contract_non_executable") is True and preflight.get("research_execution_allowed_now") is False, {"contract_non_executable": preflight.get("contract_non_executable"), "research_execution_allowed_now": preflight.get("research_execution_allowed_now")}, "True/False"),
        gate("PREFLIGHT_QUEUE_READY", preflight_queue.get("queue_status") == "RESTRICTED_PREFLIGHT_NEXT_QUEUE_READY", preflight_queue.get("queue_status"), "RESTRICTED_PREFLIGHT_NEXT_QUEUE_READY"),
        gate("CONTRACT_READY_NOT_EXECUTABLE", contract.get("contract_status") == "RESTRICTED_RESEARCH_CONTRACT_PROPOSAL_READY_NOT_EXECUTABLE", contract.get("contract_status"), "RESTRICTED_RESEARCH_CONTRACT_PROPOSAL_READY_NOT_EXECUTABLE"),
        gate("CONTRACT_ID_MATCHES_PREFLIGHT", contract_id == preflight.get("contract_id"), {"contract": contract_id, "preflight": preflight.get("contract_id")}, "match"),
        gate("ROUTE_HASH_MATCHES_PREFLIGHT", route_hash == preflight.get("route_hash"), {"contract": route_hash, "preflight": preflight.get("route_hash")}, "match"),
        gate("ROUTE_HASH_NOT_BLOCKED", not route_is_blocked, route_is_blocked, False),
        gate("ROUTE_FAMILY_PRESENT", route_family not in {"", "UNKNOWN"}, route_family, "known route family"),
        gate("FAMILY_ROW_PRESENT", bool(family_row), family_row.get("route_family"), route_family),
        gate("BROAD_STRATEGY_SEARCH_BLOCKED", contract.get("broad_strategy_search_allowed") is False and preflight.get("broad_strategy_search_allowed") is False, {"contract": contract.get("broad_strategy_search_allowed"), "preflight": preflight.get("broad_strategy_search_allowed")}, "all False"),
        gate("RESEARCH_EXECUTION_STILL_BLOCKED", contract.get("research_execution_allowed_now") is False and preflight.get("research_execution_allowed_now") is False, {"contract": contract.get("research_execution_allowed_now"), "preflight": preflight.get("research_execution_allowed_now")}, "all False"),
        gate("HOLDOUT_ACCESS_STILL_FORBIDDEN", contract.get("holdout_access_allowed") is False and preflight.get("holdout_access_allowed") is False and holdout_access.get("holdout_access_allowed_now") is False, {"contract": contract.get("holdout_access_allowed"), "preflight": preflight.get("holdout_access_allowed"), "policy": holdout_access.get("holdout_access_allowed_now")}, "all False"),
        gate("HOLDOUT_NOT_SELECTED", holdout_registry.get("holdout_selected") is False, holdout_registry.get("holdout_selected"), False),
        gate("HOLDOUT_NOT_PEEKED", holdout_registry.get("holdout_peeked") is False, holdout_registry.get("holdout_peeked"), False),
        gate("HOLDOUT_NOT_USABLE_NOW", holdout_registry.get("holdout_usable_now") is False, holdout_registry.get("holdout_usable_now"), False),
        gate("NESTED_VALIDATION_READY", nested_policy.get("policy_status") == "NESTED_VALIDATION_POLICY_READY_STRATEGY_SEARCH_LOCKED", nested_policy.get("policy_status"), "NESTED_VALIDATION_POLICY_READY_STRATEGY_SEARCH_LOCKED"),
        gate("PRE_REGISTRATION_READY", pre_reg_policy.get("policy_status") == "PRE_REGISTRATION_POLICY_DRAFT_READY", pre_reg_policy.get("policy_status"), "PRE_REGISTRATION_POLICY_DRAFT_READY"),
        gate("ROUTE_BUDGET_POLICY_READY", route_budget_policy.get("policy_status") == "ROUTE_BUDGET_ALLOCATION_POLICY_DRAFT_READY", route_budget_policy.get("policy_status"), "ROUTE_BUDGET_ALLOCATION_POLICY_DRAFT_READY"),
        gate("GLOBAL_ALPHA_ACCOUNTING_PASS", alpha_accounting.get("global_alpha_accounting_pass") is True, alpha_accounting.get("global_alpha_accounting_pass"), True),
        gate("GLOBAL_ALPHA_POLICY_ACTIVE", alpha_policy.get("policy_status") == "GLOBAL_ALPHA_SPENDING_POLICY_ACTIVE_ZERO_STRATEGY_BUDGET", alpha_policy.get("policy_status"), "GLOBAL_ALPHA_SPENDING_POLICY_ACTIVE_ZERO_STRATEGY_BUDGET"),
        gate("CURRENT_TOTAL_ALPHA_BUDGET_ZERO_BEFORE_ALLOCATION", current_total_strategy_alpha_budget == 0.0, current_total_strategy_alpha_budget, 0.0),
        gate("CURRENT_TOTAL_ROUTE_BUDGET_ZERO_BEFORE_ALLOCATION", current_total_strategy_route_budget == 0, current_total_strategy_route_budget, 0),
        gate("PROPOSED_ALPHA_BUDGET_POSITIVE_TINY", proposed_alpha_budget > 0.0, proposed_alpha_budget, ">0"),
        gate("PROPOSED_ALPHA_BUDGET_NOT_GREATER_THAN_PRESSURE_ALPHA", proposed_alpha_budget <= diagnostic_alpha_after_pressure, {"proposed": proposed_alpha_budget, "diagnostic": diagnostic_alpha_after_pressure}, "<= diagnostic alpha"),
        gate("PROPOSED_ROUTE_BUDGET_ONE", proposed_route_budget == 1, proposed_route_budget, 1),
        gate("VAULT_ACTIVE", vault.get("vault_status") == "PROMISING_SIGNAL_VAULT_ACTIVE_RELEASE_BLOCKED" and len(vault_items) >= 1, {"vault_status": vault.get("vault_status"), "vault_items": len(vault_items)}, "active and >=1"),
        gate("LESSONS_PRESENT", len(lessons) >= 1, len(lessons), ">=1"),
        gate("BLOCKLIST_PRESENT", len(blocked_routes) >= 1, len(blocked_routes), ">=1"),
        gate("RESEARCH_BUDGET_POLICY_ACTIVE", research_budget_policy.get("policy_status") == "RESEARCH_BUDGET_POLICY_ACTIVE_METHODOLOGY_ONLY", research_budget_policy.get("policy_status"), "RESEARCH_BUDGET_POLICY_ACTIVE_METHODOLOGY_ONLY"),
    ]

    gates.extend(safety_flags_all_false(contract, "CONTRACT"))
    gates.extend(safety_flags_all_false(preflight, "PREFLIGHT"))
    gates.extend(safety_flags_all_false(alpha_accounting, "ALPHA_ACCOUNTING"))
    gates.extend(safety_flags_all_false(alpha_policy, "ALPHA_POLICY"))
    gates.extend(safety_flags_all_false(holdout_registry, "HOLDOUT_REGISTRY"))
    gates.extend(safety_flags_all_false(holdout_access, "HOLDOUT_ACCESS"))

    failed = [row["gate_key"] for row in gates if row["passed"] is not True]
    budget_gate_pass = len(failed) == 0

    if budget_gate_pass:
        budget_gate_status = "RESTRICTED_RESEARCH_BUDGET_ALLOCATION_GATE_PASS_EXECUTION_STILL_BLOCKED"
        severity = "ATTENTION"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        next_action = "BUILD_RESTRICTED_RESEARCH_EXECUTION_GATE_NO_CANDIDATES_NO_RELEASE"
        reason = "tiny research-only budget proposal is valid; research execution remains blocked until execution gate"
        next_module = NEXT_MODULE
        return_code = 0
    else:
        budget_gate_status = "RESTRICTED_RESEARCH_BUDGET_ALLOCATION_GATE_FAIL_REVIEW_REQUIRED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_BUDGET_ALLOCATION_GATE_FAILURES_BEFORE_EXECUTION_GATE"
        reason = f"failed_gate_count={len(failed)}"
        next_module = None
        return_code = 2

    budget_allocation = {
        "allocation_name": "edge_factory_os_restricted_research_budget_allocation_v1",
        "created_at_utc": utc_now_iso(),
        "allocation_status": "RESTRICTED_RESEARCH_BUDGET_ALLOCATION_PROPOSED_EXECUTION_BLOCKED" if budget_gate_pass else "RESTRICTED_RESEARCH_BUDGET_ALLOCATION_BLOCKED",
        "strict_policy_key": STRICT_POLICY_KEY,
        "contract_id": contract_id,
        "route_hash": route_hash,
        "route_family": route_family,
        "budget_gate_pass": budget_gate_pass,
        "proposed_alpha_budget": proposed_alpha_budget if budget_gate_pass else 0.0,
        "proposed_route_budget": proposed_route_budget if budget_gate_pass else 0,
        "diagnostic_alpha_after_pressure": diagnostic_alpha_after_pressure,
        "budget_type": "RESEARCH_ONLY_NOT_TRADING",
        "research_execution_allowed_now": False,
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
        "execution_gate_required_before_any_runner": True,
        "runner_allowed_now": False,
        "notes": [
            "Budget is for a future restricted research execution gate only.",
            "This is not capital and not trading exposure.",
            "This does not permit active paper, live trading, candidates, or family release.",
            "Final holdout remains unselected/unpeeked/unusable.",
        ],
        **SAFETY_FLAGS,
    }

    budget_gate_state = {
        "state_name": "edge_factory_os_restricted_research_budget_allocation_gate_state_v1",
        "created_at_utc": utc_now_iso(),
        "budget_gate_status": budget_gate_status,
        "budget_gate_pass": budget_gate_pass,
        "contract_id": contract_id,
        "route_hash": route_hash,
        "route_family": route_family,
        "proposed_alpha_budget": proposed_alpha_budget if budget_gate_pass else 0.0,
        "proposed_route_budget": proposed_route_budget if budget_gate_pass else 0,
        "research_execution_allowed_now": False,
        "budget_allocation_created": budget_gate_pass,
        "failed_gate_count": len(failed),
        "failed_gate_keys": failed,
        "next_recommended_research_key": NEXT_RESEARCH_KEY if budget_gate_pass else None,
        "next_module": next_module,
        **SAFETY_FLAGS,
    }

    next_queue = {
        "queue_name": "edge_factory_os_restricted_research_budget_allocation_next_queue_v1",
        "created_at_utc": utc_now_iso(),
        "queue_status": "RESTRICTED_RESEARCH_BUDGET_ALLOCATION_NEXT_QUEUE_READY" if budget_gate_pass else "RESTRICTED_RESEARCH_BUDGET_ALLOCATION_QUEUE_BLOCKED_REVIEW_REQUIRED",
        "research_execution_allowed_now": False,
        "budget_allocation_created": budget_gate_pass,
        "top_next_research_key": NEXT_RESEARCH_KEY if budget_gate_pass else None,
        "top_next_module": next_module,
        "next_steps": [
            {
                "research_key": NEXT_RESEARCH_KEY,
                "module": NEXT_MODULE,
                "priority": 100,
                "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
                "purpose": "Decide whether the restricted pre-registered research runner may be built/executed under tiny research-only budget, without candidates or release.",
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
        ] if budget_gate_pass else [],
        **SAFETY_FLAGS,
    }

    write_csv(OUT_GATES_CSV, gates)
    write_json(REPO_BUDGET_ALLOCATION_JSON, budget_allocation)
    write_json(REPO_BUDGET_GATE_STATE_JSON, budget_gate_state)
    write_json(REPO_NEXT_QUEUE_JSON, next_queue)

    result = {
        "gate_name": "edge_factory_os_restricted_research_budget_allocation_gate_v1",
        "created_at_utc": utc_now_iso(),
        "budget_gate_status": budget_gate_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "budget_gate_pass": budget_gate_pass,
        "failed_gate_count": len(failed),
        "failed_gate_keys": failed,
        "contract_id": contract_id,
        "route_hash": route_hash,
        "route_family": route_family,
        "proposed_alpha_budget": proposed_alpha_budget if budget_gate_pass else 0.0,
        "proposed_route_budget": proposed_route_budget if budget_gate_pass else 0,
        "diagnostic_alpha_after_pressure": diagnostic_alpha_after_pressure,
        "research_execution_allowed_now": False,
        "budget_allocation_created": budget_gate_pass,
        "broad_strategy_search_allowed": False,
        "holdout_access_allowed": False,
        "next_recommended_research_key": NEXT_RESEARCH_KEY if budget_gate_pass else None,
        "next_module": next_module,
        "gate_rows": gates,
        "budget_allocation": budget_allocation,
        "budget_gate_state": budget_gate_state,
        "next_queue": next_queue,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "gates_csv": str(OUT_GATES_CSV),
        "budget_allocation_json": str(REPO_BUDGET_ALLOCATION_JSON),
        "budget_gate_state_json": str(REPO_BUDGET_GATE_STATE_JSON),
        "next_queue_json": str(REPO_NEXT_QUEUE_JSON),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text(result))
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
