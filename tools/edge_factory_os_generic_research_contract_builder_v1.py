#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Generic Research Contract Builder v1

Purpose:
- Consume framework router spec v1.
- Consume selected plugin config.
- Consume data-quality guard feed.
- Consume lesson memory and route blocklist.
- Build a standardized framework research contract.
- This is the first framework-style contract builder replacing one-off contract builders.

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

ROUTER_SPEC_JSON = CORE_DIR / "research_router_spec_v1.json"
ROUTER_BUILDER_JSON = BASE_DIR / "edge_factory_os_framework_router_spec" / "framework_router_spec_latest.json"
GUARD_FEED_JSON = BASE_DIR / "edge_factory_os_data_quality_guard_runner" / "data_quality_guard_feed_latest.json"
LESSON_INDEX_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"
CONTRACT_SCHEMA_PATH = SCHEMA_DIR / "research_contract_schema_v1.json"

OUT_DIR = BASE_DIR / "edge_factory_os_generic_research_contract_builder"
OUT_JSON = OUT_DIR / "generic_research_contract_builder_latest.json"
OUT_TXT = OUT_DIR / "generic_research_contract_builder_latest.txt"

REPO_CONTRACT_DIR = FRAMEWORK_DIR / "contracts"
REPO_CONTRACT_JSON = REPO_CONTRACT_DIR / "current_research_contract_v1.json"
REPO_CONTRACT_TXT = REPO_CONTRACT_DIR / "current_research_contract_v1.txt"

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


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def utc_now_iso() -> str:
    return utc_now().isoformat()


def timestamp_compact() -> str:
    return utc_now().strftime("%Y%m%d_%H%M%S")


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


def extract_lessons(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get("lessons"), list):
        return [x for x in obj["lessons"] if isinstance(x, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def extract_blocked_routes(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get("blocked_routes"), list):
        return [x for x in obj["blocked_routes"] if isinstance(x, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def load_selected_plugin(router_spec: Dict[str, Any]) -> Dict[str, Any]:
    plugin_rel = router_spec.get("selected_plugin_path")
    if not plugin_rel:
        return {}

    plugin_path = REPO_DIR / str(plugin_rel)
    return load_json(plugin_path, default={})


def validate_plugin(plugin: Dict[str, Any], guard_feed: Dict[str, Any], blocked_routes: List[Dict[str, Any]]) -> Dict[str, Any]:
    failures: List[str] = []
    warnings: List[str] = []

    if not plugin:
        failures.append("PLUGIN_CONFIG_MISSING")

    if plugin.get("strict_policy_key") != STRICT_POLICY_KEY:
        failures.append("PLUGIN_STRICT_POLICY_MISMATCH")

    if int(plugin.get("canonical_policy_month_count") or 0) != 12:
        failures.append("PLUGIN_CANONICAL_POLICY_MONTH_COUNT_NOT_12")

    if not bool(plugin.get("must_consume_guard_feed")):
        failures.append("PLUGIN_DOES_NOT_REQUIRE_GUARD_FEED")

    if not bool(plugin.get("must_not_reopen_blocked_routes")):
        failures.append("PLUGIN_DOES_NOT_BLOCK_ROUTE_REOPEN")

    for flag in [
        "candidate_generation_allowed",
        "family_release_allowed",
        "runtime_touch_allowed",
        "capital_change_allowed",
        "live_allowed",
        "real_orders_allowed",
    ]:
        if bool(plugin.get(flag)):
            failures.append(f"PLUGIN_SAFETY_FLAG_OPEN_{flag}")

    if not bool(guard_feed.get("guard_pass")):
        failures.append("DATA_QUALITY_GUARD_NOT_PASS")

    if not bool(guard_feed.get("research_meta_synthesis_allowed")):
        failures.append("RESEARCH_META_SYNTHESIS_NOT_ALLOWED_BY_GUARD")

    negative_controls = plugin.get("negative_controls")
    if not isinstance(negative_controls, list) or len(negative_controls) < 3:
        failures.append("NEGATIVE_CONTROLS_INSUFFICIENT")

    null_models = plugin.get("null_models")
    if not isinstance(null_models, list) or len(null_models) < 3:
        failures.append("NULL_MODELS_INSUFFICIENT")

    forbidden_inputs = plugin.get("forbidden_inputs")
    if not isinstance(forbidden_inputs, list) or len(forbidden_inputs) == 0:
        failures.append("FORBIDDEN_INPUTS_NOT_DECLARED")

    feature_families = plugin.get("feature_families")
    if not isinstance(feature_families, list) or len(feature_families) == 0:
        failures.append("FEATURE_FAMILIES_NOT_DECLARED")

    if len(blocked_routes) == 0:
        warnings.append("BLOCKLIST_EMPTY_OR_NOT_LOADED")

    return {
        "plugin_validation_pass": len(failures) == 0,
        "plugin_validation_failures": failures,
        "plugin_validation_warnings": warnings,
    }


def make_route_hash_payload(plugin: Dict[str, Any], guard_feed: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "research_key": plugin.get("research_key"),
        "plugin_key": plugin.get("plugin_key"),
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "feature_families": plugin.get("feature_families", []),
        "negative_controls": plugin.get("negative_controls", []),
        "null_models": plugin.get("null_models", []),
        "forbidden_inputs": plugin.get("forbidden_inputs", []),
        "guard_status": guard_feed.get("guard_status"),
        "guard_requirement_count": guard_feed.get("guard_requirement_count"),
    }


def route_hash_blocked(route_hash: str, blocked_routes: List[Dict[str, Any]]) -> bool:
    for item in blocked_routes:
        if str(item.get("route_hash")) == route_hash:
            return True
    return False


def build_contract_text(contract: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS GENERIC RESEARCH CONTRACT v1")
    lines.append("=" * 100)
    for k in [
        "contract_status",
        "allowed_scope",
        "contract_id",
        "contract_hash",
        "route_hash",
        "plugin_key",
        "research_key",
        "strict_policy_key",
        "canonical_policy_month_count",
        "guard_pass",
        "route_hash_blocked",
        "next_module",
    ]:
        lines.append(f"{k}: {contract.get(k)}")

    lines.append("")
    lines.append("FEATURE FAMILIES")
    lines.append("-" * 100)
    for item in contract.get("feature_families", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("NEGATIVE CONTROLS")
    lines.append("-" * 100)
    for item in contract.get("negative_controls", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("NULL MODELS")
    lines.append("-" * 100)
    for item in contract.get("null_models", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("HARD BLOCKS")
    lines.append("-" * 100)
    for item in contract.get("hard_blocks", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        lines.append(f"{k}: {v}")

    return "\n".join(lines)


def build_summary_text(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS GENERIC RESEARCH CONTRACT BUILDER v1")
    lines.append("=" * 100)
    for k in [
        "builder_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "contract_status",
        "contract_id",
        "contract_hash",
        "route_hash",
        "route_hash_blocked",
        "plugin_key",
        "research_key",
        "guard_pass",
        "plugin_validation_pass",
        "next_module",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("VALIDATION")
    lines.append("-" * 100)
    lines.append(json.dumps(result.get("validation", {}), indent=2, ensure_ascii=False))

    lines.append("")
    lines.append("OUTPUT PATHS")
    lines.append("-" * 100)
    for k in ["output_json", "output_txt", "repo_contract_json", "repo_contract_txt"]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        lines.append(f"{k}: {v}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS GENERIC RESEARCH CONTRACT BUILDER v1")
    print("=" * 100)
    print(f"builder_status: {result.get('builder_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"contract_status: {result.get('contract_status')}")
    print(f"contract_id: {result.get('contract_id')}")
    print(f"contract_hash: {result.get('contract_hash')}")
    print(f"route_hash: {result.get('route_hash')}")
    print(f"route_hash_blocked: {result.get('route_hash_blocked')}")
    print(f"plugin_key: {result.get('plugin_key')}")
    print(f"research_key: {result.get('research_key')}")
    print(f"guard_pass: {result.get('guard_pass')}")
    print(f"plugin_validation_pass: {result.get('plugin_validation_pass')}")
    print(f"next_module: {result.get('next_module')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"CONTRACT JSON: {result.get('repo_contract_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPO_CONTRACT_DIR.mkdir(parents=True, exist_ok=True)

    router_builder = load_json(ROUTER_BUILDER_JSON, default={})
    router_spec = load_json(ROUTER_SPEC_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})
    lesson_index = load_json(LESSON_INDEX_PATH, default={})
    blocklist = load_json(BLOCKLIST_PATH, default={})
    contract_schema = load_json(CONTRACT_SCHEMA_PATH, default={})

    lessons = extract_lessons(lesson_index)
    blocked_routes = extract_blocked_routes(blocklist)
    plugin = load_selected_plugin(router_spec)

    validation = validate_plugin(plugin, guard_feed, blocked_routes)

    route_hash_payload = make_route_hash_payload(plugin, guard_feed)
    route_hash = stable_hash(route_hash_payload)
    blocked = route_hash_blocked(route_hash, blocked_routes)

    router_ready = bool(router_spec.get("router_ready")) and router_builder.get("builder_status") == "FRAMEWORK_ROUTER_SPEC_READY"
    guard_pass = bool(guard_feed.get("guard_pass"))
    plugin_validation_pass = bool(validation.get("plugin_validation_pass"))

    contract_ready = bool(
        router_ready
        and guard_pass
        and plugin_validation_pass
        and not blocked
        and plugin.get("research_key")
    )

    contract_hash_payload = {
        "route_hash": route_hash,
        "plugin_key": plugin.get("plugin_key"),
        "research_key": plugin.get("research_key"),
        "guard_status": guard_feed.get("guard_status"),
        "lesson_count": len(lessons),
        "blocked_route_count": len(blocked_routes),
        "schema_name": contract_schema.get("schema_name"),
    }
    contract_hash = stable_hash(contract_hash_payload)
    contract_id = f"GENERIC_RESEARCH_CONTRACT_V1_{contract_hash}_{timestamp_compact()}"

    if contract_ready:
        contract_status = "GENERIC_RESEARCH_CONTRACT_READY"
        builder_status = "GENERIC_RESEARCH_CONTRACT_BUILDER_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_GENERIC_RESEARCH_RUNNER_V1"
        next_module = "edge_factory_os_generic_research_runner_v1.py"
        reason = (
            f"router_ready=True; guard_pass=True; plugin_validation_pass=True; "
            f"route_hash_blocked=False; research_key={plugin.get('research_key')}"
        )
        return_code = 0
    else:
        contract_status = "GENERIC_RESEARCH_CONTRACT_BLOCKED"
        builder_status = "GENERIC_RESEARCH_CONTRACT_BUILDER_BLOCKED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_ROUTER_PLUGIN_GUARD_OR_BLOCKLIST"
        next_module = None
        reason = (
            f"router_ready={router_ready}; guard_pass={guard_pass}; "
            f"plugin_validation_pass={plugin_validation_pass}; route_hash_blocked={blocked}; "
            f"plugin_key={plugin.get('plugin_key')}"
        )
        return_code = 2

    contract = {
        "contract_name": "edge_factory_os_generic_research_contract_v1",
        "created_at_utc": utc_now_iso(),
        "contract_status": contract_status,
        "contract_id": contract_id if contract_ready else None,
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "route_hash_payload": route_hash_payload,
        "route_hash_blocked": blocked,
        "plugin_key": plugin.get("plugin_key"),
        "plugin_type": plugin.get("plugin_type"),
        "research_key": plugin.get("research_key"),
        "direction_queue_key": plugin.get("research_key"),
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "allowed_scope": "READ_ONLY_RESEARCH" if contract_ready else "READ_ONLY_REVIEW",
        "guard_feed_path": str(GUARD_FEED_JSON),
        "guard_status": guard_feed.get("guard_status"),
        "guard_pass": guard_pass,
        "guard_requirement_count": guard_feed.get("guard_requirement_count"),
        "guard_warning_count": guard_feed.get("guard_warning_count"),
        "lesson_count": len(lessons),
        "blocked_route_count": len(blocked_routes),
        "plugin_config": plugin,
        "plugin_validation": validation,
        "feature_families": plugin.get("feature_families", []),
        "negative_controls": plugin.get("negative_controls", []),
        "null_models": plugin.get("null_models", []),
        "forbidden_inputs": plugin.get("forbidden_inputs", []),
        "hard_blocks": [
            "candidate_generation_forbidden",
            "candidate_contract_forbidden",
            "family_release_forbidden",
            "runtime_touch_forbidden",
            "capital_change_forbidden",
            "active_paper_forbidden",
            "live_trading_forbidden",
            "real_orders_forbidden",
            "blocked_route_hash_reuse_forbidden",
            "missing_guard_feed_forbidden",
            "future_return_as_feature_forbidden",
            "manual_symbol_whitelist_forbidden",
            "manual_month_blacklist_forbidden",
        ],
        "required_runner_outputs": [
            "guard_consumption_report",
            "feature_family_inventory",
            "negative_control_results",
            "null_model_results",
            "feature_diagnostic_rankings",
            "strict_12_feature_signal_preview_count",
            "null_adjusted_signal_count",
            "latest_json",
            "latest_txt",
            "csv_outputs",
        ],
        "next_module": next_module,
        "schema_path": str(CONTRACT_SCHEMA_PATH),
        "router_spec_path": str(ROUTER_SPEC_JSON),
        "release_gate_feed": {
            "GENERIC_RESEARCH_CONTRACT_READY": contract_ready,
            "DATA_QUALITY_GUARD_PASS": guard_pass,
            "ROUTE_HASH_BLOCKED": blocked,
            "STRICT_MONTH_STABILITY_12_OF_12": True,
            "RELEASE_PASS_FROM_THIS_CONTRACT": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_THIS_CONTRACT": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_THIS_CONTRACT": False,
            "FAMILY_RELEASE_ALLOWED_FROM_THIS_CONTRACT": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_THIS_CONTRACT": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_THIS_CONTRACT": False,
            "ACTIVE_PAPER_ALLOWED_FROM_THIS_CONTRACT": False,
            "LIVE_ALLOWED_FROM_THIS_CONTRACT": False,
            "REAL_ORDERS_ALLOWED_FROM_THIS_CONTRACT": False,
        },
        **SAFETY_FLAGS,
    }

    write_json(REPO_CONTRACT_JSON, contract)
    write_text(REPO_CONTRACT_TXT, build_contract_text(contract))

    git_status_short = run_git(["status", "--short"])
    git_branch = run_git(["branch", "--show-current"])
    git_last_commit = run_git(["log", "-1", "--oneline"])

    result = {
        "builder_name": "edge_factory_os_generic_research_contract_builder_v1",
        "created_at_utc": utc_now_iso(),
        "builder_status": builder_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "contract_status": contract_status,
        "contract_id": contract.get("contract_id"),
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "route_hash_blocked": blocked,
        "plugin_key": plugin.get("plugin_key"),
        "research_key": plugin.get("research_key"),
        "guard_pass": guard_pass,
        "router_ready": router_ready,
        "plugin_validation_pass": plugin_validation_pass,
        "validation": validation,
        "next_module": next_module,
        "git_branch": git_branch,
        "git_last_commit": git_last_commit,
        "git_status_short": git_status_short,
        "contract": contract,
        "release_gate_feed": {
            "GENERIC_RESEARCH_CONTRACT_BUILDER_RAN": True,
            "GENERIC_RESEARCH_CONTRACT_READY": contract_ready,
            "RELEASE_PASS_FROM_THIS_BUILDER": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_THIS_BUILDER": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_THIS_BUILDER": False,
            "FAMILY_RELEASE_ALLOWED_FROM_THIS_BUILDER": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_THIS_BUILDER": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_THIS_BUILDER": False,
            "ACTIVE_PAPER_ALLOWED_FROM_THIS_BUILDER": False,
            "LIVE_ALLOWED_FROM_THIS_BUILDER": False,
            "REAL_ORDERS_ALLOWED_FROM_THIS_BUILDER": False,
        },
        "input_paths": {
            "router_builder_json": str(ROUTER_BUILDER_JSON),
            "router_spec_json": str(ROUTER_SPEC_JSON),
            "guard_feed_json": str(GUARD_FEED_JSON),
            "lesson_index_path": str(LESSON_INDEX_PATH),
            "blocklist_path": str(BLOCKLIST_PATH),
            "contract_schema_path": str(CONTRACT_SCHEMA_PATH),
        },
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "repo_contract_json": str(REPO_CONTRACT_JSON),
        "repo_contract_txt": str(REPO_CONTRACT_TXT),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_summary_text(result))
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
