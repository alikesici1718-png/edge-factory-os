#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO = WORKSPACE / "edge_factory_os_repo"
OUT_ROOT = WORKSPACE / "edge_factory_os_dangerous_marker_review_index_v1"

DEPENDENCY_GRAPH_ROOT = WORKSPACE / "edge_factory_os_dependency_graph_v1"
SOURCE_MAP_PATH = WORKSPACE / "edge_factory_os_repo_source_map_v1" / "os_repo_source_map_latest.json"
STACK_PATH = WORKSPACE / "edge_factory_os_standard_stack_runner_v1" / "os_standard_stack_latest.json"

CRITICAL_MARKERS = {
    "create_order",
    "place_order",
    "live order",
    "capital_change_allowed = True",
    "live_allowed = True",
    "active_paper_allowed = True",
}

EXPECTED_REVIEW_ONLY_MARKERS = {
    "capital_change_allowed",
    "live_allowed",
    "active_paper_allowed",
    "patch",
    "launcher",
    "Start-Process",
    "start_edge_factory_MASTER_UPPER_SYSTEM_v5_supervised.ps1",
    "patch_runtime",
    "runtime patch",
}

PATCH_OR_REPAIR_CATEGORIES = {
    "PATCH_OR_REPAIR_TOOL",
    "ARCHIVE_OR_BACKUP",
}

CORE_SAFE_TEXT_HINTS = [
    "False",
    "blocked",
    "Do not",
    "do not",
    "runtime_touch_allowed: False",
    "launcher_allowed",
    "patch_runtime_allowed",
    "capital_change_allowed: False",
    "live_allowed: False",
    "active_paper_allowed: False",
    "real_orders_allowed: False",
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

def latest_file(root: Path, pattern: str) -> Path | None:
    if not root.exists():
        return None
    files = list(root.rglob(pattern))
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def read_csv_rows(path: Path) -> list[dict]:
    if not path or not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
            return list(csv.DictReader(f))
    except Exception:
        return []

def repo_path_from_row_path(raw: str) -> Path:
    # dependency graph stores repo-relative path in `path`
    return REPO / raw

def classify_marker(row: dict, file_text: str) -> tuple[str, str, str]:
    marker = str(row.get("danger_marker") or "")
    category = str(row.get("category") or "")
    node_id = str(row.get("node_id") or "")
    path = str(row.get("path") or "")

    marker_lower = marker.lower()
    text_lower = file_text.lower()

    # Direct live/order/capital true markers are the only true critical class.
    if marker in CRITICAL_MARKERS:
        if "false" in text_lower and marker_lower.replace(" = true", "") in text_lower:
            return "REVIEW_ONLY_SAFETY_FLAG_TEXT", "ATTENTION", "critical-looking marker appears in safety text, but file contains false/blocking language"
        return "POTENTIAL_REAL_RISK", "CRITICAL", "critical marker requires manual review"

    # Actual exchange/order names are high attention unless clearly in blocked text.
    if marker_lower in {"create_order", "place_order", "live order"}:
        if any(h.lower() in text_lower for h in CORE_SAFE_TEXT_HINTS):
            return "REVIEW_ONLY_BLOCKED_ORDER_TEXT", "ATTENTION", "order marker appears in blocked/safety wording"
        return "POTENTIAL_REAL_ORDER_RISK", "CRITICAL", "order marker may indicate real execution path"

    if category in PATCH_OR_REPAIR_CATEGORIES:
        return "EXPECTED_PATCH_OR_ARCHIVE_REVIEW", "ATTENTION", "patch/repair/archive file; review-only, not active route"

    if "launcher" in marker_lower or "start-process" in marker_lower or "start_edge_factory" in marker_lower:
        if category in {"CORE_OS_TOOL", "OS_SUPERVISION", "DIAGNOSTIC_OR_GUARD"}:
            return "EXPECTED_LAUNCHER_BLOCK_OR_REFERENCE", "ATTENTION", "launcher marker appears in OS guard/router/supervision context"
        return "LAUNCHER_REFERENCE_REVIEW", "ATTENTION", "launcher reference should stay blocked unless explicit preflight allows"

    if "capital_change_allowed" in marker_lower or "live_allowed" in marker_lower or "active_paper_allowed" in marker_lower:
        if "false" in text_lower:
            return "EXPECTED_SAFETY_FLAG_FALSE", "OK", "safety flag appears with false/blocking semantics"
        return "SAFETY_FLAG_REVIEW", "ATTENTION", "safety flag appears without obvious false semantics"

    if marker in EXPECTED_REVIEW_ONLY_MARKERS:
        return "EXPECTED_REVIEW_ONLY_MARKER", "ATTENTION", "broad marker expected in OS safety/review code"

    if category in {"LOGGER", "RISK_MANAGER"}:
        return "RUNTIME_FILE_REVIEW_ONLY", "ATTENTION", "runtime-related repo copy contains marker; review only, runtime not touched"

    return "UNCLASSIFIED_REVIEW", "ATTENTION", "marker requires review classification"

def main() -> int:
    out_dir = OUT_ROOT / f"dangerous_marker_review_index_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    dependency_state_path = DEPENDENCY_GRAPH_ROOT / "os_dependency_graph_latest.json"
    dangerous_csv = latest_file(DEPENDENCY_GRAPH_ROOT, "os_dependency_graph_v1_dangerous_markers.csv")
    dependency_state = read_json(dependency_state_path)
    source_map = read_json(SOURCE_MAP_PATH)
    stack = read_json(STACK_PATH)

    rows_in = read_csv_rows(dangerous_csv) if dangerous_csv else []
    reviewed = []

    for row in rows_in:
        p = repo_path_from_row_path(str(row.get("path") or ""))
        text = read_text(p)
        classification, severity, reason = classify_marker(row, text)

        reviewed.append({
            "node_id": row.get("node_id", ""),
            "path": row.get("path", ""),
            "category": row.get("category", ""),
            "danger_marker": row.get("danger_marker", ""),
            "classification": classification,
            "severity": severity,
            "reason": reason,
        })

    severity_counts = Counter(r["severity"] for r in reviewed)
    classification_counts = Counter(r["classification"] for r in reviewed)
    category_counts = Counter(r["category"] for r in reviewed)

    critical_rows = [r for r in reviewed if r["severity"] == "CRITICAL"]
    attention_rows = [r for r in reviewed if r["severity"] == "ATTENTION"]

    git_status = run(["git", "status", "--short"], cwd=REPO)
    git_dirty = bool(git_status["stdout"].strip())

    source_map_ready = source_map.get("map_status") == "REPO_SOURCE_MAP_READY"
    dependency_graph_ready = dependency_state.get("dependency_graph_status") == "DEPENDENCY_GRAPH_READY"
    stack_pass = stack.get("stack_status") == "STACK_PASS"

    critical = []
    attention = []

    if not dependency_graph_ready:
        critical.append("DEPENDENCY_GRAPH_NOT_READY")
    if critical_rows:
        critical.append("CRITICAL_DANGEROUS_MARKERS_REQUIRE_MANUAL_REVIEW")
    if not source_map_ready:
        attention.append("SOURCE_MAP_NOT_READY")
    if not stack_pass:
        attention.append("STANDARD_STACK_NOT_PASS")
    if attention_rows:
        attention.append("ATTENTION_MARKERS_PRESENT_REVIEW_ONLY")
    if git_dirty:
        attention.append("REPO_DIRTY_EXPECTED_IF_NEW_DANGEROUS_MARKER_REVIEW_UNCOMMITTED")

    if critical:
        review_status = "DANGEROUS_MARKER_REVIEW_CRITICAL"
        next_action = "MANUALLY_REVIEW_CRITICAL_MARKERS_BEFORE_CONTINUING"
    else:
        review_status = "DANGEROUS_MARKER_REVIEW_READY"
        next_action = "CONTINUE_REPO_ONLY_OS_INTELLIGENCE_OR_WAIT"

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),
        "review_status": review_status,
        "marker_count": len(reviewed),
        "critical_marker_count": len(critical_rows),
        "attention_marker_count": len(attention_rows),
        "severity_counts": dict(severity_counts),
        "classification_counts": dict(classification_counts),
        "category_counts": dict(category_counts),
        "critical": critical,
        "attention": sorted(set(attention)),
        "dependency_graph_ready": dependency_graph_ready,
        "source_map_ready": source_map_ready,
        "stack_pass": stack_pass,
        "git_dirty": git_dirty,
        "git_status_short": git_status["stdout"].strip(),
        "dangerous_csv": str(dangerous_csv) if dangerous_csv else "",
        "next_action": next_action,
        "runtime_touch_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "execution_performed": False,
        "reviewed_markers": reviewed,
    }

    state_path = out_dir / "dangerous_marker_review_index_v1_state.json"
    latest_path = OUT_ROOT / "dangerous_marker_review_index_latest.json"
    reviewed_csv = out_dir / "dangerous_marker_review_index_v1_reviewed.csv"
    critical_csv = out_dir / "dangerous_marker_review_index_v1_critical.csv"
    report_path = out_dir / "dangerous_marker_review_index_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    fieldnames = ["node_id", "path", "category", "danger_marker", "classification", "severity", "reason"]

    with reviewed_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reviewed)

    with critical_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(critical_rows)

    md = []
    md.append("# Edge Factory OS Dangerous Marker Review Index v1")
    md.append("")
    md.append(f"review_status: `{review_status}`")
    md.append(f"marker_count: `{len(reviewed)}`")
    md.append(f"critical_marker_count: `{len(critical_rows)}`")
    md.append(f"attention_marker_count: `{len(attention_rows)}`")
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
    md.append("## Classification counts")
    for k, v in classification_counts.most_common():
        md.append(f"- `{k}`: `{v}`")
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

    print("EDGE FACTORY OS DANGEROUS MARKER REVIEW INDEX v1")
    print("=" * 100)
    print(f"review_status: {review_status}")
    print(f"marker_count: {len(reviewed)}")
    print(f"critical_marker_count: {len(critical_rows)}")
    print(f"attention_marker_count: {len(attention_rows)}")
    print(f"critical: {critical}")
    print(f"attention: {sorted(set(attention))}")
    print(f"dependency_graph_ready={dependency_graph_ready}")
    print(f"source_map_ready={source_map_ready}")
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
    print("CLASSIFICATION COUNTS")
    print("-" * 100)
    for k, v in classification_counts.most_common():
        print(f"{k}: {v}")
    print()
    print("CRITICAL MARKERS")
    print("-" * 100)
    if critical_rows:
        for r in critical_rows:
            print(f"- {r['path']} | {r['danger_marker']} | {r['classification']} | {r['reason']}")
    else:
        print("NONE")
    print()
    print(f"State   : {state_path}")
    print(f"Latest  : {latest_path}")
    print(f"Reviewed: {reviewed_csv}")
    print(f"Critical: {critical_csv}")
    print(f"Report  : {report_path}")

if __name__ == "__main__":
    main()
