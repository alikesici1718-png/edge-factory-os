#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Runtime Family Status Panel + Backup Hygiene v1

Purpose:
- Consolidate current runtime family status after old_short-aware monitor/evaluator.
- Mark old_short as MONITORING_READY_CONTINUE_COLLECT_NO_CAPITAL.
- Keep old_short separate from failed research routes.
- Report untracked backup/hygiene files without deleting or moving them.
- Create a repo status panel and backup hygiene report.
- Do NOT delete files.
- Do NOT move files.
- Do NOT modify .gitignore.
- Do NOT run research.
- Do NOT touch runtime/capital/live.
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

EVALUATOR_JSON = BASE_DIR / "edge_factory_os_runtime_family_monitor_evaluator_no_capital" / "runtime_family_monitor_evaluator_no_capital_latest.json"
EVALUATOR_STATE_JSON = POLICY_DIR / "runtime_family_monitor_evaluator_no_capital_state_v1.json"
EVALUATOR_STATUS_PANEL_JSON = STATUS_DIR / "runtime_family_monitor_status_panel_no_capital_v1.json"

REFRESH_JSON = BASE_DIR / "edge_factory_os_runtime_family_monitor_refresh_old_short_aware" / "runtime_family_monitor_refresh_old_short_aware_latest.json"
FAMILY_REGISTRY_JSON = REGISTRY_DIR / "runtime_family_registry_v1.json"
LESSON_ENFORCER_JSON = POLICY_DIR / "lesson_memory_route_enforcer_v1.json"

PATCH_AUDIT_JSON = STATUS_DIR / "patch_integrity_audit_v1.json"
EXPLICIT_FLAG_POLICY_JSON = POLICY_DIR / "explicit_safety_flag_enforcement_policy_v1.json"
GOV_REPAIR_STATE_JSON = POLICY_DIR / "governance_repair_suite_ledger_alpha_prereg_state_v1.json"
HOLDOUT_REPAIR_STATE_JSON = POLICY_DIR / "holdout_trigger_and_vault_status_repair_state_v1.json"
ALPHA_ENFORCEMENT_JSON = POLICY_DIR / "global_alpha_accounting_enforcement_v1.json"
HOLDOUT_TRIGGER_JSON = POLICY_DIR / "holdout_trigger_protocol_enforced_v1.json"
VAULT_STATUS_JSON = POLICY_DIR / "promising_signal_vault_validation_status_v1.json"

OUT_DIR = BASE_DIR / "edge_factory_os_runtime_family_status_panel_and_backup_hygiene"
OUT_JSON = OUT_DIR / "runtime_family_status_panel_and_backup_hygiene_latest.json"
OUT_TXT = OUT_DIR / "runtime_family_status_panel_and_backup_hygiene_latest.txt"
OUT_BACKUP_CSV = OUT_DIR / "backup_hygiene_report_latest.csv"

REPO_STATUS_PANEL_JSON = STATUS_DIR / "runtime_family_status_panel_and_backup_hygiene_v1.json"
REPO_BACKUP_HYGIENE_JSON = STATUS_DIR / "backup_hygiene_report_v1.json"
REPO_BACKUP_HYGIENE_POLICY_JSON = POLICY_DIR / "backup_hygiene_policy_v1.json"
REPO_STATE_JSON = POLICY_DIR / "runtime_family_status_panel_and_backup_hygiene_state_v1.json"
REPO_NEXT_QUEUE_JSON = QUEUE_DIR / "runtime_family_status_panel_and_backup_hygiene_next_queue_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD8_10_BACKUP_HYGIENE_APPROVAL_OR_STANDARD_STACK_REFRESH"
NEXT_MODULE = "edge_factory_os_backup_hygiene_approval_or_standard_stack_refresh_v1.py"

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


def git_status_short() -> List[str]:
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


def classify_untracked_line(line: str) -> Dict[str, Any]:
    clean = line.strip()
    path_text = clean[3:].strip() if len(clean) > 3 else clean
    lower = path_text.lower()

    if "joint_null_distribution_validator" in lower and "readonly_fix_bak" in lower:
        classification = "KNOWN_TECHNICAL_FIX_BACKUP"
        risk = "LOW"
        recommendation = "Keep until backup hygiene approval; safe to ignore/delete only after explicit user approval."
    elif "source_panel_anomaly_discovery_runner" in lower and "blocked_patch_bak" in lower:
        classification = "KNOWN_POLICY_SENSITIVE_PATCH_BACKUP"
        risk = "ATTENTION"
        recommendation = "Keep until policy-sensitive patch audit remains committed; do not delete automatically."
    elif "universe_coverage_guard_v1.py" in lower:
        classification = "UNTRACKED_LEGACY_OR_SUPERSEDED_TOOL_REVIEW_REQUIRED"
        risk = "ATTENTION"
        recommendation = "Do not delete automatically; classify as legacy/superseded/uncommitted guard before action."
    elif lower.endswith(".bak") or "_bak" in lower or "backup" in lower:
        classification = "UNTRACKED_BACKUP_REVIEW_REQUIRED"
        risk = "ATTENTION"
        recommendation = "Do not delete automatically."
    else:
        classification = "UNTRACKED_REVIEW_REQUIRED"
        risk = "ATTENTION"
        recommendation = "Review before staging/deleting."

    return {
        "git_status_line": clean,
        "path": path_text,
        "classification": classification,
        "risk": risk,
        "recommendation": recommendation,
        "delete_allowed_now": False,
        "move_allowed_now": False,
        "archive_allowed_now": False,
    }


def extract_family_decisions(evaluator: Dict[str, Any], status_panel: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = evaluator.get("family_decision_rows")
    if isinstance(rows, list):
        return [x for x in rows if isinstance(x, dict)]
    rows = status_panel.get("family_decision_rows")
    if isinstance(rows, list):
        return [x for x in rows if isinstance(x, dict)]
    return []


def find_family(rows: List[Dict[str, Any]], family_key: str) -> Dict[str, Any]:
    for row in rows:
        if row.get("family_key") == family_key:
            return row
    return {}


def build_text(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS RUNTIME FAMILY STATUS PANEL + BACKUP HYGIENE v1")
    lines.append("=" * 100)

    for key in [
        "panel_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "old_short_final_decision",
        "old_short_closed_trades",
        "old_short_next_required_closed_trades_for_capital_review",
        "old_short_research_invalidation_applies",
        "old_short_capital_action_allowed",
        "family_count",
        "git_untracked_or_dirty_count",
        "known_backup_count",
        "backup_delete_allowed_now",
        "backup_move_allowed_now",
        "capital_change_allowed",
        "active_paper_allowed",
        "live_allowed",
        "real_orders_allowed",
        "next_recommended_research_key",
        "next_module",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("RUNTIME FAMILY DECISIONS")
    lines.append("-" * 100)
    for row in result.get("family_decision_rows", []):
        lines.append(json.dumps(row, ensure_ascii=False))

    lines.append("")
    lines.append("BACKUP HYGIENE ROWS")
    lines.append("-" * 100)
    for row in result.get("backup_hygiene_rows", []):
        lines.append(json.dumps(row, ensure_ascii=False))

    lines.append("")
    lines.append("CORE DECISION")
    lines.append("-" * 100)
    lines.append("old_short is monitoring-ready and must continue collecting sample.")
    lines.append("old_short needs 30 more closed trades before capital-review threshold.")
    lines.append("No capital, runtime, active paper, live, or real-order action is allowed.")
    lines.append("Backup files are classified, not deleted or moved.")

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        lines.append(f"{key}: {value}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS RUNTIME FAMILY STATUS PANEL + BACKUP HYGIENE v1")
    print("=" * 100)
    print(f"panel_status: {result.get('panel_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"old_short_final_decision: {result.get('old_short_final_decision')}")
    print(f"old_short_closed_trades: {result.get('old_short_closed_trades')}")
    print(f"old_short_next_required_closed_trades_for_capital_review: {result.get('old_short_next_required_closed_trades_for_capital_review')}")
    print(f"old_short_research_invalidation_applies: {result.get('old_short_research_invalidation_applies')}")
    print(f"old_short_capital_action_allowed: {result.get('old_short_capital_action_allowed')}")
    print(f"family_count: {result.get('family_count')}")
    print(f"git_untracked_or_dirty_count: {result.get('git_untracked_or_dirty_count')}")
    print(f"known_backup_count: {result.get('known_backup_count')}")
    print(f"backup_delete_allowed_now: {result.get('backup_delete_allowed_now')}")
    print(f"backup_move_allowed_now: {result.get('backup_move_allowed_now')}")
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
    print(f"BACKUP_CSV: {result.get('backup_csv')}")
    print(f"STATUS_PANEL: {result.get('repo_status_panel_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    evaluator = load_json(EVALUATOR_JSON, {})
    evaluator_state = load_json(EVALUATOR_STATE_JSON, {})
    evaluator_status_panel = load_json(EVALUATOR_STATUS_PANEL_JSON, {})
    refresh = load_json(REFRESH_JSON, {})
    family_registry = load_json(FAMILY_REGISTRY_JSON, {})
    lesson_enforcer = load_json(LESSON_ENFORCER_JSON, {})
    patch_audit = load_json(PATCH_AUDIT_JSON, {})
    explicit_flags = load_json(EXPLICIT_FLAG_POLICY_JSON, {})
    gov_repair = load_json(GOV_REPAIR_STATE_JSON, {})
    holdout_repair = load_json(HOLDOUT_REPAIR_STATE_JSON, {})
    alpha = load_json(ALPHA_ENFORCEMENT_JSON, {})
    holdout = load_json(HOLDOUT_TRIGGER_JSON, {})
    vault = load_json(VAULT_STATUS_JSON, {})

    family_rows = extract_family_decisions(evaluator, evaluator_status_panel)
    old_short = find_family(family_rows, "old_short")

    git_lines = git_status_short()
    hygiene_rows = [classify_untracked_line(line) for line in git_lines]
    known_backup_count = sum(
        1 for row in hygiene_rows
        if row["classification"] in {
            "KNOWN_TECHNICAL_FIX_BACKUP",
            "KNOWN_POLICY_SENSITIVE_PATCH_BACKUP",
            "UNTRACKED_BACKUP_REVIEW_REQUIRED",
        }
    )

    old_short_closed = int(old_short.get("closed_trades") or evaluator.get("old_short_closed_trades") or 0)
    old_short_next_required = int(
        evaluator.get("old_short_next_required_closed_trades_for_capital_review")
        or evaluator_state.get("old_short_next_required_closed_trades_for_capital_review")
        or max(0, 50 - old_short_closed)
    )

    prerequisites = {
        "EVALUATOR_READY": evaluator.get("evaluator_status") == "RUNTIME_FAMILY_MONITOR_EVALUATOR_OLD_SHORT_MONITORING_READY_NO_CAPITAL",
        "EVALUATOR_STATE_READY": evaluator_state.get("evaluator_status") == "RUNTIME_FAMILY_MONITOR_EVALUATOR_OLD_SHORT_MONITORING_READY_NO_CAPITAL",
        "REFRESH_READY": refresh.get("refresh_status") == "RUNTIME_FAMILY_MONITOR_REFRESH_OLD_SHORT_AWARE_READY",
        "FAMILY_REGISTRY_ACTIVE": family_registry.get("registry_status") == "RUNTIME_FAMILY_REGISTRY_ACTIVE_OLD_SHORT_AWARE",
        "LESSON_ENFORCER_ACTIVE": lesson_enforcer.get("policy_status") == "LESSON_MEMORY_ROUTE_ENFORCER_ACTIVE",
        "PATCH_AUDIT_OK": patch_audit.get("audit_status") in {
            "PATCH_INTEGRITY_AUDIT_PASS_WITH_SCHEMA_REPAIR_REQUIRED",
            "PATCH_INTEGRITY_AUDIT_PASS_WITH_EXPLICIT_FLAG_POLICY_ACTIVE",
        },
        "EXPLICIT_FLAG_POLICY_ACTIVE": explicit_flags.get("policy_status") == "EXPLICIT_SAFETY_FLAG_POLICY_ACTIVE",
        "GOV_REPAIR_PASS": gov_repair.get("repair_pass") is True,
        "HOLDOUT_REPAIR_PASS": holdout_repair.get("repair_pass") is True,
        "ALPHA_RESEARCH_PASS_FALSE": alpha.get("research_execution_alpha_pass") is False,
        "HOLDOUT_ACCESS_BLOCKED": holdout.get("holdout_access_allowed_now") is False,
        "VAULT_RELEASE_ZERO": vault.get("vault_release_allowed_count") == 0,
        "OLD_SHORT_MONITORING_READY": old_short.get("final_decision") == "OLD_SHORT_MONITORING_READY_CONTINUE_COLLECT_NO_CAPITAL",
        "OLD_SHORT_CAPITAL_FALSE": old_short.get("capital_action_allowed") is False,
        "OLD_SHORT_RESEARCH_INVALIDATION_FALSE": old_short.get("research_invalidation_applies") is False,
    }

    failed = [k for k, v in prerequisites.items() if v is not True]
    pass_panel = len(failed) == 0

    if pass_panel:
        panel_status = "RUNTIME_FAMILY_STATUS_PANEL_AND_BACKUP_HYGIENE_READY"
        severity = "ATTENTION"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        next_action = "BUILD_BACKUP_HYGIENE_APPROVAL_OR_STANDARD_STACK_REFRESH_NO_ACTION"
        reason = "Runtime family status panel consolidated; backup files classified but not deleted or moved."
        next_key = NEXT_RESEARCH_KEY
        next_module = NEXT_MODULE
        return_code = 0
    else:
        panel_status = "RUNTIME_FAMILY_STATUS_PANEL_AND_BACKUP_HYGIENE_ATTENTION_REVIEW_REQUIRED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_RUNTIME_FAMILY_STATUS_PANEL_FAILURES"
        reason = f"failed_prerequisites={failed}"
        next_key = None
        next_module = None
        return_code = 2

    backup_policy = {
        "policy_name": "edge_factory_os_backup_hygiene_policy_v1",
        "created_at_utc": utc_now_iso(),
        "policy_status": "BACKUP_HYGIENE_POLICY_ACTIVE_NO_DELETE_WITHOUT_APPROVAL",
        "backup_delete_allowed_now": False,
        "backup_move_allowed_now": False,
        "archive_allowed_now": False,
        "gitignore_modification_allowed_now": False,
        "known_backup_count": known_backup_count,
        "rules": [
            "Do not delete backup files automatically.",
            "Do not move backup files automatically.",
            "Do not modify .gitignore automatically.",
            "Known technical fix backup may be ignored/deleted only after explicit approval.",
            "Policy-sensitive patch backup must remain until audit trail is accepted.",
            "Untracked legacy guard must be classified before any action.",
        ],
        **SAFETY_FLAGS,
    }

    backup_report = {
        "report_name": "edge_factory_os_backup_hygiene_report_v1",
        "created_at_utc": utc_now_iso(),
        "report_status": "BACKUP_HYGIENE_REPORT_READY_NO_DELETE",
        "git_untracked_or_dirty_count": len(git_lines),
        "known_backup_count": known_backup_count,
        "backup_delete_allowed_now": False,
        "backup_move_allowed_now": False,
        "archive_allowed_now": False,
        "hygiene_rows": hygiene_rows,
        **SAFETY_FLAGS,
    }

    status_panel = {
        "panel_name": "edge_factory_os_runtime_family_status_panel_and_backup_hygiene_v1",
        "created_at_utc": utc_now_iso(),
        "panel_status": panel_status,
        "strict_policy_key": STRICT_POLICY_KEY,
        "old_short": {
            "final_decision": old_short.get("final_decision"),
            "closed_trades": old_short_closed,
            "monitoring_ready": old_short.get("monitoring_threshold_met"),
            "capital_review_ready": old_short.get("capital_review_threshold_met"),
            "research_invalidation_applies": old_short.get("research_invalidation_applies"),
            "capital_action_allowed": False,
            "next_required_closed_trades_for_capital_review": old_short_next_required,
            "interpretation": "old_short is monitoring-ready and should continue collecting sample; no capital/runtime/live action.",
        },
        "family_decision_rows": family_rows,
        "backup_hygiene": {
            "git_untracked_or_dirty_count": len(git_lines),
            "known_backup_count": known_backup_count,
            "backup_delete_allowed_now": False,
            "backup_move_allowed_now": False,
            "archive_allowed_now": False,
        },
        "global_blocks": {
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
        },
        "release_gate_feed": {
            "RUNTIME_FAMILY_STATUS_PANEL_READY": pass_panel,
            "OLD_SHORT_MONITORING_READY": old_short.get("final_decision") == "OLD_SHORT_MONITORING_READY_CONTINUE_COLLECT_NO_CAPITAL",
            "OLD_SHORT_CAPITAL_REVIEW_READY": old_short.get("capital_review_threshold_met") is True,
            "OLD_SHORT_CAPITAL_ACTION_ALLOWED": False,
            "BACKUP_HYGIENE_REPORTED": True,
            "BACKUP_DELETE_ALLOWED": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_STATUS_PANEL": False,
            "FAMILY_RELEASE_ALLOWED_FROM_STATUS_PANEL": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_STATUS_PANEL": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_STATUS_PANEL": False,
            "ACTIVE_PAPER_ALLOWED_FROM_STATUS_PANEL": False,
            "LIVE_ALLOWED_FROM_STATUS_PANEL": False,
            "REAL_ORDERS_ALLOWED_FROM_STATUS_PANEL": False,
        },
        **SAFETY_FLAGS,
    }

    state = {
        "state_name": "edge_factory_os_runtime_family_status_panel_and_backup_hygiene_state_v1",
        "created_at_utc": utc_now_iso(),
        "panel_status": panel_status,
        "old_short_final_decision": old_short.get("final_decision"),
        "old_short_closed_trades": old_short_closed,
        "old_short_next_required_closed_trades_for_capital_review": old_short_next_required,
        "old_short_research_invalidation_applies": old_short.get("research_invalidation_applies"),
        "old_short_capital_action_allowed": False,
        "family_count": len(family_rows),
        "git_untracked_or_dirty_count": len(git_lines),
        "known_backup_count": known_backup_count,
        "backup_delete_allowed_now": False,
        "backup_move_allowed_now": False,
        "failed_prerequisite_count": len(failed),
        "failed_prerequisites": failed,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        **SAFETY_FLAGS,
    }

    next_queue = {
        "queue_name": "edge_factory_os_runtime_family_status_panel_and_backup_hygiene_next_queue_v1",
        "created_at_utc": utc_now_iso(),
        "queue_status": "RUNTIME_FAMILY_STATUS_PANEL_BACKUP_HYGIENE_NEXT_QUEUE_READY" if pass_panel else "RUNTIME_FAMILY_STATUS_PANEL_BACKUP_HYGIENE_QUEUE_BLOCKED",
        "top_next_research_key": next_key,
        "top_next_module": next_module,
        "next_steps": [
            {
                "research_key": NEXT_RESEARCH_KEY,
                "module": NEXT_MODULE,
                "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
                "purpose": "Decide backup hygiene approval or refresh standard stack status without deleting files automatically.",
                "backup_delete_allowed_now": False,
                "old_short_final_decision": old_short.get("final_decision"),
                "candidate_generation_allowed": False,
                "family_release_allowed": False,
                "runtime_touch_allowed": False,
                "capital_change_allowed": False,
                "active_paper_allowed": False,
                "live_allowed": False,
                "real_orders_allowed": False,
            }
        ] if pass_panel else [],
        **SAFETY_FLAGS,
    }

    write_json(REPO_STATUS_PANEL_JSON, status_panel)
    write_json(REPO_BACKUP_HYGIENE_JSON, backup_report)
    write_json(REPO_BACKUP_HYGIENE_POLICY_JSON, backup_policy)
    write_json(REPO_STATE_JSON, state)
    write_json(REPO_NEXT_QUEUE_JSON, next_queue)
    write_csv(OUT_BACKUP_CSV, hygiene_rows)

    result = {
        "module_name": "edge_factory_os_runtime_family_status_panel_and_backup_hygiene_v1",
        "created_at_utc": utc_now_iso(),
        "panel_status": panel_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "old_short_final_decision": old_short.get("final_decision"),
        "old_short_closed_trades": old_short_closed,
        "old_short_next_required_closed_trades_for_capital_review": old_short_next_required,
        "old_short_research_invalidation_applies": old_short.get("research_invalidation_applies"),
        "old_short_capital_action_allowed": False,
        "family_count": len(family_rows),
        "git_untracked_or_dirty_count": len(git_lines),
        "known_backup_count": known_backup_count,
        "backup_delete_allowed_now": False,
        "backup_move_allowed_now": False,
        "backup_hygiene_rows": hygiene_rows,
        "family_decision_rows": family_rows,
        "status_panel": status_panel,
        "backup_report": backup_report,
        "backup_policy": backup_policy,
        "state": state,
        "next_queue": next_queue,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "backup_csv": str(OUT_BACKUP_CSV),
        "repo_status_panel_json": str(REPO_STATUS_PANEL_JSON),
        "repo_backup_hygiene_json": str(REPO_BACKUP_HYGIENE_JSON),
        "repo_backup_hygiene_policy_json": str(REPO_BACKUP_HYGIENE_POLICY_JSON),
        "repo_state_json": str(REPO_STATE_JSON),
        "repo_next_queue_json": str(REPO_NEXT_QUEUE_JSON),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text(result))
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
