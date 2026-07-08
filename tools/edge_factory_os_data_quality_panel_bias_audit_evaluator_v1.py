#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Data Quality Panel Bias Audit Evaluator v1

Purpose:
- Evaluate Data Quality Panel Bias Audit Runner v1 output.
- Classify CRITICAL / ATTENTION / INFO findings.
- Decide whether to:
  1) block further research and build panel repair,
  2) build data-quality guard / triage contract,
  3) proceed to research meta-synthesis with audit guard.
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

RUNNER_DIR = BASE_DIR / "edge_factory_os_data_quality_panel_bias_audit_runner"
RUNNER_JSON = RUNNER_DIR / "data_quality_panel_bias_audit_runner_latest.json"
FINDINGS_CSV = RUNNER_DIR / "data_quality_audit_findings_latest.csv"
COLUMN_CSV = RUNNER_DIR / "data_quality_column_quality_latest.csv"
SYMBOL_CSV = RUNNER_DIR / "data_quality_symbol_coverage_latest.csv"
MONTH_CSV = RUNNER_DIR / "data_quality_month_coverage_latest.csv"
GAP_CSV = RUNNER_DIR / "data_quality_symbol_gap_summary_latest.csv"
OUTLIER_CSV = RUNNER_DIR / "data_quality_return_outliers_latest.csv"

CONTRACT_PATH = BASE_DIR / "edge_factory_os_research_direction_contracts" / "data_quality_panel_bias_audit_contract_latest.json"

OUT_DIR = BASE_DIR / "edge_factory_os_data_quality_panel_bias_audit_evaluator"
OUT_JSON = OUT_DIR / "data_quality_panel_bias_audit_evaluator_latest.json"
OUT_TXT = OUT_DIR / "data_quality_panel_bias_audit_evaluator_latest.txt"
NEXT_QUEUE_JSON = OUT_DIR / "data_quality_panel_bias_next_queue_latest.json"

LESSON_DIR = BASE_DIR / "edge_factory_os_lesson_memory"
LESSON_INDEX_PATH = LESSON_DIR / "lesson_memory_index.json"
SPECIFIC_LESSON_PATH = LESSON_DIR / "data_quality_panel_bias_audit_attention_lesson_latest.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_GUARD_KEY = "RD4_05A_DATA_QUALITY_GUARD_AND_TRIAGE"
NEXT_GUARD_MODULE = "edge_factory_os_data_quality_guard_contract_builder_v1.py"

NEXT_META_KEY = "RD4_06_RESEARCH_META_SYNTHESIS_AFTER_AUDIT"
NEXT_META_MODULE = "edge_factory_os_research_meta_synthesizer_v2.py"

NEXT_REPAIR_KEY = "RD4_05R_PANEL_REPAIR_OR_DATA_FIX_CONTRACT"
NEXT_REPAIR_MODULE = "edge_factory_os_panel_repair_contract_builder_v1.py"

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


def classify_findings(findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    critical = [f for f in findings if str(f.get("severity", "")).upper() == "CRITICAL"]
    attention = [f for f in findings if str(f.get("severity", "")).upper() == "ATTENTION"]
    info = [f for f in findings if str(f.get("severity", "")).upper() == "INFO"]

    attention_keys = [str(f.get("finding_key", "")) for f in attention]
    critical_keys = [str(f.get("finding_key", "")) for f in critical]

    material_repair_keys = {
        "DUPLICATE_ROWS_PRESENT",
        "HIGH_COLUMN_MISSINGNESS",
        "INF_VALUES_PRESENT",
        "LARGE_TIMESTAMP_GAPS_PRESENT",
        "EXTREME_RETURN_OUTLIERS_PRESENT",
        "CLOSE_OUTSIDE_HIGH_LOW",
        "SYMBOL_LIFECYCLE_SHORT_COVERAGE_PRESENT",
    }

    guard_only_keys = {
        "RAW_13_WITH_PARTIAL_BOUNDARIES_DETECTED",
        "PANEL_PATH_NOT_OBVIOUS_FEATURE_PANEL",
    }

    material_attention = [k for k in attention_keys if k in material_repair_keys]
    guard_only_attention = [k for k in attention_keys if k in guard_only_keys]
    unknown_attention = [k for k in attention_keys if k and k not in material_repair_keys and k not in guard_only_keys]

    if critical:
        decision_class = "CRITICAL_PANEL_REPAIR_REQUIRED"
        next_key = NEXT_REPAIR_KEY
        next_module = NEXT_REPAIR_MODULE
        decision_reason = "critical audit findings exist; block further research until panel repair/data fix contract"
    elif material_attention:
        decision_class = "ATTENTION_DATA_QUALITY_GUARD_REQUIRED"
        next_key = NEXT_GUARD_KEY
        next_module = NEXT_GUARD_MODULE
        decision_reason = "material attention findings exist; build guard/triage before further research"
    elif unknown_attention:
        decision_class = "ATTENTION_UNKNOWN_FINDINGS_TRIAGE_REQUIRED"
        next_key = NEXT_GUARD_KEY
        next_module = NEXT_GUARD_MODULE
        decision_reason = "unknown attention findings exist; triage before research meta-synthesis"
    elif attention:
        decision_class = "GUARD_ONLY_ATTENTION_META_SYNTHESIS_ALLOWED_AFTER_GUARD"
        next_key = NEXT_GUARD_KEY
        next_module = NEXT_GUARD_MODULE
        decision_reason = "only guard-style attention findings exist; build guard then meta-synthesis"
    else:
        decision_class = "AUDIT_CLEAN_META_SYNTHESIS_ALLOWED"
        next_key = NEXT_META_KEY
        next_module = NEXT_META_MODULE
        decision_reason = "no critical or attention findings; research meta-synthesis allowed"

    return {
        "critical_count_from_csv": len(critical),
        "attention_count_from_csv": len(attention),
        "info_count_from_csv": len(info),
        "critical_keys": critical_keys,
        "attention_keys": attention_keys,
        "material_attention_keys": material_attention,
        "guard_only_attention_keys": guard_only_attention,
        "unknown_attention_keys": unknown_attention,
        "decision_class": decision_class,
        "next_key": next_key,
        "next_module": next_module,
        "decision_reason": decision_reason,
    }


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS DATA QUALITY PANEL BIAS AUDIT EVALUATOR v1")
    lines.append("=" * 100)

    for k in [
        "evaluator_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "audit_decision_class",
        "audit_research_blocked_until_guard",
        "strict_policy_key",
        "canonical_policy_month_count",
        "raw_calendar_month_count",
        "symbol_count",
        "row_count",
        "finding_count",
        "critical_finding_count",
        "attention_finding_count",
        "next_recommended_research_key",
        "next_module",
        "lesson_id",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("FINDINGS")
    lines.append("-" * 100)
    for row in result.get("audit_findings", []):
        lines.append(f"[{row.get('severity')}] {row.get('finding_key')}: {row.get('message')}")
        lines.append(f"  recommendation: {row.get('recommendation')}")

    lines.append("")
    lines.append("CLASSIFICATION")
    lines.append("-" * 100)
    cls = result.get("classification", {})
    for k, v in cls.items():
        lines.append(f"{k}: {v}")

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
        "specific_lesson_path",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS DATA QUALITY PANEL BIAS AUDIT EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {result.get('evaluator_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"audit_decision_class: {result.get('audit_decision_class')}")
    print(f"audit_research_blocked_until_guard: {result.get('audit_research_blocked_until_guard')}")
    print(f"strict_policy_key: {result.get('strict_policy_key')}")
    print(f"canonical_policy_month_count: {result.get('canonical_policy_month_count')}")
    print(f"raw_calendar_month_count: {result.get('raw_calendar_month_count')}")
    print(f"symbol_count: {result.get('symbol_count')}")
    print(f"row_count: {result.get('row_count')}")
    print(f"finding_count: {result.get('finding_count')}")
    print(f"critical_finding_count: {result.get('critical_finding_count')}")
    print(f"attention_finding_count: {result.get('attention_finding_count')}")
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
    findings = read_csv_rows(FINDINGS_CSV)

    runner_status = str(runner.get("runner_status", ""))
    runner_missing = not RUNNER_JSON.exists()
    runner_error = "ERROR" in runner_status.upper()

    canonical_policy_month_count = to_int(runner.get("canonical_policy_month_count"), 12)
    raw_calendar_month_count = to_int(runner.get("raw_calendar_month_count"))
    symbol_count = to_int(runner.get("symbol_count"))
    row_count = to_int(runner.get("row_count"))
    finding_count = to_int(runner.get("finding_count"))
    critical_finding_count = to_int(runner.get("critical_finding_count"))
    attention_finding_count = to_int(runner.get("attention_finding_count"))
    info_finding_count = to_int(runner.get("info_finding_count"))

    canonical_months = runner.get("canonical_months") if isinstance(runner.get("canonical_months"), list) else []
    partial_boundary_months = runner.get("partial_boundary_months") if isinstance(runner.get("partial_boundary_months"), list) else []
    excluded_policy_months = runner.get("excluded_policy_months") if isinstance(runner.get("excluded_policy_months"), list) else []

    classification = classify_findings(findings)

    audit_ran_valid = (
        not runner_missing
        and not runner_error
        and canonical_policy_month_count == 12
        and raw_calendar_month_count >= 12
        and symbol_count > 0
        and row_count > 0
        and finding_count >= 0
    )

    contract_hash = contract.get("contract_hash") or runner.get("contract_hash")
    contract_id = contract.get("contract_id") or runner.get("contract_id")

    lesson_hash_payload = {
        "research_branch": "DATA_QUALITY_AND_PANEL_BIAS_AUDIT",
        "contract_hash": contract_hash,
        "contract_id": contract_id,
        "runner_status": runner_status,
        "classification": classification,
        "finding_count": finding_count,
        "critical_finding_count": critical_finding_count,
        "attention_finding_count": attention_finding_count,
        "findings": findings,
    }

    lesson_id = f"LESSON_DATA_QUALITY_PANEL_BIAS_AUDIT_{stable_hash(lesson_hash_payload)}"

    if not audit_ran_valid:
        evaluator_status = "DATA_QUALITY_PANEL_BIAS_AUDIT_EVALUATOR_INCOMPLETE_OR_INVALID_INPUT"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "RERUN_OR_INSPECT_DATA_QUALITY_AUDIT_RUNNER_NO_RELEASE"
        reason = (
            f"runner_missing={runner_missing}; runner_error={runner_error}; runner_status={runner_status}; "
            f"canonical_policy_month_count={canonical_policy_month_count}; raw_months={raw_calendar_month_count}; "
            f"symbols={symbol_count}; rows={row_count}"
        )
        audit_research_blocked_until_guard = True
        next_key = None
        next_module = None
    else:
        decision_class = classification["decision_class"]
        next_key = classification["next_key"]
        next_module = classification["next_module"]

        if decision_class == "CRITICAL_PANEL_REPAIR_REQUIRED":
            evaluator_status = "DATA_QUALITY_PANEL_BIAS_AUDIT_EVALUATOR_CRITICAL_REPAIR_REQUIRED"
            severity = "CRITICAL"
            allowed_scope = "READ_ONLY_RESEARCH"
            next_action = "BUILD_PANEL_REPAIR_OR_DATA_FIX_CONTRACT_BLOCK_RESEARCH"
            audit_research_blocked_until_guard = True
        elif decision_class in {
            "ATTENTION_DATA_QUALITY_GUARD_REQUIRED",
            "ATTENTION_UNKNOWN_FINDINGS_TRIAGE_REQUIRED",
            "GUARD_ONLY_ATTENTION_META_SYNTHESIS_ALLOWED_AFTER_GUARD",
        }:
            evaluator_status = "DATA_QUALITY_PANEL_BIAS_AUDIT_EVALUATOR_ATTENTION_GUARD_REQUIRED"
            severity = "ATTENTION"
            allowed_scope = "READ_ONLY_RESEARCH"
            next_action = "BUILD_DATA_QUALITY_GUARD_CONTRACT_BEFORE_META_SYNTHESIS"
            audit_research_blocked_until_guard = True
        else:
            evaluator_status = "DATA_QUALITY_PANEL_BIAS_AUDIT_EVALUATOR_CLEAN_META_SYNTHESIS_ALLOWED"
            severity = "OK"
            allowed_scope = "READ_ONLY_RESEARCH"
            next_action = "BUILD_RESEARCH_META_SYNTHESIZER_AFTER_AUDIT"
            audit_research_blocked_until_guard = False

        reason = (
            f"decision_class={decision_class}; critical={critical_finding_count}; attention={attention_finding_count}; "
            f"raw_months={raw_calendar_month_count}; canonical_months={canonical_policy_month_count}; "
            f"symbols={symbol_count}; rows={row_count}"
        )

    next_queue = {
        "created_at_utc": utc_now_iso(),
        "queue_status": "DATA_QUALITY_PANEL_BIAS_NEXT_QUEUE_READY" if audit_ran_valid else "DATA_QUALITY_PANEL_BIAS_NEXT_QUEUE_BLOCKED",
        "source_evaluator": "edge_factory_os_data_quality_panel_bias_audit_evaluator_v1",
        "strict_policy_key": STRICT_POLICY_KEY,
        "audit_decision_class": classification.get("decision_class"),
        "audit_research_blocked_until_guard": audit_research_blocked_until_guard,
        "top_next_research_key": next_key,
        "top_next_module": next_module,
        "next_direction_queue": [
            {
                "research_key": next_key,
                "priority": 100,
                "next_module_recommendation": next_module,
                "allowed_scope": "READ_ONLY_RESEARCH",
                "why": classification.get("decision_reason"),
                "candidate_generation_allowed_now": False,
                "candidate_contract_allowed_now": False,
                "family_release_allowed_now": False,
                "runtime_touch_allowed_now": False,
                "capital_change_allowed_now": False,
                "live_allowed_now": False,
                "real_orders_allowed_now": False,
            }
        ] if next_key and next_module else [],
        "candidate_generation_allowed": False,
        "candidate_contract_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
    }

    lesson_record = {
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "lesson_type": "DATA_QUALITY_PANEL_BIAS_AUDIT_EVALUATED",
        "research_branch": "DATA_QUALITY_AND_PANEL_BIAS_AUDIT",
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "strict_policy_key": STRICT_POLICY_KEY,
        "runner_status": runner_status,
        "audit_decision_class": classification.get("decision_class"),
        "audit_research_blocked_until_guard": audit_research_blocked_until_guard,
        "canonical_policy_month_count": canonical_policy_month_count,
        "raw_calendar_month_count": raw_calendar_month_count,
        "canonical_months": canonical_months,
        "partial_boundary_months": partial_boundary_months,
        "excluded_policy_months": excluded_policy_months,
        "symbol_count": symbol_count,
        "row_count": row_count,
        "finding_count": finding_count,
        "critical_finding_count": critical_finding_count,
        "attention_finding_count": attention_finding_count,
        "info_finding_count": info_finding_count,
        "classification": classification,
        "audit_findings": findings,
        "interpretation": (
            "Data quality audit found no critical issue but did find attention findings. "
            "Further research should consume a data-quality guard/triage layer before reopening or creating new research paths."
        ),
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        "source_runner_json": str(RUNNER_JSON),
        "source_findings_csv": str(FINDINGS_CSV),
        "source_column_csv": str(COLUMN_CSV),
        "source_symbol_csv": str(SYMBOL_CSV),
        "source_month_csv": str(MONTH_CSV),
        "source_gap_csv": str(GAP_CSV),
        "source_outlier_csv": str(OUTLIER_CSV),
    }

    lesson_append_status = None
    if audit_ran_valid:
        write_json(SPECIFIC_LESSON_PATH, lesson_record)
        lesson_append_status = append_lesson_record(LESSON_INDEX_PATH, lesson_record)
        write_json(NEXT_QUEUE_JSON, next_queue)

    result = {
        "evaluator_name": "edge_factory_os_data_quality_panel_bias_audit_evaluator_v1",
        "created_at_utc": utc_now_iso(),
        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "audit_decision_class": classification.get("decision_class"),
        "audit_research_blocked_until_guard": audit_research_blocked_until_guard,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "runner_status": runner_status,
        "raw_calendar_month_count": raw_calendar_month_count,
        "canonical_months": canonical_months,
        "partial_boundary_months": partial_boundary_months,
        "excluded_policy_months": excluded_policy_months,
        "symbol_count": symbol_count,
        "row_count": row_count,
        "finding_count": finding_count,
        "critical_finding_count": critical_finding_count,
        "attention_finding_count": attention_finding_count,
        "info_finding_count": info_finding_count,
        "classification": classification,
        "audit_findings": findings,
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "lesson_id": lesson_id,
        "lesson_written": bool(audit_ran_valid),
        "lesson_append_status": lesson_append_status,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        "release_gate_feed": {
            "DATA_QUALITY_PANEL_BIAS_AUDIT_EVALUATED": True,
            "DATA_QUALITY_AUDIT_CRITICAL_COUNT": critical_finding_count,
            "DATA_QUALITY_AUDIT_ATTENTION_COUNT": attention_finding_count,
            "DATA_QUALITY_RESEARCH_BLOCKED_UNTIL_GUARD": audit_research_blocked_until_guard,
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
            "findings_csv": str(FINDINGS_CSV),
            "column_csv": str(COLUMN_CSV),
            "symbol_csv": str(SYMBOL_CSV),
            "month_csv": str(MONTH_CSV),
            "gap_csv": str(GAP_CSV),
            "outlier_csv": str(OUTLIER_CSV),
            "contract_path": str(CONTRACT_PATH),
        },
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "next_queue_json": str(NEXT_QUEUE_JSON),
        "lesson_index_path": str(LESSON_INDEX_PATH),
        "specific_lesson_path": str(SPECIFIC_LESSON_PATH),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text_summary(OUT_TXT, result)
    print_summary(result)

    return 0 if audit_ran_valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
