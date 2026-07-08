#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Research Gate Tightening Policy Builder v1

Purpose:
- Consume Null Model Permutation Baseline Evaluator v1.
- Consume the framework policy draft.
- Convert high false-positive baseline lesson into enforceable research gate policy.
- Block plugin expansion until tightened gates are active.
- Keep all candidate/family/runtime/capital/live/real-order actions blocked.

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
    / "edge_factory_os_null_model_permutation_baseline_evaluator"
    / "null_model_permutation_baseline_evaluator_latest.json"
)

NEXT_QUEUE_JSON = (
    BASE_DIR
    / "edge_factory_os_null_model_permutation_baseline_evaluator"
    / "null_model_permutation_next_queue_latest.json"
)

RUNNER_JSON = (
    BASE_DIR
    / "edge_factory_os_null_model_permutation_baseline_runner"
    / "null_model_permutation_baseline_runner_latest.json"
)

GUARD_FEED_JSON = (
    BASE_DIR
    / "edge_factory_os_data_quality_guard_runner"
    / "data_quality_guard_feed_latest.json"
)

LESSON_INDEX_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

FRAMEWORK_POLICY_DIR = REPO_DIR / "edge_factory_os_framework" / "policies"
POLICY_DRAFT_JSON = FRAMEWORK_POLICY_DIR / "research_gate_tightening_policy_v1.json"
ENFORCED_POLICY_JSON = FRAMEWORK_POLICY_DIR / "research_gate_enforcement_policy_v1.json"
ENFORCED_POLICY_TXT = FRAMEWORK_POLICY_DIR / "research_gate_enforcement_policy_v1.txt"

OUT_DIR = BASE_DIR / "edge_factory_os_research_gate_tightening_policy_builder"
OUT_JSON = OUT_DIR / "research_gate_tightening_policy_builder_latest.json"
OUT_TXT = OUT_DIR / "research_gate_tightening_policy_builder_latest.txt"
OUT_QUEUE_JSON = OUT_DIR / "research_gate_tightening_next_queue_latest.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

REQUIRED_EVALUATOR_STATUS = "NULL_MODEL_BASELINE_EVALUATOR_HIGH_FALSE_POSITIVE_RISK_GATE_TIGHTENING_REQUIRED"
REQUIRED_DECISION_CLASS = "FALSE_POSITIVE_BASELINE_HIGH_RESEARCH_GATES_MUST_TIGHTEN"
REQUIRED_NEXT_RESEARCH_KEY = "RD5_03_RESEARCH_GATE_TIGHTENING_POLICY"

NEXT_RESEARCH_KEY = "RD5_04_STRONGER_NULL_MODEL_BASELINE_REBUILD"
NEXT_MODULE = "edge_factory_os_stronger_null_model_baseline_contract_builder_v1.py"

ALT_RESEARCH_KEY = "RD5_05_RESEARCH_GATE_ENFORCEMENT_VALIDATOR"
ALT_MODULE = "edge_factory_os_research_gate_enforcement_validator_v1.py"

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


def extract_blocked_count(obj: Any) -> int:
    if isinstance(obj, dict) and isinstance(obj.get("blocked_routes"), list):
        return len(obj["blocked_routes"])
    if isinstance(obj, list):
        return len([x for x in obj if isinstance(x, dict)])
    return 0


def build_enforcement_policy(
    evaluator: Dict[str, Any],
    runner: Dict[str, Any],
    draft: Dict[str, Any],
    guard_feed: Dict[str, Any],
) -> Dict[str, Any]:
    draft_rules = draft.get("draft_gate_rules")
    if not isinstance(draft_rules, dict):
        draft_rules = {}

    max_strict_rate = float(evaluator.get("max_strict_12_any_random_hit_rate") or 1.0)
    max_null_rate = float(evaluator.get("max_null_adjusted_any_random_hit_rate") or 1.0)

    policy_hash = stable_hash({
        "source_assessment": evaluator.get("overall_false_positive_assessment"),
        "max_strict_rate": max_strict_rate,
        "max_null_rate": max_null_rate,
        "draft_rules": draft_rules,
        "strict_policy_key": STRICT_POLICY_KEY,
    })

    return {
        "policy_name": "edge_factory_os_research_gate_enforcement_policy_v1",
        "policy_hash": policy_hash,
        "created_at_utc": utc_now_iso(),
        "policy_status": "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE",
        "severity": "ATTENTION",
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "source_evaluator_status": evaluator.get("evaluator_status"),
        "source_decision_class": evaluator.get("decision_class"),
        "source_false_positive_assessment": evaluator.get("overall_false_positive_assessment"),
        "source_max_strict_12_any_random_hit_rate": max_strict_rate,
        "source_max_null_adjusted_any_random_hit_rate": max_null_rate,
        "source_runner_status": runner.get("runner_status"),
        "source_baseline_test_count": runner.get("baseline_test_count"),
        "source_permutation_runs_per_test": runner.get("permutation_runs_per_test"),
        "data_quality_guard_required": True,
        "data_quality_guard_status": guard_feed.get("guard_status"),
        "data_quality_guard_pass": bool(guard_feed.get("guard_pass")),
        "research_gate_tightening_required": True,
        "plugin_expansion_allowed_before_policy_validation": False,
        "candidate_generation_allowed": False,
        "candidate_contract_allowed": False,
        "family_release_allowed": False,
        "promotion_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        "enforced_gate_rules": {
            "minimum_permutation_runs": max(1000, int(draft_rules.get("minimum_permutation_runs") or 1000)),
            "required_independent_null_models": max(8, int(draft_rules.get("required_independent_null_models") or 8)),
            "max_allowed_strict_12_any_random_hit_rate": min(0.01, float(draft_rules.get("max_allowed_strict_12_any_random_hit_rate") or 0.01)),
            "max_allowed_null_adjusted_any_random_hit_rate": min(0.005, float(draft_rules.get("max_allowed_null_adjusted_any_random_hit_rate") or 0.005)),
            "empirical_p_value_required_lte": min(0.01, float(draft_rules.get("empirical_p_value_required_lte") or 0.01)),
            "minimum_actual_vs_null_margin_bps": 2500.0,
            "minimum_positive_months": 12,
            "required_canonical_months": 12,
            "require_out_of_time_month_split": True,
            "require_symbol_holdout_split": True,
            "require_cost_stress_pass": True,
            "require_top_symbol_concentration_cap": True,
            "max_top_symbol_share": 0.20,
            "max_top5_symbol_share": 0.50,
            "require_no_manual_symbol_whitelist": True,
            "require_no_manual_month_blacklist": True,
            "require_data_quality_guard_pass": True,
            "require_route_hash_not_blocked": True,
            "require_negative_controls": True,
            "require_null_models": True,
            "require_deep_validation_before_candidate_contract": True,
            "require_manual_or_ai_review_non_override": True,
        },
        "hard_blocks": [
            "plugin_expansion_without_policy_validation",
            "strict_preview_without_null_adjustment",
            "null_adjusted_signal_without_empirical_p_value",
            "false_positive_rate_above_cap",
            "data_quality_guard_missing_or_failed",
            "blocked_route_hash_reuse",
            "manual_symbol_whitelist",
            "manual_month_blacklist",
            "candidate_generation_before_deep_validation",
            "family_release_before_full_release_gate",
            "runtime_touch_before_final_release_gate",
            "capital_or_live_action_before_final_release_gate",
        ],
        "required_next_validations": [
            "stronger_null_model_baseline_rebuild",
            "research_gate_enforcement_validator",
            "plugin_expansion_preflight_under_tightened_gates",
            "deep_validation_contract_if_signal_ever_found",
        ],
        "policy_effect": {
            "all_future_research_must_consume_this_policy": True,
            "old_loose_null_gate_routes_blocked": True,
            "rd5_plugin_expansion_blocked_until_validation": True,
            "release_pass_from_policy": False,
        },
    }


def policy_text(policy: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS RESEARCH GATE ENFORCEMENT POLICY v1")
    lines.append("=" * 100)

    for k in [
        "policy_status",
        "policy_hash",
        "severity",
        "strict_policy_key",
        "canonical_policy_month_count",
        "source_false_positive_assessment",
        "source_max_strict_12_any_random_hit_rate",
        "source_max_null_adjusted_any_random_hit_rate",
        "research_gate_tightening_required",
        "plugin_expansion_allowed_before_policy_validation",
    ]:
        lines.append(f"{k}: {policy.get(k)}")

    lines.append("")
    lines.append("ENFORCED GATE RULES")
    lines.append("-" * 100)
    for k, v in policy.get("enforced_gate_rules", {}).items():
        lines.append(f"{k}: {v}")

    lines.append("")
    lines.append("HARD BLOCKS")
    lines.append("-" * 100)
    for item in policy.get("hard_blocks", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("SAFETY")
    lines.append("-" * 100)
    for k in [
        "candidate_generation_allowed",
        "candidate_contract_allowed",
        "family_release_allowed",
        "runtime_touch_allowed",
        "capital_change_allowed",
        "active_paper_allowed",
        "live_allowed",
        "real_orders_allowed",
    ]:
        lines.append(f"{k}: {policy.get(k)}")

    return "\n".join(lines)


def summary_text(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS RESEARCH GATE TIGHTENING POLICY BUILDER v1")
    lines.append("=" * 100)

    for k in [
        "builder_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "policy_status",
        "policy_hash",
        "research_gate_tightening_required",
        "plugin_expansion_allowed_before_policy_validation",
        "max_allowed_strict_12_any_random_hit_rate",
        "max_allowed_null_adjusted_any_random_hit_rate",
        "minimum_permutation_runs",
        "required_independent_null_models",
        "next_recommended_research_key",
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
        "next_queue_json",
        "enforced_policy_json",
        "enforced_policy_txt",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS RESEARCH GATE TIGHTENING POLICY BUILDER v1")
    print("=" * 100)
    print(f"builder_status: {result.get('builder_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"policy_status: {result.get('policy_status')}")
    print(f"policy_hash: {result.get('policy_hash')}")
    print(f"research_gate_tightening_required: {result.get('research_gate_tightening_required')}")
    print(f"plugin_expansion_allowed_before_policy_validation: {result.get('plugin_expansion_allowed_before_policy_validation')}")
    print(f"max_allowed_strict_12_any_random_hit_rate: {result.get('max_allowed_strict_12_any_random_hit_rate')}")
    print(f"max_allowed_null_adjusted_any_random_hit_rate: {result.get('max_allowed_null_adjusted_any_random_hit_rate')}")
    print(f"minimum_permutation_runs: {result.get('minimum_permutation_runs')}")
    print(f"required_independent_null_models: {result.get('required_independent_null_models')}")
    print(f"next_recommended_research_key: {result.get('next_recommended_research_key')}")
    print(f"next_module: {result.get('next_module')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"POLICY: {result.get('enforced_policy_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FRAMEWORK_POLICY_DIR.mkdir(parents=True, exist_ok=True)

    evaluator = load_json(EVALUATOR_JSON, default={})
    queue = load_json(NEXT_QUEUE_JSON, default={})
    runner = load_json(RUNNER_JSON, default={})
    draft_policy = load_json(POLICY_DRAFT_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})
    lesson_index = load_json(LESSON_INDEX_PATH, default={})
    blocklist = load_json(BLOCKLIST_PATH, default={})

    top_queue = extract_top_queue(queue, evaluator)

    evaluator_status = evaluator.get("evaluator_status")
    decision_class = evaluator.get("decision_class")
    top_key = top_queue.get("research_key") or evaluator.get("next_recommended_research_key")
    top_module = top_queue.get("next_module_recommendation") or evaluator.get("next_module")

    research_gate_tightening_required = bool(evaluator.get("research_gate_tightening_required"))
    plugin_expansion_allowed = bool(evaluator.get("plugin_expansion_allowed"))
    guard_pass = bool(guard_feed.get("guard_pass"))

    prerequisite_pass = (
        evaluator_status == REQUIRED_EVALUATOR_STATUS
        and decision_class == REQUIRED_DECISION_CLASS
        and top_key == REQUIRED_NEXT_RESEARCH_KEY
        and research_gate_tightening_required is True
        and plugin_expansion_allowed is False
        and guard_pass is True
    )

    policy = build_enforcement_policy(evaluator, runner, draft_policy, guard_feed)
    rules = policy["enforced_gate_rules"]

    if prerequisite_pass:
        builder_status = "RESEARCH_GATE_TIGHTENING_POLICY_READY"
        severity = "ATTENTION"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        next_action = "BUILD_STRONGER_NULL_MODEL_BASELINE_CONTRACT_OR_VALIDATE_POLICY"
        reason = (
            f"false_positive_baseline_high=True; policy_hash={policy.get('policy_hash')}; "
            "plugin_expansion_blocked_until_policy_validation=True"
        )
        next_key = NEXT_RESEARCH_KEY
        next_module = NEXT_MODULE
        return_code = 0
    else:
        builder_status = "RESEARCH_GATE_TIGHTENING_POLICY_BLOCKED_PREREQUISITE_NOT_MET"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_NULL_MODEL_EVALUATOR_POLICY_PREREQUISITES"
        reason = (
            f"evaluator_status={evaluator_status}; decision_class={decision_class}; "
            f"top_key={top_key}; top_module={top_module}; "
            f"research_gate_tightening_required={research_gate_tightening_required}; "
            f"plugin_expansion_allowed={plugin_expansion_allowed}; guard_pass={guard_pass}"
        )
        next_key = None
        next_module = None
        return_code = 2

    next_queue = {
        "created_at_utc": utc_now_iso(),
        "queue_status": "RESEARCH_GATE_TIGHTENING_NEXT_QUEUE_READY" if prerequisite_pass else "RESEARCH_GATE_TIGHTENING_NEXT_QUEUE_BLOCKED",
        "source_builder": "edge_factory_os_research_gate_tightening_policy_builder_v1",
        "policy_hash": policy.get("policy_hash"),
        "research_gate_tightening_required": True,
        "plugin_expansion_allowed_before_policy_validation": False,
        "top_next_research_key": next_key,
        "top_next_module": next_module,
        "next_direction_queue": [
            {
                "research_key": NEXT_RESEARCH_KEY,
                "priority": 100,
                "next_module_recommendation": NEXT_MODULE,
                "allowed_scope": "READ_ONLY_RESEARCH",
                "why": "False-positive risk is high; rebuild stronger null/permutation baseline under tighter gates.",
                "must_consume_guard_feed": True,
                "must_consume_research_gate_policy": True,
                "must_not_reopen_blocked_routes": True,
                "candidate_generation_allowed_now": False,
                "candidate_contract_allowed_now": False,
                "family_release_allowed_now": False,
                "runtime_touch_allowed_now": False,
                "capital_change_allowed_now": False,
                "active_paper_allowed_now": False,
                "live_allowed_now": False,
                "real_orders_allowed_now": False,
            },
            {
                "research_key": ALT_RESEARCH_KEY,
                "priority": 80,
                "next_module_recommendation": ALT_MODULE,
                "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
                "why": "Validate that future contracts/runners consume the tightened gate policy before more research.",
                "must_consume_guard_feed": True,
                "must_consume_research_gate_policy": True,
                "candidate_generation_allowed_now": False,
                "family_release_allowed_now": False,
            },
        ] if prerequisite_pass else [],
        "candidate_generation_allowed": False,
        "candidate_contract_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
    }

    if prerequisite_pass:
        write_json(ENFORCED_POLICY_JSON, policy)
        write_text(ENFORCED_POLICY_TXT, policy_text(policy))
        write_json(OUT_QUEUE_JSON, next_queue)

    result = {
        "builder_name": "edge_factory_os_research_gate_tightening_policy_builder_v1",
        "created_at_utc": utc_now_iso(),
        "builder_status": builder_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "policy_status": policy.get("policy_status"),
        "policy_hash": policy.get("policy_hash"),
        "strict_policy_key": STRICT_POLICY_KEY,
        "research_gate_tightening_required": True,
        "plugin_expansion_allowed_before_policy_validation": False,
        "max_allowed_strict_12_any_random_hit_rate": rules.get("max_allowed_strict_12_any_random_hit_rate"),
        "max_allowed_null_adjusted_any_random_hit_rate": rules.get("max_allowed_null_adjusted_any_random_hit_rate"),
        "empirical_p_value_required_lte": rules.get("empirical_p_value_required_lte"),
        "minimum_permutation_runs": rules.get("minimum_permutation_runs"),
        "required_independent_null_models": rules.get("required_independent_null_models"),
        "required_canonical_months": rules.get("required_canonical_months"),
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        "lessons_count": extract_lessons_count(lesson_index),
        "blocked_route_count": extract_blocked_count(blocklist),
        "policy": policy,
        "release_gate_feed": {
            "RESEARCH_GATE_TIGHTENING_POLICY_READY": prerequisite_pass,
            "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE": prerequisite_pass,
            "PLUGIN_EXPANSION_ALLOWED_BEFORE_POLICY_VALIDATION": False,
            "STRICT_MONTH_STABILITY_12_OF_12": True,
            "RELEASE_PASS_FROM_THIS_POLICY_BUILDER": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_THIS_POLICY_BUILDER": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_THIS_POLICY_BUILDER": False,
            "FAMILY_RELEASE_ALLOWED_FROM_THIS_POLICY_BUILDER": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_THIS_POLICY_BUILDER": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_THIS_POLICY_BUILDER": False,
            "ACTIVE_PAPER_ALLOWED_FROM_THIS_POLICY_BUILDER": False,
            "LIVE_ALLOWED_FROM_THIS_POLICY_BUILDER": False,
            "REAL_ORDERS_ALLOWED_FROM_THIS_POLICY_BUILDER": False,
        },
        "input_paths": {
            "evaluator_json": str(EVALUATOR_JSON),
            "next_queue_json": str(NEXT_QUEUE_JSON),
            "runner_json": str(RUNNER_JSON),
            "policy_draft_json": str(POLICY_DRAFT_JSON),
            "guard_feed_json": str(GUARD_FEED_JSON),
            "lesson_index_path": str(LESSON_INDEX_PATH),
            "blocklist_path": str(BLOCKLIST_PATH),
        },
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "next_queue_json": str(OUT_QUEUE_JSON),
        "enforced_policy_json": str(ENFORCED_POLICY_JSON),
        "enforced_policy_txt": str(ENFORCED_POLICY_TXT),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, summary_text(result))
    print_summary(result)
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
