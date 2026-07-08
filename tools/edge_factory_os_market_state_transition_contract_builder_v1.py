#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Market State Transition Contract Builder v1

Purpose:
- Consume Source Panel Anomaly Deep Validation Evaluator v1.
- Consume failed anomaly deep validation state and route blocklist.
- Consume framework status, research gate policy, true source-panel null state, guard/validator state.
- Build a materially different outcome-agnostic market-state transition research contract.
- Keep plugin expansion, candidate generation, family release, runtime, capital, live, and real orders blocked.

This builder does NOT:
- run market-state transition research
- generate candidates
- create candidate contracts
- release families
- touch runtime
- change capital
- start active paper
- enable live
- place real orders
- delete/move/archive files
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

EVALUATOR_JSON = (
    BASE_DIR
    / "edge_factory_os_source_panel_anomaly_deep_validation_evaluator"
    / "source_panel_anomaly_deep_validation_evaluator_latest.json"
)

NEXT_QUEUE_JSON = (
    BASE_DIR
    / "edge_factory_os_source_panel_anomaly_deep_validation_evaluator"
    / "source_panel_anomaly_deep_validation_next_queue_latest.json"
)

FAILED_DEEP_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "source_panel_anomaly_deep_validation_state_v1.json"
)

FRAMEWORK_STATUS_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "status"
    / "framework_status_panel_v1.json"
)

TRUE_PANEL_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "true_source_panel_empirical_null_baseline_state_v1.json"
)

POLICY_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_enforcement_policy_v1.json"
)

POLICY_RUNTIME_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_policy_runtime_state_v1.json"
)

POLICY_VALIDATION_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_validation_state_v1.json"
)

GUARD_FEED_JSON = (
    BASE_DIR
    / "edge_factory_os_data_quality_guard_runner"
    / "data_quality_guard_feed_latest.json"
)

SOURCE_PANEL_PATH = (
    BASE_DIR
    / "edge_factory_feature_panels"
    / "post_impulse_drift_long_v1"
    / "post_impulse_drift_long_v1_feature_panel_1h_dynamic.parquet"
)

LESSON_INDEX_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

FRAMEWORK_DIR = REPO_DIR / "edge_factory_os_framework"
PLUGIN_DIR = FRAMEWORK_DIR / "plugins"
CONTRACT_DIR = FRAMEWORK_DIR / "contracts"

REPO_PLUGIN_JSON = PLUGIN_DIR / "market_state_transition_plugin_v1.json"
REPO_CONTRACT_JSON = CONTRACT_DIR / "market_state_transition_contract_v1.json"
REPO_CONTRACT_TXT = CONTRACT_DIR / "market_state_transition_contract_v1.txt"

OUT_DIR = BASE_DIR / "edge_factory_os_market_state_transition_contract"
OUT_JSON = OUT_DIR / "market_state_transition_contract_latest.json"
OUT_TXT = OUT_DIR / "market_state_transition_contract_latest.txt"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

EXPECTED_EVALUATOR_STATUS = "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_EVALUATOR_ROUTE_CLOSED"
EXPECTED_DECISION_CLASS = "ANOMALY_PREVIEW_FAILED_DEEP_VALIDATION_UNSTABLE_AND_NULL_UNSAFE"
EXPECTED_NEXT_RESEARCH_KEY = "RD6_02_OUTCOME_AGNOSTIC_MARKET_STATE_TRANSITION_SEARCH"

RESEARCH_KEY = "OUTCOME_AGNOSTIC_MARKET_STATE_TRANSITION_SEARCH_V1"
DIRECTION_QUEUE_KEY = "RD6_02_OUTCOME_AGNOSTIC_MARKET_STATE_TRANSITION_SEARCH"
PLUGIN_KEY = "MARKET_STATE_TRANSITION_PLUGIN_V1"
NEXT_MODULE = "edge_factory_os_market_state_transition_runner_v1.py"

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
    "file_delete_performed": False,
    "file_move_performed": False,
    "archive_performed": False,
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
    except Exception as exc:
        return {"_load_error": f"{type(exc).__name__}: {exc}", "_path": str(path)}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    tmp.replace(path)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def stable_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def extract_lessons(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get("lessons"), list):
        return [x for x in obj["lessons"] if isinstance(x, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def extract_blocked_routes(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get("blocked_routes"), list):
        return [x for x in obj["blocked_routes"] if isinstance(x, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def blocked_hashes(obj: Any) -> set:
    out = set()
    for item in extract_blocked_routes(obj):
        route_hash = item.get("route_hash")
        if route_hash:
            out.add(str(route_hash))
    return out


def selected_queue_item(queue: Dict[str, Any]) -> Dict[str, Any]:
    items = queue.get("next_direction_queue")
    if isinstance(items, list):
        valid = [x for x in items if isinstance(x, dict)]
        if valid:
            return sorted(valid, key=lambda x: int(x.get("priority", 0)), reverse=True)[0]
    return {}


def build_plugin_config(
    *,
    policy: Dict[str, Any],
    guard_feed: Dict[str, Any],
    failed_deep_state: Dict[str, Any],
    evaluator: Dict[str, Any],
) -> Dict[str, Any]:
    rules = policy.get("enforced_gate_rules")
    if not isinstance(rules, dict):
        rules = {}

    required_guard_keys = [
        x.get("guard_key")
        for x in guard_feed.get("mandatory_future_research_requirements", [])
        if isinstance(x, dict) and x.get("guard_key")
    ]

    state_feature_groups = [
        {
            "group_key": "market_volatility_state",
            "description": "Outcome-agnostic volatility/range regime state using current and historical candle/range features only.",
            "candidate_features": [
                "derived_candle_range_bps",
                "entry_range_bps",
                "range_bps",
                "atr_bps",
                "realized_vol_bps",
            ],
        },
        {
            "group_key": "market_liquidity_state",
            "description": "Liquidity/participation state using volume/quote-volume/turnover style features.",
            "candidate_features": [
                "volume",
                "quote_volume",
                "entry_vol_quote",
                "vol_quote",
                "turnover",
            ],
        },
        {
            "group_key": "cross_sectional_dispersion_state",
            "description": "Cross-sectional dispersion/breadth state across symbols at each timestamp.",
            "candidate_features": [
                "cross_sectional_rank",
                "symbol_percentile",
                "market_dispersion",
                "breadth_proxy",
            ],
        },
        {
            "group_key": "market_beta_residual_state",
            "description": "Coin-vs-market residual or co-movement state without using forward returns.",
            "candidate_features": [
                "market_beta_proxy",
                "market_residual_proxy",
                "market_relative_level",
            ],
        },
        {
            "group_key": "time_structure_state",
            "description": "Intraday/day-of-week transition structure as control or state descriptor.",
            "candidate_features": [
                "derived_hour_utc",
                "derived_dayofweek_utc",
            ],
        },
    ]

    transition_methods = [
        "rolling_state_quantile_bucket_transition",
        "cross_sectional_state_rank_transition",
        "volatility_liquidity_joint_transition",
        "state_persistence_break_detection",
        "state_transition_matrix_asymmetry",
        "state_duration_and_reentry_profile",
        "state_change_point_candidate_scan",
        "state_cluster_transition_graph",
    ]

    negative_controls = [
        "timestamp_shuffle_control",
        "month_shuffle_control",
        "symbol_shuffle_control",
        "state_label_permutation_control",
        "transition_direction_flip_control",
        "feature_group_shuffle_control",
        "calendar_block_shuffle_control",
        "null_transition_matrix_control",
    ]

    return {
        "plugin_key": PLUGIN_KEY,
        "plugin_type": "READ_ONLY_OUTCOME_AGNOSTIC_MARKET_STATE_TRANSITION_SEARCH",
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "source_panel_path": str(SOURCE_PANEL_PATH),
        "must_consume_failed_anomaly_deep_validation_state": True,
        "must_consume_framework_status_panel": True,
        "must_consume_true_source_panel_null_state": True,
        "must_consume_research_gate_policy": True,
        "must_consume_guard_feed": True,
        "must_consume_route_blocklist": True,
        "must_be_materially_different_from_blocked_routes": True,
        "must_keep_plugin_expansion_blocked": True,
        "must_not_generate_candidate": True,
        "must_not_release_family": True,
        "must_not_touch_runtime": True,
        "must_not_change_capital": True,
        "must_not_enable_live": True,
        "source_closed_route_hash": failed_deep_state.get("route_hash") or evaluator.get("route_hash"),
        "source_failed_gates": failed_deep_state.get("failed_gate_keys") or evaluator.get("failed_gate_keys"),
        "state_feature_groups": state_feature_groups,
        "transition_methods": transition_methods,
        "negative_controls": negative_controls,
        "minimum_state_feature_group_count": 4,
        "minimum_transition_method_count": 6,
        "minimum_negative_control_count": 6,
        "minimum_empirical_null_runs": max(1000, int(rules.get("minimum_permutation_runs") or 1000)),
        "preferred_empirical_null_runs": max(2000, int(rules.get("minimum_permutation_runs") or 1000) * 2),
        "gate_caps": {
            "max_allowed_strict_12_any_random_hit_rate": min(0.01, float(rules.get("max_allowed_strict_12_any_random_hit_rate") or 0.01)),
            "max_allowed_null_adjusted_any_random_hit_rate": min(0.005, float(rules.get("max_allowed_null_adjusted_any_random_hit_rate") or 0.005)),
            "empirical_p_value_required_lte": min(0.01, float(rules.get("empirical_p_value_required_lte") or 0.01)),
            "minimum_actual_vs_null_margin_bps": float(rules.get("minimum_actual_vs_null_margin_bps") or 2500.0),
        },
        "transition_preview_requirements": {
            "must_be_outcome_agnostic": True,
            "must_have_canonical_12_month_presence": True,
            "must_pass_true_source_panel_null": True,
            "must_pass_negative_controls": True,
            "must_not_reuse_failed_anomaly_axis": True,
            "minimum_transition_stability_months": 12,
            "minimum_symbol_coverage": 200,
            "minimum_row_coverage": 1000000,
        },
        "required_guard_keys": required_guard_keys,
        "forbidden_inputs": [
            "future_return_as_feature",
            "future_pnl_as_feature",
            "outcome_label_first_selection",
            "post_outcome_filtering",
            "manual_symbol_whitelist",
            "manual_month_blacklist",
            "reuse_failed_source_panel_anomaly_route",
            "reuse_failed_derived_candle_body_high_extreme_route",
            "summary_row_only_replay",
            "synthetic_month_generation_only",
            "candidate_generation",
            "family_release",
            "runtime_touch",
            "capital_change",
            "active_paper",
            "live_or_real_orders",
        ],
        "required_runner_outputs": [
            "input_consumption_report",
            "state_feature_inventory",
            "state_transition_method_inventory",
            "market_state_transition_summary",
            "market_state_transition_month_stability",
            "market_state_transition_negative_controls",
            "true_source_panel_null_rerun",
            "policy_gate_pass_fail_table",
            "material_difference_report",
            "latest_json",
            "latest_txt",
            "csv_outputs",
        ],
        **SAFETY_FLAGS,
    }


def build_contract_text(contract: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS MARKET STATE TRANSITION CONTRACT v1")
    lines.append("=" * 100)

    for key in [
        "contract_status",
        "allowed_scope",
        "next_action",
        "contract_id",
        "contract_hash",
        "route_hash",
        "route_hash_blocked",
        "source_failed_route_hash",
        "source_failed_decision_class",
        "research_key",
        "direction_queue_key",
        "plugin_key",
        "policy_hash",
        "source_panel_path",
        "source_panel_exists",
        "state_feature_group_count",
        "transition_method_count",
        "negative_control_count",
        "release_allowed",
        "next_module",
    ]:
        lines.append(f"{key}: {contract.get(key)}")

    lines.append("")
    lines.append("STATE FEATURE GROUPS")
    lines.append("-" * 100)
    for item in contract.get("state_feature_groups", []):
        lines.append(f"- {item.get('group_key')}: {item.get('description')}")

    lines.append("")
    lines.append("TRANSITION METHODS")
    lines.append("-" * 100)
    for item in contract.get("transition_methods", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("NEGATIVE CONTROLS")
    lines.append("-" * 100)
    for item in contract.get("negative_controls", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("HARD REQUIREMENTS")
    lines.append("-" * 100)
    for item in contract.get("hard_requirements_for_runner", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        lines.append(f"{key}: {value}")

    return "\n".join(lines)


def build_summary_text(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS MARKET STATE TRANSITION CONTRACT BUILDER v1")
    lines.append("=" * 100)

    for key in [
        "builder_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "contract_id",
        "contract_hash",
        "route_hash",
        "route_hash_blocked",
        "source_failed_route_hash",
        "source_failed_decision_class",
        "research_key",
        "direction_queue_key",
        "plugin_key",
        "policy_hash",
        "source_panel_exists",
        "state_feature_group_count",
        "transition_method_count",
        "negative_control_count",
        "release_allowed",
        "next_module",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        lines.append(f"{key}: {value}")

    lines.append("")
    lines.append("OUTPUT PATHS")
    lines.append("-" * 100)
    for key in [
        "output_json",
        "output_txt",
        "repo_plugin_json",
        "repo_contract_json",
        "repo_contract_txt",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS MARKET STATE TRANSITION CONTRACT BUILDER v1")
    print("=" * 100)
    print(f"builder_status: {result.get('builder_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"contract_id: {result.get('contract_id')}")
    print(f"contract_hash: {result.get('contract_hash')}")
    print(f"route_hash: {result.get('route_hash')}")
    print(f"route_hash_blocked: {result.get('route_hash_blocked')}")
    print(f"source_failed_route_hash: {result.get('source_failed_route_hash')}")
    print(f"source_failed_decision_class: {result.get('source_failed_decision_class')}")
    print(f"research_key: {result.get('research_key')}")
    print(f"direction_queue_key: {result.get('direction_queue_key')}")
    print(f"plugin_key: {result.get('plugin_key')}")
    print(f"policy_hash: {result.get('policy_hash')}")
    print(f"source_panel_exists: {result.get('source_panel_exists')}")
    print(f"state_feature_group_count: {result.get('state_feature_group_count')}")
    print(f"transition_method_count: {result.get('transition_method_count')}")
    print(f"negative_control_count: {result.get('negative_control_count')}")
    print(f"release_allowed: {result.get('release_allowed')}")
    print(f"next_module: {result.get('next_module')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        print(f"{key}: {value}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"CONTRACT JSON: {result.get('repo_contract_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PLUGIN_DIR.mkdir(parents=True, exist_ok=True)
    CONTRACT_DIR.mkdir(parents=True, exist_ok=True)

    evaluator = load_json(EVALUATOR_JSON, default={})
    next_queue = load_json(NEXT_QUEUE_JSON, default={})
    failed_deep_state = load_json(FAILED_DEEP_STATE_JSON, default={})
    framework_status = load_json(FRAMEWORK_STATUS_JSON, default={})
    true_panel_state = load_json(TRUE_PANEL_STATE_JSON, default={})
    policy = load_json(POLICY_JSON, default={})
    runtime_state = load_json(POLICY_RUNTIME_STATE_JSON, default={})
    validation_state = load_json(POLICY_VALIDATION_STATE_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})
    lesson_index = load_json(LESSON_INDEX_PATH, default={})
    blocklist = load_json(BLOCKLIST_PATH, default={})

    selected = selected_queue_item(next_queue)

    evaluator_ok = (
        evaluator.get("evaluator_status") == EXPECTED_EVALUATOR_STATUS
        and evaluator.get("decision_class") == EXPECTED_DECISION_CLASS
        and evaluator.get("route_closed") is True
        and evaluator.get("redesign_allowed") is False
        and evaluator.get("release_allowed") is False
        and evaluator.get("next_recommended_research_key") == EXPECTED_NEXT_RESEARCH_KEY
    )

    queue_ok = (
        next_queue.get("queue_status") == "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_NEXT_QUEUE_READY"
        and next_queue.get("top_next_research_key") == EXPECTED_NEXT_RESEARCH_KEY
        and selected.get("next_module_recommendation") == "edge_factory_os_market_state_transition_contract_builder_v1.py"
    )

    state_ok = (
        failed_deep_state.get("state_status") == "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_FAILED_ROUTE_CLOSED"
        and failed_deep_state.get("route_closed") is True
        and failed_deep_state.get("release_allowed") is False
    )

    framework_ok = framework_status.get("panel_status") == "FRAMEWORK_STATUS_PANEL_READY_POLICY_LOCKED_NO_ACTUAL_SIGNAL"
    true_panel_ok = bool(true_panel_state.get("false_positive_methodology_repaired")) and not bool(true_panel_state.get("actual_signal_present"))
    policy_active = policy.get("policy_status") == "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE"
    validator_pass = bool(validation_state.get("validator_pass"))
    guard_pass = bool(guard_feed.get("guard_pass"))
    runtime_blocks_plugin = runtime_state.get("plugin_expansion_allowed") is False
    source_panel_exists = SOURCE_PANEL_PATH.exists()

    block_hashes = blocked_hashes(blocklist)

    plugin_config = build_plugin_config(
        policy=policy,
        guard_feed=guard_feed,
        failed_deep_state=failed_deep_state,
        evaluator=evaluator,
    )

    source_failed_route_hash = failed_deep_state.get("route_hash") or evaluator.get("route_hash")
    source_failed_decision_class = failed_deep_state.get("decision_class") or evaluator.get("decision_class")
    source_failed_gates = failed_deep_state.get("failed_gate_keys") or evaluator.get("failed_gate_keys")

    route_hash_payload = {
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "plugin_key": PLUGIN_KEY,
        "policy_hash": policy.get("policy_hash"),
        "source_failed_route_hash": source_failed_route_hash,
        "source_failed_decision_class": source_failed_decision_class,
        "source_failed_gates": source_failed_gates,
        "state_feature_groups": [x.get("group_key") for x in plugin_config["state_feature_groups"]],
        "transition_methods": plugin_config["transition_methods"],
        "negative_controls": plugin_config["negative_controls"],
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "release_allowed": False,
        "material_difference": "market_state_transition_not_single_feature_anomaly",
    }

    route_hash = stable_hash(route_hash_payload)
    route_hash_blocked = route_hash in block_hashes

    prerequisite_pass = (
        evaluator_ok
        and queue_ok
        and state_ok
        and framework_ok
        and true_panel_ok
        and policy_active
        and validator_pass
        and guard_pass
        and runtime_blocks_plugin
        and source_panel_exists
        and not route_hash_blocked
    )

    contract_hash = stable_hash({
        "route_hash": route_hash,
        "research_key": RESEARCH_KEY,
        "plugin_key": PLUGIN_KEY,
        "policy_hash": policy.get("policy_hash"),
        "lesson_count": len(extract_lessons(lesson_index)),
        "blocked_route_count": len(extract_blocked_routes(blocklist)),
        "state_feature_group_count": len(plugin_config["state_feature_groups"]),
        "transition_method_count": len(plugin_config["transition_methods"]),
        "negative_control_count": len(plugin_config["negative_controls"]),
    })

    contract_id = f"MARKET_STATE_TRANSITION_CONTRACT_V1_{contract_hash}_{timestamp_compact()}"

    if prerequisite_pass:
        builder_status = "MARKET_STATE_TRANSITION_CONTRACT_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_MARKET_STATE_TRANSITION_RUNNER"
        reason = (
            f"source_failed_route_closed=True; selected={EXPECTED_NEXT_RESEARCH_KEY}; "
            f"route_hash_blocked=False; materially_different=True; release_allowed=False"
        )
        next_module = NEXT_MODULE
        return_code = 0
    else:
        builder_status = "MARKET_STATE_TRANSITION_CONTRACT_BLOCKED_PREREQUISITE_NOT_MET"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_MARKET_STATE_TRANSITION_CONTRACT_PREREQUISITES_NO_RELEASE"
        reason = (
            f"evaluator_ok={evaluator_ok}; queue_ok={queue_ok}; state_ok={state_ok}; "
            f"framework_ok={framework_ok}; true_panel_ok={true_panel_ok}; policy_active={policy_active}; "
            f"validator_pass={validator_pass}; guard_pass={guard_pass}; runtime_blocks_plugin={runtime_blocks_plugin}; "
            f"source_panel_exists={source_panel_exists}; route_hash_blocked={route_hash_blocked}"
        )
        next_module = None
        return_code = 2

    hard_requirements_for_runner = [
        "read full source panel parquet",
        "consume failed anomaly deep validation state",
        "consume framework status panel",
        "consume true source-panel null baseline state",
        "consume research gate policy",
        "consume data quality guard feed",
        "consume route blocklist",
        "prove route hash not blocked",
        "prove material difference from failed source-panel anomaly route",
        "exclude future return/pnl/outcome/label features from state discovery",
        "build outcome-agnostic market state features",
        "build state transition summaries across canonical 12 months",
        "run negative controls",
        "run true source-panel null replay before signal claim",
        "produce policy gate table",
        "keep plugin expansion false",
        "keep candidate/family/runtime/capital/live false",
    ]

    contract = {
        "contract_name": "edge_factory_os_market_state_transition_contract_v1",
        "created_at_utc": utc_now_iso(),
        "contract_status": "MARKET_STATE_TRANSITION_CONTRACT_READY" if prerequisite_pass else "MARKET_STATE_TRANSITION_CONTRACT_BLOCKED",
        "contract_id": contract_id if prerequisite_pass else None,
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "route_hash_payload": route_hash_payload,
        "route_hash_blocked": route_hash_blocked,
        "source_failed_route_hash": source_failed_route_hash,
        "source_failed_decision_class": source_failed_decision_class,
        "source_failed_gates": source_failed_gates,
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "plugin_key": PLUGIN_KEY,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "next_module": next_module,
        "policy_hash": policy.get("policy_hash"),
        "source_panel_path": str(SOURCE_PANEL_PATH),
        "source_panel_exists": source_panel_exists,
        "state_feature_group_count": len(plugin_config["state_feature_groups"]),
        "transition_method_count": len(plugin_config["transition_methods"]),
        "negative_control_count": len(plugin_config["negative_controls"]),
        "state_feature_groups": plugin_config["state_feature_groups"],
        "transition_methods": plugin_config["transition_methods"],
        "negative_controls": plugin_config["negative_controls"],
        "transition_preview_requirements": plugin_config["transition_preview_requirements"],
        "gate_caps": plugin_config["gate_caps"],
        "hard_requirements_for_runner": hard_requirements_for_runner,
        "required_runner_outputs": plugin_config["required_runner_outputs"],
        "release_allowed": False,
        "plugin_expansion_allowed": False,
        "source_artifacts": {
            "evaluator_json": str(EVALUATOR_JSON),
            "next_queue_json": str(NEXT_QUEUE_JSON),
            "failed_deep_state_json": str(FAILED_DEEP_STATE_JSON),
            "framework_status_json": str(FRAMEWORK_STATUS_JSON),
            "true_panel_state_json": str(TRUE_PANEL_STATE_JSON),
            "policy_json": str(POLICY_JSON),
            "policy_runtime_state_json": str(POLICY_RUNTIME_STATE_JSON),
            "policy_validation_state_json": str(POLICY_VALIDATION_STATE_JSON),
            "guard_feed_json": str(GUARD_FEED_JSON),
            "lesson_index_path": str(LESSON_INDEX_PATH),
            "blocklist_path": str(BLOCKLIST_PATH),
        },
        "downstream_rules": {
            "if_transition_preview_found": "build evaluator/deep validation contract; no candidate release",
            "if_no_transition_preview": "close route and queue next policy-locked direction",
            "if_true_null_or_negative_control_fails": "close route and lesson/blocklist",
            "release_allowed_from_this_contract": False,
        },
        "release_gate_feed": {
            "MARKET_STATE_TRANSITION_CONTRACT_READY": prerequisite_pass,
            "FAILED_ANOMALY_DEEP_VALIDATION_STATE_CONSUMED": True,
            "FRAMEWORK_STATUS_CONSUMED": True,
            "TRUE_SOURCE_PANEL_STATE_CONSUMED": True,
            "RESEARCH_GATE_POLICY_CONSUMED": True,
            "DATA_QUALITY_GUARD_CONSUMED": True,
            "ROUTE_BLOCKLIST_CONSUMED": True,
            "CONTRACT_ROUTE_HASH_BLOCKED": route_hash_blocked,
            "PLUGIN_EXPANSION_ALLOWED_FROM_THIS_CONTRACT": False,
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
        **SAFETY_FLAGS,
    }

    write_json(REPO_PLUGIN_JSON, plugin_config)
    write_json(REPO_CONTRACT_JSON, contract)
    write_text(REPO_CONTRACT_TXT, build_contract_text(contract))

    result = {
        "builder_name": "edge_factory_os_market_state_transition_contract_builder_v1",
        "created_at_utc": utc_now_iso(),
        "builder_status": builder_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "contract_id": contract.get("contract_id"),
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "route_hash_blocked": route_hash_blocked,
        "source_failed_route_hash": source_failed_route_hash,
        "source_failed_decision_class": source_failed_decision_class,
        "source_failed_gates": source_failed_gates,
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "plugin_key": PLUGIN_KEY,
        "policy_hash": policy.get("policy_hash"),
        "source_panel_path": str(SOURCE_PANEL_PATH),
        "source_panel_exists": source_panel_exists,
        "state_feature_group_count": len(plugin_config["state_feature_groups"]),
        "transition_method_count": len(plugin_config["transition_methods"]),
        "negative_control_count": len(plugin_config["negative_controls"]),
        "release_allowed": False,
        "plugin_expansion_allowed": False,
        "next_module": next_module,
        "contract": contract,
        "plugin_config": plugin_config,
        "release_gate_feed": contract["release_gate_feed"],
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "repo_plugin_json": str(REPO_PLUGIN_JSON),
        "repo_contract_json": str(REPO_CONTRACT_JSON),
        "repo_contract_txt": str(REPO_CONTRACT_TXT),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_summary_text(result))
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
