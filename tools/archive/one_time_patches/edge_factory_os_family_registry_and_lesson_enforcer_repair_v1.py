#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Family Registry + Lesson Enforcer Repair v1

Purpose:
- Repair runtime family registry after external audit.
- Separate runtime family monitoring from failed/closed research routes.
- Explicitly protect old_short from unrelated research-route invalidation.
- Mark old_short as monitoring-only / not invalidated, not capital-approved.
- Mark impulse_long as negative/early-watch from prior monitoring.
- Mark market_relative_short as exposure/no-closed-sample attention.
- Mark weak_market_short as inconclusive / insufficient sample.
- Enforce lesson memory and route blocklist before any future route reuse.
- Do NOT run research.
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

HOLDOUT_VAULT_REPAIR_STATE_JSON = POLICY_DIR / "holdout_trigger_and_vault_status_repair_state_v1.json"
GOV_REPAIR_STATE_JSON = POLICY_DIR / "governance_repair_suite_ledger_alpha_prereg_state_v1.json"
LEDGER_ENFORCED_JSON = POLICY_DIR / "global_multiple_testing_ledger_enforced_v1.json"
ALPHA_ENFORCEMENT_JSON = POLICY_DIR / "global_alpha_accounting_enforcement_v1.json"
PREREG_ENFORCEMENT_JSON = POLICY_DIR / "pre_registration_enforcement_policy_v1.json"
HOLDOUT_TRIGGER_JSON = POLICY_DIR / "holdout_trigger_protocol_enforced_v1.json"
VAULT_STATUS_JSON = POLICY_DIR / "promising_signal_vault_validation_status_v1.json"
EXPLICIT_FLAG_POLICY_JSON = POLICY_DIR / "explicit_safety_flag_enforcement_policy_v1.json"
CLOSED_ROUTE_REGISTRY_JSON = POLICY_DIR / "restricted_retest_closed_route_registry_v1.json"

LESSON_INDEX_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

OUT_DIR = BASE_DIR / "edge_factory_os_family_registry_and_lesson_enforcer_repair"
OUT_JSON = OUT_DIR / "family_registry_and_lesson_enforcer_repair_latest.json"
OUT_TXT = OUT_DIR / "family_registry_and_lesson_enforcer_repair_latest.txt"

REPO_FAMILY_REGISTRY_JSON = REGISTRY_DIR / "runtime_family_registry_v1.json"
REPO_LESSON_ENFORCER_JSON = POLICY_DIR / "lesson_memory_route_enforcer_v1.json"
REPO_REPAIR_STATE_JSON = POLICY_DIR / "family_registry_and_lesson_enforcer_repair_state_v1.json"
REPO_REPAIR_MANIFEST_JSON = STATUS_DIR / "family_registry_and_lesson_enforcer_repair_manifest_v1.json"
REPO_NEXT_QUEUE_JSON = QUEUE_DIR / "family_registry_and_lesson_enforcer_repair_next_queue_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD8_07_RUNTIME_FAMILY_MONITOR_REFRESH_OLD_SHORT_AWARE"
NEXT_MODULE = "edge_factory_os_runtime_family_monitor_refresh_old_short_aware_v1.py"

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


def route_hash_blocked(blocked_routes: List[Dict[str, Any]], route_hash: str) -> bool:
    return route_hash in {str(x.get("route_hash")) for x in blocked_routes if isinstance(x, dict)}


def build_runtime_family_registry(closed_route_hash: str) -> Dict[str, Any]:
    family_rows = [
        {
            "family_key": "old_short",
            "family_type": "runtime_family",
            "audit_classification": "NOT_INVALIDATED_MONITORING_ONLY",
            "prior_monitoring_status": "OK_OR_POSITIVE_INFO_IN_PRIOR_MONITORING",
            "research_route_failure_applies": False,
            "protected_from_unrelated_research_route_failures": True,
            "capital_approved": False,
            "release_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
            "minimum_closed_trades_for_monitoring_decision": 20,
            "minimum_closed_trades_for_capital_review": 50,
            "required_before_capital_review": [
                "current_runtime_family_monitor_refresh",
                "family_specific_drift_review",
                "capital_governor_pass",
                "drawdown_review",
                "exposure_review",
                "no_new_runtime_errors",
                "no cross-contamination with failed research routes",
            ],
            "notes": [
                "Prior monitoring showed old_short as the strongest/cleanest family relative to others.",
                "It is not validated for capital increase by this registry.",
                "It must not be punished solely because market-state/source-panel research routes failed.",
                "It still needs current sample and governance review before any runtime/capital action.",
            ],
        },
        {
            "family_key": "impulse_long",
            "family_type": "runtime_family",
            "audit_classification": "NEGATIVE_OR_EARLY_WATCH",
            "prior_monitoring_status": "NEGATIVE_WATCH_IN_PRIOR_MONITORING",
            "research_route_failure_applies": False,
            "protected_from_unrelated_research_route_failures": False,
            "capital_approved": False,
            "release_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
            "minimum_closed_trades_for_monitoring_decision": 20,
            "minimum_closed_trades_for_capital_review": 50,
            "required_before_capital_review": [
                "escape negative watch",
                "current family-specific positive sample",
                "drift review",
                "capital governor pass",
            ],
            "notes": [
                "Previously flagged as early negative watch.",
                "No promotion/capital action allowed.",
            ],
        },
        {
            "family_key": "market_relative_short",
            "family_type": "runtime_family",
            "audit_classification": "EXPOSURE_OR_SAMPLE_ATTENTION",
            "prior_monitoring_status": "EXPOSURE_OR_NO_CLOSED_SAMPLE_ATTENTION",
            "research_route_failure_applies": False,
            "protected_from_unrelated_research_route_failures": False,
            "capital_approved": False,
            "release_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
            "minimum_closed_trades_for_monitoring_decision": 20,
            "minimum_closed_trades_for_capital_review": 50,
            "required_before_capital_review": [
                "closed sample maturity",
                "exposure normalization",
                "drift review",
                "capital governor pass",
            ],
            "notes": [
                "Prior status was not validated edge; sample/exposure review needed.",
            ],
        },
        {
            "family_key": "weak_market_short",
            "family_type": "runtime_family",
            "audit_classification": "INCONCLUSIVE_INSUFFICIENT_SAMPLE",
            "prior_monitoring_status": "LOW_OR_NO_SAMPLE",
            "research_route_failure_applies": False,
            "protected_from_unrelated_research_route_failures": False,
            "capital_approved": False,
            "release_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
            "minimum_closed_trades_for_monitoring_decision": 20,
            "minimum_closed_trades_for_capital_review": 50,
            "required_before_capital_review": [
                "closed sample maturity",
                "drift review",
                "capital governor pass",
            ],
            "notes": [
                "Insufficient sample; no decision.",
            ],
        },
    ]

    research_route_rows = [
        {
            "route_hash": closed_route_hash,
            "route_family": "MARKET_STATE_TRANSITION_FAMILY",
            "classification": "CLOSED_RESEARCH_ROUTE_NOT_RUNTIME_FAMILY",
            "release_allowed": False,
            "candidate_generation_allowed": False,
            "can_invalidate_old_short": False,
            "notes": [
                "Closed because restricted retest underpowered/not validated and more null power was not justified.",
                "This closure must not automatically invalidate old_short runtime family.",
            ],
        }
    ]

    return {
        "registry_name": "edge_factory_os_runtime_family_registry_v1",
        "created_at_utc": utc_now_iso(),
        "registry_status": "RUNTIME_FAMILY_REGISTRY_ACTIVE_OLD_SHORT_AWARE",
        "strict_policy_key": STRICT_POLICY_KEY,
        "family_count": len(family_rows),
        "runtime_family_rows": family_rows,
        "closed_research_route_rows": research_route_rows,
        "global_rules": {
            "runtime_family_monitoring_is_not_strategy_research": True,
            "research_route_failure_does_not_auto_invalidate_runtime_family": True,
            "old_short_requires_current_monitor_refresh_before_any_decision": True,
            "old_short_capital_review_requires_min_closed_trades": 50,
            "old_short_monitoring_decision_requires_min_closed_trades": 20,
            "capital_change_requires_separate_governor": True,
            "family_release_requires_separate_release_gate": True,
            "active_paper_requires_separate_gate": True,
            "live_requires_separate_gate": True,
        },
        "release_gate_feed": {
            "RUNTIME_FAMILY_REGISTRY_ACTIVE": True,
            "OLD_SHORT_INVALIDATED_BY_RESEARCH_FAILURES": False,
            "OLD_SHORT_CAPITAL_APPROVED": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_FAMILY_REGISTRY": False,
            "FAMILY_RELEASE_ALLOWED_FROM_FAMILY_REGISTRY": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_FAMILY_REGISTRY": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_FAMILY_REGISTRY": False,
            "ACTIVE_PAPER_ALLOWED_FROM_FAMILY_REGISTRY": False,
            "LIVE_ALLOWED_FROM_FAMILY_REGISTRY": False,
            "REAL_ORDERS_ALLOWED_FROM_FAMILY_REGISTRY": False,
        },
        **SAFETY_FLAGS,
    }


def build_lesson_enforcer(blocked_routes: List[Dict[str, Any]], lessons: List[Dict[str, Any]], closed_route_hash: str) -> Dict[str, Any]:
    blocked_hashes = sorted({str(x.get("route_hash")) for x in blocked_routes if x.get("route_hash")})
    lesson_ids = sorted({str(x.get("lesson_id")) for x in lessons if x.get("lesson_id")})

    return {
        "policy_name": "edge_factory_os_lesson_memory_route_enforcer_v1",
        "created_at_utc": utc_now_iso(),
        "policy_status": "LESSON_MEMORY_ROUTE_ENFORCER_ACTIVE",
        "blocked_route_count": len(blocked_hashes),
        "lesson_count": len(lesson_ids),
        "blocked_route_hashes": blocked_hashes,
        "closed_restricted_retest_route_hash": closed_route_hash,
        "closed_restricted_retest_route_blocked": closed_route_hash in blocked_hashes if closed_route_hash else False,
        "lesson_ids_sample": lesson_ids[:50],
        "hard_rules": {
            "missing_blocklist_check": "hard_fail",
            "missing_lesson_check": "hard_fail",
            "route_hash_in_blocklist": "blocked",
            "same_route_hash_reuse": "forbidden_without_explicit_governance_reopen",
            "same_route_family_research": "requires_material_difference_and_new_contract",
            "closed_route_retest": "forbidden_without_new_budget_and_reopen_gate",
            "lesson_memory_unavailable": "research_execution_blocked",
        },
        "required_preflight_for_future_research": [
            "load_lesson_memory_route_enforcer_v1",
            "load_candidate_route_blocklist",
            "load_lesson_memory_index",
            "verify_route_hash_not_blocked",
            "verify_material_difference_from_closed_routes",
            "verify pre-registration active",
            "verify ledger enforced non-null",
            "verify alpha explicit budget",
            "verify holdout access blocked",
        ],
        "release_gate_feed": {
            "LESSON_MEMORY_ROUTE_ENFORCER_ACTIVE": True,
            "BLOCKED_ROUTE_CHECK_REQUIRED": True,
            "LESSON_CHECK_REQUIRED": True,
            "CANDIDATE_GENERATION_ALLOWED_FROM_LESSON_ENFORCER": False,
            "FAMILY_RELEASE_ALLOWED_FROM_LESSON_ENFORCER": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_LESSON_ENFORCER": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_LESSON_ENFORCER": False,
            "ACTIVE_PAPER_ALLOWED_FROM_LESSON_ENFORCER": False,
            "LIVE_ALLOWED_FROM_LESSON_ENFORCER": False,
            "REAL_ORDERS_ALLOWED_FROM_LESSON_ENFORCER": False,
        },
        **SAFETY_FLAGS,
    }


def build_text(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS FAMILY REGISTRY + LESSON ENFORCER REPAIR v1")
    lines.append("=" * 100)

    for key in [
        "repair_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "family_registry_status",
        "lesson_enforcer_status",
        "family_count",
        "old_short_classification",
        "old_short_research_invalidation_applies",
        "old_short_capital_approved",
        "old_short_min_closed_trades_monitoring",
        "old_short_min_closed_trades_capital",
        "blocked_route_count",
        "lesson_count",
        "closed_route_hash",
        "closed_route_blocked",
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
    lines.append("old_short is not invalidated by unrelated research route failures.")
    lines.append("old_short is also not approved for capital/release/live by this module.")
    lines.append("Runtime family monitoring is separated from research-route validation.")
    lines.append("Lesson/blocklist checks are mandatory before future route reuse.")
    lines.append("No candidate, release, runtime, capital, active paper, live, or real order action is allowed.")

    lines.append("")
    lines.append("RUNTIME FAMILY REGISTRY")
    lines.append("-" * 100)
    lines.append(json.dumps(result.get("runtime_family_registry"), indent=2, ensure_ascii=False))

    lines.append("")
    lines.append("LESSON ENFORCER")
    lines.append("-" * 100)
    lines.append(json.dumps(result.get("lesson_enforcer"), indent=2, ensure_ascii=False))

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        lines.append(f"{key}: {value}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS FAMILY REGISTRY + LESSON ENFORCER REPAIR v1")
    print("=" * 100)
    print(f"repair_status: {result.get('repair_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"family_registry_status: {result.get('family_registry_status')}")
    print(f"lesson_enforcer_status: {result.get('lesson_enforcer_status')}")
    print(f"family_count: {result.get('family_count')}")
    print(f"old_short_classification: {result.get('old_short_classification')}")
    print(f"old_short_research_invalidation_applies: {result.get('old_short_research_invalidation_applies')}")
    print(f"old_short_capital_approved: {result.get('old_short_capital_approved')}")
    print(f"old_short_min_closed_trades_monitoring: {result.get('old_short_min_closed_trades_monitoring')}")
    print(f"old_short_min_closed_trades_capital: {result.get('old_short_min_closed_trades_capital')}")
    print(f"blocked_route_count: {result.get('blocked_route_count')}")
    print(f"lesson_count: {result.get('lesson_count')}")
    print(f"closed_route_hash: {result.get('closed_route_hash')}")
    print(f"closed_route_blocked: {result.get('closed_route_blocked')}")
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
    print(f"FAMILY_REGISTRY: {result.get('family_registry_json')}")
    print(f"LESSON_ENFORCER: {result.get('lesson_enforcer_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    STATUS_DIR.mkdir(parents=True, exist_ok=True)

    holdout_vault = load_json(HOLDOUT_VAULT_REPAIR_STATE_JSON, {})
    gov_repair = load_json(GOV_REPAIR_STATE_JSON, {})
    ledger = load_json(LEDGER_ENFORCED_JSON, {})
    alpha = load_json(ALPHA_ENFORCEMENT_JSON, {})
    prereg = load_json(PREREG_ENFORCEMENT_JSON, {})
    holdout_trigger = load_json(HOLDOUT_TRIGGER_JSON, {})
    vault_status = load_json(VAULT_STATUS_JSON, {})
    explicit_flags = load_json(EXPLICIT_FLAG_POLICY_JSON, {})
    closed_registry = load_json(CLOSED_ROUTE_REGISTRY_JSON, {})

    lessons = extract_list(load_json(LESSON_INDEX_JSON, {}), "lessons")
    blocked_routes = extract_list(load_json(BLOCKLIST_JSON, {}), "blocked_routes")

    closed_route_hash = str(closed_registry.get("closed_route_hash") or "")
    closed_route_blocked = route_hash_blocked(blocked_routes, closed_route_hash)

    runtime_family_registry = build_runtime_family_registry(closed_route_hash)
    lesson_enforcer = build_lesson_enforcer(blocked_routes, lessons, closed_route_hash)

    old_short_row = next(
        row for row in runtime_family_registry["runtime_family_rows"]
        if row["family_key"] == "old_short"
    )

    checks = {
        "HOLDOUT_VAULT_REPAIR_PASS": holdout_vault.get("repair_pass") is True,
        "GOV_REPAIR_PASS": gov_repair.get("repair_pass") is True,
        "LEDGER_ENFORCED": ledger.get("ledger_status") == "GLOBAL_MULTIPLE_TESTING_LEDGER_ENFORCED_NON_NULL",
        "ALPHA_RESEARCH_PASS_FALSE": alpha.get("research_execution_alpha_pass") is False,
        "PREREG_ACTIVE": prereg.get("policy_status") == "PRE_REGISTRATION_ENFORCEMENT_ACTIVE",
        "HOLDOUT_TRIGGER_ENFORCED": holdout_trigger.get("policy_status") == "HOLDOUT_TRIGGER_PROTOCOL_ENFORCED_ACCESS_BLOCKED",
        "VAULT_STATUS_ENFORCED": vault_status.get("vault_status") == "PROMISING_SIGNAL_VAULT_VALIDATION_STATUS_ENFORCED",
        "EXPLICIT_FLAGS_ACTIVE": explicit_flags.get("policy_status") == "EXPLICIT_SAFETY_FLAG_POLICY_ACTIVE",
        "FAMILY_REGISTRY_ACTIVE": runtime_family_registry.get("registry_status") == "RUNTIME_FAMILY_REGISTRY_ACTIVE_OLD_SHORT_AWARE",
        "LESSON_ENFORCER_ACTIVE": lesson_enforcer.get("policy_status") == "LESSON_MEMORY_ROUTE_ENFORCER_ACTIVE",
        "OLD_SHORT_NOT_INVALIDATED": old_short_row.get("research_route_failure_applies") is False,
        "OLD_SHORT_PROTECTED": old_short_row.get("protected_from_unrelated_research_route_failures") is True,
        "OLD_SHORT_NOT_CAPITAL_APPROVED": old_short_row.get("capital_approved") is False,
        "OLD_SHORT_MIN_MONITORING_20": old_short_row.get("minimum_closed_trades_for_monitoring_decision") == 20,
        "OLD_SHORT_MIN_CAPITAL_50": old_short_row.get("minimum_closed_trades_for_capital_review") == 50,
        "BLOCKLIST_PRESENT": len(blocked_routes) >= 1,
        "LESSONS_PRESENT": len(lessons) >= 1,
        "CLOSED_ROUTE_PRESENT": bool(closed_route_hash),
        "CLOSED_ROUTE_BLOCKED": closed_route_blocked is True,
    }

    failed = [k for k, v in checks.items() if v is not True]
    repair_pass = len(failed) == 0

    if repair_pass:
        repair_status = "FAMILY_REGISTRY_AND_LESSON_ENFORCER_REPAIR_PASS"
        severity = "ATTENTION"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        next_action = "BUILD_RUNTIME_FAMILY_MONITOR_REFRESH_OLD_SHORT_AWARE_NO_CAPITAL_ACTION"
        reason = "Runtime family registry and lesson route enforcer are active; old_short separated from research failures."
        next_key = NEXT_RESEARCH_KEY
        next_module = NEXT_MODULE
        return_code = 0
    else:
        repair_status = "FAMILY_REGISTRY_AND_LESSON_ENFORCER_REPAIR_FAIL_REVIEW_REQUIRED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_FAMILY_REGISTRY_OR_LESSON_ENFORCER_FAILURES"
        reason = f"failed_repair_keys={failed}"
        next_key = None
        next_module = None
        return_code = 2

    repair_state = {
        "state_name": "edge_factory_os_family_registry_and_lesson_enforcer_repair_state_v1",
        "created_at_utc": utc_now_iso(),
        "repair_status": repair_status,
        "strict_policy_key": STRICT_POLICY_KEY,
        "repair_pass": repair_pass,
        "failed_repair_count": len(failed),
        "failed_repair_keys": failed,
        "family_registry_status": runtime_family_registry["registry_status"],
        "lesson_enforcer_status": lesson_enforcer["policy_status"],
        "family_count": runtime_family_registry["family_count"],
        "old_short_classification": old_short_row["audit_classification"],
        "old_short_research_invalidation_applies": old_short_row["research_route_failure_applies"],
        "old_short_capital_approved": old_short_row["capital_approved"],
        "old_short_min_closed_trades_monitoring": old_short_row["minimum_closed_trades_for_monitoring_decision"],
        "old_short_min_closed_trades_capital": old_short_row["minimum_closed_trades_for_capital_review"],
        "blocked_route_count": len(blocked_routes),
        "lesson_count": len(lessons),
        "closed_route_hash": closed_route_hash,
        "closed_route_blocked": closed_route_blocked,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        **SAFETY_FLAGS,
    }

    manifest = {
        "manifest_name": "edge_factory_os_family_registry_and_lesson_enforcer_repair_manifest_v1",
        "created_at_utc": utc_now_iso(),
        "manifest_status": "FAMILY_REGISTRY_LESSON_ENFORCER_MANIFEST_READY" if repair_pass else "FAMILY_REGISTRY_LESSON_ENFORCER_MANIFEST_ATTENTION",
        "repair_mapping": {
            "external_audit_family_registry": "implemented",
            "external_audit_lesson_enforcer": "implemented",
            "old_short_runtime_family_separation": "implemented",
        },
        "repair_files": {
            "runtime_family_registry_json": str(REPO_FAMILY_REGISTRY_JSON),
            "lesson_enforcer_json": str(REPO_LESSON_ENFORCER_JSON),
            "repair_state_json": str(REPO_REPAIR_STATE_JSON),
        },
        "key_decisions": {
            "old_short_not_invalidated": True,
            "old_short_not_capital_approved": True,
            "minimum_closed_trades_monitoring": 20,
            "minimum_closed_trades_capital": 50,
            "closed_research_route_cannot_invalidate_old_short": True,
        },
        **SAFETY_FLAGS,
    }

    next_queue = {
        "queue_name": "edge_factory_os_family_registry_and_lesson_enforcer_repair_next_queue_v1",
        "created_at_utc": utc_now_iso(),
        "queue_status": "FAMILY_REGISTRY_LESSON_ENFORCER_NEXT_QUEUE_READY" if repair_pass else "FAMILY_REGISTRY_LESSON_ENFORCER_QUEUE_BLOCKED",
        "top_next_research_key": next_key,
        "top_next_module": next_module,
        "next_steps": [
            {
                "research_key": NEXT_RESEARCH_KEY,
                "module": NEXT_MODULE,
                "allowed_scope": "READ_ONLY_RUNTIME_MONITORING",
                "purpose": "Refresh runtime family monitor with old_short-aware separation; no capital/runtime/live action.",
                "old_short_research_invalidation_applies": False,
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

    write_json(REPO_FAMILY_REGISTRY_JSON, runtime_family_registry)
    write_json(REPO_LESSON_ENFORCER_JSON, lesson_enforcer)
    write_json(REPO_REPAIR_STATE_JSON, repair_state)
    write_json(REPO_REPAIR_MANIFEST_JSON, manifest)
    write_json(REPO_NEXT_QUEUE_JSON, next_queue)

    result = {
        "module_name": "edge_factory_os_family_registry_and_lesson_enforcer_repair_v1",
        "created_at_utc": utc_now_iso(),
        "repair_status": repair_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "family_registry_status": runtime_family_registry["registry_status"],
        "lesson_enforcer_status": lesson_enforcer["policy_status"],
        "family_count": runtime_family_registry["family_count"],
        "old_short_classification": old_short_row["audit_classification"],
        "old_short_research_invalidation_applies": old_short_row["research_route_failure_applies"],
        "old_short_capital_approved": old_short_row["capital_approved"],
        "old_short_min_closed_trades_monitoring": old_short_row["minimum_closed_trades_for_monitoring_decision"],
        "old_short_min_closed_trades_capital": old_short_row["minimum_closed_trades_for_capital_review"],
        "blocked_route_count": len(blocked_routes),
        "lesson_count": len(lessons),
        "closed_route_hash": closed_route_hash,
        "closed_route_blocked": closed_route_blocked,
        "repair_pass": repair_pass,
        "failed_repair_count": len(failed),
        "failed_repair_keys": failed,
        "checks": checks,
        "runtime_family_registry": runtime_family_registry,
        "lesson_enforcer": lesson_enforcer,
        "repair_state": repair_state,
        "manifest": manifest,
        "next_queue": next_queue,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "family_registry_json": str(REPO_FAMILY_REGISTRY_JSON),
        "lesson_enforcer_json": str(REPO_LESSON_ENFORCER_JSON),
        "repair_state_json": str(REPO_REPAIR_STATE_JSON),
        "repair_manifest_json": str(REPO_REPAIR_MANIFEST_JSON),
        "next_queue_json": str(REPO_NEXT_QUEUE_JSON),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text(result))
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
