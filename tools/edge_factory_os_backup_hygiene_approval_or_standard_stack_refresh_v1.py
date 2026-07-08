#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Backup Hygiene Approval or Standard Stack Refresh v1

Purpose:
- Consume Runtime Family Status Panel + Backup Hygiene v1.
- Decide whether backup hygiene action is approved.
- Default: no approval -> no delete, no move, no .gitignore modification.
- Preserve untracked backup files as pending hygiene items.
- Queue a repo-only standard OS status/stack refresh.
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

STATUS_PANEL_JSON = STATUS_DIR / "runtime_family_status_panel_and_backup_hygiene_v1.json"
BACKUP_REPORT_JSON = STATUS_DIR / "backup_hygiene_report_v1.json"
BACKUP_POLICY_JSON = POLICY_DIR / "backup_hygiene_policy_v1.json"
STATUS_PANEL_STATE_JSON = POLICY_DIR / "runtime_family_status_panel_and_backup_hygiene_state_v1.json"

RUNTIME_FAMILY_EVALUATOR_JSON = POLICY_DIR / "runtime_family_monitor_evaluator_no_capital_state_v1.json"
RUNTIME_FAMILY_REGISTRY_JSON = FRAMEWORK_DIR / "registries" / "runtime_family_registry_v1.json"
LESSON_ENFORCER_JSON = POLICY_DIR / "lesson_memory_route_enforcer_v1.json"

PATCH_AUDIT_JSON = STATUS_DIR / "patch_integrity_audit_v1.json"
EXPLICIT_FLAG_POLICY_JSON = POLICY_DIR / "explicit_safety_flag_enforcement_policy_v1.json"
GOV_REPAIR_STATE_JSON = POLICY_DIR / "governance_repair_suite_ledger_alpha_prereg_state_v1.json"
HOLDOUT_REPAIR_STATE_JSON = POLICY_DIR / "holdout_trigger_and_vault_status_repair_state_v1.json"
ALPHA_ENFORCEMENT_JSON = POLICY_DIR / "global_alpha_accounting_enforcement_v1.json"
HOLDOUT_TRIGGER_JSON = POLICY_DIR / "holdout_trigger_protocol_enforced_v1.json"
VAULT_STATUS_JSON = POLICY_DIR / "promising_signal_vault_validation_status_v1.json"

# This file intentionally does not exist unless the user/manual operator creates it.
# Its absence means no cleanup action is approved.
HUMAN_APPROVAL_JSON = POLICY_DIR / "manual_backup_hygiene_approval_v1.json"

OUT_DIR = BASE_DIR / "edge_factory_os_backup_hygiene_approval_or_standard_stack_refresh"
OUT_JSON = OUT_DIR / "backup_hygiene_approval_or_standard_stack_refresh_latest.json"
OUT_TXT = OUT_DIR / "backup_hygiene_approval_or_standard_stack_refresh_latest.txt"
OUT_CSV = OUT_DIR / "backup_hygiene_pending_items_latest.csv"

REPO_DECISION_JSON = STATUS_DIR / "backup_hygiene_approval_or_standard_stack_refresh_decision_v1.json"
REPO_STATE_JSON = POLICY_DIR / "backup_hygiene_approval_or_standard_stack_refresh_state_v1.json"
REPO_PENDING_JSON = STATUS_DIR / "backup_hygiene_pending_items_v1.json"
REPO_NEXT_QUEUE_JSON = QUEUE_DIR / "backup_hygiene_approval_or_standard_stack_refresh_next_queue_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD8_11_REPO_ONLY_STANDARD_OS_STATUS_REFRESH"
NEXT_MODULE = "edge_factory_os_repo_only_standard_os_status_refresh_v1.py"

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


def classify_git_line(line: str) -> Dict[str, Any]:
    clean = line.strip()
    path_text = clean[3:].strip() if len(clean) > 3 else clean
    lower = path_text.lower()

    if "joint_null_distribution_validator" in lower and "readonly_fix_bak" in lower:
        classification = "KNOWN_TECHNICAL_FIX_BACKUP_PENDING_APPROVAL"
        risk = "LOW"
        required_action = "KEEP_PENDING_OR_APPROVE_DELETE_LATER"
    elif "source_panel_anomaly_discovery_runner" in lower and "blocked_patch_bak" in lower:
        classification = "KNOWN_POLICY_SENSITIVE_PATCH_BACKUP_PENDING_APPROVAL"
        risk = "ATTENTION"
        required_action = "KEEP_PENDING_UNTIL_POLICY_AUDIT_ACCEPTED"
    elif "universe_coverage_guard_v1.py" in lower:
        classification = "UNTRACKED_UNIVERSE_COVERAGE_GUARD_REVIEW_REQUIRED"
        risk = "ATTENTION"
        required_action = "CLASSIFY_AS_ACTIVE_CORE_OR_SUPERSEDED_BEFORE_STAGING_OR_DELETING"
    elif "backup_hygiene_approval_or_standard_stack_refresh" in lower:
        classification = "CURRENT_MODULE_UNTRACKED_BEFORE_COMMIT_EXPECTED"
        risk = "LOW"
        required_action = "EXPECTED_TO_BE_COMMITTED_THIS_STEP"
    elif lower.endswith(".bak") or "_bak" in lower or "backup" in lower:
        classification = "UNTRACKED_BACKUP_PENDING_APPROVAL"
        risk = "ATTENTION"
        required_action = "KEEP_PENDING_UNTIL_EXPLICIT_APPROVAL"
    else:
        classification = "UNTRACKED_OR_DIRTY_REVIEW_REQUIRED"
        risk = "ATTENTION"
        required_action = "REVIEW_BEFORE_ACTION"

    return {
        "git_status_line": clean,
        "path": path_text,
        "classification": classification,
        "risk": risk,
        "required_action": required_action,
        "delete_allowed_now": False,
        "move_allowed_now": False,
        "archive_allowed_now": False,
        "gitignore_change_allowed_now": False,
    }


def approval_valid(approval: Dict[str, Any]) -> bool:
    if not isinstance(approval, dict) or not approval:
        return False

    return (
        approval.get("approval_status") == "MANUAL_BACKUP_HYGIENE_APPROVAL_GRANTED"
        and approval.get("delete_allowed") is True
        and approval.get("scope") in {"known_backups_only", "specific_files_only"}
        and isinstance(approval.get("approved_paths"), list)
        and len(approval.get("approved_paths")) > 0
    )


def build_text(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS BACKUP HYGIENE APPROVAL OR STANDARD STACK REFRESH v1")
    lines.append("=" * 100)

    for key in [
        "decision_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "manual_approval_present",
        "manual_approval_valid",
        "backup_delete_allowed_now",
        "backup_move_allowed_now",
        "gitignore_change_allowed_now",
        "pending_hygiene_item_count",
        "known_backup_pending_count",
        "universe_guard_review_required",
        "old_short_final_decision",
        "old_short_closed_trades",
        "old_short_next_required_closed_trades_for_capital_review",
        "standard_status_refresh_recommended",
        "next_recommended_research_key",
        "next_module",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("PENDING HYGIENE ITEMS")
    lines.append("-" * 100)
    for row in result.get("pending_hygiene_rows", []):
        lines.append(json.dumps(row, ensure_ascii=False))

    lines.append("")
    lines.append("CORE DECISION")
    lines.append("-" * 100)
    lines.append("No valid manual backup hygiene approval exists, so no cleanup action is allowed.")
    lines.append("Backup files and untracked guard remain pending hygiene items.")
    lines.append("Next safe step is repo-only standard OS status refresh.")
    lines.append("No runtime, capital, active paper, live, real order, candidate, or release action is allowed.")

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        lines.append(f"{key}: {value}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS BACKUP HYGIENE APPROVAL OR STANDARD STACK REFRESH v1")
    print("=" * 100)
    print(f"decision_status: {result.get('decision_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"manual_approval_present: {result.get('manual_approval_present')}")
    print(f"manual_approval_valid: {result.get('manual_approval_valid')}")
    print(f"backup_delete_allowed_now: {result.get('backup_delete_allowed_now')}")
    print(f"backup_move_allowed_now: {result.get('backup_move_allowed_now')}")
    print(f"gitignore_change_allowed_now: {result.get('gitignore_change_allowed_now')}")
    print(f"pending_hygiene_item_count: {result.get('pending_hygiene_item_count')}")
    print(f"known_backup_pending_count: {result.get('known_backup_pending_count')}")
    print(f"universe_guard_review_required: {result.get('universe_guard_review_required')}")
    print(f"old_short_final_decision: {result.get('old_short_final_decision')}")
    print(f"old_short_closed_trades: {result.get('old_short_closed_trades')}")
    print(f"old_short_next_required_closed_trades_for_capital_review: {result.get('old_short_next_required_closed_trades_for_capital_review')}")
    print(f"standard_status_refresh_recommended: {result.get('standard_status_refresh_recommended')}")
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
    print(f"CSV : {result.get('pending_csv')}")
    print(f"DECISION: {result.get('repo_decision_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    status_panel = load_json(STATUS_PANEL_JSON, {})
    backup_report = load_json(BACKUP_REPORT_JSON, {})
    backup_policy = load_json(BACKUP_POLICY_JSON, {})
    status_panel_state = load_json(STATUS_PANEL_STATE_JSON, {})
    runtime_eval = load_json(RUNTIME_FAMILY_EVALUATOR_JSON, {})
    family_registry = load_json(RUNTIME_FAMILY_REGISTRY_JSON, {})
    lesson_enforcer = load_json(LESSON_ENFORCER_JSON, {})
    patch_audit = load_json(PATCH_AUDIT_JSON, {})
    explicit_flags = load_json(EXPLICIT_FLAG_POLICY_JSON, {})
    gov_repair = load_json(GOV_REPAIR_STATE_JSON, {})
    holdout_repair = load_json(HOLDOUT_REPAIR_STATE_JSON, {})
    alpha = load_json(ALPHA_ENFORCEMENT_JSON, {})
    holdout = load_json(HOLDOUT_TRIGGER_JSON, {})
    vault = load_json(VAULT_STATUS_JSON, {})
    approval = load_json(HUMAN_APPROVAL_JSON, {})

    git_lines = git_status_short()
    pending_rows = [classify_git_line(line) for line in git_lines]
    manual_approval_present = HUMAN_APPROVAL_JSON.exists()
    manual_approval_is_valid = approval_valid(approval)

    known_backup_pending_count = sum(
        1 for row in pending_rows
        if "BACKUP" in str(row.get("classification", ""))
    )
    universe_guard_review_required = any(
        row.get("classification") == "UNTRACKED_UNIVERSE_COVERAGE_GUARD_REVIEW_REQUIRED"
        for row in pending_rows
    )

    # Even if approval exists, this v1 module intentionally does not delete/move.
    # It only records whether cleanup could be requested in a later separate tool.
    backup_delete_allowed_now = False
    backup_move_allowed_now = False
    gitignore_change_allowed_now = False

    old_short = status_panel.get("old_short", {})
    old_short_final_decision = old_short.get("final_decision") or status_panel_state.get("old_short_final_decision")
    old_short_closed_trades = old_short.get("closed_trades") or status_panel_state.get("old_short_closed_trades")
    old_short_next_required = (
        old_short.get("next_required_closed_trades_for_capital_review")
        or status_panel_state.get("old_short_next_required_closed_trades_for_capital_review")
    )

    prerequisites = {
        "STATUS_PANEL_READY": status_panel.get("panel_status") == "RUNTIME_FAMILY_STATUS_PANEL_AND_BACKUP_HYGIENE_READY",
        "STATUS_PANEL_STATE_READY": status_panel_state.get("panel_status") == "RUNTIME_FAMILY_STATUS_PANEL_AND_BACKUP_HYGIENE_READY",
        "BACKUP_POLICY_ACTIVE": backup_policy.get("policy_status") == "BACKUP_HYGIENE_POLICY_ACTIVE_NO_DELETE_WITHOUT_APPROVAL",
        "BACKUP_REPORT_READY": backup_report.get("report_status") == "BACKUP_HYGIENE_REPORT_READY_NO_DELETE",
        "RUNTIME_EVALUATOR_READY": runtime_eval.get("evaluator_status") == "RUNTIME_FAMILY_MONITOR_EVALUATOR_OLD_SHORT_MONITORING_READY_NO_CAPITAL",
        "FAMILY_REGISTRY_ACTIVE": family_registry.get("registry_status") == "RUNTIME_FAMILY_REGISTRY_ACTIVE_OLD_SHORT_AWARE",
        "LESSON_ENFORCER_ACTIVE": lesson_enforcer.get("policy_status") == "LESSON_MEMORY_ROUTE_ENFORCER_ACTIVE",
        "PATCH_AUDIT_OK": patch_audit.get("audit_status") in {
            "PATCH_INTEGRITY_AUDIT_PASS_WITH_SCHEMA_REPAIR_REQUIRED",
            "PATCH_INTEGRITY_AUDIT_PASS_WITH_EXPLICIT_FLAG_POLICY_ACTIVE",
        },
        "EXPLICIT_FLAGS_ACTIVE": explicit_flags.get("policy_status") == "EXPLICIT_SAFETY_FLAG_POLICY_ACTIVE",
        "GOV_REPAIR_PASS": gov_repair.get("repair_pass") is True,
        "HOLDOUT_REPAIR_PASS": holdout_repair.get("repair_pass") is True,
        "ALPHA_RESEARCH_PASS_FALSE": alpha.get("research_execution_alpha_pass") is False,
        "HOLDOUT_ACCESS_BLOCKED": holdout.get("holdout_access_allowed_now") is False,
        "VAULT_RELEASE_ZERO": vault.get("vault_release_allowed_count") == 0,
        "OLD_SHORT_MONITORING_READY": old_short_final_decision == "OLD_SHORT_MONITORING_READY_CONTINUE_COLLECT_NO_CAPITAL",
        "OLD_SHORT_NOT_CAPITAL_READY": bool(old_short_next_required and int(old_short_next_required) > 0),
        "NO_BACKUP_DELETE_ALLOWED": backup_delete_allowed_now is False,
        "NO_BACKUP_MOVE_ALLOWED": backup_move_allowed_now is False,
        "NO_GITIGNORE_CHANGE_ALLOWED": gitignore_change_allowed_now is False,
    }

    failed = [k for k, v in prerequisites.items() if v is not True]
    pass_decision = len(failed) == 0

    if pass_decision:
        decision_status = "BACKUP_HYGIENE_APPROVAL_ABSENT_STANDARD_STACK_REFRESH_READY"
        severity = "ATTENTION"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        next_action = "BUILD_REPO_ONLY_STANDARD_OS_STATUS_REFRESH_NO_RUNTIME_ACTION"
        reason = "No valid cleanup approval exists; hygiene remains pending and repo-only standard OS status refresh is recommended."
        next_key = NEXT_RESEARCH_KEY
        next_module = NEXT_MODULE
        return_code = 0
    else:
        decision_status = "BACKUP_HYGIENE_OR_STANDARD_REFRESH_DECISION_ATTENTION_REVIEW_REQUIRED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_BACKUP_HYGIENE_STANDARD_REFRESH_PREREQUISITES"
        reason = f"failed_prerequisites={failed}"
        next_key = None
        next_module = None
        return_code = 2

    decision_doc = {
        "decision_name": "edge_factory_os_backup_hygiene_approval_or_standard_stack_refresh_decision_v1",
        "created_at_utc": utc_now_iso(),
        "decision_status": decision_status,
        "manual_approval_present": manual_approval_present,
        "manual_approval_valid": manual_approval_is_valid,
        "manual_approval_json": str(HUMAN_APPROVAL_JSON),
        "backup_delete_allowed_now": backup_delete_allowed_now,
        "backup_move_allowed_now": backup_move_allowed_now,
        "gitignore_change_allowed_now": gitignore_change_allowed_now,
        "pending_hygiene_item_count": len(pending_rows),
        "known_backup_pending_count": known_backup_pending_count,
        "universe_guard_review_required": universe_guard_review_required,
        "standard_status_refresh_recommended": pass_decision,
        "old_short_final_decision": old_short_final_decision,
        "old_short_closed_trades": old_short_closed_trades,
        "old_short_next_required_closed_trades_for_capital_review": old_short_next_required,
        "pending_hygiene_rows": pending_rows,
        "hard_rules": [
            "No delete without explicit manual approval and separate delete module.",
            "No move without explicit manual approval and separate move module.",
            "No .gitignore modification without explicit approval and separate module.",
            "Universe coverage guard must be classified before action.",
            "Standard OS status refresh may proceed repo-only.",
        ],
        **SAFETY_FLAGS,
    }

    pending_doc = {
        "report_name": "edge_factory_os_backup_hygiene_pending_items_v1",
        "created_at_utc": utc_now_iso(),
        "report_status": "BACKUP_HYGIENE_PENDING_ITEMS_RECORDED_NO_ACTION",
        "pending_hygiene_item_count": len(pending_rows),
        "known_backup_pending_count": known_backup_pending_count,
        "universe_guard_review_required": universe_guard_review_required,
        "pending_hygiene_rows": pending_rows,
        "delete_allowed_now": False,
        "move_allowed_now": False,
        "archive_allowed_now": False,
        "gitignore_change_allowed_now": False,
        **SAFETY_FLAGS,
    }

    state = {
        "state_name": "edge_factory_os_backup_hygiene_approval_or_standard_stack_refresh_state_v1",
        "created_at_utc": utc_now_iso(),
        "decision_status": decision_status,
        "strict_policy_key": STRICT_POLICY_KEY,
        "manual_approval_present": manual_approval_present,
        "manual_approval_valid": manual_approval_is_valid,
        "backup_delete_allowed_now": backup_delete_allowed_now,
        "backup_move_allowed_now": backup_move_allowed_now,
        "gitignore_change_allowed_now": gitignore_change_allowed_now,
        "pending_hygiene_item_count": len(pending_rows),
        "known_backup_pending_count": known_backup_pending_count,
        "universe_guard_review_required": universe_guard_review_required,
        "old_short_final_decision": old_short_final_decision,
        "old_short_closed_trades": old_short_closed_trades,
        "old_short_next_required_closed_trades_for_capital_review": old_short_next_required,
        "standard_status_refresh_recommended": pass_decision,
        "failed_prerequisite_count": len(failed),
        "failed_prerequisites": failed,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        **SAFETY_FLAGS,
    }

    next_queue = {
        "queue_name": "edge_factory_os_backup_hygiene_approval_or_standard_stack_refresh_next_queue_v1",
        "created_at_utc": utc_now_iso(),
        "queue_status": "BACKUP_HYGIENE_STANDARD_REFRESH_NEXT_QUEUE_READY" if pass_decision else "BACKUP_HYGIENE_STANDARD_REFRESH_QUEUE_BLOCKED",
        "top_next_research_key": next_key,
        "top_next_module": next_module,
        "next_steps": [
            {
                "research_key": NEXT_RESEARCH_KEY,
                "module": NEXT_MODULE,
                "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
                "purpose": "Refresh consolidated repo-only OS status after governance repairs and old_short monitor classification.",
                "backup_delete_allowed_now": False,
                "backup_move_allowed_now": False,
                "runtime_touch_allowed": False,
                "capital_change_allowed": False,
                "active_paper_allowed": False,
                "live_allowed": False,
                "real_orders_allowed": False,
            }
        ] if pass_decision else [],
        **SAFETY_FLAGS,
    }

    write_json(REPO_DECISION_JSON, decision_doc)
    write_json(REPO_PENDING_JSON, pending_doc)
    write_json(REPO_STATE_JSON, state)
    write_json(REPO_NEXT_QUEUE_JSON, next_queue)
    write_csv(OUT_CSV, pending_rows)

    result = {
        "module_name": "edge_factory_os_backup_hygiene_approval_or_standard_stack_refresh_v1",
        "created_at_utc": utc_now_iso(),
        "decision_status": decision_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "manual_approval_present": manual_approval_present,
        "manual_approval_valid": manual_approval_is_valid,
        "backup_delete_allowed_now": backup_delete_allowed_now,
        "backup_move_allowed_now": backup_move_allowed_now,
        "gitignore_change_allowed_now": gitignore_change_allowed_now,
        "pending_hygiene_item_count": len(pending_rows),
        "known_backup_pending_count": known_backup_pending_count,
        "universe_guard_review_required": universe_guard_review_required,
        "old_short_final_decision": old_short_final_decision,
        "old_short_closed_trades": old_short_closed_trades,
        "old_short_next_required_closed_trades_for_capital_review": old_short_next_required,
        "standard_status_refresh_recommended": pass_decision,
        "failed_prerequisite_count": len(failed),
        "failed_prerequisites": failed,
        "pending_hygiene_rows": pending_rows,
        "decision_doc": decision_doc,
        "pending_doc": pending_doc,
        "state": state,
        "next_queue": next_queue,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "pending_csv": str(OUT_CSV),
        "repo_decision_json": str(REPO_DECISION_JSON),
        "repo_pending_json": str(REPO_PENDING_JSON),
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
