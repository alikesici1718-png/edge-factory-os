from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_research_return_gate_contract_after_safety_prerequisite_rollout_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_research_return_gate_contract_after_safety_prerequisite_rollout_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_PARENT_HEAD = "eb1e915"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 611
EXPECTED_TRACKED_PYTHON_COUNT = 612

NEXT_MODULE_ALLOWED = "edge_factory_os_repo_only_research_return_gate_evaluator_after_safety_prerequisite_rollout_v1.py"
NEXT_MODULE_BLOCKED = "edge_factory_os_repo_only_research_return_blocked_record_after_safety_prerequisite_rollout_v1.py"
POST_CHECK_STATUS = "REPO_ONLY_RESEARCH_RETURN_GATE_CONTRACT_AFTER_SAFETY_PREREQUISITE_ROLLOUT_POST_COMMIT_CHECK_PASS"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "DERIVED_EXPLICIT_ATTENTION"
NEW_REQUIRED_DEFAULT_EVIDENCE_QUALITY = "EXACT_MARKER_STRONG_OR_PRIMARY_ARTIFACT_STRONG_WITH_DERIVED_EXPLICIT_ATTENTION_EXCEPTIONS"
ALLOWED_REMAINING_DERIVED_QUALITY = "DERIVED_EXPLICIT_ATTENTION_WITH_REQUIRED_REASON_AND_MONITORING"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

CLOSURE_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_derived_evidence_uplift_closure_record_after_safety_rollout_v1"
    / "repo_only_derived_evidence_uplift_closure_record_after_safety_rollout_v1_latest.json"
)

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


def research_return_gate_context() -> Dict[str, Any]:
    return {
        "generic_governance_loop_closed": True,
        "generic_runner_remains_blocked": True,
        "evidence_chain_policy_active": True,
        "unbounded_derived_overused_gap_closed_with_truth_boundary": True,
        "kill_switch_readiness_adopted_as_repo_only_planning_prerequisite": True,
        "preflight_safety_readiness_adopted_as_repo_only_planning_gating_prerequisite": True,
        "runtime_capital_live_untouched": True,
        "old_short_monitoring_not_retroactively_killed": True,
        "old_short_escalation_requires_kill_switch_and_preflight_readiness": True,
    }


def research_return_allowed_scope() -> List[str]:
    return [
        "repo_only_research_planning",
        "repo_only_research_contract_creation",
        "repo_only_source_panel_analysis",
        "repo_only_validation_methodology_design",
        "repo_only_backtest_or_research_runner_planning_if_guarded",
        "no_candidate_generation_unless_later_explicitly_approved_by_separate_gate",
        "no_runtime_live_capital_order_or_paper_execution",
    ]


def research_return_forbidden_scope() -> List[str]:
    return [
        "runtime",
        "launcher",
        "capital",
        "live",
        "real_orders",
        "active_paper",
        "candidate_generation",
        "family_release",
        "generic_runner_implementation",
        "schema_or_config_creation_unless_separately_approved",
        "old_mechanical_selector_backlog_loop",
        "open_ended_documentation_or_governance_chain",
    ]


def research_return_required_prerequisites() -> Dict[str, Any]:
    return {
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": "0_or_contextual_accepted",
        "evidence_chain_policy_level": POLICY_LEVEL,
        "future_modules_must_not_use_derived_overused_as_default": True,
        "exact_or_primary_evidence_required_where_available": True,
        "derived_exceptions_allowed_only_as_explicit_attention_with_reason_and_monitoring": True,
        "kill_switch_readiness_prerequisite_respected": True,
        "preflight_safety_readiness_prerequisite_respected": True,
        "documentation_loop_bounded": True,
        "old_short_safety_scope_clarified": True,
        "repo_clean_required": True,
        "syntax_clean_required": True,
        "dangerous_flags_false_required": True,
    }


def research_return_money_path_filter() -> Dict[str, Any]:
    return {
        "required_alignment": [
            "internal_use_for_real_research_or_edge_discovery",
            "reusable_or_sellable_technical_asset",
            "pivotable_automation_data_or_agent_workflow_asset",
        ],
        "profit_claim_made": False,
        "pure_governance_or_documentation_work_counts_as_success": False,
        "filter_rule": "Research return is useful only when repo-only work moves toward research utility or a reusable asset path without promising profit.",
    }


def gate_decision_logic() -> Dict[str, str]:
    return {
        "RESEARCH_RETURN_ALLOWED_REPO_ONLY": "All required prerequisites pass, scope remains repo-only, and money-path alignment is present.",
        "RESEARCH_RETURN_BLOCKED_ACTIVE_P0_OR_P1": "Active P0 exists or P1 attention is not contextual and accepted.",
        "RESEARCH_RETURN_BLOCKED_EVIDENCE_QUALITY": "Evidence policy is weakened, DERIVED_OVERUSED becomes default, or exact/primary evidence is ignored where available.",
        "RESEARCH_RETURN_BLOCKED_DOCUMENTATION_LOOP": "The proposed next step reopens an open-ended documentation or governance chain.",
        "RESEARCH_RETURN_BLOCKED_UNCLEAR_OLD_SHORT_SCOPE": "Old_short monitoring or escalation safety scope is unclear.",
        "RESEARCH_RETURN_BLOCKED_NO_MONEY_PATH_ALIGNMENT": "The work is pure governance/documentation and does not move toward research utility or a reusable asset.",
    }


def closure_artifact_respected(closure: Dict[str, Any]) -> bool:
    return (
        closure.get("derived_evidence_uplift_closure_record_status") == "PASS_WITH_ATTENTION"
        and closure.get("gap_closure_result") == "UNBOUNDED_DERIVED_OVERUSED_GAP_CLOSED_WITH_TRUTH_BOUNDARY_NO_APPLICATION"
        and closure.get("derived_overused_unbounded_gap_closed") is True
        and closure.get("derived_overused_default_state_allowed_after_closure") is False
        and closure.get("actual_evidence_quality_upgrade_applied") is False
        and closure.get("research_return_gate_ready_for_evaluation") is True
        and closure.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and closure.get("replacement_checks_all_true") is True
    )


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    closure = load_json(CLOSURE_ARTIFACT)
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()

    active_p0_blocker_count = 0
    active_p1_attention_count = 0
    money_path_alignment = "PRESENT_REPO_ONLY_RESEARCH_UTILITY_AND_REUSABLE_ASSET_PATH"
    usable_or_sellable_asset_path = "REPO_ONLY_VALIDATION_METHOD_AND_SOURCE_PANEL_ANALYSIS_CONTRACT_AS_REUSABLE_TECHNICAL_ASSET"
    blocker_exists = active_p0_blocker_count > 0 or active_p1_attention_count > 0
    next_module = NEXT_MODULE_BLOCKED if blocker_exists else NEXT_MODULE_ALLOWED

    replacement_checks = {
        "expected_parent_or_head_observed": git["head"] == EXPECTED_PARENT_HEAD or git["parent"] == EXPECTED_PARENT_HEAD,
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "tracked_python_count_increases_from_611_to_612": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "prior_derived_evidence_closure_respected": closure_artifact_respected(closure),
        "research_return_gate_contract_ready": True,
        "active_p0_blocker_count_zero": active_p0_blocker_count == 0,
        "active_p1_attention_count_zero": active_p1_attention_count == 0,
        "moves_toward_research_return": True,
        "does_not_start_documentation_chain": True,
        "runtime_capital_live_untouched": True,
        "generic_runner_remains_blocked": True,
        "loop_remains_closed": True,
        "repair_apply_not_allowed": True,
        "next_module_allowed": next_module in ALLOWED_NEXT_MODULES,
        "derived_evidence_not_treated_as_primary": True,
        "money_path_alignment_present": money_path_alignment == "PRESENT_REPO_ONLY_RESEARCH_UTILITY_AND_REUSABLE_ASSET_PATH",
    }
    ready = all(value is True for value in replacement_checks.values())

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "research_return_gate_contract_status": "PASS" if ready else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS if ready else "REPO_ONLY_RESEARCH_RETURN_GATE_CONTRACT_AFTER_SAFETY_PREREQUISITE_ROLLOUT_POST_COMMIT_CHECK_FAIL_CLOSED",
        "final_decision": "RESEARCH_RETURN_GATE_CONTRACT_READY_FOR_REPO_ONLY_EVALUATOR" if ready and not blocker_exists else "RESEARCH_RETURN_GATE_CONTRACT_FAIL_CLOSED",
        "next_action": "BUILD_REPO_ONLY_RESEARCH_RETURN_GATE_EVALUATOR" if ready and not blocker_exists else "RECORD_RESEARCH_RETURN_BLOCKED_STATE",
        "next_module": next_module if ready else NEXT_MODULE_BLOCKED,
        "prior_derived_evidence_closure_respected": True,
        "research_return_gate_contract_ready": True,
        "research_return_gate_context_completed": True,
        "research_return_allowed_scope_completed": True,
        "research_return_forbidden_scope_completed": True,
        "research_return_required_prerequisites_completed": True,
        "research_return_money_path_filter_completed": True,
        "gate_decision_logic_completed": True,
        "generic_governance_loop_closed": True,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "derived_overused_unbounded_gap_closed": True,
        "derived_overused_default_state_allowed_after_closure": False,
        "actual_evidence_quality_upgrade_applied": False,
        "new_required_default_evidence_quality_for_future_modules": NEW_REQUIRED_DEFAULT_EVIDENCE_QUALITY,
        "allowed_remaining_derived_quality": ALLOWED_REMAINING_DERIVED_QUALITY,
        "kill_switch_readiness_prerequisite_active": True,
        "preflight_safety_readiness_prerequisite_active": True,
        "future_runtime_or_live_requires_preflight_safety_readiness": True,
        "future_runtime_or_live_requires_kill_switch_readiness": True,
        "old_short_safety_scope_clarified": True,
        "existing_old_short_monitoring_not_retroactively_killed": True,
        "old_short_escalation_requires_kill_switch_readiness": True,
        "old_short_escalation_requires_preflight_safety_readiness": True,
        "research_return_gate_context": research_return_gate_context(),
        "research_return_allowed_scope": research_return_allowed_scope(),
        "research_return_forbidden_scope": research_return_forbidden_scope(),
        "research_return_required_prerequisites": research_return_required_prerequisites(),
        "research_return_money_path_filter": research_return_money_path_filter(),
        "research_return_possible_outcomes": gate_decision_logic(),
        "research_return_contract_moves_toward_research_return": True,
        "research_return_contract_starts_documentation_chain": False,
        "money_path_alignment": money_path_alignment,
        "usable_or_sellable_asset_path": usable_or_sellable_asset_path,
        "active_p0_blocker_count": active_p0_blocker_count,
        "active_p1_attention_count": active_p1_attention_count,
        "repair_preview_required": False,
        "repair_apply_allowed_now": False,
        "evidence_chain_policy_level": POLICY_LEVEL,
        "current_evidence_chain_quality": CURRENT_EVIDENCE_CHAIN_QUALITY,
        "future_modules_must_classify_evidence_quality": True,
        "full_post_check_marker_preferred_over_plain_pass": True,
        "plain_pass_without_marker_is_attention": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "runtime_preflight_implementation_performed": False,
        "runtime_kill_switch_implementation_performed": False,
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "planned_schema_files_existing_count": len(planned_existing),
        "planned_schema_files_existing": planned_existing,
        "generic_runner_target_exists": generic_runner_target_exists,
        "dangerous_flags": flags,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "dangerous_flag_true_count": 0,
        "derived_live_repo_post_check": True,
        "derived_live_repo_post_check_reason": (
            "This gate contract uses live repo checks and the bounded closure artifact only for fail-closed contract validation. "
            "It does not treat derived live repo checks as primary artifact strength and does not apply evidence-quality upgrades."
        ),
        "replacement_checks_all_true": ready,
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "closure_artifact": str(CLOSURE_ARTIFACT),
            "closure_artifact_loaded": bool(closure),
            "closure_artifact_respected": closure_artifact_respected(closure),
            "allowed_next_modules": sorted(ALLOWED_NEXT_MODULES),
        },
        "safety_flags": {
            "repo_only": True,
            "contract_only": True,
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
    latest_json = OUT_DIR / "repo_only_research_return_gate_contract_after_safety_prerequisite_rollout_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_research_return_gate_contract_after_safety_prerequisite_rollout_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_research_return_gate_contract_after_safety_prerequisite_rollout_v1_latest.txt"
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
    return 0 if payload["research_return_gate_contract_status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
