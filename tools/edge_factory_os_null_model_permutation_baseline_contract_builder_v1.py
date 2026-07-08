#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Null Model Permutation Baseline Contract Builder v1

Purpose:
- Consume Generic Research Evaluator v1.
- Consume Generic Research Runner v1 diagnostics/control outputs.
- Build a read-only contract for null/permutation baseline research.
- Quantify how often strict-looking signals can appear by chance.
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

import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

GENERIC_EVALUATOR_JSON = BASE_DIR / "edge_factory_os_generic_research_evaluator" / "generic_research_evaluator_latest.json"
GENERIC_NEXT_QUEUE_JSON = BASE_DIR / "edge_factory_os_generic_research_evaluator" / "generic_research_next_queue_latest.json"
GENERIC_RUNNER_JSON = BASE_DIR / "edge_factory_os_generic_research_runner" / "generic_research_runner_latest.json"

GENERIC_DIAGNOSTIC_CSV = BASE_DIR / "edge_factory_os_generic_research_runner" / "generic_research_feature_diagnostics_latest.csv"
GENERIC_NEGATIVE_CONTROL_CSV = BASE_DIR / "edge_factory_os_generic_research_runner" / "generic_research_negative_controls_latest.csv"
GENERIC_NULL_MODEL_CSV = BASE_DIR / "edge_factory_os_generic_research_runner" / "generic_research_null_models_latest.csv"

GUARD_FEED_JSON = BASE_DIR / "edge_factory_os_data_quality_guard_runner" / "data_quality_guard_feed_latest.json"
LESSON_INDEX_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

OUT_DIR = BASE_DIR / "edge_factory_os_research_direction_contracts"
OUT_JSON = OUT_DIR / "null_model_permutation_baseline_contract_latest.json"
OUT_TXT = OUT_DIR / "null_model_permutation_baseline_contract_latest.txt"

FRAMEWORK_DIR = REPO_DIR / "edge_factory_os_framework"
PLUGIN_DIR = FRAMEWORK_DIR / "plugins"
CONTRACT_DIR = FRAMEWORK_DIR / "contracts"
REPO_PLUGIN_JSON = PLUGIN_DIR / "null_model_permutation_baseline_plugin_v1.json"
REPO_CONTRACT_JSON = CONTRACT_DIR / "null_model_permutation_baseline_contract_v1.json"
REPO_CONTRACT_TXT = CONTRACT_DIR / "null_model_permutation_baseline_contract_v1.txt"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

REQUIRED_EVALUATOR_STATUS = "GENERIC_RESEARCH_EVALUATOR_PLUGIN_ROUTE_CLOSED_NO_SIGNAL"
REQUIRED_NEXT_RESEARCH_KEY = "RD5_02_NULL_MODEL_AND_PERMUTATION_BASELINE"

RESEARCH_KEY = "NULL_MODEL_AND_PERMUTATION_BASELINE_V1"
DIRECTION_QUEUE_KEY = "RD5_02_NULL_MODEL_AND_PERMUTATION_BASELINE"
PLUGIN_KEY = "NULL_MODEL_PERMUTATION_BASELINE_PLUGIN_V1"
NEXT_MODULE = "edge_factory_os_null_model_permutation_baseline_runner_v1.py"

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


def read_csv_rows(path: Path, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(dict(row))
                if limit is not None and len(rows) >= limit:
                    break
    except Exception:
        return []
    return rows


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


def extract_top_queue(queue: Dict[str, Any], evaluator: Dict[str, Any]) -> Dict[str, Any]:
    items = queue.get("next_direction_queue")
    if isinstance(items, list) and items:
        valid = [x for x in items if isinstance(x, dict)]
        if valid:
            return sorted(valid, key=lambda x: int(x.get("priority", 0)), reverse=True)[0]
    return {
        "research_key": evaluator.get("next_recommended_research_key"),
        "next_module_recommendation": evaluator.get("next_module"),
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


def summarize_prior_outputs() -> Dict[str, Any]:
    runner = load_json(GENERIC_RUNNER_JSON, default={})
    diagnostics = read_csv_rows(GENERIC_DIAGNOSTIC_CSV, limit=20)
    negative_controls = read_csv_rows(GENERIC_NEGATIVE_CONTROL_CSV, limit=20)
    null_models = read_csv_rows(GENERIC_NULL_MODEL_CSV, limit=20)

    return {
        "source_runner_status": runner.get("runner_status"),
        "source_contract_id": runner.get("contract_id"),
        "source_route_hash": runner.get("route_hash"),
        "source_plugin_key": runner.get("plugin_key"),
        "source_research_key": runner.get("research_key"),
        "source_row_count": runner.get("row_count"),
        "source_symbol_count": runner.get("symbol_count"),
        "source_raw_calendar_month_count": runner.get("raw_calendar_month_count"),
        "source_canonical_policy_month_count": runner.get("canonical_policy_month_count"),
        "source_feature_count": runner.get("feature_count"),
        "source_diagnostic_row_count": runner.get("diagnostic_row_count"),
        "source_negative_control_row_count": runner.get("negative_control_row_count"),
        "source_null_model_row_count": runner.get("null_model_row_count"),
        "source_strict_12_feature_signal_preview_count": runner.get("strict_12_feature_signal_preview_count"),
        "source_null_adjusted_signal_count": runner.get("null_adjusted_signal_count"),
        "top_diagnostics_sample": diagnostics,
        "negative_controls_sample": negative_controls,
        "null_models_sample": null_models,
    }


def build_plugin_config(guard_feed: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "plugin_key": PLUGIN_KEY,
        "plugin_type": "READ_ONLY_NULL_AND_PERMUTATION_BASELINE",
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "must_consume_guard_feed": True,
        "must_not_reopen_blocked_routes": True,
        "must_use_prior_runner_outputs": True,
        "baseline_goal": (
            "Quantify expected false positive frequency for strict 12/12-like diagnostics under randomized and permuted baselines."
        ),
        "baseline_tests": [
            "random_feature_decile_baseline",
            "within_month_symbol_shuffle_baseline",
            "month_label_permutation_baseline",
            "time_block_permutation_baseline",
            "side_flip_baseline",
            "hold_period_shuffle_baseline",
            "cost_perturbation_baseline",
            "feature_rank_shuffle_baseline",
        ],
        "required_guard_keys": [
            x.get("guard_key")
            for x in guard_feed.get("mandatory_future_research_requirements", [])
            if isinstance(x, dict) and x.get("guard_key")
        ],
        "minimum_permutation_runs": 200,
        "preferred_permutation_runs": 500,
        "strict_policy": {
            "canonical_month_count": 12,
            "positive_months_required": 12,
            "total_pnl_must_be_positive": True,
            "null_adjusted_required": True,
            "empirical_p_value_required_lte": 0.05,
        },
        "forbidden_inputs": [
            "future_return_as_feature",
            "future_pnl_as_feature",
            "manual_symbol_whitelist",
            "manual_month_blacklist",
            "blocked_route_hash_reuse",
            "post_outcome_filtering",
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
    lines.append("EDGE FACTORY OS NULL MODEL PERMUTATION BASELINE CONTRACT v1")
    lines.append("=" * 100)

    for k in [
        "contract_status",
        "allowed_scope",
        "next_action",
        "contract_id",
        "contract_hash",
        "research_key",
        "direction_queue_key",
        "plugin_key",
        "route_hash",
        "strict_policy_key",
        "canonical_policy_month_count",
        "next_module",
    ]:
        lines.append(f"{k}: {contract.get(k)}")

    lines.append("")
    lines.append("BASELINE TESTS")
    lines.append("-" * 100)
    for item in contract.get("baseline_tests", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("REQUIRED OUTPUTS")
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
    lines.append("EDGE FACTORY OS NULL MODEL PERMUTATION BASELINE CONTRACT BUILDER v1")
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
        "research_key",
        "direction_queue_key",
        "plugin_key",
        "baseline_test_count",
        "minimum_permutation_runs",
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
    print("EDGE FACTORY OS NULL MODEL PERMUTATION BASELINE CONTRACT BUILDER v1")
    print("=" * 100)
    print(f"builder_status: {result.get('builder_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"contract_id: {result.get('contract_id')}")
    print(f"contract_hash: {result.get('contract_hash')}")
    print(f"route_hash: {result.get('route_hash')}")
    print(f"research_key: {result.get('research_key')}")
    print(f"direction_queue_key: {result.get('direction_queue_key')}")
    print(f"plugin_key: {result.get('plugin_key')}")
    print(f"baseline_test_count: {result.get('baseline_test_count')}")
    print(f"minimum_permutation_runs: {result.get('minimum_permutation_runs')}")
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

    evaluator = load_json(GENERIC_EVALUATOR_JSON, default={})
    queue = load_json(GENERIC_NEXT_QUEUE_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})
    lesson_index = load_json(LESSON_INDEX_PATH, default={})
    blocklist = load_json(BLOCKLIST_PATH, default={})

    top_queue = extract_top_queue(queue, evaluator)
    lessons_count = extract_lessons_count(lesson_index)
    blocked_routes = extract_blocked_routes(blocklist)

    top_key = top_queue.get("research_key") or evaluator.get("next_recommended_research_key")
    top_module = top_queue.get("next_module_recommendation") or evaluator.get("next_module")

    evaluator_status = evaluator.get("evaluator_status")
    branch_closed = bool(evaluator.get("branch_closed"))
    route_blocklist_required = bool(evaluator.get("route_blocklist_required"))
    guard_pass = bool(guard_feed.get("guard_pass"))

    prerequisite_pass = (
        evaluator_status == REQUIRED_EVALUATOR_STATUS
        and branch_closed is True
        and route_blocklist_required is True
        and top_key == REQUIRED_NEXT_RESEARCH_KEY
        and guard_pass is True
        and int(evaluator.get("canonical_policy_month_count") or 0) == 12
    )

    prior_summary = summarize_prior_outputs()
    plugin_config = build_plugin_config(guard_feed)

    route_hash_payload = {
        "research_key": RESEARCH_KEY,
        "plugin_key": PLUGIN_KEY,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "source_closed_route_hash": evaluator.get("route_hash"),
        "baseline_tests": plugin_config.get("baseline_tests"),
        "minimum_permutation_runs": plugin_config.get("minimum_permutation_runs"),
        "guard_status": guard_feed.get("guard_status"),
    }

    route_hash = stable_hash(route_hash_payload)
    contract_hash = stable_hash({
        "route_hash": route_hash,
        "research_key": RESEARCH_KEY,
        "plugin_key": PLUGIN_KEY,
        "source_evaluator_status": evaluator_status,
        "lessons_count": lessons_count,
        "blocked_route_count": len(blocked_routes),
    })

    contract_id = f"NULL_MODEL_PERMUTATION_BASELINE_CONTRACT_V1_{contract_hash}_{timestamp_compact()}"

    if prerequisite_pass:
        builder_status = "NULL_MODEL_PERMUTATION_BASELINE_CONTRACT_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_NULL_MODEL_PERMUTATION_BASELINE_RUNNER"
        reason = (
            f"generic_route_closed=True; guard_pass=True; baseline_test_count={len(plugin_config['baseline_tests'])}; "
            "null_permutation_contract_ready=True"
        )
        next_module = NEXT_MODULE
        return_code = 0
    else:
        builder_status = "NULL_MODEL_PERMUTATION_BASELINE_CONTRACT_BLOCKED_PREREQUISITE_NOT_MET"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_GENERIC_EVALUATOR_QUEUE_AND_GUARD_FEED"
        reason = (
            f"evaluator_status={evaluator_status}; branch_closed={branch_closed}; "
            f"route_blocklist_required={route_blocklist_required}; top_key={top_key}; "
            f"top_module={top_module}; guard_pass={guard_pass}"
        )
        next_module = None
        return_code = 2

    contract = {
        "contract_name": "edge_factory_os_null_model_permutation_baseline_contract_v1",
        "created_at_utc": utc_now_iso(),
        "contract_status": builder_status.replace("NULL_MODEL_PERMUTATION_BASELINE_CONTRACT_", "CONTRACT_"),
        "contract_id": contract_id if prerequisite_pass else None,
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "route_hash_payload": route_hash_payload,
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "plugin_key": PLUGIN_KEY,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "next_module": next_module,
        "guard_feed_path": str(GUARD_FEED_JSON),
        "guard_pass": guard_pass,
        "source_generic_evaluator": {
            "path": str(GENERIC_EVALUATOR_JSON),
            "evaluator_status": evaluator_status,
            "decision_class": evaluator.get("decision_class"),
            "branch_closed": branch_closed,
            "route_hash": evaluator.get("route_hash"),
            "plugin_key": evaluator.get("plugin_key"),
            "research_key": evaluator.get("research_key"),
            "strict_12_feature_signal_preview_count": evaluator.get("strict_12_feature_signal_preview_count"),
            "null_adjusted_signal_count": evaluator.get("null_adjusted_signal_count"),
        },
        "source_prior_runner_summary": prior_summary,
        "baseline_tests": plugin_config["baseline_tests"],
        "minimum_permutation_runs": plugin_config["minimum_permutation_runs"],
        "preferred_permutation_runs": plugin_config["preferred_permutation_runs"],
        "strict_policy": plugin_config["strict_policy"],
        "required_runner_outputs": [
            "guard_consumption_report",
            "permutation_run_summary",
            "baseline_false_positive_rate",
            "strict_12_random_hit_rate",
            "null_adjusted_random_hit_rate",
            "feature_vs_null_threshold_table",
            "empirical_p_value_table",
            "recommendation_for_plugin_expansion",
            "latest_json",
            "latest_txt",
            "csv_outputs",
        ],
        "downstream_rules": {
            "if_false_positive_rate_high": "tighten research gates before plugin expansion",
            "if_false_positive_rate_low": "plugin expansion may proceed under guard, still no candidate/release",
            "if_null_model_runner_fails": "block further feature expansion until baseline fixed",
            "release_allowed_from_this_contract": False,
        },
        "lessons_count": lessons_count,
        "blocked_route_count": len(blocked_routes),
        "release_gate_feed": {
            "NULL_MODEL_PERMUTATION_BASELINE_CONTRACT_READY": prerequisite_pass,
            "DATA_QUALITY_GUARD_PASS": guard_pass,
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
        "builder_name": "edge_factory_os_null_model_permutation_baseline_contract_builder_v1",
        "created_at_utc": utc_now_iso(),
        "builder_status": builder_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "contract_id": contract.get("contract_id"),
        "contract_hash": contract_hash,
        "route_hash": route_hash,
        "research_key": RESEARCH_KEY,
        "direction_queue_key": DIRECTION_QUEUE_KEY,
        "plugin_key": PLUGIN_KEY,
        "baseline_test_count": len(plugin_config["baseline_tests"]),
        "minimum_permutation_runs": plugin_config["minimum_permutation_runs"],
        "preferred_permutation_runs": plugin_config["preferred_permutation_runs"],
        "guard_pass": guard_pass,
        "source_route_hash": evaluator.get("route_hash"),
        "lessons_count": lessons_count,
        "blocked_route_count": len(blocked_routes),
        "next_module": next_module,
        "contract": contract,
        "plugin_config": plugin_config,
        "release_gate_feed": contract["release_gate_feed"],
        "input_paths": {
            "generic_evaluator_json": str(GENERIC_EVALUATOR_JSON),
            "generic_next_queue_json": str(GENERIC_NEXT_QUEUE_JSON),
            "generic_runner_json": str(GENERIC_RUNNER_JSON),
            "guard_feed_json": str(GUARD_FEED_JSON),
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
