#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Exit Risk Shape Deep Validation Evaluator v1

Purpose:
- Evaluate Exit Risk Shape Deep Validation Runner v1.
- If preview rows fail deep validation, close/archive the route.
- Record lesson + blocklist evidence.
- Queue next materially different research direction:
  RD4_04_SYMBOL_CLUSTER_AND_MICROSTRUCTURE_SEGMENT_SEARCH.
- Keep all candidate/family/runtime/capital/live/real-order actions blocked.
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

RUNNER_DIR = BASE_DIR / "edge_factory_os_exit_risk_shape_deep_validation_runner"
RUNNER_JSON = RUNNER_DIR / "exit_risk_shape_deep_validation_runner_latest.json"
RUNNER_CSV = RUNNER_DIR / "exit_risk_shape_deep_validation_results_latest.csv"
RUNNER_MONTH_CSV = RUNNER_DIR / "exit_risk_shape_deep_validation_months_latest.csv"
RUNNER_COST_CSV = RUNNER_DIR / "exit_risk_shape_deep_validation_cost_sensitivity_latest.csv"
RUNNER_SYMBOL_CSV = RUNNER_DIR / "exit_risk_shape_deep_validation_symbol_concentration_latest.csv"

CONTRACT_PATH = BASE_DIR / "edge_factory_os_research_direction_contracts" / "exit_risk_shape_deep_validation_contract_latest.json"

OUT_DIR = BASE_DIR / "edge_factory_os_exit_risk_shape_deep_validation_evaluator"
OUT_JSON = OUT_DIR / "exit_risk_shape_deep_validation_evaluator_latest.json"
OUT_TXT = OUT_DIR / "exit_risk_shape_deep_validation_evaluator_latest.txt"
NEXT_QUEUE_JSON = OUT_DIR / "exit_risk_shape_next_research_queue_latest.json"

LESSON_DIR = BASE_DIR / "edge_factory_os_lesson_memory"
LESSON_INDEX_PATH = LESSON_DIR / "lesson_memory_index.json"
BLOCKLIST_PATH = LESSON_DIR / "candidate_route_blocklist.json"
SPECIFIC_LESSON_PATH = LESSON_DIR / "exit_risk_shape_deep_validation_failed_lesson_latest.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD4_04_SYMBOL_CLUSTER_AND_MICROSTRUCTURE_SEGMENT_SEARCH"
NEXT_MODULE = "edge_factory_os_symbol_cluster_segment_contract_builder_v1.py"

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


def read_csv_rows(path: Path, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    rows: List[Dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(dict(row))
                if limit is not None and len(rows) >= limit:
                    break
    except Exception:
        return []

    return rows


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


def summarize_failures(validation_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    counts: Dict[str, int] = {}
    for row in validation_rows:
        reasons = str(row.get("failure_reasons", "")).split("|")
        for reason in reasons:
            reason = reason.strip()
            if reason:
                counts[reason] = counts.get(reason, 0) + 1

    return {
        "failure_reason_counts": counts,
        "failed_route_count": sum(1 for row in validation_rows if str(row.get("deep_validation_pass", "")).lower() not in {"true", "1", "yes"}),
        "passed_route_count": sum(1 for row in validation_rows if str(row.get("deep_validation_pass", "")).lower() in {"true", "1", "yes"}),
    }


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS EXIT RISK SHAPE DEEP VALIDATION EVALUATOR v1")
    lines.append("=" * 100)

    for k in [
        "evaluator_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "branch_closed",
        "preview_failed_deep_validation",
        "release_allowed",
        "strict_policy_key",
        "canonical_policy_month_count",
        "preview_count",
        "validation_result_count",
        "deep_validation_pass_count",
        "all_deep_validations_passed",
        "next_recommended_research_key",
        "next_module",
        "lesson_id",
        "route_hash",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("FAILURE SUMMARY")
    lines.append("-" * 100)
    fs = result.get("failure_summary", {})
    for k, v in fs.items():
        lines.append(f"{k}: {v}")

    lines.append("")
    lines.append("VALIDATION ROWS")
    lines.append("-" * 100)
    for row in result.get("validation_rows", [])[:20]:
        lines.append(
            f"{row.get('reference_id')} {row.get('exit_shape_id')} | "
            f"deep={row.get('deep_validation_pass')} | "
            f"fail={row.get('failure_reasons')}"
        )

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
    print("EDGE FACTORY OS EXIT RISK SHAPE DEEP VALIDATION EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {result.get('evaluator_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"branch_closed: {result.get('branch_closed')}")
    print(f"preview_failed_deep_validation: {result.get('preview_failed_deep_validation')}")
    print(f"release_allowed: {result.get('release_allowed')}")
    print(f"strict_policy_key: {result.get('strict_policy_key')}")
    print(f"canonical_policy_month_count: {result.get('canonical_policy_month_count')}")
    print(f"preview_count: {result.get('preview_count')}")
    print(f"validation_result_count: {result.get('validation_result_count')}")
    print(f"deep_validation_pass_count: {result.get('deep_validation_pass_count')}")
    print(f"all_deep_validations_passed: {result.get('all_deep_validations_passed')}")
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
    contract = load_json(CONTRACT_PATH, default={})
    validation_rows = read_csv_rows(RUNNER_CSV)

    runner_status = str(runner.get("runner_status", ""))
    runner_missing = not RUNNER_JSON.exists()
    runner_error = "ERROR" in runner_status.upper()

    canonical_policy_month_count = to_int(runner.get("canonical_policy_month_count"), 12)
    preview_count = to_int(runner.get("preview_count"))
    validation_result_count = to_int(runner.get("validation_result_count"))
    deep_validation_pass_count = to_int(runner.get("deep_validation_pass_count"))
    all_deep_validations_passed = bool(runner.get("all_deep_validations_passed"))
    release_allowed = bool(runner.get("release_allowed"))

    contract_hash = contract.get("contract_hash") or runner.get("contract_hash")
    contract_id = contract.get("contract_id") or runner.get("contract_id")
    validation_queue_id = contract.get("validation_queue_id") or runner.get("validation_queue_id")

    route_hash_payload = {
        "research_branch": "EXIT_RISK_SHAPE_DEEP_VALIDATION",
        "contract_hash": contract_hash,
        "contract_id": contract_id,
        "validation_queue_id": validation_queue_id,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "preview_count": preview_count,
        "validation_result_count": validation_result_count,
        "deep_validation_pass_count": deep_validation_pass_count,
        "validation_rows": validation_rows,
    }

    route_hash = str(contract_hash or stable_hash(route_hash_payload))
    lesson_id = f"LESSON_EXIT_RISK_SHAPE_DEEP_VALIDATION_FAILED_{stable_hash(route_hash_payload)}"

    preview_failed_deep_validation = (
        not runner_missing
        and not runner_error
        and canonical_policy_month_count == 12
        and preview_count > 0
        and validation_result_count > 0
        and deep_validation_pass_count == 0
        and all_deep_validations_passed is False
        and release_allowed is False
    )

    deep_validation_promising = (
        not runner_missing
        and not runner_error
        and deep_validation_pass_count > 0
        and release_allowed is False
    )

    failure_summary = summarize_failures(validation_rows)

    if preview_failed_deep_validation:
        evaluator_status = "EXIT_RISK_SHAPE_DEEP_VALIDATION_EVALUATOR_ROUTE_CLOSED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_SYMBOL_CLUSTER_SEGMENT_CONTRACT_NO_RUNTIME_ACTION"
        reason = (
            f"preview_count={preview_count}; validation_result_count={validation_result_count}; "
            "deep_validation_pass_count=0; route_closed=True"
        )
        branch_closed = True
        next_key = NEXT_RESEARCH_KEY
        next_module = NEXT_MODULE
    elif deep_validation_promising:
        evaluator_status = "EXIT_RISK_SHAPE_DEEP_VALIDATION_EVALUATOR_PROMISING_STILL_RELEASE_BLOCKED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_RELEASE_GATE_REVIEW_CONTRACT_KEEP_ALL_ACTIONS_BLOCKED"
        reason = (
            f"deep_validation_pass_count={deep_validation_pass_count}; "
            "release_allowed=False; release_gate_review_required"
        )
        branch_closed = False
        next_key = "EXIT_RISK_SHAPE_RELEASE_GATE_REVIEW_REQUIRED"
        next_module = "edge_factory_os_exit_risk_shape_release_gate_review_contract_builder_v1.py"
    else:
        evaluator_status = "EXIT_RISK_SHAPE_DEEP_VALIDATION_EVALUATOR_INCOMPLETE_OR_INVALID_INPUT"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "RERUN_OR_INSPECT_DEEP_VALIDATION_RUNNER_NO_RELEASE"
        reason = (
            f"runner_missing={runner_missing}; runner_error={runner_error}; "
            f"runner_status={runner_status}; preview_count={preview_count}; "
            f"validation_result_count={validation_result_count}; deep_validation_pass_count={deep_validation_pass_count}; "
            f"release_allowed={release_allowed}"
        )
        branch_closed = False
        next_key = None
        next_module = None

    lesson_record = {
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "lesson_type": "EXIT_RISK_SHAPE_DEEP_VALIDATION_FAILED",
        "research_branch": "EXIT_RISK_SHAPE_DEEP_VALIDATION",
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "validation_queue_id": validation_queue_id,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "runner_status": runner_status,
        "preview_count": preview_count,
        "validation_result_count": validation_result_count,
        "deep_validation_pass_count": deep_validation_pass_count,
        "all_deep_validations_passed": all_deep_validations_passed,
        "release_allowed": False,
        "branch_closed": branch_closed,
        "failure_summary": failure_summary,
        "validation_rows_sample": validation_rows[:10],
        "interpretation": (
            "Exit/risk-shape strict 12/12 preview existed, but failed deep validation. "
            "Preview must not become candidate, family, runtime, capital, active paper, live, or real order action."
        ),
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        "source_runner_json": str(RUNNER_JSON),
        "source_runner_csv": str(RUNNER_CSV),
        "source_month_csv": str(RUNNER_MONTH_CSV),
        "source_cost_csv": str(RUNNER_COST_CSV),
        "source_symbol_csv": str(RUNNER_SYMBOL_CSV),
    }

    block_record = {
        "route_hash": route_hash,
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "blocked_reason": "EXIT_RISK_SHAPE_PREVIEW_FAILED_DEEP_VALIDATION",
        "research_branch": "EXIT_RISK_SHAPE_DEEP_VALIDATION",
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "validation_queue_id": validation_queue_id,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "preview_count": preview_count,
        "validation_result_count": validation_result_count,
        "deep_validation_pass_count": deep_validation_pass_count,
        "reopen_requirements": [
            "new reference event set or materially different exit/risk-shape validation design",
            "new route hash",
            "full-universe replay pass",
            "rolling/OOS pass",
            "cost/slippage sensitivity pass",
            "symbol concentration pass",
            "strict 12/12 month stability recheck pass",
            "release gate review pass before any candidate/family/runtime/capital/live action",
        ],
    }

    next_queue = {
        "created_at_utc": utc_now_iso(),
        "queue_status": "EXIT_RISK_SHAPE_NEXT_RESEARCH_QUEUE_READY" if branch_closed else "EXIT_RISK_SHAPE_NEXT_RESEARCH_QUEUE_BLOCKED",
        "source_evaluator": "edge_factory_os_exit_risk_shape_deep_validation_evaluator_v1",
        "source_route_hash": route_hash,
        "strict_policy_key": STRICT_POLICY_KEY,
        "top_next_research_key": next_key,
        "top_next_module": next_module,
        "next_direction_queue": [
            {
                "research_key": NEXT_RESEARCH_KEY,
                "priority": 100,
                "title": "Symbol cluster and microstructure segment search",
                "allowed_scope": "READ_ONLY_RESEARCH",
                "why": (
                    "Entry/archetype/regime/motif branches failed and exit/risk strict previews failed deep validation. "
                    "Next route should examine whether stable structure exists only within pre-outcome symbol/microstructure segments."
                ),
                "next_module_recommendation": NEXT_MODULE,
                "candidate_generation_allowed_now": False,
                "family_release_allowed_now": False,
                "runtime_touch_allowed_now": False,
                "capital_change_allowed_now": False,
                "live_allowed_now": False,
                "real_orders_allowed_now": False,
            },
            {
                "research_key": "RD4_05_DATA_QUALITY_AND_PANEL_BIAS_AUDIT",
                "priority": 80,
                "title": "Data quality and panel bias audit",
                "allowed_scope": "READ_ONLY_RESEARCH",
                "why": "If symbol-segment research fails, audit whether panel construction or survivorship/coverage is limiting edge discovery.",
                "next_module_recommendation": "edge_factory_os_data_quality_panel_bias_audit_contract_builder_v1.py",
                "candidate_generation_allowed_now": False,
                "family_release_allowed_now": False,
            },
        ],
        "candidate_generation_allowed": False,
        "candidate_contract_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
    }

    lesson_append_status = None
    blocklist_append_status = None

    if preview_failed_deep_validation or deep_validation_promising:
        write_json(SPECIFIC_LESSON_PATH, lesson_record)
        lesson_append_status = append_lesson_record(LESSON_INDEX_PATH, lesson_record)

    if preview_failed_deep_validation:
        blocklist_append_status = append_blocklist_record(BLOCKLIST_PATH, block_record)
        write_json(NEXT_QUEUE_JSON, next_queue)

    result = {
        "evaluator_name": "edge_factory_os_exit_risk_shape_deep_validation_evaluator_v1",
        "created_at_utc": utc_now_iso(),
        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "branch_closed": branch_closed,
        "preview_failed_deep_validation": preview_failed_deep_validation,
        "deep_validation_promising": deep_validation_promising,
        "release_allowed": False,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "runner_status": runner_status,
        "preview_count": preview_count,
        "validation_result_count": validation_result_count,
        "deep_validation_pass_count": deep_validation_pass_count,
        "all_deep_validations_passed": all_deep_validations_passed,
        "failure_summary": failure_summary,
        "validation_rows": validation_rows,
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "validation_queue_id": validation_queue_id,
        "route_hash": route_hash,
        "lesson_id": lesson_id,
        "lesson_written": bool(preview_failed_deep_validation or deep_validation_promising),
        "blocklist_written": bool(preview_failed_deep_validation),
        "lesson_append_status": lesson_append_status,
        "blocklist_append_status": blocklist_append_status,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        "release_gate_feed": {
            "EXIT_RISK_SHAPE_DEEP_VALIDATION_EVALUATED": True,
            "EXIT_RISK_SHAPE_PREVIEW_FAILED_DEEP_VALIDATION": preview_failed_deep_validation,
            "STRICT_MONTH_STABILITY_12_OF_12": True,
            "DEEP_VALIDATION_PASS_COUNT": deep_validation_pass_count,
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
            "runner_csv": str(RUNNER_CSV),
            "runner_month_csv": str(RUNNER_MONTH_CSV),
            "runner_cost_csv": str(RUNNER_COST_CSV),
            "runner_symbol_csv": str(RUNNER_SYMBOL_CSV),
            "contract_path": str(CONTRACT_PATH),
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

    return 0 if preview_failed_deep_validation or deep_validation_promising else 2


if __name__ == "__main__":
    raise SystemExit(main())
