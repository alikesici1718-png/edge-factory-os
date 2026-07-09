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
OUT_ROOT = WORKSPACE / "edge_factory_os_self_improvement_planner_v1"

STACK_PATH = WORKSPACE / "edge_factory_os_standard_stack_runner_v1" / "os_standard_stack_latest.json"
UNIFIED_PATH = WORKSPACE / "edge_factory_os_unified_state_reader_v1" / "os_unified_state_latest.json"
POLICY_PATH = WORKSPACE / "edge_factory_os_policy_engine_v1" / "os_policy_engine_latest.json"
DECISION_PATH = WORKSPACE / "edge_factory_os_autopilot_decision_adapter_v1" / "os_autopilot_decision_latest.json"
ROUTER_PATH = WORKSPACE / "edge_factory_os_execution_router_v1" / "os_execution_router_latest.json"
MEMORY_PATH = WORKSPACE / "edge_factory_os_memory_lesson_index_v1" / "os_memory_lesson_index_latest.json"

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

def exists_repo_tool(name: str) -> bool:
    return (REPO / "tools" / name).exists()

def add_task(
    tasks: list[dict],
    priority: int,
    task_key: str,
    status: str,
    allowed: bool,
    reason: str,
    output_module: str,
    blocked_by: str = "",
) -> None:
    tasks.append({
        "priority": priority,
        "task_key": task_key,
        "status": status,
        "allowed": bool(allowed),
        "reason": reason,
        "output_module": output_module,
        "blocked_by": blocked_by,
    })

def main() -> int:
    out_dir = OUT_ROOT / f"os_self_improvement_planner_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    stack = read_json(STACK_PATH)
    unified = read_json(UNIFIED_PATH)
    policy = read_json(POLICY_PATH)
    decision = read_json(DECISION_PATH)
    router = read_json(ROUTER_PATH)
    memory = read_json(MEMORY_PATH)

    git_status = run(["git", "status", "--short"], cwd=REPO)
    git_dirty = bool(git_status["stdout"].strip())

    stack_pass = stack.get("stack_status") == "STACK_PASS"
    unified_ok = unified.get("state_level") == "OK"
    policy_pass = policy.get("policy_status") == "POLICY_ENGINE_PASS"
    decision_ok = decision.get("final_status") == "DECISION_OK_REPO_ONLY"
    router_ready = router.get("router_status") == "EXECUTION_ROUTER_READY"

    runtime = unified.get("runtime", {})
    runtime_ok = runtime.get("runtime_ok") is True
    new_errors = runtime.get("new_errors_since_ack") is True
    closed = int(runtime.get("closed") or 0)
    drift_ready = runtime.get("drift_ready") is True
    capital_ready = runtime.get("capital_review_ready") is True

    repo_only_allowed = (
        stack_pass
        and unified_ok
        and policy_pass
        and decision_ok
        and router_ready
        and runtime_ok
        and not new_errors
        and not git_dirty
    )

    tasks: list[dict] = []

    add_task(
        tasks,
        1000,
        "protect_runtime",
        "ACTIVE_RULE",
        True,
        "Runtime is healthy; do not touch MASTER, do not restart, do not patch runtime.",
        "existing_runtime_protection",
    )

    add_task(
        tasks,
        950,
        "standard_stack_before_every_change",
        "ACTIVE_RULE",
        True,
        "Standard Stack Runner is the mandatory pre-work gate.",
        "edge_factory_os_standard_stack_runner_v1.py",
    )

    # Highest-value next OS capabilities.
    add_task(
        tasks,
        900,
        "build_repo_source_map",
        "READY" if repo_only_allowed else "BLOCKED",
        repo_only_allowed,
        "Create a repo source map: classify scripts by runtime/os/research/tools, detect duplicates, stale versions, and unsafe scripts.",
        "edge_factory_os_repo_source_map_v1.py",
        "" if repo_only_allowed else "standard_stack_not_clean_or_repo_dirty",
    )

    add_task(
        tasks,
        875,
        "build_artifact_freshness_index",
        "READY" if repo_only_allowed else "BLOCKED",
        repo_only_allowed,
        "Index latest output artifacts and detect stale/missing state files, so OS does not read old evidence.",
        "edge_factory_os_artifact_freshness_index_v1.py",
        "" if repo_only_allowed else "standard_stack_not_clean_or_repo_dirty",
    )

    add_task(
        tasks,
        850,
        "build_test_harness_manifest",
        "READY" if repo_only_allowed else "BLOCKED",
        repo_only_allowed,
        "Create a test harness manifest for py_compile/smoke tests without touching runtime.",
        "edge_factory_os_test_harness_manifest_v1.py",
        "" if repo_only_allowed else "standard_stack_not_clean_or_repo_dirty",
    )

    add_task(
        tasks,
        825,
        "build_module_dependency_graph",
        "READY" if repo_only_allowed else "BLOCKED",
        repo_only_allowed,
        "Map which tools depend on which latest JSON/state files; reduce hidden coupling.",
        "edge_factory_os_dependency_graph_v1.py",
        "" if repo_only_allowed else "standard_stack_not_clean_or_repo_dirty",
    )

    add_task(
        tasks,
        800,
        "build_runtime_apply_gate",
        "WAIT",
        False,
        "Later: gate that decides whether a repo change is allowed to be applied to runtime. Not needed while runtime is healthy and no runtime patch is planned.",
        "edge_factory_os_runtime_apply_gate_v1.py",
        "no_runtime_patch_allowed_currently",
    )

    add_task(
        tasks,
        775,
        "build_candidate_generation_guard",
        "WAIT",
        False,
        "Later: prevent new candidate generation that violates memory blocks/family cooldowns. Not urgent while strategy work is paused.",
        "edge_factory_os_candidate_generation_guard_v1.py",
        "strategy_research_paused",
    )

    add_task(
        tasks,
        750,
        "defer_drift_review",
        "BLOCKED" if not drift_ready else "READY_READ_ONLY",
        drift_ready,
        f"closed={closed}/20",
        "existing_drift_review",
        "closed_below_20" if not drift_ready else "",
    )

    add_task(
        tasks,
        725,
        "defer_capital_review",
        "BLOCKED" if not capital_ready else "READY_READ_ONLY",
        capital_ready,
        f"closed={closed}/50",
        "existing_capital_review",
        "closed_below_50" if not capital_ready else "",
    )

    sorted_tasks = sorted(tasks, key=lambda x: x["priority"], reverse=True)

    ready_tasks = [t for t in sorted_tasks if t["allowed"] and t["status"] == "READY"]

    if not stack_pass:
        planner_status = "SELF_IMPROVEMENT_BLOCKED_STACK_NOT_PASS"
        next_task = "FIX_STANDARD_STACK"
        next_module = ""
    elif git_dirty:
        planner_status = "SELF_IMPROVEMENT_BLOCKED_REPO_DIRTY"
        next_task = "COMMIT_OR_REVIEW_REPO_CHANGES"
        next_module = ""
    elif not runtime_ok or new_errors:
        planner_status = "SELF_IMPROVEMENT_BLOCKED_RUNTIME_OR_ERRORS"
        next_task = "RUN_RUNTIME_OR_ERROR_REVIEW"
        next_module = ""
    elif ready_tasks:
        planner_status = "SELF_IMPROVEMENT_READY"
        next_task = ready_tasks[0]["task_key"]
        next_module = ready_tasks[0]["output_module"]
    else:
        planner_status = "SELF_IMPROVEMENT_WAIT"
        next_task = "KEEP_RUNNING_COLLECT_SAMPLE"
        next_module = ""

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),
        "planner_status": planner_status,
        "next_task": next_task,
        "next_module": next_module,
        "repo_only_allowed": repo_only_allowed,
        "stack_pass": stack_pass,
        "unified_ok": unified_ok,
        "policy_pass": policy_pass,
        "decision_ok": decision_ok,
        "router_ready": router_ready,
        "runtime_ok": runtime_ok,
        "new_errors_since_ack": new_errors,
        "git_dirty": git_dirty,
        "closed": closed,
        "drift_ready": drift_ready,
        "capital_review_ready": capital_ready,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "runtime_touch_allowed": False,
        "execution_performed": False,
        "tasks": sorted_tasks,
        "source_paths": {
            "stack": str(STACK_PATH),
            "unified": str(UNIFIED_PATH),
            "policy": str(POLICY_PATH),
            "decision": str(DECISION_PATH),
            "router": str(ROUTER_PATH),
            "memory": str(MEMORY_PATH),
        },
    }

    state_path = out_dir / "os_self_improvement_planner_v1_state.json"
    latest_path = OUT_ROOT / "os_self_improvement_planner_latest.json"
    tasks_csv = out_dir / "os_self_improvement_planner_v1_tasks.csv"
    report_path = out_dir / "os_self_improvement_planner_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    with tasks_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["priority", "task_key", "status", "allowed", "reason", "output_module", "blocked_by"],
        )
        writer.writeheader()
        writer.writerows(sorted_tasks)

    md = []
    md.append("# Edge Factory OS Self-Improvement Planner v1")
    md.append("")
    md.append(f"planner_status: `{planner_status}`")
    md.append(f"next_task: `{next_task}`")
    md.append(f"next_module: `{next_module}`")
    md.append("")
    md.append("## State")
    md.append(f"- repo_only_allowed: `{repo_only_allowed}`")
    md.append(f"- stack_pass: `{stack_pass}`")
    md.append(f"- runtime_ok: `{runtime_ok}`")
    md.append(f"- git_dirty: `{git_dirty}`")
    md.append(f"- closed: `{closed}`")
    md.append("")
    md.append("## Top tasks")
    for t in sorted_tasks[:8]:
        md.append(f"- `{t['priority']}` `{t['task_key']}` `{t['status']}` allowed=`{t['allowed']}`")
    md.append("")
    md.append("## Safety")
    md.append("- runtime_touch_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS SELF-IMPROVEMENT PLANNER v1")
    print("=" * 100)
    print(f"planner_status: {planner_status}")
    print(f"next_task     : {next_task}")
    print(f"next_module   : {next_module}")
    print(f"repo_only_allowed={repo_only_allowed}")
    print(f"stack_pass={stack_pass} unified_ok={unified_ok} policy_pass={policy_pass} decision_ok={decision_ok} router_ready={router_ready}")
    print(f"runtime_ok={runtime_ok} new_errors_since_ack={new_errors} git_dirty={git_dirty}")
    print(f"closed={closed} drift_ready={drift_ready} capital_review_ready={capital_ready}")
    print("runtime_touch_allowed: False")
    print("active_paper_allowed : False")
    print("live_allowed         : False")
    print("capital_change_allowed: False")
    print("execution_performed  : False")
    print()
    print("TASKS")
    print("-" * 100)
    for t in sorted_tasks:
        print(f"{t['priority']} | {t['task_key']} | {t['status']} | allowed={t['allowed']} | {t['output_module']}")
    print()
    print(f"State : {state_path}")
    print(f"Latest: {latest_path}")
    print(f"Tasks : {tasks_csv}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
