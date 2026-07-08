from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

OUT_DIR = REPO_ROOT / "edge_factory_os_old_short_manual_reactivation_approval"
OUT_DIR.mkdir(parents=True, exist_ok=True)

NOW_UTC = datetime.now(timezone.utc).isoformat()

APPROVAL_TEXT = (
    "I explicitly approve repo-only preparation for old_short reactivation gate. "
    "Do not enable live trading, real orders, or capital changes. "
    "Only prepare a separate guarded runtime re-enable plan for old_short monitoring/active-paper restoration."
)

PREVIOUS_GATE_JSON = (
    REPO_ROOT
    / "edge_factory_os_old_short_reactivation_gate"
    / "old_short_reactivation_gate_latest.json"
)

SAFETY_FLAGS = {
    "repo_only": True,
    "runtime_touch_allowed": False,
    "launcher_allowed": False,
    "runtime_patch_allowed": False,
    "backup_delete_allowed": False,
    "backup_move_allowed": False,
    "gitignore_change_allowed": False,
    "strategy_research_allowed": False,
    "candidate_generation_allowed": False,
    "candidate_contract_allowed": False,
    "family_release_allowed": False,
    "promotion_allowed": False,
    "capital_change_allowed": False,
    "active_paper_allowed": False,
    "live_allowed": False,
    "real_orders_allowed": False,
    "file_delete_allowed": False,
    "file_move_allowed": False,
    "archive_allowed": False,
    "execution_allowed": False,
    "old_short_reactivation_approval_record_allowed": True,
    "old_short_runtime_enable_allowed_now": False,
}


def run_cmd(args: List[str], timeout: int = 20) -> Dict[str, Any]:
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


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else {"_json": obj}
    except Exception:
        return None


def gate(name: str, status: str, observed: Any, required: Any, evidence: str) -> Dict[str, Any]:
    return {
        "gate": name,
        "status": status,
        "observed": observed,
        "required": required,
        "evidence": evidence,
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
    }


def build_report() -> Dict[str, Any]:
    previous_gate = load_json(PREVIOUS_GATE_JSON)
    git_state = inspect_git()

    previous_gate_found = previous_gate is not None
    previous_gate_status = previous_gate.get("gate_status") if previous_gate else None
    previous_final_decision = previous_gate.get("final_decision") if previous_gate else None
    previous_old_short_can_be_reopened_now = previous_gate.get("old_short_can_be_reopened_now") if previous_gate else None
    previous_old_short_status = previous_gate.get("old_short_status", {}) if previous_gate else {}

    approval_present = True
    approval_valid = True
    approval_scope = "OLD_SHORT_MONITORING_ACTIVE_PAPER_RESTORATION_PLAN_ONLY"

    policy_gates = [
        gate(
            "REPO_ONLY_APPROVAL_RECORD",
            "PASS",
            SAFETY_FLAGS["repo_only"],
            True,
            "This module only records explicit manual approval for planning; it does not touch runtime.",
        ),
        gate(
            "PREVIOUS_REACTIVATION_GATE_FOUND",
            "PASS" if previous_gate_found else "FAIL",
            previous_gate_found,
            True,
            "The old_short reactivation gate output must exist before approval is accepted.",
        ),
        gate(
            "PREVIOUS_GATE_BLOCKED_AS_EXPECTED",
            "PASS" if previous_gate_status == "OLD_SHORT_REACTIVATION_GATE_BLOCKED_MANUAL_APPROVAL_REQUIRED" else "FAIL",
            previous_gate_status,
            "OLD_SHORT_REACTIVATION_GATE_BLOCKED_MANUAL_APPROVAL_REQUIRED",
            "Approval is only valid after the gate blocked due missing manual approval.",
        ),
        gate(
            "MANUAL_APPROVAL_TEXT_PRESENT",
            "PASS" if approval_present and approval_valid else "FAIL",
            {
                "approval_present": approval_present,
                "approval_valid": approval_valid,
                "approval_text": APPROVAL_TEXT,
            },
            {
                "approval_present": True,
                "approval_valid": True,
            },
            "Explicit approval is recorded for guarded old_short restoration planning only.",
        ),
        gate(
            "NO_RUNTIME_OR_EXECUTION_ACTION",
            "BLOCKED_AS_REQUIRED",
            {
                "runtime_touch_allowed": SAFETY_FLAGS["runtime_touch_allowed"],
                "launcher_allowed": SAFETY_FLAGS["launcher_allowed"],
                "runtime_patch_allowed": SAFETY_FLAGS["runtime_patch_allowed"],
                "execution_allowed": SAFETY_FLAGS["execution_allowed"],
                "old_short_runtime_enable_allowed_now": SAFETY_FLAGS["old_short_runtime_enable_allowed_now"],
            },
            {
                "runtime_touch_allowed": False,
                "launcher_allowed": False,
                "runtime_patch_allowed": False,
                "execution_allowed": False,
                "old_short_runtime_enable_allowed_now": False,
            },
            "This step does not reopen old_short and does not run any runtime command.",
        ),
        gate(
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
            "Approval does not authorize capital change, live trading, or real orders.",
        ),
    ]

    failed_gates = [x["gate"] for x in policy_gates if x["status"] == "FAIL"]

    approval_status = (
        "OLD_SHORT_MANUAL_REACTIVATION_APPROVAL_READY_FOR_GUARDED_PLAN"
        if not failed_gates
        else "OLD_SHORT_MANUAL_REACTIVATION_APPROVAL_FAILED"
    )

    result = {
        "module": "edge_factory_os_old_short_manual_reactivation_approval_v1.py",
        "generated_at_utc": NOW_UTC,
        "repo_root": str(REPO_ROOT),
        "lab_root": str(LAB_ROOT),
        "approval_status": approval_status,
        "severity": "ATTENTION",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": (
            "MANUAL_APPROVAL_RECORDED_BUILD_GUARDED_OLD_SHORT_RUNTIME_REENABLE_PLAN_NEXT"
            if not failed_gates
            else "DO_NOT_CONTINUE_APPROVAL_FAILED"
        ),
        "reason": (
            "Manual approval is recorded only for preparing a guarded old_short monitoring/active-paper restoration plan. "
            "This module does not enable old_short, does not touch runtime, does not launch anything, and does not authorize capital/live/real orders."
        ),
        "manual_approval": {
            "manual_approval_present": approval_present,
            "manual_approval_valid": approval_valid,
            "approval_text": APPROVAL_TEXT,
            "approval_scope": approval_scope,
            "capital_change_approved": False,
            "live_trading_approved": False,
            "real_orders_approved": False,
            "runtime_enable_approved_now": False,
        },
        "previous_gate": {
            "path": str(PREVIOUS_GATE_JSON),
            "found": previous_gate_found,
            "gate_status": previous_gate_status,
            "final_decision": previous_final_decision,
            "old_short_can_be_reopened_now": previous_old_short_can_be_reopened_now,
            "old_short_status": previous_old_short_status,
        },
        "safety_flags": SAFETY_FLAGS,
        "policy_gates": policy_gates,
        "failed_gates": failed_gates,
        "git_state": git_state,
        "next_module": "edge_factory_os_old_short_guarded_runtime_reenable_plan_v1.py",
        "next_action": "BUILD_GUARDED_RUNTIME_REENABLE_PLAN_NO_RUNTIME_EXECUTION_YET",
        "next_step_rules": {
            "runtime_touch": False,
            "launcher": False,
            "runtime_patch": False,
            "backup_delete": False,
            "backup_move": False,
            "gitignore_change": False,
            "strategy_research": False,
            "candidate_generation": False,
            "family_release": False,
            "capital_change": False,
            "active_paper_enable_execution": False,
            "live": False,
            "real_orders": False,
        },
        "outputs": {
            "json": str(OUT_DIR / "old_short_manual_reactivation_approval_latest.json"),
            "txt": str(OUT_DIR / "old_short_manual_reactivation_approval_latest.txt"),
        },
    }

    return result


def write_outputs(result: Dict[str, Any]) -> None:
    json_path = OUT_DIR / "old_short_manual_reactivation_approval_latest.json"
    txt_path = OUT_DIR / "old_short_manual_reactivation_approval_latest.txt"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True)

    lines = []
    lines.append("EDGE FACTORY OS OLD_SHORT MANUAL REACTIVATION APPROVAL v1")
    lines.append("=" * 100)
    lines.append(f"approval_status: {result['approval_status']}")
    lines.append(f"severity: {result['severity']}")
    lines.append(f"allowed_scope: {result['allowed_scope']}")
    lines.append(f"final_decision: {result['final_decision']}")
    lines.append(f"next_action: {result['next_action']}")
    lines.append(f"next_module: {result['next_module']}")
    lines.append("")
    lines.append("MANUAL APPROVAL")
    lines.append("-" * 100)
    for key, value in result["manual_approval"].items():
        lines.append(f"{key}: {value}")
    lines.append("")
    lines.append("PREVIOUS GATE")
    lines.append("-" * 100)
    for key, value in result["previous_gate"].items():
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

    text = "\n".join(lines) + "\n"

    with txt_path.open("w", encoding="utf-8") as f:
        f.write(text)

    print(text)


def main() -> None:
    result = build_report()
    write_outputs(result)


if __name__ == "__main__":
    main()
