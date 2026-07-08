#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Source Panel Anomaly Discovery Contract Builder v1

Purpose:
- Consume Policy Locked New Research Direction Queue v1.
- Consume Framework Status Panel v1.
- Consume True Source Panel Empirical Null Baseline State v1.
- Consume research gate policy / validator / guard / blocklist.
- Build a materially different source-panel anomaly discovery contract.
- Keep plugin expansion blocked.
- Keep candidate/family/runtime/capital/live/real-order actions blocked.

This builder does NOT:
- run anomaly discovery
- run strategy research
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

POLICY_LOCKED_QUEUE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "queues"
    / "policy_locked_new_research_direction_queue_v1.json"
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

REPO_PLUGIN_JSON = PLUGIN_DIR / "source_panel_anomaly_discovery_with_true_nulls_plugin_v1.json"
REPO_CONTRACT_JSON = CONTRACT_DIR / "source_panel_anomaly_discovery_contract_v1.json"
REPO_CONTRACT_TXT = CONTRACT_DIR / "source_panel_anomaly_discovery_contract_v1.txt"

OUT_DIR = BASE_DIR / "edge_factory_os_source_panel_anomaly_discovery_contract"
OUT_JSON = OUT_DIR / "source_panel_anomaly_discovery_contract_latest.json"
OUT_TXT = OUT_DIR / "source_panel_anomaly_discovery_contract_latest.txt"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

EXPECTED_SELECTED_RESEARCH_KEY = "RD6_01_SOURCE_PANEL_ANOMALY_DISCOVERY_WITH_TRUE_NULLS"
EXPECTED_SELECTED_MODULE = "edge_factory_os_source_panel_anomaly_discovery_contract_builder_v1.py"

RESEARCH_KEY = "SOURCE_PANEL_ANOMALY_DISCOVERY_WITH_TRUE_NULLS_V1"
DIRECTION_QUEUE_KEY = "RD6_01_SOURCE_PANEL_ANOMALY_DISCOVERY_WITH_TRUE_NULLS"
PLUGIN_KEY = "SOURCE_PANEL_ANOMALY_DISCOVERY_WITH_TRUE_NULLS_PLUGIN_V1"
NEXT_MODULE = "edge_factory_os_source_panel_anomaly_discovery_runner_v1.py"

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


def count_lessons(obj: Any) -> int:
    if isinstance(obj, dict) and isinstance(obj.get("lessons"), list):
        return len(obj["lessons"])
    if isinstance(obj, list):
        return len([x for x in obj if isinstance(x, dict)])
    return 0


def count_blocked_routes(obj: Any) -> int:
    return len(extract_blocked_routes(obj))


def selected_direction_from_queue(queue: Dict[str, Any]) -> Dict[str, Any]:
    selected = queue.get("selected_direction")
    if isinstance(selected, dict):
        return selected

    items = queue.get("next_direction_queue")
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict) and item.get("selected"):
                return item
        valid = [x for x in items if isinstance(x, dict)]
        if valid:
            return sorted(valid, key=lambda x: int(x.get("priority", 0)), reverse=True)[0]

    return {}


def build_plugin_config(policy: Dict[str, Any], guard_feed: Dict[str, Any], selected: Dict[str, Any]) -> Dict[str, Any]:
    rules = policy.get("enforced_gate_rules")
    if not isinstance(rules, dict):
        rules = {}

    required_guard_keys = [
        x.get("guard_key")
        for x in guard_feed.get("mandatory_future_research_requirements", [])
        if isinstance(x, dict) and x.get("guard_key")
    ]

    anomaly_discovery_axes = [
        "cross_sectional_return_distribution_anomaly",
        "symbol_month_volatility_compression_expansion",
        "range_volume_dislocation",
        "coin_vs_market_residual_anomaly",
        "liquidity_regime_shift",
        "market_beta_instability",
        "tail_event_clustering",
        "symbol_cohort_divergence",
        "intramonth_state_transition",
        "outcome_agnostic_event_motif",
    ]

    negative_controls = [
        "symbol_shuffle_control",
        "month_shuffle_control",
        "time_block_shuffle_control",
        "feature_label_permutation_control",
        "side_flip_control",
        "market_return_permutation_control",
        "volume_bucket_shuffle_control",
        "range_bucket_shuffle_control",
    ]

    return {
        "plugin_key": PLUGIN_KEY,
        "plugin_type": "READ_ONLY_SOURCE_PANEL_ANOMALY_DISCOVERY_WITH_TRUE_NULLS",
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "selected_queue_research_key": selected.get("research_key"),
        "selected_queue_route_hash": selected.get("route_hash"),
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "source_panel_path": str(SOURCE_PANEL_PATH),
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
        "anomaly_discovery_axes": anomaly_discovery_axes,
        "negative_controls": negative_controls,
        "minimum_axis_count": 6,
        "minimum_negative_control_count": 5,
        "minimum_empirical_null_runs": max(1000, int(rules.get("minimum_permutation_runs") or 1000)),
        "preferred_empirical_null_runs": max(2000, int(rules.get("minimum_permutation_runs") or 1000) * 2),
        "gate_caps": {
            "max_allowed_strict_12_any_random_hit_rate": min(0.01, float(rules.get("max_allowed_strict_12_any_random_hit_rate") or 0.01)),
            "max_allowed_null_adjusted_any_random_hit_rate": min(0.005, float(rules.get("max_allowed_null_adjusted_any_random_hit_rate") or 0.005)),
            "empirical_p_value_required_lte": min(0.01, float(rules.get("empirical_p_value_required_lte") or 0.01)),
            "minimum_actual_vs_null_margin_bps": float(rules.get("minimum_actual_vs_null_margin_bps") or 2500.0),
        },
        "required_guard_keys": required_guard_keys,
        "forbidden_inputs": [
            "future_return_as_feature",
            "future_pnl_as_feature",
            "manual_symbol_whitelist",
            "manual_month_blacklist",
            "post_outcome_filtering",
            "blocked_route_hash_reuse",
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
            "source_panel_schema_report",
            "source_panel_month_symbol_coverage_report",
            "anomaly_axis_inventory",
            "negative_control_inventory",
            "outcome_agnostic_anomaly_score_table",
            "true_null_replay_summary",
            "policy_gate_pass_fail_table",
            "material_difference_report",
            "lesson_blocklist_consumption_report",
            "latest_json",
            "latest_txt",
            "csv_outputs",
        ],
        **SAFETY_FLAGS,
    }


def build_contract_text(contract: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS SOURCE PANEL ANOMALY DISCOVERY CONTRACT v1")
    lines.append("=" * 100)

    for key in [
        "contract_status",
        "allowed_scope",
        "next_action",
        "contract_id",
        "contract_hash",
        "route_hash",
        "selected_queue_route_hash",
        "selected_queue_route_hash_blocked",
        "research_key",
        "direction_queue_key",
        "plugin_key",
        "policy_hash",
        "source_panel_path",
        "source_panel_exists",
        "framework_ready",
        "false_positive_methodology_repaired",
        "actual_signal_present",
        "minimum_empirical_null_runs",
        "anomaly_axis_count",
        "negative_control_count",
        "next_module",
    ]:
        lines.append(f"{key}: {contract.get(key)}")

    lines.append("")
    lines.append("ANOMALY DISCOVERY AXES")
    lines.append("-" * 100)
    for item in contract.get("anomaly_discovery_axes", []):
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
    for k, v in SAFETY_FLAGS.items():
        lines.append(f"{k}: {v}")

    return "\n".join(lines)


def build_summary_text(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS SOURCE PANEL ANOMALY DISCOVERY CONTRACT BUILDER v1")
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
        "selected_queue_route_hash",
        "selected_queue_route_hash_blocked",
        "research_key",
        "direction_queue_key",
        "plugin_key",
        "policy_hash",
        "source_panel_path",
        "source_panel_exists",
        "framework_ready",
        "false_positive_methodology_repaired",
        "actual_signal_present",
        "plugin_expansion_allowed",
        "anomaly_axis_count",
        "negative_control_count",
        "next_module",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        lines.append(f"{k}: {v}")

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
    print("EDGE FACTORY OS SOURCE PANEL ANOMALY DISCOVERY CONTRACT BUILDER v1")
    print("=" * 100)
    print(f"builder_status: {result.get('builder_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"contract_id: {result.get('contract_id')}")
    print(f"contract_hash: {result.get('contract_hash')}")
    print(f"route_hash: {result.get('route_hash')}")
    print(f"selected_queue_route_hash: {result.get('selected_queue_route_hash')}")
    print(f"selected_queue_route_hash_blocked: {result.get('selected_queue_route_hash_blocked')}")
    print(f"research_key: {result.get('research_key')}")
    print(f"direction_queue_key: {result.get('direction_queue_key')}")
    print(f"plugin_key: {result.get('plugin_key')}")
    print(f"policy_hash: {result.get('policy_hash')}")
    print(f"source_panel_exists: {result.get('source_panel_exists')}")
    print(f"framework_ready: {result.get('framework_ready')}")
    print(f"false_positive_methodology_repaired: {result.get('false_positive_methodology_repaired')}")
    print(f"actual_signal_present: {result.get('actual_signal_present')}")
    print(f"plugin_expansion_allowed: {result.get('plugin_expansion_allowed')}")
    print(f"anomaly_axis_count: {result.get('anomaly_axis_count')}")
    print(f"negative_control_count: {result.get('negative_control_count')}")
    print(f"next_module: {result.get('next_module')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"CONTRACT JSON: {result.get('repo_contract_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PLUGIN_DIR.mkdir(parents=True, exist_ok=True)
    CONTRACT_DIR.mkdir(parents=True, exist_ok=True)

    queue = load_json(POLICY_LOCKED_QUEUE_JSON, default={})
    framework_status = load_json(FRAMEWORK_STATUS_JSON, default={})
    true_panel_state = load_json(TRUE_PANEL_STATE_JSON, default={})
    policy = load_json(POLICY_JSON, default={})
    runtime_state = load_json(POLICY_RUNTIME_STATE_JSON, default={})
    validation_state = load_json(POLICY_VALIDATION_STATE_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})
    lesson_index = load_json(LESSON_INDEX_PATH, default={})
    blocklist = load_json(BLOCKLIST_PATH, default={})

    selected = selected_direction_from_queue(queue)

    selected_research_key = selected.get("research_key") or queue.get("selected_research_key")
    selected_next_module = selected.get("next_module_recommendation") or queue.get("selected_next_module")
    selected_route_hash = selected.get("route_hash") or queue.get("selected_route_hash")

    block_hashes = blocked_hashes(blocklist)
    selected_queue_route_hash_blocked = bool(selected_route_hash and str(selected_route_hash) in block_hashes)

    policy_active = policy.get("policy_status") == "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE"
    guard_pass = bool(guard_feed.get("guard_pass"))
    validator_pass = bool(validation_state.get("validator_pass"))
    runtime_blocks_plugin = runtime_state.get("plugin_expansion_allowed") is False

    framework_ready = framework_status.get("panel_status") == "FRAMEWORK_STATUS_PANEL_READY_POLICY_LOCKED_NO_ACTUAL_SIGNAL"
    false_positive_methodology_repaired = bool(true_panel_state.get("false_positive_methodology_repaired"))
    actual_signal_present = bool(true_panel_state.get("actual_signal_present"))

    plugin_expansion_allowed = False
    source_panel_exists = SOURCE_PANEL_PATH.exists()

    plugin_config = build_plugin_config(policy, guard_feed, selected)

    route_hash_payload = {
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "plugin_key": PLUGIN_KEY,
        "selected_queue_research_key": selected_research_key,
        "selected_queue_route_hash": selected_route_hash,
        "policy_hash": policy.get("policy_hash"),
        "source_panel_path": str(SOURCE_PANEL_PATH),
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "anomaly_discovery_axes": plugin_config["anomaly_discovery_axes"],
        "negative_controls": plugin_config["negative_controls"],
        "false_positive_methodology_repaired": false_positive_methodology_repaired,
        "actual_signal_present": actual_signal_present,
    }
    route_hash = stable_hash(route_hash_payload)
    route_hash_blocked = route_hash in block_hashes

    prerequisite_pass = (
        selected_research_key == EXPECTED_SELECTED_RESEARCH_KEY
        and selected_next_module == EXPECTED_SELECTED_MODULE
        and not selected_queue_route_hash_blocked
        and not route_hash_blocked
        and framework_ready
        and policy_active
        and guard_pass
        and validator_pass
        and runtime_blocks_plugin
        and false_positive_methodology_repaired
        and not actual_signal_present
        and plugin_expansion_allowed is False
        and source_panel_exists
    )

    contract_hash = stable_hash({
        "route_hash": route_hash,
        "selected_queue_route_hash": selected_route_hash,
        "research_key": RESEARCH_KEY,
        "plugin_key": PLUGIN_KEY,
        "policy_hash": policy.get("policy_hash"),
        "lesson_count": count_lessons(lesson_index),
        "blocked_route_count": count_blocked_routes(blocklist),
        "anomaly_axis_count": len(plugin_config["anomaly_discovery_axes"]),
        "negative_control_count": len(plugin_config["negative_controls"]),
    })

    contract_id = f"SOURCE_PANEL_ANOMALY_DISCOVERY_CONTRACT_V1_{contract_hash}_{timestamp_compact()}"

    if prerequisite_pass:
        builder_status = "SOURCE_PANEL_ANOMALY_DISCOVERY_CONTRACT_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_SOURCE_PANEL_ANOMALY_DISCOVERY_RUNNER"
        reason = (
            f"selected={selected_research_key}; framework_ready=True; true_null_state_consumed=True; "
            f"source_panel_exists=True; route_hash_blocked=False; plugin_expansion_allowed=False"
        )
        next_module = NEXT_MODULE
        return_code = 0
    else:
        builder_status = "SOURCE_PANEL_ANOMALY_DISCOVERY_CONTRACT_BLOCKED_PREREQUISITE_NOT_MET"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_SOURCE_PANEL_ANOMALY_CONTRACT_PREREQUISITES_NO_RELEASE"
        reason = (
            f"selected_research_key={selected_research_key}; selected_next_module={selected_next_module}; "
            f"selected_route_hash={selected_route_hash}; selected_queue_route_hash_blocked={selected_queue_route_hash_blocked}; "
            f"route_hash_blocked={route_hash_blocked}; framework_ready={framework_ready}; policy_active={policy_active}; "
            f"guard_pass={guard_pass}; validator_pass={validator_pass}; runtime_blocks_plugin={runtime_blocks_plugin}; "
            f"false_positive_methodology_repaired={false_positive_methodology_repaired}; actual_signal_present={actual_signal_present}; "
            f"source_panel_exists={source_panel_exists}"
        )
        next_module = None
        return_code = 2

    hard_requirements_for_runner = [
        "read full source panel parquet",
        "validate time/symbol/schema/month coverage",
        "build canonical 12 policy months",
        "run outcome-agnostic anomaly discovery axes",
        "run negative controls",
        "run true source-panel empirical null before any signal claim",
        "consume research gate policy",
        "consume data quality guard feed",
        "consume true source-panel null state",
        "consume route blocklist",
        "prove material difference from blocked routes",
        "keep plugin expansion false",
        "keep candidate/family/runtime/capital/live false",
    ]

    contract = {
        "contract_name": "edge_factory_os_source_panel_anomaly_discovery_contract_v1",
        "created_at_utc": utc_now_iso(),
        "contract_status": "SOURCE_PANEL_ANOMALY_DISCOVERY_CONTRACT_READY" if prerequisite_pass else "SOURCE_PANEL_ANOMALY_DISCOVERY_CONTRACT_BLOCKED",
        "contract_id": contract_id if prerequisite_pass else None,
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "route_hash_payload": route_hash_payload,
        "route_hash_blocked": route_hash_blocked,
        "selected_queue_route_hash": selected_route_hash,
        "selected_queue_route_hash_blocked": selected_queue_route_hash_blocked,
        "selected_queue_research_key": selected_research_key,
        "selected_queue_next_module": selected_next_module,
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
        "framework_ready": framework_ready,
        "policy_active": policy_active,
        "guard_pass": guard_pass,
        "validator_pass": validator_pass,
        "runtime_blocks_plugin": runtime_blocks_plugin,
        "false_positive_methodology_repaired": false_positive_methodology_repaired,
        "actual_signal_present": actual_signal_present,
        "plugin_expansion_allowed": False,
        "minimum_empirical_null_runs": plugin_config["minimum_empirical_null_runs"],
        "preferred_empirical_null_runs": plugin_config["preferred_empirical_null_runs"],
        "anomaly_axis_count": len(plugin_config["anomaly_discovery_axes"]),
        "negative_control_count": len(plugin_config["negative_controls"]),
        "anomaly_discovery_axes": plugin_config["anomaly_discovery_axes"],
        "negative_controls": plugin_config["negative_controls"],
        "gate_caps": plugin_config["gate_caps"],
        "hard_requirements_for_runner": hard_requirements_for_runner,
        "required_runner_outputs": plugin_config["required_runner_outputs"],
        "source_artifacts": {
            "policy_locked_queue_json": str(POLICY_LOCKED_QUEUE_JSON),
            "framework_status_json": str(FRAMEWORK_STATUS_JSON),
            "true_panel_state_json": str(TRUE_PANEL_STATE_JSON),
            "policy_json": str(POLICY_JSON),
            "policy_validation_state_json": str(POLICY_VALIDATION_STATE_JSON),
            "guard_feed_json": str(GUARD_FEED_JSON),
            "lesson_index_path": str(LESSON_INDEX_PATH),
            "blocklist_path": str(BLOCKLIST_PATH),
        },
        "downstream_rules": {
            "if_anomaly_discovery_finds_preview": "build evaluator/deep validation contract; no candidate release",
            "if_no_anomaly_discovery_signal": "close route and queue next policy-locked direction",
            "if_policy_guard_or_blocklist_not_consumed": "block output",
            "release_allowed_from_this_contract": False,
        },
        "release_gate_feed": {
            "SOURCE_PANEL_ANOMALY_DISCOVERY_CONTRACT_READY": prerequisite_pass,
            "POLICY_LOCKED_QUEUE_CONSUMED": True,
            "FRAMEWORK_STATUS_CONSUMED": True,
            "TRUE_SOURCE_PANEL_STATE_CONSUMED": True,
            "RESEARCH_GATE_POLICY_CONSUMED": True,
            "DATA_QUALITY_GUARD_CONSUMED": True,
            "ROUTE_BLOCKLIST_CONSUMED": True,
            "SELECTED_ROUTE_HASH_BLOCKED": selected_queue_route_hash_blocked,
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
        "builder_name": "edge_factory_os_source_panel_anomaly_discovery_contract_builder_v1",
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
        "selected_queue_route_hash": selected_route_hash,
        "selected_queue_route_hash_blocked": selected_queue_route_hash_blocked,
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "plugin_key": PLUGIN_KEY,
        "policy_hash": policy.get("policy_hash"),
        "source_panel_path": str(SOURCE_PANEL_PATH),
        "source_panel_exists": source_panel_exists,
        "framework_ready": framework_ready,
        "policy_active": policy_active,
        "guard_pass": guard_pass,
        "validator_pass": validator_pass,
        "runtime_blocks_plugin": runtime_blocks_plugin,
        "false_positive_methodology_repaired": false_positive_methodology_repaired,
        "actual_signal_present": actual_signal_present,
        "plugin_expansion_allowed": False,
        "anomaly_axis_count": len(plugin_config["anomaly_discovery_axes"]),
        "negative_control_count": len(plugin_config["negative_controls"]),
        "minimum_empirical_null_runs": plugin_config["minimum_empirical_null_runs"],
        "preferred_empirical_null_runs": plugin_config["preferred_empirical_null_runs"],
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
