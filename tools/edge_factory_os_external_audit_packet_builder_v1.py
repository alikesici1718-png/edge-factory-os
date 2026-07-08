#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - External Audit Packet Builder v1

Purpose:
- Stop forward research escalation.
- Build a compact adversarial audit packet for Claude / external model review.
- Summarize current framework, policy, guard, null, lesson/blocklist, route history, and latest preview.
- Explicitly ask about overfitting, multiple testing, leakage, null methodology, and whether to continue.
- Keep all candidate/family/runtime/capital/live/real-order actions blocked.

This module does NOT:
- run research
- generate candidates
- release families
- touch runtime
- change capital
- call external APIs
- delete/move/archive files
"""

from __future__ import annotations

import csv
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

OUT_DIR = BASE_DIR / "edge_factory_os_external_audit_packet"
OUT_JSON = OUT_DIR / "external_audit_packet_latest.json"
OUT_TXT = OUT_DIR / "external_audit_packet_for_claude_latest.txt"

FRAMEWORK_STATUS_JSON = REPO_DIR / "edge_factory_os_framework" / "status" / "framework_status_panel_v1.json"
RESEARCH_GATE_POLICY_JSON = REPO_DIR / "edge_factory_os_framework" / "policies" / "research_gate_enforcement_policy_v1.json"
RESEARCH_GATE_VALIDATION_JSON = REPO_DIR / "edge_factory_os_framework" / "policies" / "research_gate_validation_state_v1.json"
TRUE_SOURCE_NULL_STATE_JSON = REPO_DIR / "edge_factory_os_framework" / "policies" / "true_source_panel_empirical_null_baseline_state_v1.json"
DATA_QUALITY_GUARD_JSON = BASE_DIR / "edge_factory_os_data_quality_guard_runner" / "data_quality_guard_feed_latest.json"

LESSON_INDEX_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

MARKET_STATE_RUNNER_JSON = BASE_DIR / "edge_factory_os_market_state_transition_runner" / "market_state_transition_runner_latest.json"
MARKET_STATE_SUMMARY_CSV = BASE_DIR / "edge_factory_os_market_state_transition_runner" / "market_state_transition_summary_latest.csv"
MARKET_STATE_POLICY_GATE_CSV = BASE_DIR / "edge_factory_os_market_state_transition_runner" / "market_state_transition_policy_gate_pass_fail_latest.csv"
MARKET_STATE_TRUE_NULL_CSV = BASE_DIR / "edge_factory_os_market_state_transition_runner" / "market_state_transition_true_source_panel_null_rerun_latest.csv"
MARKET_STATE_NEGATIVE_CSV = BASE_DIR / "edge_factory_os_market_state_transition_runner" / "market_state_transition_negative_controls_latest.csv"
MARKET_STATE_MATERIAL_CSV = BASE_DIR / "edge_factory_os_market_state_transition_runner" / "market_state_transition_material_difference_report_latest.csv"

SOURCE_ANOMALY_DEEP_EVAL_JSON = BASE_DIR / "edge_factory_os_source_panel_anomaly_deep_validation_evaluator" / "source_panel_anomaly_deep_validation_evaluator_latest.json"
SOURCE_ANOMALY_DEEP_STATE_JSON = REPO_DIR / "edge_factory_os_framework" / "policies" / "source_panel_anomaly_deep_validation_state_v1.json"

MODULE_CONSOLIDATION_JSON = BASE_DIR / "edge_factory_os_module_consolidation_planner" / "module_consolidation_plan_latest.json"
ACTIVE_CORE_JSON = BASE_DIR / "edge_factory_os_active_core_manifest" / "active_core_manifest_latest.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

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


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def load_json(path: Path, default: Any = None) -> Any:
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_load_error": f"{type(exc).__name__}: {exc}", "_path": str(path)}


def read_csv_rows(path: Path, limit: int = 25) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= limit:
                    break
                rows.append(dict(row))
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


def compact_json(obj: Any, max_chars: int = 5000) -> str:
    text = json.dumps(obj, indent=2, ensure_ascii=False, default=str)
    if len(text) > max_chars:
        return text[:max_chars] + "\n...TRUNCATED..."
    return text


def build_claude_prompt(packet: Dict[str, Any]) -> str:
    latest = packet.get("latest_market_state_transition", {})
    safety = packet.get("safety", {})

    prompt = f"""
You are auditing an algorithmic trading research operating system called Edge Factory OS.

The user is worried that the system is drifting into overfitting / multiple-testing even though safety gates remain blocked.

Your task:
1. Be adversarial.
2. Identify overfitting, multiple testing, data leakage, null model, false positive, and research-process risks.
3. Decide whether the current research path should continue, be redesigned, or be frozen.
4. Do NOT recommend live trading, real orders, capital increase, active paper, or candidate release unless every prerequisite is truly satisfied.
5. Prefer saying "blocked" if evidence is weak.

Current hard safety state:
- candidate_generation_allowed={safety.get("candidate_generation_allowed")}
- candidate_contract_allowed={safety.get("candidate_contract_allowed")}
- family_release_allowed={safety.get("family_release_allowed")}
- runtime_touch_allowed={safety.get("runtime_touch_allowed")}
- capital_change_allowed={safety.get("capital_change_allowed")}
- active_paper_allowed={safety.get("active_paper_allowed")}
- live_allowed={safety.get("live_allowed")}
- real_orders_allowed={safety.get("real_orders_allowed")}

Strict policy:
- {STRICT_POLICY_KEY}
- canonical months must be 12, not raw 13 calendar buckets.
- 12/12 month stability is required for any serious promotion chain.
- Current result is research-only, not release.

Latest market-state transition runner:
- runner_status={latest.get("runner_status")}
- research_key={latest.get("research_key")}
- row_count={latest.get("row_count")}
- symbol_count={latest.get("symbol_count")}
- raw_calendar_month_count={latest.get("raw_calendar_month_count")}
- canonical_policy_month_count={latest.get("canonical_policy_month_count")}
- selected_state_feature_count={latest.get("selected_state_feature_count")}
- transition_method_count={latest.get("transition_method_count")}
- transition_axis_count={latest.get("transition_axis_count")}
- strict_12_transition_preview_count={latest.get("strict_12_transition_preview_count")}
- negative_control_count={latest.get("negative_control_count")}
- true_null_runs={latest.get("true_null_runs")}
- max_strict_12_any_random_hit_rate={latest.get("max_strict_12_any_random_hit_rate")}
- max_null_adjusted_any_random_hit_rate={latest.get("max_null_adjusted_any_random_hit_rate")}
- policy_gate_pass={latest.get("policy_gate_pass")}
- failed_gate_keys={latest.get("failed_gate_keys")}
- release_allowed={latest.get("release_allowed")}

Important history:
- Many prior branches failed strict 12/12 month stability or deep validation.
- Source-panel anomaly preview initially passed true-null, then failed deep validation on:
  FEATURE_THRESHOLD_PERTURBATION, NEGATIVE_CONTROLS_RERUN, TRUE_SOURCE_PANEL_NULL_RERUN_PASS.
- The system then rotated to outcome-agnostic market-state transitions.
- Latest market-state transition found 3 strict previews among 160 transition axes with null rates 0.0.
- This may still be overfit due to repeated route exploration and many degrees of freedom.

Please audit the packet below.

I need your answer in this structure:

A) Verdict:
- OK_TO_CONTINUE_RESEARCH
- CONTINUE_ONLY_AFTER_REDESIGN
- FREEZE_RESEARCH_AND_REPAIR_METHODOLOGY
- BLOCK_ALL_PROMOTION

B) Biggest risks:
List the top 10 risks, especially overfitting/multiple-testing.

C) Specific red flags in current numbers:
Use the supplied stats.

D) Required repairs before continuing:
Concrete methodology changes.

E) What to do next:
Give exact next module recommendation.

F) What must remain blocked:
Explicitly state candidate/family/runtime/capital/live/real orders remain blocked.

G) If you think the current market-state transition result is invalid:
Explain why and what evidence would be needed.

Full audit packet follows:

{compact_json(packet, max_chars=50000)}
"""
    return prompt.strip()


def build_summary_text(packet: Dict[str, Any]) -> str:
    latest = packet.get("latest_market_state_transition", {})
    source_fail = packet.get("source_panel_anomaly_deep_validation", {})
    framework = packet.get("framework_status", {})

    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS EXTERNAL AUDIT PACKET v1")
    lines.append("=" * 100)
    lines.append("")
    lines.append("PURPOSE")
    lines.append("-" * 100)
    lines.append("External adversarial audit before continuing research due to overfitting / multiple-testing risk.")
    lines.append("No candidate, family, runtime, capital, active paper, live, or real-order action is allowed.")
    lines.append("")
    lines.append("FRAMEWORK STATUS")
    lines.append("-" * 100)
    lines.append(f"framework_panel_status: {framework.get('panel_status')}")
    lines.append(f"policy_active: {packet.get('research_gate_policy', {}).get('policy_status')}")
    lines.append(f"validator_pass: {packet.get('research_gate_validation', {}).get('validator_pass')}")
    lines.append(f"true_source_false_positive_repaired: {packet.get('true_source_null_state', {}).get('false_positive_methodology_repaired')}")
    lines.append(f"actual_signal_present: {packet.get('true_source_null_state', {}).get('actual_signal_present')}")
    lines.append("")
    lines.append("LATEST MARKET STATE TRANSITION RESULT")
    lines.append("-" * 100)
    for key in [
        "runner_status",
        "research_key",
        "row_count",
        "symbol_count",
        "raw_calendar_month_count",
        "canonical_policy_month_count",
        "selected_state_feature_count",
        "transition_method_count",
        "transition_axis_count",
        "strict_12_transition_preview_count",
        "negative_control_count",
        "true_null_runs",
        "max_strict_12_any_random_hit_rate",
        "max_null_adjusted_any_random_hit_rate",
        "policy_gate_pass",
        "policy_gate_fail_count",
        "failed_gate_keys",
        "release_allowed",
    ]:
        lines.append(f"{key}: {latest.get(key)}")

    lines.append("")
    lines.append("PRIOR SOURCE PANEL ANOMALY FAILURE")
    lines.append("-" * 100)
    for key in [
        "evaluator_status",
        "decision_class",
        "route_closed",
        "redesign_allowed",
        "release_allowed",
        "failed_gate_keys",
        "validation_test_count",
        "validation_pass_count",
        "validation_fail_count",
        "preview_axis_key",
        "preview_feature",
        "preview_side",
    ]:
        lines.append(f"{key}: {source_fail.get(key)}")

    lines.append("")
    lines.append("AUDIT QUESTIONS")
    lines.append("-" * 100)
    for q in packet.get("audit_questions", []):
        lines.append(f"- {q}")

    lines.append("")
    lines.append("CLAUDE PROMPT")
    lines.append("-" * 100)
    lines.append(packet.get("claude_prompt", ""))

    return "\n".join(lines)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    framework_status = load_json(FRAMEWORK_STATUS_JSON, {})
    policy = load_json(RESEARCH_GATE_POLICY_JSON, {})
    validation = load_json(RESEARCH_GATE_VALIDATION_JSON, {})
    true_null = load_json(TRUE_SOURCE_NULL_STATE_JSON, {})
    guard = load_json(DATA_QUALITY_GUARD_JSON, {})
    lessons = extract_lessons(load_json(LESSON_INDEX_JSON, {}))
    blocklist = extract_blocked_routes(load_json(BLOCKLIST_JSON, {}))

    market_runner = load_json(MARKET_STATE_RUNNER_JSON, {})
    market_summary = read_csv_rows(MARKET_STATE_SUMMARY_CSV, limit=20)
    market_policy_gate = read_csv_rows(MARKET_STATE_POLICY_GATE_CSV, limit=50)
    market_true_null = read_csv_rows(MARKET_STATE_TRUE_NULL_CSV, limit=25)
    market_negative = read_csv_rows(MARKET_STATE_NEGATIVE_CSV, limit=25)
    market_material = read_csv_rows(MARKET_STATE_MATERIAL_CSV, limit=25)

    anomaly_deep_eval = load_json(SOURCE_ANOMALY_DEEP_EVAL_JSON, {})
    anomaly_deep_state = load_json(SOURCE_ANOMALY_DEEP_STATE_JSON, {})

    module_plan = load_json(MODULE_CONSOLIDATION_JSON, {})
    active_core = load_json(ACTIVE_CORE_JSON, {})

    audit_questions = [
        "Is the latest market-state transition preview likely overfit due to 160 tested transition axes?",
        "Are 1000 true-null runs enough after this much route exploration?",
        "Do null models account for cross-sectional/time dependence, or are they too easy?",
        "Are strict 12/12 month gates sufficient when many routes have been tried?",
        "Should the system apply family-wise error correction or nested holdout before any further research?",
        "Is there leakage risk in derived state features even though future returns are excluded?",
        "Should research freeze until a global multiple-testing ledger exists?",
        "Should the next module be evaluator/deep validation or methodology repair?",
        "What exact evidence would be needed before candidate generation is even considered?",
        "What should stay permanently blocked right now?",
    ]

    safety = dict(SAFETY_FLAGS)

    packet = {
        "packet_name": "edge_factory_os_external_audit_packet_v1",
        "created_at_utc": utc_now_iso(),
        "audit_reason": "User raised overfitting/multiple-testing risk after market-state transition preview found 3 strict_12 transition previews among 160 axes.",
        "strict_policy_key": STRICT_POLICY_KEY,
        "framework_status": framework_status,
        "research_gate_policy": policy,
        "research_gate_validation": validation,
        "true_source_null_state": true_null,
        "data_quality_guard": guard,
        "lesson_count": len(lessons),
        "blocked_route_count": len(blocklist),
        "recent_lessons_tail": lessons[-20:],
        "blocked_routes_tail": blocklist[-30:],
        "latest_market_state_transition": market_runner,
        "latest_market_state_transition_top_rows": market_summary,
        "latest_market_state_transition_policy_gates": market_policy_gate,
        "latest_market_state_transition_true_null": market_true_null,
        "latest_market_state_transition_negative_controls": market_negative,
        "latest_market_state_transition_material_difference": market_material,
        "source_panel_anomaly_deep_validation": anomaly_deep_eval,
        "source_panel_anomaly_deep_validation_state": anomaly_deep_state,
        "module_consolidation_plan": module_plan,
        "active_core_manifest": active_core,
        "audit_questions": audit_questions,
        "must_not_recommend": [
            "candidate generation",
            "candidate contract",
            "family release",
            "runtime touch",
            "capital change",
            "active paper",
            "live trading",
            "real orders",
        ],
        "safety": safety,
        "recommended_current_pause": {
            "pause_forward_research": True,
            "do_not_build_market_state_evaluator_until_external_audit_reviewed": True,
            "reason": "Increasing route/axis exploration creates overfitting risk even when local true-null gates pass.",
        },
        **SAFETY_FLAGS,
    }

    packet["claude_prompt"] = build_claude_prompt(packet)

    write_json(OUT_JSON, packet)
    write_text(OUT_TXT, build_summary_text(packet))

    print("")
    print("=" * 100)
    print("EDGE FACTORY OS EXTERNAL AUDIT PACKET BUILDER v1")
    print("=" * 100)
    print("packet_status: EXTERNAL_AUDIT_PACKET_READY")
    print("severity: ATTENTION")
    print("allowed_scope: REPO_ONLY_OS_INTELLIGENCE")
    print("next_action: PASTE_EXTERNAL_AUDIT_PACKET_TO_CLAUDE_BEFORE_CONTINUING_RESEARCH")
    print("reason: overfitting_multiple_testing_risk_after_market_state_transition_preview")
    print(f"latest_runner_status: {market_runner.get('runner_status')}")
    print(f"transition_axis_count: {market_runner.get('transition_axis_count')}")
    print(f"strict_12_transition_preview_count: {market_runner.get('strict_12_transition_preview_count')}")
    print(f"max_strict_12_any_random_hit_rate: {market_runner.get('max_strict_12_any_random_hit_rate')}")
    print(f"max_null_adjusted_any_random_hit_rate: {market_runner.get('max_null_adjusted_any_random_hit_rate')}")
    print(f"lesson_count: {len(lessons)}")
    print(f"blocked_route_count: {len(blocklist)}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        print(f"{key}: {value}")
    print("")
    print(f"JSON: {OUT_JSON}")
    print(f"TXT : {OUT_TXT}")
    print("=" * 100)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
