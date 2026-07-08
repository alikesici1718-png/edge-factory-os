#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Data Quality Guard Contract Builder v1

Purpose:
- Consume Data Quality Panel Bias Audit Evaluator v1 output.
- Convert audit attention findings into mandatory research guards.
- Block research meta-synthesis until guard requirements are formalized.
- Keep all candidate/family/runtime/capital/live/real-order actions blocked.

This builder does NOT:
- repair panel data
- run strategy research
- generate candidates
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
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

SOURCE_EVALUATOR_JSON = (
    BASE_DIR
    / "edge_factory_os_data_quality_panel_bias_audit_evaluator"
    / "data_quality_panel_bias_audit_evaluator_latest.json"
)

SOURCE_QUEUE_JSON = (
    BASE_DIR
    / "edge_factory_os_data_quality_panel_bias_audit_evaluator"
    / "data_quality_panel_bias_next_queue_latest.json"
)

AUDIT_FINDINGS_CSV = (
    BASE_DIR
    / "edge_factory_os_data_quality_panel_bias_audit_runner"
    / "data_quality_audit_findings_latest.csv"
)

AUDIT_RUNNER_JSON = (
    BASE_DIR
    / "edge_factory_os_data_quality_panel_bias_audit_runner"
    / "data_quality_panel_bias_audit_runner_latest.json"
)

OUT_DIR = BASE_DIR / "edge_factory_os_research_direction_contracts"
OUT_JSON = OUT_DIR / "data_quality_guard_contract_latest.json"
OUT_TXT = OUT_DIR / "data_quality_guard_contract_latest.txt"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

REQUIRED_EVALUATOR_STATUS = "DATA_QUALITY_PANEL_BIAS_AUDIT_EVALUATOR_ATTENTION_GUARD_REQUIRED"
REQUIRED_DIRECTION_KEY = "RD4_05A_DATA_QUALITY_GUARD_AND_TRIAGE"

RESEARCH_KEY = "DATA_QUALITY_GUARD_AND_TRIAGE_V1"
DIRECTION_QUEUE_KEY = "RD4_05A_DATA_QUALITY_GUARD_AND_TRIAGE"
NEXT_MODULE = "edge_factory_os_data_quality_guard_runner_v1.py"

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


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def utc_now_iso() -> str:
    return utc_now().isoformat()


def timestamp_compact() -> str:
    return utc_now().strftime("%Y%m%d_%H%M%S")


def load_json(path: Path, default: Any = None) -> Any:
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"_load_error": f"{type(e).__name__}: {e}", "_path": str(path)}


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


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    tmp.replace(path)


def stable_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def get_top_queue_direction(queue: Dict[str, Any], evaluator: Dict[str, Any]) -> Dict[str, Any]:
    q = queue.get("next_direction_queue")
    if isinstance(q, list) and q:
        sorted_q = sorted(
            [x for x in q if isinstance(x, dict)],
            key=lambda x: int(x.get("priority", 0)),
            reverse=True,
        )
        if sorted_q:
            return sorted_q[0]

    return {
        "research_key": evaluator.get("next_recommended_research_key"),
        "next_module_recommendation": evaluator.get("next_module"),
        "priority": 100,
    }


def guard_requirements_from_findings(findings: List[Dict[str, Any]], evaluator: Dict[str, Any], runner: Dict[str, Any]) -> List[Dict[str, Any]]:
    requirements: List[Dict[str, Any]] = []

    # Always required after audit.
    requirements.append({
        "guard_key": "CANONICAL_MONTH_POLICY_GUARD",
        "severity": "MANDATORY",
        "source_finding_key": "ALWAYS_ON",
        "description": "Every future research runner must separate raw calendar months from canonical policy months.",
        "required_behavior": [
            "raw_calendar_month_count may be 13",
            "canonical_policy_month_count must be exactly 12",
            "release/stability calculations must use canonical 12 months only",
            "partial boundary months must be observation-only unless explicitly allowed by a later guard",
        ],
        "pass_condition": "canonical_policy_month_count == 12 and policy calculations exclude non-canonical boundary months",
        "blocks_candidate_or_release_if_failed": True,
    })

    requirements.append({
        "guard_key": "FULL_UNIVERSE_IDENTITY_GUARD",
        "severity": "MANDATORY",
        "source_finding_key": "ALWAYS_ON",
        "description": "Every future research runner must verify it is using the intended full-universe panel.",
        "required_behavior": [
            "report panel_path",
            "report symbol_count",
            "report row_count",
            "report raw_calendar_month_count",
            "report canonical_policy_month_count",
            "fail read-only if symbol_count or row_count materially differs from audited panel unless a new audit is run",
        ],
        "pass_condition": "symbol_count >= 0.90 * audited_symbol_count and canonical_policy_month_count == 12",
        "blocks_candidate_or_release_if_failed": True,
    })

    for finding in findings:
        severity = str(finding.get("severity", "")).upper()
        key = str(finding.get("finding_key", ""))
        message = finding.get("message")
        recommendation = finding.get("recommendation")

        if severity not in {"ATTENTION", "CRITICAL"}:
            continue

        if key == "RAW_13_WITH_PARTIAL_BOUNDARIES_DETECTED":
            requirements.append({
                "guard_key": "PARTIAL_BOUNDARY_MONTH_EXCLUSION_GUARD",
                "severity": "MANDATORY",
                "source_finding_key": key,
                "description": message,
                "required_behavior": [
                    "future runners must output raw_calendar_months",
                    "future runners must output canonical_policy_months",
                    "future runners must output excluded_policy_months",
                    "partial boundary months must not be used in strict release calculations",
                ],
                "pass_condition": "excluded_policy_months are not included in strict 12/12 policy metrics",
                "blocks_candidate_or_release_if_failed": True,
                "recommendation": recommendation,
            })

        elif key == "DUPLICATE_ROWS_PRESENT":
            requirements.append({
                "guard_key": "DUPLICATE_SYMBOL_TIME_GUARD",
                "severity": "MANDATORY",
                "source_finding_key": key,
                "description": message,
                "required_behavior": [
                    "future runners must report duplicate_full_row_count",
                    "future runners must report duplicate_symbol_time_count",
                    "candidate/release paths blocked if duplicate_symbol_time_count > 0 unless repaired or explicitly proven harmless",
                ],
                "pass_condition": "duplicate_symbol_time_count == 0 or audited_duplicate_exception_approved == True",
                "blocks_candidate_or_release_if_failed": True,
                "recommendation": recommendation,
            })

        elif key == "HIGH_COLUMN_MISSINGNESS":
            requirements.append({
                "guard_key": "HIGH_MISSINGNESS_FEATURE_USAGE_GUARD",
                "severity": "MANDATORY",
                "source_finding_key": key,
                "description": message,
                "required_behavior": [
                    "future runners must report feature columns used",
                    "future runners must check missingness of every used feature",
                    "features with >20% missingness must be blocked unless explicitly imputed and tagged diagnostic-only",
                ],
                "pass_condition": "no used feature has missing_ratio > 0.20 unless imputation_policy_approved == True",
                "blocks_candidate_or_release_if_failed": True,
                "recommendation": recommendation,
            })

        elif key == "INF_VALUES_PRESENT":
            requirements.append({
                "guard_key": "INF_VALUE_GUARD",
                "severity": "MANDATORY",
                "source_finding_key": key,
                "description": message,
                "required_behavior": [
                    "future runners must replace or block inf/-inf values before ranking/backtesting",
                    "future runners must report inf_count_by_used_column",
                ],
                "pass_condition": "inf_count_by_used_column == 0 after cleaning",
                "blocks_candidate_or_release_if_failed": True,
                "recommendation": recommendation,
            })

        elif key == "LARGE_TIMESTAMP_GAPS_PRESENT":
            requirements.append({
                "guard_key": "TIMESTAMP_GAP_GUARD",
                "severity": "MANDATORY",
                "source_finding_key": key,
                "description": message,
                "required_behavior": [
                    "future runners must report gap_gt_24h_count and gap_gt_3h_count for symbols used",
                    "features must not forward-fill across large gaps without a gap-aware reset",
                    "research previews must report whether results are gap-sensitive",
                ],
                "pass_condition": "gap-aware feature reset is applied or gap-sensitive symbols are excluded in a documented read-only way",
                "blocks_candidate_or_release_if_failed": True,
                "recommendation": recommendation,
            })

        elif key == "SYMBOL_LIFECYCLE_SHORT_COVERAGE_PRESENT":
            requirements.append({
                "guard_key": "SYMBOL_LIFECYCLE_COVERAGE_GUARD",
                "severity": "MANDATORY",
                "source_finding_key": key,
                "description": message,
                "required_behavior": [
                    "future runners must report active_month_count per symbol",
                    "future runners must be lifecycle-aware",
                    "strict month stability cannot be credited to symbols without sufficient lifecycle coverage unless explicitly segmented",
                ],
                "pass_condition": "symbol lifecycle handling is explicit and reported",
                "blocks_candidate_or_release_if_failed": True,
                "recommendation": recommendation,
            })

        elif key == "EXTREME_RETURN_OUTLIERS_PRESENT":
            requirements.append({
                "guard_key": "EXTREME_RETURN_OUTLIER_GUARD",
                "severity": "MANDATORY",
                "source_finding_key": key,
                "description": message,
                "required_behavior": [
                    "future runners must report extreme return outlier counts",
                    "research results must be recomputed with and without outlier rows if outliers intersect the signal set",
                ],
                "pass_condition": "outlier sensitivity does not change pass/fail conclusion",
                "blocks_candidate_or_release_if_failed": True,
                "recommendation": recommendation,
            })

        elif key == "CLOSE_OUTSIDE_HIGH_LOW":
            requirements.append({
                "guard_key": "OHLC_CONSISTENCY_GUARD",
                "severity": "MANDATORY",
                "source_finding_key": key,
                "description": message,
                "required_behavior": [
                    "future runners using high/low/MAE/MFE/range must verify OHLC consistency",
                    "exit/risk-shape previews blocked if close/high/low inconsistencies touch selected rows",
                ],
                "pass_condition": "selected rows have OHLC consistency pass",
                "blocks_candidate_or_release_if_failed": True,
                "recommendation": recommendation,
            })

        else:
            requirements.append({
                "guard_key": f"TRIAGE_{key or 'UNKNOWN_ATTENTION'}",
                "severity": "MANDATORY",
                "source_finding_key": key,
                "description": message,
                "required_behavior": [
                    "future research must not ignore this audit finding",
                    "triage must classify whether this finding affects feature construction, sample selection, or release metrics",
                ],
                "pass_condition": "finding_triaged == True",
                "blocks_candidate_or_release_if_failed": True,
                "recommendation": recommendation,
            })

    # De-duplicate by guard_key while preserving order.
    seen = set()
    deduped = []
    for req in requirements:
        g = req.get("guard_key")
        if g not in seen:
            seen.add(g)
            deduped.append(req)

    return deduped


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS DATA QUALITY GUARD CONTRACT BUILDER v1")
    lines.append("=" * 100)

    for k in [
        "builder_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "contract_id",
        "contract_hash",
        "research_key",
        "direction_queue_key",
        "strict_policy_key",
        "canonical_policy_month_count",
        "guard_requirement_count",
        "next_module",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("GUARD REQUIREMENTS")
    lines.append("-" * 100)
    for req in result.get("guard_requirements", []):
        lines.append(f"- {req.get('guard_key')} [{req.get('severity')}] from {req.get('source_finding_key')}")
        lines.append(f"  pass_condition: {req.get('pass_condition')}")

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        lines.append(f"{k}: {v}")

    lines.append("")
    lines.append("OUTPUT")
    lines.append("-" * 100)
    lines.append(f"contract_latest_path: {result.get('contract_latest_path')}")
    lines.append(f"summary_path: {result.get('summary_path')}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS DATA QUALITY GUARD CONTRACT BUILDER v1")
    print("=" * 100)
    print(f"builder_status: {result.get('builder_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"contract_id: {result.get('contract_id')}")
    print(f"contract_hash: {result.get('contract_hash')}")
    print(f"research_key: {result.get('research_key')}")
    print(f"direction_queue_key: {result.get('direction_queue_key')}")
    print(f"strict_policy_key: {result.get('strict_policy_key')}")
    print(f"canonical_policy_month_count: {result.get('canonical_policy_month_count')}")
    print(f"guard_requirement_count: {result.get('guard_requirement_count')}")
    print(f"next_module: {result.get('next_module')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('contract_latest_path')}")
    print(f"TXT : {result.get('summary_path')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    evaluator = load_json(SOURCE_EVALUATOR_JSON, default={})
    queue = load_json(SOURCE_QUEUE_JSON, default={})
    audit_runner = load_json(AUDIT_RUNNER_JSON, default={})
    findings = read_csv_rows(AUDIT_FINDINGS_CSV)

    top_direction = get_top_queue_direction(queue, evaluator)

    evaluator_status = evaluator.get("evaluator_status")
    audit_decision_class = evaluator.get("audit_decision_class")
    audit_research_blocked_until_guard = bool(evaluator.get("audit_research_blocked_until_guard"))
    release_allowed = bool(evaluator.get("release_allowed"))

    top_key = top_direction.get("research_key") or evaluator.get("next_recommended_research_key")
    top_module = top_direction.get("next_module_recommendation") or evaluator.get("next_module")
    queue_status = queue.get("queue_status")

    canonical_policy_month_count = int(evaluator.get("canonical_policy_month_count") or 12)
    if canonical_policy_month_count != 12:
        canonical_policy_month_count = 12

    prerequisite_pass = (
        evaluator_status == REQUIRED_EVALUATOR_STATUS
        and audit_decision_class in {
            "ATTENTION_DATA_QUALITY_GUARD_REQUIRED",
            "ATTENTION_UNKNOWN_FINDINGS_TRIAGE_REQUIRED",
            "GUARD_ONLY_ATTENTION_META_SYNTHESIS_ALLOWED_AFTER_GUARD",
        }
        and audit_research_blocked_until_guard is True
        and release_allowed is False
        and top_key == REQUIRED_DIRECTION_KEY
        and canonical_policy_month_count == 12
    )

    guard_requirements = guard_requirements_from_findings(findings, evaluator, audit_runner)

    seed = {
        "builder": "edge_factory_os_data_quality_guard_contract_builder_v1",
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "source_evaluator_status": evaluator_status,
        "audit_decision_class": audit_decision_class,
        "guard_requirement_keys": [x.get("guard_key") for x in guard_requirements],
    }

    contract_hash = stable_hash(seed)
    contract_id = f"DATA_QUALITY_GUARD_CONTRACT_V1_{contract_hash}_{timestamp_compact()}"

    if prerequisite_pass:
        builder_status = "DATA_QUALITY_GUARD_CONTRACT_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_DATA_QUALITY_GUARD_RUNNER"
        reason = (
            f"audit_decision_class={audit_decision_class}; "
            f"guard_requirement_count={len(guard_requirements)}; "
            "data_quality_guard_contract_ready=True"
        )
    else:
        builder_status = "DATA_QUALITY_GUARD_CONTRACT_BLOCKED_PREREQUISITE_NOT_MET"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_DATA_QUALITY_AUDIT_EVALUATOR_QUEUE_BEFORE_BUILDING_GUARD"
        reason = (
            f"evaluator_status={evaluator_status}; audit_decision_class={audit_decision_class}; "
            f"audit_research_blocked_until_guard={audit_research_blocked_until_guard}; "
            f"release_allowed={release_allowed}; queue_status={queue_status}; "
            f"top_key={top_key}; top_module={top_module}; "
            f"canonical_policy_month_count={canonical_policy_month_count}"
        )

    contract = {
        "builder_name": "edge_factory_os_data_quality_guard_contract_builder_v1",
        "created_at_utc": utc_now_iso(),
        "builder_status": builder_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "contract_id": contract_id if prerequisite_pass else None,
        "contract_hash": contract_hash,
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "audit_decision_class": audit_decision_class,
        "audit_research_blocked_until_guard": audit_research_blocked_until_guard,
        "source_audit_summary": {
            "runner_status": audit_runner.get("runner_status"),
            "finding_count": audit_runner.get("finding_count"),
            "critical_finding_count": audit_runner.get("critical_finding_count"),
            "attention_finding_count": audit_runner.get("attention_finding_count"),
            "raw_calendar_month_count": audit_runner.get("raw_calendar_month_count"),
            "canonical_policy_month_count": audit_runner.get("canonical_policy_month_count"),
            "symbol_count": audit_runner.get("symbol_count"),
            "row_count": audit_runner.get("row_count"),
            "partial_boundary_months": audit_runner.get("partial_boundary_months"),
            "excluded_policy_months": audit_runner.get("excluded_policy_months"),
            "duplicate_info": audit_runner.get("duplicate_info"),
            "column_quality_summary": audit_runner.get("column_quality_summary"),
            "symbol_coverage_summary": audit_runner.get("symbol_coverage_summary"),
            "gap_summary": audit_runner.get("gap_summary"),
            "outlier_summary": audit_runner.get("outlier_summary"),
        },
        "audit_findings": findings,
        "guard_requirement_count": len(guard_requirements),
        "guard_requirements": guard_requirements,
        "guard_policy": {
            "research_meta_synthesis_blocked_until_guard_runner_pass": True,
            "future_research_must_import_or_consume_guard": True,
            "guard_failure_blocks_candidate_generation": True,
            "guard_failure_blocks_candidate_contract": True,
            "guard_failure_blocks_family_release": True,
            "guard_failure_blocks_runtime_touch": True,
            "guard_failure_blocks_capital_change": True,
            "guard_failure_blocks_active_paper": True,
            "guard_failure_blocks_live": True,
            "guard_failure_blocks_real_orders": True,
            "strict_month_policy": STRICT_POLICY_KEY,
            "canonical_policy_month_count_required": 12,
        },
        "required_guard_runner_outputs": [
            "guard_status",
            "guard_pass",
            "guard_requirement_count",
            "guard_pass_count",
            "guard_fail_count",
            "guard_warning_count",
            "canonical_month_policy_pass",
            "panel_identity_guard_pass",
            "used_feature_quality_guard_pass",
            "timestamp_gap_guard_pass",
            "symbol_lifecycle_guard_pass",
            "outlier_guard_pass",
            "latest_json",
            "latest_txt",
            "guard_report_csv",
        ],
        "downstream_decision_rules": {
            "if_guard_runner_passes": "build research meta-synthesizer after audit, still no candidate/family/runtime/capital/live action",
            "if_guard_runner_fails": "build panel/data guard repair contract or block further research",
            "if_guard_runner_incomplete": "block research meta-synthesis",
        },
        "input_evaluator_json": str(SOURCE_EVALUATOR_JSON),
        "input_queue_json": str(SOURCE_QUEUE_JSON),
        "input_audit_runner_json": str(AUDIT_RUNNER_JSON),
        "input_audit_findings_csv": str(AUDIT_FINDINGS_CSV),
        "next_module": NEXT_MODULE if prerequisite_pass else None,
        "release_gate_feed": {
            "DATA_QUALITY_GUARD_CONTRACT_READY": prerequisite_pass,
            "STRICT_MONTH_STABILITY_12_OF_12": True,
            "RESEARCH_META_SYNTHESIS_ALLOWED_FROM_THIS_CONTRACT": False,
            "RELEASE_PASS_FROM_THIS_CONTRACT": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_THIS_CONTRACT": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_THIS_CONTRACT": False,
            "FAMILY_RELEASE_ALLOWED_FROM_THIS_CONTRACT": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_THIS_CONTRACT": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_THIS_CONTRACT": False,
            "ACTIVE_PAPER_ALLOWED_FROM_THIS_CONTRACT": False,
            "LIVE_ALLOWED_FROM_THIS_CONTRACT": False,
            "REAL_ORDERS_ALLOWED_FROM_THIS_CONTRACT": False,
        },
        "contract_latest_path": str(OUT_JSON),
        "summary_path": str(OUT_TXT),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, contract)
    write_text_summary(OUT_TXT, contract)
    print_summary(contract)

    return 0 if prerequisite_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
