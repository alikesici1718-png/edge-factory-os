#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO = WORKSPACE / "edge_factory_os_repo"
OUT_ROOT = WORKSPACE / "edge_factory_os_repo_source_map_v1"

ACTIVE_RUNTIME_NAMES = {
    "start_edge_factory_MASTER_UPPER_SYSTEM_v5_supervised.ps1",
    "global_paper_risk_manager_v4_config.py",
    "global_paper_risk_manager_v3_priority.py",
    "old_short_gate_aware_live_paper_logger.py",
    "impulse_long_gate_aware_live_paper_logger.py",
    "market_relative_live_paper_logger.py",
    "weak_market_breakdown_short_live_paper_logger.py",
    "edge_factory_os_process_watchdog_v1.py",
    "edge_factory_live_health_check_v5.py",
    "edge_factory_os_command_center_v2_overlay.py",
    "edge_factory_error_classifier_v1.py",
    "edge_factory_error_acknowledger_v1.py",
    "edge_factory_os_autopilot_loop_v4.py",
}

CORE_OS_TOOL_NAMES = {
    "edge_factory_runtime_regression_guard_v1.py",
    "edge_factory_os_unified_state_reader_v1.py",
    "edge_factory_os_policy_engine_v1.py",
    "edge_factory_os_next_action_planner_v1.py",
    "edge_factory_os_memory_lesson_index_v1.py",
    "edge_factory_os_autopilot_decision_adapter_v1.py",
    "edge_factory_os_execution_router_v1.py",
    "edge_factory_os_standard_stack_runner_v1.py",
    "edge_factory_os_self_improvement_planner_v1.py",
    "edge_factory_os_repo_source_map_v1.py",
}

RISKY_PATTERNS = [
    "live_order",
    "place_order",
    "create_order",
    "market_order",
    "private_post",
    "api_key",
    "secret",
    "passphrase",
    "delete",
    "remove",
    "shutil.rmtree",
    "os.remove",
    "unlink",
    "Start-Process",
    "powershell -ExecutionPolicy",
    "capital_change_allowed",
    "live_allowed",
    "active_paper_allowed",
    "patch",
    "launcher",
    "force",
]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

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

def read_text(path: Path, max_bytes: int = 1_000_000) -> str:
    try:
        if path.stat().st_size > max_bytes:
            return path.read_text(encoding="utf-8", errors="replace")[:max_bytes]
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except Exception:
        return str(path)

def classify_by_name(path: Path, text: str) -> tuple[str, str]:
    name = path.name.lower()
    r = rel(path).lower()

    if path.name in ACTIVE_RUNTIME_NAMES:
        return "ACTIVE_RUNTIME", "known active runtime file"

    if path.name in CORE_OS_TOOL_NAMES:
        return "CORE_OS_TOOL", "current OS intelligence/control tool"

    if "backup" in name or "archive" in r or "before_" in name:
        return "ARCHIVE_OR_BACKUP", "backup/archive naming"

    if name.endswith(".ps1"):
        if "start_edge_factory" in name or "launcher" in name:
            return "LAUNCHER_SCRIPT", "powershell launcher"
        return "POWERSHELL_SCRIPT", "powershell script"

    if "patch" in name or "repair" in name:
        return "PATCH_OR_REPAIR_TOOL", "patch/repair naming"

    if "diagnos" in name or "auditor" in name or "preflight" in name or "guard" in name:
        return "DIAGNOSTIC_OR_GUARD", "diagnostic/audit/guard naming"

    if "risk_manager" in name:
        return "RISK_MANAGER", "risk manager naming"

    if "logger" in name or "live_paper" in name or "gate_aware" in name:
        return "LOGGER", "logger naming"

    if "command_center" in name or "watchdog" in name or "autopilot" in name or "supervisor" in name:
        return "OS_SUPERVISION", "OS supervision naming"

    if "candidate" in name or "contract" in name or "selector" in name or "learning" in name:
        return "RESEARCH_CANDIDATE_OS", "candidate/research naming"

    if "offline" in name or "runner" in name or "feature_panel" in name or "validation" in name:
        return "OFFLINE_RESEARCH", "offline/validation naming"

    if path.suffix.lower() in {".json"}:
        return "CONFIG_OR_STATE_COPY", "json file"

    if path.suffix.lower() in {".md"}:
        return "DOCS", "markdown docs"

    return "UNCATEGORIZED", "no rule matched"

def base_family_name(name: str) -> str:
    # Remove version suffixes and common backup markers.
    stem = Path(name).stem
    stem = re.sub(r"_v\d+(_\d+)?$", "", stem)
    stem = re.sub(r"_backup.*$", "", stem)
    stem = re.sub(r"_before.*$", "", stem)
    stem = re.sub(r"_\d{8}_\d{6}$", "", stem)
    return stem

def main() -> int:
    out_dir = OUT_ROOT / f"os_repo_source_map_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = []
    for pattern in ["*.py", "*.ps1", "*.json", "*.md", "*.toml", "*.yml", "*.yaml"]:
        files.extend(REPO.rglob(pattern))

    rows = []
    duplicate_groups = defaultdict(list)
    risky_rows = []

    for p in sorted(set(files)):
        if ".git" in p.parts or "__pycache__" in p.parts:
            continue

        text = read_text(p)
        category, reason = classify_by_name(p, text)
        base = base_family_name(p.name)
        duplicate_groups[base].append(rel(p))

        hits = []
        lower_text = text.lower()
        for pat in RISKY_PATTERNS:
            if pat.lower() in lower_text or pat.lower() in p.name.lower():
                hits.append(pat)

        line_count = text.count("\n") + 1 if text else 0
        size = p.stat().st_size if p.exists() else 0

        row = {
            "path": rel(p),
            "name": p.name,
            "suffix": p.suffix,
            "category": category,
            "reason": reason,
            "base_family": base,
            "size_bytes": size,
            "line_count": line_count,
            "risky_hit_count": len(hits),
            "risky_hits": "|".join(sorted(set(hits))),
            "is_active_runtime": p.name in ACTIVE_RUNTIME_NAMES,
            "is_core_os_tool": p.name in CORE_OS_TOOL_NAMES,
        }
        rows.append(row)

        if hits:
            risky_rows.append(row)

    category_counts = Counter(r["category"] for r in rows)

    duplicate_summary = []
    for base, paths in duplicate_groups.items():
        if len(paths) >= 2:
            duplicate_summary.append({
                "base_family": base,
                "count": len(paths),
                "paths": paths,
            })

    duplicate_summary = sorted(duplicate_summary, key=lambda x: x["count"], reverse=True)

    active_missing = sorted([x for x in ACTIVE_RUNTIME_NAMES if not any(r["name"] == x for r in rows)])
    core_missing = sorted([x for x in CORE_OS_TOOL_NAMES if not any(r["name"] == x for r in rows)])

    git_status = run(["git", "status", "--short"], cwd=REPO)
    git_dirty = bool(git_status["stdout"].strip())

    map_status = "REPO_SOURCE_MAP_READY"
    attention = []

    if active_missing:
        attention.append("ACTIVE_RUNTIME_FILE_MISSING_FROM_REPO_COPY")
    if core_missing:
        attention.append("CORE_OS_TOOL_MISSING_FROM_REPO")
    if git_dirty:
        attention.append("REPO_DIRTY_EXPECTED_IF_NEW_MAP_SCRIPT_UNCOMMITTED")

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),
        "map_status": map_status,
        "file_count": len(rows),
        "category_counts": dict(category_counts),
        "risky_file_count": len(risky_rows),
        "duplicate_group_count": len(duplicate_summary),
        "active_runtime_known_count": len(ACTIVE_RUNTIME_NAMES),
        "active_runtime_missing": active_missing,
        "core_os_tool_known_count": len(CORE_OS_TOOL_NAMES),
        "core_os_tool_missing": core_missing,
        "attention": attention,
        "git_dirty": git_dirty,
        "git_status_short": git_status["stdout"].strip(),
        "runtime_touch_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "execution_performed": False,
        "next_action": "REVIEW_SOURCE_MAP_THEN_BUILD_ARTIFACT_FRESHNESS_INDEX",
    }

    state_path = out_dir / "os_repo_source_map_v1_state.json"
    latest_path = OUT_ROOT / "os_repo_source_map_latest.json"
    files_csv = out_dir / "os_repo_source_map_v1_files.csv"
    risky_csv = out_dir / "os_repo_source_map_v1_risky_files.csv"
    duplicates_csv = out_dir / "os_repo_source_map_v1_duplicate_groups.csv"
    report_path = out_dir / "os_repo_source_map_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    with files_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "path", "name", "suffix", "category", "reason", "base_family",
                "size_bytes", "line_count", "risky_hit_count", "risky_hits",
                "is_active_runtime", "is_core_os_tool",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    with risky_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "path", "name", "suffix", "category", "reason", "base_family",
                "size_bytes", "line_count", "risky_hit_count", "risky_hits",
                "is_active_runtime", "is_core_os_tool",
            ],
        )
        writer.writeheader()
        writer.writerows(risky_rows)

    with duplicates_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["base_family", "count", "paths"])
        writer.writeheader()
        for d in duplicate_summary:
            writer.writerow({
                "base_family": d["base_family"],
                "count": d["count"],
                "paths": "|".join(d["paths"]),
            })

    md = []
    md.append("# Edge Factory OS Repo Source Map v1")
    md.append("")
    md.append(f"map_status: `{map_status}`")
    md.append(f"file_count: `{len(rows)}`")
    md.append(f"risky_file_count: `{len(risky_rows)}`")
    md.append(f"duplicate_group_count: `{len(duplicate_summary)}`")
    md.append("")
    md.append("## Category counts")
    for k, v in sorted(category_counts.items()):
        md.append(f"- `{k}`: `{v}`")
    md.append("")
    md.append("## Attention")
    if attention:
        for a in attention:
            md.append(f"- `{a}`")
    else:
        md.append("- `NONE`")
    md.append("")
    md.append("## Top duplicate groups")
    for d in duplicate_summary[:20]:
        md.append(f"- `{d['base_family']}` count=`{d['count']}`")
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

    print("EDGE FACTORY OS REPO SOURCE MAP v1")
    print("=" * 100)
    print(f"map_status: {map_status}")
    print(f"file_count: {len(rows)}")
    print(f"risky_file_count: {len(risky_rows)}")
    print(f"duplicate_group_count: {len(duplicate_summary)}")
    print(f"active_runtime_missing: {len(active_missing)}")
    print(f"core_os_tool_missing: {len(core_missing)}")
    print(f"git_dirty: {git_dirty}")
    print("runtime_touch_allowed: False")
    print("launcher_allowed     : False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed : False")
    print("live_allowed         : False")
    print("capital_change_allowed: False")
    print("execution_performed  : False")
    print()
    print("CATEGORY COUNTS")
    print("-" * 100)
    for k, v in sorted(category_counts.items()):
        print(f"{k}: {v}")
    print()
    print("ATTENTION")
    print("-" * 100)
    print("\n".join(f"- {a}" for a in attention) if attention else "NONE")
    print()
    print("TOP DUPLICATE GROUPS")
    print("-" * 100)
    for d in duplicate_summary[:20]:
        print(f"{d['base_family']}: {d['count']}")
    print()
    print(f"State     : {state_path}")
    print(f"Latest    : {latest_path}")
    print(f"Files     : {files_csv}")
    print(f"Risky     : {risky_csv}")
    print(f"Duplicates: {duplicates_csv}")
    print(f"Report    : {report_path}")

if __name__ == "__main__":
    main()
