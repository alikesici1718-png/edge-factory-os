#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - True Source Panel Empirical Null Baseline Evaluator v1

Purpose:
- Consume True Source Panel Empirical Null Baseline Runner v1.
- Evaluate whether the true source-panel empirical null baseline fixed false-positive methodology.
- Distinguish:
  1) false-positive methodology repaired
  2) actual signal still absent
- Keep plugin expansion blocked.
- Queue framework status panel / policy-locked research queue.
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
    / "edge_factory_os_true_source_panel_empirical_null_baseline_runner"
    / "true_source_panel_empirical_null_baseline_runner_latest.json"
)

FALSE_POSITIVE_CSV = (
    BASE_DIR
    / "edge_factory_os_true_source_panel_empirical_null_baseline_runner"
    / "true_source_panel_empirical_false_positive_summary_latest.csv"
)

POLICY_GATE_CSV = (
    BASE_DIR
    / "edge_factory_os_true_source_panel_empirical_null_baseline_runner"
    / "true_source_panel_empirical_policy_gate_pass_fail_latest.csv"
)

PVALUE_CSV = (
    BASE_DIR
    / "edge_factory_os_true_source_panel_empirical_null_baseline_runner"
    / "true_source_panel_empirical_p_value_table_latest.csv"
)

SCHEMA_CSV = (
    BASE_DIR
    / "edge_factory_os_true_source_panel_empirical_null_baseline_runner"
    / "true_source_panel_schema_report_latest.csv"
)

COVERAGE_CSV = (
    BASE_DIR
    / "edge_factory_os_true_source_panel_empirical_null_baseline_runner"
    / "true_source_panel_month_symbol_coverage_latest.csv"
)

METHOD_INVENTORY_CSV = (
    BASE_DIR
    / "edge_factory_os_true_source_panel_empirical_null_baseline_runner"
    / "true_source_panel_replay_method_inventory_latest.csv"
)

CONTRACT_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "contracts"
    / "true_source_panel_empirical_null_baseline_contract_v1.json"
)

POLICY_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_enforcement_policy_v1.json"
)

REPAIR_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "null_baseline_method_repair_state_v1.json"
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

LESSON_DIR = BASE_DIR / "edge_factory_os_lesson_memory"
LESSON_INDEX_PATH = LESSON_DIR / "lesson_memory_index.json"
BLOCKLIST_PATH = LESSON_DIR / "candidate_route_blocklist.json"
SPECIFIC_LESSON_PATH = LESSON_DIR / "true_source_panel_empirical_null_baseline_lesson_latest.json"

OUT_DIR = BASE_DIR / "edge_factory_os_true_source_panel_empirical_null_baseline_evaluator"
OUT_JSON = OUT_DIR / "true_source_panel_empirical_null_baseline_evaluator_latest.json"
OUT_TXT = OUT_DIR / "true_source_panel_empirical_null_baseline_evaluator_latest.txt"
NEXT_QUEUE_JSON = OUT_DIR / "true_source_panel_empirical_null_baseline_next_queue_latest.json"

FRAMEWORK_POLICY_DIR = REPO_DIR / "edge_factory_os_framework" / "policies"
TRUE_PANEL_STATE_JSON = FRAMEWORK_POLICY_DIR / "true_source_panel_empirical_null_baseline_state_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD5_07_FRAMEWORK_STATUS_PANEL_AND_STACK_INTEGRATION"
NEXT_MODULE = "edge_factory_os_framework_status_panel_builder_v1.py"

ALT_RESEARCH_KEY = "RD5_08_POLICY_LOCKED_NEW_RESEARCH_DIRECTION_QUEUE"
ALT_MODULE = "edge_factory_os_policy_locked_new_research_direction_queue_v1.py"

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


def classify_result(
    runner: Dict[str, Any],
    policy_gate_rows: List[Dict[str, Any]],
    false_positive_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    failed_gate_keys = runner.get("failed_gate_keys")
    if not isinstance(failed_gate_keys, list):
        failed_gate_keys = [
            row.get("gate_key")
            for row in policy_gate_rows
            if not to_bool(row.get("passed"))
        ]

    max_strict = to_float(runner.get("max_strict_12_any_random_hit_rate"), 1.0)
    max_null = to_float(runner.get("max_null_adjusted_any_random_hit_rate"), 1.0)
    panel_gate_pass = bool(runner.get("panel_empirical_policy_gate_pass"))

    false_positive_fixed = (
        max_strict <= 0.01
        and max_null <= 0.005
        and "STRICT_12_RANDOM_HIT_RATE_CAP" not in failed_gate_keys
        and "NULL_ADJUSTED_RANDOM_HIT_RATE_CAP" not in failed_gate_keys
    )

    actual_signal_present = "ACTUAL_SIGNAL_PRESENT" not in failed_gate_keys

    if false_positive_fixed and not actual_signal_present:
        return {
            "decision_class": "TRUE_SOURCE_PANEL_NULL_BASELINE_FALSE_POSITIVE_REPAIRED_NO_ACTUAL_SIGNAL",
            "false_positive_methodology_repaired": True,
            "actual_signal_present": False,
            "panel_empirical_policy_gate_pass": False,
            "branch_closed": True,
            "route_blocklist_required": True,
            "plugin_expansion_allowed": False,
            "next_recommended_research_key": NEXT_RESEARCH_KEY,
            "next_module": NEXT_MODULE,
            "next_action": "BUILD_FRAMEWORK_STATUS_PANEL_AND_STACK_INTEGRATION_NO_RELEASE",
            "reason": (
                "True source-panel replay repaired false-positive methodology: strict/null random hit rates are below caps. "
                "But actual signal is absent, so plugin expansion remains blocked and this research route is closed."
            ),
        }

    if panel_gate_pass and false_positive_fixed and actual_signal_present:
        return {
            "decision_class": "TRUE_SOURCE_PANEL_NULL_BASELINE_PASS_REVIEW_ONLY",
            "false_positive_methodology_repaired": True,
            "actual_signal_present": True,
            "panel_empirical_policy_gate_pass": True,
            "branch_closed": False,
            "route_blocklist_required": False,
            "plugin_expansion_allowed": False,
            "next_recommended_research_key": NEXT_RESEARCH_KEY,
            "next_module": NEXT_MODULE,
            "next_action": "BUILD_FRAMEWORK_STATUS_PANEL_AND_STACK_INTEGRATION_REVIEW_ONLY",
            "reason": (
                "True source-panel replay passed all policy gates, but plugin expansion remains blocked pending status integration and separate policy decision."
            ),
        }

    return {
        "decision_class": "TRUE_SOURCE_PANEL_NULL_BASELINE_FAILED_OR_INCONCLUSIVE",
        "false_positive_methodology_repaired": False,
        "actual_signal_present": actual_signal_present,
        "panel_empirical_policy_gate_pass": panel_gate_pass,
        "branch_closed": True,
        "route_blocklist_required": True,
        "plugin_expansion_allowed": False,
        "next_recommended_research_key": NEXT_RESEARCH_KEY,
        "next_module": NEXT_MODULE,
        "next_action": "BUILD_FRAMEWORK_STATUS_PANEL_AND_STACK_INTEGRATION_NO_RELEASE",
        "reason": (
            f"True source-panel replay did not fully validate methodology or signal. failed_gate_keys={failed_gate_keys}. "
            "Plugin expansion remains blocked."
        ),
    }


def build_true_panel_state(
    *,
    runner: Dict[str, Any],
    decision: Dict[str, Any],
    policy: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "state_name": "edge_factory_os_true_source_panel_empirical_null_baseline_state_v1",
        "created_at_utc": utc_now_iso(),
        "state_status": (
            "TRUE_SOURCE_PANEL_NULL_BASELINE_FALSE_POSITIVE_REPAIRED_NO_SIGNAL"
            if decision.get("false_positive_methodology_repaired") and not decision.get("actual_signal_present")
            else "TRUE_SOURCE_PANEL_NULL_BASELINE_REVIEW_REQUIRED"
        ),
        "decision_class": decision.get("decision_class"),
        "policy_hash": policy.get("policy_hash"),
        "source_runner_status": runner.get("runner_status"),
        "source_route_hash": runner.get("route_hash"),
        "false_positive_methodology_repaired": bool(decision.get("false_positive_methodology_repaired")),
        "actual_signal_present": bool(decision.get("actual_signal_present")),
        "panel_empirical_policy_gate_pass": bool(runner.get("panel_empirical_policy_gate_pass")),
        "failed_gate_keys": runner.get("failed_gate_keys"),
        "max_strict_12_any_random_hit_rate": runner.get("max_strict_12_any_random_hit_rate"),
        "max_null_adjusted_any_random_hit_rate": runner.get("max_null_adjusted_any_random_hit_rate"),
        "row_count": runner.get("row_count"),
        "symbol_count": runner.get("symbol_count"),
        "raw_calendar_month_count": runner.get("raw_calendar_month_count"),
        "canonical_policy_month_count": runner.get("canonical_policy_month_count"),
        "outcome_column": runner.get("outcome_column"),
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
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS TRUE SOURCE PANEL EMPIRICAL NULL BASELINE EVALUATOR v1")
    lines.append("=" * 100)

    for key in [
        "evaluator_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "decision_class",
        "false_positive_methodology_repaired",
        "actual_signal_present",
        "branch_closed",
        "route_blocklist_required",
        "plugin_expansion_allowed",
        "runner_status",
        "contract_id",
        "route_hash",
        "research_key",
        "plugin_key",
        "policy_hash",
        "panel_empirical_policy_gate_pass",
        "panel_empirical_policy_gate_fail_count",
        "failed_gate_keys",
        "max_strict_12_any_random_hit_rate",
        "max_null_adjusted_any_random_hit_rate",
        "row_count",
        "symbol_count",
        "raw_calendar_month_count",
        "canonical_policy_month_count",
        "outcome_column",
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
        "true_panel_state_json",
        "specific_lesson_path",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS TRUE SOURCE PANEL EMPIRICAL NULL BASELINE EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {result.get('evaluator_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"decision_class: {result.get('decision_class')}")
    print(f"false_positive_methodology_repaired: {result.get('false_positive_methodology_repaired')}")
    print(f"actual_signal_present: {result.get('actual_signal_present')}")
    print(f"branch_closed: {result.get('branch_closed')}")
    print(f"route_blocklist_required: {result.get('route_blocklist_required')}")
    print(f"plugin_expansion_allowed: {result.get('plugin_expansion_allowed')}")
    print(f"panel_empirical_policy_gate_pass: {result.get('panel_empirical_policy_gate_pass')}")
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
    print(f"STATE: {result.get('true_panel_state_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LESSON_DIR.mkdir(parents=True, exist_ok=True)
    FRAMEWORK_POLICY_DIR.mkdir(parents=True, exist_ok=True)

    runner = load_json(RUNNER_JSON, default={})
    contract = load_json(CONTRACT_JSON, default={})
    policy = load_json(POLICY_JSON, default={})
    repair_state = load_json(REPAIR_STATE_JSON, default={})
    validation_state = load_json(VALIDATION_STATE_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})

    false_positive_rows = read_csv_rows(FALSE_POSITIVE_CSV)
    policy_gate_rows = read_csv_rows(POLICY_GATE_CSV)
    pvalue_rows = read_csv_rows(PVALUE_CSV)
    schema_rows = read_csv_rows(SCHEMA_CSV)
    coverage_rows = read_csv_rows(COVERAGE_CSV)
    method_rows = read_csv_rows(METHOD_INVENTORY_CSV)

    runner_status = str(runner.get("runner_status", ""))
    runner_missing = not RUNNER_JSON.exists()
    runner_error = "ERROR" in runner_status.upper()

    contract_id = runner.get("contract_id") or contract.get("contract_id")
    contract_hash = runner.get("contract_hash") or contract.get("contract_hash")
    route_hash = runner.get("route_hash") or contract.get("route_hash")
    research_key = runner.get("research_key") or contract.get("research_key")
    plugin_key = runner.get("plugin_key") or contract.get("plugin_key")
    policy_hash = runner.get("policy_hash") or contract.get("policy_hash") or policy.get("policy_hash")

    failed_gate_keys = runner.get("failed_gate_keys")
    if not isinstance(failed_gate_keys, list):
        failed_gate_keys = [
            row.get("gate_key")
            for row in policy_gate_rows
            if not to_bool(row.get("passed"))
        ]

    max_strict_rate = to_float(runner.get("max_strict_12_any_random_hit_rate"), 1.0)
    max_null_rate = to_float(runner.get("max_null_adjusted_any_random_hit_rate"), 1.0)

    panel_empirical_policy_gate_pass = bool(runner.get("panel_empirical_policy_gate_pass"))
    panel_empirical_policy_gate_fail_count = to_int(runner.get("panel_empirical_policy_gate_fail_count"))

    row_count = to_int(runner.get("row_count"))
    symbol_count = to_int(runner.get("symbol_count"))
    raw_calendar_month_count = to_int(runner.get("raw_calendar_month_count"))
    canonical_policy_month_count = to_int(runner.get("canonical_policy_month_count"))
    replay_method_count = to_int(runner.get("replay_method_count"))
    empirical_replay_runs_per_method = to_int(runner.get("empirical_replay_runs_per_method"))
    total_empirical_replay_run_rows = to_int(runner.get("total_empirical_replay_run_rows"))

    valid_input = (
        not runner_missing
        and not runner_error
        and runner_status.startswith("TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_RUNNER_")
        and bool(route_hash)
        and bool(guard_feed.get("guard_pass"))
        and bool(validation_state.get("validator_pass"))
        and bool(repair_state.get("true_source_panel_replay_required"))
        and row_count >= 1000000
        and symbol_count >= 200
        and canonical_policy_month_count == 12
        and replay_method_count >= 8
        and empirical_replay_runs_per_method >= 1000
        and total_empirical_replay_run_rows >= 8000
    )

    decision = classify_result(
        runner=runner,
        policy_gate_rows=policy_gate_rows,
        false_positive_rows=false_positive_rows,
    )

    if not valid_input:
        evaluator_status = "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_EVALUATOR_INVALID_OR_INCOMPLETE_INPUT"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "RERUN_OR_INSPECT_TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_RUNNER_NO_RELEASE"
        reason = (
            f"runner_missing={runner_missing}; runner_error={runner_error}; runner_status={runner_status}; "
            f"route_hash_present={bool(route_hash)}; guard_pass={bool(guard_feed.get('guard_pass'))}; "
            f"validator_pass={bool(validation_state.get('validator_pass'))}; "
            f"true_source_panel_replay_required={bool(repair_state.get('true_source_panel_replay_required'))}; "
            f"row_count={row_count}; symbol_count={symbol_count}; canonical_months={canonical_policy_month_count}; "
            f"replay_method_count={replay_method_count}; runs_per_method={empirical_replay_runs_per_method}; "
            f"total_rows={total_empirical_replay_run_rows}"
        )
        interpretation = "Evaluator could not trust true source-panel empirical null baseline runner input."
        return_code = 2
    else:
        if decision["false_positive_methodology_repaired"] and not decision["actual_signal_present"]:
            evaluator_status = "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_EVALUATOR_FALSE_POSITIVE_REPAIRED_NO_ACTUAL_SIGNAL"
            interpretation = (
                "The true source-panel empirical replay fixed the false-positive baseline problem: strict and null-adjusted random hit rates are below policy caps. "
                "However, the tested research/plugin route still has no actual signal, so this route remains closed and plugin expansion stays blocked."
            )
        elif decision["panel_empirical_policy_gate_pass"]:
            evaluator_status = "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_EVALUATOR_POLICY_GATES_PASS_REVIEW_ONLY"
            interpretation = (
                "The true source-panel empirical replay passed all policy gates. Plugin expansion still remains blocked until separate framework status and policy decision."
            )
        else:
            evaluator_status = "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_EVALUATOR_FAILED_OR_INCONCLUSIVE"
            interpretation = (
                "The true source-panel empirical replay did not fully validate methodology/signal. Plugin expansion remains blocked."
            )

        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = decision["next_action"]
        reason = decision["reason"]
        return_code = 0

    true_panel_state = build_true_panel_state(runner=runner, decision=decision, policy=policy)
    if valid_input:
        write_json(TRUE_PANEL_STATE_JSON, true_panel_state)

    lesson_payload = {
        "runner_status": runner_status,
        "panel_empirical_policy_gate_pass": panel_empirical_policy_gate_pass,
        "failed_gate_keys": failed_gate_keys,
        "max_strict_rate": max_strict_rate,
        "max_null_rate": max_null_rate,
        "false_positive_methodology_repaired": decision["false_positive_methodology_repaired"],
        "actual_signal_present": decision["actual_signal_present"],
        "route_hash": route_hash,
        "decision_class": decision["decision_class"],
    }
    lesson_id = f"LESSON_TRUE_SOURCE_PANEL_NULL_{stable_hash(lesson_payload)}"

    lesson_record = {
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "lesson_type": "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_EVALUATED",
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
        "false_positive_methodology_repaired": bool(decision["false_positive_methodology_repaired"]),
        "actual_signal_present": bool(decision["actual_signal_present"]),
        "panel_empirical_policy_gate_pass": panel_empirical_policy_gate_pass,
        "panel_empirical_policy_gate_fail_count": panel_empirical_policy_gate_fail_count,
        "failed_gate_keys": failed_gate_keys,
        "max_strict_12_any_random_hit_rate": max_strict_rate,
        "max_null_adjusted_any_random_hit_rate": max_null_rate,
        "row_count": row_count,
        "symbol_count": symbol_count,
        "raw_calendar_month_count": raw_calendar_month_count,
        "canonical_policy_month_count": canonical_policy_month_count,
        "outcome_column": runner.get("outcome_column"),
        "replay_method_count": replay_method_count,
        "empirical_replay_runs_per_method": empirical_replay_runs_per_method,
        "total_empirical_replay_run_rows": total_empirical_replay_run_rows,
        "plugin_expansion_allowed": False,
        "branch_closed": bool(decision["branch_closed"]),
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
        "blocked_reason": "TRUE_SOURCE_PANEL_NULL_BASELINE_NO_ACTUAL_SIGNAL_OR_REVIEW_REQUIRED",
        "research_branch": "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE",
        "research_key": research_key,
        "plugin_key": plugin_key,
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "policy_hash": policy_hash,
        "false_positive_methodology_repaired": bool(decision["false_positive_methodology_repaired"]),
        "actual_signal_present": bool(decision["actual_signal_present"]),
        "panel_empirical_policy_gate_pass": panel_empirical_policy_gate_pass,
        "failed_gate_keys": failed_gate_keys,
        "plugin_expansion_allowed": False,
        "reopen_requirements": [
            "new policy-locked research route must be materially different",
            "true source-panel null baseline consumed",
            "false-positive rates below policy caps",
            "actual signal present before any plugin expansion",
            "guard and policy consumed",
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
        "queue_status": "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_NEXT_QUEUE_READY" if valid_input else "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_NEXT_QUEUE_BLOCKED",
        "source_evaluator": "edge_factory_os_true_source_panel_empirical_null_baseline_evaluator_v1",
        "source_route_hash": route_hash,
        "source_lesson_id": lesson_id,
        "decision_class": decision["decision_class"],
        "false_positive_methodology_repaired": bool(decision["false_positive_methodology_repaired"]),
        "actual_signal_present": bool(decision["actual_signal_present"]),
        "plugin_expansion_allowed": False,
        "top_next_research_key": decision["next_recommended_research_key"],
        "top_next_module": decision["next_module"],
        "next_direction_queue": [
            {
                "research_key": decision["next_recommended_research_key"],
                "priority": 100,
                "next_module_recommendation": decision["next_module"],
                "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
                "why": decision["reason"],
                "must_consume_guard_feed": True,
                "must_consume_research_gate_policy": True,
                "must_consume_true_source_panel_state": True,
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
                "priority": 80,
                "next_module_recommendation": ALT_MODULE,
                "allowed_scope": "READ_ONLY_RESEARCH",
                "why": "After framework status integration, queue a new policy-locked research direction only if it consumes the true source-panel null baseline state.",
                "must_consume_guard_feed": True,
                "must_consume_research_gate_policy": True,
                "must_consume_true_source_panel_state": True,
                "plugin_expansion_allowed_now": False,
                "candidate_generation_allowed_now": False,
                "candidate_contract_allowed_now": False,
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
        "evaluator_name": "edge_factory_os_true_source_panel_empirical_null_baseline_evaluator_v1",
        "created_at_utc": utc_now_iso(),
        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "decision_class": decision["decision_class"],
        "false_positive_methodology_repaired": bool(decision["false_positive_methodology_repaired"]),
        "actual_signal_present": bool(decision["actual_signal_present"]),
        "branch_closed": bool(decision["branch_closed"]),
        "route_blocklist_required": bool(decision["route_blocklist_required"]),
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
        "panel_empirical_policy_gate_pass": panel_empirical_policy_gate_pass,
        "panel_empirical_policy_gate_fail_count": panel_empirical_policy_gate_fail_count,
        "failed_gate_keys": failed_gate_keys,
        "max_strict_12_any_random_hit_rate": max_strict_rate,
        "max_null_adjusted_any_random_hit_rate": max_null_rate,
        "row_count": row_count,
        "symbol_count": symbol_count,
        "raw_calendar_month_count": raw_calendar_month_count,
        "canonical_policy_month_count": canonical_policy_month_count,
        "outcome_column": runner.get("outcome_column"),
        "replay_method_count": replay_method_count,
        "empirical_replay_runs_per_method": empirical_replay_runs_per_method,
        "total_empirical_replay_run_rows": total_empirical_replay_run_rows,
        "false_positive_summary_row_count": len(false_positive_rows),
        "policy_gate_row_count": len(policy_gate_rows),
        "pvalue_row_count": len(pvalue_rows),
        "schema_row_count": len(schema_rows),
        "coverage_row_count": len(coverage_rows),
        "method_inventory_row_count": len(method_rows),
        "lesson_id": lesson_id,
        "lesson_written": bool(valid_input),
        "lesson_append_status": lesson_append_status,
        "blocklist_written": bool(valid_input and decision["route_blocklist_required"] and route_hash),
        "blocklist_append_status": blocklist_append_status,
        "next_recommended_research_key": decision["next_recommended_research_key"],
        "next_module": decision["next_module"],
        "true_panel_state": true_panel_state,
        "release_gate_feed": {
            "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_EVALUATOR_RAN": True,
            "FALSE_POSITIVE_METHODOLOGY_REPAIRED": bool(decision["false_positive_methodology_repaired"]),
            "ACTUAL_SIGNAL_PRESENT": bool(decision["actual_signal_present"]),
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
            "false_positive_csv": str(FALSE_POSITIVE_CSV),
            "policy_gate_csv": str(POLICY_GATE_CSV),
            "pvalue_csv": str(PVALUE_CSV),
            "schema_csv": str(SCHEMA_CSV),
            "coverage_csv": str(COVERAGE_CSV),
            "method_inventory_csv": str(METHOD_INVENTORY_CSV),
            "contract_json": str(CONTRACT_JSON),
            "policy_json": str(POLICY_JSON),
            "repair_state_json": str(REPAIR_STATE_JSON),
            "validation_state_json": str(VALIDATION_STATE_JSON),
            "guard_feed_json": str(GUARD_FEED_JSON),
        },
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "next_queue_json": str(NEXT_QUEUE_JSON),
        "true_panel_state_json": str(TRUE_PANEL_STATE_JSON),
        "specific_lesson_path": str(SPECIFIC_LESSON_PATH),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text_summary(result))
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
