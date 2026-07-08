#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Null Baseline Method Repair Evaluator v1

Purpose:
- Consume Null Baseline Method Repair Runner v1 output.
- Record failed repaired-method policy gates.
- Keep plugin expansion blocked.
- Distinguish summary-row repair failure from true source-panel empirical replay requirement.
- Queue a true source-panel / row-month empirical null baseline contract.
- Keep all candidate/family/runtime/capital/live/real-order actions blocked.

This evaluator does NOT:
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

import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

RUNNER_JSON = (
    BASE_DIR
    / "edge_factory_os_null_baseline_method_repair_runner"
    / "null_baseline_method_repair_runner_latest.json"
)

REPAIRED_SUMMARY_CSV = (
    BASE_DIR
    / "edge_factory_os_null_baseline_method_repair_runner"
    / "null_baseline_repair_false_positive_summary_latest.csv"
)

POLICY_GATE_CSV = (
    BASE_DIR
    / "edge_factory_os_null_baseline_method_repair_runner"
    / "null_baseline_repair_policy_gate_pass_fail_latest.csv"
)

INPUT_INVENTORY_CSV = (
    BASE_DIR
    / "edge_factory_os_null_baseline_method_repair_runner"
    / "null_baseline_repair_input_inventory_latest.csv"
)

METHOD_INVENTORY_CSV = (
    BASE_DIR
    / "edge_factory_os_null_baseline_method_repair_runner"
    / "null_baseline_repair_method_inventory_latest.csv"
)

CONTRACT_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "contracts"
    / "null_baseline_method_repair_contract_v1.json"
)

POLICY_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_enforcement_policy_v1.json"
)

METHOD_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "null_baseline_method_state_v1.json"
)

VALIDATION_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_validation_state_v1.json"
)

GUARD_FEED_JSON = (
    BASE_DIR
    / "edge_factory_os_data_quality_guard_runner"
    / "data_quality_guard_feed_latest.json"
)

GENERIC_RUNNER_JSON = (
    BASE_DIR
    / "edge_factory_os_generic_research_runner"
    / "generic_research_runner_latest.json"
)

LESSON_DIR = BASE_DIR / "edge_factory_os_lesson_memory"
LESSON_INDEX_PATH = LESSON_DIR / "lesson_memory_index.json"
BLOCKLIST_PATH = LESSON_DIR / "candidate_route_blocklist.json"
SPECIFIC_LESSON_PATH = LESSON_DIR / "null_baseline_method_repair_failed_lesson_latest.json"

OUT_DIR = BASE_DIR / "edge_factory_os_null_baseline_method_repair_evaluator"
OUT_JSON = OUT_DIR / "null_baseline_method_repair_evaluator_latest.json"
OUT_TXT = OUT_DIR / "null_baseline_method_repair_evaluator_latest.txt"
NEXT_QUEUE_JSON = OUT_DIR / "null_baseline_method_repair_next_queue_latest.json"

FRAMEWORK_POLICY_DIR = REPO_DIR / "edge_factory_os_framework" / "policies"
REPAIR_STATE_JSON = FRAMEWORK_POLICY_DIR / "null_baseline_method_repair_state_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD5_06B_TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_CONTRACT"
NEXT_MODULE = "edge_factory_os_true_source_panel_empirical_null_baseline_contract_builder_v1.py"

ALT_RESEARCH_KEY = "RD5_07_FRAMEWORK_STATUS_PANEL_AND_STACK_INTEGRATION"
ALT_MODULE = "edge_factory_os_framework_status_panel_builder_v1.py"

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


def stable_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y", "pass"}


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


def classify_repair_result(
    runner: Dict[str, Any],
    gate_rows: List[Dict[str, Any]],
    repaired_summary_rows: List[Dict[str, Any]],
    input_inventory_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    repair_gate_pass = bool(runner.get("repair_policy_gate_pass"))
    max_strict = to_float(runner.get("max_strict_12_any_random_hit_rate"), 1.0)
    max_null = to_float(runner.get("max_null_adjusted_any_random_hit_rate"), 1.0)

    failed_gate_keys = runner.get("failed_gate_keys")
    if not isinstance(failed_gate_keys, list):
        failed_gate_keys = [
            row.get("gate_key")
            for row in gate_rows
            if not to_bool(row.get("passed"))
        ]

    actual_signal_missing = "ACTUAL_SIGNAL_PRESENT" in failed_gate_keys
    strict_rate_failed = "STRICT_12_RANDOM_HIT_RATE_CAP" in failed_gate_keys
    null_rate_failed = "NULL_ADJUSTED_RANDOM_HIT_RATE_CAP" in failed_gate_keys

    # Detect whether v1 repair only had summary diagnostics/control rows, not true source panel rows.
    inventory_names = [str(x.get("artifact")) for x in input_inventory_rows]
    has_true_source_panel_rows = any(
        "source_panel" in name or "row_level" in name or "panel_rows" in name
        for name in inventory_names
    )

    if not repair_gate_pass and strict_rate_failed and null_rate_failed and actual_signal_missing:
        return {
            "decision_class": "REPAIRED_METHOD_POLICY_GATES_FAIL_TRUE_SOURCE_PANEL_REPLAY_REQUIRED",
            "branch_closed": True,
            "route_blocklist_required": True,
            "method_repair_v1_failed": True,
            "true_source_panel_replay_required": True,
            "plugin_expansion_allowed": False,
            "next_recommended_research_key": NEXT_RESEARCH_KEY,
            "next_module": NEXT_MODULE,
            "next_action": "BUILD_TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_CONTRACT_NO_RELEASE",
            "reason": (
                "Repaired v1 method still fails strict/null false-positive caps and has no actual signal. "
                "Because v1 repair is based on diagnostic/control summary rows, the next step must use true source-panel row/month replay."
            ),
            "has_true_source_panel_rows": has_true_source_panel_rows,
        }

    if not repair_gate_pass:
        return {
            "decision_class": "REPAIRED_METHOD_POLICY_GATES_FAIL_PLUGIN_EXPANSION_BLOCKED",
            "branch_closed": True,
            "route_blocklist_required": True,
            "method_repair_v1_failed": True,
            "true_source_panel_replay_required": True,
            "plugin_expansion_allowed": False,
            "next_recommended_research_key": NEXT_RESEARCH_KEY,
            "next_module": NEXT_MODULE,
            "next_action": "BUILD_TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_CONTRACT_NO_RELEASE",
            "reason": (
                f"Repaired v1 method failed policy gates {failed_gate_keys}. "
                "Plugin expansion remains blocked."
            ),
            "has_true_source_panel_rows": has_true_source_panel_rows,
        }

    return {
        "decision_class": "REPAIRED_METHOD_POLICY_GATES_PASS_REVIEW_ONLY",
        "branch_closed": False,
        "route_blocklist_required": False,
        "method_repair_v1_failed": False,
        "true_source_panel_replay_required": False,
        "plugin_expansion_allowed": False,
        "next_recommended_research_key": ALT_RESEARCH_KEY,
        "next_module": ALT_MODULE,
        "next_action": "BUILD_FRAMEWORK_STATUS_PANEL_AND_STACK_INTEGRATION",
        "reason": (
            "Repaired v1 method passed policy gates, but plugin expansion still remains blocked until framework status integration and future validator approval."
        ),
        "has_true_source_panel_rows": has_true_source_panel_rows,
    }


def build_repair_state(
    *,
    runner: Dict[str, Any],
    decision: Dict[str, Any],
    policy: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "state_name": "edge_factory_os_null_baseline_method_repair_state_v1",
        "created_at_utc": utc_now_iso(),
        "repair_state": (
            "NULL_BASELINE_METHOD_REPAIR_V1_FAILED_TRUE_SOURCE_PANEL_REPLAY_REQUIRED"
            if decision.get("method_repair_v1_failed")
            else "NULL_BASELINE_METHOD_REPAIR_V1_PASS_REVIEW_ONLY"
        ),
        "decision_class": decision.get("decision_class"),
        "policy_hash": policy.get("policy_hash"),
        "source_runner_status": runner.get("runner_status"),
        "repair_policy_gate_pass": bool(runner.get("repair_policy_gate_pass")),
        "failed_gate_keys": runner.get("failed_gate_keys"),
        "max_strict_12_any_random_hit_rate": runner.get("max_strict_12_any_random_hit_rate"),
        "max_null_adjusted_any_random_hit_rate": runner.get("max_null_adjusted_any_random_hit_rate"),
        "method_repair_v1_failed": bool(decision.get("method_repair_v1_failed")),
        "true_source_panel_replay_required": bool(decision.get("true_source_panel_replay_required")),
        "plugin_expansion_allowed": False,
        "candidate_generation_allowed": False,
        "candidate_contract_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        "next_recommended_research_key": decision.get("next_recommended_research_key"),
        "next_module": decision.get("next_module"),
    }


def build_text_summary(result: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS NULL BASELINE METHOD REPAIR EVALUATOR v1")
    lines.append("=" * 100)

    for key in [
        "evaluator_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "decision_class",
        "branch_closed",
        "route_blocklist_required",
        "method_repair_v1_failed",
        "true_source_panel_replay_required",
        "plugin_expansion_allowed",
        "runner_status",
        "contract_id",
        "route_hash",
        "research_key",
        "plugin_key",
        "policy_hash",
        "repair_policy_gate_pass",
        "repair_policy_gate_fail_count",
        "failed_gate_keys",
        "max_strict_12_any_random_hit_rate",
        "max_null_adjusted_any_random_hit_rate",
        "repair_method_count",
        "empirical_replay_runs_per_method",
        "total_empirical_replay_run_rows",
        "next_recommended_research_key",
        "next_module",
        "lesson_id",
    ]:
        lines.append(f"{key}: {result.get(key)}")

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
    for key in [
        "output_json",
        "output_txt",
        "next_queue_json",
        "repair_state_json",
        "specific_lesson_path",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS NULL BASELINE METHOD REPAIR EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {result.get('evaluator_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"decision_class: {result.get('decision_class')}")
    print(f"branch_closed: {result.get('branch_closed')}")
    print(f"route_blocklist_required: {result.get('route_blocklist_required')}")
    print(f"method_repair_v1_failed: {result.get('method_repair_v1_failed')}")
    print(f"true_source_panel_replay_required: {result.get('true_source_panel_replay_required')}")
    print(f"plugin_expansion_allowed: {result.get('plugin_expansion_allowed')}")
    print(f"repair_policy_gate_pass: {result.get('repair_policy_gate_pass')}")
    print(f"repair_policy_gate_fail_count: {result.get('repair_policy_gate_fail_count')}")
    print(f"failed_gate_keys: {result.get('failed_gate_keys')}")
    print(f"max_strict_12_any_random_hit_rate: {result.get('max_strict_12_any_random_hit_rate')}")
    print(f"max_null_adjusted_any_random_hit_rate: {result.get('max_null_adjusted_any_random_hit_rate')}")
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
    print(f"REPAIR_STATE: {result.get('repair_state_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LESSON_DIR.mkdir(parents=True, exist_ok=True)
    FRAMEWORK_POLICY_DIR.mkdir(parents=True, exist_ok=True)

    runner = load_json(RUNNER_JSON, default={})
    contract = load_json(CONTRACT_JSON, default={})
    policy = load_json(POLICY_JSON, default={})
    method_state = load_json(METHOD_STATE_JSON, default={})
    validation_state = load_json(VALIDATION_STATE_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})
    generic_runner = load_json(GENERIC_RUNNER_JSON, default={})

    repaired_summary_rows = read_csv_rows(REPAIRED_SUMMARY_CSV)
    gate_rows = read_csv_rows(POLICY_GATE_CSV)
    input_inventory_rows = read_csv_rows(INPUT_INVENTORY_CSV)
    method_inventory_rows = read_csv_rows(METHOD_INVENTORY_CSV)

    runner_status = str(runner.get("runner_status", ""))
    runner_missing = not RUNNER_JSON.exists()
    runner_error = "ERROR" in runner_status.upper()

    contract_id = runner.get("contract_id") or contract.get("contract_id")
    contract_hash = runner.get("contract_hash") or contract.get("contract_hash")
    route_hash = runner.get("route_hash") or contract.get("route_hash")
    research_key = runner.get("research_key") or contract.get("research_key")
    plugin_key = runner.get("plugin_key") or contract.get("plugin_key")
    policy_hash = runner.get("policy_hash") or contract.get("policy_hash") or policy.get("policy_hash")

    repair_policy_gate_pass = bool(runner.get("repair_policy_gate_pass"))
    repair_policy_gate_fail_count = to_int(runner.get("repair_policy_gate_fail_count"))
    failed_gate_keys = runner.get("failed_gate_keys")
    if not isinstance(failed_gate_keys, list):
        failed_gate_keys = [
            row.get("gate_key")
            for row in gate_rows
            if not to_bool(row.get("passed"))
        ]

    max_strict_rate = to_float(runner.get("max_strict_12_any_random_hit_rate"), 1.0)
    max_null_rate = to_float(runner.get("max_null_adjusted_any_random_hit_rate"), 1.0)

    repair_method_count = to_int(runner.get("repair_method_count"))
    empirical_replay_runs_per_method = to_int(runner.get("empirical_replay_runs_per_method"))
    total_empirical_replay_run_rows = to_int(runner.get("total_empirical_replay_run_rows"))

    valid_input = (
        not runner_missing
        and not runner_error
        and runner_status.startswith("NULL_BASELINE_METHOD_REPAIR_RUNNER_")
        and bool(route_hash)
        and bool(guard_feed.get("guard_pass"))
        and bool(validation_state.get("validator_pass"))
        and bool(method_state.get("method_repair_required"))
        and repair_method_count >= 8
        and empirical_replay_runs_per_method >= 1000
        and total_empirical_replay_run_rows >= 8000
    )

    decision = classify_repair_result(
        runner=runner,
        gate_rows=gate_rows,
        repaired_summary_rows=repaired_summary_rows,
        input_inventory_rows=input_inventory_rows,
    )

    if not valid_input:
        evaluator_status = "NULL_BASELINE_METHOD_REPAIR_EVALUATOR_INVALID_OR_INCOMPLETE_INPUT"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "RERUN_OR_INSPECT_NULL_BASELINE_METHOD_REPAIR_RUNNER_NO_RELEASE"
        reason = (
            f"runner_missing={runner_missing}; runner_error={runner_error}; runner_status={runner_status}; "
            f"route_hash_present={bool(route_hash)}; guard_pass={bool(guard_feed.get('guard_pass'))}; "
            f"validator_pass={bool(validation_state.get('validator_pass'))}; "
            f"method_repair_required={bool(method_state.get('method_repair_required'))}; "
            f"repair_method_count={repair_method_count}; empirical_replay_runs_per_method={empirical_replay_runs_per_method}; "
            f"total_empirical_replay_run_rows={total_empirical_replay_run_rows}"
        )
        interpretation = "Evaluator could not trust method repair runner input."
        return_code = 2
    else:
        if decision["method_repair_v1_failed"]:
            evaluator_status = "NULL_BASELINE_METHOD_REPAIR_EVALUATOR_REPAIR_V1_FAILED_TRUE_SOURCE_PANEL_REQUIRED"
            interpretation = (
                "Null baseline repair v1 consumed policy/guard/method state and ran empirical replay over available diagnostic/control summaries. "
                "It still failed strict/null false-positive caps and still has no actual signal. "
                "Because the input is summary-level rather than true source-panel rows/month buckets, the next required step is a true source-panel empirical null baseline contract."
            )
        else:
            evaluator_status = "NULL_BASELINE_METHOD_REPAIR_EVALUATOR_REPAIR_V1_PASS_REVIEW_ONLY"
            interpretation = (
                "Null baseline repair v1 passed policy gates, but plugin expansion remains blocked until framework status integration and future validator approval."
            )

        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = decision["next_action"]
        reason = decision["reason"]
        return_code = 0

    repair_state = build_repair_state(runner=runner, decision=decision, policy=policy)
    if valid_input:
        write_json(REPAIR_STATE_JSON, repair_state)

    lesson_payload = {
        "runner_status": runner_status,
        "repair_policy_gate_pass": repair_policy_gate_pass,
        "failed_gate_keys": failed_gate_keys,
        "max_strict_rate": max_strict_rate,
        "max_null_rate": max_null_rate,
        "route_hash": route_hash,
        "decision_class": decision["decision_class"],
    }
    lesson_id = f"LESSON_NULL_BASELINE_REPAIR_{stable_hash(lesson_payload)}"

    lesson_record = {
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "lesson_type": "NULL_BASELINE_METHOD_REPAIR_EVALUATED",
        "strict_policy_key": STRICT_POLICY_KEY,
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "research_key": research_key,
        "plugin_key": plugin_key,
        "policy_hash": policy_hash,
        "runner_status": runner_status,
        "evaluator_status": evaluator_status,
        "decision_class": decision["decision_class"],
        "repair_policy_gate_pass": repair_policy_gate_pass,
        "repair_policy_gate_fail_count": repair_policy_gate_fail_count,
        "failed_gate_keys": failed_gate_keys,
        "max_strict_12_any_random_hit_rate": max_strict_rate,
        "max_null_adjusted_any_random_hit_rate": max_null_rate,
        "repair_method_count": repair_method_count,
        "empirical_replay_runs_per_method": empirical_replay_runs_per_method,
        "total_empirical_replay_run_rows": total_empirical_replay_run_rows,
        "method_repair_v1_failed": bool(decision["method_repair_v1_failed"]),
        "true_source_panel_replay_required": bool(decision["true_source_panel_replay_required"]),
        "plugin_expansion_allowed": False,
        "interpretation": interpretation,
        "next_recommended_research_key": decision["next_recommended_research_key"],
        "next_module": decision["next_module"],
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
    }

    block_record = {
        "route_hash": route_hash,
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "blocked_reason": "NULL_BASELINE_METHOD_REPAIR_V1_FAILED_OR_REVIEW_REQUIRED",
        "research_branch": "NULL_BASELINE_METHOD_REPAIR",
        "research_key": research_key,
        "plugin_key": plugin_key,
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "policy_hash": policy_hash,
        "repair_policy_gate_pass": repair_policy_gate_pass,
        "failed_gate_keys": failed_gate_keys,
        "plugin_expansion_allowed": False,
        "reopen_requirements": [
            "true source-panel row/month empirical replay contract completed",
            "policy and guard consumed",
            "false-positive rates below policy caps",
            "actual signal present before any signal claim",
            "no candidate/family/runtime/capital/live action",
        ],
    }

    lesson_append_status = None
    blocklist_append_status = None

    if valid_input:
        write_json(SPECIFIC_LESSON_PATH, lesson_record)
        lesson_append_status = append_lesson_record(LESSON_INDEX_PATH, lesson_record)

        if decision["route_blocklist_required"] and route_hash:
            blocklist_append_status = append_blocklist_record(BLOCKLIST_PATH, block_record)

    next_queue = {
        "created_at_utc": utc_now_iso(),
        "queue_status": "NULL_BASELINE_METHOD_REPAIR_NEXT_QUEUE_READY" if valid_input else "NULL_BASELINE_METHOD_REPAIR_NEXT_QUEUE_BLOCKED",
        "source_evaluator": "edge_factory_os_null_baseline_method_repair_evaluator_v1",
        "source_route_hash": route_hash,
        "source_lesson_id": lesson_id,
        "decision_class": decision["decision_class"],
        "method_repair_v1_failed": bool(decision["method_repair_v1_failed"]),
        "true_source_panel_replay_required": bool(decision["true_source_panel_replay_required"]),
        "plugin_expansion_allowed": False,
        "top_next_research_key": decision["next_recommended_research_key"],
        "top_next_module": decision["next_module"],
        "next_direction_queue": [
            {
                "research_key": decision["next_recommended_research_key"],
                "priority": 100,
                "next_module_recommendation": decision["next_module"],
                "allowed_scope": "READ_ONLY_RESEARCH",
                "why": decision["reason"],
                "must_consume_guard_feed": True,
                "must_consume_research_gate_policy": True,
                "must_use_true_source_panel_rows_or_month_buckets": bool(decision["true_source_panel_replay_required"]),
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
                "why": "Expose blocked method-repair state to standard stack/control tower.",
                "must_consume_guard_feed": True,
                "must_consume_research_gate_policy": True,
                "plugin_expansion_allowed_now": False,
                "candidate_generation_allowed_now": False,
                "family_release_allowed_now": False,
            },
        ] if valid_input else [],
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
        "evaluator_name": "edge_factory_os_null_baseline_method_repair_evaluator_v1",
        "created_at_utc": utc_now_iso(),
        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "decision_class": decision["decision_class"],
        "branch_closed": bool(decision["branch_closed"]),
        "route_blocklist_required": bool(decision["route_blocklist_required"]),
        "method_repair_v1_failed": bool(decision["method_repair_v1_failed"]),
        "true_source_panel_replay_required": bool(decision["true_source_panel_replay_required"]),
        "has_true_source_panel_rows": bool(decision["has_true_source_panel_rows"]),
        "plugin_expansion_allowed": False,
        "interpretation": interpretation,
        "strict_policy_key": STRICT_POLICY_KEY,
        "runner_status": runner_status,
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "research_key": research_key,
        "plugin_key": plugin_key,
        "policy_hash": policy_hash,
        "repair_policy_gate_pass": repair_policy_gate_pass,
        "repair_policy_gate_fail_count": repair_policy_gate_fail_count,
        "failed_gate_keys": failed_gate_keys,
        "max_strict_12_any_random_hit_rate": max_strict_rate,
        "max_null_adjusted_any_random_hit_rate": max_null_rate,
        "repair_method_count": repair_method_count,
        "empirical_replay_runs_per_method": empirical_replay_runs_per_method,
        "total_empirical_replay_run_rows": total_empirical_replay_run_rows,
        "repaired_summary_row_count": len(repaired_summary_rows),
        "policy_gate_row_count": len(gate_rows),
        "input_inventory_row_count": len(input_inventory_rows),
        "method_inventory_row_count": len(method_inventory_rows),
        "generic_runner_status": generic_runner.get("runner_status"),
        "generic_diagnostic_row_count": generic_runner.get("diagnostic_row_count"),
        "generic_negative_control_row_count": generic_runner.get("negative_control_row_count"),
        "lesson_id": lesson_id,
        "lesson_written": bool(valid_input),
        "lesson_append_status": lesson_append_status,
        "blocklist_written": bool(valid_input and decision["route_blocklist_required"] and route_hash),
        "blocklist_append_status": blocklist_append_status,
        "next_recommended_research_key": decision["next_recommended_research_key"],
        "next_module": decision["next_module"],
        "repair_state": repair_state,
        "release_gate_feed": {
            "NULL_BASELINE_METHOD_REPAIR_EVALUATOR_RAN": True,
            "NULL_BASELINE_METHOD_REPAIR_V1_FAILED": bool(decision["method_repair_v1_failed"]),
            "TRUE_SOURCE_PANEL_REPLAY_REQUIRED": bool(decision["true_source_panel_replay_required"]),
            "PLUGIN_EXPANSION_ALLOWED": False,
            "STRICT_MONTH_STABILITY_12_OF_12": True,
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
            "repaired_summary_csv": str(REPAIRED_SUMMARY_CSV),
            "policy_gate_csv": str(POLICY_GATE_CSV),
            "input_inventory_csv": str(INPUT_INVENTORY_CSV),
            "method_inventory_csv": str(METHOD_INVENTORY_CSV),
            "contract_json": str(CONTRACT_JSON),
            "policy_json": str(POLICY_JSON),
            "method_state_json": str(METHOD_STATE_JSON),
            "validation_state_json": str(VALIDATION_STATE_JSON),
            "guard_feed_json": str(GUARD_FEED_JSON),
            "generic_runner_json": str(GENERIC_RUNNER_JSON),
        },
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "next_queue_json": str(NEXT_QUEUE_JSON),
        "repair_state_json": str(REPAIR_STATE_JSON),
        "specific_lesson_path": str(SPECIFIC_LESSON_PATH),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text_summary(result))
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
