#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Framework Router Spec Builder v1

Purpose:
- Consume Generic Framework Skeleton v1.
- Consume Active Core Manifest v1.
- Consume Data Quality Guard feed.
- Consume framework plugin configs.
- Build a repo-only router specification for future generic research routing.
- This is the bridge from one-off module sprawl to plugin/config-driven research.

This builder does NOT:
- run research
- generate candidates
- create candidate contracts
- release families
- touch runtime
- change capital
- start active paper
- enable live
- place real orders
- delete/move/archive files
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

FRAMEWORK_DIR = REPO_DIR / "edge_factory_os_framework"
CORE_DIR = FRAMEWORK_DIR / "core"
PLUGIN_DIR = FRAMEWORK_DIR / "plugins"
SCHEMA_DIR = FRAMEWORK_DIR / "schemas"

SKELETON_JSON = BASE_DIR / "edge_factory_os_generic_framework_skeleton" / "generic_framework_skeleton_latest.json"
ACTIVE_MANIFEST_JSON = BASE_DIR / "edge_factory_os_active_core_manifest" / "active_core_manifest_latest.json"
GUARD_FEED_JSON = BASE_DIR / "edge_factory_os_data_quality_guard_runner" / "data_quality_guard_feed_latest.json"
LESSON_INDEX_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

OUT_DIR = BASE_DIR / "edge_factory_os_framework_router_spec"
OUT_JSON = OUT_DIR / "framework_router_spec_latest.json"
OUT_TXT = OUT_DIR / "framework_router_spec_latest.txt"

REPO_ROUTER_SPEC_JSON = CORE_DIR / "research_router_spec_v1.json"
REPO_ROUTER_README = CORE_DIR / "README_research_router_spec_v1.md"

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


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    tmp.replace(path)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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


def stable_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def list_plugin_configs() -> List[Dict[str, Any]]:
    configs: List[Dict[str, Any]] = []

    if not PLUGIN_DIR.exists():
        return configs

    for path in sorted(PLUGIN_DIR.glob("*.json")):
        payload = load_json(path, default={})
        configs.append({
            "plugin_path": str(path.relative_to(REPO_DIR)),
            "plugin_key": payload.get("plugin_key"),
            "plugin_type": payload.get("plugin_type"),
            "research_key": payload.get("research_key"),
            "must_consume_guard_feed": bool(payload.get("must_consume_guard_feed")),
            "must_not_reopen_blocked_routes": bool(payload.get("must_not_reopen_blocked_routes")),
            "strict_policy_key": payload.get("strict_policy_key"),
            "canonical_policy_month_count": payload.get("canonical_policy_month_count"),
            "candidate_generation_allowed": bool(payload.get("candidate_generation_allowed")),
            "family_release_allowed": bool(payload.get("family_release_allowed")),
            "runtime_touch_allowed": bool(payload.get("runtime_touch_allowed")),
            "capital_change_allowed": bool(payload.get("capital_change_allowed")),
            "live_allowed": bool(payload.get("live_allowed")),
            "real_orders_allowed": bool(payload.get("real_orders_allowed")),
            "feature_family_count": len(payload.get("feature_families", [])) if isinstance(payload.get("feature_families"), list) else 0,
            "negative_control_count": len(payload.get("negative_controls", [])) if isinstance(payload.get("negative_controls"), list) else 0,
            "null_model_count": len(payload.get("null_models", [])) if isinstance(payload.get("null_models"), list) else 0,
            "payload": payload,
        })

    return configs


def extract_lessons_count(obj: Any) -> int:
    if isinstance(obj, dict) and isinstance(obj.get("lessons"), list):
        return len(obj["lessons"])
    if isinstance(obj, list):
        return len([x for x in obj if isinstance(x, dict)])
    return 0


def extract_blocked_count(obj: Any) -> int:
    if isinstance(obj, dict) and isinstance(obj.get("blocked_routes"), list):
        return len(obj["blocked_routes"])
    if isinstance(obj, list):
        return len([x for x in obj if isinstance(x, dict)])
    return 0


def select_default_plugin(plugin_configs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    valid = []
    for cfg in plugin_configs:
        if (
            cfg.get("must_consume_guard_feed") is True
            and cfg.get("must_not_reopen_blocked_routes") is True
            and cfg.get("strict_policy_key") == STRICT_POLICY_KEY
            and int(cfg.get("canonical_policy_month_count") or 0) == 12
            and cfg.get("candidate_generation_allowed") is False
            and cfg.get("family_release_allowed") is False
            and cfg.get("runtime_touch_allowed") is False
            and cfg.get("capital_change_allowed") is False
            and cfg.get("live_allowed") is False
            and cfg.get("real_orders_allowed") is False
        ):
            valid.append(cfg)

    if not valid:
        return None

    valid = sorted(
        valid,
        key=lambda x: (
            x.get("research_key") != "GUARDED_FEATURE_SPACE_EXPANSION_AND_NEGATIVE_CONTROL_SEARCH_V1",
            -int(x.get("negative_control_count") or 0),
            -int(x.get("null_model_count") or 0),
            str(x.get("plugin_key")),
        ),
    )
    return valid[0]


def build_router_spec(
    skeleton: Dict[str, Any],
    active_manifest: Dict[str, Any],
    guard_feed: Dict[str, Any],
    plugin_configs: List[Dict[str, Any]],
    selected_plugin: Optional[Dict[str, Any]],
    lesson_count: int,
    blocked_route_count: int,
) -> Dict[str, Any]:
    guard_pass = bool(guard_feed.get("guard_pass"))
    meta_allowed = bool(guard_feed.get("research_meta_synthesis_allowed"))
    framework_ready = skeleton.get("skeleton_status") == "GENERIC_FRAMEWORK_SKELETON_READY"
    manifest_ready = active_manifest.get("manifest_status") == "ACTIVE_CORE_MANIFEST_READY"

    router_ready = bool(
        framework_ready
        and manifest_ready
        and guard_pass
        and meta_allowed
        and selected_plugin is not None
    )

    router_hash = stable_hash({
        "framework_ready": framework_ready,
        "manifest_ready": manifest_ready,
        "guard_pass": guard_pass,
        "meta_allowed": meta_allowed,
        "selected_plugin": selected_plugin.get("plugin_key") if selected_plugin else None,
        "lesson_count": lesson_count,
        "blocked_route_count": blocked_route_count,
    })

    return {
        "spec_name": "edge_factory_os_framework_research_router_spec_v1",
        "created_at_utc": utc_now_iso(),
        "router_spec_hash": router_hash,
        "router_ready": router_ready,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "framework_ready": framework_ready,
        "active_manifest_ready": manifest_ready,
        "data_quality_guard_pass": guard_pass,
        "research_meta_synthesis_allowed": meta_allowed,
        "plugin_config_count": len(plugin_configs),
        "selected_plugin_key": selected_plugin.get("plugin_key") if selected_plugin else None,
        "selected_plugin_path": selected_plugin.get("plugin_path") if selected_plugin else None,
        "selected_research_key": selected_plugin.get("research_key") if selected_plugin else None,
        "lesson_count": lesson_count,
        "blocked_route_count": blocked_route_count,
        "router_order": [
            "load_active_core_manifest",
            "load_data_quality_guard_feed",
            "load_lesson_memory",
            "load_route_blocklist",
            "load_plugin_configs",
            "validate_plugin_safety_flags",
            "validate_plugin_guard_requirements",
            "route_hash_preflight_against_blocklist",
            "build_generic_research_contract",
            "hand_to_generic_runner_framework",
            "hand_to_generic_evaluator_framework",
        ],
        "hard_blocks": [
            {
                "block_key": "DATA_QUALITY_GUARD_NOT_PASS",
                "condition": "guard_pass != True",
                "effect": "block all research routing",
            },
            {
                "block_key": "PLUGIN_SAFETY_FLAG_OPEN",
                "condition": "plugin candidate/family/runtime/capital/live/real_order flag is True",
                "effect": "reject plugin",
            },
            {
                "block_key": "BLOCKED_ROUTE_HASH_REUSE",
                "condition": "route_hash in candidate_route_blocklist",
                "effect": "reject contract",
            },
            {
                "block_key": "CANONICAL_MONTH_POLICY_NOT_12",
                "condition": "canonical_policy_month_count != 12",
                "effect": "reject research contract",
            },
            {
                "block_key": "MISSING_NEGATIVE_CONTROLS_OR_NULL_MODELS",
                "condition": "plugin lacks negative controls or null models",
                "effect": "diagnostic research not allowed",
            },
        ],
        "contract_builder_handoff": {
            "next_framework_component": "generic_contract_builder",
            "recommended_builder_module": "edge_factory_os_generic_research_contract_builder_v1.py",
            "selected_plugin_path": selected_plugin.get("plugin_path") if selected_plugin else None,
            "guard_feed_path": str(GUARD_FEED_JSON),
            "lesson_index_path": str(LESSON_INDEX_PATH),
            "blocklist_path": str(BLOCKLIST_PATH),
            "schema_path": str((SCHEMA_DIR / "research_contract_schema_v1.json").relative_to(REPO_DIR)),
        },
        "safety_policy": {
            "router_can_select_plugin": router_ready,
            "router_can_run_research": False,
            "router_can_generate_candidate": False,
            "router_can_release_family": False,
            "router_can_touch_runtime": False,
            "router_can_change_capital": False,
            "router_can_enable_live": False,
            "router_can_place_real_orders": False,
        },
        "plugin_configs": [
            {k: v for k, v in cfg.items() if k != "payload"}
            for cfg in plugin_configs
        ],
        "selected_plugin_summary": (
            {k: v for k, v in selected_plugin.items() if k != "payload"}
            if selected_plugin else None
        ),
    }


def write_repo_router_readme(path: Path, spec: Dict[str, Any]) -> None:
    text = f"""# Edge Factory OS Research Router Spec v1

Status: `{spec.get('router_ready')}`

This router spec defines how future research should be selected through the framework.

## Required order

{chr(10).join(f"- {x}" for x in spec.get("router_order", []))}

## Hard blocks

{chr(10).join(f"- `{x.get('block_key')}`: {x.get('condition')} -> {x.get('effect')}" for x in spec.get("hard_blocks", []))}

## Selected plugin

- plugin: `{spec.get('selected_plugin_key')}`
- path: `{spec.get('selected_plugin_path')}`
- research: `{spec.get('selected_research_key')}`

## Safety

This spec does not allow candidate generation, family release, runtime touch, capital change, live trading, active paper, or real orders.
"""
    write_text(path, text)


def write_summary_text(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS FRAMEWORK ROUTER SPEC BUILDER v1")
    lines.append("=" * 100)

    for k in [
        "builder_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "router_ready",
        "selected_plugin_key",
        "selected_research_key",
        "plugin_config_count",
        "lesson_count",
        "blocked_route_count",
        "next_module",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("ROUTER ORDER")
    lines.append("-" * 100)
    for item in result.get("router_spec", {}).get("router_order", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("HARD BLOCKS")
    lines.append("-" * 100)
    for item in result.get("router_spec", {}).get("hard_blocks", []):
        lines.append(f"- {item.get('block_key')}: {item.get('condition')} -> {item.get('effect')}")

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
    lines.append(f"repo_router_spec_json: {result.get('repo_router_spec_json')}")
    lines.append(f"repo_router_readme: {result.get('repo_router_readme')}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS FRAMEWORK ROUTER SPEC BUILDER v1")
    print("=" * 100)
    print(f"builder_status: {result.get('builder_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"router_ready: {result.get('router_ready')}")
    print(f"selected_plugin_key: {result.get('selected_plugin_key')}")
    print(f"selected_research_key: {result.get('selected_research_key')}")
    print(f"plugin_config_count: {result.get('plugin_config_count')}")
    print(f"lesson_count: {result.get('lesson_count')}")
    print(f"blocked_route_count: {result.get('blocked_route_count')}")
    print(f"next_module: {result.get('next_module')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"SPEC: {result.get('repo_router_spec_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CORE_DIR.mkdir(parents=True, exist_ok=True)

    skeleton = load_json(SKELETON_JSON, default={})
    manifest = load_json(ACTIVE_MANIFEST_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})
    lesson_index = load_json(LESSON_INDEX_PATH, default={})
    blocklist = load_json(BLOCKLIST_PATH, default={})

    plugin_configs = list_plugin_configs()
    selected_plugin = select_default_plugin(plugin_configs)

    lesson_count = extract_lessons_count(lesson_index)
    blocked_route_count = extract_blocked_count(blocklist)

    router_spec = build_router_spec(
        skeleton=skeleton,
        active_manifest=manifest,
        guard_feed=guard_feed,
        plugin_configs=plugin_configs,
        selected_plugin=selected_plugin,
        lesson_count=lesson_count,
        blocked_route_count=blocked_route_count,
    )

    write_json(REPO_ROUTER_SPEC_JSON, router_spec)
    write_repo_router_readme(REPO_ROUTER_README, router_spec)

    router_ready = bool(router_spec.get("router_ready"))

    if router_ready:
        builder_status = "FRAMEWORK_ROUTER_SPEC_READY"
        severity = "ATTENTION"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        next_action = "BUILD_GENERIC_RESEARCH_CONTRACT_BUILDER_V1"
        reason = (
            f"router_ready=True; selected_plugin={router_spec.get('selected_plugin_key')}; "
            f"plugin_config_count={len(plugin_configs)}; blocked_route_count={blocked_route_count}"
        )
        next_module = "edge_factory_os_generic_research_contract_builder_v1.py"
        return_code = 0
    else:
        builder_status = "FRAMEWORK_ROUTER_SPEC_BLOCKED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_FRAMEWORK_SKELETON_GUARD_FEED_AND_PLUGIN_CONFIGS"
        reason = (
            f"framework_ready={router_spec.get('framework_ready')}; "
            f"active_manifest_ready={router_spec.get('active_manifest_ready')}; "
            f"data_quality_guard_pass={router_spec.get('data_quality_guard_pass')}; "
            f"research_meta_synthesis_allowed={router_spec.get('research_meta_synthesis_allowed')}; "
            f"selected_plugin={router_spec.get('selected_plugin_key')}"
        )
        next_module = None
        return_code = 2

    git_status_short = run_git(["status", "--short"])
    git_branch = run_git(["branch", "--show-current"])
    git_last_commit = run_git(["log", "-1", "--oneline"])

    result = {
        "builder_name": "edge_factory_os_framework_router_spec_builder_v1",
        "created_at_utc": utc_now_iso(),
        "builder_status": builder_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "strict_policy_key": STRICT_POLICY_KEY,
        "router_ready": router_ready,
        "selected_plugin_key": router_spec.get("selected_plugin_key"),
        "selected_plugin_path": router_spec.get("selected_plugin_path"),
        "selected_research_key": router_spec.get("selected_research_key"),
        "plugin_config_count": len(plugin_configs),
        "lesson_count": lesson_count,
        "blocked_route_count": blocked_route_count,
        "next_module": next_module,
        "router_spec": router_spec,
        "git_branch": git_branch,
        "git_last_commit": git_last_commit,
        "git_status_short": git_status_short,
        "release_gate_feed": {
            "FRAMEWORK_ROUTER_SPEC_READY": router_ready,
            "REPO_ONLY_OS_INTELLIGENCE": True,
            "RELEASE_PASS_FROM_THIS_ROUTER_SPEC": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_THIS_ROUTER_SPEC": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_THIS_ROUTER_SPEC": False,
            "FAMILY_RELEASE_ALLOWED_FROM_THIS_ROUTER_SPEC": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_THIS_ROUTER_SPEC": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_THIS_ROUTER_SPEC": False,
            "ACTIVE_PAPER_ALLOWED_FROM_THIS_ROUTER_SPEC": False,
            "LIVE_ALLOWED_FROM_THIS_ROUTER_SPEC": False,
            "REAL_ORDERS_ALLOWED_FROM_THIS_ROUTER_SPEC": False,
        },
        "input_paths": {
            "skeleton_json": str(SKELETON_JSON),
            "active_manifest_json": str(ACTIVE_MANIFEST_JSON),
            "guard_feed_json": str(GUARD_FEED_JSON),
            "lesson_index_path": str(LESSON_INDEX_PATH),
            "blocklist_path": str(BLOCKLIST_PATH),
            "plugin_dir": str(PLUGIN_DIR),
            "schema_dir": str(SCHEMA_DIR),
        },
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "repo_router_spec_json": str(REPO_ROUTER_SPEC_JSON),
        "repo_router_readme": str(REPO_ROUTER_README),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_summary_text(OUT_TXT, result)
    print_summary(result)
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
