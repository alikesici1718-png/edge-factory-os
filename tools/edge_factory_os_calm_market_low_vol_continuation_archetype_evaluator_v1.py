#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Calm Market Low-Vol Continuation Archetype Evaluator v1

Purpose:
- Evaluate Calm Market Low-Vol Continuation Runner v1 output.
- If valid rules were tested but strict_12_subset_pass_count == 0,
  close the branch with lesson/blocklist evidence.
- Route next step to offline research result synthesis / new research direction queue.
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

RUNNER_DIR = BASE_DIR / "edge_factory_os_calm_market_low_vol_continuation_archetype_runner"
RUNNER_JSON = RUNNER_DIR / "calm_market_low_vol_continuation_archetype_runner_latest.json"
RUNNER_CSV = RUNNER_DIR / "calm_market_low_vol_continuation_archetype_ranked_rules_latest.csv"

CONTRACT_PATH = (
    BASE_DIR
    / "edge_factory_os_research_direction_contracts"
    / "calm_market_low_vol_continuation_archetype_contract_latest.json"
)

OUT_DIR = BASE_DIR / "edge_factory_os_calm_market_low_vol_continuation_archetype_evaluator"
OUT_JSON = OUT_DIR / "calm_market_low_vol_continuation_archetype_evaluator_latest.json"
OUT_TXT = OUT_DIR / "calm_market_low_vol_continuation_archetype_evaluator_latest.txt"

LESSON_DIR = BASE_DIR / "edge_factory_os_lesson_memory"
LESSON_INDEX_PATH = LESSON_DIR / "lesson_memory_index.json"
BLOCKLIST_PATH = LESSON_DIR / "candidate_route_blocklist.json"
SPECIFIC_LESSON_PATH = LESSON_DIR / "calm_market_low_vol_continuation_no_strict_12_lesson_latest.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RECOMMENDED_RESEARCH_KEY = "RD3_SYNTHESIZE_FAILED_ARCHETYPES_AND_QUEUE_NEW_DIRECTION"
NEXT_MODULE = "edge_factory_os_offline_research_result_synthesizer_v1.py"

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
    except Exception:
        return default


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


def read_top_csv_rows(path: Path, limit: int = 10) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    rows: List[Dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(dict(row))
                if len(rows) >= limit:
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


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS CALM MARKET LOW-VOL CONTINUATION ARCHETYPE EVALUATOR v1")
    lines.append("=" * 100)

    keys = [
        "evaluator_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "branch_closed",
        "strict_policy_key",
        "canonical_policy_month_count",
        "rules_tested",
        "valid_rule_count",
        "strict_12_subset_pass_count",
        "next_recommended_research_key",
        "next_module",
        "lesson_id",
        "route_hash",
    ]

    for k in keys:
        lines.append(f"{k}: {result.get(k)}")

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
    print("EDGE FACTORY OS CALM MARKET LOW-VOL CONTINUATION ARCHETYPE EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {result.get('evaluator_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"branch_closed: {result.get('branch_closed')}")
    print(f"strict_policy_key: {result.get('strict_policy_key')}")
    print(f"canonical_policy_month_count: {result.get('canonical_policy_month_count')}")
    print(f"rules_tested: {result.get('rules_tested')}")
    print(f"valid_rule_count: {result.get('valid_rule_count')}")
    print(f"strict_12_subset_pass_count: {result.get('strict_12_subset_pass_count')}")
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
    print(f"LESSON: {result.get('specific_lesson_path')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LESSON_DIR.mkdir(parents=True, exist_ok=True)

    runner = load_json(RUNNER_JSON, default={})
    contract = load_json(CONTRACT_PATH, default={})
    top_rows = read_top_csv_rows(RUNNER_CSV, limit=10)

    rules_tested = to_int(runner.get("rules_tested"))
    valid_rule_count = to_int(runner.get("valid_rule_count"))
    strict_12_subset_pass_count = to_int(runner.get("strict_12_subset_pass_count"))
    canonical_policy_month_count = to_int(runner.get("canonical_policy_month_count"), 12)

    runner_status = str(runner.get("runner_status", ""))
    runner_missing = not RUNNER_JSON.exists()
    runner_error = "ERROR" in runner_status.upper()

    contract_hash = contract.get("contract_hash") or runner.get("contract_hash")
    contract_id = contract.get("contract_id") or runner.get("contract_id")

    route_hash_payload = {
        "research_branch": "CALM_MARKET_LOW_VOL_CONTINUATION_ARCHETYPE_SEARCH",
        "contract_hash": contract_hash,
        "contract_id": contract_id,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "rules_tested": rules_tested,
        "valid_rule_count": valid_rule_count,
        "strict_12_subset_pass_count": strict_12_subset_pass_count,
    }

    route_hash = str(contract_hash or stable_hash(route_hash_payload))
    lesson_id = f"LESSON_CALM_MARKET_LOW_VOL_CONTINUATION_NO_STRICT_12_{route_hash}"

    branch_closed = (
        not runner_missing
        and not runner_error
        and rules_tested > 0
        and valid_rule_count > 0
        and strict_12_subset_pass_count == 0
        and canonical_policy_month_count == 12
    )

    if branch_closed:
        evaluator_status = "CALM_MARKET_LOW_VOL_CONTINUATION_EVALUATOR_BRANCH_CLOSED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "RUN_OFFLINE_RESEARCH_RESULT_SYNTHESIZER_OR_NEW_RESEARCH_QUEUE"
        reason = (
            f"rules_tested={rules_tested}; "
            f"valid_rule_count={valid_rule_count}; "
            f"strict_12_subset_pass_count={strict_12_subset_pass_count}; "
            "branch_closed=True"
        )
    elif strict_12_subset_pass_count > 0:
        evaluator_status = "CALM_MARKET_LOW_VOL_CONTINUATION_EVALUATOR_STRICT_PREVIEW_REVIEW_REQUIRED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "DO_NOT_RELEASE_BUILD_DEEP_VALIDATION_EVALUATOR"
        reason = (
            f"strict_12_subset_pass_count={strict_12_subset_pass_count}; "
            "preview found but not release pass"
        )
        branch_closed = False
    else:
        evaluator_status = "CALM_MARKET_LOW_VOL_CONTINUATION_EVALUATOR_INCOMPLETE_OR_INVALID_INPUT"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "RERUN_OR_INSPECT_CALM_RUNNER_NO_RELEASE"
        reason = (
            f"runner_missing={runner_missing}; runner_error={runner_error}; "
            f"runner_status={runner_status}; rules_tested={rules_tested}; "
            f"valid_rule_count={valid_rule_count}; strict_12_subset_pass_count={strict_12_subset_pass_count}"
        )
        branch_closed = False

    lesson_record = {
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "lesson_type": "STRICT_MONTH_STABILITY_12_OF_12_BRANCH_FAILURE",
        "research_branch": "CALM_MARKET_LOW_VOL_CONTINUATION_ARCHETYPE_SEARCH",
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "runner_status": runner_status,
        "rules_tested": rules_tested,
        "valid_rule_count": valid_rule_count,
        "strict_12_subset_pass_count": strict_12_subset_pass_count,
        "raw_calendar_month_count": runner.get("raw_calendar_month_count"),
        "symbol_count": runner.get("symbol_count"),
        "row_count": runner.get("row_count"),
        "branch_closed": branch_closed,
        "failure_summary": (
            "Calm/low-vol continuation archetype produced valid full-universe rules "
            "but no strict 12-of-12 canonical month-stable preview."
        ),
        "do_not_repeat_without_new_features": True,
        "next_recommended_research_key": NEXT_RECOMMENDED_RESEARCH_KEY,
        "next_module": NEXT_MODULE,
        "source_runner_json": str(RUNNER_JSON),
        "source_runner_csv": str(RUNNER_CSV),
        "top_rows_sample": top_rows[:5],
    }

    block_record = {
        "route_hash": route_hash,
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "blocked_reason": "NO_STRICT_MONTH_STABILITY_12_OF_12_CALM_LOW_VOL_CONTINUATION",
        "research_branch": "CALM_MARKET_LOW_VOL_CONTINUATION_ARCHETYPE_SEARCH",
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "rules_tested": rules_tested,
        "valid_rule_count": valid_rule_count,
        "strict_12_subset_pass_count": strict_12_subset_pass_count,
        "reopen_requirements": [
            "new feature family or materially different archetype",
            "new route hash",
            "canonical_policy_month_count == 12",
            "canonical_positive_month_count == 12",
            "canonical_negative_month_count == 0",
            "full prerequisite chain before any candidate/family/runtime/capital/live action",
        ],
    }

    lesson_append_status: Optional[Dict[str, Any]] = None
    blocklist_append_status: Optional[Dict[str, Any]] = None

    if branch_closed:
        write_json(SPECIFIC_LESSON_PATH, lesson_record)
        lesson_append_status = append_lesson_record(LESSON_INDEX_PATH, lesson_record)
        blocklist_append_status = append_blocklist_record(BLOCKLIST_PATH, block_record)

    result = {
        "evaluator_name": "edge_factory_os_calm_market_low_vol_continuation_archetype_evaluator_v1",
        "created_at_utc": utc_now_iso(),
        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "branch_closed": branch_closed,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "runner_status": runner_status,
        "rules_tested": rules_tested,
        "valid_rule_count": valid_rule_count,
        "strict_12_subset_pass_count": strict_12_subset_pass_count,
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "lesson_id": lesson_id,
        "lesson_written": bool(branch_closed),
        "blocklist_written": bool(branch_closed),
        "lesson_append_status": lesson_append_status,
        "blocklist_append_status": blocklist_append_status,
        "next_recommended_research_key": NEXT_RECOMMENDED_RESEARCH_KEY if branch_closed else None,
        "next_module": NEXT_MODULE if branch_closed else None,
        "release_gate_feed": {
            "CALM_MARKET_LOW_VOL_CONTINUATION_BRANCH_EVALUATED": True,
            "CALM_MARKET_LOW_VOL_CONTINUATION_BRANCH_CLOSED": branch_closed,
            "STRICT_MONTH_STABILITY_12_OF_12": True,
            "STRICT_12_SUBSET_PASS_COUNT": strict_12_subset_pass_count,
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
            "contract_path": str(CONTRACT_PATH),
        },
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "lesson_index_path": str(LESSON_INDEX_PATH),
        "blocklist_path": str(BLOCKLIST_PATH),
        "specific_lesson_path": str(SPECIFIC_LESSON_PATH),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text_summary(OUT_TXT, result)
    print_summary(result)

    return 0 if branch_closed else 2


if __name__ == "__main__":
    raise SystemExit(main())
