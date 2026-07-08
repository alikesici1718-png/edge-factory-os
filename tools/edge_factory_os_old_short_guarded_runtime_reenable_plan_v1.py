from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

OUT_DIR = REPO_ROOT / "edge_factory_os_old_short_guarded_runtime_reenable_plan"
OUT_DIR.mkdir(parents=True, exist_ok=True)

NOW_UTC = datetime.now(timezone.utc).isoformat()

APPROVAL_JSON = (
    REPO_ROOT
    / "edge_factory_os_old_short_manual_reactivation_approval"
    / "old_short_manual_reactivation_approval_latest.json"
)

REACTIVATION_GATE_JSON = (
    REPO_ROOT
    / "edge_factory_os_old_short_reactivation_gate"
    / "old_short_reactivation_gate_latest.json"
)

STATUS_JSONS = [
    LAB_ROOT / "edge_factory_os_runtime_family_status_panel_and_backup_hygiene" / "runtime_family_status_panel_and_backup_hygiene_latest.json",
    LAB_ROOT / "edge_factory_os_runtime_family_monitor_refresh_old_short_aware" / "runtime_family_monitor_refresh_old_short_aware_latest.json",
    LAB_ROOT / "edge_factory_os_runtime_family_monitor_evaluator_no_capital" / "runtime_family_monitor_evaluator_no_capital_latest.json",
    REPO_ROOT / "edge_factory_os_repo_only_standard_stack_refresh" / "repo_only_standard_stack_refresh_latest.json",
]

SCAN_ROOTS = [
    REPO_ROOT / "tools",
    REPO_ROOT / "edge_factory_os_framework",
    REPO_ROOT,
]

SCAN_SUFFIXES = {".py", ".json", ".txt", ".md", ".yaml", ".yml"}

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
    "active_paper_execution_allowed_now": False,
    "live_allowed": False,
    "real_orders_allowed": False,
    "file_delete_allowed": False,
    "file_move_allowed": False,
    "archive_allowed": False,
    "execution_allowed": False,
    "old_short_runtime_enable_allowed_now": False,
    "old_short_guarded_reenable_plan_allowed": True,
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


def safe_relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else {"_json": obj}
    except Exception:
        return None


def recursive_find(obj: Any, key: str) -> Any:
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for value in obj.values():
            found = recursive_find(value, key)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = recursive_find(item, key)
            if found is not None:
                return found
    return None


def first_found(payloads: List[Dict[str, Any]], key: str, fallback: Any = None) -> Any:
    for payload in payloads:
        found = recursive_find(payload, key)
        if found is not None:
            return found
    return fallback


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
            if ".bak" in x or "_bak_" in x or "blocked_patch_bak" in x or "readonly_fix_bak" in x
        ]),
        "universe_guard_review_required": any(
            "tools/edge_factory_os_universe_coverage_guard_v1.py" in x
            for x in lines
        ),
    }


def collect_status_payloads() -> Dict[str, Any]:
    approval = load_json(APPROVAL_JSON)
    gate = load_json(REACTIVATION_GATE_JSON)

    status_payloads = []
    status_inventory = []

    for path in STATUS_JSONS:
        data = load_json(path)
        if data is not None:
            status_payloads.append(data)
        status_inventory.append({
            "path": str(path),
            "found": data is not None,
        })

    all_payloads = []
    if approval is not None:
        all_payloads.append(approval)
    if gate is not None:
        all_payloads.append(gate)
    all_payloads.extend(status_payloads)

    return {
        "approval": approval,
        "gate": gate,
        "status_payloads": status_payloads,
        "all_payloads": all_payloads,
        "status_inventory": status_inventory,
    }


def read_text(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None


def classify_old_short_line(line: str) -> List[str]:
    low = line.lower()
    tags: List[str] = []

    if "old_short" in low:
        tags.append("OLD_SHORT")
    if any(x in low for x in ["enable", "enabled", "disable", "disabled", "active", "inactive"]):
        tags.append("ENABLE_DISABLE_ACTIVE")
    if any(x in low for x in ["runtime", "launcher", "supervisor", "autopilot", "paper"]):
        tags.append("RUNTIME_OR_PAPER")
    if any(x in low for x in ["capital", "allocation", "size", "sizing"]):
        tags.append("CAPITAL")
    if any(x in low for x in ["live", "real_order", "real orders", "order"]):
        tags.append("LIVE_OR_ORDER")
    if any(x in low for x in ["family", "registry", "monitor", "status"]):
        tags.append("FAMILY_STATUS")
    if any(x in low for x in ["block", "blocked", "allow", "allowed", "gate", "approval"]):
        tags.append("GATE_OR_POLICY")

    return tags


def scan_old_short_control_surface() -> Dict[str, Any]:
    seen: set[str] = set()
    candidates: List[Dict[str, Any]] = []

    for root in SCAN_ROOTS:
        if not root.exists():
            continue

        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in SCAN_SUFFIXES:
                continue

            rel = safe_relative(path)
            if rel in seen:
                continue
            seen.add(rel)

            text = read_text(path)
            if not text or "old_short" not in text.lower():
                continue

            hits = []
            score = 0

            for line_no, line in enumerate(text.splitlines(), start=1):
                if "old_short" not in line.lower():
                    continue

                tags = classify_old_short_line(line)
                if not tags:
                    continue

                line_score = 1
                if "ENABLE_DISABLE_ACTIVE" in tags:
                    line_score += 5
                if "RUNTIME_OR_PAPER" in tags:
                    line_score += 5
                if "FAMILY_STATUS" in tags:
                    line_score += 3
                if "GATE_OR_POLICY" in tags:
                    line_score += 2
                if "CAPITAL" in tags:
                    line_score += 1
                if "LIVE_OR_ORDER" in tags:
                    line_score += 1

                score += line_score
                hits.append({
                    "line": line_no,
                    "tags": tags,
                    "text": line.strip()[:300],
                    "line_score": line_score,
                })

            path_low = rel.lower()
            role = "REFERENCE_ONLY"

            if any(x in path_low for x in ["family_registry", "runtime_family", "status_panel", "monitor_refresh", "monitor_evaluator"]):
                role = "FAMILY_STATUS_OR_REGISTRY_SURFACE"
                score += 20
            elif any(x in path_low for x in ["autopilot", "supervisor", "launcher", "runtime", "paper", "command_center"]):
                role = "POSSIBLE_RUNTIME_CONTROL_SURFACE"
                score += 15
            elif any(x in path_low for x in ["approval", "reactivation", "gate", "policy"]):
                role = "GOVERNANCE_OR_APPROVAL_SURFACE"
                score += 10

            candidates.append({
                "path": rel,
                "role": role,
                "score": score,
                "hit_count": len(hits),
                "hits": hits[:25],
            })

    candidates.sort(key=lambda x: (-x["score"], x["path"]))

    return {
        "old_short_control_surface_file_count": len(candidates),
        "ranked_candidates": candidates[:80],
        "top_family_status_or_registry": [
            x for x in candidates
            if x["role"] == "FAMILY_STATUS_OR_REGISTRY_SURFACE"
        ][:20],
        "top_possible_runtime_control_surface": [
            x for x in candidates
            if x["role"] == "POSSIBLE_RUNTIME_CONTROL_SURFACE"
        ][:20],
        "top_governance_or_approval_surface": [
            x for x in candidates
            if x["role"] == "GOVERNANCE_OR_APPROVAL_SURFACE"
        ][:20],
    }


def gate_row(name: str, status: str, observed: Any, required: Any, evidence: str) -> Dict[str, Any]:
    return {
        "gate": name,
        "status": status,
        "observed": observed,
        "required": required,
        "evidence": evidence,
    }


def build_guarded_plan(
    approval: Dict[str, Any],
    reactivation_gate: Dict[str, Any],
    status_payloads: List[Dict[str, Any]],
    scan: Dict[str, Any],
) -> Dict[str, Any]:
    all_payloads = []
    if approval:
        all_payloads.append(approval)
    if reactivation_gate:
        all_payloads.append(reactivation_gate)
    all_payloads.extend(status_payloads)

    old_short_closed = int(first_found(all_payloads, "old_short_closed_trades", 20))
    old_short_threshold = int(first_found(all_payloads, "old_short_capital_review_threshold", 50))
    old_short_remaining = max(0, old_short_threshold - old_short_closed)

    old_short_status = {
        "old_short_final_decision": first_found(
            all_payloads,
            "old_short_final_decision",
            "OLD_SHORT_MONITORING_READY_CONTINUE_COLLECT_NO_CAPITAL",
        ),
        "old_short_closed_trades": old_short_closed,
        "old_short_capital_review_threshold": old_short_threshold,
        "old_short_next_required_closed_trades_for_capital_review": old_short_remaining,
        "old_short_monitoring_ready": bool(first_found(all_payloads, "old_short_monitoring_ready", True)),
        "old_short_capital_ready": bool(first_found(all_payloads, "old_short_capital_ready", False)),
        "old_short_capital_action_allowed": bool(first_found(all_payloads, "old_short_capital_action_allowed", False)),
    }

    manual_approval = approval.get("manual_approval", {}) if approval else {}

    approval_ready = (
        approval is not None
        and approval.get("approval_status") == "OLD_SHORT_MANUAL_REACTIVATION_APPROVAL_READY_FOR_GUARDED_PLAN"
        and manual_approval.get("manual_approval_valid") is True
        and manual_approval.get("capital_change_approved") is False
        and manual_approval.get("live_trading_approved") is False
        and manual_approval.get("real_orders_approved") is False
        and manual_approval.get("runtime_enable_approved_now") is False
    )

    runtime_candidates = scan["top_possible_runtime_control_surface"]
    family_candidates = scan["top_family_status_or_registry"]

    plan_steps = [
        {
            "step": 1,
            "name": "Confirm approval scope",
            "allowed_now": True,
            "action": "Use manual approval only for guarded monitoring/active-paper restoration planning.",
            "must_not_do": ["capital_change", "live_trading", "real_orders", "runtime_enable_in_this_step"],
        },
        {
            "step": 2,
            "name": "Identify control surface",
            "allowed_now": True,
            "action": "Inspect ranked old_short control-surface candidates from this report.",
            "primary_targets": [
                x["path"] for x in (family_candidates[:5] + runtime_candidates[:5])
            ],
            "must_not_do": ["modify_files", "run_launcher", "touch_runtime"],
        },
        {
            "step": 3,
            "name": "Build patch preview only",
            "allowed_now": False,
            "action": "Next module may create a patch-preview/diff for old_short monitoring/active-paper restoration, but must not apply it.",
            "required_next_module": "edge_factory_os_old_short_guarded_runtime_reenable_patch_preview_v1.py",
            "must_not_do": ["apply_patch", "start_process", "change_capital", "enable_live", "send_real_orders"],
        },
        {
            "step": 4,
            "name": "Runtime re-enable execution",
            "allowed_now": False,
            "action": "Only after patch preview, explicit execution approval, and final safety gate.",
            "required_before_execution": [
                "manual execution approval",
                "runtime process state check",
                "active-paper-only proof",
                "capital/live/real-order false proof",
                "rollback plan",
            ],
        },
    ]

    return {
        "approval_ready_for_plan": approval_ready,
        "old_short_status": old_short_status,
        "plan_steps": plan_steps,
        "restore_scope": {
            "restore_family": "old_short",
            "restore_mode": "MONITORING_OR_ACTIVE_PAPER_ONLY",
            "capital_change_allowed": False,
            "live_trading_allowed": False,
            "real_orders_allowed": False,
            "runtime_enable_allowed_now": False,
            "patch_apply_allowed_now": False,
        },
        "control_surface_summary": {
            "family_status_or_registry_candidate_count": len(family_candidates),
            "runtime_control_candidate_count": len(runtime_candidates),
            "top_family_status_or_registry_paths": [x["path"] for x in family_candidates[:10]],
            "top_possible_runtime_control_paths": [x["path"] for x in runtime_candidates[:10]],
        },
    }


def build_report() -> Dict[str, Any]:
    git_state = inspect_git()
    payloads = collect_status_payloads()
    approval = payloads["approval"]
    reactivation_gate = payloads["gate"]
    status_payloads = payloads["status_payloads"]
    scan = scan_old_short_control_surface()

    plan = build_guarded_plan(
        approval=approval or {},
        reactivation_gate=reactivation_gate or {},
        status_payloads=status_payloads,
        scan=scan,
    )

    approval_exists = approval is not None
    approval_status = approval.get("approval_status") if approval else None
    approval_ready_for_plan = plan["approval_ready_for_plan"]

    reactivation_gate_exists = reactivation_gate is not None
    reactivation_gate_status = reactivation_gate.get("gate_status") if reactivation_gate else None

    policy_gates = [
        gate_row(
            "REPO_ONLY_PLAN",
            "PASS",
            SAFETY_FLAGS["repo_only"],
            True,
            "This module only creates a guarded re-enable plan and writes report outputs.",
        ),
        gate_row(
            "MANUAL_APPROVAL_READY",
            "PASS" if approval_ready_for_plan else "FAIL",
            {
                "approval_exists": approval_exists,
                "approval_status": approval_status,
                "approval_ready_for_plan": approval_ready_for_plan,
            },
            {
                "approval_status": "OLD_SHORT_MANUAL_REACTIVATION_APPROVAL_READY_FOR_GUARDED_PLAN",
                "runtime_enable_approved_now": False,
                "capital_live_real_orders_approved": False,
            },
            "Manual approval must exist and must authorize planning only, not execution.",
        ),
        gate_row(
            "REACTIVATION_GATE_PRESENT",
            "PASS" if reactivation_gate_exists else "FAIL",
            {
                "reactivation_gate_exists": reactivation_gate_exists,
                "reactivation_gate_status": reactivation_gate_status,
            },
            {
                "reactivation_gate_required": True,
            },
            "The previous reactivation gate is required as prerequisite context.",
        ),
        gate_row(
            "NO_RUNTIME_OR_PATCH_EXECUTION",
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
            "No runtime enable, launcher, runtime patch, or execution command is performed.",
        ),
        gate_row(
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
            "old_short restoration planning cannot authorize capital, live trading, or real orders.",
        ),
        gate_row(
            "CONTROL_SURFACE_DISCOVERED",
            "PASS" if scan["old_short_control_surface_file_count"] > 0 else "FAIL",
            {
                "old_short_control_surface_file_count": scan["old_short_control_surface_file_count"],
                "runtime_control_candidate_count": plan["control_surface_summary"]["runtime_control_candidate_count"],
                "family_status_or_registry_candidate_count": plan["control_surface_summary"]["family_status_or_registry_candidate_count"],
            },
            {
                "old_short_control_surface_file_count_gt_zero": True,
            },
            "The repo contains old_short references sufficient to build a patch preview in a later module.",
        ),
    ]

    failed_gates = [x["gate"] for x in policy_gates if x["status"] == "FAIL"]

    plan_status = (
        "OLD_SHORT_GUARDED_RUNTIME_REENABLE_PLAN_READY_NO_EXECUTION"
        if not failed_gates
        else "OLD_SHORT_GUARDED_RUNTIME_REENABLE_PLAN_BLOCKED"
    )

    result = {
        "module": "edge_factory_os_old_short_guarded_runtime_reenable_plan_v1.py",
        "generated_at_utc": NOW_UTC,
        "repo_root": str(REPO_ROOT),
        "lab_root": str(LAB_ROOT),
        "plan_status": plan_status,
        "severity": "ATTENTION",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "final_decision": (
            "BUILD_PATCH_PREVIEW_ONLY_NEXT_DO_NOT_ENABLE_RUNTIME"
            if not failed_gates
            else "DO_NOT_CONTINUE_PLAN_BLOCKED"
        ),
        "reason": (
            "Manual approval allows planning only. This module identified the old_short control surface and produced a guarded "
            "monitoring/active-paper restoration plan, while keeping runtime enable, launcher, patch apply, capital, live, and real orders blocked."
        ),
        "safety_flags": SAFETY_FLAGS,
        "git_state": git_state,
        "input_artifacts": {
            "approval_json": {
                "path": str(APPROVAL_JSON),
                "found": approval_exists,
                "approval_status": approval_status,
            },
            "reactivation_gate_json": {
                "path": str(REACTIVATION_GATE_JSON),
                "found": reactivation_gate_exists,
                "gate_status": reactivation_gate_status,
            },
            "status_inventory": payloads["status_inventory"],
        },
        "guarded_reenable_plan": plan,
        "old_short_control_surface_scan": scan,
        "policy_gates": policy_gates,
        "failed_gates": failed_gates,
        "next_module": "edge_factory_os_old_short_guarded_runtime_reenable_patch_preview_v1.py",
        "next_action": "BUILD_PATCH_PREVIEW_ONLY_DO_NOT_APPLY_DO_NOT_TOUCH_RUNTIME",
        "next_step_rules": {
            "runtime_touch": False,
            "launcher": False,
            "runtime_patch_apply": False,
            "backup_delete": False,
            "backup_move": False,
            "gitignore_change": False,
            "strategy_research": False,
            "candidate_generation": False,
            "family_release": False,
            "capital_change": False,
            "active_paper_execution": False,
            "live": False,
            "real_orders": False,
        },
        "outputs": {
            "json": str(OUT_DIR / "old_short_guarded_runtime_reenable_plan_latest.json"),
            "txt": str(OUT_DIR / "old_short_guarded_runtime_reenable_plan_latest.txt"),
        },
    }

    return result


def write_outputs(result: Dict[str, Any]) -> None:
    json_path = OUT_DIR / "old_short_guarded_runtime_reenable_plan_latest.json"
    txt_path = OUT_DIR / "old_short_guarded_runtime_reenable_plan_latest.txt"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True)

    lines: List[str] = []
    lines.append("EDGE FACTORY OS OLD_SHORT GUARDED RUNTIME RE-ENABLE PLAN v1")
    lines.append("=" * 100)
    lines.append(f"plan_status: {result['plan_status']}")
    lines.append(f"severity: {result['severity']}")
    lines.append(f"allowed_scope: {result['allowed_scope']}")
    lines.append(f"final_decision: {result['final_decision']}")
    lines.append(f"next_action: {result['next_action']}")
    lines.append(f"next_module: {result['next_module']}")
    lines.append("")
    lines.append("OLD_SHORT STATUS")
    lines.append("-" * 100)
    for key, value in result["guarded_reenable_plan"]["old_short_status"].items():
        lines.append(f"{key}: {value}")
    lines.append("")
    lines.append("RESTORE SCOPE")
    lines.append("-" * 100)
    for key, value in result["guarded_reenable_plan"]["restore_scope"].items():
        lines.append(f"{key}: {value}")
    lines.append("")
    lines.append("CONTROL SURFACE SUMMARY")
    lines.append("-" * 100)
    for key, value in result["guarded_reenable_plan"]["control_surface_summary"].items():
        lines.append(f"{key}: {value}")
    lines.append("")
    lines.append("PLAN STEPS")
    lines.append("-" * 100)
    for step in result["guarded_reenable_plan"]["plan_steps"]:
        lines.append(f"step {step['step']}: {step['name']}")
        for key, value in step.items():
            if key not in {"step", "name"}:
                lines.append(f"  {key}: {value}")
    lines.append("")
    lines.append("TOP FAMILY STATUS / REGISTRY CANDIDATES")
    lines.append("-" * 100)
    for item in result["old_short_control_surface_scan"]["top_family_status_or_registry"][:12]:
        lines.append(f"path: {item['path']} | score={item['score']} | hit_count={item['hit_count']}")
        for hit in item["hits"][:6]:
            lines.append(f"  L{hit['line']} {hit['tags']}: {hit['text']}")
    lines.append("")
    lines.append("TOP POSSIBLE RUNTIME CONTROL CANDIDATES")
    lines.append("-" * 100)
    for item in result["old_short_control_surface_scan"]["top_possible_runtime_control_surface"][:12]:
        lines.append(f"path: {item['path']} | score={item['score']} | hit_count={item['hit_count']}")
        for hit in item["hits"][:6]:
            lines.append(f"  L{hit['line']} {hit['tags']}: {hit['text']}")
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
