#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Label-Free Event Motif Contract Builder v1

Purpose:
- Consume Regime First Cluster Evaluator v1 output.
- Build a read-only/offline research contract for:
  RD4_02_LABEL_FREE_EVENT_MOTIF_MINING.
- This is not another hand-designed entry rule.
- The goal is to mine recurring event motifs from return/range/vol/liquidity tensors
  without future labels in the motif discovery input.

This builder does NOT:
- run motif mining
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

REGIME_EVALUATOR_JSON = (
    BASE_DIR
    / "edge_factory_os_regime_first_cluster_evaluator"
    / "regime_first_cluster_evaluator_latest.json"
)

REGIME_NEXT_QUEUE_JSON = (
    BASE_DIR
    / "edge_factory_os_regime_first_cluster_evaluator"
    / "regime_first_next_research_queue_latest.json"
)

OUT_DIR = BASE_DIR / "edge_factory_os_research_direction_contracts"
OUT_JSON = OUT_DIR / "label_free_event_motif_contract_latest.json"
OUT_TXT = OUT_DIR / "label_free_event_motif_contract_latest.txt"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

REQUIRED_EVALUATOR_STATUS = "REGIME_FIRST_CLUSTER_EVALUATOR_BRANCH_CLOSED"
REQUIRED_DIRECTION_KEY = "RD4_02_LABEL_FREE_EVENT_MOTIF_MINING"

RESEARCH_KEY = "LABEL_FREE_EVENT_MOTIF_MINING_V1"
DIRECTION_QUEUE_KEY = "RD4_02_LABEL_FREE_EVENT_MOTIF_MINING"
NEXT_MODULE = "edge_factory_os_label_free_event_motif_runner_v1.py"

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
    lines.append("EDGE FACTORY OS LABEL-FREE EVENT MOTIF CONTRACT BUILDER v1")
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
    lines.append("MOTIF DISCOVERY DESIGN")
    lines.append("-" * 100)
    design = result.get("motif_contract", {})
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
    print("EDGE FACTORY OS LABEL-FREE EVENT MOTIF CONTRACT BUILDER v1")
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

    evaluator = load_json(REGIME_EVALUATOR_JSON, default={})
    queue = load_json(REGIME_NEXT_QUEUE_JSON, default={})
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
        "builder": "edge_factory_os_label_free_event_motif_contract_builder_v1",
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
    contract_id = f"LABEL_FREE_EVENT_MOTIF_CONTRACT_V1_{contract_hash}_{timestamp_compact()}"

    if prerequisite_pass:
        builder_status = "LABEL_FREE_EVENT_MOTIF_CONTRACT_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_LABEL_FREE_EVENT_MOTIF_RUNNER"
        reason = (
            f"regime_first_branch_closed=True; top_key={top_key}; "
            "building label-free event motif mining contract"
        )
    else:
        builder_status = "LABEL_FREE_EVENT_MOTIF_CONTRACT_BLOCKED_PREREQUISITE_NOT_MET"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_REGIME_FIRST_EVALUATOR_QUEUE_BEFORE_BUILDING_MOTIF_CONTRACT"
        reason = (
            f"evaluator_status={evaluator_status}; branch_closed={branch_closed}; "
            f"queue_status={queue_status}; top_key={top_key}; top_module={top_module}; "
            f"canonical_policy_month_count={canonical_policy_month_count}"
        )

    contract_principles = [
        "Motif discovery first; no hand-designed entry rule first.",
        "Use full 1Y 285-symbol OKX swap panel if available.",
        "Use only pre-outcome event tensors during motif discovery.",
        "Future return/PnL may be used only after motif discovery for diagnostic preview.",
        "No manual month blacklist.",
        "No manual symbol cherry-picking.",
        "No candidate generation from motif preview.",
        "No family release from motif preview.",
        "STRICT_MONTH_STABILITY_12_OF_12 remains mandatory for any future release chain.",
        "Any later candidate route must have a new route hash and pass the full prerequisite chain.",
    ]

    contract = {
        "builder_name": "edge_factory_os_label_free_event_motif_contract_builder_v1",
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
        "research_title": "Label-free event motif mining",
        "research_question": (
            "Can recurring event motifs be mined directly from return/range/volatility/liquidity tensors, "
            "without assuming impulse, continuation, mean-reversion, market-neutral spread, or aggregate regime clusters, "
            "and do any such motifs explain stable 12-of-12 canonical month opportunity structure?"
        ),
        "why_now": {
            "source_evaluator_status": evaluator_status,
            "source_branch_closed": branch_closed,
            "source_strict_12_cluster_preview_count": evaluator.get("strict_12_cluster_preview_count"),
            "source_lesson_id": evaluator.get("lesson_id"),
            "summary": (
                "Multiple hand-designed archetypes and the first regime-cluster approach failed strict month stability. "
                "The OS should now search for recurring event motifs before defining any entry family."
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
        "motif_contract": {
            "motif_level": [
                "symbol_event_sequence",
                "timestamp_cross_sectional_event_sequence",
                "market_state_event_sequence",
            ],
            "allowed_discovery_inputs_pre_outcome_only": [
                "past_return_windows",
                "past_return_sign_and_magnitude_bins",
                "range_bins",
                "volatility_bins",
                "liquidity_bins",
                "cross_sectional_rank_bins",
                "relative_strength_bins",
                "breadth_bins",
                "drawdown_or_rebound_state_without_future_labels",
            ],
            "forbidden_discovery_inputs": [
                "future_return",
                "future_pnl",
                "future_win_loss",
                "month_outcome_label",
                "manual_month_blacklist",
                "manual_symbol_whitelist",
                "post_outcome_selected_motif",
            ],
            "allowed_diagnostic_outputs_after_discovery": [
                "motif_forward_return_preview",
                "motif_month_coverage",
                "motif_positive_month_count",
                "motif_symbol_concentration",
                "motif_frequency_by_month",
                "strict_12_preview_count",
            ],
            "motif_methods_allowed": [
                "discretized_state_ngrams",
                "rolling_event_windows",
                "frequent_sequence_mining_lightweight",
                "shapelet_like_event_templates_without_future_labels",
                "cross_sectional_rank_state_sequences",
            ],
            "motif_sequence_lengths": [3, 4, 6, 8, 12],
            "state_bin_design": {
                "return_bins": ["large_down", "medium_down", "flat", "medium_up", "large_up"],
                "range_bins": ["low", "mid", "high"],
                "volatility_bins": ["low", "mid", "high"],
                "liquidity_bins": ["low", "mid", "high"],
                "relative_strength_bins": ["weak", "neutral", "strong"],
            },
            "required_runner_outputs": [
                "motif_count",
                "motif_frequency_table",
                "motif_month_coverage_table",
                "motif_symbol_coverage_table",
                "motif_forward_diagnostic_preview",
                "strict_12_motif_preview_count",
                "ranked_motif_report_csv",
                "latest_json",
            ],
            "required_evaluator_outputs_later": [
                "whether any motif has 12 canonical active months",
                "whether any motif has 12 positive canonical months under preview",
                "whether motif is too symbol-concentrated",
                "whether motif is too rare",
                "whether a later candidate contract is justified",
                "whether branch should close and rotate to exit/risk-shape research",
            ],
        },
        "panel_candidates": infer_panel_candidates(),
        "input_regime_evaluator_path": str(REGIME_EVALUATOR_JSON),
        "input_regime_queue_path": str(REGIME_NEXT_QUEUE_JSON),
        "source_regime_first_evaluator": {
            "evaluator_status": evaluator_status,
            "branch_closed": branch_closed,
            "route_hash": evaluator.get("route_hash"),
            "lesson_id": evaluator.get("lesson_id"),
            "cluster_grid_count": evaluator.get("cluster_grid_count"),
            "strict_12_cluster_preview_count": evaluator.get("strict_12_cluster_preview_count"),
            "next_recommended_research_key": evaluator.get("next_recommended_research_key"),
            "next_module": evaluator.get("next_module"),
        },
        "next_module": NEXT_MODULE if prerequisite_pass else None,
        "release_gate_feed": {
            "LABEL_FREE_EVENT_MOTIF_CONTRACT_READY": prerequisite_pass,
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
