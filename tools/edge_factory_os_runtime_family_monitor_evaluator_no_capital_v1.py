#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Runtime Family Monitor Evaluator No Capital v1

Purpose:
- Evaluate Runtime Family Monitor Refresh Old-Short Aware v1.
- Confirm old_short is not invalidated by failed research routes.
- Confirm old_short has reached monitoring threshold at >=20 closed trades.
- Confirm old_short has NOT reached capital-review threshold at >=50 closed trades.
- Explicitly block capital/release/runtime/active-paper/live/real-order action.
- Queue continued monitoring / status panel, not capital action.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = BASE_DIR / "edge_factory_os_repo"

FRAMEWORK_DIR = REPO_DIR / "edge_factory_os_framework"
POLICY_DIR = FRAMEWORK_DIR / "policies"
QUEUE_DIR = FRAMEWORK_DIR / "queues"
STATUS_DIR = FRAMEWORK_DIR / "status"
REGISTRY_DIR = FRAMEWORK_DIR / "registries"

REFRESH_JSON = BASE_DIR / "edge_factory_os_runtime_family_monitor_refresh_old_short_aware" / "runtime_family_monitor_refresh_old_short_aware_latest.json"
REFRESH_STATE_JSON = POLICY_DIR / "runtime_family_monitor_refresh_old_short_aware_state_v1.json"
REFRESH_SUMMARY_JSON = STATUS_DIR / "runtime_family_monitor_refresh_old_short_aware_summary_v1.json"

FAMILY_REGISTRY_JSON = REGISTRY_DIR / "runtime_family_registry_v1.json"
LESSON_ENFORCER_JSON = POLICY_DIR / "lesson_memory_route_enforcer_v1.json"
FAMILY_REPAIR_STATE_JSON = POLICY_DIR / "family_registry_and_lesson_enforcer_repair_state_v1.json"
ALPHA_ENFORCEMENT_JSON = POLICY_DIR / "global_alpha_accounting_enforcement_v1.json"
HOLDOUT_TRIGGER_JSON = POLICY_DIR / "holdout_trigger_protocol_enforced_v1.json"
VAULT_STATUS_JSON = POLICY_DIR / "promising_signal_vault_validation_status_v1.json"
PREREG_ENFORCEMENT_JSON = POLICY_DIR / "pre_registration_enforcement_policy_v1.json"
LEDGER_ENFORCED_JSON = POLICY_DIR / "global_multiple_testing_ledger_enforced_v1.json"

OUT_DIR = BASE_DIR / "edge_factory_os_runtime_family_monitor_evaluator_no_capital"
OUT_JSON = OUT_DIR / "runtime_family_monitor_evaluator_no_capital_latest.json"
OUT_TXT = OUT_DIR / "runtime_family_monitor_evaluator_no_capital_latest.txt"
OUT_CSV = OUT_DIR / "runtime_family_monitor_evaluator_no_capital_family_decisions_latest.csv"

REPO_EVALUATOR_STATE_JSON = POLICY_DIR / "runtime_family_monitor_evaluator_no_capital_state_v1.json"
REPO_STATUS_PANEL_JSON = STATUS_DIR / "runtime_family_monitor_status_panel_no_capital_v1.json"
REPO_NEXT_QUEUE_JSON = QUEUE_DIR / "runtime_family_monitor_evaluator_no_capital_next_queue_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD8_09_RUNTIME_FAMILY_STATUS_PANEL_AND_BACKUP_HYGIENE"
NEXT_MODULE = "edge_factory_os_runtime_family_status_panel_and_backup_hygiene_v1.py"

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


def get_git_status_short() -> List[str]:
    try:
        proc = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(REPO_DIR),
            text=True,
            capture_output=True,
            timeout=30,
        )
        return [x for x in proc.stdout.splitlines() if x.strip()]
    except Exception as exc:
        return [f"GIT_STATUS_ERROR: {type(exc).__name__}: {exc}"]


def find_family_row(rows: List[Dict[str, Any]], family_key: str) -> Dict[str, Any]:
    for row in rows:
        if isinstance(row, dict) and row.get("family_key") == family_key:
            return row
    return {}


def family_decision_from_refresh(row: Dict[str, Any]) -> Dict[str, Any]:
    family_key = row.get("family_key")
    closed = int(row.get("closed_trades") or 0)
    monitoring_met = row.get("monitoring_threshold_met") is True
    capital_met = row.get("capital_review_threshold_met") is True
    research_invalidation = row.get("research_invalidation_applies") is True
    capital_action = row.get("capital_action_allowed") is True

    if family_key == "old_short":
        if research_invalidation:
            final_decision = "OLD_SHORT_REVIEW_REQUIRED_REGISTRY_CONFLICT"
            decision_reason = "old_short unexpectedly marked as affected by research invalidation"
            severity = "ATTENTION"
        elif capital_action:
            final_decision = "OLD_SHORT_REVIEW_REQUIRED_CAPITAL_ACTION_CONFLICT"
            decision_reason = "refresh unexpectedly allowed capital action"
            severity = "ATTENTION"
        elif capital_met:
            final_decision = "OLD_SHORT_CAPITAL_REVIEW_THRESHOLD_MET_BUT_NO_CAPITAL_ACTION"
            decision_reason = "old_short has >=50 closed trades, but separate drift/capital-governor is still required"
            severity = "ATTENTION"
        elif monitoring_met:
            final_decision = "OLD_SHORT_MONITORING_READY_CONTINUE_COLLECT_NO_CAPITAL"
            decision_reason = "old_short has >=20 closed trades and is not invalidated, but below 50-trade capital-review threshold"
            severity = "OK"
        elif closed > 0:
            final_decision = "OLD_SHORT_NOT_INVALIDATED_COLLECT_MORE_SAMPLE_NO_CAPITAL"
            decision_reason = "old_short has sample but below monitoring threshold"
            severity = "ATTENTION"
        else:
            final_decision = "OLD_SHORT_NOT_INVALIDATED_NO_CURRENT_SAMPLE_NO_CAPITAL"
            decision_reason = "old_short is protected but current evidence is insufficient"
            severity = "ATTENTION"
    elif family_key == "impulse_long":
        final_decision = "IMPULSE_LONG_MONITORING_ATTENTION_NO_CAPITAL"
        decision_reason = "impulse_long remains separate and not approved"
        severity = "ATTENTION"
    elif family_key == "market_relative_short":
        final_decision = "MARKET_RELATIVE_SHORT_SAMPLE_EXPOSURE_ATTENTION_NO_CAPITAL"
        decision_reason = "market_relative_short needs sample/exposure review"
        severity = "ATTENTION"
    elif family_key == "weak_market_short":
        final_decision = "WEAK_MARKET_SHORT_INCONCLUSIVE_NO_CAPITAL"
        decision_reason = "weak_market_short is inconclusive"
        severity = "ATTENTION"
    else:
        final_decision = "UNKNOWN_FAMILY_REVIEW_REQUIRED"
        decision_reason = "unknown family"
        severity = "ATTENTION"

    return {
        "family_key": family_key,
        "final_decision": final_decision,
        "decision_reason": decision_reason,
        "decision_severity": severity,
        "closed_trades": closed,
        "monitoring_threshold": row.get("monitoring_threshold"),
        "capital_review_threshold": row.get("capital_review_threshold"),
        "monitoring_threshold_met": monitoring_met,
        "capital_review_threshold_met": capital_met,
        "research_invalidation_applies": research_invalidation,
        "capital_action_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        "best_source_file": row.get("best_source_file"),
        "best_source_mtime_utc": row.get("best_source_mtime_utc"),
        "best_evidence_quality_score": row.get("best_evidence_quality_score"),
        "best_status": row.get("best_status"),
    }


def build_text(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS RUNTIME FAMILY MONITOR EVALUATOR NO CAPITAL v1")
    lines.append("=" * 100)

    for key in [
        "evaluator_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "old_short_final_decision",
        "old_short_closed_trades",
        "old_short_monitoring_threshold_met",
        "old_short_capital_review_threshold_met",
        "old_short_research_invalidation_applies",
        "old_short_capital_action_allowed",
        "old_short_next_required_closed_trades_for_capital_review",
        "family_count",
        "capital_change_allowed",
        "active_paper_allowed",
        "live_allowed",
        "real_orders_allowed",
        "next_recommended_research_key",
        "next_module",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("FAMILY DECISIONS")
    lines.append("-" * 100)
    for row in result.get("family_decision_rows", []):
        lines.append(json.dumps(row, ensure_ascii=False))

    lines.append("")
    lines.append("CORE DECISION")
    lines.append("-" * 100)
    lines.append("old_short is monitoring-ready, not capital-ready.")
    lines.append("20 closed trades is enough for monitoring classification, not enough for capital review.")
    lines.append("Capital review requires at least 50 closed trades plus drift review and capital governor.")
    lines.append("This module cannot approve capital, runtime changes, active paper, live, or real orders.")

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        lines.append(f"{key}: {value}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS RUNTIME FAMILY MONITOR EVALUATOR NO CAPITAL v1")
    print("=" * 100)
    print(f"evaluator_status: {result.get('evaluator_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"old_short_final_decision: {result.get('old_short_final_decision')}")
    print(f"old_short_closed_trades: {result.get('old_short_closed_trades')}")
    print(f"old_short_monitoring_threshold_met: {result.get('old_short_monitoring_threshold_met')}")
    print(f"old_short_capital_review_threshold_met: {result.get('old_short_capital_review_threshold_met')}")
    print(f"old_short_research_invalidation_applies: {result.get('old_short_research_invalidation_applies')}")
    print(f"old_short_capital_action_allowed: {result.get('old_short_capital_action_allowed')}")
    print(f"old_short_next_required_closed_trades_for_capital_review: {result.get('old_short_next_required_closed_trades_for_capital_review')}")
    print(f"family_count: {result.get('family_count')}")
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
    print(f"CSV : {result.get('decision_csv')}")
    print(f"STATE: {result.get('evaluator_state_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    refresh = load_json(REFRESH_JSON, {})
    refresh_state = load_json(REFRESH_STATE_JSON, {})
    refresh_summary = load_json(REFRESH_SUMMARY_JSON, {})
    family_registry = load_json(FAMILY_REGISTRY_JSON, {})
    lesson_enforcer = load_json(LESSON_ENFORCER_JSON, {})
    family_repair = load_json(FAMILY_REPAIR_STATE_JSON, {})
    alpha = load_json(ALPHA_ENFORCEMENT_JSON, {})
    holdout = load_json(HOLDOUT_TRIGGER_JSON, {})
    vault = load_json(VAULT_STATUS_JSON, {})
    prereg = load_json(PREREG_ENFORCEMENT_JSON, {})
    ledger = load_json(LEDGER_ENFORCED_JSON, {})

    family_rows = refresh.get("family_summary_rows")
    if not isinstance(family_rows, list):
        family_rows = refresh_summary.get("family_summary_rows")
    if not isinstance(family_rows, list):
        family_rows = []

    decision_rows = [family_decision_from_refresh(row) for row in family_rows if isinstance(row, dict)]
    old_short = find_family_row(decision_rows, "old_short")

    old_short_closed = int(old_short.get("closed_trades") or 0)
    next_required_for_capital = max(0, 50 - old_short_closed)

    prerequisites = {
        "REFRESH_READY": refresh.get("refresh_status") == "RUNTIME_FAMILY_MONITOR_REFRESH_OLD_SHORT_AWARE_READY",
        "REFRESH_STATE_READY": refresh_state.get("refresh_status") == "RUNTIME_FAMILY_MONITOR_REFRESH_OLD_SHORT_AWARE_READY",
        "FAMILY_REGISTRY_ACTIVE": family_registry.get("registry_status") == "RUNTIME_FAMILY_REGISTRY_ACTIVE_OLD_SHORT_AWARE",
        "LESSON_ENFORCER_ACTIVE": lesson_enforcer.get("policy_status") == "LESSON_MEMORY_ROUTE_ENFORCER_ACTIVE",
        "FAMILY_REPAIR_PASS": family_repair.get("repair_pass") is True,
        "ALPHA_RESEARCH_PASS_FALSE": alpha.get("research_execution_alpha_pass") is False,
        "HOLDOUT_ACCESS_BLOCKED": holdout.get("holdout_access_allowed_now") is False,
        "VAULT_RELEASE_ZERO": vault.get("vault_release_allowed_count") == 0,
        "PREREG_ACTIVE": prereg.get("policy_status") == "PRE_REGISTRATION_ENFORCEMENT_ACTIVE",
        "LEDGER_ENFORCED": ledger.get("ledger_status") == "GLOBAL_MULTIPLE_TESTING_LEDGER_ENFORCED_NON_NULL",
        "OLD_SHORT_PRESENT": bool(old_short),
        "OLD_SHORT_NOT_INVALIDATED": old_short.get("research_invalidation_applies") is False,
        "OLD_SHORT_CAPITAL_ACTION_FALSE": old_short.get("capital_action_allowed") is False,
        "OLD_SHORT_MONITORING_MET": old_short.get("monitoring_threshold_met") is True,
        "OLD_SHORT_CAPITAL_REVIEW_NOT_MET": old_short.get("capital_review_threshold_met") is False,
    }

    failed = [k for k, v in prerequisites.items() if v is not True]
    pass_eval = len(failed) == 0

    if pass_eval:
        evaluator_status = "RUNTIME_FAMILY_MONITOR_EVALUATOR_OLD_SHORT_MONITORING_READY_NO_CAPITAL"
        severity = "ATTENTION"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        next_action = "BUILD_RUNTIME_FAMILY_STATUS_PANEL_AND_BACKUP_HYGIENE_NO_ACTION"
        reason = "old_short has monitoring-ready sample but is not capital-review-ready; all capital/runtime/live actions blocked."
        next_key = NEXT_RESEARCH_KEY
        next_module = NEXT_MODULE
        return_code = 0
    else:
        evaluator_status = "RUNTIME_FAMILY_MONITOR_EVALUATOR_ATTENTION_REVIEW_REQUIRED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_RUNTIME_FAMILY_MONITOR_EVALUATOR_FAILURES"
        reason = f"failed_prerequisites={failed}"
        next_key = None
        next_module = None
        return_code = 2

    status_panel = {
        "panel_name": "edge_factory_os_runtime_family_monitor_status_panel_no_capital_v1",
        "created_at_utc": utc_now_iso(),
        "panel_status": evaluator_status,
        "family_decision_rows": decision_rows,
        "old_short": {
            "final_decision": old_short.get("final_decision"),
            "closed_trades": old_short_closed,
            "monitoring_ready": old_short.get("monitoring_threshold_met"),
            "capital_review_ready": old_short.get("capital_review_threshold_met"),
            "next_required_closed_trades_for_capital_review": next_required_for_capital,
            "capital_action_allowed": False,
            "runtime_touch_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
        },
        "global_runtime_decision": {
            "candidate_generation_allowed": False,
            "family_release_allowed": False,
            "runtime_touch_allowed": False,
            "capital_change_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
        },
        "git_status_short": get_git_status_short(),
        **SAFETY_FLAGS,
    }

    evaluator_state = {
        "state_name": "edge_factory_os_runtime_family_monitor_evaluator_no_capital_state_v1",
        "created_at_utc": utc_now_iso(),
        "evaluator_status": evaluator_status,
        "strict_policy_key": STRICT_POLICY_KEY,
        "old_short_final_decision": old_short.get("final_decision"),
        "old_short_closed_trades": old_short_closed,
        "old_short_monitoring_threshold_met": old_short.get("monitoring_threshold_met"),
        "old_short_capital_review_threshold_met": old_short.get("capital_review_threshold_met"),
        "old_short_research_invalidation_applies": old_short.get("research_invalidation_applies"),
        "old_short_capital_action_allowed": False,
        "old_short_next_required_closed_trades_for_capital_review": next_required_for_capital,
        "family_count": len(decision_rows),
        "failed_prerequisite_count": len(failed),
        "failed_prerequisites": failed,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        **SAFETY_FLAGS,
    }

    next_queue = {
        "queue_name": "edge_factory_os_runtime_family_monitor_evaluator_no_capital_next_queue_v1",
        "created_at_utc": utc_now_iso(),
        "queue_status": "RUNTIME_FAMILY_MONITOR_EVALUATOR_NEXT_QUEUE_READY" if pass_eval else "RUNTIME_FAMILY_MONITOR_EVALUATOR_QUEUE_BLOCKED",
        "top_next_research_key": next_key,
        "top_next_module": next_module,
        "next_steps": [
            {
                "research_key": NEXT_RESEARCH_KEY,
                "module": NEXT_MODULE,
                "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
                "purpose": "Build a consolidated runtime-family status panel and handle backup hygiene without deleting files automatically.",
                "old_short_final_decision": old_short.get("final_decision"),
                "old_short_closed_trades": old_short_closed,
                "old_short_next_required_closed_trades_for_capital_review": next_required_for_capital,
                "candidate_generation_allowed": False,
                "family_release_allowed": False,
                "runtime_touch_allowed": False,
                "capital_change_allowed": False,
                "active_paper_allowed": False,
                "live_allowed": False,
                "real_orders_allowed": False,
            }
        ] if pass_eval else [],
        **SAFETY_FLAGS,
    }

    write_json(REPO_STATUS_PANEL_JSON, status_panel)
    write_json(REPO_EVALUATOR_STATE_JSON, evaluator_state)
    write_json(REPO_NEXT_QUEUE_JSON, next_queue)
    write_csv(OUT_CSV, decision_rows)

    result = {
        "module_name": "edge_factory_os_runtime_family_monitor_evaluator_no_capital_v1",
        "created_at_utc": utc_now_iso(),
        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "old_short_final_decision": old_short.get("final_decision"),
        "old_short_closed_trades": old_short_closed,
        "old_short_monitoring_threshold_met": old_short.get("monitoring_threshold_met"),
        "old_short_capital_review_threshold_met": old_short.get("capital_review_threshold_met"),
        "old_short_research_invalidation_applies": old_short.get("research_invalidation_applies"),
        "old_short_capital_action_allowed": False,
        "old_short_next_required_closed_trades_for_capital_review": next_required_for_capital,
        "family_count": len(decision_rows),
        "failed_prerequisite_count": len(failed),
        "failed_prerequisites": failed,
        "family_decision_rows": decision_rows,
        "status_panel": status_panel,
        "evaluator_state": evaluator_state,
        "next_queue": next_queue,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "decision_csv": str(OUT_CSV),
        "status_panel_json": str(REPO_STATUS_PANEL_JSON),
        "evaluator_state_json": str(REPO_EVALUATOR_STATE_JSON),
        "next_queue_json": str(REPO_NEXT_QUEUE_JSON),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text(result))
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
