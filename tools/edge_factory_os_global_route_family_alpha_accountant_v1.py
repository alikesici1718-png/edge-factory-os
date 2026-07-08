#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Global Route-Family Alpha Accountant v1

Purpose:
- Consume global multiple-testing ledger, research budget policy, promising vault,
  pre-registration governance, untouched holdout registry, and nested validation policy.
- Build global route-family alpha accounting.
- Assign zero strategy-search budget until governance chain is complete.
- Preserve promising-but-unvalidated ideas without release.
- Prepare future alpha allocation rules for pre-registered redesign only.
- Keep candidate/family/runtime/capital/active-paper/live/real-order actions blocked.

This module does NOT:
- run strategy research
- generate candidates
- create candidate contracts
- release families
- touch runtime
- change capital
- expose or use final holdout
- start active paper
- enable live
- place real orders
- delete/move/archive files
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

FRAMEWORK_DIR = REPO_DIR / "edge_factory_os_framework"
POLICY_DIR = FRAMEWORK_DIR / "policies"
REGISTRY_DIR = FRAMEWORK_DIR / "registries"
QUEUE_DIR = FRAMEWORK_DIR / "queues"

LEDGER_JSON = POLICY_DIR / "global_multiple_testing_ledger_v1.json"
RESEARCH_BUDGET_JSON = POLICY_DIR / "research_budget_policy_v1.json"
PROMISING_VAULT_JSON = POLICY_DIR / "promising_signal_vault_v1.json"
ANTI_OVERFIT_JSON = POLICY_DIR / "anti_overfitting_governance_state_v1.json"
PRE_REG_GOVERNANCE_JSON = POLICY_DIR / "pre_registered_research_redesign_governance_state_v1.json"
NESTED_VALIDATION_JSON = POLICY_DIR / "nested_validation_policy_v1.json"
HOLDOUT_ACCESS_JSON = POLICY_DIR / "holdout_access_control_policy_v1.json"
HOLDOUT_COMMITMENT_JSON = POLICY_DIR / "holdout_commitment_protocol_v1.json"
UNTOUCHED_HOLDOUT_REGISTRY_JSON = REGISTRY_DIR / "untouched_holdout_registry_v1.json"
HOLDOUT_NEXT_QUEUE_JSON = QUEUE_DIR / "holdout_nested_validation_next_queue_v1.json"

LESSON_INDEX_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

OUT_DIR = BASE_DIR / "edge_factory_os_global_route_family_alpha_accountant"
OUT_JSON = OUT_DIR / "global_route_family_alpha_accountant_latest.json"
OUT_TXT = OUT_DIR / "global_route_family_alpha_accountant_latest.txt"
OUT_FAMILY_CSV = OUT_DIR / "global_route_family_alpha_accounting_latest.csv"
OUT_GATES_CSV = OUT_DIR / "global_route_family_alpha_accounting_gates_latest.csv"

REPO_ALPHA_ACCOUNTING_JSON = POLICY_DIR / "global_route_family_alpha_accounting_v1.json"
REPO_ALPHA_POLICY_JSON = POLICY_DIR / "global_alpha_spending_policy_v1.json"
REPO_NEXT_QUEUE_JSON = QUEUE_DIR / "global_alpha_accounting_next_queue_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD7_04_GOVERNED_RESEARCH_REOPEN_GATE"
NEXT_MODULE = "edge_factory_os_governed_research_reopen_gate_v1.py"

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


def stable_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def extract_list(obj: Any, key: str) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get(key), list):
        return [x for x in obj[key] if isinstance(x, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def classify_route_family(row: Dict[str, Any]) -> str:
    text = " ".join(str(row.get(k, "")) for k in ["research_branch", "research_key", "blocked_reason", "lesson_id"]).lower()

    if "market_state" in text or "transition" in text:
        return "MARKET_STATE_TRANSITION_FAMILY"
    if "source_panel_anomaly" in text or "anomaly" in text:
        return "SOURCE_PANEL_ANOMALY_FAMILY"
    if "null" in text or "permutation" in text:
        return "NULL_BASELINE_METHOD_FAMILY"
    if "motif" in text:
        return "LABEL_FREE_EVENT_MOTIF_FAMILY"
    if "regime" in text or "cluster" in text:
        return "REGIME_CLUSTER_FAMILY"
    if "symbol" in text or "microstructure" in text:
        return "SYMBOL_MICROSTRUCTURE_FAMILY"
    if "calm" in text or "low_vol" in text:
        return "CALM_LOW_VOL_FAMILY"
    if "exit" in text or "risk_shape" in text:
        return "EXIT_RISK_SHAPE_FAMILY"
    if "mean_reversion" in text:
        return "MEAN_REVERSION_FAMILY"
    if "impulse" in text:
        return "IMPULSE_FAMILY"
    return "OTHER_OR_UNKNOWN_RESEARCH_FAMILY"


def gate(key: str, passed: bool, observed: Any, required: Any) -> Dict[str, Any]:
    return {
        "gate_key": key,
        "passed": bool(passed),
        "observed": observed,
        "required": required,
    }


def safety_flags_all_false(obj: Dict[str, Any], label: str) -> List[Dict[str, Any]]:
    rows = []
    for key, required in SAFETY_FLAGS.items():
        rows.append({
            "gate_key": f"{label}_{key.upper()}_FALSE",
            "passed": obj.get(key, False) is False,
            "observed": obj.get(key, False),
            "required": False,
        })
    return rows


def build_family_accounting(
    *,
    blocked_routes: List[Dict[str, Any]],
    vault_items: List[Dict[str, Any]],
    ledger: Dict[str, Any],
) -> List[Dict[str, Any]]:
    family_map: Dict[str, Dict[str, Any]] = {}

    for row in blocked_routes:
        fam = classify_route_family(row)
        rec = family_map.setdefault(fam, {
            "route_family": fam,
            "blocked_route_count": 0,
            "vault_item_count": 0,
            "known_procedural_null_fail_count": 0,
            "known_deep_validation_fail_count": 0,
            "known_release_block_count": 0,
            "current_alpha_budget": 0.0,
            "current_strategy_search_budget": 0,
            "future_reopen_allowed": False,
            "requires_pre_registration": True,
            "requires_nested_validation": True,
            "requires_untouched_holdout": True,
            "requires_procedural_null": True,
            "requires_global_alpha_accounting": True,
            "candidate_generation_allowed": False,
            "family_release_allowed": False,
            "runtime_touch_allowed": False,
            "capital_change_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
        })

        rec["blocked_route_count"] += 1
        reason = str(row.get("blocked_reason", "")).lower()
        failed = " ".join(str(x) for x in row.get("failed_gate_keys", [])) if isinstance(row.get("failed_gate_keys"), list) else str(row.get("failed_gate_keys", ""))

        if "procedural" in reason or "joint_null" in reason or "PROCEDURAL_NULL" in failed:
            rec["known_procedural_null_fail_count"] += 1
        if "deep_validation" in reason or "deep" in failed.lower():
            rec["known_deep_validation_fail_count"] += 1
        if row.get("release_allowed") is False or row.get("route_closed_for_release") is True:
            rec["known_release_block_count"] += 1

    for item in vault_items:
        fam = classify_route_family({
            "research_branch": item.get("vault_class"),
            "research_key": item.get("source_research_key"),
            "blocked_reason": item.get("why_blocked_for_release"),
            "lesson_id": item.get("vault_item_id"),
        })
        rec = family_map.setdefault(fam, {
            "route_family": fam,
            "blocked_route_count": 0,
            "vault_item_count": 0,
            "known_procedural_null_fail_count": 0,
            "known_deep_validation_fail_count": 0,
            "known_release_block_count": 0,
            "current_alpha_budget": 0.0,
            "current_strategy_search_budget": 0,
            "future_reopen_allowed": False,
            "requires_pre_registration": True,
            "requires_nested_validation": True,
            "requires_untouched_holdout": True,
            "requires_procedural_null": True,
            "requires_global_alpha_accounting": True,
            "candidate_generation_allowed": False,
            "family_release_allowed": False,
            "runtime_touch_allowed": False,
            "capital_change_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
        })
        rec["vault_item_count"] += 1

    effective_comparisons = int(
        ledger.get("global_testing_pressure", {}).get("effective_comparison_count") or
        max(1, sum(x["blocked_route_count"] for x in family_map.values()))
    )

    global_alpha = float(ledger.get("global_testing_pressure", {}).get("familywise_alpha") or 0.05)
    diagnostic_alpha = global_alpha / max(1, effective_comparisons)

    for rec in family_map.values():
        rec["effective_global_comparison_count"] = effective_comparisons
        rec["familywise_alpha"] = global_alpha
        rec["diagnostic_alpha_after_pressure"] = diagnostic_alpha
        rec["current_alpha_budget"] = 0.0
        rec["current_strategy_search_budget"] = 0
        rec["future_reopen_allowed"] = False
        rec["reopen_requirements"] = [
            "governed_research_reopen_gate_pass",
            "fresh_pre_registered_contract",
            "explicit_route_family_alpha_allocation",
            "nested_validation_plan",
            "untouched_holdout_registry_active_not_peeked",
            "procedural_null_plan",
            "promising_vault_consumed_if_using_prior_hint",
            "same_route_hash_blocked",
            "candidate/family/runtime/capital/live remain blocked",
        ]

    return sorted(family_map.values(), key=lambda r: (r["blocked_route_count"], r["vault_item_count"]), reverse=True)


def build_text(result: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS GLOBAL ROUTE-FAMILY ALPHA ACCOUNTANT v1")
    lines.append("=" * 100)

    for key in [
        "accountant_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "global_alpha_accounting_pass",
        "family_count",
        "blocked_route_count",
        "vault_item_count",
        "effective_comparison_count",
        "familywise_alpha",
        "diagnostic_alpha_after_pressure",
        "strategy_search_allowed_now",
        "methodology_repair_allowed_now",
        "future_strategy_reopen_allowed_now",
        "next_recommended_research_key",
        "next_module",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("ROUTE FAMILY SUMMARY")
    lines.append("-" * 100)
    for fam in result.get("family_rows", []):
        lines.append(
            f"{fam.get('route_family')}: blocked={fam.get('blocked_route_count')} "
            f"vault={fam.get('vault_item_count')} alpha_budget={fam.get('current_alpha_budget')} "
            f"search_budget={fam.get('current_strategy_search_budget')}"
        )

    lines.append("")
    lines.append("FAILED GATES")
    lines.append("-" * 100)
    for gate_key in result.get("failed_gate_keys", []):
        lines.append(f"- {gate_key}")

    lines.append("")
    lines.append("CORE DECISION")
    lines.append("-" * 100)
    lines.append("No route family receives strategy-search budget yet.")
    lines.append("No prior promising idea is deleted.")
    lines.append("Any future research must pass governed reopen gate before alpha can be allocated.")
    lines.append("All release/candidate/runtime/capital/live actions remain blocked.")

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
        "family_csv",
        "gates_csv",
        "alpha_accounting_json",
        "alpha_policy_json",
        "next_queue_json",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS GLOBAL ROUTE-FAMILY ALPHA ACCOUNTANT v1")
    print("=" * 100)
    print(f"accountant_status: {result.get('accountant_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"global_alpha_accounting_pass: {result.get('global_alpha_accounting_pass')}")
    print(f"family_count: {result.get('family_count')}")
    print(f"blocked_route_count: {result.get('blocked_route_count')}")
    print(f"vault_item_count: {result.get('vault_item_count')}")
    print(f"effective_comparison_count: {result.get('effective_comparison_count')}")
    print(f"familywise_alpha: {result.get('familywise_alpha')}")
    print(f"diagnostic_alpha_after_pressure: {result.get('diagnostic_alpha_after_pressure')}")
    print(f"strategy_search_allowed_now: {result.get('strategy_search_allowed_now')}")
    print(f"methodology_repair_allowed_now: {result.get('methodology_repair_allowed_now')}")
    print(f"future_strategy_reopen_allowed_now: {result.get('future_strategy_reopen_allowed_now')}")
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
    print(f"CSV : {result.get('family_csv')}")
    print(f"ALPHA: {result.get('alpha_accounting_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    ledger = load_json(LEDGER_JSON, {})
    budget = load_json(RESEARCH_BUDGET_JSON, {})
    vault = load_json(PROMISING_VAULT_JSON, {})
    anti = load_json(ANTI_OVERFIT_JSON, {})
    pre_reg_gov = load_json(PRE_REG_GOVERNANCE_JSON, {})
    nested = load_json(NESTED_VALIDATION_JSON, {})
    holdout_access = load_json(HOLDOUT_ACCESS_JSON, {})
    holdout_commitment = load_json(HOLDOUT_COMMITMENT_JSON, {})
    holdout_registry = load_json(UNTOUCHED_HOLDOUT_REGISTRY_JSON, {})
    holdout_queue = load_json(HOLDOUT_NEXT_QUEUE_JSON, {})
    lessons = extract_list(load_json(LESSON_INDEX_JSON, {}), "lessons")
    blocked_routes = extract_list(load_json(BLOCKLIST_JSON, {}), "blocked_routes")
    vault_items = extract_list(vault, "vault_items")

    family_rows = build_family_accounting(
        blocked_routes=blocked_routes,
        vault_items=vault_items,
        ledger=ledger,
    )

    effective_comparison_count = int(ledger.get("global_testing_pressure", {}).get("effective_comparison_count") or 1)
    familywise_alpha = float(ledger.get("global_testing_pressure", {}).get("familywise_alpha") or 0.05)
    diagnostic_alpha_after_pressure = float(
        ledger.get("global_testing_pressure", {}).get("diagnostic_alpha_after_pressure")
        or familywise_alpha / max(1, effective_comparison_count)
    )

    gates: List[Dict[str, Any]] = [
        gate("LEDGER_ACTIVE", ledger.get("ledger_status") == "GLOBAL_MULTIPLE_TESTING_LEDGER_ACTIVE_RESEARCH_LOCKED", ledger.get("ledger_status"), "GLOBAL_MULTIPLE_TESTING_LEDGER_ACTIVE_RESEARCH_LOCKED"),
        gate("RESEARCH_BUDGET_ACTIVE", budget.get("policy_status") == "RESEARCH_BUDGET_POLICY_ACTIVE_METHODOLOGY_ONLY", budget.get("policy_status"), "RESEARCH_BUDGET_POLICY_ACTIVE_METHODOLOGY_ONLY"),
        gate("STRATEGY_BUDGET_LOCKED", budget.get("research_budget_status") == "STRATEGY_SEARCH_BUDGET_LOCKED_UNTIL_GOVERNANCE_REPAIR", budget.get("research_budget_status"), "STRATEGY_SEARCH_BUDGET_LOCKED_UNTIL_GOVERNANCE_REPAIR"),
        gate("VAULT_ACTIVE", vault.get("vault_status") == "PROMISING_SIGNAL_VAULT_ACTIVE_RELEASE_BLOCKED", vault.get("vault_status"), "PROMISING_SIGNAL_VAULT_ACTIVE_RELEASE_BLOCKED"),
        gate("VAULT_ITEM_PRESERVED", len(vault_items) >= 1, len(vault_items), ">=1"),
        gate("ANTI_OVERFIT_ACTIVE", anti.get("state_status") == "ANTI_OVERFITTING_GOVERNANCE_ACTIVE_RESEARCH_REPAIR_REQUIRED", anti.get("state_status"), "ANTI_OVERFITTING_GOVERNANCE_ACTIVE_RESEARCH_REPAIR_REQUIRED"),
        gate("PRE_REG_GOVERNANCE_PASS", pre_reg_gov.get("governance_gate_pass") is True, pre_reg_gov.get("governance_gate_pass"), True),
        gate("NESTED_VALIDATION_READY", nested.get("policy_status") == "NESTED_VALIDATION_POLICY_READY_STRATEGY_SEARCH_LOCKED", nested.get("policy_status"), "NESTED_VALIDATION_POLICY_READY_STRATEGY_SEARCH_LOCKED"),
        gate("HOLDOUT_ACCESS_BLOCKED", holdout_access.get("holdout_access_allowed_now") is False, holdout_access.get("holdout_access_allowed_now"), False),
        gate("HOLDOUT_NOT_SELECTED", holdout_registry.get("holdout_selected") is False, holdout_registry.get("holdout_selected"), False),
        gate("HOLDOUT_NOT_PEEKED", holdout_registry.get("holdout_peeked") is False, holdout_registry.get("holdout_peeked"), False),
        gate("HOLDOUT_NOT_USABLE_NOW", holdout_registry.get("holdout_usable_now") is False, holdout_registry.get("holdout_usable_now"), False),
        gate("HOLDOUT_COMMITMENT_READY_NO_SELECTION", holdout_commitment.get("protocol_status") == "HOLDOUT_COMMITMENT_PROTOCOL_READY_NO_HOLDOUT_SELECTED", holdout_commitment.get("protocol_status"), "HOLDOUT_COMMITMENT_PROTOCOL_READY_NO_HOLDOUT_SELECTED"),
        gate("HOLDOUT_NEXT_QUEUE_READY", holdout_queue.get("queue_status") == "HOLDOUT_NESTED_VALIDATION_NEXT_QUEUE_READY", holdout_queue.get("queue_status"), "HOLDOUT_NESTED_VALIDATION_NEXT_QUEUE_READY"),
        gate("BLOCKED_ROUTES_PRESENT", len(blocked_routes) >= 1, len(blocked_routes), ">=1"),
        gate("LESSONS_PRESENT", len(lessons) >= 1, len(lessons), ">=1"),
        gate("FAMILY_ACCOUNTING_HAS_ROWS", len(family_rows) >= 1, len(family_rows), ">=1"),
        gate("ALL_ROUTE_FAMILIES_HAVE_ZERO_STRATEGY_BUDGET", all(int(r.get("current_strategy_search_budget", -1)) == 0 for r in family_rows), [r.get("current_strategy_search_budget") for r in family_rows], "all 0"),
        gate("ALL_ROUTE_FAMILIES_HAVE_ZERO_ALPHA_BUDGET_NOW", all(float(r.get("current_alpha_budget", -1)) == 0.0 for r in family_rows), [r.get("current_alpha_budget") for r in family_rows], "all 0.0"),
    ]

    gates.extend(safety_flags_all_false(budget, "BUDGET"))
    gates.extend(safety_flags_all_false(anti, "ANTI_OVERFIT"))
    gates.extend(safety_flags_all_false(nested, "NESTED"))
    gates.extend(safety_flags_all_false(holdout_access, "HOLDOUT_ACCESS"))
    gates.extend(safety_flags_all_false(holdout_registry, "HOLDOUT_REGISTRY"))

    failed = [row["gate_key"] for row in gates if row["passed"] is not True]
    alpha_pass = len(failed) == 0

    if alpha_pass:
        accountant_status = "GLOBAL_ROUTE_FAMILY_ALPHA_ACCOUNTANT_READY_STRATEGY_SEARCH_STILL_LOCKED"
        severity = "ATTENTION"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        next_action = "BUILD_GOVERNED_RESEARCH_REOPEN_GATE_NO_STRATEGY_SEARCH"
        reason = "route-family alpha accounting is active; all current route families have zero strategy budget; promising ideas preserved; reopen requires separate governed gate"
        next_module = NEXT_MODULE
        return_code = 0
    else:
        accountant_status = "GLOBAL_ROUTE_FAMILY_ALPHA_ACCOUNTANT_REVIEW_REQUIRED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_ALPHA_ACCOUNTING_GATES_BEFORE_RESEARCH_REOPEN"
        reason = f"failed_gate_count={len(failed)}"
        next_module = None
        return_code = 2

    alpha_accounting = {
        "accounting_name": "edge_factory_os_global_route_family_alpha_accounting_v1",
        "created_at_utc": utc_now_iso(),
        "accounting_status": accountant_status,
        "strict_policy_key": STRICT_POLICY_KEY,
        "global_alpha_accounting_pass": alpha_pass,
        "strategy_search_allowed_now": False,
        "methodology_repair_allowed_now": alpha_pass,
        "future_strategy_reopen_allowed_now": False,
        "family_count": len(family_rows),
        "blocked_route_count": len(blocked_routes),
        "vault_item_count": len(vault_items),
        "lesson_count": len(lessons),
        "effective_comparison_count": effective_comparison_count,
        "familywise_alpha": familywise_alpha,
        "diagnostic_alpha_after_pressure": diagnostic_alpha_after_pressure,
        "route_family_rows": family_rows,
        "failed_gate_keys": failed,
        "rules": {
            "new_strategy_research_requires_reopen_gate": True,
            "alpha_allocation_before_research_required": True,
            "post_hoc_alpha_allocation_allowed": False,
            "same_route_hash_reuse_allowed": False,
            "promising_vault_can_request_redesign_but_not_release": True,
            "untouched_holdout_access_before_final_gate_allowed": False,
            "candidate_generation_allowed_now": False,
            "family_release_allowed_now": False,
            "runtime_touch_allowed_now": False,
            "capital_change_allowed_now": False,
            "active_paper_allowed_now": False,
            "live_allowed_now": False,
            "real_orders_allowed_now": False,
        },
        **SAFETY_FLAGS,
    }

    alpha_policy = {
        "policy_name": "edge_factory_os_global_alpha_spending_policy_v1",
        "created_at_utc": utc_now_iso(),
        "policy_status": "GLOBAL_ALPHA_SPENDING_POLICY_ACTIVE_ZERO_STRATEGY_BUDGET",
        "strategy_search_allowed_now": False,
        "methodology_repair_allowed_now": alpha_pass,
        "future_strategy_reopen_allowed_now": False,
        "current_total_strategy_alpha_budget": 0.0,
        "current_total_strategy_route_budget": 0,
        "global_familywise_alpha": familywise_alpha,
        "diagnostic_alpha_after_pressure": diagnostic_alpha_after_pressure,
        "allocation_rules": {
            "all_future_alpha_must_be_allocated_by_governed_reopen_gate": True,
            "all_future_alpha_must_reference_route_family": True,
            "all_future_alpha_must_reference_pre_registered_contract": True,
            "all_future_alpha_must_reference_nested_validation_plan": True,
            "all_future_alpha_must_reference_untouched_holdout_registry": True,
            "all_future_alpha_must_reference_promising_vault_if_reusing_hint": True,
            "broad_axis_search_requires_procedural_null": True,
            "unused_alpha_does_not_imply_release": True,
            "passing_alpha_gate_does_not_allow_live_or_capital": True,
        },
        "release_gate_feed": {
            "GLOBAL_ALPHA_SPENDING_POLICY_ACTIVE": True,
            "STRATEGY_SEARCH_ALLOWED_NOW": False,
            "METHODOLOGY_REPAIR_ALLOWED_NOW": alpha_pass,
            "FUTURE_REOPEN_ALLOWED_NOW": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_ALPHA_POLICY": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_ALPHA_POLICY": False,
            "FAMILY_RELEASE_ALLOWED_FROM_ALPHA_POLICY": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_ALPHA_POLICY": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_ALPHA_POLICY": False,
            "ACTIVE_PAPER_ALLOWED_FROM_ALPHA_POLICY": False,
            "LIVE_ALLOWED_FROM_ALPHA_POLICY": False,
            "REAL_ORDERS_ALLOWED_FROM_ALPHA_POLICY": False,
        },
        **SAFETY_FLAGS,
    }

    next_queue = {
        "queue_name": "edge_factory_os_global_alpha_accounting_next_queue_v1",
        "created_at_utc": utc_now_iso(),
        "queue_status": "GLOBAL_ALPHA_ACCOUNTING_NEXT_QUEUE_READY" if alpha_pass else "GLOBAL_ALPHA_ACCOUNTING_NEXT_QUEUE_BLOCKED_REVIEW_REQUIRED",
        "strategy_search_allowed_now": False,
        "methodology_repair_allowed_now": alpha_pass,
        "future_strategy_reopen_allowed_now": False,
        "top_next_research_key": NEXT_RESEARCH_KEY if alpha_pass else None,
        "top_next_module": NEXT_MODULE if alpha_pass else None,
        "next_steps": [
            {
                "research_key": NEXT_RESEARCH_KEY,
                "module": NEXT_MODULE,
                "priority": 100,
                "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
                "purpose": "Create final governed gate that decides whether any tightly pre-registered research can reopen with explicit alpha/budget allocation.",
                "strategy_search_allowed_now": False,
                "candidate_generation_allowed": False,
                "family_release_allowed": False,
                "runtime_touch_allowed": False,
                "capital_change_allowed": False,
                "active_paper_allowed": False,
                "live_allowed": False,
                "real_orders_allowed": False,
            }
        ] if alpha_pass else [],
        **SAFETY_FLAGS,
    }

    write_csv(OUT_FAMILY_CSV, family_rows)
    write_csv(OUT_GATES_CSV, gates)
    write_json(REPO_ALPHA_ACCOUNTING_JSON, alpha_accounting)
    write_json(REPO_ALPHA_POLICY_JSON, alpha_policy)
    write_json(REPO_NEXT_QUEUE_JSON, next_queue)

    result = {
        "accountant_name": "edge_factory_os_global_route_family_alpha_accountant_v1",
        "created_at_utc": utc_now_iso(),
        "accountant_status": accountant_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "strict_policy_key": STRICT_POLICY_KEY,
        "global_alpha_accounting_pass": alpha_pass,
        "family_count": len(family_rows),
        "blocked_route_count": len(blocked_routes),
        "vault_item_count": len(vault_items),
        "lesson_count": len(lessons),
        "effective_comparison_count": effective_comparison_count,
        "familywise_alpha": familywise_alpha,
        "diagnostic_alpha_after_pressure": diagnostic_alpha_after_pressure,
        "strategy_search_allowed_now": False,
        "methodology_repair_allowed_now": alpha_pass,
        "future_strategy_reopen_allowed_now": False,
        "failed_gate_keys": failed,
        "family_rows": family_rows,
        "gate_rows": gates,
        "next_recommended_research_key": NEXT_RESEARCH_KEY if alpha_pass else None,
        "next_module": next_module,
        "alpha_accounting": alpha_accounting,
        "alpha_policy": alpha_policy,
        "next_queue": next_queue,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "family_csv": str(OUT_FAMILY_CSV),
        "gates_csv": str(OUT_GATES_CSV),
        "alpha_accounting_json": str(REPO_ALPHA_ACCOUNTING_JSON),
        "alpha_policy_json": str(REPO_ALPHA_POLICY_JSON),
        "next_queue_json": str(REPO_NEXT_QUEUE_JSON),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text(result))
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
