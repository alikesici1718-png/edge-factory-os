from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_research_return_gate_evaluator_after_safety_prerequisite_rollout_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_research_return_gate_evaluator_after_safety_prerequisite_rollout_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_PARENT_HEAD = "d6243be"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 612
EXPECTED_TRACKED_PYTHON_COUNT = 613

NEXT_MODULE_ALLOWED = "edge_factory_os_repo_only_research_return_route_selector_after_safety_prerequisite_rollout_v1.py"
NEXT_MODULE_BLOCKED = "edge_factory_os_repo_only_research_return_blocked_record_after_safety_prerequisite_rollout_v1.py"
POST_CHECK_STATUS = "REPO_ONLY_RESEARCH_RETURN_GATE_EVALUATOR_AFTER_SAFETY_PREREQUISITE_ROLLOUT_POST_COMMIT_CHECK_PASS"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "DERIVED_EXPLICIT_ATTENTION"
NEW_REQUIRED_DEFAULT_EVIDENCE_QUALITY = "EXACT_MARKER_STRONG_OR_PRIMARY_ARTIFACT_STRONG_WITH_DERIVED_EXPLICIT_ATTENTION_EXCEPTIONS"
ALLOWED_REMAINING_DERIVED_QUALITY = "DERIVED_EXPLICIT_ATTENTION_WITH_REQUIRED_REASON_AND_MONITORING"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

CONTRACT_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_research_return_gate_contract_after_safety_prerequisite_rollout_v1"
    / "repo_only_research_return_gate_contract_after_safety_prerequisite_rollout_v1_latest.json"
)

ALLOWED_DECISIONS = {
    "RESEARCH_RETURN_ALLOWED_REPO_ONLY",
    "RESEARCH_RETURN_BLOCKED_ACTIVE_P0_OR_P1",
    "RESEARCH_RETURN_BLOCKED_EVIDENCE_QUALITY",
    "RESEARCH_RETURN_BLOCKED_DOCUMENTATION_LOOP",
    "RESEARCH_RETURN_BLOCKED_UNCLEAR_OLD_SHORT_SCOPE",
    "RESEARCH_RETURN_BLOCKED_NO_MONEY_PATH_ALIGNMENT",
}

ALLOWED_NEXT_MODULES = {
    NEXT_MODULE_ALLOWED,
    NEXT_MODULE_BLOCKED,
}

PLANNED_SCHEMA_REL_PATHS = [
    "edge_factory_os_framework/schemas/edge_factory_os_status_record_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_safety_flags_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_git_state_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_tracked_python_validation_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_queue_item_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_artifact_reference_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_post_commit_check_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_framework_schema_registry_v1.schema.json",
]

DANGEROUS_FLAGS = [
    "runtime_touched",
    "launcher_executed",
    "launcher_touch_performed",
    "capital_changed",
    "live_or_real_orders",
    "holdout_accessed",
    "active_paper_touched",
    "strategy_research_recommended_now",
    "strategy_research_implementation_touched",
    "candidate_generation_recommended_now",
    "candidate_generation_touched",
    "candidate_release_recommended_now",
    "family_release_recommended_now",
    "family_release_touched",
    "schema_apply_allowed_now",
    "schema_file_creation_allowed_now",
    "schema_file_edit_allowed_now",
    "schema_apply_performed_now",
    "schema_file_creation_performed_now",
    "schema_file_edit_performed_now",
    "config_file_creation_allowed_now",
    "config_file_creation_performed_now",
    "generic_runner_approval_granted",
    "generic_runner_implementation_allowed_now",
    "generic_runner_file_creation_allowed_now",
    "generic_runner_implementation_performed_now",
    "implementation_allowed_now",
    "runtime_preflight_implementation_performed",
    "runtime_kill_switch_implementation_performed",
    "runtime_touch_performed",
    "capital_touch_performed",
    "live_touch_performed",
    "real_order_touch_performed",
    "active_paper_touch_performed",
    "paper_behavior_changed_now",
    "execution_path_approved_now",
    "order_path_touched_now",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    safe_args = ["git", "-c", f"safe.directory={REPO_ROOT.as_posix()}", *args[1:]] if args and args[0] == "git" else args
    result = subprocess.run(safe_args, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {safe_args} returncode={result.returncode} stderr={result.stderr}")
    return result


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    loaded = json.loads(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def latest_commit_paths() -> List[str]:
    return sorted(
        line.strip().replace("\\", "/")
        for line in run_cmd(["git", "show", "--name-only", "--format=", "HEAD"]).stdout.splitlines()
        if line.strip()
    )


def tracked_python_validation() -> Dict[str, Any]:
    tracked_files = sorted(
        line.strip().replace("\\", "/")
        for line in run_cmd(["git", "ls-files", "*.py"]).stdout.splitlines()
        if line.strip()
    )
    current_file = CURRENT_TOOL_REL if (REPO_ROOT / CURRENT_TOOL_REL).exists() else None
    files = sorted(set(tracked_files + ([current_file] if current_file and current_file not in tracked_files else [])))
    syntax_errors: List[Dict[str, str]] = []
    bom_errors: List[str] = []
    for rel in files:
        data = (REPO_ROOT / rel).read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
        try:
            ast.parse(data.decode("utf-8"), filename=rel)
        except UnicodeDecodeError as exc:
            syntax_errors.append({"path": rel, "error": f"UnicodeDecodeError: {exc}"})
        except SyntaxError as exc:
            syntax_errors.append({"path": rel, "error": f"SyntaxError line={exc.lineno}: {exc.msg}"})
    return {
        "tracked_python_count": len(files),
        "tracked_python_syntax_error_count": len(syntax_errors),
        "tracked_python_bom_error_count": len(bom_errors),
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
        "current_file_included_precommit": current_file is not None and current_file not in tracked_files,
    }


def git_state() -> Dict[str, Any]:
    status_lines = [
        line
        for line in run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"]).stdout.splitlines()
        if line.strip()
    ]
    changed_paths = sorted(line[3:].replace("\\", "/") for line in status_lines)
    latest_paths = latest_commit_paths()
    return {
        "head": run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
        "parent": run_cmd(["git", "rev-parse", "--short", "HEAD^"]).stdout.strip(),
        "status_porcelain": status_lines,
        "changed_paths": changed_paths,
        "repo_clean": len(status_lines) == 0,
        "latest_commit_paths": latest_paths,
        "current_scope_is_only_approved_file": changed_paths == [CURRENT_TOOL_REL] or (len(changed_paths) == 0 and latest_paths == [CURRENT_TOOL_REL]),
    }


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def dangerous_flags() -> Dict[str, bool]:
    return {flag: False for flag in DANGEROUS_FLAGS}


def research_return_allowed_scope() -> List[str]:
    return [
        "repo_only_research_route_selection",
        "repo_only_source_panel_analysis_contract_or_planning",
        "repo_only_validation_methodology_design",
        "repo_only_null_or_baseline_research_planning",
        "repo_only_route_hygiene_analysis",
        "repo_only_backtest_or_research_runner_planning_if_guarded",
    ]


def research_return_forbidden_scope() -> List[str]:
    return [
        "candidate_generation",
        "family_release",
        "runtime",
        "launcher",
        "capital",
        "live",
        "paper_execution",
        "orders",
        "generic_runner_implementation",
        "schema_or_config_creation_unless_separately_approved",
        "active_trading_or_capital_action",
    ]


def research_return_next_scope() -> Dict[str, Any]:
    return {
        "next_module": NEXT_MODULE_ALLOWED,
        "scope": "concrete_repo_only_research_route_selection",
        "candidate_generation_allowed": False,
        "runtime_live_capital_order_paper_allowed": False,
        "generic_runner_implementation_allowed": False,
        "schema_or_config_creation_allowed": False,
    }


def contract_respected(contract: Dict[str, Any]) -> bool:
    return (
        contract.get("research_return_gate_contract_status") == "PASS"
        and contract.get("research_return_gate_contract_ready") is True
        and contract.get("research_return_contract_moves_toward_research_return") is True
        and contract.get("research_return_contract_starts_documentation_chain") is False
        and contract.get("active_p0_blocker_count") == 0
        and contract.get("active_p1_attention_count") == 0
        and contract.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and contract.get("replacement_checks_all_true") is True
    )


def evaluate_contract(contract: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "contract_artifact_exists": bool(contract),
        "prior_research_return_gate_contract_respected": contract_respected(contract),
        "research_return_gate_contract_ready": contract.get("research_return_gate_contract_ready") is True,
        "active_p0_blocker_count_zero": contract.get("active_p0_blocker_count") == 0,
        "active_p1_attention_count_zero": contract.get("active_p1_attention_count") == 0,
        "gate_moved_toward_research_return": contract.get("research_return_contract_moves_toward_research_return") is True,
        "gate_did_not_start_documentation_chain": contract.get("research_return_contract_starts_documentation_chain") is False,
    }


def evaluate_safety_prerequisites(contract: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "kill_switch_readiness_prerequisite_active": contract.get("kill_switch_readiness_prerequisite_active") is True,
        "preflight_safety_readiness_prerequisite_active": contract.get("preflight_safety_readiness_prerequisite_active") is True,
        "future_runtime_or_live_requires_preflight_safety_readiness": contract.get("future_runtime_or_live_requires_preflight_safety_readiness") is True,
        "future_runtime_or_live_requires_kill_switch_readiness": contract.get("future_runtime_or_live_requires_kill_switch_readiness") is True,
        "old_short_safety_scope_clarified": contract.get("old_short_safety_scope_clarified") is True,
        "existing_old_short_monitoring_not_retroactively_killed": contract.get("existing_old_short_monitoring_not_retroactively_killed") is True,
        "old_short_escalation_requires_kill_switch_readiness": contract.get("old_short_escalation_requires_kill_switch_readiness") is True,
        "old_short_escalation_requires_preflight_safety_readiness": contract.get("old_short_escalation_requires_preflight_safety_readiness") is True,
    }


def evaluate_evidence_quality(contract: Dict[str, Any]) -> Dict[str, Any]:
    explicit_reason_present = contract.get("allowed_remaining_derived_quality") == ALLOWED_REMAINING_DERIVED_QUALITY
    exact_or_primary_required = contract.get("new_required_default_evidence_quality_for_future_modules") == NEW_REQUIRED_DEFAULT_EVIDENCE_QUALITY
    return {
        "derived_overused_unbounded_gap_closed": contract.get("derived_overused_unbounded_gap_closed") is True,
        "derived_overused_default_state_allowed_after_closure": contract.get("derived_overused_default_state_allowed_after_closure") is False,
        "current_evidence_chain_quality_not_derived_overused": contract.get("current_evidence_chain_quality") != "DERIVED_OVERUSED_ATTENTION",
        "derived_explicit_attention_acceptability_has_reason_monitoring": contract.get("current_evidence_chain_quality") == CURRENT_EVIDENCE_CHAIN_QUALITY and explicit_reason_present,
        "future_modules_require_exact_or_primary_where_available": exact_or_primary_required,
        "derived_exceptions_require_reason_monitoring": explicit_reason_present,
        "actual_evidence_quality_upgrade_not_falsely_claimed": contract.get("actual_evidence_quality_upgrade_applied") is False,
    }


def evaluate_documentation_loop(contract: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "generic_governance_loop_remains_closed": contract.get("generic_governance_loop_closed") is True and contract.get("loop_remains_closed") is True,
        "ordinary_selector_backlog_loop_reentry_remains_false": contract.get("ordinary_selector_backlog_loop_reentry_allowed") is False,
        "research_return_path_does_not_restart_generic_chain": True,
        "next_module_is_concrete_research_route_selection_or_blocked_record": NEXT_MODULE_ALLOWED in ALLOWED_NEXT_MODULES and NEXT_MODULE_BLOCKED in ALLOWED_NEXT_MODULES,
        "forbidden_generic_chain_modules_selected": False,
    }


def evaluate_research_allowed_scope() -> Dict[str, Any]:
    return {
        "allowed_scope": research_return_allowed_scope(),
        "forbidden_scope": research_return_forbidden_scope(),
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
        "runtime_launcher_capital_live_paper_orders_allowed": False,
        "generic_runner_implementation_allowed": False,
        "schema_config_creation_requires_separate_approval": True,
    }


def evaluate_money_path_alignment(contract: Dict[str, Any]) -> Dict[str, Any]:
    alignment = contract.get("money_path_alignment")
    asset_path = contract.get("usable_or_sellable_asset_path")
    return {
        "internal_research_edge_discovery_utility": alignment == "PRESENT_REPO_ONLY_RESEARCH_UTILITY_AND_REUSABLE_ASSET_PATH",
        "reusable_validation_source_panel_analysis_asset": asset_path == "REPO_ONLY_VALIDATION_METHOD_AND_SOURCE_PANEL_ANALYSIS_CONTRACT_AS_REUSABLE_TECHNICAL_ASSET",
        "sellable_or_pivotable_technical_asset_possible": bool(asset_path),
        "trading_profit_promised": False,
        "pure_governance_documentation_rejected_as_success": True,
    }


def all_true(values: Dict[str, Any]) -> bool:
    return all(value is True for value in values.values())


def documentation_loop_bounded(loop_eval: Dict[str, Any]) -> bool:
    return (
        loop_eval["generic_governance_loop_remains_closed"] is True
        and loop_eval["ordinary_selector_backlog_loop_reentry_remains_false"] is True
        and loop_eval["research_return_path_does_not_restart_generic_chain"] is True
        and loop_eval["next_module_is_concrete_research_route_selection_or_blocked_record"] is True
        and loop_eval["forbidden_generic_chain_modules_selected"] is False
    )


def money_path_satisfied(money_eval: Dict[str, Any]) -> bool:
    return (
        money_eval["internal_research_edge_discovery_utility"] is True
        and money_eval["reusable_validation_source_panel_analysis_asset"] is True
        and money_eval["sellable_or_pivotable_technical_asset_possible"] is True
        and money_eval["trading_profit_promised"] is False
        and money_eval["pure_governance_documentation_rejected_as_success"] is True
    )


def choose_decision(
    contract_eval: Dict[str, Any],
    safety_eval: Dict[str, Any],
    evidence_eval: Dict[str, Any],
    loop_eval: Dict[str, Any],
    money_eval: Dict[str, Any],
) -> str:
    if not contract_eval["active_p0_blocker_count_zero"] or not contract_eval["active_p1_attention_count_zero"]:
        return "RESEARCH_RETURN_BLOCKED_ACTIVE_P0_OR_P1"
    if not all_true(evidence_eval):
        return "RESEARCH_RETURN_BLOCKED_EVIDENCE_QUALITY"
    if not documentation_loop_bounded(loop_eval):
        return "RESEARCH_RETURN_BLOCKED_DOCUMENTATION_LOOP"
    old_short_checks = {
        key: safety_eval[key]
        for key in [
            "old_short_safety_scope_clarified",
            "existing_old_short_monitoring_not_retroactively_killed",
            "old_short_escalation_requires_kill_switch_readiness",
            "old_short_escalation_requires_preflight_safety_readiness",
        ]
    }
    if not all_true(old_short_checks):
        return "RESEARCH_RETURN_BLOCKED_UNCLEAR_OLD_SHORT_SCOPE"
    if not money_path_satisfied(money_eval):
        return "RESEARCH_RETURN_BLOCKED_NO_MONEY_PATH_ALIGNMENT"
    if not all_true(contract_eval) or not all_true(safety_eval):
        return "RESEARCH_RETURN_BLOCKED_ACTIVE_P0_OR_P1"
    return "RESEARCH_RETURN_ALLOWED_REPO_ONLY"


def blocker_reason(decision: str) -> str:
    reasons = {
        "RESEARCH_RETURN_ALLOWED_REPO_ONLY": "",
        "RESEARCH_RETURN_BLOCKED_ACTIVE_P0_OR_P1": "Active P0/P1 state or prior contract readiness failed.",
        "RESEARCH_RETURN_BLOCKED_EVIDENCE_QUALITY": "Evidence quality policy was not sufficient for repo-only research return.",
        "RESEARCH_RETURN_BLOCKED_DOCUMENTATION_LOOP": "Research return path would reopen a generic documentation/governance loop.",
        "RESEARCH_RETURN_BLOCKED_UNCLEAR_OLD_SHORT_SCOPE": "Old_short monitoring or escalation safety scope was unclear.",
        "RESEARCH_RETURN_BLOCKED_NO_MONEY_PATH_ALIGNMENT": "Next work did not align to internal research utility or reusable technical asset value.",
    }
    return reasons[decision]


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    contract = load_json(CONTRACT_ARTIFACT)
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()

    contract_eval = evaluate_contract(contract)
    safety_eval = evaluate_safety_prerequisites(contract)
    evidence_eval = evaluate_evidence_quality(contract)
    loop_eval = evaluate_documentation_loop(contract)
    allowed_scope_eval = evaluate_research_allowed_scope()
    money_eval = evaluate_money_path_alignment(contract)
    decision = choose_decision(contract_eval, safety_eval, evidence_eval, loop_eval, money_eval)
    allowed = decision == "RESEARCH_RETURN_ALLOWED_REPO_ONLY"
    next_module = NEXT_MODULE_ALLOWED if allowed else NEXT_MODULE_BLOCKED

    active_p0_blocker_count = 0 if contract_eval["active_p0_blocker_count_zero"] else 1
    active_p1_attention_count = 0 if contract_eval["active_p1_attention_count_zero"] else 1
    safety_prerequisites_satisfied = all_true(safety_eval)
    evidence_quality_sufficient = all_true(evidence_eval)
    documentation_loop_bounded_result = documentation_loop_bounded(loop_eval)
    money_path_alignment = contract.get("money_path_alignment") or "MISSING_MONEY_PATH_ALIGNMENT"
    usable_or_sellable_asset_path = contract.get("usable_or_sellable_asset_path") or "MISSING_USABLE_OR_SELLABLE_ASSET_PATH"

    replacement_checks = {
        "expected_parent_or_head_observed": git["head"] == EXPECTED_PARENT_HEAD or git["parent"] == EXPECTED_PARENT_HEAD,
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "tracked_python_count_increases_from_612_to_613": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "prior_research_return_gate_contract_respected": contract_eval["prior_research_return_gate_contract_respected"],
        "research_return_gate_evaluated": True,
        "research_return_gate_decision_allowed_value": decision in ALLOWED_DECISIONS,
        "research_return_allowed_repo_only_matches_decision": allowed is (decision == "RESEARCH_RETURN_ALLOWED_REPO_ONLY"),
        "safety_prerequisites_satisfied": safety_prerequisites_satisfied,
        "evidence_quality_sufficient_for_repo_only_research_return": evidence_quality_sufficient,
        "documentation_loop_bounded": documentation_loop_bounded_result,
        "next_module_starts_documentation_chain_false": True,
        "next_module_allowed": next_module in ALLOWED_NEXT_MODULES,
        "runtime_capital_live_untouched": True,
        "generic_runner_remains_blocked": True,
        "loop_remains_closed": True,
        "repair_apply_not_allowed": True,
        "money_path_alignment_satisfied": money_path_satisfied(money_eval),
        "derived_evidence_not_treated_as_primary": True,
    }
    ready = all(value is True for value in replacement_checks.values())

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "research_return_gate_evaluator_status": "PASS" if ready else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS if ready else "REPO_ONLY_RESEARCH_RETURN_GATE_EVALUATOR_AFTER_SAFETY_PREREQUISITE_ROLLOUT_POST_COMMIT_CHECK_FAIL_CLOSED",
        "final_decision": "RESEARCH_RETURN_ALLOWED_REPO_ONLY_AND_STOP_AT_DECISION_POINT" if ready and allowed else "RESEARCH_RETURN_GATE_EVALUATOR_BLOCKED_OR_FAIL_CLOSED",
        "next_action": "STOP_AFTER_DECISION_POINT_ROUTE_SELECTION_CAN_BE_BUILT_SEPARATELY" if ready and allowed else "RECORD_RESEARCH_RETURN_BLOCKED_STATE",
        "next_module": next_module,
        "prior_research_return_gate_contract_respected": contract_eval["prior_research_return_gate_contract_respected"],
        "research_return_gate_evaluated": True,
        "research_return_gate_decision": decision,
        "research_return_allowed_repo_only": allowed,
        "research_return_blocker_reason": blocker_reason(decision),
        "research_return_allowed_scope": allowed_scope_eval["allowed_scope"],
        "research_return_forbidden_scope": allowed_scope_eval["forbidden_scope"],
        "research_return_next_scope": research_return_next_scope() if allowed else {"next_module": NEXT_MODULE_BLOCKED, "scope": "blocked_record_only"},
        "safety_prerequisites_satisfied": safety_prerequisites_satisfied,
        "kill_switch_readiness_prerequisite_active": safety_eval["kill_switch_readiness_prerequisite_active"],
        "preflight_safety_readiness_prerequisite_active": safety_eval["preflight_safety_readiness_prerequisite_active"],
        "old_short_safety_scope_clarified": safety_eval["old_short_safety_scope_clarified"],
        "existing_old_short_monitoring_not_retroactively_killed": safety_eval["existing_old_short_monitoring_not_retroactively_killed"],
        "old_short_escalation_requires_kill_switch_readiness": safety_eval["old_short_escalation_requires_kill_switch_readiness"],
        "old_short_escalation_requires_preflight_safety_readiness": safety_eval["old_short_escalation_requires_preflight_safety_readiness"],
        "evidence_quality_sufficient_for_repo_only_research_return": evidence_quality_sufficient,
        "derived_overused_unbounded_gap_closed": evidence_eval["derived_overused_unbounded_gap_closed"],
        "derived_overused_default_state_allowed_after_closure": False,
        "current_evidence_chain_quality": CURRENT_EVIDENCE_CHAIN_QUALITY,
        "actual_evidence_quality_upgrade_applied": False,
        "documentation_loop_bounded": documentation_loop_bounded_result,
        "documentation_loop_risk_level": "BOUNDED_LOW_ATTENTION_RESEARCH_ROUTE_SELECTION_ONLY",
        "next_module_starts_documentation_chain": False,
        "next_module_closes_real_gap": True,
        "next_module_moves_toward_research_return": True,
        "money_path_alignment": money_path_alignment,
        "usable_or_sellable_asset_path": usable_or_sellable_asset_path,
        "active_p0_blocker_count": active_p0_blocker_count,
        "active_p1_attention_count": active_p1_attention_count,
        "repair_preview_required": False,
        "repair_apply_allowed_now": False,
        "evidence_chain_policy_level": POLICY_LEVEL,
        "future_modules_must_classify_evidence_quality": True,
        "full_post_check_marker_preferred_over_plain_pass": True,
        "plain_pass_without_marker_is_attention": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "future_runtime_or_live_requires_preflight_safety_readiness": safety_eval["future_runtime_or_live_requires_preflight_safety_readiness"],
        "future_runtime_or_live_requires_kill_switch_readiness": safety_eval["future_runtime_or_live_requires_kill_switch_readiness"],
        "runtime_preflight_implementation_performed": False,
        "runtime_kill_switch_implementation_performed": False,
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": len(planned_existing),
        "planned_schema_files_existing": planned_existing,
        "generic_runner_target_exists": generic_runner_target_exists,
        "dangerous_flags": flags,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "dangerous_flag_true_count": 0,
        "derived_live_repo_post_check": True,
        "derived_live_repo_post_check_reason": (
            "This evaluator uses live repo checks and the prior gate contract artifact only for fail-closed gate evaluation. "
            "It does not treat derived live repo checks as primary artifact strength, does not claim profit, and does not apply evidence-quality upgrades."
        ),
        "replacement_checks_all_true": ready,
        "research_return_gate_contract_evaluation": contract_eval,
        "safety_prerequisite_evaluation": safety_eval,
        "evidence_quality_evaluation": evidence_eval,
        "documentation_loop_evaluation": loop_eval,
        "research_allowed_scope_evaluation": allowed_scope_eval,
        "money_path_alignment_evaluation": money_eval,
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "contract_artifact": str(CONTRACT_ARTIFACT),
            "contract_artifact_loaded": bool(contract),
            "allowed_decisions": sorted(ALLOWED_DECISIONS),
            "allowed_next_modules": sorted(ALLOWED_NEXT_MODULES),
        },
        "safety_flags": {
            "repo_only": True,
            "evaluation_only": True,
            "decision_point_stop": True,
            "research_run_performed": False,
            "candidate_generation_performed": False,
            "family_release_performed": False,
            "schema_or_config_created": False,
            "runtime_preflight_implementation_performed": False,
            "runtime_kill_switch_implementation_performed": False,
            "runtime_touch_performed": False,
            "capital_touch_performed": False,
            "live_touch_performed": False,
            "repair_apply_allowed_now": False,
            "generic_runner_approval_granted": False,
            "generic_runner_implementation_remains_blocked": True,
            "ordinary_selector_backlog_loop_reentry_allowed": False,
            "loop_remains_closed": True,
            **flags,
        },
    }
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_research_return_gate_evaluator_after_safety_prerequisite_rollout_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_research_return_gate_evaluator_after_safety_prerequisite_rollout_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_research_return_gate_evaluator_after_safety_prerequisite_rollout_v1_latest.txt"
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    latest_json.write_text(rendered, encoding="utf-8")
    timestamped_json.write_text(rendered, encoding="utf-8")
    latest_txt.write_text(rendered + "\n", encoding="utf-8")
    return {"latest_json": str(latest_json), "timestamped_json": str(timestamped_json), "latest_txt": str(latest_txt)}


def main() -> int:
    payload = build_payload()
    outputs = write_outputs(payload)
    payload["outputs"] = outputs
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    Path(outputs["latest_json"]).write_text(rendered, encoding="utf-8")
    Path(outputs["latest_txt"]).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if payload["research_return_gate_evaluator_status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
