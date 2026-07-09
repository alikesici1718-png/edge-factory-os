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
OUT_ROOT = WORKSPACE / "edge_factory_os_self_improvement_planner_v2"

STACK_PATH = WORKSPACE / "edge_factory_os_standard_stack_runner_v1" / "os_standard_stack_latest.json"
UNIFIED_PATH = WORKSPACE / "edge_factory_os_unified_state_reader_v1" / "os_unified_state_latest.json"
POLICY_PATH = WORKSPACE / "edge_factory_os_policy_engine_v1" / "os_policy_engine_latest.json"
DECISION_PATH = WORKSPACE / "edge_factory_os_autopilot_decision_adapter_v1" / "os_autopilot_decision_latest.json"
ROUTER_PATH = WORKSPACE / "edge_factory_os_execution_router_v1" / "os_execution_router_latest.json"

SOURCE_MAP_PATH = WORKSPACE / "edge_factory_os_repo_source_map_v1" / "os_repo_source_map_latest.json"
ARTIFACT_FRESHNESS_PATH = WORKSPACE / "edge_factory_os_artifact_freshness_index_v1" / "os_artifact_freshness_index_latest.json"
TEST_HARNESS_PATH = WORKSPACE / "edge_factory_os_test_harness_manifest_v1" / "os_test_harness_manifest_latest.json"
DEPENDENCY_GRAPH_PATH = WORKSPACE / "edge_factory_os_dependency_graph_v1" / "os_dependency_graph_latest.json"
RUNTIME_APPLY_GATE_PATH = WORKSPACE / "edge_factory_os_runtime_apply_gate_v1" / "os_runtime_apply_gate_latest.json"
CANDIDATE_GENERATION_GUARD_PATH = WORKSPACE / "edge_factory_os_candidate_generation_guard_v1" / "os_candidate_generation_guard_latest.json"

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

def module_done(path: Path, expected_key: str, expected_value: str) -> tuple[bool, str]:
    data = read_json(path)
    if not data:
        return False, "missing_latest_json"
    actual = data.get(expected_key)
    if actual == expected_value:
        return True, f"{expected_key}={actual}"
    return False, f"{expected_key}={actual}, expected={expected_value}"

def add_task(
    tasks: list[dict],
    priority: int,
    task_key: str,
    module_name: str,
    done: bool,
    allowed: bool,
    reason: str,
    blocked_by: str = "",
) -> None:
    if done:
        status = "DONE"
        final_allowed = False
    elif allowed:
        status = "READY"
        final_allowed = True
    else:
        status = "BLOCKED"
        final_allowed = False

    tasks.append({
        "priority": priority,
        "task_key": task_key,
        "module_name": module_name,
        "status": status,
        "done": bool(done),
        "allowed": bool(final_allowed),
        "reason": reason,
        "blocked_by": blocked_by,
    })

def main() -> int:
    out_dir = OUT_ROOT / f"os_self_improvement_planner_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    stack = read_json(STACK_PATH)
    unified = read_json(UNIFIED_PATH)
    policy = read_json(POLICY_PATH)
    decision = read_json(DECISION_PATH)
    router = read_json(ROUTER_PATH)

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

    source_map_done, source_map_evidence = module_done(
        SOURCE_MAP_PATH,
        "map_status",
        "REPO_SOURCE_MAP_READY",
    )
    artifact_freshness_done, artifact_freshness_evidence = module_done(
        ARTIFACT_FRESHNESS_PATH,
        "freshness_status",
        "ARTIFACT_FRESHNESS_INDEX_READY",
    )
    test_harness_done, test_harness_evidence = module_done(
        TEST_HARNESS_PATH,
        "test_harness_status",
        "TEST_HARNESS_MANIFEST_READY",
    )
    dependency_graph_done, dependency_graph_evidence = module_done(
        DEPENDENCY_GRAPH_PATH,
        "dependency_graph_status",
        "DEPENDENCY_GRAPH_READY",
    )
    runtime_apply_gate_done, runtime_apply_gate_evidence = module_done(
        RUNTIME_APPLY_GATE_PATH,
        "runtime_apply_gate_status",
        "RUNTIME_APPLY_GATE_READY",
    )
    candidate_generation_guard_done, candidate_generation_guard_evidence = module_done(
        CANDIDATE_GENERATION_GUARD_PATH,
        "candidate_generation_guard_status",
        "CANDIDATE_GENERATION_GUARD_READY",
    )

    tasks: list[dict] = []

    tasks.append({
        "priority": 1000,
        "task_key": "protect_runtime",
        "module_name": "existing_runtime_protection",
        "status": "ACTIVE_RULE",
        "done": True,
        "allowed": True,
        "reason": "Runtime is healthy; do not touch MASTER, do not restart, do not patch runtime.",
        "blocked_by": "",
    })

    tasks.append({
        "priority": 950,
        "task_key": "standard_stack_before_every_change",
        "module_name": "edge_factory_os_standard_stack_runner_v1.py",
        "status": "ACTIVE_RULE",
        "done": True,
        "allowed": True,
        "reason": "Standard Stack Runner is mandatory pre-work gate.",
        "blocked_by": "",
    })

    add_task(
        tasks,
        900,
        "build_repo_source_map",
        "edge_factory_os_repo_source_map_v1.py",
        source_map_done,
        repo_only_allowed,
        f"Source map completion evidence: {source_map_evidence}",
        "" if repo_only_allowed else "standard_stack_not_clean_or_repo_dirty",
    )

    add_task(
        tasks,
        875,
        "build_artifact_freshness_index",
        "edge_factory_os_artifact_freshness_index_v1.py",
        artifact_freshness_done,
        repo_only_allowed and source_map_done,
        f"Artifact freshness completion evidence: {artifact_freshness_evidence}",
        "" if repo_only_allowed and source_map_done else "source_map_required_or_repo_not_clean",
    )

    add_task(
        tasks,
        850,
        "build_test_harness_manifest",
        "edge_factory_os_test_harness_manifest_v1.py",
        test_harness_done,
        repo_only_allowed and source_map_done and artifact_freshness_done,
        f"Test harness completion evidence: {test_harness_evidence}",
        "" if repo_only_allowed and source_map_done and artifact_freshness_done else "artifact_freshness_required",
    )

    add_task(
        tasks,
        825,
        "build_module_dependency_graph",
        "edge_factory_os_dependency_graph_v1.py",
        dependency_graph_done,
        repo_only_allowed and source_map_done and artifact_freshness_done and test_harness_done,
        f"Dependency graph completion evidence: {dependency_graph_evidence}",
        "" if repo_only_allowed and source_map_done and artifact_freshness_done and test_harness_done else "test_harness_required",
    )

    add_task(
        tasks,
        800,
        "build_runtime_apply_gate",
        "edge_factory_os_runtime_apply_gate_v1.py",
        runtime_apply_gate_done,
        False,
        f"Runtime apply gate evidence: {runtime_apply_gate_evidence}. Wait until runtime patch is actually needed.",
        "no_runtime_patch_allowed_currently",
    )

    add_task(
        tasks,
        775,
        "build_candidate_generation_guard",
        "edge_factory_os_candidate_generation_guard_v1.py",
        candidate_generation_guard_done,
        False,
        f"Candidate guard evidence: {candidate_generation_guard_evidence}. Strategy research is paused.",
        "strategy_research_paused",
    )

    tasks.append({
        "priority": 750,
        "task_key": "defer_drift_review",
        "module_name": "existing_drift_review",
        "status": "READY_READ_ONLY" if drift_ready else "BLOCKED",
        "done": False,
        "allowed": bool(drift_ready),
        "reason": f"closed={closed}/20",
        "blocked_by": "" if drift_ready else "closed_below_20",
    })

    tasks.append({
        "priority": 725,
        "task_key": "defer_capital_review",
        "module_name": "existing_capital_review",
        "status": "READY_READ_ONLY" if capital_ready else "BLOCKED",
        "done": False,
        "allowed": bool(capital_ready),
        "reason": f"closed={closed}/50",
        "blocked_by": "" if capital_ready else "closed_below_50",
    })

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
        next_module = ready_tasks[0]["module_name"]
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
        "module_completion": {
            "source_map_done": source_map_done,
            "artifact_freshness_done": artifact_freshness_done,
            "test_harness_done": test_harness_done,
            "dependency_graph_done": dependency_graph_done,
            "runtime_apply_gate_done": runtime_apply_gate_done,
            "candidate_generation_guard_done": candidate_generation_guard_done,
        },
        "runtime_touch_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "execution_performed": False,
        "tasks": sorted_tasks,
    }

    state_path = out_dir / "os_self_improvement_planner_v2_state.json"
    latest_path = OUT_ROOT / "os_self_improvement_planner_latest.json"
    tasks_csv = out_dir / "os_self_improvement_planner_v2_tasks.csv"
    report_path = out_dir / "os_self_improvement_planner_v2_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    with tasks_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["priority", "task_key", "module_name", "status", "done", "allowed", "reason", "blocked_by"],
        )
        writer.writeheader()
        writer.writerows(sorted_tasks)

    md = []
    md.append("# Edge Factory OS Self-Improvement Planner v2")
    md.append("")
    md.append(f"planner_status: `{planner_status}`")
    md.append(f"next_task: `{next_task}`")
    md.append(f"next_module: `{next_module}`")
    md.append("")
    md.append("## Completion")
    for k, v in state["module_completion"].items():
        md.append(f"- `{k}`: `{v}`")
    md.append("")
    md.append("## Safety")
    md.append("- runtime_touch_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    md.append("- execution_performed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS SELF-IMPROVEMENT PLANNER v2")
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
    print("MODULE COMPLETION")
    print("-" * 100)
    for k, v in state["module_completion"].items():
        print(f"{k}: {v}")
    print()
    print("TASKS")
    print("-" * 100)
    for t in sorted_tasks:
        print(f"{t['priority']} | {t['task_key']} | {t['status']} | done={t['done']} | allowed={t['allowed']} | {t['module_name']}")
    print()
    print(f"State : {state_path}")
    print(f"Latest: {latest_path}")
    print(f"Tasks : {tasks_csv}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
