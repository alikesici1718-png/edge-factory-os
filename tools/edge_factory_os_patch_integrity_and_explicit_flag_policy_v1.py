#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Patch Integrity + Explicit Safety Flag Policy v1

Purpose:
- Inspect policy-sensitive backup diffs after external audit.
- Classify the source-panel anomaly blocked_patch backup.
- Classify the joint-null readonly fix backup.
- Log whether these were process risks, technical fixes, or policy violations.
- Add an explicit safety flag enforcement policy:
    * missing/None safety flag means action is NOT allowed
    * but missing/None safety flag must NOT make plugin/schema "ready"
    * readiness requires explicit fields with explicit False where blocked
- Do NOT delete backup files.
- Do NOT run research.
- Do NOT touch runtime/capital/live.
"""

from __future__ import annotations

import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = BASE_DIR / "edge_factory_os_repo"
POLICY_DIR = REPO_DIR / "edge_factory_os_framework" / "policies"
QUEUE_DIR = REPO_DIR / "edge_factory_os_framework" / "queues"
STATUS_DIR = REPO_DIR / "edge_factory_os_framework" / "status"

SOURCE_PANEL_CURRENT = REPO_DIR / "tools" / "edge_factory_os_source_panel_anomaly_discovery_runner_v1.py"
SOURCE_PANEL_BAK = REPO_DIR / "tools" / "edge_factory_os_source_panel_anomaly_discovery_runner_v1.py.blocked_patch_bak_20260514_000647"

JOINT_NULL_CURRENT = REPO_DIR / "tools" / "edge_factory_os_joint_null_distribution_validator_v1.py"
JOINT_NULL_BAK = REPO_DIR / "tools" / "edge_factory_os_joint_null_distribution_validator_v1.py.readonly_fix_bak_20260514_022123"

OUT_DIR = BASE_DIR / "edge_factory_os_patch_integrity_and_explicit_flag_policy"
OUT_JSON = OUT_DIR / "patch_integrity_and_explicit_flag_policy_latest.json"
OUT_TXT = OUT_DIR / "patch_integrity_and_explicit_flag_policy_latest.txt"

REPO_PATCH_AUDIT_JSON = STATUS_DIR / "patch_integrity_audit_v1.json"
REPO_EXPLICIT_FLAG_POLICY_JSON = POLICY_DIR / "explicit_safety_flag_enforcement_policy_v1.json"
REPO_NEXT_QUEUE_JSON = QUEUE_DIR / "patch_integrity_explicit_flag_policy_next_queue_v1.json"

NEXT_RESEARCH_KEY = "RD8_04_GOVERNANCE_REPAIR_SUITE_LEDGER_ALPHA_PREREG"
NEXT_MODULE = "edge_factory_os_governance_repair_suite_ledger_alpha_prereg_v1.py"

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


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True, default=str), encoding="utf-8")
    tmp.replace(path)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def git_status_short() -> List[str]:
    try:
        p = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(REPO_DIR),
            text=True,
            capture_output=True,
            timeout=30,
        )
        return [x for x in p.stdout.splitlines() if x.strip()]
    except Exception as exc:
        return [f"GIT_STATUS_ERROR: {type(exc).__name__}: {exc}"]


def git_diff_no_index(a: Path, b: Path) -> Dict[str, Any]:
    try:
        p = subprocess.run(
            ["git", "diff", "--no-index", str(a), str(b)],
            cwd=str(REPO_DIR),
            text=True,
            capture_output=True,
            timeout=60,
        )
        return {
            "returncode": p.returncode,
            "stdout": p.stdout,
            "stderr": p.stderr,
            "has_diff": bool(p.stdout.strip()),
        }
    except Exception as exc:
        return {
            "returncode": None,
            "stdout": "",
            "stderr": f"{type(exc).__name__}: {exc}",
            "has_diff": False,
        }


def classify_source_panel_patch(current_text: str, bak_text: str) -> Dict[str, Any]:
    current_has_helper = "def explicitly_blocked" in current_text
    bak_has_helper = "def explicitly_blocked" in bak_text
    current_uses_helper = "explicitly_blocked(plugin.get(\"plugin_expansion_allowed\"))" in current_text
    bak_uses_strict_false = "plugin.get(\"plugin_expansion_allowed\") is False" in bak_text

    policy_sensitive = current_has_helper and current_uses_helper and bak_uses_strict_false and not bak_has_helper

    if policy_sensitive:
        classification = "POLICY_SENSITIVE_PATCH_LOGGED_SCHEMA_WEAKNESS_REPAIR_REQUIRED"
        violation = False
        severity = "ATTENTION"
        interpretation = (
            "The current source-panel anomaly runner treats missing/None/False plugin_expansion_allowed as blocked. "
            "This did not enable candidates/release/runtime/capital/live, and the route later failed deep validation. "
            "However, using missing/None to satisfy plugin readiness can hide schema omissions. "
            "Future modules must separate action safety from readiness validation."
        )
    else:
        classification = "SOURCE_PANEL_PATCH_REVIEW_REQUIRED"
        violation = True
        severity = "ATTENTION"
        interpretation = "Unexpected diff pattern. Manual review required before continuing."

    return {
        "file_pair": "source_panel_anomaly_discovery_runner current vs blocked_patch_bak",
        "classification": classification,
        "severity": severity,
        "policy_violation_detected": violation,
        "current_has_explicitly_blocked_helper": current_has_helper,
        "backup_has_explicitly_blocked_helper": bak_has_helper,
        "current_uses_explicitly_blocked_for_plugin_expansion": current_uses_helper,
        "backup_uses_plugin_expansion_is_false": bak_uses_strict_false,
        "interpretation": interpretation,
        "required_repair": [
            "Add explicit safety flag policy.",
            "Future plugin readiness requires explicit field presence.",
            "Missing safety flag means action blocked, but schema not ready.",
            "Do not re-run closed source-panel anomaly route.",
        ],
    }


def classify_joint_null_patch(current_text: str, bak_text: str) -> Dict[str, Any]:
    current_has_copy_true = "to_numpy(copy=True)" in current_text
    bak_has_copy_false = "to_numpy()" in bak_text
    current_has_progress = "JOINT_NULL_PROGRESS" in current_text
    bak_has_progress = "JOINT_NULL_PROGRESS" in bak_text

    technical_fix = current_has_copy_true and bak_has_copy_false

    if technical_fix:
        classification = "TECHNICAL_BUG_FIX_CONFIRMED_NO_POLICY_VIOLATION"
        violation = False
        severity = "OK"
        interpretation = (
            "The current joint-null validator uses to_numpy(copy=True), fixing the read-only NumPy assignment crash. "
            "Progress logging was also added. This is a technical fix, not a methodology relaxation."
        )
    else:
        classification = "JOINT_NULL_PATCH_REVIEW_REQUIRED"
        violation = True
        severity = "ATTENTION"
        interpretation = "Unexpected diff pattern. Manual review required."

    return {
        "file_pair": "joint_null_distribution_validator current vs readonly_fix_bak",
        "classification": classification,
        "severity": severity,
        "policy_violation_detected": violation,
        "current_has_to_numpy_copy_true": current_has_copy_true,
        "backup_has_to_numpy_without_copy": bak_has_copy_false,
        "current_has_progress_logging": current_has_progress,
        "backup_has_progress_logging": bak_has_progress,
        "interpretation": interpretation,
        "required_repair": [
            "Keep current technical fix.",
            "Do not restore backup.",
            "Backup may be deleted only after audit state is committed and .gitignore covers backup patterns.",
        ],
    }


def build_text(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS PATCH INTEGRITY + EXPLICIT SAFETY FLAG POLICY v1")
    lines.append("=" * 100)

    for key in [
        "audit_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "source_panel_patch_classification",
        "source_panel_policy_violation_detected",
        "joint_null_patch_classification",
        "joint_null_policy_violation_detected",
        "explicit_flag_policy_status",
        "backup_delete_allowed_now",
        "closed_route_rerun_allowed",
        "next_recommended_research_key",
        "next_module",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("SOURCE PANEL PATCH AUDIT")
    lines.append("-" * 100)
    lines.append(json.dumps(result.get("source_panel_patch_audit"), indent=2, ensure_ascii=False))

    lines.append("")
    lines.append("JOINT NULL PATCH AUDIT")
    lines.append("-" * 100)
    lines.append(json.dumps(result.get("joint_null_patch_audit"), indent=2, ensure_ascii=False))

    lines.append("")
    lines.append("EXPLICIT FLAG POLICY")
    lines.append("-" * 100)
    lines.append(json.dumps(result.get("explicit_flag_policy"), indent=2, ensure_ascii=False))

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        lines.append(f"{key}: {value}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS PATCH INTEGRITY + EXPLICIT SAFETY FLAG POLICY v1")
    print("=" * 100)
    print(f"audit_status: {result.get('audit_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"source_panel_patch_classification: {result.get('source_panel_patch_classification')}")
    print(f"source_panel_policy_violation_detected: {result.get('source_panel_policy_violation_detected')}")
    print(f"joint_null_patch_classification: {result.get('joint_null_patch_classification')}")
    print(f"joint_null_policy_violation_detected: {result.get('joint_null_policy_violation_detected')}")
    print(f"explicit_flag_policy_status: {result.get('explicit_flag_policy_status')}")
    print(f"backup_delete_allowed_now: {result.get('backup_delete_allowed_now')}")
    print(f"closed_route_rerun_allowed: {result.get('closed_route_rerun_allowed')}")
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
    print(f"PATCH_AUDIT: {result.get('patch_audit_json')}")
    print(f"POLICY: {result.get('explicit_flag_policy_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    source_current = read_text(SOURCE_PANEL_CURRENT)
    source_bak = read_text(SOURCE_PANEL_BAK)
    joint_current = read_text(JOINT_NULL_CURRENT)
    joint_bak = read_text(JOINT_NULL_BAK)

    source_diff = git_diff_no_index(SOURCE_PANEL_CURRENT, SOURCE_PANEL_BAK)
    joint_diff = git_diff_no_index(JOINT_NULL_CURRENT, JOINT_NULL_BAK)

    source_audit = classify_source_panel_patch(source_current, source_bak)
    joint_audit = classify_joint_null_patch(joint_current, joint_bak)

    hard_violation = bool(source_audit["policy_violation_detected"] or joint_audit["policy_violation_detected"])

    explicit_flag_policy = {
        "policy_name": "edge_factory_os_explicit_safety_flag_enforcement_policy_v1",
        "created_at_utc": utc_now_iso(),
        "policy_status": "EXPLICIT_SAFETY_FLAG_POLICY_ACTIVE",
        "core_rule": "Missing/None safety flag blocks action but does not satisfy readiness.",
        "action_safety_interpretation": {
            "True": "allowed only if all higher gates also pass",
            "False": "blocked",
            "None_or_missing": "blocked",
        },
        "schema_readiness_interpretation": {
            "required_field_present_and_false": "ready for blocked-state validation",
            "required_field_missing": "schema_not_ready",
            "required_field_none": "schema_not_ready",
            "required_field_true": "not blocked; requires explicit authorization gate",
        },
        "hard_requirements_for_future_plugins": [
            "plugin_expansion_allowed must be present",
            "candidate_generation_allowed must be present",
            "family_release_allowed must be present",
            "runtime_touch_allowed must be present",
            "capital_change_allowed must be present",
            "active_paper_allowed must be present",
            "live_allowed must be present",
            "real_orders_allowed must be present",
            "Missing fields make plugin_ready=False even though action remains blocked.",
        ],
        "forbidden_pattern": "Do not use missing/None safety flags to satisfy plugin_ready or contract_ready.",
        "allowed_pattern": "Use missing/None safety flags only to deny actions.",
        "source_panel_patch_resolution": source_audit["classification"],
        "joint_null_patch_resolution": joint_audit["classification"],
        "closed_route_rerun_allowed": False,
        **SAFETY_FLAGS,
    }

    patch_audit = {
        "audit_name": "edge_factory_os_patch_integrity_audit_v1",
        "created_at_utc": utc_now_iso(),
        "audit_status": "PATCH_INTEGRITY_AUDIT_PASS_WITH_SCHEMA_REPAIR_REQUIRED" if not hard_violation else "PATCH_INTEGRITY_AUDIT_FAIL_MANUAL_REVIEW_REQUIRED",
        "source_panel_patch_audit": source_audit,
        "joint_null_patch_audit": joint_audit,
        "source_panel_diff_has_content": source_diff["has_diff"],
        "joint_null_diff_has_content": joint_diff["has_diff"],
        "source_panel_diff_summary": {
            "current": str(SOURCE_PANEL_CURRENT),
            "backup": str(SOURCE_PANEL_BAK),
            "returncode": source_diff["returncode"],
            "stderr": source_diff["stderr"][:1000],
        },
        "joint_null_diff_summary": {
            "current": str(JOINT_NULL_CURRENT),
            "backup": str(JOINT_NULL_BAK),
            "returncode": joint_diff["returncode"],
            "stderr": joint_diff["stderr"][:1000],
        },
        "git_status_short_lines": git_status_short(),
        "backup_delete_allowed_now": False,
        "backup_delete_allowed_after": [
            "patch integrity audit committed",
            "explicit safety flag policy committed",
            "backup ignore policy committed",
            "manual user approval",
        ],
        "closed_source_panel_route_rerun_allowed": False,
        **SAFETY_FLAGS,
    }

    next_queue = {
        "queue_name": "edge_factory_os_patch_integrity_explicit_flag_policy_next_queue_v1",
        "created_at_utc": utc_now_iso(),
        "queue_status": "PATCH_INTEGRITY_NEXT_QUEUE_READY" if not hard_violation else "PATCH_INTEGRITY_QUEUE_BLOCKED_MANUAL_REVIEW",
        "top_next_research_key": NEXT_RESEARCH_KEY if not hard_violation else None,
        "top_next_module": NEXT_MODULE if not hard_violation else None,
        "next_steps": [
            {
                "research_key": NEXT_RESEARCH_KEY,
                "module": NEXT_MODULE,
                "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
                "purpose": "Repair ledger/alpha/pre-registration enforcement after patch integrity is logged.",
                "research_execution_allowed_now": False,
                "candidate_generation_allowed": False,
                "family_release_allowed": False,
                "runtime_touch_allowed": False,
                "capital_change_allowed": False,
                "active_paper_allowed": False,
                "live_allowed": False,
                "real_orders_allowed": False,
            }
        ] if not hard_violation else [],
        **SAFETY_FLAGS,
    }

    if hard_violation:
        audit_status = "PATCH_INTEGRITY_AUDIT_FAIL_MANUAL_REVIEW_REQUIRED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "STOP_AND_MANUALLY_REVIEW_PATCH_DIFFS"
        reason = "Unexpected patch diff pattern detected."
        next_key = None
        next_module = None
        return_code = 2
    else:
        audit_status = "PATCH_INTEGRITY_AUDIT_PASS_WITH_EXPLICIT_FLAG_POLICY_ACTIVE"
        severity = "ATTENTION"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        next_action = "BUILD_GOVERNANCE_REPAIR_SUITE_LEDGER_ALPHA_PREREG_NO_EXECUTION"
        reason = "Patch integrity logged; source-panel patch is policy-sensitive but not a detected hard violation; explicit flag policy now active."
        next_key = NEXT_RESEARCH_KEY
        next_module = NEXT_MODULE
        return_code = 0

    result = {
        "module_name": "edge_factory_os_patch_integrity_and_explicit_flag_policy_v1",
        "created_at_utc": utc_now_iso(),
        "audit_status": audit_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "source_panel_patch_classification": source_audit["classification"],
        "source_panel_policy_violation_detected": source_audit["policy_violation_detected"],
        "joint_null_patch_classification": joint_audit["classification"],
        "joint_null_policy_violation_detected": joint_audit["policy_violation_detected"],
        "explicit_flag_policy_status": explicit_flag_policy["policy_status"],
        "backup_delete_allowed_now": False,
        "closed_route_rerun_allowed": False,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        "source_panel_patch_audit": source_audit,
        "joint_null_patch_audit": joint_audit,
        "explicit_flag_policy": explicit_flag_policy,
        "patch_audit": patch_audit,
        "next_queue": next_queue,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "patch_audit_json": str(REPO_PATCH_AUDIT_JSON),
        "explicit_flag_policy_json": str(REPO_EXPLICIT_FLAG_POLICY_JSON),
        "next_queue_json": str(REPO_NEXT_QUEUE_JSON),
        **SAFETY_FLAGS,
    }

    write_json(REPO_PATCH_AUDIT_JSON, patch_audit)
    write_json(REPO_EXPLICIT_FLAG_POLICY_JSON, explicit_flag_policy)
    write_json(REPO_NEXT_QUEUE_JSON, next_queue)
    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text(result))
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
