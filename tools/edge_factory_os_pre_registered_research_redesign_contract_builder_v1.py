#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Pre-Registered Research Redesign + Holdout Governance Contract Builder v1

Purpose:
- Consume Global Multiple Testing Ledger v1.
- Consume Research Budget Policy v1.
- Consume Promising Signal Vault v1.
- Consume Anti-Overfitting Governance State v1.
- Build methodology-only governance contract for future research redesign.
- Require pre-registration, nested validation, untouched final holdout, route budget allocation,
  global alpha accounting, and procedural null validation before any future strategy escalation.
- Preserve promising-but-unvalidated ideas without allowing release.
- Keep candidate/family/runtime/capital/active-paper/live/real-order actions blocked.

This builder does NOT:
- run strategy research
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

import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

LEDGER_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "global_multiple_testing_ledger_v1.json"
)

RESEARCH_BUDGET_POLICY_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_budget_policy_v1.json"
)

PROMISING_SIGNAL_VAULT_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "promising_signal_vault_v1.json"
)

ANTI_OVERFITTING_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "anti_overfitting_governance_state_v1.json"
)

JOINT_VALIDATION_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "joint_null_distribution_validation_state_v1.json"
)

FRAMEWORK_STATUS_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "status"
    / "framework_status_panel_v1.json"
)

LESSON_INDEX_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

FRAMEWORK_DIR = REPO_DIR / "edge_factory_os_framework"
PLUGIN_DIR = FRAMEWORK_DIR / "plugins"
CONTRACT_DIR = FRAMEWORK_DIR / "contracts"
POLICY_DIR = FRAMEWORK_DIR / "policies"
REGISTRY_DIR = FRAMEWORK_DIR / "registries"

REPO_PLUGIN_JSON = PLUGIN_DIR / "pre_registered_research_redesign_plugin_v1.json"
REPO_CONTRACT_JSON = CONTRACT_DIR / "pre_registered_research_redesign_contract_v1.json"
REPO_CONTRACT_TXT = CONTRACT_DIR / "pre_registered_research_redesign_contract_v1.txt"
HOLDOUT_GOVERNANCE_POLICY_JSON = POLICY_DIR / "holdout_governance_policy_v1.json"
PRE_REGISTRATION_POLICY_JSON = POLICY_DIR / "pre_registration_policy_v1.json"
ROUTE_BUDGET_ALLOCATION_POLICY_JSON = POLICY_DIR / "route_budget_allocation_policy_v1.json"
UNTOUCHED_HOLDOUT_REGISTRY_STUB_JSON = REGISTRY_DIR / "untouched_holdout_registry_stub_v1.json"

OUT_DIR = BASE_DIR / "edge_factory_os_pre_registered_research_redesign_contract"
OUT_JSON = OUT_DIR / "pre_registered_research_redesign_contract_latest.json"
OUT_TXT = OUT_DIR / "pre_registered_research_redesign_contract_latest.txt"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

RESEARCH_KEY = "PRE_REGISTERED_RESEARCH_REDESIGN_AND_HOLDOUT_GOVERNANCE_V1"
DIRECTION_QUEUE_KEY = "RD7_01_PRE_REGISTERED_RESEARCH_REDESIGN_AND_HOLDOUT_GOVERNANCE"
PLUGIN_KEY = "PRE_REGISTERED_RESEARCH_REDESIGN_PLUGIN_V1"
NEXT_MODULE = "edge_factory_os_pre_registered_research_redesign_governance_runner_v1.py"

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


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def utc_now_iso() -> str:
    return utc_now().isoformat()


def timestamp_compact() -> str:
    return utc_now().strftime("%Y%m%d_%H%M%S")


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


def extract_lessons(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get("lessons"), list):
        return [x for x in obj["lessons"] if isinstance(x, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def extract_blocked_routes(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get("blocked_routes"), list):
        return [x for x in obj["blocked_routes"] if isinstance(x, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def extract_vault_items(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get("vault_items"), list):
        return [x for x in obj["vault_items"] if isinstance(x, dict)]
    return []


def build_plugin_config(
    *,
    ledger: Dict[str, Any],
    budget: Dict[str, Any],
    vault: Dict[str, Any],
    anti_overfit: Dict[str, Any],
    lessons: List[Dict[str, Any]],
    blocked_routes: List[Dict[str, Any]],
) -> Dict[str, Any]:
    vault_items = extract_vault_items(vault)

    governance_requirements = [
        "pre_registered_contract_before_any_search",
        "route_budget_allocation_before_any_search",
        "global_multiple_testing_ledger_consumed_before_any_search",
        "promising_signal_vault_consumed_before_redesign",
        "blocked_route_hash_preflight",
        "nested_search_validation_split_required",
        "untouched_final_holdout_registry_required",
        "procedural_joint_null_required_for_search_procedure",
        "familywise_or_route_family_alpha_correction_required",
        "no_release_from_diagnostic_or_preview_only",
        "all_candidate_family_runtime_capital_live_flags_false",
    ]

    nested_validation_requirements = {
        "search_set": {
            "purpose": "allowed to explore within pre-registered route budget only",
            "may_influence_hypothesis": True,
            "may_influence_release": False,
        },
        "validation_set": {
            "purpose": "test pre-registered hypothesis after search is fixed",
            "may_influence_hypothesis": False,
            "may_influence_release": False,
        },
        "untouched_final_holdout": {
            "purpose": "single-use final examination after full governance chain passes",
            "may_influence_hypothesis": False,
            "may_be_reused": False,
            "required_before_any_candidate_release": True,
        },
    }

    route_budget_rules = {
        "strategy_search_allowed_now": False,
        "methodology_repair_allowed_now": True,
        "default_new_route_budget": 0,
        "redesign_budget_requires_manual_governance_contract": True,
        "promising_vault_redesign_budget_requires": [
            "new_route_hash",
            "material_difference_report",
            "explicit alpha allocation",
            "nested validation plan",
            "untouched holdout plan",
            "procedural null plan",
        ],
        "budget_spend_events": [
            "route_family_created",
            "feature_family_scanned",
            "threshold_grid_scanned",
            "axis_family_scanned",
            "null_model_family_added",
            "evaluator_or_deep_validation_run",
        ],
    }

    alpha_policy = {
        "familywise_alpha": 0.05,
        "diagnostic_alpha_source": "global_multiple_testing_ledger_v1",
        "effective_comparison_count": ledger.get("global_testing_pressure", {}).get("effective_comparison_count"),
        "diagnostic_alpha_after_pressure": ledger.get("global_testing_pressure", {}).get("diagnostic_alpha_after_pressure"),
        "future_alpha_must_be_allocated_before_run": True,
        "post_hoc_alpha_allocation_allowed": False,
        "procedural_null_p_value_required": True,
        "single_axis_null_not_sufficient_after_search": True,
    }

    return {
        "plugin_key": PLUGIN_KEY,
        "plugin_type": "METHODOLOGY_ONLY_PRE_REGISTERED_RESEARCH_REDESIGN_GOVERNANCE",
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "strict_policy_key": STRICT_POLICY_KEY,
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "ledger_status": ledger.get("ledger_status"),
        "research_budget_status": budget.get("research_budget_status"),
        "anti_overfitting_state_status": anti_overfit.get("state_status"),
        "vault_status": vault.get("vault_status"),
        "lesson_count": len(lessons),
        "blocked_route_count": len(blocked_routes),
        "vault_item_count": len(vault_items),
        "governance_requirements": governance_requirements,
        "nested_validation_requirements": nested_validation_requirements,
        "route_budget_rules": route_budget_rules,
        "alpha_policy": alpha_policy,
        "forbidden_actions": [
            "strategy_search_without_budget",
            "post_hoc_threshold_selection",
            "post_hoc_feature_selection_without_accounting",
            "single_axis_null_after_multi_axis_search",
            "same_route_hash_reuse",
            "untouched_holdout_peeking",
            "candidate_generation",
            "candidate_contract",
            "family_release",
            "runtime_touch",
            "capital_change",
            "active_paper",
            "live_trading",
            "real_orders",
        ],
        "required_runner_outputs": [
            "pre_registration_policy_validation_report",
            "holdout_governance_policy_validation_report",
            "route_budget_policy_validation_report",
            "promising_signal_vault_consumption_report",
            "global_alpha_accounting_readiness_report",
            "blocked_route_hash_preflight_report",
            "governance_gate_table",
            "methodology_repair_next_queue",
        ],
        **SAFETY_FLAGS,
    }


def build_contract_text(contract: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS PRE-REGISTERED RESEARCH REDESIGN + HOLDOUT GOVERNANCE CONTRACT v1")
    lines.append("=" * 100)

    for key in [
        "contract_status",
        "allowed_scope",
        "next_action",
        "contract_id",
        "contract_hash",
        "route_hash",
        "research_key",
        "direction_queue_key",
        "plugin_key",
        "strategy_search_allowed_now",
        "methodology_repair_allowed_now",
        "vault_item_count",
        "blocked_route_count",
        "lesson_count",
        "next_module",
    ]:
        lines.append(f"{key}: {contract.get(key)}")

    lines.append("")
    lines.append("GOVERNANCE REQUIREMENTS")
    lines.append("-" * 100)
    for item in contract.get("governance_requirements", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("ROUTE BUDGET RULES")
    lines.append("-" * 100)
    lines.append(json.dumps(contract.get("route_budget_rules", {}), indent=2, ensure_ascii=False))

    lines.append("")
    lines.append("NESTED VALIDATION REQUIREMENTS")
    lines.append("-" * 100)
    lines.append(json.dumps(contract.get("nested_validation_requirements", {}), indent=2, ensure_ascii=False))

    lines.append("")
    lines.append("ALPHA POLICY")
    lines.append("-" * 100)
    lines.append(json.dumps(contract.get("alpha_policy", {}), indent=2, ensure_ascii=False))

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        lines.append(f"{key}: {value}")

    return "\n".join(lines)


def build_summary_text(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS PRE-REGISTERED RESEARCH REDESIGN CONTRACT BUILDER v1")
    lines.append("=" * 100)

    for key in [
        "builder_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "contract_id",
        "contract_hash",
        "route_hash",
        "research_key",
        "direction_queue_key",
        "plugin_key",
        "strategy_search_allowed_now",
        "methodology_repair_allowed_now",
        "vault_item_count",
        "blocked_route_count",
        "lesson_count",
        "next_module",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("CORE DECISION")
    lines.append("-" * 100)
    lines.append("No new strategy search is allowed.")
    lines.append("The only allowed direction is methodology/governance repair.")
    lines.append("Promising-but-unvalidated ideas are preserved, not deleted.")
    lines.append("Any future redesign must be pre-registered and budgeted before execution.")

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
        "repo_plugin_json",
        "repo_contract_json",
        "repo_contract_txt",
        "holdout_governance_policy_json",
        "pre_registration_policy_json",
        "route_budget_allocation_policy_json",
        "untouched_holdout_registry_stub_json",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS PRE-REGISTERED RESEARCH REDESIGN CONTRACT BUILDER v1")
    print("=" * 100)
    print(f"builder_status: {result.get('builder_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"contract_id: {result.get('contract_id')}")
    print(f"contract_hash: {result.get('contract_hash')}")
    print(f"route_hash: {result.get('route_hash')}")
    print(f"research_key: {result.get('research_key')}")
    print(f"direction_queue_key: {result.get('direction_queue_key')}")
    print(f"plugin_key: {result.get('plugin_key')}")
    print(f"strategy_search_allowed_now: {result.get('strategy_search_allowed_now')}")
    print(f"methodology_repair_allowed_now: {result.get('methodology_repair_allowed_now')}")
    print(f"vault_item_count: {result.get('vault_item_count')}")
    print(f"blocked_route_count: {result.get('blocked_route_count')}")
    print(f"lesson_count: {result.get('lesson_count')}")
    print(f"next_module: {result.get('next_module')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        print(f"{key}: {value}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"CONTRACT: {result.get('repo_contract_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PLUGIN_DIR.mkdir(parents=True, exist_ok=True)
    CONTRACT_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)

    ledger = load_json(LEDGER_JSON, {})
    budget = load_json(RESEARCH_BUDGET_POLICY_JSON, {})
    vault = load_json(PROMISING_SIGNAL_VAULT_JSON, {})
    anti_overfit = load_json(ANTI_OVERFITTING_STATE_JSON, {})
    joint_state = load_json(JOINT_VALIDATION_STATE_JSON, {})
    framework_status = load_json(FRAMEWORK_STATUS_JSON, {})
    lesson_index = load_json(LESSON_INDEX_JSON, {})
    blocklist = load_json(BLOCKLIST_JSON, {})

    lessons = extract_lessons(lesson_index)
    blocked_routes = extract_blocked_routes(blocklist)
    vault_items = extract_vault_items(vault)

    prerequisites = {
        "ledger_active": ledger.get("ledger_status") == "GLOBAL_MULTIPLE_TESTING_LEDGER_ACTIVE_RESEARCH_LOCKED",
        "budget_active": budget.get("policy_status") == "RESEARCH_BUDGET_POLICY_ACTIVE_METHODOLOGY_ONLY",
        "strategy_search_locked": budget.get("research_budget_status") == "STRATEGY_SEARCH_BUDGET_LOCKED_UNTIL_GOVERNANCE_REPAIR",
        "vault_active": vault.get("vault_status") == "PROMISING_SIGNAL_VAULT_ACTIVE_RELEASE_BLOCKED",
        "anti_overfit_active": anti_overfit.get("state_status") == "ANTI_OVERFITTING_GOVERNANCE_ACTIVE_RESEARCH_REPAIR_REQUIRED",
        "joint_null_failed": joint_state.get("joint_null_policy_gate_pass") is False,
        "framework_policy_locked": framework_status.get("panel_status") == "FRAMEWORK_STATUS_PANEL_READY_POLICY_LOCKED_NO_ACTUAL_SIGNAL",
        "vault_has_item": len(vault_items) >= 1,
        "blocked_routes_exist": len(blocked_routes) >= 1,
        "lessons_exist": len(lessons) >= 1,
    }

    prerequisite_pass = all(prerequisites.values())

    plugin_config = build_plugin_config(
        ledger=ledger,
        budget=budget,
        vault=vault,
        anti_overfit=anti_overfit,
        lessons=lessons,
        blocked_routes=blocked_routes,
    )

    route_hash_payload = {
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "plugin_key": PLUGIN_KEY,
        "ledger_status": ledger.get("ledger_status"),
        "budget_status": budget.get("research_budget_status"),
        "vault_status": vault.get("vault_status"),
        "anti_overfit_status": anti_overfit.get("state_status"),
        "strict_policy_key": STRICT_POLICY_KEY,
        "governance_requirements": plugin_config["governance_requirements"],
        "strategy_search_allowed_now": False,
        "methodology_repair_allowed_now": True,
    }

    route_hash = stable_hash(route_hash_payload)
    contract_hash = stable_hash({
        "route_hash": route_hash,
        "research_key": RESEARCH_KEY,
        "plugin_key": PLUGIN_KEY,
        "lesson_count": len(lessons),
        "blocked_route_count": len(blocked_routes),
        "vault_item_count": len(vault_items),
    })

    contract_id = f"PRE_REGISTERED_RESEARCH_REDESIGN_CONTRACT_V1_{contract_hash}_{timestamp_compact()}"

    if prerequisite_pass:
        builder_status = "PRE_REGISTERED_RESEARCH_REDESIGN_CONTRACT_READY"
        severity = "ATTENTION"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        next_action = "BUILD_PRE_REGISTERED_RESEARCH_REDESIGN_GOVERNANCE_RUNNER"
        reason = (
            "global ledger, research budget policy, promising vault, and anti-overfitting governance are active; "
            "methodology-only redesign governance contract is ready; strategy search remains locked"
        )
        next_module = NEXT_MODULE
        return_code = 0
    else:
        builder_status = "PRE_REGISTERED_RESEARCH_REDESIGN_CONTRACT_BLOCKED_PREREQUISITE_NOT_MET"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_PRE_REGISTERED_RESEARCH_REDESIGN_PREREQUISITES_NO_RELEASE"
        reason = f"prerequisites={prerequisites}"
        next_module = None
        return_code = 2

    holdout_governance_policy = {
        "policy_name": "edge_factory_os_holdout_governance_policy_v1",
        "policy_status": "HOLDOUT_GOVERNANCE_POLICY_DRAFT_READY",
        "created_at_utc": utc_now_iso(),
        "untouched_final_holdout_required": True,
        "holdout_peeking_allowed": False,
        "holdout_reuse_allowed": False,
        "holdout_must_be_registered_before_research": True,
        "holdout_may_influence_hypothesis": False,
        "holdout_may_influence_release_only_after_full_governance_pass": True,
        "required_split_layers": [
            "search_set",
            "validation_set",
            "untouched_final_holdout",
        ],
        "release_without_holdout_policy_allowed": False,
        **SAFETY_FLAGS,
    }

    pre_registration_policy = {
        "policy_name": "edge_factory_os_pre_registration_policy_v1",
        "policy_status": "PRE_REGISTRATION_POLICY_DRAFT_READY",
        "created_at_utc": utc_now_iso(),
        "all_future_research_must_be_pre_registered": True,
        "contract_mutation_after_start_invalidates_route": True,
        "feature_family_must_be_declared_before_run": True,
        "threshold_grid_must_be_declared_before_run": True,
        "null_models_must_be_declared_before_run": True,
        "axis_family_must_be_declared_before_run": True,
        "success_criteria_must_be_declared_before_run": True,
        "post_hoc_success_criteria_allowed": False,
        "release_without_pre_registration_allowed": False,
        **SAFETY_FLAGS,
    }

    route_budget_allocation_policy = {
        "policy_name": "edge_factory_os_route_budget_allocation_policy_v1",
        "policy_status": "ROUTE_BUDGET_ALLOCATION_POLICY_DRAFT_READY",
        "created_at_utc": utc_now_iso(),
        "strategy_search_allowed_now": False,
        "methodology_repair_allowed_now": True,
        "new_strategy_route_budget_now": 0,
        "budget_required_before_any_future_search": True,
        "alpha_required_before_any_future_search": True,
        "post_hoc_budget_allocation_allowed": False,
        "budget_spend_events": plugin_config["route_budget_rules"]["budget_spend_events"],
        "promising_vault_redesign_requires_budget": True,
        "release_without_budget_policy_allowed": False,
        **SAFETY_FLAGS,
    }

    untouched_holdout_registry_stub = {
        "registry_name": "edge_factory_os_untouched_holdout_registry_stub_v1",
        "registry_status": "UNTOUCHED_HOLDOUT_REGISTRY_STUB_READY_NOT_POPULATED",
        "created_at_utc": utc_now_iso(),
        "purpose": "Defines required registry schema. It does not expose or select final holdout yet.",
        "holdout_selected": False,
        "holdout_peeked": False,
        "holdout_usable_now": False,
        "required_fields_for_future_registry": [
            "holdout_id",
            "selection_time_utc",
            "selection_method",
            "time_window_or_symbol_split",
            "forbidden_access_until_gate",
            "single_use_policy",
            "hash_of_holdout_definition",
            "access_log",
        ],
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
    }

    contract = {
        "contract_name": "edge_factory_os_pre_registered_research_redesign_contract_v1",
        "created_at_utc": utc_now_iso(),
        "contract_status": "PRE_REGISTERED_RESEARCH_REDESIGN_CONTRACT_READY" if prerequisite_pass else "PRE_REGISTERED_RESEARCH_REDESIGN_CONTRACT_BLOCKED",
        "contract_id": contract_id if prerequisite_pass else None,
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "route_hash_payload": route_hash_payload,
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "plugin_key": PLUGIN_KEY,
        "strict_policy_key": STRICT_POLICY_KEY,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "next_module": next_module,
        "strategy_search_allowed_now": False,
        "methodology_repair_allowed_now": True,
        "vault_item_count": len(vault_items),
        "blocked_route_count": len(blocked_routes),
        "lesson_count": len(lessons),
        "governance_requirements": plugin_config["governance_requirements"],
        "nested_validation_requirements": plugin_config["nested_validation_requirements"],
        "route_budget_rules": plugin_config["route_budget_rules"],
        "alpha_policy": plugin_config["alpha_policy"],
        "forbidden_actions": plugin_config["forbidden_actions"],
        "required_runner_outputs": plugin_config["required_runner_outputs"],
        "source_artifacts": {
            "ledger_json": str(LEDGER_JSON),
            "research_budget_policy_json": str(RESEARCH_BUDGET_POLICY_JSON),
            "promising_signal_vault_json": str(PROMISING_SIGNAL_VAULT_JSON),
            "anti_overfitting_state_json": str(ANTI_OVERFITTING_STATE_JSON),
            "joint_validation_state_json": str(JOINT_VALIDATION_STATE_JSON),
            "framework_status_json": str(FRAMEWORK_STATUS_JSON),
            "lesson_index_json": str(LESSON_INDEX_JSON),
            "blocklist_json": str(BLOCKLIST_JSON),
        },
        "release_gate_feed": {
            "PRE_REGISTERED_RESEARCH_REDESIGN_CONTRACT_READY": prerequisite_pass,
            "STRATEGY_SEARCH_ALLOWED_NOW": False,
            "METHODOLOGY_REPAIR_ALLOWED_NOW": True,
            "PROMISING_SIGNAL_VAULT_CONSUMED": True,
            "GLOBAL_LEDGER_CONSUMED": True,
            "RESEARCH_BUDGET_POLICY_CONSUMED": True,
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

    write_json(REPO_PLUGIN_JSON, plugin_config)
    write_json(REPO_CONTRACT_JSON, contract)
    write_text(REPO_CONTRACT_TXT, build_contract_text(contract))
    write_json(HOLDOUT_GOVERNANCE_POLICY_JSON, holdout_governance_policy)
    write_json(PRE_REGISTRATION_POLICY_JSON, pre_registration_policy)
    write_json(ROUTE_BUDGET_ALLOCATION_POLICY_JSON, route_budget_allocation_policy)
    write_json(UNTOUCHED_HOLDOUT_REGISTRY_STUB_JSON, untouched_holdout_registry_stub)

    result = {
        "builder_name": "edge_factory_os_pre_registered_research_redesign_contract_builder_v1",
        "created_at_utc": utc_now_iso(),
        "builder_status": builder_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "contract_id": contract.get("contract_id"),
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "plugin_key": PLUGIN_KEY,
        "strategy_search_allowed_now": False,
        "methodology_repair_allowed_now": True,
        "vault_item_count": len(vault_items),
        "blocked_route_count": len(blocked_routes),
        "lesson_count": len(lessons),
        "prerequisites": prerequisites,
        "next_module": next_module,
        "contract": contract,
        "plugin_config": plugin_config,
        "holdout_governance_policy": holdout_governance_policy,
        "pre_registration_policy": pre_registration_policy,
        "route_budget_allocation_policy": route_budget_allocation_policy,
        "untouched_holdout_registry_stub": untouched_holdout_registry_stub,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "repo_plugin_json": str(REPO_PLUGIN_JSON),
        "repo_contract_json": str(REPO_CONTRACT_JSON),
        "repo_contract_txt": str(REPO_CONTRACT_TXT),
        "holdout_governance_policy_json": str(HOLDOUT_GOVERNANCE_POLICY_JSON),
        "pre_registration_policy_json": str(PRE_REGISTRATION_POLICY_JSON),
        "route_budget_allocation_policy_json": str(ROUTE_BUDGET_ALLOCATION_POLICY_JSON),
        "untouched_holdout_registry_stub_json": str(UNTOUCHED_HOLDOUT_REGISTRY_STUB_JSON),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_summary_text(result))
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
