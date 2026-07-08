#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Policy-Locked Research Rotation After Restricted Retest v1

Purpose:
- Consume Restricted Null Power Feasibility Review v1.
- Confirm the restricted market-state route is closed for release.
- Confirm no additional null-power budget is allowed now.
- Preserve the market-state structure hint as underpowered/not validated.
- Queue materially different policy-locked research directions.
- Do NOT execute research.
- Keep candidate/family/runtime/capital/active-paper/live/real-order actions blocked.
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
REGISTRY_DIR = FRAMEWORK_DIR / "registries"

FEASIBILITY_JSON = (
    BASE_DIR
    / "edge_factory_os_restricted_null_power_feasibility_review"
    / "restricted_null_power_feasibility_review_latest.json"
)
FEASIBILITY_STATE_JSON = POLICY_DIR / "restricted_null_power_feasibility_review_state_v1.json"
RESTRICTED_RETEST_EVALUATOR_STATE_JSON = POLICY_DIR / "restricted_market_state_structure_retest_evaluator_state_v1.json"
RESTRICTED_RETEST_STATE_JSON = POLICY_DIR / "restricted_market_state_structure_retest_state_v1.json"
RESTRICTED_BUDGET_CONSUMPTION_JSON = POLICY_DIR / "restricted_market_state_structure_retest_budget_consumption_v1.json"

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

OUT_DIR = BASE_DIR / "edge_factory_os_policy_locked_research_rotation_after_restricted_retest"
OUT_JSON = OUT_DIR / "policy_locked_research_rotation_after_restricted_retest_latest.json"
OUT_TXT = OUT_DIR / "policy_locked_research_rotation_after_restricted_retest_latest.txt"
OUT_CANDIDATES_CSV = OUT_DIR / "policy_locked_research_rotation_candidates_latest.csv"

REPO_ROTATION_STATE_JSON = POLICY_DIR / "policy_locked_research_rotation_after_restricted_retest_state_v1.json"
REPO_ROTATION_QUEUE_JSON = QUEUE_DIR / "policy_locked_research_rotation_after_restricted_retest_queue_v1.json"
REPO_CLOSED_ROUTE_REGISTRY_JSON = POLICY_DIR / "restricted_retest_closed_route_registry_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD8_01_POLICY_LOCKED_RESEARCH_DIRECTION_CONTRACT_BUILDER"
NEXT_MODULE = "edge_factory_os_policy_locked_research_direction_contract_builder_v1.py"

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


def write_csv(path: Path, rows: List[Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    import csv

    fields: List[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def stable_hash(payload: Dict[str, object]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def extract_list(obj: object, key: str) -> List[Dict[str, object]]:
    if isinstance(obj, dict) and isinstance(obj.get(key), list):
        return [x for x in obj[key] if isinstance(x, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def route_hash_blocked(blocked_routes: List[Dict[str, object]], route_hash: str) -> bool:
    return route_hash in {str(x.get("route_hash")) for x in blocked_routes if isinstance(x, dict)}


def build_candidates(
    *,
    closed_route_hash: str,
    closed_route_family: str,
    vault_item_count: int,
    blocked_route_count: int,
    lesson_count: int,
) -> List[Dict[str, object]]:
    candidates: List[Dict[str, object]] = []

    # RD8_01 is deliberately not another market-state route. It is a governance-contract builder
    # for a new policy-locked direction, selected by strict constraints before any execution.
    rows = [
        {
            "research_key": "RD8_01_POLICY_LOCKED_RESEARCH_DIRECTION_CONTRACT_BUILDER",
            "next_module": "edge_factory_os_policy_locked_research_direction_contract_builder_v1.py",
            "direction_type": "GOVERNANCE_CONTRACT_BUILDER",
            "route_family": "POLICY_LOCKED_MATERIAL_DIFFERENCE_SELECTION",
            "priority": 100,
            "reason": "Build a new materially different research contract only after restricted route closure; no execution.",
            "materially_different_from_closed_route": True,
        },
        {
            "research_key": "RD8_02_EXTERNAL_AUDIT_PACKET_REFRESH",
            "next_module": "edge_factory_os_external_audit_packet_refresh_v1.py",
            "direction_type": "AUDIT_PACKET",
            "route_family": "METHODOLOGY_AUDIT_FAMILY",
            "priority": 92,
            "reason": "Refresh adversarial audit packet after restricted retest and governance chain updates.",
            "materially_different_from_closed_route": True,
        },
        {
            "research_key": "RD8_03_SOURCE_PANEL_INFORMATION_QUALITY_REVIEW",
            "next_module": "edge_factory_os_source_panel_information_quality_review_contract_builder_v1.py",
            "direction_type": "DATA_INFORMATION_REVIEW",
            "route_family": "SOURCE_PANEL_INFORMATION_QUALITY_FAMILY",
            "priority": 84,
            "reason": "Investigate whether panel/features contain enough stable exploitable information before more strategy search.",
            "materially_different_from_closed_route": True,
        },
    ]

    for row in rows:
        route_payload = {
            "research_key": row["research_key"],
            "route_family": row["route_family"],
            "closed_route_hash": closed_route_hash,
            "closed_route_family": closed_route_family,
            "vault_item_count": vault_item_count,
            "blocked_route_count": blocked_route_count,
            "lesson_count": lesson_count,
            "policy_locked": True,
            "no_execution": True,
        }
        row["route_hash"] = stable_hash(route_payload)
        row["candidate_generation_allowed"] = False
        row["family_release_allowed"] = False
        row["runtime_touch_allowed"] = False
        row["capital_change_allowed"] = False
        row["active_paper_allowed"] = False
        row["live_allowed"] = False
        row["real_orders_allowed"] = False
        candidates.append(row)

    return candidates


def build_text(result: Dict[str, object]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS POLICY-LOCKED RESEARCH ROTATION AFTER RESTRICTED RETEST v1")
    lines.append("=" * 100)

    for key in [
        "rotation_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "closed_route_hash",
        "closed_route_family",
        "restricted_route_closed",
        "additional_null_budget_allowed_now",
        "release_allowed",
        "candidate_direction_count",
        "selected_research_key",
        "selected_route_hash",
        "selected_next_module",
        "broad_strategy_search_allowed",
        "research_execution_allowed_now",
        "candidate_generation_allowed",
        "family_release_allowed",
        "runtime_touch_allowed",
        "capital_change_allowed",
        "active_paper_allowed",
        "live_allowed",
        "real_orders_allowed",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("CANDIDATE DIRECTIONS")
    lines.append("-" * 100)
    for row in result.get("candidate_rows", []):
        if isinstance(row, dict):
            lines.append(
                f"{row.get('priority')} | {row.get('research_key')} | "
                f"{row.get('route_family')} | {row.get('next_module')}"
            )

    lines.append("")
    lines.append("CORE DECISION")
    lines.append("-" * 100)
    lines.append("The restricted market-state route is closed for release.")
    lines.append("No more null budget is allowed now.")
    lines.append("The next step is a policy-locked, materially different contract builder, not execution.")
    lines.append("All trading/release/runtime/capital/live actions remain blocked.")

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
        "candidates_csv",
        "rotation_state_json",
        "rotation_queue_json",
        "closed_route_registry_json",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, object]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS POLICY-LOCKED RESEARCH ROTATION AFTER RESTRICTED RETEST v1")
    print("=" * 100)
    print(f"rotation_status: {result.get('rotation_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"closed_route_hash: {result.get('closed_route_hash')}")
    print(f"closed_route_family: {result.get('closed_route_family')}")
    print(f"restricted_route_closed: {result.get('restricted_route_closed')}")
    print(f"additional_null_budget_allowed_now: {result.get('additional_null_budget_allowed_now')}")
    print(f"release_allowed: {result.get('release_allowed')}")
    print(f"candidate_direction_count: {result.get('candidate_direction_count')}")
    print(f"selected_research_key: {result.get('selected_research_key')}")
    print(f"selected_route_hash: {result.get('selected_route_hash')}")
    print(f"selected_next_module: {result.get('selected_next_module')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        print(f"{key}: {value}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"CSV : {result.get('candidates_csv')}")
    print(f"QUEUE: {result.get('rotation_queue_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    feasibility = load_json(FEASIBILITY_JSON, {})
    feasibility_state = load_json(FEASIBILITY_STATE_JSON, {})
    retest_eval_state = load_json(RESTRICTED_RETEST_EVALUATOR_STATE_JSON, {})
    retest_state = load_json(RESTRICTED_RETEST_STATE_JSON, {})
    budget_consumption = load_json(RESTRICTED_BUDGET_CONSUMPTION_JSON, {})
    ledger = load_json(GLOBAL_LEDGER_JSON, {})
    alpha_accounting = load_json(GLOBAL_ALPHA_ACCOUNTING_JSON, {})
    alpha_policy = load_json(GLOBAL_ALPHA_POLICY_JSON, {})
    vault = load_json(PROMISING_VAULT_JSON, {})
    reopen_policy = load_json(GOVERNED_REOPEN_POLICY_JSON, {})
    pre_reg_policy = load_json(PRE_REG_POLICY_JSON, {})
    nested = load_json(NESTED_VALIDATION_POLICY_JSON, {})
    holdout_registry = load_json(UNTOUCHED_HOLDOUT_REGISTRY_JSON, {})
    holdout_access = load_json(HOLDOUT_ACCESS_CONTROL_JSON, {})

    lessons = extract_list(load_json(LESSON_INDEX_JSON, {}), "lessons")
    blocked_routes = extract_list(load_json(BLOCKLIST_JSON, {}), "blocked_routes")
    vault_items = extract_list(vault, "vault_items")

    closed_route_hash = str(feasibility.get("route_hash") or feasibility_state.get("route_hash") or "")
    closed_route_family = str(feasibility.get("route_family") or feasibility_state.get("route_family") or "")
    route_closed = feasibility.get("route_closed") is True and feasibility_state.get("route_closed") is True
    additional_null_budget_allowed_now = feasibility.get("additional_null_budget_allowed_now") is True

    prerequisites = {
        "feasibility_route_closed": route_closed,
        "additional_null_budget_not_allowed": feasibility.get("additional_null_budget_allowed_now") is False,
        "additional_null_power_not_recommended": feasibility.get("additional_null_power_recommended") is False,
        "release_blocked": feasibility.get("release_allowed") is False,
        "route_budget_consumed": feasibility.get("route_budget_consumed") is True,
        "closed_route_hash_present": bool(closed_route_hash),
        "closed_route_family_market_state": closed_route_family == "MARKET_STATE_TRANSITION_FAMILY",
        "route_in_blocklist": route_hash_blocked(blocked_routes, closed_route_hash),
        "retest_underpowered": retest_eval_state.get("decision_class") == "UNDERPOWERED_FOR_TINY_GLOBAL_ALPHA_ROUTE_BUDGET_CONSUMED",
        "budget_consumed_once": budget_consumption.get("route_budget_consumed") == 1,
        "global_ledger_active": ledger.get("ledger_status") == "GLOBAL_MULTIPLE_TESTING_LEDGER_ACTIVE_RESEARCH_LOCKED",
        "alpha_accounting_pass": alpha_accounting.get("global_alpha_accounting_pass") is True,
        "alpha_policy_active": alpha_policy.get("policy_status") == "GLOBAL_ALPHA_SPENDING_POLICY_ACTIVE_ZERO_STRATEGY_BUDGET",
        "vault_active": vault.get("vault_status") == "PROMISING_SIGNAL_VAULT_ACTIVE_RELEASE_BLOCKED",
        "reopen_policy_restricted": reopen_policy.get("policy_status") == "GOVERNED_RESEARCH_REOPEN_POLICY_ACTIVE_RESTRICTED_CONTRACTS_ONLY",
        "pre_registration_required": pre_reg_policy.get("all_future_research_must_be_pre_registered") is True,
        "nested_ready": nested.get("policy_status") == "NESTED_VALIDATION_POLICY_READY_STRATEGY_SEARCH_LOCKED",
        "holdout_not_selected": holdout_registry.get("holdout_selected") is False,
        "holdout_not_peeked": holdout_registry.get("holdout_peeked") is False,
        "holdout_access_blocked": holdout_access.get("holdout_access_allowed_now") is False,
    }

    prerequisite_pass = all(prerequisites.values())

    candidate_rows = build_candidates(
        closed_route_hash=closed_route_hash,
        closed_route_family=closed_route_family,
        vault_item_count=len(vault_items),
        blocked_route_count=len(blocked_routes),
        lesson_count=len(lessons),
    )

    for row in candidate_rows:
        row["route_hash_blocked"] = route_hash_blocked(blocked_routes, str(row.get("route_hash")))

    selectable = [
        row for row in candidate_rows
        if row.get("materially_different_from_closed_route") is True
        and row.get("route_hash_blocked") is False
    ]

    selected = selectable[0] if selectable and prerequisite_pass else {}

    if prerequisite_pass and selected:
        rotation_status = "POLICY_LOCKED_RESEARCH_ROTATION_READY_MATERIAL_DIFFERENT_DIRECTION_SELECTED"
        severity = "ATTENTION"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        next_action = "BUILD_POLICY_LOCKED_RESEARCH_DIRECTION_CONTRACT_NO_EXECUTION"
        reason = "restricted market-state route closed; no more null budget; selected materially different policy-locked direction"
        return_code = 0
    else:
        rotation_status = "POLICY_LOCKED_RESEARCH_ROTATION_BLOCKED_REVIEW_REQUIRED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_POLICY_LOCKED_ROTATION_PREREQUISITES_NO_RELEASE"
        reason = f"prerequisites={prerequisites}; selectable_count={len(selectable)}"
        return_code = 2

    closed_route_registry = {
        "registry_name": "edge_factory_os_restricted_retest_closed_route_registry_v1",
        "created_at_utc": utc_now_iso(),
        "registry_status": "RESTRICTED_RETEST_CLOSED_ROUTE_REGISTERED",
        "closed_route_hash": closed_route_hash,
        "closed_route_family": closed_route_family,
        "closed_decision_class": feasibility.get("decision_class"),
        "reason": feasibility.get("reason"),
        "additional_null_budget_allowed_now": False,
        "release_allowed": False,
        "preservation_status": "PRESERVED_AS_UNDERPOWERED_NOT_VALIDATED_STRUCTURE_HINT",
        "do_not_repeat_without": [
            "new_governance_budget_decision",
            "new_route_hash_or_explicit_reopen_approval",
            "new pre-registered materially different contract",
            "null-power feasibility pass",
            "no holdout access",
        ],
        **SAFETY_FLAGS,
    }

    rotation_state = {
        "state_name": "edge_factory_os_policy_locked_research_rotation_after_restricted_retest_state_v1",
        "created_at_utc": utc_now_iso(),
        "rotation_status": rotation_status,
        "strict_policy_key": STRICT_POLICY_KEY,
        "closed_route_hash": closed_route_hash,
        "closed_route_family": closed_route_family,
        "restricted_route_closed": route_closed,
        "additional_null_budget_allowed_now": False,
        "release_allowed": False,
        "candidate_direction_count": len(candidate_rows),
        "selected_research_key": selected.get("research_key"),
        "selected_route_hash": selected.get("route_hash"),
        "selected_next_module": selected.get("next_module"),
        "broad_strategy_search_allowed": False,
        "research_execution_allowed_now": False,
        "next_recommended_research_key": NEXT_RESEARCH_KEY if prerequisite_pass and selected else None,
        "next_module": NEXT_MODULE if prerequisite_pass and selected else None,
        **SAFETY_FLAGS,
    }

    rotation_queue = {
        "queue_name": "edge_factory_os_policy_locked_research_rotation_after_restricted_retest_queue_v1",
        "created_at_utc": utc_now_iso(),
        "queue_status": "POLICY_LOCKED_ROTATION_QUEUE_READY" if prerequisite_pass and selected else "POLICY_LOCKED_ROTATION_QUEUE_BLOCKED",
        "closed_route_hash": closed_route_hash,
        "closed_route_family": closed_route_family,
        "additional_null_budget_allowed_now": False,
        "broad_strategy_search_allowed": False,
        "research_execution_allowed_now": False,
        "selected_research_key": selected.get("research_key"),
        "selected_route_hash": selected.get("route_hash"),
        "selected_next_module": selected.get("next_module"),
        "candidate_rows": candidate_rows,
        "next_steps": [
            {
                "research_key": selected.get("research_key"),
                "route_hash": selected.get("route_hash"),
                "module": selected.get("next_module"),
                "priority": selected.get("priority"),
                "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
                "purpose": selected.get("reason"),
                "research_execution_allowed_now": False,
                "candidate_generation_allowed": False,
                "family_release_allowed": False,
                "runtime_touch_allowed": False,
                "capital_change_allowed": False,
                "active_paper_allowed": False,
                "live_allowed": False,
                "real_orders_allowed": False,
            }
        ] if selected else [],
        **SAFETY_FLAGS,
    }

    write_json(REPO_CLOSED_ROUTE_REGISTRY_JSON, closed_route_registry)
    write_json(REPO_ROTATION_STATE_JSON, rotation_state)
    write_json(REPO_ROTATION_QUEUE_JSON, rotation_queue)
    write_csv(OUT_CANDIDATES_CSV, candidate_rows)

    result = {
        "rotation_name": "edge_factory_os_policy_locked_research_rotation_after_restricted_retest_v1",
        "created_at_utc": utc_now_iso(),
        "rotation_status": rotation_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "strict_policy_key": STRICT_POLICY_KEY,
        "closed_route_hash": closed_route_hash,
        "closed_route_family": closed_route_family,
        "restricted_route_closed": route_closed,
        "additional_null_budget_allowed_now": False,
        "release_allowed": False,
        "candidate_direction_count": len(candidate_rows),
        "selectable_direction_count": len(selectable),
        "selected_research_key": selected.get("research_key"),
        "selected_route_hash": selected.get("route_hash"),
        "selected_next_module": selected.get("next_module"),
        "prerequisites": prerequisites,
        "candidate_rows": candidate_rows,
        "rotation_state": rotation_state,
        "rotation_queue": rotation_queue,
        "closed_route_registry": closed_route_registry,
        "broad_strategy_search_allowed": False,
        "research_execution_allowed_now": False,
        "next_recommended_research_key": NEXT_RESEARCH_KEY if prerequisite_pass and selected else None,
        "next_module": NEXT_MODULE if prerequisite_pass and selected else None,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "candidates_csv": str(OUT_CANDIDATES_CSV),
        "rotation_state_json": str(REPO_ROTATION_STATE_JSON),
        "rotation_queue_json": str(REPO_ROTATION_QUEUE_JSON),
        "closed_route_registry_json": str(REPO_CLOSED_ROUTE_REGISTRY_JSON),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text(result))
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
