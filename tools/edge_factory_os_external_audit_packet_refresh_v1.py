#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - External Audit Packet Refresh v1

Purpose:
- Build an external/red-team audit packet from current governance state.
- Clearly separate failed/closed research routes from runtime family monitoring.
- Explicitly include old_short as a currently non-invalidated runtime family from prior monitoring.
- Include impulse_long / market_relative_short warnings separately.
- Include overfitting, null-power, holdout, alpha-accounting, and route closure state.
- Do NOT execute research.
- Do NOT generate candidates.
- Do NOT release families.
- Do NOT touch runtime/capital/live.
"""

from __future__ import annotations

import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = BASE_DIR / "edge_factory_os_repo"

FRAMEWORK_DIR = REPO_DIR / "edge_factory_os_framework"
POLICY_DIR = FRAMEWORK_DIR / "policies"
QUEUE_DIR = FRAMEWORK_DIR / "queues"
CONTRACT_DIR = FRAMEWORK_DIR / "contracts"
REGISTRY_DIR = FRAMEWORK_DIR / "registries"
AUDIT_DIR = FRAMEWORK_DIR / "audit"

CONTRACT_JSON = CONTRACT_DIR / "policy_locked_research_direction_contract_v1.json"
BUILDER_STATE_JSON = POLICY_DIR / "policy_locked_research_direction_contract_builder_state_v1.json"
ROTATION_STATE_JSON = POLICY_DIR / "policy_locked_research_rotation_after_restricted_retest_state_v1.json"
CLOSED_ROUTE_REGISTRY_JSON = POLICY_DIR / "restricted_retest_closed_route_registry_v1.json"

GLOBAL_LEDGER_JSON = POLICY_DIR / "global_multiple_testing_ledger_v1.json"
RESEARCH_BUDGET_POLICY_JSON = POLICY_DIR / "research_budget_policy_v1.json"
PROMISING_VAULT_JSON = POLICY_DIR / "promising_signal_vault_v1.json"
ANTI_OVERFIT_JSON = POLICY_DIR / "anti_overfitting_governance_state_v1.json"
PRE_REG_POLICY_JSON = POLICY_DIR / "pre_registration_policy_v1.json"
NESTED_VALIDATION_JSON = POLICY_DIR / "nested_validation_policy_v1.json"
UNTOUCHED_HOLDOUT_REGISTRY_JSON = REGISTRY_DIR / "untouched_holdout_registry_v1.json"
HOLDOUT_ACCESS_JSON = POLICY_DIR / "holdout_access_control_policy_v1.json"
GLOBAL_ALPHA_ACCOUNTING_JSON = POLICY_DIR / "global_route_family_alpha_accounting_v1.json"
GLOBAL_ALPHA_POLICY_JSON = POLICY_DIR / "global_alpha_spending_policy_v1.json"

RESTRICTED_RETEST_EVALUATOR_JSON = POLICY_DIR / "restricted_market_state_structure_retest_evaluator_state_v1.json"
RESTRICTED_NULL_POWER_JSON = POLICY_DIR / "restricted_null_power_feasibility_review_state_v1.json"

LESSON_INDEX_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

OUT_DIR = BASE_DIR / "edge_factory_os_external_audit_packet_refresh"
OUT_JSON = OUT_DIR / "external_audit_packet_refresh_latest.json"
OUT_TXT = OUT_DIR / "external_audit_packet_refresh_latest.txt"

REPO_PACKET_JSON = AUDIT_DIR / "external_audit_packet_refresh_v1.json"
REPO_PACKET_TXT = AUDIT_DIR / "external_audit_packet_refresh_v1.txt"
REPO_MANIFEST_JSON = AUDIT_DIR / "audit_packet_manifest_v1.json"
REPO_PROMPT_TXT = AUDIT_DIR / "audit_prompt_red_team_packet_v1.txt"
REPO_STATE_JSON = POLICY_DIR / "external_audit_packet_refresh_state_v1.json"
REPO_NEXT_QUEUE_JSON = QUEUE_DIR / "external_audit_packet_refresh_next_queue_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD8_03_EXTERNAL_AUDIT_RESPONSE_INTEGRATION_OR_SOURCE_PANEL_INFO_REVIEW"
NEXT_MODULE = "edge_factory_os_external_audit_response_integrator_or_source_panel_info_review_v1.py"

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


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    tmp.replace(path)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def extract_list(obj: Any, key: str) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get(key), list):
        return [x for x in obj[key] if isinstance(x, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def get_git_status() -> Dict[str, Any]:
    try:
        proc = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(REPO_DIR),
            text=True,
            capture_output=True,
            timeout=30,
        )
        lines = [x for x in proc.stdout.splitlines() if x.strip()]
        return {
            "git_status_command_returncode": proc.returncode,
            "git_status_short_lines": lines,
            "git_untracked_or_dirty_count": len(lines),
            "git_status_stderr": proc.stderr.strip(),
        }
    except Exception as exc:
        return {
            "git_status_command_returncode": None,
            "git_status_short_lines": [],
            "git_untracked_or_dirty_count": None,
            "git_status_error": f"{type(exc).__name__}: {exc}",
        }


def summarize_json_file(path: Path, keys: List[str]) -> Dict[str, Any]:
    obj = load_json(path, {})
    return {
        "path": str(path),
        "exists": path.exists(),
        "selected_fields": {k: obj.get(k) for k in keys} if isinstance(obj, dict) else {},
        "load_error": obj.get("_load_error") if isinstance(obj, dict) else None,
    }


def collect_runtime_family_prior_snapshot() -> Dict[str, Any]:
    """
    This is intentionally labelled as prior snapshot, not current proof.
    Current runtime should be re-checked separately by runtime monitors.
    """
    return {
        "snapshot_type": "PRIOR_MONITORING_SUMMARY_NOT_CURRENT_PROOF",
        "important_warning": "Do not mix runtime family monitoring with failed research-route validation.",
        "families": {
            "old_short": {
                "prior_status": "OK_OR_POSITIVE_INFO_IN_PRIOR_MONITORING",
                "prior_notes": [
                    "Previously seen as OK/HAS_CLOSED_SAMPLE.",
                    "Earlier family performance snapshot showed old_short positive with roughly 5 closed trades and around 80% win rate.",
                    "No direct invalidation of old_short occurred in the anti-overfitting research-route work.",
                    "Still requires current runtime sample, drift review, and capital governor before any promotion/capital action.",
                ],
                "audit_instruction": "Protect from being incorrectly grouped with failed research routes; verify current metrics before any decision.",
            },
            "impulse_long": {
                "prior_status": "NEGATIVE_OR_EARLY_WATCH_IN_PRIOR_MONITORING",
                "prior_notes": [
                    "Previously identified as negative_watch family.",
                    "Anti-overfitting research work repeatedly touched impulse/market-state style hypotheses, but that does not automatically equal runtime family release decision.",
                ],
                "audit_instruction": "Review separately from old_short; do not allow promotion without family-specific evidence.",
            },
            "market_relative_short": {
                "prior_status": "ATTENTION_IN_PRIOR_EXPOSURE_MONITORING",
                "prior_notes": [
                    "Previously had high exposure / no closed sample attention.",
                    "Needs closed sample and exposure review.",
                ],
                "audit_instruction": "Treat as monitoring risk, not validated edge.",
            },
            "weak_market_short": {
                "prior_status": "INCONCLUSIVE_OR_LOW_EXPOSURE_PRIOR_MONITORING",
                "prior_notes": [
                    "Previously had little/no closed sample.",
                    "Needs more data before decisions.",
                ],
                "audit_instruction": "No release/capital action without sample.",
            },
        },
    }


def build_audit_prompt(packet: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("EDGE FACTORY OS - EXTERNAL / RED-TEAM AUDIT REQUEST")
    lines.append("=" * 100)
    lines.append("")
    lines.append("You are auditing an automated trading research OS. Be adversarial.")
    lines.append("Your job is to find ways the system can still fool itself.")
    lines.append("")
    lines.append("CRITICAL CONTEXT")
    lines.append("- Broad strategy search is currently blocked.")
    lines.append("- Candidate generation is blocked.")
    lines.append("- Family release is blocked.")
    lines.append("- Runtime/capital/active-paper/live/real orders are blocked.")
    lines.append("- The final holdout is unselected, unpeeked, and unusable.")
    lines.append("- Many research routes were closed due overfitting/null/power failures.")
    lines.append("- Runtime family monitoring must not be confused with research route failures.")
    lines.append("")
    lines.append("SPECIFIC REQUESTS")
    lines.append("1. Identify any remaining overfitting, leakage, multiple-testing, or post-hoc selection risk.")
    lines.append("2. Decide whether any gate is too easy to satisfy or circular.")
    lines.append("3. Check whether the route-family alpha accounting is strict enough.")
    lines.append("4. Check whether the restricted market-state retest closure is correct.")
    lines.append("5. Check whether old_short is being unfairly punished by unrelated failed research routes.")
    lines.append("6. Tell us what to build next: data-information review, architecture consolidation, or runtime family monitor refresh.")
    lines.append("7. Default stance: no more budget, no candidate, no release unless evidence is exceptional.")
    lines.append("")
    lines.append("RUNTIME FAMILY DISTINCTION")
    lines.append("- old_short: prior monitoring positive/OK; not invalidated by research route failures; must be rechecked with current sample before action.")
    lines.append("- impulse_long: prior negative/early watch.")
    lines.append("- market_relative_short: prior exposure/no closed sample attention.")
    lines.append("- weak_market_short: inconclusive.")
    lines.append("")
    lines.append("OUTPUT FORMAT REQUEST")
    lines.append("- Verdict: PASS / FAIL / REVIEW_REQUIRED")
    lines.append("- Top 10 risks.")
    lines.append("- Any gate that must be strengthened.")
    lines.append("- Whether old_short should be protected, paused, or further monitored.")
    lines.append("- Next safest module.")
    lines.append("")
    lines.append("PACKET JSON SUMMARY")
    lines.append(json.dumps(packet.get("summary_for_external_auditor", {}), indent=2, ensure_ascii=False))
    return "\n".join(lines)


def build_packet_text(packet: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS EXTERNAL AUDIT PACKET REFRESH v1")
    lines.append("=" * 100)
    lines.append(f"packet_status: {packet.get('packet_status')}")
    lines.append(f"created_at_utc: {packet.get('created_at_utc')}")
    lines.append(f"selected_audit_focus: {packet.get('selected_audit_focus')}")
    lines.append(f"runtime_family_section_included: {packet.get('runtime_family_section_included')}")
    lines.append(f"old_short_status_included: {packet.get('old_short_status_included')}")
    lines.append("")
    lines.append("SUMMARY FOR AUDITOR")
    lines.append("-" * 100)
    lines.append(json.dumps(packet.get("summary_for_external_auditor", {}), indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("RUNTIME FAMILY PRIOR SNAPSHOT")
    lines.append("-" * 100)
    lines.append(json.dumps(packet.get("runtime_family_prior_snapshot", {}), indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("GOVERNANCE COMPONENTS")
    lines.append("-" * 100)
    for item in packet.get("governance_component_summaries", []):
        lines.append(json.dumps(item, ensure_ascii=False))
    lines.append("")
    lines.append("GIT STATUS")
    lines.append("-" * 100)
    lines.append(json.dumps(packet.get("git_status", {}), indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("QUESTIONS FOR EXTERNAL AUDIT")
    lines.append("-" * 100)
    for q in packet.get("questions_for_external_audit", []):
        lines.append(f"- {q}")
    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS EXTERNAL AUDIT PACKET REFRESH v1")
    print("=" * 100)
    print(f"packet_status: {result.get('packet_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"selected_audit_focus: {result.get('selected_audit_focus')}")
    print(f"runtime_family_section_included: {result.get('runtime_family_section_included')}")
    print(f"old_short_status_included: {result.get('old_short_status_included')}")
    print(f"closed_route_hash: {result.get('closed_route_hash')}")
    print(f"closed_route_family: {result.get('closed_route_family')}")
    print(f"restricted_route_closed: {result.get('restricted_route_closed')}")
    print(f"git_untracked_or_dirty_count: {result.get('git_untracked_or_dirty_count')}")
    print(f"next_recommended_research_key: {result.get('next_recommended_research_key')}")
    print(f"next_module: {result.get('next_module')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        print(f"{key}: {value}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"PROMPT: {result.get('audit_prompt_txt')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    contract = load_json(CONTRACT_JSON, {})
    builder_state = load_json(BUILDER_STATE_JSON, {})
    rotation_state = load_json(ROTATION_STATE_JSON, {})
    closed_registry = load_json(CLOSED_ROUTE_REGISTRY_JSON, {})
    feasibility_state = load_json(RESTRICTED_NULL_POWER_JSON, {})
    retest_eval_state = load_json(RESTRICTED_RETEST_EVALUATOR_JSON, {})

    vault = load_json(PROMISING_VAULT_JSON, {})
    lessons = extract_list(load_json(LESSON_INDEX_JSON, {}), "lessons")
    blocked_routes = extract_list(load_json(BLOCKLIST_JSON, {}), "blocked_routes")
    vault_items = extract_list(vault, "vault_items")
    git_status = get_git_status()

    closed_route_hash = (
        closed_registry.get("closed_route_hash")
        or rotation_state.get("closed_route_hash")
        or feasibility_state.get("route_hash")
    )
    closed_route_family = (
        closed_registry.get("closed_route_family")
        or rotation_state.get("closed_route_family")
        or feasibility_state.get("route_family")
    )

    component_summaries = [
        summarize_json_file(GLOBAL_LEDGER_JSON, ["ledger_status", "market_state_route_status", "effective_comparison_count", "diagnostic_alpha_after_pressure"]),
        summarize_json_file(RESEARCH_BUDGET_POLICY_JSON, ["policy_status", "research_budget_status"]),
        summarize_json_file(PROMISING_VAULT_JSON, ["vault_status", "vault_item_count_after"]),
        summarize_json_file(ANTI_OVERFIT_JSON, ["state_status"]),
        summarize_json_file(PRE_REG_POLICY_JSON, ["policy_status", "all_future_research_must_be_pre_registered"]),
        summarize_json_file(NESTED_VALIDATION_JSON, ["policy_status"]),
        summarize_json_file(UNTOUCHED_HOLDOUT_REGISTRY_JSON, ["registry_status", "holdout_selected", "holdout_peeked", "holdout_usable_now"]),
        summarize_json_file(HOLDOUT_ACCESS_JSON, ["policy_status", "holdout_access_allowed_now"]),
        summarize_json_file(GLOBAL_ALPHA_ACCOUNTING_JSON, ["accounting_status", "global_alpha_accounting_pass", "family_count", "blocked_route_count"]),
        summarize_json_file(GLOBAL_ALPHA_POLICY_JSON, ["policy_status", "current_total_strategy_alpha_budget", "current_total_strategy_route_budget"]),
        summarize_json_file(RESTRICTED_RETEST_EVALUATOR_JSON, ["evaluator_status", "decision_class", "required_runs_per_null_model_for_alpha", "estimated_total_required_null_runs", "release_allowed"]),
        summarize_json_file(RESTRICTED_NULL_POWER_JSON, ["review_status", "decision_class", "additional_null_power_recommended", "route_closed", "release_allowed"]),
    ]

    runtime_family_prior_snapshot = collect_runtime_family_prior_snapshot()

    packet_status = "EXTERNAL_AUDIT_PACKET_REFRESH_READY"
    selected_audit_focus = "METHODOLOGY_AND_RUNTIME_FAMILY_DISTINCTION"

    summary_for_external_auditor = {
        "high_level_verdict_before_external_audit": "REVIEW_REQUIRED_NO_RELEASE",
        "broad_strategy_search_allowed": False,
        "research_execution_allowed_now": False,
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        "closed_restricted_route": {
            "closed_route_hash": closed_route_hash,
            "closed_route_family": closed_route_family,
            "restricted_route_closed": rotation_state.get("restricted_route_closed"),
            "additional_null_budget_allowed_now": rotation_state.get("additional_null_budget_allowed_now"),
            "release_allowed": rotation_state.get("release_allowed"),
        },
        "restricted_retest_key_numbers": {
            "alpha_budget": retest_eval_state.get("alpha_budget"),
            "max_p_empirical_plus_one": retest_eval_state.get("max_p_empirical_plus_one"),
            "required_runs_per_null_model_for_alpha": retest_eval_state.get("required_runs_per_null_model_for_alpha"),
            "estimated_total_required_null_runs": retest_eval_state.get("estimated_total_required_null_runs"),
            "decision_class": retest_eval_state.get("decision_class"),
        },
        "old_short_runtime_family_note": (
            "old_short was not directly invalidated by research route failures. "
            "Prior monitoring saw it as OK/positive, but it still needs current runtime sample/drift/capital-governor review before action."
        ),
        "blocked_route_count": len(blocked_routes),
        "lesson_count": len(lessons),
        "vault_item_count": len(vault_items),
        "git_untracked_or_dirty_count": git_status.get("git_untracked_or_dirty_count"),
    }

    questions = [
        "Where can the OS still fool itself despite the new gates?",
        "Are any gates circular, cosmetic, or too easy to pass?",
        "Is the tiny-alpha policy too strict, too loose, or correctly conservative?",
        "Was the restricted market-state route closure correct?",
        "Should old_short be protected from unrelated research-route failures?",
        "What current runtime family monitor refresh is needed before any capital decision?",
        "Should the next step be data-information quality review, architecture consolidation, or runtime monitor refresh?",
        "Are untracked backup files a process risk or harmless artifacts?",
        "Which modules should be consolidated before more research?",
        "What single next module minimizes self-deception risk?",
    ]

    packet = {
        "packet_name": "edge_factory_os_external_audit_packet_refresh_v1",
        "created_at_utc": utc_now_iso(),
        "packet_status": packet_status,
        "severity": "ATTENTION",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "selected_audit_focus": selected_audit_focus,
        "runtime_family_section_included": True,
        "old_short_status_included": True,
        "summary_for_external_auditor": summary_for_external_auditor,
        "runtime_family_prior_snapshot": runtime_family_prior_snapshot,
        "governance_component_summaries": component_summaries,
        "policy_locked_contract": contract,
        "builder_state": builder_state,
        "rotation_state": rotation_state,
        "closed_route_registry": closed_registry,
        "git_status": git_status,
        "questions_for_external_audit": questions,
        "input_paths": {
            "contract_json": str(CONTRACT_JSON),
            "builder_state_json": str(BUILDER_STATE_JSON),
            "rotation_state_json": str(ROTATION_STATE_JSON),
            "closed_route_registry_json": str(CLOSED_ROUTE_REGISTRY_JSON),
            "lesson_index_json": str(LESSON_INDEX_JSON),
            "blocklist_json": str(BLOCKLIST_JSON),
        },
        "release_gate_feed": {
            "EXTERNAL_AUDIT_PACKET_READY": True,
            "BROAD_STRATEGY_SEARCH_ALLOWED": False,
            "RESEARCH_EXECUTION_ALLOWED_NOW": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_AUDIT_PACKET": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_AUDIT_PACKET": False,
            "FAMILY_RELEASE_ALLOWED_FROM_AUDIT_PACKET": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_AUDIT_PACKET": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_AUDIT_PACKET": False,
            "ACTIVE_PAPER_ALLOWED_FROM_AUDIT_PACKET": False,
            "LIVE_ALLOWED_FROM_AUDIT_PACKET": False,
            "REAL_ORDERS_ALLOWED_FROM_AUDIT_PACKET": False,
        },
        **SAFETY_FLAGS,
    }

    manifest = {
        "manifest_name": "edge_factory_os_audit_packet_manifest_v1",
        "created_at_utc": utc_now_iso(),
        "manifest_status": "AUDIT_PACKET_MANIFEST_READY",
        "packet_json": str(REPO_PACKET_JSON),
        "packet_txt": str(REPO_PACKET_TXT),
        "audit_prompt_txt": str(REPO_PROMPT_TXT),
        "component_count": len(component_summaries),
        "runtime_family_section_included": True,
        "old_short_status_included": True,
        "recommended_use": "Paste audit_prompt_red_team_packet_v1.txt and attach/include external_audit_packet_refresh_v1.json for Claude/red-team review.",
        **SAFETY_FLAGS,
    }

    audit_prompt = build_audit_prompt(packet)

    state = {
        "state_name": "edge_factory_os_external_audit_packet_refresh_state_v1",
        "created_at_utc": utc_now_iso(),
        "packet_status": packet_status,
        "selected_audit_focus": selected_audit_focus,
        "runtime_family_section_included": True,
        "old_short_status_included": True,
        "closed_route_hash": closed_route_hash,
        "closed_route_family": closed_route_family,
        "restricted_route_closed": rotation_state.get("restricted_route_closed"),
        "git_untracked_or_dirty_count": git_status.get("git_untracked_or_dirty_count"),
        "next_recommended_research_key": NEXT_RESEARCH_KEY,
        "next_module": NEXT_MODULE,
        **SAFETY_FLAGS,
    }

    next_queue = {
        "queue_name": "edge_factory_os_external_audit_packet_refresh_next_queue_v1",
        "created_at_utc": utc_now_iso(),
        "queue_status": "EXTERNAL_AUDIT_PACKET_REFRESH_NEXT_QUEUE_READY",
        "top_next_research_key": NEXT_RESEARCH_KEY,
        "top_next_module": NEXT_MODULE,
        "recommended_human_action": "Send audit_prompt_red_team_packet_v1.txt plus external_audit_packet_refresh_v1.json to Claude/external auditor, then integrate response.",
        "research_execution_allowed_now": False,
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        **SAFETY_FLAGS,
    }

    write_json(REPO_PACKET_JSON, packet)
    write_text(REPO_PACKET_TXT, build_packet_text(packet))
    write_json(REPO_MANIFEST_JSON, manifest)
    write_text(REPO_PROMPT_TXT, audit_prompt)
    write_json(REPO_STATE_JSON, state)
    write_json(REPO_NEXT_QUEUE_JSON, next_queue)

    result = {
        "packet_name": "edge_factory_os_external_audit_packet_refresh_v1",
        "created_at_utc": utc_now_iso(),
        "packet_status": packet_status,
        "severity": "ATTENTION",
        "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
        "next_action": "SEND_AUDIT_PACKET_TO_EXTERNAL_REVIEW_OR_BUILD_RESPONSE_INTEGRATOR",
        "reason": "external audit packet refreshed with governance state and runtime family distinction including old_short",
        "selected_audit_focus": selected_audit_focus,
        "runtime_family_section_included": True,
        "old_short_status_included": True,
        "closed_route_hash": closed_route_hash,
        "closed_route_family": closed_route_family,
        "restricted_route_closed": rotation_state.get("restricted_route_closed"),
        "git_untracked_or_dirty_count": git_status.get("git_untracked_or_dirty_count"),
        "next_recommended_research_key": NEXT_RESEARCH_KEY,
        "next_module": NEXT_MODULE,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "packet_json": str(REPO_PACKET_JSON),
        "packet_txt": str(REPO_PACKET_TXT),
        "manifest_json": str(REPO_MANIFEST_JSON),
        "audit_prompt_txt": str(REPO_PROMPT_TXT),
        "state_json": str(REPO_STATE_JSON),
        "next_queue_json": str(REPO_NEXT_QUEUE_JSON),
        "packet": packet,
        "manifest": manifest,
        "state": state,
        "next_queue": next_queue,
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_packet_text(packet))
    print_summary(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
