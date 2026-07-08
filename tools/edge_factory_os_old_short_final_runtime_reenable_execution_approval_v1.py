from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]

PATCH_PREVIEW_JSON = (
    REPO_ROOT
    / "edge_factory_os_old_short_guarded_runtime_reenable_patch_preview"
    / "old_short_guarded_runtime_reenable_patch_preview_latest.json"
)

OUT_DIR = REPO_ROOT / "edge_factory_os_old_short_final_runtime_reenable_execution_approval"
OUT_JSON = OUT_DIR / "old_short_final_runtime_reenable_execution_approval_latest.json"
OUT_TXT = OUT_DIR / "old_short_final_runtime_reenable_execution_approval_latest.txt"

REQUIRED_PATCH_PREVIEW_STATUS = "OLD_SHORT_GUARDED_RUNTIME_REENABLE_PATCH_PREVIEW_READY_NO_APPLY"
REQUIRED_PREVIEW_FINAL_DECISION = "PATCH_PREVIEW_READY_REQUIRE_FINAL_EXECUTION_APPROVAL_BEFORE_APPLY"

NOW_UTC = datetime.now(timezone.utc).isoformat()

SAFETY_FLAGS: Dict[str, bool] = {
    "repo_only": True,
    "runtime_touch_allowed": False,
    "launcher_allowed": False,
    "runtime_patch_allowed": False,
    "runtime_patch_apply_allowed_now": False,
    "patch_apply_allowed_now": False,
    "backup_delete_allowed": False,
    "backup_move_allowed": False,
    "gitignore_change_allowed": False,
    "strategy_research_allowed": False,
    "candidate_generation_allowed": False,
    "candidate_contract_allowed": False,
    "family_release_allowed": False,
    "promotion_allowed": False,
    "capital_change_allowed": False,
    "active_paper_execution_allowed_now": False,
    "live_allowed": False,
    "real_orders_allowed": False,
    "file_delete_allowed": False,
    "file_move_allowed": False,
    "archive_allowed": False,
    "execution_allowed": False,
    "old_short_runtime_enable_allowed_now": False,
}

FORBIDDEN_ACTIONS: List[str] = [
    "Do not apply the patch from this module.",
    "Do not touch runtime.",
    "Do not run launcher.",
    "Do not enable old_short yet.",
    "Do not enable active paper execution yet.",
    "Do not change capital.",
    "Do not enable live trading.",
    "Do not enable real orders.",
    "Do not delete, move, or archive backup files.",
    "Do not change .gitignore.",
    "Do not use git add -f.",
]

PREVIEW_SAFETY_BLOCKERS: Tuple[str, ...] = (
    "runtime_touch_allowed",
    "launcher_allowed",
    "runtime_patch_allowed",
    "patch_apply_allowed_now",
    "capital_change_allowed",
    "active_paper_execution_allowed_now",
    "live_allowed",
    "real_orders_allowed",
)


def run_cmd(args: List[str], timeout: int = 30) -> Dict[str, Any]:
    try:
        proc = subprocess.run(
            args,
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except Exception as exc:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": repr(exc),
        }


def inspect_git() -> Dict[str, Any]:
    status = run_cmd(["git", "-C", str(REPO_ROOT), "status", "--short"])
    head = run_cmd(["git", "-C", str(REPO_ROOT), "rev-parse", "--short", "HEAD"])
    last = run_cmd(["git", "-C", str(REPO_ROOT), "log", "-1", "--pretty=%h %s"])

    lines = status["stdout"].splitlines() if status["ok"] else []
    lines = [x.strip().replace("\\", "/") for x in lines if x.strip()]

    return {
        "status_ok": status["ok"],
        "head_short": head["stdout"].strip() if head["ok"] else None,
        "last_commit": last["stdout"].strip() if last["ok"] else None,
        "git_status_lines": lines,
        "untracked_or_dirty_count": len(lines),
        "known_backup_pending_count": len([
            x for x in lines
            if ".bak" in x
            or "_bak_" in x
            or "blocked_patch_bak" in x
            or "readonly_fix_bak" in x
        ]),
        "universe_guard_review_required": any(
            "tools/edge_factory_os_universe_coverage_guard_v1.py" in x
            for x in lines
        ),
    }


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def validate_restore_scope(scope: Any) -> Tuple[bool, List[str], Dict[str, Any]]:
    errors: List[str] = []

    expected = {
        "restore_family": "old_short",
        "restore_mode": "MONITORING_OR_ACTIVE_PAPER_ONLY",
        "capital_change_allowed": False,
        "live_trading_allowed": False,
        "real_orders_allowed": False,
        "runtime_enable_allowed_now": False,
        "patch_apply_allowed_now": False,
    }

    detail = {
        "restore_scope_object": scope,
        "expected_fields": expected,
    }

    if not isinstance(scope, dict):
        errors.append("restore_scope_missing_or_not_object")
        return False, errors, detail

    for key, expected_value in expected.items():
        observed = scope.get(key)
        if observed != expected_value:
            errors.append(
                f"restore_scope_field_mismatch:{key}:observed={observed!r}:expected={expected_value!r}"
            )

    return len(errors) == 0, errors, detail


def validate_preview_safety_flags(flags: Any) -> Tuple[bool, List[str], Dict[str, Any]]:
    errors: List[str] = []

    detail = {
        "safety_flags_object": flags,
        "required_false_flags": list(PREVIEW_SAFETY_BLOCKERS),
    }

    if not isinstance(flags, dict):
        errors.append("safety_flags_missing_or_not_object")
        return False, errors, detail

    for key in PREVIEW_SAFETY_BLOCKERS:
        if key not in flags:
            errors.append(f"safety_flag_missing:{key}")
            continue

        if flags[key] is not False:
            errors.append(f"safety_flag_not_false:{key}:observed={flags[key]!r}")

    runtime_patch_allowed = bool(flags.get("runtime_patch_allowed"))
    patch_apply_allowed_now = bool(flags.get("patch_apply_allowed_now"))
    detail["runtime_patch_apply_allowed_now_derived"] = (
        runtime_patch_allowed or patch_apply_allowed_now
    )

    if detail["runtime_patch_apply_allowed_now_derived"] is not False:
        errors.append("runtime_patch_apply_allowed_now_derived_not_false")

    return len(errors) == 0, errors, detail


def policy_gate(
    name: str,
    status: str,
    observed: Any,
    required: Any,
    evidence: str,
) -> Dict[str, Any]:
    return {
        "gate": name,
        "status": status,
        "observed": observed,
        "required": required,
        "evidence": evidence,
    }


def build_report() -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    git_state = inspect_git()
    preview = load_json(PATCH_PREVIEW_JSON)

    failed_gates: List[str] = []

    preview_loaded = preview is not None
    preview_status = preview.get("patch_preview_status") if preview else None
    preview_final_decision = preview.get("final_decision") if preview else None

    preview_status_ok = preview_status == REQUIRED_PATCH_PREVIEW_STATUS
    preview_final_decision_ok = preview_final_decision == REQUIRED_PREVIEW_FINAL_DECISION

    if not preview_loaded:
        failed_gates.append("PATCH_PREVIEW_JSON_MISSING_OR_UNREADABLE")

    if not preview_status_ok:
        failed_gates.append("PATCH_PREVIEW_STATUS_MISMATCH")

    if not preview_final_decision_ok:
        failed_gates.append("PATCH_PREVIEW_FINAL_DECISION_MISMATCH")

    restore_scope = preview.get("restore_scope") if preview else None
    restore_scope_ok, restore_scope_errors, restore_scope_detail = validate_restore_scope(restore_scope)

    if not restore_scope_ok:
        failed_gates.append("RESTORE_SCOPE_INVALID")

    preview_safety_flags = preview.get("safety_flags") if preview else None
    preview_safety_ok, preview_safety_errors, preview_safety_detail = validate_preview_safety_flags(
        preview_safety_flags
    )

    if not preview_safety_ok:
        failed_gates.append("PREVIEW_SAFETY_FLAGS_INVALID")

    old_short_status = preview.get("old_short_status") if preview else None

    gates = [
        policy_gate(
            "PATCH_PREVIEW_JSON_LOADED",
            "PASS" if preview_loaded else "FAIL",
            preview_loaded,
            True,
            "The final execution approval must read the patch preview artifact.",
        ),
        policy_gate(
            "PATCH_PREVIEW_STATUS_READY_NO_APPLY",
            "PASS" if preview_status_ok else "FAIL",
            preview_status,
            REQUIRED_PATCH_PREVIEW_STATUS,
            "The patch preview must be ready but explicitly not applied.",
        ),
        policy_gate(
            "PATCH_PREVIEW_FINAL_DECISION_REQUIRES_APPROVAL",
            "PASS" if preview_final_decision_ok else "FAIL",
            preview_final_decision,
            REQUIRED_PREVIEW_FINAL_DECISION,
            "The previous module must require final execution approval before apply.",
        ),
        policy_gate(
            "RESTORE_SCOPE_STILL_OLD_SHORT_MONITORING_ONLY",
            "PASS" if restore_scope_ok else "FAIL",
            restore_scope_detail,
            {
                "restore_family": "old_short",
                "restore_mode": "MONITORING_OR_ACTIVE_PAPER_ONLY",
                "capital/live/real_orders/runtime_enable/patch_apply": False,
            },
            "Restore scope must remain old_short monitoring/active-paper only.",
        ),
        policy_gate(
            "PREVIEW_SAFETY_FLAGS_STILL_BLOCK_EXECUTION",
            "PASS" if preview_safety_ok else "FAIL",
            preview_safety_detail,
            {
                "runtime_touch": False,
                "launcher": False,
                "runtime_patch": False,
                "patch_apply": False,
                "capital": False,
                "active_paper_execution": False,
                "live": False,
                "real_orders": False,
            },
            "Preview safety flags must still block all execution and risk pathways.",
        ),
        policy_gate(
            "THIS_MODULE_NO_RUNTIME_OR_PATCH_APPLY",
            "BLOCKED_AS_REQUIRED",
            {
                "runtime_touch_allowed": SAFETY_FLAGS["runtime_touch_allowed"],
                "launcher_allowed": SAFETY_FLAGS["launcher_allowed"],
                "runtime_patch_apply_allowed_now": SAFETY_FLAGS["runtime_patch_apply_allowed_now"],
                "execution_allowed": SAFETY_FLAGS["execution_allowed"],
            },
            {
                "runtime_touch_allowed": False,
                "launcher_allowed": False,
                "runtime_patch_apply_allowed_now": False,
                "execution_allowed": False,
            },
            "This approval module records approval only; it does not apply patch or touch runtime.",
        ),
        policy_gate(
            "NO_CAPITAL_LIVE_REAL_ORDER",
            "BLOCKED_AS_REQUIRED",
            {
                "capital_change_allowed": SAFETY_FLAGS["capital_change_allowed"],
                "live_allowed": SAFETY_FLAGS["live_allowed"],
                "real_orders_allowed": SAFETY_FLAGS["real_orders_allowed"],
            },
            {
                "capital_change_allowed": False,
                "live_allowed": False,
                "real_orders_allowed": False,
            },
            "Final approval still does not authorize capital, live trading, or real orders.",
        ),
    ]

    hard_failed = [gate["gate"] for gate in gates if gate["status"] == "FAIL"]
    failed_gates = sorted(set(failed_gates + hard_failed))

    if not failed_gates:
        approval_status = "OLD_SHORT_FINAL_RUNTIME_REENABLE_EXECUTION_APPROVAL_READY_FOR_GUARDED_APPLY"
        severity = "ATTENTION"
        final_decision = "FINAL_APPROVAL_RECORDED_BUILD_GUARDED_APPLY_MODULE_NEXT"
        next_action = "BUILD_GUARDED_APPLY_MODULE_BUT_DO_NOT_RUN_LAUNCHER_OR_LIVE"
        next_module = "edge_factory_os_old_short_guarded_runtime_reenable_apply_v1.py"
    else:
        approval_status = "OLD_SHORT_FINAL_RUNTIME_REENABLE_EXECUTION_APPROVAL_BLOCKED"
        severity = "HIGH"
        final_decision = "STOP_FINAL_APPROVAL_BLOCKED_DO_NOT_APPLY"
        next_action = "STOP_REVIEW_PATCH_PREVIEW_AND_SAFETY_FLAGS_NO_RUNTIME_ACTION"
        next_module = "edge_factory_os_old_short_guarded_runtime_reenable_patch_preview_v1.py"

    result = {
        "module": "edge_factory_os_old_short_final_runtime_reenable_execution_approval_v1.py",
        "generated_at_utc": NOW_UTC,
        "repo_root": str(REPO_ROOT),
        "approval_status": approval_status,
        "severity": severity,
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "reason": (
            "This module records final guarded-apply approval readiness only. "
            "It does not apply a patch, touch runtime, run launcher, enable old_short, enable active paper execution, "
            "change capital, enable live trading, or enable real orders."
        ),
        "input_patch_preview": {
            "path": rel(PATCH_PREVIEW_JSON),
            "loaded": preview_loaded,
            "patch_preview_status": preview_status,
            "required_patch_preview_status": REQUIRED_PATCH_PREVIEW_STATUS,
            "final_decision": preview_final_decision,
            "required_final_decision": REQUIRED_PREVIEW_FINAL_DECISION,
        },
        "old_short_status": old_short_status,
        "restore_scope": restore_scope,
        "restore_scope_validation": {
            "ok": restore_scope_ok,
            "errors": restore_scope_errors,
            "detail": restore_scope_detail,
        },
        "preview_safety_flags_validation": {
            "ok": preview_safety_ok,
            "errors": preview_safety_errors,
            "detail": preview_safety_detail,
        },
        "manual_final_execution_approval": {
            "approval_recorded": not failed_gates,
            "approval_scope": "BUILD_GUARDED_APPLY_MODULE_ONLY",
            "runtime_enable_approved_now": False,
            "patch_apply_approved_now": False,
            "active_paper_execution_approved_now": False,
            "capital_change_approved": False,
            "live_trading_approved": False,
            "real_orders_approved": False,
        },
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "safety_flags": SAFETY_FLAGS,
        "policy_gates": gates,
        "failed_gates": failed_gates,
        "git_state": git_state,
        "outputs": {
            "json": str(OUT_JSON),
            "txt": str(OUT_TXT),
        },
    }

    return result


def write_outputs(result: Dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    lines: List[str] = []
    lines.append("EDGE FACTORY OS OLD_SHORT FINAL RUNTIME RE-ENABLE EXECUTION APPROVAL v1")
    lines.append("=" * 100)
    lines.append(f"approval_status: {result['approval_status']}")
    lines.append(f"severity: {result['severity']}")
    lines.append(f"allowed_scope: {result['allowed_scope']}")
    lines.append(f"final_decision: {result['final_decision']}")
    lines.append(f"next_action: {result['next_action']}")
    lines.append(f"next_module: {result['next_module']}")
    lines.append("")
    lines.append("INPUT PATCH PREVIEW")
    lines.append("-" * 100)
    for key, value in result["input_patch_preview"].items():
        lines.append(f"{key}: {value}")
    lines.append("")
    lines.append("OLD_SHORT STATUS")
    lines.append("-" * 100)
    lines.append(json.dumps(result["old_short_status"], indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("RESTORE SCOPE")
    lines.append("-" * 100)
    lines.append(json.dumps(result["restore_scope"], indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("MANUAL FINAL EXECUTION APPROVAL")
    lines.append("-" * 100)
    for key, value in result["manual_final_execution_approval"].items():
        lines.append(f"{key}: {value}")
    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for key, value in result["safety_flags"].items():
        lines.append(f"{key}: {value}")
    lines.append("")
    lines.append("POLICY GATES")
    lines.append("-" * 100)
    for row in result["policy_gates"]:
        lines.append(f"{row['gate']}: {row['status']}")
        lines.append(f"  observed: {row['observed']}")
        lines.append(f"  required: {row['required']}")
        lines.append(f"  evidence: {row['evidence']}")
    lines.append("")
    lines.append("FAILED GATES")
    lines.append("-" * 100)
    if result["failed_gates"]:
        for item in result["failed_gates"]:
            lines.append(str(item))
    else:
        lines.append("none")
    lines.append("")
    lines.append("FORBIDDEN ACTIONS")
    lines.append("-" * 100)
    for item in result["forbidden_actions"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("GIT STATE")
    lines.append("-" * 100)
    lines.append(json.dumps(result["git_state"], indent=2, ensure_ascii=False))

    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_TXT}")
    print(f"approval_status={result['approval_status']}")


def main() -> None:
    result = build_report()
    write_outputs(result)


if __name__ == "__main__":
    main()
