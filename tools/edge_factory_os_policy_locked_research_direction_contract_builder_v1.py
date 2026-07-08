#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Policy-Locked Research Direction Contract Builder v1

Purpose:
- Consume policy-locked rotation after restricted retest.
- Confirm restricted market-state route is closed.
- Select a materially different, non-execution research direction.
- Build a policy-locked contract for the selected direction.
- Prefer external audit / methodology refresh before more strategy research.
- Do NOT execute research.
- Keep broad strategy search, candidates, release, runtime, capital, active paper, live, and real orders blocked.
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
QUEUE_DIR = FRAMEWORK_DIR / "queues"
CONTRACT_DIR = FRAMEWORK_DIR / "contracts"
REGISTRY_DIR = FRAMEWORK_DIR / "registries"

ROTATION_JSON = (
    BASE_DIR
    / "edge_factory_os_policy_locked_research_rotation_after_restricted_retest"
    / "policy_locked_research_rotation_after_restricted_retest_latest.json"
)
ROTATION_STATE_JSON = POLICY_DIR / "policy_locked_research_rotation_after_restricted_retest_state_v1.json"
ROTATION_QUEUE_JSON = QUEUE_DIR / "policy_locked_research_rotation_after_restricted_retest_queue_v1.json"
CLOSED_ROUTE_REGISTRY_JSON = POLICY_DIR / "restricted_retest_closed_route_registry_v1.json"

GLOBAL_LEDGER_JSON = POLICY_DIR / "global_multiple_testing_ledger_v1.json"
GLOBAL_ALPHA_ACCOUNTING_JSON = POLICY_DIR / "global_route_family_alpha_accounting_v1.json"
GLOBAL_ALPHA_POLICY_JSON = POLICY_DIR / "global_alpha_spending_policy_v1.json"
PROMISING_VAULT_JSON = POLICY_DIR / "promising_signal_vault_v1.json"
GOVERNED_REOPEN_POLICY_JSON = POLICY_DIR / "governed_research_reopen_policy_v1.json"
PRE_REG_POLICY_JSON = POLICY_DIR / "pre_registration_policy_v1.json"
NESTED_VALIDATION_POLICY_JSON = POLICY_DIR / "nested_validation_policy_v1.json"
UNTOUCHED_HOLDOUT_REGISTRY_JSON = REGISTRY_DIR / "untouched_holdout_registry_v1.json"
HOLDOUT_ACCESS_CONTROL_JSON = POLICY_DIR / "holdout_access_control_policy_v1.json"

LESSON_INDEX_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

OUT_DIR = BASE_DIR / "edge_factory_os_policy_locked_research_direction_contract_builder"
OUT_JSON = OUT_DIR / "policy_locked_research_direction_contract_builder_latest.json"
OUT_TXT = OUT_DIR / "policy_locked_research_direction_contract_builder_latest.txt"

REPO_CONTRACT_JSON = CONTRACT_DIR / "policy_locked_research_direction_contract_v1.json"
REPO_CONTRACT_TXT = CONTRACT_DIR / "policy_locked_research_direction_contract_v1.txt"
REPO_BUILDER_STATE_JSON = POLICY_DIR / "policy_locked_research_direction_contract_builder_state_v1.json"
REPO_NEXT_QUEUE_JSON = QUEUE_DIR / "policy_locked_research_direction_contract_next_queue_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD8_02_EXTERNAL_AUDIT_PACKET_REFRESH"
NEXT_MODULE = "edge_factory_os_external_audit_packet_refresh_v1.py"

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


def route_hash_blocked(blocked_routes: List[Dict[str, Any]], route_hash: str) -> bool:
    return route_hash in {str(x.get("route_hash")) for x in blocked_routes if isinstance(x, dict)}


def select_direction(candidate_rows: List[Dict[str, Any]], blocked_routes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Avoid selecting the meta-builder itself as the next executable module.
    Prefer external audit before any new data/strategy-like work.
    """
    preferred_order = [
        "RD8_02_EXTERNAL_AUDIT_PACKET_REFRESH",
        "RD8_03_SOURCE_PANEL_INFORMATION_QUALITY_REVIEW",
    ]

    rows_by_key = {
        str(row.get("research_key")): row
        for row in candidate_rows
        if isinstance(row, dict)
    }

    for key in preferred_order:
        row = rows_by_key.get(key)
        if not row:
            continue
        rh = str(row.get("route_hash") or "")
        if row.get("materially_different_from_closed_route") is True and not route_hash_blocked(blocked_routes, rh):
            return row

    fallback = [
        row for row in candidate_rows
        if row.get("research_key") != "RD8_01_POLICY_LOCKED_RESEARCH_DIRECTION_CONTRACT_BUILDER"
        and row.get("materially_different_from_closed_route") is True
        and not route_hash_blocked(blocked_routes, str(row.get("route_hash") or ""))
    ]

    fallback.sort(key=lambda r: int(r.get("priority") or 0), reverse=True)
    return fallback[0] if fallback else {}


def build_contract_text(contract: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS POLICY-LOCKED RESEARCH DIRECTION CONTRACT v1")
    lines.append("=" * 100)

    for key in [
        "contract_status",
        "contract_id",
        "contract_hash",
        "selected_research_key",
        "selected_route_hash",
        "selected_next_module",
        "selected_route_family",
        "closed_route_hash",
        "closed_route_family",
        "broad_strategy_search_allowed",
        "research_execution_allowed_now",
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
    lines.append("CONTRACT PURPOSE")
    lines.append("-" * 100)
    lines.append(str(contract.get("purpose")))

    lines.append("")
    lines.append("HARD RULES")
    lines.append("-" * 100)
    for item in contract.get("hard_rules", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("REQUIRED INPUTS")
    lines.append("-" * 100)
    for item in contract.get("required_inputs", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("REQUIRED OUTPUTS")
    lines.append("-" * 100)
    for item in contract.get("required_outputs", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        lines.append(f"{key}: {value}")

    return "\n".join(lines)


def build_summary_text(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS POLICY-LOCKED RESEARCH DIRECTION CONTRACT BUILDER v1")
    lines.append("=" * 100)

    for key in [
        "builder_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "selected_research_key",
        "selected_route_hash",
        "selected_next_module",
        "selected_route_family",
        "closed_route_hash",
        "closed_route_family",
        "restricted_route_closed",
        "materially_different_from_closed_route",
        "contract_created",
        "broad_strategy_search_allowed",
        "research_execution_allowed_now",
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
    lines.append("A policy-locked contract was created for external audit packet refresh.")
    lines.append("This is not strategy search and not research execution.")
    lines.append("The closed market-state route remains closed.")
    lines.append("All release/trading/runtime/capital/live actions remain blocked.")

    lines.append("")
    lines.append("OUTPUT PATHS")
    lines.append("-" * 100)
    for key in [
        "output_json",
        "output_txt",
        "contract_json",
        "contract_txt",
        "builder_state_json",
        "next_queue_json",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS POLICY-LOCKED RESEARCH DIRECTION CONTRACT BUILDER v1")
    print("=" * 100)
    print(f"builder_status: {result.get('builder_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"selected_research_key: {result.get('selected_research_key')}")
    print(f"selected_route_hash: {result.get('selected_route_hash')}")
    print(f"selected_next_module: {result.get('selected_next_module')}")
    print(f"selected_route_family: {result.get('selected_route_family')}")
    print(f"closed_route_hash: {result.get('closed_route_hash')}")
    print(f"closed_route_family: {result.get('closed_route_family')}")
    print(f"restricted_route_closed: {result.get('restricted_route_closed')}")
    print(f"materially_different_from_closed_route: {result.get('materially_different_from_closed_route')}")
    print(f"contract_created: {result.get('contract_created')}")
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
    print(f"CONTRACT: {result.get('contract_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CONTRACT_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    rotation = load_json(ROTATION_JSON, {})
    rotation_state = load_json(ROTATION_STATE_JSON, {})
    rotation_queue = load_json(ROTATION_QUEUE_JSON, {})
    closed_registry = load_json(CLOSED_ROUTE_REGISTRY_JSON, {})
    ledger = load_json(GLOBAL_LEDGER_JSON, {})
    alpha_accounting = load_json(GLOBAL_ALPHA_ACCOUNTING_JSON, {})
    alpha_policy = load_json(GLOBAL_ALPHA_POLICY_JSON, {})
    vault = load_json(PROMISING_VAULT_JSON, {})
    reopen_policy = load_json(GOVERNED_REOPEN_POLICY_JSON, {})
    pre_reg = load_json(PRE_REG_POLICY_JSON, {})
    nested = load_json(NESTED_VALIDATION_POLICY_JSON, {})
    holdout_registry = load_json(UNTOUCHED_HOLDOUT_REGISTRY_JSON, {})
    holdout_access = load_json(HOLDOUT_ACCESS_CONTROL_JSON, {})

    lessons = extract_list(load_json(LESSON_INDEX_JSON, {}), "lessons")
    blocked_routes = extract_list(load_json(BLOCKLIST_JSON, {}), "blocked_routes")
    vault_items = extract_list(vault, "vault_items")

    candidate_rows = rotation_queue.get("candidate_rows", [])
    if not isinstance(candidate_rows, list):
        candidate_rows = []

    selected = select_direction(candidate_rows, blocked_routes)

    closed_route_hash = str(rotation.get("closed_route_hash") or rotation_state.get("closed_route_hash") or closed_registry.get("closed_route_hash") or "")
    closed_route_family = str(rotation.get("closed_route_family") or rotation_state.get("closed_route_family") or closed_registry.get("closed_route_family") or "")
    selected_research_key = str(selected.get("research_key") or "")
    selected_route_hash = str(selected.get("route_hash") or "")
    selected_next_module = str(selected.get("next_module") or "")
    selected_route_family = str(selected.get("route_family") or "")
    selected_is_blocked = route_hash_blocked(blocked_routes, selected_route_hash)

    prerequisites = {
        "rotation_ready": rotation.get("rotation_status") == "POLICY_LOCKED_RESEARCH_ROTATION_READY_MATERIAL_DIFFERENT_DIRECTION_SELECTED",
        "rotation_state_ready": rotation_state.get("rotation_status") == "POLICY_LOCKED_RESEARCH_ROTATION_READY_MATERIAL_DIFFERENT_DIRECTION_SELECTED",
        "queue_ready": rotation_queue.get("queue_status") == "POLICY_LOCKED_ROTATION_QUEUE_READY",
        "closed_registry_ready": closed_registry.get("registry_status") == "RESTRICTED_RETEST_CLOSED_ROUTE_REGISTERED",
        "closed_route_hash_present": bool(closed_route_hash),
        "closed_route_family_market_state": closed_route_family == "MARKET_STATE_TRANSITION_FAMILY",
        "restricted_route_closed": rotation.get("restricted_route_closed") is True and rotation_state.get("restricted_route_closed") is True,
        "additional_null_budget_not_allowed": rotation.get("additional_null_budget_allowed_now") is False and rotation_state.get("additional_null_budget_allowed_now") is False,
        "release_blocked": rotation.get("release_allowed") is False and rotation_state.get("release_allowed") is False,
        "selected_direction_present": bool(selected),
        "selected_not_meta_builder": selected_research_key != "RD8_01_POLICY_LOCKED_RESEARCH_DIRECTION_CONTRACT_BUILDER",
        "selected_materially_different": selected.get("materially_different_from_closed_route") is True,
        "selected_route_hash_not_blocked": not selected_is_blocked,
        "ledger_active": ledger.get("ledger_status") == "GLOBAL_MULTIPLE_TESTING_LEDGER_ACTIVE_RESEARCH_LOCKED",
        "alpha_accounting_pass": alpha_accounting.get("global_alpha_accounting_pass") is True,
        "alpha_policy_active": alpha_policy.get("policy_status") == "GLOBAL_ALPHA_SPENDING_POLICY_ACTIVE_ZERO_STRATEGY_BUDGET",
        "vault_active": vault.get("vault_status") == "PROMISING_SIGNAL_VAULT_ACTIVE_RELEASE_BLOCKED",
        "reopen_policy_restricted": reopen_policy.get("policy_status") == "GOVERNED_RESEARCH_REOPEN_POLICY_ACTIVE_RESTRICTED_CONTRACTS_ONLY",
        "pre_registration_required": pre_reg.get("all_future_research_must_be_pre_registered") is True,
        "nested_ready": nested.get("policy_status") == "NESTED_VALIDATION_POLICY_READY_STRATEGY_SEARCH_LOCKED",
        "holdout_not_selected": holdout_registry.get("holdout_selected") is False,
        "holdout_not_peeked": holdout_registry.get("holdout_peeked") is False,
        "holdout_access_blocked": holdout_access.get("holdout_access_allowed_now") is False,
        "lessons_present": len(lessons) >= 1,
        "blocklist_present": len(blocked_routes) >= 1,
    }

    prerequisite_pass = all(prerequisites.values())

    contract_hash = stable_hash({
        "selected_research_key": selected_research_key,
        "selected_route_hash": selected_route_hash,
        "selected_next_module": selected_next_module,
        "closed_route_hash": closed_route_hash,
        "closed_route_family": closed_route_family,
        "policy_locked": True,
        "no_execution": True,
    })

    contract_id = f"POLICY_LOCKED_RESEARCH_DIRECTION_CONTRACT_V1_{contract_hash}_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')}"

    contract = {
        "contract_name": "edge_factory_os_policy_locked_research_direction_contract_v1",
        "created_at_utc": utc_now_iso(),
        "contract_status": "POLICY_LOCKED_RESEARCH_DIRECTION_CONTRACT_READY_NO_EXECUTION" if prerequisite_pass else "POLICY_LOCKED_RESEARCH_DIRECTION_CONTRACT_BLOCKED",
        "contract_id": contract_id if prerequisite_pass else None,
        "contract_hash": contract_hash,
        "strict_policy_key": STRICT_POLICY_KEY,
        "selected_research_key": selected_research_key,
        "selected_route_hash": selected_route_hash,
        "selected_next_module": selected_next_module,
        "selected_route_family": selected_route_family,
        "closed_route_hash": closed_route_hash,
        "closed_route_family": closed_route_family,
        "purpose": (
            "Build an external audit / methodology packet refresh after restricted market-state route closure, "
            "without executing research, without strategy search, and without any release/candidate/runtime/capital/live action."
        ),
        "why_this_direction": [
            "The restricted market-state route failed validation under tiny global alpha.",
            "Additional null power was not justified.",
            "Before more research, the system should refresh an adversarial audit packet.",
            "This direction is materially different from market-state strategy retesting.",
        ],
        "required_inputs": [
            str(ROTATION_JSON),
            str(ROTATION_STATE_JSON),
            str(ROTATION_QUEUE_JSON),
            str(CLOSED_ROUTE_REGISTRY_JSON),
            str(GLOBAL_LEDGER_JSON),
            str(GLOBAL_ALPHA_ACCOUNTING_JSON),
            str(PROMISING_VAULT_JSON),
            str(PRE_REG_POLICY_JSON),
            str(NESTED_VALIDATION_POLICY_JSON),
            str(UNTOUCHED_HOLDOUT_REGISTRY_JSON),
        ],
        "required_outputs": [
            "external_audit_packet_refresh_latest.json",
            "external_audit_packet_refresh_latest.txt",
            "audit_packet_manifest_v1.json",
            "audit_prompt_red_team_packet_v1.txt",
        ],
        "hard_rules": [
            "no strategy search",
            "no research execution",
            "no broad axis expansion",
            "no holdout access",
            "no candidate generation",
            "no candidate contract",
            "no family release",
            "no runtime touch",
            "no capital change",
            "no active paper enable",
            "no live trading",
            "no real orders",
            "preserve closed-route evidence",
            "include all anti-overfitting governance state in audit packet",
            "include overfitting/null-power failure lessons",
            "include untracked backup/git-status warning section",
        ],
        "release_gate_feed": {
            "POLICY_LOCKED_CONTRACT_READY": prerequisite_pass,
            "BROAD_STRATEGY_SEARCH_ALLOWED": False,
            "RESEARCH_EXECUTION_ALLOWED_NOW": False,
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
        "audit_scope": {
            "must_review": [
                "global multiple-testing ledger",
                "research budget policy",
                "promising signal vault",
                "pre-registration policy",
                "nested validation policy",
                "untouched holdout governance",
                "route-family alpha accounting",
                "restricted market-state retest failure",
                "null power feasibility closure",
                "closed route registry",
                "current git status/untracked backups",
            ],
            "must_answer": [
                "Where can the OS still fool itself?",
                "Which gates are too weak or too easy to satisfy?",
                "Which one-off modules should be consolidated before more research?",
                "Whether the next direction should be data-information quality, external audit, or architecture consolidation.",
                "Whether any current route deserves more budget. Default answer should be no unless evidence is exceptional.",
            ],
        },
        **SAFETY_FLAGS,
    }

    builder_state = {
        "state_name": "edge_factory_os_policy_locked_research_direction_contract_builder_state_v1",
        "created_at_utc": utc_now_iso(),
        "builder_status": "POLICY_LOCKED_RESEARCH_DIRECTION_CONTRACT_BUILDER_READY" if prerequisite_pass else "POLICY_LOCKED_RESEARCH_DIRECTION_CONTRACT_BUILDER_BLOCKED",
        "contract_created": prerequisite_pass,
        "contract_id": contract.get("contract_id"),
        "contract_hash": contract_hash,
        "selected_research_key": selected_research_key,
        "selected_route_hash": selected_route_hash,
        "selected_next_module": selected_next_module,
        "selected_route_family": selected_route_family,
        "closed_route_hash": closed_route_hash,
        "closed_route_family": closed_route_family,
        "restricted_route_closed": prerequisites["restricted_route_closed"],
        "materially_different_from_closed_route": selected.get("materially_different_from_closed_route") is True,
        "broad_strategy_search_allowed": False,
        "research_execution_allowed_now": False,
        "next_recommended_research_key": NEXT_RESEARCH_KEY if prerequisite_pass else None,
        "next_module": NEXT_MODULE if prerequisite_pass else None,
        "prerequisites": prerequisites,
        **SAFETY_FLAGS,
    }

    next_queue = {
        "queue_name": "edge_factory_os_policy_locked_research_direction_contract_next_queue_v1",
        "created_at_utc": utc_now_iso(),
        "queue_status": "POLICY_LOCKED_RESEARCH_DIRECTION_CONTRACT_NEXT_QUEUE_READY" if prerequisite_pass else "POLICY_LOCKED_RESEARCH_DIRECTION_CONTRACT_QUEUE_BLOCKED",
        "selected_research_key": selected_research_key,
        "selected_route_hash": selected_route_hash,
        "selected_next_module": selected_next_module,
        "contract_id": contract.get("contract_id"),
        "contract_hash": contract_hash,
        "broad_strategy_search_allowed": False,
        "research_execution_allowed_now": False,
        "top_next_research_key": NEXT_RESEARCH_KEY if prerequisite_pass else None,
        "top_next_module": NEXT_MODULE if prerequisite_pass else None,
        "next_steps": [
            {
                "research_key": NEXT_RESEARCH_KEY,
                "module": NEXT_MODULE,
                "priority": 100,
                "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
                "purpose": "Refresh external/adversarial audit packet from current governance state before more research.",
                "contract_id": contract.get("contract_id"),
                "broad_strategy_search_allowed": False,
                "research_execution_allowed_now": False,
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
        builder_status = "POLICY_LOCKED_RESEARCH_DIRECTION_CONTRACT_BUILDER_READY"
        severity = "ATTENTION"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        next_action = "BUILD_EXTERNAL_AUDIT_PACKET_REFRESH_NO_EXECUTION"
        reason = "policy-locked external audit direction contract ready; no research execution or release allowed"
        return_code = 0
    else:
        builder_status = "POLICY_LOCKED_RESEARCH_DIRECTION_CONTRACT_BUILDER_BLOCKED_PREREQUISITE_NOT_MET"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_POLICY_LOCKED_RESEARCH_DIRECTION_CONTRACT_PREREQUISITES"
        reason = f"prerequisites={prerequisites}"
        return_code = 2

    write_json(REPO_CONTRACT_JSON, contract)
    write_text(REPO_CONTRACT_TXT, build_contract_text(contract))
    write_json(REPO_BUILDER_STATE_JSON, builder_state)
    write_json(REPO_NEXT_QUEUE_JSON, next_queue)

    result = {
        "builder_name": "edge_factory_os_policy_locked_research_direction_contract_builder_v1",
        "created_at_utc": utc_now_iso(),
        "builder_status": builder_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "contract_created": prerequisite_pass,
        "contract_id": contract.get("contract_id"),
        "contract_hash": contract_hash,
        "selected_research_key": selected_research_key,
        "selected_route_hash": selected_route_hash,
        "selected_next_module": selected_next_module,
        "selected_route_family": selected_route_family,
        "closed_route_hash": closed_route_hash,
        "closed_route_family": closed_route_family,
        "restricted_route_closed": prerequisites["restricted_route_closed"],
        "materially_different_from_closed_route": selected.get("materially_different_from_closed_route") is True,
        "candidate_direction_count": len(candidate_rows),
        "vault_item_count": len(vault_items),
        "lesson_count": len(lessons),
        "blocked_route_count": len(blocked_routes),
        "prerequisites": prerequisites,
        "contract": contract,
        "builder_state": builder_state,
        "next_queue": next_queue,
        "broad_strategy_search_allowed": False,
        "research_execution_allowed_now": False,
        "next_recommended_research_key": NEXT_RESEARCH_KEY if prerequisite_pass else None,
        "next_module": NEXT_MODULE if prerequisite_pass else None,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "contract_json": str(REPO_CONTRACT_JSON),
        "contract_txt": str(REPO_CONTRACT_TXT),
        "builder_state_json": str(REPO_BUILDER_STATE_JSON),
        "next_queue_json": str(REPO_NEXT_QUEUE_JSON),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_summary_text(result))
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
