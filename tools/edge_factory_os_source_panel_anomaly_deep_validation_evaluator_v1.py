#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Source Panel Anomaly Deep Validation Evaluator v1

Purpose:
- Consume Source Panel Anomaly Deep Validation Runner v1.
- Classify failed deep validation.
- Close/block the current source-panel anomaly preview route.
- Write lesson memory and blocklist record.
- Write framework policy state.
- Queue next materially different policy-locked research direction.
- Keep candidate/family/runtime/capital/live/real-order actions blocked.

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
    / "edge_factory_os_source_panel_anomaly_deep_validation_runner"
    / "source_panel_anomaly_deep_validation_runner_latest.json"
)

RESULTS_CSV = (
    BASE_DIR
    / "edge_factory_os_source_panel_anomaly_deep_validation_runner"
    / "source_panel_anomaly_deep_validation_results_latest.csv"
)

GATE_CSV = (
    BASE_DIR
    / "edge_factory_os_source_panel_anomaly_deep_validation_runner"
    / "source_panel_anomaly_deep_validation_gate_table_latest.csv"
)

MONTH_HOLDOUT_CSV = (
    BASE_DIR
    / "edge_factory_os_source_panel_anomaly_deep_validation_runner"
    / "source_panel_anomaly_month_holdout_stability_latest.csv"
)

SYMBOL_HOLDOUT_CSV = (
    BASE_DIR
    / "edge_factory_os_source_panel_anomaly_deep_validation_runner"
    / "source_panel_anomaly_symbol_holdout_stability_latest.csv"
)

THRESHOLD_PERTURB_CSV = (
    BASE_DIR
    / "edge_factory_os_source_panel_anomaly_deep_validation_runner"
    / "source_panel_anomaly_threshold_perturbation_latest.csv"
)

NOISE_PERTURB_CSV = (
    BASE_DIR
    / "edge_factory_os_source_panel_anomaly_deep_validation_runner"
    / "source_panel_anomaly_noise_perturbation_latest.csv"
)

NEGATIVE_CONTROL_CSV = (
    BASE_DIR
    / "edge_factory_os_source_panel_anomaly_deep_validation_runner"
    / "source_panel_anomaly_deep_negative_controls_latest.csv"
)

TRUE_NULL_RERUN_CSV = (
    BASE_DIR
    / "edge_factory_os_source_panel_anomaly_deep_validation_runner"
    / "source_panel_anomaly_deep_true_null_rerun_latest.csv"
)

LEAKAGE_AUDIT_CSV = (
    BASE_DIR
    / "edge_factory_os_source_panel_anomaly_deep_validation_runner"
    / "source_panel_anomaly_leakage_audit_latest.csv"
)

CALENDAR_EDGE_CSV = (
    BASE_DIR
    / "edge_factory_os_source_panel_anomaly_deep_validation_runner"
    / "source_panel_anomaly_calendar_edge_sensitivity_latest.csv"
)

CONTRACT_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "contracts"
    / "source_panel_anomaly_deep_validation_contract_v1.json"
)

ANOMALY_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "source_panel_anomaly_discovery_state_v1.json"
)

FRAMEWORK_STATUS_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "status"
    / "framework_status_panel_v1.json"
)

TRUE_PANEL_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "true_source_panel_empirical_null_baseline_state_v1.json"
)

POLICY_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_enforcement_policy_v1.json"
)

LESSON_DIR = BASE_DIR / "edge_factory_os_lesson_memory"
LESSON_INDEX_PATH = LESSON_DIR / "lesson_memory_index.json"
BLOCKLIST_PATH = LESSON_DIR / "candidate_route_blocklist.json"
SPECIFIC_LESSON_PATH = LESSON_DIR / "source_panel_anomaly_deep_validation_failed_lesson_latest.json"

OUT_DIR = BASE_DIR / "edge_factory_os_source_panel_anomaly_deep_validation_evaluator"
OUT_JSON = OUT_DIR / "source_panel_anomaly_deep_validation_evaluator_latest.json"
OUT_TXT = OUT_DIR / "source_panel_anomaly_deep_validation_evaluator_latest.txt"
OUT_QUEUE_JSON = OUT_DIR / "source_panel_anomaly_deep_validation_next_queue_latest.json"

FRAMEWORK_POLICY_DIR = REPO_DIR / "edge_factory_os_framework" / "policies"
DEEP_VALIDATION_STATE_JSON = FRAMEWORK_POLICY_DIR / "source_panel_anomaly_deep_validation_state_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

EXPECTED_RUNNER_STATUS = "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_RUNNER_FAILED_VALIDATION"

NEXT_RESEARCH_KEY = "RD6_02_OUTCOME_AGNOSTIC_MARKET_STATE_TRANSITION_SEARCH"
NEXT_MODULE = "edge_factory_os_market_state_transition_contract_builder_v1.py"

ALT_RESEARCH_KEY = "RD6_03_PANEL_DATA_GENERATING_PROCESS_AUDIT"
ALT_MODULE = "edge_factory_os_panel_data_generating_process_audit_v1.py"

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
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            return [dict(row) for row in csv.DictReader(f)]
    except Exception:
        return []


def stable_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y", "pass"}


def to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


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


def failed_gate_keys_from_rows(gate_rows: List[Dict[str, Any]]) -> List[str]:
    return [
        str(row.get("gate_key"))
        for row in gate_rows
        if not to_bool(row.get("passed"))
    ]


def classify_failure(failed_gates: List[str]) -> Dict[str, Any]:
    gate_set = set(failed_gates)

    threshold_fail = "FEATURE_THRESHOLD_PERTURBATION" in gate_set
    negative_control_fail = "NEGATIVE_CONTROLS_RERUN" in gate_set
    true_null_fail = "TRUE_SOURCE_PANEL_NULL_RERUN_PASS" in gate_set

    if threshold_fail and negative_control_fail and true_null_fail:
        return {
            "decision_class": "ANOMALY_PREVIEW_FAILED_DEEP_VALIDATION_UNSTABLE_AND_NULL_UNSAFE",
            "route_closed": True,
            "redesign_allowed": False,
            "next_recommended_research_key": NEXT_RESEARCH_KEY,
            "next_module": NEXT_MODULE,
            "reason": (
                "Preview failed threshold perturbation, negative controls, and true-null rerun. "
                "This means the preview is not robust enough to redesign in-place; route should be closed and next materially different policy-locked direction queued."
            ),
        }

    if negative_control_fail or true_null_fail:
        return {
            "decision_class": "ANOMALY_PREVIEW_FAILED_DEEP_VALIDATION_NULL_OR_CONTROL_UNSAFE",
            "route_closed": True,
            "redesign_allowed": False,
            "next_recommended_research_key": NEXT_RESEARCH_KEY,
            "next_module": NEXT_MODULE,
            "reason": (
                "Preview failed null/control safety. Route should be closed; no release/candidate action."
            ),
        }

    if threshold_fail:
        return {
            "decision_class": "ANOMALY_PREVIEW_FAILED_DEEP_VALIDATION_THRESHOLD_UNSTABLE",
            "route_closed": True,
            "redesign_allowed": True,
            "next_recommended_research_key": NEXT_RESEARCH_KEY,
            "next_module": NEXT_MODULE,
            "reason": (
                "Preview failed threshold perturbation. Redesign could be possible later, but current route is not releaseable."
            ),
        }

    return {
        "decision_class": "ANOMALY_PREVIEW_FAILED_DEEP_VALIDATION_OTHER",
        "route_closed": True,
        "redesign_allowed": False,
        "next_recommended_research_key": NEXT_RESEARCH_KEY,
        "next_module": NEXT_MODULE,
        "reason": "Deep validation failed. Route is closed and next policy-locked direction is queued.",
    }


def build_deep_validation_state(
    *,
    runner: Dict[str, Any],
    decision: Dict[str, Any],
    failed_gates: List[str],
) -> Dict[str, Any]:
    return {
        "state_name": "edge_factory_os_source_panel_anomaly_deep_validation_state_v1",
        "created_at_utc": utc_now_iso(),
        "state_status": "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_FAILED_ROUTE_CLOSED",
        "decision_class": decision.get("decision_class"),
        "source_runner_status": runner.get("runner_status"),
        "contract_id": runner.get("contract_id"),
        "contract_hash": runner.get("contract_hash"),
        "route_hash": runner.get("route_hash"),
        "source_anomaly_route_hash": runner.get("source_anomaly_route_hash"),
        "research_key": runner.get("research_key"),
        "plugin_key": runner.get("plugin_key"),
        "policy_hash": runner.get("policy_hash"),
        "preview_axis_key": runner.get("preview_axis_key"),
        "preview_feature": runner.get("preview_feature"),
        "preview_side": runner.get("preview_side"),
        "deep_validation_gate_pass": False,
        "failed_gate_keys": failed_gates,
        "validation_test_count": runner.get("validation_test_count"),
        "validation_pass_count": runner.get("validation_pass_count"),
        "validation_fail_count": runner.get("validation_fail_count"),
        "route_closed": bool(decision.get("route_closed")),
        "redesign_allowed": bool(decision.get("redesign_allowed")),
        "release_allowed": False,
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


def build_next_queue(
    *,
    decision: Dict[str, Any],
    runner: Dict[str, Any],
    lesson_id: str,
) -> Dict[str, Any]:
    return {
        "created_at_utc": utc_now_iso(),
        "queue_status": "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_NEXT_QUEUE_READY",
        "source_evaluator": "edge_factory_os_source_panel_anomaly_deep_validation_evaluator_v1",
        "source_runner_status": runner.get("runner_status"),
        "source_route_hash": runner.get("route_hash"),
        "source_contract_id": runner.get("contract_id"),
        "source_lesson_id": lesson_id,
        "decision_class": decision.get("decision_class"),
        "route_closed": bool(decision.get("route_closed")),
        "redesign_allowed": bool(decision.get("redesign_allowed")),
        "release_allowed": False,
        "candidate_generation_allowed": False,
        "candidate_contract_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        "top_next_research_key": decision.get("next_recommended_research_key"),
        "top_next_module": decision.get("next_module"),
        "next_direction_queue": [
            {
                "research_key": decision.get("next_recommended_research_key"),
                "priority": 100,
                "next_module_recommendation": decision.get("next_module"),
                "allowed_scope": "READ_ONLY_RESEARCH",
                "why": decision.get("reason"),
                "must_consume_framework_status_panel": True,
                "must_consume_research_gate_policy": True,
                "must_consume_true_source_panel_null_state": True,
                "must_consume_deep_validation_failed_state": True,
                "must_consume_route_blocklist": True,
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
                "allowed_scope": "READ_ONLY_RESEARCH",
                "why": "Fallback if state-transition contract is blocked: audit panel data-generating process instead of searching a strategy.",
                "must_consume_route_blocklist": True,
                "candidate_generation_allowed_now": False,
                "family_release_allowed_now": False,
                "runtime_touch_allowed_now": False,
                "capital_change_allowed_now": False,
                "live_allowed_now": False,
                "real_orders_allowed_now": False,
            },
        ],
    }


def build_text(result: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS SOURCE PANEL ANOMALY DEEP VALIDATION EVALUATOR v1")
    lines.append("=" * 100)

    for key in [
        "evaluator_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "decision_class",
        "route_closed",
        "redesign_allowed",
        "release_allowed",
        "deep_validation_gate_pass",
        "failed_gate_keys",
        "validation_test_count",
        "validation_pass_count",
        "validation_fail_count",
        "preview_axis_key",
        "preview_feature",
        "preview_side",
        "next_recommended_research_key",
        "next_module",
        "lesson_id",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("FAILED GATES")
    lines.append("-" * 100)
    for gate in result.get("failed_gate_keys", []):
        lines.append(f"- {gate}")

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
        "next_queue_json",
        "deep_validation_state_json",
        "specific_lesson_path",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS SOURCE PANEL ANOMALY DEEP VALIDATION EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {result.get('evaluator_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"decision_class: {result.get('decision_class')}")
    print(f"route_closed: {result.get('route_closed')}")
    print(f"redesign_allowed: {result.get('redesign_allowed')}")
    print(f"release_allowed: {result.get('release_allowed')}")
    print(f"deep_validation_gate_pass: {result.get('deep_validation_gate_pass')}")
    print(f"failed_gate_keys: {result.get('failed_gate_keys')}")
    print(f"validation_test_count: {result.get('validation_test_count')}")
    print(f"validation_pass_count: {result.get('validation_pass_count')}")
    print(f"validation_fail_count: {result.get('validation_fail_count')}")
    print(f"preview_axis_key: {result.get('preview_axis_key')}")
    print(f"preview_feature: {result.get('preview_feature')}")
    print(f"preview_side: {result.get('preview_side')}")
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
    print(f"QUEUE: {result.get('next_queue_json')}")
    print(f"STATE: {result.get('deep_validation_state_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FRAMEWORK_POLICY_DIR.mkdir(parents=True, exist_ok=True)
    LESSON_DIR.mkdir(parents=True, exist_ok=True)

    runner = load_json(RUNNER_JSON, default={})
    contract = load_json(CONTRACT_JSON, default={})
    anomaly_state = load_json(ANOMALY_STATE_JSON, default={})
    framework_status = load_json(FRAMEWORK_STATUS_JSON, default={})
    true_panel_state = load_json(TRUE_PANEL_STATE_JSON, default={})
    policy = load_json(POLICY_JSON, default={})
    lesson_index = load_json(LESSON_INDEX_PATH, default={})
    blocklist = load_json(BLOCKLIST_PATH, default={})

    result_rows = read_csv_rows(RESULTS_CSV)
    gate_rows = read_csv_rows(GATE_CSV)
    month_rows = read_csv_rows(MONTH_HOLDOUT_CSV)
    symbol_rows = read_csv_rows(SYMBOL_HOLDOUT_CSV)
    threshold_rows = read_csv_rows(THRESHOLD_PERTURB_CSV)
    noise_rows = read_csv_rows(NOISE_PERTURB_CSV)
    negative_rows = read_csv_rows(NEGATIVE_CONTROL_CSV)
    true_null_rows = read_csv_rows(TRUE_NULL_RERUN_CSV)
    leakage_rows = read_csv_rows(LEAKAGE_AUDIT_CSV)
    calendar_rows = read_csv_rows(CALENDAR_EDGE_CSV)

    runner_status = str(runner.get("runner_status", ""))
    failed_gate_keys = runner.get("failed_gate_keys")
    if not isinstance(failed_gate_keys, list):
        failed_gate_keys = failed_gate_keys_from_rows(gate_rows)

    deep_validation_gate_pass = bool(runner.get("deep_validation_gate_pass"))
    validation_test_count = to_int(runner.get("validation_test_count"))
    validation_pass_count = to_int(runner.get("validation_pass_count"))
    validation_fail_count = to_int(runner.get("validation_fail_count"))

    valid_input = (
        runner_status == EXPECTED_RUNNER_STATUS
        and deep_validation_gate_pass is False
        and validation_fail_count > 0
        and len(failed_gate_keys) > 0
        and runner.get("release_allowed") is False
        and framework_status.get("panel_status") == "FRAMEWORK_STATUS_PANEL_READY_POLICY_LOCKED_NO_ACTUAL_SIGNAL"
        and bool(true_panel_state.get("false_positive_methodology_repaired"))
        and policy.get("policy_status") == "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE"
    )

    decision = classify_failure(failed_gate_keys)

    if valid_input:
        evaluator_status = "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_EVALUATOR_ROUTE_CLOSED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_OUTCOME_AGNOSTIC_MARKET_STATE_TRANSITION_CONTRACT_NO_RELEASE"
        reason = decision.get("reason")
        return_code = 0
    else:
        evaluator_status = "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_EVALUATOR_REVIEW_REQUIRED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_OUTPUTS_NO_RELEASE"
        reason = (
            f"runner_status={runner_status}; deep_validation_gate_pass={deep_validation_gate_pass}; "
            f"validation_fail_count={validation_fail_count}; failed_gate_keys={failed_gate_keys}; valid_input={valid_input}"
        )
        return_code = 2

    deep_state = build_deep_validation_state(
        runner=runner,
        decision=decision,
        failed_gates=failed_gate_keys,
    )

    if valid_input:
        write_json(DEEP_VALIDATION_STATE_JSON, deep_state)

    lesson_payload = {
        "runner_status": runner_status,
        "route_hash": runner.get("route_hash"),
        "contract_id": runner.get("contract_id"),
        "failed_gate_keys": failed_gate_keys,
        "decision_class": decision.get("decision_class"),
        "validation_pass_count": validation_pass_count,
        "validation_fail_count": validation_fail_count,
    }
    lesson_id = f"LESSON_SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_FAILED_{stable_hash(lesson_payload)}"

    lesson_record = {
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "lesson_type": "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_FAILED",
        "evaluator_status": evaluator_status,
        "decision_class": decision.get("decision_class"),
        "contract_id": runner.get("contract_id"),
        "contract_hash": runner.get("contract_hash"),
        "route_hash": runner.get("route_hash"),
        "source_anomaly_route_hash": runner.get("source_anomaly_route_hash"),
        "research_key": runner.get("research_key"),
        "plugin_key": runner.get("plugin_key"),
        "policy_hash": runner.get("policy_hash"),
        "preview_axis_key": runner.get("preview_axis_key"),
        "preview_feature": runner.get("preview_feature"),
        "preview_side": runner.get("preview_side"),
        "deep_validation_gate_pass": False,
        "failed_gate_keys": failed_gate_keys,
        "validation_test_count": validation_test_count,
        "validation_pass_count": validation_pass_count,
        "validation_fail_count": validation_fail_count,
        "route_closed": bool(decision.get("route_closed")),
        "redesign_allowed": bool(decision.get("redesign_allowed")),
        "release_allowed": False,
        "next_recommended_research_key": decision.get("next_recommended_research_key"),
        "next_module": decision.get("next_module"),
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
    }

    block_record = {
        "route_hash": runner.get("route_hash"),
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "blocked_reason": "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_FAILED",
        "research_branch": "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION",
        "research_key": runner.get("research_key"),
        "plugin_key": runner.get("plugin_key"),
        "contract_id": runner.get("contract_id"),
        "contract_hash": runner.get("contract_hash"),
        "policy_hash": runner.get("policy_hash"),
        "failed_gate_keys": failed_gate_keys,
        "decision_class": decision.get("decision_class"),
        "route_closed": bool(decision.get("route_closed")),
        "redesign_allowed": bool(decision.get("redesign_allowed")),
        "plugin_expansion_allowed": False,
        "release_allowed": False,
        "reopen_requirements": [
            "must not reuse same route hash",
            "must consume failed deep validation state",
            "must be materially different",
            "must pass threshold perturbation",
            "must pass negative controls",
            "must pass true source-panel null rerun",
            "must keep candidate/family/runtime/capital/live blocked",
        ],
    }

    lesson_append_status = None
    blocklist_append_status = None

    if valid_input:
        write_json(SPECIFIC_LESSON_PATH, lesson_record)
        lesson_append_status = append_lesson_record(LESSON_INDEX_PATH, lesson_record)
        blocklist_append_status = append_blocklist_record(BLOCKLIST_PATH, block_record)

    next_queue = build_next_queue(
        decision=decision,
        runner=runner,
        lesson_id=lesson_id,
    ) if valid_input else {
        "created_at_utc": utc_now_iso(),
        "queue_status": "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_NEXT_QUEUE_BLOCKED_REVIEW_REQUIRED",
        "reason": reason,
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
    }

    if valid_input:
        write_json(OUT_QUEUE_JSON, next_queue)

    result = {
        "evaluator_name": "edge_factory_os_source_panel_anomaly_deep_validation_evaluator_v1",
        "created_at_utc": utc_now_iso(),
        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "decision_class": decision.get("decision_class"),
        "route_closed": bool(decision.get("route_closed")),
        "redesign_allowed": bool(decision.get("redesign_allowed")),
        "release_allowed": False,
        "strict_policy_key": STRICT_POLICY_KEY,
        "runner_status": runner_status,
        "contract_id": runner.get("contract_id"),
        "contract_hash": runner.get("contract_hash"),
        "route_hash": runner.get("route_hash"),
        "source_anomaly_route_hash": runner.get("source_anomaly_route_hash"),
        "research_key": runner.get("research_key"),
        "plugin_key": runner.get("plugin_key"),
        "policy_hash": runner.get("policy_hash"),
        "preview_axis_key": runner.get("preview_axis_key"),
        "preview_feature": runner.get("preview_feature"),
        "preview_side": runner.get("preview_side"),
        "deep_validation_gate_pass": deep_validation_gate_pass,
        "deep_validation_gate_fail_count": to_int(runner.get("deep_validation_gate_fail_count")),
        "failed_gate_keys": failed_gate_keys,
        "validation_test_count": validation_test_count,
        "validation_pass_count": validation_pass_count,
        "validation_fail_count": validation_fail_count,
        "source_result_row_count": len(result_rows),
        "source_gate_row_count": len(gate_rows),
        "source_month_holdout_row_count": len(month_rows),
        "source_symbol_holdout_row_count": len(symbol_rows),
        "source_threshold_perturb_row_count": len(threshold_rows),
        "source_noise_perturb_row_count": len(noise_rows),
        "source_negative_control_row_count": len(negative_rows),
        "source_true_null_row_count": len(true_null_rows),
        "source_leakage_row_count": len(leakage_rows),
        "source_calendar_edge_row_count": len(calendar_rows),
        "lesson_count_before": len(extract_lessons(lesson_index)),
        "blocked_route_count_before": len(extract_blocked_routes(blocklist)),
        "lesson_id": lesson_id,
        "lesson_written": bool(valid_input),
        "lesson_append_status": lesson_append_status,
        "blocklist_written": bool(valid_input),
        "blocklist_append_status": blocklist_append_status,
        "next_recommended_research_key": decision.get("next_recommended_research_key"),
        "next_module": decision.get("next_module"),
        "deep_validation_state": deep_state,
        "next_queue": next_queue,
        "release_gate_feed": {
            "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_EVALUATOR_RAN": True,
            "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_FAILED": valid_input,
            "ROUTE_CLOSED": bool(decision.get("route_closed")),
            "REDESIGN_ALLOWED": bool(decision.get("redesign_allowed")),
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
            "results_csv": str(RESULTS_CSV),
            "gate_csv": str(GATE_CSV),
            "month_holdout_csv": str(MONTH_HOLDOUT_CSV),
            "symbol_holdout_csv": str(SYMBOL_HOLDOUT_CSV),
            "threshold_perturb_csv": str(THRESHOLD_PERTURB_CSV),
            "noise_perturb_csv": str(NOISE_PERTURB_CSV),
            "negative_control_csv": str(NEGATIVE_CONTROL_CSV),
            "true_null_rerun_csv": str(TRUE_NULL_RERUN_CSV),
            "leakage_audit_csv": str(LEAKAGE_AUDIT_CSV),
            "calendar_edge_csv": str(CALENDAR_EDGE_CSV),
            "contract_json": str(CONTRACT_JSON),
            "anomaly_state_json": str(ANOMALY_STATE_JSON),
            "framework_status_json": str(FRAMEWORK_STATUS_JSON),
            "true_panel_state_json": str(TRUE_PANEL_STATE_JSON),
            "policy_json": str(POLICY_JSON),
        },
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "next_queue_json": str(OUT_QUEUE_JSON),
        "deep_validation_state_json": str(DEEP_VALIDATION_STATE_JSON),
        "specific_lesson_path": str(SPECIFIC_LESSON_PATH),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text(result))
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
