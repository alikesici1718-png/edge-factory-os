#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Null Baseline Method Repair Contract Builder v1

Purpose:
- Consume Null Baseline Method Audit v1.
- Consume active research gate enforcement policy.
- Consume null baseline method state.
- Build a repair contract for empirical row/month-level null baseline methodology.
- Replace synthetic/proxy month generation with empirical replay/resampling requirements.
- Keep plugin expansion blocked.
- Keep all candidate/family/runtime/capital/live/real-order actions blocked.

This builder does NOT:
- run research
- run the repair baseline
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

AUDIT_JSON = (
    BASE_DIR
    / "edge_factory_os_null_baseline_method_audit"
    / "null_baseline_method_audit_latest.json"
)

AUDIT_QUEUE_JSON = (
    BASE_DIR
    / "edge_factory_os_null_baseline_method_audit"
    / "null_baseline_method_next_queue_latest.json"
)

AUDIT_FINDINGS_CSV = (
    BASE_DIR
    / "edge_factory_os_null_baseline_method_audit"
    / "null_baseline_method_audit_findings_latest.csv"
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

GENERIC_RUNNER_JSON = (
    BASE_DIR
    / "edge_factory_os_generic_research_runner"
    / "generic_research_runner_latest.json"
)

GENERIC_DIAGNOSTIC_CSV = (
    BASE_DIR
    / "edge_factory_os_generic_research_runner"
    / "generic_research_feature_diagnostics_latest.csv"
)

GENERIC_NEGATIVE_CONTROL_CSV = (
    BASE_DIR
    / "edge_factory_os_generic_research_runner"
    / "generic_research_negative_controls_latest.csv"
)

LESSON_INDEX_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

FRAMEWORK_DIR = REPO_DIR / "edge_factory_os_framework"
PLUGIN_DIR = FRAMEWORK_DIR / "plugins"
CONTRACT_DIR = FRAMEWORK_DIR / "contracts"

REPO_PLUGIN_JSON = PLUGIN_DIR / "null_baseline_method_repair_plugin_v1.json"
REPO_CONTRACT_JSON = CONTRACT_DIR / "null_baseline_method_repair_contract_v1.json"
REPO_CONTRACT_TXT = CONTRACT_DIR / "null_baseline_method_repair_contract_v1.txt"

OUT_DIR = BASE_DIR / "edge_factory_os_research_direction_contracts"
OUT_JSON = OUT_DIR / "null_baseline_method_repair_contract_latest.json"
OUT_TXT = OUT_DIR / "null_baseline_method_repair_contract_latest.txt"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

REQUIRED_AUDIT_STATUS = "NULL_BASELINE_METHOD_AUDIT_ATTENTION_REPAIR_RECOMMENDED"
REQUIRED_DECISION_CLASS = "ATTENTION_METHOD_REPAIR_RECOMMENDED_PLUGIN_EXPANSION_BLOCKED"
REQUIRED_NEXT_RESEARCH_KEY = "RD5_06A_NULL_BASELINE_METHOD_REPAIR_CONTRACT"

RESEARCH_KEY = "NULL_BASELINE_METHOD_REPAIR_V1"
DIRECTION_QUEUE_KEY = "RD5_06A_NULL_BASELINE_METHOD_REPAIR_CONTRACT"
PLUGIN_KEY = "NULL_BASELINE_METHOD_REPAIR_PLUGIN_V1"
NEXT_MODULE = "edge_factory_os_null_baseline_method_repair_runner_v1.py"

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

    repair_methods = [
        "empirical_month_block_bootstrap",
        "within_month_symbol_resample",
        "symbol_holdout_replay",
        "month_holdout_replay",
        "time_block_bootstrap_from_diagnostic_rows",
        "negative_control_replay",
        "cost_stress_empirical_replay",
        "liquidity_bucket_empirical_shuffle",
        "volatility_bucket_empirical_shuffle",
        "side_flip_empirical_replay",
    ]

    return {
        "plugin_key": PLUGIN_KEY,
        "plugin_type": "READ_ONLY_NULL_BASELINE_METHOD_REPAIR",
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "must_consume_guard_feed": True,
        "must_consume_research_gate_policy": True,
        "must_consume_null_baseline_method_state": True,
        "must_not_reopen_blocked_routes": True,
        "plugin_expansion_allowed": False,
        "repair_goal": (
            "Replace synthetic/proxy null baseline month generation with empirical row/month-level replay and resampling."
        ),
        "repair_methods": repair_methods,
        "minimum_empirical_replay_runs": max(1000, int(rules.get("minimum_permutation_runs") or 1000)),
        "preferred_empirical_replay_runs": max(2000, int(rules.get("minimum_permutation_runs") or 1000) * 2),
        "required_repair_method_count": 8,
        "required_input_artifacts": [
            str(GENERIC_RUNNER_JSON),
            str(GENERIC_DIAGNOSTIC_CSV),
            str(GENERIC_NEGATIVE_CONTROL_CSV),
            str(POLICY_JSON),
            str(METHOD_STATE_JSON),
            str(GUARD_FEED_JSON),
        ],
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
            "proxy_only_null_model",
            "blocked_route_hash_reuse",
            "loose_null_gate_reuse",
        ],
        "required_runner_outputs": [
            "policy_consumption_report",
            "guard_consumption_report",
            "method_state_consumption_report",
            "empirical_replay_input_inventory",
            "repair_method_inventory",
            "empirical_replay_run_summary",
            "repaired_false_positive_summary",
            "repaired_policy_gate_pass_fail_table",
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
    lines.append("EDGE FACTORY OS NULL BASELINE METHOD REPAIR CONTRACT v1")
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
        "method_state",
        "strict_policy_key",
        "canonical_policy_month_count",
        "minimum_empirical_replay_runs",
        "required_repair_method_count",
        "next_module",
    ]:
        lines.append(f"{key}: {contract.get(key)}")

    lines.append("")
    lines.append("REPAIR METHODS")
    lines.append("-" * 100)
    for item in contract.get("repair_methods", []):
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
    lines.append("EDGE FACTORY OS NULL BASELINE METHOD REPAIR CONTRACT BUILDER v1")
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
        "method_repair_required",
        "minimum_empirical_replay_runs",
        "required_repair_method_count",
        "repair_method_count",
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
    print("EDGE FACTORY OS NULL BASELINE METHOD REPAIR CONTRACT BUILDER v1")
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
    print(f"method_repair_required: {result.get('method_repair_required')}")
    print(f"minimum_empirical_replay_runs: {result.get('minimum_empirical_replay_runs')}")
    print(f"required_repair_method_count: {result.get('required_repair_method_count')}")
    print(f"repair_method_count: {result.get('repair_method_count')}")
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

    audit = load_json(AUDIT_JSON, default={})
    audit_queue = load_json(AUDIT_QUEUE_JSON, default={})
    method_state = load_json(METHOD_STATE_JSON, default={})
    policy = load_json(POLICY_JSON, default={})
    validation_state = load_json(VALIDATION_STATE_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})
    generic_runner = load_json(GENERIC_RUNNER_JSON, default={})
    lesson_index = load_json(LESSON_INDEX_PATH, default={})
    blocklist = load_json(BLOCKLIST_PATH, default={})

    top_queue = extract_top_queue(audit_queue, audit)
    top_key = top_queue.get("research_key") or audit.get("next_recommended_research_key")
    top_module = top_queue.get("next_module_recommendation") or audit.get("next_module")

    audit_status = audit.get("audit_status")
    decision_class = audit.get("decision_class")
    method_repair_required = bool(audit.get("method_repair_required"))
    plugin_expansion_allowed = bool(audit.get("plugin_expansion_allowed"))
    policy_status = policy.get("policy_status")
    policy_hash = policy.get("policy_hash")
    method_state_status = method_state.get("method_state")
    validation_pass = bool(validation_state.get("validator_pass"))
    guard_pass = bool(guard_feed.get("guard_pass"))

    plugin_config = build_plugin_config(policy, guard_feed)

    route_hash_payload = {
        "research_key": RESEARCH_KEY,
        "plugin_key": PLUGIN_KEY,
        "policy_hash": policy_hash,
        "method_state": method_state_status,
        "audit_status": audit_status,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "repair_methods": plugin_config.get("repair_methods"),
        "minimum_empirical_replay_runs": plugin_config.get("minimum_empirical_replay_runs"),
        "generic_runner_status": generic_runner.get("runner_status"),
    }
    route_hash = stable_hash(route_hash_payload)

    blocked_routes = extract_blocked_routes(blocklist)
    blocked = route_hash_blocked(route_hash, blocked_routes)

    prerequisite_pass = (
        audit_status == REQUIRED_AUDIT_STATUS
        and decision_class == REQUIRED_DECISION_CLASS
        and top_key == REQUIRED_NEXT_RESEARCH_KEY
        and method_repair_required is True
        and plugin_expansion_allowed is False
        and policy_status == "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE"
        and validation_pass is True
        and guard_pass is True
        and blocked is False
    )

    contract_hash = stable_hash({
        "route_hash": route_hash,
        "research_key": RESEARCH_KEY,
        "plugin_key": PLUGIN_KEY,
        "policy_hash": policy_hash,
        "method_state": method_state_status,
        "repair_method_count": len(plugin_config["repair_methods"]),
        "lessons_count": extract_lessons_count(lesson_index),
        "blocked_route_count": len(blocked_routes),
    })

    contract_id = f"NULL_BASELINE_METHOD_REPAIR_CONTRACT_V1_{contract_hash}_{timestamp_compact()}"

    if prerequisite_pass:
        builder_status = "NULL_BASELINE_METHOD_REPAIR_CONTRACT_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_NULL_BASELINE_METHOD_REPAIR_RUNNER"
        reason = (
            f"method_repair_required=True; empirical_replay_runs={plugin_config['minimum_empirical_replay_runs']}; "
            f"repair_methods={len(plugin_config['repair_methods'])}; route_hash_blocked=False"
        )
        next_module = NEXT_MODULE
        return_code = 0
    else:
        builder_status = "NULL_BASELINE_METHOD_REPAIR_CONTRACT_BLOCKED_PREREQUISITE_NOT_MET"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_METHOD_AUDIT_POLICY_GUARD_OR_BLOCKLIST"
        reason = (
            f"audit_status={audit_status}; decision_class={decision_class}; top_key={top_key}; "
            f"top_module={top_module}; method_repair_required={method_repair_required}; "
            f"plugin_expansion_allowed={plugin_expansion_allowed}; policy_status={policy_status}; "
            f"validation_pass={validation_pass}; guard_pass={guard_pass}; route_hash_blocked={blocked}"
        )
        next_module = None
        return_code = 2

    contract = {
        "contract_name": "edge_factory_os_null_baseline_method_repair_contract_v1",
        "created_at_utc": utc_now_iso(),
        "contract_status": "NULL_BASELINE_METHOD_REPAIR_CONTRACT_READY" if prerequisite_pass else "NULL_BASELINE_METHOD_REPAIR_CONTRACT_BLOCKED",
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
        "guard_feed_path": str(GUARD_FEED_JSON),
        "guard_pass": guard_pass,
        "method_state": method_state_status,
        "method_repair_required": method_repair_required,
        "plugin_expansion_allowed": False,
        "minimum_empirical_replay_runs": plugin_config["minimum_empirical_replay_runs"],
        "preferred_empirical_replay_runs": plugin_config["preferred_empirical_replay_runs"],
        "required_repair_method_count": plugin_config["required_repair_method_count"],
        "repair_method_count": len(plugin_config["repair_methods"]),
        "repair_methods": plugin_config["repair_methods"],
        "gate_caps": plugin_config["gate_caps"],
        "required_input_artifacts": plugin_config["required_input_artifacts"],
        "source_method_audit": {
            "path": str(AUDIT_JSON),
            "audit_status": audit_status,
            "decision_class": decision_class,
            "finding_count": audit.get("finding_count"),
            "critical_finding_count": audit.get("critical_finding_count"),
            "attention_finding_count": audit.get("attention_finding_count"),
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
        "method_repair_rules": {
            "must_use_empirical_rows_or_month_buckets": True,
            "must_not_use_synthetic_month_generation_only": True,
            "must_not_use_proxy_only_null_model": True,
            "must_report_row_count_by_method": True,
            "must_report_month_coverage_by_method": True,
            "must_report_symbol_coverage_by_method": True,
            "must_report_policy_gate_table": True,
            "must_keep_plugin_expansion_blocked": True,
        },
        "required_runner_outputs": plugin_config["required_runner_outputs"],
        "downstream_rules": {
            "if_repaired_method_passes": "build method repair evaluator; plugin expansion still blocked until separate status/validator allows it",
            "if_repaired_method_fails": "keep plugin expansion blocked and repair methodology again",
            "if_runner_missing_policy_or_guard_consumption": "block output",
            "release_allowed_from_this_contract": False,
        },
        "release_gate_feed": {
            "NULL_BASELINE_METHOD_REPAIR_CONTRACT_READY": prerequisite_pass,
            "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE": policy_status == "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE",
            "RESEARCH_GATE_VALIDATION_PASS": validation_pass,
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
        "builder_name": "edge_factory_os_null_baseline_method_repair_contract_builder_v1",
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
        "method_state": method_state_status,
        "method_repair_required": method_repair_required,
        "minimum_empirical_replay_runs": plugin_config["minimum_empirical_replay_runs"],
        "preferred_empirical_replay_runs": plugin_config["preferred_empirical_replay_runs"],
        "required_repair_method_count": plugin_config["required_repair_method_count"],
        "repair_method_count": len(plugin_config["repair_methods"]),
        "gate_caps": plugin_config["gate_caps"],
        "guard_pass": guard_pass,
        "validation_pass": validation_pass,
        "plugin_expansion_allowed": False,
        "next_module": next_module,
        "contract": contract,
        "plugin_config": plugin_config,
        "release_gate_feed": contract["release_gate_feed"],
        "input_paths": {
            "audit_json": str(AUDIT_JSON),
            "audit_queue_json": str(AUDIT_QUEUE_JSON),
            "audit_findings_csv": str(AUDIT_FINDINGS_CSV),
            "method_state_json": str(METHOD_STATE_JSON),
            "policy_json": str(POLICY_JSON),
            "validation_state_json": str(VALIDATION_STATE_JSON),
            "guard_feed_json": str(GUARD_FEED_JSON),
            "generic_runner_json": str(GENERIC_RUNNER_JSON),
            "generic_diagnostic_csv": str(GENERIC_DIAGNOSTIC_CSV),
            "generic_negative_control_csv": str(GENERIC_NEGATIVE_CONTROL_CSV),
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
