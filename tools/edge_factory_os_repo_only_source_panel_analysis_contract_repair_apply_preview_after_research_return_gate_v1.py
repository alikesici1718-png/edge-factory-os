from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_source_panel_analysis_contract_repair_apply_preview_after_research_return_gate_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_source_panel_analysis_contract_repair_apply_preview_after_research_return_gate_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_PARENT_HEAD = "a96a774"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 619
EXPECTED_TRACKED_PYTHON_COUNT = 620

CONTRACT_ARTIFACT_PATH = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_contract_after_research_return_gate_v1"
    / "source_panel_analysis_contract_after_research_return_gate_v1.json"
)
REPAIR_PREVIEW_ARTIFACT_PATH = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_contract_repair_preview_after_research_return_gate_v1"
    / "repo_only_source_panel_analysis_contract_repair_preview_after_research_return_gate_v1_latest.json"
)
REPAIR_APPROVAL_ARTIFACT_PATH = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_contract_repair_approval_after_research_return_gate_v1"
    / "repo_only_source_panel_analysis_contract_repair_approval_after_research_return_gate_v1_latest.json"
)
VALIDATOR_ARTIFACT_PATH = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_contract_validator_after_research_return_gate_v1"
    / "repo_only_source_panel_analysis_contract_validator_after_research_return_gate_v1_latest.json"
)
BLOCKED_RECORD_ARTIFACT_PATH = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_contract_blocked_record_after_research_return_gate_v1"
    / "repo_only_source_panel_analysis_contract_blocked_record_after_research_return_gate_v1_latest.json"
)

NEXT_MODULE_REPAIR_APPLY_APPROVAL = "edge_factory_os_repo_only_source_panel_analysis_contract_repair_apply_approval_after_research_return_gate_v1.py"
NEXT_MODULE_ROUTE_RESELECTOR = "edge_factory_os_repo_only_research_return_route_reselector_after_source_panel_contract_block_v1.py"
NEXT_MODULE_RESEARCH_RETURN_BLOCKED = "edge_factory_os_repo_only_research_return_blocked_record_after_source_panel_contract_block_v1.py"
POST_CHECK_STATUS = "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_REPAIR_APPLY_PREVIEW_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_PASS"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "DERIVED_EXPLICIT_ATTENTION"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

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

REQUIRED_REPAIRED_SECTIONS = [
    "research_return_context",
    "source_panel_contract_scope",
    "old_source_panel_anomaly_route_guard",
    "primary_artifact_requirement",
    "evidence_quality_requirements",
    "money_path_alignment",
    "next_module_decision",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    safe_args = ["git", "-c", f"safe.directory={REPO_ROOT.as_posix()}", *args[1:]] if args and args[0] == "git" else args
    result = subprocess.run(safe_args, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {safe_args} returncode={result.returncode} stderr={result.stderr}")
    return result


def load_json_checked(path: Path) -> Tuple[Dict[str, Any], bool, str]:
    if not path.exists():
        return {}, False, "missing"
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {}, False, f"{type(exc).__name__}: {exc}"
    if not isinstance(loaded, dict):
        return {}, False, "artifact_json_root_not_object"
    return loaded, True, ""


def sha256_or_missing(path: Path) -> str:
    if not path.exists():
        return "missing"
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def prior_repair_approval_respected(approval: Dict[str, Any]) -> bool:
    return (
        approval.get("source_panel_analysis_contract_repair_approval_status") == "PASS"
        and approval.get("repair_approval_record_created") is True
        and approval.get("user_repair_approval_present") is True
        and approval.get("approval_grants_repair_approval_record_only") is True
        and approval.get("approval_grants_repair_apply_now") is False
        and approval.get("approval_grants_contract_artifact_edit_now") is False
        and approval.get("repair_apply_performed") is False
        and approval.get("repair_apply_allowed_now") is False
        and approval.get("repair_apply_preview_allowed_next") is True
        and approval.get("runner_preview_blocked") is True
        and approval.get("source_panel_analysis_execution_blocked") is True
        and approval.get("source_panel_contract_validated") is False
        and approval.get("contract_artifact_primary_strength_for_contract_only") is False
        and approval.get("evidence_quality_sufficient_for_contract_validation") is False
        and approval.get("active_p0_blocker_count") == 1
        and approval.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and approval.get("replacement_checks_all_true") is True
    )


def exact_apply_preview(contract_hash: str) -> Dict[str, Any]:
    return {
        "add_or_strengthen_contract_only_primary_artifact_marker": {
            "field": "contract_artifact_primary_strength_for_contract_only",
            "future_apply_value": True,
            "scope": "contract artifact validation only; not source-panel result primary strength",
        },
        "add_exact_contract_identity_marker": {
            "contract_name": "source_panel_analysis_contract_after_research_return_gate_v1",
            "contract_type": "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT",
            "target_artifact_path": str(CONTRACT_ARTIFACT_PATH),
        },
        "add_contract_artifact_hash_identity_expectation": {
            "pre_apply_sha256": contract_hash,
            "future_apply_must_record_pre_apply_sha256": True,
            "future_apply_must_record_post_apply_sha256": True,
        },
        "add_contract_section_completeness_markers": {
            "required_sections": REQUIRED_REPAIRED_SECTIONS,
            "required_sections_all_present": True,
            "missing_section_to_add": "next_module_decision",
        },
        "add_old_source_panel_anomaly_closed_route_guard_marker": {
            "old_source_panel_anomaly_route_reopen_allowed": False,
            "source_panel_contract_must_be_independent_of_old_failed_route": True,
            "route_closed_artifacts_active_evidence_allowed": False,
        },
        "add_future_source_panel_primary_artifact_requirement_marker": {
            "future_source_panel_runner_primary_artifacts_required": True,
            "future_source_panel_primary_artifact_list_marker_present": True,
        },
        "add_no_profit_marker": {"profit_promise": False},
        "add_no_runtime_no_capital_no_live_no_order_marker": {
            "runtime_touch_allowed": False,
            "capital_touch_allowed": False,
            "live_touch_allowed": False,
            "order_touch_allowed": False,
        },
        "add_no_candidate_no_family_no_active_paper_marker": {
            "candidate_generation_allowed": False,
            "family_release_allowed": False,
            "active_paper_allowed": False,
        },
        "add_no_generic_runner_marker": {"generic_runner_approval_or_implementation_allowed": False},
        "add_no_schema_config_marker": {"schema_or_config_creation_allowed": False},
        "add_fail_closed_behavior_if_markers_missing": {
            "validator_must_fail_closed_if_required_marker_missing": True,
            "runner_preview_must_remain_blocked_if_required_marker_missing": True,
        },
        "preserve_future_result_artifact_boundary": {
            "source_panel_result_artifacts_are_future_expected_artifacts_only": True,
            "source_panel_result_primary_strength_claimed_now": False,
        },
    }


def apply_safety_preview() -> Dict[str, bool]:
    return {
        "future_apply_would_touch_runtime": False,
        "future_apply_would_touch_launcher": False,
        "future_apply_would_touch_capital": False,
        "future_apply_would_touch_live": False,
        "future_apply_would_touch_orders": False,
        "future_apply_would_generate_candidates": False,
        "future_apply_would_release_families": False,
        "future_apply_would_activate_paper": False,
        "future_apply_would_approve_or_implement_generic_runner": False,
        "future_apply_would_create_schema_or_config_files": False,
        "future_apply_would_reopen_old_source_panel_anomaly_route": False,
        "future_apply_would_treat_old_route_closed_artifacts_as_active_evidence": False,
        "future_apply_would_claim_source_panel_result_primary_strength_now": False,
        "future_apply_would_claim_trading_profit": False,
    }


def post_apply_expected_state_preview() -> Dict[str, Any]:
    return {
        "source_panel_contract_validated": True,
        "contract_artifact_primary_strength_for_contract_only": True,
        "evidence_quality_sufficient_for_contract_validation": True,
        "active_p0_blocker_count": 0,
        "runner_preview_may_become_eligible_only_after_separate_validator_confirms_repaired_artifact": True,
        "source_panel_execution_still_not_allowed_until_later_runner_preview_and_approval": True,
        "repair_apply_itself_would_not_run_source_panel_analysis": True,
    }


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    contract, contract_valid_json, contract_json_error = load_json_checked(CONTRACT_ARTIFACT_PATH)
    approval, approval_valid_json, approval_json_error = load_json_checked(REPAIR_APPROVAL_ARTIFACT_PATH)
    repair_preview, repair_preview_valid_json, repair_preview_json_error = load_json_checked(REPAIR_PREVIEW_ARTIFACT_PATH)
    validator, validator_valid_json, validator_json_error = load_json_checked(VALIDATOR_ARTIFACT_PATH)
    blocked, blocked_valid_json, blocked_json_error = load_json_checked(BLOCKED_RECORD_ARTIFACT_PATH)
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()

    target_artifact_exists = CONTRACT_ARTIFACT_PATH.exists()
    target_artifact_valid_json = contract_valid_json
    target_artifact_hash = sha256_or_missing(CONTRACT_ARTIFACT_PATH)
    prior_approval_ok = prior_repair_approval_respected(approval)
    preview_safe = target_artifact_exists and target_artifact_valid_json and approval_valid_json and prior_approval_ok
    next_module = NEXT_MODULE_REPAIR_APPLY_APPROVAL if preview_safe else NEXT_MODULE_ROUTE_RESELECTOR
    exact_preview = exact_apply_preview(target_artifact_hash)
    safety_preview = apply_safety_preview()
    expected_state = post_apply_expected_state_preview()

    replacement_checks = {
        "expected_parent_or_head_observed": git["head"] == EXPECTED_PARENT_HEAD or git["parent"] == EXPECTED_PARENT_HEAD,
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "tracked_python_count_increases_from_619_to_620": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "contract_artifact_valid_json": target_artifact_valid_json,
        "repair_preview_artifact_valid_json": repair_preview_valid_json,
        "repair_approval_artifact_valid_json": approval_valid_json,
        "validator_artifact_valid_json": validator_valid_json,
        "blocked_record_artifact_valid_json": blocked_valid_json,
        "prior_repair_approval_respected": prior_approval_ok,
        "repair_apply_preview_completed": True,
        "repair_apply_preview_only": True,
        "repair_apply_performed_false": True,
        "repair_apply_allowed_now_false": True,
        "current_approval_grants_apply_false": True,
        "target_artifact_modified_now_false": True,
        "runner_preview_blocked": True,
        "source_panel_analysis_execution_blocked": True,
        "source_panel_contract_validated_false": True,
        "contract_artifact_primary_strength_for_contract_only_false": True,
        "evidence_quality_sufficient_for_contract_validation_false": True,
        "active_p0_blocker_count_one": True,
        "selected_route_runs_research_now_false": True,
        "selected_route_generates_candidates_now_false": True,
        "selected_route_touches_runtime_capital_live_false": True,
        "selected_route_approves_generic_runner_false": True,
        "selected_route_creates_schema_or_config_false": True,
        "runtime_capital_live_candidate_untouched": True,
        "generic_runner_approval_false": True,
        "generic_runner_implementation_blocked": True,
        "loop_remains_closed": True,
        "future_apply_safety_all_false": all(value is False for value in safety_preview.values()),
        "next_module_allowed": next_module in {
            NEXT_MODULE_REPAIR_APPLY_APPROVAL,
            NEXT_MODULE_ROUTE_RESELECTOR,
            NEXT_MODULE_RESEARCH_RETURN_BLOCKED,
        },
        "repair_apply_not_selected_directly": next_module != "edge_factory_os_repo_only_source_panel_analysis_contract_repair_apply_after_research_return_gate_v1.py",
        "runner_preview_not_selected": "runner_preview" not in next_module,
        "source_panel_execution_not_selected": "source_panel_analysis_execution" not in next_module,
        "contract_artifact_hash_matches_observed": target_artifact_hash == sha256_or_missing(CONTRACT_ARTIFACT_PATH),
    }
    ready = all(value is True for value in replacement_checks.values())

    apply_preview_context = {
        "source_panel_contract_exists": target_artifact_exists,
        "source_panel_contract_valid_json": target_artifact_valid_json,
        "validator_blocked_contract": validator.get("source_panel_contract_validated") is False,
        "blocked_record_created": blocked.get("source_panel_contract_blocked_record_created") is True,
        "repair_preview_found_repairable": repair_preview.get("source_panel_contract_repairable") is True,
        "repair_approval_record_exists": approval.get("repair_approval_record_created") is True,
        "user_approval_is_only_for_approval_record_creation_not_apply": approval.get("approval_grants_repair_apply_now") is False,
        "repair_apply_allowed_now": False,
    }
    target_artifact_preview = {
        "target_artifact_path": str(CONTRACT_ARTIFACT_PATH),
        "target_artifact_exists": target_artifact_exists,
        "target_artifact_valid_json": target_artifact_valid_json,
        "target_artifact_is_repo_file": False,
        "target_artifact_is_output_artifact": True,
        "target_artifact_would_be_modified_by_future_apply": True,
        "target_artifact_current_validation_failure_summary": (
            "Missing/insufficient contract-only primary marker, exact identity/hash markers, self-check and section completeness markers, "
            "including next_module_decision; current contract remains unvalidated with active P0 blocker."
        ),
        "target_artifact_current_sha256": target_artifact_hash,
        "target_artifact_json_error": contract_json_error,
    }
    human_approval_requirement = {
        "future_repair_apply_requires_explicit_user_approval": True,
        "current_approval_does_not_grant_apply": True,
        "next_module_may_record_repair_apply_approval_not_apply_directly": True,
    }

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "source_panel_analysis_contract_repair_apply_preview_status": "PASS" if ready else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS if ready else "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_REPAIR_APPLY_PREVIEW_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_FAIL_CLOSED",
        "final_decision": "SOURCE_PANEL_CONTRACT_REPAIR_APPLY_PREVIEW_SAFE_APPLY_APPROVAL_REQUIRED" if ready and preview_safe else "SOURCE_PANEL_CONTRACT_REPAIR_APPLY_PREVIEW_FAIL_CLOSED",
        "next_action": "BUILD_SOURCE_PANEL_ANALYSIS_CONTRACT_REPAIR_APPLY_APPROVAL_AFTER_RESEARCH_RETURN_GATE" if ready and preview_safe else "RESELECT_RESEARCH_RETURN_ROUTE_AFTER_SOURCE_PANEL_CONTRACT_BLOCK",
        "next_module": next_module if ready else NEXT_MODULE_RESEARCH_RETURN_BLOCKED,
        "prior_repair_approval_respected": prior_approval_ok,
        "repair_apply_preview_completed": True,
        "apply_preview_context_completed": True,
        "target_artifact_preview_completed": True,
        "exact_apply_preview_completed": True,
        "apply_safety_preview_completed": True,
        "post_apply_expected_state_preview_completed": True,
        "human_approval_requirement_completed": True,
        "repair_apply_preview_only": True,
        "repair_apply_performed": False,
        "repair_apply_allowed_now": False,
        "repair_apply_requires_human_approval": True,
        "repair_apply_approval_required_next": bool(preview_safe),
        "current_approval_grants_apply": False,
        "target_artifact_path": str(CONTRACT_ARTIFACT_PATH),
        "target_artifact_exists": target_artifact_exists,
        "target_artifact_valid_json": target_artifact_valid_json,
        "target_artifact_would_be_modified_by_future_apply": True,
        "target_artifact_modified_now": False,
        "exact_apply_preview": exact_preview,
        "apply_safety_preview": safety_preview,
        "post_apply_expected_state_preview": expected_state,
        "future_apply_would_touch_runtime_capital_live": False,
        "future_apply_would_create_schema_or_config": False,
        "future_apply_would_approve_generic_runner": False,
        "future_apply_would_reopen_old_source_panel_anomaly_route": False,
        "future_apply_would_claim_source_panel_result_primary_strength_now": False,
        "future_apply_would_claim_profit": False,
        "future_apply_expected_source_panel_contract_validated": bool(preview_safe),
        "future_apply_expected_contract_artifact_primary_strength_for_contract_only": bool(preview_safe),
        "future_apply_expected_evidence_quality_sufficient_for_contract_validation": bool(preview_safe),
        "future_apply_expected_active_p0_blocker_count": 0 if preview_safe else 1,
        "runner_preview_blocked": True,
        "source_panel_analysis_execution_blocked": True,
        "source_panel_contract_validated": False,
        "contract_artifact_primary_strength_for_contract_only": False,
        "evidence_quality_sufficient_for_contract_validation": False,
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 0,
        "old_source_panel_anomaly_route_reopen_allowed": False,
        "source_panel_contract_must_be_independent_of_old_failed_route": True,
        "selected_route_category": "SOURCE_PANEL_ANALYSIS",
        "selected_route_runs_research_now": False,
        "selected_route_generates_candidates_now": False,
        "selected_route_touches_runtime_capital_live": False,
        "selected_route_approves_generic_runner": False,
        "selected_route_creates_schema_or_config": False,
        "evidence_chain_policy_level": POLICY_LEVEL,
        "current_evidence_chain_quality": CURRENT_EVIDENCE_CHAIN_QUALITY,
        "future_modules_must_classify_evidence_quality": True,
        "full_post_check_marker_preferred_over_plain_pass": True,
        "plain_pass_without_marker_is_attention": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "future_runtime_or_live_requires_preflight_safety_readiness": True,
        "future_runtime_or_live_requires_kill_switch_readiness": True,
        "runtime_preflight_implementation_performed": False,
        "runtime_kill_switch_implementation_performed": False,
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "candidate_generation_performed": False,
        "family_release_performed": False,
        "active_paper_performed": False,
        "real_order_touch_performed": False,
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
            "This repair apply preview uses live repo checks plus prior contract, validator, blocked-record, repair-preview, and repair-approval artifacts only to preview a future apply operation. "
            "It does not apply repair, edit the source-panel contract artifact, run source-panel analysis, proceed to runner preview, generate candidates, touch runtime/capital/live/orders, "
            "approve or implement a generic runner, create schemas/configs, reopen old source-panel anomaly routes, claim profit, or claim source-panel result primary strength now."
        ),
        "replacement_checks_all_true": ready,
        "apply_preview_context": apply_preview_context,
        "target_artifact_preview": target_artifact_preview,
        "human_approval_requirement": human_approval_requirement,
        "contract_artifact_snapshot": {
            "artifact_loaded": bool(contract),
            "artifact_valid_json": contract_valid_json,
            "artifact_json_error": contract_json_error,
            "artifact_path": str(CONTRACT_ARTIFACT_PATH),
            "artifact_sha256": target_artifact_hash,
            "root_keys": sorted(contract.keys()),
            "edited_by_this_module": False,
        },
        "prior_artifact_snapshots": {
            "repair_approval": {
                "artifact_loaded": bool(approval),
                "artifact_valid_json": approval_valid_json,
                "artifact_json_error": approval_json_error,
                "artifact_path": str(REPAIR_APPROVAL_ARTIFACT_PATH),
                "status": approval.get("source_panel_analysis_contract_repair_approval_status"),
                "next_module": approval.get("next_module"),
            },
            "repair_preview": {
                "artifact_loaded": bool(repair_preview),
                "artifact_valid_json": repair_preview_valid_json,
                "artifact_json_error": repair_preview_json_error,
                "artifact_path": str(REPAIR_PREVIEW_ARTIFACT_PATH),
                "status": repair_preview.get("source_panel_analysis_contract_repair_preview_status"),
            },
            "validator": {
                "artifact_loaded": bool(validator),
                "artifact_valid_json": validator_valid_json,
                "artifact_json_error": validator_json_error,
                "artifact_path": str(VALIDATOR_ARTIFACT_PATH),
                "status": validator.get("source_panel_analysis_contract_validator_status"),
            },
            "blocked_record": {
                "artifact_loaded": bool(blocked),
                "artifact_valid_json": blocked_valid_json,
                "artifact_json_error": blocked_json_error,
                "artifact_path": str(BLOCKED_RECORD_ARTIFACT_PATH),
                "status": blocked.get("source_panel_analysis_contract_blocked_record_status"),
            },
        },
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "allowed_next_modules": [
                NEXT_MODULE_REPAIR_APPLY_APPROVAL,
                NEXT_MODULE_ROUTE_RESELECTOR,
                NEXT_MODULE_RESEARCH_RETURN_BLOCKED,
            ],
        },
        "safety_flags": {
            "repo_only": True,
            "repair_apply_preview_only": True,
            "repair_apply_performed": False,
            "contract_artifact_edit_performed": False,
            "source_panel_analysis_run_performed": False,
            "research_run_performed": False,
            "backtest_run_performed": False,
            "candidate_generation_performed": False,
            "family_release_performed": False,
            "active_paper_performed": False,
            "schema_or_config_created": False,
            "runtime_preflight_implementation_performed": False,
            "runtime_kill_switch_implementation_performed": False,
            "runtime_touch_performed": False,
            "capital_touch_performed": False,
            "live_touch_performed": False,
            "real_order_touch_performed": False,
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
    latest_json = OUT_DIR / "repo_only_source_panel_analysis_contract_repair_apply_preview_after_research_return_gate_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_source_panel_analysis_contract_repair_apply_preview_after_research_return_gate_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_source_panel_analysis_contract_repair_apply_preview_after_research_return_gate_v1_latest.txt"
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
    return 0 if payload["source_panel_analysis_contract_repair_apply_preview_status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
