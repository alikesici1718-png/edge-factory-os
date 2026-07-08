#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Stronger Null Model Baseline Contract Builder v1

Purpose:
- Consume Research Gate Tightening Policy Builder v1 output.
- Consume active Research Gate Enforcement Policy v1.
- Build a stronger null/permutation baseline contract.
- Require >=1000 permutation runs and >=8 independent null models.
- Keep plugin expansion blocked until this stronger baseline is run/evaluated.
- Keep all candidate/family/runtime/capital/live/real-order actions blocked.

This builder does NOT:
- run research
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

POLICY_BUILDER_JSON = (
    BASE_DIR
    / "edge_factory_os_research_gate_tightening_policy_builder"
    / "research_gate_tightening_policy_builder_latest.json"
)

POLICY_NEXT_QUEUE_JSON = (
    BASE_DIR
    / "edge_factory_os_research_gate_tightening_policy_builder"
    / "research_gate_tightening_next_queue_latest.json"
)

ENFORCED_POLICY_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_enforcement_policy_v1.json"
)

GUARD_FEED_JSON = (
    BASE_DIR
    / "edge_factory_os_data_quality_guard_runner"
    / "data_quality_guard_feed_latest.json"
)

PRIOR_NULL_RUNNER_JSON = (
    BASE_DIR
    / "edge_factory_os_null_model_permutation_baseline_runner"
    / "null_model_permutation_baseline_runner_latest.json"
)

PRIOR_NULL_EVALUATOR_JSON = (
    BASE_DIR
    / "edge_factory_os_null_model_permutation_baseline_evaluator"
    / "null_model_permutation_baseline_evaluator_latest.json"
)

GENERIC_RUNNER_JSON = (
    BASE_DIR
    / "edge_factory_os_generic_research_runner"
    / "generic_research_runner_latest.json"
)

LESSON_INDEX_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

FRAMEWORK_DIR = REPO_DIR / "edge_factory_os_framework"
PLUGIN_DIR = FRAMEWORK_DIR / "plugins"
CONTRACT_DIR = FRAMEWORK_DIR / "contracts"

REPO_PLUGIN_JSON = PLUGIN_DIR / "stronger_null_model_baseline_plugin_v1.json"
REPO_CONTRACT_JSON = CONTRACT_DIR / "stronger_null_model_baseline_contract_v1.json"
REPO_CONTRACT_TXT = CONTRACT_DIR / "stronger_null_model_baseline_contract_v1.txt"

OUT_DIR = BASE_DIR / "edge_factory_os_research_direction_contracts"
OUT_JSON = OUT_DIR / "stronger_null_model_baseline_contract_latest.json"
OUT_TXT = OUT_DIR / "stronger_null_model_baseline_contract_latest.txt"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

REQUIRED_POLICY_BUILDER_STATUS = "RESEARCH_GATE_TIGHTENING_POLICY_READY"
REQUIRED_POLICY_STATUS = "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE"
REQUIRED_NEXT_RESEARCH_KEY = "RD5_04_STRONGER_NULL_MODEL_BASELINE_REBUILD"

RESEARCH_KEY = "STRONGER_NULL_MODEL_BASELINE_REBUILD_V1"
DIRECTION_QUEUE_KEY = "RD5_04_STRONGER_NULL_MODEL_BASELINE_REBUILD"
PLUGIN_KEY = "STRONGER_NULL_MODEL_BASELINE_PLUGIN_V1"
NEXT_MODULE = "edge_factory_os_stronger_null_model_baseline_runner_v1.py"

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
    except Exception as e:
        return {"_load_error": f"{type(e).__name__}: {e}", "_path": str(path)}


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

    minimum_runs = max(1000, int(rules.get("minimum_permutation_runs") or 1000))
    required_null_models = max(8, int(rules.get("required_independent_null_models") or 8))

    independent_null_models = [
        "within_month_symbol_shuffle",
        "cross_section_symbol_resample",
        "month_label_permutation",
        "time_block_bootstrap",
        "side_flip_null",
        "hold_period_shuffle",
        "feature_rank_shuffle",
        "cost_stress_permutation",
        "symbol_holdout_null",
        "month_holdout_null",
        "liquidity_bucket_shuffle",
        "volatility_regime_shuffle",
    ]

    return {
        "plugin_key": PLUGIN_KEY,
        "plugin_type": "READ_ONLY_STRONGER_NULL_BASELINE",
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "must_consume_guard_feed": True,
        "must_consume_research_gate_policy": True,
        "must_not_reopen_blocked_routes": True,
        "plugin_expansion_allowed": False,
        "baseline_goal": (
            "Rebuild the null/permutation baseline under the tightened research gate enforcement policy, "
            "using more independent null models and stricter false-positive caps before any plugin expansion."
        ),
        "minimum_permutation_runs": minimum_runs,
        "preferred_permutation_runs": max(2000, minimum_runs),
        "required_independent_null_models": required_null_models,
        "independent_null_models": independent_null_models,
        "baseline_tests": independent_null_models[: max(required_null_models, 8)],
        "gate_caps": {
            "max_allowed_strict_12_any_random_hit_rate": min(0.01, float(rules.get("max_allowed_strict_12_any_random_hit_rate") or 0.01)),
            "max_allowed_null_adjusted_any_random_hit_rate": min(0.005, float(rules.get("max_allowed_null_adjusted_any_random_hit_rate") or 0.005)),
            "empirical_p_value_required_lte": min(0.01, float(rules.get("empirical_p_value_required_lte") or 0.01)),
            "minimum_actual_vs_null_margin_bps": float(rules.get("minimum_actual_vs_null_margin_bps") or 2500.0),
        },
        "required_splits": {
            "require_out_of_time_month_split": True,
            "require_symbol_holdout_split": True,
            "require_cost_stress_pass": True,
            "require_top_symbol_concentration_cap": True,
        },
        "required_guard_keys": [
            x.get("guard_key")
            for x in guard_feed.get("mandatory_future_research_requirements", [])
            if isinstance(x, dict) and x.get("guard_key")
        ],
        "forbidden_inputs": [
            "future_return_as_feature",
            "future_pnl_as_feature",
            "manual_symbol_whitelist",
            "manual_month_blacklist",
            "post_outcome_filtering",
            "blocked_route_hash_reuse",
            "loose_null_gate_reuse",
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
    lines.append("EDGE FACTORY OS STRONGER NULL MODEL BASELINE CONTRACT v1")
    lines.append("=" * 100)

    for k in [
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
        "strict_policy_key",
        "canonical_policy_month_count",
        "minimum_permutation_runs",
        "required_independent_null_models",
        "next_module",
    ]:
        lines.append(f"{k}: {contract.get(k)}")

    lines.append("")
    lines.append("BASELINE TESTS")
    lines.append("-" * 100)
    for item in contract.get("baseline_tests", []):
        lines.append(f"- {item}")

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
    lines.append("EDGE FACTORY OS STRONGER NULL MODEL BASELINE CONTRACT BUILDER v1")
    lines.append("=" * 100)

    for k in [
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
        "minimum_permutation_runs",
        "required_independent_null_models",
        "baseline_test_count",
        "next_module",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        lines.append(f"{k}: {v}")

    lines.append("")
    lines.append("OUTPUT PATHS")
    lines.append("-" * 100)
    for k in [
        "output_json",
        "output_txt",
        "repo_plugin_json",
        "repo_contract_json",
        "repo_contract_txt",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS STRONGER NULL MODEL BASELINE CONTRACT BUILDER v1")
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
    print(f"minimum_permutation_runs: {result.get('minimum_permutation_runs')}")
    print(f"required_independent_null_models: {result.get('required_independent_null_models')}")
    print(f"baseline_test_count: {result.get('baseline_test_count')}")
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

    policy_builder = load_json(POLICY_BUILDER_JSON, default={})
    policy_queue = load_json(POLICY_NEXT_QUEUE_JSON, default={})
    policy = load_json(ENFORCED_POLICY_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})
    prior_runner = load_json(PRIOR_NULL_RUNNER_JSON, default={})
    prior_evaluator = load_json(PRIOR_NULL_EVALUATOR_JSON, default={})
    generic_runner = load_json(GENERIC_RUNNER_JSON, default={})
    lesson_index = load_json(LESSON_INDEX_PATH, default={})
    blocklist = load_json(BLOCKLIST_PATH, default={})

    top_queue = extract_top_queue(policy_queue, policy_builder)
    top_key = top_queue.get("research_key") or policy_builder.get("next_recommended_research_key")
    top_module = top_queue.get("next_module_recommendation") or policy_builder.get("next_module")

    policy_builder_status = policy_builder.get("builder_status")
    policy_status = policy.get("policy_status")
    policy_hash = policy.get("policy_hash")
    guard_pass = bool(guard_feed.get("guard_pass"))

    rules = policy.get("enforced_gate_rules")
    if not isinstance(rules, dict):
        rules = {}

    minimum_permutation_runs = max(1000, int(rules.get("minimum_permutation_runs") or 1000))
    required_independent_null_models = max(8, int(rules.get("required_independent_null_models") or 8))

    plugin_config = build_plugin_config(policy, guard_feed)

    route_hash_payload = {
        "research_key": RESEARCH_KEY,
        "plugin_key": PLUGIN_KEY,
        "policy_hash": policy_hash,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "minimum_permutation_runs": minimum_permutation_runs,
        "required_independent_null_models": required_independent_null_models,
        "baseline_tests": plugin_config.get("baseline_tests"),
        "prior_false_positive_assessment": prior_runner.get("overall_false_positive_assessment"),
        "prior_max_strict_rate": prior_runner.get("max_strict_12_any_random_hit_rate"),
        "prior_max_null_rate": prior_runner.get("max_null_adjusted_any_random_hit_rate"),
    }

    route_hash = stable_hash(route_hash_payload)
    blocked_routes = extract_blocked_routes(blocklist)
    blocked = route_hash_blocked(route_hash, blocked_routes)

    prerequisite_pass = (
        policy_builder_status == REQUIRED_POLICY_BUILDER_STATUS
        and policy_status == REQUIRED_POLICY_STATUS
        and top_key == REQUIRED_NEXT_RESEARCH_KEY
        and policy.get("research_gate_tightening_required") is True
        and policy.get("plugin_expansion_allowed_before_policy_validation") is False
        and guard_pass is True
        and minimum_permutation_runs >= 1000
        and required_independent_null_models >= 8
        and blocked is False
    )

    contract_hash = stable_hash({
        "route_hash": route_hash,
        "research_key": RESEARCH_KEY,
        "plugin_key": PLUGIN_KEY,
        "policy_hash": policy_hash,
        "minimum_permutation_runs": minimum_permutation_runs,
        "required_independent_null_models": required_independent_null_models,
        "lessons_count": extract_lessons_count(lesson_index),
        "blocked_route_count": len(blocked_routes),
    })

    contract_id = f"STRONGER_NULL_MODEL_BASELINE_CONTRACT_V1_{contract_hash}_{timestamp_compact()}"

    if prerequisite_pass:
        builder_status = "STRONGER_NULL_MODEL_BASELINE_CONTRACT_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_STRONGER_NULL_MODEL_BASELINE_RUNNER"
        reason = (
            f"policy_active=True; min_runs={minimum_permutation_runs}; "
            f"required_null_models={required_independent_null_models}; route_hash_blocked=False"
        )
        next_module = NEXT_MODULE
        return_code = 0
    else:
        builder_status = "STRONGER_NULL_MODEL_BASELINE_CONTRACT_BLOCKED_PREREQUISITE_NOT_MET"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_POLICY_GUARD_QUEUE_OR_BLOCKLIST"
        reason = (
            f"policy_builder_status={policy_builder_status}; policy_status={policy_status}; "
            f"top_key={top_key}; top_module={top_module}; guard_pass={guard_pass}; "
            f"min_runs={minimum_permutation_runs}; required_null_models={required_independent_null_models}; "
            f"route_hash_blocked={blocked}"
        )
        next_module = None
        return_code = 2

    contract = {
        "contract_name": "edge_factory_os_stronger_null_model_baseline_contract_v1",
        "created_at_utc": utc_now_iso(),
        "contract_status": "STRONGER_NULL_MODEL_BASELINE_CONTRACT_READY" if prerequisite_pass else "STRONGER_NULL_MODEL_BASELINE_CONTRACT_BLOCKED",
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
        "policy_path": str(ENFORCED_POLICY_JSON),
        "guard_feed_path": str(GUARD_FEED_JSON),
        "guard_pass": guard_pass,
        "minimum_permutation_runs": minimum_permutation_runs,
        "preferred_permutation_runs": plugin_config["preferred_permutation_runs"],
        "required_independent_null_models": required_independent_null_models,
        "baseline_test_count": len(plugin_config["baseline_tests"]),
        "baseline_tests": plugin_config["baseline_tests"],
        "gate_caps": plugin_config["gate_caps"],
        "required_splits": plugin_config["required_splits"],
        "source_prior_null_baseline": {
            "runner_path": str(PRIOR_NULL_RUNNER_JSON),
            "evaluator_path": str(PRIOR_NULL_EVALUATOR_JSON),
            "runner_status": prior_runner.get("runner_status"),
            "evaluator_status": prior_evaluator.get("evaluator_status"),
            "overall_false_positive_assessment": prior_runner.get("overall_false_positive_assessment"),
            "max_strict_12_any_random_hit_rate": prior_runner.get("max_strict_12_any_random_hit_rate"),
            "max_null_adjusted_any_random_hit_rate": prior_runner.get("max_null_adjusted_any_random_hit_rate"),
        },
        "source_generic_research_runner": {
            "path": str(GENERIC_RUNNER_JSON),
            "runner_status": generic_runner.get("runner_status"),
            "feature_count": generic_runner.get("feature_count"),
            "diagnostic_row_count": generic_runner.get("diagnostic_row_count"),
            "negative_control_row_count": generic_runner.get("negative_control_row_count"),
            "null_model_row_count": generic_runner.get("null_model_row_count"),
            "strict_12_feature_signal_preview_count": generic_runner.get("strict_12_feature_signal_preview_count"),
            "null_adjusted_signal_count": generic_runner.get("null_adjusted_signal_count"),
        },
        "required_runner_outputs": [
            "policy_consumption_report",
            "guard_consumption_report",
            "independent_null_model_inventory",
            "permutation_run_summary",
            "false_positive_rate_by_null_model",
            "strict_12_random_hit_rate_by_null_model",
            "null_adjusted_random_hit_rate_by_null_model",
            "empirical_p_value_table",
            "policy_gate_pass_fail_table",
            "recommendation_for_future_plugin_expansion",
            "latest_json",
            "latest_txt",
            "csv_outputs",
        ],
        "downstream_rules": {
            "if_policy_caps_pass": "build enforcement validator, then plugin expansion may be reconsidered under guard; no candidate/release",
            "if_policy_caps_fail": "keep plugin expansion blocked and tighten/rebuild null baseline again",
            "if_runner_missing_policy_consumption": "block output",
            "release_allowed_from_this_contract": False,
        },
        "release_gate_feed": {
            "STRONGER_NULL_MODEL_BASELINE_CONTRACT_READY": prerequisite_pass,
            "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE": policy_status == REQUIRED_POLICY_STATUS,
            "DATA_QUALITY_GUARD_PASS": guard_pass,
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
        "builder_name": "edge_factory_os_stronger_null_model_baseline_contract_builder_v1",
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
        "policy_status": policy_status,
        "minimum_permutation_runs": minimum_permutation_runs,
        "preferred_permutation_runs": plugin_config["preferred_permutation_runs"],
        "required_independent_null_models": required_independent_null_models,
        "baseline_test_count": len(plugin_config["baseline_tests"]),
        "gate_caps": plugin_config["gate_caps"],
        "guard_pass": guard_pass,
        "plugin_expansion_allowed": False,
        "next_module": next_module,
        "contract": contract,
        "plugin_config": plugin_config,
        "release_gate_feed": contract["release_gate_feed"],
        "input_paths": {
            "policy_builder_json": str(POLICY_BUILDER_JSON),
            "policy_next_queue_json": str(POLICY_NEXT_QUEUE_JSON),
            "enforced_policy_json": str(ENFORCED_POLICY_JSON),
            "guard_feed_json": str(GUARD_FEED_JSON),
            "prior_null_runner_json": str(PRIOR_NULL_RUNNER_JSON),
            "prior_null_evaluator_json": str(PRIOR_NULL_EVALUATOR_JSON),
            "generic_runner_json": str(GENERIC_RUNNER_JSON),
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
