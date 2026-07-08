#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Symbol Cluster Segment Evaluator v1

Purpose:
- Evaluate Symbol Cluster Segment Runner v1 output.
- If segment diagnostics ran but strict_12_segment_preview_count == 0,
  close/archive the branch.
- Record lesson + blocklist evidence.
- Queue next materially different research direction:
  RD4_05_DATA_QUALITY_AND_PANEL_BIAS_AUDIT.
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

RUNNER_DIR = BASE_DIR / "edge_factory_os_symbol_cluster_segment_runner"
RUNNER_JSON = RUNNER_DIR / "symbol_cluster_segment_runner_latest.json"
RUNNER_CSV = RUNNER_DIR / "symbol_cluster_segment_ranked_diagnostics_latest.csv"
RUNNER_MONTH_CSV = RUNNER_DIR / "symbol_cluster_segment_month_diagnostics_latest.csv"
RUNNER_PROFILE_CSV = RUNNER_DIR / "symbol_cluster_segment_symbol_profiles_latest.csv"
RUNNER_MEMBERSHIP_CSV = RUNNER_DIR / "symbol_cluster_segment_membership_latest.csv"
RUNNER_CONCENTRATION_CSV = RUNNER_DIR / "symbol_cluster_segment_concentration_latest.csv"

CONTRACT_PATH = BASE_DIR / "edge_factory_os_research_direction_contracts" / "symbol_cluster_segment_contract_latest.json"

OUT_DIR = BASE_DIR / "edge_factory_os_symbol_cluster_segment_evaluator"
OUT_JSON = OUT_DIR / "symbol_cluster_segment_evaluator_latest.json"
OUT_TXT = OUT_DIR / "symbol_cluster_segment_evaluator_latest.txt"
NEXT_QUEUE_JSON = OUT_DIR / "symbol_cluster_segment_next_research_queue_latest.json"

LESSON_DIR = BASE_DIR / "edge_factory_os_lesson_memory"
LESSON_INDEX_PATH = LESSON_DIR / "lesson_memory_index.json"
BLOCKLIST_PATH = LESSON_DIR / "candidate_route_blocklist.json"
SPECIFIC_LESSON_PATH = LESSON_DIR / "symbol_cluster_segment_no_strict_12_lesson_latest.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD4_05_DATA_QUALITY_AND_PANEL_BIAS_AUDIT"
NEXT_MODULE = "edge_factory_os_data_quality_panel_bias_audit_contract_builder_v1.py"

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


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS SYMBOL CLUSTER SEGMENT EVALUATOR v1")
    lines.append("=" * 100)

    for k in [
        "evaluator_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "branch_closed",
        "strict_policy_key",
        "canonical_policy_month_count",
        "symbol_count",
        "row_count",
        "segment_membership_count",
        "segment_diagnostic_row_count",
        "strict_12_segment_preview_count",
        "next_recommended_research_key",
        "next_module",
        "lesson_id",
        "route_hash",
    ]:
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
    print("EDGE FACTORY OS SYMBOL CLUSTER SEGMENT EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {result.get('evaluator_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"branch_closed: {result.get('branch_closed')}")
    print(f"strict_policy_key: {result.get('strict_policy_key')}")
    print(f"canonical_policy_month_count: {result.get('canonical_policy_month_count')}")
    print(f"segment_diagnostic_row_count: {result.get('segment_diagnostic_row_count')}")
    print(f"strict_12_segment_preview_count: {result.get('strict_12_segment_preview_count')}")
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
    top_rows = read_csv_rows(RUNNER_CSV, limit=10)

    runner_status = str(runner.get("runner_status", ""))
    runner_missing = not RUNNER_JSON.exists()
    runner_error = "ERROR" in runner_status.upper()

    canonical_policy_month_count = to_int(runner.get("canonical_policy_month_count"), 12)
    symbol_count = to_int(runner.get("symbol_count"))
    row_count = to_int(runner.get("row_count"))
    raw_calendar_month_count = to_int(runner.get("raw_calendar_month_count"))
    segment_membership_count = to_int(runner.get("segment_membership_count"))
    segment_group_count = to_int(runner.get("segment_group_count"))
    segment_diagnostic_row_count = to_int(runner.get("segment_diagnostic_row_count"))
    strict_12_segment_preview_count = to_int(runner.get("strict_12_segment_preview_count"))
    month_diagnostic_row_count = to_int(runner.get("month_diagnostic_row_count"))
    concentration_row_count = to_int(runner.get("concentration_row_count"))

    contract_hash = contract.get("contract_hash") or runner.get("contract_hash")
    contract_id = contract.get("contract_id") or runner.get("contract_id")

    route_hash_payload = {
        "research_branch": "SYMBOL_CLUSTER_AND_MICROSTRUCTURE_SEGMENT_SEARCH",
        "contract_hash": contract_hash,
        "contract_id": contract_id,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "segment_membership_count": segment_membership_count,
        "segment_diagnostic_row_count": segment_diagnostic_row_count,
        "strict_12_segment_preview_count": strict_12_segment_preview_count,
    }

    route_hash = str(contract_hash or stable_hash(route_hash_payload))
    lesson_id = f"LESSON_SYMBOL_CLUSTER_SEGMENT_NO_STRICT_12_{stable_hash(route_hash_payload)}"

    branch_closed = (
        not runner_missing
        and not runner_error
        and canonical_policy_month_count == 12
        and segment_diagnostic_row_count > 0
        and strict_12_segment_preview_count == 0
    )

    preview_found = (
        not runner_missing
        and not runner_error
        and strict_12_segment_preview_count > 0
    )

    if branch_closed:
        evaluator_status = "SYMBOL_CLUSTER_SEGMENT_EVALUATOR_BRANCH_CLOSED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_DATA_QUALITY_PANEL_BIAS_AUDIT_CONTRACT_NO_RUNTIME_ACTION"
        reason = (
            f"segment_diagnostic_row_count={segment_diagnostic_row_count}; "
            f"strict_12_segment_preview_count={strict_12_segment_preview_count}; "
            "branch_closed=True"
        )
        next_key = NEXT_RESEARCH_KEY
        next_module = NEXT_MODULE
    elif preview_found:
        evaluator_status = "SYMBOL_CLUSTER_SEGMENT_EVALUATOR_PREVIEW_FOUND_DEEP_VALIDATION_REQUIRED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_SYMBOL_CLUSTER_SEGMENT_DEEP_VALIDATION_CONTRACT_KEEP_ACTIONS_BLOCKED"
        reason = (
            f"strict_12_segment_preview_count={strict_12_segment_preview_count}; "
            "preview_found=True; release_allowed=False"
        )
        branch_closed = False
        next_key = "SYMBOL_CLUSTER_SEGMENT_DEEP_VALIDATION_REQUIRED"
        next_module = "edge_factory_os_symbol_cluster_segment_deep_validation_contract_builder_v1.py"
    else:
        evaluator_status = "SYMBOL_CLUSTER_SEGMENT_EVALUATOR_INCOMPLETE_OR_INVALID_INPUT"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "RERUN_OR_INSPECT_SYMBOL_CLUSTER_SEGMENT_RUNNER_NO_RELEASE"
        reason = (
            f"runner_missing={runner_missing}; runner_error={runner_error}; "
            f"runner_status={runner_status}; segment_diagnostic_row_count={segment_diagnostic_row_count}; "
            f"strict_12_segment_preview_count={strict_12_segment_preview_count}"
        )
        branch_closed = False
        next_key = None
        next_module = None

    lesson_record = {
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "lesson_type": "STRICT_MONTH_STABILITY_12_OF_12_SYMBOL_SEGMENT_FAILURE",
        "research_branch": "SYMBOL_CLUSTER_AND_MICROSTRUCTURE_SEGMENT_SEARCH",
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "runner_status": runner_status,
        "symbol_count": symbol_count,
        "row_count": row_count,
        "raw_calendar_month_count": raw_calendar_month_count,
        "segment_membership_count": segment_membership_count,
        "segment_group_count": segment_group_count,
        "segment_diagnostic_row_count": segment_diagnostic_row_count,
        "strict_12_segment_preview_count": strict_12_segment_preview_count,
        "month_diagnostic_row_count": month_diagnostic_row_count,
        "concentration_row_count": concentration_row_count,
        "branch_closed": branch_closed,
        "failure_summary": (
            "Symbol/microstructure segment search produced segment diagnostics but zero strict 12-of-12 canonical month previews."
        ),
        "interpretation": (
            "The OS has now failed broad entry/archetype, feature repair, regime-first, label-free motif, "
            "exit/risk-shape deep validation, and symbol/microstructure segment searches under strict 12/12. "
            "Next route should audit data quality, coverage, survivorship, panel construction, and possible bias before further edge discovery."
        ),
        "do_not_repeat_without_new_feature_space_or_data_audit": True,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        "source_runner_json": str(RUNNER_JSON),
        "source_runner_csv": str(RUNNER_CSV),
        "source_profile_csv": str(RUNNER_PROFILE_CSV),
        "source_membership_csv": str(RUNNER_MEMBERSHIP_CSV),
        "source_month_csv": str(RUNNER_MONTH_CSV),
        "source_concentration_csv": str(RUNNER_CONCENTRATION_CSV),
        "top_segment_rows_sample": top_rows,
    }

    block_record = {
        "route_hash": route_hash,
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "blocked_reason": "NO_STRICT_MONTH_STABILITY_12_OF_12_SYMBOL_CLUSTER_SEGMENT_V1",
        "research_branch": "SYMBOL_CLUSTER_AND_MICROSTRUCTURE_SEGMENT_SEARCH",
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "segment_diagnostic_row_count": segment_diagnostic_row_count,
        "strict_12_segment_preview_count": strict_12_segment_preview_count,
        "reopen_requirements": [
            "materially different segment feature space or data audit finding",
            "new route hash",
            "no manual symbol whitelist",
            "no manual month blacklist",
            "strict 12/12 canonical month preview",
            "deep validation before any candidate/family/runtime/capital/live action",
        ],
    }

    next_queue = {
        "created_at_utc": utc_now_iso(),
        "queue_status": "SYMBOL_CLUSTER_SEGMENT_NEXT_RESEARCH_QUEUE_READY" if branch_closed else "SYMBOL_CLUSTER_SEGMENT_NEXT_RESEARCH_QUEUE_BLOCKED",
        "source_evaluator": "edge_factory_os_symbol_cluster_segment_evaluator_v1",
        "source_route_hash": route_hash,
        "strict_policy_key": STRICT_POLICY_KEY,
        "top_next_research_key": next_key,
        "top_next_module": next_module,
        "next_direction_queue": [
            {
                "research_key": NEXT_RESEARCH_KEY,
                "priority": 100,
                "title": "Data quality and panel bias audit",
                "allowed_scope": "READ_ONLY_RESEARCH",
                "why": (
                    "Multiple materially different research branches failed strict 12/12. "
                    "Before more edge discovery, audit whether panel coverage, symbol lifecycle, missingness, survivorship, "
                    "calendar windows, costs, or feature construction are limiting or distorting the search."
                ),
                "next_module_recommendation": NEXT_MODULE,
                "candidate_generation_allowed_now": False,
                "candidate_contract_allowed_now": False,
                "family_release_allowed_now": False,
                "runtime_touch_allowed_now": False,
                "capital_change_allowed_now": False,
                "live_allowed_now": False,
                "real_orders_allowed_now": False,
            }
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

    if branch_closed or preview_found:
        write_json(SPECIFIC_LESSON_PATH, lesson_record)
        lesson_append_status = append_lesson_record(LESSON_INDEX_PATH, lesson_record)

    if branch_closed:
        blocklist_append_status = append_blocklist_record(BLOCKLIST_PATH, block_record)
        write_json(NEXT_QUEUE_JSON, next_queue)

    result = {
        "evaluator_name": "edge_factory_os_symbol_cluster_segment_evaluator_v1",
        "created_at_utc": utc_now_iso(),
        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "branch_closed": branch_closed,
        "preview_found": preview_found,
        "release_allowed": False,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "runner_status": runner_status,
        "symbol_count": symbol_count,
        "row_count": row_count,
        "raw_calendar_month_count": raw_calendar_month_count,
        "segment_membership_count": segment_membership_count,
        "segment_group_count": segment_group_count,
        "segment_diagnostic_row_count": segment_diagnostic_row_count,
        "strict_12_segment_preview_count": strict_12_segment_preview_count,
        "month_diagnostic_row_count": month_diagnostic_row_count,
        "concentration_row_count": concentration_row_count,
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "lesson_id": lesson_id,
        "lesson_written": bool(branch_closed or preview_found),
        "blocklist_written": bool(branch_closed),
        "lesson_append_status": lesson_append_status,
        "blocklist_append_status": blocklist_append_status,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        "release_gate_feed": {
            "SYMBOL_CLUSTER_SEGMENT_BRANCH_EVALUATED": True,
            "SYMBOL_CLUSTER_SEGMENT_BRANCH_CLOSED": branch_closed,
            "STRICT_MONTH_STABILITY_12_OF_12": True,
            "STRICT_12_SEGMENT_PREVIEW_COUNT": strict_12_segment_preview_count,
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
            "runner_profile_csv": str(RUNNER_PROFILE_CSV),
            "runner_membership_csv": str(RUNNER_MEMBERSHIP_CSV),
            "runner_concentration_csv": str(RUNNER_CONCENTRATION_CSV),
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

    return 0 if branch_closed or preview_found else 2


if __name__ == "__main__":
    raise SystemExit(main())
