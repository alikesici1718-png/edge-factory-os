#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Data Quality Panel Bias Audit Contract Builder v1

Purpose:
- Consume Symbol Cluster Segment Evaluator v1 output.
- Build a read-only/offline research contract for:
  RD4_05_DATA_QUALITY_AND_PANEL_BIAS_AUDIT.
- This is not strategy search.
- This is not candidate generation.
- This is not family release.
- This is not runtime/capital/live action.

Why:
- Multiple materially different research routes failed STRICT_MONTH_STABILITY_12_OF_12.
- Before continuing edge discovery, audit whether the full panel, canonical month logic,
  symbol coverage, missingness, survivorship, feature construction, cost assumptions,
  or calendar boundary handling are limiting or distorting results.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

SOURCE_EVALUATOR_JSON = (
    BASE_DIR
    / "edge_factory_os_symbol_cluster_segment_evaluator"
    / "symbol_cluster_segment_evaluator_latest.json"
)

SOURCE_QUEUE_JSON = (
    BASE_DIR
    / "edge_factory_os_symbol_cluster_segment_evaluator"
    / "symbol_cluster_segment_next_research_queue_latest.json"
)

OUT_DIR = BASE_DIR / "edge_factory_os_research_direction_contracts"
OUT_JSON = OUT_DIR / "data_quality_panel_bias_audit_contract_latest.json"
OUT_TXT = OUT_DIR / "data_quality_panel_bias_audit_contract_latest.txt"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

REQUIRED_EVALUATOR_STATUS = "SYMBOL_CLUSTER_SEGMENT_EVALUATOR_BRANCH_CLOSED"
REQUIRED_DIRECTION_KEY = "RD4_05_DATA_QUALITY_AND_PANEL_BIAS_AUDIT"

RESEARCH_KEY = "DATA_QUALITY_AND_PANEL_BIAS_AUDIT_V1"
DIRECTION_QUEUE_KEY = "RD4_05_DATA_QUALITY_AND_PANEL_BIAS_AUDIT"
NEXT_MODULE = "edge_factory_os_data_quality_panel_bias_audit_runner_v1.py"

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


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    tmp.replace(path)


def stable_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def infer_panel_candidates() -> List[str]:
    candidates: List[str] = []

    known = [
        BASE_DIR
        / "edge_factory_feature_panels"
        / "post_impulse_drift_long_v1"
        / "post_impulse_drift_long_v1_feature_panel_1h_dynamic.parquet",
    ]

    for p in known:
        if p.exists():
            candidates.append(str(p))

    if candidates:
        return candidates

    roots = [
        BASE_DIR / "edge_factory_feature_panels",
        BASE_DIR / "edge_factory_os_universe",
        BASE_DIR / "edge_factory_universe",
        BASE_DIR,
    ]

    patterns = [
        "**/*feature_panel*.parquet",
        "**/*okx*swap*.parquet",
        "**/*285*.parquet",
        "**/*full*panel*.parquet",
        "**/*panel*.parquet",
    ]

    found: List[Path] = []

    for root in roots:
        if not root.exists():
            continue
        for pattern in patterns:
            try:
                for p in root.glob(pattern):
                    if p.is_file() and p.suffix.lower() == ".parquet":
                        found.append(p)
            except Exception:
                pass

    def score(path: Path) -> int:
        s = str(path).lower()
        value = 0
        for token, weight in [
            ("okx", 20),
            ("swap", 20),
            ("285", 15),
            ("1y", 15),
            ("feature_panel", 12),
            ("dynamic", 8),
            ("full", 8),
            ("panel", 8),
            ("universe", 6),
        ]:
            if token in s:
                value += weight
        try:
            value += min(int(path.stat().st_size / 100_000_000), 25)
        except Exception:
            pass
        return value

    found = sorted(set(found), key=score, reverse=True)
    return [str(p) for p in found[:5]]


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


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS DATA QUALITY PANEL BIAS AUDIT CONTRACT BUILDER v1")
    lines.append("=" * 100)

    for k in [
        "builder_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "contract_id",
        "research_key",
        "direction_queue_key",
        "contract_hash",
        "strict_policy_key",
        "canonical_policy_month_count",
        "next_module",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("AUDIT PRINCIPLES")
    lines.append("-" * 100)
    for item in result.get("audit_principles", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("AUDIT CONTRACT")
    lines.append("-" * 100)
    audit = result.get("data_quality_panel_bias_audit_contract", {})
    for k, v in audit.items():
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f"  - {item}")
        elif isinstance(v, dict):
            lines.append(f"{k}:")
            for kk, vv in v.items():
                lines.append(f"  {kk}: {vv}")
        else:
            lines.append(f"{k}: {v}")

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
    print("EDGE FACTORY OS DATA QUALITY PANEL BIAS AUDIT CONTRACT BUILDER v1")
    print("=" * 100)
    print(f"builder_status: {result.get('builder_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"contract_id: {result.get('contract_id')}")
    print(f"research_key: {result.get('research_key')}")
    print(f"direction_queue_key: {result.get('direction_queue_key')}")
    print(f"contract_hash: {result.get('contract_hash')}")
    print(f"strict_policy_key: {result.get('strict_policy_key')}")
    print(f"canonical_policy_month_count: {result.get('canonical_policy_month_count')}")
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
    top_direction = get_top_queue_direction(queue, evaluator)

    evaluator_status = evaluator.get("evaluator_status")
    branch_closed = bool(evaluator.get("branch_closed"))
    release_allowed = bool(evaluator.get("release_allowed"))

    top_key = top_direction.get("research_key") or evaluator.get("next_recommended_research_key")
    top_module = top_direction.get("next_module_recommendation") or evaluator.get("next_module")
    queue_status = queue.get("queue_status")

    canonical_policy_month_count = int(evaluator.get("canonical_policy_month_count") or 12)
    if canonical_policy_month_count != 12:
        canonical_policy_month_count = 12

    prerequisite_pass = (
        evaluator_status == REQUIRED_EVALUATOR_STATUS
        and branch_closed is True
        and release_allowed is False
        and top_key == REQUIRED_DIRECTION_KEY
        and canonical_policy_month_count == 12
    )

    seed = {
        "builder": "edge_factory_os_data_quality_panel_bias_audit_contract_builder_v1",
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "source_evaluator_status": evaluator_status,
        "source_route_hash": evaluator.get("route_hash"),
        "source_lesson_id": evaluator.get("lesson_id"),
        "top_key": top_key,
    }

    contract_hash = stable_hash(seed)
    contract_id = f"DATA_QUALITY_PANEL_BIAS_AUDIT_CONTRACT_V1_{contract_hash}_{timestamp_compact()}"

    if prerequisite_pass:
        builder_status = "DATA_QUALITY_PANEL_BIAS_AUDIT_CONTRACT_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_DATA_QUALITY_PANEL_BIAS_AUDIT_RUNNER"
        reason = (
            f"symbol_cluster_segment_branch_closed=True; top_key={top_key}; "
            "building data quality and panel bias audit contract"
        )
    else:
        builder_status = "DATA_QUALITY_PANEL_BIAS_AUDIT_CONTRACT_BLOCKED_PREREQUISITE_NOT_MET"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_SYMBOL_CLUSTER_SEGMENT_EVALUATOR_QUEUE_BEFORE_BUILDING_DATA_AUDIT_CONTRACT"
        reason = (
            f"evaluator_status={evaluator_status}; branch_closed={branch_closed}; "
            f"release_allowed={release_allowed}; queue_status={queue_status}; "
            f"top_key={top_key}; top_module={top_module}; "
            f"canonical_policy_month_count={canonical_policy_month_count}"
        )

    audit_principles = [
        "This is a data/panel audit, not strategy discovery.",
        "No candidate generation from audit output.",
        "No family release from audit output.",
        "No runtime, launcher, patch_runtime, active paper, capital, live, or real-order action.",
        "Audit full available 1Y OKX swap panel if available.",
        "Canonical month logic must distinguish raw calendar buckets from policy months.",
        "Raw 13 calendar buckets can exist; release policy remains canonical 12 months.",
        "Detect survivorship, symbol lifecycle, missingness, duplicate rows, gap patterns, partial boundary leakage, and feature construction bias.",
        "Any future research direction must consume audit findings before reopening blocked routes.",
    ]

    contract = {
        "builder_name": "edge_factory_os_data_quality_panel_bias_audit_contract_builder_v1",
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
        "research_title": "Data quality and panel bias audit",
        "research_question": (
            "After multiple materially different research routes failed strict 12-of-12 month stability, "
            "is the search being limited or distorted by panel coverage, symbol lifecycle, survivorship, missingness, "
            "calendar boundary leakage, duplicate rows, stale symbols, cost assumptions, or feature construction bias?"
        ),
        "why_now": {
            "source_evaluator_status": evaluator_status,
            "source_branch_closed": branch_closed,
            "source_segment_diagnostic_row_count": evaluator.get("segment_diagnostic_row_count"),
            "source_strict_12_segment_preview_count": evaluator.get("strict_12_segment_preview_count"),
            "source_lesson_id": evaluator.get("lesson_id"),
            "summary": (
                "Broad entry/archetype, regime-first, label-free motif, exit/risk-shape, and symbol-segment routes "
                "failed strict 12/12. The OS should audit the panel before further edge search."
            ),
        },
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "canonical_month_policy": {
            "required_canonical_month_count": 12,
            "positive_months_required": 12,
            "negative_months_allowed": 0,
            "raw_13_calendar_buckets_allowed_for_observation_only": True,
            "release_requires_canonical_12_of_12": True,
            "audit_must_report_raw_vs_canonical_months": True,
            "audit_must_detect_partial_boundary_month_leak": True,
        },
        "audit_principles": audit_principles,
        "data_quality_panel_bias_audit_contract": {
            "audit_categories": [
                "panel_identity_and_coverage",
                "raw_calendar_vs_canonical_month_window",
                "symbol_lifecycle_and_survivorship",
                "missingness_and_gap_patterns",
                "duplicate_and_timestamp_integrity",
                "feature_column_availability_and_nan_inf",
                "liquidity_volume_quality",
                "range_high_low_quality",
                "return_distribution_outliers",
                "cost_slippage_assumption_review",
                "train_oos_calendar_split_sanity",
                "universe_guard_consistency",
                "blocked_route_failure_meta_analysis",
            ],
            "required_audit_outputs": [
                "panel_path",
                "row_count",
                "symbol_count",
                "raw_calendar_month_count",
                "canonical_policy_month_count",
                "canonical_months",
                "partial_boundary_months",
                "duplicate_row_count",
                "timestamp_gap_summary",
                "symbol_lifecycle_summary",
                "missingness_by_column",
                "nan_inf_by_column",
                "outlier_summary",
                "coverage_by_month",
                "coverage_by_symbol",
                "universe_guard_consistency",
                "audit_findings",
                "audit_recommendations",
                "latest_json",
                "latest_txt",
                "csv_outputs",
            ],
            "hard_attention_conditions": [
                "canonical_policy_month_count_not_12",
                "raw_calendar_month_count_less_than_12",
                "duplicate_rows_present",
                "missing_required_columns",
                "inf_values_present",
                "large_unexplained_gaps",
                "symbol_count_far_below_expected_285",
                "partial_boundary_month_used_as_policy_month",
                "feature_panel_path_not_full_universe",
            ],
            "allowed_runner_outputs": [
                "read_only_audit_pass",
                "read_only_audit_attention",
                "read_only_audit_blocked",
            ],
            "forbidden_outputs": [
                "candidate_generation",
                "candidate_contract",
                "family_release",
                "promotion",
                "runtime_touch",
                "capital_change",
                "active_paper",
                "live",
                "real_orders",
            ],
            "downstream_decision_rules": {
                "if_audit_finds_material_panel_issue": "build panel repair or data correction contract, no strategy search",
                "if_audit_passes_cleanly": "build research meta-synthesizer or new evidence generation queue",
                "if_audit_incomplete": "block further research until audit is complete",
            },
        },
        "panel_candidates": infer_panel_candidates(),
        "input_source_evaluator_path": str(SOURCE_EVALUATOR_JSON),
        "input_source_queue_path": str(SOURCE_QUEUE_JSON),
        "source_symbol_cluster_segment_evaluator": {
            "evaluator_status": evaluator_status,
            "branch_closed": branch_closed,
            "route_hash": evaluator.get("route_hash"),
            "lesson_id": evaluator.get("lesson_id"),
            "symbol_count": evaluator.get("symbol_count"),
            "row_count": evaluator.get("row_count"),
            "segment_membership_count": evaluator.get("segment_membership_count"),
            "segment_diagnostic_row_count": evaluator.get("segment_diagnostic_row_count"),
            "strict_12_segment_preview_count": evaluator.get("strict_12_segment_preview_count"),
            "next_recommended_research_key": evaluator.get("next_recommended_research_key"),
            "next_module": evaluator.get("next_module"),
        },
        "next_module": NEXT_MODULE if prerequisite_pass else None,
        "release_gate_feed": {
            "DATA_QUALITY_PANEL_BIAS_AUDIT_CONTRACT_READY": prerequisite_pass,
            "STRICT_MONTH_STABILITY_12_OF_12": True,
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
