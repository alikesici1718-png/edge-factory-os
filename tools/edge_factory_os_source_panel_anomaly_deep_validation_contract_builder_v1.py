#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Source Panel Anomaly Deep Validation Contract Builder v1

Purpose:
- Consume Source Panel Anomaly Discovery Evaluator v1.
- Consume Source Panel Anomaly Discovery State v1.
- Consume deep-validation queue and preview CSV.
- Build a read-only deep validation contract for the discovered anomaly preview.
- Require month holdout, symbol holdout, feature perturbation, leakage audit, negative controls, and true-null rerun.
- Keep candidate/family/runtime/capital/live/real-order actions blocked.

This builder does NOT:
- run deep validation
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

import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

EVALUATOR_JSON = (
    BASE_DIR
    / "edge_factory_os_source_panel_anomaly_discovery_evaluator"
    / "source_panel_anomaly_discovery_evaluator_latest.json"
)

DEEP_VALIDATION_QUEUE_JSON = (
    BASE_DIR
    / "edge_factory_os_source_panel_anomaly_discovery_evaluator"
    / "source_panel_anomaly_deep_validation_queue_latest.json"
)

PREVIEW_CSV = (
    BASE_DIR
    / "edge_factory_os_source_panel_anomaly_discovery_evaluator"
    / "source_panel_anomaly_preview_candidates_for_validation_latest.csv"
)

ANOMALY_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "source_panel_anomaly_discovery_state_v1.json"
)

SOURCE_PANEL_CONTRACT_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "contracts"
    / "source_panel_anomaly_discovery_contract_v1.json"
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

REPO_PLUGIN_JSON = PLUGIN_DIR / "source_panel_anomaly_deep_validation_plugin_v1.json"
REPO_CONTRACT_JSON = CONTRACT_DIR / "source_panel_anomaly_deep_validation_contract_v1.json"
REPO_CONTRACT_TXT = CONTRACT_DIR / "source_panel_anomaly_deep_validation_contract_v1.txt"

OUT_DIR = BASE_DIR / "edge_factory_os_source_panel_anomaly_deep_validation_contract"
OUT_JSON = OUT_DIR / "source_panel_anomaly_deep_validation_contract_latest.json"
OUT_TXT = OUT_DIR / "source_panel_anomaly_deep_validation_contract_latest.txt"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

EXPECTED_EVALUATOR_STATUS = "SOURCE_PANEL_ANOMALY_DISCOVERY_EVALUATOR_PREVIEW_FOUND_TRUE_NULL_CLEAN_DEEP_VALIDATION_REQUIRED"
EXPECTED_DECISION_CLASS = "SOURCE_PANEL_ANOMALY_PREVIEW_TRUE_NULL_CLEAN_NOT_RELEASE_DEEP_VALIDATION_REQUIRED"
EXPECTED_QUEUE_KEY = "RD6_01A_SOURCE_PANEL_ANOMALY_DEEP_VALIDATION"

RESEARCH_KEY = "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_V1"
DIRECTION_QUEUE_KEY = "RD6_01A_SOURCE_PANEL_ANOMALY_DEEP_VALIDATION"
PLUGIN_KEY = "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_PLUGIN_V1"
NEXT_MODULE = "edge_factory_os_source_panel_anomaly_deep_validation_runner_v1.py"

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


def read_csv_rows(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(dict(row))
    except Exception:
        return []
    return rows


def stable_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y", "pass"}


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def extract_blocked_routes(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get("blocked_routes"), list):
        return [x for x in obj["blocked_routes"] if isinstance(x, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def count_lessons(obj: Any) -> int:
    if isinstance(obj, dict) and isinstance(obj.get("lessons"), list):
        return len(obj["lessons"])
    if isinstance(obj, list):
        return len([x for x in obj if isinstance(x, dict)])
    return 0


def count_blocked_routes(obj: Any) -> int:
    return len(extract_blocked_routes(obj))


def blocked_hashes(obj: Any) -> set:
    out = set()
    for item in extract_blocked_routes(obj):
        rh = item.get("route_hash")
        if rh:
            out.add(str(rh))
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
    evaluator: Dict[str, Any],
    anomaly_state: Dict[str, Any],
    preview_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    rules = policy.get("enforced_gate_rules")
    if not isinstance(rules, dict):
        rules = {}

    required_guard_keys = [
        x.get("guard_key")
        for x in guard_feed.get("mandatory_future_research_requirements", [])
        if isinstance(x, dict) and x.get("guard_key")
    ]

    top_preview = preview_rows[0] if preview_rows else {}

    validation_tests = [
        "month_holdout_stability",
        "symbol_holdout_stability",
        "feature_threshold_perturbation",
        "feature_value_noise_perturbation",
        "negative_controls_rerun",
        "true_source_panel_null_rerun",
        "outcome_leakage_audit",
        "feature_name_leakage_audit",
        "calendar_edge_month_sensitivity",
        "minimum_symbol_coverage_check",
        "minimum_row_coverage_check",
        "optional_outcome_diagnostic_after_stability_only",
    ]

    return {
        "plugin_key": PLUGIN_KEY,
        "plugin_type": "READ_ONLY_SOURCE_PANEL_ANOMALY_DEEP_VALIDATION",
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "source_panel_path": str(SOURCE_PANEL_PATH),
        "must_consume_source_panel_anomaly_state": True,
        "must_consume_preview_csv": True,
        "must_consume_framework_status_panel": True,
        "must_consume_true_source_panel_null_state": True,
        "must_consume_research_gate_policy": True,
        "must_consume_guard_feed": True,
        "must_consume_route_blocklist": True,
        "must_keep_plugin_expansion_blocked": True,
        "must_not_generate_candidate": True,
        "must_not_release_family": True,
        "must_not_touch_runtime": True,
        "must_not_change_capital": True,
        "must_not_enable_live": True,
        "preview_axis_key": top_preview.get("axis_key") or anomaly_state.get("top_preview_axis_key"),
        "preview_feature": top_preview.get("feature") or anomaly_state.get("top_preview_feature"),
        "preview_side": top_preview.get("side") or anomaly_state.get("top_preview_side"),
        "preview_total_anomaly_score": top_preview.get("total_anomaly_score") or anomaly_state.get("top_preview_total_anomaly_score"),
        "preview_min_month_anomaly_score": top_preview.get("min_month_anomaly_score"),
        "preview_median_month_anomaly_score": top_preview.get("median_month_anomaly_score"),
        "validation_tests": validation_tests,
        "required_validation_count": len(validation_tests),
        "minimum_deep_validation_pass_count": len(validation_tests),
        "minimum_empirical_null_runs": max(1000, int(rules.get("minimum_permutation_runs") or 1000)),
        "preferred_empirical_null_runs": max(2000, int(rules.get("minimum_permutation_runs") or 1000) * 2),
        "gate_caps": {
            "max_allowed_strict_12_any_random_hit_rate": min(0.01, float(rules.get("max_allowed_strict_12_any_random_hit_rate") or 0.01)),
            "max_allowed_null_adjusted_any_random_hit_rate": min(0.005, float(rules.get("max_allowed_null_adjusted_any_random_hit_rate") or 0.005)),
            "empirical_p_value_required_lte": min(0.01, float(rules.get("empirical_p_value_required_lte") or 0.01)),
            "minimum_actual_vs_null_margin_bps": float(rules.get("minimum_actual_vs_null_margin_bps") or 2500.0),
        },
        "stability_thresholds": {
            "minimum_month_holdout_pass_rate": 0.75,
            "minimum_symbol_holdout_pass_rate": 0.75,
            "minimum_feature_perturbation_pass_rate": 0.75,
            "minimum_negative_control_pass_rate": 1.0,
            "minimum_true_null_rerun_pass_rate": 1.0,
            "minimum_canonical_month_count": 12,
            "minimum_symbol_count": 200,
            "minimum_row_count": 1000000,
        },
        "required_guard_keys": required_guard_keys,
        "forbidden_inputs": [
            "future_return_as_discovery_feature",
            "future_pnl_as_discovery_feature",
            "outcome_label_first_selection",
            "manual_symbol_whitelist",
            "manual_month_blacklist",
            "post_outcome_filtering",
            "blocked_route_hash_reuse",
            "candidate_generation",
            "family_release",
            "runtime_touch",
            "capital_change",
            "active_paper",
            "live_or_real_orders",
        ],
        "required_runner_outputs": [
            "deep_validation_input_consumption_report",
            "preview_candidate_consumption_report",
            "month_holdout_stability_report",
            "symbol_holdout_stability_report",
            "feature_threshold_perturbation_report",
            "feature_value_noise_perturbation_report",
            "negative_controls_rerun_report",
            "true_source_panel_null_rerun_report",
            "outcome_leakage_audit_report",
            "feature_name_leakage_audit_report",
            "calendar_edge_month_sensitivity_report",
            "deep_validation_gate_table",
            "deep_validation_results_csv",
            "latest_json",
            "latest_txt",
        ],
        **SAFETY_FLAGS,
    }


def build_contract_text(contract: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS SOURCE PANEL ANOMALY DEEP VALIDATION CONTRACT v1")
    lines.append("=" * 100)

    for key in [
        "contract_status",
        "allowed_scope",
        "next_action",
        "contract_id",
        "contract_hash",
        "route_hash",
        "route_hash_blocked",
        "source_anomaly_route_hash",
        "research_key",
        "direction_queue_key",
        "plugin_key",
        "policy_hash",
        "source_panel_path",
        "source_panel_exists",
        "preview_axis_key",
        "preview_feature",
        "preview_side",
        "preview_found",
        "true_null_clean",
        "deep_validation_required",
        "release_allowed",
        "required_validation_count",
        "next_module",
    ]:
        lines.append(f"{key}: {contract.get(key)}")

    lines.append("")
    lines.append("VALIDATION TESTS")
    lines.append("-" * 100)
    for item in contract.get("validation_tests", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("STABILITY THRESHOLDS")
    lines.append("-" * 100)
    lines.append(json.dumps(contract.get("stability_thresholds", {}), indent=2, ensure_ascii=False))

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
    lines.append("EDGE FACTORY OS SOURCE PANEL ANOMALY DEEP VALIDATION CONTRACT BUILDER v1")
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
        "source_anomaly_route_hash",
        "research_key",
        "direction_queue_key",
        "plugin_key",
        "policy_hash",
        "source_panel_exists",
        "preview_axis_key",
        "preview_feature",
        "preview_side",
        "preview_found",
        "true_null_clean",
        "deep_validation_required",
        "release_allowed",
        "required_validation_count",
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
    print("EDGE FACTORY OS SOURCE PANEL ANOMALY DEEP VALIDATION CONTRACT BUILDER v1")
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
    print(f"source_anomaly_route_hash: {result.get('source_anomaly_route_hash')}")
    print(f"research_key: {result.get('research_key')}")
    print(f"direction_queue_key: {result.get('direction_queue_key')}")
    print(f"plugin_key: {result.get('plugin_key')}")
    print(f"policy_hash: {result.get('policy_hash')}")
    print(f"source_panel_exists: {result.get('source_panel_exists')}")
    print(f"preview_axis_key: {result.get('preview_axis_key')}")
    print(f"preview_feature: {result.get('preview_feature')}")
    print(f"preview_side: {result.get('preview_side')}")
    print(f"preview_found: {result.get('preview_found')}")
    print(f"true_null_clean: {result.get('true_null_clean')}")
    print(f"deep_validation_required: {result.get('deep_validation_required')}")
    print(f"release_allowed: {result.get('release_allowed')}")
    print(f"required_validation_count: {result.get('required_validation_count')}")
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
    queue = load_json(DEEP_VALIDATION_QUEUE_JSON, default={})
    anomaly_state = load_json(ANOMALY_STATE_JSON, default={})
    source_contract = load_json(SOURCE_PANEL_CONTRACT_JSON, default={})
    framework_status = load_json(FRAMEWORK_STATUS_JSON, default={})
    true_panel_state = load_json(TRUE_PANEL_STATE_JSON, default={})
    policy = load_json(POLICY_JSON, default={})
    runtime_state = load_json(POLICY_RUNTIME_STATE_JSON, default={})
    validation_state = load_json(POLICY_VALIDATION_STATE_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})
    lesson_index = load_json(LESSON_INDEX_PATH, default={})
    blocklist = load_json(BLOCKLIST_PATH, default={})
    preview_rows = read_csv_rows(PREVIEW_CSV)

    selected = selected_queue_item(queue)

    evaluator_ok = (
        evaluator.get("evaluator_status") == EXPECTED_EVALUATOR_STATUS
        and evaluator.get("decision_class") == EXPECTED_DECISION_CLASS
        and bool(evaluator.get("preview_found"))
        and bool(evaluator.get("true_null_clean"))
        and bool(evaluator.get("material_difference_pass"))
        and bool(evaluator.get("deep_validation_required"))
        and evaluator.get("release_allowed") is False
    )

    queue_ok = (
        queue.get("queue_status") == "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_QUEUE_READY"
        and queue.get("top_next_research_key") == EXPECTED_QUEUE_KEY
        and selected.get("next_module_recommendation") == "edge_factory_os_source_panel_anomaly_deep_validation_contract_builder_v1.py"
    )

    state_ok = (
        anomaly_state.get("state_status") == "SOURCE_PANEL_ANOMALY_PREVIEW_FOUND_TRUE_NULL_CLEAN_DEEP_VALIDATION_REQUIRED"
        and bool(anomaly_state.get("preview_found"))
        and bool(anomaly_state.get("true_null_clean"))
        and bool(anomaly_state.get("material_difference_pass"))
        and bool(anomaly_state.get("deep_validation_required"))
        and anomaly_state.get("release_allowed") is False
    )

    framework_ok = framework_status.get("panel_status") == "FRAMEWORK_STATUS_PANEL_READY_POLICY_LOCKED_NO_ACTUAL_SIGNAL"
    true_panel_ok = bool(true_panel_state.get("false_positive_methodology_repaired")) and not bool(true_panel_state.get("actual_signal_present"))
    policy_active = policy.get("policy_status") == "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE"
    validator_pass = bool(validation_state.get("validator_pass"))
    guard_pass = bool(guard_feed.get("guard_pass"))
    runtime_blocks_plugin = runtime_state.get("plugin_expansion_allowed") is False
    source_panel_exists = SOURCE_PANEL_PATH.exists()

    block_hashes = blocked_hashes(blocklist)

    top_preview = preview_rows[0] if preview_rows else {}
    preview_axis_key = top_preview.get("axis_key") or anomaly_state.get("top_preview_axis_key")
    preview_feature = top_preview.get("feature") or anomaly_state.get("top_preview_feature")
    preview_side = top_preview.get("side") or anomaly_state.get("top_preview_side")
    source_anomaly_route_hash = anomaly_state.get("route_hash") or evaluator.get("route_hash")

    plugin_config = build_plugin_config(
        policy=policy,
        guard_feed=guard_feed,
        evaluator=evaluator,
        anomaly_state=anomaly_state,
        preview_rows=preview_rows,
    )

    route_hash_payload = {
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "plugin_key": PLUGIN_KEY,
        "policy_hash": policy.get("policy_hash"),
        "source_anomaly_route_hash": source_anomaly_route_hash,
        "preview_axis_key": preview_axis_key,
        "preview_feature": preview_feature,
        "preview_side": preview_side,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "validation_tests": plugin_config["validation_tests"],
        "release_allowed": False,
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
        and len(preview_rows) > 0
        and not route_hash_blocked
    )

    contract_hash = stable_hash({
        "route_hash": route_hash,
        "source_anomaly_route_hash": source_anomaly_route_hash,
        "research_key": RESEARCH_KEY,
        "plugin_key": PLUGIN_KEY,
        "policy_hash": policy.get("policy_hash"),
        "preview_axis_key": preview_axis_key,
        "preview_feature": preview_feature,
        "preview_side": preview_side,
        "lesson_count": count_lessons(lesson_index),
        "blocked_route_count": count_blocked_routes(blocklist),
        "validation_count": len(plugin_config["validation_tests"]),
    })

    contract_id = f"SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_CONTRACT_V1_{contract_hash}_{timestamp_compact()}"

    if prerequisite_pass:
        builder_status = "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_CONTRACT_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_RUNNER"
        reason = (
            f"preview_axis={preview_axis_key}; preview_feature={preview_feature}; "
            f"true_null_clean=True; deep_validation_required=True; route_hash_blocked=False; release_allowed=False"
        )
        next_module = NEXT_MODULE
        return_code = 0
    else:
        builder_status = "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_CONTRACT_BLOCKED_PREREQUISITE_NOT_MET"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_CONTRACT_PREREQUISITES_NO_RELEASE"
        reason = (
            f"evaluator_ok={evaluator_ok}; queue_ok={queue_ok}; state_ok={state_ok}; "
            f"framework_ok={framework_ok}; true_panel_ok={true_panel_ok}; policy_active={policy_active}; "
            f"validator_pass={validator_pass}; guard_pass={guard_pass}; runtime_blocks_plugin={runtime_blocks_plugin}; "
            f"source_panel_exists={source_panel_exists}; preview_rows={len(preview_rows)}; route_hash_blocked={route_hash_blocked}"
        )
        next_module = None
        return_code = 2

    hard_requirements_for_runner = [
        "read full source panel parquet",
        "consume anomaly discovery state",
        "consume preview candidate CSV",
        "consume framework status panel",
        "consume true source-panel null baseline state",
        "consume policy and guard states",
        "consume route blocklist",
        "validate no future/outcome feature leakage",
        "run month holdout stability",
        "run symbol holdout stability",
        "run feature threshold perturbation",
        "run feature value noise perturbation",
        "rerun negative controls",
        "rerun true source-panel null baseline on preview",
        "perform calendar edge month sensitivity",
        "produce deep validation gate table",
        "keep release false",
        "keep candidate/family/runtime/capital/live false",
    ]

    contract = {
        "contract_name": "edge_factory_os_source_panel_anomaly_deep_validation_contract_v1",
        "created_at_utc": utc_now_iso(),
        "contract_status": "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_CONTRACT_READY" if prerequisite_pass else "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_CONTRACT_BLOCKED",
        "contract_id": contract_id if prerequisite_pass else None,
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "route_hash_payload": route_hash_payload,
        "route_hash_blocked": route_hash_blocked,
        "source_anomaly_route_hash": source_anomaly_route_hash,
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
        "preview_axis_key": preview_axis_key,
        "preview_feature": preview_feature,
        "preview_side": preview_side,
        "preview_rows": preview_rows,
        "preview_found": bool(evaluator.get("preview_found")),
        "true_null_clean": bool(evaluator.get("true_null_clean")),
        "material_difference_pass": bool(evaluator.get("material_difference_pass")),
        "deep_validation_required": bool(evaluator.get("deep_validation_required")),
        "release_allowed": False,
        "plugin_expansion_allowed": False,
        "required_validation_count": len(plugin_config["validation_tests"]),
        "minimum_deep_validation_pass_count": plugin_config["minimum_deep_validation_pass_count"],
        "validation_tests": plugin_config["validation_tests"],
        "stability_thresholds": plugin_config["stability_thresholds"],
        "gate_caps": plugin_config["gate_caps"],
        "hard_requirements_for_runner": hard_requirements_for_runner,
        "required_runner_outputs": plugin_config["required_runner_outputs"],
        "source_artifacts": {
            "evaluator_json": str(EVALUATOR_JSON),
            "deep_validation_queue_json": str(DEEP_VALIDATION_QUEUE_JSON),
            "preview_csv": str(PREVIEW_CSV),
            "anomaly_state_json": str(ANOMALY_STATE_JSON),
            "source_panel_contract_json": str(SOURCE_PANEL_CONTRACT_JSON),
            "framework_status_json": str(FRAMEWORK_STATUS_JSON),
            "true_panel_state_json": str(TRUE_PANEL_STATE_JSON),
            "policy_json": str(POLICY_JSON),
            "policy_validation_state_json": str(POLICY_VALIDATION_STATE_JSON),
            "guard_feed_json": str(GUARD_FEED_JSON),
            "blocklist_path": str(BLOCKLIST_PATH),
        },
        "downstream_rules": {
            "if_deep_validation_passes": "build evaluator; still no release, only deep-validation-pass state",
            "if_deep_validation_fails": "close route and add lesson/blocklist",
            "if_any_leakage_or_holdout_failure": "fail validation and keep all actions blocked",
            "release_allowed_from_this_contract": False,
        },
        "release_gate_feed": {
            "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_CONTRACT_READY": prerequisite_pass,
            "SOURCE_ANOMALY_PREVIEW_FOUND": bool(evaluator.get("preview_found")),
            "TRUE_NULL_CLEAN": bool(evaluator.get("true_null_clean")),
            "DEEP_VALIDATION_REQUIRED": bool(evaluator.get("deep_validation_required")),
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
        "builder_name": "edge_factory_os_source_panel_anomaly_deep_validation_contract_builder_v1",
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
        "source_anomaly_route_hash": source_anomaly_route_hash,
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "plugin_key": PLUGIN_KEY,
        "policy_hash": policy.get("policy_hash"),
        "source_panel_path": str(SOURCE_PANEL_PATH),
        "source_panel_exists": source_panel_exists,
        "preview_axis_key": preview_axis_key,
        "preview_feature": preview_feature,
        "preview_side": preview_side,
        "preview_found": bool(evaluator.get("preview_found")),
        "true_null_clean": bool(evaluator.get("true_null_clean")),
        "material_difference_pass": bool(evaluator.get("material_difference_pass")),
        "deep_validation_required": bool(evaluator.get("deep_validation_required")),
        "release_allowed": False,
        "plugin_expansion_allowed": False,
        "required_validation_count": len(plugin_config["validation_tests"]),
        "minimum_deep_validation_pass_count": plugin_config["minimum_deep_validation_pass_count"],
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
