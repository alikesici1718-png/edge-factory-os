#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Regime First Cluster Contract Builder v1

Purpose:
- Consume Offline Research Result Synthesizer v1 queue.
- Build a read-only/offline research contract for:
  RD4_01_REGIME_FIRST_UNSUPERVISED_CLUSTER_SEARCH.
- The goal is NOT another hand-designed entry rule.
- The goal is to cluster market/month regimes first, then later inspect whether any
  regime has stable opportunity structure under STRICT_MONTH_STABILITY_12_OF_12.

This builder does NOT:
- run clustering
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
from typing import Any, Dict, List, Optional


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

SYNTH_JSON = (
    BASE_DIR
    / "edge_factory_os_offline_research_result_synthesizer"
    / "offline_research_result_synthesizer_latest.json"
)

QUEUE_JSON = (
    BASE_DIR
    / "edge_factory_os_offline_research_result_synthesizer"
    / "offline_research_next_direction_queue_latest.json"
)

OUT_DIR = BASE_DIR / "edge_factory_os_research_direction_contracts"
OUT_JSON = OUT_DIR / "regime_first_cluster_contract_latest.json"
OUT_TXT = OUT_DIR / "regime_first_cluster_contract_latest.txt"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

REQUIRED_SYNTH_STATUS = "OFFLINE_RESEARCH_SYNTHESIZER_NEW_DIRECTION_QUEUED"
REQUIRED_RESEARCH_KEY = "RD4_01_REGIME_FIRST_UNSUPERVISED_CLUSTER_SEARCH"

RESEARCH_KEY = "REGIME_FIRST_UNSUPERVISED_CLUSTER_SEARCH_V1"
DIRECTION_QUEUE_KEY = "RD4_01_REGIME_FIRST_UNSUPERVISED_CLUSTER_SEARCH"
NEXT_MODULE = "edge_factory_os_regime_first_cluster_runner_v1.py"

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
        score_value = 0
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
                score_value += weight
        try:
            score_value += min(int(path.stat().st_size / 100_000_000), 25)
        except Exception:
            pass
        return score_value

    found = sorted(set(found), key=score, reverse=True)
    return [str(p) for p in found[:5]]


def get_top_queue_direction(queue: Dict[str, Any], synth: Dict[str, Any]) -> Dict[str, Any]:
    q = queue.get("next_direction_queue")
    if isinstance(q, list) and q:
        sorted_q = sorted(q, key=lambda x: int(x.get("priority", 0)) if isinstance(x, dict) else 0, reverse=True)
        if isinstance(sorted_q[0], dict):
            return sorted_q[0]

    q2 = synth.get("next_direction_queue")
    if isinstance(q2, list) and q2:
        sorted_q2 = sorted(q2, key=lambda x: int(x.get("priority", 0)) if isinstance(x, dict) else 0, reverse=True)
        if isinstance(sorted_q2[0], dict):
            return sorted_q2[0]

    return {}


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []

    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS REGIME FIRST CLUSTER CONTRACT BUILDER v1")
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
    print("EDGE FACTORY OS REGIME FIRST CLUSTER CONTRACT BUILDER v1")
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

    synth = load_json(SYNTH_JSON, default={})
    queue = load_json(QUEUE_JSON, default={})
    top_direction = get_top_queue_direction(queue, synth)

    synth_status = synth.get("synthesizer_status")
    queue_status = queue.get("queue_status")
    top_key = top_direction.get("research_key") or queue.get("top_next_research_key") or synth.get("top_next_research_key")
    top_module = top_direction.get("next_module_recommendation") or queue.get("top_next_module") or synth.get("top_next_module")

    materially_different_required = bool(synth.get("materially_different_direction_required"))
    strict_failure_count = int(synth.get("strict_failure_record_count") or 0)
    closed_branch_count = int(synth.get("closed_branch_count") or 0)

    prerequisite_pass = (
        synth_status == REQUIRED_SYNTH_STATUS
        and materially_different_required is True
        and top_key == REQUIRED_RESEARCH_KEY
        and strict_failure_count >= 2
        and closed_branch_count >= 2
    )

    seed = {
        "builder": "edge_factory_os_regime_first_cluster_contract_builder_v1",
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "strict_policy_key": STRICT_POLICY_KEY,
        "synthesis_hash": synth.get("synthesis_hash"),
        "strict_failure_record_count": strict_failure_count,
        "closed_branch_count": closed_branch_count,
        "top_key": top_key,
    }

    contract_hash = stable_hash(seed)
    contract_id = f"REGIME_FIRST_CLUSTER_CONTRACT_V1_{contract_hash}_{timestamp_compact()}"

    if prerequisite_pass:
        builder_status = "REGIME_FIRST_CLUSTER_CONTRACT_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_REGIME_FIRST_CLUSTER_RUNNER"
        reason = (
            f"synth_status={synth_status}; strict_failure_record_count={strict_failure_count}; "
            f"closed_branch_count={closed_branch_count}; top_key={top_key}"
        )
    else:
        builder_status = "REGIME_FIRST_CLUSTER_CONTRACT_BLOCKED_PREREQUISITE_NOT_MET"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_SYNTHESIZER_QUEUE_BEFORE_BUILDING_REGIME_CONTRACT"
        reason = (
            f"synth_status={synth_status}; queue_status={queue_status}; "
            f"materially_different_required={materially_different_required}; "
            f"strict_failure_record_count={strict_failure_count}; closed_branch_count={closed_branch_count}; "
            f"top_key={top_key}; top_module={top_module}"
        )

    contract_principles = [
        "Regime discovery first; no hand-designed entry rule first.",
        "Use full 1Y 285-symbol OKX swap panel if available.",
        "Cluster only pre-outcome market/month/symbol-state features.",
        "No manual month blacklist.",
        "No manual symbol cherry-picking.",
        "No candidate generation from cluster preview.",
        "No family release from cluster preview.",
        "STRICT_MONTH_STABILITY_12_OF_12 remains mandatory for any future release chain.",
        "Any later candidate route must have a new route hash and pass full prerequisite chain.",
    ]

    contract = {
        "builder_name": "edge_factory_os_regime_first_cluster_contract_builder_v1",
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
        "research_title": "Regime-first unsupervised cluster search",
        "research_question": (
            "Can market/month regimes be discovered label-free from full-universe pre-outcome features, "
            "and can those regimes explain why hand-designed archetypes keep failing strict 12-of-12 month stability?"
        ),
        "why_now": {
            "source_synthesizer_status": synth_status,
            "strict_failure_record_count": strict_failure_count,
            "closed_branch_count": closed_branch_count,
            "materially_different_direction_required": materially_different_required,
            "summary": (
                "Multiple entry/archetype branches failed strict month stability. "
                "The OS should stop rotating minor entry variants and first map regimes."
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
        "cluster_contract": {
            "cluster_level": [
                "timestamp_market_state",
                "month_market_state",
                "symbol_state_optional_second_pass",
            ],
            "allowed_input_features_pre_outcome_only": [
                "market_return_windows",
                "cross_sectional_dispersion",
                "market_realized_volatility",
                "range_distribution",
                "liquidity_distribution",
                "trend_breadth",
                "relative_strength_distribution",
                "drawdown_or_rebound_state_without_future_labels",
            ],
            "explicitly_forbidden_inputs": [
                "future_return",
                "future_pnl",
                "month_outcome_label",
                "manual_month_blacklist",
                "manual_symbol_whitelist",
                "post_outcome_cluster_selection",
            ],
            "required_runner_outputs": [
                "cluster_count_grid",
                "cluster_membership_by_timestamp",
                "cluster_month_coverage",
                "cluster_feature_centroids",
                "cluster_stability_summary",
                "per_cluster_forward_diagnostic_preview",
                "strict_12_policy_readiness_summary",
                "ranked_cluster_report_csv",
                "latest_json",
            ],
            "required_evaluator_outputs_later": [
                "whether any cluster has 12 canonical active months",
                "whether any cluster has 12 positive canonical months under preview",
                "whether results are symbol-concentrated",
                "whether a later rule-search contract is justified",
                "whether no cluster explains failure and search space must rotate again",
            ],
        },
        "panel_candidates": infer_panel_candidates(),
        "input_synthesizer_path": str(SYNTH_JSON),
        "input_queue_path": str(QUEUE_JSON),
        "source_synthesis": {
            "synthesizer_status": synth_status,
            "queue_status": queue_status,
            "synthesis_hash": synth.get("synthesis_hash"),
            "strict_failure_record_count": strict_failure_count,
            "closed_branch_count": closed_branch_count,
            "top_next_research_key": top_key,
            "top_next_module": top_module,
        },
        "next_module": NEXT_MODULE if prerequisite_pass else None,
        "release_gate_feed": {
            "REGIME_FIRST_CLUSTER_CONTRACT_READY": prerequisite_pass,
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
