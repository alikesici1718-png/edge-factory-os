#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Global Multiple Testing Ledger + Research Budget Policy v1

Purpose:
- Consume Joint Null Distribution Validator v1.
- Record global multiple-testing / route exploration pressure.
- Mark current market-state route as release-blocked after procedural null failure.
- Preserve useful-but-invalidated ideas in Promising Signal Vault.
- Add research budget policy: no further strategy search until methodology repair is active.
- Keep candidate/family/runtime/capital/active-paper/live/real-order actions blocked.

This module does NOT:
- run new research
- generate candidates
- create candidate contracts
- release families
- touch runtime
- change capital
- start active paper
- enable live trading
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

JOINT_VALIDATOR_JSON = (
    BASE_DIR
    / "edge_factory_os_joint_null_distribution_validator"
    / "joint_null_distribution_validator_latest.json"
)

JOINT_VALIDATION_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "joint_null_distribution_validation_state_v1.json"
)

MARKET_RUNNER_JSON = (
    BASE_DIR
    / "edge_factory_os_market_state_transition_runner"
    / "market_state_transition_runner_latest.json"
)

MARKET_CONTRACT_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "contracts"
    / "market_state_transition_contract_v1.json"
)

FRAMEWORK_STATUS_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "status"
    / "framework_status_panel_v1.json"
)

RESEARCH_GATE_POLICY_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_enforcement_policy_v1.json"
)

TRUE_SOURCE_PANEL_NULL_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "true_source_panel_empirical_null_baseline_state_v1.json"
)

SOURCE_ANOMALY_DEEP_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "source_panel_anomaly_deep_validation_state_v1.json"
)

LESSON_DIR = BASE_DIR / "edge_factory_os_lesson_memory"
LESSON_INDEX_JSON = LESSON_DIR / "lesson_memory_index.json"
BLOCKLIST_JSON = LESSON_DIR / "candidate_route_blocklist.json"

FRAMEWORK_POLICY_DIR = REPO_DIR / "edge_factory_os_framework" / "policies"
LEDGER_JSON = FRAMEWORK_POLICY_DIR / "global_multiple_testing_ledger_v1.json"
RESEARCH_BUDGET_POLICY_JSON = FRAMEWORK_POLICY_DIR / "research_budget_policy_v1.json"
PROMISING_SIGNAL_VAULT_JSON = FRAMEWORK_POLICY_DIR / "promising_signal_vault_v1.json"
ANTI_OVERFITTING_STATE_JSON = FRAMEWORK_POLICY_DIR / "anti_overfitting_governance_state_v1.json"

OUT_DIR = BASE_DIR / "edge_factory_os_global_multiple_testing_ledger_research_budget_policy"
OUT_JSON = OUT_DIR / "global_multiple_testing_ledger_research_budget_policy_latest.json"
OUT_TXT = OUT_DIR / "global_multiple_testing_ledger_research_budget_policy_latest.txt"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD7_01_PRE_REGISTERED_RESEARCH_REDESIGN_AND_HOLDOUT_GOVERNANCE"
NEXT_MODULE = "edge_factory_os_pre_registered_research_redesign_contract_builder_v1.py"

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


def append_blocklist_record(path: Path, block_record: Dict[str, Any]) -> Dict[str, Any]:
    obj = load_json(path, default={})

    if isinstance(obj, list):
        existing = {str(x.get("route_hash")) for x in obj if isinstance(x, dict)}
        if str(block_record["route_hash"]) not in existing:
            obj.append(block_record)
        write_json(path, obj)
        return {"append_mode": "list_root", "path": str(path)}

    if not isinstance(obj, dict):
        obj = {}

    blocked = obj.get("blocked_routes")
    if not isinstance(blocked, list):
        blocked = []

    existing = {str(x.get("route_hash")) for x in blocked if isinstance(x, dict)}
    if str(block_record["route_hash"]) not in existing:
        blocked.append(block_record)

    obj["blocked_routes"] = blocked
    obj["updated_at_utc"] = utc_now_iso()
    write_json(path, obj)
    return {"append_mode": "dict_blocked_routes", "path": str(path)}


def append_lesson_record(path: Path, lesson_record: Dict[str, Any]) -> Dict[str, Any]:
    obj = load_json(path, default={})

    if isinstance(obj, list):
        existing = {str(x.get("lesson_id")) for x in obj if isinstance(x, dict)}
        if str(lesson_record["lesson_id"]) not in existing:
            obj.append(lesson_record)
        write_json(path, obj)
        return {"append_mode": "list_root", "path": str(path)}

    if not isinstance(obj, dict):
        obj = {}

    lessons = obj.get("lessons")
    if not isinstance(lessons, list):
        lessons = []

    existing = {str(x.get("lesson_id")) for x in lessons if isinstance(x, dict)}
    if str(lesson_record["lesson_id"]) not in existing:
        lessons.append(lesson_record)

    obj["lessons"] = lessons
    obj["updated_at_utc"] = utc_now_iso()
    write_json(path, obj)
    return {"append_mode": "dict_lessons", "path": str(path)}


def vault_items(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get("vault_items"), list):
        return [x for x in obj["vault_items"] if isinstance(x, dict)]
    return []


def append_vault_item(path: Path, item: Dict[str, Any]) -> Dict[str, Any]:
    obj = load_json(path, default={})
    if not isinstance(obj, dict):
        obj = {}

    items = obj.get("vault_items")
    if not isinstance(items, list):
        items = []

    existing = {str(x.get("vault_item_id")) for x in items if isinstance(x, dict)}
    if str(item["vault_item_id"]) not in existing:
        items.append(item)

    obj["vault_status"] = "PROMISING_SIGNAL_VAULT_ACTIVE_RELEASE_BLOCKED"
    obj["updated_at_utc"] = utc_now_iso()
    obj["vault_items"] = items
    write_json(path, obj)
    return {"append_mode": "vault_items", "path": str(path)}


def build_text(result: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS GLOBAL MULTIPLE TESTING LEDGER + RESEARCH BUDGET POLICY v1")
    lines.append("=" * 100)

    for key in [
        "policy_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "joint_null_validator_status",
        "market_state_route_status",
        "market_state_release_status",
        "promising_signal_vault_status",
        "research_budget_status",
        "global_multiple_testing_pressure_status",
        "lesson_count",
        "blocked_route_count_before",
        "blocked_route_count_after",
        "vault_item_count_after",
        "observed_transition_axis_count",
        "observed_strict_12_transition_preview_count",
        "joint_null_max_p_count",
        "joint_null_max_p_joint",
        "effective_comparison_count",
        "familywise_alpha",
        "diagnostic_alpha_after_pressure",
        "next_recommended_research_key",
        "next_module",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("CORE DECISION")
    lines.append("-" * 100)
    lines.append("Market-state transition preview is BLOCKED_FOR_RELEASE because procedural/joint null failed.")
    lines.append("The idea is NOT deleted. It is preserved as PROMISING_BUT_UNVALIDATED_STRUCTURE_HINT in Promising Signal Vault.")
    lines.append("Further strategy search is blocked until pre-registration, nested/untouched holdout, and global testing budget governance exist.")

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
        "ledger_json",
        "research_budget_policy_json",
        "promising_signal_vault_json",
        "anti_overfitting_state_json",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS GLOBAL MULTIPLE TESTING LEDGER + RESEARCH BUDGET POLICY v1")
    print("=" * 100)
    print(f"policy_status: {result.get('policy_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"joint_null_validator_status: {result.get('joint_null_validator_status')}")
    print(f"market_state_route_status: {result.get('market_state_route_status')}")
    print(f"market_state_release_status: {result.get('market_state_release_status')}")
    print(f"promising_signal_vault_status: {result.get('promising_signal_vault_status')}")
    print(f"research_budget_status: {result.get('research_budget_status')}")
    print(f"global_multiple_testing_pressure_status: {result.get('global_multiple_testing_pressure_status')}")
    print(f"lesson_count: {result.get('lesson_count')}")
    print(f"blocked_route_count_before: {result.get('blocked_route_count_before')}")
    print(f"blocked_route_count_after: {result.get('blocked_route_count_after')}")
    print(f"vault_item_count_after: {result.get('vault_item_count_after')}")
    print(f"observed_transition_axis_count: {result.get('observed_transition_axis_count')}")
    print(f"observed_strict_12_transition_preview_count: {result.get('observed_strict_12_transition_preview_count')}")
    print(f"joint_null_max_p_count: {result.get('joint_null_max_p_count')}")
    print(f"joint_null_max_p_joint: {result.get('joint_null_max_p_joint')}")
    print(f"effective_comparison_count: {result.get('effective_comparison_count')}")
    print(f"familywise_alpha: {result.get('familywise_alpha')}")
    print(f"diagnostic_alpha_after_pressure: {result.get('diagnostic_alpha_after_pressure')}")
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
    print(f"LEDGER: {result.get('ledger_json')}")
    print(f"BUDGET: {result.get('research_budget_policy_json')}")
    print(f"VAULT : {result.get('promising_signal_vault_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FRAMEWORK_POLICY_DIR.mkdir(parents=True, exist_ok=True)
    LESSON_DIR.mkdir(parents=True, exist_ok=True)

    joint = load_json(JOINT_VALIDATOR_JSON, {})
    joint_state = load_json(JOINT_VALIDATION_STATE_JSON, {})
    market_runner = load_json(MARKET_RUNNER_JSON, {})
    market_contract = load_json(MARKET_CONTRACT_JSON, {})
    framework_status = load_json(FRAMEWORK_STATUS_JSON, {})
    research_gate_policy = load_json(RESEARCH_GATE_POLICY_JSON, {})
    true_null_state = load_json(TRUE_SOURCE_PANEL_NULL_STATE_JSON, {})
    anomaly_deep_state = load_json(SOURCE_ANOMALY_DEEP_STATE_JSON, {})

    lesson_index = load_json(LESSON_INDEX_JSON, {})
    blocklist_obj = load_json(BLOCKLIST_JSON, {})
    vault_obj_before = load_json(PROMISING_SIGNAL_VAULT_JSON, {})

    lessons = extract_lessons(lesson_index)
    blocked_before = extract_blocked_routes(blocklist_obj)

    joint_fail = (
        joint.get("validator_status") == "JOINT_NULL_DISTRIBUTION_VALIDATOR_FAIL_RESEARCH_METHODOLOGY_REPAIR_REQUIRED"
        and joint.get("joint_null_policy_gate_pass") is False
    )

    market_route_hash = market_contract.get("route_hash") or market_runner.get("route_hash")
    market_contract_id = market_contract.get("contract_id") or market_runner.get("contract_id")
    market_research_key = market_contract.get("research_key") or market_runner.get("research_key")

    observed_axis_count = int(joint.get("observed_transition_axis_count") or market_runner.get("transition_axis_count") or 0)
    observed_preview_count = int(joint.get("observed_strict_12_transition_preview_count") or market_runner.get("strict_12_transition_preview_count") or 0)
    max_p_count = float(joint.get("max_p_ge_observed_preview_count") or 1.0)
    max_p_joint = float(joint.get("max_p_joint_ge_count_and_score") or 1.0)

    blocked_count_before = len(blocked_before)
    lesson_count = len(lessons)

    effective_comparison_count = max(1, observed_axis_count * max(1, blocked_count_before + 1))
    familywise_alpha = 0.05
    diagnostic_alpha_after_pressure = familywise_alpha / effective_comparison_count

    vault_payload = {
        "route_hash": market_route_hash,
        "contract_id": market_contract_id,
        "research_key": market_research_key,
        "observed_axis_count": observed_axis_count,
        "observed_preview_count": observed_preview_count,
        "max_p_count": max_p_count,
        "max_p_joint": max_p_joint,
    }
    vault_item_id = f"PROMISING_STRUCTURE_HINT_{stable_hash(vault_payload)}"

    vault_item = {
        "vault_item_id": vault_item_id,
        "created_at_utc": utc_now_iso(),
        "vault_class": "PROMISING_BUT_UNVALIDATED_STRUCTURE_HINT",
        "release_status": "RELEASE_BLOCKED",
        "preservation_status": "PRESERVED_NOT_DELETED",
        "source_route_hash": market_route_hash,
        "source_contract_id": market_contract_id,
        "source_research_key": market_research_key,
        "source_runner_status": market_runner.get("runner_status"),
        "observed_transition_axis_count": observed_axis_count,
        "observed_strict_12_transition_preview_count": observed_preview_count,
        "observed_best_total_transition_score": joint.get("observed_best_total_transition_score") or market_runner.get("observed_best_total_transition_score"),
        "joint_null_status": joint.get("validator_status"),
        "joint_null_max_p_ge_observed_preview_count": max_p_count,
        "joint_null_max_p_joint_ge_count_and_score": max_p_joint,
        "why_preserved": (
            "Market-state transitions may contain useful structural information, "
            "but current search procedure failed procedural/joint null and cannot be used for release."
        ),
        "why_blocked_for_release": (
            "Under full procedural null, the same search finds >= observed preview count and score too often. "
            "Current result is consistent with search-process false positives."
        ),
        "allowed_future_use": [
            "hypothesis memory only",
            "materially different pre-registered redesign",
            "nested validation",
            "untouched final holdout",
            "global testing budget accounting",
            "procedural null re-validation",
        ],
        "forbidden_future_use": [
            "direct promotion",
            "candidate generation",
            "candidate contract",
            "family release",
            "runtime touch",
            "capital change",
            "active paper",
            "live trading",
            "real orders",
            "same route hash reuse",
        ],
        "retest_requirements": [
            "fresh pre-registered contract",
            "narrower state-transition hypothesis",
            "route budget allocated before test",
            "nested search/validation split",
            "untouched final holdout",
            "global family-wise correction",
            "joint/procedural null pass",
            "candidate/family/runtime/capital/live still blocked",
        ],
        **SAFETY_FLAGS,
    }

    lesson_payload = {
        "route_hash": market_route_hash,
        "joint_status": joint.get("validator_status"),
        "p_count": max_p_count,
        "p_joint": max_p_joint,
        "observed_axis_count": observed_axis_count,
        "observed_preview_count": observed_preview_count,
    }
    lesson_id = f"LESSON_MARKET_STATE_PROCEDURAL_NULL_FAILED_{stable_hash(lesson_payload)}"

    lesson_record = {
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "lesson_type": "PROCEDURAL_NULL_FAILED_BUT_STRUCTURE_HINT_PRESERVED",
        "source_route_hash": market_route_hash,
        "source_contract_id": market_contract_id,
        "source_research_key": market_research_key,
        "validator_status": joint.get("validator_status"),
        "failed_gate_keys": joint.get("failed_gate_keys"),
        "observed_transition_axis_count": observed_axis_count,
        "observed_strict_12_transition_preview_count": observed_preview_count,
        "joint_null_max_p_ge_observed_preview_count": max_p_count,
        "joint_null_max_p_joint_ge_count_and_score": max_p_joint,
        "release_allowed": False,
        "vault_item_id": vault_item_id,
        "lesson": (
            "Local true-null/negative-control gates are insufficient after broad route/axis search. "
            "Future research must use global multiple-testing ledger, research budget, pre-registration, "
            "nested validation, untouched holdout, and procedural null validation."
        ),
        **SAFETY_FLAGS,
    }

    block_record = {
        "route_hash": market_route_hash,
        "lesson_id": lesson_id,
        "vault_item_id": vault_item_id,
        "created_at_utc": utc_now_iso(),
        "blocked_reason": "MARKET_STATE_TRANSITION_PROCEDURAL_JOINT_NULL_FAILED",
        "research_branch": "OUTCOME_AGNOSTIC_MARKET_STATE_TRANSITION_SEARCH",
        "research_key": market_research_key,
        "contract_id": market_contract_id,
        "contract_hash": market_contract.get("contract_hash"),
        "policy_hash": market_contract.get("policy_hash") or market_runner.get("policy_hash"),
        "failed_gate_keys": joint.get("failed_gate_keys"),
        "max_p_ge_observed_preview_count": max_p_count,
        "max_p_joint_ge_count_and_score": max_p_joint,
        "route_closed_for_release": True,
        "preserve_in_promising_vault": True,
        "redesign_allowed_under_new_contract": True,
        "plugin_expansion_allowed": False,
        "release_allowed": False,
        "reopen_requirements": [
            "must not reuse same route hash",
            "must consume global multiple-testing ledger",
            "must consume promising signal vault",
            "must allocate research budget before running",
            "must be pre-registered",
            "must use nested validation",
            "must reserve untouched final holdout",
            "must pass procedural/joint null after global correction",
            "must keep candidate/family/runtime/capital/live blocked",
        ],
    }

    if joint_fail and market_route_hash:
        lesson_append_status = append_lesson_record(LESSON_INDEX_JSON, lesson_record)
        block_append_status = append_blocklist_record(BLOCKLIST_JSON, block_record)
        vault_append_status = append_vault_item(PROMISING_SIGNAL_VAULT_JSON, vault_item)
    else:
        lesson_append_status = {"skipped": True, "reason": "joint_fail_or_market_route_hash_missing"}
        block_append_status = {"skipped": True, "reason": "joint_fail_or_market_route_hash_missing"}
        vault_append_status = {"skipped": True, "reason": "joint_fail_or_market_route_hash_missing"}

    blocklist_after = load_json(BLOCKLIST_JSON, {})
    vault_after = load_json(PROMISING_SIGNAL_VAULT_JSON, {})
    blocked_after = extract_blocked_routes(blocklist_after)
    vault_after_items = vault_items(vault_after)

    ledger = {
        "ledger_name": "edge_factory_os_global_multiple_testing_ledger_v1",
        "ledger_status": "GLOBAL_MULTIPLE_TESTING_LEDGER_ACTIVE_RESEARCH_LOCKED",
        "created_at_utc": utc_now_iso(),
        "strict_policy_key": STRICT_POLICY_KEY,
        "current_global_assessment": "RESEARCH_METHODOLOGY_REPAIR_REQUIRED",
        "lesson_count": lesson_count,
        "blocked_route_count": len(blocked_after),
        "vault_item_count": len(vault_after_items),
        "latest_invalidated_route": {
            "route_hash": market_route_hash,
            "contract_id": market_contract_id,
            "research_key": market_research_key,
            "invalidated_by": "JOINT_NULL_DISTRIBUTION_VALIDATOR_V1",
            "max_p_ge_observed_preview_count": max_p_count,
            "max_p_joint_ge_count_and_score": max_p_joint,
            "blocked_for_release": True,
            "preserved_in_vault": True,
            "vault_item_id": vault_item_id,
        },
        "global_testing_pressure": {
            "observed_transition_axis_count": observed_axis_count,
            "blocked_route_count_before": blocked_count_before,
            "effective_comparison_count": effective_comparison_count,
            "familywise_alpha": familywise_alpha,
            "diagnostic_alpha_after_pressure": diagnostic_alpha_after_pressure,
            "note": "Diagnostic only. Future modules must use formal route-family accounting before new strategy search.",
        },
        "rules": {
            "same_route_hash_reuse_allowed": False,
            "release_without_global_ledger_allowed": False,
            "release_without_research_budget_allowed": False,
            "release_without_pre_registration_allowed": False,
            "release_without_nested_validation_allowed": False,
            "release_without_untouched_holdout_allowed": False,
            "release_without_procedural_null_allowed": False,
            "promising_but_unvalidated_should_be_preserved": True,
            "failed_does_not_mean_delete": True,
        },
        "source_paths": {
            "joint_validator_json": str(JOINT_VALIDATOR_JSON),
            "joint_validation_state_json": str(JOINT_VALIDATION_STATE_JSON),
            "market_runner_json": str(MARKET_RUNNER_JSON),
            "market_contract_json": str(MARKET_CONTRACT_JSON),
            "lesson_index_json": str(LESSON_INDEX_JSON),
            "blocklist_json": str(BLOCKLIST_JSON),
            "promising_signal_vault_json": str(PROMISING_SIGNAL_VAULT_JSON),
        },
        **SAFETY_FLAGS,
    }

    research_budget_policy = {
        "policy_name": "edge_factory_os_research_budget_policy_v1",
        "policy_status": "RESEARCH_BUDGET_POLICY_ACTIVE_METHODOLOGY_ONLY",
        "created_at_utc": utc_now_iso(),
        "research_budget_status": "STRATEGY_SEARCH_BUDGET_LOCKED_UNTIL_GOVERNANCE_REPAIR",
        "reason": "Procedural/joint null failed with max_p_count=1.0 and max_p_joint=1.0 after 160-axis market-state search.",
        "allowed_scope_now": "METHODOLOGY_REPAIR_ONLY",
        "disallowed_until_repair": [
            "new broad strategy search",
            "market-state evaluator escalation",
            "candidate generation",
            "candidate contracts",
            "family release",
            "runtime touch",
            "capital change",
            "active paper",
            "live trading",
            "real orders",
        ],
        "allowed_next_modules": [
            NEXT_MODULE,
            "edge_factory_os_untouched_holdout_registry_builder_v1.py",
            "edge_factory_os_nested_validation_policy_builder_v1.py",
            "edge_factory_os_global_route_family_alpha_accountant_v1.py",
        ],
        "budget_rules": {
            "all_future_research_must_pre_register_contract": True,
            "all_future_research_must_have_budget_allocation_before_run": True,
            "broad_axis_search_requires_harsher_alpha": True,
            "procedural_null_required_for_search_procedures": True,
            "promising_signal_vault_required_before_blocking_promising_hypothesis": True,
            "nested_validation_required": True,
            "untouched_final_holdout_required": True,
            "same_route_hash_reuse_allowed": False,
        },
        "release_gate_feed": {
            "RESEARCH_BUDGET_POLICY_ACTIVE": True,
            "STRATEGY_SEARCH_ALLOWED_NOW": False,
            "METHODOLOGY_REPAIR_ALLOWED_NOW": True,
            "CANDIDATE_GENERATION_ALLOWED_FROM_THIS_POLICY": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_THIS_POLICY": False,
            "FAMILY_RELEASE_ALLOWED_FROM_THIS_POLICY": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_THIS_POLICY": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_THIS_POLICY": False,
            "ACTIVE_PAPER_ALLOWED_FROM_THIS_POLICY": False,
            "LIVE_ALLOWED_FROM_THIS_POLICY": False,
            "REAL_ORDERS_ALLOWED_FROM_THIS_POLICY": False,
        },
        **SAFETY_FLAGS,
    }

    anti_overfitting_state = {
        "state_name": "edge_factory_os_anti_overfitting_governance_state_v1",
        "state_status": "ANTI_OVERFITTING_GOVERNANCE_ACTIVE_RESEARCH_REPAIR_REQUIRED",
        "created_at_utc": utc_now_iso(),
        "joint_null_failure_confirmed": joint_fail,
        "market_state_preview_validated": False,
        "market_state_route_blocked_for_release": True,
        "market_state_structure_hint_preserved": True,
        "promising_signal_vault_status": "ACTIVE",
        "global_multiple_testing_ledger_status": ledger["ledger_status"],
        "research_budget_policy_status": research_budget_policy["policy_status"],
        "next_recommended_research_key": NEXT_RESEARCH_KEY,
        "next_module": NEXT_MODULE,
        "release_allowed": False,
        **SAFETY_FLAGS,
    }

    write_json(LEDGER_JSON, ledger)
    write_json(RESEARCH_BUDGET_POLICY_JSON, research_budget_policy)
    write_json(ANTI_OVERFITTING_STATE_JSON, anti_overfitting_state)

    result = {
        "module_name": "edge_factory_os_global_multiple_testing_ledger_and_research_budget_policy_v1",
        "created_at_utc": utc_now_iso(),
        "policy_status": "GLOBAL_MULTIPLE_TESTING_LEDGER_AND_RESEARCH_BUDGET_POLICY_READY",
        "severity": "ATTENTION",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "next_action": "BUILD_PRE_REGISTERED_RESEARCH_REDESIGN_AND_HOLDOUT_GOVERNANCE_NO_RELEASE",
        "reason": (
            "Joint/procedural null failed; market-state route is release-blocked and preserved as promising-but-unvalidated. "
            "Future strategy research is locked until global ledger, budget, pre-registration, nested validation, and holdout governance are enforced."
        ),
        "joint_null_validator_status": joint.get("validator_status"),
        "market_state_route_status": "PROCEDURAL_NULL_FAILED_ROUTE_BLOCKED_FOR_RELEASE",
        "market_state_release_status": "RELEASE_BLOCKED",
        "promising_signal_vault_status": "PROMISING_SIGNAL_PRESERVED_NOT_DELETED",
        "research_budget_status": research_budget_policy["research_budget_status"],
        "global_multiple_testing_pressure_status": "HIGH_PRESSURE_REQUIRES_GOVERNANCE",
        "lesson_count": lesson_count,
        "blocked_route_count_before": blocked_count_before,
        "blocked_route_count_after": len(blocked_after),
        "vault_item_count_after": len(vault_after_items),
        "observed_transition_axis_count": observed_axis_count,
        "observed_strict_12_transition_preview_count": observed_preview_count,
        "joint_null_max_p_count": max_p_count,
        "joint_null_max_p_joint": max_p_joint,
        "effective_comparison_count": effective_comparison_count,
        "familywise_alpha": familywise_alpha,
        "diagnostic_alpha_after_pressure": diagnostic_alpha_after_pressure,
        "lesson_id": lesson_id,
        "vault_item_id": vault_item_id,
        "lesson_append_status": lesson_append_status,
        "block_append_status": block_append_status,
        "vault_append_status": vault_append_status,
        "next_recommended_research_key": NEXT_RESEARCH_KEY,
        "next_module": NEXT_MODULE,
        "ledger": ledger,
        "research_budget_policy": research_budget_policy,
        "anti_overfitting_state": anti_overfitting_state,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "ledger_json": str(LEDGER_JSON),
        "research_budget_policy_json": str(RESEARCH_BUDGET_POLICY_JSON),
        "promising_signal_vault_json": str(PROMISING_SIGNAL_VAULT_JSON),
        "anti_overfitting_state_json": str(ANTI_OVERFITTING_STATE_JSON),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text(result))
    print_summary(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
