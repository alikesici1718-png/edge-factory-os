#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Generic Research Evaluator v1

Purpose:
- Consume Generic Research Runner v1 output.
- Consume current framework research contract.
- Evaluate whether the current plugin route produced:
  1) null-adjusted signal,
  2) strict preview but not null-adjusted,
  3) no usable signal.
- Write lesson memory and route blocklist for failed/no-signal routes.
- Queue the next framework-safe research direction.
- Keep all candidate/family/runtime/capital/live/real-order actions blocked.

This evaluator does NOT:
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
from pathlib import Path
from typing import Any, Dict, List, Optional


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

RUNNER_JSON = BASE_DIR / "edge_factory_os_generic_research_runner" / "generic_research_runner_latest.json"
CONTRACT_JSON = REPO_DIR / "edge_factory_os_framework" / "contracts" / "current_research_contract_v1.json"
GUARD_FEED_JSON = BASE_DIR / "edge_factory_os_data_quality_guard_runner" / "data_quality_guard_feed_latest.json"

LESSON_DIR = BASE_DIR / "edge_factory_os_lesson_memory"
LESSON_INDEX_PATH = LESSON_DIR / "lesson_memory_index.json"
BLOCKLIST_PATH = LESSON_DIR / "candidate_route_blocklist.json"
SPECIFIC_LESSON_PATH = LESSON_DIR / "generic_research_no_strict_or_null_signal_lesson_latest.json"

OUT_DIR = BASE_DIR / "edge_factory_os_generic_research_evaluator"
OUT_JSON = OUT_DIR / "generic_research_evaluator_latest.json"
OUT_TXT = OUT_DIR / "generic_research_evaluator_latest.txt"
NEXT_QUEUE_JSON = OUT_DIR / "generic_research_next_queue_latest.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD5_02_NULL_MODEL_AND_PERMUTATION_BASELINE"
NEXT_MODULE = "edge_factory_os_null_model_permutation_baseline_contract_builder_v1.py"

ALT_RESEARCH_KEY = "RD5_01B_GUARDED_FEATURE_SPACE_PLUGIN_EXPANSION"
ALT_MODULE = "edge_factory_os_plugin_expansion_planner_v1.py"

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


def stable_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def append_lesson_record(path: Path, lesson_record: Dict[str, Any]) -> Dict[str, Any]:
    obj = load_json(path, default={})

    if isinstance(obj, list):
        existing_ids = {x.get("lesson_id") for x in obj if isinstance(x, dict)}
        if lesson_record["lesson_id"] not in existing_ids:
            obj.append(lesson_record)
        write_json(path, obj)
        return {"append_mode": "list_root", "path": str(path)}

    if not isinstance(obj, dict):
        obj = {}

    lessons = obj.get("lessons")
    if not isinstance(lessons, list):
        lessons = []

    existing_ids = {x.get("lesson_id") for x in lessons if isinstance(x, dict)}
    if lesson_record["lesson_id"] not in existing_ids:
        lessons.append(lesson_record)

    obj["lessons"] = lessons
    obj["updated_at_utc"] = utc_now_iso()
    write_json(path, obj)
    return {"append_mode": "dict_lessons", "path": str(path)}


def append_blocklist_record(path: Path, block_record: Dict[str, Any]) -> Dict[str, Any]:
    obj = load_json(path, default={})

    if isinstance(obj, list):
        existing = {x.get("route_hash") for x in obj if isinstance(x, dict)}
        if block_record["route_hash"] not in existing:
            obj.append(block_record)
        write_json(path, obj)
        return {"append_mode": "list_root", "path": str(path)}

    if not isinstance(obj, dict):
        obj = {}

    blocked = obj.get("blocked_routes")
    if not isinstance(blocked, list):
        blocked = []

    existing = {x.get("route_hash") for x in blocked if isinstance(x, dict)}
    if block_record["route_hash"] not in existing:
        blocked.append(block_record)

    obj["blocked_routes"] = blocked
    obj["updated_at_utc"] = utc_now_iso()
    write_json(path, obj)
    return {"append_mode": "dict_blocked_routes", "path": str(path)}


def choose_next_route(
    *,
    strict_preview_count: int,
    null_adjusted_signal_count: int,
    diagnostic_row_count: int,
    negative_control_row_count: int,
    null_model_row_count: int,
) -> Dict[str, Any]:
    if null_adjusted_signal_count > 0:
        return {
            "decision_class": "NULL_ADJUSTED_SIGNAL_FOUND_DEEP_VALIDATION_REQUIRED",
            "branch_closed": False,
            "route_blocklist_required": False,
            "next_recommended_research_key": "RD5_SIGNAL_DEEP_VALIDATION_REQUIRED",
            "next_module": "edge_factory_os_generic_deep_validation_contract_builder_v1.py",
            "next_action": "BUILD_GENERIC_DEEP_VALIDATION_CONTRACT_NO_RELEASE",
            "reason": "Null-adjusted signal exists; requires deep validation but no candidate/release.",
        }

    if strict_preview_count > 0 and null_adjusted_signal_count == 0:
        return {
            "decision_class": "STRICT_PREVIEW_REJECTED_BY_NULL_MODEL",
            "branch_closed": True,
            "route_blocklist_required": True,
            "next_recommended_research_key": NEXT_RESEARCH_KEY,
            "next_module": NEXT_MODULE,
            "next_action": "BUILD_NULL_MODEL_PERMUTATION_BASELINE_CONTRACT_NO_RELEASE",
            "reason": "Strict preview existed but failed null adjustment; strengthen null/permutation baseline.",
        }

    if diagnostic_row_count > 0 and strict_preview_count == 0 and null_adjusted_signal_count == 0:
        return {
            "decision_class": "NO_STRICT_OR_NULL_ADJUSTED_SIGNAL_CLOSE_PLUGIN_ROUTE",
            "branch_closed": True,
            "route_blocklist_required": True,
            "next_recommended_research_key": NEXT_RESEARCH_KEY,
            "next_module": NEXT_MODULE,
            "next_action": "BUILD_NULL_MODEL_PERMUTATION_BASELINE_CONTRACT_NO_RELEASE",
            "reason": "Feature diagnostics ran with negative controls/null models but no strict or null-adjusted signal.",
        }

    return {
        "decision_class": "NO_VALID_DIAGNOSTICS_PLUGIN_EXPANSION_OR_INSPECTION_REQUIRED",
        "branch_closed": True,
        "route_blocklist_required": True,
        "next_recommended_research_key": ALT_RESEARCH_KEY,
        "next_module": ALT_MODULE,
        "next_action": "BUILD_PLUGIN_EXPANSION_OR_INSPECTION_PLANNER_NO_RELEASE",
        "reason": "No valid feature diagnostics; inspect/expand plugin before more research.",
    }


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS GENERIC RESEARCH EVALUATOR v1")
    lines.append("=" * 100)

    for k in [
        "evaluator_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "decision_class",
        "branch_closed",
        "route_blocklist_required",
        "plugin_key",
        "research_key",
        "contract_id",
        "route_hash",
        "strict_policy_key",
        "canonical_policy_month_count",
        "feature_count",
        "diagnostic_row_count",
        "negative_control_row_count",
        "null_model_row_count",
        "strict_12_feature_signal_preview_count",
        "null_adjusted_signal_count",
        "next_recommended_research_key",
        "next_module",
        "lesson_id",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("INTERPRETATION")
    lines.append("-" * 100)
    lines.append(str(result.get("interpretation")))

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        lines.append(f"{k}: {v}")

    lines.append("")
    lines.append("OUTPUT PATHS")
    lines.append("-" * 100)
    for k in [
        "output_json",
        "output_txt",
        "next_queue_json",
        "lesson_index_path",
        "blocklist_path",
        "specific_lesson_path",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS GENERIC RESEARCH EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {result.get('evaluator_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"decision_class: {result.get('decision_class')}")
    print(f"branch_closed: {result.get('branch_closed')}")
    print(f"route_blocklist_required: {result.get('route_blocklist_required')}")
    print(f"plugin_key: {result.get('plugin_key')}")
    print(f"research_key: {result.get('research_key')}")
    print(f"contract_id: {result.get('contract_id')}")
    print(f"route_hash: {result.get('route_hash')}")
    print(f"feature_count: {result.get('feature_count')}")
    print(f"diagnostic_row_count: {result.get('diagnostic_row_count')}")
    print(f"negative_control_row_count: {result.get('negative_control_row_count')}")
    print(f"null_model_row_count: {result.get('null_model_row_count')}")
    print(f"strict_12_feature_signal_preview_count: {result.get('strict_12_feature_signal_preview_count')}")
    print(f"null_adjusted_signal_count: {result.get('null_adjusted_signal_count')}")
    print(f"next_recommended_research_key: {result.get('next_recommended_research_key')}")
    print(f"next_module: {result.get('next_module')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"QUEUE: {result.get('next_queue_json')}")
    print(f"LESSON: {result.get('specific_lesson_path')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LESSON_DIR.mkdir(parents=True, exist_ok=True)

    runner = load_json(RUNNER_JSON, default={})
    contract = load_json(CONTRACT_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})

    runner_status = str(runner.get("runner_status", ""))
    runner_missing = not RUNNER_JSON.exists()
    runner_error = "ERROR" in runner_status.upper()

    plugin_key = runner.get("plugin_key") or contract.get("plugin_key")
    research_key = runner.get("research_key") or contract.get("research_key")
    contract_id = runner.get("contract_id") or contract.get("contract_id")
    contract_hash = contract.get("contract_hash")
    route_hash = runner.get("route_hash") or contract.get("route_hash")

    canonical_policy_month_count = to_int(runner.get("canonical_policy_month_count"), 12)
    feature_count = to_int(runner.get("feature_count"))
    diagnostic_row_count = to_int(runner.get("diagnostic_row_count"))
    negative_control_row_count = to_int(runner.get("negative_control_row_count"))
    null_model_row_count = to_int(runner.get("null_model_row_count"))
    strict_preview_count = to_int(runner.get("strict_12_feature_signal_preview_count"))
    null_adjusted_signal_count = to_int(runner.get("null_adjusted_signal_count"))

    valid_input = (
        not runner_missing
        and not runner_error
        and runner_status.startswith("GENERIC_RESEARCH_RUNNER_")
        and canonical_policy_month_count == 12
        and bool(guard_feed.get("guard_pass"))
        and bool(route_hash)
    )

    decision = choose_next_route(
        strict_preview_count=strict_preview_count,
        null_adjusted_signal_count=null_adjusted_signal_count,
        diagnostic_row_count=diagnostic_row_count,
        negative_control_row_count=negative_control_row_count,
        null_model_row_count=null_model_row_count,
    )

    lesson_payload = {
        "research_branch": "GENERIC_FRAMEWORK_RESEARCH",
        "plugin_key": plugin_key,
        "research_key": research_key,
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "runner_status": runner_status,
        "decision_class": decision["decision_class"],
        "feature_count": feature_count,
        "diagnostic_row_count": diagnostic_row_count,
        "negative_control_row_count": negative_control_row_count,
        "null_model_row_count": null_model_row_count,
        "strict_preview_count": strict_preview_count,
        "null_adjusted_signal_count": null_adjusted_signal_count,
    }

    lesson_id = f"LESSON_GENERIC_RESEARCH_{stable_hash(lesson_payload)}"

    if not valid_input:
        evaluator_status = "GENERIC_RESEARCH_EVALUATOR_INVALID_OR_INCOMPLETE_INPUT"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "RERUN_OR_INSPECT_GENERIC_RESEARCH_RUNNER_NO_RELEASE"
        reason = (
            f"runner_missing={runner_missing}; runner_error={runner_error}; "
            f"runner_status={runner_status}; canonical_policy_month_count={canonical_policy_month_count}; "
            f"guard_pass={bool(guard_feed.get('guard_pass'))}; route_hash_present={bool(route_hash)}"
        )
        branch_closed = False
        route_blocklist_required = False
        next_key = None
        next_module = None
        interpretation = "Generic research evaluator could not trust runner input."
        return_code = 2
    else:
        decision_class = decision["decision_class"]
        branch_closed = bool(decision["branch_closed"])
        route_blocklist_required = bool(decision["route_blocklist_required"])
        next_key = decision["next_recommended_research_key"]
        next_module = decision["next_module"]
        next_action = decision["next_action"]

        if null_adjusted_signal_count > 0:
            evaluator_status = "GENERIC_RESEARCH_EVALUATOR_SIGNAL_REQUIRES_DEEP_VALIDATION"
            severity = "ATTENTION"
            interpretation = (
                "A null-adjusted diagnostic signal exists, but this still cannot create a candidate or release. "
                "Only deep validation contract is allowed."
            )
        elif branch_closed:
            evaluator_status = "GENERIC_RESEARCH_EVALUATOR_PLUGIN_ROUTE_CLOSED_NO_SIGNAL"
            severity = "ATTENTION"
            interpretation = (
                "The generic framework route ran with guard feed, negative controls, and null models. "
                "It found no strict 12/12 signal and no null-adjusted signal. "
                "This plugin route is closed/blocked unless materially changed."
            )
        else:
            evaluator_status = "GENERIC_RESEARCH_EVALUATOR_ATTENTION"
            severity = "ATTENTION"
            interpretation = "Generic research route needs follow-up review."

        allowed_scope = "READ_ONLY_RESEARCH"
        reason = decision["reason"]
        return_code = 0

    lesson_record = {
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "lesson_type": "GENERIC_FRAMEWORK_RESEARCH_RESULT",
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "plugin_key": plugin_key,
        "research_key": research_key,
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "runner_status": runner_status,
        "evaluator_status": evaluator_status,
        "decision_class": decision.get("decision_class"),
        "branch_closed": branch_closed,
        "route_blocklist_required": route_blocklist_required,
        "feature_count": feature_count,
        "diagnostic_row_count": diagnostic_row_count,
        "negative_control_row_count": negative_control_row_count,
        "null_model_row_count": null_model_row_count,
        "strict_12_feature_signal_preview_count": strict_preview_count,
        "null_adjusted_signal_count": null_adjusted_signal_count,
        "interpretation": interpretation,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        "source_runner_json": str(RUNNER_JSON),
        "source_contract_json": str(CONTRACT_JSON),
        "source_guard_feed_json": str(GUARD_FEED_JSON),
    }

    block_record = {
        "route_hash": route_hash,
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "blocked_reason": "GENERIC_RESEARCH_NO_STRICT_OR_NULL_ADJUSTED_SIGNAL",
        "research_branch": "GENERIC_FRAMEWORK_RESEARCH",
        "plugin_key": plugin_key,
        "research_key": research_key,
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "feature_count": feature_count,
        "diagnostic_row_count": diagnostic_row_count,
        "negative_control_row_count": negative_control_row_count,
        "null_model_row_count": null_model_row_count,
        "strict_12_feature_signal_preview_count": strict_preview_count,
        "null_adjusted_signal_count": null_adjusted_signal_count,
        "reopen_requirements": [
            "materially different plugin config",
            "new route hash",
            "data quality guard consumed",
            "negative controls included",
            "null models included",
            "strict 12/12 canonical preview",
            "null-adjusted signal confirmation",
            "deep validation before any candidate/family/runtime/capital/live action",
        ],
    }

    lesson_append_status = None
    blocklist_append_status = None

    if valid_input:
        write_json(SPECIFIC_LESSON_PATH, lesson_record)
        lesson_append_status = append_lesson_record(LESSON_INDEX_PATH, lesson_record)

        if route_blocklist_required and route_hash:
            blocklist_append_status = append_blocklist_record(BLOCKLIST_PATH, block_record)

    next_queue = {
        "created_at_utc": utc_now_iso(),
        "queue_status": "GENERIC_RESEARCH_NEXT_QUEUE_READY" if valid_input else "GENERIC_RESEARCH_NEXT_QUEUE_BLOCKED",
        "source_evaluator": "edge_factory_os_generic_research_evaluator_v1",
        "source_route_hash": route_hash,
        "source_lesson_id": lesson_id,
        "decision_class": decision.get("decision_class"),
        "branch_closed": branch_closed,
        "route_blocklist_required": route_blocklist_required,
        "strict_policy_key": STRICT_POLICY_KEY,
        "top_next_research_key": next_key,
        "top_next_module": next_module,
        "next_direction_queue": [
            {
                "research_key": next_key,
                "priority": 100,
                "next_module_recommendation": next_module,
                "allowed_scope": "READ_ONLY_RESEARCH",
                "why": decision.get("reason"),
                "must_consume_guard_feed": True,
                "must_not_reopen_blocked_routes": True,
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
                "priority": 80,
                "next_module_recommendation": ALT_MODULE,
                "allowed_scope": "READ_ONLY_RESEARCH",
                "why": "Alternative: expand guarded feature plugin materially if null/permutation baseline says the initial feature space was too narrow.",
                "must_consume_guard_feed": True,
                "must_not_reopen_blocked_routes": True,
                "candidate_generation_allowed_now": False,
                "family_release_allowed_now": False,
            },
        ] if next_key and next_module else [],
        "candidate_generation_allowed": False,
        "candidate_contract_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
    }

    if valid_input:
        write_json(NEXT_QUEUE_JSON, next_queue)

    result = {
        "evaluator_name": "edge_factory_os_generic_research_evaluator_v1",
        "created_at_utc": utc_now_iso(),
        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "decision_class": decision.get("decision_class"),
        "branch_closed": branch_closed,
        "route_blocklist_required": route_blocklist_required,
        "interpretation": interpretation,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "runner_status": runner_status,
        "plugin_key": plugin_key,
        "research_key": research_key,
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "feature_count": feature_count,
        "diagnostic_row_count": diagnostic_row_count,
        "negative_control_row_count": negative_control_row_count,
        "null_model_row_count": null_model_row_count,
        "strict_12_feature_signal_preview_count": strict_preview_count,
        "null_adjusted_signal_count": null_adjusted_signal_count,
        "lesson_id": lesson_id,
        "lesson_written": bool(valid_input),
        "blocklist_written": bool(valid_input and route_blocklist_required and route_hash),
        "lesson_append_status": lesson_append_status,
        "blocklist_append_status": blocklist_append_status,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        "release_gate_feed": {
            "GENERIC_RESEARCH_EVALUATOR_RAN": True,
            "GENERIC_RESEARCH_BRANCH_CLOSED": branch_closed,
            "GENERIC_RESEARCH_ROUTE_BLOCKLIST_REQUIRED": route_blocklist_required,
            "STRICT_MONTH_STABILITY_12_OF_12": True,
            "STRICT_12_FEATURE_SIGNAL_PREVIEW_COUNT": strict_preview_count,
            "NULL_ADJUSTED_SIGNAL_COUNT": null_adjusted_signal_count,
            "RELEASE_PASS_FROM_THIS_EVALUATOR": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_THIS_EVALUATOR": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_THIS_EVALUATOR": False,
            "FAMILY_RELEASE_ALLOWED_FROM_THIS_EVALUATOR": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_THIS_EVALUATOR": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_THIS_EVALUATOR": False,
            "ACTIVE_PAPER_ALLOWED_FROM_THIS_EVALUATOR": False,
            "LIVE_ALLOWED_FROM_THIS_EVALUATOR": False,
            "REAL_ORDERS_ALLOWED_FROM_THIS_EVALUATOR": False,
        },
        "input_paths": {
            "runner_json": str(RUNNER_JSON),
            "contract_json": str(CONTRACT_JSON),
            "guard_feed_json": str(GUARD_FEED_JSON),
        },
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "next_queue_json": str(NEXT_QUEUE_JSON),
        "lesson_index_path": str(LESSON_INDEX_PATH),
        "blocklist_path": str(BLOCKLIST_PATH),
        "specific_lesson_path": str(SPECIFIC_LESSON_PATH),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text_summary(OUT_TXT, result)
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
