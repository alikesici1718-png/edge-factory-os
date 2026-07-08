#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Generic Framework Skeleton v1

Purpose:
- Consume Active Core Manifest v1.
- Create a repo-only, non-runtime framework skeleton plan.
- Create directories and starter JSON configs for the future generic framework.
- Do not modify existing modules.
- Do not delete/move/archive files.
- Do not touch runtime/live/capital/family/candidate systems.

This skeleton creates:
- framework manifest
- schema stubs
- plugin config stubs
- framework directory plan
- migration map from one-off modules to framework targets

This does NOT:
- replace active modules yet
- run research
- generate candidates
- release families
- touch runtime
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

ACTIVE_CORE_MANIFEST_JSON = (
    BASE_DIR
    / "edge_factory_os_active_core_manifest"
    / "active_core_manifest_latest.json"
)

ACTIVE_CORE_MANIFEST_CSV = (
    BASE_DIR
    / "edge_factory_os_active_core_manifest"
    / "active_core_manifest_inventory_latest.csv"
)

OUT_DIR = BASE_DIR / "edge_factory_os_generic_framework_skeleton"
OUT_JSON = OUT_DIR / "generic_framework_skeleton_latest.json"
OUT_TXT = OUT_DIR / "generic_framework_skeleton_latest.txt"
OUT_MIGRATION_CSV = OUT_DIR / "generic_framework_migration_map_latest.csv"

FRAMEWORK_DIR = REPO_DIR / "edge_factory_os_framework"
SCHEMA_DIR = FRAMEWORK_DIR / "schemas"
PLUGIN_DIR = FRAMEWORK_DIR / "plugins"
CORE_DIR = FRAMEWORK_DIR / "core"
DOCS_DIR = FRAMEWORK_DIR / "docs"

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


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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


def ensure_dirs() -> List[str]:
    created_or_present = []
    for d in [FRAMEWORK_DIR, SCHEMA_DIR, PLUGIN_DIR, CORE_DIR, DOCS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
        created_or_present.append(str(d.relative_to(REPO_DIR)))
    return created_or_present


def build_schema_stubs() -> Dict[str, Dict[str, Any]]:
    return {
        "research_contract_schema_v1.json": {
            "schema_name": "research_contract_schema_v1",
            "required_fields": [
                "contract_id",
                "contract_hash",
                "research_key",
                "direction_queue_key",
                "strict_policy_key",
                "canonical_policy_month_count",
                "guard_feed_path",
                "blocked_route_preflight_required",
                "plugin_config_path",
                "safety_flags",
            ],
            "safety_defaults": SAFETY_FLAGS,
            "notes": "Starter schema only. Enforce in future framework validator.",
        },
        "runner_output_schema_v1.json": {
            "schema_name": "runner_output_schema_v1",
            "required_fields": [
                "runner_status",
                "allowed_scope",
                "strict_policy_key",
                "canonical_policy_month_count",
                "guard_consumption_report",
                "result_metrics",
                "release_gate_feed",
                "safety_flags",
            ],
            "safety_defaults": SAFETY_FLAGS,
            "notes": "Starter schema only. Runner framework will validate outputs.",
        },
        "evaluator_output_schema_v1.json": {
            "schema_name": "evaluator_output_schema_v1",
            "required_fields": [
                "evaluator_status",
                "branch_closed",
                "lesson_written",
                "blocklist_written",
                "next_recommended_research_key",
                "next_module",
                "release_gate_feed",
                "safety_flags",
            ],
            "safety_defaults": SAFETY_FLAGS,
            "notes": "Starter schema only. Evaluator framework will validate outputs.",
        },
        "plugin_config_schema_v1.json": {
            "schema_name": "plugin_config_schema_v1",
            "required_fields": [
                "plugin_key",
                "plugin_type",
                "feature_families",
                "negative_controls",
                "null_models",
                "forbidden_inputs",
                "required_guards",
                "output_tables",
            ],
            "notes": "Research logic should move from large one-off modules into plugin config where possible.",
        },
    }


def build_plugin_stubs() -> Dict[str, Dict[str, Any]]:
    return {
        "guarded_feature_space_expansion_plugin_v1.json": {
            "plugin_key": "GUARDED_FEATURE_SPACE_EXPANSION_PLUGIN_V1",
            "plugin_type": "READ_ONLY_DIAGNOSTIC_RESEARCH",
            "research_key": "GUARDED_FEATURE_SPACE_EXPANSION_AND_NEGATIVE_CONTROL_SEARCH_V1",
            "must_consume_guard_feed": True,
            "must_not_reopen_blocked_routes": True,
            "strict_policy_key": STRICT_POLICY_KEY,
            "canonical_policy_month_count": 12,
            "feature_families": [
                "pre_outcome_multi_horizon_return_shape",
                "pre_outcome_realized_volatility_surface",
                "pre_outcome_range_compression_expansion",
                "pre_outcome_liquidity_state_and_rank_stability",
                "pre_outcome_cross_sectional_dispersion",
                "pre_outcome_market_beta_correlation",
                "pre_outcome_symbol_lifecycle_and_coverage",
                "gap_aware_feature_resets",
            ],
            "negative_controls": [
                "random_symbol_feature_control",
                "month_shuffled_feature_control",
                "time_shifted_feature_control",
                "random_noise_feature_control",
                "direction_flipped_label_control",
            ],
            "null_models": [
                "within_month_symbol_shuffle",
                "month_order_shuffle",
                "feature_rank_shuffle",
                "side_label_shuffle",
                "cost_perturbation_null",
            ],
            "forbidden_inputs": [
                "future_return_as_feature",
                "future_pnl_as_feature",
                "future_win_loss_as_feature",
                "manual_symbol_whitelist",
                "manual_month_blacklist",
                "blocked_route_hash_reuse",
            ],
            "candidate_generation_allowed": False,
            "family_release_allowed": False,
            "runtime_touch_allowed": False,
            "capital_change_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
        }
    }


def build_core_stub_files() -> Dict[str, str]:
    return {
        "README_framework_skeleton.md": """# Edge Factory OS Framework Skeleton v1

This directory is a repo-only framework skeleton.

It is not yet the active runtime system.

Goals:
- reduce one-off module sprawl
- standardize contract/runner/evaluator schemas
- enforce data-quality guard feed consumption
- preserve lesson memory and blocklist discipline
- move future research into plugin configs where possible

Hard safety:
- no candidate generation
- no family release
- no runtime touch
- no capital change
- no active paper/live
- no real orders
""",
        "core/README_core_framework.md": """# Core Framework Target

Planned components:
- Standard Stack Runner
- Research Router
- Generic Contract Builder
- Generic Runner
- Generic Evaluator
- Lesson Memory Adapter
- Route Blocklist Adapter
- Data Quality Guard Adapter

This folder currently contains planning stubs only.
""",
        "plugins/README_plugins.md": """# Research Plugin Configs

Future research should move from one-off Python modules into plugin configs where practical.

Plugin configs must declare:
- feature families
- negative controls
- null models
- forbidden inputs
- guard requirements
- output schemas
""",
        "schemas/README_schemas.md": """# Framework Schemas

Starter schemas:
- research_contract_schema_v1.json
- runner_output_schema_v1.json
- evaluator_output_schema_v1.json
- plugin_config_schema_v1.json

These are planning schemas and should be hardened before becoming enforcement code.
""",
    }


def build_migration_map(manifest_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    migration_rows: List[Dict[str, Any]] = []

    for row in manifest_rows:
        bucket = row.get("manifest_bucket")
        role = row.get("module_role")
        target = row.get("framework_target")
        rel = row.get("relative_path")

        if bucket not in {
            "ACTIVE_CORE",
            "CURRENT_RESEARCH_FRONTIER",
            "CONSOLIDATE_INTO_FRAMEWORK",
            "UNKNOWN_REVIEW",
        }:
            continue

        if bucket == "ACTIVE_CORE":
            migration_phase = "PHASE_1_KEEP_AND_WRAP"
            migration_action = "Wrap active module behind Standard Stack/Core manifest; do not rewrite yet."
        elif bucket == "CURRENT_RESEARCH_FRONTIER":
            migration_phase = "PHASE_2_KEEP_FRONTIER_GUARDED"
            migration_action = "Keep current frontier modules active until framework runner can consume plugin config."
        elif bucket == "CONSOLIDATE_INTO_FRAMEWORK":
            migration_phase = "PHASE_3_PORT_PATTERN"
            migration_action = "Extract reusable contract/runner/evaluator pattern into generic framework."
        else:
            migration_phase = "PHASE_0_MANUAL_REVIEW"
            migration_action = "Manual review required before port/archive decision."

        migration_rows.append({
            "relative_path": rel,
            "file_name": row.get("file_name"),
            "module_role": role,
            "manifest_bucket": bucket,
            "framework_target": target,
            "migration_phase": migration_phase,
            "migration_action": migration_action,
            "delete_allowed_now": False,
            "move_allowed_now": False,
            "runtime_touch_allowed": False,
        })

    return migration_rows


def write_framework_files(schema_stubs: Dict[str, Any], plugin_stubs: Dict[str, Any], core_stubs: Dict[str, str]) -> Dict[str, List[str]]:
    written = {
        "schemas": [],
        "plugins": [],
        "docs": [],
        "core_docs": [],
    }

    for file_name, payload in schema_stubs.items():
        path = SCHEMA_DIR / file_name
        write_json(path, payload)
        written["schemas"].append(str(path.relative_to(REPO_DIR)))

    for file_name, payload in plugin_stubs.items():
        path = PLUGIN_DIR / file_name
        write_json(path, payload)
        written["plugins"].append(str(path.relative_to(REPO_DIR)))

    for rel_path, text in core_stubs.items():
        path = FRAMEWORK_DIR / rel_path
        write_text(path, text)
        if "core/" in rel_path:
            written["core_docs"].append(str(path.relative_to(REPO_DIR)))
        else:
            written["docs"].append(str(path.relative_to(REPO_DIR)))

    return written


def write_summary_text(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS GENERIC FRAMEWORK SKELETON v1")
    lines.append("=" * 100)

    for k in [
        "skeleton_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "framework_dir",
        "schema_stub_count",
        "plugin_stub_count",
        "migration_map_count",
        "active_core_count",
        "current_frontier_count",
        "consolidate_into_framework_count",
        "unknown_review_count",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("WRITTEN FRAMEWORK FILES")
    lines.append("-" * 100)
    lines.append(json.dumps(result.get("written_framework_files", {}), indent=2, ensure_ascii=False))

    lines.append("")
    lines.append("FRAMEWORK COMPONENTS")
    lines.append("-" * 100)
    for item in result.get("framework_components", []):
        lines.append(f"- {item.get('component_key')}: {item.get('purpose')}")

    lines.append("")
    lines.append("NEXT STEPS")
    lines.append("-" * 100)
    for item in result.get("recommended_next_steps", []):
        lines.append(f"{item.get('priority')} | {item.get('step_key')}: {item.get('description')}")

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
    lines.append(f"migration_csv: {result.get('migration_csv')}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS GENERIC FRAMEWORK SKELETON v1")
    print("=" * 100)
    print(f"skeleton_status: {result.get('skeleton_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"framework_dir: {result.get('framework_dir')}")
    print(f"schema_stub_count: {result.get('schema_stub_count')}")
    print(f"plugin_stub_count: {result.get('plugin_stub_count')}")
    print(f"migration_map_count: {result.get('migration_map_count')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"CSV : {result.get('migration_csv')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest = load_json(ACTIVE_CORE_MANIFEST_JSON, default={})
    manifest_rows = read_csv_rows(ACTIVE_CORE_MANIFEST_CSV)

    if not manifest_rows and isinstance(manifest.get("manifest_inventory"), list):
        manifest_rows = [x for x in manifest["manifest_inventory"] if isinstance(x, dict)]

    manifest_ready = manifest.get("manifest_status") == "ACTIVE_CORE_MANIFEST_READY"

    dirs = ensure_dirs()
    schema_stubs = build_schema_stubs()
    plugin_stubs = build_plugin_stubs()
    core_stubs = build_core_stub_files()
    written_files = write_framework_files(schema_stubs, plugin_stubs, core_stubs)

    migration_map = build_migration_map(manifest_rows)
    write_csv(OUT_MIGRATION_CSV, migration_map)

    bucket_counts = manifest.get("bucket_counts", {}) if isinstance(manifest.get("bucket_counts"), dict) else {}

    framework_components = [
        {
            "component_key": "standard_stack_runner",
            "purpose": "Unify existing stack/regression/state/policy/router checks behind one framework entrypoint.",
            "status": "SKELETON_DEFINED",
        },
        {
            "component_key": "research_router",
            "purpose": "Select next research plugin using guard feed, lessons, blocklist, and route preflight.",
            "status": "SKELETON_DEFINED",
        },
        {
            "component_key": "generic_contract_builder",
            "purpose": "Build standardized contracts from plugin configs.",
            "status": "SKELETON_DEFINED",
        },
        {
            "component_key": "generic_runner",
            "purpose": "Run read-only research plugins with guard enforcement and schema validation.",
            "status": "SKELETON_DEFINED",
        },
        {
            "component_key": "generic_evaluator",
            "purpose": "Evaluate outputs, write lessons/blocklists, and queue next action.",
            "status": "SKELETON_DEFINED",
        },
        {
            "component_key": "plugin_configs",
            "purpose": "Move research logic into declarative configs when possible.",
            "status": "SKELETON_DEFINED",
        },
    ]

    recommended_next_steps = [
        {
            "priority": 100,
            "step_key": "BUILD_FRAMEWORK_README_AND_ROUTER_SPEC",
            "description": "Create a framework router spec before porting old modules.",
            "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        },
        {
            "priority": 95,
            "step_key": "BUILD_GENERIC_CONTRACT_BUILDER_MINIMAL_RUNTIME",
            "description": "Implement a minimal generic contract builder that reads plugin config and guard feed.",
            "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        },
        {
            "priority": 90,
            "step_key": "PORT_RD5_TO_PLUGIN_CONFIG",
            "description": "Run RD5 guarded feature-space expansion through plugin config rather than another isolated one-off runner.",
            "allowed_scope": "READ_ONLY_RESEARCH",
        },
    ]

    if manifest_ready and len(migration_map) > 0:
        skeleton_status = "GENERIC_FRAMEWORK_SKELETON_READY"
        severity = "ATTENTION"
        next_action = "BUILD_FRAMEWORK_ROUTER_SPEC_OR_PORT_RD5_TO_PLUGIN_CONFIG"
        reason = (
            f"manifest_ready=True; schema_stub_count={len(schema_stubs)}; "
            f"plugin_stub_count={len(plugin_stubs)}; migration_map_count={len(migration_map)}"
        )
        return_code = 0
    else:
        skeleton_status = "GENERIC_FRAMEWORK_SKELETON_ATTENTION_INCOMPLETE_MANIFEST"
        severity = "ATTENTION"
        next_action = "INSPECT_ACTIVE_CORE_MANIFEST_BEFORE_FRAMEWORK_BUILD"
        reason = f"manifest_ready={manifest_ready}; migration_map_count={len(migration_map)}"
        return_code = 2

    git_status_short = run_git(["status", "--short"])
    git_branch = run_git(["branch", "--show-current"])
    git_last_commit = run_git(["log", "-1", "--oneline"])

    result = {
        "builder_name": "edge_factory_os_generic_framework_skeleton_v1",
        "created_at_utc": utc_now_iso(),
        "skeleton_status": skeleton_status,
        "severity": severity,
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "next_action": next_action,
        "reason": reason,
        "strict_policy_key": STRICT_POLICY_KEY,
        "repo_dir": str(REPO_DIR),
        "framework_dir": str(FRAMEWORK_DIR),
        "created_or_verified_dirs": dirs,
        "git_branch": git_branch,
        "git_last_commit": git_last_commit,
        "git_status_short": git_status_short,
        "schema_stub_count": len(schema_stubs),
        "plugin_stub_count": len(plugin_stubs),
        "migration_map_count": len(migration_map),
        "active_core_count": bucket_counts.get("ACTIVE_CORE", manifest.get("active_core_count")),
        "current_frontier_count": bucket_counts.get("CURRENT_RESEARCH_FRONTIER", manifest.get("current_frontier_count")),
        "consolidate_into_framework_count": bucket_counts.get("CONSOLIDATE_INTO_FRAMEWORK", manifest.get("consolidate_into_framework_count")),
        "unknown_review_count": bucket_counts.get("UNKNOWN_REVIEW", manifest.get("unknown_review_count")),
        "written_framework_files": written_files,
        "schema_stubs": schema_stubs,
        "plugin_stubs": plugin_stubs,
        "framework_components": framework_components,
        "recommended_next_steps": recommended_next_steps,
        "migration_map_sample": migration_map[:80],
        "architecture_policy": {
            "historical_modules_preserved": True,
            "delete_allowed_now": False,
            "move_allowed_now": False,
            "archive_allowed_now": False,
            "future_one_off_modules_discouraged": True,
            "future_research_should_use_plugin_config": True,
            "future_research_must_consume_guard_feed": True,
            "candidate_family_runtime_capital_live_still_blocked": True,
        },
        "release_gate_feed": {
            "GENERIC_FRAMEWORK_SKELETON_READY": skeleton_status == "GENERIC_FRAMEWORK_SKELETON_READY",
            "REPO_ONLY_OS_INTELLIGENCE": True,
            "RELEASE_PASS_FROM_THIS_SKELETON": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_THIS_SKELETON": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_THIS_SKELETON": False,
            "FAMILY_RELEASE_ALLOWED_FROM_THIS_SKELETON": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_THIS_SKELETON": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_THIS_SKELETON": False,
            "ACTIVE_PAPER_ALLOWED_FROM_THIS_SKELETON": False,
            "LIVE_ALLOWED_FROM_THIS_SKELETON": False,
            "REAL_ORDERS_ALLOWED_FROM_THIS_SKELETON": False,
        },
        "input_paths": {
            "active_core_manifest_json": str(ACTIVE_CORE_MANIFEST_JSON),
            "active_core_manifest_csv": str(ACTIVE_CORE_MANIFEST_CSV),
        },
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "migration_csv": str(OUT_MIGRATION_CSV),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_summary_text(OUT_TXT, result)
    print_summary(result)
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
