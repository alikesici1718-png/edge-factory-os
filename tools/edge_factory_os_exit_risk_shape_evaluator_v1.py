#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Exit Risk Shape Evaluator v1

Purpose:
- Evaluate Exit Risk Shape Runner v1 output.
- If strict 12/12 previews exist, mark them as PREVIEW ONLY.
- Do NOT allow candidate generation, family release, runtime touch, capital change, active paper, live, or real orders.
- Create a deep-validation requirement/queue for:
  OOS/rolling, cost/slippage, symbol concentration, route-hash preflight, full prerequisite release gate.

This evaluator is intentionally conservative:
- strict_12_exit_shape_preview_count > 0 is not release.
- It only means: build deep validation contract next.
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

RUNNER_DIR = BASE_DIR / "edge_factory_os_exit_risk_shape_runner"
RUNNER_JSON = RUNNER_DIR / "exit_risk_shape_runner_latest.json"
RUNNER_CSV = RUNNER_DIR / "exit_risk_shape_ranked_diagnostics_latest.csv"
RUNNER_MONTH_CSV = RUNNER_DIR / "exit_risk_shape_month_diagnostics_latest.csv"

CONTRACT_PATH = BASE_DIR / "edge_factory_os_research_direction_contracts" / "exit_risk_shape_contract_latest.json"

OUT_DIR = BASE_DIR / "edge_factory_os_exit_risk_shape_evaluator"
OUT_JSON = OUT_DIR / "exit_risk_shape_evaluator_latest.json"
OUT_TXT = OUT_DIR / "exit_risk_shape_evaluator_latest.txt"
DEEP_VALIDATION_QUEUE_JSON = OUT_DIR / "exit_risk_shape_deep_validation_queue_latest.json"
PREVIEW_CSV = OUT_DIR / "exit_risk_shape_strict_preview_candidates_for_validation_latest.csv"

LESSON_DIR = BASE_DIR / "edge_factory_os_lesson_memory"
LESSON_INDEX_PATH = LESSON_DIR / "lesson_memory_index.json"
SPECIFIC_LESSON_PATH = LESSON_DIR / "exit_risk_shape_strict_preview_deep_validation_required_lesson_latest.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_MODULE = "edge_factory_os_exit_risk_shape_deep_validation_contract_builder_v1.py"
NEXT_RESEARCH_KEY = "EXIT_RISK_SHAPE_DEEP_VALIDATION_REQUIRED_V1"

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
        if value is None:
            return default
        return int(float(value))
    except Exception:
        return default


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
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


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


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


def get_strict_preview_rows(ranked_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    strict_rows = []

    for row in ranked_rows:
        raw = str(row.get("strict_12_exit_shape_preview_pass", "")).strip().lower()
        is_true = raw in {"true", "1", "yes"}

        if is_true:
            cleaned = dict(row)
            cleaned["validation_status"] = "DEEP_VALIDATION_REQUIRED_PREVIEW_ONLY"
            cleaned["release_allowed"] = "False"
            cleaned["candidate_generation_allowed"] = "False"
            cleaned["family_release_allowed"] = "False"
            strict_rows.append(cleaned)

    strict_rows = sorted(
        strict_rows,
        key=lambda r: (
            to_int(r.get("positive_months")),
            to_float(r.get("total_month_pnl_bps")),
            to_float(r.get("worst_month_bps")),
            to_int(r.get("symbol_count")),
            to_int(r.get("event_count")),
        ),
        reverse=True,
    )

    return strict_rows


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS EXIT RISK SHAPE EVALUATOR v1")
    lines.append("=" * 100)

    for k in [
        "evaluator_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "preview_found",
        "deep_validation_required",
        "branch_closed",
        "release_allowed",
        "strict_policy_key",
        "canonical_policy_month_count",
        "reference_event_count",
        "exit_shape_count",
        "ranked_diagnostic_row_count",
        "strict_12_exit_shape_preview_count",
        "next_module",
        "validation_queue_id",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("TOP STRICT PREVIEWS FOR VALIDATION")
    lines.append("-" * 100)
    for row in result.get("strict_preview_rows", [])[:10]:
        lines.append(
            f"{row.get('reference_id')} {row.get('side')} {row.get('exit_shape_id')} | "
            f"positive={row.get('positive_months')}/{row.get('canonical_month_count')} | "
            f"total={row.get('total_month_pnl_bps')} | worst={row.get('worst_month_bps')} | "
            f"events={row.get('event_count')} symbols={row.get('symbol_count')}"
        )

    lines.append("")
    lines.append("REQUIRED VALIDATION CHAIN")
    lines.append("-" * 100)
    for item in result.get("required_validation_chain", []):
        lines.append(f"- {item}")

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
        "deep_validation_queue_json",
        "preview_csv",
        "specific_lesson_path",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS EXIT RISK SHAPE EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {result.get('evaluator_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"preview_found: {result.get('preview_found')}")
    print(f"deep_validation_required: {result.get('deep_validation_required')}")
    print(f"branch_closed: {result.get('branch_closed')}")
    print(f"release_allowed: {result.get('release_allowed')}")
    print(f"strict_policy_key: {result.get('strict_policy_key')}")
    print(f"canonical_policy_month_count: {result.get('canonical_policy_month_count')}")
    print(f"strict_12_exit_shape_preview_count: {result.get('strict_12_exit_shape_preview_count')}")
    print(f"next_module: {result.get('next_module')}")
    print(f"validation_queue_id: {result.get('validation_queue_id')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"QUEUE: {result.get('deep_validation_queue_json')}")
    print(f"PREVIEW CSV: {result.get('preview_csv')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LESSON_DIR.mkdir(parents=True, exist_ok=True)

    runner = load_json(RUNNER_JSON, default={})
    contract = load_json(CONTRACT_PATH, default={})
    ranked_rows = read_csv_rows(RUNNER_CSV)
    strict_preview_rows = get_strict_preview_rows(ranked_rows)

    runner_status = str(runner.get("runner_status", ""))
    runner_missing = not RUNNER_JSON.exists()
    runner_error = "ERROR" in runner_status.upper()

    canonical_policy_month_count = to_int(runner.get("canonical_policy_month_count"), 12)
    reference_event_count = to_int(runner.get("reference_event_count"))
    exit_shape_count = to_int(runner.get("exit_shape_count"))
    ranked_diagnostic_row_count = to_int(runner.get("ranked_diagnostic_row_count"))
    strict_12_exit_shape_preview_count = to_int(runner.get("strict_12_exit_shape_preview_count"))
    symbol_count = to_int(runner.get("symbol_count"))
    row_count = to_int(runner.get("row_count"))
    raw_calendar_month_count = to_int(runner.get("raw_calendar_month_count"))

    preview_found = (
        not runner_missing
        and not runner_error
        and canonical_policy_month_count == 12
        and strict_12_exit_shape_preview_count > 0
        and len(strict_preview_rows) > 0
    )

    no_preview_complete = (
        not runner_missing
        and not runner_error
        and canonical_policy_month_count == 12
        and reference_event_count > 0
        and exit_shape_count > 0
        and ranked_diagnostic_row_count > 0
        and strict_12_exit_shape_preview_count == 0
    )

    contract_hash = contract.get("contract_hash") or runner.get("contract_hash")
    contract_id = contract.get("contract_id") or runner.get("contract_id")

    route_hash_payload = {
        "research_branch": "EXIT_RISK_SHAPE_SEARCH",
        "contract_hash": contract_hash,
        "contract_id": contract_id,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "strict_12_exit_shape_preview_count": strict_12_exit_shape_preview_count,
        "top_preview": strict_preview_rows[0] if strict_preview_rows else None,
    }

    validation_queue_id = f"EXIT_RISK_SHAPE_DEEP_VALIDATION_QUEUE_{stable_hash(route_hash_payload)}"
    lesson_id = f"LESSON_EXIT_RISK_SHAPE_PREVIEW_DEEP_VALIDATION_REQUIRED_{stable_hash(route_hash_payload)}"

    required_validation_chain = [
        "route_hash_preflight_no_repeat_failure",
        "full_universe_replay_validation",
        "train_oos_or_rolling_split_validation",
        "cost_slippage_sensitivity_validation",
        "symbol_concentration_validation",
        "month_stability_12_of_12_recheck",
        "mae_mfe_path_sanity_check",
        "risk_capital_safety_check",
        "release_gate_review",
        "explicit_action_authorization_guard",
    ]

    if preview_found:
        evaluator_status = "EXIT_RISK_SHAPE_EVALUATOR_PREVIEW_FOUND_DEEP_VALIDATION_REQUIRED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_EXIT_RISK_SHAPE_DEEP_VALIDATION_CONTRACT_KEEP_ACTIONS_BLOCKED"
        reason = (
            f"strict_12_exit_shape_preview_count={strict_12_exit_shape_preview_count}; "
            "preview_found=True; release_allowed=False; deep_validation_required=True"
        )
        branch_closed = False
        deep_validation_required = True
    elif no_preview_complete:
        evaluator_status = "EXIT_RISK_SHAPE_EVALUATOR_BRANCH_CLOSED_NO_PREVIEW"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "ROTATE_TO_NEXT_RESEARCH_DIRECTION_NO_RELEASE"
        reason = (
            f"ranked_diagnostic_row_count={ranked_diagnostic_row_count}; "
            "strict_12_exit_shape_preview_count=0; branch_closed=True"
        )
        branch_closed = True
        deep_validation_required = False
    else:
        evaluator_status = "EXIT_RISK_SHAPE_EVALUATOR_INCOMPLETE_OR_INVALID_INPUT"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "RERUN_OR_INSPECT_EXIT_RISK_SHAPE_RUNNER_NO_RELEASE"
        reason = (
            f"runner_missing={runner_missing}; runner_error={runner_error}; "
            f"runner_status={runner_status}; ranked_diagnostic_row_count={ranked_diagnostic_row_count}; "
            f"strict_12_exit_shape_preview_count={strict_12_exit_shape_preview_count}; "
            f"strict_preview_rows={len(strict_preview_rows)}"
        )
        branch_closed = False
        deep_validation_required = False

    write_csv(PREVIEW_CSV, strict_preview_rows)

    lesson_record = {
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "lesson_type": "EXIT_RISK_SHAPE_STRICT_PREVIEW_DEEP_VALIDATION_REQUIRED",
        "research_branch": "EXIT_RISK_SHAPE_SEARCH",
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "validation_queue_id": validation_queue_id,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "runner_status": runner_status,
        "strict_12_exit_shape_preview_count": strict_12_exit_shape_preview_count,
        "reference_event_count": reference_event_count,
        "exit_shape_count": exit_shape_count,
        "ranked_diagnostic_row_count": ranked_diagnostic_row_count,
        "preview_found": preview_found,
        "release_allowed": False,
        "candidate_generation_allowed": False,
        "deep_validation_required": deep_validation_required,
        "warning": (
            "Strict 12/12 exit-shape preview is not release permission. "
            "It only authorizes read-only deep validation contract generation."
        ),
        "required_validation_chain": required_validation_chain,
        "top_strict_preview_rows": strict_preview_rows[:10],
        "source_runner_json": str(RUNNER_JSON),
        "source_runner_csv": str(RUNNER_CSV),
    }

    write_json(SPECIFIC_LESSON_PATH, lesson_record)
    lesson_append_status = append_lesson_record(LESSON_INDEX_PATH, lesson_record)

    queue_payload = {
        "created_at_utc": utc_now_iso(),
        "queue_status": "EXIT_RISK_SHAPE_DEEP_VALIDATION_QUEUE_READY" if preview_found else "EXIT_RISK_SHAPE_DEEP_VALIDATION_QUEUE_BLOCKED",
        "validation_queue_id": validation_queue_id,
        "source_evaluator": "edge_factory_os_exit_risk_shape_evaluator_v1",
        "source_runner_json": str(RUNNER_JSON),
        "source_runner_csv": str(RUNNER_CSV),
        "source_month_csv": str(RUNNER_MONTH_CSV),
        "source_contract_path": str(CONTRACT_PATH),
        "strict_policy_key": STRICT_POLICY_KEY,
        "preview_found": preview_found,
        "strict_12_exit_shape_preview_count": strict_12_exit_shape_preview_count,
        "strict_preview_rows": strict_preview_rows,
        "required_validation_chain": required_validation_chain,
        "next_module": NEXT_MODULE if preview_found else None,
        "next_research_key": NEXT_RESEARCH_KEY if preview_found else None,
        "release_allowed": False,
        "candidate_generation_allowed": False,
        "candidate_contract_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
    }

    write_json(DEEP_VALIDATION_QUEUE_JSON, queue_payload)

    result = {
        "evaluator_name": "edge_factory_os_exit_risk_shape_evaluator_v1",
        "created_at_utc": utc_now_iso(),
        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "preview_found": preview_found,
        "deep_validation_required": deep_validation_required,
        "branch_closed": branch_closed,
        "release_allowed": False,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "runner_status": runner_status,
        "reference_event_count": reference_event_count,
        "exit_shape_count": exit_shape_count,
        "ranked_diagnostic_row_count": ranked_diagnostic_row_count,
        "strict_12_exit_shape_preview_count": strict_12_exit_shape_preview_count,
        "strict_preview_row_count": len(strict_preview_rows),
        "strict_preview_rows": strict_preview_rows,
        "raw_calendar_month_count": raw_calendar_month_count,
        "symbol_count": symbol_count,
        "row_count": row_count,
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "validation_queue_id": validation_queue_id,
        "lesson_id": lesson_id,
        "lesson_written": True,
        "lesson_append_status": lesson_append_status,
        "required_validation_chain": required_validation_chain,
        "next_research_key": NEXT_RESEARCH_KEY if preview_found else None,
        "next_module": NEXT_MODULE if preview_found else None,
        "release_gate_feed": {
            "EXIT_RISK_SHAPE_BRANCH_EVALUATED": True,
            "EXIT_RISK_SHAPE_PREVIEW_FOUND": preview_found,
            "EXIT_RISK_SHAPE_DEEP_VALIDATION_REQUIRED": deep_validation_required,
            "STRICT_MONTH_STABILITY_12_OF_12": True,
            "STRICT_12_EXIT_SHAPE_PREVIEW_COUNT": strict_12_exit_shape_preview_count,
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
            "contract_path": str(CONTRACT_PATH),
        },
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "deep_validation_queue_json": str(DEEP_VALIDATION_QUEUE_JSON),
        "preview_csv": str(PREVIEW_CSV),
        "lesson_index_path": str(LESSON_INDEX_PATH),
        "specific_lesson_path": str(SPECIFIC_LESSON_PATH),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text_summary(OUT_TXT, result)
    print_summary(result)

    return 0 if preview_found or no_preview_complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
