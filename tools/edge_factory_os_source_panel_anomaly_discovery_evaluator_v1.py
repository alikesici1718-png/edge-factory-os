#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Source Panel Anomaly Discovery Evaluator v1

Purpose:
- Consume Source Panel Anomaly Discovery Runner v1.
- Record whether policy-locked anomaly preview exists.
- Confirm true-null caps passed and material-difference passed.
- Keep release/candidate/family/runtime/capital/live blocked.
- Queue Source Panel Anomaly Deep Validation Contract Builder v1.

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
    / "edge_factory_os_source_panel_anomaly_discovery_runner"
    / "source_panel_anomaly_discovery_runner_latest.json"
)

SCORE_CSV = (
    BASE_DIR
    / "edge_factory_os_source_panel_anomaly_discovery_runner"
    / "source_panel_outcome_agnostic_anomaly_scores_latest.csv"
)

MONTH_SCORE_CSV = (
    BASE_DIR
    / "edge_factory_os_source_panel_anomaly_discovery_runner"
    / "source_panel_anomaly_month_scores_latest.csv"
)

TRUE_NULL_CSV = (
    BASE_DIR
    / "edge_factory_os_source_panel_anomaly_discovery_runner"
    / "source_panel_anomaly_true_null_replay_summary_latest.csv"
)

POLICY_GATE_CSV = (
    BASE_DIR
    / "edge_factory_os_source_panel_anomaly_discovery_runner"
    / "source_panel_anomaly_policy_gate_pass_fail_latest.csv"
)

MATERIAL_DIFF_CSV = (
    BASE_DIR
    / "edge_factory_os_source_panel_anomaly_discovery_runner"
    / "source_panel_anomaly_material_difference_report_latest.csv"
)

CONSUMPTION_CSV = (
    BASE_DIR
    / "edge_factory_os_source_panel_anomaly_discovery_runner"
    / "source_panel_anomaly_consumption_report_latest.csv"
)

CONTRACT_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "contracts"
    / "source_panel_anomaly_discovery_contract_v1.json"
)

POLICY_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_enforcement_policy_v1.json"
)

TRUE_PANEL_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "true_source_panel_empirical_null_baseline_state_v1.json"
)

FRAMEWORK_STATUS_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "status"
    / "framework_status_panel_v1.json"
)

LESSON_DIR = BASE_DIR / "edge_factory_os_lesson_memory"
LESSON_INDEX_PATH = LESSON_DIR / "lesson_memory_index.json"
BLOCKLIST_PATH = LESSON_DIR / "candidate_route_blocklist.json"
SPECIFIC_LESSON_PATH = LESSON_DIR / "source_panel_anomaly_discovery_preview_lesson_latest.json"

OUT_DIR = BASE_DIR / "edge_factory_os_source_panel_anomaly_discovery_evaluator"
OUT_JSON = OUT_DIR / "source_panel_anomaly_discovery_evaluator_latest.json"
OUT_TXT = OUT_DIR / "source_panel_anomaly_discovery_evaluator_latest.txt"
OUT_QUEUE_JSON = OUT_DIR / "source_panel_anomaly_deep_validation_queue_latest.json"
OUT_PREVIEW_CSV = OUT_DIR / "source_panel_anomaly_preview_candidates_for_validation_latest.csv"

FRAMEWORK_POLICY_DIR = REPO_DIR / "edge_factory_os_framework" / "policies"
ANOMALY_STATE_JSON = FRAMEWORK_POLICY_DIR / "source_panel_anomaly_discovery_state_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

EXPECTED_RUNNER_STATUS = "SOURCE_PANEL_ANOMALY_DISCOVERY_RUNNER_PREVIEW_FOUND_TRUE_NULL_CLEAN_NOT_RELEASE"

NEXT_RESEARCH_KEY = "RD6_01A_SOURCE_PANEL_ANOMALY_DEEP_VALIDATION"
NEXT_MODULE = "edge_factory_os_source_panel_anomaly_deep_validation_contract_builder_v1.py"

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


def select_preview_rows(score_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    previews = []
    for row in score_rows:
        if to_bool(row.get("strict_12_anomaly_preview")):
            previews.append(row)

    previews = sorted(
        previews,
        key=lambda r: (
            to_float(r.get("total_anomaly_score")),
            to_float(r.get("median_month_anomaly_score")),
            to_float(r.get("min_month_anomaly_score")),
        ),
        reverse=True,
    )
    return previews


def failed_gate_keys_from_rows(policy_gate_rows: List[Dict[str, Any]]) -> List[str]:
    return [
        str(row.get("gate_key"))
        for row in policy_gate_rows
        if not to_bool(row.get("passed"))
    ]


def build_anomaly_state(
    *,
    runner: Dict[str, Any],
    decision_class: str,
    preview_found: bool,
    true_null_clean: bool,
    material_difference_pass: bool,
    deep_validation_required: bool,
    preview_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "state_name": "edge_factory_os_source_panel_anomaly_discovery_state_v1",
        "created_at_utc": utc_now_iso(),
        "state_status": (
            "SOURCE_PANEL_ANOMALY_PREVIEW_FOUND_TRUE_NULL_CLEAN_DEEP_VALIDATION_REQUIRED"
            if preview_found and true_null_clean and material_difference_pass
            else "SOURCE_PANEL_ANOMALY_DISCOVERY_REVIEW_REQUIRED"
        ),
        "decision_class": decision_class,
        "source_runner_status": runner.get("runner_status"),
        "contract_id": runner.get("contract_id"),
        "route_hash": runner.get("route_hash"),
        "selected_queue_route_hash": runner.get("selected_queue_route_hash"),
        "research_key": runner.get("research_key"),
        "plugin_key": runner.get("plugin_key"),
        "policy_hash": runner.get("policy_hash"),
        "preview_found": preview_found,
        "true_null_clean": true_null_clean,
        "material_difference_pass": material_difference_pass,
        "deep_validation_required": deep_validation_required,
        "release_allowed": False,
        "candidate_generation_allowed": False,
        "candidate_contract_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        "row_count": runner.get("row_count"),
        "symbol_count": runner.get("symbol_count"),
        "raw_calendar_month_count": runner.get("raw_calendar_month_count"),
        "canonical_policy_month_count": runner.get("canonical_policy_month_count"),
        "selected_feature_count": runner.get("selected_feature_count"),
        "anomaly_axis_row_count": runner.get("anomaly_axis_row_count"),
        "strict_12_anomaly_preview_count": runner.get("strict_12_anomaly_preview_count"),
        "negative_control_count": runner.get("negative_control_count"),
        "true_null_runs_per_control": runner.get("true_null_runs_per_control"),
        "total_true_null_run_rows": runner.get("total_true_null_run_rows"),
        "max_strict_12_any_random_hit_rate": runner.get("max_strict_12_any_random_hit_rate"),
        "max_null_adjusted_any_random_hit_rate": runner.get("max_null_adjusted_any_random_hit_rate"),
        "anomaly_policy_gate_pass": runner.get("anomaly_policy_gate_pass"),
        "failed_gate_keys": runner.get("failed_gate_keys"),
        "preview_row_count": len(preview_rows),
        "top_preview_axis_key": preview_rows[0].get("axis_key") if preview_rows else None,
        "top_preview_feature": preview_rows[0].get("feature") if preview_rows else None,
        "top_preview_side": preview_rows[0].get("side") if preview_rows else None,
        "top_preview_total_anomaly_score": preview_rows[0].get("total_anomaly_score") if preview_rows else None,
        "next_recommended_research_key": NEXT_RESEARCH_KEY,
        "next_module": NEXT_MODULE,
    }


def build_next_queue(
    *,
    state: Dict[str, Any],
    preview_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    preview_payload = []
    for row in preview_rows:
        preview_payload.append({
            "axis_key": row.get("axis_key"),
            "feature": row.get("feature"),
            "side": row.get("side"),
            "active_months": row.get("active_months"),
            "strict_months": row.get("strict_months"),
            "total_anomaly_score": row.get("total_anomaly_score"),
            "min_month_anomaly_score": row.get("min_month_anomaly_score"),
            "median_month_anomaly_score": row.get("median_month_anomaly_score"),
            "avg_symbol_count": row.get("avg_symbol_count"),
            "avg_row_count": row.get("avg_row_count"),
            "strict_12_anomaly_preview": row.get("strict_12_anomaly_preview"),
        })

    return {
        "created_at_utc": utc_now_iso(),
        "queue_status": "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_QUEUE_READY",
        "source_evaluator": "edge_factory_os_source_panel_anomaly_discovery_evaluator_v1",
        "source_state_status": state.get("state_status"),
        "source_route_hash": state.get("route_hash"),
        "source_contract_id": state.get("contract_id"),
        "preview_found": state.get("preview_found"),
        "true_null_clean": state.get("true_null_clean"),
        "material_difference_pass": state.get("material_difference_pass"),
        "deep_validation_required": True,
        "release_allowed": False,
        "candidate_generation_allowed": False,
        "candidate_contract_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        "top_next_research_key": NEXT_RESEARCH_KEY,
        "top_next_module": NEXT_MODULE,
        "preview_candidates_for_validation": preview_payload,
        "next_direction_queue": [
            {
                "research_key": NEXT_RESEARCH_KEY,
                "priority": 100,
                "next_module_recommendation": NEXT_MODULE,
                "allowed_scope": "READ_ONLY_RESEARCH",
                "why": (
                    "Outcome-agnostic source-panel anomaly preview passed true-null caps. "
                    "Deep validation is required before any candidate/family/release action."
                ),
                "required_validation_steps": [
                    "month holdout stability",
                    "symbol holdout stability",
                    "feature perturbation stability",
                    "negative controls rerun",
                    "true source-panel null replay rerun",
                    "no outcome leakage audit",
                    "optional outcome validation only after anomaly stability",
                    "no candidate generation",
                    "no family release",
                    "no runtime/capital/live action",
                ],
                "consume_state_path": str(ANOMALY_STATE_JSON),
                "consume_preview_csv": str(OUT_PREVIEW_CSV),
                "plugin_expansion_allowed_now": False,
                "candidate_generation_allowed_now": False,
                "candidate_contract_allowed_now": False,
                "family_release_allowed_now": False,
                "runtime_touch_allowed_now": False,
                "capital_change_allowed_now": False,
                "active_paper_allowed_now": False,
                "live_allowed_now": False,
                "real_orders_allowed_now": False,
            }
        ],
    }


def build_text(result: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS SOURCE PANEL ANOMALY DISCOVERY EVALUATOR v1")
    lines.append("=" * 100)

    for key in [
        "evaluator_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "decision_class",
        "preview_found",
        "true_null_clean",
        "material_difference_pass",
        "deep_validation_required",
        "release_allowed",
        "candidate_generation_allowed",
        "family_release_allowed",
        "runtime_touch_allowed",
        "capital_change_allowed",
        "live_allowed",
        "real_orders_allowed",
        "strict_12_anomaly_preview_count",
        "max_strict_12_any_random_hit_rate",
        "max_null_adjusted_any_random_hit_rate",
        "anomaly_policy_gate_pass",
        "failed_gate_keys",
        "top_preview_axis_key",
        "top_preview_feature",
        "top_preview_side",
        "next_recommended_research_key",
        "next_module",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("PREVIEW CANDIDATES")
    lines.append("-" * 100)
    for row in result.get("preview_rows", []):
        lines.append(
            f"{row.get('axis_key')} | feature={row.get('feature')} | side={row.get('side')} | "
            f"score={row.get('total_anomaly_score')} | strict_months={row.get('strict_months')}"
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
        "next_queue_json",
        "preview_csv",
        "anomaly_state_json",
        "specific_lesson_path",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS SOURCE PANEL ANOMALY DISCOVERY EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {result.get('evaluator_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"decision_class: {result.get('decision_class')}")
    print(f"preview_found: {result.get('preview_found')}")
    print(f"true_null_clean: {result.get('true_null_clean')}")
    print(f"material_difference_pass: {result.get('material_difference_pass')}")
    print(f"deep_validation_required: {result.get('deep_validation_required')}")
    print(f"release_allowed: {result.get('release_allowed')}")
    print(f"strict_12_anomaly_preview_count: {result.get('strict_12_anomaly_preview_count')}")
    print(f"max_strict_12_any_random_hit_rate: {result.get('max_strict_12_any_random_hit_rate')}")
    print(f"max_null_adjusted_any_random_hit_rate: {result.get('max_null_adjusted_any_random_hit_rate')}")
    print(f"anomaly_policy_gate_pass: {result.get('anomaly_policy_gate_pass')}")
    print(f"failed_gate_keys: {result.get('failed_gate_keys')}")
    print(f"top_preview_axis_key: {result.get('top_preview_axis_key')}")
    print(f"top_preview_feature: {result.get('top_preview_feature')}")
    print(f"top_preview_side: {result.get('top_preview_side')}")
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
    print(f"STATE: {result.get('anomaly_state_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FRAMEWORK_POLICY_DIR.mkdir(parents=True, exist_ok=True)
    LESSON_DIR.mkdir(parents=True, exist_ok=True)

    runner = load_json(RUNNER_JSON, default={})
    contract = load_json(CONTRACT_JSON, default={})
    policy = load_json(POLICY_JSON, default={})
    true_panel_state = load_json(TRUE_PANEL_STATE_JSON, default={})
    framework_status = load_json(FRAMEWORK_STATUS_JSON, default={})
    lesson_index = load_json(LESSON_INDEX_PATH, default={})
    blocklist = load_json(BLOCKLIST_PATH, default={})

    score_rows = read_csv_rows(SCORE_CSV)
    month_score_rows = read_csv_rows(MONTH_SCORE_CSV)
    true_null_rows = read_csv_rows(TRUE_NULL_CSV)
    policy_gate_rows = read_csv_rows(POLICY_GATE_CSV)
    material_rows = read_csv_rows(MATERIAL_DIFF_CSV)
    consumption_rows = read_csv_rows(CONSUMPTION_CSV)

    runner_status = str(runner.get("runner_status", ""))
    preview_rows = select_preview_rows(score_rows)

    strict_preview_count = to_int(runner.get("strict_12_anomaly_preview_count"))
    anomaly_policy_gate_pass = bool(runner.get("anomaly_policy_gate_pass"))
    material_difference_pass = bool(runner.get("material_difference_pass"))
    max_strict = to_float(runner.get("max_strict_12_any_random_hit_rate"), 1.0)
    max_null = to_float(runner.get("max_null_adjusted_any_random_hit_rate"), 1.0)
    failed_gate_keys = runner.get("failed_gate_keys")
    if not isinstance(failed_gate_keys, list):
        failed_gate_keys = failed_gate_keys_from_rows(policy_gate_rows)

    consumption_pass = all(to_bool(row.get("passed")) for row in consumption_rows) if consumption_rows else False

    valid_input = (
        runner_status == EXPECTED_RUNNER_STATUS
        and strict_preview_count > 0
        and len(preview_rows) > 0
        and anomaly_policy_gate_pass
        and material_difference_pass
        and max_strict <= 0.01
        and max_null <= 0.005
        and not failed_gate_keys
        and consumption_pass
        and bool(true_panel_state.get("false_positive_methodology_repaired"))
        and not bool(true_panel_state.get("actual_signal_present"))
        and framework_status.get("panel_status") == "FRAMEWORK_STATUS_PANEL_READY_POLICY_LOCKED_NO_ACTUAL_SIGNAL"
    )

    if valid_input:
        evaluator_status = "SOURCE_PANEL_ANOMALY_DISCOVERY_EVALUATOR_PREVIEW_FOUND_TRUE_NULL_CLEAN_DEEP_VALIDATION_REQUIRED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_CONTRACT_NO_RELEASE"
        decision_class = "SOURCE_PANEL_ANOMALY_PREVIEW_TRUE_NULL_CLEAN_NOT_RELEASE_DEEP_VALIDATION_REQUIRED"
        reason = (
            f"preview_found=True; strict_12_anomaly_preview_count={strict_preview_count}; "
            f"true_null_clean=True; material_difference_pass=True; release_allowed=False; deep_validation_required=True"
        )
        preview_found = True
        true_null_clean = True
        deep_validation_required = True
        return_code = 0
    else:
        evaluator_status = "SOURCE_PANEL_ANOMALY_DISCOVERY_EVALUATOR_REVIEW_REQUIRED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_SOURCE_PANEL_ANOMALY_DISCOVERY_OUTPUTS_NO_RELEASE"
        decision_class = "SOURCE_PANEL_ANOMALY_DISCOVERY_REVIEW_REQUIRED"
        reason = (
            f"runner_status={runner_status}; strict_preview_count={strict_preview_count}; "
            f"preview_rows={len(preview_rows)}; anomaly_policy_gate_pass={anomaly_policy_gate_pass}; "
            f"material_difference_pass={material_difference_pass}; max_strict={max_strict}; max_null={max_null}; "
            f"failed_gate_keys={failed_gate_keys}; consumption_pass={consumption_pass}"
        )
        preview_found = strict_preview_count > 0
        true_null_clean = anomaly_policy_gate_pass and max_strict <= 0.01 and max_null <= 0.005
        deep_validation_required = False
        return_code = 2

    state = build_anomaly_state(
        runner=runner,
        decision_class=decision_class,
        preview_found=preview_found,
        true_null_clean=true_null_clean,
        material_difference_pass=material_difference_pass,
        deep_validation_required=deep_validation_required,
        preview_rows=preview_rows,
    )

    if valid_input:
        write_json(ANOMALY_STATE_JSON, state)

    preview_export_rows = []
    for idx, row in enumerate(preview_rows, start=1):
        preview_export_rows.append({
            "rank": idx,
            "axis_key": row.get("axis_key"),
            "feature": row.get("feature"),
            "side": row.get("side"),
            "active_months": row.get("active_months"),
            "strict_months": row.get("strict_months"),
            "total_anomaly_score": row.get("total_anomaly_score"),
            "min_month_anomaly_score": row.get("min_month_anomaly_score"),
            "median_month_anomaly_score": row.get("median_month_anomaly_score"),
            "avg_symbol_count": row.get("avg_symbol_count"),
            "avg_row_count": row.get("avg_row_count"),
            "strict_12_anomaly_preview": row.get("strict_12_anomaly_preview"),
            "candidate_generation_allowed": False,
            "family_release_allowed": False,
            "runtime_touch_allowed": False,
            "capital_change_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
        })

    if valid_input:
        write_csv(OUT_PREVIEW_CSV, preview_export_rows)

    next_queue = build_next_queue(state=state, preview_rows=preview_rows) if valid_input else {
        "created_at_utc": utc_now_iso(),
        "queue_status": "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_QUEUE_BLOCKED_REVIEW_REQUIRED",
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

    lesson_payload = {
        "runner_status": runner_status,
        "strict_preview_count": strict_preview_count,
        "max_strict": max_strict,
        "max_null": max_null,
        "material_difference_pass": material_difference_pass,
        "route_hash": runner.get("route_hash"),
        "decision_class": decision_class,
    }
    lesson_id = f"LESSON_SOURCE_PANEL_ANOMALY_PREVIEW_{stable_hash(lesson_payload)}"

    lesson_record = {
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "lesson_type": "SOURCE_PANEL_ANOMALY_DISCOVERY_EVALUATED",
        "evaluator_status": evaluator_status,
        "decision_class": decision_class,
        "contract_id": runner.get("contract_id"),
        "contract_hash": runner.get("contract_hash"),
        "route_hash": runner.get("route_hash"),
        "selected_queue_route_hash": runner.get("selected_queue_route_hash"),
        "research_key": runner.get("research_key"),
        "plugin_key": runner.get("plugin_key"),
        "policy_hash": runner.get("policy_hash"),
        "preview_found": preview_found,
        "true_null_clean": true_null_clean,
        "material_difference_pass": material_difference_pass,
        "deep_validation_required": deep_validation_required,
        "release_allowed": False,
        "strict_12_anomaly_preview_count": strict_preview_count,
        "max_strict_12_any_random_hit_rate": max_strict,
        "max_null_adjusted_any_random_hit_rate": max_null,
        "top_preview_axis_key": preview_rows[0].get("axis_key") if preview_rows else None,
        "top_preview_feature": preview_rows[0].get("feature") if preview_rows else None,
        "top_preview_side": preview_rows[0].get("side") if preview_rows else None,
        "next_recommended_research_key": NEXT_RESEARCH_KEY,
        "next_module": NEXT_MODULE,
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
    }

    if valid_input:
        write_json(SPECIFIC_LESSON_PATH, lesson_record)
        lesson_append_status = append_lesson_record(LESSON_INDEX_PATH, lesson_record)
    else:
        lesson_append_status = None

    result = {
        "evaluator_name": "edge_factory_os_source_panel_anomaly_discovery_evaluator_v1",
        "created_at_utc": utc_now_iso(),
        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "decision_class": decision_class,
        "strict_policy_key": STRICT_POLICY_KEY,
        "preview_found": preview_found,
        "true_null_clean": true_null_clean,
        "material_difference_pass": material_difference_pass,
        "deep_validation_required": deep_validation_required,
        "release_allowed": False,
        "runner_status": runner_status,
        "contract_id": runner.get("contract_id"),
        "contract_hash": runner.get("contract_hash"),
        "route_hash": runner.get("route_hash"),
        "selected_queue_route_hash": runner.get("selected_queue_route_hash"),
        "research_key": runner.get("research_key"),
        "plugin_key": runner.get("plugin_key"),
        "policy_hash": runner.get("policy_hash"),
        "row_count": runner.get("row_count"),
        "symbol_count": runner.get("symbol_count"),
        "raw_calendar_month_count": runner.get("raw_calendar_month_count"),
        "canonical_policy_month_count": runner.get("canonical_policy_month_count"),
        "selected_feature_count": runner.get("selected_feature_count"),
        "anomaly_axis_row_count": runner.get("anomaly_axis_row_count"),
        "strict_12_anomaly_preview_count": strict_preview_count,
        "negative_control_count": runner.get("negative_control_count"),
        "true_null_runs_per_control": runner.get("true_null_runs_per_control"),
        "total_true_null_run_rows": runner.get("total_true_null_run_rows"),
        "max_strict_12_any_random_hit_rate": max_strict,
        "max_null_adjusted_any_random_hit_rate": max_null,
        "anomaly_policy_gate_pass": anomaly_policy_gate_pass,
        "anomaly_policy_gate_fail_count": runner.get("anomaly_policy_gate_fail_count"),
        "failed_gate_keys": failed_gate_keys,
        "top_preview_axis_key": preview_rows[0].get("axis_key") if preview_rows else None,
        "top_preview_feature": preview_rows[0].get("feature") if preview_rows else None,
        "top_preview_side": preview_rows[0].get("side") if preview_rows else None,
        "preview_rows": preview_export_rows,
        "source_score_row_count": len(score_rows),
        "source_month_score_row_count": len(month_score_rows),
        "source_true_null_row_count": len(true_null_rows),
        "source_policy_gate_row_count": len(policy_gate_rows),
        "source_material_difference_row_count": len(material_rows),
        "source_consumption_row_count": len(consumption_rows),
        "lesson_count_before": len(extract_lessons(lesson_index)),
        "blocked_route_count": len(extract_blocked_routes(blocklist)),
        "lesson_id": lesson_id,
        "lesson_written": bool(valid_input),
        "lesson_append_status": lesson_append_status,
        "next_recommended_research_key": NEXT_RESEARCH_KEY,
        "next_module": NEXT_MODULE,
        "anomaly_state": state,
        "next_queue": next_queue,
        "release_gate_feed": {
            "SOURCE_PANEL_ANOMALY_DISCOVERY_EVALUATOR_RAN": True,
            "SOURCE_PANEL_ANOMALY_PREVIEW_FOUND": preview_found,
            "TRUE_NULL_CLEAN": true_null_clean,
            "MATERIAL_DIFFERENCE_PASS": material_difference_pass,
            "DEEP_VALIDATION_REQUIRED": deep_validation_required,
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
            "score_csv": str(SCORE_CSV),
            "month_score_csv": str(MONTH_SCORE_CSV),
            "true_null_csv": str(TRUE_NULL_CSV),
            "policy_gate_csv": str(POLICY_GATE_CSV),
            "material_difference_csv": str(MATERIAL_DIFF_CSV),
            "consumption_csv": str(CONSUMPTION_CSV),
            "contract_json": str(CONTRACT_JSON),
            "policy_json": str(POLICY_JSON),
            "true_panel_state_json": str(TRUE_PANEL_STATE_JSON),
            "framework_status_json": str(FRAMEWORK_STATUS_JSON),
        },
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "next_queue_json": str(OUT_QUEUE_JSON),
        "preview_csv": str(OUT_PREVIEW_CSV),
        "anomaly_state_json": str(ANOMALY_STATE_JSON),
        "specific_lesson_path": str(SPECIFIC_LESSON_PATH),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text(result))
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
