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
OUT_ROOT = WORKSPACE / "edge_factory_os_artifact_freshness_index_v1"

# name, path, importance, max_age_minutes
ARTIFACTS = [
    ("standard_stack", WORKSPACE / "edge_factory_os_standard_stack_runner_v1" / "os_standard_stack_latest.json", "CRITICAL", 120),
    ("unified_state", WORKSPACE / "edge_factory_os_unified_state_reader_v1" / "os_unified_state_latest.json", "CRITICAL", 120),
    ("policy_engine", WORKSPACE / "edge_factory_os_policy_engine_v1" / "os_policy_engine_latest.json", "CRITICAL", 120),
    ("next_action_planner", WORKSPACE / "edge_factory_os_next_action_planner_v1" / "os_next_action_planner_latest.json", "CRITICAL", 120),
    ("autopilot_decision", WORKSPACE / "edge_factory_os_autopilot_decision_adapter_v1" / "os_autopilot_decision_latest.json", "CRITICAL", 120),
    ("execution_router", WORKSPACE / "edge_factory_os_execution_router_v1" / "os_execution_router_latest.json", "CRITICAL", 120),

    ("memory_lesson_index", WORKSPACE / "edge_factory_os_memory_lesson_index_v1" / "os_memory_lesson_index_latest.json", "IMPORTANT", 24 * 60),
    ("repo_source_map", WORKSPACE / "edge_factory_os_repo_source_map_v1" / "os_repo_source_map_latest.json", "IMPORTANT", 24 * 60),
    ("self_improvement_planner_v2", WORKSPACE / "edge_factory_os_self_improvement_planner_v2" / "os_self_improvement_planner_latest.json", "IMPORTANT", 240),

    ("command_center_v2_overlay", WORKSPACE / "edge_factory_os_command_center_v2_overlay" / "os_command_center_v2_overlay_latest.json", "RUNTIME", 120),
    ("error_acknowledger", WORKSPACE / "edge_factory_error_acknowledger_v1" / "error_acknowledger_latest.json", "RUNTIME", 24 * 60),
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

def artifact_age_minutes(path: Path, now_ts: float) -> float | None:
    if not path.exists():
        return None
    return round((now_ts - path.stat().st_mtime) / 60.0, 2)

def detect_status(name: str, data: dict) -> str:
    if not data:
        return "NO_JSON"
    if "__read_error__" in data:
        return "READ_ERROR"

    known_keys = [
        "stack_status",
        "state_level",
        "policy_status",
        "planner_status",
        "final_status",
        "router_status",
        "memory_status",
        "map_status",
        "overlay_status",
        "status",
        "freshness_status",
    ]

    for key in known_keys:
        if key in data:
            return f"{key}={data.get(key)}"

    return "JSON_READABLE_NO_KNOWN_STATUS_KEY"

def add_artifact_row(rows: list[dict], name: str, path: Path, importance: str, max_age_minutes: int, now_ts: float) -> None:
    exists = path.exists()
    age = artifact_age_minutes(path, now_ts)
    data = read_json(path)
    detected_status = detect_status(name, data)

    if not exists:
        freshness = "MISSING"
        severity = "CRITICAL" if importance == "CRITICAL" else "ATTENTION"
    elif "__read_error__" in data:
        freshness = "READ_ERROR"
        severity = "CRITICAL"
    elif age is not None and age > max_age_minutes:
        freshness = "STALE"
        severity = "ATTENTION" if importance != "CRITICAL" else "CRITICAL"
    else:
        freshness = "FRESH"
        severity = "OK"

    rows.append({
        "artifact": name,
        "path": str(path),
        "importance": importance,
        "exists": exists,
        "age_minutes": age if age is not None else "",
        "max_age_minutes": max_age_minutes,
        "freshness": freshness,
        "severity": severity,
        "detected_status": detected_status,
    })

def main() -> int:
    out_dir = OUT_ROOT / f"os_artifact_freshness_index_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    now_ts = datetime.now(timezone.utc).timestamp()
    rows: list[dict] = []

    for name, path, importance, max_age in ARTIFACTS:
        add_artifact_row(rows, name, path, importance, max_age, now_ts)

    # Dynamic latest error classifier state.
    classifier_latest = latest_file(WORKSPACE / "edge_factory_error_classifier_v1", "error_classifier_v1_state.json")
    if classifier_latest:
        add_artifact_row(rows, "error_classifier_latest_state", classifier_latest, "RUNTIME", 24 * 60, now_ts)
    else:
        rows.append({
            "artifact": "error_classifier_latest_state",
            "path": str(WORKSPACE / "edge_factory_error_classifier_v1"),
            "importance": "RUNTIME",
            "exists": False,
            "age_minutes": "",
            "max_age_minutes": 24 * 60,
            "freshness": "MISSING",
            "severity": "ATTENTION",
            "detected_status": "NO_CLASSIFIER_STATE_FOUND",
        })

    git_status = run(["git", "status", "--short"], cwd=REPO)
    git_dirty = bool(git_status["stdout"].strip())

    critical_failed = [r for r in rows if r["severity"] == "CRITICAL"]
    attention_failed = [r for r in rows if r["severity"] == "ATTENTION"]

    if critical_failed:
        freshness_status = "ARTIFACT_FRESHNESS_CRITICAL"
        next_action = "REBUILD_MISSING_OR_STALE_CRITICAL_ARTIFACTS"
    elif attention_failed:
        freshness_status = "ARTIFACT_FRESHNESS_PASS_WITH_ATTENTION"
        next_action = "REVIEW_ATTENTION_ARTIFACTS_THEN_CONTINUE"
    else:
        freshness_status = "ARTIFACT_FRESHNESS_INDEX_READY"
        next_action = "CONTINUE_TO_TEST_HARNESS_MANIFEST"

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),
        "freshness_status": freshness_status,
        "artifact_count": len(rows),
        "critical_failed": len(critical_failed),
        "attention_failed": len(attention_failed),
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
        "artifacts": rows,
    }

    state_path = out_dir / "os_artifact_freshness_index_v1_state.json"
    latest_path = OUT_ROOT / "os_artifact_freshness_index_latest.json"
    csv_path = out_dir / "os_artifact_freshness_index_v1_artifacts.csv"
    report_path = out_dir / "os_artifact_freshness_index_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "artifact", "path", "importance", "exists", "age_minutes",
                "max_age_minutes", "freshness", "severity", "detected_status",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    md = []
    md.append("# Edge Factory OS Artifact Freshness Index v1")
    md.append("")
    md.append(f"freshness_status: `{freshness_status}`")
    md.append(f"artifact_count: `{len(rows)}`")
    md.append(f"critical_failed: `{len(critical_failed)}`")
    md.append(f"attention_failed: `{len(attention_failed)}`")
    md.append("")
    md.append("## Failed / attention artifacts")
    failed = critical_failed + attention_failed
    if failed:
        for r in failed:
            md.append(f"- `{r['severity']}` `{r['artifact']}` `{r['freshness']}` age=`{r['age_minutes']}` status=`{r['detected_status']}`")
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

    print("EDGE FACTORY OS ARTIFACT FRESHNESS INDEX v1")
    print("=" * 100)
    print(f"freshness_status: {freshness_status}")
    print(f"artifact_count: {len(rows)}")
    print(f"critical_failed: {len(critical_failed)}")
    print(f"attention_failed: {len(attention_failed)}")
    print(f"git_dirty: {git_dirty}")
    print(f"next_action: {next_action}")
    print("runtime_touch_allowed: False")
    print("launcher_allowed     : False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed : False")
    print("live_allowed         : False")
    print("capital_change_allowed: False")
    print("execution_performed  : False")
    print()
    print("FAILED / ATTENTION ARTIFACTS")
    print("-" * 100)
    failed = critical_failed + attention_failed
    if not failed:
        print("NONE")
    else:
        for r in failed:
            print(f"[{r['severity']}] {r['artifact']} | {r['freshness']} | age={r['age_minutes']} | status={r['detected_status']}")
    print()
    print("ARTIFACT SUMMARY")
    print("-" * 100)
    for r in rows:
        print(f"{r['artifact']}: {r['freshness']} age={r['age_minutes']} status={r['detected_status']}")
    print()
    print(f"State : {state_path}")
    print(f"Latest: {latest_path}")
    print(f"CSV   : {csv_path}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
