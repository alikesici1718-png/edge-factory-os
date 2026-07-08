#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import json
import re
import subprocess
from collections import defaultdict, Counter
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO = WORKSPACE / "edge_factory_os_repo"
OUT_ROOT = WORKSPACE / "edge_factory_os_dependency_graph_v1"

SOURCE_MAP_PATH = WORKSPACE / "edge_factory_os_repo_source_map_v1" / "os_repo_source_map_latest.json"
FRESHNESS_PATH = WORKSPACE / "edge_factory_os_artifact_freshness_index_v1" / "os_artifact_freshness_index_latest.json"
TEST_HARNESS_PATH = WORKSPACE / "edge_factory_os_test_harness_manifest_v1" / "os_test_harness_manifest_latest.json"
STACK_PATH = WORKSPACE / "edge_factory_os_standard_stack_runner_v1" / "os_standard_stack_latest.json"

KNOWN_ARTIFACTS = {
    "standard_stack_latest": "edge_factory_os_standard_stack_runner_v1/os_standard_stack_latest.json",
    "unified_state_latest": "edge_factory_os_unified_state_reader_v1/os_unified_state_latest.json",
    "policy_engine_latest": "edge_factory_os_policy_engine_v1/os_policy_engine_latest.json",
    "next_action_planner_latest": "edge_factory_os_next_action_planner_v1/os_next_action_planner_latest.json",
    "autopilot_decision_latest": "edge_factory_os_autopilot_decision_adapter_v1/os_autopilot_decision_latest.json",
    "execution_router_latest": "edge_factory_os_execution_router_v1/os_execution_router_latest.json",
    "memory_lesson_index_latest": "edge_factory_os_memory_lesson_index_v1/os_memory_lesson_index_latest.json",
    "repo_source_map_latest": "edge_factory_os_repo_source_map_v1/os_repo_source_map_latest.json",
    "artifact_freshness_latest": "edge_factory_os_artifact_freshness_index_v1/os_artifact_freshness_index_latest.json",
    "test_harness_latest": "edge_factory_os_test_harness_manifest_v1/os_test_harness_manifest_latest.json",
    "dependency_graph_latest": "edge_factory_os_dependency_graph_v1/os_dependency_graph_latest.json",
    "self_improvement_planner_latest": "edge_factory_os_self_improvement_planner_v2/os_self_improvement_planner_latest.json",
    "command_center_v2_overlay_latest": "edge_factory_os_command_center_v2_overlay/os_command_center_v2_overlay_latest.json",
    "error_acknowledger_latest": "edge_factory_error_acknowledger_v1/error_acknowledger_latest.json",
}

CANONICAL_STACK_ORDER = [
    "edge_factory_runtime_regression_guard_v1.py",
    "edge_factory_os_unified_state_reader_v1.py",
    "edge_factory_os_policy_engine_v1.py",
    "edge_factory_os_next_action_planner_v1.py",
    "edge_factory_os_autopilot_decision_adapter_v1.py",
    "edge_factory_os_execution_router_v1.py",
    "edge_factory_os_standard_stack_runner_v1.py",
]

CORE_TOOLS = set(CANONICAL_STACK_ORDER + [
    "edge_factory_os_memory_lesson_index_v1.py",
    "edge_factory_os_repo_source_map_v1.py",
    "edge_factory_os_artifact_freshness_index_v1.py",
    "edge_factory_os_test_harness_manifest_v1.py",
    "edge_factory_os_self_improvement_planner_v2.py",
    "edge_factory_os_dependency_graph_v1.py",
])

DANGEROUS_RUNTIME_MARKERS = [
    "Start-Process",
    "start_edge_factory_MASTER_UPPER_SYSTEM_v5_supervised.ps1",
    "patch_runtime",
    "runtime patch",
    "create_order",
    "place_order",
    "live order",
    "capital_change_allowed = True",
    "live_allowed = True",
    "active_paper_allowed = True",
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

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

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

def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except Exception:
        return str(path)

def classify_tool(path: Path) -> str:
    name = path.name
    if name in CORE_TOOLS:
        return "CORE_OS_TOOL"
    if "risk_manager" in name:
        return "RISK_MANAGER"
    if "logger" in name or "live_paper" in name:
        return "LOGGER"
    if "patch" in name or "repair" in name:
        return "PATCH_OR_REPAIR_TOOL"
    if "candidate" in name or "contract" in name or "selector" in name or "learning" in name:
        return "RESEARCH_CANDIDATE_OS"
    if "offline" in name or "runner" in name or "feature" in name or "validation" in name:
        return "OFFLINE_RESEARCH"
    if "command_center" in name or "watchdog" in name or "autopilot" in name or "supervisor" in name:
        return "OS_SUPERVISION"
    if "diagnos" in name or "guard" in name or "auditor" in name or "preflight" in name:
        return "DIAGNOSTIC_OR_GUARD"
    return "OTHER"

def detect_artifact_deps(text: str) -> list[dict]:
    deps = []
    for artifact_key, marker in KNOWN_ARTIFACTS.items():
        if marker.replace("/", "\\") in text or marker.replace("/", "/") in text or Path(marker).name in text:
            deps.append({
                "artifact_key": artifact_key,
                "artifact_marker": marker,
            })
    return deps

def detect_tool_deps(text: str, all_tool_names: set[str]) -> list[str]:
    deps = []
    for name in all_tool_names:
        if name in text:
            deps.append(name)
    return sorted(set(deps))

def detect_dangerous_hits(text: str) -> list[str]:
    hits = []
    lower = text.lower()
    for marker in DANGEROUS_RUNTIME_MARKERS:
        if marker.lower() in lower:
            hits.append(marker)
    return sorted(set(hits))

def main() -> int:
    out_dir = OUT_ROOT / f"os_dependency_graph_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    source_map = read_json(SOURCE_MAP_PATH)
    freshness = read_json(FRESHNESS_PATH)
    test_harness = read_json(TEST_HARNESS_PATH)
    stack = read_json(STACK_PATH)

    tool_paths = []
    for p in REPO.rglob("*.py"):
        if ".git" in p.parts or "__pycache__" in p.parts:
            continue
        if rel(p).startswith("tools\\") or rel(p).startswith("tools/") or rel(p).startswith("src\\") or rel(p).startswith("src/"):
            tool_paths.append(p)

    all_tool_names = {p.name for p in tool_paths}

    nodes = []
    edges = []
    dangerous = []

    for p in sorted(tool_paths):
        text = read_text(p)
        category = classify_tool(p)
        node_id = p.name

        nodes.append({
            "node_id": node_id,
            "path": rel(p),
            "category": category,
            "is_core_tool": node_id in CORE_TOOLS,
            "line_count": text.count("\n") + 1 if text else 0,
        })

        for dep in detect_artifact_deps(text):
            edges.append({
                "from_node": node_id,
                "to_node": dep["artifact_key"],
                "edge_type": "READS_ARTIFACT",
                "evidence": dep["artifact_marker"],
            })

        for dep_tool in detect_tool_deps(text, all_tool_names):
            if dep_tool != node_id:
                edges.append({
                    "from_node": node_id,
                    "to_node": dep_tool,
                    "edge_type": "REFERENCES_TOOL",
                    "evidence": dep_tool,
                })

        hits = detect_dangerous_hits(text)
        for h in hits:
            dangerous.append({
                "node_id": node_id,
                "path": rel(p),
                "category": category,
                "danger_marker": h,
            })

    # Add artifact nodes.
    for artifact_key, marker in KNOWN_ARTIFACTS.items():
        nodes.append({
            "node_id": artifact_key,
            "path": marker,
            "category": "ARTIFACT",
            "is_core_tool": False,
            "line_count": "",
        })

    incoming_count = Counter(e["to_node"] for e in edges)
    outgoing_count = Counter(e["from_node"] for e in edges)

    node_summary = []
    for n in nodes:
        node_summary.append({
            **n,
            "incoming_edges": incoming_count.get(n["node_id"], 0),
            "outgoing_edges": outgoing_count.get(n["node_id"], 0),
        })

    # Canonical stack dependency sanity.
    stack_order_checks = []
    for i, name in enumerate(CANONICAL_STACK_ORDER):
        expected_position = i + 1
        exists = any(n["node_id"] == name for n in nodes)
        stack_order_checks.append({
            "tool": name,
            "expected_position": expected_position,
            "exists": exists,
        })

    missing_core_tools = [x for x in CORE_TOOLS if not any(n["node_id"] == x for n in nodes)]

    source_map_ready = source_map.get("map_status") == "REPO_SOURCE_MAP_READY"
    freshness_ready = freshness.get("freshness_status") in {
        "ARTIFACT_FRESHNESS_INDEX_READY",
        "ARTIFACT_FRESHNESS_PASS_WITH_ATTENTION",
    }
    test_harness_ready = test_harness.get("test_harness_status") == "TEST_HARNESS_MANIFEST_READY"
    stack_pass = stack.get("stack_status") == "STACK_PASS"

    git_status = run(["git", "status", "--short"], cwd=REPO)
    git_dirty = bool(git_status["stdout"].strip())

    critical = []
    attention = []

    if missing_core_tools:
        critical.append("MISSING_CORE_OS_TOOLS")
    if not source_map_ready:
        attention.append("SOURCE_MAP_NOT_READY")
    if not freshness_ready:
        attention.append("FRESHNESS_INDEX_NOT_READY")
    if not test_harness_ready:
        attention.append("TEST_HARNESS_NOT_READY")
    if not stack_pass:
        attention.append("STANDARD_STACK_NOT_PASS")
    if git_dirty:
        attention.append("REPO_DIRTY_EXPECTED_IF_NEW_DEPENDENCY_GRAPH_UNCOMMITTED")

    # Dangerous hits are informational/attention because source map already classified many broad markers.
    runtime_dangerous = [
        d for d in dangerous
        if d["category"] in {"CORE_OS_TOOL", "OS_SUPERVISION", "RISK_MANAGER", "LOGGER", "PATCH_OR_REPAIR_TOOL"}
    ]
    if runtime_dangerous:
        attention.append("DANGEROUS_MARKERS_PRESENT_REVIEW_ONLY")

    if critical:
        dependency_graph_status = "DEPENDENCY_GRAPH_CRITICAL"
        next_action = "FIX_MISSING_CORE_TOOL_DEPENDENCIES"
    else:
        dependency_graph_status = "DEPENDENCY_GRAPH_READY"
        next_action = "CONTINUE_TO_RUNTIME_APPLY_GATE_LATER_OR_HOLD"

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),
        "dependency_graph_status": dependency_graph_status,
        "node_count": len(nodes),
        "tool_node_count": len(tool_paths),
        "artifact_node_count": len(KNOWN_ARTIFACTS),
        "edge_count": len(edges),
        "dangerous_marker_count": len(dangerous),
        "runtime_dangerous_marker_count": len(runtime_dangerous),
        "missing_core_tool_count": len(missing_core_tools),
        "missing_core_tools": sorted(missing_core_tools),
        "critical": critical,
        "attention": sorted(set(attention)),
        "source_map_ready": source_map_ready,
        "freshness_ready": freshness_ready,
        "test_harness_ready": test_harness_ready,
        "stack_pass": stack_pass,
        "git_dirty": git_dirty,
        "git_status_short": git_status["stdout"].strip(),
        "next_action": next_action,
        "runtime_touch_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "execution_performed": False,
        "stack_order_checks": stack_order_checks,
    }

    state_path = out_dir / "os_dependency_graph_v1_state.json"
    latest_path = OUT_ROOT / "os_dependency_graph_latest.json"
    nodes_csv = out_dir / "os_dependency_graph_v1_nodes.csv"
    edges_csv = out_dir / "os_dependency_graph_v1_edges.csv"
    dangerous_csv = out_dir / "os_dependency_graph_v1_dangerous_markers.csv"
    report_path = out_dir / "os_dependency_graph_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    with nodes_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["node_id", "path", "category", "is_core_tool", "line_count", "incoming_edges", "outgoing_edges"],
        )
        writer.writeheader()
        writer.writerows(node_summary)

    with edges_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["from_node", "to_node", "edge_type", "evidence"],
        )
        writer.writeheader()
        writer.writerows(edges)

    with dangerous_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["node_id", "path", "category", "danger_marker"],
        )
        writer.writeheader()
        writer.writerows(dangerous)

    md = []
    md.append("# Edge Factory OS Dependency Graph v1")
    md.append("")
    md.append(f"dependency_graph_status: `{dependency_graph_status}`")
    md.append(f"node_count: `{len(nodes)}`")
    md.append(f"edge_count: `{len(edges)}`")
    md.append(f"dangerous_marker_count: `{len(dangerous)}`")
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
        for x in sorted(set(attention)):
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

    print("EDGE FACTORY OS DEPENDENCY GRAPH v1")
    print("=" * 100)
    print(f"dependency_graph_status: {dependency_graph_status}")
    print(f"node_count: {len(nodes)}")
    print(f"tool_node_count: {len(tool_paths)}")
    print(f"artifact_node_count: {len(KNOWN_ARTIFACTS)}")
    print(f"edge_count: {len(edges)}")
    print(f"dangerous_marker_count: {len(dangerous)}")
    print(f"runtime_dangerous_marker_count: {len(runtime_dangerous)}")
    print(f"missing_core_tool_count: {len(missing_core_tools)}")
    print(f"critical: {critical}")
    print(f"attention: {sorted(set(attention))}")
    print(f"source_map_ready={source_map_ready}")
    print(f"freshness_ready={freshness_ready}")
    print(f"test_harness_ready={test_harness_ready}")
    print(f"stack_pass={stack_pass}")
    print(f"git_dirty={git_dirty}")
    print(f"next_action: {next_action}")
    print("runtime_touch_allowed: False")
    print("launcher_allowed     : False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed : False")
    print("live_allowed         : False")
    print("capital_change_allowed: False")
    print("execution_performed  : False")
    print()
    print("MISSING CORE TOOLS")
    print("-" * 100)
    print("\n".join(f"- {x}" for x in sorted(missing_core_tools)) if missing_core_tools else "NONE")
    print()
    print("TOP ARTIFACT DEPENDENCIES")
    print("-" * 100)
    artifact_edges = [e for e in edges if e["edge_type"] == "READS_ARTIFACT"]
    c = Counter(e["to_node"] for e in artifact_edges)
    if c:
        for k, v in c.most_common(20):
            print(f"{k}: {v}")
    else:
        print("NONE")
    print()
    print(f"State    : {state_path}")
    print(f"Latest   : {latest_path}")
    print(f"Nodes    : {nodes_csv}")
    print(f"Edges    : {edges_csv}")
    print(f"Dangerous: {dangerous_csv}")
    print(f"Report   : {report_path}")

if __name__ == "__main__":
    main()
