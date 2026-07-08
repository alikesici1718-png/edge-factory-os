#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Active Core Manifest Builder v1

Purpose:
- Consume Module Consolidation Planner v1 output.
- Produce an active/core/frontier/history/consolidation manifest.
- Freeze the current repo architecture map before more one-off modules are added.
- This is read-only repo intelligence.

This builder does NOT:
- delete files
- move files
- archive files
- touch runtime
- launch runtime
- patch runtime
- generate candidates
- release families
- change capital
- start active paper
- enable live
- place real orders
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

PLANNER_JSON = (
    BASE_DIR
    / "edge_factory_os_module_consolidation_planner"
    / "module_consolidation_plan_latest.json"
)

PLANNER_CSV = (
    BASE_DIR
    / "edge_factory_os_module_consolidation_planner"
    / "module_consolidation_inventory_latest.csv"
)

OUT_DIR = BASE_DIR / "edge_factory_os_active_core_manifest"
OUT_JSON = OUT_DIR / "active_core_manifest_latest.json"
OUT_TXT = OUT_DIR / "active_core_manifest_latest.txt"
OUT_CSV = OUT_DIR / "active_core_manifest_inventory_latest.csv"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

SAFETY_FLAGS = {
    "candidate_generation_allowed": False,
    "candidate_contract_allowed": False,
    "family_release_allowed": False,
    "promotion_allowed": False,
    "runtime_touch_allowed": False,
    "launcher_allowed": False,
    "patch_runtime_allowed": False,
    "capital_change_allowed": False,
    "active_paper_allowed": False,
    "live_allowed": False,
    "real_orders_allowed": False,
    "execution_performed": False,
    "file_delete_performed": False,
    "file_move_performed": False,
    "archive_performed": False,
}


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def load_json(path: Path, default: Any = None) -> Any:
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"_load_error": f"{type(e).__name__}: {e}", "_path": str(path)}


def read_csv_rows(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(dict(row))
    except Exception:
        return []
    return rows


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    tmp.replace(path)


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fields: List[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fields:
                fields.append(key)

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run_git(args: List[str]) -> str:
    try:
        p = subprocess.run(
            ["git", *args],
            cwd=str(REPO_DIR),
            capture_output=True,
            text=True,
            timeout=20,
        )
        return (p.stdout or p.stderr or "").strip()
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {e}"


def to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def enrich_manifest_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    enriched: List[Dict[str, Any]] = []

    for row in rows:
        classification = row.get("classification", "UNKNOWN_REVIEW")
        module_role = row.get("module_role", "OTHER")
        relative_path = row.get("relative_path", "")
        file_name = row.get("file_name", "")

        keep_in_active_manifest = classification in {
            "ACTIVE_CORE",
            "CURRENT_RESEARCH_FRONTIER",
            "CONSOLIDATE_INTO_FRAMEWORK",
            "UNKNOWN_REVIEW",
        }

        if classification == "ACTIVE_CORE":
            manifest_bucket = "ACTIVE_CORE"
            lifecycle_action = "KEEP_ACTIVE"
            framework_target = "STANDARD_STACK_OR_CORE_SERVICE"
            priority = 100
        elif classification == "CURRENT_RESEARCH_FRONTIER":
            manifest_bucket = "CURRENT_RESEARCH_FRONTIER"
            lifecycle_action = "KEEP_ACTIVE_UNTIL_NEXT_FRONTIER_DECISION"
            framework_target = "GUARDED_RESEARCH_FRONTIER"
            priority = 90
        elif classification == "CONSOLIDATE_INTO_FRAMEWORK":
            manifest_bucket = "CONSOLIDATE_INTO_FRAMEWORK"
            lifecycle_action = "PRESERVE_THEN_PORT_PATTERN_TO_FRAMEWORK"
            if module_role == "CONTRACT_BUILDER":
                framework_target = "GENERIC_CONTRACT_BUILDER_FRAMEWORK"
            elif module_role == "RUNNER":
                framework_target = "GENERIC_RUNNER_FRAMEWORK"
            elif module_role == "EVALUATOR":
                framework_target = "GENERIC_EVALUATOR_FRAMEWORK"
            else:
                framework_target = "GENERIC_RESEARCH_FRAMEWORK"
            priority = 70
        elif classification == "RESEARCH_BRANCH_HISTORY":
            manifest_bucket = "RESEARCH_BRANCH_HISTORY"
            lifecycle_action = "KEEP_FOR_TRACEABILITY"
            framework_target = "HISTORICAL_ARCHIVE_LATER"
            priority = 50
        elif classification == "ARCHIVE_CANDIDATE":
            manifest_bucket = "ARCHIVE_CANDIDATE"
            lifecycle_action = "DO_NOT_USE_ACTIVE_PATH"
            framework_target = "ARCHIVE_LATER_NO_DELETE_NOW"
            priority = 20
        else:
            manifest_bucket = "UNKNOWN_REVIEW"
            lifecycle_action = "MANUAL_CLASSIFICATION_REQUIRED"
            framework_target = "REVIEW_BEFORE_FRAMEWORK_PORT"
            priority = 40

        enriched.append({
            **row,
            "manifest_bucket": manifest_bucket,
            "lifecycle_action": lifecycle_action,
            "framework_target": framework_target,
            "manifest_priority": priority,
            "keep_in_active_manifest": keep_in_active_manifest,
            "delete_allowed_by_manifest": False,
            "move_allowed_by_manifest": False,
            "archive_allowed_now": False,
            "runtime_touch_allowed": False,
            "notes": f"{file_name} -> {manifest_bucket} / {framework_target}",
        })

    enriched = sorted(
        enriched,
        key=lambda x: (
            -to_int(x.get("manifest_priority"), 0),
            x.get("manifest_bucket", ""),
            x.get("module_role", ""),
            x.get("relative_path", ""),
        ),
    )

    return enriched


def summarize_manifest(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    bucket_counts: Dict[str, int] = {}
    target_counts: Dict[str, int] = {}
    role_counts: Dict[str, int] = {}

    for row in rows:
        bucket = row.get("manifest_bucket", "UNKNOWN")
        target = row.get("framework_target", "UNKNOWN")
        role = row.get("module_role", "UNKNOWN")
        bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
        target_counts[target] = target_counts.get(target, 0) + 1
        role_counts[role] = role_counts.get(role, 0) + 1

    return {
        "manifest_item_count": len(rows),
        "bucket_counts": bucket_counts,
        "framework_target_counts": target_counts,
        "role_counts": role_counts,
        "active_core_count": bucket_counts.get("ACTIVE_CORE", 0),
        "current_frontier_count": bucket_counts.get("CURRENT_RESEARCH_FRONTIER", 0),
        "consolidate_into_framework_count": bucket_counts.get("CONSOLIDATE_INTO_FRAMEWORK", 0),
        "research_branch_history_count": bucket_counts.get("RESEARCH_BRANCH_HISTORY", 0),
        "archive_candidate_count": bucket_counts.get("ARCHIVE_CANDIDATE", 0),
        "unknown_review_count": bucket_counts.get("UNKNOWN_REVIEW", 0),
    }


def build_framework_plan(summary: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            "priority": 100,
            "framework_component": "standard_stack_runner",
            "purpose": "One command to run regression guard, state reader, policy, decision adapter, router, monitor checks.",
            "inputs": ["repo state", "runtime state", "guard feed", "policy config"],
            "outputs": ["standard_stack_latest.json", "stack_pass", "allowed_scope"],
            "should_replace": ["multiple ad hoc stack/check runner scripts"],
        },
        {
            "priority": 95,
            "framework_component": "research_router",
            "purpose": "Choose next research direction from queue, lessons, blocklist, guard feed.",
            "inputs": ["lesson_memory", "candidate_route_blocklist", "guard_feed", "research_queue"],
            "outputs": ["selected_research_contract", "route_hash_preflight"],
            "should_replace": ["one-off research direction contract builders"],
        },
        {
            "priority": 90,
            "framework_component": "generic_contract_builder_framework",
            "purpose": "Create standardized research contracts from plugin configs.",
            "inputs": ["plugin config", "guard feed", "lessons", "blocklist"],
            "outputs": ["contract_latest.json", "contract_latest.txt"],
            "should_replace": ["many edge_factory_os_*_contract_builder_v*.py files"],
        },
        {
            "priority": 85,
            "framework_component": "generic_runner_framework",
            "purpose": "Run read-only research plugins with guard enforcement, canonical months, output schema.",
            "inputs": ["contract", "panel", "guard feed", "plugin config"],
            "outputs": ["runner_latest.json", "CSV outputs", "guard consumption report"],
            "should_replace": ["many edge_factory_os_*_runner_v*.py files"],
        },
        {
            "priority": 80,
            "framework_component": "generic_evaluator_framework",
            "purpose": "Evaluate runner outputs, write lessons/blocklist, route next queue.",
            "inputs": ["runner output", "contract", "lesson memory", "blocklist"],
            "outputs": ["evaluator_latest.json", "lesson", "blocklist update", "next queue"],
            "should_replace": ["many edge_factory_os_*_evaluator_v*.py files"],
        },
        {
            "priority": 75,
            "framework_component": "research_plugin_configs",
            "purpose": "Move one-off research logic into JSON/YAML plugin configs where possible.",
            "inputs": ["feature families", "references", "null controls", "validation policy"],
            "outputs": ["config-driven research runs"],
            "should_replace": ["hard-coded large one-off research modules"],
        },
    ]


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS ACTIVE CORE MANIFEST BUILDER v1")
    lines.append("=" * 100)

    for k in [
        "manifest_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "manifest_item_count",
        "active_core_count",
        "current_frontier_count",
        "consolidate_into_framework_count",
        "research_branch_history_count",
        "archive_candidate_count",
        "unknown_review_count",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("BUCKET COUNTS")
    lines.append("-" * 100)
    lines.append(json.dumps(result.get("bucket_counts", {}), indent=2, ensure_ascii=False))

    lines.append("")
    lines.append("FRAMEWORK PLAN")
    lines.append("-" * 100)
    for item in result.get("framework_plan", []):
        lines.append(f"{item.get('priority')} | {item.get('framework_component')}: {item.get('purpose')}")

    lines.append("")
    lines.append("ACTIVE CORE SAMPLE")
    lines.append("-" * 100)
    for row in result.get("active_core_items", [])[:50]:
        lines.append(f"{row.get('relative_path')} | {row.get('module_role')} | {row.get('lifecycle_action')}")

    lines.append("")
    lines.append("CURRENT FRONTIER SAMPLE")
    lines.append("-" * 100)
    for row in result.get("current_frontier_items", [])[:50]:
        lines.append(f"{row.get('relative_path')} | {row.get('module_role')} | {row.get('lifecycle_action')}")

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        lines.append(f"{k}: {v}")

    lines.append("")
    lines.append("OUTPUT PATHS")
    lines.append("-" * 100)
    lines.append(f"output_json: {result.get('output_json')}")
    lines.append(f"output_txt: {result.get('output_txt')}")
    lines.append(f"manifest_csv: {result.get('manifest_csv')}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS ACTIVE CORE MANIFEST BUILDER v1")
    print("=" * 100)
    print(f"manifest_status: {result.get('manifest_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"manifest_item_count: {result.get('manifest_item_count')}")
    print(f"active_core_count: {result.get('active_core_count')}")
    print(f"current_frontier_count: {result.get('current_frontier_count')}")
    print(f"consolidate_into_framework_count: {result.get('consolidate_into_framework_count')}")
    print(f"research_branch_history_count: {result.get('research_branch_history_count')}")
    print(f"archive_candidate_count: {result.get('archive_candidate_count')}")
    print(f"unknown_review_count: {result.get('unknown_review_count')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"CSV : {result.get('manifest_csv')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    planner = load_json(PLANNER_JSON, default={})
    inventory_rows = read_csv_rows(PLANNER_CSV)

    if not inventory_rows and isinstance(planner.get("inventory"), list):
        inventory_rows = [x for x in planner["inventory"] if isinstance(x, dict)]

    enriched_rows = enrich_manifest_rows(inventory_rows)
    summary = summarize_manifest(enriched_rows)
    framework_plan = build_framework_plan(summary)

    git_status_short = run_git(["status", "--short"])
    git_branch = run_git(["branch", "--show-current"])
    git_last_commit = run_git(["log", "-1", "--oneline"])

    active_core_items = [x for x in enriched_rows if x.get("manifest_bucket") == "ACTIVE_CORE"]
    current_frontier_items = [x for x in enriched_rows if x.get("manifest_bucket") == "CURRENT_RESEARCH_FRONTIER"]
    consolidate_items = [x for x in enriched_rows if x.get("manifest_bucket") == "CONSOLIDATE_INTO_FRAMEWORK"]
    unknown_items = [x for x in enriched_rows if x.get("manifest_bucket") == "UNKNOWN_REVIEW"]

    if summary.get("manifest_item_count", 0) <= 0:
        manifest_status = "ACTIVE_CORE_MANIFEST_BLOCKED_NO_INVENTORY"
        severity = "ATTENTION"
        next_action = "RERUN_MODULE_CONSOLIDATION_PLANNER"
        reason = "No module inventory found."
        return_code = 2
    else:
        manifest_status = "ACTIVE_CORE_MANIFEST_READY"
        severity = "ATTENTION" if summary.get("unknown_review_count", 0) > 0 else "OK"
        next_action = "BUILD_GENERIC_FRAMEWORK_SKELETON_V1"
        reason = (
            f"manifest_item_count={summary.get('manifest_item_count')}; "
            f"active_core={summary.get('active_core_count')}; "
            f"current_frontier={summary.get('current_frontier_count')}; "
            f"consolidate={summary.get('consolidate_into_framework_count')}; "
            f"unknown_review={summary.get('unknown_review_count')}"
        )
        return_code = 0

    write_csv(OUT_CSV, enriched_rows)

    result = {
        "builder_name": "edge_factory_os_active_core_manifest_builder_v1",
        "created_at_utc": utc_now_iso(),
        "manifest_status": manifest_status,
        "severity": severity,
        "allowed_scope": "READ_ONLY_REPO_INTELLIGENCE",
        "next_action": next_action,
        "reason": reason,
        "strict_policy_key": STRICT_POLICY_KEY,
        "repo_dir": str(REPO_DIR),
        "tools_dir": str(REPO_DIR / "tools"),
        "git_branch": git_branch,
        "git_last_commit": git_last_commit,
        "git_status_short": git_status_short,
        **summary,
        "manifest_inventory": enriched_rows,
        "active_core_items": active_core_items,
        "current_frontier_items": current_frontier_items,
        "consolidate_items_sample": consolidate_items[:80],
        "unknown_review_items_sample": unknown_items[:80],
        "framework_plan": framework_plan,
        "architecture_policy": {
            "do_not_delete_history_now": True,
            "do_not_move_files_now": True,
            "new_one_off_modules_should_be_avoided": True,
            "future_research_should_use_guard_feed": True,
            "future_research_should_use_plugin_config": True,
            "framework_skeleton_next": True,
            "candidate_family_runtime_capital_live_still_blocked": True,
        },
        "release_gate_feed": {
            "ACTIVE_CORE_MANIFEST_READY": manifest_status == "ACTIVE_CORE_MANIFEST_READY",
            "REPO_ONLY_READ_ONLY": True,
            "FRAMEWORK_SKELETON_RECOMMENDED": True,
            "RELEASE_PASS_FROM_THIS_MANIFEST": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_THIS_MANIFEST": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_THIS_MANIFEST": False,
            "FAMILY_RELEASE_ALLOWED_FROM_THIS_MANIFEST": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_THIS_MANIFEST": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_THIS_MANIFEST": False,
            "ACTIVE_PAPER_ALLOWED_FROM_THIS_MANIFEST": False,
            "LIVE_ALLOWED_FROM_THIS_MANIFEST": False,
            "REAL_ORDERS_ALLOWED_FROM_THIS_MANIFEST": False,
        },
        "input_paths": {
            "planner_json": str(PLANNER_JSON),
            "planner_csv": str(PLANNER_CSV),
        },
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "manifest_csv": str(OUT_CSV),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text_summary(OUT_TXT, result)
    print_summary(result)
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
