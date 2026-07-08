#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - True Source Panel Empirical Null Baseline Contract Builder v1

Purpose:
- Consume Null Baseline Method Repair Evaluator v1.
- Consume active research gate enforcement policy.
- Consume null baseline method repair state.
- Build a true source-panel empirical null baseline contract.
- Require real source panel row/month replay instead of summary-row/proxy replay.
- Keep plugin expansion blocked.
- Keep all candidate/family/runtime/capital/live/real-order actions blocked.

This builder does NOT:
- run the null baseline
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
from typing import Any, Dict, List, Optional


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

REPAIR_EVALUATOR_JSON = (
    BASE_DIR
    / "edge_factory_os_null_baseline_method_repair_evaluator"
    / "null_baseline_method_repair_evaluator_latest.json"
)

REPAIR_NEXT_QUEUE_JSON = (
    BASE_DIR
    / "edge_factory_os_null_baseline_method_repair_evaluator"
    / "null_baseline_method_repair_next_queue_latest.json"
)

REPAIR_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "null_baseline_method_repair_state_v1.json"
)

METHOD_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "null_baseline_method_state_v1.json"
)

POLICY_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_enforcement_policy_v1.json"
)

VALIDATION_STATE_JSON = (
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

REPO_PLUGIN_JSON = PLUGIN_DIR / "true_source_panel_empirical_null_baseline_plugin_v1.json"
REPO_CONTRACT_JSON = CONTRACT_DIR / "true_source_panel_empirical_null_baseline_contract_v1.json"
REPO_CONTRACT_TXT = CONTRACT_DIR / "true_source_panel_empirical_null_baseline_contract_v1.txt"

OUT_DIR = BASE_DIR / "edge_factory_os_research_direction_contracts"
OUT_JSON = OUT_DIR / "true_source_panel_empirical_null_baseline_contract_latest.json"
OUT_TXT = OUT_DIR / "true_source_panel_empirical_null_baseline_contract_latest.txt"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

REQUIRED_EVALUATOR_STATUS = "NULL_BASELINE_METHOD_REPAIR_EVALUATOR_REPAIR_V1_FAILED_TRUE_SOURCE_PANEL_REQUIRED"
REQUIRED_DECISION_CLASS = "REPAIRED_METHOD_POLICY_GATES_FAIL_TRUE_SOURCE_PANEL_REPLAY_REQUIRED"
REQUIRED_NEXT_RESEARCH_KEY = "RD5_06B_TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_CONTRACT"

RESEARCH_KEY = "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_V1"
DIRECTION_QUEUE_KEY = "RD5_06B_TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_CONTRACT"
PLUGIN_KEY = "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_PLUGIN_V1"
NEXT_MODULE = "edge_factory_os_true_source_panel_empirical_null_baseline_runner_v1.py"

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


def extract_top_queue(queue: Dict[str, Any], fallback: Dict[str, Any]) -> Dict[str, Any]:
    items = queue.get("next_direction_queue")
    if isinstance(items, list) and items:
        valid = [x for x in items if isinstance(x, dict)]
        if valid:
            return sorted(valid, key=lambda x: int(x.get("priority", 0)), reverse=True)[0]
    return {
        "research_key": fallback.get("next_recommended_research_key"),
        "next_module_recommendation": fallback.get("next_module"),
        "priority": 100,
    }


def extract_lessons_count(obj: Any) -> int:
    if isinstance(obj, dict) and isinstance(obj.get("lessons"), list):
        return len(obj["lessons"])
    if isinstance(obj, list):
        return len([x for x in obj if isinstance(x, dict)])
    return 0


def extract_blocked_routes(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get("blocked_routes"), list):
        return [x for x in obj["blocked_routes"] if isinstance(x, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def route_hash_blocked(route_hash: str, blocked_routes: List[Dict[str, Any]]) -> bool:
    for item in blocked_routes:
        if str(item.get("route_hash")) == str(route_hash):
            return True
    return False


def build_plugin_config(policy: Dict[str, Any], guard_feed: Dict[str, Any]) -> Dict[str, Any]:
    rules = policy.get("enforced_gate_rules")
    if not isinstance(rules, dict):
        rules = {}

    required_guard_keys = [
        x.get("guard_key")
        for x in guard_feed.get("mandatory_future_research_requirements", [])
        if isinstance(x, dict) and x.get("guard_key")
    ]

    replay_methods = [
        "panel_row_month_block_bootstrap",
        "panel_within_month_symbol_shuffle",
        "panel_symbol_holdout_replay",
        "panel_month_holdout_replay",
        "panel_time_block_bootstrap",
        "panel_negative_control_replay",
        "panel_cost_stress_replay",
        "panel_liquidity_bucket_shuffle",
        "panel_volatility_bucket_shuffle",
        "panel_side_flip_replay",
        "panel_feature_label_permutation",
        "panel_entry_time_permutation",
    ]

    return {
        "plugin_key": PLUGIN_KEY,
        "plugin_type": "READ_ONLY_TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE",
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "must_consume_guard_feed": True,
        "must_consume_research_gate_policy": True,
        "must_consume_repair_state": True,
        "must_use_true_source_panel_rows_or_month_buckets": True,
        "must_not_use_summary_rows_only": True,
        "must_not_use_synthetic_month_generation_only": True,
        "must_not_reopen_blocked_routes": True,
        "plugin_expansion_allowed": False,
        "source_panel_path": str(SOURCE_PANEL_PATH),
        "source_panel_requirements": {
            "required_format": "parquet",
            "minimum_row_count": 1000000,
            "minimum_symbol_count": 200,
            "expected_symbol_count": 285,
            "required_time_span_days_min": 300,
            "required_columns": [
                "time",
                "symbol",
                "open",
                "high",
                "low",
                "close",
                "entry_vol_quote",
                "entry_range_bps",
                "coin_ret3_bps",
                "coin_ret6_bps",
                "mkt_ret3_bps",
                "mkt_ret6_bps",
            ],
            "canonical_policy_month_count": 12,
            "allow_raw_calendar_month_count": 13,
        },
        "empirical_replay_goal": (
            "Use the full source panel row/month structure to estimate null false-positive rates, "
            "instead of using diagnostic/control summary rows."
        ),
        "replay_methods": replay_methods,
        "minimum_empirical_replay_runs": max(1000, int(rules.get("minimum_permutation_runs") or 1000)),
        "preferred_empirical_replay_runs": max(2000, int(rules.get("minimum_permutation_runs") or 1000) * 2),
        "required_replay_method_count": 8,
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
            "synthetic_month_generation_only",
            "summary_row_only_replay",
            "proxy_only_null_model",
            "blocked_route_hash_reuse",
            "loose_null_gate_reuse",
        ],
        "required_runner_outputs": [
            "source_panel_schema_report",
            "source_panel_month_symbol_coverage_report",
            "policy_consumption_report",
            "guard_consumption_report",
            "repair_state_consumption_report",
            "panel_replay_method_inventory",
            "panel_empirical_replay_run_summary",
            "panel_empirical_false_positive_summary",
            "panel_empirical_policy_gate_pass_fail_table",
            "panel_empirical_p_value_table",
            "method_repair_recommendation",
            "latest_json",
            "latest_txt",
            "csv_outputs",
        ],
        "candidate_generation_allowed": False,
        "candidate_contract_allowed": False,
        "family_release_allowed": False,
        "promotion_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
    }


def build_contract_text(contract: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS TRUE SOURCE PANEL EMPIRICAL NULL BASELINE CONTRACT v1")
    lines.append("=" * 100)

    for key in [
        "contract_status",
        "allowed_scope",
        "next_action",
        "contract_id",
        "contract_hash",
        "route_hash",
        "route_hash_blocked",
        "research_key",
        "direction_queue_key",
        "plugin_key",
        "policy_hash",
        "repair_state",
        "strict_policy_key",
        "canonical_policy_month_count",
        "source_panel_path",
        "source_panel_exists",
        "minimum_empirical_replay_runs",
        "required_replay_method_count",
        "replay_method_count",
        "next_module",
    ]:
        lines.append(f"{key}: {contract.get(key)}")

    lines.append("")
    lines.append("REPLAY METHODS")
    lines.append("-" * 100)
    for item in contract.get("replay_methods", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("SOURCE PANEL REQUIREMENTS")
    lines.append("-" * 100)
    lines.append(json.dumps(contract.get("source_panel_requirements", {}), indent=2, ensure_ascii=False))

    lines.append("")
    lines.append("GATE CAPS")
    lines.append("-" * 100)
    for k, v in contract.get("gate_caps", {}).items():
        lines.append(f"{k}: {v}")

    lines.append("")
    lines.append("REQUIRED RUNNER OUTPUTS")
    lines.append("-" * 100)
    for item in contract.get("required_runner_outputs", []):
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
    lines.append("EDGE FACTORY OS TRUE SOURCE PANEL EMPIRICAL NULL BASELINE CONTRACT BUILDER v1")
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
        "research_key",
        "direction_queue_key",
        "plugin_key",
        "policy_hash",
        "repair_state",
        "source_panel_path",
        "source_panel_exists",
        "true_source_panel_replay_required",
        "minimum_empirical_replay_runs",
        "required_replay_method_count",
        "replay_method_count",
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
    print("EDGE FACTORY OS TRUE SOURCE PANEL EMPIRICAL NULL BASELINE CONTRACT BUILDER v1")
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
    print(f"research_key: {result.get('research_key')}")
    print(f"direction_queue_key: {result.get('direction_queue_key')}")
    print(f"plugin_key: {result.get('plugin_key')}")
    print(f"policy_hash: {result.get('policy_hash')}")
    print(f"repair_state: {result.get('repair_state')}")
    print(f"source_panel_path: {result.get('source_panel_path')}")
    print(f"source_panel_exists: {result.get('source_panel_exists')}")
    print(f"true_source_panel_replay_required: {result.get('true_source_panel_replay_required')}")
    print(f"minimum_empirical_replay_runs: {result.get('minimum_empirical_replay_runs')}")
    print(f"required_replay_method_count: {result.get('required_replay_method_count')}")
    print(f"replay_method_count: {result.get('replay_method_count')}")
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

    evaluator = load_json(REPAIR_EVALUATOR_JSON, default={})
    queue = load_json(REPAIR_NEXT_QUEUE_JSON, default={})
    repair_state = load_json(REPAIR_STATE_JSON, default={})
    method_state = load_json(METHOD_STATE_JSON, default={})
    policy = load_json(POLICY_JSON, default={})
    validation_state = load_json(VALIDATION_STATE_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})
    lesson_index = load_json(LESSON_INDEX_PATH, default={})
    blocklist = load_json(BLOCKLIST_PATH, default={})

    top_queue = extract_top_queue(queue, evaluator)
    top_key = top_queue.get("research_key") or evaluator.get("next_recommended_research_key")
    top_module = top_queue.get("next_module_recommendation") or evaluator.get("next_module")

    evaluator_status = evaluator.get("evaluator_status")
    decision_class = evaluator.get("decision_class")
    true_source_panel_replay_required = bool(evaluator.get("true_source_panel_replay_required"))
    plugin_expansion_allowed = bool(evaluator.get("plugin_expansion_allowed"))

    repair_state_status = repair_state.get("repair_state")
    method_state_status = method_state.get("method_state")
    policy_status = policy.get("policy_status")
    policy_hash = policy.get("policy_hash")
    validation_pass = bool(validation_state.get("validator_pass"))
    guard_pass = bool(guard_feed.get("guard_pass"))
    source_panel_exists = SOURCE_PANEL_PATH.exists()

    plugin_config = build_plugin_config(policy, guard_feed)

    route_hash_payload = {
        "research_key": RESEARCH_KEY,
        "plugin_key": PLUGIN_KEY,
        "policy_hash": policy_hash,
        "repair_state": repair_state_status,
        "method_state": method_state_status,
        "source_panel_path": str(SOURCE_PANEL_PATH),
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "replay_methods": plugin_config.get("replay_methods"),
        "minimum_empirical_replay_runs": plugin_config.get("minimum_empirical_replay_runs"),
        "source_panel_requirements": plugin_config.get("source_panel_requirements"),
    }

    route_hash = stable_hash(route_hash_payload)
    blocked_routes = extract_blocked_routes(blocklist)
    blocked = route_hash_blocked(route_hash, blocked_routes)

    prerequisite_pass = (
        evaluator_status == REQUIRED_EVALUATOR_STATUS
        and decision_class == REQUIRED_DECISION_CLASS
        and top_key == REQUIRED_NEXT_RESEARCH_KEY
        and true_source_panel_replay_required is True
        and plugin_expansion_allowed is False
        and policy_status == "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE"
        and validation_pass is True
        and guard_pass is True
        and source_panel_exists is True
        and blocked is False
    )

    contract_hash = stable_hash({
        "route_hash": route_hash,
        "research_key": RESEARCH_KEY,
        "plugin_key": PLUGIN_KEY,
        "policy_hash": policy_hash,
        "repair_state": repair_state_status,
        "source_panel_path": str(SOURCE_PANEL_PATH),
        "replay_method_count": len(plugin_config["replay_methods"]),
        "lessons_count": extract_lessons_count(lesson_index),
        "blocked_route_count": len(blocked_routes),
    })

    contract_id = f"TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_CONTRACT_V1_{contract_hash}_{timestamp_compact()}"

    if prerequisite_pass:
        builder_status = "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_CONTRACT_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_RUNNER"
        reason = (
            f"true_source_panel_replay_required=True; source_panel_exists=True; "
            f"empirical_replay_runs={plugin_config['minimum_empirical_replay_runs']}; "
            f"replay_methods={len(plugin_config['replay_methods'])}; route_hash_blocked=False"
        )
        next_module = NEXT_MODULE
        return_code = 0
    else:
        builder_status = "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_CONTRACT_BLOCKED_PREREQUISITE_NOT_MET"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_REPAIR_EVALUATOR_POLICY_GUARD_PANEL_OR_BLOCKLIST"
        reason = (
            f"evaluator_status={evaluator_status}; decision_class={decision_class}; top_key={top_key}; "
            f"top_module={top_module}; true_source_panel_replay_required={true_source_panel_replay_required}; "
            f"plugin_expansion_allowed={plugin_expansion_allowed}; policy_status={policy_status}; "
            f"validation_pass={validation_pass}; guard_pass={guard_pass}; "
            f"source_panel_exists={source_panel_exists}; route_hash_blocked={blocked}"
        )
        next_module = None
        return_code = 2

    contract = {
        "contract_name": "edge_factory_os_true_source_panel_empirical_null_baseline_contract_v1",
        "created_at_utc": utc_now_iso(),
        "contract_status": (
            "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_CONTRACT_READY"
            if prerequisite_pass
            else "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_CONTRACT_BLOCKED"
        ),
        "contract_id": contract_id if prerequisite_pass else None,
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "route_hash_payload": route_hash_payload,
        "route_hash_blocked": blocked,
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "plugin_key": PLUGIN_KEY,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "next_module": next_module,
        "policy_hash": policy_hash,
        "policy_path": str(POLICY_JSON),
        "validation_state_path": str(VALIDATION_STATE_JSON),
        "method_state_path": str(METHOD_STATE_JSON),
        "repair_state_path": str(REPAIR_STATE_JSON),
        "guard_feed_path": str(GUARD_FEED_JSON),
        "guard_pass": guard_pass,
        "repair_state": repair_state_status,
        "method_state": method_state_status,
        "true_source_panel_replay_required": true_source_panel_replay_required,
        "source_panel_path": str(SOURCE_PANEL_PATH),
        "source_panel_exists": source_panel_exists,
        "source_panel_requirements": plugin_config["source_panel_requirements"],
        "plugin_expansion_allowed": False,
        "minimum_empirical_replay_runs": plugin_config["minimum_empirical_replay_runs"],
        "preferred_empirical_replay_runs": plugin_config["preferred_empirical_replay_runs"],
        "required_replay_method_count": plugin_config["required_replay_method_count"],
        "replay_method_count": len(plugin_config["replay_methods"]),
        "replay_methods": plugin_config["replay_methods"],
        "gate_caps": plugin_config["gate_caps"],
        "source_repair_evaluator": {
            "path": str(REPAIR_EVALUATOR_JSON),
            "evaluator_status": evaluator_status,
            "decision_class": decision_class,
            "method_repair_v1_failed": evaluator.get("method_repair_v1_failed"),
            "true_source_panel_replay_required": evaluator.get("true_source_panel_replay_required"),
            "repair_policy_gate_pass": evaluator.get("repair_policy_gate_pass"),
            "failed_gate_keys": evaluator.get("failed_gate_keys"),
            "max_strict_12_any_random_hit_rate": evaluator.get("max_strict_12_any_random_hit_rate"),
            "max_null_adjusted_any_random_hit_rate": evaluator.get("max_null_adjusted_any_random_hit_rate"),
        },
        "runner_contract_rules": {
            "must_read_source_panel_parquet": True,
            "must_validate_schema_before_replay": True,
            "must_validate_row_symbol_month_coverage": True,
            "must_build_canonical_12_policy_months": True,
            "may_observe_raw_13_calendar_buckets": True,
            "must_use_empirical_panel_rows_or_month_buckets": True,
            "must_not_use_summary_rows_only": True,
            "must_not_use_synthetic_month_generation_only": True,
            "must_report_panel_schema": True,
            "must_report_replay_method_inventory": True,
            "must_report_policy_gate_table": True,
            "must_keep_plugin_expansion_blocked": True,
        },
        "required_runner_outputs": plugin_config["required_runner_outputs"],
        "downstream_rules": {
            "if_true_source_panel_baseline_passes": (
                "build evaluator; plugin expansion still blocked until framework status and a separate policy decision"
            ),
            "if_true_source_panel_baseline_fails": (
                "keep plugin expansion blocked and escalate to framework status/route closure"
            ),
            "if_runner_missing_policy_guard_or_repair_state_consumption": "block output",
            "release_allowed_from_this_contract": False,
        },
        "release_gate_feed": {
            "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_CONTRACT_READY": prerequisite_pass,
            "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE": policy_status == "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE",
            "RESEARCH_GATE_VALIDATION_PASS": validation_pass,
            "DATA_QUALITY_GUARD_PASS": guard_pass,
            "TRUE_SOURCE_PANEL_REPLAY_REQUIRED": true_source_panel_replay_required,
            "SOURCE_PANEL_EXISTS": source_panel_exists,
            "PLUGIN_EXPANSION_ALLOWED_FROM_THIS_CONTRACT": False,
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
        **SAFETY_FLAGS,
    }

    write_json(REPO_PLUGIN_JSON, plugin_config)
    write_json(REPO_CONTRACT_JSON, contract)
    write_text(REPO_CONTRACT_TXT, build_contract_text(contract))

    result = {
        "builder_name": "edge_factory_os_true_source_panel_empirical_null_baseline_contract_builder_v1",
        "created_at_utc": utc_now_iso(),
        "builder_status": builder_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "contract_id": contract.get("contract_id"),
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "route_hash_blocked": blocked,
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "plugin_key": PLUGIN_KEY,
        "policy_hash": policy_hash,
        "repair_state": repair_state_status,
        "method_state": method_state_status,
        "true_source_panel_replay_required": true_source_panel_replay_required,
        "source_panel_path": str(SOURCE_PANEL_PATH),
        "source_panel_exists": source_panel_exists,
        "minimum_empirical_replay_runs": plugin_config["minimum_empirical_replay_runs"],
        "preferred_empirical_replay_runs": plugin_config["preferred_empirical_replay_runs"],
        "required_replay_method_count": plugin_config["required_replay_method_count"],
        "replay_method_count": len(plugin_config["replay_methods"]),
        "gate_caps": plugin_config["gate_caps"],
        "guard_pass": guard_pass,
        "validation_pass": validation_pass,
        "plugin_expansion_allowed": False,
        "next_module": next_module,
        "contract": contract,
        "plugin_config": plugin_config,
        "release_gate_feed": contract["release_gate_feed"],
        "input_paths": {
            "repair_evaluator_json": str(REPAIR_EVALUATOR_JSON),
            "repair_next_queue_json": str(REPAIR_NEXT_QUEUE_JSON),
            "repair_state_json": str(REPAIR_STATE_JSON),
            "method_state_json": str(METHOD_STATE_JSON),
            "policy_json": str(POLICY_JSON),
            "validation_state_json": str(VALIDATION_STATE_JSON),
            "guard_feed_json": str(GUARD_FEED_JSON),
            "source_panel_path": str(SOURCE_PANEL_PATH),
            "lesson_index_path": str(LESSON_INDEX_PATH),
            "blocklist_path": str(BLOCKLIST_PATH),
        },
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
