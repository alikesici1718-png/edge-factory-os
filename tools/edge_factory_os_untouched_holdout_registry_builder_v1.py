#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Untouched Holdout Registry + Nested Validation Builder v1

Purpose:
- Consume pre-registered research redesign governance state.
- Build an untouched holdout registry framework without exposing or using any final holdout.
- Build nested validation governance plan:
  search set -> validation set -> untouched final holdout.
- Lock strategy search until holdout/nested validation governance is fully validated.
- Preserve promising ideas without allowing release.
- Keep candidate/family/runtime/capital/active-paper/live/real-order actions blocked.

This builder does NOT:
- select actual final holdout data
- expose holdout periods/symbols
- run strategy research
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

GOVERNANCE_STATE_JSON = POLICY_DIR / "pre_registered_research_redesign_governance_state_v1.json"
NEXT_QUEUE_JSON = QUEUE_DIR / "anti_overfitting_governance_next_queue_v1.json"

LEDGER_JSON = POLICY_DIR / "global_multiple_testing_ledger_v1.json"
RESEARCH_BUDGET_JSON = POLICY_DIR / "research_budget_policy_v1.json"
PROMISING_VAULT_JSON = POLICY_DIR / "promising_signal_vault_v1.json"
ANTI_OVERFIT_JSON = POLICY_DIR / "anti_overfitting_governance_state_v1.json"

HOLDOUT_POLICY_JSON = POLICY_DIR / "holdout_governance_policy_v1.json"
PRE_REG_POLICY_JSON = POLICY_DIR / "pre_registration_policy_v1.json"
ROUTE_BUDGET_POLICY_JSON = POLICY_DIR / "route_budget_allocation_policy_v1.json"

LESSON_INDEX_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

SOURCE_PANEL_PATH = (
    BASE_DIR
    / "edge_factory_feature_panels"
    / "post_impulse_drift_long_v1"
    / "post_impulse_drift_long_v1_feature_panel_1h_dynamic.parquet"
)

REPO_UNTOUCHED_HOLDOUT_REGISTRY_JSON = REGISTRY_DIR / "untouched_holdout_registry_v1.json"
REPO_NESTED_VALIDATION_PLAN_JSON = POLICY_DIR / "nested_validation_policy_v1.json"
REPO_HOLDOUT_ACCESS_CONTROL_JSON = POLICY_DIR / "holdout_access_control_policy_v1.json"
REPO_HOLDOUT_COMMITMENT_PROTOCOL_JSON = POLICY_DIR / "holdout_commitment_protocol_v1.json"
REPO_NEXT_QUEUE_JSON = QUEUE_DIR / "holdout_nested_validation_next_queue_v1.json"

OUT_DIR = BASE_DIR / "edge_factory_os_untouched_holdout_registry_builder"
OUT_JSON = OUT_DIR / "untouched_holdout_registry_builder_latest.json"
OUT_TXT = OUT_DIR / "untouched_holdout_registry_builder_latest.txt"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

RESEARCH_KEY = "UNTOUCHED_HOLDOUT_REGISTRY_AND_NESTED_VALIDATION_V1"
DIRECTION_QUEUE_KEY = "RD7_02_UNTOUCHED_HOLDOUT_REGISTRY_AND_NESTED_VALIDATION"
NEXT_RESEARCH_KEY = "RD7_03_GLOBAL_ROUTE_FAMILY_ALPHA_ACCOUNTANT"
NEXT_MODULE = "edge_factory_os_global_route_family_alpha_accountant_v1.py"

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


def build_text(result: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS UNTOUCHED HOLDOUT REGISTRY + NESTED VALIDATION BUILDER v1")
    lines.append("=" * 100)

    for key in [
        "builder_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "holdout_registry_status",
        "holdout_selected",
        "holdout_peeked",
        "holdout_usable_now",
        "nested_validation_policy_status",
        "holdout_access_control_status",
        "holdout_commitment_protocol_status",
        "strategy_search_allowed_now",
        "methodology_repair_allowed_now",
        "next_recommended_research_key",
        "next_module",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("CORE DECISION")
    lines.append("-" * 100)
    lines.append("The final holdout is still NOT selected and NOT exposed.")
    lines.append("No strategy search can use holdout data.")
    lines.append("Nested validation is now defined as search -> validation -> untouched final holdout.")
    lines.append("The next repair step is global route-family alpha accounting.")

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
        "untouched_holdout_registry_json",
        "nested_validation_policy_json",
        "holdout_access_control_json",
        "holdout_commitment_protocol_json",
        "next_queue_json",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS UNTOUCHED HOLDOUT REGISTRY + NESTED VALIDATION BUILDER v1")
    print("=" * 100)
    print(f"builder_status: {result.get('builder_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"holdout_registry_status: {result.get('holdout_registry_status')}")
    print(f"holdout_selected: {result.get('holdout_selected')}")
    print(f"holdout_peeked: {result.get('holdout_peeked')}")
    print(f"holdout_usable_now: {result.get('holdout_usable_now')}")
    print(f"nested_validation_policy_status: {result.get('nested_validation_policy_status')}")
    print(f"holdout_access_control_status: {result.get('holdout_access_control_status')}")
    print(f"holdout_commitment_protocol_status: {result.get('holdout_commitment_protocol_status')}")
    print(f"strategy_search_allowed_now: {result.get('strategy_search_allowed_now')}")
    print(f"methodology_repair_allowed_now: {result.get('methodology_repair_allowed_now')}")
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
    print(f"REGISTRY: {result.get('untouched_holdout_registry_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    governance = load_json(GOVERNANCE_STATE_JSON, {})
    queue = load_json(NEXT_QUEUE_JSON, {})
    ledger = load_json(LEDGER_JSON, {})
    budget = load_json(RESEARCH_BUDGET_JSON, {})
    vault = load_json(PROMISING_VAULT_JSON, {})
    anti = load_json(ANTI_OVERFIT_JSON, {})
    holdout_policy = load_json(HOLDOUT_POLICY_JSON, {})
    pre_reg_policy = load_json(PRE_REG_POLICY_JSON, {})
    route_budget_policy = load_json(ROUTE_BUDGET_POLICY_JSON, {})
    lessons = extract_list(load_json(LESSON_INDEX_JSON, {}), "lessons")
    blocked = extract_list(load_json(BLOCKLIST_JSON, {}), "blocked_routes")
    vault_items = extract_list(vault, "vault_items")

    prerequisites = {
        "governance_pass": governance.get("governance_gate_pass") is True,
        "strategy_search_locked": governance.get("strategy_search_allowed_now") is False,
        "methodology_repair_allowed": governance.get("methodology_repair_allowed_now") is True,
        "queue_ready": queue.get("queue_status") == "ANTI_OVERFITTING_GOVERNANCE_NEXT_QUEUE_READY",
        "top_next_module_match": queue.get("top_next_module") == "edge_factory_os_untouched_holdout_registry_builder_v1.py",
        "ledger_active": ledger.get("ledger_status") == "GLOBAL_MULTIPLE_TESTING_LEDGER_ACTIVE_RESEARCH_LOCKED",
        "budget_active": budget.get("policy_status") == "RESEARCH_BUDGET_POLICY_ACTIVE_METHODOLOGY_ONLY",
        "vault_active": vault.get("vault_status") == "PROMISING_SIGNAL_VAULT_ACTIVE_RELEASE_BLOCKED",
        "anti_overfit_active": anti.get("state_status") == "ANTI_OVERFITTING_GOVERNANCE_ACTIVE_RESEARCH_REPAIR_REQUIRED",
        "holdout_policy_ready": holdout_policy.get("policy_status") == "HOLDOUT_GOVERNANCE_POLICY_DRAFT_READY",
        "pre_registration_ready": pre_reg_policy.get("policy_status") == "PRE_REGISTRATION_POLICY_DRAFT_READY",
        "route_budget_ready": route_budget_policy.get("policy_status") == "ROUTE_BUDGET_ALLOCATION_POLICY_DRAFT_READY",
    }

    prerequisite_pass = all(prerequisites.values())

    commitment_protocol_payload = {
        "research_key": RESEARCH_KEY,
        "source_panel_path_hash_only": stable_hash({"source_panel_path": str(SOURCE_PANEL_PATH)}),
        "holdout_selected": False,
        "holdout_definition_hidden": True,
        "holdout_commitment_not_created_yet": True,
        "created_at_utc": utc_now_iso(),
    }

    holdout_commitment_protocol = {
        "protocol_name": "edge_factory_os_holdout_commitment_protocol_v1",
        "protocol_status": "HOLDOUT_COMMITMENT_PROTOCOL_READY_NO_HOLDOUT_SELECTED",
        "created_at_utc": utc_now_iso(),
        "purpose": "Defines how a future untouched final holdout must be selected and committed without exposing it during strategy search.",
        "holdout_selected": False,
        "holdout_peeked": False,
        "holdout_usable_now": False,
        "holdout_definition_visible_to_research_modules": False,
        "commitment_protocol_hash": stable_hash(commitment_protocol_payload),
        "required_future_steps": [
            "select holdout only after governance approval",
            "write hash commitment of holdout definition",
            "do not expose actual holdout periods/symbols to strategy-search modules",
            "record every access request",
            "allow final holdout use only after search and validation are frozen",
            "single-use final holdout policy",
        ],
        "forbidden_actions": [
            "holdout_peeking",
            "holdout_reuse",
            "holdout_in_strategy_search",
            "holdout_in_threshold_selection",
            "holdout_in_feature_selection",
            "holdout_in_route_selection",
            "post_hoc_holdout_selection",
        ],
        **SAFETY_FLAGS,
    }

    untouched_holdout_registry = {
        "registry_name": "edge_factory_os_untouched_holdout_registry_v1",
        "registry_status": "UNTOUCHED_HOLDOUT_REGISTRY_READY_NOT_SELECTED_NOT_PEEKED",
        "created_at_utc": utc_now_iso(),
        "strict_policy_key": STRICT_POLICY_KEY,
        "source_panel_path_hash_only": stable_hash({"source_panel_path": str(SOURCE_PANEL_PATH)}),
        "source_panel_exists": SOURCE_PANEL_PATH.exists(),
        "holdout_selected": False,
        "holdout_peeked": False,
        "holdout_usable_now": False,
        "holdout_definition_visible": False,
        "holdout_commitment_hash": None,
        "holdout_access_log": [],
        "registry_schema": {
            "holdout_id": "string_future_required",
            "selection_time_utc": "future_required",
            "selection_method": "future_required",
            "hash_of_holdout_definition": "future_required",
            "access_policy": "future_required",
            "single_use_status": "future_required",
            "access_log": "future_required",
            "retirement_status": "future_required",
        },
        "access_rules": {
            "strategy_search_access_allowed": False,
            "validation_access_allowed": False,
            "final_holdout_access_allowed_now": False,
            "access_requires_governance_state": True,
            "access_requires_frozen_hypothesis": True,
            "access_requires_candidate_family_runtime_capital_live_still_blocked": True,
        },
        "release_gate_feed": {
            "UNTOUCHED_HOLDOUT_REGISTRY_READY": prerequisite_pass,
            "HOLDOUT_SELECTED": False,
            "HOLDOUT_PEEKED": False,
            "HOLDOUT_USABLE_NOW": False,
            "STRATEGY_SEARCH_ALLOWED_FROM_THIS_REGISTRY": False,
            "RELEASE_PASS_FROM_THIS_REGISTRY": False,
        },
        **SAFETY_FLAGS,
    }

    nested_validation_policy = {
        "policy_name": "edge_factory_os_nested_validation_policy_v1",
        "policy_status": "NESTED_VALIDATION_POLICY_READY_STRATEGY_SEARCH_LOCKED",
        "created_at_utc": utc_now_iso(),
        "strict_policy_key": STRICT_POLICY_KEY,
        "strategy_search_allowed_now": False,
        "methodology_repair_allowed_now": True,
        "layers": {
            "layer_1_search_set": {
                "purpose": "Exploration only within pre-registered route budget.",
                "may_select_features": True,
                "may_select_thresholds": True,
                "may_influence_release": False,
                "requires_budget_before_run": True,
            },
            "layer_2_validation_set": {
                "purpose": "Test frozen pre-registered hypothesis after search is complete.",
                "may_select_features": False,
                "may_select_thresholds": False,
                "may_influence_release_alone": False,
                "requires_no_post_hoc_mutation": True,
            },
            "layer_3_untouched_final_holdout": {
                "purpose": "Single-use final examination only after search and validation are frozen.",
                "may_select_features": False,
                "may_select_thresholds": False,
                "may_be_reused": False,
                "may_be_exposed_before_final_gate": False,
                "required_before_candidate_release": True,
            },
        },
        "hard_rules": [
            "same data cannot serve as search and final holdout",
            "holdout cannot influence feature/threshold/route selection",
            "any contract mutation after validation invalidates route",
            "procedural null remains required for search procedures",
            "global alpha accounting remains required",
            "promising vault items cannot bypass validation",
            "candidate/family/runtime/capital/live remain blocked",
        ],
        "release_gate_feed": {
            "NESTED_VALIDATION_POLICY_READY": prerequisite_pass,
            "STRATEGY_SEARCH_ALLOWED_FROM_THIS_POLICY": False,
            "METHODOLOGY_REPAIR_ALLOWED_FROM_THIS_POLICY": True,
            "RELEASE_PASS_FROM_THIS_POLICY": False,
        },
        **SAFETY_FLAGS,
    }

    holdout_access_control = {
        "policy_name": "edge_factory_os_holdout_access_control_policy_v1",
        "policy_status": "HOLDOUT_ACCESS_CONTROL_POLICY_READY_ACCESS_BLOCKED",
        "created_at_utc": utc_now_iso(),
        "holdout_access_allowed_now": False,
        "authorized_access_stage": "NONE_CURRENTLY",
        "required_before_access": [
            "pre_registered_contract_frozen",
            "route_budget_spent_and_closed",
            "search_results_locked",
            "validation_results_locked",
            "global_alpha_accounting_pass",
            "procedural_null_pass",
            "manual_governance_review_or_os_authorization",
        ],
        "forbidden_access_reasons": [
            "strategy_search",
            "feature_selection",
            "threshold_selection",
            "route_selection",
            "debugging_strategy_performance",
            "post_hoc_explanation",
        ],
        "access_log_required": True,
        "release_gate_feed": {
            "HOLDOUT_ACCESS_CONTROL_READY": prerequisite_pass,
            "HOLDOUT_ACCESS_ALLOWED_NOW": False,
            "RELEASE_PASS_FROM_ACCESS_CONTROL": False,
        },
        **SAFETY_FLAGS,
    }

    next_queue = {
        "queue_name": "edge_factory_os_holdout_nested_validation_next_queue_v1",
        "created_at_utc": utc_now_iso(),
        "queue_status": "HOLDOUT_NESTED_VALIDATION_NEXT_QUEUE_READY" if prerequisite_pass else "HOLDOUT_NESTED_VALIDATION_QUEUE_BLOCKED_REVIEW_REQUIRED",
        "strategy_search_allowed_now": False,
        "methodology_repair_allowed_now": prerequisite_pass,
        "top_next_research_key": NEXT_RESEARCH_KEY if prerequisite_pass else None,
        "top_next_module": NEXT_MODULE if prerequisite_pass else None,
        "next_steps": [
            {
                "research_key": NEXT_RESEARCH_KEY,
                "module": NEXT_MODULE,
                "priority": 100,
                "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
                "purpose": "Create global route-family alpha accountant before any strategy search can reopen.",
                "strategy_search_allowed": False,
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

    if prerequisite_pass:
        builder_status = "UNTOUCHED_HOLDOUT_REGISTRY_BUILDER_READY"
        severity = "ATTENTION"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        next_action = "BUILD_GLOBAL_ROUTE_FAMILY_ALPHA_ACCOUNTANT_NO_STRATEGY_SEARCH"
        reason = "untouched holdout registry and nested validation governance are ready; holdout remains unselected/unpeeked; strategy search remains locked"
        next_module = NEXT_MODULE
        return_code = 0
    else:
        builder_status = "UNTOUCHED_HOLDOUT_REGISTRY_BUILDER_BLOCKED_PREREQUISITE_NOT_MET"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_HOLDOUT_REGISTRY_PREREQUISITES_NO_RELEASE"
        reason = f"prerequisites={prerequisites}"
        next_module = None
        return_code = 2

    write_json(REPO_UNTOUCHED_HOLDOUT_REGISTRY_JSON, untouched_holdout_registry)
    write_json(REPO_NESTED_VALIDATION_PLAN_JSON, nested_validation_policy)
    write_json(REPO_HOLDOUT_ACCESS_CONTROL_JSON, holdout_access_control)
    write_json(REPO_HOLDOUT_COMMITMENT_PROTOCOL_JSON, holdout_commitment_protocol)
    write_json(REPO_NEXT_QUEUE_JSON, next_queue)

    result = {
        "builder_name": "edge_factory_os_untouched_holdout_registry_builder_v1",
        "created_at_utc": utc_now_iso(),
        "builder_status": builder_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "strict_policy_key": STRICT_POLICY_KEY,
        "holdout_registry_status": untouched_holdout_registry["registry_status"],
        "holdout_selected": False,
        "holdout_peeked": False,
        "holdout_usable_now": False,
        "nested_validation_policy_status": nested_validation_policy["policy_status"],
        "holdout_access_control_status": holdout_access_control["policy_status"],
        "holdout_commitment_protocol_status": holdout_commitment_protocol["protocol_status"],
        "strategy_search_allowed_now": False,
        "methodology_repair_allowed_now": prerequisite_pass,
        "lesson_count": len(lessons),
        "blocked_route_count": len(blocked),
        "vault_item_count": len(vault_items),
        "prerequisites": prerequisites,
        "next_recommended_research_key": NEXT_RESEARCH_KEY if prerequisite_pass else None,
        "next_module": next_module,
        "untouched_holdout_registry": untouched_holdout_registry,
        "nested_validation_policy": nested_validation_policy,
        "holdout_access_control": holdout_access_control,
        "holdout_commitment_protocol": holdout_commitment_protocol,
        "next_queue": next_queue,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "untouched_holdout_registry_json": str(REPO_UNTOUCHED_HOLDOUT_REGISTRY_JSON),
        "nested_validation_policy_json": str(REPO_NESTED_VALIDATION_PLAN_JSON),
        "holdout_access_control_json": str(REPO_HOLDOUT_ACCESS_CONTROL_JSON),
        "holdout_commitment_protocol_json": str(REPO_HOLDOUT_COMMITMENT_PROTOCOL_JSON),
        "next_queue_json": str(REPO_NEXT_QUEUE_JSON),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text(result))
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
