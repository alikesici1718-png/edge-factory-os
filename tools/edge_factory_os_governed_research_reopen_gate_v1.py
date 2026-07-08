#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Governed Research Reopen Gate v1

Purpose:
- Consume the full anti-overfitting governance chain.
- Decide whether research may reopen under strict governance.
- Keep broad/free strategy search blocked.
- Permit only a narrow future pre-registered research contract template if all governance gates pass.
- Keep candidate/family/runtime/capital/active-paper/live/real-order actions blocked.

This gate does NOT:
- run strategy research
- allocate real trading capital
- generate candidates
- create candidate trading contracts
- release families
- touch runtime
- expose or use final holdout
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
REGISTRY_DIR = FRAMEWORK_DIR / "registries"
QUEUE_DIR = FRAMEWORK_DIR / "queues"
CONTRACT_DIR = FRAMEWORK_DIR / "contracts"

LEDGER_JSON = POLICY_DIR / "global_multiple_testing_ledger_v1.json"
RESEARCH_BUDGET_JSON = POLICY_DIR / "research_budget_policy_v1.json"
PROMISING_VAULT_JSON = POLICY_DIR / "promising_signal_vault_v1.json"
ANTI_OVERFIT_JSON = POLICY_DIR / "anti_overfitting_governance_state_v1.json"
PRE_REG_GOVERNANCE_JSON = POLICY_DIR / "pre_registered_research_redesign_governance_state_v1.json"
NESTED_VALIDATION_JSON = POLICY_DIR / "nested_validation_policy_v1.json"
HOLDOUT_ACCESS_JSON = POLICY_DIR / "holdout_access_control_policy_v1.json"
HOLDOUT_COMMITMENT_JSON = POLICY_DIR / "holdout_commitment_protocol_v1.json"
UNTOUCHED_HOLDOUT_REGISTRY_JSON = REGISTRY_DIR / "untouched_holdout_registry_v1.json"
GLOBAL_ALPHA_ACCOUNTING_JSON = POLICY_DIR / "global_route_family_alpha_accounting_v1.json"
GLOBAL_ALPHA_POLICY_JSON = POLICY_DIR / "global_alpha_spending_policy_v1.json"
GLOBAL_ALPHA_NEXT_QUEUE_JSON = QUEUE_DIR / "global_alpha_accounting_next_queue_v1.json"

LESSON_INDEX_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

OUT_DIR = BASE_DIR / "edge_factory_os_governed_research_reopen_gate"
OUT_JSON = OUT_DIR / "governed_research_reopen_gate_latest.json"
OUT_TXT = OUT_DIR / "governed_research_reopen_gate_latest.txt"
OUT_GATES_CSV = OUT_DIR / "governed_research_reopen_gate_checks_latest.csv"

REPO_REOPEN_STATE_JSON = POLICY_DIR / "governed_research_reopen_gate_state_v1.json"
REPO_REOPEN_POLICY_JSON = POLICY_DIR / "governed_research_reopen_policy_v1.json"
REPO_RESTRICTED_TEMPLATE_JSON = CONTRACT_DIR / "restricted_pre_registered_research_contract_template_v1.json"
REPO_NEXT_QUEUE_JSON = QUEUE_DIR / "governed_research_reopen_next_queue_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD7_05_RESTRICTED_PRE_REGISTERED_RESEARCH_CONTRACT_FACTORY"
NEXT_MODULE = "edge_factory_os_restricted_pre_registered_research_contract_factory_v1.py"

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


def gate(key: str, passed: bool, observed: Any, required: Any) -> Dict[str, Any]:
    return {
        "gate_key": key,
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
            "passed": observed is False,
            "observed": observed,
            "required": False,
        })
    return rows


def build_text(result: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS GOVERNED RESEARCH REOPEN GATE v1")
    lines.append("=" * 100)

    for key in [
        "gate_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "governed_reopen_gate_pass",
        "broad_strategy_search_allowed",
        "restricted_pre_registered_research_contract_allowed",
        "candidate_generation_allowed",
        "candidate_contract_allowed",
        "family_release_allowed",
        "runtime_touch_allowed",
        "capital_change_allowed",
        "active_paper_allowed",
        "live_allowed",
        "real_orders_allowed",
        "failed_gate_count",
        "failed_gate_keys",
        "next_recommended_research_key",
        "next_module",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("CORE DECISION")
    lines.append("-" * 100)
    lines.append("Broad/free strategy search remains blocked.")
    lines.append("Only a future narrow pre-registered research contract factory may be built if gate passes.")
    lines.append("That future factory still cannot release candidates or touch runtime/capital/live.")
    lines.append("Promising vault ideas are preserved but cannot bypass governance.")

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
        "reopen_state_json",
        "reopen_policy_json",
        "restricted_template_json",
        "next_queue_json",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS GOVERNED RESEARCH REOPEN GATE v1")
    print("=" * 100)
    print(f"gate_status: {result.get('gate_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"governed_reopen_gate_pass: {result.get('governed_reopen_gate_pass')}")
    print(f"broad_strategy_search_allowed: {result.get('broad_strategy_search_allowed')}")
    print(f"restricted_pre_registered_research_contract_allowed: {result.get('restricted_pre_registered_research_contract_allowed')}")
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
    print(f"STATE: {result.get('reopen_state_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    CONTRACT_DIR.mkdir(parents=True, exist_ok=True)

    ledger = load_json(LEDGER_JSON, {})
    budget = load_json(RESEARCH_BUDGET_JSON, {})
    vault = load_json(PROMISING_VAULT_JSON, {})
    anti = load_json(ANTI_OVERFIT_JSON, {})
    pre_reg_gov = load_json(PRE_REG_GOVERNANCE_JSON, {})
    nested = load_json(NESTED_VALIDATION_JSON, {})
    holdout_access = load_json(HOLDOUT_ACCESS_JSON, {})
    holdout_commitment = load_json(HOLDOUT_COMMITMENT_JSON, {})
    holdout_registry = load_json(UNTOUCHED_HOLDOUT_REGISTRY_JSON, {})
    alpha_accounting = load_json(GLOBAL_ALPHA_ACCOUNTING_JSON, {})
    alpha_policy = load_json(GLOBAL_ALPHA_POLICY_JSON, {})
    alpha_queue = load_json(GLOBAL_ALPHA_NEXT_QUEUE_JSON, {})
    lessons = extract_list(load_json(LESSON_INDEX_JSON, {}), "lessons")
    blocked = extract_list(load_json(BLOCKLIST_JSON, {}), "blocked_routes")
    vault_items = extract_list(vault, "vault_items")
    family_rows = alpha_accounting.get("route_family_rows", [])
    if not isinstance(family_rows, list):
        family_rows = []

    gates: List[Dict[str, Any]] = [
        gate("GLOBAL_LEDGER_ACTIVE", ledger.get("ledger_status") == "GLOBAL_MULTIPLE_TESTING_LEDGER_ACTIVE_RESEARCH_LOCKED", ledger.get("ledger_status"), "GLOBAL_MULTIPLE_TESTING_LEDGER_ACTIVE_RESEARCH_LOCKED"),
        gate("RESEARCH_BUDGET_ACTIVE", budget.get("policy_status") == "RESEARCH_BUDGET_POLICY_ACTIVE_METHODOLOGY_ONLY", budget.get("policy_status"), "RESEARCH_BUDGET_POLICY_ACTIVE_METHODOLOGY_ONLY"),
        gate("STRATEGY_SEARCH_BUDGET_LOCKED", budget.get("research_budget_status") == "STRATEGY_SEARCH_BUDGET_LOCKED_UNTIL_GOVERNANCE_REPAIR", budget.get("research_budget_status"), "STRATEGY_SEARCH_BUDGET_LOCKED_UNTIL_GOVERNANCE_REPAIR"),
        gate("PROMISING_VAULT_ACTIVE", vault.get("vault_status") == "PROMISING_SIGNAL_VAULT_ACTIVE_RELEASE_BLOCKED", vault.get("vault_status"), "PROMISING_SIGNAL_VAULT_ACTIVE_RELEASE_BLOCKED"),
        gate("PROMISING_VAULT_HAS_ITEM", len(vault_items) >= 1, len(vault_items), ">=1"),
        gate("ANTI_OVERFITTING_ACTIVE", anti.get("state_status") == "ANTI_OVERFITTING_GOVERNANCE_ACTIVE_RESEARCH_REPAIR_REQUIRED", anti.get("state_status"), "ANTI_OVERFITTING_GOVERNANCE_ACTIVE_RESEARCH_REPAIR_REQUIRED"),
        gate("PRE_REG_GOVERNANCE_PASS", pre_reg_gov.get("governance_gate_pass") is True, pre_reg_gov.get("governance_gate_pass"), True),
        gate("PRE_REG_STRATEGY_LOCKED", pre_reg_gov.get("strategy_search_allowed_now") is False, pre_reg_gov.get("strategy_search_allowed_now"), False),
        gate("NESTED_VALIDATION_READY", nested.get("policy_status") == "NESTED_VALIDATION_POLICY_READY_STRATEGY_SEARCH_LOCKED", nested.get("policy_status"), "NESTED_VALIDATION_POLICY_READY_STRATEGY_SEARCH_LOCKED"),
        gate("HOLDOUT_ACCESS_BLOCKED", holdout_access.get("holdout_access_allowed_now") is False, holdout_access.get("holdout_access_allowed_now"), False),
        gate("HOLDOUT_NOT_SELECTED", holdout_registry.get("holdout_selected") is False, holdout_registry.get("holdout_selected"), False),
        gate("HOLDOUT_NOT_PEEKED", holdout_registry.get("holdout_peeked") is False, holdout_registry.get("holdout_peeked"), False),
        gate("HOLDOUT_NOT_USABLE_NOW", holdout_registry.get("holdout_usable_now") is False, holdout_registry.get("holdout_usable_now"), False),
        gate("HOLDOUT_COMMITMENT_READY_NO_SELECTION", holdout_commitment.get("protocol_status") == "HOLDOUT_COMMITMENT_PROTOCOL_READY_NO_HOLDOUT_SELECTED", holdout_commitment.get("protocol_status"), "HOLDOUT_COMMITMENT_PROTOCOL_READY_NO_HOLDOUT_SELECTED"),
        gate("GLOBAL_ALPHA_ACCOUNTING_PASS", alpha_accounting.get("global_alpha_accounting_pass") is True, alpha_accounting.get("global_alpha_accounting_pass"), True),
        gate("GLOBAL_ALPHA_STRATEGY_SEARCH_LOCKED", alpha_accounting.get("strategy_search_allowed_now") is False, alpha_accounting.get("strategy_search_allowed_now"), False),
        gate("GLOBAL_ALPHA_FUTURE_REOPEN_NOT_ALREADY_ALLOWED", alpha_accounting.get("future_strategy_reopen_allowed_now") is False, alpha_accounting.get("future_strategy_reopen_allowed_now"), False),
        gate("ALPHA_POLICY_ZERO_STRATEGY_BUDGET", alpha_policy.get("current_total_strategy_route_budget") == 0, alpha_policy.get("current_total_strategy_route_budget"), 0),
        gate("ALPHA_POLICY_ZERO_ALPHA_BUDGET", float(alpha_policy.get("current_total_strategy_alpha_budget", -1)) == 0.0, alpha_policy.get("current_total_strategy_alpha_budget"), 0.0),
        gate("ALPHA_NEXT_QUEUE_READY", alpha_queue.get("queue_status") == "GLOBAL_ALPHA_ACCOUNTING_NEXT_QUEUE_READY", alpha_queue.get("queue_status"), "GLOBAL_ALPHA_ACCOUNTING_NEXT_QUEUE_READY"),
        gate("FAMILY_ROWS_PRESENT", len(family_rows) >= 1, len(family_rows), ">=1"),
        gate("ALL_FAMILY_ALPHA_ZERO", all(float(r.get("current_alpha_budget", -1)) == 0.0 for r in family_rows), [r.get("current_alpha_budget") for r in family_rows], "all 0.0"),
        gate("ALL_FAMILY_STRATEGY_BUDGET_ZERO", all(int(r.get("current_strategy_search_budget", -1)) == 0 for r in family_rows), [r.get("current_strategy_search_budget") for r in family_rows], "all 0"),
        gate("LESSONS_PRESENT", len(lessons) >= 1, len(lessons), ">=1"),
        gate("BLOCKLIST_PRESENT", len(blocked) >= 1, len(blocked), ">=1"),
    ]

    gates.extend(safety_flags_all_false(budget, "BUDGET"))
    gates.extend(safety_flags_all_false(anti, "ANTI_OVERFIT"))
    gates.extend(safety_flags_all_false(nested, "NESTED"))
    gates.extend(safety_flags_all_false(holdout_access, "HOLDOUT_ACCESS"))
    gates.extend(safety_flags_all_false(holdout_registry, "HOLDOUT_REGISTRY"))
    gates.extend(safety_flags_all_false(alpha_accounting, "ALPHA_ACCOUNTING"))
    gates.extend(safety_flags_all_false(alpha_policy, "ALPHA_POLICY"))

    failed = [row["gate_key"] for row in gates if row["passed"] is not True]
    gate_pass = len(failed) == 0

    broad_strategy_search_allowed = False
    restricted_pre_registered_research_contract_allowed = gate_pass

    if gate_pass:
        gate_status = "GOVERNED_RESEARCH_REOPEN_GATE_PASS_RESTRICTED_CONTRACT_FACTORY_ALLOWED"
        severity = "ATTENTION"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        next_action = "BUILD_RESTRICTED_PRE_REGISTERED_RESEARCH_CONTRACT_FACTORY_NO_STRATEGY_EXECUTION"
        reason = "full anti-overfitting chain passes; broad strategy search remains blocked; only restricted pre-registered research contract factory may be built"
        next_module = NEXT_MODULE
        return_code = 0
    else:
        gate_status = "GOVERNED_RESEARCH_REOPEN_GATE_FAIL_RESEARCH_REOPEN_BLOCKED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_REOPEN_GATE_FAILURES_BEFORE_ANY_RESEARCH"
        reason = f"failed_gate_count={len(failed)}"
        next_module = None
        return_code = 2

    reopen_policy = {
        "policy_name": "edge_factory_os_governed_research_reopen_policy_v1",
        "created_at_utc": utc_now_iso(),
        "policy_status": "GOVERNED_RESEARCH_REOPEN_POLICY_ACTIVE_RESTRICTED_CONTRACTS_ONLY" if gate_pass else "GOVERNED_RESEARCH_REOPEN_POLICY_BLOCKED_REVIEW_REQUIRED",
        "broad_strategy_search_allowed": False,
        "restricted_pre_registered_research_contract_allowed": restricted_pre_registered_research_contract_allowed,
        "strategy_execution_allowed": False,
        "candidate_generation_allowed": False,
        "candidate_contract_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        "hard_rules": {
            "no_broad_axis_search": True,
            "no_post_hoc_threshold_selection": True,
            "no_same_route_hash_reuse": True,
            "promising_vault_may_inform_hypothesis_but_not_release": True,
            "all_hypotheses_must_be_pre_registered": True,
            "all_research_must_receive_explicit_alpha_budget_before_run": True,
            "all_research_must_have nested_validation_plan": True,
            "holdout_access_for_strategy_search_allowed": False,
            "procedural_null_required_for_any_search_procedure": True,
            "candidate_generation_stays_blocked_after_contract_factory": True,
        },
        "minimum_contract_requirements": [
            "new_route_hash",
            "route_family",
            "hypothesis_plain_english",
            "feature_family_pre_declared",
            "threshold_grid_pre_declared",
            "null_models_pre_declared",
            "success_criteria_pre_declared",
            "budget_allocation_pre_declared",
            "nested_validation_plan",
            "holdout_access_forbidden",
            "promising_vault_reference_if_reusing_prior_hint",
            "blocked_route_preflight",
            "candidate/family/runtime/capital/live/real_orders_false",
        ],
        "release_gate_feed": {
            "GOVERNED_RESEARCH_REOPEN_GATE_PASS": gate_pass,
            "BROAD_STRATEGY_SEARCH_ALLOWED": False,
            "RESTRICTED_PRE_REGISTERED_RESEARCH_CONTRACT_ALLOWED": restricted_pre_registered_research_contract_allowed,
            "CANDIDATE_GENERATION_ALLOWED_FROM_REOPEN_POLICY": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_REOPEN_POLICY": False,
            "FAMILY_RELEASE_ALLOWED_FROM_REOPEN_POLICY": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_REOPEN_POLICY": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_REOPEN_POLICY": False,
            "ACTIVE_PAPER_ALLOWED_FROM_REOPEN_POLICY": False,
            "LIVE_ALLOWED_FROM_REOPEN_POLICY": False,
            "REAL_ORDERS_ALLOWED_FROM_REOPEN_POLICY": False,
        },
        **SAFETY_FLAGS,
    }

    restricted_template = {
        "template_name": "edge_factory_os_restricted_pre_registered_research_contract_template_v1",
        "created_at_utc": utc_now_iso(),
        "template_status": "RESTRICTED_PRE_REGISTERED_RESEARCH_CONTRACT_TEMPLATE_READY" if gate_pass else "RESTRICTED_TEMPLATE_BLOCKED",
        "purpose": "Template only. Does not create or run strategy research.",
        "broad_strategy_search_allowed": False,
        "strategy_execution_allowed": False,
        "required_fields": {
            "research_key": None,
            "route_family": None,
            "new_route_hash": None,
            "hypothesis_plain_english": None,
            "prior_vault_item_reference": None,
            "feature_family_pre_declared": [],
            "threshold_grid_pre_declared": [],
            "axis_family_pre_declared": [],
            "null_models_pre_declared": [],
            "success_criteria_pre_declared": {},
            "failure_criteria_pre_declared": {},
            "alpha_budget_requested": 0.0,
            "route_budget_requested": 0,
            "nested_validation_plan_reference": None,
            "holdout_access_policy": "FORBIDDEN",
            "blocked_route_preflight_required": True,
            "procedural_null_required": True,
            "candidate_generation_allowed": False,
            "family_release_allowed": False,
            "runtime_touch_allowed": False,
            "capital_change_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
        },
        "forbidden_mutations_after_contract_start": [
            "feature_family",
            "threshold_grid",
            "axis_family",
            "null_models",
            "success_criteria",
            "holdout_definition",
            "route_family",
        ],
        **SAFETY_FLAGS,
    }

    next_queue = {
        "queue_name": "edge_factory_os_governed_research_reopen_next_queue_v1",
        "created_at_utc": utc_now_iso(),
        "queue_status": "GOVERNED_RESEARCH_REOPEN_NEXT_QUEUE_READY" if gate_pass else "GOVERNED_RESEARCH_REOPEN_QUEUE_BLOCKED_REVIEW_REQUIRED",
        "broad_strategy_search_allowed": False,
        "restricted_pre_registered_research_contract_allowed": restricted_pre_registered_research_contract_allowed,
        "top_next_research_key": NEXT_RESEARCH_KEY if gate_pass else None,
        "top_next_module": next_module,
        "next_steps": [
            {
                "research_key": NEXT_RESEARCH_KEY,
                "module": NEXT_MODULE,
                "priority": 100,
                "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
                "purpose": "Build a factory that can create a narrow pre-registered research contract from vault/ledger under explicit alpha and route budget, without running research.",
                "broad_strategy_search_allowed": False,
                "strategy_execution_allowed": False,
                "candidate_generation_allowed": False,
                "family_release_allowed": False,
                "runtime_touch_allowed": False,
                "capital_change_allowed": False,
                "active_paper_allowed": False,
                "live_allowed": False,
                "real_orders_allowed": False,
            }
        ] if gate_pass else [],
        **SAFETY_FLAGS,
    }

    reopen_state = {
        "state_name": "edge_factory_os_governed_research_reopen_gate_state_v1",
        "created_at_utc": utc_now_iso(),
        "gate_status": gate_status,
        "strict_policy_key": STRICT_POLICY_KEY,
        "governed_reopen_gate_pass": gate_pass,
        "broad_strategy_search_allowed": False,
        "restricted_pre_registered_research_contract_allowed": restricted_pre_registered_research_contract_allowed,
        "strategy_execution_allowed": False,
        "failed_gate_count": len(failed),
        "failed_gate_keys": failed,
        "next_recommended_research_key": NEXT_RESEARCH_KEY if gate_pass else None,
        "next_module": next_module,
        **SAFETY_FLAGS,
    }

    write_csv(OUT_GATES_CSV, gates)
    write_json(REPO_REOPEN_STATE_JSON, reopen_state)
    write_json(REPO_REOPEN_POLICY_JSON, reopen_policy)
    write_json(REPO_RESTRICTED_TEMPLATE_JSON, restricted_template)
    write_json(REPO_NEXT_QUEUE_JSON, next_queue)

    result = {
        "gate_name": "edge_factory_os_governed_research_reopen_gate_v1",
        "created_at_utc": utc_now_iso(),
        "gate_status": gate_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "strict_policy_key": STRICT_POLICY_KEY,
        "governed_reopen_gate_pass": gate_pass,
        "broad_strategy_search_allowed": broad_strategy_search_allowed,
        "restricted_pre_registered_research_contract_allowed": restricted_pre_registered_research_contract_allowed,
        "strategy_execution_allowed": False,
        "failed_gate_count": len(failed),
        "failed_gate_keys": failed,
        "family_count": len(family_rows),
        "vault_item_count": len(vault_items),
        "blocked_route_count": len(blocked),
        "lesson_count": len(lessons),
        "next_recommended_research_key": NEXT_RESEARCH_KEY if gate_pass else None,
        "next_module": next_module,
        "gate_rows": gates,
        "reopen_state": reopen_state,
        "reopen_policy": reopen_policy,
        "restricted_template": restricted_template,
        "next_queue": next_queue,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "gates_csv": str(OUT_GATES_CSV),
        "reopen_state_json": str(REPO_REOPEN_STATE_JSON),
        "reopen_policy_json": str(REPO_REOPEN_POLICY_JSON),
        "restricted_template_json": str(REPO_RESTRICTED_TEMPLATE_JSON),
        "next_queue_json": str(REPO_NEXT_QUEUE_JSON),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text(result))
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
