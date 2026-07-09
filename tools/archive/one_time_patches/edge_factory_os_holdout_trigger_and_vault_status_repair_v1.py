#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Holdout Trigger + Vault Status Repair v1

Purpose:
- Repair 04: create an explicit holdout trigger protocol.
- Repair 05: create explicit promising-signal vault validation statuses.
- Keep holdout unselected/unpeeked/access-blocked.
- Ensure "promising" never means "validated" or "releaseable".
- Do NOT run research.
- Do NOT select/peek/use holdout.
- Do NOT allocate budget.
- Do NOT generate candidates.
- Do NOT release families.
- Do NOT touch runtime/capital/live.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = BASE_DIR / "edge_factory_os_repo"

FRAMEWORK_DIR = REPO_DIR / "edge_factory_os_framework"
POLICY_DIR = FRAMEWORK_DIR / "policies"
QUEUE_DIR = FRAMEWORK_DIR / "queues"
REGISTRY_DIR = FRAMEWORK_DIR / "registries"
STATUS_DIR = FRAMEWORK_DIR / "status"

GOV_REPAIR_STATE_JSON = POLICY_DIR / "governance_repair_suite_ledger_alpha_prereg_state_v1.json"
LEDGER_ENFORCED_JSON = POLICY_DIR / "global_multiple_testing_ledger_enforced_v1.json"
ALPHA_ENFORCEMENT_JSON = POLICY_DIR / "global_alpha_accounting_enforcement_v1.json"
PREREG_ENFORCEMENT_JSON = POLICY_DIR / "pre_registration_enforcement_policy_v1.json"
EXPLICIT_FLAG_POLICY_JSON = POLICY_DIR / "explicit_safety_flag_enforcement_policy_v1.json"

OLD_HOLDOUT_REGISTRY_JSON = REGISTRY_DIR / "untouched_holdout_registry_v1.json"
OLD_HOLDOUT_ACCESS_JSON = POLICY_DIR / "holdout_access_control_policy_v1.json"
OLD_HOLDOUT_COMMITMENT_JSON = POLICY_DIR / "holdout_commitment_protocol_v1.json"
OLD_VAULT_JSON = POLICY_DIR / "promising_signal_vault_v1.json"
CLOSED_ROUTE_REGISTRY_JSON = POLICY_DIR / "restricted_retest_closed_route_registry_v1.json"

LESSON_INDEX_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

OUT_DIR = BASE_DIR / "edge_factory_os_holdout_trigger_and_vault_status_repair"
OUT_JSON = OUT_DIR / "holdout_trigger_and_vault_status_repair_latest.json"
OUT_TXT = OUT_DIR / "holdout_trigger_and_vault_status_repair_latest.txt"

REPAIRED_HOLDOUT_TRIGGER_JSON = POLICY_DIR / "holdout_trigger_protocol_enforced_v1.json"
REPAIRED_HOLDOUT_ACCESS_JSON = POLICY_DIR / "holdout_access_enforcement_state_v1.json"
REPAIRED_VAULT_JSON = POLICY_DIR / "promising_signal_vault_validation_status_v1.json"
REPAIR_STATE_JSON = POLICY_DIR / "holdout_trigger_and_vault_status_repair_state_v1.json"
REPAIR_MANIFEST_JSON = STATUS_DIR / "holdout_trigger_and_vault_status_repair_manifest_v1.json"
NEXT_QUEUE_JSON = QUEUE_DIR / "holdout_trigger_and_vault_status_repair_next_queue_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD8_06_FAMILY_REGISTRY_AND_LESSON_ENFORCER_REPAIR"
NEXT_MODULE = "edge_factory_os_family_registry_and_lesson_enforcer_repair_v1.py"

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
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True, default=str), encoding="utf-8")
    tmp.replace(path)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def extract_list(obj: Any, key: str) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get(key), list):
        return [x for x in obj[key] if isinstance(x, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def normalize_vault_items(vault: Any, closed_route_hash: str) -> List[Dict[str, Any]]:
    rows = extract_list(vault, "vault_items")
    if not rows and isinstance(vault, dict):
        maybe = vault.get("items")
        if isinstance(maybe, list):
            rows = [x for x in maybe if isinstance(x, dict)]

    if not rows and closed_route_hash:
        rows = [
            {
                "vault_item_id": f"VAULT_ITEM_UNDERPOWERED_{closed_route_hash}",
                "source_route_hash": closed_route_hash,
                "source_research_key": "RESTRICTED_MARKET_STATE_STRUCTURE_RETEST_V1",
                "vault_class": "PROMISING_BUT_UNVALIDATED_STRUCTURE_HINT",
            }
        ]

    repaired: List[Dict[str, Any]] = []
    for i, item in enumerate(rows, start=1):
        source_route_hash = str(item.get("source_route_hash") or item.get("route_hash") or closed_route_hash or "")
        vault_class = str(item.get("vault_class") or item.get("class") or "PROMISING_BUT_UNVALIDATED_STRUCTURE_HINT")

        validation_status = "UNVALIDATED_NOT_RELEASEABLE"
        if "VALIDATED" in vault_class and "UNVALIDATED" not in vault_class:
            validation_status = "REVIEW_REQUIRED_STATUS_CONFLICT"

        repaired.append({
            **item,
            "vault_item_index": i,
            "source_route_hash": source_route_hash,
            "vault_class": vault_class,
            "validation_status": validation_status,
            "release_allowed": False,
            "candidate_generation_allowed": False,
            "family_release_allowed": False,
            "runtime_touch_allowed": False,
            "capital_change_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
            "status_rule": "PROMISING_OR_PRESERVED_NEVER_EQUALS_VALIDATED_OR_RELEASEABLE",
        })

    return repaired


def build_text(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS HOLDOUT TRIGGER + VAULT STATUS REPAIR v1")
    lines.append("=" * 100)

    for key in [
        "repair_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "holdout_trigger_status",
        "holdout_access_status",
        "vault_validation_status",
        "holdout_selected",
        "holdout_peeked",
        "holdout_usable_now",
        "holdout_access_allowed_now",
        "vault_item_count",
        "vault_unvalidated_count",
        "vault_release_allowed_count",
        "repair_pass",
        "failed_repair_count",
        "failed_repair_keys",
        "next_recommended_research_key",
        "next_module",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("CORE DECISION")
    lines.append("-" * 100)
    lines.append("Holdout remains unselected, unpeeked, unusable, and access-blocked.")
    lines.append("Holdout can only be opened by a future explicit trigger protocol after all prerequisite gates pass.")
    lines.append("Promising vault items are explicitly UNVALIDATED_NOT_RELEASEABLE.")
    lines.append("No research, candidate, release, runtime, capital, active paper, live, or real order action is allowed.")

    lines.append("")
    lines.append("HOLDOUT TRIGGER PROTOCOL")
    lines.append("-" * 100)
    lines.append(json.dumps(result.get("holdout_trigger_protocol"), indent=2, ensure_ascii=False))

    lines.append("")
    lines.append("VAULT VALIDATION STATUS")
    lines.append("-" * 100)
    lines.append(json.dumps(result.get("vault_validation_status_doc"), indent=2, ensure_ascii=False))

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
        "holdout_trigger_json",
        "holdout_access_json",
        "vault_validation_json",
        "repair_state_json",
        "repair_manifest_json",
        "next_queue_json",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS HOLDOUT TRIGGER + VAULT STATUS REPAIR v1")
    print("=" * 100)
    print(f"repair_status: {result.get('repair_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"holdout_trigger_status: {result.get('holdout_trigger_status')}")
    print(f"holdout_access_status: {result.get('holdout_access_status')}")
    print(f"vault_validation_status: {result.get('vault_validation_status')}")
    print(f"holdout_selected: {result.get('holdout_selected')}")
    print(f"holdout_peeked: {result.get('holdout_peeked')}")
    print(f"holdout_usable_now: {result.get('holdout_usable_now')}")
    print(f"holdout_access_allowed_now: {result.get('holdout_access_allowed_now')}")
    print(f"vault_item_count: {result.get('vault_item_count')}")
    print(f"vault_unvalidated_count: {result.get('vault_unvalidated_count')}")
    print(f"vault_release_allowed_count: {result.get('vault_release_allowed_count')}")
    print(f"repair_pass: {result.get('repair_pass')}")
    print(f"failed_repair_count: {result.get('failed_repair_count')}")
    print(f"failed_repair_keys: {result.get('failed_repair_keys')}")
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
    print(f"HOLDOUT: {result.get('holdout_trigger_json')}")
    print(f"VAULT  : {result.get('vault_validation_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    STATUS_DIR.mkdir(parents=True, exist_ok=True)

    gov_state = load_json(GOV_REPAIR_STATE_JSON, {})
    ledger = load_json(LEDGER_ENFORCED_JSON, {})
    alpha = load_json(ALPHA_ENFORCEMENT_JSON, {})
    prereg = load_json(PREREG_ENFORCEMENT_JSON, {})
    explicit_flags = load_json(EXPLICIT_FLAG_POLICY_JSON, {})
    old_holdout_registry = load_json(OLD_HOLDOUT_REGISTRY_JSON, {})
    old_holdout_access = load_json(OLD_HOLDOUT_ACCESS_JSON, {})
    old_holdout_commitment = load_json(OLD_HOLDOUT_COMMITMENT_JSON, {})
    old_vault = load_json(OLD_VAULT_JSON, {})
    closed_registry = load_json(CLOSED_ROUTE_REGISTRY_JSON, {})

    lessons = extract_list(load_json(LESSON_INDEX_JSON, {}), "lessons")
    blocked_routes = extract_list(load_json(BLOCKLIST_JSON, {}), "blocked_routes")

    closed_route_hash = str(closed_registry.get("closed_route_hash") or "")
    closed_route_family = str(closed_registry.get("closed_route_family") or "")

    holdout_selected = False
    holdout_peeked = False
    holdout_usable_now = False
    holdout_access_allowed_now = False

    holdout_trigger_protocol = {
        "policy_name": "edge_factory_os_holdout_trigger_protocol_enforced_v1",
        "created_at_utc": utc_now_iso(),
        "policy_status": "HOLDOUT_TRIGGER_PROTOCOL_ENFORCED_ACCESS_BLOCKED",
        "supersedes_for_decisioning": [
            str(OLD_HOLDOUT_REGISTRY_JSON),
            str(OLD_HOLDOUT_ACCESS_JSON),
            str(OLD_HOLDOUT_COMMITMENT_JSON),
        ],
        "repair_source": "external_audit_repair_04_holdout_trigger_protocol",
        "holdout_selected": holdout_selected,
        "holdout_peeked": holdout_peeked,
        "holdout_usable_now": holdout_usable_now,
        "holdout_access_allowed_now": holdout_access_allowed_now,
        "holdout_open_trigger_status": "NO_TRIGGER_ARMED",
        "holdout_open_allowed_now": False,
        "trigger_stages": [
            {
                "stage": "STAGE_0_DEFAULT",
                "status": "ACTIVE_NOW",
                "holdout_access_allowed": False,
                "description": "Default locked state. No holdout selected, peeked, or usable.",
            },
            {
                "stage": "STAGE_1_PRE_HOLDOUT_REVIEW",
                "status": "FUTURE_ONLY",
                "required_before_trigger": [
                    "pre_registration_enforcement_pass",
                    "ledger_enforced_non_null_pass",
                    "alpha_research_execution_budget_explicit_nonzero",
                    "nested_validation_pass",
                    "route_not_blocked",
                    "family_release_still_blocked",
                    "human_or_external_audit_approval",
                ],
                "holdout_access_allowed": False,
            },
            {
                "stage": "STAGE_2_HOLDOUT_COMMITMENT",
                "status": "FUTURE_ONLY",
                "required_before_trigger": [
                    "immutable_contract_hash",
                    "single_route_hash",
                    "success_criteria_locked",
                    "failure_criteria_locked",
                    "budget_consumption_locked",
                    "no post-hoc mutation allowed",
                ],
                "holdout_access_allowed": False,
            },
            {
                "stage": "STAGE_3_SINGLE_FINAL_HOLDOUT_OPEN",
                "status": "DISABLED_UNTIL_EXPLICIT_SEPARATE_MODULE",
                "required_before_trigger": [
                    "separate_holdout_open_module",
                    "manual approval",
                    "all prior stages pass",
                    "audit trail committed",
                ],
                "holdout_access_allowed": False,
            },
        ],
        "hard_rules": [
            "No module may select, peek, sample, summarize, or use holdout unless holdout_open_trigger_status is EXPLICITLY_ARMED_BY_SEPARATE_COMMITTED_MODULE.",
            "Promising vault status cannot trigger holdout.",
            "Research preview cannot trigger holdout.",
            "Underpowered route cannot trigger holdout.",
            "Runtime family monitoring cannot trigger holdout.",
            "Holdout cannot be used for candidate generation directly.",
        ],
        "release_gate_feed": {
            "HOLDOUT_TRIGGER_PROTOCOL_ENFORCED": True,
            "HOLDOUT_SELECTED": False,
            "HOLDOUT_PEEKED": False,
            "HOLDOUT_USABLE_NOW": False,
            "HOLDOUT_ACCESS_ALLOWED_NOW": False,
            "RESEARCH_EXECUTION_ALLOWED_FROM_HOLDOUT_POLICY": False,
        },
        **SAFETY_FLAGS,
    }

    holdout_access_enforcement = {
        "policy_name": "edge_factory_os_holdout_access_enforcement_state_v1",
        "created_at_utc": utc_now_iso(),
        "policy_status": "HOLDOUT_ACCESS_ENFORCEMENT_ACTIVE_BLOCKED",
        "holdout_selected": holdout_selected,
        "holdout_peeked": holdout_peeked,
        "holdout_usable_now": holdout_usable_now,
        "holdout_access_allowed_now": holdout_access_allowed_now,
        "old_registry_status": old_holdout_registry.get("holdout_registry_status") or old_holdout_registry.get("registry_status"),
        "old_access_policy_status": old_holdout_access.get("policy_status"),
        "old_commitment_status": old_holdout_commitment.get("holdout_commitment_protocol_status") or old_holdout_commitment.get("policy_status"),
        "blocked_reason": "NO_EXPLICIT_HOLDOUT_TRIGGER_ARMED",
        **SAFETY_FLAGS,
    }

    repaired_vault_items = normalize_vault_items(old_vault, closed_route_hash)

    vault_release_allowed_count = sum(1 for item in repaired_vault_items if item.get("release_allowed") is True)
    vault_unvalidated_count = sum(1 for item in repaired_vault_items if item.get("validation_status") == "UNVALIDATED_NOT_RELEASEABLE")

    vault_validation_status_doc = {
        "policy_name": "edge_factory_os_promising_signal_vault_validation_status_v1",
        "created_at_utc": utc_now_iso(),
        "vault_status": "PROMISING_SIGNAL_VAULT_VALIDATION_STATUS_ENFORCED",
        "supersedes_for_decisioning": str(OLD_VAULT_JSON),
        "repair_source": "external_audit_repair_05_vault_status_not_release_status",
        "closed_route_hash": closed_route_hash,
        "closed_route_family": closed_route_family,
        "vault_item_count": len(repaired_vault_items),
        "vault_unvalidated_count": vault_unvalidated_count,
        "vault_release_allowed_count": vault_release_allowed_count,
        "vault_items": repaired_vault_items,
        "global_rules": {
            "promising_means": "preserved_for_memory_or_future_review",
            "promising_does_not_mean": [
                "validated",
                "candidate_allowed",
                "release_allowed",
                "runtime_allowed",
                "capital_allowed",
                "live_allowed",
                "holdout_trigger_allowed",
            ],
            "required_for_status_upgrade": [
                "new pre-registered contract",
                "route not blocked",
                "ledger enforced non-null",
                "alpha explicit budget",
                "nested validation pass",
                "procedural null pass",
                "separate governance approval",
                "holdout remains blocked until separate trigger",
            ],
        },
        "release_gate_feed": {
            "VAULT_VALIDATION_STATUS_ENFORCED": True,
            "VAULT_CONTAINS_RELEASEABLE_ITEM": vault_release_allowed_count > 0,
            "CANDIDATE_GENERATION_ALLOWED_FROM_VAULT": False,
            "FAMILY_RELEASE_ALLOWED_FROM_VAULT": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_VAULT": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_VAULT": False,
            "ACTIVE_PAPER_ALLOWED_FROM_VAULT": False,
            "LIVE_ALLOWED_FROM_VAULT": False,
            "REAL_ORDERS_ALLOWED_FROM_VAULT": False,
            "HOLDOUT_TRIGGER_ALLOWED_FROM_VAULT": False,
        },
        **SAFETY_FLAGS,
    }

    checks = {
        "GOV_REPAIR_PASS": gov_state.get("repair_pass") is True,
        "LEDGER_ENFORCED": ledger.get("ledger_status") == "GLOBAL_MULTIPLE_TESTING_LEDGER_ENFORCED_NON_NULL",
        "ALPHA_RESEARCH_PASS_FALSE": alpha.get("research_execution_alpha_pass") is False,
        "PREREG_ACTIVE": prereg.get("policy_status") == "PRE_REGISTRATION_ENFORCEMENT_ACTIVE",
        "EXPLICIT_FLAGS_ACTIVE": explicit_flags.get("policy_status") == "EXPLICIT_SAFETY_FLAG_POLICY_ACTIVE",
        "HOLDOUT_SELECTED_FALSE": holdout_selected is False,
        "HOLDOUT_PEEKED_FALSE": holdout_peeked is False,
        "HOLDOUT_USABLE_FALSE": holdout_usable_now is False,
        "HOLDOUT_ACCESS_FALSE": holdout_access_allowed_now is False,
        "VAULT_ITEMS_PRESENT_OR_SYNTHETIC": len(repaired_vault_items) >= 1,
        "VAULT_RELEASE_ALLOWED_ZERO": vault_release_allowed_count == 0,
        "VAULT_UNVALIDATED_PRESENT": vault_unvalidated_count >= 1,
        "CLOSED_ROUTE_PRESENT": bool(closed_route_hash),
    }

    failed = [k for k, v in checks.items() if v is not True]
    repair_pass = len(failed) == 0

    if repair_pass:
        repair_status = "HOLDOUT_TRIGGER_AND_VAULT_STATUS_REPAIR_PASS"
        severity = "ATTENTION"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        next_action = "BUILD_FAMILY_REGISTRY_AND_LESSON_ENFORCER_REPAIR_NO_EXECUTION"
        reason = "Holdout trigger protocol and vault validation status enforcement are active."
        next_key = NEXT_RESEARCH_KEY
        next_module = NEXT_MODULE
        return_code = 0
    else:
        repair_status = "HOLDOUT_TRIGGER_AND_VAULT_STATUS_REPAIR_FAIL_REVIEW_REQUIRED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_HOLDOUT_TRIGGER_OR_VAULT_STATUS_REPAIR_FAILURES"
        reason = f"failed_repair_keys={failed}"
        next_key = None
        next_module = None
        return_code = 2

    repair_state = {
        "state_name": "edge_factory_os_holdout_trigger_and_vault_status_repair_state_v1",
        "created_at_utc": utc_now_iso(),
        "repair_status": repair_status,
        "strict_policy_key": STRICT_POLICY_KEY,
        "repair_pass": repair_pass,
        "failed_repair_count": len(failed),
        "failed_repair_keys": failed,
        "holdout_trigger_status": holdout_trigger_protocol["policy_status"],
        "holdout_access_status": holdout_access_enforcement["policy_status"],
        "vault_validation_status": vault_validation_status_doc["vault_status"],
        "holdout_selected": holdout_selected,
        "holdout_peeked": holdout_peeked,
        "holdout_usable_now": holdout_usable_now,
        "holdout_access_allowed_now": holdout_access_allowed_now,
        "vault_item_count": len(repaired_vault_items),
        "vault_unvalidated_count": vault_unvalidated_count,
        "vault_release_allowed_count": vault_release_allowed_count,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        **SAFETY_FLAGS,
    }

    manifest = {
        "manifest_name": "edge_factory_os_holdout_trigger_and_vault_status_repair_manifest_v1",
        "created_at_utc": utc_now_iso(),
        "manifest_status": "HOLDOUT_VAULT_REPAIR_MANIFEST_READY" if repair_pass else "HOLDOUT_VAULT_REPAIR_MANIFEST_ATTENTION",
        "repair_mapping": {
            "repair_04_holdout_trigger_protocol": "implemented",
            "repair_05_vault_validation_status": "implemented",
        },
        "repair_files": {
            "holdout_trigger_json": str(REPAIRED_HOLDOUT_TRIGGER_JSON),
            "holdout_access_json": str(REPAIRED_HOLDOUT_ACCESS_JSON),
            "vault_validation_json": str(REPAIRED_VAULT_JSON),
            "repair_state_json": str(REPAIR_STATE_JSON),
        },
        "old_files_preserved": {
            "old_holdout_registry_json": str(OLD_HOLDOUT_REGISTRY_JSON),
            "old_holdout_access_json": str(OLD_HOLDOUT_ACCESS_JSON),
            "old_vault_json": str(OLD_VAULT_JSON),
        },
        "lesson_count": len(lessons),
        "blocked_route_count": len(blocked_routes),
        **SAFETY_FLAGS,
    }

    next_queue = {
        "queue_name": "edge_factory_os_holdout_trigger_and_vault_status_repair_next_queue_v1",
        "created_at_utc": utc_now_iso(),
        "queue_status": "HOLDOUT_TRIGGER_VAULT_STATUS_NEXT_QUEUE_READY" if repair_pass else "HOLDOUT_TRIGGER_VAULT_STATUS_QUEUE_BLOCKED",
        "top_next_research_key": next_key,
        "top_next_module": next_module,
        "next_steps": [
            {
                "research_key": NEXT_RESEARCH_KEY,
                "module": NEXT_MODULE,
                "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
                "purpose": "Repair runtime family registry and lesson enforcer after holdout/vault status repair.",
                "research_execution_allowed_now": False,
                "candidate_generation_allowed": False,
                "family_release_allowed": False,
                "runtime_touch_allowed": False,
                "capital_change_allowed": False,
                "active_paper_allowed": False,
                "live_allowed": False,
                "real_orders_allowed": False,
            }
        ] if repair_pass else [],
        **SAFETY_FLAGS,
    }

    write_json(REPAIRED_HOLDOUT_TRIGGER_JSON, holdout_trigger_protocol)
    write_json(REPAIRED_HOLDOUT_ACCESS_JSON, holdout_access_enforcement)
    write_json(REPAIRED_VAULT_JSON, vault_validation_status_doc)
    write_json(REPAIR_STATE_JSON, repair_state)
    write_json(REPAIR_MANIFEST_JSON, manifest)
    write_json(NEXT_QUEUE_JSON, next_queue)

    result = {
        "module_name": "edge_factory_os_holdout_trigger_and_vault_status_repair_v1",
        "created_at_utc": utc_now_iso(),
        "repair_status": repair_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "holdout_trigger_status": holdout_trigger_protocol["policy_status"],
        "holdout_access_status": holdout_access_enforcement["policy_status"],
        "vault_validation_status": vault_validation_status_doc["vault_status"],
        "holdout_selected": holdout_selected,
        "holdout_peeked": holdout_peeked,
        "holdout_usable_now": holdout_usable_now,
        "holdout_access_allowed_now": holdout_access_allowed_now,
        "vault_item_count": len(repaired_vault_items),
        "vault_unvalidated_count": vault_unvalidated_count,
        "vault_release_allowed_count": vault_release_allowed_count,
        "repair_pass": repair_pass,
        "failed_repair_count": len(failed),
        "failed_repair_keys": failed,
        "checks": checks,
        "holdout_trigger_protocol": holdout_trigger_protocol,
        "holdout_access_enforcement": holdout_access_enforcement,
        "vault_validation_status_doc": vault_validation_status_doc,
        "repair_state": repair_state,
        "manifest": manifest,
        "next_queue": next_queue,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "holdout_trigger_json": str(REPAIRED_HOLDOUT_TRIGGER_JSON),
        "holdout_access_json": str(REPAIRED_HOLDOUT_ACCESS_JSON),
        "vault_validation_json": str(REPAIRED_VAULT_JSON),
        "repair_state_json": str(REPAIR_STATE_JSON),
        "repair_manifest_json": str(REPAIR_MANIFEST_JSON),
        "next_queue_json": str(NEXT_QUEUE_JSON),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text(result))
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
