#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Null Model Permutation Baseline Evaluator v1

Purpose:
- Consume Null Model Permutation Baseline Runner v1 output.
- Evaluate false-positive baseline risk.
- Record a high-false-positive lesson when needed.
- Queue a stricter research gate tightening policy/contract.
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

import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

RUNNER_JSON = (
    BASE_DIR
    / "edge_factory_os_null_model_permutation_baseline_runner"
    / "null_model_permutation_baseline_runner_latest.json"
)

BASELINE_SUMMARY_CSV = (
    BASE_DIR
    / "edge_factory_os_null_model_permutation_baseline_runner"
    / "null_model_baseline_false_positive_summary_latest.csv"
)

PVALUE_CSV = (
    BASE_DIR
    / "edge_factory_os_null_model_permutation_baseline_runner"
    / "null_model_empirical_p_value_table_latest.csv"
)

CONTRACT_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "contracts"
    / "null_model_permutation_baseline_contract_v1.json"
)

GUARD_FEED_JSON = (
    BASE_DIR
    / "edge_factory_os_data_quality_guard_runner"
    / "data_quality_guard_feed_latest.json"
)

LESSON_DIR = BASE_DIR / "edge_factory_os_lesson_memory"
LESSON_INDEX_PATH = LESSON_DIR / "lesson_memory_index.json"
BLOCKLIST_PATH = LESSON_DIR / "candidate_route_blocklist.json"
SPECIFIC_LESSON_PATH = LESSON_DIR / "null_model_false_positive_high_lesson_latest.json"

OUT_DIR = BASE_DIR / "edge_factory_os_null_model_permutation_baseline_evaluator"
OUT_JSON = OUT_DIR / "null_model_permutation_baseline_evaluator_latest.json"
OUT_TXT = OUT_DIR / "null_model_permutation_baseline_evaluator_latest.txt"
NEXT_QUEUE_JSON = OUT_DIR / "null_model_permutation_next_queue_latest.json"

FRAMEWORK_POLICY_DIR = REPO_DIR / "edge_factory_os_framework" / "policies"
FRAMEWORK_POLICY_JSON = FRAMEWORK_POLICY_DIR / "research_gate_tightening_policy_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD5_03_RESEARCH_GATE_TIGHTENING_POLICY"
NEXT_MODULE = "edge_factory_os_research_gate_tightening_policy_builder_v1.py"

ALT_RESEARCH_KEY = "RD5_04_STRONGER_NULL_MODEL_BASELINE_REBUILD"
ALT_MODULE = "edge_factory_os_stronger_null_model_baseline_contract_builder_v1.py"

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


def classify_baseline(
    assessment: str,
    max_strict_rate: float,
    max_null_rate: float,
    summary_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    high_rows = [
        r for r in summary_rows
        if str(r.get("interpretation")) == "FALSE_POSITIVE_RISK_HIGH"
    ]
    moderate_rows = [
        r for r in summary_rows
        if str(r.get("interpretation")) == "FALSE_POSITIVE_RISK_MODERATE"
    ]

    if (
        assessment == "FALSE_POSITIVE_BASELINE_HIGH_TIGHTEN_RESEARCH_GATES"
        or max_strict_rate >= 0.25
        or max_null_rate >= 0.10
        or len(high_rows) > 0
    ):
        return {
            "decision_class": "FALSE_POSITIVE_BASELINE_HIGH_RESEARCH_GATES_MUST_TIGHTEN",
            "severity": "ATTENTION",
            "branch_closed": True,
            "route_blocklist_required": True,
            "research_gate_tightening_required": True,
            "plugin_expansion_allowed": False,
            "next_recommended_research_key": NEXT_RESEARCH_KEY,
            "next_module": NEXT_MODULE,
            "next_action": "BUILD_RESEARCH_GATE_TIGHTENING_POLICY_NO_RELEASE",
            "reason": (
                "Null/permutation baseline indicates high false-positive risk. "
                "Future feature expansion is blocked until research gates are tightened."
            ),
        }

    if (
        assessment == "FALSE_POSITIVE_BASELINE_MODERATE_USE_STRONGER_NULL_ADJUSTMENT"
        or max_strict_rate >= 0.05
        or max_null_rate >= 0.02
        or len(moderate_rows) > 0
    ):
        return {
            "decision_class": "FALSE_POSITIVE_BASELINE_MODERATE_STRENGTHEN_NULL_GATES",
            "severity": "ATTENTION",
            "branch_closed": False,
            "route_blocklist_required": False,
            "research_gate_tightening_required": True,
            "plugin_expansion_allowed": False,
            "next_recommended_research_key": NEXT_RESEARCH_KEY,
            "next_module": NEXT_MODULE,
            "next_action": "BUILD_RESEARCH_GATE_TIGHTENING_POLICY_NO_RELEASE",
            "reason": (
                "Null/permutation baseline indicates moderate false-positive risk. "
                "Strengthen null gates before plugin expansion."
            ),
        }

    return {
        "decision_class": "FALSE_POSITIVE_BASELINE_LOW_PLUGIN_EXPANSION_CAN_BE_QUEUED_UNDER_GUARD",
        "severity": "ATTENTION",
        "branch_closed": False,
        "route_blocklist_required": False,
        "research_gate_tightening_required": False,
        "plugin_expansion_allowed": True,
        "next_recommended_research_key": "RD5_01B_GUARDED_FEATURE_SPACE_PLUGIN_EXPANSION",
        "next_module": "edge_factory_os_plugin_expansion_planner_v1.py",
        "next_action": "BUILD_PLUGIN_EXPANSION_PLANNER_UNDER_GUARD_NO_RELEASE",
        "reason": (
            "False-positive baseline is low enough to allow guarded plugin expansion, "
            "but candidate/release/live remain blocked."
        ),
    }


def build_policy(decision: Dict[str, Any], runner: Dict[str, Any]) -> Dict[str, Any]:
    high_risk = decision["decision_class"] == "FALSE_POSITIVE_BASELINE_HIGH_RESEARCH_GATES_MUST_TIGHTEN"

    return {
        "policy_name": "edge_factory_os_research_gate_tightening_policy_v1",
        "created_at_utc": utc_now_iso(),
        "policy_status": "RESEARCH_GATE_TIGHTENING_POLICY_DRAFT_READY",
        "strict_policy_key": STRICT_POLICY_KEY,
        "source_runner_status": runner.get("runner_status"),
        "source_assessment": runner.get("overall_false_positive_assessment"),
        "source_max_strict_12_any_random_hit_rate": runner.get("max_strict_12_any_random_hit_rate"),
        "source_max_null_adjusted_any_random_hit_rate": runner.get("max_null_adjusted_any_random_hit_rate"),
        "tightening_required": bool(decision.get("research_gate_tightening_required")),
        "plugin_expansion_allowed_before_tightening": bool(decision.get("plugin_expansion_allowed")),
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        "draft_gate_rules": {
            "minimum_permutation_runs": 1000 if high_risk else 500,
            "required_independent_null_models": 8 if high_risk else 5,
            "max_allowed_strict_12_any_random_hit_rate": 0.01 if high_risk else 0.03,
            "max_allowed_null_adjusted_any_random_hit_rate": 0.005 if high_risk else 0.01,
            "empirical_p_value_required_lte": 0.01 if high_risk else 0.025,
            "require_out_of_time_month_split": True,
            "require_symbol_holdout_split": True,
            "require_cost_stress_pass": True,
            "require_top_symbol_concentration_cap": True,
            "require_no_manual_symbol_whitelist": True,
            "require_no_manual_month_blacklist": True,
            "require_data_quality_guard_pass": True,
            "require_route_hash_not_blocked": True,
            "require_deep_validation_before_candidate_contract": True,
        },
        "blocked_until_policy_builder_runs": True,
    }


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS NULL MODEL PERMUTATION BASELINE EVALUATOR v1")
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
        "research_gate_tightening_required",
        "plugin_expansion_allowed",
        "runner_status",
        "contract_id",
        "route_hash",
        "research_key",
        "plugin_key",
        "overall_false_positive_assessment",
        "max_strict_12_any_random_hit_rate",
        "max_null_adjusted_any_random_hit_rate",
        "next_recommended_research_key",
        "next_module",
        "lesson_id",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("POLICY DRAFT")
    lines.append("-" * 100)
    lines.append(json.dumps(result.get("policy_draft", {}), indent=2, ensure_ascii=False))

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
        "framework_policy_json",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS NULL MODEL PERMUTATION BASELINE EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {result.get('evaluator_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"decision_class: {result.get('decision_class')}")
    print(f"branch_closed: {result.get('branch_closed')}")
    print(f"route_blocklist_required: {result.get('route_blocklist_required')}")
    print(f"research_gate_tightening_required: {result.get('research_gate_tightening_required')}")
    print(f"plugin_expansion_allowed: {result.get('plugin_expansion_allowed')}")
    print(f"overall_false_positive_assessment: {result.get('overall_false_positive_assessment')}")
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
    print(f"POLICY: {result.get('framework_policy_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LESSON_DIR.mkdir(parents=True, exist_ok=True)
    FRAMEWORK_POLICY_DIR.mkdir(parents=True, exist_ok=True)

    runner = load_json(RUNNER_JSON, default={})
    contract = load_json(CONTRACT_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})

    summary_rows = read_csv_rows(BASELINE_SUMMARY_CSV)
    pvalue_rows = read_csv_rows(PVALUE_CSV)

    runner_status = str(runner.get("runner_status", ""))
    runner_missing = not RUNNER_JSON.exists()
    runner_error = "ERROR" in runner_status.upper()

    assessment = str(runner.get("overall_false_positive_assessment", ""))
    max_strict_rate = to_float(runner.get("max_strict_12_any_random_hit_rate"))
    max_null_rate = to_float(runner.get("max_null_adjusted_any_random_hit_rate"))

    route_hash = runner.get("route_hash") or contract.get("route_hash")
    contract_id = runner.get("contract_id") or contract.get("contract_id")
    contract_hash = runner.get("contract_hash") or contract.get("contract_hash")
    research_key = runner.get("research_key") or contract.get("research_key")
    plugin_key = runner.get("plugin_key") or contract.get("plugin_key")

    baseline_test_count = to_int(runner.get("baseline_test_count"))
    permutation_runs_per_test = to_int(runner.get("permutation_runs_per_test"))
    total_permutation_run_rows = to_int(runner.get("total_permutation_run_rows"))

    valid_input = (
        not runner_missing
        and not runner_error
        and runner_status.startswith("NULL_MODEL_PERMUTATION_BASELINE_RUNNER_")
        and bool(guard_feed.get("guard_pass"))
        and bool(route_hash)
        and baseline_test_count > 0
        and total_permutation_run_rows > 0
    )

    decision = classify_baseline(
        assessment=assessment,
        max_strict_rate=max_strict_rate,
        max_null_rate=max_null_rate,
        summary_rows=summary_rows,
    )

    policy_draft = build_policy(decision, runner)

    lesson_payload = {
        "research_branch": "NULL_MODEL_PERMUTATION_BASELINE",
        "runner_status": runner_status,
        "assessment": assessment,
        "max_strict_rate": max_strict_rate,
        "max_null_rate": max_null_rate,
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "decision_class": decision["decision_class"],
    }

    lesson_id = f"LESSON_NULL_MODEL_BASELINE_{stable_hash(lesson_payload)}"

    if not valid_input:
        evaluator_status = "NULL_MODEL_BASELINE_EVALUATOR_INVALID_OR_INCOMPLETE_INPUT"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "RERUN_OR_INSPECT_NULL_MODEL_BASELINE_RUNNER_NO_RELEASE"
        reason = (
            f"runner_missing={runner_missing}; runner_error={runner_error}; "
            f"runner_status={runner_status}; guard_pass={bool(guard_feed.get('guard_pass'))}; "
            f"route_hash_present={bool(route_hash)}; baseline_test_count={baseline_test_count}; "
            f"total_permutation_run_rows={total_permutation_run_rows}"
        )
        return_code = 2
    else:
        if decision["decision_class"] == "FALSE_POSITIVE_BASELINE_HIGH_RESEARCH_GATES_MUST_TIGHTEN":
            evaluator_status = "NULL_MODEL_BASELINE_EVALUATOR_HIGH_FALSE_POSITIVE_RISK_GATE_TIGHTENING_REQUIRED"
        elif decision["decision_class"] == "FALSE_POSITIVE_BASELINE_MODERATE_STRENGTHEN_NULL_GATES":
            evaluator_status = "NULL_MODEL_BASELINE_EVALUATOR_MODERATE_FALSE_POSITIVE_RISK_GATE_TIGHTENING_REQUIRED"
        else:
            evaluator_status = "NULL_MODEL_BASELINE_EVALUATOR_LOW_FALSE_POSITIVE_RISK_PLUGIN_EXPANSION_ALLOWED_UNDER_GUARD"

        severity = decision["severity"]
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = decision["next_action"]
        reason = decision["reason"]
        return_code = 0

    lesson_record = {
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "lesson_type": "NULL_MODEL_FALSE_POSITIVE_BASELINE_EVALUATED",
        "strict_policy_key": STRICT_POLICY_KEY,
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "research_key": research_key,
        "plugin_key": plugin_key,
        "runner_status": runner_status,
        "evaluator_status": evaluator_status,
        "overall_false_positive_assessment": assessment,
        "max_strict_12_any_random_hit_rate": max_strict_rate,
        "max_null_adjusted_any_random_hit_rate": max_null_rate,
        "baseline_test_count": baseline_test_count,
        "permutation_runs_per_test": permutation_runs_per_test,
        "total_permutation_run_rows": total_permutation_run_rows,
        "decision_class": decision["decision_class"],
        "research_gate_tightening_required": bool(decision["research_gate_tightening_required"]),
        "plugin_expansion_allowed": bool(decision["plugin_expansion_allowed"]),
        "branch_closed": bool(decision["branch_closed"]),
        "interpretation": (
            "Null/permutation baseline detected high false-positive risk. "
            "Future research gates must be tightened before any plugin expansion or candidate-style workflow."
        ),
        "source_runner_json": str(RUNNER_JSON),
        "source_baseline_summary_csv": str(BASELINE_SUMMARY_CSV),
        "source_pvalue_csv": str(PVALUE_CSV),
    }

    block_record = {
        "route_hash": route_hash,
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "blocked_reason": "NULL_MODEL_FALSE_POSITIVE_BASELINE_HIGH_OR_UNSAFE",
        "research_branch": "NULL_MODEL_PERMUTATION_BASELINE",
        "research_key": research_key,
        "plugin_key": plugin_key,
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "strict_policy_key": STRICT_POLICY_KEY,
        "overall_false_positive_assessment": assessment,
        "max_strict_12_any_random_hit_rate": max_strict_rate,
        "max_null_adjusted_any_random_hit_rate": max_null_rate,
        "reopen_requirements": [
            "research gate tightening policy implemented",
            "stronger null/permutation baseline implemented",
            "empirical p-value threshold tightened",
            "false-positive random hit rates below allowed caps",
            "data quality guard pass",
            "no blocked route hash reuse",
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

        write_json(FRAMEWORK_POLICY_JSON, policy_draft)

    next_queue = {
        "created_at_utc": utc_now_iso(),
        "queue_status": "NULL_MODEL_BASELINE_NEXT_QUEUE_READY" if valid_input else "NULL_MODEL_BASELINE_NEXT_QUEUE_BLOCKED",
        "source_evaluator": "edge_factory_os_null_model_permutation_baseline_evaluator_v1",
        "source_route_hash": route_hash,
        "source_lesson_id": lesson_id,
        "decision_class": decision["decision_class"],
        "research_gate_tightening_required": bool(decision["research_gate_tightening_required"]),
        "plugin_expansion_allowed": bool(decision["plugin_expansion_allowed"]),
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
                "priority": 70,
                "next_module_recommendation": ALT_MODULE,
                "allowed_scope": "READ_ONLY_RESEARCH",
                "why": "Alternative: rebuild stronger null model baseline if current baseline is considered too crude.",
                "must_consume_guard_feed": True,
                "must_not_reopen_blocked_routes": True,
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
        "evaluator_name": "edge_factory_os_null_model_permutation_baseline_evaluator_v1",
        "created_at_utc": utc_now_iso(),
        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "decision_class": decision["decision_class"],
        "branch_closed": bool(decision["branch_closed"]),
        "route_blocklist_required": bool(decision["route_blocklist_required"]),
        "research_gate_tightening_required": bool(decision["research_gate_tightening_required"]),
        "plugin_expansion_allowed": bool(decision["plugin_expansion_allowed"]),
        "strict_policy_key": STRICT_POLICY_KEY,
        "runner_status": runner_status,
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "research_key": research_key,
        "plugin_key": plugin_key,
        "overall_false_positive_assessment": assessment,
        "max_strict_12_any_random_hit_rate": max_strict_rate,
        "max_null_adjusted_any_random_hit_rate": max_null_rate,
        "baseline_test_count": baseline_test_count,
        "permutation_runs_per_test": permutation_runs_per_test,
        "total_permutation_run_rows": total_permutation_run_rows,
        "baseline_summary_rows": summary_rows,
        "empirical_p_value_rows": pvalue_rows,
        "policy_draft": policy_draft,
        "lesson_id": lesson_id,
        "lesson_written": bool(valid_input),
        "blocklist_written": bool(valid_input and decision["route_blocklist_required"] and route_hash),
        "lesson_append_status": lesson_append_status,
        "blocklist_append_status": blocklist_append_status,
        "next_recommended_research_key": decision["next_recommended_research_key"],
        "next_module": decision["next_module"],
        "release_gate_feed": {
            "NULL_MODEL_BASELINE_EVALUATOR_RAN": True,
            "FALSE_POSITIVE_BASELINE_HIGH": decision["decision_class"] == "FALSE_POSITIVE_BASELINE_HIGH_RESEARCH_GATES_MUST_TIGHTEN",
            "RESEARCH_GATE_TIGHTENING_REQUIRED": bool(decision["research_gate_tightening_required"]),
            "PLUGIN_EXPANSION_ALLOWED": bool(decision["plugin_expansion_allowed"]),
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
            "baseline_summary_csv": str(BASELINE_SUMMARY_CSV),
            "pvalue_csv": str(PVALUE_CSV),
            "contract_json": str(CONTRACT_JSON),
            "guard_feed_json": str(GUARD_FEED_JSON),
        },
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "next_queue_json": str(NEXT_QUEUE_JSON),
        "lesson_index_path": str(LESSON_INDEX_PATH),
        "blocklist_path": str(BLOCKLIST_PATH),
        "specific_lesson_path": str(SPECIFIC_LESSON_PATH),
        "framework_policy_json": str(FRAMEWORK_POLICY_JSON),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text_summary(OUT_TXT, result)
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
