#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO = WORKSPACE / "edge_factory_os_repo"
OUT_ROOT = WORKSPACE / "edge_factory_os_execution_router_v1"

DECISION_PATH = WORKSPACE / "edge_factory_os_autopilot_decision_adapter_v1" / "os_autopilot_decision_latest.json"
UNIFIED_PATH = WORKSPACE / "edge_factory_os_unified_state_reader_v1" / "os_unified_state_latest.json"
POLICY_PATH = WORKSPACE / "edge_factory_os_policy_engine_v1" / "os_policy_engine_latest.json"
PLANNER_PATH = WORKSPACE / "edge_factory_os_next_action_planner_v1" / "os_next_action_planner_latest.json"

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e), "__path__": str(path)}

def run(cmd: list[str], cwd: Path | None = None, timeout: int = 40) -> dict:
    try:
        p = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "ok": p.returncode == 0,
            "returncode": p.returncode,
            "stdout": p.stdout,
            "stderr": p.stderr,
        }
    except Exception as e:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": repr(e),
        }

def route_for_decision(final_decision: str) -> dict:
    routes = {
        "DO_NOT_TOUCH_RUNTIME_CONTINUE_REPO_ONLY_OS_INTELLIGENCE": {
            "route_key": "repo_only_os_intelligence",
            "route_status": "ROUTE_READY_REPO_ONLY",
            "execution_mode": "READ_ONLY_OR_REPO_ONLY",
            "runtime_touch_allowed": False,
            "launcher_allowed": False,
            "patch_runtime_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "capital_change_allowed": False,
            "allowed_commands": [
                r'python -u ".\tools\edge_factory_runtime_regression_guard_v1.py"',
                r'python -u ".\tools\edge_factory_os_unified_state_reader_v1.py"',
                r'python -u ".\tools\edge_factory_os_policy_engine_v1.py"',
                r'python -u ".\tools\edge_factory_os_next_action_planner_v1.py"',
                r'python -u ".\tools\edge_factory_os_autopilot_decision_adapter_v1.py"',
            ],
            "blocked_commands": [
                r'powershell -ExecutionPolicy Bypass -File "C:\Users\alike\start_edge_factory_MASTER_UPPER_SYSTEM_v5_supervised.ps1"',
                "any runtime patch command",
                "any new active paper family launcher",
                "any live order command",
            ],
            "reason": "Runtime is healthy and sample is immature; continue repo-only OS intelligence work.",
        },
        "COMMIT_OR_REVIEW_REPO_CHANGES_BEFORE_NEXT_STEP": {
            "route_key": "repo_cleanup",
            "route_status": "ROUTE_REPO_ATTENTION",
            "execution_mode": "GIT_REVIEW_ONLY",
            "runtime_touch_allowed": False,
            "launcher_allowed": False,
            "patch_runtime_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "capital_change_allowed": False,
            "allowed_commands": [
                "git status --short",
                "git diff --stat",
                "git add <reviewed-files>",
                'git commit -m "<message>"',
                "git push",
            ],
            "blocked_commands": [
                "runtime patch",
                "launcher restart",
                "new candidate execution",
            ],
            "reason": "Repo has uncommitted changes; review/commit before stacking more work.",
        },
        "RUN_ERROR_REVIEW": {
            "route_key": "error_review",
            "route_status": "ROUTE_READY_READ_ONLY_ERROR_REVIEW",
            "execution_mode": "READ_ONLY_ERROR_CLASSIFICATION",
            "runtime_touch_allowed": False,
            "launcher_allowed": False,
            "patch_runtime_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "capital_change_allowed": False,
            "allowed_commands": [
                r'python -u "C:\Users\alike\edge_factory_error_classifier_v1.py"',
                r'python -u "C:\Users\alike\edge_factory_error_acknowledger_v1.py"',
                r'python -u "C:\Users\alike\edge_factory_os_command_center_v2_overlay.py"',
            ],
            "blocked_commands": [
                "delete errors.csv",
                "ignore new errors",
                "runtime patch before classification",
            ],
            "reason": "New or unacknowledged errors require classification first.",
        },
        "RUN_DRIFT_REVIEW": {
            "route_key": "drift_review",
            "route_status": "ROUTE_READY_READ_ONLY_DRIFT_REVIEW",
            "execution_mode": "READ_ONLY_VALIDATION",
            "runtime_touch_allowed": False,
            "launcher_allowed": False,
            "patch_runtime_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "capital_change_allowed": False,
            "allowed_commands": [
                r'python -u "C:\Users\alike\edge_factory_active_family_drift_monitor_planner_v1.py"',
            ],
            "blocked_commands": [
                "automatic family disable",
                "automatic family promotion",
                "capital change",
                "live/paper escalation",
            ],
            "reason": "Closed sample reached drift threshold; read-only drift review allowed.",
        },
        "RUN_CAPITAL_REVIEW_READ_ONLY": {
            "route_key": "capital_review_read_only",
            "route_status": "ROUTE_READY_READ_ONLY_CAPITAL_REVIEW",
            "execution_mode": "READ_ONLY_CAPITAL_REVIEW",
            "runtime_touch_allowed": False,
            "launcher_allowed": False,
            "patch_runtime_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "capital_change_allowed": False,
            "allowed_commands": [
                r'python -u "C:\Users\alike\edge_factory_active_capital_governor_review_v2.py"',
            ],
            "blocked_commands": [
                "automatic sizing contract edit",
                "capital allocation change",
                "live/paper escalation",
            ],
            "reason": "Closed sample reached capital review threshold; read-only review only.",
        },
        "STOP_AND_INSPECT_RUNTIME": {
            "route_key": "runtime_inspection",
            "route_status": "ROUTE_RUNTIME_ATTENTION",
            "execution_mode": "READ_ONLY_DIAGNOSTICS",
            "runtime_touch_allowed": False,
            "launcher_allowed": False,
            "patch_runtime_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "capital_change_allowed": False,
            "allowed_commands": [
                r'python -u "C:\Users\alike\edge_factory_os_command_center_v2_overlay.py"',
                r'python -u "C:\Users\alike\edge_factory_os_process_watchdog_v1.py"',
                r'python "C:\Users\alike\edge_factory_live_health_check_v5.py" --base_dir "C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_MASTER_UPPER_SYSTEM"',
            ],
            "blocked_commands": [
                "blind restart",
                "duplicate launcher",
                "runtime patch before diagnosis",
            ],
            "reason": "Runtime is not clean; inspect before any action.",
        },
    }

    return routes.get(final_decision, {
        "route_key": "unknown_decision",
        "route_status": "ROUTE_BLOCKED_UNKNOWN_DECISION",
        "execution_mode": "NONE",
        "runtime_touch_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "allowed_commands": [],
        "blocked_commands": [
            "all runtime actions",
            "all launchers",
            "all patching",
            "all research execution",
        ],
        "reason": f"Unknown final_decision={final_decision}; block by default.",
    })

def main() -> int:
    out_dir = OUT_ROOT / f"os_execution_router_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    decision = read_json(DECISION_PATH)
    unified = read_json(UNIFIED_PATH)
    policy = read_json(POLICY_PATH)
    planner = read_json(PLANNER_PATH)

    final_decision = decision.get("final_decision", "UNKNOWN")
    final_status = decision.get("final_status", "UNKNOWN")
    allowed_scope = decision.get("allowed_scope", "UNKNOWN")

    route = route_for_decision(final_decision)

    git_status = run(["git", "status", "--short"], cwd=REPO)
    git_dirty = bool(git_status["stdout"].strip())

    # Router itself should never execute the route command.
    execution_performed = False

    hard_safety_ok = (
        route.get("runtime_touch_allowed") is False
        and route.get("launcher_allowed") is False
        and route.get("patch_runtime_allowed") is False
        and route.get("active_paper_allowed") is False
        and route.get("live_allowed") is False
        and route.get("capital_change_allowed") is False
    )

    if not hard_safety_ok:
        router_status = "EXECUTION_ROUTER_SAFETY_FAIL"
        recommended_action = "STOP_AND_REVIEW_ROUTER_SAFETY"
    elif route["route_status"].startswith("ROUTE_BLOCKED"):
        router_status = "EXECUTION_ROUTER_BLOCKED"
        recommended_action = "DO_NOT_EXECUTE_UNKNOWN_ROUTE"
    elif git_dirty and final_decision != "COMMIT_OR_REVIEW_REPO_CHANGES_BEFORE_NEXT_STEP":
        router_status = "EXECUTION_ROUTER_REPO_ATTENTION"
        recommended_action = "REVIEW_OR_COMMIT_REPO_CHANGES"
    else:
        router_status = "EXECUTION_ROUTER_READY"
        recommended_action = "FOLLOW_ROUTE_WITHOUT_TOUCHING_RUNTIME"

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),
        "router_status": router_status,
        "recommended_action": recommended_action,
        "execution_performed": execution_performed,
        "final_decision": final_decision,
        "final_status": final_status,
        "allowed_scope_from_decision": allowed_scope,
        "route": route,
        "git_dirty": git_dirty,
        "git_status_short": git_status["stdout"].strip(),
        "runtime_ok": unified.get("runtime", {}).get("runtime_ok"),
        "process_ok": unified.get("runtime", {}).get("process_watchdog_pass"),
        "health_ok": unified.get("runtime", {}).get("health_ok"),
        "policy_status": policy.get("policy_status"),
        "planner_decision": planner.get("decision"),
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "real_orders_allowed": False,
        "source_paths": {
            "decision": str(DECISION_PATH),
            "unified": str(UNIFIED_PATH),
            "policy": str(POLICY_PATH),
            "planner": str(PLANNER_PATH),
        },
    }

    state_path = out_dir / "os_execution_router_v1_state.json"
    latest_path = OUT_ROOT / "os_execution_router_latest.json"
    commands_csv = out_dir / "os_execution_router_v1_commands.csv"
    report_path = out_dir / "os_execution_router_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    with commands_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["kind", "command"])
        writer.writeheader()
        for c in route.get("allowed_commands", []):
            writer.writerow({"kind": "allowed", "command": c})
        for c in route.get("blocked_commands", []):
            writer.writerow({"kind": "blocked", "command": c})

    md = []
    md.append("# Edge Factory OS Execution Router v1")
    md.append("")
    md.append(f"router_status: `{router_status}`")
    md.append(f"final_decision: `{final_decision}`")
    md.append(f"route_key: `{route.get('route_key')}`")
    md.append(f"execution_mode: `{route.get('execution_mode')}`")
    md.append("")
    md.append("## Allowed commands")
    for c in route.get("allowed_commands", []):
        md.append(f"- `{c}`")
    md.append("")
    md.append("## Blocked commands")
    for c in route.get("blocked_commands", []):
        md.append(f"- `{c}`")
    md.append("")
    md.append("## Safety")
    md.append("- execution_performed: `False`")
    md.append("- runtime_touch_allowed: `False`")
    md.append("- launcher_allowed: `False`")
    md.append("- patch_runtime_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS EXECUTION ROUTER v1")
    print("=" * 100)
    print(f"router_status     : {router_status}")
    print(f"recommended_action: {recommended_action}")
    print(f"final_status      : {final_status}")
    print(f"final_decision    : {final_decision}")
    print(f"route_key         : {route.get('route_key')}")
    print(f"route_status      : {route.get('route_status')}")
    print(f"execution_mode    : {route.get('execution_mode')}")
    print(f"execution_performed: {execution_performed}")
    print(f"git_dirty         : {git_dirty}")
    print("runtime_touch_allowed: False")
    print("launcher_allowed     : False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed : False")
    print("live_allowed         : False")
    print("capital_change_allowed: False")
    print()
    print("ALLOWED COMMANDS")
    print("-" * 100)
    allowed = route.get("allowed_commands", [])
    print("\n".join(f"- {c}" for c in allowed) if allowed else "NONE")
    print()
    print("BLOCKED COMMANDS")
    print("-" * 100)
    blocked = route.get("blocked_commands", [])
    print("\n".join(f"- {c}" for c in blocked) if blocked else "NONE")
    print()
    print(f"State   : {state_path}")
    print(f"Latest  : {latest_path}")
    print(f"Commands: {commands_csv}")
    print(f"Report  : {report_path}")

if __name__ == "__main__":
    main()
