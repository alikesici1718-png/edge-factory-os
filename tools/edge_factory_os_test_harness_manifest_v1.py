#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import json
import py_compile
import subprocess
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO = WORKSPACE / "edge_factory_os_repo"
OUT_ROOT = WORKSPACE / "edge_factory_os_test_harness_manifest_v1"

SOURCE_MAP_PATH = WORKSPACE / "edge_factory_os_repo_source_map_v1" / "os_repo_source_map_latest.json"
FRESHNESS_PATH = WORKSPACE / "edge_factory_os_artifact_freshness_index_v1" / "os_artifact_freshness_index_latest.json"
STACK_PATH = WORKSPACE / "edge_factory_os_standard_stack_runner_v1" / "os_standard_stack_latest.json"

CORE_TOOLS = [
    "edge_factory_runtime_regression_guard_v1.py",
    "edge_factory_os_unified_state_reader_v1.py",
    "edge_factory_os_policy_engine_v1.py",
    "edge_factory_os_next_action_planner_v1.py",
    "edge_factory_os_memory_lesson_index_v1.py",
    "edge_factory_os_autopilot_decision_adapter_v1.py",
    "edge_factory_os_execution_router_v1.py",
    "edge_factory_os_standard_stack_runner_v1.py",
    "edge_factory_os_self_improvement_planner_v2.py",
    "edge_factory_os_repo_source_map_v1.py",
    "edge_factory_os_artifact_freshness_index_v1.py",
    "edge_factory_os_test_harness_manifest_v1.py",
]

ACTIVE_RUNTIME_REPO_COPIES = [
    "src/global_paper_risk_manager_v4_config.py",
    "src/global_paper_risk_manager_v3_priority.py",
    "src/old_short_gate_aware_live_paper_logger.py",
    "src/impulse_long_gate_aware_live_paper_logger.py",
    "src/market_relative_live_paper_logger.py",
    "src/weak_market_breakdown_short_live_paper_logger.py",
    "src/edge_factory_os_process_watchdog_v1.py",
    "src/edge_factory_live_health_check_v5.py",
    "src/edge_factory_os_command_center_v2_overlay.py",
    "src/edge_factory_error_classifier_v1.py",
    "src/edge_factory_error_acknowledger_v1.py",
    "src/edge_factory_os_autopilot_loop_v4.py",
]

BLOCKED_TEST_PATTERNS = [
    "start_edge_factory_MASTER_UPPER_SYSTEM",
    "Start-Process",
    "launcher",
    "live order",
    "create_order",
    "place_order",
    "capital_change",
    "runtime patch",
]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e), "__path__": str(path)}

def run(cmd: list[str], cwd: Path | None = None, timeout: int = 60) -> dict:
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

def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except Exception:
        return str(path)

def compile_file(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, "missing"
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "py_compile_pass"
    except Exception as e:
        return False, repr(e)

def add_test(
    rows: list[dict],
    test_key: str,
    file_path: Path,
    test_type: str,
    allowed: bool,
    status: str,
    result: str,
    command: str,
    notes: str = "",
) -> None:
    rows.append({
        "test_key": test_key,
        "path": rel(file_path),
        "test_type": test_type,
        "allowed": bool(allowed),
        "status": status,
        "result": result,
        "command": command,
        "notes": notes,
    })

def main() -> int:
    out_dir = OUT_ROOT / f"os_test_harness_manifest_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    source_map = read_json(SOURCE_MAP_PATH)
    freshness = read_json(FRESHNESS_PATH)
    stack = read_json(STACK_PATH)

    git_status = run(["git", "status", "--short"], cwd=REPO)
    git_dirty = bool(git_status["stdout"].strip())

    rows: list[dict] = []

    # 1) Compile core OS tools.
    for name in CORE_TOOLS:
        path = REPO / "tools" / name
        ok, result = compile_file(path)
        add_test(
            rows,
            f"compile_core_tool:{name}",
            path,
            "py_compile_core_os_tool",
            True,
            "PASS" if ok else "FAIL",
            result,
            f'python -m py_compile "{path}"',
        )

    # 2) Compile active runtime repo copies only. This does not touch actual runtime files.
    for rel_path in ACTIVE_RUNTIME_REPO_COPIES:
        path = REPO / rel_path
        ok, result = compile_file(path)
        add_test(
            rows,
            f"compile_runtime_copy:{Path(rel_path).name}",
            path,
            "py_compile_runtime_repo_copy",
            True,
            "PASS" if ok else "FAIL",
            result,
            f'python -m py_compile "{path}"',
            "repo copy only; actual runtime file untouched",
        )

    # 3) Safe command manifest tests, not executed.
    safe_commands = [
        r'python -u ".\tools\edge_factory_os_standard_stack_runner_v1.py"',
        r'python -u ".\tools\edge_factory_runtime_regression_guard_v1.py"',
        r'python -u ".\tools\edge_factory_os_unified_state_reader_v1.py"',
        r'python -u ".\tools\edge_factory_os_policy_engine_v1.py"',
        r'python -u ".\tools\edge_factory_os_next_action_planner_v1.py"',
        r'python -u ".\tools\edge_factory_os_autopilot_decision_adapter_v1.py"',
        r'python -u ".\tools\edge_factory_os_execution_router_v1.py"',
        r'python -u ".\tools\edge_factory_os_self_improvement_planner_v2.py"',
        r'python -u ".\tools\edge_factory_os_repo_source_map_v1.py"',
        r'python -u ".\tools\edge_factory_os_artifact_freshness_index_v1.py"',
    ]

    for i, cmd in enumerate(safe_commands, start=1):
        blocked_hit = [p for p in BLOCKED_TEST_PATTERNS if p.lower() in cmd.lower()]
        add_test(
            rows,
            f"safe_command_manifest:{i}",
            REPO,
            "safe_command_manifest_only",
            not blocked_hit,
            "PASS" if not blocked_hit else "FAIL",
            "safe_repo_or_read_only_command" if not blocked_hit else "blocked_pattern:" + "|".join(blocked_hit),
            cmd,
            "manifest only; not executed by this harness",
        )

    # 4) Explicit blocked commands manifest.
    blocked_commands = [
        r'powershell -ExecutionPolicy Bypass -File "C:\Users\alike\start_edge_factory_MASTER_UPPER_SYSTEM_v5_supervised.ps1"',
        "any runtime patch command",
        "any new active paper family launcher",
        "any live order command",
        "any capital change command",
    ]

    for i, cmd in enumerate(blocked_commands, start=1):
        add_test(
            rows,
            f"blocked_command_manifest:{i}",
            REPO,
            "blocked_command_manifest_only",
            False,
            "BLOCKED_EXPECTED",
            "blocked_by_safety_contract",
            cmd,
            "must not be executed by test harness",
        )

    compile_failures = [
        r for r in rows
        if r["test_type"] in {"py_compile_core_os_tool", "py_compile_runtime_repo_copy"}
        and r["status"] == "FAIL"
    ]

    unsafe_allowed = [
        r for r in rows
        if r["allowed"] is True
        and any(p.lower() in r["command"].lower() for p in BLOCKED_TEST_PATTERNS)
    ]

    missing_core_source_map = source_map.get("map_status") != "REPO_SOURCE_MAP_READY"
    freshness_not_ready = freshness.get("freshness_status") not in {
        "ARTIFACT_FRESHNESS_INDEX_READY",
        "ARTIFACT_FRESHNESS_PASS_WITH_ATTENTION",
    }
    stack_not_pass = stack.get("stack_status") != "STACK_PASS"

    attention = []
    critical = []

    if compile_failures:
        critical.append("PY_COMPILE_FAILURES")
    if unsafe_allowed:
        critical.append("UNSAFE_ALLOWED_TEST_COMMAND")
    if missing_core_source_map:
        attention.append("SOURCE_MAP_NOT_READY")
    if freshness_not_ready:
        attention.append("FRESHNESS_INDEX_NOT_READY")
    if stack_not_pass:
        attention.append("STANDARD_STACK_NOT_PASS")
    if git_dirty:
        attention.append("REPO_DIRTY_EXPECTED_IF_NEW_TEST_HARNESS_UNCOMMITTED")

    if critical:
        test_harness_status = "TEST_HARNESS_MANIFEST_CRITICAL"
        next_action = "FIX_TEST_HARNESS_CRITICAL_FAILURES"
    else:
        test_harness_status = "TEST_HARNESS_MANIFEST_READY"
        next_action = "CONTINUE_TO_DEPENDENCY_GRAPH"

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),
        "test_harness_status": test_harness_status,
        "test_count": len(rows),
        "compile_failure_count": len(compile_failures),
        "unsafe_allowed_count": len(unsafe_allowed),
        "critical": critical,
        "attention": attention,
        "git_dirty": git_dirty,
        "git_status_short": git_status["stdout"].strip(),
        "source_map_status": source_map.get("map_status"),
        "freshness_status": freshness.get("freshness_status"),
        "stack_status": stack.get("stack_status"),
        "next_action": next_action,
        "runtime_touch_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "execution_performed": False,
        "tests": rows,
    }

    state_path = out_dir / "os_test_harness_manifest_v1_state.json"
    latest_path = OUT_ROOT / "os_test_harness_manifest_latest.json"
    tests_csv = out_dir / "os_test_harness_manifest_v1_tests.csv"
    report_path = out_dir / "os_test_harness_manifest_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    with tests_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["test_key", "path", "test_type", "allowed", "status", "result", "command", "notes"],
        )
        writer.writeheader()
        writer.writerows(rows)

    md = []
    md.append("# Edge Factory OS Test Harness Manifest v1")
    md.append("")
    md.append(f"test_harness_status: `{test_harness_status}`")
    md.append(f"test_count: `{len(rows)}`")
    md.append(f"compile_failure_count: `{len(compile_failures)}`")
    md.append(f"unsafe_allowed_count: `{len(unsafe_allowed)}`")
    md.append("")
    md.append("## Critical")
    if critical:
        for x in critical:
            md.append(f"- `{x}`")
    else:
        md.append("- `NONE`")
    md.append("")
    md.append("## Attention")
    if attention:
        for x in attention:
            md.append(f"- `{x}`")
    else:
        md.append("- `NONE`")
    md.append("")
    md.append("## Safety")
    md.append("- runtime_touch_allowed: `False`")
    md.append("- launcher_allowed: `False`")
    md.append("- patch_runtime_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    md.append("- execution_performed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS TEST HARNESS MANIFEST v1")
    print("=" * 100)
    print(f"test_harness_status: {test_harness_status}")
    print(f"test_count: {len(rows)}")
    print(f"compile_failure_count: {len(compile_failures)}")
    print(f"unsafe_allowed_count: {len(unsafe_allowed)}")
    print(f"critical: {critical}")
    print(f"attention: {attention}")
    print(f"git_dirty: {git_dirty}")
    print(f"source_map_status: {source_map.get('map_status')}")
    print(f"freshness_status: {freshness.get('freshness_status')}")
    print(f"stack_status: {stack.get('stack_status')}")
    print(f"next_action: {next_action}")
    print("runtime_touch_allowed: False")
    print("launcher_allowed     : False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed : False")
    print("live_allowed         : False")
    print("capital_change_allowed: False")
    print("execution_performed  : False")
    print()
    print("COMPILE FAILURES")
    print("-" * 100)
    if compile_failures:
        for r in compile_failures:
            print(f"- {r['path']}: {r['result']}")
    else:
        print("NONE")
    print()
    print("UNSAFE ALLOWED")
    print("-" * 100)
    if unsafe_allowed:
        for r in unsafe_allowed:
            print(f"- {r['test_key']}: {r['command']}")
    else:
        print("NONE")
    print()
    print(f"State : {state_path}")
    print(f"Latest: {latest_path}")
    print(f"Tests : {tests_csv}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
