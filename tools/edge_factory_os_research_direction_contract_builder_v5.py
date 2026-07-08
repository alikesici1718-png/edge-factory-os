#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Research Direction Contract Builder v5

Builds the next RD3 research contract after market-neutral relative value branch closure.

Input prerequisite:
- Market Neutral Relative Value Archetype Evaluator v1 must have:
  evaluator_status = MARKET_NEUTRAL_RELATIVE_VALUE_ARCHETYPE_EVALUATOR_BRANCH_CLOSED
  branch_closed = True
  next_recommended_research_key = RD3_03_CALM_MARKET_LOW_VOL_CONTINUATION_ARCHETYPE_SEARCH

Output:
- calm_market_low_vol_continuation_archetype_contract_latest.json

Safety:
- read-only research only
- no candidate generation
- no candidate contract release
- no family release
- no runtime touch
- no capital change
- no active paper
- no live
- no real orders
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

INPUT_EVALUATOR_JSON = (
    BASE_DIR
    / "edge_factory_os_market_neutral_relative_value_archetype_evaluator"
    / "market_neutral_relative_value_archetype_evaluator_latest.json"
)

OUT_DIR = BASE_DIR / "edge_factory_os_research_direction_contracts"
OUT_JSON = OUT_DIR / "calm_market_low_vol_continuation_archetype_contract_latest.json"
OUT_TXT = OUT_DIR / "calm_market_low_vol_continuation_archetype_contract_latest.txt"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

REQUIRED_PREVIOUS_STATUS = "MARKET_NEUTRAL_RELATIVE_VALUE_ARCHETYPE_EVALUATOR_BRANCH_CLOSED"
REQUIRED_RESEARCH_KEY = "RD3_03_CALM_MARKET_LOW_VOL_CONTINUATION_ARCHETYPE_SEARCH"

RESEARCH_KEY = "CALM_MARKET_LOW_VOL_CONTINUATION_ARCHETYPE_SEARCH_V1"
DIRECTION_QUEUE_KEY = "RD3_03_CALM_MARKET_LOW_VOL_CONTINUATION_ARCHETYPE_SEARCH"
NEXT_MODULE = "edge_factory_os_calm_market_low_vol_continuation_archetype_runner_v1.py"

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


def infer_panel_candidates() -> List[str]:
    """
    Contract builder does not run research. It only records likely full-universe panel candidates
    for the next runner. The next runner must still validate universe coverage before using any panel.
    """
    candidates: List[str] = []

    known = [
        BASE_DIR
        / "edge_factory_feature_panels"
        / "post_impulse_drift_long_v1"
        / "post_impulse_drift_long_v1_feature_panel_1h_dynamic.parquet",
        BASE_DIR
        / "edge_factory_feature_panels"
        / "market_panic_rebound_long_v1"
        / "market_panic_rebound_long_v1_feature_panel_1h.parquet",
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
        "**/*panel*.parquet",
        "**/*okx*swap*.parquet",
        "**/*universe*.parquet",
    ]

    found = []
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
        score_value = 0
        for token, weight in [
            ("okx", 20),
            ("swap", 20),
            ("285", 15),
            ("1y", 15),
            ("feature_panel", 12),
            ("dynamic", 8),
            ("panel", 8),
            ("full", 6),
            ("universe", 5),
        ]:
            if token in s:
                score_value += weight
        try:
            score_value += min(int(path.stat().st_size / 100_000_000), 20)
        except Exception:
            pass
        return score_value

    found = sorted(set(found), key=score, reverse=True)
    return [str(p) for p in found[:5]]


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS RESEARCH DIRECTION CONTRACT BUILDER v5")
    lines.append("=" * 100)

    keys = [
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
    ]

    for k in keys:
        lines.append(f"{k}: {result.get(k)}")

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
    print("EDGE FACTORY OS RESEARCH DIRECTION CONTRACT BUILDER v5")
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

    evaluator = load_json(INPUT_EVALUATOR_JSON, default={})

    previous_status = evaluator.get("evaluator_status")
    previous_branch_closed = bool(evaluator.get("branch_closed"))
    previous_next_key = evaluator.get("next_recommended_research_key")

    prerequisite_pass = (
        previous_status == REQUIRED_PREVIOUS_STATUS
        and previous_branch_closed is True
        and previous_next_key == REQUIRED_RESEARCH_KEY
    )

    canonical_policy_month_count = int(evaluator.get("canonical_policy_month_count") or 12)
    if canonical_policy_month_count != 12:
        canonical_policy_month_count = 12

    contract_seed = {
        "builder": "edge_factory_os_research_direction_contract_builder_v5",
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "previous_evaluator_status": previous_status,
        "previous_route_hash": evaluator.get("route_hash"),
        "previous_lesson_id": evaluator.get("lesson_id"),
    }

    contract_hash = stable_hash(contract_seed)
    contract_id = f"CALM_MARKET_LOW_VOL_CONTINUATION_ARCHETYPE_CONTRACT_V1_{contract_hash}_{timestamp_compact()}"

    if prerequisite_pass:
        builder_status = "RESEARCH_DIRECTION_CONTRACT_V5_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_CALM_MARKET_LOW_VOL_CONTINUATION_ARCHETYPE_RUNNER"
        reason = (
            "previous_market_neutral_branch_closed=True; "
            "rotating_to_RD3_03_CALM_MARKET_LOW_VOL_CONTINUATION_ARCHETYPE_SEARCH"
        )
    else:
        builder_status = "RESEARCH_DIRECTION_CONTRACT_V5_BLOCKED_PREREQUISITE_NOT_MET"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_MARKET_NEUTRAL_EVALUATOR_BEFORE_BUILDING_NEW_CONTRACT"
        reason = (
            f"previous_status={previous_status}; "
            f"previous_branch_closed={previous_branch_closed}; "
            f"previous_next_key={previous_next_key}"
        )

    contract = {
        "builder_name": "edge_factory_os_research_direction_contract_builder_v5",
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
        "research_title": "Calm Market Low-Vol Continuation Archetype Search",
        "research_question": (
            "Can low-volatility, calm-market continuation conditions produce a stricter "
            "12-of-12 canonical month-stable edge than impulse, feature-repair, non-impulse "
            "mean reversion, and market-neutral relative-value branches?"
        ),
        "branch_rationale": [
            "Impulse-derived routes produced promise in subsets but failed release-quality validation.",
            "Feature-conditioned month repair found no canonical 12-of-12 signal.",
            "Non-impulse mean reversion branch produced no strict preview.",
            "Market-neutral relative value branch produced 576 valid rules but zero strict 12/12 passes.",
            "Next branch rotates to calmer continuation regimes rather than high-vol impulse or spread-style relative value.",
        ],
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "canonical_month_policy": {
            "use_canonical_policy_month_count": True,
            "required_canonical_month_count": 12,
            "ignore_raw_13_calendar_bucket_for_release": True,
            "positive_months_required": 12,
            "negative_months_allowed": 0,
            "partial_boundary_months_allowed_for_raw_observation_only": True,
        },
        "search_design": {
            "archetype": "calm_market_low_vol_continuation",
            "allowed_signal_family": "continuation_only_read_only_research",
            "disallowed_signal_families": [
                "repeat_impulse_route_without_new_evidence",
                "repeat_market_neutral_relative_value_route_without_new_features",
                "candidate_generation_from_preview_only",
                "family_release_from_preview_only",
            ],
            "core_hypotheses": [
                {
                    "hypothesis_id": "CM_LV_CONT_H1",
                    "description": "Low market volatility plus mild positive coin trend may have better month stability than extreme impulse.",
                    "test_axis": ["market_volatility_low", "coin_ret_positive_mild", "no_extreme_range"],
                },
                {
                    "hypothesis_id": "CM_LV_CONT_H2",
                    "description": "Continuation may work only when broad market drift is calm or slightly supportive.",
                    "test_axis": ["mkt_ret_non_negative", "mkt_vol_low", "coin_relative_strength_positive"],
                },
                {
                    "hypothesis_id": "CM_LV_CONT_H3",
                    "description": "Avoiding high range/high volatility buckets may reduce tail-loss concentration.",
                    "test_axis": ["entry_range_filter", "realized_vol_filter", "liquidity_floor"],
                },
                {
                    "hypothesis_id": "CM_LV_CONT_H4",
                    "description": "Shorter holds may preserve edge better under low volatility continuation.",
                    "test_axis": ["hold_1h", "hold_3h", "hold_6h", "hold_12h"],
                },
            ],
            "minimum_runner_requirements": {
                "must_use_full_universe_panel": True,
                "must_use_1y_okx_swap_universe_if_available": True,
                "must_report_raw_calendar_month_count": True,
                "must_report_canonical_policy_month_count": True,
                "must_rank_rules_by_strict_policy_first": True,
                "must_write_ranked_csv": True,
                "must_write_latest_json": True,
                "must_keep_all_action_flags_false": True,
            },
            "release_requirements_not_satisfied_by_this_contract": [
                "full_universe_offline_backtest_pass",
                "oos_or_rolling_validation_pass",
                "month_stability_12_of_12_pass",
                "cost_slippage_sensitivity_pass",
                "regime_bucket_diagnostic_pass",
                "symbol_concentration_risk_pass",
                "lesson_memory_no_repeat_failure_pass",
                "risk_and_capital_safety_pass",
                "manual_or_ai_review_pass",
            ],
        },
        "panel_candidates": infer_panel_candidates(),
        "input_evaluator_path": str(INPUT_EVALUATOR_JSON),
        "previous_branch": {
            "evaluator_status": previous_status,
            "branch_closed": previous_branch_closed,
            "next_recommended_research_key": previous_next_key,
            "route_hash": evaluator.get("route_hash"),
            "lesson_id": evaluator.get("lesson_id"),
            "rules_tested": evaluator.get("rules_tested"),
            "valid_rule_count": evaluator.get("valid_rule_count"),
            "strict_12_subset_pass_count": evaluator.get("strict_12_subset_pass_count"),
        },
        "next_module": NEXT_MODULE if prerequisite_pass else None,
        "release_gate_feed": {
            "RESEARCH_DIRECTION_CONTRACT_V5_READY": prerequisite_pass,
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
