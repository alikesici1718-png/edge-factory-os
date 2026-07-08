#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Module Consolidation Planner v1

Purpose:
- Read-only scan of edge_factory_os_repo/tools.
- Classify modules into:
  ACTIVE_CORE
  CURRENT_RESEARCH_FRONTIER
  RESEARCH_BRANCH_HISTORY
  CONSOLIDATE_INTO_FRAMEWORK
  ARCHIVE_CANDIDATE
  UNKNOWN_REVIEW
- Produce a consolidation plan before adding many more one-off modules.

This planner does NOT:
- delete files
- move files
- modify runtime
- launch runtime
- patch runtime
- create candidates
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
from typing import Any, Dict, List, Tuple


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
TOOLS_DIR = REPO_DIR / "tools"

OUT_DIR = BASE_DIR / "edge_factory_os_module_consolidation_planner"
OUT_JSON = OUT_DIR / "module_consolidation_plan_latest.json"
OUT_TXT = OUT_DIR / "module_consolidation_plan_latest.txt"
OUT_CSV = OUT_DIR / "module_consolidation_inventory_latest.csv"

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
        for k in row.keys():
            if k not in fields:
                fields.append(k)

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def file_head(path: Path, max_chars: int = 1800) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:max_chars]
    except Exception:
        return ""


def classify_file(path: Path) -> Tuple[str, str, str]:
    name = path.name.lower()
    stem = path.stem.lower()
    text = file_head(path).lower()

    if name.endswith((".bak", ".backup")) or ".bak" in name or "backup" in name:
        return (
            "ARCHIVE_CANDIDATE",
            "Backup or historical copy.",
            "Keep in quarantine/archive if needed; do not treat as active OS module.",
        )

    active_core_tokens = [
        "regression_guard",
        "unified_state_reader",
        "policy_engine",
        "next_action_planner",
        "autopilot_decision_adapter",
        "execution_router",
        "cycle_operator",
        "cycle_runner",
        "control_tower",
        "state_transition_journal",
        "sample_maturity",
        "family_performance",
        "open_pending_aging",
        "error_acknowledger",
        "error_inventory",
    ]

    if any(t in stem for t in active_core_tokens):
        return (
            "ACTIVE_CORE",
            "Runtime/repo governance or safety/state module.",
            "Keep as active core until consolidated into Standard Stack framework.",
        )

    current_frontier_tokens = [
        "data_quality_guard",
        "research_meta_synthesizer_v2",
        "guarded_feature_space_expansion",
        "module_consolidation_planner",
    ]

    if any(t in stem for t in current_frontier_tokens):
        return (
            "CURRENT_RESEARCH_FRONTIER",
            "Current guarded research/frontier or consolidation module.",
            "Keep active; future modules should consume guard feed and consolidation plan.",
        )

    one_off_research_tokens = [
        "market_neutral",
        "calm_market",
        "regime_first",
        "label_free",
        "exit_risk",
        "symbol_cluster",
        "feature_conditioned",
        "broader_month",
        "non_impulse",
        "mean_reversion",
        "month_first",
        "candidate_route",
        "research_direction_contract_builder",
        "offline_research_result_synthesizer",
        "data_quality_panel_bias_audit",
    ]

    if any(t in stem for t in one_off_research_tokens):
        if "contract_builder" in stem or "_runner" in stem or "_evaluator" in stem:
            return (
                "CONSOLIDATE_INTO_FRAMEWORK",
                "One-off contract/runner/evaluator research branch module.",
                "Preserve as historical evidence, but fold pattern into generic ContractRunnerEvaluator framework.",
            )
        return (
            "RESEARCH_BRANCH_HISTORY",
            "Historical research branch support module.",
            "Keep for traceability; do not extend endlessly with new one-off files.",
        )

    framework_tokens = [
        "contract",
        "runner",
        "evaluator",
        "router",
        "scheduler",
        "guard",
        "validator",
        "planner",
        "synthesizer",
    ]

    if any(t in stem for t in framework_tokens):
        return (
            "UNKNOWN_REVIEW",
            "Looks like OS framework/research module but not confidently classified.",
            "Review manually; decide active core vs consolidation candidate.",
        )

    if "read_only" in text or "candidate_generation_allowed" in text:
        return (
            "UNKNOWN_REVIEW",
            "Contains safety/read-only markers but filename does not match known patterns.",
            "Review manually and classify before adding more modules.",
        )

    return (
        "UNKNOWN_REVIEW",
        "No confident classification.",
        "Review manually.",
    )


def infer_module_role(path: Path) -> str:
    stem = path.stem.lower()

    if "contract_builder" in stem:
        return "CONTRACT_BUILDER"
    if stem.endswith("_runner_v1") or "_runner_" in stem:
        return "RUNNER"
    if stem.endswith("_evaluator_v1") or "_evaluator_" in stem:
        return "EVALUATOR"
    if "guard" in stem:
        return "GUARD"
    if "router" in stem:
        return "ROUTER"
    if "planner" in stem:
        return "PLANNER"
    if "synthesizer" in stem:
        return "SYNTHESIZER"
    if "validator" in stem:
        return "VALIDATOR"
    return "OTHER"


def inspect_tools() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    if not TOOLS_DIR.exists():
        return rows

    for path in sorted(TOOLS_DIR.glob("*.py")):
        classification, reason, recommendation = classify_file(path)
        role = infer_module_role(path)

        try:
            size_bytes = path.stat().st_size
            modified_utc = dt.datetime.fromtimestamp(path.stat().st_mtime, tz=dt.timezone.utc).isoformat()
        except Exception:
            size_bytes = None
            modified_utc = None

        rows.append({
            "file_name": path.name,
            "relative_path": str(path.relative_to(REPO_DIR)),
            "module_role": role,
            "classification": classification,
            "reason": reason,
            "recommendation": recommendation,
            "size_bytes": size_bytes,
            "modified_utc": modified_utc,
            "delete_allowed_by_planner": False,
            "move_allowed_by_planner": False,
            "runtime_touch_allowed": False,
        })

    return rows


def summarize(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_class: Dict[str, int] = {}
    by_role: Dict[str, int] = {}

    for row in rows:
        c = row["classification"]
        r = row["module_role"]
        by_class[c] = by_class.get(c, 0) + 1
        by_role[r] = by_role.get(r, 0) + 1

    return {
        "tool_file_count": len(rows),
        "classification_counts": by_class,
        "role_counts": by_role,
        "active_core_count": by_class.get("ACTIVE_CORE", 0),
        "current_frontier_count": by_class.get("CURRENT_RESEARCH_FRONTIER", 0),
        "consolidate_into_framework_count": by_class.get("CONSOLIDATE_INTO_FRAMEWORK", 0),
        "research_branch_history_count": by_class.get("RESEARCH_BRANCH_HISTORY", 0),
        "archive_candidate_count": by_class.get("ARCHIVE_CANDIDATE", 0),
        "unknown_review_count": by_class.get("UNKNOWN_REVIEW", 0),
    }


def build_consolidation_recommendations(summary: Dict[str, Any]) -> List[Dict[str, Any]]:
    recs: List[Dict[str, Any]] = []

    recs.append({
        "priority": 100,
        "recommendation_key": "STOP_ENDLESS_ONE_OFF_MODULE_SPRAWL",
        "title": "Stop adding unlimited one-off research modules",
        "description": (
            "The repo has reached prototype-chain density. Future research should move toward reusable "
            "contract/runner/evaluator frameworks and plugin configs."
        ),
        "action_allowed_now": "READ_ONLY_PLANNING",
        "runtime_touch_allowed": False,
    })

    recs.append({
        "priority": 95,
        "recommendation_key": "BUILD_GENERIC_CONTRACT_RUNNER_EVALUATOR_FRAMEWORK",
        "title": "Build generic ContractRunnerEvaluator framework",
        "description": (
            "Convert repeated builder/runner/evaluator patterns into a reusable framework that consumes JSON contracts, "
            "guard feed, lesson memory, blocklist, and emits standardized latest JSON/TXT/CSV."
        ),
        "action_allowed_now": "REPO_ONLY_OS_INTELLIGENCE",
        "runtime_touch_allowed": False,
    })

    recs.append({
        "priority": 90,
        "recommendation_key": "KEEP_HISTORY_DO_NOT_DELETE",
        "title": "Preserve historical modules as evidence",
        "description": (
            "Do not delete previous branch modules yet. They are audit trail and lesson evidence. "
            "Later move them to archive only after framework can reproduce or reference their outputs."
        ),
        "action_allowed_now": "READ_ONLY_PLANNING",
        "runtime_touch_allowed": False,
    })

    recs.append({
        "priority": 85,
        "recommendation_key": "DEFINE_ACTIVE_CORE_MANIFEST",
        "title": "Define active core manifest",
        "description": (
            "Create a manifest that says which modules are active core, which are current frontier, "
            "and which are historical/consolidation candidates."
        ),
        "action_allowed_now": "REPO_ONLY_OS_INTELLIGENCE",
        "runtime_touch_allowed": False,
    })

    recs.append({
        "priority": 80,
        "recommendation_key": "CONTINUE_RD5_ONLY_AFTER_FRAMEWORK_DECISION",
        "title": "Continue RD5 runner only after consolidation decision",
        "description": (
            "Guarded Feature Space Expansion Runner can be built next, but if created as another 1000-line one-off file, "
            "sprawl continues. Prefer framework skeleton first or make RD5 runner consume the new manifest."
        ),
        "action_allowed_now": "READ_ONLY_OR_REPO_ONLY",
        "runtime_touch_allowed": False,
    })

    return recs


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS MODULE CONSOLIDATION PLANNER v1")
    lines.append("=" * 100)

    for k in [
        "planner_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "tool_file_count",
        "active_core_count",
        "current_frontier_count",
        "consolidate_into_framework_count",
        "research_branch_history_count",
        "archive_candidate_count",
        "unknown_review_count",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("CLASSIFICATION COUNTS")
    lines.append("-" * 100)
    lines.append(json.dumps(result.get("classification_counts", {}), indent=2, ensure_ascii=False))

    lines.append("")
    lines.append("TOP RECOMMENDATIONS")
    lines.append("-" * 100)
    for rec in result.get("consolidation_recommendations", []):
        lines.append(f"{rec.get('priority')} | {rec.get('recommendation_key')}: {rec.get('title')}")
        lines.append(f"  {rec.get('description')}")

    lines.append("")
    lines.append("SAMPLE INVENTORY")
    lines.append("-" * 100)
    for row in result.get("inventory_sample", [])[:40]:
        lines.append(
            f"{row.get('classification')} | {row.get('module_role')} | "
            f"{row.get('relative_path')} | {row.get('recommendation')}"
        )

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
    lines.append(f"inventory_csv: {result.get('inventory_csv')}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS MODULE CONSOLIDATION PLANNER v1")
    print("=" * 100)
    print(f"planner_status: {result.get('planner_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"tool_file_count: {result.get('tool_file_count')}")
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
    print(f"CSV : {result.get('inventory_csv')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = inspect_tools()
    summary = summarize(rows)
    recommendations = build_consolidation_recommendations(summary)

    git_status_short = run_git(["status", "--short"])
    git_branch = run_git(["branch", "--show-current"])
    git_last_commit = run_git(["log", "-1", "--oneline"])

    consolidate_count = summary.get("consolidate_into_framework_count", 0)
    unknown_count = summary.get("unknown_review_count", 0)
    tool_count = summary.get("tool_file_count", 0)

    if tool_count >= 40 or consolidate_count >= 10:
        planner_status = "MODULE_CONSOLIDATION_PLANNER_SPRAWL_ATTENTION"
        severity = "ATTENTION"
        next_action = "BUILD_ACTIVE_CORE_MANIFEST_AND_GENERIC_FRAMEWORK_SKELETON_BEFORE_MORE_ONE_OFF_RUNNERS"
        reason = (
            f"tool_file_count={tool_count}; consolidate_into_framework_count={consolidate_count}; "
            f"unknown_review_count={unknown_count}; repo needs consolidation planning"
        )
    else:
        planner_status = "MODULE_CONSOLIDATION_PLANNER_READY"
        severity = "OK"
        next_action = "OPTIONAL_CONTINUE_CURRENT_RESEARCH_FRONTIER"
        reason = (
            f"tool_file_count={tool_count}; consolidate_into_framework_count={consolidate_count}; "
            "module sprawl not yet severe"
        )

    write_csv(OUT_CSV, rows)

    result = {
        "planner_name": "edge_factory_os_module_consolidation_planner_v1",
        "created_at_utc": utc_now_iso(),
        "planner_status": planner_status,
        "severity": severity,
        "allowed_scope": "READ_ONLY_REPO_INTELLIGENCE",
        "next_action": next_action,
        "reason": reason,
        "strict_policy_key": STRICT_POLICY_KEY,
        "repo_dir": str(REPO_DIR),
        "tools_dir": str(TOOLS_DIR),
        "git_branch": git_branch,
        "git_last_commit": git_last_commit,
        "git_status_short": git_status_short,
        **summary,
        "inventory": rows,
        "inventory_sample": rows[:80],
        "consolidation_recommendations": recommendations,
        "final_architecture_target": {
            "standard_stack_runner": True,
            "research_router": True,
            "contract_builder_framework": True,
            "runner_framework": True,
            "evaluator_framework": True,
            "lesson_memory": True,
            "route_blocklist": True,
            "data_quality_guard_feed": True,
            "research_plugin_configs": True,
            "historical_branch_archive": True,
        },
        "release_gate_feed": {
            "MODULE_CONSOLIDATION_PLANNER_RAN": True,
            "REPO_ONLY_READ_ONLY": True,
            "RUNTIME_TOUCH_ALLOWED_FROM_THIS_PLANNER": False,
            "RELEASE_PASS_FROM_THIS_PLANNER": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_THIS_PLANNER": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_THIS_PLANNER": False,
            "FAMILY_RELEASE_ALLOWED_FROM_THIS_PLANNER": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_THIS_PLANNER": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_THIS_PLANNER": False,
            "ACTIVE_PAPER_ALLOWED_FROM_THIS_PLANNER": False,
            "LIVE_ALLOWED_FROM_THIS_PLANNER": False,
            "REAL_ORDERS_ALLOWED_FROM_THIS_PLANNER": False,
        },
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "inventory_csv": str(OUT_CSV),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text_summary(OUT_TXT, result)
    print_summary(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
