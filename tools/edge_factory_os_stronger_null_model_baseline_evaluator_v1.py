#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Stronger Null Model Baseline Evaluator v1

Purpose:
- Consume Stronger Null Model Baseline Runner v1 output.
- Evaluate policy gate pass/fail.
- If gates fail, keep plugin expansion blocked.
- Record lesson and block route.
- Queue Research Gate Enforcement Validator / Null Baseline Methodology Audit.
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
    / "edge_factory_os_stronger_null_model_baseline_runner"
    / "stronger_null_model_baseline_runner_latest.json"
)

MODEL_SUMMARY_CSV = (
    BASE_DIR
    / "edge_factory_os_stronger_null_model_baseline_runner"
    / "stronger_null_model_false_positive_summary_latest.csv"
)

PVALUE_CSV = (
    BASE_DIR
    / "edge_factory_os_stronger_null_model_baseline_runner"
    / "stronger_null_model_empirical_p_value_table_latest.csv"
)

GATE_CSV = (
    BASE_DIR
    / "edge_factory_os_stronger_null_model_baseline_runner"
    / "stronger_null_model_policy_gate_pass_fail_latest.csv"
)

CONTRACT_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "contracts"
    / "stronger_null_model_baseline_contract_v1.json"
)

POLICY_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_enforcement_policy_v1.json"
)

GUARD_FEED_JSON = (
    BASE_DIR
    / "edge_factory_os_data_quality_guard_runner"
    / "data_quality_guard_feed_latest.json"
)

LESSON_DIR = BASE_DIR / "edge_factory_os_lesson_memory"
LESSON_INDEX_PATH = LESSON_DIR / "lesson_memory_index.json"
BLOCKLIST_PATH = LESSON_DIR / "candidate_route_blocklist.json"
SPECIFIC_LESSON_PATH = LESSON_DIR / "stronger_null_model_policy_gates_failed_lesson_latest.json"

OUT_DIR = BASE_DIR / "edge_factory_os_stronger_null_model_baseline_evaluator"
OUT_JSON = OUT_DIR / "stronger_null_model_baseline_evaluator_latest.json"
OUT_TXT = OUT_DIR / "stronger_null_model_baseline_evaluator_latest.txt"
NEXT_QUEUE_JSON = OUT_DIR / "stronger_null_model_next_queue_latest.json"

FRAMEWORK_POLICY_DIR = REPO_DIR / "edge_factory_os_framework" / "policies"
POLICY_STATE_JSON = FRAMEWORK_POLICY_DIR / "research_gate_policy_runtime_state_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD5_05_RESEARCH_GATE_ENFORCEMENT_VALIDATOR"
NEXT_MODULE = "edge_factory_os_research_gate_enforcement_validator_v1.py"

ALT_RESEARCH_KEY = "RD5_06_NULL_BASELINE_METHOD_AUDIT_AND_REPAIR"
ALT_MODULE = "edge_factory_os_null_baseline_method_audit_v1.py"

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


def classify_runner_result(runner: Dict[str, Any], gate_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    policy_gate_pass = bool(runner.get("policy_gate_pass"))
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

    if not policy_gate_pass and strict_rate_failed and null_rate_failed and actual_signal_missing:
        return {
            "decision_class": "STRONGER_NULL_BASELINE_POLICY_GATES_FAIL_FULL_BLOCK",
            "branch_closed": True,
            "route_blocklist_required": True,
            "plugin_expansion_allowed": False,
            "research_gate_policy_remains_active": True,
            "next_recommended_research_key": NEXT_RESEARCH_KEY,
            "next_module": NEXT_MODULE,
            "next_action": "BUILD_RESEARCH_GATE_ENFORCEMENT_VALIDATOR_NO_RELEASE",
            "reason": (
                "Stronger null baseline failed strict-rate cap, null-adjusted-rate cap, and actual-signal gate. "
                "Plugin expansion remains fully blocked; validate enforcement before any further research."
            ),
        }

    if not policy_gate_pass:
        return {
            "decision_class": "STRONGER_NULL_BASELINE_POLICY_GATES_FAIL_PARTIAL_BLOCK",
            "branch_closed": True,
            "route_blocklist_required": True,
            "plugin_expansion_allowed": False,
            "research_gate_policy_remains_active": True,
            "next_recommended_research_key": NEXT_RESEARCH_KEY,
            "next_module": NEXT_MODULE,
            "next_action": "BUILD_RESEARCH_GATE_ENFORCEMENT_VALIDATOR_NO_RELEASE",
            "reason": (
                f"Stronger null baseline failed policy gates {failed_gate_keys}. "
                "Plugin expansion remains blocked."
            ),
        }

    if policy_gate_pass and max_strict <= 0.01 and max_null <= 0.005:
        return {
            "decision_class": "STRONGER_NULL_BASELINE_POLICY_GATES_PASS_REVIEW_ONLY",
            "branch_closed": False,
            "route_blocklist_required": False,
            "plugin_expansion_allowed": False,
            "research_gate_policy_remains_active": True,
            "next_recommended_research_key": NEXT_RESEARCH_KEY,
            "next_module": NEXT_MODULE,
            "next_action": "BUILD_RESEARCH_GATE_ENFORCEMENT_VALIDATOR_BEFORE_PLUGIN_EXPANSION",
            "reason": (
                "Stronger null baseline passed policy caps, but plugin expansion still requires enforcement validator."
            ),
        }

    return {
        "decision_class": "STRONGER_NULL_BASELINE_EVALUATOR_ATTENTION",
        "branch_closed": True,
        "route_blocklist_required": True,
        "plugin_expansion_allowed": False,
        "research_gate_policy_remains_active": True,
        "next_recommended_research_key": ALT_RESEARCH_KEY,
        "next_module": ALT_MODULE,
        "next_action": "BUILD_NULL_BASELINE_METHOD_AUDIT_NO_RELEASE",
        "reason": "Stronger null baseline needs methodology audit or enforcement review.",
    }


def build_policy_runtime_state(
    *,
    runner: Dict[str, Any],
    policy: Dict[str, Any],
    decision: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "state_name": "edge_factory_os_research_gate_policy_runtime_state_v1",
        "created_at_utc": utc_now_iso(),
        "state_status": "RESEARCH_GATE_POLICY_ACTIVE_PLUGIN_EXPANSION_BLOCKED",
        "policy_hash": policy.get("policy_hash"),
        "policy_status": policy.get("policy_status"),
        "source_runner_status": runner.get("runner_status"),
        "source_policy_gate_pass": bool(runner.get("policy_gate_pass")),
        "source_failed_gate_keys": runner.get("failed_gate_keys"),
        "max_strict_12_any_random_hit_rate": runner.get("max_strict_12_any_random_hit_rate"),
        "max_null_adjusted_any_random_hit_rate": runner.get("max_null_adjusted_any_random_hit_rate"),
        "decision_class": decision.get("decision_class"),
        "plugin_expansion_allowed": False,
        "candidate_generation_allowed": False,
        "candidate_contract_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        "hard_blocks_active": [
            "NO_PLUGIN_EXPANSION_UNTIL_GATE_ENFORCEMENT_VALIDATOR",
            "NO_CANDIDATE_GENERATION",
            "NO_FAMILY_RELEASE",
            "NO_RUNTIME_TOUCH",
            "NO_CAPITAL_CHANGE",
            "NO_ACTIVE_PAPER",
            "NO_LIVE",
            "NO_REAL_ORDERS",
        ],
    }


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS STRONGER NULL MODEL BASELINE EVALUATOR v1")
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
        "plugin_expansion_allowed",
        "research_gate_policy_remains_active",
        "runner_status",
        "contract_id",
        "route_hash",
        "research_key",
        "plugin_key",
        "policy_hash",
        "policy_gate_pass",
        "policy_gate_fail_count",
        "failed_gate_keys",
        "max_strict_12_any_random_hit_rate",
        "max_null_adjusted_any_random_hit_rate",
        "null_model_count",
        "permutation_runs_per_model",
        "total_permutation_run_rows",
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
        "lesson_index_path",
        "blocklist_path",
        "specific_lesson_path",
        "policy_runtime_state_json",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS STRONGER NULL MODEL BASELINE EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {result.get('evaluator_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"decision_class: {result.get('decision_class')}")
    print(f"branch_closed: {result.get('branch_closed')}")
    print(f"route_blocklist_required: {result.get('route_blocklist_required')}")
    print(f"plugin_expansion_allowed: {result.get('plugin_expansion_allowed')}")
    print(f"research_gate_policy_remains_active: {result.get('research_gate_policy_remains_active')}")
    print(f"policy_gate_pass: {result.get('policy_gate_pass')}")
    print(f"policy_gate_fail_count: {result.get('policy_gate_fail_count')}")
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
    print(f"POLICY_STATE: {result.get('policy_runtime_state_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LESSON_DIR.mkdir(parents=True, exist_ok=True)
    FRAMEWORK_POLICY_DIR.mkdir(parents=True, exist_ok=True)

    runner = load_json(RUNNER_JSON, default={})
    contract = load_json(CONTRACT_JSON, default={})
    policy = load_json(POLICY_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})

    model_summary_rows = read_csv_rows(MODEL_SUMMARY_CSV)
    pvalue_rows = read_csv_rows(PVALUE_CSV)
    gate_rows = read_csv_rows(GATE_CSV)

    runner_status = str(runner.get("runner_status", ""))
    runner_missing = not RUNNER_JSON.exists()
    runner_error = "ERROR" in runner_status.upper()

    contract_id = runner.get("contract_id") or contract.get("contract_id")
    contract_hash = runner.get("contract_hash") or contract.get("contract_hash")
    route_hash = runner.get("route_hash") or contract.get("route_hash")
    research_key = runner.get("research_key") or contract.get("research_key")
    plugin_key = runner.get("plugin_key") or contract.get("plugin_key")
    policy_hash = runner.get("policy_hash") or contract.get("policy_hash") or policy.get("policy_hash")

    policy_gate_pass = bool(runner.get("policy_gate_pass"))
    policy_gate_fail_count = to_int(runner.get("policy_gate_fail_count"))
    failed_gate_keys = runner.get("failed_gate_keys")
    if not isinstance(failed_gate_keys, list):
        failed_gate_keys = [row.get("gate_key") for row in gate_rows if not to_bool(row.get("passed"))]

    max_strict_rate = to_float(runner.get("max_strict_12_any_random_hit_rate"), 1.0)
    max_null_rate = to_float(runner.get("max_null_adjusted_any_random_hit_rate"), 1.0)

    null_model_count = to_int(runner.get("null_model_count"))
    permutation_runs_per_model = to_int(runner.get("permutation_runs_per_model"))
    total_permutation_run_rows = to_int(runner.get("total_permutation_run_rows"))

    valid_input = (
        not runner_missing
        and not runner_error
        and runner_status.startswith("STRONGER_NULL_MODEL_BASELINE_RUNNER_")
        and bool(route_hash)
        and bool(guard_feed.get("guard_pass"))
        and null_model_count >= 8
        and permutation_runs_per_model >= 1000
        and total_permutation_run_rows >= 8000
    )

    decision = classify_runner_result(runner, gate_rows)

    lesson_payload = {
        "research_branch": "STRONGER_NULL_MODEL_BASELINE",
        "runner_status": runner_status,
        "policy_gate_pass": policy_gate_pass,
        "failed_gate_keys": failed_gate_keys,
        "max_strict_rate": max_strict_rate,
        "max_null_rate": max_null_rate,
        "contract_id": contract_id,
        "route_hash": route_hash,
        "decision_class": decision["decision_class"],
    }
    lesson_id = f"LESSON_STRONGER_NULL_BASELINE_{stable_hash(lesson_payload)}"

    if not valid_input:
        evaluator_status = "STRONGER_NULL_MODEL_BASELINE_EVALUATOR_INVALID_OR_INCOMPLETE_INPUT"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "RERUN_OR_INSPECT_STRONGER_NULL_MODEL_BASELINE_RUNNER_NO_RELEASE"
        reason = (
            f"runner_missing={runner_missing}; runner_error={runner_error}; runner_status={runner_status}; "
            f"route_hash_present={bool(route_hash)}; guard_pass={bool(guard_feed.get('guard_pass'))}; "
            f"null_model_count={null_model_count}; permutation_runs_per_model={permutation_runs_per_model}; "
            f"total_permutation_run_rows={total_permutation_run_rows}"
        )
        interpretation = "Evaluator could not trust stronger null baseline runner input."
        return_code = 2
    else:
        if policy_gate_pass:
            evaluator_status = "STRONGER_NULL_MODEL_BASELINE_EVALUATOR_POLICY_GATES_PASS_REVIEW_ONLY"
        else:
            evaluator_status = "STRONGER_NULL_MODEL_BASELINE_EVALUATOR_POLICY_GATES_FAILED_PLUGIN_EXPANSION_BLOCKED"

        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = decision["next_action"]
        reason = decision["reason"]
        interpretation = (
            "The stronger null-model baseline consumed policy and guard feed. "
            "Policy gates failed, so plugin expansion remains blocked. "
            "The OS must validate enforcement and/or audit null baseline methodology before any further feature expansion."
            if not policy_gate_pass
            else
            "The stronger null-model baseline passed, but plugin expansion still requires enforcement validation. No release action is allowed."
        )
        return_code = 0

    lesson_record = {
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "lesson_type": "STRONGER_NULL_MODEL_BASELINE_EVALUATED",
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
        "policy_gate_pass": policy_gate_pass,
        "policy_gate_fail_count": policy_gate_fail_count,
        "failed_gate_keys": failed_gate_keys,
        "max_strict_12_any_random_hit_rate": max_strict_rate,
        "max_null_adjusted_any_random_hit_rate": max_null_rate,
        "null_model_count": null_model_count,
        "permutation_runs_per_model": permutation_runs_per_model,
        "total_permutation_run_rows": total_permutation_run_rows,
        "plugin_expansion_allowed": False,
        "branch_closed": bool(decision["branch_closed"]),
        "interpretation": interpretation,
        "next_recommended_research_key": decision["next_recommended_research_key"],
        "next_module": decision["next_module"],
        "source_runner_json": str(RUNNER_JSON),
        "source_model_summary_csv": str(MODEL_SUMMARY_CSV),
        "source_pvalue_csv": str(PVALUE_CSV),
        "source_gate_csv": str(GATE_CSV),
    }

    block_record = {
        "route_hash": route_hash,
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "blocked_reason": "STRONGER_NULL_MODEL_POLICY_GATES_FAILED_OR_REVIEW_REQUIRED",
        "research_branch": "STRONGER_NULL_MODEL_BASELINE",
        "research_key": research_key,
        "plugin_key": plugin_key,
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "policy_hash": policy_hash,
        "strict_policy_key": STRICT_POLICY_KEY,
        "policy_gate_pass": policy_gate_pass,
        "failed_gate_keys": failed_gate_keys,
        "max_strict_12_any_random_hit_rate": max_strict_rate,
        "max_null_adjusted_any_random_hit_rate": max_null_rate,
        "reopen_requirements": [
            "research gate enforcement validator pass",
            "null baseline methodology audit or repair if required",
            "policy-consumption proof",
            "guard-consumption proof",
            "false-positive rates below policy caps",
            "actual signal present if any future feature expansion claims signal",
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

        policy_state = build_policy_runtime_state(runner=runner, policy=policy, decision=decision)
        write_json(POLICY_STATE_JSON, policy_state)

    next_queue = {
        "created_at_utc": utc_now_iso(),
        "queue_status": "STRONGER_NULL_MODEL_NEXT_QUEUE_READY" if valid_input else "STRONGER_NULL_MODEL_NEXT_QUEUE_BLOCKED",
        "source_evaluator": "edge_factory_os_stronger_null_model_baseline_evaluator_v1",
        "source_route_hash": route_hash,
        "source_lesson_id": lesson_id,
        "decision_class": decision["decision_class"],
        "policy_gate_pass": policy_gate_pass,
        "plugin_expansion_allowed": False,
        "research_gate_policy_remains_active": True,
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
                "must_not_reopen_blocked_routes": True,
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
                "priority": 75,
                "next_module_recommendation": ALT_MODULE,
                "allowed_scope": "READ_ONLY_RESEARCH",
                "why": "Audit or repair null baseline methodology if validator says enforcement is not sufficient.",
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
        "evaluator_name": "edge_factory_os_stronger_null_model_baseline_evaluator_v1",
        "created_at_utc": utc_now_iso(),
        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "decision_class": decision["decision_class"],
        "branch_closed": bool(decision["branch_closed"]),
        "route_blocklist_required": bool(decision["route_blocklist_required"]),
        "plugin_expansion_allowed": False,
        "research_gate_policy_remains_active": True,
        "interpretation": interpretation,
        "strict_policy_key": STRICT_POLICY_KEY,
        "runner_status": runner_status,
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "research_key": research_key,
        "plugin_key": plugin_key,
        "policy_hash": policy_hash,
        "policy_gate_pass": policy_gate_pass,
        "policy_gate_fail_count": policy_gate_fail_count,
        "failed_gate_keys": failed_gate_keys,
        "max_strict_12_any_random_hit_rate": max_strict_rate,
        "max_null_adjusted_any_random_hit_rate": max_null_rate,
        "null_model_count": null_model_count,
        "permutation_runs_per_model": permutation_runs_per_model,
        "total_permutation_run_rows": total_permutation_run_rows,
        "model_summary_row_count": len(model_summary_rows),
        "empirical_pvalue_row_count": len(pvalue_rows),
        "policy_gate_row_count": len(gate_rows),
        "lesson_id": lesson_id,
        "lesson_written": bool(valid_input),
        "blocklist_written": bool(valid_input and decision["route_blocklist_required"] and route_hash),
        "lesson_append_status": lesson_append_status,
        "blocklist_append_status": blocklist_append_status,
        "next_recommended_research_key": decision["next_recommended_research_key"],
        "next_module": decision["next_module"],
        "release_gate_feed": {
            "STRONGER_NULL_MODEL_BASELINE_EVALUATOR_RAN": True,
            "POLICY_GATE_PASS": policy_gate_pass,
            "PLUGIN_EXPANSION_ALLOWED": False,
            "RESEARCH_GATE_POLICY_REMAINS_ACTIVE": True,
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
            "model_summary_csv": str(MODEL_SUMMARY_CSV),
            "pvalue_csv": str(PVALUE_CSV),
            "gate_csv": str(GATE_CSV),
            "contract_json": str(CONTRACT_JSON),
            "policy_json": str(POLICY_JSON),
            "guard_feed_json": str(GUARD_FEED_JSON),
        },
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "next_queue_json": str(NEXT_QUEUE_JSON),
        "lesson_index_path": str(LESSON_INDEX_PATH),
        "blocklist_path": str(BLOCKLIST_PATH),
        "specific_lesson_path": str(SPECIFIC_LESSON_PATH),
        "policy_runtime_state_json": str(POLICY_STATE_JSON),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text_summary(OUT_TXT, result)
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
