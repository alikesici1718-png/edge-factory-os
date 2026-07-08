#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Exit Risk Shape Contract Builder v1

Purpose:
- Consume Label-Free Event Motif Evaluator v1 output.
- Build a read-only/offline research contract for:
  RD4_03_EXIT_AND_RISK_SHAPE_SEARCH_INSTEAD_OF_ENTRY_SEARCH.
- This is not another entry/archetype/motif search.
- The goal is to inspect whether exit logic, hold decay, adverse excursion,
  favorable excursion, time stop, volatility stop, and risk-shape explain why
  previous entry/motif/regime branches fail STRICT_MONTH_STABILITY_12_OF_12.

This builder does NOT:
- run exit/risk-shape diagnostics
- generate candidates
- release families
- touch runtime
- change capital
- start active paper
- enable live
- place real orders
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

MOTIF_EVALUATOR_JSON = (
    BASE_DIR
    / "edge_factory_os_label_free_event_motif_evaluator"
    / "label_free_event_motif_evaluator_latest.json"
)

MOTIF_NEXT_QUEUE_JSON = (
    BASE_DIR
    / "edge_factory_os_label_free_event_motif_evaluator"
    / "label_free_event_motif_next_research_queue_latest.json"
)

OUT_DIR = BASE_DIR / "edge_factory_os_research_direction_contracts"
OUT_JSON = OUT_DIR / "exit_risk_shape_contract_latest.json"
OUT_TXT = OUT_DIR / "exit_risk_shape_contract_latest.txt"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

REQUIRED_EVALUATOR_STATUS = "LABEL_FREE_EVENT_MOTIF_EVALUATOR_BRANCH_CLOSED"
REQUIRED_DIRECTION_KEY = "RD4_03_EXIT_AND_RISK_SHAPE_SEARCH_INSTEAD_OF_ENTRY_SEARCH"

RESEARCH_KEY = "EXIT_AND_RISK_SHAPE_SEARCH_V1"
DIRECTION_QUEUE_KEY = "RD4_03_EXIT_AND_RISK_SHAPE_SEARCH_INSTEAD_OF_ENTRY_SEARCH"
NEXT_MODULE = "edge_factory_os_exit_risk_shape_runner_v1.py"

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
    lines.append("EDGE FACTORY OS EXIT RISK SHAPE CONTRACT BUILDER v1")
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
    lines.append("CONTRACT PRINCIPLES")
    lines.append("-" * 100)
    for item in result.get("contract_principles", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("EXIT/RISK SHAPE DESIGN")
    lines.append("-" * 100)
    design = result.get("exit_risk_shape_contract", {})
    for k, v in design.items():
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f"  - {item}")
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
    print("EDGE FACTORY OS EXIT RISK SHAPE CONTRACT BUILDER v1")
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

    evaluator = load_json(MOTIF_EVALUATOR_JSON, default={})
    queue = load_json(MOTIF_NEXT_QUEUE_JSON, default={})
    top_direction = get_top_queue_direction(queue, evaluator)

    evaluator_status = evaluator.get("evaluator_status")
    branch_closed = bool(evaluator.get("branch_closed"))
    top_key = top_direction.get("research_key") or evaluator.get("next_recommended_research_key")
    top_module = top_direction.get("next_module_recommendation") or evaluator.get("next_module")
    queue_status = queue.get("queue_status")

    canonical_policy_month_count = int(evaluator.get("canonical_policy_month_count") or 12)
    if canonical_policy_month_count != 12:
        canonical_policy_month_count = 12

    prerequisite_pass = (
        evaluator_status == REQUIRED_EVALUATOR_STATUS
        and branch_closed is True
        and top_key == REQUIRED_DIRECTION_KEY
        and canonical_policy_month_count == 12
    )

    seed = {
        "builder": "edge_factory_os_exit_risk_shape_contract_builder_v1",
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
    contract_id = f"EXIT_RISK_SHAPE_CONTRACT_V1_{contract_hash}_{timestamp_compact()}"

    if prerequisite_pass:
        builder_status = "EXIT_RISK_SHAPE_CONTRACT_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_EXIT_RISK_SHAPE_RUNNER"
        reason = (
            f"label_free_event_motif_branch_closed=True; top_key={top_key}; "
            "building exit/risk-shape research contract"
        )
    else:
        builder_status = "EXIT_RISK_SHAPE_CONTRACT_BLOCKED_PREREQUISITE_NOT_MET"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_LABEL_FREE_EVENT_MOTIF_EVALUATOR_QUEUE_BEFORE_BUILDING_EXIT_RISK_CONTRACT"
        reason = (
            f"evaluator_status={evaluator_status}; branch_closed={branch_closed}; "
            f"queue_status={queue_status}; top_key={top_key}; top_module={top_module}; "
            f"canonical_policy_month_count={canonical_policy_month_count}"
        )

    contract_principles = [
        "This is exit/risk-shape research, not a new entry-signal search.",
        "Use full 1Y 285-symbol OKX swap panel if available.",
        "Entry trigger families are diagnostic references only, not release candidates.",
        "Measure hold decay, MAE, MFE, time stop, volatility stop, and adverse/favorable path shape.",
        "Do not select exits using future labels before defining the diagnostic grid.",
        "No manual month blacklist.",
        "No manual symbol cherry-picking.",
        "No candidate generation from exit/risk preview.",
        "No family release from exit/risk preview.",
        "STRICT_MONTH_STABILITY_12_OF_12 remains mandatory for any future release chain.",
    ]

    contract = {
        "builder_name": "edge_factory_os_exit_risk_shape_contract_builder_v1",
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
        "research_title": "Exit and risk-shape search instead of entry search",
        "research_question": (
            "After repeated entry/archetype/regime/motif failures under strict 12-of-12 month stability, "
            "does the instability come from exit shape, hold decay, adverse excursion, favorable excursion, "
            "time stop, volatility stop, or risk-path behavior rather than entry discovery?"
        ),
        "why_now": {
            "source_evaluator_status": evaluator_status,
            "source_branch_closed": branch_closed,
            "source_motif_count": evaluator.get("motif_count"),
            "source_ranked_motif_row_count": evaluator.get("ranked_motif_row_count"),
            "source_strict_12_motif_preview_count": evaluator.get("strict_12_motif_preview_count"),
            "source_lesson_id": evaluator.get("lesson_id"),
            "summary": (
                "Hand-designed entries, regime-first clustering, and label-free motifs failed strict 12/12. "
                "The OS should inspect whether the issue is not entry discovery but exit/risk geometry."
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
        },
        "contract_principles": contract_principles,
        "exit_risk_shape_contract": {
            "diagnostic_level": [
                "path_shape_after_predefined_entry_reference",
                "hold_decay_surface",
                "mae_mfe_surface",
                "time_stop_surface",
                "volatility_stop_surface",
                "drawdown_recovery_profile",
                "month_stability_by_exit_shape",
            ],
            "allowed_reference_entries": [
                "top historical diagnostic routes from blocked branches",
                "simple pre-outcome neutral event references",
                "broad market state references",
                "label-free motif references only as frozen historical diagnostic groups",
            ],
            "forbidden_actions": [
                "candidate_generation",
                "family_release",
                "runtime_patch",
                "capital_change",
                "active_paper_start",
                "live_trading",
                "real_orders",
                "manual_month_blacklist",
                "manual_symbol_whitelist",
            ],
            "exit_dimensions_to_scan": [
                "hold_1h",
                "hold_3h",
                "hold_6h",
                "hold_12h",
                "hold_24h",
                "time_decay_exit",
                "mfe_take_profit_surface",
                "mae_stop_surface",
                "volatility_scaled_stop_surface",
                "range_scaled_stop_surface",
                "breakeven_after_mfe_threshold",
                "adverse_excursion_filter",
                "favorable_excursion_capture",
            ],
            "path_metrics_required": [
                "entry_to_exit_return",
                "max_adverse_excursion_bps",
                "max_favorable_excursion_bps",
                "time_to_mfe",
                "time_to_mae",
                "return_by_hold_hour",
                "month_sum_by_exit_shape",
                "positive_month_count",
                "worst_month_bps",
                "symbol_concentration",
            ],
            "runner_requirements": [
                "must use full available panel",
                "must not touch runtime",
                "must not create candidate",
                "must output ranked exit_shape diagnostics",
                "must report strict_12_exit_shape_preview_count",
                "must report concentration and sample size",
                "must write latest json and csv outputs",
            ],
            "evaluator_requirements_later": [
                "close branch if strict_12_exit_shape_preview_count == 0",
                "if preview exists, still require OOS/rolling/cost/concentration/release gates",
                "no release from exit preview alone",
            ],
        },
        "panel_candidates": infer_panel_candidates(),
        "input_motif_evaluator_path": str(MOTIF_EVALUATOR_JSON),
        "input_motif_queue_path": str(MOTIF_NEXT_QUEUE_JSON),
        "source_label_free_event_motif_evaluator": {
            "evaluator_status": evaluator_status,
            "branch_closed": branch_closed,
            "route_hash": evaluator.get("route_hash"),
            "lesson_id": evaluator.get("lesson_id"),
            "motif_count": evaluator.get("motif_count"),
            "ranked_motif_row_count": evaluator.get("ranked_motif_row_count"),
            "strict_12_motif_preview_count": evaluator.get("strict_12_motif_preview_count"),
            "next_recommended_research_key": evaluator.get("next_recommended_research_key"),
            "next_module": evaluator.get("next_module"),
        },
        "next_module": NEXT_MODULE if prerequisite_pass else None,
        "release_gate_feed": {
            "EXIT_RISK_SHAPE_CONTRACT_READY": prerequisite_pass,
            "STRICT_MONTH_STABILITY_12_OF_12": True,
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
