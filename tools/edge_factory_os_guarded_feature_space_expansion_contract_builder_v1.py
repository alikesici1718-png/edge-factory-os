#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Guarded Feature Space Expansion Contract Builder v1

Purpose:
- Consume Research Meta Synthesizer v2 output.
- Consume Data Quality Guard feed.
- Build a read-only research contract for:
  RD5_01_GUARDED_FEATURE_SPACE_EXPANSION_AND_NEGATIVE_CONTROL_SEARCH.
- Require future runner to use data-quality guards, lesson memory, route blocklist,
  null models, negative controls, and no-release discipline.

This builder does NOT:
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

import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

META_JSON = (
    BASE_DIR
    / "edge_factory_os_research_meta_synthesizer_v2"
    / "research_meta_synthesizer_v2_latest.json"
)

META_QUEUE_JSON = (
    BASE_DIR
    / "edge_factory_os_research_meta_synthesizer_v2"
    / "guarded_research_direction_queue_v2_latest.json"
)

GUARD_FEED_JSON = (
    BASE_DIR
    / "edge_factory_os_data_quality_guard_runner"
    / "data_quality_guard_feed_latest.json"
)

GUARD_RUNNER_JSON = (
    BASE_DIR
    / "edge_factory_os_data_quality_guard_runner"
    / "data_quality_guard_runner_latest.json"
)

LESSON_INDEX_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

OUT_DIR = BASE_DIR / "edge_factory_os_research_direction_contracts"
OUT_JSON = OUT_DIR / "guarded_feature_space_expansion_contract_latest.json"
OUT_TXT = OUT_DIR / "guarded_feature_space_expansion_contract_latest.txt"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

REQUIRED_META_STATUS = "RESEARCH_META_SYNTHESIZER_V2_NEW_GUARDED_DIRECTION_QUEUED"
REQUIRED_DIRECTION_KEY = "RD5_01_GUARDED_FEATURE_SPACE_EXPANSION_AND_NEGATIVE_CONTROL_SEARCH"

RESEARCH_KEY = "GUARDED_FEATURE_SPACE_EXPANSION_AND_NEGATIVE_CONTROL_SEARCH_V1"
DIRECTION_QUEUE_KEY = "RD5_01_GUARDED_FEATURE_SPACE_EXPANSION_AND_NEGATIVE_CONTROL_SEARCH"
NEXT_MODULE = "edge_factory_os_guarded_feature_space_expansion_runner_v1.py"

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


def extract_top_direction(queue: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, Any]:
    items = queue.get("next_direction_queue")
    if isinstance(items, list) and items:
        valid = [x for x in items if isinstance(x, dict)]
        if valid:
            return sorted(valid, key=lambda x: int(x.get("priority", 0)), reverse=True)[0]

    return {
        "research_key": meta.get("top_next_research_key"),
        "next_module_recommendation": meta.get("top_next_module"),
        "priority": 100,
    }


def extract_blocked_route_hashes(blocklist: Dict[str, Any]) -> List[str]:
    if isinstance(blocklist, dict):
        routes = blocklist.get("blocked_routes")
        if isinstance(routes, list):
            return [str(x.get("route_hash")) for x in routes if isinstance(x, dict) and x.get("route_hash")]
    if isinstance(blocklist, list):
        return [str(x.get("route_hash")) for x in blocklist if isinstance(x, dict) and x.get("route_hash")]
    return []


def extract_lesson_ids(lesson_index: Dict[str, Any]) -> List[str]:
    if isinstance(lesson_index, dict):
        lessons = lesson_index.get("lessons")
        if isinstance(lessons, list):
            return [str(x.get("lesson_id")) for x in lessons if isinstance(x, dict) and x.get("lesson_id")]
    if isinstance(lesson_index, list):
        return [str(x.get("lesson_id")) for x in lesson_index if isinstance(x, dict) and x.get("lesson_id")]
    return []


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


def build_feature_space_requirements(guard_feed: Dict[str, Any]) -> List[Dict[str, Any]]:
    guard_results = guard_feed.get("mandatory_future_research_requirements")
    if not isinstance(guard_results, list):
        guard_results = []

    guard_keys = [
        str(x.get("guard_key"))
        for x in guard_results
        if isinstance(x, dict) and x.get("guard_key")
    ]

    return [
        {
            "requirement_key": "CONSUME_DATA_QUALITY_GUARD_FEED",
            "description": "Runner must load and report data_quality_guard_feed_latest.json.",
            "must_pass": True,
            "source_guard_keys": guard_keys,
        },
        {
            "requirement_key": "DO_NOT_REOPEN_BLOCKED_ROUTES",
            "description": "Runner must check route blocklist and avoid all known failed route hashes.",
            "must_pass": True,
        },
        {
            "requirement_key": "FEATURE_SPACE_EXPANSION_PRE_OUTCOME_ONLY",
            "description": "Expanded features may use only information available before the diagnostic timestamp.",
            "must_pass": True,
            "allowed_feature_families": [
                "multi_horizon_return_shape_pre_outcome",
                "volatility_regime_pre_outcome",
                "range_compression_expansion_pre_outcome",
                "liquidity_state_pre_outcome",
                "cross_sectional_dispersion_pre_outcome",
                "market_beta_and_correlation_pre_outcome",
                "symbol_lifecycle_pre_outcome",
                "gap_aware_feature_resets",
                "rank_stability_pre_outcome",
            ],
            "forbidden_feature_families": [
                "future_return",
                "future_pnl",
                "future_win_loss",
                "future_month_label",
                "post_outcome_symbol_selection",
                "manual_month_blacklist",
                "manual_symbol_whitelist",
            ],
        },
        {
            "requirement_key": "NEGATIVE_CONTROLS_REQUIRED",
            "description": "Runner must include negative controls before ranking any feature family.",
            "must_pass": True,
            "negative_controls": [
                "random_symbol_feature_control",
                "month_shuffled_feature_control",
                "time_shifted_feature_control",
                "random_noise_feature_control",
                "direction_flipped_label_control",
            ],
        },
        {
            "requirement_key": "NULL_MODEL_BASELINE_REQUIRED",
            "description": "Runner must estimate whether observed feature diagnostics beat null/permutation baselines.",
            "must_pass": True,
            "null_models": [
                "within_month_symbol_shuffle",
                "month_order_shuffle",
                "feature_rank_shuffle",
                "side_label_shuffle",
                "cost_perturbation_null",
            ],
        },
        {
            "requirement_key": "NO_RELEASE_FROM_FEATURE_DIAGNOSTICS",
            "description": "Feature diagnostics can only queue later validation contracts; they cannot create candidate/family/runtime/capital/live actions.",
            "must_pass": True,
        },
    ]


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS GUARDED FEATURE SPACE EXPANSION CONTRACT BUILDER v1")
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
        "guard_status",
        "guard_pass",
        "feature_requirement_count",
        "negative_control_count",
        "null_model_count",
        "blocked_route_count",
        "lesson_count",
        "next_module",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("FEATURE SPACE REQUIREMENTS")
    lines.append("-" * 100)
    for item in result.get("feature_space_requirements", []):
        lines.append(f"- {item.get('requirement_key')}: {item.get('description')}")

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
    print("EDGE FACTORY OS GUARDED FEATURE SPACE EXPANSION CONTRACT BUILDER v1")
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
    print(f"guard_status: {result.get('guard_status')}")
    print(f"guard_pass: {result.get('guard_pass')}")
    print(f"feature_requirement_count: {result.get('feature_requirement_count')}")
    print(f"negative_control_count: {result.get('negative_control_count')}")
    print(f"null_model_count: {result.get('null_model_count')}")
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

    meta = load_json(META_JSON, default={})
    meta_queue = load_json(META_QUEUE_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})
    guard_runner = load_json(GUARD_RUNNER_JSON, default={})
    lesson_index = load_json(LESSON_INDEX_PATH, default={})
    blocklist = load_json(BLOCKLIST_PATH, default={})

    top_direction = extract_top_direction(meta_queue, meta)

    meta_status = meta.get("synthesizer_status")
    top_key = top_direction.get("research_key") or meta.get("top_next_research_key")
    top_module = top_direction.get("next_module_recommendation") or meta.get("top_next_module")

    guard_status = guard_feed.get("guard_status") or guard_runner.get("guard_status")
    guard_pass = bool(guard_feed.get("guard_pass")) and bool(guard_runner.get("guard_pass"))
    research_meta_synthesis_allowed = (
        bool(guard_feed.get("research_meta_synthesis_allowed"))
        and bool(guard_runner.get("research_meta_synthesis_allowed"))
        and bool(meta.get("research_meta_synthesis_allowed"))
    )

    canonical_policy_month_count = int(guard_feed.get("canonical_policy_month_count") or 12)
    if canonical_policy_month_count != 12:
        canonical_policy_month_count = 12

    blocked_route_hashes = extract_blocked_route_hashes(blocklist)
    lesson_ids = extract_lesson_ids(lesson_index)

    feature_requirements = build_feature_space_requirements(guard_feed)

    negative_control_count = 0
    null_model_count = 0
    for item in feature_requirements:
        negative_control_count += len(item.get("negative_controls", [])) if isinstance(item.get("negative_controls"), list) else 0
        null_model_count += len(item.get("null_models", [])) if isinstance(item.get("null_models"), list) else 0

    prerequisite_pass = (
        meta_status == REQUIRED_META_STATUS
        and top_key == REQUIRED_DIRECTION_KEY
        and guard_pass is True
        and research_meta_synthesis_allowed is True
        and canonical_policy_month_count == 12
        and len(feature_requirements) > 0
    )

    seed = {
        "builder": "edge_factory_os_guarded_feature_space_expansion_contract_builder_v1",
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "meta_status": meta_status,
        "guard_status": guard_status,
        "guard_pass": guard_pass,
        "blocked_route_count": len(blocked_route_hashes),
        "lesson_count": len(lesson_ids),
        "requirement_keys": [x.get("requirement_key") for x in feature_requirements],
    }

    contract_hash = stable_hash(seed)
    contract_id = f"GUARDED_FEATURE_SPACE_EXPANSION_CONTRACT_V1_{contract_hash}_{timestamp_compact()}"

    if prerequisite_pass:
        builder_status = "GUARDED_FEATURE_SPACE_EXPANSION_CONTRACT_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_GUARDED_FEATURE_SPACE_EXPANSION_RUNNER"
        reason = (
            f"guard_pass=True; research_meta_synthesis_allowed=True; "
            f"blocked_route_count={len(blocked_route_hashes)}; lesson_count={len(lesson_ids)}; "
            "guarded_feature_space_contract_ready=True"
        )
    else:
        builder_status = "GUARDED_FEATURE_SPACE_EXPANSION_CONTRACT_BLOCKED_PREREQUISITE_NOT_MET"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_META_SYNTHESIZER_AND_DATA_QUALITY_GUARD_NO_RESEARCH"
        reason = (
            f"meta_status={meta_status}; top_key={top_key}; top_module={top_module}; "
            f"guard_status={guard_status}; guard_pass={guard_pass}; "
            f"research_meta_synthesis_allowed={research_meta_synthesis_allowed}; "
            f"canonical_policy_month_count={canonical_policy_month_count}"
        )

    contract = {
        "builder_name": "edge_factory_os_guarded_feature_space_expansion_contract_builder_v1",
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
        "research_title": "Guarded feature-space expansion and negative-control search",
        "research_question": (
            "After multiple strict 12/12 failures and after data-quality guard pass, can a broader pre-outcome "
            "feature space show diagnostic signal that beats negative controls and null/permutation baselines, "
            "without reopening blocked routes or creating candidates?"
        ),
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "guard_status": guard_status,
        "guard_pass": guard_pass,
        "research_meta_synthesis_allowed": research_meta_synthesis_allowed,
        "data_quality_guard_feed_path": str(GUARD_FEED_JSON),
        "blocked_route_count": len(blocked_route_hashes),
        "blocked_route_hashes": blocked_route_hashes,
        "lesson_count": len(lesson_ids),
        "lesson_ids_sample": lesson_ids[-20:],
        "feature_requirement_count": len(feature_requirements),
        "feature_space_requirements": feature_requirements,
        "negative_control_count": negative_control_count,
        "null_model_count": null_model_count,
        "guarded_feature_space_contract": {
            "contract_scope": "READ_ONLY_DIAGNOSTIC_FEATURE_SPACE_EXPANSION",
            "must_consume_guard_feed": True,
            "must_not_reopen_blocked_routes": True,
            "must_include_negative_controls": True,
            "must_include_null_models": True,
            "feature_discovery_is_candidate_generation": False,
            "release_from_feature_diagnostics_allowed": False,
            "candidate_generation_allowed": False,
            "candidate_contract_allowed": False,
            "family_release_allowed": False,
            "runtime_touch_allowed": False,
            "capital_change_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
            "allowed_feature_families": [
                "pre_outcome_multi_horizon_return_shape",
                "pre_outcome_realized_volatility_surface",
                "pre_outcome_range_compression_expansion",
                "pre_outcome_liquidity_state_and_rank_stability",
                "pre_outcome_cross_sectional_dispersion",
                "pre_outcome_market_beta_correlation",
                "pre_outcome_symbol_lifecycle_and_coverage",
                "gap_aware_feature_resets",
                "pre_outcome_month_state_context_without_outcome_labels",
            ],
            "forbidden_inputs": [
                "future_return",
                "future_pnl",
                "future_win_loss",
                "future_month_label",
                "post_outcome_cluster_selection",
                "manual_symbol_whitelist",
                "manual_month_blacklist",
                "blocked_route_hash_reuse",
            ],
            "required_runner_outputs": [
                "guard_consumption_report",
                "feature_family_inventory",
                "negative_control_results",
                "null_model_results",
                "feature_diagnostic_rankings",
                "strict_12_feature_signal_preview_count",
                "null_adjusted_signal_count",
                "latest_json",
                "latest_txt",
                "csv_outputs",
            ],
            "downstream_rules": {
                "if_no_feature_beats_null": "record lesson and queue null-model/permutation baseline expansion",
                "if_feature_beats_null": "build deep validation contract, still no candidate/family/runtime/capital/live",
                "if_guard_not_consumed": "block runner output",
            },
        },
        "panel_candidates": infer_panel_candidates(),
        "source_meta_synthesizer": {
            "path": str(META_JSON),
            "status": meta_status,
            "lesson_count": meta.get("lesson_count"),
            "blocked_route_count": meta.get("blocked_route_count"),
            "top_next_research_key": meta.get("top_next_research_key"),
            "top_next_module": meta.get("top_next_module"),
        },
        "source_guard": {
            "guard_runner_json": str(GUARD_RUNNER_JSON),
            "guard_feed_json": str(GUARD_FEED_JSON),
            "guard_status": guard_status,
            "guard_pass": guard_pass,
            "guard_requirement_count": guard_feed.get("guard_requirement_count") or guard_runner.get("guard_requirement_count"),
            "guard_warning_count": guard_feed.get("guard_warning_count") or guard_runner.get("guard_warning_count"),
        },
        "input_paths": {
            "meta_json": str(META_JSON),
            "meta_queue_json": str(META_QUEUE_JSON),
            "guard_feed_json": str(GUARD_FEED_JSON),
            "guard_runner_json": str(GUARD_RUNNER_JSON),
            "lesson_index_path": str(LESSON_INDEX_PATH),
            "blocklist_path": str(BLOCKLIST_PATH),
        },
        "next_module": NEXT_MODULE if prerequisite_pass else None,
        "release_gate_feed": {
            "GUARDED_FEATURE_SPACE_EXPANSION_CONTRACT_READY": prerequisite_pass,
            "DATA_QUALITY_GUARD_PASS": guard_pass,
            "STRICT_MONTH_STABILITY_12_OF_12": True,
            "RESEARCH_RUNNER_ALLOWED_FROM_THIS_CONTRACT": prerequisite_pass,
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
