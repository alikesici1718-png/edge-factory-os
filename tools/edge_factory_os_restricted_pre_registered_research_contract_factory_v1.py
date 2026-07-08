#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Restricted Pre-Registered Research Contract Factory v1

Purpose:
- Consume governed research reopen gate.
- Consume restricted pre-registered research contract template.
- Consume promising signal vault, global alpha accounting, blocklist, nested validation, and holdout governance.
- Create a narrow research-only pre-registered contract PROPOSAL.
- Do NOT run research.
- Do NOT allow candidate generation, family release, runtime touch, capital, active paper, live, or real orders.

This factory is intentionally conservative:
- broad strategy search remains blocked
- research execution remains blocked until a separate preflight validator passes
- final holdout remains unselected/unpeeked/unusable
"""

from __future__ import annotations

import datetime as dt
import hashlib
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

OUT_DIR = BASE_DIR / "edge_factory_os_restricted_pre_registered_research_contract_factory"
OUT_JSON = OUT_DIR / "restricted_pre_registered_research_contract_factory_latest.json"
OUT_TXT = OUT_DIR / "restricted_pre_registered_research_contract_factory_latest.txt"

REPO_PROPOSED_CONTRACT_JSON = CONTRACT_DIR / "restricted_pre_registered_research_contract_proposal_v1.json"
REPO_PROPOSED_CONTRACT_TXT = CONTRACT_DIR / "restricted_pre_registered_research_contract_proposal_v1.txt"
REPO_FACTORY_STATE_JSON = POLICY_DIR / "restricted_pre_registered_research_contract_factory_state_v1.json"
REPO_NEXT_QUEUE_JSON = QUEUE_DIR / "restricted_pre_registered_research_contract_factory_next_queue_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

RESEARCH_KEY = "RESTRICTED_PRE_REGISTERED_RESEARCH_CONTRACT_FACTORY_V1"
DIRECTION_QUEUE_KEY = "RD7_05_RESTRICTED_PRE_REGISTERED_RESEARCH_CONTRACT_FACTORY"
PROPOSED_RESEARCH_KEY = "RESTRICTED_MARKET_STATE_STRUCTURE_RETEST_V1"
NEXT_RESEARCH_KEY = "RD7_06_RESTRICTED_RESEARCH_CONTRACT_PREFLIGHT_VALIDATOR"
NEXT_MODULE = "edge_factory_os_restricted_research_contract_preflight_validator_v1.py"

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


def stable_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def extract_list(obj: Any, key: str) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get(key), list):
        return [x for x in obj[key] if isinstance(x, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def choose_vault_hint(vault_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    for item in vault_items:
        if str(item.get("vault_class")) == "PROMISING_BUT_UNVALIDATED_STRUCTURE_HINT":
            return item
    return vault_items[0] if vault_items else {}


def route_hash_blocked(blocked_routes: List[Dict[str, Any]], route_hash: str) -> bool:
    return route_hash in {str(x.get("route_hash")) for x in blocked_routes if isinstance(x, dict)}


def build_contract_text(contract: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS RESTRICTED PRE-REGISTERED RESEARCH CONTRACT PROPOSAL v1")
    lines.append("=" * 100)

    for key in [
        "contract_status",
        "contract_id",
        "contract_hash",
        "route_hash",
        "research_key",
        "route_family",
        "hypothesis_plain_english",
        "research_execution_allowed_now",
        "broad_strategy_search_allowed",
        "holdout_access_allowed",
        "candidate_generation_allowed",
        "family_release_allowed",
        "runtime_touch_allowed",
        "capital_change_allowed",
        "active_paper_allowed",
        "live_allowed",
        "real_orders_allowed",
    ]:
        lines.append(f"{key}: {contract.get(key)}")

    lines.append("")
    lines.append("PRE-REGISTERED FEATURE FAMILY")
    lines.append("-" * 100)
    for item in contract.get("feature_family_pre_declared", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("PRE-REGISTERED AXIS FAMILY")
    lines.append("-" * 100)
    for item in contract.get("axis_family_pre_declared", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("PRE-REGISTERED NULL MODELS")
    lines.append("-" * 100)
    for item in contract.get("null_models_pre_declared", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("SUCCESS CRITERIA")
    lines.append("-" * 100)
    lines.append(json.dumps(contract.get("success_criteria_pre_declared", {}), indent=2, ensure_ascii=False))

    lines.append("")
    lines.append("FAILURE CRITERIA")
    lines.append("-" * 100)
    lines.append(json.dumps(contract.get("failure_criteria_pre_declared", {}), indent=2, ensure_ascii=False))

    lines.append("")
    lines.append("NESTED VALIDATION PLAN")
    lines.append("-" * 100)
    lines.append(json.dumps(contract.get("nested_validation_plan", {}), indent=2, ensure_ascii=False))

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        lines.append(f"{key}: {value}")

    return "\n".join(lines)


def build_summary_text(result: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS RESTRICTED PRE-REGISTERED RESEARCH CONTRACT FACTORY v1")
    lines.append("=" * 100)

    for key in [
        "factory_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "contract_proposal_status",
        "proposed_contract_id",
        "proposed_route_hash",
        "proposed_route_hash_blocked",
        "broad_strategy_search_allowed",
        "research_execution_allowed_now",
        "restricted_contract_proposal_created",
        "next_recommended_research_key",
        "next_module",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("CORE DECISION")
    lines.append("-" * 100)
    lines.append("A restricted research contract proposal was created, but it is not executable yet.")
    lines.append("A separate preflight validator must pass before any research runner is allowed.")
    lines.append("Broad strategy search remains blocked.")
    lines.append("Candidate/family/runtime/capital/active-paper/live/real-order actions remain blocked.")

    lines.append("")
    lines.append("OUTPUT PATHS")
    lines.append("-" * 100)
    for key in [
        "output_json",
        "output_txt",
        "proposed_contract_json",
        "proposed_contract_txt",
        "factory_state_json",
        "next_queue_json",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS RESTRICTED PRE-REGISTERED RESEARCH CONTRACT FACTORY v1")
    print("=" * 100)
    print(f"factory_status: {result.get('factory_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"contract_proposal_status: {result.get('contract_proposal_status')}")
    print(f"proposed_contract_id: {result.get('proposed_contract_id')}")
    print(f"proposed_route_hash: {result.get('proposed_route_hash')}")
    print(f"proposed_route_hash_blocked: {result.get('proposed_route_hash_blocked')}")
    print(f"broad_strategy_search_allowed: {result.get('broad_strategy_search_allowed')}")
    print(f"research_execution_allowed_now: {result.get('research_execution_allowed_now')}")
    print(f"restricted_contract_proposal_created: {result.get('restricted_contract_proposal_created')}")
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
    print(f"CONTRACT: {result.get('proposed_contract_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CONTRACT_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)

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

    selected_hint = choose_vault_hint(vault_items)

    base_route_payload = {
        "proposal_type": "restricted_pre_registered_research_contract",
        "research_key": PROPOSED_RESEARCH_KEY,
        "route_family": "MARKET_STATE_TRANSITION_FAMILY",
        "source_vault_item_id": selected_hint.get("vault_item_id"),
        "source_route_hash": selected_hint.get("source_route_hash"),
        "feature_family": ["market_state_time_aggregate_features_only"],
        "axis_family": ["narrow_market_state_transition_retest_only"],
        "null_models": [
            "procedural_joint_null_full_search",
            "month_block_shuffle",
            "time_block_shuffle",
            "state_col_independent_block_shuffle",
            "within_month_time_shuffle",
        ],
        "holdout_access": "FORBIDDEN",
        "broad_search": False,
        "created_under_gate": reopen_state.get("gate_status"),
    }

    proposed_route_hash = stable_hash(base_route_payload)
    proposed_route_hash_is_blocked = route_hash_blocked(blocked_routes, proposed_route_hash)

    contract_hash = stable_hash({
        "route_hash": proposed_route_hash,
        "research_key": PROPOSED_RESEARCH_KEY,
        "source_vault_item_id": selected_hint.get("vault_item_id"),
        "template_status": template.get("template_status"),
    })

    contract_id = f"RESTRICTED_PRE_REGISTERED_RESEARCH_CONTRACT_PROPOSAL_V1_{contract_hash}_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')}"

    prerequisites = {
        "reopen_gate_pass": reopen_state.get("governed_reopen_gate_pass") is True,
        "restricted_contract_allowed": reopen_state.get("restricted_pre_registered_research_contract_allowed") is True,
        "broad_strategy_search_blocked": reopen_state.get("broad_strategy_search_allowed") is False,
        "reopen_policy_active": reopen_policy.get("policy_status") == "GOVERNED_RESEARCH_REOPEN_POLICY_ACTIVE_RESTRICTED_CONTRACTS_ONLY",
        "template_ready": template.get("template_status") == "RESTRICTED_PRE_REGISTERED_RESEARCH_CONTRACT_TEMPLATE_READY",
        "vault_has_hint": bool(selected_hint),
        "vault_active": vault.get("vault_status") == "PROMISING_SIGNAL_VAULT_ACTIVE_RELEASE_BLOCKED",
        "alpha_accounting_pass": alpha_accounting.get("global_alpha_accounting_pass") is True,
        "alpha_policy_zero_strategy_budget": float(alpha_policy.get("current_total_strategy_alpha_budget", -1)) == 0.0,
        "holdout_not_selected": holdout_registry.get("holdout_selected") is False,
        "holdout_not_peeked": holdout_registry.get("holdout_peeked") is False,
        "holdout_access_blocked": holdout_access.get("holdout_access_allowed_now") is False,
        "nested_validation_ready": nested_policy.get("policy_status") == "NESTED_VALIDATION_POLICY_READY_STRATEGY_SEARCH_LOCKED",
        "pre_registration_policy_ready": pre_reg_policy.get("policy_status") == "PRE_REGISTRATION_POLICY_DRAFT_READY",
        "route_budget_policy_ready": route_budget_policy.get("policy_status") == "ROUTE_BUDGET_ALLOCATION_POLICY_DRAFT_READY",
        "proposed_route_hash_not_blocked": not proposed_route_hash_is_blocked,
    }

    prerequisite_pass = all(prerequisites.values())

    proposed_contract = {
        "contract_name": "edge_factory_os_restricted_pre_registered_research_contract_proposal_v1",
        "created_at_utc": utc_now_iso(),
        "contract_status": "RESTRICTED_RESEARCH_CONTRACT_PROPOSAL_READY_NOT_EXECUTABLE" if prerequisite_pass else "RESTRICTED_RESEARCH_CONTRACT_PROPOSAL_BLOCKED",
        "contract_id": contract_id if prerequisite_pass else None,
        "contract_hash": contract_hash,
        "route_hash": proposed_route_hash,
        "route_hash_payload": base_route_payload,
        "research_key": PROPOSED_RESEARCH_KEY,
        "route_family": "MARKET_STATE_TRANSITION_FAMILY",
        "source_vault_item_id": selected_hint.get("vault_item_id"),
        "source_route_hash": selected_hint.get("source_route_hash"),
        "source_research_key": selected_hint.get("source_research_key"),
        "hypothesis_plain_english": (
            "A narrow retest of whether market-state transition structure contains non-random information, "
            "without broad axis search, without holdout access, and with full procedural null validation."
        ),
        "broad_strategy_search_allowed": False,
        "research_execution_allowed_now": False,
        "contract_preflight_required": True,
        "holdout_access_allowed": False,
        "holdout_access_policy": "FORBIDDEN",
        "feature_family_pre_declared": [
            "market-level candle body/range aggregate states",
            "time-state aggregate transition states",
            "no future returns",
            "no pnl labels",
            "no outcome leakage features",
        ],
        "threshold_grid_pre_declared": [
            "fixed tertile bucket transitions only",
            "no post-hoc threshold tuning",
            "no adaptive threshold expansion",
        ],
        "axis_family_pre_declared": [
            "restricted market-state transition axes only",
            "no symbol-level expansion",
            "no event-motif expansion",
            "no new archetype expansion",
        ],
        "null_models_pre_declared": [
            "procedural_joint_null_full_search",
            "month_block_shuffle",
            "time_block_shuffle",
            "state_col_independent_block_shuffle",
            "within_month_time_shuffle",
        ],
        "success_criteria_pre_declared": {
            "procedural_joint_null_max_p_count_required": "<= 0.01",
            "procedural_joint_null_max_p_joint_required": "<= diagnostic_alpha_after_pressure",
            "nested_validation_required": True,
            "holdout_access_required": False,
            "no_candidate_generation_even_if_pass": True,
            "no_family_release_even_if_pass": True,
        },
        "failure_criteria_pre_declared": {
            "any_post_hoc_feature_or_threshold_change": "route_invalid",
            "proposed_route_hash_blocked": "route_invalid",
            "procedural_null_fail": "route_closed_or_redesign_required",
            "holdout_access_attempt": "critical_failure",
            "candidate_or_runtime_flag_true": "critical_failure",
        },
        "budget_allocation_pre_declared": {
            "alpha_budget_requested": 0.0,
            "route_budget_requested": 0,
            "reason": "Factory only creates proposal. Separate preflight must allocate nonzero research budget before execution.",
        },
        "nested_validation_plan": {
            "search_set": "not allocated by factory",
            "validation_set": "not allocated by factory",
            "untouched_final_holdout": "forbidden/unselected/unpeeked",
            "preflight_validator_required": True,
        },
        "blocked_route_preflight_required": True,
        "procedural_null_required": True,
        "same_route_hash_reuse_allowed": False,
        "contract_mutation_after_start_invalidates_route": True,
        "release_gate_feed": {
            "RESTRICTED_RESEARCH_CONTRACT_PROPOSAL_READY": prerequisite_pass,
            "RESEARCH_EXECUTION_ALLOWED_NOW": False,
            "BROAD_STRATEGY_SEARCH_ALLOWED": False,
            "HOLDOUT_ACCESS_ALLOWED": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_THIS_CONTRACT": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_THIS_CONTRACT": False,
            "FAMILY_RELEASE_ALLOWED_FROM_THIS_CONTRACT": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_THIS_CONTRACT": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_THIS_CONTRACT": False,
            "ACTIVE_PAPER_ALLOWED_FROM_THIS_CONTRACT": False,
            "LIVE_ALLOWED_FROM_THIS_CONTRACT": False,
            "REAL_ORDERS_ALLOWED_FROM_THIS_CONTRACT": False,
        },
        **SAFETY_FLAGS,
    }

    if prerequisite_pass:
        factory_status = "RESTRICTED_PRE_REGISTERED_RESEARCH_CONTRACT_FACTORY_PROPOSAL_READY"
        severity = "ATTENTION"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        next_action = "BUILD_RESTRICTED_RESEARCH_CONTRACT_PREFLIGHT_VALIDATOR_NO_EXECUTION"
        reason = "restricted research contract proposal created; research execution remains blocked until separate preflight validator passes"
        next_module = NEXT_MODULE
        return_code = 0
    else:
        factory_status = "RESTRICTED_PRE_REGISTERED_RESEARCH_CONTRACT_FACTORY_BLOCKED_PREREQUISITE_NOT_MET"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_RESTRICTED_CONTRACT_FACTORY_PREREQUISITES_NO_RESEARCH"
        reason = f"prerequisites={prerequisites}"
        next_module = None
        return_code = 2

    factory_state = {
        "state_name": "edge_factory_os_restricted_pre_registered_research_contract_factory_state_v1",
        "created_at_utc": utc_now_iso(),
        "factory_status": factory_status,
        "restricted_contract_proposal_created": prerequisite_pass,
        "proposed_contract_id": proposed_contract.get("contract_id"),
        "proposed_route_hash": proposed_route_hash,
        "proposed_route_hash_blocked": proposed_route_hash_is_blocked,
        "research_execution_allowed_now": False,
        "broad_strategy_search_allowed": False,
        "next_recommended_research_key": NEXT_RESEARCH_KEY if prerequisite_pass else None,
        "next_module": next_module,
        **SAFETY_FLAGS,
    }

    next_queue = {
        "queue_name": "edge_factory_os_restricted_pre_registered_research_contract_factory_next_queue_v1",
        "created_at_utc": utc_now_iso(),
        "queue_status": "RESTRICTED_CONTRACT_FACTORY_NEXT_QUEUE_READY" if prerequisite_pass else "RESTRICTED_CONTRACT_FACTORY_QUEUE_BLOCKED_REVIEW_REQUIRED",
        "research_execution_allowed_now": False,
        "broad_strategy_search_allowed": False,
        "top_next_research_key": NEXT_RESEARCH_KEY if prerequisite_pass else None,
        "top_next_module": next_module,
        "next_steps": [
            {
                "research_key": NEXT_RESEARCH_KEY,
                "module": NEXT_MODULE,
                "priority": 100,
                "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
                "purpose": "Validate restricted pre-registered research contract before any research execution can be considered.",
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
        ] if prerequisite_pass else [],
        **SAFETY_FLAGS,
    }

    write_json(REPO_PROPOSED_CONTRACT_JSON, proposed_contract)
    write_text(REPO_PROPOSED_CONTRACT_TXT, build_contract_text(proposed_contract))
    write_json(REPO_FACTORY_STATE_JSON, factory_state)
    write_json(REPO_NEXT_QUEUE_JSON, next_queue)

    result = {
        "factory_name": "edge_factory_os_restricted_pre_registered_research_contract_factory_v1",
        "created_at_utc": utc_now_iso(),
        "factory_status": factory_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "contract_proposal_status": proposed_contract["contract_status"],
        "restricted_contract_proposal_created": prerequisite_pass,
        "proposed_contract_id": proposed_contract.get("contract_id"),
        "proposed_route_hash": proposed_route_hash,
        "proposed_route_hash_blocked": proposed_route_hash_is_blocked,
        "source_vault_item_id": selected_hint.get("vault_item_id"),
        "source_route_hash": selected_hint.get("source_route_hash"),
        "broad_strategy_search_allowed": False,
        "research_execution_allowed_now": False,
        "holdout_access_allowed": False,
        "prerequisites": prerequisites,
        "next_recommended_research_key": NEXT_RESEARCH_KEY if prerequisite_pass else None,
        "next_module": next_module,
        "proposed_contract": proposed_contract,
        "factory_state": factory_state,
        "next_queue": next_queue,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "proposed_contract_json": str(REPO_PROPOSED_CONTRACT_JSON),
        "proposed_contract_txt": str(REPO_PROPOSED_CONTRACT_TXT),
        "factory_state_json": str(REPO_FACTORY_STATE_JSON),
        "next_queue_json": str(REPO_NEXT_QUEUE_JSON),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_summary_text(result))
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
