#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Framework Status Panel Builder v1

Purpose:
- Consolidate current framework/guard/policy/research-null-baseline states.
- Make the OS status visible as one canonical panel.
- Record that false-positive methodology is repaired, but actual signal is absent.
- Keep plugin expansion and all release/runtime/capital/live actions blocked.
- Queue policy-locked next research direction builder.

This module does NOT:
- run strategy research
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

import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

POLICY_JSON = REPO_DIR / "edge_factory_os_framework" / "policies" / "research_gate_enforcement_policy_v1.json"
POLICY_RUNTIME_STATE_JSON = REPO_DIR / "edge_factory_os_framework" / "policies" / "research_gate_policy_runtime_state_v1.json"
POLICY_VALIDATION_STATE_JSON = REPO_DIR / "edge_factory_os_framework" / "policies" / "research_gate_validation_state_v1.json"
NULL_METHOD_STATE_JSON = REPO_DIR / "edge_factory_os_framework" / "policies" / "null_baseline_method_state_v1.json"
NULL_REPAIR_STATE_JSON = REPO_DIR / "edge_factory_os_framework" / "policies" / "null_baseline_method_repair_state_v1.json"
TRUE_PANEL_STATE_JSON = REPO_DIR / "edge_factory_os_framework" / "policies" / "true_source_panel_empirical_null_baseline_state_v1.json"

GUARD_FEED_JSON = BASE_DIR / "edge_factory_os_data_quality_guard_runner" / "data_quality_guard_feed_latest.json"
VALIDATOR_JSON = BASE_DIR / "edge_factory_os_research_gate_enforcement_validator" / "research_gate_enforcement_validator_latest.json"
TRUE_PANEL_EVALUATOR_JSON = (
    BASE_DIR
    / "edge_factory_os_true_source_panel_empirical_null_baseline_evaluator"
    / "true_source_panel_empirical_null_baseline_evaluator_latest.json"
)

ACTIVE_CORE_MANIFEST_JSON = BASE_DIR / "edge_factory_os_active_core_manifest" / "active_core_manifest_latest.json"
GENERIC_FRAMEWORK_SKELETON_JSON = BASE_DIR / "edge_factory_os_generic_framework_skeleton" / "generic_framework_skeleton_latest.json"

LESSON_INDEX_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"
SPECIFIC_LESSON_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "framework_status_panel_lesson_latest.json"

OUT_DIR = BASE_DIR / "edge_factory_os_framework_status_panel"
OUT_JSON = OUT_DIR / "framework_status_panel_latest.json"
OUT_TXT = OUT_DIR / "framework_status_panel_latest.txt"
OUT_CSV = OUT_DIR / "framework_status_panel_components_latest.csv"
OUT_QUEUE_JSON = OUT_DIR / "framework_status_panel_next_queue_latest.json"

FRAMEWORK_STATUS_DIR = REPO_DIR / "edge_factory_os_framework" / "status"
REPO_STATUS_JSON = FRAMEWORK_STATUS_DIR / "framework_status_panel_v1.json"
REPO_STATUS_TXT = FRAMEWORK_STATUS_DIR / "framework_status_panel_v1.txt"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD5_08_POLICY_LOCKED_NEW_RESEARCH_DIRECTION_QUEUE"
NEXT_MODULE = "edge_factory_os_policy_locked_new_research_direction_queue_v1.py"

ALT_RESEARCH_KEY = "RD5_09_FRAMEWORK_ROUTE_PLUGIN_REFRESH"
ALT_MODULE = "edge_factory_os_framework_route_plugin_refresh_v1.py"

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
    except Exception as exc:
        return {"_load_error": f"{type(exc).__name__}: {exc}", "_path": str(path)}


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


def stable_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def count_lessons(obj: Any) -> int:
    if isinstance(obj, dict) and isinstance(obj.get("lessons"), list):
        return len(obj["lessons"])
    if isinstance(obj, list):
        return len([x for x in obj if isinstance(x, dict)])
    return 0


def count_blocked_routes(obj: Any) -> int:
    if isinstance(obj, dict) and isinstance(obj.get("blocked_routes"), list):
        return len([x for x in obj["blocked_routes"] if isinstance(x, dict)])
    if isinstance(obj, list):
        return len([x for x in obj if isinstance(x, dict)])
    return 0


def component_row(
    *,
    component_key: str,
    component_status: str,
    pass_state: bool,
    severity: str,
    summary: str,
    source_path: Path,
) -> Dict[str, Any]:
    return {
        "component_key": component_key,
        "component_status": component_status,
        "pass_state": bool(pass_state),
        "severity": severity,
        "summary": summary,
        "source_path": str(source_path),
        "candidate_generation_allowed": False,
        "candidate_contract_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
    }


def append_lesson_record(path: Path, lesson_record: Dict[str, Any]) -> Dict[str, Any]:
    obj = load_json(path, default={})

    if isinstance(obj, list):
        existing = {x.get("lesson_id") for x in obj if isinstance(x, dict)}
        if lesson_record["lesson_id"] not in existing:
            obj.append(lesson_record)
        write_json(path, obj)
        return {"append_mode": "list_root", "path": str(path)}

    if not isinstance(obj, dict):
        obj = {}

    lessons = obj.get("lessons")
    if not isinstance(lessons, list):
        lessons = []

    existing = {x.get("lesson_id") for x in lessons if isinstance(x, dict)}
    if lesson_record["lesson_id"] not in existing:
        lessons.append(lesson_record)

    obj["lessons"] = lessons
    obj["updated_at_utc"] = utc_now_iso()
    write_json(path, obj)
    return {"append_mode": "dict_lessons", "path": str(path)}


def build_panel_text(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS FRAMEWORK STATUS PANEL v1")
    lines.append("=" * 100)

    for key in [
        "panel_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "strict_policy_key",
        "policy_active",
        "guard_pass",
        "validator_pass",
        "false_positive_methodology_repaired",
        "actual_signal_present",
        "plugin_expansion_allowed",
        "release_allowed",
        "runtime_touch_allowed",
        "capital_change_allowed",
        "live_allowed",
        "real_orders_allowed",
        "lesson_count",
        "blocked_route_count",
        "next_recommended_research_key",
        "next_module",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("COMPONENTS")
    lines.append("-" * 100)
    for row in result.get("component_rows", []):
        lines.append(
            f"{row.get('component_key')}: pass={row.get('pass_state')} "
            f"status={row.get('component_status')} | {row.get('summary')}"
        )

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        lines.append(f"{key}: {value}")

    lines.append("")
    lines.append("OUTPUT PATHS")
    lines.append("-" * 100)
    for key in [
        "output_json",
        "output_txt",
        "output_csv",
        "next_queue_json",
        "repo_status_json",
        "repo_status_txt",
        "specific_lesson_path",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS FRAMEWORK STATUS PANEL BUILDER v1")
    print("=" * 100)
    print(f"panel_status: {result.get('panel_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"policy_active: {result.get('policy_active')}")
    print(f"guard_pass: {result.get('guard_pass')}")
    print(f"validator_pass: {result.get('validator_pass')}")
    print(f"false_positive_methodology_repaired: {result.get('false_positive_methodology_repaired')}")
    print(f"actual_signal_present: {result.get('actual_signal_present')}")
    print(f"plugin_expansion_allowed: {result.get('plugin_expansion_allowed')}")
    print(f"next_recommended_research_key: {result.get('next_recommended_research_key')}")
    print(f"next_module: {result.get('next_module')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        print(f"{key}: {value}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"CSV : {result.get('output_csv')}")
    print(f"REPO_STATUS: {result.get('repo_status_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FRAMEWORK_STATUS_DIR.mkdir(parents=True, exist_ok=True)
    LESSON_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

    policy = load_json(POLICY_JSON, default={})
    policy_runtime_state = load_json(POLICY_RUNTIME_STATE_JSON, default={})
    validation_state = load_json(POLICY_VALIDATION_STATE_JSON, default={})
    null_method_state = load_json(NULL_METHOD_STATE_JSON, default={})
    null_repair_state = load_json(NULL_REPAIR_STATE_JSON, default={})
    true_panel_state = load_json(TRUE_PANEL_STATE_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})
    validator = load_json(VALIDATOR_JSON, default={})
    true_panel_evaluator = load_json(TRUE_PANEL_EVALUATOR_JSON, default={})
    active_core_manifest = load_json(ACTIVE_CORE_MANIFEST_JSON, default={})
    framework_skeleton = load_json(GENERIC_FRAMEWORK_SKELETON_JSON, default={})
    lesson_index = load_json(LESSON_INDEX_PATH, default={})
    blocklist = load_json(BLOCKLIST_PATH, default={})

    policy_active = policy.get("policy_status") == "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE"
    guard_pass = bool(guard_feed.get("guard_pass"))
    validator_pass = bool(validation_state.get("validator_pass")) and bool(validator.get("validator_pass"))

    false_positive_methodology_repaired = bool(true_panel_state.get("false_positive_methodology_repaired"))
    actual_signal_present = bool(true_panel_state.get("actual_signal_present"))

    plugin_expansion_allowed = False
    release_allowed = False

    lesson_count = count_lessons(lesson_index)
    blocked_route_count = count_blocked_routes(blocklist)

    component_rows = [
        component_row(
            component_key="research_gate_policy",
            component_status=str(policy.get("policy_status")),
            pass_state=policy_active,
            severity="OK" if policy_active else "ATTENTION",
            summary=f"policy_hash={policy.get('policy_hash')}",
            source_path=POLICY_JSON,
        ),
        component_row(
            component_key="policy_runtime_state",
            component_status=str(policy_runtime_state.get("state_status")),
            pass_state=policy_runtime_state.get("plugin_expansion_allowed") is False,
            severity="OK",
            summary="plugin expansion blocked in runtime policy state",
            source_path=POLICY_RUNTIME_STATE_JSON,
        ),
        component_row(
            component_key="policy_validation_state",
            component_status=str(validation_state.get("validation_state")),
            pass_state=validator_pass,
            severity="OK" if validator_pass else "ATTENTION",
            summary=f"validator_pass={validation_state.get('validator_pass')}",
            source_path=POLICY_VALIDATION_STATE_JSON,
        ),
        component_row(
            component_key="data_quality_guard",
            component_status=str(guard_feed.get("guard_status")),
            pass_state=guard_pass,
            severity="OK" if guard_pass else "ATTENTION",
            summary=f"guard_warning_count={guard_feed.get('guard_warning_count')}",
            source_path=GUARD_FEED_JSON,
        ),
        component_row(
            component_key="null_baseline_method_state",
            component_status=str(null_method_state.get("method_state")),
            pass_state=null_method_state.get("plugin_expansion_allowed") is False,
            severity="OK",
            summary=f"method_repair_required={null_method_state.get('method_repair_required')}",
            source_path=NULL_METHOD_STATE_JSON,
        ),
        component_row(
            component_key="null_baseline_repair_state",
            component_status=str(null_repair_state.get("repair_state")),
            pass_state=null_repair_state.get("plugin_expansion_allowed") is False,
            severity="OK",
            summary=f"true_source_panel_replay_required={null_repair_state.get('true_source_panel_replay_required')}",
            source_path=NULL_REPAIR_STATE_JSON,
        ),
        component_row(
            component_key="true_source_panel_null_baseline_state",
            component_status=str(true_panel_state.get("state_status")),
            pass_state=false_positive_methodology_repaired and not actual_signal_present,
            severity="ATTENTION",
            summary=(
                f"false_positive_repaired={false_positive_methodology_repaired}; "
                f"actual_signal_present={actual_signal_present}; "
                f"max_strict={true_panel_state.get('max_strict_12_any_random_hit_rate')}; "
                f"max_null={true_panel_state.get('max_null_adjusted_any_random_hit_rate')}"
            ),
            source_path=TRUE_PANEL_STATE_JSON,
        ),
        component_row(
            component_key="active_core_manifest",
            component_status=str(active_core_manifest.get("manifest_status")),
            pass_state=bool(active_core_manifest.get("manifest_item_count") or active_core_manifest.get("active_core_count")),
            severity="OK",
            summary=(
                f"active_core={active_core_manifest.get('active_core_count')}; "
                f"current_frontier={active_core_manifest.get('current_frontier_count')}; "
                f"consolidate={active_core_manifest.get('consolidate_into_framework_count')}"
            ),
            source_path=ACTIVE_CORE_MANIFEST_JSON,
        ),
        component_row(
            component_key="generic_framework_skeleton",
            component_status=str(framework_skeleton.get("skeleton_status")),
            pass_state=bool(framework_skeleton.get("schema_stub_count") or framework_skeleton.get("framework_dir")),
            severity="OK",
            summary=f"framework_dir={framework_skeleton.get('framework_dir')}",
            source_path=GENERIC_FRAMEWORK_SKELETON_JSON,
        ),
    ]

    hard_failures = [
        row for row in component_rows
        if not bool(row.get("pass_state"))
        and row.get("component_key") not in {"true_source_panel_null_baseline_state"}
    ]

    expected_policy_locked_state = (
        policy_active
        and guard_pass
        and validator_pass
        and false_positive_methodology_repaired
        and not actual_signal_present
        and plugin_expansion_allowed is False
        and release_allowed is False
        and len(hard_failures) == 0
    )

    if expected_policy_locked_state:
        panel_status = "FRAMEWORK_STATUS_PANEL_READY_POLICY_LOCKED_NO_ACTUAL_SIGNAL"
        severity = "ATTENTION"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        next_action = "BUILD_POLICY_LOCKED_NEW_RESEARCH_DIRECTION_QUEUE_NO_RELEASE"
        reason = (
            "Framework status consolidated: policy/guard/validator pass, false-positive methodology repaired, "
            "actual signal absent, plugin expansion and all release actions blocked."
        )
        next_key = NEXT_RESEARCH_KEY
        next_module = NEXT_MODULE
        return_code = 0
    else:
        panel_status = "FRAMEWORK_STATUS_PANEL_ATTENTION_REVIEW_REQUIRED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_FRAMEWORK_STATUS_PANEL_COMPONENTS_NO_RELEASE"
        reason = (
            f"expected_policy_locked_state={expected_policy_locked_state}; "
            f"hard_failures={[x.get('component_key') for x in hard_failures]}; "
            f"policy_active={policy_active}; guard_pass={guard_pass}; validator_pass={validator_pass}; "
            f"false_positive_methodology_repaired={false_positive_methodology_repaired}; actual_signal_present={actual_signal_present}"
        )
        next_key = NEXT_RESEARCH_KEY
        next_module = NEXT_MODULE
        return_code = 2

    status_hash = stable_hash({
        "panel_status": panel_status,
        "policy_hash": policy.get("policy_hash"),
        "false_positive_methodology_repaired": false_positive_methodology_repaired,
        "actual_signal_present": actual_signal_present,
        "lesson_count": lesson_count,
        "blocked_route_count": blocked_route_count,
    })

    lesson_id = f"LESSON_FRAMEWORK_STATUS_PANEL_{status_hash}"

    next_queue = {
        "created_at_utc": utc_now_iso(),
        "queue_status": "FRAMEWORK_STATUS_PANEL_NEXT_QUEUE_READY" if return_code == 0 else "FRAMEWORK_STATUS_PANEL_NEXT_QUEUE_REVIEW_REQUIRED",
        "source_panel": "edge_factory_os_framework_status_panel_builder_v1",
        "panel_status": panel_status,
        "status_hash": status_hash,
        "policy_hash": policy.get("policy_hash"),
        "false_positive_methodology_repaired": false_positive_methodology_repaired,
        "actual_signal_present": actual_signal_present,
        "plugin_expansion_allowed": False,
        "top_next_research_key": next_key,
        "top_next_module": next_module,
        "next_direction_queue": [
            {
                "research_key": next_key,
                "priority": 100,
                "next_module_recommendation": next_module,
                "allowed_scope": "READ_ONLY_RESEARCH",
                "why": (
                    "Queue a materially different policy-locked research direction. "
                    "It must consume guard, policy, validator state, true source-panel null baseline state, "
                    "and route blocklist before any plugin expansion."
                ),
                "must_consume_guard_feed": True,
                "must_consume_research_gate_policy": True,
                "must_consume_true_source_panel_state": True,
                "must_consume_blocklist": True,
                "must_be_materially_different_from_blocked_routes": True,
                "plugin_expansion_allowed_now": False,
                "candidate_generation_allowed_now": False,
                "candidate_contract_allowed_now": False,
                "family_release_allowed_now": False,
                "runtime_touch_allowed_now": False,
                "capital_change_allowed_now": False,
                "active_paper_allowed_now": False,
                "live_allowed_now": False,
                "real_orders_allowed_now": False,
            },
            {
                "research_key": ALT_RESEARCH_KEY,
                "priority": 70,
                "next_module_recommendation": ALT_MODULE,
                "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
                "why": "Refresh generic framework routing/plugin config after status panel is canonical.",
                "must_consume_guard_feed": True,
                "must_consume_research_gate_policy": True,
                "plugin_expansion_allowed_now": False,
                "candidate_generation_allowed_now": False,
                "family_release_allowed_now": False,
            },
        ],
        **SAFETY_FLAGS,
    }

    result = {
        "builder_name": "edge_factory_os_framework_status_panel_builder_v1",
        "created_at_utc": utc_now_iso(),
        "panel_status": panel_status,
        "status_hash": status_hash,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "strict_policy_key": STRICT_POLICY_KEY,
        "policy_active": policy_active,
        "policy_hash": policy.get("policy_hash"),
        "guard_pass": guard_pass,
        "validator_pass": validator_pass,
        "false_positive_methodology_repaired": false_positive_methodology_repaired,
        "actual_signal_present": actual_signal_present,
        "plugin_expansion_allowed": False,
        "release_allowed": False,
        "lesson_count": lesson_count,
        "blocked_route_count": blocked_route_count,
        "component_count": len(component_rows),
        "hard_failure_count": len(hard_failures),
        "hard_failures": hard_failures,
        "component_rows": component_rows,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        "lesson_id": lesson_id,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "output_csv": str(OUT_CSV),
        "next_queue_json": str(OUT_QUEUE_JSON),
        "repo_status_json": str(REPO_STATUS_JSON),
        "repo_status_txt": str(REPO_STATUS_TXT),
        "specific_lesson_path": str(SPECIFIC_LESSON_PATH),
        "release_gate_feed": {
            "FRAMEWORK_STATUS_PANEL_READY": return_code == 0,
            "POLICY_ACTIVE": policy_active,
            "GUARD_PASS": guard_pass,
            "VALIDATOR_PASS": validator_pass,
            "FALSE_POSITIVE_METHODOLOGY_REPAIRED": false_positive_methodology_repaired,
            "ACTUAL_SIGNAL_PRESENT": actual_signal_present,
            "PLUGIN_EXPANSION_ALLOWED": False,
            "RELEASE_PASS_FROM_THIS_PANEL": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_THIS_PANEL": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_THIS_PANEL": False,
            "FAMILY_RELEASE_ALLOWED_FROM_THIS_PANEL": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_THIS_PANEL": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_THIS_PANEL": False,
            "ACTIVE_PAPER_ALLOWED_FROM_THIS_PANEL": False,
            "LIVE_ALLOWED_FROM_THIS_PANEL": False,
            "REAL_ORDERS_ALLOWED_FROM_THIS_PANEL": False,
        },
        **SAFETY_FLAGS,
    }

    lesson_record = {
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "lesson_type": "FRAMEWORK_STATUS_PANEL_BUILT",
        "panel_status": panel_status,
        "status_hash": status_hash,
        "policy_hash": policy.get("policy_hash"),
        "false_positive_methodology_repaired": false_positive_methodology_repaired,
        "actual_signal_present": actual_signal_present,
        "plugin_expansion_allowed": False,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        "component_count": len(component_rows),
        "hard_failure_count": len(hard_failures),
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
    }

    write_json(SPECIFIC_LESSON_PATH, lesson_record)
    result["lesson_append_status"] = append_lesson_record(LESSON_INDEX_PATH, lesson_record)

    write_json(OUT_QUEUE_JSON, next_queue)
    write_csv(OUT_CSV, component_rows)
    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_panel_text(result))

    write_json(REPO_STATUS_JSON, result)
    write_text(REPO_STATUS_TXT, build_panel_text(result))

    print_summary(result)
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
