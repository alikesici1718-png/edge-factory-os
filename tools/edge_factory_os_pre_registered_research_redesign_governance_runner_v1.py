#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Pre-Registered Research Redesign Governance Runner v1

Purpose:
- Verify that anti-overfitting governance is actually active.
- Verify strategy search is locked.
- Verify methodology repair is the only allowed scope.
- Verify promising ideas are preserved but blocked from release.
- Verify pre-registration / holdout / route-budget policies exist and are restrictive.
- Produce governance state and next governance queue.

This runner does NOT:
- search strategies
- generate candidates
- create candidate contracts
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
PLUGIN_DIR = FRAMEWORK_DIR / "plugins"
REGISTRY_DIR = FRAMEWORK_DIR / "registries"
QUEUE_DIR = FRAMEWORK_DIR / "queues"

CONTRACT_JSON = CONTRACT_DIR / "pre_registered_research_redesign_contract_v1.json"
PLUGIN_JSON = PLUGIN_DIR / "pre_registered_research_redesign_plugin_v1.json"

LEDGER_JSON = POLICY_DIR / "global_multiple_testing_ledger_v1.json"
RESEARCH_BUDGET_JSON = POLICY_DIR / "research_budget_policy_v1.json"
PROMISING_VAULT_JSON = POLICY_DIR / "promising_signal_vault_v1.json"
ANTI_OVERFIT_JSON = POLICY_DIR / "anti_overfitting_governance_state_v1.json"
JOINT_NULL_STATE_JSON = POLICY_DIR / "joint_null_distribution_validation_state_v1.json"

HOLDOUT_POLICY_JSON = POLICY_DIR / "holdout_governance_policy_v1.json"
PRE_REG_POLICY_JSON = POLICY_DIR / "pre_registration_policy_v1.json"
ROUTE_BUDGET_POLICY_JSON = POLICY_DIR / "route_budget_allocation_policy_v1.json"
HOLDOUT_REGISTRY_STUB_JSON = REGISTRY_DIR / "untouched_holdout_registry_stub_v1.json"

LESSON_INDEX_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

OUT_DIR = BASE_DIR / "edge_factory_os_pre_registered_research_redesign_governance_runner"
OUT_JSON = OUT_DIR / "pre_registered_research_redesign_governance_runner_latest.json"
OUT_TXT = OUT_DIR / "pre_registered_research_redesign_governance_runner_latest.txt"
OUT_GATES_CSV = OUT_DIR / "pre_registered_research_redesign_governance_gates_latest.csv"

REPO_GOVERNANCE_STATE_JSON = POLICY_DIR / "pre_registered_research_redesign_governance_state_v1.json"
REPO_NEXT_QUEUE_JSON = QUEUE_DIR / "anti_overfitting_governance_next_queue_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD7_02_UNTOUCHED_HOLDOUT_REGISTRY_AND_NESTED_VALIDATION"
NEXT_MODULE = "edge_factory_os_untouched_holdout_registry_builder_v1.py"

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


def safety_flags_all_false(obj: Dict[str, Any], label: str) -> List[Dict[str, Any]]:
    rows = []
    for key, required in SAFETY_FLAGS.items():
        observed = obj.get(key, False)
        rows.append({
            "gate_key": f"{label}_{key.upper()}_FALSE",
            "passed": observed is False,
            "observed": observed,
            "required": False,
        })
    return rows


def gate(key: str, passed: bool, observed: Any, required: Any) -> Dict[str, Any]:
    return {
        "gate_key": key,
        "passed": bool(passed),
        "observed": observed,
        "required": required,
    }


def build_text(result: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS PRE-REGISTERED RESEARCH REDESIGN GOVERNANCE RUNNER v1")
    lines.append("=" * 100)

    for key in [
        "runner_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "governance_gate_pass",
        "governance_gate_fail_count",
        "failed_gate_keys",
        "strategy_search_allowed_now",
        "methodology_repair_allowed_now",
        "promising_vault_preserved",
        "pre_registration_enforced",
        "holdout_governance_enforced",
        "route_budget_enforced",
        "global_ledger_enforced",
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
    lines.append("FAILED GATES")
    lines.append("-" * 100)
    for item in result.get("failed_gate_keys", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("CORE DECISION")
    lines.append("-" * 100)
    lines.append("Strategy search remains locked.")
    lines.append("Methodology repair remains allowed.")
    lines.append("Promising ideas remain preserved, not deleted.")
    lines.append("No candidate/family/runtime/capital/active-paper/live/real-order action is allowed.")

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
        "repo_governance_state_json",
        "repo_next_queue_json",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS PRE-REGISTERED RESEARCH REDESIGN GOVERNANCE RUNNER v1")
    print("=" * 100)
    print(f"runner_status: {result.get('runner_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"governance_gate_pass: {result.get('governance_gate_pass')}")
    print(f"governance_gate_fail_count: {result.get('governance_gate_fail_count')}")
    print(f"failed_gate_keys: {result.get('failed_gate_keys')}")
    print(f"strategy_search_allowed_now: {result.get('strategy_search_allowed_now')}")
    print(f"methodology_repair_allowed_now: {result.get('methodology_repair_allowed_now')}")
    print(f"promising_vault_preserved: {result.get('promising_vault_preserved')}")
    print(f"pre_registration_enforced: {result.get('pre_registration_enforced')}")
    print(f"holdout_governance_enforced: {result.get('holdout_governance_enforced')}")
    print(f"route_budget_enforced: {result.get('route_budget_enforced')}")
    print(f"global_ledger_enforced: {result.get('global_ledger_enforced')}")
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
    print(f"STATE: {result.get('repo_governance_state_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    contract = load_json(CONTRACT_JSON, {})
    plugin = load_json(PLUGIN_JSON, {})
    ledger = load_json(LEDGER_JSON, {})
    budget = load_json(RESEARCH_BUDGET_JSON, {})
    vault = load_json(PROMISING_VAULT_JSON, {})
    anti = load_json(ANTI_OVERFIT_JSON, {})
    joint = load_json(JOINT_NULL_STATE_JSON, {})
    holdout_policy = load_json(HOLDOUT_POLICY_JSON, {})
    pre_reg_policy = load_json(PRE_REG_POLICY_JSON, {})
    route_budget_policy = load_json(ROUTE_BUDGET_POLICY_JSON, {})
    holdout_stub = load_json(HOLDOUT_REGISTRY_STUB_JSON, {})
    lessons = extract_list(load_json(LESSON_INDEX_JSON, {}), "lessons")
    blocked = extract_list(load_json(BLOCKLIST_JSON, {}), "blocked_routes")
    vault_items = extract_list(vault, "vault_items")

    gates: List[Dict[str, Any]] = []

    gates.extend([
        gate("CONTRACT_READY", contract.get("contract_status") == "PRE_REGISTERED_RESEARCH_REDESIGN_CONTRACT_READY", contract.get("contract_status"), "PRE_REGISTERED_RESEARCH_REDESIGN_CONTRACT_READY"),
        gate("PLUGIN_READY", plugin.get("plugin_key") == "PRE_REGISTERED_RESEARCH_REDESIGN_PLUGIN_V1", plugin.get("plugin_key"), "PRE_REGISTERED_RESEARCH_REDESIGN_PLUGIN_V1"),
        gate("STRATEGY_SEARCH_LOCKED_IN_CONTRACT", contract.get("strategy_search_allowed_now") is False, contract.get("strategy_search_allowed_now"), False),
        gate("METHODOLOGY_REPAIR_ALLOWED_IN_CONTRACT", contract.get("methodology_repair_allowed_now") is True, contract.get("methodology_repair_allowed_now"), True),
        gate("GLOBAL_LEDGER_ACTIVE", ledger.get("ledger_status") == "GLOBAL_MULTIPLE_TESTING_LEDGER_ACTIVE_RESEARCH_LOCKED", ledger.get("ledger_status"), "GLOBAL_MULTIPLE_TESTING_LEDGER_ACTIVE_RESEARCH_LOCKED"),
        gate("RESEARCH_BUDGET_ACTIVE", budget.get("policy_status") == "RESEARCH_BUDGET_POLICY_ACTIVE_METHODOLOGY_ONLY", budget.get("policy_status"), "RESEARCH_BUDGET_POLICY_ACTIVE_METHODOLOGY_ONLY"),
        gate("BUDGET_STRATEGY_SEARCH_LOCKED", budget.get("research_budget_status") == "STRATEGY_SEARCH_BUDGET_LOCKED_UNTIL_GOVERNANCE_REPAIR", budget.get("research_budget_status"), "STRATEGY_SEARCH_BUDGET_LOCKED_UNTIL_GOVERNANCE_REPAIR"),
        gate("PROMISING_VAULT_ACTIVE", vault.get("vault_status") == "PROMISING_SIGNAL_VAULT_ACTIVE_RELEASE_BLOCKED", vault.get("vault_status"), "PROMISING_SIGNAL_VAULT_ACTIVE_RELEASE_BLOCKED"),
        gate("PROMISING_VAULT_HAS_ITEM", len(vault_items) >= 1, len(vault_items), ">=1"),
        gate("ANTI_OVERFITTING_STATE_ACTIVE", anti.get("state_status") == "ANTI_OVERFITTING_GOVERNANCE_ACTIVE_RESEARCH_REPAIR_REQUIRED", anti.get("state_status"), "ANTI_OVERFITTING_GOVERNANCE_ACTIVE_RESEARCH_REPAIR_REQUIRED"),
        gate("JOINT_NULL_FAILURE_CONSUMED", joint.get("joint_null_policy_gate_pass") is False, joint.get("joint_null_policy_gate_pass"), False),
        gate("LESSON_MEMORY_PRESENT", len(lessons) >= 1, len(lessons), ">=1"),
        gate("BLOCKLIST_PRESENT", len(blocked) >= 1, len(blocked), ">=1"),
        gate("HOLDOUT_POLICY_READY", holdout_policy.get("policy_status") == "HOLDOUT_GOVERNANCE_POLICY_DRAFT_READY", holdout_policy.get("policy_status"), "HOLDOUT_GOVERNANCE_POLICY_DRAFT_READY"),
        gate("HOLDOUT_PEEKING_FORBIDDEN", holdout_policy.get("holdout_peeking_allowed") is False, holdout_policy.get("holdout_peeking_allowed"), False),
        gate("HOLDOUT_REUSE_FORBIDDEN", holdout_policy.get("holdout_reuse_allowed") is False, holdout_policy.get("holdout_reuse_allowed"), False),
        gate("PRE_REG_POLICY_READY", pre_reg_policy.get("policy_status") == "PRE_REGISTRATION_POLICY_DRAFT_READY", pre_reg_policy.get("policy_status"), "PRE_REGISTRATION_POLICY_DRAFT_READY"),
        gate("PRE_REG_REQUIRED", pre_reg_policy.get("all_future_research_must_be_pre_registered") is True, pre_reg_policy.get("all_future_research_must_be_pre_registered"), True),
        gate("POST_HOC_SUCCESS_CRITERIA_FORBIDDEN", pre_reg_policy.get("post_hoc_success_criteria_allowed") is False, pre_reg_policy.get("post_hoc_success_criteria_allowed"), False),
        gate("CONTRACT_MUTATION_INVALIDATES_ROUTE", pre_reg_policy.get("contract_mutation_after_start_invalidates_route") is True, pre_reg_policy.get("contract_mutation_after_start_invalidates_route"), True),
        gate("ROUTE_BUDGET_POLICY_READY", route_budget_policy.get("policy_status") == "ROUTE_BUDGET_ALLOCATION_POLICY_DRAFT_READY", route_budget_policy.get("policy_status"), "ROUTE_BUDGET_ALLOCATION_POLICY_DRAFT_READY"),
        gate("NEW_STRATEGY_ROUTE_BUDGET_ZERO", int(route_budget_policy.get("new_strategy_route_budget_now", -1)) == 0, route_budget_policy.get("new_strategy_route_budget_now"), 0),
        gate("POST_HOC_BUDGET_FORBIDDEN", route_budget_policy.get("post_hoc_budget_allocation_allowed") is False, route_budget_policy.get("post_hoc_budget_allocation_allowed"), False),
        gate("UNTOUCHED_HOLDOUT_STUB_READY", holdout_stub.get("registry_status") == "UNTOUCHED_HOLDOUT_REGISTRY_STUB_READY_NOT_POPULATED", holdout_stub.get("registry_status"), "UNTOUCHED_HOLDOUT_REGISTRY_STUB_READY_NOT_POPULATED"),
        gate("HOLDOUT_NOT_SELECTED_YET", holdout_stub.get("holdout_selected") is False, holdout_stub.get("holdout_selected"), False),
        gate("HOLDOUT_NOT_PEEKED", holdout_stub.get("holdout_peeked") is False, holdout_stub.get("holdout_peeked"), False),
        gate("HOLDOUT_NOT_USABLE_NOW", holdout_stub.get("holdout_usable_now") is False, holdout_stub.get("holdout_usable_now"), False),
    ])

    gates.extend(safety_flags_all_false(contract, "CONTRACT"))
    gates.extend(safety_flags_all_false(plugin, "PLUGIN"))
    gates.extend(safety_flags_all_false(budget, "BUDGET"))
    gates.extend(safety_flags_all_false(anti, "ANTI_OVERFIT"))
    gates.extend(safety_flags_all_false(holdout_policy, "HOLDOUT_POLICY"))
    gates.extend(safety_flags_all_false(pre_reg_policy, "PRE_REG_POLICY"))
    gates.extend(safety_flags_all_false(route_budget_policy, "ROUTE_BUDGET_POLICY"))

    failed = [row["gate_key"] for row in gates if row["passed"] is not True]
    governance_pass = len(failed) == 0

    if governance_pass:
        runner_status = "PRE_REGISTERED_RESEARCH_REDESIGN_GOVERNANCE_RUNNER_PASS_STRATEGY_SEARCH_LOCKED"
        severity = "ATTENTION"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        next_action = "BUILD_UNTOUCHED_HOLDOUT_REGISTRY_AND_NESTED_VALIDATION_NO_STRATEGY_SEARCH"
        reason = "governance gates pass; strategy search remains locked; methodology repair may proceed"
        next_module = NEXT_MODULE
    else:
        runner_status = "PRE_REGISTERED_RESEARCH_REDESIGN_GOVERNANCE_RUNNER_FAIL_REVIEW_REQUIRED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_GOVERNANCE_GATES_BEFORE_ANY_RESEARCH"
        reason = f"failed_gate_count={len(failed)}"
        next_module = None

    governance_state = {
        "state_name": "edge_factory_os_pre_registered_research_redesign_governance_state_v1",
        "created_at_utc": utc_now_iso(),
        "state_status": runner_status,
        "strict_policy_key": STRICT_POLICY_KEY,
        "governance_gate_pass": governance_pass,
        "governance_gate_fail_count": len(failed),
        "failed_gate_keys": failed,
        "strategy_search_allowed_now": False,
        "methodology_repair_allowed_now": True,
        "promising_vault_preserved": len(vault_items) >= 1,
        "pre_registration_enforced": True,
        "holdout_governance_enforced": True,
        "route_budget_enforced": True,
        "global_ledger_enforced": True,
        "next_recommended_research_key": NEXT_RESEARCH_KEY if governance_pass else None,
        "next_module": next_module,
        **SAFETY_FLAGS,
    }

    next_queue = {
        "queue_name": "edge_factory_os_anti_overfitting_governance_next_queue_v1",
        "created_at_utc": utc_now_iso(),
        "queue_status": "ANTI_OVERFITTING_GOVERNANCE_NEXT_QUEUE_READY" if governance_pass else "ANTI_OVERFITTING_GOVERNANCE_QUEUE_BLOCKED_REVIEW_REQUIRED",
        "strategy_search_allowed_now": False,
        "methodology_repair_allowed_now": governance_pass,
        "top_next_research_key": NEXT_RESEARCH_KEY if governance_pass else None,
        "top_next_module": next_module,
        "next_steps": [
            {
                "research_key": NEXT_RESEARCH_KEY,
                "module": NEXT_MODULE,
                "priority": 100,
                "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
                "purpose": "Create real untouched holdout governance and nested validation registry without exposing or using holdout for strategy search.",
                "strategy_search_allowed": False,
                "candidate_generation_allowed": False,
                "family_release_allowed": False,
                "runtime_touch_allowed": False,
                "capital_change_allowed": False,
                "active_paper_allowed": False,
                "live_allowed": False,
                "real_orders_allowed": False,
            }
        ] if governance_pass else [],
        **SAFETY_FLAGS,
    }

    write_csv(OUT_GATES_CSV, gates)
    write_json(REPO_GOVERNANCE_STATE_JSON, governance_state)
    write_json(REPO_NEXT_QUEUE_JSON, next_queue)

    result = {
        "runner_name": "edge_factory_os_pre_registered_research_redesign_governance_runner_v1",
        "created_at_utc": utc_now_iso(),
        "runner_status": runner_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "strict_policy_key": STRICT_POLICY_KEY,
        "governance_gate_pass": governance_pass,
        "governance_gate_fail_count": len(failed),
        "failed_gate_keys": failed,
        "strategy_search_allowed_now": False,
        "methodology_repair_allowed_now": governance_pass,
        "promising_vault_preserved": len(vault_items) >= 1,
        "pre_registration_enforced": True,
        "holdout_governance_enforced": True,
        "route_budget_enforced": True,
        "global_ledger_enforced": True,
        "lesson_count": len(lessons),
        "blocked_route_count": len(blocked),
        "vault_item_count": len(vault_items),
        "next_recommended_research_key": NEXT_RESEARCH_KEY if governance_pass else None,
        "next_module": next_module,
        "gate_rows": gates,
        "governance_state": governance_state,
        "next_queue": next_queue,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "gates_csv": str(OUT_GATES_CSV),
        "repo_governance_state_json": str(REPO_GOVERNANCE_STATE_JSON),
        "repo_next_queue_json": str(REPO_NEXT_QUEUE_JSON),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text(result))
    print_summary(result)

    return 0 if governance_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
