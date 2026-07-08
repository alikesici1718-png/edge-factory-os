#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Symbol Cluster Segment Contract Builder v1

Purpose:
- Consume Exit Risk Shape Deep Validation Evaluator v1 output.
- Build a read-only/offline research contract for:
  RD4_04_SYMBOL_CLUSTER_AND_MICROSTRUCTURE_SEGMENT_SEARCH.
- This is not candidate generation.
- This is not family release.
- This is not runtime/capital/live action.
- Goal: test whether repeated strict failures are caused by using the whole universe
  instead of stable pre-outcome symbol/microstructure segments.

This builder does NOT:
- run symbol segmentation
- create candidates
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

SOURCE_EVALUATOR_JSON = (
    BASE_DIR
    / "edge_factory_os_exit_risk_shape_deep_validation_evaluator"
    / "exit_risk_shape_deep_validation_evaluator_latest.json"
)

SOURCE_QUEUE_JSON = (
    BASE_DIR
    / "edge_factory_os_exit_risk_shape_deep_validation_evaluator"
    / "exit_risk_shape_next_research_queue_latest.json"
)

OUT_DIR = BASE_DIR / "edge_factory_os_research_direction_contracts"
OUT_JSON = OUT_DIR / "symbol_cluster_segment_contract_latest.json"
OUT_TXT = OUT_DIR / "symbol_cluster_segment_contract_latest.txt"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

REQUIRED_EVALUATOR_STATUS = "EXIT_RISK_SHAPE_DEEP_VALIDATION_EVALUATOR_ROUTE_CLOSED"
REQUIRED_DIRECTION_KEY = "RD4_04_SYMBOL_CLUSTER_AND_MICROSTRUCTURE_SEGMENT_SEARCH"

RESEARCH_KEY = "SYMBOL_CLUSTER_AND_MICROSTRUCTURE_SEGMENT_SEARCH_V1"
DIRECTION_QUEUE_KEY = "RD4_04_SYMBOL_CLUSTER_AND_MICROSTRUCTURE_SEGMENT_SEARCH"
NEXT_MODULE = "edge_factory_os_symbol_cluster_segment_runner_v1.py"

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
    lines.append("EDGE FACTORY OS SYMBOL CLUSTER SEGMENT CONTRACT BUILDER v1")
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
    lines.append("SYMBOL/MICROSTRUCTURE SEGMENT DESIGN")
    lines.append("-" * 100)
    design = result.get("symbol_cluster_segment_contract", {})
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
    print("EDGE FACTORY OS SYMBOL CLUSTER SEGMENT CONTRACT BUILDER v1")
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
    preview_failed_deep_validation = bool(evaluator.get("preview_failed_deep_validation"))
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
        and preview_failed_deep_validation is True
        and release_allowed is False
        and top_key == REQUIRED_DIRECTION_KEY
        and canonical_policy_month_count == 12
    )

    seed = {
        "builder": "edge_factory_os_symbol_cluster_segment_contract_builder_v1",
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
    contract_id = f"SYMBOL_CLUSTER_SEGMENT_CONTRACT_V1_{contract_hash}_{timestamp_compact()}"

    if prerequisite_pass:
        builder_status = "SYMBOL_CLUSTER_SEGMENT_CONTRACT_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_SYMBOL_CLUSTER_SEGMENT_RUNNER"
        reason = (
            f"exit_risk_deep_validation_route_closed=True; top_key={top_key}; "
            "building symbol/microstructure segment research contract"
        )
    else:
        builder_status = "SYMBOL_CLUSTER_SEGMENT_CONTRACT_BLOCKED_PREREQUISITE_NOT_MET"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_EXIT_RISK_DEEP_VALIDATION_EVALUATOR_QUEUE_BEFORE_BUILDING_SYMBOL_SEGMENT_CONTRACT"
        reason = (
            f"evaluator_status={evaluator_status}; branch_closed={branch_closed}; "
            f"preview_failed_deep_validation={preview_failed_deep_validation}; release_allowed={release_allowed}; "
            f"queue_status={queue_status}; top_key={top_key}; top_module={top_module}; "
            f"canonical_policy_month_count={canonical_policy_month_count}"
        )

    contract_principles = [
        "This is symbol/microstructure segmentation research, not candidate generation.",
        "Use full 1Y 285-symbol OKX swap panel if available.",
        "Segments must be defined only from pre-outcome symbol and microstructure features.",
        "No manual symbol whitelist.",
        "No manual month blacklist.",
        "No post-outcome selected cluster release.",
        "No family release from a segment preview.",
        "No active paper/live/capital action from this contract.",
        "STRICT_MONTH_STABILITY_12_OF_12 remains mandatory for any future release chain.",
        "If a segment preview appears, it still requires full replay, OOS/rolling, cost/slippage, concentration, risk and release gates.",
    ]

    contract = {
        "builder_name": "edge_factory_os_symbol_cluster_segment_contract_builder_v1",
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
        "research_title": "Symbol cluster and microstructure segment search",
        "research_question": (
            "After broad-universe entry, regime, motif, and exit/risk-shape routes failed strict validation, "
            "does any stable edge structure exist only inside pre-outcome symbol/microstructure segments "
            "such as liquidity tier, volatility/range tier, trend behavior, dispersion behavior, or listing-style behavior?"
        ),
        "why_now": {
            "source_evaluator_status": evaluator_status,
            "source_branch_closed": branch_closed,
            "source_preview_failed_deep_validation": preview_failed_deep_validation,
            "source_deep_validation_pass_count": evaluator.get("deep_validation_pass_count"),
            "source_validation_result_count": evaluator.get("validation_result_count"),
            "source_lesson_id": evaluator.get("lesson_id"),
            "summary": (
                "All broad entry/archetype/regime/motif attempts failed, and exit/risk-shape strict previews failed deep validation. "
                "The next plausible axis is that edge, if any, is segment-specific and hidden by full-universe averaging."
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
        "symbol_cluster_segment_contract": {
            "segment_level": [
                "symbol_static_profile",
                "symbol_rolling_profile",
                "symbol_x_market_microstructure_profile",
                "pre_outcome_symbol_cluster",
            ],
            "allowed_segment_features_pre_outcome_only": [
                "median_liquidity_proxy",
                "liquidity_rank_stability",
                "median_range_bps",
                "range_rank_stability",
                "realized_volatility_profile",
                "trend_persistence_profile",
                "mean_reversion_profile",
                "cross_sectional_rank_persistence",
                "market_beta_proxy",
                "dispersion_sensitivity",
                "gap_or_jump_proxy_from_past_returns",
                "coverage_count_and_missingness",
            ],
            "forbidden_segment_inputs": [
                "future_return",
                "future_pnl",
                "future_win_loss",
                "month_outcome_label",
                "manual_symbol_whitelist",
                "manual_month_blacklist",
                "post_outcome_selected_symbols",
                "release_based_on_segment_preview_only",
            ],
            "segment_methods_allowed": [
                "pre_outcome_quantile_buckets",
                "symbol_profile_kmeans_or_fallback_quantile_cluster",
                "liquidity_x_volatility_cross_segments",
                "range_x_trend_persistence_segments",
                "beta_x_dispersion_sensitivity_segments",
            ],
            "diagnostic_reference_tests_allowed_after_segment_definition": [
                "replay prior frozen reference events inside each segment",
                "test simple neutral pre-outcome event references inside each segment",
                "test segment-conditioned month stability previews",
                "test segment concentration and sample size",
                "test whether segment improves or just overfits",
            ],
            "required_runner_outputs": [
                "symbol_profile_table",
                "segment_membership_table",
                "segment_diagnostic_table",
                "segment_month_stability_table",
                "segment_concentration_table",
                "strict_12_segment_preview_count",
                "ranked_segment_report_csv",
                "latest_json",
            ],
            "required_evaluator_outputs_later": [
                "close branch if strict_12_segment_preview_count == 0",
                "if preview exists, require deep validation before any release path",
                "record lesson/blocklist for failed segment route",
                "route to data quality/panel bias audit if segment search fails",
            ],
        },
        "panel_candidates": infer_panel_candidates(),
        "input_source_evaluator_path": str(SOURCE_EVALUATOR_JSON),
        "input_source_queue_path": str(SOURCE_QUEUE_JSON),
        "source_exit_risk_deep_validation_evaluator": {
            "evaluator_status": evaluator_status,
            "branch_closed": branch_closed,
            "preview_failed_deep_validation": preview_failed_deep_validation,
            "route_hash": evaluator.get("route_hash"),
            "lesson_id": evaluator.get("lesson_id"),
            "preview_count": evaluator.get("preview_count"),
            "validation_result_count": evaluator.get("validation_result_count"),
            "deep_validation_pass_count": evaluator.get("deep_validation_pass_count"),
            "next_recommended_research_key": evaluator.get("next_recommended_research_key"),
            "next_module": evaluator.get("next_module"),
        },
        "next_module": NEXT_MODULE if prerequisite_pass else None,
        "release_gate_feed": {
            "SYMBOL_CLUSTER_SEGMENT_CONTRACT_READY": prerequisite_pass,
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
