#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Data Quality Guard Runner v1

Purpose:
- Consume Data Quality Guard Contract v1.
- Verify mandatory data-quality guard requirements are formalized and enforceable.
- Produce a guard feed that future research/meta-synthesis must consume.
- Allow only read-only research continuation if guard layer is valid.

This runner does NOT:
- repair panel data
- run strategy research
- generate candidates
- create candidate contracts
- release families
- touch runtime
- change capital
- start active paper
- enable live
- place real orders
"""

from __future__ import annotations

import csv
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

CONTRACT_PATH = BASE_DIR / "edge_factory_os_research_direction_contracts" / "data_quality_guard_contract_latest.json"

AUDIT_RUNNER_JSON = (
    BASE_DIR
    / "edge_factory_os_data_quality_panel_bias_audit_runner"
    / "data_quality_panel_bias_audit_runner_latest.json"
)

AUDIT_EVALUATOR_JSON = (
    BASE_DIR
    / "edge_factory_os_data_quality_panel_bias_audit_evaluator"
    / "data_quality_panel_bias_audit_evaluator_latest.json"
)

OUT_DIR = BASE_DIR / "edge_factory_os_data_quality_guard_runner"
OUT_JSON = OUT_DIR / "data_quality_guard_runner_latest.json"
OUT_TXT = OUT_DIR / "data_quality_guard_runner_latest.txt"
OUT_REPORT_CSV = OUT_DIR / "data_quality_guard_report_latest.csv"
OUT_FEED_JSON = OUT_DIR / "data_quality_guard_feed_latest.json"

RUNNER_NAME = "edge_factory_os_data_quality_guard_runner_v1"
STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

REQUIRED_BUILDER_STATUS = "DATA_QUALITY_GUARD_CONTRACT_READY"
REQUIRED_DIRECTION_QUEUE_KEY = "RD4_05A_DATA_QUALITY_GUARD_AND_TRIAGE"

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


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fieldnames: List[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def as_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def evaluate_requirement(
    req: Dict[str, Any],
    contract: Dict[str, Any],
    audit_runner: Dict[str, Any],
    audit_evaluator: Dict[str, Any],
) -> Dict[str, Any]:
    guard_key = str(req.get("guard_key", "UNKNOWN_GUARD"))
    severity = str(req.get("severity", "MANDATORY"))
    source_finding_key = str(req.get("source_finding_key", "UNKNOWN"))
    blocks_release = bool(req.get("blocks_candidate_or_release_if_failed", True))

    source_summary = contract.get("source_audit_summary", {})
    if not isinstance(source_summary, dict):
        source_summary = {}

    canonical_policy_month_count = to_int(
        audit_runner.get("canonical_policy_month_count")
        or source_summary.get("canonical_policy_month_count"),
        0,
    )
    raw_calendar_month_count = to_int(
        audit_runner.get("raw_calendar_month_count")
        or source_summary.get("raw_calendar_month_count"),
        0,
    )
    symbol_count = to_int(
        audit_runner.get("symbol_count")
        or source_summary.get("symbol_count"),
        0,
    )
    row_count = to_int(
        audit_runner.get("row_count")
        or source_summary.get("row_count"),
        0,
    )

    canonical_months = as_list(audit_runner.get("canonical_months"))
    partial_boundary_months = as_list(audit_runner.get("partial_boundary_months"))
    excluded_policy_months = as_list(audit_runner.get("excluded_policy_months"))

    column_quality_summary = source_summary.get("column_quality_summary", {})
    if not isinstance(column_quality_summary, dict):
        column_quality_summary = {}

    gap_summary = source_summary.get("gap_summary", {})
    if not isinstance(gap_summary, dict):
        gap_summary = {}

    symbol_coverage_summary = source_summary.get("symbol_coverage_summary", {})
    if not isinstance(symbol_coverage_summary, dict):
        symbol_coverage_summary = {}

    outlier_summary = source_summary.get("outlier_summary", {})
    if not isinstance(outlier_summary, dict):
        outlier_summary = {}

    duplicate_info = source_summary.get("duplicate_info", {})
    if not isinstance(duplicate_info, dict):
        duplicate_info = {}

    pass_status = "PASS"
    guard_pass = True
    warning = False
    message = ""

    if not blocks_release:
        pass_status = "FAIL"
        guard_pass = False
        message = "Guard does not block candidate/release if failed; mandatory guard malformed."

    elif guard_key == "CANONICAL_MONTH_POLICY_GUARD":
        guard_pass = (
            canonical_policy_month_count == 12
            and raw_calendar_month_count >= 12
            and len(canonical_months) == 12
        )
        pass_status = "PASS" if guard_pass else "FAIL"
        message = (
            f"canonical_policy_month_count={canonical_policy_month_count}; "
            f"raw_calendar_month_count={raw_calendar_month_count}; "
            f"canonical_month_len={len(canonical_months)}"
        )

    elif guard_key == "FULL_UNIVERSE_IDENTITY_GUARD":
        audited_symbol_count = to_int(source_summary.get("symbol_count"), symbol_count)
        min_symbol_count = int(audited_symbol_count * 0.90) if audited_symbol_count else 1
        guard_pass = symbol_count >= min_symbol_count and row_count > 0 and canonical_policy_month_count == 12
        pass_status = "PASS" if guard_pass else "FAIL"
        message = (
            f"symbol_count={symbol_count}; audited_symbol_count={audited_symbol_count}; "
            f"min_symbol_count={min_symbol_count}; row_count={row_count}"
        )

    elif guard_key == "PARTIAL_BOUNDARY_MONTH_EXCLUSION_GUARD":
        if raw_calendar_month_count > 12:
            guard_pass = len(excluded_policy_months) > 0 and len(canonical_months) == 12
            pass_status = "PASS" if guard_pass else "FAIL"
            message = (
                f"raw_calendar_month_count={raw_calendar_month_count}; "
                f"partial_boundary_months={partial_boundary_months}; "
                f"excluded_policy_months={excluded_policy_months}; canonical_months={canonical_months}"
            )
        else:
            guard_pass = True
            pass_status = "PASS"
            message = "No extra raw calendar month detected; boundary exclusion guard remains active."

    elif guard_key == "DUPLICATE_SYMBOL_TIME_GUARD":
        duplicate_symbol_time_count = to_int(duplicate_info.get("duplicate_symbol_time_count"), 0)
        duplicate_full_row_count = to_int(duplicate_info.get("duplicate_full_row_count"), 0)
        guard_pass = duplicate_symbol_time_count == 0
        pass_status = "PASS" if guard_pass else "FAIL"
        message = f"duplicate_symbol_time_count={duplicate_symbol_time_count}; duplicate_full_row_count={duplicate_full_row_count}"

    elif guard_key == "HIGH_MISSINGNESS_FEATURE_USAGE_GUARD":
        # This guard cannot be fully exercised until a future runner declares used feature columns.
        # Passing here means the enforcement rule exists and must be consumed downstream.
        warning = True
        guard_pass = True
        pass_status = "PASS_WITH_ACTIVE_FUTURE_ENFORCEMENT"
        message = (
            f"columns_with_missing_gt_20pct={column_quality_summary.get('columns_with_missing_gt_20pct')}; "
            "future runners must check used features before research output is trusted."
        )

    elif guard_key == "INF_VALUE_GUARD":
        columns_with_inf = to_int(column_quality_summary.get("columns_with_inf"), 0)
        # Guard layer passes if rule is active; future used columns must have inf cleaned.
        warning = columns_with_inf > 0
        guard_pass = True
        pass_status = "PASS_WITH_ACTIVE_FUTURE_ENFORCEMENT" if warning else "PASS"
        message = f"columns_with_inf={columns_with_inf}; future used columns must have inf_count_after_cleaning=0."

    elif guard_key == "TIMESTAMP_GAP_GUARD":
        symbols_with_gap_gt_24h = to_int(gap_summary.get("symbols_with_gap_gt_24h"), 0)
        symbols_with_gap_gt_3h = to_int(gap_summary.get("symbols_with_gap_gt_3h"), 0)
        warning = symbols_with_gap_gt_24h > 0 or symbols_with_gap_gt_3h > 0
        guard_pass = True
        pass_status = "PASS_WITH_ACTIVE_FUTURE_ENFORCEMENT" if warning else "PASS"
        message = (
            f"symbols_with_gap_gt_24h={symbols_with_gap_gt_24h}; "
            f"symbols_with_gap_gt_3h={symbols_with_gap_gt_3h}; future feature builders must be gap-aware."
        )

    elif guard_key == "SYMBOL_LIFECYCLE_COVERAGE_GUARD":
        symbols_lt_10 = to_int(symbol_coverage_summary.get("symbols_lt_10_active_months"), 0)
        warning = symbols_lt_10 > 0
        guard_pass = True
        pass_status = "PASS_WITH_ACTIVE_FUTURE_ENFORCEMENT" if warning else "PASS"
        message = f"symbols_lt_10_active_months={symbols_lt_10}; future runners must be lifecycle-aware."

    elif guard_key == "EXTREME_RETURN_OUTLIER_GUARD":
        outlier_count = to_int(outlier_summary.get("exported_outlier_row_count"), 0)
        warning = outlier_count > 0
        guard_pass = True
        pass_status = "PASS_WITH_ACTIVE_FUTURE_ENFORCEMENT" if warning else "PASS"
        message = f"exported_outlier_row_count={outlier_count}; future signal rows must run outlier sensitivity."

    elif guard_key == "OHLC_CONSISTENCY_GUARD":
        high_low_quality = source_summary.get("high_low_range_quality", {})
        if not isinstance(high_low_quality, dict):
            high_low_quality = {}
        close_outside = to_int(high_low_quality.get("close_outside_high_low_count"), 0)
        high_low_inverted = to_int(high_low_quality.get("high_low_inverted_count"), 0)
        guard_pass = high_low_inverted == 0
        warning = close_outside > 0
        pass_status = "PASS_WITH_ACTIVE_FUTURE_ENFORCEMENT" if guard_pass and warning else ("PASS" if guard_pass else "FAIL")
        message = f"high_low_inverted_count={high_low_inverted}; close_outside_high_low_count={close_outside}"

    else:
        # Unknown guards are allowed only as active triage guards, not silent pass.
        warning = True
        guard_pass = True
        pass_status = "PASS_WITH_TRIAGE_REQUIRED"
        message = "Unknown guard key; future research must explicitly triage it before candidate/release paths."

    return {
        "guard_key": guard_key,
        "source_finding_key": source_finding_key,
        "severity": severity,
        "guard_pass": bool(guard_pass),
        "warning": bool(warning),
        "pass_status": pass_status,
        "message": message,
        "pass_condition": req.get("pass_condition"),
        "blocks_candidate_or_release_if_failed": blocks_release,
        "required_behavior": json.dumps(req.get("required_behavior", []), ensure_ascii=False),
        "recommendation": req.get("recommendation"),
    }


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS DATA QUALITY GUARD RUNNER v1")
    lines.append("=" * 100)

    for k in [
        "guard_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "guard_pass",
        "guard_requirement_count",
        "guard_pass_count",
        "guard_fail_count",
        "guard_warning_count",
        "canonical_month_policy_pass",
        "panel_identity_guard_pass",
        "research_meta_synthesis_allowed",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("GUARD RESULTS")
    lines.append("-" * 100)
    for row in result.get("guard_results", []):
        lines.append(
            f"{row.get('guard_key')} | pass={row.get('guard_pass')} | "
            f"status={row.get('pass_status')} | warning={row.get('warning')} | {row.get('message')}"
        )

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        lines.append(f"{k}: {v}")

    lines.append("")
    lines.append("OUTPUT PATHS")
    lines.append("-" * 100)
    for k in ["output_json", "output_txt", "guard_report_csv", "guard_feed_json"]:
        lines.append(f"{k}: {result.get(k)}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS DATA QUALITY GUARD RUNNER v1")
    print("=" * 100)
    print(f"guard_status: {result.get('guard_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"guard_pass: {result.get('guard_pass')}")
    print(f"guard_requirement_count: {result.get('guard_requirement_count')}")
    print(f"guard_pass_count: {result.get('guard_pass_count')}")
    print(f"guard_fail_count: {result.get('guard_fail_count')}")
    print(f"guard_warning_count: {result.get('guard_warning_count')}")
    print(f"research_meta_synthesis_allowed: {result.get('research_meta_synthesis_allowed')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"CSV : {result.get('guard_report_csv')}")
    print(f"FEED: {result.get('guard_feed_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    contract = load_json(CONTRACT_PATH, default={})
    audit_runner = load_json(AUDIT_RUNNER_JSON, default={})
    audit_evaluator = load_json(AUDIT_EVALUATOR_JSON, default={})

    guard_requirements = contract.get("guard_requirements")
    if not isinstance(guard_requirements, list):
        guard_requirements = []

    base_result = {
        "runner_name": RUNNER_NAME,
        "created_at_utc": utc_now_iso(),
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": contract.get("canonical_policy_month_count"),
        "contract_path": str(CONTRACT_PATH),
        "contract_id": contract.get("contract_id"),
        "contract_hash": contract.get("contract_hash"),
        "research_key": contract.get("research_key"),
        "direction_queue_key": contract.get("direction_queue_key"),
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "guard_report_csv": str(OUT_REPORT_CSV),
        "guard_feed_json": str(OUT_FEED_JSON),
        **SAFETY_FLAGS,
    }

    prerequisite_pass = (
        contract.get("builder_status") == REQUIRED_BUILDER_STATUS
        and contract.get("direction_queue_key") == REQUIRED_DIRECTION_QUEUE_KEY
        and int(contract.get("canonical_policy_month_count") or 0) == 12
        and len(guard_requirements) > 0
    )

    if not prerequisite_pass:
        result = {
            **base_result,
            "guard_status": "DATA_QUALITY_GUARD_RUNNER_BLOCKED_PREREQUISITE_NOT_MET",
            "severity": "ATTENTION",
            "allowed_scope": "READ_ONLY_REVIEW",
            "next_action": "INSPECT_DATA_QUALITY_GUARD_CONTRACT_NO_RELEASE",
            "reason": (
                f"builder_status={contract.get('builder_status')}; "
                f"direction_queue_key={contract.get('direction_queue_key')}; "
                f"canonical_policy_month_count={contract.get('canonical_policy_month_count')}; "
                f"guard_requirement_count={len(guard_requirements)}"
            ),
            "guard_pass": False,
            "research_meta_synthesis_allowed": False,
            **SAFETY_FLAGS,
        }
        write_json(OUT_JSON, result)
        write_text_summary(OUT_TXT, result)
        print_summary(result)
        return 2

    guard_results = [
        evaluate_requirement(req, contract, audit_runner, audit_evaluator)
        for req in guard_requirements
    ]

    guard_requirement_count = len(guard_results)
    guard_pass_count = int(sum(1 for r in guard_results if r.get("guard_pass") is True))
    guard_fail_count = int(sum(1 for r in guard_results if r.get("guard_pass") is False))
    guard_warning_count = int(sum(1 for r in guard_results if r.get("warning") is True))

    canonical_month_policy_pass = any(
        r.get("guard_key") == "CANONICAL_MONTH_POLICY_GUARD" and r.get("guard_pass") is True
        for r in guard_results
    )
    panel_identity_guard_pass = any(
        r.get("guard_key") == "FULL_UNIVERSE_IDENTITY_GUARD" and r.get("guard_pass") is True
        for r in guard_results
    )

    guard_pass = (
        guard_fail_count == 0
        and guard_requirement_count > 0
        and canonical_month_policy_pass
        and panel_identity_guard_pass
    )

    research_meta_synthesis_allowed = bool(guard_pass)

    if guard_pass and guard_warning_count > 0:
        guard_status = "DATA_QUALITY_GUARD_PASS_WITH_ACTIVE_ATTENTION_GUARDS"
        severity = "ATTENTION"
        next_action = "BUILD_RESEARCH_META_SYNTHESIZER_AFTER_DATA_QUALITY_GUARD"
        reason = (
            f"guard_pass=True; guard_requirement_count={guard_requirement_count}; "
            f"guard_warning_count={guard_warning_count}; active_future_enforcement_required"
        )
    elif guard_pass:
        guard_status = "DATA_QUALITY_GUARD_PASS"
        severity = "OK"
        next_action = "BUILD_RESEARCH_META_SYNTHESIZER_AFTER_DATA_QUALITY_GUARD"
        reason = f"guard_pass=True; guard_requirement_count={guard_requirement_count}"
    else:
        guard_status = "DATA_QUALITY_GUARD_FAIL_BLOCK_RESEARCH_META_SYNTHESIS"
        severity = "ATTENTION"
        next_action = "BUILD_DATA_QUALITY_GUARD_REPAIR_OR_TRIAGE_NO_RESEARCH"
        reason = (
            f"guard_pass=False; guard_fail_count={guard_fail_count}; "
            f"canonical_month_policy_pass={canonical_month_policy_pass}; "
            f"panel_identity_guard_pass={panel_identity_guard_pass}"
        )

    feed = {
        "created_at_utc": utc_now_iso(),
        "feed_name": "data_quality_guard_feed_v1",
        "guard_status": guard_status,
        "guard_pass": guard_pass,
        "research_meta_synthesis_allowed": research_meta_synthesis_allowed,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "guard_requirement_count": guard_requirement_count,
        "guard_pass_count": guard_pass_count,
        "guard_fail_count": guard_fail_count,
        "guard_warning_count": guard_warning_count,
        "mandatory_future_research_requirements": guard_results,
        "candidate_generation_allowed": False,
        "candidate_contract_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
    }

    write_json(OUT_FEED_JSON, feed)
    write_csv(OUT_REPORT_CSV, guard_results)

    result = {
        **base_result,
        "guard_status": guard_status,
        "severity": severity,
        "allowed_scope": "READ_ONLY_RESEARCH",
        "next_action": next_action,
        "reason": reason,
        "guard_pass": guard_pass,
        "guard_requirement_count": guard_requirement_count,
        "guard_pass_count": guard_pass_count,
        "guard_fail_count": guard_fail_count,
        "guard_warning_count": guard_warning_count,
        "canonical_month_policy_pass": canonical_month_policy_pass,
        "panel_identity_guard_pass": panel_identity_guard_pass,
        "research_meta_synthesis_allowed": research_meta_synthesis_allowed,
        "guard_results": guard_results,
        "guard_feed_json": str(OUT_FEED_JSON),
        "release_gate_feed": {
            "DATA_QUALITY_GUARD_RUNNER_RAN": True,
            "DATA_QUALITY_GUARD_PASS": guard_pass,
            "RESEARCH_META_SYNTHESIS_ALLOWED_FROM_GUARD": research_meta_synthesis_allowed,
            "STRICT_MONTH_STABILITY_12_OF_12": True,
            "RELEASE_PASS_FROM_THIS_RUNNER": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_THIS_RUNNER": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_THIS_RUNNER": False,
            "FAMILY_RELEASE_ALLOWED_FROM_THIS_RUNNER": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_THIS_RUNNER": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_THIS_RUNNER": False,
            "ACTIVE_PAPER_ALLOWED_FROM_THIS_RUNNER": False,
            "LIVE_ALLOWED_FROM_THIS_RUNNER": False,
            "REAL_ORDERS_ALLOWED_FROM_THIS_RUNNER": False,
        },
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text_summary(OUT_TXT, result)
    print_summary(result)

    return 0 if guard_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
